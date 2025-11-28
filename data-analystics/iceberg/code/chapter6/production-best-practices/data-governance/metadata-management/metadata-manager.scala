// Metadata Manager for Iceberg Tables
// ===================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.hadoop.HadoopCatalog
import java.time.LocalDateTime
import java.util.Properties
import scala.collection.JavaConverters._

object MetadataManager {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Metadata Manager")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .getOrCreate()

    import spark.implicits._

    // Case class for metadata information
    case class TableMetadataInfo(
      tableName: String,
      namespace: String,
      location: String,
      formatVersion: Int,
      specId: Int,
      schemaId: Int,
      snapshotId: Long,
      totalRecords: Long,
      totalFiles: Int,
      lastUpdated: LocalDateTime
    )

    // Initialize Hadoop catalog for low-level metadata operations
    def initializeHadoopCatalog(): HadoopCatalog = {
      val conf = spark.sparkContext.hadoopConfiguration
      val catalog = new HadoopCatalog(conf, "hdfs://namenode:9000/warehouse")
      catalog
    }

    // Get detailed metadata for a specific table
    def getTableMetadata(tableName: String): Unit = {
      println(s"Retrieving metadata for table: $tableName")
      
      val catalog = initializeHadoopCatalog()
      val tableIdentifier = TableIdentifier.parse(tableName)
      val table = catalog.loadTable(tableIdentifier)
      
      // Basic metadata
      val location = table.location()
      val formatVersion = table.properties().getOrDefault("format-version", "1").toInt
      val specId = table.spec().specId()
      val schemaId = table.schema().schemaId()
      
      // Snapshot information
      val currentSnapshot = table.currentSnapshot()
      val snapshotId = if (currentSnapshot != null) currentSnapshot.snapshotId() else -1L
      
      // Statistics
      var totalRecords = 0L
      var totalFiles = 0
      if (currentSnapshot != null) {
        totalRecords = currentSnapshot.summary().getOrDefault("total-records", "0").toLong
        totalFiles = currentSnapshot.summary().getOrDefault("total-data-files", "0").toInt
      }
      
      val lastUpdated = if (currentSnapshot != null) {
        LocalDateTime.ofInstant(
          java.time.Instant.ofEpochMilli(currentSnapshot.timestampMillis()),
          java.time.ZoneId.systemDefault()
        )
      } else {
        LocalDateTime.now()
      }
      
      val metadataInfo = TableMetadataInfo(
        tableName,
        tableIdentifier.namespace().toString,
        location,
        formatVersion,
        specId,
        schemaId,
        snapshotId,
        totalRecords,
        totalFiles,
        lastUpdated
      )
      
      println(s"Table: ${metadataInfo.tableName}")
      println(s"Namespace: ${metadataInfo.namespace}")
      println(s"Location: ${metadataInfo.location}")
      println(s"Format Version: ${metadataInfo.formatVersion}")
      println(s"Spec ID: ${metadataInfo.specId}")
      println(s"Schema ID: ${metadataInfo.schemaId}")
      println(s"Current Snapshot ID: ${metadataInfo.snapshotId}")
      println(s"Total Records: ${metadataInfo.totalRecords}")
      println(s"Total Files: ${metadataInfo.totalFiles}")
      println(s"Last Updated: ${metadataInfo.lastUpdated}")
      
      catalog.close()
    }

    // List all tables in a namespace
    def listTables(namespace: String): Unit = {
      println(s"Listing tables in namespace: $namespace")
      
      val catalog = initializeHadoopCatalog()
      val namespaceIdentifier = org.apache.iceberg.catalog.Namespace.of(namespace.split("\\."): _*)
      val tables = catalog.listTables(namespaceIdentifier).asScala
      
      println("Tables:")
      tables.foreach { tableIdentifier =>
        println(s"  - ${tableIdentifier.name()}")
      }
      
      catalog.close()
    }

    // Get schema information for a table
    def getTableSchema(tableName: String): Unit = {
      println(s"Retrieving schema for table: $tableName")
      
      val table = spark.table(tableName)
      val schema = table.schema()
      
      println("Schema:")
      schema.fields.foreach { field =>
        println(s"  ${field.name}: ${field.dataType} (nullable: ${field.nullable})")
      }
    }

    // Get partition information for a table
    def getPartitionInfo(tableName: String): Unit = {
      println(s"Retrieving partition information for table: $tableName")
      
      val catalog = initializeHadoopCatalog()
      val tableIdentifier = TableIdentifier.parse(tableName)
      val table = catalog.loadTable(tableIdentifier)
      
      val specs = table.specs().asScala
      println("Partition Specs:")
      specs.foreach { case (specId, spec) =>
        println(s"  Spec ID: $specId")
        val fields = spec.fields().asScala
        fields.foreach { field =>
          println(s"    - ${field.name} (source-id: ${field.sourceId}, transform: ${field.transform})")
        }
      }
      
      catalog.close()
    }

    // Get snapshot history for a table
    def getSnapshotHistory(tableName: String): Unit = {
      println(s"Retrieving snapshot history for table: $tableName")
      
      val catalog = initializeHadoopCatalog()
      val tableIdentifier = TableIdentifier.parse(tableName)
      val table = catalog.loadTable(tableIdentifier)
      
      val snapshots = table.snapshots().asScala.toList.reverse
      println("Snapshot History (most recent first):")
      snapshots.foreach { snapshot =>
        val timestamp = LocalDateTime.ofInstant(
          java.time.Instant.ofEpochMilli(snapshot.timestampMillis()),
          java.time.ZoneId.systemDefault()
        )
        println(s"  Snapshot ID: ${snapshot.snapshotId()}")
        println(s"    Timestamp: $timestamp")
        println(s"    Operation: ${snapshot.operation()}")
        println(s"    Summary: ${snapshot.summary().asScala.toMap}")
        println()
      }
      
      catalog.close()
    }

    // Export metadata to a JSON file
    def exportMetadata(tableName: String, outputPath: String): Unit = {
      println(s"Exporting metadata for table: $tableName to $outputPath")
      
      val catalog = initializeHadoopCatalog()
      val tableIdentifier = TableIdentifier.parse(tableName)
      val table = catalog.loadTable(tableIdentifier)
      
      // Collect metadata information
      val metadata = Map(
        "table_name" -> tableName,
        "location" -> table.location(),
        "format_version" -> table.properties().getOrDefault("format-version", "1"),
        "schema" -> table.schema().toString,
        "partition_specs" -> table.spec().toString,
        "properties" -> table.properties().asScala.toMap,
        "current_snapshot_id" -> (if (table.currentSnapshot() != null) table.currentSnapshot().snapshotId().toString else "null"),
        "snapshots_count" -> table.snapshots().asScala.size.toString
      )
      
      // Convert to DataFrame and save as JSON
      val metadataDF = Seq(metadata).toDF()
      metadataDF.coalesce(1)
        .write
        .mode("overwrite")
        .json(outputPath)
      
      println(s"Metadata exported to: $outputPath")
      catalog.close()
    }

    // Update table properties
    def updateTableProperties(tableName: String, properties: Map[String, String]): Unit = {
      println(s"Updating properties for table: $tableName")
      
      val propertyUpdates = properties.map { case (k, v) => s"'$k' = '$v'" }.mkString(", ")
      val sql = s"ALTER TABLE $tableName SET TBLPROPERTIES ($propertyUpdates)"
      
      println(s"Executing: $sql")
      spark.sql(sql)
      
      println("Table properties updated successfully")
    }

    // Create metadata summary table
    def createMetadataSummaryTable(): Unit = {
      println("Creating metadata summary table...")
      
      val summarySchema = StructType(Seq(
        StructField("table_name", StringType, nullable = false),
        StructField("namespace", StringType, nullable = false),
        StructField("location", StringType, nullable = false),
        StructField("format_version", IntegerType, nullable = false),
        StructField("total_records", LongType, nullable = false),
        StructField("total_files", IntegerType, nullable = false),
        StructField("last_updated", TimestampType, nullable = false),
        StructField("partition_columns", StringType, nullable = true)
      ))
      
      spark.createDataFrame(spark.sparkContext.emptyRDD[Row], summarySchema)
        .write
        .format("iceberg")
        .mode("ignore")
        .save("iceberg_catalog.metadata_summary")
      
      println("Metadata summary table created")
    }

    // Refresh metadata summary
    def refreshMetadataSummary(): Unit = {
      println("Refreshing metadata summary...")
      
      // This would typically scan all tables and collect their metadata
      // For demonstration, we'll just show the concept
      val sampleData = Seq(
        ("transactions", "iceberg_catalog", "hdfs://namenode:9000/warehouse/transactions", 2, 1000000L, 120, java.sql.Timestamp.valueOf(LocalDateTime.now()), "date,currency"),
        ("customers", "iceberg_catalog", "hdfs://namenode:9000/warehouse/customers", 2, 50000L, 15, java.sql.Timestamp.valueOf(LocalDateTime.now()), "region"),
        ("products", "iceberg_catalog", "hdfs://namenode:9000/warehouse/products", 2, 10000L, 5, java.sql.Timestamp.valueOf(LocalDateTime.now()), "category")
      ).toDF("table_name", "namespace", "location", "format_version", "total_records", "total_files", "last_updated", "partition_columns")
      
      sampleData.write
        .format("iceberg")
        .mode("overwrite")
        .save("iceberg_catalog.metadata_summary")
      
      println("Metadata summary refreshed")
    }

    // Execute all metadata management functions
    createMetadataSummaryTable()
    refreshMetadataSummary()
    
    // Example operations on a specific table
    val tableName = "iceberg_catalog.transactions"
    getTableMetadata(tableName)
    getTableSchema(tableName)
    getPartitionInfo(tableName)
    getSnapshotHistory(tableName)
    listTables("iceberg_catalog")
    
    // Export metadata example
    exportMetadata(tableName, "hdfs://namenode:9000/metadata_exports/transactions_metadata.json")
    
    // Update properties example
    val newProperties = Map(
      "owner" -> "data-team",
      "department" -> "analytics",
      "pii_data" -> "true",
      "retention_days" -> "365"
    )
    updateTableProperties(tableName, newProperties)
    
    spark.stop()
  }
}