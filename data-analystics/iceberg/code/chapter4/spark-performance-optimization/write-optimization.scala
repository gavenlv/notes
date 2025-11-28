// Spark Iceberg性能优化示例 - 写入性能优化
// 需要启动Spark Shell: spark-shell --packages org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:0.13.0

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.sql.Date

// 初始化Spark Session with Iceberg配置和性能优化参数
val spark = SparkSession.builder()
  .appName("Iceberg Write Performance Optimization")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hadoop")
  .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
  // 启用自适应查询执行
  .config("spark.sql.adaptive.enabled", "true")
  .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
  .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")
  // 设置shuffle分区数
  .config("spark.sql.shuffle.partitions", "200")
  // Iceberg写入优化配置
  .config("spark.sql.iceberg.write.target-file-size-bytes", "536870912") // 512MB
  .config("spark.sql.iceberg.write.distribution-mode", "hash")
  .getOrCreate()

import spark.implicits._

// 1. 创建测试表

println("=== 创建测试表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.write_performance_test (
    id BIGINT,
    name STRING,
    category STRING,
    price DOUBLE,
    created_date DATE,
    details STRING
  )
  USING iceberg
  PARTITIONED BY (category, days(created_date))
  TBLPROPERTIES (
    'write.format.default'='parquet',
    'write.target-file-size-bytes'='536870912',  -- 512MB
    'write.distribution-mode'='hash'
  )
""")

// 2. 生成测试数据集

println("=== 生成测试数据 ===")
val categories = Seq("Electronics", "Clothing", "Books", "Home", "Sports", "Toys", "Beauty", "Food")
val startDate = Date.valueOf("2023-01-01")
val endDate = Date.valueOf("2023-12-31")

def randomDate(start: Date, end: Date): Date = {
  val random = scala.util.Random
  val startMillis = start.getTime
  val endMillis = end.getTime
  val randomMillis = startMillis + random.nextLong() % (endMillis - startMillis)
  new Date(randomMillis)
}

def generateTestData(numRecords: Int): Seq[(Long, String, String, Double, Date, String)] = {
  val random = scala.util.Random
  (1 to numRecords).map { i =>
    val categoryId = random.nextInt(categories.length)
    val categoryName = categories(categoryId)
    (
      i.toLong,
      s"Product_$i",
      categoryName,
      random.nextDouble() * 1000,
      randomDate(startDate, endDate),
      s"Detailed description for product $i with additional information to make the record larger and more realistic for testing purposes"
    )
  }
}

// 3. 写入性能优化示例

// 3.1 默认写入方式
println("=== 默认写入方式 ===")
val defaultData = generateTestData(50000) // 5万条记录
val defaultDf = spark.createDataset(defaultData).toDF("id", "name", "category", "price", "created_date", "details")

val defaultStartTime = System.currentTimeMillis()
defaultDf.writeTo("spark_catalog.default.write_performance_test").append()
val defaultEndTime = System.currentTimeMillis()

println(s"默认写入耗时: ${defaultEndTime - defaultStartTime} ms")

// 3.2 优化写入方式 - 调整分区数
println("=== 优化写入方式 - 调整分区数 ===")
val repartitionedDf = defaultDf.repartition(200, $"category", $"created_date")

val repartitionStartTime = System.currentTimeMillis()
repartitionedDf.writeTo("spark_catalog.default.write_performance_test").append()
val repartitionEndTime = System.currentTimeMillis()

println(s"重新分区写入耗时: ${repartitionEndTime - repartitionStartTime} ms")

// 3.3 优化写入方式 - 批量写入
println("=== 优化写入方式 - 批量写入 ===")
val batchSize = 10000
val batchData = generateTestData(100000) // 10万条记录

val batchStartTime = System.currentTimeMillis()
batchData.grouped(batchSize).foreach { batch =>
  val batchDf = spark.createDataset(batch).toDF("id", "name", "category", "price", "created_date", "details")
  batchDf.writeTo("spark_catalog.default.write_performance_test").append()
}
val batchEndTime = System.currentTimeMillis()

println(s"批量写入耗时: ${batchEndTime - batchStartTime} ms")

// 4. 写入模式优化示例

// 4.1 创建Copy-on-Write模式表
println("=== 创建Copy-on-Write模式表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.cow_test (
    id BIGINT,
    name STRING,
    value DOUBLE
  )
  USING iceberg
  TBLPROPERTIES (
    'write.update.mode'='copy-on-write',
    'write.delete.mode'='copy-on-write',
    'write.merge.mode'='copy-on-write'
  )
""")

// 4.2 创建Merge-on-Read模式表
println("=== 创建Merge-on-Read模式表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.mor_test (
    id BIGINT,
    name STRING,
    value DOUBLE
  )
  USING iceberg
  TBLPROPERTIES (
    'write.update.mode'='merge-on-read',
    'write.delete.mode'='merge-on-read',
    'write.merge.mode'='merge-on-read'
  )
""")

// 4.3 测试不同写入模式的性能
println("=== 测试不同写入模式的性能 ===")

val testData = (1 to 20000).map(i => (i.toLong, s"Name_$i", scala.util.Random.nextDouble() * 1000))

// 测试Copy-on-Write模式
val cowDf = spark.createDataset(testData).toDF("id", "name", "value")
val cowStartTime = System.currentTimeMillis()
cowDf.writeTo("spark_catalog.default.cow_test").append()
val cowEndTime = System.currentTimeMillis()
println(s"Copy-on-Write模式写入耗时: ${cowEndTime - cowStartTime} ms")

// 测试Merge-on-Read模式
val morDf = spark.createDataset(testData).toDF("id", "name", "value")
val morStartTime = System.currentTimeMillis()
morDf.writeTo("spark_catalog.default.mor_test").append()
val morEndTime = System.currentTimeMillis()
println(s"Merge-on-Read模式写入耗时: ${morEndTime - morStartTime} ms")

// 5. 并行度优化示例

println("=== 并行度优化示例 ===")

// 获取当前默认并行度
val defaultParallelism = spark.sparkContext.defaultParallelism
println(s"默认并行度: $defaultParallelism")

// 调整并行度进行写入
spark.conf.set("spark.sql.shuffle.partitions", "400") // 增加shuffle分区数

val parallelData = generateTestData(50000)
val parallelDf = spark.createDataset(parallelData).toDF("id", "name", "category", "price", "created_date", "details")

val parallelStartTime = System.currentTimeMillis()
parallelDf.writeTo("spark_catalog.default.write_performance_test").append()
val parallelEndTime = System.currentTimeMillis()

println(s"高并行度写入耗时: ${parallelEndTime - parallelStartTime} ms")

// 6. 文件格式和压缩优化

println("=== 文件格式和压缩优化 ===")

// 6.1 创建Parquet格式表（默认）
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.parquet_test (
    id BIGINT,
    name STRING,
    data STRING
  )
  USING iceberg
  TBLPROPERTIES (
    'write.format.default'='parquet',
    'write.parquet.compression-codec'='zstd'
  )
""")

// 6.2 创建ORC格式表
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.orc_test (
    id BIGINT,
    name STRING,
    data STRING
  )
  USING iceberg
  TBLPROPERTIES (
    'write.format.default'='orc',
    'write.orc.compression-codec'='zstd'
  )
""")

// 测试不同格式的写入性能
val formatTestData = (1 to 30000).map(i => (i.toLong, s"Name_$i", s"Data content for record $i which contains more text to make the records larger for testing compression effectiveness"))

// 测试Parquet格式
val parquetDf = spark.createDataset(formatTestData).toDF("id", "name", "data")
val parquetStartTime = System.currentTimeMillis()
parquetDf.writeTo("spark_catalog.default.parquet_test").append()
val parquetEndTime = System.currentTimeMillis()
println(s"Parquet格式写入耗时: ${parquetEndTime - parquetStartTime} ms")

// 测试ORC格式
val orcDf = spark.createDataset(formatTestData).toDF("id", "name", "data")
val orcStartTime = System.currentTimeMillis()
orcDf.writeTo("spark_catalog.default.orc_test").append()
val orcEndTime = System.currentTimeMillis()
println(s"ORC格式写入耗时: ${orcEndTime - orcStartTime} ms")

// 7. 写入性能监控

println("=== 写入性能监控 ===")

// 查看表的历史记录和文件信息
println("表历史记录:")
spark.sql("""
  SELECT 
    made_current_at,
    snapshot_id,
    parent_id,
    operation,
    summary
  FROM spark_catalog.default.write_performance_test.history
  ORDER BY made_current_at DESC
  LIMIT 5
""").show(false)

println("表文件统计:")
spark.sql("""
  SELECT 
    COUNT(*) as total_files,
    AVG(file_size_in_bytes) as avg_file_size,
    MAX(file_size_in_bytes) as max_file_size,
    MIN(file_size_in_bytes) as min_file_size
  FROM spark_catalog.default.write_performance_test.files
""").show()

// 8. 最佳实践建议输出

println("=== 写入性能优化最佳实践 ===")
println("""
1. 批处理大小优化：
   - 设置合适的目标文件大小（通常512MB-1GB）
   - 避免生成过多小文件
   - 根据集群资源调整批处理大小

2. 并行度调优：
   - 根据数据量和集群资源设置合适的分区数
   - 启用自适应查询执行（AQE）
   - 合理配置shuffle分区数

3. 写入模式选择：
   - Copy-on-Write：适合读多写少场景，提供更好的查询性能
   - Merge-on-Read：适合写多读少场景，提供更好的写入性能

4. 文件格式和压缩：
   - Parquet：适合大多数分析场景
   - ORC：在某些场景下可能有更好的压缩比
   - 压缩编解码器选择：ZSTD提供良好的压缩比和性能平衡

5. 分区策略：
   - 合理设计分区字段以支持查询模式
   - 避免创建过多分区
   - 使用分区演化功能适应业务变化

6. 资源配置：
   - 合理分配执行器内存和核心数
   - 根据工作负载特性调整Spark配置
   - 监控和调优JVM垃圾回收

7. 性能监控：
   - 定期检查文件大小分布
   - 监控写入操作的性能指标
   - 分析历史记录以识别性能趋势
""")

// 9. 清理测试表
println("=== 清理测试表 ===")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.write_performance_test")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.cow_test")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.mor_test")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.parquet_test")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.orc_test")

println("写入性能优化示例完成！")