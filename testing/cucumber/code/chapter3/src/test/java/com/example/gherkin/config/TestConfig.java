package com.example.gherkin.config;

import com.example.gherkin.context.TestContext;
import com.example.gherkin.service.*;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;

/**
 * 测试配置类
 */
@TestConfiguration
public class TestConfig {
    
    @Bean
    @Primary
    public UserService userService() {
        return new UserService();
    }
    
    @Bean
    @Primary
    public ProductService productService() {
        return new ProductService();
    }
    
    @Bean
    @Primary
    public OrderService orderService() {
        return new OrderService();
    }
    
    @Bean
    @Primary
    public CartService cartService() {
        return new CartService();
    }
    
    @Bean
    @Primary
    public PaymentService paymentService() {
        return new PaymentService();
    }
    
    @Bean
    public TestContext testContext() {
        return new TestContext();
    }
}