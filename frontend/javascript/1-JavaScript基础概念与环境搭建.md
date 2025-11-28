# 第1章：JavaScript基础概念与环境搭建

## 1.1 JavaScript是什么？

### 1.1.1 JavaScript的定义

JavaScript是一种高级的、解释型的、多范式的编程语言，最初由Brendan Eich在1995年用仅仅10天时间创建。尽管名字中包含"Java"，但JavaScript与Java是完全不同的编程语言。

JavaScript的设计目标是在网页中添加交互性和动态功能，使网页不再是静态的HTML页面，而是可以响应用户操作的动态界面。

### 1.1.2 JavaScript的历史

| 时间 | 事件 |
|------|------|
| 1995年 | Brendan Eich在Netscape创建了JavaScript（最初叫LiveScript） |
| 1997年 | ECMAScript标准（ES1）发布，统一了JavaScript的语言规范 |
| 1998年 | ECMAScript 2（ES2）发布 |
| 1999年 | ECMAScript 3（ES3）发布，成为广泛支持的版本 |
| 2009年 | ECMAScript 5（ES5）发布，增加了"严格模式"等功能 |
| 2015年 | ECMAScript 2015（ES6）发布，这是一个重大更新，引入了许多新特性 |
| 2016年至今 | 每年发布一个新版本（ES2016, ES2017等） |

### 1.1.3 JavaScript的应用领域

JavaScript最初是为浏览器设计的，但现在已经扩展到多个领域：

1. **Web前端开发** - 这是JavaScript最经典的应用领域
2. **后端开发** - 通过Node.js，JavaScript可以运行在服务器端
3. **移动应用开发** - 使用React Native、Ionic等框架
4. **桌面应用开发** - 使用Electron、NW.js等框架
5. **物联网(IoT)** - 嵌入式设备上的JavaScript
6. **区块链开发** - 智能合约开发

## 1.2 JavaScript运行环境

### 1.2.1 浏览器环境

JavaScript最原始的运行环境是Web浏览器。浏览器内置了JavaScript引擎，负责解析和执行JavaScript代码。

主流浏览器的JavaScript引擎：
- **V8引擎** - Google Chrome、Node.js使用
- **SpiderMonkey** - Mozilla Firefox使用
- **JavaScriptCore** - Apple Safari使用
- **Chakra** - Microsoft Edge（旧版）使用

### 1.2.2 服务器端环境

Node.js是JavaScript在服务器端的主要运行环境，它使用V8引擎并提供了一系列服务器端API，如文件系统访问、网络通信等。

### 1.3 开发环境搭建

### 1.3.1 基础开发环境

对于JavaScript初学者，最简单的开发环境只需要：
1. 一个文本编辑器（如VS Code、Sublime Text、Notepad++）
2. 一个现代Web浏览器（如Chrome、Firefox、Safari、Edge）

### 1.3.2 推荐开发工具

#### 文本编辑器/IDE
**Visual Studio Code (VS Code)** 是目前最受欢迎的JavaScript开发工具，具有以下优势：
- 轻量级但功能强大
- 丰富的插件生态系统
- 内置调试功能
- Git集成
- 智能代码补全

推荐的VS Code插件：
- **Live Server** - 实时预览网页
- **Prettier** - 代码格式化
- **ESLint** - 代码质量检查
- **JavaScript (ES6) code snippets** - ES6代码片段
- **Auto Rename Tag** - 自动重命名配对HTML标签

#### 浏览器开发者工具
所有现代浏览器都内置了开发者工具，提供以下功能：
- **Console** - 执行JavaScript代码和查看日志
- **Elements** - 检查和修改HTML/CSS
- **Network** - 监控网络请求
- **Sources** - 调试JavaScript代码
- **Performance** - 性能分析

### 1.3.3 环境配置步骤

1. **安装VS Code**
   - 访问 https://code.visualstudio.com/
   - 下载并安装适合您操作系统的版本

2. **安装浏览器**
   - 推荐使用Chrome或Firefox，它们拥有强大的开发者工具

3. **安装Node.js（可选）**
   - 访问 https://nodejs.org/
   - 下载并安装LTS（长期支持）版本
   - Node.js包含了npm（Node包管理器）

4. **配置VS Code**
   - 安装推荐的插件
   - 设置合适的主题和字体

## 1.4 第一个JavaScript程序

### 1.4.1 在HTML中嵌入JavaScript

最简单的运行JavaScript的方式是在HTML文件中直接编写代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的第一个JavaScript程序</title>
</head>
<body>
    <h1>JavaScript入门示例</h1>
    
    <script>
        // 这是我的第一个JavaScript程序
        console.log('Hello, JavaScript!');
        
        // 在页面中显示消息
        document.write('<p>这是由JavaScript生成的文本</p>');
        
        // 使用alert显示对话框
        // alert('欢迎学习JavaScript!');
    </script>
    
    <button onclick="showMessage()">点击我</button>
    
    <script>
        function showMessage() {
            alert('你点击了按钮!');
        }
    </script>
</body>
</html>
```

### 1.4.2 使用外部JavaScript文件

为了更好的代码组织，通常将JavaScript代码放在单独的文件中：

**index.html**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>外部JavaScript示例</title>
</head>
<body>
    <h1>使用外部JavaScript文件</h1>
    <button id="myButton">点击我</button>
    
    <!-- 引入外部JavaScript文件 -->
    <script src="script.js"></script>
</body>
</html>
```

**script.js**
```javascript
// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 获取按钮元素
    const button = document.getElementById('myButton');
    
    // 为按钮添加点击事件
    button.addEventListener('click', function() {
        // 创建一个新的段落元素
        const paragraph = document.createElement('p');
        paragraph.textContent = '按钮被点击了！时间：' + new Date().toLocaleTimeString();
        
        // 将段落添加到页面
        document.body.appendChild(paragraph);
    });
});

console.log('JavaScript文件已加载');
```

### 1.4.3 使用浏览器控制台

浏览器控制台是学习和测试JavaScript代码的好地方：

1. 打开浏览器开发者工具（F12或右键→检查）
2. 切换到"Console"（控制台）标签
3. 直接输入JavaScript代码并按Enter执行

示例代码：
```javascript
// 简单计算
1 + 2
Math.sqrt(16)

// 创建变量
let message = 'Hello, Console!';
console.log(message);

// 创建函数
function greet(name) {
    return '你好，' + name + '！';
}

greet('JavaScript学习者');
```

## 1.5 JavaScript代码的基本组成

### 1.5.1 语句与表达式

JavaScript代码由语句组成，语句是执行操作的指令。表达式是能产生值的代码片段。

```javascript
// 语句
let x = 10;      // 声明语句
if (x > 5) {     // 条件语句
    console.log('x大于5');
}

// 表达式
10 + 5           // 算术表达式，结果为15
x * 2            // 变量表达式，结果为20
'Message ' + x   // 字符串连接表达式，结果为"Message 10"
```

### 1.5.2 注释

注释是代码中的说明文字，不会被执行，用于提高代码可读性：

```javascript
// 单行注释

/* 
   多行注释
   可以跨越多行
*/

/**
 * 文档注释
 * 通常用于函数和类的说明
 * @param {string} name - 用户名
 * @returns {string} 问候语
 */
function greetUser(name) {
    return '你好，' + name;
}
```

### 1.5.3 大小写敏感

JavaScript是大小写敏感的语言：

```javascript
let myVariable = 10;
// 下面这行会报错，因为myvariable与myVariable不同
// console.log(myvariable); // ReferenceError: myvariable is not defined
```

## 1.6 调试技巧

### 1.6.1 使用console.log()

`console.log()`是最简单的调试方法，可以输出变量的值：

```javascript
let user = {
    name: '张三',
    age: 25,
    skills: ['JavaScript', 'HTML', 'CSS']
};

// 查看对象内容
console.log(user);

// 使用表格形式查看对象
console.table(user);

// 查看特定属性
console.log('用户姓名:', user.name);
console.log('用户年龄:', user.age);
```

### 1.6.2 使用断点调试

现代浏览器的开发者工具支持断点调试：

1. 在Sources面板中打开JavaScript文件
2. 点击行号左侧设置断点
3. 刷新页面或触发相应操作
4. 代码会在断点处暂停
5. 可以查看变量值、单步执行代码

### 1.6.3 使用debugger语句

在代码中插入`debugger`语句，当代码执行到这一行时会自动暂停：

```javascript
function calculateSum(numbers) {
    let sum = 0;
    debugger; // 代码执行到这里会暂停
    for (let i = 0; i < numbers.length; i++) {
        sum += numbers[i];
    }
    return sum;
}

calculateSum([1, 2, 3, 4, 5]);
```

## 1.7 开发最佳实践

### 1.7.1 代码风格

1. **使用有意义的变量名**
   ```javascript
   // 好的命名
   let userAge = 25;
   let isLoggedIn = true;
   
   // 不好的命名
   let a = 25;
   let b = true;
   ```

2. **使用适当的缩进**（通常2或4个空格）
   ```javascript
   function calculatePrice(quantity, unitPrice) {
       if (quantity > 10) {
           return quantity * unitPrice * 0.9; // 10%折扣
       } else {
           return quantity * unitPrice;
       }
   }
   ```

3. **添加适当的注释**
   ```javascript
   // 计算折扣后的总价
   // 如果购买数量超过10，给予10%的折扣
   function calculateDiscountPrice(quantity, unitPrice) {
       if (quantity > 10) {
           // 应用10%折扣
           return quantity * unitPrice * 0.9;
       } else {
           // 无折扣
           return quantity * unitPrice;
       }
   }
   ```

### 1.7.2 错误处理

使用`try...catch`语句处理可能的错误：

```javascript
try {
    // 尝试执行的代码
    let data = JSON.parse(invalidJSON);
    console.log(data);
} catch (error) {
    // 如果发生错误，执行这里的代码
    console.error('解析JSON时出错:', error.message);
}
```

### 1.7.3 性能考虑

1. **避免全局变量**
   ```javascript
   // 不推荐：全局变量
   counter = 0;
   
   // 推荐：使用局部变量
   function initializeCounter() {
       let counter = 0;
       return counter;
   }
   ```

2. **合理使用循环**
   ```javascript
   // 不推荐：在循环中重复计算
   for (let i = 0; i < array.length; i++) {
       // 使用array.length
   }
   
   // 推荐：缓存长度
   const len = array.length;
   for (let i = 0; i < len; i++) {
       // 使用缓存的len
   }
   ```

## 1.8 总结

本章介绍了JavaScript的基础知识和开发环境搭建，主要包括：

1. JavaScript的定义、历史和应用领域
2. 不同的JavaScript运行环境（浏览器和服务器）
3. 开发环境的选择和配置
4. 如何编写和运行第一个JavaScript程序
5. JavaScript代码的基本组成（语句、表达式、注释等）
6. 基本的调试技巧
7. 开发最佳实践

通过本章的学习，您应该已经了解了JavaScript的基本概念，并且能够搭建基本的开发环境，编写简单的JavaScript程序。在下一章中，我们将深入探讨JavaScript的语法和数据类型。

## 1.9 练习

1. 创建一个HTML文件，包含一个按钮，当点击按钮时在控制台输出一条消息。
2. 创建一个外部JavaScript文件，并在HTML文件中引用它。
3. 尝试使用浏览器控制台执行一些基本的JavaScript代码，如变量声明和简单计算。
4. 尝试使用`console.log()`和`console.table()`输出不同类型的数据。
5. 设置一个断点并观察代码的执行过程。

## 1.10 参考资料

- [MDN JavaScript指南](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Guide)
- [JavaScript.info](https://javascript.info/)
- [ECMAScript规范](https://www.ecma-international.org/publications-and-standards/standards/ecma-262/)
- [Chrome开发者工具文档](https://developers.google.com/web/tools/chrome-devtools)