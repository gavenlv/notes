// Partition Strategy Optimization for Iceberg Tables
// =================================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.spark.actions.SparkActions
import org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
import org.apache.iceberg.TableProperties

object PartitionStrategyOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Partition Strategy Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .getOrCreate()

    import spark.implicits._

    // Analyze current partitioning strategy
    def analyzePartitioning(tableName: String): Unit = {
      println(s"Analyzing partitioning strategy for table: $tableName")
      
      // Get partition information
      val partitionInfo = spark.sql(
        s"""
           |SELECT 
           |  partition,
           |  COUNT(*) as file_count,
           |  SUM(record_count) as total_records,
           |  SUM(file_size_in_bytes) / 1024 / 1024 as total_size_mb,
           |  AVG(record_count) as avg_records_per_file,
           |  AVG(file_size_in_bytes) / 1024 / 1024 as avg_file_size_mb
           |FROM iceberg_catalog.$tableName.files
           |GROUP BY partition
           |ORDER BY total_size_mb DESC
         """.stripMargin)
      
      println("Current partition distribution:")
      partitionInfo.show(20, truncate = false)
      
      // Identify problematic partitions
      println("Partitions with too many small files:")
      partitionInfo.filter($"avg_file_size_mb" < 16).show(10, truncate = false)
      
      println("Partitions with too few files (potential for combining):")
      partitionInfo.filter($"file_count" < 5).show(10, truncate = false)
    }
    
    // Optimize partition strategy by repartitioning
    def optimizePartitioning(tableName: String, partitionColumns: Seq[String]): Unit = {
      println(s"Optimizing partitioning for table: $tableName with columns: ${partitionColumns.mkString(", ")}")
      
      // Read the table
      val df = spark.table(s"iceberg_catalog.$tableName")
      
      // Determine optimal number of partitions based on data size
      val dataSize = df.rdd.map(_.asInstanceOf[org.apache.spark.sql.Row].mkString(",").getBytes.length).sum()
      val optimalPartitions = Math.max(1, (dataSize / (512 * 1024 * 1024)).toInt) // Target ~512MB per partition
      
      println(s"Repartitioning data into $optimalPartitions partitions")
      
      // Repartition and rewrite the table
      val repartitionedDF = df.repartition(optimalPartitions, partitionColumns.map(col): _*)
      
      // Write back to Iceberg with new partitioning
      repartitionedDF.write
        .format("iceberg")
        .mode("overwrite")
        .option("path", s"iceberg_catalog.$tableName")
        .save()
      
      println(s"Repartitioning completed for table: $tableName")
    }
    
    // Implement partition pruning optimization
    def implementPartitionPruning(tableName: String): Unit = {
      println(s"Implementing partition pruning for table: $tableName")
      
      // Example query with partition pruning
      val prunedQuery = spark.sql(
        s"""
           |SELECT *
           |FROM iceberg_catalog.$tableName
           |WHERE partition_date >= '2023-01-01' 
           |  AND partition_date < '2023-02-01'
           |  AND region = 'US'
         """.stripMargin)
      
      // Show query plan to verify partition pruning
      println("Query plan with partition pruning:")
      prunedQuery.queryExecution.executedPlan.foreach(plan => {
        println(plan.toString())
      })
      
      // Execute the query
      val result = prunedQuery.collect()
      println(s"Query returned ${result.length} rows")
    }
    
    // Analyze and optimize partition evolution
    def optimizePartitionEvolution(tableName: String): Unit = {
      println(s"Optimizing partition evolution for table: $tableName")
      
      // Get the Iceberg table
      val tableIdent = Spark3Util.identifierToTable(spark, s"iceberg_catalog.$tableName")
      val table = Spark3Util.loadIcebergTable(spark, tableIdent)
      
      // Show current partition spec
      println(s"Current partition spec: ${table.spec()}")
      
      // Example of adding a new partition field
      // This would typically be done when data patterns change
      spark.sql(
        s"""
           |ALTER TABLE iceberg_catalog.$tableName 
           |ADD PARTITION FIELD days(event_timestamp) AS event_day
         """.stripMargin)
      
      println("Added event_day partition field for better time-based queries")
    }
    
    // Execute partition optimization strategies
    analyzePartitioning("web_events")
    optimizePartitioning("sales_data", Seq("region", "category"))
    implementPartitionPruning("web_events")
    optimizePartitionEvolution("user_activity")
    
    spark.stop()
  }
}