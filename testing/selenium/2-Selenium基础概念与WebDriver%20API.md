# 第2章：Selenium基础概念与WebDriver API

## 📖 章节介绍

本章将深入讲解Selenium WebDriver的核心概念、接口和常用API。通过本章的学习，您将掌握WebDriver的基础操作方法，理解元素定位的基本原理，并能够编写基础的页面交互脚本。这些知识是构建复杂自动化测试脚本的基石。

## 🎯 学习目标

- 理解WebDriver接口层次结构和设计原理
- 掌握常用的WebDriver API方法
- 学会基本的页面导航操作
- 了解Cookies、JavaScript执行等高级API
- 掌握WebElement的基本操作方法
- 理解不同的元素定位策略

## 2.1 WebDriver接口体系

### 2.1.1 WebDriver接口层次结构

Selenium WebDriver采用基于接口的设计模式，主要接口层次如下：

```
WebDriver (顶层接口)
├── SearchContext (搜索上下文接口)
├── JavascriptExecutor (执行JavaScript接口)
├── TakesScreenshot (截图接口)
└── WebDriver
    ├── ChromeDriver
    ├── FirefoxDriver
    ├── EdgeDriver
    ├── SafariDriver
    └── ...
```

### 2.1.2 核心接口说明

#### WebDriver接口
WebDriver是Selenium的核心接口，定义了浏览器操作的基本方法：

```java
// 导航方法
void get(String url);                    // 导航到指定URL
String getCurrentUrl();                  // 获取当前URL
String getTitle();                       // 获取页面标题
void navigate();                         // 返回Navigation接口，用于前进/后退/刷新

// 窗口管理
Window getWindowHandle();                // 获取当前窗口句柄
Set<String> getWindowHandles();         // 获取所有窗口句柄
void switchTo();                         // 返回TargetLocator接口，用于切换窗口/框架/警告框

// 查找元素
WebElement findElement(By by);           // 查找单个元素
List<WebElement> findElements(By by);    // 查找多个元素

// 选项管理
Options manage();                        // 返回Options接口，用于管理Cookie、超时等

// 执行操作
void quit();                             // 关闭所有窗口并退出WebDriver
void close();                            // 关闭当前窗口
```

#### SearchContext接口
SearchContext是WebDriver的父接口，定义了元素查找的基本方法：

```java
WebElement findElement(By by);           // 查找单个元素
List<WebElement> findElements(By by);    // 查找多个元素
```

#### JavascriptExecutor接口
用于在浏览器中执行JavaScript代码：

```java
Object executeScript(String script, Object... args);     // 同步执行JavaScript
Object executeAsyncScript(String script, Object... args); // 异步执行JavaScript
```

#### TakesScreenshot接口
用于页面截图：

```java
<X> X getScreenshotAs(OutputType<X> target) throws WebDriverException;
```

## 2.2 WebDriver基本操作

### 2.2.1 页面导航

#### get()方法
`get()`方法是最基础的导航方法，用于导航到指定URL：

```java
// 导航到示例网站
driver.get("https://www.example.com");

// 获取页面信息
System.out.println("当前URL: " + driver.getCurrentUrl());
System.out.println("页面标题: " + driver.getTitle());
```

**注意事项：**
- `get()`方法会等待页面完全加载（document.readyState为complete）
- 如果页面加载超时（默认30秒），会抛出TimeoutException
- 可以通过设置页面加载超时时间来调整：
  ```java
  driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(60));
  ```

#### Navigation接口
Navigation接口提供了更灵活的导航操作：

```java
// 获取Navigation接口
Navigation navigation = driver.navigate();

// 前进
navigation.forward();

// 后退
navigation.back();

// 刷新
navigation.refresh();

// 导航到URL（与get()类似，但可能行为略有不同）
navigation.to("https://www.example.com");
```

**get() vs navigate().to()的区别：**
- `get()`是WebDriver接口的直接方法
- `navigate().to()`是Navigation接口的方法
- 功能上基本相同，但实现可能有细微差别
- 建议使用`get()`进行页面加载，使用`navigate()`进行历史操作

### 2.2.2 窗口管理

#### 窗口大小和位置控制
```java
// 获取窗口大小
Dimension size = driver.manage().window().getSize();
int width = size.getWidth();
int height = size.getHeight();

// 设置窗口大小
driver.manage().window().setSize(new Dimension(800, 600));

// 最大化窗口
driver.manage().window().maximize();

// 全屏窗口
driver.manage().window().fullscreen();

// 获取窗口位置
Point position = driver.manage().window().getPosition();
int x = position.getX();
int y = position.getY();

// 设置窗口位置
driver.manage().window().setPosition(new Point(100, 100));
```

#### 多窗口处理
```java
// 获取当前窗口句柄
String currentWindow = driver.getWindowHandle();

// 打开新窗口（通过JavaScript）
((JavascriptExecutor) driver).executeScript("window.open('', '_blank');");
Set<String> allWindows = driver.getWindowHandles();
System.out.println("所有窗口句柄: " + allWindows);

// 切换到新窗口
for (String window : allWindows) {
    if (!window.equals(currentWindow)) {
        driver.switchTo().window(window);
        break;
    }
}

// 操作新窗口
driver.get("https://www.google.com");

// 关闭当前窗口
driver.close();

// 切换回原窗口
driver.switchTo().window(currentWindow);
```

### 2.2.3 浏览器选项

#### Cookie管理
```java
// 添加Cookie
Cookie cookie = new Cookie.Builder("session_id", "abc123")
    .domain(".example.com")
    .path("/")
    .expiresOn(new Date(System.currentTimeMillis() + 24 * 60 * 60 * 1000)) // 24小时后过期
    .isSecure(true)
    .isHttpOnly(true)
    .build();
driver.manage().addCookie(cookie);

// 获取所有Cookie
Set<Cookie> allCookies = driver.manage().getCookies();
for (Cookie c : allCookies) {
    System.out.println("Cookie名称: " + c.getName() + ", 值: " + c.getValue());
}

// 获取指定Cookie
Cookie sessionId = driver.manage().getCookieNamed("session_id");
if (sessionId != null) {
    System.out.println("Session ID: " + sessionId.getValue());
}

// 删除Cookie
driver.manage().deleteCookie(sessionId);  // 删除指定Cookie
driver.manage().deleteCookieNamed("session_id");  // 按名称删除
driver.manage().deleteAllCookies();  // 删除所有Cookie
```

#### 超时设置
```java
// 隐式等待 - 设置查找元素的最大等待时间
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));

// 页面加载超时 - 设置页面加载的最大等待时间
driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));

// 脚本执行超时 - 设置JavaScript执行的最大等待时间
driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(20));
```

## 2.3 元素定位基础

### 2.3.1 By类与定位策略

Selenium提供了多种元素定位策略，都通过By类实现：

```java
// 通过ID定位 - 最常用，最高效
By byId = By.id("element-id");
WebElement elementById = driver.findElement(byId);

// 通过Name定位
By byName = By.name("element-name");
WebElement elementByName = driver.findElement(byName);

// 通过ClassName定位
By byClassName = By.className("element-class");
WebElement elementByClass = driver.findElement(byClassName);

// 通过TagName定位
By byTagName = By.tagName("div");
WebElement elementByTag = driver.findElement(byTagName);

// 通过LinkText定位（精确匹配）
By byLinkText = By.linkText("Click Here");
WebElement elementByLink = driver.findElement(byLinkText);

// 通过PartialLinkText定位（部分匹配）
By byPartialLinkText = By.partialLinkText("Click");
WebElement elementByPartialLink = driver.findElement(byPartialLinkText);

// 通过CSS选择器定位 - 功能强大，性能较好
By byCss = By.cssSelector("#id .class > tag");
WebElement elementByCss = driver.findElement(byCss);

// 通过XPath定位 - 功能最强大，但性能稍差
By byXPath = By.xpath("//div[@id='id']//a[contains(text(), 'Click')]");
WebElement elementByXPath = driver.findElement(byXPath);
```

### 2.3.2 定位策略选择指南

| 定位策略 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| ID | 元素有唯一ID时 | 精确、快速 | 不是所有元素都有ID |
| Name | 表单元素 | 对表单友好 | 可能重复 |
| ClassName | 样式类元素 | 可批量选择 | 可能多个元素使用同一类 |
| TagName | 同类型元素 | 简单易用 | 精确度低 |
| LinkText/PartialLinkText | 链接元素 | 直观 | 仅适用于链接 |
| CSS Selector | 复杂定位 | 功能强大，性能好 | 语法复杂 |
| XPath | 复杂定位 | 功能最强大 | 语法复杂，性能较差 |

**最佳实践建议：**
1. 优先使用ID定位，因为它最精确、最快
2. 没有ID时，考虑使用CSS Selector
3. 需要复杂定位时，使用XPath
4. 避免使用绝对XPath（如`/html/body/div[1]/...`），因为它脆弱且易受页面结构变化影响

## 2.4 WebElement基本操作

### 2.4.1 WebElement接口概述

WebElement代表页面上的一个元素，提供了操作该元素的各种方法：

```java
// 获取元素属性
String id = element.getAttribute("id");
String className = element.getAttribute("class");
String value = element.getAttribute("value");

// 获取元素文本
String text = element.getText();

// 获取CSS属性
String backgroundColor = element.getCssValue("background-color");
String fontSize = element.getCssValue("font-size");

// 元素状态检查
boolean isDisplayed = element.isDisplayed();      // 是否可见
boolean isEnabled = element.isEnabled();          // 是否可用
boolean isSelected = element.isSelected();        // 是否选中（适用于复选框、单选框）

// 元素尺寸和位置
Dimension size = element.getSize();               // 获取尺寸
Point location = element.getLocation();           // 获取位置
Rectangle rect = element.getRect();               // 同时获取尺寸和位置

// 元素交互
element.click();                                  // 点击
element.sendKeys("input text");                   // 输入文本
element.clear();                                  // 清空输入框
```

### 2.4.2 文本输入与表单操作

```java
// 文本输入
WebElement searchBox = driver.findElement(By.id("search"));
searchBox.sendKeys("Selenium WebDriver");

// 清空输入框
searchBox.clear();
searchBox.sendKeys("新的搜索词");

// 特殊键位操作
searchBox.sendKeys(Keys.RETURN);      // 按回车键
searchBox.sendKeys(Keys.CONTROL + "a"); // 全选
searchBox.sendKeys(Keys.CONTROL + "c"); // 复制

// 文件上传
WebElement fileInput = driver.findElement(By.id("file-upload"));
fileInput.sendKeys("C:\\path\\to\\file.txt");

// 下拉框选择（使用Select类）
Select dropdown = new Select(driver.findElement(By.id("dropdown")));
dropdown.selectByVisibleText("选项文本");
dropdown.selectByValue("option-value");
dropdown.selectByIndex(2);  // 第三个选项（索引从0开始）

// 多选下拉框
Select multiSelect = new Select(driver.findElement(By.id("multi-select")));
multiSelect.selectByVisibleText("选项1");
multiSelect.selectByVisibleText("选项2");
multiSelect.deselectByVisibleText("选项1");  // 取消选择
multiSelect.deselectAll();  // 取消所有选择
```

### 2.4.3 按钮与链接操作

```java
// 点击按钮
WebElement button = driver.findElement(By.id("submit-button"));
button.click();

// 点击链接
WebElement link = driver.findElement(By.linkText("了解更多"));
link.click();

// 使用JavaScript点击（适用于点击覆盖或不可见元素）
WebElement hiddenButton = driver.findElement(By.id("hidden-button"));
((JavascriptExecutor) driver).executeScript("arguments[0].click();", hiddenButton);

// 验证链接的href属性
WebElement linkWithHref = driver.findElement(By.tagName("a"));
String href = linkWithHref.getAttribute("href");
System.out.println("链接目标: " + href);
```

## 2.5 JavaScript交互

### 2.5.1 执行JavaScript代码

Selenium提供了`JavascriptExecutor`接口，允许在页面中执行JavaScript代码：

```java
// 将WebDriver转换为JavascriptExecutor
JavascriptExecutor jsExecutor = (JavascriptExecutor) driver;

// 执行简单JavaScript并获取返回值
String pageTitle = (String) jsExecutor.executeScript("return document.title;");
System.out.println("页面标题: " + pageTitle);

// 执行带参数的JavaScript
Long windowHeight = (Long) jsExecutor.executeScript("return window.innerHeight;");
System.out.println("窗口高度: " + windowHeight);

// 修改元素属性
jsExecutor.executeScript("document.getElementById('element-id').style.backgroundColor = 'red';");

// 滚动到页面底部
jsExecutor.executeScript("window.scrollTo(0, document.body.scrollHeight);");

// 滚动到特定元素
WebElement element = driver.findElement(By.id("target-element"));
jsExecutor.executeScript("arguments[0].scrollIntoView(true);", element);
```

### 2.5.2 异步JavaScript执行

对于需要时间的异步操作，可以使用`executeAsyncScript`：

```java
// 异步执行JavaScript，适用于AJAX调用等
jsExecutor.executeAsyncScript(
    "var callback = arguments[arguments.length - 1];" +
    "setTimeout(function() { callback('异步操作完成'); }, 3000);"
);
```

### 2.5.3 实用JavaScript操作

```java
// 获取页面源代码
String pageSource = (String) jsExecutor.executeScript("return document.documentElement.outerHTML;");

// 获取元素的内部HTML
WebElement element = driver.findElement(By.id("content"));
String innerHTML = (String) jsExecutor.executeScript("return arguments[0].innerHTML;", element);

// 触发自定义事件
jsExecutor.executeScript(
    "var event = new Event('customEvent', { bubbles: true, cancelable: true });" +
    "arguments[0].dispatchEvent(event);", 
    element
);

// 高亮元素（用于调试）
jsExecutor.executeScript(
    "arguments[0].style.border = '3px solid red'; " +
    "arguments[0].style.backgroundColor = 'yellow';", 
    element
);

// 等待元素出现
jsExecutor.executeScript(
    "return !!document.querySelector('#wait-for-element')"
);
```

## 2.6 截图功能

### 2.6.1 页面截图

```java
// 将WebDriver转换为TakesScreenshot
TakesScreenshot screenshot = (TakesScreenshot) driver;

// 截取整个页面
File screenshotFile = screenshot.getScreenshotAs(OutputType.FILE);
FileUtils.copyFile(screenshotFile, new File("screenshots/full_page.png"));

// 直接获取截图字节数组
byte[] screenshotBytes = screenshot.getScreenshotAs(OutputType.BYTES);

// 获取Base64编码的截图
String base64Screenshot = screenshot.getScreenshotAs(OutputType.BASE64);
```

### 2.6.2 元素截图（Selenium 4+）

```java
// 截取特定元素
WebElement element = driver.findElement(By.id("target-element"));
File elementScreenshot = element.getScreenshotAs(OutputType.FILE);
FileUtils.copyFile(elementScreenshot, new File("screenshots/element.png"));
```

### 2.6.3 封装截图工具类

```java
import org.openqa.selenium.*;
import org.apache.commons.io.FileUtils;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ScreenshotUtil {
    private WebDriver driver;
    private String screenshotPath = "screenshots/";
    
    public ScreenshotUtil(WebDriver driver) {
        this.driver = driver;
        // 确保截图目录存在
        new File(screenshotPath).mkdirs();
    }
    
    /**
     * 截取整个页面并保存
     * @param fileName 文件名（不含扩展名）
     * @return 保存的文件路径
     */
    public String takeFullPageScreenshot(String fileName) {
        try {
            // 生成带时间戳的文件名
            String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss").format(new Date());
            String fullFileName = fileName + "_" + timestamp + ".png";
            String filePath = screenshotPath + fullFileName;
            
            // 截图并保存
            File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            FileUtils.copyFile(screenshot, new File(filePath));
            
            System.out.println("截图已保存: " + filePath);
            return filePath;
        } catch (IOException e) {
            System.err.println("截图保存失败: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 截取特定元素
     * @param element 要截图的元素
     * @param fileName 文件名（不含扩展名）
     * @return 保存的文件路径
     */
    public String takeElementScreenshot(WebElement element, String fileName) {
        try {
            // 生成带时间戳的文件名
            String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss").format(new Date());
            String fullFileName = fileName + "_" + timestamp + ".png";
            String filePath = screenshotPath + fullFileName;
            
            // 截图并保存
            File screenshot = element.getScreenshotAs(OutputType.FILE);
            FileUtils.copyFile(screenshot, new File(filePath));
            
            System.out.println("元素截图已保存: " + filePath);
            return filePath;
        } catch (IOException e) {
            System.err.println("元素截图保存失败: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 测试失败时自动截图
     * @param testName 测试名称
     * @param status 测试状态（通过/失败）
     */
    public void captureOnTestResult(String testName, boolean status) {
        if (!status) {
            takeFullPageScreenshot("FAILED_" + testName);
        }
    }
}
```

## 2.7 高级API应用

### 2.7.1 执行文件下载

```java
// 设置下载目录（Chrome示例）
HashMap<String, Object> chromePrefs = new HashMap<>();
chromePrefs.put("download.default_directory", "C:\\downloads");
chromePrefs.put("download.prompt_for_download", false);

ChromeOptions options = new ChromeOptions();
options.setExperimentalOption("prefs", chromePrefs);

WebDriver driver = new ChromeDriver(options);

// 触发下载
driver.get("https://example.com/download");
driver.findElement(By.id("download-button")).click();

// 等待下载完成（简单示例）
Thread.sleep(5000);
```

### 2.7.2 操作浏览器历史记录

```java
// 获取历史记录数量
Long historyCount = (Long) jsExecutor.executeScript("return window.history.length;");
System.out.println("历史记录数量: " + historyCount);

// 返回到历史记录中的特定位置
jsExecutor.executeScript("window.history.go(-2);"); // 后退两页
```

### 2.7.3 获取页面性能数据

```java
// 获取页面加载时间
Map<String, Object> timing = (Map<String, Object>) jsExecutor.executeScript(
    "var perf = performance.timing;" +
    "return {" +
    "  navigationStart: perf.navigationStart," +
    "  domContentLoaded: perf.domContentLoadedEventEnd," +
    "  loadComplete: perf.loadEventEnd" +
    "};"
);

Long navigationStart = (Long) timing.get("navigationStart");
Long domContentLoaded = (Long) timing.get("domContentLoaded");
Long loadComplete = (Long) timing.get("loadComplete");

long domLoadTime = domContentLoaded - navigationStart;
long fullLoadTime = loadComplete - navigationStart;

System.out.println("DOM加载时间: " + domLoadTime + "ms");
System.out.println("完整加载时间: " + fullLoadTime + "ms");
```

## 2.8 常见问题与解决方案

### 2.8.1 元素定位失败

**问题**：`NoSuchElementException` - 找不到元素

**可能原因**：
- 元素ID/属性不正确
- 页面尚未加载完成
- 元素在iframe中
- 元素被其他元素遮挡

**解决方案**：
```java
// 1. 检查元素定位策略
try {
    driver.findElement(By.id("correct-id"));
} catch (NoSuchElementException e) {
    // 尝试其他定位方式
    driver.findElement(By.cssSelector(".class-name"));
}

// 2. 使用显式等待
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("element-id")));

// 3. 检查iframe
driver.switchTo().frame("frame-name");
WebElement elementInFrame = driver.findElement(By.id("element-in-frame"));
driver.switchTo().defaultContent();
```

### 2.8.2 StaleElementReferenceException

**问题**：元素引用过期，元素已被修改或删除

**解决方案**：
```java
// 重新查找元素
try {
    element.click();
} catch (StaleElementReferenceException e) {
    element = driver.findElement(By.id("element-id"));
    element.click();
}

// 或者使用更可靠的定位方式
public void safeClick(By locator) {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement element = wait.until(ExpectedConditions.elementToBeClickable(locator));
    element.click();
}
```

### 2.8.3 ElementClickInterceptedException

**问题**：点击元素时被其他元素遮挡

**解决方案**：
```java
// 方法1：使用JavaScript点击
((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);

// 方法2：滚动到元素后点击
((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(true);", element);
element.click();

// 方法3：使用Actions类
Actions actions = new Actions(driver);
actions.moveToElement(element).click().perform();
```

## 2.9 最佳实践

### 2.9.1 定位策略最佳实践

1. **优先使用ID定位**：精确且快速
2. **避免使用绝对XPath**：页面结构变化时易失败
3. **使用相对定位**：更稳定可靠
4. **创建可靠的定位策略**：结合多个属性定位
5. **封装元素定位方法**：便于维护

```java
// 封装元素查找方法
public WebElement findElementWithRetry(By locator, int maxAttempts) {
    int attempts = 0;
    while (attempts < maxAttempts) {
        try {
            return driver.findElement(locator);
        } catch (NoSuchElementException e) {
            attempts++;
            if (attempts >= maxAttempts) {
                throw e;
            }
            try {
                Thread.sleep(1000); // 等待1秒后重试
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("等待被中断", ie);
            }
        }
    }
    throw new NoSuchElementException("无法找到元素: " + locator);
}
```

### 2.9.2 API使用最佳实践

1. **合理使用等待策略**：避免使用Thread.sleep()，使用显式等待
2. **异常处理**：适当处理各种异常情况
3. **资源清理**：确保测试后关闭浏览器和释放资源
4. **日志记录**：记录关键操作和测试结果
5. **模块化设计**：将常用操作封装为方法

```java
// 封装常用操作
public class BrowserUtils {
    private WebDriver driver;
    
    public BrowserUtils(WebDriver driver) {
        this.driver = driver;
    }
    
    public void navigateToUrl(String url) {
        System.out.println("导航到: " + url);
        driver.get(url);
    }
    
    public void clickElement(By locator) {
        try {
            WebElement element = driver.findElement(locator);
            element.click();
            System.out.println("点击元素: " + locator);
        } catch (Exception e) {
            System.err.println("点击元素失败: " + locator + ", 错误: " + e.getMessage());
            throw e;
        }
    }
    
    public void typeText(By locator, String text) {
        try {
            WebElement element = driver.findElement(locator);
            element.clear();
            element.sendKeys(text);
            System.out.println("输入文本: " + text + " 到元素: " + locator);
        } catch (Exception e) {
            System.err.println("输入文本失败: " + locator + ", 错误: " + e.getMessage());
            throw e;
        }
    }
}
```

## 2.10 章节总结

本章详细介绍了Selenium WebDriver的核心概念和常用API，包括WebDriver接口体系、基本操作方法、元素定位策略、WebElement操作、JavaScript交互和截图功能。通过学习这些内容，您应该能够编写基础的自动化测试脚本，并对页面元素进行基本的交互操作。

### 关键要点回顾

1. **WebDriver接口体系**：理解WebDriver的接口层次结构和设计模式
2. **基本操作**：掌握页面导航、窗口管理、Cookie操作等基本功能
3. **元素定位**：熟练使用各种定位策略，理解各自的优缺点和适用场景
4. **WebElement操作**：掌握文本输入、点击、状态检查等基本操作
5. **JavaScript交互**：学会使用JavascriptExecutor执行自定义脚本
6. **截图功能**：掌握页面和元素截图的方法和技巧

### 下一步学习

在下一章中，我们将深入学习元素定位策略和交互操作，包括高级定位技巧、复杂交互场景处理以及Actions类的使用，为编写更加复杂和稳定的自动化测试脚本打下坚实基础。

## 2.11 实践练习

1. **基础导航操作**：编写一个测试，打开多个网站，测试前进、后退和刷新功能
2. **元素定位练习**：使用不同定位策略找到同一页面的多个元素，比较它们的性能和稳定性
3. **表单操作**：编写一个完整的表单填写和提交测试
4. **JavaScript交互**：使用JavaScript执行滚动、高亮元素、获取元素属性等操作
5. **截图功能**：封装一个截图工具类，实现失败时自动截图功能

请完成以上练习，并思考：
- 在什么情况下应该使用JavaScript操作而不是Selenium原生API？
- 如何提高元素定位的稳定性和效率？
- 如何处理动态加载的元素和异步操作？

通过思考这些问题，您将更深入地理解Selenium WebDriver的使用方法和最佳实践。