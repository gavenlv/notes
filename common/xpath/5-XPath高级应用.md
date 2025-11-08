# 第5章：XPath高级应用

## 5.1 高级路径表达式

### 5.1.1 复杂路径组合

#### 多级谓语嵌套

XPath谓语可以嵌套多层，实现复杂的筛选逻辑：

```xpath
# 选择价格高于所有编程书籍平均价格的非编程书籍
//book[@category!='programming' and price > sum(//book[@category='programming']/price) div count(//book[@category='programming'])]

# 选择作者数量最多且价格在中间范围（排除最高和最低20%）的书籍
//book[
    count(author) = max(//book/count(author)) and 
    price > (min(//book/price) + (max(//book/price) - min(//book/price)) * 0.2) and 
    price < (max(//book/price) - (max(//book/price) - min(//book/price)) * 0.2)
]

# 选择每个section中价格排名第二的书籍
//section/book[
    price = max(
        ../book[
            price != max(../book/price)
        ]/price
    )
]
```

#### 条件路径选择

使用条件路径实现动态路径选择：

```xpath
# 如果存在isbn元素，则选择isbn，否则选择id
//book/(isbn | @id)[1]

# 选择书籍的标识符（优先顺序：isbn > id > position()）
//book[
    isbn | 
    @id | 
    concat('position-', position())
][1]

# 动态属性选择
//book[@*[starts-with(name(), 'data-')]]  # 选择具有data-前缀属性的书籍
```

### 5.1.2 高级节点选择

#### 基于内容的节点选择

```xpath
# 选择标题中包含价格信息的书籍
//book[contains(translate(title, '$', ''), //book[1]/price)]

# 选择作者名与书籍部分标题相同的书籍
//book[contains(title, author)]

# 选择出版年份与页数相同的书籍
//book[published = pages]

# 选择价格与页数有特定比例关系的书籍
//book[pages div price > 10]  # 页数与价格比率大于10的书籍
```

#### 基于结构的节点选择

```xpath
# 选择具有完整元数据（title, author, price, published）的书籍
//book[count(*) = 4 and title and author and price and published]

# 选择具有多作者且包含副标题的书籍（假设副标题在title中用冒号分隔）
//book[count(author) > 1 and contains(title, ':')]

# 选择具有不规则结构的书籍（缺少必要字段）
//book[
    not(title) or 
    not(author) or 
    not(price) or 
    not(published)
]

# 选择具有深层嵌套结构的书籍
//book[.//*/*]
```

## 5.2 变量与计算

### 5.2.1 XPath 1.0中的变量模拟

XPath 1.0本身不支持变量，但可以通过一些技巧模拟变量效果：

```xpath
# 使用函数调用模拟常量
//book[price > sum(//price) div count(//book)]  # 价格高于平均值

# 使用嵌套查询避免重复计算
//section[
    . = max(//section/book/price) and
    ./book[price = max(../book/price)]
]

# 使用相对路径避免绝对路径
//section/book[
    price = max(../book/price)  # 相对于当前section
]
```

### 5.2.2 XPath 2.0+的变量支持

XPath 2.0引入了变量支持，使表达式更加清晰和可维护：

```xpath
# 使用let绑定变量
let $avg-price := avg(//book/price)
return //book[price > $avg-price]

# 复杂变量计算
let $books := //book
let $categories := distinct-values($books/@category)
return 
    for $cat in $categories
    return 
        <category name="{$cat}">
            {$books[@category=$cat]}
        </category>

# 多变量绑定
let $max-price := max(//book/price)
let $min-price := min(//book/price)
let $price-range := $max-price - $min-price
return 
    //book[
        price > $min-price + $price-range * 0.3 and 
        price < $max-price - $price-range * 0.3
    ]
```

## 5.3 高级字符串处理

### 5.3.1 正则表达式（XPath 2.0+）

XPath 2.0引入了正则表达式支持，大大增强了字符串处理能力：

```xpath
# 检查ISBN格式（10位或13位）
//book[matches(isbn, '^(\d{10}|\d{13})$')]

# 检查邮箱格式
//author[matches(email, '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$')]

# 提取价格数字
//book[replace(price, '[^\d.]', '') cast as xs:decimal > 50]

# 检查标题中的数字
//book[matches(title, '\d+')]

# 提取标题中的单词
//book/tokenize(title, '\s+')
```

### 5.3.2 高级字符串操作

```xpath
# 移除所有非字母数字字符
//book[replace(title, '[^a-zA-Z0-9]', '')]

# 标准化标题（转换为小写并移除标点）
//book[
    lower-case(translate(title, '.,;!?', '    '))
]

# 检查标题中的重复单词
//book[matches(title, '\b(\w+)\b.*\b\1\b')]

# 提取价格范围中的最小和最大值
//book[
    let $prices := tokenize(price, '-'),
        $min := number($prices[1]),
        $max := number($prices[2])
    return $max > 50
]

# 分割和合并字符串
//book[
    string-join(
        for $word in tokenize(title, '\s+') 
        return upper-case(substring($word, 1, 1)) || lower-case(substring($word, 2)),
        ' '
    )
]
```

## 5.4 高级数值计算

### 5.4.1 统计计算

```xpath
# 计算标准差（XPath 2.0+）
let $prices := //book/price,
    $avg := avg($prices),
    $variance := sum(
        for $p in $prices 
        return ($p - $avg) * ($p - $avg)
    ) div count($prices)
return sqrt($variance)

# 计算中位数
let $prices := sort(//book/price),
    $count := count($prices),
    $mid := $count idiv 2
return 
    if ($count mod 2 = 0) 
    then ($prices[$mid] + $prices[$mid + 1]) div 2
    else $prices[$mid + 1]

# 计算四分位数
let $prices := sort(//book/price),
    $count := count($prices),
    $q1-index := $count idiv 4 + 1,
    $q2-index := $count idiv 2 + 1,
    $q3-index := $count * 3 idiv 4 + 1
return 
    <quartiles>
        <q1>{$prices[$q1-index]}</q1>
        <q2>{$prices[$q2-index]}</q2>
        <q3>{$prices[$q3-index]}</q3>
    </quartiles>
```

### 5.4.2 高级数值操作

```xpath
# 价格分组统计
for $book in //book
let $price-range := 
    if ($book/price < 20) then "low"
    else if ($book/price < 50) then "medium"
    else "high"
group by $price-range
return 
    <price-range category="{$price-range}" count="{count($book)}"/>

# 年代分布统计
for $book in //book
let $decade := floor($book/published div 10) * 10
group by $decade
return 
    <decade years="{$decade}s" count="{count($book)}"/>

# 计算复合指标（价格与页数的综合评分）
//book[
    let $price-score := 50 - price,  # 价格越低分数越高
        $pages-score := pages div 20,  # 每20页得1分
        $total-score := $price-score + $pages-score
    return $total-score
]
```

## 5.5 高级布尔逻辑

### 5.5.1 复杂条件组合

```xpath
# 多重嵌套条件
//book[
    (@category = 'programming' and price < 50) or
    (@category = 'database' and published > 2010) or
    (count(author) > 2 and price < 70)
]

# 条件中的条件
//book[
    if (@category = 'programming')
    then price < 50
    else if (@category = 'database')
         then published > 2010
         else price < 70
]

# 逻辑异或实现（XPath中没有直接的XOR操作）
//book[
    (price > 50 and not(published > 2005)) or 
    (not(price > 50) and published > 2005)
]

# 条件存在性检查
//book[
    (isbn and matches(isbn, '^\d{10}$')) or
    (not(isbn) and published > 2000)
]
```

### 5.5.2 动态条件构建

```xpath
# 基于用户输入的动态查询（概念）
let $category := $user-input/category,
    $min-price := $user-input/min-price,
    $max-price := $user-input/max-price
return 
    //book[
        (not($category) or @category = $category) and
        (not($min-price) or price >= $min-price) and
        (not($max-price) or price <= $max-price)
    ]

# 多条件组合生成
let $conditions := (
    if ($user-input/category) then concat('@category = "', $user-input/category, '"') else "",
    if ($user-input/min-price) then concat('price >= ', $user-input/min-price) else "",
    if ($user-input/max-price) then concat('price <= ', $user-input/max-price) else ""
)
return 
    //book[concat(string-join($conditions, ' and '))]
```

## 5.6 高级节点操作

### 5.6.1 节点集运算

```xpath
# 节点集交集（同时属于两个集合的节点）
let $cheap-books := //book[price < 30],
    $programming-books := //book[@category = 'programming']
return $cheap-books[count(. | $programming-books) = count($programming-books)]

# 节点集差集（属于第一个集但不属于第二个集的节点）
let $all-books := //book,
    $expensive-books := //book[price > 50]
return $all-books[not(. | $expensive-books = $expensive-books)]

# 节点集并集
//author | //publisher

# 节点集对称差集（属于两个集之一但不属于两者的节点）
let $category1-books := //book[@category = 'programming'],
    $category2-books := //book[@category = 'database']
return (
    $category1-books[not(. | $category2-books = $category2-books)] |
    $category2-books[not(. | $category1-books = $category1-books)]
)
```

### 5.6.2 节点重组与转换

```xpath
# 按类别分组
for $book in //book
group by $category := $book/@category
return 
    <category name="{$category}">
        {$book}
    </category>

# 构建新的文档结构
<books>
    {
        for $book in //book
        return 
            <book id="{$book/@id}">
                <title>{$book/title}</title>
                <authors>
                    {
                        for $author in $book/author
                        return <author>{$author}</author>
                    }
                </authors>
                <price currency="{$book/price/@currency}">
                    {$book/price/text()}
                </price>
            </book>
    }
</books>

# 创建摘要信息
<summary>
    <total-books>{count(//book)}</total-books>
    <categories>{count(distinct-values(//book/@category))}</categories>
    <authors>{count(distinct-values(//author))}</authors>
    <price-range>
        <min>{min(//book/price)}</min>
        <max>{max(//book/price)}</max>
        <average>{avg(//book/price)}</average>
    </price-range>
</summary>
```

## 5.7 高级应用场景

### 5.7.1 XML文档分析

```xpath
# 文档结构分析
let $elements := //*
return 
    <structure-analysis>
        <total-elements>{count($elements)}</total-elements>
        <unique-elements>{count(distinct-values($elements/name()))}</unique-elements>
        <max-depth>
            {
                max(
                    for $elem in $elements
                    return count($elem/ancestor-or-self::*)
                )
            }
        </max-depth>
        <elements-without-children>
            {
                count($elements[not(*)])
            }
        </elements-without-children>
        <elements-with-attributes>
            {
                count($elements[@*])
            }
        </elements-with-attributes>
    </structure-analysis>

# 属性使用分析
let $attributes := //@*
return 
    <attribute-analysis>
        <total-attributes>{count($attributes)}</total-attributes>
        <unique-attributes>{count(distinct-values($attributes/name()))}</unique-attributes>
        <attribute-frequencies>
            {
                for $attr-name in distinct-values($attributes/name())
                let $attr-count := count($attributes[name() = $attr-name])
                order by $attr-count descending
                return 
                    <attribute name="{$attr-name}" count="{$attr-count}"/>
            }
        </attribute-frequencies>
    </attribute-analysis>

# 文本内容分析
let $text-nodes := //text()[normalize-space()]
return 
    <text-analysis>
        <total-text-nodes>{count($text-nodes)}</total-text-nodes>
        <total-characters>{sum(string-length($text-nodes))}</total-characters>
        <average-text-length>
            {
                sum(string-length($text-nodes)) div count($text-nodes)
            }
        </average-text-length>
        <empty-text-nodes>
            {
                count(//text()[not(normalize-space())])
            }
        </empty-text-nodes>
    </text-analysis>
```

### 5.7.2 数据质量检查

```xpath
# 检查数据完整性
<quality-checks>
    <missing-required-fields>
        {
            //book[
                not(title) or 
                not(author) or 
                not(price) or 
                not(published)
            ]
        }
    </missing-required-fields>
    
    <invalid-isbn-formats>
        {
            //book[
                isbn and 
                not(matches(isbn, '^(\d{10}|\d{13})$'))
            ]
        }
    </invalid-isbn-formats>
    
    <unreasonable-prices>
        {
            //book[
                price < 5 or 
                price > 500
            ]
        }
    </unreasonable-prices>
    
    <future-publication-dates>
        {
            //book[published > year-from-date(current-date())]
        }
    </future-publication-dates>
    
    <duplicate-isbns>
        {
            for $isbn in distinct-values(//book/isbn)
            let $books-with-isbn := //book[isbn = $isbn]
            where count($books-with-isbn) > 1
            return 
                <duplicate-isbn isbn="{$isbn}">
                    {$books-with-isbn}
                </duplicate-isbn>
        }
    </duplicate-isbns>
</quality-checks>

# 数据一致性检查
<consistency-checks>
    <price-currency-consistency>
        {
            //book[
                price/@currency and 
                not(price/@currency = preceding::book[1]/price/@currency) and
                not(preceding::book[1]/price/@currency)
            ]
        }
    </price-currency-consistency>
    
    <author-name-consistency>
        {
            for $author in //author
            let $variations := //author[normalize-space(.) = normalize-space($author)]
            where count($variations) > 1
            return 
                <author-variations name="{normalize-space($author)}">
                    {$variations}
                </author-variations>
        }
    </author-name-consistency>
</consistency-checks>
```

## 5.8 实验验证

让我们通过Python代码来验证XPath的高级应用：

```python
# code/basic-examples/xpath_advanced_demo.py
from lxml import etree
import re

# 复杂XML文档，包含各种数据质量问题
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns="http://example.com/catalog">
    <!-- 书籍目录 -->
    <book id="bk001" category="programming">
        <title>Clean Code: A Handbook of Agile Software Craftsmanship</title>
        <author>Robert C. Martin</author>
        <author>Uncle Bob</author>  <!-- 同一作者的别名 -->
        <published>2008</published>
        <price currency="USD">34.99</price>
        <pages>464</pages>
        <isbn>978-0132350884</isbn>
        <tags>
            <tag>programming</tag>
            <tag>best practices</tag>
        </tags>
    </book>
    
    <book id="bk002" category="programming">
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
    
    <book id="bk003" category="database">
        <title>Database System Concepts</title>
        <author>Abraham Silberschatz</author>
        <author>Henry F. Korth</author>
        <author>S. Sudarshan</author>
        <published>2019</published>
        <price currency="USD">89.99</price>
        <pages>1104</pages>
        <isbn>978-0078022159</isbn>
    </book>
    
    <!-- 数据质量问题示例 -->
    <book id="bk004" category="web">
        <!-- 缺少作者 -->
        <title>Learning Web Design</title>
        <published>2021</published>
        <price currency="USD">45.00</price>
        <!-- 缺少页数 -->
    </book>
    
    <book id="bk005" category="fiction">
        <title>The Great Novel</title>
        <author>Famous Author</author>
        <published>2025</published> <!-- 未来日期 -->
        <price currency="USD">3.99</price> <!-- 不合理的低价 -->
        <pages>25</pages> <!-- 过少的页数 -->
    </book>
    
    <book id="bk006" category="programming">
        <title>Advanced Python Programming</title>
        <author>John Smith</author>
        <published>2020</published>
        <price currency="EUR">35.00</price> <!-- 货币不一致 -->
        <pages>512</pages>
        <isbn>1234567890</isbn> <!-- 缺少连字符的ISBN -->
    </book>
    
    <book id="bk007" category="data">
        <title>Data Science Essentials</title>
        <author>Jane Doe</author>
        <author>John Smith</author> <!-- 重复作者 -->
        <published>2022</published>
        <price currency="USD">60.00</price>
        <pages>450</pages>
        <!-- 缺少ISBN -->
    </book>
</catalog>
"""

def test_advanced_xpath():
    # 解析XML并处理命名空间
    root = etree.fromstring(xml_data)
    ns = {'c': 'http://example.com/catalog'}
    
    print("=" * 60)
    print("XPath高级应用演示")
    print("=" * 60)
    
    # 1. 高级路径表达式
    print("\n1. 高级路径表达式")
    print("-" * 40)
    
    tests = [
        ("多作者且价格合理的编程书籍", "//c:book[@category='programming' and count(c:author) > 1 and number(c:price) < 50]"),
        ("页数与价格比率最高的书籍", "//c:book[number(c:pages) div number(c:price) = max(//c:book[number(c:pages) div number(c:price)])]"),
        ("标题包含冒号的多作者书籍", "//c:book[contains(c:title, ':') and count(c:author) > 1]"),
        ("出版年份与页数相等的书籍", "//c:book[number(c:published) = number(c:pages)]"),
        ("价格高于平均值的非编程书籍", "//c:book[@category!='programming' and number(c:price) > sum(//c:book[number(c:price)]/c:price) div count(//c:book[number(c:price)])]"),
    ]
    
    for description, xpath_expr in tests:
        results = root.xpath(xpath_expr, namespaces=ns)
        print(f"\n{description}")
        print(f"XPath: {xpath_expr}")
        print(f"结果: {len(results)} 个节点")
        for book in results:
            book_id = book.get('id')
            title = book.xpath('string(c:title)', namespaces=ns)
            print(f"  - {book_id}: {title}")
    
    # 2. 数据质量检查
    print("\n\n2. 数据质量检查")
    print("-" * 40)
    
    quality_checks = [
        ("缺少必要字段的书籍", "//c:book[not(c:title) or not(c:author) or not(c:price) or not(c:published)]"),
        ("具有未来出版日期的书籍", f"//c:book[number(c:published) > {2023}]"),
        ("价格过低的书籍", "//c:book[number(c:price) < 10]"),
        ("页数过少的书籍", "//c:book[number(c:pages) and number(c:pages) < 50]"),
        ("缺少ISBN的书籍", "//c:book[@category='programming' and not(c:isbn)]"),
    ]
    
    for description, xpath_expr in quality_checks:
        results = root.xpath(xpath_expr, namespaces=ns)
        print(f"\n{description}")
        print(f"XPath: {xpath_expr}")
        print(f"结果: {len(results)} 个节点")
        for book in results:
            book_id = book.get('id')
            title = book.xpath('string(c:title)', namespaces=ns)
            print(f"  - {book_id}: {title}")
    
    # 3. 数据分析查询
    print("\n\n3. 数据分析查询")
    print("-" * 40)
    
    analysis_queries = [
        ("书籍总数", "count(//c:book)"),
        ("平均价格", "sum(//c:book[number(c:price)]/c:price) div count(//c:book[number(c:price)])"),
        ("最高价格", "max(//c:book[number(c:price)]/c:price)"),
        ("最低价格", "min(//c:book[number(c:price)]/c:price)"),
        ("平均页数", "sum(//c:book[number(c:pages)]/c:pages) div count(//c:book[number(c:pages)])"),
        ("作者最多的书籍", "//c:book[count(c:author) = max(//c:book/count(c:author))]"),
        ("作者总数", "count(distinct-values(//c:author/text()))"),
        ("类别总数", "count(distinct-values(//c:book/@category))"),
    ]
    
    for description, xpath_expr in analysis_queries:
        try:
            result = root.xpath(xpath_expr, namespaces=ns)
            print(f"\n{description}")
            print(f"XPath: {xpath_expr}")
            print(f"结果: {result}")
        except Exception as e:
            print(f"\n{description}")
            print(f"XPath: {xpath_expr}")
            print(f"错误: {str(e)}")
    
    # 4. 复杂字符串处理
    print("\n\n4. 复杂字符串处理")
    print("-" * 40)
    
    string_queries = [
        ("标题超过50个字符的书籍", "//c:book[string-length(c:title) > 50]"),
        ("标题包含数字的书籍", "//c:book[matches(c:title, '\\d+')]"),
        ("作者姓名包含空格的书籍", "//c:book[contains(c:author, ' ')]"),
        ("标题标准化测试", "//c:book[lower-case(translate(c:title, ' ,.!?;:', '        '))]"),
    ]
    
    for description, xpath_expr in string_queries:
        try:
            results = root.xpath(xpath_expr, namespaces=ns)
            print(f"\n{description}")
            print(f"XPath: {xpath_expr}")
            print(f"结果: {len(results)} 个节点")
            for book in results:
                book_id = book.get('id')
                title = book.xpath('string(c:title)', namespaces=ns)
                print(f"  - {book_id}: {title}")
        except Exception as e:
            print(f"\n{description}")
            print(f"XPath: {xpath_expr}")
            print(f"错误: {str(e)}")
    
    # 5. 自定义分析
    print("\n\n5. 自定义分析")
    print("-" * 40)
    
    # 模拟XPath 2.0+的变量和循环（使用Python实现）
    books = root.xpath('//c:book', namespaces=ns)
    
    # 按类别分组
    categories = {}
    for book in books:
        category = book.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(book)
    
    print("\n按类别分组的书籍:")
    for category, category_books in categories.items():
        print(f"\n{category}: {len(category_books)} 本书")
        for book in category_books:
            book_id = book.get('id')
            title = book.xpath('string(c:title)', namespaces=ns)
            print(f"  - {book_id}: {title}")
    
    # 价格分析
    prices = []
    for book in books:
        price_element = book.xpath('c:price', namespaces=ns)
        if price_element:
            price_text = price_element[0].text
            try:
                price = float(price_text)
                prices.append(price)
            except ValueError:
                pass
    
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print("\n\n价格分析:")
        print(f"总书籍数: {len(books)}")
        print(f"有价格的书籍数: {len(prices)}")
        print(f"平均价格: {avg_price:.2f}")
        print(f"最低价格: {min_price:.2f}")
        print(f"最高价格: {max_price:.2f}")
        
        print("\n高于平均价格的书籍:")
        for book in books:
            price_element = book.xpath('c:price', namespaces=ns)
            if price_element:
                try:
                    price = float(price_element[0].text)
                    if price > avg_price:
                        book_id = book.get('id')
                        title = book.xpath('string(c:title)', namespaces=ns)
                        print(f"  - {book_id}: {title} (${price})")
                except ValueError:
                    pass

if __name__ == "__main__":
    test_advanced_xpath()
```

## 5.9 本章小结

本章深入探讨了XPath的高级应用技巧，包括：

- 复杂路径表达式和条件组合
- 高级字符串处理和正则表达式
- 数值计算和统计分析
- 高级布尔逻辑和动态条件构建
- 节点集运算和重组转换
- XML文档分析和数据质量检查

掌握这些高级技巧，您将能够：

1. 处理复杂的XML结构和数据
2. 执行深入的数据分析和验证
3. 构建动态和灵活的查询
4. 检查和修复数据质量问题
5. 提取和处理复杂的数据模式

下一章我们将学习XPath在不同编程语言中的应用，这将帮助您将XPath技能应用到实际开发工作中。

## 5.10 练习

1. 编写XPath表达式找出所有价格高于平均值且作者数量大于1的书籍
2. 查找所有标题包含数字且页数超过500的书籍
3. 识别所有数据质量问题（缺少字段、无效数据等）
4. 按价格区间（低、中、高）对书籍进行分组统计
5. 找出同一作者写的不同类别的书籍

尝试在提供的代码示例中验证您的答案，并尝试扩展这些示例以适应更复杂的需求。