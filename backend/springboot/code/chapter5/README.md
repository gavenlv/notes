# Spring Boot集成Spring Security示例项目

这是一个演示如何在Spring Boot应用程序中集成Spring Security的完整示例项目。该项目展示了用户注册、登录、JWT令牌生成与验证、基于角色的访问控制等功能。

## 功能特性

1. 用户注册和登录
2. JWT令牌认证
3. 基于角色的访问控制（RBAC）
4. 方法级安全控制
5. 密码加密存储
6. H2内存数据库用于演示

## 技术栈

- Spring Boot 2.7.0
- Spring Security
- Spring Data JPA
- H2 Database
- JSON Web Tokens (JWT)
- Maven

## 项目结构

```
src/
├── main/
│   ├── java/
│   │   └── com/example/security/
│   │       ├── Application.java          # 应用启动类
│   │       ├── config/                   # 配置类
│   │       ├── controller/               # 控制器
│   │       ├── model/                    # 实体类
│   │       ├── repository/               # 数据访问层
│   │       ├── service/                  # 业务逻辑层
│   │       ├── util/                     # 工具类
│   │       ├── filter/                   # 过滤器
│   │       └── payload/                  # 请求/响应数据传输对象
│   │           ├── request/
│   │           └── response/
│   └── resources/
│       ├── application.properties        # 应用配置
└── test/                                # 测试代码
```

## 快速开始

### 环境要求

- Java 11 或更高版本
- Maven 3.6 或更高版本

### 构建和运行

1. 克隆项目到本地：
   ```
   git clone <项目地址>
   ```

2. 进入项目目录：
   ```
   cd springboot-security-demo
   ```

3. 构建项目：
   ```
   mvn clean install
   ```

4. 运行应用：
   ```
   mvn spring-boot:run
   ```

   或者
   
   ```
   java -jar target/springboot-security-demo-1.0.0.jar
   ```

## API端点

### 认证相关

1. **用户注册**
   - URL: `POST /api/auth/signup`
   - 请求体:
     ```json
     {
       "username": "testuser",
       "email": "test@example.com",
       "password": "password",
       "roles": ["user"]  // 可选: user, admin, mod
     }
     ```

2. **用户登录**
   - URL: `POST /api/auth/signin`
   - 请求体:
     ```json
     {
       "username": "testuser",
       "password": "password"
     }
     ```

### 测试端点

1. **公开内容**
   - URL: `GET /api/test/all`
   - 无需认证

2. **用户内容**
   - URL: `GET /api/test/user`
   - 需要 USER, MODERATOR 或 ADMIN 角色

3. **版主内容**
   - URL: `GET /api/test/mod`
   - 需要 MODERATOR 角色

4. **管理员内容**
   - URL: `GET /api/test/admin`
   - 需要 ADMIN 角色

## 数据库

项目使用H2内存数据库，应用启动时会自动创建表结构。可以通过以下URL访问H2控制台：

- URL: `http://localhost:8080/h2-console`
- JDBC URL: `jdbc:h2:mem:testdb`
- 用户名: `sa`
- 密码: (留空)

## 配置说明

在 `application.properties` 文件中可以配置以下参数：

- `security.app.jwtSecret`: JWT签名密钥
- `security.app.jwtExpirationMs`: JWT过期时间（毫秒）
- 数据库连接信息
- 服务器端口等

## 测试

项目包含完整的单元测试和集成测试，可以通过以下命令运行：

```
mvn test
```

## 安全最佳实践

1. 使用BCrypt进行密码加密
2. 使用JWT进行无状态认证
3. 实现基于角色的访问控制
4. 启用方法级安全控制
5. 防止跨站请求伪造（CSRF）攻击
6. 设置适当的CORS策略

## 扩展建议

1. 集成OAuth2支持第三方登录
2. 添加验证码机制防止暴力破解
3. 实现账户锁定机制
4. 添加邮件验证功能
5. 集成Redis缓存提高性能
6. 添加API限流功能

## 贡献

欢迎提交Issue和Pull Request来改进这个示例项目。