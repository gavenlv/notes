# Python Data Quality Framework

A self-developed data quality framework inspired by Soda and Great Expectations, but implemented from scratch with ClickHouse support.

## Features

- **Database Support**: ClickHouse with SSL support
- **Configuration**: YAML-based rule definitions
- **Security**: Environment variable management (.env files)
- **Flexibility**: Custom SQL checks for complex validations
- **Reporting**: Cucumber-style HTML reports
- **Dependency Management**: Python virtual environment

## Quick Start

1. Set up virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp config/environment.env.example config/environment.env
# Edit config/environment.env with your database credentials
```

4. Define data quality rules in YAML format
5. Run quality checks:
```bash
python src/main.py
```

## Project Structure

```
python-data-quality/
├── config/           # Configuration files
├── src/             # Source code
├── tests/           # Test files
├── reports/         # Generated reports
├── requirements.txt # Dependencies
└── README.md
```