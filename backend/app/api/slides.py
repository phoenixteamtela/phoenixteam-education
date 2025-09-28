import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.config import settings
from ..models.models import Slide, Class, User, DocumentChunk
from ..schemas.schemas import SlideCreate, Slide as SlideSchema
from .auth import get_current_user, get_current_admin_user
from ..services.document_processor import document_processor

router = APIRouter()

ALLOWED_SLIDE_TYPES = {
    "application/pdf": ".pdf"
}

# Additional validation for files that may be detected as application/octet-stream
ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf"
}

@router.post("/upload/{class_id}", response_model=SlideSchema)
async def upload_slide(
    class_id: int,
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if file type is allowed by MIME type
    file_allowed = file.content_type in ALLOWED_SLIDE_TYPES
    effective_content_type = file.content_type

    # If MIME type is application/octet-stream, check by file extension
    if not file_allowed and file.content_type == "application/octet-stream":
        if file.filename:
            for ext in ALLOWED_EXTENSIONS:
                if file.filename.lower().endswith(ext.lower()):
                    file_allowed = True
                    # Use the correct content type for database storage
                    effective_content_type = ALLOWED_EXTENSIONS[ext]
                    print(f"ACCEPTED FILE by extension: {file.filename} ({file.content_type} -> {effective_content_type})")
                    break

    if not file_allowed:
        print(f"REJECTED FILE TYPE: {file.content_type} for file: {file.filename}")
        print(f"ALLOWED TYPES: {list(ALLOWED_SLIDE_TYPES.keys())}")
        print(f"ALLOWED EXTENSIONS: {list(ALLOWED_EXTENSIONS.keys())}")
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. Allowed types: {', '.join(ALLOWED_SLIDE_TYPES.keys())} or files with extensions: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )

    os.makedirs(f"{settings.slides_path}/{class_id}", exist_ok=True)

    file_extension = ALLOWED_SLIDE_TYPES[effective_content_type]
    filename = f"{len(os.listdir(f'{settings.slides_path}/{class_id}')) + 1}_{file.filename}"
    file_path = f"{settings.slides_path}/{class_id}/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    next_order = db.query(Slide).filter(Slide.class_id == class_id).count() + 1

    db_slide = Slide(
        title=title,
        filename=filename,
        file_path=file_path,
        file_type=effective_content_type,
        class_id=class_id,
        upload_order=next_order
    )
    db.add(db_slide)
    db.commit()
    db.refresh(db_slide)

    # Process the document for vector storage (async operation)
    processing_success = False
    processing_message = ""
    chunks_created = 0

    try:
        print(f"Starting document processing for slide: {db_slide.title}")
        success = document_processor.process_document(db_slide, db)
        if success:
            # Count the chunks created
            chunks_created = db.query(DocumentChunk).filter(DocumentChunk.slide_id == db_slide.id).count()
            processing_success = True
            processing_message = f"Successfully processed document into {chunks_created} searchable chunks"
            print(f"API: Vectorization completed for {db_slide.title} - ready to respond")
        else:
            print(f"Document processing failed for: {db_slide.title}")
            processing_message = "Document processing failed - content uploaded but not searchable"
    except Exception as e:
        print(f"Error during document processing for {db_slide.title}: {e}")
        processing_message = f"Document processing error: {str(e)}"
        # Don't fail the upload if document processing fails

    # Create response with processing info
    response_data = {
        **db_slide.__dict__,
        "processing_success": processing_success,
        "processing_message": processing_message,
        "chunks_created": chunks_created
    }

    return response_data

@router.get("/class/{class_id}", response_model=List[SlideSchema])
def get_class_slides(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
        raise HTTPException(status_code=403, detail="Not enrolled in this class")

    slides = db.query(Slide).filter(Slide.class_id == class_id).order_by(Slide.upload_order).all()
    return slides

@router.get("/{slide_id}")
def view_slide(
    slide_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    class_obj = db.query(Class).filter(Class.id == slide.class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
        raise HTTPException(status_code=403, detail="Not enrolled in this class")

    if not os.path.exists(slide.file_path):
        raise HTTPException(status_code=404, detail="Slide file not found")

    return FileResponse(
        slide.file_path,
        media_type=slide.file_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Content-Disposition": "inline",  # Force inline viewing, not download
            "X-Content-Type-Options": "nosniff"
        }
    )

@router.delete("/{slide_id}")
def delete_slide(
    slide_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    # Count and delete associated document chunks first
    chunks_deleted = db.query(DocumentChunk).filter(DocumentChunk.slide_id == slide.id).count()
    db.query(DocumentChunk).filter(DocumentChunk.slide_id == slide.id).delete()

    if os.path.exists(slide.file_path):
        os.remove(slide.file_path)

    slide_title = slide.title
    db.delete(slide)
    db.commit()

    return {
        "detail": f"Document '{slide_title}' deleted successfully",
        "vectors_deleted": chunks_deleted,
        "message": f"Removed {chunks_deleted} vector embeddings from the knowledge base"
    }

@router.put("/{slide_id}/reorder")
def reorder_slide(
    slide_id: int,
    new_order: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    class_slides = db.query(Slide).filter(Slide.class_id == slide.class_id).order_by(Slide.upload_order).all()

    if new_order < 1 or new_order > len(class_slides):
        raise HTTPException(status_code=400, detail="Invalid order position")

    old_order = slide.upload_order

    if new_order > old_order:
        for s in class_slides:
            if old_order < s.upload_order <= new_order:
                s.upload_order -= 1
    else:
        for s in class_slides:
            if new_order <= s.upload_order < old_order:
                s.upload_order += 1

    slide.upload_order = new_order
    db.commit()
    return {"detail": "Slide reordered successfully"}