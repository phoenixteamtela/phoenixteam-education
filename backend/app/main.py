from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .core.config import settings
from .core.database import engine, get_db
from .models import models
from .api import auth, classes, slides, resources, chat, flashcards

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PhoenixTeam Education Platform",
    description="An education platform for managing classes, slides, and resources",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend/src"), name="static")
app.mount("/uploads", StaticFiles(directory="../uploads"), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(classes.router, prefix="/api/classes", tags=["classes"])
app.include_router(slides.router, prefix="/api/slides", tags=["slides"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(flashcards.router, prefix="/api/flashcards", tags=["flashcards"])

@app.get("/")
async def root():
    return {"message": "PhoenixTeam Education Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}