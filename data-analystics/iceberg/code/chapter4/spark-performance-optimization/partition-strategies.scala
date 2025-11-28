// Spark Iceberg性能优化示例 - 分区策略优化
// 需要启动Spark Shell: spark-shell --packages org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:0.13.0

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.sql.Date

// 初始化Spark Session with Iceberg配置
val spark = SparkSession.builder()
  .appName("Iceberg Partition Strategies Optimization")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hadoop")
  .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
  .getOrCreate()

import spark.implicits._

// 1. 创建不同分区策略的测试表

// 1.1 Identity分区表
println("=== 创建Identity分区表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.sales_identity (
    id BIGINT,
    product STRING,
    region STRING,
    sale_date DATE,
    amount DOUBLE
  )
  USING iceberg
  PARTITIONED BY (region)
""")

// 1.2 时间分区表（按月）
println("=== 创建时间分区表（按月）===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.sales_time (
    id BIGINT,
    product STRING,
    region STRING,
    sale_date DATE,
    amount DOUBLE
  )
  USING iceberg
  PARTITIONED BY (months(sale_date))
""")

// 1.3 Bucket分区表
println("=== 创建Bucket分区表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.users_bucket (
    user_id BIGINT,
    name STRING,
    email STRING,
    signup_date DATE
  )
  USING iceberg
  PARTITIONED BY (bucket(16, user_id))
""")

// 1.4 Truncate分区表
println("=== 创建Truncate分区表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.products_truncate (
    product_id STRING,
    name STRING,
    category STRING,
    price DOUBLE
  )
  USING iceberg
  PARTITIONED BY (truncate(2, category))
""")

// 1.5 复合分区表
println("=== 创建复合分区表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.events_composite (
    event_id BIGINT,
    event_type STRING,
    user_id BIGINT,
    event_date DATE,
    details STRING
  )
  USING iceberg
  PARTITIONED BY (event_type, bucket(8, user_id), days(event_date))
""")

// 2. 插入测试数据

// 2.1 为Identity分区表插入数据
println("=== 为Identity分区表插入数据 ===")
val regions = Seq("North", "South", "East", "West")
val products = Seq("ProductA", "ProductB", "ProductC", "ProductD")
val salesData = for {
  region <- regions
  day <- 1 to 30
  product <- products.take(2) // 每个区域少量产品
} yield (scala.util.Random.nextLong(), product, region, Date.valueOf(s"2023-01-${"%02d".format(day)}"), scala.util.Random.nextDouble() * 1000)

val salesDf = spark.createDataset(salesData).toDF("id", "product", "region", "sale_date", "amount")
salesDf.writeTo("spark_catalog.default.sales_identity").append()

// 2.2 为时间分区表插入数据
println("=== 为时间分区表插入数据 ===")
val timeSalesData = for {
  day <- 1 to 30
  product <- products.take(2)
} yield (scala.util.Random.nextLong(), product, regions(scala.util.Random.nextInt(regions.length)), Date.valueOf(s"2023-01-${"%02d".format(day)}"), scala.util.Random.nextDouble() * 1000)

val timeSalesDf = spark.createDataset(timeSalesData).toDF("id", "product", "region", "sale_date", "amount")
timeSalesDf.writeTo("spark_catalog.default.sales_time").append()

// 2.3 为Bucket分区表插入数据
println("=== 为Bucket分区表插入数据 ===")
val usersData = for {
  i <- 1 to 1000
} yield (i.toLong, s"User$i", s"user$i@example.com", Date.valueOf(s"2023-01-${"%02d".format((i % 30) + 1)}"))

val usersDf = spark.createDataset(usersData).toDF("user_id", "name", "email", "signup_date")
usersDf.writeTo("spark_catalog.default.users_bucket").append()

// 2.4 为Truncate分区表插入数据
println("=== 为Truncate分区表插入数据 ===")
val categories = Seq("Electronics", "Clothing", "Books", "Home", "Sports")
val productsData = for {
  i <- 1 to 200
  category = categories(scala.util.Random.nextInt(categories.length))
} yield (f"P${"%04d".format(i)}", s"Product$i", category, scala.util.Random.nextDouble() * 500)

val productsDf = spark.createDataset(productsData).toDF("product_id", "name", "category", "price")
productsDf.writeTo("spark_catalog.default.products_truncate").append()

// 2.5 为复合分区表插入数据
println("=== 为复合分区表插入数据 ===")
val eventTypes = Seq("login", "purchase", "view", "search")
val eventsData = for {
  i <- 1 to 500
  eventType = eventTypes(scala.util.Random.nextInt(eventTypes.length))
  userId = scala.util.Random.nextLong().abs % 1000 + 1
} yield (i.toLong, eventType, userId, Date.valueOf(s"2023-01-${"%02d".format((i % 30) + 1)}"), s"Event details for event $i")

val eventsDf = spark.createDataset(eventsData).toDF("event_id", "event_type", "user_id", "event_date", "details")
eventsDf.writeTo("spark_catalog.default.events_composite").append()

// 3. 分析不同分区策略的效果

// 3.1 查看Identity分区表的分区信息
println("=== Identity分区表分区信息 ===")
spark.sql("""
  SELECT 
    partition.region,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size
  FROM spark_catalog.default.sales_identity.files
  GROUP BY partition.region
  ORDER BY total_size DESC
""").show()

// 3.2 查看时间分区表的分区信息
println("=== 时间分区表分区信息 ===")
spark.sql("""
  SELECT 
    partition.sale_date_month,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size
  FROM spark_catalog.default.sales_time.files
  GROUP BY partition.sale_date_month
  ORDER BY partition.sale_date_month
""").show()

// 3.3 查看Bucket分区表的分区信息
println("=== Bucket分区表分区信息 ===")
spark.sql("""
  SELECT 
    partition.user_id_bucket,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size
  FROM spark_catalog.default.users_bucket.files
  GROUP BY partition.user_id_bucket
  ORDER BY partition.user_id_bucket
""").show()

// 3.4 查看Truncate分区表的分区信息
println("=== Truncate分区表分区信息 ===")
spark.sql("""
  SELECT 
    partition.category_trunc,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size
  FROM spark_catalog.default.products_truncate.files
  GROUP BY partition.category_trunc
  ORDER BY total_size DESC
""").show()

// 3.5 查看复合分区表的分区信息
println("=== 复合分区表分区信息 ===")
spark.sql("""
  SELECT 
    partition.event_type,
    partition.user_id_bucket,
    partition.event_date_day,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size
  FROM spark_catalog.default.events_composite.files
  GROUP BY partition.event_type, partition.user_id_bucket, partition.event_date_day
  ORDER BY total_size DESC
  LIMIT 10
""").show()

// 4. 分区演化示例

// 4.1 为Identity分区表添加新的分区字段
println("=== 为Identity分区表添加日期分区 ===")
spark.sql("""
  ALTER TABLE spark_catalog.default.sales_identity 
  ADD PARTITION FIELD days(sale_date)
""")

// 4.2 查看分区演化后的效果
println("=== 分区演化后Identity表的分区信息 ===")
spark.sql("""
  SELECT * FROM spark_catalog.default.sales_identity.partitions
""").show(false)

// 4.3 替换分区字段
println("=== 替换分区字段 ===")
spark.sql("""
  ALTER TABLE spark_catalog.default.sales_identity 
  REPLACE PARTITION FIELD region 
  WITH truncate(2, product)
""")

// 5. 分区裁剪效果演示

// 5.1 查看查询计划以确认分区裁剪生效
println("=== 分区裁剪效果演示 ===")
spark.sql("""
  EXPLAIN SELECT * FROM spark_catalog.default.sales_identity 
  WHERE region = 'North' AND sale_date >= '2023-01-15'
""").show(false)

// 6. 最佳实践建议输出
println("=== 分区策略优化最佳实践 ===")
println("""
1. Identity分区：
   - 适用于低基数维度字段
   - 适合经常用于过滤的字段
   - 注意避免创建过多分区

2. 时间分区：
   - 适用于时间序列数据
   - 根据数据量选择合适粒度（年/月/日）
   - 有助于时间范围查询优化

3. Bucket分区：
   - 适用于高基数字段
   - 提供均匀的数据分布
   - 有助于连接操作性能

4. Truncate分区：
   - 适用于字符串或数值前缀分区
   - 减少分区数量
   - 适合层级分类数据

5. 复合分区：
   - 结合多种分区策略
   - 注意控制总分区数量
   - 考虑查询模式进行设计

6. 分区演化：
   - 支持动态调整分区策略
   - 无需重写现有数据
   - 根据业务发展调整分区方案
""")

// 7. 清理测试表
println("=== 清理测试表 ===")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.sales_identity")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.sales_time")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.users_bucket")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.products_truncate")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.events_composite")

println("分区策略优化示例完成！")