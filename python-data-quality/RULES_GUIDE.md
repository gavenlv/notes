# 数据质量规则使用指南

## 规则类型概览

本框架支持多种数据质量规则类型，每种类型针对不同的数据质量问题：

### 1. 完整性检查规则 (Completeness Rules)
**用途**：检查数据字段的完整性和非空性

**适用场景**：
- 主键字段完整性验证
- 关键业务字段非空检查
- 必填字段数据完整性

**示例配置**：
```yaml
- name: "用户表主键完整性"
type: "completeness"
table: "users"
column: "user_id"
description: "检查用户ID主键字段的完整性"
enabled: true
threshold: 0.99  # 允许1%的缺失率
```

### 2. 准确性检查规则 (Accuracy Rules)
**用途**：验证数据格式、范围和业务逻辑的准确性

**子类型**：
- **格式验证**：邮箱、手机号等格式检查
- **范围验证**：数值范围、日期范围检查
- **业务逻辑验证**：自定义业务规则检查

**示例配置**：
```yaml
- name: "年龄范围验证"
type: "accuracy"
table: "users"
column: "age"
description: "验证年龄在合理范围内（0-150）"
enabled: true
validation_type: "range"
min_value: 0
max_value: 150
```

### 3. 自定义SQL检查规则 (Custom SQL Rules)
**用途**：通过自定义SQL实现复杂业务逻辑检查

**适用场景**：
- 跨表一致性检查
- 数据新鲜度验证
- 引用完整性检查
- 业务指标监控

**示例配置**：
```yaml
- name: "收入一致性检查"
type: "custom_sql"
description: "检查用户总收入和订单收入是否一致"
enabled: true
sql: |
  SELECT 
    u.user_id,
    u.total_income,
    SUM(o.amount) as order_total
  FROM users u
  LEFT JOIN orders o ON u.user_id = o.user_id
  GROUP BY u.user_id, u.total_income
  HAVING ABS(u.total_income - COALESCE(SUM(o.amount), 0)) > 0.01
expected_result: "empty"  # 期望查询结果为空
```

### 4. 通用检查规则 (Generic Check Rules)
**用途**：通用的数据质量检查

**子类型**：
- **行数检查**：表数据量监控
- **数据分布检查**：字段值分布验证
- **唯一性检查**：重复数据检测

**示例配置**：
```yaml
- name: "用户表行数检查"
type: "generic"
description: "检查用户表是否有数据"
enabled: true
check_type: "row_count"
table: "users"
min_rows: 1
max_rows: 1000000
```

### 5. 高级检查规则 (Advanced Rules)
**用途**：复杂的数据质量分析

**子类型**：
- **跨表一致性检查**：多表数据一致性验证
- **趋势分析检查**：时间序列数据分析
- **异常检测**：离群值检测

**示例配置**：
```yaml
- name: "跨表数据一致性"
type: "cross_table"
description: "检查用户表和用户档案表的数据一致性"
enabled: true
tables: ["users", "user_profiles"]
join_condition: "users.user_id = user_profiles.user_id"
comparison_columns: ["name", "email"]
```

## 快速开始示例

### 基础完整性检查
```yaml
completeness_rules:
  - name: "产品表SKU完整性"
    type: "completeness"
    table: "products"
    column: "sku"
    description: "检查产品SKU字段完整性"
    enabled: true
    threshold: 0.98
```

### 业务准确性检查
```yaml
accuracy_rules:
  - name: "订单状态验证"
    type: "accuracy"
    table: "orders"
    column: "status"
    description: "验证订单状态值在预定义范围内"
    enabled: true
    validation_type: "enum"
    allowed_values: ["pending", "processing", "shipped", "delivered", "cancelled"]
```

### 自定义业务逻辑检查
```yaml
custom_sql_rules:
  - name: "库存一致性检查"
    type: "custom_sql"
    description: "检查产品库存与销售记录的一致性"
    enabled: true
    sql: |
      SELECT 
        p.product_id,
        p.stock_quantity,
        SUM(s.quantity) as sold_quantity
      FROM products p
      LEFT JOIN sales s ON p.product_id = s.product_id
      WHERE s.sale_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
      GROUP BY p.product_id, p.stock_quantity
      HAVING p.stock_quantity < 0 OR p.stock_quantity < sold_quantity
    expected_result: "empty"
```

## 规则配置参数说明

### 通用参数
- `name`: 规则名称（必填）
- `type`: 规则类型（必填）
- `description`: 规则描述
- `enabled`: 是否启用（默认true）
- `threshold`: 阈值（0-1之间的小数）

### 表相关参数
- `table`: 目标表名
- `column`: 目标字段名
- `tables`: 多表检查时的表名列表

### SQL相关参数
- `sql`: 自定义SQL查询
- `expected_result`: 期望结果（"empty"或"not_empty"）
- `min_records`: 最小记录数

### 验证参数
- `validation_type`: 验证类型
- `min_value`/`max_value`: 数值范围
- `allowed_values`: 允许的值列表

## 最佳实践

### 1. 规则命名规范
- 使用清晰的业务描述
- 包含表名和检查类型
- 避免使用技术术语

### 2. 阈值设置建议
- 关键业务字段：0.99+
- 重要业务字段：0.95-0.99
- 一般业务字段：0.90-0.95

### 3. 性能优化
- 对大表使用索引字段
- 避免全表扫描的SQL
- 合理设置检查频率

### 4. 错误处理
- 设置合理的超时时间
- 配置错误通知机制
- 记录详细的检查日志

## 故障排除

### 常见问题
1. **规则不执行**：检查enabled参数和依赖配置
2. **SQL执行错误**：验证SQL语法和表权限
3. **阈值报警**：调整阈值或检查数据质量

### 调试技巧
- 启用详细日志
- 使用测试数据验证规则
- 分步骤执行复杂规则

## 扩展开发

如需添加新的规则类型，请参考现有规则引擎的实现，确保：
- 实现规则验证逻辑
- 添加相应的配置参数
- 更新文档和示例

---

*更多详细信息请参考框架源代码和测试用例。*