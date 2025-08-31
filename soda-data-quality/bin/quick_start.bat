@echo off
REM Quick start script for Soda Data Quality App
REM This script checks if venv exists and runs the demo

echo Quick Start - Soda Data Quality App
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating one...
    echo.
    call setup_venv.bat
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment found
)

REM Activate virtual environment and run demo
echo.
echo Running real data quality checks...
call venv\Scripts\activate.bat
python src\app.py

echo.
echo Data quality checks completed!

