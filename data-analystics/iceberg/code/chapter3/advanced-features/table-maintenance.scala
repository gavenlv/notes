import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
import org.apache.log4j.{Level, Logger}

object TableMaintenance {
  def main(args: Array[String]): Unit = {
    // 设置日志级别
    Logger.getLogger("org").setLevel(Level.WARN)
    Logger.getLogger("akka").setLevel(Level.WARN)

    // 创建 Spark Session 并启用 Iceberg 扩展
    val spark = SparkSession.builder()
      .appName("Iceberg Table Maintenance")
      .master("local[*]")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
      .config("spark.sql.catalog.spark_catalog.type", "hadoop")
      .config("spark.sql.catalog.spark_catalog.warehouse", "file:///tmp/iceberg/warehouse")
      .getOrCreate()

    import spark.implicits._

    println("=== Apache Iceberg 表维护操作示例 ===")

    // 创建数据库
    spark.sql("CREATE DATABASE IF NOT EXISTS iceberg_db")
    spark.sql("USE iceberg_db")

    // 1. 创建测试表
    println("\n1. 创建测试表 orders_maintenance")
    spark.sql("""
      CREATE OR REPLACE TABLE orders_maintenance (
        order_id BIGINT,
        customer_id STRING,
        product STRING,
        amount DECIMAL(10,2),
        order_date DATE,
        status STRING
      ) USING iceberg
      PARTITIONED BY (order_date)
      TBLPROPERTIES (
        'format-version'='2',
        'write.distribution-mode'='hash'
      )
    """)

    // 2. 插入初始数据
    println("\n2. 插入初始数据")
    spark.sql("""
      INSERT INTO orders_maintenance VALUES
      (1001, 'CUST001', 'Laptop', 1200.00, DATE '2024-01-15', 'completed'),
      (1002, 'CUST002', 'Phone', 800.00, DATE '2024-01-16', 'completed'),
      (1003, 'CUST001', 'Mouse', 25.00, DATE '2024-01-17', 'pending'),
      (1004, 'CUST003', 'Keyboard', 75.00, DATE '2024-01-18', 'cancelled')
    """)

    // 3. 模拟多次更新产生多个快照
    println("\n3. 模拟多次更新产生多个快照")
    for (i <- 1 to 5) {
      spark.sql(s"""
        INSERT INTO orders_maintenance VALUES
        (${
        1004 + i
      }, 'CUST00${i}', 'Product${i}', ${
        100.00 + i * 10
      }, DATE '2024-01-2${i}', 'completed')
      """)
      
      Thread.sleep(1000) // 确保不同时间戳
      
      if (i % 2 == 0) {
        spark.sql(s"UPDATE orders_maintenance SET status = 'processed' WHERE order_id = ${1004 + i}")
      }
    }

    // 4. 查看当前快照历史
    println("\n4. 查看当前快照历史")
    spark.sql("SELECT snapshot_id, operation, committed_at FROM orders_maintenance.history").show(false)

    // 5. 查看当前文件信息
    println("\n5. 查看当前文件信息")
    spark.sql("SELECT file_path, record_count, file_size_in_bytes FROM orders_maintenance.files").show(false)

    // 6. 查看表统计信息
    println("\n6. 查看表统计信息")
    spark.sql("SELECT * FROM orders_maintenance.entries").show(false)

    // 7. 数据文件优化 - 合并小文件
    println("\n7. 数据文件优化 - 合并小文件")
    val rewriteResult = spark.sql("""
      CALL spark_catalog.system.rewrite_data_files(
        table => 'orders_maintenance',
        options => map('target-file-size-bytes', '536870912')  -- 512MB
      )
    """)
    rewriteResult.show(false)

    // 8. 元数据文件优化 - 重写清单文件
    println("\n8. 元数据文件优化 - 重写清单文件")
    val manifestRewriteResult = spark.sql("""
      CALL spark_catalog.system.rewrite_manifests(
        table => 'orders_maintenance'
      )
    """)
    manifestRewriteResult.show(false)

    // 9. 清理过期快照 - 删除24小时前的快照
    println("\n9. 清理过期快照")
    val expireSnapshotsResult = spark.sql("""
      CALL spark_catalog.system.expire_snapshots(
        table => 'orders_maintenance',
        older_than => TIMESTAMP '2024-12-31 00:00:00',
        retain_last => 1
      )
    """)
    expireSnapshotsResult.show(false)

    // 10. 删除孤立文件
    println("\n10. 删除孤立文件")
    val removeOrphanFilesResult = spark.sql("""
      CALL spark_catalog.system.remove_orphan_files(
        table => 'orders_maintenance'
      )
    """)
    removeOrphanFilesResult.show(false)

    // 11. 压缩表元数据
    println("\n11. 压缩表元数据")
    val metadataCompressionResult = spark.sql("""
      CALL spark_catalog.system.compress_metadata(
        table => 'orders_maintenance'
      )
    """)
    metadataCompressionResult.show(false)

    // 12. 创建表快照标签
    println("\n12. 创建表快照标签")
    val latestSnapshotId = spark.sql("SELECT snapshot_id FROM orders_maintenance.history ORDER BY committed_at DESC LIMIT 1")
      .collect()(0).getLong(0)
    
    spark.sql(s"""
      ALTER TABLE orders_maintenance CREATE TAG 'weekly_backup' AS OF VERSION $latestSnapshotId
    """)
    
    println("创建快照标签 'weekly_backup'")

    // 13. 查看所有标签
    println("\n13. 查看所有标签")
    spark.sql("SELECT * FROM orders_maintenance.refs WHERE ref_type = 'TAG'").show(false)

    // 14. 创建分支用于测试
    println("\n14. 创建分支用于测试")
    spark.sql(s"""
      ALTER TABLE orders_maintenance CREATE BRANCH 'test_branch' AS OF VERSION $latestSnapshotId
    """)
    
    println("创建分支 'test_branch'")

    // 15. 在分支上进行操作
    println("\n15. 在分支上进行操作")
    // 切换到分支（这需要在查询时指定）
    spark.sql("""
      INSERT INTO orders_maintenance.branch_test_branch VALUES
      (2001, 'CUST999', 'Test Product', 99.99, DATE '2024-02-01', 'test')
    """)

    // 16. 查看分支信息
    println("\n16. 查看分支信息")
    spark.sql("SELECT * FROM orders_maintenance.refs WHERE ref_type = 'BRANCH'").show(false)

    // 17. 合并分支到主分支
    println("\n17. 合并分支到主分支")
    spark.sql("""
      CALL spark_catalog.system.cherrypick_snapshot(
        table => 'orders_maintenance',
        snapshot_id => (SELECT snapshot_id FROM orders_maintenance.refs WHERE name = 'test_branch')
      )
    """)

    // 18. 删除分支
    println("\n18. 删除分支")
    spark.sql("ALTER TABLE orders_maintenance DROP BRANCH 'test_branch'")

    // 19. 最终表状态检查
    println("\n19. 最终表状态检查")
    println("最终快照历史:")
    spark.sql("SELECT snapshot_id, operation, committed_at FROM orders_maintenance.history ORDER BY committed_at DESC").show(false)
    
    println("最终文件信息:")
    spark.sql("SELECT file_path, record_count, file_size_in_bytes FROM orders_maintenance.files").show(false)
    
    println("最终表数据:")
    spark.sql("SELECT * FROM orders_maintenance ORDER BY order_id").show(false)

    println("\n表维护操作示例完成!")
    spark.stop()
  }
}