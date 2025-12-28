#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock configuration with Claude Sonnet 4
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.config import settings
from app.services.bedrock_client import bedrock_client
from app.models.schemas import BedrockModel

async def test_bedrock_configuration():
    """Test the Bedrock configuration"""
    print("🔧 Testing AWS Bedrock Configuration")
    print("=" * 50)
    
    # Test configuration loading
    print(f"AWS Region: {settings.AWS_REGION}")
    print(f"Bedrock Region: {settings.BEDROCK_REGION}")
    print(f"Bedrock Model: {settings.BEDROCK_MODEL}")
    print(f"Max Tokens: {settings.BEDROCK_MAX_TOKENS}")
    print(f"Temperature: {settings.BEDROCK_TEMPERATURE}")
    print()
    
    # Test AWS credentials (without exposing them)
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        print("✅ AWS credentials are configured")
        print(f"Access Key ID: {settings.AWS_ACCESS_KEY_ID[:8]}...")
    else:
        print("❌ AWS credentials are missing")
        return False
    
    # Test Bedrock client initialization
    if bedrock_client.client:
        print("✅ Bedrock client initialized successfully")
    else:
        print("❌ Bedrock client failed to initialize")
        return False
    
    # Test model invocation with a simple prompt
    print("\n🧪 Testing Claude Sonnet 4 model invocation...")
    try:
        response = await bedrock_client.invoke_model(
            model_id=BedrockModel.NOVA_PRO,
            prompt="Hello! Please respond with 'Configuration test successful' if you can read this.",
            max_tokens=50,
            temperature=0.1
        )
        
        if response:
            print(f"✅ Model response: {response.strip()}")
            return True
        else:
            print("❌ No response from model")
            return False
            
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🌍 Environment Variables Check")
    print("=" * 30)
    
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", 
        "AWS_REGION",
        "BEDROCK_REGION",
        "BEDROCK_MODEL"
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var:
                print(f"✅ {var}: {value[:8]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_present = False
    
    return all_present

async def main():
    """Main test function"""
    print("🚀 AWS Bedrock + Claude Sonnet 4 Configuration Test")
    print("=" * 60)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variables are not properly configured")
        print("Please check your .env file")
        return
    
    # Test Bedrock configuration
    config_ok = await test_bedrock_configuration()
    
    if config_ok:
        print("\n🎉 All tests passed! Claude Sonnet 4 is ready to use.")
    else:
        print("\n❌ Configuration test failed. Please check your setup.")

if __name__ == "__main__":
    asyncio.run(main())