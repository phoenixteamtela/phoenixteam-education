from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClassBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    students: List[User] = []

    class Config:
        from_attributes = True

class SlideBase(BaseModel):
    title: str

class SlideCreate(SlideBase):
    class_id: int

class Slide(SlideBase):
    id: int
    filename: str
    file_path: str
    file_type: str
    class_id: int
    upload_order: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_global: bool = False

class ResourceCreate(ResourceBase):
    class_id: Optional[int] = None

class Resource(ResourceBase):
    id: int
    filename: str
    file_path: str
    file_type: str
    class_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessage(BaseModel):
    id: int
    user_id: int
    message: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FlashcardBase(BaseModel):
    term: str
    definition: str
    category: Optional[str] = None

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class Flashcard(FlashcardBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FlashcardBulkCreate(BaseModel):
    flashcards: List[FlashcardBase]

class FlashcardAssignment(BaseModel):
    flashcard_id: int
    class_ids: List[int]

class DocumentChunkBase(BaseModel):
    chunk_text: str
    chunk_index: int

class DocumentChunk(DocumentChunkBase):
    id: int
    slide_id: int
    created_at: datetime

    class Config:
        from_attributes = True