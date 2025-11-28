/*
 * Spark Iceberg 集成基础示例
 * 
 * 本示例演示如何在 Spark 中配置 Iceberg 并进行基本的表操作。
 */

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object SparkIcebergBasicSetup {
  def main(args: Array[String]): Unit = {
    // 1. 创建 Spark Session 并配置 Iceberg
    val spark = SparkSession.builder()
      .appName("Spark Iceberg Basic Setup")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
      .config("spark.sql.catalog.spark_catalog.type", "hadoop")
      .config("spark.sql.catalog.spark_catalog.warehouse", "hdfs://localhost:9000/iceberg/warehouse")
      .getOrCreate()

    import spark.implicits._

    println("=== Spark Iceberg 集成基础配置 ===")
    
    // 2. 创建数据库
    spark.sql("CREATE DATABASE IF NOT EXISTS default")
    spark.sql("USE default")
    
    // 3. 创建 Iceberg 表
    println("创建 Iceberg 表...")
    spark.sql("""
      CREATE TABLE IF NOT EXISTS users (
        id BIGINT,
        name STRING,
        email STRING,
        age INT,
        created_at TIMESTAMP
      )
      USING iceberg
      PARTITIONED BY (days(created_at))
      TBLPROPERTIES (
        'write.format.default'='parquet',
        'write.target-file-size-bytes'='536870912'
      )
    """)
    
    // 4. 插入测试数据
    println("插入测试数据...")
    val userData = Seq(
      (1L, "张三", "zhangsan@example.com", 25, java.sql.Timestamp.valueOf("2023-01-15 10:30:00")),
      (2L, "李四", "lisi@example.com", 30, java.sql.Timestamp.valueOf("2023-01-16 14:45:00")),
      (3L, "王五", "wangwu@example.com", 28, java.sql.Timestamp.valueOf("2023-01-17 09:15:00")),
      (4L, "赵六", "zhaoliu@example.com", 35, java.sql.Timestamp.valueOf("2023-01-18 16:20:00"))
    ).toDF("id", "name", "email", "age", "created_at")
    
    userData.writeTo("users").append()
    
    // 5. 查询数据
    println("查询所有用户数据:")
    spark.table("users").show(false)
    
    // 6. 条件查询
    println("查询年龄大于25的用户:")
    spark.sql("SELECT * FROM users WHERE age > 25").show(false)
    
    // 7. 聚合查询
    println("用户年龄统计:")
    spark.sql("""
      SELECT 
        COUNT(*) as total_users,
        AVG(age) as avg_age,
        MIN(age) as min_age,
        MAX(age) as max_age
      FROM users
    """).show()
    
    // 8. 查看表的元数据信息
    println("查看表的历史快照:")
    spark.sql("SELECT * FROM users.history").show(false)
    
    println("查看表的分区信息:")
    spark.sql("SELECT * FROM users.partitions").show(false)
    
    // 9. 更新数据
    println("更新用户数据...")
    spark.sql("""
      UPDATE users 
      SET email = 'zhangsan_new@example.com' 
      WHERE id = 1
    """)
    
    println("更新后的用户数据:")
    spark.sql("SELECT * FROM users WHERE id = 1").show(false)
    
    // 10. 删除数据
    println("删除用户数据...")
    spark.sql("DELETE FROM users WHERE id = 4")
    
    println("删除后的用户数据:")
    spark.table("users").show(false)
    
    // 11. 查看表的当前快照
    println("当前表快照信息:")
    spark.sql("SELECT * FROM users.snapshots").show(false)
    
    // 12. 时间旅行查询
    println("时间旅行查询 - 查看表的早期状态:")
    val earliestSnapshot = spark.sql("SELECT snapshot_id FROM users.history ORDER BY committed_at ASC LIMIT 1")
      .collect()(0).getAs[Long]("snapshot_id")
    
    spark.sql(s"SELECT * FROM users VERSION AS OF $earliestSnapshot").show(false)
    
    // 13. 创建分支
    println("创建分支...")
    spark.sql("ALTER TABLE users CREATE BRANCH test_branch")
    
    // 14. 在分支上插入数据
    println("在分支上插入数据...")
    val branchData = Seq(
      (5L, "孙七", "sunqi@example.com", 22, java.sql.Timestamp.valueOf("2023-01-19 11:30:00"))
    ).toDF("id", "name", "email", "age", "created_at")
    
    branchData.write.option("branch", "test_branch").mode("append").saveAsTable("users")
    
    println("主分支数据:")
    spark.table("users").show(false)
    
    println("test_branch 分支数据:")
    spark.read.option("branch", "test_branch").table("users").show(false)
    
    // 15. 合并分支
    println("合并分支...")
    spark.sql("CALL system.merge_branches(table => 'users', branch => 'test_branch')")
    
    println("合并后的数据:")
    spark.table("users").show(false)
    
    // 16. 查看表属性
    println("表属性信息:")
    spark.sql("SHOW TBLPROPERTIES users").show(false)
    
    // 17. 修改表属性
    println("修改表属性...")
    spark.sql("ALTER TABLE users SET TBLPROPERTIES ('comments' = '用户信息表')")
    
    println("修改后的表属性:")
    spark.sql("SHOW TBLPROPERTIES users").show(false)
    
    // 18. 清理资源
    println("清理测试表...")
    spark.sql("DROP TABLE IF EXISTS users")
    
    spark.stop()
    println("Spark Iceberg 基础配置示例完成!")
  }
}