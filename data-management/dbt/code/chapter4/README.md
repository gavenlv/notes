# 第4章：dbt宏与Jinja模板 - 代码示例

## 代码结构说明

本章演示dbt宏和Jinja模板的使用，包含以下文件：

```
chapter4/
├── README.md                    # 本章说明文档
├── dbt_project.yml              # dbt项目配置
├── macros/                      # 宏定义目录
│   ├── date_utils.sql           # 日期工具宏
│   ├── string_utils.sql         # 字符串工具宏
│   ├── conditional_aggregation.sql # 条件聚合宏
│   ├── dynamic_sql.sql          # 动态SQL生成宏
│   └── validation_utils.sql     # 验证工具宏
├── models/
│   ├── staging/
│   │   ├── stg_customers.sql    # 客户数据模型
│   │   └── stg_orders.sql       # 订单数据模型
│   ├── intermediate/
│   │   └── int_customer_metrics.sql # 客户指标计算
│   └── marts/
│       └── dim_customers.sql    # 客户维度表
├── tests/
│   └── macros/                   # 宏测试
│       └── test_date_utils.sql  # 日期工具宏测试
└── run_example.bat              # 运行脚本
```

## 文件说明

### 宏文件

1. **macros/date_utils.sql** - 日期处理相关宏
2. **macros/string_utils.sql** - 字符串处理相关宏
3. **macros/conditional_aggregation.sql** - 条件聚合宏
4. **macros/dynamic_sql.sql** - 动态SQL生成宏
5. **macros/validation_utils.sql** - 数据验证宏

### 模型文件

1. **models/staging/stg_customers.sql** - 客户数据清洗模型
2. **models/staging/stg_orders.sql** - 订单数据清洗模型
3. **models/intermediate/int_customer_metrics.sql** - 客户指标计算
4. **models/marts/dim_customers.sql** - 客户维度表

## 运行步骤

1. 确保已安装dbt和数据库连接
2. 运行 `run_example.bat` 脚本
3. 观察宏的使用效果和生成的SQL

## 学习目标

通过本章代码示例，您将学习：

- 如何创建和使用dbt宏
- Jinja模板的基本语法和高级特性
- 动态SQL生成技术
- 宏的模块化和重用
- 宏测试和调试方法

## 关键概念演示

- **宏参数传递** - 学习如何向宏传递参数
- **条件逻辑** - 使用Jinja控制结构
- **动态字段选择** - 根据条件动态生成SQL
- **宏返回值** - 宏如何返回复杂数据结构
- **错误处理** - 宏中的异常处理机制