# 第三章：Spring Boot Web开发详解

在这一章中，我们将深入探讨Spring Boot Web开发的核心概念和技术。我们将学习如何构建RESTful API、处理HTTP请求、使用不同的视图技术（如Thymeleaf和Vue.js）以及如何进行Web应用的安全配置。

## 目录

1. [RESTful API设计](#1-restful-api设计)
2. [控制器详解](#2-控制器详解)
3. [请求处理](#3-请求处理)
4. [视图技术](#4-视图技术)
5. [异常处理](#5-异常处理)
6. [拦截器和过滤器](#6-拦截器和过滤器)
7. [文件上传](#7-文件上传)
8. [最佳实践](#8-最佳实践)
9. [实践案例](#9-实践案例)

---

## 1. RESTful API设计

### 1.1 什么是RESTful API

REST（Representational State Transfer）是一种软件架构风格，它定义了一组约束和属性，用于创建Web服务。RESTful API遵循这些约束，使得客户端和服务器之间的通信更加简单和可预测。

### 1.2 设计原则

- 使用HTTP动词表示操作类型（GET、POST、PUT、DELETE）
- 使用名词表示资源（如/users而不是/getUsers）
- 使用HTTP状态码表示操作结果
- 支持多种数据格式（JSON、XML）

### 1.3 示例

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> getAllUsers() {
        // 返回所有用户
    }
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        // 根据ID返回用户
    }
    
    @PostMapping
    public User createUser(@RequestBody User user) {
        // 创建新用户
    }
    
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        // 更新用户信息
    }
    
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        // 删除用户
    }
}
```

## 2. 控制器详解

### 2.1 @RestController vs @Controller

- `@RestController` = `@Controller` + `@ResponseBody`
- `@Controller`用于返回视图名称
- `@RestController`用于直接返回数据（JSON/XML）

### 2.2 请求映射注解

- `@RequestMapping`：通用映射注解
- `@GetMapping`：映射GET请求
- `@PostMapping`：映射POST请求
- `@PutMapping`：映射PUT请求
- `@DeleteMapping`：映射DELETE请求

### 2.3 参数绑定

```java
@RestController
public class ExampleController {
    
    // 路径变量
    @GetMapping("/users/{id}")
    public User getUserById(@PathVariable Long id) {
        // ...
    }
    
    // 请求参数
    @GetMapping("/users")
    public List<User> getUsersByName(@RequestParam String name) {
        // ...
    }
    
    // 请求体
    @PostMapping("/users")
    public User createUser(@RequestBody User user) {
        // ...
    }
    
    // 请求头
    @GetMapping("/info")
    public String getInfo(@RequestHeader("Authorization") String token) {
        // ...
    }
}
```

## 3. 请求处理

### 3.1 数据验证

使用Hibernate Validator进行数据验证：

```java
public class User {
    @NotBlank(message = "用户名不能为空")
    private String name;
    
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @Min(value = 18, message = "年龄不能小于18岁")
    private Integer age;
    
    // getters and setters
}
```

在控制器中使用：

```java
@PostMapping("/users")
public ResponseEntity<User> createUser(@Valid @RequestBody User user, BindingResult result) {
    if (result.hasErrors()) {
        // 处理验证错误
        return ResponseEntity.badRequest().build();
    }
    // 保存用户
    return ResponseEntity.ok(user);
}
```

### 3.2 文件上传

```java
@PostMapping("/upload")
public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) {
    if (file.isEmpty()) {
        return ResponseEntity.badRequest().body("文件为空");
    }
    
    try {
        // 保存文件
        String fileName = file.getOriginalFilename();
        Path path = Paths.get("uploads/" + fileName);
        Files.write(path, file.getBytes());
        
        return ResponseEntity.ok("文件上传成功: " + fileName);
    } catch (IOException e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("文件上传失败");
    }
}
```

## 4. 视图技术

### 4.1 Thymeleaf模板引擎

添加依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

控制器：

```java
@Controller
public class HomeController {
    
    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("message", "欢迎来到Spring Boot!");
        return "index"; // 返回视图名称
    }
}
```

模板文件（src/main/resources/templates/index.html）：

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>首页</title>
</head>
<body>
    <h1 th:text="${message}">默认消息</h1>
</body>
</html>
```

### 4.2 Vue.js前端集成

创建Vue.js项目：

```bash
npm create vue@latest my-vue-app
cd my-vue-app
npm install
npm run dev
```

Spring Boot配置CORS支持：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:5173") // Vue.js默认端口
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowCredentials(true);
    }
}
```

## 5. 异常处理

### 5.1 全局异常处理器

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<String> handleUserNotFound(UserNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(ex.getMessage());
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleGenericException(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("内部服务器错误");
    }
}
```

### 5.2 自定义异常

```java
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}
```

## 6. 拦截器和过滤器

### 6.1 拦截器

```java
@Component
public class LoggingInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        System.out.println("请求URL: " + request.getRequestURI());
        return true; // 继续处理请求
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
        System.out.println("请求完成");
    }
}
```

注册拦截器：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Autowired
    private LoggingInterceptor loggingInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loggingInterceptor)
                .addPathPatterns("/api/**"); // 拦截API请求
    }
}
```

### 6.2 过滤器

```java
@Component
public class RequestLoggingFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        System.out.println("收到请求: " + httpRequest.getRequestURI());
        
        chain.doFilter(request, response);
        
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        System.out.println("响应状态: " + httpResponse.getStatus());
    }
}
```

## 7. 文件上传

### 7.1 配置文件上传

application.properties:

```properties
# 文件上传配置
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB
```

### 7.2 文件上传控制器

```java
@RestController
public class FileUploadController {
    
    @Value("${upload.path}")
    private String uploadPath;
    
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("请选择文件");
        }
        
        try {
            // 创建上传目录
            Path uploadDir = Paths.get(uploadPath);
            if (!Files.exists(uploadDir)) {
                Files.createDirectories(uploadDir);
            }
            
            // 保存文件
            String fileName = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
            Path filePath = uploadDir.resolve(fileName);
            Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
            
            return ResponseEntity.ok("文件上传成功: " + fileName);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("文件上传失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/download/{fileName}")
    public ResponseEntity<Resource> downloadFile(@PathVariable String fileName) {
        try {
            Path filePath = Paths.get(uploadPath).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());
            
            if (resource.exists()) {
                return ResponseEntity.ok()
                        .contentType(MediaType.APPLICATION_OCTET_STREAM)
                        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (MalformedURLException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
```

## 8. 最佳实践

### 8.1 API版本控制

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserV1Controller {
    // v1版本API
}

@RestController
@RequestMapping("/api/v2/users")
public class UserV2Controller {
    // v2版本API
}
```

### 8.2 统一响应格式

```java
public class ApiResponse<T> {
    private int code;
    private String message;
    private T data;
    
    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> response = new ApiResponse<>();
        response.code = 200;
        response.message = "成功";
        response.data = data;
        return response;
    }
    
    public static <T> ApiResponse<T> error(int code, String message) {
        ApiResponse<T> response = new ApiResponse<>();
        response.code = code;
        response.message = message;
        return response;
    }
    
    // getters and setters
}
```

使用统一响应格式：

```java
@GetMapping("/users")
public ApiResponse<List<User>> getAllUsers() {
    List<User> users = userService.getAllUsers();
    return ApiResponse.success(users);
}
```

### 8.3 日志记录

```java
@RestController
@RequestMapping("/api/users")
@Slf4j
public class UserController {
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        log.info("获取用户信息，用户ID: {}", id);
        User user = userService.getUserById(id);
        log.info("成功获取用户信息，用户: {}", user);
        return user;
    }
}
```

## 9. 实践案例

让我们创建一个完整的博客系统作为实践案例。

### 9.1 项目结构

```
blog-system/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/blog/
│   │   │       ├── BlogApplication.java
│   │   │       ├── controller/
│   │   │       │   ├── PostController.java
│   │   │       │   └── CommentController.java
│   │   │       ├── service/
│   │   │       │   ├── PostService.java
│   │   │       │   └── CommentService.java
│   │   │       ├── repository/
│   │   │       │   ├── PostRepository.java
│   │   │       │   └── CommentRepository.java
│   │   │       ├── entity/
│   │   │       │   ├── Post.java
│   │   │       │   └── Comment.java
│   │   │       └── exception/
│   │   │           ├── PostNotFoundException.java
│   │   │           └── GlobalExceptionHandler.java
│   │   └── resources/
│   │       ├── application.properties
│   │       └── templates/
│   └── test/
│       └── java/
│           └── com/example/blog/
└── pom.xml
```

### 9.2 核心代码

实体类：

```java
@Entity
@Table(name = "posts")
public class Post {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "标题不能为空")
    private String title;
    
    @NotBlank(message = "内容不能为空")
    @Column(length = 10000)
    private String content;
    
    private LocalDateTime createdAt;
    
    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL)
    private List<Comment> comments = new ArrayList<>();
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
    
    // constructors, getters and setters
}

@Entity
@Table(name = "comments")
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "评论内容不能为空")
    private String content;
    
    private LocalDateTime createdAt;
    
    @ManyToOne
    @JoinColumn(name = "post_id")
    private Post post;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
    
    // constructors, getters and setters
}
```

仓库接口：

```java
@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    List<Post> findByTitleContainingIgnoreCase(String title);
}

@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {
    List<Comment> findByPostId(Long postId);
}
```

服务类：

```java
@Service
@Transactional
public class PostService {
    
    @Autowired
    private PostRepository postRepository;
    
    public List<Post> getAllPosts() {
        return postRepository.findAll();
    }
    
    public Post getPostById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new PostNotFoundException("文章未找到，ID: " + id));
    }
    
    public Post createPost(Post post) {
        return postRepository.save(post);
    }
    
    public Post updatePost(Long id, Post postDetails) {
        Post post = getPostById(id);
        post.setTitle(postDetails.getTitle());
        post.setContent(postDetails.getContent());
        return postRepository.save(post);
    }
    
    public void deletePost(Long id) {
        Post post = getPostById(id);
        postRepository.delete(post);
    }
    
    public List<Post> searchPosts(String keyword) {
        return postRepository.findByTitleContainingIgnoreCase(keyword);
    }
}

@Service
@Transactional
public class CommentService {
    
    @Autowired
    private CommentRepository commentRepository;
    
    @Autowired
    private PostService postService;
    
    public List<Comment> getCommentsByPostId(Long postId) {
        return commentRepository.findByPostId(postId);
    }
    
    public Comment createComment(Long postId, Comment comment) {
        Post post = postService.getPostById(postId);
        comment.setPost(post);
        return commentRepository.save(comment);
    }
    
    public void deleteComment(Long id) {
        commentRepository.deleteById(id);
    }
}
```

控制器：

```java
@RestController
@RequestMapping("/api/posts")
@Slf4j
public class PostController {
    
    @Autowired
    private PostService postService;
    
    @GetMapping
    public ApiResponse<List<Post>> getAllPosts(@RequestParam(required = false) String search) {
        log.info("获取所有文章，搜索关键词: {}", search);
        List<Post> posts = search != null ? postService.searchPosts(search) : postService.getAllPosts();
        return ApiResponse.success(posts);
    }
    
    @GetMapping("/{id}")
    public ApiResponse<Post> getPostById(@PathVariable Long id) {
        log.info("获取文章，ID: {}", id);
        Post post = postService.getPostById(id);
        return ApiResponse.success(post);
    }
    
    @PostMapping
    public ApiResponse<Post> createPost(@Valid @RequestBody Post post) {
        log.info("创建文章，标题: {}", post.getTitle());
        Post createdPost = postService.createPost(post);
        return ApiResponse.success(createdPost);
    }
    
    @PutMapping("/{id}")
    public ApiResponse<Post> updatePost(@PathVariable Long id, @Valid @RequestBody Post postDetails) {
        log.info("更新文章，ID: {}", id);
        Post updatedPost = postService.updatePost(id, postDetails);
        return ApiResponse.success(updatedPost);
    }
    
    @DeleteMapping("/{id}")
    public ApiResponse<Void> deletePost(@PathVariable Long id) {
        log.info("删除文章，ID: {}", id);
        postService.deletePost(id);
        return ApiResponse.success(null);
    }
}

@RestController
@RequestMapping("/api/comments")
@Slf4j
public class CommentController {
    
    @Autowired
    private CommentService commentService;
    
    @GetMapping("/post/{postId}")
    public ApiResponse<List<Comment>> getCommentsByPostId(@PathVariable Long postId) {
        log.info("获取文章评论，文章ID: {}", postId);
        List<Comment> comments = commentService.getCommentsByPostId(postId);
        return ApiResponse.success(comments);
    }
    
    @PostMapping("/post/{postId}")
    public ApiResponse<Comment> createComment(@PathVariable Long postId, @Valid @RequestBody Comment comment) {
        log.info("创建评论，文章ID: {}", postId);
        Comment createdComment = commentService.createComment(postId, comment);
        return ApiResponse.success(createdComment);
    }
    
    @DeleteMapping("/{id}")
    public ApiResponse<Void> deleteComment(@PathVariable Long id) {
        log.info("删除评论，ID: {}", id);
        commentService.deleteComment(id);
        return ApiResponse.success(null);
    }
}
```

全局异常处理：

```java
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(PostNotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handlePostNotFound(PostNotFoundException ex) {
        log.error("文章未找到: {}", ex.getMessage());
        ApiResponse<Void> response = ApiResponse.error(404, ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationExceptions(MethodArgumentNotValidException ex) {
        StringBuilder errors = new StringBuilder();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.append(fieldName).append(": ").append(errorMessage).append("; ");
        });
        
        log.error("数据验证失败: {}", errors.toString());
        ApiResponse<Void> response = ApiResponse.error(400, "数据验证失败: " + errors.toString());
        return ResponseEntity.badRequest().body(response);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGenericException(Exception ex) {
        log.error("服务器内部错误", ex);
        ApiResponse<Void> response = ApiResponse.error(500, "服务器内部错误");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}
```

配置文件（application.properties）：

```properties
# 数据库配置
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA配置
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# 文件上传配置
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB

# 日志配置
logging.level.com.example.blog=DEBUG
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n

# 服务器端口
server.port=8080
```

这个完整的博客系统示例展示了：

1. RESTful API的设计和实现
2. 数据验证和异常处理
3. JPA实体关系映射
4. 统一响应格式
5. 日志记录
6. CRUD操作的完整实现

通过这个案例，你可以看到Spring Boot在Web开发中的强大功能和灵活性。

## 总结

在本章中，我们深入探讨了Spring Boot Web开发的各个方面：

1. 学习了RESTful API的设计原则和实现方式
2. 掌握了控制器的使用和请求处理技巧
3. 了解了不同视图技术的集成方法
4. 学会了异常处理和拦截器的使用
5. 实现了文件上传功能
6. 通过实际案例巩固了所学知识

下一章我们将探讨Spring Boot的数据持久化技术，包括JPA、MyBatis等ORM框架的使用。