# 第5章 Java异常处理机制

## 目录
1. [异常处理概述](#1异常处理概述)
2. [异常的分类](#2异常的分类)
3. [异常处理语法](#3异常处理语法)
4. [自定义异常](#4自定义异常)
5. [异常链](#5异常链)
6. [try-with-resources语句](#6try-with-resources语句)
7. [最佳实践](#7最佳实践)
8. [常见陷阱](#8常见陷阱)
9. [总结](#9总结)

---

## 1.异常处理概述

### 1.1 什么是异常

异常是在程序执行过程中发生的不正常情况，它会中断程序的正常执行流程。Java通过异常处理机制来处理这些运行时错误，使程序能够优雅地处理错误情况而不至于崩溃。

### 1.2 传统错误处理方式的问题

在没有异常处理机制之前，程序员通常采用以下方式处理错误：

```java
// 传统的错误处理方式
int divide(int a, int b) {
    if (b == 0) {
        return -1; // 使用特殊返回值表示错误
    }
    return a / b;
}

// 调用代码需要检查返回值
int result = divide(10, 0);
if (result == -1) {
    System.out.println("除法运算出错");
} else {
    System.out.println("结果：" + result);
}
```

这种方式存在以下问题：
1. **返回值污染**：正常的返回值范围被错误标识占用
2. **错误处理分散**：每个调用都需要检查返回值
3. **难以维护**：错误处理代码与业务逻辑混合

### 1.3 异常处理的优势

Java的异常处理机制解决了上述问题：

```java
// 使用异常处理机制
public static int divide(int a, int b) throws ArithmeticException {
    if (b == 0) {
        throw new ArithmeticException("除数不能为零");
    }
    return a / b;
}

// 调用代码可以选择性处理异常
public static void main(String[] args) {
    try {
        int result = divide(10, 0);
        System.out.println("结果：" + result);
    } catch (ArithmeticException e) {
        System.out.println("发生异常：" + e.getMessage());
    }
}
```

异常处理的优势：
1. **分离错误处理与正常逻辑**
2. **向上冒泡传播异常**
3. **提供详细的错误信息**
4. **支持异常分类和处理**

---

## 2.异常的分类

### 2.1 Throwable类层次结构

Java中所有的异常和错误都继承自`Throwable`类：

```
Throwable
├── Error
│   ├── VirtualMachineError
│   │   ├── OutOfMemoryError
│   │   └── StackOverflowError
│   ├── LinkageError
│   └── IOError
└── Exception
    ├── RuntimeException
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   ├── IndexOutOfBoundsException
    │   └── ArithmeticException
    └── 其他受检异常
        ├── IOException
        ├── SQLException
        └── ClassNotFoundException
```

### 2.2 受检异常（Checked Exceptions）

受检异常是指在编译时必须处理的异常，要么使用try-catch捕获，要么使用throws声明抛出。

```java
import java.io.*;

public class CheckedExceptionExample {
    // 方法声明抛出受检异常
    public static void readFile(String fileName) throws IOException {
        FileReader file = new FileReader(fileName);
        BufferedReader reader = new BufferedReader(file);
        System.out.println(reader.readLine());
        reader.close();
    }
    
    public static void main(String[] args) {
        try {
            // 必须处理IOException
            readFile("nonexistent.txt");
        } catch (IOException e) {
            System.out.println("文件读取异常：" + e.getMessage());
        }
    }
}
```

### 2.3 非受检异常（Unchecked Exceptions）

非受检异常是指运行时异常（RuntimeException及其子类），编译器不要求强制处理。

```java
public class UncheckedExceptionExample {
    // 不需要声明throws
    public static int divide(int a, int b) {
        return a / b; // 可能抛出ArithmeticException
    }
    
    public static void main(String[] args) {
        try {
            int result = divide(10, 0);
            System.out.println("结果：" + result);
        } catch (ArithmeticException e) {
            System.out.println("算术异常：" + e.getMessage());
        }
        
        // NullPointerException示例
        String str = null;
        try {
            int length = str.length(); // 抛出NullPointerException
        } catch (NullPointerException e) {
            System.out.println("空指针异常：" + e.getMessage());
        }
    }
}
```

### 2.4 错误（Errors）

错误表示JVM系统级的错误或资源耗尽的情况，应用程序通常不应该捕获这些错误。

```java
public class ErrorExample {
    // StackOverflowError示例
    public static void recursiveMethod() {
        recursiveMethod(); // 无限递归导致栈溢出
    }
    
    // OutOfMemoryError示例
    public static void memoryError() {
        // 创建大量对象导致内存溢出
        List<byte[]> list = new ArrayList<>();
        while (true) {
            list.add(new byte[1024 * 1024]); // 每次添加1MB数据
        }
    }
    
    public static void main(String[] args) {
        // 注意：运行这些方法会导致程序崩溃
        // recursiveMethod();
        // memoryError();
    }
}
```

---

## 3.异常处理语法

### 3.1 try-catch语句

try-catch语句用于捕获和处理异常。

```java
public class TryCatchExample {
    public static void main(String[] args) {
        // 基本的try-catch
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            System.out.println("捕获到算术异常：" + e.getMessage());
        }
        
        // 多重catch块
        try {
            String str = null;
            int length = str.length(); // NullPointerException
        } catch (NullPointerException e) {
            System.out.println("空指针异常：" + e.getMessage());
        } catch (RuntimeException e) {
            System.out.println("运行时异常：" + e.getMessage());
        }
        
        // 多异常类型捕获（Java 7+）
        try {
            int[] arr = new int[5];
            arr[10] = 100; // ArrayIndexOutOfBoundsException
            String str = null;
            str.length(); // NullPointerException
        } catch (ArrayIndexOutOfBoundsException | NullPointerException e) {
            System.out.println("数组越界或空指针异常：" + e.getMessage());
        }
    }
}
```

### 3.2 finally块

finally块总是会执行，无论是否发生异常。

```java
import java.io.*;

public class FinallyExample {
    public static void readFile(String fileName) {
        FileReader file = null;
        try {
            file = new FileReader(fileName);
            BufferedReader reader = new BufferedReader(file);
            System.out.println(reader.readLine());
        } catch (IOException e) {
            System.out.println("文件读取异常：" + e.getMessage());
        } finally {
            // 清理资源
            if (file != null) {
                try {
                    file.close();
                    System.out.println("文件已关闭");
                } catch (IOException e) {
                    System.out.println("关闭文件时出错：" + e.getMessage());
                }
            }
        }
    }
    
    public static void main(String[] args) {
        readFile("test.txt");
    }
}
```

### 3.3 try-with-resources语句

try-with-resources是Java 7引入的语法，用于自动管理资源。

```java
import java.io.*;

public class TryWithResourcesExample {
    // 传统方式
    public static void readFileOldWay(String fileName) {
        FileReader file = null;
        try {
            file = new FileReader(fileName);
            BufferedReader reader = new BufferedReader(file);
            System.out.println(reader.readLine());
        } catch (IOException e) {
            System.out.println("文件读取异常：" + e.getMessage());
        } finally {
            if (file != null) {
                try {
                    file.close();
                } catch (IOException e) {
                    System.out.println("关闭文件时出错：" + e.getMessage());
                }
            }
        }
    }
    
    // try-with-resources方式
    public static void readFileNewWay(String fileName) {
        try (FileReader file = new FileReader(fileName);
             BufferedReader reader = new BufferedReader(file)) {
            System.out.println(reader.readLine());
        } catch (IOException e) {
            System.out.println("文件读取异常：" + e.getMessage());
        }
        // 资源会自动关闭，无需手动处理
    }
    
    public static void main(String[] args) {
        // 创建测试文件
        try (PrintWriter writer = new PrintWriter("test.txt")) {
            writer.println("Hello, World!");
        } catch (IOException e) {
            System.out.println("创建文件时出错：" + e.getMessage());
        }
        
        System.out.println("传统方式读取文件：");
        readFileOldWay("test.txt");
        
        System.out.println("try-with-resources方式读取文件：");
        readFileNewWay("test.txt");
    }
}
```

### 3.4 throws声明

throws关键字用于声明方法可能抛出的异常。

```java
import java.io.*;

public class ThrowsExample {
    // 声明抛出单个异常
    public static void readFile(String fileName) throws IOException {
        FileReader file = new FileReader(fileName);
        BufferedReader reader = new BufferedReader(file);
        System.out.println(reader.readLine());
        reader.close();
    }
    
    // 声明抛出多个异常
    public static void processFile(String fileName) throws IOException, IllegalArgumentException {
        if (fileName == null || fileName.isEmpty()) {
            throw new IllegalArgumentException("文件名不能为空");
        }
        FileReader file = new FileReader(fileName);
        BufferedReader reader = new BufferedReader(file);
        System.out.println(reader.readLine());
        reader.close();
    }
    
    // 声明抛出异常的父类
    public static void handleFile(String fileName) throws Exception {
        if (fileName == null || fileName.isEmpty()) {
            throw new IllegalArgumentException("文件名不能为空");
        }
        FileReader file = new FileReader(fileName);
        BufferedReader reader = new BufferedReader(file);
        System.out.println(reader.readLine());
        reader.close();
    }
    
    public static void main(String[] args) {
        try {
            readFile("test.txt");
            processFile("");
            handleFile("test.txt");
        } catch (IllegalArgumentException e) {
            System.out.println("非法参数异常：" + e.getMessage());
        } catch (IOException e) {
            System.out.println("IO异常：" + e.getMessage());
        } catch (Exception e) {
            System.out.println("其他异常：" + e.getMessage());
        }
    }
}
```

---

## 4.自定义异常

### 4.1 创建自定义异常类

通过继承Exception或RuntimeException创建自定义异常。

```java
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

// 银行账户类
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

public class CustomExceptionExample {
    public static void main(String[] args) {
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
    }
}
```

### 4.2 带有错误码的自定义异常

```java
// 带有错误码的自定义异常
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

// 业务服务类
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

public class ErrorCodeExceptionExample {
    public static void main(String[] args) {
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
}
```

---

## 5.异常链

异常链允许将一个异常包装在另一个异常中，保留原始异常的信息。

```java
import java.io.*;

class DataProcessingException extends Exception {
    public DataProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}

class DatabaseException extends Exception {
    public DatabaseException(String message, Throwable cause) {
        super(message, cause);
    }
}

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

public class ExceptionChainingExample {
    public static void main(String[] args) {
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
}
```

---

## 6.try-with-resources语句

### 6.1 基本用法

try-with-resources语句确保每个资源在语句结束时自动关闭。

```java
import java.io.*;
import java.sql.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class TryWithResourcesDetailedExample {
    // 实现AutoCloseable接口的自定义资源
    static class CustomResource implements AutoCloseable {
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
    
    // 基本用法
    public static void basicUsage() {
        System.out.println("=== 基本用法 ===");
        try (CustomResource resource = new CustomResource("Resource1")) {
            resource.doSomething();
        } catch (Exception e) {
            System.out.println("发生异常：" + e.getMessage());
        }
    }
    
    // 多个资源
    public static void multipleResources() {
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
    }
    
    // 文件操作示例
    public static void fileOperations() {
        System.out.println("\n=== 文件操作示例 ===");
        
        // 写入文件
        try (FileWriter writer = new FileWriter("example.txt");
             PrintWriter printWriter = new PrintWriter(writer)) {
            printWriter.println("Hello, World!");
            printWriter.println("这是第二行");
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
    }
    
    // 压缩文件示例
    public static void zipFileExample() {
        System.out.println("\n=== 压缩文件示例 ===");
        
        try (FileOutputStream fos = new FileOutputStream("example.zip");
             ZipOutputStream zos = new ZipOutputStream(fos);
             FileInputStream fis = new FileInputStream("example.txt")) {
            
            ZipEntry zipEntry = new ZipEntry("example.txt");
            zos.putNextEntry(zipEntry);
            
            byte[] buffer = new byte[1024];
            int length;
            while ((length = fis.read(buffer)) > 0) {
                zos.write(buffer, 0, length);
            }
            
            zos.closeEntry();
            System.out.println("文件压缩成功");
        } catch (IOException e) {
            System.out.println("压缩文件时出错：" + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        basicUsage();
        multipleResources();
        fileOperations();
        zipFileExample();
        
        // 清理测试文件
        try {
            new File("example.txt").delete();
            new File("example.zip").delete();
        } catch (Exception e) {
            // 忽略清理错误
        }
    }
}
```

### 6.2 资源关闭顺序

try-with-resources语句按照资源声明的相反顺序关闭资源。

```java
import java.io.*;

public class ResourceClosingOrderExample {
    static class OrderedResource implements AutoCloseable {
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
    
    public static void main(String[] args) {
        System.out.println("资源关闭顺序演示：");
        try (OrderedResource r1 = new OrderedResource("Resource1");
             OrderedResource r2 = new OrderedResource("Resource2");
             OrderedResource r3 = new OrderedResource("Resource3")) {
            System.out.println("在try块中执行操作");
        } catch (Exception e) {
            System.out.println("发生异常：" + e.getMessage());
        }
        System.out.println("try-with-resources块结束");
    }
}
```

---

## 7.最佳实践

### 7.1 异常处理原则

```java
import java.io.*;
import java.util.logging.Logger;
import java.util.logging.Level;

public class ExceptionBestPractices {
    private static final Logger logger = Logger.getLogger(ExceptionBestPractices.class.getName());
    
    // 1. 优先使用具体的异常类型
    public static void specificExceptionExample() {
        System.out.println("=== 使用具体异常类型 ===");
        try {
            int[] arr = new int[5];
            arr[10] = 100; // 应该抛出ArrayIndexOutOfBoundsException
        } catch (ArrayIndexOutOfBoundsException e) {
            // 好的做法：捕获具体的异常类型
            System.out.println("数组越界异常：" + e.getMessage());
        }
        
        // 避免这样做：
        /*
        try {
            int[] arr = new int[5];
            arr[10] = 100;
        } catch (Exception e) {
            // 不好的做法：捕获过于宽泛的异常类型
            System.out.println("发生了某种异常：" + e.getMessage());
        }
        */
    }
    
    // 2. 不要忽略异常
    public static void dontIgnoreExceptions() {
        System.out.println("\n=== 不要忽略异常 ===");
        
        // 不好的做法：
        /*
        try {
            // 一些可能抛出异常的操作
        } catch (Exception e) {
            // 空的catch块，忽略了异常
        }
        */
        
        // 好的做法：
        try {
            // 一些可能抛出异常的操作
            throw new IOException("模拟IO异常");
        } catch (IOException e) {
            // 至少记录日志
            logger.log(Level.WARNING, "IO操作失败", e);
            // 或者重新抛出异常
            // throw new RuntimeException("操作失败", e);
        }
    }
    
    // 3. 保持异常信息的完整性
    public static void preserveExceptionInfo() {
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
    
    public static void main(String[] args) {
        specificExceptionExample();
        dontIgnoreExceptions();
        try {
            preserveExceptionInfo();
        } catch (RuntimeException e) {
            System.out.println("包装后的异常：" + e.getMessage());
            System.out.println("原始异常：" + e.getCause().getMessage());
        }
        appropriateExceptionTypes();
        meaningfulExceptionMessages();
        exceptionAndResourceCleanup();
    }
}
```

### 7.2 日志记录与异常

```java
import java.util.logging.Logger;
import java.util.logging.Level;
import java.io.IOException;

public class LoggingWithExceptions {
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
    
    public static void main(String[] args) {
        System.out.println("=== 日志记录与异常处理 ===");
        logAndContinue();
        
        try {
            logAndRethrow();
        } catch (IOException e) {
            System.out.println("重新抛出的异常：" + e.getMessage());
        }
        
        try {
            wrapAndLog();
        } catch (RuntimeException e) {
            System.out.println("包装后的异常：" + e.getMessage());
        }
    }
}
```

---

## 8.常见陷阱

### 8.1 在循环中捕获异常

```java
import java.util.*;

public class ExceptionInLoopTrap {
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
    
    public static void main(String[] args) {
        badPractice();
        betterPractice();
    }
}
```

### 8.2 异常处理影响性能

```java
public class ExceptionPerformanceTrap {
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
    
    public static void main(String[] args) {
        System.out.println("=== 异常处理性能对比 ===");
        
        // 测试正常情况
        System.out.println("正常情况 - 不好的做法：" + badPractice("123"));
        System.out.println("正常情况 - 更好做法：" + betterPractice("123"));
        
        // 测试异常情况
        System.out.println("异常情况 - 不好的做法：" + badPractice("abc"));
        System.out.println("异常情况 - 更好做法：" + betterPractice("abc"));
    }
}
```

### 8.3 资源泄露问题

```java
import java.io.*;

public class ResourceLeakTrap {
    // 不好的做法：可能导致资源泄露
    public static void badPractice() {
        System.out.println("=== 可能导致资源泄露的做法 ===");
        FileInputStream fis = null;
        try {
            fis = new FileInputStream("example.txt");
            // 处理文件...
            throw new RuntimeException("模拟异常"); // 这会导致finally不执行
        } catch (FileNotFoundException e) {
            System.out.println("文件未找到：" + e.getMessage());
        } finally {
            // 如果上面抛出了RuntimeException，这里的代码可能不会执行
            if (fis != null) {
                try {
                    fis.close();
                    System.out.println("文件已关闭");
                } catch (IOException e) {
                    System.out.println("关闭文件时出错：" + e.getMessage());
                }
            }
        }
    }
    
    // 更好的做法：使用try-with-resources
    public static void betterPractice() {
        System.out.println("\n=== 使用try-with-resources避免资源泄露 ===");
        try (FileInputStream fis = new FileInputStream("example.txt")) {
            // 处理文件...
            throw new RuntimeException("模拟异常");
            // 即使抛出异常，资源也会自动关闭
        } catch (FileNotFoundException e) {
            System.out.println("文件未找到：" + e.getMessage());
        } catch (IOException e) {
            System.out.println("IO异常：" + e.getMessage());
        }
        // 资源已经自动关闭
        System.out.println("资源已自动清理");
    }
    
    public static void main(String[] args) {
        // 创建测试文件
        try (PrintWriter writer = new PrintWriter("example.txt")) {
            writer.println("Test content");
        } catch (IOException e) {
            System.out.println("创建测试文件时出错：" + e.getMessage());
        }
        
        // badPractice(); // 这个方法会导致问题，所以注释掉
        betterPractice();
        
        // 清理测试文件
        new File("example.txt").delete();
    }
}
```

---

## 9.总结

### 9.1 核心要点回顾

1. **异常分类**：
   - Throwable是所有异常和错误的基类
   - Error表示系统级错误，不应被捕获
   - Exception分为受检异常和非受检异常
   - 受检异常必须处理，非受检异常通常是编程错误

2. **异常处理语法**：
   - try-catch-finally用于捕获和处理异常
   - try-with-resources用于自动资源管理
   - throws用于声明方法可能抛出的异常

3. **自定义异常**：
   - 继承Exception创建受检异常
   - 继承RuntimeException创建非受检异常
   - 可以添加错误码和额外信息

4. **异常链**：
   - 通过构造函数传递cause参数建立异常链
   - 保留原始异常信息便于调试

### 9.2 最佳实践总结

1. **使用具体的异常类型**：避免捕获过于宽泛的Exception
2. **不要忽略异常**：至少记录日志
3. **保持异常信息完整性**：使用异常链保留原始信息
4. **合理选择异常类型**：受检异常用于预期错误，非受检异常用于编程错误
5. **提供有意义的异常信息**：帮助开发者快速定位问题
6. **正确处理资源清理**：使用try-with-resources确保资源释放
7. **适当记录异常**：根据异常级别选择合适的日志级别

### 9.3 学习建议

1. **理解概念**：深入理解异常处理机制的设计思想
2. **动手实践**：通过编写代码掌握异常处理的各种语法
3. **阅读源码**：学习Java标准库中的异常处理模式
4. **关注性能**：了解异常处理对性能的影响
5. **团队规范**：制定团队的异常处理编码规范

通过本章的学习，你应该能够：
- 理解Java异常处理机制的核心概念
- 掌握异常处理的各种语法和技巧
- 编写健壮、易维护的异常处理代码
- 避免常见的异常处理陷阱
- 设计合理的自定义异常体系

在下一章中，我们将学习Java的输入输出（I/O）操作，这是Java编程中另一个重要的主题。