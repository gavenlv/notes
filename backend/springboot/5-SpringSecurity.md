# 第五章 Spring Boot集成Spring Security

在现代Web应用程序中，安全性是至关重要的。Spring Security是一个功能强大且高度可定制的身份验证和访问控制框架，专为Java应用程序设计。它为基于Java的企业应用程序提供了全面的安全服务。

本章将详细介绍如何在Spring Boot应用程序中集成Spring Security，包括用户认证、授权、JWT支持等功能。

## 目录
1. [Spring Security简介](#spring-security简介)
2. [核心概念](#核心概念)
3. [基本配置](#基本配置)
4. [用户认证](#用户认证)
5. [用户授权](#用户授权)
6. [JWT集成](#jwt集成)
7. [方法级安全](#方法级安全)
8. [最佳实践](#最佳实践)

## Spring Security简介

Spring Security是Spring生态系统中的一个核心项目，专门用于为Java应用程序提供安全服务。它提供了一套完整的安全解决方案，包括：

- 认证（Authentication）：验证用户身份
- 授权（Authorization）：控制用户访问权限
- 攻击防护：防止常见的安全攻击如CSRF、点击劫持等
- 会话管理：管理用户会话
- 密码加密：安全地存储和验证密码

### 主要特性

1. **全面的认证支持**：支持多种认证方式，包括表单登录、HTTP基本认证、LDAP、OAuth等
2. **细粒度的授权机制**：支持基于角色、权限的访问控制
3. **防护常见攻击**：内置防护CSRF、点击劫持、会话固定等攻击
4. **与Spring框架无缝集成**：充分利用Spring框架的优势
5. **高度可扩展性**：可以根据需要自定义各种安全组件

## 核心概念

在深入学习Spring Security之前，我们需要了解一些核心概念：

### Authentication（认证）

认证是验证用户身份的过程。在Spring Security中，认证过程通常涉及以下几个步骤：

1. 用户提供凭据（如用户名和密码）
2. 系统验证这些凭据的有效性
3. 如果验证成功，则建立用户的认证状态

### Authorization（授权）

授权是在用户通过认证后，确定该用户可以访问哪些资源或执行哪些操作的过程。Spring Security提供了多种授权机制：

- 基于角色的访问控制（RBAC）
- 基于权限的访问控制
- 方法级别的安全控制

### Principal（主体）

Principal代表当前用户的信息，包含了用户的标识和其他相关信息。

### Granted Authority（授予的权限）

Granted Authority表示用户被授予的权限，通常以角色或具体权限的形式存在。

### Security Context（安全上下文）

Security Context保存了当前安全相关的上下文信息，包括当前认证的用户信息。

## 基本配置

要在Spring Boot项目中集成Spring Security，我们需要添加相应的依赖并进行基本配置。

### 添加依赖

在`pom.xml`中添加以下依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 默认安全配置

添加Spring Security依赖后，Spring Boot会自动配置一些默认的安全设置：

- 所有HTTP请求都需要认证
- 自动生成一个登录页面
- 使用HTTP Basic认证作为备选方案
- 自动生成一个用户，用户名为"user"，密码会在控制台打印

### 自定义安全配置

我们可以通过继承`WebSecurityConfigurerAdapter`（Spring Security 5.7之前的版本）或实现`SecurityFilterChain`（Spring Security 5.7及之后版本）来自定义安全配置。

#### Spring Security 5.7之前版本的配置方式：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/", "/home").permitAll()
                .anyRequest().authenticated()
                .and()
            .formLogin()
                .loginPage("/login")
                .permitAll()
                .and()
            .logout()
                .permitAll();
    }
}
```

#### Spring Security 5.7及之后版本的配置方式：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/", "/home").permitAll()
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

## 用户认证

Spring Security提供了多种认证方式，我们可以根据需求选择合适的认证机制。

### 内存认证

最简单的认证方式是使用内存中的用户信息：

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
            .roles("ADMIN")
            .build();
            
        return new InMemoryUserDetailsManager(user, admin);
    }
}
```

注意：`withDefaultPasswordEncoder()`仅用于演示，在生产环境中应使用更安全的密码编码器。

### 数据库认证

实际项目中，用户信息通常存储在数据库中。我们需要实现`UserDetailsService`接口来从数据库加载用户信息：

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username);
        if (user == null) {
            throw new UsernameNotFoundException("User not found");
        }
        
        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getUsername())
            .password(user.getPassword())
            .authorities(getAuthorities(user))
            .build();
    }
    
    private Collection<? extends GrantedAuthority> getAuthorities(User user) {
        return user.getRoles().stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role.getName()))
            .collect(Collectors.toList());
    }
}
```

### 密码加密

为了安全地存储密码，我们需要使用密码编码器：

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

在保存用户时使用密码编码器：

```java
@Autowired
private PasswordEncoder passwordEncoder;

public void saveUser(User user) {
    String encodedPassword = passwordEncoder.encode(user.getPassword());
    user.setPassword(encodedPassword);
    userRepository.save(user);
}
```

## 用户授权

授权决定了经过认证的用户可以访问哪些资源。Spring Security提供了多种授权机制。

### 基于URL的授权

我们可以在安全配置中定义基于URL的访问控制规则：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(authz -> authz
            .requestMatchers("/public/**").permitAll()
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .requestMatchers("/user/**").hasAnyRole("USER", "ADMIN")
            .anyRequest().authenticated()
        );
    return http.build();
}
```

### 基于方法的安全控制

除了URL级别的授权，我们还可以在方法级别进行安全控制：

```java
@RestController
public class UserController {
    
    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/users/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Long id) {
        // 删除用户的逻辑
        return ResponseEntity.ok().build();
    }
    
    @PreAuthorize("hasAnyRole('USER', 'ADMIN')")
    @GetMapping("/users/profile")
    public ResponseEntity<UserProfile> getUserProfile() {
        // 获取用户资料的逻辑
        return ResponseEntity.ok(profile);
    }
}
```

需要在配置类上添加`@EnableGlobalMethodSecurity`注解启用方法级安全：

```java
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    // 配置内容
}
```

## JWT集成

JSON Web Token (JWT) 是一种开放标准(RFC 7519)，用于在各方之间安全地传输信息。在无状态的REST API中，JWT是一种常用的认证方式。

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
public class JwtUtil {
    
    private String SECRET_KEY = "mySecretKey";
    
    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }
    
    public Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }
    
    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }
    
    private Claims extractAllClaims(String token) {
        return Jwts.parser().setSigningKey(SECRET_KEY).parseClaimsJws(token).getBody();
    }
    
    private Boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }
    
    public String generateToken(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();
        return createToken(claims, userDetails.getUsername());
    }
    
    private String createToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 10))
                .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
                .compact();
    }
    
    public Boolean validateToken(String token, UserDetails userDetails) {
        final String username = extractUsername(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }
}
```

### JWT过滤器

```java
@Component
public class JwtRequestFilter extends OncePerRequestFilter {
    
    @Autowired
    private CustomUserDetailsService userDetailsService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        
        final String authorizationHeader = request.getHeader("Authorization");
        
        String username = null;
        String jwt = null;
        
        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            jwt = authorizationHeader.substring(7);
            username = jwtUtil.extractUsername(jwt);
        }
        
        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);
            
            if (jwtUtil.validateToken(jwt, userDetails)) {
                UsernamePasswordAuthenticationToken usernamePasswordAuthenticationToken = 
                    new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
                usernamePasswordAuthenticationToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(usernamePasswordAuthenticationToken);
            }
        }
        chain.doFilter(request, response);
    }
}
```

### 配置JWT

修改安全配置以使用JWT：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Autowired
    private JwtRequestFilter jwtRequestFilter;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/authenticate").permitAll()
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            );
        
        http.addFilterBefore(jwtRequestFilter, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

### 认证控制器

```java
@RestController
public class AuthenticationController {
    
    @Autowired
    private AuthenticationManager authenticationManager;
    
    @Autowired
    private CustomUserDetailsService userDetailsService;
    
    @Autowired
    private JwtUtil jwtTokenUtil;
    
    @PostMapping("/authenticate")
    public ResponseEntity<?> createAuthenticationToken(@RequestBody AuthenticationRequest authenticationRequest) throws Exception {
        try {
            authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(authenticationRequest.getUsername(), authenticationRequest.getPassword())
            );
        } catch (BadCredentialsException e) {
            throw new Exception("Incorrect username or password", e);
        }
        
        final UserDetails userDetails = userDetailsService.loadUserByUsername(authenticationRequest.getUsername());
        final String jwt = jwtTokenUtil.generateToken(userDetails);
        
        return ResponseEntity.ok(new AuthenticationResponse(jwt));
    }
}
```

## 方法级安全

Spring Security不仅支持URL级别的安全控制，还支持方法级别的安全控制，这使得我们可以更精细地控制访问权限。

### 启用方法级安全

首先需要在配置类上添加`@EnableGlobalMethodSecurity`注解：

```java
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class SecurityConfig {
    // 安全配置
}
```

### 使用注解控制方法访问

#### @PreAuthorize 和 @PostAuthorize

- `@PreAuthorize`：在方法执行前进行权限检查
- `@PostAuthorize`：在方法执行后进行权限检查

```java
@Service
public class UserService {
    
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(Long userId) {
        // 只有管理员才能删除用户
    }
    
    @PreAuthorize("#userId == authentication.principal.id")
    public User updateUser(Long userId, UserUpdateRequest request) {
        // 用户只能更新自己的信息
        return userRepository.save(/* 更新逻辑 */);
    }
    
    @PostAuthorize("returnObject.owner == authentication.name")
    public Document getDocument(Long documentId) {
        // 返回的文档必须属于当前用户
        return documentRepository.findById(documentId);
    }
}
```

#### @Secured

`@Secured`注解是另一种方法级安全控制方式：

```java
@Service
public class ReportService {
    
    @Secured("ROLE_ADMIN")
    public void generateReport() {
        // 只有管理员可以生成报告
    }
    
    @Secured({"ROLE_USER", "ROLE_ADMIN"})
    public List<Order> getUserOrders() {
        // 用户或管理员都可以获取订单列表
        return orderRepository.findAll();
    }
}
```

## 最佳实践

在使用Spring Security时，遵循一些最佳实践可以帮助我们构建更安全的应用程序：

### 1. 使用强密码编码器

始终使用强密码编码器（如BCrypt）来存储密码：

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

### 2. 正确处理异常

妥善处理认证和授权过程中可能出现的异常：

```java
@Component
public class CustomAuthenticationEntryPoint implements AuthenticationEntryPoint {
    
    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException authException) throws IOException {
        response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized");
    }
}
```

### 3. 防止CSRF攻击

对于传统的Web应用程序，启用CSRF保护：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf
            .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
        );
    return http.build();
}
```

### 4. 安全头配置

配置安全头以增强应用程序的安全性：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .headers(headers -> headers
            .frameOptions().deny()
            .contentTypeOptions().and()
            .httpStrictTransportSecurity(hstsConfig -> hstsConfig
                .maxAgeInSeconds(31536000)
                .includeSubdomains(true)
            )
        );
    return http.build();
}
```

### 5. 会话管理

合理配置会话管理策略：

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .sessionManagement(session -> session
            .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
            .maximumSessions(1)
            .maxSessionsPreventsLogin(false)
        );
    return http.build();
}
```

### 6. 定期更新依赖

定期更新Spring Security及相关依赖到最新稳定版本，以获得最新的安全修复和改进。

通过遵循这些最佳实践，我们可以确保应用程序具有更强的安全性，更好地保护用户数据和系统资源。