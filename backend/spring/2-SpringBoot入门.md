# 第2章 Spring Boot入门

## 本章概述

本章将介绍Spring Boot框架，它是Spring生态系统中的一个重要组成部分，旨在简化Spring应用程序的创建和开发过程。我们将学习Spring Boot的核心特性、自动配置机制、起步依赖以及如何快速构建Web应用程序。

## 目录

1. [Spring Boot简介](#spring-boot简介)
2. [Spring Boot的核心特性](#spring-boot的核心特性)
3. [Spring Boot项目结构](#spring-boot项目结构)
4. [起步依赖（Starter Dependencies）](#起步依赖starter-dependencies)
5. [自动配置（Auto-configuration）](#自动配置auto-configuration)
6. [创建第一个Spring Boot应用程序](#创建第一个spring-boot应用程序)
7. [Spring Boot Actuator](#spring-boot-actuator)
8. [配置文件](#配置文件)
9. [Spring Boot DevTools](#spring-boot-devtools)
10. [打包和部署](#打包和部署)

## Spring Boot简介

Spring Boot是由Pivotal团队提供的全新框架，其设计目的是用来简化Spring应用的初始搭建以及开发过程。该框架使用了特定的方式来进行配置，从而使开发人员不再需要定义样板化的配置。

### Spring Boot的目标

1. **为所有Spring开发者提供更快、更广泛的入门体验**
2. **开箱即用，但通过不采用默认值可以快速摆脱这种方式**
3. **提供大型项目（如嵌入式服务器、安全、指标、健康检查和外部化配置）中常见的一系列非功能性特性**
4. **绝对没有代码生成，也不要求XML配置**

### Spring Boot的优点

1. **简化配置**：通过自动配置减少大量的XML配置或注解配置
2. **内嵌服务器**：内置Tomcat、Jetty、Undertow等服务器，无需部署WAR文件
3. **起步依赖**：提供一系列方便的依赖描述符，可以一次性引入需要的Spring和相关技术
4. **生产就绪**：提供健康检查、指标、外部化配置等生产就绪功能
5. **无代码生成和XML配置**：完全基于注解和约定优于配置的原则

## Spring Boot的核心特性

### 1. 自动配置（Auto-configuration）

Spring Boot会尝试根据添加的jar依赖自动配置Spring应用。例如，如果classpath下存在HSQLDB，并且没有手动配置任何数据库连接的Bean，那么Spring Boot会自动配置一个内存数据库。

### 2. 起步依赖（Starter Dependencies）

Spring Boot提供了一系列的"starter"依赖，这些依赖能够以一种简单的方式将常用的库聚合在一起。例如，如果你想使用Spring和JPA访问数据库，只需要在项目中包含spring-boot-starter-data-jpa依赖即可。

### 3. 内嵌服务器

Spring Boot支持内嵌的Tomcat、Jetty和Undertow服务器，这意味着你可以将应用程序打包成一个可执行的JAR文件，而不需要部署到外部服务器上。

### 4. 生产就绪特性

Spring Boot提供了一系列生产就绪的功能，如指标、健康检查和外部化配置，可以帮助你在生产环境中更好地监控和管理应用程序。

## Spring Boot项目结构

一个典型的Spring Boot项目具有以下结构：

```
myproject/
├── pom.xml
└── src/
    └── main/
        ├── java/
        │   └── com/
        │       └── example/
        │           └── myproject/
        │               ├── MyProjectApplication.java
        │               ├── controller/
        │               ├── service/
        │               ├── repository/
        │               └── model/
        └── resources/
            ├── application.properties
            ├── static/
            └── templates/
```

### 主要组件说明

1. **MyProjectApplication.java**：应用程序的入口点，包含main方法
2. **controller/**：控制器层，处理HTTP请求
3. **service/**：业务逻辑层
4. **repository/**：数据访问层
5. **model/**：实体类
6. **application.properties**：配置文件
7. **static/**：静态资源文件（CSS、JS、图片等）
8. **templates/**：模板文件（Thymeleaf、Freemarker等）

## 起步依赖（Starter Dependencies）

Spring Boot提供了一系列的starter依赖，它们是一组便捷的依赖描述符，可以包含相关的技术栈。你只需在项目中包含相应的starter，就能获得所需的所有功能。

### 常用的Starter依赖

| Starter | 描述 |
|---------|------|
| spring-boot-starter | 核心starter，包括自动配置支持、日志和YAML |
| spring-boot-starter-web | 构建Web应用，包括RESTful应用，使用Spring MVC和Tomcat作为默认内嵌容器 |
| spring-boot-starter-data-jpa | 使用Hibernate的Spring Data JPA |
| spring-boot-starter-security | 使用Spring Security |
| spring-boot-starter-test | 测试Spring Boot应用，包括JUnit、Hamcrest和Mockito |
| spring-boot-starter-actuator | 生产就绪功能，用于监控和管理应用 |

### Maven依赖示例

```xml
<dependencies>
    <!-- Web starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Data JPA starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <!-- Test starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

## 自动配置（Auto-configuration）

Spring Boot的自动配置机制会尝试根据类路径下的jar包、类和各种属性设置来合理地推断和配置应用程序需要的Bean。

### 如何工作

1. Spring Boot检查类路径下的依赖
2. 根据依赖和配置属性，应用相应的自动配置
3. 如果需要，可以覆盖默认配置

### 条件注解

自动配置大量使用了条件注解，这些注解确保只有在满足特定条件时才会应用配置：

```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
public class DataSourceAutoConfiguration {
    // 自动配置代码
}
```

常见的条件注解包括：
- `@ConditionalOnClass`：当类路径下有指定的类时条件匹配
- `@ConditionalOnMissingBean`：当容器中没有指定Bean时条件匹配
- `@ConditionalOnProperty`：当指定的属性有指定的值时条件匹配
- `@ConditionalOnWebApplication`：当应用是Web应用时条件匹配

### 排除自动配置

如果需要排除某些自动配置，可以通过以下方式：

```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

或者在配置文件中：

```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

## 创建第一个Spring Boot应用程序

### 使用Spring Initializr

Spring Initializr是创建Spring Boot项目的最快方式。你可以通过以下几种方式使用它：

1. 访问 https://start.spring.io/
2. 使用IDE内置的Spring Initializr功能
3. 使用Spring Boot CLI

### 手动创建Maven项目

1. 创建pom.xml文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.0</version>
        <relativePath/>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>my-spring-boot-app</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>my-spring-boot-app</name>
    
    <properties>
        <java.version>11</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

2. 创建主应用程序类：

```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class MySpringBootApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(MySpringBootApplication.class, args);
    }
    
    @GetMapping("/")
    public String hello() {
        return "Hello, Spring Boot!";
    }
}
```

3. 运行应用程序：

```bash
mvn spring-boot:run
```

或者打包后运行：

```bash
mvn clean package
java -jar target/my-spring-boot-app-0.0.1-SNAPSHOT.jar
```

## Spring Boot Actuator

Spring Boot Actuator提供了生产就绪的功能，帮助你监控和管理应用程序。

### 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### 常用端点

| 端点ID | 描述 |
|--------|------|
| /actuator/health | 显示应用程序的健康信息 |
| /actuator/info | 显示应用程序的信息 |
| /actuator/metrics | 显示应用程序的指标信息 |
| /actuator/env | 显示环境属性 |
| /actuator/loggers | 显示和修改日志级别 |

### 配置示例

```properties
# 启用所有端点
management.endpoints.web.exposure.include=*
# 启用特定端点
management.endpoints.web.exposure.include=health,info,metrics
# 修改端点基础路径
management.endpoints.web.base-path=/manage
```

## 配置文件

Spring Boot支持多种格式的配置文件，默认配置文件名为application.properties或application.yml。

### application.properties示例

```properties
# 服务器配置
server.port=8080
server.servlet.context-path=/api

# 数据库配置
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA配置
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect

# 日志配置
logging.level.com.example=DEBUG
logging.file.name=logs/app.log
```

### application.yml示例

```yaml
server:
  port: 8080
  servlet:
    context-path: /api

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
  
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect

logging:
  level:
    com.example: DEBUG
  file:
    name: logs/app.log
```

### 配置属性绑定

```java
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    private int timeout;
    private List<String> servers;
    
    // getters and setters
}
```

对应的配置文件：

```properties
app.name=MyApp
app.timeout=30
app.servers[0]=server1
app.servers[1]=server2
```

## Spring Boot DevTools

Spring Boot DevTools提供了一套开发时的增强功能，可以提高开发效率。

### 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
```

### 主要特性

1. **自动重启**：当类路径下的文件发生变化时自动重启应用
2. **LiveReload**：浏览器自动刷新页面
3. **全局设置**：可以为所有Spring Boot应用设置通用的配置

### 配置示例

```properties
# 启用安静期以防止频繁重启
spring.devtools.restart.poll-interval=2s
spring.devtools.restart.quiet-period=1s

# 排除不需要触发重启的路径
spring.devtools.restart.exclude=static/**,public/**

# 启用LiveReload
spring.devtools.livereload.enabled=true
```

## 打包和部署

Spring Boot应用可以打包成可执行的JAR文件或WAR文件。

### 打包为JAR

在pom.xml中确保有以下插件：

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

然后执行命令：

```bash
mvn clean package
```

### 打包为WAR

1. 修改pom.xml：

```xml
<packaging>war</packaging>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-tomcat</artifactId>
    <scope>provided</scope>
</dependency>
```

2. 修改主应用程序类：

```java
@SpringBootApplication
public class MyApplication extends SpringBootServletInitializer {
    
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application.sources(MyApplication.class);
    }
    
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

### Docker部署

创建Dockerfile：

```dockerfile
FROM openjdk:11-jre-slim
VOLUME /tmp
COPY target/my-spring-boot-app-0.0.1-SNAPSHOT.jar app.jar
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app.jar"]
```

构建和运行：

```bash
docker build -t my-spring-boot-app .
docker run -p 8080:8080 my-spring-boot-app
```

## 总结

本章我们学习了Spring Boot的核心概念和入门知识，包括：

1. **Spring Boot简介**：了解了Spring Boot的设计目标和优点
2. **核心特性**：自动配置、起步依赖、内嵌服务器和生产就绪特性
3. **项目结构**：标准的Spring Boot项目结构
4. **起步依赖**：如何使用starter依赖简化项目配置
5. **自动配置**：Spring Boot如何根据类路径自动配置应用
6. **创建应用**：通过示例演示了如何创建第一个Spring Boot应用
7. **Actuator**：如何使用Actuator监控应用
8. **配置文件**：properties和yml格式的配置文件使用
9. **DevTools**：开发时的增强工具
10. **打包部署**：如何打包和部署Spring Boot应用

Spring Boot极大地简化了Spring应用的开发过程，使开发者能够专注于业务逻辑而不是基础设施配置。通过自动配置和起步依赖，我们可以快速搭建起功能完整的应用。