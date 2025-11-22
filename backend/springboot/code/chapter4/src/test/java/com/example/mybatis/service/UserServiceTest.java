package com.example.mybatis.service;

import com.example.mybatis.MyBatisApplication;
import com.example.mybatis.entity.User;
import com.github.pagehelper.PageInfo;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(classes = MyBatisApplication.class)
@Transactional
class UserServiceTest {
    
    @Autowired
    private UserService userService;
    
    @Test
    void testGetUserById() {
        User user = userService.getUserById(1L);
        assertNotNull(user);
        assertEquals("张三", user.getUsername());
    }
    
    @Test
    void testGetAllUsers() {
        List<User> users = userService.getAllUsers();
        assertNotNull(users);
        assertTrue(users.size() > 0);
    }
    
    @Test
    void testGetUsersByPage() {
        PageInfo<User> pageInfo = userService.getUsersByPage(1, 3);
        assertNotNull(pageInfo);
        assertEquals(1, pageInfo.getPageNum());
        assertEquals(3, pageInfo.getPageSize());
        assertTrue(pageInfo.getList().size() <= 3);
    }
    
    @Test
    void testGetUsersByUsername() {
        List<User> users = userService.getUsersByUsername("张");
        assertNotNull(users);
        assertTrue(users.size() > 0);
        assertEquals("张三", users.get(0).getUsername());
    }
    
    @Test
    void testCreateUser() {
        User user = new User("测试用户", "test@example.com");
        int result = userService.createUser(user);
        assertEquals(1, result);
        assertNotNull(user.getId());
        assertTrue(user.getId() > 0);
    }
    
    @Test
    void testBatchCreateUsers() {
        User user1 = new User("批量测试1", "batch1@example.com");
        User user2 = new User("批量测试2", "batch2@example.com");
        
        int result = userService.batchCreateUsers(Arrays.asList(user1, user2));
        assertEquals(2, result);
    }
    
    @Test
    void testUpdateUser() {
        User user = userService.getUserById(1L);
        assertNotNull(user);
        
        user.setUsername("张三丰");
        int result = userService.updateUser(user);
        assertEquals(1, result);
        
        User updatedUser = userService.getUserById(1L);
        assertEquals("张三丰", updatedUser.getUsername());
    }
    
    @Test
    void testDeleteUser() {
        int result = userService.deleteUser(5L);
        assertEquals(1, result);
    }
}