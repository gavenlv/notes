// Data Compression Optimization for Iceberg Tables
// =============================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.spark.actions.SparkActions
import org.apache.spark.sql.execution.datasources.v2.FileFormat
import java.text.DecimalFormat

object DataCompressionOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Data Compression Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .getOrCreate()

    import spark.implicits._

    // Configure compression settings
    def configureCompressionSettings(): Unit = {
      println("Configuring compression settings...")
      
      // Set default compression codec for Parquet
      spark.conf.set("spark.sql.parquet.compression.codec", "snappy")
      
      // Set compression codec for Iceberg tables
      spark.conf.set("spark.sql.iceberg.write.format.default", "parquet")
      
      // Configure Parquet block size
      spark.conf.set("spark.sql.parquet.block.size", "134217728") // 128MB
      
      // Enable Parquet dictionary encoding
      spark.conf.set("spark.sql.parquet.dictionary.enabled", "true")
      
      // Set Parquet page size
      spark.conf.set("spark.sql.parquet.page.size", "1048576") // 1MB
      
      println("Compression settings configured")
    }
    
    // Compare different compression codecs
    def compareCompressionCodecs(): Unit = {
      println("Comparing different compression codecs...")
      
      // Sample data for testing
      val sampleData = spark.range(1000000)
        .toDF("id")
        .withColumn("name", concat(lit("name_"), ($"id" % 100000).cast("string")))
        .withColumn("value", rand() * 10000)
        .withColumn("category", concat(lit("category_"), ($"id" % 100).cast("string")))
        .withColumn("timestamp", current_timestamp())
      
      // Test UNCOMPRESSED
      spark.conf.set("spark.sql.parquet.compression.codec", "uncompressed")
      val uncompressedStartTime = System.currentTimeMillis()
      sampleData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.test_uncompressed")
      val uncompressedEndTime = System.currentTimeMillis()
      val uncompressedWriteTime = uncompressedEndTime - uncompressedStartTime
      
      // Get file size for uncompressed
      val uncompressedFileSize = getFileSize("iceberg_catalog.test_uncompressed")
      
      // Test SNAPPY
      spark.conf.set("spark.sql.parquet.compression.codec", "snappy")
      val snappyStartTime = System.currentTimeMillis()
      sampleData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.test_snappy")
      val snappyEndTime = System.currentTimeMillis()
      val snappyWriteTime = snappyEndTime - snappyStartTime
      
      // Get file size for Snappy
      val snappyFileSize = getFileSize("iceberg_catalog.test_snappy")
      
      // Test GZIP
      spark.conf.set("spark.sql.parquet.compression.codec", "gzip")
      val gzipStartTime = System.currentTimeMillis()
      sampleData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.test_gzip")
      val gzipEndTime = System.currentTimeMillis()
      val gzipWriteTime = gzipEndTime - gzipStartTime
      
      // Get file size for GZIP
      val gzipFileSize = getFileSize("iceberg_catalog.test_gzip")
      
      // Test LZO
      spark.conf.set("spark.sql.parquet.compression.codec", "lzo")
      val lzoStartTime = System.currentTimeMillis()
      sampleData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.test_lzo")
      val lzoEndTime = System.currentTimeMillis()
      val lzoWriteTime = lzoEndTime - lzoStartTime
      
      // Get file size for LZO
      val lzoFileSize = getFileSize("iceberg_catalog.test_lzo")
      
      // Test ZSTD
      spark.conf.set("spark.sql.parquet.compression.codec", "zstd")
      val zstdStartTime = System.currentTimeMillis()
      sampleData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.test_zstd")
      val zstdEndTime = System.currentTimeMillis()
      val zstdWriteTime = zstdEndTime - zstdStartTime
      
      // Get file size for ZSTD
      val zstdFileSize = getFileSize("iceberg_catalog.test_zstd")
      
      // Print comparison results
      val df = new DecimalFormat("#.##")
      println("Compression Codec Comparison Results:")
      println("-----------------------------------")
      println(f"UNCOMPRESSED: ${df.format(uncompressedFileSize / (1024.0 * 1024.0))}%6.2f MB, Write Time: ${uncompressedWriteTime}ms")
      println(f"SNAPPY:       ${df.format(snappyFileSize / (1024.0 * 1024.0))}%6.2f MB, Write Time: ${snappyWriteTime}ms")
      println(f"GZIP:         ${df.format(gzipFileSize / (1024.0 * 1024.0))}%6.2f MB, Write Time: ${gzipWriteTime}ms")
      println(f"LZO:          ${df.format(lzoFileSize / (1024.0 * 1024.0))}%6.2f MB, Write Time: ${lzoWriteTime}ms")
      println(f"ZSTD:         ${df.format(zstdFileSize / (1024.0 * 1024.0))}%6.2f MB, Write Time: ${zstdWriteTime}ms")
      
      // Calculate compression ratios
      val uncompressedRatio = 1.0
      val snappyRatio = uncompressedFileSize / snappyFileSize.toDouble
      val gzipRatio = uncompressedFileSize / gzipFileSize.toDouble
      val lzoRatio = uncompressedFileSize / lzoFileSize.toDouble
      val zstdRatio = uncompressedFileSize / zstdFileSize.toDouble
      
      println("\nCompression Ratios (relative to uncompressed):")
      println("---------------------------------------------")
      println(f"SNAPPY: ${snappyRatio}%1.2f")
      println(f"GZIP:   ${gzipRatio}%1.2f")
      println(f"LZO:    ${lzoRatio}%1.2f")
      println(f"ZSTD:   ${zstdRatio}%1.2f")
      
      println("Compression codec comparison completed")
    }
    
    // Helper method to get file size
    def getFileSize(tablePath: String): Long = {
      val files = spark.sql(s"SELECT * FROM $tablePath.files")
      files.agg(sum("file_size_in_bytes")).collect()(0).getLong(0)
    }
    
    // Implement column-specific compression
    def implementColumnSpecificCompression(): Unit = {
      println("Implementing column-specific compression...")
      
      // Create table with different compression for different columns
      val dataWithSchema = spark.range(1000000)
        .toDF("id")
        .withColumn("name", concat(lit("name_"), ($"id" % 100000).cast("string")))
        .withColumn("value", rand() * 10000)
        .withColumn("category", concat(lit("category_"), ($"id" % 100).cast("string")))
        .withColumn("timestamp", current_timestamp())
        .withColumn("description", lit("This is a sample description that might be quite long and repetitive"))
      
      // Write with column-specific compression settings
      dataWithSchema.write
        .format("iceberg")
        .option("write-format", "parquet")
        .option("parquet.compression", "zstd") // Default compression
        .mode("overwrite")
        .save("iceberg_catalog.column_compressed_table")
      
      // For more fine-grained control, we would typically set this at the Parquet level
      // But in Iceberg, we can use table properties
      spark.sql("""
        ALTER TABLE iceberg_catalog.column_compressed_table 
        SET TBLPROPERTIES (
          'write.parquet.compression-codec' = 'zstd',
          'write.parquet.dictionary.enabled' = 'true'
        )
      """)
      
      println("Column-specific compression implemented")
    }
    
    // Optimize compression for different data types
    def optimizeCompressionForDataTypes(): Unit = {
      println("Optimizing compression for different data types...")
      
      // Create dataset with various data types
      val mixedData = spark.range(1000000)
        .toDF("id")
        .withColumn("small_int", ($"id" % 1000).cast("short"))
        .withColumn("large_int", ($"id" * 1000).cast("long"))
        .withColumn("decimal_value", ($"id" * 1.23).cast("decimal(10,2)"))
        .withColumn("float_value", ($"id" * 1.5f).cast("float"))
        .withColumn("double_value", ($"id" * 1.23456789).cast("double"))
        .withColumn("string_value", concat(lit("string_"), ($"id" % 10000).cast("string")))
        .withColumn("timestamp_value", current_timestamp())
        .withColumn("boolean_value", ($"id" % 2 === 0))
        .withColumn("binary_value", lit(Array.fill(10)(0.toByte))) // Small binary
      
      // Write with optimized compression
      mixedData.write
        .format("iceberg")
        .option("write-format", "parquet")
        .option("parquet.compression", "zstd") // Good balance of speed and compression
        .mode("overwrite")
        .save("iceberg_catalog.data_type_optimized_table")
      
      println("Data type compression optimization completed")
    }
    
    // Implement adaptive compression based on data characteristics
    def implementAdaptiveCompression(): Unit = {
      println("Implementing adaptive compression based on data characteristics...")
      
      // Analyze data to determine optimal compression
      def determineOptimalCompression(data: org.apache.spark.sql.DataFrame): String = {
        // In a real implementation, we would analyze:
        // 1. Data cardinality
        // 2. Text repetitiveness
        // 3. Numeric ranges
        // 4. Data size
        
        // For this example, we'll use a simple heuristic
        val rowCount = data.count()
        
        // Use different compression based on row count
        if (rowCount < 100000) {
          "snappy" // Faster for smaller datasets
        } else if (rowCount < 1000000) {
          "zstd" // Balanced for medium datasets
        } else {
          "gzip" // Better compression for large datasets
        }
      }
      
      // Sample datasets of different sizes
      val smallData = spark.range(50000).toDF("id")
      val mediumData = spark.range(500000).toDF("id")
      val largeData = spark.range(2000000).toDF("id")
      
      // Determine optimal compression for each
      val smallCompression = determineOptimalCompression(smallData)
      val mediumCompression = determineOptimalCompression(mediumData)
      val largeCompression = determineOptimalCompression(largeData)
      
      println(s"Recommended compression - Small: $smallCompression, Medium: $mediumCompression, Large: $largeCompression")
      
      // Apply recommended compression
      spark.conf.set("spark.sql.parquet.compression.codec", smallCompression)
      smallData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.small_adaptive_table")
      
      spark.conf.set("spark.sql.parquet.compression.codec", mediumCompression)
      mediumData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.medium_adaptive_table")
      
      spark.conf.set("spark.sql.parquet.compression.codec", largeCompression)
      largeData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.large_adaptive_table")
      
      println("Adaptive compression implemented")
    }
    
    // Monitor compression effectiveness
    def monitorCompressionEffectiveness(): Unit = {
      println("Monitoring compression effectiveness...")
      
      // Enable detailed metrics
      spark.conf.set("spark.sql.execution.metric.output", "true")
      
      // Create test data
      val testData = spark.range(1000000)
        .toDF("id")
        .withColumn("value", rand() * 10000)
        .withColumn("category", concat(lit("category_"), ($"id" % 100).cast("string")))
        .withColumn("description", lit("Sample description for compression testing"))
      
      // Write with different compression codecs and measure
      val codecs = Seq("snappy", "gzip", "zstd")
      
      codecs.foreach { codec =>
        spark.conf.set("spark.sql.parquet.compression.codec", codec)
        
        val startTime = System.currentTimeMillis()
        testData.write
          .format("iceberg")
          .mode("overwrite")
          .save(s"iceberg_catalog.monitor_$codec")
        val endTime = System.currentTimeMillis()
        
        val writeTime = endTime - startTime
        val fileSize = getFileSize(s"iceberg_catalog.monitor_$codec")
        
        // Read performance test
        val readStartTime = System.currentTimeMillis()
        val readCount = spark.table(s"iceberg_catalog.monitor_$codec").count()
        val readEndTime = System.currentTimeMillis()
        val readTime = readEndTime - readStartTime
        
        val df = new DecimalFormat("#.##")
        println(f"$codec - File Size: ${df.format(fileSize / (1024.0 * 1024.0))}%6.2f MB, Write Time: ${writeTime}ms, Read Time: ${readTime}ms, Rows: $readCount")
      }
      
      println("Compression effectiveness monitoring completed")
    }
    
    // Execute all compression optimization techniques
    configureCompressionSettings()
    compareCompressionCodecs()
    implementColumnSpecificCompression()
    optimizeCompressionForDataTypes()
    implementAdaptiveCompression()
    monitorCompressionEffectiveness()
    
    spark.stop()
  }
}