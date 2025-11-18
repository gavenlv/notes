package com.example.selenium.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;

import java.io.File;
import java.time.Duration;

/**
 * 元素定位测试类
 * 演示Selenium的8种元素定位方式
 */
public class ElementLocatorTest {

    private WebDriver driver;
    private String testPagePath;

    @BeforeClass
    public void classSetup() {
        // 获取测试页面路径
        File file = new File("src/test/resources/locator-test.html");
        testPagePath = file.getAbsolutePath();
        System.out.println("测试页面路径: " + testPagePath);
    }

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
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    /**
     * 测试通过ID定位元素
     */
    @Test
    public void testLocateById() {
        driver.get("file:///" + testPagePath);
        
        WebElement element = driver.findElement(By.id("by-id"));
        Assert.assertNotNull(element);
        Assert.assertEquals(element.getText(), "通过ID定位的元素");
        
        // 验证元素的属性
        Assert.assertEquals(element.getAttribute("id"), "by-id");
        Assert.assertTrue(element.isDisplayed());
    }

    /**
     * 测试通过类名定位元素
     */
    @Test
    public void testLocateByClassName() {
        driver.get("file:///" + testPagePath);
        
        // 单个元素
        WebElement element = driver.findElement(By.className("highlight"));
        Assert.assertNotNull(element);
        Assert.assertTrue(element.getText().contains("通过类名定位的元素"));
        
        // 多个元素
        java.util.List<WebElement> elements = driver.findElements(By.className("form-group"));
        Assert.assertTrue(elements.size() > 0);
    }

    /**
     * 测试通过name属性定位元素
     */
    @Test
    public void testLocateByName() {
        driver.get("file:///" + testPagePath);
        
        WebElement element = driver.findElement(By.name("username"));
        Assert.assertNotNull(element);
        Assert.assertEquals(element.getAttribute("placeholder"), "请输入用户名");
        
        // 验证可以输入文本
        element.sendKeys("testuser");
        Assert.assertEquals(element.getAttribute("value"), "testuser");
    }

    /**
     * 测试通过标签名定位元素
     */
    @Test
    public void testLocateByTagName() {
        driver.get("file:///" + testPagePath);
        
        // 单个元素
        WebElement element = driver.findElement(By.tagName("h1"));
        Assert.assertNotNull(element);
        Assert.assertEquals(element.getText(), "元素定位测试页面");
        
        // 多个元素
        java.util.List<WebElement> buttons = driver.findElements(By.tagName("button"));
        Assert.assertTrue(buttons.size() > 0);
    }

    /**
     * 测试通过链接文本定位元素
     */
    @Test
    public void testLocateByLinkText() {
        driver.get("file:///" + testPagePath);
        
        // 完整链接文本
        WebElement element = driver.findElement(By.linkText("通过链接文本定位的元素"));
        Assert.assertNotNull(element);
        Assert.assertEquals(element.getAttribute("href"), "https://www.example.com");
        Assert.assertEquals(element.getAttribute("title"), "链接示例");
    }

    /**
     * 测试通过部分链接文本定位元素
     */
    @Test
    public void testLocateByPartialLinkText() {
        driver.get("file:///" + testPagePath);
        
        // 部分链接文本
        WebElement element = driver.findElement(By.partialLinkText("部分链接文本"));
        Assert.assertNotNull(element);
        Assert.assertEquals(element.getAttribute("href"), "https://www.selenium.dev");
        Assert.assertEquals(element.getAttribute("title"), "Selenium官网");
    }

    /**
     * 测试通过CSS选择器定位元素
     */
    @Test
    public void testLocateByCssSelector() {
        driver.get("file:///" + testPagePath);
        
        // 通过ID
        WebElement elementById = driver.findElement(By.cssSelector("#username"));
        Assert.assertNotNull(elementById);
        
        // 通过类名
        WebElement elementByClass = driver.findElement(By.cssSelector(".highlight"));
        Assert.assertNotNull(elementByClass);
        
        // 通过属性
        WebElement elementByAttr = driver.findElement(By.cssSelector("[data-test='locator-test']"));
        Assert.assertNotNull(elementByAttr);
        
        // 通过组合选择器
        WebElement elementByCombo = driver.findElement(By.cssSelector("form#test-form input[name='password']"));
        Assert.assertNotNull(elementByCombo);
        
        // 通过伪类选择器（定位第一个输入框）
        WebElement elementByPseudo = driver.findElement(By.cssSelector("input:first-of-type"));
        Assert.assertNotNull(elementByPseudo);
        
        // 复杂选择器（表格中的特定单元格）
        WebElement cellElement = driver.findElement(By.cssSelector("#data-table tbody tr:first-child td:first-child"));
        Assert.assertNotNull(cellElement);
        Assert.assertEquals(cellElement.getText(), "张三");
    }

    /**
     * 测试通过XPath定位元素
     */
    @Test
    public void testLocateByXPath() {
        driver.get("file:///" + testPagePath);
        
        // 绝对路径
        WebElement elementByAbsolute = driver.findElement(By.xpath("/html/body/div/div[1]/div[1]"));
        Assert.assertNotNull(elementByAbsolute);
        
        // 相对路径
        WebElement elementByRelative = driver.findElement(By.xpath("//div[@id='by-id']"));
        Assert.assertNotNull(elementByRelative);
        Assert.assertEquals(elementByRelative.getText(), "通过ID定位的元素");
        
        // 通过属性定位
        WebElement elementByAttr = driver.findElement(By.xpath("//input[@name='username']"));
        Assert.assertNotNull(elementByAttr);
        
        // 通过文本内容定位
        WebElement elementByText = driver.findElement(By.xpath("//div[contains(text(), '通过ID定位')]"));
        Assert.assertNotNull(elementByText);
        
        // 使用contains函数
        WebElement elementByContains = driver.findElement(By.xpath("//button[contains(@class, 'edit-btn')]"));
        Assert.assertNotNull(elementByContains);
        
        // 使用starts-with函数
        WebElement elementByStarts = driver.findElement(By.xpath("//button[starts-with(@id, 'submit')]"));
        Assert.assertNotNull(elementByStarts);
        
        // 使用and/or运算符
        WebElement elementByAnd = driver.findElement(By.xpath("//input[@name='username' and @type='text']"));
        Assert.assertNotNull(elementByAnd);
        
        // 使用轴定位（查找父元素）
        WebElement buttonParent = driver.findElement(By.xpath("//button[@id='submit-btn']/parent::div"));
        Assert.assertNotNull(buttonParent);
        
        // 使用index定位（表格第二行第一列）
        WebElement tableCell = driver.findElement(By.xpath("//table[@id='data-table']/tbody/tr[2]/td[1]"));
        Assert.assertNotNull(tableCell);
        Assert.assertEquals(tableCell.getText(), "李四");
    }

    /**
     * 测试定位下拉列表元素
     */
    @Test
    public void testLocateDropdownElements() {
        driver.get("file:///" + testPagePath);
        
        // 定位select元素
        WebElement selectElement = driver.findElement(By.id("country"));
        Assert.assertNotNull(selectElement);
        
        // 定位option元素
        WebElement optionElement = driver.findElement(By.cssSelector("#country option[value='china']"));
        Assert.assertNotNull(optionElement);
        Assert.assertEquals(optionElement.getText(), "中国");
        
        // 定位所有option元素
        java.util.List<WebElement> options = driver.findElements(By.cssSelector("#country option"));
        Assert.assertTrue(options.size() > 0);
        Assert.assertEquals(options.get(0).getText(), "请选择");
    }

    /**
     * 测试定位复选框和单选框
     */
    @Test
    public void testLocateCheckboxAndRadio() {
        driver.get("file:///" + testPagePath);
        
        // 定位所有复选框
        java.util.List<WebElement> checkboxes = driver.findElements(By.cssSelector("input[type='checkbox']"));
        Assert.assertTrue(checkboxes.size() > 0);
        
        // 定位所有单选框
        java.util.List<WebElement> radios = driver.findElements(By.cssSelector("input[type='radio']"));
        Assert.assertTrue(radios.size() > 0);
        
        // 定位特定复选框
        WebElement readingCheckbox = driver.findElement(By.id("reading"));
        Assert.assertNotNull(readingCheckbox);
        Assert.assertEquals(readingCheckbox.getAttribute("value"), "reading");
        
        // 通过XPath定位单选框
        WebElement maleRadio = driver.findElement(By.xpath("//input[@type='radio' and @value='male']"));
        Assert.assertNotNull(maleRadio);
        Assert.assertEquals(maleRadio.getAttribute("id"), "male");
    }

    /**
     * 测试定位表格元素
     */
    @Test
    public void testLocateTableElements() {
        driver.get("file:///" + testPagePath);
        
        // 定位表格
        WebElement table = driver.findElement(By.id("data-table"));
        Assert.assertNotNull(table);
        
        // 定位表头
        WebElement header = driver.findElement(By.cssSelector("#data-table th"));
        Assert.assertNotNull(header);
        Assert.assertEquals(header.getText(), "姓名");
        
        // 定位表体中的所有行
        java.util.List<WebElement> rows = driver.findElements(By.cssSelector("#data-table tbody tr"));
        Assert.assertTrue(rows.size() >= 3);
        
        // 定位特定行
        WebElement row2 = driver.findElement(By.id("row2"));
        Assert.assertNotNull(row2);
        
        // 定位特定单元格
        WebElement cell = driver.findElement(By.xpath("//table[@id='data-table']//tr[3]//td[3]"));
        Assert.assertNotNull(cell);
        Assert.assertEquals(cell.getText(), "广州");
        
        // 定位表格中的按钮
        WebElement editButton = driver.findElement(By.cssSelector("#row2 .edit-btn"));
        Assert.assertNotNull(editButton);
        Assert.assertEquals(editButton.getText(), "编辑");
    }

    /**
     * 测试定位隐藏元素
     */
    @Test
    public void testLocateHiddenElements() {
        driver.get("file:///" + testPagePath);
        
        // 隐藏元素仍然可以被定位，只是不可见
        WebElement hiddenElement = driver.findElement(By.id("hidden-element"));
        Assert.assertNotNull(hiddenElement);
        Assert.assertFalse(hiddenElement.isDisplayed()); // 元素不可见但存在
        
        // 点击显示按钮
        driver.findElement(By.id("show-hidden-btn")).click();
        
        // 验证元素现在可见
        Assert.assertTrue(hiddenElement.isDisplayed());
        Assert.assertEquals(hiddenElement.getText(), "这是初始隐藏的元素");
    }

    /**
     * 测试元素定位的异常处理
     */
    @Test
    public void testLocateElementExceptions() {
        driver.get("file:///" + testPagePath);
        
        // 测试NoSuchElementException
        try {
            driver.findElement(By.id("non-existent-id"));
            Assert.fail("应该抛出NoSuchElementException异常");
        } catch (NoSuchElementException e) {
            Assert.assertTrue(e.getMessage().contains("no such element"));
        }
        
        // 测试超时后的元素查找
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(2));
        long startTime = System.currentTimeMillis();
        try {
            driver.findElement(By.id("another-non-existent-id"));
            Assert.fail("应该抛出NoSuchElementException异常");
        } catch (NoSuchElementException e) {
            long elapsedTime = System.currentTimeMillis() - startTime;
            Assert.assertTrue(elapsedTime >= 2000); // 等待了至少2秒
        }
    }
}