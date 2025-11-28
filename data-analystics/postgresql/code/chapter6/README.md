# 第6章代码示例

本目录包含PostgreSQL第6章"索引和性能优化"的所有代码示例：

1. `index_types_demo.sql` - 不同类型索引的创建和使用示例
2. `performance_analysis.sql` - 性能分析和执行计划示例
3. `optimization_examples.sql` - 性能优化技巧示例
4. `python_examples.py` - Python中索引和性能优化的演示
5. `requirements.txt` - Python依赖包

## 运行说明

1. 确保PostgreSQL服务器正在运行
2. 创建一个新的数据库用于测试
3. 按顺序运行SQL文件以创建表结构和示例数据
4. 执行各个示例文件中的查询语句，观察执行计划变化
5. 运行Python示例前需要安装依赖：`pip install -r requirements.txt`

## 主要功能演示

- **B-Tree索引**：通用等值和范围查询优化
- **Hash索引**：等值查询优化
- **GiST索引**：几何数据和全文搜索
- **GIN索引**：数组和JSON数据查询
- **BRIN索引**：大表范围查询优化
- **EXPLAIN分析**：查询执行计划分析
- **性能对比**：索引前后性能差异