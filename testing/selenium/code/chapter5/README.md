# 第5章代码示例 - Selenium测试框架设计与Page Object模式

本目录包含第5章"Selenium测试框架设计与Page Object模式"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. Page Object模式示例
- **BasePage.java** - 基础页面类，包含通用操作
- **HomePage.java** - 首页页面对象
- **LoginPage.java** - 登录页面对象
- **SearchResultsPage.java** - 搜索结果页面对象

### 2. 页面对象工厂模式示例
- **PageFactoryExample.java** - 演示PageFactory的使用
- **FindByAnnotations.java** - 演示@FindBy注解的使用
- **CustomElementLocator.java** - 自定义元素定位器

### 3. 测试框架结构示例
- **BaseTest.java** - 基础测试类，包含通用测试设置
- **TestDataManager.java** - 测试数据管理器
- **ReportManager.java** - 报告管理器
- **ConfigurationManager.java** - 配置管理器

### 4. 实际测试示例
- **LoginTest.java** - 使用Page Object模式的登录测试
- **SearchTest.java** - 搜索功能测试
- **EndToEndTest.java** - 端到端测试示例

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
src/main/java/com/example/selenium/
├── framework/                      # 框架核心类
│   ├── BaseTest.java              # 基础测试类
│   ├── TestDataManager.java       # 测试数据管理
│   ├── ReportManager.java         # 报告管理
│   └── ConfigurationManager.java  # 配置管理
├── pages/                          # 页面对象
│   ├── BasePage.java              # 基础页面类
│   ├── HomePage.java              # 首页页面对象
│   ├── LoginPage.java             # 登录页面对象
│   └── SearchResultsPage.java     # 搜索结果页面对象
├── elements/                       # 自定义元素类
│   ├── Button.java                # 自定义按钮元素
│   ├── TextField.java             # 自定义文本框元素
│   └── Table.java                 # 自定义表格元素
├── utilities/                      # 工具类
│   ├── WaitUtils.java             # 等待工具
│   ├── StringUtils.java           # 字符串工具
│   └── ExcelUtils.java            # Excel处理工具
└── exceptions/                     # 自定义异常
    ├── ElementNotFoundException.java
    └── FrameworkException.java

src/test/java/com/example/selenium/tests/
├── LoginTest.java                  # 登录测试
├── SearchTest.java                 # 搜索测试
├── EndToEndTest.java               # 端到端测试
└── PageFactoryExample.java         # PageFactory示例

src/test/resources/
├── config.properties               # 配置文件
├── test-data.xlsx                  # 测试数据Excel
├── test-website.html               # 测试网站模拟
└── testng.xml                      # TestNG配置
```

## 设计原则

1. **单一职责原则** - 每个类只负责一个功能
2. **开闭原则** - 对扩展开放，对修改封闭
3. **依赖倒置原则** - 依赖抽象而非具体实现
4. **Page Object模式** - 将页面交互封装到页面对象中
5. **数据驱动** - 测试数据与测试逻辑分离

## 注意事项

1. Page Object模式中，页面对象应该只包含页面元素的定义和操作，不应包含测试断言
2. 页面对象应该返回其他页面对象，支持链式调用
3. 测试类应该只包含测试逻辑和断言，不应包含页面交互细节
4. 基础类应该封装通用功能，减少重复代码
5. 配置信息应该集中管理，便于维护和修改