"""Go project detector."""

from pathlib import Path
from typing import Optional

from dprod_shared.models import ProjectConfig, ProjectType
from .base import BaseDetector


class GoDetector(BaseDetector):
    """Detector for Go projects."""
    
    def __init__(self):
        super().__init__(ProjectType.GO)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a Go project."""
        go_mod = self._find_file(project_path, "go.mod")
        go_sum = self._find_file(project_path, "go.sum")
        return go_mod is not None or go_sum is not None
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Get Go project configuration."""
        # Determine start command
        start_command = self._get_start_command(project_path)
        
        # Determine port
        port = self._get_port(project_path)
        
        # Get environment variables
        environment = self._get_environment()
        
        return ProjectConfig(
            type=ProjectType.GO,
            build_command="go mod download",
            start_command=start_command,
            port=port,
            environment=environment
        )
    
    def _get_start_command(self, project_path: Path) -> str:
        """Determine the start command."""
        # Check for main.go
        if self._find_file(project_path, "main.go"):
            return "go run main.go"
        
        # Check for cmd directory
        cmd_dir = project_path / "cmd"
        if cmd_dir.exists() and cmd_dir.is_dir():
            # Look for main.go in cmd subdirectories
            for subdir in cmd_dir.iterdir():
                if subdir.is_dir() and (subdir / "main.go").exists():
                    return f"go run cmd/{subdir.name}/main.go"
        
        # Check for app.go or server.go
        for filename in ["app.go", "server.go", "main.go"]:
            if self._find_file(project_path, filename):
                return f"go run {filename}"
        
        # Default fallback
        return "go run main.go"
    
    def _get_port(self, project_path: Path) -> int:
        """Determine the port."""
        # Check for port in Go files
        go_files = list(project_path.glob("*.go"))
        for go_file in go_files:
            content = self._read_text_file(go_file)
            # Look for port assignments
            for line in content.split('\n'):
                if 'port' in line.lower() and ('=' in line or ':' in line):
                    try:
                        # Extract port number
                        if '=' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                port_str = parts[1].strip().rstrip(',')
                                # Remove quotes and extract number
                                port_str = port_str.strip('"\'')
                                return int(port_str)
                        elif ':' in line:
                            # Look for :8080 pattern
                            import re
                            match = re.search(r':(\d+)', line)
                            if match:
                                return int(match.group(1))
                    except ValueError:
                        continue
        
        # Default port for Go
        return 8080
    
    def _get_environment(self) -> dict:
        """Get environment variables for Go projects."""
        return {
            "PORT": "8080"
        }
