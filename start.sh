#!/bin/bash

# MetaGPT + AWS Bedrock App Generator Production Startup Script

set -e  # Exit on any error

echo "🚀 Starting MetaGPT + AWS Bedrock App Generator (Production Mode)"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 16 ]; then
    echo "❌ Node.js 16+ required. Found: v$node_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create MetaGPT workspace directory
echo "📁 Setting up MetaGPT workspace..."
mkdir -p workspace

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please configure your API keys:"
    echo "   - AWS credentials for Bedrock"
    echo "   - OpenAI or Anthropic API key for MetaGPT"
    echo "   - E2B API key for live code execution"
else
    echo "✅ .env file already exists"
fi

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm ci --production=false

# Build frontend for production
echo "🏗️  Building frontend for production..."
npm run build

# Verify build
if [ ! -d "dist" ]; then
    echo "❌ Frontend build failed - dist directory not found"
    exit 1
fi

echo "✅ Build completed successfully"

echo ""
echo "🎯 Starting production server..."
echo "🌐 Application: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔧 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Required Configuration:"
echo "   Make sure your .env file contains:"
echo "   - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY"
echo "   - E2B_API_KEY (get from https://e2b.dev/)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start production server
exec python3 main.py