from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.models import Class, User
from ..schemas.schemas import ClassCreate, Class as ClassSchema
from .auth import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/", response_model=ClassSchema)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_class = Class(
        name=class_data.name,
        description=class_data.description,
        created_by=current_user.id
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/", response_model=List[ClassSchema])
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.is_admin:
        return db.query(Class).filter(Class.is_active == True).all()
    else:
        return current_user.enrolled_classes

@router.get("/{class_id}", response_model=ClassSchema)
def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
        raise HTTPException(status_code=403, detail="Not enrolled in this class")

    return class_obj

@router.put("/{class_id}", response_model=ClassSchema)
def update_class(
    class_id: int,
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    class_obj.name = class_data.name
    class_obj.description = class_data.description
    db.commit()
    db.refresh(class_obj)
    return class_obj

@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    class_obj.is_active = False
    db.commit()
    return {"detail": "Class deleted successfully"}

@router.post("/{class_id}/enroll/{user_id}")
def enroll_user(
    class_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user in class_obj.students:
        raise HTTPException(status_code=400, detail="User already enrolled in this class")

    class_obj.students.append(user)
    db.commit()
    return {"detail": "User enrolled successfully"}

@router.delete("/{class_id}/unenroll/{user_id}")
def unenroll_user(
    class_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in class_obj.students:
        raise HTTPException(status_code=400, detail="User not enrolled in this class")

    class_obj.students.remove(user)
    db.commit()
    return {"detail": "User unenrolled successfully"}

@router.get("/{class_id}/students", response_model=List[dict])
def get_class_students(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    return [{"id": user.id, "username": user.username, "email": user.email}
            for user in class_obj.students if user.is_active and not user.is_admin]

@router.post("/{class_id}/assign-user")
def assign_user_to_class(
    class_id: int,
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Assign a user to a class"""
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user in class_obj.students:
        raise HTTPException(status_code=400, detail="User already enrolled in this class")

    class_obj.students.append(user)
    db.commit()
    return {"detail": f"User {user.username} assigned to class {class_obj.name} successfully"}

@router.post("/{class_id}/unassign-user")
def unassign_user_from_class(
    class_id: int,
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Unassign a user from a class"""
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in class_obj.students:
        raise HTTPException(status_code=400, detail="User not enrolled in this class")

    class_obj.students.remove(user)
    db.commit()
    return {"detail": f"User {user.username} removed from class {class_obj.name} successfully"}

@router.get("/{class_id}/stats")
def get_class_stats(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get basic class statistics (accessible to enrolled students and admins)"""
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user has access to this class
    if not current_user.is_admin and class_obj not in current_user.enrolled_classes:
        raise HTTPException(status_code=403, detail="Not enrolled in this class")

    # Count slides/content
    content_count = len([slide for slide in class_obj.slides])

    # Count students (only active, non-admin users)
    student_count = len([student for student in class_obj.students
                        if student.is_active and not student.is_admin])

    return {
        "content_count": content_count,
        "student_count": student_count
    }