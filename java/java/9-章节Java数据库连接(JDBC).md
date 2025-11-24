# 第九章：Java数据库连接(JDBC)

## 目录
1. [JDBC概述](#jdbc概述)
2. [JDBC架构](#jdbc架构)
3. [JDBC驱动类型](#jdbc驱动类型)
4. [数据库连接](#数据库连接)
5. [Statement与PreparedStatement](#statement与preparedstatement)
6. [ResultSet处理](#resultset处理)
7. [事务处理](#事务处理)
8. [连接池](#连接池)
9. [批处理](#批处理)
10. [元数据](#元数据)
11. [LOB数据处理](#lob数据处理)
12. [SQL注入防护](#sql注入防护)
13. [最佳实践](#最佳实践)
14. [常见陷阱与解决方案](#常见陷阱与解决方案)
15. [总结](#总结)

---

## JDBC概述

### 什么是JDBC
JDBC（Java Database Connectivity）是Java语言中用来规范客户端程序如何访问数据库的应用程序接口，提供了诸如查询和更新数据库中数据的方法。JDBC是面向关系型数据库的。

### JDBC的作用
1. 提供了统一的数据库访问接口
2. 屏蔽了不同数据库之间的差异
3. 简化了数据库操作的复杂性
4. 支持多种数据库管理系统

### JDBC的优势
- 标准化：遵循Java标准规范
- 可移植性：可在不同的平台上运行
- 易于维护：统一的接口降低了维护成本
- 高性能：直接与数据库通信，效率较高

---

## JDBC架构

### JDBC API
JDBC API包含两个包：
1. **java.sql**：所有与数据库相关的接口和类
2. **javax.sql**：扩展的JDBC API，包含连接池等高级特性

### JDBC驱动架构
JDBC驱动是JDBC API和特定数据库管理系统之间的桥梁，负责处理与数据库的通信。

### JDBC工作流程
1. 加载JDBC驱动
2. 建立数据库连接
3. 创建Statement对象
4. 执行SQL语句
5. 处理结果集
6. 关闭连接

---

## JDBC驱动类型

### Type 1: JDBC-ODBC桥接驱动
- 使用ODBC驱动连接数据库
- 需要安装ODBC驱动
- 性能较差，已不推荐使用

### Type 2: 本地API驱动
- 部分使用Java，部分使用本地代码
- 需要安装本地库
- 性能比Type 1好，但仍有限制

### Type 3: 网络协议驱动
- 完全由Java实现
- 通过中间件服务器连接数据库
- 可以连接多种数据库

### Type 4: 纯Java驱动（Thin驱动）
- 完全由Java实现
- 直接与数据库通信
- 性能最好，最常用
- 数据库厂商提供的驱动通常是这种类型

---

## 数据库连接

### 加载驱动
```java
// 方式1：Class.forName()（JDBC 4.0之前必需）
Class.forName("com.mysql.cj.jdbc.Driver");

// 方式2：自动加载（JDBC 4.0之后）
// 通过Service Provider机制自动加载驱动
```

### 建立连接
```java
// 基本连接方式
String url = "jdbc:mysql://localhost:3306/testdb";
String username = "root";
String password = "password";
Connection conn = DriverManager.getConnection(url, username, password);

// 带参数的连接
Properties props = new Properties();
props.setProperty("user", "root");
props.setProperty("password", "password");
props.setProperty("useSSL", "false");
props.setProperty("serverTimezone", "UTC");
Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/testdb", props);
```

### 连接URL格式
```
jdbc:<subprotocol>:<subname>
```
常见数据库URL格式：
- MySQL: `jdbc:mysql://hostname:port/databaseName`
- PostgreSQL: `jdbc:postgresql://hostname:port/databaseName`
- Oracle: `jdbc:oracle:thin:@hostname:port:databaseName`
- SQL Server: `jdbc:sqlserver://hostname:port;databaseName=databaseName`

### Connection接口常用方法
- `createStatement()`：创建Statement对象
- `prepareStatement(String sql)`：创建PreparedStatement对象
- `close()`：关闭连接
- `isClosed()`：检查连接是否已关闭
- `setAutoCommit(boolean autoCommit)`：设置自动提交
- `commit()`：提交事务
- `rollback()`：回滚事务

---

## Statement与PreparedStatement

### Statement
Statement用于执行静态SQL语句：

```java
Statement stmt = connection.createStatement();
// 执行查询
ResultSet rs = stmt.executeQuery("SELECT * FROM users");
// 执行更新
int rowsAffected = stmt.executeUpdate("INSERT INTO users(name, email) VALUES('John', 'john@example.com')");
// 执行任意SQL
boolean hasResultSet = stmt.execute("SELECT * FROM users");
```

### PreparedStatement
PreparedStatement用于执行预编译SQL语句，具有以下优势：
1. 防止SQL注入
2. 提高性能（预编译）
3. 更好的可读性

```java
String sql = "INSERT INTO users(name, email, age) VALUES(?, ?, ?)";
PreparedStatement pstmt = connection.prepareStatement(sql);
pstmt.setString(1, "John");
pstmt.setString(2, "john@example.com");
pstmt.setInt(3, 25);
int rowsAffected = pstmt.executeUpdate();
```

### CallableStatement
CallableStatement用于执行存储过程：

```java
String sql = "{call get_user_info(?)}";
CallableStatement cstmt = connection.prepareCall(sql);
cstmt.setInt(1, userId);
ResultSet rs = cstmt.executeQuery();
```

---

## ResultSet处理

### ResultSet类型
1. **TYPE_FORWARD_ONLY**：只能向前遍历（默认）
2. **TYPE_SCROLL_INSENSITIVE**：可滚动，但对数据变化不敏感
3. **TYPE_SCROLL_SENSITIVE**：可滚动，对数据变化敏感

### ResultSet并发性
1. **CONCUR_READ_ONLY**：只读（默认）
2. **CONCUR_UPDATABLE**：可更新

### 基本操作
```java
Statement stmt = connection.createStatement(
    ResultSet.TYPE_SCROLL_INSENSITIVE, 
    ResultSet.CONCUR_READ_ONLY);
ResultSet rs = stmt.executeQuery("SELECT * FROM users");

// 遍历结果集
while (rs.next()) {
    int id = rs.getInt("id");
    String name = rs.getString("name");
    String email = rs.getString("email");
    System.out.println("ID: " + id + ", Name: " + name + ", Email: " + email);
}

// 移动游标
rs.first();  // 移动到第一条记录
rs.last();   // 移动到最后一条记录
rs.previous(); // 移动到前一条记录
rs.absolute(5); // 移动到第5条记录
```

### 更新结果集
```java
Statement stmt = connection.createStatement(
    ResultSet.TYPE_SCROLL_INSENSITIVE, 
    ResultSet.CONCUR_UPDATABLE);
ResultSet rs = stmt.executeQuery("SELECT * FROM users");

// 更新记录
if (rs.next()) {
    rs.updateString("name", "Updated Name");
    rs.updateRow(); // 提交更新
}

// 插入新记录
rs.moveToInsertRow();
rs.updateString("name", "New User");
rs.updateString("email", "newuser@example.com");
rs.insertRow(); // 插入记录
```

---

## 事务处理

### 事务概念
事务是数据库操作的逻辑单元，具有ACID特性：
- **原子性（Atomicity）**：事务要么全部执行，要么全部不执行
- **一致性（Consistency）**：事务执行前后数据保持一致状态
- **隔离性（Isolation）**：并发事务之间相互隔离
- **持久性（Durability）**：事务提交后对数据库的改变是永久的

### JDBC事务处理
```java
Connection conn = DriverManager.getConnection(url, username, password);
try {
    // 关闭自动提交
    conn.setAutoCommit(false);
    
    // 执行多个操作
    PreparedStatement pstmt1 = conn.prepareStatement(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?");
    pstmt1.setDouble(1, 100.0);
    pstmt1.setInt(2, 1);
    pstmt1.executeUpdate();
    
    PreparedStatement pstmt2 = conn.prepareStatement(
        "UPDATE accounts SET balance = balance + ? WHERE id = ?");
    pstmt2.setDouble(1, 100.0);
    pstmt2.setInt(2, 2);
    pstmt2.executeUpdate();
    
    // 提交事务
    conn.commit();
    System.out.println("转账成功");
} catch (SQLException e) {
    try {
        // 回滚事务
        conn.rollback();
        System.out.println("转账失败，已回滚");
    } catch (SQLException rollbackEx) {
        rollbackEx.printStackTrace();
    }
} finally {
    try {
        // 恢复自动提交
        conn.setAutoCommit(true);
        conn.close();
    } catch (SQLException e) {
        e.printStackTrace();
    }
}
```

### 保存点
```java
Savepoint savepoint1 = conn.setSavepoint("savepoint1");
// 执行操作...
conn.rollback(savepoint1); // 回滚到保存点
```

---

## 连接池

### 连接池概念
连接池是创建和管理数据库连接的缓冲池，可以：
1. 减少连接创建和销毁的开销
2. 控制数据库连接数量
3. 提高系统性能和稳定性

### 常见连接池实现
1. **HikariCP**：高性能连接池
2. **Apache DBCP**：Apache Commons项目
3. **C3P0**：开源连接池

### HikariCP示例
```java
// 配置HikariCP
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:mysql://localhost:3306/testdb");
config.setUsername("root");
config.setPassword("password");
config.setMaximumPoolSize(10);

// 创建数据源
HikariDataSource dataSource = new HikariDataSource(config);

// 获取连接
Connection conn = dataSource.getConnection();
// 使用连接...
conn.close(); // 归还连接到池中
```

### 自定义简单连接池
```java
public class SimpleConnectionPool {
    private final Queue<Connection> connectionPool;
    private final String url;
    private final String user;
    private final String password;
    private final int maxPoolSize;
    
    public SimpleConnectionPool(String url, String user, String password, int poolSize) {
        this.url = url;
        this.user = user;
        this.password = password;
        this.maxPoolSize = poolSize;
        this.connectionPool = new ConcurrentLinkedQueue<>();
        
        // 初始化连接池
        for (int i = 0; i < poolSize; i++) {
            connectionPool.add(createConnection());
        }
    }
    
    private Connection createConnection() {
        try {
            return DriverManager.getConnection(url, user, password);
        } catch (SQLException e) {
            throw new RuntimeException("创建数据库连接失败", e);
        }
    }
    
    public Connection getConnection() throws SQLException {
        Connection conn = connectionPool.poll();
        if (conn == null) {
            // 池中没有连接，创建新连接
            conn = createConnection();
        } else if (conn.isClosed()) {
            // 连接已关闭，创建新连接
            conn = createConnection();
        }
        return conn;
    }
    
    public void releaseConnection(Connection conn) {
        if (conn != null) {
            connectionPool.offer(conn);
        }
    }
}
```

---

## 批处理

### Statement批处理
```java
Statement stmt = connection.createStatement();
stmt.addBatch("INSERT INTO users(name, email) VALUES('User1', 'user1@example.com')");
stmt.addBatch("INSERT INTO users(name, email) VALUES('User2', 'user2@example.com')");
stmt.addBatch("INSERT INTO users(name, email) VALUES('User3', 'user3@example.com')");

// 执行批处理
int[] results = stmt.executeBatch();
```

### PreparedStatement批处理
```java
String sql = "INSERT INTO users(name, email) VALUES(?, ?)";
PreparedStatement pstmt = connection.prepareStatement(sql);

for (int i = 0; i < 1000; i++) {
    pstmt.setString(1, "User" + i);
    pstmt.setString(2, "user" + i + "@example.com");
    pstmt.addBatch();
    
    // 每100条执行一次批处理
    if (i % 100 == 0) {
        pstmt.executeBatch();
        pstmt.clearBatch();
    }
}

// 执行剩余的批处理
pstmt.executeBatch();
```

### 批处理的优势
1. 减少网络往返次数
2. 提高执行效率
3. 减少数据库负载

---

## 元数据

### DatabaseMetaData
DatabaseMetaData提供了关于数据库的信息：

```java
DatabaseMetaData metaData = connection.getMetaData();
System.out.println("数据库产品名称: " + metaData.getDatabaseProductName());
System.out.println("数据库版本: " + metaData.getDatabaseProductVersion());
System.out.println("驱动名称: " + metaData.getDriverName());
System.out.println("驱动版本: " + metaData.getDriverVersion());

// 获取表信息
ResultSet tables = metaData.getTables(null, null, "%", new String[]{"TABLE"});
while (tables.next()) {
    System.out.println("表名: " + tables.getString("TABLE_NAME"));
}
```

### ResultSetMetaData
ResultSetMetaData提供了关于结果集的信息：

```java
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM users");
ResultSetMetaData rsMetaData = rs.getMetaData();

int columnCount = rsMetaData.getColumnCount();
for (int i = 1; i <= columnCount; i++) {
    System.out.println("列名: " + rsMetaData.getColumnName(i));
    System.out.println("类型: " + rsMetaData.getColumnTypeName(i));
    System.out.println("大小: " + rsMetaData.getColumnDisplaySize(i));
}
```

---

## LOB数据处理

### BLOB处理
BLOB（Binary Large Object）用于存储二进制数据：

```java
// 插入BLOB数据
String insertSQL = "INSERT INTO documents(title, content) VALUES(?, ?)";
PreparedStatement pstmt = connection.prepareStatement(insertSQL);
pstmt.setString(1, "文档标题");
pstmt.setBlob(2, new FileInputStream("document.pdf"));
pstmt.executeUpdate();

// 读取BLOB数据
String selectSQL = "SELECT title, content FROM documents WHERE id = ?";
PreparedStatement selectStmt = connection.prepareStatement(selectSQL);
selectStmt.setInt(1, documentId);
ResultSet rs = selectStmt.executeQuery();

if (rs.next()) {
    String title = rs.getString("title");
    Blob blob = rs.getBlob("content");
    InputStream inputStream = blob.getBinaryStream();
    // 处理输入流...
}
```

### CLOB处理
CLOB（Character Large Object）用于存储大文本数据：

```java
// 插入CLOB数据
String insertSQL = "INSERT INTO articles(title, content) VALUES(?, ?)";
PreparedStatement pstmt = connection.prepareStatement(insertSQL);
pstmt.setString(1, "文章标题");
pstmt.setClob(2, new StringReader("很长的文章内容..."));
pstmt.executeUpdate();

// 读取CLOB数据
String selectSQL = "SELECT title, content FROM articles WHERE id = ?";
PreparedStatement selectStmt = connection.prepareStatement(selectSQL);
selectStmt.setInt(1, articleId);
ResultSet rs = selectStmt.executeQuery();

if (rs.next()) {
    String title = rs.getString("title");
    Clob clob = rs.getClob("content");
    Reader reader = clob.getCharacterStream();
    // 处理字符流...
}
```

---

## SQL注入防护

### 什么是SQL注入
SQL注入是攻击者通过在输入中插入恶意SQL代码来操纵数据库查询的行为。

### SQL注入示例
```java
// 危险的做法 - 容易受到SQL注入攻击
String userInput = "'; DROP TABLE users; --";
String sql = "SELECT * FROM users WHERE name = '" + userInput + "'";
Statement stmt = connection.createStatement();
stmt.executeQuery(sql); // 可能会删除users表！

// 安全的做法 - 使用PreparedStatement
String sql = "SELECT * FROM users WHERE name = ?";
PreparedStatement pstmt = connection.prepareStatement(sql);
pstmt.setString(1, userInput);
ResultSet rs = pstmt.executeQuery(); // 安全地处理用户输入
```

### 防护措施
1. 使用PreparedStatement而不是Statement
2. 输入验证和过滤
3. 最小权限原则
4. 使用ORM框架（如Hibernate）

---

## 最佳实践

### 1. 资源管理
始终使用try-with-resources语句确保资源正确关闭：

```java
try (Connection conn = dataSource.getConnection();
     PreparedStatement pstmt = conn.prepareStatement(sql);
     ResultSet rs = pstmt.executeQuery()) {
    // 使用资源...
} catch (SQLException e) {
    // 处理异常...
}
```

### 2. 连接池使用
- 使用成熟的连接池实现
- 合理设置池大小
- 监控连接池状态

### 3. 异常处理
- 捕获并适当处理SQLException
- 记录详细的错误日志
- 实现重试机制

### 4. 性能优化
- 使用PreparedStatement提高性能
- 合理使用批处理
- 避免在循环中执行查询
- 使用索引优化查询

### 5. 安全性
- 防止SQL注入
- 敏感信息加密存储
- 使用最小权限原则

---

## 常见陷阱与解决方案

### 1. 忘记关闭资源
**问题**：忘记关闭Connection、Statement、ResultSet导致内存泄露
**解决方案**：使用try-with-resources或finally块确保资源关闭

### 2. 连接泄露
**问题**：未正确归还连接到连接池导致连接耗尽
**解决方案**：确保每次使用完连接后调用close()方法

### 3. 事务未提交或回滚
**问题**：事务未正确提交或回滚导致数据不一致
**解决方案**：在try-catch-finally块中正确处理事务

### 4. SQL注入漏洞
**问题**：使用字符串拼接构造SQL导致安全风险
**解决方案**：使用PreparedStatement参数化查询

### 5. 性能问题
**问题**：频繁创建和销毁连接、未使用批处理等导致性能低下
**解决方案**：使用连接池、批处理、合理的查询设计

---

## 总结

JDBC作为Java访问数据库的标准API，为我们提供了强大而灵活的数据库操作能力。通过本章的学习，我们了解了：

1. JDBC的基本概念和架构
2. 如何建立数据库连接
3. Statement和PreparedStatement的使用
4. 结果集的处理方式
5. 事务管理和连接池的实现
6. 批处理和元数据的操作
7. LOB数据的处理
8. SQL注入防护措施
9. 最佳实践和常见问题解决

掌握JDBC对于Java开发者来说至关重要，它不仅是数据库操作的基础，也是理解更高级ORM框架的前提。在实际开发中，我们应该：
- 遵循最佳实践，确保代码的安全性和性能
- 合理使用连接池提高系统效率
- 注意资源管理，防止内存泄露
- 采用适当的异常处理机制

随着技术的发展，虽然出现了许多ORM框架（如Hibernate、MyBatis），但理解JDBC的工作原理仍然非常重要，它有助于我们更好地使用这些高级框架并解决相关问题。