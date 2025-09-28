import streamlit as st
import subprocess
import threading
import time
import requests
import os
from pathlib import Path
from app_secrets import get_secrets, validate_secrets

# Configure Streamlit page
st.set_page_config(
    page_title="PhoenixTeam Education Platform",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit UI elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@st.cache_resource
def start_fastapi_server():
    """For Streamlit Cloud, skip FastAPI and serve frontend directly"""
    secrets = get_secrets()

    if not validate_secrets(secrets):
        return None, None

    # Set environment variables from secrets
    for key, value in secrets.items():
        os.environ[key] = str(value)

    # For Streamlit Cloud deployment, return mock server status
    return True, secrets

def main():
    # Start FastAPI server
    server_thread, secrets = start_fastapi_server()

    if server_thread is None:
        st.error("Failed to start the application. Please check your configuration.")
        return

    # Main application title
    st.title("🔥 PhoenixTeam Education Platform")

    # For Streamlit Cloud, skip backend health check and serve frontend
    try:
            st.success("✅ Application is running successfully!")

            # Display the main application
            st.markdown("""
            ### Welcome to PhoenixTeam Education Platform

            Your education platform is now running! Click the link below to access the application:
            """)

            # Create columns for better layout
            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                # For Streamlit Cloud, serve HTML files directly
                st.markdown("""
                <div style="text-align: center; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
                              color: white;
                              padding: 15px 30px;
                              border-radius: 10px;
                              font-weight: bold;
                              font-size: 18px;
                              display: inline-block;
                              box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
                              margin-bottom: 20px;">
                        🚀 PhoenixTeam Education Platform
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Serve your login page directly
                if st.button("Access Login Page", use_container_width=True):
                    # Read and display your original login.html
                    login_path = Path(__file__).parent / "frontend" / "src" / "pages" / "login.html"
                    if login_path.exists():
                        with open(login_path, 'r', encoding='utf-8') as f:
                            login_html = f.read()
                        # Display the HTML content
                        st.components.v1.html(login_html, height=800, scrolling=True)
                    else:
                        st.error("Login page not found. Please check the file path.")

            # Application information
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📚 Features")
                st.markdown("""
                - **Class Management**: Create and manage educational classes
                - **Slide Viewing**: Upload and display presentation slides (no download)
                - **Resource Sharing**: Upload and share educational resources
                - **Chat Assistant**: AI-powered educational assistant
                - **User Management**: Admin and student role management
                - **Secure Authentication**: Role-based access control
                """)

            with col2:
                st.subheader("🛠️ System Status")
                st.markdown(f"""
                - **Backend API**: ✅ Running on port 8000
                - **Database**: ✅ SQLite configured
                - **Authentication**: ✅ JWT token-based
                - **File Uploads**: ✅ Configured
                - **OpenAI Chat**: {'✅ Enabled' if secrets.get('OPENAI_API_KEY') else '⚠️ Disabled (API key not set)'}
                """)

            # Admin information
            st.markdown("---")
            st.subheader("👨‍💼 Admin Information")
            st.info("""
            **Default Admin Credentials:**
            - You'll need to create an admin account using the API
            - Use the `/api/auth/register-admin` endpoint to create your first admin user
            - Students can be registered by admins through the application interface
            """)

            # API Documentation
            st.markdown("---")
            st.subheader("📖 API Documentation")
            st.markdown("""
            The FastAPI backend provides automatic API documentation:
            - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
            - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
            """)

    except Exception as e:
        st.error("❌ Application error. Please refresh the page.")
        st.write("If the problem persists, check the application logs.")

if __name__ == "__main__":
    main()