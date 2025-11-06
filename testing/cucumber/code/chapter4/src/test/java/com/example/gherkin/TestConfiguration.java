package com.example.gherkin;

import com.example.gherkin.service.BankAccountService;
import com.example.gherkin.service.ProductService;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;

/**
 * 测试配置类
 * 为测试环境提供必要的Bean配置
 */
@TestConfiguration
public class TestConfiguration {

    @Bean
    public ProductService productService() {
        return new ProductService();
    }

    @Bean
    public BankAccountService bankAccountService() {
        return new BankAccountService();
    }
}