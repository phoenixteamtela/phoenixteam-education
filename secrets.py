import os
from typing import Dict, Any
import streamlit as st

def get_secrets() -> Dict[str, Any]:
    """
    Get secrets for deployment. Supports both Streamlit secrets and environment variables.
    """
    secrets = {}

    # Try Streamlit secrets first (for deployment)
    if hasattr(st, 'secrets') and st.secrets:
        try:
            secrets.update({
                'OPENAI_API_KEY': st.secrets.get('OPENAI_API_KEY', ''),
                'SECRET_KEY': st.secrets.get('SECRET_KEY', ''),
                'APP_PASSWORD': st.secrets.get('APP_PASSWORD', 'phoenixteam2024'),
                'DATABASE_URL': st.secrets.get('DATABASE_URL', 'sqlite:///./phoenixteam_edu.db'),
            })
        except Exception:
            pass

    # Fall back to environment variables (for local development)
    secrets.update({
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', secrets.get('OPENAI_API_KEY', '')),
        'SECRET_KEY': os.getenv('SECRET_KEY', secrets.get('SECRET_KEY', 'your-secret-key-change-this')),
        'APP_PASSWORD': os.getenv('APP_PASSWORD', secrets.get('APP_PASSWORD', 'phoenixteam2024')),
        'DATABASE_URL': os.getenv('DATABASE_URL', secrets.get('DATABASE_URL', 'sqlite:///./phoenixteam_edu.db')),
    })

    return secrets

def validate_secrets(secrets: Dict[str, Any]) -> bool:
    """
    Validate that all required secrets are present.
    """
    required_secrets = ['SECRET_KEY', 'APP_PASSWORD']
    missing_secrets = [key for key in required_secrets if not secrets.get(key)]

    if missing_secrets:
        st.error(f"Missing required secrets: {', '.join(missing_secrets)}")
        return False

    if not secrets.get('OPENAI_API_KEY'):
        st.warning("OpenAI API key not set. Chat functionality will be disabled.")

    return True