package com.example.gherkin;

import com.example.gherkin.service.BankAccountService;
import com.example.gherkin.service.ProductService;
import io.cucumber.java.Before;
import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ContextConfiguration;

/**
 * Cucumber Spring集成测试基类
 * 提供Spring Boot测试环境和共享服务实例
 */
@SpringBootTest
@ContextConfiguration(classes = TestConfiguration.class)
@CucumberContextConfiguration
public class CucumberSpringIntegrationTest {

    @Autowired
    protected ProductService productService;

    @Autowired
    protected BankAccountService bankAccountService;

    @Before
    public void setUp() {
        // 在每个场景执行前重置服务状态
        productService.resetProducts();
        bankAccountService.resetAccounts();
    }
}