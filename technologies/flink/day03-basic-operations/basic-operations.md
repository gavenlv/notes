# Flink 基础操作详解 (Day 03) - 深入理解数据源、转换和输出

## 1. Flink 数据源详解

### 1.1 什么是数据源？

数据源是 Flink 程序的起点，负责从外部系统读取数据并将其转换为 Flink 内部的数据流。可以把它想象成自来水公司的水源，所有后续的处理都从这里开始。

### 1.2 内置数据源

#### 文件数据源

文件数据源是最常见的数据源类型，用于读取本地或分布式文件系统中的数据。

```java
// 读取本地文本文件
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
DataStream<String> textFileStream = env.readTextFile("file:///path/to/file.txt");

// 读取HDFS文件
DataStream<String> hdfsStream = env.readTextFile("hdfs://namenode:port/path/to/file.txt");

// 读取压缩文件（自动解压）
DataStream<String> compressedStream = env.readTextFile("file:///path/to/file.gz");
```

#### Socket 数据源

Socket 数据源用于从网络套接字读取数据，通常用于测试和开发环境。

```java
// 从Socket读取文本数据流
DataStream<String> socketStream = env.socketTextStream("localhost", 9999);

// 带参数的Socket数据源
DataStream<String> socketStreamWithParams = env.socketTextStream(
    "localhost",           // 主机名
    9999,                 // 端口号
    "\n",                 // 行分隔符
    30000                 // 连接超时时间（毫秒）
);
```

#### 集合数据源

集合数据源用于从Java集合创建数据流，主要用于测试和演示。

```java
// 从List创建数据流
List<String> dataList = Arrays.asList("apple", "banana", "orange");
DataStream<String> listStream = env.fromCollection(dataList);

// 从数组创建数据流
String[] dataArray = {"apple", "banana", "orange"};
DataStream<String> arrayStream = env.fromElements(dataArray);

// 从迭代器创建数据流
Iterator<Integer> iterator = Arrays.asList(1, 2, 3, 4, 5).iterator();
DataStream<Integer> iteratorStream = env.fromCollection(iterator, Integer.class);
```

### 1.3 连接器数据源

连接器是 Flink 与外部系统集成的桥梁，提供了丰富的数据源连接器。

#### Kafka 连接器

Kafka 是最常用的流处理数据源之一。

```java
// 添加Maven依赖
/*
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-kafka_2.11</artifactId>
    <version>1.13.0</version>
</dependency>
*/

// Kafka消费者配置
Properties properties = new Properties();
properties.setProperty("bootstrap.servers", "localhost:9092");
properties.setProperty("group.id", "flink-consumer-group");

// 创建Kafka数据源
FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
    "topic-name",                    // Kafka主题名
    new SimpleStringSchema(),        // 数据序列化方式
    properties                       // Kafka配置
);

// 设置起始消费位置
kafkaConsumer.setStartFromLatest();     // 从最新消息开始
// kafkaConsumer.setStartFromEarliest();   // 从最早消息开始
// kafkaConsumer.setStartFromTimestamp(1625097600000L); // 从指定时间戳开始

DataStream<String> kafkaStream = env.addSource(kafkaConsumer);
```

#### RabbitMQ 连接器

```java
// 添加Maven依赖
/*
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-rabbitmq_2.11</artifactId>
    <version>1.13.0</version>
</dependency>
*/

// RabbitMQ连接配置
RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
    .setHost("localhost")
    .setPort(5672)
    .setUserName("guest")
    .setPassword("guest")
    .setVirtualHost("/")
    .build();

// 创建RabbitMQ数据源
DataStream<String> rabbitMQStream = env
    .addSource(new RMQSource<>(
        connectionConfig,            // 连接配置
        "queue-name",                // 队列名
        true,                        // 使用correlation ids
        new SimpleStringSchema()     // 数据序列化方式
    ));
```

## 2. Flink 转换操作详解

### 2.1 基本转换操作

#### Map 转换

Map 转换是最基础的转换操作，对数据流中的每个元素应用一个函数，产生一个新的元素。

```java
// 将字符串转换为大写
DataStream<String> inputStream = env.fromElements("hello", "world", "flink");
DataStream<String> upperCaseStream = inputStream.map(String::toUpperCase);

// 复杂的数据转换
DataStream<String> textStream = env.socketTextStream("localhost", 9999);
DataStream<Integer> wordLengthStream = textStream.map(
    new MapFunction<String, Integer>() {
        @Override
        public Integer map(String value) throws Exception {
            return value.length(); // 计算每个字符串的长度
        }
    }
);

// 使用Lambda表达式简化
DataStream<Integer> wordLengthStreamLambda = textStream.map(String::length);
```

#### FlatMap 转换

FlatMap 转换比 Map 更强大，它可以将一个元素转换为零个、一个或多个元素。

```java
// 分割句子为单词
DataStream<String> sentenceStream = env.fromElements(
    "Hello World", 
    "Flink is awesome", 
    "Stream processing"
);

DataStream<String> wordStream = sentenceStream.flatMap(
    new FlatMapFunction<String, String>() {
        @Override
        public void flatMap(String sentence, Collector<String> out) throws Exception {
            // 将句子分割为单词并逐个输出
            for (String word : sentence.split(" ")) {
                out.collect(word);
            }
        }
    }
);

// 使用Lambda表达式简化
DataStream<String> wordStreamLambda = sentenceStream.flatMap(
    (String sentence, Collector<String> out) -> {
        for (String word : sentence.split(" ")) {
            out.collect(word);
        }
    }
);
```

#### Filter 转换

Filter 转换用于过滤数据流，只保留满足条件的元素。

```java
// 过滤出长度大于5的字符串
DataStream<String> inputStream = env.fromElements("apple", "banana", "cat", "elephant");
DataStream<String> filteredStream = inputStream.filter(
    new FilterFunction<String>() {
        @Override
        public boolean filter(String value) throws Exception {
            return value.length() > 5;
        }
    }
);

// 使用Lambda表达式简化
DataStream<String> filteredStreamLambda = inputStream.filter(s -> s.length() > 5);

// 复杂过滤条件
DataStream<Integer> numberStream = env.fromElements(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
DataStream<Integer> evenNumbers = numberStream.filter(n -> n % 2 == 0); // 偶数
DataStream<Integer> primeNumbers = numberStream.filter(n -> isPrime(n)); // 质数
```

### 2.2 聚合转换操作

#### KeyBy 转换

KeyBy 是流处理中最重要的转换之一，它将数据流按键分组，使得相同键的数据被发送到同一个处理实例。

```java
// 定义数据类
public class Transaction {
    private String userId;
    private String product;
    private double amount;
    
    // 构造函数、getter和setter省略
}

// 按用户ID分组
DataStream<Transaction> transactionStream = env.addSource(new TransactionSource());
KeyedStream<Transaction, String> keyedStream = transactionStream.keyBy(
    new KeySelector<Transaction, String>() {
        @Override
        public String getKey(Transaction transaction) throws Exception {
            return transaction.getUserId();
        }
    }
);

// 使用Lambda表达式简化
KeyedStream<Transaction, String> keyedStreamLambda = transactionStream.keyBy(
    Transaction::getUserId
);

// 按多个字段分组
KeyedStream<Transaction, Tuple2<String, String>> multiKeyedStream = 
    transactionStream.keyBy(
        new KeySelector<Transaction, Tuple2<String, String>>() {
            @Override
            public Tuple2<String, String> getKey(Transaction transaction) throws Exception {
                return new Tuple2<>(transaction.getUserId(), transaction.getProduct());
            }
        }
    );
```

#### Reduce 转换

Reduce 转换对分组后的数据进行聚合操作。

```java
// 计算每个用户的累计消费金额
KeyedStream<Transaction, String> keyedStream = transactionStream.keyBy(Transaction::getUserId);
DataStream<Transaction> reducedStream = keyedStream.reduce(
    new ReduceFunction<Transaction>() {
        @Override
        public Transaction reduce(Transaction t1, Transaction t2) throws Exception {
            // 创建新的Transaction对象，金额为两者之和
            return new Transaction(
                t1.getUserId(),
                t1.getProduct(),
                t1.getAmount() + t2.getAmount()
            );
        }
    }
);

// 使用Lambda表达式简化
DataStream<Transaction> reducedStreamLambda = keyedStream.reduce(
    (t1, t2) -> new Transaction(
        t1.getUserId(),
        t1.getProduct(),
        t1.getAmount() + t2.getAmount()
    )
);
```

#### Aggregation 转换

Flink 提供了一些预定义的聚合函数，如 sum、min、max 等。

```java
// 定义带累计金额的交易类
public class TransactionWithTotal {
    private String userId;
    private String product;
    private double amount;
    private double totalAmount;
    
    // 构造函数、getter和setter省略
}

// 计算每个用户的累计消费总和
KeyedStream<TransactionWithTotal, String> keyedStream = 
    transactionStream.keyBy(TransactionWithTotal::getUserId);

DataStream<TransactionWithTotal> sumStream = keyedStream.sum("totalAmount");
DataStream<TransactionWithTotal> maxStream = keyedStream.max("amount");
DataStream<TransactionWithTotal> minStream = keyedStream.min("amount");

// 获取字段最大值及其对应的元素
DataStream<TransactionWithTotal> maxByStream = keyedStream.maxBy("amount");
```

### 2.3 多流转换操作

#### Connect 转换

Connect 转换可以连接两个数据流，它们可以是不同类型的数据流。

```java
// 定义两个不同类型的数据流
DataStream<String> controlStream = env.socketTextStream("localhost", 9998);
DataStream<Long> dataStream = env.socketTextStream("localhost", 9999)
    .map(Long::parseLong);

// 连接两个数据流
ConnectedStreams<Long, String> connectedStreams = dataStream.connect(controlStream);

// 对连接后的流进行处理
DataStream<String> resultStream = connectedStreams.process(
    new CoProcessFunction<Long, String, String>() {
        private boolean enabled = true;
        
        @Override
        public void processElement1(Long value, Context ctx, Collector<String> out) 
                throws Exception {
            if (enabled) {
                out.collect("Data: " + value);
            }
        }
        
        @Override
        public void processElement2(String controlSignal, Context ctx, Collector<String> out) 
                throws Exception {
            if ("DISABLE".equals(controlSignal)) {
                enabled = false;
            } else if ("ENABLE".equals(controlSignal)) {
                enabled = true;
            }
        }
    }
);
```

#### Union 转换

Union 转换可以合并多个相同类型的数据流。

```java
// 创建多个相同类型的数据流
DataStream<String> stream1 = env.fromElements("A", "B", "C");
DataStream<String> stream2 = env.fromElements("D", "E", "F");
DataStream<String> stream3 = env.fromElements("G", "H", "I");

// 合并多个数据流
DataStream<String> unionStream = stream1.union(stream2, stream3);

// Union操作后的数据流保持原有的并行度
unionStream.print();
```

#### Join 转换

Join 转换用于连接两个数据流中的元素。

```java
// 定义用户和订单数据流
DataStream<User> userStream = env.addSource(new UserSource());
DataStream<Order> orderStream = env.addSource(new OrderSource());

// 窗口连接
DataStream<Tuple2<User, Order>> joinedStream = userStream.join(orderStream)
    .where(User::getId)           // 用户流的连接键
    .equalTo(Order::getUserId)    // 订单流的连接键
    .window(TumblingEventTimeWindows.of(Time.minutes(5))) // 窗口大小
    .apply(new JoinFunction<User, Order, Tuple2<User, Order>>() {
        @Override
        public Tuple2<User, Order> join(User user, Order order) throws Exception {
            return new Tuple2<>(user, order);
        }
    });
```

## 3. Flink 输出操作详解

### 3.1 内置输出操作

#### Print 输出

Print 是最简单的输出方式，主要用于调试和测试。

```java
DataStream<String> inputStream = env.fromElements("Hello", "Flink", "World");

// 直接打印到控制台
inputStream.print();

// 带标签的打印
inputStream.print("MyStream");

// 打印到标准错误输出
inputStream.printToErr();
```

#### WriteAsText 输出

将数据流写入文本文件。

```java
DataStream<String> inputStream = env.fromElements("Hello", "Flink", "World");

// 写入本地文件系统
inputStream.writeAsText("file:///path/to/output.txt");

// 写入HDFS
inputStream.writeAsText("hdfs://namenode:port/path/to/output.txt");

// 设置写入模式
inputStream.writeAsText("file:///path/to/output.txt", FileSystem.WriteMode.OVERWRITE);
```

#### WriteAsCsv 输出

将数据流写入CSV格式文件。

```java
// 定义数据类
public class Person {
    private String name;
    private int age;
    private String city;
    
    // 构造函数、getter和setter省略
}

DataStream<Person> personStream = env.fromElements(
    new Person("Alice", 25, "New York"),
    new Person("Bob", 30, "San Francisco")
);

// 写入CSV文件
personStream.writeAsCsv("file:///path/to/persons.csv");

// 自定义CSV格式
personStream.writeAsCsv(
    "file:///path/to/persons.csv",
    FileSystem.WriteMode.OVERWRITE,
    CsvOutputFormat.DEFAULT_LINE_DELIMITER,
    ","  // 字段分隔符
);
```

### 3.2 连接器输出

#### Kafka 输出

```java
// 添加Maven依赖
/*
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-kafka_2.11</artifactId>
    <version>1.13.0</version>
</dependency>
*/

// Kafka生产者配置
Properties properties = new Properties();
properties.setProperty("bootstrap.servers", "localhost:9092");

// 创建Kafka生产者
FlinkKafkaProducer<String> kafkaProducer = new FlinkKafkaProducer<>(
    "output-topic",                 // Kafka主题名
    new SimpleStringSchema(),       // 数据序列化方式
    properties                      // Kafka配置
);

// 将数据流写入Kafka
DataStream<String> inputStream = env.fromElements("message1", "message2", "message3");
inputStream.addSink(kafkaProducer);
```

#### Elasticsearch 输出

```java
// 添加Maven依赖
/*
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-elasticsearch6_2.11</artifactId>
    <version>1.13.0</version>
</dependency>
*/

// Elasticsearch配置
List<HttpHost> httpHosts = new ArrayList<>();
httpHosts.add(new HttpHost("127.0.0.1", 9200, "http"));

ElasticsearchSink.Builder<String> esSinkBuilder = new ElasticsearchSink.Builder<>(
    httpHosts,
    new ElasticsearchSinkFunction<String>() {
        public IndexRequest createIndexRequest(String element) {
            Map<String, String> json = new HashMap<>();
            json.put("data", element);
            
            return Requests.indexRequest()
                .index("my-index")
                .type("my-type")
                .source(json);
        }
        
        @Override
        public void process(String element, RuntimeContext ctx, RequestIndexer indexer) {
            indexer.add(createIndexRequest(element));
        }
    }
);

// 设置批量处理参数
esSinkBuilder.setBulkFlushMaxActions(1000);

// 将数据流写入Elasticsearch
DataStream<String> inputStream = env.fromElements("doc1", "doc2", "doc3");
inputStream.addSink(esSinkBuilder.build());
```

#### JDBC 输出

```java
// 添加Maven依赖
/*
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-jdbc_2.11</artifactId>
    <version>1.13.0</version>
</dependency>
*/

// JDBC连接配置
String driverName = "com.mysql.cj.jdbc.Driver";
String dbUrl = "jdbc:mysql://localhost:3306/testdb";
String username = "root";
String password = "password";

// 创建JDBC Sink
JdbcSink.sink(
    "INSERT INTO transactions (user_id, product, amount) VALUES (?, ?, ?)", // SQL语句
    (statement, transaction) -> {  // 参数设置函数
        statement.setString(1, transaction.getUserId());
        statement.setString(2, transaction.getProduct());
        statement.setDouble(3, transaction.getAmount());
    },
    new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
        .withDriverName(driverName)
        .withUrl(dbUrl)
        .withUsername(username)
        .withPassword(password)
        .build()
);
```

## 4. 执行环境配置详解

### 4.1 基本执行环境配置

```java
// 创建本地执行环境
StreamExecutionEnvironment localEnv = StreamExecutionEnvironment.createLocalEnvironment();

// 创建远程执行环境
StreamExecutionEnvironment remoteEnv = StreamExecutionEnvironment.createRemoteEnvironment(
    "localhost",  // JobManager主机
    6123,         // JobManager端口
    "path/to/jar" // 需要的JAR文件
);

// 获取默认执行环境
StreamExecutionEnvironment defaultEnv = StreamExecutionEnvironment.getExecutionEnvironment();
```

### 4.2 并行度配置

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 设置全局并行度
env.setParallelism(4);

// 为特定操作设置并行度
DataStream<String> inputStream = env.fromElements("A", "B", "C", "D");
inputStream.map(String::toUpperCase).setParallelism(2); // Map操作并行度为2

// 获取默认并行度
int defaultParallelism = env.getParallelism();
System.out.println("Default parallelism: " + defaultParallelism);
```

### 4.3 时间特性配置

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 设置时间特性为事件时间
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

// 设置时间特性为处理时间
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

// 设置时间特性为摄取时间
env.setStreamTimeCharacteristic(TimeCharacteristic.IngestionTime);
```

### 4.4 检查点配置

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 启用检查点
env.enableCheckpointing(5000); // 每5秒创建一个检查点

// 设置检查点模式
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);

// 设置检查点超时时间
env.getCheckpointConfig().setCheckpointTimeout(60000); // 60秒

// 设置检查点之间的最小时间间隔
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(500);

// 设置同时进行的检查点数量
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);

// 启用检查点外部化
env.getCheckpointConfig().enableExternalizedCheckpoints(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);
```

## 5. 实例演示：实时温度监控系统

让我们通过一个完整的例子来理解这些操作：

### 5.1 场景描述

构建一个实时温度监控系统，需要实现：
1. 从传感器读取温度数据
2. 过滤异常温度数据
3. 计算每个传感器的平均温度
4. 检测温度异常并发出警报
5. 将结果存储到数据库

### 5.2 代码实现

```java
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.util.Collector;

import java.util.Properties;

/**
 * 实时温度监控系统示例
 */
public class TemperatureMonitoringSystem {
    
    public static void main(String[] args) throws Exception {
        // 创建执行环境
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 配置执行环境
        env.setParallelism(4);
        env.enableCheckpointing(5000);
        
        // 1. 从Kafka读取传感器数据
        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", "localhost:9092");
        kafkaProps.setProperty("group.id", "temperature-monitor");
        
        FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
            "sensor-data",
            new SimpleStringSchema(),
            kafkaProps
        );
        
        DataStream<String> sensorDataStream = env.addSource(kafkaConsumer);
        
        // 2. 解析传感器数据
        DataStream<TemperatureReading> temperatureStream = sensorDataStream
            .map(new SensorDataParser())
            .filter(new ValidTemperatureFilter()); // 过滤无效数据
        
        // 3. 计算每个传感器的平均温度（每分钟）
        DataStream<Tuple2<String, Double>> avgTemperatureStream = temperatureStream
            .keyBy(TemperatureReading::getSensorId)
            .timeWindow(Time.minutes(1))
            .aggregate(
                new TemperatureAggregate(), 
                new TemperatureWindowFunction()
            );
        
        // 4. 检测温度异常
        DataStream<TemperatureAlert> alertStream = temperatureStream
            .filter(new TemperatureAnomalyFilter(30.0)) // 检测超过30度的异常
            .map(new TemperatureAlertMapper());
        
        // 5. 输出结果
        // 打印平均温度
        avgTemperatureStream.print("Average Temperature: ");
        
        // 打印温度警报
        alertStream.print("Temperature Alert: ");
        
        // 将警报发送到另一个Kafka主题
        alertStream.map(TemperatureAlert::toString)
                  .addSink(new FlinkKafkaProducer<>(
                      "temperature-alerts",
                      new SimpleStringSchema(),
                      kafkaProps
                  ));
        
        // 执行程序
        env.execute("Temperature Monitoring System");
    }
    
    /**
     * 传感器数据解析函数
     */
    public static class SensorDataParser implements MapFunction<String, TemperatureReading> {
        @Override
        public TemperatureReading map(String value) throws Exception {
            // 假设数据格式为: sensorId,timestamp,temperature
            String[] parts = value.split(",");
            if (parts.length == 3) {
                String sensorId = parts[0];
                long timestamp = Long.parseLong(parts[1]);
                double temperature = Double.parseDouble(parts[2]);
                return new TemperatureReading(sensorId, timestamp, temperature);
            }
            return null; // 解析失败返回null
        }
    }
    
    /**
     * 有效温度数据过滤器
     */
    public static class ValidTemperatureFilter implements FilterFunction<TemperatureReading> {
        @Override
        public boolean filter(TemperatureReading reading) throws Exception {
            // 过滤无效温度数据（假设有效范围为-50到100度）
            return reading != null && 
                   reading.getTemperature() >= -50.0 && 
                   reading.getTemperature() <= 100.0;
        }
    }
    
    /**
     * 温度聚合函数
     */
    public static class TemperatureAggregate implements AggregateFunction<TemperatureReading, 
            TemperatureAccumulator, Double> {
        
        @Override
        public TemperatureAccumulator createAccumulator() {
            return new TemperatureAccumulator(0.0, 0);
        }
        
        @Override
        public TemperatureAccumulator add(TemperatureReading reading, 
                TemperatureAccumulator accumulator) {
            return new TemperatureAccumulator(
                accumulator.sum + reading.getTemperature(),
                accumulator.count + 1
            );
        }
        
        @Override
        public Double getResult(TemperatureAccumulator accumulator) {
            return accumulator.count > 0 ? accumulator.sum / accumulator.count : 0.0;
        }
        
        @Override
        public TemperatureAccumulator merge(TemperatureAccumulator a, TemperatureAccumulator b) {
            return new TemperatureAccumulator(
                a.sum + b.sum,
                a.count + b.count
            );
        }
    }
    
    /**
     * 温度窗口函数
     */
    public static class TemperatureWindowFunction 
            implements WindowFunction<Double, Tuple2<String, Double>, String, TimeWindow> {
        
        @Override
        public void apply(String sensorId, TimeWindow window, 
                Iterable<Double> averages, Collector<Tuple2<String, Double>> out) {
            Double avgTemp = averages.iterator().next();
            out.collect(new Tuple2<>(sensorId, avgTemp));
        }
    }
    
    /**
     * 温度异常检测过滤器
     */
    public static class TemperatureAnomalyFilter implements FilterFunction<TemperatureReading> {
        private final double threshold;
        
        public TemperatureAnomalyFilter(double threshold) {
            this.threshold = threshold;
        }
        
        @Override
        public boolean filter(TemperatureReading reading) throws Exception {
            return reading.getTemperature() > threshold;
        }
    }
    
    /**
     * 温度警报映射函数
     */
    public static class TemperatureAlertMapper 
            implements MapFunction<TemperatureReading, TemperatureAlert> {
        
        @Override
        public TemperatureAlert map(TemperatureReading reading) throws Exception {
            return new TemperatureAlert(
                reading.getSensorId(),
                reading.getTemperature(),
                System.currentTimeMillis(),
                "High temperature detected"
            );
        }
    }
}

// 数据类定义
class TemperatureReading {
    private String sensorId;
    private long timestamp;
    private double temperature;
    
    public TemperatureReading() {} // 无参构造函数
    
    public TemperatureReading(String sensorId, long timestamp, double temperature) {
        this.sensorId = sensorId;
        this.timestamp = timestamp;
        this.temperature = temperature;
    }
    
    // Getter和Setter方法
    public String getSensorId() { return sensorId; }
    public void setSensorId(String sensorId) { this.sensorId = sensorId; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    
    public double getTemperature() { return temperature; }
    public void setTemperature(double temperature) { this.temperature = temperature; }
}

class TemperatureAccumulator {
    public double sum;
    public int count;
    
    public TemperatureAccumulator(double sum, int count) {
        this.sum = sum;
        this.count = count;
    }
}

class TemperatureAlert {
    private String sensorId;
    private double temperature;
    private long timestamp;
    private String message;
    
    public TemperatureAlert() {} // 无参构造函数
    
    public TemperatureAlert(String sensorId, double temperature, long timestamp, String message) {
        this.sensorId = sensorId;
        this.temperature = temperature;
        this.timestamp = timestamp;
        this.message = message;
    }
    
    // Getter和Setter方法
    public String getSensorId() { return sensorId; }
    public void setSensorId(String sensorId) { this.sensorId = sensorId; }
    
    public double getTemperature() { return temperature; }
    public void setTemperature(double temperature) { this.temperature = temperature; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    @Override
    public String toString() {
        return "TemperatureAlert{" +
                "sensorId='" + sensorId + '\'' +
                ", temperature=" + temperature +
                ", timestamp=" + timestamp +
                ", message='" + message + '\'' +
                '}';
    }
}
```

## 6. 本章小结

通过本章的学习，你应该已经深入理解了：

1. **数据源操作**：内置数据源（文件、Socket、集合）和连接器数据源（Kafka、RabbitMQ等）的使用方法
2. **转换操作**：基本转换（Map、FlatMap、Filter）、聚合转换（KeyBy、Reduce、Aggregation）和多流转换（Connect、Union、Join）的详细用法
3. **输出操作**：内置输出（Print、WriteAsText、WriteAsCsv）和连接器输出（Kafka、Elasticsearch、JDBC）的配置和使用
4. **执行环境配置**：并行度、时间特性、检查点等重要配置项的设置方法
5. **实际应用**：通过温度监控系统的例子理解各种操作的实际应用场景

## 7. 下一步学习

掌握了这些基础操作后，建议继续学习：
- [Flink 数据流编程](../day04-data-streams/data-streams.md) - 深入学习 DataStream API 的高级特性和复杂应用场景

## 8. 参考资源

- [Apache Flink 官方文档 - DataStream API](https://flink.apache.org/docs/stable/dev/datastream_api.html)
- [Flink Connectors 文档](https://flink.apache.org/docs/stable/dev/connectors/)
- [Flink 窗口操作文档](https://flink.apache.org/docs/stable/dev/stream/operators/windows.html)
