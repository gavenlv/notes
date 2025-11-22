# 第四章：Spring Boot集成MyBatis

在前面的章节中，我们学习了Spring Boot的基础知识和Web开发的相关内容。在实际的企业级应用开发中，数据访问是一个核心组成部分。虽然Spring Data JPA提供了便捷的ORM解决方案，但在某些场景下，我们可能需要更灵活的SQL控制能力，这时MyBatis就成为了一个很好的选择。

MyBatis是一个优秀的持久层框架，它支持定制化SQL、存储过程以及高级映射。MyBatis避免了几乎所有的JDBC代码和手动设置参数以及获取结果集的工作。通过简单的XML或注解来配置和映射原始类型、接口和Java POJO（Plain Old Java Objects）为数据库中的记录。

## 本章内容概要

1. MyBatis简介与核心概念
2. Spring Boot集成MyBatis的配置方式
3. MyBatis的XML映射文件详解
4. MyBatis注解方式使用
5. 动态SQL的使用
6. MyBatis分页插件PageHelper
7. MyBatis Generator代码生成器
8. 事务管理
9. 最佳实践与性能优化

## 4.1 MyBatis简介与核心概念

### 4.1.1 MyBatis是什么

MyBatis是一个半自动化的ORM（对象关系映射）框架，它内部封装了JDBC，使得开发人员只需要关注SQL本身，而不需要花费精力去处理注册驱动、创建Connection、Statement、ResultSet等繁杂的过程。

MyBatis通过XML或注解的方式将接口方法与SQL语句进行映射，最终执行SQL并将结果映射为Java对象。

### 4.1.2 MyBatis的核心组件

1. **SqlSessionFactoryBuilder**：用于创建SqlSessionFactory，只在应用启动时使用一次。
2. **SqlSessionFactory**：用于创建SqlSession，相当于一个数据源，线程安全，可以被多个DAO共享。
3. **SqlSession**：用于执行SQL语句，是线程不安全的，每次请求都需要创建新的实例。
4. **Mapper接口**：MyBatis通过Mapper接口定义数据访问方法，框架会为接口生成代理对象。
5. **Mapper XML文件**：包含SQL语句的XML文件，与Mapper接口一一对应。

### 4.1.3 MyBatis与JPA的对比

| 特性 | MyBatis | JPA/Hibernate |
|------|---------|---------------|
| 学习成本 | 需要掌握SQL | ORM概念较多 |
| SQL控制 | 完全控制 | 由框架生成 |
| 灵活性 | 高 | 中等 |
| 开发效率 | 中等 | 高 |
| 性能 | 高 | 中等 |
| 适用场景 | 复杂查询、报表系统 | 快速开发、简单CRUD |

## 4.2 Spring Boot集成MyBatis

在Spring Boot中集成MyBatis有两种主要方式：
1. 使用MyBatis官方提供的`mybatis-spring-boot-starter`
2. 使用阿里巴巴的`mybatis-plus-boot-starter`（MyBatis增强工具）

我们先介绍第一种方式。

### 4.2.1 添加依赖

在`pom.xml`中添加MyBatis和相关依赖：

```xml
<dependencies>
    <!-- Spring Boot Web Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- MyBatis Starter -->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>2.2.2</version>
    </dependency>
    
    <!-- MySQL驱动 -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <scope>runtime</scope>
    </dependency>
    
    <!-- 连接池 -->
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>druid-spring-boot-starter</artifactId>
        <version>1.2.8</version>
    </dependency>
    
    <!-- 分页插件 -->
    <dependency>
        <groupId>com.github.pagehelper</groupId>
        <artifactId>pagehelper-spring-boot-starter</artifactId>
        <version>1.4.1</version>
    </dependency>
    
    <!-- 测试依赖 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### 4.2.2 配置文件

在`application.properties`中配置数据源和MyBatis相关属性：

```properties
# 数据源配置
spring.datasource.url=jdbc:mysql://localhost:3306/mybatis_demo?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
spring.datasource.username=root
spring.datasource.password=root
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# Druid连接池配置
spring.datasource.druid.initial-size=5
spring.datasource.druid.min-idle=5
spring.datasource.druid.max-active=20
spring.datasource.druid.stat-view-servlet.login-username=admin
spring.datasource.druid.stat-view-servlet.login-password=admin

# MyBatis配置
mybatis.mapper-locations=classpath:mapper/*.xml
mybatis.type-aliases-package=com.example.mybatis.entity
mybatis.configuration.map-underscore-to-camel-case=true

# PageHelper分页插件配置
pagehelper.helper-dialect=mysql
pagehelper.reasonable=true
pagehelper.support-methods-arguments=true
pagehelper.params=count=countSql
```

### 4.2.3 启动类配置

在Spring Boot启动类上添加Mapper扫描注解：

```java
@SpringBootApplication
@MapperScan("com.example.mybatis.mapper")
public class MyBatisApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyBatisApplication.class, args);
    }
}
```

## 4.3 MyBatis的XML映射文件详解

XML映射文件是MyBatis的核心，它包含了SQL语句和结果映射的定义。

### 4.3.1 基本结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" 
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.example.mybatis.mapper.UserMapper">
    <!-- SQL语句定义 -->
</mapper>
```

### 4.3.2 Select查询

```xml
<!-- 根据ID查询用户 -->
<select id="selectUserById" parameterType="long" resultType="com.example.mybatis.entity.User">
    SELECT id, username, email, created_at FROM users WHERE id = #{id}
</select>

<!-- 查询所有用户 -->
<select id="selectAllUsers" resultType="com.example.mybatis.entity.User">
    SELECT id, username, email, created_at FROM users
</select>

<!-- 根据用户名模糊查询 -->
<select id="selectUsersByUsername" parameterType="string" resultType="com.example.mybatis.entity.User">
    SELECT id, username, email, created_at FROM users WHERE username LIKE CONCAT('%', #{username}, '%')
</select>
```

### 4.3.3 Insert插入

```xml
<!-- 插入用户 -->
<insert id="insertUser" parameterType="com.example.mybatis.entity.User" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO users(username, email, created_at) 
    VALUES(#{username}, #{email}, #{createdAt})
</insert>
```

### 4.3.4 Update更新

```xml
<!-- 更新用户 -->
<update id="updateUser" parameterType="com.example.mybatis.entity.User">
    UPDATE users 
    SET username = #{username}, email = #{email} 
    WHERE id = #{id}
</update>
```

### 4.3.5 Delete删除

```xml
<!-- 删除用户 -->
<delete id="deleteUser" parameterType="long">
    DELETE FROM users WHERE id = #{id}
</delete>
```

### 4.3.6 结果映射

当数据库字段名与实体类属性名不一致时，可以使用`<resultMap>`进行映射：

```xml
<resultMap id="UserResultMap" type="com.example.mybatis.entity.User">
    <id property="id" column="id"/>
    <result property="username" column="user_name"/>
    <result property="email" column="email_address"/>
    <result property="createdAt" column="created_at"/>
</resultMap>

<select id="selectUserById" parameterType="long" resultMap="UserResultMap">
    SELECT id, user_name, email_address, created_at FROM users WHERE id = #{id}
</select>
```

## 4.4 MyBatis注解方式使用

除了XML映射文件，MyBatis还支持使用注解来定义SQL语句。

### 4.4.1 基本注解

```java
@Mapper
public interface UserMapper {
    
    @Select("SELECT id, username, email, created_at FROM users WHERE id = #{id}")
    User selectUserById(Long id);
    
    @Select("SELECT id, username, email, created_at FROM users")
    List<User> selectAllUsers();
    
    @Insert("INSERT INTO users(username, email, created_at) VALUES(#{username}, #{email}, #{createdAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertUser(User user);
    
    @Update("UPDATE users SET username = #{username}, email = #{email} WHERE id = #{id}")
    int updateUser(User user);
    
    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteUser(Long id);
}
```

### 4.4.2 结果映射注解

```java
@Results({
    @Result(property = "id", column = "id"),
    @Result(property = "username", column = "user_name"),
    @Result(property = "email", column = "email_address"),
    @Result(property = "createdAt", column = "created_at")
})
@Select("SELECT id, user_name, email_address, created_at FROM users WHERE id = #{id}")
User selectUserById(Long id);
```

## 4.5 动态SQL的使用

MyBatis提供了强大的动态SQL功能，可以根据不同的条件生成不同的SQL语句。

### 4.5.1 if标签

```xml
<select id="selectUsers" parameterType="com.example.mybatis.entity.User" resultType="com.example.mybatis.entity.User">
    SELECT id, username, email, created_at FROM users
    WHERE 1=1
    <if test="username != null and username != ''">
        AND username LIKE CONCAT('%', #{username}, '%')
    </if>
    <if test="email != null and email != ''">
        AND email = #{email}
    </if>
</select>
```

### 4.5.2 where标签

```xml
<select id="selectUsers" parameterType="com.example.mybatis.entity.User" resultType="com.example.mybatis.entity.User">
    SELECT id, username, email, created_at FROM users
    <where>
        <if test="username != null and username != ''">
            username LIKE CONCAT('%', #{username}, '%')
        </if>
        <if test="email != null and email != ''">
            AND email = #{email}
        </if>
    </where>
</select>
```

### 4.5.3 set标签

```xml
<update id="updateUser" parameterType="com.example.mybatis.entity.User">
    UPDATE users
    <set>
        <if test="username != null and username != ''">
            username = #{username},
        </if>
        <if test="email != null and email != ''">
            email = #{email},
        </if>
    </set>
    WHERE id = #{id}
</update>
```

### 4.5.4 foreach标签

```xml
<!-- 批量删除 -->
<delete id="deleteUsers" parameterType="list">
    DELETE FROM users WHERE id IN
    <foreach collection="list" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</delete>

<!-- 批量插入 -->
<insert id="insertUsers" parameterType="list">
    INSERT INTO users(username, email, created_at) VALUES
    <foreach collection="list" item="user" separator=",">
        (#{user.username}, #{user.email}, #{user.createdAt})
    </foreach>
</insert>
```

## 4.6 MyBatis分页插件PageHelper

PageHelper是MyBatis的一个非常实用的分页插件，使用起来非常简单。

### 4.6.1 基本使用

```java
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    public PageInfo<User> getUsersByPage(int pageNum, int pageSize) {
        // 开始分页
        PageHelper.startPage(pageNum, pageSize);
        
        // 查询数据
        List<User> users = userMapper.selectAllUsers();
        
        // 封装分页信息
        PageInfo<User> pageInfo = new PageInfo<>(users);
        
        return pageInfo;
    }
}
```

### 4.6.2 Controller中使用

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public PageInfo<User> getUsers(
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize) {
        return userService.getUsersByPage(pageNum, pageSize);
    }
}
```

## 4.7 MyBatis Generator代码生成器

MyBatis Generator是一个代码生成工具，可以根据数据库表自动生成实体类、Mapper接口和XML映射文件。

### 4.7.1 配置文件

创建`generatorConfig.xml`文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE generatorConfiguration
        PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
        "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">

<generatorConfiguration>
    <context id="DB2Tables" targetRuntime="MyBatis3">
        <commentGenerator>
            <property name="suppressAllComments" value="true"/>
        </commentGenerator>

        <jdbcConnection driverClass="com.mysql.cj.jdbc.Driver"
                        connectionURL="jdbc:mysql://localhost:3306/mybatis_demo"
                        userId="root"
                        password="root">
        </jdbcConnection>

        <javaTypeResolver>
            <property name="forceBigDecimals" value="false"/>
        </javaTypeResolver>

        <!-- 实体类生成位置 -->
        <javaModelGenerator targetPackage="com.example.mybatis.entity" targetProject="src/main/java">
            <property name="enableSubPackages" value="true"/>
            <property name="trimStrings" value="true"/>
        </javaModelGenerator>

        <!-- Mapper XML文件生成位置 -->
        <sqlMapGenerator targetPackage="mapper" targetProject="src/main/resources">
            <property name="enableSubPackages" value="true"/>
        </sqlMapGenerator>

        <!-- Mapper接口生成位置 -->
        <javaClientGenerator type="XMLMAPPER" targetPackage="com.example.mybatis.mapper" targetProject="src/main/java">
            <property name="enableSubPackages" value="true"/>
        </javaClientGenerator>

        <!-- 表映射配置 -->
        <table tableName="users" domainObjectName="User">
            <generatedKey column="id" sqlStatement="MySql" identity="true"/>
        </table>
    </context>
</generatorConfiguration>
```

### 4.7.2 运行生成器

在`pom.xml`中添加插件：

```xml
<plugin>
    <groupId>org.mybatis.generator</groupId>
    <artifactId>mybatis-generator-maven-plugin</artifactId>
    <version>1.4.0</version>
    <configuration>
        <configurationFile>src/main/resources/generatorConfig.xml</configurationFile>
        <overwrite>true</overwrite>
        <verbose>true</verbose>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.28</version>
        </dependency>
    </dependencies>
</plugin>
```

运行命令生成代码：

```bash
mvn mybatis-generator:generate
```

## 4.8 事务管理

在Spring Boot中使用MyBatis时，事务管理与使用JPA时类似。

### 4.8.1 声明式事务

```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private OrderMapper orderMapper;
    
    public void createUserAndOrder(User user, Order order) {
        // 插入用户
        userMapper.insertUser(user);
        
        // 设置用户ID
        order.setUserId(user.getId());
        
        // 插入订单
        orderMapper.insertOrder(order);
    }
}
```

### 4.8.2 编程式事务

```java
@Service
public class UserService {
    
    @Autowired
    private TransactionTemplate transactionTemplate;
    
    public void createUserAndOrder(User user, Order order) {
        transactionTemplate.execute(status -> {
            try {
                // 插入用户
                userMapper.insertUser(user);
                
                // 设置用户ID
                order.setUserId(user.getId());
                
                // 插入订单
                orderMapper.insertOrder(order);
                
                return null;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

## 4.9 最佳实践与性能优化

### 4.9.1 SQL优化

1. 避免使用`SELECT *`，只查询需要的字段
2. 合理使用索引
3. 避免在WHERE子句中对字段进行函数操作
4. 使用EXPLAIN分析SQL执行计划

### 4.9.2 MyBatis优化

1. 合理使用缓存
2. 避免N+1查询问题
3. 批量操作优化
4. 使用延迟加载

### 4.9.3 连接池优化

使用Druid连接池，并合理配置参数：

```properties
# 初始连接数
spring.datasource.druid.initial-size=5
# 最小连接数
spring.datasource.druid.min-idle=5
# 最大连接数
spring.datasource.druid.max-active=20
# 获取连接等待超时时间
spring.datasource.druid.max-wait=60000
# 连接池检测间隔
spring.datasource.druid.time-between-eviction-runs-millis=60000
# 连接在池中最小生存时间
spring.datasource.druid.min-evictable-idle-time-millis=300000
```

## 4.10 实践案例：用户管理系统

接下来我们通过一个完整的用户管理系统示例来演示MyBatis在Spring Boot中的使用。

### 4.10.1 项目结构

```
src/
├── main/
│   ├── java/com/example/mybatis/
│   │   ├── MyBatisApplication.java          # 应用启动类
│   │   ├── entity/                         # 实体类
│   │   │   └── User.java                   # 用户实体
│   │   ├── mapper/                         # Mapper接口
│   │   │   └── UserMapper.java             # 用户Mapper
│   │   ├── service/                        # 业务逻辑层
│   │   │   └── UserService.java            # 用户服务
│   │   └── controller/                     # 控制器层
│   │       └── UserController.java         # 用户控制器
│   └── resources/
│       ├── application.properties          # 应用配置文件
│       ├── mapper/                         # Mapper XML文件
│       │   └── UserMapper.xml              # 用户Mapper XML
│       └── sql/                            # SQL脚本
│           └── data.sql                    # 初始化数据
└── test/                                   # 测试代码
    └── java/com/example/mybatis/
        └── UserMapperTest.java             # Mapper测试
```

### 4.10.2 核心代码实现

由于篇幅限制，完整代码示例请参考配套代码章节。

## 总结

本章详细介绍了Spring Boot集成MyBatis的各种方式和最佳实践。MyBatis作为一个灵活的持久层框架，在需要精确控制SQL的场景下具有很大优势。通过合理使用MyBatis的各种特性，我们可以构建高性能、易维护的数据访问层。

在下一章中，我们将学习Spring Boot集成Spring Security实现安全控制。