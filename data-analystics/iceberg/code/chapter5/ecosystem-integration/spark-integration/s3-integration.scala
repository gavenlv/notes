/*
 * Spark Iceberg 与 S3 集成示例
 * 
 * 本示例演示如何在 Spark 中配置 Iceberg 使用 S3 作为存储后端。
 */

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.FileSystem
import org.apache.hadoop.fs.Path

object SparkIcebergS3Integration {
  def main(args: Array[String]): Unit = {
    // 1. 创建 Spark Session 并配置 Iceberg 使用 S3
    val spark = SparkSession.builder()
      .appName("Spark Iceberg S3 Integration")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.s3_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.s3_catalog.type", "hadoop")
      .config("spark.sql.catalog.s3_catalog.warehouse", "s3a://my-iceberg-bucket/warehouse")
      // S3 访问配置
      .config("spark.hadoop.fs.s3a.access.key", "YOUR_AWS_ACCESS_KEY")
      .config("spark.hadoop.fs.s3a.secret.key", "YOUR_AWS_SECRET_KEY")
      .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
      .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
      .config("spark.hadoop.fs.s3a.path.style.access", "true")
      // 可选的 S3 性能优化配置
      .config("spark.hadoop.fs.s3a.connection.maximum", "100")
      .config("spark.hadoop.fs.s3a.block.size", "67108864") // 64MB
      .getOrCreate()

    import spark.implicits._

    println("=== Spark Iceberg S3 集成配置 ===")
    
    // 2. 使用 S3 Catalog
    spark.sql("USE s3_catalog")
    
    // 3. 创建数据库
    spark.sql("CREATE DATABASE IF NOT EXISTS s3_db")
    spark.sql("USE s3_db")
    
    // 4. 创建使用 S3 存储的 Iceberg 表
    println("创建使用 S3 存储的 Iceberg 表...")
    spark.sql("""
      CREATE TABLE IF NOT EXISTS s3_users (
        user_id BIGINT,
        username STRING,
        email STRING,
        registration_date DATE,
        last_login TIMESTAMP,
        is_premium BOOLEAN
      )
      USING iceberg
      PARTITIONED BY (months(registration_date))
      LOCATION 's3a://my-iceberg-bucket/tables/s3_users'
      TBLPROPERTIES (
        'write.format.default'='parquet',
        'write.target-file-size-bytes'='536870912', -- 512MB
        'write.parquet.compression-codec'='zstd',
        'write.distribution-mode'='hash'
      )
    """)
    
    // 5. 插入大量测试数据以演示 S3 性能
    println("插入测试数据...")
    val testData = (1 to 50000).map { i =>
      (
        i.toLong,
        s"user_$i",
        s"user$i@example.com",
        java.sql.Date.valueOf(s"2023-${(i % 12) + 1}-${(i % 28) + 1}"),
        java.sql.Timestamp.valueOf(s"2023-${(i % 12) + 1}-${(i % 28) + 1} ${(i % 24)}:${(i % 60)}:${(i % 60)}"),
        i % 100 == 0 // 每100个用户设为 premium
      )
    }.toDF("user_id", "username", "email", "registration_date", "last_login", "is_premium")
    
    testData.writeTo("s3_users").append()
    
    // 6. 查询数据
    println("查询 S3 上的用户数据:")
    spark.table("s3_users").show(10, false)
    
    // 7. 聚合查询
    println("用户注册统计:")
    spark.sql("""
      SELECT 
        DATE_TRUNC('month', registration_date) as registration_month,
        COUNT(*) as user_count,
        SUM(CASE WHEN is_premium THEN 1 ELSE 0 END) as premium_count
      FROM s3_users
      GROUP BY DATE_TRUNC('month', registration_date)
      ORDER BY registration_month
    """).show(false)
    
    // 8. 分区裁剪查询
    println("特定月份注册的用户:")
    spark.sql("""
      SELECT *
      FROM s3_users
      WHERE registration_date >= DATE '2023-06-01' 
      AND registration_date < DATE '2023-07-01'
    """).show(10, false)
    
    // 9. 创建带有复杂分区的表
    println("创建带有复杂分区的表...")
    spark.sql("""
      CREATE TABLE IF NOT EXISTS s3_events (
        event_id BIGINT,
        user_id BIGINT,
        event_type STRING,
        event_timestamp TIMESTAMP,
        payload STRING
      )
      USING iceberg
      PARTITIONED BY (event_type, days(event_timestamp))
      LOCATION 's3a://my-iceberg-bucket/tables/s3_events'
      TBLPROPERTIES (
        'write.format.default'='parquet',
        'write.target-file-size-bytes'='268435456' -- 256MB
      )
    """)
    
    // 10. 插入事件数据
    println("插入事件数据...")
    val eventTypes = Array("login", "purchase", "view", "search")
    val eventData = (1 to 100000).map { i =>
      (
        i.toLong,
        ((i - 1) % 50000) + 1, // user_id
        eventTypes((i - 1) % eventTypes.length),
        java.sql.Timestamp.valueOf(s"2023-${((i - 1) % 12) + 1}-${((i - 1) % 28) + 1} ${(i % 24)}:${(i % 60)}:${(i % 60)}"),
        s"Event payload for event $i"
      )
    }.toDF("event_id", "user_id", "event_type", "event_timestamp", "payload")
    
    eventData.writeTo("s3_events").append()
    
    // 11. 复杂查询
    println("事件统计分析:")
    spark.sql("""
      SELECT 
        event_type,
        DATE_TRUNC('day', event_timestamp) as event_day,
        COUNT(*) as event_count
      FROM s3_events
      WHERE event_timestamp >= TIMESTAMP '2023-06-01 00:00:00'
      GROUP BY event_type, DATE_TRUNC('day', event_timestamp)
      ORDER BY event_day, event_type
    """).show(20, false)
    
    // 12. 查看 S3 上的表元数据
    println("查看 S3 表的文件信息:")
    spark.sql("""
      SELECT 
        partition.event_type,
        partition.event_timestamp_day,
        COUNT(*) as file_count,
        SUM(file_size_in_bytes)/1024/1024 as total_size_mb
      FROM s3_events.files
      GROUP BY partition.event_type, partition.event_timestamp_day
      ORDER BY total_size_mb DESC
    """).show(false)
    
    // 13. S3 性能优化配置演示
    println("配置 S3 性能优化参数...")
    
    // 设置更大的文件大小以减少 S3 请求
    spark.sql("ALTER TABLE s3_users SET TBLPROPERTIES ('write.target-file-size-bytes'='1073741824')") // 1GB
    
    // 启用文件合并
    spark.sql("ALTER TABLE s3_users SET TBLPROPERTIES ('write.metadata.delete-after-commit.enabled'='true')")
    
    println("优化后的表属性:")
    spark.sql("SHOW TBLPROPERTIES s3_users").show(false)
    
    // 14. S3 成本优化建议
    println("S3 成本优化建议:")
    println("1. 使用 S3 Intelligent-Tiering 存储类别")
    println("2. 启用 S3 生命周期策略，将旧数据移至 Glacier")
    println("3. 使用 S3 Select 减少数据传输")
    println("4. 合理设置文件大小以平衡读写性能和请求成本")
    
    // 15. 清理资源
    println("清理测试表...")
    spark.sql("DROP TABLE IF EXISTS s3_users")
    spark.sql("DROP TABLE IF EXISTS s3_events")
    spark.sql("DROP DATABASE IF EXISTS s3_db")
    
    spark.stop()
    println("Spark Iceberg S3 集成示例完成!")
  }
}