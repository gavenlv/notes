// File Size Analysis for Iceberg Tables
// ====================================

import org.apache.spark.sql.SparkSession
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.spark.source.SparkTable
import org.apache.iceberg.Table
import org.apache.iceberg.spark.Spark3Util.{identifierToTable, tableToIdentifier}
import org.apache.spark.sql.functions._

object FileSizeAnalysis {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg File Size Analysis")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .getOrCreate()

    import spark.implicits._

    // Analyze file sizes for a specific table
    def analyzeFileSize(tableName: String): Unit = {
      println(s"Analyzing file sizes for table: $tableName")
      
      // Get the Iceberg table
      val tableIdent = Spark3Util.identifierToTable(spark, s"iceberg_catalog.$tableName")
      val table = Spark3Util.loadIcebergTable(spark, tableIdent)
      
      // Get manifest files
      val manifests = table.currentSnapshot().allManifests(table.io())
      
      // Collect file information
      val fileInfo = manifests.asScala.flatMap { manifest =>
        val entries = manifest.fetchEntries(table.io())
        entries.asScala.map { entry =>
          (entry.file().path(), entry.file().fileSizeInBytes(), entry.file().recordCount())
        }
      }.toList
      
      // Convert to DataFrame for analysis
      val fileDF = fileInfo.toDF("file_path", "file_size_bytes", "record_count")
      
      // Add calculated columns
      val enhancedDF = fileDF
        .withColumn("file_size_mb", $"file_size_bytes" / 1024 / 1024)
        .withColumn("avg_record_size_bytes", $"file_size_bytes" / $"record_count")
      
      // Show statistics
      println("File Size Statistics:")
      enhancedDF.select(
        min("file_size_mb").as("min_size_mb"),
        max("file_size_mb").as("max_size_mb"),
        avg("file_size_mb").as("avg_size_mb"),
        stddev("file_size_mb").as("stddev_size_mb"),
        count("*").as("total_files")
      ).show()
      
      // Identify files that are too small (< 16MB)
      println("Files smaller than recommended size (16MB):")
      enhancedDF.filter($"file_size_mb" < 16)
        .orderBy($"file_size_mb".asc)
        .show(20, truncate = false)
      
      // Identify files that are too large (> 512MB)
      println("Files larger than recommended size (512MB):")
      enhancedDF.filter($"file_size_mb" > 512)
        .orderBy($"file_size_mb".desc)
        .show(20, truncate = false)
    }
    
    // Analyze file sizes for different tables
    analyzeFileSize("sales_data")
    analyzeFileSize("customer_profiles")
    analyzeFileSize("product_catalog")
    
    spark.stop()
  }
}