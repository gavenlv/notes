package com.example.selenium.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.edge.EdgeDriver;
import org.testng.annotations.Test;
import org.testng.Assert;
import org.testng.annotations.Optional;
import org.testng.annotations.Parameters;

/**
 * 环境设置验证测试
 * 用于验证Selenium环境是否正确配置
 */
public class EnvironmentSetupTest {
    
    /**
     * 验证Chrome浏览器环境
     */
    @Test
    public void testChromeDriver() {
        // 自动配置Chrome驱动
        WebDriverManager.chromedriver().setup();
        
        // 创建ChromeDriver实例
        WebDriver driver = new ChromeDriver();
        
        try {
            // 导航到网页
            driver.get("https://www.google.com");
            
            // 验证标题
            String title = driver.getTitle();
            Assert.assertTrue(title.contains("Google"), "页面标题应包含'Google'");
            
            System.out.println("Chrome环境配置成功！浏览器标题: " + title);
        } finally {
            // 关闭浏览器
            driver.quit();
        }
    }
    
    /**
     * 验证Firefox浏览器环境（如果安装了Firefox）
     */
    @Test(enabled = false)  // 默认禁用，如有Firefox可改为true
    public void testFirefoxDriver() {
        // 自动配置Firefox驱动
        WebDriverManager.firefoxdriver().setup();
        
        // 创建FirefoxDriver实例
        WebDriver driver = new FirefoxDriver();
        
        try {
            // 导航到网页
            driver.get("https://www.mozilla.org");
            
            // 验证标题
            String title = driver.getTitle();
            Assert.assertTrue(title.contains("Mozilla"), "页面标题应包含'Mozilla'");
            
            System.out.println("Firefox环境配置成功！浏览器标题: " + title);
        } finally {
            // 关闭浏览器
            driver.quit();
        }
    }
    
    /**
     * 验证Edge浏览器环境（如果安装了Edge）
     */
    @Test(enabled = false)  // 默认禁用，如有Edge可改为true
    public void testEdgeDriver() {
        // 自动配置Edge驱动
        WebDriverManager.edgedriver().setup();
        
        // 创建EdgeDriver实例
        WebDriver driver = new EdgeDriver();
        
        try {
            // 导航到网页
            driver.get("https://www.microsoft.com/edge");
            
            // 验证标题
            String title = driver.getTitle();
            Assert.assertTrue(title.contains("Microsoft Edge"), "页面标题应包含'Microsoft Edge'");
            
            System.out.println("Edge环境配置成功！浏览器标题: " + title);
        } finally {
            // 关闭浏览器
            driver.quit();
        }
    }
    
    /**
     * 参数化浏览器测试
     */
    @Test
    @Parameters("browser")
    public void testParameterizedBrowser(@Optional("chrome") String browser) {
        WebDriver driver;
        
        switch (browser.toLowerCase()) {
            case "chrome":
                WebDriverManager.chromedriver().setup();
                driver = new ChromeDriver();
                break;
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                driver = new FirefoxDriver();
                break;
            case "edge":
                WebDriverManager.edgedriver().setup();
                driver = new EdgeDriver();
                break;
            default:
                throw new IllegalArgumentException("不支持的浏览器类型: " + browser);
        }
        
        try {
            // 导航到示例网站
            driver.get("https://example.com");
            
            // 验证标题
            String title = driver.getTitle();
            Assert.assertEquals(title, "Example Domain", "页面标题应为'Example Domain'");
            
            System.out.println(browser.toUpperCase() + "浏览器测试成功！页面标题: " + title);
        } finally {
            // 关闭浏览器
            driver.quit();
        }
    }
}