# 第1章 Spring核心概念

## 本章概述

本章将介绍Spring框架的核心概念，包括控制反转（IoC）、依赖注入（DI）、Spring容器、Bean的生命周期等。这些概念是理解和使用Spring框架的基础。

## 目录

1. [Spring框架简介](#spring框架简介)
2. [控制反转（IoC）](#控制反转ioc)
3. [依赖注入（DI）](#依赖注入di)
4. [Spring容器](#spring容器)
5. [Bean的定义和配置](#bean的定义和配置)
6. [Bean的作用域](#bean的作用域)
7. [Bean的生命周期](#bean的生命周期)
8. [ApplicationContext和BeanFactory](#applicationcontext和beanfactory)

## Spring框架简介

Spring框架是一个开源的Java平台应用程序框架和控制反转容器。它由Rod Johnson在2003年首次发布，现在由Pivotal Software维护。

### Spring框架的核心特性

1. **轻量级**：Spring在大小和透明度方面都是轻量级的。
2. **控制反转（IoC）**：Spring容器使用控制反转来管理应用程序的对象。
3. **面向切面编程（AOP）**：Spring支持面向切面编程，允许通过分离横切关注点来解耦应用程序。
4. **容器**：Spring包含并管理应用程序对象的生命周期和配置。
5. **框架**：Spring提供了全面的基础设施支持，用于开发Java应用程序。

### Spring框架模块

Spring框架由大约20个模块组成，这些模块被组织在核心容器、数据访问/集成、Web、AOP（面向切面编程）、仪器（Instrumentation）、消息传递和测试等模块组中。

```
Spring Framework Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    Core Container                           │
├─────────────────────────────────────────────────────────────┤
│  Beans  │  Core  │  Context  │  Expression Language         │
├─────────────────────────────────────────────────────────────┤
│                 Data Access/Integration                     │
├─────────────────────────────────────────────────────────────┤
│  JDBC  │  ORM  │  OXM  │  JMS  │  Transactions              │
├─────────────────────────────────────────────────────────────┤
│                        Web Layer                            │
├─────────────────────────────────────────────────────────────┤
│  Web  │  Web MVC  │  Web Socket  │  Web Portlet             │
├─────────────────────────────────────────────────────────────┤
│                    Miscellaneous                            │
├─────────────────────────────────────────────────────────────┤
│  AOP  │  Aspects  │  Instrumentation  │  Messaging          │
└─────────────────────────────────────────────────────────────┘
```

## 控制反转（IoC）

控制反转（Inversion of Control，IoC）是面向对象编程中的一种设计原则，用于降低代码之间的耦合度。在传统的编程方式中，对象的创建和依赖关系由对象自身管理，而在IoC模式中，这些控制权被反转给了外部容器。

### 传统方式 vs IoC方式

#### 传统方式
```java
public class UserService {
    private UserRepository userRepository = new UserRepository(); // 直接创建依赖
    
    public void saveUser(User user) {
        userRepository.save(user);
    }
}
```

#### IoC方式
```java
public class UserService {
    private UserRepository userRepository; // 依赖通过外部注入
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public void saveUser(User user) {
        userRepository.save(user);
    }
}
```

### IoC的优势

1. **降低耦合度**：对象不需要知道其依赖的具体实现
2. **提高可测试性**：可以轻松地注入模拟对象进行测试
3. **提高可维护性**：更容易修改和扩展代码
4. **提高可重用性**：对象不依赖于特定的实现

## 依赖注入（DI）

依赖注入（Dependency Injection，DI）是控制反转的一种实现方式。它通过构造函数、setter方法或接口来提供对象依赖关系，而不是由对象内部创建这些依赖。

### 依赖注入的类型

#### 1. 构造函数注入
```java
public class UserService {
    private final UserRepository userRepository;
    
    // 通过构造函数注入依赖
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public void saveUser(User user) {
        userRepository.save(user);
    }
}
```

#### 2. Setter方法注入
```java
public class UserService {
    private UserRepository userRepository;
    
    // 通过setter方法注入依赖
    public void setUserRepository(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public void saveUser(User user) {
        userRepository.save(user);
    }
}
```

#### 3. 字段注入
```java
public class UserService {
    @Autowired
    private UserRepository userRepository; // 通过注解直接注入字段
    
    public void saveUser(User user) {
        userRepository.save(user);
    }
}
```

### 依赖注入的优势

1. **松耦合**：对象不直接依赖于具体实现
2. **可测试性**：可以轻松注入模拟对象进行单元测试
3. **可配置性**：依赖关系可以通过配置文件或注解进行配置
4. **可重用性**：对象可以在不同的上下文中重用

## Spring容器

Spring容器是Spring框架的核心，它负责创建对象、配置对象以及管理对象的生命周期。

### 容器的类型

Spring框架提供了两种主要类型的容器：

1. **BeanFactory**：这是Spring框架最核心的部分，提供了基本的IoC功能
2. **ApplicationContext**：这是BeanFactory的子接口，提供了更多企业级功能

### ApplicationContext的实现

Spring提供了多种ApplicationContext的实现：

1. **ClassPathXmlApplicationContext**：从类路径加载配置文件
2. **FileSystemXmlApplicationContext**：从文件系统加载配置文件
3. **AnnotationConfigApplicationContext**：基于注解的配置
4. **WebApplicationContext**：用于Web应用程序

### 容器的使用示例

#### XML配置方式
```java
// applicationContext.xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
                           http://www.springframework.org/schema/beans/spring-beans.xsd">
    
    <bean id="userRepository" class="com.example.UserRepository"/>
    
    <bean id="userService" class="com.example.UserService">
        <constructor-arg ref="userRepository"/>
    </bean>
</beans>

// Java代码
ApplicationContext context = new ClassPathXmlApplicationContext("applicationContext.xml");
UserService userService = context.getBean("userService", UserService.class);
```

#### 注解配置方式
```java
@Configuration
@ComponentScan(basePackages = "com.example")
public class AppConfig {
    @Bean
    public UserRepository userRepository() {
        return new UserRepository();
    }
    
    @Bean
    public UserService userService() {
        return new UserService(userRepository());
    }
}

// Java代码
ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);
UserService userService = context.getBean(UserService.class);
```

## Bean的定义和配置

在Spring中，Bean是由Spring容器管理的对象。Bean的定义包含了创建对象所需的信息，包括类名、属性值、依赖关系等。

### Bean的定义方式

#### 1. XML配置
```xml
<bean id="userService" class="com.example.UserService">
    <property name="userRepository" ref="userRepository"/>
    <property name="maxRetryAttempts" value="3"/>
</bean>
```

#### 2. 注解配置
```java
@Component
public class UserService {
    @Autowired
    private UserRepository userRepository;
    
    @Value("${max.retry.attempts:3}")
    private int maxRetryAttempts;
}
```

#### 3. Java配置
```java
@Configuration
public class AppConfig {
    @Bean
    public UserService userService(UserRepository userRepository) {
        UserService service = new UserService();
        service.setUserRepository(userRepository);
        service.setMaxRetryAttempts(3);
        return service;
    }
}
```

### Bean的命名

每个Bean都有一个或多个标识符，在基于XML的配置中，可以使用id属性或name属性来指定Bean的标识符。

```xml
<!-- 使用id属性 -->
<bean id="userService" class="com.example.UserService"/>

<!-- 使用name属性 -->
<bean name="userService" class="com.example.UserService"/>

<!-- 使用多个名称 -->
<bean name="userService, userSvc, service" class="com.example.UserService"/>
```

## Bean的作用域

Spring框架支持多种Bean的作用域，用于定义Bean实例的创建方式和生命周期。

### 内置作用域

1. **singleton**（默认）：每个Spring IoC容器只有一个Bean实例
2. **prototype**：每次请求时创建一个新的Bean实例
3. **request**：每个HTTP请求创建一个Bean实例，仅在Web-aware Spring ApplicationContext中有效
4. **session**：每个HTTP Session创建一个Bean实例，仅在Web-aware Spring ApplicationContext中有效
5. **application**：每个ServletContext创建一个Bean实例，仅在Web-aware Spring ApplicationContext中有效
6. **websocket**：每个WebSocket创建一个Bean实例，仅在Web-aware Spring ApplicationContext中有效

### 作用域配置示例

#### XML配置
```xml
<bean id="userService" class="com.example.UserService" scope="singleton"/>
<bean id="userController" class="com.example.UserController" scope="prototype"/>
```

#### 注解配置
```java
@Component
@Scope("singleton")
public class UserService {
    // ...
}

@Component
@Scope("prototype")
public class UserController {
    // ...
}
```

## Bean的生命周期

Spring Bean的生命周期从创建到销毁经历了多个阶段，Spring容器提供了多种方式来参与这个生命周期。

### 生命周期阶段

1. **实例化**：Spring容器根据Bean定义创建Bean实例
2. **属性赋值**：Spring容器将所有属性值和依赖注入到Bean实例中
3. **设置Bean名称**：如果Bean实现了BeanNameAware接口，Spring容器会调用setBeanName()方法
4. **设置Bean工厂**：如果Bean实现了BeanFactoryAware接口，Spring容器会调用setBeanFactory()方法
5. **预初始化**：如果Bean实现了ApplicationContextAware接口，Spring容器会调用setApplicationContext()方法
6. **BeanPostProcessor前置处理**：如果存在BeanPostProcessor，Spring容器会调用postProcessBeforeInitialization()方法
7. **初始化**：如果Bean实现了InitializingBean接口，Spring容器会调用afterPropertiesSet()方法
8. **自定义初始化**：如果Bean定义了init-method，Spring容器会调用指定的方法
9. **BeanPostProcessor后置处理**：如果存在BeanPostProcessor，Spring容器会调用postProcessAfterInitialization()方法
10. **使用**：Bean可以被应用程序使用
11. **销毁**：如果Bean实现了DisposableBean接口，Spring容器会调用destroy()方法
12. **自定义销毁**：如果Bean定义了destroy-method，Spring容器会调用指定的方法

### 生命周期回调示例

```java
public class UserService implements InitializingBean, DisposableBean, BeanNameAware {
    private String beanName;
    
    @Override
    public void setBeanName(String name) {
        this.beanName = name;
        System.out.println("Bean name set: " + name);
    }
    
    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("UserService afterPropertiesSet");
    }
    
    @PostConstruct
    public void init() {
        System.out.println("UserService init method");
    }
    
    @PreDestroy
    public void destroyMethod() {
        System.out.println("UserService destroy method");
    }
    
    @Override
    public void destroy() throws Exception {
        System.out.println("UserService destroy");
    }
}
```

### 配置初始化和销毁方法

#### XML配置
```xml
<bean id="userService" class="com.example.UserService" 
      init-method="init" destroy-method="destroyMethod"/>
```

#### 注解配置
```java
@Bean(initMethod = "init", destroyMethod = "destroyMethod")
public UserService userService() {
    return new UserService();
}
```

## ApplicationContext和BeanFactory

ApplicationContext是BeanFactory的子接口，它提供了更多企业级功能。

### BeanFactory vs ApplicationContext

| 特性 | BeanFactory | ApplicationContext |
|------|-------------|-------------------|
| Bean实例化/装配 | 支持 | 支持 |
| 自动BeanPostProcessor注册 | 不支持 | 支持 |
| 自动BeanFactoryPostProcessor注册 | 不支持 | 支持 |
| 国际化支持 | 不支持 | 支持 |
| ApplicationEvent发布 | 不支持 | 支持 |
| 消息源访问 | 不支持 | 支持 |

### ApplicationContext的使用

```java
// ClassPathXmlApplicationContext
ApplicationContext context = new ClassPathXmlApplicationContext("applicationContext.xml");

// FileSystemXmlApplicationContext
ApplicationContext context = new FileSystemXmlApplicationContext("config/applicationContext.xml");

// AnnotationConfigApplicationContext
ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);

// WebApplicationContext（在Web应用中）
WebApplicationContext context = WebApplicationContextUtils.getWebApplicationContext(servletContext);
```

### 访问ApplicationContext中的Bean

```java
// 通过Bean的名称获取
UserService userService = (UserService) context.getBean("userService");

// 通过Bean的名称和类型获取
UserService userService = context.getBean("userService", UserService.class);

// 通过类型获取（当容器中只有一个该类型的Bean时）
UserService userService = context.getBean(UserService.class);

// 获取所有Bean的名称
String[] beanNames = context.getBeanDefinitionNames();

// 检查Bean是否存在
boolean exists = context.containsBean("userService");
```

## 总结

本章介绍了Spring框架的核心概念，包括：

1. **控制反转（IoC）**：将对象的创建和管理控制权交给外部容器
2. **依赖注入（DI）**：通过构造函数、setter方法或字段注入来提供对象依赖
3. **Spring容器**：负责创建、配置和管理Bean的生命周期
4. **Bean的定义和配置**：通过XML、注解或Java配置来定义Bean
5. **Bean的作用域**：singleton、prototype等不同作用域的使用
6. **Bean的生命周期**：从创建到销毁的各个阶段及回调方法
7. **ApplicationContext和BeanFactory**：两种容器类型的区别和使用

理解这些核心概念是掌握Spring框架的基础，后续章节将深入探讨Spring的其他重要特性，如AOP、数据访问、Web开发等。

在实际开发中，建议：
1. 优先使用注解配置而非XML配置
2. 合理选择Bean的作用域
3. 正确处理Bean的生命周期回调
4. 充分利用Spring容器提供的各种功能