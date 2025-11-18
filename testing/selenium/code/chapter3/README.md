# 第3章代码示例 - Selenium元素定位与交互操作

本目录包含第3章"Selenium元素定位与交互操作"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. 元素定位示例
- **ElementLocatorTest.java** - 演示所有8种元素定位方式
- **AdvancedElementLocatorTest.java** - 演示高级元素定位技术
- **RelativeLocatorsTest.java** - 演示相对定位器使用

### 2. 元素交互示例
- **ElementInteractionTest.java** - 演示基本元素交互操作
- **FormInteractionTest.java** - 演示表单操作
- **MouseActionsTest.java** - 演示鼠标操作
- **KeyboardActionsTest.java** - 演示键盘操作

### 3. 等待策略示例
- **WaitStrategiesTest.java** - 演显式等待和自定义条件

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
├── ElementLocatorTest.java          # 元素定位基础
├── AdvancedElementLocatorTest.java   # 高级元素定位
├── RelativeLocatorsTest.java         # 相对定位器
├── ElementInteractionTest.java       # 基本元素交互
├── FormInteractionTest.java         # 表单操作
├── MouseActionsTest.java            # 鼠标操作
├── KeyboardActionsTest.java         # 键盘操作
└── WaitStrategiesTest.java          # 等待策略

src/test/resources/
├── locator-test.html               # 元素定位测试页面
├── form-test.html                  # 表单测试页面
├── actions-test.html               # 交互操作测试页面
└── test-data.json                  # 测试数据文件
```

## 注意事项

1. 测试使用Chrome浏览器的无头模式运行，如需有界面运行，请删除ChromeOptions中的"--headless"参数
2. 部分测试使用本地HTML文件，确保这些文件位于正确的路径
3. 相对定位器需要Selenium 4+版本支持
4. 高级元素定位示例中包含Xpath和CSS选择器的复杂使用场景