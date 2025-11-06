# 第6天：图表和可视化

## 用户故事1：创建基本图表

**标题**：构建基础图表类型

**描述**：学习创建基本图表类型，包括条形图、折线图和饼图，以有效可视化数据。

**验收标准**：
- 条形图显示分类数据
- 折线图显示时间序列数据
- 饼图表示比例
- 图表具有响应性和交互性
- 数据格式正确

**分步指南**：

1. **创建条形图**：
```sql
-- 条形图的示例查询
SELECT 
    product_category,
    SUM(sales_amount) as total_sales
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY product_category
ORDER BY total_sales DESC
```

2. **配置图表设置**：
```json
{
  "viz_type": "bar",
  "metrics": ["SUM(sales_amount)"],
  "columns": ["product_category"],
  "x_axis_label": "产品类别",
  "y_axis_label": "总销售额"
}
```

3. **折线图配置**：
```sql
-- 时间序列数据
SELECT 
    DATE(order_date) as date,
    SUM(sales_amount) as daily_sales
FROM sales_data
WHERE order_date >= '2023-01-01'
GROUP BY DATE(order_date)
ORDER BY date
```

**参考文档**：
- [Superset图表类型](https://superset.apache.org/docs/creating-charts-dashboards)
- [图表配置指南](https://superset.apache.org/docs/creating-charts-dashboards/chart-types)

---

## 用户故事2：高级图表类型

**标题**：实现高级可视化

**描述**：创建高级图表类型，包括散点图、热力图和气泡图，用于复杂数据分析。

**验收标准**：
- 散点图显示变量间的相关性
- 热力图有效显示矩阵数据
- 气泡图表示三个维度
- 图表包含适当的图例和工具提示

**分步指南**：

1. **散点图设置**：
```sql
-- 相关性分析
SELECT 
    customer_age,
    order_value,
    COUNT(*) as frequency
FROM customer_orders
WHERE order_date >= '2023-01-01'
```

2. **热力图配置**：
```sql
-- 热力图的矩阵数据
SELECT 
    product_category,
    region,
    SUM(sales_amount) as total_sales
FROM sales_data
GROUP BY product_category, region
```

3. **气泡图查询**：
```sql
-- 三维数据
SELECT 
    country,
    SUM(population) as total_population,
    AVG(gdp_per_capita) as avg_gdp,
    COUNT(*) as city_count
FROM world_cities
GROUP BY country
```

**参考文档**：
- [高级图表类型](https://superset.apache.org/docs/creating-charts-dashboards/chart-types)
- [图表定制](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization)

---

## 用户故事3：图表定制

**标题**：定制图表外观和行为

**描述**：配置图表外观、颜色、字体和交互功能，以创建专业的可视化效果。

**验收标准**：
- 图表使用一致的配色方案
- 字体清晰专业
- 交互功能正常工作
- 图表具有可访问性

**分步指南**：

1. **颜色配置**：
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

2. **字体和排版**：
```json
{
  "font_size": 12,
  "font_family": "Arial, sans-serif",
  "title_font_size": 16,
  "axis_font_size": 10
}
```

3. **交互功能**：
```json
{
  "enable_tooltip": true,
  "enable_legend": true,
  "enable_zoom": true,
  "enable_pan": true
}
```

**参考文档**：
- [图表样式指南](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization)
- [配色方案](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization#colors)

---

## 用户故事4：图表性能优化

**标题**：优化图表性能

**描述**：实现图表性能优化，包括数据采样、缓存和查询优化。

**验收标准**：
- 大数据集快速渲染
- 图表使用适当的数据采样
- 实现缓存
- 查询已优化

**分步指南**：

1. **数据采样配置**：
```python
# superset_config.py
SAMPLES_ROW_LIMIT = 1000
SAMPLES_ROW_LIMIT_BY_ENGINE = {
    'postgresql': 1000,
    'mysql': 1000,
    'bigquery': 1000
}
```

2. **查询优化**：
```sql
-- 带有适当索引的优化查询
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

3. **缓存配置**：
```python
# superset_config.py
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_charts_'
}
```

**参考文档**：
- [性能优化](https://superset.apache.org/docs/installation/performance-tuning)
- [缓存配置](https://superset.apache.org/docs/installation/performance-tuning#caching)

---

## 用户故事5：图表模板和可重用性

**标题**：创建可重用的图表模板

**描述**：构建可在不同数据集和仪表板中重用的图表模板和配置。

**验收标准**：
- 创建图表模板
- 模板可应用于不同数据
- 配置一致
- 模板有文档记录

**分步指南**：

1. **创建图表模板**：
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

2. **将模板应用于新数据**：
```sql
-- 将模板应用于不同数据集
SELECT 
    department,
    SUM(budget) as total_budget
FROM budget_data
GROUP BY department
ORDER BY total_budget DESC
```

3. **模板文档**：
```markdown
# 销售摘要模板
- 图表类型: 条形图
- 指标: SUM of sales_amount
- 列: product_category
- 用例: 按类别分析销售情况
```

**参考文档**：
- [图表模板](https://superset.apache.org/docs/creating-charts-dashboards/chart-templates)
- [可重用组件](https://superset.apache.org/docs/creating-charts-dashboards/chart-customization)

---

## 总结

涵盖的关键图表概念：
- **基本图表**：条形图、折线图、饼图
- **高级图表**：散点图、热力图、气泡图
- **定制**：颜色、字体、交互性
- **性能**：采样、缓存、优化
- **模板**：可重用配置

**下一步**：
- 练习创建不同类型的图表
- 尝试定制选项
- 测试大数据集的性能
- 为常见用例创建图表模板

**下一步学习**：
- [第7天：SQL Lab与高级查询](./day07-sql-lab.md)