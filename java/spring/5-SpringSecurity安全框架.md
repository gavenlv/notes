# 第5章 Spring Security安全框架

## 本章概述

本章将深入探讨Spring Security，这是一个功能强大且高度可定制的身份验证和访问控制框架。我们将学习如何使用Spring Security保护Web应用程序，实现身份验证、授权、会话管理等功能，并了解其核心概念和最佳实践。

## 目录

1. [Spring Security简介](#spring-security简介)
2. [核心概念](#核心概念)
3. [环境搭建](#环境搭建)
4. [基本配置](#基本配置)
5. [身份验证](#身份验证)
6. [授权](#授权)
7. [密码加密](#密码加密)
8. [会话管理](#会话管理)
9. [CSRF保护](#csrf保护)
10. [跨域资源共享(CORS)](#跨域资源共享cors)
11. [OAuth2集成](#oauth2集成)
12. [JWT令牌](#jwt令牌)
13. [方法级安全](#方法级安全)
14. [测试安全配置](#测试安全配置)
15. [最佳实践](#最佳实践)

## Spring Security简介

Spring Security是一个为基于Spring的应用程序提供声明式安全服务的框架。它提供全面的安全服务，包括认证、授权、防护常见攻击等功能。

### 主要特性

1. **全面的认证和授权支持**：支持多种认证方式和细粒度的权限控制
2. **防护常见攻击**：内置防护CSRF、点击劫持、会话固定等攻击
3. **Servlet API集成**：与Servlet API无缝集成
4. **可选框架集成**：支持与Spring Web MVC、Spring Boot等框架集成
5. **高度可定制**：提供丰富的扩展点和配置选项

## 核心概念

### 安全上下文(Security Context)

Security Context持有当前用户的认证信息，可以通过SecurityContextHolder访问。

```java
Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
String username = authentication.getName();
Collection<? extends GrantedAuthority> authorities = authentication.getAuthorities();
```

### 认证(Authentication)

Authentication代表用户的身份验证信息，包括用户名、密码、权限等。

### 授权(Authorization)

Authorization决定经过认证的用户是否具有执行某个操作的权限。

### 过滤器链(Filter Chain)

Spring Security通过一系列过滤器来处理安全相关的逻辑，每个过滤器负责特定的安全功能。

## 环境搭建

### Maven依赖

```xml
<dependencies>
    <!-- Spring Boot Security Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    
    <!-- Spring Boot Web Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Thymeleaf模板引擎（如果需要） -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-thymeleaf</artifactId>
    </dependency>
    
    <!-- Thymeleaf Spring Security集成 -->
    <dependency>
        <groupId>org.thymeleaf.extras</groupId>
        <artifactId>thymeleaf-extras-springsecurity6</artifactId>
    </dependency>
</dependencies>
```

### 启动类配置

```java
@SpringBootApplication
public class SecurityApplication {
    public static void main(String[] args) {
        SpringApplication.run(SecurityApplication.class, args);
    }
}
```

## 基本配置

### 默认安全配置

当引入Spring Security依赖后，默认会启用以下安全配置：

1. 所有HTTP请求都需要认证
2. 自动生成登录页面
3. 支持基于表单的认证
4. 自动生成登出功能
5. 防护CSRF攻击
6. Session Fixation保护
7. Security Header集成

### 自定义安全配置

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .permitAll()
            )
            .logout(logout -> logout
                .permitAll()
            );
            
        return http.build();
    }
}
```

## 身份验证

### 内存认证

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public InMemoryUserDetailsManager userDetailsService() {
        UserDetails user = User.withDefaultPasswordEncoder()
            .username("user")
            .password("password")
            .roles("USER")
            .build();
            
        UserDetails admin = User.withDefaultPasswordEncoder()
            .username("admin")
            .password("admin")
            .roles("USER", "ADMIN")
            .build();
            
        return new InMemoryUserDetailsManager(user, admin);
    }
}
```

### JDBC认证

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Autowired
    private DataSource dataSource;
    
    @Bean
    public JdbcUserDetailsManager userDetailsManager() {
        JdbcUserDetailsManager manager = new JdbcUserDetailsManager(dataSource);
        
        // 自定义查询语句
        manager.setUsersByUsernameQuery(
            "select username,password,enabled from users where username=?");
        manager.setAuthoritiesByUsernameQuery(
            "select username,authority from authorities where username=?");
            
        return manager;
    }
}
```

### 自定义UserDetailsService

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));
            
        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getUsername())
            .password(user.getPassword())
            .authorities(getAuthorities(user))
            .accountExpired(false)
            .accountLocked(false)
            .credentialsExpired(false)
            .disabled(!user.isEnabled())
            .build();
    }
    
    private Collection<? extends GrantedAuthority> getAuthorities(User user) {
        return user.getRoles().stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role.getName()))
            .collect(Collectors.toList());
    }
}
```

## 授权

### 基于URL的授权

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(authz -> authz
            .requestMatchers("/public/**").permitAll()
            .requestMatchers("/user/**").hasAnyRole("USER", "ADMIN")
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .requestMatchers(HttpMethod.POST, "/api/books").hasAuthority("BOOK_CREATE")
            .anyRequest().authenticated()
        );
        
    return http.build();
}
```

### 基于方法的安全控制

```java
@RestController
@RequestMapping("/api/books")
public class BookController {
    
    @PreAuthorize("hasRole('USER')")
    @GetMapping
    public List<Book> getAllBooks() {
        // 只有USER角色才能访问
        return bookService.findAll();
    }
    
    @PreAuthorize("hasAuthority('BOOK_CREATE')")
    @PostMapping
    public Book createBook(@RequestBody Book book) {
        // 只有拥有BOOK_CREATE权限的用户才能创建书籍
        return bookService.save(book);
    }
    
    @PostAuthorize("returnObject.owner == authentication.name")
    @GetMapping("/{id}")
    public Book getBook(@PathVariable Long id) {
        // 返回的对象必须属于当前用户
        return bookService.findById(id);
    }
    
    @PreAuthorize("#book.owner == authentication.name")
    @PutMapping("/{id}")
    public Book updateBook(@PathVariable Long id, @RequestBody Book book) {
        // 传入的书籍对象必须属于当前用户
        return bookService.update(id, book);
    }
}
```

### 表达式安全

Spring Security支持使用表达式语言进行复杂的权限控制：

```java
@PreAuthorize("hasRole('ADMIN') or #userId == principal.id")
public User getUserProfile(Long userId) {
    return userService.findById(userId);
}

@PreAuthorize("@webSecurity.checkUserId(authentication, #id)")
public void updateUser(Long id, User user) {
    userService.update(id, user);
}
```

## 密码加密

### BCryptPasswordEncoder

```java
@Configuration
public class SecurityConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 使用密码编码器

```java
@Service
public class UserService {
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @Autowired
    private UserRepository userRepository;
    
    public User createUser(CreateUserRequest request) {
        User user = new User();
        user.setUsername(request.getUsername());
        // 加密密码
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setEnabled(true);
        
        return userRepository.save(user);
    }
    
    public boolean validatePassword(String rawPassword, String encodedPassword) {
        return passwordEncoder.matches(rawPassword, encodedPassword);
    }
}
```

## 会话管理

### 会话配置

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .sessionManagement(session -> session
            .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
            .invalidSessionUrl("/invalidSession.html")
            .maximumSessions(1)
            .maxSessionsPreventsLogin(false)
            .expiredUrl("/expired.html")
        );
        
    return http.build();
}
```

### 自定义会话注册表

```java
@Component
public class CustomSessionRegistry {
    
    @Autowired
    private SessionRegistry sessionRegistry;
    
    public List<SessionInformation> getActiveSessions(String username) {
        return sessionRegistry.getAllSessions(username, false);
    }
    
    public void expireUserSessions(String username) {
        List<SessionInformation> sessions = sessionRegistry.getAllSessions(username, false);
        for (SessionInformation session : sessions) {
            session.expireNow();
        }
    }
}
```

## CSRF保护

### 启用CSRF保护

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf
            .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            .ignoringRequestMatchers("/api/public/**")
        );
        
    return http.build();
}
```

### 在Thymeleaf中使用CSRF令牌

```html
<form th:action="@{/logout}" method="post">
    <input type="hidden" 
           th:name="${_csrf.parameterName}" 
           th:value="${_csrf.token}"/>
    <button type="submit">Logout</button>
</form>
```

### 在AJAX请求中使用CSRF令牌

```javascript
// 获取CSRF令牌
var token = $("meta[name='_csrf']").attr("content");
var header = $("meta[name='_csrf_header']").attr("content");

// 在AJAX请求中添加CSRF头
$.ajaxSetup({
    beforeSend: function(xhr) {
        xhr.setRequestHeader(header, token);
    }
});
```

## 跨域资源共享(CORS)

### CORS配置

```java
@Configuration
public class CorsConfig {
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

### 在Security配置中启用CORS

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        .csrf(csrf -> csrf.disable()); // 在前后端分离应用中通常禁用CSRF
        
    return http.build();
}
```

## OAuth2集成

### 添加OAuth2客户端依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>
```

### OAuth2客户端配置

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          github:
            clientId: your-github-client-id
            clientSecret: your-github-client-secret
            scope: read:user,user:email
        provider:
          github:
            authorization-uri: https://github.com/login/oauth/authorize
            token-uri: https://github.com/login/oauth/access_token
            user-info-uri: https://api.github.com/user
            user-name-attribute: login
```

### OAuth2登录配置

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(authz -> authz
            .requestMatchers("/", "/login**", "/error**").permitAll()
            .anyRequest().authenticated()
        )
        .oauth2Login(oauth2 -> oauth2
            .defaultSuccessUrl("/dashboard")
            .failureUrl("/login?error=true")
        );
        
    return http.build();
}
```

### 自定义OAuth2用户服务

```java
@Service
public class CustomOAuth2UserService implements OAuth2UserService<OAuth2UserRequest, OAuth2User> {
    
    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2UserService<OAuth2UserRequest, OAuth2User> delegate = 
            new DefaultOAuth2UserService();
        OAuth2User oAuth2User = delegate.loadUser(userRequest);
        
        String registrationId = userRequest.getClientRegistration().getRegistrationId();
        String userNameAttributeName = userRequest.getClientRegistration()
            .getProviderDetails().getUserInfoEndpoint().getUserNameAttributeName();
            
        return processOAuth2User(registrationId, userNameAttributeName, oAuth2User);
    }
    
    private OAuth2User processOAuth2User(String registrationId, 
                                       String userNameAttributeName, 
                                       OAuth2User oAuth2User) {
        // 处理OAuth2用户信息，例如保存到数据库
        Map<String, Object> attributes = oAuth2User.getAttributes();
        String email = (String) attributes.get("email");
        String name = (String) attributes.get("name");
        
        // 自定义逻辑...
        
        return oAuth2User;
    }
}
```

## JWT令牌

### 添加JWT依赖

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.11.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.11.5</version>
    <scope>runtime</scope>
</dependency>
```

### JWT工具类

```java
@Component
public class JwtTokenUtil {
    
    private String secret = "mySecretKey";
    private int jwtExpiration = 86400; // 24小时
    
    public String generateToken(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();
        return createToken(claims, userDetails.getUsername());
    }
    
    private String createToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + jwtExpiration * 1000))
                .signWith(SignatureAlgorithm.HS512, secret)
                .compact();
    }
    
    public Boolean validateToken(String token, UserDetails userDetails) {
        final String username = getUsernameFromToken(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }
    
    public String getUsernameFromToken(String token) {
        return getClaimFromToken(token, Claims::getSubject);
    }
    
    public Date getExpirationDateFromToken(String token) {
        return getClaimFromToken(token, Claims::getExpiration);
    }
    
    public <T> T getClaimFromToken(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = getAllClaimsFromToken(token);
        return claimsResolver.apply(claims);
    }
    
    private Claims getAllClaimsFromToken(String token) {
        return Jwts.parser().setSigningKey(secret).parseClaimsJws(token).getBody();
    }
    
    private Boolean isTokenExpired(String token) {
        final Date expiration = getExpirationDateFromToken(token);
        return expiration.before(new Date());
    }
}
```

### JWT认证过滤器

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Autowired
    private UserDetailsService userDetailsService;
    
    @Autowired
    private JwtTokenUtil jwtTokenUtil;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                  HttpServletResponse response, 
                                  FilterChain chain) throws ServletException, IOException {
        
        final String requestTokenHeader = request.getHeader("Authorization");
        
        String username = null;
        String jwtToken = null;
        
        if (requestTokenHeader != null && requestTokenHeader.startsWith("Bearer ")) {
            jwtToken = requestTokenHeader.substring(7);
            try {
                username = jwtTokenUtil.getUsernameFromToken(jwtToken);
            } catch (IllegalArgumentException e) {
                logger.error("Unable to get JWT Token");
            } catch (ExpiredJwtException e) {
                logger.error("JWT Token has expired");
            }
        }
        
        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);
            
            if (jwtTokenUtil.validateToken(jwtToken, userDetails)) {
                UsernamePasswordAuthenticationToken authToken = 
                    new UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.getAuthorities());
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }
        chain.doFilter(request, response);
    }
}
```

### 配置JWT安全

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
            
        return http.build();
    }
}
```

## 方法级安全

### 启用方法级安全

```java
@Configuration
@EnableMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class MethodSecurityConfig {
    // 配置类
}
```

### 使用@Secured注解

```java
@Service
public class BookService {
    
    @Secured("ROLE_ADMIN")
    public void deleteBook(Long id) {
        // 只有ADMIN角色才能删除书籍
        bookRepository.deleteById(id);
    }
    
    @Secured({"ROLE_USER", "ROLE_ADMIN"})
    public Book createBook(Book book) {
        // USER或ADMIN角色都可以创建书籍
        return bookRepository.save(book);
    }
}
```

### 使用@PreAuthorize和@PostAuthorize

```java
@Service
public class BookService {
    
    @PreAuthorize("hasRole('ADMIN') or #book.owner == authentication.name")
    public Book updateBook(Long id, Book book) {
        // ADMIN角色或书籍所有者可以更新书籍
        return bookRepository.save(book);
    }
    
    @PostAuthorize("returnObject.owner == authentication.name")
    public Book getBook(Long id) {
        // 返回的书籍必须属于当前用户
        return bookRepository.findById(id).orElse(null);
    }
}
```

## 测试安全配置

### 添加测试依赖

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-test</artifactId>
    <scope>test</scope>
</dependency>
```

### 使用@WithMockUser注解

```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class BookControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    @WithMockUser(roles = "USER")
    void testGetAllBooks() throws Exception {
        mockMvc.perform(get("/api/books"))
               .andExpect(status().isOk());
    }
    
    @Test
    @WithMockUser(roles = "ADMIN")
    void testDeleteBook() throws Exception {
        mockMvc.perform(delete("/api/books/1"))
               .andExpect(status().isOk());
    }
    
    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void testCreateBook() throws Exception {
        Book book = new Book();
        book.setTitle("Test Book");
        book.setAuthor("Test Author");
        
        mockMvc.perform(post("/api/books")
               .contentType(MediaType.APPLICATION_JSON)
               .content(objectMapper.writeValueAsString(book)))
               .andExpect(status().isOk());
    }
}
```

### 使用TestExecutionEvent

```java
@Test
@WithMockUser(username = "admin", roles = {"USER", "ADMIN"}, setupBefore = TestExecutionEvent.TEST_EXECUTION)
void testAdminFunctionality() throws Exception {
    // 测试需要管理员权限的功能
}
```

## 最佳实践

### 1. 安全配置分离

```java
@Configuration
@EnableWebSecurity
public class WebSecurityConfig {
    
    @Bean
    @Order(1)
    public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/api/**")
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable());
            
        return http.build();
    }
    
    @Bean
    @Order(2)
    public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/static/**", "/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form.permitAll())
            .logout(logout -> logout.permitAll());
            
        return http.build();
    }
}
```

### 2. 密码安全策略

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // 增加强度
}

// 密码策略验证
@Component
public class PasswordValidator {
    
    public boolean isValid(String password) {
        // 至少8位，包含大写字母、小写字母、数字和特殊字符
        String pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$";
        return password.matches(pattern);
    }
}
```

### 3. 安全日志记录

```java
@Component
public class SecurityEventListener {
    
    private static final Logger logger = LoggerFactory.getLogger(SecurityEventListener.class);
    
    @EventListener
    public void handleAuthenticationSuccess(AuthenticationSuccessEvent event) {
        String username = event.getAuthentication().getPrincipal().toString();
        logger.info("Authentication successful for user: {}", username);
    }
    
    @EventListener
    public void handleAuthenticationFailure(AbstractAuthenticationFailureEvent event) {
        String username = event.getAuthentication().getPrincipal().toString();
        logger.warn("Authentication failed for user: {}", username);
    }
    
    @EventListener
    public void handleAuthorizationFailure(AuthorizationDeniedEvent event) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null) {
            logger.warn("Authorization denied for user: {}", authentication.getPrincipal());
        }
    }
}
```

### 4. 安全响应头

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .headers(headers -> headers
            .frameOptions(frame -> frame.deny())
            .contentTypeOptions(contentType -> contentType.configureDefaults())
            .httpStrictTransportSecurity(hsts -> hsts
                .maxAgeInSeconds(31536000)
                .includeSubdomains(true)
                .preload(true))
            .xssProtection(xss -> xss.headerValue(XXssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK))
            .contentSecurityPolicy(csp -> csp
                .policyDirectives("default-src 'self'; script-src 'self' 'unsafe-inline'"))
        );
        
    return http.build();
}
```

### 5. 异常处理

```java
@Component
public class SecurityExceptionHandler {
    
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDenied(AccessDeniedException ex) {
        ErrorResponse error = new ErrorResponse("ACCESS_DENIED", "Access denied");
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(error);
    }
    
    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ErrorResponse> handleAuthentication(AuthenticationException ex) {
        ErrorResponse error = new ErrorResponse("AUTHENTICATION_FAILED", "Authentication failed");
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
    }
}
```

## 总结

本章详细介绍了Spring Security的核心概念和使用方法，包括：

1. **Spring Security简介**：了解其主要特性和优势
2. **核心概念**：安全上下文、认证、授权、过滤器链等
3. **环境搭建**：Maven依赖和基本配置
4. **基本配置**：默认配置和自定义安全配置
5. **身份验证**：内存认证、JDBC认证、自定义UserDetailsService
6. **授权**：基于URL和方法的安全控制
7. **密码加密**：BCryptPasswordEncoder的使用
8. **会话管理**：会话配置和管理
9. **CSRF保护**：CSRF防护机制和配置
10. **跨域资源共享**：CORS配置和支持
11. **OAuth2集成**：OAuth2客户端配置和使用
12. **JWT令牌**：JWT生成、验证和使用
13. **方法级安全**：@Secured、@PreAuthorize等注解的使用
14. **测试安全配置**：使用Spring Security Test进行安全测试
15. **最佳实践**：安全配置分离、密码策略、日志记录、响应头设置等

Spring Security提供了全面的安全解决方案，通过合理配置和使用可以有效保护应用程序免受各种安全威胁。掌握这些核心概念和最佳实践对于构建安全可靠的Web应用程序至关重要。