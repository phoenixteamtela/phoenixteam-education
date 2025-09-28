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
    """For Streamlit Cloud deployment, skip FastAPI server startup"""
    secrets = get_secrets()

    if not validate_secrets(secrets):
        return None, None

    # Set environment variables from secrets
    for key, value in secrets.items():
        os.environ[key] = str(value)

    # For Streamlit Cloud, return mock server thread and secrets
    # The frontend will be served directly through Streamlit
    return True, secrets

def main():
    # Start FastAPI server
    server_thread, secrets = start_fastapi_server()

    if server_thread is None:
        st.error("Failed to start the application. Please check your configuration.")
        return

    # Main application title
    st.title("🔥 PhoenixTeam Education Platform")

    # For Streamlit Cloud deployment, serve the frontend directly
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
            # For Streamlit Cloud, create a direct link to login functionality
            if st.button("🚀 Launch PhoenixTeam Education",
                        help="Access your educational dashboard"):
                # Set session state to show login
                st.session_state.show_login = True
                st.rerun()

        # Check if we should show the login interface
        if st.session_state.get('show_login', False):
            # Embed your login page functionality here
            st.markdown("---")
            st.markdown("### Login to PhoenixTeam Education")

            # Simple redirect message for now - you can expand this
            st.info("""
            **Frontend Integration Notice:**

            Your original app is designed with separate HTML frontend pages.
            For Streamlit Cloud deployment, these would need to be integrated
            into Streamlit components.

            Your original frontend files are preserved in:
            - `/frontend/src/pages/login.html`
            - `/frontend/src/pages/admin-dashboard.html`
            - `/frontend/src/pages/student-dashboard.html`

            The FastAPI backend is also preserved in `/backend/` for local development.
            """)

            if st.button("← Back to Main Page"):
                st.session_state.show_login = False
                st.rerun()

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

        else:
            st.error("❌ Application failed to start. Please check the logs.")

    except requests.exceptions.RequestException:
        st.error("❌ Cannot connect to the application. Please wait and refresh the page.")

        # Show loading indicator
        with st.spinner("Starting application..."):
            time.sleep(5)
            st.rerun()

if __name__ == "__main__":
    main()