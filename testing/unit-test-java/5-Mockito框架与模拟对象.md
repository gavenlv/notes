# 第5章：Mockito框架与模拟对象

## 5.1 Mock对象基础

### 5.1.1 什么是Mock对象

Mock对象是在测试中用来替代真实对象的模拟对象，它具有以下特点：

- **可控制**：可以预设行为和返回值
- **可观察**：可以验证交互是否按预期发生
- **隔离性**：将被测对象与外部依赖隔离
- **快速性**：通常比真实对象执行更快

```java
// 不使用Mock的测试示例
public class UserServiceWithoutMockTest {
    
    @Test
    public void testUserService() {
        // 需要真实的数据库连接，测试复杂且慢
        DatabaseConnection db = new DatabaseConnection();
        db.connect("localhost:3306", "user", "password");
        
        UserService service = new UserService(db);
        User user = service.getUser(1);
        
        assertNotNull(user);
        // 测试依赖于数据库状态，不稳定
    }
}

// 使用Mock的测试示例
public class UserServiceWithMockTest {
    
    private UserRepository mockRepository;
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        // 创建Mock对象
        mockRepository = mock(UserRepository.class);
        userService = new UserService(mockRepository);
    }
    
    @Test
    public void testGetUser() {
        // 预设Mock对象行为
        User expectedUser = new User(1, "test-user");
        when(mockRepository.findById(1)).thenReturn(expectedUser);
        
        // 执行测试
        User actualUser = userService.getUser(1);
        
        // 验证结果
        assertNotNull(actualUser);
        assertEquals("test-user", actualUser.getName());
        
        // 验证交互
        verify(mockRepository).findById(1);
    }
}
```

### 5.1.2 何时使用Mock对象

Mock对象适用于以下场景：

1. **依赖外部系统**：数据库、网络服务、文件系统
2. **执行速度慢**：需要长时间初始化或执行的对象
3. **难以构造**：构造函数复杂或需要特定配置的对象
4. **行为不确定性**：如时间、随机数生成器等
5. **需要验证交互**：关心对象间的交互而非最终状态

```java
// 适合使用Mock的场景示例

public class NotificationServiceTest {
    
    private EmailService emailService;
    private SMSService smsService;
    private UserRepository userRepository;
    private NotificationService notificationService;
    
    @BeforeEach
    void setUp() {
        // 所有依赖都使用Mock对象
        emailService = mock(EmailService.class);
        smsService = mock(SMSService.class);
        userRepository = mock(UserRepository.class);
        
        notificationService = new NotificationService(
            emailService, smsService, userRepository);
    }
    
    @Test
    void testSendEmailNotification() {
        // 准备数据
        User user = new User(1, "test@example.com", "123456789");
        when(userRepository.findById(1)).thenReturn(user);
        when(emailService.sendEmail(anyString(), anyString())).thenReturn(true);
        
        // 执行测试
        boolean result = notificationService.sendEmailNotification(1, "测试消息");
        
        // 验证结果
        assertTrue(result);
        
        // 验证交互
        verify(userRepository).findById(1);
        verify(emailService).sendEmail("test@example.com", "测试消息");
        verifyNoInteractions(smsService);  // 确保没有发送短信
    }
    
    @Test
    void testSendSMSNotification() {
        User user = new User(1, "test@example.com", "123456789");
        when(userRepository.findById(1)).thenReturn(user);
        when(smsService.sendSMS(anyString(), anyString())).thenReturn(true);
        
        boolean result = notificationService.sendSMSNotification(1, "测试短信");
        
        assertTrue(result);
        verify(userRepository).findById(1);
        verify(smsService).sendSMS("123456789", "测试短信");
        verifyNoInteractions(emailService);
    }
}
```

## 5.2 Mockito基础使用

### 5.2.1 创建Mock对象

Mockito提供了多种创建Mock对象的方式：

```java
import static org.mockito.Mockito.*;

public class MockCreationDemo {
    
    @Test
    public void basicMockCreation() {
        // 方式1：使用mock()方法
        List<String> mockList = mock(List.class);
        Map<String, Integer> mockMap = mock(Map.class);
        
        // Mock对象默认返回默认值
        assertNull(mockList.get(0));  // 返回null
        assertEquals(0, mockList.size());  // 返回0
        assertFalse(mockList.contains("anything"));  // 返回false
        
        // 方式2：使用@Mock注解（需要MockitoExtension）
        MockitoAnnotations.openMocks(this);  // 或者使用JUnit Jupiter扩展
        
        // 方式3：Mock特定实现类
        ArrayList<String> mockArrayList = mock(ArrayList.class);
        
        // 方式4：Mock接口并指定额外接口
        List<String> mockWithExtraInterface = mock(
            List.class, 
            withSettings().extraInterfaces(Comparable.class)
        );
    }
    
    // 使用@Mock注解创建Mock对象
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    @Test
    public void annotatedMockCreation() {
        // @Mock注解的字段已经被初始化为Mock对象
        assertNotNull(userRepository);
        assertNotNull(emailService);
    }
    
    @Test
    public void mockWithSpecificBehavior() {
        // 创建带有特定行为的Mock
        UserService mockUserService = mock(UserService.class);
        
        // 默认情况下，未定义的方法返回默认值
        assertNull(mockUserService.getUser(1));
        
        // 但可以覆盖默认行为
        User user = new User(1, "mocked-user");
        when(mockUserService.getUser(1)).thenReturn(user);
        
        assertEquals("mocked-user", mockUserService.getUser(1).getName());
    }
}
```

### 5.2.2 预设Mock行为

使用`when().thenReturn()`和`when().thenThrow()`预设Mock对象行为：

```java
public class MockBehaviorDemo {
    
    private UserRepository userRepository;
    private EmailService emailService;
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        emailService = mock(EmailService.class);
        userService = new UserService(userRepository, emailService);
    }
    
    @Test
    public void basicStubbing() {
        // 基本预设：特定参数返回特定值
        User user1 = new User(1, "user1");
        when(userRepository.findById(1)).thenReturn(user1);
        
        assertEquals("user1", userService.getUserName(1));
        
        // 不同参数返回不同值
        User user2 = new User(2, "user2");
        when(userRepository.findById(2)).thenReturn(user2);
        
        assertEquals("user2", userService.getUserName(2));
        
        // 未预设的参数返回默认值
        assertNull(userService.getUserName(3));
    }
    
    @Test
    public void conditionalStubbing() {
        // 使用any()匹配器
        when(userRepository.exists(anyInt())).thenReturn(true);
        
        assertTrue(userService.userExists(1));
        assertTrue(userService.userExists(999));
        assertTrue(userService.userExists(-1));
        
        // 使用特定匹配器
        when(userRepository.findByName(startsWith("admin"))).thenReturn(
            Arrays.asList(new User(1, "admin1"), new User(2, "admin2"))
        );
        
        List<User> admins = userService.getUsersByName("admin-users");
        assertEquals(2, admins.size());
        
        // 组合匹配器
        when(userRepository.findByEmail(and(contains("@"), endsWith(".com"))))
            .thenReturn(new User(3, "domain-user"));
        
        User domainUser = userService.getUserByEmail("user@domain.com");
        assertEquals("domain-user", domainUser.getName());
    }
    
    @Test
    public void exceptionStubbing() {
        // 预设抛出异常
        when(userRepository.findById(-1))
            .thenThrow(new IllegalArgumentException("用户ID不能为负数"));
        
        assertThrows(IllegalArgumentException.class, () -> {
            userService.getUserName(-1);
        });
        
        // 为void方法预设异常
        doThrow(new IllegalStateException("数据库不可用"))
            .when(userRepository).save(any(User.class));
        
        assertThrows(IllegalStateException.class, () -> {
            userService.createUser(new User("new-user"));
        });
    }
    
    @Test
    public void consecutiveStubbing() {
        // 连续调用返回不同值
        when(userRepository.findById(1))
            .thenReturn(new User(1, "first-call"))
            .thenReturn(new User(1, "second-call"))
            .thenReturn(new User(1, "third-call"))
            .thenThrow(new RuntimeException("不再提供服务"));
        
        assertEquals("first-call", userService.getUserName(1));
        assertEquals("second-call", userService.getUserName(1));
        assertEquals("third-call", userService.getUserName(1));
        
        assertThrows(RuntimeException.class, () -> {
            userService.getUserName(1);
        });
    }
    
    @Test
    public void stubbingWithAnswer() {
        // 使用Answer自定义返回逻辑
        when(userRepository.findById(anyInt())).thenAnswer(invocation -> {
            Integer id = invocation.getArgument(0);
            return new User(id, "user-" + id);
        });
        
        assertEquals("user-5", userService.getUserName(5));
        assertEquals("user-100", userService.getUserName(100));
    }
}
```

### 5.2.3 验证Mock交互

使用`verify()`方法验证Mock对象是否按预期被调用：

```java
public class MockVerificationDemo {
    
    private UserRepository userRepository;
    private EmailService emailService;
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        emailService = mock(EmailService.class);
        userService = new UserService(userRepository, emailService);
    }
    
    @Test
    public void basicVerification() {
        User user = new User(1, "test-user");
        when(userRepository.findById(1)).thenReturn(user);
        when(emailService.sendEmail(anyString(), anyString())).thenReturn(true);
        
        // 执行操作
        userService.sendWelcomeEmail(1);
        
        // 基本验证：检查方法是否被调用
        verify(userRepository).findById(1);
        verify(emailService).sendEmail("test-user@example.com", "欢迎邮件");
        
        // 验证调用次数
        verify(userRepository, times(1)).findById(1);
        verify(emailService, times(1)).sendEmail(anyString(), anyString());
        
        // 验证没有额外调用
        verifyNoMoreInteractions(userRepository, emailService);
    }
    
    @Test
    public void atMostAndAtLeastVerification() {
        User user = new User(1, "test-user");
        when(userRepository.findById(1)).thenReturn(user);
        
        // 多次调用
        userService.getUserName(1);
        userService.getUserName(1);
        userService.getUserName(1);
        
        // 验证调用次数范围
        verify(userRepository, atLeast(2)).findById(1);
        verify(userRepository, atMost(5)).findById(1);
        verify(userRepository, between(2, 5)).findById(1);
        
        // 验证精确次数
        verify(userRepository, times(3)).findById(1);
    }
    
    @Test
    public void timeoutVerification() {
        // 异步操作可能需要时间
        when(userRepository.findById(1)).thenReturn(new User(1, "async-user"));
        
        // 模拟异步操作
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(100);
                userService.getUserName(1);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        // 验证在指定时间内被调用
        verify(userRepository, timeout(200)).findById(1);
        
        // 验证在指定时间内至少调用指定次数
        // verify(userRepository, timeout(200).atLeast(2)).findById(1);
    }
    
    @Test
    public void verificationWithMatchers() {
        // 验证特定参数调用
        userService.createUser("user1", "user1@example.com");
        userService.createUser("admin", "admin@domain.com");
        
        verify(userRepository).save(argThat(user -> 
            user.getName().equals("user1")));
        
        verify(emailService).sendEmail(endsWith("@example.com"), anyString());
        
        // 验证没有调用特定参数
        verify(userRepository, never()).save(argThat(user -> 
            user.getName().equals("nonexistent")));
    }
    
    @Test
    public void inOrderVerification() {
        // 验证调用顺序
        InOrder inOrder = inOrder(userRepository, emailService);
        
        userService.createUserWithNotification("ordered-user");
        
        // 验证按顺序调用
        inOrder.verify(userRepository).save(any(User.class));
        inOrder.verify(emailService).sendEmail(anyString(), anyString());
    }
    
    @Test
    public void verifyNoInteractions() {
        // 确保某些Mock对象完全没有被调用
        PaymentService paymentService = mock(PaymentService.class);
        
        userService.updateProfile(1, "new-name");
        
        // 确保支付服务没有被调用
        verifyNoInteractions(paymentService);
        
        // 确保特定Mock对象的额外调用
        verify(paymentService, never()).processPayment(any());
    }
}
```

## 5.3 高级Mockito特性

### 5.3.1 参数匹配器

Mockito提供了丰富的参数匹配器来灵活匹配方法调用：

```java
public class ArgumentMatcherDemo {
    
    private UserRepository userRepository;
    private EmailService emailService;
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        emailService = mock(EmailService.class);
        userService = new UserService(userRepository, emailService);
    }
    
    @Test
    public void basicMatchers() {
        User user = new User(1, "test-user");
        when(userRepository.findById(anyInt())).thenReturn(user);
        when(userRepository.findByName(anyString())).thenReturn(Arrays.asList(user));
        when(userRepository.save(any(User.class))).thenReturn(user);
        
        // 使用any()匹配器
        assertEquals("test-user", userService.getUserName(123));
        assertEquals(1, userService.getUsersByName("any-name").size());
        
        User newUser = userService.createUser("new-user", "new@example.com");
        assertEquals("test-user", newUser.getName());  // 返回预设的Mock对象
    }
    
    @Test
    public void specificMatchers() {
        when(userRepository.findById(eq(1))).thenReturn(new User(1, "specific-user"));
        when(userRepository.findByName(startsWith("admin"))).thenReturn(
            Arrays.asList(new User(2, "admin1"), new User(3, "admin2"))
        );
        when(userRepository.findByEmail(endsWith("@domain.com"))).thenReturn(
            new User(4, "domain-user")
        );
        
        assertEquals("specific-user", userService.getUserName(1));
        assertEquals(2, userService.getUsersByName("admin-user").size());
        assertEquals("domain-user", userService.getUserByEmail("user@domain.com").getName());
        
        // 不匹配的调用返回默认值
        assertNull(userService.getUserName(2));
        assertEquals(0, userService.getUsersByName("regular-user").size());
    }
    
    @Test
    public void customArgumentMatchers() {
        // 自定义匹配器：验证邮箱格式
        when(userRepository.findByEmail(argThat(email -> 
            email != null && email.contains("@") && email.contains(".")))).thenReturn(
                new User(5, "email-user"));
        
        assertEquals("email-user", userService.getUserByEmail("valid@domain.com").getName());
        assertNull(userService.getUserByEmail("invalid-email"));
        
        // 自定义匹配器：验证用户对象
        when(userRepository.save(argThat(user -> 
            user.getName() != null && !user.getName().isEmpty() &&
            user.getEmail() != null && user.getEmail().contains("@")))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            user.setId(100);  // 模拟数据库分配ID
            return user;
        });
        
        User savedUser = userService.createUser("valid-user", "valid@domain.com");
        assertEquals(100, savedUser.getId());
    }
    
    @Test
    public void combinationMatchers() {
        when(userRepository.findByNameAndEmail(
            and(startsWith("test"), endsWith("user")),
            and(contains("@"), endsWith(".com"))
        )).thenReturn(Arrays.asList(new User(6, "testuser@domain.com")));
        
        List<User> users = userService.getUsersByNameAndEmail("testuser", "testuser@domain.com");
        assertEquals(1, users.size());
        assertEquals("testuser@domain.com", users.get(0).getName());
        
        // 使用or匹配器
        when(userRepository.findByName(or(eq("admin"), eq("superadmin")))).thenReturn(
            Arrays.asList(new User(7, "admin-user"))
        );
        
        List<User> adminUsers = userService.getUsersByName("admin");
        List<User> superAdminUsers = userService.getUsersByName("superadmin");
        
        assertEquals(1, adminUsers.size());
        assertEquals(1, superAdminUsers.size());
    }
    
    @Test
    public void argumentCaptor() {
        // 参数捕获器：捕获方法调用时的参数
        ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
        
        userService.createUser("captured-user", "captured@domain.com");
        
        // 验证save方法被调用，并捕获参数
        verify(userRepository).save(userCaptor.capture());
        
        // 检查捕获的参数
        User capturedUser = userCaptor.getValue();
        assertEquals("captured-user", capturedUser.getName());
        assertEquals("captured@domain.com", capturedUser.getEmail());
        
        // 多次调用的参数捕获
        ArgumentCaptor<String> emailCaptor = ArgumentCaptor.forClass(String.class);
        
        userService.sendEmailNotification(1, "message1");
        userService.sendEmailNotification(2, "message2");
        
        verify(emailService, times(2)).sendEmail(anyString(), emailCaptor.capture());
        
        List<String> capturedEmails = emailCaptor.getAllValues();
        assertEquals("message1", capturedEmails.get(0));
        assertEquals("message2", capturedEmails.get(1));
    }
}
```

### 5.3.2 Spy和部分Mock

Spy对象可以部分保留原始行为，只Mock特定方法：

```java
public class SpyDemo {
    
    @Test
    public void basicSpyUsage() {
        // 创建真实对象的Spy
        List<String> realList = new ArrayList<>();
        List<String> spyList = spy(realList);
        
        // Spy默认保留原始行为
        spyList.add("real");
        assertEquals(1, spyList.size());
        assertEquals("real", spyList.get(0));
        
        // 可以Mock特定方法
        when(spyList.size()).thenReturn(100);
        assertEquals(100, spyList.size());  // 调用Mock行为
        
        // 其他方法仍然保留原始行为
        assertEquals("real", spyList.get(0));
        
        // 验证调用
        verify(spyList).add("real");
    }
    
    @Test
    public void partialMockWithSpy() {
        // 使用注解创建Spy
        @SuppressWarnings("unchecked")
        List<String> spiedList = spy(ArrayList.class);
        
        // 使用doReturn()来Mock方法（推荐用于Spy）
        doReturn("mocked-value").when(spiedList).get(0);
        
        assertEquals("mocked-value", spiedList.get(0));  // Mock行为
        
        // 其他方法使用原始实现
        spiedList.add("real-value");
        assertEquals(1, spiedList.size());
        
        // 验证调用
        verify(spiedList).get(0);
        verify(spiedList).add("real-value");
    }
    
    @Test
    public void realServiceWithSpy() {
        // 真实服务对象
        RealUserService realService = new RealUserService();
        UserService spiedService = spy(realService);
        
        // 只Mock特定方法，其他方法使用真实实现
        when(spiedService.getExternalUserInfo(anyInt())).thenReturn(
            new User(1, "mocked-external-user"));
        
        // 测试真实实现的方法
        User user = spiedService.processUser(1);
        
        assertEquals("mocked-external-user", user.getName());  // Mock的方法
        assertNotNull(user.getProcessedAt());  // 真实实现的方法
        
        // 验证调用
        verify(spiedService).getExternalUserInfo(1);
    }
    
    @Test
    public void spyPitfalls() {
        // Spy的常见陷阱
        List<String> spiedList = spy(new ArrayList<>());
        
        // 陷阱：这样写会导致调用真实方法而不是Mock
        // when(spiedList.get(0)).thenReturn("mocked");  // 错误！
        
        // 正确的方式：使用doReturn()
        doReturn("mocked").when(spiedList).get(0);
        
        assertEquals("mocked", spiedList.get(0));
    }
    
    // 真实服务类示例
    static class RealUserService {
        public User getExternalUserInfo(int userId) {
            // 调用外部服务获取用户信息
            return new User(userId, "external-user-" + userId);
        }
        
        public User processUser(int userId) {
            User user = getExternalUserInfo(userId);
            user.setProcessedAt(LocalDateTime.now());
            return user;
        }
    }
}
```

### 5.3.3 注解扩展

使用MockitoExtension和注解简化Mock创建：

```java
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)  // 启用Mockito扩展
public class AnnotationExtensionDemo {
    
    // @Mock 创建Mock对象
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    @Mock
    private PaymentService paymentService;
    
    // @InjectMocks 创建实例并注入Mock依赖
    @InjectMocks
    private UserService userService;
    
    // @Captor 创建参数捕获器
    @Captor
    private ArgumentCaptor<User> userCaptor;
    
    @Captor
    private ArgumentCaptor<String> stringCaptor;
    
    @Test
    public void annotationBasedTest() {
        // Mock对象已经被自动创建和注入
        assertNotNull(userRepository);
        assertNotNull(emailService);
        assertNotNull(paymentService);
        assertNotNull(userService);
        
        // 预设Mock行为
        User user = new User(1, "annotation-user");
        when(userRepository.save(any(User.class))).thenReturn(user);
        when(emailService.sendEmail(anyString(), anyString())).thenReturn(true);
        
        // 执行测试
        User createdUser = userService.createUser("annotation-user", "user@example.com");
        
        // 验证结果
        assertEquals("annotation-user", createdUser.getName());
        
        // 验证交互
        verify(userRepository).save(userCaptor.capture());
        verify(emailService).sendEmail(stringCaptor.capture(), stringCaptor.capture());
        
        // 检查捕获的参数
        assertEquals("annotation-user", userCaptor.getValue().getName());
        assertEquals("user@example.com", stringCaptor.getAllValues().get(0));
        assertEquals("欢迎邮件", stringCaptor.getAllValues().get(1));
    }
    
    @Test
    public void resetAnnotationsTest() {
        // 使用后重置Mock（通常不推荐）
        reset(userRepository);
        
        // 重置后，Mock回到初始状态
        assertNull(userRepository.findById(1));
    }
    
    // 自定义Mock答案
    @Test
    public void customAnswerTest() {
        // 使用自定义Answer
        when(userRepository.findById(anyInt())).thenAnswer(invocation -> {
            Integer id = invocation.getArgument(0);
            if (id > 0 && id <= 100) {
                return new User(id, "valid-user-" + id);
            } else {
                throw new IllegalArgumentException("用户ID必须在1-100之间");
            }
        });
        
        // 测试有效ID
        User user1 = userService.getUserName(1);
        assertEquals("valid-user-1", user1.getName());
        
        User user50 = userService.getUserName(50);
        assertEquals("valid-user-50", user50.getName());
        
        // 测试无效ID
        assertThrows(IllegalArgumentException.class, () -> {
            userService.getUserName(101);
        });
    }
    
    // 静态方法Mock（需要Mockito-inline依赖）
    @Test
    public void staticMethodMockingTest() {
        try (MockedStatic<UUID> mockedUUID = mockStatic(UUID.class)) {
            UUID mockUUID = UUID.fromString("550e8400-e29b-41d4-a716-446655440000");
            mockedUUID.when(UUID::randomUUID).thenReturn(mockUUID);
            
            String generatedId = userService.generateUniqueId();
            assertEquals("550e8400-e29b-41d4-a716-446655440000", generatedId);
        }
    }
}
```

## 5.4 Mockito与JUnit集成

### 5.4.1 使用MockitoExtension

```java
@ExtendWith(MockitoExtension.class)
public class MockitoJUnitIntegration {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    @InjectMocks
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        // MockitoExtension会自动初始化@Mock和@InjectMocks字段
        // 不需要手动调用MockitoAnnotations.openMocks(this)
    }
    
    @Test
    public void testUserServiceWithMocks() {
        // 测试逻辑
        User user = new User(1, "integration-user");
        when(userRepository.findById(1)).thenReturn(user);
        
        User foundUser = userService.getUser(1);
        assertEquals("integration-user", foundUser.getName());
    }
    
    @Test
    public void testWithStrictness() {
        // 可以设置Mock的严格程度
        lenient().when(userRepository.findById(2)).thenReturn(new User(2, "lenient-user"));
        
        // lenient预设的方法可以不被调用，不会影响测试结果
        // 而普通的when预设如果不被调用，可能会影响Strictness
        
        assertEquals("integration-user", userService.getUser(1).getName());
    }
}
```

### 5.4.2 Mockito和JUnit Jupiter的最佳实践

```java
@ExtendWith(MockitoExtension.class)
@TestMethodOrder(OrderAnnotation.class)
public class MockitoBestPractices {
    
    // 1. 使用描述性名称
    @Mock
    private UserRepository userRepository;  // 清晰的Mock对象命名
    
    @Mock
    private EmailService emailService;     // 使用服务命名而非技术实现
    
    @Mock
    private NotificationGateway notificationGateway;  // 表明这是一个网关Mock
    
    @InjectMocks
    private UserService userService;
    
    @Captor
    private ArgumentCaptor<User> userArgumentCaptor;  // 描述性捕获器名称
    
    @Captor
    private ArgumentCaptor<NotificationMessage> messageArgumentCaptor;
    
    // 2. 使用有意义的测试方法名
    @Test
    @Order(1)
    @DisplayName("应该成功创建用户并发送欢迎邮件")
    public void shouldCreateUserAndSendWelcomeEmail() {
        // 3. 准备阶段（Arrange）
        String userName = "test-user";
        String userEmail = "test@example.com";
        User expectedUser = new User(userName, userEmail);
        
        when(userRepository.save(any(User.class))).thenReturn(expectedUser);
        when(emailService.sendEmail(anyString(), anyString())).thenReturn(true);
        
        // 4. 执行阶段（Act）
        User actualUser = userService.createUser(userName, userEmail);
        
        // 5. 验证阶段（Assert）
        assertEquals(userName, actualUser.getName(), "用户名应该匹配");
        assertEquals(userEmail, actualUser.getEmail(), "邮箱应该匹配");
        
        // 6. 验证交互（可选）
        verify(userRepository).save(userArgumentCaptor.capture());
        verify(emailService).sendEmail(eq(userEmail), anyString());
        
        User savedUser = userArgumentCaptor.getValue();
        assertEquals(userName, savedUser.getName(), "保存的用户名应该正确");
    }
    
    @Test
    @Order(2)
    @DisplayName("当邮箱无效时应该抛出异常且不保存用户")
    public void shouldThrowExceptionWhenEmailIsInvalid() {
        // 准备阶段
        String userName = "invalid-user";
        String invalidEmail = "invalid-email";  // 无效邮箱格式
        
        // 执行和验证阶段
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.createUser(userName, invalidEmail),
            "应该抛出IllegalArgumentException"
        );
        
        assertTrue(exception.getMessage().contains("邮箱格式不正确"), 
            "异常消息应该包含邮箱格式错误信息");
        
        // 验证没有执行保存操作
        verify(userRepository, never()).save(any(User.class));
        
        // 验证没有发送邮件
        verifyNoInteractions(emailService);
    }
    
    @Test
    @Order(3)
    @DisplayName("应该按正确顺序调用外部服务")
    public void shouldInvokeServicesInCorrectOrder() {
        // 准备阶段
        String userName = "sequence-user";
        String userEmail = "sequence@example.com";
        User user = new User(userName, userEmail);
        
        when(userRepository.save(any(User.class))).thenReturn(user);
        when(emailService.sendEmail(anyString(), anyString())).thenReturn(true);
        when(notificationGateway.send(any(NotificationMessage.class))).thenReturn(true);
        
        // 执行阶段
        userService.createUserWithNotifications(userName, userEmail);
        
        // 验证阶段 - 验证调用顺序
        InOrder inOrder = inOrder(userRepository, emailService, notificationGateway);
        
        inOrder.verify(userRepository).save(any(User.class));
        inOrder.verify(emailService).sendEmail(eq(userEmail), anyString());
        inOrder.verify(notificationGateway).send(messageArgumentCaptor.capture());
        
        NotificationMessage sentMessage = messageArgumentCaptor.getValue();
        assertEquals("欢迎", sentMessage.getType(), "应该发送欢迎消息");
    }
    
    // 7. 使用@DisplayName提供可读性强的测试描述
    @Test
    @DisplayName("应该正确处理部分服务调用失败的情况")
    public void shouldHandlePartialServiceFailureGracefully() {
        // 准备阶段
        when(userRepository.save(any(User.class))).thenThrow(
            new DatabaseException("数据库连接失败"));
        
        // 执行和验证阶段
        UserServiceException exception = assertThrows(
            UserServiceException.class,
            () -> userService.createUser("failure-user", "failure@example.com"),
            "应该抛出UserServiceException"
        );
        
        assertEquals("数据库操作失败", exception.getMessage(), 
            "异常消息应该反映数据库错误");
        
        // 验证没有尝试发送邮件（因为保存失败）
        verifyNoInteractions(emailService);
    }
}
```

## 5.5 Mockito测试模式

### 5.5.1 状态验证 vs 行为验证

```java
public class VerificationStylesDemo {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    @InjectMocks
    private UserService userService;
    
    // 状态验证（State Verification）
    // 关注系统的最终状态，而非交互过程
    @Test
    public void stateVerificationStyle() {
        // 准备阶段
        User expectedUser = new User(1, "state-user");
        when(userRepository.save(any(User.class))).thenReturn(expectedUser);
        
        // 执行阶段
        User createdUser = userService.createUser("state-user", "state@example.com");
        
        // 验证阶段：检查最终状态
        assertEquals(1, createdUser.getId(), "用户ID应该为1");
        assertEquals("state-user", createdUser.getName(), "用户名应该正确");
        
        // 不关心具体如何实现的，只关心结果是否正确
        // 不需要验证Mock的调用
    }
    
    // 行为验证（Behavior Verification）
    // 关注对象间的交互过程，确保正确的协作
    @Test
    public void behaviorVerificationStyle() {
        // 准备阶段
        User user = new User(1, "behavior-user");
        when(userRepository.save(any(User.class))).thenReturn(user);
        
        // 执行阶段
        userService.createUser("behavior-user", "behavior@example.com");
        
        // 验证阶段：检查交互过程
        verify(userRepository).save(argThat(u -> 
            "behavior-user".equals(u.getName()) && 
            "behavior@example.com".equals(u.getEmail())
        ));
        
        verify(emailService).sendEmail("behavior@example.com", contains("欢迎"));
        
        // 确保没有多余的交互
        verifyNoMoreInteractions(userRepository, emailService);
    }
    
    // 混合验证：既有状态验证又有行为验证
    @Test
    public void hybridVerificationStyle() {
        User user = new User(1, "hybrid-user");
        when(userRepository.save(any(User.class))).thenReturn(user);
        when(emailService.sendEmail(anyString(), anyString())).thenReturn(true);
        
        boolean result = userService.createUserWithNotification("hybrid-user", "hybrid@example.com");
        
        // 状态验证
        assertTrue(result, "创建和通知应该成功");
        
        // 行为验证
        verify(userRepository).save(any(User.class));
        verify(emailService).sendEmail(eq("hybrid@example.com"), anyString());
    }
}
```

### 5.5.2 测试替身模式

测试替身（Test Double）是一个通用概念，Mock只是其中一种：

```java
public class TestDoublePatterns {
    
    // 1. Test Stub（测试桩） - 返回预设答案
    @Test
    public void testStubPattern() {
        // Stub总是返回预设答案，不关心是否被调用
        UserRepository stubRepository = new UserRepositoryStub();
        UserService service = new UserService(stubRepository);
        
        User user = service.getUser(1);
        assertEquals("stub-user", user.getName());  // 总是返回相同值
    }
    
    // 2. Mock Object（模拟对象） - 可验证交互
    @Test
    public void mockObjectPattern() {
        UserRepository mockRepository = mock(UserRepository.class);
        UserService service = new UserService(mockRepository);
        
        when(mockRepository.findById(1)).thenReturn(new User(1, "mock-user"));
        
        User user = service.getUser(1);
        assertEquals("mock-user", user.getName());
        
        verify(mockRepository).findById(1);  // 验证交互
    }
    
    // 3. Test Spy（测试间谍） - 部分真实实现，部分监控
    @Test
    public void testSpyPattern() {
        UserRepository realRepository = new InMemoryUserRepository();
        UserRepository spyRepository = spy(realRepository);
        
        UserService service = new UserService(spyRepository);
        
        service.createUser("spy-user", "spy@example.com");
        
        // 验证方法是否被调用，同时保留真实行为
        verify(spyRepository).save(any(User.class));
        
        // 仍然可以验证真实结果
        User savedUser = spyRepository.findById(1);
        assertEquals("spy-user", savedUser.getName());
    }
    
    // 4. Fake Object（伪对象） - 简化实现但有工作逻辑
    @Test
    public void fakeObjectPattern() {
        // Fake是简化的实现，但实际执行逻辑
        UserRepository fakeRepository = new FakeUserRepository();
        UserService service = new UserService(fakeRepository);
        
        service.createUser("fake-user", "fake@example.com");
        User user = service.getUser(1);
        
        assertEquals("fake-user", user.getName());  // 真实的逻辑执行
        assertEquals(1, user.getId());  // 自动生成的ID
    }
    
    // 5. Dummy Object（虚拟对象） - 仅作为参数传递，不被使用
    @Test
    public void dummyObjectPattern() {
        // Dummy对象只用于填充参数，实际不会被使用
        DummyLogger dummyLogger = new DummyLogger();
        UserService service = new UserService(null, dummyLogger);
        
        // dummyLogger不会被调用，只是为了满足构造函数要求
        User user = new User("dummy-user");
        boolean result = service.validateUser(user);
        
        assertTrue(result, "用户应该有效");
    }
    
    // 简单的测试替身实现示例
    static class UserRepositoryStub implements UserRepository {
        @Override
        public User findById(int id) {
            return new User(id, "stub-user");
        }
        
        @Override
        public User save(User user) {
            return new User(1, "stub-user");
        }
        
        // 其他方法...
    }
    
    static class InMemoryUserRepository implements UserRepository {
        private Map<Integer, User> users = new HashMap<>();
        private int nextId = 1;
        
        @Override
        public User findById(int id) {
            return users.get(id);
        }
        
        @Override
        public User save(User user) {
            User savedUser = new User(nextId++, user.getName(), user.getEmail());
            users.put(savedUser.getId(), savedUser);
            return savedUser;
        }
        
        // 其他方法...
    }
    
    static class FakeUserRepository implements UserRepository {
        private Map<Integer, User> users = new HashMap<>();
        private int nextId = 1;
        
        @Override
        public User findById(int id) {
            return users.get(id);
        }
        
        @Override
        public User save(User user) {
            if (user.getName() == null || user.getEmail() == null) {
                throw new IllegalArgumentException("用户名和邮箱不能为空");
            }
            
            User savedUser = new User(nextId++, user.getName(), user.getEmail());
            users.put(savedUser.getId(), savedUser);
            return savedUser;
        }
        
        // 其他方法...
    }
    
    static class DummyLogger {
        // 空实现，不被使用
        public void log(String message) {
            // 什么都不做
        }
    }
}
```

## 5.6 小结

本章深入讲解了Mockito框架与模拟对象的使用，主要内容包括：

1. **Mock对象基础**：什么是Mock对象、何时使用以及基本创建方法
2. **Mockito基础使用**：创建Mock对象、预设行为、验证交互
3. **高级Mockito特性**：参数匹配器、Spy对象、注解扩展
4. **Mockito与JUnit集成**：MockitoExtension的使用和最佳实践
5. **测试模式**：状态验证vs行为验证、测试替身模式

掌握Mockito是编写隔离、可靠单元测试的关键技能。在下一章中，我们将学习参数化测试与测试套件，进一步提高测试效率。

## 5.7 实践练习

### 练习1：基本Mock使用
1. 创建一个服务类，依赖多个其他服务
2. 使用Mockito创建Mock对象
3. 预设Mock行为并验证交互

### 练习2：高级Mockito特性
1. 使用参数匹配器和参数捕获器
2. 创建Spy对象进行部分Mock
3. 使用自定义Answer实现复杂行为

### 练习3：测试模式实践
1. 比较状态验证和行为验证的测试编写方式
2. 实现不同类型的测试替身
3. 选择合适的测试替身解决实际问题

通过这些练习，您将掌握Mockito的核心使用技巧，能够编写高效、隔离的单元测试。