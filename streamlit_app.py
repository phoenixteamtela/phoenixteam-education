#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import time
import os
import hashlib
from pathlib import Path
from app_secrets import get_secrets, validate_secrets

# Configure Streamlit page
st.set_page_config(
    page_title="PhoenixTeam Education Platform",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the original design
st.markdown("""
<style>
.main-header {
    text-align: center;
    background: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
}

.login-form {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.dashboard-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.btn-primary {
    background: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

def authenticate_user(username: str, password: str, secrets: dict) -> tuple:
    """Authenticate user and return (success, role)"""
    # Simple authentication - in production this would use a database
    app_password = secrets.get('APP_PASSWORD', 'phoenixteam2024')

    # Admin authentication
    if username == 'admin' and password == app_password:
        return True, 'admin'

    # Student authentication (for demo, accept any username with the app password)
    elif password == app_password:
        return True, 'student'

    return False, None

def show_login_page(secrets: dict):
    """Display the login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🔥 PhoenixTeam Education Platform</h1>
        <p>AI-Powered Learning Management System</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.markdown("### Welcome Back")
        st.markdown("Sign in to access your educational dashboard")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Sign In", use_container_width=True)

            if submit_button:
                if username and password:
                    success, role = authenticate_user(username, password, secrets)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_role = role
                        st.session_state.username = username
                        st.session_state.current_page = f'{role}_dashboard'
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.error("Please enter both username and password.")

        st.markdown("</div>", unsafe_allow_html=True)

        # Demo credentials info
        st.info("""
        **Demo Credentials:**

        **Admin Access:**
        - Username: `admin`
        - Password: `phoenixteam2024`

        **Student Access:**
        - Username: Any name (e.g., `student`)
        - Password: `phoenixteam2024`
        """)

def show_admin_dashboard(secrets: dict):
    """Display the admin dashboard"""
    st.markdown(f"### 👨‍💼 Admin Dashboard - Welcome {st.session_state.username}!")

    if st.button("Logout", key="admin_logout"):
        for key in ['authenticated', 'user_role', 'username', 'current_page']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Classes", "📚 Resources", "💬 Chat Assistant"])

    with tab1:
        st.subheader("Platform Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", "25", "↗️ 3")
        with col2:
            st.metric("Active Classes", "4", "↗️ 1")
        with col3:
            st.metric("Resources", "48", "↗️ 12")
        with col4:
            st.metric("Chat Sessions", "156", "↗️ 23")

        st.markdown("### Recent Activity")
        activity_data = [
            {"Time": "10:30 AM", "User": "Sarah Johnson", "Action": "Completed flashcard set: Machine Learning Basics"},
            {"Time": "10:15 AM", "User": "Mike Chen", "Action": "Started quiz: Python Fundamentals"},
            {"Time": "9:45 AM", "User": "Admin", "Action": "Uploaded new resource: Data Science Guide"},
            {"Time": "9:30 AM", "User": "Emma Davis", "Action": "Asked question in chat about neural networks"}
        ]
        st.dataframe(pd.DataFrame(activity_data), use_container_width=True)

    with tab2:
        st.subheader("Class Management")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Current Classes")
            classes_data = [
                {"Class": "AI & Machine Learning", "Students": 8, "Progress": "85%", "Status": "Active"},
                {"Class": "Data Science Fundamentals", "Students": 12, "Progress": "72%", "Status": "Active"},
                {"Class": "Python Programming", "Students": 15, "Progress": "90%", "Status": "Active"},
                {"Class": "Statistics & Analytics", "Students": 6, "Progress": "45%", "Status": "Active"}
            ]
            st.dataframe(pd.DataFrame(classes_data), use_container_width=True)

        with col2:
            st.markdown("### Quick Actions")
            if st.button("➕ Create New Class", use_container_width=True):
                st.success("Class creation form would open here")
            if st.button("📋 Manage Students", use_container_width=True):
                st.success("Student management panel would open here")
            if st.button("📊 View Analytics", use_container_width=True):
                st.success("Analytics dashboard would open here")

    with tab3:
        st.subheader("Resource Management")

        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader("Upload New Resource",
                                           type=['pdf', 'pptx', 'docx', 'txt'],
                                           help="Upload educational materials for students")
            if uploaded_file:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                st.info("In the full platform, this would be processed and made available to students.")

        with col2:
            st.markdown("### Resource Stats")
            st.metric("PDFs", "23")
            st.metric("Presentations", "15")
            st.metric("Documents", "10")

        # Sample resources
        st.markdown("### Current Resources")
        resources_data = [
            {"Name": "Machine Learning Slides.pptx", "Type": "Presentation", "Size": "2.4 MB", "Uploaded": "2024-09-25"},
            {"Name": "Python Basics.pdf", "Type": "Document", "Size": "1.8 MB", "Uploaded": "2024-09-24"},
            {"Name": "Data Analysis Guide.docx", "Type": "Document", "Size": "950 KB", "Uploaded": "2024-09-23"}
        ]
        st.dataframe(pd.DataFrame(resources_data), use_container_width=True)

    with tab4:
        show_chat_interface(secrets, "admin")

def show_student_dashboard(secrets: dict):
    """Display the student dashboard"""
    st.markdown(f"### 🎓 Student Dashboard - Welcome {st.session_state.username}!")

    if st.button("Logout", key="student_logout"):
        for key in ['authenticated', 'user_role', 'username', 'current_page']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📚 My Courses", "🎯 Flashcards", "📊 Progress", "💬 Ask AI"])

    with tab1:
        st.subheader("My Enrolled Courses")

        courses_data = [
            {"Course": "AI & Machine Learning", "Progress": "85%", "Next Lesson": "Neural Networks", "Due": "Oct 2"},
            {"Course": "Python Programming", "Progress": "90%", "Next Lesson": "Web Scraping", "Due": "Oct 5"},
            {"Course": "Data Science", "Progress": "72%", "Next Lesson": "Statistical Analysis", "Due": "Oct 3"}
        ]

        for course in courses_data:
            with st.expander(f"📖 {course['Course']} - {course['Progress']} Complete"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Next Lesson:** {course['Next Lesson']}")
                    st.write(f"**Due Date:** {course['Due']}")
                with col2:
                    st.progress(int(course['Progress'].replace('%', '')) / 100)
                    if st.button(f"Continue Learning", key=course['Course']):
                        st.success(f"Opening {course['Course']} lesson...")

    with tab2:
        st.subheader("Interactive Flashcards")

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

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #FFD23F 100%);
                    padding: 2rem; border-radius: 10px; text-align: center; color: white; margin: 1rem 0;">
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
                <div style="background: #f0f0f0; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                    <h4>Answer:</h4>
                    <p>{card['Answer']}</p>
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

    with tab3:
        st.subheader("Learning Progress")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cards Studied Today", "12", "↗️ 3")
            st.metric("Streak", "7 days", "🔥")
            st.metric("Total Points", "2,450", "↗️ 150")

        with col2:
            # Sample progress chart
            progress_data = pd.DataFrame({
                'Date': pd.date_range('2024-09-20', periods=8),
                'Cards Studied': [5, 8, 12, 6, 15, 10, 14, 12]
            })
            st.line_chart(progress_data.set_index('Date'))

    with tab4:
        show_chat_interface(secrets, "student")

def show_chat_interface(secrets: dict, user_type: str):
    """Display the chat interface"""
    st.subheader("💬 AI Education Assistant")

    if not secrets.get('OPENAI_API_KEY'):
        st.warning("⚠️ OpenAI API key not configured. Chat functionality is disabled.")
        st.info("To enable chat, add your OpenAI API key in the Streamlit secrets configuration.")
        return

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**AI Assistant:** {message['content']}")

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

def main():
    # Get secrets for Streamlit Cloud deployment
    secrets = get_secrets()
    validate_secrets(secrets)

    # Initialize session state
    initialize_session_state()

    # Route to appropriate page based on authentication state
    if not st.session_state.authenticated:
        show_login_page(secrets)
    elif st.session_state.user_role == 'admin':
        show_admin_dashboard(secrets)
    elif st.session_state.user_role == 'student':
        show_student_dashboard(secrets)
    else:
        st.error("Invalid user role. Please login again.")
        if st.button("Return to Login"):
            for key in ['authenticated', 'user_role', 'username', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()