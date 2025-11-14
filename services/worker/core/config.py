"""Configuration for worker service."""
import os
from typing import Optional


class WorkerConfig:
    """Worker configuration."""
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    SQS_QUEUE_URL: str = os.getenv("SQS_QUEUE_URL", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Worker Configuration
    WORKER_ID: str = os.getenv("WORKER_ID", os.getenv("HOSTNAME", "worker-1"))
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
    POLL_INTERVAL: int = int(os.getenv("POLL_INTERVAL", "5"))  # seconds
    MESSAGE_VISIBILITY_TIMEOUT: int = int(os.getenv("MESSAGE_VISIBILITY_TIMEOUT", "900"))  # 15 minutes
    
    # Docker Configuration
    DOCKER_SOCKET: str = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
    CONTAINER_NETWORK: str = os.getenv("CONTAINER_NETWORK", "dprod-network")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.SQS_QUEUE_URL:
            raise ValueError("SQS_QUEUE_URL environment variable is required")
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")


config = WorkerConfig()
