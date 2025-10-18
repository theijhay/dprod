"""Main project detector that identifies project types and generates configurations."""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from services.shared.core.models import ProjectType, ProjectConfig
from .detectors import (
    NodeJSDetector,
    PythonDetector,
    GoDetector,
    StaticDetector,
    GenericDetector
)


class ProjectDetector:
    """Main project detector that orchestrates all detection logic."""
    
    def __init__(self):
        """Initialize the detector with all available detectors."""
        self.detectors = [
            NodeJSDetector(),
            PythonDetector(),
            GoDetector(),
            StaticDetector(),
            GenericDetector()
        ]
    
    def detect_project(self, project_path: Path) -> Optional[ProjectConfig]:
        """
        Detect project type and generate configuration.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectConfig if detection successful, None otherwise
        """
        if not project_path.exists() or not project_path.is_dir():
            return None
        
        print(f"🔍 Analyzing project at: {project_path}")
        
        for detector in self.detectors:
            if detector.can_handle(project_path):
                print(f"✅ Detected {detector.project_type.value} project")
                config = detector.get_config(project_path)
                print(f"📋 Generated config: {config}")
                return config
        
        print("❌ Could not detect project type")
        return None
    
    def get_dockerfile(self, project_path: Path) -> Optional[str]:
        """
        Generate Dockerfile for the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dockerfile content as string, None if not supported
        """
        config = self.detect_project(project_path)
        if not config:
            return None
        
        for detector in self.detectors:
            if detector.project_type == config.type:
                return detector.generate_dockerfile(config)
        
        return None