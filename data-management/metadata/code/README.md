# 元数据管理代码示例集

本目录包含元数据管理学习指南中的所有配套代码示例，帮助读者通过实践加深对理论知识的理解。

## 📁 文件结构

```
code/
├── README.md                           # 本文件，代码示例说明
├── chapter1_metadata_basics.py         # 第1章：元数据管理基础概念
├── chapter2_metadata_types.py          # 第2章：元数据类型与分类
├── chapter3_metadata_storage.py        # 第3章：元数据存储与模型
└── chapter4_metadata_collection.py     # 第4章：元数据收集与提取
```

## 🚀 运行方法

### 环境准备
```bash
# 建议创建虚拟环境
python -m venv metadata_env
source metadata_env/bin/activate  # Linux/Mac
# 或 metadata_env\Scripts\activate  # Windows

# 安装基础依赖
pip install pandas sqlalchemy
```

### 运行代码
```bash
# 运行特定章节的示例
python chapter1_metadata_basics.py
python chapter2_metadata_types.py
python chapter3_metadata_storage.py
python chapter4_metadata_collection.py
```

## 📖 各章节代码说明

### chapter1_metadata_basics.py
**第1章：元数据管理基础概念**

包含以下示例：
- 元数据与数据的关系演示
- 数据目录实现（SimpleDataCatalog）
- 数据血缘管理（DataLineage）
- 基础元数据管理系统（MetadataManagementSystem）

**主要类**：
- `SimpleDataCatalog`：简单数据目录实现
- `DataLineage`：数据血缘管理
- `MetadataManagementSystem`：基础元数据管理系统

### chapter2_metadata_types.py
**第2章：元数据类型与分类**

包含以下示例：
- 业务元数据管理（BusinessMetadataManager）
- 技术元数据管理（TechnicalMetadataManager）
- 操作元数据管理（OperationalMetadataManager）
- 结构元数据管理（StructuralMetadata）
- 描述元数据管理（DescriptiveMetadata）
- 管理元数据管理（ManagementMetadata）
- 企业级元数据分类（EnterpriseMetadataClassification）
- ISO/IEC 11179标准实现（ISO11179MetadataRegistry）
- Dublin Core标准实现（DublinCoreMetadata）

**主要类**：
- `BusinessMetadataManager`：业务元数据管理器
- `TechnicalMetadataManager`：技术元数据管理器
- `OperationalMetadataManager`：操作元数据管理器
- `EnterpriseMetadataClassification`：企业级元数据分类
- `ISO11179MetadataRegistry`：ISO标准元数据注册系统
- `DublinCoreMetadata`：Dublin Core元数据标准实现

### chapter3_metadata_storage.py
**第3章：元数据存储与模型**

包含以下示例：
- 集中式元数据存储（CentralizedMetadataStorage）
- 分布式元数据存储（DistributedMetadataStorage）
- 混合式元数据存储（HybridMetadataStorage）
- 关系型元数据模型（RelationalMetadataModel）
- 图形元数据模型（GraphMetadataModel）
- 文档型元数据模型（DocumentMetadataModel）
- 元数据索引优化（MetadataIndexOptimizer）

**主要类**：
- `CentralizedMetadataStorage`：集中式存储系统
- `DistributedMetadataStorage`：分布式存储系统
- `RelationalMetadataModel`：关系型元数据模型
- `GraphMetadataModel`：图形元数据模型
- `DocumentMetadataModel`：文档型元数据模型
- `MetadataIndexOptimizer`：索引优化器

### chapter4_metadata_collection.py
**第4章：元数据收集与提取**

包含以下示例：
- 数据库元数据提取（SimpleMySQLMetadataExtractor、SimpleMongoMetadataExtractor）
- 文件系统元数据提取（SimpleFileSystemMetadataExtractor）
- 半自动化元数据收集（SemiAutomatedMetadataCollector）
- 结构化数据提取（SimpleStructuredDataExtractor）
- 元数据整合（MetadataIntegrator）

**主要类**：
- `SimpleMySQLMetadataExtractor`：MySQL元数据提取器
- `SimpleMongoMetadataExtractor`：MongoDB元数据提取器
- `SemiAutomatedMetadataCollector`：半自动化收集器
- `SimpleStructuredDataExtractor`：结构化数据提取器
- `MetadataIntegrator`：元数据整合器

## 💡 使用提示

1. **循序渐进**：建议按照章节顺序运行代码，确保理解每个概念
2. **实验修改**：尝试修改代码中的参数，观察结果变化
3. **扩展实践**：基于示例代码，解决实际问题
4. **组合使用**：尝试组合不同章节的代码，构建完整解决方案

## 🔧 自定义扩展

### 添加新的元数据源类型
```python
# 在chapter4中添加新的提取器
class CustomMetadataExtractor(DatabaseMetadataExtractor):
    def connect(self):
        # 自定义连接逻辑
        pass
    
    def extract_table_metadata(self, schema_name):
        # 自定义提取逻辑
        pass
```

### 扩展元数据模型
```python
# 在chapter3中添加新的模型
class CustomMetadataModel:
    def __init__(self):
        # 初始化自定义模型
        pass
    
    def store_metadata(self, metadata_id, metadata):
        # 自定义存储逻辑
        pass
```

### 实现新的元数据类型
```python
# 在chapter2中添加新的元数据类型
class CustomMetadataManager:
    def __init__(self):
        # 初始化自定义管理器
        pass
    
    def manage_metadata(self, metadata):
        # 自定义管理逻辑
        pass
```

## 🐛 常见问题

### Q: 运行代码时出现导入错误
A: 确保已安装所需的依赖包，特别是pandas和sqlalchemy。

### Q: 代码示例使用的是模拟数据，如何连接真实数据库？
A: 替换模拟数据为真实数据库连接字符串和配置。

### Q: 如何将多个章节的代码整合到一起？
A: 可以创建一个主程序，导入不同章节的类并组合使用。

## 📈 进阶实践

1. **集成真实数据源**：将示例代码与您的实际数据源集成
2. **构建完整系统**：基于示例构建完整的元数据管理系统
3. **性能优化**：针对大数据量场景优化代码性能
4. **部署到生产**：将元数据管理系统部署到生产环境

## 📚 参考资料

- [Python官方文档](https://docs.python.org/)
- [Pandas文档](https://pandas.pydata.org/docs/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [元数据管理最佳实践](../1-元数据管理基础概念.md)

---

**提示**：本代码示例主要用于学习目的，生产环境使用时请进行适当的安全性和性能优化。