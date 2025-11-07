# 4. Spark Core编程基础

## 4.1 RDD概述

RDD(Resilient Distributed Dataset，弹性分布式数据集)是Spark的基础数据结构，是一个不可变的、分区的记录集合。理解RDD是掌握Spark编程的关键。

### 4.1.1 RDD特性

#### 1. 不可变性(Immutability)

一旦创建，RDD不能被修改。任何转换操作都会生成新的RDD。

```python
# code/core-examples/rdd_immutability.py
from pyspark import SparkContext

def rdd_immutability_example():
    sc = SparkContext("local[*]", "ImmutabilityExample")
    
    # 创建原始RDD
    data = [1, 2, 3, 4, 5]
    original_rdd = sc.parallelize(data)
    print(f"原始RDD: {original_rdd.collect()}")
    
    # 执行转换操作（不会修改原始RDD）
    doubled_rdd = original_rdd.map(lambda x: x * 2)
    print(f"加倍RDD: {doubled_rdd.collect()}")
    
    # 原始RDD保持不变
    print(f"原始RDD（转换后）: {original_rdd.collect()}")
    
    sc.stop()

if __name__ == "__main__":
    rdd_immutability_example()
```

#### 2. 分区(Partitioning)

RDD数据被分成多个分区，每个分区在不同节点上并行处理。

```python
# code/core-examples/rdd_partitioning.py
from pyspark import SparkContext

def rdd_partitioning_example():
    sc = SparkContext("local[*]", "PartitioningExample")
    
    # 创建带分区的RDD
    data = range(1, 21)  # 1到20的数字
    rdd = sc.parallelize(data, numSlices=4)  # 分成4个分区
    
    print(f"总元素数量: {rdd.count()}")
    print(f"分区数量: {rdd.getNumPartitions()}")
    
    # 查看每个分区的内容
    def partition_info(index, iterator):
        partition_data = list(iterator)
        return [f"分区 {index}: {len(partition_data)} 个元素: {partition_data}"]
    
    partition_contents = rdd.mapPartitionsWithIndex(partition_info).collect()
    for content in partition_contents:
        print(content)
    
    sc.stop()

if __name__ == "__main__":
    rdd_partitioning_example()
```

#### 3. 依赖关系(Lineage/DAG)

RDD记录其创建过程，形成有向无环图(DAG)，用于容错恢复。

```python
# code/core-examples/rdd_lineage.py
from pyspark import SparkContext

def rdd_lineage_example():
    sc = SparkContext("local[*]", "LineageExample")
    
    # 创建RDD转换链
    base_rdd = sc.parallelize(range(1, 11), 3)
    print(f"基础RDD血缘: {base_rdd.toDebugString()}")
    
    # 转换操作1: 过滤偶数
    even_rdd = base_rdd.filter(lambda x: x % 2 == 0)
    print(f"过滤RDD血缘: {even_rdd.toDebugString()}")
    
    # 转换操作2: 平方
    squared_rdd = even_rdd.map(lambda x: x * x)
    print(f"平方RDD血缘: {squared_rdd.toDebugString()}")
    
    # 转换操作3: 求和
    result = squared_rdd.sum()
    print(f"最终结果: {result}")
    
    sc.stop()

if __name__ == "__main__":
    rdd_lineage_example()
```

## 4.2 RDD创建方式

### 4.2.1 从内存中集合创建

```python
# code/core-examples/create_rdd_from_collection.py
from pyspark import SparkContext

def create_rdd_from_collection():
    sc = SparkContext("local[*]", "CollectionRDD")
    
    # 方式1: 使用parallelize
    data1 = [1, 2, 3, 4, 5]
    rdd1 = sc.parallelize(data1)
    print("从列表创建RDD:", rdd1.collect())
    
    # 方式2: 使用makeRDD（提供更多选项）
    data2 = ["apple", "banana", "orange"]
    rdd2 = sc.makeRDD(data2)
    print("makeRDD创建:", rdd2.collect())
    
    # 指定分区数
    rdd3 = sc.parallelize(range(1, 100), 5)  # 5个分区
    print(f"指定分区数: {rdd3.getNumPartitions()}")
    
    # 带优先级的RDD
    pref_list = [("a", 1), ("b", 2), ("c", 3)]
    rdd4 = sc.parallelize(pref_list)
    print("键值对RDD:", rdd4.collect())
    
    sc.stop()

if __name__ == "__main__":
    create_rdd_from_collection()
```

### 4.2.2 从外部存储创建

```python
# code/core-examples/create_rdd_from_external.py
from pyspark import SparkContext

def create_rdd_from_external():
    sc = SparkContext("local[*]", "ExternalRDD")
    
    # 从文本文件创建RDD
    # text_rdd = sc.textFile("hdfs://path/to/file.txt")
    # print("文本文件内容:", text_rdd.take(5))
    
    # 创建模拟文本文件
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/sample.txt", "w") as f:
        f.write("Hello Spark\n")
        f.write("RDD from file\n")
        f.write("External storage\n")
    
    # 从本地文件创建
    local_text_rdd = sc.textFile("data/sample.txt")
    print("本地文件内容:", local_text_rdd.collect())
    
    # 读取整个文件作为单个记录
    whole_file_rdd = sc.wholeTextFiles("data/")
    print("整个文件:", whole_file_rdd.collect())
    
    # 从CSV文件创建RDD（假设有CSV文件）
    os.makedirs("data/csv", exist_ok=True)
    with open("data/csv/sample.csv", "w") as f:
        f.write("name,age,city\n")
        f.write("Alice,30,New York\n")
        f.write("Bob,25,Los Angeles\n")
        f.write("Charlie,35,Chicago\n")
    
    csv_rdd = sc.textFile("data/csv/sample.csv")
    header = csv_rdd.first()
    data_rdd = csv_rdd.filter(lambda line: line != header)
    
    print("CSV文件内容（不含标题）:")
    for line in data_rdd.collect():
        print(line)
    
    sc.stop()

if __name__ == "__main__":
    create_rdd_from_external()
```

### 4.2.3 从其他RDD转换

```python
# code/core-examples/create_rdd_from_transformation.py
from pyspark import SparkContext

def create_rdd_from_transformation():
    sc = SparkContext("local[*]", "TransformationRDD")
    
    # 基础RDD
    base_rdd = sc.parallelize(range(1, 11))
    
    # 通过map转换
    squared_rdd = base_rdd.map(lambda x: x * x)
    print("平方RDD:", squared_rdd.collect())
    
    # 通过filter转换
    even_rdd = base_rdd.filter(lambda x: x % 2 == 0)
    print("偶数RDD:", even_rdd.collect())
    
    # 通过flatMap转换
    flat_rdd = sc.parallelize(["Hello World", "Spark is Great"])
    words_rdd = flat_rdd.flatMap(lambda line: line.split(" "))
    print("单词RDD:", words_rdd.collect())
    
    # 通过union转换
    union_rdd = even_rdd.union(squared_rdd)
    print("合并RDD:", union_rdd.collect())
    
    # 通过intersection转换
    intersection_rdd = even_rdd.intersection(squared_rdd)
    print("交集RDD:", intersection_rdd.collect())
    
    sc.stop()

if __name__ == "__main__":
    create_rdd_from_transformation()
```

## 4.3 RDD转换操作

转换操作是懒执行操作，不会立即计算结果，而是构建执行计划。

### 4.3.1 基本转换操作

#### 1. map操作

对RDD中的每个元素应用函数，生成新的RDD。

```python
# code/core-examples/map_operations.py
from pyspark import SparkContext

def map_operations():
    sc = SparkContext("local[*]", "MapOperations")
    
    # 基础map操作
    numbers_rdd = sc.parallelize([1, 2, 3, 4, 5])
    squared = numbers_rdd.map(lambda x: x * x)
    print("平方操作:", squared.collect())
    
    # 字符串map操作
    words_rdd = sc.parallelize(["spark", "hadoop", "hive"])
    upper_words = words_rdd.map(lambda word: word.upper())
    print("转大写:", upper_words.collect())
    
    # 复杂map操作
    data_rdd = sc.parallelize([
        ("Alice", 30, "Engineer"),
        ("Bob", 25, "Designer"),
        ("Charlie", 35, "Manager")
    ])
    
    # 提取姓名和职业
    name_job_rdd = data_rdd.map(lambda x: (x[0], x[2]))
    print("姓名和职业:", name_job_rdd.collect())
    
    # 使用普通函数
    def complex_transform(person):
        name, age, job = person
        if age < 30:
            return (name, f"Young {job}")
        else:
            return (name, f"Experienced {job}")
    
    transformed_rdd = data_rdd.map(complex_transform)
    print("复杂转换:", transformed_rdd.collect())
    
    sc.stop()

if __name__ == "__main__":
    map_operations()
```

#### 2. filter操作

选择满足条件的元素，生成新的RDD。

```python
# code/core-examples/filter_operations.py
from pyspark import SparkContext

def filter_operations():
    sc = SparkContext("local[*]", "FilterOperations")
    
    # 数字过滤
    numbers_rdd = sc.parallelize(range(1, 21))
    evens = numbers_rdd.filter(lambda x: x % 2 == 0)
    print("偶数:", evens.collect())
    
    # 复杂条件过滤
    range_filtered = numbers_rdd.filter(lambda x: 5 <= x <= 15 and x % 3 == 0)
    print("5到15之间且能被3整除:", range_filtered.collect())
    
    # 字符串过滤
    words_rdd = sc.parallelize(["apple", "banana", "orange", "grape", "watermelon"])
    long_words = words_rdd.filter(lambda word: len(word) > 5)
    print("长度大于5的单词:", long_words.collect())
    
    # 对象过滤
    people_rdd = sc.parallelize([
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ])
    
    ny_people = people_rdd.filter(lambda person: person["city"] == "New York")
    print("纽约居民:", ny_people.collect())
    
    # 组合过滤条件
    senior_ny = people_rdd.filter(lambda p: p["city"] == "New York" and p["age"] > 25)
    print("纽约年长居民:", senior_ny.collect())
    
    sc.stop()

if __name__ == "__main__":
    filter_operations()
```

#### 3. flatMap操作

类似于map，但每个输入元素可以映射到0个或多个输出元素。

```python
# code/core-examples/flatmap_operations.py
from pyspark import SparkContext

def flatmap_operations():
    sc = SparkContext("local[*]", "FlatMapOperations")
    
    # 基础flatMap - 分割单词
    sentences_rdd = sc.parallelize(["Hello world", "Spark is great", "Big data processing"])
    words_rdd = sentences_rdd.flatMap(lambda sentence: sentence.split(" "))
    print("单词列表:", words_rdd.collect())
    
    # 每个元素生成多个输出
    numbers_rdd = sc.parallelize([1, 2, 3])
    expanded_rdd = numbers_rdd.flatMap(lambda x: [x, x*x, x*x*x])
    print("展开列表:", expanded_rdd.collect())
    
    # 过滤掉空值
    optional_rdd = sc.parallelize(["apple", "", "orange", "grape", ""])
    non_empty_rdd = optional_rdd.flatMap(lambda x: [x] if x else [])
    print("非空字符串:", non_empty_rdd.collect())
    
    # 复杂示例：解析句子中的单词和长度
    def sentence_info(sentence):
        words = sentence.split(" ")
        return [(word, len(word)) for word in words]
    
    sentence_rdd = sc.parallelize(["Spark programming", "Data processing"])
    word_lengths_rdd = sentence_rdd.flatMap(sentence_info)
    print("单词和长度:", word_lengths_rdd.collect())
    
    sc.stop()

if __name__ == "__main__":
    flatmap_operations()
```

### 4.3.2 集合操作

#### 1. union操作

合并两个RDD，生成包含所有元素的新RDD。

```python
# code/core-examples/union_operations.py
from pyspark import SparkContext

def union_operations():
    sc = SparkContext("local[*]", "UnionOperations")
    
    # 基础union
    rdd1 = sc.parallelize([1, 2, 3, 4])
    rdd2 = sc.parallelize([3, 4, 5, 6])
    union_rdd = rdd1.union(rdd2)
    print("Union结果（有重复）:", union_rdd.collect())
    
    # union与去重
    distinct_rdd = union_rdd.distinct()
    print("Union后去重:", distinct_rdd.collect())
    
    # 多个RDD的union
    rdd3 = sc.parallelize([7, 8])
    multi_union = rdd1.union(rdd2).union(rdd3)
    print("多个RDD Union:", multi_union.collect())
    
    # 字符串union
    words1 = sc.parallelize(["spark", "hadoop"])
    words2 = sc.parallelize(["hive", "spark"])
    words_union = words1.union(words2)
    print("字符串Union:", words_union.collect())
    
    sc.stop()

if __name__ == "__main__":
    union_operations()
```

#### 2. intersection操作

返回两个RDD的共同元素。

```python
# code/core-examples/intersection_operations.py
from pyspark import SparkContext

def intersection_operations():
    sc = SparkContext("local[*]", "IntersectionOperations")
    
    # 基础intersection
    rdd1 = sc.parallelize([1, 2, 3, 4, 5])
    rdd2 = sc.parallelize([3, 4, 5, 6, 7])
    intersection_rdd = rdd1.intersection(rdd2)
    print("交集结果:", intersection_rdd.collect())
    
    # 字符串intersection
    words1 = sc.parallelize(["spark", "hadoop", "hive", "flink"])
    words2 = sc.parallelize(["spark", "flink", "storm", "kafka"])
    common_words = words1.intersection(words2)
    print("共同单词:", common_words.collect())
    
    # 复杂对象intersection
    people1 = sc.parallelize([("Alice", 30), ("Bob", 25), ("Charlie", 35)])
    people2 = sc.parallelize([("Bob", 25), ("Charlie", 35), ("David", 40)])
    common_people = people1.intersection(people2)
    print("共同人员:", common_people.collect())
    
    sc.stop()

if __name__ == "__main__":
    intersection_operations()
```

### 4.3.3 排序操作

#### 1. sortBy操作

根据指定函数对RDD元素进行排序。

```python
# code/core-examples/sort_operations.py
from pyspark import SparkContext

def sort_operations():
    sc = SparkContext("local[*]", "SortOperations")
    
    # 数字排序
    numbers_rdd = sc.parallelize([5, 2, 8, 1, 9, 3])
    sorted_numbers = numbers_rdd.sortBy(lambda x: x)  # 升序
    print("升序排列:", sorted_numbers.collect())
    
    # 降序排列
    descending_numbers = numbers_rdd.sortBy(lambda x: x, ascending=False)
    print("降序排列:", descending_numbers.collect())
    
    # 字符串排序
    words_rdd = sc.parallelize(["apple", "Orange", "banana", "Grape"])
    sorted_words = words_rdd.sortBy(lambda word: word.lower())
    print("字符串排序（不区分大小写）:", sorted_words.collect())
    
    # 复杂对象排序
    people_rdd = sc.parallelize([
        ("Alice", 30, "New York"),
        ("Bob", 25, "Los Angeles"),
        ("Charlie", 35, "Chicago")
    ])
    
    # 按年龄排序
    age_sorted = people_rdd.sortBy(lambda person: person[1])
    print("按年龄排序:", age_sorted.collect())
    
    # 按城市排序
    city_sorted = people_rdd.sortBy(lambda person: person[2])
    print("按城市排序:", city_sorted.collect())
    
    sc.stop()

if __name__ == "__main__":
    sort_operations()
```

### 4.3.4 分区操作

#### 1. mapPartitions操作

对每个分区应用函数，提高处理效率。

```python
# code/core-examples/partition_operations.py
from pyspark import SparkContext

def partition_operations():
    sc = SparkContext("local[*]", "PartitionOperations")
    
    # 创建带分区的RDD
    data = range(1, 101)
    rdd = sc.parallelize(data, numSlices=5)
    print(f"分区数量: {rdd.getNumPartitions()}")
    
    # mapPartitions示例：计算每个分区的平均值
    def partition_avg(iterator):
        values = list(iterator)
        if values:
            return [sum(values) / len(values)]
        else:
            return [0.0]
    
    avg_per_partition = rdd.mapPartitions(partition_avg)
    print("每个分区的平均值:", avg_per_partition.collect())
    
    # mapPartitionsWithIndex示例：带索引的分区处理
    def partition_with_index(index, iterator):
        values = list(iterator)
        return [(index, len(values), sum(values))]
    
    partition_stats = rdd.mapPartitionsWithIndex(partition_with_index)
    print("每个分区的统计（索引，元素数量，总和）:", partition_stats.collect())
    
    # 与map的效率对比
    def square(x):
        print(f"处理单个元素: {x}")
        return x * x
    
    def partition_square(iterator):
        print(f"处理分区")
        for item in iterator:
            yield item * item
    
    # map操作：每个元素调用一次函数
    map_result = rdd.map(square).take(5)
    
    # mapPartitions操作：每个分区调用一次函数
    partition_result = rdd.mapPartitions(partition_square).take(5)
    
    sc.stop()

if __name__ == "__main__":
    partition_operations()
```

## 4.4 RDD行动操作

行动操作触发实际计算，并返回结果给驱动程序。

### 4.4.1 基本行动操作

#### 1. collect操作

将RDD所有元素收集到驱动程序。

```python
# code/core-examples/collect_operations.py
from pyspark import SparkContext

def collect_operations():
    sc = SparkContext("local[*]", "CollectOperations")
    
    # 基础collect
    numbers_rdd = sc.parallelize([1, 2, 3, 4, 5])
    all_numbers = numbers_rdd.collect()
    print("所有元素:", all_numbers)
    
    # 注意：对于大型RDD，collect可能导致内存问题
    # 可以使用take获取部分元素
    first_three = numbers_rdd.take(3)
    print("前3个元素:", first_three)
    
    # takeSample随机采样
    sample = numbers_rdd.takeSample(False, 3, seed=42)  # False表示不放回
    print("随机采样3个元素:", sample)
    
    # takeOrdered按顺序获取元素
    top_three = numbers_rdd.takeOrdered(3)
    print("最小的3个元素:", top_three)
    
    # largest three
    largest_three = numbers_rdd.top(3)
    print("最大的3个元素:", largest_three)
    
    # first获取第一个元素
    first_element = numbers_rdd.first()
    print("第一个元素:", first_element)
    
    sc.stop()

if __name__ == "__main__":
    collect_operations()
```

#### 2. reduce操作

使用指定函数聚合RDD中的元素。

```python
# code/core-examples/reduce_operations.py
from pyspark import SparkContext

def reduce_operations():
    sc = SparkContext("local[*]", "ReduceOperations")
    
    # 数字求和
    numbers_rdd = sc.parallelize([1, 2, 3, 4, 5])
    total = numbers_rdd.reduce(lambda a, b: a + b)
    print("求和:", total)
    
    # 查找最大值
    max_value = numbers_rdd.reduce(lambda a, b: a if a > b else b)
    print("最大值:", max_value)
    
    # 查找最小值
    min_value = numbers_rdd.reduce(lambda a, b: a if a < b else b)
    print("最小值:", min_value)
    
    # 字符串连接
    words_rdd = sc.parallelize(["Hello", " ", "Spark", " ", "World"])
    concatenated = words_rdd.reduce(lambda a, b: a + b)
    print("字符串连接:", concatenated)
    
    # 复杂聚合操作：统计词频
    text_rdd = sc.parallelize(["hello spark", "spark is great", "hello world"])
    words = text_rdd.flatMap(lambda line: line.split(" "))
    
    # 创建键值对
    word_pairs = words.map(lambda word: (word, 1))
    
    # 按单词聚合
    word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
    print("词频统计:", word_counts.collect())
    
    sc.stop()

if __name__ == "__main__":
    reduce_operations()
```

#### 3. 聚合操作

#### aggregate操作

```python
# code/core-examples/aggregate_operations.py
from pyspark import SparkContext

def aggregate_operations():
    sc = SparkContext("local[*]", "AggregateOperations")
    
    # 基础aggregate示例
    numbers_rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
    
    # 计算平均值
    seq_op = (lambda acc, x: (acc[0] + x, acc[1] + 1))  # 分区内聚合
    comb_op = (lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1]))  # 分区间聚合
    
    sum_count = numbers_rdd.aggregate((0, 0), seq_op, comb_op)
    avg = sum_count[0] / sum_count[1] if sum_count[1] > 0 else 0
    print(f"平均值: {avg} (总和: {sum_count[0]}, 计数: {sum_count[1]})")
    
    # aggregateByKey示例
    grades_rdd = sc.parallelize([
        ("math", 85),
        ("english", 90),
        ("math", 78),
        ("english", 95),
        ("science", 88),
        ("math", 92)
    ])
    
    # 计算每科的平均分
    grade_seq = (lambda acc, x: (acc[0] + x, acc[1] + 1))
    grade_comb = (lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1]))
    
    subject_stats = grades_rdd.aggregateByKey((0, 0), grade_seq, grade_comb)
    subject_avg = subject_stats.mapValues(lambda x: x[0] / x[1])
    print("各科平均分:", subject_avg.collect())
    
    # fold操作（aggregate的简化版本）
    fold_result = numbers_rdd.fold(0, lambda acc, x: acc + x)
    print("fold求和:", fold_result)
    
    sc.stop()

if __name__ == "__main__":
    aggregate_operations()
```

### 4.4.2 统计操作

#### 1. count系列操作

```python
# code/core-examples/count_operations.py
from pyspark import SparkContext

def count_operations():
    sc = SparkContext("local[*]", "CountOperations")
    
    # 基础count
    numbers_rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    total_count = numbers_rdd.count()
    print("总元素数:", total_count)
    
    # countByValue统计每个值的出现次数
    words_rdd = sc.parallelize(["spark", "hadoop", "spark", "hive", "spark", "hadoop"])
    word_counts = words_rdd.countByValue()
    print("词频统计:", dict(word_counts))
    
    # countByKey按键统计
    pairs_rdd = sc.parallelize([("math", 85), ("english", 90), ("math", 78)])
    subject_counts = pairs_rdd.countByKey()
    print("科目统计:", dict(subject_counts))
    
    # isEmpty检查是否为空
    empty_rdd = sc.parallelize([])
    non_empty_rdd = sc.parallelize([1, 2, 3])
    
    print("空RDD是否为空:", empty_rdd.isEmpty())
    print("非空RDD是否为空:", non_empty_rdd.isEmpty())
    
    sc.stop()

if __name__ == "__main__":
    count_operations()
```

#### 2. 统计摘要操作

```python
# code/core-examples/summary_operations.py
from pyspark import SparkContext

def summary_operations():
    sc = SparkContext("local[*]", "SummaryOperations")
    
    # 数字统计
    numbers_rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    min_val = numbers_rdd.min()
    max_val = numbers_rdd.max()
    total = numbers_rdd.sum()
    count = numbers_rdd.count()
    avg = numbers_rdd.mean()
    
    print(f"最小值: {min_val}")
    print(f"最大值: {max_val}")
    print(f"总和: {total}")
    print(f"数量: {count}")
    print(f"平均值: {avg}")
    
    # 使用stats一次性获取所有统计信息
    stats = numbers_rdd.stats()
    print(f"统计摘要: {stats}")
    
    # 方差和标准差
    variance = numbers_rdd.variance()
    stdev = numbers_rdd.stdev()
    
    print(f"方差: {variance}")
    print(f"标准差: {stdev}")
    
    # 带权重的统计
    values_weights_rdd = sc.parallelize([(1, 2.0), (2, 3.0), (3, 4.0), (4, 5.0)])
    
    # 提取值和权重
    values = values_weights_rdd.map(lambda x: x[0])
    weights = values_weights_rdd.map(lambda x: x[1])
    
    # 计算加权平均值
    weighted_sum = values_weights_rdd.map(lambda x: x[0] * x[1]).sum()
    total_weight = weights.sum()
    weighted_avg = weighted_sum / total_weight
    
    print(f"加权平均值: {weighted_avg}")
    
    sc.stop()

if __name__ == "__main__":
    summary_operations()
```

## 4.5 键值对操作

键值对RDD是Spark中的重要数据结构，支持丰富的高级操作。

### 4.5.1 分组操作

#### 1. groupByKey操作

```python
# code/core-examples/groupby_operations.py
from pyspark import SparkContext

def groupby_operations():
    sc = SparkContext("local[*]", "GroupByOperations")
    
    # 基础groupByKey
    pairs_rdd = sc.parallelize([
        ("math", 85),
        ("english", 90),
        ("math", 78),
        ("english", 95),
        ("science", 88),
        ("math", 92)
    ])
    
    grouped_rdd = pairs_rdd.groupByKey()
    print("按科目分组:")
    for subject, scores in grouped_rdd.collect():
        print(f"{subject}: {list(scores)}")
    
    # 计算每科平均分
    avg_scores = grouped_rdd.mapValues(lambda scores: sum(scores) / len(scores))
    print("各科平均分:", avg_scores.collect())
    
    # 复杂分组：按首字母分组
    words_rdd = sc.parallelize(["apple", "ant", "banana", "ball", "cat", "car"])
    first_letter_pairs = words_rdd.map(lambda word: (word[0], word))
    grouped_by_letter = first_letter_pairs.groupByKey()
    
    print("按首字母分组:")
    for letter, words in grouped_by_letter.collect():
        print(f"{letter}: {list(words)}")
    
    sc.stop()

if __name__ == "__main__":
    groupby_operations()
```

#### 2. reduceByKey操作

```python
# code/core-examples/reducebykey_operations.py
from pyspark import SparkContext

def reducebykey_operations():
    sc = SparkContext("local[*]", "ReduceByKeyOperations")
    
    # 基础reduceByKey
    pairs_rdd = sc.parallelize([
        ("math", 85),
        ("english", 90),
        ("math", 78),
        ("english", 95),
        ("science", 88),
        ("math", 92)
    ])
    
    # 计算每科总分
    total_scores = pairs_rdd.reduceByKey(lambda a, b: a + b)
    print("各科总分:", total_scores.collect())
    
    # 计算每科最高分
    max_scores = pairs_rdd.reduceByKey(lambda a, b: a if a > b else b)
    print("各科最高分:", max_scores.collect())
    
    # 计算每科最低分
    min_scores = pairs_rdd.reduceByKey(lambda a, b: a if a < b else b)
    print("各科最低分:", min_scores.collect())
    
    # 计算单词出现次数（词频统计）
    words_rdd = sc.parallelize(["spark", "hadoop", "spark", "hive", "spark", "hadoop"])
    word_pairs = words_rdd.map(lambda word: (word, 1))
    word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
    print("词频统计:", word_counts.collect())
    
    sc.stop()

if __name__ == "__main__":
    reducebykey_operations()
```

### 4.5.2 连接操作

#### 1. join操作

```python
# code/core-examples/join_operations.py
from pyspark import SparkContext

def join_operations():
    sc = SparkContext("local[*]", "JoinOperations")
    
    # 创建两个RDD
    employees = sc.parallelize([
        (1, "Alice", "Engineering"),
        (2, "Bob", "Marketing"),
        (3, "Charlie", "Engineering"),
        (4, "David", "Sales")
    ])
    
    departments = sc.parallelize([
        ("Engineering", "E101"),
        ("Marketing", "M101"),
        ("Sales", "S101"),
        ("HR", "H101")
    ])
    
    # 准备键值对RDD
    emp_dept_pairs = employees.map(lambda x: (x[2], (x[0], x[1])))  # (部门, (ID, 姓名))
    dept_info = departments.map(lambda x: (x[0], x[1]))  # (部门, 部门代码)
    
    # 内连接
    inner_join = emp_dept_pairs.join(dept_info)
    print("内连接结果:")
    for dept, ((emp_id, emp_name), dept_code) in inner_join.collect():
        print(f"部门: {dept}, 员工: {emp_id}-{emp_name}, 部门代码: {dept_code}")
    
    # 左外连接
    left_join = emp_dept_pairs.leftOuterJoin(dept_info)
    print("\n左外连接结果:")
    for dept, ((emp_id, emp_name), dept_code) in left_join.collect():
        code = dept_code if dept_code is not None else "NULL"
        print(f"部门: {dept}, 员工: {emp_id}-{emp_name}, 部门代码: {code}")
    
    # 右外连接
    right_join = emp_dept_pairs.rightOuterJoin(dept_info)
    print("\n右外连接结果:")
    for dept, (emp_info, dept_code) in right_join.collect():
        if emp_info is not None:
            emp_id, emp_name = emp_info
            print(f"部门: {dept}, 员工: {emp_id}-{emp_name}, 部门代码: {dept_code}")
        else:
            print(f"部门: {dept}, 员工: NULL, 部门代码: {dept_code}")
    
    # 全外连接
    full_join = emp_dept_pairs.fullOuterJoin(dept_info)
    print("\n全外连接结果:")
    for dept, (emp_info, dept_code) in full_join.collect():
        emp_desc = "NULL" if emp_info is None else f"{emp_info[0]}-{emp_info[1]}"
        code = "NULL" if dept_code is None else dept_code
        print(f"部门: {dept}, 员工: {emp_desc}, 部门代码: {code}")
    
    sc.stop()

if __name__ == "__main__":
    join_operations()
```

## 4.6 数据分区与缓存

### 4.6.1 数据分区策略

```python
# code/core-examples/partition_strategies.py
from pyspark import SparkContext
from pyspark import Partitioner

class CustomPartitioner(Partitioner):
    def __init__(self, num_partitions):
        self.num_partitions = num_partitions
    
    def getPartition(self, key):
        # 根据键的哈希值决定分区
        return hash(key) % self.num_partitions
    
    def __eq__(self, other):
        return isinstance(other, CustomPartitioner) and self.num_partitions == other.num_partitions

def partition_strategies():
    sc = SparkContext("local[*]", "PartitionStrategies")
    
    # 创建键值对RDD
    pairs = sc.parallelize([
        ("apple", 1), ("banana", 2), ("orange", 3),
        ("apple", 4), ("banana", 5), ("orange", 6),
        ("apple", 7), ("banana", 8), ("orange", 9),
        ("grape", 10), ("grape", 11), ("grape", 12)
    ], 3)
    
    print(f"原始分区数: {pairs.getNumPartitions()}")
    
    # 使用默认分区器进行分区
    partitioned_rdd = pairs.partitionBy(3)
    print(f"默认分区后分区数: {partitioned_rdd.getNumPartitions()}")
    
    # 使用自定义分区器
    custom_partitioned = pairs.partitionBy(3, lambda key: hash(key) % 3)
    print(f"自定义分区后分区数: {custom_partitioned.getNumPartitions()}")
    
    # 查看分区内容
    def partition_contents(index, iterator):
        data = list(iterator)
        return [(index, data)]
    
    print("\n默认分区内容:")
    for idx, contents in partitioned_rdd.mapPartitionsWithIndex(partition_contents).collect():
        print(f"分区 {idx}: {contents}")
    
    print("\n自定义分区内容:")
    for idx, contents in custom_partitioned.mapPartitionsWithIndex(partition_contents).collect():
        print(f"分区 {idx}: {contents}")
    
    # 分区对性能的影响演示
    def simulate_processing():
        import time
        start_time = time.time()
        
        # 在每个分区内进行计算
        def process_partition(iterator):
            items = list(iterator)
            # 模拟处理时间
            import time
            time.sleep(0.1)
            return [len(items)]
        
        # 默认分区处理
        default_result = partitioned_rdd.mapPartitions(process_partition).collect()
        print(f"默认分区处理结果: {default_result}")
        
        # 重新分区处理
        repartitioned = pairs.repartition(6)  # 增加分区数
        rebalanced_result = repartitioned.mapPartitions(process_partition).collect()
        print(f"重分区处理结果: {rebalanced_result}")
        
        end_time = time.time()
        print(f"总处理时间: {end_time - start_time:.2f}秒")
    
    simulate_processing()
    
    sc.stop()

if __name__ == "__main__":
    partition_strategies()
```

### 4.6.2 RDD缓存与持久化

```python
# code/core-examples/rdd_persistence.py
from pyspark import SparkContext
from pyspark.storagelevel import StorageLevel

def rdd_persistence():
    sc = SparkContext("local[*]", "RDDPersistence")
    
    # 创建一个较大的RDD
    large_rdd = sc.parallelize(range(1, 1000001), 10)  # 1百万个数字，10个分区
    
    # 第一次计算 - 不使用缓存
    import time
    start_time = time.time()
    count1 = large_rdd.map(lambda x: x * x).filter(lambda x: x % 100 == 0).count()
    first_time = time.time() - start_time
    print(f"第一次计算（无缓存）耗时: {first_time:.2f}秒，结果: {count1}")
    
    # 第二次计算 - 不使用缓存
    start_time = time.time()
    count2 = large_rdd.map(lambda x: x * x).filter(lambda x: x % 100 == 0).count()
    second_time = time.time() - start_time
    print(f"第二次计算（无缓存）耗时: {second_time:.2f}秒，结果: {count2}")
    
    # 第三次计算 - 使用缓存
    # 先进行转换，然后缓存
    transformed_rdd = large_rdd.map(lambda x: x * x).filter(lambda x: x % 100 == 0)
    transformed_rdd.cache()  # 或者 persist(StorageLevel.MEMORY_ONLY)
    
    # 触发缓存
    start_time = time.time()
    count3 = transformed_rdd.count()
    cache_time = time.time() - start_time
    print(f"缓存计算耗时: {cache_time:.2f}秒，结果: {count3}")
    
    # 第四次计算 - 使用缓存
    start_time = time.time()
    count4 = transformed_rdd.count()
    cached_time = time.time() - start_time
    print(f"使用缓存计算耗时: {cached_time:.2f}秒，结果: {count4}")
    
    # 不同存储级别的演示
    print("\n不同存储级别演示:")
    
    # 创建一个较小的RDD用于演示
    demo_rdd = sc.parallelize(range(1, 1001), 5)
    
    # 存储级别1: 仅内存
    mem_rdd = demo_rdd.map(lambda x: x * x)
    mem_rdd.persist(StorageLevel.MEMORY_ONLY)
    mem_count = mem_rdd.count()
    print(f"内存存储级别: 内存使用={mem_rdd.getStorageLevel().useMemory}, 磁盘使用={mem_rdd.getStorageLevel().useDisk}")
    
    # 存储级别2: 内存和磁盘
    mem_disk_rdd = demo_rdd.map(lambda x: x * x + 1)
    mem_disk_rdd.persist(StorageLevel.MEMORY_AND_DISK)
    mem_disk_count = mem_disk_rdd.count()
    print(f"内存+磁盘存储级别: 内存使用={mem_disk_rdd.getStorageLevel().useMemory}, 磁盘使用={mem_disk_rdd.getStorageLevel().useDisk}")
    
    # 存储级别3: 仅磁盘
    disk_rdd = demo_rdd.map(lambda x: x * x + 2)
    disk_rdd.persist(StorageLevel.DISK_ONLY)
    disk_count = disk_rdd.count()
    print(f"仅磁盘存储级别: 内存使用={disk_rdd.getStorageLevel().useMemory}, 磁盘使用={disk_rdd.getStorageLevel().useDisk}")
    
    # 清理缓存
    mem_rdd.unpersist()
    mem_disk_rdd.unpersist()
    disk_rdd.unpersist()
    transformed_rdd.unpersist()
    
    # 检查缓存状态
    print(f"清理后的缓存状态: {transformed_rdd.getStorageLevel()}")
    
    sc.stop()

if __name__ == "__main__":
    rdd_persistence()
```

## 4.7 共享变量

### 4.7.1 广播变量

```python
# code/core-examples/broadcast_variables.py
from pyspark import SparkContext

def broadcast_variables():
    sc = SparkContext("local[*]", "BroadcastVariables")
    
    # 创建一个较大的数据集作为广播变量
    lookup_data = {
        "A": "Apple",
        "B": "Banana",
        "C": "Cherry",
        "D": "Date",
        "E": "Elderberry"
    }
    
    # 将数据广播到所有节点
    broadcast_lookup = sc.broadcast(lookup_data)
    
    # 创建主数据集
    main_data = ["A", "C", "E", "B", "D", "A", "C"]
    main_rdd = sc.parallelize(main_data, 3)
    
    # 使用广播变量进行查找
    def lookup_key(key):
        lookup_map = broadcast_lookup.value
        return lookup_map.get(key, "Unknown")
    
    result_rdd = main_rdd.map(lookup_key)
    print("使用广播变量的结果:", result_rdd.collect())
    
    # 对比不使用广播变量的情况
    print("\n不使用广播变量（假设lookup_data在每个节点上都需要传输）:")
    
    # 模拟不使用广播变量的情况
    def lookup_without_broadcast(key):
        # 在每次函数调用中都需要访问lookup_data
        # 这在分布式环境中会导致lookup_data被多次传输
        return lookup_data.get(key, "Unknown")
    
    result_without_broadcast = main_rdd.map(lookup_without_broadcast)
    print("不使用广播变量的结果:", result_without_broadcast.collect())
    
    # 更新广播变量
    updated_lookup = {
        "A": "Apricot",
        "B": "Blueberry",
        "C": "Coconut",
        "D": "Dragonfruit",
        "E": "Eggplant"
    }
    
    # 广播更新后的变量
    broadcast_updated = sc.broadcast(updated_lookup)
    
    def lookup_updated(key):
        lookup_map = broadcast_updated.value
        return lookup_map.get(key, "Unknown")
    
    result_updated = main_rdd.map(lookup_updated)
    print("\n使用更新后广播变量的结果:", result_updated.collect())
    
    # 清理广播变量
    broadcast_lookup.unpersist()
    broadcast_updated.unpersist()
    
    sc.stop()

if __name__ == "__main__":
    broadcast_variables()
```

### 4.7.2 累加器

```python
# code/core-examples/accumulators.py
from pyspark import SparkContext
from pyspark.accumulator import AccumulatorParam

class VectorAccumulatorParam(AccumulatorParam):
    def zero(self, value):
        return [0.0, 0.0, 0.0]
    
    def addInPlace(self, val1, val2):
        return [val1[i] + val2[i] for i in range(len(val1))]

def accumulators():
    sc = SparkContext("local[*]", "Accumulators")
    
    # 基础累加器 - 计数器
    counter = sc.accumulator(0)
    
    numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
    
    def count_even(x):
        if x % 2 == 0:
            counter.add(1)
        return x * x
    
    squared_numbers = numbers.map(count_even)
    result = squared_numbers.collect()
    
    print("平方数:", result)
    print("偶数个数:", counter.value)
    
    # 累加器作为统计工具
    sum_acc = sc.accumulator(0)
    max_acc = sc.accumulator(float('-inf'))
    min_acc = sc.accumulator(float('inf'))
    
    def calculate_stats(x):
        sum_acc.add(x)
        if x > max_acc.value:
            max_acc.add(x - max_acc.value)
        if x < min_acc.value:
            min_acc.add(x - min_acc.value)
        return x
    
    numbers.map(calculate_stats).count()  # 触发计算
    count = numbers.count()
    
    print(f"统计结果: 总和={sum_acc.value}, 最大值={max_acc.value}, 最小值={min_acc.value}, 个数={count}")
    print(f"平均值={sum_acc.value / count if count > 0 else 0}")
    
    # 自定义累加器
    vector_acc = sc.accumulator([0.0, 0.0, 0.0], VectorAccumulatorParam())
    
    data_points = sc.parallelize([
        (1.0, 2.0, 3.0),
        (4.0, 5.0, 6.0),
        (7.0, 8.0, 9.0)
    ])
    
    def sum_vectors(point):
        x, y, z = point
        vector_acc.add([x, y, z])
        return point
    
    data_points.map(sum_vectors).count()  # 触发计算
    
    print(f"向量总和: {vector_acc.value}")
    
    # 注意：在转换操作中使用累加器需要谨慎，因为可能被多次执行
    print("\n累加器执行次数警告:")
    warning_counter = sc.accumulator(0)
    
    def sometimes_executed(x):
        warning_counter.add(1)
        return x
    
    # 如果RDD被多次使用（如cache未命中），累加器可能被多次执行
    rdd = sc.parallelize([1, 2, 3, 4, 5])
    transformed = rdd.map(sometimes_executed)
    
    # 第一次调用
    result1 = transformed.collect()
    # 第二次调用（可能导致累加器再次执行）
    result2 = transformed.collect()
    
    print(f"第一次结果: {result1}")
    print(f"第二次结果: {result2}")
    print(f"累加器值: {warning_counter.value} (可能 > 实际元素个数)")
    
    sc.stop()

if __name__ == "__main__":
    accumulators()
```

## 4.8 实战案例：WordCount进阶

```python
# code/core-examples/advanced_wordcount.py
from pyspark import SparkContext
import re

def advanced_wordcount():
    sc = SparkContext("local[*]", "AdvancedWordCount")
    
    # 创建示例文本数据
    import os
    os.makedirs("data", exist_ok=True)
    
    sample_text = """
    Apache Spark is a fast and general cluster-computing framework.
    Spark provides interfaces for programming entire clusters with implicit data parallelism and fault tolerance.
    Spark Core is the foundation of the overall project.
    It provides distributed task dispatching, scheduling, and basic I/O functionalities.
    Spark SQL is a component on top of Spark Core that introduces a data abstraction called DataFrames.
    """
    
    with open("data/spark_article.txt", "w") as f:
        f.write(sample_text)
    
    # 基础WordCount
    text_rdd = sc.textFile("data/spark_article.txt")
    words = text_rdd.flatMap(lambda line: line.split(" "))
    word_counts = words.map(lambda word: (word.lower(), 1)).reduceByKey(lambda a, b: a + b)
    
    print("基础WordCount结果（前10个）:")
    word_counts.takeOrdered(10, key=lambda x: -x[1]).forEach(lambda x: print(f"{x[0]}: {x[1]}"))
    
    # 高级WordCount：过滤停用词
    stop_words = set(["a", "an", "the", "is", "are", "and", "or", "in", "on", "at", "to", "of", "with", "for"])
    broadcast_stopwords = sc.broadcast(stop_words)
    
    # 清理文本：移除标点符号
    def clean_word(word):
        # 移除标点符号
        cleaned = re.sub(r'[^\w]', '', word.lower())
        return cleaned
    
    # 过滤停用词和空字符串
    def is_valid_word(word):
        return word and word not in broadcast_stopwords.value and len(word) > 2
    
    # 高级WordCount处理链
    advanced_counts = text_rdd.flatMap(lambda line: line.split(" ")) \
                              .map(clean_word) \
                              .filter(is_valid_word) \
                              .map(lambda word: (word, 1)) \
                              .reduceByKey(lambda a, b: a + b)
    
    print("\n高级WordCount结果（前10个，过滤停用词）:")
    advanced_counts.takeOrdered(10, key=lambda x: -x[1]).forEach(lambda x: print(f"{x[0]}: {x[1]}"))
    
    # 统计指标
    total_words = advanced_counts.map(lambda x: x[1]).sum()
    unique_words = advanced_counts.count()
    
    print(f"\n统计指标:")
    print(f"总词数（过滤后）: {total_words}")
    print(f"唯一词数: {unique_words}")
    
    # 词频分布
    min_count = advanced_counts.map(lambda x: x[1]).min()
    max_count = advanced_counts.map(lambda x: x[1]).max()
    
    print(f"词频范围: {min_count} - {max_count}")
    
    # 按词频分组
    def count_group(count):
        if count == 1:
            return "出现1次"
        elif count <= 3:
            return "出现2-3次"
        elif count <= 5:
            return "出现4-5次"
        else:
            return "出现5次以上"
    
    freq_distribution = advanced_counts.map(lambda x: (count_group(x[1]), 1)) \
                                      .reduceByKey(lambda a, b: a + b)
    
    print("\n词频分布:")
    for group, count in freq_distribution.collect():
        print(f"{group}: {count}个词")
    
    sc.stop()

if __name__ == "__main__":
    advanced_wordcount()
```

## 4.9 小结

本章详细介绍了Spark Core编程的基础知识，包括RDD的创建、转换操作、行动操作、键值对操作、数据分区、缓存和共享变量。掌握这些核心概念和操作是使用Spark进行大数据处理的基础。在下一章中，我们将学习Spark SQL，了解如何使用结构化数据处理API。

## 实验与练习

1. 实现一个简单的日志分析系统，使用RDD API统计访问频率最高的页面
2. 实现推荐系统的协同过滤算法，使用键值对操作
3. 实现PageRank算法，理解迭代计算和RDD持久化的重要性
4. 比较不同分区策略对join操作性能的影响
5. 实现一个简单的倒排索引，使用广播变量优化性能

## 参考资源

- [Spark RDD编程指南](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Spark API文档](https://spark.apache.org/docs/latest/api/python/index.html)