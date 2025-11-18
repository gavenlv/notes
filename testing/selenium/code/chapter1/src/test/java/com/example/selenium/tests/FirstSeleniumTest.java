package com.example.selenium.tests;

import com.example.selenium.base.BaseTest;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.testng.Assert;
import org.testng.annotations.Test;
import org.testng.annotations.DataProvider;

/**
 * 第一个Selenium测试类
 * 演示基本的浏览器操作
 */
public class FirstSeleniumTest extends BaseTest {
    
    /**
     * 第一个简单测试 - 访问Example网站
     */
    @Test
    public void firstTest() {
        // 导航到网页
        driver.get("https://www.example.com");
        
        // 获取并验证标题
        String title = driver.getTitle();
        System.out.println("页面标题: " + title);
        Assert.assertEquals(title, "Example Domain", "页面标题不匹配");
        
        // 获取并验证URL
        String url = driver.getCurrentUrl();
        System.out.println("当前URL: " + url);
        Assert.assertTrue(url.contains("example.com"), "URL不包含example.com");
        
        // 获取页面源代码长度
        String pageSource = driver.getPageSource();
        System.out.println("页面源代码长度: " + pageSource.length());
        Assert.assertTrue(pageSource.contains("Example Domain"), "页面源代码应包含'Example Domain'");
    }
    
    /**
     * 测试访问百度首页
     */
    @Test
    public void testBaiduHomePage() {
        // 导航到百度首页
        driver.get("https://www.baidu.com");
        
        // 验证标题
        String title = driver.getTitle();
        System.out.println("百度页面标题: " + title);
        Assert.assertTrue(title.contains("百度"), "页面标题应包含'百度'");
        
        // 验证搜索框是否存在
        WebElement searchBox = driver.findElement(By.id("kw"));
        Assert.assertTrue(searchBox.isDisplayed(), "搜索框应该可见");
        
        // 验证搜索按钮是否存在
        WebElement searchButton = driver.findElement(By.id("su"));
        Assert.assertTrue(searchButton.isDisplayed(), "搜索按钮应该可见");
    }
    
    /**
     * 参数化测试 - 访问多个网站
     */
    @Test(dataProvider = "websiteDataProvider")
    public void testMultipleWebsites(String url, String expectedTitle) {
        // 导航到指定网页
        driver.get(url);
        
        // 获取标题
        String title = driver.getTitle();
        System.out.println("访问网站: " + url + ", 标题: " + title);
        
        // 验证标题包含预期文本
        Assert.assertTrue(title.contains(expectedTitle), 
            "标题 '" + title + "' 应包含 '" + expectedTitle + "'");
    }
    
    /**
     * 数据提供者 - 提供测试网站数据
     */
    @DataProvider(name = "websiteDataProvider")
    public Object[][] websiteDataProvider() {
        return new Object[][] {
            {"https://www.google.com", "Google"},
            {"https://www.github.com", "GitHub"},
            {"https://www.example.com", "Example Domain"}
        };
    }
    
    /**
     * 测试浏览器导航功能
     */
    @Test
    public void testBrowserNavigation() {
        // 访问第一个页面
        driver.get("https://www.example.com");
        String firstUrl = driver.getCurrentUrl();
        System.out.println("访问第一个URL: " + firstUrl);
        
        // 访问第二个页面
        driver.get("https://www.google.com");
        String secondUrl = driver.getCurrentUrl();
        System.out.println("访问第二个URL: " + secondUrl);
        Assert.assertEquals(secondUrl, "https://www.google.com/", "当前URL应该是Google");
        
        // 后退到第一个页面
        driver.navigate().back();
        String backUrl = driver.getCurrentUrl();
        System.out.println("后退后URL: " + backUrl);
        Assert.assertEquals(backUrl, firstUrl, "后退后应该回到第一个URL");
        
        // 前进到第二个页面
        driver.navigate().forward();
        String forwardUrl = driver.getCurrentUrl();
        System.out.println("前进后URL: " + forwardUrl);
        Assert.assertEquals(forwardUrl, secondUrl, "前进后应该回到第二个URL");
        
        // 刷新页面
        driver.navigate().refresh();
        System.out.println("页面已刷新");
        
        // 验证刷新后仍为同一页面
        String refreshUrl = driver.getCurrentUrl();
        Assert.assertEquals(refreshUrl, secondUrl, "刷新后URL应该不变");
    }
    
    /**
     * 测试窗口管理
     */
    @Test
    public void testWindowManagement() {
        // 获取原始窗口句柄
        String originalWindow = driver.getWindowHandle();
        
        // 访问一个有链接的页面
        driver.get("https://www.example.com");
        
        // 获取窗口大小
        int height = driver.manage().window().getSize().getHeight();
        int width = driver.manage().window().getSize().getWidth();
        System.out.println("窗口大小: 宽=" + width + ", 高=" + height);
        
        // 设置窗口大小
        driver.manage().window().setSize(new org.openqa.selenium.Dimension(800, 600));
        org.openqa.selenium.Dimension newSize = driver.manage().window().getSize();
        Assert.assertEquals(newSize.getWidth(), 800, "窗口宽度应设置为800");
        Assert.assertEquals(newSize.getHeight(), 600, "窗口高度应设置为600");
        
        // 最大化窗口
        driver.manage().window().maximize();
        org.openqa.selenium.Dimension maxSize = driver.manage().window().getSize();
        System.out.println("最大化窗口大小: 宽=" + maxSize.getWidth() + ", 高=" + maxSize.getHeight());
        Assert.assertTrue(maxSize.getWidth() > 800, "最大化后宽度应大于800");
        Assert.assertTrue(maxSize.getHeight() > 600, "最大化后高度应大于600");
        
        // 全屏模式
        driver.manage().window().fullscreen();
        org.openqa.selenium.Dimension fullSize = driver.manage().window().getSize();
        System.out.println("全屏窗口大小: 宽=" + fullSize.getWidth() + ", 高=" + fullSize.getHeight());
    }
}