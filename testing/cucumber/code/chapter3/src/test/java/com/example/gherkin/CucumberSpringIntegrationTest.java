package com.example.gherkin;

import com.example.gherkin.config.TestConfig;
import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

/**
 * Cucumber与Spring Boot集成测试基类
 */
@CucumberContextConfiguration
@SpringBootTest
@Import(TestConfig.class)
@ActiveProfiles("test")
public class CucumberSpringIntegrationTest {
}