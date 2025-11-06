package com.example.gherkin.service;

import com.example.gherkin.model.User;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * 用户服务类
 */
@Service
public class UserService {
    
    // 使用内存存储用户数据，实际项目中应该使用数据库
    private final Map<Long, User> userStore = new ConcurrentHashMap<>();
    private final Map<String, User> usernameIndex = new ConcurrentHashMap<>();
    private final Map<String, User> emailIndex = new ConcurrentHashMap<>();
    private long nextId = 1L;
    
    /**
     * 创建新用户
     */
    public User createUser(String username, String email, String password) {
        // 验证用户名是否已存在
        if (usernameIndex.containsKey(username)) {
            throw new IllegalArgumentException("用户名已存在: " + username);
        }
        
        // 验证邮箱是否已存在
        if (emailIndex.containsKey(email)) {
            throw new IllegalArgumentException("邮箱已存在: " + email);
        }
        
        // 验证邮箱格式
        if (!isValidEmail(email)) {
            throw new IllegalArgumentException("邮箱格式无效: " + email);
        }
        
        // 验证密码强度
        if (!isStrongPassword(password)) {
            throw new IllegalArgumentException("密码强度不足");
        }
        
        // 创建新用户
        User user = new User(username, email, password);
        user.setId(nextId++);
        
        // 存储用户
        userStore.put(user.getId(), user);
        usernameIndex.put(user.getUsername(), user);
        emailIndex.put(user.getEmail(), user);
        
        return user;
    }
    
    /**
     * 根据ID获取用户
     */
    public Optional<User> getUserById(Long id) {
        return Optional.ofNullable(userStore.get(id));
    }
    
    /**
     * 根据用户名获取用户
     */
    public Optional<User> getUserByUsername(String username) {
        return Optional.ofNullable(usernameIndex.get(username));
    }
    
    /**
     * 根据邮箱获取用户
     */
    public Optional<User> getUserByEmail(String email) {
        return Optional.ofNullable(emailIndex.get(email));
    }
    
    /**
     * 更新用户信息
     */
    public User updateUser(Long id, String firstName, String lastName, String phone) {
        User user = userStore.get(id);
        if (user == null) {
            throw new IllegalArgumentException("用户不存在: " + id);
        }
        
        user.setFirstName(firstName);
        user.setLastName(lastName);
        user.setPhone(phone);
        user.updateTimestamp();
        
        return user;
    }
    
    /**
     * 更新用户密码
     */
    public void updatePassword(Long id, String oldPassword, String newPassword) {
        User user = userStore.get(id);
        if (user == null) {
            throw new IllegalArgumentException("用户不存在: " + id);
        }
        
        // 验证旧密码
        if (!user.verifyPassword(oldPassword)) {
            throw new IllegalArgumentException("旧密码不正确");
        }
        
        // 验证新密码强度
        if (!isStrongPassword(newPassword)) {
            throw new IllegalArgumentException("新密码强度不足");
        }
        
        user.setPassword(newPassword);
        user.updateTimestamp();
    }
    
    /**
     * 验证用户登录
     */
    public User authenticate(String username, String password) {
        User user = usernameIndex.get(username);
        if (user == null) {
            throw new IllegalArgumentException("用户名或密码错误");
        }
        
        if (!user.verifyPassword(password)) {
            throw new IllegalArgumentException("用户名或密码错误");
        }
        
        if (!user.isEnabled()) {
            throw new IllegalArgumentException("账户已被禁用");
        }
        
        return user;
    }
    
    /**
     * 验证用户邮箱
     */
    public void verifyEmail(Long id) {
        User user = userStore.get(id);
        if (user == null) {
            throw new IllegalArgumentException("用户不存在: " + id);
        }
        
        user.setEmailVerified(true);
        user.updateTimestamp();
    }
    
    /**
     * 启用/禁用用户
     */
    public void enableUser(Long id, boolean enabled) {
        User user = userStore.get(id);
        if (user == null) {
            throw new IllegalArgumentException("用户不存在: " + id);
        }
        
        user.setEnabled(enabled);
        user.updateTimestamp();
    }
    
    /**
     * 删除用户
     */
    public void deleteUser(Long id) {
        User user = userStore.remove(id);
        if (user != null) {
            usernameIndex.remove(user.getUsername());
            emailIndex.remove(user.getEmail());
        }
    }
    
    /**
     * 检查用户名是否存在
     */
    public boolean existsByUsername(String username) {
        return usernameIndex.containsKey(username);
    }
    
    /**
     * 检查邮箱是否存在
     */
    public boolean existsByEmail(String email) {
        return emailIndex.containsKey(email);
    }
    
    /**
     * 获取所有用户
     */
    public List<User> getAllUsers() {
        return new ArrayList<>(userStore.values());
    }
    
    /**
     * 搜索用户
     */
    public List<User> searchUsers(String keyword) {
        String lowerKeyword = keyword.toLowerCase();
        
        return userStore.values().stream()
                .filter(user -> 
                    user.getUsername().toLowerCase().contains(lowerKeyword) ||
                    user.getEmail().toLowerCase().contains(lowerKeyword) ||
                    (user.getFirstName() != null && user.getFirstName().toLowerCase().contains(lowerKeyword)) ||
                    (user.getLastName() != null && user.getLastName().toLowerCase().contains(lowerKeyword))
                )
                .collect(Collectors.toList());
    }
    
    /**
     * 批量创建用户
     */
    public List<User> createUsers(List<Map<String, String>> userDataList) {
        List<User> createdUsers = new ArrayList<>();
        
        for (Map<String, String> userData : userDataList) {
            String username = userData.get("username");
            String email = userData.get("email");
            String password = userData.get("password");
            String firstName = userData.get("firstName");
            String lastName = userData.get("lastName");
            
            User user = createUser(username, email, password);
            
            if (firstName != null) {
                user.setFirstName(firstName);
            }
            if (lastName != null) {
                user.setLastName(lastName);
            }
            
            createdUsers.add(user);
        }
        
        return createdUsers;
    }
    
    /**
     * 验证邮箱格式
     */
    private boolean isValidEmail(String email) {
        if (email == null || email.isEmpty()) {
            return false;
        }
        
        // 简单的邮箱格式验证
        return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");
    }
    
    /**
     * 验证密码强度
     */
    private boolean isStrongPassword(String password) {
        if (password == null || password.length() < 8) {
            return false;
        }
        
        boolean hasUpper = false;
        boolean hasLower = false;
        boolean hasDigit = false;
        
        for (char c : password.toCharArray()) {
            if (Character.isUpperCase(c)) {
                hasUpper = true;
            } else if (Character.isLowerCase(c)) {
                hasLower = true;
            } else if (Character.isDigit(c)) {
                hasDigit = true;
            }
        }
        
        return hasUpper && hasLower && hasDigit;
    }
    
    /**
     * 清空所有用户数据（仅用于测试）
     */
    public void clearAllUsers() {
        userStore.clear();
        usernameIndex.clear();
        emailIndex.clear();
        nextId = 1L;
    }
}