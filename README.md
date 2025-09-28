# PhoenixTeam Education Platform

A modern, secure education platform built with FastAPI backend and vanilla JavaScript frontend, designed for deployment via Streamlit.

## 🚀 Features

- **Class Management**: Create and manage educational classes
- **Slide Viewing**: Upload and display presentation slides (view-only, no downloads)
- **Resource Sharing**: Upload and share educational resources
- **AI Chat Assistant**: OpenAI-powered educational assistant
- **User Management**: Admin and student role management
- **Secure Authentication**: JWT token-based authentication
- **Modern UI**: Clean, responsive design with Sofia Pro typography
- **PhoenixTeam Branding**: Integrated PhoenixTeam logos and color scheme

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript with modern CSS
- **Database**: SQLite (default) with PostgreSQL support
- **Authentication**: JWT tokens with bcrypt password hashing
- **Deployment**: Streamlit for secure, easy deployment
- **File Storage**: Local file system with organized structure

## 📋 Prerequisites

- Python 3.8+
- Node.js (for development)
- OpenAI API key (optional, for chat features)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phoenixteam-education
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up Streamlit secrets for deployment**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml with your actual secrets
   ```

## 🚀 Deployment

### Local Development

1. **Start the backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Serve the frontend**
   ```bash
   # Simple HTTP server
   python -m http.server 3000 --directory frontend
   ```

3. **Access the application**
   - Frontend: http://localhost:3000/src/pages/login.html
   - API Documentation: http://localhost:8000/docs

### Streamlit Deployment

1. **Configure secrets**
   Edit `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   SECRET_KEY = "your_long_random_secret_key"
   APP_PASSWORD = "your_admin_password"
   ```

2. **Deploy with Streamlit**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access via Streamlit Cloud**
   - Deploy to Streamlit Cloud for public access
   - Configure secrets in Streamlit Cloud dashboard

## 🔐 Security

- **Environment Variables**: Sensitive data stored in environment variables
- **Password Hashing**: bcrypt for secure password storage
- **JWT Tokens**: Secure authentication with configurable expiration
- **File Upload Validation**: Strict file type checking
- **CORS Protection**: Configurable CORS policies
- **Input Validation**: Pydantic schemas for request validation

## 👥 User Management

### Creating the First Admin

Use the API to create your first admin user:

```bash
curl -X POST "http://localhost:8000/api/auth/register-admin" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "email": "admin@phoenixteam.com",
       "password": "your_secure_password"
     }'
```

### User Roles

- **Admin**: Can create classes, upload slides/resources, manage users
- **Student**: Can view enrolled classes, access slides/resources, use chat

## 📁 Project Structure

```
phoenixteam-education/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # Database models
│   │   └── schemas/        # Pydantic schemas
├── frontend/               # Frontend application
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Application pages
│   │   ├── services/       # API services
│   │   ├── styles/         # CSS stylesheets
│   │   └── assets/         # Static assets
├── uploads/                # File storage
│   ├── slides/            # Presentation slides
│   └── resources/         # Educational resources
├── assets/                 # Design assets
│   ├── fonts/             # Sofia Pro fonts
│   └── *.png              # PhoenixTeam logos
├── streamlit_app.py       # Streamlit deployment entry point
├── secrets.py             # Secrets management
└── requirements.txt       # Python dependencies
```

## 🎨 Styling

The application uses:
- **Sofia Pro** font family (included in assets)
- **PhoenixTeam colors**: Orange (#FF6B35), Yellow (#FFD23F), Blue (#004E89)
- **Modern CSS**: Flexbox/Grid layouts, gradients, shadows
- **Responsive design**: Mobile-friendly layouts

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/register-admin` - Register admin user
- `POST /api/auth/token` - Login and get token
- `GET /api/auth/me` - Get current user info

### Classes
- `POST /api/classes/` - Create class (admin)
- `GET /api/classes/` - List classes
- `GET /api/classes/{id}` - Get class details
- `POST /api/classes/{id}/enroll/{user_id}` - Enroll user

### Slides
- `POST /api/slides/upload/{class_id}` - Upload slide
- `GET /api/slides/class/{class_id}` - List class slides
- `GET /api/slides/{id}` - View slide (no download)

### Resources
- `POST /api/resources/upload` - Upload resource
- `GET /api/resources/global` - List global resources
- `GET /api/resources/class/{class_id}` - List class resources

### Chat
- `POST /api/chat/` - Send message to AI
- `GET /api/chat/history` - Get chat history

## 🧪 Testing

Run the backend tests:
```bash
cd backend
pytest
```

## 📝 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for chat features | "" |
| `SECRET_KEY` | JWT signing secret | "change-this" |
| `APP_PASSWORD` | Admin password | "phoenixteam2024" |
| `DATABASE_URL` | Database connection string | SQLite |

### File Upload Limits

- **Slides**: PDF, PPT, PPTX, JPG, PNG, GIF
- **Resources**: Documents, images, videos, audio files
- **Max file size**: Configurable per file type

## 🚨 Troubleshooting

### Common Issues

1. **Database not created**: Ensure FastAPI has write permissions
2. **File uploads failing**: Check uploads directory permissions
3. **CORS errors**: Configure CORS origins in settings
4. **OpenAI chat not working**: Verify API key configuration

### Logs

- Backend logs: Check uvicorn output
- Frontend errors: Check browser console
- File operations: Check filesystem permissions

## 📄 License

This project is proprietary to PhoenixTeam.

## 🤝 Support

For support, contact the PhoenixTeam development team.