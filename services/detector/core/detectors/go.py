"""Go project detector."""

from pathlib import Path

from .base import BaseDetector
from services.shared.core.models import ProjectType
from services.shared.core.schemas import ProjectConfig


class GoDetector(BaseDetector):
    """Detector for Go projects."""
    
    def __init__(self):
        super().__init__(ProjectType.GO)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a Go project."""
        go_mod = project_path / "go.mod"
        return go_mod.exists()
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Generate configuration for Go project."""
        # Look for main.go or other Go files
        main_files = ["main.go", "cmd/main.go", "app.go"]
        start_command = "go run main.go"
        
        for main_file in main_files:
            if (project_path / main_file).exists():
                start_command = f"go run {main_file}"
                break
        
        return ProjectConfig(
            type=ProjectType.GO,
            build_command="go mod download && go build -o app .",
            start_command=start_command,
            port=8080,
            environment={"CGO_ENABLED": "0"},
            install_path="/app"
        )