#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import time
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

# Simple CSS that works on Streamlit Cloud
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}

.main .block-container {
    padding: 1rem;
    max-width: 100%;
}

.phoenix-login {
    background: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
    padding: 3rem;
    border-radius: 15px;
    text-align: center;
    color: white;
    margin: 2rem auto;
    max-width: 500px;
}

.phoenix-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
}

.phoenix-header {
    background: #f8f9fa;
    padding: 1rem;
    border-bottom: 2px solid #FF6B35;
    margin: -1rem -1rem 1rem -1rem;
    border-radius: 12px 12px 0 0;
}

.phoenix-metric {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #e0e0e0;
    margin: 0.5rem 0;
}

.phoenix-metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #FF6B35;
}

.phoenix-flashcard {
    background: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    color: white;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

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
    return True, secrets

def show_login_page(secrets):
    """Display the login page"""
    st.markdown("""
    <div class="phoenix-login">
        <h1>🔥 PhoenixTeam Education Platform</h1>
        <h3>AI-Powered Learning Management System</h3>
    </div>
    """, unsafe_allow_html=True)

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
        st.markdown("### Welcome Back")
        st.markdown("Sign in to access your educational dashboard")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)

            if submitted:
                if username and password:
                    app_password = secrets.get('APP_PASSWORD', 'phoenixteam2024')

                    if username == 'admin' and password == app_password:
                        st.session_state.authenticated = True
                        st.session_state.user_role = 'admin'
                        st.session_state.username = username
                        st.rerun()
                    elif password == app_password:
                        st.session_state.authenticated = True
                        st.session_state.user_role = 'student'
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.error("Please enter both username and password.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Demo credentials
        st.info("""
        **Demo Credentials:**

        **Admin Access:** Username: `admin`, Password: `phoenixteam2024`

        **Student Access:** Username: any name, Password: `phoenixteam2024`
        """)

def show_header(title):
    """Display header"""
    logo_b64 = get_logo_base64()

    st.markdown(f"""
    <div class="phoenix-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <h2 style="margin: 0; color: #1E2A4A;">🔥 PhoenixTeam › Education Center › {title}</h2>
            </div>
            <div>
                <span style="color: #666;">Welcome, {st.session_state.username}!</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_admin_dashboard(secrets):
    """Display admin dashboard"""
    show_header("Admin Dashboard")

    # Logout button
    if st.button("🚪 Logout", key="admin_logout"):
        for key in ['authenticated', 'user_role', 'username']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Sidebar and main content
    col_sidebar, col_main = st.columns([1, 3])

    with col_sidebar:
        st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
        st.markdown("### Quick Actions")

        if st.button("➕ Create New Class", use_container_width=True):
            st.success("Class creation feature")
        if st.button("📚 Upload Resource", use_container_width=True):
            st.success("Resource upload feature")
        if st.button("👥 Manage Users", use_container_width=True):
            st.success("User management feature")
        if st.button("🎯 Manage Flashcards", use_container_width=True):
            st.success("Flashcard management feature")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        # Dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Classes", "📚 Resources", "💬 Chat Assistant"])

        with tab1:
            st.markdown("### Platform Overview")

            # Metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">25</div>
                    <div>Total Students</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_col2:
                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">4</div>
                    <div>Active Classes</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_col3:
                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">48</div>
                    <div>Resources</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_col4:
                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">156</div>
                    <div>Chat Sessions</div>
                </div>
                """, unsafe_allow_html=True)

            # Recent Activity
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            st.markdown("### Recent Activity")

            activity_data = [
                {"Time": "10:30 AM", "User": "Sarah Johnson", "Action": "Completed flashcard set: Machine Learning Basics"},
                {"Time": "10:15 AM", "User": "Mike Chen", "Action": "Started quiz: Python Fundamentals"},
                {"Time": "9:45 AM", "User": "Admin", "Action": "Uploaded new resource: Data Science Guide"},
                {"Time": "9:30 AM", "User": "Emma Davis", "Action": "Asked question in chat about neural networks"}
            ]

            for activity in activity_data:
                st.markdown(f"""
                **{activity['User']}** - {activity['Time']}
                {activity['Action']}
                ---
                """)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            st.markdown("### Class Management")

            classes_data = [
                {"Class": "AI & Machine Learning", "Students": 8, "Progress": "85%", "Status": "Active"},
                {"Class": "Data Science Fundamentals", "Students": 12, "Progress": "72%", "Status": "Active"},
                {"Class": "Python Programming", "Students": 15, "Progress": "90%", "Status": "Active"},
                {"Class": "Statistics & Analytics", "Students": 6, "Progress": "45%", "Status": "Active"}
            ]

            for class_info in classes_data:
                st.markdown(f"""
                **{class_info['Class']}**
                👥 {class_info['Students']} students | 📊 {class_info['Progress']} complete | ✅ {class_info['Status']}
                """)
                st.markdown("---")

            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
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
                **{resource['Name']}**
                {resource['Type']} • {resource['Size']} • Uploaded: {resource['Uploaded']}
                """)
                st.markdown("---")

            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            show_chat_interface(secrets, "admin")

def show_student_dashboard(secrets):
    """Display student dashboard"""
    show_header("My Classes")

    # Logout button
    if st.button("🚪 Logout", key="student_logout"):
        for key in ['authenticated', 'user_role', 'username']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Sidebar and main content
    col_sidebar, col_main = st.columns([1, 3])

    with col_sidebar:
        st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
        st.markdown("### My Classes")
        st.markdown("📚 AI & Machine Learning")
        st.markdown("🐍 Python Programming")
        st.markdown("📊 Data Science")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        tab1, tab2, tab3, tab4 = st.tabs(["📚 My Courses", "🎯 Flashcards", "📊 Progress", "💬 Ask AI"])

        with tab1:
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
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
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            st.markdown("### Interactive Flashcards")

            # Sample flashcards
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

            # Flashcard with gradient styling
            st.markdown(f"""
            <div class="phoenix-flashcard">
                <h3>Card {st.session_state.current_card + 1} of {len(flashcards)}</h3>
                <h2>{card['Question']}</h2>
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
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #ddd;">
                        <h4 style="color: #1E2A4A; margin-bottom: 12px;">Answer:</h4>
                        <p style="color: #333; margin: 0;">{card['Answer']}</p>
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
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            st.markdown("### Learning Progress")

            prog_col1, prog_col2 = st.columns(2)
            with prog_col1:
                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">12</div>
                    <div>Cards Studied Today</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">7</div>
                    <div>Day Streak 🔥</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="phoenix-metric">
                    <div class="phoenix-metric-value">2,450</div>
                    <div>Total Points</div>
                </div>
                """, unsafe_allow_html=True)

            with prog_col2:
                # Progress chart
                progress_data = pd.DataFrame({
                    'Date': pd.date_range('2024-09-20', periods=8),
                    'Cards Studied': [5, 8, 12, 6, 15, 10, 14, 12]
                })
                st.line_chart(progress_data.set_index('Date'))

            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            show_chat_interface(secrets, "student")

def show_chat_interface(secrets, user_type):
    """AI chat interface"""
    st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
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