import sys
import os

# Add the parent directory to Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# This is the entry point for Vercel serverless functions
# Vercel will look for this file to handle requests

# Export the app for Vercel
handler = app 