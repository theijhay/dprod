"""Static site detector."""

from pathlib import Path

from .base import BaseDetector
from services.shared.core.models import ProjectType, ProjectConfig


class StaticDetector(BaseDetector):
    """Detector for static websites."""
    
    def __init__(self):
        super().__init__(ProjectType.STATIC)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a static site."""
        # Look for common static site files
        static_files = [
            "index.html",
            "index.htm",
            "public/index.html",
            "dist/index.html",
            "build/index.html"
        ]
        
        return any((project_path / file).exists() for file in static_files)
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Generate configuration for static site."""
        # Find the static files directory
        static_dirs = ["public", "dist", "build", "."]
        static_dir = "."
        
        for dir_name in static_dirs:
            if (project_path / dir_name / "index.html").exists():
                static_dir = dir_name
                break
        
        return ProjectConfig(
            type=ProjectType.STATIC,
            build_command="",  # No build needed for static sites
            start_command=f"nginx -g 'daemon off;'",
            port=80,
            environment={},
            install_path="/usr/share/nginx/html"
        )
    
    def generate_dockerfile(self, config: ProjectConfig) -> str:
        """Generate custom Dockerfile for static sites."""
        return f"""FROM nginx:alpine

# Copy static files
COPY . /usr/share/nginx/html

# Copy nginx configuration
RUN echo 'server {{' > /etc/nginx/conf.d/default.conf && \\
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    index index.html index.htm;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    location / {{' >> /etc/nginx/conf.d/default.conf && \\
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    }}' >> /etc/nginx/conf.d/default.conf && \\
    echo '}}' >> /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""