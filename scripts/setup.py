#!/usr/bin/env python3
"""
Setup script for development environment
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None


def setup_python_environment():
    """Setup Python environment"""
    print("🐍 Setting up Python environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
    
    run_command(f"{activate_cmd} && pip install --upgrade pip", "Upgrading pip")
    run_command(f"{activate_cmd} && pip install -r requirements.txt", "Installing Python dependencies")
    
    return True


def setup_node_environment():
    """Setup Node.js environment"""
    print("📦 Setting up Node.js environment...")
    
    # Check if Node.js is installed
    node_version = run_command("node --version", "Checking Node.js version")
    if not node_version:
        print("❌ Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/")
        return False
    
    print(f"✅ Node.js {node_version.strip()} detected")
    
    # Install npm dependencies
    run_command("npm install", "Installing Node.js dependencies")
    
    return True


def setup_environment_file():
    """Setup environment file"""
    print("⚙️ Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example file
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from .env.example")
        print("⚠️  Please update .env file with your actual configuration values")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ No .env.example file found")
        return False
    
    return True


def setup_directories():
    """Setup required directories"""
    print("📁 Setting up directories...")
    
    directories = [
        "logs",
        "workspace",
        "tests/fixtures"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True


def run_tests():
    """Run tests to verify setup"""
    print("🧪 Running tests to verify setup...")
    
    # Run Python tests
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
    
    test_result = run_command(f"{activate_cmd} && python -m pytest tests/ -v", "Running Python tests")
    
    if test_result:
        print("✅ All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed, but setup is complete")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up MetaGPT + E2B Integration System")
    print("=" * 50)
    
    success = True
    
    # Setup steps
    steps = [
        ("Python environment", setup_python_environment),
        ("Node.js environment", setup_node_environment),
        ("Environment file", setup_environment_file),
        ("Directories", setup_directories)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"❌ Failed to setup {step_name}")
            success = False
        print()
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your configuration")
        print("2. Run 'python test_bedrock_config.py' to test AWS Bedrock")
        print("3. Start development server: 'python main_clean.py'")
        print("4. Start frontend: 'npm run dev'")
        
        # Optionally run tests
        print("\n" + "=" * 50)
        run_tests()
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()