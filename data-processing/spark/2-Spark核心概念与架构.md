# 2. Spark核心概念与架构

## 2.1 Spark运行架构

理解Spark的运行架构是掌握Spark的关键。Spark采用主从架构，由驱动程序(Driver)、集群管理器(Cluster Manager)和工作节点(Worker)组成。

### 2.1.1 基本架构组件

#### 1. 驱动程序(Driver)

驱动程序是运行`main`函数的进程，负责创建SparkContext，构建DAG，并与集群管理器通信。

**代码示例：查看Driver信息**

```python
# code/core-examples/driver_info.py
from pyspark import SparkContext
import os

def driver_info_example():
    # 创建SparkContext
    sc = SparkContext("local[*]", "DriverInfo")
    
    # 打印Driver相关信息
    print("Driver信息:")
    print(f"Spark应用程序名称: {sc.appName}")
    print(f"Spark版本: {sc.version}")
    print(f"应用程序ID: {sc.applicationId}")
    print(f"Driver主机地址: {sc.master}")
    
    # 获取Driver运行环境
    print(f"Python版本: {sc.pythonVer}")
    print(f"Driver端口: {sc.driverPort}")
    
    sc.stop()

if __name__ == "__main__":
    driver_info_example()
```

#### 2. 集群管理器(Cluster Manager)

Spark支持多种集群管理器，包括：

- **Standalone**: Spark自带的简单集群管理器
- **Apache Mesos**: 通用的集群管理器
- **Hadoop YARN**: Hadoop生态系统的资源管理器
- **Kubernetes**: 容器编排平台

#### 3. 工作节点(Worker)

工作节点是在集群中运行应用程序任务的进程，负责管理计算资源。

#### 4. 执行器(Executor)

执行器是在工作节点上启动的进程，负责运行具体的任务，并将数据存储在内存或磁盘中。

### 2.1.2 Spark执行流程

一个Spark应用程序的执行流程如下：

1. 用户提交应用程序代码
2. 驱动程序创建SparkContext，连接到集群管理器
3. 集群管理器分配资源，在工作节点上启动执行器
4. 驱动程序将代码发送到执行器
5. 执行器执行任务，并将结果返回给驱动程序
6. 任务完成后，驱动程序退出或调用`stop()`方法

**代码示例：监控Spark执行流程**

```python
# code/core-examples/execution_flow.py
from pyspark import SparkContext
import time

def execution_flow_example():
    sc = SparkContext("local[*]", "ExecutionFlow")
    
    # 添加监听器以监控执行过程
    sc.addPyFile(__file__)  # 将当前文件添加到Spark上下文
    
    # 创建RDD并执行转换
    data = range(1, 10001)
    rdd = sc.parallelize(data, numSlices=10)  # 分成10个分区
    
    # 执行多个转换操作
    mapped_rdd = rdd.map(lambda x: x * 2)
    filtered_rdd = mapped_rdd.filter(lambda x: x % 3 == 0)
    
    # 执行行动操作，触发实际计算
    start_time = time.time()
    result = filtered_rdd.count()
    end_time = time.time()
    
    print(f"结果: {result}")
    print(f"执行时间: {end_time - start_time:.2f}秒")
    print(f"分区数: {rdd.getNumPartitions()}")
    
    # 获取RDD的依赖关系
    print("RDD依赖关系:")
    print(f"filtered_rdd -> {filtered_rdd.context}")
    
    sc.stop()

if __name__ == "__main__":
    execution_flow_example()
```

### 2.1.3 Spark核心组件交互

以下是Spark核心组件之间的交互图：

```
+-------------------+      +---------------------+      +------------------+
|    Driver Program |      |  Cluster Manager    |      |    Worker Nodes  |
|   (SparkContext)  |<---->| (Resource Manager)  |<---->|                  |
+-------------------+      +---------------------+      +------------------+
        |                           |                          |
        | 任务提交                   | 资源分配                  | 启动执行器
        v                           v                          v
+-------------------+      +---------------------+      +------------------+
|      DAG Scheduler|----->|      Task Scheduler|----->|     Executor     |
+-------------------+      +---------------------+      +------------------+
```

## 2.2 RDD、DataFrame与Dataset

Spark提供了三种主要的数据抽象：RDD、DataFrame和Dataset。每种抽象都有其特定的用途和优势。

### 2.2.1 RDD(弹性分布式数据集)

RDD是Spark的基础数据结构，是一个不可变的分布式对象集合。

#### RDD特性

1. **不可变性**: 一旦创建，不能修改
2. **分布式**: 数据分布在集群的多个节点上
3. **弹性**: 可以自动从节点故障中恢复
4. **懒加载**: 只有在行动操作执行时才计算

**代码示例：RDD基本操作**

```python
# code/core-examples/rdd_operations.py
from pyspark import SparkContext

def rdd_operations_example():
    sc = SparkContext("local[*]", "RDDOperations")
    
    # 创建RDD的几种方式
    # 1. 从内存中的集合创建
    data = [1, 2, 3, 4, 5]
    rdd1 = sc.parallelize(data)
    
    # 2. 从外部存储创建
    # rdd2 = sc.textFile("hdfs://path/to/file.txt")
    
    # RDD转换操作
    # map操作
    squared_rdd = rdd1.map(lambda x: x * x)
    print("map结果:", squared_rdd.collect())
    
    # filter操作
    even_rdd = rdd1.filter(lambda x: x % 2 == 0)
    print("filter结果:", even_rdd.collect())
    
    # flatMap操作
    flat_rdd = sc.parallelize(["hello world", "spark is great"])
    words_rdd = flat_rdd.flatMap(lambda line: line.split(" "))
    print("flatMap结果:", words_rdd.collect())
    
    # RDD行动操作
    # collect操作
    all_data = rdd1.collect()
    print("collect结果:", all_data)
    
    # count操作
    count = rdd1.count()
    print("count结果:", count)
    
    # reduce操作
    sum_result = rdd1.reduce(lambda a, b: a + b)
    print("reduce结果:", sum_result)
    
    # RDD缓存
    rdd1.cache()  # 将RDD缓存到内存
    
    sc.stop()

if __name__ == "__main__":
    rdd_operations_example()
```

#### RDD依赖关系

RDD的依赖关系分为窄依赖和宽依赖：

- **窄依赖**: 每个父RDD的分区最多被子RDD的一个分区使用
- **宽依赖**: 子RDD的一个分区可能依赖于父RDD的多个分区

**代码示例：分析RDD依赖关系**

```python
# code/core-examples/rdd_dependencies.py
from pyspark import SparkContext

def rdd_dependencies_example():
    sc = SparkContext("local[*]", "RDDDependencies")
    
    # 创建父RDD
    parent_rdd = sc.parallelize(range(1, 101), 10)
    
    # 窄依赖示例 - map操作
    narrow_rdd = parent_rdd.map(lambda x: x * 2)
    
    # 宽依赖示例 - groupByKey操作
    pairs_rdd = sc.parallelize([(x, x % 3) for x in range(1, 101)], 10)
    wide_rdd = pairs_rdd.groupByKey()
    
    # 打印依赖信息
    print("父RDD分区数:", parent_rdd.getNumPartitions())
    print("窄依赖(map)分区数:", narrow_rdd.getNumPartitions())
    print("宽依赖(groupByKey)分区数:", wide_rdd.getNumPartitions())
    
    # 获取RDD的依赖关系
    print("\n窄依赖关系:")
    for dep in narrow_rdd.dependencies():
        print(f"  {dep}")
    
    print("\n宽依赖关系:")
    for dep in wide_rdd.dependencies():
        print(f"  {dep}")
    
    sc.stop()

if __name__ == "__main__":
    rdd_dependencies_example()
```

### 2.2.2 DataFrame

DataFrame是一个带有命名列的分布式数据集合，类似于关系数据库中的表或R/Python中的数据框。

**代码示例：DataFrame基本操作**

```python
# code/sql-examples/dataframe_operations.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

def dataframe_operations_example():
    spark = SparkSession.builder.appName("DataFrameOperations").getOrCreate()
    
    # 创建DataFrame的几种方式
    # 1. 从RDD创建
    rdd = spark.sparkContext.parallelize([("Alice", 34), ("Bob", 45), ("Charlie", 29)])
    schema = StructType([
        StructField("name", StringType, True),
        StructField("age", IntegerType, True)
    ])
    df1 = spark.createDataFrame(rdd, schema)
    
    # 2. 从列表创建
    data = [("Alice", 34), ("Bob", 45), ("Charlie", 29)]
    columns = ["name", "age"]
    df2 = spark.createDataFrame(data, columns)
    
    # DataFrame基本操作
    # 显示数据
    print("显示DataFrame内容:")
    df1.show()
    
    # 打印模式
    print("DataFrame模式:")
    df1.printSchema()
    
    # 选择列
    print("选择name列:")
    df1.select("name").show()
    
    # 过滤数据
    print("过滤年龄大于30的人:")
    df1.filter(df1.age > 30).show()
    
    # 聚合操作
    print("年龄统计:")
    df1.agg({"age": "avg", "age": "max", "age": "min"}).show()
    
    spark.stop()

if __name__ == "__main__":
    dataframe_operations_example()
```

### 2.2.3 Dataset

Dataset是DataFrame API的扩展，提供了类型安全，在Scala和Java中使用较多。在Python中，DataFrame实际上就是Dataset[Row]的别名。

### 2.2.4 RDD、DataFrame与Dataset对比

| 特性 | RDD | DataFrame | Dataset |
|------|-----|-----------|---------|
| API类型 | 函数式 | 声明式 | 声明式+类型安全 |
| 类型安全 | 编译时不检查 | 运行时检查 | 编译时检查 |
| 性能优化 | 手动优化 | Catalyst优化器优化 | Catalyst优化器优化 |
| 序列化 | Java/Kryo序列化 | Tungsten二进制格式 | Tungsten二进制格式 |
| 易用性 | 较低 | 高 | 高 |

## 2.3 Spark执行流程

### 2.3.1 DAG(有向无环图)

Spark将用户代码转换为DAG，然后根据DAG执行任务。

**代码示例：查看DAG**

```python
# code/core-examples/dag_visualization.py
from pyspark import SparkContext
import json

def dag_visualization_example():
    sc = SparkContext("local[*]", "DAGVisualization")
    
    # 创建一个复杂的RDD转换链
    data = sc.parallelize(range(1, 100), 10)
    
    # 复杂的转换操作
    step1 = data.filter(lambda x: x % 2 == 0)  # 过滤偶数
    step2 = step1.map(lambda x: x * 2)        # 乘以2
    step3 = step2.filter(lambda x: x > 10)    # 过滤大于10的数
    step4 = step3.map(lambda x: (x, str(x)))  # 转换为键值对
    
    # 触发行动操作
    result = step4.collect()
    print(f"结果示例: {result[:5]}...")
    
    # 在Web UI中可以查看DAG可视化
    print("请在Spark UI的Stages页面查看DAG可视化")
    
    sc.stop()

if __name__ == "__main__":
    dag_visualization_example()
```

### 2.3.2 Job、Stage与Task

Spark将一个应用程序分解为多个Job，每个Job分解为多个Stage，每个Stage分解为多个Task。

**代码示例：理解Job、Stage与Task**

```python
# code/core-examples/job_stage_task.py
from pyspark import SparkContext

def job_stage_task_example():
    sc = SparkContext("local[*]", "JobStageTask")
    
    # 创建两个不同的RDD操作
    rdd = sc.parallelize(range(1, 101), 10)
    
    # 第一个Job：计算平方和
    square_sum = rdd.map(lambda x: x * x).sum()
    print(f"平方和: {square_sum}")
    
    # 第二个Job：计算平均值
    count = rdd.count()
    total = rdd.reduce(lambda a, b: a + b)
    average = total / count
    print(f"平均值: {average}")
    
    # 第三个Job：复杂的转换链
    result = rdd.filter(lambda x: x % 2 == 0) \
               .map(lambda x: x * 2) \
               .filter(lambda x: x > 50) \
               .collect()
    
    print(f"复杂转换结果: {result[:5]}...")
    
    print("请在Spark UI中查看Job、Stage和Task的执行情况")
    
    sc.stop()

if __name__ == "__main__":
    job_stage_task_example()
```

## 2.4 内存管理机制

Spark的内存管理是其高性能的关键，主要分为执行内存和存储内存。

### 2.4.1 内存区域划分

Spark的内存分为以下几个区域：

1. **执行内存(Execution Memory)**: 用于shuffle、join、sort等操作
2. **存储内存(Storage Memory)**: 用于缓存RDD和数据
3. **用户内存(User Memory)**: 用于存储用户数据结构
4. **预留内存(Reserved Memory)**: 系统预留，固定为300MB

**代码示例：查看内存使用情况**

```python
# code/core-examples/memory_management.py
from pyspark import SparkContext

def memory_management_example():
    sc = SparkContext("local[*]", "MemoryManagement")
    
    # 设置内存参数
    sc.setSystemProperty("spark.executor.memory", "2g")
    sc.setSystemProperty("spark.memory.fraction", "0.6")
    
    # 创建RDD并缓存
    rdd = sc.parallelize(range(1, 1000000))
    rdd.cache()  # 缓存到内存
    
    # 触发缓存
    count = rdd.count()
    print(f"RDD缓存，元素个数: {count}")
    
    # 查看存储信息
    storage_level = rdd.getStorageLevel()
    print(f"存储级别: {storage_level}")
    
    # 查看RDD的内存使用情况
    print("请在Spark UI的Storage页面查看内存使用情况")
    
    sc.stop()

if __name__ == "__main__":
    memory_management_example()
```

### 2.4.2 存储级别

Spark提供了多种存储级别，以适应不同的使用场景：

```python
# code/core-examples/storage_levels.py
from pyspark import SparkContext
from pyspark.storagelevel import StorageLevel

def storage_levels_example():
    sc = SparkContext("local[*]", "StorageLevels")
    
    # 创建RDD
    rdd = sc.parallelize(range(1, 100000))
    
    # 演示不同的存储级别
    print("存储级别演示:")
    
    # 1. 默认存储级别：内存 + 磁盘
    rdd.cache()  # 等同于 persist(StorageLevel.MEMORY_AND_DISK)
    print("1. MEMORY_AND_DISK: 优先内存，内存不足时使用磁盘")
    
    # 2. 仅内存
    rdd.persist(StorageLevel.MEMORY_ONLY)
    print("2. MEMORY_ONLY: 仅存储在内存中")
    
    # 3. 仅磁盘
    rdd.persist(StorageLevel.DISK_ONLY)
    print("3. DISK_ONLY: 仅存储在磁盘上")
    
    # 4. 内存 + 序列化
    rdd.persist(StorageLevel.MEMORY_ONLY_SER)
    print("4. MEMORY_ONLY_SER: 内存中以序列化形式存储")
    
    # 5. 内存 + 磁盘 + 序列化
    rdd.persist(StorageLevel.MEMORY_AND_DISK_SER)
    print("5. MEMORY_AND_DISK_SER: 内存和磁盘序列化存储")
    
    # 6. 副本数
    rdd.persist(StorageLevel.MEMORY_AND_DISK_2)
    print("6. MEMORY_AND_DISK_2: 在内存和磁盘中存储2个副本")
    
    # 触发缓存
    count = rdd.count()
    print(f"元素个数: {count}")
    
    # 查看存储信息
    print(f"当前存储级别: {rdd.getStorageLevel()}")
    
    sc.stop()

if __name__ == "__main__":
    storage_levels_example()
```

### 2.4.3 内存回收与优化

Spark的内存回收策略和优化方法：

**代码示例：内存优化技巧**

```python
# code/core-examples/memory_optimization.py
from pyspark import SparkContext
from pyspark.sql import SparkSession

def memory_optimization_example():
    # Spark Core内存优化
    sc = SparkContext("local[*]", "MemoryOptimization")
    
    # 1. 使用合适的数据类型
    # 避免使用复杂对象，使用基本类型
    simple_rdd = sc.parallelize(range(1, 1000000))
    
    # 2. 使用序列化
    # 序列化可以减少内存占用
    serialized_rdd = simple_rdd.map(lambda x: (x, x*x)).persist()
    
    # 3. 及时释放不需要的缓存
    count = serialized_rdd.count()
    print(f"序列化RDD元素个数: {count}")
    
    # 解除缓存
    serialized_rdd.unpersist()
    
    sc.stop()
    
    # Spark SQL内存优化
    spark = SparkSession.builder.appName("MemoryOptimizationSQL").getOrCreate()
    
    # 1. 使用列式存储格式
    # 2. 启用压缩
    # 3. 分区表
    df = spark.read.format("csv") \
                  .option("header", "true") \
                  .option("inferSchema", "true") \
                  .load("data/sample.csv")
    
    # 缓存DataFrame
    df.cache()
    df.count()  # 触发缓存
    
    # 查看执行计划，确认优化
    df.explain()
    
    spark.stop()

if __name__ == "__main__":
    memory_optimization_example()
```

## 2.5 数据分区

### 2.5.1 分区原理

分区是Spark并行处理的基础，数据被分成多个分区，每个分区在一个Task中处理。

**代码示例：分区操作**

```python
# code/core-examples/partitioning.py
from pyspark import SparkContext

def partitioning_example():
    sc = SparkContext("local[*]", "Partitioning")
    
    # 创建RDD，指定分区数
    data = range(1, 101)
    rdd = sc.parallelize(data, numSlices=10)  # 分成10个分区
    
    print(f"初始分区数: {rdd.getNumPartitions()}")
    
    # 查看每个分区的内容
    def partition_func(index, iterator):
        yield f"Partition {index}: {list(iterator)}"
    
    partition_contents = rdd.mapPartitionsWithIndex(partition_func).collect()
    for content in partition_contents:
        print(content)
    
    # 重新分区
    repartitioned_rdd = rdd.repartition(5)  # 重分区为5个，会进行shuffle
    print(f"重分区后的分区数: {repartitioned_rdd.getNumPartitions()}")
    
    coalesced_rdd = rdd.coalesce(5)  # 合并为5个分区，避免shuffle
    print(f"合并后的分区数: {coalesced_rdd.getNumPartitions()}")
    
    sc.stop()

if __name__ == "__main__":
    partitioning_example()
```

### 2.5.2 自定义分区器

当数据需要按照特定规则分区时，可以使用自定义分区器。

**代码示例：自定义分区器**

```python
# code/core-examples/custom_partitioner.py
from pyspark import SparkContext
from pyspark import Partitioner

class CustomPartitioner(Partitioner):
    def __init__(self, num_partitions):
        self.num_partitions = num_partitions
        
    def getPartition(self, key):
        # 根据key的哈希值决定分区
        return hash(key) % self.num_partitions
        
    def __eq__(self, other):
        return isinstance(other, CustomPartitioner) and \
               self.num_partitions == other.num_partitions

def custom_partitioner_example():
    sc = SparkContext("local[*]", "CustomPartitioner")
    
    # 创建键值对RDD
    pairs = sc.parallelize([("apple", 1), ("banana", 2), ("orange", 3), 
                           ("apple", 4), ("banana", 5), ("orange", 6),
                           ("apple", 7), ("banana", 8), ("orange", 9)], 3)
    
    # 使用自定义分区器
    partitioner = CustomPartitioner(3)
    partitioned_rdd = pairs.partitionBy(3, lambda key: hash(key) % 3)
    
    # 查看分区结果
    def print_partition(index, iterator):
        print(f"Partition {index}: {list(iterator)}")
        return iterator
    
    partitioned_rdd.foreachPartition(lambda iterator: 
                                   print(f"Partition content: {list(iterator)}"))
    
    # 在每个分区内排序
    sorted_rdd = partitioned_rdd.mapPartitions(lambda iterator: sorted(iterator))
    
    print("分区内排序结果:")
    sorted_rdd.foreach(lambda x: print(x))
    
    sc.stop()

if __name__ == "__main__":
    custom_partitioner_example()
```

## 2.6 小结

本章深入讲解了Spark的核心概念和架构，包括运行架构、数据抽象（RDD、DataFrame、Dataset）、执行流程、内存管理和数据分区。理解这些核心概念是掌握Spark的基础，也是进行性能优化的前提。在接下来的章节中，我们将学习如何安装和配置Spark环境，以及如何使用Spark进行实际的数据处理。

## 实验与练习

1. 编写程序演示Spark执行流程，包括Driver、Executor和Task的交互
2. 比较RDD、DataFrame和Dataset的性能差异
3. 分析一个复杂Spark应用的DAG，识别窄依赖和宽依赖
4. 实现自定义分区器，优化特定数据分布的查询性能
5. 测试不同存储级别对内存使用和性能的影响

## 参考资源

- [Spark Core编程指南](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Spark性能调优指南](https://spark.apache.org/docs/latest/tuning.html)