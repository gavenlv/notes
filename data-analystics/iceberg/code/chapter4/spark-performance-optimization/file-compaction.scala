// Spark Iceberg性能优化示例 - 文件合并与压缩优化
// 需要启动Spark Shell: spark-shell --packages org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:0.13.0

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

// 初始化Spark Session with Iceberg配置
val spark = SparkSession.builder()
  .appName("Iceberg File Compaction Optimization")
  .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
  .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
  .config("spark.sql.catalog.spark_catalog.type", "hadoop")
  .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
  .getOrCreate()

import spark.implicits._

// 1. 创建测试表并插入数据以模拟小文件问题
println("=== 创建测试表 ===")
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.test_compaction (
    id BIGINT,
    name STRING,
    category STRING,
    price DOUBLE,
    created_date DATE
  )
  USING iceberg
  PARTITIONED BY (category, days(created_date))
  TBLPROPERTIES (
    'write.format.default'='parquet',
    'write.target-file-size-bytes'='32MB'  // 故意设置较小的目标文件大小
  )
""")

// 插入多批次小数据以生成小文件
println("=== 插入测试数据 ===")
for (i <- 1 to 10) {
  val data = Seq.fill(100)((i.toLong, s"name_$i", s"category_${i%3}", i.toDouble, java.sql.Date.valueOf(s"2023-01-${String.format("%02d", Integer.valueOf(i))}")))
  val df = spark.createDataset(data).toDF("id", "name", "category", "price", "created_date")
  df.writeTo("spark_catalog.default.test_compaction").append()
  println(s"Inserted batch $i")
}

// 2. 查看当前表的文件信息
println("=== 查看表文件信息 ===")
spark.read.format("iceberg").load("spark_catalog.default.test_compaction.files").show(20, truncate = false)

// 3. 执行文件合并操作
println("=== 执行文件合并 ===")
// 方法一：使用系统过程进行数据文件重写
spark.sql("""
  CALL spark_catalog.system.rewrite_data_files(
    table => 'default.test_compaction',
    options => map(
      'target-file-size-bytes', '536870912',  -- 512MB目标文件大小
      'min-input-files', '5',                 -- 至少5个输入文件才合并
      'min-file-size-bytes', '16777216'       -- 最小文件大小16MB
    )
  )
""").show()

// 4. 查看合并后的文件信息
println("=== 查看合并后的文件信息 ===")
spark.read.format("iceberg").load("spark_catalog.default.test_compaction.files").show(20, truncate = false)

// 5. 元数据文件优化
println("=== 执行元数据文件优化 ===")
// 重写manifests文件
spark.sql("""
  CALL spark_catalog.system.rewrite_manifests(
    table => 'default.test_compaction'
  )
""").show()

// 压缩元数据文件
spark.sql("""
  CALL spark_catalog.system.compress_metadata(
    table => 'default.test_compaction'
  )
""").show()

// 6. 验证优化效果
println("=== 验证优化效果 ===")
// 查看表的历史记录
spark.sql("SELECT * FROM spark_catalog.default.test_compaction.history").show(truncate = false)

// 查看表的快照信息
spark.sql("SELECT * FROM spark_catalog.default.test_compaction.snapshots").show(truncate = false)

// 7. 自定义压缩策略示例
println("=== 自定义压缩策略示例 ===")
// 创建一个新的表，演示不同的压缩配置
spark.sql("""
  CREATE TABLE IF NOT EXISTS spark_catalog.default.test_compression (
    id BIGINT,
    name STRING,
    description STRING
  )
  USING iceberg
  TBLPROPERTIES (
    'write.format.default'='parquet',
    'write.parquet.compression-codec'='zstd',  -- 使用ZSTD压缩
    'write.parquet.compression-level'='3',     -- 压缩级别
    'write.target-file-size-bytes'='134217728' -- 128MB目标文件大小
  )
""")

// 插入测试数据
val compressionData = Seq.fill(5000)((1L to 5000L, (1 to 5000).map(i => s"name_$i"), (1 to 5000).map(i => s"description_for_item_$i_with_more_text_to_make_it_larger")))
val compressionDf = spark.createDataset(compressionData).toDF("id", "name", "description")
compressionDf.writeTo("spark_catalog.default.test_compression").append()

println("=== 比较不同压缩格式的文件大小 ===")
// 查看使用不同压缩格式的文件大小
spark.read.format("iceberg").load("spark_catalog.default.test_compression.files").select("file_path", "file_size_in_bytes").show(10, truncate = false)

// 8. 清理测试表
println("=== 清理测试表 ===")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.test_compaction")
spark.sql("DROP TABLE IF EXISTS spark_catalog.default.test_compression")

println("文件合并与压缩优化示例完成！")