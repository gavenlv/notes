# **Apache Superset Enhancement Specification: Intelligent Pivot Table for Star Schema Models**

## 1. Project Overview

### 1.1. Project Background
Apache Superset is a powerful open-source data visualization and business intelligence platform. However, when handling complex data models (such as star schema or snowflake schema commonly found in data warehouses), particularly for Pivot Table components, there are bottlenecks in user experience and performance.

Current Pivot Tables, when dealing with multi-table joins, either rely on users creating physical views or logical datasets (by writing SQL through SQL Lab), or use inefficient default join methods. This increases the barrier to entry for business users and may cause performance issues when processing massive datasets (such as with ClickHouse).

### 1.2. Project Objectives
This project aims to enhance Superset functionality with the core objective: **Enable users to seamlessly and efficiently use data based on star schema models in Pivot Tables through simple interface configuration, without writing any SQL**.

Specific objectives include:
1. **Simplified Configuration**: Allow administrators to pre-define fact tables, dimension tables, and their relationships in Dataset configuration.
2. **Intelligent Query Generation**: Backend can dynamically generate optimized SQL queries based on user's Pivot Table operations (dimensions, measures, filters).
3. **Query Performance Optimization**: Generated SQL must follow the best practice of "filter fact table first and aggregate, then join dimension tables", with specific optimizations for ClickHouse.
4. **Seamless User Experience**: For frontend users, the usage is identical to operating single-table Datasets, with all underlying complexity hidden.

## 2. Functional Requirements

### 2.1. Core Feature: Star Schema Configuration
Add a new configuration section (e.g., a tab) "Star Schema Model" in the Dataset editing interface.

| Field Name | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `fact_table` | String (dropdown) | Yes | Specify the physical table name as the fact table (main table). | `default.fact_sales` |
| `dimension_tables` | List of Objects | No | A list to configure all associated dimension tables. | |
| -> `table_name` | String (dropdown) | Yes | Physical table name of the dimension table. | `default.dim_customer` |
| -> `join_type` | Enum (dropdown) | Yes | Join type: `INNER`, `LEFT`, `RIGHT`, `FULL OUTER`. | `LEFT` |
| -> `join_conditions` | List of Objects | Yes | Define join conditions. | |
| --> `fact_column` | String (dropdown) | Yes | Join field in the fact table. | `customer_id` |
| --> `dimension_column` | String (dropdown) | Yes | Join field in the dimension table. | `id` |

**UI Interactions:**
1. Users first select `fact_table` from database and schema.
2. Click "Add Dimension Table" button to populate the above configuration for each dimension table.
3. Provide "Test Join" button to validate whether the configured join relationships are valid.

### 2.2. Core Feature: Dynamic Field Synchronization
To avoid the tedious work of manually defining all fields, an automation mechanism is needed.

| Feature | Description |
| :--- | :--- |
| **"Sync Fields" Button** | After saving the "Star Schema Model" configuration, provide a button. When clicked, the system backend performs the following operations: |
| **Backend Operations** | 1. Execute a **predefined SQL** (or database metadata query) to retrieve all column metadata (column names, data types) from the configured `fact_table` and all `dimension_tables`.<br>2. Sync all fields to the current Dataset's "Columns" list in the format `table_name.column_name` (or more readable aliases like `dimension_table_name_column_name`).<br>3. Automatically mark which fields come from fact tables (can be used for measures) and which come from dimension tables (can be used for rows, columns, filters). |
| **Result** | Users don't need to manually add any fields and can see all available dimensions and measures in the Explore interface field selector. |

### 2.3. Core Feature: Intelligent Query Generation Engine
This is the technical core of the project. When users drag fields, set filter conditions, and trigger queries in Pivot Table, the backend must generate efficient SQL.

**SQL Generation Rules (Pseudocode Logic):**
```python
# Input: User-selected metrics, rows, columns, filters
def generate_pivot_sql(metrics, rows, columns, filters):
    # 1. Parse which table each field belongs to
    fact_metrics = [m for m in metrics if m.table == fact_table]
    fact_group_bys = [] # Group fields from fact table (usually Degenerate Dimensions, like order_id)
    dim_group_bys = []  # Group fields from dimension tables (like customer_name, product_category)
    fact_filters = []   # Filter conditions on fact table (like sales_date, amount)
    dim_filters = []    # Filter conditions on dimension tables (like customer_region, product_name)

    for field in rows + columns:
        if field.table == fact_table:
            fact_group_bys.append(field)
        else:
            dim_group_bys.append(field.qualified_name) # Need to join before SELECT

    for filter in filters:
        if filter.column.table == fact_table:
            fact_filters.append(filter)
        else:
            dim_filters.append(filter)

    # 2. Build CTE or subquery: efficiently process fact table first
    fact_subquery = f"""
    SELECT
        {', '.join([f.column_name for f in fact_group_bys])},   -- Group fields from fact table
        {', '.join([m.expression for m in fact_metrics])}      -- Aggregated measures
    FROM {fact_table} f
    WHERE 1=1
        {build_where_clause(fact_filters)} -- Apply fact table filter conditions
    GROUP BY {', '.join([f.column_name for f in fact_group_bys])}
    """

    # 3. Main query: join aggregated results with dimension tables
    main_query = f"""
    WITH fact_agg AS ({fact_subquery})
    SELECT
        {', '.join(dim_group_bys + [f"fact_agg.{m.alias}" for m in metrics])}
    FROM fact_agg
    {build_join_clause(dimension_tables, dim_group_bys)} -- Only join needed dimension tables
    WHERE 1=1
        {build_where_clause(dim_filters)} -- Apply dimension table filters (efficient at this point because fact table is already aggregated)
    """

    return main_query
```

#### 2.4. ClickHouse Optimization
When generating SQL, it's necessary to identify ClickHouse as the data source and apply specific optimizations:

1.  **Use `ANY` Join**: When joining dimension tables, if it's determined that the join key in the dimension table is unique, use `LEFT ANY JOIN`. This can avoid multiplication issues in ClickHouse when there are duplicates in the right table, significantly improving performance.
    *   `sql LEFT ANY JOIN dim_table ON fact_agg.dim_id = dim_table.id`
2.  **Pre-process dimension filters**: For complex dimension table filter conditions, consider filtering and deduplicating dimension tables in a CTE first, then joining with the aggregated fact results, but this increases complexity. Priority should be given to the main logic above, as the data volume is already significantly reduced after fact table aggregation.
3.  **Engine-specific functions**: Ensure that the generated aggregation functions (such as `sum`, `count`) use ClickHouse's native syntax.

### 3. Non-Functional Requirements

1.  **Backward Compatibility**: This feature should be optional. Existing single-table Datasets and SQL query-based Datasets must remain completely unaffected.
2.  **Performance**: The performance of generated SQL queries should be significantly better than or equivalent to manually written optimized SQL. For fact tables with hundreds of millions of records, query response time should be within an acceptable range (e.g., within 30 seconds).
3.  **Security**: Inherit Superset's existing row-level security (RLS) and permission controls. This feature must not introduce SQL injection vulnerabilities; all table names and column names must undergo strict escaping or whitelist validation.
4.  **Error Handling**: Configuration errors (such as invalid join conditions) should have clear, user-friendly frontend error messages.

### 4. User Interface (UI/UX) Changes

1.  **Dataset Editing Interface**: Add a "Star Schema Model" configuration tab for the configuration described in section 2.1.
2.  **Explore / Chart Interface**: **Zero changes**. This is the core advantage of this design—advanced functionality is completed in the backend, while frontend users enjoy a simple and consistent experience.

### 5. Future Enhancements

1.  **Automatic Relationship Detection**: Provide functionality to automatically infer potential relationships between fact tables and dimension tables.
2.  **Snowflake Schema Support**: Extend configuration to support dimension tables joining other dimension tables (snowflake model).
3.  **Multiple Fact Table Support**: Support configuring multiple fact tables in a single Dataset (constellation model), but this would greatly increase complexity.
4.  **Data Source Extension**: Adapt optimization logic to other OLAP databases such as Doris, StarRocks, Druid, etc.

---