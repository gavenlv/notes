# 第四章：Spring Boot集成MyBatis - 示例代码

本示例项目演示了如何在Spring Boot中集成MyBatis，包括基本的CRUD操作、分页查询、动态SQL、事务管理等功能。

## 项目结构

```
src/
├── main/
│   ├── java/com/example/mybatis/
│   │   ├── MyBatisApplication.java          # 应用启动类
│   │   ├── entity/                         # 实体类
│   │   │   ├── User.java                   # 用户实体
│   │   │   └── Order.java                  # 订单实体
│   │   ├── mapper/                         # Mapper接口
│   │   │   ├── UserMapper.java             # 用户Mapper接口
│   │   │   └── OrderMapper.java            # 订单Mapper接口
│   │   ├── service/                        # 业务逻辑层
│   │   │   ├── UserService.java            # 用户服务
│   │   │   └── OrderService.java           # 订单服务
│   │   └── controller/                     # 控制器层
│   │       ├── UserController.java         # 用户控制器
│   │       └── OrderController.java        # 订单控制器
│   └── resources/
│       ├── application.properties          # 应用配置文件
│       ├── mapper/                         # Mapper XML文件
│       │   ├── UserMapper.xml              # 用户Mapper XML
│       │   └── OrderMapper.xml             # 订单Mapper XML
│       ├── sql/                            # SQL脚本
│       │   ├── schema.sql                  # 数据库表结构
│       │   └── data.sql                    # 初始化数据
│       └── generatorConfig.xml             # MyBatis Generator配置
└── test/                                   # 测试代码
    └── java/com/example/mybatis/
        ├── mapper/
        │   └── UserMapperTest.java         # Mapper测试
        └── service/
            └── UserServiceTest.java        # Service测试
```

## 功能特性

1. **基本CRUD操作**：用户和订单的增删改查
2. **分页查询**：集成PageHelper实现分页功能
3. **动态SQL**：根据条件动态生成SQL语句
4. **事务管理**：使用Spring的声明式事务
5. **代码生成**：使用MyBatis Generator自动生成代码
6. **连接池**：集成Druid连接池
7. **单元测试**：包含Mapper和Service层的测试用例

## 运行环境

- JDK 11+
- Maven 3.6+
- MySQL 5.7+

## 数据库配置

在`application.properties`中配置数据库连接信息：

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/mybatis_demo?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
spring.datasource.username=root
spring.datasource.password=root
```

## 数据库初始化

项目包含两个SQL脚本用于初始化数据库：

1. `schema.sql`：创建表结构
2. `data.sql`：插入初始数据

## API接口

### 用户管理接口

- GET `/api/users` - 查询所有用户
- GET `/api/users/{id}` - 根据ID查询用户
- GET `/api/users/page` - 分页查询用户
- GET `/api/users/search?username={username}` - 根据用户名模糊查询
- POST `/api/users` - 创建用户
- PUT `/api/users/{id}` - 更新用户
- DELETE `/api/users/{id}` - 删除用户
- POST `/api/users/batch` - 批量创建用户

### 订单管理接口

- GET `/api/orders` - 查询所有订单
- GET `/api/orders/{id}` - 根据ID查询订单
- GET `/api/orders/user/{userId}` - 根据用户ID查询订单
- POST `/api/orders` - 创建订单
- PUT `/api/orders/{id}` - 更新订单
- DELETE `/api/orders/{id}` - 删除订单

## 运行项目

1. 创建数据库：
   ```sql
   CREATE DATABASE mybatis_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. 修改`application.properties`中的数据库连接配置

3. 运行项目：
   ```bash
   mvn spring-boot:run
   ```

4. 访问API：
   - http://localhost:8080/api/users
   - http://localhost:8080/api/orders

## 测试

运行测试：
```bash
mvn test
```

## MyBatis Generator使用

生成代码：
```bash
mvn mybatis-generator:generate
```

## 许可证

MIT License