# 第6章：Selenium等待机制与异常处理

## 📖 章节介绍

本章将深入探讨Selenium中的等待机制和异常处理策略。在Web应用自动化测试中，等待机制是确保测试稳定性的关键，而合理的异常处理则是保证测试可靠性的重要手段。通过本章的学习，您将掌握各种等待策略的适用场景，学会分类处理不同类型的异常，并能够设计出更加健壮和稳定的自动化测试脚本。

## 🎯 学习目标

- 理解不同类型的等待机制及其适用场景
- 掌握显式等待的高级用法和自定义等待条件
- 学会合理处理常见的Selenium异常
- 了解异常分类和恢复策略
- 掌握超时和超时处理的设计原则
- 学会设计健壮的自动化测试脚本

## 6.1 Selenium等待机制概述

### 6.1.1 为什么需要等待机制

Web应用具有动态性和异步性，元素可能不会立即可用：

1. **页面加载时间**：页面内容需要时间从服务器加载
2. **JavaScript执行**：客户端脚本可能需要时间处理和渲染
3. **AJAX请求**：异步请求完成后才会更新页面内容
4. **动画效果**：CSS动画和过渡效果需要时间完成
5. **延迟加载**：页面可能采用延迟加载策略，内容在特定条件下才加载

### 6.1.2 等待机制的分类

Selenium提供了三种主要的等待机制：

1. **隐式等待（Implicit Wait）**：
   - 设置全局等待时间，作用于整个WebDriver生命周期
   - 在查找元素时，如果元素不存在，会等待指定时间后再抛出异常

2. **显式等待（Explicit Wait）**：
   - 针对特定元素或条件的等待
   - 可以设置更灵活的等待条件和超时时间
   - 是推荐使用的等待方式

3. **线程等待（Thread Sleep）**：
   - 强制暂停脚本执行指定时间
   - 不推荐使用，因为不灵活且可能导致不必要的等待

### 6.1.3 等待机制性能比较

```java
// 1. 隐式等待示例
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
WebElement element = driver.findElement(By.id("dynamic-element")); // 最多等待10秒

// 2. 显式等待示例
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("dynamic-element")));

// 3. 线程等待示例
Thread.sleep(5000); // 强制等待5秒，不管元素是否已经出现
WebElement element = driver.findElement(By.id("dynamic-element"));
```

**性能比较**：
- **隐式等待**：简单易用，但不够灵活，可能导致不必要的等待
- **显式等待**：灵活可控，性能更好，是最佳实践
- **线程等待**：最不推荐，不考虑页面实际状态，导致测试执行缓慢

## 6.2 隐式等待详解

### 6.2.1 隐式等待的工作原理

隐式告诉WebDriver在查找元素时，如果元素不存在，应该等待一段时间再抛出NoSuchElementException。

```java
// 设置隐式等待时间为10秒
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));

// 查找元素时，如果元素不存在，会每隔500毫秒重试一次，最多等待10秒
WebElement element = driver.findElement(By.id("element-id"));
```

### 6.2.2 隐式等待的设置与取消

```java
// 设置隐式等待
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));

// 取消隐式等待
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(0));

// 临时修改隐式等待
Duration originalWait = driver.manage().timeouts().getImplicitWaitTimeout();
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(20));
// 执行需要更长等待的操作
driver.manage().timeouts().implicitlyWait(originalWait); // 恢复原始设置
```

### 6.2.3 隐式等待的最佳实践

```java
// 好的实践：在测试初始化时设置一次隐式等待
public class BaseTest {
    @BeforeClass
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        
        // 设置合理的隐式等待时间（通常5-10秒）
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(5));
        
        // 设置页面加载超时
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
    }
    
    @Test
    public void testExample() {
        // 不需要为每个元素单独设置等待
        driver.get("https://example.com");
        
        // 隐式等待会自动应用于元素查找
        WebElement element = driver.findElement(By.id("some-element"));
        element.click();
    }
}
```

## 6.3 显式等待详解

### 6.3.1 显式等待的基本用法

显式等待是更灵活和推荐的等待方式，可以针对特定条件进行等待：

```java
// 创建显式等待对象，最长等待10秒
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

// 等待元素可见
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("dynamic-element")));

// 等待元素可点击
WebElement button = wait.until(ExpectedConditions.elementToBeClickable(By.id("submit-button")));

// 等待元素存在（不一定可见）
WebElement input = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("input-field")));
```

### 6.3.2 ExpectedConditions常用方法

Selenium提供了丰富的ExpectedConditions类，包含各种常用等待条件：

#### 元素存在性条件
```java
// 等待元素存在（不一定可见）
WebElement element = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("element-id")));

// 等待所有元素存在
List<WebElement> elements = wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.className("item")));

// 等待元素可见
WebElement visibleElement = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("visible-element")));

// 等待所有元素可见
List<WebElement> visibleElements = wait.until(ExpectedConditions.visibilityOfAllElementsLocatedBy(By.className("visible-item")));

// 等待元素不可见
wait.until(ExpectedConditions.invisibilityOfElementLocated(By.id("loading-spinner")));
```

#### 元素交互条件
```java
// 等待元素可点击
WebElement clickableElement = wait.until(ExpectedConditions.elementToBeClickable(By.id("button-id")));

// 等待元素被选中
WebElement selectedOption = wait.until(ExpectedConditions.elementToBeSelected(By.id("option-id")));

// 等待选择框包含特定值
wait.until(ExpectedConditions.textToBePresentInElementLocated(By.id("dropdown"), "Expected Value"));
```

#### 页面和URL条件
```java
// 等待标题包含特定文本
wait.until(ExpectedConditions.titleContains("Dashboard"));

// 等待标题完全匹配
wait.until(ExpectedConditions.titleIs("Dashboard - Home"));

// 等待URL包含特定文本
wait.until(ExpectedConditions.urlContains("/dashboard"));

// 等待URL完全匹配
wait.until(ExpectedConditions.urlToBe("https://example.com/dashboard"));

// 等待URL包含特定正则表达式
wait.until(ExpectedConditions.urlMatches(".*\\.com/.*"));
```

#### JavaScript条件
```java
// 等待JavaScript执行返回true
Boolean result = wait.until(ExpectedConditions.jsReturnsValue("return document.readyState === 'complete'"));

// 等待JavaScript执行返回特定值
String result = (String) wait.until(ExpectedConditions.jsReturnsValue("return document.title"));
```

### 6.3.3 FluentWait高级用法

FluentWait是显式等待的更高级形式，提供更细粒度的控制：

```java
// 创建FluentWait，自定义轮询间隔和忽略的异常
Wait<WebDriver> fluentWait = new FluentWait<WebDriver>(driver)
    .withTimeout(Duration.ofSeconds(30))                    // 最长等待时间
    .pollingEvery(Duration.ofMillis(500))                 // 轮询间隔
    .ignoring(NoSuchElementException.class)               // 忽略的异常类型
    .ignoring(StaleElementReferenceException.class)
    .withMessage("等待元素超时");                        // 超时消息

// 使用FluentWait等待元素
WebElement element = fluentWait.until(new Function<WebDriver, WebElement>() {
    public WebElement apply(WebDriver driver) {
        return driver.findElement(By.id("dynamic-element"));
    }
});
```

### 6.3.4 自定义等待条件

当内置的ExpectedConditions不满足需求时，可以创建自定义等待条件：

```java
// 自定义等待条件接口实现
public class CustomExpectedConditions {
    
    // 等待元素属性包含特定值
    public static ExpectedCondition<Boolean> attributeContains(By locator, String attributeName, String value) {
        return new ExpectedCondition<Boolean>() {
            @Override
            public Boolean apply(WebDriver driver) {
                try {
                    WebElement element = driver.findElement(locator);
                    String attrValue = element.getAttribute(attributeName);
                    return attrValue != null && attrValue.contains(value);
                } catch (Exception e) {
                    return false;
                }
            }
            
            @Override
            public String toString() {
                return String.format("元素 %s 的属性 %s 包含值 %s", locator, attributeName, value);
            }
        };
    }
    
    // 等待元素数量大于指定值
    public static ExpectedCondition<Boolean> elementCountGreaterThan(By locator, int count) {
        return new ExpectedCondition<Boolean>() {
            @Override
            public Boolean apply(WebDriver driver) {
                try {
                    List<WebElement> elements = driver.findElements(locator);
                    return elements.size() > count;
                } catch (Exception e) {
                    return false;
                }
            }
            
            @Override
            public String toString() {
                return String.format("元素 %s 的数量大于 %d", locator, count);
            }
        };
    }
    
    // 等待元素文本长度大于指定值
    public static ExpectedCondition<Boolean> elementTextLengthGreaterThan(By locator, int length) {
        return new ExpectedCondition<Boolean>() {
            @Override
            public Boolean apply(WebDriver driver) {
                try {
                    WebElement element = driver.findElement(locator);
                    return element.getText().length() > length;
                } catch (Exception e) {
                    return false;
                }
            }
            
            @Override
            public String toString() {
                return String.format("元素 %s 的文本长度大于 %d", locator, length);
            }
        };
    }
    
    // 等待AJAX请求完成（基于jQuery）
    public static ExpectedCondition<Boolean> ajaxRequestCompleted() {
        return new ExpectedCondition<Boolean>() {
            @Override
            public Boolean apply(WebDriver driver) {
                try {
                    JavascriptExecutor js = (JavascriptExecutor) driver;
                    return (Boolean) js.executeScript("return jQuery.active == 0");
                } catch (Exception e) {
                    // 页面可能没有jQuery
                    return true;
                }
            }
            
            @Override
            public String toString() {
                return "AJAX请求完成";
            }
        };
    }
    
    // 等待页面加载完成
    public static ExpectedCondition<Boolean> pageLoadComplete() {
        return new ExpectedCondition<Boolean>() {
            @Override
            public Boolean apply(WebDriver driver) {
                try {
                    JavascriptExecutor js = (JavascriptExecutor) driver;
                    return js.executeScript("return document.readyState").equals("complete");
                } catch (Exception e) {
                    return false;
                }
            }
            
            @Override
            public String toString() {
                return "页面加载完成";
            }
        };
    }
}

// 使用自定义等待条件
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

// 等待元素属性包含特定值
wait.until(CustomExpectedConditions.attributeContains(By.id("status"), "class", "active"));

// 等待元素数量大于指定值
wait.until(CustomExpectedConditions.elementCountGreaterThan(By.className("list-item"), 5));

// 等待AJAX请求完成
wait.until(CustomExpectedConditions.ajaxRequestCompleted());
```

## 6.4 常见Selenium异常

### 6.4.1 异常分类与处理策略

Selenium异常可以分为以下几类：

#### 元素定位异常
1. **NoSuchElementException**：找不到指定元素
2. **NoSuchFrameException**：找不到指定的frame
3. **NoAlertPresentException**：没有弹出的警告框
4. **NoSuchWindowException**：找不到指定的窗口

#### 元素状态异常
1. **ElementNotVisibleException**：元素存在但不可见
2. **ElementNotInteractableException**：元素可见但不可交互
3. **StaleElementReferenceException**：元素引用已过期（元素已被修改或删除）
4. **ElementClickInterceptedException**：点击操作被其他元素拦截

#### 超时异常
1. **TimeoutException**：操作超时
2. **ScriptTimeoutException**：JavaScript执行超时
3. **PageLoadTimeoutException**：页面加载超时

#### 浏览器和驱动异常
1. **InvalidElementStateException**：元素状态无效
2. **InvalidSelectorException**：选择器无效
3. **MoveTargetOutOfBoundsException**：移动目标超出边界
4. **WebDriverException**：通用的WebDriver异常

#### 会话异常
1. **SessionNotCreatedException**：无法创建会话
2. **NoSuchSessionException**：会话不存在
3. **SessionNotCreatedException**：会话未创建

### 6.4.2 异常处理最佳实践

```java
// 1. 元素定位异常处理
public WebElement safeFindElement(By locator, int maxAttempts) {
    int attempts = 0;
    while (attempts < maxAttempts) {
        try {
            return driver.findElement(locator);
        } catch (NoSuchElementException e) {
            attempts++;
            if (attempts >= maxAttempts) {
                throw new NoSuchElementException("经过 " + maxAttempts + " 次尝试仍找不到元素: " + locator, e);
            }
            
            // 等待一段时间后重试
            try {
                Thread.sleep(1000);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("等待被中断", ie);
            }
            
            // 尝试刷新页面
            if (attempts == maxAttempts / 2) {
                driver.navigate().refresh();
            }
        }
    }
    throw new NoSuchElementException("无法找到元素: " + locator);
}

// 2. 元素状态异常处理
public void safeClick(By locator, int maxAttempts) {
    int attempts = 0;
    while (attempts < maxAttempts) {
        try {
            WebElement element = driver.findElement(locator);
            
            // 检查元素是否可见和可点击
            if (element.isDisplayed() && element.isEnabled()) {
                element.click();
                return;
            } else {
                // 元素不可见或不可点击，尝试滚动到元素
                ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(true);", element);
                element.click();
                return;
            }
        } catch (ElementClickInterceptedException e) {
            // 点击被拦截，尝试使用JavaScript点击
            try {
                WebElement element = driver.findElement(locator);
                ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
                return;
            } catch (Exception jsException) {
                // JavaScript点击也失败，继续尝试
            }
        } catch (ElementNotInteractableException e) {
            // 元素不可交互，等待一段时间后重试
        } catch (StaleElementReferenceException e) {
            // 元素引用过期，下次循环会重新查找元素
        } catch (NoSuchElementException e) {
            // 元素不存在，下次循环会继续尝试
        }
        
        attempts++;
        try {
            Thread.sleep(1000);
        } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("等待被中断", ie);
        }
    }
    
    throw new RuntimeException("无法点击元素，已尝试 " + maxAttempts + " 次: " + locator);
}

// 3. 超时异常处理
public <T> T waitWithRetry(ExpectedCondition<T> condition, Duration timeout, int maxRetries) {
    int attempts = 0;
    while (attempts < maxRetries) {
        try {
            WebDriverWait wait = new WebDriverWait(driver, timeout);
            return wait.until(condition);
        } catch (TimeoutException e) {
            attempts++;
            if (attempts >= maxRetries) {
                throw new TimeoutException("经过 " + maxRetries + " 次重试后等待条件仍不满足: " + condition, e);
            }
            
            // 尝试刷新页面或执行其他恢复操作
            driver.navigate().refresh();
        }
    }
    
    throw new TimeoutException("等待条件未满足: " + condition);
}
```

## 6.5 异常恢复策略

### 6.5.1 异常恢复的通用原则

1. **识别异常类型**：区分临时性异常和永久性异常
2. **设置重试次数**：避免无限重试
3. **增加等待时间**：在重试之间增加适当的等待
4. **记录异常信息**：提供详细的错误日志
5. **优雅降级**：在无法恢复时提供替代方案

### 6.5.2 实用的异常恢复工具类

```java
// ExceptionRecovery.java - 异常恢复工具类
public class ExceptionRecovery {
    private WebDriver driver;
    
    public ExceptionRecovery(WebDriver driver) {
        this.driver = driver;
    }
    
    /**
     * 带重试的元素查找
     * @param locator 元素定位器
     * @param maxAttempts 最大尝试次数
     * @param waitBetweenAttempts 尝试之间的等待时间
     * @return 找到的元素
     */
    public WebElement findElementWithRetry(By locator, int maxAttempts, Duration waitBetweenAttempts) {
        int attempts = 0;
        while (attempts < maxAttempts) {
            try {
                return driver.findElement(locator);
            } catch (NoSuchElementException e) {
                attempts++;
                if (attempts >= maxAttempts) {
                    throw new NoSuchElementException("无法找到元素: " + locator + ", 已尝试 " + maxAttempts + " 次", e);
                }
                
                // 记录重试信息
                System.out.println("元素查找失败，重试中 (" + attempts + "/" + maxAttempts + "): " + locator);
                
                try {
                    Thread.sleep(waitBetweenAttempts.toMillis());
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("等待被中断", ie);
                }
                
                // 尝试刷新页面（在中间尝试时）
                if (attempts == maxAttempts / 2) {
                    System.out.println("尝试刷新页面以重新加载元素");
                    driver.navigate().refresh();
                }
            }
        }
        
        throw new NoSuchElementException("无法找到元素: " + locator);
    }
    
    /**
     * 带重试的元素点击
     * @param locator 元素定位器
     * @param maxAttempts 最大尝试次数
     * @param waitBetweenAttempts 尝试之间的等待时间
     */
    public void clickWithRetry(By locator, int maxAttempts, Duration waitBetweenAttempts) {
        int attempts = 0;
        while (attempts < maxAttempts) {
            try {
                WebElement element = driver.findElement(locator);
                
                // 尝试常规点击
                if (element.isDisplayed() && element.isEnabled()) {
                    element.click();
                    return;
                }
                
                // 尝试滚动到元素并点击
                ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView({block: 'center'});", element);
                element.click();
                return;
                
            } catch (ElementClickInterceptedException e) {
                // 点击被拦截，尝试使用JavaScript点击
                try {
                    WebElement element = driver.findElement(locator);
                    ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
                    System.out.println("使用JavaScript成功点击元素: " + locator);
                    return;
                } catch (Exception jsException) {
                    System.out.println("JavaScript点击也失败: " + jsException.getMessage());
                }
            } catch (StaleElementReferenceException e) {
                System.out.println("元素引用过期，重新查找: " + locator);
            } catch (ElementNotInteractableException e) {
                System.out.println("元素不可交互: " + locator);
            } catch (NoSuchElementException e) {
                System.out.println("元素不存在: " + locator);
            } catch (Exception e) {
                System.out.println("点击元素时发生未知异常: " + e.getMessage());
            }
            
            attempts++;
            if (attempts >= maxAttempts) {
                throw new RuntimeException("无法点击元素: " + locator + ", 已尝试 " + maxAttempts + " 次");
            }
            
            System.out.println("点击元素失败，重试中 (" + attempts + "/" + maxAttempts + "): " + locator);
            
            try {
                Thread.sleep(waitBetweenAttempts.toMillis());
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("等待被中断", ie);
            }
        }
    }
    
    /**
     * 带重试的文本输入
     * @param locator 输入框定位器
     * @param text 要输入的文本
     * @param maxAttempts 最大尝试次数
     * @param waitBetweenAttempts 尝试之间的等待时间
     */
    public void typeWithRetry(By locator, String text, int maxAttempts, Duration waitBetweenAttempts) {
        int attempts = 0;
        while (attempts < maxAttempts) {
            try {
                WebElement element = driver.findElement(locator);
                
                if (element.isDisplayed() && element.isEnabled()) {
                    element.clear();
                    element.sendKeys(text);
                    
                    // 验证输入是否成功
                    String actualValue = element.getAttribute("value");
                    if (actualValue.equals(text)) {
                        return;
                    } else {
                        System.out.println("输入验证失败，期望: " + text + ", 实际: " + actualValue);
                    }
                }
                
            } catch (StaleElementReferenceException e) {
                System.out.println("元素引用过期，重新查找: " + locator);
            } catch (ElementNotInteractableException e) {
                System.out.println("元素不可交互: " + locator);
            } catch (NoSuchElementException e) {
                System.out.println("元素不存在: " + locator);
            } catch (Exception e) {
                System.out.println("输入文本时发生未知异常: " + e.getMessage());
            }
            
            attempts++;
            if (attempts >= maxAttempts) {
                throw new RuntimeException("无法输入文本: " + text + " 到元素: " + locator + ", 已尝试 " + maxAttempts + " 次");
            }
            
            System.out.println("输入文本失败，重试中 (" + attempts + "/" + maxAttempts + "): " + locator);
            
            try {
                Thread.sleep(waitBetweenAttempts.toMillis());
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("等待被中断", ie);
            }
        }
    }
    
    /**
     * 等待页面加载完成
     * @param timeout 超时时间
     * @return 是否加载完成
     */
    public boolean waitForPageLoadComplete(Duration timeout) {
        long endTime = System.currentTimeMillis() + timeout.toMillis();
        
        while (System.currentTimeMillis() < endTime) {
            try {
                JavascriptExecutor js = (JavascriptExecutor) driver;
                String readyState = (String) js.executeScript("return document.readyState");
                if ("complete".equals(readyState)) {
                    return true;
                }
                
                // 检查jQuery AJAX请求（如果页面使用jQuery）
                Boolean ajaxComplete = (Boolean) js.executeScript("return typeof jQuery !== 'undefined' && jQuery.active === 0");
                if (ajaxComplete != null && ajaxComplete) {
                    return true;
                }
            } catch (Exception e) {
                // 继续等待
            }
            
            try {
                Thread.sleep(500);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        
        return false;
    }
    
    /**
     * 处理意外弹窗
     */
    public void handleUnexpectedAlerts() {
        try {
            driver.switchTo().alert().accept();
            System.out.println("发现意外弹窗，已接受");
        } catch (NoAlertPresentException e) {
            // 没有弹窗，正常情况
        } catch (Exception e) {
            System.out.println("处理弹窗时出错: " + e.getMessage());
        }
    }
    
    /**
     * 恢复到基础状态
     */
    public void recoverToBaseState(String baseUrl) {
        try {
            // 处理可能的弹窗
            handleUnexpectedAlerts();
            
            // 切换到主文档
            driver.switchTo().defaultContent();
            
            // 切换到主窗口
            String currentWindow = driver.getWindowHandle();
            for (String window : driver.getWindowHandles()) {
                if (!window.equals(currentWindow)) {
                    driver.switchTo().window(window);
                    driver.close();
                }
            }
            driver.switchTo().window(currentWindow);
            
            // 导航到基础URL
            driver.get(baseUrl);
            
            // 等待页面加载完成
            waitForPageLoadComplete(Duration.ofSeconds(10));
            
        } catch (Exception e) {
            System.out.println("恢复到基础状态时出错: " + e.getMessage());
            // 最后的尝试：重启浏览器
            try {
                driver.quit();
                // 这里需要重新初始化driver，但具体实现取决于框架设计
            } catch (Exception restartException) {
                System.out.println("重启浏览器时出错: " + restartException.getMessage());
            }
        }
    }
}
```

## 6.6 超时处理策略

### 6.6.1 超时类型与设置

Selenium支持多种超时设置：

```java
// 隐式等待超时
driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));

// 页面加载超时
driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));

// 脚本执行超时
driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(20));

// 显式等待超时（在创建WebDriverWait时设置）
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
```

### 6.6.2 超时处理最佳实践

```java
// TimeoutManager.java - 超时管理工具类
public class TimeoutManager {
    private WebDriver driver;
    private Duration defaultImplicitWait;
    private Duration defaultPageLoadTimeout;
    private Duration defaultScriptTimeout;
    private Duration defaultExplicitWait;
    
    public TimeoutManager(WebDriver driver) {
        this.driver = driver;
        // 保存默认超时设置
        this.defaultImplicitWait = driver.manage().timeouts().getImplicitWaitTimeout();
        this.defaultPageLoadTimeout = driver.manage().timeouts().getPageLoadTimeout();
        this.defaultScriptTimeout = driver.manage().timeouts().getScriptTimeout();
        this.defaultExplicitWait = Duration.ofSeconds(10);
    }
    
    /**
     * 设置长时间操作的超时
     */
    public void setLongOperationTimeout() {
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(0));  // 禁用隐式等待
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(60));  // 增加页面加载超时
        driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(30));   // 增加脚本执行超时
    }
    
    /**
     * 设置快速操作的超时
     */
    public void setQuickOperationTimeout() {
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(2));   // 减少隐式等待
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(10)); // 减少页面加载超时
        driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(5));    // 减少脚本执行超时
    }
    
    /**
     * 恢复默认超时设置
     */
    public void restoreDefaultTimeouts() {
        driver.manage().timeouts().implicitlyWait(defaultImplicitWait);
        driver.manage().timeouts().pageLoadTimeout(defaultPageLoadTimeout);
        driver.manage().timeouts().scriptTimeout(defaultScriptTimeout);
    }
    
    /**
     * 临时设置超时并执行操作
     */
    public <T> T withTimeouts(Duration implicitWait, Duration pageLoadTimeout, 
                               Duration scriptTimeout, Supplier<T> operation) {
        try {
            // 设置临时超时
            driver.manage().timeouts().implicitlyWait(implicitWait);
            driver.manage().timeouts().pageLoadTimeout(pageLoadTimeout);
            driver.manage().timeouts().scriptTimeout(scriptTimeout);
            
            // 执行操作
            return operation.get();
            
        } finally {
            // 恢复默认超时
            restoreDefaultTimeouts();
        }
    }
    
    /**
     * 等待条件并处理超时
     */
    public <T> T waitForCondition(ExpectedCondition<T> condition, Duration timeout, 
                                   String timeoutMessage) {
        try {
            WebDriverWait wait = new WebDriverWait(driver, timeout);
            return wait.until(condition);
        } catch (TimeoutException e) {
            throw new TimeoutException(timeoutMessage, e);
        }
    }
    
    /**
     * 带重试的等待条件
     */
    public <T> T waitForConditionWithRetry(ExpectedCondition<T> condition, Duration timeout, 
                                            int maxRetries, Duration retryInterval) {
        int attempts = 0;
        Exception lastException = null;
        
        while (attempts <= maxRetries) {
            try {
                WebDriverWait wait = new WebDriverWait(driver, timeout);
                return wait.until(condition);
            } catch (TimeoutException e) {
                lastException = e;
                attempts++;
                
                if (attempts > maxRetries) {
                    break;
                }
                
                System.out.println("等待条件超时，重试中 (" + attempts + "/" + maxRetries + "): " + condition);
                
                try {
                    Thread.sleep(retryInterval.toMillis());
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("等待被中断", ie);
                }
                
                // 尝试刷新页面（在中间尝试时）
                if (attempts == maxRetries / 2) {
                    driver.navigate().refresh();
                }
            }
        }
        
        throw new TimeoutException("等待条件不满足，已重试 " + maxRetries + " 次: " + condition, lastException);
    }
}
```

## 6.7 健壮测试设计

### 6.7.1 健壮测试设计原则

1. **预期明确**：明确每个步骤的预期结果
2. **异常处理**：处理所有可能的异常情况
3. **状态恢复**：测试失败后能够恢复到已知状态
4. **资源清理**：确保测试完成后释放所有资源
5. **日志记录**：记录详细的测试执行信息

### 6.7.2 健壮的页面对象设计

```java
// RobustBasePage.java - 健壮的基础页面对象
public abstract class RobustBasePage {
    protected WebDriver driver;
    protected WebDriverWait wait;
    protected TimeoutManager timeoutManager;
    protected ExceptionRecovery exceptionRecovery;
    
    public RobustBasePage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        this.timeoutManager = new TimeoutManager(driver);
        this.exceptionRecovery = new ExceptionRecovery(driver);
        PageFactory.initElements(driver, this);
    }
    
    /**
     * 安全地点击元素
     */
    protected void safeClick(By locator) {
        exceptionRecovery.clickWithRetry(locator, 3, Duration.ofSeconds(1));
    }
    
    /**
     * 安全地输入文本
     */
    protected void safeType(By locator, String text) {
        exceptionRecovery.typeWithRetry(locator, text, 3, Duration.ofSeconds(1));
    }
    
    /**
     * 安全地查找元素
     */
    protected WebElement safeFindElement(By locator) {
        return exceptionRecovery.findElementWithRetry(locator, 3, Duration.ofSeconds(1));
    }
    
    /**
     * 等待元素可见
     */
    protected WebElement waitForElementVisible(By locator) {
        return timeoutManager.waitForCondition(
            ExpectedConditions.visibilityOfElementLocated(locator),
            Duration.ofSeconds(10),
            "元素未可见: " + locator
        );
    }
    
    /**
     * 等待元素可点击
     */
    protected WebElement waitForElementClickable(By locator) {
        return timeoutManager.waitForCondition(
            ExpectedConditions.elementToBeClickable(locator),
            Duration.ofSeconds(10),
            "元素不可点击: " + locator
        );
    }
    
    /**
     * 导航到页面URL
     */
    public void navigateTo(String url) {
        timeoutManager.withTimeouts(
            Duration.ofSeconds(0),  // 禁用隐式等待
            Duration.ofSeconds(30), // 页面加载超时
            Duration.ofSeconds(15), // 脚本执行超时
            () -> {
                driver.get(url);
                return true;
            }
        );
        
        // 等待页面加载完成
        boolean loaded = exceptionRecovery.waitForPageLoadComplete(Duration.ofSeconds(15));
        if (!loaded) {
            throw new RuntimeException("页面加载超时: " + url);
        }
    }
    
    /**
     * 验证当前页面
     */
    public abstract boolean isCorrectPage();
    
    /**
     * 获取页面URL
     */
    public String getCurrentUrl() {
        return driver.getCurrentUrl();
    }
    
    /**
     * 获取页面标题
     */
    public String getPageTitle() {
        return driver.getTitle();
    }
    
    /**
     * 截图
     */
    public String takeScreenshot(String testName) {
        try {
            String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss").format(new Date());
            String fileName = testName + "_" + timestamp + ".png";
            String filePath = "screenshots/" + fileName;
            
            // 确保目录存在
            new File("screenshots").mkdirs();
            
            // 截图
            File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            FileUtils.copyFile(screenshot, new File(filePath));
            
            return filePath;
        } catch (IOException e) {
            throw new RuntimeException("截图失败", e);
        }
    }
    
    /**
     * 滚动到元素
     */
    protected void scrollToElement(WebElement element) {
        ((JavascriptExecutor) driver).executeScript(
            "arguments[0].scrollIntoView({block: 'center'});", element);
    }
    
    /**
     * 等待并处理加载指示器消失
     */
    protected void waitForLoadingComplete() {
        By loadingIndicators[] = {
            By.cssSelector(".loading"),
            By.cssSelector(".spinner"),
            By.cssSelector(".loader"),
            By.id("loading"),
            By.id("spinner")
        };
        
        for (By indicator : loadingIndicators) {
            try {
                // 等待加载指示器出现和消失
                timeoutManager.waitForCondition(
                    ExpectedConditions.visibilityOfElementLocated(indicator),
                    Duration.ofSeconds(2),
                    "加载指示器未出现: " + indicator
                );
                
                // 等待加载指示器消失
                timeoutManager.waitForCondition(
                    ExpectedConditions.invisibilityOfElementLocated(indicator),
                    Duration.ofSeconds(30),
                    "加载指示器未消失: " + indicator
                );
            } catch (TimeoutException e) {
                // 加载指示器可能不存在，继续处理下一个
            }
        }
    }
}
```

## 6.8 章节总结

本章深入讲解了Selenium中的等待机制和异常处理策略，这是构建稳定可靠的自动化测试框架的关键技术。通过学习不同类型的等待机制、异常分类与处理、超时管理和健壮测试设计，您现在应该能够设计出更加稳定和可靠的自动化测试脚本。

### 关键要点回顾

1. **等待机制分类**：隐式等待、显式等待、线程等待及其适用场景
2. **显式等待高级用法**：ExpectedConditions方法、FluentWait、自定义等待条件
3. **常见Selenium异常**：异常分类、处理策略和恢复方法
4. **异常恢复工具类**：元素查找、点击、输入的重试机制
5. **超时处理策略**：超时类型设置、超时管理器设计
6. **健壮测试设计**：设计原则、健壮的页面对象实现

### 下一步学习

在下一章中，我们将学习Selenium数据驱动与参数化测试，这是提高测试覆盖率和测试效率的重要技术。我们将深入了解如何使用各种数据源驱动测试、如何设计参数化测试、以及如何实现测试数据的生成和管理。

## 6.9 实践练习

1. **等待机制应用**：在一个动态网页上使用不同类型的等待机制，比较它们的效率和可靠性
2. **自定义等待条件**：实现几个自定义等待条件，如等待特定数量的元素出现、等待AJAX请求完成等
3. **异常处理工具**：实现一个完整的异常处理工具类，包括元素查找、点击和输入的重试机制
4. **超时管理**：设计一个超时管理器，可以根据不同操作场景动态调整超时设置
5. **健壮测试设计**：设计一个健壮的页面对象基类，包含完善的等待和异常处理机制

请完成以上练习，并思考：
- 在什么情况下应该使用隐式等待而不是显式等待？
- 如何设计异常处理策略既能提高测试稳定性，又不会掩盖真正的问题？
- 如何平衡测试执行速度和测试稳定性？

通过思考这些问题，您将更深入地理解等待机制和异常处理的最佳实践和技巧。