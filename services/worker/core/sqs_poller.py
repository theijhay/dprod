"""SQS message poller for deployment jobs."""
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
import boto3
from botocore.exceptions import ClientError

from .config import config

logger = logging.getLogger(__name__)


class SQSPoller:
    """Poll SQS queue for deployment jobs."""
    
    def __init__(self):
        """Initialize SQS client."""
        self.sqs = boto3.client('sqs', region_name=config.AWS_REGION)
        self.queue_url = config.SQS_QUEUE_URL
        self.running = False
        
    async def start(self, message_handler):
        """Start polling for messages.
        
        Args:
            message_handler: Async function to handle messages
        """
        self.running = True
        logger.info(f"🚀 Worker {config.WORKER_ID} starting SQS poller...")
        logger.info(f"📥 Polling queue: {self.queue_url}")
        
        while self.running:
            try:
                # Poll for messages
                messages = await self._receive_messages()
                
                if messages:
                    logger.info(f"📬 Received {len(messages)} message(s)")
                    
                    # Process messages concurrently (up to MAX_CONCURRENT_JOBS)
                    tasks = []
                    for message in messages[:config.MAX_CONCURRENT_JOBS]:
                        task = asyncio.create_task(
                            self._process_message(message, message_handler)
                        )
                        tasks.append(task)
                    
                    # Wait for all tasks to complete
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    # No messages, wait before polling again
                    await asyncio.sleep(config.POLL_INTERVAL)
                    
            except Exception as e:
                logger.error(f"❌ Error in polling loop: {e}", exc_info=True)
                await asyncio.sleep(config.POLL_INTERVAL)
    
    async def stop(self):
        """Stop polling."""
        logger.info("🛑 Stopping SQS poller...")
        self.running = False
    
    async def _receive_messages(self) -> List[Dict[str, Any]]:
        """Receive messages from SQS.
        
        Returns:
            List of messages
        """
        try:
            response = await asyncio.to_thread(
                self.sqs.receive_message,
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=config.MAX_CONCURRENT_JOBS,
                WaitTimeSeconds=20,  # Long polling
                VisibilityTimeout=config.MESSAGE_VISIBILITY_TIMEOUT,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            
            return response.get('Messages', [])
            
        except ClientError as e:
            logger.error(f"❌ Error receiving messages: {e}")
            return []
    
    async def _process_message(self, message: Dict[str, Any], handler):
        """Process a single message.
        
        Args:
            message: SQS message
            handler: Message handler function
        """
        receipt_handle = message['ReceiptHandle']
        message_id = message['MessageId']
        
        try:
            # Parse message body
            body = json.loads(message['Body'])
            logger.info(f"🔄 Processing job: {body.get('deployment_id', 'unknown')}")
            
            # Handle the message
            success = await handler(body)
            
            if success:
                # Delete message from queue
                await self._delete_message(receipt_handle)
                logger.info(f"✅ Job completed: {message_id}")
            else:
                logger.warning(f"⚠️  Job failed, message will be retried: {message_id}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in message {message_id}: {e}")
            # Delete invalid messages
            await self._delete_message(receipt_handle)
            
        except Exception as e:
            logger.error(f"❌ Error processing message {message_id}: {e}", exc_info=True)
            # Message will become visible again after visibility timeout
    
    async def _delete_message(self, receipt_handle: str):
        """Delete message from queue.
        
        Args:
            receipt_handle: Message receipt handle
        """
        try:
            await asyncio.to_thread(
                self.sqs.delete_message,
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
        except ClientError as e:
            logger.error(f"❌ Error deleting message: {e}")
    
    async def send_message(self, message: Dict[str, Any]) -> Optional[str]:
        """Send a message to the queue.
        
        Args:
            message: Message body
            
        Returns:
            Message ID if successful
        """
        try:
            response = await asyncio.to_thread(
                self.sqs.send_message,
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message)
            )
            return response.get('MessageId')
            
        except ClientError as e:
            logger.error(f"❌ Error sending message: {e}")
            return None
