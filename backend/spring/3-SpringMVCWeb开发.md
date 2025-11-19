# 第3章 Spring MVC Web开发

## 本章概述

本章将深入探讨Spring MVC框架，这是Spring生态系统中用于构建Web应用程序的核心模块。我们将学习Spring MVC的架构、核心组件、请求处理流程以及如何使用它来构建功能丰富的Web应用。

## 目录

1. [Spring MVC简介](#spring-mvc简介)
2. [Spring MVC架构](#spring-mvc架构)
3. [核心组件](#核心组件)
4. [请求处理流程](#请求处理流程)
5. [控制器（Controller）](#控制器controller)
6. [数据绑定和验证](#数据绑定和验证)
7. [视图解析](#视图解析)
8. [异常处理](#异常处理)
9. [拦截器](#拦截器)
10. [文件上传](#文件上传)
11. [RESTful Web服务](#restful-web服务)
12. [配置Spring MVC](#配置spring-mvc)
13. [最佳实践](#最佳实践)

## Spring MVC简介

Spring MVC是Spring框架的一部分，专门用于构建Web应用程序。它遵循Model-View-Controller（MVC）设计模式，将应用程序的不同方面（输入逻辑、业务逻辑和UI逻辑）分离，从而提供松耦合的架构。

### MVC设计模式

MVC模式将应用程序分为三个核心组件：

1. **Model（模型）**：封装应用程序的数据和业务逻辑
2. **View（视图）**：负责渲染用户界面
3. **Controller（控制器）**：处理用户请求并协调模型和视图

### Spring MVC的优势

1. **清晰的角色划分**：每个组件都有明确的职责
2. **灵活的配置**：支持基于注解和XML的配置
3. **强大的数据绑定**：自动将请求参数绑定到对象
4. **丰富的视图技术**：支持JSP、Thymeleaf、FreeMarker等多种视图技术
5. **易于测试**：支持单元测试和集成测试
6. **RESTful支持**：原生支持构建RESTful Web服务

## Spring MVC架构

Spring MVC的架构基于前端控制器模式，其中DispatcherServlet作为中央处理器协调整个请求处理流程。

### 架构图

```
Client Request
       ↓
┌─────────────────────┐
│   DispatcherServlet │←→ HandlerMapping
└─────────────────────┘         ↓
       ↓                ┌─────────────────┐
┌─────────────────────┐ │  Controller     │
│   HandlerAdapter    │←→ HandlerExecutionChain
└─────────────────────┘ └─────────────────┘
       ↓                        ↓
┌─────────────────────┐ ┌─────────────────┐
│   ModelAndView      │ │  Model & View   │
└─────────────────────┘ └─────────────────┘
       ↓                        ↓
┌─────────────────────┐ ┌─────────────────┐
│   ViewResolver      │ │  View Template  │
└─────────────────────┘ └─────────────────┘
       ↓                        ↓
┌─────────────────────────────────────────┐
│              View                       │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│           Response to Client            │
└─────────────────────────────────────────┘
```

### 组件说明

1. **DispatcherServlet**：前端控制器，接收所有请求并分发给相应的处理器
2. **HandlerMapping**：根据请求URL查找对应的处理器
3. **Controller**：处理请求并返回ModelAndView
4. **ModelAndView**：包含模型数据和视图信息
5. **ViewResolver**：解析视图名称并返回具体的视图实现
6. **View**：负责渲染最终的响应内容

## 核心组件

### 1. DispatcherServlet

DispatcherServlet是Spring MVC的核心，它是一个Servlet，继承自HttpServlet基类。

```java
public class DispatcherServlet extends FrameworkServlet {
    // 处理HTTP请求的核心方法
}
```

在web.xml中配置：

```xml
<servlet>
    <servlet-name>dispatcher</servlet-name>
    <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
    <init-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>/WEB-INF/dispatcher-servlet.xml</param-value>
    </init-param>
    <load-on-startup>1</load-on-startup>
</servlet>

<servlet-mapping>
    <servlet-name>dispatcher</servlet-name>
    <url-pattern>/</url-pattern>
</servlet-mapping>
```

### 2. HandlerMapping

HandlerMapping负责根据请求URL找到对应的处理器（Controller）。

```java
// 基于注解的HandlerMapping
@RequestMapping("/users")
public class UserController {
    
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        // 处理逻辑
    }
}
```

### 3. HandlerAdapter

HandlerAdapter负责调用处理器方法并处理返回值。

```java
// SimpleControllerHandlerAdapter处理实现了Controller接口的处理器
public class SimpleControllerHandlerAdapter implements HandlerAdapter {
    public ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        return ((Controller) handler).handleRequest(request, response);
    }
}
```

### 4. ViewResolver

ViewResolver负责解析视图名称并返回具体的视图实现。

```java
// InternalResourceViewResolver配置
@Bean
public ViewResolver viewResolver() {
    InternalResourceViewResolver resolver = new InternalResourceViewResolver();
    resolver.setPrefix("/WEB-INF/views/");
    resolver.setSuffix(".jsp");
    return resolver;
}
```

## 请求处理流程

Spring MVC的请求处理流程如下：

1. 客户端发送请求到DispatcherServlet
2. DispatcherServlet查询HandlerMapping确定请求对应的处理器
3. HandlerMapping返回处理器执行链（HandlerExecutionChain）
4. DispatcherServlet调用HandlerAdapter执行处理器
5. 处理器执行完成后返回ModelAndView
6. DispatcherServlet查询ViewResolver解析视图
7. ViewResolver返回具体的View实现
8. DispatcherServlet将模型数据传递给View进行渲染
9. View渲染完成后返回响应给客户端

### 流程图示

```
Client → DispatcherServlet → HandlerMapping → HandlerExecutionChain
                              ↑              ↓
                         HandlerAdapter → Controller → ModelAndView
                              ↑              ↓
                         ViewResolver → View → Response
```

## 控制器（Controller）

控制器是Spring MVC中处理请求的核心组件。在现代Spring MVC中，主要使用基于注解的控制器。

### 基本控制器示例

```java
@Controller
@RequestMapping("/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    // GET /users
    @GetMapping
    public String listUsers(Model model) {
        List<User> users = userService.findAll();
        model.addAttribute("users", users);
        return "user/list";
    }
    
    // GET /users/1
    @GetMapping("/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id);
        model.addAttribute("user", user);
        return "user/detail";
    }
    
    // GET /users/new
    @GetMapping("/new")
    public String newUserForm(Model model) {
        model.addAttribute("user", new User());
        return "user/form";
    }
    
    // POST /users
    @PostMapping
    public String createUser(@ModelAttribute User user, RedirectAttributes redirectAttributes) {
        User savedUser = userService.save(user);
        redirectAttributes.addFlashAttribute("message", "User created successfully");
        return "redirect:/users/" + savedUser.getId();
    }
}
```

### 常用注解

#### 请求映射注解

```java
@RestController
@RequestMapping("/api/users")
public class UserRestController {
    
    // GET /api/users
    @GetMapping
    public List<User> getUsers() {
        return userService.findAll();
    }
    
    // POST /api/users
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }
    
    // PUT /api/users/1
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        return userService.update(user);
    }
    
    // DELETE /api/users/1
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

#### 参数绑定注解

```java
@GetMapping("/search")
public String searchUsers(
    @RequestParam(required = false) String name,
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "10") int size,
    @RequestHeader("User-Agent") String userAgent,
    @CookieValue("JSESSIONID") String sessionId,
    Model model) {
    
    Page<User> users = userService.findByName(name, PageRequest.of(page, size));
    model.addAttribute("users", users);
    return "user/search";
}
```

## 数据绑定和验证

Spring MVC提供了强大的数据绑定和验证机制。

### 数据绑定

```java
@PostMapping("/users")
public String createUser(@ModelAttribute("user") User user, BindingResult result) {
    if (result.hasErrors()) {
        return "user/form";
    }
    userService.save(user);
    return "redirect:/users";
}
```

### 验证

首先在实体类上添加验证注解：

```java
public class User {
    @NotNull(message = "Name is required")
    @Size(min = 2, max = 50, message = "Name must be between 2 and 50 characters")
    private String name;
    
    @NotNull(message = "Email is required")
    @Email(message = "Email should be valid")
    private String email;
    
    @Min(value = 18, message = "Age should be greater than 18")
    private Integer age;
    
    // getters and setters
}
```

在控制器中进行验证：

```java
@PostMapping("/users")
public String createUser(@Valid @ModelAttribute("user") User user, BindingResult result) {
    if (result.hasErrors()) {
        return "user/form";
    }
    userService.save(user);
    return "redirect:/users";
}
```

### 自定义验证器

```java
@Component
public class UserValidator implements Validator {
    
    @Override
    public boolean supports(Class<?> clazz) {
        return User.class.equals(clazz);
    }
    
    @Override
    public void validate(Object target, Errors errors) {
        User user = (User) target;
        if (user.getEmail() != null && user.getEmail().contains("admin")) {
            errors.rejectValue("email", "email.admin", "Email cannot contain 'admin'");
        }
    }
}

// 在控制器中使用
@InitBinder
protected void initBinder(WebDataBinder binder) {
    binder.addValidators(new UserValidator());
}
```

## 视图解析

Spring MVC支持多种视图技术，包括JSP、Thymeleaf、FreeMarker等。

### JSP视图

配置ViewResolver：

```java
@Configuration
@EnableWebMvc
public class WebConfig implements WebMvcConfigurer {
    
    @Bean
    public ViewResolver viewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        return resolver;
    }
}
```

JSP页面示例：

```jsp
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<head>
    <title>User List</title>
</head>
<body>
    <h1>Users</h1>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
            </tr>
        </thead>
        <tbody>
            <c:forEach items="${users}" var="user">
                <tr>
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                </tr>
            </c:forEach>
        </tbody>
    </table>
</body>
</html>
```

### Thymeleaf视图

添加依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

Thymeleaf模板示例：

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>User List</title>
</head>
<body>
    <h1>Users</h1>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
            </tr>
        </thead>
        <tbody>
            <tr th:each="user : ${users}">
                <td th:text="${user.id}">ID</td>
                <td th:text="${user.name}">Name</td>
                <td th:text="${user.email}">Email</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
```

## 异常处理

Spring MVC提供了多种异常处理机制。

### 全局异常处理器

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException ex) {
        ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        ErrorResponse error = new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ValidationErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex) {
        ValidationErrorResponse errorResponse = new ValidationErrorResponse();
        ex.getBindingResult().getFieldErrors().forEach(error -> 
            errorResponse.addFieldError(error.getField(), error.getDefaultMessage()));
        return ResponseEntity.badRequest().body(errorResponse);
    }
}
```

### 局部异常处理

```java
@Controller
public class UserController {
    
    @ExceptionHandler(UserNotFoundException.class)
    public String handleUserNotFound(UserNotFoundException ex, Model model) {
        model.addAttribute("error", ex.getMessage());
        return "error/user-not-found";
    }
    
    @GetMapping("/users/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id);
        if (user == null) {
            throw new UserNotFoundException("User not found with id: " + id);
        }
        model.addAttribute("user", user);
        return "user/detail";
    }
}
```

## 拦截器

拦截器用于在请求处理前后执行特定逻辑。

### 创建拦截器

```java
@Component
public class LoggingInterceptor implements HandlerInterceptor {
    
    private static final Logger logger = LoggerFactory.getLogger(LoggingInterceptor.class);
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        logger.info("Request URL: {} | Method: {}", request.getRequestURL(), request.getMethod());
        request.setAttribute("startTime", System.currentTimeMillis());
        return true; // 返回true继续处理，返回false中断处理
    }
    
    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
        long startTime = (Long) request.getAttribute("startTime");
        long endTime = System.currentTimeMillis();
        logger.info("Request processed in {} ms", (endTime - startTime));
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
        if (ex != null) {
            logger.error("Request failed with exception", ex);
        }
    }
}
```

### 注册拦截器

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Autowired
    private LoggingInterceptor loggingInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loggingInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/public/**");
    }
}
```

## 文件上传

Spring MVC提供了简单的文件上传支持。

### 配置文件上传

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Bean
    public MultipartResolver multipartResolver() {
        CommonsMultipartResolver resolver = new CommonsMultipartResolver();
        resolver.setMaxUploadSize(10485760); // 10MB
        resolver.setMaxInMemorySize(1048576); // 1MB
        return resolver;
    }
}
```

### 处理文件上传

```java
@Controller
public class FileUploadController {
    
    @PostMapping("/upload")
    public String handleFileUpload(@RequestParam("file") MultipartFile file, 
                                  RedirectAttributes redirectAttributes) {
        if (file.isEmpty()) {
            redirectAttributes.addFlashAttribute("message", "Please select a file to upload");
            return "redirect:/uploadStatus";
        }
        
        try {
            // 保存文件
            byte[] bytes = file.getBytes();
            Path path = Paths.get("uploads/" + file.getOriginalFilename());
            Files.write(path, bytes);
            
            redirectAttributes.addFlashAttribute("message", 
                "You successfully uploaded '" + file.getOriginalFilename() + "'");
        } catch (IOException e) {
            redirectAttributes.addFlashAttribute("message", "Failed to upload '" + file.getOriginalFilename() + "'");
        }
        
        return "redirect:/uploadStatus";
    }
    
    @GetMapping("/upload")
    public String uploadForm() {
        return "uploadForm";
    }
    
    @GetMapping("/uploadStatus")
    public String uploadStatus() {
        return "uploadStatus";
    }
}
```

### HTML表单

```html
<!DOCTYPE html>
<html>
<body>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <table>
            <tr>
                <td><input type="file" name="file" /></td>
            </tr>
            <tr>
                <td><input type="submit" value="Upload" /></td>
            </tr>
        </table>
    </form>
</body>
</html>
```

## RESTful Web服务

Spring MVC非常适合构建RESTful Web服务。

### REST控制器示例

```java
@RestController
@RequestMapping("/api/users")
public class UserRestController {
    
    @Autowired
    private UserService userService;
    
    // GET /api/users
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.findAll();
        return ResponseEntity.ok(users);
    }
    
    // GET /api/users/1
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        return userService.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    // POST /api/users
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        User savedUser = userService.save(user);
        URI location = ServletUriComponentsBuilder
                .fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(savedUser.getId())
                .toUri();
        return ResponseEntity.created(location).body(savedUser);
    }
    
    // PUT /api/users/1
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @Valid @RequestBody User user) {
        if (!userService.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        user.setId(id);
        User updatedUser = userService.save(user);
        return ResponseEntity.ok(updatedUser);
    }
    
    // DELETE /api/users/1
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (!userService.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        userService.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

### HATEOAS支持

```java
// 添加HATEOAS依赖
// <dependency>
//     <groupId>org.springframework.boot</groupId>
//     <artifactId>spring-boot-starter-hateoas</artifactId>
// </dependency>

@GetMapping("/{id}")
public EntityModel<User> getUserById(@PathVariable Long id) {
    User user = userService.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found with id: " + id));
    
    EntityModel<User> userResource = EntityModel.of(user);
    userResource.add(linkTo(methodOn(UserRestController.class).getUserById(id)).withSelfRel());
    userResource.add(linkTo(methodOn(UserRestController.class).getAllUsers()).withRel("all-users"));
    
    return userResource;
}
```

## 配置Spring MVC

Spring MVC可以通过多种方式进行配置。

### 基于Java的配置

```java
@Configuration
@EnableWebMvc
@ComponentScan(basePackages = "com.example.controller")
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void configureDefaultServletHandling(DefaultServletHandlerConfigurer configurer) {
        configurer.enable();
    }
    
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
                .addResourceLocations("/public/", "classpath:/static/");
    }
    
    @Override
    public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
        configurer.defaultContentType(MediaType.APPLICATION_JSON);
    }
    
    @Bean
    public ViewResolver viewResolver() {
        InternalResourceViewResolver resolver = new InternalResourceViewResolver();
        resolver.setPrefix("/WEB-INF/views/");
        resolver.setSuffix(".jsp");
        return resolver;
    }
}
```

### Spring Boot自动配置

在Spring Boot中，大部分配置都是自动完成的：

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

自定义配置：

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowCredentials(true);
    }
}
```

## 最佳实践

### 1. 控制器设计

```java
// 使用@RestController处理REST API
@RestController
@RequestMapping("/api/v1")
public class UserController {
    
    // 使用明确的HTTP方法注解
    @GetMapping("/users")
    public ResponseEntity<List<UserDto>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        // 实现逻辑
    }
    
    // 使用DTO而不是直接暴露实体
    @PostMapping("/users")
    public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserRequest request) {
        // 实现逻辑
    }
}
```

### 2. 异常处理

```java
// 定义统一的错误响应格式
public class ErrorResponse {
    private String code;
    private String message;
    private LocalDateTime timestamp;
    
    // 构造函数、getter和setter
}

// 全局异常处理
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(ValidationException ex) {
        ErrorResponse error = ErrorResponse.builder()
                .code("VALIDATION_ERROR")
                .message(ex.getMessage())
                .timestamp(LocalDateTime.now())
                .build();
        return ResponseEntity.badRequest().body(error);
    }
}
```

### 3. 数据验证

```java
// DTO验证
public class CreateUserRequest {
    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 20, message = "Username must be between 3 and 20 characters")
    private String username;
    
    @Email(message = "Email should be valid")
    private String email;
    
    @Pattern(regexp = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).{8,}$",
             message = "Password must contain at least one digit, one lowercase and one uppercase letter, and be at least 8 characters long")
    private String password;
    
    // getter和setter
}
```

### 4. 日志记录

```java
@RestController
@RequestMapping("/api/users")
@Slf4j
public class UserController {
    
    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        log.info("Fetching user with id: {}", id);
        
        UserDto user = userService.findById(id);
        
        log.debug("User found: {}", user);
        return ResponseEntity.ok(user);
    }
}
```

## 总结

本章详细介绍了Spring MVC的核心概念和使用方法，包括：

1. **Spring MVC架构**：理解前端控制器模式和各组件的作用
2. **控制器开发**：使用注解创建RESTful控制器
3. **数据绑定和验证**：处理请求参数和数据验证
4. **视图解析**：支持多种视图技术
5. **异常处理**：全局和局部异常处理机制
6. **拦截器**：在请求处理前后执行逻辑
7. **文件上传**：处理文件上传请求
8. **RESTful服务**：构建符合REST规范的Web服务
9. **配置方式**：基于Java和Spring Boot的配置方法
10. **最佳实践**：控制器设计、异常处理、数据验证等方面的最佳实践

Spring MVC是一个功能强大且灵活的Web框架，通过合理的使用可以构建出高性能、易维护的Web应用程序。掌握这些核心概念和技巧对于开发高质量的Spring Web应用至关重要。