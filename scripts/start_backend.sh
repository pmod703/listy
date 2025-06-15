#!/bin/bash

echo "🚀 Starting Real Estate Open Home Optimizer Backend..."
echo "📍 Activating Python virtual environment..."

# Activate virtual environment
source .venv/bin/activate

echo "✅ Virtual environment activated"
echo "🔧 Installing/updating dependencies..."

# Install dependencies
pip install flask flask-cors selenium playwright requests python-dotenv

echo "🌐 Installing Playwright browsers..."
playwright install firefox

echo "🚀 Starting Flask API server..."
python backend/api/integrated_api.py