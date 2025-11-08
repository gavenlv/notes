# XPath快速开始指南

本指南将帮助您快速上手XPath，了解基本概念并开始编写XPath表达式。

## 什么是XPath？

XPath（XML Path Language）是一种用于在XML文档中定位信息的语言。它使用路径表达式来导航XML文档的层次结构，并选择节点或节点集。

## 快速入门示例

### 1. 基本语法

假设我们有以下XML文档：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="programming">
        <title lang="en">XPath for Dummies</title>
        <author>John Doe</author>
        <year>2020</year>
        <price>29.99</price>
    </book>
</bookstore>
```

### 2. 常用XPath表达式

| 表达式 | 描述 | 示例结果 |
|--------|------|----------|
| `/bookstore/book` | 从根节点选择所有book元素 | 两个book元素 |
| `//book` | 选择文档中所有book元素，不考虑位置 | 两个book元素 |
| `//book[1]` | 选择第一个book元素 | 第一个book |
| `//book[last()]` | 选择最后一个book元素 | 第二个book |
| `//book[@category='web']` | 选择所有category属性为web的book元素 | 第一个book |
| `//title[@lang='en']` | 选择所有lang属性为en的title元素 | 两个title |
| `//price>30` | 选择所有price元素值大于30的节点 | 第一个price (39.95) |

### 3. 浏览器中测试XPath

在浏览器开发者工具中，可以使用`$x()`函数测试XPath表达式：

```javascript
// 在浏览器控制台中运行
$x("//book")                    // 获取所有book元素
$x("//title/text()")            // 获取所有title文本
$x("//book[@category='web']")   // 获取category为web的book
$x("//price[.>30]")             // 获取价格大于30的price
```

### 4. Python中使用XPath

```python
from lxml import etree

# 解析XML
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
</bookstore>"""

root = etree.fromstring(xml_data)

# 使用XPath
titles = root.xpath("//title/text()")  # 获取所有标题
print(titles)  # 输出: ['Learning XML']

books = root.xpath("//book[@category='web']")
for book in books:
    title = book.xpath("title/text()")[0]
    price = book.xpath("price/text()")[0]
    print(f"{title}: ${price}")  # 输出: Learning XML: $39.95
```

## 学习路径

### 1. 初级（第1-3章）

1. **XPath简介与基础语法** - 了解XPath基本概念和语法
2. **XPath路径表达式** - 掌握路径表达式和节点选择
3. **XPath轴与节点测试** - 理解轴系统和节点测试

### 2. 中级（第4-6章）

4. **XPath函数详解** - 学习内置函数的使用
5. **XPath高级应用** - 掌握复杂查询技巧
6. **XPath在不同语言中的应用** - 了解各语言中的XPath实现

### 3. 高级（第7-8章）

7. **XPath性能优化与最佳实践** - 提高XPath查询效率
8. **XPath实战案例** - 通过真实案例巩固知识

## 常用XPath速查表

### 基本选择器

| 表达式 | 说明 |
|--------|------|
| `nodename` | 选择所有名为nodename的子节点 |
| `/` | 从根节点选择 |
| `//` | 从文档任意位置选择 |
| `.` | 选择当前节点 |
| `..` | 选择当前节点的父节点 |
| `@` | 选择属性 |

### 谓语（Predicates）

| 表达式 | 说明 |
|--------|------|
| `[1]` | 第一个节点 |
| `[last()]` | 最后一个节点 |
| `[position()>2]` | 位置大于2的节点 |
| `[@attribute]` | 具有特定属性的节点 |
| `[@attribute='value']` | 属性等于特定值的节点 |
| `[text()='value']` | 文本等于特定值的节点 |
| `[price>30]` | 子元素price大于30的节点 |

### 通配符

| 表达式 | 说明 |
|--------|------|
| `*` | 匹配任意元素节点 |
| `@*` | 匹配任意属性节点 |
| `node()` | 匹配任意类型的节点 |
| `text()` | 匹配文本节点 |
| `comment()` | 匹配注释节点 |

### 常用函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `count()` | 计算节点数量 | `count(//book)` |
| `position()` | 返回节点位置 | `//book[position()=2]` |
| `last()` | 返回最后一个节点位置 | `//book[last()]` |
| `contains()` | 检查字符串包含 | `//book[contains(title, 'XML')]` |
| `starts-with()` | 检查字符串开始 | `//book[starts-with(title, 'Learning')]` |
| `text()` | 获取文本内容 | `//title/text()` |

## 实践练习

### 练习1：基本选择

使用以下XML文档：

```xml
<library>
    <book id="b1" category="fiction">
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
        <year>1925</year>
        <price>12.99</price>
    </book>
    <book id="b2" category="non-fiction">
        <title>A Brief History of Time</title>
        <author>Stephen Hawking</author>
        <year>1988</year>
        <price>14.99</price>
    </book>
</library>
```

编写XPath表达式：

1. 选择所有书籍
2. 选择第一本书
3. 选择非小说类书籍
4. 选择价格高于13美元的书籍
5. 选择书名中包含"History"的书籍

**答案：**
1. `//book`
2. `//book[1]`
3. `//book[@category='non-fiction']`
4. `//book[price > 13]`
5. `//book[contains(title, 'History')]`

### 练习2：实际网页测试

在浏览器控制台中使用`$x()`函数测试当前页面：

1. 获取所有链接：`$x("//a[@href]")`
2. 获取所有图片：`$x("//img[@src]")`
3. 获取页面标题：`$x("//title/text()")`
4. 获取具有特定class的元素：`$x("//*[@class='your-class-name']")`

## 常见陷阱和技巧

### 陷阱1：属性与元素混淆

```xpath
//book[category='fiction']    // 正确：属性用@前缀
//book[category/text()='fiction']  // 错误：category是属性，不是元素
```

### 陷阱2：文本内容提取

```xpath
//title                    // 返回title元素节点
//title/text()            // 返回title元素的文本内容
//title/string()           // 返回title元素及其所有后代的文本内容
```

### 技巧1：组合谓语

```xpath
//book[@category='fiction' and price > 12]
```

### 技巧2：使用轴进行复杂导航

```xpath
//title/ancestor::book        // 获取title的所有book祖先
//book/following-sibling::*   // 获取book之后的所有兄弟元素
```

## 下一步

1. 阅读[第1章：XPath简介与基础语法](1-XPath简介与基础语法.md)
2. 运行[code/basic-examples/xpath_basics.py](code/basic-examples/xpath_basics.py)中的示例
3. 尝试练习中的XPath表达式
4. 在真实网页上测试XPath

## 更多资源

- [W3C XPath 1.0 规范](https://www.w3.org/TR/xpath/)
- [MDN XPath 文档](https://developer.mozilla.org/en-US/docs/Web/XPath)
- [lxml 文档](https://lxml.de/xpathxslt.html)

有了这个快速开始指南，您现在应该能够编写基本的XPath表达式并开始在项目中使用XPath了！