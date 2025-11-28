// Data Lineage Tracker for Iceberg Tables
// ====================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.TableIdentifier
import java.time.LocalDateTime
import java.util.UUID

object DataLineageTracker {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Data Lineage Tracker")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .getOrCreate()

    import spark.implicits._

    // Case class for lineage events
    case class LineageEvent(
      eventId: String,
      timestamp: LocalDateTime,
      operation: String,
      sourceTables: Seq[String],
      targetTable: String,
      jobId: String,
      jobName: String,
      userName: String,
      metadata: Map[String, String]
    )

    // Initialize lineage tracking table
    def initializeLineageTracking(): Unit = {
      println("Initializing lineage tracking table...")
      
      // Create lineage tracking table if it doesn't exist
      val lineageSchema = StructType(Seq(
        StructField("event_id", StringType, nullable = false),
        StructField("timestamp", TimestampType, nullable = false),
        StructField("operation", StringType, nullable = false),
        StructField("source_tables", ArrayType(StringType), nullable = true),
        StructField("target_table", StringType, nullable = false),
        StructField("job_id", StringType, nullable = false),
        StructField("job_name", StringType, nullable = false),
        StructField("user_name", StringType, nullable = false),
        StructField("metadata", MapType(StringType, StringType), nullable = true)
      ))
      
      // Create the lineage table
      spark.createDataFrame(spark.sparkContext.emptyRDD[Row], lineageSchema)
        .write
        .format("iceberg")
        .mode("ignore")
        .save("iceberg_catalog.data_lineage")
      
      println("Lineage tracking table initialized")
    }
    
    // Track data transformation
    def trackTransformation(
      sourceTables: Seq[String],
      targetTable: String,
      operation: String,
      jobName: String,
      additionalMetadata: Map[String, String] = Map.empty
    ): Unit = {
      val eventId = UUID.randomUUID().toString
      val timestamp = LocalDateTime.now()
      val jobId = spark.sparkContext.applicationId
      val userName = System.getProperty("user.name")
      
      val lineageEvent = LineageEvent(
        eventId,
        timestamp,
        operation,
        sourceTables,
        targetTable,
        jobId,
        jobName,
        userName,
        additionalMetadata
      )
      
      // Convert to DataFrame and append to lineage table
      val lineageDF = Seq(lineageEvent).toDF()
      
      lineageDF.write
        .format("iceberg")
        .mode("append")
        .save("iceberg_catalog.data_lineage")
      
      println(s"Tracked lineage event: $operation from ${sourceTables.mkString(",")} to $targetTable")
    }
    
    // Track ETL pipeline
    def trackETLPipeline(): Unit = {
      println("Tracking ETL pipeline...")
      
      // Stage 1: Raw data ingestion
      trackTransformation(
        sourceTables = Seq("external:kafka:transactions"),
        targetTable = "iceberg_catalog.raw_transactions",
        operation = "INGEST",
        jobName = "raw-data-ingestion",
        additionalMetadata = Map(
          "source_type" -> "kafka",
          "topic" -> "transactions",
          "format" -> "json"
        )
      )
      
      // Stage 2: Data cleaning
      trackTransformation(
        sourceTables = Seq("iceberg_catalog.raw_transactions"),
        targetTable = "iceberg_catalog.cleaned_transactions",
        operation = "TRANSFORM",
        jobName = "data-cleaning-pipeline",
        additionalMetadata = Map(
          "transformation_type" -> "data_cleaning",
          "rules_applied" -> "duplicate_removal,format_normalization,null_handling"
        )
      )
      
      // Stage 3: Enrichment
      trackTransformation(
        sourceTables = Seq("iceberg_catalog.cleaned_transactions", "iceberg_catalog.customer_master"),
        targetTable = "iceberg_catalog.enriched_transactions",
        operation = "ENRICH",
        jobName = "data-enrichment-pipeline",
        additionalMetadata = Map(
          "enrichment_sources" -> "customer_master,dim_product,dim_location",
          "derived_columns" -> "customer_segment,product_category,region"
        )
      )
      
      // Stage 4: Aggregation
      trackTransformation(
        sourceTables = Seq("iceberg_catalog.enriched_transactions"),
        targetTable = "iceberg_catalog.daily_summary",
        operation = "AGGREGATE",
        jobName = "daily-aggregation-pipeline",
        additionalMetadata = Map(
          "aggregation_granularity" -> "daily",
          "metrics_computed" -> "transaction_count,total_amount,average_ticket_size"
        )
      )
      
      println("ETL pipeline tracking completed")
    }
    
    // Track ML model training
    def trackMLTraining(): Unit = {
      println("Tracking ML model training...")
      
      // Feature engineering
      trackTransformation(
        sourceTables = Seq("iceberg_catalog.enriched_transactions", "iceberg_catalog.customer_behavior"),
        targetTable = "iceberg_catalog.model_features",
        operation = "FEATURE_ENGINEERING",
        jobName = "feature-engineering-pipeline",
        additionalMetadata = Map(
          "features_created" -> "customer_lifetime_value,purchase_frequency,average_order_value",
          "techniques_used" -> "window_functions,aggregations,normalization"
        )
      )
      
      // Model training
      trackTransformation(
        sourceTables = Seq("iceberg_catalog.model_features"),
        targetTable = "iceberg_catalog.trained_model:v1.2",
        operation = "MODEL_TRAINING",
        jobName = "model-training-pipeline",
        additionalMetadata = Map(
          "algorithm" -> "random_forest",
          "hyperparameters" -> "trees=100,max_depth=10,min_samples_split=5",
          "evaluation_metrics" -> "accuracy=0.92,precision=0.89,recall=0.91"
        )
      )
      
      // Model validation
      trackTransformation(
        sourceTables = Seq("iceberg_catalog.trained_model:v1.2", "iceberg_catalog.validation_dataset"),
        targetTable = "iceberg_catalog.model_validation_results",
        operation = "MODEL_VALIDATION",
        jobName = "model-validation-pipeline",
        additionalMetadata = Map(
          "validation_approach" -> "cross_validation",
          "test_dataset_size" -> "10000",
          "validation_passed" -> "true"
        )
      )
      
      println("ML training tracking completed")
    }
    
    // Query lineage information
    def queryLineage(tableName: String): Unit = {
      println(s"Querying lineage for table: $tableName")
      
      // Upstream lineage (what feeds into this table)
      val upstreamLineage = spark.sql(
        s"""
           |SELECT 
           |  operation,
           |  source_tables,
           |  job_name,
           |  timestamp,
           |  user_name
           |FROM iceberg_catalog.data_lineage
           |WHERE target_table = '$tableName'
           |ORDER BY timestamp DESC
        """.stripMargin)
      
      println("Upstream lineage:")
      upstreamLineage.show(false)
      
      // Downstream lineage (what this table feeds into)
      val downstreamLineage = spark.sql(
        s"""
           |SELECT 
           |  operation,
           |  target_table,
           |  job_name,
           |  timestamp,
           |  user_name
           |FROM iceberg_catalog.data_lineage
           |WHERE array_contains(source_tables, '$tableName')
           |ORDER BY timestamp DESC
        """.stripMargin)
      
      println("Downstream lineage:")
      downstreamLineage.show(false)
    }
    
    // Generate lineage report
    def generateLineageReport(): Unit = {
      println("Generating lineage report...")
      
      // Full lineage graph
      val fullLineage = spark.sql(
        """
          |SELECT 
          |  source_tables,
          |  target_table,
          |  operation,
          |  job_name,
          |  timestamp,
          |  user_name
          |FROM iceberg_catalog.data_lineage
          |ORDER BY timestamp DESC
        """.stripMargin)
      
      println("Full lineage report:")
      fullLineage.show(false)
      
      // Impact analysis for a specific table
      val impactAnalysis = spark.sql(
        """
          |WITH RECURSIVE downstream_chain AS (
          |  SELECT 
          |    target_table as affected_table,
          |    1 as level
          |  FROM iceberg_catalog.data_lineage
          |  WHERE array_contains(source_tables, 'iceberg_catalog.raw_transactions')
          |  
          |  UNION ALL
          |  
          |  SELECT 
          |    dl.target_table,
          |    dc.level + 1
          |  FROM iceberg_catalog.data_lineage dl
          |  JOIN downstream_chain dc ON array_contains(dl.source_tables, dc.affected_table)
          |  WHERE dc.level < 5 -- Limit recursion depth
          |)
          |SELECT DISTINCT affected_table, level
          |FROM downstream_chain
          |ORDER BY level, affected_table
        """.stripMargin)
      
      println("Impact analysis for raw_transactions table:")
      impactAnalysis.show(false)
    }
    
    // Execute all lineage tracking functions
    initializeLineageTracking()
    trackETLPipeline()
    trackMLTraining()
    queryLineage("iceberg_catalog.daily_summary")
    generateLineageReport()
    
    spark.stop()
  }
}