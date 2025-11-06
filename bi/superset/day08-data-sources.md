# Day 8: Data Sources & Connections

## User Story 1: Configure Database Connections

**Title**: Set Up Multiple Database Connections

**Description**: Configure connections to various database types including PostgreSQL, MySQL, BigQuery, and other supported databases.

**Acceptance Criteria**:
- Database connections are established
- Connection parameters are secure
- Connection pooling is configured
- SSL/TLS encryption is enabled
- Connection testing is successful

**Step-by-Step Guide**:

1. **PostgreSQL Connection**:
```python
# superset_config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/superset'

# Connection parameters
DATABASE_CONNECTION_PARAMETERS = {
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'superset',
        'username': 'superset_user',
        'password': 'secure_password',
        'sslmode': 'require'
    }
}
```

2. **MySQL Connection**:
```python
# MySQL connection configuration
MYSQL_CONNECTION = {
    'host': 'localhost',
    'port': 3306,
    'database': 'superset',
    'user': 'superset_user',
    'password': 'secure_password',
    'charset': 'utf8mb4',
    'ssl': {'ssl': {}}
}
```

3. **BigQuery Connection**:
```python
# BigQuery service account configuration
BIGQUERY_CONNECTION = {
    'project_id': 'your-project-id',
    'key_path': '/path/to/service-account-key.json',
    'location': 'US'
}
```

**Reference Documents**:
- [Database Connections](https://superset.apache.org/docs/installation/connecting-to-databases)
- [Supported Databases](https://superset.apache.org/docs/installation/connecting-to-databases#supported-databases)

---

## User Story 2: Data Source Management

**Title**: Manage and Organize Data Sources

**Description**: Create, configure, and manage data sources including tables, views, and custom SQL queries.

**Acceptance Criteria**:
- Data sources are properly configured
- Table schemas are documented
- Views are created for complex queries
- Custom SQL sources are validated
- Source metadata is maintained

**Step-by-Step Guide**:

1. **Create Database Source**:
```sql
-- Create a view for complex data
CREATE VIEW sales_summary AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_category,
    SUM(sales_amount) as total_sales,
    COUNT(*) as order_count
FROM sales_data
GROUP BY DATE_TRUNC('month', order_date), product_category;
```

2. **Configure Source in Superset**:
```python
# Data source configuration
DATA_SOURCE_CONFIG = {
    'table_name': 'sales_summary',
    'schema': 'public',
    'database_id': 1,
    'description': 'Monthly sales summary by category',
    'columns': [
        {'name': 'month', 'type': 'timestamp'},
        {'name': 'product_category', 'type': 'string'},
        {'name': 'total_sales', 'type': 'decimal'},
        {'name': 'order_count', 'type': 'integer'}
    ]
}
```

3. **Custom SQL Source**:
```sql
-- Custom SQL query as data source
SELECT 
    customer_id,
    customer_name,
    COUNT(*) as total_orders,
    SUM(sales_amount) as total_spent,
    AVG(sales_amount) as avg_order_value
FROM customers c
JOIN sales_data s ON c.customer_id = s.customer_id
WHERE s.order_date >= '2023-01-01'
GROUP BY customer_id, customer_name
HAVING SUM(sales_amount) > 1000;
```

**Reference Documents**:
- [Data Source Configuration](https://superset.apache.org/docs/using-superset/data-sources)
- [Custom SQL Sources](https://superset.apache.org/docs/using-superset/data-sources#custom-sql)

---

## User Story 3: Data Modeling and Schema Design

**Title**: Design Effective Data Models

**Description**: Create well-structured data models with proper relationships, indexes, and constraints for optimal Superset performance.

**Acceptance Criteria**:
- Data models are normalized
- Relationships are properly defined
- Indexes are created for performance
- Constraints ensure data integrity
- Models support analytical queries

**Step-by-Step Guide**:

1. **Create Analytical Tables**:
```sql
-- Create fact table for sales
CREATE TABLE sales_fact (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    order_date DATE NOT NULL,
    sales_amount DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_sales_customer ON sales_fact(customer_id);
CREATE INDEX idx_sales_date ON sales_fact(order_date);
CREATE INDEX idx_sales_product ON sales_fact(product_id);
CREATE INDEX idx_sales_region ON sales_fact(region);
```

2. **Create Dimension Tables**:
```sql
-- Customer dimension table
CREATE TABLE customer_dim (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    segment VARCHAR(50),
    region VARCHAR(50),
    created_date DATE
);

-- Product dimension table
CREATE TABLE product_dim (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    price DECIMAL(10,2)
);
```

3. **Create Analytical Views**:
```sql
-- Customer analytics view
CREATE VIEW customer_analytics AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    COUNT(s.sale_id) as total_orders,
    SUM(s.sales_amount) as total_spent,
    AVG(s.sales_amount) as avg_order_value,
    MAX(s.order_date) as last_order_date
FROM customer_dim c
LEFT JOIN sales_fact s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.region;
```

**Reference Documents**:
- [Data Modeling Best Practices](https://superset.apache.org/docs/installation/performance-tuning#data-modeling)
- [Database Schema Design](https://superset.apache.org/docs/installation/performance-tuning#schema-design)

---

## User Story 4: Data Source Security and Permissions

**Title**: Implement Data Source Security

**Description**: Configure security measures for data sources including row-level security, column-level permissions, and access controls.

**Acceptance Criteria**:
- Row-level security is implemented
- Column-level permissions are set
- Access controls are configured
- Data masking is applied where needed
- Audit logging is enabled

**Step-by-Step Guide**:

1. **Row-Level Security**:
```sql
-- Enable RLS on sales table
ALTER TABLE sales_fact ENABLE ROW LEVEL SECURITY;

-- Create policy for regional access
CREATE POLICY regional_access ON sales_fact
    FOR SELECT
    USING (region = current_setting('app.current_region', true));

-- Create policy for user-based access
CREATE POLICY user_sales_access ON sales_fact
    FOR SELECT
    USING (customer_id IN (
        SELECT customer_id FROM user_customers 
        WHERE user_id = current_user
    ));
```

2. **Column-Level Permissions**:
```sql
-- Grant specific column access
GRANT SELECT (customer_id, order_date, sales_amount) 
ON sales_fact TO analyst_role;

-- Revoke sensitive column access
REVOKE SELECT (customer_email, credit_card) 
ON customers FROM public;
```

3. **Data Masking**:
```sql
-- Create masked view for sensitive data
CREATE VIEW masked_customers AS
SELECT 
    customer_id,
    CONCAT(LEFT(customer_name, 1), '***') as masked_name,
    CONCAT(LEFT(email, 3), '***@***') as masked_email,
    segment,
    region
FROM customer_dim;
```

**Reference Documents**:
- [Data Source Security](https://superset.apache.org/docs/security)
- [Row-Level Security](https://superset.apache.org/docs/security#row-level-security)

---

## User Story 5: Data Source Monitoring and Maintenance

**Title**: Monitor and Maintain Data Sources

**Description**: Implement monitoring and maintenance procedures for data sources including performance monitoring, data quality checks, and backup strategies.

**Acceptance Criteria**:
- Data source performance is monitored
- Data quality is regularly checked
- Backup procedures are in place
- Maintenance schedules are established
- Issues are proactively identified

**Step-by-Step Guide**:

1. **Performance Monitoring**:
```sql
-- Monitor query performance
SELECT 
    query,
    execution_time,
    rows_returned,
    created_at
FROM query_log
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY execution_time DESC
LIMIT 10;
```

2. **Data Quality Checks**:
```sql
-- Check for data quality issues
SELECT 
    'Missing customer_id' as issue,
    COUNT(*) as count
FROM sales_fact
WHERE customer_id IS NULL

UNION ALL

SELECT 
    'Negative sales amounts' as issue,
    COUNT(*) as count
FROM sales_fact
WHERE sales_amount < 0

UNION ALL

SELECT 
    'Future order dates' as issue,
    COUNT(*) as count
FROM sales_fact
WHERE order_date > CURRENT_DATE;
```

3. **Backup Strategy**:
```bash
#!/bin/bash
# Backup script for Superset data sources

# Backup PostgreSQL database
pg_dump -h localhost -U superset_user superset > backup_$(date +%Y%m%d).sql

# Backup configuration files
cp superset_config.py backup_config_$(date +%Y%m%d).py

# Compress backups
gzip backup_$(date +%Y%m%d).sql
```

**Reference Documents**:
- [Data Source Monitoring](https://superset.apache.org/docs/installation/monitoring)
- [Backup and Recovery](https://superset.apache.org/docs/installation/backup-recovery)

---

## Summary

Key data source concepts covered:
- **Database Connections**: PostgreSQL, MySQL, BigQuery
- **Data Source Management**: Tables, views, custom SQL
- **Data Modeling**: Schemas, relationships, indexes
- **Security**: RLS, permissions, data masking
- **Monitoring**: Performance, quality, maintenance

**Next Steps**:
- Configure additional database connections
- Design comprehensive data models
- Implement security measures
- Set up monitoring and maintenance
- Optimize data source performance