from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io

from ..core.database import get_db
from ..models.models import Flashcard, User, Class
from ..schemas.schemas import (
    FlashcardCreate,
    FlashcardUpdate,
    Flashcard as FlashcardSchema,
    FlashcardBulkCreate,
    FlashcardAssignment
)
from .auth import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/", response_model=FlashcardSchema)
def create_flashcard(
    flashcard_data: FlashcardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new flashcard (admin only)"""
    db_flashcard = Flashcard(
        term=flashcard_data.term,
        definition=flashcard_data.definition,
        category=flashcard_data.category,
        created_by=current_user.id
    )
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard

@router.post("/bulk", response_model=List[FlashcardSchema])
def create_flashcards_bulk(
    bulk_data: FlashcardBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create multiple flashcards at once (admin only)"""
    db_flashcards = []

    for flashcard_data in bulk_data.flashcards:
        db_flashcard = Flashcard(
            term=flashcard_data.term,
            definition=flashcard_data.definition,
            category=flashcard_data.category,
            created_by=current_user.id
        )
        db.add(db_flashcard)
        db_flashcards.append(db_flashcard)

    db.commit()

    for flashcard in db_flashcards:
        db.refresh(flashcard)

    return db_flashcards

@router.post("/bulk-excel", response_model=List[FlashcardSchema])
async def create_flashcards_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create multiple flashcards from Excel file (admin only)"""

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an Excel file (.xlsx or .xls)"
        )

    try:
        # Read Excel file content
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))

        # Validate required columns
        required_columns = ['term', 'definition']
        missing_columns = [col for col in required_columns if col.lower() not in df.columns.str.lower()]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}. Expected columns: Term, Definition, Category (optional)"
            )

        # Normalize column names
        df.columns = df.columns.str.lower()

        # Process flashcards
        db_flashcards = []
        errors = []

        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row.get('term')) or pd.isna(row.get('definition')):
                    continue

                term = str(row['term']).strip()
                definition = str(row['definition']).strip()
                category = str(row.get('category', '')).strip() if not pd.isna(row.get('category')) else None

                if not term or not definition:
                    errors.append(f"Row {index + 2}: Term and definition cannot be empty")
                    continue

                # Create flashcard
                db_flashcard = Flashcard(
                    term=term,
                    definition=definition,
                    category=category if category else None,
                    created_by=current_user.id
                )
                db.add(db_flashcard)
                db_flashcards.append(db_flashcard)

            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")

        if not db_flashcards:
            if errors:
                raise HTTPException(status_code=400, detail=f"No valid flashcards found. Errors: {'; '.join(errors[:5])}")
            else:
                raise HTTPException(status_code=400, detail="No flashcards found in the file")

        # Commit all flashcards
        db.commit()

        # Refresh all flashcards
        for flashcard in db_flashcards:
            db.refresh(flashcard)

        return db_flashcards

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Excel file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid Excel file format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

@router.get("/", response_model=List[FlashcardSchema])
def get_flashcards(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all flashcards (admin only)"""
    query = db.query(Flashcard).filter(Flashcard.is_active == True)

    if category:
        query = query.filter(Flashcard.category == category)

    return query.all()

@router.get("/class/{class_id}", response_model=List[FlashcardSchema])
def get_flashcards_for_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get flashcards assigned to a specific class"""
    # Check if class exists and user has access
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
        raise HTTPException(status_code=403, detail="Not enrolled in this class")

    return class_obj.flashcards

@router.get("/categories", response_model=List[str])
def get_flashcard_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all unique flashcard categories (admin only)"""
    categories = db.query(Flashcard.category).filter(
        Flashcard.category.isnot(None),
        Flashcard.is_active == True
    ).distinct().all()

    return [cat[0] for cat in categories if cat[0]]

@router.get("/{flashcard_id}", response_model=FlashcardSchema)
def get_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific flashcard"""
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.is_active == True
    ).first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # If not admin, check if user has access to this flashcard through their classes
    if not current_user.is_admin:
        user_flashcards = []
        for class_obj in current_user.enrolled_classes:
            user_flashcards.extend(class_obj.flashcards)

        if flashcard not in user_flashcards:
            raise HTTPException(status_code=403, detail="No access to this flashcard")

    return flashcard

@router.put("/{flashcard_id}", response_model=FlashcardSchema)
def update_flashcard(
    flashcard_id: int,
    flashcard_update: FlashcardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a flashcard (admin only)"""
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    update_data = flashcard_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(flashcard, field, value)

    db.commit()
    db.refresh(flashcard)
    return flashcard

@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a flashcard (admin only)"""
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Soft delete
    flashcard.is_active = False
    db.commit()

    return {"message": "Flashcard deleted successfully"}

@router.post("/{flashcard_id}/assign")
def assign_flashcard_to_classes(
    flashcard_id: int,
    assignment: FlashcardAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Assign a flashcard to multiple classes (admin only)"""
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.is_active == True
    ).first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Clear existing assignments
    flashcard.assigned_classes.clear()

    # Add new assignments
    for class_id in assignment.class_ids:
        class_obj = db.query(Class).filter(
            Class.id == class_id,
            Class.is_active == True
        ).first()

        if class_obj:
            flashcard.assigned_classes.append(class_obj)

    db.commit()

    return {"message": f"Flashcard assigned to {len(assignment.class_ids)} classes"}

@router.delete("/{flashcard_id}/unassign/{class_id}")
def unassign_flashcard_from_class(
    flashcard_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Unassign a flashcard from a specific class (admin only)"""
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.is_active == True
    ).first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.is_active == True
    ).first()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if class_obj in flashcard.assigned_classes:
        flashcard.assigned_classes.remove(class_obj)
        db.commit()
        return {"message": "Flashcard unassigned from class"}
    else:
        raise HTTPException(status_code=400, detail="Flashcard is not assigned to this class")