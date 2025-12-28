#!/usr/bin/env python3
"""
Script to help request access to Claude Sonnet 4 on AWS Bedrock
"""

import boto3
import json
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()

def check_model_access():
    """Check which models are available"""
    try:
        bedrock = boto3.client(
            'bedrock',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        print("🔍 Checking available models...")
        response = bedrock.list_foundation_models()
        
        claude_models = []
        available_models = []
        
        for model in response['modelSummaries']:
            if 'claude' in model['modelId'].lower():
                claude_models.append({
                    'id': model['modelId'],
                    'name': model['modelName'],
                    'status': model.get('modelLifecycle', {}).get('status', 'Unknown')
                })
            available_models.append({
                'id': model['modelId'],
                'name': model['modelName'],
                'provider': model['providerName'],
                'status': model.get('modelLifecycle', {}).get('status', 'Unknown')
            })
        
        print(f"\n📊 Found {len(available_models)} total models")
        print(f"🤖 Found {len(claude_models)} Claude models")
        
        print("\n🔹 Claude Models:")
        for model in claude_models:
            status_emoji = "✅" if model['status'] == 'ACTIVE' else "❌"
            print(f"  {status_emoji} {model['name']} ({model['id']}) - {model['status']}")
        
        # Check if Claude Sonnet 4 is available
        target_model = "anthropic.claude-sonnet-4-20250514-v1:0"
        claude_sonnet_4 = next((m for m in claude_models if target_model in m['id']), None)
        
        if claude_sonnet_4:
            if claude_sonnet_4['status'] == 'ACTIVE':
                print(f"\n🎉 Claude Sonnet 4 is ACTIVE and ready to use!")
                return True
            else:
                print(f"\n⚠️  Claude Sonnet 4 found but status: {claude_sonnet_4['status']}")
        else:
            print(f"\n❌ Claude Sonnet 4 ({target_model}) not found in available models")
        
        return False
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def print_access_instructions():
    """Print instructions for requesting model access"""
    print("\n" + "="*60)
    print("📋 HOW TO REQUEST ACCESS TO CLAUDE SONNET 4")
    print("="*60)
    
    print("""
1. 🌐 Go to AWS Bedrock Console:
   https://console.aws.amazon.com/bedrock/

2. 📍 Make sure you're in the correct region: us-west-2

3. 🔧 Navigate to "Model access" in the left sidebar

4. 🎯 Find "Claude Sonnet 4" in the list and click "Request model access"

5. 📝 Fill out the use case form with details like:
   - Use case: Software development and code generation
   - Description: Using Claude Sonnet 4 for MetaGPT multi-agent application generation
   - Expected usage: Development and testing purposes

6. ⏳ Wait for approval (usually takes 15 minutes to a few hours)

7. 🔄 Once approved, update your .env file:
   BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0

Alternative models you can use immediately:
- us.amazon.nova-pro-v1:0 (Amazon Nova Pro)
- us.amazon.nova-lite-v1:0 (Amazon Nova Lite)
- us.meta.llama3-3-70b-instruct-v1:0 (Llama 3.3 70B)
""")

def update_config_for_claude():
    """Update configuration to use Claude Sonnet 4"""
    print("\n🔧 To switch to Claude Sonnet 4 after approval:")
    print("1. Update your .env file:")
    print("   BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0")
    print("\n2. Restart your application")
    print("\n3. Run the test again:")
    print("   python test_bedrock_config.py")

def main():
    print("🚀 AWS Bedrock Claude Sonnet 4 Access Checker")
    print("="*50)
    
    # Check current model access
    has_access = check_model_access()
    
    if not has_access:
        print_access_instructions()
        update_config_for_claude()
    else:
        print("\n✅ You already have access to Claude Sonnet 4!")
        print("Update your .env file to use it:")
        print("BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0")

if __name__ == "__main__":
    main()