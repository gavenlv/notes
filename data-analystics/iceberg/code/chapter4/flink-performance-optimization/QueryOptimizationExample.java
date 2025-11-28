/*
 * Flink Iceberg性能优化示例 - 查询优化
 * 
 * 本示例演示如何在Flink中优化Iceberg表的查询性能，包括布隆过滤器、数据裁剪等技术。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableResult;

public class QueryOptimizationExample {

    public static void main(String[] args) throws Exception {
        // 1. 创建Flink执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.BATCH);
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        // 2. 配置Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 创建带布隆过滤器的测试表
        createOptimizedTable(tableEnv);

        // 4. 插入大量测试数据
        insertTestData(tableEnv);

        // 5. 查询优化技术演示
        demonstrateBloomFilters(tableEnv);
        demonstratePartitionPruning(tableEnv);
        demonstrateColumnPruning(tableEnv);

        // 6. 查询性能对比
        compareQueryPerformance(tableEnv);

        // 7. 查看表统计信息
        showTableStatistics(tableEnv);

        // 8. 清理测试表
        cleanup(tableEnv);
    }

    private static void configureIcebergCatalog(StreamTableEnvironment tableEnv) {
        // 配置Iceberg Catalog
        tableEnv.executeSql("CREATE CATALOG iceberg_catalog WITH (" +
                "'type'='iceberg'," +
                "'catalog-type'='hadoop'," +
                "'warehouse'='hdfs://localhost:9000/iceberg/warehouse'" +
                ")");
        
        tableEnv.executeSql("USE CATALOG iceberg_catalog");
    }

    private static void createOptimizedTable(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 创建带布隆过滤器的优化表 ===");
        
        // 创建带布隆过滤器的用户表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.users_optimized (" +
                "user_id BIGINT," +
                "email STRING," +
                "name STRING," +
                "signup_date DATE," +
                "status STRING" +
                ") WITH (" +
                "'write.metadata.metrics.column.user_id'='truncate(16)'," +
                "'write.metadata.metrics.column.email'='full'," +
                "'write.metadata.metrics.mode'='full'" +
                ")");
    }

    private static void insertTestData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 插入测试数据 ===");
        
        // 插入大量测试数据以演示优化效果
        StringBuilder batchInsert = new StringBuilder();
        batchInsert.append("INSERT INTO default.users_optimized VALUES ");
        
        for (int i = 1; i <= 10000; i++) {
            if (i > 1) batchInsert.append(", ");
            batchInsert.append(String.format("(%d, 'user%d@example.com', 'User Name %d', DATE '2023-%02d-%02d', '%s')",
                    i, i, i, (i % 12) + 1, (i % 28) + 1, (i % 100 == 0) ? "premium" : "standard"));
        }
        
        tableEnv.executeSql(batchInsert.toString()).await();
        System.out.println("插入了10000条测试记录");
        
        // 再插入几批数据以创建多个文件
        for (int batch = 1; batch <= 3; batch++) {
            StringBuilder additionalBatch = new StringBuilder();
            additionalBatch.append("INSERT INTO default.users_optimized VALUES ");
            
            for (int i = 1; i <= 5000; i++) {
                int userId = 10000 + (batch - 1) * 5000 + i;
                if (i > 1) additionalBatch.append(", ");
                additionalBatch.append(String.format("(%d, 'user%d@example.com', 'User Name %d', DATE '2023-%02d-%02d', '%s')",
                        userId, userId, userId, ((batch - 1) * 4 + (i % 12)) + 1, (i % 28) + 1, (i % 75 == 0) ? "premium" : "standard"));
            }
            
            tableEnv.executeSql(additionalBatch.toString()).await();
            System.out.println("插入了第" + batch + "批数据，5000条记录");
        }
    }

    private static void demonstrateBloomFilters(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 布隆过滤器优化效果演示 ===");
        
        System.out.println("查询特定用户的记录（利用布隆过滤器）:");
        
        // 查询特定用户（应该能利用布隆过滤器快速定位）
        long startTime = System.currentTimeMillis();
        TableResult result = tableEnv.executeSql("SELECT * FROM default.users_optimized WHERE user_id = 1234");
        result.print();
        long endTime = System.currentTimeMillis();
        
        System.out.println("查询耗时: " + (endTime - startTime) + " ms");
    }

    private static void demonstratePartitionPruning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 分区裁剪优化演示 ===");
        
        // 创建分区表以演示分区裁剪
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.events_partitioned (" +
                "event_id BIGINT," +
                "user_id BIGINT," +
                "event_type STRING," +
                "event_date DATE," +
                "details STRING" +
                ") PARTITIONED BY (event_type, months(event_date))");
        
        // 插入测试数据
        tableEnv.executeSql("INSERT INTO default.events_partitioned VALUES " +
                "(1, 1001, 'purchase', DATE '2023-01-15', 'Purchase event'), " +
                "(2, 1002, 'login', DATE '2023-01-16', 'Login event'), " +
                "(3, 1003, 'purchase', DATE '2023-02-20', 'Purchase event')").await();
        
        System.out.println("查询特定类型和时间段的事件:");
        
        long startTime = System.currentTimeMillis();
        TableResult result = tableEnv.executeSql("SELECT COUNT(*) as event_count " +
                "FROM default.events_partitioned " +
                "WHERE event_type = 'purchase' " +
                "AND event_date >= DATE '2023-01-01' " +
                "AND event_date <= DATE '2023-01-31'");
        result.print();
        long endTime = System.currentTimeMillis();
        
        System.out.println("查询耗时: " + (endTime - startTime) + " ms");
    }

    private static void demonstrateColumnPruning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 列裁剪优化演示 ===");
        
        System.out.println("只查询需要的列:");
        
        long startTime = System.currentTimeMillis();
        TableResult result = tableEnv.executeSql("SELECT user_id, email " +
                "FROM default.users_optimized " +
                "WHERE status = 'premium'");
        result.print();
        long endTime = System.currentTimeMillis();
        
        System.out.println("查询耗时: " + (endTime - startTime) + " ms");
    }

    private static void compareQueryPerformance(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 查询性能对比 ===");
        
        // 未优化查询（全表扫描）
        System.out.println("未优化查询（全表扫描）:");
        long startTime1 = System.currentTimeMillis();
        TableResult result1 = tableEnv.executeSql("SELECT * FROM default.users_optimized WHERE email LIKE '%1234@example.com%'");
        // 我们不打印结果以避免大量输出，只关注执行时间
        long endTime1 = System.currentTimeMillis();
        System.out.println("未优化查询耗时: " + (endTime1 - startTime1) + " ms");
        
        // 优化查询（利用布隆过滤器）
        System.out.println("优化查询（利用布隆过滤器）:");
        long startTime2 = System.currentTimeMillis();
        TableResult result2 = tableEnv.executeSql("SELECT * FROM default.users_optimized WHERE user_id = 1234");
        // 我们不打印结果以避免大量输出，只关注执行时间
        long endTime2 = System.currentTimeMillis();
        System.out.println("优化查询耗时: " + (endTime2 - startTime2) + " ms");
    }

    private static void showTableStatistics(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 表统计信息 ===");
        
        // 查看用户表的文件信息
        System.out.println("用户表文件信息:");
        TableResult fileInfo = tableEnv.executeSql("SELECT " +
                "COUNT(*) as file_count, " +
                "AVG(file_size_in_bytes) as avg_file_size, " +
                "MAX(file_size_in_bytes) as max_file_size, " +
                "MIN(file_size_in_bytes) as min_file_size " +
                "FROM default.users_optimized.files");
        fileInfo.print();
        
        // 查看事件表的分区信息
        System.out.println("事件表分区信息:");
        TableResult partitionInfo = tableEnv.executeSql("SELECT " +
                "partition.event_type, " +
                "partition.event_date_month, " +
                "COUNT(*) as file_count, " +
                "SUM(file_size_in_bytes) as total_size " +
                "FROM default.events_partitioned.files " +
                "GROUP BY partition.event_type, partition.event_date_month " +
                "ORDER BY total_size DESC");
        partitionInfo.print();
    }

    private static void cleanup(StreamTableEnvironment tableEnv) {
        System.out.println("=== 清理测试表 ===");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.users_optimized");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.events_partitioned");
    }
}