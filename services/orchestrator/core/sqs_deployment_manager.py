"""SQS-based deployment manager for hybrid architecture."""

import asyncio
import base64
import json
import os
import tempfile
import tarfile
from pathlib import Path
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

from services.shared.core.models import Project
from services.shared.core.schemas import ProjectConfig
from services.shared.core.exceptions import DeploymentError, BuildError


class SQSDeploymentManager:
    """Manages deployments via SQS queue for EC2 workers."""
    
    def __init__(self):
        """Initialize SQS deployment manager."""
        self.sqs_queue_url = os.getenv("SQS_QUEUE_URL")
        if not self.sqs_queue_url:
            raise ValueError("SQS_QUEUE_URL environment variable is required")
        
        # Get AWS region from queue URL or environment
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize SQS client
        self.sqs_client = boto3.client('sqs', region_name=self.aws_region)
        
        print(f"📥 SQS Deployment Manager initialized: {self.sqs_queue_url}")
    
    async def deploy_project(
        self,
        project: Project,
        source_code: bytes,
        detection_engine
    ) -> Dict[str, Any]:
        """
        Deploy a project by queuing it to SQS.
        
        Args:
            project: Project database model
            source_code: Compressed source code bytes
            detection_engine: Project detection engine (can be AI-enhanced)
            
        Returns:
            Dict containing deployment information
        """
        try:
            print(f"🚀 Queueing deployment for project: {project.name}")
            
            # Create temporary directory for build context
            with tempfile.TemporaryDirectory() as temp_dir:
                build_context = Path(temp_dir)
                
                # Extract source code
                await self._extract_source_code(source_code, build_context)
                
                # Detect project type and generate config
                is_ai_detector = hasattr(detection_engine, 'detect_project') and \
                                asyncio.iscoroutinefunction(detection_engine.detect_project)
                
                if is_ai_detector:
                    # AI-enhanced detection (async)
                    detection_result = await detection_engine.detect_project(
                        build_context,
                        project_id=str(project.id),
                        use_ai=True
                    )
                    
                    if not detection_result:
                        raise DeploymentError("Could not detect project type")
                    
                    config = detection_result.get('recommended_config') or \
                             detection_result.get('config') or \
                             detection_result.get('rule_based_config')
                    
                    decision_id = detection_result.get('decision_id')
                    ai_verified = detection_result.get('ai_verified', False)
                    
                    if ai_verified:
                        print(f"🤖 AI-enhanced detection used (decision_id: {decision_id})")
                else:
                    # Rule-based detection (sync)
                    config = detection_engine.detect_project(build_context)
                    decision_id = None
                    ai_verified = False
                
                if not config:
                    raise DeploymentError("Could not detect project type")
                
                print(f"📋 Project config: {config}")
                
                # Prepare project files as base64
                project_files = await self._encode_project_files(build_context)
                
                # Generate dockerfile content if needed
                dockerfile_content = None
                dockerfile_path = build_context / "Dockerfile"
                if dockerfile_path.exists():
                    with open(dockerfile_path, 'r') as f:
                        dockerfile_content = f.read()
                
                # Prepare deployment job message
                job_message = {
                    "deployment_id": str(project.id),
                    "project_name": project.name,
                    "project_files": project_files,
                    "dockerfile_content": dockerfile_content,
                    "environment": config.environment if hasattr(config, 'environment') else {},
                    "ports": config.ports if hasattr(config, 'ports') else {"3000": 3000},
                    "config": config.dict() if hasattr(config, 'dict') else config,
                    "ai_verified": ai_verified,
                    "decision_id": decision_id
                }
                
                # Send to SQS
                await self._send_to_sqs(job_message)
                
                # Generate URL (will be updated by worker once deployed)
                subdomain = getattr(project, 'subdomain', None) or project.name.lower().replace('_', '-')
                url = f"https://{subdomain}.dprod.app"
                
                deployment_info = {
                    "project_id": str(project.id),
                    "status": "queued",
                    "url": url,
                    "message": "Deployment queued successfully. Worker will process shortly.",
                    "config": config.dict() if hasattr(config, 'dict') else config,
                    "ai_verified": ai_verified,
                    "decision_id": decision_id
                }
                
                print(f"✅ Deployment queued: {url}")
                
                # Verify AI decision outcome if applicable
                if is_ai_detector and decision_id:
                    try:
                        await detection_engine.verify_deployment_outcome(
                            decision_id=decision_id,
                            was_successful=True,
                            feedback="Deployment queued successfully"
                        )
                        print(f"📊 AI decision outcome logged")
                    except Exception as e:
                        print(f"⚠️  Failed to log AI outcome: {e}")
                
                return deployment_info
                
        except Exception as e:
            print(f"❌ Deployment queueing failed: {e}")
            raise DeploymentError(f"Failed to queue deployment: {e}")
    
    async def _send_to_sqs(self, job_message: Dict[str, Any]) -> None:
        """Send deployment job to SQS queue."""
        try:
            # Convert to JSON
            message_body = json.dumps(job_message)
            
            # Send message
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.sqs_client.send_message(
                    QueueUrl=self.sqs_queue_url,
                    MessageBody=message_body,
                    MessageAttributes={
                        'deployment_id': {
                            'StringValue': job_message['deployment_id'],
                            'DataType': 'String'
                        },
                        'project_name': {
                            'StringValue': job_message['project_name'],
                            'DataType': 'String'
                        }
                    }
                )
            )
            
            message_id = response.get('MessageId')
            print(f"📤 Message sent to SQS: {message_id}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise DeploymentError(f"SQS error ({error_code}): {error_message}")
        except Exception as e:
            raise DeploymentError(f"Failed to send message to SQS: {e}")
    
    async def _encode_project_files(self, build_context: Path) -> Dict[str, str]:
        """Encode project files as base64 for SQS message."""
        files = {}
        
        for file_path in build_context.rglob('*'):
            if file_path.is_file():
                # Get relative path
                rel_path = file_path.relative_to(build_context)
                
                # Read and encode file
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        encoded = base64.b64encode(content).decode('utf-8')
                        files[str(rel_path)] = encoded
                except Exception as e:
                    print(f"⚠️  Failed to encode file {rel_path}: {e}")
        
        print(f"📦 Encoded {len(files)} files for deployment")
        return files
    
    async def _extract_source_code(self, source_code: bytes, target_dir: Path) -> None:
        """Extract compressed source code to target directory."""
        try:
            # Write compressed data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as temp_file:
                temp_file.write(source_code)
                temp_file_path = temp_file.name
            
            # Extract tar.gz file
            with tarfile.open(temp_file_path, 'r:gz') as tar:
                tar.extractall(target_dir)
            
            # Clean up temporary file
            Path(temp_file_path).unlink()
            
        except Exception as e:
            raise BuildError(f"Failed to extract source code: {e}")
    
    async def get_deployment_status(self, project_id: str) -> Dict[str, Any]:
        """Get deployment status for a project.
        
        Note: Status is now tracked in the database by workers.
        This method queries the database instead of local state.
        """
        # TODO: Query database for deployment status
        return {
            "status": "pending",
            "project_id": project_id,
            "message": "Check database for deployment status"
        }
    
    async def get_deployment_logs(self, project_id: str) -> str:
        """Get deployment logs for a project.
        
        Note: Logs are now tracked in the database by workers.
        """
        # TODO: Query database for deployment logs
        return "Check database for deployment logs"
    
    async def stop_deployment(self, project_id: str) -> bool:
        """Stop a deployment.
        
        Note: Stopping deployments requires communicating with workers.
        This would need a separate queue or database flag.
        """
        # TODO: Implement deployment stop via worker communication
        print(f"⚠️  Stop deployment not yet implemented for SQS-based deployments")
        return False
    
    async def list_deployments(self) -> Dict[str, Dict[str, Any]]:
        """List all active deployments.
        
        Note: Deployments are now tracked in the database.
        """
        # TODO: Query database for all deployments
        return {}
    
    async def health_check(self, project_id: str) -> bool:
        """Perform health check on a deployment.
        
        Note: Health status is now tracked in the database by workers.
        """
        # TODO: Query database for deployment health
        return False
