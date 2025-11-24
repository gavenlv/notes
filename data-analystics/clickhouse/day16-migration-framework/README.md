# ClickHouse Migration Framework

A comprehensive database migration framework for ClickHouse, inspired by Flyway, that provides DDL/DML management with execution and rollback capabilities.

## 🎯 Features

### Core Capabilities
- **Version Control**: Track migration versions and execution history
- **Forward Migration**: Execute DDL/DML statements in order
- **Rollback Support**: Undo migrations with automatic rollback scripts
- **Validation**: Verify migration integrity and dependencies
- **Parallel Execution**: Support for concurrent migrations
- **Environment Management**: Different configurations for dev/staging/prod

### Advanced Features
- **Dependency Management**: Handle migration dependencies and ordering
- **Dry Run Mode**: Preview migrations without execution
- **Migration Templates**: Pre-built templates for common operations
- **Rollback Strategies**: Multiple rollback approaches (DROP, ALTER, etc.)
- **Audit Trail**: Complete history of all migration operations
- **Cluster Support**: Multi-node ClickHouse cluster migrations

## 📁 Architecture

```
migration-framework/
├── README.md                    # This file
├── core/                        # Core framework components
│   ├── migration_manager.py     # Main migration orchestrator
│   ├── migration_parser.py      # SQL parsing and validation
│   ├── rollback_manager.py      # Rollback logic and execution
│   └── version_control.py       # Version tracking and history
├── templates/                   # Migration templates
│   ├── create_table.sql         # Table creation template
│   ├── alter_table.sql          # Table modification template
│   ├── create_index.sql         # Index creation template
│   └── data_migration.sql       # Data migration template
├── migrations/                  # Migration files
│   ├── V1__create_users_table.sql
│   ├── V2__add_user_indexes.sql
│   ├── V3__create_events_table.sql
│   └── V4__add_partitioning.sql
├── configs/                     # Configuration files
│   ├── migration-config.yml     # Main configuration
│   ├── environments/            # Environment-specific configs
│   │   ├── development.yml
│   │   ├── staging.yml
│   │   └── production.yml
│   └── templates/               # Template configurations
├── scripts/                     # Management scripts
│   ├── migrate.py               # Main migration script
│   ├── rollback.py              # Rollback script
│   ├── status.py                # Status checking script
│   └── validate.py              # Validation script
├── examples/                    # Usage examples
│   ├── basic-migration.sql      # Basic migration example
│   ├── complex-migration.sql    # Complex migration example
│   └── rollback-example.sql     # Rollback example
└── tests/                       # Test suite
    ├── test_migration_manager.py
    ├── test_rollback_manager.py
    └── test_integration.py
```

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the migration framework directory
cd clickhouse/day16-migration-framework

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp configs/environments/development.yml configs/environments/local.yml
# Edit local.yml with your ClickHouse connection details
```

### 2. Create Your First Migration

```bash
# Create a new migration
python scripts/migrate.py create --name create_users_table

# This creates: migrations/V1__create_users_table.sql
```

### 3. Write Migration

```sql
-- migrations/V1__create_users_table.sql
-- Migration: Create users table
-- Version: 1
-- Description: Initial users table with basic fields

-- Forward Migration
CREATE TABLE IF NOT EXISTS users (
    id UInt32,
    username String,
    email String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id
PARTITION BY toYYYYMM(created_at);

-- Rollback Migration
-- ROLLBACK: DROP TABLE IF EXISTS users;
```

### 4. Execute Migration

```bash
# Run migration
python scripts/migrate.py migrate

# Check status
python scripts/migrate.py status

# Rollback if needed
python scripts/migrate.py rollback --version 1
```

## 📋 Migration File Format

### Standard Format
```sql
-- Migration: [Migration Name]
-- Version: [Version Number]
-- Description: [Description]
-- Author: [Author Name]
-- Created: [Date]
-- Dependencies: [Optional comma-separated version numbers]

-- Forward Migration (Required)
[Your SQL statements here]

-- Rollback Migration (Optional)
-- ROLLBACK: [Rollback SQL statements]
```

### Advanced Format with Metadata
```sql
-- Migration: Create complex table with indexes
-- Version: 2
-- Description: Create events table with partitioning and indexing
-- Author: Data Team
-- Created: 2024-01-15
-- Dependencies: 1
-- Environment: all
-- Rollback: true

-- Forward Migration
CREATE TABLE IF NOT EXISTS events (
    event_id UUID,
    user_id UInt32,
    event_type String,
    event_data String,
    timestamp DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp)
PARTITION BY toYYYYMM(timestamp)
TTL created_at + INTERVAL 1 YEAR;

-- Create indexes
CREATE INDEX idx_events_type ON events (event_type) TYPE bloom_filter GRANULARITY 1;
CREATE INDEX idx_events_timestamp ON events (timestamp) TYPE minmax GRANULARITY 1;

-- Rollback Migration
-- ROLLBACK: DROP TABLE IF EXISTS events;
```

## ⚙️ Configuration

### Main Configuration (migration-config.yml)
```yaml
# Database Configuration
database:
  host: localhost
  port: 9000
  database: default
  user: default
  password: ""
  secure: false
  verify: false

# Migration Settings
migration:
  table_name: schema_migrations
  version_format: "V{version}__{description}"
  rollback_enabled: true
  parallel_execution: false
  dry_run: false
  
# Environment Settings
environments:
  development:
    database: dev_db
    user: dev_user
  staging:
    database: staging_db
    user: staging_user
  production:
    database: prod_db
    user: prod_user
    rollback_enabled: false  # Disable rollback in production

# Validation Settings
validation:
  check_syntax: true
  check_dependencies: true
  check_rollback: true
  max_migration_size: 1048576  # 1MB

# Logging
logging:
  level: INFO
  file: migration.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🛠️ Usage Examples

### Basic Operations

```bash
# Initialize migration framework
python scripts/migrate.py init

# Create new migration
python scripts/migrate.py create --name add_user_profile

# Run all pending migrations
python scripts/migrate.py migrate

# Run specific migration
python scripts/migrate.py migrate --version 3

# Check migration status
python scripts/migrate.py status

# Validate migrations
python scripts/migrate.py validate

# Rollback last migration
python scripts/migrate.py rollback

# Rollback to specific version
python scripts/migrate.py rollback --version 2

# Dry run (preview without execution)
python scripts/migrate.py migrate --dry-run
```

### Advanced Operations

```bash
# Run with specific environment
python scripts/migrate.py migrate --env production

# Run with custom configuration
python scripts/migrate.py migrate --config custom-config.yml

# Generate migration report
python scripts/migrate.py report --format html

# Clean migration history
python scripts/migrate.py clean --older-than 30

# Export migration state
python scripts/migrate.py export --file migration-state.json

# Import migration state
python scripts/migrate.py import --file migration-state.json
```

## 🔧 Migration Templates

### Table Creation Template
```sql
-- Template: Create table with standard fields
-- Usage: python scripts/migrate.py create --template table --name create_products

-- Migration: Create {table_name} table
-- Version: {version}
-- Description: Create {table_name} table with standard structure

-- Forward Migration
CREATE TABLE IF NOT EXISTS {table_name} (
    id UInt32,
    name String,
    description String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id
PARTITION BY toYYYYMM(created_at);

-- Rollback Migration
-- ROLLBACK: DROP TABLE IF EXISTS {table_name};
```

### Data Migration Template
```sql
-- Template: Data migration with validation
-- Usage: python scripts/migrate.py create --template data --name migrate_user_data

-- Migration: Migrate user data
-- Version: {version}
-- Description: Migrate user data from old format to new format

-- Forward Migration
-- Validate source data
SELECT count() as source_count FROM old_users;

-- Perform data migration
INSERT INTO new_users (id, username, email, created_at)
SELECT id, username, email, created_at
FROM old_users
WHERE id IS NOT NULL;

-- Validate migration
SELECT count() as target_count FROM new_users;

-- Rollback Migration
-- ROLLBACK: DELETE FROM new_users WHERE id IN (SELECT id FROM old_users);
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_migration_manager.py

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html
```

### Test Migration
```bash
# Test migration without execution
python scripts/migrate.py test --migration V1__create_users_table.sql

# Test rollback
python scripts/migrate.py test --rollback --migration V1__create_users_table.sql
```

## 📊 Monitoring and Logging

### Migration Logs
```bash
# View migration logs
tail -f migration.log

# Filter logs by level
grep "ERROR" migration.log

# View migration history
python scripts/migrate.py history --format json
```

### Performance Monitoring
```bash
# Check migration performance
python scripts/migrate.py profile --migration V1__create_users_table.sql

# Generate performance report
python scripts/migrate.py report --performance
```

## 🔒 Security Considerations

### Production Guidelines
1. **Disable Rollback**: Set `rollback_enabled: false` in production
2. **Use Service Accounts**: Create dedicated database users for migrations
3. **Audit Trail**: Enable comprehensive logging
4. **Backup Before Migration**: Always backup before major migrations
5. **Test in Staging**: Test all migrations in staging environment first

### Security Configuration
```yaml
# Production security config
security:
  use_ssl: true
  verify_cert: true
  service_account: migration_service
  audit_logging: true
  backup_before_migration: true
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Issues**
   ```bash
   # Test connection
   python scripts/migrate.py test-connection
   
   # Check ClickHouse status
   systemctl status clickhouse-server
   ```

2. **Migration Conflicts**
   ```bash
   # Check for conflicts
   python scripts/migrate.py validate --check-conflicts
   
   # Resolve conflicts
   python scripts/migrate.py resolve --migration V3__conflict.sql
   ```

3. **Rollback Failures**
   ```bash
   # Check rollback status
   python scripts/migrate.py status --show-rollback
   
   # Manual rollback
   python scripts/migrate.py rollback --manual --version 3
   ```

### Debug Mode
```bash
# Enable debug logging
python scripts/migrate.py migrate --debug

# Verbose output
python scripts/migrate.py migrate --verbose
```

## 📚 Best Practices

### Migration Design
1. **Atomic Operations**: Each migration should be atomic
2. **Idempotent**: Migrations should be safe to run multiple times
3. **Backward Compatible**: Consider impact on existing data
4. **Tested**: Always test migrations in development first
5. **Documented**: Include clear descriptions and comments

### Performance
1. **Batch Operations**: Use batch operations for large datasets
2. **Indexing Strategy**: Plan indexes carefully
3. **Partitioning**: Use appropriate partitioning strategies
4. **Monitoring**: Monitor migration performance

### Team Collaboration
1. **Version Control**: Use Git for migration files
2. **Code Review**: Review all migrations before deployment
3. **Communication**: Notify team of major migrations
4. **Rollback Plan**: Always have a rollback strategy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Happy Migrating!** 🚀

> 💡 **Tip**: Always backup your database before running migrations in production! 