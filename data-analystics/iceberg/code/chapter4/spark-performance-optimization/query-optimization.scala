// Spark Iceberg性能优化示例 - 查询优化技术
// 需要启动Spark Shell: spark-shell --packages org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:0.13.0

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.sql.Date

// 初始化Spark Session with Iceberg配置
val spark = SparkSession.builder()
  .appName("Iceberg Query Optimization")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hadoop")
  .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
  .getOrCreate()

import spark.implicits._

// 1. 创建带布隆过滤器的测试表

println("=== 创建带布隆过滤器的用户表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.users_optimized (
    user_id BIGINT,
    email STRING,
    name STRING,
    signup_date DATE,
    status STRING
  )
  USING iceberg
  TBLPROPERTIES (
    'write.metadata.metrics.column.user_id'='truncate(16)',
    'write.metadata.metrics.column.email'='full',
    'write.metadata.metrics.mode'='full'
  )
""")

// 2. 插入大量测试数据以演示优化效果

println("=== 插入测试数据 ===")
val userData = for {
  i <- 1 to 50000 // 插入5万条记录
} yield (
  i.toLong, 
  s"user${i}@example.com", 
  s"User Name ${i}", 
  Date.valueOf(s"2023-${"%02d".format((i % 12) + 1)}-${"%02d".format((i % 28) + 1)}"),
  if (i % 100 == 0) "premium" else "standard"
)

val userDf = spark.createDataset(userData).toDF("user_id", "email", "name", "signup_date", "status")
userDf.writeTo("spark_catalog.default.users_optimized").append()

println("=== 插入更多数据以创建多个文件 ===")
// 再插入几批数据以创建多个文件
for (batch <- 1 to 3) {
  val additionalData = for {
    i <- 1 to 10000
  } yield (
    (50000 + (batch - 1) * 10000 + i).toLong,
    s"user${50000 + (batch - 1) * 10000 + i}@example.com",
    s"User Name ${50000 + (batch - 1) * 10000 + i}",
    Date.valueOf(s"2023-${"%02d".format(((batch - 1) * 4 + i % 12) + 1)}-${"%02d".format((i % 28) + 1)}"),
    if (i % 75 == 0) "premium" else "standard"
  )
  
  val additionalDf = spark.createDataset(additionalData).toDF("user_id", "email", "name", "signup_date", "status")
  additionalDf.writeTo("spark_catalog.default.users_optimized").append()
  println(s"Inserted batch $batch")
}

// 3. 创建分区表以演示分区裁剪

println("=== 创建分区表以演示分区裁剪 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.events_partitioned (
    event_id BIGINT,
    user_id BIGINT,
    event_type STRING,
    event_date DATE,
    details STRING
  )
  USING iceberg
  PARTITIONED BY (event_type, months(event_date))
""")

val eventTypes = Seq("login", "purchase", "view", "search", "logout")
val eventsData = for {
  i <- 1 to 100000 // 10万条事件记录
  eventType = eventTypes(scala.util.Random.nextInt(eventTypes.length))
} yield (
  i.toLong,
  scala.util.Random.nextLong().abs % 60000 + 1,
  eventType,
  Date.valueOf(s"2023-${"%02d".format((i % 12) + 1)}-${"%02d".format((i % 28) + 1)}"),
  s"Event details for event $i"
)

val eventsDf = spark.createDataset(eventsData).toDF("event_id", "user_id", "event_type", "event_date", "details")
eventsDf.writeTo("spark_catalog.default.events_partitioned").append()

// 4. 查询优化技术演示

// 4.1 布隆过滤器优化效果演示

println("=== 布隆过滤器优化效果演示 ===")
println("查询特定用户的记录（利用布隆过滤器）:")

// 开启查询计划查看
spark.conf.set("spark.sql.debug.maxToStringFields", 100)

// 查询特定用户（应该能利用布隆过滤器快速定位）
val bloomFilterQuery = spark.sql("""
  SELECT * FROM spark_catalog.default.users_optimized 
  WHERE user_id = 12345
""")

println("执行计划（注意数据裁剪信息）:")
bloomFilterQuery.explain()

println("查询结果:")
bloomFilterQuery.show()

// 4.2 数据裁剪优化演示

println("=== 分区裁剪优化演示 ===")
println("查询特定类型和时间段的事件:")

val partitionPruningQuery = spark.sql("""
  SELECT COUNT(*) as event_count 
  FROM spark_catalog.default.events_partitioned 
  WHERE event_type = 'purchase' 
  AND event_date >= '2023-01-01' 
  AND event_date <= '2023-03-31'
""")

println("执行计划（注意分区裁剪信息）:")
partitionPruningQuery.explain()

println("查询结果:")
partitionPruningQuery.show()

// 4.3 列裁剪优化演示

println("=== 列裁剪优化演示 ===")
println("只查询需要的列:")

val columnPruningQuery = spark.sql("""
  SELECT user_id, email 
  FROM spark_catalog.default.users_optimized 
  WHERE status = 'premium'
""")

println("执行计划（注意只读取必要列）:")
columnPruningQuery.explain()

println("查询结果（前10条）:")
columnPruningQuery.show(10)

// 5. 元数据缓存配置示例

println("=== 元数据缓存配置 ===")
// 在实际应用中，这些配置应在Spark配置文件中设置
spark.conf.set("spark.sql.catalog.spark_catalog.cache-enabled", "true")
spark.conf.set("spark.sql.catalog.spark_catalog.cache.expiration-interval-ms", "300000") // 5分钟
spark.conf.set("spark.sql.catalog.spark_catalog.cache.max-entries", "1000")

println("元数据缓存已启用")

// 6. 查询性能对比

println("=== 查询性能对比 ===")

// 6.1 未优化查询
println("未优化查询（全表扫描）:")
val startTime1 = System.currentTimeMillis()
val unoptimizedQuery = spark.sql("""
  SELECT * FROM spark_catalog.default.users_optimized 
  WHERE email LIKE '%1234@example.com'
""")
unoptimizedQuery.collect() // 触发执行
val endTime1 = System.currentTimeMillis()
println(s"未优化查询耗时: ${endTime1 - startTime1} ms")

// 6.2 优化查询
println("优化查询（利用布隆过滤器）:")
val startTime2 = System.currentTimeMillis()
val optimizedQuery = spark.sql("""
  SELECT * FROM spark_catalog.default.users_optimized 
  WHERE user_id = 1234
""")
optimizedQuery.collect() // 触发执行
val endTime2 = System.currentTimeMillis()
println(s"优化查询耗时: ${endTime2 - startTime2} ms")

// 7. 查看表统计信息

println("=== 表统计信息 ===")

// 查看用户表的文件信息
println("用户表文件信息:")
spark.sql("""
  SELECT 
    COUNT(*) as file_count,
    AVG(file_size_in_bytes) as avg_file_size,
    MAX(file_size_in_bytes) as max_file_size,
    MIN(file_size_in_bytes) as min_file_size
  FROM spark_catalog.default.users_optimized.files
""").show()

// 查看事件表的分区信息
println("事件表分区信息:")
spark.sql("""
  SELECT 
    partition.event_type,
    partition.event_date_month,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size
  FROM spark_catalog.default.events_partitioned.files
  GROUP BY partition.event_type, partition.event_date_month
  ORDER BY total_size DESC
  LIMIT 10
""").show()

// 8. 最佳实践建议输出

println("=== 查询优化最佳实践 ===")
println("""
1. 布隆过滤器应用：
   - 适用于高基数列的精确匹配查询
   - 对于ID、邮箱等唯一标识符特别有效
   - 需要在建表时配置相应的表属性

2. 分区裁剪：
   - 在WHERE子句中包含分区字段过滤条件
   - 合理设计分区策略以最大化裁剪效果
   - 避免在分区字段上使用函数变换

3. 列裁剪：
   - 只选择需要的列，避免SELECT *
   - 减少网络传输和内存使用
   - 提高查询执行效率

4. 元数据缓存：
   - 启用并合理配置元数据缓存
   - 根据集群资源调整缓存大小
   - 设置合适的缓存过期时间

5. 查询计划分析：
   - 使用EXPLAIN分析查询执行计划
   - 确认优化器是否应用了预期的优化
   - 根据计划调整查询或表结构
""")

// 9. 清理测试表
println("=== 清理测试表 ===")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.users_optimized")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.events_partitioned")

println("查询优化示例完成！")