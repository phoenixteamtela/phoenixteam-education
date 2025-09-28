from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from openai import OpenAI

from ..core.database import get_db
from ..core.config import settings
from ..models.models import ChatMessage, User
from ..schemas.schemas import ChatMessageCreate, ChatMessage as ChatMessageSchema
from .auth import get_current_user
from ..services.rag_service import rag_service

router = APIRouter()

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

@router.post("/", response_model=ChatMessageSchema)
async def send_message(
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not openai_client or not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat functionality requires OpenAI API key configuration. Please check the setup documentation."
        )

    try:
        # Get user's course context using RAG
        user_context = rag_service.get_user_context(current_user, db)

        # Find relevant context for the user's question
        relevant_context = rag_service.find_relevant_context(
            message_data.message,
            user_context,
            top_k=5
        )

        # Create system prompt with relevant context
        system_prompt = rag_service.create_system_prompt(current_user, relevant_context)

        # Call OpenAI with context-aware prompt
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message_data.message
                }
            ],
            max_tokens=500,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        chat_message = ChatMessage(
            user_id=current_user.id,
            message=message_data.message,
            response=ai_response
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)

        return chat_message

    except Exception as e:
        import traceback
        print(f"Chat endpoint error: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error communicating with OpenAI: {str(e)}"
        )

@router.get("/history", response_model=List[ChatMessageSchema])
def get_chat_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    return messages[::-1]

@router.delete("/history")
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).delete()
    db.commit()
    return {"detail": "Chat history cleared successfully"}