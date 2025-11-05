# Soda Core Data Quality Startup App

A comprehensive data quality monitoring application built with **soda-core** for PostgreSQL and ClickHouse databases. This application demonstrates enterprise-grade data quality checks with secure environment variable management.

## 📚 Comprehensive Documentation

For detailed information about the project, including installation, usage, refactoring details, and Superset integration, please refer to the [COMPREHENSIVE_DOCUMENTATION.md](COMPREHENSIVE_DOCUMENTATION.md) file.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (running on localhost:25011)
- ClickHouse (running on localhost:9000)

### Quick Setup

#### Windows
```batch
# Run the setup script
bin\setup_venv.bat
```

#### Linux/macOS
```bash
# Make scripts executable and run setup
chmod +x bin/setup_venv.sh bin/run_app.sh bin/run_quality_checks.sh
./bin/setup_venv.sh
```

### Running Data Quality Checks

#### Windows
```batch
bin\run_quality_checks.bat
```

#### Linux/macOS
```bash
chmod +x bin/run_quality_checks.sh
./bin/run_quality_checks.sh
```

## 📁 Project Structure

```
soda-data-quality/
├── src/                        # Source code directory
│   ├── core/                   # SOLID framework
│   │   ├── interfaces.py       # All interfaces
│   │   ├── configuration.py    # Configuration management
│   │   ├── logging.py          # Logging system
│   │   ├── file_manager.py     # File operations
│   │   ├── database_connections.py # Database abstractions
│   │   ├── mysql_connection.py      # MySQL connection implementation
│   │   ├── scan_coordinator.py # Scan coordination
│   │   └── factories.py        # Factory implementations
│   ├── checkers/               # Data quality checkers
│   │   ├── base_checker.py     # Base checker
│   │   ├── clickhouse_checker.py # ClickHouse checker
│   │   ├── mysql_checker.py   # MySQL-specific checks
│   │   └── soda_checker.py     # Soda Core checker
│   ├── reporters/              # Result reporters
│   │   ├── base_reporter.py    # Base reporter
│   │   ├── clickhouse_reporter.py # ClickHouse reporter
│   │   ├── mysql_reporter.py   # MySQL reporter
│   │   └── json_reporter.py    # JSON reporter
│   └── app.py                  # Main application
├── init/                       # Database initialization scripts
│   ├── init_databases.py       # Full database initialization script
│   ├── scripts/                # SQL scripts
│   │   ├── init_clickhouse.sql
│   │   └── init_postgresql.sql
│   ├── setup_clickhouse.py     # ClickHouse setup
│   └── verify_db.py            # Database verification
├── config/                     # Configuration files
│   ├── environment.env         # Environment configuration
│   ├── configuration.yml       # Soda configuration
│   └── checks/                 # Data quality checks
│       ├── postgresql_checks.yml   # PostgreSQL data quality checks
│       └── clickhouse_checks.yml   # ClickHouse data quality checks
├── bin/                        # Executable scripts
│   ├── *.bat                   # Windows scripts
│   ├── *.sh                    # Linux/macOS scripts
│   └── *.ps1                   # PowerShell scripts
├── reports/                    # Generated reports directory
├── logs/                       # Application logs directory
├── requirements.txt            # Python dependencies
├── COMPREHENSIVE_DOCUMENTATION.md # Complete project documentation
├── README.md                   # This documentation
└── venv/                       # Virtual environment (created by setup)
```

2. **Run Data Quality Checks:**
  ```bash
  python src/app.py
  ```

3. **Test Database Connections:**
  ```bash
  python src/test_connections.py
  ```

## Extending Database Support

The project is designed to easily support new database types without modifying existing code. See [EXTENDING_DATABASE_SUPPORT.md](EXTENDING_DATABASE_SUPPORT.md) for detailed instructions on how to add support for new databases.

## 📊 Data Quality Checks Overview

### PostgreSQL Checks

The application performs comprehensive checks on the `users` and `orders` tables.

### ClickHouse Checks

The application performs comprehensive checks on the `events` table.

### MySQL Checks

The application performs comprehensive checks on MySQL databases, providing an additional option for data quality monitoring.

## 📈 Report Output

Reports are automatically saved in the `reports/` directory with detailed JSON reports for each data source, and a summary is printed to the console.

## 🔧 Configuration

### Soda Configuration (`config/configuration.yml`)

```yaml
data_source postgresql:
  type: postgres
  host: localhost
  port: 25011
  username: postgres
  password: root
  database: postgres
  schema: public

data_source clickhouse:
  type: clickhouse
  host: localhost
  port: 9000
  username: admin
  password: admin
  database: default
```

### Custom Checks

Add custom checks in `config/checks/postgresql_checks.yml` or `config/checks/clickhouse_checks.yml`:

```yaml
checks for your_table:
  - row_count > 1000:
      name: Minimum data volume
  
  - failed rows:
      name: Custom business rule
      fail query: |
        SELECT * FROM your_table 
        WHERE your_condition_here
```

## 🛡️ Security Features

- **Environment Variables**: All sensitive credentials stored in environment files
- **No Hardcoded Passwords**: Secure configuration management
- **Connection Validation**: Pre-check database connectivity
- **Error Handling**: Graceful failure management
- **Logging**: Comprehensive audit trail

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify database is running
   - Check host, port, and credentials in `config/environment.env`
   - Ensure firewall allows connections

2. **Missing Dependencies**
   - Run: `pip install -r requirements.txt`

3. **Permission Denied**
   - Verify username/password in `config/environment.env`
   - Check database user permissions

4. **Permissions Issue (Linux/macOS)**
   - Give execution permission to scripts: `chmod +x bin/*.sh`

## 🔄 Exit Codes

- `0`: All checks passed
- `1`: Some checks failed or errors occurred
- `130`: Interrupted by user (Ctrl+C)

## 📝 Logs

Application logs are written to:
- Console output (INFO level)
- `logs/data_quality.log` and `logs/clickhouse_checker.log` files (all levels)

## 🚀 Production Deployment

For production use:

1. Set up proper database monitoring
2. Configure alerting based on exit codes
3. Schedule regular runs with cron/scheduler
4. Set up log rotation
5. Monitor report outputs
6. Configure Soda Cloud integration (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Soda Core for reliable data quality monitoring**
