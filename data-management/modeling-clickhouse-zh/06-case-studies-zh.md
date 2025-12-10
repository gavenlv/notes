# 6. 实际案例与代码示例

## 6.1 电商用户行为分析案例

### 6.1.1 业务场景
- **数据源**: 用户行为日志（Kafka）、订单数据（MySQL）
- **实时性要求**: 用户行为实时分析，订单数据准实时
- **分析需求**: 用户漏斗分析、实时推荐、业务监控

### 6.1.2 架构设计

```
数据源层:
  - Kafka (用户行为日志)
  - MySQL (订单数据)
    ↓
ETL层:
  - Flink (实时数据处理)
  - BigQuery (批量数据处理)
    ↓
分析数据库层:
  - ClickHouse (实时分析查询)
    ↓
应用层:
  - BI工具 (Tableau/Superset)
  - 实时推荐系统
```

### 6.1.3 代码实现

#### Flink实时ETL作业
```java
// 用户行为实时处理
public class UserBehaviorETL {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Kafka数据源
        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");
        
        DataStream<UserEvent> userEvents = env
            .addSource(new FlinkKafkaConsumer<>("user_events", 
                new JSONDeserializationSchema(), properties))
            .map(new UserEventParser())
            .filter(new DataValidator());
        
        // 实时用户行为聚合
        DataStream<UserBehaviorAggregate> aggregates = userEvents
            .keyBy(UserEvent::getUserId)
            .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
            .aggregate(new UserBehaviorAggregator());
        
        // 写入ClickHouse
        aggregates.addSink(new ClickHouseSink());
        
        env.execute("User Behavior Real-time ETL");
    }
}

// 用户行为聚合器
public class UserBehaviorAggregator implements AggregateFunction<UserEvent, 
    UserBehaviorState, UserBehaviorAggregate> {
    
    @Override
    public UserBehaviorState createAccumulator() {
        return new UserBehaviorState();
    }
    
    @Override
    public UserBehaviorState add(UserEvent event, UserBehaviorState accumulator) {
        accumulator.addEvent(event);
        return accumulator;
    }
    
    @Override
    public UserBehaviorAggregate getResult(UserBehaviorState accumulator) {
        return accumulator.getAggregate();
    }
    
    @Override
    public UserBehaviorState merge(UserBehaviorState a, UserBehaviorState b) {
        return a.merge(b);
    }
}
```

#### ClickHouse表设计
```sql
-- 用户行为表
CREATE TABLE user_events (
    event_date Date,
    event_timestamp DateTime64(3),
    user_id UInt64,
    session_id String,
    event_type LowCardinality(String),
    page_url String,
    product_id UInt64,
    amount Nullable(Decimal(10,2)),
    device_type LowCardinality(String),
    country LowCardinality(String),
    ip String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type, event_timestamp)
SETTINGS index_granularity = 8192;

-- 用户行为物化视图
CREATE MATERIALIZED VIEW user_daily_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type)
AS SELECT
    event_date,
    user_id,
    event_type,
    count() as event_count,
    sum(amount) as total_amount
FROM user_events
GROUP BY event_date, user_id, event_type;
```

#### 用户漏斗分析查询
```sql
-- 用户转化漏斗分析
WITH funnel_data AS (
    SELECT
        user_id,
        minIf(event_timestamp, event_type = 'page_view') as view_time,
        minIf(event_timestamp, event_type = 'add_to_cart') as cart_time,
        minIf(event_timestamp, event_type = 'checkout_start') as checkout_time,
        minIf(event_timestamp, event_type = 'purchase') as purchase_time
    FROM user_events
    WHERE event_date >= '2024-01-01'
    GROUP BY user_id
)
SELECT
    'Page View' as step,
    countIf(view_time IS NOT NULL) as user_count,
    100.0 as conversion_rate
FROM funnel_data

UNION ALL

SELECT
    'Add to Cart' as step,
    countIf(cart_time IS NOT NULL AND cart_time > view_time) as user_count,
    round(countIf(cart_time IS NOT NULL AND cart_time > view_time) * 100.0 / 
          countIf(view_time IS NOT NULL), 2) as conversion_rate
FROM funnel_data

UNION ALL

SELECT
    'Checkout' as step,
    countIf(checkout_time IS NOT NULL AND checkout_time > cart_time) as user_count,
    round(countIf(checkout_time IS NOT NULL AND checkout_time > cart_time) * 100.0 / 
          countIf(cart_time IS NOT NULL AND cart_time > view_time), 2) as conversion_rate
FROM funnel_data

UNION ALL

SELECT
    'Purchase' as step,
    countIf(purchase_time IS NOT NULL AND purchase_time > checkout_time) as user_count,
    round(countIf(purchase_time IS NOT NULL AND purchase_time > checkout_time) * 100.0 / 
          countIf(checkout_time IS NOT NULL AND checkout_time > cart_time), 2) as conversion_rate
FROM funnel_data
ORDER BY 
    CASE step 
        WHEN 'Page View' THEN 1
        WHEN 'Add to Cart' THEN 2
        WHEN 'Checkout' THEN 3
        WHEN 'Purchase' THEN 4
    END;
```

## 6.2 物联网设备监控案例

### 6.2.1 业务场景
- **数据源**: 设备传感器数据（MQTT）、设备状态数据（API）
- **实时性要求**: 设备状态实时监控，异常检测
- **分析需求**: 设备健康度分析、预测性维护

### 6.2.2 架构设计

```
数据源层:
  - MQTT Broker (传感器数据)
  - REST API (设备状态)
    ↓
ETL层:
  - Flink (流式数据处理)
  - BigQuery (历史数据分析)
    ↓
分析数据库层:
  - ClickHouse (时序数据分析)
    ↓
应用层:
  - 监控仪表板
  - 告警系统
```

### 6.2.3 代码实现

#### Flink设备数据处理
```java
// 设备传感器数据处理
public class IoTDeviceETL {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // MQTT数据源
        DataStream<SensorData> sensorData = env
            .addSource(new MQTTSource("tcp://mqtt-broker:1883", "sensors/#"))
            .map(new SensorDataParser())
            .filter(new SensorDataValidator());
        
        // 设备状态异常检测
        DataStream<DeviceAlert> alerts = sensorData
            .keyBy(SensorData::getDeviceId)
            .process(new DeviceAnomalyDetector());
        
        // 设备状态聚合
        DataStream<DeviceStatus> statusAggregates = sensorData
            .keyBy(SensorData::getDeviceId)
            .window(SlidingProcessingTimeWindows.of(Time.minutes(10), Time.minutes(1)))
            .aggregate(new DeviceStatusAggregator());
        
        // 写入ClickHouse
        statusAggregates.addSink(new ClickHouseSink());
        alerts.addSink(new AlertSink());
        
        env.execute("IoT Device Monitoring ETL");
    }
}

// 设备异常检测器
public class DeviceAnomalyDetector extends 
    KeyedProcessFunction<String, SensorData, DeviceAlert> {
    
    private transient ValueState<DeviceStats> deviceStatsState;
    
    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<DeviceStats> descriptor = 
            new ValueStateDescriptor<>("device-stats", DeviceStats.class);
        deviceStatsState = getRuntimeContext().getState(descriptor);
    }
    
    @Override
    public void processElement(SensorData data, Context ctx, 
                              Collector<DeviceAlert> out) throws Exception {
        
        DeviceStats stats = deviceStatsState.value();
        if (stats == null) {
            stats = new DeviceStats();
        }
        
        // 检测异常
        if (stats.isAnomaly(data)) {
            out.collect(new DeviceAlert(data.getDeviceId(), data.getTimestamp(), 
                "Anomaly detected", data.getValue()));
        }
        
        stats.update(data);
        deviceStatsState.update(stats);
    }
}
```

#### ClickHouse时序数据表设计
```sql
-- 设备传感器数据表
CREATE TABLE device_sensor_data (
    device_id UInt64,
    timestamp DateTime64(3),
    sensor_type LowCardinality(String),
    value Float64,
    unit LowCardinality(String),
    status LowCardinality(String),
    location String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (device_id, sensor_type, timestamp)
SETTINGS index_granularity = 8192;

-- 设备状态汇总表
CREATE MATERIALIZED VIEW device_daily_stats
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (device_id, sensor_type, toDate(timestamp))
AS SELECT
    device_id,
    sensor_type,
    toDate(timestamp) as date,
    countState() as count_state,
    avgState(value) as avg_value_state,
    minState(value) as min_value_state,
    maxState(value) as max_value_state,
    sumState(value) as sum_value_state
FROM device_sensor_data
GROUP BY device_id, sensor_type, toDate(timestamp);
```

#### 设备健康度分析查询
```sql
-- 设备健康度评分
WITH device_stats AS (
    SELECT
        device_id,
        sensor_type,
        countMerge(count_state) as data_points,
        avgMerge(avg_value_state) as avg_value,
        minMerge(min_value_state) as min_value,
        maxMerge(max_value_state) as max_value,
        (maxMerge(max_value_state) - minMerge(min_value_state)) as value_range
    FROM device_daily_stats
    WHERE date >= today() - 30
    GROUP BY device_id, sensor_type
),
device_health AS (
    SELECT
        device_id,
        -- 计算健康度评分（0-100）
        round(
            CASE 
                WHEN data_points < 100 THEN 0  -- 数据点不足
                WHEN value_range > (avg_value * 2) THEN 20  -- 波动过大
                WHEN avg_value < expected_min THEN 30  -- 低于预期最小值
                WHEN avg_value > expected_max THEN 40  -- 高于预期最大值
                ELSE 80 + (20 * (1 - (value_range / avg_value)))  -- 基于稳定性评分
            END, 2
        ) as health_score
    FROM device_stats
    JOIN device_expected_ranges USING (device_id, sensor_type)
)
SELECT
    device_id,
    health_score,
    CASE
        WHEN health_score >= 90 THEN 'Excellent'
        WHEN health_score >= 70 THEN 'Good'
        WHEN health_score >= 50 THEN 'Fair'
        ELSE 'Poor'
    END as health_status
FROM device_health
ORDER BY health_score DESC;
```

## 6.3 金融交易风控案例

### 6.3.1 业务场景
- **数据源**: 交易流水（Kafka）、用户信息（MySQL）、黑名单（API）
- **实时性要求**: 交易实时风控，毫秒级响应
- **分析需求**: 欺诈检测、交易模式分析、合规报告

### 6.3.2 架构设计

```
数据源层:
  - Kafka (交易流水)
  - MySQL (用户信息)
  - REST API (黑名单)
    ↓
ETL层:
  - Flink (实时风控处理)
  - BigQuery (批量合规分析)
    ↓
分析数据库层:
  - ClickHouse (交易分析查询)
    ↓
应用层:
  - 风控决策引擎
  - 合规报告系统
```

### 6.3.3 代码实现

#### Flink实时风控处理
```java
// 交易风控实时处理
public class TransactionRiskETL {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 交易数据源
        DataStream<Transaction> transactions = env
            .addSource(new KafkaSource<>("transactions"))
            .map(new TransactionParser())
            .filter(new TransactionValidator());
        
        // 实时风控规则处理
        DataStream<RiskAssessment> riskAssessments = transactions
            .keyBy(Transaction::getUserId)
            .process(new RiskRuleEngine());
        
        // 交易模式分析
        DataStream<TransactionPattern> patterns = transactions
            .keyBy(Transaction::getUserId)
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .aggregate(new TransactionPatternAggregator());
        
        // 写入ClickHouse
        riskAssessments.addSink(new ClickHouseSink());
        patterns.addSink(new ClickHouseSink());
        
        env.execute("Transaction Risk Real-time ETL");
    }
}

// 风控规则引擎
public class RiskRuleEngine extends 
    KeyedProcessFunction<Long, Transaction, RiskAssessment> {
    
    private transient ValueState<UserBehaviorProfile> userProfileState;
    private transient MapState<String, Boolean> blacklistState;
    
    @Override
    public void open(Configuration parameters) {
        // 初始化状态
        ValueStateDescriptor<UserBehaviorProfile> profileDescriptor = 
            new ValueStateDescriptor<>("user-profile", UserBehaviorProfile.class);
        userProfileState = getRuntimeContext().getState(profileDescriptor);
        
        MapStateDescriptor<String, Boolean> blacklistDescriptor = 
            new MapStateDescriptor<>("blacklist", String.class, Boolean.class);
        blacklistState = getRuntimeContext().getMapState(blacklistDescriptor);
    }
    
    @Override
    public void processElement(Transaction transaction, Context ctx, 
                              Collector<RiskAssessment> out) throws Exception {
        
        // 检查黑名单
        if (blacklistState.contains(transaction.getAccountNumber())) {
            out.collect(new RiskAssessment(transaction, "BLACKLISTED", 100));
            return;
        }
        
        // 获取用户行为画像
        UserBehaviorProfile profile = userProfileState.value();
        if (profile == null) {
            profile = new UserBehaviorProfile(transaction.getUserId());
        }
        
        // 应用风控规则
        int riskScore = calculateRiskScore(transaction, profile);
        String riskLevel = getRiskLevel(riskScore);
        
        out.collect(new RiskAssessment(transaction, riskLevel, riskScore));
        
        // 更新用户画像
        profile.update(transaction);
        userProfileState.update(profile);
    }
    
    private int calculateRiskScore(Transaction transaction, UserBehaviorProfile profile) {
        int score = 0;
        
        // 规则1: 交易金额异常
        if (transaction.getAmount() > profile.getAvgAmount() * 3) {
            score += 30;
        }
        
        // 规则2: 交易频率异常
        if (profile.getRecentTransactionCount() > 10) {
            score += 20;
        }
        
        // 规则3: 地理位置异常
        if (!profile.isNormalLocation(transaction.getLocation())) {
            score += 25;
        }
        
        // 规则4: 交易时间异常
        if (!profile.isNormalTime(transaction.getTimestamp())) {
            score += 15;
        }
        
        // 规则5: 收款方风险
        if (isRiskyRecipient(transaction.getRecipient())) {
            score += 10;
        }
        
        return Math.min(score, 100);
    }
}
```

## 6.4 总结

通过以上三个实际案例，我们可以看到在不同业务场景下，ETL层与ClickHouse层的职责划分如何根据具体需求进行调整。关键是要根据数据特性、实时性要求和分析复杂度来合理分配扫描逻辑，充分发挥各技术组件的优势。