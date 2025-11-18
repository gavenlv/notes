package com.example.selenium.base;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Optional;
import org.testng.annotations.Parameters;

import java.time.Duration;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * 基础测试类
 * 封装通用的WebDriver初始化和清理逻辑
 */
public class BaseTest {
    
    protected WebDriver driver;
    protected Properties config;
    
    /**
     * 测试前置操作 - 初始化WebDriver
     */
    @BeforeMethod
    @Parameters("browser")
    public void setUp(@Optional("chrome") String browser) {
        // 加载配置文件
        loadConfig();
        
        // 根据参数选择浏览器
        switch (browser.toLowerCase()) {
            case "chrome":
                setupChromeDriver();
                break;
            case "firefox":
                setupFirefoxDriver();
                break;
            case "edge":
                setupEdgeDriver();
                break;
            default:
                throw new IllegalArgumentException("不支持的浏览器类型: " + browser);
        }
        
        // 设置通用配置
        setupDriver();
    }
    
    /**
     * 测试后置操作 - 关闭浏览器
     */
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
            System.out.println("浏览器已关闭");
        }
    }
    
    /**
     * 加载配置文件
     */
    private void loadConfig() {
        config = new Properties();
        try (InputStream input = getClass().getClassLoader().getResourceAsStream("config.properties")) {
            if (input != null) {
                config.load(input);
            }
        } catch (IOException ex) {
            System.out.println("警告: 无法加载配置文件，使用默认设置");
        }
    }
    
    /**
     * 设置Chrome驱动
     */
    private void setupChromeDriver() {
        WebDriverManager.chromedriver().setup();
        
        ChromeOptions options = new ChromeOptions();
        
        // 根据配置决定是否使用无头模式
        if ("true".equals(config.getProperty("headless"))) {
            options.addArguments("--headless");
            System.out.println("Chrome: 使用无头模式");
        }
        
        // 根据配置决定是否禁用GPU（无头模式下建议禁用）
        if ("true".equals(config.getProperty("disable-gpu"))) {
            options.addArguments("--disable-gpu");
        }
        
        // 其他常用选项
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--window-size=1920,1080");
        
        driver = new ChromeDriver(options);
        System.out.println("Chrome浏览器已启动");
    }
    
    /**
     * 设置Firefox驱动
     */
    private void setupFirefoxDriver() {
        WebDriverManager.firefoxdriver().setup();
        
        FirefoxOptions options = new FirefoxOptions();
        
        // 根据配置决定是否使用无头模式
        if ("true".equals(config.getProperty("headless"))) {
            options.addArguments("--headless");
            System.out.println("Firefox: 使用无头模式");
        }
        
        driver = new FirefoxDriver(options);
        System.out.println("Firefox浏览器已启动");
    }
    
    /**
     * 设置Edge驱动
     */
    private void setupEdgeDriver() {
        WebDriverManager.edgedriver().setup();
        
        EdgeOptions options = new EdgeOptions();
        
        // 根据配置决定是否使用无头模式
        if ("true".equals(config.getProperty("headless"))) {
            options.addArguments("--headless");
            System.out.println("Edge: 使用无头模式");
        }
        
        // 其他常用选项
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--window-size=1920,1080");
        
        driver = new EdgeDriver(options);
        System.out.println("Edge浏览器已启动");
    }
    
    /**
     * 设置WebDriver通用配置
     */
    private void setupDriver() {
        // 设置隐式等待时间
        int timeout = 10;  // 默认10秒
        String timeoutStr = config.getProperty("timeout.seconds");
        if (timeoutStr != null) {
            try {
                timeout = Integer.parseInt(timeoutStr);
            } catch (NumberFormatException e) {
                System.out.println("警告: 无效的超时时间设置，使用默认值10秒");
            }
        }
        
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(timeout));
        System.out.println("隐式等待时间设置为: " + timeout + "秒");
        
        // 设置页面加载超时
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        
        // 设置脚本执行超时
        driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(20));
        
        // 最大化窗口
        driver.manage().window().maximize();
        
        System.out.println("WebDriver配置完成");
    }
    
    /**
     * 获取配置属性
     */
    protected String getConfigProperty(String key) {
        return config.getProperty(key);
    }
    
    /**
     * 获取配置属性（带默认值）
     */
    protected String getConfigProperty(String key, String defaultValue) {
        return config.getProperty(key, defaultValue);
    }
}