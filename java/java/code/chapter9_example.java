import java.sql.*;
import java.util.Properties;
import java.io.*;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import javax.sql.DataSource;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

/**
 * 第九章：Java数据库连接(JDBC) - 完整示例代码
 * 
 * 本示例涵盖了JDBC的所有核心概念和最佳实践：
 * 1. 数据库连接建立
 * 2. Statement与PreparedStatement使用
 * 3. ResultSet处理
 * 4. 事务管理
 * 5. 连接池实现
 * 6. 批处理操作
 * 7. 元数据获取
 * 8. LOB数据处理
 * 9. SQL注入防护
 * 10. 综合示例：学生管理系统
 */

// 1. 数据库连接示例
class DatabaseConnectionExample {
    // 基本连接方式
    public static Connection getBasicConnection() throws SQLException {
        String url = "jdbc:mysql://localhost:3306/testdb";
        String username = "root";
        String password = "password";
        return DriverManager.getConnection(url, username, password);
    }
    
    // 带参数的连接方式
    public static Connection getConnectionWithProperties() throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", "root");
        props.setProperty("password", "password");
        props.setProperty("useSSL", "false");
        props.setProperty("serverTimezone", "UTC");
        return DriverManager.getConnection("jdbc:mysql://localhost:3306/testdb", props);
    }
    
    // 测试连接
    public static void testConnection() {
        try (Connection conn = getBasicConnection()) {
            System.out.println("数据库连接成功！");
            System.out.println("数据库产品名称: " + conn.getMetaData().getDatabaseProductName());
            System.out.println("数据库版本: " + conn.getMetaData().getDatabaseProductVersion());
        } catch (SQLException e) {
            System.err.println("数据库连接失败: " + e.getMessage());
        }
    }
}

// 2. Statement使用示例
class StatementExample {
    public static void executeQueries(Connection conn) throws SQLException {
        // 创建Statement
        Statement stmt = conn.createStatement();
        
        // 执行查询
        ResultSet rs = stmt.executeQuery("SELECT * FROM users LIMIT 5");
        System.out.println("查询结果:");
        while (rs.next()) {
            System.out.println("ID: " + rs.getInt("id") + 
                             ", Name: " + rs.getString("name") + 
                             ", Email: " + rs.getString("email"));
        }
        rs.close();
        
        // 执行更新
        int rowsInserted = stmt.executeUpdate(
            "INSERT INTO users(name, email) VALUES('Test User', 'test@example.com')");
        System.out.println("插入行数: " + rowsInserted);
        
        // 执行删除
        int rowsDeleted = stmt.executeUpdate("DELETE FROM users WHERE name='Test User'");
        System.out.println("删除行数: " + rowsDeleted);
        
        stmt.close();
    }
}

// 3. PreparedStatement使用示例（防SQL注入）
class PreparedStatementExample {
    // 不安全的方式（容易受到SQL注入攻击）
    public static void unsafeQuery(Connection conn, String userInput) throws SQLException {
        String sql = "SELECT * FROM users WHERE name = '" + userInput + "'";
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(sql);
        System.out.println("不安全查询结果:");
        while (rs.next()) {
            System.out.println("ID: " + rs.getInt("id") + ", Name: " + rs.getString("name"));
        }
        rs.close();
        stmt.close();
    }
    
    // 安全的方式（使用PreparedStatement）
    public static void safeQuery(Connection conn, String userInput) throws SQLException {
        String sql = "SELECT * FROM users WHERE name = ?";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        pstmt.setString(1, userInput);
        ResultSet rs = pstmt.executeQuery();
        System.out.println("安全查询结果:");
        while (rs.next()) {
            System.out.println("ID: " + rs.getInt("id") + ", Name: " + rs.getString("name"));
        }
        rs.close();
        pstmt.close();
    }
    
    // 参数化插入
    public static void insertUser(Connection conn, String name, String email, int age) throws SQLException {
        String sql = "INSERT INTO users(name, email, age) VALUES(?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, name);
            pstmt.setString(2, email);
            pstmt.setInt(3, age);
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("插入用户成功，影响行数: " + rowsAffected);
        }
    }
}

// 4. ResultSet处理示例
class ResultSetExample {
    public static void processResultSet(Connection conn) throws SQLException {
        // 创建可滚动的结果集
        Statement stmt = conn.createStatement(
            ResultSet.TYPE_SCROLL_INSENSITIVE, 
            ResultSet.CONCUR_READ_ONLY);
        
        ResultSet rs = stmt.executeQuery("SELECT * FROM users ORDER BY id");
        
        // 向后遍历
        System.out.println("向后遍历结果:");
        while (rs.next()) {
            System.out.println("ID: " + rs.getInt("id") + ", Name: " + rs.getString("name"));
        }
        
        // 向前遍历
        System.out.println("\n向前遍历结果:");
        while (rs.previous()) {
            System.out.println("ID: " + rs.getInt("id") + ", Name: " + rs.getString("name"));
        }
        
        // 移动到指定位置
        if (rs.last()) {
            System.out.println("\n最后一条记录: ID=" + rs.getInt("id"));
        }
        
        if (rs.first()) {
            System.out.println("第一条记录: ID=" + rs.getInt("id"));
        }
        
        rs.close();
        stmt.close();
    }
}

// 5. 事务处理示例
class TransactionExample {
    public static void transferMoney(Connection conn, int fromAccountId, int toAccountId, double amount) {
        try {
            // 关闭自动提交
            conn.setAutoCommit(false);
            
            // 扣款
            PreparedStatement debitStmt = conn.prepareStatement(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?");
            debitStmt.setDouble(1, amount);
            debitStmt.setInt(2, fromAccountId);
            int debitRows = debitStmt.executeUpdate();
            
            // 入账
            PreparedStatement creditStmt = conn.prepareStatement(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?");
            creditStmt.setDouble(1, amount);
            creditStmt.setInt(2, toAccountId);
            int creditRows = creditStmt.executeUpdate();
            
            // 检查操作是否成功
            if (debitRows > 0 && creditRows > 0) {
                conn.commit();
                System.out.println("转账成功: " + amount + " 从账户 " + fromAccountId + " 到账户 " + toAccountId);
            } else {
                conn.rollback();
                System.out.println("转账失败，已回滚");
            }
            
            debitStmt.close();
            creditStmt.close();
        } catch (SQLException e) {
            try {
                conn.rollback();
                System.out.println("转账异常，已回滚: " + e.getMessage());
            } catch (SQLException rollbackEx) {
                System.err.println("回滚失败: " + rollbackEx.getMessage());
            }
        } finally {
            try {
                conn.setAutoCommit(true);
            } catch (SQLException e) {
                System.err.println("恢复自动提交失败: " + e.getMessage());
            }
        }
    }
}

// 6. 简单连接池实现
class SimpleConnectionPool {
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
    
    public int getAvailableConnections() {
        return connectionPool.size();
    }
}

// 7. 批处理示例
class BatchProcessingExample {
    // Statement批处理
    public static void statementBatch(Connection conn) throws SQLException {
        Statement stmt = conn.createStatement();
        stmt.addBatch("INSERT INTO users(name, email) VALUES('Batch User 1', 'batch1@example.com')");
        stmt.addBatch("INSERT INTO users(name, email) VALUES('Batch User 2', 'batch2@example.com')");
        stmt.addBatch("INSERT INTO users(name, email) VALUES('Batch User 3', 'batch3@example.com')");
        
        // 执行批处理
        int[] results = stmt.executeBatch();
        System.out.println("Statement批处理结果:");
        for (int i = 0; i < results.length; i++) {
            System.out.println("第" + (i+1) + "个操作影响行数: " + results[i]);
        }
        
        stmt.close();
    }
    
    // PreparedStatement批处理
    public static void preparedStatementBatch(Connection conn) throws SQLException {
        String sql = "INSERT INTO users(name, email) VALUES(?, ?)";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        
        for (int i = 1; i <= 5; i++) {
            pstmt.setString(1, "Prepared Batch User " + i);
            pstmt.setString(2, "prepared" + i + "@example.com");
            pstmt.addBatch();
        }
        
        // 执行批处理
        int[] results = pstmt.executeBatch();
        System.out.println("PreparedStatement批处理结果:");
        for (int i = 0; i < results.length; i++) {
            System.out.println("第" + (i+1) + "个操作影响行数: " + results[i]);
        }
        
        pstmt.close();
    }
}

// 8. 元数据示例
class MetadataExample {
    // 数据库元数据
    public static void showDatabaseMetadata(Connection conn) throws SQLException {
        DatabaseMetaData metaData = conn.getMetaData();
        System.out.println("=== 数据库元数据 ===");
        System.out.println("数据库产品名称: " + metaData.getDatabaseProductName());
        System.out.println("数据库版本: " + metaData.getDatabaseProductVersion());
        System.out.println("驱动名称: " + metaData.getDriverName());
        System.out.println("驱动版本: " + metaData.getDriverVersion());
        System.out.println("用户名: " + metaData.getUserName());
        
        // 获取表信息
        System.out.println("\n=== 表信息 ===");
        ResultSet tables = metaData.getTables(null, null, "%", new String[]{"TABLE"});
        while (tables.next()) {
            System.out.println("表名: " + tables.getString("TABLE_NAME"));
        }
        tables.close();
    }
    
    // 结果集元数据
    public static void showResultSetMetadata(Connection conn) throws SQLException {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT id, name, email FROM users LIMIT 1");
        
        ResultSetMetaData rsMetaData = rs.getMetaData();
        System.out.println("\n=== 结果集元数据 ===");
        int columnCount = rsMetaData.getColumnCount();
        for (int i = 1; i <= columnCount; i++) {
            System.out.println("列" + i + ":");
            System.out.println("  名称: " + rsMetaData.getColumnName(i));
            System.out.println("  类型: " + rsMetaData.getColumnTypeName(i));
            System.out.println("  大小: " + rsMetaData.getColumnDisplaySize(i));
        }
        
        rs.close();
        stmt.close();
    }
}

// 9. LOB数据处理示例
class LOBExample {
    // BLOB处理示例
    public static void handleBLOB(Connection conn) throws SQLException, IOException {
        // 插入BLOB数据（模拟）
        String insertSQL = "INSERT INTO documents(title, content) VALUES(?, ?)";
        PreparedStatement pstmt = conn.prepareStatement(insertSQL);
        pstmt.setString(1, "测试文档");
        // 模拟BLOB数据
        byte[] fakeData = "这是一个测试文档的内容".getBytes("UTF-8");
        pstmt.setBytes(2, fakeData);
        pstmt.executeUpdate();
        pstmt.close();
        
        // 读取BLOB数据
        String selectSQL = "SELECT title, content FROM documents WHERE title = ?";
        PreparedStatement selectStmt = conn.prepareStatement(selectSQL);
        selectStmt.setString(1, "测试文档");
        ResultSet rs = selectStmt.executeQuery();
        
        if (rs.next()) {
            String title = rs.getString("title");
            byte[] content = rs.getBytes("content");
            System.out.println("BLOB数据读取:");
            System.out.println("标题: " + title);
            System.out.println("内容: " + new String(content, "UTF-8"));
        }
        
        rs.close();
        selectStmt.close();
    }
    
    // CLOB处理示例
    public static void handleCLOB(Connection conn) throws SQLException {
        // 插入CLOB数据（模拟）
        String insertSQL = "INSERT INTO articles(title, content) VALUES(?, ?)";
        PreparedStatement pstmt = conn.prepareStatement(insertSQL);
        pstmt.setString(1, "测试文章");
        pstmt.setString(2, "这是一篇很长的文章内容，用于测试CLOB数据的处理...");
        pstmt.executeUpdate();
        pstmt.close();
        
        // 读取CLOB数据
        String selectSQL = "SELECT title, content FROM articles WHERE title = ?";
        PreparedStatement selectStmt = conn.prepareStatement(selectSQL);
        selectStmt.setString(1, "测试文章");
        ResultSet rs = selectStmt.executeQuery();
        
        if (rs.next()) {
            String title = rs.getString("title");
            String content = rs.getString("content");
            System.out.println("CLOB数据读取:");
            System.out.println("标题: " + title);
            System.out.println("内容: " + content);
        }
        
        rs.close();
        selectStmt.close();
    }
}

// 10. HikariCP连接池示例
class HikariCPExample {
    public static DataSource createHikariDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/testdb");
        config.setUsername("root");
        config.setPassword("password");
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(2);
        config.setConnectionTimeout(30000);
        config.setIdleTimeout(600000);
        config.setMaxLifetime(1800000);
        
        return new HikariDataSource(config);
    }
    
    public static void testHikariCP(DataSource dataSource) {
        try (Connection conn = dataSource.getConnection()) {
            System.out.println("HikariCP连接成功!");
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT 1");
            if (rs.next()) {
                System.out.println("查询结果: " + rs.getInt(1));
            }
            rs.close();
            stmt.close();
        } catch (SQLException e) {
            System.err.println("HikariCP连接失败: " + e.getMessage());
        }
    }
}

// 11. 综合示例：学生管理系统
class StudentManagementSystem {
    private DataSource dataSource;
    
    public StudentManagementSystem(DataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    // 创建学生表
    public void createStudentsTable() {
        String sql = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT,
                email VARCHAR(100),
                grade DOUBLE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """;
        
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
            System.out.println("学生表创建成功");
        } catch (SQLException e) {
            System.err.println("创建学生表失败: " + e.getMessage());
        }
    }
    
    // 添加学生
    public boolean addStudent(String name, int age, String email, double grade) {
        String sql = "INSERT INTO students(name, age, email, grade) VALUES(?, ?, ?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, name);
            pstmt.setInt(2, age);
            pstmt.setString(3, email);
            pstmt.setDouble(4, grade);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            System.err.println("添加学生失败: " + e.getMessage());
            return false;
        }
    }
    
    // 查询所有学生
    public void listAllStudents() {
        String sql = "SELECT * FROM students ORDER BY id";
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            System.out.println("=== 所有学生信息 ===");
            while (rs.next()) {
                System.out.printf("ID: %d, 姓名: %s, 年龄: %d, 邮箱: %s, 成绩: %.2f, 创建时间: %s%n",
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getInt("age"),
                    rs.getString("email"),
                    rs.getDouble("grade"),
                    rs.getTimestamp("created_at"));
            }
        } catch (SQLException e) {
            System.err.println("查询学生失败: " + e.getMessage());
        }
    }
    
    // 根据ID查询学生
    public void findStudentById(int id) {
        String sql = "SELECT * FROM students WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            ResultSet rs = pstmt.executeQuery();
            
            if (rs.next()) {
                System.out.println("=== 学生信息 ===");
                System.out.printf("ID: %d, 姓名: %s, 年龄: %d, 邮箱: %s, 成绩: %.2f, 创建时间: %s%n",
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getInt("age"),
                    rs.getString("email"),
                    rs.getDouble("grade"),
                    rs.getTimestamp("created_at"));
            } else {
                System.out.println("未找到ID为 " + id + " 的学生");
            }
            rs.close();
        } catch (SQLException e) {
            System.err.println("查询学生失败: " + e.getMessage());
        }
    }
    
    // 更新学生成绩
    public boolean updateStudentGrade(int id, double newGrade) {
        String sql = "UPDATE students SET grade = ? WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, newGrade);
            pstmt.setInt(2, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            System.err.println("更新成绩失败: " + e.getMessage());
            return false;
        }
    }
    
    // 删除学生
    public boolean deleteStudent(int id) {
        String sql = "DELETE FROM students WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            System.err.println("删除学生失败: " + e.getMessage());
            return false;
        }
    }
    
    // 统计学生人数
    public void countStudents() {
        String sql = "SELECT COUNT(*) as total FROM students";
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            if (rs.next()) {
                System.out.println("学生总人数: " + rs.getInt("total"));
            }
        } catch (SQLException e) {
            System.err.println("统计学生人数失败: " + e.getMessage());
        }
    }
}

// 主测试类
public class Chapter9Example {
    public static void main(String[] args) {
        System.out.println("第九章：Java数据库连接(JDBC) 示例程序");
        System.out.println("=====================================");
        
        try {
            // 1. 测试基本连接
            System.out.println("\n1. 测试数据库连接:");
            DatabaseConnectionExample.testConnection();
            
            // 获取连接用于后续示例
            Connection conn = DatabaseConnectionExample.getBasicConnection();
            
            // 2. Statement示例
            System.out.println("\n2. Statement使用示例:");
            StatementExample.executeQueries(conn);
            
            // 3. PreparedStatement示例
            System.out.println("\n3. PreparedStatement使用示例:");
            PreparedStatementExample.insertUser(conn, "张三", "zhangsan@example.com", 20);
            PreparedStatementExample.safeQuery(conn, "张三");
            
            // 演示SQL注入防护
            System.out.println("\n4. SQL注入防护演示:");
            System.out.println("正常查询:");
            PreparedStatementExample.safeQuery(conn, "张三");
            
            System.out.println("\n模拟SQL注入攻击:");
            String maliciousInput = "'; DROP TABLE users; --";
            System.out.println("恶意输入: " + maliciousInput);
            System.out.println("使用PreparedStatement安全处理:");
            PreparedStatementExample.safeQuery(conn, maliciousInput);
            
            // 5. ResultSet处理示例
            System.out.println("\n5. ResultSet处理示例:");
            ResultSetExample.processResultSet(conn);
            
            // 6. 事务处理示例
            System.out.println("\n6. 事务处理示例:");
            // 创建测试账户表
            Statement stmt = conn.createStatement();
            stmt.execute("CREATE TABLE IF NOT EXISTS accounts (id INT PRIMARY KEY, balance DECIMAL(10,2))");
            stmt.execute("INSERT IGNORE INTO accounts VALUES (1, 1000.00), (2, 500.00)");
            stmt.close();
            
            TransactionExample.transferMoney(conn, 1, 2, 100.0);
            
            // 7. 批处理示例
            System.out.println("\n7. 批处理示例:");
            BatchProcessingExample.statementBatch(conn);
            BatchProcessingExample.preparedStatementBatch(conn);
            
            // 8. 元数据示例
            System.out.println("\n8. 元数据示例:");
            MetadataExample.showDatabaseMetadata(conn);
            MetadataExample.showResultSetMetadata(conn);
            
            // 9. LOB处理示例
            System.out.println("\n9. LOB数据处理示例:");
            // 创建测试表
            stmt = conn.createStatement();
            stmt.execute("CREATE TABLE IF NOT EXISTS documents (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(100), content LONGBLOB)");
            stmt.execute("CREATE TABLE IF NOT EXISTS articles (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(100), content LONGTEXT)");
            stmt.close();
            
            LOBExample.handleBLOB(conn);
            LOBExample.handleCLOB(conn);
            
            // 关闭连接
            conn.close();
            
            // 10. 连接池示例
            System.out.println("\n10. 连接池示例:");
            SimpleConnectionPool pool = new SimpleConnectionPool(
                "jdbc:mysql://localhost:3306/testdb", "root", "password", 5);
            
            System.out.println("初始可用连接数: " + pool.getAvailableConnections());
            
            Connection pooledConn1 = pool.getConnection();
            System.out.println("获取连接后可用连接数: " + pool.getAvailableConnections());
            
            Connection pooledConn2 = pool.getConnection();
            System.out.println("再次获取连接后可用连接数: " + pool.getAvailableConnections());
            
            pool.releaseConnection(pooledConn1);
            System.out.println("归还连接后可用连接数: " + pool.getAvailableConnections());
            
            pooledConn2.close(); // 这里应该调用releaseConnection，但在简单实现中直接close也可以
            
            // 11. HikariCP示例
            System.out.println("\n11. HikariCP连接池示例:");
            DataSource hikariDS = HikariCPExample.createHikariDataSource();
            HikariCPExample.testHikariCP(hikariDS);
            
            // 12. 综合示例：学生管理系统
            System.out.println("\n12. 综合示例：学生管理系统:");
            StudentManagementSystem sms = new StudentManagementSystem(hikariDS);
            sms.createStudentsTable();
            
            // 添加学生
            sms.addStudent("李四", 19, "lisi@example.com", 85.5);
            sms.addStudent("王五", 21, "wangwu@example.com", 92.0);
            sms.addStudent("赵六", 20, "zhaoliu@example.com", 78.5);
            
            // 查询所有学生
            sms.listAllStudents();
            
            // 查询特定学生
            sms.findStudentById(1);
            
            // 更新学生成绩
            System.out.println("\n更新学生成绩:");
            if (sms.updateStudentGrade(1, 95.0)) {
                System.out.println("更新成功");
                sms.findStudentById(1);
            }
            
            // 统计学生人数
            sms.countStudents();
            
            // 删除学生
            System.out.println("\n删除学生:");
            if (sms.deleteStudent(3)) {
                System.out.println("删除成功");
                sms.countStudents();
            }
            
            System.out.println("\n所有示例执行完毕!");
            
        } catch (Exception e) {
            System.err.println("示例执行出错: " + e.getMessage());
            e.printStackTrace();
        }
    }
}