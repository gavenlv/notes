# 第五章：数据集创建与配置

## 5.1 什么是数据集？

在 Apache Superset 中，数据集（Dataset）是对数据源的抽象表示，它是连接原始数据和可视化图表的桥梁。数据集不仅包含了数据源的基本信息，还定义了数据的结构、字段类型、计算指标以及业务含义。

### 数据集与数据源的区别

- **数据源（Datasource）**：指的是实际的数据库表或 SQL 查询结果，是数据的物理存储
- **数据集（Dataset）**：是在数据源基础上的逻辑抽象，包含了更多的元数据和业务定义

### 数据集的作用

1. **语义层抽象**：隐藏底层数据源的复杂性，为用户提供简化的数据视图
2. **字段定义**：明确定义每个字段的类型、格式和业务含义
3. **指标计算**：预定义常用的计算指标，简化图表创建过程
4. **权限控制**：实现列级别和行级别的数据访问控制
5. **性能优化**：通过缓存和预计算提高查询性能

## 5.2 创建数据集

### 方法一：从数据库表创建

1. 进入 **Data** → **Database Connections**
2. 选择相应的数据库
3. 找到目标表，点击表名进入表详情页面
4. 点击右上角的 **Edit Dataset** 按钮
5. 系统会自动创建基于该表的数据集

### 方法二：从 SQL 查询创建

1. 进入 **Data** → **Database Connections**
2. 选择相应的数据库
3. 点击 **+ sign** 图标创建新的虚拟数据集
4. 输入数据集名称
5. 编写 SQL 查询语句
6. 点击 **Save** 保存

### 方法三：从 SQL Lab 创建

1. 在 SQL Lab 中编写并执行查询
2. 在查询结果页面，点击 **Explore** 按钮
3. 系统会自动创建基于该查询的数据集

## 5.3 数据集基本配置

### 数据集基本信息

在数据集编辑页面，可以配置以下基本信息：

- **Name**：数据集名称
- **Description**：数据集描述
- **Schema**：所属 schema（如果适用）
- **Table Name**：表名（如果是基于表的数据集）
- **SQL**：SQL 查询语句（如果是基于查询的数据集）
- **Owners**：数据集所有者

### 字段配置

字段是数据集的核心组成部分，每个字段都需要正确配置：

#### 字段类型

Superset 支持以下字段类型：

- **字符串类型**：VARCHAR, TEXT, STRING 等
- **数值类型**：INTEGER, BIGINT, DECIMAL, FLOAT 等
- **日期时间类型**：DATE, DATETIME, TIMESTAMP 等
- **布尔类型**：BOOLEAN
- **地理类型**：GEOMETRY, GEOGRAPHY

#### 字段属性

每个字段可以配置以下属性：

- **Column Name**：字段名称
- **Verbose Name**：字段显示名称
- **Description**：字段描述
- **Type**：字段类型
- **Group By**：是否可用于分组
- **Filterable**：是否可用于过滤
- **Is Dimension**：是否为维度字段
- **Is Temporal**：是否为时间字段

### 示例配置

假设我们有一个销售数据表，包含以下字段：

| 字段名 | 类型 | 描述 | 配置建议 |
|--------|------|------|----------|
| order_id | INTEGER | 订单ID | Group By: Yes, Filterable: Yes |
| customer_name | VARCHAR | 客户名称 | Group By: Yes, Filterable: Yes |
| product_name | VARCHAR | 产品名称 | Group By: Yes, Filterable: Yes |
| order_date | DATE | 订单日期 | Is Temporal: Yes, Group By: Yes |
| quantity | INTEGER | 数量 | Group By: No, Filterable: Yes |
| price | DECIMAL | 单价 | Group By: No, Filterable: Yes |
| total_amount | DECIMAL | 总金额 | Group By: No, Filterable: Yes |

## 5.4 指标配置

指标是预定义的计算公式，可以在创建图表时直接使用。

### 创建指标

1. 在数据集编辑页面，切换到 **Metrics** 标签页
2. 点击 **+ Add Item** 按钮
3. 配置指标信息：
   - **Metric Name**：指标名称
   - **Verbose Name**：指标显示名称
   - **Description**：指标描述
   - **Expression**：计算表达式
   - **D3 Format**：数字格式化

### 常用指标示例

#### 基础指标

```sql
-- 销售总额
SUM(total_amount)

-- 订单数量
COUNT(order_id)

-- 平均单价
AVG(price)

-- 客户数量
COUNT(DISTINCT customer_name)
```

#### 复杂指标

```sql
-- 利润率
(SUM(revenue) - SUM(cost)) / SUM(revenue) * 100

-- 同比增长率
(SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE) THEN total_amount ELSE 0 END) - 
 SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE) - 1 THEN total_amount ELSE 0 END)) / 
 SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE) - 1 THEN total_amount ELSE 0 END) * 100
```

### 指标格式化

通过 D3 Format 可以控制指标的显示格式：

- **货币格式**：$.2f （显示为 $1,234.56）
- **百分比格式**：.2% （显示为 12.34%）
- **数字格式**：,.0f （显示为 1,234）
- **小数格式**：.2f （显示为 1234.56）

## 5.5 时间字段配置

时间字段在 Superset 中具有特殊的重要性，因为它们支持时间序列分析和时间过滤。

### 时间字段识别

1. 在字段配置中，将相应的时间字段标记为 **Is Temporal**
2. 系统会自动识别时间字段，并在图表中提供时间相关的功能

### 时间粒度设置

Superset 支持多种时间粒度：

- **秒**：Second
- **分钟**：Minute
- **小时**：Hour
- **日**：Day
- **周**：Week
- **月**：Month
- **季度**：Quarter
- **年**：Year

### 时间范围过滤

在创建图表时，可以使用时间字段进行范围过滤：

- **Last 7 days**：最近7天
- **Last 30 days**：最近30天
- **Last quarter**：上一季度
- **Year to date**：年初至今
- **Custom**：自定义时间范围

## 5.6 数据集权限控制

### 列级别权限

可以控制用户能够访问哪些列：

1. 在数据集编辑页面，切换到 **Columns** 标签页
2. 选择需要限制的字段
3. 在 **Permission** 部分配置访问权限

### 行级别权限

可以控制用户能够看到哪些数据行：

1. 在数据集编辑页面，切换到 **Calculated Columns** 标签页
2. 创建计算列来实现行过滤逻辑
3. 通过安全规则控制数据访问

### 示例：基于部门的数据访问控制

```sql
-- 创建计算列 department_filter
CASE 
  WHEN '{{ current_username() }}' IN ('admin') THEN 1
  WHEN department = '{{ current_user().extra_attributes.department }}' THEN 1
  ELSE 0
END
```

## 5.7 数据集性能优化

### 缓存配置

1. **Cache Timeout**：设置查询结果缓存超时时间
2. **Cache Keys**：定义缓存键值，提高缓存命中率

### 查询优化

1. **索引优化**：确保常用查询字段有适当索引
2. **分区表**：对大表进行分区以提高查询性能
3. **物化视图**：对复杂查询结果创建物化视图

### 预聚合

对于大量数据的聚合查询，可以预先计算并存储聚合结果：

```sql
-- 创建预聚合表
CREATE TABLE sales_summary AS
SELECT 
  DATE_TRUNC('month', order_date) as month,
  product_category,
  SUM(total_amount) as total_sales,
  COUNT(order_id) as order_count
FROM sales
GROUP BY DATE_TRUNC('month', order_date), product_category;
```

## 5.8 数据集管理

### 数据集列表

在 **Data** → **Datasets** 页面可以查看所有数据集：

- **Dataset Name**：数据集名称
- **Owner**：所有者
- **Database**：所属数据库
- **Kind**：类型（物理表/虚拟数据集）
- **Modified**：最后修改时间

### 数据集搜索和过滤

可以通过以下条件搜索数据集：

- 名称关键字
- 所有者
- 数据库
- 类型

### 数据集导出和导入

Superset 支持数据集的导出和导入功能：

1. **导出**：将数据集配置导出为 YAML 文件
2. **导入**：从 YAML 文件导入数据集配置

## 5.9 最佳实践

### 命名规范

1. 使用有意义的名称，便于识别
2. 遵循统一的命名约定
3. 包含业务域信息

### 配置规范

1. 完整填写字段描述信息
2. 合理设置字段属性
3. 预定义常用指标
4. 配置适当的权限控制

### 性能优化

1. 合理使用缓存
2. 优化查询性能
3. 定期维护统计数据

## 5.10 小结

本章详细介绍了 Apache Superset 中数据集的创建与配置方法，包括数据集的基本概念、创建方式、字段配置、指标定义、时间字段处理、权限控制和性能优化等内容。数据集是 Superset 数据可视化的核心组件，合理的配置能够大大提高数据分析的效率和准确性。

在下一章中，我们将学习如何创建各种类型的图表和可视化效果。