// Access Control for Iceberg Tables
// ================================

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.iceberg.spark.Spark3Util
import java.time.LocalDateTime
import scala.util.{Success, Failure, Try}

object AccessControl {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Iceberg Access Control")
      .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg_catalog.type", "hive")
      .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083")
      .config("spark.sql.catalog.iceberg_catalog.warehouse", "hdfs://namenode:9000/warehouse")
      // Enable row-level security (this would depend on your specific setup)
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .getOrCreate()

    import spark.implicits._

    // Case classes for access control entities
    case class User(username: String, roles: Set[String], department: String)
    case class Role(name: String, permissions: Set[String])
    case class TableAccessRule(
      tableName: String,
      roleName: String,
      permissions: Set[String], // SELECT, INSERT, UPDATE, DELETE, ALTER
      conditions: Option[String] = None // Row/column level filtering conditions
    )
    case class DataAccessLog(
      logId: String,
      username: String,
      tableName: String,
      operation: String,
      timestamp: LocalDateTime,
      success: Boolean,
      ipAddress: String
    )

    // Sample users and roles
    val users = Map(
      "analyst1" -> User("analyst1", Set("analyst"), "marketing"),
      "analyst2" -> User("analyst2", Set("analyst"), "finance"),
      "manager1" -> User("manager1", Set("manager", "analyst"), "marketing"),
      "admin1" -> User("admin1", Set("admin"), "it"),
      "engineer1" -> User("engineer1", Set("engineer"), "engineering")
    )

    val roles = Map(
      "analyst" -> Role("analyst", Set("SELECT")),
      "manager" -> Role("manager", Set("SELECT", "INSERT", "UPDATE")),
      "admin" -> Role("admin", Set("SELECT", "INSERT", "UPDATE", "DELETE", "ALTER")),
      "engineer" -> Role("engineer", Set("SELECT", "INSERT", "UPDATE", "ALTER"))
    )

    // Access control rules
    val accessRules = Seq(
      TableAccessRule("iceberg_catalog.transactions", "analyst", Set("SELECT")),
      TableAccessRule("iceberg_catalog.transactions", "manager", Set("SELECT", "INSERT", "UPDATE")),
      TableAccessRule("iceberg_catalog.transactions", "admin", Set("SELECT", "INSERT", "UPDATE", "DELETE", "ALTER")),
      TableAccessRule("iceberg_catalog.customers", "analyst", Set("SELECT"), Some("department = 'marketing'")),
      TableAccessRule("iceberg_catalog.customers", "manager", Set("SELECT", "INSERT", "UPDATE")),
      TableAccessRule("iceberg_catalog.customers", "admin", Set("SELECT", "INSERT", "UPDATE", "DELETE", "ALTER")),
      TableAccessRule("iceberg_catalog.products", "analyst", Set("SELECT")),
      TableAccessRule("iceberg_catalog.products", "manager", Set("SELECT", "INSERT", "UPDATE")),
      TableAccessRule("iceberg_catalog.products", "admin", Set("SELECT", "INSERT", "UPDATE", "DELETE", "ALTER")),
      TableAccessRule("iceberg_catalog.financial_reports", "analyst", Set("SELECT"), Some("department = current_user_department()")),
      TableAccessRule("iceberg_catalog.financial_reports", "manager", Set("SELECT"), Some("department = current_user_department()")),
      TableAccessRule("iceberg_catalog.financial_reports", "admin", Set("SELECT", "INSERT", "UPDATE", "DELETE", "ALTER"))
    )

    // Initialize access control logs table
    def initializeAccessLogs(): Unit = {
      println("Initializing access control logs table...")
      
      val logSchema = StructType(Seq(
        StructField("log_id", StringType, nullable = false),
        StructField("username", StringType, nullable = false),
        StructField("table_name", StringType, nullable = false),
        StructField("operation", StringType, nullable = false),
        StructField("timestamp", TimestampType, nullable = false),
        StructField("success", BooleanType, nullable = false),
        StructField("ip_address", StringType, nullable = false)
      ))
      
      spark.createDataFrame(spark.sparkContext.emptyRDD[Row], logSchema)
        .write
        .format("iceberg")
        .mode("ignore")
        .save("iceberg_catalog.access_logs")
      
      println("Access control logs table initialized")
    }

    // Check if user has permission for a specific operation on a table
    def checkPermission(username: String, tableName: String, operation: String): Boolean = {
      // Get user information
      val userOpt = users.get(username)
      if (userOpt.isEmpty) {
        logAccessAttempt(username, tableName, operation, false, "User not found")
        return false
      }
      
      val user = userOpt.get
      println(s"Checking permission for user: $username on table: $tableName for operation: $operation")
      
      // Check if user has any role that grants this permission
      val hasPermission = user.roles.exists { roleName =>
        // Find access rules for this table and role
        accessRules.exists { rule =>
          rule.tableName == tableName && 
          rule.roleName == roleName && 
          rule.permissions.contains(operation)
        }
      }
      
      logAccessAttempt(username, tableName, operation, hasPermission, if (hasPermission) "Permission granted" else "Permission denied")
      hasPermission
    }

    // Apply row-level filtering based on user context
    def applyRowLevelFiltering(username: String, tableName: String, df: org.apache.spark.sql.DataFrame): org.apache.spark.sql.DataFrame = {
      val userOpt = users.get(username)
      if (userOpt.isEmpty) return df
      
      val user = userOpt.get
      var filteredDF = df
      
      // Apply any row-level filters from access rules
      accessRules.foreach { rule =>
        if (rule.tableName == tableName && user.roles.contains(rule.roleName) && rule.conditions.isDefined) {
          val condition = rule.conditions.get.replace("current_user_department()", s"'${user.department}'")
          println(s"Applying row-level filter for user $username on table $tableName: $condition")
          filteredDF = filteredDF.filter(condition)
        }
      }
      
      filteredDF
    }

    // Log access attempts
    def logAccessAttempt(username: String, tableName: String, operation: String, success: Boolean, reason: String): Unit = {
      val logId = java.util.UUID.randomUUID().toString
      val timestamp = LocalDateTime.now()
      val ipAddress = "127.0.0.1" // In a real implementation, this would come from the request context
      
      val accessLog = DataAccessLog(logId, username, tableName, operation, timestamp, success, ipAddress)
      
      val logDF = Seq(accessLog).toDF()
      logDF.write
        .format("iceberg")
        .mode("append")
        .save("iceberg_catalog.access_logs")
      
      if (!success) {
        println(s"ACCESS DENIED: User $username attempted $operation on $tableName - $reason")
      } else {
        println(s"ACCESS GRANTED: User $username performed $operation on $tableName")
      }
    }

    // Create a secure view with access controls
    def createSecureView(viewName: String, baseTable: String, owner: String): Unit = {
      println(s"Creating secure view: $viewName based on $baseTable")
      
      // Check if owner has ALTER permission on base table
      if (!checkPermission(owner, baseTable, "ALTER")) {
        println(s"Permission denied: User $owner cannot create view on $baseTable")
        return
      }
      
      // Create view with row-level security
      val user = users(owner)
      val departmentCondition = s"department = '${user.department}'"
      
      val createViewSQL = 
        s"""
           |CREATE VIEW $viewName AS
           |SELECT * FROM $baseTable
           |WHERE $departmentCondition
         """.stripMargin
      
      println(s"Executing: $createViewSQL")
      spark.sql(createViewSQL)
      println(s"Secure view $viewName created successfully")
    }

    // Audit access logs
    def auditAccessLogs(durationHours: Int = 24): Unit = {
      println(s"Auditing access logs for the last $durationHours hours...")
      
      val auditTime = java.sql.Timestamp.valueOf(LocalDateTime.now().minusHours(durationHours))
      
      val failedAttempts = spark.sql(
        s"""
           |SELECT 
           |  username,
           |  table_name,
           |  operation,
           |  timestamp,
           |  ip_address,
           |  COUNT(*) as attempt_count
           |FROM iceberg_catalog.access_logs
           |WHERE success = false AND timestamp >= '$auditTime'
           |GROUP BY username, table_name, operation, timestamp, ip_address
           |ORDER BY attempt_count DESC
        """.stripMargin)
      
      val failedCount = failedAttempts.count()
      if (failedCount > 0) {
        println(s"Found $failedCount failed access attempts:")
        failedAttempts.show(false)
      } else {
        println("No failed access attempts found")
      }
      
      // Show successful accesses by admins
      val adminAccesses = spark.sql(
        s"""
           |SELECT 
           |  username,
           |  table_name,
           |  operation,
           |  timestamp
           |FROM iceberg_catalog.access_logs
           |WHERE success = true 
           |  AND username IN (${users.filter(_._2.roles.contains("admin")).keys.map("'" + _ + "'").mkString(", ")})
           |  AND timestamp >= '$auditTime'
           |ORDER BY timestamp DESC
           |LIMIT 10
        """.stripMargin)
      
      println("Recent admin access activities:")
      adminAccesses.show(false)
    }

    // Grant permission to a user
    def grantPermission(username: String, tableName: String, permissions: Set[String], granter: String): Unit = {
      println(s"Granting permissions to user: $username on table: $tableName")
      
      // Check if granter has admin privileges
      if (!users.get(granter).exists(_.roles.contains("admin"))) {
        println(s"Permission denied: Only admins can grant permissions")
        return
      }
      
      // In a real implementation, this would update the access control system
      // For this example, we'll just simulate the action
      val permissionsStr = permissions.mkString(", ")
      println(s"Granted $permissionsStr on $tableName to $username by $granter")
      
      // Log the granting action
      logAccessAttempt(granter, tableName, "GRANT", true, s"Granted $permissionsStr to $username")
    }

    // Revoke permission from a user
    def revokePermission(username: String, tableName: String, permissions: Set[String], revoker: String): Unit = {
      println(s"Revoking permissions from user: $username on table: $tableName")
      
      // Check if revoker has admin privileges
      if (!users.get(revoker).exists(_.roles.contains("admin"))) {
        println(s"Permission denied: Only admins can revoke permissions")
        return
      }
      
      // In a real implementation, this would update the access control system
      // For this example, we'll just simulate the action
      val permissionsStr = permissions.mkString(", ")
      println(s"Revoked $permissionsStr on $tableName from $username by $revoker")
      
      // Log the revoking action
      logAccessAttempt(revoker, tableName, "REVOKE", true, s"Revoked $permissionsStr from $username")
    }

    // Execute access control functions
    initializeAccessLogs()
    
    // Test permission checks
    println("\n=== Testing Permission Checks ===")
    checkPermission("analyst1", "iceberg_catalog.transactions", "SELECT")  // Should be granted
    checkPermission("analyst1", "iceberg_catalog.transactions", "INSERT")  // Should be denied
    checkPermission("manager1", "iceberg_catalog.transactions", "INSERT")  // Should be granted
    checkPermission("admin1", "iceberg_catalog.transactions", "DELETE")    // Should be granted
    
    // Test row-level filtering
    println("\n=== Testing Row-Level Filtering ===")
    val customersDF = spark.table("iceberg_catalog.customers")
    val filteredDF = applyRowLevelFiltering("analyst1", "iceberg_catalog.customers", customersDF)
    println("Filtered customers data for analyst1:")
    filteredDF.show(false)
    
    // Test secure view creation
    println("\n=== Testing Secure View Creation ===")
    createSecureView("iceberg_catalog.marketing_customers", "iceberg_catalog.customers", "manager1")
    
    // Test audit functionality
    println("\n=== Testing Access Audit ===")
    auditAccessLogs(24)
    
    // Test grant/revoke functionality
    println("\n=== Testing Grant/Revoke ===")
    grantPermission("analyst1", "iceberg_catalog.products", Set("SELECT"), "admin1")
    revokePermission("analyst1", "iceberg_catalog.products", Set("SELECT"), "admin1")
    
    spark.stop()
  }
}