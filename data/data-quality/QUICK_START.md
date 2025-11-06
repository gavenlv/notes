# Quick Start Guide

This guide will help you get started with the Data Quality Framework v2.0 in minutes.

## Prerequisites

- Python 3.8 or higher
- ClickHouse database (or other supported databases)
- Git (optional)

## Step 1: Setup Virtual Environment

### Windows
```bash
# Run the setup script
setup_venv.bat

# Or manually:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-v2.txt
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-v2.txt
```

## Step 2: Configure Database Connection

Edit `configs/test-config.yml` to match your database settings:

```yaml
database:
  type: "clickhouse"
  host: "localhost"
  port: 8123
  database: "default"
  user: "admin"
  password: "admin"
  secure: false
  timeout: 60
```

## Step 3: Test Connection

```bash
python data_quality_runner.py --test-connection
```

Expected output:
```
Testing clickhouse database connection...
Host: localhost
Port: 8123
Database: default
✓ Database connection successful
```

## Step 4: Run Basic Test

```bash
python run_test.py
```

This will:
- Load the basic test scenario
- Execute connectivity and completeness checks
- Generate HTML, JSON, and text reports
- Display results in the console

## Step 5: View Results

Check the generated reports in the `reports/` directory:

- `data_quality_report_basic_test_YYYYMMDD_HHMMSS.html` - Interactive HTML report
- `data_quality_report_basic_test_YYYYMMDD_HHMMSS.json` - Machine-readable JSON
- `data_quality_report_basic_test_YYYYMMDD_HHMMSS.txt` - Console-friendly text

## Available Commands

### List Available Scenarios
```bash
python data_quality_runner.py --list-scenarios
```

### List Supported Databases
```bash
python data_quality_runner.py --list-databases
```

### Validate Configuration
```bash
python data_quality_runner.py --validate-config
```

### Run Specific Scenario
```bash
python data_quality_runner.py --scenario basic_test
```

### Debug Mode
```bash
python data_quality_runner.py --log-level DEBUG --scenario basic_test
```

## Next Steps

1. **Explore Scenarios**: Check the `scenarios/` directory for different test configurations
2. **Create Custom Rules**: Add your own rules in YAML format
3. **Add New Databases**: Extend support for additional database types
4. **Customize Reports**: Modify report templates and formats
5. **Integrate with CI/CD**: Use the framework in automated testing pipelines

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify ClickHouse is running
- Check connection parameters
- Confirm user permissions

**Rule Validation Errors**
- Check YAML syntax
- Verify required fields
- Review rule schema

**Template Rendering Issues**
- Check Jinja2 syntax
- Verify variable names
- Review SQL dialect

### Getting Help

1. Check the main README.md for detailed documentation
2. Review the troubleshooting section
3. Enable debug logging for detailed information
4. Check the examples in the `scenarios/` directory

## Example Output

Successful test run:
```
=== Data Quality Test Runner ===
ClickHouse connection information:
  Host: localhost
  Port: 8123
  User: admin
  Password: admin

Starting data quality scenario: basic_test
==================================================
[1/4] OK clickhouse_connection_test: PASS
[2/4] OK system_tables_access: PASS
[3/4] OK data_types_functions_test: PASS
[4/4] OK user_permissions_test: PASS

Execution completed!
==================================================
Execution summary:
  Scenario: basic_test
  Environment: default
  Status: COMPLETED
  Duration: 2.34 seconds
  Total rules: 4
  Passed rules: 4
  Failed rules: 0
  Error rules: 0
  Pass rate: 100%

✅ All data quality checks passed
✅ Test completed!
Report files generated in reports/ directory
```

