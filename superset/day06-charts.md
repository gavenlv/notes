# Day 6: Charts & Visualizations

## User Story 1: Create Basic Charts

**Title**: Build Fundamental Chart Types

**Description**: Learn to create basic chart types including bar charts, line charts, and pie charts to visualize data effectively.

**Acceptance Criteria**:
- Bar chart displays categorical data
- Line chart shows time series data
- Pie chart represents proportions
- Charts are responsive and interactive
- Data is properly formatted

**Step-by-Step Guide**:

1. **Create Bar Chart**:
```sql
-- Sample query for bar chart
SELECT 
    product_category,
    SUM(sales_amount) as total_sales
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY product_category
ORDER BY total_sales DESC
```

2. **Configure Chart Settings**:
```json
{
  "viz_type": "bar",
  "metrics": ["SUM(sales_amount)"],
  "columns": ["product_category"],
  "x_axis_label": "Product Category",
  "y_axis_label": "Total Sales"
}
```

3. **Line Chart Configuration**:
```sql
-- Time series data
SELECT 
    DATE(order_date) as date,
    SUM(sales_amount) as daily_sales
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY DATE(order_date)
ORDER BY date
```

**Reference Documents**:
- [Superset Chart Types](https://superset.apache.org/docs/creating-charts-dashboards)
- [Chart Configuration Guide](https://superset.apache.org/docs/creating-charts-dashboards/chart-types)

---

## User Story 2: Advanced Chart Types

**Title**: Implement Advanced Visualizations

**Description**: Create advanced chart types including scatter plots, heatmaps, and bubble charts for complex data analysis.

**Acceptance Criteria**:
- Scatter plot shows correlation between variables
- Heatmap displays matrix data effectively
- Bubble chart represents three dimensions
- Charts include proper legends and tooltips

**Step-by-Step Guide**:

1. **Scatter Plot Setup**:
```sql
-- Correlation analysis
SELECT 
    customer_age,
    order_value,
    COUNT(*) as frequency
FROM customer_orders
WHERE order_date >= '2023-01-01'
```

2. **Heatmap Configuration**:
```sql
-- Matrix data for heatmap
SELECT 
    product_category,
    region,
    SUM(sales_amount) as total_sales
FROM sales_data
GROUP BY product_category, region
```

3. **Bubble Chart Query**:
```sql
-- Three-dimensional data
SELECT 
    country,
    SUM(population) as total_population,
    AVG(gdp_per_capita) as avg_gdp,
    COUNT(*) as city_count
FROM world_cities
GROUP BY country
```

**Reference Documents**:
- [Advanced Chart Types](https://superset.apache.org/docs/creating-charts-dashboards/chart-types)
- [Chart Customization](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization)

---

## User Story 3: Chart Customization

**Title**: Customize Chart Appearance and Behavior

**Description**: Configure chart appearance, colors, fonts, and interactive features to create professional visualizations.

**Acceptance Criteria**:
- Charts use consistent color schemes
- Fonts are readable and professional
- Interactive features work properly
- Charts are accessible

**Step-by-Step Guide**:

1. **Color Configuration**:
```json
{
  "color_scheme": "supersetColors",
  "custom_colors": {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c"
  }
}
```

2. **Font and Typography**:
```json
{
  "font_size": 12,
  "font_family": "Arial, sans-serif",
  "title_font_size": 16,
  "axis_font_size": 10
}
```

3. **Interactive Features**:
```json
{
  "enable_tooltip": true,
  "enable_legend": true,
  "enable_zoom": true,
  "enable_pan": true
}
```

**Reference Documents**:
- [Chart Styling Guide](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization)
- [Color Schemes](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization#colors)

---

## User Story 4: Chart Performance Optimization

**Title**: Optimize Chart Performance

**Description**: Implement performance optimizations for charts including data sampling, caching, and query optimization.

**Acceptance Criteria**:
- Large datasets render quickly
- Charts use appropriate data sampling
- Caching is implemented
- Queries are optimized

**Step-by-Step Guide**:

1. **Data Sampling Configuration**:
```python
# superset_config.py
SAMPLES_ROW_LIMIT = 1000
SAMPLES_ROW_LIMIT_BY_ENGINE = {
    'postgresql': 1000,
    'mysql': 1000,
    'bigquery': 1000
}
```

2. **Query Optimization**:
```sql
-- Optimized query with proper indexing
SELECT 
    product_category,
    SUM(sales_amount) as total_sales
FROM sales_data
WHERE order_date >= '2023-01-01'
  AND order_date < '2024-01-01'
GROUP BY product_category
ORDER BY total_sales DESC
LIMIT 20
```

3. **Caching Configuration**:
```python
# superset_config.py
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_charts_'
}
```

**Reference Documents**:
- [Performance Optimization](https://superset.apache.org/docs/installation/performance-tuning)
- [Caching Configuration](https://superset.apache.org/docs/installation/performance-tuning#caching)

---

## User Story 5: Chart Templates and Reusability

**Title**: Create Reusable Chart Templates

**Description**: Build chart templates and configurations that can be reused across different datasets and dashboards.

**Acceptance Criteria**:
- Chart templates are created
- Templates can be applied to different data
- Configuration is consistent
- Templates are documented

**Step-by-Step Guide**:

1. **Create Chart Template**:
```json
{
  "template_name": "sales_summary",
  "chart_type": "bar",
  "default_config": {
    "metrics": ["SUM(sales_amount)"],
    "columns": ["product_category"],
    "color_scheme": "supersetColors",
    "enable_tooltip": true
  }
}
```

2. **Apply Template to New Data**:
```sql
-- Apply template to different dataset
SELECT 
    department,
    SUM(budget) as total_budget
FROM budget_data
GROUP BY department
ORDER BY total_budget DESC
```

3. **Template Documentation**:
```markdown
# Sales Summary Template
- Chart Type: Bar Chart
- Metrics: SUM of sales_amount
- Columns: product_category
- Use Case: Sales analysis by category
```

**Reference Documents**:
- [Chart Templates](https://superset.apache.org/docs/creating-charts-dashboards/chart-templates)
- [Reusable Components](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization)

---

## Summary

Key chart concepts covered:
- **Basic Charts**: Bar, line, pie charts
- **Advanced Charts**: Scatter, heatmap, bubble charts
- **Customization**: Colors, fonts, interactivity
- **Performance**: Sampling, caching, optimization
- **Templates**: Reusable configurations

**Next Steps**:
- Practice creating different chart types
- Experiment with customization options
- Test performance with large datasets
- Create chart templates for common use cases 