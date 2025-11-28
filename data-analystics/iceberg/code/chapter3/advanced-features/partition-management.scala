import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
import org.apache.log4j.{Level, Logger}

object PartitionManagement {
  def main(args: Array[String]): Unit = {
    // 设置日志级别
    Logger.getLogger("org").setLevel(Level.WARN)
    Logger.getLogger("akka").setLevel(Level.WARN)

    // 创建 Spark Session 并启用 Iceberg 扩展
    val spark = SparkSession.builder()
      .appName("Iceberg Partition Management")
      .master("local[*]")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
      .config("spark.sql.catalog.spark_catalog.type", "hadoop")
      .config("spark.sql.catalog.spark_catalog.warehouse", "file:///tmp/iceberg/warehouse")
      .getOrCreate()

    import spark.implicits._

    println("=== Apache Iceberg 分区管理示例 ===")

    // 创建数据库
    spark.sql("CREATE DATABASE IF NOT EXISTS iceberg_db")
    spark.sql("USE iceberg_db")

    // 1. 创建多级分区表
    println("\n1. 创建多级分区表 sales_partitioned")
    spark.sql("""
      CREATE OR REPLACE TABLE sales_partitioned (
        id BIGINT,
        product STRING,
        category STRING,
        amount DECIMAL(10,2),
        quantity INT,
        sale_date DATE,
        region STRING
      ) USING iceberg
      PARTITIONED BY (region, category, years(sale_date))
      TBLPROPERTIES (
        'format-version'='2',
        'write.distribution-mode'='hash'
      )
    """)

    // 2. 插入测试数据
    println("\n2. 插入测试数据")
    spark.sql("""
      INSERT INTO sales_partitioned VALUES
      (1, 'Laptop', 'Electronics', 1200.00, 1, DATE '2024-01-15', 'North'),
      (2, 'Phone', 'Electronics', 800.00, 2, DATE '2024-01-16', 'South'),
      (3, 'Desk', 'Furniture', 300.00, 1, DATE '2024-02-15', 'North'),
      (4, 'Chair', 'Furniture', 150.00, 4, DATE '2024-02-16', 'South'),
      (5, 'Tablet', 'Electronics', 500.00, 1, DATE '2024-03-15', 'East'),
      (6, 'Monitor', 'Electronics', 400.00, 3, DATE '2024-03-16', 'West'),
      (7, 'Bookshelf', 'Furniture', 200.00, 2, DATE '2024-04-15', 'East'),
      (8, 'Lamp', 'Furniture', 50.00, 5, DATE '2024-04-16', 'West')
    """)

    // 3. 查看分区信息
    println("\n3. 查看分区信息")
    spark.sql("SELECT * FROM sales_partitioned.partitions").show(false)

    // 4. 查询特定分区数据
    println("\n4. 查询特定分区数据 - North 地区电子产品")
    spark.sql("""
      SELECT * FROM sales_partitioned 
      WHERE region = 'North' AND category = 'Electronics'
    """).show(false)

    // 5. 分区裁剪效果展示
    println("\n5. 分区裁剪效果展示")
    spark.sql("""
      EXPLAIN SELECT * FROM sales_partitioned 
      WHERE region = 'North' AND category = 'Electronics' AND sale_date >= '2024-01-01'
    """).show(false)

    // 6. 添加新的分区字段
    println("\n6. 添加新的分区字段 - brand")
    spark.sql("ALTER TABLE sales_partitioned ADD PARTITION FIELD brand")

    // 更新数据以包含品牌信息
    spark.sql("ALTER TABLE sales_partitioned ADD COLUMN brand STRING")
    
    spark.sql("""
      UPDATE sales_partitioned 
      SET brand = CASE 
        WHEN product LIKE '%Laptop%' OR product LIKE '%Phone%' OR product LIKE '%Tablet%' OR product LIKE '%Monitor%' THEN 'TechBrand'
        WHEN product LIKE '%Desk%' OR product LIKE '%Chair%' OR product LIKE '%Tablet%' OR product LIKE '%Bookshelf%' OR product LIKE '%Lamp%' THEN 'HomeBrand'
        ELSE 'Generic'
      END
    """)

    // 插入一些带品牌的新数据
    spark.sql("""
      INSERT INTO sales_partitioned VALUES
      (9, 'Smartphone', 'Electronics', 900.00, 1, DATE '2024-05-15', 'North', 'MobileBrand'),
      (10, 'Sofa', 'Furniture', 1000.00, 1, DATE '2024-05-16', 'South', 'ComfortBrand')
    """)

    println("添加分区字段后的分区信息:")
    spark.sql("SELECT * FROM sales_partitioned.partitions").show(false)

    // 7. 删除分区字段
    println("\n7. 删除分区字段 - years(sale_date)")
    spark.sql("ALTER TABLE sales_partitioned DROP PARTITION FIELD years(sale_date)")

    println("删除分区字段后的分区信息:")
    spark.sql("SELECT * FROM sales_partitioned.partitions").show(false)

    // 8. 创建 Identity 分区
    println("\n8. 创建 Identity 分区表")
    spark.sql("""
      CREATE OR REPLACE TABLE orders_identity (
        order_id BIGINT,
        customer_id STRING,
        product STRING,
        amount DECIMAL(10,2),
        order_date DATE
      ) USING iceberg
      PARTITIONED BY (customer_id, order_date)
      TBLPROPERTIES ('format-version'='2')
    """)

    // 插入数据
    spark.sql("""
      INSERT INTO orders_identity VALUES
      (1001, 'CUST001', 'Laptop', 1200.00, DATE '2024-01-15'),
      (1002, 'CUST002', 'Phone', 800.00, DATE '2024-01-16'),
      (1003, 'CUST001', 'Mouse', 25.00, DATE '2024-01-17'),
      (1004, 'CUST003', 'Keyboard', 75.00, DATE '2024-01-18')
    """)

    println("Identity 分区表数据:")
    spark.sql("SELECT * FROM orders_identity").show(false)

    // 9. 创建 Bucket 分区
    println("\n9. 创建 Bucket 分区表")
    spark.sql("""
      CREATE OR REPLACE TABLE user_bucketed (
        user_id BIGINT,
        username STRING,
        email STRING,
        department STRING
      ) USING iceberg
      PARTITIONED BY (bucket(16, department))
      TBLPROPERTIES ('format-version'='2')
    """)

    // 插入数据
    spark.sql("""
      INSERT INTO user_bucketed VALUES
      (1, 'Alice', 'alice@example.com', 'Engineering'),
      (2, 'Bob', 'bob@example.com', 'Marketing'),
      (3, 'Charlie', 'charlie@example.com', 'Engineering'),
      (4, 'David', 'david@example.com', 'Sales'),
      (5, 'Eve', 'eve@example.com', 'Marketing')
    """)

    println("Bucket 分区表分区信息:")
    spark.sql("SELECT * FROM user_bucketed.partitions").show(false)

    // 10. 创建 Truncate 分区
    println("\n10. 创建 Truncate 分区表")
    spark.sql("""
      CREATE OR REPLACE TABLE products_truncated (
        product_id BIGINT,
        product_name STRING,
        price DECIMAL(10,2),
        category_id INT
      ) USING iceberg
      PARTITIONED BY (truncate(10, category_id))
      TBLPROPERTIES ('format-version'='2')
    """)

    // 插入数据
    spark.sql("""
      INSERT INTO products_truncated VALUES
      (1, 'Laptop', 1200.00, 1001),
      (2, 'Phone', 800.00, 1002),
      (3, 'Mouse', 25.00, 1001),
      (4, 'Keyboard', 75.00, 1003),
      (5, 'Monitor', 400.00, 1015)
    """)

    println("Truncate 分区表分区信息:")
    spark.sql("SELECT * FROM products_truncated.partitions").show(false)

    // 11. 查看所有表的分区统计信息
    println("\n11. 查看所有表的分区统计信息")
    spark.sql("SELECT * FROM sales_partitioned.files").show(false)

    // 12. 分区优化 - 合并小文件
    println("\n12. 分区优化 - 合并小文件")
    spark.sql("CALL spark_catalog.system.rewrite_data_files(table => 'sales_partitioned')")

    println("分区管理示例完成!")
    spark.stop()
  }
}