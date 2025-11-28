/*
 * Flink Iceberg性能优化示例 - 缓存配置优化
 * 
 * 本示例演示如何在Flink中优化Iceberg表的缓存配置，包括元数据缓存、文件缓存等。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableResult;

public class CachingConfigExample {

    public static void main(String[] args) throws Exception {
        // 1. 创建Flink执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.BATCH);
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        // 2. 配置Iceberg Catalog及缓存参数
        configureIcebergCatalogWithCaching(tableEnv);

        // 3. 创建测试表并插入数据
        createAndPopulateTestTables(tableEnv);

        // 4. 演示缓存配置优化效果
        demonstrateCachingOptimizations(tableEnv);

        // 5. 查看缓存统计信息
        showCacheStatistics(tableEnv);

        // 6. 清理测试表
        cleanup(tableEnv);
    }

    private static void configureIcebergCatalogWithCaching(StreamTableEnvironment tableEnv) {
        System.out.println("=== 配置Iceberg Catalog及缓存参数 ===");
        
        // 配置Iceberg Catalog，启用各种缓存机制
        tableEnv.executeSql("CREATE CATALOG iceberg_catalog WITH (" +
                "'type'='iceberg'," +
                "'catalog-type'='hadoop'," +
                "'warehouse'='hdfs://localhost:9000/iceberg/warehouse'," +
                "'cache-enabled'='true'," +
                "'cache.expiration-interval-ms'='300000'," + // 5分钟缓存过期
                "'table-cache-enabled'='true'," +
                "'table-cache.expiration-interval-ms'='600000'" + // 10分钟表缓存过期
                ")");
        
        tableEnv.executeSql("USE CATALOG iceberg_catalog");
    }

    private static void createAndPopulateTestTables(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 创建并填充测试表 ===");
        
        // 创建用户表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.caching_users (" +
                "user_id BIGINT," +
                "username STRING," +
                "email STRING," +
                "registration_date DATE," +
                "last_login TIMESTAMP(3)," +
                "is_active BOOLEAN" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='268435456'," + // 256MB
                "'write.parquet.compression-codec'='zstd'," +
                "'write.metadata.metrics.column.user_id'='truncate(16)'," +
                "'write.metadata.metrics.column.email'='full'," +
                "'write.metadata.metrics.mode'='full'" +
                ")");
        
        // 创建订单表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.caching_orders (" +
                "order_id BIGINT," +
                "user_id BIGINT," +
                "product_name STRING," +
                "amount DECIMAL(10,2)," +
                "order_date DATE," +
                "status STRING" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='268435456'," +
                "'write.parquet.compression-codec'='zstd'" +
                ")");
        
        // 插入用户数据
        System.out.println("插入用户数据...");
        StringBuilder userInsert = new StringBuilder();
        userInsert.append("INSERT INTO default.caching_users VALUES ");
        
        for (int i = 1; i <= 20000; i++) {
            if (i > 1) userInsert.append(", ");
            userInsert.append(String.format("(%d, 'user_%d', 'user%d@example.com', DATE '2023-%02d-%02d', CURRENT_TIMESTAMP, %s)",
                    i, i, i, (i % 12) + 1, (i % 28) + 1, (i % 5 == 0) ? "false" : "true"));
        }
        
        tableEnv.executeSql(userInsert.toString()).await();
        
        // 插入订单数据
        System.out.println("插入订单数据...");
        StringBuilder orderInsert = new StringBuilder();
        orderInsert.append("INSERT INTO default.caching_orders VALUES ");
        
        for (int i = 1; i <= 50000; i++) {
            if (i > 1) orderInsert.append(", ");
            orderInsert.append(String.format("(%d, %d, 'Product %d', %.2f, DATE '2023-%02d-%02d', '%s')",
                    i, ((i - 1) % 20000) + 1, i, (Math.random() * 1000) + 10, 
                    ((i - 1) % 12) + 1, ((i - 1) % 28) + 1, 
                    (i % 1000 == 0) ? "cancelled" : (i % 100 == 0) ? "shipped" : "pending"));
        }
        
        tableEnv.executeSql(orderInsert.toString()).await();
        
        System.out.println("数据插入完成");
    }

    private static void demonstrateCachingOptimizations(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 缓存优化效果演示 ===");
        
        // 第一次查询（无缓存）
        System.out.println("--- 第一次查询（无缓存）---");
        long startTime1 = System.currentTimeMillis();
        TableResult result1 = tableEnv.executeSql(
            "SELECT u.username, COUNT(o.order_id) as order_count " +
            "FROM default.caching_users u " +
            "JOIN default.caching_orders o ON u.user_id = o.user_id " +
            "WHERE u.is_active = true " +
            "GROUP BY u.username " +
            "ORDER BY order_count DESC " +
            "LIMIT 10"
        );
        result1.print();
        long endTime1 = System.currentTimeMillis();
        System.out.println("第一次查询耗时: " + (endTime1 - startTime1) + " ms");
        
        // 等待一小段时间让缓存生效
        Thread.sleep(2000);
        
        // 第二次查询（利用缓存）
        System.out.println("--- 第二次查询（利用缓存）---");
        long startTime2 = System.currentTimeMillis();
        TableResult result2 = tableEnv.executeSql(
            "SELECT u.username, COUNT(o.order_id) as order_count " +
            "FROM default.caching_users u " +
            "JOIN default.caching_orders o ON u.user_id = o.user_id " +
            "WHERE u.is_active = true " +
            "GROUP BY u.username " +
            "ORDER BY order_count DESC " +
            "LIMIT 10"
        );
        result2.print();
        long endTime2 = System.currentTimeMillis();
        System.out.println("第二次查询耗时: " + (endTime2 - startTime2) + " ms");
        
        // 展示缓存命中率提升
        double improvement = (double)(endTime1 - startTime1 - (endTime2 - startTime2)) / (endTime1 - startTime1) * 100;
        System.out.println("查询性能提升: " + String.format("%.2f", improvement) + "%");
    }

    private static void showCacheStatistics(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 缓存统计信息 ===");
        
        // 查看表的文件信息（可以间接反映缓存效果）
        System.out.println("用户表文件信息:");
        TableResult userFileInfo = tableEnv.executeSql(
            "SELECT " +
            "COUNT(*) as file_count, " +
            "SUM(file_size_in_bytes)/1024/1024 as total_size_mb, " +
            "AVG(record_count) as avg_records_per_file " +
            "FROM default.caching_users.files"
        );
        userFileInfo.print();
        
        System.out.println("订单表文件信息:");
        TableResult orderFileInfo = tableEnv.executeSql(
            "SELECT " +
            "COUNT(*) as file_count, " +
            "SUM(file_size_in_bytes)/1024/1024 as total_size_mb, " +
            "AVG(record_count) as avg_records_per_file " +
            "FROM default.caching_orders.files"
        );
        orderFileInfo.print();
        
        // 查看表的分区信息
        System.out.println("订单表按日期分区统计:");
        TableResult partitionStats = tableEnv.executeSql(
            "SELECT " +
            "partition.order_date, " +
            "COUNT(*) as file_count, " +
            "SUM(record_count) as total_records " +
            "FROM default.caching_orders.files " +
            "GROUP BY partition.order_date " +
            "ORDER BY partition.order_date"
        );
        partitionStats.print();
    }

    private static void cleanup(StreamTableEnvironment tableEnv) {
        System.out.println("=== 清理测试表 ===");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.caching_users");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.caching_orders");
    }
}