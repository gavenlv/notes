/*
 * Flink Iceberg 与 Kafka 集成示例
 * 
 * 本示例演示如何在 Flink 中消费 Kafka 数据并写入 Iceberg 表。
 */

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.types.Row;

public class FlinkIcebergKafkaIntegration {

    public static void main(String[] args) throws Exception {
        // 1. 创建 Flink 执行环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(30000); // 30秒检查点间隔
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        System.out.println("=== Flink Iceberg 与 Kafka 集成示例 ===");
        
        // 2. 配置 Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 创建用于 Kafka 数据接收的 Iceberg 表
        createKafkaConsumerTables(tableEnv);

        // 4. 配置 Kafka Source 并消费数据写入 Iceberg
        setupKafkaConsumer(tableEnv, env);

        // 5. 查询写入的数据
        queryKafkaData(tableEnv);

        // 6. 查看表的元数据
        showTableMetadata(tableEnv);

        // 7. 清理资源
        // 注意：在实际流式应用中，我们不会立即清理资源
        // 这里仅为了演示目的在最后清理
        // cleanup(tableEnv);

        System.out.println("Flink Iceberg 与 Kafka 集成示例完成!");
        System.out.println("注意：这是一个持续运行的流式作业，按 Ctrl+C 停止");
        
        // 执行流式作业
        // env.execute("Flink Iceberg Kafka Integration Job");
    }

    private static void configureIcebergCatalog(StreamTableEnvironment tableEnv) {
        System.out.println("配置 Iceberg Catalog...");
        
        // 配置 Iceberg Catalog
        tableEnv.executeSql("CREATE CATALOG iceberg_catalog WITH (" +
                "'type'='iceberg'," +
                "'catalog-type'='hadoop'," +
                "'warehouse'='hdfs://localhost:9000/iceberg/warehouse'" +
                ")");
        
        tableEnv.executeSql("USE CATALOG iceberg_catalog");
    }

    private static void createKafkaConsumerTables(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("创建用于 Kafka 数据接收的 Iceberg 表...");
        
        // 创建用户行为事件表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.user_behavior_events (" +
                "user_id BIGINT," +
                "event_type STRING," +
                "product_id STRING," +
                "timestamp TIMESTAMP(3)," +
                "session_id STRING," +
                "processed_at TIMESTAMP(3) METADATA FROM 'timestamp'" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='134217728'," + // 128MB
                "'write.parquet.compression-codec'='zstd'," +
                "'write.distribution-mode'='hash'," +
                "'format-version'='2'" +
                ")");
        
        // 创建实时指标聚合表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.realtime_metrics (" +
                "window_start TIMESTAMP(3)," +
                "window_end TIMESTAMP(3)," +
                "event_type STRING," +
                "count BIGINT," +
                "unique_users BIGINT" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='67108864'," + // 64MB
                "'write.parquet.compression-codec'='snappy'" +
                ")");
    }

    private static void setupKafkaConsumer(StreamTableEnvironment tableEnv, StreamExecutionEnvironment env) throws Exception {
        System.out.println("配置 Kafka Source 并消费数据...");
        
        // 方法1: 使用 SQL DDL 创建 Kafka 表
        System.out.println("方法1: 使用 SQL DDL 创建 Kafka 表");
        
        tableEnv.executeSql("CREATE TABLE kafka_user_events (" +
                "user_id BIGINT," +
                "event_type STRING," +
                "product_id STRING," +
                "timestamp TIMESTAMP(3)," +
                "session_id STRING," +
                " WATERMARK FOR timestamp AS timestamp - INTERVAL '5' SECOND" +
                ") WITH (" +
                "  'connector' = 'kafka'," +
                "  'topic' = 'user-events'," +
                "  'properties.bootstrap.servers' = 'localhost:9092'," +
                "  'properties.group.id' = 'iceberg-consumer-group'," +
                "  'scan.startup.mode' = 'earliest-offset'," +
                "  'format' = 'json'" +
                ")");
        
        // 将 Kafka 数据写入 Iceberg 表
        tableEnv.executeSql(
            "INSERT INTO default.user_behavior_events " +
            "SELECT *, CURRENT_TIMESTAMP FROM kafka_user_events"
        );
        
        // 方法2: 使用DataStream API创建Kafka消费者
        System.out.println("方法2: 使用DataStream API创建Kafka消费者");
        
        KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
                .setBootstrapServers("localhost:9092")
                .setTopics("user-metrics")
                .setGroupId("iceberg-metrics-group")
                .setStartingOffsets(OffsetsInitializer.earliest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();
        
        DataStream<String> kafkaStream = env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "Kafka Source");
        
        // 将DataStream注册为临时表
        tableEnv.createTemporaryView("kafka_metrics_stream", kafkaStream);
        
        // 处理并写入聚合数据到Iceberg
        tableEnv.executeSql(
            "INSERT INTO default.realtime_metrics " +
            "SELECT " +
            "  TUMBLE_START(timestamp, INTERVAL '1' MINUTE) as window_start, " +
            "  TUMBLE_END(timestamp, INTERVAL '1' MINUTE) as window_end, " +
            "  event_type, " +
            "  COUNT(*) as count, " +
            "  COUNT(DISTINCT user_id) as unique_users " +
            "FROM kafka_metrics_stream " +
            "GROUP BY TUMBLE(timestamp, INTERVAL '1' MINUTE), event_type"
        );
        
        System.out.println("Kafka消费者配置完成，开始消费数据...");
    }

    private static void queryKafkaData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("查询从Kafka消费并写入的数据...");
        
        System.out.println("用户行为事件表数据:");
        TableResult eventsResult = tableEnv.executeSql("SELECT * FROM default.user_behavior_events ORDER BY timestamp DESC LIMIT 10");
        eventsResult.print();
        
        System.out.println("实时指标聚合表数据:");
        TableResult metricsResult = tableEnv.executeSql("SELECT * FROM default.realtime_metrics ORDER BY window_end DESC LIMIT 10");
        metricsResult.print();
    }

    private static void showTableMetadata(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("查看表的元数据信息...");
        
        System.out.println("用户行为事件表的文件信息:");
        TableResult filesResult = tableEnv.executeSql(
            "SELECT " +
            "  COUNT(*) as file_count, " +
            "  SUM(file_size_in_bytes)/1024/1024 as total_size_mb " +
            "FROM default.user_behavior_events.files"
        );
        filesResult.print();
        
        System.out.println("用户行为事件表的分区信息:");
        TableResult partitionsResult = tableEnv.executeSql("SELECT * FROM default.user_behavior_events.partitions");
        partitionsResult.print();
    }

    private static void cleanup(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("清理测试表...");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.user_behavior_events");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.realtime_metrics");
        tableEnv.executeSql("DROP TABLE IF EXISTS kafka_user_events");
    }
}