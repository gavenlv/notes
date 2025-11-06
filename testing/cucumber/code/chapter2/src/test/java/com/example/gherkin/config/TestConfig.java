package com.example.gherkin.config;

import com.example.gherkin.service.UserService;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;

/**
 * 测试配置类
 * 提供测试环境所需的Bean配置
 */
@TestConfiguration
public class TestConfig {

    /**
     * 创建用户服务测试Bean
     * @return 用户服务实例
     */
    @Bean
    public UserService userService() {
        return new UserService();
    }
}