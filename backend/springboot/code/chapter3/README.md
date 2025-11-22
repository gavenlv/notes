# 第三章：Spring Boot Web开发详解 - 示例代码

本目录包含了《Spring Boot教程》第三章的完整示例代码，实现了一个简单的博客系统，展示了Spring Boot在Web开发中的各种特性和最佳实践。

## 项目结构

```
src/
├── main/
│   ├── java/com/example/blog/
│   │   ├── BlogApplication.java          # 应用启动类
│   │   ├── entity/                       # 实体类
│   │   │   ├── Post.java                 # 文章实体
│   │   │   └── Comment.java              # 评论实体
│   │   ├── repository/                   # 数据访问层
│   │   │   ├── PostRepository.java       # 文章Repository
│   │   │   └── CommentRepository.java    # 评论Repository
│   │   ├── service/                      # 业务逻辑层
│   │   │   ├── PostService.java          # 文章服务
│   │   │   └── CommentService.java       # 评论服务
│   │   └── controller/                   # 控制器层
│   │       ├── PostController.java       # REST API控制器（文章）
│   │       ├── CommentController.java    # REST API控制器（评论）
│   │       └── WebController.java        # Web页面控制器
│   └── resources/
│       ├── application.properties        # 应用配置文件
│       ├── data.sql                      # 初始化数据
│       └── templates/                    # Thymeleaf模板
│           ├── index.html                # 首页模板
│           └── post.html                 # 文章详情页模板
└── test/                                 # 测试代码
    └── java/com/example/blog/
        ├── PostRepositoryTest.java       # Repository层测试
        └── PostControllerIntegrationTest.java  # Controller集成测试
```

## 功能特性

1. **RESTful API**
   - 文章的增删改查接口
   - 评论的增删查接口
   - 文章搜索功能

2. **Web页面**
   - 博客首页展示文章列表
   - 文章详情页展示文章内容和评论
   - 评论提交功能
   - 文章搜索功能

3. **数据存储**
   - 使用H2内存数据库
   - JPA/Hibernate ORM映射
   - 自动建表和初始化数据

4. **模板引擎**
   - Thymeleaf模板渲染
   - 动态页面内容展示

## 运行项目

1. 确保已安装JDK 11+和Maven
2. 在项目根目录执行以下命令：

```bash
mvn spring-boot:run
```

或者打包后运行：

```bash
mvn clean package
java -jar target/chapter3-0.0.1-SNAPSHOT.jar
```

3. 访问应用：
   - Web界面: http://localhost:8080/
   - REST API: http://localhost:8080/api/posts
   - H2控制台: http://localhost:8080/h2-console (JDBC URL: jdbc:h2:mem:testdb)

## API接口测试

### 文章相关接口

- `GET /api/posts` - 获取所有文章
- `GET /api/posts/{id}` - 根据ID获取文章
- `POST /api/posts` - 创建新文章
- `PUT /api/posts/{id}` - 更新文章
- `DELETE /api/posts/{id}` - 删除文章
- `GET /api/posts/search?keyword={keyword}` - 搜索文章

### 评论相关接口

- `GET /api/comments/post/{postId}` - 获取某篇文章的所有评论
- `POST /api/comments` - 创建新评论
- `DELETE /api/comments/{id}` - 删除评论

## 测试

项目包含了Repository层的单元测试和Controller层的集成测试，可以通过以下命令运行：

```bash
mvn test
```

## 相关文档

详细的技术说明请参考主目录下的 [3-Web开发详解.md](../3-Web开发详解.md) 文档。