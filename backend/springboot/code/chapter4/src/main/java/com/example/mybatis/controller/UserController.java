package com.example.mybatis.controller;

import com.example.mybatis.entity.User;
import com.example.mybatis.service.UserService;
import com.github.pagehelper.PageInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    /**
     * 根据ID查询用户
     */
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        User user = userService.getUserById(id);
        if (user != null) {
            return ResponseEntity.ok(user);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 查询所有用户
     */
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }
    
    /**
     * 分页查询用户
     */
    @GetMapping("/page")
    public ResponseEntity<PageInfo<User>> getUsersByPage(
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize) {
        PageInfo<User> pageInfo = userService.getUsersByPage(pageNum, pageSize);
        return ResponseEntity.ok(pageInfo);
    }
    
    /**
     * 根据用户名模糊查询
     */
    @GetMapping("/search")
    public ResponseEntity<List<User>> searchUsers(@RequestParam String username) {
        List<User> users = userService.getUsersByUsername(username);
        return ResponseEntity.ok(users);
    }
    
    /**
     * 创建用户
     */
    @PostMapping
    public ResponseEntity<Integer> createUser(@RequestBody User user) {
        int result = userService.createUser(user);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 更新用户
     */
    @PutMapping("/{id}")
    public ResponseEntity<Integer> updateUser(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        int result = userService.updateUser(user);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 删除用户
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Integer> deleteUser(@PathVariable Long id) {
        int result = userService.deleteUser(id);
        return ResponseEntity.ok(result);
    }
    
    /**
     * 批量创建用户
     */
    @PostMapping("/batch")
    public ResponseEntity<Integer> batchCreateUsers(@RequestBody List<User> users) {
        int result = userService.batchCreateUsers(users);
        return ResponseEntity.ok(result);
    }
}