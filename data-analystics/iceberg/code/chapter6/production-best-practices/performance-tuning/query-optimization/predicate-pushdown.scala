// Predicate Pushdown Optimization for Iceberg Queries
// ==================================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

object PredicatePushdownOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Predicate Pushdown Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.optimizer.runtimeFilter.enabled", "true")
      .getOrCreate()

    import spark.implicits._

    // Demonstrate predicate pushdown with partition filters
    def demonstratePartitionPushdown(): Unit = {
      println("Demonstrating partition predicate pushdown...")
      
      // Query with partition filter - should be pushed down
      val partitionFilteredQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE sale_date >= '2023-01-01' 
          |  AND sale_date < '2023-02-01'
          |  AND region = 'US'
        """.stripMargin)
      
      println("Query plan with partition predicate pushdown:")
      partitionFilteredQuery.show(false)
    }
    
    // Demonstrate predicate pushdown with data filters
    def demonstrateDataPushdown(): Unit = {
      println("Demonstrating data predicate pushdown...")
      
      // Query with data column filters - should be pushed down to Parquet/ORC readers
      val dataFilteredQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT customer_id, product_id, sale_amount
          |FROM iceberg_catalog.sales_data
          |WHERE sale_amount > 1000 
          |  AND category IN ('Electronics', 'Books')
          |  AND status = 'completed'
        """.stripMargin)
      
      println("Query plan with data predicate pushdown:")
      dataFilteredQuery.show(false)
    }
    
    // Demonstrate advanced predicate pushdown with date functions
    def demonstrateDateFunctionPushdown(): Unit = {
      println("Demonstrating date function predicate pushdown...")
      
      // Query with date functions - should be optimized
      val dateFunctionQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT *
          |FROM iceberg_catalog.web_events
          |WHERE year(event_timestamp) = 2023
          |  AND month(event_timestamp) = 1
          |  AND dayofmonth(event_timestamp) BETWEEN 1 AND 7
        """.stripMargin)
      
      println("Query plan with date function pushdown:")
      dateFunctionQuery.show(false)
    }
    
    // Demonstrate join predicate pushdown
    def demonstrateJoinPushdown(): Unit = {
      println("Demonstrating join predicate pushdown...")
      
      // Join query with filters - should push predicates to both sides
      val joinQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT s.*, c.customer_name, c.email
          |FROM iceberg_catalog.sales_data s
          |JOIN iceberg_catalog.customer_data c ON s.customer_id = c.customer_id
          |WHERE s.sale_date >= '2023-01-01'
          |  AND s.sale_amount > 500
          |  AND c.status = 'active'
          |  AND c.region = 'US'
        """.stripMargin)
      
      println("Query plan with join predicate pushdown:")
      joinQuery.show(false)
    }
    
    // Demonstrate bloom filter usage for high cardinality columns
    def demonstrateBloomFilterUsage(): Unit = {
      println("Demonstrating bloom filter usage...")
      
      // Enable bloom filters for specific columns
      spark.sql(
        """
          |ALTER TABLE iceberg_catalog.sales_data 
          |SET TBLPROPERTIES (
          |  'read.parquet.bloom.filter.enabled#customer_id' = 'true',
          |  'read.parquet.bloom.filter.expected.ndv#customer_id' = '1000000'
          |)
        """.stripMargin)
      
      // Query that benefits from bloom filter
      val bloomFilterQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE customer_id IN (12345, 67890, 11111, 22222)
        """.stripMargin)
      
      println("Query plan with bloom filter optimization:")
      bloomFilterQuery.show(false)
    }
    
    // Compare performance with and without predicate pushdown
    def comparePerformance(): Unit = {
      println("Comparing performance with and without predicate pushdown...")
      
      // Enable timing
      spark.conf.set("spark.sql.adaptive.enabled", "true")
      
      // Query without effective pushdown
      val startTime1 = System.currentTimeMillis()
      val result1 = spark.sql(
        """
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE upper(customer_name) = 'JOHN DOE'
        """.stripMargin).count()
      val endTime1 = System.currentTimeMillis()
      
      println(s"Query without effective pushdown took ${endTime1 - startTime1} ms, returned $result1 rows")
      
      // Query with effective pushdown
      val startTime2 = System.currentTimeMillis()
      val result2 = spark.sql(
        """
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE customer_id = 12345
        """.stripMargin).count()
      val endTime2 = System.currentTimeMillis()
      
      println(s"Query with effective pushdown took ${endTime2 - startTime2} ms, returned $result2 rows")
    }
    
    // Execute all predicate pushdown demonstrations
    demonstratePartitionPushdown()
    demonstrateDataPushdown()
    demonstrateDateFunctionPushdown()
    demonstrateJoinPushdown()
    demonstrateBloomFilterUsage()
    comparePerformance()
    
    spark.stop()
  }
}