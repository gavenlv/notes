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
Configuration will be stored in the dataset's `extra` field as JSON to avoid UI changes:

```json
{
  "star_schema": {
    "fact_table": "default.fact_sales",
    "dimension_tables": [
      {
        "table_name": "default.dim_customer",
        "join_type": "LEFT",
        "join_conditions": [
          {
            "fact_column": "customer_id",
            "dimension_column": "id"
          }
        ]
      }
    ]
  }
}
```

**Configuration Fields:**
| Field Name | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `fact_table` | String | Yes | Physical table name of the fact table | `default.fact_sales` |
| `dimension_tables` | List of Objects | No | List of dimension tables and their join configurations | |
| -> `table_name` | String | Yes | Physical table name of the dimension table | `default.dim_customer` |
| -> `join_type` | Enum | Yes | Join type: `INNER`, `LEFT`, `RIGHT`, `FULL OUTER` | `LEFT` |
| -> `join_conditions` | List of Objects | Yes | Join conditions between fact and dimension tables | |
| --> `fact_column` | String | Yes | Join field in the fact table | `customer_id` |
| --> `dimension_column` | String | Yes | Join field in the dimension table | `id` |

**Implementation:**
1. Configuration is done via Dataset > Settings > Extra
2. No UI changes required - uses existing configuration interface
3. After configuration, use "Sync Columns from Source" to populate dataset columns
4. Enables programmatic configuration via API

### 2.2. Core Feature: Enhanced Column Synchronization
Leverage existing Superset "Sync Columns from Source" functionality with star schema enhancement:

#### 2.2.1 Enhanced Sync Process
When user clicks "Sync Columns from Source" and star schema is configured:

```python
def sync_columns_from_source(dataset):
    """Enhanced column sync that handles star schema configuration"""
    
    # Standard single-table sync if no star schema config
    if "star_schema" not in dataset.extra:
        return standard_sync_columns(dataset)
    
    config = dataset.extra["star_schema"]
    all_columns = []
    
    # Get columns from fact table
    fact_table = config["fact_table"]
    fact_columns = get_table_columns(dataset.database, fact_table)
    
    for col in fact_columns:
        all_columns.append({
            "column_name": col.name,
            "verbose_name": f"fact_{col.name}",
            "type": col.type,
            "is_dttm": col.is_dttm,
            "groupby": True,
            "filterable": True,
            "description": f"From fact table: {fact_table}",
            "python_date_format": col.python_date_format,
            "source_table": fact_table,
            "is_fact_column": True
        })
    
    # Get columns from dimension tables
    for dim_config in config["dimension_tables"]:
        dim_table = dim_config["table_name"]
        dim_columns = get_table_columns(dataset.database, dim_table)
        
        for col in dim_columns:
            all_columns.append({
                "column_name": f"{dim_table.split('.')[-1]}_{col.name}",
                "verbose_name": f"{dim_table.split('.')[-1]}_{col.name}",
                "type": col.type,
                "is_dttm": col.is_dttm,
                "groupby": True,
                "filterable": True,
                "description": f"From dimension table: {dim_table}",
                "python_date_format": col.python_date_format,
                "source_table": dim_table,
                "is_fact_column": False
            })
    
    # Replace dataset columns
    dataset.columns = all_columns
    return len(all_columns)
```

#### 2.2.2 User Experience
1. **Configuration**: Admin sets up star schema in Dataset > Settings > Extra
2. **Column Sync**: User clicks existing "Sync Columns from Source" button
3. **Result**: All columns from fact + dimension tables appear in dataset
4. **Chart Creation**: Users see full list of pre-defined columns in Explore interface
5. **Transparent Usage**: Users create pivot tables without knowing the underlying table structure

#### 2.2.3 Column Naming Convention
- **Fact columns**: Use original name (e.g., `sales_amount`, `order_date`)
- **Dimension columns**: Prefixed with table name (e.g., `customer_name`, `product_category`)
- **Verbose names**: Human-readable descriptions for UI display
- **Metadata**: Each column retains source table information for query generation

### 2.3. Core Feature: Intelligent Query Generation Engine
The query generator uses the column metadata to determine physical table sources and generate efficient SQL.

**SQL Generation Rules (Pseudocode Logic):**
```python
def generate_pivot_sql(dataset, metrics, rows, columns, filters):
    """Generate optimized SQL for star schema pivot tables"""
    
    if "star_schema" not in dataset.extra:
        # Fall back to standard query generation
        return standard_generate_sql(dataset, metrics, rows, columns, filters)
    
    config = dataset.extra["star_schema"]
    fact_table = config["fact_table"]
    
    # 1. Categorize fields by source table using column metadata
    fact_metrics = []
    fact_dimensions = []
    dim_tables_needed = set()
    fact_filters = []
    dim_filters = []
    
    # Process metrics
    for metric in metrics:
        col = dataset.get_column(metric.column)
        if col.is_fact_column:
            fact_metrics.append({
                "expression": metric.expression,
                "column": col.column_name,
                "alias": metric.label
            })
    
    # Process dimensions (rows + columns)
    for field in rows + columns:
        col = dataset.get_column(field)
        if col.is_fact_column:
            fact_dimensions.append(col.column_name)
        else:
            dim_tables_needed.add(col.source_table)
    
    # Process filters
    for filter_obj in filters:
        col = dataset.get_column(filter_obj.column)
        if col.is_fact_column:
            fact_filters.append({
                "column": col.column_name,
                "operator": filter_obj.operator,
                "value": filter_obj.value
            })
        else:
            dim_filters.append({
                "table": col.source_table,
                "column": col.column_name.split('_', 1)[1],  # Remove table prefix
                "operator": filter_obj.operator,
                "value": filter_obj.value
            })
            dim_tables_needed.add(col.source_table)
    
    # 2. Build optimized query with fact aggregation first
    fact_select = fact_dimensions + [f"{m['expression']} AS {m['alias']}" for m in fact_metrics]
    fact_where = " AND ".join([f"{f['column']} {f['operator']} {f['value']}" for f in fact_filters])
    
    if fact_dimensions:
        fact_query = f"""
        SELECT {', '.join(fact_select)}
        FROM {fact_table}
        {f"WHERE {fact_where}" if fact_where else ""}
        GROUP BY {', '.join(fact_dimensions)}
        """
    else:
        fact_query = f"""
        SELECT {', '.join(fact_select)}
        FROM {fact_table}
        {f"WHERE {fact_where}" if fact_where else ""}
        """
    
    # 3. Add dimension joins only for needed tables
    if dim_tables_needed:
        joins = []
        for dim_config in config["dimension_tables"]:
            if dim_config["table_name"] in dim_tables_needed:
                join_conditions = " AND ".join([
                    f"fact_agg.{jc['fact_column']} = {dim_config['table_name']}.{jc['dimension_column']}"
                    for jc in dim_config["join_conditions"]
                ])
                joins.append(f"{dim_config['join_type']} JOIN {dim_config['table_name']} ON {join_conditions}")
        
        dim_where = " AND ".join([f"{f['table']}.{f['column']} {f['operator']} {f['value']}" for f in dim_filters])
        
        main_query = f"""
        WITH fact_agg AS ({fact_query})
        SELECT *
        FROM fact_agg
        {' '.join(joins)}
        {f"WHERE {dim_where}" if dim_where else ""}
        """
    else:
        main_query = fact_query
    
    return main_query
```

### 2.4. ClickHouse-Specific Optimizations
When generating SQL, identify ClickHouse as the data source and apply specific optimizations:

1. **Use `ANY` Join**: When joining dimension tables, if the join key in the dimension table is confirmed to be unique, use `LEFT ANY JOIN`. This avoids ClickHouse's multiplication problem when there are duplicates in the right table, significantly improving performance.
   *   `sql LEFT ANY JOIN dim_table ON fact_agg.dim_id = dim_table.id`
2. **Pre-filter Dimension Tables**: For complex dimension table filter conditions, consider filtering and deduplicating dimension tables in CTE first, then joining with fact aggregation results, but this increases complexity. Prioritize the main logic above because fact table aggregation already significantly reduces data volume.
3. **Engine-Specific Functions**: Ensure generated aggregate functions (like `sum`, `count`) use ClickHouse's native syntax.

## 3. Non-Functional Requirements

1. **Backward Compatibility**: This feature should be optional. Existing single-table Datasets and SQL query-based Datasets must be completely unaffected.
2. **Performance**: Generated SQL query performance should be significantly better than or equal to manually written optimized SQL. For fact tables with hundreds of millions of records, query response time should be within acceptable range (e.g., within 30 seconds).
3. **Security**: Inherit Superset's existing Row-Level Security (RLS) and permission controls. This feature must not introduce SQL injection vulnerabilities; all table names and column names must be strictly escaped or whitelist validated.
4. **Error Handling**: Configuration errors (such as invalid join conditions) should have clear, user-friendly frontend error messages.

## 4. User Interface (UI/UX) Changes

**Zero UI changes required**. This is the core advantage of this design:

1. **Configuration**: Uses existing Dataset > Settings > Extra field
2. **Column Sync**: Uses existing "Sync Columns from Source" button 
3. **Chart Creation**: Users see all columns in standard Explore interface
4. **User Experience**: Completely transparent - users don't need to know about underlying table structure

## 5. Future Enhancements

1. **Automatic Join Detection**: Provide functionality to automatically infer potential join relationships between fact tables and dimension tables.
2. **Snowflake Schema Support**: Extend configuration to support dimension tables joining other dimension tables (snowflake schema).
3. **Multi-Fact Table Support**: Support configuring multiple fact tables in a single Dataset (constellation schema), but this would greatly increase complexity.
4. **Data Source Extension**: Adapt optimization logic to other OLAP databases such as Doris, StarRocks, Druid, etc.

## 6. Implementation Summary

### 6.1. Simplified Design Benefits
1. **No Frontend Changes**: Leverages existing UI components (Extra field, Sync button)
2. **Familiar User Experience**: Uses standard Superset column sync workflow
3. **Reduced Complexity**: No version control or complex state management
4. **Easy Deployment**: Can be implemented as backend-only changes

### 6.2. Implementation Steps
1. **Phase 1**: Enhance `sync_columns_from_source()` function to detect star schema config
2. **Phase 2**: Modify query generation logic to use column metadata 
3. **Phase 3**: Add ClickHouse-specific optimizations
4. **Phase 4**: Testing and documentation

### 6.3. User Workflow
```
1. Admin configures star schema in Dataset > Settings > Extra
2. Admin clicks "Sync Columns from Source" 
3. All fact + dimension columns appear in dataset
4. End users create pivot tables normally in Explore view
5. Backend generates optimized star schema SQL automatically
```

---