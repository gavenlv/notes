/*
 * Flink Iceberg性能优化示例 - 文件合并优化
 * 
 * 本示例演示如何在Flink中对Iceberg表进行文件合并优化，以提高查询性能。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.types.Row;
import org.apache.hadoop.conf.Configuration;
import org.apache.iceberg.flink.FlinkCatalogFactory;
import org.apache.iceberg.flink.TableLoader;
import org.apache.iceberg.flink.actions.Actions;
import org.apache.iceberg.flink.source.FlinkSource;
import org.apache.iceberg.Table;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

public class FileCompactionExample {

    public static void main(String[] args) throws Exception {
        // 1. 创建Flink执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.BATCH);
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        // 2. 配置Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 创建测试表
        createTestTable(tableEnv);

        // 4. 插入测试数据以生成小文件
        insertTestData(tableEnv);

        // 5. 查看合并前的文件信息
        System.out.println("=== 合并前的文件信息 ===");
        showFileInfo(tableEnv);

        // 6. 执行文件合并操作
        compactFiles(tableEnv);

        // 7. 查看合并后的文件信息
        System.out.println("=== 合并后的文件信息 ===");
        showFileInfo(tableEnv);

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

    private static void createTestTable(StreamTableEnvironment tableEnv) {
        // 创建测试表，故意设置较小的目标文件大小以生成小文件
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.compaction_test (" +
                "id BIGINT," +
                "name STRING," +
                "category STRING," +
                "price DOUBLE," +
                "created_date DATE" +
                ") PARTITIONED BY (category, created_date)" +
                " WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='33554432'  -- 32MB，较小的目标文件大小" +
                ")");
    }

    private static void insertTestData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("=== 插入测试数据 ===");
        
        // 插入多批次小数据以生成小文件
        for (int i = 1; i <= 10; i++) {
            String insertSql = String.format(
                "INSERT INTO default.compaction_test VALUES " +
                "(%d, 'name_%d', 'category_%d', %f, DATE '2023-01-%02d')",
                i, i, i % 3, i * 10.0, i
            );
            
            tableEnv.executeSql(insertSql).await();
            System.out.println("Inserted batch " + i);
            
            // 小间隔以确保生成多个文件
            Thread.sleep(100);
        }
    }

    private static void showFileInfo(StreamTableEnvironment tableEnv) {
        TableResult result = tableEnv.executeSql(
            "SELECT file_path, file_size_in_bytes, partition FROM default.compaction_test.files"
        );
        
        result.print();
    }

    private static void compactFiles(StreamTableEnvironment tableEnv) {
        System.out.println("=== 执行文件合并 ===");
        
        try {
            // 使用Iceberg Actions进行文件合并
            TableLoader tableLoader = TableLoader.fromCatalog(
                FlinkCatalogFactory.createCatalog("iceberg_catalog"),
                org.apache.iceberg.catalog.TableIdentifier.of("default", "compaction_test")
            );
            
            Actions.forTable(tableLoader)
                .rewriteDataFiles()
                .targetSizeInBytes(536870912L)  // 512MB目标文件大小
                .minInputFiles(5)               // 至少5个输入文件才合并
                .execute();
                
            System.out.println("文件合并完成");
        } catch (Exception e) {
            System.err.println("文件合并失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void cleanup(StreamTableEnvironment tableEnv) {
        System.out.println("=== 清理测试表 ===");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.compaction_test");
    }
}