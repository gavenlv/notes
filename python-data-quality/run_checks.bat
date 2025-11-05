@echo off
REM Batch script to run Data Quality Framework checks

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the data quality framework
python src/main.py %*

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Data quality checks completed with errors
    echo Check the logs for more details
    pause
) else (
    echo.
    echo Data quality checks completed successfully!
)