#!/bin/bash

echo "🚀 Starting Clean Real Estate API (No Scraping)"
echo "================================================"
echo ""
echo "📝 Note: Scraping functionality has been removed"
echo "🤝 Ready for Domain API integration when available"
echo "🧪 Using realistic mock data for demonstration"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv311" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv311
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv311/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the clean API
echo ""
echo "🚀 Starting Clean API server..."
echo "📍 Server will be available at: http://localhost:5001"
echo "🔗 Health check: http://localhost:5001/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python clean_api.py