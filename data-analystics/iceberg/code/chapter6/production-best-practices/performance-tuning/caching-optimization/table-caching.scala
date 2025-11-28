// Table Caching Optimization for Iceberg Tables
// ===========================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import org.apache.iceberg.spark.actions.SparkActions
import org.apache.spark.storage.StorageLevel
import java.util.concurrent.TimeUnit

object TableCachingOptimization {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Table Caching Optimization")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .getOrCreate()

    import spark.implicits._

    // Configure caching settings
    def configureCachingSettings(): Unit = {
      println("Configuring caching settings...")
      
      // Set cache storage level
      spark.conf.set("spark.sql.cache.storageLevel", "MEMORY_AND_DISK_SER")
      
      // Configure cache expiration
      spark.conf.set("spark.sql.cache.expirationDuration", "24h")
      
      // Enable automatic cache cleanup
      spark.conf.set("spark.sql.cache.autoCleanup", "true")
      
      // Set cache serialization
      spark.conf.set("spark.sql.cache.serializer", "org.apache.spark.serializer.KryoSerializer")
      
      println("Caching settings configured")
    }
    
    // Implement table-level caching
    def implementTableLevelCaching(): Unit = {
      println("Implementing table-level caching...")
      
      // Cache frequently accessed table
      val cachedTable = spark.table("iceberg_catalog.frequent_access_table")
        .cache()
      
      // Perform operations on cached table
      val result = cachedTable
        .filter($"date" >= "2023-01-01")
        .groupBy($"category")
        .agg(sum("amount").as("total_amount"))
        .orderBy(desc("total_amount"))
      
      result.show()
      
      println("Table-level caching implemented")
    }
    
    // Implement partition-level caching
    def implementPartitionLevelCaching(): Unit = {
      println("Implementing partition-level caching...")
      
      // Read specific partitions
      val partitionedData = spark.read
        .format("iceberg")
        .load("iceberg_catalog.partitioned_table")
        .where($"year" === 2023 && $"month" === 12)
      
      // Cache the partitioned data
      partitionedData.persist(StorageLevel.MEMORY_AND_DISK_SER)
      
      // Perform analytics on cached partition
      val analyticsResult = partitionedData
        .groupBy($"customer_id")
        .agg(
          sum("transaction_amount").as("total_spent"),
          count("*").as("transaction_count")
        )
        .filter($"total_spent" > 1000)
      
      analyticsResult.show()
      
      // Unpersist when done
      partitionedData.unpersist()
      
      println("Partition-level caching implemented")
    }
    
    // Implement query result caching
    def implementQueryResultCaching(): Unit = {
      println("Implementing query result caching...")
      
      // Complex analytical query
      val complexQuery = spark.sql(
        """
          |SELECT 
          |  c.customer_name,
          |  p.product_category,
          |  SUM(t.amount) as total_sales,
          |  AVG(t.amount) as avg_transaction,
          |  COUNT(*) as transaction_count
          |FROM iceberg_catalog.transactions t
          |JOIN iceberg_catalog.customers c ON t.customer_id = c.customer_id
          |JOIN iceberg_catalog.products p ON t.product_id = p.product_id
          |WHERE t.transaction_date >= '2023-01-01'
          |GROUP BY c.customer_name, p.product_category
          |HAVING SUM(t.amount) > 10000
          |ORDER BY total_sales DESC
        """.stripMargin)
      
      // Cache the query result
      val cachedResult = complexQuery.cache()
      
      // Use cached result for multiple operations
      val topCustomers = cachedResult
        .filter($"product_category" === "Electronics")
        .limit(10)
      
      val categoryStats = cachedResult
        .groupBy($"product_category")
        .agg(
          sum("total_sales").as("category_total"),
          avg("avg_transaction").as("category_avg_transaction")
        )
      
      topCustomers.show()
      categoryStats.show()
      
      println("Query result caching implemented")
    }
    
    // Implement intelligent cache eviction
    def implementIntelligentCacheEviction(): Unit = {
      println("Implementing intelligent cache eviction...")
      
      // Create a DataFrame that will be cached
      val dataToCache = spark.table("iceberg_catalog.large_table")
        .filter($"date" >= "2023-06-01")
      
      // Cache with explicit storage level
      dataToCache.persist(StorageLevel.MEMORY_AND_DISK_SER_2)
      
      // Perform operations
      val dailyAggregates = dataToCache
        .groupBy($"date")
        .agg(
          sum("sales_amount").as("daily_sales"),
          countDistinct("customer_id").as("unique_customers")
        )
      
      dailyAggregates.show()
      
      // Check cache status
      val cacheStatus = spark.sharedState.cacheManager.cacheEntries
      println(s"Current cache entries: ${cacheStatus.size}")
      
      // Intelligent eviction based on usage frequency
      cacheStatus.foreach { entry =>
        val tableName = entry._1
        val cacheEntry = entry._2
        println(s"Table: $tableName, Memory Usage: ${cacheEntry.memSize}, Disk Usage: ${cacheEntry.diskSize}")
        
        // Evict if not accessed recently and large
        if (cacheEntry.memSize > 1024 * 1024 * 1024) { // 1GB threshold
          println(s"Consider evicting $tableName due to large memory footprint")
        }
      }
      
      println("Intelligent cache eviction implemented")
    }
    
    // Implement cache warming strategy
    def implementCacheWarming(): Unit = {
      println("Implementing cache warming strategy...")
      
      // List of tables to warm up
      val tablesToWarm = Seq(
        "iceberg_catalog.frequently_accessed_table",
        "iceberg_catalog.recent_transactions",
        "iceberg_catalog.customer_master"
      )
      
      // Warm up tables in parallel
      val warmUpFutures = tablesToWarm.map { tableName =>
        scala.concurrent.Future {
          println(s"Warming up table: $tableName")
          val table = spark.table(tableName)
          
          // Materialize the table in cache
          table.cache()
          
          // Trigger computation to load into memory
          val rowCount = table.count()
          println(s"Warmed up $tableName with $rowCount rows")
          
          table
        }(scala.concurrent.ExecutionContext.global)
      }
      
      // Wait for all warm-up operations to complete
      scala.concurrent.Await.ready(
        scala.concurrent.Future.sequence(warmUpFutures),
        scala.concurrent.duration.Duration(30, TimeUnit.SECONDS)
      )
      
      println("Cache warming completed")
    }
    
    // Monitor cache performance
    def monitorCachePerformance(): Unit = {
      println("Monitoring cache performance...")
      
      // Enable cache statistics
      spark.conf.set("spark.sql.cache.stats.enabled", "true")
      
      // Perform cached operations
      val cachedData = spark.table("iceberg_catalog.performance_test_table").cache()
      
      // Query 1 - Full scan
      val result1 = cachedData.filter($"amount" > 1000).count()
      println(s"Query 1 result: $result1")
      
      // Query 2 - Aggregation (should benefit from cache)
      val result2 = cachedData.groupBy($"category").agg(sum("amount")).count()
      println(s"Query 2 result: $result2")
      
      // Query 3 - Join (should benefit from cache)
      val lookupTable = spark.table("iceberg_catalog.lookup_table").cache()
      val result3 = cachedData.join(lookupTable, "category").count()
      println(s"Query 3 result: $result3")
      
      // Get cache statistics
      val cacheManager = spark.sharedState.cacheManager
      val cacheEntries = cacheManager.cacheEntries
      
      cacheEntries.foreach { case (tableName, cacheEntry) =>
        println(s"""
          |Table: $tableName
          |Memory Size: ${cacheEntry.memSize} bytes
          |Disk Size: ${cacheEntry.diskSize} bytes
          |Deserialized: ${cacheEntry.deserialized}
          |Storage Level: ${cacheEntry.storageLevel}
        """.stripMargin)
      }
      
      println("Cache performance monitoring completed")
    }
    
    // Execute all caching optimization techniques
    configureCachingSettings()
    implementTableLevelCaching()
    implementPartitionLevelCaching()
    implementQueryResultCaching()
    implementIntelligentCacheEviction()
    implementCacheWarming()
    monitorCachePerformance()
    
    spark.stop()
  }
}