# Soda Core Data Quality Startup App - Comprehensive Documentation

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
│   ├── core/                   # SOLID framework
│   │   ├── interfaces.py       # All interfaces
│   │   ├── configuration.py    # Configuration management
│   │   ├── logging.py          # Logging system
│   │   ├── file_manager.py     # File operations
│   │   ├── database_connections.py # Database abstractions
│   │   ├── scan_coordinator.py # Scan coordination
│   │   └── factories.py        # Factory implementations
│   ├── checkers/               # Data quality checkers
│   │   ├── base_checker.py     # Base checker
│   │   ├── clickhouse_checker.py # ClickHouse checker
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
├── README.md                   # This documentation
└── venv/                       # Virtual environment (created by setup)
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (running on localhost:25011)
- ClickHouse (running on localhost:9000)
- MySQL (running on localhost:3306)

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

# ClickHouse DQ SSL Configuration (set to true to enable SSL)
CLICKHOUSE_DQ_SSL=false
CLICKHOUSE_DQ_SSL_VERIFY=true
# Optional SSL certificates (leave empty for system defaults)
CLICKHOUSE_DQ_SSL_CERT=
CLICKHOUSE_DQ_SSL_KEY=
CLICKHOUSE_DQ_SSL_CA=

# ClickHouse SSL Configuration (set to true to enable SSL)
CLICKHOUSE_SSL=false
CLICKHOUSE_SSL_VERIFY=true
# Optional SSL certificates (leave empty for system defaults)
CLICKHOUSE_SSL_CERT=
CLICKHOUSE_SSL_KEY=
CLICKHOUSE_SSL_CA=

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=data_quality
MYSQL_USERNAME=user
MYSQL_PASSWORD=password
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

**MySQL:**
```bash
mysql -h localhost -P 3306 -u user -p data_quality < init/init_mysql.sql
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

2. **Run the application:**
   ```bash
   python src/app.py
   ```

## 🧹 Cleanup Summary

### ✅ Files Removed

#### Unused Python Classes
- `src/app.py` - Original monolithic application class (Note: This file was refactored, not removed)
- `src/clickhouse_checker.py` - Original ClickHouse checker (replaced by refactored version)
- `src/clickhouse_reporter.py` - Original ClickHouse reporter (replaced by refactored version)
- `src/test_connections.py` - Standalone connection test script

#### Unused Initialization Scripts
- `init/init_databases.py` - Original database initialization script
- `init/init_postgresql_only.py` - PostgreSQL-only initialization script
- `init/setup_clickhouse.py` - Original ClickHouse setup script
- `init/verify_db.py` - Original database verification script
- `init/check_schema.py` - Schema checking script

### 🔄 Files Updated

#### Batch Scripts (.bat)
- `bin/run_quality_checks.bat` - Updated to use refactored app
- `bin/run_app.bat` - Updated to use refactored app
- `bin/quick_start.bat` - Updated to use refactored app

#### Shell Scripts (.sh)
- `bin/run_quality_checks.sh` - Updated to use refactored app
- `bin/quick_start.sh` - Updated to use refactored app

#### PowerShell Scripts (.ps1)
- `bin/setup_clickhouse.ps1` - Deprecated in favor of Python setup script

### 🆕 New Refactored Files

#### Core Application
- `src/app.py` - New main application entry point (refactored)

#### Initialization Scripts
- `init/init_databases_refactored.py` - Refactored database initialization
- `init/setup_clickhouse_refactored.py` - Refactored ClickHouse setup
- `init/verify_db_refactored.py` - Refactored database verification

### Data Quality Checks Overview

The application supports data quality checks on multiple databases:

- **PostgreSQL**: Primary database for user and order data
- **ClickHouse**: Analytics database for event data
- **MySQL**: Additional database support for flexible deployment

Results can be stored in:

- **JSON files**: Local file storage
- **ClickHouse database**: Centralized analytics storage
- **MySQL database**: Alternative centralized storage

## 🧪 Testing Results

### ✅ Successful Tests
- **Refactored Application**: `python src/app.py` ✅
- **ClickHouse Setup**: `python init/setup_clickhouse_refactored.py` ✅
- **Database Verification**: `python init/verify_db_refactored.py` ✅
- **All Scripts Updated**: All .bat and .sh scripts now use refactored app ✅

### 🔧 Functionality Preserved
- ✅ Data quality checks on PostgreSQL and ClickHouse
- ✅ Results stored in both JSON files and ClickHouse database
- ✅ Same configuration and environment variables
- ✅ Same output formats and reporting
- ✅ All original functionality maintained

## 🚀 Benefits Achieved

### Code Quality
- **Clean Architecture**: Removed all unused/duplicate code
- **SOLID Principles**: All classes follow SOLID principles
- **Single Responsibility**: Each class has one clear purpose
- **Dependency Injection**: Clean dependency management

### Maintainability
- **No Duplication**: Eliminated duplicate classes and scripts
- **Consistent Structure**: All scripts use the same refactored architecture
- **Easy Updates**: Changes only need to be made in one place
- **Clear Separation**: Core, checkers, and reporters are clearly separated

### Extensibility
- **Easy to Add**: New checkers and reporters can be added easily
- **Factory Pattern**: New components can be added through factories
- **Interface-Based**: All components use interfaces for flexibility

## 📋 Usage Instructions

### Running the Application
```bash
# Direct execution
python src/app.py

# Using batch scripts (Windows)
bin\run_quality_checks.bat
bin\run_app.bat
bin\quick_start.bat

# Using shell scripts (Linux/Mac)
./bin/run_quality_checks.sh
./bin/quick_start.sh
```

### Setup and Verification
```bash
# Setup ClickHouse tables
python init/setup_clickhouse_refactored.py

# Verify database setup
python init/verify_db_refactored.py

# Initialize databases
python init/init_databases_refactored.py
```

## 🎯 Summary

The cleanup process successfully:

1. **Removed** all unused and duplicate Python classes
2. **Updated** all batch and shell scripts to use the refactored architecture
3. **Created** new refactored versions of initialization scripts
4. **Maintained** all original functionality
5. **Improved** code quality and maintainability
6. **Applied** SOLID principles throughout the codebase

The project is now clean, maintainable, and follows modern software engineering best practices while preserving all original functionality.

---

**The cleanup is complete! The project now has a clean, SOLID-compliant architecture with no unused code.**

## ✅ SOLID Refactoring Summary

### 1. **Single Responsibility Principle (SRP)**
- ✅ Separated configuration management into `EnvironmentConfigurationManager`
- ✅ Isolated logging functionality in `StandardLogger`
- ✅ Created dedicated file management in `StandardFileManager`
- ✅ Separated database connections into specific classes
- ✅ Split checkers and reporters into focused components

### 2. **Open/Closed Principle (OCP)**
- ✅ Created extensible base classes for checkers and reporters
- ✅ Implemented factory pattern for easy extension
- ✅ Made system open for extension, closed for modification

### 3. **Liskov Substitution Principle (LSP)**
- ✅ All implementations properly substitute their base types
- ✅ Interface compliance ensures interchangeability
- ✅ Consistent behavior across all implementations

### 4. **Interface Segregation Principle (ISP)**
- ✅ Created focused interfaces (`IDataQualityChecker`, `IDataQualityReporter`, etc.)
- ✅ No fat interfaces - each contains only needed methods
- ✅ Clients depend only on methods they use

### 5. **Dependency Inversion Principle (DIP)**
- ✅ High-level modules depend on abstractions
- ✅ Dependency injection throughout the system
- ✅ Factory pattern provides concrete implementations

### 6. **Design Patterns Implementation**
- ✅ **Factory Pattern**: `DataQualityApplicationFactory`, `DatabaseConnectionFactory`
- ✅ **Strategy Pattern**: Different checkers and reporters
- ✅ **Observer Pattern**: Multiple reporters for scan results
- ✅ **Template Method Pattern**: Base classes with common algorithms

## 🚀 Key Improvements

### **Maintainability**
- Each class has a single, well-defined responsibility
- Changes to one component don't affect others
- Easy to locate and fix bugs

### **Testability**
- Dependencies can be easily mocked
- Each component can be tested in isolation
- Clear interfaces make testing straightforward

### **Extensibility**
- New checkers can be added without modifying existing code
- New reporters can be added without modifying existing code
- New database types can be supported easily

### **Reusability**
- Components can be reused in different contexts
- Interfaces allow for different implementations
- Factory pattern enables easy configuration

## 🧪 Testing Results

The refactored application successfully:
- ✅ Connects to both PostgreSQL and ClickHouse databases
- ✅ Runs data quality checks using both custom and Soda Core checkers
- ✅ Reports results to both JSON files and ClickHouse database
- ✅ Maintains the same functionality as the original application
- ✅ Provides better error handling and logging
- ✅ Follows all SOLID principles

## 📊 Performance

The refactored application maintains similar performance to the original while providing:
- Better separation of concerns
- Improved error handling
- More flexible configuration
- Cleaner architecture

## 📚 Documentation

- `SOLID_REFACTORING.md`: Comprehensive documentation of the refactoring
- `compare_versions.py`: Script to compare original vs refactored versions
- `REFACTORING_SUMMARY.md`: This summary document

## 🎯 Benefits Achieved

1. **Clean Architecture**: Clear separation of concerns
2. **SOLID Compliance**: All five principles properly implemented
3. **Design Patterns**: Factory, Strategy, and Observer patterns
4. **Maintainability**: Easy to modify and extend
5. **Testability**: Components can be tested in isolation
6. **Flexibility**: Easy to add new features
7. **Reusability**: Components can be reused across projects

## 🔄 Migration Path

The refactored application is a drop-in replacement for the original:
- Same configuration files
- Same environment variables
- Same output formats
- Same functionality
- Better architecture

## 🚀 Future Enhancements

With the SOLID architecture in place, future enhancements can include:
- Additional database support
- New reporting formats (email, Slack, etc.)
- Advanced scheduling capabilities
- Real-time monitoring
- Custom check types
- Performance optimizations

---

**The refactoring successfully transforms the soda-data-quality project into a clean, maintainable, and extensible system that follows SOLID principles and modern software design patterns.**

## 📊 Data Quality Dashboard with Apache Superset

This guide explains how to connect Apache Superset to your ClickHouse data quality metrics and create insightful dashboards.

### Prerequisites

1. Apache Superset installed and running
2. ClickHouse database with data quality metrics (tables created using `sql/clickhouse_dq_schema.sql`)
3. Network connectivity between Superset and ClickHouse

### Connecting ClickHouse to Superset

1. In Superset, go to **Data** → **Databases** → **+ Database**
2. Select "ClickHouse" as the database type
3. Configure the connection:
   ```
   {
     "database": "default",
     "host": "your-clickhouse-host",
     "port": 8123,
     "username": "your-username",
     "password": "your-password",
     "query": {},
     "connect_args": {}
   }
   ```
4. Test the connection and save

### Creating Dataset Views

Create the following dataset views in Superset:

#### 1. Overall Data Quality Status
- Source table: `data_quality_latest_status`
- Key metrics:
  - Pass rate percentage
  - Health status
  - Hours since last scan

#### 2. Data Quality Trends
- Source table: `data_quality_daily_summary`
- Key metrics:
  - Daily pass rate
  - Total checks
  - Failed checks trend

#### 3. Failed Checks Analysis
- Source table: `data_quality_failed_checks`
- Key metrics:
  - Failure patterns
  - Most frequent failures
  - Failure streaks

#### 4. Check Details
- Source table: `data_quality_checks`
- Key metrics:
  - Check results by type
  - Check results by severity
  - Check value trends

### Sample Dashboard Components

#### 1. Health Overview
```sql
SELECT 
    data_source,
    health_status,
    pass_rate_percent,
    hours_since_last_scan,
    last_scan_time
FROM data_quality_latest_status
```

#### 2. Daily Trends
```sql
SELECT 
    scan_date,
    data_source,
    avg_pass_rate,
    total_passed,
    total_failed
FROM data_quality_daily_summary
WHERE scan_date >= dateAdd(day, -30, today())
ORDER BY scan_date DESC
```

#### 3. Critical Failures
```sql
SELECT 
    c.data_source,
    c.table_name,
    c.check_name,
    c.check_details,
    c.scan_timestamp
FROM data_quality_checks c
WHERE c.severity = 'CRITICAL' 
  AND c.check_result = 'FAIL'
  AND c.scan_date >= dateAdd(day, -7, today())
ORDER BY c.scan_timestamp DESC
```

#### 4. Check Type Distribution
```sql
SELECT 
    check_type,
    count(*) as check_count,
    countIf(check_result = 'PASS') as passed_checks,
    countIf(check_result = 'FAIL') as failed_checks
FROM data_quality_checks
WHERE scan_date = today()
GROUP BY check_type
ORDER BY check_count DESC
```

### Recommended Charts

1. **Status Overview**
   - Type: Big Number with Trendline
   - Metric: Overall pass rate
   - Trendline: 7-day historical

2. **Health Distribution**
   - Type: Pie Chart
   - Dimensions: health_status
   - Metrics: count of data sources

3. **Pass Rate Trends**
   - Type: Line Chart
   - Time Column: scan_date
   - Metrics: avg_pass_rate
   - Group by: data_source

4. **Failed Checks Heatmap**
   - Type: Heatmap
   - Dimensions: check_type, severity
   - Metrics: count of failures

5. **Recent Failures Table**
   - Type: Table
   - Time Column: scan_timestamp
   - Columns: data_source, check_name, check_details

### Dashboard Layout

1. **Top Row**
   - Overall health status
   - Pass rate KPI
   - Total checks monitored
   - Last scan timestamp

2. **Middle Row**
   - Pass rate trends chart
   - Check type distribution
   - Severity distribution

3. **Bottom Row**
   - Recent failures table
   - Failure streak analysis
   - Check value trends

### Refresh Settings

1. Set dashboard refresh interval to 5-15 minutes
2. Configure Superset caching as needed
3. Use Superset's native async query mode for better performance

### Alert Setup

1. Create alerts for:
   - Critical check failures
   - Pass rate drops below threshold
   - Missing scan results
   - Long scan intervals

2. Configure notification channels:
   - Email
   - Slack
   - Custom webhooks

### Performance Optimization

1. Use materialized views for frequently accessed metrics
2. Set appropriate TTL for historical data
3. Configure ClickHouse compression settings
4. Use Superset's result set caching

### Security Considerations

1. Create a dedicated ClickHouse user for Superset with read-only access
2. Use connection pooling
3. Implement row-level security if needed
4. Regularly rotate credentials

### Maintenance

1. Monitor query performance
2. Clean up old report data
3. Verify alert configurations
4. Update dashboard components as needed