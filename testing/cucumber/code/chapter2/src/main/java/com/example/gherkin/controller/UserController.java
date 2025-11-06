package com.example.gherkin.controller;

import com.example.gherkin.model.User;
import com.example.gherkin.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

/**
 * 用户控制器类
 * 提供用户相关的RESTful API接口
 */
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }

    /**
     * 用户注册
     * @param registrationData 注册数据
     * @return 注册结果
     */
    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody Map<String, String> registrationData) {
        String username = registrationData.get("username");
        String email = registrationData.get("email");
        String password = registrationData.get("password");
        String firstName = registrationData.get("firstName");
        String lastName = registrationData.get("lastName");

        UserService.RegistrationResult result = userService.registerUser(username, email, password, firstName, lastName);

        if (result.isSuccess()) {
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "success", true,
                "message", result.getMessage(),
                "verificationToken", result.getVerificationToken()
            ));
        } else {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", result.getMessage()
            ));
        }
    }

    /**
     * 用户登录
     * @param loginData 登录数据
     * @return 登录结果
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> loginData) {
        String username = loginData.get("username");
        String password = loginData.get("password");

        UserService.LoginResult result = userService.authenticateUser(username, password);

        if (result.isSuccess()) {
            User user = result.getUser();
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", result.getMessage(),
                "user", Map.of(
                    "id", user.getId(),
                    "username", user.getUsername(),
                    "email", user.getEmail(),
                    "fullName", user.getFullName(),
                    "lastLoginTime", user.getLastLoginTime()
                )
            ));
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                "success", false,
                "message", result.getMessage()
            ));
        }
    }

    /**
     * 验证用户邮箱
     * @param verificationData 验证数据
     * @return 验证结果
     */
    @PostMapping("/verify")
    public ResponseEntity<Map<String, Object>> verify(@RequestBody Map<String, String> verificationData) {
        String token = verificationData.get("token");

        UserService.VerificationResult result = userService.verifyUser(token);

        if (result.isSuccess()) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", result.getMessage()
            ));
        } else {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", result.getMessage()
            ));
        }
    }

    /**
     * 获取用户信息
     * @param username 用户名
     * @return 用户信息
     */
    @GetMapping("/{username}")
    public ResponseEntity<Map<String, Object>> getUser(@PathVariable String username) {
        Optional<User> userOptional = userService.getUserByUsername(username);

        if (userOptional.isPresent()) {
            User user = userOptional.get();
            return ResponseEntity.ok(Map.of(
                "success", true,
                "user", Map.of(
                    "id", user.getId(),
                    "username", user.getUsername(),
                    "email", user.getEmail(),
                    "firstName", user.getFirstName(),
                    "lastName", user.getLastName(),
                    "fullName", user.getFullName(),
                    "active", user.isActive(),
                    "verified", user.isVerified(),
                    "lastLoginTime", user.getLastLoginTime()
                )
            ));
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * 更新用户信息
     * @param username 用户名
     * @param updateData 更新数据
     * @return 更新结果
     */
    @PutMapping("/{username}")
    public ResponseEntity<Map<String, Object>> updateUser(
            @PathVariable String username,
            @RequestBody Map<String, String> updateData) {
        
        Optional<User> userOptional = userService.getUserByUsername(username);
        
        if (userOptional.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        
        User user = userOptional.get();
        
        // 更新用户信息
        if (updateData.containsKey("firstName")) {
            user.setFirstName(updateData.get("firstName"));
        }
        
        if (updateData.containsKey("lastName")) {
            user.setLastName(updateData.get("lastName"));
        }
        
        if (updateData.containsKey("email")) {
            user.setEmail(updateData.get("email"));
        }
        
        boolean updated = userService.updateUser(user);
        
        if (updated) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "User updated successfully"
            ));
        } else {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", "Failed to update user"
            ));
        }
    }

    /**
     * 禁用用户账户
     * @param username 用户名
     * @return 操作结果
     */
    @PostMapping("/{username}/disable")
    public ResponseEntity<Map<String, Object>> disableUser(@PathVariable String username) {
        boolean disabled = userService.disableUser(username);
        
        if (disabled) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "User disabled successfully"
            ));
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * 启用用户账户
     * @param username 用户名
     * @return 操作结果
     */
    @PostMapping("/{username}/enable")
    public ResponseEntity<Map<String, Object>> enableUser(@PathVariable String username) {
        boolean enabled = userService.enableUser(username);
        
        if (enabled) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "User enabled successfully"
            ));
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * 重置用户密码
     * @param username 用户名
     * @param passwordData 密码数据
     * @return 重置结果
     */
    @PostMapping("/{username}/reset-password")
    public ResponseEntity<Map<String, Object>> resetPassword(
            @PathVariable String username,
            @RequestBody Map<String, String> passwordData) {
        
        String oldPassword = passwordData.get("oldPassword");
        String newPassword = passwordData.get("newPassword");
        
        UserService.PasswordResetResult result = userService.resetPassword(username, oldPassword, newPassword);
        
        if (result.isSuccess()) {
            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", result.getMessage()
            ));
        } else {
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", result.getMessage()
            ));
        }
    }
}