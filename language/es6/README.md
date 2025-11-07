# ES6 (ECMAScript 2015) 学习笔记

## 概述

ES6（ECMAScript 2015）是JavaScript语言的重大更新版本，引入了许多新特性和语法糖，极大地提升了JavaScript的开发体验和代码质量。这些新特性包括箭头函数、类、模块系统、Promise等。

## 目录结构

```
es6/
├── basics/                 # ES6基础
│   ├── let-const.md       # let和const变量声明
│   ├── arrow-functions.md # 箭头函数
│   ├── template-strings.md # 模板字符串
│   └── default-parameters.md # 默认参数
├── data-structures/         # 数据结构
│   ├── destructuring.md    # 解构赋值
│   ├── spread-operator.md # 展开运算符
│   └── enhanced-objects.md # 对象增强
├── functions/               # 函数特性
│   ├── rest-parameters.md  # 剩余参数
│   ├── enhanced-functions.md # 函数增强
│   └── generators.md       # 生成器函数
├── classes/                 # 类和继承
│   ├── class-syntax.md     # 类语法
│   ├── inheritance.md      # 继承
│   ├── getters-setters.md # getter和setter
│   └── static-methods.md   # 静态方法
├── modules/                 # 模块系统
│   ├── import-export.md    # 导入导出
│   ├── module-system.md    # 模块系统概述
│   └── dynamic-import.md   # 动态导入
├── promises/                # Promise和异步
│   ├── promise-basics.md   # Promise基础
│   ├── promise-methods.md  # Promise方法
│   ├── async-await.md      # async/await
│   └── error-handling.md   # 错误处理
├── built-ins/               # 内置对象扩展
│   ├── string-methods.md   # 字符串方法
│   ├── array-methods.md    # 数组方法
│   ├── object-methods.md   # 对象方法
│   ├── number-methods.md   # 数字方法
│   └── map-set.md         # Map和Set
├── iterators/               # 迭代器和遍历
│   ├── iterator-protocol.md # 迭代器协议
│   ├── for-of.md           # for...of循环
│   └── symbols.md          # Symbol类型
├── metaprogramming/         # 元编程
│   ├── proxies.md          # 代理
│   └── reflect.md          # 反射
├── new-types/               # 新类型
│   ├── symbols.md          # Symbol类型
│   └── typedarrays.md      # 类型化数组
└── tools/                   # 工具和资源
    ├── transpilation.md    # 转译工具(Babel)
    ├── polyfills.md        # 垫片库
    └── compatibility.md    # 兼容性
```

## 学习路径

### 初学者路径
1. **变量声明** - 学习let和const代替var
2. **箭头函数** - 掌握简洁的函数语法
3. **模板字符串** - 使用反引号创建字符串
4. **解构赋值** - 从数组或对象中提取值
5. **默认参数** - 为函数参数设置默认值

### 进阶路径
1. **类和继承** - 使用class语法创建对象
2. **Promise** - 处理异步操作
3. **模块系统** - 使用import/export组织代码
4. **迭代器和for...of** - 遍历数据结构
5. **Map和Set** - 使用新的集合类型

### 高级路径
1. **生成器函数** - 控制函数执行流程
2. **代理和反射** - 元编程能力
3. **async/await** - 更优雅的异步编程
4. **Symbol** - 创建唯一标识符
5. **类型化数组** - 处理二进制数据

## 常见问题

### Q: let、const和var有什么区别？
A: let、const和var的主要区别：
- var有函数作用域，let和const有块级作用域
- var存在变量提升，let和const存在暂时性死区
- const声明的变量必须初始化且不能重新赋值
- let和const不能在同一作用域内重复声明

### Q: 箭头函数与普通函数有什么区别？
A: 箭头函数与普通函数的区别：
- 箭头函数没有自己的this，会捕获外层this
- 箭头函数没有arguments对象
- 箭头函数不能作为构造函数使用new
- 箭头函数没有prototype属性

### Q: Promise和async/await有什么关系？
A: Promise和async/await的关系：
- async/await是Promise的语法糖
- async函数返回Promise
- await只能在async函数内使用
- async/await使异步代码看起来像同步代码

## 资源链接

- [MDN JavaScript文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)
- [ES6入门教程](http://es6.ruanyifeng.com/)
- [Babel文档](https://babeljs.io/docs/en/)
- [ECMAScript规范](https://www.ecma-international.org/publications-and-standards/standards/ecma-262/)
- [现代JavaScript教程](https://zh.javascript.info/)

## 代码示例

### let和const

```javascript
// 使用let声明变量
let name = 'Alice';
name = 'Bob'; // 可以重新赋值

// 使用const声明常量
const PI = 3.14159;
// PI = 3.14; // 错误，不能重新赋值

// 块级作用域
if (true) {
  let blockScoped = 'I am block scoped';
  const alsoBlockScoped = 'Me too';
}

// console.log(blockScoped); // 错误，变量不存在
```

### 箭头函数

```javascript
// 传统函数
function add(a, b) {
  return a + b;
}

// 箭头函数
const addArrow = (a, b) => a + b;

// 带多行体的箭头函数
const calculate = (a, b, operation) => {
  let result;
  switch (operation) {
    case 'add':
      result = a + b;
      break;
    case 'subtract':
      result = a - b;
      break;
    default:
      result = 0;
  }
  return result;
};

// 箭头函数中的this
const person = {
  name: 'Alice',
  greet: function() {
    // 传统函数中的this指向person
    setTimeout(function() {
      console.log(`Hello, my name is ${this.name}`); // this为undefined
    }, 100);
    
    // 箭头函数中的this继承自外层作用域
    setTimeout(() => {
      console.log(`Hello, my name is ${this.name}`); // this为person
    }, 200);
  }
};
```

### 模板字符串

```javascript
const name = 'Alice';
const age = 30;

// 传统字符串拼接
const message1 = 'My name is ' + name + ' and I am ' + age + ' years old.';

// 模板字符串
const message2 = `My name is ${name} and I am ${age} years old.`;

// 多行字符串
const html = `
  <div class="person">
    <h2>${name}</h2>
    <p>Age: ${age}</p>
  </div>
`;

// 表达式计算
const price = 19.99;
const quantity = 3;
const total = `Total: $${(price * quantity).toFixed(2)}`;
```

### 解构赋值

```javascript
// 数组解构
const numbers = [1, 2, 3, 4, 5];
const [first, second, ...rest] = numbers;
console.log(first); // 1
console.log(second); // 2
console.log(rest); // [3, 4, 5]

// 对象解构
const person = {
  name: 'Alice',
  age: 30,
  city: 'New York'
};

const { name, age } = person;
console.log(name); // Alice
console.log(age); // 30

// 重命名和默认值
const { name: personName, country = 'Unknown' } = person;
console.log(personName); // Alice
console.log(country); // Unknown

// 函数参数解构
function greet({ name, age = 25 }) {
  console.log(`Hello ${name}, you are ${age} years old!`);
}

greet({ name: 'Bob' }); // Hello Bob, you are 25 years old!
```

### 展开运算符

```javascript
// 数组展开
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2]; // [1, 2, 3, 4, 5, 6]

// 对象展开
const person = {
  name: 'Alice',
  age: 30
};

const employee = {
  ...person,
  position: 'Developer',
  salary: 80000
};

// 函数调用中的展开
function sum(a, b, c) {
  return a + b + c;
}

const numbers = [1, 2, 3];
const result = sum(...numbers); // 6
```

### 类和继承

```javascript
// 基本类定义
class Animal {
  constructor(name) {
    this.name = name;
  }
  
  speak() {
    console.log(`${this.name} makes a sound.`);
  }
  
  // 静态方法
  static getCategory() {
    return 'Living Being';
  }
}

// 继承
class Dog extends Animal {
  constructor(name, breed) {
    super(name); // 调用父类构造函数
    this.breed = breed;
  }
  
  speak() {
    console.log(`${this.name} barks.`);
  }
  
  // getter
  get description() {
    return `${this.name} is a ${this.breed}`;
  }
  
  // setter
  set nickname(nick) {
    this.name = nick;
  }
}

const myDog = new Dog('Rex', 'German Shepherd');
myDog.speak(); // Rex barks.
console.log(myDog.description); // Rex is a German Shepherd
myDog.nickname = 'Buddy';
console.log(myDog.name); // Buddy
console.log(Animal.getCategory()); // Living Being
```

### Promise

```javascript
// 创建Promise
function fetchData() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.5;
      if (success) {
        resolve('Data fetched successfully!');
      } else {
        reject('Error: Failed to fetch data');
      }
    }, 1000);
  });
}

// 使用Promise
fetchData()
  .then(data => console.log(data))
  .catch(error => console.error(error))
  .finally(() => console.log('Operation completed'));

// Promise链
function processStep1() {
  return new Promise(resolve => {
    setTimeout(() => {
      console.log('Step 1 completed');
      resolve('Result from step 1');
    }, 500);
  });
}

function processStep2(data) {
  return new Promise(resolve => {
    setTimeout(() => {
      console.log(`Step 2 completed with data: ${data}`);
      resolve('Result from step 2');
    }, 500);
  });
}

processStep1()
  .then(processStep2)
  .then(result => console.log(`Final result: ${result}`));

// Promise.all
const promise1 = Promise.resolve(3);
const promise2 = new Promise(resolve => setTimeout(() => resolve('foo'), 1000));
const promise3 = Promise.resolve(42);

Promise.all([promise1, promise2, promise3]).then(values => {
  console.log(values); // [3, "foo", 42]
});
```

### async/await

```javascript
// 基本async/await用法
async function fetchUserData() {
  try {
    const response = await fetch('https://api.example.com/user');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
}

// 使用async函数
fetchUserData()
  .then(user => console.log('User:', user))
  .catch(error => console.error('Failed:', error));

// 并行处理
async function fetchMultipleResources() {
  const [users, posts, comments] = await Promise.all([
    fetch('https://api.example.com/users').then(res => res.json()),
    fetch('https://api.example.com/posts').then(res => res.json()),
    fetch('https://api.example.com/comments').then(res => res.json())
  ]);
  
  return { users, posts, comments };
}

// 顺序处理
async function processItems(items) {
  const results = [];
  
  for (const item of items) {
    const result = await processItem(item);
    results.push(result);
  }
  
  return results;
}
```

### 模块系统

```javascript
// math.js - 导出模块
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
  
  divide(a, b) {
    return a / b;
  }
}

// main.js - 导入模块
import Calculator, { add, subtract, PI } from './math.js';

const calc = new Calculator();
console.log(calc.multiply(5, 3)); // 15
console.log(add(2, 3)); // 5
console.log(subtract(5, 2)); // 3
console.log(PI); // 3.14159

// 导入所有
import * as math from './math.js';
console.log(math.add(1, 2)); // 3
const anotherCalc = new math.default();
```

### 数组新方法

```javascript
const numbers = [1, 2, 3, 4, 5];

// Array.from - 从类数组对象创建数组
const arrayLike = { 0: 'a', 1: 'b', 2: 'c', length: 3 };
const chars = Array.from(arrayLike); // ['a', 'b', 'c']

// Array.of - 创建数组
const arr = Array.of(1, 2, 3); // [1, 2, 3]

// find - 查找满足条件的第一个元素
const found = numbers.find(num => num > 3); // 4

// findIndex - 查找满足条件的第一个元素的索引
const index = numbers.findIndex(num => num > 3); // 3

// includes - 检查数组是否包含某个元素
const hasThree = numbers.includes(3); // true

// entries - 返回键值对迭代器
const iterator = numbers.entries();
for (const [index, value] of iterator) {
  console.log(`${index}: ${value}`);
}

// keys - 返回键迭代器
for (const key of numbers.keys()) {
  console.log(key);
}

// values - 返回值迭代器
for (const value of numbers.values()) {
  console.log(value);
}
```

### Map和Set

```javascript
// Map - 键值对集合
const myMap = new Map();

// 设置键值对
myMap.set('name', 'Alice');
myMap.set(1, 'number key');
myMap.set({}, 'object key');

// 获取值
console.log(myMap.get('name')); // Alice

// 检查键是否存在
console.log(myMap.has('name')); // true

// 删除键值对
myMap.delete('name');

// 获取大小
console.log(myMap.size);

// 遍历Map
myMap.forEach((value, key) => {
  console.log(`${key} = ${value}`);
});

// Set - 唯一值集合
const mySet = new Set([1, 2, 3, 3, 4]); // 重复的3会被忽略

// 添加值
mySet.add(5);
mySet.add(1); // 重复的1会被忽略

// 检查值是否存在
console.log(mySet.has(3)); // true

// 删除值
mySet.delete(2);

// 获取大小
console.log(mySet.size);

// 转换为数组
const setToArray = [...mySet]; // [1, 3, 4, 5]

// 数组去重
const duplicates = [1, 2, 2, 3, 4, 4, 5];
const unique = [...new Set(duplicates)]; // [1, 2, 3, 4, 5]
```

## 最佳实践

1. **变量声明**
   - 优先使用const，只有需要重新赋值时使用let
   - 避免使用var
   - 在块级作用域内声明变量

2. **函数使用**
   - 对于简短的单行函数，使用箭头函数
   - 需要this绑定或arguments时，使用传统函数
   - 使用默认参数代替参数检查

3. **异步编程**
   - 优先使用async/await而不是Promise链
   - 始终处理Promise的拒绝情况
   - 使用Promise.all并行处理独立操作

4. **模块化**
   - 使用ES6模块系统组织代码
   - 明确区分命名导出和默认导出
   - 避免循环依赖

5. **代码风格**
   - 使用解构赋值简化代码
   - 使用模板字符串代替字符串拼接
   - 使用展开运算符处理数组和对象

## 贡献指南

欢迎对本学习笔记进行贡献！请遵循以下指南：

1. 确保内容准确、清晰、实用
2. 使用规范的Markdown格式
3. 代码示例需要完整且可运行
4. 添加适当的注释和说明
5. 保持目录结构的一致性

## 注意事项

- ES6特性在不同环境中的支持程度不同
- 在生产环境中使用Babel等工具转译代码
- 注意浏览器兼容性问题
- 新特性不总是最佳选择，根据实际需求决定是否使用
- 持续关注ECMAScript新版本的发布

---

*最后更新: 2023年*