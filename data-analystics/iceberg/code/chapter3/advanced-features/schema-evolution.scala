import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
import org.apache.log4j.{Level, Logger}

object SchemaEvolution {
  def main(args: Array[String]): Unit = {
    // 设置日志级别
    Logger.getLogger("org").setLevel(Level.WARN)
    Logger.getLogger("akka").setLevel(Level.WARN)

    // 创建 Spark Session 并启用 Iceberg 扩展
    val spark = SparkSession.builder()
      .appName("Iceberg Schema Evolution")
      .master("local[*]")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
      .config("spark.sql.catalog.spark_catalog.type", "hadoop")
      .config("spark.sql.catalog.spark_catalog.warehouse", "file:///tmp/iceberg/warehouse")
      .getOrCreate()

    import spark.implicits._

    println("=== Apache Iceberg Schema Evolution 示例 ===")

    // 创建数据库
    spark.sql("CREATE DATABASE IF NOT EXISTS iceberg_db")
    spark.sql("USE iceberg_db")

    // 1. 创建初始表 - 只有基本字段
    println("\n1. 创建初始表 users_basic")
    spark.sql("""
      CREATE OR REPLACE TABLE users_basic (
        id BIGINT COMMENT '用户ID',
        name STRING COMMENT '用户名',
        age INT COMMENT '年龄'
      ) USING iceberg
      TBLPROPERTIES (
        'format-version'='2',
        'write.distribution-mode'='hash'
      )
    """)

    // 插入初始数据
    spark.sql("""
      INSERT INTO users_basic VALUES
      (1, 'Alice', 25),
      (2, 'Bob', 30),
      (3, 'Charlie', 35)
    """)

    println("初始表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    // 2. 添加新列
    println("\n2. 添加新的列: email 和 created_at")
    spark.sql("ALTER TABLE users_basic ADD COLUMN email STRING COMMENT '邮箱'")
    spark.sql("ALTER TABLE users_basic ADD COLUMN created_at TIMESTAMP COMMENT '创建时间'")

    // 更新现有记录的新列值
    spark.sql("""
      UPDATE users_basic 
      SET email = CASE 
        WHEN name = 'Alice' THEN 'alice@example.com'
        WHEN name = 'Bob' THEN 'bob@example.com'
        WHEN name = 'Charlie' THEN 'charlie@example.com'
      END,
      created_at = CURRENT_TIMESTAMP()
    """)

    println("添加列后的表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    // 插入包含新列的新数据
    spark.sql("""
      INSERT INTO users_basic VALUES
      (4, 'David', 28, 'david@example.com', CURRENT_TIMESTAMP()),
      (5, 'Eve', 22, 'eve@example.com', CURRENT_TIMESTAMP())
    """)

    println("添加列后查询所有数据:")
    spark.sql("SELECT * FROM users_basic").show(false)

    // 3. 修改列名
    println("\n3. 修改列名: age -> user_age")
    spark.sql("ALTER TABLE users_basic RENAME COLUMN age TO user_age")

    println("修改列名后的表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    // 4. 修改列类型（需要兼容性）
    println("\n4. 修改列类型: user_age INT -> BIGINT")
    spark.sql("ALTER TABLE users_basic ALTER COLUMN user_age TYPE BIGINT")

    println("修改列类型后的表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    // 5. 添加嵌套结构
    println("\n5. 添加嵌套结构: address 结构体")
    spark.sql("ALTER TABLE users_basic ADD COLUMN address STRUCT<street: STRING, city: STRING, zipcode: STRING> COMMENT '地址信息'")

    // 更新嵌套结构数据
    spark.sql("""
      UPDATE users_basic 
      SET address = CASE 
        WHEN name = 'Alice' THEN NAMED_STRUCT('street', '123 Main St', 'city', 'New York', 'zipcode', '10001')
        WHEN name = 'Bob' THEN NAMED_STRUCT('street', '456 Oak Ave', 'city', 'Los Angeles', 'zipcode', '90210')
        ELSE address
      END
    """)

    println("添加嵌套结构后的表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    println("添加嵌套结构后查询所有数据:")
    spark.sql("SELECT *, address.street, address.city FROM users_basic").show(false)

    // 6. 添加数组类型列
    println("\n6. 添加数组类型列: tags")
    spark.sql("ALTER TABLE users_basic ADD COLUMN tags ARRAY<STRING> COMMENT '标签'")

    // 更新数组数据
    spark.sql("""
      UPDATE users_basic 
      SET tags = CASE 
        WHEN name = 'Alice' THEN ARRAY('vip', 'premium')
        WHEN name = 'Bob' THEN ARRAY('standard')
        ELSE tags
      END
    """)

    println("添加数组列后的表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    println("添加数组列后查询所有数据:")
    spark.sql("SELECT *, tags FROM users_basic").show(false)

    // 7. 查看表的历史版本
    println("\n7. 查看表的历史版本")
    spark.sql("SELECT * FROM users_basic.history").show(false)

    // 8. Schema 兼容性检查
    println("\n8. Schema 兼容性检查")
    try {
      // 尝试添加一个已存在的列（会失败）
      spark.sql("ALTER TABLE users_basic ADD COLUMN id BIGINT")
    } catch {
      case e: Exception =>
        println(s"添加重复列失败（预期行为）: ${e.getMessage}")
    }

    try {
      // 尝试修改为不兼容的类型（会失败）
      spark.sql("ALTER TABLE users_basic ALTER COLUMN name TYPE INT")
    } catch {
      case e: Exception =>
        println(s"修改为不兼容类型失败（预期行为）: ${e.getMessage}")
    }

    // 展示最终表结构
    println("\n最终表结构:")
    spark.sql("DESCRIBE users_basic").show(false)

    // 展示最终数据
    println("最终数据:")
    spark.sql("SELECT * FROM users_basic").show(false)

    spark.stop()
  }
}