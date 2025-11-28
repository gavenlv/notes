// Spark Iceberg性能优化示例 - 缓存配置优化
// 需要启动Spark Shell: spark-shell --packages org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:0.13.0

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.storage.StorageLevel
import java.sql.Date

// 初始化Spark Session with Iceberg配置和缓存优化参数
val spark = SparkSession.builder()
  .appName("Iceberg Caching Configuration Optimization")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hadoop")
  .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
  // Iceberg元数据缓存配置
  .config("spark.sql.catalog.spark_catalog.cache-enabled", "true")
  .config("spark.sql.catalog.spark_catalog.cache.expiration-interval-ms", "300000") // 5分钟
  .config("spark.sql.catalog.spark_catalog.cache.max-entries", "1000")
  // 文件IO缓存配置
  .config("spark.sql.iceberg.io.cache.enabled", "true")
  .config("spark.sql.iceberg.io.cache.expiration-interval-ms", "300000") // 5分钟
  // Spark SQL缓存配置
  .config("spark.sql.inMemoryColumnarStorage.compressed", "true")
  .config("spark.sql.inMemoryColumnarStorage.batchSize", "10000")
  .getOrCreate()

import spark.implicits._

// 1. 创建测试表

println("=== 创建测试表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.cache_test (
    id BIGINT,
    name STRING,
    category STRING,
    price DOUBLE,
    created_date DATE,
    description STRING
  )
  USING iceberg
  PARTITIONED BY (category, months(created_date))
  TBLPROPERTIES (
    'write.format.default'='parquet',
    'write.target-file-size-bytes'='536870912'  -- 512MB
  )
""")

// 2. 插入测试数据

println("=== 插入测试数据 ===")
val categories = Seq("Electronics", "Clothing", "Books", "Home", "Sports", "Toys", "Beauty", "Food")
val testData = for {
  i <- 1 to 50000 // 5万条记录
  categoryId = scala.util.Random.nextInt(categories.length)
} yield (
  i.toLong,
  s"Product_$i",
  categories(categoryId),
  scala.util.Random.nextDouble() * 1000,
  Date.valueOf(s"2023-${"%02d".format(scala.util.Random.nextInt(12) + 1)}-${"%02d".format(scala.util.Random.nextInt(28) + 1)}"),
  s"Detailed description for product $i with additional information to make the record larger and more realistic for testing cache performance"
)

val testDf = spark.createDataset(testData).toDF("id", "name", "category", "price", "created_date", "description")
testDf.writeTo("spark_catalog.default.cache_test").append()

// 3. Iceberg元数据缓存演示

println("=== Iceberg元数据缓存演示 ===")

// 3.1 首次查询（无缓存）
println("首次查询（无缓存）:")
val firstQueryStart = System.currentTimeMillis()
val firstQueryResult = spark.sql("""
  SELECT category, COUNT(*) as count, AVG(price) as avg_price
  FROM spark_catalog.default.cache_test
  GROUP BY category
  ORDER BY count DESC
""").collect()
val firstQueryEnd = System.currentTimeMillis()
println(s"首次查询耗时: ${firstQueryEnd - firstQueryStart} ms")

// 3.2 第二次查询（利用元数据缓存）
println("第二次查询（利用元数据缓存）:")
val secondQueryStart = System.currentTimeMillis()
val secondQueryResult = spark.sql("""
  SELECT category, COUNT(*) as count, AVG(price) as avg_price
  FROM spark_catalog.default.cache_test
  GROUP BY category
  ORDER BY count DESC
""").collect()
val secondQueryEnd = System.currentTimeMillis()
println(s"第二次查询耗时: ${secondQueryEnd - secondQueryStart} ms")

// 4. Spark DataFrame缓存演示

println("=== Spark DataFrame缓存演示 ===")

// 4.1 创建DataFrame并缓存
println("创建并缓存DataFrame:")
val df = spark.table("spark_catalog.default.cache_test")
  .filter($"price" > 100)
  .select("id", "name", "category", "price")

val cacheStart = System.currentTimeMillis()
df.persist(StorageLevel.MEMORY_AND_DISK_SER)
val cacheEnd = System.currentTimeMillis()
println(s"缓存DataFrame耗时: ${cacheEnd - cacheStart} ms")

// 4.2 首次使用缓存的DataFrame
println("首次使用缓存的DataFrame:")
val cachedQuery1Start = System.currentTimeMillis()
val cachedResult1 = df.groupBy("category").agg(count("*").as("count"), avg("price").as("avg_price")).collect()
val cachedQuery1End = System.currentTimeMillis()
println(s"首次使用缓存查询耗时: ${cachedQuery1End - cachedQuery1Start} ms")

// 4.3 第二次使用缓存的DataFrame
println("第二次使用缓存的DataFrame:")
val cachedQuery2Start = System.currentTimeMillis()
val cachedResult2 = df.filter($"category" === "Electronics").collect()
val cachedQuery2End = System.currentTimeMillis()
println(s"第二次使用缓存查询耗时: ${cachedQuery2End - cachedQuery2Start} ms")

// 5. 分区缓存优化

println("=== 分区缓存优化 ===")

// 5.1 缓存特定分区数据
println("缓存特定分区数据:")
val partitionDf = spark.table("spark_catalog.default.cache_test")
  .filter($"category" === "Electronics" && $"created_date".between(Date.valueOf("2023-01-01"), Date.valueOf("2023-03-31")))

val partitionCacheStart = System.currentTimeMillis()
partitionDf.persist(StorageLevel.MEMORY_ONLY)
val partitionCacheEnd = System.currentTimeMillis()
println(s"缓存分区数据耗时: ${partitionCacheEnd - partitionCacheStart} ms")

// 5.2 查询缓存的分区数据
println("查询缓存的分区数据:")
val partitionQueryStart = System.currentTimeMillis()
val partitionResult = partitionDf.agg(count("*").as("count"), avg("price").as("avg_price")).collect()
val partitionQueryEnd = System.currentTimeMillis()
println(s"查询缓存分区数据耗时: ${partitionQueryEnd - partitionQueryStart} ms")

// 6. 自定义缓存策略

println("=== 自定义缓存策略 ===")

// 6.1 创建视图并缓存
println("创建并缓存视图:")
spark.sql("""
  CREATE OR REPLACE TEMPORARY VIEW electronics_view AS
  SELECT id, name, price, created_date
  FROM spark_catalog.default.cache_test
  WHERE category = 'Electronics'
""")

val viewCacheStart = System.currentTimeMillis()
spark.catalog.cacheTable("electronics_view")
val viewCacheEnd = System.currentTimeMillis()
println(s"缓存视图耗时: ${viewCacheEnd - viewCacheStart} ms")

// 6.2 查询缓存的视图
println("查询缓存的视图:")
val viewQueryStart = System.currentTimeMillis()
val viewResult = spark.sql("""
  SELECT DATE_TRUNC('month', created_date) as month, 
         COUNT(*) as count, 
         AVG(price) as avg_price
  FROM electronics_view
  GROUP BY DATE_TRUNC('month', created_date)
  ORDER BY month
""").collect()
val viewQueryEnd = System.currentTimeMillis()
println(s"查询缓存视图耗时: ${viewQueryEnd - viewQueryStart} ms")

// 7. 缓存性能对比

println("=== 缓存性能对比 ===")

// 7.1 未缓存查询
println("未缓存查询:")
val uncachedQueryStart = System.currentTimeMillis()
val uncachedResult = spark.sql("""
  SELECT category, 
         DATE_TRUNC('month', created_date) as month,
         COUNT(*) as count, 
         AVG(price) as avg_price
  FROM spark_catalog.default.cache_test
  WHERE price > 50
  GROUP BY category, DATE_TRUNC('month', created_date)
  ORDER BY category, month
""").collect()
val uncachedQueryEnd = System.currentTimeMillis()
println(s"未缓存查询耗时: ${uncachedQueryEnd - uncachedQueryStart} ms")

// 7.2 缓存后查询
println("缓存后查询:")
val cachedTable = spark.table("spark_catalog.default.cache_test")
  .filter($"price" > 50)
  .persist(StorageLevel.MEMORY_AND_DISK_SER)

val cachedQueryStart = System.currentTimeMillis()
val cachedQueryResult = cachedTable.groupBy($"category", date_trunc("month", $"created_date").as("month"))
  .agg(count("*").as("count"), avg("price").as("avg_price"))
  .orderBy($"category", $"month")
  .collect()
val cachedQueryEnd = System.currentTimeMillis()
println(s"缓存后查询耗时: ${cachedQueryEnd - cachedQueryStart} ms")

// 8. 缓存监控和管理

println("=== 缓存监控和管理 ===")

// 8.1 查看缓存状态
println("当前缓存状态:")
spark.sharedState.cacheManager.getCachedData.foreach { cachedData =>
  val tableName = cachedData.cachedRepresentation.queryExecution.analyzed.toString
  val storageLevel = cachedData.cachedRepresentation.cacheBuilder.storageLevel
  val cachedRDD = cachedData.cachedRepresentation.cachedRDD
  println(s"表: $tableName")
  println(s"存储级别: $storageLevel")
  println(s"缓存内存大小: ${cachedRDD.map(_.memoryStoreMemSize).sum} bytes")
  println(s"缓存磁盘大小: ${cachedRDD.map(_.diskStoreMemSize).sum} bytes")
  println("---")
}

// 8.2 查看Iceberg表的缓存信息
println("Iceberg表缓存信息:")
spark.sql("""
  SELECT 
    table_name,
    last_cached_at,
    entry_count
  FROM spark_catalog.system.cache_entries
""").show(false)

// 9. 缓存配置最佳实践

println("=== 缓存配置最佳实践 ===")
println("""
1. Iceberg元数据缓存配置：
   - 启用元数据缓存：spark.sql.catalog.spark_catalog.cache-enabled=true
   - 设置合理的过期时间：300000ms（5分钟）
   - 控制缓存条目数量：根据集群资源设置适当值

2. Spark SQL缓存配置：
   - 启用列式存储压缩：spark.sql.inMemoryColumnarStorage.compressed=true
   - 设置合适的批处理大小：spark.sql.inMemoryColumnarStorage.batchSize=10000

3. 存储级别选择：
   - MEMORY_ONLY：高性能，但可能因内存不足而丢失
   - MEMORY_AND_DISK：平衡性能和可靠性
   - MEMORY_AND_DISK_SER：节省内存但增加CPU开销

4. 缓存策略：
   - 频繁访问的数据应优先缓存
   - 大表的热点分区可单独缓存
   - 定期清理不再使用的缓存

5. 监控和调优：
   - 监控缓存命中率
   - 调整缓存大小和过期时间
   - 根据查询模式优化缓存策略
""")

// 10. 清理资源

println("=== 清理资源 ===")

// 取消缓存
spark.catalog.uncacheTable("electronics_view")
df.unpersist()
partitionDf.unpersist()
cachedTable.unpersist()

// 清理测试表
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.cache_test")

println("缓存配置优化示例完成！")