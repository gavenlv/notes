# 第7章：XPath性能优化与最佳实践

## 7.1 XPath性能基础

### 7.1.1 XPath执行过程

理解XPath的执行过程是优化的基础。XPath查询通常经过以下步骤：

1. **解析阶段**：解析XPath表达式为内部表示形式
2. **优化阶段**：优化查询执行计划（部分引擎支持）
3. **执行阶段**：在XML文档上执行查询
4. **结果构建阶段**：构建和返回结果集

### 7.1.2 性能影响因素

影响XPath性能的主要因素：

| 因素 | 影响程度 | 说明 |
|------|---------|------|
| 文档大小 | 高 | 文档越大，遍历成本越高 |
| 路径复杂度 | 高 | 复杂路径表达式需要更多遍历 |
| 谓语数量 | 中高 | 谓语增加筛选成本 |
| 函数调用 | 中 | 函数执行增加计算开销 |
| 命名空间处理 | 中 | 命名空间解析增加复杂度 |
| 索引支持 | 极高 | 有索引的查询性能显著提升 |

## 7.2 XPath表达式优化

### 7.2.1 路径优化原则

#### 优先使用绝对路径

```xpath
# 好的做法 - 直接路径
/library/section/book/title

# 不好的做法 - 文档全局搜索
//title

# 如果文档很大且结构固定，绝对路径更高效
```

#### 避免过度使用通配符

```xpath
# 好的做法 - 指定具体元素名
/library/section/book

# 不好的做法 - 使用通配符
/library/*/*

# 通配符会匹配所有节点，增加不必要的遍历
```

#### 减少轴的使用

```xpath
# 好的做法 - 使用直接路径
/book/author

# 不好的做法 - 使用轴
/book/child::author

# 仅在需要复杂导航时使用轴
```

#### 避免深度遍历

```xpath
# 好的做法 - 限制搜索范围
/section[@name='programming']/book

# 不好的做法 - 全局深度搜索
//book[@category='programming']
```

### 7.2.2 谓语优化

#### 谓语顺序很重要

```xpath
# 好的做法 - 先缩小范围，再筛选属性
/section/book[@category='web'][price > 30]

# 不好的做法 - 先数值比较，再属性筛选
/section/book[price > 30][@category='web']

# 属性筛选通常比数值比较更快
```

#### 使用更高效的谓语

```xpath
# 好的做法 - 使用位置函数
/book[position() < 10]

# 不好的做法 - 使用计数函数
/book[count(preceding-sibling::*) < 10]

# position()比计算兄弟节点数量更高效
```

#### 避免重复计算

```xpath
# 好的做法 - 避免在谓语中重复路径
/book[price > 30 and category = 'web']

# 不好的做法 - 重复计算
/book[price > 30 and /book[price > 30]/category = 'web']
```

### 7.2.3 函数使用优化

#### 避免昂贵的函数调用

```xpath
# 好的做法 - 尽量使用简单比较
/book[contains(title, 'XML')]

# 不好的做法 - 复杂字符串操作
/book[translate(title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') = 'XML']

# translate函数比contains更昂贵
```

#### 合理使用字符串函数

```xpath
# 好的做法 - 使用starts-with
/book[starts-with(@id, 'bk')]

# 不好的做法 - 使用substring
/book[substring(@id, 1, 2) = 'bk']

# starts-with比substring更高效
```

## 7.3 文档结构优化

### 7.3.1 XML文档设计

#### 合理的嵌套层次

```xml
<!-- 好的做法 - 适当的嵌套层次 -->
<library>
    <section name="programming">
        <book id="bk001">
            <title>Effective Java</title>
            <author>Joshua Bloch</author>
        </book>
    </section>
</library>

<!-- 不好的做法 - 过深的嵌套 -->
<library>
    <metadata>
        <sections>
            <sectionGroup>
                <section name="programming">
                    <bookList>
                        <book>
                            <details>
                                <title>Effective Java</title>
                                <authors>
                                    <author>Joshua Bloch</author>
                                </authors>
                            </details>
                        </book>
                    </bookList>
                </section>
            </sectionGroup>
        </sections>
    </metadata>
</library>
```

#### 合理使用属性和元素

```xml
<!-- 适合用属性的情况：简单的标识信息 -->
<book id="bk001" category="programming" lang="en">
    <title>Effective Java</title>
    <author>Joshua Bloch</author>
</book>

<!-- 适合用元素的情况：复杂或多值信息 -->
<book id="bk001">
    <title>Effective Java</title>
    <authors>
        <author>Joshua Bloch</author>
        <author>Other Author</author>
    </authors>
</book>
```

#### 减少命名空间使用

```xml
<!-- 好的做法 - 最小化命名空间 -->
<bookstore xmlns:book="http://example.com/book">
    <book:book id="bk001">
        <book:title>Effective Java</book:title>
    </book:book>
</bookstore>

<!-- 不好的做法 - 过多命名空间 -->
<bookstore xmlns:book="http://example.com/book" 
           xmlns:meta="http://example.com/metadata" 
           xmlns:pub="http://example.com/publisher">
    <book:book>
        <book:title>Effective Java</book:title>
        <meta:metadata>
            <pub:publisher>...</pub:publisher>
        </meta:metadata>
    </book:book>
</bookstore>
```

### 7.3.2 文档分割策略

对于大型XML文档，考虑使用以下分割策略：

1. **按类别分割**
   ```xml
   <!-- 将大文档分割为多个小文档 -->
   <programming-books>
       <book id="bk001">...</book>
   </programming-books>
   
   <database-books>
       <book id="bk201">...</book>
   </database-books>
   ```

2. **按时间分割**
   ```xml
   <!-- 按年份分割数据 -->
   <books-2020>
       <book id="bk001">...</book>
   </books-2020>
   
   <books-2021>
       <book id="bk101">...</book>
   </books-2021>
   ```

3. **使用外部实体引用**
   ```xml
   <!-- 主文档 -->
   <library>
       &programming-books;
       &database-books;
   </library>
   
   <!-- 外部实体定义 -->
   <!DOCTYPE library [
       <!ENTITY programming-books SYSTEM "programming-books.xml">
       <!ENTITY database-books SYSTEM "database-books.xml">
   ]>
   ```

## 7.4 索引与缓存

### 7.4.1 XPath引擎索引支持

一些XPath引擎提供了索引支持，可以显著提升查询性能：

```python
# Python中的lxml索引示例
from lxml import etree

# 加载大型XML文档
doc = etree.parse("large_library.xml")

# 创建XPath查找器，自动为常用查询路径建立索引
finder = doc.xpath('/library/section/book/title | /library/section/book/author')

# 后续查询将利用索引，性能更好
titles = finder.xpath('/library/section/book/title/text()')
authors = finder.xpath('/library/section/book/author/text()')
```

### 7.4.2 自定义缓存策略

实现自定义缓存可以避免重复解析和查询：

```python
# code/performance-optimization/xpath_cache.py
from functools import lru_cache
from lxml import etree

class XPathProcessor:
    def __init__(self, xml_file):
        self.doc = etree.parse(xml_file)
    
    @lru_cache(maxsize=128)
    def cached_query(self, xpath_expr):
        """缓存XPath查询结果"""
        return self.doc.xpath(xpath_expr)
    
    def clear_cache(self):
        """清除缓存"""
        self.cached_query.cache_clear()
    
    def get_book_titles(self):
        """获取所有书籍标题"""
        return self.cached_query("//title/text()")
    
    def get_books_by_category(self, category):
        """获取特定类别的书籍"""
        return self.cached_query(f"//book[@category='{category}']/title/text()")

# 使用示例
processor = XPathProcessor("large_library.xml")

# 第一次查询，会执行并缓存结果
programming_titles = processor.get_books_by_category("programming")

# 后续相同查询，从缓存获取，性能更高
programming_titles_again = processor.get_books_by_category("programming")
```

### 7.4.3 查询结果预计算

对于常用查询，可以考虑预计算结果：

```python
# code/performance-optimization/precomputed_queries.py
from lxml import etree
import json
import os

class PrecomputedQueries:
    def __init__(self, xml_file, cache_file="xpath_cache.json"):
        self.xml_file = xml_file
        self.cache_file = cache_file
        self.doc = None
        self.cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """加载预计算缓存"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
    
    def _save_cache(self):
        """保存预计算缓存"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _get_document(self):
        """懒加载XML文档"""
        if self.doc is None:
            self.doc = etree.parse(self.xml_file)
        return self.doc
    
    def precompute_common_queries(self):
        """预计算常用查询"""
        doc = self._get_document()
        
        # 常用查询列表
        queries = {
            "all_titles": "//title/text()",
            "book_categories": "distinct-values(//book/@category)",  # XPath 2.0
            "books_by_category": {},  # 动态生成
            "max_price": "max(//book/price)",
            "min_price": "min(//book/price)",
            "avg_price": "sum(//book/price) div count(//book)"
        }
        
        # 执行并缓存查询结果
        for name, query in queries.items():
            if name == "books_by_category":
                # 特殊处理：按类别查询
                categories = doc.xpath("distinct-values(//book/@category)")
                for category in categories:
                    cat_query = f"//book[@category='{category}']/title/text()"
                    result = doc.xpath(cat_query)
                    queries[name][category] = result
            else:
                try:
                    result = doc.xpath(query)
                    queries[name] = result
                except:
                    queries[name] = None
        
        # 保存到缓存
        self.cache.update(queries)
        self._save_cache()
    
    def get_cached_result(self, query_name):
        """获取缓存结果"""
        return self.cache.get(query_name)
    
    def get_books_by_category(self, category):
        """获取特定类别的书籍（从缓存）"""
        return self.cache.get("books_by_category", {}).get(category)
    
    def invalidate_cache(self):
        """使缓存失效，重新加载文档"""
        self.doc = None
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

# 使用示例
precomputed = PrecomputedQueries("large_library.xml")

# 如果是新文档，预计算常用查询
if not precomputed.get_cached_result("all_titles"):
    precomputed.precompute_common_queries()

# 从缓存快速获取结果
programming_titles = precomputed.get_books_by_category("programming")
max_price = precomputed.get_cached_result("max_price")
```

## 7.5 XPath引擎特定优化

### 7.5.1 Python lxml优化

```python
# code/performance-optimization/lxml_optimization.py
from lxml import etree

class LxmlOptimizer:
    def __init__(self, xml_file):
        self.doc = etree.parse(xml_file)
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """设置lxml特定优化"""
        # 1. 使用迭代器处理大型节点集
        self.large_node_iterator = self.doc.xpath('//book', smart_strings=False)
        
        # 2. 创建XPath查找器
        self.finder = self.doc.xpath('//book', smart_strings=False)
    
    def get_all_titles_iterator(self):
        """使用迭代器高效处理大型节点集"""
        for book in self.large_node_iterator:
            title = book.xpath('string(title)')
            yield title
    
    def get_titles_using_finder(self):
        """使用查找器提高重复查询性能"""
        return self.finder.xpath('string(title)')
    
    def optimize_namespace_queries(self):
        """优化命名空间查询"""
        # 预定义命名空间映射
        self.ns_map = {
            'book': 'http://example.com/book'
        }
        
        # 使用预定义的命名空间映射
        return self.doc.xpath('//book:book/title/text()', namespaces=self.ns_map)
    
    def batch_process_books(self, batch_size=100):
        """批量处理书籍以提高效率"""
        books = self.doc.xpath('//book')
        results = []
        
        for i in range(0, len(books), batch_size):
            batch = books[i:i+batch_size]
            batch_results = []
            
            for book in batch:
                title = book.xpath('string(title)')
                price = book.xpath('number(price)')
                batch_results.append((title, price))
            
            results.extend(batch_results)
        
        return results
```

### 7.5.2 JavaScript DOM优化

```javascript
// code/performance-optimization/dom_optimization.js

class DOMXPathOptimizer {
    constructor(xmlString) {
        this.parser = new DOMParser();
        this.doc = this.parser.parseFromString(xmlString, "text/xml");
        this.setupOptimizations();
    }
    
    setupOptimizations() {
        // 1. 使用DocumentFragment处理大量节点
        this.fragment = document.createDocumentFragment();
        
        // 2. 缓存常用查询结果
        this.cache = new Map();
        
        // 3. 创建XPathEvaluator提高性能
        this.evaluator = new XPathEvaluator();
    }
    
    // 使用缓存避免重复查询
    cachedQuery(xpath, resultType = XPathResult.ORDERED_NODE_SNAPSHOT_TYPE) {
        if (this.cache.has(xpath)) {
            return this.cache.get(xpath);
        }
        
        const result = this.doc.evaluate(xpath, this.doc, null, resultType, null);
        this.cache.set(xpath, result);
        return result;
    }
    
    // 批量处理书籍
    batchProcessBooks() {
        const books = this.cachedQuery("//book");
        const results = [];
        
        for (let i = 0; i < books.snapshotLength; i++) {
            const book = books.snapshotItem(i);
            
            // 使用相对路径查询避免全局搜索
            const title = this.evaluator.evaluate("string(title)", book, null, 
                XPathResult.STRING_TYPE, null).stringValue;
            const price = this.evaluator.evaluate("number(price)", book, null, 
                XPathResult.NUMBER_TYPE, null).numberValue;
            
            results.push({title, price});
        }
        
        return results;
    }
    
    // 优化选择器性能
    getElementsByAttributeOptimized(tagName, attributeName, attributeValue) {
        // 使用XPath进行一次性选择
        const xpath = `//${tagName}[@${attributeName}='${attributeValue}']`;
        return this.cachedQuery(xpath);
    }
    
    // 高效处理大型文档
    processLargeDocumentInChunks(chunkSize = 100, processor) {
        const allBooks = this.cachedQuery("//book");
        const total = allBooks.snapshotLength;
        
        for (let i = 0; i < total; i += chunkSize) {
            const end = Math.min(i + chunkSize, total);
            const chunk = [];
            
            for (let j = i; j < end; j++) {
                chunk.push(allBooks.snapshotItem(j));
            }
            
            // 处理当前块
            processor(chunk, i / chunkSize);
            
            // 让浏览器有机会处理其他任务
            if (i % (chunkSize * 5) === 0) {
                setTimeout(() => {}, 0);
            }
        }
    }
}
```

### 7.5.3 Java XPath优化

```java
// code/performance-optimization/java_optimization.java
package com.example.xpath.optimization;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.*;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.ArrayList;

public class JavaXPathOptimizer {
    private Document document;
    private XPath xpath;
    private ConcurrentHashMap<String, XPathExpression> expressionCache;
    private ConcurrentHashMap<String, Object> resultCache;
    
    public JavaXPathOptimizer(String xmlFilePath) throws Exception {
        // 1. 高效解析XML
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);  // 启用命名空间支持
        
        DocumentBuilder builder = factory.newDocumentBuilder();
        document = builder.parse(xmlFilePath);
        
        // 2. 创建XPath对象
        XPathFactory xPathFactory = XPathFactory.newInstance();
        xpath = xPathFactory.newXPath();
        
        // 3. 初始化缓存
        expressionCache = new ConcurrentHashMap<>();
        resultCache = new ConcurrentHashMap<>();
    }
    
    // 缓存XPath表达式
    private XPathExpression getCompiledExpression(String xpathExpression) throws XPathExpressionException {
        return expressionCache.computeIfAbsent(xpathExpression, expr -> {
            try {
                return xpath.compile(expr);
            } catch (XPathExpressionException e) {
                throw new RuntimeException("Invalid XPath expression: " + expr, e);
            }
        });
    }
    
    // 执行缓存查询
    public Object evaluateXPath(String xpathExpression, QName returnType) throws Exception {
        String cacheKey = xpathExpression + ":" + returnType.toString();
        
        // 检查结果缓存
        if (resultCache.containsKey(cacheKey)) {
            return resultCache.get(cacheKey);
        }
        
        // 获取编译表达式
        XPathExpression expr = getCompiledExpression(xpathExpression);
        
        // 执行查询
        Object result = expr.evaluate(document, returnType);
        
        // 缓存结果（只缓存简单类型的结果）
        if (returnType == XPathConstants.STRING || 
            returnType == XPathConstants.NUMBER || 
            returnType == XPathConstants.BOOLEAN) {
            resultCache.put(cacheKey, result);
        }
        
        return result;
    }
    
    // 批量处理节点
    public List<BookInfo> batchProcessBooks(int batchSize) throws Exception {
        List<BookInfo> allBooks = new ArrayList<>();
        
        // 获取所有书籍节点
        NodeList bookNodes = (NodeList) evaluateXPath("//book", XPathConstants.NODESET);
        int total = bookNodes.getLength();
        
        // 批量处理
        for (int i = 0; i < total; i += batchSize) {
            int end = Math.min(i + batchSize, total);
            
            for (int j = i; j < end; j++) {
                Node bookNode = bookNodes.item(j);
                BookInfo bookInfo = extractBookInfo(bookNode);
                allBooks.add(bookInfo);
            }
            
            // 可选：在批处理间暂停，允许其他任务执行
            if (i % (batchSize * 5) == 0) {
                try {
                    Thread.sleep(10);  // 短暂暂停
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
        
        return allBooks;
    }
    
    // 提取书籍信息（使用相对路径避免全局搜索）
    private BookInfo extractBookInfo(Node bookNode) throws XPathExpressionException {
        String title = xpath.evaluate("string(title)", bookNode);
        String author = xpath.evaluate("string(author)", bookNode);
        Double price = (Double) xpath.evaluate("number(price)", bookNode);
        
        return new BookInfo(title, author, price);
    }
    
    // 清除缓存
    public void clearCaches() {
        expressionCache.clear();
        resultCache.clear();
    }
    
    // 书籍信息类
    public static class BookInfo {
        private String title;
        private String author;
        private Double price;
        
        public BookInfo(String title, String author, Double price) {
            this.title = title;
            this.author = author;
            this.price = price;
        }
        
        // getters...
        public String getTitle() { return title; }
        public String getAuthor() { return author; }
        public Double getPrice() { return price; }
    }
}
```

## 7.6 性能测试与监控

### 7.6.1 XPath性能测试框架

```python
# code/performance-optimization/xpath_benchmark.py
import time
import statistics
from lxml import etree
from typing import List, Tuple, Callable

class XPathBenchmark:
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.doc = etree.parse(xml_file)
        self.results = {}
    
    def benchmark_xpath(self, name: str, xpath_expr: str, iterations: int = 10) -> float:
        """对XPath表达式进行基准测试"""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            self.doc.xpath(xpath_expr)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times)
        
        self.results[name] = {
            'xpath': xpath_expr,
            'avg_time': avg_time,
            'std_dev': std_dev,
            'min_time': min(times),
            'max_time': max(times)
        }
        
        return avg_time
    
    def compare_expressions(self, test_cases: List[Tuple[str, str]], iterations: int = 10):
        """比较多个XPath表达式的性能"""
        print("XPath性能比较结果:")
        print("-" * 70)
        print(f"{'测试名称':<30} {'XPath':<40} {'平均时间(ms)':<15}")
        print("-" * 70)
        
        for name, xpath_expr in test_cases:
            avg_time_ms = self.benchmark_xpath(name, xpath_expr, iterations) * 1000
            print(f"{name:<30} {xpath_expr:<40} {avg_time_ms:<15.4f}")
        
        print("-" * 70)
        self.print_performance_ranking()
    
    def print_performance_ranking(self):
        """打印性能排名"""
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['avg_time'])
        
        print("\n性能排名 (从快到慢):")
        print("-" * 50)
        for i, (name, result) in enumerate(sorted_results, 1):
            print(f"{i}. {name}: {result['avg_time']*1000:.4f}ms")
    
    def generate_optimization_report(self, test_cases: List[Tuple[str, str]]):
        """生成优化建议报告"""
        self.compare_expressions(test_cases)
        
        print("\n优化建议:")
        print("-" * 50)
        
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['avg_time'])
        fastest = sorted_results[0][1]['avg_time']
        
        for name, result in sorted_results:
            relative_slowdown = result['avg_time'] / fastest
            xpath = result['xpath']
            
            suggestions = []
            
            # 检查常见问题并生成建议
            if '//' in xpath and not xpath.startswith('//'):
                suggestions.append("考虑使用更具体的路径替换'//'以减少搜索范围")
            
            if xpath.count('[') > 2:
                suggestions.append("谓语较多，考虑优化谓语顺序或减少谓语数量")
            
            if '*' in xpath:
                suggestions.append("通配符'*'可能降低性能，考虑使用具体元素名")
            
            if 'translate(' in xpath:
                suggestions.append("translate函数较为昂贵，考虑使用contains或starts-with替代")
            
            if 'count(' in xpath and '[position()' not in xpath:
                suggestions.append("在适用情况下，position()可能比count()更高效")
            
            if suggestions:
                print(f"\n{name} (相对速度: {relative_slowdown:.2f}x):")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")

# 使用示例
def run_benchmark():
    # 生成测试用例
    test_cases = [
        ("绝对路径", "/library/section/book/title/text()"),
        ("全局搜索", "//title/text()"),
        ("通配符路径", "/library/*/*/title/text()"),
        ("复杂谓语", "/library/section/book[@category='programming' and price > 30]/title/text()"),
        ("谓语顺序1", "/library/section/book[@category='web' and price > 30]/title/text()"),
        ("谓语顺序2", "/library/section/book[price > 30 and @category='web']/title/text()"),
        ("位置函数", "/library/section/book[position() < 5]/title/text()"),
        ("计数函数", "/library/section/book[count(preceding-sibling::*) < 5]/title/text()"),
        ("translate函数", "/library/section/book[translate(title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') = 'XML']/title/text()"),
        ("contains函数", "/library/section/book[contains(translate(title, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'XML')]/title/text()")
    ]
    
    # 创建基准测试实例
    benchmark = XPathBenchmark("large_library.xml")
    
    # 运行比较测试
    benchmark.compare_expressions(test_cases)
    
    # 生成优化报告
    benchmark.generate_optimization_report(test_cases)

if __name__ == "__main__":
    run_benchmark()
```

## 7.7 实验验证

让我们创建一个综合实验，演示XPath性能优化的各种技巧：

```python
# code/performance-optimization/xpath_optimization_demo.py
import time
import random
from lxml import etree

def generate_large_xml(num_books=10000, categories=None):
    """生成大型XML文档用于性能测试"""
    if categories is None:
        categories = ['programming', 'database', 'web', 'data-science', 'ai']
    
    root = etree.Element("library")
    
    for i in range(num_books):
        book = etree.SubElement(root, "book")
        book.set("id", f"bk{i:05d}")
        book.set("category", random.choice(categories))
        
        title = etree.SubElement(book, "title")
        title.text = f"Book Title {i}"
        
        author = etree.SubElement(book, "author")
        author.text = f"Author {random.randint(1, 500)}"
        
        year = etree.SubElement(book, "year")
        year.text = str(random.randint(1990, 2023))
        
        price = etree.SubElement(book, "price")
        price.text = f"{random.uniform(10, 100):.2f}"
        
        pages = etree.SubElement(book, "pages")
        pages.text = str(random.randint(100, 1000))
        
        # 添加更多元素使文档更复杂
        publisher = etree.SubElement(book, "publisher")
        publisher.text = f"Publisher {random.randint(1, 50)}"
        
        isbn = etree.SubElement(book, "isbn")
        isbn.text = f"{random.randint(1000000000, 9999999999)}"
    
    return etree.ElementTree(root)

def test_optimization_techniques():
    """测试各种XPath优化技巧"""
    print("生成测试XML文档...")
    xml_doc = generate_large_xml(5000)  # 生成5000本书的文档
    
    # 测试用例
    test_cases = [
        ("1. 使用绝对路径", "/library/book/title/text()", "//title/text()"),
        ("2. 避免通配符", "/library/book/title/text()", "/library/*/title/text()"),
        ("3. 谓语顺序优化", "/library/book[@category='programming' and price > 50]/title/text()", 
                               "/library/book[price > 50 and @category='programming']/title/text()"),
        ("4. 位置vs计数", "/library/book[position() < 10]/title/text()", 
                            "/library/book[count(preceding-sibling::*) < 10]/title/text()"),
        ("5. 字符串函数比较", "/library/book[contains(title, '100')]/title/text()", 
                               "/library/book[translate(title, '0123456789', '##########') = '###']/title/text()")
    ]
    
    print("开始性能测试...")
    print("=" * 80)
    print(f"{'测试名称':<40} {'优化前(ms)':<15} {'优化后(ms)':<15} {'性能提升':<15}")
    print("=" * 80)
    
    for name, optimized_expr, unoptimized_expr in test_cases:
        # 测试优化后的表达式
        opt_times = []
        for _ in range(10):
            start_time = time.time()
            xml_doc.xpath(optimized_expr)
            opt_times.append(time.time() - start_time)
        
        # 测试未优化的表达式
        unopt_times = []
        for _ in range(10):
            start_time = time.time()
            xml_doc.xpath(unoptimized_expr)
            unopt_times.append(time.time() - start_time)
        
        opt_avg = sum(opt_times) / len(opt_times) * 1000  # 转换为毫秒
        unopt_avg = sum(unopt_times) / len(unopt_times) * 1000  # 转换为毫秒
        improvement = (unopt_avg - opt_avg) / unopt_avg * 100  # 性能提升百分比
        
        print(f"{name:<40} {unopt_avg:<15.4f} {opt_avg:<15.4f} {improvement:<15.2f}%")
    
    print("=" * 80)
    
    # 缓存测试
    print("\n测试XPath缓存效果...")
    
    class XPathCache:
        def __init__(self, doc):
            self.doc = doc
            self.cache = {}
        
        def cached_query(self, xpath_expr):
            if xpath_expr not in self.cache:
                self.cache[xpath_expr] = self.doc.xpath(xpath_expr)
            return self.cache[xpath_expr]
    
    cache = XPathCache(xml_doc)
    
    # 测试复杂查询
    complex_query = "/library/book[@category='programming' and price > 30 and year > 2000]"
    
    # 不使用缓存
    start_time = time.time()
    for _ in range(100):
        xml_doc.xpath(complex_query)
    no_cache_time = time.time() - start_time
    
    # 使用缓存
    start_time = time.time()
    for _ in range(100):
        cache.cached_query(complex_query)
    cache_time = time.time() - start_time
    
    cache_improvement = (no_cache_time - cache_time) / no_cache_time * 100
    
    print(f"复杂查询执行100次:")
    print(f"  不使用缓存: {no_cache_time:.4f}秒")
    print(f"  使用缓存: {cache_time:.4f}秒")
    print(f"  性能提升: {cache_improvement:.2f}%")
    
    # 批量处理测试
    print("\n测试批量处理效果...")
    
    # 获取所有书籍
    all_books = xml_doc.xpath("//book")
    
    # 单个处理
    start_time = time.time()
    titles = []
    for book in all_books:
        titles.append(book.xpath("string(title)"))
    single_process_time = time.time() - start_time
    
    # 批量处理
    start_time = time.time()
    batch_titles = xml_doc.xpath("//book/string(title)")
    batch_process_time = time.time() - start_time
    
    batch_improvement = (single_process_time - batch_process_time) / single_process_time * 100
    
    print(f"处理所有书籍标题:")
    print(f"  单个处理: {single_process_time:.4f}秒")
    print(f"  批量处理: {batch_process_time:.4f}秒")
    print(f"  性能提升: {batch_improvement:.2f}%")
    
    print("\n性能测试完成！")

if __name__ == "__main__":
    test_optimization_techniques()
```

## 7.8 本章小结

本章详细介绍了XPath性能优化与最佳实践，包括：

- **XPath表达式优化**：路径优化、谓语优化、函数使用优化
- **文档结构优化**：合理设计XML结构、文档分割策略
- **索引与缓存**：XPath引擎索引支持、自定义缓存、查询预计算
- **引擎特定优化**：Python lxml、JavaScript DOM、Java XPath的优化技巧
- **性能测试与监控**：XPath性能测试框架、优化建议生成

通过本章学习，您应该能够：

1. 识别和避免XPath性能陷阱
2. 编写高效的XPath表达式
3. 设计适合XPath查询的XML文档结构
4. 实现XPath查询缓存和优化机制
5. 测试和监控XPath性能

下一章我们将通过实战案例来巩固和应用所学的XPath知识，展示如何在实际项目中使用XPath解决复杂问题。

## 7.9 练习

1. 编写一个XPath性能测试工具，可以比较不同XPath表达式的执行时间
2. 实现一个XPath表达式优化器，可以自动识别和改进常见的性能问题
3. 设计一个XML文档结构，针对特定的查询场景进行优化
4. 实现一个XPath查询缓存系统，支持智能缓存失效策略
5. 分析一个大型XML文档的查询模式，并提出优化建议

尝试运行本章中的示例代码，并根据您的实际需求进行修改和扩展。