"""Configuration settings for Dprod API."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    port: int = 8000
    debug: bool = False
    host: str = "0.0.0.0"
    
    # Database Configuration
    database_url: str = "postgresql+asyncpg://dprod:dprod@localhost:5432/dprod"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # Docker Configuration
    docker_socket_path: str = "/var/run/docker.sock"
    
    # File Upload
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_path: str = "/tmp/dprod/uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
