"""Generic detector for unknown project types."""

from pathlib import Path

from dprod_shared.models import ProjectConfig, ProjectType
from .base import BaseDetector


class GenericDetector(BaseDetector):
    """Generic detector for unknown project types."""
    
    def __init__(self):
        super().__init__(ProjectType.UNKNOWN)
    
    def can_handle(self, project_path: Path) -> bool:
        """Generic detector can handle any project."""
        return True
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Get generic project configuration."""
        # Try to determine if it's a web application
        if self._is_web_app(project_path):
            return self._get_web_app_config(project_path)
        
        # Default to a simple file server
        return ProjectConfig(
            type=ProjectType.UNKNOWN,
            build_command=None,
            start_command="python -m http.server 8080",
            port=8080,
            environment={"PORT": "8080"}
        )
    
    def _is_web_app(self, project_path: Path) -> bool:
        """Check if this looks like a web application."""
        web_indicators = [
            "index.html",
            "index.php",
            "app.py",
            "main.py",
            "server.py",
            "app.js",
            "main.js",
            "server.js"
        ]
        
        for indicator in web_indicators:
            if self._find_file(project_path, indicator):
                return True
        
        return False
    
    def _get_web_app_config(self, project_path: Path) -> ProjectConfig:
        """Get configuration for a web application."""
        # Check for Python files
        python_files = list(project_path.glob("*.py"))
        if python_files:
            return ProjectConfig(
                type=ProjectType.UNKNOWN,
                build_command="pip install -r requirements.txt" if self._find_file(project_path, "requirements.txt") else None,
                start_command="python app.py" if self._find_file(project_path, "app.py") else "python main.py",
                port=8000,
                environment={"PYTHONUNBUFFERED": "1", "PORT": "8000"}
            )
        
        # Check for Node.js files
        js_files = list(project_path.glob("*.js"))
        if js_files:
            return ProjectConfig(
                type=ProjectType.UNKNOWN,
                build_command="npm install" if self._find_file(project_path, "package.json") else None,
                start_command="node app.js" if self._find_file(project_path, "app.js") else "node main.js",
                port=3000,
                environment={"NODE_ENV": "production", "PORT": "3000"}
            )
        
        # Check for Go files
        go_files = list(project_path.glob("*.go"))
        if go_files:
            return ProjectConfig(
                type=ProjectType.UNKNOWN,
                build_command="go mod download" if self._find_file(project_path, "go.mod") else None,
                start_command="go run main.go",
                port=8080,
                environment={"PORT": "8080"}
            )
        
        # Default web app configuration
        return ProjectConfig(
            type=ProjectType.UNKNOWN,
            build_command=None,
            start_command="python -m http.server 8080",
            port=8080,
            environment={"PORT": "8080"}
        )
