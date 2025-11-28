// Data Quality Monitor for Iceberg Tables
// ===================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import java.time.LocalDateTime
import java.util.UUID

object DataQualityMonitor {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Data Quality Monitor")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .getOrCreate()

    import spark.implicits._

    // Case class for data quality metrics
    case class DataQualityMetric(
      metricId: String,
      tableName: String,
      columnName: String,
      metricType: String,
      value: Double,
      threshold: Double,
      status: String,
      timestamp: LocalDateTime,
      details: Map[String, String]
    )

    // Initialize data quality metrics table
    def initializeQualityMetricsTable(): Unit = {
      println("Initializing data quality metrics table...")
      
      val metricsSchema = StructType(Seq(
        StructField("metric_id", StringType, nullable = false),
        StructField("table_name", StringType, nullable = false),
        StructField("column_name", StringType, nullable = true),
        StructField("metric_type", StringType, nullable = false),
        StructField("value", DoubleType, nullable = false),
        StructField("threshold", DoubleType, nullable = false),
        StructField("status", StringType, nullable = false),
        StructField("timestamp", TimestampType, nullable = false),
        StructField("details", MapType(StringType, StringType), nullable = true)
      ))
      
      spark.createDataFrame(spark.sparkContext.emptyRDD[Row], metricsSchema)
        .write
        .format("iceberg")
        .mode("ignore")
        .save("iceberg_catalog.data_quality_metrics")
      
      println("Data quality metrics table initialized")
    }
    
    // Calculate completeness metrics
    def calculateCompleteness(tableName: String, columns: Seq[String]): Unit = {
      println(s"Calculating completeness for table: $tableName")
      
      val table = spark.table(tableName)
      val totalRows = table.count()
      
      columns.foreach { column =>
        val nonNullCount = table.filter(col(column).isNotNull).count()
        val completeness = nonNullCount.toDouble / totalRows
        val threshold = 0.99 // 99% completeness required
        val status = if (completeness >= threshold) "PASS" else "FAIL"
        
        val metricId = UUID.randomUUID().toString
        val timestamp = LocalDateTime.now()
        
        val qualityMetric = DataQualityMetric(
          metricId,
          tableName,
          column,
          "completeness",
          completeness,
          threshold,
          status,
          timestamp,
          Map("total_rows" -> totalRows.toString, "non_null_count" -> nonNullCount.toString)
        )
        
        // Save metric
        val metricDF = Seq(qualityMetric).toDF()
        metricDF.write
          .format("iceberg")
          .mode("append")
          .save("iceberg_catalog.data_quality_metrics")
        
        println(s"Completeness for $column: $completeness (Status: $status)")
      }
    }
    
    // Calculate accuracy metrics
    def calculateAccuracy(tableName: String, rules: Seq[Map[String, Any]]): Unit = {
      println(s"Calculating accuracy for table: $tableName")
      
      val table = spark.table(tableName)
      val totalRows = table.count()
      
      rules.foreach { rule =>
        val column = rule("column").asInstanceOf[String]
        val condition = rule("condition").asInstanceOf[String]
        val threshold = rule("threshold").asInstanceOf[Double]
        
        // Apply condition to filter valid rows
        val validRows = table.where(condition).count()
        val accuracy = validRows.toDouble / totalRows
        val status = if (accuracy >= threshold) "PASS" else "FAIL"
        
        val metricId = UUID.randomUUID().toString
        val timestamp = LocalDateTime.now()
        
        val qualityMetric = DataQualityMetric(
          metricId,
          tableName,
          column,
          "accuracy",
          accuracy,
          threshold,
          status,
          timestamp,
          Map("total_rows" -> totalRows.toString, "valid_rows" -> validRows.toString, "condition" -> condition)
        )
        
        // Save metric
        val metricDF = Seq(qualityMetric).toDF()
        metricDF.write
          .format("iceberg")
          .mode("append")
          .save("iceberg_catalog.data_quality_metrics")
        
        println(s"Accuracy for $column with condition '$condition': $accuracy (Status: $status)")
      }
    }
    
    // Calculate consistency metrics
    def calculateConsistency(tableName: String, rules: Seq[Map[String, Any]]): Unit = {
      println(s"Calculating consistency for table: $tableName")
      
      val table = spark.table(tableName)
      val totalRows = table.count()
      
      rules.foreach { rule =>
        val column = rule("column").asInstanceOf[String]
        val pattern = rule("pattern").asInstanceOf[String]
        val threshold = rule("threshold").asInstanceOf[Double]
        
        // Count rows matching the pattern
        val validRows = table.filter(col(column).rlike(pattern)).count()
        val consistency = validRows.toDouble / totalRows
        val status = if (consistency >= threshold) "PASS" else "FAIL"
        
        val metricId = UUID.randomUUID().toString
        val timestamp = LocalDateTime.now()
        
        val qualityMetric = DataQualityMetric(
          metricId,
          tableName,
          column,
          "consistency",
          consistency,
          threshold,
          status,
          timestamp,
          Map("total_rows" -> totalRows.toString, "valid_rows" -> validRows.toString, "pattern" -> pattern)
        )
        
        // Save metric
        val metricDF = Seq(qualityMetric).toDF()
        metricDF.write
          .format("iceberg")
          .mode("append")
          .save("iceberg_catalog.data_quality_metrics")
        
        println(s"Consistency for $column with pattern '$pattern': $consistency (Status: $status)")
      }
    }
    
    // Calculate uniqueness metrics
    def calculateUniqueness(tableName: String, columns: Seq[String]): Unit = {
      println(s"Calculating uniqueness for table: $tableName")
      
      val table = spark.table(tableName)
      val totalRows = table.count()
      
      columns.foreach { column =>
        val distinctCount = table.select(col(column)).distinct().count()
        val uniqueness = distinctCount.toDouble / totalRows
        val threshold = 1.0 // 100% uniqueness required
        val status = if (uniqueness >= threshold) "PASS" else "FAIL"
        
        val metricId = UUID.randomUUID().toString
        val timestamp = LocalDateTime.now()
        
        val qualityMetric = DataQualityMetric(
          metricId,
          tableName,
          column,
          "uniqueness",
          uniqueness,
          threshold,
          status,
          timestamp,
          Map("total_rows" -> totalRows.toString, "distinct_count" -> distinctCount.toString)
        )
        
        // Save metric
        val metricDF = Seq(qualityMetric).toDF()
        metricDF.write
          .format("iceberg")
          .mode("append")
          .save("iceberg_catalog.data_quality_metrics")
        
        println(s"Uniqueness for $column: $uniqueness (Status: $status)")
      }
    }
    
    // Monitor data quality for a specific table
    def monitorTableQuality(tableName: String): Unit = {
      println(s"Monitoring data quality for table: $tableName")
      
      // Completeness checks
      calculateCompleteness(
        tableName,
        Seq("customer_id", "transaction_amount", "transaction_date")
      )
      
      // Accuracy checks
      val accuracyRules = Seq(
        Map(
          "column" -> "transaction_amount",
          "condition" -> "transaction_amount > 0",
          "threshold" -> 0.999
        ),
        Map(
          "column" -> "currency_code",
          "condition" -> "currency_code in ('USD', 'EUR', 'GBP', 'JPY', 'CAD')",
          "threshold" -> 1.0
        )
      )
      calculateAccuracy(tableName, accuracyRules)
      
      // Consistency checks
      val consistencyRules = Seq(
        Map(
          "column" -> "email",
          "pattern" -> "^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\\.[A-Za-z]{2,})$",
          "threshold" -> 0.99
        ),
        Map(
          "column" -> "phone",
          "pattern" -> "^\\+?[1-9]\\d{1,14}$",
          "threshold" -> 0.95
        )
      )
      calculateConsistency(tableName, consistencyRules)
      
      // Uniqueness checks
      calculateUniqueness(
        tableName,
        Seq("transaction_id")
      )
      
      println(s"Data quality monitoring completed for table: $tableName")
    }
    
    // Generate data quality report
    def generateQualityReport(tableName: String): Unit = {
      println(s"Generating data quality report for table: $tableName")
      
      val qualityReport = spark.sql(
        s"""
           |SELECT 
           |  metric_type,
           |  column_name,
           |  AVG(value) as avg_value,
           |  MIN(value) as min_value,
           |  MAX(value) as max_value,
           |  COUNT(CASE WHEN status = 'FAIL' THEN 1 END) as failure_count,
           |  COUNT(*) as total_checks
           |FROM iceberg_catalog.data_quality_metrics
           |WHERE table_name = '$tableName'
           |  AND timestamp >= date_sub(current_timestamp(), 7)
           |GROUP BY metric_type, column_name
           |ORDER BY metric_type, column_name
        """.stripMargin)
      
      println("Data Quality Report (Last 7 Days):")
      qualityReport.show(false)
    }
    
    // Alert on data quality issues
    def alertOnQualityIssues(): Unit = {
      println("Checking for data quality alerts...")
      
      val failedMetrics = spark.sql(
        """
          |SELECT 
          |  table_name,
          |  column_name,
          |  metric_type,
          |  value,
          |  threshold,
          |  timestamp,
          |  details
          |FROM iceberg_catalog.data_quality_metrics
          |WHERE status = 'FAIL'
          |  AND timestamp >= date_sub(current_timestamp(), 1)
          |ORDER BY timestamp DESC
        """.stripMargin)
      
      val failureCount = failedMetrics.count()
      
      if (failureCount > 0) {
        println(s"ALERT: $failureCount data quality issues detected in the last 24 hours!")
        failedMetrics.show(false)
        
        // In a real implementation, you would send alerts via email, Slack, etc.
      } else {
        println("No data quality issues detected in the last 24 hours.")
      }
    }
    
    // Execute all data quality monitoring functions
    initializeQualityMetricsTable()
    monitorTableQuality("iceberg_catalog.transactions")
    generateQualityReport("iceberg_catalog.transactions")
    alertOnQualityIssues()
    
    spark.stop()
  }
}