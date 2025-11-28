// Spark Scala 示例代码：Iceberg 表操作详解

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

// 创建 Spark Session 并配置 Iceberg
val spark = SparkSession.builder()
  .appName("Iceberg Table Operations Example")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hive")
  .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.local.type", "hadoop")
  .config("spark.sql.catalog.local.warehouse", "file:///tmp/iceberg/warehouse")
  .getOrCreate()

import spark.implicits._

println("=== Apache Iceberg 表操作示例 ===")

// 1. 创建数据库
spark.sql("CREATE DATABASE IF NOT EXISTS local.iceberg_db")

// 2. 创建基础表
println("\n--- 创建基础表 ---")
spark.sql("""
  CREATE TABLE IF NOT EXISTS local.iceberg_db.users (
    id BIGINT COMMENT '用户ID',
    name STRING COMMENT '用户名',
    age INT COMMENT '年龄',
    email STRING COMMENT '邮箱'
  ) USING iceberg
  TBLPROPERTIES ('format-version'='2')
""")

// 3. 插入初始数据
println("\n--- 插入初始数据 ---")
val usersData = Seq(
  (1L, "Alice", 25, "alice@example.com"),
  (2L, "Bob", 30, "bob@example.com"),
  (3L, "Charlie", 35, "charlie@example.com"),
  (4L, "David", 28, "david@example.com"),
  (5L, "Eve", 22, "eve@example.com")
).toDF("id", "name", "age", "email")

usersData.writeTo("local.iceberg_db.users").append()

// 4. 查询数据
println("\n--- 查询所有用户数据 ---")
spark.table("local.iceberg_db.users").show()

// 5. 条件查询
println("\n--- 查询年龄大于25的用户 ---")
spark.table("local.iceberg_db.users")
  .filter($"age" > 25)
  .show()

// 6. 聚合查询
println("\n--- 统计各年龄段用户数量 ---")
spark.table("local.iceberg_db.users")
  .groupBy($"age")
  .count()
  .orderBy($"age")
  .show()

// 7. 更新数据
println("\n--- 更新Alice的邮箱 ---")
spark.sql("""
  UPDATE local.iceberg_db.users 
  SET email = 'alice.updated@example.com' 
  WHERE name = 'Alice'
""")

println("更新后的Alice信息：")
spark.table("local.iceberg_db.users")
  .filter($"name" === "Alice")
  .show()

// 8. 删除数据
println("\n--- 删除年龄小于25的用户 ---")
spark.sql("""
  DELETE FROM local.iceberg_db.users 
  WHERE age < 25
""")

println("删除后的用户数据：")
spark.table("local.iceberg_db.users").show()

// 9. 创建分区表
println("\n--- 创建分区表 ---")
spark.sql("""
  CREATE TABLE IF NOT EXISTS local.iceberg_db.sales (
    id BIGINT,
    product STRING,
    amount DECIMAL(10,2),
    sale_date DATE
  ) USING iceberg
  PARTITIONED BY (sale_date)
  TBLPROPERTIES ('format-version'='2')
""")

// 10. 插入分区表数据
println("\n--- 插入分区表数据 ---")
val salesData = Seq(
  (1L, "Product A", 100.50, java.sql.Date.valueOf("2024-01-15")),
  (2L, "Product B", 200.75, java.sql.Date.valueOf("2024-01-16")),
  (3L, "Product A", 150.25, java.sql.Date.valueOf("2024-01-17")),
  (4L, "Product C", 300.00, java.sql.Date.valueOf("2024-01-15"))
).toDF("id", "product", "amount", "sale_date")

salesData.writeTo("local.iceberg_db.sales").append()

// 11. 分区查询
println("\n--- 查询2024-01-15的销售数据 ---")
spark.table("local.iceberg_db.sales")
  .filter($"sale_date" === "2024-01-15")
  .show()

// 12. 查看表结构
println("\n--- 查看users表结构 ---")
spark.sql("DESCRIBE local.iceberg_db.users").show(false)

// 13. 查看表属性
println("\n--- 查看users表属性 ---")
spark.sql("SHOW TBLPROPERTIES local.iceberg_db.users").show(false)

// 14. Schema演变 - 添加列
println("\n--- 添加phone列 ---")
spark.sql("""
  ALTER TABLE local.iceberg_db.users 
  ADD COLUMN phone STRING COMMENT '电话号码'
""")

// 15. 更新新增列的数据
println("\n--- 更新用户电话号码 ---")
spark.sql("""
  UPDATE local.iceberg_db.users 
  SET phone = '+1-555-0123' 
  WHERE name = 'Alice'
""")

println("更新电话号码后的用户数据：")
spark.table("local.iceberg_db.users").show()

// 16. 查看表的历史快照
println("\n--- 查看表的历史快照 ---")
spark.sql("""
  SELECT * FROM local.iceberg_db.users.history
""").show(false)

println("\n=== Iceberg 表操作示例完成 ===")

// 停止 Spark Session
spark.stop()