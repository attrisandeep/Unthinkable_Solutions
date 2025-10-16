"""
KnowledgeExplorer Backend Configuration
Central configuration loader using python-dotenv and Pydantic BaseSettings
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Central configuration class for KnowledgeExplorer backend.
    All settings are loaded from environment variables or .env file.
    """
    
    # Groq API Configuration
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    groq_model: str = Field(default="mixtral-8x7b-32768", env="GROQ_MODEL")
    groq_temperature: float = Field(default=0.7, env="GROQ_TEMPERATURE")
    groq_max_tokens: int = Field(default=2048, env="GROQ_MAX_TOKENS")
    
    # Pinecone Configuration
    pinecone_api_key: str = Field(default="", env="PINECONE_API_KEY")
    pinecone_env: str = Field(default="us-west1-gcp", env="PINECONE_ENV")
    pinecone_index: str = Field(default="knowledge-explorer", env="PINECONE_INDEX")
    
    # Jina AI Configuration
    jina_api_key: str = Field(default="", env="JINA_API_KEY")
    
    # Document Processing Configuration
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    min_relevance_score: float = Field(default=0.7, env="MIN_RELEVANCE_SCORE")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Upload Configuration
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def validate_api_keys(self) -> dict:
        """
        Validate that required API keys are present.
        Returns a dict of validation status for each service.
        """
        validation = {
            "groq": bool(self.groq_api_key and self.groq_api_key != ""),
            "pinecone": bool(self.pinecone_api_key and self.pinecone_api_key != ""),
            "jina": bool(self.jina_api_key and self.jina_api_key != "")
        }
        return validation
    
    def ensure_upload_dir(self):
        """Create upload directory if it doesn't exist."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure upload directory exists on import
settings.ensure_upload_dir()
