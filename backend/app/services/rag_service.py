from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
import numpy as np

from ..models.models import User, Class, Flashcard, DocumentChunk
from ..core.config import settings

class RAGService:
    def __init__(self):
        try:
            # Use a lightweight, fast sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            self.embedding_model = None

    def get_user_context(self, user: User, db: Session) -> Dict[str, List[str]]:
        """Get all relevant context for a user (flashcards and document chunks from enrolled classes)"""
        context = {
            'flashcards': [],
            'document_chunks': []
        }

        # Admin users get access to ALL content, regular users only their enrolled classes
        if user.is_admin:
            print(f"RAG Debug: Admin user {user.username} - accessing ALL content")
            classes_to_process = db.query(Class).filter(Class.is_active == True).all()
        else:
            print(f"RAG Debug: User {user.username} enrolled in {len(user.enrolled_classes)} classes")
            classes_to_process = user.enrolled_classes

        # Get flashcards from relevant classes
        for enrolled_class in classes_to_process:
            print(f"RAG Debug: Processing class {enrolled_class.name} (ID: {enrolled_class.id})")

            # Get flashcards assigned to this class
            class_flashcards = db.query(Flashcard).filter(
                Flashcard.assigned_classes.any(Class.id == enrolled_class.id),
                Flashcard.is_active == True
            ).all()

            print(f"RAG Debug: Found {len(class_flashcards)} flashcards for class {enrolled_class.name}")

            for flashcard in class_flashcards:
                flashcard_text = f"Term: {flashcard.term}\nDefinition: {flashcard.definition}"
                if flashcard.category:
                    flashcard_text += f"\nCategory: {flashcard.category}"
                flashcard_text += f"\nClass: {enrolled_class.name}"
                context['flashcards'].append(flashcard_text)

            # Get pre-computed document chunks from class slides
            for slide in enrolled_class.slides:
                # Get all chunks for this slide
                slide_chunks = db.query(DocumentChunk).filter(
                    DocumentChunk.slide_id == slide.id
                ).order_by(DocumentChunk.chunk_index).all()

                print(f"RAG Debug: Found {len(slide_chunks)} chunks for document {slide.title}")

                for chunk in slide_chunks:
                    chunk_text = f"Document: {slide.title}\nClass: {enrolled_class.name}\nContent: {chunk.chunk_text}"
                    context['document_chunks'].append(chunk_text)

        print(f"RAG Debug: Total context - {len(context['flashcards'])} flashcards, {len(context['document_chunks'])} document chunks")
        return context


    def find_relevant_context(self, query: str, user_context: Dict[str, List[str]], top_k: int = 5) -> List[str]:
        """Find the most relevant context pieces for a given query using semantic similarity"""
        all_context = []

        # Combine all context with source labels
        for flashcard in user_context['flashcards']:
            all_context.append(f"[FLASHCARD] {flashcard}")

        for chunk in user_context['document_chunks']:
            all_context.append(f"[DOCUMENT_CHUNK] {chunk}")

        print(f"RAG Debug: Query: '{query}' - Processing {len(all_context)} total context items")

        if not all_context:
            print("RAG Debug: No context available")
            return []

        # If embedding model is not available, return all context (fallback)
        if not self.embedding_model:
            return all_context[:top_k]

        try:
            # Generate embeddings
            query_embedding = self.embedding_model.encode([query])
            context_embeddings = self.embedding_model.encode(all_context)

            # Calculate similarities
            similarities = cosine_similarity(query_embedding, context_embeddings)[0]

            # Get top_k most similar contexts
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            # Filter out very low similarity scores (threshold: 0.1 - lowered for better recall)
            relevant_contexts = []
            for idx in top_indices:
                if similarities[idx] > 0.1:
                    relevant_contexts.append(all_context[idx])
                    print(f"RAG Debug: Relevant context (similarity {similarities[idx]:.3f}): {all_context[idx][:100]}...")

            print(f"RAG Debug: Found {len(relevant_contexts)} relevant contexts above threshold 0.1")
            return relevant_contexts

        except Exception as e:
            print(f"Error in semantic search: {e}")
            # Fallback to returning first few contexts
            return all_context[:top_k]

    def create_system_prompt(self, user: User, relevant_context: List[str]) -> str:
        """Create a system prompt with relevant context"""
        base_prompt = f"""You are a helpful educational AI assistant for {user.username} on the PhoenixTeam Education Platform.

Your role is to help students understand their course materials, including flashcards and documents from their enrolled classes.

IMPORTANT GUIDELINES:
- Only answer questions related to the student's course materials
- If a question is not related to their studies, politely redirect them to their course content
- Be encouraging and educational in your responses
- Provide clear, concise explanations
- When referencing flashcards, you can quote the term and definition
- For document-related questions, refer to the document titles available

"""

        if relevant_context:
            base_prompt += f"""
RELEVANT COURSE MATERIALS:
{chr(10).join(relevant_context)}

Please use this information to answer the student's question. If the question cannot be answered using the available course materials, let the student know and suggest they review their assigned materials or contact their instructor.
"""
        else:
            base_prompt += """
No specific course materials were found relevant to this question. Please encourage the student to review their assigned flashcards and documents, or ask questions directly related to their course content.
"""

        return base_prompt

# Global instance
rag_service = RAGService()