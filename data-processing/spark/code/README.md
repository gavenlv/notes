# Spark代码示例

本目录包含了《Apache Spark从入门到专家》教程中所有章节的代码示例。

## 目录结构

- `installation/` - Spark安装与配置示例
- `core-examples/` - Spark Core编程示例
- `sql-examples/` - Spark SQL与结构化数据处理示例
- `streaming-examples/` - Spark Streaming实时数据处理示例
- `mlib-examples/` - Spark MLlib机器学习库示例
- `performance-tuning/` - Spark性能调优示例
- `production-templates/` - 生产环境配置模板

## 运行环境要求

- Python 3.6+
- Java 8+
- Apache Spark 3.4+
- PySpark (Python API for Spark)

## 快速开始

1. 安装PySpark:
   ```bash
   pip install pyspark==3.4.0
   ```

2. 运行示例代码:
   ```bash
   python core-examples/rdd_basics.py
   ```

3. 对于需要Spark环境的示例，确保已正确安装并配置Spark。

## 各目录说明

### installation/

包含Spark安装与配置相关的脚本和配置文件，适用于不同的部署模式和环境。

### core-examples/

包含Spark Core编程的基础和进阶示例，展示RDD操作、转换和行动操作、数据分区等核心概念。

### sql-examples/

包含Spark SQL和DataFrame操作的示例，涵盖基本操作、聚合函数、窗口函数、数据源读写等。

### streaming-examples/

包含Spark Streaming实时数据处理的示例，展示DStream操作、窗口计算、输入输出源等。

### mlib-examples/

包含Spark MLlib机器学习库的示例，涵盖特征工程、分类、回归、聚类等机器学习任务。

### performance-tuning/

包含Spark性能调优的示例，展示内存管理、并行度优化、数据倾斜处理等技术。

### production-templates/

包含生产环境中使用的配置模板和最佳实践代码，帮助构建可靠的Spark应用程序。