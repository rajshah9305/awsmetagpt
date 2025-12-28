#!/usr/bin/env python3
"""
Deployment verification script for MetaGPT + E2B integration
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version < (3, 8):
        print("❌ Python 3.8+ required, found:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if all Python dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'boto3', 'websockets', 
        'metagpt', 'e2b', 'pydantic_settings', 'python_dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    return len(missing) == 0, missing

def check_node_dependencies():
    """Check if Node.js dependencies are installed"""
    if not Path("node_modules").exists():
        print("❌ Node.js dependencies not installed")
        return False
    
    print("✅ Node.js dependencies installed")
    return True

def check_environment():
    """Check environment configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Check for required environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    optional_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'E2B_API_KEY']
    
    with open(env_file) as f:
        content = f.read()
    
    missing_required = []
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_required.append(var)
        else:
            print(f"✅ {var} configured")
    
    missing_optional = []
    for var in optional_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_optional.append(var)
        else:
            print(f"✅ {var} configured")
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    if len(missing_optional) == len(optional_vars):
        print("⚠️  No AI API keys configured (need at least one)")
        return False
    
    return True

def check_ports():
    """Check if required ports are available"""
    import socket
    
    ports = [8000, 3000]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} is in use")
        else:
            print(f"✅ Port {port} available")
    
    return True

def check_workspace():
    """Check workspace directory"""
    workspace = Path("workspace")
    if not workspace.exists():
        workspace.mkdir(exist_ok=True)
        print("✅ Workspace directory created")
    else:
        print("✅ Workspace directory exists")
    return True

def main():
    """Main verification function"""
    print("🔍 MetaGPT + E2B Deployment Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", lambda: check_dependencies()[0]),
        ("Node.js Dependencies", check_node_dependencies),
        ("Environment Configuration", check_environment),
        ("Port Availability", check_ports),
        ("Workspace Setup", check_workspace),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            if check_func():
                passed += 1
            else:
                print(f"❌ {name} failed")
        except Exception as e:
            print(f"❌ {name} error: {e}")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready for deployment.")
        print("\n🚀 To start the application:")
        print("   Development: ./start-dev.sh")
        print("   Production:  ./start.sh")
        return True
    else:
        print(f"\n⚠️  {total - passed} issues need to be resolved.")
        
        # Provide specific guidance
        if not check_dependencies()[0]:
            print("\n💡 To fix Python dependencies:")
            print("   pip install -r requirements.txt")
        
        if not check_node_dependencies():
            print("\n💡 To fix Node.js dependencies:")
            print("   npm install")
        
        if not check_environment():
            print("\n💡 To fix environment configuration:")
            print("   1. Copy .env.example to .env")
            print("   2. Add your AWS credentials")
            print("   3. Add at least one AI API key (OpenAI/Anthropic)")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)