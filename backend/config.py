"""
Configuration and environment variables for Easy-Trade backend
"""

from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App Settings
    app_name: str = "Easy-Trade"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./easy_trade.db")
    database_echo: bool = debug
    
    # Project Storage
    projects_dir: Path = Path(os.getenv("PROJECTS_DIR", "./projects"))
    max_project_size_mb: int = 100
    
    # Security Settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Upload Settings
    max_upload_size_mb: int = 50
    allowed_image_formats: list = ["jpg", "jpeg", "png", "gif", "webp"]
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Ensure projects directory exists
settings.projects_dir.mkdir(parents=True, exist_ok=True)
