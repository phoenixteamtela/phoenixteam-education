import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.config import settings
from ..models.models import Resource, Class, User
from ..schemas.schemas import ResourceCreate, Resource as ResourceSchema
from .auth import get_current_user, get_current_admin_user

router = APIRouter()

ALLOWED_RESOURCE_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-powerpoint": ".ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "text/plain": ".txt",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "application/zip": ".zip",
    "video/mp4": ".mp4",
    "video/mpeg": ".mpeg",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav"
}

@router.post("/upload", response_model=ResourceSchema)
async def upload_resource(
    title: str,
    description: Optional[str] = None,
    is_global: bool = False,
    class_id: Optional[int] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    if file.content_type not in ALLOWED_RESOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_RESOURCE_TYPES.keys())}"
        )

    if not is_global and not class_id:
        raise HTTPException(status_code=400, detail="class_id required for class-specific resources")

    if class_id:
        class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")

    folder_path = f"{settings.resources_path}/global" if is_global else f"{settings.resources_path}/class_{class_id}"
    os.makedirs(folder_path, exist_ok=True)

    file_extension = ALLOWED_RESOURCE_TYPES[file.content_type]
    filename = f"{len(os.listdir(folder_path)) + 1}_{file.filename}"
    file_path = f"{folder_path}/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_resource = Resource(
        title=title,
        description=description,
        filename=filename,
        file_path=file_path,
        file_type=file.content_type,
        is_global=is_global,
        class_id=class_id if not is_global else None
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.get("/global", response_model=List[ResourceSchema])
def get_global_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Resource).filter(Resource.is_global == True).all()

@router.get("/class/{class_id}", response_model=List[ResourceSchema])
def get_class_resources(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
        raise HTTPException(status_code=403, detail="Not enrolled in this class")

    return db.query(Resource).filter(Resource.class_id == class_id).all()

@router.get("/{resource_id}")
def download_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if not resource.is_global:
        class_obj = db.query(Class).filter(Class.id == resource.class_id, Class.is_active == True).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")

        if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
            raise HTTPException(status_code=403, detail="Not enrolled in this class")

    if not os.path.exists(resource.file_path):
        raise HTTPException(status_code=404, detail="Resource file not found")

    return FileResponse(
        resource.file_path,
        media_type=resource.file_type,
        filename=resource.filename
    )

@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if os.path.exists(resource.file_path):
        os.remove(resource.file_path)

    db.delete(resource)
    db.commit()
    return {"detail": "Resource deleted successfully"}

@router.put("/{resource_id}", response_model=ResourceSchema)
def update_resource(
    resource_id: int,
    title: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.title = title
    if description is not None:
        resource.description = description

    db.commit()
    db.refresh(resource)
    return resource