#!/bin/bash

# MetaGPT + E2B Integration System - Development Startup Script
# Enhanced with hot reloading and development tools

set -e  # Exit on any error

echo "🚀 Starting MetaGPT + E2B Integration System (Development Mode)"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check system requirements
print_info "Checking system requirements..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.8+ required. Found: $python_version"
    exit 1
fi
print_status "Python version: $python_version"

# Check Node.js version
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 16 ]; then
    print_error "Node.js 16+ required. Found: v$node_version"
    exit 1
fi
print_status "Node.js version: v$node_version"

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Install development dependencies
print_info "Installing development dependencies..."
pip install --quiet \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy

# Create necessary directories
print_info "Setting up directories..."
mkdir -p workspace
mkdir -p logs
mkdir -p temp

# Check environment configuration
print_info "Setting up development environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        
        # Set development-specific values
        sed -i.bak 's/DEBUG=false/DEBUG=true/' .env
        sed -i.bak 's/LOG_LEVEL=INFO/LOG_LEVEL=DEBUG/' .env
        sed -i.bak 's/RELOAD_ON_CHANGE=false/RELOAD_ON_CHANGE=true/' .env
        rm .env.bak 2>/dev/null || true
        
        print_warning "Please configure your API keys in .env file:"
        print_warning "   - AWS credentials for Bedrock"
        print_warning "   - OpenAI or Anthropic API key for MetaGPT"
        print_warning "   - E2B API key for live code execution"
    else
        print_error ".env.example file not found"
        exit 1
    fi
else
    print_status ".env file exists"
fi

# Install Node.js dependencies
print_info "Installing Node.js dependencies..."
npm install --silent

# Run quick system validation
print_info "Running quick system validation..."
if python3 validate_system.py; then
    print_status "System validation passed"
else
    print_warning "System validation had issues - check configuration"
    print_info "Run 'python3 validate_system.py --report' for detailed report"
fi

# Display development server information
echo ""
echo "=================================================="
print_info "Development servers will start on:"
echo "🔧 Backend API: http://localhost:8000"
echo "🌐 Frontend UI: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔧 Health Check: http://localhost:8000/api/v1/health"
echo "📊 System Status: http://localhost:8000/api/v1/system/status"
echo ""
print_info "Development features enabled:"
echo "   🔄 Hot reloading for both frontend and backend"
echo "   🐛 Debug mode with detailed error messages"
echo "   📝 Verbose logging for development"
echo "   🧪 API documentation available"
echo ""
print_info "Required Configuration:"
echo "   ✓ AWS credentials for Bedrock AI models"
echo "   ✓ OpenAI or Anthropic API key for MetaGPT agents"
echo "   ✓ E2B API key for live code execution (optional)"
echo ""
print_warning "Press Ctrl+C to stop both servers"
echo "=================================================="
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    print_info "Stopping development servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Wait for processes to terminate
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    print_status "Development servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend in background with development settings
print_status "Starting backend server (port 8000)..."
DEBUG=true LOG_LEVEL=DEBUG RELOAD_ON_CHANGE=true uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level debug \
    --reload-dir app \
    --reload-dir . \
    --reload-exclude "*.log" \
    --reload-exclude "node_modules/*" \
    --reload-exclude "venv/*" \
    --reload-exclude "dist/*" \
    --reload-exclude "workspace/*" &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend server failed to start"
    exit 1
fi

# Start frontend in background
print_status "Starting frontend server (port 3000)..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

print_status "Both servers started successfully!"
print_info "Backend PID: $BACKEND_PID"
print_info "Frontend PID: $FRONTEND_PID"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID