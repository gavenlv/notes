# Quick Start Guide

This guide will help you get started with the Python Data Quality Framework quickly.

## Prerequisites

- Python 3.8 or higher
- ClickHouse database (optional for testing)

## Installation

### Option 1: Automated Setup (Recommended)

1. **Run the setup script:**
   ```bash
   python setup.py
   ```

2. **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Setup environment variables:**
   ```bash
   copy config\environment.env.example config\environment.env
   ```

2. **Edit the environment file** with your database credentials:
   ```bash
   # Edit config/environment.env
   CLICKHOUSE_HOST=your_clickhouse_host
   CLICKHOUSE_PORT=9440
   CLICKHOUSE_USER=your_username
   CLICKHOUSE_PASSWORD=your_password
   CLICKHOUSE_DATABASE=your_database
   ```

3. **Review and customize rules** in `config/rules.yml`:
   ```yaml
   rules:
     my_table_check:
       description: "Check my table completeness"
       type: "completeness"
       table: "my_table"
       expected_rows: 1000
       tolerance: 0.1
       enabled: true
   ```

## Running Data Quality Checks

### Basic Usage

```bash
# Run all checks with default configuration
python src/main.py

# Run specific rules only
python src/main.py --rules table_row_count_check user_email_accuracy

# Validate configuration without running checks
python src/main.py --validate-only

# Generate JSON report only
python src/main.py --format json
```

### Advanced Usage

```bash
# Verbose output for debugging
python src/main.py --verbose

# Custom configuration directory
python src/main.py --config-dir my_config --rules-file custom_rules.yml

# Run in parallel mode (default)
python src/main.py --parallel

# Run sequentially
python src/main.py --no-parallel
```

## Example Rules

### Completeness Check
```yaml
rules:
  user_table_completeness:
    description: "Check if users table has expected number of rows"
    type: "completeness"
    table: "users"
    expected_rows: 10000
    tolerance: 0.1  # 10% tolerance
    enabled: true
```

### Accuracy Check
```yaml
rules:
  email_accuracy:
    description: "Check email accuracy in users table"
    type: "accuracy"
    table: "users"
    column: "email"
    threshold: 95.0  # Minimum 95% accuracy
    enabled: true
```

### Custom SQL Check
```yaml
rules:
  revenue_consistency:
    description: "Check revenue consistency"
    type: "custom_sql"
    custom_sql: |
      SELECT 
        DATE(created_at) as date,
        SUM(amount) as daily_revenue
      FROM orders 
      WHERE created_at >= today() - 30
      GROUP BY DATE(created_at)
    expected_result: 30  # Expect 30 days of data
    enabled: true
```

## SSL Configuration

For secure connections, configure SSL in your environment file:

```bash
CLICKHOUSE_SSL_ENABLED=true
CLICKHOUSE_SSL_VERIFY=true
CLICKHOUSE_SSL_CA_CERT=/path/to/ca.pem
CLICKHOUSE_SSL_CERT=/path/to/client.crt
CLICKHOUSE_SSL_KEY=/path/to/client.key
```

## Report Generation

After running checks, reports are generated in the `reports/` directory:

- **HTML Report**: Interactive cucumber-style report with visualizations
- **JSON Report**: Machine-readable format for integration with other tools

### Viewing Reports

1. **HTML Report**: Open `reports/data_quality_report_YYYYMMDD_HHMMSS.html` in your browser
2. **JSON Report**: Use for programmatic analysis or integration

## Testing

Run the test suite to verify your installation:

```bash
python -m pytest tests/ -v
```

Or use the setup script to run tests:

```bash
python setup.py --test
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify database credentials in `config/environment.env`
   - Check network connectivity to your ClickHouse server
   - Ensure SSL certificates are properly configured if using SSL

2. **Rule Execution Errors**
   - Check that tables and columns exist in your database
   - Verify SQL syntax in custom rules
   - Review rule configuration in `config/rules.yml`

3. **Virtual Environment Issues**
   - Ensure virtual environment is activated
   - Re-run `pip install -r requirements.txt` if packages are missing

### Debug Mode

Enable verbose logging for detailed debugging:

```bash
python src/main.py --verbose
```

## Next Steps

- Customize rules in `config/rules.yml` for your specific data quality requirements
- Integrate with your CI/CD pipeline using the JSON report format
- Extend the framework by adding custom rule types
- Configure alerts and notifications for failed checks

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the comprehensive documentation in `README.md`
- Examine generated logs in `data_quality.log`

---

**Happy data quality checking!** 🚀