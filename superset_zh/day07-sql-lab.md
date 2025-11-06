# 第7天：SQL Lab与高级查询

## 用户故事1：掌握SQL Lab界面

**标题**：高效导航和使用SQL Lab

**描述**：学习使用SQL Lab界面编写、执行和保存带有高级功能的复杂SQL查询。

**验收标准**：
- 熟悉SQL Lab界面
- 能够编写和执行查询
- 结果正确显示
- 查询可以保存和共享
- 可访问查询历史记录

**分步指南**：

1. **访问SQL Lab**：
```bash
# 在Superset UI中导航到SQL Lab
# URL: http://localhost:8088/superset/sqllab
```

2. **基本查询执行**：
```sql
-- 简单查询测试连接
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

3. **保存和共享查询**：
```sql
-- 使用描述保存查询
-- 使用"保存查询"按钮
-- 添加元数据：标题、描述、标签
```

**参考文档**：
- [SQL Lab文档](https://superset.apache.org/docs/using-superset/sql-lab)
- [查询管理](https://superset.apache.org/docs/using-superset/sql-lab#saving-queries)

---

## 用户故事2：高级SQL技术

**标题**：实现复杂SQL查询

**描述**：使用窗口函数、CTE、子查询和复杂连接编写高级SQL查询，进行复杂的数据分析。

**验收标准**：
- 正确使用窗口函数
- CTE提高查询可读性
- 子查询得到优化
- 复杂连接高效运行
- 查询性能可接受

**分步指南**：

1. **窗口函数**：
```sql
-- 运行总计和排名
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

2. **公共表表达式(CTE)**：
```sql
-- 使用CTE进行复杂分析
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

3. **复杂连接**：
```sql
-- 带条件的多表连接
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

**参考文档**：
- [Superset中的高级SQL](https://superset.apache.org/docs/using-superset/sql-lab#advanced-sql)
- [查询优化](https://superset.apache.org/docs/using-superset/sql-lab#query-optimization)

---

## 用户故事3：查询性能优化

**标题**：优化SQL查询性能

**描述**：实施查询优化技术，包括索引、查询结构和执行计划分析。

**验收标准**：
- 查询在可接受时间内执行
- 分析执行计划
- 有效使用索引
- 优化查询结构
- 监控资源使用情况

**分步指南**：

1. **查询结构优化**：
```sql
-- 具有适当过滤的优化查询
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

2. **索引使用分析**：
```sql
-- 检查索引使用情况
EXPLAIN ANALYZE
SELECT 
    customer_id,
    SUM(sales_amount) as total_spent
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY customer_id
HAVING SUM(sales_amount) > 1000;
```

3. **查询计划优化**：
```sql
-- 对于复杂查询使用物化视图
CREATE MATERIALIZED VIEW monthly_sales_summary AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_category,
    SUM(sales_amount) as total_sales,
    COUNT(*) as order_count
FROM sales_data
GROUP BY DATE_TRUNC('month', order_date), product_category;
```

**参考文档**：
- [查询性能](https://superset.apache.org/docs/installation/performance-tuning)
- [数据库优化](https://superset.apache.org/docs/installation/performance-tuning#database-optimization)

---

## 用户故事4：数据探索与分析

**标题**：进行全面的数据探索

**描述**：使用SQL Lab进行探索性数据分析，包括数据画像、统计分析和数据质量检查。

**验收标准**：
- 全面的数据画像
- 准确的统计分析
- 识别数据质量问题
- 记录洞察结果
- 分析可重现

**分步指南**：

1. **数据画像**：
```sql
-- 全面的数据画像
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

2. **统计分析**：
```sql
-- 按类别进行统计分析
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

3. **数据质量检查**：
```sql
-- 识别数据质量问题
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

**参考文档**：
- [数据探索](https://superset.apache.org/docs/using-superset/sql-lab#data-exploration)
- [统计分析](https://superset.apache.org/docs/using-superset/sql-lab#statistical-analysis)

---

## 用户故事5：查询模板和最佳实践

**标题**：创建可重用的查询模板

**描述**：开发查询模板并为常见的分析任务和报告建立最佳实践。

**验收标准**：
- 创建查询模板
- 记录最佳实践
- 模板可重用
- 遵循性能指南
- 代码有良好文档

**分步指南**：

1. **销售分析模板**：
```sql
-- 模板: 月度销售分析
-- 参数: @start_date, @end_date, @category_filter
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

2. **客户细分模板**：
```sql
-- 模板: 按消费细分客户
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
        WHEN total_spent >= 10000 THEN '高价值'
        WHEN total_spent >= 5000 THEN '中等价值'
        ELSE '低价值'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_spent,
    AVG(order_count) as avg_orders
FROM customer_totals
GROUP BY customer_segment
ORDER BY avg_spent DESC;
```

3. **最佳实践文档**：
```markdown
# SQL Lab最佳实践

## 查询结构
- 使用CTE处理复杂查询
- 尽早使用WHERE子句限制结果
- 使用适当的索引
- 在生产环境中避免SELECT *

## 性能
- 使用EXPLAIN ANALYZE测试查询
- 对大型结果集使用LIMIT
- 考虑对频繁查询使用物化视图
- 监控查询执行时间

## 文档
- 为复杂查询添加注释
- 记录参数用法
- 包含查询目的和预期结果
- 对重要查询进行版本控制
```

**参考文档**：
- [SQL最佳实践](https://superset.apache.org/docs/using-superset/sql-lab#best-practices)
- [查询模板](https://superset.apache.org/docs/using-superset/sql-lab#templates)

---

## 总结

SQL Lab关键概念总结：
- **界面掌握**：导航、执行、保存
- **高级SQL**：窗口函数、CTE、复杂连接
- **性能**：优化、索引、执行计划
- **数据探索**：数据画像、统计、质量检查
- **模板**：可重用查询、最佳实践

**下一步**：
- 练习高级SQL技术
- 优化查询性能
- 创建可重用模板
- 记录最佳实践
- 使用复杂查询探索数据

**下一步学习**：
- [第8天：数据源连接与配置](./day08-data-connections.md)