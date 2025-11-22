package com.example.mybatis.mapper;

import com.example.mybatis.MyBatisApplication;
import com.example.mybatis.entity.User;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(classes = MyBatisApplication.class)
@Transactional
class UserMapperTest {
    
    @Autowired
    private UserMapper userMapper;
    
    @Test
    void testSelectUserById() {
        User user = userMapper.selectUserById(1L);
        assertNotNull(user);
        assertEquals("张三", user.getUsername());
        assertEquals("zhangsan@example.com", user.getEmail());
    }
    
    @Test
    void testSelectAllUsers() {
        List<User> users = userMapper.selectAllUsers();
        assertNotNull(users);
        assertTrue(users.size() > 0);
    }
    
    @Test
    void testSelectUsersByUsername() {
        List<User> users = userMapper.selectUsersByUsername("张");
        assertNotNull(users);
        assertTrue(users.size() > 0);
        assertEquals("张三", users.get(0).getUsername());
    }
    
    @Test
    void testInsertUser() {
        User user = new User("测试用户", "test@example.com");
        int result = userMapper.insertUser(user);
        assertEquals(1, result);
        assertNotNull(user.getId());
        assertTrue(user.getId() > 0);
    }
    
    @Test
    void testUpdateUser() {
        User user = userMapper.selectUserById(1L);
        assertNotNull(user);
        
        user.setUsername("张三丰");
        int result = userMapper.updateUser(user);
        assertEquals(1, result);
        
        User updatedUser = userMapper.selectUserById(1L);
        assertEquals("张三丰", updatedUser.getUsername());
    }
    
    @Test
    void testDeleteUser() {
        int result = userMapper.deleteUser(5L);
        assertEquals(1, result);
        
        User user = userMapper.selectUserById(5L);
        assertNull(user);
    }
}