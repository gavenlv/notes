/*
 * Flink Iceberg性能优化示例 - 写入性能优化
 * 
 * 本示例演示如何在Flink中优化Iceberg表的写入性能，包括批处理大小、并行度、文件格式等配置。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableResult;

public class WriteOptimizationExample {

    public static void main(String[] args) throws Exception {
        // 1. 创建Flink执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.STREAMING);
        env.enableCheckpointing(30000); // 30秒检查点间隔
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        // 2. 配置Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 创建用于写入性能测试的表
        createTestTables(tableEnv);

        // 4. 演示不同写入配置对性能的影响
        demonstrateWriteOptimizations(tableEnv);

        // 5. 清理测试表
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

    private static void createTestTables(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 创建测试表 ===");
        
        // 创建基础测试表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.write_test_base (" +
                "id BIGINT," +
                "name STRING," +
                "value DOUBLE," +
                "timestamp_col TIMESTAMP(3)" +
                ")");
        
        // 创建优化配置的测试表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.write_test_optimized (" +
                "id BIGINT," +
                "name STRING," +
                "value DOUBLE," +
                "timestamp_col TIMESTAMP(3)" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='536870912'," + // 512MB
                "'write.parquet.compression-codec'='zstd'," +
                "'write.distribution-mode'='hash'," +
                "'write.upsert.enabled'='false'" +
                ")");
        
        // 创建ORC格式的测试表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.write_test_orc (" +
                "id BIGINT," +
                "name STRING," +
                "value DOUBLE," +
                "timestamp_col TIMESTAMP(3)" +
                ") WITH (" +
                "'write.format.default'='orc'," +
                "'write.target-file-size-bytes'='536870912'," + // 512MB
                "'write.orc.compression.codec'='zstd'" +
                ")");
    }

    private static void demonstrateWriteOptimizations(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 写入性能优化演示 ===");
        
        // 1. 测试基础写入性能
        testBasicWritePerformance(tableEnv);
        
        // 2. 测试优化配置的写入性能
        testOptimizedWritePerformance(tableEnv);
        
        // 3. 测试ORC格式的写入性能
        testORCWritePerformance(tableEnv);
        
        // 4. 并行度优化测试
        testParallelismOptimization(tableEnv);
        
        // 5. 批处理大小优化测试
        testBatchSizeOptimization(tableEnv);
    }

    private static void testBasicWritePerformance(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("--- 基础写入性能测试 ---");
        
        long startTime = System.currentTimeMillis();
        
        // 插入大量数据到基础表
        StringBuilder insertSql = new StringBuilder();
        insertSql.append("INSERT INTO default.write_test_base VALUES ");
        
        for (int i = 1; i <= 50000; i++) {
            if (i > 1) insertSql.append(", ");
            insertSql.append(String.format("(%d, 'Name %d', %.2f, CURRENT_TIMESTAMP)", i, i, Math.random() * 1000));
        }
        
        tableEnv.executeSql(insertSql.toString()).await();
        
        long endTime = System.currentTimeMillis();
        System.out.println("基础写入耗时: " + (endTime - startTime) + " ms");
        
        // 查看写入的数据量
        TableResult countResult = tableEnv.executeSql("SELECT COUNT(*) as row_count FROM default.write_test_base");
        countResult.print();
    }

    private static void testOptimizedWritePerformance(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("--- 优化配置写入性能测试 ---");
        
        long startTime = System.currentTimeMillis();
        
        // 插入同样数量的数据到优化表
        StringBuilder insertSql = new StringBuilder();
        insertSql.append("INSERT INTO default.write_test_optimized VALUES ");
        
        for (int i = 1; i <= 50000; i++) {
            if (i > 1) insertSql.append(", ");
            insertSql.append(String.format("(%d, 'Name %d', %.2f, CURRENT_TIMESTAMP)", i, i, Math.random() * 1000));
        }
        
        tableEnv.executeSql(insertSql.toString()).await();
        
        long endTime = System.currentTimeMillis();
        System.out.println("优化写入耗时: " + (endTime - startTime) + " ms");
        
        // 查看写入的数据量
        TableResult countResult = tableEnv.executeSql("SELECT COUNT(*) as row_count FROM default.write_test_optimized");
        countResult.print();
    }

    private static void testORCWritePerformance(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("--- ORC格式写入性能测试 ---");
        
        long startTime = System.currentTimeMillis();
        
        // 插入同样数量的数据到ORC表
        StringBuilder insertSql = new StringBuilder();
        insertSql.append("INSERT INTO default.write_test_orc VALUES ");
        
        for (int i = 1; i <= 50000; i++) {
            if (i > 1) insertSql.append(", ");
            insertSql.append(String.format("(%d, 'Name %d', %.2f, CURRENT_TIMESTAMP)", i, i, Math.random() * 1000));
        }
        
        tableEnv.executeSql(insertSql.toString()).await();
        
        long endTime = System.currentTimeMillis();
        System.out.println("ORC写入耗时: " + (endTime - startTime) + " ms");
        
        // 查看写入的数据量
        TableResult countResult = tableEnv.executeSql("SELECT COUNT(*) as row_count FROM default.write_test_orc");
        countResult.print();
    }

    private static void testParallelismOptimization(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("--- 并行度优化测试 ---");
        
        // 创建更高并行度的表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.write_test_parallel (" +
                "id BIGINT," +
                "name STRING," +
                "value DOUBLE," +
                "timestamp_col TIMESTAMP(3)" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='268435456'," + // 256MB
                "'write.parquet.compression-codec'='zstd'" +
                ")");
        
        long startTime = System.currentTimeMillis();
        
        // 使用更高的并行度插入数据
        StringBuilder insertSql = new StringBuilder();
        insertSql.append("INSERT INTO default.write_test_parallel VALUES ");
        
        for (int i = 1; i <= 100000; i++) {
            if (i > 1) insertSql.append(", ");
            insertSql.append(String.format("(%d, 'Name %d', %.2f, CURRENT_TIMESTAMP)", i, i, Math.random() * 1000));
        }
        
        // 设置更高的并行度进行写入
        tableEnv.getConfig().getConfiguration().setString("table.exec.resource.default-parallelism", "8");
        tableEnv.executeSql(insertSql.toString()).await();
        
        long endTime = System.currentTimeMillis();
        System.out.println("高并行度写入耗时: " + (endTime - startTime) + " ms");
        
        // 查看写入的数据量
        TableResult countResult = tableEnv.executeSql("SELECT COUNT(*) as row_count FROM default.write_test_parallel");
        countResult.print();
    }

    private static void testBatchSizeOptimization(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("--- 批处理大小优化测试 ---");
        
        // 创建适合小批量写入的表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.write_test_batch (" +
                "id BIGINT," +
                "name STRING," +
                "value DOUBLE," +
                "timestamp_col TIMESTAMP(3)" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='134217728'," + // 128MB
                "'write.parquet.compression-codec'='snappy'" +
                ")");
        
        long startTime = System.currentTimeMillis();
        
        // 分批插入数据，模拟流式写入场景
        for (int batch = 0; batch < 10; batch++) {
            StringBuilder insertSql = new StringBuilder();
            insertSql.append("INSERT INTO default.write_test_batch VALUES ");
            
            for (int i = 1; i <= 10000; i++) {
                int id = batch * 10000 + i;
                if (i > 1) insertSql.append(", ");
                insertSql.append(String.format("(%d, 'Name %d', %.2f, CURRENT_TIMESTAMP)", id, id, Math.random() * 1000));
            }
            
            tableEnv.executeSql(insertSql.toString()).await();
        }
        
        long endTime = System.currentTimeMillis();
        System.out.println("分批写入总耗时: " + (endTime - startTime) + " ms");
        
        // 查看写入的数据量
        TableResult countResult = tableEnv.executeSql("SELECT COUNT(*) as row_count FROM default.write_test_batch");
        countResult.print();
    }

    private static void cleanup(StreamTableEnvironment tableEnv) {
        System.out.println("=== 清理测试表 ===");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.write_test_base");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.write_test_optimized");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.write_test_orc");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.write_test_parallel");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.write_test_batch");
    }
}