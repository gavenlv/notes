# JavaScript基础

## 章节概述
JavaScript是一种跨平台的脚本语言，主要用于为网页添加交互功能。作为前端开发的核心技术之一，JavaScript不仅可以在浏览器中运行，还可以在服务器端(Node.js)、移动应用和嵌入式设备上运行。本章将介绍JavaScript的基础知识，包括语法、数据类型、控制流程、函数、对象、DOM操作等核心概念。

## 目录结构
- [JavaScript基础概述](#javascript基础概述)
- [JavaScript语法基础](#javascript语法基础)
- [数据类型与变量](#数据类型与变量)
- [运算符与表达式](#运算符与表达式)
- [控制流程](#控制流程)
- [函数](#函数)
- [数组](#数组)
- [对象](#对象)
- [DOM操作基础](#dom操作基础)
- [事件处理](#事件处理)
- [异步编程基础](#异步编程基础)
- [错误处理](#错误处理)
- [JavaScript最佳实践](#javascript最佳实践)
- [练习题](#练习题)
- [学习资源](#学习资源)

## JavaScript基础概述

### JavaScript的发展历史
JavaScript由Netscape公司的Brendan Eich于1995年创建，最初名为LiveScript，后更名为JavaScript。1997年，JavaScript 1.0被提交给欧洲计算机制造商协会(ECMA)，并制定了ECMAScript标准。此后，JavaScript不断发展，主要版本包括：

- ECMAScript 3 (1999)：成为广泛支持的标准
- ECMAScript 5 (2009)：添加了严格模式、JSON支持等新特性
- ECMAScript 6/2015：引入了箭头函数、类、模块等重大改进
- ECMAScript 2016-2023：每年发布新版本，持续增强语言功能

### JavaScript的应用场景
- **网页交互**：表单验证、动画效果、用户界面响应
- **单页应用(SPA)**：使用React、Vue、Angular等框架开发
- **服务器端开发**：使用Node.js构建后端服务
- **移动应用**：使用React Native、Ionic等开发跨平台应用
- **游戏开发**：使用Canvas、WebGL开发网页游戏
- **物联网**：在嵌入式设备上运行

### JavaScript与其他语言的区别
- **解释型语言**：无需编译，由浏览器或JavaScript引擎直接执行
- **弱类型语言**：变量类型可以动态改变
- **基于原型的面向对象**：不同于传统的基于类的面向对象
- **单线程执行**：但可以通过异步编程实现并发效果

## JavaScript语法基础

### 代码的编写位置
JavaScript代码可以写在以下几个位置：

1. **内联脚本**：直接写在HTML元素的事件属性中
   ```html
   <button onclick="alert('Hello World!')">点击我</button>
   ```

2. **内部脚本**：在HTML文件的`<script>`标签内
   ```html
   <script>
     alert('Hello World!');
   </script>
   ```

3. **外部脚本**：写在独立的.js文件中，通过`<script>`标签引入
   ```html
   <script src="script.js"></script>
   ```

### 基本语法规则
- **区分大小写**：`myVar`和`myvar`是不同的变量
- **语句结束符**：建议使用分号(`;`)结束语句，但不强制要求
- **注释**：
  ```javascript
  // 单行注释
  
  /*
   * 多行注释
   */
  ```
- **空白字符**：JavaScript忽略多余的空白和换行
- **标识符**：变量名、函数名等标识符必须以字母、下划线(`_`)或美元符号(`$`)开头，后续字符可以包含数字

### 输出方法
JavaScript提供多种输出数据的方式：

```javascript
// 弹窗显示
alert('Hello World!');

// 控制台输出（开发调试用）
console.log('Hello World!');
console.warn('警告信息');
console.error('错误信息');

// 写入HTML文档
document.write('Hello World!');

// 修改HTML元素内容
document.getElementById('demo').innerHTML = 'Hello World!';
```

## 数据类型与变量

### 变量声明
JavaScript中有三种变量声明方式：

```javascript
// var - 函数作用域，存在变量提升
var name = 'John';

// let - 块级作用域，ES6引入
let age = 25;

// const - 块级作用域，声明常量
const PI = 3.14159;
```

**var、let和const的区别**：
- **var**：函数作用域，可以重复声明，存在变量提升
- **let**：块级作用域，不能重复声明，不存在变量提升
- **const**：块级作用域，不能重复声明，声明后不能重新赋值，但对象的属性可以修改

### 数据类型
JavaScript有7种基本数据类型和1种引用数据类型：

#### 基本数据类型
1. **Number**：数字类型，包括整数和浮点数
   ```javascript
   let num1 = 42;
   let num2 = 3.14;
   let num3 = Infinity; // 无穷大
   let num4 = NaN;      // 不是一个数字
   ```

2. **String**：字符串类型
   ```javascript
   let str1 = 'Hello';
   let str2 = "World";
   let str3 = `Hello ${name}`; // 模板字符串，ES6引入
   ```

3. **Boolean**：布尔类型
   ```javascript
   let isActive = true;
   let isFinished = false;
   ```

4. **Undefined**：未定义类型
   ```javascript
   let x;
   console.log(x); // undefined
   ```

5. **Null**：空值类型
   ```javascript
   let emptyValue = null;
   ```

6. **Symbol**：唯一标识符类型，ES6引入
   ```javascript
   let sym1 = Symbol('description');
   let sym2 = Symbol('description');
   console.log(sym1 === sym2); // false
   ```

7. **BigInt**：大整数类型，ES2020引入
   ```javascript
   let bigNumber = 9007199254740991n;
   ```

#### 引用数据类型
1. **Object**：对象类型
   ```javascript
   let person = {
     name: 'John',
     age: 25,
     greet: function() {
       console.log('Hello!');
     }
   };
   ```

### 类型转换
JavaScript是弱类型语言，会自动进行类型转换，但了解显式类型转换也是很重要的：

#### 转换为字符串
```javascript
let num = 42;
let str1 = String(num);      // '42'
let str2 = num.toString();   // '42'
let str3 = '' + num;         // '42'
```

#### 转换为数字
```javascript
let str = '42';
let num1 = Number(str);      // 42
let num2 = parseInt(str);    // 42
let num3 = parseFloat('3.14'); // 3.14
let num4 = +str;             // 42
```

#### 转换为布尔值
```javascript
let value = 'hello';
let bool1 = Boolean(value);  // true
let bool2 = !!value;         // true
```

**转换为false的值**：`0`, `''`, `null`, `undefined`, `NaN`, `false`
**其他值都会转换为true**

## 运算符与表达式

### 算术运算符
```javascript
let a = 10, b = 3;

console.log(a + b);  // 13
console.log(a - b);  // 7
console.log(a * b);  // 30
console.log(a / b);  // 3.333...
console.log(a % b);  // 1 (取余)
console.log(a++);    // 10 (后增)
console.log(++a);    // 12 (前增)
console.log(a--);    // 12 (后减)
console.log(--a);    // 10 (前减)
```

### 赋值运算符
```javascript
let x = 10;
x += 5;  // x = x + 5
x -= 5;  // x = x - 5
x *= 5;  // x = x * 5
x /= 5;  // x = x / 5
x %= 5;  // x = x % 5
x **= 2; // x = x^2
```

### 比较运算符
```javascript
console.log(5 > 3);     // true
console.log(5 < 3);     // false
console.log(5 >= 3);    // true
console.log(5 <= 3);    // false
console.log(5 == '5');  // true (宽松相等，会进行类型转换)
console.log(5 === '5'); // false (严格相等，不进行类型转换)
console.log(5 != '5');  // false
console.log(5 !== '5'); // true
```

### 逻辑运算符
```javascript
let a = true, b = false;

console.log(a && b);  // false (逻辑与)
console.log(a || b);  // true (逻辑或)
console.log(!a);      // false (逻辑非)
```

### 三元运算符
```javascript
let age = 18;
let status = age >= 18 ? '成年人' : '未成年人';
console.log(status);  // 成年人
```

### 其他运算符
```javascript
// 类型运算符
console.log(typeof 42);       // 'number'
console.log(typeof 'hello');  // 'string'

// 解构赋值（ES6）
let [x, y] = [1, 2];
let {name, age} = {name: 'John', age: 25};

// 展开运算符（ES6）
let arr1 = [1, 2, 3];
let arr2 = [...arr1, 4, 5];
```

## 控制流程

### 条件语句

#### if语句
```javascript
if (condition) {
  // 条件为true时执行
} else if (anotherCondition) {
  // 第一个条件为false，第二个条件为true时执行
} else {
  // 所有条件都为false时执行
}
```

#### switch语句
```javascript
switch (expression) {
  case value1:
    // 当expression等于value1时执行
    break;
  case value2:
    // 当expression等于value2时执行
    break;
  default:
    // 当expression不等于任何case值时执行
}
```

### 循环语句

#### for循环
```javascript
for (let i = 0; i < 10; i++) {
  console.log(i);
}
```

#### while循环
```javascript
let i = 0;
while (i < 10) {
  console.log(i);
  i++;
}
```

#### do...while循环
```javascript
let i = 0;
do {
  console.log(i);
  i++;
} while (i < 10);
```

#### for...in循环（遍历对象属性）
```javascript
let person = {name: 'John', age: 25};
for (let key in person) {
  console.log(key + ': ' + person[key]);
}
```

#### for...of循环（遍历可迭代对象）
```javascript
let arr = [1, 2, 3];
for (let value of arr) {
  console.log(value);
}
```

### 跳转语句
```javascript
// break语句 - 跳出循环或switch
for (let i = 0; i < 10; i++) {
  if (i === 5) break;
  console.log(i);
}

// continue语句 - 跳过当前循环迭代，继续下一次
for (let i = 0; i < 10; i++) {
  if (i % 2 === 0) continue;
  console.log(i); // 只打印奇数
}

// return语句 - 从函数返回值
function sum(a, b) {
  return a + b;
}
```

## 函数

### 函数定义

#### 函数声明
```javascript
function greet(name) {
  return 'Hello, ' + name + '!';
}
```

#### 函数表达式
```javascript
const greet = function(name) {
  return 'Hello, ' + name + '!';
};
```

#### 箭头函数（ES6）
```javascript
const greet = (name) => {
  return 'Hello, ' + name + '!';
};

// 简化语法
const greet = name => 'Hello, ' + name + '!';
```

### 函数参数

#### 默认参数（ES6）
```javascript
function greet(name = 'Guest') {
  return 'Hello, ' + name + '!';
}
```

#### 剩余参数（ES6）
```javascript
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}
```

### 作用域
- **全局作用域**：在函数外部声明的变量，可在任何地方访问
- **函数作用域**：在函数内部声明的变量，只能在函数内部访问
- **块级作用域**：在块（如if、for）内部使用let或const声明的变量，只能在块内部访问

### 闭包
闭包是指函数能够访问其词法作用域之外的变量：

```javascript
function outer() {
  let count = 0;
  
  function inner() {
    count++;
    return count;
  }
  
  return inner;
}

const counter = outer();
console.log(counter()); // 1
console.log(counter()); // 2
```

## 数组

### 数组创建
```javascript
// 字面量方式
let fruits = ['Apple', 'Banana', 'Orange'];

// 构造函数方式
let numbers = new Array(1, 2, 3, 4, 5);

// 创建指定长度的数组
let emptyArray = new Array(5);
```

### 数组访问
```javascript
let fruits = ['Apple', 'Banana', 'Orange'];
console.log(fruits[0]);      // 'Apple'
console.log(fruits.length);  // 3
```

### 数组方法

#### 添加/删除元素
```javascript
let fruits = ['Apple', 'Banana'];

fruits.push('Orange');       // 在末尾添加元素: ['Apple', 'Banana', 'Orange']
let last = fruits.pop();     // 删除并返回末尾元素: 'Orange'

fruits.unshift('Mango');     // 在开头添加元素: ['Mango', 'Apple', 'Banana']
let first = fruits.shift();  // 删除并返回开头元素: 'Mango'
```

#### 数组遍历
```javascript
let fruits = ['Apple', 'Banana', 'Orange'];

// forEach方法
fruits.forEach(function(fruit, index) {
  console.log(index + ': ' + fruit);
});

// map方法 - 创建新数组
let upperFruits = fruits.map(fruit => fruit.toUpperCase());

// filter方法 - 筛选元素
let aFruits = fruits.filter(fruit => fruit.startsWith('A'));

// reduce方法 - 归约操作
let totalLength = fruits.reduce((total, fruit) => total + fruit.length, 0);
```

#### 其他常用方法
```javascript
let fruits = ['Apple', 'Banana', 'Orange'];

console.log(fruits.indexOf('Banana'));  // 1
console.log(fruits.includes('Grape'));  // false

let joined = fruits.join(', ');         // 'Apple, Banana, Orange'
let sliced = fruits.slice(1, 3);        // ['Banana', 'Orange']
let sorted = fruits.sort();             // 排序
let reversed = fruits.reverse();        // 反转
```

## 对象

### 对象创建
```javascript
// 字面量方式
let person = {
  name: 'John',
  age: 25,
  greet: function() {
    console.log('Hello, my name is ' + this.name);
  }
};

// 构造函数方式
function Person(name, age) {
  this.name = name;
  this.age = age;
  this.greet = function() {
    console.log('Hello, my name is ' + this.name);
  };
}

let john = new Person('John', 25);

// Object.create方法
let personProto = {greet: function() {}};
let person2 = Object.create(personProto);
person2.name = 'Jane';
```

### 对象属性访问
```javascript
let person = {name: 'John', age: 25};

// 点符号访问
console.log(person.name);  // 'John'

// 方括号访问（适用于动态属性名）
let prop = 'age';
console.log(person[prop]); // 25

// 添加新属性
person.job = 'Developer';

// 删除属性
delete person.age;
```

### 对象遍历
```javascript
let person = {name: 'John', age: 25, job: 'Developer'};

// for...in循环
for (let key in person) {
  if (person.hasOwnProperty(key)) {
    console.log(key + ': ' + person[key]);
  }
}

// Object.keys - 获取键数组
let keys = Object.keys(person);

// Object.values - 获取值数组
let values = Object.values(person);

// Object.entries - 获取键值对数组
let entries = Object.entries(person);
entries.forEach(([key, value]) => {
  console.log(key + ': ' + value);
});
```

### 原型与原型链
JavaScript是基于原型的语言，每个对象都有一个原型对象：

```javascript
function Person(name) {
  this.name = name;
}

Person.prototype.greet = function() {
  console.log('Hello, my name is ' + this.name);
};

let john = new Person('John');
john.greet();  // 从原型继承的方法

// 原型链查找：john -> Person.prototype -> Object.prototype -> null
```

### 类（ES6）
ES6引入了类语法，但JavaScript仍然是基于原型的：

```javascript
class Person {
  constructor(name) {
    this.name = name;
  }
  
  greet() {
    console.log('Hello, my name is ' + this.name);
  }
}

let john = new Person('John');
john.greet();
```

## DOM操作基础

### DOM概述
DOM（文档对象模型）是HTML和XML文档的编程接口，它将文档解析为树结构，允许JavaScript操作文档的内容、结构和样式。

### 选择元素
```javascript
// 通过ID选择
let element = document.getElementById('myId');

// 通过类名选择（返回元素集合）
let elements = document.getElementsByClassName('myClass');

// 通过标签名选择（返回元素集合）
let paragraphs = document.getElementsByTagName('p');

// 通过CSS选择器选择（返回第一个匹配元素）
let firstElement = document.querySelector('.myClass');

// 通过CSS选择器选择（返回所有匹配元素）
let allElements = document.querySelectorAll('div.myClass');
```

### 修改内容
```javascript
let element = document.getElementById('demo');

// 修改HTML内容
element.innerHTML = '<strong>粗体文本</strong>';

// 修改文本内容
element.textContent = '普通文本';

// 修改属性
element.setAttribute('href', 'https://www.example.com');
element.src = 'image.jpg';

// 获取属性
let href = element.getAttribute('href');
let src = element.src;
```

### 修改样式
```javascript
let element = document.getElementById('demo');

// 修改单个样式
element.style.color = 'red';
element.style.fontSize = '18px';
element.style.backgroundColor = '#f0f0f0';

// 添加类名
element.classList.add('highlight');

// 移除类名
element.classList.remove('highlight');

// 切换类名
element.classList.toggle('active');

// 检查是否包含类名
let hasClass = element.classList.contains('active');
```

### 创建和删除元素
```javascript
// 创建新元素
let newDiv = document.createElement('div');
newDiv.textContent = '新创建的元素';
newDiv.className = 'new-class';

// 添加到文档中
let parent = document.getElementById('container');
parent.appendChild(newDiv);

// 在指定位置插入
let referenceNode = document.getElementById('reference');
parent.insertBefore(newDiv, referenceNode);

// 删除元素
parent.removeChild(newDiv);

// 或直接删除
element.remove();
```

## 事件处理

### 事件类型
常见的DOM事件包括：
- **鼠标事件**：click, dblclick, mouseover, mouseout, mousedown, mouseup
- **键盘事件**：keydown, keyup, keypress
- **表单事件**：submit, change, input, focus, blur
- **窗口事件**：load, resize, scroll, unload

### 事件监听器
```javascript
let button = document.getElementById('myButton');

// 方式一：内联事件（不推荐）
// <button onclick="handleClick()">点击我</button>

// 方式二：DOM属性（不推荐）
button.onclick = function() {
  console.log('按钮被点击了！');
};

// 方式三：addEventListener（推荐）
button.addEventListener('click', function(event) {
  console.log('按钮被点击了！');
  console.log(event);  // 事件对象
});

// 带参数的事件处理函数
function handleClick(param) {
  console.log('参数：', param);
}

button.addEventListener('click', function() {
  handleClick('这是参数');
});

// 移除事件监听器
function myHandler() {}
button.addEventListener('click', myHandler);
button.removeEventListener('click', myHandler);
```

### 事件对象
事件处理函数接收一个事件对象，包含事件相关的信息：

```javascript
element.addEventListener('click', function(event) {
  // 阻止默认行为
  event.preventDefault();
  
  // 阻止事件冒泡
  event.stopPropagation();
  
  // 获取目标元素
  let target = event.target;
  
  // 获取鼠标位置
  let x = event.clientX;
  let y = event.clientY;
});
```

### 事件冒泡与捕获
- **事件冒泡**：事件从最具体的元素开始，逐级向上传播到最不具体的元素（默认行为）
- **事件捕获**：事件从最不具体的元素开始，逐级向下传播到最具体的元素

```javascript
// 事件捕获（使用第三个参数true）
element.addEventListener('click', handler, true);

// 事件冒泡（默认，第三个参数为false或省略）
element.addEventListener('click', handler, false);
```

## 异步编程基础

### 定时器
```javascript
// setTimeout - 延迟执行一次
let timerId = setTimeout(function() {
  console.log('1秒后执行');
}, 1000);

// 清除定时器
clearTimeout(timerId);

// setInterval - 周期性执行
let intervalId = setInterval(function() {
  console.log('每秒执行一次');
}, 1000);

// 清除周期性执行
clearInterval(intervalId);
```

### 回调函数
回调函数是作为参数传递给另一个函数的函数：

```javascript
function fetchData(callback) {
  // 模拟异步操作
  setTimeout(function() {
    let data = {name: 'John', age: 25};
    callback(data);
  }, 1000);
}

fetchData(function(data) {
  console.log('获取到的数据：', data);
});
```

### Promise（ES6）
Promise是用于处理异步操作的对象，代表一个异步操作的最终完成（或失败）及其结果值：

```javascript
let promise = new Promise(function(resolve, reject) {
  // 异步操作
  setTimeout(function() {
    let success = true;
    if (success) {
      resolve('操作成功');
    } else {
      reject('操作失败');
    }
  }, 1000);
});

promise.then(function(result) {
  console.log('成功：', result);
}).catch(function(error) {
  console.log('错误：', error);
}).finally(function() {
  console.log('无论成功或失败都会执行');
});
```

### async/await（ES2017）
async/await是基于Promise的语法糖，使异步代码看起来更像同步代码：

```javascript
async function fetchData() {
  try {
    let response = await fetch('https://api.example.com/data');
    let data = await response.json();
    return data;
  } catch (error) {
    console.error('错误：', error);
  }
}

fetchData().then(data => {
  console.log(data);
});
```

## 错误处理

### try...catch语句
```javascript
try {
  // 可能抛出错误的代码
  let result = riskyOperation();
  console.log(result);
} catch (error) {
  // 捕获并处理错误
  console.error('发生错误：', error.message);
} finally {
  // 无论是否发生错误都会执行的代码
  console.log('清理工作');
}
```

### 抛出错误
```javascript
function divide(a, b) {
  if (b === 0) {
    throw new Error('除数不能为零');
  }
  return a / b;
}

try {
  let result = divide(10, 0);
} catch (error) {
  console.error(error.message);  // '除数不能为零'
}
```

## JavaScript最佳实践

### 代码风格
- 使用一致的缩进（2或4个空格）
- 使用有意义的变量和函数名
- 避免使用全局变量
- 使用const和let而不是var
- 保持函数简短，每个函数只做一件事

### 性能优化
- 减少DOM操作
- 使用事件委托处理大量相似元素的事件
- 避免在循环中使用eval()和with
- 使用适当的缓存（如缓存DOM元素）
- 优化JavaScript执行（避免阻塞主线程）

### 安全性
- 防止XSS攻击（避免直接插入用户输入的HTML）
- 防止CSRF攻击
- 验证和清理用户输入
- 避免使用不安全的内置函数（如eval()）
- 使用HTTPS保护数据传输

### 调试技巧
- 使用console.log()输出变量和执行流程
- 使用Chrome DevTools的Sources面板进行断点调试
- 使用console.table()可视化对象和数组
- 使用console.time()和console.timeEnd()测量代码执行时间
- 使用try...catch捕获和分析错误

## 练习题

### 基础练习
1. 编写一个函数，计算两个数字的和、差、积、商。
2. 编写一个函数，判断一个数字是否为质数。
3. 编写一个函数，反转字符串。
4. 编写一个函数，找出数组中的最大值和最小值。
5. 创建一个简单的待办事项列表，支持添加和删除功能。

### 进阶练习
1. 实现一个简单的计算器，支持基本的算术运算。
2. 创建一个图片轮播组件，自动切换图片。
3. 编写一个函数，深拷贝一个嵌套对象。
4. 实现一个简单的AJAX请求函数，获取并显示远程数据。
5. 创建一个表单验证组件，检查用户输入是否符合要求。

## 学习资源

### 在线教程
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)：最全面的JavaScript文档
- [JavaScript 教程 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1022910821149312)：适合中文学习者
- [JavaScript.info](https://javascript.info/)：现代JavaScript教程
- [前端入门 - JavaScript](https://developer.mozilla.org/zh-CN/docs/Learn/JavaScript)：MDN的JavaScript学习指南

### 书籍推荐
- 《JavaScript高级程序设计》（第4版）- Matt Frisbie
- 《你不知道的JavaScript》（上中下卷）- Kyle Simpson
- 《JavaScript设计模式与开发实践》- 曾探
- 《深入理解ES6》- Nicholas C. Zakas

### 在线练习平台
- [LeetCode](https://leetcode.com/)：算法题练习
- [CodeWars](https://www.codewars.com/)：编程挑战
- [freeCodeCamp](https://www.freecodecamp.org/)：免费的编程教程和项目
- [JavaScript30](https://javascript30.com/)：30天JavaScript挑战

### 开发工具
- **编辑器**：Visual Studio Code（推荐使用，有丰富的JavaScript插件）
- **浏览器开发工具**：Chrome DevTools、Firefox Developer Tools
- **代码规范**：ESLint、Prettier
- **包管理器**：npm、yarn

通过本章的学习，你已经掌握了JavaScript的基础知识，为后续学习更高级的JavaScript特性和前端框架打下了坚实的基础。继续练习和实践，将理论知识应用到实际项目中，是巩固和提高JavaScript技能的最佳方式。