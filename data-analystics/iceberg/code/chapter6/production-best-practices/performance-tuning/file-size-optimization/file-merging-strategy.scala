// File Merging Strategy for Iceberg Tables
// =======================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.actions.SparkActions
import org.apache.iceberg.Table
import org.apache.iceberg.spark.Spark3Util

object FileMergingStrategy {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg File Merging Strategy")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .getOrCreate()

    import spark.implicits._

    // Merge small files strategy
    def mergeSmallFiles(tableName: String, targetFileSizeMB: Long = 512): Unit = {
      println(s"Merging small files for table: $tableName")
      
      // Get the Iceberg table
      val tableIdent = Spark3Util.identifierToTable(spark, s"iceberg_catalog.$tableName")
      val table = Spark3Util.loadIcebergTable(spark, tableIdent)
      
      // Use Iceberg's rewriteDataFiles action to merge small files
      val result = SparkActions.get(spark)
        .rewriteDataFiles(table)
        .targetSizeInBytes(targetFileSizeMB * 1024 * 1024) // Convert MB to bytes
        .execute()
      
      println(s"Merged ${result.rewrittenDataFilesCount()} files into ${result.addedDataFilesCount()} new files")
      println(s"Deleted ${result.deletedDataFilesCount()} old files")
    }
    
    // Optimize file layout strategy
    def optimizeFileLayout(tableName: String): Unit = {
      println(s"Optimizing file layout for table: $tableName")
      
      // Get the Iceberg table
      val tableIdent = Spark3Util.identifierToTable(spark, s"iceberg_catalog.$tableName")
      val table = Spark3Util.loadIcebergTable(spark, tableIdent)
      
      // Use Iceberg's rewriteDataFiles action with bin packing
      val result = SparkActions.get(spark)
        .rewriteDataFiles(table)
        .binPack() // Use bin pack strategy
        .execute()
      
      println(s"Optimized file layout: ${result.rewrittenDataFilesCount()} files rewritten")
    }
    
    // Adaptive file merging based on partition statistics
    def adaptiveMergeByPartition(tableName: String): Unit = {
      println(s"Performing adaptive merge for table: $tableName")
      
      // First, analyze partition sizes
      val partitionStats = spark.sql(
        s"""
           |SELECT 
           |  partition,
           |  COUNT(*) as file_count,
           |  SUM(file_size_in_bytes) as total_size_bytes,
           |  AVG(file_size_in_bytes) as avg_file_size_bytes
           |FROM iceberg_catalog.$tableName.files
           |GROUP BY partition
           |ORDER BY total_size_bytes DESC
         """.stripMargin)
      
      // Show partitions with too many small files
      println("Partitions with high file fragmentation:")
      partitionStats.filter($"file_count" > 10 && $"avg_file_size_bytes" < 16 * 1024 * 1024)
        .show(20, truncate = false)
      
      // Get the Iceberg table
      val tableIdent = Spark3Util.identifierToTable(spark, s"iceberg_catalog.$tableName")
      val table = Spark3Util.loadIcebergTable(spark, tableIdent)
      
      // Apply rewrite strategy to fragmented partitions
      val result = SparkActions.get(spark)
        .rewriteDataFiles(table)
        .filterWhere("partition_date >= '2023-01-01'") // Example filter
        .targetSizeInBytes(512 * 1024 * 1024) // 512MB target
        .execute()
      
      println(s"Adaptive merge completed: ${result.rewrittenDataFilesCount()} files merged")
    }
    
    // Execute merging strategies
    mergeSmallFiles("sales_data", 512)
    optimizeFileLayout("customer_profiles")
    adaptiveMergeByPartition("web_events")
    
    spark.stop()
  }
}