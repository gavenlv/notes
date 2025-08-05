# Day 5: Building Dashboards

## User Story 1: Create Your First Dashboard

**Title**: As a business analyst, I want to create my first dashboard in Superset so that I can visualize data and share insights with stakeholders.

**Description**: 
Dashboards are the primary way to present data insights in Superset. They combine multiple charts and filters to create comprehensive data views.

**Acceptance Criteria**:
- [ ] Dashboard is created successfully
- [ ] At least one chart is added to the dashboard
- [ ] Dashboard is saved and accessible
- [ ] Dashboard can be shared with other users
- [ ] Dashboard loads data correctly

**Step-by-Step Guide**:

1. **Access Superset**
   - Open browser: http://localhost:8088
   - Login with admin credentials

2. **Create a New Dashboard**
   - Navigate to Dashboards → + Dashboard
   - Enter dashboard name: "Sales Overview"
   - Click "Save"

3. **Add a Chart**
   - Click "Add Chart" button
   - Select a dataset (e.g., "World Bank's Health Stats")
   - Choose chart type: "Bar Chart"
   - Configure metrics and dimensions
   - Click "Create Chart"

4. **Customize Dashboard**
   - Drag and drop charts to arrange layout
   - Add filters using the filter panel
   - Set dashboard properties (auto-refresh, etc.)

5. **Save and Share**
   - Click "Save" to persist changes
   - Use "Share" button to get dashboard URL
   - Set permissions for other users

**Reference Documents**:
- [Dashboard Creation Guide](https://superset.apache.org/docs/creating-charts-dashboards/creating-dashboards)
- [Dashboard Best Practices](https://superset.apache.org/docs/creating-charts-dashboards/dashboard-best-practices)

---

## User Story 2: Create Advanced Charts

**Title**: As a data analyst, I want to create advanced charts with complex visualizations so that I can present sophisticated data insights.

**Description**: 
Superset supports various chart types including time series, scatter plots, heatmaps, and custom visualizations to represent different data patterns.

**Acceptance Criteria**:
- [ ] Multiple chart types are created
- [ ] Charts display data correctly
- [ ] Interactive features work
- [ ] Charts are responsive
- [ ] Performance is acceptable

**Step-by-Step Guide**:

1. **Time Series Chart**
   ```
   Chart Type: Time Series
   Metrics: SUM(sales_amount)
   Time Column: order_date
   Time Range: Last 30 days
   Group By: product_category
   ```

2. **Scatter Plot**
   ```
   Chart Type: Scatter Plot
   X Axis: customer_age
   Y Axis: total_purchase_amount
   Size: purchase_frequency
   Color: customer_segment
   ```

3. **Heatmap**
   ```
   Chart Type: Heatmap
   X Axis: product_category
   Y Axis: region
   Metric: SUM(sales_amount)
   ```

4. **Advanced Features**
   - Enable "Show Values" for data labels
   - Configure color schemes
   - Set up drill-down capabilities
   - Add custom tooltips

**Reference Documents**:
- [Chart Types Reference](https://superset.apache.org/docs/creating-charts-dashboards/exploring-charts)
- [Advanced Chart Configuration](https://superset.apache.org/docs/creating-charts-dashboards/advanced-chart-configuration)

---

## User Story 3: Implement Dashboard Filters

**Title**: As a dashboard creator, I want to add interactive filters to my dashboard so that users can explore data dynamically.

**Description**: 
Filters allow users to interact with dashboards by selecting specific data subsets, making dashboards more useful and engaging.

**Acceptance Criteria**:
- [ ] Filters are added to dashboard
- [ ] Filters work across all charts
- [ ] Filter values are populated correctly
- [ ] Filters update charts in real-time
- [ ] Filter state is preserved

**Step-by-Step Guide**:

1. **Add Native Filters**
   - Open dashboard in edit mode
   - Click "Add Filter" button
   - Select filter type: "Native Filter"
   - Choose column: "product_category"
   - Configure filter options

2. **Configure Filter Properties**
   ```
   Filter Type: Single Select
   Default Value: All
   Search: Enabled
   Sort: Alphabetical
   ```

3. **Add Cross-Filters**
   - Enable "Cross-Filtering" feature
   - Configure which charts respond to filters
   - Set up filter dependencies

4. **Advanced Filter Types**
   - Date Range Filter
   - Numeric Range Filter
   - Text Search Filter
   - Custom SQL Filter

**Reference Documents**:
- [Native Filters Guide](https://superset.apache.org/docs/creating-charts-dashboards/native-filters)
- [Cross-Filtering](https://superset.apache.org/docs/creating-charts-dashboards/cross-filtering)

---

## User Story 4: Create SQL Lab Queries

**Title**: As a SQL developer, I want to use SQL Lab to write and test complex queries so that I can create custom datasets for dashboards.

**Description**: 
SQL Lab provides a powerful interface for writing, testing, and saving SQL queries that can be used as data sources for charts and dashboards.

**Acceptance Criteria**:
- [ ] SQL Lab interface is accessible
- [ ] Queries execute successfully
- [ ] Results are displayed correctly
- [ ] Queries can be saved
- [ ] Saved queries can be used in charts

**Step-by-Step Guide**:

1. **Access SQL Lab**
   - Navigate to SQL Lab → SQL Editor
   - Select database connection
   - Choose schema/database

2. **Write a Query**
   ```sql
   SELECT 
       product_category,
       SUM(sales_amount) as total_sales,
       COUNT(*) as order_count,
       AVG(sales_amount) as avg_order_value
   FROM sales_data
   WHERE order_date >= '2023-01-01'
   GROUP BY product_category
   ORDER BY total_sales DESC
   ```

3. **Execute and Test**
   - Click "Run" button
   - Review results
   - Check query performance
   - Optimize if needed

4. **Save and Use Query**
   - Click "Save" to store query
   - Name: "Product Sales Summary"
   - Use as data source for charts

**Reference Documents**:
- [SQL Lab Guide](https://superset.apache.org/docs/using-superset/sql-lab)
- [SQL Best Practices](https://superset.apache.org/docs/using-superset/sql-lab-best-practices)

---

## User Story 5: Create Scheduled Reports

**Title**: As a business user, I want to set up scheduled reports so that stakeholders receive regular updates automatically.

**Description**: 
Superset can automatically generate and send reports via email on a scheduled basis, ensuring stakeholders stay informed without manual intervention.

**Acceptance Criteria**:
- [ ] Report is created from dashboard
- [ ] Schedule is configured
- [ ] Email recipients are set
- [ ] Reports are sent automatically
- [ ] Report format is correct

**Step-by-Step Guide**:

1. **Create Report from Dashboard**
   - Open dashboard
   - Click "Schedule" button
   - Select "Create Report"

2. **Configure Report Settings**
   ```
   Report Name: Weekly Sales Summary
   Schedule: Every Monday at 9:00 AM
   Format: PDF
   Recipients: sales-team@company.com
   ```

3. **Set Up Email Configuration**
   - Ensure SMTP is configured in superset_config.py
   - Test email delivery
   - Configure email templates

4. **Monitor Report Delivery**
   - Check report logs
   - Verify email delivery
   - Monitor report performance

**Reference Documents**:
- [Scheduled Reports](https://superset.apache.org/docs/using-superset/scheduled-reports)
- [Email Configuration](https://superset.apache.org/docs/installation/configuring-superset#email)

---

## Dashboard Best Practices

### 1. Performance Optimization
- Use appropriate chart types for data size
- Implement query caching
- Limit data points in charts
- Use database-level aggregations

### 2. User Experience
- Keep dashboards focused on specific use cases
- Use consistent color schemes
- Provide clear titles and descriptions
- Add helpful tooltips

### 3. Data Quality
- Validate data sources
- Handle missing data appropriately
- Use consistent date formats
- Implement data refresh schedules

### 4. Security
- Apply row-level security filters
- Limit user access to sensitive data
- Audit dashboard usage
- Regular permission reviews

## Next Steps

After completing dashboard creation, proceed to:
- [Day 6: Creating Charts & Visualizations](../day6-charts/charts.md)
- [Day 7: SQL Lab & Query Building](../day7-sql-lab/sql-lab.md) 