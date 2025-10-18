"""Generic fallback detector."""

from pathlib import Path

from .base import BaseDetector
from services.shared.core.models import ProjectType, ProjectConfig


class GenericDetector(BaseDetector):
    """Generic detector for unknown project types."""
    
    def __init__(self):
        super().__init__(ProjectType.UNKNOWN)
    
    def can_handle(self, project_path: Path) -> bool:
        """Always return True as this is the fallback detector."""
        return True
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Generate generic configuration."""
        return ProjectConfig(
            type=ProjectType.UNKNOWN,
            build_command="echo 'No build command specified'",
            start_command="echo 'No start command specified'",
            port=3000,
            environment={},
            install_path="/app"
        )