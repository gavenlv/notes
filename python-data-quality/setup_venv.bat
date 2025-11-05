@echo off
REM Batch script to setup Python virtual environment for Data Quality Framework

echo ========================================
echo Python Data Quality Framework Setup
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully!

REM Install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully!

REM Setup environment file
echo Setting up environment configuration...
if not exist config\environment.env (
    if exist config\environment.env.example (
        copy config\environment.env.example config\environment.env >nul
        echo Created config/environment.env - Please edit with your database credentials
    )
)

echo.
echo ========================================
echo Setup Completed Successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config/environment.env with your database credentials
echo 2. Review config/rules.yml for your data quality rules
echo 3. Run data quality checks using run_checks.bat
echo.
echo To activate the virtual environment manually:
echo   venv\Scripts\activate.bat
echo.

pause