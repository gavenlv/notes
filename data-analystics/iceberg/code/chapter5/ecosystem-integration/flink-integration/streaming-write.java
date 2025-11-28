/*
 * Flink Iceberg 流式写入示例
 * 
 * 本示例演示如何在 Flink 中将流式数据写入 Iceberg 表。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringEncoder;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.connector.file.sink.FileSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.core.fs.Path;
import org.apache.flink.formats.json.JsonDeserializationSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.filesystem.rollingpolicies.DefaultRollingPolicy;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.types.Row;

import java.time.Duration;
import java.util.Arrays;
import java.util.List;

// 模拟事件数据类
class EventData {
    public String eventId;
    public Long userId;
    public String eventType;
    public String timestamp;
    public String payload;
    
    // 无参构造函数
    public EventData() {}
    
    // 有参构造函数
    public EventData(String eventId, Long userId, String eventType, String timestamp, String payload) {
        this.eventId = eventId;
        this.userId = userId;
        this.eventType = eventType;
        this.timestamp = timestamp;
        this.payload = payload;
    }
    
    @Override
    public String toString() {
        return "EventData{" +
                "eventId='" + eventId + '\'' +
                ", userId=" + userId +
                ", eventType='" + eventType + '\'' +
                ", timestamp='" + timestamp + '\'' +
                ", payload='" + payload + '\'' +
                '}';
    }
}

public class FlinkIcebergStreamingWrite {

    public static void main(String[] args) throws Exception {
        // 1. 创建 Flink 执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.STREAMING);
        env.enableCheckpointing(30000); // 30秒检查点间隔
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        System.out.println("=== Flink Iceberg 流式写入示例 ===");
        
        // 2. 配置 Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 创建用于流式写入的 Iceberg 表
        createStreamingTables(tableEnv);

        // 4. 模拟流式数据源并写入 Iceberg
        simulateStreamingWrite(tableEnv, env);

        // 5. 查询写入的数据
        queryStreamingData(tableEnv);

        // 6. 查看表的元数据
        showTableMetadata(tableEnv);

        // 7. 清理资源
        // 注意：在实际流式应用中，我们不会立即清理资源
        // 这里仅为了演示目的在最后清理
        // cleanup(tableEnv);

        System.out.println("Flink Iceberg 流式写入示例完成!");
        System.out.println("注意：这是一个持续运行的流式作业，按 Ctrl+C 停止");
        
        // 执行流式作业
        // env.execute("Flink Iceberg Streaming Write Job");
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

    private static void createStreamingTables(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("创建用于流式写入的 Iceberg 表...");
        
        // 创建事件日志表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.event_logs (" +
                "event_id STRING," +
                "user_id BIGINT," +
                "event_type STRING," +
                "event_timestamp TIMESTAMP(3)," +
                "payload STRING," +
                "processed_at TIMESTAMP(3) METADATA FROM 'timestamp'" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='134217728'," + // 128MB
                "'write.parquet.compression-codec'='zstd'," +
                "'write.distribution-mode'='hash'," +
                "'format-version'='2'" +
                ")");
        
        // 创建用户活动汇总表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.user_activity_summary (" +
                "user_id BIGINT," +
                "event_count BIGINT," +
                "last_event_time TIMESTAMP(3)," +
                "event_types ARRAY<STRING>" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='67108864'," + // 64MB
                "'write.parquet.compression-codec'='snappy'" +
                ")");
    }

    private static void simulateStreamingWrite(StreamTableEnvironment tableEnv, StreamExecutionEnvironment env) throws Exception {
        System.out.println("模拟流式数据写入...");
        
        // 方法1: 使用表API进行流式写入
        System.out.println("方法1: 使用表API进行流式写入");
        
        // 创建临时视图模拟流式数据
        tableEnv.executeSql("CREATE TEMPORARY VIEW event_stream AS " +
                "VALUES " +
                "('evt_001', 1001L, 'login', TIMESTAMP '2023-06-01 10:00:00', 'user login'), " +
                "('evt_002', 1002L, 'view', TIMESTAMP '2023-06-01 10:01:00', 'page view'), " +
                "('evt_003', 1001L, 'purchase', TIMESTAMP '2023-06-01 10:05:00', 'product purchase')");
        
        // 将流式数据写入 Iceberg 表
        tableEnv.executeSql(
            "INSERT INTO default.event_logs " +
            "SELECT *, CURRENT_TIMESTAMP FROM event_stream"
        );
        
        // 方法2: 使用DataStream API模拟更真实的流式场景
        System.out.println("方法2: 使用DataStream API模拟流式场景");
        
        // 模拟生成事件数据流
        DataStream<String> eventStream = env.fromCollection(Arrays.asList(
            "{\"eventId\":\"evt_004\",\"userId\":1003,\"eventType\":\"search\",\"timestamp\":\"2023-06-01T10:10:00\",\"payload\":\"search query\"}",
            "{\"eventId\":\"evt_005\",\"userId\":1004,\"eventType\":\"login\",\"timestamp\":\"2023-06-01T10:15:00\",\"payload\":\"user login\"}",
            "{\"eventId\":\"evt_006\",\"userId\":1003,\"eventType\":\"view\",\"timestamp\":\"2023-06-01T10:16:00\",\"payload\":\"product view\"}"
        ));
        
        // 解析JSON数据
        DataStream<EventData> parsedStream = eventStream.map(new MapFunction<String, EventData>() {
            @Override
            public EventData map(String value) throws Exception {
                // 简化的JSON解析，实际应用中应使用更健壮的解析器
                value = value.replace("{", "").replace("}", "").replace("\"", "");
                String[] pairs = value.split(",");
                EventData event = new EventData();
                for (String pair : pairs) {
                    String[] keyValue = pair.split(":");
                    switch (keyValue[0].trim()) {
                        case "eventId":
                            event.eventId = keyValue[1].trim();
                            break;
                        case "userId":
                            event.userId = Long.parseLong(keyValue[1].trim());
                            break;
                        case "eventType":
                            event.eventType = keyValue[1].trim();
                            break;
                        case "timestamp":
                            event.timestamp = keyValue[1].trim();
                            break;
                        case "payload":
                            event.payload = keyValue[1].trim();
                            break;
                    }
                }
                return event;
            }
        });
        
        // 将DataStream注册为临时表
        tableEnv.createTemporaryView("stream_events", parsedStream);
        
        // 将流式数据写入 Iceberg 表
        tableEnv.executeSql(
            "INSERT INTO default.event_logs " +
            "SELECT eventId, userId, eventType, TO_TIMESTAMP(timestamp), payload, CURRENT_TIMESTAMP FROM stream_events"
        );
        
        System.out.println("流式数据写入任务已提交");
    }

    private static void queryStreamingData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("查询流式写入的数据...");
        
        System.out.println("事件日志表数据:");
        TableResult eventLogsResult = tableEnv.executeSql("SELECT * FROM default.event_logs ORDER BY event_timestamp");
        eventLogsResult.print();
        
        // 创建用户活动汇总数据
        System.out.println("创建用户活动汇总...");
        tableEnv.executeSql(
            "INSERT INTO default.user_activity_summary " +
            "SELECT " +
            "  user_id, " +
            "  COUNT(*) as event_count, " +
            "  MAX(event_timestamp) as last_event_time, " +
            "  COLLECT_LIST(DISTINCT event_type) as event_types " +
            "FROM default.event_logs " +
            "GROUP BY user_id"
        );
        
        // 查询用户活动汇总
        Thread.sleep(5000); // 等待插入完成
        System.out.println("用户活动汇总数据:");
        TableResult summaryResult = tableEnv.executeSql("SELECT * FROM default.user_activity_summary ORDER BY event_count DESC");
        summaryResult.print();
    }

    private static void showTableMetadata(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("查看表的元数据信息...");
        
        System.out.println("事件日志表的文件信息:");
        TableResult filesResult = tableEnv.executeSql(
            "SELECT " +
            "  COUNT(*) as file_count, " +
            "  SUM(file_size_in_bytes)/1024/1024 as total_size_mb " +
            "FROM default.event_logs.files"
        );
        filesResult.print();
        
        System.out.println("事件日志表的分区信息:");
        TableResult partitionsResult = tableEnv.executeSql("SELECT * FROM default.event_logs.partitions");
        partitionsResult.print();
    }

    private static void cleanup(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("清理测试表...");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.event_logs");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.user_activity_summary");
    }
}