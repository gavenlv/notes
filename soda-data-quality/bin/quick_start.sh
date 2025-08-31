#!/bin/bash
# Quick start script for Soda Data Quality App
# This script checks if venv exists and runs the demo

echo "🚀 Quick Start - Soda Data Quality App"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    echo
    ./setup_venv.sh
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment and run demo
echo
echo "🧪 Running demo with mock data..."
source venv/bin/activate
python src/demo_with_mock_data.py

echo
echo "🏁 Demo completed!"

