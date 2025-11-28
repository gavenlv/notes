// Batch Write Optimization for Iceberg Tables
// =========================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.spark.actions.SparkActions

object BatchWriteOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Batch Write Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()

    import spark.implicits._

    // Optimize batch writes with proper partitioning
    def optimizeBatchWriteWithPartitioning(): Unit = {
      println("Optimizing batch writes with proper partitioning...")
      
      // Read source data
      val sourceData = spark.read
        .format("parquet")
        .load("/data/source/sales_data/")
      
      // Determine optimal partitioning based on data size and target table
      val dataSize = sourceData.rdd.map(_.asInstanceOf[org.apache.spark.sql.Row].mkString(",").getBytes.length).sum()
      val optimalPartitions = Math.max(1, (dataSize / (512 * 1024 * 1024)).toInt) // Target ~512MB per partition
      
      println(s"Repartitioning data into $optimalPartitions partitions for optimal write performance")
      
      // Repartition data for optimal write performance
      val repartitionedData = sourceData
        .repartition(optimalPartitions, col("region"), col("sale_date"))
      
      // Write to Iceberg with optimized settings
      repartitionedData.write
        .format("iceberg")
        .mode("append")
        .option("write-format", "parquet")
        .option("target-file-size-bytes", "536870912") // 512MB
        .option("distribution-mode", "hash")
        .save("iceberg_catalog.sales_data")
      
      println("Batch write with optimized partitioning completed")
    }
    
    // Optimize batch writes with schema validation
    def optimizeBatchWriteWithSchemaValidation(): Unit = {
      println("Optimizing batch writes with schema validation...")
      
      // Read source data
      val sourceData = spark.read
        .format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("/data/source/customer_data/")
      
      // Validate schema compatibility before write
      val targetTable = spark.table("iceberg_catalog.customer_data")
      val sourceSchema = sourceData.schema
      val targetSchema = targetTable.schema
      
      // Check for schema compatibility
      val compatible = sourceSchema.fields.forall { sourceField =>
        targetSchema.fields.exists { targetField =>
          targetField.name == sourceField.name && 
          (targetField.dataType == sourceField.dataType || 
           isCompatibleType(targetField.dataType, sourceField.dataType))
        }
      }
      
      if (compatible) {
        println("Schema is compatible, proceeding with write...")
        
        // Write with schema enforcement
        sourceData.write
          .format("iceberg")
          .mode("append")
          .option("check-ordering", "true")
          .option("validate-required-columns", "true")
          .save("iceberg_catalog.customer_data")
      } else {
        println("Schema is not compatible, performing schema evolution...")
        
        // Perform schema evolution if needed
        evolveSchema("customer_data", sourceSchema)
        
        // Retry write after schema evolution
        sourceData.write
          .format("iceberg")
          .mode("append")
          .save("iceberg_catalog.customer_data")
      }
      
      println("Batch write with schema validation completed")
    }
    
    // Helper method to check type compatibility
    def isCompatibleType(targetType: DataType, sourceType: DataType): Boolean = {
      (targetType, sourceType) match {
        case (target: NumericType, source: NumericType) => true
        case (target: StringType, source: StringType) => true
        case _ => targetType == sourceType
      }
    }
    
    // Helper method to evolve schema
    def evolveSchema(tableName: String, newSchema: StructType): Unit = {
      // Generate ALTER TABLE statements for new columns
      val existingTable = spark.table(s"iceberg_catalog.$tableName")
      val existingSchema = existingTable.schema
      
      val newColumns = newSchema.fields.filterNot { field =>
        existingSchema.fields.exists(_.name == field.name)
      }
      
      newColumns.foreach { field =>
        val sqlType = field.dataType match {
          case StringType => "STRING"
          case IntegerType => "INT"
          case LongType => "BIGINT"
          case DoubleType => "DOUBLE"
          case TimestampType => "TIMESTAMP"
          case DateType => "DATE"
          case BooleanType => "BOOLEAN"
          case _ => "STRING" // Default to STRING for unknown types
        }
        
        spark.sql(
          s"""
             |ALTER TABLE iceberg_catalog.$tableName 
             |ADD COLUMN ${field.name} $sqlType COMMENT '${field.metadata.toString()}'
           """.stripMargin)
      }
      
      println(s"Schema evolved with ${newColumns.length} new columns")
    }
    
    // Optimize batch writes with compression
    def optimizeBatchWriteWithCompression(): Unit = {
      println("Optimizing batch writes with compression...")
      
      // Read source data
      val sourceData = spark.read
        .format("json")
        .load("/data/source/web_events/")
      
      // Write with optimal compression settings
      sourceData.write
        .format("iceberg")
        .mode("append")
        .option("write-format", "parquet")
        .option("parquet.compression", "zstd") // Better compression ratio than gzip/snappy
        .option("parquet.block.size", "134217728") // 128MB blocks
        .option("parquet.page.size", "1048576") // 1MB pages
        .save("iceberg_catalog.web_events")
      
      println("Batch write with compression optimization completed")
    }
    
    // Optimize batch writes with concurrent processing
    def optimizeBatchWriteWithConcurrency(): Unit = {
      println("Optimizing batch writes with concurrent processing...")
      
      // Read multiple source datasets
      val salesData = spark.read.parquet("/data/source/sales_data/")
      val customerData = spark.read.parquet("/data/source/customer_data/")
      val productData = spark.read.parquet("/data/source/product_data/")
      
      // Process and write concurrently using async operations
      import scala.concurrent.Future
      import scala.concurrent.ExecutionContext.Implicits.global
      
      val salesFuture = Future {
        salesData.write
          .format("iceberg")
          .mode("append")
          .option("write-distribution-mode", "hash")
          .save("iceberg_catalog.sales_data")
      }
      
      val customerFuture = Future {
        customerData.write
          .format("iceberg")
          .mode("append")
          .option("write-distribution-mode", "range")
          .save("iceberg_catalog.customer_data")
      }
      
      val productFuture = Future {
        productData.write
          .format("iceberg")
          .mode("append")
          .option("write-distribution-mode", "none")
          .save("iceberg_catalog.product_data")
      }
      
      // Wait for all writes to complete
      scala.concurrent.Await.all(salesFuture, customerFuture, productFuture)
      
      println("Concurrent batch writes completed")
    }
    
    // Monitor and optimize write performance
    def monitorWritePerformance(): Unit = {
      println("Monitoring and optimizing write performance...")
      
      // Enable detailed metrics collection
      spark.conf.set("spark.sql.metrics.enabled", "true")
      
      // Perform a sample write operation
      val testData = spark.range(1000000)
        .toDF("id")
        .withColumn("value", rand() * 1000)
        .withColumn("category", concat(lit("category_"), (rand() * 10).cast("int")))
        .withColumn("timestamp", current_timestamp())
      
      val startTime = System.currentTimeMillis()
      
      testData.write
        .format("iceberg")
        .mode("append")
        .option("write-format", "parquet")
        .option("target-file-size-bytes", "536870912")
        .save("iceberg_catalog.performance_test")
      
      val endTime = System.currentTimeMillis()
      
      println(s"Write operation completed in ${endTime - startTime} ms")
      
      // Analyze write metrics
      val writeMetrics = spark.sql(
        """
          |SELECT 
          |  COUNT(*) as written_records,
          |  SUM(file_size_in_bytes) / 1024 / 1024 as total_size_mb,
          |  AVG(file_size_in_bytes) / 1024 / 1024 as avg_file_size_mb,
          |  MAX(file_size_in_bytes) / 1024 / 1024 as max_file_size_mb
          |FROM iceberg_catalog.performance_test.files
        """.stripMargin)
      
      println("Write performance metrics:")
      writeMetrics.show()
    }
    
    // Execute all batch write optimization techniques
    optimizeBatchWriteWithPartitioning()
    optimizeBatchWriteWithSchemaValidation()
    optimizeBatchWriteWithCompression()
    optimizeBatchWriteWithConcurrency()
    monitorWritePerformance()
    
    spark.stop()
  }
}