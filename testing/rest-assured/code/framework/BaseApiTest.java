package com.example.restassured.framework;

import io.restassured.RestAssured;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.builder.ResponseSpecBuilder;
import io.restassured.filter.log.LogDetail;
import io.restassured.filter.log.RequestLoggingFilter;
import io.restassured.filter.log.ResponseLoggingFilter;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import io.restassured.specification.ResponseSpecification;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

/**
 * API测试基类，提供通用的测试配置和功能
 * 包含请求/响应规范、日志记录、环境配置等
 */
public abstract class BaseApiTest {
    
    protected static ByteArrayOutputStream logCapture;
    protected static PrintStream originalOut;
    
    // 默认环境配置
    protected static String BASE_URL = "https://jsonplaceholder.typicode.com";
    protected static String API_VERSION = "/v1";
    
    // 通用请求规范
    protected static RequestSpecification requestSpec;
    protected static ResponseSpecification responseSpec;
    
    @BeforeAll
    public static void setUpClass() {
        // 设置基础URI
        RestAssured.baseURI = BASE_URL;
        
        // 创建请求规范构建器
        RequestSpecBuilder requestSpecBuilder = new RequestSpecBuilder()
            .setBaseUri(BASE_URL + API_VERSION)
            .setContentType(ContentType.JSON)
            .setAccept(ContentType.JSON)
            .addHeader("User-Agent", "REST-Assured-Testing-Framework/1.0")
            .addHeader("X-Client-Version", "1.0.0");
        
        // 添加通用请求头
        requestSpecBuilder.addHeader("X-Test-Environment", getTestEnvironment());
        
        // 添加全局日志过滤器
        if (shouldLogRequests()) {
            requestSpecBuilder.addFilter(new RequestLoggingFilter(LogDetail.ALL));
        }
        if (shouldLogResponses()) {
            requestSpecBuilder.addFilter(new ResponseLoggingFilter(LogDetail.ALL));
        }
        
        requestSpec = requestSpecBuilder.build();
        
        // 创建响应规范构建器
        ResponseSpecBuilder responseSpecBuilder = new ResponseSpecBuilder()
            .expectContentType(ContentType.JSON)
            .expectResponseTime(maxAllowedResponseTime());
        
        responseSpec = responseSpecBuilder.build();
        
        // 初始化日志捕获（可选）
        if (shouldCaptureLogs()) {
            setupLogCapture();
        }
        
        // 执行环境特定的初始化
        initializeTestEnvironment();
    }
    
    @BeforeEach
    public void setUp() {
        // 每个测试方法执行前的设置
        RestAssured.requestSpecification = requestSpec;
        RestAssured.responseSpecification = responseSpec;
        
        // 清除之前的日志捕获（如果启用）
        if (shouldCaptureLogs()) {
            logCapture.reset();
        }
        
        // 每个测试前的自定义设置
        beforeTestSetup();
    }
    
    @AfterEach
    public void tearDown() {
        // 每个测试方法执行后的清理
        afterTestCleanup();
    }
    
    @AfterAll
    public static void tearDownClass() {
        // 测试类执行后的清理
        cleanupTestEnvironment();
        
        // 恢复日志输出（如果启用了日志捕获）
        if (shouldCaptureLogs()) {
            System.setOut(originalOut);
        }
    }
    
    /**
     * 获取测试环境标识
     */
    protected static String getTestEnvironment() {
        String env = System.getProperty("test.environment", "dev");
        return env;
    }
    
    /**
     * 是否应该记录请求日志
     */
    protected static boolean shouldLogRequests() {
        return Boolean.parseBoolean(System.getProperty("test.log.requests", "true"));
    }
    
    /**
     * 是否应该记录响应日志
     */
    protected static boolean shouldLogResponses() {
        return Boolean.parseBoolean(System.getProperty("test.log.responses", "true"));
    }
    
    /**
     * 是否应该捕获日志用于验证
     */
    protected static boolean shouldCaptureLogs() {
        return Boolean.parseBoolean(System.getProperty("test.capture.logs", "false"));
    }
    
    /**
     * 最大允许响应时间（毫秒）
     */
    protected static long maxAllowedResponseTime() {
        return 5000L;
    }
    
    /**
     * 设置日志捕获
     */
    private static void setupLogCapture() {
        logCapture = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream(logCapture);
        originalOut = System.out;
        System.setOut(ps);
    }
    
    /**
     * 获取捕获的日志内容
     */
    protected static String getCapturedLogs() {
        return logCapture != null ? logCapture.toString() : "";
    }
    
    /**
     * 环境特定的初始化
     * 子类可以重写此方法以提供特定环境的初始化逻辑
     */
    protected static void initializeTestEnvironment() {
        // 默认实现：根据环境变量设置不同的基础URI
        String env = getTestEnvironment();
        switch (env.toLowerCase()) {
            case "dev":
                BASE_URL = "https://jsonplaceholder.typicode.com";
                break;
            case "staging":
                BASE_URL = "https://staging-api.example.com";
                break;
            case "prod":
                BASE_URL = "https://api.example.com";
                break;
            case "local":
                BASE_URL = "http://localhost:8080";
                break;
            default:
                BASE_URL = "https://jsonplaceholder.typicode.com";
                break;
        }
        
        // 重新设置基础URI
        RestAssured.baseURI = BASE_URL;
        
        // 重建请求规范
        RequestSpecBuilder requestSpecBuilder = new RequestSpecBuilder()
            .setBaseUri(BASE_URL + API_VERSION)
            .setContentType(ContentType.JSON)
            .setAccept(ContentType.JSON)
            .addHeader("User-Agent", "REST-Assured-Testing-Framework/1.0")
            .addHeader("X-Client-Version", "1.0.0")
            .addHeader("X-Test-Environment", env);
        
        if (shouldLogRequests()) {
            requestSpecBuilder.addFilter(new RequestLoggingFilter(LogDetail.ALL));
        }
        if (shouldLogResponses()) {
            requestSpecBuilder.addFilter(new ResponseLoggingFilter(LogDetail.ALL));
        }
        
        requestSpec = requestSpecBuilder.build();
    }
    
    /**
     * 测试前的自定义设置
     * 子类可以重写此方法以提供特定的测试前逻辑
     */
    protected void beforeTestSetup() {
        // 默认实现：无操作
    }
    
    /**
     * 测试后的自定义清理
     * 子类可以重写此方法以提供特定的测试后逻辑
     */
    protected void afterTestCleanup() {
        // 默认实现：无操作
    }
    
    /**
     * 环境特定的清理
     * 子类可以重写此方法以提供特定环境的清理逻辑
     */
    protected static void cleanupTestEnvironment() {
        // 默认实现：重置RestAssured配置
        RestAssured.reset();
    }
    
    /**
     * 获取认证令牌（如果需要）
     * 子类可以重写此方法以提供认证逻辑
     */
    protected String getAuthToken() {
        // 默认实现：返回空字符串
        return "";
    }
    
    /**
     * 创建带有认证的请求规范
     */
    protected RequestSpecification authenticatedRequest() {
        String token = getAuthToken();
        if (!token.isEmpty()) {
            return requestSpec.auth().oauth2(token);
        }
        return requestSpec;
    }
    
    /**
     * 等待指定时间（毫秒）
     * 用于需要延迟的测试场景
     */
    protected void waitFor(long milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    /**
     * 随机延迟（1-3秒）
     * 用于模拟用户行为
     */
    protected void randomDelay() {
        long delay = 1000 + (long)(Math.random() * 2000);
        waitFor(delay);
    }
}