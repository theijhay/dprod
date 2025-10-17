"""Base detector class for all project type detectors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from dprod_shared.models import ProjectConfig, ProjectType


class BaseDetector(ABC):
    """Base class for all project type detectors."""
    
    def __init__(self, project_type: ProjectType):
        """Initialize the detector with project type."""
        self.project_type = project_type
    
    @abstractmethod
    def can_handle(self, project_path: Path) -> bool:
        """
        Check if this detector can handle the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            bool: True if this detector can handle the project
        """
        pass
    
    @abstractmethod
    def get_config(self, project_path: Path) -> ProjectConfig:
        """
        Get project configuration for the detected project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectConfig: Project configuration
        """
        pass
    
    def _find_file(self, project_path: Path, filename: str) -> Optional[Path]:
        """Find a file in the project directory."""
        file_path = project_path / filename
        return file_path if file_path.exists() else None
    
    def _read_json_file(self, file_path: Path) -> dict:
        """Read and parse a JSON file."""
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to parse JSON file {file_path}: {e}")
    
    def _read_text_file(self, file_path: Path) -> str:
        """Read a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
