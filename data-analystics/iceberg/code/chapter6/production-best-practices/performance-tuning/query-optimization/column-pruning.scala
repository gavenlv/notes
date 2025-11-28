// Column Pruning Optimization for Iceberg Queries
// ==============================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object ColumnPruningOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Column Pruning Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.optimizer.projectStarRetentionStrategy", "spark2")
      .getOrCreate()

    import spark.implicits._

    // Demonstrate column pruning in SELECT statements
    def demonstrateSelectPruning(): Unit = {
      println("Demonstrating column pruning in SELECT statements...")
      
      // Query selecting only needed columns - should prune unused columns
      val prunedQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT customer_id, sale_amount, sale_date
          |FROM iceberg_catalog.sales_data
          |WHERE sale_amount > 1000
        """.stripMargin)
      
      println("Query plan with column pruning:")
      prunedQuery.show(false)
    }
    
    // Demonstrate column pruning in aggregations
    def demonstrateAggregationPruning(): Unit = {
      println("Demonstrating column pruning in aggregations...")
      
      // Aggregation query - should prune non-aggregated, non-grouped columns
      val aggregationQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT region, category, SUM(sale_amount) as total_sales, COUNT(*) as transaction_count
          |FROM iceberg_catalog.sales_data
          |WHERE sale_date >= '2023-01-01'
          |GROUP BY region, category
        """.stripMargin)
      
      println("Query plan with aggregation column pruning:")
      aggregationQuery.show(false)
    }
    
    // Demonstrate column pruning in joins
    def demonstrateJoinPruning(): Unit = {
      println("Demonstrating column pruning in joins...")
      
      // Join query - should prune columns not needed in final result
      val joinQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT s.customer_id, s.sale_amount, c.customer_name
          |FROM iceberg_catalog.sales_data s
          |JOIN iceberg_catalog.customer_data c ON s.customer_id = c.customer_id
          |WHERE s.sale_amount > 500
        """.stripMargin)
      
      println("Query plan with join column pruning:")
      joinQuery.show(false)
    }
    
    // Demonstrate column pruning with nested structures
    def demonstrateNestedPruning(): Unit = {
      println("Demonstrating column pruning with nested structures...")
      
      // Query with nested fields - should prune unused nested fields
      val nestedQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT customer_id, address.street, address.city
          |FROM iceberg_catalog.customer_data
          |WHERE status = 'active'
        """.stripMargin)
      
      println("Query plan with nested column pruning:")
      nestedQuery.show(false)
    }
    
    // Compare performance with and without column pruning
    def compareColumnPruningPerformance(): Unit = {
      println("Comparing performance with and without column pruning...")
      
      // Enable timing
      spark.conf.set("spark.sql.adaptive.enabled", "true")
      
      // Query selecting all columns (no pruning)
      val startTime1 = System.currentTimeMillis()
      val result1 = spark.sql(
        """
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE sale_amount > 1000
        """.stripMargin).count()
      val endTime1 = System.currentTimeMillis()
      
      println(s"Query without column pruning took ${endTime1 - startTime1} ms, returned $result1 rows")
      
      // Query selecting only needed columns (with pruning)
      val startTime2 = System.currentTimeMillis()
      val result2 = spark.sql(
        """
          |SELECT customer_id, sale_amount, sale_date
          |FROM iceberg_catalog.sales_data
          |WHERE sale_amount > 1000
        """.stripMargin).count()
      val endTime2 = System.currentTimeMillis()
      
      println(s"Query with column pruning took ${endTime2 - startTime2} ms, returned $result2 rows")
    }
    
    // Demonstrate column pruning with file format optimizations
    def demonstrateFormatOptimizations(): Unit = {
      println("Demonstrating column pruning with file format optimizations...")
      
      // Enable Parquet column projection
      spark.conf.set("spark.sql.parquet.filterPushdown", "true")
      spark.conf.set("spark.sql.parquet.pushdown.inFilterThreshold", "1000")
      
      // Query that benefits from Parquet column projection
      val parquetQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT customer_id, product_id, sale_amount
          |FROM iceberg_catalog.sales_data
          |WHERE sale_date >= '2023-01-01'
        """.stripMargin)
      
      println("Query plan with Parquet column projection:")
      parquetQuery.show(false)
    }
    
    // Demonstrate column pruning in subqueries
    def demonstrateSubqueryPruning(): Unit = {
      println("Demonstrating column pruning in subqueries...")
      
      // Subquery with column pruning
      val subquery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT customer_id, customer_name
          |FROM iceberg_catalog.customer_data
          |WHERE customer_id IN (
          |  SELECT DISTINCT customer_id
          |  FROM iceberg_catalog.sales_data
          |  WHERE sale_amount > 1000
          |)
        """.stripMargin)
      
      println("Query plan with subquery column pruning:")
      subquery.show(false)
    }
    
    // Execute all column pruning demonstrations
    demonstrateSelectPruning()
    demonstrateAggregationPruning()
    demonstrateJoinPruning()
    demonstrateNestedPruning()
    compareColumnPruningPerformance()
    demonstrateFormatOptimizations()
    demonstrateSubqueryPruning()
    
    spark.stop()
  }
}