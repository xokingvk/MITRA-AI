import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "MITRA AI Gemini Assistant Backend"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Gemini Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Temporary Document Processing Path
    TEMPORARY_DOCUMENT_PATH: str = str(BASE_DIR / "data" / "temporary_documents")
    
    # CORS Configuration
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
