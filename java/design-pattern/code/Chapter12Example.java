// Chapter12Example.java - 代理模式示例代码

// 抽象主题接口
interface Image {
    void display();
}

// 真实主题类
class RealImage implements Image {
    private String fileName;
    
    public RealImage(String fileName){
        this.fileName = fileName;
        loadFromDisk(fileName);
    }
    
    @Override
    public void display() {
        System.out.println("Displaying " + fileName);
    }
    
    private void loadFromDisk(String fileName){
        System.out.println("Loading " + fileName);
    }
}

// 代理类
class ProxyImage implements Image{
    private RealImage realImage;
    private String fileName;
    
    public ProxyImage(String fileName){
        this.fileName = fileName;
    }
    
    @Override
    public void display() {
        if(realImage == null){
            realImage = new RealImage(fileName);
        }
        realImage.display();
    }
}

// 抽象主题接口
interface Internet {
    void connectTo(String serverHost) throws Exception;
}

// 真实主题类
class RealInternet implements Internet {
    @Override
    public void connectTo(String serverHost) {
        System.out.println("Connecting to " + serverHost);
    }
}

// 保护代理类
class ProxyInternet implements Internet {
    private Internet internet = new RealInternet();
    private static java.util.List<String> bannedSites;
    
    static {
        bannedSites = new java.util.ArrayList<String>();
        bannedSites.add("badsite.com");
        bannedSites.add("restricted.com");
        bannedSites.add("illegal.com");
    }
    
    @Override
    public void connectTo(String serverHost) throws Exception {
        if(bannedSites.contains(serverHost.toLowerCase())) {
            throw new Exception("Access Denied to " + serverHost);
        }
        internet.connectTo(serverHost);
    }
}

// 抽象主题接口
interface DatabaseConnection {
    void executeQuery(String sql);
    void close();
}

// 真实主题类
class RealDatabaseConnection implements DatabaseConnection {
    private String connectionId;
    private boolean closed = false;
    
    public RealDatabaseConnection(String connectionId) {
        this.connectionId = connectionId;
        System.out.println("Creating database connection: " + connectionId);
    }
    
    @Override
    public void executeQuery(String sql) {
        if (closed) {
            System.out.println("Connection is closed, cannot execute query");
            return;
        }
        System.out.println("Executing query on connection " + connectionId + ": " + sql);
    }
    
    @Override
    public void close() {
        if (!closed) {
            System.out.println("Closing database connection: " + connectionId);
            closed = true;
        }
    }
    
    public boolean isClosed() {
        return closed;
    }
}

// 智能引用代理类
class SmartDatabaseProxy implements DatabaseConnection {
    private RealDatabaseConnection realConnection;
    private String connectionId;
    private static int accessCount = 0;
    private static java.util.Map<String, Integer> connectionUsage = new java.util.HashMap<>();
    
    public SmartDatabaseProxy(String connectionId) {
        this.connectionId = connectionId;
        this.realConnection = new RealDatabaseConnection(connectionId);
    }
    
    @Override
    public void executeQuery(String sql) {
        // 记录访问次数
        accessCount++;
        connectionUsage.put(connectionId, connectionUsage.getOrDefault(connectionId, 0) + 1);
        
        System.out.println("Access count: " + accessCount);
        System.out.println("Connection " + connectionId + " usage: " + connectionUsage.get(connectionId));
        
        // 检查是否超过使用限制
        if (connectionUsage.get(connectionId) > 5) {
            System.out.println("Warning: Connection " + connectionId + " has been used more than 5 times");
        }
        
        realConnection.executeQuery(sql);
    }
    
    @Override
    public void close() {
        System.out.println("Closing proxy for connection: " + connectionId);
        realConnection.close();
    }
    
    // 获取统计信息
    public static int getTotalAccessCount() {
        return accessCount;
    }
    
    public static java.util.Map<String, Integer> getConnectionUsage() {
        return new java.util.HashMap<>(connectionUsage);
    }
}

// 数学计算器接口
interface Calculator {
    double add(double a, double b);
    double subtract(double a, double b);
    double multiply(double a, double b);
    double divide(double a, double b);
}

// 真实计算器实现
class RealCalculator implements Calculator {
    @Override
    public double add(double a, double b) {
        System.out.println("Performing addition: " + a + " + " + b);
        return a + b;
    }
    
    @Override
    public double subtract(double a, double b) {
        System.out.println("Performing subtraction: " + a + " - " + b);
        return a - b;
    }
    
    @Override
    public double multiply(double a, double b) {
        System.out.println("Performing multiplication: " + a + " * " + b);
        return a * b;
    }
    
    @Override
    public double divide(double a, double b) {
        System.out.println("Performing division: " + a + " / " + b);
        if (b == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return a / b;
    }
}

// 日志代理计算器
class LoggingCalculatorProxy implements Calculator {
    private RealCalculator calculator;
    private java.util.List<String> log;
    
    public LoggingCalculatorProxy() {
        this.calculator = new RealCalculator();
        this.log = new java.util.ArrayList<>();
    }
    
    @Override
    public double add(double a, double b) {
        String operation = "ADD: " + a + " + " + b;
        log.add(operation);
        System.out.println("[LOG] " + operation);
        return calculator.add(a, b);
    }
    
    @Override
    public double subtract(double a, double b) {
        String operation = "SUBTRACT: " + a + " - " + b;
        log.add(operation);
        System.out.println("[LOG] " + operation);
        return calculator.subtract(a, b);
    }
    
    @Override
    public double multiply(double a, double b) {
        String operation = "MULTIPLY: " + a + " * " + b;
        log.add(operation);
        System.out.println("[LOG] " + operation);
        return calculator.multiply(a, b);
    }
    
    @Override
    public double divide(double a, double b) {
        String operation = "DIVIDE: " + a + " / " + b;
        log.add(operation);
        System.out.println("[LOG] " + operation);
        try {
            return calculator.divide(a, b);
        } catch (ArithmeticException e) {
            log.add("ERROR: " + e.getMessage());
            throw e;
        }
    }
    
    public void printLog() {
        System.out.println("\n=== Calculation Log ===");
        for (String entry : log) {
            System.out.println(entry);
        }
        System.out.println("======================\n");
    }
}

// 主类 - 演示代理模式
public class Chapter12Example {
    public static void main(String[] args) {
        System.out.println("=== 第十二章 代理模式示例 ===\n");
        
        // 示例1: 图片代理
        System.out.println("1. 图片代理示例:");
        Image image = new ProxyImage("test_10mb.jpg");
        
        // 图像将从磁盘加载
        image.display();
        System.out.println("");
        
        // 图像不需要从磁盘加载
        image.display();
        System.out.println();
        
        // 示例2: 互联网保护代理
        System.out.println("2. 互联网保护代理示例:");
        Internet internet = new ProxyInternet();
        
        try {
            internet.connectTo("google.com");
            internet.connectTo("badsite.com");
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
        System.out.println();
        
        // 示例3: 智能引用代理 - 数据库连接
        System.out.println("3. 智能引用代理示例:");
        DatabaseConnection db1 = new SmartDatabaseProxy("DB_CONN_001");
        DatabaseConnection db2 = new SmartDatabaseProxy("DB_CONN_002");
        
        // 多次使用数据库连接
        for (int i = 0; i < 3; i++) {
            db1.executeQuery("SELECT * FROM users WHERE id = " + (i+1));
            db2.executeQuery("SELECT * FROM orders WHERE user_id = " + (i+1));
        }
        
        System.out.println("Total access count: " + SmartDatabaseProxy.getTotalAccessCount());
        System.out.println("Connection usage: " + SmartDatabaseProxy.getConnectionUsage());
        System.out.println();
        
        // 示例4: 日志代理计算器
        System.out.println("4. 日志代理计算器示例:");
        Calculator calc = new LoggingCalculatorProxy();
        
        calc.add(10, 5);
        calc.subtract(20, 8);
        calc.multiply(6, 7);
        try {
            calc.divide(15, 3);
            calc.divide(10, 0); // 这会抛出异常
        } catch (ArithmeticException e) {
            System.out.println("Caught exception: " + e.getMessage());
        }
        
        // 打印日志
        ((LoggingCalculatorProxy) calc).printLog();
    }
}