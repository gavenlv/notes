# PostgreSQL教程第8章：存储过程和函数

## 概述
本章将介绍PostgreSQL中的存储过程和函数开发，重点讲解PL/pgSQL语言的使用方法和最佳实践。

## 文件说明

### SQL文件
1. **basic_functions.sql** - 基础函数创建和调用
2. **plpgsql_procedures.md** - PL/pgSQL存储过程详解
3. **advanced_functions.md** - 高级函数技巧
4. **triggers.md** - 触发器使用指南
5. **function_examples.sql** - 函数实例代码
6. **performance_optimization.md** - 函数性能优化

### Python文件
7. **python_function_demo.py** - Python中调用PostgreSQL函数
8. **function_examples.py** - Python调用函数和存储过程的示例

## 运行指南

### 1. 执行SQL文件
```bash
# 进入PostgreSQL命令行
psql -U your_username -d your_database

# 依次执行SQL文件
\i basic_functions.sql
\i function_examples.sql
```

### 2. 运行Python示例
```bash
# 安装依赖
pip install -r requirements.txt

# 运行Python脚本
python python_function_demo.py
```

## 学习目标
- 掌握PL/pgSQL语言基础
- 学会创建各种类型的函数和存储过程
- 了解触发器的使用场景
- 掌握函数性能优化技巧
- 能够使用Python调用数据库函数

## 注意事项
- 所有示例代码均基于PostgreSQL 12+
- 请根据实际环境调整连接参数
- 测试环境建议使用专门的测试数据库