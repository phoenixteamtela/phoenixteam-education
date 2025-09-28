#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import time
import os
from pathlib import Path
from app_secrets import get_secrets, validate_secrets

# Configure Streamlit page
st.set_page_config(
    page_title="PhoenixTeam Education Platform",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Get secrets for Streamlit Cloud deployment
    secrets = get_secrets()
    validate_secrets(secrets)

    # Main application title
    st.title("🔥 PhoenixTeam Education Platform")

    st.success("✅ PhoenixTeam Education Platform (Streamlit Cloud Deployment)")

    # Display the main application
    st.markdown("""
    ### Welcome to PhoenixTeam Education Platform

    This is a demonstration of the PhoenixTeam Education Platform running on Streamlit Cloud.
    """)

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Platform Features")
        st.markdown("""
        - **Smart Flashcards**: AI-powered study cards with spaced repetition
        - **Class Management**: Organize students and course content
        - **File Upload**: Support for presentations, documents, and more
        - **Chat Assistant**: Get instant help with course material
        - **Progress Tracking**: Monitor learning progress and performance
        """)

        st.subheader("🎓 For Students")
        st.markdown("""
        - Access interactive flashcards
        - Ask questions about course material
        - Track your learning progress
        - Download study resources
        """)

    with col2:
        st.subheader("🛠️ System Status")
        st.markdown(f"""
        - **Deployment**: ✅ Streamlit Cloud
        - **Authentication**: ✅ JWT token-based
        - **File Processing**: ✅ Document analysis ready
        - **OpenAI Chat**: {'✅ Enabled' if secrets.get('OPENAI_API_KEY') else '⚠️ Disabled (API key not set)'}
        """)

        st.subheader("👨‍💼 For Administrators")
        st.markdown("""
        - Create and manage classes
        - Upload course materials
        - Monitor student progress
        - Generate AI-powered content
        """)

    # Demo section
    st.markdown("---")
    st.subheader("🎮 Try the Platform")

    if secrets.get('OPENAI_API_KEY'):
        st.markdown("**Chat Assistant Demo** - Ask a question about education or learning:")
        user_question = st.text_input("Ask me anything about education...")

        if user_question and st.button("Ask"):
            with st.spinner("Thinking..."):
                try:
                    # Import openai here to avoid errors if not configured
                    from openai import OpenAI
                    client = OpenAI(api_key=secrets.get('OPENAI_API_KEY'))

                    # Simple educational assistant
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an educational assistant helping students learn. Provide helpful, encouraging, and educational responses."},
                            {"role": "user", "content": user_question}
                        ]
                    )

                    st.write(f"**AI Assistant:** {response.choices[0].message.content}")
                except Exception as e:
                    st.error("Error connecting to OpenAI. Please check your API key configuration.")
    else:
        st.warning("⚠️ OpenAI Chat is disabled. Add your API key in the Streamlit secrets to enable chat functionality.")

    # Sample flashcards demo
    st.markdown("---")
    st.subheader("📚 Sample Flashcards")

    # Sample educational content
    sample_flashcards = [
        {"Question": "What is machine learning?", "Answer": "A subset of AI that enables computers to learn and improve from experience without being explicitly programmed."},
        {"Question": "What is the difference between supervised and unsupervised learning?", "Answer": "Supervised learning uses labeled data, while unsupervised learning finds patterns in unlabeled data."},
        {"Question": "What is a neural network?", "Answer": "A computing system inspired by biological neural networks, consisting of interconnected nodes (neurons)."}
    ]

    df = pd.DataFrame(sample_flashcards)
    st.dataframe(df, use_container_width=True)

    # Information section
    st.markdown("---")
    st.subheader("📖 About This Platform")
    st.info("""
    **PhoenixTeam Education Platform** is a comprehensive learning management system featuring:

    - AI-powered educational assistance
    - Interactive flashcard system with spaced repetition
    - Document processing and knowledge extraction
    - Real-time chat support for students
    - Administrative tools for content management

    This Streamlit deployment demonstrates the platform's frontend capabilities.
    The full platform includes a FastAPI backend for complete functionality.
    """)

    # Repository link
    st.markdown("---")
    st.markdown("**🔗 Source Code:** [GitHub Repository](https://github.com/phoenixteamtela/phoenixteam-education)")

if __name__ == "__main__":
    main()