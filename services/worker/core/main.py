"""Main worker process for handling deployment jobs."""
import asyncio
import logging
import signal
import sys
from typing import Dict, Any

from .config import config
from .sqs_poller import SQSPoller
from .docker_executor import DockerExecutor
from .status_updater import StatusUpdater

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/dprod-worker.log')
    ]
)

logger = logging.getLogger(__name__)


class DeploymentWorker:
    """Main deployment worker."""
    
    def __init__(self):
        """Initialize worker components."""
        self.sqs_poller = SQSPoller()
        self.docker_executor = DockerExecutor()
        self.status_updater = StatusUpdater()
        self.running = False
    
    async def handle_deployment_job(self, job: Dict[str, Any]) -> bool:
        """Handle a deployment job from SQS.
        
        Args:
            job: Job data from SQS message
            
        Returns:
            True if successful, False otherwise
        """
        deployment_id = job.get('deployment_id')
        if not deployment_id:
            logger.error("❌ No deployment_id in job")
            return False
        
        logger.info(f"🚀 Processing deployment: {deployment_id}")
        
        try:
            # Update status to building
            await self.status_updater.update_build_started(deployment_id)
            await self.status_updater.add_build_log(
                deployment_id,
                f"Build started on worker {config.WORKER_ID}"
            )
            
            # Extract job data
            project_files = job.get('project_files', {})
            dockerfile_content = job.get('dockerfile_content')
            env_vars = job.get('environment', {})
            ports = job.get('ports', {})
            
            if not project_files:
                raise ValueError("No project files provided")
            
            # Build Docker image
            logger.info(f"🔨 Building image for {deployment_id}")
            await self.status_updater.add_build_log(
                deployment_id,
                "Building Docker image..."
            )
            
            image_id = await self.docker_executor.build_image(
                deployment_id,
                project_files,
                dockerfile_content
            )
            
            if not image_id:
                raise RuntimeError("Image build failed")
            
            await self.status_updater.update_build_completed(
                deployment_id,
                image_id
            )
            await self.status_updater.add_build_log(
                deployment_id,
                f"Image built successfully: {image_id[:12]}"
            )
            
            # Run container
            logger.info(f"🚀 Starting container for {deployment_id}")
            await self.status_updater.add_build_log(
                deployment_id,
                "Starting container..."
            )
            
            container_id = await self.docker_executor.run_container(
                image_id,
                deployment_id,
                env_vars,
                ports
            )
            
            if not container_id:
                raise RuntimeError("Container start failed")
            
            # Get container info
            container_info = await self.docker_executor.get_container_info(container_id)
            
            # Determine URL
            url = None
            if container_info and container_info.get('ports'):
                # Get first exposed port
                first_port = list(container_info['ports'].values())[0]
                if first_port:
                    # Use EC2 instance public IP (will be set in environment)
                    public_ip = job.get('worker_public_ip') or 'localhost'
                    url = f"http://{public_ip}:{first_port}"
            
            # Update deployment as running
            await self.status_updater.update_deployment_running(
                deployment_id,
                container_id,
                url
            )
            await self.status_updater.add_build_log(
                deployment_id,
                f"✅ Deployment successful! Container: {container_id[:12]}"
            )
            
            if url:
                await self.status_updater.add_build_log(
                    deployment_id,
                    f"🌐 Application available at: {url}"
                )
            
            logger.info(f"✅ Deployment completed: {deployment_id}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Deployment failed: {deployment_id} - {error_msg}", exc_info=True)
            
            await self.status_updater.update_deployment_failed(
                deployment_id,
                error_msg
            )
            await self.status_updater.add_build_log(
                deployment_id,
                f"❌ Deployment failed: {error_msg}"
            )
            
            return False
    
    async def start(self):
        """Start the worker."""
        self.running = True
        
        logger.info("=" * 60)
        logger.info(f"🚀 dprod Worker {config.WORKER_ID} starting...")
        logger.info(f"📥 SQS Queue: {config.SQS_QUEUE_URL}")
        logger.info(f"🔧 Max concurrent jobs: {config.MAX_CONCURRENT_JOBS}")
        logger.info(f"⏱️  Poll interval: {config.POLL_INTERVAL}s")
        logger.info("=" * 60)
        
        # Validate configuration
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            return
        
        # Start polling
        try:
            await self.sqs_poller.start(self.handle_deployment_job)
        except KeyboardInterrupt:
            logger.info("⌨️  Received keyboard interrupt")
        except Exception as e:
            logger.error(f"❌ Worker error: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the worker gracefully."""
        if not self.running:
            return
        
        logger.info("🛑 Shutting down worker...")
        self.running = False
        
        # Stop SQS poller
        await self.sqs_poller.stop()
        
        # Cleanup
        self.docker_executor.cleanup()
        await self.status_updater.cleanup()
        
        logger.info("👋 Worker stopped")


async def main():
    """Main entry point."""
    worker = DeploymentWorker()
    
    # Handle signals
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        logger.info("📡 Received shutdown signal")
        asyncio.create_task(worker.stop())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    # Start worker
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
