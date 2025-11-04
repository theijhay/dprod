"""Python project detector."""

import configparser
from pathlib import Path
from typing import Dict, Any

from .base import BaseDetector
from services.shared.core.models import ProjectType
from services.shared.core.schemas import ProjectConfig


class PythonDetector(BaseDetector):
    """Detector for Python projects."""
    
    def __init__(self):
        super().__init__(ProjectType.PYTHON)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a Python project."""
        # Check for common Python project files
        python_files = [
            "requirements.txt",
            "pyproject.toml", 
            "setup.py",
            "Pipfile",
            "poetry.lock"
        ]
        
        return any((project_path / file).exists() for file in python_files)
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Generate configuration for Python project."""
        # Default configuration
        config = ProjectConfig(
            type=ProjectType.PYTHON,
            build_command="pip install --no-cache-dir -r requirements.txt",
            start_command="python app.py",
            port=8000,
            environment={"PYTHONUNBUFFERED": "1"},
            install_path="/app"
        )
        
        # Try to detect the main application file
        main_files = ["app.py", "main.py", "server.py", "wsgi.py", "manage.py"]
        for main_file in main_files:
            if (project_path / main_file).exists():
                config.start_command = f"python {main_file}"
                break
        
        # Check for specific requirements file
        if (project_path / "requirements.txt").exists():
            config.build_command = "pip install --no-cache-dir -r requirements.txt"
        elif (project_path / "pyproject.toml").exists():
            config.build_command = "pip install --no-cache-dir ."
        
        # Try to read pyproject.toml for better configuration
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                config_parser = configparser.ConfigParser()
                config_parser.read(pyproject_path)
                
                if "tool.dprod" in config_parser:
                    dprod_section = config_parser["tool.dprod"]
                    
                    if "port" in dprod_section:
                        config.port = int(dprod_section["port"])
                    
                    if "start_command" in dprod_section:
                        config.start_command = dprod_section["start_command"]
                    
                    if "environment" in dprod_section:
                        # Parse environment variables (format: KEY1=value1,KEY2=value2)
                        env_vars = dprod_section["environment"].split(",")
                        for env_var in env_vars:
                            if "=" in env_var:
                                key, value = env_var.split("=", 1)
                                config.environment[key.strip()] = value.strip()
                
            except Exception as e:
                print(f"Warning: Could not parse pyproject.toml: {e}")
        
        return config