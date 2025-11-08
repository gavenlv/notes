# Apache Spark 快速开始指南

本指南将帮助您快速开始使用Apache Spark，并运行我们提供的示例代码。

## 环境要求

- Python 3.6+
- Java 8+
- 足够的系统内存（建议4GB以上）

## 安装步骤

### 1. 安装PySpark

```bash
pip install pyspark==3.4.0
```

### 2. 验证安装

```bash
pyspark --version
```

## 运行示例

### 方法1: 使用运行脚本（推荐）

我们提供了一个便捷的运行脚本，可以快速运行所有示例：

```bash
# 运行单个示例
python run_examples.py wordcount

# 运行Pi估计器
python run_examples.py pi

# 运行销售分析
python run_examples.py sales

# 运行鸢尾花分类
python run_examples.py iris

# 运行所有示例
python run_examples.py all
```

### 方法2: 直接运行Python脚本

```bash
# 运行WordCount示例
python code/core-examples/wordcount.py

# 使用spark-submit运行（推荐）
spark-submit code/core-examples/wordcount.py

# 运行Pi估计器
spark-submit code/core-examples/pi_estimator.py 10

# 运行销售分析
spark-submit code/sql-examples/sales_analysis.py

# 运行鸢尾花分类
spark-submit code/mlib-examples/iris_classification.py
```

## 示例说明

### 1. WordCount (代码/core-examples/wordcount.py)

Spark的经典入门示例，统计文本中单词的出现频率。

```bash
spark-submit code/core-examples/wordcount.py
```

### 2. Pi估计器 (代码/core-examples/pi_estimator.py)

使用蒙特卡洛方法估计π值，展示Spark的并行计算能力。

```bash
spark-submit code/core-examples/pi_estimator.py 10
```

### 3. 销售分析 (代码/sql-examples/sales_analysis.py)

使用Spark SQL和DataFrame API分析销售数据，展示SQL操作、数据转换和聚合分析。

```bash
spark-submit code/sql-examples/sales_analysis.py
```

### 4. 鸢尾花分类 (代码/mlib-examples/iris_classification.py)

使用Spark MLlib对鸢尾花数据集进行分类，展示机器学习工作流。

```bash
spark-submit code/mlib-examples/iris_classification.py
```

### 5. 配置优化器 (代码/performance-tuning/spark_config_optimizer.py)

自动生成优化的Spark配置，提高应用程序性能。

```bash
python code/performance-tuning/spark_config_optimizer.py
```

## 常见问题

### 1. 找不到PySpark

确保已正确安装PySpark：

```bash
pip install pyspark==3.4.0
```

### 2. 内存不足错误

尝试增加Executor内存：

```bash
spark-submit --executor-memory 2g your_script.py
```

### 3. Python路径问题

指定Python路径：

```bash
spark-submit --conf spark.pyspark.python=/usr/bin/python3 your_script.py
```

## 进一步学习

- 阅读完整的教程：[Spark从入门到专家](README.md)
- 查看官方文档：[Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- 尝试更复杂的示例：查看code目录中的其他示例

## 交互式环境

### Spark Shell (Scala)

```bash
spark-shell
```

### PySpark Shell (Python)

```bash
pyspark
```

在交互式环境中，您可以实时运行Spark代码，非常适合学习和实验。

## 下一步

1. 阅读[README.md](README.md)了解完整的教程结构
2. 尝试修改示例代码，观察结果变化
3. 根据您的兴趣深入学习特定章节：
   - [Spark Core编程基础](4-Spark Core编程基础.md)
   - [Spark SQL与结构化数据处理](5-Spark SQL与结构化数据处理.md)
   - [Spark Streaming实时数据处理](6-Spark Streaming实时数据处理.md)
   - [Spark MLlib机器学习库](7-Spark MLlib机器学习库.md)
   - [Spark性能调优与生产实践](8-Spark性能调优与生产实践.md)

祝您学习愉快！