# 第4章：Selenium高级操作与窗口管理

## 📖 章节介绍

本章将深入探讨Selenium中的高级操作和窗口管理技术。在复杂的Web应用测试中，经常需要处理多窗口、多框架、文件操作等复杂场景。通过本章的学习，您将能够处理各种窗口管理场景、掌握文件上传下载技巧、操作浏览器控制台、处理弹出窗口以及进行浏览器历史和导航的高级操作。

## 🎯 学习目标

- 掌握多窗口和标签页的管理方法
- 学会处理iframe和frame嵌套结构
- 了解文件上传与下载的实现方法
- 掌握浏览器控制台操作和日志分析
- 学会处理各种弹出窗口和对话框
- 理解浏览器历史管理和高级导航技巧

## 4.1 多窗口与标签页管理

### 4.1.1 窗口句柄与切换

在Web应用中，经常需要处理新打开的窗口或标签页。Selenium通过窗口句柄（Window Handle）来区分不同的窗口：

```java
// 获取当前窗口句柄
String currentWindowHandle = driver.getWindowHandle();
System.out.println("当前窗口句柄: " + currentWindowHandle);

// 打开新窗口（通过JavaScript）
((JavascriptExecutor) driver).executeScript("window.open('', '_blank');");
Set<String> allWindowHandles = driver.getWindowHandles();
System.out.println("所有窗口句柄: " + allWindowHandles);

// 切换到新打开的窗口
for (String handle : allWindowHandles) {
    if (!handle.equals(currentWindowHandle)) {
        driver.switchTo().window(handle);
        break;
    }
}

// 操作新窗口
driver.get("https://www.example.com");
System.out.println("新窗口标题: " + driver.getTitle());

// 关闭当前窗口
driver.close();

// 切换回原窗口
driver.switchTo().window(currentWindowHandle);
```

### 4.1.2 多窗口操作实用方法

封装窗口操作工具类，提高代码复用性：

```java
public class WindowManager {
    private WebDriver driver;
    private String originalWindow;
    
    public WindowManager(WebDriver driver) {
        this.driver = driver;
        this.originalWindow = driver.getWindowHandle();
    }
    
    /**
     * 切换到新打开的窗口
     * @return 新窗口的句柄
     */
    public String switchToNewWindow() {
        // 等待新窗口出现
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        
        // 获取所有窗口句柄
        Set<String> allWindows = driver.getWindowHandles();
        
        // 等待窗口数量变化
        wait.until(ExpectedConditions.numberOfWindowsToBe(allWindows.size()));
        
        // 切换到新窗口
        allWindows = driver.getWindowHandles();
        allWindows.remove(originalWindow);
        
        if (!allWindows.isEmpty()) {
            String newWindow = allWindows.iterator().next();
            driver.switchTo().window(newWindow);
            return newWindow;
        } else {
            throw new RuntimeException("没有找到新窗口");
        }
    }
    
    /**
     * 根据窗口标题切换窗口
     * @param title 窗口标题或标题的一部分
     */
    public void switchToWindowByTitle(String title) {
        Set<String> allWindows = driver.getWindowHandles();
        String currentWindow = driver.getWindowHandle();
        
        for (String windowHandle : allWindows) {
            driver.switchTo().window(windowHandle);
            if (driver.getTitle().contains(title)) {
                return;
            }
        }
        
        // 如果未找到，切换回原窗口
        driver.switchTo().window(currentWindow);
        throw new RuntimeException("未找到标题包含 '" + title + "' 的窗口");
    }
    
    /**
     * 关闭所有其他窗口，保留原始窗口
     */
    public void closeAllOtherWindows() {
        Set<String> allWindows = driver.getWindowHandles();
        
        for (String windowHandle : allWindows) {
            if (!windowHandle.equals(originalWindow)) {
                driver.switchTo().window(windowHandle);
                driver.close();
            }
        }
        
        // 切换回原始窗口
        driver.switchTo().window(originalWindow);
    }
    
    /**
     * 切换回原始窗口
     */
    public void switchToOriginalWindow() {
        driver.switchTo().window(originalWindow);
    }
}
```

### 4.1.3 多窗口交互场景

实际应用中的多窗口场景示例：

```java
// 场景：从主页面打开一个新窗口进行操作，然后返回主页面
@Test
public void testMultiWindowInteraction() {
    // 访问主页面
    driver.get("https://the-internet.herokuapp.com/windows");
    
    // 保存主窗口句柄
    String mainWindow = driver.getWindowHandle();
    
    // 点击打开新窗口的链接
    driver.findElement(By.linkText("Click Here")).click();
    
    // 等待新窗口打开并切换
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
    wait.until(ExpectedConditions.numberOfWindowsToBe(2));
    
    // 切换到新窗口
    Set<String> allWindows = driver.getWindowHandles();
    for (String window : allWindows) {
        if (!window.equals(mainWindow)) {
            driver.switchTo().window(window);
            break;
        }
    }
    
    // 在新窗口中操作
    WebElement newWindowHeading = wait.until(ExpectedConditions.visibilityOfElementLocated(By.tagName("h3")));
    Assert.assertEquals(newWindowHeading.getText(), "New Window");
    
    // 关闭新窗口并返回主窗口
    driver.close();
    driver.switchTo().window(mainWindow);
    
    // 验证仍在主页面
    WebElement mainHeading = driver.findElement(By.tagName("h3"));
    Assert.assertEquals(mainHeading.getText(), "Opening a new window");
}
```

## 4.2 Frame与iFrame处理

### 4.2.1 Frame基础操作

Frame和iFrame（inline frame）是网页中的嵌套文档，需要先切换到相应的frame内才能操作其中的元素：

```java
// 切换到frame（通过ID、name、WebElement或索引）
driver.switchTo().frame("frameId");          // 通过ID
driver.switchTo().frame("frameName");        // 通过name
driver.switchTo().frame(0);                   // 通过索引（第一个frame）
driver.switchTo().frame(frameElement);       // 通过WebElement

// 切换到默认内容（主文档）
driver.switchTo().defaultContent();

// 切换到父frame（如果当前在嵌套frame中）
driver.switchTo().parentFrame();

// 示例：处理嵌套frame结构
driver.switchTo().frame("outerFrame");       // 切换到外层frame
driver.switchTo().frame("innerFrame");       // 切换到内层frame

// 在内层frame中操作
driver.findElement(By.id("inner-element")).click();

// 返回到外层frame
driver.switchTo().parentFrame();

// 在外层frame中操作
driver.findElement(By.id("outer-element")).sendKeys("text");

// 返回到主文档
driver.switchTo().defaultContent();
```

### 4.2.2 动态Frame处理

处理动态生成的或条件性的frame：

```java
// 查找并切换到可见的frame
public void switchToVisibleFrame() {
    List<WebElement> frames = driver.findElements(By.tagName("iframe"));
    
    for (WebElement frame : frames) {
        if (frame.isDisplayed()) {
            driver.switchTo().frame(frame);
            return;
        }
    }
    
    throw new RuntimeException("没有找到可见的iframe");
}

// 根据frame内容切换
public void switchToFrameContaining(String elementText) {
    List<WebElement> frames = driver.findElements(By.tagName("iframe"));
    
    for (WebElement frame : frames) {
        driver.switchTo().frame(frame);
        
        try {
            WebElement element = driver.findElement(By.xpath("//*[contains(text(), '" + elementText + "')]"));
            if (element != null) {
                return; // 找到包含指定文本的元素，停留在当前frame
            }
        } catch (NoSuchElementException e) {
            // 继续检查下一个frame
        }
        
        driver.switchTo().defaultContent(); // 返回主文档，检查下一个frame
    }
    
    throw new RuntimeException("没有找到包含文本 '" + elementText + "' 的frame");
}

// 使用显式等待等待frame加载
public void waitForAndSwitchToFrame(String frameId) {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.id(frameId)));
}
```

### 4.2.3 Frame操作完整示例

```java
@Test
public void testNestedFrames() {
    // 访问包含嵌套frame的页面
    driver.get("https://the-internet.herokuapp.com/nested_frames");
    
    // 切换到顶层frame
    driver.switchTo().frame("frame-top");
    
    // 获取顶层frame内的所有frame
    List<WebElement> frames = driver.findElements(By.tagName("frame"));
    
    // 切换到中间frame
    driver.switchTo().frame(frames.get(1));  // 中间的frame
    WebElement middleText = driver.findElement(By.id("content"));
    System.out.println("中间frame内容: " + middleText.getText());
    Assert.assertEquals(middleText.getText(), "MIDDLE", "中间frame内容应为'MIDDLE'");
    
    // 返回顶层frame
    driver.switchTo().parentFrame();
    
    // 切换到底部frame
    driver.switchTo().defaultContent();  // 先返回主文档
    driver.switchTo().frame("frame-bottom");
    
    WebElement bottomText = driver.findElement(By.id("content"));
    System.out.println("底部frame内容: " + bottomText.getText());
    Assert.assertEquals(bottomText.getText(), "BOTTOM", "底部frame内容应为'BOTTOM'");
    
    // 返回主文档
    driver.switchTo().defaultContent();
}
```

## 4.3 文件上传与下载

### 4.3.1 文件上传

Selenium处理文件上传有两种主要方式：

#### 方式一：使用sendKeys方法（适用于<input type="file">元素）

```java
// 简单的文件上传
WebElement fileInput = driver.findElement(By.id("file-upload"));
fileInput.sendKeys("C:\\path\\to\\your\\file.txt");

// 提交表单
driver.findElement(By.id("file-submit")).click();

// 验证上传结果
WebElement uploadMessage = driver.findElement(By.id("upload-messages"));
Assert.assertTrue(uploadMessage.getText().contains("文件上传成功"));
```

#### 方式二：使用AutoIT或其他工具（适用于非标准上传）

对于非标准的文件上传组件（如Flash上传器、自定义上传组件），可以使用AutoIT或Robot类：

```java
// 使用Java Robot类模拟键盘操作
public void uploadFileWithRobot(String filePath) {
    try {
        // 设置剪贴板内容
        StringSelection stringSelection = new StringSelection(filePath);
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents(stringSelection, null);
        
        // 创建Robot实例
        Robot robot = new Robot();
        
        // 模拟Ctrl+V粘贴
        robot.keyPress(KeyEvent.VK_CONTROL);
        robot.keyPress(KeyEvent.VK_V);
        robot.keyRelease(KeyEvent.VK_V);
        robot.keyRelease(KeyEvent.VK_CONTROL);
        
        // 模拟Enter确认
        robot.keyPress(KeyEvent.VK_ENTER);
        robot.keyRelease(KeyEvent.VK_ENTER);
        
        // 等待上传完成
        Thread.sleep(2000);
    } catch (Exception e) {
        throw new RuntimeException("文件上传失败", e);
    }
}

// 使用示例
WebElement uploadButton = driver.findElement(By.id("upload-button"));
uploadButton.click(); // 点击打开文件选择对话框

// 等待对话框出现
Thread.sleep(1000);

// 使用Robot类模拟文件选择
uploadFileWithRobot("C:\\path\\to\\file.txt");
```

### 4.3.2 文件下载

#### 配置浏览器下载目录

```java
// Chrome下载配置
HashMap<String, Object> chromePrefs = new HashMap<>();
chromePrefs.put("download.default_directory", "C:\\downloads");
chromePrefs.put("download.prompt_for_download", false);
chromePrefs.put("download.directory_upgrade", true);
chromePrefs.put("safebrowsing.enabled", true);

ChromeOptions options = new ChromeOptions();
options.setExperimentalOption("prefs", chromePrefs);

WebDriver driver = new ChromeDriver(options);

// Firefox下载配置
FirefoxProfile firefoxProfile = new FirefoxProfile();
firefoxProfile.setPreference("browser.download.folderList", 2); // 0:桌面, 1:默认, 2:自定义
firefoxProfile.setPreference("browser.download.dir", "C:\\downloads");
firefoxProfile.setPreference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream");
firefoxProfile.setPreference("browser.download.manager.showWhenStarting", false);
firefoxProfile.setPreference("pdfjs.disabled", true); // 禁用内置PDF查看器

WebDriver driver = new FirefoxDriver(firefoxProfile);
```

#### 文件下载验证

```java
// 触发下载
driver.get("https://example.com/file-to-download");
driver.findElement(By.id("download-button")).click();

// 等待下载完成
public boolean waitForDownloadToComplete(String fileName, int timeoutInSeconds) {
    File downloadDir = new File("C:\\downloads");
    long endTime = System.currentTimeMillis() + (timeoutInSeconds * 1000);
    
    while (System.currentTimeMillis() < endTime) {
        File[] files = downloadDir.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.getName().equals(fileName) && !file.getName().endsWith(".crdownload")) {
                    return true; // 下载完成且不是临时文件
                }
            }
        }
        
        try {
            Thread.sleep(500); // 等待500ms再检查
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
    }
    
    return false; // 下载未在指定时间内完成
}

// 使用示例
boolean downloaded = waitForDownloadToComplete("example-file.pdf", 30);
Assert.assertTrue(downloaded, "文件下载未在30秒内完成");

// 验证文件大小
File downloadedFile = new File("C:\\downloads\\example-file.pdf");
Assert.assertTrue(downloadedFile.exists(), "下载的文件不存在");
Assert.assertTrue(downloadedFile.length() > 0, "下载的文件为空");
```

#### 文件下载工具类

```java
public class DownloadHelper {
    private String downloadDirectory;
    
    public DownloadHelper(String downloadDirectory) {
        this.downloadDirectory = downloadDirectory;
        // 确保下载目录存在
        new File(downloadDirectory).mkdirs();
    }
    
    /**
     * 等待文件下载完成
     * @param fileName 文件名（可以是部分匹配）
     * @param timeout 超时时间（秒）
     * @return 下载完成的文件
     */
    public File waitForDownload(String fileName, int timeout) {
        File downloadDir = new File(downloadDirectory);
        long endTime = System.currentTimeMillis() + (timeout * 1000);
        
        while (System.currentTimeMillis() < endTime) {
            File[] files = downloadDir.listFiles();
            if (files != null) {
                for (File file : files) {
                    // 检查文件名匹配且不是临时文件
                    if (file.getName().contains(fileName) && 
                        !file.getName().endsWith(".crdownload") && 
                        !file.getName().endsWith(".tmp")) {
                        return file;
                    }
                }
            }
            
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        throw new RuntimeException("文件下载超时: " + fileName);
    }
    
    /**
     * 清理下载目录
     */
    public void cleanupDownloads() {
        File downloadDir = new File(downloadDirectory);
        File[] files = downloadDir.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.delete()) {
                    System.out.println("已删除文件: " + file.getName());
                } else {
                    System.out.println("无法删除文件: " + file.getName());
                }
            }
        }
    }
}
```

## 4.4 浏览器控制台操作

### 4.4.1 访问浏览器控制台

Selenium可以通过JavascriptExecutor访问浏览器控制台日志和执行JavaScript命令：

```java
// 获取控制台日志（适用于Chrome）
Logs logs = driver.manage().logs();
LogEntries logEntries = logs.get(LogType.BROWSER);

// 遍历日志条目
for (LogEntry entry : logEntries) {
    System.out.println(new Date(entry.getTimestamp()) + " " + entry.getLevel() + " " + entry.getMessage());
}

// 只获取错误和警告日志
LogEntries errorLogs = logs.get(LogType.BROWSER);
for (LogEntry entry : errorLogs) {
    if (entry.getLevel().equals(Level.SEVERE) || entry.getLevel().equals(Level.WARNING)) {
        System.out.println("[" + entry.getLevel() + "] " + entry.getMessage());
    }
}

// 使用JavaScript记录自定义日志
((JavascriptExecutor) driver).executeScript("console.log('测试日志');");
((JavascriptExecutor) driver).executeScript("console.warn('警告信息');");
((JavascriptExecutor) driver).executeScript("console.error('错误信息');");
```

### 4.4.2 控制台命令执行

```java
// 执行JavaScript命令并获取结果
JavascriptExecutor js = (JavascriptExecutor) driver;

// 获取页面标题
String title = (String) js.executeScript("return document.title;");
System.out.println("页面标题: " + title);

// 获取所有链接
List<WebElement> links = (List<WebElement>) js.executeScript(
    "return Array.from(document.querySelectorAll('a'));");
System.out.println("页面链接数量: " + links.size());

// 检查页面是否有JavaScript错误
Object hasErrors = js.executeScript(
    "return window.__hasErrors || false;");
if (hasErrors.equals(true)) {
    System.out.println("检测到JavaScript错误");
}

// 获取所有监听器（调试用）
List<String> eventListeners = (List<String>) js.executeScript(
    "return Array.from(document.querySelectorAll('*')).map(el => ({tag: el.tagName, listeners: getEventListeners ? Object.keys(getEventListeners(el) || {}) : []}));");
System.out.println("事件监听器: " + eventListeners);
```

### 4.4.3 性能监控

```java
// 获取页面加载性能数据
JavascriptExecutor js = (JavascriptExecutor) driver;

// 获取导航计时
Map<String, Object> navigationTiming = (Map<String, Object>) js.executeScript(
    "var timing = performance.timing;" +
    "return {" +
    "  dnsLookup: timing.domainLookupEnd - timing.domainLookupStart," +
    "  tcpConnect: timing.connectEnd - timing.connectStart," +
    "  serverResponse: timing.responseEnd - timing.requestStart," +
    "  domLoad: timing.domContentLoadedEventEnd - timing.navigationStart," +
    "  pageLoad: timing.loadEventEnd - timing.navigationStart" +
    "};");

// 打印性能数据
System.out.println("DNS查询时间: " + navigationTiming.get("dnsLookup") + "ms");
System.out.println("TCP连接时间: " + navigationTiming.get("tcpConnect") + "ms");
System.out.println("服务器响应时间: " + navigationTiming.get("serverResponse") + "ms");
System.out.println("DOM加载时间: " + navigationTiming.get("domLoad") + "ms");
System.out.println("页面完全加载时间: " + navigationTiming.get("pageLoad") + "ms");

// 获取资源加载时间
List<Map<String, Object>> resourceTiming = (List<Map<String, Object>>) js.executeScript(
    "return performance.getEntriesByType('resource').map(function(r) {" +
    "  return {name: r.name, type: r.initiatorType, duration: r.duration};" +
    "});");

// 找出加载时间最长的资源
Optional<Map<String, Object>> slowestResource = resourceTiming.stream()
    .max(Comparator.comparing(r -> (Long) r.get("duration")));

if (slowestResource.isPresent()) {
    Map<String, Object> resource = slowestResource.get();
    System.out.println("加载最慢的资源: " + resource.get("name") + 
                      ", 类型: " + resource.get("type") + 
                      ", 耗时: " + resource.get("duration") + "ms");
}
```

## 4.5 弹出窗口与对话框处理

### 4.5.1 警告框（Alert）

JavaScript警告框是简单的弹出框，包含一个消息和一个确认按钮：

```java
// 触发警告框
driver.findElement(By.id("alert-button")).click();

// 切换到警告框
Alert alert = driver.switchTo().alert();

// 获取警告框文本
String alertText = alert.getText();
System.out.println("警告框内容: " + alertText);

// 接受警告框（点击"确定"按钮）
alert.accept();

// 拒绝警告框（如果有取消按钮）
alert.dismiss();

// 输入文本（适用于prompt类型的对话框）
alert.sendKeys("输入的文本");
alert.accept();

// 使用显式等待等待警告框出现
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
Alert alert = wait.until(ExpectedConditions.alertIsPresent());
alert.accept();
```

### 4.5.2 确认框（Confirm）

确认框有两个按钮：确定和取消：

```java
// 触发确认框
driver.findElement(By.id("confirm-button")).click();

// 等待确认框出现
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
Alert confirmDialog = wait.until(ExpectedConditions.alertIsPresent());

// 获取确认框消息
String message = confirmDialog.getText();
System.out.println("确认框消息: " + message);

// 选择"确定"
confirmDialog.accept();

// 或者选择"取消"
// confirmDialog.dismiss();
```

### 4.5.3 提示框（Prompt）

提示框允许用户输入文本：

```java
// 触发提示框
driver.findElement(By.id("prompt-button")).click();

// 切换到提示框
Alert promptDialog = driver.switchTo().alert();

// 输入文本
promptDialog.sendKeys("用户输入的内容");

// 获取提示框消息
String promptMessage = promptDialog.getText();
System.out.println("提示框消息: " + promptMessage);

// 确认输入
promptDialog.accept();
```

### 4.5.4 模态对话框处理

对于非标准的模态对话框（非JavaScript原生对话框），需要使用常规元素操作：

```java
// 等待模态框出现
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement modalDialog = wait.until(ExpectedConditions.visibilityOfElementLocated(
    By.cssSelector(".modal-dialog")));

// 在模态框中操作
WebElement modalTitle = modalDialog.findElement(By.className("modal-title"));
System.out.println("模态框标题: " + modalTitle.getText());

// 填写表单
WebElement inputField = modalDialog.findElement(By.id("modal-input"));
inputField.sendKeys("在模态框中输入的内容");

// 点击确认按钮
WebElement confirmButton = modalDialog.findElement(By.id("modal-confirm"));
confirmButton.click();

// 等待模态框关闭
wait.until(ExpectedConditions.invisibilityOf(modalDialog));
```

### 4.5.5 弹出窗口处理工具类

```java
public class DialogHandler {
    private WebDriver driver;
    private WebDriverWait wait;
    
    public DialogHandler(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }
    
    /**
     * 处理JavaScript警告框
     * @param accept 是否接受警告框（true=接受，false=拒绝）
     * @return 警告框文本
     */
    public String handleAlert(boolean accept) {
        Alert alert = wait.until(ExpectedConditions.alertIsPresent());
        String alertText = alert.getText();
        
        if (accept) {
            alert.accept();
        } else {
            alert.dismiss();
        }
        
        return alertText;
    }
    
    /**
     * 处理提示框
     * @param inputText 要输入的文本
     * @param accept 是否接受提示框
     * @return 提示框文本
     */
    public String handlePrompt(String inputText, boolean accept) {
        Alert prompt = wait.until(ExpectedConditions.alertIsPresent());
        String promptText = prompt.getText();
        
        if (inputText != null && !inputText.isEmpty()) {
            prompt.sendKeys(inputText);
        }
        
        if (accept) {
            prompt.accept();
        } else {
            prompt.dismiss();
        }
        
        return promptText;
    }
    
    /**
     * 检查是否有弹出对话框
     * @return 是否有弹出对话框
     */
    public boolean hasDialog() {
        try {
            driver.switchTo().alert();
            return true;
        } catch (NoAlertPresentException e) {
            return false;
        }
    }
    
    /**
     * 等待模态对话框出现或消失
     * @param dialogLocator 对话框定位器
     * @param appearOrDisappear true=等待出现，false=等待消失
     * @return 对话框元素（如果等待出现）
     */
    public WebElement waitForModal(By dialogLocator, boolean appearOrDisappear) {
        if (appearOrDisappear) {
            return wait.until(ExpectedConditions.visibilityOfElementLocated(dialogLocator));
        } else {
            wait.until(ExpectedConditions.invisibilityOfElementLocated(dialogLocator));
            return null;
        }
    }
}
```

## 4.6 浏览器历史与高级导航

### 4.6.1 浏览器历史操作

除了基本的导航方法，还可以进行更复杂的浏览器历史操作：

```java
// 获取浏览器历史信息
JavascriptExecutor js = (JavascriptExecutor) driver;

// 获取历史记录数量
int historyLength = ((Long) js.executeScript("return window.history.length;")).intValue();
System.out.println("浏览器历史记录数量: " + historyLength);

// 使用JavaScript导航到历史记录中的特定位置
js.executeScript("window.history.go(-2);"); // 后退两页
js.executeScript("window.history.go(1);");  // 前进一页

// 检查是否可以前进或后退
Boolean canGoBack = (Boolean) js.executeScript("return window.history.length > 1;");
Boolean canGoForward = (Boolean) js.executeScript("return window.history.length > window.history.state.position;");

System.out.println("可以后退: " + canGoBack);
System.out.println("可以前进: " + canGoForward);
```

### 4.6.2 高级刷新技巧

```java
// 使用JavaScript强制刷新（忽略缓存）
((JavascriptExecutor) driver).executeScript("window.location.reload(true);");

// 智能刷新 - 仅当页面存在错误时刷新
public void smartRefreshIfErrors() {
    JavascriptExecutor js = (JavascriptExecutor) driver;
    
    // 检查页面是否有404或500错误
    Boolean hasErrors = (Boolean) js.executeScript(
        "return document.title.includes('Error') || " +
        "document.body.innerText.includes('404') || " +
        "document.body.innerText.includes('500');");
    
    if (hasErrors) {
        System.out.println("检测到页面错误，执行刷新");
        driver.navigate().refresh();
        
        // 等待页面加载
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        wait.until(ExpectedConditions.presenceOfElementLocated(By.tagName("body")));
    }
}

// 条件性刷新 - 根据URL变化决定是否刷新
public void refreshIfUrlNotChanged(String expectedUrl, int maxAttempts) {
    int attempts = 0;
    while (attempts < maxAttempts) {
        String currentUrl = driver.getCurrentUrl();
        if (currentUrl.contains(expectedUrl)) {
            return; // URL已正确，无需刷新
        }
        
        System.out.println("URL不匹配，执行刷新（尝试: " + (attempts + 1) + "/" + maxAttempts + ")");
        driver.navigate().refresh();
        
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
        attempts++;
    }
    
    Assert.assertTrue(driver.getCurrentUrl().contains(expectedUrl), 
                     "经过 " + maxAttempts + " 次刷新后URL仍不正确");
}
```

### 4.6.3 导航状态监控

```java
// 获取页面加载状态
public String getPageLoadState() {
    return (String) ((JavascriptExecutor) driver).executeScript("return document.readyState;");
}

// 等待页面完全加载
public void waitForPageLoad() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(30));
    wait.until(driver -> {
        String state = ((JavascriptExecutor) driver).executeScript("return document.readyState;").toString();
        return state.equals("complete");
    });
}

// 监控导航性能
public void logNavigationPerformance(String action) {
    JavascriptExecutor js = (JavascriptExecutor) driver;
    
    // 获取性能数据
    Map<String, Object> performance = (Map<String, Object>) js.executeScript(
        "return window.performance ? {" +
        "  navigation: performance.navigation," +
        "  timing: performance.timing" +
        "} : null;");
    
    if (performance != null) {
        Map<String, Object> timing = (Map<String, Object>) performance.get("timing");
        long loadTime = (Long) timing.get("loadEventEnd") - (Long) timing.get("navigationStart");
        System.out.println("导航动作: " + action + ", 加载时间: " + loadTime + "ms");
    }
}
```

## 4.7 高级浏览器配置

### 4.7.1 自定义浏览器选项

```java
// Chrome高级选项
ChromeOptions chromeOptions = new ChromeOptions();

// 无头模式
chromeOptions.addArguments("--headless");

// 禁用GPU（常用于无头模式）
chromeOptions.addArguments("--disable-gpu");

// 禁用沙盒
chromeOptions.addArguments("--no-sandbox");

// 设置窗口大小
chromeOptions.addArguments("--window-size=1920,1080");

// 禁用扩展
chromeOptions.addArguments("--disable-extensions");

// 禁用信息栏
chromeOptions.addArguments("--disable-infobars");

// 禁用密码保存提示
Map<String, Object> prefs = new HashMap<>();
prefs.put("credentials_enable_service", false);
prefs.put("profile.password_manager_enabled", false);
chromeOptions.setExperimentalOption("prefs", prefs);

// 设置下载目录
prefs.put("download.default_directory", "/path/to/downloads");
prefs.put("download.prompt_for_download", false);

// 设置用户代理
chromeOptions.addArguments("--user-agent=CustomUserAgentString");

// 启动Chrome
WebDriver driver = new ChromeDriver(chromeOptions);
```

### 4.7.2 移动端模拟

```java
// Chrome移动设备模拟
Map<String, Object> mobileEmulation = new HashMap<>();
mobileEmulation.put("deviceName", "Pixel 2");
// 或者自定义设备参数
Map<String, Object> deviceMetrics = new HashMap<>();
deviceMetrics.put("width", 411);
deviceMetrics.put("height", 731);
deviceMetrics.put("pixelRatio", 2.6);
deviceMetrics.put("touch", true);
mobileEmulation.put("deviceMetrics", deviceMetrics);
mobileEmulation.put("userAgent", "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Mobile Safari/537.36");

ChromeOptions chromeOptions = new ChromeOptions();
chromeOptions.setExperimentalOption("mobileEmulation", mobileEmulation);

WebDriver driver = new ChromeDriver(chromeOptions);

// 验证移动端视图
boolean isMobile = (Boolean) ((JavascriptExecutor) driver).executeScript(
    "return 'ontouchstart' in window || navigator.maxTouchPoints > 0;");
System.out.println("当前是否为移动设备视图: " + isMobile);
```

### 4.7.3 网络条件模拟

```java
// Chrome网络条件模拟（需要Chrome DevTools Protocol）
ChromeDriver driver = new ChromeDriver();
DevTools devTools = driver.getDevTools();
devTools.createSession();

// 启用网络域
devTools.send(Network.enable(Optional.empty(), Optional.empty(), Optional.empty()));

// 设置网络条件（模拟慢速3G网络）
devTools.send(Network.emulateNetworkConditions(
    false,  // 离线
    2000,   // 下载吞吐量（字节/秒）
    500,    // 上传吞吐量（字节/秒）
    100     // 延迟（毫秒）
));

// 测试慢速网络下的页面加载
long startTime = System.currentTimeMillis();
driver.get("https://example.com");
long loadTime = System.currentTimeMillis() - startTime;
System.out.println("慢速网络下加载时间: " + loadTime + "ms");

// 恢复正常网络条件
devTools.send(Network.emulateNetworkConditions(
    false,  // 离线
    0,      // 下载吞吐量（不限制）
    0,      // 上传吞吐量（不限制）
    0       // 延迟（无延迟）
));

// 关闭DevTools会话
devTools.close();
```

## 4.8 常见问题与解决方案

### 4.8.1 新窗口/标签页切换失败

**问题**：无法切换到新打开的窗口或标签页

**解决方案**：
```java
// 使用显式等待等待新窗口出现
public boolean switchToNewWindowByTitle(String expectedTitle) {
    String originalWindow = driver.getWindowHandle();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    
    try {
        // 等待窗口数量变化
        wait.until(ExpectedConditions.numberOfWindowsToBe(2));
        
        // 遍历所有窗口
        for (String windowHandle : driver.getWindowHandles()) {
            if (!windowHandle.equals(originalWindow)) {
                driver.switchTo().window(windowHandle);
                
                // 等待标题出现
                wait.until(ExpectedConditions.titleContains(expectedTitle));
                return true;
            }
        }
    } catch (TimeoutException e) {
        driver.switchTo().window(originalWindow);
        return false;
    }
    
    return false;
}
```

### 4.8.2 文件上传/下载失败

**问题**：文件上传或下载操作不成功

**解决方案**：
```java
// 文件上传前验证元素
public boolean uploadFile(String filePath) {
    try {
        WebElement fileInput = driver.findElement(By.cssSelector("input[type='file']"));
        
        // 确保元素可见且可用
        if (!fileInput.isDisplayed()) {
            // 尝试使元素可见
            ((JavascriptExecutor) driver).executeScript("arguments[0].style.display = 'block';", fileInput);
        }
        
        // 验证文件路径
        File file = new File(filePath);
        if (!file.exists()) {
            throw new RuntimeException("文件不存在: " + filePath);
        }
        
        // 上传文件
        fileInput.sendKeys(file.getAbsolutePath());
        
        // 等待上传完成（根据实际页面情况调整）
        Thread.sleep(2000);
        
        return true;
    } catch (Exception e) {
        System.err.println("文件上传失败: " + e.getMessage());
        return false;
    }
}

// 文件下载验证
public File waitForFileDownload(String fileName, int timeoutSeconds) {
    String downloadDir = getConfigProperty("download.directory", "downloads");
    long endTime = System.currentTimeMillis() + (timeoutSeconds * 1000);
    
    while (System.currentTimeMillis() < endTime) {
        File dir = new File(downloadDir);
        File[] files = dir.listFiles();
        
        if (files != null) {
            for (File file : files) {
                if (file.getName().contains(fileName) && 
                    !file.getName().endsWith(".tmp") && 
                    !file.getName().endsWith(".crdownload")) {
                    return file;
                }
            }
        }
        
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
    }
    
    throw new RuntimeException("文件下载超时: " + fileName);
}
```

### 4.8.3 弹出框处理失败

**问题**：无法识别或处理弹出对话框

**解决方案**：
```java
// 处理多种类型的弹出框
public boolean handleAnyDialog() {
    try {
        // 首先尝试处理JavaScript原生对话框
        if (hasAlert()) {
            Alert alert = driver.switchTo().alert();
            String alertText = alert.getText();
            System.out.println("发现JavaScript警告框: " + alertText);
            alert.accept();
            return true;
        }
        
        // 然后尝试查找模态对话框
        List<WebElement> modals = driver.findElements(By.cssSelector(".modal, .dialog, .popup"));
        for (WebElement modal : modals) {
            if (modal.isDisplayed()) {
                System.out.println("发现模态对话框: " + modal.getText());
                
                // 尝试找到关闭按钮
                List<WebElement> closeButtons = modal.findElements(By.cssSelector(".close, .modal-close, [data-dismiss='modal']"));
                if (!closeButtons.isEmpty()) {
                    closeButtons.get(0).click();
                    return true;
                }
            }
        }
        
        return false;
    } catch (Exception e) {
        System.err.println("处理对话框时出错: " + e.getMessage());
        return false;
    }
}

// 检查是否有JavaScript警告框
private boolean hasAlert() {
    try {
        driver.switchTo().alert();
        return true;
    } catch (NoAlertPresentException e) {
        return false;
    }
}
```

## 4.9 最佳实践

### 4.9.1 窗口和Frame管理最佳实践

1. **使用WindowManager工具类**：封装窗口操作，提高代码复用性
2. **明确切换策略**：总是明确知道当前在哪个窗口/frame中
3. **及时返回主文档**：完成frame操作后及时返回主文档
4. **使用显式等待**：等待窗口/frame加载完成，避免时间等待
5. **异常处理**：适当处理窗口切换失败的情况

```java
// 好的实践示例
public void handleWindowOperation() {
    WindowManager windowManager = new WindowManager(driver);
    String mainWindow = driver.getWindowHandle();
    
    try {
        // 执行会打开新窗口的操作
        driver.findElement(By.id("open-new-window")).click();
        
        // 切换到新窗口
        String newWindow = windowManager.switchToNewWindow();
        
        // 在新窗口中执行操作
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.id("button-in-new-window")));
        element.click();
        
        // 关闭新窗口并返回
        driver.close();
        windowManager.switchToOriginalWindow();
        
    } catch (Exception e) {
        // 确保在出错时也返回主窗口
        windowManager.closeAllOtherWindows();
        throw new RuntimeException("窗口操作失败", e);
    }
}
```

### 4.9.2 文件操作最佳实践

1. **使用相对路径**：提高脚本可移植性
2. **清理下载目录**：测试前清理，避免旧文件干扰
3. **验证上传/下载**：确认操作成功
4. **异常处理**：处理文件不存在、权限不足等问题
5. **配置下载目录**：集中管理下载文件，便于验证和清理

```java
// 好的实践示例
public void handleFileOperation() {
    DownloadHelper downloadHelper = new DownloadHelper(getConfigProperty("download.directory"));
    
    try {
        // 清理下载目录
        downloadHelper.cleanupDownloads();
        
        // 执行文件上传
        String filePath = "test-files/sample.pdf";
        WebElement fileInput = driver.findElement(By.id("file-input"));
        fileInput.sendKeys(new File(filePath).getAbsolutePath());
        
        // 验证上传
        WebElement uploadStatus = new WebDriverWait(driver, Duration.ofSeconds(10))
            .until(ExpectedConditions.visibilityOfElementLocated(By.id("upload-status")));
        Assert.assertTrue(uploadStatus.getText().contains("上传成功"));
        
        // 执行下载
        driver.findElement(By.id("download-button")).click();
        
        // 等待下载完成
        File downloadedFile = downloadHelper.waitForDownload("downloaded-sample.pdf", 30);
        Assert.assertNotNull(downloadedFile, "文件下载失败");
        Assert.assertTrue(downloadedFile.length() > 0, "下载的文件为空");
        
    } finally {
        // 测试后清理
        downloadHelper.cleanupDownloads();
    }
}
```

## 4.10 章节总结

本章深入讲解了Selenium中的高级操作和窗口管理技术，包括多窗口管理、Frame处理、文件上传下载、浏览器控制台操作、弹出窗口处理和高级导航等。通过学习这些高级技巧，您现在应该能够应对复杂的Web应用自动化测试场景。

### 关键要点回顾

1. **多窗口管理**：窗口句柄获取与切换、窗口操作封装
2. **Frame处理**：frame切换、嵌套frame处理、动态frame
3. **文件操作**：文件上传与下载配置及验证
4. **控制台操作**：获取浏览器日志、执行JavaScript命令、性能监控
5. **弹出窗口处理**：JavaScript原生对话框和模态对话框的处理
6. **高级导航**：浏览器历史操作、智能刷新、导航状态监控
7. **浏览器配置**：自定义选项、移动端模拟、网络条件模拟

### 下一步学习

在下一章中，我们将学习Selenium测试框架设计与Page Object模式，这是构建可维护、可扩展的自动化测试框架的关键技术。我们将学习如何设计优雅的测试架构、实现Page Object模式、设计测试基类和工具类，以及如何组织和管理测试数据。

## 4.11 实践练习

1. **多窗口操作**：设计一个测试，在一个页面打开多个新窗口，并在各个窗口之间切换操作
2. **嵌套Frame处理**：访问一个包含多层嵌套frame的页面，在不同层级的frame中操作元素
3. **文件上传下载**：实现一个完整的文件上传和下载流程，包括验证文件内容
4. **控制台操作**：使用JavaScript获取页面性能数据，并分析页面加载瓶颈
5. **弹窗处理**：处理一个包含多种弹出窗口（警告框、确认框、模态框）的复杂页面

请完成以上练习，并思考：
- 如何提高多窗口和frame操作的稳定性？
- 在什么情况下应该使用文件上传下载的替代方案？
- 如何处理不同浏览器之间在窗口和frame处理上的差异？

通过思考这些问题，您将更深入地理解Selenium高级操作的最佳实践和技巧。