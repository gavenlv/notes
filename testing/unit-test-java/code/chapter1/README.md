# 第1章：Java单元测试简介与环境搭建 - 代码示例

本章包含Java单元测试入门的完整代码示例，包括基础配置、简单测试类和异常测试。

## 项目结构

```
chapter1/
├── pom.xml                      # Maven配置文件
├── build.gradle                 # Gradle配置文件(可选)
└── src/
    ├── main/
    │   └── java/
    │       └── com/example/calculator/
    │           └── Calculator.java    # 待测试的Calculator类
    └── test/
        └── java/
            └── com/example/calculator/
                └── CalculatorTest.java # Calculator类的单元测试
```

## 运行说明

### 使用Maven
```bash
# 编译项目
mvn compile

# 运行测试
mvn test

# 只运行CalculatorTest
mvn test -Dtest=CalculatorTest
```

### 使用Gradle
```bash
# 编译项目
gradle build

# 运行测试
gradle test
```

### 在IDE中运行
1. 导入项目到IDE (IntelliJ IDEA或Eclipse)
2. 右键点击CalculatorTest类
3. 选择"Run 'CalculatorTest'"运行所有测试
4. 或右键点击单个测试方法运行特定测试

## 核心示例说明

### 1. Calculator.java
这是一个简单的计算器类，包含基本的四则运算方法，其中除法方法包含异常处理。

### 2. CalculatorTest.java
包含了Calculator类的完整单元测试，展示了：
- 基本断言使用
- 异常测试方法
- 断言消息的使用

## 学习要点

1. 理解Maven/Gradle项目结构
2. 掌握基本的JUnit测试编写方法
3. 学会编写正常和异常情况的测试
4. 了解测试结果的解读

## 扩展练习

1. 为Calculator类添加更多功能（如幂运算、开方等）
2. 为新功能编写测试
3. 尝试修改测试代码，故意制造失败，观察错误信息
4. 尝试在IDE中使用调试功能单步执行测试