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

REM Check if we want to run demo or real app
if "%1"=="demo" (
    echo Running demo with mock data...
    python src\demo_with_mock_data.py
) else if "%1"=="test" (
    echo Testing database connections...
    python src\test_connections.py
) else if "%1"=="init" (
    echo Initializing all databases...
    python init\init_databases.py
) else if "%1"=="init-pg" (
    echo Initializing PostgreSQL database only...
    python init\init_postgresql_only.py
) else if "%1"=="app" (
    echo Running main application...
    python src\app.py
) else (
    echo Running real data quality checks...
    python src\app.py
)

echo.
echo Application finished
