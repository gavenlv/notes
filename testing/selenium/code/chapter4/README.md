# 第4章代码示例 - Selenium高级操作与窗口管理

本目录包含第4章"Selenium高级操作与窗口管理"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. 高级操作示例
- **JavaScriptExecutorTest.java** - 演示JavaScript执行器的高级使用
- **CookieManagementTest.java** - 演示Cookie操作和管理
- **LocalAndSessionStorageTest.java** - 演示LocalStorage和SessionStorage操作

### 2. 窗口管理示例
- **WindowManagementTest.java** - 演示多窗口和标签页管理
- **IFrameHandlingTest.java** - 演示iFrame处理
- **TabsAndWindowsTest.java** - 演示标签页和窗口操作

### 3. 浏览器控制示例
- **BrowserNavigationTest.java** - 演示浏览器导航控制
- **BrowserOptionsTest.java** - 演示浏览器选项和配置
- **MobileEmulationTest.java** - 演示移动设备模拟

### 4. 文件操作示例
- **FileUploadTest.java** - 演示文件上传操作
- **FileDownloadTest.java** - 演示文件下载操作

## 运行说明

1. 使用Maven运行测试：`mvn test`
2. 使用TestNG运行：`mvn test -DsuiteXmlFile=testng.xml`
3. 在IDE中直接运行测试类

## 环境要求

- Java 11+
- Maven 3.6+
- Chrome浏览器
- ChromeDriver（由WebDriverManager自动管理）

## 项目结构

```
src/test/java/com/example/selenium/tests/
├── JavaScriptExecutorTest.java     # JavaScript执行器
├── CookieManagementTest.java       # Cookie操作
├── LocalAndSessionStorageTest.java # 本地和会话存储
├── WindowManagementTest.java       # 窗口管理
├── IFramesHandlingTest.java        # iFrame处理
├── TabsAndWindowsTest.java         # 标签页和窗口
├── BrowserNavigationTest.java      # 浏览器导航
├── BrowserOptionsTest.java          # 浏览器选项
├── MobileEmulationTest.java         # 移动设备模拟
├── FileUploadTest.java             # 文件上传
└── FileDownloadTest.java            # 文件下载

src/test/resources/
├── advanced-operations.html        # 高级操作测试页面
├── iframes-test.html               # iFrame测试页面
├── file-operations-test.html        # 文件操作测试页面
├── mobile-test.html                 # 移动设备测试页面
└── download-test-file.txt           # 测试下载文件
```

## 注意事项

1. 文件下载测试可能需要根据实际浏览器配置调整下载路径
2. 移动设备模拟需要Selenium 4+版本支持
3. JavaScript执行器示例中包含DOM操作和事件触发
4. Cookie管理示例包含跨域和安全限制的处理
5. 窗口管理示例需要处理浏览器窗口句柄切换
6. 部分测试可能需要在有界面的浏览器中运行才能看到完整效果