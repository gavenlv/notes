package com.example.gherkin.service;

import com.example.gherkin.model.User;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * 用户服务类
 * 提供用户注册、登录、验证等功能
 */
@Service
public class UserService {
    private final Map<String, User> usersByUsername = new HashMap<>();
    private final Map<String, User> usersByEmail = new HashMap<>();
    private final Map<String, String> verificationTokens = new HashMap<>();
    
    // 密码验证正则表达式
    private static final Pattern PASSWORD_PATTERN = Pattern.compile(
        "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\\S+$).{8,}$"
    );
    
    // 邮箱验证正则表达式
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@(.+)$"
    );

    /**
     * 用户注册
     * @param username 用户名
     * @param email 邮箱
     * @param password 密码
     * @param firstName 名
     * @param lastName 姓
     * @return 注册结果
     */
    public RegistrationResult registerUser(String username, String email, String password, 
                                         String firstName, String lastName) {
        // 验证用户名是否已存在
        if (usersByUsername.containsKey(username)) {
            return RegistrationResult.failure("Username already exists");
        }
        
        // 验证邮箱是否已存在
        if (usersByEmail.containsKey(email)) {
            return RegistrationResult.failure("Email already exists");
        }
        
        // 验证邮箱格式
        if (!EMAIL_PATTERN.matcher(email).matches()) {
            return RegistrationResult.failure("Invalid email format");
        }
        
        // 验证密码强度
        if (!PASSWORD_PATTERN.matcher(password).matches()) {
            return RegistrationResult.failure("Password does not meet security requirements");
        }
        
        // 创建新用户
        User newUser = new User(username, email, password, firstName, lastName);
        
        // 生成验证令牌
        String verificationToken = UUID.randomUUID().toString();
        verificationTokens.put(verificationToken, username);
        
        // 保存用户
        usersByUsername.put(username, newUser);
        usersByEmail.put(email, newUser);
        
        return RegistrationResult.success(verificationToken);
    }

    /**
     * 用户登录验证
     * @param username 用户名
     * @param password 密码
     * @return 登录结果
     */
    public LoginResult authenticateUser(String username, String password) {
        Optional<User> userOptional = Optional.ofNullable(usersByUsername.get(username));
        
        if (userOptional.isEmpty()) {
            return LoginResult.failure("Invalid username or password");
        }
        
        User user = userOptional.get();
        
        // 检查用户是否已激活
        if (!user.isActive()) {
            return LoginResult.failure("Account is disabled");
        }
        
        // 检查用户是否已验证
        if (!user.isVerified()) {
            return LoginResult.failure("Account is not verified");
        }
        
        // 验证密码
        if (!user.getPassword().equals(password)) {
            return LoginResult.failure("Invalid username or password");
        }
        
        // 更新最后登录时间
        user.updateLastLoginTime();
        
        return LoginResult.success(user);
    }

    /**
     * 验证用户邮箱
     * @param token 验证令牌
     * @return 验证结果
     */
    public VerificationResult verifyUser(String token) {
        String username = verificationTokens.get(token);
        
        if (username == null) {
            return VerificationResult.failure("Invalid verification token");
        }
        
        User user = usersByUsername.get(username);
        if (user == null) {
            return VerificationResult.failure("User not found");
        }
        
        // 激活用户
        user.setVerified(true);
        
        // 移除验证令牌
        verificationTokens.remove(token);
        
        return VerificationResult.success();
    }

    /**
     * 获取用户信息
     * @param username 用户名
     * @return 用户信息
     */
    public Optional<User> getUserByUsername(String username) {
        return Optional.ofNullable(usersByUsername.get(username));
    }

    /**
     * 通过邮箱获取用户信息
     * @param email 邮箱
     * @return 用户信息
     */
    public Optional<User> getUserByEmail(String email) {
        return Optional.ofNullable(usersByEmail.get(email));
    }

    /**
     * 更新用户信息
     * @param user 用户信息
     * @return 更新结果
     */
    public boolean updateUser(User user) {
        if (usersByUsername.containsKey(user.getUsername())) {
            usersByUsername.put(user.getUsername(), user);
            usersByEmail.put(user.getEmail(), user);
            return true;
        }
        return false;
    }

    /**
     * 禁用用户账户
     * @param username 用户名
     * @return 操作结果
     */
    public boolean disableUser(String username) {
        User user = usersByUsername.get(username);
        if (user != null) {
            user.setActive(false);
            return true;
        }
        return false;
    }

    /**
     * 启用用户账户
     * @param username 用户名
     * @return 操作结果
     */
    public boolean enableUser(String username) {
        User user = usersByUsername.get(username);
        if (user != null) {
            user.setActive(true);
            return true;
        }
        return false;
    }

    /**
     * 重置用户密码
     * @param username 用户名
     * @param oldPassword 旧密码
     * @param newPassword 新密码
     * @return 重置结果
     */
    public PasswordResetResult resetPassword(String username, String oldPassword, String newPassword) {
        User user = usersByUsername.get(username);
        
        if (user == null) {
            return PasswordResetResult.failure("User not found");
        }
        
        // 验证旧密码
        if (!user.getPassword().equals(oldPassword)) {
            return PasswordResetResult.failure("Current password is incorrect");
        }
        
        // 验证新密码强度
        if (!PASSWORD_PATTERN.matcher(newPassword).matches()) {
            return PasswordResetResult.failure("New password does not meet security requirements");
        }
        
        // 更新密码
        user.setPassword(newPassword);
        
        return PasswordResetResult.success();
    }

    // 内部结果类

    public static class RegistrationResult {
        private final boolean success;
        private final String message;
        private final String verificationToken;

        private RegistrationResult(boolean success, String message, String verificationToken) {
            this.success = success;
            this.message = message;
            this.verificationToken = verificationToken;
        }

        public static RegistrationResult success(String verificationToken) {
            return new RegistrationResult(true, "Registration successful", verificationToken);
        }

        public static RegistrationResult failure(String message) {
            return new RegistrationResult(false, message, null);
        }

        public boolean isSuccess() {
            return success;
        }

        public String getMessage() {
            return message;
        }

        public String getVerificationToken() {
            return verificationToken;
        }
    }

    public static class LoginResult {
        private final boolean success;
        private final String message;
        private final User user;

        private LoginResult(boolean success, String message, User user) {
            this.success = success;
            this.message = message;
            this.user = user;
        }

        public static LoginResult success(User user) {
            return new LoginResult(true, "Login successful", user);
        }

        public static LoginResult failure(String message) {
            return new LoginResult(false, message, null);
        }

        public boolean isSuccess() {
            return success;
        }

        public String getMessage() {
            return message;
        }

        public User getUser() {
            return user;
        }
    }

    public static class VerificationResult {
        private final boolean success;
        private final String message;

        private VerificationResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }

        public static VerificationResult success() {
            return new VerificationResult(true, "Account verified successfully");
        }

        public static VerificationResult failure(String message) {
            return new VerificationResult(false, message);
        }

        public boolean isSuccess() {
            return success;
        }

        public String getMessage() {
            return message;
        }
    }

    public static class PasswordResetResult {
        private final boolean success;
        private final String message;

        private PasswordResetResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }

        public static PasswordResetResult success() {
            return new PasswordResetResult(true, "Password reset successful");
        }

        public static PasswordResetResult failure(String message) {
            return new PasswordResetResult(false, message);
        }

        public boolean isSuccess() {
            return success;
        }

        public String getMessage() {
            return message;
        }
    }
}