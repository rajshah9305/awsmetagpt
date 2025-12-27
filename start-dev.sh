#!/bin/bash

# MetaGPT + AWS Bedrock App Generator Development Startup Script

set -e  # Exit on any error

echo "🚀 Starting MetaGPT + AWS Bedrock App Generator (Development Mode)"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please configure your AWS credentials"
fi

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install

echo ""
echo "🎯 Starting development servers..."
echo "🔧 Backend API: http://localhost:8000"
echo "🌐 Frontend UI: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔧 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🚀 Starting backend server (port 8000)..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo "🚀 Starting frontend server (port 3000)..."
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID