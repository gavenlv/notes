# 第4章 Spring Data JPA数据访问

## 本章概述

本章将详细介绍Spring Data JPA，这是Spring Data项目中专门用于简化JPA数据访问的模块。我们将学习如何使用Spring Data JPA来减少数据访问层的样板代码，提高开发效率，并探索其丰富的查询功能。

## 目录

1. [Spring Data JPA简介](#spring-data-jpa简介)
2. [核心概念](#核心概念)
3. [环境搭建](#环境搭建)
4. [实体类映射](#实体类映射)
5. [Repository接口](#repository接口)
6. [查询方法](#查询方法)
7. [JPQL查询](#jpql查询)
8. [原生SQL查询](#原生sql查询)
9. [事务管理](#事务管理)
10. [审计功能](#审计功能)
11. [分页和排序](#分页和排序)
12. [关联关系处理](#关联关系处理)
13. [性能优化](#性能优化)
14. [最佳实践](#最佳实践)

## Spring Data JPA简介

Spring Data JPA是Spring Data项目的一部分，旨在显著减少实现数据访问层所需的样板代码。它建立在JPA（Java Persistence API）之上，提供了更简洁的API和强大的查询功能。

### Spring Data JPA的优势

1. **减少样板代码**：自动生成常见的CRUD操作实现
2. **方法名查询**：通过方法命名约定自动生成查询
3. **丰富的查询功能**：支持JPQL、原生SQL、动态查询等
4. **分页和排序**：内置分页和排序支持
5. **事务管理**：简化事务配置和管理
6. **审计功能**：自动记录创建时间和修改时间等信息
7. **类型安全**：提供类型安全的查询API（Criteria API）

## 核心概念

### Repository模式

Repository模式是一种将数据访问逻辑与业务逻辑分离的设计模式。Spring Data JPA通过Repository接口实现这一模式。

### JpaRepository接口

JpaRepository是Spring Data JPA提供的核心接口，继承自PagingAndSortingRepository和QueryByExampleExecutor，提供了丰富的数据访问方法。

```java
public interface JpaRepository<T, ID> extends PagingAndSortingRepository<T, ID>, QueryByExampleExecutor<T> {
    // 提供了save, saveAll, findById, findAll, delete等方法
}
```

### EntityManager

EntityManager是JPA的核心组件，负责实体的持久化操作。Spring Data JPA在底层使用EntityManager来执行数据库操作。

## 环境搭建

### Maven依赖

```xml
<dependencies>
    <!-- Spring Boot Data JPA Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <!-- 数据库驱动（以MySQL为例） -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <scope>runtime</scope>
    </dependency>
    
    <!-- H2数据库（用于测试） -->
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### 配置文件

```properties
# application.properties
# 数据库配置
spring.datasource.url=jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=utf8&useSSL=false
spring.datasource.username=root
spring.datasource.password=password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA配置
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
spring.jpa.properties.hibernate.format_sql=true

# 连接池配置
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
```

### 启用JPA Repositories

```java
@Configuration
@EnableJpaRepositories(basePackages = "com.example.repository")
@EntityScan(basePackages = "com.example.entity")
public class JpaConfig {
    // 配置类
}
```

在Spring Boot中，这些配置通常是自动完成的。

## 实体类映射

### 基本实体类

```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String username;
    
    @Column(nullable = false)
    private String email;
    
    @Column(name = "first_name")
    private String firstName;
    
    @Column(name = "last_name")
    private String lastName;
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Enumerated(EnumType.STRING)
    private UserRole role;
    
    @Transient
    private String fullName;
    
    public String getFullName() {
        return firstName + " " + lastName;
    }
}
```

### 枚举类型

```java
public enum UserRole {
    ADMIN, USER, GUEST
}
```

### 关联关系

```java
@Entity
@Table(name = "orders")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Order {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<OrderItem> orderItems = new ArrayList<>();
    
    @Column(nullable = false)
    private BigDecimal totalAmount;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
}
```

## Repository接口

### 基本Repository

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // JpaRepository已经提供了基本的CRUD方法
    // save, saveAll, findById, findAll, delete等
}
```

### 自定义查询方法

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 方法名查询
    List<User> findByUsername(String username);
    
    List<User> findByEmailContaining(String email);
    
    List<User> findByRole(UserRole role);
    
    // 多条件查询
    List<User> findByFirstNameAndLastName(String firstName, String lastName);
    
    List<User> findByFirstNameOrLastName(String firstName, String lastName);
    
    // 范围查询
    List<User> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    // 排序查询
    List<User> findByRoleOrderByUsernameAsc(UserRole role);
    
    // 限制结果数量
    List<User> findFirst10ByRole(UserRole role);
    
    // 存在性检查
    boolean existsByUsername(String username);
    
    // 计数查询
    long countByRole(UserRole role);
    
    // 删除操作
    @Modifying
    @Transactional
    void deleteByEmail(String email);
}
```

### 使用示例

```java
@Service
@Transactional(readOnly = true)
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }
    
    @Transactional
    public User saveUser(User user) {
        return userRepository.save(user);
    }
    
    public List<User> getUsersByUsername(String username) {
        return userRepository.findByUsername(username);
    }
    
    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
```

## 查询方法

### 方法名查询规则

Spring Data JPA支持通过方法名自动生成查询语句：

| 关键字 | 示例 | JPQL片段 |
|--------|------|----------|
| And | findByLastnameAndFirstname | where x.lastname = ?1 and x.firstname = ?2 |
| Or | findByLastnameOrFirstname | where x.lastname = ?1 or x.firstname = ?2 |
| Is, Equals | findByFirstname,findByFirstnameIs,findByFirstnameEquals | where x.firstname = ?1 |
| Between | findByStartDateBetween | where x.startDate between ?1 and ?2 |
| LessThan | findByAgeLessThan | where x.age < ?1 |
| GreaterThan | findByAgeGreaterThan | where x.age > ?1 |
| After | findByStartDateAfter | where x.startDate > ?1 |
| Before | findByStartDateBefore | where x.startDate < ?1 |
| IsNull | findByAgeIsNull | where x.age is null |
| IsNotNull, NotNull | findByAge(Is)NotNull | where x.age not null |
| Like | findByFirstnameLike | where x.firstname like ?1 |
| NotLike | findByFirstnameNotLike | where x.firstname not like ?1 |
| StartingWith | findByFirstnameStartingWith | where x.firstname like ?1 (parameter bound with appended %) |
| EndingWith | findByFirstnameEndingWith | where x.firstname like ?1 (parameter bound with prepended %) |
| Containing | findByFirstnameContaining | where x.firstname like ?1 (parameter bound wrapped in %) |
| OrderBy | findByAgeOrderByLastnameDesc | where x.age = ?1 order by x.lastname desc |
| Not | findByLastnameNot | where x.lastname <> ?1 |

### 复杂查询示例

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 使用Distinct去重
    List<User> findDistinctByRole(UserRole role);
    
    // 忽略大小写查询
    List<User> findByUsernameIgnoreCase(String username);
    
    // 使用IN查询
    List<User> findByRoleIn(Collection<UserRole> roles);
    
    // 使用NOT IN查询
    List<User> findByRoleNotIn(Collection<UserRole> roles);
    
    // 使用TRUE/FALSE查询
    List<User> findByActiveTrue();
    List<User> findByActiveFalse();
    
    // 使用LIKE查询
    List<User> findByEmailLike(String email);
    
    // 使用ORDER BY排序
    List<User> findByRoleOrderByUsernameAsc(UserRole role);
    
    // 多级排序
    List<User> findByRoleOrderByCreatedAtDescUsernameAsc(UserRole role);
}
```

## JPQL查询

### 使用@Query注解

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // JPQL查询
    @Query("SELECT u FROM User u WHERE u.email = ?1")
    User findByEmail(String email);
    
    // 命名参数
    @Query("SELECT u FROM User u WHERE u.firstName = :firstName AND u.lastName = :lastName")
    List<User> findByFullName(@Param("firstName") String firstName, @Param("lastName") String lastName);
    
    // 更新操作
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.role = :role WHERE u.id IN :ids")
    int updateRoles(@Param("role") UserRole role, @Param("ids") List<Long> ids);
    
    // 删除操作
    @Modifying
    @Transactional
    @Query("DELETE FROM User u WHERE u.createdAt < :date")
    int deleteUsersCreatedBefore(@Param("date") LocalDateTime date);
    
    // 使用原生SQL
    @Query(value = "SELECT * FROM users WHERE email LIKE %:pattern%", nativeQuery = true)
    List<User> findUsersByEmailPattern(@Param("pattern") String pattern);
}
```

### 使用示例类查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 使用示例类查询
    default List<User> findByExample(User probe) {
        ExampleMatcher matcher = ExampleMatcher.matching()
                .withIgnoreCase()
                .withStringMatcher(ExampleMatcher.StringMatcher.CONTAINING);
        Example<User> example = Example.of(probe, matcher);
        return findAll(example);
    }
}
```

## 原生SQL查询

### 基本原生SQL查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 基本原生SQL查询
    @Query(value = "SELECT * FROM users WHERE username = ?1", nativeQuery = true)
    User findByUsernameNative(String username);
    
    // 使用命名参数
    @Query(value = "SELECT * FROM users WHERE email LIKE CONCAT('%', :email, '%')", nativeQuery = true)
    List<User> findByEmailContainingNative(@Param("email") String email);
    
    // 分页原生SQL查询
    @Query(value = "SELECT * FROM users WHERE role = :role",
           countQuery = "SELECT COUNT(*) FROM users WHERE role = :role",
           nativeQuery = true)
    Page<User> findByRoleNative(@Param("role") String role, Pageable pageable);
}
```

### 存储过程调用

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 调用存储过程
    @Procedure(name = "User.countByRole")
    int countByRoleProcedure(@Param("role") String role);
    
    // 或者直接指定存储过程名称
    @Procedure("count_users_by_role")
    int countUsersByRole(@Param("role") String role);
}
```

## 事务管理

### 声明式事务

```java
@Service
@Transactional(readOnly = true)
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    @Transactional
    public User saveUser(User user) {
        return userRepository.save(user);
    }
    
    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
    
    // 在方法级别覆盖类级别的事务配置
    @Transactional(readOnly = false, propagation = Propagation.REQUIRES_NEW)
    public User updateUser(User user) {
        return userRepository.save(user);
    }
}
```

### 编程式事务

```java
@Service
public class UserService {
    
    @Autowired
    private TransactionTemplate transactionTemplate;
    
    public User saveUserWithProgrammaticTransaction(User user) {
        return transactionTemplate.execute(status -> {
            try {
                // 业务逻辑
                return userRepository.save(user);
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

### 事务传播行为

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private OrderService orderService;
    
    @Transactional(propagation = Propagation.REQUIRED)
    public void createUserAndOrder(User user, Order order) {
        User savedUser = userRepository.save(user);
        order.setUser(savedUser);
        orderService.createOrder(order); // 如果OrderService.createOrder也有@Transactional，则使用相同的事务
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void createUserInNewTransaction(User user) {
        userRepository.save(user); // 在新的事务中执行
    }
}
```

## 审计功能

### 启用JPA审计

```java
@Configuration
@EnableJpaAuditing
public class JpaConfig {
    // 配置类
}
```

### 审计实体基类

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
@Data
public abstract class AuditableEntity {
    
    @CreatedBy
    @Column(name = "created_by")
    private String createdBy;
    
    @CreatedDate
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @LastModifiedBy
    @Column(name = "modified_by")
    private String modifiedBy;
    
    @LastModifiedDate
    @Column(name = "modified_at")
    private LocalDateTime modifiedAt;
}
```

### 使用审计功能

```java
@Entity
@Table(name = "products")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class Product extends AuditableEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column
    private BigDecimal price;
}
```

### 配置审计用户

```java
@Configuration
public class AuditConfig {
    
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
                .map(SecurityContext::getAuthentication)
                .filter(Authentication::isAuthenticated)
                .map(Authentication::getName)
                .or(() -> Optional.of("SYSTEM"));
    }
}
```

## 分页和排序

### 分页查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 使用Pageable参数进行分页查询
    Page<User> findByRole(UserRole role, Pageable pageable);
    
    // 使用Sort参数进行排序查询
    List<User> findByRole(UserRole role, Sort sort);
}
```

### 使用示例

```java
@Service
@Transactional(readOnly = true)
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public Page<User> getUsersByRole(UserRole role, int page, int size, String sortBy) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sortBy));
        return userRepository.findByRole(role, pageable);
    }
    
    public List<User> getUsersSortedByRole(UserRole role, String sortBy) {
        Sort sort = Sort.by(sortBy);
        return userRepository.findByRole(role, sort);
    }
}
```

### 控制器中的分页使用

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<Page<User>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "id") String sortBy,
            @RequestParam(required = false) UserRole role) {
        
        Page<User> users;
        if (role != null) {
            users = userService.getUsersByRole(role, page, size, sortBy);
        } else {
            Pageable pageable = PageRequest.of(page, size, Sort.by(sortBy));
            users = userService.getAllUsers(pageable);
        }
        
        return ResponseEntity.ok(users);
    }
}
```

## 关联关系处理

### 延迟加载和急加载

```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // 急加载 - 立即加载订单信息
    @OneToMany(mappedBy = "user", fetch = FetchType.EAGER, cascade = CascadeType.ALL)
    private List<Order> orders = new ArrayList<>();
    
    // 延迟加载 - 需要时才加载地址信息
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    private List<Address> addresses = new ArrayList<>();
}
```

### 使用@JoinFetch优化查询

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long>, JpaSpecificationExecutor<User> {
    
    // 使用JOIN FETCH避免N+1问题
    @Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
    Optional<User> findByIdWithOrders(@Param("id") Long id);
    
    // 使用LEFT JOIN FETCH处理可能为空的关联
    @Query("SELECT u FROM User u LEFT JOIN FETCH u.addresses WHERE u.id = :id")
    Optional<User> findByIdWithAddresses(@Param("id") Long id);
}
```

### 实体图（Entity Graph）

```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EntityGraphs({
    @EntityGraph(name = "User.withOrders", attributePaths = {"orders"}),
    @EntityGraph(name = "User.withAddresses", attributePaths = {"addresses"})
})
public class User {
    // 实体类定义
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 使用实体图
    @EntityGraph("User.withOrders")
    Optional<User> findById(Long id);
    
    // 动态实体图
    @EntityGraph(attributePaths = {"orders", "addresses"})
    List<User> findByRole(UserRole role);
}
```

## 性能优化

### 批量操作

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 批量插入
    @Modifying
    @Transactional
    @Query("INSERT INTO User(username, email, role) VALUES (:username, :email, :role)")
    int insertUser(@Param("username") String username, @Param("email") String email, @Param("role") UserRole role);
    
    // 批量更新
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.role = :role WHERE u.id IN :ids")
    int updateRolesInBatch(@Param("role") UserRole role, @Param("ids") List<Long> ids);
}
```

### 使用@BatchSize优化集合加载

```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // 设置批量大小以优化集合加载
    @BatchSize(size = 10)
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    private List<Order> orders = new ArrayList<>();
}
```

### 查询缓存

```java
// 启用二级缓存
// application.properties
spring.jpa.properties.hibernate.cache.use_second_level_cache=true
spring.jpa.properties.hibernate.cache.region.factory_class=org.hibernate.cache.ehcache.EhCacheRegionFactory

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Cacheable
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class User {
    // 实体类定义
}
```

## 最佳实践

### 1. Repository设计

```java
// 使用Fragment接口分离复杂查询逻辑
public interface UserRepositoryCustom {
    List<User> findUsersWithComplexCriteria(UserSearchCriteria criteria);
}

public interface UserRepository extends JpaRepository<User, Long>, UserRepositoryCustom {
    // 基本查询方法
}

@Repository
public class UserRepositoryImpl implements UserRepositoryCustom {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public List<User> findUsersWithComplexCriteria(UserSearchCriteria criteria) {
        // 复杂查询实现
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> root = query.from(User.class);
        
        // 构建查询条件
        List<Predicate> predicates = new ArrayList<>();
        
        if (criteria.getUsername() != null) {
            predicates.add(cb.like(root.get("username"), "%" + criteria.getUsername() + "%"));
        }
        
        if (criteria.getRole() != null) {
            predicates.add(cb.equal(root.get("role"), criteria.getRole()));
        }
        
        query.where(predicates.toArray(new Predicate[0]));
        
        return entityManager.createQuery(query).getResultList();
    }
}
```

### 2. 事务边界控制

```java
@Service
@Transactional(readOnly = true)
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
    }
    
    @Transactional
    public User createUser(CreateUserRequest request) {
        // 验证用户名唯一性
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new UsernameAlreadyExistsException("Username already exists: " + request.getUsername());
        }
        
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setRole(request.getRole());
        
        return userRepository.save(user);
    }
    
    // 对于只读操作，明确指定readOnly = true
    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}
```

### 3. 异常处理

```java
// 自定义异常
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}

public class UsernameAlreadyExistsException extends RuntimeException {
    public UsernameAlreadyExistsException(String message) {
        super(message);
    }
}

// 全局异常处理
@ControllerAdvice
public class DataAccessExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException ex) {
        ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(UsernameAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleUsernameExists(UsernameAlreadyExistsException ex) {
        ErrorResponse error = new ErrorResponse("USERNAME_EXISTS", ex.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }
}
```

### 4. DTO转换

```java
// 使用MapStruct进行高效转换
@Mapper
public interface UserMapper {
    UserMapper INSTANCE = Mappers.getMapper(UserMapper.class);
    
    UserDto toDto(User user);
    User toEntity(UserDto userDto);
    List<UserDto> toDtoList(List<User> users);
}

// 在Service中使用
@Service
@Transactional(readOnly = true)
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private UserMapper userMapper;
    
    public List<UserDto> getAllUsers() {
        List<User> users = userRepository.findAll();
        return userMapper.toDtoList(users);
    }
    
    public UserDto getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
        return userMapper.toDto(user);
    }
}
```

## 总结

本章详细介绍了Spring Data JPA的核心概念和使用方法，包括：

1. **Spring Data JPA简介**：理解其优势和核心理念
2. **核心概念**：Repository模式、JpaRepository接口等
3. **环境搭建**：Maven依赖和配置文件设置
4. **实体类映射**：基本映射、关联关系、枚举类型等
5. **Repository接口**：基本CRUD操作和自定义查询方法
6. **查询方法**：方法名查询规则和复杂查询示例
7. **JPQL查询**：使用@Query注解和示例类查询
8. **原生SQL查询**：基本原生SQL和存储过程调用
9. **事务管理**：声明式和编程式事务、传播行为
10. **审计功能**：启用审计、审计实体基类、配置审计用户
11. **分页和排序**：Pageable和Sort的使用
12. **关联关系处理**：延迟加载、急加载、实体图等
13. **性能优化**：批量操作、查询缓存、@BatchSize等
14. **最佳实践**：Repository设计、事务控制、异常处理、DTO转换等

Spring Data JPA极大地简化了数据访问层的开发工作，通过合理的使用可以显著提高开发效率并减少错误。掌握这些核心概念和最佳实践对于构建高性能、可维护的数据访问层至关重要。