"""Configuration management for AI DevOps Agent Platform."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Backend Configuration
    backend_host: str = Field("localhost", env="BACKEND_HOST")
    backend_port: int = Field(8000, env="BACKEND_PORT")
    debug: bool = Field(False, env="DEBUG")
    
    # Frontend Configuration
    streamlit_port: int = Field(8501, env="STREAMLIT_PORT")
    
    # Database
    database_url: str = Field("sqlite:///./data/ai_devops.db", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # File Upload
    max_upload_size: int = Field(10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    upload_folder: str = Field("./uploads", env="UPLOAD_FOLDER")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("./logs/app.log", env="LOG_FILE")
    
    # Carbon Tracking
    enable_carbon_tracking: bool = Field(True, env="ENABLE_CARBON_TRACKING")
    
    # Model Configuration
    default_vision_model: str = Field("gpt-4-vision-preview", env="DEFAULT_VISION_MODEL")
    default_code_model: str = Field("gpt-4-turbo-preview", env="DEFAULT_CODE_MODEL")
    default_layout_model: str = Field("claude-3-sonnet-20240229", env="DEFAULT_LAYOUT_MODEL")
    
    # Generated Code Output
    output_folder: str = Field("./output", env="OUTPUT_FOLDER")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def ensure_directories():
    """Ensure required directories exist."""
    dirs = [
        settings.upload_folder,
        settings.output_folder,
        os.path.dirname(settings.log_file),
        "data"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)