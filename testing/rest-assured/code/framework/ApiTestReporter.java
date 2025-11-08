package com.example.restassured.framework;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.ExtentTest;
import com.aventstack.extentreports.Status;
import com.aventstack.extentreports.reporter.ExtentHtmlReporter;
import com.aventstack.extentreports.reporter.configuration.Theme;
import io.restassured.response.Response;
import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.extension.*;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * API测试报告生成器
 * 提供详细的测试报告，包括请求、响应、断言结果等
 */
public class ApiTestReporter implements BeforeAllCallback, AfterAllCallback, 
                                       BeforeEachCallback, AfterEachCallback {
    
    private static ExtentReports extent;
    private static ExtentTest test;
    private static final Map<String, ExtentTest> classTestMap = new ConcurrentHashMap<>();
    private static final Map<String, Object> testData = new ConcurrentHashMap<>();
    private static final String REPORT_PATH = "test-reports/api-test-report.html";
    private static final String SCREENSHOT_PATH = "test-reports/screenshots";
    private static final String JSON_RESPONSE_PATH = "test-reports/responses";
    
    @Override
    public void beforeAll(ExtensionContext context) throws Exception {
        // 初始化ExtentReports
        if (extent == null) {
            ExtentHtmlReporter htmlReporter = new ExtentHtmlReporter(REPORT_PATH);
            htmlReporter.config().setDocumentTitle("REST Assured API Test Report");
            htmlReporter.config().setReportName("API Testing Report");
            htmlReporter.config().setTheme(Theme.DARK);
            htmlReporter.config().setEncoding("UTF-8");
            
            extent = new ExtentReports();
            extent.attachReporter(htmlReporter);
            
            // 添加系统信息
            extent.setSystemInfo("OS", System.getProperty("os.name"));
            extent.setSystemInfo("Java Version", System.getProperty("java.version"));
            extent.setSystemInfo("User", System.getProperty("user.name"));
            extent.setSystemInfo("Test Environment", System.getProperty("test.environment", "dev"));
        }
        
        // 创建类级别的测试节点
        String className = context.getTestClass().get().getSimpleName();
        ExtentTest classTest = extent.createTest(className);
        classTestMap.put(className, classTest);
    }
    
    @Override
    public void beforeEach(ExtensionContext context) throws Exception {
        // 创建方法级别的测试节点
        String className = context.getTestClass().get().getSimpleName();
        String methodName = context.getTestMethod().get().getName();
        
        ExtentTest classTest = classTestMap.get(className);
        test = classTest.createNode(methodName);
        
        // 记录测试开始时间
        testData.put("startTime", System.currentTimeMillis());
    }
    
    @Override
    public void afterEach(ExtensionContext context) throws Exception {
        long endTime = System.currentTimeMillis();
        long startTime = (long) testData.get("startTime");
        long duration = endTime - startTime;
        
        // 获取测试结果
        boolean testPassed = context.getExecutionException().isPresent() == false;
        
        if (testPassed) {
            test.log(Status.PASS, "Test passed successfully");
        } else {
            test.log(Status.FAIL, "Test failed: " + context.getExecutionException().get().getMessage());
        }
        
        // 记录测试持续时间
        test.log(Status.INFO, "Execution time: " + duration + " ms");
        
        // 清除测试数据
        testData.clear();
    }
    
    @Override
    public void afterAll(ExtensionContext context) throws Exception {
        // 写入报告
        extent.flush();
    }
    
    /**
     * 记录API请求
     */
    public static void logRequest(String method, String url, Map<String, String> headers, Object body) {
        if (test == null) return;
        
        test.log(Status.INFO, "<b>Request Details:</b>");
        test.log(Status.INFO, "Method: " + method);
        test.log(Status.INFO, "URL: " + url);
        
        if (headers != null && !headers.isEmpty()) {
            test.log(Status.INFO, "<b>Headers:</b>");
            headers.forEach((k, v) -> test.log(Status.INFO, k + ": " + v));
        }
        
        if (body != null) {
            test.log(Status.INFO, "<b>Request Body:</b>");
            test.log(Status.INFO, "<pre>" + formatJson(body) + "</pre>");
        }
    }
    
    /**
     * 记录API响应
     */
    public static void logResponse(Response response) {
        if (test == null) return;
        
        test.log(Status.INFO, "<b>Response Details:</b>");
        test.log(Status.INFO, "Status Code: " + response.getStatusCode());
        test.log(Status.INFO, "Status Line: " + response.getStatusLine());
        test.log(Status.INFO, "Response Time: " + response.getTime() + " ms");
        
        // 记录响应头
        test.log(Status.INFO, "<b>Response Headers:</b>");
        response.getHeaders().forEach(header -> 
            test.log(Status.INFO, header.getName() + ": " + header.getValue()));
        
        // 记录响应体
        String responseBody = response.getBody().asString();
        if (responseBody != null && !responseBody.isEmpty()) {
            test.log(Status.INFO, "<b>Response Body:</b>");
            
            // 如果是JSON，格式化显示
            if (response.getContentType() != null && 
                response.getContentType().contains("application/json")) {
                test.log(Status.INFO, "<pre>" + formatJson(responseBody) + "</pre>");
            } else {
                test.log(Status.INFO, "<pre>" + responseBody + "</pre>");
            }
            
            // 保存响应体到文件
            saveResponseToFile(responseBody);
        }
    }
    
    /**
     * 记录断言结果
     */
    public static void logAssertion(String description, boolean result, Object expected, Object actual) {
        if (test == null) return;
        
        if (result) {
            test.log(Status.PASS, "Assertion PASSED: " + description);
        } else {
            test.log(Status.FAIL, "Assertion FAILED: " + description);
            test.log(Status.FAIL, "Expected: " + expected);
            test.log(Status.FAIL, "Actual: " + actual);
        }
        
        test.log(Status.INFO, "Expected: " + expected + ", Actual: " + actual);
    }
    
    /**
     * 记录测试步骤
     */
    public static void logStep(String step) {
        if (test == null) return;
        
        test.log(Status.INFO, "<b>Step:</b> " + step);
    }
    
    /**
     * 记录测试信息
     */
    public static void logInfo(String info) {
        if (test == null) return;
        
        test.log(Status.INFO, info);
    }
    
    /**
     * 记录警告
     */
    public static void logWarning(String warning) {
        if (test == null) return;
        
        test.log(Status.WARNING, warning);
    }
    
    /**
     * 记录错误
     */
    public static void logError(String error) {
        if (test == null) return;
        
        test.log(Status.ERROR, error);
    }
    
    /**
     * 记录异常
     */
    public static void logException(Throwable throwable) {
        if (test == null) return;
        
        test.log(Status.ERROR, "Exception occurred: " + throwable.getMessage());
        test.log(Status.ERROR, "<pre>" + getStackTrace(throwable) + "</pre>");
    }
    
    /**
     * 添加测试截图（对于Web UI测试）
     */
    public static void addScreenshot(String screenshotName) {
        if (test == null) return;
        
        try {
            // 创建截图目录
            Path screenshotDir = Paths.get(SCREENSHOT_PATH);
            if (!Files.exists(screenshotDir)) {
                Files.createDirectories(screenshotDir);
            }
            
            // 生成截图文件名
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            String screenshotFile = screenshotName + "_" + timestamp + ".png";
            Path filePath = Paths.get(SCREENSHOT_PATH, screenshotFile);
            
            // 在实际应用中，这里应该保存实际的截图
            // 这里只是创建一个空文件作为示例
            Files.createFile(filePath);
            
            // 添加到报告
            test.addScreenCaptureFromPath(filePath.toString());
        } catch (IOException e) {
            test.log(Status.ERROR, "Failed to save screenshot: " + e.getMessage());
        }
    }
    
    /**
     * 保存响应到文件
     */
    private static void saveResponseToFile(String responseBody) {
        try {
            // 创建响应目录
            Path responseDir = Paths.get(JSON_RESPONSE_PATH);
            if (!Files.exists(responseDir)) {
                Files.createDirectories(responseDir);
            }
            
            // 生成响应文件名
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmssSSS"));
            String responseFile = "response_" + timestamp + ".json";
            Path filePath = Paths.get(JSON_RESPONSE_PATH, responseFile);
            
            // 保存响应
            FileUtils.writeStringToFile(filePath.toFile(), responseBody, "UTF-8");
        } catch (IOException e) {
            test.log(Status.ERROR, "Failed to save response to file: " + e.getMessage());
        }
    }
    
    /**
     * 格式化JSON字符串
     */
    private static String formatJson(Object json) {
        try {
            if (json instanceof String) {
                return com.fasterxml.jackson.databind.ObjectMapper().writerWithDefaultPrettyPrinter()
                    .writeValueAsString(com.fasterxml.jackson.databind.ObjectMapper().readTree((String) json));
            } else {
                return com.fasterxml.jackson.databind.ObjectMapper().writerWithDefaultPrettyPrinter()
                    .writeValueAsString(json);
            }
        } catch (Exception e) {
            return json.toString();
        }
    }
    
    /**
     * 获取异常堆栈跟踪
     */
    private static String getStackTrace(Throwable throwable) {
        StringBuilder sb = new StringBuilder();
        sb.append(throwable.toString()).append("\n");
        
        for (StackTraceElement element : throwable.getStackTrace()) {
            sb.append("\tat ").append(element.toString()).append("\n");
        }
        
        return sb.toString();
    }
    
    /**
     * 创建自定义测试标签
     */
    public static void assignCategory(String... categories) {
        if (test != null) {
            test.assignCategory(categories);
        }
    }
    
    /**
     * 添加测试作者信息
     */
    public static void assignAuthor(String... authors) {
        if (test != null) {
            test.assignAuthor(authors);
        }
    }
    
    /**
     * 添加测试设备信息
     */
    public static void assignDevice(String... devices) {
        if (test != null) {
            test.assignDevice(devices);
        }
    }
}