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
| `field_sync_version` | String | Yes | Timestamp of last successful sync | `2023-11-15T12:00:00Z` |
| `table_versions` | Object | Yes | Version tracking for schema changes | `{"table": "version"}` |

**Implementation:**
1. Configuration is done via Dataset > Settings > Extra
2. No UI changes required - uses existing configuration interface
3. Supports automatic schema version tracking
4. Enables programmatic configuration via API

### 2.2. Core Feature: Dynamic Field Synchronization
To maintain column metadata automatically without UI changes, we implement an automatic synchronization system:

#### 2.2.1 Sync Triggers
| Method | Trigger | Use Case |
|--------|---------|----------|
| **Auto Sync** | Dataset save with star schema config | Initial setup and updates |
| **Background Sync** | Periodic schema check (configurable interval) | Production monitoring |
| **Lazy Sync** | First dataset access after schema change | Development environments |

#### 2.2.2 Sync Process
```python
class StarSchemaManager:
    def sync_columns(self, dataset):
        config = dataset.extra.get("star_schema")
        if not config or not self.needs_sync(dataset):
            return False
            
        # Preserve user customizations
        custom_columns = [c for c in dataset.columns 
                         if not c.get("managed_by_star_schema")]
        
        # Get columns from all tables
        all_columns = []
        tables = [config["fact_table"]] + [
            dim["table_name"] for dim in config["dimension_tables"]
        ]
        
        for table in tables:
            for col in self._get_table_columns(table):
                all_columns.append({
                    "column_name": f"{table}.{col.name}",
                    "verbose_name": f"{table.split('.')[-1]}_{col.name}",
                    "type": col.type,
                    "is_fact": (table == config["fact_table"]),
                    "managed_by_star_schema": True,
                    "source_table": table
                })
        
        # Update dataset
        dataset.columns = custom_columns + all_columns
        self._update_sync_version(dataset)
        return True

    def needs_sync(self, dataset):
        config = dataset.extra.get("star_schema", {})
        current_versions = self._get_table_versions(dataset)
        last_versions = config.get("table_versions", {})
        return current_versions != last_versions
```

#### 2.2.3 Performance Optimizations
1. **Caching**: Table schemas cached with 1-hour TTL
2. **Differential Sync**: Only sync changed tables
3. **Background Processing**: Async tasks for non-urgent syncs

### 2.3. Core Feature: Intelligent Query Generation Engine
This is the technical core of the project. The query generator uses the virtual columns from the dataset metadata to generate efficient SQL.

**SQL Generation Rules (Pseudocode Logic):**
```python
class StarSchemaQueryGenerator:
    def generate_pivot_sql(self, dataset, metrics, rows, columns, filters):
        config = dataset.extra["star_schema"]
        fact_table = config["fact_table"]
        
        # 1. Parse fields using column metadata
        fact_metrics = []
        fact_group_bys = []
        dim_group_bys = []
        fact_filters = []
        dim_filters = []
        
        # Helper to get column metadata
        def get_column_info(field):
            col = dataset.columns[field.column_name]
            return {
                "physical_table": col.source_table,
                "physical_column": col.column_name.split(".")[-1],
                "is_fact": col.is_fact
            }
        
        # Categorize metrics
        for metric in metrics:
            col_info = get_column_info(metric)
            if col_info["is_fact"]:
                fact_metrics.append({
                    "expression": metric.expression,
                    "column": col_info["physical_column"],
                    "alias": metric.alias
                })
        
        # Categorize dimensions (rows + columns)
        for field in rows + columns:
            col_info = get_column_info(field)
            if col_info["is_fact"]:
                fact_group_bys.append(col_info["physical_column"])
            else:
                dim_group_bys.append({
                    "table": col_info["physical_table"],
                    "column": col_info["physical_column"],
                    "alias": field.alias
                })
        
        # Categorize filters
        for filter in filters:
            col_info = get_column_info(filter)
            filter_obj = {
                "column": col_info["physical_column"],
                "operator": filter.operator,
                "value": filter.value
            }
            if col_info["is_fact"]:
                fact_filters.append(filter_obj)
            else:
                dim_filters.append({
                    **filter_obj,
                    "table": col_info["physical_table"]
                })

        # 2. Build CTE for fact table aggregation
        fact_subquery = f"""
        SELECT
            {', '.join(fact_group_bys)},
            {', '.join(f"{m['expression']}({m['column']}) AS {m['alias']}" 
                      for m in fact_metrics)}
        FROM {fact_table}
        WHERE 1=1
            {self._build_filters(fact_filters)}
        GROUP BY {', '.join(fact_group_bys)}
        """

        # 3. Build main query with dimension joins
        main_query = f"""
        WITH fact_agg AS ({fact_subquery})
        SELECT
            {', '.join([
                f"{d['table']}.{d['column']} AS {d['alias']}" 
                for d in dim_group_bys
            ] + [
                f"fact_agg.{m['alias']}" for m in fact_metrics
            ])}
        FROM fact_agg
        {self._build_joins(config['dimension_tables'], dim_group_bys)}
        WHERE 1=1
            {self._build_filters(dim_filters)}
        """

        return main_query

    def _build_joins(self, dimension_tables, needed_dims):
        # Build only necessary joins based on used dimensions
        needed_tables = {d["table"] for d in needed_dims}
        joins = []
        
        for dim in dimension_tables:
            if dim["table_name"] in needed_tables:
                joins.append(
                    f"{dim['join_type']} JOIN {dim['table_name']} ON " +
                    " AND ".join(
                        f"fact_agg.{jc['fact_column']} = "
                        f"{dim['table_name']}.{jc['dimension_column']}"
                        for jc in dim["join_conditions"]
                    )
                )
        
        return "\n".join(joins)

    def _build_filters(self, filters):
        if not filters:
            return ""
            
        conditions = []
        for f in filters:
            table = f.get("table", "fact_agg")
            conditions.append(
                f"AND {table}.{f['column']} {f['operator']} {f['value']}"
            )
            
        return "\n".join(conditions)
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

1.  **Dataset编辑界面**：增加一个“Star Schema Model”配置标签页，用于2.1节描述的配置。
2.  **Explore / Chart界面**：**零变更**。这是本设计的核心优势——高级功能在后台完成，前端用户享受简单一致的体验。

### 5. 后续可选增强 (Future Enhancements)

1.  **自动关联探测**：提供功能自动推测事实表和维度表之间的潜在关联关系。
2.  **雪花模型支持**：扩展配置以支持维度表再关联其他维度表（雪花模型）。
3.  **多事实表支持**：支持在单个Dataset中配置多个事实表（星座模型），但这会极大增加复杂性。
4.  **数据源扩展**：将优化逻辑适配到其他OLAP数据库，如Doris、StarRocks、Druid等。

---