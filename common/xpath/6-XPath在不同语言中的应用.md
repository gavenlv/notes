# 第6章：XPath在不同语言中的应用

## 6.1 Python中的XPath

### 6.1.1 lxml库基础

Python中最常用的XPath处理库是lxml，它提供了强大的XPath支持：

```python
# code/python-examples/xpath_basics.py
from lxml import etree

# 解析XML字符串
xml_data = """<?xml version="1.0"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="web">
        <title lang="en">XPath for Dummies</title>
        <author>John Doe</author>
        <year>2020</year>
        <price>29.99</price>
    </book>
</bookstore>
"""

# 解析XML
root = etree.fromstring(xml_data)

# 基本XPath查询
titles = root.xpath("//title/text()")
print("所有书籍标题:", titles)

# 带谓语的XPath查询
web_books = root.xpath("//book[@category='web']/title/text()")
print("Web类书籍标题:", web_books)

# 获取属性
languages = root.xpath("//title/@lang")
print("书籍语言:", languages)

# 组合查询
book_info = root.xpath("//book[price > 30]")
for book in book_info:
    title = book.xpath("title/text()")[0]
    price = book.xpath("price/text()")[0]
    print(f"{title}: ${price}")
```

### 6.1.2 lxml高级功能

```python
# code/python-examples/xpath_advanced.py
from lxml import etree

# 处理命名空间
xml_with_ns = """<?xml version="1.0"?>
<bookstore xmlns:book="http://example.com/book">
    <book:book category="web">
        <book:title lang="en">Learning XML</book:title>
        <book:author>Erik T. Ray</book:author>
        <book:year>2003</book:year>
        <book:price>39.95</book:price>
    </book:book>
</bookstore>
"""

# 解析带命名空间的XML
root_ns = etree.fromstring(xml_with_ns)
ns = {'book': 'http://example.com/book'}

# 使用命名空间前缀查询
titles_ns = root_ns.xpath("//book:title/text()", namespaces=ns)
print("带命名空间的标题:", titles_ns)

# 使用变量和XPath 2.0功能（如果支持）
try:
    # lxml支持一些XPath 2.0功能
    result = root_ns.xpath("//book:book[book:price > avg(//book:book/book:price)]", namespaces=ns)
    print("价格高于平均的书籍:", len(result))
except Exception as e:
    print(f"XPath 2.0功能不支持: {e}")

# 使用XPathEvaluator优化性能
evaluator = etree.XPathEvaluator(root_ns, namespaces=ns)
books_over_30 = evaluator("//book:book[number(book:price) > 30]")
print("价格超过30的书籍数量:", len(books_over_30))

# 动态构建XPath
def dynamic_query(category="", min_price=None, max_price=None):
    conditions = []
    if category:
        conditions.append(f"@category='{category}'")
    if min_price is not None:
        conditions.append(f"number(price) > {min_price}")
    if max_price is not None:
        conditions.append(f"number(price) < {max_price}")
    
    xpath_expr = f"//book:book"
    if conditions:
        xpath_expr += f"[{' and '.join(conditions)}]"
    
    return xpath_expr

# 使用动态查询
query = dynamic_query(category="web", min_price=30)
print(f"动态XPath: {query}")
result = evaluator(query)
print(f"查询结果: {len(result)}本书")
```

### 6.1.3 Python中的XPath实战

```python
# code/python-examples/xpath_real_world.py
import requests
from lxml import etree
import re

# 从网络获取XML/HTML并使用XPath分析
def analyze_web_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 使用lxml解析HTML
        tree = etree.HTML(response.content)
        
        # 提取页面标题
        title = tree.xpath("//title/text()")
        print(f"页面标题: {title[0] if title else '无标题'}")
        
        # 提取所有链接
        links = tree.xpath("//a/@href")
        print(f"链接数量: {len(links)}")
        
        # 提取所有图片
        images = tree.xpath("//img/@src")
        print(f"图片数量: {len(images)}")
        
        # 提取文本内容
        paragraphs = tree.xpath("//p//text()")
        total_text = " ".join(p.strip() for p in paragraphs if p.strip())
        print(f"文本总长度: {len(total_text)} 字符")
        
        # 统计标题层级
        headers = {}
        for level in range(1, 7):
            h_count = len(tree.xpath(f"//h{level}"))
            headers[f"h{level}"] = h_count
        
        print("标题层级统计:", headers)
        
        return tree
        
    except Exception as e:
        print(f"分析网页失败: {e}")
        return None

def process_xml_file(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # 获取XML文档结构信息
        total_elements = len(root.xpath("//*"))
        unique_elements = len(set(root.xpath("/*/name()")))
        max_depth = max(len(elem.xpath("ancestor::*")) for elem in root.xpath("//*"))
        
        print(f"总元素数: {total_elements}")
        print(f"唯一元素类型: {unique_elements}")
        print(f"最大深度: {max_depth}")
        
        # 提取属性信息
        all_attributes = root.xpath("//@*")
        unique_attributes = len(set(root.xpath("//@*/name()")))
        print(f"总属性数: {len(all_attributes)}")
        print(f"唯一属性类型: {unique_attributes}")
        
        # 分析文本内容
        text_nodes = root.xpath("//text()[normalize-space()]")
        total_text_length = sum(len(text.strip()) for text in text_nodes)
        print(f"文本节点数: {len(text_nodes)}")
        print(f"文本总长度: {total_text_length}")
        
        return root
        
    except Exception as e:
        print(f"处理XML文件失败: {e}")
        return None

# 运行示例
if __name__ == "__main__":
    print("分析网络页面:")
    analyze_web_page("https://www.example.com")
    
    print("\n分析XML文件:")
    # 假设有一个本地XML文件
    process_xml_file("sample.xml")
```

## 6.2 JavaScript中的XPath

### 6.2.1 DOM中的XPath

JavaScript内置了XPath支持，可以直接在浏览器中使用：

```javascript
// code/javascript-examples/xpath_basics.js

// XML文档示例
const xmlString = `<?xml version="1.0"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="programming">
        <title lang="en">JavaScript: The Good Parts</title>
        <author>Douglas Crockford</author>
        <year>2008</year>
        <price>29.99</price>
    </book>
</bookstore>`;

// 创建XML DOM
const parser = new DOMParser();
const xmlDoc = parser.parseFromString(xmlString, "text/xml");

// 使用XPath查询
function evaluateXPath(xmlDoc, xpathExpr, resultType = XPathResult.ORDERED_NODE_SNAPSHOT_TYPE) {
    return xmlDoc.evaluate(xpathExpr, xmlDoc, null, resultType, null);
}

// 获取所有书籍标题
const titles = evaluateXPath(xmlDoc, "//title/text()");
for (let i = 0; i < titles.snapshotLength; i++) {
    console.log(`标题 ${i + 1}: ${titles.snapshotItem(i).textContent}`);
}

// 获取特定类别的书籍
const webBooks = evaluateXPath(xmlDoc, "//book[@category='web']");
for (let i = 0; i < webBooks.snapshotLength; i++) {
    const book = webBooks.snapshotItem(i);
    const title = book.querySelector("title").textContent;
    const price = book.querySelector("price").textContent;
    console.log(`Web书籍: ${title} - $${price}`);
}

// 获取属性值
const languages = evaluateXPath(xmlDoc, "//title/@lang");
for (let i = 0; i < languages.snapshotLength; i++) {
    console.log(`语言 ${i + 1}: ${languages.snapshotItem(i).textContent}`);
}
```

### 6.2.2 浏览器控制台中的XPath

在浏览器开发者工具中，可以使用便捷函数`$x()`来测试XPath：

```javascript
// code/javascript-examples/xpath_browser_console.js

// 在浏览器控制台中的XPath示例

// 1. 获取所有链接
$x("//a[@href]");

// 2. 获取所有图片
$x("//img[@src]");

// 3. 获取特定类名的元素
$x("//*[@class='active']");

// 4. 获取包含特定文本的元素
$x("//*[contains(text(), 'XPath')]");

// 5. 获取表格中的特定单元格
$x("//table[@id='data-table']//tr[td[contains(text(), 'XPath')]]");

// 6. 获取表单中的所有输入元素
$x("//form[@name='search']//input");

// 7. 获取价格高于平均值的商品
let prices = $x("//div[@class='product-price']/text()");
let avgPrice = prices.reduce((sum, price) => sum + parseFloat(price.textContent), 0) / prices.length;
$x("//div[@class='product'][number(div[@class='product-price']) > " + avgPrice + "]");

// 8. 获取具有特定数据属性的元素
$x("//*[@data-category='technology']");

// 9. 获取按钮和链接的文本内容
$x("//button//text() | //a//text()");

// 10. 获取表格的标题和内容
{
    headers: $x("//table[@id='data-table']//th//text()"),
    rows: $x("//table[@id='data-table']//tr[position()>1]/td//text()")
}
```

### 6.2.3 JavaScript中的XPath封装

```javascript
// code/javascript-examples/xpath_wrapper.js

// XPath封装类
class XPathHelper {
    constructor(document) {
        this.document = document;
    }

    // 执行XPath查询
    query(xpathExpr, contextNode = this.document, resultType = XPathResult.ORDERED_NODE_SNAPSHOT_TYPE) {
        return this.document.evaluate(
            xpathExpr, 
            contextNode, 
            null, 
            resultType, 
            null
        );
    }

    // 获取单个节点
    selectSingleNode(xpathExpr, contextNode = this.document) {
        return this.query(
            xpathExpr, 
            contextNode, 
            XPathResult.FIRST_ORDERED_NODE_TYPE
        ).singleNodeValue;
    }

    // 获取节点数组
    selectNodes(xpathExpr, contextNode = this.document) {
        const result = this.query(xpathExpr, contextNode, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE);
        const nodes = [];
        for (let i = 0; i < result.snapshotLength; i++) {
            nodes.push(result.snapshotItem(i));
        }
        return nodes;
    }

    // 获取字符串值
    selectString(xpathExpr, contextNode = this.document) {
        return this.query(
            xpathExpr, 
            contextNode, 
            XPathResult.STRING_TYPE
        ).stringValue;
    }

    // 获取数值
    selectNumber(xpathExpr, contextNode = this.document) {
        return this.query(
            xpathExpr, 
            contextNode, 
            XPathResult.NUMBER_TYPE
        ).numberValue;
    }

    // 获取布尔值
    selectBoolean(xpathExpr, contextNode = this.document) {
        return this.query(
            xpathExpr, 
            contextNode, 
            XPathResult.BOOLEAN_TYPE
        ).booleanValue;
    }

    // 创建命名空间解析器
    createNSResolver(namespaces) {
        return function(prefix) {
            return namespaces[prefix] || null;
        };
    }

    // 带命名空间的查询
    queryWithNS(xpathExpr, namespaces, contextNode = this.document) {
        const resolver = this.createNSResolver(namespaces);
        return this.document.evaluate(
            xpathExpr, 
            contextNode, 
            resolver, 
            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, 
            null
        );
    }
}

// 使用示例
function xpathDemo() {
    const helper = new XPathHelper(document);
    
    // 获取文档标题
    const title = helper.selectString("//title");
    console.log("页面标题:", title);
    
    // 获取所有链接
    const links = helper.selectNodes("//a[@href]");
    console.log("链接数量:", links.length);
    
    // 检查特定元素是否存在
    const hasMenu = helper.selectBoolean("//*[@id='main-menu']");
    console.log("有主菜单:", hasMenu);
    
    // 获取元素数量
    const imageCount = helper.selectNumber("count(//img)");
    console.log("图片数量:", imageCount);
    
    // 处理命名空间XML
    const xmlString = `<?xml version="1.0"?>
    <bookstore xmlns:book="http://example.com/book">
        <book:book category="web">
            <book:title>Learning XML</book:title>
        </book:book>
    </bookstore>`;
    
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "text/xml");
    const xmlHelper = new XPathHelper(xmlDoc);
    
    const namespaces = {
        'book': 'http://example.com/book'
    };
    
    const title = xmlHelper.queryWithNS("//book:title/text()", namespaces);
    console.log("命名空间标题:", title.stringValue);
}

// 如果在浏览器中运行，可以直接调用xpathDemo()
// 如果在Node.js中运行，需要适当的DOM环境
```

### 6.2.4 实际应用：网页爬虫和数据提取

```javascript
// code/javascript-examples/web_scraper.js

// 使用XPath实现的简单网页爬虫
class WebScraper {
    constructor() {
        this.helper = new XPathHelper(document);
    }

    // 提取文章标题和链接
    extractArticles(containerSelector = ".article-list") {
        const articles = [];
        const container = document.querySelector(containerSelector);
        
        if (!container) return articles;
        
        const articleElements = this.helper.selectNodes(".//div[contains(@class, 'article')]", container);
        
        articleElements.forEach(article => {
            const titleElement = this.helper.selectSingleNode(".//h2[contains(@class, 'title')]/a", article);
            const summaryElement = this.helper.selectSingleNode(".//p[contains(@class, 'summary')]", article);
            const authorElement = this.helper.selectSingleNode(".//span[contains(@class, 'author')]", article);
            const dateElement = this.helper.selectSingleNode(".//time[contains(@class, 'date')]", article);
            
            articles.push({
                title: titleElement ? titleElement.textContent.trim() : "",
                url: titleElement ? titleElement.getAttribute('href') : "",
                summary: summaryElement ? summaryElement.textContent.trim() : "",
                author: authorElement ? authorElement.textContent.trim() : "",
                date: dateElement ? dateElement.getAttribute('datetime') : dateElement.textContent.trim()
            });
        });
        
        return articles;
    }

    // 提取产品信息
    extractProducts(containerSelector = ".products") {
        const products = [];
        const container = document.querySelector(containerSelector);
        
        if (!container) return products;
        
        const productElements = this.helper.selectNodes(".//div[contains(@class, 'product')]", container);
        
        productElements.forEach(product => {
            const titleElement = this.helper.selectSingleNode(".//h3[contains(@class, 'product-title')]", product);
            const priceElement = this.helper.selectSingleNode(".//span[contains(@class, 'price')]", product);
            const imageElement = this.helper.selectSingleNode(".//img[contains(@class, 'product-image')]", product);
            const ratingElement = this.helper.selectSingleNode(".//div[contains(@class, 'rating')]", product);
            
            // 提取评分
            let rating = 0;
            if (ratingElement) {
                const stars = this.helper.selectNodes(".//i[contains(@class, 'star')]", ratingElement);
                rating = stars.length;
            }
            
            // 提取价格数值
            let price = 0;
            if (priceElement) {
                const priceText = priceElement.textContent.replace(/[^0-9.]/g, '');
                price = parseFloat(priceText);
            }
            
            products.push({
                title: titleElement ? titleElement.textContent.trim() : "",
                price: price,
                image: imageElement ? imageElement.getAttribute('src') : "",
                rating: rating
            });
        });
        
        return products;
    }

    // 提取表格数据
    extractTableData(tableSelector) {
        const table = document.querySelector(tableSelector);
        if (!table) return [];
        
        const headers = [];
        const headerCells = this.helper.selectNodes(".//thead//th", table);
        
        headerCells.forEach(cell => {
            headers.push(cell.textContent.trim());
        });
        
        const rows = [];
        const rowElements = this.helper.selectNodes(".//tbody//tr", table);
        
        rowElements.forEach(rowElement => {
            const cells = this.helper.selectNodes("./td", rowElement);
            const rowData = {};
            
            cells.forEach((cell, index) => {
                const header = headers[index] || `column_${index}`;
                rowData[header] = cell.textContent.trim();
            });
            
            rows.push(rowData);
        });
        
        return rows;
    }

    // 获取页面元数据
    getPageMetadata() {
        return {
            title: this.helper.selectString("//title") || "",
            description: this.helper.selectString("//meta[@name='description']/@content") || "",
            keywords: this.helper.selectString("//meta[@name='keywords']/@content") || "",
            author: this.helper.selectString("//meta[@name='author']/@content") || "",
            canonicalUrl: this.helper.selectString("//link[@rel='canonical']/@href") || "",
            language: document.documentElement.getAttribute('lang') || "",
            totalLinks: this.helper.selectNumber("count(//a[@href])"),
            totalImages: this.helper.selectNumber("count(//img[@src])"),
            hasStructuredData: this.helper.selectBoolean("boolean(//script[@type='application/ld+json'])")
        };
    }
}

// 在浏览器中使用示例
function runScraper() {
    const scraper = new WebScraper();
    
    // 获取页面元数据
    const metadata = scraper.getPageMetadata();
    console.log("页面元数据:", metadata);
    
    // 提取文章列表
    const articles = scraper.extractArticles();
    console.log("文章列表:", articles);
    
    // 提取产品信息
    const products = scraper.extractProducts();
    console.log("产品信息:", products);
    
    // 提取表格数据
    const tableData = scraper.extractTableData("#data-table");
    console.log("表格数据:", tableData);
    
    return {
        metadata,
        articles,
        products,
        tableData
    };
}

// 导出供Node.js使用（如果有适当的DOM环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WebScraper, XPathHelper };
}
```

## 6.3 Java中的XPath

### 6.3.1 Java XPath API基础

Java提供了强大的XPath API支持，位于`javax.xml.xpath`包中：

```java
// code/java-examples/XPathBasics.java
package com.example.xpath;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;

public class XPathBasics {
    public static void main(String[] args) {
        try {
            // XML文档
            String xmlString = "<?xml version=\"1.0\"?>" +
                "<bookstore>" +
                "  <book category=\"web\">" +
                "    <title lang=\"en\">Learning XML</title>" +
                "    <author>Erik T. Ray</author>" +
                "    <year>2003</year>" +
                "    <price>39.95</price>" +
                "  </book>" +
                "  <book category=\"programming\">" +
                "    <title lang=\"en\">Java Programming</title>" +
                "    <author>John Smith</author>" +
                "    <year>2020</year>" +
                "    <price>45.99</price>" +
                "  </book>" +
                "</bookstore>";

            // 解析XML
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document document = builder.parse(new java.io.ByteArrayInputStream(xmlString.getBytes()));

            // 创建XPath对象
            XPathFactory xPathFactory = XPathFactory.newInstance();
            XPath xpath = xPathFactory.newXPath();

            // 基本XPath查询
            // 1. 获取所有书籍标题
            XPathExpression expr = xpath.compile("//title/text()");
            NodeList titles = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("所有书籍标题:");
            for (int i = 0; i < titles.getLength(); i++) {
                System.out.println("  " + titles.item(i).getNodeValue());
            }

            // 2. 获取web类别的书籍
            expr = xpath.compile("//book[@category='web']");
            NodeList webBooks = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\nWeb类别书籍数量: " + webBooks.getLength());

            // 3. 获取价格超过40的书籍标题
            expr = xpath.compile("//book[price > 40]/title/text()");
            NodeList expensiveBooks = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\n价格超过40的书籍:");
            for (int i = 0; i < expensiveBooks.getLength(); i++) {
                System.out.println("  " + expensiveBooks.item(i).getNodeValue());
            }

            // 4. 获取属性
            expr = xpath.compile("//title/@lang");
            NodeList languages = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\n书籍语言:");
            for (int i = 0; i < languages.getLength(); i++) {
                System.out.println("  " + languages.item(i).getNodeValue());
            }

            // 5. 计算平均价格
            expr = xpath.compile("sum(//book/price) div count(//book)");
            Double avgPrice = (Double) expr.evaluate(document, XPathConstants.NUMBER);
            System.out.println("\n平均价格: $" + avgPrice);

            // 6. 计算书籍数量
            expr = xpath.compile("count(//book)");
            Double bookCount = (Double) expr.evaluate(document, XPathConstants.NUMBER);
            System.out.println("\n书籍总数: " + bookCount.intValue());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 6.3.2 Java中的XPath高级应用

```java
// code/java-examples/XPathAdvanced.java
package com.example.xpath;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathFactory;
import javax.xml.xpath.XPathFunction;
import javax.xml.xpath.XPathFunctionResolver;
import javax.xml.xpath.XPathVariableResolver;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import java.util.List;
import java.util.ArrayList;

public class XPathAdvanced {
    
    // 自定义XPath函数
    public static class StringLengthFunction implements XPathFunction {
        @Override
        public Object evaluate(@SuppressWarnings("rawtypes") List args) {
            if (args.size() == 1) {
                String str = (String) args.get(0);
                return str.length();
            }
            return 0;
        }
    }
    
    // 自定义变量解析器
    public static class CustomVariableResolver implements XPathVariableResolver {
        @Override
        public Object resolveVariable(QName variableName) {
            if (variableName.getLocalPart().equals("minPrice")) {
                return 30;
            }
            return null;
        }
    }
    
    // 自定义函数解析器
    public static class CustomFunctionResolver implements XPathFunctionResolver {
        @Override
        public XPathFunction resolveFunction(QName functionName, int arity) {
            if (functionName.getLocalPart().equals("stringLength") && arity == 1) {
                return new StringLengthFunction();
            }
            return null;
        }
    }

    public static void main(String[] args) {
        try {
            // XML文档示例
            String xmlString = "<?xml version=\"1.0\"?>" +
                "<library>" +
                "  <section name=\"programming\">" +
                "    <book id=\"bk001\" category=\"programming\">" +
                "      <title>Effective Java</title>" +
                "      <author>Joshua Bloch</author>" +
                "      <year>2018</year>" +
                "      <price>45.99</price>" +
                "      <pages>416</pages>" +
                "    </book>" +
                "    <book id=\"bk002\" category=\"programming\">" +
                "      <title>Clean Code</title>" +
                "      <author>Robert C. Martin</author>" +
                "      <year>2008</year>" +
                "      <price>34.99</price>" +
                "      <pages>464</pages>" +
                "    </book>" +
                "  </section>" +
                "  <section name=\"database\">" +
                "    <book id=\"bk003\" category=\"database\">" +
                "      <title>Database System Concepts</title>" +
                "      <author>Abraham Silberschatz</author>" +
                "      <author>Henry F. Korth</author>" +
                "      <author>S. Sudarshan</author>" +
                "      <year>2019</year>" +
                "      <price>89.99</price>" +
                "      <pages>1104</pages>" +
                "    </book>" +
                "  </section>" +
                "</library>";

            // 解析XML
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document document = builder.parse(new java.io.ByteArrayInputStream(xmlString.getBytes()));

            // 创建XPath对象
            XPathFactory xPathFactory = XPathFactory.newInstance();
            XPath xpath = xPathFactory.newXPath();
            
            // 设置自定义变量和函数解析器
            xpath.setXPathVariableResolver(new CustomVariableResolver());
            xpath.setXPathFunctionResolver(new CustomFunctionResolver());

            // 1. 使用自定义变量
            XPathExpression expr = xpath.compile("//book[price > $minPrice]/title/text()");
            NodeList titles = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("价格超过 $" + 30 + " 的书籍:");
            for (int i = 0; i < titles.getLength(); i++) {
                System.out.println("  " + titles.item(i).getNodeValue());
            }
            
            // 2. 使用自定义函数
            expr = xpath.compile("//book[stringLength(title) > 10]/title/text()");
            NodeList longTitles = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\n标题长度超过10个字符的书籍:");
            for (int i = 0; i < longTitles.getLength(); i++) {
                System.out.println("  " + longTitles.item(i).getNodeValue());
            }
            
            // 3. 复杂XPath表达式
            expr = xpath.compile("//section/book[price = max(ancestor::section/book/price)]/title/text()");
            NodeList mostExpensiveBooks = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\n每个section中最贵的书籍:");
            for (int i = 0; i < mostExpensiveBooks.getLength(); i++) {
                System.out.println("  " + mostExpensiveBooks.item(i).getNodeValue());
            }
            
            // 4. 多作者书籍
            expr = xpath.compile("//book[count(author) > 1]/title/text()");
            NodeList multiAuthorBooks = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\n多作者书籍:");
            for (int i = 0; i < multiAuthorBooks.getLength(); i++) {
                System.out.println("  " + multiAuthorBooks.item(i).getNodeValue());
            }
            
            // 5. 页数与价格比率分析
            expr = xpath.compile("//book[pages div price > 10]/title/text()");
            NodeList goodValueBooks = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            System.out.println("\n页数与价格比率高的书籍 (>10页/美元):");
            for (int i = 0; i < goodValueBooks.getLength(); i++) {
                System.out.println("  " + goodValueBooks.item(i).getNodeValue());
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    // XPath分析工具方法
    public static class XPathAnalyzer {
        private Document document;
        private XPath xpath;
        
        public XPathAnalyzer(Document document) {
            this.document = document;
            XPathFactory factory = XPathFactory.newInstance();
            this.xpath = factory.newXPath();
        }
        
        public List<String> evaluateXPathToStringList(String xpathExpr) throws Exception {
            XPathExpression expr = xpath.compile(xpathExpr);
            NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            List<String> result = new ArrayList<>();
            
            for (int i = 0; i < nodes.getLength(); i++) {
                result.add(nodes.item(i).getNodeValue());
            }
            
            return result;
        }
        
        public List<Node> evaluateXPathToNodeList(String xpathExpr) throws Exception {
            XPathExpression expr = xpath.compile(xpathExpr);
            NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            List<Node> result = new ArrayList<>();
            
            for (int i = 0; i < nodes.getLength(); i++) {
                result.add(nodes.item(i));
            }
            
            return result;
        }
        
        public Double evaluateXPathToNumber(String xpathExpr) throws Exception {
            XPathExpression expr = xpath.compile(xpathExpr);
            return (Double) expr.evaluate(document, XPathConstants.NUMBER);
        }
        
        public Boolean evaluateXPathToBoolean(String xpathExpr) throws Exception {
            XPathExpression expr = xpath.compile(xpathExpr);
            return (Boolean) expr.evaluate(document, XPathConstants.BOOLEAN);
        }
        
        public String evaluateXPathToString(String xpathExpr) throws Exception {
            XPathExpression expr = xpath.compile(xpathExpr);
            return (String) expr.evaluate(document, XPathConstants.STRING);
        }
    }
}
```

### 6.3.3 Java中的XPath实战案例

```java
// code/java-examples/XPathRealWorld.java
package com.example.xpath;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class XPathRealWorld {
    
    // 产品配置分析
    public static class ProductConfigAnalyzer {
        private Document document;
        private XPath xpath;
        
        public ProductConfigAnalyzer(String xmlFilePath) throws Exception {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            document = builder.parse(new File(xmlFilePath));
            
            XPathFactory xPathFactory = XPathFactory.newInstance();
            xpath = xPathFactory.newXPath();
        }
        
        public List<String> getAllComponentNames() throws Exception {
            XPathExpression expr = xpath.compile("//component/@name");
            NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            List<String> names = new ArrayList<>();
            
            for (int i = 0; i < nodes.getLength(); i++) {
                names.add(nodes.item(i).getNodeValue());
            }
            
            return names;
        }
        
        public List<String> getComponentsByType(String type) throws Exception {
            XPathExpression expr = xpath.compile(String.format("//component[@type='%s']/@name", type));
            NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            List<String> names = new ArrayList<>();
            
            for (int i = 0; i < nodes.getLength(); i++) {
                names.add(nodes.item(i).getNodeValue());
            }
            
            return names;
        }
        
        public List<String> getComponentsWithDependency(String dependency) throws Exception {
            XPathExpression expr = xpath.compile(String.format("//component[dependencies/dependency[text()='%s']]/@name", dependency));
            NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
            List<String> names = new ArrayList<>();
            
            for (int i = 0; i < nodes.getLength(); i++) {
                names.add(nodes.item(i).getNodeValue());
            }
            
            return names;
        }
        
        public ComponentDetail getComponentDetail(String componentName) throws Exception {
            XPathExpression expr = xpath.compile(String.format("//component[@name='%s']", componentName));
            Node node = (Node) expr.evaluate(document, XPathConstants.NODE);
            
            if (node == null) {
                return null;
            }
            
            Element element = (Element) node;
            ComponentDetail detail = new ComponentDetail();
            detail.setName(element.getAttribute("name"));
            detail.setType(element.getAttribute("type"));
            detail.setVersion(element.getAttribute("version"));
            
            // 获取依赖列表
            XPathExpression depsExpr = xpath.compile("dependencies/dependency/text()");
            NodeList deps = (NodeList) depsExpr.evaluate(element, XPathConstants.NODESET);
            List<String> dependencies = new ArrayList<>();
            
            for (int i = 0; i < deps.getLength(); i++) {
                dependencies.add(deps.item(i).getNodeValue());
            }
            detail.setDependencies(dependencies);
            
            // 获取属性
            XPathExpression propsExpr = xpath.compile("properties/property");
            NodeList props = (NodeList) propsExpr.evaluate(element, XPathConstants.NODESET);
            List<Property> properties = new ArrayList<>();
            
            for (int i = 0; i < props.getLength(); i++) {
                Element propElement = (Element) props.item(i);
                Property prop = new Property();
                prop.setName(propElement.getAttribute("name"));
                prop.setValue(propElement.getAttribute("value"));
                properties.add(prop);
            }
            detail.setProperties(properties);
            
            return detail;
        }
    }
    
    // 数据模型类
    public static class ComponentDetail {
        private String name;
        private String type;
        private String version;
        private List<String> dependencies;
        private List<Property> properties;
        
        // getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        public List<String> getDependencies() { return dependencies; }
        public void setDependencies(List<String> dependencies) { this.dependencies = dependencies; }
        public List<Property> getProperties() { return properties; }
        public void setProperties(List<Property> properties) { this.properties = properties; }
    }
    
    public static class Property {
        private String name;
        private String value;
        
        // getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getValue() { return value; }
        public void setValue(String value) { this.value = value; }
    }
    
    // 测试方法
    public static void main(String[] args) {
        try {
            // 示例XML文件路径（需要实际文件）
            String configFilePath = "product-config.xml";
            
            ProductConfigAnalyzer analyzer = new ProductConfigAnalyzer(configFilePath);
            
            // 获取所有组件名称
            List<String> allComponents = analyzer.getAllComponentNames();
            System.out.println("所有组件:");
            for (String name : allComponents) {
                System.out.println("  " + name);
            }
            
            // 获取数据库类型的组件
            List<String> dbComponents = analyzer.getComponentsByType("database");
            System.out.println("\n数据库组件:");
            for (String name : dbComponents) {
                System.out.println("  " + name);
            }
            
            // 获取依赖于特定组件的组件
            List<String> dependentComponents = analyzer.getComponentsWithDependency("core-framework");
            System.out.println("\n依赖于core-framework的组件:");
            for (String name : dependentComponents) {
                System.out.println("  " + name);
            }
            
            // 获取特定组件的详细信息
            ComponentDetail detail = analyzer.getComponentDetail("user-service");
            if (detail != null) {
                System.out.println("\n组件详细信息: " + detail.getName());
                System.out.println("  类型: " + detail.getType());
                System.out.println("  版本: " + detail.getVersion());
                System.out.println("  依赖:");
                for (String dep : detail.getDependencies()) {
                    System.out.println("    " + dep);
                }
                System.out.println("  属性:");
                for (Property prop : detail.getProperties()) {
                    System.out.println("    " + prop.getName() + " = " + prop.getValue());
                }
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## 6.4 C#/.NET中的XPath

### 6.4.1 C# XPath基础

.NET Framework提供了强大的XPath支持，主要通过`System.Xml.XPath`命名空间实现：

```csharp
// code/csharp-examples/XPathBasics.cs
using System;
using System.Xml;
using System.Xml.XPath;
using System.Collections.Generic;

public class XPathBasics
{
    public static void Main()
    {
        // XML文档
        string xmlString = @"<?xml version=""1.0""?>
<bookstore>
    <book category=""web"">
        <title lang=""en"">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category=""programming"">
        <title lang=""en"">C# Programming</title>
        <author>John Smith</author>
        <year>2020</year>
        <price>45.99</price>
    </book>
</bookstore>";

        // 加载XML文档
        XmlDocument xmlDoc = new XmlDocument();
        xmlDoc.LoadXml(xmlString);

        // 创建XPath导航器
        XPathNavigator navigator = xmlDoc.CreateNavigator();

        // 1. 基本XPath查询
        XPathNodeIterator titles = navigator.Select("//title/text()");
        Console.WriteLine("所有书籍标题:");
        while (titles.MoveNext())
        {
            Console.WriteLine("  " + titles.Current.Value);
        }

        // 2. 带谓语的XPath查询
        XPathNodeIterator webBooks = navigator.Select("//book[@category='web']");
        Console.WriteLine("\nWeb类别书籍数量: " + webBooks.Count);

        // 3. 获取价格超过40的书籍标题
        XPathNodeIterator expensiveBooks = navigator.Select("//book[price > 40]/title/text()");
        Console.WriteLine("\n价格超过40的书籍:");
        while (expensiveBooks.MoveNext())
        {
            Console.WriteLine("  " + expensiveBooks.Current.Value);
        }

        // 4. 获取属性
        XPathNodeIterator languages = navigator.Select("//title/@lang");
        Console.WriteLine("\n书籍语言:");
        while (languages.MoveNext())
        {
            Console.WriteLine("  " + languages.Current.Value);
        }

        // 5. 计算平均价格
        double avgPrice = (double)navigator.Evaluate("sum(//book/price) div count(//book)");
        Console.WriteLine("\n平均价格: $" + avgPrice.ToString("F2"));

        // 6. 计算书籍数量
        double bookCount = (double)navigator.Evaluate("count(//book)");
        Console.WriteLine("\n书籍总数: " + (int)bookCount);
    }
}
```

### 6.4.2 C# XPath高级应用

```csharp
// code/csharp-examples/XPathAdvanced.cs
using System;
using System.Xml;
using System.Xml.XPath;
using System.Collections.Generic;
using System.Xml.Xsl;

public class XPathAdvanced
{
    // 扩展方法：获取属性值
    public static string GetAttribute(this XPathNavigator navigator, string attributeName)
    {
        if (navigator.HasAttributes)
        {
            XPathNavigator attribute = navigator.GetAttribute(attributeName, string.Empty);
            return attribute?.Value ?? string.Empty;
        }
        return string.Empty;
    }

    // 扩展方法：获取子元素值
    public static string GetElementValue(this XPathNavigator navigator, string elementName)
    {
        XPathNodeIterator iterator = navigator.Select(elementName);
        if (iterator.MoveNext())
        {
            return iterator.Current.Value;
        }
        return string.Empty;
    }

    // 扩展方法：转换为数值
    public static double ToDouble(this string value)
    {
        double result;
        return double.TryParse(value, out result) ? result : 0.0;
    }

    public static void Main()
    {
        // 示例XML
        string xmlString = @"<?xml version=""1.0""?>
<library>
    <section name=""programming"">
        <book id=""bk001"" category=""programming"">
            <title>Effective Java</title>
            <author>Joshua Bloch</author>
            <year>2018</year>
            <price>45.99</price>
            <pages>416</pages>
            <reviews>
                <review rating=""5"">Excellent book!</review>
                <review rating=""4"">Very informative.</review>
            </reviews>
        </book>
        <book id=""bk002"" category=""programming"">
            <title>Clean Code</title>
            <author>Robert C. Martin</author>
            <year>2008</year>
            <price>34.99</price>
            <pages>464</pages>
            <reviews>
                <review rating=""5"">Must read!</review>
                <review rating=""5"">Changed my career.</review>
            </reviews>
        </book>
    </section>
    <section name=""database"">
        <book id=""bk003"" category=""database"">
            <title>Database System Concepts</title>
            <author>Abraham Silberschatz</author>
            <author>Henry F. Korth</author>
            <author>S. Sudarshan</author>
            <year>2019</year>
            <price>89.99</price>
            <pages>1104</pages>
            <reviews>
                <review rating=""4"">Comprehensive.</review>
                <review rating=""3"">A bit academic.</review>
            </reviews>
        </book>
    </section>
</library>";

        XmlDocument xmlDoc = new XmlDocument();
        xmlDoc.LoadXml(xmlString);
        XPathNavigator navigator = xmlDoc.CreateNavigator();

        // 1. 使用命名空间管理器
        XmlNamespaceManager nsManager = new XmlNamespaceManager(xmlDoc.NameTable);
        // 添加命名空间（如果有的话）
        // nsManager.AddNamespace("ns", "http://example.com/namespace");

        // 2. 复杂XPath表达式
        XPathNodeIterator mostExpensiveBooks = navigator.Select("//section/book[price = max(ancestor::section/book/price)]");
        Console.WriteLine("每个section中最贵的书籍:");
        while (mostExpensiveBooks.MoveNext())
        {
            string title = mostExpensiveBooks.Current.GetElementValue("title");
            Console.WriteLine("  " + title);
        }

        // 3. 多作者书籍
        XPathNodeIterator multiAuthorBooks = navigator.Select("//book[count(author) > 1]");
        Console.WriteLine("\n多作者书籍:");
        while (multiAuthorBooks.MoveNext())
        {
            string title = multiAuthorBooks.Current.GetElementValue("title");
            XPathNodeIterator authors = multiAuthorBooks.Current.Select("author");
            Console.WriteLine("  " + title);
            while (authors.MoveNext())
            {
                Console.WriteLine("    作者: " + authors.Current.Value);
            }
        }

        // 4. 页数与价格比率分析
        XPathNodeIterator goodValueBooks = navigator.Select("//book[number(pages) div number(price) > 10]");
        Console.WriteLine("\n页数与价格比率高的书籍 (>10页/美元):");
        while (goodValueBooks.MoveNext())
        {
            string title = goodValueBooks.Current.GetElementValue("title");
            double pages = goodValueBooks.Current.GetElementValue("pages").ToDouble();
            double price = goodValueBooks.Current.GetElementValue("price").ToDouble();
            double ratio = pages / price;
            Console.WriteLine("  " + title + " - 比率: " + ratio.ToString("F1"));
        }

        // 5. 使用XPath转换
        XPathExpression expr = navigator.Compile("//book[reviews/review/@rating >= 4]");
        expr.AddSort("reviews/review/@rating", XmlSortOrder.Descending, XmlCaseOrder.None, "", XmlDataType.Number);
        
        XPathNodeIterator highlyRatedBooks = navigator.Select(expr);
        Console.WriteLine("\n高评分书籍 (评分 >= 4，按评分排序):");
        while (highlyRatedBooks.MoveNext())
        {
            string title = highlyRatedBooks.Current.GetElementValue("title");
            XPathNodeIterator reviews = highlyRatedBooks.Current.Select("reviews/review");
            Console.WriteLine("  " + title);
            
            List<double> ratings = new List<double>();
            while (reviews.MoveNext())
            {
                double rating = reviews.Current.GetAttribute("rating").ToDouble();
                ratings.Add(rating);
                Console.WriteLine("    评分: " + rating);
            }
            
            if (ratings.Count > 0)
            {
                double avgRating = 0;
                foreach (double rating in ratings)
                {
                    avgRating += rating;
                }
                avgRating /= ratings.Count;
                Console.WriteLine("    平均评分: " + avgRating.ToString("F1"));
            }
        }

        // 6. 使用XPath计算
        XPathNodeIterator sections = navigator.Select("//section");
        Console.WriteLine("\n每个section的统计信息:");
        while (sections.MoveNext())
        {
            string sectionName = sections.Current.GetAttribute("name");
            Console.WriteLine("\n  Section: " + sectionName);
            
            // 书籍数量
            int bookCount = Convert.ToInt32((double)navigator.Evaluate(
                string.Format("count(//section[@name='{0}']/book)", sectionName)));
            Console.WriteLine("    书籍数量: " + bookCount);
            
            // 平均价格
            double avgPrice = (double)navigator.Evaluate(
                string.Format("sum(//section[@name='{0}']/book/price) div count(//section[@name='{0}']/book)", sectionName));
            Console.WriteLine("    平均价格: $" + avgPrice.ToString("F2"));
            
            // 总页数
            int totalPages = Convert.ToInt32((double)navigator.Evaluate(
                string.Format("sum(//section[@name='{0}']/book/pages)", sectionName)));
            Console.WriteLine("    总页数: " + totalPages);
        }
    }
}
```

## 6.5 实验验证

下面是一个综合的实验验证脚本，展示在不同语言中使用XPath处理同一XML文档的方法：

```python
# code/language-comparison/xpath_comparison.py
import subprocess
import os
import time

# 示例XML文档
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<library>
    <section name="programming">
        <book id="bk001" category="programming">
            <title>Effective Java</title>
            <author>Joshua Bloch</author>
            <year>2018</year>
            <price>45.99</price>
            <pages>416</pages>
        </book>
        <book id="bk002" category="programming">
            <title>Clean Code</title>
            <author>Robert C. Martin</author>
            <year>2008</year>
            <price>34.99</price>
            <pages>464</pages>
        </book>
    </section>
    <section name="database">
        <book id="bk003" category="database">
            <title>Database System Concepts</title>
            <author>Abraham Silberschatz</author>
            <author>Henry F. Korth</author>
            <author>S. Sudarshan</author>
            <year>2019</year>
            <price>89.99</price>
            <pages>1104</pages>
        </book>
    </section>
</library>
"""

def run_python_xpath():
    print("=" * 50)
    print("Python XPath实现")
    print("=" * 50)
    
    from lxml import etree
    
    # 解析XML
    root = etree.fromstring(xml_content)
    
    # XPath查询
    queries = [
        ("所有书籍标题", "//title/text()"),
        ("所有书籍价格", "//price/text()"),
        ("编程类书籍", "//section[@name='programming']/book/title/text()"),
        ("多作者书籍", "//book[count(author) > 1]/title/text()"),
        ("价格高于平均值的书籍", "//book[price > sum(//book/price) div count(//book)]/title/text()"),
        ("书籍总数", "count(//book)"),
        ("平均价格", "sum(//book/price) div count(//book)")
    ]
    
    for description, xpath_expr in queries:
        try:
            result = root.xpath(xpath_expr)
            print(f"{description}: {result}")
        except Exception as e:
            print(f"{description}: 错误 - {str(e)}")

def run_javascript_xpath():
    print("\n" + "=" * 50)
    print("JavaScript XPath实现")
    print("=" * 50)
    
    # 创建HTML文件包含JavaScript代码
    js_code = f"""
    <!DOCTYPE html>
    <html>
    <head><title>XPath Test</title></head>
    <body>
        <script>
        const xmlString = `{xml_content.replace(/`/g, '\\`')}`;
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlString, "text/xml");
        
        const results = [];
        
        queries = [
            ["所有书籍标题", "//title/text()"],
            ["所有书籍价格", "//price/text()"],
            ["编程类书籍", "//section[@name='programming']/book/title/text()"],
            ["多作者书籍", "//book[count(author) > 1]/title/text()"],
            ["价格高于平均值的书籍", "//book[price > sum(//book/price) div count(//book)]/title/text()"],
            ["书籍总数", "count(//book)"],
            ["平均价格", "sum(//book/price) div count(//book)"]
        ];
        
        for (const [description, xpath] of queries) {{
            try {{
                const result = xmlDoc.evaluate(xpath, xmlDoc, null, XPathResult.STRING_TYPE, null);
                results.push(description + ": " + result.stringValue);
            }} catch (e) {{
                results.push(description + ": 错误 - " + e.message);
            }}
        }}
        
        document.body.innerHTML = "<pre>" + results.join("\\n") + "</pre>";
        </script>
    </body>
    </html>
    """
    
    # 写入临时HTML文件
    with open("xpath_test.html", "w", encoding="utf-8") as f:
        f.write(js_code)
    
    print("JavaScript XPath测试已保存到 xpath_test.html，请在浏览器中打开查看结果")

def run_java_xpath():
    print("\n" + "=" * 50)
    print("Java XPath实现")
    print("=" * 50)
    
    # 创建Java源文件
    java_code = f"""
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;

public class XPathTest {{
    public static void main(String[] args) {{
        try {{
            String xmlString = "{xml_content.replace('"', '\\"').replace("\n", "\\n")}";
            
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document document = builder.parse(new java.io.ByteArrayInputStream(xmlString.getBytes()));
            
            XPathFactory xPathFactory = XPathFactory.newInstance();
            XPath xpath = xPathFactory.newXPath();
            
            String[][] queries = {{
                {{"所有书籍标题", "//title/text()"}},
                {{"所有书籍价格", "//price/text()"}},
                {{"编程类书籍", "//section[@name='programming']/book/title/text()"}},
                {{"多作者书籍", "//book[count(author) > 1]/title/text()"}},
                {{"价格高于平均值的书籍", "//book[price > sum(//book/price) div count(//book)]/title/text()"}},
                {{"书籍总数", "count(//book)"}},
                {{"平均价格", "sum(//book/price) div count(//book)"}}
            }};
            
            for (String[] query : queries) {{
                String description = query[0];
                String xpathExpr = query[1];
                
                try {{
                    XPathExpression expr = xpath.compile(xpathExpr);
                    Object result = expr.evaluate(document, XPathConstants.STRING);
                    System.out.println(description + ": " + result.toString());
                }} catch (Exception e) {{
                    System.out.println(description + ": 错误 - " + e.getMessage());
                }}
            }}
        }} catch (Exception e) {{
            e.printStackTrace();
        }}
    }}
}}
"""
    
    # 写入Java文件
    with open("XPathTest.java", "w", encoding="utf-8") as f:
        f.write(java_code)
    
    # 编译并运行Java代码（如果系统支持）
    try:
        # 编译Java代码
        compile_result = subprocess.run(["javac", "XPathTest.java"], capture_output=True, text=True)
        if compile_result.returncode != 0:
            print("Java编译失败:")
            print(compile_result.stderr)
        else:
            # 运行Java代码
            run_result = subprocess.run(["java", "XPathTest"], capture_output=True, text=True)
            print(run_result.stdout)
            if run_result.stderr:
                print("错误:")
                print(run_result.stderr)
    except FileNotFoundError:
        print("Java编译器未找到，跳过Java测试")

if __name__ == "__main__":
    print("XPath在不同语言中的实现比较")
    print("=" * 50)
    
    run_python_xpath()
    run_javascript_xpath()
    run_java_xpath()
    
    # 清理临时文件
    try:
        os.remove("XPathTest.class")
        os.remove("XPathTest.java")
    except:
        pass
    
    print("\n测试完成！")
    print("Python实现直接显示了结果。")
    print("JavaScript实现已保存到HTML文件，请在浏览器中打开查看。")
    print("Java实现需要系统安装JDK并配置好环境变量。")
```

## 6.6 本章小结

本章详细介绍了XPath在不同编程语言中的应用，包括：

- **Python中的XPath**：使用lxml库进行XML处理和XPath查询
- **JavaScript中的XPath**：在浏览器和Node.js环境中使用XPath
- **Java中的XPath**：使用Java标准库处理XML文档
- **C#/.NET中的XPath**：在.NET框架中使用XPath导航XML

通过本章学习，您应该能够：

1. 在不同编程语言环境中使用XPath
2. 处理带命名空间的XML文档
3. 实现复杂的XPath查询和数据处理
4. 构建跨平台的XPath解决方案
5. 选择最适合您项目需求的XPath实现方式

下一章我们将学习XPath的性能优化与最佳实践，这将帮助您编写更高效、更可靠的XPath表达式。

## 6.7 练习

1. 使用Python的lxml库实现一个XML文档分析器，可以统计元素类型、属性使用情况等
2. 使用JavaScript编写一个浏览器扩展，可以使用XPath高亮和提取网页中的特定内容
3. 使用Java实现一个XML配置文件验证工具，可以检查配置项的完整性和一致性
4. 使用C#编写一个XML数据转换工具，可以使用XPath提取和重组数据
5. 比较不同语言中XPath实现的性能特点，并给出各自的优势和劣势

尝试运行本章中的示例代码，并根据实际需求进行修改和扩展。