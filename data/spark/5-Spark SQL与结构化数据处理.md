# 5. Spark SQL与结构化数据处理

## 5.1 Spark SQL概述

Spark SQL是Spark处理结构化数据的模块，提供了DataFrame和Dataset API，以及支持SQL查询。它将SQL查询与Spark编程相结合，使得数据分析更加便捷高效。

### 5.1.1 DataFrame与RDD对比

| 特性 | RDD | DataFrame |
|------|-----|-----------|
| 数据表示 | Java/Python对象 | 具有命名列的分布式数据集 |
| 类型安全 | 编译时不检查 | 运行时检查 |
| 优化 | 用户手动优化 | Catalyst优化器自动优化 |
| 性能 | 较低 | 较高（得益于Tungsten） |
| API风格 | 函数式 | 声明式 |

**代码示例：RDD与DataFrame性能对比**

```python
# code/sql-examples/rdd_vs_dataframe.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
import time

def rdd_vs_dataframe_performance():
    # 初始化Spark
    sc = SparkContext("local[*]", "RDDvsDataFrame")
    spark = SparkSession(sc)
    
    # 创建测试数据
    data = [(i, f"user_{i}", i % 100) for i in range(1, 100001)]  # 10万条记录
    
    # RDD处理
    rdd = sc.parallelize(data)
    
    start_time = time.time()
    rdd_filtered = rdd.filter(lambda x: x[2] > 50)  # 过滤第三个元素大于50的记录
    rdd_mapped = rdd_filtered.map(lambda x: (x[0], x[1], x[2] * 2))  # 第三个元素乘以2
    rdd_grouped = rdd_mapped.map(lambda x: (x[2], 1)).reduceByKey(lambda a, b: a + b)  # 按第三个元素分组计数
    rdd_result = rdd_grouped.collect()
    rdd_time = time.time() - start_time
    
    print(f"RDD处理时间: {rdd_time:.2f}秒")
    print(f"RDD结果（前5个）: {rdd_result[:5]}")
    
    # DataFrame处理
    df = spark.createDataFrame(data, ["id", "name", "group_id"])
    
    start_time = time.time()
    df_filtered = df.filter(df.group_id > 50)
    df_mapped = df_filtered.withColumn("group_id", df.group_id * 2)
    df_grouped = df_mapped.groupBy("group_id").count()
    df_result = df_grouped.collect()
    df_time = time.time() - start_time
    
    print(f"DataFrame处理时间: {df_time:.2f}秒")
    print(f"DataFrame结果（前5个）: {df_result[:5]}")
    
    print(f"性能提升: {rdd_time / df_time:.2f}倍")
    
    sc.stop()

if __name__ == "__main__":
    rdd_vs_dataframe_performance()
```

## 5.2 DataFrame基础操作

### 5.2.1 创建DataFrame

```python
# code/sql-examples/create_dataframe.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

def create_dataframe_examples():
    spark = SparkSession.builder.appName("CreateDataFrame").getOrCreate()
    
    # 方法1: 从列表创建DataFrame
    print("=== 方法1: 从列表创建 ===")
    data = [("Alice", 34), ("Bob", 45), ("Charlie", 29)]
    columns = ["name", "age"]
    df_from_list = spark.createDataFrame(data, columns)
    df_from_list.show()
    
    # 方法2: 从RDD创建DataFrame
    print("\n=== 方法2: 从RDD创建 ===")
    rdd = spark.sparkContext.parallelize([("David", 38), ("Eve", 27), ("Frank", 42)])
    df_from_rdd = spark.createDataFrame(rdd, ["name", "age"])
    df_from_rdd.show()
    
    # 方法3: 使用Schema定义创建DataFrame
    print("\n=== 方法3: 使用Schema定义 ===")
    schema = StructType([
        StructField("name", StringType, nullable=False),
        StructField("age", IntegerType, nullable=True)
    ])
    
    people_data = [("Grace", 31), ("Henry", 36)]
    df_with_schema = spark.createDataFrame(people_data, schema)
    df_with_schema.show()
    
    # 方法4: 从外部数据源创建DataFrame
    print("\n=== 方法4: 从外部数据源创建 ===")
    
    # 创建临时CSV文件
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/people.csv", "w") as f:
        f.write("name,age,city\n")
        f.write("Alice,30,New York\n")
        f.write("Bob,25,Los Angeles\n")
        f.write("Charlie,35,Chicago\n")
    
    df_from_csv = spark.read.option("header", "true").csv("data/people.csv")
    df_from_csv.show()
    
    # 方法5: 使用pandas DataFrame创建（需要安装pandas）
    try:
        print("\n=== 方法5: 从pandas DataFrame创建 ===")
        import pandas as pd
        pandas_df = pd.DataFrame({
            "name": ["Iris", "Jack"],
            "age": [28, 33]
        })
        df_from_pandas = spark.createDataFrame(pandas_df)
        df_from_pandas.show()
    except ImportError:
        print("Pandas未安装，跳过pandas DataFrame示例")
    
    spark.stop()

if __name__ == "__main__":
    create_dataframe_examples()
```

### 5.2.2 DataFrame基本操作

```python
# code/sql-examples/dataframe_operations.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, concat, when

def dataframe_basic_operations():
    spark = SparkSession.builder.appName("DataFrameOperations").getOrCreate()
    
    # 创建示例DataFrame
    data = [
        ("Alice", 34, "Engineer", 85000),
        ("Bob", 25, "Designer", 65000),
        ("Charlie", 35, "Manager", 95000),
        ("David", 28, "Developer", 75000),
        ("Eve", 31, "Analyst", 70000),
        ("Frank", 42, "Director", 120000)
    ]
    columns = ["name", "age", "job", "salary"]
    
    df = spark.createDataFrame(data, columns)
    print("原始DataFrame:")
    df.show()
    
    # 查看DataFrame结构
    print("Schema:")
    df.printSchema()
    
    # 选择列
    print("\n选择特定列:")
    df.select("name", "job").show()
    
    # 使用col()选择列
    df.select(col("name"), col("salary")).show()
    
    # 添加新列
    print("\n添加新列:")
    df_with_bonus = df.withColumn("bonus", col("salary") * 0.1)
    df_with_bonus.show()
    
    # 添加常量列
    df_with_dept = df.withColumn("department", lit("IT"))
    df_with_dept.show()
    
    # 修改列
    print("\n修改列:")
    df_modified = df.withColumn("salary", col("salary") * 1.05)  # 涨薪5%
    df_modified.show()
    
    # 重命名列
    df_renamed = df.withColumnRenamed("job", "position")
    df_renamed.show()
    
    # 条件列
    print("\n条件列:")
    df_with_category = df.withColumn("category", 
                                    when(col("salary") >= 100000, "High")
                                    .when(col("salary") >= 75000, "Medium")
                                    .otherwise("Low"))
    df_with_category.show()
    
    # 拼接列
    print("\n拼接列:")
    df_with_fullname = df.withColumn("name_age", concat(col("name"), lit(" ("), col("age"), lit(")")))
    df_with_fullname.select("name_age", "job").show()
    
    spark.stop()

if __name__ == "__main__":
    dataframe_basic_operations()
```

### 5.2.3 DataFrame过滤与排序

```python
# code/sql-examples/dataframe_filter_sort.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc, asc

def dataframe_filter_sort():
    spark = SparkSession.builder.appName("DataFrameFilterSort").getOrCreate()
    
    # 创建示例DataFrame
    data = [
        ("Alice", 34, "Engineer", 85000, "New York"),
        ("Bob", 25, "Designer", 65000, "Los Angeles"),
        ("Charlie", 35, "Manager", 95000, "Chicago"),
        ("David", 28, "Developer", 75000, "New York"),
        ("Eve", 31, "Analyst", 70000, "Chicago"),
        ("Frank", 42, "Director", 120000, "New York"),
        ("Grace", 29, "Developer", 72000, "San Francisco"),
        ("Henry", 36, "Engineer", 88000, "Chicago"),
        ("Iris", 33, "Designer", 68000, "Los Angeles"),
        ("Jack", 39, "Manager", 98000, "San Francisco")
    ]
    columns = ["name", "age", "job", "salary", "city"]
    
    df = spark.createDataFrame(data, columns)
    print("原始DataFrame:")
    df.show()
    
    # 基础过滤
    print("\n=== 基础过滤 ===")
    # 年龄大于30
    df.filter(col("age") > 30).show()
    
    # 职位为Engineer
    df.filter(col("job") == "Engineer").show()
    
    # 复杂条件过滤
    print("\n=== 复杂条件过滤 ===")
    # 年龄大于30且薪资大于80000
    df.filter((col("age") > 30) & (col("salary") > 80000)).show()
    
    # 职位为Engineer或Developer
    df.filter(col("job").isin(["Engineer", "Developer"])).show()
    
    # 姓名以A或E开头
    df.filter(col("name").rlike("^(A|E)")).show()
    
    # 多条件组合
    df.filter((col("city") == "New York") | (col("city") == "Chicago")) \
      .filter(col("salary") > 70000).show()
    
    # 排序
    print("\n=== 排序 ===")
    # 按薪资升序排序
    df.orderBy(col("salary")).show()
    
    # 按年龄降序排序
    df.orderBy(desc("age")).show()
    
    # 多列排序
    df.orderBy(col("city").asc(), col("salary").desc()).show()
    
    # 排序的链式调用
    df.filter(col("age") > 30).orderBy(desc("salary")).show()
    
    spark.stop()

if __name__ == "__main__":
    dataframe_filter_sort()
```

## 5.3 DataFrame聚合操作

### 5.3.1 基础聚合函数

```python
# code/sql-examples/dataframe_aggregation.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, max, min, count, countDistinct

def dataframe_aggregation():
    spark = SparkSession.builder.appName("DataFrameAggregation").getOrCreate()
    
    # 创建示例DataFrame
    data = [
        ("Alice", "Engineer", 85000, "New York", 2020),
        ("Bob", "Designer", 65000, "Los Angeles", 2019),
        ("Charlie", "Manager", 95000, "Chicago", 2018),
        ("David", "Developer", 75000, "New York", 2021),
        ("Eve", "Analyst", 70000, "Chicago", 2020),
        ("Frank", "Director", 120000, "New York", 2019),
        ("Grace", "Developer", 72000, "San Francisco", 2021),
        ("Henry", "Engineer", 88000, "Chicago", 2020),
        ("Iris", "Designer", 68000, "Los Angeles", 2021),
        ("Jack", "Manager", 98000, "San Francisco", 2018),
        ("Alice", "Engineer", 85000, "New York", 2022),  # Alice重复记录
        ("Bob", "Designer", 70000, "Los Angeles", 2022)   # Bob薪资更新
    ]
    columns = ["name", "job", "salary", "city", "year"]
    
    df = spark.createDataFrame(data, columns)
    print("原始DataFrame:")
    df.show()
    
    # 基础聚合
    print("\n=== 基础聚合 ===")
    
    # 总薪资
    total_salary = df.select(sum(col("salary")).alias("total_salary"))
    total_salary.show()
    
    # 平均薪资
    avg_salary = df.select(avg(col("salary")).alias("avg_salary"))
    avg_salary.show()
    
    # 最高薪资
    max_salary = df.select(max(col("salary")).alias("max_salary"))
    max_salary.show()
    
    # 最低薪资
    min_salary = df.select(min(col("salary")).alias("min_salary"))
    min_salary.show()
    
    # 员工数量
    employee_count = df.select(count(col("name")).alias("employee_count"))
    employee_count.show()
    
    # 去重员工数量
    unique_employees = df.select(countDistinct(col("name")).alias("unique_employees"))
    unique_employees.show()
    
    # groupBy聚合
    print("\n=== groupBy聚合 ===")
    
    # 按职位分组统计
    job_stats = df.groupBy("job") \
                  .agg(
                      count("name").alias("count"),
                      avg("salary").alias("avg_salary"),
                      max("salary").alias("max_salary"),
                      min("salary").alias("min_salary")
                  ) \
                  .orderBy(desc("avg_salary"))
    
    job_stats.show()
    
    # 按城市分组统计
    city_stats = df.groupBy("city") \
                  .agg(
                      count("name").alias("employee_count"),
                      avg("salary").alias("avg_salary"),
                      sum("salary").alias("total_salary")
                  )
    
    city_stats.show()
    
    # 多列分组
    city_job_stats = df.groupBy("city", "job") \
                      .agg(
                          count("name").alias("count"),
                          avg("salary").alias("avg_salary")
                      )
    
    city_job_stats.show()
    
    # 多个聚合表达式
    print("\n=== 多个聚合表达式 ===")
    all_stats = df.groupBy("job") \
                 .agg(
                     count("*").alias("total_records"),
                     countDistinct("name").alias("unique_people"),
                     sum("salary").alias("total_salary"),
                     avg("salary").alias("avg_salary"),
                     max("salary").alias("max_salary"),
                     min("salary").alias("min_salary")
                 )
    
    all_stats.show()
    
    spark.stop()

if __name__ == "__main__":
    dataframe_aggregation()
```

### 5.3.2 高级聚合与窗口函数

```python
# code/sql-examples/advanced_aggregation.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, row_number, rank, dense_rank, lead, lag
from pyspark.sql.window import Window

def advanced_aggregation():
    spark = SparkSession.builder.appName("AdvancedAggregation").getOrCreate()
    
    # 创建销售数据示例
    data = [
        ("2021-01", "Alice", "Electronics", 1200, "Store A"),
        ("2021-01", "Bob", "Clothing", 800, "Store B"),
        ("2021-01", "Charlie", "Electronics", 1500, "Store A"),
        ("2021-02", "Alice", "Clothing", 600, "Store B"),
        ("2021-02", "David", "Electronics", 2000, "Store C"),
        ("2021-02", "Eve", "Clothing", 750, "Store A"),
        ("2021-03", "Alice", "Electronics", 1800, "Store C"),
        ("2021-03", "Bob", "Clothing", 900, "Store B"),
        ("2021-03", "Charlie", "Electronics", 1700, "Store A"),
        ("2021-03", "David", "Clothing", 850, "Store B")
    ]
    columns = ["month", "salesperson", "category", "sales_amount", "store"]
    
    df = spark.createDataFrame(data, columns)
    print("销售数据:")
    df.show()
    
    # 窗口函数示例
    print("\n=== 窗口函数示例 ===")
    
    # 按月份和销售人员的销售排名
    month_window = Window.partitionBy("month").orderBy(col("sales_amount").desc())
    
    ranked_sales = df.withColumn("rank_in_month", rank().over(month_window)) \
                     .withColumn("dense_rank_in_month", dense_rank().over(month_window)) \
                     .withColumn("row_number_in_month", row_number().over(month_window))
    
    ranked_sales.show()
    
    # 按类别计算销售总额
    category_window = Window.partitionBy("category")
    
    df_with_category_total = df.withColumn(
        "category_total", 
        sum("sales_amount").over(category_window)
    )
    
    df_with_category_total.show()
    
    # 计算与类别总额的比率
    df_with_ratio = df_with_category_total.withColumn(
        "sales_ratio", 
        col("sales_amount") / col("category_total")
    )
    
    df_with_ratio.show()
    
    # Lead和Lag函数
    print("\n=== Lead和Lag函数 ===")
    
    # 按销售人员排序，计算上个月和下个月的销售额
    salesperson_window = Window.partitionBy("salesperson").orderBy("month")
    
    df_with_lead_lag = df.withColumn(
        "prev_month_sales", 
        lag("sales_amount").over(salesperson_window)
    ).withColumn(
        "next_month_sales", 
        lead("sales_amount").over(salesperson_window)
    )
    
    df_with_lead_lag.orderBy("salesperson", "month").show()
    
    # 计算销售额环比变化
    df_with_change = df_with_lead_lag.withColumn(
        "month_over_month_change", 
        col("sales_amount") - col("prev_month_sales")
    ).withColumn(
        "month_over_month_pct", 
        (col("sales_amount") - col("prev_month_sales")) / col("prev_month_sales") * 100
    )
    
    df_with_change.orderBy("salesperson", "month").show()
    
    # 滚动聚合
    print("\n=== 滚动聚合 ===")
    
    # 按时间排序的滚动窗口
    time_window = Window.partitionBy("salesperson").orderBy("month") \
                       .rowsBetween(-2, 0)  # 当前行和前两行
    
    df_with_rolling = df.withColumn(
        "rolling_3_month_avg", 
        avg("sales_amount").over(time_window)
    ).withColumn(
        "rolling_3_month_sum", 
        sum("sales_amount").over(time_window)
    )
    
    df_with_rolling.orderBy("salesperson", "month").show()
    
    spark.stop()

if __name__ == "__main__":
    advanced_aggregation()
```

## 5.4 SQL查询

### 5.4.1 使用SQL查询DataFrame

```python
# code/sql-examples/sql_queries.py
from pyspark.sql import SparkSession

def sql_queries_example():
    spark = SparkSession.builder.appName("SQLQueries").getOrCreate()
    
    # 创建员工数据
    employees = [
        (1, "Alice", 34, "Engineer", 85000, 1),
        (2, "Bob", 25, "Designer", 65000, 2),
        (3, "Charlie", 35, "Manager", 95000, 1),
        (4, "David", 28, "Developer", 75000, 3),
        (5, "Eve", 31, "Analyst", 70000, 3),
        (6, "Frank", 42, "Director", 120000, 1),
        (7, "Grace", 29, "Developer", 72000, 2),
        (8, "Henry", 36, "Engineer", 88000, 2),
        (9, "Iris", 33, "Designer", 68000, 3),
        (10, "Jack", 39, "Manager", 98000, 2)
    ]
    employee_columns = ["id", "name", "age", "job", "salary", "department_id"]
    
    # 创建部门数据
    departments = [
        (1, "Engineering", "New York"),
        (2, "Design", "Los Angeles"),
        (3, "Marketing", "Chicago")
    ]
    department_columns = ["id", "name", "location"]
    
    emp_df = spark.createDataFrame(employees, employee_columns)
    dept_df = spark.createDataFrame(departments, department_columns)
    
    # 创建临时视图
    emp_df.createOrReplaceTempView("employees")
    dept_df.createOrReplaceTempView("departments")
    
    print("=== 基础SQL查询 ===")
    
    # 基础查询
    result1 = spark.sql("SELECT * FROM employees WHERE age > 30")
    result1.show()
    
    # 使用SQL表达式
    result2 = spark.sql("""
        SELECT name, job, salary 
        FROM employees 
        WHERE salary BETWEEN 70000 AND 90000 
        ORDER BY salary DESC
    """)
    result2.show()
    
    # 字符串函数
    result3 = spark.sql("""
        SELECT name, 
               UPPER(name) as uppercase_name,
               LENGTH(name) as name_length
        FROM employees
        WHERE name LIKE 'A%'
    """)
    result3.show()
    
    # 条件表达式
    result4 = spark.sql("""
        SELECT name, age, salary,
               CASE 
                   WHEN salary >= 100000 THEN 'High'
                   WHEN salary >= 75000 THEN 'Medium'
                   ELSE 'Low'
               END as salary_category
        FROM employees
    """)
    result4.show()
    
    print("\n=== 聚合查询 ===")
    
    # 基础聚合
    result5 = spark.sql("""
        SELECT job, 
               COUNT(*) as count,
               AVG(salary) as avg_salary,
               MAX(salary) as max_salary,
               MIN(salary) as min_salary
        FROM employees
        GROUP BY job
        ORDER BY avg_salary DESC
    """)
    result5.show()
    
    # HAVING子句
    result6 = spark.sql("""
        SELECT department_id, 
               AVG(salary) as avg_salary
        FROM employees
        GROUP BY department_id
        HAVING AVG(salary) > 80000
    """)
    result6.show()
    
    print("\n=== JOIN查询 ===")
    
    # 内连接
    result7 = spark.sql("""
        SELECT e.name, e.job, e.salary, d.name as department, d.location
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        WHERE d.location = 'New York'
    """)
    result7.show()
    
    # 左外连接
    result8 = spark.sql("""
        SELECT d.name as department, COUNT(e.id) as employee_count
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.name
    """)
    result8.show()
    
    # 子查询
    result9 = spark.sql("""
        SELECT name, job, salary
        FROM employees
        WHERE salary > (
            SELECT AVG(salary) 
            FROM employees
        )
        ORDER BY salary DESC
    """)
    result9.show()
    
    print("\n=== 窗口函数查询 ===")
    
    result10 = spark.sql("""
        SELECT name, job, department_id, salary,
               ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank_in_dept
        FROM employees
    """)
    result10.show()
    
    spark.stop()

if __name__ == "__main__":
    sql_queries_example()
```

### 5.4.2 复杂SQL查询示例

```python
# code/sql-examples/complex_sql.py
from pyspark.sql import SparkSession

def complex_sql_example():
    spark = SparkSession.builder.appName("ComplexSQL").getOrCreate()
    
    # 创建销售数据
    sales_data = [
        (1, 101, "2021-01-15", 1500.0, "Electronics"),
        (2, 102, "2021-01-20", 800.0, "Clothing"),
        (3, 101, "2021-02-10", 2000.0, "Electronics"),
        (4, 103, "2021-02-15", 1200.0, "Home"),
        (5, 102, "2021-03-05", 900.0, "Clothing"),
        (6, 104, "2021-03-12", 2500.0, "Electronics"),
        (7, 101, "2021-03-20", 1800.0, "Electronics"),
        (8, 103, "2021-04-05", 700.0, "Clothing"),
        (9, 104, "2021-04-15", 2200.0, "Electronics"),
        (10, 105, "2021-04-20", 1300.0, "Home")
    ]
    sales_columns = ["sale_id", "customer_id", "sale_date", "amount", "category"]
    
    # 创建客户数据
    customer_data = [
        (101, "Alice", "New York", "Premium"),
        (102, "Bob", "Los Angeles", "Standard"),
        (103, "Charlie", "Chicago", "Standard"),
        (104, "David", "New York", "Premium"),
        (105, "Eve", "Los Angeles", "Standard")
    ]
    customer_columns = ["customer_id", "name", "city", "customer_type"]
    
    sales_df = spark.createDataFrame(sales_data, sales_columns)
    customer_df = spark.createDataFrame(customer_data, customer_columns)
    
    # 创建视图
    sales_df.createOrReplaceTempView("sales")
    customer_df.createOrReplaceTempView("customers")
    
    # 复杂查询1: 各城市按客户类型的销售统计
    print("=== 按城市和客户类型的销售统计 ===")
    query1 = """
        SELECT c.city, c.customer_type,
               COUNT(DISTINCT s.customer_id) as customer_count,
               COUNT(s.sale_id) as transaction_count,
               SUM(s.amount) as total_sales,
               AVG(s.amount) as avg_sale_amount
        FROM customers c
        JOIN sales s ON c.customer_id = s.customer_id
        GROUP BY c.city, c.customer_type
        ORDER BY c.city, c.customer_type
    """
    result1 = spark.sql(query1)
    result1.show()
    
    # 复杂查询2: 月度销售趋势分析
    print("\n=== 月度销售趋势 ===")
    query2 = """
        SELECT 
            SUBSTRING(sale_date, 1, 7) as month,
            category,
            COUNT(sale_id) as transaction_count,
            SUM(amount) as total_sales,
            AVG(amount) as avg_transaction
        FROM sales
        GROUP BY SUBSTRING(sale_date, 1, 7), category
        ORDER BY month, total_sales DESC
    """
    result2 = spark.sql(query2)
    result2.show()
    
    # 复杂查询3: 客户购买行为分析
    print("\n=== 客户购买行为分析 ===")
    query3 = """
        WITH customer_stats AS (
            SELECT c.customer_id, c.name, c.customer_type,
                   COUNT(s.sale_id) as transaction_count,
                   SUM(s.amount) as total_spent,
                   AVG(s.amount) as avg_transaction,
                   MIN(s.sale_date) as first_purchase,
                   MAX(s.sale_date) as last_purchase,
                   COUNT(DISTINCT s.category) as unique_categories
            FROM customers c
            JOIN sales s ON c.customer_id = s.customer_id
            GROUP BY c.customer_id, c.name, c.customer_type
        ),
        customer_ranking AS (
            SELECT *, 
                   ROW_NUMBER() OVER (ORDER BY total_spent DESC) as spend_rank,
                   ROW_NUMBER() OVER (ORDER BY transaction_count DESC) as frequency_rank
            FROM customer_stats
        )
        SELECT customer_id, name, customer_type, transaction_count, total_spent, 
               avg_transaction, unique_categories, spend_rank, frequency_rank
        FROM customer_ranking
        ORDER BY total_spent DESC
    """
    result3 = spark.sql(query3)
    result3.show()
    
    # 复杂查询4: 销售预测的基础数据分析
    print("\n=== 销售预测数据分析 ===")
    query4 = """
        WITH monthly_sales AS (
            SELECT 
                SUBSTRING(sale_date, 1, 7) as month,
                category,
                SUM(amount) as monthly_sales
            FROM sales
            GROUP BY SUBSTRING(sale_date, 1, 7), category
        ),
        monthly_growth AS (
            SELECT 
                month,
                category,
                monthly_sales,
                LAG(monthly_sales) OVER (PARTITION BY category ORDER BY month) as prev_month_sales,
                (monthly_sales - LAG(monthly_sales) OVER (PARTITION BY category ORDER BY month)) / 
                    LAG(monthly_sales) OVER (PARTITION BY category ORDER BY month) * 100 as growth_rate
            FROM monthly_sales
        )
        SELECT * 
        FROM monthly_growth
        WHERE prev_month_sales IS NOT NULL
        ORDER BY category, month
    """
    result4 = spark.sql(query4)
    result4.show()
    
    spark.stop()

if __name__ == "__main__":
    complex_sql_example()
```

## 5.5 数据源与格式

### 5.5.1 读取和写入CSV

```python
# code/sql-examples/csv_operations.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
import os

def csv_operations():
    spark = SparkSession.builder.appName("CSVOperations").getOrCreate()
    
    # 创建示例目录
    os.makedirs("data/csv", exist_ok=True)
    
    # 创建示例CSV数据
    with open("data/csv/employees.csv", "w") as f:
        f.write("id,name,age,salary,department,hire_date\n")
        f.write("1,Alice,34,85000,Engineering,2020-01-15\n")
        f.write("2,Bob,25,65000,Design,2021-03-20\n")
        f.write("3,Charlie,35,95000,Engineering,2019-06-10\n")
        f.write("4,David,28,75000,Marketing,2021-01-05\n")
        f.write("5,Eve,31,70000,Design,2020-08-12\n")
    
    # 定义Schema
    schema = StructType([
        StructField("id", IntegerType(), nullable=False),
        StructField("name", StringType(), nullable=True),
        StructField("age", IntegerType(), nullable=True),
        StructField("salary", IntegerType(), nullable=True),
        StructField("department", StringType(), nullable=True),
        StructField("hire_date", DateType(), nullable=True)
    ])
    
    # 读取CSV文件
    print("=== 读取CSV ===")
    
    # 基础读取
    df1 = spark.read.csv("data/csv/employees.csv", header=True)
    print("基础读取（默认类型）:")
    df1.printSchema()
    df1.show()
    
    # 带Schema读取
    df2 = spark.read.csv("data/csv/employees.csv", header=True, schema=schema)
    print("\n带Schema读取:")
    df2.printSchema()
    df2.show()
    
    # 更多选项
    df3 = spark.read.format("csv") \
                 .option("header", "true") \
                 .option("inferSchema", "true") \
                 .option("dateFormat", "yyyy-MM-dd") \
                 .load("data/csv/employees.csv")
    
    print("\n带多种选项读取:")
    df3.printSchema()
    df3.show()
    
    # 写入CSV
    print("\n=== 写入CSV ===")
    
    # 创建一个示例DataFrame
    sales_data = [
        (101, "Electronics", 1500.0, "2022-01-15"),
        (102, "Clothing", 800.0, "2022-01-16"),
        (103, "Home", 1200.0, "2022-01-17")
    ]
    sales_columns = ["sale_id", "category", "amount", "sale_date"]
    
    sales_df = spark.createDataFrame(sales_data, sales_columns)
    
    # 写入CSV文件
    sales_df.write.format("csv") \
               .mode("overwrite") \
               .option("header", "true") \
               .save("data/csv/sales_output")
    
    print("CSV文件已写入到 data/csv/sales_output/")
    
    # 验证写入结果
    written_df = spark.read.csv("data/csv/sales_output", header=True, inferSchema=True)
    print("验证写入结果:")
    written_df.show()
    
    # 分区写入
    print("\n=== 分区写入 ===")
    
    # 按部门分区写入
    df2.write.partitionBy("department") \
            .mode("overwrite") \
            .option("header", "true") \
            .csv("data/csv/employees_by_dept")
    
    print("按部门分区写入完成")
    
    # 验证分区写入
    partitioned_df = spark.read.csv("data/csv/employees_by_dept", header=True, inferSchema=True)
    partitioned_df.show()
    
    spark.stop()

if __name__ == "__main__":
    csv_operations()
```

### 5.5.2 读取和写入Parquet

```python
# code/sql-examples/parquet_operations.py
from pyspark.sql import SparkSession
import os

def parquet_operations():
    spark = SparkSession.builder.appName("ParquetOperations").getOrCreate()
    
    # 创建示例DataFrame
    employees = [
        (1, "Alice", 34, "Engineer", 85000, "Engineering", "2020-01-15"),
        (2, "Bob", 25, "Designer", 65000, "Design", "2021-03-20"),
        (3, "Charlie", 35, "Manager", 95000, "Engineering", "2019-06-10"),
        (4, "David", 28, "Developer", 75000, "Engineering", "2021-01-05"),
        (5, "Eve", 31, "Analyst", 70000, "Marketing", "2020-08-12"),
        (6, "Frank", 42, "Director", 120000, "Management", "2018-02-10"),
        (7, "Grace", 29, "Developer", 72000, "Engineering", "2021-09-15"),
        (8, "Henry", 36, "Engineer", 88000, "Engineering", "2019-11-20"),
        (9, "Iris", 33, "Designer", 68000, "Design", "2020-07-30"),
        (10, "Jack", 39, "Manager", 98000, "Marketing", "2018-04-25")
    ]
    columns = ["id", "name", "age", "job", "salary", "department", "hire_date"]
    
    df = spark.createDataFrame(employees, columns)
    print("原始DataFrame:")
    df.show()
    
    # 创建目录
    os.makedirs("data/parquet", exist_ok=True)
    
    # 写入Parquet
    print("\n=== 写入Parquet ===")
    df.write.mode("overwrite").parquet("data/parquet/employees")
    print("Parquet文件已写入")
    
    # 读取Parquet
    print("\n=== 读取Parquet ===")
    parquet_df = spark.read.parquet("data/parquet/employees")
    print("从Parquet读取的数据:")
    parquet_df.show()
    parquet_df.printSchema()
    
    # 分区写入
    print("\n=== 分区写入 ===")
    df.write.partitionBy("department") \
            .mode("overwrite") \
            .parquet("data/parquet/employees_partitioned")
    print("按部门分区写入完成")
    
    # 读取分区数据
    print("\n=== 读取分区数据 ===")
    partitioned_df = spark.read.parquet("data/parquet/employees_partitioned")
    partitioned_df.show()
    
    # 谓词下推优化示例
    print("\n=== 谓词下推优化 ===")
    # 只读取特定部门的数据
    engineering_df = spark.read.parquet("data/parquet/employees_partitioned") \
                           .filter(col("department") == "Engineering")
    
    print("工程部门员工:")
    engineering_df.show()
    
    # 列裁剪优化示例
    print("\n=== 列裁剪优化 ===")
    # 只读取特定列
    name_salary_df = spark.read.parquet("data/parquet/employees") \
                            .select("name", "salary", "department")
    
    print("只包含姓名、薪资和部门的数据:")
    name_salary_df.show()
    
    # 查看Parquet文件的元数据
    print("\n=== Parquet元数据 ===")
    from pyspark.sql.functions import col
    
    # 创建一个简单的DataFrame并查看执行计划
    test_df = spark.read.parquet("data/parquet/employees")
    
    print("执行计划（查看优化）:")
    test_df.filter(col("department") == "Engineering").select("name", "salary").explain()
    
    spark.stop()

if __name__ == "__main__":
    parquet_operations()
```

### 5.5.3 读取和写入JSON

```python
# code/sql-examples/json_operations.py
from pyspark.sql import SparkSession
import os
import json

def json_operations():
    spark = SparkSession.builder.appName("JSONOperations").getOrCreate()
    
    # 创建示例JSON数据
    os.makedirs("data/json", exist_ok=True)
    
    # 创建多行JSON文件
    with open("data/json/employees.json", "w") as f:
        json_data = [
            {"id": 1, "name": "Alice", "age": 34, "skills": ["Java", "Python", "SQL"], "contact": {"email": "alice@example.com", "phone": "123-456-7890"}},
            {"id": 2, "name": "Bob", "age": 25, "skills": ["JavaScript", "React"], "contact": {"email": "bob@example.com", "phone": "234-567-8901"}},
            {"id": 3, "name": "Charlie", "age": 35, "skills": ["Python", "Machine Learning"], "contact": {"email": "charlie@example.com", "phone": "345-678-9012"}}
        ]
        
        for item in json_data:
            f.write(json.dumps(item) + "\n")
    
    # 创建单行JSON文件
    with open("data/json/employees_single_line.json", "w") as f:
        json.dump(json_data, f)
    
    # 读取JSON
    print("=== 读取JSON ===")
    
    # 读取多行JSON
    df1 = spark.read.json("data/json/employees.json")
    print("多行JSON数据:")
    df1.printSchema()
    df1.show(truncate=False)
    
    # 读取单行JSON
    df2 = spark.read.json("data/json/employees_single_line.json")
    print("\n单行JSON数据:")
    df2.printSchema()
    df2.show(truncate=False)
    
    # 处理嵌套结构
    print("\n=== 处理嵌套结构 ===")
    
    # 提取嵌套字段
    print("提取嵌套的联系人信息:")
    df1.select("name", "contact.email", "contact.phone").show(truncate=False)
    
    # 处理数组字段
    print("\n处理数组字段:")
    from pyspark.sql.functions import explode, size
    
    # 展开技能数组
    skills_df = df1.select("id", "name", explode("skills").alias("skill"))
    skills_df.show()
    
    # 计算技能数量
    df1_with_skill_count = df1.withColumn("skill_count", size("skills"))
    df1_with_skill_count.select("name", "skill_count").show()
    
    # 写入JSON
    print("\n=== 写入JSON ===")
    
    # 创建新的DataFrame
    departments = [
        (1, "Engineering", ["Alice", "Charlie", "Henry"]),
        (2, "Design", ["Bob", "Iris"]),
        (3, "Marketing", ["David", "Eve", "Jack"])
    ]
    
    dept_columns = ["dept_id", "dept_name", "employees"]
    dept_df = spark.createDataFrame(departments, dept_columns)
    
    # 写入JSON文件
    dept_df.write.mode("overwrite").json("data/json/departments")
    print("JSON文件已写入")
    
    # 验证写入结果
    result_df = spark.read.json("data/json/departments")
    print("验证写入结果:")
    result_df.printSchema()
    result_df.show(truncate=False)
    
    # 分区写入
    print("\n=== 分区写入 ===")
    dept_df.write.partitionBy("dept_name") \
                .mode("overwrite") \
                .json("data/json/departments_partitioned")
    print("按部门分区写入完成")
    
    # 复杂JSON处理
    print("\n=== 复杂JSON处理 ===")
    
    # 创建更复杂的JSON数据
    complex_json = [
        {"id": 1, "name": "Alice", "details": {"personal": {"age": 34, "city": "New York"}, "professional": {"department": "Engineering", "level": "Senior"}}},
        {"id": 2, "name": "Bob", "details": {"personal": {"age": 25, "city": "Los Angeles"}, "professional": {"department": "Design", "level": "Junior"}}},
        {"id": 3, "name": "Charlie", "details": {"personal": {"age": 35, "city": "Chicago"}, "professional": {"department": "Engineering", "level": "Lead"}}}
    ]
    
    with open("data/json/complex.json", "w") as f:
        for item in complex_json:
            f.write(json.dumps(item) + "\n")
    
    # 读取复杂JSON
    complex_df = spark.read.json("data/json/complex.json")
    print("复杂JSON结构:")
    complex_df.printSchema()
    complex_df.show(truncate=False)
    
    # 提取深层嵌套数据
    extracted_df = complex_df.select(
        "id",
        "name",
        "details.personal.age",
        "details.personal.city",
        "details.professional.department",
        "details.professional.level"
    )
    
    print("提取的深层嵌套数据:")
    extracted_df.show(truncate=False)
    
    spark.stop()

if __name__ == "__main__":
    json_operations()
```

### 5.5.4 连接外部数据源（JDBC）

```python
# code/sql-examples/jdbc_operations.py
from pyspark.sql import SparkSession

def jdbc_operations():
    spark = SparkSession.builder.appName("JDBCOperations").getOrCreate()
    
    # JDBC连接参数（以SQLite为例，实际生产环境可能是MySQL、PostgreSQL等）
    # 注意：需要先安装SQLite JDBC驱动并添加到Spark的jars目录
    jdbc_url = "jdbc:sqlite:data/sample.db"  # 示例URL，实际使用时替换为真实的数据库URL
    
    # 这是一个示例，实际使用时需要确保有正确的JDBC驱动
    try:
        # 读取数据库表
        print("=== 读取JDBC表 ===")
        
        # 方法1: 直接读取表
        # df = spark.read.jdbc(url=jdbc_url, table="employees", properties=properties)
        
        # 方法2: 使用SQL查询
        # df = spark.read.jdbc(url=jdbc_url, table="(SELECT * FROM employees WHERE age > 30) AS filtered", properties=properties)
        
        # 方法3: 分区读取（适用于大表）
        # df = spark.read.jdbc(
        #     url=jdbc_url, 
        #     table="employees", 
        #     columnName="id", 
        #     lowerBound=1, 
        #     upperBound=1000, 
        #     numPartitions=10, 
        #     properties=properties
        # )
        
        print("JDBC读取示例（需要有效的数据库连接和驱动）")
        
        # 写入数据库
        print("\n=== 写入JDBC表 ===")
        
        # 创建示例DataFrame
        data = [
            (1, "Alice", 34, "Engineer", 85000),
            (2, "Bob", 25, "Designer", 65000),
            (3, "Charlie", 35, "Manager", 95000)
        ]
        columns = ["id", "name", "age", "job", "salary"]
        
        df = spark.createDataFrame(data, columns)
        
        # 写入模式
        # write_mode = "overwrite"  # 覆盖表
        # write_mode = "append"     # 追加数据
        # write_mode = "ignore"     # 如果表存在则忽略
        # write_mode = "error"      # 如果表存在则报错（默认）
        
        # df.write.jdbc(url=jdbc_url, table="employees", mode=write_mode, properties=properties)
        
        print("JDBC写入示例（需要有效的数据库连接和驱动）")
        
    except Exception as e:
        print(f"JDBC操作失败: {e}")
        print("请确保:")
        print("1. 数据库服务器正在运行")
        print("2. JDBC驱动已正确安装")
        print("3. 连接参数正确")
    
    spark.stop()

if __name__ == "__main__":
    # 这是一个示例，实际使用时需要有效的数据库连接和JDBC驱动
    print("JDBC操作需要有效的数据库连接和驱动")
    print("请确保配置正确的数据库URL、表名、用户名和密码")
    jdbc_operations()
```

## 5.6 实战案例：ETL数据处理

```python
# code/sql-examples/etl_pipeline.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, upper, regexp_replace, split, trim, to_date, year, month, dayofmonth
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType, TimestampType
import os

def etl_pipeline_example():
    spark = SparkSession.builder.appName("ETLPipeline") \
                         .config("spark.sql.adaptive.enabled", "true") \
                         .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                         .getOrCreate()
    
    # 创建示例数据目录
    os.makedirs("data/etl/raw", exist_ok=True)
    os.makedirs("data/etl/cleaned", exist_ok=True)
    os.makedirs("data/etl/transformed", exist_ok=True)
    
    # ETL步骤1: 提取（Extract）- 模拟从原始源获取数据
    
    # 1.1 创建模拟原始销售数据
    print("=== ETL步骤1: 提取（Extract） ===")
    raw_sales_data = [
        (101, "  alice  ", "  new york ", 1500.50, "2021-01-15", "electronics"),
        (102, "bob", "los angeles", 850.75, "2021-01-16", "clothing"),
        (103, "charlie", "  chicago", 1200.0, "2021-01-17", "home & garden"),
        (104, "  david", "new york", 2500.0, "2021-01-18", "electronics"),
        (105, "eve", "san francisco", 1750.25, "2021-01-19", "electronics"),
        (106, "frank", "los angeles", 950.0, "2021-01-20", "clothing"),
        (107, "grace", "chicago", 1350.0, "2021-01-21", "home & garden"),
        (108, "henry", "new york", 3000.0, "2021-01-22", "electronics"),
        (109, "iris", "san francisco", 1100.0, "2021-01-23", "clothing"),
        (110, "jack", "chicago", 800.0, "2021-01-24", "home & garden")
    ]
    
    raw_sales_schema = StructType([
        StructField("customer_id", IntegerType(), nullable=False),
        StructField("customer_name", StringType(), nullable=True),
        StructField("city", StringType(), nullable=True),
        StructField("sale_amount", FloatType(), nullable=True),
        StructField("sale_date", StringType(), nullable=True),
        StructField("category", StringType(), nullable=True)
    ])
    
    raw_sales_df = spark.createDataFrame(raw_sales_data, raw_sales_schema)
    
    print("原始销售数据:")
    raw_sales_df.show(truncate=False)
    
    # 1.2 创建模拟原始客户数据
    raw_customer_data = [
        (101, "alice@example.com", "555-1234", "premium"),
        (102, "bob@example.com", "555-5678", "standard"),
        (103, "charlie@example.com", "555-9012", "premium"),
        (104, "david@example.com", "555-3456", "premium"),
        (105, "eve@example.com", "555-7890", "standard"),
        (106, "frank@example.com", "555-2345", "standard"),
        (107, "grace@example.com", "555-6789", "standard"),
        (108, "henry@example.com", "555-0123", "premium"),
        (109, "iris@example.com", "555-4567", "premium"),
        (110, "jack@example.com", "555-8901", "standard")
    ]
    
    raw_customer_schema = StructType([
        StructField("customer_id", IntegerType(), nullable=False),
        StructField("email", StringType(), nullable=True),
        StructField("phone", StringType(), nullable=True),
        StructField("tier", StringType(), nullable=True)
    ])
    
    raw_customer_df = spark.createDataFrame(raw_customer_data, raw_customer_schema)
    
    print("\n原始客户数据:")
    raw_customer_df.show(truncate=False)
    
    # ETL步骤2: 转换（Transform）- 清洗和处理数据
    
    print("\n=== ETL步骤2: 转换（Transform） ===")
    
    # 2.1 清洗销售数据
    cleaned_sales_df = raw_sales_df.withColumn("customer_name", trim(upper(col("customer_name")))) \
                                 .withColumn("city", trim(upper(col("city")))) \
                                 .withColumn("category", trim(lower(col("category")))) \
                                 .withColumn("category_clean", regexp_replace(col("category"), "[&\\s]+", "_")) \
                                 .withColumn("sale_date_clean", to_date(col("sale_date"), "yyyy-MM-dd")) \
                                 .withColumn("sale_year", year(col("sale_date_clean"))) \
                                 .withColumn("sale_month", month(col("sale_date_clean"))) \
                                 .withColumn("sale_day", dayofmonth(col("sale_date_clean")))
    
    print("清洗后的销售数据:")
    cleaned_sales_df.select(
        "customer_id", "customer_name", "city", "sale_amount", 
        "sale_date_clean", "category_clean", "sale_year", "sale_month"
    ).show(truncate=False)
    
    # 2.2 添加衍生字段
    enriched_sales_df = cleaned_sales_df.withColumn(
        "sale_category", 
        when(col("sale_amount") >= 2000, "high")
        .when(col("sale_amount") >= 1000, "medium")
        .otherwise("low")
    ).withColumn(
        "city_region", 
        when(col("city").isin("NEW YORK", "BOSTON", "PHILADELPHIA"), "EAST")
        .when(col("city").isin("LOS ANGELES", "SAN FRANCISCO", "SEATTLE"), "WEST")
        .otherwise("CENTRAL")
    )
    
    print("\n添加衍生字段后的销售数据:")
    enriched_sales_df.select(
        "customer_id", "sale_amount", "sale_category", "city", "city_region"
    ).show(truncate=False)
    
    # 2.3 处理客户数据
    cleaned_customer_df = raw_customer_df.withColumn("email", lower(trim(col("email")))) \
                                        .withColumn("tier", upper(col("tier")))
    
    print("\n清洗后的客户数据:")
    cleaned_customer_df.show(truncate=False)
    
    # ETL步骤3: 加载（Load）- 将处理后的数据保存到目标位置
    
    print("\n=== ETL步骤3: 加载（Load） ===")
    
    # 3.1 保存清洗后的数据
    enriched_sales_df.select(
        "customer_id", "customer_name", "city", "sale_amount", 
        "sale_date_clean", "category_clean", "sale_year", "sale_month", 
        "sale_category", "city_region"
    ).write.mode("overwrite").parquet("data/etl/cleaned/sales")
    
    cleaned_customer_df.write.mode("overwrite").parquet("data/etl/cleaned/customers")
    
    print("清洗后的数据已保存到parquet文件")
    
    # 3.2 创建聚合视图
    from pyspark.sql.functions import count, sum, avg
    
    sales_by_category = enriched_sales_df.groupBy("category_clean", "sale_year", "sale_month") \
                                       .agg(
                                           count("customer_id").alias("transaction_count"),
                                           sum("sale_amount").alias("total_sales"),
                                           avg("sale_amount").alias("avg_sale")
                                       )
    
    sales_by_category.write.mode("overwrite").parquet("data/etl/transformed/sales_by_category")
    
    sales_by_region = enriched_sales_df.groupBy("city_region", "sale_year") \
                                     .agg(
                                         count("customer_id").alias("transaction_count"),
                                         sum("sale_amount").alias("total_sales"),
                                         avg("sale_amount").alias("avg_sale")
                                     )
    
    sales_by_region.write.mode("overwrite").parquet("data/etl/transformed/sales_by_region")
    
    print("聚合数据已保存")
    
    # 验证ETL结果
    print("\n=== 验证ETL结果 ===")
    
    # 验证清洗后的数据
    verified_sales = spark.read.parquet("data/etl/cleaned/sales")
    print("验证清洗后的销售数据:")
    verified_sales.select("customer_id", "customer_name", "city", "sale_amount").show(5, truncate=False)
    
    # 验证聚合数据
    verified_aggregates = spark.read.parquet("data/etl/transformed/sales_by_category")
    print("\n验证聚合数据（按类别）:")
    verified_aggregates.show(5, truncate=False)
    
    # 创建最终报告
    final_report = spark.read.parquet("data/etl/cleaned/sales") \
                         .groupBy("sale_year", "city_region") \
                         .agg(
                             count("customer_id").alias("transaction_count"),
                             sum("sale_amount").alias("total_sales"),
                             avg("sale_amount").alias("avg_sale_amount")
                         ) \
                         .orderBy("sale_year", "city_region")
    
    print("\n=== 最终报告 ===")
    final_report.show(truncate=False)
    
    # 保存最终报告
    final_report.write.mode("overwrite").parquet("data/etl/final_report")
    final_report.write.mode("overwrite").option("header", "true").csv("data/etl/final_report_csv")
    
    print("\n最终报告已保存到parquet和CSV格式")
    
    spark.stop()

if __name__ == "__main__":
    # 确保lower函数可用
    from pyspark.sql.functions import lower
    etl_pipeline_example()
```

## 5.7 性能优化技巧

### 5.7.1 查询优化

```python
# code/sql-examples/query_optimization.py
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, broadcast
import time

def query_optimization_example():
    spark = SparkSession.builder.appName("QueryOptimization") \
                         .config("spark.sql.adaptive.enabled", "true") \
                         .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                         .getOrCreate()
    
    # 创建大数据集
    print("创建测试数据集...")
    
    # 创建大表：用户表（100万记录）
    large_user_data = [(i, f"user_{i}", f"city_{i % 100}", i % 1000) for i in range(1, 1_000_001)]
    large_user_df = spark.createDataFrame(large_user_data, ["user_id", "name", "city", "age"])
    
    # 创建小表：城市信息表（100条记录）
    small_city_data = [(i, f"city_{i}", f"region_{i % 10}") for i in range(100)]
    small_city_df = spark.createDataFrame(small_city_data, ["city_id", "city_name", "region"])
    
    # 创建临时视图
    large_user_df.createOrReplaceTempView("users")
    small_city_df.createOrReplaceTempView(" cities")
    
    # 优化技巧1: 使用广播连接（小表广播）
    print("\n=== 优化技巧1: 广播连接 ===")
    
    # 未优化的连接
    start_time = time.time()
    regular_join = large_user_df.join(small_city_df, 
                                     large_user_df.city == small_city_df.city_name)
    regular_join.count()
    regular_time = time.time() - start_time
    print(f"未优化连接时间: {regular_time:.2f}秒")
    
    # 使用广播连接优化
    start_time = time.time()
    broadcast_join = large_user_df.join(broadcast(small_city_df), 
                                       large_user_df.city == small_city_df.city_name)
    broadcast_join.count()
    broadcast_time = time.time() - start_time
    print(f"广播连接时间: {broadcast_time:.2f}秒")
    print(f"性能提升: {regular_time / broadcast_time:.2f}倍")
    
    # 优化技巧2: 列裁剪
    print("\n=== 优化技巧2: 列裁剪 ===")
    
    # 查询所有列
    start_time = time.time()
    all_columns = large_user_df.select("*").where(col("age") > 500).limit(1000)
    all_columns.collect()
    all_columns_time = time.time() - start_time
    print(f"查询所有列时间: {all_columns_time:.2f}秒")
    
    # 只查询需要的列
    start_time = time.time()
    selected_columns = large_user_df.select("user_id", "age").where(col("age") > 500).limit(1000)
    selected_columns.collect()
    selected_columns_time = time.time() - start_time
    print(f"查询选定列时间: {selected_columns_time:.2f}秒")
    print(f"性能提升: {all_columns_time / selected_columns_time:.2f}倍")
    
    # 优化技巧3: 谓词下推
    print("\n=== 优化技巧3: 谓词下推 ===")
    
    # 先连接再过滤
    start_time = time.time()
    join_then_filter = large_user_df.join(small_city_df, 
                                        large_user_df.city == small_city_df.city_name) \
                                   .filter(col("region") == "region_1")
    join_then_filter.count()
    join_then_filter_time = time.time() - start_time
    print(f"先连接再过滤时间: {join_then_filter_time:.2f}秒")
    
    # 先过滤再连接
    start_time = time.time()
    filtered_small_city = small_city_df.filter(col("region") == "region_1")
    filter_then_join = large_user_df.join(filtered_small_city, 
                                         large_user_df.city == filtered_small_city.city_name)
    filter_then_join.count()
    filter_then_join_time = time.time() - start_time
    print(f"先过滤再连接时间: {filter_then_join_time:.2f}秒")
    print(f"性能提升: {join_then_filter_time / filter_then_join_time:.2f}倍")
    
    # 优化技巧4: 分区裁剪
    print("\n=== 优化技巧4: 分区裁剪 ===")
    
    # 创建分区表
    large_user_df.write.partitionBy("age").mode("overwrite").parquet("data/partitioned_users")
    
    # 读取分区表
    partitioned_df = spark.read.parquet("data/partitioned_users")
    
    # 不使用分区裁剪
    start_time = time.time()
    full_scan = partitioned_df.filter(col("age") > 500)
    full_scan.count()
    full_scan_time = time.time() - start_time
    print(f"全表扫描时间: {full_scan_time:.2f}秒")
    
    # 使用分区裁剪
    start_time = time.time()
    partition_pruned = spark.read.parquet("data/partitioned_users") \
                                .filter(col("age") > 500)
    partition_pruned.count()
    partition_pruned_time = time.time() - start_time
    print(f"分区裁剪时间: {partition_pruned_time:.2f}秒")
    print(f"性能提升: {full_scan_time / partition_pruned_time:.2f}倍")
    
    # 查看执行计划
    print("\n=== 执行计划对比 ===")
    
    # 查看未优化查询的执行计划
    print("未优化查询的执行计划:")
    regular_join.explain()
    
    print("\n优化查询的执行计划:")
    broadcast_join.explain()
    
    spark.stop()

if __name__ == "__main__":
    query_optimization_example()
```

## 5.8 小结

本章详细介绍了Spark SQL和结构化数据处理，包括DataFrame基础操作、聚合函数、SQL查询、多种数据源读写以及性能优化技巧。Spark SQL通过引入DataFrame和Dataset API，以及Catalyst查询优化器，使得结构化数据处理更加高效便捷。在下一章中，我们将学习Spark Streaming，了解如何进行实时流数据处理。

## 实验与练习

1. 实现一个销售数据分析系统，使用DataFrame API计算各产品类别的销售趋势
2. 设计一个ETL流程，从多个数据源抽取数据，进行清洗和转换，然后加载到数据仓库
3. 使用Spark SQL实现复杂的数据分析查询，包括窗口函数和多表连接
4. 比较不同数据格式（CSV、JSON、Parquet）的性能差异
5. 优化一个慢查询，应用本章学到的性能优化技巧

## 参考资源

- [Spark SQL、DataFrame和Dataset编程指南](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Spark SQL性能调优指南](https://spark.apache.org/docs/latest/sql-performance-tuning.html)