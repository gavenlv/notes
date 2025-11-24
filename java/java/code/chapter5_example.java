import java.io.*;
import java.util.*;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.sql.SQLException;

/**
 * 第五章：Java异常处理机制 - 完整示例代码
 * 
 * 本文件包含了第五章讨论的所有核心概念和示例代码：
 * 1. 异常基础概念和分类
 * 2. try-catch-finally语法
 * 3. try-with-resources资源管理
 * 4. 自定义异常
 * 5. 异常链
 * 6. 最佳实践示例
 */

// 1. 自定义异常类
// 自定义受检异常
class InsufficientFundsException extends Exception {
    private double amount;
    
    public InsufficientFundsException(double amount) {
        super("账户余额不足，缺少金额：" + amount);
        this.amount = amount;
    }
    
    public double getAmount() {
        return amount;
    }
}

// 自定义非受检异常
class InvalidAccountException extends RuntimeException {
    public InvalidAccountException(String message) {
        super(message);
    }
}

// 带错误码的自定义异常
class BusinessException extends Exception {
    private int errorCode;
    private String errorMessage;
    
    public BusinessException(int errorCode, String errorMessage) {
        super(errorMessage);
        this.errorCode = errorCode;
        this.errorMessage = errorMessage;
    }
    
    public BusinessException(int errorCode, String errorMessage, Throwable cause) {
        super(errorMessage, cause);
        this.errorCode = errorCode;
        this.errorMessage = errorMessage;
    }
    
    public int getErrorCode() {
        return errorCode;
    }
    
    public String getErrorMessage() {
        return errorMessage;
    }
    
    @Override
    public String toString() {
        return "BusinessException{" +
                "errorCode=" + errorCode +
                ", errorMessage='" + errorMessage + '\'' +
                '}';
    }
}

// 数据处理异常
class DataProcessingException extends Exception {
    public DataProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}

// 数据库异常
class DatabaseException extends Exception {
    public DatabaseException(String message, Throwable cause) {
        super(message, cause);
    }
}

// 2. 实现AutoCloseable接口的自定义资源
class CustomResource implements AutoCloseable {
    private String name;
    
    public CustomResource(String name) {
        this.name = name;
        System.out.println(name + " 资源已打开");
    }
    
    public void doSomething() {
        System.out.println(name + " 正在执行操作");
    }
    
    @Override
    public void close() throws Exception {
        System.out.println(name + " 资源已关闭");
    }
}

// 有序关闭资源示例
class OrderedResource implements AutoCloseable {
    private String name;
    
    public OrderedResource(String name) {
        this.name = name;
        System.out.println(name + " 已打开");
    }
    
    @Override
    public void close() throws Exception {
        System.out.println(name + " 已关闭");
    }
}

// 3. 银行账户类（用于演示自定义异常）
class BankAccount {
    private String accountNumber;
    private double balance;
    
    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }
    
    // 存款
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new InvalidAccountException("存款金额必须大于0");
        }
        balance += amount;
        System.out.println("存款成功，当前余额：" + balance);
    }
    
    // 取款
    public void withdraw(double amount) throws InsufficientFundsException {
        if (amount <= 0) {
            throw new InvalidAccountException("取款金额必须大于0");
        }
        if (amount > balance) {
            throw new InsufficientFundsException(amount - balance);
        }
        balance -= amount;
        System.out.println("取款成功，当前余额：" + balance);
    }
    
    public double getBalance() {
        return balance;
    }
    
    public String getAccountNumber() {
        return accountNumber;
    }
}

// 用户服务类（用于演示带错误码的异常）
class UserService {
    public void registerUser(String username, String email) throws BusinessException {
        if (username == null || username.trim().isEmpty()) {
            throw new BusinessException(1001, "用户名不能为空");
        }
        
        if (email == null || !email.contains("@")) {
            throw new BusinessException(1002, "邮箱格式不正确");
        }
        
        if (username.length() < 3) {
            throw new BusinessException(1003, "用户名长度不能少于3位", 
                new IllegalArgumentException("用户名太短"));
        }
        
        System.out.println("用户注册成功：" + username);
    }
}

// 数据处理器（用于演示异常链）
class DataProcessor {
    public void processData(String fileName) throws DataProcessingException {
        try {
            readDataFromFile(fileName);
        } catch (IOException e) {
            // 将IOException包装在DataProcessingException中
            throw new DataProcessingException("处理数据文件时发生错误：" + fileName, e);
        }
    }
    
    private void readDataFromFile(String fileName) throws IOException {
        try (FileReader file = new FileReader(fileName);
             BufferedReader reader = new BufferedReader(file)) {
            String line = reader.readLine();
            saveToDatabase(line);
        } catch (FileNotFoundException e) {
            throw new IOException("找不到数据文件：" + fileName, e);
        }
    }
    
    private void saveToDatabase(String data) throws IOException {
        try {
            // 模拟数据库操作
            if (data == null) {
                throw new SQLException("数据为空");
            }
            System.out.println("数据保存成功：" + data);
        } catch (SQLException e) {
            throw new IOException("数据库操作失败", e);
        }
    }
}

// 最佳实践示例类
class ExceptionBestPractices {
    private static final Logger logger = Logger.getLogger(ExceptionBestPractices.class.getName());
    
    // 1. 使用具体的异常类型
    public static void specificExceptionExample() {
        System.out.println("=== 使用具体异常类型 ===");
        try {
            int[] arr = new int[5];
            arr[10] = 100; // 应该抛出ArrayIndexOutOfBoundsException
        } catch (ArrayIndexOutOfBoundsException e) {
            // 好的做法：捕获具体的异常类型
            System.out.println("数组越界异常：" + e.getMessage());
        }
    }
    
    // 2. 不要忽略异常
    public static void dontIgnoreExceptions() {
        System.out.println("\n=== 不要忽略异常 ===");
        
        try {
            // 模拟可能抛出异常的操作
            throw new IOException("模拟IO异常");
        } catch (IOException e) {
            // 至少记录日志
            logger.log(Level.WARNING, "IO操作失败", e);
            // 或者重新抛出异常
            // throw new RuntimeException("操作失败", e);
        }
    }
    
    // 3. 保持异常信息的完整性
    public static void preserveExceptionInfo() throws RuntimeException {
        System.out.println("\n=== 保持异常信息完整性 ===");
        
        try {
            // 模拟底层操作
            throw new FileNotFoundException("配置文件不存在");
        } catch (FileNotFoundException e) {
            // 好的做法：保留原始异常信息
            throw new RuntimeException("初始化配置失败", e);
        }
    }
    
    // 4. 合理使用受检异常和非受检异常
    public static void appropriateExceptionTypes() {
        System.out.println("\n=== 合理使用异常类型 ===");
        
        // 受检异常适用于调用者必须处理的情况
        try {
            readFileContent("config.txt");
        } catch (IOException e) {
            System.out.println("必须处理的IO异常：" + e.getMessage());
        }
        
        // 非受检异常适用于编程错误
        validateAge(-5); // 不需要强制处理，但应该修正代码
    }
    
    // 可能发生预期错误的方法（使用受检异常）
    public static String readFileContent(String fileName) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
            return reader.readLine();
        }
    }
    
    // 参数验证方法（使用非受检异常）
    public static void validateAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("年龄不能为负数：" + age);
        }
        if (age > 150) {
            throw new IllegalArgumentException("年龄不能超过150：" + age);
        }
        System.out.println("年龄验证通过：" + age);
    }
    
    // 5. 提供有意义的异常信息
    public static void meaningfulExceptionMessages() {
        System.out.println("\n=== 提供有意义的异常信息 ===");
        
        String userName = "";
        if (userName == null || userName.trim().isEmpty()) {
            // 好的做法：提供清晰的错误信息
            throw new IllegalArgumentException("用户名不能为空，请提供有效的用户名");
        }
    }
    
    // 6. 异常处理与资源清理
    public static void exceptionAndResourceCleanup() {
        System.out.println("\n=== 异常处理与资源清理 ===");
        
        // 使用try-with-resources确保资源清理
        try (FileInputStream fis = new FileInputStream("example.txt");
             BufferedInputStream bis = new BufferedInputStream(fis)) {
            // 处理文件
            System.out.println("文件处理完成");
        } catch (IOException e) {
            System.out.println("文件处理异常：" + e.getMessage());
            // 资源会自动清理，无需手动关闭
        }
    }
}

// 日志记录与异常处理示例
class LoggingWithExceptions {
    private static final Logger logger = Logger.getLogger(LoggingWithExceptions.class.getName());
    
    // 记录异常但不中断程序执行
    public static void logAndContinue() {
        try {
            // 模拟可能失败的操作
            throw new IOException("网络连接超时");
        } catch (IOException e) {
            // 记录警告级别的日志
            logger.log(Level.WARNING, "网络操作失败，使用默认值继续执行", e);
            // 继续执行其他逻辑
            System.out.println("使用缓存数据继续执行...");
        }
    }
    
    // 记录异常并重新抛出
    public static void logAndRethrow() throws IOException {
        try {
            // 模拟关键操作
            throw new IOException("数据库连接失败");
        } catch (IOException e) {
            // 记录严重错误级别的日志
            logger.log(Level.SEVERE, "关键操作失败，无法继续执行", e);
            // 重新抛出异常
            throw e;
        }
    }
    
    // 包装异常并记录
    public static void wrapAndLog() {
        try {
            // 模拟底层操作
            throw new IOException("文件损坏");
        } catch (IOException e) {
            // 记录原始异常
            logger.log(Level.FINE, "底层操作失败", e);
            // 包装为业务异常并记录
            RuntimeException businessException = new RuntimeException("数据处理失败", e);
            logger.log(Level.WARNING, "转换为业务异常", businessException);
            throw businessException;
        }
    }
}

// 异常处理陷阱示例
class ExceptionInLoopTrap {
    // 不好的做法：在循环内部捕获异常
    public static void badPractice() {
        System.out.println("=== 循环中捕获异常（不好做法）===");
        List<String> numbers = Arrays.asList("1", "2", "abc", "4", "5.5");
        
        int sum = 0;
        for (String str : numbers) {
            try {
                int num = Integer.parseInt(str);
                sum += num;
            } catch (NumberFormatException e) {
                System.out.println("跳过无效数字：" + str);
                // 继续处理下一个元素
            }
        }
        System.out.println("总和：" + sum);
    }
    
    // 更好的做法：将异常处理移到循环外部
    public static void betterPractice() {
        System.out.println("\n=== 循环中捕获异常（更好做法）===");
        List<String> validNumbers = Arrays.asList("1", "2", "4", "5");
        List<String> invalidNumbers = Arrays.asList("abc", "def");
        
        // 处理有效数字
        int sum = 0;
        for (String str : validNumbers) {
            int num = Integer.parseInt(str); // 不需要try-catch
            sum += num;
        }
        System.out.println("有效数字总和：" + sum);
        
        // 单独处理无效数字的情况
        try {
            for (String str : invalidNumbers) {
                int num = Integer.parseInt(str); // 会在第一个无效数字处抛出异常
                sum += num;
            }
        } catch (NumberFormatException e) {
            System.out.println("发现无效数字，停止处理：" + e.getMessage());
        }
    }
}

class ExceptionPerformanceTrap {
    // 不好的做法：使用异常控制程序流程
    public static int badPractice(String str) {
        try {
            return Integer.parseInt(str);
        } catch (NumberFormatException e) {
            return 0; // 使用异常处理默认值
        }
    }
    
    // 更好的做法：预先检查条件
    public static int betterPractice(String str) {
        if (str == null || str.isEmpty()) {
            return 0;
        }
        
        // 检查是否为有效数字
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            if (i == 0 && c == '-') {
                continue; // 允许负号
            }
            if (!Character.isDigit(c)) {
                return 0; // 不是数字字符
            }
        }
        
        try {
            return Integer.parseInt(str);
        } catch (NumberFormatException e) {
            return 0;
        }
    }
}

// 资源泄露问题示例
class ResourceLeakTrap {
    // 更好的做法：使用try-with-resources
    public static void betterPractice() {
        System.out.println("\n=== 使用try-with-resources避免资源泄露 ===");
        try (FileInputStream fis = new FileInputStream("example.txt")) {
            // 处理文件...
            System.out.println("文件处理完成");
            // 即使抛出异常，资源也会自动关闭
        } catch (FileNotFoundException e) {
            System.out.println("文件未找到：" + e.getMessage());
        } catch (IOException e) {
            System.out.println("IO异常：" + e.getMessage());
        }
        // 资源已经自动关闭
        System.out.println("资源已自动清理");
    }
}

// 主类 - 包含所有示例的测试方法
public class Chapter5Example {
    public static void main(String[] args) {
        System.out.println("第五章：Java异常处理机制 - 完整示例代码");
        System.out.println("========================================");
        
        // 1. 自定义异常示例
        customExceptionExample();
        
        // 2. try-with-resources示例
        tryWithResourcesExample();
        
        // 3. 异常链示例
        exceptionChainingExample();
        
        // 4. 最佳实践示例
        bestPracticesExample();
        
        // 5. 日志记录与异常示例
        loggingWithExceptionsExample();
        
        // 6. 异常处理陷阱示例
        exceptionTrapsExample();
        
        // 清理测试文件
        cleanup();
    }
    
    // 自定义异常示例
    public static void customExceptionExample() {
        System.out.println("\n--- 自定义异常示例 ---");
        
        BankAccount account = new BankAccount("123456", 1000.0);
        
        try {
            // 正常操作
            account.deposit(500);
            account.withdraw(200);
            
            // 异常操作
            account.deposit(-100); // 抛出InvalidAccountException
        } catch (InvalidAccountException e) {
            System.out.println("无效账户操作：" + e.getMessage());
        }
        
        try {
            // 余额不足
            account.withdraw(2000); // 抛出InsufficientFundsException
        } catch (InsufficientFundsException e) {
            System.out.println("资金不足：" + e.getMessage());
            System.out.println("缺少金额：" + e.getAmount());
        }
        
        UserService userService = new UserService();
        
        try {
            userService.registerUser("", "test@example.com");
        } catch (BusinessException e) {
            System.out.println("业务异常：" + e);
            System.out.println("错误码：" + e.getErrorCode());
            System.out.println("错误信息：" + e.getErrorMessage());
        }
        
        try {
            userService.registerUser("ab", "test@example.com");
        } catch (BusinessException e) {
            System.out.println("业务异常：" + e);
            System.out.println("错误码：" + e.getErrorCode());
            System.out.println("错误信息：" + e.getErrorMessage());
            System.out.println("原因：" + e.getCause().getMessage());
        }
    }
    
    // try-with-resources示例
    public static void tryWithResourcesExample() {
        System.out.println("\n--- try-with-resources示例 ---");
        
        // 基本用法
        System.out.println("=== 基本用法 ===");
        try (CustomResource resource = new CustomResource("Resource1")) {
            resource.doSomething();
        } catch (Exception e) {
            System.out.println("发生异常：" + e.getMessage());
        }
        
        // 多个资源
        System.out.println("\n=== 多个资源 ===");
        try (CustomResource resource1 = new CustomResource("Resource1");
             CustomResource resource2 = new CustomResource("Resource2");
             CustomResource resource3 = new CustomResource("Resource3")) {
            resource1.doSomething();
            resource2.doSomething();
            resource3.doSomething();
        } catch (Exception e) {
            System.out.println("发生异常：" + e.getMessage());
        }
        
        // 文件操作示例
        System.out.println("\n=== 文件操作示例 ===");
        
        // 创建测试文件
        try (PrintWriter writer = new PrintWriter("example.txt")) {
            writer.println("Hello, World!");
            writer.println("这是第二行");
            System.out.println("文件写入成功");
        } catch (IOException e) {
            System.out.println("写入文件时出错：" + e.getMessage());
        }
        
        // 读取文件
        try (FileReader reader = new FileReader("example.txt");
             BufferedReader bufferedReader = new BufferedReader(reader)) {
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                System.out.println("读取到：" + line);
            }
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
        
        // 资源关闭顺序演示
        System.out.println("\n=== 资源关闭顺序演示 ===");
        try (OrderedResource r1 = new OrderedResource("Resource1");
             OrderedResource r2 = new OrderedResource("Resource2");
             OrderedResource r3 = new OrderedResource("Resource3")) {
            System.out.println("在try块中执行操作");
        } catch (Exception e) {
            System.out.println("发生异常：" + e.getMessage());
        }
        System.out.println("try-with-resources块结束");
    }
    
    // 异常链示例
    public static void exceptionChainingExample() {
        System.out.println("\n--- 异常链示例 ---");
        
        // 创建测试数据文件
        try (PrintWriter writer = new PrintWriter("data.txt")) {
            writer.println("测试数据");
        } catch (IOException e) {
            System.out.println("创建测试文件时出错：" + e.getMessage());
        }
        
        DataProcessor processor = new DataProcessor();
        
        try {
            processor.processData("data.txt");
        } catch (DataProcessingException e) {
            System.out.println("数据处理异常：" + e.getMessage());
            
            // 打印异常链
            Throwable cause = e.getCause();
            while (cause != null) {
                System.out.println("引起的原因：" + cause.getClass().getSimpleName() + 
                                 " - " + cause.getMessage());
                cause = cause.getCause();
            }
            
            // 打印完整的堆栈跟踪
            System.out.println("\n完整堆栈跟踪：");
            e.printStackTrace();
        }
    }
    
    // 最佳实践示例
    public static void bestPracticesExample() {
        System.out.println("\n--- 最佳实践示例 ---");
        
        ExceptionBestPractices.specificExceptionExample();
        ExceptionBestPractices.dontIgnoreExceptions();
        try {
            ExceptionBestPractices.preserveExceptionInfo();
        } catch (RuntimeException e) {
            System.out.println("包装后的异常：" + e.getMessage());
            System.out.println("原始异常：" + e.getCause().getMessage());
        }
        ExceptionBestPractices.appropriateExceptionTypes();
        ExceptionBestPractices.meaningfulExceptionMessages();
        ExceptionBestPractices.exceptionAndResourceCleanup();
    }
    
    // 日志记录与异常示例
    public static void loggingWithExceptionsExample() {
        System.out.println("\n--- 日志记录与异常示例 ---");
        
        LoggingWithExceptions.logAndContinue();
        
        try {
            LoggingWithExceptions.logAndRethrow();
        } catch (IOException e) {
            System.out.println("重新抛出的异常：" + e.getMessage());
        }
        
        try {
            LoggingWithExceptions.wrapAndLog();
        } catch (RuntimeException e) {
            System.out.println("包装后的异常：" + e.getMessage());
        }
    }
    
    // 异常处理陷阱示例
    public static void exceptionTrapsExample() {
        System.out.println("\n--- 异常处理陷阱示例 ---");
        
        ExceptionInLoopTrap.badPractice();
        ExceptionInLoopTrap.betterPractice();
        
        System.out.println("\n=== 异常处理性能对比 ===");
        
        // 测试正常情况
        System.out.println("正常情况 - 不好的做法：" + ExceptionPerformanceTrap.badPractice("123"));
        System.out.println("正常情况 - 更好做法：" + ExceptionPerformanceTrap.betterPractice("123"));
        
        // 测试异常情况
        System.out.println("异常情况 - 不好的做法：" + ExceptionPerformanceTrap.badPractice("abc"));
        System.out.println("异常情况 - 更好做法：" + ExceptionPerformanceTrap.betterPractice("abc"));
        
        ResourceLeakTrap.betterPractice();
    }
    
    // 清理测试文件
    public static void cleanup() {
        System.out.println("\n--- 清理测试文件 ---");
        try {
            new File("example.txt").delete();
            new File("data.txt").delete();
            System.out.println("测试文件已清理");
        } catch (Exception e) {
            System.out.println("清理文件时出错：" + e.getMessage());
        }
    }
}