"""
FastAPI application — Vercel serverless entry point
"""
# Re-export the app from main.py so Vercel can find it
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

__all__ = ['app']

