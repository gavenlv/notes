package com.example.selenium.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.safari.SafariDriver;
import org.testng.Assert;
import org.testng.annotations.*;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * WebDriver API 测试类
 * 演示WebDriver的基础API操作
 */
public class WebDriverAPITest {

    private WebDriver driver;
    private static final String TEST_URL = "https://www.example.com";

    @BeforeMethod
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless"); // 无头模式运行
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        driver = new ChromeDriver(options);
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    /**
     * 测试基本的导航操作
     */
    @Test
    public void testBasicNavigation() {
        // 导航到指定URL
        driver.get(TEST_URL);
        
        // 验证当前URL
        Assert.assertEquals(driver.getCurrentUrl(), TEST_URL);
        
        // 获取页面标题
        String title = driver.getTitle();
        Assert.assertNotNull(title);
        
        // 刷新页面
        driver.navigate().refresh();
        
        // 导航到另一个页面
        driver.navigate().to("https://www.google.com");
        Assert.assertTrue(driver.getCurrentUrl().contains("google"));
        
        // 后退
        driver.navigate().back();
        Assert.assertEquals(driver.getCurrentUrl(), TEST_URL);
        
        // 前进
        driver.navigate().forward();
        Assert.assertTrue(driver.getCurrentUrl().contains("google"));
    }

    /**
     * 测试窗口和标签页操作
     */
    @Test
    public void testWindowAndTabOperations() {
        driver.get(TEST_URL);
        
        // 获取当前窗口句柄
        String originalWindow = driver.getWindowHandle();
        Assert.assertNotNull(originalWindow);
        
        // 获取所有窗口句柄
        Set<String> allWindows = driver.getWindowHandles();
        Assert.assertTrue(allWindows.size() >= 1);
        Assert.assertTrue(allWindows.contains(originalWindow));
        
        // 打开新标签页
        ((JavascriptExecutor)driver).executeScript("window.open()");
        
        // 等待新标签页打开
        Set<String> newWindows = driver.getWindowHandles();
        Assert.assertTrue(newWindows.size() > allWindows.size());
        
        // 切换到新标签页
        for (String windowHandle : newWindows) {
            if (!windowHandle.equals(originalWindow)) {
                driver.switchTo().window(windowHandle);
                break;
            }
        }
        
        // 验证已切换到新标签页
        Assert.assertNotEquals(driver.getWindowHandle(), originalWindow);
        
        // 关闭当前标签页并切换回原始标签页
        driver.close();
        driver.switchTo().window(originalWindow);
        Assert.assertEquals(driver.getWindowHandle(), originalWindow);
    }

    /**
     * 测试窗口大小和位置操作
     */
    @Test
    public void testWindowOperations() {
        driver.get(TEST_URL);
        
        // 获取窗口大小
        Dimension windowSize = driver.manage().window().getSize();
        Assert.assertTrue(windowSize.getWidth() > 0);
        Assert.assertTrue(windowSize.getHeight() > 0);
        
        // 设置窗口大小
        Dimension newSize = new Dimension(800, 600);
        driver.manage().window().setSize(newSize);
        
        // 验证窗口大小已更改
        Assert.assertEquals(driver.manage().window().getSize(), newSize);
        
        // 获取窗口位置
        Point windowPosition = driver.manage().window().getPosition();
        Assert.assertNotNull(windowPosition);
        
        // 设置窗口位置
        Point newPosition = new Point(100, 100);
        driver.manage().window().setPosition(newPosition);
        
        // 验证窗口位置已更改
        Assert.assertEquals(driver.manage().window().getPosition(), newPosition);
        
        // 最大化窗口
        driver.manage().window().maximize();
        
        // 全屏窗口
        driver.manage().window().fullscreen();
    }

    /**
     * 测试JavaScript执行
     */
    @Test
    public void testJavaScriptExecution() {
        driver.get(TEST_URL);
        
        // 执行JavaScript并返回结果
        String title = (String) ((JavascriptExecutor)driver).executeScript("return document.title;");
        Assert.assertNotNull(title);
        
        // 执行JavaScript修改页面内容
        ((JavascriptExecutor)driver).executeScript("document.body.style.backgroundColor = 'yellow';");
        
        // 执行JavaScript滚动页面
        ((JavascriptExecutor)driver).executeScript("window.scrollTo(0, document.body.scrollHeight);");
        
        // 执行JavaScript并获取元素
        WebElement element = (WebElement) ((JavascriptExecutor)driver)
                .executeScript("return document.querySelector('h1');");
        Assert.assertNotNull(element);
    }

    /**
     * 测试Cookie操作
     */
    @Test
    public void testCookieOperations() {
        driver.get(TEST_URL);
        
        // 添加Cookie
        Cookie cookie = new Cookie("test_cookie", "test_value");
        driver.manage().addCookie(cookie);
        
        // 获取Cookie
        Cookie retrievedCookie = driver.manage().getCookieNamed("test_cookie");
        Assert.assertNotNull(retrievedCookie);
        Assert.assertEquals(retrievedCookie.getValue(), "test_value");
        
        // 获取所有Cookie
        Set<Cookie> allCookies = driver.manage().getCookies();
        Assert.assertTrue(allCookies.size() >= 1);
        
        // 删除Cookie
        driver.manage().deleteCookieNamed("test_cookie");
        Assert.assertNull(driver.manage().getCookieNamed("test_cookie"));
    }

    /**
     * 测试Web Storage操作
     */
    @Test
    public void testWebStorageOperations() {
        driver.get(TEST_URL);
        
        // 设置LocalStorage
        ((JavascriptExecutor)driver).executeScript("localStorage.setItem('test_key', 'test_value');");
        
        // 获取LocalStorage
        String localStorageValue = (String) ((JavascriptExecutor)driver)
                .executeScript("return localStorage.getItem('test_key');");
        Assert.assertEquals(localStorageValue, "test_value");
        
        // 设置SessionStorage
        ((JavascriptExecutor)driver).executeScript("sessionStorage.setItem('session_key', 'session_value');");
        
        // 获取SessionStorage
        String sessionStorageValue = (String) ((JavascriptExecutor)driver)
                .executeScript("return sessionStorage.getItem('session_key');");
        Assert.assertEquals(sessionStorageValue, "session_value");
        
        // 清除LocalStorage
        ((JavascriptExecutor)driver).executeScript("localStorage.clear();");
        
        // 验证LocalStorage已清除
        String clearedValue = (String) ((JavascriptExecutor)driver)
                .executeScript("return localStorage.getItem('test_key');");
        Assert.assertNull(clearedValue);
    }

    /**
     * 测试页面源代码和元素信息
     */
    @Test
    public void testPageSourceAndElementInfo() {
        driver.get(TEST_URL);
        
        // 获取页面源代码
        String pageSource = driver.getPageSource();
        Assert.assertNotNull(pageSource);
        Assert.assertTrue(pageSource.contains("<html"));
        
        // 获取当前URL
        String currentUrl = driver.getCurrentUrl();
        Assert.assertEquals(currentUrl, TEST_URL);
        
        // 获取页面标题
        String title = driver.getTitle();
        Assert.assertNotNull(title);
    }

    /**
     * 测试不同浏览器驱动
     */
    @Test
    @Parameters("browser")
    public void testDifferentBrowsers(@Optional("chrome") String browser) {
        WebDriver driver = null;
        
        try {
            switch (browser.toLowerCase()) {
                case "chrome":
                    WebDriverManager.chromedriver().setup();
                    ChromeOptions chromeOptions = new ChromeOptions();
                    chromeOptions.addArguments("--headless");
                    driver = new ChromeDriver(chromeOptions);
                    break;
                case "firefox":
                    WebDriverManager.firefoxdriver().setup();
                    driver = new FirefoxDriver();
                    break;
                case "edge":
                    WebDriverManager.edgedriver().setup();
                    driver = new EdgeDriver();
                    break;
                case "safari":
                    // Safari驱动需要手动启用
                    driver = new SafariDriver();
                    break;
                default:
                    throw new IllegalArgumentException("不支持的浏览器: " + browser);
            }
            
            driver.get(TEST_URL);
            Assert.assertEquals(driver.getCurrentUrl(), TEST_URL);
            
        } finally {
            if (driver != null) {
                driver.quit();
            }
        }
    }

    /**
     * 测试等待策略
     */
    @Test
    public void testWaitStrategies() {
        // 设置页面加载超时
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        
        // 设置脚本执行超时
        driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(20));
        
        // 设置隐式等待
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        
        driver.get(TEST_URL);
        
        // 测试隐式等待
        long startTime = System.currentTimeMillis();
        try {
            // 尝试查找不存在的元素，应该等待10秒后抛出异常
            driver.findElement(By.id("non_existent_element"));
        } catch (NoSuchElementException e) {
            long elapsedTime = System.currentTimeMillis() - startTime;
            Assert.assertTrue(elapsedTime >= 5000); // 至少等待了5秒
        }
    }

    /**
     * 测试移动设备模拟
     */
    @Test
    public void testMobileDeviceEmulation() {
        ChromeOptions options = new ChromeOptions();
        
        // 设置移动设备模拟
        Map<String, Object> mobileEmulation = new HashMap<>();
        mobileEmulation.put("deviceName", "iPhone X");
        
        options.setExperimentalOption("mobileEmulation", mobileEmulation);
        options.addArguments("--headless");
        
        WebDriver mobileDriver = new ChromeDriver(options);
        
        try {
            mobileDriver.get(TEST_URL);
            
            // 获取用户代理字符串
            String userAgent = (String) ((JavascriptExecutor)mobileDriver)
                    .executeScript("return navigator.userAgent;");
            
            // 验证是否为移动设备用户代理
            Assert.assertTrue(userAgent.contains("iPhone") || userAgent.contains("Mobile"));
            
            // 获取窗口大小
            Dimension windowSize = mobileDriver.manage().window().getSize();
            Assert.assertTrue(windowSize.getWidth() < 1000); // 移动设备宽度通常较小
            
        } finally {
            if (mobileDriver != null) {
                mobileDriver.quit();
            }
        }
    }
}