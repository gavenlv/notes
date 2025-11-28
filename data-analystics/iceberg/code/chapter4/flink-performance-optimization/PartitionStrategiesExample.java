/*
 * Flink Iceberg性能优化示例 - 分区策略优化
 * 
 * 本示例演示如何在Flink中使用不同的Iceberg分区策略来优化性能。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.types.Row;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

public class PartitionStrategiesExample {

    public static void main(String[] args) throws Exception {
        // 1. 创建Flink执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.BATCH);
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        // 2. 配置Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 演示不同的分区策略
        demonstrateIdentityPartitioning(tableEnv);
        demonstrateTimePartitioning(tableEnv);
        demonstrateBucketPartitioning(tableEnv);
        demonstrateTruncatePartitioning(tableEnv);
        demonstrateCompositePartitioning(tableEnv);

        // 4. 分区演化示例
        demonstratePartitionEvolution(tableEnv);

        // 5. 分区裁剪效果演示
        demonstratePartitionPruning(tableEnv);

        // 6. 清理测试表
        cleanupTables(tableEnv);
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

    private static void demonstrateIdentityPartitioning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== Identity分区策略演示 ===");
        
        // 创建Identity分区表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.sales_identity (" +
                "id BIGINT," +
                "product STRING," +
                "region STRING," +
                "sale_date DATE," +
                "amount DOUBLE" +
                ") PARTITIONED BY (region)");
        
        // 插入测试数据
        String[] regions = {"North", "South", "East", "West"};
        String[] products = {"ProductA", "ProductB", "ProductC"};
        
        for (int i = 1; i <= 20; i++) {
            String region = regions[i % regions.length];
            String product = products[i % products.length];
            String insertSql = String.format(
                "INSERT INTO default.sales_identity VALUES " +
                "(%d, '%s', '%s', DATE '2023-01-%02d', %f)",
                (long)i, product, region, i, i * 100.0
            );
            tableEnv.executeSql(insertSql).await();
        }
        
        // 查看分区信息
        System.out.println("Identity分区表分区信息:");
        tableEnv.executeSql("SELECT partition.region, COUNT(*) as file_count " +
                "FROM default.sales_identity.files " +
                "GROUP BY partition.region").print();
    }

    private static void demonstrateTimePartitioning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 时间分区策略演示 ===");
        
        // 创建时间分区表（按月）
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.sales_time (" +
                "id BIGINT," +
                "product STRING," +
                "region STRING," +
                "sale_date DATE," +
                "amount DOUBLE" +
                ") PARTITIONED BY (months(sale_date))");
        
        // 插入测试数据
        String[] products = {"ProductA", "ProductB", "ProductC"};
        String[] regions = {"North", "South", "East", "West"};
        
        for (int i = 1; i <= 30; i++) {
            String product = products[i % products.length];
            String region = regions[i % regions.length];
            int day = i;
            int month = (i - 1) / 10 + 1; // 每10天一个月份
            String insertSql = String.format(
                "INSERT INTO default.sales_time VALUES " +
                "(%d, '%s', '%s', DATE '2023-%02d-%02d', %f)",
                (long)i, product, region, month, day, i * 100.0
            );
            tableEnv.executeSql(insertSql).await();
        }
        
        // 查看分区信息
        System.out.println("时间分区表分区信息:");
        tableEnv.executeSql("SELECT partition.sale_date_month, COUNT(*) as file_count " +
                "FROM default.sales_time.files " +
                "GROUP BY partition.sale_date_month " +
                "ORDER BY partition.sale_date_month").print();
    }

    private static void demonstrateBucketPartitioning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== Bucket分区策略演示 ===");
        
        // 创建Bucket分区表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.users_bucket (" +
                "user_id BIGINT," +
                "name STRING," +
                "email STRING," +
                "signup_date DATE" +
                ") PARTITIONED BY (bucket(8, user_id))");
        
        // 插入测试数据
        for (int i = 1; i <= 100; i++) {
            String insertSql = String.format(
                "INSERT INTO default.users_bucket VALUES " +
                "(%d, 'User%d', 'user%d@example.com', DATE '2023-01-%02d')",
                (long)i, i, i, (i % 28) + 1
            );
            tableEnv.executeSql(insertSql).await();
        }
        
        // 查看分区信息
        System.out.println("Bucket分区表分区信息:");
        tableEnv.executeSql("SELECT partition.user_id_bucket, COUNT(*) as file_count " +
                "FROM default.users_bucket.files " +
                "GROUP BY partition.user_id_bucket " +
                "ORDER BY partition.user_id_bucket").print();
    }

    private static void demonstrateTruncatePartitioning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== Truncate分区策略演示 ===");
        
        // 创建Truncate分区表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.products_truncate (" +
                "product_id STRING," +
                "name STRING," +
                "category STRING," +
                "price DOUBLE" +
                ") PARTITIONED BY (truncate(2, category))");
        
        // 插入测试数据
        String[] categories = {"Electronics", "Clothing", "Books", "Home", "Sports"};
        
        for (int i = 1; i <= 50; i++) {
            String category = categories[i % categories.length];
            String insertSql = String.format(
                "INSERT INTO default.products_truncate VALUES " +
                "('P%04d', 'Product%d', '%s', %f)",
                i, i, category, i * 10.0
            );
            tableEnv.executeSql(insertSql).await();
        }
        
        // 查看分区信息
        System.out.println("Truncate分区表分区信息:");
        tableEnv.executeSql("SELECT partition.category_trunc, COUNT(*) as file_count " +
                "FROM default.products_truncate.files " +
                "GROUP BY partition.category_trunc " +
                "ORDER BY partition.category_trunc").print();
    }

    private static void demonstrateCompositePartitioning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 复合分区策略演示 ===");
        
        // 创建复合分区表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.events_composite (" +
                "event_id BIGINT," +
                "event_type STRING," +
                "user_id BIGINT," +
                "event_date DATE," +
                "details STRING" +
                ") PARTITIONED BY (event_type, bucket(4, user_id), days(event_date))");
        
        // 插入测试数据
        String[] eventTypes = {"login", "purchase", "view", "search"};
        
        for (int i = 1; i <= 100; i++) {
            String eventType = eventTypes[i % eventTypes.length];
            long userId = (long)(i % 20 + 1);
            String insertSql = String.format(
                "INSERT INTO default.events_composite VALUES " +
                "(%d, '%s', %d, DATE '2023-01-%02d', 'Event details for event %d')",
                (long)i, eventType, userId, (i % 28) + 1, i
            );
            tableEnv.executeSql(insertSql).await();
        }
        
        // 查看分区信息
        System.out.println("复合分区表分区信息 (前10个分区):");
        tableEnv.executeSql("SELECT " +
                "partition.event_type, " +
                "partition.user_id_bucket, " +
                "partition.event_date_day, " +
                "COUNT(*) as file_count " +
                "FROM default.events_composite.files " +
                "GROUP BY partition.event_type, partition.user_id_bucket, partition.event_date_day " +
                "ORDER BY file_count DESC " +
                "LIMIT 10").print();
    }

    private static void demonstratePartitionEvolution(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 分区演化演示 ===");
        
        // 创建初始表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.partition_evolution (" +
                "id BIGINT," +
                "name STRING," +
                "region STRING," +
                "created_date DATE" +
                ") PARTITIONED BY (region)");
        
        // 插入初始数据
        tableEnv.executeSql("INSERT INTO default.partition_evolution VALUES " +
                "(1, 'Product1', 'North', DATE '2023-01-01'), " +
                "(2, 'Product2', 'South', DATE '2023-01-02')").await();
        
        // 添加新的分区字段
        System.out.println("添加日期分区字段:");
        tableEnv.executeSql("ALTER TABLE default.partition_evolution ADD PARTITION FIELD days(created_date)");
        
        // 插入更多数据
        tableEnv.executeSql("INSERT INTO default.partition_evolution VALUES " +
                "(3, 'Product3', 'East', DATE '2023-01-03'), " +
                "(4, 'Product4', 'West', DATE '2023-01-04')").await();
        
        // 查看分区演化后的效果
        System.out.println("分区演化后的分区信息:");
        tableEnv.executeSql("SELECT * FROM default.partition_evolution.partitions").print();
    }

    private static void demonstratePartitionPruning(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 分区裁剪效果演示 ===");
        
        // 查看查询计划以确认分区裁剪生效
        System.out.println("查询计划（注意分区裁剪信息）:");
        tableEnv.executeSql("EXPLAIN PLAN FOR " +
                "SELECT * FROM default.sales_identity " +
                "WHERE region = 'North' AND sale_date >= DATE '2023-01-15'").print();
    }

    private static void cleanupTables(StreamTableEnvironment tableEnv) {
        System.out.println("=== 清理测试表 ===");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.sales_identity");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.sales_time");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.users_bucket");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.products_truncate");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.events_composite");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.partition_evolution");
    }
}