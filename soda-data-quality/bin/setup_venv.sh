#!/bin/bash
# Setup virtual environment for Soda Data Quality App
# Linux/macOS shell script

echo "🚀 Setting up Python Virtual Environment for Soda Data Quality App"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and add it to PATH"
    exit 1
fi

echo "✅ Python found"
python3 --version

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "📂 Virtual environment already exists."
    echo "🔄 Updating dependencies..."
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install dependencies
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
else
    # Create virtual environment
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install dependencies
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
fi

echo
echo "✅ Virtual environment setup complete!"
echo
echo "🎯 To activate the environment manually, run:"
echo "   source venv/bin/activate"
echo
echo "🚀 To run the application:"
echo "   source venv/bin/activate"
echo "   python src/app.py"
echo
