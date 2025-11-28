/*
 * Spark Iceberg 与 Apache Atlas 集成示例
 * 
 * 本示例演示如何在 Spark 中配置 Iceberg 与 Apache Atlas 集成，
 * 实现数据治理和血缘追踪功能。
 */

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.atlas.AtlasClientV2
import org.apache.atlas.model.instance.AtlasEntity
import org.apache.atlas.model.instance.AtlasObjectId

object SparkIcebergAtlasIntegration {
  def main(args: Array[String]): Unit = {
    // 1. 创建 Spark Session 并配置 Iceberg 与 Atlas 集成
    val spark = SparkSession.builder()
      .appName("Spark Iceberg Atlas Integration")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
      .config("spark.sql.catalog.spark_catalog.type", "hadoop")
      .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
      // Atlas 集成配置
      .config("spark.extraListeners", "org.apache.atlas.spark.SparkAtlasEventTracker")
      .config("spark.sql.queryExecutionListeners", "org.apache.atlas.spark.SparkAtlasEventTracker")
      .config("atlas.rest.address", "http://atlas-server:21000")
      .config("atlas.kafka.bootstrap.servers", "kafka-server:9092")
      .getOrCreate()

    import spark.implicits._

    println("=== Spark Iceberg Atlas 集成配置 ===")
    
    // 2. 创建数据库
    spark.sql("CREATE DATABASE IF NOT EXISTS atlas_demo")
    spark.sql("USE atlas_demo")
    
    // 3. 创建用于数据治理演示的 Iceberg 表
    println("创建用于数据治理演示的 Iceberg 表...")
    spark.sql("""
      CREATE TABLE IF NOT EXISTS customer_data (
        customer_id BIGINT,
        name STRING,
        email STRING,
        phone STRING,
        address STRING,
        registration_date DATE,
        last_purchase_date DATE,
        total_spent DECIMAL(10,2)
      )
      USING iceberg
      PARTITIONED BY (months(registration_date))
      TBLPROPERTIES (
        'write.format.default'='parquet',
        'write.target-file-size-bytes'='268435456',
        'comment' = '客户数据表，包含基本信息和购买历史'
      )
    """)
    
    spark.sql("""
      CREATE TABLE IF NOT EXISTS product_catalog (
        product_id BIGINT,
        product_name STRING,
        category STRING,
        price DECIMAL(10,2),
        description STRING,
        created_date DATE
      )
      USING iceberg
      TBLPROPERTIES (
        'write.format.default'='parquet',
        'write.target-file-size-bytes'='134217728',
        'comment' = '产品目录表，包含产品信息'
      )
    """)
    
    spark.sql("""
      CREATE TABLE IF NOT EXISTS sales_transactions (
        transaction_id BIGINT,
        customer_id BIGINT,
        product_id BIGINT,
        quantity INT,
        unit_price DECIMAL(10,2),
        transaction_date TIMESTAMP,
        payment_method STRING
      )
      USING iceberg
      PARTITIONED BY (days(transaction_date))
      TBLPROPERTIES (
        'write.format.default'='parquet',
        'write.target-file-size-bytes'='536870912',
        'comment' = '销售交易表，记录每笔交易详情'
      )
    """)
    
    // 4. 插入测试数据
    println("插入客户数据...")
    val customerData = (1 to 10000).map { i =>
      (
        i.toLong,
        s"Customer $i",
        s"customer$i@example.com",
        s"+1-555-000-$i",
        s"Address $i, City, Country",
        java.sql.Date.valueOf(s"2020-${(i % 12) + 1}-${(i % 28) + 1}"),
        if (i % 5 == 0) java.sql.Date.valueOf(s"2023-${(i % 12) + 1}-${(i % 28) + 1}") else null,
        (Math.random() * 10000).setScale(2, BigDecimal.RoundingMode.HALF_UP)
      )
    }.toDF("customer_id", "name", "email", "phone", "address", "registration_date", "last_purchase_date", "total_spent")
    
    customerData.writeTo("customer_data").append()
    
    println("插入产品数据...")
    val categories = Array("Electronics", "Clothing", "Books", "Home & Garden", "Sports")
    val productData = (1 to 5000).map { i =>
      (
        i.toLong,
        s"Product $i",
        categories((i - 1) % categories.length),
        (Math.random() * 500).setScale(2, BigDecimal.RoundingMode.HALF_UP),
        s"Description for Product $i",
        java.sql.Date.valueOf(s"2022-${(i % 12) + 1}-${(i % 28) + 1}")
      )
    }.toDF("product_id", "product_name", "category", "price", "description", "created_date")
    
    productData.writeTo("product_catalog").append()
    
    println("插入销售交易数据...")
    val paymentMethods = Array("Credit Card", "Debit Card", "PayPal", "Bank Transfer")
    val transactionData = (1 to 50000).map { i =>
      (
        i.toLong,
        ((i - 1) % 10000) + 1, // customer_id
        ((i - 1) % 5000) + 1,  // product_id
        (Math.random() * 10).toInt + 1, // quantity
        (Math.random() * 500).setScale(2, BigDecimal.RoundingMode.HALF_UP), // unit_price
        java.sql.Timestamp.valueOf(s"2023-${((i - 1) % 12) + 1}-${((i - 1) % 28) + 1} ${(i % 24)}:${(i % 60)}:${(i % 60)}"),
        paymentMethods((i - 1) % paymentMethods.length)
      )
    }.toDF("transaction_id", "customer_id", "product_id", "quantity", "unit_price", "transaction_date", "payment_method")
    
    transactionData.writeTo("sales_transactions").append()
    
    // 5. 执行一些复杂的查询以生成数据血缘
    println("执行数据分析查询...")
    
    // 查询每个客户的总消费
    val customerSpending = spark.sql("""
      SELECT 
        c.customer_id,
        c.name,
        c.email,
        SUM(t.quantity * t.unit_price) as total_spent
      FROM customer_data c
      JOIN sales_transactions t ON c.customer_id = t.customer_id
      GROUP BY c.customer_id, c.name, c.email
      ORDER BY total_spent DESC
      LIMIT 100
    """)
    
    // 将结果保存到新表
    customerSpending.writeTo("customer_spending_summary").create()
    
    // 查询每个产品类别的销售统计
    val categorySales = spark.sql("""
      SELECT 
        p.category,
        COUNT(t.transaction_id) as transaction_count,
        SUM(t.quantity * t.unit_price) as total_revenue,
        AVG(t.unit_price) as avg_price
      FROM product_catalog p
      JOIN sales_transactions t ON p.product_id = t.product_id
      GROUP BY p.category
      ORDER BY total_revenue DESC
    """)
    
    // 将结果保存到新表
    categorySales.writeTo("category_sales_summary").create()
    
    // 6. 查看表的血缘关系
    println("查看表的血缘关系...")
    spark.sql("SELECT * FROM customer_spending_summary.history").show(false)
    spark.sql("SELECT * FROM category_sales_summary.history").show(false)
    
    // 7. 与 Atlas API 交互，获取实体信息
    println("与 Atlas 交互获取数据治理信息...")
    try {
      // 注意：这只是一个示例，在实际环境中需要正确的认证配置
      /*
      val atlasClient = new AtlasClientV2(Array("http://atlas-server:21000"), Array("username", "password"))
      
      // 查询表实体
      val tableEntities = atlasClient.searchEntities("hive_table", "customer_data")
      println(s"找到 ${tableEntities.size()} 个相关实体")
      
      // 显示实体属性
      tableEntities.foreach { entity =>
        println(s"实体名称: ${entity.getAttribute("name")}")
        println(s"实体类型: ${entity.getTypeName}")
        println(s"描述: ${entity.getAttribute("description")}")
      }
      */
      
      println("注意：在实际环境中，需要正确配置 Atlas 连接信息和认证")
    } catch {
      case e: Exception =>
        println(s"Atlas 连接异常: ${e.getMessage}")
        println("请确保 Atlas 服务正在运行并且配置正确")
    }
    
    // 8. 数据质量检查
    println("执行数据质量检查...")
    
    // 检查空值
    spark.sql("""
      SELECT 
        COUNT(*) as total_records,
        COUNT(customer_id) as non_null_customer_ids,
        COUNT(name) as non_null_names,
        COUNT(email) as non_null_emails
      FROM customer_data
    """).show()
    
    // 检查重复记录
    spark.sql("""
      SELECT 
        customer_id,
        COUNT(*) as duplicate_count
      FROM customer_data
      GROUP BY customer_id
      HAVING COUNT(*) > 1
    """).show()
    
    // 9. 数据分类和标签
    println("为表添加数据分类标签...")
    spark.sql("ALTER TABLE customer_data SET TBLPROPERTIES ('classification' = 'PII')")
    spark.sql("ALTER TABLE customer_data SET TBLPROPERTIES ('sensitivity' = 'high')")
    spark.sql("ALTER TABLE sales_transactions SET TBLPROPERTIES ('classification' = 'financial')")
    spark.sql("ALTER TABLE sales_transactions SET TBLPROPERTIES ('sensitivity' = 'medium')")
    
    // 10. 查看表属性
    println("查看带标签的表属性:")
    spark.sql("SHOW TBLPROPERTIES customer_data").show(false)
    spark.sql("SHOW TBLPROPERTIES sales_transactions").show(false)
    
    // 11. 数据治理最佳实践演示
    println("数据治理最佳实践:")
    println("1. 为敏感数据表添加分类标签")
    println("2. 定期执行数据质量检查")
    println("3. 维护数据字典和业务术语表")
    println("4. 实施数据访问控制策略")
    println("5. 监控数据血缘和影响分析")
    
    // 12. 清理资源
    println("清理测试表...")
    spark.sql("DROP TABLE IF EXISTS customer_data")
    spark.sql("DROP TABLE IF EXISTS product_catalog")
    spark.sql("DROP TABLE IF EXISTS sales_transactions")
    spark.sql("DROP TABLE IF EXISTS customer_spending_summary")
    spark.sql("DROP TABLE IF EXISTS category_sales_summary")
    spark.sql("DROP DATABASE IF EXISTS atlas_demo CASCADE")
    
    spark.stop()
    println("Spark Iceberg Atlas 集成示例完成!")
  }
}