package com.example.gherkin;

import com.example.gherkin.config.TestConfig;
import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

/**
 * Cucumber与Spring Boot集成的测试基类
 * 提供测试环境配置
 */
@CucumberContextConfiguration
@SpringBootTest(classes = CucumberSpringIntegrationTest.class)
@Import(TestConfig.class)
@ActiveProfiles("test")
public class CucumberSpringIntegrationTest {
    // 测试基类，不需要实现任何方法
}