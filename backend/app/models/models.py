from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class_users = Table(
    'class_users',
    Base.metadata,
    Column('class_id', Integer, ForeignKey('classes.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class_flashcards = Table(
    'class_flashcards',
    Base.metadata,
    Column('class_id', Integer, ForeignKey('classes.id')),
    Column('flashcard_id', Integer, ForeignKey('flashcards.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    enrolled_classes = relationship("Class", secondary=class_users, back_populates="students")

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User")
    students = relationship("User", secondary=class_users, back_populates="enrolled_classes")
    slides = relationship("Slide", back_populates="class_obj")
    resources = relationship("Resource", back_populates="class_obj")
    flashcards = relationship("Flashcard", secondary=class_flashcards, back_populates="assigned_classes")

class Slide(Base):
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    upload_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    class_obj = relationship("Class", back_populates="slides")
    chunks = relationship("DocumentChunk", back_populates="slide")

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    is_global = Column(Boolean, default=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    class_obj = relationship("Class", back_populates="resources")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, nullable=False, index=True)
    definition = Column(Text, nullable=False)
    category = Column(String, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User")
    assigned_classes = relationship("Class", secondary=class_flashcards, back_populates="flashcards")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    slide_id = Column(Integer, ForeignKey("slides.id"))
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunks within the document
    embedding = Column(JSON)  # Store the vector embedding as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    slide = relationship("Slide", back_populates="chunks")