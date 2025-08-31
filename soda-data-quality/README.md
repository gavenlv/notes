# Soda Core Data Quality Startup App

A comprehensive data quality monitoring application built with **soda-core** for PostgreSQL and ClickHouse databases. This application demonstrates enterprise-grade data quality checks with secure environment variable management.

## 🚀 Features

- **Multi-Database Support**: PostgreSQL and ClickHouse data quality monitoring
- **Secure Configuration**: Environment variables for password protection
- **Comprehensive Checks**: 20+ built-in data quality validations
- **Real-time Monitoring**: Automated data quality scanning
- **Rich Reporting**: JSON reports with detailed check results
- **Production Ready**: Logging, error handling, and cleanup routines

## 📁 Project Structure

```
soda-data-quality/
├── src/                        # Source code directory
│   ├── app.py                  # Main application
│   ├── test_connections.py     # Database connectivity test
│   └── clickhouse_checker.py   # Custom ClickHouse data quality checker
├── init/                       # Database initialization scripts
│   ├── init_databases.py       # Full database initialization script
│   ├── init_postgresql_only.py # PostgreSQL-only initialization
│   ├── init_postgresql.sql     # PostgreSQL schema and data
│   └── init_clickhouse.sql     # ClickHouse schema and data
├── config/                     # Configuration files
│   ├── environment.env         # Environment configuration
│   ├── configuration.yml       # Soda configuration
│   └── checks/                 # Data quality checks
│       ├── postgresql_checks.yml   # PostgreSQL data quality checks
│       └── clickhouse_checks.yml   # ClickHouse data quality checks
├── bin/                        # Executable scripts
│   ├── quick_start.bat         # Windows quick start script
│   ├── quick_start.sh          # Linux/macOS quick start script
│   ├── setup_venv.bat          # Windows venv setup script
│   ├── setup_venv.sh           # Linux/macOS venv setup script
│   ├── run_app.bat             # Windows app runner script
│   ├── run_app.sh              # Linux/macOS app runner script
│   ├── run_quality_checks.bat  # Windows script to run all quality checks
│   └── run_quality_checks.sh   # Linux/macOS script to run all quality checks
├── reports/                    # Generated reports directory
├── logs/                       # Application logs directory
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
└── venv/                       # Virtual environment (created by setup)
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (running on localhost:25011)
- ClickHouse (running on localhost:9000)

### Setup

#### Option 1: Quick Setup with Scripts

##### Windows
```batch
# Run the setup script
bin\setup_venv.bat
```

##### Linux/macOS
```bash
# Make scripts executable and run setup
chmod +x bin/setup_venv.sh bin/run_app.sh bin/run_quality_checks.sh
./bin/setup_venv.sh
```

#### Option 2: Manual Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository_url>
   cd soda-data-quality
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate.bat
   
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Update `config/environment.env` with your database credentials:
   ```env
   # PostgreSQL Configuration
   POSTGRES_HOST=localhost
   POSTGRES_PORT=25011
   POSTGRES_DATABASE=postgres
   POSTGRES_USERNAME=postgres
   POSTGRES_PASSWORD=root
   
   # ClickHouse Configuration
   CLICKHOUSE_HOST=localhost
   CLICKHOUSE_PORT=9000
   CLICKHOUSE_DATABASE=default
   CLICKHOUSE_USERNAME=admin
   CLICKHOUSE_PASSWORD=admin
   ```

## 🗄️ Database Setup

### Option 1: Automatic Initialization

Run the initialization script to create sample databases:

```bash
# Windows
bin\run_app.bat init
# Linux/macOS
./bin/run_app.sh init
```

This creates:
- **PostgreSQL**: `users` and `orders` tables
- **ClickHouse**: `events` table

### Option 2: Manual Setup

Execute the SQL scripts directly:

**PostgreSQL:**
```bash
psql -h localhost -p 25011 -U postgres -d postgres -f init/init_postgresql.sql
```

**ClickHouse:**
```bash
clickhouse-client --host localhost --port 9000 --user admin --password admin < init/init_clickhouse.sql
```

## 🚀 Usage

### Quick Start (Recommended)

#### Windows
```batch
bin\quick_start.bat
```

#### Linux/macOS
```bash
chmod +x bin/quick_start.sh
./bin/quick_start.sh
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

### Testing Database Connections

#### Windows
```batch
bin\run_app.bat test
```

#### Linux/macOS
```bash
./bin/run_app.sh test
```

### Manual Run (with Virtual Environment)

1. **Activate virtual environment:**
   ```bash
   # Windows:
   venv\Scripts\activate.bat
   
   # Linux/macOS:
   source venv/bin/activate
   ```

2. **Run Data Quality Checks:**
   ```bash
   python src/app.py
   ```

3. **Test Database Connections:**
   ```bash
   python src/test_connections.py
   ```

## 📊 Data Quality Checks Overview

### PostgreSQL Checks

The application performs comprehensive checks on the `users` and `orders` tables.

### ClickHouse Checks

The application performs comprehensive checks on the `events` table.

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
