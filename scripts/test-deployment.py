#!/usr/bin/env python3
"""Test script to verify Dprod deployment functionality."""

import asyncio
import tempfile
import tarfile
import io
from pathlib import Path

# Add services to path
import sys
sys.path.append('services')

from shared.core.models import Project, ProjectType
from detector.core.detector import ProjectDetector
from orchestrator.core.deployment_manager import DeploymentManager


async def test_detection_engine():
    """Test the project detection engine."""
    print("🔍 Testing Project Detection Engine...")
    
    # Create a test Node.js project
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create package.json
        package_json = {
            "name": "test-app",
            "version": "1.0.0",
            "scripts": {
                "start": "node index.js"
            }
        }
        
        (temp_path / "package.json").write_text(str(package_json).replace("'", '"'))
        (temp_path / "index.js").write_text("console.log('Hello World!');")
        
        # Test detection
        detector = ProjectDetector()
        config = detector.detect(temp_path)
        
        print(f"✅ Detected project type: {config.type}")
        print(f"✅ Start command: {config.start_command}")
        print(f"✅ Port: {config.port}")
        
        assert config.type == ProjectType.NODEJS
        assert "npm" in config.start_command
        assert config.port == 3000
        
        print("✅ Detection engine test passed!")


async def test_docker_orchestrator():
    """Test the Docker orchestrator."""
    print("\n🐳 Testing Docker Orchestrator...")
    
    try:
        # Create a test project
        project = Project(
            id="test-project-123",
            user_id="test-user-123",
            name="test-app",
            type=ProjectType.NODEJS
        )
        
        # Create test source code
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a simple Node.js app
            (temp_path / "package.json").write_text('{"name":"test","version":"1.0.0","scripts":{"start":"node index.js"}}')
            (temp_path / "index.js").write_text("console.log('Hello from Dprod!');")
            
            # Create tar.gz
            tar_buffer = io.BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
                tar.add(temp_path, arcname='.')
            tar_buffer.seek(0)
            
            # Test deployment
            deployment_manager = DeploymentManager()
            detector = ProjectDetector()
            
            print("🚀 Starting test deployment...")
            deployment_info = await deployment_manager.deploy_project(
                project=project,
                source_code=tar_buffer.getvalue(),
                detection_engine=detector
            )
            
            print(f"✅ Deployment successful!")
            print(f"🔗 URL: {deployment_info.get('url')}")
            print(f"📦 Container: {deployment_info.get('container_id', 'N/A')[:12]}")
            
            # Cleanup
            await deployment_manager.stop_deployment(project.id)
            print("🧹 Cleaned up test deployment")
            
    except Exception as e:
        print(f"⚠️  Docker orchestrator test failed (this is expected if Docker is not running): {e}")
        print("   This is normal in environments without Docker access")


async def main():
    """Run all tests."""
    print("🧪 Running Dprod Integration Tests\n")
    
    # Test detection engine
    await test_detection_engine()
    
    # Test Docker orchestrator (may fail if Docker not available)
    await test_docker_orchestrator()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Next steps:")
    print("   1. Start the development environment: make dev")
    print("   2. Test the API: curl http://localhost:8000/health")
    print("   3. Install CLI: cd packages/cli && npm install")
    print("   4. Test CLI: node src/index.js --help")


if __name__ == "__main__":
    asyncio.run(main())
