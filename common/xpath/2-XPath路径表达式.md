# 第2章：XPath路径表达式

## 2.1 路径表达式概述

XPath路径表达式是XPath的核心功能，用于在XML文档中定位节点。路径表达式类似于文件系统的路径，但更加灵活和强大。

### 2.1.1 路径表达式的组成

路径表达式由以下部分组成：

1. **轴（Axis）**：定义相对于当前节点的节点集合
2. **节点测试（Node Test）**：筛选轴中的节点
3. **谓语（Predicate）**：进一步筛选节点集（可选）

```
轴名称::节点测试[谓语]
```

### 2.1.2 路径表达式的两种形式

1. **绝对路径**：从根节点开始，以`/`开头
2. **相对路径**：从当前节点开始，不以`/`开头

## 2.2 基本路径操作符

### 2.2.1 斜杠操作符

```xpath
# 绝对路径 - 从根节点开始
/bookstore/book/title

# 相对路径 - 从当前节点开始
./title
# 或者直接写
title

# 分隔符 - 表示层级关系
bookstore/book/title

# 双斜杠 - 在文档任意层级查找
//title  # 在文档任何位置查找title元素
```

### 2.2.2 简写语法

XPath提供了简写语法来简化常用操作：

| 简写 | 完整语法 | 描述 |
|------|---------|------|
| `@attr` | `attribute::attr` | 选择属性 |
| `//` | `/descendant-or-self::node()/` | 选择后代节点 |
| `.` | `self::node()` | 当前节点 |
| `..` | `parent::node()` | 父节点 |
| `*` | `child::*` | 所有子元素 |
| `child::` | `child::` | 子轴（可省略） |

## 2.3 节点选择与筛选

### 2.3.1 基本选择

```xpath
# 选择所有book元素
//book

# 选择所有title元素
//title

# 选择bookstore的直接子元素book
/bookstore/book

# 选择所有名为book的元素，不论在文档中的位置
//book
```

### 2.3.2 位置筛选

```xpath
# 第一个book元素
/bookstore/book[1]

# 最后一个book元素
/bookstore/book[last()]

# 前两个book元素
/bookstore/book[position() < 3]

# 倒数第二个book元素
/bookstore/book[position() = last() - 1]

# 第2、4、6个book元素
/bookstore/book[position() mod 2 = 0]
```

### 2.3.3 条件筛选

```xpath
# 选择category属性为'web'的book元素
//book[@category='web']

# 选择价格大于35的book元素
//book[price > 35]

# 选择标题包含'XML'的book元素
//book[contains(title, 'XML')]

# 选择有多个作者的book元素
//book[count(author) > 1]

# 选择category属性不为空的book元素
//book[@category]
```

## 2.4 组合路径表达式

### 2.4.1 路径联合（|操作符）

```xpath
# 选择所有title和author元素
//title | //author

# 选择所有price大于30的book或category为'children'的book
//book[price > 30] | //book[@category='children']
```

### 2.4.2 复杂条件组合

```xpath
# 选择category为web且价格在30-50之间的book
//book[@category='web' and price > 30 and price < 50]

# 选择category为web或children，且价格不大于40的book
//book[(@category='web' or @category='children') and price <= 40]

# 选择2003年或2005年出版的书，且价格不高于40
//book[(year = 2003 or year = 2005) and price <= 40]
```

## 2.5 高级路径表达式

### 2.5.1 位置与条件结合

```xpath
# 选择category为'web'的book中价格最低的
//book[@category='web'][price = min(//book[@category='web']/price)]

# 选择价格排名前3的book
//book[price >= max(substring-before(substring-after(//book/price, ''), '') - 2)]

# 选择价格高于平均价格的book
//book[price > sum(//book/price) div count(//book)]
```

### 2.5.2 嵌套路径

```xpath
# 选择所有价格高于其兄弟节点的book
/bookstore/book[price > ../book/price]

# 选择包含"XML"标题的book，并选择其作者
//book[contains(title, 'XML')]/author

# 选择第二个作者名为特定值的book
//book[author[2] = 'James McGovern']
```

## 2.6 路径表达式实战

让我们使用一个更复杂的XML文档来演示路径表达式：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<library>
    <section id="fiction">
        <section name="science-fiction">
            <book id="bk001" category="scifi">
                <title lang="en">Dune</title>
                <author>Frank Herbert</author>
                <published>1965</published>
                <price currency="USD">12.99</price>
                <reviews>
                    <review rating="5">Excellent sci-fi classic!</review>
                    <review rating="4">A bit complex but rewarding.</review>
                </reviews>
            </book>
            <book id="bk002" category="scifi">
                <title lang="en">Neuromancer</title>
                <author>William Gibson</author>
                <published>1984</published>
                <price currency="USD">14.99</price>
            </book>
        </section>
        <section name="fantasy">
            <book id="bk003" category="fantasy">
                <title lang="en">The Hobbit</title>
                <author>J.R.R. Tolkien</author>
                <published>1937</published>
                <price currency="USD">15.99</price>
                <series>The Lord of the Rings</series>
            </book>
        </section>
    </section>
    <section id="non-fiction">
        <section name="technology">
            <book id="bk004" category="tech">
                <title lang="en">Clean Code</title>
                <author>Robert C. Martin</author>
                <published>2008</published>
                <price currency="USD">34.99</price>
                <tags>
                    <tag>programming</tag>
                    <tag>software engineering</tag>
                </tags>
            </book>
        </section>
    </section>
</library>
```

### 2.6.1 复杂路径表达式示例

```xpath
# 选择所有深度为3的section元素
//section[count(ancestor::*) = 2]

# 选择所有具有series属性的book
//book[series]

# 选择所有具有reviews子元素的book
//book[reviews]

# 选择所有currency属性为USD的price元素
//price[@currency='USD']

# 选择所有rating属性大于4的review元素
//review[@rating > 4]

# 选择所有包含多个tag的book
//book[count(tags/tag) > 1]

# 选择id以"bk"开头的book元素
//book[starts-with(@id, 'bk')]

# 选择title包含"Code"的book
//book[contains(title, 'Code')]

# 选择所有在2000年后出版的书
//book[published > 2000]

# 选择所有价格在20到40美元之间的书
//book[price[@currency='USD'] > 20 and price[@currency='USD'] < 40]
```

## 2.7 实验验证

让我们通过Python代码来验证上述路径表达式：

```python
# code/basic-examples/xpath_path_expressions.py
from lxml import etree

# 复杂XML文档
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<library>
    <section id="fiction">
        <section name="science-fiction">
            <book id="bk001" category="scifi">
                <title lang="en">Dune</title>
                <author>Frank Herbert</author>
                <published>1965</published>
                <price currency="USD">12.99</price>
                <reviews>
                    <review rating="5">Excellent sci-fi classic!</review>
                    <review rating="4">A bit complex but rewarding.</review>
                </reviews>
            </book>
            <book id="bk002" category="scifi">
                <title lang="en">Neuromancer</title>
                <author>William Gibson</author>
                <published>1984</published>
                <price currency="USD">14.99</price>
            </book>
        </section>
        <section name="fantasy">
            <book id="bk003" category="fantasy">
                <title lang="en">The Hobbit</title>
                <author>J.R.R. Tolkien</author>
                <published>1937</published>
                <price currency="USD">15.99</price>
                <series>The Lord of the Rings</series>
            </book>
        </section>
    </section>
    <section id="non-fiction">
        <section name="technology">
            <book id="bk004" category="tech">
                <title lang="en">Clean Code</title>
                <author>Robert C. Martin</author>
                <published>2008</published>
                <price currency="USD">34.99</price>
                <tags>
                    <tag>programming</tag>
                    <tag>software engineering</tag>
                </tags>
            </book>
        </section>
    </section>
</library>
"""

def test_path_expressions():
    # 解析XML
    root = etree.fromstring(xml_data)
    
    # 测试路径表达式
    expressions = [
        ("//section[count(ancestor::*) = 2]", "所有深度为3的section元素"),
        ("//book[series]", "所有具有series属性的book"),
        ("//book[reviews]", "所有具有reviews子元素的book"),
        ("//price[@currency='USD']", "所有currency属性为USD的price元素"),
        ("//review[@rating > 4]", "所有rating属性大于4的review元素"),
        ("//book[count(tags/tag) > 1]", "包含多个tag的book"),
        ("//book[starts-with(@id, 'bk')]", "id以'bk'开头的book元素"),
        ("//book[contains(title, 'Code')]", "title包含'Code'的book"),
        ("//book[published > 2000]", "2000年后出版的书"),
        ("//book[price[@currency='USD'] > 20 and price[@currency='USD'] < 40]", "价格20-40美元的书")
    ]
    
    for xpath_expr, description in expressions:
        results = root.xpath(xpath_expr)
        print(f"\nXPath: {xpath_expr}")
        print(f"描述: {description}")
        print(f"结果数量: {len(results)}")
        for i, result in enumerate(results[:3], 1):  # 只显示前3个结果
            if isinstance(result, etree._Element):
                id_attr = result.get('id', '无ID')
                text_content = result.text.strip() if result.text else "无文本内容"
                print(f"  结果{i}: {result.tag}(id={id_attr})={text_content}")
```

### 2.7.1 路径表达式性能测试

```python
# code/basic-examples/xpath_performance_test.py
import time
from lxml import etree

def compare_xpath_performance():
    # 生成大型XML文档
    large_xml = """
    <catalog>
        <products>
    """
    
    for i in range(1000):
        large_xml += f"""
            <product id="p{i:04d}">
                <name>Product {i}</name>
                <price>{i * 0.99 + 10.00:.2f}</price>
                <category>Category {i % 10}</category>
                <available>{'true' if i % 5 != 0 else 'false'}</available>
            </product>
        """
    
    large_xml += """
        </products>
    </catalog>
    """
    
    # 解析XML
    root = etree.fromstring(large_xml)
    
    # 不同的XPath表达式
    test_cases = [
        ("//product", "所有product元素"),
        ("//product[@id='p0500']", "特定ID的product"),
        ("//product[price > 500]", "价格大于500的product"),
        ("//product[position() < 10]", "前10个product"),
        ("//product[category='Category 3']", "特定类别的product")
    ]
    
    print("XPath表达式性能比较:")
    print("-" * 60)
    
    for xpath_expr, description in test_cases:
        start_time = time.time()
        results = root.xpath(xpath_expr)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # 转换为毫秒
        print(f"{description:<30} | 结果数: {len(results):<4} | 耗时: {execution_time:.4f}ms")

if __name__ == "__main__":
    compare_xpath_performance()
```

## 2.8 路径表达式最佳实践

### 2.8.1 性能优化原则

1. **使用具体的节点名称而非通配符**
   ```xpath
   # 好的做法
   //book/title
   # 不好的做法
   //*/title
   ```

2. **优先使用绝对路径**
   ```xpath
   # 好的做法
   /library/section/book/title
   # 不好的做法
   //title
   ```

3. **避免过度使用`//`**
   ```xpath
   # 好的做法
   /library/section[@id='fiction']//book
   # 不好的做法
   //book
   ```

4. **尽量减少谓语数量**
   ```xpath
   # 好的做法
   //book[@category='scifi' and price > 13]
   # 不好的做法
   //book[@category='scifi'][price > 13]
   ```

### 2.8.2 可读性建议

1. **使用有意义的变量名和注释**
   ```xpath
   /*  选择价格高于平均值的书籍
       先计算平均价格，再筛选
   */
   //book[price > sum(//book/price) div count(//book)]
   ```

2. **复杂表达式分解**
   ```xpath
   # 复杂表达式
   //book[price > 30 and @category='web' and year > 2000]
   
   # 可分解为：
   # 1. //book[@category='web']
   # 2. //book[price > 30]
   # 3. //book[year > 2000]
   # 然后根据具体需求组合
   ```

## 2.9 本章小结

本章深入学习了XPath路径表达式，包括：

- 路径表达式的组成部分和基本语法
- 节点选择与筛选的各种方法
- 位置筛选和条件筛选技巧
- 组合路径表达式的方法
- 复杂路径表达式的构建
- 路径表达式的性能比较和优化

通过本章学习，您应该能够编写复杂的XPath表达式来精确选择XML文档中的节点。下一章我们将深入研究XPath的轴系统，这将使您能够更加灵活地遍历XML文档树。

## 2.10 练习

1. 编写XPath表达式选择所有具有多个作者的书籍
2. 选择所有价格高于平均价格的书籍
3. 选择所有在2000年后出版且价格低于20美元的书籍
4. 选择所有具有标签(tags)且标签包含"programming"的书籍
5. 选择所有评论评分高于平均值的书籍

尝试在提供的代码示例中验证您的答案。