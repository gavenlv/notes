# 8. Spark性能调优与生产实践

## 8.1 性能调优概述

Spark性能调优是确保Spark应用程序在大规模数据处理中高效运行的关键。性能调优涉及多个方面，包括资源配置、代码优化、数据结构优化和系统级调优。

### 8.1.1 性能调优的基本原则

1. **减少数据移动**：尽量在本地处理数据，减少网络传输
2. **优化数据结构**：使用适当的数据结构和序列化方式
3. **合理分区**：确保数据均匀分布在集群中
4. **内存管理**：有效利用内存，避免不必要的磁盘I/O
5. **并行度设置**：根据集群资源和数据量设置合适的并行度

**代码示例：性能调优基础框架**

```python
# code/performance-tuning/performance_framework.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time
import psutil

class PerformanceAnalyzer:
    """Spark性能分析器"""
    
    def __init__(self, spark_context=None, spark_session=None):
        self.sc = spark_context
        self.spark = spark_session
        self.metrics = {}
    
    def record_start_time(self, operation_name):
        """记录操作开始时间"""
        self.metrics[f"{operation_name}_start"] = time.time()
    
    def record_end_time(self, operation_name):
        """记录操作结束时间"""
        self.metrics[f"{operation_name}_end"] = time.time()
    
    def get_duration(self, operation_name):
        """获取操作持续时间"""
        if f"{operation_name}_start" in self.metrics and f"{operation_name}_end" in self.metrics:
            return self.metrics[f"{operation_name}_end"] - self.metrics[f"{operation_name}_start"]
        return None
    
    def print_metrics(self):
        """打印性能指标"""
        print("\n=== 性能指标 ===")
        
        # 获取操作的持续时间
        operations = set()
        for key in self.metrics:
            if key.endswith("_start"):
                operation = key[:-6]  # 移除"_start"后缀
                operations.add(operation)
        
        for operation in sorted(operations):
            duration = self.get_duration(operation)
            if duration is not None:
                print(f"{operation}: {duration:.4f}秒")
        
        # 打印Spark配置信息
        if self.spark:
            print("\n=== Spark配置信息 ===")
            config = self.spark.sparkContext.getConf().getAll()
            for key, value in config:
                print(f"{key}: {value}")
        
        # 打印系统资源信息
        print("\n=== 系统资源信息 ===")
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        print(f"CPU使用率: {cpu_percent}%")
        print(f"内存使用: {memory.used / (1024**3):.2f}GB / {memory.total / (1024**3):.2f}GB")
        print(f"内存使用率: {memory.percent}%")
    
    def analyze_job_stages(self, df):
        """分析DataFrame操作的执行阶段"""
        if self.spark:
            # 触发执行计划分析
            print("\n=== 执行计划分析 ===")
            df.explain(extended=True)
            
            # 使用explain()方法查看物理计划
            print("\n=== 物理计划 ===")
            df.explain()

def performance_framework_demo():
    """性能分析框架演示"""
    
    # 创建SparkSession
    spark = SparkSession.builder \
                         .appName("PerformanceFrameworkDemo") \
                         .config("spark.sql.adaptive.enabled", "true") \
                         .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                         .getOrCreate()
    
    # 创建性能分析器
    analyzer = PerformanceAnalyzer(spark_session=spark)
    
    # 生成测试数据
    analyzer.record_start_time("data_generation")
    data = [(i, f"user_{i}", i % 10) for i in range(1000000)]
    df = spark.createDataFrame(data, ["id", "name", "group"])
    analyzer.record_end_time("data_generation")
    
    # 转换操作1：过滤
    analyzer.record_start_time("filter_operation")
    filtered_df = df.filter(df["group"] > 5)
    filtered_df.count()  # 触发执行
    analyzer.record_end_time("filter_operation")
    
    # 转换操作2：聚合
    analyzer.record_start_time("aggregation_operation")
    aggregated_df = df.groupBy("group").count()
    aggregated_df.collect()  # 触发执行
    analyzer.record_end_time("aggregation_operation")
    
    # 打印性能指标
    analyzer.print_metrics()
    
    # 分析作业阶段
    analyzer.analyze_job_stages(aggregated_df)
    
    spark.stop()

if __name__ == "__main__":
    performance_framework_demo()
```

## 8.2 内存管理优化

内存管理是Spark性能调优的关键环节，包括执行内存和存储内存的管理。

### 8.2.1 内存区域配置

```python
# code/performance-tuning/memory_management.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.storagelevel import StorageLevel
import time

def memory_management_optimization():
    """内存管理优化演示"""
    
    # 创建SparkSession，配置内存参数
    spark = SparkSession.builder \
                         .appName("MemoryManagementOptimization") \
                         .config("spark.memory.fraction", "0.6") \  # Spark内存占总内存的比例
                         .config("spark.memory.storageFraction", "0.5") \  # 存储内存占Spark内存的比例
                         .config("spark.memory.useLegacyMode", "false") \  # 使用统一内存管理
                         .config("spark.sql.execution.arrow.enabled", "true") \  # 启用Arrow优化
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== 内存配置信息 ===")
    print(f"spark.memory.fraction: {spark.conf.get('spark.memory.fraction')}")
    print(f"spark.memory.storageFraction: {spark.conf.get('spark.memory.storageFraction')}")
    print(f"spark.memory.useLegacyMode: {spark.conf.get('spark.memory.useLegacyMode')}")
    
    # 创建一个较大的数据集
    print("\n创建大数据集...")
    start_time = time.time()
    large_data = [(i, f"user_{i}", i % 100) for i in range(10000000)]  # 1000万条记录
    df = spark.createDataFrame(large_data, ["id", "name", "group"])
    end_time = time.time()
    print(f"数据创建耗时: {end_time - start_time:.2f}秒")
    
    # 测试不同存储级别的内存使用
    print("\n=== 测试不同存储级别 ===")
    
    # 1. MEMORY_ONLY
    start_time = time.time()
    df.persist(StorageLevel.MEMORY_ONLY)
    count = df.count()  # 触发缓存
    end_time = time.time()
    print(f"MEMORY_ONLY: 缓存耗时 {end_time - start_time:.2f}秒, 记录数: {count}")
    
    # 解除缓存
    df.unpersist()
    
    # 2. MEMORY_AND_DISK
    start_time = time.time()
    df.persist(StorageLevel.MEMORY_AND_DISK)
    count = df.count()  # 触发缓存
    end_time = time.time()
    print(f"MEMORY_AND_DISK: 缓存耗时 {end_time - start_time:.2f}秒, 记录数: {count}")
    
    # 解除缓存
    df.unpersist()
    
    # 3. MEMORY_ONLY_SER
    start_time = time.time()
    df.persist(StorageLevel.MEMORY_ONLY_SER)
    count = df.count()  # 触发缓存
    end_time = time.time()
    print(f"MEMORY_ONLY_SER: 缓存耗时 {end_time - start_time:.2f}秒, 记录数: {count}")
    
    # 解除缓存
    df.unpersist()
    
    # 4. MEMORY_AND_DISK_SER
    start_time = time.time()
    df.persist(StorageLevel.MEMORY_AND_DISK_SER)
    count = df.count()  # 触发缓存
    end_time = time.time()
    print(f"MEMORY_AND_DISK_SER: 缓存耗时 {end_time - start_time:.2f}秒, 记录数: {count}")
    
    # 解除缓存
    df.unpersist()
    
    # 测试序列化对性能的影响
    print("\n=== 测试序列化对性能的影响 ===")
    
    # 关闭序列化
    spark.conf.set("spark.serializer", "org.apache.spark.serializer.JavaSerializer")
    
    start_time = time.time()
    transformed_df = df.filter(df["group"] > 50).groupBy("group").count()
    transformed_df.collect()
    end_time = time.time()
    java_serializer_time = end_time - start_time
    print(f"Java序列化耗时: {java_serializer_time:.2f}秒")
    
    # 启用Kryo序列化
    spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    
    start_time = time.time()
    transformed_df = df.filter(df["group"] > 50).groupBy("group").count()
    transformed_df.collect()
    end_time = time.time()
    kryo_serializer_time = end_time - start_time
    print(f"Kryo序列化耗时: {kryo_serializer_time:.2f}秒")
    print(f"性能提升: {java_serializer_time / kryo_serializer_time:.2f}倍")
    
    spark.stop()

if __name__ == "__main__":
    memory_management_optimization()
```

### 8.2.2 垃圾回收优化

```python
# code/performance-tuning/gc_optimization.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time

def gc_optimization():
    """垃圾回收优化演示"""
    
    # 创建SparkSession，配置GC参数
    spark = SparkSession.builder \
                         .appName("GCOptimization") \
                         .config("spark.executor.extraJavaOptions", 
                                "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:MaxGCPauseMillis=200") \
                         .config("spark.driver.extraJavaOptions", 
                                "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:MaxGCPauseMillis=200") \
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== GC配置信息 ===")
    print(f"spark.executor.extraJavaOptions: {spark.conf.get('spark.executor.extraJavaOptions')}")
    print(f"spark.driver.extraJavaOptions: {spark.conf.get('spark.driver.extraJavaOptions')}")
    
    # 创建大数据集
    print("\n创建大数据集...")
    start_time = time.time()
    
    # 生成大量中间数据，触发GC
    large_data = []
    for i in range(100000):
        # 每条记录包含多个字段，增加内存压力
        large_data.append((
            i, f"user_{i}", f"email_{i}@example.com", 
            f"address_{i}", i % 100, i % 50, i % 25, 
            i * 0.1, i * 0.2, i * 0.3
        ))
    
    df = spark.createDataFrame(large_data, [
        "id", "name", "email", "address", "group1", "group2", "group3", "value1", "value2", "value3"
    ])
    end_time = time.time()
    print(f"数据创建耗时: {end_time - start_time:.2f}秒")
    
    # 执行复杂的转换操作
    print("\n执行复杂转换操作...")
    start_time = time.time()
    
    # 多次转换，创建大量中间对象
    transformed_df = df.filter(df["group1"] > 20) \
                      .withColumn("new_value1", df["value1"] * 2) \
                      .withColumn("new_value2", df["value2"] * 3) \
                      .filter(df["group2"] < 30) \
                      .groupBy("group1", "group2") \
                      .agg({
                          "new_value1": "sum",
                          "new_value2": "avg",
                          "value3": "max"
                      })
    
    result = transformed_df.collect()
    end_time = time.time()
    print(f"复杂转换耗时: {end_time - start_time:.2f}秒")
    print(f"结果数量: {len(result)}")
    
    # 测试不同数据结构对GC的影响
    print("\n测试不同数据结构对GC的影响...")
    
    # 1. 使用元组
    start_time = time.time()
    tuple_rdd = sc.parallelize([(i, i*2, i*3) for i in range(1000000)])
    tuple_result = tuple_rdd.map(lambda x: (x[0], x[1] + x[2])).filter(lambda x: x[1] % 3 == 0).count()
    tuple_time = time.time() - start_time
    print(f"元组结构耗时: {tuple_time:.2f}秒, 结果: {tuple_result}")
    
    # 2. 使用字典
    start_time = time.time()
    dict_rdd = sc.parallelize([{"id": i, "value1": i*2, "value2": i*3} for i in range(1000000)])
    dict_result = dict_rdd.map(lambda x: (x["id"], x["value1"] + x["value2"])).filter(lambda x: x[1] % 3 == 0).count()
    dict_time = time.time() - start_time
    print(f"字典结构耗时: {dict_time:.2f}秒, 结果: {dict_result}")
    
    print(f"性能比: {dict_time / tuple_time:.2f}倍")
    
    spark.stop()

if __name__ == "__main__":
    gc_optimization()
```

## 8.3 并行度与分区优化

并行度和分区设置直接影响Spark应用程序的执行效率和资源利用率。

### 8.3.1 分区策略优化

```python
# code/performance-tuning/partition_optimization.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand
import time

def partition_optimization():
    """分区优化演示"""
    
    # 创建SparkSession
    spark = SparkSession.builder \
                         .appName("PartitionOptimization") \
                         .config("spark.sql.shuffle.partitions", "200") \  # 设置shuffle分区数
                         .getOrCreate()
    
    print("=== 分区配置信息 ===")
    print(f"spark.sql.shuffle.partitions: {spark.conf.get('spark.sql.shuffle.partitions')}")
    
    # 创建大数据集
    print("\n创建大数据集...")
    start_time = time.time()
    data = [(i, f"user_{i}", i % 100, i % 50) for i in range(10000000)]  # 1000万条记录
    df = spark.createDataFrame(data, ["id", "name", "group1", "group2"])
    end_time = time.time()
    print(f"数据创建耗时: {end_time - start_time:.2f}秒")
    print(f"初始分区数: {df.rdd.getNumPartitions()}")
    
    # 测试不同分区数对性能的影响
    partition_counts = [10, 50, 100, 200, 500]
    
    for partition_count in partition_counts:
        print(f"\n=== 测试分区数: {partition_count} ===")
        
        # 重新分区
        start_time = time.time()
        repartitioned_df = df.repartition(partition_count)
        end_time = time.time()
        repartition_time = end_time - start_time
        print(f"重新分区耗时: {repartition_time:.2f}秒")
        print(f"重新分区后分区数: {repartitioned_df.rdd.getNumPartitions()}")
        
        # 执行聚合操作
        start_time = time.time()
        result = repartitioned_df.groupBy("group1").count().collect()
        end_time = time.time()
        aggregation_time = end_time - start_time
        print(f"聚合操作耗时: {aggregation_time:.2f}秒")
        print(f"结果数量: {len(result)}")
    
    # 测试coalesce与repartition的性能差异
    print("\n=== coalesce vs repartition ===")
    
    # coalesce - 减少分区，避免shuffle
    start_time = time.time()
    coalesced_df = df.coalesce(50)
    coalesced_count = coalesced_df.groupBy("group1").count().collect()
    coalesce_time = time.time() - start_time
    print(f"coalesce到50分区耗时: {coalesce_time:.2f}秒")
    
    # repartition - 增加分区，会触发shuffle
    start_time = time.time()
    repartitioned_df = df.repartition(50)
    repartitioned_count = repartitioned_df.groupBy("group1").count().collect()
    repartition_time = time.time() - start_time
    print(f"repartition到50分区耗时: {repartition_time:.2f}秒")
    
    print(f"性能差异: {repartition_time / coalesce_time:.2f}倍")
    
    # 自定义分区器优化
    print("\n=== 自定义分区器优化 ===")
    
    # 基于业务逻辑的分区
    from pyspark.sql import Window
    from pyspark.sql.functions import row_number
    
    # 按group1字段进行分区优化
    start_time = time.time()
    
    # 使用Window函数分区处理
    window_spec = Window.partitionBy("group1").orderBy(rand())
    windowed_df = df.withColumn("row_num", row_number().over(window_spec))
    
    # 按group1进行重新分区
    optimized_df = windowed_df.repartition(100, "group1")
    
    # 执行聚合
    optimized_result = optimized_df.groupBy("group1").count().collect()
    
    end_time = time.time()
    optimized_time = end_time - start_time
    print(f"基于业务逻辑的分区优化耗时: {optimized_time:.2f}秒")
    print(f"结果数量: {len(optimized_result)}")
    
    spark.stop()

if __name__ == "__main__":
    partition_optimization()
```

### 8.3.2 并行度设置与动态资源分配

```python
# code/performance-tuning/parallelism_tuning.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time

def parallelism_tuning():
    """并行度设置与动态资源分配演示"""
    
    # 创建SparkSession，配置并行度参数
    spark = SparkSession.builder \
                         .appName("ParallelismTuning") \
                         .config("spark.default.parallelism", "200") \  # 默认并行度
                         .config("spark.sql.shuffle.partitions", "200") \  # SQL shuffle并行度
                         .config("spark.dynamicAllocation.enabled", "true") \  # 启用动态分配
                         .config("spark.dynamicAllocation.minExecutors", "2") \  # 最小Executor数
                         .config("spark.dynamicAllocation.maxExecutors", "10") \  # 最大Executor数
                         .config("spark.dynamicAllocation.initialExecutors", "4") \  # 初始Executor数
                         .config("spark.shuffle.service.enabled", "true") \  # 启用shuffle服务
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== 并行度配置信息 ===")
    print(f"spark.default.parallelism: {spark.conf.get('spark.default.parallelism')}")
    print(f"spark.sql.shuffle.partitions: {spark.conf.get('spark.sql.shuffle.partitions')}")
    print(f"spark.dynamicAllocation.enabled: {spark.conf.get('spark.dynamicAllocation.enabled')}")
    print(f"spark.dynamicAllocation.minExecutors: {spark.conf.get('spark.dynamicAllocation.minExecutors')}")
    print(f"spark.dynamicAllocation.maxExecutors: {spark.conf.get('spark.dynamicAllocation.maxExecutors')}")
    print(f"spark.dynamicAllocation.initialExecutors: {spark.conf.get('spark.dynamicAllocation.initialExecutors')}")
    
    # 创建大数据集
    print("\n创建大数据集...")
    start_time = time.time()
    
    # 生成多个数据集，模拟复杂工作负载
    data1 = [(i, f"item_{i}", i % 100, i * 0.1) for i in range(5000000)]
    data2 = [(i, f"product_{i}", i % 50, i * 0.2) for i in range(3000000)]
    data3 = [(i, f"order_{i}", i % 200, i * 0.3) for i in range(2000000)]
    
    df1 = spark.createDataFrame(data1, ["id", "name", "category", "value"])
    df2 = spark.createDataFrame(data2, ["id", "name", "type", "price"])
    df3 = spark.createDataFrame(data3, ["id", "name", "status", "amount"])
    
    end_time = time.time()
    print(f"数据创建耗时: {end_time - start_time:.2f}秒")
    
    # 缓存数据，提高重复访问性能
    print("\n缓存数据...")
    start_time = time.time()
    df1.cache()
    df2.cache()
    df3.cache()
    
    # 触发缓存
    df1.count()
    df2.count()
    df3.count()
    
    end_time = time.time()
    print(f"数据缓存耗时: {end_time - start_time:.2f}秒")
    
    # 执行并行操作
    print("\n执行并行操作...")
    start_time = time.time()
    
    # 使用union和join操作创建复杂查询
    combined_df = df1.join(df2, "id", "inner").join(df3, "id", "left")
    
    # 执行多个聚合操作
    result1 = combined_df.groupBy("category").agg({"value": "sum", "price": "avg"}).collect()
    result2 = combined_df.groupBy("type").agg({"amount": "sum", "price": "max"}).collect()
    result3 = combined_df.filter(combined_df["status"] == "active").groupBy("category").count().collect()
    
    end_time = time.time()
    print(f"并行操作耗时: {end_time - start_time:.2f}秒")
    print(f"结果1数量: {len(result1)}")
    print(f"结果2数量: {len(result2)}")
    print(f"结果3数量: {len(result3)}")
    
    # 演示SQL并行度设置
    print("\n=== SQL并行度设置 ===")
    
    # 创建临时视图
    df1.createOrReplaceTempView("items")
    df2.createOrReplaceTempView("products")
    df3.createOrReplaceTempView("orders")
    
    # 执行SQL查询
    start_time = time.time()
    
    sql_result1 = spark.sql("""
        SELECT category, SUM(value) as total_value, AVG(price) as avg_price
        FROM items i JOIN products p ON i.id = p.id
        GROUP BY category
        ORDER BY total_value DESC
        LIMIT 10
    """).collect()
    
    sql_result2 = spark.sql("""
        SELECT type, SUM(amount) as total_amount, MAX(price) as max_price
        FROM items i JOIN products p ON i.id = p.id LEFT JOIN orders o ON i.id = o.id
        GROUP BY type
        ORDER BY total_amount DESC
        LIMIT 10
    """).collect()
    
    end_time = time.time()
    print(f"SQL查询耗时: {end_time - start_time:.2f}秒")
    print(f"SQL结果1数量: {len(sql_result1)}")
    print(f"SQL结果2数量: {len(sql_result2)}")
    
    spark.stop()

if __name__ == "__main__":
    parallelism_tuning()
```

## 8.4 数据倾斜处理

数据倾斜是Spark性能优化中的常见问题，指数据在分区中分布不均匀，导致某些任务执行时间远长于其他任务。

### 8.4.1 数据倾斜检测与处理

```python
# code/performance-tuning/data_skew.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, rand, when
import time

def data_skew_detection_and_handling():
    """数据倾斜检测与处理演示"""
    
    # 创建SparkSession
    spark = SparkSession.builder \
                         .appName("DataSkewDetectionAndHandling") \
                         .config("spark.sql.adaptive.enabled", "true") \  # 启用自适应查询执行
                         .config("spark.sql.adaptive.skewJoin.enabled", "true") \  # 启用倾斜连接优化
                         .config("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5") \  # 倾斜分区因子
                         .config("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB") \  # 倾斜分区阈值
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== 数据倾斜配置信息 ===")
    print(f"spark.sql.adaptive.enabled: {spark.conf.get('spark.sql.adaptive.enabled')}")
    print(f"spark.sql.adaptive.skewJoin.enabled: {spark.conf.get('spark.sql.adaptive.skewJoin.enabled')}")
    
    # 创建倾斜数据集
    print("\n创建倾斜数据集...")
    start_time = time.time()
    
    # 创建第一个表，大部分数据集中在少数几个key上
    skewed_data1 = []
    for i in range(1000000):
        if i < 100:  # 0.01%的数据占用了大量记录
            key = "skewed_key"
        else:
            key = f"normal_key_{i % 1000}"  # 正常分布的key
        skewed_data1.append((key, f"value_{i}", i % 10))
    
    # 创建第二个表，与第一个表有相同的key分布
    skewed_data2 = []
    for i in range(100000):
        if i < 10:
            key = "skewed_key"
        else:
            key = f"normal_key_{i % 1000}"
        skewed_data2.append((key, f"other_value_{i}", i % 5))
    
    df1 = spark.createDataFrame(skewed_data1, ["key", "value", "category"])
    df2 = spark.createDataFrame(skewed_data2, ["key", "other_value", "type"])
    
    end_time = time.time()
    print(f"倾斜数据创建耗时: {end_time - start_time:.2f}秒")
    
    # 检测数据倾斜
    print("\n=== 检测数据倾斜 ===")
    
    # 统计每个key的记录数
    key_counts1 = df1.groupBy("key").agg(count("*").alias("count")).orderBy(col("count").desc())
    key_counts2 = df2.groupBy("key").agg(count("*").alias("count")).orderBy(col("count").desc())
    
    print("表1中的key分布:")
    key_counts1.show(10)
    
    print("表2中的key分布:")
    key_counts2.show(10)
    
    # 处理数据倾斜前的连接操作
    print("\n=== 处理数据倾斜前的连接操作 ===")
    start_time = time.time()
    
    # 执行join操作
    skewed_join = df1.join(df2, "key", "inner")
    skewed_result = skewed_join.collect()
    
    end_time = time.time()
    skewed_time = end_time - start_time
    print(f"倾斜数据连接耗时: {skewed_time:.2f}秒")
    print(f"结果记录数: {len(skewed_result)}")
    
    # 方法1: 使用随机前缀处理数据倾斜
    print("\n=== 方法1: 使用随机前缀处理数据倾斜 ===")
    
    # 为倾斜key添加随机前缀
    df1_with_prefix = df1.withColumn(
        "prefixed_key", 
        when(col("key") == "skewed_key", concat(col("key"), lit("_"), (rand() * 5).cast("int")))
        .otherwise(col("key"))
    )
    
    df2_with_prefix = df2.withColumn(
        "prefixed_key", 
        when(col("key") == "skewed_key", concat(col("key"), lit("_"), (rand() * 5).cast("int")))
        .otherwise(col("key"))
    )
    
    # 执行连接操作
    start_time = time.time()
    
    prefix_join = df1_with_prefix.join(df2_with_prefix, "prefixed_key", "inner")
    prefix_result = prefix_join.collect()
    
    end_time = time.time()
    prefix_time = end_time - start_time
    print(f"使用随机前缀连接耗时: {prefix_time:.2f}秒")
    print(f"结果记录数: {len(prefix_result)}")
    print(f"性能提升: {skewed_time / prefix_time:.2f}倍")
    
    # 方法2: 使用广播表处理数据倾斜
    print("\n=== 方法2: 使用广播表处理数据倾斜 ===")
    
    # 找出倾斜的key
    skewed_keys = key_counts1.filter(col("count") > 1000).select("key").rdd.map(lambda row: row.key).collect()
    print(f"倾斜的keys: {skewed_keys}")
    
    # 将倾斜的数据广播
    if skewed_keys:
        skewed_df1 = df1.filter(col("key").isin(skewed_keys))
        normal_df1 = df1.filter(~col("key").isin(skewed_keys))
        
        skewed_df2 = df2.filter(col("key").isin(skewed_keys))
        normal_df2 = df2.filter(~col("key").isin(skewed_keys))
        
        # 广播倾斜数据
        from pyspark.sql.functions import broadcast
        broadcast_join1 = broadcast(skewed_df1).join(skewed_df2, "key", "inner")
        
        # 正常数据使用常规join
        normal_join = normal_df1.join(normal_df2, "key", "inner")
        
        start_time = time.time()
        
        # 合并结果
        broadcast_result = broadcast_join1.union(normal_join).collect()
        
        end_time = time.time()
        broadcast_time = end_time - start_time
        print(f"使用广播表连接耗时: {broadcast_time:.2f}秒")
        print(f"结果记录数: {len(broadcast_result)}")
        print(f"性能提升: {skewed_time / broadcast_time:.2f}倍")
    
    spark.stop()

if __name__ == "__main__":
    # 导入需要的函数
    from pyspark.sql.functions import concat, lit
    data_skew_detection_and_handling()
```

## 8.5 查询优化

Spark SQL和DataFrame提供了多种查询优化技术，包括谓词下推、列裁剪、连接优化等。

### 8.5.1 Catalyst优化器与查询计划分析

```python
# code/performance-tuning/query_optimization.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, broadcast
import time

def query_optimization():
    """查询优化演示"""
    
    # 创建SparkSession，启用查询优化
    spark = SparkSession.builder \
                         .appName("QueryOptimization") \
                         .config("spark.sql.adaptive.enabled", "true") \  # 启用自适应查询执行
                         .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \  # 启用分区合并
                         .config("spark.sql.adaptive.localShuffleReader.enabled", "true") \  # 启用本地shuffle读取
                         .config("spark.sql.autoBroadcastJoinThreshold", "10MB") \  # 设置广播join阈值
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== 查询优化配置信息 ===")
    print(f"spark.sql.adaptive.enabled: {spark.conf.get('spark.sql.adaptive.enabled')}")
    print(f"spark.sql.adaptive.coalescePartitions.enabled: {spark.conf.get('spark.sql.adaptive.coalescePartitions.enabled')}")
    print(f"spark.sql.adaptive.localShuffleReader.enabled: {spark.conf.get('spark.sql.adaptive.localShuffleReader.enabled')}")
    print(f"spark.sql.autoBroadcastJoinThreshold: {spark.conf.get('spark.sql.autoBroadcastJoinThreshold')}")
    
    # 创建测试数据
    print("\n创建测试数据...")
    start_time = time.time()
    
    # 创建员工表
    employees_data = [
        (1, "Alice", 34, "Engineering", 85000, 2018),
        (2, "Bob", 28, "Marketing", 72000, 2019),
        (3, "Charlie", 45, "Engineering", 120000, 2015),
        (4, "David", 32, "Sales", 78000, 2019),
        (5, "Eve", 29, "Engineering", 95000, 2020),
        (6, "Frank", 51, "Management", 150000, 2010),
        (7, "Grace", 26, "Marketing", 65000, 2021),
        (8, "Henry", 38, "Engineering", 110000, 2017),
        (9, "Iris", 41, "Sales", 92000, 2016),
        (10, "Jack", 33, "Engineering", 98000, 2018)
    ] * 100000  # 乘以100000创建大数据集
    
    employees = spark.createDataFrame(employees_data, ["emp_id", "name", "age", "department", "salary", "hire_year"])
    
    # 创建部门表
    departments_data = [
        (1, "Engineering", "Building A"),
        (2, "Marketing", "Building B"),
        (3, "Sales", "Building C"),
        (4, "Management", "Building D"),
        (5, "HR", "Building E")
    ] * 100000  # 乘以100000创建大数据集
    
    departments = spark.createDataFrame(departments_data, ["dept_id", "dept_name", "location"])
    
    # 创建工资历史表
    salary_history_data = []
    for i in range(1, 11):  # 10个员工
        for year in range(2015, 2022):  # 7年
            base_salary = 50000 + i * 2000 + (year - 2015) * 3000
            for _ in range(100000):  # 每年10万条记录
                salary_variation = base_salary + (year * 100) + (i * 50)
                salary_history_data.append((i, year, salary_variation))
    
    salary_history = spark.createDataFrame(salary_history_data, ["emp_id", "year", "salary"])
    
    end_time = time.time()
    print(f"数据创建耗时: {end_time - start_time:.2f}秒")
    
    # 创建临时视图
    employees.createOrReplaceTempView("employees")
    departments.createOrReplaceTempView("departments")
    salary_history.createOrReplaceTempView("salary_history")
    
    # 查询计划分析
    print("\n=== 查询计划分析 ===")
    
    # 简单查询
    simple_query = employees.filter(employees["department"] == "Engineering").select("name", "salary")
    
    print("简单查询的执行计划:")
    simple_query.explain(extended=True)
    
    # 复杂连接查询
    complex_query = employees.join(
        departments, 
        employees["department"] == departments["dept_name"], 
        "inner"
    ).join(
        salary_history,
        (employees["emp_id"] == salary_history["emp_id"]) & (employees["hire_year"] == salary_history["year"]),
        "inner"
    ).select(
        employees["name"], 
        employees["department"], 
        departments["location"],
        salary_history["salary"]
    )
    
    print("\n复杂连接查询的执行计划:")
    complex_query.explain(extended=True)
    
    # 谓词下推优化
    print("\n=== 谓词下推优化 ===")
    
    # 未优化：先连接后过滤
    start_time = time.time()
    unoptimized_result = employees.join(departments, employees["department"] == departments["dept_name"]) \
                                .filter(departments["dept_name"] == "Engineering") \
                                .select(employees["name"], employees["salary"]) \
                                .collect()
    unoptimized_time = time.time() - start_time
    print(f"先连接后过滤耗时: {unoptimized_time:.2f}秒")
    print(f"结果数量: {len(unoptimized_result)}")
    
    # 优化：先过滤后连接
    start_time = time.time()
    filtered_employees = employees.filter(employees["department"] == "Engineering")
    optimized_result = filtered_employees.join(
        departments, 
        filtered_employees["department"] == departments["dept_name"]
    ).select(filtered_employees["name"], filtered_employees["salary"]).collect()
    optimized_time = time.time() - start_time
    print(f"先过滤后连接耗时: {optimized_time:.2f}秒")
    print(f"结果数量: {len(optimized_result)}")
    print(f"性能提升: {unoptimized_time / optimized_time:.2f}倍")
    
    # 列裁剪优化
    print("\n=== 列裁剪优化 ===")
    
    # 查询所有列
    start_time = time.time()
    all_columns_result = employees.select("*").filter(employees["department"] == "Engineering").collect()
    all_columns_time = time.time() - start_time
    print(f"查询所有列耗时: {all_columns_time:.2f}秒")
    
    # 只查询需要的列
    start_time = time.time()
    selected_columns_result = employees.select("name", "salary").filter(employees["department"] == "Engineering").collect()
    selected_columns_time = time.time() - start_time
    print(f"查询选定列耗时: {selected_columns_time:.2f}秒")
    print(f"性能提升: {all_columns_time / selected_columns_time:.2f}倍")
    
    # 广播连接优化
    print("\n=== 广播连接优化 ===")
    
    # 小表departments可以广播
    start_time = time.time()
    broadcast_result = employees.join(broadcast(departments), 
                                    employees["department"] == departments["dept_name"]).collect()
    broadcast_time = time.time() - start_time
    print(f"广播连接耗时: {broadcast_time:.2f}秒")
    print(f"结果数量: {len(broadcast_result)}")
    
    spark.stop()

if __name__ == "__main__":
    query_optimization()
```

## 8.6 作业监控与故障排查

有效的作业监控和故障排查是确保Spark应用程序稳定运行的关键。

### 8.6.1 作业监控

```python
# code/performance-tuning/job_monitoring.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time

def job_monitoring():
    """作业监控演示"""
    
    # 创建SparkSession
    spark = SparkSession.builder \
                         .appName("JobMonitoring") \
                         .config("spark.ui.enabled", "true") \  # 启用Spark UI
                         .config("spark.eventLog.enabled", "true") \  # 启用事件日志
                         .config("spark.eventLog.dir", "logs/spark-events") \  # 事件日志目录
                         .config("spark.history.fs.logDirectory", "logs/spark-events") \  # 历史服务器日志目录
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== 作业监控配置信息 ===")
    print(f"spark.ui.enabled: {spark.conf.get('spark.ui.enabled')}")
    print(f"spark.eventLog.enabled: {spark.conf.get('spark.eventLog.enabled')}")
    print(f"spark.eventLog.dir: {spark.conf.get('spark.eventLog.dir')}")
    print(f"spark.history.fs.logDirectory: {spark.conf.get('spark.history.fs.logDirectory')}")
    print(f"Spark UI地址: {sc.uiWebUrl}")
    
    # 设置监听器
    from pyspark import SparkListener, SparkListenerJobStart, SparkListenerJobEnd, SparkListenerStageCompleted
    
    class JobMonitoringListener(SparkListener):
        def __init__(self):
            super(JobMonitoringListener, self).__init__()
            self.job_metrics = []
        
        def onJobStart(self, jobStart):
            job_id = jobStart.jobId
            stage_ids = jobStart.stageIds
            print(f"\n=== 作业开始 ===")
            print(f"作业ID: {job_id}")
            print(f"阶段IDs: {stage_ids}")
            start_time = time.time()
            self.job_metrics.append({"job_id": job_id, "start_time": start_time, "stage_ids": stage_ids})
        
        def onJobEnd(self, jobEnd):
            job_id = jobEnd.jobId
            job_result = jobEnd.jobResult
            end_time = time.time()
            
            # 找到对应的作业开始时间
            start_time = None
            for metric in self.job_metrics:
                if metric["job_id"] == job_id:
                    start_time = metric["start_time"]
                    metric["end_time"] = end_time
                    metric["duration"] = end_time - start_time
                    metric["result"] = job_result
                    break
            
            print(f"\n=== 作业结束 ===")
            print(f"作业ID: {job_id}")
            print(f"作业结果: {job_result}")
            if start_time:
                print(f"作业耗时: {end_time - start_time:.2f}秒")
        
        def onStageCompleted(self, stageCompleted):
            stage_info = stageCompleted.stageInfo
            stage_id = stage_info.stageId
            stage_name = stage_info.name
            task_metrics = stage_info.taskMetrics
            duration = stage_info.completionTime - stage_info.submissionTime
            
            print(f"\n=== 阶段完成 ===")
            print(f"阶段ID: {stage_id}")
            print(f"阶段名称: {stage_name}")
            print(f"阶段耗时: {duration / 1000:.2f}秒")  # 毫秒转秒
            if task_metrics:
                print(f"任务执行时间: {task_metrics.executorRunTime / 1000:.2f}秒")
                print(f" shuffle读取: {task_metrics.shuffleReadMetrics.totalBytesRead / (1024*1024):.2f}MB")
                print(f" shuffle写入: {task_metrics.shuffleWriteMetrics.bytesWritten / (1024*1024):.2f}MB")
    
    # 添加监听器
    listener = JobMonitoringListener()
    sc.addSparkListener(listener)
    
    # 执行多个作业
    print("\n=== 执行作业 ===")
    
    # 创建测试数据
    print("\n创建测试数据...")
    data = [(i, f"user_{i}", i % 100) for i in range(1000000)]
    df = spark.createDataFrame(data, ["id", "name", "group"])
    
    # 作业1: 简单计数
    print("\n执行作业1: 简单计数")
    start_time = time.time()
    count = df.count()
    end_time = time.time()
    print(f"作业1结果: {count}, 耗时: {end_time - start_time:.2f}秒")
    
    # 作业2: 分组计数
    print("\n执行作业2: 分组计数")
    start_time = time.time()
    group_counts = df.groupBy("group").count().collect()
    end_time = time.time()
    print(f"作业2结果数量: {len(group_counts)}, 耗时: {end_time - start_time:.2f}秒")
    
    # 作业3: 复杂聚合
    print("\n执行作业3: 复杂聚合")
    start_time = time.time()
    complex_result = df.filter(df["group"] > 50) \
                      .groupBy("group") \
                      .agg({"id": "count", "group": "max"}) \
                      .collect()
    end_time = time.time()
    print(f"作业3结果数量: {len(complex_result)}, 耗时: {end_time - start_time:.2f}秒")
    
    # 打印监听器收集的指标
    print("\n=== 监听器收集的指标 ===")
    for metric in listener.job_metrics:
        if "duration" in metric:
            print(f"作业ID: {metric['job_id']}, 耗时: {metric['duration']:.2f}秒, 结果: {metric.get('result', 'Unknown')}")
    
    spark.stop()

if __name__ == "__main__":
    job_monitoring()
```

### 8.6.2 故障排查

```python
# code/performance-tuning/troubleshooting.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.storagelevel import StorageLevel
import time

def troubleshooting():
    """故障排查演示"""
    
    # 创建SparkSession，配置故障排查参数
    spark = SparkSession.builder \
                         .appName("Troubleshooting") \
                         .config("spark.ui.enabled", "true") \  # 启用Spark UI
                         .config("spark.eventLog.enabled", "true") \  # 启用事件日志
                         .config("spark.eventLog.dir", "logs/spark-events") \  # 事件日志目录
                         .config("spark.sql.execution.arrow.pyspark.enabled", "true") \  # 启用Arrow优化
                         .config("spark.sql.adaptive.enabled", "true") \  # 启用自适应查询执行
                         .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \  # 启用分区合并
                         .config("spark.sql.adaptive.skewJoin.enabled", "true") \  # 启用倾斜连接优化
                         .getOrCreate()
    
    sc = spark.sparkContext
    
    print("=== 故障排查配置信息 ===")
    print(f"Spark UI地址: {sc.uiWebUrl}")
    print(f"spark.eventLog.dir: {spark.conf.get('spark.eventLog.dir')}")
    
    # 常见问题1: 内存不足
    print("\n=== 问题1: 内存不足 ===")
    print("症状: OutOfMemoryError")
    print("解决方案:")
    print("1. 增加Executor内存: spark.executor.memory")
    print("2. 使用序列化存储: MEMORY_ONLY_SER")
    print("3. 减少分区大小，增加分区数")
    print("4. 使用广播变量减少数据传输")
    
    # 演示内存优化
    print("\n内存优化演示:")
    data = [(i, f"user_{i}", i % 1000) for i in range(1000000)]
    df = spark.createDataFrame(data, ["id", "name", "group"])
    
    # 使用序列化存储
    df.persist(StorageLevel.MEMORY_ONLY_SER)
    count = df.count()
    print(f"使用序列化存储的记录数: {count}")
    df.unpersist()
    
    # 常见问题2: 数据倾斜
    print("\n=== 问题2: 数据倾斜 ===")
    print("症状: 某些任务执行时间特别长")
    print("解决方案:")
    print("1. 使用随机前缀打散倾斜的key")
    print("2. 使用广播表处理小表")
    print("3. 启用自适应查询执行和倾斜连接优化")
    print("4. 调整分区数")
    
    # 演示数据倾斜处理
    from pyspark.sql.functions import when, concat, lit, rand
    
    # 创建倾斜数据
    skewed_data = []
    for i in range(100000):
        if i < 1000:
            key = "skewed_key"
        else:
            key = f"normal_key_{i % 1000}"
        skewed_data.append((key, f"value_{i}"))
    
    skewed_df = spark.createDataFrame(skewed_data, ["key", "value"])
    
    # 使用随机前缀处理倾斜
    fixed_df = skewed_df.withColumn(
        "prefixed_key",
        when(col("key") == "skewed_key", concat(col("key"), lit("_"), (rand() * 10).cast("int")))
        .otherwise(col("key"))
    )
    
    result = fixed_df.groupBy("prefixed_key").count().collect()
    print(f"处理倾斜后的结果数量: {len(result)}")
    
    # 常见问题3: 分区不均
    print("\n=== 问题3: 分区不均 ===")
    print("症状: 部分分区数据量过大，部分分区数据量过小")
    print("解决方案:")
    print("1. 使用repartition调整分区数")
    print("2. 使用自定义分区器按业务逻辑分区")
    print("3. 使用coalesce减少分区（避免shuffle）")
    
    # 演示分区优化
    initial_partitions = df.rdd.getNumPartitions()
    print(f"初始分区数: {initial_partitions}")
    
    # 使用repartition增加分区
    repartitioned_df = df.repartition(100)
    repartitioned_partitions = repartitioned_df.rdd.getNumPartitions()
    print(f"重新分区后分区数: {repartitioned_partitions}")
    
    # 使用coalesce减少分区
    coalesced_df = df.coalesce(50)
    coalesced_partitions = coalesced_df.rdd.getNumPartitions()
    print(f"合并后分区数: {coalesced_partitions}")
    
    # 常见问题4: 执行计划不佳
    print("\n=== 问题4: 执行计划不佳 ===")
    print("症状: 查询执行时间长，资源利用率低")
    print("解决方案:")
    print("1. 使用explain()分析执行计划")
    print("2. 启用自适应查询执行")
    print("3. 优化SQL语句，避免不必要的连接和排序")
    print("4. 使用合适的存储格式（如Parquet）")
    
    # 演示执行计划分析
    print("\n执行计划分析:")
    
    # 创建复杂查询
    complex_query = df.filter(col("group") > 500) \
                    .groupBy("group") \
                    .agg({"id": "count", "group": "max"}) \
                    .filter(col("count(id)") > 100)
    
    # 分析执行计划
    print("逻辑计划:")
    complex_query.explain(extended=False)
    
    print("\n物理计划:")
    complex_query.explain(extended=True)
    
    # 执行查询
    result = complex_query.collect()
    print(f"查询结果数量: {len(result)}")
    
    spark.stop()

if __name__ == "__main__":
    troubleshooting()
```

## 8.7 生产环境最佳实践

在生产环境中运行Spark应用程序需要考虑安全性、可靠性、可扩展性和监控等方面。

### 8.7.1 生产环境配置

```python
# code/production-templates/production_config.py
def production_spark_config(app_name, executor_memory, driver_memory, executor_cores, num_executors):
    """生产环境Spark配置模板"""
    
    config = {
        # 应用程序配置
        "spark.app.name": app_name,
        
        # 资源配置
        "spark.executor.memory": executor_memory,
        "spark.driver.memory": driver_memory,
        "spark.executor.cores": executor_cores,
        "spark.executor.instances": num_executors,
        "spark.dynamicAllocation.enabled": "false",  # 生产环境通常关闭动态分配
        
        # 序列化配置
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        
        # 内存配置
        "spark.memory.fraction": "0.6",
        "spark.memory.storageFraction": "0.5",
        
        # SQL优化
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        
        # 网络配置
        "spark.network.timeout": "300s",
        "spark.rpc.askTimeout": "300s",
        
        # 日志配置
        "spark.eventLog.enabled": "true",
        "spark.eventLog.dir": "/var/log/spark/events",
        "spark.history.fs.logDirectory": "/var/log/spark/events",
        
        # 安全配置
        "spark.authenticate": "true",
        "spark.network.crypto.enabled": "true",
        
        # 错误处理
        "spark.task.maxFailures": "4",
        "spark.stage.maxConsecutiveAttempts": "4"
    }
    
    return config

def example_usage():
    """示例使用"""
    
    # 生产环境配置
    config = production_spark_config(
        app_name="ProductionExample",
        executor_memory="8g",
        driver_memory="4g",
        executor_cores=4,
        num_executors=10
    )
    
    # 打印配置
    print("=== 生产环境Spark配置 ===")
    for key, value in config.items():
        print(f"{key}: {value}")
    
    # 实际使用时，可以将这些配置应用到SparkSession
    # from pyspark.sql import SparkSession
    # spark = SparkSession.builder.appName("ProductionExample") \
    #                         .config("spark.executor.memory", "8g") \
    #                         .config("spark.driver.memory", "4g") \
    #                         ... 其他配置 ...
    #                         .getOrCreate()

if __name__ == "__main__":
    example_usage()
```

### 8.7.2 错误处理与重试机制

```python
# code/production-templates/error_handling.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time
import logging

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("SparkProduction")

class ProductionError(Exception):
    """生产环境自定义错误"""
    pass

def retry_operation(operation, max_retries=3, retry_interval=10, logger=None):
    """重试操作"""
    if logger is None:
        logger = setup_logging()
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试执行操作，第 {attempt + 1} 次")
            result = operation()
            logger.info(f"操作成功，尝试次数: {attempt + 1}")
            return result
        except Exception as e:
            last_exception = e
            logger.error(f"操作失败，尝试次数: {attempt + 1}, 错误: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_interval} 秒后重试...")
                time.sleep(retry_interval)
    
    raise ProductionError(f"操作在 {max_retries} 次尝试后仍然失败: {str(last_exception)}")

def robust_spark_operation():
    """健壮的Spark操作示例"""
    
    # 创建SparkSession
    spark = SparkSession.builder \
                         .appName("ProductionErrorHandling") \
                         .config("spark.task.maxFailures", "4") \  # 增加任务失败重试次数
                         .config("spark.stage.maxConsecutiveAttempts", "4") \  # 增加阶段失败重试次数
                         .getOrCreate()
    
    logger = setup_logging()
    
    try:
        # 定义可能失败的操作
        def load_data():
            """加载数据操作"""
            try:
                # 尝试加载可能不存在的数据
                data_path = "data/production_input.csv"
                df = spark.read.csv(data_path, header=True, inferSchema=True)
                return df
            except Exception as e:
                logger.error(f"加载数据失败: {str(e)}")
                raise
        
        def process_data(df):
            """处理数据操作"""
            try:
                # 可能失败的数据处理
                processed_df = df.filter(df["value"] > 0) \
                                .groupBy("category") \
                                .agg({"value": "sum"}) \
                                .filter("sum(value) > 1000")
                return processed_df
            except Exception as e:
                logger.error(f"数据处理失败: {str(e)}")
                raise
        
        def save_data(df):
            """保存数据操作"""
            try:
                # 可能失败的数据保存
                output_path = "data/production_output"
                df.write.mode("overwrite").parquet(output_path)
                return True
            except Exception as e:
                logger.error(f"保存数据失败: {str(e)}")
                raise
        
        # 使用重试机制执行操作
        logger.info("开始执行Spark操作")
        
        # 加载数据
        df = retry_operation(load_data, max_retries=3, retry_interval=5, logger=logger)
        logger.info(f"数据加载成功，记录数: {df.count()}")
        
        # 处理数据
        processed_df = retry_operation(lambda: process_data(df), max_retries=3, retry_interval=5, logger=logger)
        logger.info(f"数据处理成功，记录数: {processed_df.count()}")
        
        # 保存数据
        retry_operation(lambda: save_data(processed_df), max_retries=3, retry_interval=5, logger=logger)
        logger.info("数据保存成功")
        
        logger.info("Spark操作执行完成")
        
    except ProductionError as e:
        logger.error(f"生产环境错误: {str(e)}")
        # 发送告警通知
        alert_administrators(f"Spark应用程序失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        # 发送告警通知
        alert_administrators(f"Spark应用程序未知错误: {str(e)}")
        
    finally:
        spark.stop()
        logger.info("SparkSession已停止")

def alert_administrators(message):
    """向管理员发送告警"""
    # 实际实现中，这里可以发送邮件、短信或调用其他通知系统
    print(f"告警通知: {message}")

if __name__ == "__main__":
    robust_spark_operation()
```

### 8.7.3 监控与告警

```python
# code/production-templates/monitoring.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time
import psutil
import logging
import json

class SparkMonitoring:
    """Spark监控类"""
    
    def __init__(self, spark_context=None, spark_session=None):
        self.sc = spark_context
        self.spark = spark_session
        self.logger = logging.getLogger("SparkMonitoring")
        self.metrics = {}
        self.start_time = time.time()
    
    def collect_system_metrics(self):
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        system_metrics = {
            "timestamp": int(time.time()),
            "cpu_percent": cpu_percent,
            "memory_total": memory.total,
            "memory_used": memory.used,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_used": disk.used,
            "disk_percent": (disk.used / disk.total) * 100
        }
        
        return system_metrics
    
    def collect_spark_metrics(self):
        """收集Spark指标"""
        if not self.sc:
            return {}
        
        # 获取Spark应用信息
        app_id = self.sc.applicationId
        app_name = self.sc.appName
        
        # 获取Executor信息
        try:
            # 注意：在实际生产环境中，需要通过REST API或SparkListener获取更详细的指标
            metrics = {
                "timestamp": int(time.time()),
                "app_id": app_id,
                "app_name": app_name,
                "status": "running",
                "executor_memory_used": 0,  # 实际实现中需要获取真实值
                "executor_cores_used": 0,   # 实际实现中需要获取真实值
                "completed_tasks": 0,       # 实际实现中需要获取真实值
                "failed_tasks": 0          # 实际实现中需要获取真实值
            }
            return metrics
        except Exception as e:
            self.logger.error(f"收集Spark指标失败: {str(e)}")
            return {}
    
    def collect_job_metrics(self):
        """收集作业指标"""
        # 实际实现中，需要通过SparkListener或REST API获取作业指标
        return {
            "timestamp": int(time.time()),
            "active_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "average_job_duration": 0
        }
    
    def check_thresholds(self, metrics):
        """检查阈值并触发告警"""
        alerts = []
        
        # 检查CPU使用率
        if metrics.get("cpu_percent", 0) > 90:
            alerts.append({
                "type": "cpu_high",
                "message": f"CPU使用率过高: {metrics.get('cpu_percent', 0)}%",
                "severity": "warning"
            })
        
        # 检查内存使用率
        if metrics.get("memory_percent", 0) > 90:
            alerts.append({
                "type": "memory_high",
                "message": f"内存使用率过高: {metrics.get('memory_percent', 0)}%",
                "severity": "warning"
            })
        
        # 检查磁盘使用率
        if metrics.get("disk_percent", 0) > 90:
            alerts.append({
                "type": "disk_high",
                "message": f"磁盘使用率过高: {metrics.get('disk_percent', 0)}%",
                "severity": "critical"
            })
        
        return alerts
    
    def send_alerts(self, alerts):
        """发送告警"""
        for alert in alerts:
            self.logger.warning(f"告警: {alert['message']}")
            # 在实际实现中，可以发送邮件、短信或调用其他通知系统
            # send_email(alert['message'])
            # send_sms(alert['message'])
    
    def start_monitoring(self, interval=60, max_duration=3600):
        """启动监控"""
        self.logger.info("启动监控，间隔: {}秒，最大持续时间: {}秒".format(interval, max_duration))
        
        start_time = time.time()
        while time.time() - start_time < max_duration:
            # 收集指标
            system_metrics = self.collect_system_metrics()
            spark_metrics = self.collect_spark_metrics()
            job_metrics = self.collect_job_metrics()
            
            # 合并指标
            all_metrics = {**system_metrics, **spark_metrics, **job_metrics}
            
            # 保存指标
            self.metrics[all_metrics["timestamp"]] = all_metrics
            
            # 检查阈值
            alerts = self.check_thresholds(system_metrics)
            
            # 发送告警
            if alerts:
                self.send_alerts(alerts)
            
            # 等待下一次收集
            time.sleep(interval)
        
        self.logger.info("监控结束")
        
        return self.metrics
    
    def generate_report(self):
        """生成监控报告"""
        if not self.metrics:
            return "没有可用的监控数据"
        
        # 计算平均指标
        cpu_values = [m.get("cpu_percent", 0) for m in self.metrics.values()]
        memory_values = [m.get("memory_percent", 0) for m in self.metrics.values()]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
        
        # 生成报告
        report = {
            "monitoring_duration": time.time() - self.start_time,
            "metrics_collected": len(self.metrics),
            "avg_cpu_percent": avg_cpu,
            "avg_memory_percent": avg_memory,
            "max_cpu_percent": max(cpu_values) if cpu_values else 0,
            "max_memory_percent": max(memory_values) if memory_values else 0
        }
        
        return json.dumps(report, indent=2)

def monitoring_example():
    """监控示例"""
    
    # 创建SparkSession
    spark = SparkSession.builder.appName("ProductionMonitoring").getOrCreate()
    
    # 创建监控实例
    monitoring = SparkMonitoring(spark_context=spark.sparkContext, spark_session=spark)
    
    # 启动监控（在实际生产环境中，这通常在一个单独的线程中运行）
    print("启动监控示例...")
    
    # 短时间监控演示（实际生产环境中通常监控更长时间）
    metrics = monitoring.start_monitoring(interval=5, max_duration=30)
    
    # 生成报告
    report = monitoring.generate_report()
    print("\n监控报告:")
    print(report)
    
    spark.stop()
    print("监控示例结束")

if __name__ == "__main__":
    monitoring_example()
```

## 8.8 小结

本章详细介绍了Spark性能调优和生产实践，包括内存管理、并行度与分区优化、数据倾斜处理、查询优化、作业监控与故障排查，以及生产环境最佳实践。通过合理的配置和优化，可以显著提高Spark应用程序的性能和稳定性。在生产环境中，还需要考虑安全性、可靠性和可扩展性等方面，以确保Spark应用程序能够稳定、高效地运行。

## 实验与练习

1. 实现一个性能分析工具，用于监控Spark作业的执行情况
2. 优化一个存在数据倾斜的Spark应用程序
3. 配置并测试Spark自适应查询执行功能
4. 实现一个简单的错误处理和重试机制
5. 设计并实现一个生产环境Spark应用程序的监控和告警系统

## 参考资源

- [Spark性能调优指南](https://spark.apache.org/docs/latest/tuning.html)
- [Spark配置指南](https://spark.apache.org/docs/latest/configuration.html)