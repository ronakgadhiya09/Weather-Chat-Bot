#!/bin/bash

# Quick fix for Python environment issue
echo "🐍 Fixing Python Environment Setup"
echo "=================================="

cd backend

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "📥 Installing dependencies in virtual environment..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python environment setup complete!"
echo ""
echo "To use the backend:"
echo "1. cd backend"
echo "2. source venv/bin/activate"
echo "3. python app/main.py"
echo ""
echo "Virtual environment created at: backend/venv/"

deactivate 