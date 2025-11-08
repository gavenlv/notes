# 第3章：XPath轴与节点测试

## 3.1 轴（Axes）概述

XPath轴定义了相对于当前节点的节点集合，是XPath中最强大的概念之一。轴指定了在XML文档中导航的方向和范围，使我们能够从任意节点访问其他相关节点。

### 3.1.1 轴的基本语法

轴的基本语法格式为：

```
轴名称::节点测试[谓语]
```

例如：

```xpath
child::book        # 当前节点的所有book子元素
attribute::id      # 当前节点的id属性
ancestor::section # 当前节点的所有section祖先元素
```

### 3.1.2 轴的完整列表

XPath 1.0定义了13个轴：

| 轴名称 | 描述 | 方向 |
|-------|------|------|
| `ancestor` | 当前节点的所有祖先节点 | 向上 |
| `ancestor-or-self` | 当前节点及其所有祖先节点 | 向上 |
| `attribute` | 当前节点的所有属性节点 | 向下 |
| `child` | 当前节点的所有子节点 | 向下 |
| `descendant` | 当前节点的所有后代节点 | 向下 |
| `descendant-or-self` | 当前节点及其所有后代节点 | 向下 |
| `following` | 文档中当前节点之后的所有节点 | 向前 |
| `following-sibling` | 当前节点之后的所有兄弟节点 | 向前 |
| `namespace` | 当前节点的所有命名空间节点 | 特殊 |
| `parent` | 当前节点的父节点 | 向上 |
| `preceding` | 文档中当前节点之前的所有节点 | 向后 |
| `preceding-sibling` | 当前节点之前的所有兄弟节点 | 向后 |
| `self` | 当前节点本身 | 无 |

## 3.2 树形导航轴

### 3.2.1 向下导航轴

#### child轴
```xpath
# 选择当前节点的所有book子元素
child::book

# 选择当前节点的所有子元素
child::*

# 等价于直接使用元素名
book
```

#### descendant轴
```xpath
# 选择当前节点的所有后代book元素
descendant::book

# 选择当前节点的所有后代元素
descendant::*
```

#### descendant-or-self轴
```xpath
# 选择当前节点及其所有后代book元素
descendant-or-self::book

# 选择当前节点及其所有后代元素
descendant-or-self::*
```

### 3.2.2 向上导航轴

#### parent轴
```xpath
# 选择当前节点的父节点
parent::*

# 等价于 ..
..
```

#### ancestor轴
```xpath
# 选择当前节点的所有section祖先元素
ancestor::section

# 选择当前节点的所有祖先元素
ancestor::*
```

#### ancestor-or-self轴
```xpath
# 选择当前节点及其所有section祖先元素
ancestor-or-self::section

# 选择当前节点及其所有祖先元素
ancestor-or-self::*
```

## 3.3 文档顺序轴

### 3.3.1 向前导航轴

#### following轴
```xpath
# 选择文档中当前节点之后的所有book元素
following::book

# 选择文档中当前节点之后的所有元素
following::*
```

#### following-sibling轴
```xpath
# 选择当前节点之后的所有兄弟book元素
following-sibling::book

# 选择当前节点之后的所有兄弟元素
following-sibling::*
```

### 3.3.2 向后导航轴

#### preceding轴
```xpath
# 选择文档中当前节点之前的所有book元素
preceding::book

# 选择文档中当前节点之前的所有元素
preceding::*
```

#### preceding-sibling轴
```xpath
# 选择当前节点之前的所有兄弟book元素
preceding-sibling::book

# 选择当前节点之前的所有兄弟元素
preceding-sibling::*
```

## 3.4 节点测试

节点测试用于筛选轴中的节点，可以是以下几种形式：

### 3.4.1 节点名称测试

```xpath
# 选择所有book元素
child::book

# 选择所有元素
child::*

# 选择所有属性
attribute::*
```

### 3.4.2 节点类型测试

XPath提供了几个节点类型测试函数：

```xpath
# 选择所有元素节点
child::element()

# 选择所有属性节点
attribute::attribute()

# 选择所有文本节点
child::text()

# 选择所有注释节点
child::comment()

# 选择所有处理指令节点
child::processing-instruction()

# 选择所有节点
child::node()
```

### 3.4.3 命名空间测试

```xpath
# 选择特定命名空间中的所有元素
child::ns:*

# 选择特定命名空间中的特定元素
child::ns:element
```

## 3.5 轴的组合使用

### 3.5.1 多轴导航

```xpath
# 选择祖父节点中的section元素
parent::*/parent::section

# 选择兄弟节点的后代元素
preceding-sibling::*[1]/descendant::book

# 选择祖先节点的兄弟元素
ancestor::section[1]/following-sibling::section
```

### 3.5.2 轴与谓语结合

```xpath
# 选择第一个book元素的父节点
child::book[1]/parent::*

# 选择具有category属性的book元素的祖先section
child::book[@category]/ancestor::section

# 选择前三个author元素的同级后续兄弟元素
child::author[position() <= 3]/following-sibling::*
```

## 3.6 轴的实际应用

让我们使用一个复杂的XML文档来演示轴的应用：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns:pub="http://example.com/publisher">
    <pub:publisher id="tech-books">
        <pub:name>Tech Books Publishing</pub:name>
        <pub:address>123 Tech Street, Tech City</pub:address>
    </pub:publisher>
    
    <section name="programming">
        <book id="bk101" category="programming">
            <title lang="en">Clean Code</title>
            <author>Robert C. Martin</author>
            <author>Robert C. Martin Series</author>
            <published>2008</published>
            <price currency="USD">34.99</price>
            <pub:publisher-ref ref="tech-books"/>
            <tags>
                <tag>programming</tag>
                <tag>best practices</tag>
            </tags>
        </book>
        
        <book id="bk102" category="programming">
            <title lang="en">Design Patterns</title>
            <author>Erich Gamma</author>
            <author>Richard Helm</author>
            <author>Ralph Johnson</author>
            <author>John Vlissides</author>
            <published>1994</published>
            <price currency="USD">45.99</price>
            <pub:publisher-ref ref="tech-books"/>
        </book>
    </section>
    
    <section name="database">
        <book id="bk201" category="database">
            <title lang="en">Database System Concepts</title>
            <author>Abraham Silberschatz</author>
            <author>Henry F. Korth</author>
            <author>S. Sudarshan</author>
            <published>2019</published>
            <price currency="USD">89.99</price>
            <pub:publisher-ref ref="tech-books"/>
            <!-- This is a comment about the book -->
            <related-books>
                <book-ref id="bk101"/>
                <book-ref id="bk301"/>
            </related-books>
        </book>
    </section>
    
    <appendix>
        <section name="glossary">
            <!-- Glossary content would go here -->
            <term>Normalization</term>
            <definition>A process of organizing data...</definition>
        </section>
    </appendix>
</catalog>
```

### 3.6.1 轴应用示例

```xpath
# 选择当前节点的所有section祖先
ancestor::section

# 选择当前节点的第一个book后代
descendant::book[1]

# 选择当前节点的所有属性
attribute::*

# 选择当前节点的所有作者兄弟节点
preceding-sibling::author | following-sibling::author

# 选择文档中当前节点之后的所有book元素
following::book

# 选择当前节点之前的所有注释
preceding::comment()

# 选择当前节点之后的第一个文本节点
following::text()[1]

# 选择当前节点的所有pub命名空间的子元素
child::pub:*

# 选择当前节点的所有祖先节点（包括自身）
ancestor-or-self::*
```

### 3.6.2 复杂轴查询示例

```xpath
# 选择所有在其section中价格最高的book
//book[price = max(ancestor::section/book/price)]

# 选择所有具有多个作者的book，并选择他们的第一个作者
//book[count(author) > 1]/author[1]

# 选择所有引用其他书籍的book
//book[related-books/book-ref]

# 选择所有在1990-2000年之间出版的编程书籍
//section[@name='programming']/book[published >= 1990 and published <= 2000]

# 选择所有价格高于其兄弟节点平均价格的book
//book[price > sum(../book/price) div count(../book)]

# 选择所有在文档中出现在特定书籍之后的所有书籍
//book[@id='bk101']/following::book

# 选择所有在文档中出现在特定书籍之前的所有书籍
//book[@id='bk201']/preceding::book

# 选择所有具有同名兄弟节点的元素
//*[count(../*[name() = name(current())]) > 1]

# 选择所有在当前节点的父节点中的所有元素
parent::*/child::*

# 选择当前节点的所有命名空间节点
namespace::*
```

## 3.7 实验验证

让我们通过Python代码来验证轴的概念和应用：

```python
# code/basic-examples/xpath_axes_demo.py
from lxml import etree

# 复杂XML文档
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns:pub="http://example.com/publisher">
    <pub:publisher id="tech-books">
        <pub:name>Tech Books Publishing</pub:name>
        <pub:address>123 Tech Street, Tech City</pub:address>
    </pub:publisher>
    
    <section name="programming">
        <book id="bk101" category="programming">
            <title lang="en">Clean Code</title>
            <author>Robert C. Martin</author>
            <author>Robert C. Martin Series</author>
            <published>2008</published>
            <price currency="USD">34.99</price>
            <pub:publisher-ref ref="tech-books"/>
            <tags>
                <tag>programming</tag>
                <tag>best practices</tag>
            </tags>
        </book>
        
        <book id="bk102" category="programming">
            <title lang="en">Design Patterns</title>
            <author>Erich Gamma</author>
            <author>Richard Helm</author>
            <author>Ralph Johnson</author>
            <author>John Vlissides</author>
            <published>1994</published>
            <price currency="USD">45.99</price>
            <pub:publisher-ref ref="tech-books"/>
        </book>
    </section>
    
    <section name="database">
        <book id="bk201" category="database">
            <title lang="en">Database System Concepts</title>
            <author>Abraham Silberschatz</author>
            <author>Henry F. Korth</author>
            <author>S. Sudarshan</author>
            <published>2019</published>
            <price currency="USD">89.99</price>
            <pub:publisher-ref ref="tech-books"/>
            <!-- This is a comment about the book -->
            <related-books>
                <book-ref id="bk101"/>
                <book-ref id="bk301"/>
            </related-books>
        </book>
    </section>
    
    <appendix>
        <section name="glossary">
            <!-- Glossary content would go here -->
            <term>Normalization</term>
            <definition>A process of organizing data...</definition>
        </section>
    </appendix>
</catalog>
"""

def test_axes():
    # 解析XML
    root = etree.fromstring(xml_data)
    
    # 测试轴表达式
    test_cases = [
        # 树形导航轴
        ("//book[@id='bk101']/ancestor::section", "bk101的section祖先"),
        ("//book[@id='bk101']/descendant::tag", "bk101的所有tag后代"),
        ("//book[@id='bk101']/parent::section", "bk101的section父节点"),
        ("//section[@name='programming']//ancestor-or-self::section", "programming section及其所有section祖先"),
        
        # 文档顺序轴
        ("//book[@id='bk101']/following::book", "bk101之后的所有书籍"),
        ("//book[@id='bk201']/preceding::book", "bk201之前的所有书籍"),
        ("//author[1]/following-sibling::author", "第一个作者之后的所有作者兄弟节点"),
        ("//author[last()]/preceding-sibling::author", "最后一个作者之前的所有作者兄弟节点"),
        
        # 属性和命名空间轴
        ("//book[@id='bk101']/attribute::*", "bk101的所有属性"),
        ("//book[@id='bk101']/namespace::*", "bk101的所有命名空间"),
        
        # 节点类型测试
        ("//book[@id='bk201']/child::comment()", "bk201的注释子节点"),
        ("//section[@name='glossary']/child::text()", "glossary section的文本子节点"),
        
        # 复杂轴查询
        ("//section[@name='database']/book[price = max(ancestor::section/book/price)]", "database section中最贵的书"),
        ("//book[count(author) > 1]/author[1]", "多作者书籍的第一个作者"),
        ("//book[related-books/book-ref]/@id", "所有引用其他书籍的书籍ID"),
        ("//book[@id='bk102']/ancestor-or-self::*", "bk102及其所有祖先节点"),
        ("//section[@name='programming']/*[1]/following-sibling::*", "programming section第一个元素的所有兄弟节点"),
    ]
    
    for xpath_expr, description in test_cases:
        try:
            results = root.xpath(xpath_expr)
            print(f"\nXPath: {xpath_expr}")
            print(f"描述: {description}")
            print(f"结果数量: {len(results)}")
            
            for i, result in enumerate(results[:3], 1):  # 只显示前3个结果
                if isinstance(result, etree._Element):
                    tag = result.tag
                    attrib = result.get('id', result.get('name', result.get('ref', '')))
                    text = result.text.strip() if result.text else "无文本"
                    print(f"  结果{i}: {tag}({attrib})={text}")
                elif isinstance(result, str):
                    print(f"  结果{i}: {result}")
                else:  # 属性
                    print(f"  结果{i}: {result}")
        except Exception as e:
            print(f"\nXPath: {xpath_expr}")
            print(f"描述: {description}")
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_axes()
```

### 3.7.1 轴导航可视化

```python
# code/basic-examples/xpath_axes_visualizer.py
from lxml import etree

def visualize_navigation():
    xml_data = """<?xml version="1.0"?>
<root>
    <section>
        <item id="i1">Content 1</item>
        <item id="i2">Content 2</item>
        <item id="i3">
            <subitem>Subcontent 1</subitem>
            <subitem>Subcontent 2</subitem>
        </item>
    </section>
</root>
"""
    
    root = etree.fromstring(xml_data)
    
    # 选择一个特定元素作为起点
    start_node = root.xpath("//item[@id='i2']")[0]
    print(f"起始节点: {start_node.tag}({start_node.get('id')})")
    print("=" * 50)
    
    # 演示各种轴导航
    navigation_cases = [
        ("parent::*", "父节点"),
        ("ancestor::*", "所有祖先节点"),
        ("ancestor-or-self::*", "自身及所有祖先节点"),
        ("child::*", "所有子节点"),
        ("descendant::*", "所有后代节点"),
        ("descendant-or-self::*", "自身及所有后代节点"),
        ("preceding::*", "文档中当前节点之前的所有元素"),
        ("following::*", "文档中当前节点之后的所有元素"),
        ("preceding-sibling::*", "当前节点之前的所有兄弟节点"),
        ("following-sibling::*", "当前节点之后的所有兄弟节点"),
        ("attribute::*", "所有属性"),
        ("namespace::*", "所有命名空间节点"),
    ]
    
    for xpath_expr, description in navigation_cases:
        try:
            # 使用XPathEvaluator以特定节点为上下文
            context = etree.XPathEvaluator(start_node)
            results = context.evaluate(xpath_expr)
            
            if hasattr(results, '__iter__') and not isinstance(results, str):
                results_list = list(results)
            else:
                results_list = [results]
            
            print(f"\n{description} ({xpath_expr}):")
            if results_list:
                for result in results_list:
                    if isinstance(result, etree._Element):
                        tag = result.tag
                        attrib = result.get('id', result.get('name', ''))
                        text = result.text.strip() if result.text else "无文本"
                        print(f"  - {tag}({attrib})={text}")
                    else:
                        print(f"  - {result}")
            else:
                print("  无结果")
        except Exception as e:
            print(f"\n{description} ({xpath_expr}):")
            print(f"  错误: {str(e)}")

if __name__ == "__main__":
    visualize_navigation()
```

## 3.8 轴与谓语的高级应用

### 3.8.1 轴在复杂查询中的应用

```xpath
# 选择所有在同section中价格高于平均价格的书籍
//book[price > sum(ancestor::section/book/price) div count(ancestor::section/book)]

# 选择所有在同section中出版年份最新的书籍
//book[published = max(ancestor::section/book/published)]

# 选择所有直接或间接引用其他书籍的书籍
//book[descendant::book-ref]

# 选择所有具有同名兄弟节点的元素
//*[count(../*[name() = name(current())]) > 1]

# 选择所有具有相同category属性的兄弟节点
//*[@category and count(../*[@category = current()/@category]) > 1]

# 选择所有在其祖先节点链中包含名为'catalog'的元素的书籍
//book[ancestor::catalog]
```

### 3.8.2 轴在文档比较中的应用

```xpath
# 比较相邻书籍的价格差异
//book[position() > 1][price > preceding-sibling::book[1]/price]

# 比较相邻书籍的出版年份
//book[position() > 1][published > preceding-sibling::book[1]/published]

# 选择所有在其前后兄弟节点中价格居中的书籍
//book[price > preceding-sibling::book[1]/price and price < following-sibling::book[1]/price]

# 选择所有在同section中价格最高的书籍
//section/book[not(following-sibling::book[price > current()/price])]

# 选择所有在同section中价格最低的书籍
//section/book[not(preceding-sibling::book[price < current()/price])]
```

## 3.9 本章小结

本章深入学习了XPath的轴系统和节点测试，包括：

- XPath轴的概念和完整列表
- 树形导航轴（向上、向下）的使用方法
- 文档顺序轴（向前、向后）的使用方法
- 节点测试的各种形式
- 轴的组合使用和复杂查询
- 轴与谓语的高级应用技巧

掌握轴系统是成为XPath专家的关键一步。通过本章学习，您现在能够：

1. 灵活地在XML文档树中导航
2. 从任意节点访问相关节点
3. 编写复杂的XPath查询
4. 解决各种文档导航问题

下一章我们将学习XPath函数，这将进一步增强XPath的表达能力和实用性。

## 3.10 练习

1. 编写XPath表达式选择所有在其section中价格排名第二的书籍
2. 选择所有具有同名兄弟节点的元素，并显示它们的共同名称
3. 选择所有在其前后兄弟节点中价格居中的书籍
4. 选择所有祖先节点中包含名为'catalog'的元素的书籍
5. 选择所有具有相同category属性但不同价格的兄弟节点

尝试在提供的代码示例中验证您的答案。