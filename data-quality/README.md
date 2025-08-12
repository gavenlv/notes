# Data Quality Framework v2.0

A comprehensive, modular data quality testing framework that supports multiple databases, scenarios, and generates automated testing-style reports.

## Features

- **Multi-Database Support**: ClickHouse, MySQL, PostgreSQL, SQL Server
- **Multi-Scenario Applications**: Different testing contexts and environments
- **Rule Isolation**: Separate rules, SQL queries, and templates
- **Automated Reports**: HTML, JSON, and text format reports
- **Parallel Execution**: Multi-threaded rule execution
- **Configuration Management**: Environment and scenario isolation
- **Virtual Environment**: Python virtual environment support

## Quick Start

### 1. Setup Virtual Environment

```bash
# Windows
setup_venv.bat

# Or manually:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-v2.txt
```

### 2. Run Basic Test

```bash
python run_test.py
```

### 3. Available Commands

```bash
# List available scenarios
python data_quality_runner.py --list-scenarios

# List supported databases
python data_quality_runner.py --list-databases

# Test database connection
python data_quality_runner.py --test-connection

# Validate configuration
python data_quality_runner.py --validate-config

# Run specific scenario
python data_quality_runner.py --scenario basic_test
```

## Project Structure

```
data-quality/
├── core/                           # Core framework modules
│   ├── engine.py                   # Main execution engine
│   ├── rule_engine.py              # Rule loading and validation
│   ├── template_engine.py          # SQL template rendering
│   ├── database_adapters.py        # Database connection adapters
│   ├── config_manager.py           # Configuration management
│   └── report_generator.py         # Report generation
├── configs/                        # Configuration files
│   ├── test-config.yml            # Test configuration
│   └── data-quality-config-v2.yml # Main configuration
├── scenarios/                      # Test scenarios
│   ├── basic_test.yml             # Basic test scenario
│   └── basic_test/                # Scenario-specific rules
├── templates/                      # SQL templates
├── reports/                        # Generated reports
├── requirements-v2.txt             # Python dependencies
├── setup_venv.bat                  # Virtual environment setup
├── data_quality_runner.py          # Main runner script
└── run_test.py                     # Simple test runner
```

## Configuration

### Database Configuration

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

### Rule Configuration

```yaml
rules:
  paths:
    - "rules/"
    - "scenarios/"
  cache_enabled: true
  validation_strict: false
```

### Execution Configuration

```yaml
execution:
  max_parallel_jobs: 3
  timeout: 300
  fail_fast: false
  retry_failed: false
```

## Rule Definition

Rules are defined in YAML format with the following structure:

```yaml
- rule_type: "connectivity"
  version: "1.0"
  description: "Database connection test"
  scenarios: ["basic_test", "connectivity", "all"]
  
  rule:
    name: "connection_test"
    description: "Test database connection"
    category: "connectivity"
    priority: "high"
    enabled: true
    
    target:
      database: "default"
      table: "system.databases"
      
    template: |
      SELECT
        'connection_test' as test_name,
        count(*) as database_count,
        version() as version,
        'PASS' as check_result
      FROM system.databases
```

## Supported Rule Types

- **connectivity**: Database connection and system access tests
- **completeness**: Data completeness and null value checks
- **accuracy**: Data accuracy and validation checks
- **consistency**: Data consistency and integrity checks
- **timeliness**: Data freshness and latency checks
- **referential_integrity**: Foreign key validation between tables
- **uniqueness**: Single column or composite uniqueness checks
- **custom**: Fully customizable rules with your own SQL logic

## Database Support

### ClickHouse
- HTTP interface support
- Native driver support
- System table queries
- Function testing

### MySQL
- PyMySQL driver
- Connection pooling
- Transaction support

### PostgreSQL
- psycopg2 driver
- Advanced data types
- JSON support

### SQL Server
- pyodbc driver
- Windows authentication
- Stored procedure support

## Report Generation

The framework generates comprehensive reports in multiple formats:

### HTML Reports
- Modern, responsive design
- Interactive charts and graphs
- Detailed rule execution results
- Sample data display
- Export functionality

### JSON Reports
- Machine-readable format
- API integration support
- Detailed metadata

### Text Reports
- Console-friendly format
- Summary statistics
- Error details

## Development

### Adding New Database Support

1. Create adapter in `core/database_adapters.py`
2. Add requirements to `requirements-v2.txt`
3. Update `DatabaseAdapterFactory`
4. Add test scenarios

### Adding New Rule Types

1. Define schema in `core/rule_engine.py`
2. Add validation logic
3. Create template examples
4. Update documentation

### Creating Custom Rules

1. Create YAML rule file in `examples/` directory
2. Define rule structure with appropriate type
3. Write SQL template with required output columns
4. Add to configuration and run tests

See `examples/CUSTOM_RULES_GUIDE.md` for detailed instructions and examples.

### Adding New Scenarios

1. Create scenario YAML file
2. Define rules directory
3. Add scenario configuration
4. Test with sample data

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check connection parameters
   - Verify network connectivity
   - Confirm user permissions

2. **Rule Validation Errors**
   - Check YAML syntax
   - Verify required fields
   - Review rule schema

3. **Template Rendering Issues**
   - Check Jinja2 syntax
   - Verify variable names
   - Review SQL dialect

### Debug Mode

Enable debug logging for detailed information:

```bash
python data_quality_runner.py --log-level DEBUG --scenario basic_test
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues
3. Create new issue with detailed information
4. Include configuration and error logs 