@echo off
REM Run Refactored Data Quality Checks
REM This script runs data quality checks using the new SOLID architecture

echo ========================================
echo Refactored Data Quality Checks
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup_venv.bat first to create the virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Run refactored data quality checks
echo.
echo Running refactored data quality checks...
echo This will check PostgreSQL and ClickHouse databases using SOLID architecture
echo.
python src\app.py

echo.
echo ========================================
echo Data Quality Checks Completed
echo ========================================
echo Check the reports directory for detailed results
echo Check ClickHouse database for stored results

