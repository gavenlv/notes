// Bloom Filters Optimization for Iceberg Queries
// ============================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object BloomFiltersOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Bloom Filters Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.optimizer.runtime.bloomFilter.enabled", "true")
      .getOrCreate()

    import spark.implicits._

    // Configure bloom filters for high cardinality columns
    def configureBloomFilters(): Unit = {
      println("Configuring bloom filters for high cardinality columns...")
      
      // Enable bloom filters for customer_id column
      spark.sql(
        """
          |ALTER TABLE iceberg_catalog.sales_data 
          |SET TBLPROPERTIES (
          |  'read.parquet.bloom.filter.enabled#customer_id' = 'true',
          |  'read.parquet.bloom.filter.expected.ndv#customer_id' = '1000000'
          |)
        """.stripMargin)
      
      // Enable bloom filters for product_id column
      spark.sql(
        """
          |ALTER TABLE iceberg_catalog.sales_data 
          |SET TBLPROPERTIES (
          |  'read.parquet.bloom.filter.enabled#product_id' = 'true',
          |  'read.parquet.bloom.filter.expected.ndv#product_id' = '500000'
          |)
        """.stripMargin)
      
      // Enable bloom filters for order_id column
      spark.sql(
        """
          |ALTER TABLE iceberg_catalog.order_details 
          |SET TBLPROPERTIES (
          |  'read.parquet.bloom.filter.enabled#order_id' = 'true',
          |  'read.parquet.bloom.filter.expected.ndv#order_id' = '2000000'
          |)
        """.stripMargin)
      
      println("Bloom filters configured for key columns")
    }
    
    // Demonstrate bloom filter usage in point lookups
    def demonstratePointLookupOptimization(): Unit = {
      println("Demonstrating bloom filter usage in point lookups...")
      
      // Point lookup query that benefits from bloom filters
      val pointLookupQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE customer_id = 123456
        """.stripMargin)
      
      println("Query plan with bloom filter optimization for point lookup:")
      pointLookupQuery.show(false)
    }
    
    // Demonstrate bloom filter usage in IN clauses
    def demonstrateInClauseOptimization(): Unit = {
      println("Demonstrating bloom filter usage in IN clauses...")
      
      // IN clause query that benefits from bloom filters
      val inClauseQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE customer_id IN (12345, 67890, 11111, 22222, 33333, 44444, 55555, 66666, 77777, 88888)
        """.stripMargin)
      
      println("Query plan with bloom filter optimization for IN clause:")
      inClauseQuery.show(false)
    }
    
    // Demonstrate bloom filter usage in joins
    def demonstrateJoinOptimization(): Unit = {
      println("Demonstrating bloom filter usage in joins...")
      
      // Join query that benefits from bloom filters
      val joinQuery = spark.sql(
        """
          |EXPLAIN EXTENDED
          |SELECT s.*, c.customer_name
          |FROM iceberg_catalog.sales_data s
          |JOIN iceberg_catalog.customer_data c ON s.customer_id = c.customer_id
          |WHERE s.sale_amount > 1000
        """.stripMargin)
      
      println("Query plan with bloom filter optimization for join:")
      joinQuery.show(false)
    }
    
    // Compare performance with and without bloom filters
    def compareBloomFilterPerformance(): Unit = {
      println("Comparing performance with and without bloom filters...")
      
      // Disable bloom filters for comparison
      spark.conf.set("spark.sql.optimizer.runtime.bloomFilter.enabled", "false")
      
      // Query without bloom filters
      val startTime1 = System.currentTimeMillis()
      val result1 = spark.sql(
        """
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE customer_id IN (12345, 67890, 11111, 22222, 33333)
        """.stripMargin).count()
      val endTime1 = System.currentTimeMillis()
      
      println(s"Query without bloom filters took ${endTime1 - startTime1} ms, returned $result1 rows")
      
      // Enable bloom filters
      spark.conf.set("spark.sql.optimizer.runtime.bloomFilter.enabled", "true")
      
      // Same query with bloom filters
      val startTime2 = System.currentTimeMillis()
      val result2 = spark.sql(
        """
          |SELECT *
          |FROM iceberg_catalog.sales_data
          |WHERE customer_id IN (12345, 67890, 11111, 22222, 33333)
        """.stripMargin).count()
      val endTime2 = System.currentTimeMillis()
      
      println(s"Query with bloom filters took ${endTime2 - startTime2} ms, returned $result2 rows")
    }
    
    // Analyze bloom filter effectiveness
    def analyzeBloomFilterEffectiveness(): Unit = {
      println("Analyzing bloom filter effectiveness...")
      
      // Check bloom filter statistics
      val bloomStats = spark.sql(
        """
          |SELECT 
          |  file_path,
          |  column_name,
          |  bloom_filter_length,
          |  bloom_filter_bit_count,
          |  bloom_filter_hash_count
          |FROM iceberg_catalog.sales_data.bloom_filters
        """.stripMargin)
      
      println("Bloom filter statistics:")
      bloomStats.show(false)
    }
    
    // Optimize bloom filter settings based on data characteristics
    def optimizeBloomFilterSettings(): Unit = {
      println("Optimizing bloom filter settings based on data characteristics...")
      
      // Analyze column cardinality
      val cardinalityStats = spark.sql(
        """
          |SELECT 
          |  COUNT(DISTINCT customer_id) as distinct_customers,
          |  COUNT(DISTINCT product_id) as distinct_products,
          |  COUNT(*) as total_rows
          |FROM iceberg_catalog.sales_data
        """.stripMargin)
      
      val stats = cardinalityStats.collect()(0)
      val distinctCustomers = stats.getLong(0)
      val distinctProducts = stats.getLong(1)
      val totalRows = stats.getLong(2)
      
      println(s"Column cardinality analysis:")
      println(s"  Distinct customers: $distinctCustomers")
      println(s"  Distinct products: $distinctProducts")
      println(s"  Total rows: $totalRows")
      
      // Adjust bloom filter settings based on actual cardinality
      val optimalCustomerNDV = distinctCustomers
      val optimalProductNDV = distinctProducts
      
      spark.sql(
        s"""
          |ALTER TABLE iceberg_catalog.sales_data 
          |SET TBLPROPERTIES (
          |  'read.parquet.bloom.filter.expected.ndv#customer_id' = '$optimalCustomerNDV',
          |  'read.parquet.bloom.filter.expected.ndv#product_id' = '$optimalProductNDV'
          |)
        """.stripMargin)
      
      println("Bloom filter settings optimized based on actual data characteristics")
    }
    
    // Execute all bloom filter optimization demonstrations
    configureBloomFilters()
    demonstratePointLookupOptimization()
    demonstrateInClauseOptimization()
    demonstrateJoinOptimization()
    compareBloomFilterPerformance()
    analyzeBloomFilterEffectiveness()
    optimizeBloomFilterSettings()
    
    spark.stop()
  }
}