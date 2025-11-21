# 第一章代码示例

这是 Spring Boot 从入门到专家教程第一章的完整代码示例。

## 项目结构

```
chapter1/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       ├── DemoApplication.java
│   │   │       └── controller/
│   │   │           └── HelloController.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
│       └── java/
│           └── com/example/demo/
│               └── DemoApplicationTests.java
└── pom.xml
```

## 如何运行

1. 确保已安装 JDK 11+ 和 Maven
2. 在项目根目录下执行以下命令：

```bash
mvn spring-boot:run
```

或者

```bash
mvn clean package
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

3. 打开浏览器访问 `http://localhost:8080/hello`

## 项目说明

这是一个最简单的 Spring Boot Web 应用程序，展示了：
1. 如何创建 Spring Boot 项目
2. 主程序类的结构
3. 控制器的创建和使用
4. 应用程序的启动方式

更多详细说明请参考教程第一章：[1-简介与环境搭建.md](../../1-简介与环境搭建.md)