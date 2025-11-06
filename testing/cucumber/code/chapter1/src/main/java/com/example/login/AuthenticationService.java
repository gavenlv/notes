package com.example.login;

import java.util.HashMap;
import java.util.Map;

public class AuthenticationService {
    private Map<String, User> users;
    
    public AuthenticationService() {
        users = new HashMap<>();
        // 添加一些测试用户
        users.put("admin", new User("admin", "admin123"));
        users.put("user", new User("user", "user123"));
        users.put("test", new User("test", "test123"));
    }
    
    public LoginResult login(String username, String password) {
        User user = users.get(username);
        
        if (user == null) {
            return LoginResult.failure("用户不存在");
        }
        
        if (!user.isActive()) {
            return LoginResult.failure("账户已被禁用");
        }
        
        if (!user.getPassword().equals(password)) {
            return LoginResult.failure("密码错误");
        }
        
        return LoginResult.success("登录成功");
    }
    
    public void addUser(String username, String password) {
        users.put(username, new User(username, password));
    }
    
    public void deactivateUser(String username) {
        User user = users.get(username);
        if (user != null) {
            user.setActive(false);
        }
    }
    
    public static class LoginResult {
        private boolean success;
        private String message;
        
        private LoginResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }
        
        public static LoginResult success(String message) {
            return new LoginResult(true, message);
        }
        
        public static LoginResult failure(String message) {
            return new LoginResult(false, message);
        }
        
        public boolean isSuccess() {
            return success;
        }
        
        public String getMessage() {
            return message;
        }
    }
}