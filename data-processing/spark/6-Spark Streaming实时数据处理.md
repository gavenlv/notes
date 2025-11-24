# 6. Spark Streaming实时数据处理

## 6.1 Spark Streaming概述

Spark Streaming是Spark生态系统中的实时计算组件，它提供了可扩展、高吞吐、容错的实时数据流处理能力。Spark Streaming将实时数据流以微批次的方式进行处理，每个批次是一个小的RDD，然后使用Spark引擎进行处理。

### 6.1.1 Spark Streaming架构

Spark Streaming的架构基于微批次处理模型：

```
实时数据流 → 接收器(Receiver) → 数据块(Block) → 微批次(Micro-batch) → RDD处理 → 结果输出
```

**代码示例：理解Spark Streaming微批次处理**

```python
# code/streaming-examples/microbatch_demo.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time

def microbatch_demo():
    # 创建SparkContext，设置批处理间隔为2秒
    sc = SparkContext("local[*]", "MicrobatchDemo")
    ssc = StreamingContext(sc, 2)  # 批处理间隔2秒
    
    # 创建一个队列RDD流
    rdd_queue = []
    for i in range(5):
        rdd = sc.parallelize([f"Batch {i}: Line 1", f"Batch {i}: Line 2", f"Batch {i}: Line 3"])
        rdd_queue.append(rdd)
    
    # 创建队列流
    queue_stream = ssc.queueStream(rdd_queue)
    
    # 处理每个批次
    processed_stream = queue_stream.map(lambda x: (x.split(":")[0], len(x)))
    
    # 打印每个批次的处理结果
    def process_batch(rdd):
        if not rdd.isEmpty():
            print(f"--- 处理批次 ---")
            for item in rdd.collect():
                print(f"{item[0]}: {item[1]} 字符")
    
    processed_stream.foreachRDD(process_batch)
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间处理所有批次
    time.sleep(12)  # 5个批次，每个2秒，加上一些额外时间
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("微批次处理演示完成")

if __name__ == "__main__":
    microbatch_demo()
```

## 6.2 DStream基础操作

DStream(Discretized Stream，离散化流)是Spark Streaming的基本抽象，表示连续的数据流。DStream可以通过输入源创建，也可以通过其他DStream转换得到。

### 6.2.1 无状态转换操作

无状态转换操作不依赖之前批次的数据，每个批次的处理都是独立的。

```python
# code/streaming-examples/stateless_operations.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random

def stateless_operations():
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "StatelessOperations")
    ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
    
    # 创建模拟数据流
    words_data = ["spark", "hadoop", "hive", "spark", "flink", "kafka", "spark", "hadoop"]
    
    def generate_rdds():
        for i in range(5):
            # 随机选择一些单词
            sample = random.sample(words_data, min(5, len(words_data)))
            yield sc.parallelize(sample)
    
    rdd_queue = list(generate_rdds())
    queue_stream = ssc.queueStream(rdd_queue)
    
    # 转换操作1: map操作
    upper_stream = queue_stream.map(lambda word: word.upper())
    
    # 转换操作2: filter操作
    spark_stream = queue_stream.filter(lambda word: word == "spark")
    
    # 转换操作3: flatMap操作
    sentence_stream = queue_stream.map(lambda word: f"{word} is great")
    words_from_sentences = sentence_stream.flatMap(lambda sentence: sentence.split(" "))
    
    # 转换操作4: union操作
    additional_words = ssc.queueStream([sc.parallelize(["data", "analytics", "big"])])
    combined_stream = queue_stream.union(additional_words)
    
    # 转换操作5: reduceByKey操作（需要先转换为键值对）
    word_pairs = queue_stream.map(lambda word: (word, 1))
    word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
    
    # 输出结果
    print("=== map操作结果 ===")
    upper_stream.pprint()
    
    print("=== filter操作结果 ===")
    spark_stream.pprint()
    
    print("=== flatMap操作结果 ===")
    words_from_sentences.pprint()
    
    print("=== union操作结果 ===")
    combined_stream.pprint()
    
    print("=== reduceByKey操作结果 ===")
    word_counts.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间处理所有批次
    time.sleep(30)  # 5个批次，每个5秒
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("无状态转换操作演示完成")

if __name__ == "__main__":
    stateless_operations()
```

### 6.2.2 有状态转换操作

有状态转换操作需要跨批次维护状态，如累计统计、滑动窗口计算等。

```python
# code/streaming-examples/stateful_operations.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random

def stateful_operations():
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "StatefulOperations")
    ssc = StreamingContext(sc, 10)  # 10秒的批处理间隔
    
    # 设置检查点目录，用于有状态操作
    ssc.checkpoint("checkpoint")
    
    # 创建模拟数据流
    words_data = ["spark", "hadoop", "hive", "spark", "flink", "kafka", "spark", "hadoop",
                  "data", "analytics", "big", "data", "spark", "hadoop", "data"]
    
    def generate_rdds():
        for i in range(6):
            # 随机选择一些单词
            sample = random.sample(words_data, min(5, len(words_data)))
            yield sc.parallelize(sample)
    
    rdd_queue = list(generate_rdds())
    queue_stream = ssc.queueStream(rdd_queue)
    
    # 有状态操作1: updateStateByKey - 累计统计
    def update_function(new_values, running_sum):
        if running_sum is None:
            running_sum = 0
        return sum(new_values) + running_sum
    
    # 计算累计词频
    word_pairs = queue_stream.map(lambda word: (word, 1))
    total_word_counts = word_pairs.updateStateByKey(update_function)
    
    # 有状态操作2: window操作 - 滑动窗口统计
    # 每个窗口包含20秒的数据，每10秒滑动一次
    windowed_word_counts = word_pairs.reduceByKeyAndWindow(
        lambda a, b: a + b, 
        lambda a, b: a - b, 
        20,  # 窗口持续时间20秒
        10   # 滑动间隔10秒
    )
    
    # 有状态操作3: countByWindow - 窗口内元素计数
    windowed_counts = queue_stream.countByWindow(
        20,  # 窗口持续时间20秒
        10   # 滑动间隔10秒
    )
    
    # 输出结果
    print("=== 累计词频 (updateStateByKey) ===")
    total_word_counts.pprint()
    
    print("=== 滑动窗口词频 (reduceByKeyAndWindow) ===")
    windowed_word_counts.pprint()
    
    print("=== 窗口内元素计数 (countByWindow) ===")
    windowed_counts.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间处理多个窗口
    time.sleep(60)  # 运行60秒，处理多个窗口
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("有状态转换操作演示完成")

if __name__ == "__main__":
    stateful_operations()
```

### 6.2.3 检查点机制

检查点机制是Spark Streaming容错的关键，它定期将DStream的元数据和状态保存到可靠的存储系统（如HDFS）中。

```python
# code/streaming-examples/checkpointing.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random
import os

def checkpointing_example():
    # 设置检查点目录
    checkpoint_dir = "checkpoint"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    def function_to_create_context():
        # 创建SparkContext和StreamingContext
        sc = SparkContext("local[*]", "CheckpointingExample")
        ssc = StreamingContext(sc, 5)  # 5秒批处理间隔
        
        # 设置检查点目录
        ssc.checkpoint(checkpoint_dir)
        print(f"检查点目录设置为: {checkpoint_dir}")
        
        # 创建模拟数据流
        words_data = ["spark", "hadoop", "hive", "spark", "flink", "kafka"]
        
        def generate_rdds():
            for i in range(10):
                sample = random.sample(words_data, min(3, len(words_data)))
                yield sc.parallelize(sample)
        
        rdd_queue = list(generate_rdds())
        queue_stream = ssc.queueStream(rdd_queue)
        
        # 使用updateStateByKey进行累计统计
        def update_function(new_values, running_count):
            if running_count is None:
                running_count = 0
            return sum(new_values) + running_count
        
        word_counts = queue_stream.map(lambda word: (word, 1)).updateStateByKey(update_function)
        word_counts.pprint()
        
        return ssc
    
    # 使用检查点创建或恢复StreamingContext
    ssc = StreamingContext.getOrCreate(checkpoint_dir, function_to_create_context)
    
    # 启动流计算
    ssc.start()
    
    # 运行一段时间
    time.sleep(30)
    
    # 停止流计算
    ssc.stop(stopSparkContext=True, stopGraceFully=True)
    
    print("检查点机制演示完成")

if __name__ == "__main__":
    checkpointing_example()
```

## 6.3 输入源与输出操作

### 6.3.1 基本输入源

```python
# code/streaming-examples/input_sources.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random
import os

def basic_input_sources():
    print("=== Spark Streaming输入源演示 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "InputSources")
    ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
    
    # 输入源1: 队列流
    print("输入源1: 队列流")
    
    rdd_queue = []
    for i in range(3):
        rdd = sc.parallelize([f"Queue Batch {i}: Line 1", f"Queue Batch {i}: Line 2"])
        rdd_queue.append(rdd)
    
    queue_stream = ssc.queueStream(rdd_queue)
    queue_stream.pprint()
    
    # 输入源2: Socket流（需要先运行nc -lk 9999）
    print("输入源2: Socket流（需要先运行: nc -lk 9999）")
    
    # socket_stream = ssc.socketTextStream("localhost", 9999)
    # words = socket_stream.flatMap(lambda line: line.split(" "))
    # word_counts = words.map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
    # word_counts.pprint()
    
    # 输入源3: 文本文件流
    print("输入源3: 文本文件流（监控目录）")
    
    # 创建监控目录
    os.makedirs("streaming_files", exist_ok=True)
    
    # 监控文件目录（实际应用中需要向该目录添加文件）
    # textFileStream会监控目录，处理新添加的文件
    # file_stream = ssc.textFileStream("streaming_files")
    # file_stream.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 模拟向监控目录添加文件
    def create_files():
        for i in range(2):
            time.sleep(7)  # 等待一段时间，让流处理开始
            with open(f"streaming_files/file_{i}.txt", "w") as f:
                f.write(f"File {i}: Line 1\n")
                f.write(f"File {i}: Line 2\n")
    
    try:
        # 启动文件创建线程
        import threading
        file_thread = threading.Thread(target=create_files)
        file_thread.daemon = True
        file_thread.start()
        
        # 运行足够长的时间处理所有批次
        time.sleep(20)
    except Exception as e:
        print(f"处理文件流时出错: {e}")
    finally:
        # 停止流计算
        ssc.stop(stopSparkContext=True)
    
    print("基本输入源演示完成")

if __name__ == "__main__":
    basic_input_sources()
```

### 6.3.2 高级输入源：Kafka

```python
# code/streaming-examples/kafka_source.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import time

def kafka_source_example():
    print("=== Kafka输入源演示 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "KafkaSource")
    ssc = StreamingContext(sc, 10)  # 10秒的批处理间隔
    
    try:
        # Kafka参数
        kafka_params = {
            "bootstrap.servers": "localhost:9092",  # Kafka服务器地址
            "group.id": "spark-streaming-group",    # 消费者组ID
            "auto.offset.reset": "latest"           # 从最新偏移量开始消费
        }
        
        # Kafka主题
        topics = ["test-topic"]
        
        # 创建Kafka流
        # kafka_stream = KafkaUtils.createDirectStream(
        #     ssc, 
        #     topics, 
        #     kafka_params
        # )
        
        # 处理Kafka消息
        # messages = kafka_stream.map(lambda x: x[1])  # 提取消息内容
        # word_counts = messages.flatMap(lambda line: line.split(" ")) \
        #                        .map(lambda word: (word, 1)) \
        #                        .reduceByKey(lambda a, b: a + b)
        # word_counts.pprint()
        
        print("注意: 此示例需要运行Kafka服务器并创建'test-topic'主题")
        print("实际代码已注释，请在Kafka环境准备就绪后取消注释")
        
    except Exception as e:
        print(f"连接Kafka时出错: {e}")
        print("请确保:")
        print("1. Kafka服务器正在运行")
        print("2. 主题'test-topic'已创建")
        print("3. 参数配置正确")
    finally:
        # 停止流计算
        ssc.stop(stopSparkContext=True)
    
    print("Kafka输入源演示完成")

if __name__ == "__main__":
    print("Kafka示例需要有效的Kafka环境")
    print("请确保:")
    print("1. Kafka服务器正在运行")
    print("2. 主题已创建")
    print("3. 参数配置正确")
    kafka_source_example()
```

### 6.3.3 输出操作

```python
# code/streaming-examples/output_operations.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random
import os

def output_operations():
    print("=== Spark Streaming输出操作演示 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "OutputOperations")
    ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
    
    # 创建模拟数据流
    data = [
        [("spark", 1), ("hadoop", 1), ("hive", 1)],
        [("spark", 1), ("hive", 1), ("flink", 1)],
        [("hadoop", 1), ("spark", 1), ("flink", 1), ("kafka", 1)],
        [("spark", 1), ("kafka", 1)],
        [("hadoop", 1), ("hive", 1), ("spark", 1)]
    ]
    
    def generate_rdds():
        for item in data:
            yield sc.parallelize(item)
    
    rdd_queue = list(generate_rdds())
    word_stream = ssc.queueStream(rdd_queue)
    
    # 词频统计
    word_counts = word_stream.reduceByKey(lambda a, b: a + b)
    
    # 输出操作1: 打印到控制台
    print("输出操作1: 打印到控制台")
    word_counts.pprint()
    
    # 输出操作2: 保存到文本文件
    print("输出操作2: 保存到文本文件")
    os.makedirs("streaming_output", exist_ok=True)
    word_counts.saveAsTextFiles("streaming_output/word_counts")
    
    # 输出操作3: foreachRDD - 自定义输出
    print("输出操作3: foreachRDD - 自定义输出")
    
    def save_to_db(rdd):
        """模拟将RDD保存到数据库"""
        if not rdd.isEmpty():
            print(f"--- 将RDD保存到数据库 ---")
            for record in rdd.collect():
                print(f"保存到数据库: {record[0]} -> {record[1]}")
    
    word_counts.foreachRDD(save_to_db)
    
    # 输出操作4: foreachRDD - 更新仪表板
    def update_dashboard(rdd):
        """模拟更新实时仪表板"""
        if not rdd.isEmpty():
            print(f"--- 更新实时仪表板 ---")
            total_words = rdd.map(lambda x: x[1]).sum()
            distinct_words = rdd.count()
            print(f"仪表板更新: 总词数={total_words}, 不同词数={distinct_words}")
    
    word_counts.foreachRDD(update_dashboard)
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间处理所有批次
    time.sleep(30)
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("输出操作演示完成")
    print("检查'streaming_output'目录查看保存的文件")

if __name__ == "__main__":
    output_operations()
```

## 6.4 窗口操作

窗口操作是Spark Streaming中处理有状态数据的重要方式，允许我们在一个滑动窗口内对数据进行聚合计算。

### 6.4.1 滑动窗口基础

```python
# code/streaming-examples/window_operations.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random

def window_operations():
    print("=== 窗口操作演示 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "WindowOperations")
    ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
    
    # 设置检查点目录，用于窗口操作
    ssc.checkpoint("checkpoint")
    
    # 创建模拟数据流
    # 每个批次包含几个数字，用于统计
    def generate_rdds():
        for i in range(10):
            # 生成5-10个随机数
            count = random.randint(5, 10)
            numbers = [random.randint(1, 100) for _ in range(count)]
            yield sc.parallelize(numbers)
    
    rdd_queue = list(generate_rdds())
    number_stream = ssc.queueStream(rdd_queue)
    
    # 窗口操作1: window操作 - 计算窗口内所有元素的和
    # 窗口长度为15秒，滑动间隔为10秒
    windowed_sum = number_stream.reduceByWindow(
        lambda a, b: a + b,
        15,  # 窗口长度15秒
        10   # 滑动间隔10秒
    )
    
    # 窗口操作2: countByWindow - 计算窗口内元素的数量
    windowed_count = number_stream.countByWindow(
        15,  # 窗口长度15秒
        10   # 滑动间隔10秒
    )
    
    # 窗口操作3: reduceByKeyAndWindow - 对键值对进行窗口操作
    # 创建一个键值对流，模拟分类计数
    categories_stream = ssc.queueStream([
        sc.parallelize([("A", 1), ("B", 2), ("A", 3)]),
        sc.parallelize([("B", 4), ("C", 5), ("A", 6)]),
        sc.parallelize([("C", 7), ("A", 8), ("B", 9)]),
        sc.parallelize([("A", 10), ("C", 11), ("B", 12)]),
        sc.parallelize([("B", 13), ("C", 14), ("A", 15)])
    ])
    
    # 计算窗口内每个类别的总和
    windowed_category_sum = categories_stream.reduceByKeyAndWindow(
        lambda a, b: a + b,         # 聚合函数：加法
        lambda a, b: a - b,         # 逆函数：减法（用于窗口滑动时减去离开窗口的元素）
        15,                         # 窗口长度15秒
        10                          # 滑动间隔10秒
    )
    
    # 输出结果
    print("窗口内元素和 (reduceByWindow):")
    windowed_sum.pprint()
    
    print("窗口内元素数量 (countByWindow):")
    windowed_count.pprint()
    
    print("窗口内类别统计 (reduceByKeyAndWindow):")
    windowed_category_sum.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间处理多个窗口
    time.sleep(60)
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("窗口操作演示完成")

if __name__ == "__main__":
    window_operations()
```

### 6.4.2 高级窗口操作

```python
# code/streaming-examples/advanced_window.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random

def advanced_window_operations():
    print("=== 高级窗口操作演示 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "AdvancedWindow")
    ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
    
    # 设置检查点目录
    ssc.checkpoint("checkpoint")
    
    # 创建模拟股票价格数据流
    def generate_stock_data():
        stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"]
        for i in range(12):
            # 每个批次包含几只股票的价格
            batch_data = []
            for stock in random.sample(stocks, 3):
                price = round(random.uniform(100, 200), 2)
                batch_data.append((stock, price))
            yield sc.parallelize(batch_data)
    
    stock_stream = ssc.queueStream(list(generate_stock_data()))
    
    # 高级窗口操作1: 计算滑动窗口内的平均价格
    def add_price_and_count(new_values, old_state):
        """函数用于更新状态：(sum, count)"""
        if old_state is None:
            return (sum(new_values), len(new_values))
        else:
            total, count = old_state
            return (total + sum(new_values), count + len(new_values))
    
    # 使用updateStateByKey计算累计平均价格
    stock_prices = stock_stream.mapValues(lambda price: (price, 1))  # (stock, (price, 1))
    stock_state = stock_prices.updateStateByKey(
        lambda new_values, old_state: add_price_and_count([v[0] for v in new_values], old_state)
    )
    
    # 计算平均价格
    avg_prices = stock_state.mapValues(lambda state: state[0] / state[1] if state[1] > 0 else 0)
    
    # 高级窗口操作2: 计算滑动窗口内的最高价格和最低价格
    def update_price_extremes(new_values, old_extremes):
        """函数用于更新价格极值：(min, max)"""
        if not new_values and old_extremes is None:
            return (float('inf'), float('-inf'))
        
        if old_extremes is None:
            return (min(new_values), max(new_values))
        else:
            old_min, old_max = old_extremes
            new_min = min([old_min] + new_values) if new_values else old_min
            new_max = max([old_max] + new_values) if new_values else old_max
            return (new_min, new_max)
    
    # 计算窗口内的价格极值
    price_extremes = stock_stream.reduceByKeyAndWindow(
        lambda a, b: a,  # 这里只是占位符，实际在updateStateByKey中计算
        lambda a, b: a,  # 这里只是占位符
        20,              # 窗口长度20秒
        10               # 滑动间隔10秒
    )
    
    # 使用updateStateByKey计算价格极值
    prices_only = stock_stream.mapValues(lambda price: [price])
    price_state = prices_only.updateStateByKey(
        lambda new_values, old_state: update_price_extremes(
            [item for sublist in new_values for item in sublist], 
            old_state
        )
    )
    
    # 输出结果
    print("股票累计平均价格:")
    avg_prices.pprint()
    
    print("股票价格极值（窗口20秒，滑动10秒）:")
    price_state.pprint()
    
    # 高级窗口操作3: 模拟异常检测（价格波动过大）
    def detect_anomalies(new_values, history):
        """函数用于检测价格异常波动"""
        if not new_values or not history:
            return new_values, []  # 返回当前价格和空异常列表
        
        current_price = new_values[0]
        historical_prices = history[0] if history else []
        
        # 如果有历史价格，计算平均值
        if historical_prices:
            avg_historical = sum(historical_prices) / len(historical_prices)
            # 如果当前价格与历史平均值差异超过20%，视为异常
            if abs(current_price - avg_historical) / avg_historical > 0.2:
                anomaly = f"异常: 当前价格 {current_price}, 历史平均 {avg_historical:.2f}"
                return [current_price], [anomaly]
        
        # 更新历史价格列表，保持最近5个价格
        updated_history = historical_prices[-4:] + [current_price]
        return [current_price], []
    
    # 检测股票价格异常
    stock_with_history = stock_stream.updateStateByKey(
        lambda new_values, old_state: detect_anomalies(
            new_values, 
            old_state if old_state else ([], [])
        )
    )
    
    # 提取异常信息
    anomalies = stock_with_history.flatMap(lambda x: x[1][1] if x[1][1] else [])
    anomalies.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间
    time.sleep(70)
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("高级窗口操作演示完成")

if __name__ == "__main__":
    advanced_window_operations()
```

## 6.5 容错机制

Spark Streaming的容错机制是其关键特性之一，它通过检查点机制和RDD血缘关系来确保系统在节点故障时能够恢复。

### 6.5.1 驱动程序故障恢复

```python
# code/streaming-examples/driver_fault_tolerance.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random
import os

def driver_fault_tolerance():
    print("=== 驱动程序容错机制演示 ===")
    
    # 设置检查点目录
    checkpoint_dir = "checkpoint_driver"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    def function_to_create_context():
        print("创建新的StreamingContext...")
        
        # 创建SparkContext和StreamingContext
        sc = SparkContext("local[*]", "DriverFaultTolerance")
        ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
        
        # 设置检查点目录
        ssc.checkpoint(checkpoint_dir)
        
        # 创建模拟数据流
        def generate_rdds():
            for i in range(10):
                batch_id = i * 100  # 使用较大的批次ID，便于观察恢复
                numbers = [random.randint(1, 100) for _ in range(5)]
                yield sc.parallelize([(batch_id + j, num) for j, num in enumerate(numbers)])
        
        rdd_queue = list(generate_rdds())
        stream = ssc.queueStream(rdd_queue)
        
        # 使用updateStateByKey进行累计统计，维护状态
        def update_function(new_values, running_state):
            if running_state is None:
                running_sum = 0
            else:
                running_sum, batch_ids = running_state
                
            # 更新总和和批次ID列表
            new_sum = running_sum + sum(new_values)
            new_batch_ids = batch_ids + [x[0] for x in new_values]
            
            return (new_sum, new_batch_ids)
        
        # 提取数值部分
        values_stream = stream.mapValues(lambda x: x)
        
        # 计算累计总和
        cumulative_sum = values_stream.updateStateByKey(update_function)
        
        # 提取总和和批次ID
        output_stream = cumulative_sum.mapValues(lambda state: (state[0], len(state[1])))
        
        # 输出结果
        output_stream.pprint()
        
        return ssc
    
    # 使用检查点创建或恢复StreamingContext
    ssc = StreamingContext.getOrCreate(checkpoint_dir, function_to_create_context)
    
    # 启动流计算
    ssc.start()
    
    # 运行一段时间
    time.sleep(20)
    
    print("模拟驱动程序故障...")
    # 注意：在实际应用中，驱动程序故障是意外的，这里仅作演示
    # 我们停止但不清理，以便下一次启动时可以从检查点恢复
    
    # 停止流计算但不清理检查点
    ssc.stop(stopSparkContext=True, stopGraceFully=False)
    
    print("驱动程序已停止，可以重新启动以从检查点恢复")
    print("在真实环境中，应使用部署系统自动重启驱动程序")

if __name__ == "__main__":
    # 多次运行此函数来模拟驱动程序故障恢复
    print("第一次运行:")
    driver_fault_tolerance()
    
    time.sleep(2)
    
    print("\n第二次运行（从检查点恢复）:")
    driver_fault_tolerance()
```

### 6.5.2 工作节点故障恢复

```python
# code/streaming-examples/worker_fault_tolerance.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random
import os

def worker_fault_tolerance():
    print("=== 工作节点容错机制演示 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "WorkerFaultTolerance")
    ssc = StreamingContext(sc, 5)  # 5秒的批处理间隔
    
    # 设置检查点目录
    ssc.checkpoint("checkpoint_worker")
    
    # 创建模拟数据流
    def generate_rdds():
        for i in range(12):
            # 每个批次包含更多数据，以模拟较重的处理负载
            numbers = [random.randint(1, 1000) for _ in range(1000)]
            yield sc.parallelize(numbers, numSlices=10)  # 分成10个分区
    
    rdd_queue = list(generate_rdds())
    number_stream = ssc.queueStream(rdd_queue)
    
    # 模拟复杂的转换操作，可能会失败
    def complex_computation(number):
        # 模拟复杂的计算
        import time
        time.sleep(0.001)  # 短暂延迟
        
        # 模拟可能的失败（1%的几率）
        if random.random() < 0.01:
            raise RuntimeError("模拟工作节点失败")
        
        return number * number
    
    def safe_computation(number):
        """带异常处理的计算函数"""
        try:
            return complex_computation(number)
        except Exception as e:
            print(f"计算错误: {e}")
            return 0  # 失败时返回默认值
    
    # 应用安全的计算函数
    processed_stream = number_stream.map(safe_computation)
    
    # 聚合结果
    sum_per_batch = processed_stream.reduce(lambda a, b: a + b)
    
    # 使用窗口操作计算移动平均
    windowed_avg = sum_per_batch.map(lambda x: (x, 1)) \
                               .reduceByWindow(
                                   lambda a, b: (a[0] + b[0], a[1] + b[1]),
                                   lambda a, b: (a[0] - b[0], a[1] - b[1]),
                                   15,  # 窗口长度15秒
                                   5    # 滑动间隔5秒
                               ) \
                               .map(lambda x: x[0] / x[1] if x[1] > 0 else 0)
    
    # 输出结果
    print("每批次的计算总和:")
    sum_per_batch.pprint()
    
    print("移动平均值（窗口15秒）:")
    windowed_avg.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间
    time.sleep(60)
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("工作节点容错机制演示完成")

if __name__ == "__main__":
    worker_fault_tolerance()
```

## 6.6 实战案例：实时网站日志分析

```python
# code/streaming-examples/web_log_analysis.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
import time
import re
import random

def web_log_analysis():
    print("=== 实时网站日志分析 ===")
    
    # 创建SparkContext和StreamingContext
    sc = SparkContext("local[*]", "WebLogAnalysis")
    ssc = StreamingContext(sc, 10)  # 10秒的批处理间隔
    
    # 设置检查点目录
    ssc.checkpoint("checkpoint_weblog")
    
    # 模拟Web日志数据
    def generate_log_lines():
        ip_addresses = [
            "192.168.1.1", "10.0.0.1", "172.16.0.1", "203.0.113.1", "198.51.100.1",
            "192.0.2.1", "192.168.2.1", "10.0.0.2", "172.16.0.2", "203.0.113.2"
        ]
        
        pages = [
            "/index.html", "/about.html", "/products.html", "/contact.html",
            "/login.html", "/dashboard.html", "/profile.html", "/search.html"
        ]
        
        methods = ["GET", "POST", "PUT", "DELETE"]
        status_codes = ["200", "301", "404", "500"]
        
        # 生成几个批次的日志数据
        for batch_id in range(8):
            batch_lines = []
            for _ in range(20):  # 每批次20条日志
                ip = random.choice(ip_addresses)
                timestamp = time.strftime("%d/%b/%Y:%H:%M:%S")
                method = random.choice(methods)
                page = random.choice(pages)
                status = random.choice(status_codes)
                size = random.randint(500, 5000)
                
                # Apache通用日志格式
                log_line = f'{ip} - - [{timestamp}] "{method} {page} HTTP/1.1" {status} {size}'
                batch_lines.append(log_line)
            
            yield sc.parallelize(batch_lines)
    
    # 创建日志数据流
    log_stream = ssc.queueStream(list(generate_log_lines()))
    
    # 解析日志
    log_pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<timestamp>.*?)\] "(?P<method>\w+) (?P<page>\S+) .*?" (?P<status>\d+) (?P<size>\d+)'
    )
    
    def parse_log_line(line):
        """解析单行日志"""
        match = log_pattern.match(line)
        if match:
            return {
                "ip": match.group("ip"),
                "timestamp": match.group("timestamp"),
                "method": match.group("method"),
                "page": match.group("page"),
                "status": int(match.group("status")),
                "size": int(match.group("size"))
            }
        else:
            return None
    
    # 解析日志流
    parsed_logs = log_stream.map(parse_log_line).filter(lambda x: x is not None)
    
    # 实时分析1: HTTP状态码统计
    status_counts = parsed_logs.map(lambda log: (log["status"], 1)) \
                             .reduceByKey(lambda a, b: a + b)
    
    print("HTTP状态码实时统计:")
    status_counts.pprint()
    
    # 实时分析2: 热门页面统计
    page_counts = parsed_logs.map(lambda log: (log["page"], 1)) \
                            .reduceByKey(lambda a, b: a + b)
    
    print("热门页面实时统计:")
    page_counts.transform(lambda rdd: rdd.sortBy(lambda x: x[1], ascending=False)).pprint()
    
    # 实时分析3: 错误页面检测
    error_pages = parsed_logs.filter(lambda log: log["status"] >= 400) \
                            .map(lambda log: (log["page"], log["status"])) \
                            .reduceByKey(lambda a, b: a)  # 保留最新的状态码
    
    print("错误页面检测:")
    error_pages.pprint()
    
    # 实时分析4: 滑动窗口分析 - 平均响应大小
    def calculate_avg_size(rdd):
        if not rdd.isEmpty():
            total_size = rdd.map(lambda x: x[1]).sum()
            count = rdd.count()
            return f"平均响应大小: {total_size/count:.2f} bytes"
        else:
            return "无数据"
    
    # 将每条日志转换为(1, size)的形式
    size_stream = parsed_logs.map(lambda log: (1, log["size"]))
    
    # 计算窗口内的平均大小
    windowed_avg_size = size_stream.reduceByWindow(
        lambda a, b: (a[0] + b[0], a[1] + b[1]),
        30,  # 窗口长度30秒
        10   # 滑动间隔10秒
    )
    
    def print_avg_size(rdd):
        if not rdd.isEmpty():
            total, count = rdd.first()
            print(f"--- 窗口内平均响应大小: {total/count:.2f} bytes ---")
    
    windowed_avg_size.foreachRDD(print_avg_size)
    
    # 实时分析5: 可疑IP检测 - 高频访问
    def update_ip_count(new_values, old_count):
        if old_count is None:
            old_count = 0
        return sum(new_values) + old_count
    
    ip_counts = parsed_logs.map(lambda log: (log["ip"], 1)) \
                         .updateStateByKey(update_ip_count) \
                         .filter(lambda x: x[1] > 10)  # 访问次数超过10次的IP
    
    print("可疑IP检测 (访问次数>10):")
    ip_counts.pprint()
    
    # 启动流计算
    ssc.start()
    
    # 运行足够长的时间
    time.sleep(80)
    
    # 停止流计算
    ssc.stop(stopSparkContext=True)
    
    print("实时网站日志分析演示完成")

if __name__ == "__main__":
    web_log_analysis()
```

## 6.7 Structured Streaming简介

Structured Streaming是Spark 2.0引入的新的流处理引擎，基于DataFrame和Dataset API，提供更简单、更强大的流处理能力。

### 6.7.1 Structured Streaming基础

```python
# code/streaming-examples/structured_streaming_basic.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, current_timestamp, lit
import time
import random

def structured_streaming_basic():
    print("=== Structured Streaming基础演示 ===")
    
    # 创建SparkSession
    spark = SparkSession.builder \
                         .appName("StructuredStreamingBasic") \
                         .getOrCreate()
    
    # 设置日志级别
    spark.sparkContext.setLogLevel("WARN")
    
    # 创建模拟的数据流源
    # 在实际应用中，可以使用socket、kafka等作为数据源
    lines = spark.readStream \
                  .format("rate") \  # 使用内置的rate源生成数据
                  .option("rowsPerSecond", 5) \  # 每秒5行
                  .load()
    
    # 查看原始数据的schema
    print("原始数据schema:")
    lines.printSchema()
    
    # 转换数据：添加单词列
    words = ["spark", "hadoop", "hive", "flink", "kafka"]
    words_stream = lines.withColumn("word", lit(random.choice(words))) \
                       .select("timestamp", "value", "word")
    
    # 输出结果到控制台
    print("输出到控制台:")
    query = words_stream.writeStream \
                        .format("console") \
                        .option("truncate", "false") \
                        .outputMode("append") \
                        .start()
    
    # 运行30秒
    time.sleep(30)
    
    # 停止查询
    query.stop()
    
    # 示例2: 聚合操作 - 统计每个单词出现的次数
    print("\n词频统计:")
    word_counts = words_stream.groupBy("word") \
                             .count() \
                             .orderBy(col("count").desc())
    
    query2 = word_counts.writeStream \
                         .format("console") \
                         .option("truncate", "false") \
                         .outputMode("complete") \  # 完整模式：每次输出完整结果
                         .start()
    
    # 运行30秒
    time.sleep(30)
    
    # 停止查询
    query2.stop()
    
    # 示例3: 窗口操作 - 每10秒统计一次词频
    print("\n窗口词频统计:")
    windowed_counts = words_stream \
        .withWatermark("timestamp", "1 minute") \  # 设置水印，处理延迟数据
        .groupBy(window("timestamp", "10 seconds"), "word") \
        .count() \
        .orderBy("window")
    
    query3 = windowed_counts.writeStream \
                           .format("console") \
                           .option("truncate", "false") \
                           .outputMode("complete") \
                           .start()
    
    # 运行40秒
    time.sleep(40)
    
    # 停止查询
    query3.stop()
    
    spark.stop()
    print("Structured Streaming基础演示完成")

if __name__ == "__main__":
    structured_streaming_basic()
```

## 6.8 性能调优

### 6.8.1 批处理间隔优化

```python
# code/streaming-examples/batch_interval_tuning.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random

def batch_interval_tuning():
    print("=== 批处理间隔调优演示 ===")
    
    # 测试不同的批处理间隔
    intervals = [1, 2, 5, 10]
    
    for interval in intervals:
        print(f"\n测试批处理间隔: {interval}秒")
        
        # 创建SparkContext和StreamingContext
        sc = SparkContext("local[*]", f"BatchInterval{interval}")
        ssc = StreamingContext(sc, interval)  # 设置不同的批处理间隔
        
        # 创建模拟数据流
        def generate_rdds():
            for i in range(5):
                # 根据批处理间隔调整数据量，保持总体处理量相似
                data_size = max(10, 100 // interval)
                numbers = [random.randint(1, 1000) for _ in range(data_size)]
                yield sc.parallelize(numbers)
        
        rdd_queue = list(generate_rdds())
        stream = ssc.queueStream(rdd_queue)
        
        # 执行计算密集型操作
        processed_stream = stream.map(lambda x: x * x) \
                               .filter(lambda x: x > 1000) \
                               .reduce(lambda a, b: a + b)
        
        # 记录处理时间
        def process_with_timing(rdd):
            if not rdd.isEmpty():
                start_time = time.time()
                result = rdd.collect()[0]  # 获取结果（只有一个值）
                end_time = time.time()
                print(f"批处理结果: {result}, 处理时间: {end_time - start_time:.4f}秒")
        
        processed_stream.foreachRDD(process_with_timing)
        
        # 启动流计算
        ssc.start()
        
        # 运行足够长的时间
        time.sleep(interval * 6)
        
        # 停止流计算
        ssc.stop(stopSparkContext=True)
    
    print("批处理间隔调优演示完成")

if __name__ == "__main__":
    batch_interval_tuning()
```

### 6.8.2 并行度优化

```python
# code/streaming-examples/parallelism_tuning.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import time
import random

def parallelism_tuning():
    print("=== 并行度调优演示 ===")
    
    # 测试不同的并行度
    parallelism_levels = [2, 4, 8]
    
    for level in parallelism_levels:
        print(f"\n测试并行度: {level}")
        
        # 创建SparkContext和StreamingContext
        sc = SparkContext("local[*]", f"Parallelism{level}")
        ssc = StreamingContext(sc, 5)
        
        # 创建模拟数据流
        def generate_rdds():
            for i in range(3):
                # 创建大数据集
                data_size = 10000
                numbers = [random.randint(1, 1000) for _ in range(data_size)]
                # 使用指定的并行度
                rdd = sc.parallelize(numbers, numSlices=level)
                yield rdd
        
        rdd_queue = list(generate_rdds())
        stream = ssc.queueStream(rdd_queue)
        
        # 执行计算
        processed_stream = stream.map(lambda x: x * x) \
                               .reduce(lambda a, b: a + b)
        
        # 记录处理时间和分区数
        def process_with_timing(rdd):
            if not rdd.isEmpty():
                start_time = time.time()
                result = rdd.collect()[0]
                end_time = time.time()
                print(f"分区数: {rdd.getNumPartitions()}, 结果: {result}, 处理时间: {end_time - start_time:.4f}秒")
        
        processed_stream.foreachRDD(process_with_timing)
        
        # 启动流计算
        ssc.start()
        
        # 运行足够长的时间
        time.sleep(20)
        
        # 停止流计算
        ssc.stop(stopSparkContext=True)
    
    print("并行度调优演示完成")

if __name__ == "__main__":
    parallelism_tuning()
```

## 6.9 小结

本章详细介绍了Spark Streaming实时数据处理，包括DStream基础操作、输入输出源、窗口操作、容错机制以及性能调优。Spark Streaming通过微批处理模型，将流计算转换为批处理，利用Spark的批处理引擎实现高效的流处理。同时，我们也介绍了Structured Streaming，这是Spark 2.0引入的新一代流处理引擎，提供了更简单、更强大的API。在下一章中，我们将学习Spark MLlib机器学习库。

## 实验与练习

1. 实现一个简单的实时词频统计系统，处理来自Socket的数据流
2. 使用窗口操作实现滑动平均值计算
3. 实现实时监控和异常检测系统，检测数据流中的异常值
4. 比较Spark Streaming和Structured Streaming的性能差异
5. 实现一个容错的流处理应用，能够从检查点恢复状态

## 参考资源

- [Spark Streaming编程指南](https://spark.apache.org/docs/latest/streaming-programming-guide.html)
- [Structured Streaming编程指南](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)