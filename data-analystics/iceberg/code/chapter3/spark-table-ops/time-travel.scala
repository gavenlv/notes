// Spark Scala 示例代码：Iceberg 时间旅行功能

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

// 创建 Spark Session 并配置 Iceberg
val spark = SparkSession.builder()
  .appName("Iceberg Time Travel Example")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hive")
  .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.local.type", "hadoop")
  .config("spark.sql.catalog.local.warehouse", "file:///tmp/iceberg/warehouse")
  .getOrCreate()

import spark.implicits._

println("=== Apache Iceberg 时间旅行功能示例 ===")

// 1. 创建数据库
spark.sql("CREATE DATABASE IF NOT EXISTS local.iceberg_db")

// 2. 创建用于时间旅行演示的表
println("\n--- 创建用户表 ---")
spark.sql("""
  CREATE TABLE IF NOT EXISTS local.iceberg_db.timetravel_users (
    id BIGINT COMMENT '用户ID',
    name STRING COMMENT '用户名',
    age INT COMMENT '年龄',
    email STRING COMMENT '邮箱'
  ) USING iceberg
  TBLPROPERTIES ('format-version'='2')
""")

// 3. 插入初始数据 (快照 1)
println("\n--- 插入初始数据 (快照 1) ---")
val initialData = Seq(
  (1L, "Alice", 25, "alice@example.com"),
  (2L, "Bob", 30, "bob@example.com")
).toDF("id", "name", "age", "email")

initialData.writeTo("local.iceberg_db.timetravel_users").append()

println("初始数据：")
spark.table("local.iceberg_db.timetravel_users").show()

// 4. 获取当前快照ID
println("\n--- 当前快照信息 ---")
val snapshot1 = spark.sql("""
  SELECT snapshot_id, committed_at FROM local.iceberg_db.timetravel_users.history
""").collect()(0)
val snapshotId1 = snapshot1.getLong(0)
val timestamp1 = snapshot1.getTimestamp(1)
println(s"快照ID: $snapshotId1, 时间戳: $timestamp1")

// 5. 更新数据 (快照 2)
println("\n--- 更新数据 (快照 2) ---")
val newData = Seq(
  (3L, "Charlie", 35, "charlie@example.com"),
  (4L, "David", 28, "david@example.com")
).toDF("id", "name", "age", "email")

newData.writeTo("local.iceberg_db.timetravel_users").append()

println("添加新用户后：")
spark.table("local.iceberg_db.timetravel_users").show()

// 6. 获取当前快照ID
println("\n--- 当前快照信息 ---")
val snapshots = spark.sql("""
  SELECT snapshot_id, committed_at FROM local.iceberg_db.timetravel_users.history
""").collect()
val snapshotId2 = snapshots(1).getLong(0)
val timestamp2 = snapshots(1).getTimestamp(1)
println(s"快照ID: $snapshotId2, 时间戳: $timestamp2")

// 7. 更新现有用户数据 (快照 3)
println("\n--- 更新现有用户数据 (快照 3) ---")
spark.sql("""
  UPDATE local.iceberg_db.timetravel_users 
  SET email = 'alice.updated@example.com' 
  WHERE name = 'Alice'
""")

println("更新Alice邮箱后：")
spark.table("local.iceberg_db.timetravel_users").show()

// 8. 获取当前快照ID
println("\n--- 当前快照信息 ---")
val snapshot3 = spark.sql("""
  SELECT snapshot_id, committed_at FROM local.iceberg_db.timetravel_users.history
""").collect()(2)
val snapshotId3 = snapshot3.getLong(0)
val timestamp3 = snapshot3.getTimestamp(1)
println(s"快照ID: $snapshotId3, 时间戳: $timestamp3")

// 9. 时间旅行 - 查询快照1的数据
println(s"\n--- 时间旅行: 查询快照 $snapshotId1 的数据 ---")
spark.read
  .option("snapshot-id", snapshotId1)
  .table("local.iceberg_db.timetravel_users")
  .show()

// 10. 时间旅行 - 查询快照2的数据
println(s"\n--- 时间旅行: 查询快照 $snapshotId2 的数据 ---")
spark.read
  .option("snapshot-id", snapshotId2)
  .table("local.iceberg_db.timetravel_users")
  .show()

// 11. 时间旅行 - 基于时间戳查询
println(s"\n--- 时间旅行: 查询时间戳 $timestamp1 的数据 ---")
spark.read
  .option("as-of-timestamp", timestamp1.getTime)
  .table("local.iceberg_db.timetravel_users")
  .show()

// 12. 删除数据 (快照 4)
println("\n--- 删除年龄小于30的用户 (快照 4) ---")
spark.sql("""
  DELETE FROM local.iceberg_db.timetravel_users 
  WHERE age < 30
""")

println("删除后剩余用户：")
spark.table("local.iceberg_db.timetravel_users").show()

// 13. 查看所有快照历史
println("\n--- 所有快照历史 ---")
spark.sql("""
  SELECT * FROM local.iceberg_db.timetravel_users.history
""").show(false)

// 14. 数据恢复 - 恢复到快照2
println(s"\n--- 数据恢复: 恢复到快照 $snapshotId2 的状态 ---")
// 注意：实际生产环境中，数据恢复通常通过创建新表或使用存储过程实现
// 这里仅演示如何查询历史数据
println(s"快照 $snapshotId2 的数据：")
spark.read
  .option("snapshot-id", snapshotId2)
  .table("local.iceberg_db.timetravel_users")
  .show()

println("\n=== Iceberg 时间旅行功能示例完成 ===")

// 停止 Spark Session
spark.stop()