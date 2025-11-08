#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark SQL销售数据分析示例
使用Spark SQL和DataFrame API分析销售数据，展示SQL操作、数据转换和聚合分析。

运行方式:
spark-submit sales_analysis.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, max, min, count, when, year, month
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType

def create_sales_dataframe(spark):
    """创建销售数据DataFrame"""
    
    # 定义销售数据模式
    sales_schema = StructType([
        StructField("order_id", IntegerType(), nullable=False),
        StructField("customer_id", IntegerType(), nullable=False),
        StructField("product_id", IntegerType(), nullable=False),
        StructField("product_name", StringType(), nullable=True),
        StructField("category", StringType(), nullable=True),
        StructField("quantity", IntegerType(), nullable=False),
        StructField("unit_price", FloatType(), nullable=False),
        StructField("order_date", DateType(), nullable=True),
        StructField("region", StringType(), nullable=True)
    ])
    
    # 创建示例销售数据
    sales_data = [
        (1001, 101, 501, "Laptop", "Electronics", 1, 1200.00, "2023-01-15", "North"),
        (1002, 102, 502, "Smartphone", "Electronics", 2, 800.00, "2023-01-16", "South"),
        (1003, 103, 503, "Desk Chair", "Furniture", 3, 150.00, "2023-01-17", "East"),
        (1004, 104, 501, "Laptop", "Electronics", 1, 1200.00, "2023-01-18", "West"),
        (1005, 105, 504, "Book", "Education", 5, 25.00, "2023-01-19", "North"),
        (1006, 106, 502, "Smartphone", "Electronics", 1, 800.00, "2023-01-20", "South"),
        (1007, 107, 503, "Desk Chair", "Furniture", 2, 150.00, "2023-02-10", "East"),
        (1008, 108, 505, "Headphones", "Electronics", 1, 120.00, "2023-02-11", "West"),
        (1009, 109, 504, "Book", "Education", 10, 25.00, "2023-02-12", "North"),
        (1010, 110, 506, "Tablet", "Electronics", 1, 600.00, "2023-02-13", "South"),
        (1011, 101, 501, "Laptop", "Electronics", 1, 1200.00, "2023-02-14", "East"),
        (1012, 111, 507, "Monitor", "Electronics", 2, 300.00, "2023-02-15", "West"),
        (1013, 112, 508, "Desk", "Furniture", 1, 400.00, "2023-03-10", "North"),
        (1014, 113, 505, "Headphones", "Electronics", 3, 120.00, "2023-03-11", "South"),
        (1015, 114, 509, "Keyboard", "Electronics", 2, 80.00, "2023-03-12", "East"),
        (1016, 115, 506, "Tablet", "Electronics", 1, 600.00, "2023-03-13", "West")
    ]
    
    # 创建DataFrame
    sales_df = spark.createDataFrame(sales_data, sales_schema)
    
    # 添加计算列
    sales_df = sales_df.withColumn("total_amount", col("quantity") * col("unit_price"))
    
    return sales_df

def basic_analysis(sales_df):
    """基础数据分析"""
    print("=== 基础数据分析 ===")
    
    # 显示前几行数据
    print("销售数据样本:")
    sales_df.show()
    
    # 数据统计
    print("数据统计信息:")
    sales_df.describe().show()
    
    # 订单总数
    total_orders = sales_df.count()
    print(f"订单总数: {total_orders}")
    
    # 总销售额
    total_sales = sales_df.agg({"total_amount": "sum"}).collect()[0][0]
    print(f"总销售额: ${total_sales:,.2f}")
    
    # 平均订单金额
    avg_order_amount = sales_df.agg({"total_amount": "avg"}).collect()[0][0]
    print(f"平均订单金额: ${avg_order_amount:,.2f}")

def category_analysis(sales_df):
    """按类别分析销售数据"""
    print("\n=== 按类别分析 ===")
    
    # 按类别分组统计
    category_stats = sales_df.groupBy("category") \
                        .agg(
                            count("order_id").alias("order_count"),
                            sum("total_amount").alias("total_sales"),
                            avg("total_amount").alias("avg_order_value")
                        ) \
                        .orderBy("total_sales", ascending=False)
    
    print("各类别销售统计:")
    category_stats.show()
    
    # 创建临时视图进行SQL查询
    sales_df.createOrReplaceTempView("sales")
    
    # 使用SQL查询获取各类别的销售占比
    category_percentage = spark.sql("""
        SELECT 
            category,
            total_sales,
            ROUND(total_sales * 100.0 / (SELECT SUM(total_amount) FROM sales), 2) AS sales_percentage
        FROM (
            SELECT category, SUM(total_amount) AS total_sales
            FROM sales
            GROUP BY category
        ) ORDER BY total_sales DESC
    """)
    
    print("各类别销售占比:")
    category_percentage.show()

def regional_analysis(sales_df):
    """按区域分析销售数据"""
    print("\n=== 按区域分析 ===")
    
    # 按区域分组统计
    region_stats = sales_df.groupBy("region") \
                     .agg(
                         count("order_id").alias("order_count"),
                         sum("total_amount").alias("total_sales"),
                         avg("total_amount").alias("avg_order_value"),
                         max("total_amount").alias("max_order_value")
                     ) \
                     .orderBy("total_sales", ascending=False)
    
    print("各区域销售统计:")
    region_stats.show()
    
    # 各区域的顶级产品
    top_products_by_region = spark.sql("""
        SELECT 
            region,
            product_name,
            total_quantity,
            total_amount
        FROM (
            SELECT 
                region,
                product_name,
                SUM(quantity) AS total_quantity,
                SUM(total_amount) AS total_amount,
                ROW_NUMBER() OVER (PARTITION BY region ORDER BY SUM(total_amount) DESC) AS rank
            FROM sales
            GROUP BY region, product_name
        ) WHERE rank <= 2
        ORDER BY region, total_amount DESC
    """)
    
    print("各区域顶级产品:")
    top_products_by_region.show()

def time_series_analysis(sales_df):
    """时间序列分析"""
    print("\n=== 时间序列分析 ===")
    
    # 添加年、月列
    sales_with_time = sales_df.withColumn("year", year("order_date")) \
                               .withColumn("month", month("order_date"))
    
    # 按月统计销售额
    monthly_sales = sales_with_time.groupBy("year", "month") \
                            .agg(
                                count("order_id").alias("order_count"),
                                sum("total_amount").alias("total_sales")
                            ) \
                            .orderBy("year", "month")
    
    print("按月销售统计:")
    monthly_sales.show()
    
    # 计算月度增长率
    monthly_sales.createOrReplaceTempView("monthly_sales")
    
    monthly_growth = spark.sql("""
        SELECT 
            year,
            month,
            total_sales,
            LAG(total_sales) OVER (ORDER BY year, month) AS prev_month_sales,
            ROUND(
                (total_sales - LAG(total_sales) OVER (ORDER BY year, month)) / 
                LAG(total_sales) OVER (ORDER BY year, month) * 100, 2
            ) AS growth_rate
        FROM monthly_sales
        ORDER BY year, month
    """)
    
    print("月度销售增长率:")
    monthly_growth.show()

def customer_analysis(sales_df):
    """客户分析"""
    print("\n=== 客户分析 ===")
    
    # 按客户统计
    customer_stats = sales_df.groupBy("customer_id") \
                          .agg(
                              count("order_id").alias("order_count"),
                              sum("total_amount").alias("total_spent"),
                              avg("total_amount").alias("avg_order_value"),
                              min("order_date").alias("first_order_date"),
                              max("order_date").alias("last_order_date")
                          )
    
    # 客户分群
    customer_segments = customer_stats.withColumn(
        "segment",
        when(col("total_spent") > 2000, "High Value")
        .when(col("total_spent") > 1000, "Medium Value")
        .otherwise("Low Value")
    )
    
    print("客户分群统计:")
    customer_segments.groupBy("segment") \
                   .agg(
                       count("customer_id").alias("customer_count"),
                       sum("total_spent").alias("total_revenue")
                   ) \
                   .orderBy("total_revenue", ascending=False) \
                   .show()
    
    # 高价值客户分析
    high_value_customers = customer_segments.filter(col("segment") == "High Value") \
                                         .orderBy("total_spent", ascending=False)
    
    print("高价值客户:")
    high_value_customers.select("customer_id", "order_count", "total_spent", "first_order_date", "last_order_date").show()

def main():
    """主函数"""
    # 创建SparkSession
    spark = SparkSession.builder.appName("SalesAnalysis").getOrCreate()
    
    # 创建销售数据DataFrame
    sales_df = create_sales_dataframe(spark)
    
    # 执行各类分析
    basic_analysis(sales_df)
    category_analysis(sales_df)
    regional_analysis(sales_df)
    time_series_analysis(sales_df)
    customer_analysis(sales_df)
    
    # 停止SparkSession
    spark.stop()
    print("销售数据分析完成")

if __name__ == "__main__":
    main()