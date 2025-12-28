#!/usr/bin/env python3
"""
Setup script for MetaGPT + E2B integration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_virtual_environment():
    """Set up virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            return False
    
    return True

def setup_workspace():
    """Set up MetaGPT workspace directory"""
    workspace_path = Path("workspace")
    workspace_path.mkdir(exist_ok=True)
    print("✅ MetaGPT workspace directory created")
    return True

def check_env_file():
    """Check if .env file exists and guide user"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from .env.example")
        else:
            print("❌ .env.example file not found")
            return False
    
    print("\n🔧 CONFIGURATION REQUIRED:")
    print("Please edit the .env file and add your API keys:")
    print("  - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (for Bedrock)")
    print("  - OPENAI_API_KEY or ANTHROPIC_API_KEY (for MetaGPT)")
    print("  - E2B_API_KEY (for live code execution)")
    print("\nGet your E2B API key from: https://e2b.dev/")
    print("Get your OpenAI API key from: https://platform.openai.com/")
    print("Get your Anthropic API key from: https://console.anthropic.com/")
    
    return True

def install_frontend_dependencies():
    """Install Node.js dependencies for frontend"""
    if not shutil.which("npm"):
        print("⚠️  npm not found. Please install Node.js to run the frontend")
        return False
    
    return run_command("npm install", "Installing frontend dependencies")

def main():
    """Main setup function"""
    print("🚀 Setting up MetaGPT + E2B Integration")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Set up workspace
    if not setup_workspace():
        sys.exit(1)
    
    # Check/create .env file
    if not check_env_file():
        sys.exit(1)
    
    # Install frontend dependencies
    install_frontend_dependencies()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Run the application:")
    print("   - Backend: ./start.sh")
    print("   - Development: ./start-dev.sh")
    print("\n📚 Documentation:")
    print("   - MetaGPT: https://github.com/geekan/MetaGPT")
    print("   - E2B: https://e2b.dev/docs")

if __name__ == "__main__":
    main()