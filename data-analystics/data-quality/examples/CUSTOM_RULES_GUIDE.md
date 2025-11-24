# Custom Rules Guide

This guide explains how to create and use custom data quality rules in the Data Quality Framework.

## Overview

The framework supports several types of custom rules:

1. **Referential Integrity** - Foreign key validation between tables
2. **Uniqueness** - Single column or composite uniqueness checks
3. **Custom** - Fully customizable rules with your own SQL logic

## Rule Structure

All rules follow this basic structure:

```yaml
- rule_type: "rule_type_name"
  version: "1.0"
  description: "Brief description of the rule"
  scenarios: ["scenario1", "scenario2", "all"]
  
  rule:
    name: "unique_rule_name"
    description: "Detailed description"
    category: "rule_category"
    priority: "high|medium|low"
    enabled: true
    
    target:
      database: "database_name"
      table: "table_name"
      column: "column_name"  # Optional
    
    # Additional fields based on rule type
    template: |
      -- Your SQL query here
      SELECT ...
```

## 1. Referential Integrity Rules

Use this type to validate foreign key relationships between tables.

### Basic Structure

```yaml
- rule_type: "referential_integrity"
  rule:
    target:
      database: "ecommerce"
      table: "orders"
      column: "customer_id"
    
    reference:
      database: "ecommerce"
      table: "customers"
      column: "id"
```

### Example: Orders → Customers

```yaml
- rule_type: "referential_integrity"
  version: "1.0"
  description: "Check if orders.customer_id exists in customers.id"
  scenarios: ["referential_integrity", "all"]
  
  rule:
    name: "orders_customers_fk_check"
    description: "Validate that all orders have valid customer references"
    category: "referential_integrity"
    priority: "high"
    enabled: true
    
    target:
      database: "ecommerce"
      table: "orders"
      column: "customer_id"
    
    reference:
      database: "ecommerce"
      table: "customers"
      column: "id"
    
    template: |
      -- Referential integrity check: orders.customer_id -> customers.id
      WITH orphan_records AS (
        SELECT 
          o.customer_id,
          COUNT(*) as orphan_count
        FROM ecommerce.orders o
        LEFT JOIN ecommerce.customers c ON o.customer_id = c.id
        WHERE c.id IS NULL
        GROUP BY o.customer_id
      )
      SELECT
        'referential_integrity_check' as check_type,
        COUNT(*) as total_orphans,
        SUM(orphan_count) as total_orphan_records,
        CASE 
          WHEN COUNT(*) = 0 THEN 'PASS'
          ELSE 'FAIL'
        END as check_result,
        'orders.customer_id references customers.id' as description
      FROM orphan_records
```

## 2. Uniqueness Rules

Use this type to check for unique values in single or multiple columns.

### Basic Structure

```yaml
- rule_type: "uniqueness"
  rule:
    target:
      database: "ecommerce"
      table: "users"
    
    columns: ["email", "domain"]  # Single or multiple columns
```

### Example 1: Single Column Uniqueness

```yaml
- rule_type: "uniqueness"
  version: "1.0"
  description: "Check if user emails are unique"
  scenarios: ["uniqueness", "all"]
  
  rule:
    name: "users_email_unique"
    description: "Ensure email addresses are unique"
    category: "uniqueness"
    priority: "high"
    enabled: true
    
    target:
      database: "ecommerce"
      table: "users"
    
    columns: ["email"]
    
    template: |
      -- Single column uniqueness check
      WITH duplicate_emails AS (
        SELECT 
          email,
          COUNT(*) as duplicate_count
        FROM ecommerce.users
        WHERE email IS NOT NULL
        GROUP BY email
        HAVING COUNT(*) > 1
      )
      SELECT
        'single_column_uniqueness_check' as check_type,
        COUNT(*) as total_duplicates,
        SUM(duplicate_count) as total_duplicate_records,
        CASE 
          WHEN COUNT(*) = 0 THEN 'PASS'
          ELSE 'FAIL'
        END as check_result,
        'email addresses must be unique' as description
      FROM duplicate_emails
```

### Example 2: Composite Uniqueness

```yaml
- rule_type: "uniqueness"
  version: "1.0"
  description: "Check uniqueness of email + domain combination"
  scenarios: ["uniqueness", "all"]
  
  rule:
    name: "users_email_domain_unique"
    description: "Ensure email + domain combination is unique"
    category: "uniqueness"
    priority: "high"
    enabled: true
    
    target:
      database: "ecommerce"
      table: "users"
    
    columns: ["email", "domain"]
    
    template: |
      -- Composite uniqueness check: email + domain
      WITH duplicate_combinations AS (
        SELECT 
          email,
          domain,
          COUNT(*) as duplicate_count
        FROM ecommerce.users
        WHERE email IS NOT NULL AND domain IS NOT NULL
        GROUP BY email, domain
        HAVING COUNT(*) > 1
      )
      SELECT
        'composite_uniqueness_check' as check_type,
        COUNT(*) as total_duplicates,
        SUM(duplicate_count) as total_duplicate_records,
        CASE 
          WHEN COUNT(*) = 0 THEN 'PASS'
          ELSE 'FAIL'
        END as check_result,
        'email + domain combination must be unique' as description
      FROM duplicate_combinations
```

## 3. Custom Rules

Use this type for any custom logic that doesn't fit the predefined categories.

### Basic Structure

```yaml
- rule_type: "custom"
  rule:
    target:
      database: "ecommerce"
      table: "orders"
    
    template: |
      -- Your custom SQL logic here
      SELECT ...
```

### Example 1: Cross-Table Consistency

```yaml
- rule_type: "custom"
  version: "1.0"
  description: "Check if order totals match sum of order items"
  scenarios: ["data_consistency", "all"]
  
  rule:
    name: "orders_items_total_consistency"
    description: "Validate order totals against sum of order items"
    category: "custom"
    priority: "high"
    enabled: true
    
    target:
      database: "ecommerce"
      table: "orders"
    
    template: |
      -- Cross-table consistency: order totals vs sum of items
      WITH order_totals AS (
        SELECT 
          o.id as order_id,
          o.total_amount as order_total,
          COALESCE(SUM(oi.quantity * oi.unit_price), 0) as calculated_total,
          ABS(o.total_amount - COALESCE(SUM(oi.quantity * oi.unit_price), 0)) as difference
        FROM ecommerce.orders o
        LEFT JOIN ecommerce.order_items oi ON o.id = oi.order_id
        WHERE o.status != 'cancelled'
        GROUP BY o.id, o.total_amount
      )
      SELECT
        'cross_table_consistency_check' as check_type,
        COUNT(*) as total_orders,
        COUNT(CASE WHEN difference > 0.01 THEN 1 END) as inconsistent_orders,
        SUM(difference) as total_difference,
        CASE 
          WHEN COUNT(CASE WHEN difference > 0.01 THEN 1 END) = 0 THEN 'PASS'
          ELSE 'FAIL'
        END as check_result,
        'order totals must match sum of order items' as description
      FROM order_totals
```

### Example 2: Business Rule Validation

```yaml
- rule_type: "custom"
  version: "1.0"
  description: "Check if product prices are within acceptable range"
  scenarios: ["business_rules", "all"]
  
  rule:
    name: "product_price_range_check"
    description: "Validate product prices are within business-defined ranges"
    category: "custom"
    priority: "medium"
    enabled: true
    
    target:
      database: "ecommerce"
      table: "products"
    
    parameters:
      min_price: 0.01
      max_price: 10000.00
      category_ranges:
        electronics:
          min: 10.00
          max: 5000.00
        books:
          min: 5.00
          max: 200.00
    
    template: |
      -- Data range validation with business rules
      WITH price_violations AS (
        SELECT 
          id,
          name,
          price,
          category,
          CASE 
            WHEN price < 0.01 THEN 'below_minimum'
            WHEN price > 10000.00 THEN 'above_maximum'
            WHEN category = 'electronics' AND (price < 10.00 OR price > 5000.00) THEN 'category_range_violation'
            WHEN category = 'books' AND (price < 5.00 OR price > 200.00) THEN 'category_range_violation'
            ELSE 'valid'
          END as violation_type
        FROM ecommerce.products
        WHERE active = 1
      )
      SELECT
        'data_range_validation_check' as check_type,
        COUNT(*) as total_products,
        COUNT(CASE WHEN violation_type != 'valid' THEN 1 END) as violations,
        CASE 
          WHEN COUNT(CASE WHEN violation_type != 'valid' THEN 1 END) = 0 THEN 'PASS'
          ELSE 'FAIL'
        END as check_result,
        'product prices must be within business-defined ranges' as description
      FROM price_violations
```

## SQL Template Requirements

Your SQL template must return a result set with these columns:

- `check_type` - Type of check being performed
- `check_result` - Must be 'PASS' or 'FAIL'
- `description` - Human-readable description of the check

### Optional Columns

- `total_records` - Total number of records checked
- `violations` - Number of violations found
- `details` - Additional details about violations

### Example Output Structure

```sql
SELECT
  'my_custom_check' as check_type,
  COUNT(*) as total_records,
  COUNT(CASE WHEN condition THEN 1 END) as violations,
  CASE 
    WHEN COUNT(CASE WHEN condition THEN 1 END) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as check_result,
  'Description of what this check validates' as description
FROM your_table
WHERE your_conditions
```

## Using Custom Rules

### 1. Create Your Rule File

Create a YAML file with your custom rules:

```yaml
# my_custom_rules.yml
- rule_type: "custom"
  version: "1.0"
  description: "My custom data quality check"
  scenarios: ["my_scenario", "all"]
  
  rule:
    name: "my_custom_check"
    description: "Description of my check"
    category: "custom"
    priority: "high"
    enabled: true
    
    target:
      database: "my_database"
      table: "my_table"
    
    template: |
      -- My custom SQL logic
      SELECT
        'my_custom_check' as check_type,
        COUNT(*) as total_records,
        CASE 
          WHEN COUNT(*) > 0 THEN 'PASS'
          ELSE 'FAIL'
        END as check_result,
        'My custom validation' as description
      FROM my_database.my_table
```

### 2. Add to Configuration

Add your rule file to the configuration:

```yaml
# configs/test-config.yml
rules:
  paths:
    - "rules/"
    - "scenarios/"
    - "examples/"  # Add your custom rules directory
```

### 3. Run Your Rules

```bash
# Run specific scenario
python data_quality_runner.py --scenario my_scenario

# Run all rules
python data_quality_runner.py --scenario all
```

## Best Practices

### 1. Naming Conventions

- Use descriptive names: `orders_customers_fk_check`
- Include table names in rule names
- Use consistent naming patterns

### 2. SQL Templates

- Always include comments explaining the logic
- Use CTEs (Common Table Expressions) for complex queries
- Return consistent column names
- Handle NULL values appropriately

### 3. Error Handling

- Use CASE statements to handle different scenarios
- Provide meaningful error messages
- Consider edge cases in your logic

### 4. Performance

- Use appropriate indexes on referenced columns
- Limit result sets when possible
- Consider using EXISTS instead of JOINs for large tables

### 5. Documentation

- Provide clear descriptions for each rule
- Document business logic and assumptions
- Include examples of expected data

## Common Patterns

### Pattern 1: Existence Check

```sql
SELECT
  'existence_check' as check_type,
  COUNT(*) as total_records,
  CASE 
    WHEN COUNT(*) > 0 THEN 'PASS'
    ELSE 'FAIL'
  END as check_result,
  'Records must exist' as description
FROM table_name
WHERE condition
```

### Pattern 2: Count Validation

```sql
SELECT
  'count_validation' as check_type,
  COUNT(*) as total_records,
  COUNT(CASE WHEN condition THEN 1 END) as violations,
  CASE 
    WHEN COUNT(CASE WHEN condition THEN 1 END) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as check_result,
  'All records must meet condition' as description
FROM table_name
```

### Pattern 3: Range Validation

```sql
SELECT
  'range_validation' as check_type,
  COUNT(*) as total_records,
  COUNT(CASE WHEN value < min OR value > max THEN 1 END) as violations,
  CASE 
    WHEN COUNT(CASE WHEN value < min OR value > max THEN 1 END) = 0 THEN 'PASS'
    ELSE 'FAIL'
  END as check_result,
  'Values must be within range' as description
FROM table_name
WHERE value IS NOT NULL
```

## Troubleshooting

### Common Issues

1. **SQL Syntax Errors**
   - Check your SQL syntax
   - Validate against your database
   - Use database-specific functions correctly

2. **Missing Columns**
   - Ensure all required columns are returned
   - Check column names match expected format

3. **Performance Issues**
   - Add appropriate indexes
   - Limit data processed
   - Use efficient SQL patterns

4. **Rule Not Executing**
   - Check rule is enabled
   - Verify scenario filtering
   - Confirm file path is correct

### Debug Mode

Enable debug logging to see detailed information:

```bash
python data_quality_runner.py --log-level DEBUG --scenario your_scenario
```

## Examples Directory

See the `examples/` directory for complete working examples:

- `custom_rules.yml` - Comprehensive examples of all rule types
- `referential_integrity_example.yml` - Foreign key validation examples
- `uniqueness_example.yml` - Uniqueness check examples
- `business_rules_example.yml` - Business logic validation examples
