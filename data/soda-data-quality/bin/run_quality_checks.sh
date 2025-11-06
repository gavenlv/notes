#!/bin/bash
# Run Refactored Data Quality Checks
# This script runs data quality checks using the new SOLID architecture

echo "========================================"
echo "Refactored Data Quality Checks"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run setup_venv.sh first to create the virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Run refactored data quality checks
echo
echo "Running refactored data quality checks..."
echo "This will check PostgreSQL and ClickHouse databases using SOLID architecture"
echo
python src/app.py

echo
echo "========================================"
echo "Data Quality Checks Completed"
echo "========================================"
echo "Check the reports directory for detailed results"
echo "Check ClickHouse database for stored results"
echo
