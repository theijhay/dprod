"""Docker executor for building and running containers."""
import asyncio
import logging
import docker
from docker.errors import DockerException, BuildError, APIError
from typing import Optional, Dict, Any, AsyncIterator
import tempfile
import os
import base64

from .config import config

logger = logging.getLogger(__name__)


class DockerExecutor:
    """Execute Docker builds and container runs."""
    
    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.DockerClient(base_url=f'unix://{config.DOCKER_SOCKET}')
            self.client.ping()
            logger.info("✅ Docker client initialized")
        except DockerException as e:
            logger.error(f"❌ Failed to initialize Docker client: {e}")
            raise
    
    async def build_image(
        self,
        deployment_id: str,
        project_files: Dict[str, str],
        dockerfile_content: Optional[str] = None
    ) -> Optional[str]:
        """Build Docker image from project files.
        
        Args:
            deployment_id: Deployment ID
            project_files: Dictionary of filename -> base64 content
            dockerfile_content: Optional Dockerfile content
            
        Returns:
            Image ID if successful, None otherwise
        """
        temp_dir = None
        try:
            # Create temporary directory for build context
            temp_dir = tempfile.mkdtemp(prefix=f"dprod-{deployment_id}-")
            logger.info(f"📁 Build context: {temp_dir}")
            
            # Write project files
            for filename, content_b64 in project_files.items():
                file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Decode base64 content
                content = base64.b64decode(content_b64)
                with open(file_path, 'wb') as f:
                    f.write(content)
            
            # Write Dockerfile if provided
            if dockerfile_content:
                with open(os.path.join(temp_dir, 'Dockerfile'), 'w') as f:
                    f.write(dockerfile_content)
            
            # Build image
            tag = f"dprod-{deployment_id}:latest"
            logger.info(f"🔨 Building image: {tag}")
            
            image, build_logs = await asyncio.to_thread(
                self.client.images.build,
                path=temp_dir,
                tag=tag,
                rm=True,
                forcerm=True
            )
            
            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    logger.debug(log['stream'].strip())
            
            logger.info(f"✅ Image built successfully: {image.id}")
            return image.id
            
        except BuildError as e:
            logger.error(f"❌ Build failed: {e}")
            for log in e.build_log:
                if 'stream' in log:
                    logger.error(log['stream'].strip())
            return None
            
        except Exception as e:
            logger.error(f"❌ Error building image: {e}", exc_info=True)
            return None
            
        finally:
            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def run_container(
        self,
        image_id: str,
        deployment_id: str,
        env_vars: Optional[Dict[str, str]] = None,
        ports: Optional[Dict[str, int]] = None
    ) -> Optional[str]:
        """Run a container from an image.
        
        Args:
            image_id: Docker image ID
            deployment_id: Deployment ID
            env_vars: Environment variables
            ports: Port mappings (container_port -> host_port)
            
        Returns:
            Container ID if successful
        """
        try:
            container_name = f"dprod-{deployment_id}"
            
            # Prepare port bindings
            port_bindings = {}
            if ports:
                for container_port, host_port in ports.items():
                    port_bindings[f'{container_port}/tcp'] = host_port
            
            logger.info(f"🚀 Starting container: {container_name}")
            
            container = await asyncio.to_thread(
                self.client.containers.run,
                image_id,
                name=container_name,
                environment=env_vars or {},
                ports=port_bindings,
                detach=True,
                remove=False,
                network=config.CONTAINER_NETWORK,
                restart_policy={"Name": "unless-stopped"}
            )
            
            logger.info(f"✅ Container started: {container.id}")
            return container.id
            
        except APIError as e:
            logger.error(f"❌ Error starting container: {e}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return None
    
    async def get_container_info(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Get container information.
        
        Args:
            container_id: Container ID
            
        Returns:
            Container info dict
        """
        try:
            container = self.client.containers.get(container_id)
            container.reload()
            
            # Get container IP
            networks = container.attrs.get('NetworkSettings', {}).get('Networks', {})
            ip_address = None
            for network in networks.values():
                if network.get('IPAddress'):
                    ip_address = network['IPAddress']
                    break
            
            # Get exposed ports
            ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            exposed_ports = {}
            for container_port, bindings in ports.items():
                if bindings:
                    exposed_ports[container_port] = bindings[0].get('HostPort')
            
            return {
                'id': container.id,
                'name': container.name,
                'status': container.status,
                'ip_address': ip_address,
                'ports': exposed_ports,
                'created': container.attrs.get('Created'),
                'started': container.attrs.get('State', {}).get('StartedAt')
            }
            
        except docker.errors.NotFound:
            logger.warning(f"⚠️  Container not found: {container_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting container info: {e}")
            return None
    
    async def get_container_logs(
        self,
        container_id: str,
        tail: int = 100
    ) -> Optional[str]:
        """Get container logs.
        
        Args:
            container_id: Container ID
            tail: Number of lines to return
            
        Returns:
            Log output as string
        """
        try:
            container = self.client.containers.get(container_id)
            logs = await asyncio.to_thread(
                container.logs,
                tail=tail,
                timestamps=True
            )
            return logs.decode('utf-8')
            
        except docker.errors.NotFound:
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting logs: {e}")
            return None
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """Stop a container.
        
        Args:
            container_id: Container ID
            timeout: Timeout in seconds
            
        Returns:
            True if successful
        """
        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.stop, timeout=timeout)
            logger.info(f"🛑 Container stopped: {container_id}")
            return True
            
        except docker.errors.NotFound:
            logger.warning(f"⚠️  Container not found: {container_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error stopping container: {e}")
            return False
    
    async def remove_container(self, container_id: str, force: bool = False) -> bool:
        """Remove a container.
        
        Args:
            container_id: Container ID
            force: Force remove
            
        Returns:
            True if successful
        """
        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.remove, force=force)
            logger.info(f"🗑️  Container removed: {container_id}")
            return True
            
        except docker.errors.NotFound:
            return True  # Already removed
            
        except Exception as e:
            logger.error(f"❌ Error removing container: {e}")
            return False
    
    def cleanup(self):
        """Cleanup Docker client."""
        try:
            self.client.close()
        except:
            pass
