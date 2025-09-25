#!/bin/bash

# WeatherBot Deployment Setup Script
# This script helps you set up and deploy your WeatherBot application

set -e

echo "🌤️  WeatherBot Deployment Setup"
echo "================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: This is not a git repository. Please run 'git init' first."
    exit 1
fi

# Check if environment template exists
if [ ! -f "env.template" ]; then
    echo "❌ Error: env.template file not found."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists git; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

# Setup environment variables
echo "🔧 Setting up environment variables..."

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - OPENWEATHER_API_KEY" 
    echo "   - GROQ_API_KEY"
    echo ""
    read -p "Press Enter after you've updated .env file..."
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing dependencies..."

echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Installing backend dependencies..."
cd backend
python3 -m pip install -r requirements.txt
cd ..

echo "✅ Dependencies installed!"
echo ""

# Test local setup
echo "🧪 Testing local setup..."

echo "Testing backend..."
cd backend
python3 -c "import fastapi; print('FastAPI imported successfully')"
cd ..

echo "Testing frontend..."
cd frontend
npm run build > /dev/null 2>&1
echo "✅ Frontend builds successfully"
cd ..

echo "✅ Local setup test passed!"
echo ""

# Git setup
echo "📚 Setting up Git repository..."

# Add all files
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No new changes to commit"
else
    echo "📝 Committing deployment configuration..."
    git commit -m "feat: add deployment configuration and GitHub workflows"
fi

echo "✅ Git repository updated!"
echo ""

# Deployment options
echo "🚀 Deployment Options:"
echo ""
echo "1. 🌟 Quick Deploy (Recommended)"
echo "   - Frontend: Vercel"
echo "   - Backend: Railway"
echo "   - GitHub Actions: Automated"
echo ""
echo "2. 🔧 Manual Deploy"
echo "   - Choose your own platforms"
echo "   - Custom configuration"
echo ""
echo "3. 🐳 Docker Deploy"
echo "   - Self-hosted with Docker"
echo "   - Full control"
echo ""

read -p "Choose deployment option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🌟 Quick Deploy Setup"
        echo "===================="
        echo ""
        echo "Follow these steps:"
        echo ""
        echo "1. 📤 Push to GitHub:"
        echo "   git push origin main"
        echo ""
        echo "2. 🚂 Deploy Backend to Railway:"
        echo "   - Visit: https://railway.app"
        echo "   - Connect your GitHub repository"
        echo "   - Add environment variables from .env"
        echo "   - Copy the Railway URL"
        echo ""
        echo "3. ⚡ Deploy Frontend to Vercel:"
        echo "   - Visit: https://vercel.com"
        echo "   - Import your GitHub repository"
        echo "   - Set REACT_APP_API_URL to your Railway URL"
        echo "   - Deploy!"
        echo ""
        echo "4. 🔐 Setup GitHub Secrets:"
        echo "   - Add VERCEL_TOKEN and RAILWAY_TOKEN"
        echo "   - Enable automatic deployments"
        echo ""
        echo "📖 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
        ;;
    2)
        echo ""
        echo "🔧 Manual Deploy"
        echo "==============="
        echo ""
        echo "Available configurations:"
        echo "- frontend/vercel.json (Vercel)"
        echo "- frontend/netlify.toml (Netlify)"
        echo "- backend/railway.json (Railway)"
        echo "- backend/render.yaml (Render)"
        echo ""
        echo "📖 See DEPLOYMENT_GUIDE.md for platform-specific instructions"
        ;;
    3)
        echo ""
        echo "🐳 Docker Deploy"
        echo "==============="
        echo ""
        echo "Run locally with Docker:"
        echo "docker-compose up --build"
        echo ""
        echo "For production:"
        echo "docker-compose --profile production up --build"
        echo ""
        echo "📖 See DEPLOYMENT_GUIDE.md for cloud provider instructions"
        ;;
    *)
        echo "❌ Invalid option. Please run the script again and choose 1-3."
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. 📖 Read DEPLOYMENT_GUIDE.md for detailed instructions"
echo "2. 🔑 Make sure your API keys are valid"
echo "3. 🚀 Deploy and enjoy your WeatherBot!"
echo ""
echo "Need help? Check the troubleshooting section in DEPLOYMENT_GUIDE.md" 