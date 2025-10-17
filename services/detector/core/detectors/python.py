"""Python project detector."""

from pathlib import Path
from typing import Optional

from dprod_shared.models import ProjectConfig, ProjectType
from .base import BaseDetector


class PythonDetector(BaseDetector):
    """Detector for Python projects."""
    
    def __init__(self):
        super().__init__(ProjectType.PYTHON)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a Python project."""
        # Check for common Python project files
        python_indicators = [
            "requirements.txt",
            "pyproject.toml", 
            "setup.py",
            "Pipfile",
            "main.py",
            "app.py",
            "manage.py"  # Django
        ]
        
        for indicator in python_indicators:
            if self._find_file(project_path, indicator):
                return True
        
        return False
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Get Python project configuration."""
        # Determine build command
        build_command = self._get_build_command(project_path)
        
        # Determine start command
        start_command = self._get_start_command(project_path)
        
        # Determine port
        port = self._get_port(project_path)
        
        # Get environment variables
        environment = self._get_environment()
        
        return ProjectConfig(
            type=ProjectType.PYTHON,
            build_command=build_command,
            start_command=start_command,
            port=port,
            environment=environment
        )
    
    def _get_build_command(self, project_path: Path) -> str:
        """Determine the build command."""
        if self._find_file(project_path, "requirements.txt"):
            return "pip install -r requirements.txt"
        elif self._find_file(project_path, "pyproject.toml"):
            return "pip install -e ."
        elif self._find_file(project_path, "Pipfile"):
            return "pipenv install"
        else:
            return "pip install -r requirements.txt"  # Default
    
    def _get_start_command(self, project_path: Path) -> str:
        """Determine the start command."""
        # Check for common Python entry points
        entry_points = [
            "main.py",
            "app.py", 
            "manage.py",  # Django
            "run.py",
            "server.py"
        ]
        
        for entry_point in entry_points:
            if self._find_file(project_path, entry_point):
                return f"python {entry_point}"
        
        # Check for uvicorn/fastapi in requirements
        requirements_file = self._find_file(project_path, "requirements.txt")
        if requirements_file:
            requirements = self._read_text_file(requirements_file)
            if "uvicorn" in requirements.lower():
                return "uvicorn main:app --host 0.0.0.0 --port 8000"
            elif "flask" in requirements.lower():
                return "python app.py"
            elif "django" in requirements.lower():
                return "python manage.py runserver 0.0.0.0:8000"
        
        # Default fallback
        return "python app.py"
    
    def _get_port(self, project_path: Path) -> int:
        """Determine the port."""
        # Check for port in common files
        for filename in ["main.py", "app.py", "server.py"]:
            file_path = self._find_file(project_path, filename)
            if file_path:
                content = self._read_text_file(file_path)
                # Look for port assignments
                for line in content.split('\n'):
                    if 'port' in line.lower() and '=' in line:
                        try:
                            # Extract port number
                            parts = line.split('=')
                            if len(parts) > 1:
                                port_str = parts[1].strip().rstrip(',')
                                return int(port_str)
                        except ValueError:
                            continue
        
        # Default port for Python
        return 8000
    
    def _get_environment(self) -> dict:
        """Get environment variables for Python projects."""
        return {
            "PYTHONUNBUFFERED": "1",
            "PORT": "8000"
        }
