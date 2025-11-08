# XPath基础语法示例
# 演示XPath的基本概念和语法

from lxml import etree

def xpath_basics_demo():
    """XPath基础语法演示"""
    
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
</bookstore>"""
    
    # 解析XML
    root = etree.fromstring(xml_data)
    
    print("=" * 60)
    print("XPath基础语法演示")
    print("=" * 60)
    
    # 1. 节点选择
    print("\n1. 节点选择:")
    print("-" * 40)
    
    tests = [
        ("选择所有book元素", "//book"),
        ("选择所有title元素", "//title"),
        ("选择所有author元素", "//author"),
        ("选择所有price元素", "//price")
    ]
    
    for description, xpath_expr in tests:
        results = root.xpath(xpath_expr)
        print(f"\n{description}:")
        print(f"  XPath: {xpath_expr}")
        print(f"  结果数量: {len(results)}")
        for i, result in enumerate(results[:2], 1):  # 只显示前两个结果
            if result.text:
                print(f"    结果{i}: {result.tag} = {result.text}")
            else:
                print(f"    结果{i}: {result.tag} (无文本)")
    
    # 2. 谓语使用
    print("\n\n2. 谓语使用:")
    print("-" * 40)
    
    predicate_tests = [
        ("第一个book元素", "//book[1]"),
        ("最后一个book元素", "//book[last()]"),
        ("前两个book元素", "//book[position() < 3]"),
        ("属性category为'web'的book", "//book[@category='web']"),
        ("价格大于35的book", "//book[price > 35]"),
        ("lang属性为'en'的title", "//title[@lang='en']")
    ]
    
    for description, xpath_expr in predicate_tests:
        results = root.xpath(xpath_expr)
        print(f"\n{description}:")
        print(f"  XPath: {xpath_expr}")
        print(f"  结果数量: {len(results)}")
        for result in results:
            if result.tag == "book":
                title = result.xpath("title/text()")
                price = result.xpath("price/text()")
                print(f"    书籍: {title[0] if title else '未知'}, 价格: {price[0] if price else '未知'}")
            else:
                print(f"    {result.tag}: {result.text if result.text else '无文本'}")
    
    # 3. 未知节点选择
    print("\n\n3. 未知节点选择:")
    print("-" * 40)
    
    wildcard_tests = [
        ("bookstore的所有子元素", "/bookstore/*"),
        ("文档中的所有元素", "//*"),
        ("所有具有category属性的book", "//book[@category]"),
        ("所有具有属性的元素", "//*[@*]"),
        ("所有text节点", "//text()"),
        ("所有comment节点", "//comment()")
    ]
    
    for description, xpath_expr in wildcard_tests:
        try:
            results = root.xpath(xpath_expr)
            print(f"\n{description}:")
            print(f"  XPath: {xpath_expr}")
            print(f"  结果数量: {len(results)}")
            
            # 只显示前几个结果，避免输出过多
            for i, result in enumerate(results[:3]):
                if hasattr(result, 'tag'):
                    # 元素节点
                    tag = result.tag
                    text = result.text.strip() if result.text and result.text.strip() else ""
                    print(f"    结果{i+1}: {tag} = {text if text else '(无文本)'}")
                else:
                    # 文本节点
                    text = str(result).strip() if result and str(result).strip() else ""
                    if text:
                        print(f"    结果{i+1}: 文本 = '{text}'")
        except Exception as e:
            print(f"\n{description}:")
            print(f"  XPath: {xpath_expr}")
            print(f"  错误: {str(e)}")
    
    # 4. 路径操作
    print("\n\n4. 路径操作:")
    print("-" * 40)
    
    path_tests = [
        ("从根节点选择book", "/bookstore/book"),
        ("从所有book元素中选择title", "//book/title"),
        ("选择所有title元素的文本", "//title/text()"),
        ("选择价格", "//price"),
        ("选择价格文本", "//price/text()"),
        ("选择具有category属性的book的title", "//book[@category]/title")
    ]
    
    for description, xpath_expr in path_tests:
        results = root.xpath(xpath_expr)
        print(f"\n{description}:")
        print(f"  XPath: {xpath_expr}")
        print(f"  结果数量: {len(results)}")
        for i, result in enumerate(results[:2], 1):
            if isinstance(result, etree._Element):
                text = result.text.strip() if result.text and result.text.strip() else ""
                print(f"    结果{i}: {result.tag} = '{text}'")
            else:
                text = str(result).strip() if result and str(result).strip() else ""
                print(f"    结果{i}: '{text}'")
    
    # 5. 轴操作演示
    print("\n\n5. 轴操作演示:")
    print("-" * 40)
    
    axis_tests = [
        ("第一个book的所有子元素", "//book[1]/*"),
        ("第一个book的父元素", "//book[1]/.."),
        ("第一个book的所有后代元素", "//book[1]//*"),
        ("第一个book的所有属性", "//book[1]/@*"),
        ("第一个title的所有祖先", "//title[1]/ancestor::*"),
        ("所有在第一个book之后的元素", "//book[1]/following::*"),
        ("第一个book之前的所有元素", "//book[1]/preceding::*")
    ]
    
    for description, xpath_expr in axis_tests:
        try:
            results = root.xpath(xpath_expr)
            print(f"\n{description}:")
            print(f"  XPath: {xpath_expr}")
            print(f"  结果数量: {len(results)}")
            
            for i, result in enumerate(results[:3], 1):
                if isinstance(result, etree._Element):
                    tag = result.tag
                    text = result.text.strip() if result.text and result.text.strip() else ""
                    print(f"    结果{i}: {tag} = '{text}'")
                else:
                    # 属性或其他类型
                    print(f"    结果{i}: {result}")
        except Exception as e:
            print(f"\n{description}:")
            print(f"  XPath: {xpath_expr}")
            print(f"  错误: {str(e)}")
    
    # 6. 运算符演示
    print("\n\n6. 运算符演示:")
    print("-" * 40)
    
    operator_tests = [
        ("价格等于29.99的book", "//book[price = 29.99]"),
        ("价格不等于39.95的book", "//book[price != 39.95]"),
        ("价格小于40的book", "//book[price < 40]"),
        ("价格大于等于40的book", "//book[price >= 40]"),
        ("category为'web'且价格小于40的book", "//book[@category = 'web' and price < 40]"),
        ("category为'children'或价格大于40的book", "//book[@category = 'children' or price > 40]")
    ]
    
    for description, xpath_expr in operator_tests:
        results = root.xpath(xpath_expr)
        print(f"\n{description}:")
        print(f"  XPath: {xpath_expr}")
        print(f"  结果数量: {len(results)}")
        
        for result in results:
            title = result.xpath("title/text()")
            price = result.xpath("price/text()")
            category = result.get("category")
            print(f"    书籍: {title[0] if title else '未知'}, 类别: {category}, 价格: {price[0] if price else '未知'}")

def interactive_xpath_test():
    """交互式XPath测试"""
    
    # 使用上面的XML文档
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
</bookstore>"""
    
    root = etree.fromstring(xml_data)
    
    print("\n" + "=" * 60)
    print("交互式XPath测试")
    print("=" * 60)
    print("输入XPath表达式，输入'exit'退出")
    print()
    
    while True:
        try:
            xpath_expr = input("XPath表达式: ").strip()
            
            if xpath_expr.lower() == 'exit':
                print("退出测试。")
                break
            
            if not xpath_expr:
                continue
            
            # 执行XPath表达式
            results = root.xpath(xpath_expr)
            
            print(f"结果数量: {len(results)}")
            
            for i, result in enumerate(results, 1):
                if isinstance(result, etree._Element):
                    # 元素节点
                    tag = result.tag
                    text = result.text.strip() if result.text and result.text.strip() else ""
                    attributes = ", ".join([f'{k}="{v}"' for k, v in result.attrib.items()])
                    attr_str = f" ({attributes})" if attributes else ""
                    
                    if text:
                        print(f"  {i}. {tag}{attr_str} = '{text}'")
                    else:
                        print(f"  {i}. {tag}{attr_str}")
                elif hasattr(result, 'attrname'):
                    # 属性节点
                    print(f"  {i}. @{result.attrname} = '{result}'")
                else:
                    # 文本节点或其他
                    text = str(result).strip() if result and str(result).strip() else ""
                    print(f"  {i}. '{text}'")
            
            print()  # 空行分隔
            
        except Exception as e:
            print(f"错误: {str(e)}")
            print()

if __name__ == "__main__":
    # 运行基础演示
    xpath_basics_demo()
    
    # 运行交互式测试
    interactive_xpath_test()