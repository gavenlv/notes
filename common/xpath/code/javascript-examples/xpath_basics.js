// JavaScript中的XPath基础示例
// 可以在浏览器控制台或Node.js环境中运行

// 示例XML文档
const xmlString = `<?xml version="1.0" encoding="UTF-8"?>
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
</bookstore>`;

// 解析XML文档
const parser = new DOMParser();
const xmlDoc = parser.parseFromString(xmlString, "text/xml");

// XPath执行函数
function executeXPath(xpathExpr, resultType = XPathResult.ORDERED_NODE_SNAPSHOT_TYPE) {
    return xmlDoc.evaluate(xpathExpr, xmlDoc, null, resultType, null);
}

// 输出结果函数
function logResults(title, results) {
    console.log(`\n${title}:`);
    console.log(`  XPath: ${results.expression}`);
    
    if (results.resultType === XPathResult.ORDERED_NODE_SNAPSHOT_TYPE) {
        console.log(`  结果数量: ${results.snapshotLength}`);
        
        for (let i = 0; i < Math.min(results.snapshotLength, 3); i++) {
            const node = results.snapshotItem(i);
            
            if (node.nodeType === Node.ELEMENT_NODE) {
                const text = node.textContent.trim();
                const attributes = Array.from(node.attributes)
                    .map(attr => `${attr.name}="${attr.value}"`)
                    .join(", ");
                
                if (text) {
                    console.log(`    ${i + 1}. ${node.tagName}(${attributes}) = "${text}"`);
                } else {
                    console.log(`    ${i + 1}. ${node.tagName}(${attributes})`);
                }
            } else if (node.nodeType === Node.ATTRIBUTE_NODE) {
                console.log(`    ${i + 1}. @${node.name} = "${node.value}"`);
            } else {
                console.log(`    ${i + 1}. ${node.nodeValue}`);
            }
        }
    } else if (results.resultType === XPathResult.STRING_TYPE) {
        console.log(`  结果: "${results.stringValue}"`);
    } else if (results.resultType === XPathResult.NUMBER_TYPE) {
        console.log(`  结果: ${results.numberValue}`);
    } else if (results.resultType === XPathResult.BOOLEAN_TYPE) {
        console.log(`  结果: ${results.booleanValue}`);
    }
}

// 基础XPath演示
function demonstrateXPathBasics() {
    console.log("=" * 60);
    console.log("JavaScript中的XPath基础演示");
    console.log("=" * 60);
    
    // 1. 节点选择
    console.log("\n1. 节点选择:");
    console.log("-".repeat(40));
    
    // 选择所有book元素
    let result = executeXPath("//book");
    result.expression = "//book";
    logResults("选择所有book元素", result);
    
    // 选择所有title元素
    result = executeXPath("//title");
    result.expression = "//title";
    logResults("选择所有title元素", result);
    
    // 选择所有author元素
    result = executeXPath("//author");
    result.expression = "//author";
    logResults("选择所有author元素", result);
    
    // 2. 谓语使用
    console.log("\n\n2. 谓语使用:");
    console.log("-".repeat(40));
    
    // 第一个book元素
    result = executeXPath("//book[1]");
    result.expression = "//book[1]";
    logResults("第一个book元素", result);
    
    // 最后一个book元素
    result = executeXPath("//book[last()]");
    result.expression = "//book[last()]";
    logResults("最后一个book元素", result);
    
    // 属性为web的book
    result = executeXPath("//book[@category='web']");
    result.expression = "//book[@category='web']";
    logResults("属性category为'web'的book", result);
    
    // 价格大于35的book
    result = executeXPath("//book[price > 35]");
    result.expression = "//book[price > 35]";
    logResults("价格大于35的book", result);
    
    // 3. 未知节点选择
    console.log("\n\n3. 未知节点选择:");
    console.log("-".repeat(40));
    
    // 所有book元素
    result = executeXPath("/bookstore/*");
    result.expression = "/bookstore/*";
    logResults("bookstore的所有子元素", result);
    
    // 所有元素
    result = executeXPath("//*");
    result.expression = "//*";
    logResults("文档中的所有元素", result);
    
    // 所有具有category属性的book
    result = executeXPath("//book[@category]");
    result.expression = "//book[@category]";
    logResults("所有具有category属性的book", result);
    
    // 4. 路径操作
    console.log("\n\n4. 路径操作:");
    console.log("-".repeat(40));
    
    // 从根节点选择book
    result = executeXPath("/bookstore/book");
    result.expression = "/bookstore/book";
    logResults("从根节点选择book", result);
    
    // 所有book的title
    result = executeXPath("//book/title");
    result.expression = "//book/title";
    logResults("所有book的title", result);
    
    // 所有title的文本
    result = executeXPath("//title/text()");
    result.expression = "//title/text()";
    logResults("所有title的文本内容", result);
    
    // 5. 轴操作
    console.log("\n\n5. 轴操作:");
    console.log("-".repeat(40));
    
    // 第一个book的所有子元素
    result = executeXPath("//book[1]/*");
    result.expression = "//book[1]/*";
    logResults("第一个book的所有子元素", result);
    
    // 第一个book的父元素
    result = executeXPath("//book[1]/..");
    result.expression = "//book[1]/..";
    logResults("第一个book的父元素", result);
    
    // 第一个book的所有后代元素
    result = executeXPath("//book[1]//*");
    result.expression = "//book[1]//*";
    logResults("第一个book的所有后代元素", result);
    
    // 6. 运算符
    console.log("\n\n6. 运算符:");
    console.log("-".repeat(40));
    
    // 价格等于29.99的book
    result = executeXPath("//book[price = 29.99]");
    result.expression = "//book[price = 29.99]";
    logResults("价格等于29.99的book", result);
    
    // 价格不等于39.95的book
    result = executeXPath("//book[price != 39.95]");
    result.expression = "//book[price != 39.95]";
    logResults("价格不等于39.95的book", result);
    
    // 价格小于40的book
    result = executeXPath("//book[price < 40]");
    result.expression = "//book[price < 40]";
    logResults("价格小于40的book", result);
    
    // 7. 函数演示
    console.log("\n\n7. 函数演示:");
    console.log("-".repeat(40));
    
    // 计算book数量
    result = executeXPath("count(//book)", XPathResult.NUMBER_TYPE);
    result.expression = "count(//book)";
    logResults("计算book数量", result);
    
    // 计算平均价格
    result = executeXPath("sum(//book/price) div count(//book)", XPathResult.NUMBER_TYPE);
    result.expression = "sum(//book/price) div count(//book)";
    logResults("计算平均价格", result);
    
    // 字符串长度
    result = executeXPath("string-length(//book[1]/title)", XPathResult.NUMBER_TYPE);
    result.expression = "string-length(//book[1]/title)";
    logResults("第一个book的标题长度", result);
}

// 浏览器控制台中的XPath测试
function browserConsoleTests() {
    console.log("\n" + "=".repeat(60));
    console.log("浏览器控制台XPath测试示例");
    console.log("=".repeat(60));
    
    console.log("\n在浏览器控制台中使用以下命令:");
    
    console.log("\n// 基本选择:");
    console.log("$x('//title'); // 获取所有标题");
    console.log("$x('//book[1]'); // 获取第一本书");
    console.log("$x('//book[@category=\"web\"]'); // 获取web类别的书");
    
    console.log("\n// 组合选择:");
    console.log("$x('//title | //author'); // 获取标题和作者");
    console.log("$x('//book[price>30][@category=\"web\"]'); // 30元以上web类别的书");
    
    console.log("\n// 高级选择:");
    console.log("$x('//book[count(author)>1]'); // 多作者的书");
    console.log("$x('//*[contains(text(), \"XML\")]'); // 包含XML文本的元素");
    
    console.log("\n// 轴操作:");
    console.log("$x('//title/ancestor::*'); // 标题的所有祖先元素");
    console.log("$x('//title/following::*'); // 标题之后的所有元素");
    console.log("$x('//title/preceding-sibling::*'); // 标题之前的兄弟元素");
}

// 交互式XPath测试（仅限浏览器环境）
function interactiveXPathTest() {
    if (typeof window === 'undefined') {
        console.log("交互式XPath测试仅适用于浏览器环境");
        return;
    }
    
    // 创建一个简单的HTML界面用于测试
    const html = `
    <div id="xpath-tester">
        <h2>交互式XPath测试</h2>
        <p>输入XPath表达式测试结果:</p>
        <textarea id="xpath-input" rows="2" cols="80" placeholder="//title">//$x('//title')</textarea>
        <br>
        <button id="execute-btn">执行XPath</button>
        <br>
        <div id="xpath-result" style="margin-top: 10px; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9; min-height: 100px;">
            结果将显示在这里...
        </div>
    </div>
    `;
    
    // 检查是否已存在测试器
    if (!document.getElementById('xpath-tester')) {
        const container = document.createElement('div');
        container.innerHTML = html;
        document.body.appendChild(container);
        
        // 添加事件监听器
        document.getElementById('execute-btn').addEventListener('click', function() {
            const input = document.getElementById('xpath-input').value;
            const resultDiv = document.getElementById('xpath-result');
            
            if (!input) {
                resultDiv.innerHTML = "请输入XPath表达式";
                return;
            }
            
            try {
                const results = executeXPath(input);
                resultDiv.innerHTML = `
                    <h4>XPath表达式: ${input}</h4>
                    <h5>结果 (${results.snapshotLength} 个):</h5>
                    <ul>
                        ${Array.from({length: results.snapshotLength}, (_, i) => {
                            const node = results.snapshotItem(i);
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                return `<li>${node.tagName} = "${node.textContent.trim()}"</li>`;
                            } else {
                                return `<li>"${node.nodeValue}"</li>`;
                            }
                        }).join('')}
                    </ul>
                `;
            } catch (e) {
                resultDiv.innerHTML = `
                    <h4>XPath表达式: ${input}</h4>
                    <h5>错误:</h5>
                    <p>${e.message}</p>
                `;
            }
        });
    }
}

// 运行演示
if (typeof window !== 'undefined') {
    // 浏览器环境
    demonstrateXPathBasics();
    browserConsoleTests();
    // interactiveXPathTest(); // 取消注释以启用交互式测试
} else {
    // Node.js环境
    try {
        const { DOMParser } = require('xmldom');
        global.DOMParser = DOMParser;
        demonstrateXPathBasics();
    } catch (e) {
        console.log("在Node.js中运行需要安装xmldom包: npm install xmldom");
    }
}

// 导出函数供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        executeXPath,
        demonstrateXPathBasics,
        browserConsoleTests,
        interactiveXPathTest
    };
}