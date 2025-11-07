# 单元测试学习资源

本目录包含单元测试的学习资源、教程和最佳实践。单元测试是软件测试的一种方法，通过测试代码中的最小可测试单元（如函数、方法或类）来验证其行为是否符合预期。单元测试是保证代码质量、提高可维护性和支持重构的重要手段。

## 单元测试概述

单元测试是软件开发过程中不可或缺的一环，它通过验证代码中最小的可测试单元来确保代码质量和功能正确性。良好的单元测试能够帮助开发人员及早发现错误、提高代码可维护性、支持重构，并提供文档化的代码使用示例。单元测试通常与测试驱动开发(TDD)和行为驱动开发(BDD)等开发方法紧密结合。

## 目录结构

### 基础入门
- 单元测试概念与原则
- 测试金字塔理论
- FIRST原则（快速、独立、可重复、自验证、及时）
- AAA模式（Arrange、Act、Assert）

### 测试框架
- JUnit（Java）
- pytest（Python）
- Jest/Mocha（JavaScript）
- NUnit/xUnit（.NET）
- Google Test（C++）

### 测试技术
- 模拟对象(Mock Objects)
- 存根(Stubs)
- 测试替身(Test Doubles)
- 断言(Assertions)
- 参数化测试

### 测试设计
- 测试用例设计
- 边界值测试
- 等价类划分
- 决策表测试
- 状态转换测试

### 测试覆盖率
- 代码覆盖率概念
- 行覆盖率、分支覆盖率、路径覆盖率
- 覆盖率工具使用
- 覆盖率目标设定

### 测试实践
- 测试驱动开发(TDD)
- 行为驱动开发(BDD)
- 持续集成中的单元测试
- 重构与测试

### 高级主题
- 测试私有方法
- 异常测试
- 异步代码测试
- 性能测试

## 学习路径

### 初学者
1. 理解单元测试的基本概念和价值
2. 学习使用主流测试框架
3. 编写简单的测试用例
4. 掌握基本的断言和验证

### 进阶学习
1. 学习模拟对象和测试替身
2. 掌握测试设计技巧
3. 理解测试覆盖率概念
4. 实践TDD开发方法

### 高级应用
1. 设计复杂的测试场景
2. 优化测试性能和维护性
3. 集成测试到CI/CD流程
4. 指导团队测试实践

## 常见问题与解决方案

### 测试设计问题
- 测试用例设计不全面
- 测试与实现耦合度过高
- 测试难以维护和理解
- 测试数据管理不当

### 模拟与依赖问题
- 外部依赖隔离困难
- 模拟对象设置复杂
- 静态方法和私有方法测试
- 异步代码测试挑战

### 性能与维护问题
- 测试执行速度慢
- 测试套件不稳定
- 测试代码重复
- 测试环境配置复杂

## 资源链接

### 官方资源
- [JUnit 5官方文档](https://junit.org/junit5/docs/current/user-guide/)
- [pytest官方文档](https://docs.pytest.org/en/stable/)
- [Jest官方文档](https://jestjs.io/docs/getting-started)
- [NUnit官方文档](https://nunit.org/documentation/)
- [Google Test文档](https://google.github.io/googletest/)

### 学习资源
- [测试驱动开发 by Example](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [有效单元测试](https://www.manning.com/books/the-effective-unit-testing)
- [单元测试的艺术](https://www.amazon.com/Art-Unit-Testing-Examples/dp/1617290898)
- [测试金字塔](https://martinfowler.com/bliki/TestPyramid.html)

### 工具与平台
- [SonarQube](https://www.sonarqube.org/)
- [Coveralls](https://coveralls.io/)
- [Codecov](https://codecov.io/)
- [CircleCI](https://circleci.com/)

## 代码示例

### Java JUnit 5示例
```java
// 添加依赖
// testImplementation 'org.junit.jupiter:junit-jupiter:5.9.2'
// testImplementation 'org.mockito:mockito-core:5.1.1'
// testImplementation 'org.mockito:mockito-junit-jupiter:5.1.1'

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        userService = new UserService(userRepository, emailService);
    }
    
    @Test
    @DisplayName("应该成功创建用户")
    void shouldCreateUserSuccessfully() {
        // Arrange
        User user = new User("test@example.com", "password123");
        User savedUser = new User(1L, "test@example.com", "password123");
        
        when(userRepository.save(any(User.class))).thenReturn(savedUser);
        
        // Act
        User result = userService.createUser(user);
        
        // Assert
        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("test@example.com", result.getEmail());
        
        // 验证交互
        verify(userRepository).save(user);
        verify(emailService).sendWelcomeEmail(savedUser.getEmail());
    }
    
    @Test
    @DisplayName("当邮箱已存在时应该抛出异常")
    void shouldThrowExceptionWhenEmailAlreadyExists() {
        // Arrange
        User user = new User("existing@example.com", "password123");
        
        when(userRepository.existsByEmail("existing@example.com")).thenReturn(true);
        
        // Act & Assert
        assertThrows(UserAlreadyExistsException.class, () -> userService.createUser(user));
        
        // 验证交互
        verify(userRepository).existsByEmail("existing@example.com");
        verify(userRepository, never()).save(any(User.class));
        verify(emailService, never()).sendWelcomeEmail(anyString());
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"", "invalid-email", "a@b.c", "email@domain"})
    @DisplayName("当邮箱格式无效时应该抛出异常")
    void shouldThrowExceptionWhenEmailIsInvalid(String email) {
        // Arrange
        User user = new User(email, "password123");
        
        // Act & Assert
        assertThrows(InvalidEmailException.class, () -> userService.createUser(user));
    }
    
    @ParameterizedTest
    @CsvSource({
        "user1@example.com, password123, true",
        "user2@example.com, password456, true",
        "user3@example.com, wrongpassword, false",
        "nonexistent@example.com, password123, false"
    })
    @DisplayName("应该根据凭据正确验证用户")
    void shouldAuthenticateUserCorrectly(String email, String password, boolean expected) {
        // Arrange
        when(userRepository.findByEmail(email)).thenReturn(
            expected ? Optional.of(new User(1L, email, password)) : Optional.empty()
        );
        
        // Act
        boolean result = userService.authenticate(email, password);
        
        // Assert
        assertEquals(expected, result);
    }
    
    @Nested
    @DisplayName("用户更新测试")
    class UserUpdateTests {
        
        @Test
        @DisplayName("应该成功更新用户信息")
        void shouldUpdateUserSuccessfully() {
            // Arrange
            Long userId = 1L;
            User existingUser = new User(userId, "old@example.com", "oldpassword");
            User updatedUser = new User(userId, "new@example.com", "newpassword");
            
            when(userRepository.findById(userId)).thenReturn(Optional.of(existingUser));
            when(userRepository.save(any(User.class))).thenReturn(updatedUser);
            
            // Act
            User result = userService.updateUser(userId, updatedUser);
            
            // Assert
            assertNotNull(result);
            assertEquals("new@example.com", result.getEmail());
            assertEquals("newpassword", result.getPassword());
            
            // 验证交互
            verify(userRepository).findById(userId);
            verify(userRepository).save(existingUser);
        }
        
        @Test
        @DisplayName("当用户不存在时应该抛出异常")
        void shouldThrowExceptionWhenUserDoesNotExist() {
            // Arrange
            Long userId = 999L;
            User updatedUser = new User(userId, "new@example.com", "newpassword");
            
            when(userRepository.findById(userId)).thenReturn(Optional.empty());
            
            // Act & Assert
            assertThrows(UserNotFoundException.class, () -> userService.updateUser(userId, updatedUser));
            
            // 验证交互
            verify(userRepository).findById(userId);
            verify(userRepository, never()).save(any(User.class));
        }
    }
}

// 被测试的类
class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
    
    public User createUser(User user) {
        if (!isValidEmail(user.getEmail())) {
            throw new InvalidEmailException("Invalid email format");
        }
        
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new UserAlreadyExistsException("Email already exists");
        }
        
        User savedUser = userRepository.save(user);
        emailService.sendWelcomeEmail(savedUser.getEmail());
        
        return savedUser;
    }
    
    public boolean authenticate(String email, String password) {
        Optional<User> userOptional = userRepository.findByEmail(email);
        return userOptional.map(user -> user.getPassword().equals(password)).orElse(false);
    }
    
    public User updateUser(Long userId, User updatedUser) {
        Optional<User> userOptional = userRepository.findById(userId);
        if (userOptional.isEmpty()) {
            throw new UserNotFoundException("User not found");
        }
        
        User existingUser = userOptional.get();
        existingUser.setEmail(updatedUser.getEmail());
        existingUser.setPassword(updatedUser.getPassword());
        
        return userRepository.save(existingUser);
    }
    
    private boolean isValidEmail(String email) {
        return email != null && email.contains("@") && email.contains(".");
    }
}

// 模拟的依赖类
interface UserRepository {
    User save(User user);
    Optional<User> findById(Long id);
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
}

interface EmailService {
    void sendWelcomeEmail(String email);
}

class User {
    private Long id;
    private String email;
    private String password;
    
    public User(String email, String password) {
        this.email = email;
        this.password = password;
    }
    
    public User(Long id, String email, String password) {
        this.id = id;
        this.email = email;
        this.password = password;
    }
    
    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}

// 自定义异常类
class UserAlreadyExistsException extends RuntimeException {
    public UserAlreadyExistsException(String message) {
        super(message);
    }
}

class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}

class InvalidEmailException extends RuntimeException {
    public InvalidEmailException(String message) {
        super(message);
    }
}
```

### Python pytest示例
```python
# 添加依赖
# pip install pytest pytest-mock

import pytest
from unittest.mock import Mock, patch
from user_service import UserService, User, UserAlreadyExistsException, UserNotFoundException, InvalidEmailException

class TestUserService:
    
    @pytest.fixture
    def mock_user_repository(self):
        return Mock()
    
    @pytest.fixture
    def mock_email_service(self):
        return Mock()
    
    @pytest.fixture
    def user_service(self, mock_user_repository, mock_email_service):
        return UserService(mock_user_repository, mock_email_service)
    
    @pytest.fixture
    def sample_user(self):
        return User(email="test@example.com", password="password123")
    
    @pytest.fixture
    def saved_user(self):
        return User(id=1, email="test@example.com", password="password123")
    
    def test_create_user_successfully(self, user_service, mock_user_repository, mock_email_service, sample_user, saved_user):
        # Arrange
        mock_user_repository.save.return_value = saved_user
        mock_user_repository.exists_by_email.return_value = False
        
        # Act
        result = user_service.create_user(sample_user)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.email == "test@example.com"
        
        # 验证交互
        mock_user_repository.exists_by_email.assert_called_once_with("test@example.com")
        mock_user_repository.save.assert_called_once_with(sample_user)
        mock_email_service.send_welcome_email.assert_called_once_with(saved_user.email)
    
    def test_create_user_when_email_already_exists(self, user_service, mock_user_repository, mock_email_service, sample_user):
        # Arrange
        mock_user_repository.exists_by_email.return_value = True
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsException):
            user_service.create_user(sample_user)
        
        # 验证交互
        mock_user_repository.exists_by_email.assert_called_once_with("test@example.com")
        mock_user_repository.save.assert_not_called()
        mock_email_service.send_welcome_email.assert_not_called()
    
    @pytest.mark.parametrize("email", ["", "invalid-email", "a@b.c", "email@domain"])
    def test_create_user_with_invalid_email(self, user_service, mock_user_repository, mock_email_service, email):
        # Arrange
        user = User(email=email, password="password123")
        
        # Act & Assert
        with pytest.raises(InvalidEmailException):
            user_service.create_user(user)
        
        # 验证交互
        mock_user_repository.exists_by_email.assert_not_called()
        mock_user_repository.save.assert_not_called()
        mock_email_service.send_welcome_email.assert_not_called()
    
    @pytest.mark.parametrize("email,password,expected", [
        ("user1@example.com", "password123", True),
        ("user2@example.com", "password456", True),
        ("user3@example.com", "wrongpassword", False),
        ("nonexistent@example.com", "password123", False)
    ])
    def test_authenticate_user(self, user_service, mock_user_repository, email, password, expected):
        # Arrange
        if expected:
            user = User(id=1, email=email, password=password)
            mock_user_repository.find_by_email.return_value = user
        else:
            mock_user_repository.find_by_email.return_value = None
        
        # Act
        result = user_service.authenticate(email, password)
        
        # Assert
        assert result == expected
        mock_user_repository.find_by_email.assert_called_once_with(email)
    
    def test_update_user_successfully(self, user_service, mock_user_repository, sample_user):
        # Arrange
        user_id = 1
        existing_user = User(id=user_id, email="old@example.com", password="oldpassword")
        updated_user = User(id=user_id, email="new@example.com", password="newpassword")
        
        mock_user_repository.find_by_id.return_value = existing_user
        mock_user_repository.save.return_value = updated_user
        
        # Act
        result = user_service.update_user(user_id, updated_user)
        
        # Assert
        assert result is not None
        assert result.email == "new@example.com"
        assert result.password == "newpassword"
        
        # 验证交互
        mock_user_repository.find_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_called_once()
    
    def test_update_user_when_user_does_not_exist(self, user_service, mock_user_repository):
        # Arrange
        user_id = 999
        updated_user = User(id=user_id, email="new@example.com", password="newpassword")
        
        mock_user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundException):
            user_service.update_user(user_id, updated_user)
        
        # 验证交互
        mock_user_repository.find_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_not_called()
    
    @patch('user_service.datetime')
    def test_get_user_activity_report(self, mock_datetime, user_service, mock_user_repository):
        # Arrange
        mock_datetime.now.return_value = "2023-01-01"
        user1 = User(id=1, email="user1@example.com", password="password1")
        user2 = User(id=2, email="user2@example.com", password="password2")
        mock_user_repository.find_all.return_value = [user1, user2]
        
        # Act
        report = user_service.get_user_activity_report()
        
        # Assert
        assert report["date"] == "2023-01-01"
        assert len(report["users"]) == 2
        assert report["users"][0]["email"] == "user1@example.com"
        assert report["users"][1]["email"] == "user2@example.com"
        
        # 验证交互
        mock_user_repository.find_all.assert_called_once()

# 被测试的类
class UserService:
    def __init__(self, user_repository, email_service):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def create_user(self, user):
        if not self._is_valid_email(user.email):
            raise InvalidEmailException("Invalid email format")
        
        if self.user_repository.exists_by_email(user.email):
            raise UserAlreadyExistsException("Email already exists")
        
        saved_user = self.user_repository.save(user)
        self.email_service.send_welcome_email(saved_user.email)
        
        return saved_user
    
    def authenticate(self, email, password):
        user = self.user_repository.find_by_email(email)
        return user is not None and user.password == password
    
    def update_user(self, user_id, updated_user):
        existing_user = self.user_repository.find_by_id(user_id)
        if existing_user is None:
            raise UserNotFoundException("User not found")
        
        existing_user.email = updated_user.email
        existing_user.password = updated_user.password
        
        return self.user_repository.save(existing_user)
    
    def get_user_activity_report(self):
        from datetime import datetime
        users = self.user_repository.find_all()
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "users": [{"id": user.id, "email": user.email} for user in users]
        }
    
    def _is_valid_email(self, email):
        return email is not None and "@" in email and "." in email

# 模拟的依赖类
class User:
    def __init__(self, id=None, email=None, password=None):
        self.id = id
        self.email = email
        self.password = password

class UserAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class InvalidEmailException(Exception):
    pass
```

### JavaScript Jest示例
```javascript
// 安装依赖
// npm install --save-dev jest

// userService.js
class UserService {
  constructor(userRepository, emailService) {
    this.userRepository = userRepository;
    this.emailService = emailService;
  }

  createUser(user) {
    if (!this._isValidEmail(user.email)) {
      throw new Error('Invalid email format');
    }

    if (this.userRepository.existsByEmail(user.email)) {
      throw new Error('Email already exists');
    }

    const savedUser = this.userRepository.save(user);
    this.emailService.sendWelcomeEmail(savedUser.email);

    return savedUser;
  }

  authenticate(email, password) {
    const user = this.userRepository.findByEmail(email);
    return user && user.password === password;
  }

  updateUser(userId, updatedUser) {
    const existingUser = this.userRepository.findById(userId);
    if (!existingUser) {
      throw new Error('User not found');
    }

    existingUser.email = updatedUser.email;
    existingUser.password = updatedUser.password;

    return this.userRepository.save(existingUser);
  }

  getUserActivityReport() {
    const users = this.userRepository.findAll();
    
    return {
      date: new Date().toISOString().split('T')[0],
      users: users.map(user => ({
        id: user.id,
        email: user.email
      }))
    };
  }

  _isValidEmail(email) {
    return email && email.includes('@') && email.includes('.');
  }
}

module.exports = UserService;

// userService.test.js
const UserService = require('./userService');

describe('UserService', () => {
  let userService;
  let mockUserRepository;
  let mockEmailService;

  beforeEach(() => {
    mockUserRepository = {
      save: jest.fn(),
      findByEmail: jest.fn(),
      findById: jest.fn(),
      existsByEmail: jest.fn(),
      findAll: jest.fn()
    };

    mockEmailService = {
      sendWelcomeEmail: jest.fn()
    };

    userService = new UserService(mockUserRepository, mockEmailService);
  });

  describe('createUser', () => {
    it('should create user successfully', () => {
      // Arrange
      const user = { email: 'test@example.com', password: 'password123' };
      const savedUser = { id: 1, email: 'test@example.com', password: 'password123' };
      
      mockUserRepository.existsByEmail.mockReturnValue(false);
      mockUserRepository.save.mockReturnValue(savedUser);

      // Act
      const result = userService.createUser(user);

      // Assert
      expect(result).toEqual(savedUser);
      expect(mockUserRepository.existsByEmail).toHaveBeenCalledWith('test@example.com');
      expect(mockUserRepository.save).toHaveBeenCalledWith(user);
      expect(mockEmailService.sendWelcomeEmail).toHaveBeenCalledWith(savedUser.email);
    });

    it('should throw error when email already exists', () => {
      // Arrange
      const user = { email: 'existing@example.com', password: 'password123' };
      mockUserRepository.existsByEmail.mockReturnValue(true);

      // Act & Assert
      expect(() => userService.createUser(user)).toThrow('Email already exists');
      expect(mockUserRepository.existsByEmail).toHaveBeenCalledWith('existing@example.com');
      expect(mockUserRepository.save).not.toHaveBeenCalled();
      expect(mockEmailService.sendWelcomeEmail).not.toHaveBeenCalled();
    });

    it.each([
      '',
      'invalid-email',
      'a@b.c',
      'email@domain'
    ])('should throw error when email is invalid: %s', (email) => {
      // Arrange
      const user = { email, password: 'password123' };

      // Act & Assert
      expect(() => userService.createUser(user)).toThrow('Invalid email format');
      expect(mockUserRepository.existsByEmail).not.toHaveBeenCalled();
      expect(mockUserRepository.save).not.toHaveBeenCalled();
      expect(mockEmailService.sendWelcomeEmail).not.toHaveBeenCalled();
    });
  });

  describe('authenticate', () => {
    it.each([
      ['user1@example.com', 'password123', true],
      ['user2@example.com', 'password456', true],
      ['user3@example.com', 'wrongpassword', false],
      ['nonexistent@example.com', 'password123', false]
    ])('should authenticate user correctly: %s, %s -> %s', (email, password, expected) => {
      // Arrange
      if (expected) {
        mockUserRepository.findByEmail.mockReturnValue({ email, password });
      } else {
        mockUserRepository.findByEmail.mockReturnValue(null);
      }

      // Act
      const result = userService.authenticate(email, password);

      // Assert
      expect(result).toBe(expected);
      expect(mockUserRepository.findByEmail).toHaveBeenCalledWith(email);
    });
  });

  describe('updateUser', () => {
    it('should update user successfully', () => {
      // Arrange
      const userId = 1;
      const existingUser = { id: userId, email: 'old@example.com', password: 'oldpassword' };
      const updatedUser = { id: userId, email: 'new@example.com', password: 'newpassword' };
      
      mockUserRepository.findById.mockReturnValue(existingUser);
      mockUserRepository.save.mockReturnValue(updatedUser);

      // Act
      const result = userService.updateUser(userId, updatedUser);

      // Assert
      expect(result).toEqual(updatedUser);
      expect(mockUserRepository.findById).toHaveBeenCalledWith(userId);
      expect(mockUserRepository.save).toHaveBeenCalled();
    });

    it('should throw error when user does not exist', () => {
      // Arrange
      const userId = 999;
      const updatedUser = { id: userId, email: 'new@example.com', password: 'newpassword' };
      
      mockUserRepository.findById.mockReturnValue(null);

      // Act & Assert
      expect(() => userService.updateUser(userId, updatedUser)).toThrow('User not found');
      expect(mockUserRepository.findById).toHaveBeenCalledWith(userId);
      expect(mockUserRepository.save).not.toHaveBeenCalled();
    });
  });

  describe('getUserActivityReport', () => {
    it('should return user activity report', () => {
      // Arrange
      const users = [
        { id: 1, email: 'user1@example.com', password: 'password1' },
        { id: 2, email: 'user2@example.com', password: 'password2' }
      ];
      
      mockUserRepository.findAll.mockReturnValue(users);
      
      // 模拟当前日期
      const mockDate = new Date('2023-01-01');
      jest.spyOn(global, 'Date').mockImplementation(() => mockDate);

      // Act
      const report = userService.getUserActivityReport();

      // Assert
      expect(report.date).toBe('2023-01-01');
      expect(report.users).toHaveLength(2);
      expect(report.users[0]).toEqual({ id: 1, email: 'user1@example.com' });
      expect(report.users[1]).toEqual({ id: 2, email: 'user2@example.com' });
      
      // 恢复原始Date构造函数
      global.Date.mockRestore();
    });
  });
});
```

### C# xUnit示例
```csharp
// 添加依赖
// using Xunit
// using Moq

using System;
using System.Collections.Generic;
using Xunit;
using Moq;

public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockUserRepository;
    private readonly Mock<IEmailService> _mockEmailService;
    private readonly UserService _userService;

    public UserServiceTests()
    {
        _mockUserRepository = new Mock<IUserRepository>();
        _mockEmailService = new Mock<IEmailService>();
        _userService = new UserService(_mockUserRepository.Object, _mockEmailService.Object);
    }

    [Fact]
    public void CreateUser_ShouldCreateUserSuccessfully()
    {
        // Arrange
        var user = new User { Email = "test@example.com", Password = "password123" };
        var savedUser = new User { Id = 1, Email = "test@example.com", Password = "password123" };
        
        _mockUserRepository.Setup(r => r.ExistsByEmail(user.Email)).Returns(false);
        _mockUserRepository.Setup(r => r.Save(user)).Returns(savedUser);

        // Act
        var result = _userService.CreateUser(user);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(1, result.Id);
        Assert.Equal("test@example.com", result.Email);
        
        // 验证交互
        _mockUserRepository.Verify(r => r.ExistsByEmail(user.Email), Times.Once);
        _mockUserRepository.Verify(r => r.Save(user), Times.Once);
        _mockEmailService.Verify(e => e.SendWelcomeEmail(savedUser.Email), Times.Once);
    }

    [Fact]
    public void CreateUser_WhenEmailAlreadyExists_ShouldThrowException()
    {
        // Arrange
        var user = new User { Email = "existing@example.com", Password = "password123" };
        _mockUserRepository.Setup(r => r.ExistsByEmail(user.Email)).Returns(true);

        // Act & Assert
        Assert.Throws<UserAlreadyExistsException>(() => _userService.CreateUser(user));
        
        // 验证交互
        _mockUserRepository.Verify(r => r.ExistsByEmail(user.Email), Times.Once);
        _mockUserRepository.Verify(r => r.Save(It.IsAny<User>()), Times.Never);
        _mockEmailService.Verify(e => e.SendWelcomeEmail(It.IsAny<string>()), Times.Never);
    }

    [Theory]
    [InlineData("")]
    [InlineData("invalid-email")]
    [InlineData("a@b.c")]
    [InlineData("email@domain")]
    public void CreateUser_WhenEmailIsInvalid_ShouldThrowException(string email)
    {
        // Arrange
        var user = new User { Email = email, Password = "password123" };

        // Act & Assert
        Assert.Throws<InvalidEmailException>(() => _userService.CreateUser(user));
        
        // 验证交互
        _mockUserRepository.Verify(r => r.ExistsByEmail(It.IsAny<string>()), Times.Never);
        _mockUserRepository.Verify(r => r.Save(It.IsAny<User>()), Times.Never);
        _mockEmailService.Verify(e => e.SendWelcomeEmail(It.IsAny<string>()), Times.Never);
    }

    [Theory]
    [InlineData("user1@example.com", "password123", true)]
    [InlineData("user2@example.com", "password456", true)]
    [InlineData("user3@example.com", "wrongpassword", false)]
    [InlineData("nonexistent@example.com", "password123", false)]
    public void Authenticate_ShouldAuthenticateUserCorrectly(string email, string password, bool expected)
    {
        // Arrange
        if (expected)
        {
            _mockUserRepository.Setup(r => r.FindByEmail(email))
                .Returns(new User { Id = 1, Email = email, Password = password });
        }
        else
        {
            _mockUserRepository.Setup(r => r.FindByEmail(email))
                .Returns((User)null);
        }

        // Act
        var result = _userService.Authenticate(email, password);

        // Assert
        Assert.Equal(expected, result);
        _mockUserRepository.Verify(r => r.FindByEmail(email), Times.Once);
    }

    [Fact]
    public void UpdateUser_ShouldUpdateUserSuccessfully()
    {
        // Arrange
        var userId = 1;
        var existingUser = new User { Id = userId, Email = "old@example.com", Password = "oldpassword" };
        var updatedUser = new User { Id = userId, Email = "new@example.com", Password = "newpassword" };
        
        _mockUserRepository.Setup(r => r.FindById(userId)).Returns(existingUser);
        _mockUserRepository.Setup(r => r.Save(existingUser)).Returns(updatedUser);

        // Act
        var result = _userService.UpdateUser(userId, updatedUser);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("new@example.com", result.Email);
        Assert.Equal("newpassword", result.Password);
        
        // 验证交互
        _mockUserRepository.Verify(r => r.FindById(userId), Times.Once);
        _mockUserRepository.Verify(r => r.Save(existingUser), Times.Once);
    }

    [Fact]
    public void UpdateUser_WhenUserDoesNotExist_ShouldThrowException()
    {
        // Arrange
        var userId = 999;
        var updatedUser = new User { Id = userId, Email = "new@example.com", Password = "newpassword" };
        
        _mockUserRepository.Setup(r => r.FindById(userId)).Returns((User)null);

        // Act & Assert
        Assert.Throws<UserNotFoundException>(() => _userService.UpdateUser(userId, updatedUser));
        
        // 验证交互
        _mockUserRepository.Verify(r => r.FindById(userId), Times.Once);
        _mockUserRepository.Verify(r => r.Save(It.IsAny<User>()), Times.Never);
    }

    [Fact]
    public void GetUserActivityReport_ShouldReturnUserActivityReport()
    {
        // Arrange
        var users = new List<User>
        {
            new User { Id = 1, Email = "user1@example.com", Password = "password1" },
            new User { Id = 2, Email = "user2@example.com", Password = "password2" }
        };
        
        _mockUserRepository.Setup(r => r.FindAll()).Returns(users);
        
        // 模拟当前日期
        var mockDateTime = new DateTime(2023, 1, 1);
        var dateTimeProvider = new Mock<IDateTimeProvider>();
        dateTimeProvider.Setup(d => d.Now).Returns(mockDateTime);
        
        var userServiceWithMockDate = new UserService(_mockUserRepository.Object, _mockEmailService.Object, dateTimeProvider.Object);

        // Act
        var report = userServiceWithMockDate.GetUserActivityReport();

        // Assert
        Assert.Equal("2023-01-01", report.Date);
        Assert.Equal(2, report.Users.Count);
        Assert.Equal(1, report.Users[0].Id);
        Assert.Equal("user1@example.com", report.Users[0].Email);
        Assert.Equal(2, report.Users[1].Id);
        Assert.Equal("user2@example.com", report.Users[1].Email);
        
        // 验证交互
        _mockUserRepository.Verify(r => r.FindAll(), Times.Once);
    }
}

// 被测试的类
public class UserService
{
    private readonly IUserRepository _userRepository;
    private readonly IEmailService _emailService;
    private readonly IDateTimeProvider _dateTimeProvider;

    public UserService(IUserRepository userRepository, IEmailService emailService, IDateTimeProvider dateTimeProvider = null)
    {
        _userRepository = userRepository;
        _emailService = emailService;
        _dateTimeProvider = dateTimeProvider ?? new SystemDateTimeProvider();
    }

    public User CreateUser(User user)
    {
        if (!IsValidEmail(user.Email))
        {
            throw new InvalidEmailException("Invalid email format");
        }

        if (_userRepository.ExistsByEmail(user.Email))
        {
            throw new UserAlreadyExistsException("Email already exists");
        }

        var savedUser = _userRepository.Save(user);
        _emailService.SendWelcomeEmail(savedUser.Email);

        return savedUser;
    }

    public bool Authenticate(string email, string password)
    {
        var user = _userRepository.FindByEmail(email);
        return user != null && user.Password == password;
    }

    public User UpdateUser(int userId, User updatedUser)
    {
        var existingUser = _userRepository.FindById(userId);
        if (existingUser == null)
        {
            throw new UserNotFoundException("User not found");
        }

        existingUser.Email = updatedUser.Email;
        existingUser.Password = updatedUser.Password;

        return _userRepository.Save(existingUser);
    }

    public UserActivityReport GetUserActivityReport()
    {
        var users = _userRepository.FindAll();
        
        return new UserActivityReport
        {
            Date = _dateTimeProvider.Now.ToString("yyyy-MM-dd"),
            Users = users.Select(u => new UserSummary { Id = u.Id, Email = u.Email }).ToList()
        };
    }

    private bool IsValidEmail(string email)
    {
        return !string.IsNullOrEmpty(email) && email.Contains("@") && email.Contains(".");
    }
}

// 模拟的依赖类
public interface IUserRepository
{
    User Save(User user);
    User FindByEmail(string email);
    User FindById(int id);
    bool ExistsByEmail(string email);
    IEnumerable<User> FindAll();
}

public interface IEmailService
{
    void SendWelcomeEmail(string email);
}

public interface IDateTimeProvider
{
    DateTime Now { get; }
}

public class SystemDateTimeProvider : IDateTimeProvider
{
    public DateTime Now => DateTime.Now;
}

public class User
{
    public int Id { get; set; }
    public string Email { get; set; }
    public string Password { get; set; }
}

public class UserActivityReport
{
    public string Date { get; set; }
    public List<UserSummary> Users { get; set; }
}

public class UserSummary
{
    public int Id { get; set; }
    public string Email { get; set; }
}

// 自定义异常类
public class UserAlreadyExistsException : Exception
{
    public UserAlreadyExistsException(string message) : base(message) { }
}

public class UserNotFoundException : Exception
{
    public UserNotFoundException(string message) : base(message) { }
}

public class InvalidEmailException : Exception
{
    public InvalidEmailException(string message) : base(message) { }
}
```

## 最佳实践

### 测试设计
- 遵循AAA模式（Arrange、Act、Assert）
- 编写清晰、描述性的测试名称
- 一个测试只验证一个行为
- 保持测试简单和专注

### 模拟与依赖
- 优先使用依赖注入
- 只模拟外部依赖，不模拟被测试的类
- 验证重要的交互，而不是所有交互
- 避免过度模拟

### 测试数据管理
- 使用工厂模式创建测试数据
- 避免硬编码测试数据
- 使用Builder模式构建复杂对象
- 考虑使用测试数据库或内存数据库

### 测试组织
- 按功能或特性组织测试
- 使用嵌套测试类组织相关测试
- 保持测试文件结构清晰
- 使用共享设置和清理代码

### 测试维护
- 定期重构测试代码
- 保持测试快速执行
- 监控测试覆盖率
- 及时修复失败的测试

## 贡献指南

1. 添加新的学习资源时，请确保：
   - 内容准确且实用
   - 包含实际示例和代码
   - 注明来源和参考链接

2. 在本README.md中更新目录结构

## 注意事项

- 单元测试不能替代集成测试和端到端测试
- 过度测试可能导致维护负担
- 测试覆盖率不是质量的唯一指标
- 测试应该与实现保持适当距离
- 定期审查和重构测试代码