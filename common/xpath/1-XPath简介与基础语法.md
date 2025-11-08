# 第1章：XPath简介与基础语法

## 1.1 什么是XPath？

XPath（XML Path Language）是一种在XML文档中查找信息的语言。它使用路径表达式来导航XML文档，可以选择节点或节点集。XPath最初设计用于XSLT，但现在已经成为一个独立的标准，广泛应用于各种XML处理场景。

### 1.1.1 XPath的历史

- 1999年：XPath 1.0作为W3C推荐标准发布，作为XSLT的一部分
- 2003年：XPath 2.0发布，增加了更多数据类型和函数
- 2017年：XPath 3.1发布，支持JSON和更多现代编程特性

### 1.1.2 XPath的应用场景

1. **XML文档查询**：从复杂的XML结构中提取特定信息
2. **Web自动化测试**：在Selenium等工具中定位页面元素
3. **HTML解析**：从网页中提取结构化数据
4. **数据转换**：在XSLT中定义节点选择规则
5. **配置文件处理**：读取和修改XML配置文件

## 1.2 XPath基础概念

### 1.2.1 节点类型

在XPath中，XML文档被视为节点树，包含以下七种节点类型：

| 节点类型 | 描述 | 示例 |
|---------|------|------|
| 元素节点 | XML元素 | `<book>`, `<title>` |
| 属性节点 | 元素的属性 | `id="bk101"`, `lang="en"` |
| 文本节点 | 元素包含的文本内容 | "Harry Potter" |
| 命名空间节点 | 元素的命名空间 | `xmlns:ns="http://example.com"` |
| 处理指令节点 | XML处理指令 | `<?xml-stylesheet type="text/xsl" href="style.xsl"?>` |
| 注释节点 | XML注释 | `<!-- This is a comment -->` |
| 文档节点 | 整个文档的根节点 | 文档本身 |

### 1.2.2 节点关系

1. **父节点（Parent）**：直接包含当前节点的节点
2. **子节点（Children）**：当前节点直接包含的节点
3. **兄弟节点（Siblings）**：拥有相同父节点的节点
4. **祖先节点（Ancestors）**：父节点、父节点的父节点等
5. **后代节点（Descendants）**：子节点、子节点的子节点等

## 1.3 XPath路径表达式基础

### 1.3.1 基本路径语法

XPath使用路径表达式来选择节点，类似于文件系统的路径：

```xpath
/          # 从根节点开始
//         # 从文档中任意位置开始
.          # 当前节点
..         # 当前节点的父节点
@          # 选择属性
*          # 通配符，匹配任意节点
```

### 1.3.2 绝对路径与相对路径

```xpath
# 绝对路径 - 从根节点开始
/bookstore/book/title
# 相对路径 - 从当前节点开始
./title
# 或者直接写
title
```

### 1.3.3 选择特定节点

```xpath
# 选择所有book元素
//book

# 选择所有title元素
//title

# 选择bookstore下的所有book元素
/bookstore/book

# 选择第一个book元素
//book[1]

# 选择最后一个book元素
//book[last()]
```

## 1.4 谓语(Predicates)

谓语用于查找特定的节点，嵌在方括号`[]`中。

### 1.4.1 基本谓语

```xpath
# 选择第一个book元素
/bookstore/book[1]

# 选择最后一个book元素
/bookstore/book[last()]

# 选择前两个book元素
/bookstore/book[position()<3]

# 选择具有特定属性的book元素
//book[@category='web']

# 选择价格大于35的book元素
//book[price>35]
```

### 1.4.2 多条件谓语

```xpath
# 选择category为web且价格大于35的book
//book[@category='web' and price>35]

# 选择category为web或children的book
//book[@category='web' or @category='children']

# 选择price不等于30的book
//book[price!=30]
```

## 1.5 选取未知节点

XPath支持使用通配符选取未知节点：

```xpath
# 选择bookstore的所有子元素
/bookstore/*

# 选择文档中的所有元素
//*

# 选择所有带有category属性的book元素
//book[@*]

# 选择bookstore下所有具有属性的子元素
/bookstore/*[@*]
```

## 1.6 XPath操作符

### 1.6.1 比较操作符

| 操作符 | 描述 | 示例 |
|-------|------|------|
| = | 等于 | price=9.90 |
| != | 不等于 | price!=9.90 |
| < | 小于 | price<9.90 |
| <= | 小于等于 | price<=9.90 |
| > | 大于 | price>9.90 |
| >= | 大于等于 | price>=9.90 |

### 1.6.2 逻辑操作符

| 操作符 | 描述 | 示例 |
|-------|------|------|
| and | 逻辑与 | price>9.00 and price<20.00 |
| or | 逻辑或 | category='web' or category='children' |
| not | 逻辑非 | not(category='web') |

## 1.7 实例演示

让我们使用一个简单的XML文档来演示XPath的基本用法：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J. K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
    </book>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="web">
        <title lang="en">XQuery Kick Start</title>
        <author>James McGovern</author>
        <author>Per Bothner</author>
        <author>Kurt Cagle</author>
        <author>James Linn</author>
        <author>Vaidyanathan Nagarajan</author>
        <year>2003</year>
        <price>49.99</price>
    </book>
</bookstore>
```

### 1.7.1 基本查询示例

```xpath
# 选择所有book元素的title
//book/title

# 选择所有book元素的所有子节点
//book/*

# 选择第一个book的title
//book[1]/title

# 选择具有category="web"属性的book元素
//book[@category='web']

# 选择所有价格大于30的book元素
//book[price>30]

# 选择所有具有lang属性的title元素
//title[@lang]

# 选择所有lang="en"的title元素
//title[@lang='en']
```

## 1.8 实验验证

让我们通过Python代码来验证上述XPath表达式：

```python
# code/basic-examples/xpath_basic_demo.py
from lxml import etree

# 示例XML文档
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J. K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
    </book>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="web">
        <title lang="en">XQuery Kick Start</title>
        <author>James McGovern</author>
        <author>Per Bothner</author>
        <author>Kurt Cagle</author>
        <author>James Linn</author>
        <author>Vaidyanathan Nagarajan</author>
        <year>2003</year>
        <price>49.99</price>
    </book>
</bookstore>
"""

def test_xpath_expressions():
    # 解析XML
    root = etree.fromstring(xml_data)
    
    # 测试XPath表达式
    expressions = [
        ("//book/title", "所有book元素的title"),
        ("//book/*", "所有book元素的所有子节点"),
        ("//book[1]/title", "第一个book的title"),
        ("//book[@category='web']", "category='web'的book元素"),
        ("//book[price>30]", "价格大于30的book元素"),
        ("//title[@lang]", "具有lang属性的title元素"),
        ("//title[@lang='en']", "lang='en'的title元素")
    ]
    
    for xpath_expr, description in expressions:
        results = root.xpath(xpath_expr)
        print(f"\nXPath: {xpath_expr}")
        print(f"描述: {description}")
        for i, result in enumerate(results, 1):
            if isinstance(result, etree._Element):
                print(f"  结果{i}: {result.tag}={result.text}")
            else:
                print(f"  结果{i}: {result}")

if __name__ == "__main__":
    test_xpath_expressions()
```

## 1.9 在浏览器中测试XPath

现代浏览器的开发者工具也支持XPath查询，您可以在HTML页面上练习XPath：

1. 打开任意网页
2. 按F12打开开发者工具
3. 在控制台(Console)中使用`$x()`函数测试XPath表达式

```javascript
// 示例：选择页面中的所有链接
$x("//a[@href]")

// 示例：选择所有包含特定文本的元素
$x("//*[contains(text(), 'XPath')]")

// 示例：选择所有具有class属性的元素
$x("//*[@class]")
```

## 1.10 本章小结

本章介绍了XPath的基本概念和语法，包括：

- XPath的定义和应用场景
- XML文档的节点类型和关系
- 基本的路径表达式语法
- 谓语的使用方法
- 通配符和操作符
- 通过Python和浏览器验证XPath表达式

掌握了这些基础知识，您已经可以编写简单的XPath表达式来查询XML/HTML文档了。下一章我们将深入学习XPath的路径表达式和轴系统，这是XPath的核心功能。

## 1.11 练习

1. 编写XPath表达式选择所有价格在30到50之间的book元素
2. 选择所有作者多于一个的book元素
3. 选择所有在2003年之后出版的book元素
4. 选择所有title包含"XML"的book元素
5. 选择所有具有lang属性且值不为"en"的title元素

尝试在浏览器控制台或使用提供的Python代码验证您的答案。