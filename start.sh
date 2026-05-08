#!/bin/bash
set -e

echo "🚀 ApexAI Startup Script"
echo "======================="

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo "To use live AI features, run:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY"
    echo "Continuing in DEMO mode..."
    sleep 2
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Navigate to backend
cd backend

# Start server
echo ""
echo "🎯 Starting ApexAI Server..."
echo "📡 Backend: http://localhost:8000"
echo "💻 Frontend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo "======================="
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
