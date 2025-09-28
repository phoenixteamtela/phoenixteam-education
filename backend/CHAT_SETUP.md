# Chat with RAG Setup Guide

## Overview
The chat system now includes RAG (Retrieval-Augmented Generation) functionality that allows students to ask questions about their assigned flashcards and course content using OpenAI's API.

## Setup Instructions

### 1. OpenAI API Key Configuration
1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### 2. How It Works

#### For Students:
- Chat is available in the student dashboard
- Students can ask questions about their assigned flashcards and course materials
- The AI will only answer questions related to their enrolled classes
- Examples of questions students can ask:
  - "What is the definition of [term from flashcard]?"
  - "Explain [concept from their flashcards]"
  - "What documents are available in my [class name] class?"
  - "Help me understand [topic from their course materials]"

#### For Administrators:
- Admins can use chat but will have access to all flashcards and content
- Same AI assistant but with broader access to the platform's content

### 3. Technical Details

#### RAG Implementation:
- Uses **sentence-transformers** with the 'all-MiniLM-L6-v2' model for embeddings
- Semantic similarity search to find relevant context
- Only retrieves content from classes the student is enrolled in
- Combines flashcards and document metadata for context

#### Context Sources:
- **Flashcards**: Term, definition, category, and source class
- **Documents**: Document titles, types, and source class
- **Scope**: Limited to user's enrolled classes for privacy

#### AI Model:
- Uses **OpenAI GPT-3.5-turbo**
- Context-aware prompts with relevant course materials
- Educational focus with appropriate response filtering

### 4. Testing the Chat

1. **Create test data**:
   - Enroll a student in a class
   - Assign flashcards to that class
   - Upload some documents to the class

2. **Test questions**:
   - Ask about specific flashcard terms
   - Request explanations of concepts
   - Inquire about available materials

3. **Expected behavior**:
   - AI responds with information from assigned materials
   - Redirects off-topic questions back to course content
   - Provides educational, helpful responses

### 5. Error Handling

- If no OpenAI API key: Returns 503 "OpenAI API key not configured"
- If no relevant context found: AI explains what materials are available
- If API errors: Returns 500 with error details

### 6. Privacy & Security

- Students only see content from their enrolled classes
- No cross-contamination between different students' materials
- Chat history is stored per user in the database
- All API calls are authenticated and authorized

## Customization Options

You can modify the RAG behavior by editing `app/services/rag_service.py`:
- Change the embedding model
- Adjust similarity thresholds
- Modify the system prompt template
- Add more content sources (e.g., full PDF text extraction)