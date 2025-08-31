#!/bin/bash
# Run Real Data Quality Checks
# This script runs data quality checks against real PostgreSQL and ClickHouse databases

echo "========================================"
echo "Real Data Quality Checks"
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

# Test database connections first
echo
echo "Testing database connections..."
python src/test_connections.py
if [ $? -ne 0 ]; then
    echo
    echo "WARNING: Database connection test failed!"
    echo "Please ensure PostgreSQL and ClickHouse are running"
    echo "and check your configuration in config/environment.env"
    echo
    read -p "Continue anyway? (y/N): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        echo "Aborting..."
        exit 1
    fi
fi

# Run real data quality checks
echo
echo "Running real data quality checks..."
echo "This will check PostgreSQL and ClickHouse databases"
echo
python src/app.py

echo
echo "========================================"
echo "Data Quality Checks Completed"
echo "========================================"
echo "Check the reports directory for detailed results"
echo
