"""Main project detector that orchestrates all detection logic."""

import os
from pathlib import Path
from typing import Optional

from dprod_shared.models import ProjectConfig, ProjectType
from dprod_shared.exceptions import ProjectDetectionError

from .detectors import (
    NodeJSDetector,
    PythonDetector,
    GoDetector,
    StaticDetector,
    GenericDetector
)


class ProjectDetector:
    """Main project detector that determines project type and configuration."""
    
    def __init__(self):
        """Initialize the detector with all available detectors."""
        self.detectors = [
            NodeJSDetector(),
            PythonDetector(),
            GoDetector(),
            StaticDetector(),
        ]
        self.generic_detector = GenericDetector()
    
    def detect(self, project_path: Path) -> ProjectConfig:
        """
        Detect project type and return configuration.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectConfig: Detected project configuration
            
        Raises:
            ProjectDetectionError: If project type cannot be determined
        """
        if not project_path.exists():
            raise ProjectDetectionError(f"Project path does not exist: {project_path}")
        
        if not project_path.is_dir():
            raise ProjectDetectionError(f"Project path is not a directory: {project_path}")
        
        # Try each detector in order
        for detector in self.detectors:
            if detector.can_handle(project_path):
                try:
                    config = detector.get_config(project_path)
                    print(f"✅ Detected {config.type} project")
                    return config
                except Exception as e:
                    print(f"⚠️  Detector {detector.__class__.__name__} failed: {e}")
                    continue
        
        # Fallback to generic detector
        print("⚠️  No specific detector matched, using generic detector")
        return self.generic_detector.get_config(project_path)
    
    def get_supported_types(self) -> list[str]:
        """Get list of supported project types."""
        return [detector.project_type for detector in self.detectors]
