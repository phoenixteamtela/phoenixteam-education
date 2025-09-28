import os
import pypdf
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
import re

from ..models.models import Slide, DocumentChunk

class DocumentProcessor:
    def __init__(self):
        try:
            # Use the same lightweight model as RAG service
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Document processor: Embedding model loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            self.embedding_model = None

    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Handle relative paths by making them absolute
            if not os.path.isabs(pdf_path):
                # Assuming uploads are relative to backend directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go up from app/services/
                pdf_path = os.path.join(base_dir, pdf_path)

            print(f"Document processor: Extracting text from PDF: {pdf_path}")

            if not os.path.exists(pdf_path):
                print(f"Document processor: PDF file not found at: {pdf_path}")
                return ""

            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"

                print(f"Document processor: Extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
                return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text from {pdf_path}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []

        # Clean up the text - remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        chunks = []
        start = 0

        while start < len(text):
            # Find the end of this chunk
            end = start + chunk_size

            if end >= len(text):
                # Last chunk
                chunks.append(text[start:].strip())
                break

            # Try to break at a sentence or paragraph boundary
            break_point = end
            for i in range(end, max(start + chunk_size - 200, start), -1):
                if text[i] in '.!?':
                    break_point = i + 1
                    break
                elif text[i] in '\n\r':
                    break_point = i
                    break

            chunk = text[start:break_point].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = break_point - overlap
            if start < 0:
                start = 0

        print(f"Document processor: Split text into {len(chunks)} chunks")
        return chunks

    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        if not self.embedding_model or not chunks:
            return []

        try:
            print(f"Document processor: Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embedding_model.encode(chunks)
            # Convert numpy arrays to Python lists for JSON storage
            return [embedding.tolist() for embedding in embeddings]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []

    def process_document(self, slide: Slide, db: Session) -> bool:
        """Process a document: extract text, chunk it, generate embeddings, and store in database"""
        try:
            print(f"Document processor: Processing document {slide.title} (ID: {slide.id})")
            print(f"Document processor: File type is: '{slide.file_type}' (lowered: '{slide.file_type.lower()}')")

            # Only process PDF files
            if slide.file_type.lower() != 'application/pdf':
                print(f"Document processor: Skipping non-PDF file: {slide.file_type}")
                return True

            # Extract text from PDF
            text = self.extract_pdf_text(slide.file_path)
            if not text:
                print(f"Document processor: No text extracted from {slide.title}")
                return False

            # Split text into chunks
            chunks = self.chunk_text(text)
            if not chunks:
                print(f"Document processor: No chunks created from {slide.title}")
                return False

            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            if not embeddings:
                print(f"Document processor: No embeddings generated for {slide.title}")
                # Still store text chunks without embeddings as fallback
                embeddings = [None] * len(chunks)

            # Delete existing chunks for this slide (in case of reprocessing)
            db.query(DocumentChunk).filter(DocumentChunk.slide_id == slide.id).delete()

            # Store chunks and embeddings in database
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                document_chunk = DocumentChunk(
                    slide_id=slide.id,
                    chunk_text=chunk_text,
                    chunk_index=i,
                    embedding=embedding
                )
                db.add(document_chunk)

            # Commit the vectorization to database
            db.commit()

            # Print success message after vectorization is complete
            print(f"Document processor: Successfully processed {slide.title} - stored {len(chunks)} chunks with embeddings")
            return True

        except Exception as e:
            print(f"Error processing document {slide.title}: {e}")
            db.rollback()
            return False

# Global instance
document_processor = DocumentProcessor()