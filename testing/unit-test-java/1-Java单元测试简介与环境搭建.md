# 第1章：Java单元测试简介与环境搭建

## 1.1 单元测试基础概念

### 什么是单元测试？

单元测试是软件开发中的一种测试方法，用于验证程序中最小的可测试单元（通常是一个方法或类）是否按预期工作。单元测试具有以下特点：

- **原子性**：测试最小的代码单元
- **独立性**：测试之间相互独立，不依赖外部环境
- **快速性**：执行速度快，可以频繁运行
- **自动化**：可以自动执行并验证结果

### 单元测试的重要性

单元测试对于软件质量保证至关重要：

1. **提高代码质量**：迫使开发者思考代码的可测试性
2. **及早发现bug**：在开发阶段就能发现问题
3. **促进重构**：有测试保护的重构更加安全
4. **文档作用**：好的测试用例可以作为代码的使用文档
5. **降低维护成本**：及早发现问题，减少后期修复成本

### 单元测试 vs 集成测试

| 特性 | 单元测试 | 集成测试 |
|------|----------|----------|
| 测试范围 | 单个类/方法 | 多个组件/服务 |
| 执行速度 | 快 | 慢 |
| 依赖处理 | 使用Mock对象 | 使用真实依赖 |
| 稳定性 | 高 | 低 |
| 维护成本 | 低 | 高 |

## 1.2 Java单元测试生态系统

### JUnit框架介绍

JUnit是Java最流行的单元测试框架，经历了多个版本演进：

- **JUnit 3**: 基于命名约定的早期版本
- **JUnit 4**: 基于注解的革命性版本
- **JUnit 5**: 模块化架构的现代化版本（Jupiter + Vintage + Platform）

### 常用测试框架和工具

1. **JUnit** - 核心测试框架
2. **Mockito** - Mock对象框架
3. **AssertJ** - 流畅的断言库
4. **TestNG** - 另一种测试框架
5. **Hamcrest** - 匹配器库
6. **PowerMock** - 静态方法Mock框架

## 1.3 开发环境搭建

### 1.3.1 JDK安装

确保已安装JDK 8或更高版本（推荐Java 11+）：

```bash
# 检查Java版本
java -version
javac -version
```

### 1.3.2 Maven项目创建

创建Maven项目，配置pom.xml依赖：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>java-unit-test-demo</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <junit.jupiter.version>5.9.2</junit.jupiter.version>
        <mockito.version>5.1.1</mockito.version>
        <assertj.version>3.24.2</assertj.version>
    </properties>

    <dependencies>
        <!-- JUnit 5 依赖 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.jupiter.version}</version>
            <scope>test</scope>
        </dependency>
        
        <!-- Mockito 依赖 -->
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>${mockito.version}</version>
            <scope>test</scope>
        </dependency>
        
        <!-- Mockito JUnit Jupiter 集成 -->
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <version>${mockito.version}</version>
            <scope>test</scope>
        </dependency>
        
        <!-- AssertJ 流畅断言库 -->
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <version>${assertj.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M8</version>
                <configuration>
                    <includes>
                        <include>**/*Test.java</include>
                        <include>**/*Tests.java</include>
                    </includes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### 1.3.3 Gradle项目创建

如果您更喜欢使用Gradle，可以创建build.gradle文件：

```gradle
plugins {
    id 'java'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.9.2'
    testImplementation 'org.mockito:mockito-core:5.1.1'
    testImplementation 'org.mockito:mockito-junit-jupiter:5.1.1'
    testImplementation 'org.assertj:assertj-core:3.24.2'
}

test {
    useJUnitPlatform()
    
    testLogging {
        events "passed", "skipped", "failed"
        exceptionFormat "full"
    }
}
```

## 1.4 第一个单元测试

### 1.4.1 创建待测试类

```java
package com.example.calculator;

public class Calculator {
    /**
     * 加法运算
     * @param a 第一个数
     * @param b 第二个数
     * @return 两个数的和
     */
    public int add(int a, int b) {
        return a + b;
    }
    
    /**
     * 减法运算
     * @param a 第一个数
     * @param b 第二个数
     * @return 两个数的差
     */
    public int subtract(int a, int b) {
        return a - b;
    }
    
    /**
     * 乘法运算
     * @param a 第一个数
     * @param b 第二个数
     * @return 两个数的积
     */
    public int multiply(int a, int b) {
        return a * b;
    }
    
    /**
     * 除法运算
     * @param a 被除数
     * @param b 除数
     * @return 两个数的商
     * @throws IllegalArgumentException 当除数为0时抛出异常
     */
    public double divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("除数不能为0");
        }
        return (double) a / b;
    }
}
```

### 1.4.2 创建测试类

在src/test/java目录下创建对应的测试类：

```java
package com.example.calculator;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CalculatorTest {
    
    private final Calculator calculator = new Calculator();
    
    @Test
    public void testAdd() {
        // 测试正常情况
        assertEquals(5, calculator.add(2, 3), "2 + 3 应该等于 5");
        assertEquals(-1, calculator.add(-2, 1), "-2 + 1 应该等于 -1");
        assertEquals(0, calculator.add(0, 0), "0 + 0 应该等于 0");
    }
    
    @Test
    public void testSubtract() {
        // 测试正常情况
        assertEquals(1, calculator.subtract(3, 2), "3 - 2 应该等于 1");
        assertEquals(-3, calculator.subtract(-2, 1), "-2 - 1 应该等于 -3");
        assertEquals(0, calculator.subtract(0, 0), "0 - 0 应该等于 0");
    }
    
    @Test
    public void testMultiply() {
        // 测试正常情况
        assertEquals(6, calculator.multiply(2, 3), "2 * 3 应该等于 6");
        assertEquals(-2, calculator.multiply(-2, 1), "-2 * 1 应该等于 -2");
        assertEquals(0, calculator.multiply(0, 5), "0 * 5 应该等于 0");
    }
    
    @Test
    public void testDivide() {
        // 测试正常情况
        assertEquals(2.5, calculator.divide(5, 2), "5 / 2 应该等于 2.5");
        assertEquals(0.5, calculator.divide(1, 2), "1 / 2 应该等于 0.5");
        assertEquals(0, calculator.divide(0, 5), "0 / 5 应该等于 0");
    }
    
    @Test
    public void testDivideByZero() {
        // 测试异常情况
        Exception exception = assertThrows(IllegalArgumentException.class, 
            () -> calculator.divide(5, 0), "除数为0应该抛出IllegalArgumentException");
        
        assertEquals("除数不能为0", exception.getMessage(), 
            "异常消息应该为'除数不能为0'");
    }
}
```

### 1.4.3 运行测试

在IDE中右键点击测试类，选择"Run 'CalculatorTest'"，或者在命令行中执行：

```bash
# Maven
mvn test

# Gradle
gradle test
```

## 1.5 IDE集成

### 1.5.1 IntelliJ IDEA配置

1. 创建新项目，选择Maven或Gradle
2. 确保项目SDK为Java 11+
3. 添加测试依赖到pom.xml或build.gradle
4. 将src/test/java标记为测试源目录
5. 使用IDE的运行/调试功能执行测试

### 1.5.2 Eclipse配置

1. 安装Eclipse IDE for Enterprise Java Developers
2. 创建Maven项目
3. 添加测试依赖
4. 确保测试源目录正确配置

### 1.5.3 VS Code配置

1. 安装Java扩展包
2. 安装Test Runner for Java扩展
3. 打开项目文件夹
4. 使用测试面板运行测试

## 1.6 测试结果解读

### 1.6.1 测试报告

运行测试后，你会看到类似如下的输出：

```
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.example.calculator.CalculatorTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.056 s - in com.example.calculator.CalculatorTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] -------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] -------------------------------------------------------
```

### 1.6.2 失败测试的分析

当测试失败时，JUnit会提供详细的失败信息：

```
[ERROR] testAdd(com.example.calculator.CalculatorTest)  Time elapsed: 0.001 s  <<< FAILURE!
org.opentest4j.AssertionFailedError: 2 + 3 应该等于 6 ==> expected: <6> but was: <5>
    at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:151)
    at org.junit.jupiter.api.AssertionFailureBuilder.buildAndThrow(AssertionFailureBuilder.java:132)
    at org.junit.jupiter.api.AssertEquals.failNotEqual(AssertEquals.java:197)
    at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:150)
    at com.example.calculator.CalculatorTest.testAdd(CalculatorTest.java:13)
```

## 1.7 常见问题与解决方案

### 1.7.1 测试找不到类

确保测试类的命名和位置正确：
- 测试类应该在src/test/java目录下
- 测试类名通常以Test结尾
- 包名应该与被测试类相同

### 1.7.2 依赖冲突

解决依赖冲突的方法：
```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.9.2</version>
    <scope>test</scope>
    <exclusions>
        <exclusion>
            <groupId>org.junit.vintage</groupId>
            <artifactId>junit-vintage-engine</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 1.7.3 版本兼容性

确保Java、JUnit和Mockito版本兼容：
- Java 8+ 适用于JUnit 5
- Mockito 3+ 适用于JUnit 5
- 推荐使用最新稳定版本

## 1.8 小结

本章介绍了单元测试的基础概念和Java单元测试环境的搭建。我们学习了：

1. 单元测试的定义、重要性和特点
2. Java单元测试生态系统和常用框架
3. 开发环境搭建，包括Maven和Gradle项目配置
4. 编写和运行第一个单元测试
5. IDE集成配置
6. 测试结果解读和常见问题解决

在下一章中，我们将深入学习JUnit的核心概念和注解，探索更多测试技巧和最佳实践。

## 1.9 实践练习

### 练习1：环境搭建
1. 创建一个Maven项目
2. 添加JUnit 5依赖
3. 验证测试环境是否正常工作

### 练习2：编写测试
1. 创建一个StringUtils类，包含字符串处理方法
2. 为StringUtils类编写完整的单元测试
3. 尝试运行测试并分析结果

### 练习3：测试异常
1. 在一个方法中添加验证逻辑，可能抛出异常
2. 编写测试验证异常情况
3. 验证异常消息是否符合预期

通过这些练习，您将巩固本章学到的知识，为后续学习打下坚实基础。