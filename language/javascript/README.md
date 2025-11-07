# JavaScript 学习笔记

## 概述

JavaScript是一种高级的、解释型的编程语言，最初设计用于网页交互，现在已发展成为全栈开发语言。JavaScript支持面向对象、命令式和函数式编程风格，是Web开发的核心技术之一，与HTML和CSS共同构成了现代Web应用的基础。

## 目录结构

```
javascript/
├── basics/                 # JavaScript基础
│   ├── syntax.md          # 基本语法
│   ├── variables.md       # 变量和数据类型
│   ├── operators.md       # 运算符
│   ├── control-flow.md    # 控制流
│   └── arrays.md          # 数组
├── functions/              # 函数
│   ├── function-basics.md # 函数基础
│   ├── scope.md           # 作用域
│   ├── closures.md        # 闭包
│   ├── hoisting.md        # 变量提升
│   ├── iife.md            # 立即执行函数
│   └── recursion.md       # 递归
├── objects/                # 对象
│   ├── object-basics.md   # 对象基础
│   ├── prototypes.md      # 原型链
│   ├── constructors.md    # 构造函数
│   ├── this.md            # this关键字
│   └── object-methods.md  # 对象方法
├── es6/                    # ES6+特性
│   ├── let-const.md       # let和const
│   ├── arrow-functions.md # 箭头函数
│   ├── template-strings.md # 模板字符串
│   ├── destructuring.md   # 解构赋值
│   ├── classes.md         # 类语法
│   ├── modules.md         # 模块系统
│   ├── promises.md        # Promise
│   ├── async-await.md     # async/await
│   └── iterators.md       # 迭代器
├── dom/                    # DOM操作
│   ├── dom-basics.md      # DOM基础
│   ├── selection.md       # 元素选择
│   ├── manipulation.md    # DOM操作
│   ├── events.md          # 事件处理
│   └── event-delegation.md # 事件委托
├── async/                  # 异步编程
│   ├── callbacks.md       # 回调函数
│   ├── promises.md        # Promise详解
│   ├── async-await.md     # async/await详解
│   └── event-loop.md      # 事件循环
├── patterns/               # 设计模式
│   ├── module-pattern.md  # 模块模式
│   ├── observer.md        # 观察者模式
│   ├── factory.md         # 工厂模式
│   ├── singleton.md       # 单例模式
│   └── decorator.md       # 装饰器模式
├── error-handling/         # 错误处理
│   ├── try-catch.md       # try-catch语句
│   ├── error-types.md     # 错误类型
│   ├── custom-errors.md   # 自定义错误
│   └── debugging.md       # 调试技巧
├── performance/            # 性能优化
│   ├── memory-management.md # 内存管理
│   ├── optimization.md    # 性能优化技巧
│   ├── lazy-loading.md    # 懒加载
│   └── profiling.md       # 性能分析
├── frameworks/             # 框架和库
│   ├── jquery.md          # jQuery
│   ├── react.md           # React
│   ├── vue.md             # Vue.js
│   ├── angular.md         # Angular
│   └── nodejs.md          # Node.js
├── tools/                  # 工具和资源
│   ├── bundlers.md        # 打包工具
│   ├── transpilers.md     # 转译工具
│   ├── linters.md         # 代码检查工具
│   └── testing.md         # 测试框架
└── advanced/               # 高级主题
    ├── metaprogramming.md # 元编程
    ├── web-workers.md     # Web Workers
    ├── service-workers.md # Service Workers
    ├── webassembly.md     # WebAssembly
    └── typescript.md      # TypeScript
```

## 学习路径

### 初学者路径
1. **JavaScript基础语法** - 了解变量、数据类型、运算符等基本概念
2. **控制流** - 学习条件语句和循环
3. **函数** - 掌握函数的定义、调用和作用域
4. **对象和数组** - 了解JavaScript中的数据结构
5. **DOM操作** - 学习如何操作网页元素

### 进阶路径
1. **ES6+特性** - 掌握现代JavaScript特性
2. **异步编程** - 理解回调、Promise和async/await
3. **原型和继承** - 深入理解JavaScript的原型链
4. **事件处理** - 掌握事件模型和事件委托
5. **模块化** - 学习如何组织JavaScript代码

### 高级路径
1. **设计模式** - 学习常用的JavaScript设计模式
2. **性能优化** - 掌握JavaScript性能优化技巧
3. **框架应用** - 学习React、Vue等现代框架
4. **Node.js** - 探索服务器端JavaScript开发
5. **TypeScript** - 学习JavaScript的超集

## 常见问题

### Q: var、let和const有什么区别？
A: var、let和const的主要区别：
- var有函数作用域，let和const有块级作用域
- var存在变量提升，let和const存在暂时性死区
- var可以重复声明，let和const不能
- const声明的变量必须初始化且不能重新赋值
- 全局声明的var会成为window对象的属性，let和const不会

### Q: 什么是闭包？它有什么用途？
A: 闭包是指函数能够访问其外部作用域中的变量，即使在外部函数执行完毕后：
- 闭包允许函数访问外部函数的变量
- 常用于创建私有变量和方法
- 用于函数工厂和回调函数
- 可能导致内存泄漏，需要注意使用

### Q: JavaScript中的this是如何工作的？
A: this的指向取决于函数的调用方式：
- 全局函数调用：this指向全局对象（浏览器中为window）
- 对象方法调用：this指向调用该方法的对象
- 构造函数调用：this指向新创建的对象
- call/apply/bind调用：this指向指定的对象
- 箭头函数：this继承自外层作用域

## 资源链接

- [MDN JavaScript文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)
- [JavaScript.info](https://zh.javascript.info/)
- [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS)
- [现代JavaScript教程](https://zh.javascript.info/)
- [JavaScript权威指南](https://book.douban.com/subject/10546125/)

## 代码示例

### 基本语法

```javascript
// 变量声明
var nameVar = 'Alice'; // 函数作用域
let nameLet = 'Bob';   // 块级作用域
const nameConst = 'Charlie'; // 块级作用域，不可重新赋值

// 数据类型
// 基本类型
let str = 'Hello';           // 字符串
let num = 42;                // 数字
let bool = true;             // 布尔值
let nothing = null;          // null
let notDefined;              // undefined
let unique = Symbol('id');   // Symbol

// 引用类型
let arr = [1, 2, 3];         // 数组
let obj = { name: 'Alice' }; // 对象
let func = function() {};    // 函数

// 运算符
let sum = 10 + 5;            // 加法
let isEqual = (10 === '10'); // 严格相等，false
let isLooseEqual = (10 == '10'); // 宽松相等，true

// 控制流
if (sum > 10) {
  console.log('Sum is greater than 10');
} else if (sum === 10) {
  console.log('Sum equals 10');
} else {
  console.log('Sum is less than 10');
}

// 循环
for (let i = 0; i < 5; i++) {
  console.log(i);
}

// while循环
let count = 0;
while (count < 3) {
  console.log(count);
  count++;
}

// for...of循环（遍历数组）
for (const value of arr) {
  console.log(value);
}

// for...in循环（遍历对象属性）
for (const key in obj) {
  console.log(key + ': ' + obj[key]);
}
```

### 函数

```javascript
// 函数声明
function greet(name) {
  return 'Hello, ' + name + '!';
}

// 函数表达式
const greetExpression = function(name) {
  return 'Hello, ' + name + '!';
};

// 箭头函数
const greetArrow = (name) => {
  return 'Hello, ' + name + '!';
};

// 简化的箭头函数
const greetShort = name => 'Hello, ' + name + '!';

// 带默认参数的函数
function greetWithDefault(name = 'Guest') {
  return 'Hello, ' + name + '!';
}

// 剩余参数
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}

// 函数调用
console.log(greet('Alice')); // Hello, Alice!
console.log(greetExpression('Bob')); // Hello, Bob!
console.log(greetArrow('Charlie')); // Hello, Charlie!
console.log(greetShort('David')); // Hello, David!
console.log(greetWithDefault()); // Hello, Guest!
console.log(sum(1, 2, 3, 4, 5)); // 15

// 作用域
let globalVar = 'I am global';

function outerFunction() {
  let outerVar = 'I am from outer function';
  
  function innerFunction() {
    let innerVar = 'I am from inner function';
    console.log(globalVar); // 可以访问全局变量
    console.log(outerVar);  // 可以访问外层函数变量
    console.log(innerVar);  // 可以访问自己的变量
  }
  
  innerFunction();
  // console.log(innerVar); // 错误，无法访问内层函数变量
}

outerFunction();
// console.log(outerVar); // 错误，无法访问函数内部变量
```

### 对象和原型

```javascript
// 对象字面量
const person = {
  name: 'Alice',
  age: 30,
  greet: function() {
    return 'Hello, my name is ' + this.name;
  },
  // ES6简写方法
  introduce() {
    return `I am ${this.name} and I'm ${this.age} years old`;
  }
};

// 访问属性
console.log(person.name); // 点表示法
console.log(person['age']); // 括号表示法

// 调用方法
console.log(person.greet());
console.log(person.introduce());

// 添加属性
person.email = 'alice@example.com';

// 删除属性
delete person.age;

// 构造函数
function Person(name, age) {
  this.name = name;
  this.age = age;
}

Person.prototype.greet = function() {
  return 'Hello, my name is ' + this.name;
};

const person1 = new Person('Bob', 25);
const person2 = new Person('Charlie', 35);

console.log(person1.greet()); // Hello, my name is Bob
console.log(person2.greet()); // Hello, my name is Charlie

// 原型链
console.log(person1.__proto__ === Person.prototype); // true
console.log(Person.prototype.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__ === null); // true

// ES6类
class Animal {
  constructor(name) {
    this.name = name;
  }
  
  speak() {
    return this.name + ' makes a sound.';
  }
  
  // 静态方法
  static category() {
    return 'Living Being';
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name); // 调用父类构造函数
    this.breed = breed;
  }
  
  speak() {
    return this.name + ' barks.';
  }
  
  // getter
  get description() {
    return `${this.name} is a ${this.breed}`;
  }
}

const myDog = new Dog('Rex', 'German Shepherd');
console.log(myDog.speak()); // Rex barks.
console.log(myDog.description); // Rex is a German Shepherd
console.log(Animal.category()); // Living Being
```

### 数组操作

```javascript
// 创建数组
const fruits = ['Apple', 'Banana', 'Orange'];
const numbers = new Array(1, 2, 3, 4, 5);
const mixed = ['Hello', 42, true, null, undefined];

// 访问元素
console.log(fruits[0]); // Apple
console.log(fruits.length); // 3

// 修改元素
fruits[1] = 'Pear';
console.log(fruits); // ['Apple', 'Pear', 'Orange']

// 数组方法
// 添加元素
fruits.push('Grape'); // 添加到末尾
fruits.unshift('Strawberry'); // 添加到开头

// 删除元素
const lastFruit = fruits.pop(); // 删除并返回最后一个元素
const firstFruit = fruits.shift(); // 删除并返回第一个元素

// 查找元素
const index = fruits.indexOf('Banana'); // 返回索引，找不到返回-1
const includesBanana = fruits.includes('Banana'); // 返回布尔值

// 切片和拼接
const slice = fruits.slice(1, 3); // 返回索引1到3的元素（不包括3）
const moreFruits = ['Mango', 'Pineapple'];
const allFruits = fruits.concat(moreFruits); // 连接数组

// 转换为字符串
const fruitsString = fruits.join(', '); // 用逗号和空格连接

// 遍历数组
fruits.forEach(function(fruit, index) {
  console.log(index + ': ' + fruit);
});

// 数组迭代方法
// map - 创建新数组
const upperFruits = fruits.map(fruit => fruit.toUpperCase());

// filter - 过滤元素
const longFruits = fruits.filter(fruit => fruit.length > 5);

// reduce - 累计计算
const sum = numbers.reduce((total, num) => total + num, 0);

// some - 检查是否有元素满足条件
const hasLongFruit = fruits.some(fruit => fruit.length > 5);

// every - 检查是否所有元素都满足条件
const allLongFruits = fruits.every(fruit => fruit.length > 5);

// find - 查找第一个满足条件的元素
const foundFruit = fruits.find(fruit => fruit.startsWith('A'));

// ES6数组方法
// Array.from - 从类数组对象创建数组
const arrayLike = { 0: 'a', 1: 'b', 2: 'c', length: 3 };
const chars = Array.from(arrayLike); // ['a', 'b', 'c']

// Array.of - 创建数组
const arr = Array.of(1, 2, 3); // [1, 2, 3]

// findIndex - 查找满足条件的第一个元素的索引
const index2 = fruits.findIndex(fruit => fruit.startsWith('B'));

// includes - 检查数组是否包含某个元素
const hasApple = fruits.includes('Apple');
```

### DOM操作

```javascript
// 选择元素
const elementById = document.getElementById('myId');
const elementsByClass = document.getElementsByClassName('myClass');
const elementsByTag = document.getElementsByTagName('div');
const elementBySelector = document.querySelector('.myClass');
const elementsBySelectorAll = document.querySelectorAll('.myClass');

// 修改元素内容
elementById.textContent = 'New text content'; // 纯文本
elementById.innerHTML = '<strong>New HTML content</strong>'; // HTML内容

// 修改元素属性
elementById.setAttribute('class', 'new-class');
elementById.id = 'new-id';
elementById.disabled = true;

// 修改元素样式
elementById.style.color = 'red';
elementById.style.backgroundColor = '#f0f0f0';
elementById.style.fontSize = '16px';

// 添加和移除类
elementById.classList.add('active');
elementById.classList.remove('inactive');
elementById.classList.toggle('highlight');
const hasClass = elementById.classList.contains('active');

// 创建和插入元素
const newDiv = document.createElement('div');
newDiv.textContent = 'New element';
newDiv.className = 'new-element';

// 添加到DOM
document.body.appendChild(newDiv);

// 插入到指定位置
const parentElement = document.getElementById('parent');
const referenceElement = document.getElementById('reference');
parentElement.insertBefore(newDiv, referenceElement);

// 替换元素
const oldElement = document.getElementById('old');
parentElement.replaceChild(newDiv, oldElement);

// 删除元素
const elementToRemove = document.getElementById('remove');
elementToRemove.parentNode.removeChild(elementToRemove);

// 事件处理
// 添加事件监听器
elementById.addEventListener('click', function(event) {
  console.log('Element clicked!');
  console.log('Event object:', event);
});

// 带参数的事件处理函数
function handleClick(message) {
  return function(event) {
    console.log(message);
    console.log('Event target:', event.target);
  };
}

elementById.addEventListener('click', handleClick('Button clicked!'));

// 移除事件监听器
function handleMouseOver(event) {
  console.log('Mouse over element');
}

elementById.addEventListener('mouseover', handleMouseOver);
// elementById.removeEventListener('mouseover', handleMouseOver);

// 事件委托
document.getElementById('parent-list').addEventListener('click', function(event) {
  if (event.target && event.target.matches('li.item')) {
    console.log('List item clicked:', event.target.textContent);
  }
});

// 事件对象属性
elementById.addEventListener('click', function(event) {
  console.log('Event type:', event.type);
  console.log('Target element:', event.target);
  console.log('Current target:', event.currentTarget);
  console.log('Mouse position:', event.clientX, event.clientY);
  
  // 阻止默认行为
  event.preventDefault();
  
  // 停止事件冒泡
  event.stopPropagation();
});
```

### 异步编程

```javascript
// 回调函数
function fetchData(callback) {
  setTimeout(() => {
    const data = { id: 1, name: 'Sample Data' };
    callback(data);
  }, 1000);
}

function processData(data) {
  console.log('Processing data:', data);
}

fetchData(processData);

// 回调地狱
fetchData(function(data) {
  processData(data);
  fetchMoreData(function(moreData) {
    processMoreData(moreData);
    fetchEvenMoreData(function(evenMoreData) {
      processEvenMoreData(evenMoreData);
      // 更多嵌套...
    });
  });
});

// Promise
function fetchDataWithPromise() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.5;
      if (success) {
        resolve({ id: 1, name: 'Sample Data' });
      } else {
        reject('Failed to fetch data');
      }
    }, 1000);
  });
}

// 使用Promise
fetchDataWithPromise()
  .then(data => {
    console.log('Data fetched:', data);
    return fetchMoreDataWithPromise();
  })
  .then(moreData => {
    console.log('More data fetched:', moreData);
  })
  .catch(error => {
    console.error('Error:', error);
  })
  .finally(() => {
    console.log('Operation completed');
  });

// Promise.all
const promise1 = Promise.resolve(3);
const promise2 = new Promise(resolve => setTimeout(() => resolve('foo'), 1000));
const promise3 = Promise.resolve(42);

Promise.all([promise1, promise2, promise3])
  .then(values => {
    console.log('All promises resolved:', values); // [3, "foo", 42]
  })
  .catch(error => {
    console.error('At least one promise rejected:', error);
  });

// Promise.race
Promise.race([promise1, promise2, promise3])
  .then(value => {
    console.log('First promise resolved:', value);
  });

// async/await
async function fetchAndProcessData() {
  try {
    const data = await fetchDataWithPromise();
    console.log('Data fetched:', data);
    
    const moreData = await fetchMoreDataWithPromise();
    console.log('More data fetched:', moreData);
    
    return { data, moreData };
  } catch (error) {
    console.error('Error:', error);
    throw error; // 重新抛出错误
  } finally {
    console.log('Operation completed');
  }
}

// 调用async函数
fetchAndProcessData()
  .then(result => {
    console.log('Final result:', result);
  })
  .catch(error => {
    console.error('Final error:', error);
  });

// 并行处理
async function fetchMultipleResources() {
  const [users, posts, comments] = await Promise.all([
    fetch('https://api.example.com/users').then(res => res.json()),
    fetch('https://api.example.com/posts').then(res => res.json()),
    fetch('https://api.example.com/comments').then(res => res.json())
  ]);
  
  return { users, posts, comments };
}

// 事件循环示例
console.log('Start');

setTimeout(() => {
  console.log('Timeout callback');
}, 0);

Promise.resolve().then(() => {
  console.log('Promise callback');
});

console.log('End');

// 输出顺序：
// Start
// End
// Promise callback
// Timeout callback
```

### ES6+特性

```javascript
// 解构赋值
// 数组解构
const [a, b, ...rest] = [1, 2, 3, 4, 5];
console.log(a); // 1
console.log(b); // 2
console.log(rest); // [3, 4, 5]

// 对象解构
const person = {
  firstName: 'John',
  lastName: 'Doe',
  age: 30
};

const { firstName, lastName, age = 25 } = person;
console.log(firstName); // John
console.log(lastName); // Doe
console.log(age); // 30

// 重命名
const { firstName: name, age: years } = person;
console.log(name); // John
console.log(years); // 30

// 模板字符串
const name = 'Alice';
const age = 30;

const message = `My name is ${name} and I'm ${age} years old.`;
console.log(message);

// 多行字符串
const html = `
  <div class="person">
    <h2>${name}</h2>
    <p>Age: ${age}</p>
  </div>
`;

// 展开运算符
// 数组展开
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2]; // [1, 2, 3, 4, 5, 6]

// 对象展开
const person1 = {
  name: 'Alice',
  age: 30
};

const employee = {
  ...person1,
  position: 'Developer',
  salary: 80000
};

// 函数参数展开
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}

console.log(sum(1, 2, 3, 4, 5)); // 15

// 箭头函数
const add = (a, b) => a + b;
const greet = name => `Hello, ${name}!`;

const person = {
  name: 'Alice',
  hobbies: ['reading', 'coding'],
  
  // 传统函数
  printHobbies: function() {
    this.hobbies.forEach(function(hobby) {
      console.log(`${this.name} likes ${hobby}`); // this为undefined
    });
  },
  
  // 箭头函数
  printHobbiesArrow: function() {
    this.hobbies.forEach(hobby => {
      console.log(`${this.name} likes ${hobby}`); // this为person对象
    });
  }
};

// 默认参数
function greet(name = 'Guest', greeting = 'Hello') {
  return `${greeting}, ${name}!`;
}

console.log(greet()); // Hello, Guest!
console.log(greet('Alice')); // Hello, Alice!
console.log(greet('Bob', 'Hi')); // Hi, Bob!

// 对象属性简写
const name = 'Alice';
const age = 30;

const person = {
  name, // 等同于 name: name
  age, // 等同于 age: age
  greet() { // 等同于 greet: function() {}
    return `Hello, I'm ${this.name}`;
  }
};

// 计算属性名
const propName = 'age';
const person = {
  name: 'Alice',
  [propName]: 30, // 计算属性名
  ['full ' + 'name']: 'Alice Smith'
};

// 模块
// math.js
export const PI = 3.14159;

export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

// 默认导出
export default class Calculator {
  multiply(a, b) {
    return a * b;
  }
}

// main.js
import Calculator, { add, subtract, PI } from './math.js';

const calc = new Calculator();
console.log(calc.multiply(5, 3)); // 15
console.log(add(2, 3)); // 5
console.log(PI); // 3.14159
```

### 错误处理

```javascript
// try-catch语句
try {
  // 可能抛出错误的代码
  const result = riskyOperation();
  console.log('Result:', result);
} catch (error) {
  // 处理错误
  console.error('Error occurred:', error.message);
} finally {
  // 无论是否出错都会执行的代码
  console.log('Operation completed');
}

// 抛出错误
function divide(a, b) {
  if (b === 0) {
    throw new Error('Division by zero is not allowed');
  }
  return a / b;
}

try {
  const result = divide(10, 0);
  console.log(result);
} catch (error) {
  console.error(error.message); // Division by zero is not allowed
}

// 不同类型的错误
try {
  // 尝试访问未定义的属性
  const obj = null;
  console.log(obj.property); // TypeError
} catch (error) {
  if (error instanceof TypeError) {
    console.error('Type error:', error.message);
  } else {
    console.error('Other error:', error.message);
  }
}

// 自定义错误
class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
  }
}

function validateAge(age) {
  if (typeof age !== 'number') {
    throw new ValidationError('Age must be a number');
  }
  
  if (age < 0 || age > 150) {
    throw new ValidationError('Age must be between 0 and 150');
  }
  
  return true;
}

try {
  validateAge(-5);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Validation failed:', error.message);
  } else {
    console.error('Unexpected error:', error.message);
  }
}

// Promise错误处理
function fetchData() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.5;
      if (success) {
        resolve('Data fetched successfully');
      } else {
        reject(new Error('Failed to fetch data'));
      }
    }, 1000);
  });
}

fetchData()
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error('Promise error:', error.message);
  });

// async/await错误处理
async function fetchDataAsync() {
  try {
    const data = await fetchData();
    console.log(data);
  } catch (error) {
    console.error('Async error:', error.message);
  }
}

fetchDataAsync();

// 全局错误处理
window.addEventListener('error', function(event) {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
  console.error('Unhandled promise rejection:', event.reason);
});
```

## 最佳实践

1. **代码风格**
   - 使用一致的命名约定（驼峰命名法）
   - 使用有意义的变量和函数名
   - 添加适当的注释和文档
   - 使用ESLint等工具保持代码风格一致

2. **变量和函数**
   - 优先使用const，其次let，避免var
   - 在函数顶部声明所有变量
   - 保持函数简短，单一职责
   - 使用默认参数而不是参数检查

3. **异步编程**
   - 优先使用async/await而不是Promise链
   - 始终处理Promise的拒绝情况
   - 避免回调地狱，使用Promise或async/await
   - 使用Promise.all并行处理独立操作

4. **错误处理**
   - 使用try-catch处理可能出错的代码
   - 提供有意义的错误信息
   - 区分不同类型的错误
   - 记录错误以便调试

5. **性能优化**
   - 避免不必要的DOM操作
   - 使用事件委托减少事件监听器数量
   - 防抖和节流处理频繁触发的事件
   - 使用懒加载和代码分割减少初始加载时间

## 贡献指南

欢迎对本学习笔记进行贡献！请遵循以下指南：

1. 确保内容准确、清晰、实用
2. 使用规范的Markdown格式
3. 代码示例需要完整且可运行
4. 添加适当的注释和说明
5. 保持目录结构的一致性

## 注意事项

- JavaScript在不同环境中的行为可能不同（浏览器 vs Node.js）
- 注意浏览器的兼容性问题，特别是ES6+特性
- JavaScript是动态类型语言，注意类型相关的错误
- 避免使用全局变量，防止命名空间污染
- 持续关注JavaScript新版本的特性和改进

---

*最后更新: 2023年*