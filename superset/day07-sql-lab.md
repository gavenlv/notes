# Day 7: SQL Lab & Advanced Queries

## User Story 1: Master SQL Lab Interface

**Title**: Navigate and Use SQL Lab Effectively

**Description**: Learn to use SQL Lab's interface for writing, executing, and saving complex SQL queries with advanced features.

**Acceptance Criteria**:
- SQL Lab interface is familiar
- Queries can be written and executed
- Results are displayed properly
- Queries can be saved and shared
- Query history is accessible

**Step-by-Step Guide**:

1. **Access SQL Lab**:
```bash
# Navigate to SQL Lab in Superset UI
# URL: http://localhost:8088/superset/sqllab
```

2. **Basic Query Execution**:
```sql
-- Simple query to test connection
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

3. **Save and Share Queries**:
```sql
-- Save query with description
-- Use "Save Query" button
-- Add metadata: title, description, tags
```

**Reference Documents**:
- [SQL Lab Documentation](https://superset.apache.org/docs/using-superset/sql-lab)
- [Query Management](https://superset.apache.org/docs/using-superset/sql-lab#saving-queries)

---

## User Story 2: Advanced SQL Techniques

**Title**: Implement Complex SQL Queries

**Description**: Write advanced SQL queries using window functions, CTEs, subqueries, and complex joins for sophisticated data analysis.

**Acceptance Criteria**:
- Window functions are used correctly
- CTEs improve query readability
- Subqueries are optimized
- Complex joins work efficiently
- Query performance is acceptable

**Step-by-Step Guide**:

1. **Window Functions**:
```sql
-- Running totals and rankings
SELECT 
    product_category,
    order_date,
    sales_amount,
    SUM(sales_amount) OVER (
        PARTITION BY product_category 
        ORDER BY order_date
    ) as running_total,
    RANK() OVER (
        PARTITION BY DATE_TRUNC('month', order_date)
        ORDER BY sales_amount DESC
    ) as monthly_rank
FROM sales_data
WHERE order_date >= '2023-01-01';
```

2. **Common Table Expressions (CTEs)**:
```sql
-- Complex analysis using CTEs
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        product_category,
        SUM(sales_amount) as total_sales
    FROM sales_data
    WHERE order_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date), product_category
),
category_ranks AS (
    SELECT 
        *,
        RANK() OVER (
            PARTITION BY month 
            ORDER BY total_sales DESC
        ) as rank
    FROM monthly_sales
)
SELECT * FROM category_ranks WHERE rank <= 5;
```

3. **Complex Joins**:
```sql
-- Multiple table joins with conditions
SELECT 
    c.customer_name,
    p.product_name,
    o.order_date,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) as total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= '2023-01-01'
  AND o.status = 'completed';
```

**Reference Documents**:
- [Advanced SQL in Superset](https://superset.apache.org/docs/using-superset/sql-lab#advanced-sql)
- [Query Optimization](https://superset.apache.org/docs/using-superset/sql-lab#query-optimization)

---

## User Story 3: Query Performance Optimization

**Title**: Optimize SQL Query Performance

**Description**: Implement query optimization techniques including indexing, query structure, and execution plan analysis.

**Acceptance Criteria**:
- Queries execute within acceptable time
- Execution plans are analyzed
- Indexes are used effectively
- Query structure is optimized
- Resource usage is monitored

**Step-by-Step Guide**:

1. **Query Structure Optimization**:
```sql
-- Optimized query with proper filtering
SELECT 
    product_category,
    SUM(sales_amount) as total_sales,
    COUNT(*) as order_count
FROM sales_data
WHERE order_date >= '2023-01-01'
  AND order_date < '2024-01-01'
  AND status = 'completed'
GROUP BY product_category
HAVING SUM(sales_amount) > 10000
ORDER BY total_sales DESC
LIMIT 20;
```

2. **Index Usage Analysis**:
```sql
-- Check index usage
EXPLAIN ANALYZE
SELECT 
    customer_id,
    SUM(sales_amount) as total_spent
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY customer_id
HAVING SUM(sales_amount) > 1000;
```

3. **Query Plan Optimization**:
```sql
-- Use materialized views for complex queries
CREATE MATERIALIZED VIEW monthly_sales_summary AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_category,
    SUM(sales_amount) as total_sales,
    COUNT(*) as order_count
FROM sales_data
GROUP BY DATE_TRUNC('month', order_date), product_category;
```

**Reference Documents**:
- [Query Performance](https://superset.apache.org/docs/installation/performance-tuning)
- [Database Optimization](https://superset.apache.org/docs/installation/performance-tuning#database-optimization)

---

## User Story 4: Data Exploration and Analysis

**Title**: Conduct Comprehensive Data Exploration

**Description**: Use SQL Lab for exploratory data analysis including data profiling, statistical analysis, and data quality checks.

**Acceptance Criteria**:
- Data profiling is comprehensive
- Statistical analysis is accurate
- Data quality issues are identified
- Insights are documented
- Analysis is reproducible

**Step-by-Step Guide**:

1. **Data Profiling**:
```sql
-- Comprehensive data profiling
SELECT 
    'sales_data' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_id) as unique_products,
    MIN(order_date) as earliest_order,
    MAX(order_date) as latest_order,
    AVG(sales_amount) as avg_order_value,
    STDDEV(sales_amount) as std_order_value
FROM sales_data;
```

2. **Statistical Analysis**:
```sql
-- Statistical analysis by category
SELECT 
    product_category,
    COUNT(*) as order_count,
    AVG(sales_amount) as avg_sales,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sales_amount) as median_sales,
    MIN(sales_amount) as min_sales,
    MAX(sales_amount) as max_sales,
    STDDEV(sales_amount) as sales_stddev
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY product_category
ORDER BY avg_sales DESC;
```

3. **Data Quality Check**:
```sql
-- Identify data quality issues
SELECT 
    'Missing customer_id' as issue_type,
    COUNT(*) as count
FROM sales_data
WHERE customer_id IS NULL

UNION ALL

SELECT 
    'Negative sales amounts' as issue_type,
    COUNT(*) as count
FROM sales_data
WHERE sales_amount < 0

UNION ALL

SELECT 
    'Future order dates' as issue_type,
    COUNT(*) as count
FROM sales_data
WHERE order_date > CURRENT_DATE;
```

**Reference Documents**:
- [Data Exploration](https://superset.apache.org/docs/using-superset/sql-lab#data-exploration)
- [Statistical Analysis](https://superset.apache.org/docs/using-superset/sql-lab#statistical-analysis)

---

## User Story 5: Query Templates and Best Practices

**Title**: Create Reusable Query Templates

**Description**: Develop query templates and establish best practices for common analytical tasks and reporting.

**Acceptance Criteria**:
- Query templates are created
- Best practices are documented
- Templates are reusable
- Performance guidelines are followed
- Code is well-documented

**Step-by-Step Guide**:

1. **Sales Analysis Template**:
```sql
-- Template: Monthly Sales Analysis
-- Parameters: @start_date, @end_date, @category_filter
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_category,
    SUM(sales_amount) as total_sales,
    COUNT(*) as order_count,
    AVG(sales_amount) as avg_order_value
FROM sales_data
WHERE order_date >= @start_date
  AND order_date <= @end_date
  AND (@category_filter IS NULL OR product_category = @category_filter)
GROUP BY DATE_TRUNC('month', order_date), product_category
ORDER BY month DESC, total_sales DESC;
```

2. **Customer Segmentation Template**:
```sql
-- Template: Customer Segmentation by Spending
WITH customer_totals AS (
    SELECT 
        customer_id,
        SUM(sales_amount) as total_spent,
        COUNT(*) as order_count,
        AVG(sales_amount) as avg_order_value
    FROM sales_data
    WHERE order_date >= '2023-01-01'
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN total_spent >= 10000 THEN 'High Value'
        WHEN total_spent >= 5000 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_spent,
    AVG(order_count) as avg_orders
FROM customer_totals
GROUP BY customer_segment
ORDER BY avg_spent DESC;
```

3. **Best Practices Documentation**:
```markdown
# SQL Lab Best Practices

## Query Structure
- Use CTEs for complex queries
- Limit results with WHERE clauses early
- Use appropriate indexes
- Avoid SELECT * in production

## Performance
- Test queries with EXPLAIN ANALYZE
- Use LIMIT for large result sets
- Consider materialized views for frequent queries
- Monitor query execution time

## Documentation
- Add comments to complex queries
- Document parameter usage
- Include query purpose and expected results
- Version control important queries
```

**Reference Documents**:
- [SQL Best Practices](https://superset.apache.org/docs/using-superset/sql-lab#best-practices)
- [Query Templates](https://superset.apache.org/docs/using-superset/sql-lab#templates)

---

## Summary

Key SQL Lab concepts covered:
- **Interface Mastery**: Navigation, execution, saving
- **Advanced SQL**: Window functions, CTEs, complex joins
- **Performance**: Optimization, indexing, execution plans
- **Data Exploration**: Profiling, statistics, quality checks
- **Templates**: Reusable queries, best practices

**Next Steps**:
- Practice advanced SQL techniques
- Optimize query performance
- Create reusable templates
- Document best practices
- Explore data with complex queries 