@echo off
REM Run Soda Data Quality App with virtual environment
REM Windows batch script

echo Starting Soda Data Quality App
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup_venv.bat first to create the virtual environment
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

REM Run real data quality checks
echo Running real data quality checks...
python src\app.py

echo.
echo Application finished
