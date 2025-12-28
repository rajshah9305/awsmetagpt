#!/bin/bash

# MetaGPT + E2B Integration System - Production Startup Script
# Enhanced with comprehensive validation and monitoring

set -e  # Exit on any error

echo "🚀 Starting MetaGPT + E2B Integration System (Production Mode)"
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

# Check Node.js version (for frontend build)
if command -v node &> /dev/null; then
    node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 16 ]; then
        print_warning "Node.js 16+ recommended. Found: v$node_version"
    else
        print_status "Node.js version: v$node_version"
    fi
else
    print_warning "Node.js not found - frontend build may not work"
fi

# Check available memory
if command -v free &> /dev/null; then
    available_memory=$(free -m | awk 'NR==2{printf "%.1f", $7/1024}')
    print_info "Available memory: ${available_memory}GB"
fi

# Check disk space
available_space=$(df -h . | awk 'NR==2 {print $4}')
print_info "Available disk space: $available_space"

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

# Create necessary directories
print_info "Setting up directories..."
mkdir -p workspace
mkdir -p logs
mkdir -p temp

# Check environment configuration
print_info "Validating configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning "Creating .env file from template..."
        cp .env.example .env
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

# Run system validation
print_info "Running system validation..."
if python3 validate_system.py; then
    print_status "System validation passed"
else
    print_error "System validation failed"
    print_warning "Run 'python3 validate_system.py --report' for detailed report"
    
    # Ask user if they want to continue anyway
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build frontend if Node.js is available and package.json exists
if command -v node &> /dev/null && [ -f "package.json" ]; then
    print_info "Installing Node.js dependencies..."
    npm ci --production=false --silent
    
    print_info "Building frontend for production..."
    npm run build
    
    # Verify build
    if [ ! -d "dist" ]; then
        print_error "Frontend build failed - dist directory not found"
        exit 1
    fi
    print_status "Frontend build completed"
else
    print_warning "Skipping frontend build (Node.js or package.json not available)"
fi

# Set production environment variables
export DEBUG=false
export LOG_LEVEL=INFO
export RELOAD_ON_CHANGE=false

# Display startup information
echo ""
echo "=================================================="
print_info "Production server configuration:"
echo "🌐 Application: http://localhost:8000"
echo "📚 API Documentation: Contact administrator"
echo "🔧 Health Check: http://localhost:8000/api/v1/health"
echo "📊 System Status: http://localhost:8000/api/v1/system/status"
echo ""
print_info "Required Configuration:"
echo "   ✓ AWS credentials for Bedrock AI models"
echo "   ✓ OpenAI or Anthropic API key for MetaGPT agents"
echo "   ✓ E2B API key for live code execution"
echo ""
print_info "Features enabled:"
echo "   🤖 MetaGPT multi-agent generation"
echo "   🏗️ E2B sandbox code execution"
echo "   🔄 Real-time WebSocket updates"
echo "   📈 System monitoring and metrics"
echo ""
print_warning "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Start production server with enhanced configuration
print_status "Starting production server..."

# Use gunicorn for production if available, otherwise uvicorn
if command -v gunicorn &> /dev/null; then
    print_info "Using Gunicorn WSGI server"
    exec gunicorn main:app \
        --bind 0.0.0.0:8000 \
        --workers 1 \
        --worker-class uvicorn.workers.UvicornWorker \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info \
        --timeout 300 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100
else
    print_info "Using Uvicorn ASGI server"
    exec python3 main.py
fi