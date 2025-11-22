package com.example.demo;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
public class UserRepositoryTest {
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    public void testSaveAndFindUser() {
        // 创建用户
        User user = new User("测试用户", "test@example.com");
        User savedUser = userRepository.save(user);
        
        // 验证保存成功
        assertThat(savedUser.getId()).isNotNull();
        
        // 查询用户
        List<User> users = userRepository.findByName("测试用户");
        assertThat(users).hasSize(1);
        assertThat(users.get(0).getEmail()).isEqualTo("test@example.com");
    }
}