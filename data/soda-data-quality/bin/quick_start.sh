#!/bin/bash
# Quick start script for Refactored Data Quality App
# This script checks if venv exists and runs the refactored application

echo "🚀 Quick Start - Refactored Data Quality App"
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

# Activate virtual environment and run refactored app
echo
echo "🧪 Running refactored data quality checks..."
source venv/bin/activate
python src/app.py

echo
echo "🏁 Data quality checks completed!"

