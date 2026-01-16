# 第5章：dbt数据源与连接配置 - 代码示例

## 项目结构说明

本章演示dbt数据源定义和数据库连接配置的最佳实践。

```
chapter5/
├── README.md                    # 项目说明文档
├── dbt_project.yml              # dbt项目配置
├── profiles.yml                 # 数据库连接配置（示例）
├── models/
│   ├── staging/
│   │   ├── stg_customers.sql    # 客户数据清洗模型
│   │   └── stg_orders.sql       # 订单数据清洗模型
│   ├── intermediate/
│   │   └── int_customer_metrics.sql  # 客户指标计算
│   └── marts/
│       └── dim_customers.sql    # 客户维度表
├── sources/
│   └── sources.yml              # 数据源定义文件
├── tests/
│   └── sources/
│       └── test_sources.yml     # 数据源测试配置
└── run_example.bat              # 运行脚本
```

## 文件说明

### 配置文件
- **dbt_project.yml**: 项目配置，包含模型分层、数据源配置等
- **profiles.yml**: 数据库连接配置（示例文件）
- **sources.yml**: 数据源定义和声明

### 模型文件
- **staging层**: 数据清洗和基础转换
- **intermediate层**: 中间计算和指标聚合
- **marts层**: 业务维度和事实表

### 测试文件
- **test_sources.yml**: 数据源级别的测试配置

## 运行步骤

1. **环境准备**
   ```bash
   # 确保已安装dbt
   dbt --version
   
   # 复制profiles.yml到正确位置
   cp profiles.yml ~/.dbt/
   ```

2. **配置数据库连接**
   ```bash
   # 测试连接
   dbt debug
   
   # 编译项目
   dbt compile
   ```

3. **运行数据源测试**
   ```bash
   # 测试数据源
   dbt test --select source:*
   
   # 运行模型
   dbt run
   ```

4. **查看数据血缘**
   ```bash
   # 生成文档
   dbt docs generate
   dbt docs serve
   ```

## 学习目标

通过本章代码示例，您将学习：

1. **数据源定义**：如何声明和使用外部数据表
2. **连接配置**：配置多环境数据库连接
3. **数据源测试**：为外部数据表添加质量检查
4. **环境管理**：开发、测试、生产环境切换
5. **安全配置**：密码管理和连接安全性

## 关键概念演示

### 1. 数据源声明
```yaml
# sources.yml
sources:
  - name: raw_data
    description: "原始业务数据表"
    database: production
    schema: raw
    
    tables:
      - name: customers
        description: "客户基本信息表"
        columns:
          - name: customer_id
            description: "客户唯一标识"
            tests:
              - not_null
              - unique
```

### 2. 多环境配置
```yaml
# profiles.yml
dev:
  type: postgres
  host: localhost
  dbname: dbt_dev
  
prod:
  type: postgres
  host: prod-db.company.com
  dbname: dbt_prod
```

### 3. 环境切换
```bash
# 开发环境
dbt run --target dev

# 生产环境  
dbt run --target prod
```

## 注意事项

1. **安全提醒**: profiles.yml包含敏感信息，不要提交到版本控制
2. **环境变量**: 推荐使用环境变量管理密码和连接信息
3. **网络配置**: 确保数据库网络连接正常
4. **权限检查**: 验证数据库用户有足够的权限

## 下一步

完成本章学习后，可以继续学习：
- 第6章：dbt最佳实践与项目结构
- 第7章：dbt高级特性与自定义操作