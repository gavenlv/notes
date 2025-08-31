@echo off
REM Run Real Data Quality Checks
REM This script runs data quality checks against real PostgreSQL and ClickHouse databases

echo ========================================
echo Real Data Quality Checks
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

REM Test database connections first
echo.
echo Testing database connections...
python src\test_connections.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Database connection test failed!
    echo Please ensure PostgreSQL and ClickHouse are running
    echo and check your configuration in config\environment.env
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i not "%continue%"=="y" (
        echo Aborting...
        pause
        exit /b 1
    )
)

REM Run real data quality checks
echo.
echo Running real data quality checks...
echo This will check PostgreSQL and ClickHouse databases
echo.
python src\app.py

echo.
echo ========================================
echo Data Quality Checks Completed
echo ========================================
echo Check the reports directory for detailed results

