@echo off
REM Setup virtual environment for Soda Data Quality App
REM Windows batch script

echo 🚀 Setting up Python Virtual Environment for Soda Data Quality App
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Remove existing venv if it exists
if exist venv (
    echo 🗑️  Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Virtual environment setup complete!
echo.
echo 🎯 To activate the environment manually, run:
echo    venv\Scripts\activate.bat
echo.
echo 🚀 To run the application:
echo    call venv\Scripts\activate.bat
echo    python app.py
echo.
echo 🧪 To run the demo:
echo    call venv\Scripts\activate.bat
echo    python demo_with_mock_data.py
echo.
pause
