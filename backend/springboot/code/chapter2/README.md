# 第二章代码示例

这是 Spring Boot 从入门到专家教程第二章的完整代码示例。

## 项目结构

```
chapter2/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       ├── DemoApplication.java
│   │   │       ├── controller/
│   │   │       │   └── UserController.java
│   │   │       ├── service/
│   │   │       │   └── UserService.java
│   │   │       ├── repository/
│   │   │       │   └── UserRepository.java
│   │   │       └── entity/
│   │   │           └── User.java
│   │   └── resources/
│   │       ├── application.properties
│   │       └── data.sql
│   └── test/
│       └── java/
│           └── com/example/demo/
│               ├── UserRepositoryTest.java
│               └── UserControllerIntegrationTest.java
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
java -jar target/chapter2-0.0.1-SNAPSHOT.jar
```

## API 测试

应用启动后，可以使用以下 API 进行测试：

1. 获取所有用户：`GET http://localhost:8080/api/users`
2. 获取特定用户：`GET http://localhost:8080/api/users/1`
3. 创建用户：`POST http://localhost:8080/api/users`
4. 更新用户：`PUT http://localhost:8080/api/users/1`
5. 删除用户：`DELETE http://localhost:8080/api/users/1`

## 项目说明

这是一个完整的 Spring Boot Web 应用程序，展示了：
1. Spring Boot 核心概念的实际应用
2. JPA 数据访问层的使用
3. RESTful API 的设计与实现
4. 单元测试和集成测试的编写

更多详细说明请参考教程第二章：[2-核心概念与基础入门.md](../../2-核心概念与基础入门.md)