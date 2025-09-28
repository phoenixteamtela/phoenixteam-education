import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = "PhoenixTeam Education Platform"
    app_password: str = os.getenv("APP_PASSWORD", "phoenixteam2024")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./phoenixteam_edu.db")

    uploads_path: str = "../uploads"
    slides_path: str = f"{uploads_path}/slides"
    resources_path: str = f"{uploads_path}/resources"

    @classmethod
    def from_secrets(cls, secrets_dict: dict):
        """Create settings from secrets dictionary for Streamlit deployment"""
        instance = cls()
        instance.app_password = secrets_dict.get("APP_PASSWORD", instance.app_password)
        instance.secret_key = secrets_dict.get("SECRET_KEY", instance.secret_key)
        instance.openai_api_key = secrets_dict.get("OPENAI_API_KEY", instance.openai_api_key)
        instance.database_url = secrets_dict.get("DATABASE_URL", instance.database_url)
        return instance

settings = Settings()