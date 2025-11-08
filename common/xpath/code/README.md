# XPath代码示例

本目录包含XPath教程中的所有代码示例，按章节组织。

## 目录结构

```
code/
├── basic-examples/          # 基础示例
│   ├── xpath_basics.py      # XPath基础语法示例
│   ├── xpath_path_expressions.py  # 路径表达式示例
│   ├── xpath_axes_demo.py   # 轴系统演示
│   └── xpath_functions_demo.py  # 函数使用示例
├── python-examples/         # Python中的XPath
│   ├── lxml_basics.py       # lxml基础用法
│   ├── lxml_advanced.py     # lxml高级功能
│   ├── xpath_real_world.py  # Python XPath实战
│   └── xpath_wrapper.py     # XPath封装类
├── javascript-examples/      # JavaScript中的XPath
│   ├── xpath_basics.js      # 浏览器中XPath基础
│   ├── xpath_browser_console.js  # 浏览器控制台XPath
│   ├── xpath_wrapper.js     # JavaScript XPath封装
│   └── web_scraper.js       # 网页爬虫示例
├── java-examples/           # Java中的XPath
│   ├── XPathBasics.java    # Java XPath基础
│   ├── XPathAdvanced.java  # Java XPath高级应用
│   └── XPathRealWorld.java  # Java XPath实战
├── csharp-examples/        # C#中的XPath
│   ├── XPathBasics.cs      # C# XPath基础
│   └── XPathAdvanced.cs    # C# XPath高级应用
├── performance-optimization/  # 性能优化
│   ├── xpath_cache.py      # XPath缓存实现
│   ├── xpath_benchmark.py  # XPath性能测试
│   └── precomputed_queries.py  # 预计算查询
└── real-world-cases/        # 实战案例
    ├── ecommerce_scraper.py    # 电商网站爬虫
    ├── news_extractor.py       # 新闻内容提取
    ├── library_system.py       # 图书馆系统
    └── xpath_project_demo.py   # 综合项目演示
```

## 使用说明

### 基础示例

基础示例展示了XPath的核心概念和基本用法，适合初学者学习：

1. `xpath_basics.py` - 演示XPath基本语法和选择器
2. `xpath_path_expressions.py` - 展示路径表达式的各种用法
3. `xpath_axes_demo.py` - 演示XPath轴系统的概念和应用
4. `xpath_functions_demo.py` - 展示XPath内置函数的使用

### 语言特定示例

不同语言中的XPath实现：

1. **Python示例**：使用lxml库处理XML和HTML
2. **JavaScript示例**：浏览器和Node.js环境中的XPath应用
3. **Java示例**：使用Java标准库处理XML文档
4. **C#示例**：在.NET框架中使用XPath导航XML

### 性能优化

XPath性能优化相关示例：

1. `xpath_cache.py` - 实现XPath查询缓存机制
2. `xpath_benchmark.py` - XPath表达式性能测试工具
3. `precomputed_queries.py` - 预计算常用查询

### 实战案例

真实项目中的XPath应用：

1. `ecommerce_scraper.py` - 电商网站商品信息抓取
2. `news_extractor.py` - 新闻网站内容提取
3. `library_system.py` - 图书馆管理系统XML处理
4. `xpath_project_demo.py` - 综合项目演示

## 运行要求

### Python示例

```bash
# 安装依赖
pip install lxml requests

# 运行示例
python code/basic-examples/xpath_basics.py
```

### JavaScript示例

在浏览器控制台或Node.js环境中运行：

```bash
# 浏览器控制台
$x("//div[@class='example']")

# Node.js (需要xmldom)
npm install xmldom
node code/javascript-examples/xpath_basics.js
```

### Java示例

```bash
# 编译Java示例
javac -cp . code/java-examples/XPathBasics.java

# 运行示例
java -cp . code.java-examples.XPathBasics
```

### C#示例

```bash
# 使用.NET CLI编译和运行
dotnet run --project code/csharp-examples/
```

## 学习建议

1. **循序渐进**：从基础示例开始，逐步学习高级特性
2. **动手实践**：运行和修改代码示例，理解XPath的工作原理
3. **比较学习**：比较不同语言中XPath的实现差异
4. **性能意识**：通过性能优化示例了解XPath的性能特点
5. **实战应用**：参考实战案例，将XPath应用到实际项目中

## 扩展资源

- [W3C XPath 1.0 规范](https://www.w3.org/TR/xpath/)
- [W3C XPath 2.0 规范](https://www.w3.org/TR/xpath20/)
- [W3C XPath 3.1 规范](https://www.w3.org/TR/xpath-31/)
- [lxml 文档](https://lxml.de/)
- [MDN XPath 文档](https://developer.mozilla.org/en-US/docs/Web/XPath)

## 问题反馈

如果您在使用这些示例时遇到问题，或有改进建议，请提交Issue或Pull Request。