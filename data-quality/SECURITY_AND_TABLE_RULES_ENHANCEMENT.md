# Security and Table Rules Enhancement

## Overview

This document describes the refactoring performed to enhance the data quality framework with improved security practices and table/view-based rule definitions.

## Changes Made

### 1. Security Enhancement - Environment Variables

**Problem**: Sensitive configuration values (database credentials, connection details) were hardcoded in the configuration file, posing security risks.

**Solution**: Moved all sensitive information to environment variables.

#### Files Created:
- `environment.env` - Contains actual environment variables (should not be committed to version control)
- `environment.env.example` - Template file showing required environment variables

#### Configuration Variables Moved:
- `CLICKHOUSE_HOST` - Database host
- `CLICKHOUSE_PORT` - Database port  
- `CLICKHOUSE_DATABASE` - Database name
- `CLICKHOUSE_USER` - Database username
- `CLICKHOUSE_PASSWORD` - Database password
- `CLICKHOUSE_SECURE` - SSL connection flag
- `CLICKHOUSE_TIMEOUT` - Connection timeout
- `RESULTS_DATABASE` - Results storage database
- `RESULTS_TABLE` - Results storage table
- `METRICS_PORT` - Prometheus metrics port
- `GRAFANA_DASHBOARD_URL` - Grafana dashboard URL
- `REPORT_LOCATION` - Report output directory
- `LOG_FILE` - Log file location

#### Usage Instructions:
1. Copy `environment.env.example` to `environment.env`
2. Update the values in `environment.env` with your actual configuration
3. Load environment variables before running the application:
   ```bash
   # On Windows
   set /p < environment.env
   
   # On Linux/Mac
   source environment.env
   ```

### 2. Table/View-Based Rule Definitions

**Enhancement**: Added comprehensive support for defining data quality rules specific to tables and views.

#### New Configuration Sections:

##### `table_rules`
Defines rules for specific tables or views with the following structure:

```yaml
table_rules:
  table_identifier:
    table_name: "actual_table_name"
    schema: "schema_name"
    rules:
      - name: "rule_name"
        type: "rule_type"
        column: "column_name"
        category: "completeness|accuracy|consistency|timeliness"
        priority: "high|medium|low"
        description: "Rule description"
        # Additional parameters based on rule type
```

##### `rule_types`
Defines available rule types and their parameters:

- **not_null**: Check for null values
- **data_range**: Validate numeric ranges
- **regex_pattern**: Pattern validation
- **value_set**: Valid value enumeration
- **freshness_check**: Data recency validation
- **uniqueness**: Unique value validation
- **referential_integrity**: Foreign key validation

### 3. Example Rule Configurations

#### User Table Rules:
```yaml
users_table:
  table_name: "users"
  schema: "default"
  rules:
    - name: "user_id_not_null"
      type: "not_null"
      column: "user_id"
      category: "completeness"
      priority: "high"
      
    - name: "age_range_validation"
      type: "data_range"
      column: "age"
      min_value: 0
      max_value: 150
      category: "accuracy"
      priority: "medium"
```

#### Order View Rules:
```yaml
user_orders_view:
  table_name: "user_orders_view"
  schema: "analytics"
  rules:
    - name: "order_status_valid"
      type: "value_set"
      column: "order_status"
      valid_values: ["pending", "processing", "shipped", "delivered", "cancelled"]
      category: "accuracy"
      priority: "high"
```

## Security Benefits

1. **Credential Protection**: Database passwords and sensitive URLs are no longer visible in configuration files
2. **Version Control Safety**: Environment files are excluded from git commits
3. **Environment Isolation**: Different environments can use different credentials without code changes
4. **Compliance**: Meets security best practices for credential management

## Functionality Benefits

1. **Table-Specific Rules**: Define rules that apply only to specific tables or views
2. **Flexible Rule Types**: Support for various validation types (null checks, ranges, patterns, etc.)
3. **Categorized Rules**: Organize rules by quality dimensions (completeness, accuracy, etc.)
4. **Priority Levels**: Set rule priorities for execution and reporting
5. **Extensible Framework**: Easy to add new rule types and table configurations

## Migration Guide

### For Existing Users:

1. **Update Environment Setup**:
   ```bash
   cp environment.env.example environment.env
   # Edit environment.env with your actual values
   ```

2. **Update Application Startup**:
   - Ensure environment variables are loaded before starting the application
   - Update deployment scripts to include environment variable loading

3. **Configure Table Rules**:
   - Review the example table rules in the configuration
   - Add rules for your specific tables and views
   - Customize rule parameters based on your data quality requirements

### For New Users:

1. Follow the standard setup process
2. Configure `environment.env` with your database credentials
3. Define table rules for your specific use case
4. Run the data quality framework as usual

## File Structure

```
data-quality/
├── environment.env              # Actual environment variables (not in git)
├── environment.env.example      # Environment template
├── .gitignore                   # Updated to exclude environment.env
└── configs/
    └── data-quality-config.yml  # Updated configuration with env vars and table rules
```

## Best Practices

1. **Never commit** `environment.env` to version control
2. **Always use** environment variables for sensitive information
3. **Document** any new environment variables in the `.example` file
4. **Test** rule configurations with sample data before production use
5. **Monitor** rule performance and adjust priorities as needed

## Next Steps

1. Implement environment variable loading in the application code
2. Add support for dynamic rule loading based on table configuration
3. Implement rule execution engine enhancements to support new rule types
4. Add validation for rule configurations during startup
5. Create automated tests for table-specific rules
