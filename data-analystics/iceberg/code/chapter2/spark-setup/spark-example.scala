// Spark Scala 示例代码：Iceberg 基本操作

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

// 创建 Spark Session 并配置 Iceberg
val spark = SparkSession.builder()
  .appName("Iceberg Spark Example")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hive")
  .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.local.type", "hadoop")
  .config("spark.sql.catalog.local.warehouse", "file:///tmp/iceberg/warehouse")
  .getOrCreate()

import spark.implicits._

// 创建示例数据
val users = Seq(
  (1L, "Alice", 25, "alice@example.com"),
  (2L, "Bob", 30, "bob@example.com"),
  (3L, "Charlie", 35, "charlie@example.com"),
  (4L, "David", 28, "david@example.com"),
  (5L, "Eve", 22, "eve@example.com")
).toDF("id", "name", "age", "email")

// 创建数据库
spark.sql("CREATE DATABASE IF NOT EXISTS local.iceberg_db")

// 创建 Iceberg 表
spark.sql("""
  CREATE TABLE IF NOT EXISTS local.iceberg_db.users (
    id BIGINT COMMENT '用户ID',
    name STRING COMMENT '用户名',
    age INT COMMENT '年龄',
    email STRING COMMENT '邮箱'
  ) USING iceberg
  PARTITIONED BY (age)
  TBLPROPERTIES ('format-version'='2')
""")

// 写入数据到 Iceberg 表
users.writeTo("local.iceberg_db.users").append()

// 查询数据
println("所有用户数据：")
spark.table("local.iceberg_db.users").show()

// 条件查询
println("年龄大于25的用户：")
spark.table("local.iceberg_db.users")
  .filter($"age" > 25)
  .show()

// 更新数据
spark.sql("""
  UPDATE local.iceberg_db.users 
  SET email = 'alice.new@example.com' 
  WHERE name = 'Alice'
""")

println("更新后的Alice信息：")
spark.table("local.iceberg_db.users")
  .filter($"name" === "Alice")
  .show()

// 删除数据
spark.sql("""
  DELETE FROM local.iceberg_db.users 
  WHERE age < 25
""")

println("删除年龄小于25后的数据：")
spark.table("local.iceberg_db.users").show()

// 查看表的历史快照
println("表的历史快照：")
spark.sql("""
  SELECT * FROM local.iceberg_db.users.history
""").show(false)

// 停止 Spark Session
spark.stop()