"""
AWS Bedrock client for AI model interactions
"""

import boto3
import json
import asyncio
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.logging import get_logger
from app.core.config import settings
from app.models.schemas import BedrockModel

logger = get_logger(__name__)

class BedrockClient:
    """AWS Bedrock client wrapper"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Bedrock client with AWS credentials"""
        try:
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                if settings.is_production():
                    raise ValueError("AWS credentials are required in production mode")
                else:
                    logger.warning("⚠️ AWS credentials not configured - Bedrock features will be disabled")
                    self.client = None
                    return
            
            self.client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            logger.info("✅ AWS Bedrock client initialized successfully")
        except NoCredentialsError:
            error_msg = "❌ AWS credentials not found"
            logger.error(error_msg)
            if settings.is_production():
                raise ValueError(error_msg)
            self.client = None
        except Exception as e:
            error_msg = f"❌ Failed to initialize Bedrock client: {e}"
            logger.error(error_msg)
            if settings.is_production():
                raise ValueError(error_msg)
            self.client = None
    
    async def invoke_model(
        self, 
        model_id: BedrockModel, 
        prompt: str, 
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Invoke a Bedrock model with the given prompt"""
        if not self.client:
            logger.error("Bedrock client not initialized")
            return None
        
        try:
            # Prepare request body based on model type
            if model_id.value.startswith("us.anthropic.claude") or model_id.value.startswith("anthropic.claude"):
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            elif model_id.value.startswith("us.meta.llama") or model_id.value.startswith("meta.llama"):
                body = {
                    "prompt": prompt,
                    "max_gen_len": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                }
            elif model_id.value.startswith("us.amazon.nova") or model_id.value.startswith("amazon.nova"):
                body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": max_tokens,
                        "temperature": temperature,
                        "topP": 0.9
                    }
                }
            elif model_id.value.startswith("amazon.titan"):
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature,
                        "topP": 0.9
                    }
                }
            else:
                logger.error(f"Unsupported model: {model_id}")
                return None
            
            # Make the API call
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.invoke_model(
                    modelId=model_id.value,
                    body=json.dumps(body),
                    contentType='application/json',
                    accept='application/json'
                )
            )
            
            # Parse response based on model type
            response_body = json.loads(response['body'].read())
            
            if model_id.value.startswith("us.anthropic.claude") or model_id.value.startswith("anthropic.claude"):
                return response_body.get('content', [{}])[0].get('text', '')
            elif model_id.value.startswith("us.meta.llama") or model_id.value.startswith("meta.llama"):
                return response_body.get('generation', '')
            elif model_id.value.startswith("us.amazon.nova") or model_id.value.startswith("amazon.nova"):
                return response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
            elif model_id.value.startswith("amazon.titan"):
                return response_body.get('results', [{}])[0].get('outputText', '')
            
            return None
            
        except ClientError as e:
            logger.error(f"AWS Bedrock API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error invoking Bedrock model: {e}")
            return None

# Global instance
bedrock_client = BedrockClient()