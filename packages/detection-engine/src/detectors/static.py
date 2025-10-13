"""Static site detector."""

from pathlib import Path
from typing import Optional

from dprod_shared.models import ProjectConfig, ProjectType
from .base import BaseDetector


class StaticDetector(BaseDetector):
    """Detector for static websites."""
    
    def __init__(self):
        super().__init__(ProjectType.STATIC)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a static website."""
        # Check for common static site files
        static_indicators = [
            "index.html",
            "index.htm",
            "index.php",  # PHP static sites
            "public/index.html",
            "dist/index.html",
            "build/index.html"
        ]
        
        for indicator in static_indicators:
            if self._find_file(project_path, indicator):
                return True
        
        return False
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Get static site configuration."""
        # Determine if we need a build step
        build_command = self._get_build_command(project_path)
        
        # Determine start command
        start_command = self._get_start_command(project_path)
        
        # Determine port
        port = self._get_port()
        
        # Get environment variables
        environment = self._get_environment()
        
        return ProjectConfig(
            type=ProjectType.STATIC,
            build_command=build_command,
            start_command=start_command,
            port=port,
            environment=environment
        )
    
    def _get_build_command(self, project_path: Path) -> Optional[str]:
        """Determine if a build step is needed."""
        # Check for package.json (React, Vue, Angular, etc.)
        if self._find_file(project_path, "package.json"):
            package_data = self._read_json_file(project_path / "package.json")
            scripts = package_data.get("scripts", {})
            
            # Check for build scripts
            if "build" in scripts:
                return "npm run build"
            elif "build:prod" in scripts:
                return "npm run build:prod"
        
        # Check for other build tools
        if self._find_file(project_path, "webpack.config.js"):
            return "npm run build"
        elif self._find_file(project_path, "vite.config.js"):
            return "npm run build"
        elif self._find_file(project_path, "next.config.js"):
            return "npm run build"
        
        # No build step needed
        return None
    
    def _get_start_command(self, project_path: Path) -> str:
        """Determine the start command."""
        # Check if there's a dist or build directory
        dist_dir = project_path / "dist"
        build_dir = project_path / "build"
        public_dir = project_path / "public"
        
        if dist_dir.exists():
            return "npx serve -s dist -l 80"
        elif build_dir.exists():
            return "npx serve -s build -l 80"
        elif public_dir.exists():
            return "npx serve -s public -l 80"
        else:
            return "npx serve -s . -l 80"
    
    def _get_port(self) -> int:
        """Get the port for static sites."""
        return 80
    
    def _get_environment(self) -> dict:
        """Get environment variables for static sites."""
        return {
            "NODE_ENV": "production"
        }
