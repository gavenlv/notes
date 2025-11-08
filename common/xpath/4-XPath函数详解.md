# 第4章：XPath函数详解

## 4.1 XPath函数概述

XPath提供了丰富的内置函数库，这些函数极大地增强了XPath的表达能力和实用性。函数可以用于谓语中、路径表达式中，或者直接返回值。XPath函数分为几个主要类别：节点函数、字符串函数、数值函数、布尔函数和日期时间函数等。

### 4.1.1 函数的基本语法

函数的基本语法格式为：

```
函数名(参数1, 参数2, ...)
```

例如：

```xpath
string-length("Hello World")          # 返回字符串长度
count(//book)                         # 计算book元素的数量
contains(title, "XML")               # 检查title是否包含"XML"
round(3.14159)                        # 四舍五入
```

### 4.1.2 函数的主要分类

| 函数类别 | 描述 | 常用函数 |
|---------|------|---------|
| 节点函数 | 处理节点集 | `position()`, `last()`, `count()`, `local-name()` |
| 字符串函数 | 处理字符串 | `string()`, `concat()`, `substring()`, `contains()` |
| 数值函数 | 处理数字 | `number()`, `sum()`, `floor()`, `ceiling()` |
| 布尔函数 | 处理布尔值 | `boolean()`, `true()`, `false()`, `not()` |
| 其他函数 | 日期时间等 | `lang()`, `generate-id()` |

## 4.2 节点函数

### 4.2.1 基本节点函数

#### position()函数
返回当前节点的位置（基于1的索引）：

```xpath
# 选择前三个book元素
//book[position() <= 3]

# 选择第偶数个book元素
//book[position() mod 2 = 0]

# 选择最后一个book元素
//book[position() = last()]
```

#### last()函数
返回当前上下文中的节点数量：

```xpath
# 选择最后一个book元素
//book[position() = last()]

# 选择倒数第二个book元素
//book[position() = last() - 1]

# 选择位置超过一半的book元素
//book[position() > last() div 2]
```

#### count()函数
计算节点集中节点的数量：

```xpath
# 计算所有book元素的数量
count(//book)

# 计算每个book元素的author子元素数量
//book[count(author) > 1]

# 计算所有section元素的数量
count(//section)
```

### 4.2.2 节点名称和类型函数

#### local-name()函数
返回节点的本地名称（不带命名空间前缀）：

```xpath
# 选择所有本地名称为"book"的元素
//*[local-name() = 'book']

# 选择所有本地名称以"sec"开头的section
//*[starts-with(local-name(), 'sec')]

# 选择所有具有"book"本地名称的元素，不论命名空间
//*[local-name() = 'book']
```

#### namespace-uri()函数
返回节点的命名空间URI：

```xpath
# 选择所有具有特定命名空间的元素
//*[namespace-uri() = 'http://example.com/publisher']

# 选择所有具有命名空间的元素
//*[namespace-uri()]

# 选择所有没有命名空间的元素
//*[not(namespace-uri())]
```

#### name()函数
返回节点的限定名称（包含命名空间前缀）：

```xpath
# 显示所有元素的全限定名
//*[name()]

# 选择所有名称包含冒号的元素（带命名空间前缀）
//*[contains(name(), ':')]

# 选择特定限定名的元素
//*[name() = 'pub:publisher']
```

## 4.3 字符串函数

### 4.3.1 基本字符串函数

#### string()函数
将参数转换为字符串：

```xpath
# 将数值转换为字符串
string(123)          # 返回 "123"

# 将布尔值转换为字符串
string(true())        # 返回 "true"

# 将节点集转换为字符串（第一个节点的字符串值）
string(//book[1])     # 返回第一个book的文本内容

# 检查字符串是否为空
string(//author) != ""    # 检查是否有文本内容
```

#### concat()函数
连接多个字符串：

```xpath
# 连接两个字符串
concat("Hello", " World")    # 返回 "Hello World"

# 连接多个字符串
concat("Title: ", title, " by ", author)

# 构造格式化输出
concat("Book ", position(), ": ", title)
```

### 4.3.2 字符串比较和检查函数

#### contains()函数
检查一个字符串是否包含另一个字符串：

```xpath
# 选择标题包含"XML"的书籍
//book[contains(title, "XML")]

# 选择作者名包含"Martin"的书籍
//book[contains(author, "Martin")]

# 不区分大小写的包含检查
//book[contains(translate(title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'XML')]
```

#### starts-with()和ends-with()函数
检查字符串的起始和结束：

```xpath
# 选择标题以"Clean"开头的书籍
//book[starts-with(title, "Clean")]

# 选择ID以"bk"开头的书籍
//book[starts-with(@id, "bk")]

# 选择文件扩展名为".xml"的资源
//*[ends-with(@filename, ".xml")]  # XPath 2.0+

# 在XPath 1.0中模拟ends-with
//*[substring(@filename, string-length(@filename) - 3) = ".xml"]
```

#### substring-before()和substring-after()函数
获取子字符串之前或之后的部分：

```xpath
# 获取文件名（去除扩展名）
substring-before("document.xml", ".xml")

# 获取文件扩展名
substring-after("document.xml", ".")

# 获取URL中的域名
substring-after("http://example.com/page", "://")
```

### 4.3.3 字符串转换和格式化函数

#### substring()函数
提取子字符串：

```xpath
# 从第1个字符开始，取5个字符
substring("Hello World", 1, 5)    # 返回 "Hello"

# 从第3个字符开始到结尾
substring("Hello World", 3)      # 返回 "llo World"

# 获取ID的后4位
substring(@id, string-length(@id) - 3)
```

#### string-length()函数
获取字符串长度：

```xpath
# 选择标题长度超过20个字符的书籍
//book[string-length(title) > 20]

# 计算标题长度的平均值
sum(//book/string-length(title)) div count(//book)

# 选择短标题的书籍（少于10个字符）
//book[string-length(title) < 10]
```

#### normalize-space()函数
规范化字符串（去除首尾空白，合并内部空白）：

```xpath
# 规范化标题文本
normalize-space(title)

# 选择包含特定关键词的书籍（忽略多余空白）
//book[contains(normalize-space(), "XML")]

# 检查节点是否只包含空白
normalize-space(.) = ""
```

#### translate()函数
转换字符串中的字符：

```xpath
# 不区分大小写的比较
translate(title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') = 'XML'

# 移除特定字符
translate(phone, '-', '')    # 移除电话号码中的连字符

# 转换为小写
translate(title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')
```

## 4.4 数值函数

### 4.4.1 基本数值函数

#### number()函数
将值转换为数字：

```xpath
# 将字符串转换为数字
number("123")         # 返回 123

# 转换包含非数字字符的字符串
number("12.3abc")     # 返回 NaN (Not a Number)

# 将布尔值转换为数字
number(true())        # 返回 1
number(false())       # 返回 0

# 将节点集转换为数字（第一个节点的字符串值）
number(//price)
```

#### sum()函数
计算节点集中所有数字值的总和：

```xpath
# 计算所有书籍的总价
sum(//price)

# 计算每个section中书籍的总价
//section[sum(./price) > 100]

# 计算平均值
sum(//price) div count(//price)
```

### 4.4.2 数学函数

#### floor()、ceiling()和round()函数
向下取整、向上取整和四舍五入：

```xpath
# 向下取整
floor(3.7)           # 返回 3
floor(-3.7)          # 返回 -4

# 向上取整
ceiling(3.2)         # 返回 4
ceiling(-3.2)        # 返回 -3

# 四舍五入
round(3.7)           # 返回 4
round(3.2)           # 返回 3
round(-3.7)          # 返回 -4
```

#### mod()函数
取模运算：

```xpath
# 选择偶数位置的元素
//book[position() mod 2 = 0]

# 选择位置是3的倍数的元素
//book[position() mod 3 = 0]

# 检查奇偶性
position() mod 2 = 1    # 奇数位置
position() mod 2 = 0    # 偶数位置
```

## 4.5 布尔函数

### 4.5.1 基本布尔函数

#### boolean()函数
将值转换为布尔值：

```xpath
# 数字转换为布尔值
boolean(0)          # 返回 false
boolean(123)        # 返回 true

# 字符串转换为布尔值
boolean("")         # 返回 false
boolean("abc")      # 返回 true

# 节点集转换为布尔值
boolean(//book)     # 如果有book元素，返回true
boolean(//book[1])  # 如果第一个book元素存在，返回true
```

#### true()和false()函数
返回布尔值true和false：

```xpath
# 在谓语中使用true()和false()
//book[boolean(price > 50) = true()]

# 显式比较（通常可以省略）
//book[price > 50 = true()]

# 选择没有category属性的book
//book[@category = false()]
```

#### not()函数
逻辑非操作：

```xpath
# 选择没有category属性的book
//book[not(@category)]

# 选择价格不大于50的book
//book[not(price > 50)]

# 选择标题不包含"XML"的book
//book[not(contains(title, "XML"))]
```

## 4.6 其他函数

### 4.6.1 lang()函数
检查节点的语言：

```xml
<!-- 示例XML -->
<book xml:lang="en">
    <title>English Title</title>
</book>
<book xml:lang="fr">
    <title>Titre Français</title>
</book>
```

```xpath
# 选择英语书籍
//book[lang("en")]

# 选择法语书籍
//book[lang("fr")]

# 选择默认语言（xml:lang="en"）的书籍
//book[lang("en")]
```

### 4.6.2 generate-id()函数
为节点生成唯一标识符：

```xpath
# 为每个book生成唯一ID
//book/generate-id()

# 比较两个节点引用是否相同
generate-id(//book[1]) = generate-id(//book[@id='bk101'])

# 检查节点是否重复
//book[count(../book[generate-id() = generate-id(current())]) > 1]
```

## 4.7 函数组合应用

### 4.7.1 复杂查询示例

```xpath
# 选择价格最高且标题最长的书籍
//book[price = max(//book/price) and string-length(title) = max(//book/string-length(title))]

# 选择每个section中最便宜的书籍
//section/book[price = min(../book/price)]

# 选择作者姓名长度超过10个字符的书籍
//book[string-length(author) > 10]

# 选择出版年份与价格总和相同的书籍
//book[published = sum(//price) div count(//price)]

# 选择ID由特定模式组成的书籍
//book[
    starts-with(@id, 'bk') and 
    substring(@id, 3) = translate(string(position() - 1), '0123456789', '0123456789')
]

# 选择在文本中包含"XML"或"JSON"的书籍，不区分大小写
//book[
    contains(
        translate(normalize-space(.), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'XML'
    ) or contains(
        translate(normalize-space(.), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'JSON'
    )
]
```

### 4.7.2 数据分析示例

```xpath
# 计算价格的标准差（近似）
sqrt(
    sum(
        //book[(price - avg) * (price - avg)]
    ) div count(//book)
)

# 选择价格在一个标准差范围内的书籍
//book[
    price >= avg - stddev and 
    price <= avg + stddev
]

# 按标题长度分组（XPath 2.0+）
for $title-length in distinct-values(//book/string-length(title))
return 
    <group length="{$title-length}" count="{count(//book[string-length(title) = $title-length])}"/>

# 选择标题包含数字的书籍
//book[matches(title, '\d+')]  # XPath 2.0+使用正则表达式
//book[translate(title, '0123456789', '') != title]  # XPath 1.0方式
```

## 4.8 实验验证

让我们通过Python代码来验证XPath函数的使用：

```python
# code/basic-examples/xpath_functions_demo.py
from lxml import etree
import math

# 包含各种数据类型的XML文档
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="bk001" category="programming" xml:lang="en">
        <title>Clean Code: A Handbook of Agile Software Craftsmanship</title>
        <author>Robert C. Martin</author>
        <author>Michael C. Martin</author>
        <published>2008</published>
        <price currency="USD">34.99</price>
        <pages>464</pages>
        <tags>
            <tag>programming</tag>
            <tag>best practices</tag>
            <tag>software engineering</tag>
        </tags>
    </book>
    
    <book id="bk002" category="programming" xml:lang="en">
        <title>Design Patterns: Elements of Reusable Object-Oriented Software</title>
        <author>Erich Gamma</author>
        <author>Richard Helm</author>
        <author>Ralph Johnson</author>
        <author>John Vlissides</author>
        <published>1994</published>
        <price currency="USD">45.99</price>
        <pages>395</pages>
        <isbn>978-0201633610</isbn>
    </book>
    
    <book id="bk003" category="database" xml:lang="en">
        <title>Database System Concepts</title>
        <author>Abraham Silberschatz</author>
        <author>Henry F. Korth</author>
        <author>S. Sudarshan</author>
        <published>2019</published>
        <price currency="USD">89.99</price>
        <pages>1104</pages>
        <isbn>978-0078022159</isbn>
    </book>
    
    <book id="bk004" category="web" xml:lang="fr">
        <title>Apprendre XML</title>
        <author>Jean-Michel Dubois</author>
        <published>2020</published>
        <price currency="EUR">32.50</price>
        <pages>312</pages>
    </book>
    
    <book id="bk005" category="data" xml:lang="en">
        <title>Data Science for Business</title>
        <author>Foster Provost</author>
        <author>Tom Fawcett</author>
        <published>2013</published>
        <price currency="USD">32.99</price>
        <pages>388</pages>
    </book>
</catalog>
"""

def test_xpath_functions():
    # 解析XML
    root = etree.fromstring(xml_data)
    
    # 测试节点函数
    print("=" * 50)
    print("节点函数测试")
    print("=" * 50)
    
    node_functions = [
        ("position()", "当前节点位置", "//book[position() = 1]"),
        ("last()", "最后一个节点", "//book[position() = last()]"),
        ("count()", "计算节点数量", "count(//book)"),
        ("local-name()", "本地名称", "//book[local-name() = 'book']"),
        ("name()", "完整名称", "//book[name() = 'book']"),
        ("namespace-uri()", "命名空间URI", "//book[namespace-uri() = '']"),
    ]
    
    for func_name, description, xpath_expr in node_functions:
        results = root.xpath(xpath_expr)
        print(f"\n{func_name}: {description}")
        print(f"XPath: {xpath_expr}")
        if isinstance(results, list):
            print(f"结果: {len(results)} 个节点")
            if results and isinstance(results[0], etree._Element):
                for i, result in enumerate(results[:2], 1):
                    id_attr = result.get('id', '无ID')
                    print(f"  示例{i}: {result.tag}(id={id_attr})")
        else:
            print(f"结果: {results}")
    
    # 测试字符串函数
    print("\n" + "=" * 50)
    print("字符串函数测试")
    print("=" * 50)
    
    string_functions = [
        ("contains()", "包含检查", "//book[contains(title, 'Code')]"),
        ("starts-with()", "前缀检查", "//book[starts-with(@id, 'bk00')]"),
        ("string-length()", "字符串长度", "//book[string-length(title) > 30]"),
        ("substring()", "子字符串", "//book[substring(@id, 3, 3) = '001']"),
        ("concat()", "字符串连接", "concat(//book[1]/title, ' by ', //book[1]/author[1])"),
        ("normalize-space()", "规范化空白", "//book[normalize-space(title) != title]"),
    ]
    
    for func_name, description, xpath_expr in string_functions:
        results = root.xpath(xpath_expr)
        print(f"\n{func_name}: {description}")
        print(f"XPath: {xpath_expr}")
        if isinstance(results, list):
            print(f"结果: {len(results)} 个节点")
            if results and isinstance(results[0], etree._Element):
                for i, result in enumerate(results[:2], 1):
                    id_attr = result.get('id', '无ID')
                    print(f"  示例{i}: {result.tag}(id={id_attr})")
        else:
            print(f"结果: {results}")
    
    # 测试数值函数
    print("\n" + "=" * 50)
    print("数值函数测试")
    print("=" * 50)
    
    numerical_functions = [
        ("sum()", "求和", "sum(//price)"),
        ("count()", "计数", "count(//book)"),
        ("round()", "四舍五入", "round(//price[1])"),
        ("floor()", "向下取整", "floor(//price[1])"),
        ("ceiling()", "向上取整", "ceiling(//price[1])"),
        ("position() mod 2", "奇偶判断", "//book[position() mod 2 = 1]"),
    ]
    
    for func_name, description, xpath_expr in numerical_functions:
        results = root.xpath(xpath_expr)
        print(f"\n{func_name}: {description}")
        print(f"XPath: {xpath_expr}")
        if isinstance(results, list):
            print(f"结果: {len(results)} 个节点")
            if results and isinstance(results[0], etree._Element):
                for i, result in enumerate(results[:2], 1):
                    id_attr = result.get('id', '无ID')
                    print(f"  示例{i}: {result.tag}(id={id_attr})")
        else:
            print(f"结果: {results}")
    
    # 测试布尔函数
    print("\n" + "=" * 50)
    print("布尔函数测试")
    print("=" * 50)
    
    boolean_functions = [
        ("not()", "逻辑非", "//book[not(@category='programming')]"),
        ("boolean()", "布尔转换", "boolean(//book[@id='bk001'])"),
        ("true()", "真值", "//book[price > 30 = true()]"),
        ("false()", "假值", "//book[price < 10 = false()]"),
    ]
    
    for func_name, description, xpath_expr in boolean_functions:
        results = root.xpath(xpath_expr)
        print(f"\n{func_name}: {description}")
        print(f"XPath: {xpath_expr}")
        print(f"结果: {len(results)} 个节点")
        if results and isinstance(results[0], etree._Element):
            for i, result in enumerate(results[:2], 1):
                id_attr = result.get('id', '无ID')
                print(f"  示例{i}: {result.tag}(id={id_attr})")
    
    # 测试高级函数组合
    print("\n" + "=" * 50)
    print("高级函数组合测试")
    print("=" * 50)
    
    advanced_expressions = [
        ("价格最高的书籍", "//book[price = max(//book/price)]"),
        ("作者最多的书籍", "//book[count(author) = max(//book/count(author))]"),
        ("标题最长的书籍", "//book[string-length(title) = max(//book/string-length(title))]"),
        ("价格大于平均值的书籍", "//book[price > sum(//price) div count(//book)]"),
        ("页数与价格比率最佳的书籍", "//book[pages div price = max(//book/pages div price)]"),
        ("多作者且价格合理的书籍", "//book[count(author) > 1 and price < 50]"),
        ("标题中包含冒号的书籍", "//book[contains(title, ':')]"),
        ("价格在30到40之间的书籍", "//book[price >= 30 and price <= 40]"),
    ]
    
    for description, xpath_expr in advanced_expressions:
        results = root.xpath(xpath_expr)
        print(f"\n{description}")
        print(f"XPath: {xpath_expr}")
        print(f"结果: {len(results)} 个节点")
        if results and isinstance(results[0], etree._Element):
            for i, result in enumerate(results, 1):
                id_attr = result.get('id', '无ID')
                title = result.xpath('title/text()')[0]
                print(f"  {i}. {result.tag}(id={id_attr}) - {title}")

if __name__ == "__main__":
    test_xpath_functions()
```

### 4.8.1 函数性能测试

```python
# code/basic-examples/xpath_functions_performance.py
import time
from lxml import etree

def test_function_performance():
    # 生成大型XML文档
    large_xml = "<catalog>"
    for i in range(1000):
        price = 10 + (i % 100)
        year = 1990 + (i % 30)
        title = f"{'ABCDEFGHIJKLMN'[: (i % 10) + 5]} {'XYZ'[: (i % 3) + 1]} Book"
        large_xml += f"""
        <book id="bk{i:04d}" category="category{i % 10}">
            <title>{title}</title>
            <author>Author {i % 100}</author>
            <published>{year}</published>
            <price>{price:.2f}</price>
            <pages>{200 + (i % 500)}</pages>
        </book>
        """
    large_xml += "</catalog>"
    
    # 解析XML
    root = etree.fromstring(large_xml)
    
    # 测试不同函数的性能
    test_cases = [
        ("count()函数", "count(//book)"),
        ("sum()函数", "sum(//price)"),
        ("max()函数", "max(//price)"),
        ("contains()函数", "//book[contains(title, 'XYZ')]"),
        ("string-length()函数", "//book[string-length(title) > 10]"),
        ("position()和last()函数", "//book[position() = last() - 1]"),
        ("starts-with()函数", "//book[starts-with(@id, 'bk00')]"),
        ("复杂组合", "//book[price > 20 and price < 50 and contains(title, 'ABC')]"),
    ]
    
    print("XPath函数性能比较:")
    print("-" * 70)
    
    for func_name, xpath_expr in test_cases:
        # 多次运行取平均值
        total_time = 0
        iterations = 10
        
        for _ in range(iterations):
            start_time = time.time()
            results = root.xpath(xpath_expr)
            end_time = time.time()
            total_time += (end_time - start_time)
        
        avg_time = (total_time / iterations) * 1000  # 转换为毫秒
        result_count = len(results) if isinstance(results, list) else 1
        
        print(f"{func_name:<25} | 结果数: {result_count:<4} | 平均耗时: {avg_time:.4f}ms")

if __name__ == "__main__":
    test_function_performance()
```

## 4.9 本章小结

本章详细介绍了XPath的各种内置函数，包括：

- 节点函数：`position()`, `last()`, `count()`, `local-name()`等
- 字符串函数：`string()`, `concat()`, `contains()`, `substring()`等
- 数值函数：`number()`, `sum()`, `floor()`, `ceiling()`等
- 布尔函数：`boolean()`, `true()`, `false()`, `not()`等
- 其他函数：`lang()`, `generate-id()`等

掌握XPath函数可以极大地增强您的查询能力，使您能够：

1. 执行复杂的数据筛选和分析
2. 进行字符串处理和转换
3. 实现数值计算和比较
4. 构建动态的、条件化的查询
5. 处理各种数据类型的转换

下一章我们将学习XPath的高级应用技巧，包括如何处理命名空间、使用XPath 2.0/3.0的新特性以及解决实际问题的策略。

## 4.10 练习

1. 编写XPath表达式选择所有价格在平均值以上且标题长度超过20个字符的书籍
2. 选择所有作者姓名长度大于其书籍ID数字部分的书籍
3. 选择所有在2000年后出版且价格低于平均价格的书籍
4. 选择所有标题包含冒号且页数大于400的书籍
5. 选择所有页数与价格比率最高的书籍

尝试在提供的代码示例中验证您的答案。