# AWS Bedrock Setup and Testing

This document contains the setup and testing process for AWS Bedrock integration.

## AWS CLI Configuration

```bash
# Check your current region
aws configure get region

# Set region if needed (Bedrock is available in specific regions)
aws configure set region us-west-2

# Verify Bedrock access
aws bedrock list-foundation-models --query 'modelSummaries[0:5].[modelName,modelId]' --output table
```

## Available Models

The following models are available in the us-west-2 region:

- Claude Sonnet 4 (anthropic.claude-sonnet-4-20250514-v1:0)
- Claude Haiku 4.5 (anthropic.claude-haiku-4-5-20251001-v1:0)
- Amazon Nova Pro (us.amazon.nova-pro-v1:0)
- Various other models from different providers

## Testing Script

```python
import boto3
import json

# Create Bedrock client
bedrock = boto3.client('bedrock')

# List models
response = bedrock.list_foundation_models()
print("Available Models:")
for model in response['modelSummaries'][:5]:
    print(f"- {model['modelName']} ({model['modelId']})")
```

## Configuration Notes

- AWS Region: us-west-2 (recommended for Bedrock)
- Default Model: us.amazon.nova-pro-v1:0 (Amazon Nova Pro)
- Credentials: Configure via AWS CLI or environment variables
- All sensitive credentials have been redacted for security