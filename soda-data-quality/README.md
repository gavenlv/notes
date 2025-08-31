# Soda Core Data Quality Startup App

A comprehensive data quality monitoring application built with **soda-core** for PostgreSQL and ClickHouse databases. This application demonstrates enterprise-grade data quality checks with secure environment variable management.

## 🚀 Features

- **Multi-Database Support**: PostgreSQL and ClickHouse data quality monitoring
- **Secure Configuration**: Environment variables for password protection
- **Comprehensive Checks**: 20+ built-in data quality validations
- **Real-time Monitoring**: Automated data quality scanning
- **Rich Reporting**: JSON reports with detailed check results
- **Mock Demo**: SQLite-based demo for testing without database setup
- **Production Ready**: Logging, error handling, and cleanup routines

## 📁 Project Structure

```
soda-data-quality/
├── src/                        # Source code directory
│   ├── app.py                  # Main application
│   ├── demo_with_mock_data.py  # Demo with SQLite mock data
│   └── test_connections.py     # Database connectivity test
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
│   └── run_app.sh              # Linux/macOS app runner script
├── reports/                    # Generated reports directory
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
chmod +x bin/setup_venv.sh bin/run_app.sh
./bin/setup_venv.sh
```

#### Option 2: Manual Setup

1. **Clone and navigate to the project:**
   ```bash
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
   CLICKHOUSE_PORT=8123
   CLICKHOUSE_DATABASE=default
   CLICKHOUSE_USERNAME=admin
   CLICKHOUSE_PASSWORD=admin
   ```

## 🗄️ Database Setup

### Option 1: Automatic Initialization

Run the initialization script to create sample databases:

```bash
python init_databases.py
```

This creates:
- **PostgreSQL**: `users` and `orders` tables with `active_users_view` and `recent_orders_view`
- **ClickHouse**: `events` and `user_sessions` tables with `daily_events_summary` and `user_activity_view`

### Database Initialization

#### Option 1: Using Python Scripts

```bash
# Initialize all databases
python init/init_databases.py

# Initialize PostgreSQL only
python init/init_postgresql_only.py
```

#### Option 2: Manual Setup

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

### Option 1: Quick Start (Recommended)

#### Windows
```batch
# Quick start - automatically checks venv and runs demo
bin\quick_start.bat
```

#### Linux/macOS
```bash
# Quick start - automatically checks venv and runs demo
chmod +x bin/quick_start.sh
./bin/quick_start.sh
```

### Option 2: Advanced Usage

#### Windows
```batch
# Run demo (no database required)
bin\run_app.bat demo

# Test database connections
bin\run_app.bat test

# Initialize all databases
bin\run_app.bat init

# Initialize PostgreSQL only
bin\run_app.bat init-pg

# Run main application
bin\run_app.bat app
```

#### Linux/macOS
```bash
# Run demo (no database required)
./bin/run_app.sh demo

# Test database connections
./bin/run_app.sh test

# Initialize all databases
./bin/run_app.sh init

# Initialize PostgreSQL only
./bin/run_app.sh init-pg

# Run main application
./bin/run_app.sh app
```

### Option 3: Manual Run (with Virtual Environment)

1. **Activate virtual environment:**
   ```bash
   # Windows:
   venv\Scripts\activate.bat
   
   # Linux/macOS:
   source venv/bin/activate
   ```

2. **Run with Real Databases:**
   ```bash
   # Test connections
   python src/test_connections.py
   
   # Run data quality checks
   python src/app.py
   ```

3. **Run Demo (No Database Required):**
   ```bash
   python src/demo_with_mock_data.py
   ```

This runs a complete demo using SQLite to simulate PostgreSQL data quality checks.

## 📊 Data Quality Checks

### PostgreSQL Checks

The application performs comprehensive checks on:

#### Users Table
- ✅ Table has data (row count > 0)
- ✅ Recent user registrations (freshness < 1 day)
- ✅ No duplicate emails
- ✅ Name is required (no missing values)
- ✅ Email is required (no missing values)
- ✅ Valid email format
- ✅ Valid user status (active/inactive/pending)
- ✅ No future registration dates

#### Orders Table
- ✅ Table has data (row count > 0)
- ✅ User ID is required
- ✅ Product name is required
- ✅ Valid order status
- ✅ Positive quantity values
- ✅ Non-negative prices
- ✅ Valid user references (referential integrity)

#### Views
- ✅ Active users view has data
- ✅ Recent orders view has data
- ✅ Calculated fields are correct

### ClickHouse Checks

#### Events Table
- ✅ Table has data (row count > 0)
- ✅ Recent event data (freshness < 2 hours)
- ✅ User ID is required
- ✅ Event name is required
- ✅ Valid event names (click, view, purchase, signup, login, page_view)
- ✅ Valid timestamps
- ✅ Valid user IDs (> 0)

#### User Sessions Table
- ✅ Table has data (row count > 0)
- ✅ Session ID is required
- ✅ User ID is required
- ✅ Valid session duration (0-86400 seconds)
- ✅ Valid page views (> 0)
- ✅ Valid session times (start < end)

#### Views
- ✅ Daily events summary has data
- ✅ User activity view has data
- ✅ Valid aggregations and calculations

## 📈 Report Output

### Sample Console Output

```
================================================================================
DATA QUALITY SCAN SUMMARY
================================================================================

POSTGRESQL:
  Status: ⚠️  ISSUES FOUND
  Checks Passed: 8
  Checks Failed: 2
  Checks Warned: 0

CLICKHOUSE:
  Status: ✅ HEALTHY
  Checks Passed: 12
  Checks Failed: 0
  Checks Warned: 1

OVERALL SUMMARY:
  Total Checks Passed: 20
  Total Checks Failed: 2
  Total Checks Warned: 1
  Overall Status: ⚠️  ATTENTION REQUIRED
================================================================================
```

### JSON Report

Reports are automatically saved in the `reports/` directory with detailed information:

```json
{
  "data_source": "postgresql",
  "timestamp": "2025-08-28T23:37:43.624762",
  "checks_passed": 8,
  "checks_failed": 2,
  "checks_warned": 0,
  "scan_result": 1
}
```

## 🔧 Configuration

### Soda Configuration (`config/configuration.yml`)

```yaml
data_source postgresql:
  type: postgres
  host: ${POSTGRES_HOST}
  port: ${POSTGRES_PORT}
  username: ${POSTGRES_USERNAME}
  password: ${POSTGRES_PASSWORD}
  database: ${POSTGRES_DATABASE}
  schema: public

data_source clickhouse:
  type: clickhouse
  host: ${CLICKHOUSE_HOST}
  port: ${CLICKHOUSE_PORT}
  username: ${CLICKHOUSE_USERNAME}
  password: ${CLICKHOUSE_PASSWORD}
  database: ${CLICKHOUSE_DATABASE}
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

## 🧪 Testing

The project includes multiple testing approaches:

1. **Connection Test**: `python src/test_connections.py`
2. **Mock Demo**: `python src/demo_with_mock_data.py`
3. **Full Application**: `python src/app.py`

## 📋 Dependencies

- `soda-core[postgres]==3.5.5` - Data quality framework
- `soda-core[clickhouse]==3.5.5` - ClickHouse support
- `python-dotenv==1.0.0` - Environment management
- `psycopg2-binary==2.9.10` - PostgreSQL adapter
- `clickhouse-driver==0.2.6` - ClickHouse adapter
- `pyyaml==6.0.1` - YAML configuration
- `pandas==2.1.0` - Data manipulation

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```
   ❌ PostgreSQL connection failed: could not connect to server
   ```
   - Verify database is running
   - Check host, port, and credentials in `environment.env`
   - Ensure firewall allows connections

2. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'soda'
   ```
   - Run: `pip install -r requirements.txt`

3. **Permission Denied**
   ```
   ❌ ClickHouse connection failed: Code: 516. admin: Not enough privileges
   ```
   - Verify username/password in `environment.env`
   - Check database user permissions

### Demo Mode

If you can't set up databases immediately, use the demo:

```bash
python demo_with_mock_data.py
```

This provides a complete working example using SQLite.

## 🔄 Exit Codes

- `0`: All checks passed
- `1`: Some checks failed or errors occurred
- `130`: Interrupted by user (Ctrl+C)

## 📝 Logs

Application logs are written to:
- Console output (INFO level)
- `data_quality.log` file (all levels)

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
