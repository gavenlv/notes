# Flink DataStream API 详解 (Day 04) - 深入理解数据流编程

## 1. DataStream API 概述

### 1.1 什么是 DataStream API？

DataStream API 是 Flink 最核心的 API，用于处理无界和有界数据流。它提供了丰富的操作来转换和处理实时数据流，是构建流处理应用程序的基础。

可以把 DataStream API 想象成一套完整的工具箱，里面包含了处理数据流所需的各种工具：
- 数据源工具：用于从各种来源读取数据
- 转换工具：用于处理和转换数据
- 输出工具：用于将结果写入各种目标系统

### 1.2 DataStream 的核心概念

#### 数据流（DataStream）
DataStream 是 Flink 程序中数据的基本表示形式，它代表了一个不断流动的数据序列。每个 DataStream 都有以下特性：
- **无界性**：数据流可以是无限的（实时流）或有限的（批处理）
- **不可变性**：一旦创建，DataStream 本身不会改变，转换操作会创建新的 DataStream
- **分布式**：DataStream 在集群中分布式处理

#### 流处理 vs 批处理
```java
// 流处理示例 - 处理实时数据流
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
DataStream<String> stream = env.socketTextStream("localhost", 9999);
stream.map(String::toUpperCase).print();

// 批处理示例 - 处理有限数据集
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
DataStream<String> batch = env.fromElements("apple", "banana", "orange");
batch.map(String::toUpperCase).print();
```

## 2. DataStream 创建详解

### 2.1 从数据源创建 DataStream

#### 基于文件的数据流
```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 监控文件目录的变化
DataStream<String> fileStream = env.readTextFile("file:///path/to/directory");

// 读取单个文件
DataStream<String> singleFileStream = env.readTextFile("file:///path/to/file.txt");

// 读取压缩文件
DataStream<String> compressedFileStream = env.readTextFile("file:///path/to/file.gz");
```

#### 基于 Socket 的数据流
```java
// 基本 Socket 数据流
DataStream<String> socketStream = env.socketTextStream("localhost", 9999);

// 带参数的 Socket 数据流
DataStream<String> socketStreamWithParams = env.socketTextStream(
    "localhost",    // 主机名
    9999,          // 端口号
    "\n",          // 行分隔符
    30000          // 连接超时时间（毫秒）
);
```

#### 基于集合的数据流
```java
// 从 List 创建
List<String> dataList = Arrays.asList("apple", "banana", "orange");
DataStream<String> listStream = env.fromCollection(dataList);

// 从数组创建
String[] dataArray = {"apple", "banana", "orange"};
DataStream<String> arrayStream = env.fromElements(dataArray);

// 从迭代器创建
Iterator<Integer> iterator = Arrays.asList(1, 2, 3, 4, 5).iterator();
DataStream<Integer> iteratorStream = env.fromCollection(iterator, Integer.class);
```

### 2.2 自定义数据源

#### 实现 SourceFunction
```java
public class CustomSource implements SourceFunction<String> {
    private volatile boolean running = true;
    
    @Override
    public void run(SourceContext<String> ctx) throws Exception {
        int counter = 0;
        while (running) {
            // 模拟生成数据
            String data = "Data-" + counter++;
            ctx.collect(data);
            
            // 控制数据生成速度
            Thread.sleep(1000);
        }
    }
    
    @Override
    public void cancel() {
        running = false;
    }
}

// 使用自定义数据源
DataStream<String> customStream = env.addSource(new CustomSource());
```

#### 实现 ParallelSourceFunction
```java
public class ParallelCustomSource implements ParallelSourceFunction<String> {
    private volatile boolean running = true;
    
    @Override
    public void run(SourceContext<String> ctx) throws Exception {
        int subtaskIndex = getRuntimeContext().getIndexOfThisSubtask();
        
        int counter = 0;
        while (running) {
            // 每个并行实例生成不同的数据
            String data = "Subtask-" + subtaskIndex + "-Data-" + counter++;
            ctx.collect(data);
            
            Thread.sleep(1000);
        }
    }
    
    @Override
    public void cancel() {
        running = false;
    }
}

// 使用并行数据源
DataStream<String> parallelStream = env.addSource(new ParallelCustomSource()).setParallelism(4);
```

## 3. DataStream 转换操作详解

### 3.1 基本转换操作

#### Map 转换
Map 是最基础的转换操作，对数据流中的每个元素应用一个函数。

```java
// 简单的 Map 转换
DataStream<String> inputStream = env.fromElements("hello", "world", "flink");
DataStream<Integer> lengthStream = inputStream.map(String::length);

// 复杂的 Map 转换
DataStream<String> textStream = env.socketTextStream("localhost", 9999);
DataStream<ProcessedData> processedStream = textStream.map(new MapFunction<String, ProcessedData>() {
    @Override
    public ProcessedData map(String value) throws Exception {
        // 复杂的数据处理逻辑
        String[] parts = value.split(",");
        return new ProcessedData(parts[0], Double.parseDouble(parts[1]), System.currentTimeMillis());
    }
});
```

#### FlatMap 转换
FlatMap 可以将一个元素转换为零个、一个或多个元素。

```java
// 分割句子为单词
DataStream<String> sentenceStream = env.fromElements(
    "Hello World Flink", 
    "Stream Processing", 
    "Real Time Data"
);

DataStream<String> wordStream = sentenceStream.flatMap(
    new FlatMapFunction<String, String>() {
        @Override
        public void flatMap(String sentence, Collector<String> out) throws Exception {
            // 将句子分割为单词并逐个输出
            for (String word : sentence.split(" ")) {
                if (!word.isEmpty()) {
                    out.collect(word.toLowerCase());
                }
            }
        }
    }
);
```

#### Filter 转换
Filter 用于过滤数据流，只保留满足条件的元素。

```java
// 过滤出偶数
DataStream<Integer> numberStream = env.fromElements(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
DataStream<Integer> evenNumbers = numberStream.filter(n -> n % 2 == 0);

// 复杂过滤条件
DataStream<Transaction> transactionStream = env.addSource(new TransactionSource());
DataStream<Transaction> highValueTransactions = transactionStream.filter(
    new FilterFunction<Transaction>() {
        @Override
        public boolean filter(Transaction transaction) throws Exception {
            return transaction.getAmount() > 1000.0 && 
                   transaction.getTimestamp() > System.currentTimeMillis() - 3600000; // 1小时内
        }
    }
);
```

### 3.2 聚合转换操作

#### KeyBy 转换
KeyBy 是流处理中最重要的转换之一，它将数据流按键分组。

```java
// 定义交易数据类
public class Transaction {
    private String userId;
    private String product;
    private double amount;
    private long timestamp;
    
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

// 使用方法引用简化
KeyedStream<Transaction, String> keyedStreamLambda = transactionStream.keyBy(Transaction::getUserId);
```

#### Reduce 转换
Reduce 对分组后的数据进行聚合操作。

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
                t1.getAmount() + t2.getAmount(),
                Math.max(t1.getTimestamp(), t2.getTimestamp())
            );
        }
    }
);
```

#### Aggregation 转换
Flink 提供了一些预定义的聚合函数。

```java
// 定义带累计金额的交易类
public class TransactionWithStats {
    private String userId;
    private String product;
    private double amount;
    private double totalAmount;
    private int transactionCount;
    
    // 构造函数、getter和setter省略
}

// 计算聚合统计
KeyedStream<TransactionWithStats, String> keyedStream = 
    transactionStream.keyBy(TransactionWithStats::getUserId);

// 计算总金额
DataStream<TransactionWithStats> sumStream = keyedStream.sum("totalAmount");

// 计算最大金额
DataStream<TransactionWithStats> maxStream = keyedStream.max("amount");

// 获取最大金额的完整记录
DataStream<TransactionWithStats> maxByStream = keyedStream.maxBy("amount");
```

### 3.3 多流转换操作

#### Connect 转换
Connect 可以连接两个不同类型的数据流。

```java
// 定义控制流和数据流
DataStream<String> controlStream = env.socketTextStream("localhost", 9998);
DataStream<Transaction> dataStream = env.addSource(new TransactionSource());

// 连接两个数据流
ConnectedStreams<Transaction, String> connectedStreams = dataStream.connect(controlStream);

// 处理连接后的流
DataStream<String> resultStream = connectedStreams.process(
    new CoProcessFunction<Transaction, String, String>() {
        private boolean enabled = true;
        private Map<String, Double> userStats = new HashMap<>();
        
        @Override
        public void processElement1(Transaction transaction, Context ctx, Collector<String> out) 
                throws Exception {
            if (enabled) {
                // 更新用户统计信息
                String userId = transaction.getUserId();
                userStats.put(userId, userStats.getOrDefault(userId, 0.0) + transaction.getAmount());
                
                out.collect("Transaction: " + transaction + ", User Total: " + userStats.get(userId));
            }
        }
        
        @Override
        public void processElement2(String controlSignal, Context ctx, Collector<String> out) 
                throws Exception {
            if ("DISABLE".equals(controlSignal)) {
                enabled = false;
                out.collect("Processing disabled");
            } else if ("ENABLE".equals(controlSignal)) {
                enabled = true;
                out.collect("Processing enabled");
            } else if ("RESET".equals(controlSignal)) {
                userStats.clear();
                out.collect("Statistics reset");
            }
        }
    }
);
```

#### Union 转换
Union 可以合并多个相同类型的数据流。

```java
// 创建多个数据流
DataStream<String> stream1 = env.fromElements("A", "B", "C");
DataStream<String> stream2 = env.fromElements("D", "E", "F");
DataStream<String> stream3 = env.fromElements("G", "H", "I");

// 合并多个数据流
DataStream<String> unionStream = stream1.union(stream2, stream3);

// Union 操作后的数据流保持原有的并行度
unionStream.print();
```

#### Join 转换
Join 用于连接两个数据流中的元素。

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

## 4. 时间处理详解

### 4.1 时间概念

Flink 支持三种时间概念：

#### 事件时间（Event Time）
事件时间是事件实际发生的时间，通常在事件数据中包含时间戳。

```java
// 设置时间特性为事件时间
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

// 分配时间戳和水印
DataStream<Transaction> timedStream = transactionStream
    .assignTimestampsAndWatermarks(new BoundedOutOfOrdernessTimestampExtractor<Transaction>(
            Time.minutes(1)) {  // 允许1分钟的延迟
        @Override
        public long extractTimestamp(Transaction transaction) {
            return transaction.getTimestamp(); // 从事件中提取时间戳
        }
    });
```

#### 处理时间（Processing Time）
处理时间是事件在处理系统中被处理的时间。

```java
// 设置时间特性为处理时间
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

// 处理时间是系统默认时间，不需要特殊处理
DataStream<String> stream = env.socketTextStream("localhost", 9999);
```

#### 摄取时间（Ingestion Time）
摄取时间是事件进入 Flink 系统的时间。

```java
// 设置时间特性为摄取时间
env.setStreamTimeCharacteristic(TimeCharacteristic.IngestionTime);
```

### 4.2 水印（Watermark）机制

水印用于处理事件时间中的乱序问题。

```java
// 自定义水印生成器
public class CustomWatermarkGenerator implements AssignerWithPeriodicWatermarks<Transaction> {
    private long maxTimestamp = 0;
    private final long maxOutOfOrderness = 3500; // 3.5秒
    
    @Nullable
    @Override
    public Watermark getCurrentWatermark() {
        // 水印 = 最大时间戳 - 最大乱序时间
        return new Watermark(maxTimestamp - maxOutOfOrderness - 1);
    }
    
    @Override
    public long extractTimestamp(Transaction transaction, long previousElementTimestamp) {
        long timestamp = transaction.getTimestamp();
        maxTimestamp = Math.max(maxTimestamp, timestamp);
        return timestamp;
    }
}

// 使用自定义水印生成器
DataStream<Transaction> timedStream = transactionStream
    .assignTimestampsAndWatermarks(new CustomWatermarkGenerator());
```

## 5. 窗口操作详解

### 5.1 窗口类型

#### 滚动窗口（Tumbling Windows）
滚动窗口是固定大小、不重叠的窗口。

```java
// 基于时间的滚动窗口
DataStream<Transaction> timedWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .timeWindow(Time.minutes(5)) // 5分钟的滚动窗口
    .sum("amount");

// 基于计数的滚动窗口
DataStream<Transaction> countWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .countWindow(100) // 每100个元素的滚动窗口
    .sum("amount");
```

#### 滑动窗口（Sliding Windows）
滑动窗口是固定大小、可重叠的窗口。

```java
// 基于时间的滑动窗口
DataStream<Transaction> slidingWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(5))) // 10分钟窗口，5分钟滑动
    .sum("amount");

// 基于计数的滑动窗口
DataStream<Transaction> countSlidingWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .window(SlidingEventTimeWindows.of(Time.countOf(100), Time.countOf(10))) // 100个元素窗口，10个元素滑动
    .sum("amount");
```

#### 会话窗口（Session Windows）
会话窗口是基于活动间隙的窗口。

```java
// 基于事件时间的会话窗口
DataStream<Transaction> sessionWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(30))) // 30分钟不活动间隙
    .sum("amount");

// 基于处理时间的会话窗口
DataStream<Transaction> processingSessionWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .window(ProcessingTimeSessionWindows.withGap(Time.minutes(30)))
    .sum("amount");
```

### 5.2 窗口函数

#### ReduceFunction
```java
DataStream<Transaction> windowedStream = transactionStream
    .keyBy(Transaction::getUserId)
    .timeWindow(Time.minutes(5))
    .reduce(new ReduceFunction<Transaction>() {
        @Override
        public Transaction reduce(Transaction t1, Transaction t2) throws Exception {
            return new Transaction(
                t1.getUserId(),
                "aggregated",
                t1.getAmount() + t2.getAmount(),
                Math.max(t1.getTimestamp(), t2.getTimestamp())
            );
        }
    });
```

#### AggregateFunction
```java
// 定义聚合累加器
public class TransactionAccumulator {
    public double totalAmount = 0.0;
    public int count = 0;
    public long startTime = Long.MAX_VALUE;
    public long endTime = Long.MIN_VALUE;
}

DataStream<TransactionSummary> aggregatedStream = transactionStream
    .keyBy(Transaction::getUserId)
    .timeWindow(Time.minutes(5))
    .aggregate(
        new AggregateFunction<Transaction, TransactionAccumulator, TransactionSummary>() {
            @Override
            public TransactionAccumulator createAccumulator() {
                return new TransactionAccumulator();
            }
            
            @Override
            public TransactionAccumulator add(Transaction transaction, TransactionAccumulator acc) {
                acc.totalAmount += transaction.getAmount();
                acc.count++;
                acc.startTime = Math.min(acc.startTime, transaction.getTimestamp());
                acc.endTime = Math.max(acc.endTime, transaction.getTimestamp());
                return acc;
            }
            
            @Override
            public TransactionSummary getResult(TransactionAccumulator acc) {
                return new TransactionSummary(
                    acc.totalAmount,
                    acc.count,
                    acc.totalAmount / acc.count,
                    acc.startTime,
                    acc.endTime
                );
            }
            
            @Override
            public TransactionAccumulator merge(TransactionAccumulator a, TransactionAccumulator b) {
                TransactionAccumulator merged = new TransactionAccumulator();
                merged.totalAmount = a.totalAmount + b.totalAmount;
                merged.count = a.count + b.count;
                merged.startTime = Math.min(a.startTime, b.startTime);
                merged.endTime = Math.max(a.endTime, b.endTime);
                return merged;
            }
        }
    );
```

#### ProcessWindowFunction
```java
DataStream<String> processedWindowStream = transactionStream
    .keyBy(Transaction::getUserId)
    .timeWindow(Time.minutes(5))
    .process(new ProcessWindowFunction<Transaction, String, String, TimeWindow>() {
        @Override
        public void process(String userId, Context context, 
                          Iterable<Transaction> transactions, 
                          Collector<String> out) throws Exception {
            
            int count = 0;
            double totalAmount = 0.0;
            
            // 遍历窗口中的所有元素
            for (Transaction transaction : transactions) {
                count++;
                totalAmount += transaction.getAmount();
            }
            
            // 获取窗口信息
            TimeWindow window = context.window();
            
            // 输出处理结果
            out.collect(String.format(
                "User: %s, Count: %d, Total: %.2f, Window: [%d - %d]",
                userId, count, totalAmount, window.getStart(), window.getEnd()
            ));
        }
    });
```

## 6. 自定义函数详解

### 6.1 Rich Functions

Rich Functions 提供了更多的生命周期方法和运行时上下文。

```java
public class RichMapFunctionExample extends RichMapFunction<Transaction, EnrichedTransaction> {
    private transient Counter transactionCounter;
    private transient ValueState<Double> userTotalState;
    
    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);
        
        // 初始化计数器
        transactionCounter = getRuntimeContext()
            .getMetricGroup()
            .counter("transactionCount");
        
        // 初始化状态
        ValueStateDescriptor<Double> descriptor = new ValueStateDescriptor<>(
            "userTotal",  // 状态名称
            Types.DOUBLE   // 状态类型
        );
        userTotalState = getRuntimeContext().getState(descriptor);
    }
    
    @Override
    public EnrichedTransaction map(Transaction transaction) throws Exception {
        // 更新计数器
        transactionCounter.inc();
        
        // 获取并更新用户累计金额
        Double currentTotal = userTotalState.value();
        if (currentTotal == null) {
            currentTotal = 0.0;
        }
        double newTotal = currentTotal + transaction.getAmount();
        userTotalState.update(newTotal);
        
        // 返回增强的交易对象
        return new EnrichedTransaction(
            transaction.getUserId(),
            transaction.getProduct(),
            transaction.getAmount(),
            newTotal,  // 累计金额
            transaction.getTimestamp()
        );
    }
    
    @Override
    public void close() throws Exception {
        super.close();
        // 清理资源
    }
}
```

### 6.2 Process Functions

Process Functions 提供了最灵活的处理能力，可以访问定时器和状态。

```java
public class TransactionAlertFunction extends KeyedProcessFunction<String, Transaction, Alert> {
    private transient ValueState<Double> totalAmountState;
    private transient ValueState<Long> lastAlertTimeState;
    
    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);
        
        // 初始化状态
        ValueStateDescriptor<Double> totalDescriptor = new ValueStateDescriptor<>(
            "totalAmount", Types.DOUBLE);
        totalAmountState = getRuntimeContext().getState(totalDescriptor);
        
        ValueStateDescriptor<Long> timeDescriptor = new ValueStateDescriptor<>(
            "lastAlertTime", Types.LONG);
        lastAlertTimeState = getRuntimeContext().getState(timeDescriptor);
    }
    
    @Override
    public void processElement(Transaction transaction, Context ctx, Collector<Alert> out) 
            throws Exception {
        
        // 更新累计金额
        Double currentTotal = totalAmountState.value();
        if (currentTotal == null) {
            currentTotal = 0.0;
        }
        double newTotal = currentTotal + transaction.getAmount();
        totalAmountState.update(newTotal);
        
        // 检查是否需要发出警报
        if (newTotal > 10000.0) { // 阈值为10000
            Long lastAlertTime = lastAlertTimeState.value();
            long currentTime = ctx.timerService().currentProcessingTime();
            
            // 限制警报频率（每小时最多一次）
            if (lastAlertTime == null || currentTime - lastAlertTime > 3600000) {
                Alert alert = new Alert(
                    transaction.getUserId(),
                    newTotal,
                    "High transaction total detected",
                    currentTime
                );
                out.collect(alert);
                
                // 更新最后警报时间
                lastAlertTimeState.update(currentTime);
            }
        }
        
        // 设置定时器，在10分钟后检查累计金额
        long timerTime = ctx.timerService().currentProcessingTime() + 600000; // 10分钟后
        ctx.timerService().registerProcessingTimeTimer(timerTime);
    }
    
    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<Alert> out) 
            throws Exception {
        // 定时器触发时的处理逻辑
        Double totalAmount = totalAmountState.value();
        if (totalAmount != null && totalAmount > 0) {
            // 可以在这里执行一些清理或报告操作
            System.out.println("User " + ctx.getCurrentKey() + 
                             " total amount after 10 minutes: " + totalAmount);
        }
    }
}
```

## 7. 实例演示：电商实时监控系统

让我们通过一个完整的电商实时监控系统来理解 DataStream API 的应用：

### 7.1 系统需求

构建一个电商实时监控系统，需要实现：
1. 实时处理用户订单数据
2. 计算实时销售统计（总销售额、订单数、热门商品）
3. 检测异常订单（大额订单、高频订单）
4. 实时更新商品库存
5. 发送实时警报

### 7.2 代码实现

```java
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.util.Collector;

import java.util.Properties;

/**
 * 电商实时监控系统示例
 */
public class ECommerceMonitoringSystem {
    
    public static void main(String[] args) throws Exception {
        // 创建执行环境
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 配置执行环境
        env.setParallelism(4);
        env.enableCheckpointing(5000);
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        
        // 1. 从Kafka读取订单数据
        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", "localhost:9092");
        kafkaProps.setProperty("group.id", "ecommerce-monitor");
        
        FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
            "orders",
            new SimpleStringSchema(),
            kafkaProps
        );
        
        DataStream<String> orderDataStream = env.addSource(kafkaConsumer);
        
        // 2. 解析订单数据
        DataStream<Order> orderStream = orderDataStream
            .map(new OrderParser())
            .filter(new ValidOrderFilter());
        
        // 3. 分配时间戳和水印
        DataStream<Order> timedOrderStream = orderStream
            .assignTimestampsAndWatermarks(new OrderWatermarkGenerator());
        
        // 4. 计算实时销售统计（每5分钟窗口）
        DataStream<SalesSummary> salesSummaryStream = timedOrderStream
            .keyBy(order -> "ALL") // 全局统计
            .timeWindow(Time.minutes(5))
            .aggregate(
                new SalesAggregateFunction(),
                new SalesWindowFunction()
            );
        
        // 5. 计算热门商品（每10分钟窗口）
        DataStream<PopularProduct> popularProductStream = timedOrderStream
            .keyBy(Order::getProductId)
            .timeWindow(Time.minutes(10))
            .aggregate(
                new PopularProductAggregateFunction(),
                new PopularProductWindowFunction()
            );
        
        // 6. 检测异常订单
        DataStream<Alert> anomalyAlertStream = timedOrderStream
            .keyBy(Order::getUserId)
            .process(new AnomalyDetectionFunction());
        
        // 7. 实时库存更新
        DataStream<InventoryUpdate> inventoryStream = timedOrderStream
            .keyBy(Order::getProductId)
            .map(new InventoryUpdateFunction());
        
        // 8. 输出结果
        salesSummaryStream.print("Sales Summary: ");
        popularProductStream.print("Popular Products: ");
        anomalyAlertStream.print("Anomaly Alerts: ");
        inventoryStream.print("Inventory Updates: ");
        
        // 执行程序
        env.execute("E-Commerce Monitoring System");
    }
    
    /**
     * 订单解析函数
     */
    public static class OrderParser implements MapFunction<String, Order> {
        @Override
        public Order map(String value) throws Exception {
            // 假设订单数据格式为: orderId,userId,productId,quantity,price,timestamp
            String[] parts = value.split(",");
            if (parts.length == 6) {
                return new Order(
                    parts[0],                           // orderId
                    parts[1],                           // userId
                    parts[2],                           // productId
                    Integer.parseInt(parts[3]),         // quantity
                    Double.parseDouble(parts[4]),       // price
                    Long.parseLong(parts[5])            // timestamp
                );
            }
            return null;
        }
    }
    
    /**
     * 有效订单过滤器
     */
    public static class ValidOrderFilter implements FilterFunction<Order> {
        @Override
        public boolean filter(Order order) throws Exception {
            return order != null && 
                   order.getQuantity() > 0 && 
                   order.getPrice() > 0 &&
                   order.getTimestamp() > 0;
        }
    }
    
    /**
     * 销售统计聚合函数
     */
    public static class SalesAggregateFunction 
            implements AggregateFunction<Order, SalesAccumulator, SalesStatistics> {
        
        @Override
        public SalesAccumulator createAccumulator() {
            return new SalesAccumulator(0.0, 0, 0);
        }
        
        @Override
        public SalesAccumulator add(Order order, SalesAccumulator accumulator) {
            double orderAmount = order.getQuantity() * order.getPrice();
            return new SalesAccumulator(
                accumulator.totalAmount + orderAmount,
                accumulator.orderCount + 1,
                accumulator.productCount + order.getQuantity()
            );
        }
        
        @Override
        public SalesStatistics getResult(SalesAccumulator accumulator) {
            return new SalesStatistics(
                accumulator.totalAmount,
                accumulator.orderCount,
                accumulator.productCount,
                accumulator.orderCount > 0 ? 
                    accumulator.totalAmount / accumulator.orderCount : 0.0
            );
        }
        
        @Override
        public SalesAccumulator merge(SalesAccumulator a, SalesAccumulator b) {
            return new SalesAccumulator(
                a.totalAmount + b.totalAmount,
                a.orderCount + b.orderCount,
                a.productCount + b.productCount
            );
        }
    }
    
    /**
     * 销售统计窗口函数
     */
    public static class SalesWindowFunction 
            implements WindowFunction<SalesStatistics, SalesSummary, String, TimeWindow> {
        
        @Override
        public void apply(String key, TimeWindow window, 
                         Iterable<SalesStatistics> stats, 
                         Collector<SalesSummary> out) throws Exception {
            
            SalesStatistics stat = stats.iterator().next();
            out.collect(new SalesSummary(
                stat.totalAmount,
                stat.orderCount,
                stat.productCount,
                stat.averageOrderValue,
                window.getStart(),
                window.getEnd()
            ));
        }
    }
    
    /**
     * 热门商品聚合函数
     */
    public static class PopularProductAggregateFunction 
            implements AggregateFunction<Order, Integer, Integer> {
        
        @Override
        public Integer createAccumulator() {
            return 0;
        }
        
        @Override
        public Integer add(Order order, Integer accumulator) {
            return accumulator + order.getQuantity();
        }
        
        @Override
        public Integer getResult(Integer accumulator) {
            return accumulator;
        }
        
        @Override
        public Integer merge(Integer a, Integer b) {
            return a + b;
        }
    }
    
    /**
     * 热门商品窗口函数
     */
    public static class PopularProductWindowFunction 
            implements WindowFunction<Integer, PopularProduct, String, TimeWindow> {
        
        @Override
        public void apply(String productId, TimeWindow window, 
                         Iterable<Integer> quantities, 
                         Collector<PopularProduct> out) throws Exception {
            
            int totalQuantity = quantities.iterator().next();
            out.collect(new PopularProduct(
                productId,
                totalQuantity,
                window.getStart(),
                window.getEnd()
            ));
        }
    }
    
    /**
     * 异常检测函数
     */
    public static class AnomalyDetectionFunction 
            extends KeyedProcessFunction<String, Order, Alert> {
        
        private transient ValueState<OrderStatistics> userStatsState;
        
        @Override
        public void open(Configuration parameters) throws Exception {
            super.open(parameters);
            
            ValueStateDescriptor<OrderStatistics> descriptor = 
                new ValueStateDescriptor<>("userStats", OrderStatistics.class);
            userStatsState = getRuntimeContext().getState(descriptor);
        }
        
        @Override
        public void processElement(Order order, Context ctx, Collector<Alert> out) 
                throws Exception {
            
            OrderStatistics stats = userStatsState.value();
            if (stats == null) {
                stats = new OrderStatistics(0.0, 0, System.currentTimeMillis());
            }
            
            // 更新用户统计信息
            double orderAmount = order.getQuantity() * order.getPrice();
            stats.totalAmount += orderAmount;
            stats.orderCount++;
            
            userStatsState.update(stats);
            
            // 检测大额订单
            if (orderAmount > 5000.0) {
                out.collect(new Alert(
                    "HIGH_VALUE_ORDER",
                    order.getUserId(),
                    "High value order detected: " + orderAmount,
                    order.getTimestamp()
                ));
            }
            
            // 检测高频订单（1小时内超过10个订单）
            long timeWindow = 3600000; // 1小时
            if (order.getTimestamp() - stats.firstOrderTime < timeWindow && 
                stats.orderCount > 10) {
                out.collect(new Alert(
                    "HIGH_FREQUENCY_ORDER",
                    order.getUserId(),
                    "High frequency order detected: " + stats.orderCount + " orders",
                    order.getTimestamp()
                ));
            }
        }
    }
    
    /**
     * 库存更新函数
     */
    public static class InventoryUpdateFunction 
            extends RichMapFunction<Order, InventoryUpdate> {
        
        private transient ValueState<Integer> inventoryState;
        
        @Override
        public void open(Configuration parameters) throws Exception {
            super.open(parameters);
            
            ValueStateDescriptor<Integer> descriptor = 
                new ValueStateDescriptor<>("inventory", Types.INT);
            inventoryState = getRuntimeContext().getState(descriptor);
        }
        
        @Override
        public InventoryUpdate map(Order order) throws Exception {
            Integer currentInventory = inventoryState.value();
            if (currentInventory == null) {
                currentInventory = 1000; // 假设初始库存为1000
            }
            
            int newInventory = currentInventory - order.getQuantity();
            inventoryState.update(newInventory);
            
            return new InventoryUpdate(
                order.getProductId(),
                currentInventory,
                newInventory,
                order.getOrderId()
            );
        }
    }
}

// 数据类定义
class Order {
    private String orderId;
    private String userId;
    private String productId;
    private int quantity;
    private double price;
    private long timestamp;
    
    public Order() {} // 无参构造函数
    
    public Order(String orderId, String userId, String productId, 
                 int quantity, double price, long timestamp) {
        this.orderId = orderId;
        this.userId = userId;
        this.productId = productId;
        this.quantity = quantity;
        this.price = price;
        this.timestamp = timestamp;
    }
    
    // Getter和Setter方法
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }
    
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    
    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}

class SalesAccumulator {
    public double totalAmount;
    public int orderCount;
    public int productCount;
    
    public SalesAccumulator(double totalAmount, int orderCount, int productCount) {
        this.totalAmount = totalAmount;
        this.orderCount = orderCount;
        this.productCount = productCount;
    }
}

class SalesStatistics {
    public double totalAmount;
    public int orderCount;
    public int productCount;
    public double averageOrderValue;
    
    public SalesStatistics(double totalAmount, int orderCount, 
                          int productCount, double averageOrderValue) {
        this.totalAmount = totalAmount;
        this.orderCount = orderCount;
        this.productCount = productCount;
        this.averageOrderValue = averageOrderValue;
    }
}

class SalesSummary {
    private double totalAmount;
    private int orderCount;
    private int productCount;
    private double averageOrderValue;
    private long windowStart;
    private long windowEnd;
    
    public SalesSummary(double totalAmount, int orderCount, int productCount,
                       double averageOrderValue, long windowStart, long windowEnd) {
        this.totalAmount = totalAmount;
        this.orderCount = orderCount;
        this.productCount = productCount;
        this.averageOrderValue = averageOrderValue;
        this.windowStart = windowStart;
        this.windowEnd = windowEnd;
    }
    
    @Override
    public String toString() {
        return String.format(
            "SalesSummary{totalAmount=%.2f, orders=%d, products=%d, avgOrder=%.2f, window=[%d-%d]}",
            totalAmount, orderCount, productCount, averageOrderValue, windowStart, windowEnd
        );
    }
}

class PopularProduct {
    private String productId;
    private int totalQuantity;
    private long windowStart;
    private long windowEnd;
    
    public PopularProduct(String productId, int totalQuantity, long windowStart, long windowEnd) {
        this.productId = productId;
        this.totalQuantity = totalQuantity;
        this.windowStart = windowStart;
        this.windowEnd = windowEnd;
    }
    
    @Override
    public String toString() {
        return String.format(
            "PopularProduct{productId='%s', quantity=%d, window=[%d-%d]}",
            productId, totalQuantity, windowStart, windowEnd
        );
    }
}

class Alert {
    private String type;
    private String userId;
    private String message;
    private long timestamp;
    
    public Alert(String type, String userId, String message, long timestamp) {
        this.type = type;
        this.userId = userId;
        this.message = message;
        this.timestamp = timestamp;
    }
    
    @Override
    public String toString() {
        return String.format(
            "Alert{type='%s', userId='%s', message='%s', timestamp=%d}",
            type, userId, message, timestamp
        );
    }
}

class OrderStatistics {
    public double totalAmount;
    public int orderCount;
    public long firstOrderTime;
    
    public OrderStatistics(double totalAmount, int orderCount, long firstOrderTime) {
        this.totalAmount = totalAmount;
        this.orderCount = orderCount;
        this.firstOrderTime = firstOrderTime;
    }
}

class InventoryUpdate {
    private String productId;
    private int oldInventory;
    private int newInventory;
    private String orderId;
    
    public InventoryUpdate(String productId, int oldInventory, int newInventory, String orderId) {
        this.productId = productId;
        this.oldInventory = oldInventory;
        this.newInventory = newInventory;
        this.orderId = orderId;
    }
    
    @Override
    public String toString() {
        return String.format(
            "InventoryUpdate{productId='%s', old=%d, new=%d, orderId='%s'}",
            productId, oldInventory, newInventory, orderId
        );
    }
}

class OrderWatermarkGenerator implements AssignerWithPeriodicWatermarks<Order> {
    private long maxTimestamp = 0;
    private final long maxOutOfOrderness = 5000; // 5秒
    
    @Nullable
    @Override
    public Watermark getCurrentWatermark() {
        return new Watermark(maxTimestamp - maxOutOfOrderness - 1);
    }
    
    @Override
    public long extractTimestamp(Order order, long previousElementTimestamp) {
        long timestamp = order.getTimestamp();
        maxTimestamp = Math.max(maxTimestamp, timestamp);
        return timestamp;
    }
}
```

## 8. 本章小结

通过本章的学习，你应该已经深入理解了：

1. **DataStream API 核心概念**：数据流的基本特性、流处理与批处理的区别
2. **数据流创建方法**：从文件、Socket、集合和自定义数据源创建数据流
3. **转换操作详解**：基本转换、聚合转换和多流转换的详细用法和应用场景
4. **时间处理机制**：事件时间、处理时间和摄取时间的概念及水印机制
5. **窗口操作**：滚动窗口、滑动窗口和会话窗口的使用方法及窗口函数
6. **自定义函数**：Rich Functions 和 Process Functions 的使用场景和实现方法
7. **实际应用**：通过电商监控系统的例子理解 DataStream API 的综合应用

## 9. 下一步学习

掌握了 DataStream API 后，建议继续学习：
- [Flink 状态管理](../day05-state-management/state-management.md) - 深入学习 Flink 的状态管理和容错机制

## 10. 参考资源

- [Apache Flink 官方文档 - DataStream API](https://flink.apache.org/docs/stable/dev/datastream_api.html)
- [Flink 窗口操作文档](https://flink.apache.org/docs/stable/dev/stream/operators/windows.html)
- [Flink 时间处理文档](https://flink.apache.org/docs/stable/dev/event_time.html)
- [Flink Process Functions 文档](https://flink.apache.org/docs/stable/dev/stream/operators/process_function.html)
