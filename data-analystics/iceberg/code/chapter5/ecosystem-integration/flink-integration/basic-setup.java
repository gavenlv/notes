/*
 * Flink Iceberg 集成基础示例
 * 
 * 本示例演示如何在 Flink 中配置 Iceberg 并进行基本的表操作。
 */

import org.apache.flink.api.common.RuntimeExecutionMode;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.CoreOptions;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.types.Row;

public class FlinkIcebergBasicSetup {

    public static void main(String[] args) throws Exception {
        // 1. 创建 Flink 执行环境
        Configuration flinkConfig = new Configuration();
        flinkConfig.set(CoreOptions.DEFAULT_PARALLELISM, 4);
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(flinkConfig);
        env.setRuntimeMode(RuntimeExecutionMode.BATCH);
        
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

        System.out.println("=== Flink Iceberg 集成基础配置 ===");
        
        // 2. 配置 Iceberg Catalog
        configureIcebergCatalog(tableEnv);

        // 3. 创建数据库
        tableEnv.executeSql("CREATE DATABASE IF NOT EXISTS default");
        tableEnv.executeSql("USE default");

        // 4. 创建 Iceberg 表
        createIcebergTables(tableEnv);

        // 5. 插入测试数据
        insertTestData(tableEnv);

        // 6. 查询数据
        queryData(tableEnv);

        // 7. 更新数据
        updateData(tableEnv);

        // 8. 删除数据
        deleteData(tableEnv);

        // 9. 查看表元数据
        showTableMetadata(tableEnv);

        // 10. 时间旅行查询
        timeTravelQuery(tableEnv);

        // 11. 清理资源
        cleanup(tableEnv);

        System.out.println("Flink Iceberg 基础配置示例完成!");
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

    private static void createIcebergTables(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("创建 Iceberg 表...");
        
        // 创建用户表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.flink_users (" +
                "id BIGINT," +
                "name STRING," +
                "email STRING," +
                "age INT," +
                "created_at TIMESTAMP(3)" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='268435456'," +
                "'write.parquet.compression-codec'='zstd'" +
                ")");
        
        // 创建订单表
        tableEnv.executeSql("CREATE TABLE IF NOT EXISTS default.flink_orders (" +
                "order_id BIGINT," +
                "user_id BIGINT," +
                "product_name STRING," +
                "amount DECIMAL(10,2)," +
                "order_date DATE," +
                "status STRING" +
                ") WITH (" +
                "'write.format.default'='parquet'," +
                "'write.target-file-size-bytes'='268435456'" +
                ")");
    }

    private static void insertTestData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("插入测试数据...");
        
        // 插入用户数据
        tableEnv.executeSql("INSERT INTO default.flink_users VALUES " +
                "(1, '张三', 'zhangsan@example.com', 25, TIMESTAMP '2023-01-15 10:30:00'), " +
                "(2, '李四', 'lisi@example.com', 30, TIMESTAMP '2023-01-16 14:45:00'), " +
                "(3, '王五', 'wangwu@example.com', 28, TIMESTAMP '2023-01-17 09:15:00'), " +
                "(4, '赵六', 'zhaoliu@example.com', 35, TIMESTAMP '2023-01-18 16:20:00')").await();
        
        // 插入订单数据
        tableEnv.executeSql("INSERT INTO default.flink_orders VALUES " +
                "(1001, 1, '笔记本电脑', 5999.99, DATE '2023-01-20', 'completed'), " +
                "(1002, 2, '手机', 2999.99, DATE '2023-01-21', 'completed'), " +
                "(1003, 1, '鼠标', 99.99, DATE '2023-01-22', 'pending'), " +
                "(1004, 3, '键盘', 199.99, DATE '2023-01-23', 'shipped')").await();
        
        System.out.println("测试数据插入完成");
    }

    private static void queryData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("查询所有用户数据:");
        TableResult userResult = tableEnv.executeSql("SELECT * FROM default.flink_users");
        userResult.print();
        
        System.out.println("查询所有订单数据:");
        TableResult orderResult = tableEnv.executeSql("SELECT * FROM default.flink_orders");
        orderResult.print();
        
        System.out.println("关联查询用户和订单:");
        TableResult joinResult = tableEnv.executeSql(
            "SELECT u.name, u.email, o.product_name, o.amount, o.status " +
            "FROM default.flink_users u " +
            "JOIN default.flink_orders o ON u.id = o.user_id"
        );
        joinResult.print();
    }

    private static void updateData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("更新用户数据...");
        
        tableEnv.executeSql(
            "UPDATE default.flink_users " +
            "SET email = 'zhangsan_updated@example.com' " +
            "WHERE id = 1"
        ).await();
        
        System.out.println("更新后的用户数据:");
        TableResult result = tableEnv.executeSql("SELECT * FROM default.flink_users WHERE id = 1");
        result.print();
    }

    private static void deleteData(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("删除订单数据...");
        
        tableEnv.executeSql(
            "DELETE FROM default.flink_orders " +
            "WHERE order_id = 1004"
        ).await();
        
        System.out.println("删除后的订单数据:");
        TableResult result = tableEnv.executeSql("SELECT * FROM default.flink_orders");
        result.print();
    }

    private static void showTableMetadata(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("查看用户表的历史快照:");
        TableResult historyResult = tableEnv.executeSql("SELECT * FROM default.flink_users.history");
        historyResult.print();
        
        System.out.println("查看订单表的分区信息:");
        TableResult partitionsResult = tableEnv.executeSql("SELECT * FROM default.flink_orders.partitions");
        partitionsResult.print();
        
        System.out.println("查看用户表的当前快照:");
        TableResult snapshotsResult = tableEnv.executeSql("SELECT * FROM default.flink_users.snapshots");
        snapshotsResult.print();
    }

    private static void timeTravelQuery(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("时间旅行查询...");
        
        // 获取最早的快照ID
        TableResult snapshotResult = tableEnv.executeSql(
            "SELECT snapshot_id FROM default.flink_users.history ORDER BY committed_at ASC LIMIT 1"
        );
        
        // 注意：在实际应用中，我们需要从结果中提取快照ID
        // 这里为了简化示例，我们直接使用AS OF语法演示
        System.out.println("查询表的早期状态:");
        TableResult timeTravelResult = tableEnv.executeSql(
            "SELECT * FROM default.flink_users /*+ OPTIONS('scan.snapshot-id'='1') */"
        );
        // 注意：上面的注释语法可能因Flink版本而异，这里仅作示意
        
        System.out.println("当前表数据:");
        TableResult currentResult = tableEnv.executeSql("SELECT * FROM default.flink_users");
        currentResult.print();
    }

    private static void cleanup(StreamTableEnvironment tableEnv) throws Exception {
        System.out.println("清理测试表...");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.flink_users");
        tableEnv.executeSql("DROP TABLE IF EXISTS default.flink_orders");
    }
}