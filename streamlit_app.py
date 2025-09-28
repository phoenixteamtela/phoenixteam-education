#!/usr/bin/env python3
import streamlit as st
import subprocess
import threading
import time
import requests
import os
import base64
from pathlib import Path
from app_secrets import get_secrets, validate_secrets

# Configure Streamlit page
st.set_page_config(
    page_title="PhoenixTeam Education Platform",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit UI elements and apply your custom CSS
def load_css():
    """Load your original CSS styling"""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}

    /* Your original CSS variables */
    :root {
        --phoenix-primary: #FF6B35;
        --phoenix-secondary: #1E2A4A;
        --phoenix-accent: #FFD23F;
        --phoenix-dark: #1A1A2E;
        --phoenix-light: #F7F7F7;
        --phoenix-white: #FFFFFF;
        --phoenix-gradient: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
        --phoenix-shadow: 0 4px 20px rgba(255, 107, 53, 0.15);
        --phoenix-border: #E5E5E5;
        --text-primary: #333333;
        --text-secondary: #666666;
        --text-muted: #999999;
    }

    /* Override Streamlit default styling */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    .stApp {
        background-color: var(--phoenix-light);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Login container styling */
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        padding: 20px;
        background: var(--phoenix-light);
    }

    .login-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--phoenix-gradient);
        opacity: 0.05;
        z-index: 1;
    }

    .gradient-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 40%, rgba(255, 107, 53, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 210, 63, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 80%, rgba(0, 78, 137, 0.05) 0%, transparent 50%);
    }

    .login-card {
        position: relative;
        z-index: 2;
        background: var(--phoenix-white);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 48px;
        max-width: 440px;
        width: 100%;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        margin: 0 auto;
    }

    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }

    .login-logo {
        height: 60px;
        width: auto;
        margin-bottom: 24px;
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
    }

    .login-header h1 {
        font-size: 2rem;
        font-weight: 600;
        color: #1E2A4A;
        margin-bottom: 8px;
    }

    /* Dashboard styling */
    .header {
        background: #f8f9fa;
        border-bottom: 1px solid var(--phoenix-border);
        padding: 16px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .header-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }

    .breadcrumb-nav {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .logo {
        height: 36px;
        width: auto;
        flex-shrink: 0;
    }

    .breadcrumb-separator {
        color: var(--text-muted);
        font-size: 1.2rem;
        font-weight: 300;
        margin: 0 4px;
    }

    .breadcrumb-item {
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-secondary);
        white-space: nowrap;
    }

    .breadcrumb-item.current {
        color: var(--phoenix-secondary);
        font-weight: 600;
    }

    .dashboard-layout {
        display: flex;
        min-height: calc(100vh - 62px);
    }

    .sidebar {
        width: 280px;
        background: var(--phoenix-white);
        border-right: 1px solid var(--phoenix-border);
        padding: 24px;
        min-height: calc(100vh - 73px);
    }

    .main-content {
        flex: 1;
        padding: 32px;
        background: var(--phoenix-light);
        overflow-y: auto;
    }

    .welcome-message h4 {
        color: var(--phoenix-secondary);
        margin-bottom: 8px;
    }

    .welcome-message p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 24px;
    }

    .card {
        background: var(--phoenix-white);
        border-radius: 12px;
        padding: 28px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--phoenix-border);
        transition: all 0.3s ease;
        margin-bottom: 24px;
    }

    .card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }

    .card h3 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 12px;
    }

    /* Button styling to match your design */
    .stButton > button {
        background: var(--phoenix-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--phoenix-shadow) !important;
        min-height: 48px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(255, 107, 53, 0.25) !important;
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        border: 2px solid var(--phoenix-border) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        transition: border-color 0.3s ease !important;
        background: var(--phoenix-white) !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--phoenix-primary) !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }

    /* Tabs styling */
    .stTabs > div > div > div > div {
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }

    .stTabs > div > div > div > div[data-testid="stMarkdownContainer"] p {
        font-weight: 500 !important;
    }

    /* Metrics styling */
    .metric-card {
        background: var(--phoenix-white);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--phoenix-border);
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--phoenix-primary);
        margin-bottom: 8px;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Hide Streamlit footer and menu */
    .stApp > footer {display: none;}
    .stApp > header {display: none;}
    .stApp > div > div > div > div > div > section > div {padding-top: 0rem;}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def get_logo_base64():
    """Get the PhoenixTeam logo as base64 for embedding"""
    try:
        logo_path = Path(__file__).parent / "assets" / "PhoenixTeam Horizontal_Gradient.png"
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return None

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

def show_login_page(secrets):
    """Display your original login page design"""
    logo_b64 = get_logo_base64()

    # Login container with your original styling
    st.markdown("""
    <div class="login-container">
        <div class="login-background">
            <div class="gradient-overlay"></div>
        </div>
        <div class="login-card">
            <div class="login-header">
    """, unsafe_allow_html=True)

    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="login-logo" alt="PhoenixTeam">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="height: 60px; margin-bottom: 24px; display: flex; align-items: center; justify-content: center; background: var(--phoenix-gradient); border-radius: 8px; color: white; font-weight: bold;">🔥 PhoenixTeam</div>', unsafe_allow_html=True)

    st.markdown("""
                <h1>Education Center</h1>
            </div>
    """, unsafe_allow_html=True)

    # Login form
    with st.form("login_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="margin-bottom: 20px;"><label style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--text-primary);">Username</label></div>', unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed")

            st.markdown('<div style="margin-bottom: 20px;"><label style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--text-primary);">Password</label></div>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")

            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if username and password:
                # Simple authentication using your app password
                app_password = secrets.get('APP_PASSWORD', 'phoenixteam2024')

                if username == 'admin' and password == app_password:
                    st.session_state.authenticated = True
                    st.session_state.user_role = 'admin'
                    st.session_state.username = username
                    st.rerun()
                elif password == app_password:  # Any username with correct password for students
                    st.session_state.authenticated = True
                    st.session_state.user_role = 'student'
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("Please enter both username and password.")

    st.markdown("""
        <div style="text-align: center; padding-top: 24px; border-top: 1px solid var(--phoenix-border); margin-top: 24px;">
            <p style="color: var(--text-muted); font-size: 0.9rem; margin: 0;">New to PhoenixTeam? Contact your administrator for access.</p>
        </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_header(title, user_type):
    """Display your original header design"""
    logo_b64 = get_logo_base64()

    st.markdown(f"""
    <div class="header">
        <div class="header-content">
            <div class="breadcrumb-nav">
                {f'<img src="data:image/png;base64,{logo_b64}" class="logo" alt="PhoenixTeam">' if logo_b64 else '<div style="height: 36px; width: 80px; background: var(--phoenix-gradient); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.8rem;">🔥 PT</div>'}
                <span class="breadcrumb-separator">›</span>
                <span class="breadcrumb-item">Education Center</span>
                <span class="breadcrumb-separator">›</span>
                <span class="breadcrumb-item current">{title}</span>
            </div>
            <div class="header-right">
                <span style="color: var(--text-secondary); margin-right: 16px;">Welcome, {st.session_state.username}!</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_admin_dashboard(secrets):
    """Display your original admin dashboard design"""
    show_header("Admin Dashboard", "admin")

    # Logout button
    if st.button("Logout", key="admin_logout"):
        for key in ['authenticated', 'user_role', 'username']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown('<div class="dashboard-layout">', unsafe_allow_html=True)

    # Sidebar
    col1, col2 = st.columns([280, 1000], gap="medium")

    with col1:
        st.markdown("""
        <div class="sidebar">
            <div class="welcome-message">
                <h4>Welcome back!</h4>
                <p>Admin Dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Quick Actions")
        if st.button("Create New Class", use_container_width=True):
            st.success("Class creation feature would be implemented here")
        if st.button("Upload Resource", use_container_width=True):
            st.success("Resource upload feature would be implemented here")
        if st.button("Manage Users", use_container_width=True):
            st.success("User management feature would be implemented here")
        if st.button("Manage Flashcards", use_container_width=True):
            st.success("Flashcard management feature would be implemented here")

    with col2:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        # Dashboard content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Classes", "📚 Resources", "💬 Chat Assistant"])

        with tab1:
            # Metrics cards
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">25</div>
                    <div class="metric-label">Total Students</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">4</div>
                    <div class="metric-label">Active Classes</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">48</div>
                    <div class="metric-label">Resources</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">156</div>
                    <div class="metric-label">Chat Sessions</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Recent Activity")

            activity_data = [
                {"Time": "10:30 AM", "User": "Sarah Johnson", "Action": "Completed flashcard set: Machine Learning Basics"},
                {"Time": "10:15 AM", "User": "Mike Chen", "Action": "Started quiz: Python Fundamentals"},
                {"Time": "9:45 AM", "User": "Admin", "Action": "Uploaded new resource: Data Science Guide"},
                {"Time": "9:30 AM", "User": "Emma Davis", "Action": "Asked question in chat about neural networks"}
            ]

            for activity in activity_data:
                st.markdown(f"""
                <div style="padding: 12px; border-bottom: 1px solid var(--phoenix-border); display: flex; justify-content: space-between;">
                    <div>
                        <strong>{activity['User']}</strong><br>
                        <span style="color: var(--text-secondary); font-size: 0.9rem;">{activity['Action']}</span>
                    </div>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">{activity['Time']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Class Management")

            classes_data = [
                {"Class": "AI & Machine Learning", "Students": 8, "Progress": "85%", "Status": "Active"},
                {"Class": "Data Science Fundamentals", "Students": 12, "Progress": "72%", "Status": "Active"},
                {"Class": "Python Programming", "Students": 15, "Progress": "90%", "Status": "Active"},
                {"Class": "Statistics & Analytics", "Students": 6, "Progress": "45%", "Status": "Active"}
            ]

            for class_info in classes_data:
                st.markdown(f"""
                <div style="padding: 16px; border: 1px solid var(--phoenix-border); border-radius: 8px; margin-bottom: 12px;">
                    <h4 style="margin-bottom: 8px; color: var(--phoenix-secondary);">{class_info['Class']}</h4>
                    <div style="display: flex; justify-content: space-between; color: var(--text-secondary); font-size: 0.9rem;">
                        <span>👥 {class_info['Students']} students</span>
                        <span>📊 {class_info['Progress']} complete</span>
                        <span style="color: #28a745;">✅ {class_info['Status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Resource Management")

            uploaded_file = st.file_uploader("Upload New Resource", type=['pdf', 'pptx', 'docx', 'txt'])
            if uploaded_file:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                st.info("In the full platform, this would be processed and made available to students.")

            st.markdown("### Current Resources")
            resources_data = [
                {"Name": "Machine Learning Slides.pptx", "Type": "Presentation", "Size": "2.4 MB", "Uploaded": "2024-09-25"},
                {"Name": "Python Basics.pdf", "Type": "Document", "Size": "1.8 MB", "Uploaded": "2024-09-24"},
                {"Name": "Data Analysis Guide.docx", "Type": "Document", "Size": "950 KB", "Uploaded": "2024-09-23"}
            ]

            for resource in resources_data:
                st.markdown(f"""
                <div style="padding: 12px; border-bottom: 1px solid var(--phoenix-border); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{resource['Name']}</strong><br>
                        <span style="color: var(--text-secondary); font-size: 0.9rem;">{resource['Type']} • {resource['Size']}</span>
                    </div>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">{resource['Uploaded']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            show_chat_interface(secrets, "admin")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def show_student_dashboard(secrets):
    """Display your original student dashboard design"""
    show_header("My Classes", "student")

    # Logout button
    if st.button("Logout", key="student_logout"):
        for key in ['authenticated', 'user_role', 'username']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown('<div class="dashboard-layout">', unsafe_allow_html=True)

    # Sidebar and main content
    col1, col2 = st.columns([280, 1000], gap="medium")

    with col1:
        st.markdown("""
        <div class="sidebar">
            <div class="welcome-message">
                <h4>Welcome back!</h4>
                <p>Student Dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### My Classes")
        st.markdown("📚 AI & Machine Learning")
        st.markdown("🐍 Python Programming")
        st.markdown("📊 Data Science")

    with col2:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["📚 My Courses", "🎯 Flashcards", "📊 Progress", "💬 Ask AI"])

        with tab1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### My Enrolled Courses")

            courses_data = [
                {"Course": "AI & Machine Learning", "Progress": 85, "Next": "Neural Networks", "Due": "Oct 2"},
                {"Course": "Python Programming", "Progress": 90, "Next": "Web Scraping", "Due": "Oct 5"},
                {"Course": "Data Science", "Progress": 72, "Next": "Statistical Analysis", "Due": "Oct 3"}
            ]

            for course in courses_data:
                with st.expander(f"📖 {course['Course']} - {course['Progress']}% Complete"):
                    prog_col1, prog_col2 = st.columns(2)
                    with prog_col1:
                        st.write(f"**Next Lesson:** {course['Next']}")
                        st.write(f"**Due Date:** {course['Due']}")
                    with prog_col2:
                        st.progress(course['Progress'] / 100)
                        if st.button(f"Continue Learning", key=course['Course']):
                            st.success(f"Opening {course['Course']} lesson...")

            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Interactive Flashcards")

            # Sample flashcards with your original styling
            flashcards = [
                {"Question": "What is machine learning?", "Answer": "A subset of AI that enables computers to learn and improve from experience without being explicitly programmed."},
                {"Question": "What is the difference between supervised and unsupervised learning?", "Answer": "Supervised learning uses labeled data, while unsupervised learning finds patterns in unlabeled data."},
                {"Question": "What is a neural network?", "Answer": "A computing system inspired by biological neural networks, consisting of interconnected nodes (neurons)."},
                {"Question": "What is overfitting in machine learning?", "Answer": "When a model learns the training data too well and fails to generalize to new, unseen data."}
            ]

            if 'current_card' not in st.session_state:
                st.session_state.current_card = 0
            if 'show_answer' not in st.session_state:
                st.session_state.show_answer = False

            card = flashcards[st.session_state.current_card]

            # Flashcard with your original gradient styling
            st.markdown(f"""
            <div style="background: var(--phoenix-gradient); padding: 2rem; border-radius: 12px; text-align: center; color: white; margin: 1rem 0; box-shadow: var(--phoenix-shadow);">
                <h3>Card {st.session_state.current_card + 1} of {len(flashcards)}</h3>
                <h2 style="margin-top: 16px;">{card['Question']}</h2>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if not st.session_state.show_answer:
                    if st.button("🔍 Show Answer", use_container_width=True):
                        st.session_state.show_answer = True
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; border: 1px solid var(--phoenix-border);">
                        <h4 style="color: var(--phoenix-secondary); margin-bottom: 12px;">Answer:</h4>
                        <p style="color: var(--text-primary); margin: 0;">{card['Answer']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("❌ Need Review", use_container_width=True):
                            st.session_state.show_answer = False
                            st.success("Card marked for review")
                    with col_b:
                        if st.button("✅ Got It!", use_container_width=True):
                            st.session_state.show_answer = False
                            st.session_state.current_card = (st.session_state.current_card + 1) % len(flashcards)
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Learning Progress")

            prog_col1, prog_col2 = st.columns(2)
            with prog_col1:
                st.markdown("""
                <div class="metric-card" style="margin-bottom: 16px;">
                    <div class="metric-value">12</div>
                    <div class="metric-label">Cards Studied Today</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="metric-card" style="margin-bottom: 16px;">
                    <div class="metric-value">7</div>
                    <div class="metric-label">Day Streak 🔥</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">2,450</div>
                    <div class="metric-label">Total Points</div>
                </div>
                """, unsafe_allow_html=True)

            with prog_col2:
                # Simple progress chart
                import pandas as pd
                progress_data = pd.DataFrame({
                    'Date': pd.date_range('2024-09-20', periods=8),
                    'Cards Studied': [5, 8, 12, 6, 15, 10, 14, 12]
                })
                st.line_chart(progress_data.set_index('Date'))

            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            show_chat_interface(secrets, "student")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def show_chat_interface(secrets, user_type):
    """AI chat interface"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💬 AI Education Assistant")

    if not secrets.get('OPENAI_API_KEY'):
        st.warning("⚠️ OpenAI API key not configured. Chat functionality is disabled.")
        st.info("To enable chat, add your OpenAI API key in the Streamlit secrets configuration.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Assistant:** {message['content']}")

    # Chat input
    user_input = st.text_input("Ask me anything about your studies...", key=f"chat_input_{user_type}")

    if st.button("Send", key=f"send_button_{user_type}") and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("AI is thinking..."):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=secrets.get('OPENAI_API_KEY'))

                system_message = f"You are an educational AI assistant helping a {user_type}. Provide helpful, encouraging, and educational responses. Keep responses concise but informative."

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_input}
                    ]
                )

                ai_response = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                st.rerun()

            except Exception as e:
                st.error("Error connecting to AI assistant. Please check your API key configuration.")

    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Load your custom CSS
    load_css()

    # Start FastAPI server (mock for Streamlit Cloud)
    server_thread, secrets = start_fastapi_server()

    if server_thread is None:
        st.error("Failed to start the application. Please check your configuration.")
        return

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None

    # Route to appropriate page
    if not st.session_state.authenticated:
        show_login_page(secrets)
    elif st.session_state.user_role == 'admin':
        show_admin_dashboard(secrets)
    elif st.session_state.user_role == 'student':
        show_student_dashboard(secrets)
    else:
        st.error("Invalid user role. Please login again.")
        if st.button("Return to Login"):
            for key in ['authenticated', 'user_role', 'username']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()