"""
Vercel serverless function entry point
"""
import sys
import os

# Add parent directory to path so we can import from main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the FastAPI app for Vercel
handler = app
