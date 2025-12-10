# 6. Case Studies & Code Examples

## 6.1 E-commerce User Behavior Analysis Case Study

### 6.1.1 Business Scenario
- **Data Sources**: User behavior logs (Kafka), order data (MySQL)
- **Real-time Requirements**: Real-time user behavior analysis, near real-time order data
- **Analysis Needs**: User funnel analysis, real-time recommendations, business monitoring

### 6.1.2 Architecture Design

```
Data Sources Layer:
  - Kafka (User behavior logs)
  - MySQL (Order data)
    ↓
ETL Layer:
  - Flink (Real-time data processing)
  - BigQuery (Batch data processing)
    ↓
Analytical Database Layer:
  - ClickHouse (Real-time analytical queries)
    ↓
Application Layer:
  - BI Tools (Tableau/Superset)
  - Real-time recommendation system
```

### 6.1.3 Code Implementation

#### Flink Real-time ETL Job
```java
// User behavior real-time processing
public class UserBehaviorETL {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Kafka data source
        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");
        
        DataStream<UserEvent> userEvents = env
            .addSource(new FlinkKafkaConsumer<>("user_events", 
                new JSONDeserializationSchema(), properties))
            .map(new UserEventParser())
            .filter(new DataValidator());
        
        // Real-time user behavior aggregation
        DataStream<UserBehaviorAggregate> aggregates = userEvents
            .keyBy(UserEvent::getUserId)
            .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
            .aggregate(new UserBehaviorAggregator());
        
        // Write to ClickHouse
        aggregates.addSink(new ClickHouseSink());
        
        env.execute("User Behavior Real-time ETL");
    }
}

// User behavior aggregator
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

#### ClickHouse Table Design
```sql
-- User behavior table
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

-- User behavior materialized view
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

#### User Funnel Analysis Query
```sql
-- User conversion funnel analysis
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

## 6.2 IoT Device Monitoring Case Study

### 6.2.1 Business Scenario
- **Data Sources**: Device sensor data (MQTT), device status data (API)
- **Real-time Requirements**: Real-time device status monitoring, anomaly detection
- **Analysis Needs**: Device health analysis, predictive maintenance

### 6.2.2 Architecture Design

```
Data Sources Layer:
  - MQTT Broker (Sensor data)
  - REST API (Device status)
    ↓
ETL Layer:
  - Flink (Stream data processing)
  - BigQuery (Historical data analysis)
    ↓
Analytical Database Layer:
  - ClickHouse (Time series data analysis)
    ↓
Application Layer:
  - Monitoring dashboard
  - Alerting system
```

### 6.2.3 Code Implementation

#### Flink Device Data Processing
```java
// Device sensor data processing
public class IoTDeviceETL {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // MQTT data source
        DataStream<SensorData> sensorData = env
            .addSource(new MQTTSource("tcp://mqtt-broker:1883", "sensors/#"))
            .map(new SensorDataParser())
            .filter(new SensorDataValidator());
        
        // Device status anomaly detection
        DataStream<DeviceAlert> alerts = sensorData
            .keyBy(SensorData::getDeviceId)
            .process(new DeviceAnomalyDetector());
        
        // Device status aggregation
        DataStream<DeviceStatus> statusAggregates = sensorData
            .keyBy(SensorData::getDeviceId)
            .window(SlidingProcessingTimeWindows.of(Time.minutes(10), Time.minutes(1)))
            .aggregate(new DeviceStatusAggregator());
        
        // Write to ClickHouse
        statusAggregates.addSink(new ClickHouseSink());
        alerts.addSink(new AlertSink());
        
        env.execute("IoT Device Monitoring ETL");
    }
}

// Device anomaly detector
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
        
        // Detect anomalies
        if (stats.isAnomaly(data)) {
            out.collect(new DeviceAlert(data.getDeviceId(), data.getTimestamp(), 
                "Anomaly detected", data.getValue()));
        }
        
        stats.update(data);
        deviceStatsState.update(stats);
    }
}
```

#### ClickHouse Time Series Table Design
```sql
-- Device sensor data table
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

-- Device status summary table
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

#### Device Health Analysis Query
```sql
-- Device health scoring
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
        -- Calculate health score (0-100)
        round(
            CASE 
                WHEN data_points < 100 THEN 0  -- Insufficient data points
                WHEN value_range > (avg_value * 2) THEN 20  -- Excessive fluctuation
                WHEN avg_value < expected_min THEN 30  -- Below expected minimum
                WHEN avg_value > expected_max THEN 40  -- Above expected maximum
                ELSE 80 + (20 * (1 - (value_range / avg_value)))  -- Based on stability score
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

## 6.3 Financial Transaction Risk Control Case Study

### 6.3.1 Business Scenario
- **Data Sources**: Transaction streams (Kafka), user information (MySQL), blacklists (API)
- **Real-time Requirements**: Real-time transaction risk control, millisecond response
- **Analysis Needs**: Fraud detection, transaction pattern analysis, compliance reporting

### 6.3.2 Architecture Design

```
Data Sources Layer:
  - Kafka (Transaction streams)
  - MySQL (User information)
  - REST API (Blacklists)
    ↓
ETL Layer:
  - Flink (Real-time risk control processing)
  - BigQuery (Batch compliance analysis)
    ↓
Analytical Database Layer:
  - ClickHouse (Transaction analysis queries)
    ↓
Application Layer:
  - Risk decision engine
  - Compliance reporting system
```

### 6.3.3 Code Implementation

#### Flink Real-time Risk Processing
```java
// Transaction risk real-time processing
public class TransactionRiskETL {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Transaction data source
        DataStream<Transaction> transactions = env
            .addSource(new KafkaSource<>("transactions"))
            .map(new TransactionParser())
            .filter(new TransactionValidator());
        
        // Real-time risk rule processing
        DataStream<RiskAssessment> riskAssessments = transactions
            .keyBy(Transaction::getUserId)
            .process(new RiskRuleEngine());
        
        // Transaction pattern analysis
        DataStream<TransactionPattern> patterns = transactions
            .keyBy(Transaction::getUserId)
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .aggregate(new TransactionPatternAggregator());
        
        // Write to ClickHouse
        riskAssessments.addSink(new ClickHouseSink());
        patterns.addSink(new ClickHouseSink());
        
        env.execute("Transaction Risk Real-time ETL");
    }
}

// Risk rule engine
public class RiskRuleEngine extends 
    KeyedProcessFunction<Long, Transaction, RiskAssessment> {
    
    private transient ValueState<UserBehaviorProfile> userProfileState;
    private transient MapState<String, Boolean> blacklistState;
    
    @Override
    public void open(Configuration parameters) {
        // Initialize state
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
        
        // Check blacklist
        if (blacklistState.contains(transaction.getAccountNumber())) {
            out.collect(new RiskAssessment(transaction, "BLACKLISTED", 100));
            return;
        }
        
        // Get user behavior profile
        UserBehaviorProfile profile = userProfileState.value();
        if (profile == null) {
            profile = new UserBehaviorProfile(transaction.getUserId());
        }
        
        // Apply risk rules
        int riskScore = calculateRiskScore(transaction, profile);
        String riskLevel = getRiskLevel(riskScore);
        
        out.collect(new RiskAssessment(transaction, riskLevel, riskScore));
        
        // Update user profile
        profile.update(transaction);
        userProfileState.update(profile);
    }
    
    private int calculateRiskScore(Transaction transaction, UserBehaviorProfile profile) {
        int score = 0;
        
        // Rule 1: Abnormal transaction amount
        if (transaction.getAmount() > profile.getAvgAmount() * 3) {
            score += 30;
        }
        
        // Rule 2: Abnormal transaction frequency
        if (profile.getRecentTransactionCount() > 10) {
            score += 20;
        }
        
        // Rule 3: Abnormal location
        if (!profile.isNormalLocation(transaction.getLocation())) {
            score += 25;
        }
        
        // Rule 4: Abnormal transaction time
        if (!profile.isNormalTime(transaction.getTimestamp())) {
            score += 15;
        }
        
        // Rule 5: Risky recipient
        if (isRiskyRecipient(transaction.getRecipient())) {
            score += 10;
        }
        
        return Math.min(score, 100);
    }
}
```

## 6.4 Summary

Through the above three case studies, we can see how the division of responsibilities between the ETL layer and the ClickHouse layer is adjusted according to specific requirements in different business scenarios. The key is to reasonably allocate scan logic based on data characteristics, real-time requirements, and analysis complexity to fully leverage the advantages of each technical component.