// Parallel Write Optimization for Iceberg Tables
// ===========================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.spark.actions.SparkActions
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Await
import scala.concurrent.duration.Duration

object ParallelWriteOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Parallel Write Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .config("spark.sql.distribution.coalescePartition.enabled", "true")
      .getOrCreate()

    import spark.implicits._

    // Configure parallel write settings
    def configureParallelWriteSettings(): Unit = {
      println("Configuring parallel write settings...")
      
      // Set optimal parallelism for Iceberg writes
      spark.conf.set("spark.sql.iceberg.planning.parallelism", "10")
      spark.conf.set("spark.sql.iceberg.write.parallelism", "20")
      
      // Configure distribution modes for different scenarios
      spark.conf.set("spark.sql.iceberg.write.distribution-mode", "hash")
      
      // Set write buffer sizes
      spark.conf.set("spark.sql.iceberg.write.buffer-size-bytes", "134217728") // 128MB
      
      // Configure commit parallelism
      spark.conf.set("spark.sql.iceberg.commit.parallelism", "5")
      
      println("Parallel write settings configured")
    }
    
    // Implement hash-based distribution for parallel writes
    def implementHashDistribution(): Unit = {
      println("Implementing hash-based distribution for parallel writes...")
      
      // Read large dataset
      val largeDataset = spark.read
        .format("parquet")
        .load("/data/large_dataset/")
      
      // Distribute data using hash partitioning on key columns
      val distributedData = largeDataset
        .repartition(col("customer_id"), col("transaction_date"))
      
      // Write with hash distribution mode
      distributedData.write
        .format("iceberg")
        .mode("append")
        .option("write-distribution-mode", "hash")
        .option("target-file-size-bytes", "536870912") // 512MB
        .save("iceberg_catalog.large_transactions")
      
      println("Hash-based parallel write completed")
    }
    
    // Implement range-based distribution for parallel writes
    def implementRangeDistribution(): Unit = {
      println("Implementing range-based distribution for parallel writes...")
      
      // Read time-series data
      val timeSeriesData = spark.read
        .format("parquet")
        .load("/data/time_series/")
      
      // Distribute data using range partitioning on timestamp
      val rangeDistributedData = timeSeriesData
        .repartition(20, col("event_timestamp"))
      
      // Write with range distribution mode
      rangeDistributedData.write
        .format("iceberg")
        .mode("append")
        .option("write-distribution-mode", "range")
        .option("target-file-size-bytes", "536870912") // 512MB
        .save("iceberg_catalog.time_series_events")
      
      println("Range-based parallel write completed")
    }
    
    // Implement concurrent writes to multiple tables
    def implementConcurrentWrites(): Unit = {
      println("Implementing concurrent writes to multiple tables...")
      
      // Read source data
      val sourceData = spark.read
        .format("parquet")
        .load("/data/source/")
      
      // Split data for different tables
      val salesData = sourceData.filter($"category" === "sales")
      val customerData = sourceData.filter($"category" === "customer")
      val productData = sourceData.filter($"category" === "product")
      
      // Perform concurrent writes using Futures
      val salesFuture = Future {
        salesData.write
          .format("iceberg")
          .mode("append")
          .option("write-distribution-mode", "hash")
          .option("target-file-size-bytes", "536870912")
          .save("iceberg_catalog.sales_data")
        println("Sales data write completed")
      }
      
      val customerFuture = Future {
        customerData.write
          .format("iceberg")
          .mode("append")
          .option("write-distribution-mode", "hash")
          .option("target-file-size-bytes", "268435456") // 256MB for smaller table
          .save("iceberg_catalog.customer_data")
        println("Customer data write completed")
      }
      
      val productFuture = Future {
        productData.write
          .format("iceberg")
          .mode("append")
          .option("write-distribution-mode", "none")
          .option("target-file-size-bytes", "134217728") // 128MB for smaller table
          .save("iceberg_catalog.product_data")
        println("Product data write completed")
      }
      
      // Wait for all concurrent writes to complete
      Await.result(Future.sequence(Seq(salesFuture, customerFuture, productFuture)), Duration.Inf)
      
      println("All concurrent writes completed")
    }
    
    // Optimize write parallelism based on cluster resources
    def optimizeWriteParallelism(): Unit = {
      println("Optimizing write parallelism based on cluster resources...")
      
      // Get cluster information
      val executorCount = spark.sparkContext.getConf.get("spark.executor.instances", "10").toInt
      val coresPerExecutor = spark.sparkContext.getConf.get("spark.executor.cores", "4").toInt
      val totalCores = executorCount * coresPerExecutor
      
      println(s"Cluster resources: $executorCount executors, $coresPerExecutor cores each, $totalCores total cores")
      
      // Calculate optimal parallelism
      val optimalParallelism = Math.min(totalCores * 2, 100) // Rule of thumb: 2x total cores, max 100
      
      // Configure Iceberg write parallelism
      spark.conf.set("spark.sql.iceberg.write.parallelism", optimalParallelism.toString)
      
      // Read data to write
      val dataToWrite = spark.read
        .format("parquet")
        .load("/data/to_write/")
      
      // Write with optimized parallelism
      dataToWrite.write
        .format("iceberg")
        .mode("append")
        .option("write-distribution-mode", "hash")
        .option("target-file-size-bytes", "536870912")
        .save("iceberg_catalog.optimized_writes")
      
      println(s"Write completed with optimized parallelism of $optimalParallelism")
    }
    
    // Implement write batching for high-throughput scenarios
    def implementWriteBatching(): Unit = {
      println("Implementing write batching for high-throughput scenarios...")
      
      // Simulate streaming data
      val streamingData = spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "transactions")
        .load()
      
      // Process and batch the data
      val processedData = streamingData
        .select(
          $"key".cast("string").as("transaction_id"),
          from_json($"value".cast("string"), getTransactionSchema).as("data")
        )
        .select($"transaction_id", $"data.*")
        .withWatermark("transaction_time", "10 minutes")
      
      // Write with batching configuration
      processedData.writeStream
        .format("iceberg")
        .option("path", "iceberg_catalog.streaming_transactions")
        .option("checkpointLocation", "/tmp/checkpoint")
        .option("write-format", "parquet")
        .option("target-file-size-bytes", "536870912")
        .option("write-distribution-mode", "hash")
        .option("fanout-enabled", "true") // Enable fanout for concurrent writers
        .trigger(Trigger.ProcessingTime("5 minutes")) // Batch every 5 minutes
        .start()
      
      println("Streaming write with batching configured")
    }
    
    // Helper method to define transaction schema
    def getTransactionSchema: StructType = {
      StructType(Seq(
        StructField("customer_id", StringType, nullable = false),
        StructField("product_id", StringType, nullable = false),
        StructField("amount", DoubleType, nullable = false),
        StructField("currency", StringType, nullable = true),
        StructField("transaction_time", TimestampType, nullable = false),
        StructField("location", StringType, nullable = true)
      ))
    }
    
    // Monitor parallel write performance
    def monitorParallelWritePerformance(): Unit = {
      println("Monitoring parallel write performance...")
      
      // Enable detailed metrics
      spark.conf.set("spark.sql.metrics.enabled", "true")
      
      // Perform a test write with parallelism
      val testData = spark.range(10000000) // 10M records
        .toDF("id")
        .withColumn("value", rand() * 10000)
        .withColumn("category", concat(lit("cat_"), (rand() * 100).cast("int")))
        .withColumn("timestamp", current_timestamp())
        .repartition(50) // Create 50 partitions for parallel processing
      
      val startTime = System.currentTimeMillis()
      
      testData.write
        .format("iceberg")
        .mode("append")
        .option("write-distribution-mode", "hash")
        .option("target-file-size-bytes", "536870912")
        .option("fanout-enabled", "true")
        .save("iceberg_catalog.parallel_write_test")
      
      val endTime = System.currentTimeMillis()
      
      println(s"Parallel write completed in ${endTime - startTime} ms")
      
      // Analyze performance metrics
      val metrics = spark.sql(
        """
          |SELECT 
          |  COUNT(*) as total_records,
          |  COUNT(DISTINCT partition) as partition_count,
          |  SUM(file_size_in_bytes) / 1024 / 1024 as total_size_mb,
          |  AVG(file_size_in_bytes) / 1024 / 1024 as avg_file_size_mb
          |FROM iceberg_catalog.parallel_write_test.files
        """.stripMargin)
      
      println("Parallel write performance metrics:")
      metrics.show()
    }
    
    // Execute all parallel write optimization techniques
    configureParallelWriteSettings()
    implementHashDistribution()
    implementRangeDistribution()
    implementConcurrentWrites()
    optimizeWriteParallelism()
    implementWriteBatching()
    monitorParallelWritePerformance()
    
    spark.stop()
  }
}