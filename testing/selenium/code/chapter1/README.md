# 第1章代码示例 - Selenium简介与环境搭建

本章包含以下代码示例：

1. **基础项目配置**
   - `pom.xml` - Maven项目配置文件
   - `testng.xml` - TestNG测试套件配置

2. **环境验证代码**
   - `EnvironmentSetupTest.java` - 验证环境配置是否正确

3. **第一个Selenium测试**
   - `FirstSeleniumTest.java` - 第一个完整的Selenium测试脚本
   - `BaseTest.java` - 基础测试类，封装通用功能

4. **工具类和配置**
   - `ConfigReader.java` - 配置文件读取工具
   - `config.properties` - 测试环境配置文件

## 运行指南

1. 确保已安装Java 11+和Maven
2. 导入项目到IDE
3. 运行`EnvironmentSetupTest`验证环境
4. 运行`FirstSeleniumTest`体验第一个Selenium脚本

## 注意事项

- 代码使用Chrome浏览器，确保已安装Chrome和对应版本的驱动
- 使用WebDriverManager自动管理浏览器驱动
- 测试使用TestNG框架，确保IDE支持TestNG插件