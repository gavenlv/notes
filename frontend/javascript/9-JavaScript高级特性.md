# 第9章：JavaScript高级特性

## 9.1 生成器与迭代器

### 9.1.1 迭代器（Iterator）

迭代器是一种对象，它提供了一个`next()`方法，用于遍历数据结构中的元素。每次调用`next()`方法时，它会返回一个包含`value`和`done`属性的对象：

- `value`: 当前元素的值
- `done`: 布尔值，表示是否遍历结束

```javascript
// 创建一个简单的迭代器
function createArrayIterator(arr) {
  let index = 0;
  
  return {
    next() {
      if (index < arr.length) {
        return { value: arr[index++], done: false };
      } else {
        return { value: undefined, done: true };
      }
    }
  };
}

const fruits = ['苹果', '香蕉', '橙子'];
const iterator = createArrayIterator(fruits);

console.log(iterator.next()); // { value: '苹果', done: false }
console.log(iterator.next()); // { value: '香蕉', done: false }
console.log(iterator.next()); // { value: '橙子', done: false }
console.log(iterator.next()); // { value: undefined, done: true }

// 使用for...of循环遍历（需要实现可迭代协议）
const iterable = {
  [Symbol.iterator]() {
    return createArrayIterator(fruits);
  }
};

for (const fruit of iterable) {
  console.log(fruit); // '苹果', '香蕉', '橙子'
}
```

### 9.1.2 生成器（Generator）

生成器是一种特殊的函数，可以暂停执行并在稍后恢复执行。它使用`function*`语法定义，并使用`yield`关键字暂停和返回值。

```javascript
// 基本生成器函数
function* countGenerator() {
  console.log('生成器开始执行');
  yield 1;
  console.log('第一次yield后继续执行');
  yield 2;
  console.log('第二次yield后继续执行');
  yield 3;
  console.log('生成器执行结束');
}

const counter = countGenerator();
console.log(counter.next()); // { value: 1, done: false }
console.log(counter.next()); // { value: 2, done: false }
console.log(counter.next()); // { value: 3, done: false }
console.log(counter.next()); // { value: undefined, done: true }

// 生成器用于创建无限序列
function* fibonacciGenerator() {
  let a = 0;
  let b = 1;
  
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

const fib = fibonacciGenerator();
console.log(fib.next().value); // 0
console.log(fib.next().value); // 1
console.log(fib.next().value); // 1
console.log(fib.next().value); // 2
console.log(fib.next().value); // 3

// 生成器与for...of结合使用
function* rangeGenerator(start, end, step = 1) {
  for (let i = start; i <= end; i += step) {
    yield i;
  }
}

for (const num of rangeGenerator(1, 10, 2)) {
  console.log(num); // 1, 3, 5, 7, 9
}
```

### 9.1.3 生成器的高级应用

#### 1. 异步任务的顺序执行

```javascript
// 模拟异步操作
function fetchData(url) {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(`来自 ${url} 的数据`);
    }, 1000);
  });
}

// 使用生成器顺序执行异步任务
function* fetchSequentially() {
  const data1 = yield fetchData('api.example.com/users');
  console.log(data1);
  
  const data2 = yield fetchData('api.example.com/posts');
  console.log(data2);
  
  const data3 = yield fetchData('api.example.com/comments');
  console.log(data3);
  
  return "所有数据获取完成";
}

// 生成器执行器
function runGenerator(generator) {
  const iterator = generator();
  
  function handle(result) {
    if (result.done) {
      return Promise.resolve(result.value);
    }
    
    return Promise.resolve(result.value)
      .then(data => handle(iterator.next(data)))
      .catch(error => handle(iterator.throw(error)));
  }
  
  return handle(iterator.next());
}

// 运行生成器
runGenerator(fetchSequentially)
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

#### 2. 实现协程（Coroutine）

```javascript
// 任务调度器
class Scheduler {
  constructor() {
    this.tasks = [];
  }
  
  add(generator) {
    this.tasks.push(generator);
    this.run();
  }
  
  run() {
    if (this.tasks.length === 0) return;
    
    const task = this.tasks.shift();
    const { value, done } = task.next();
    
    if (!done) {
      this.tasks.push(task);
    }
    
    if (value) {
      setTimeout(() => this.run(), value);
    } else {
      this.run();
    }
  }
}

// 使用调度器创建任务
const scheduler = new Scheduler();

// 任务1：打印数字
function* printNumbers() {
  for (let i = 1; i <= 5; i++) {
    console.log(`任务1: 数字 ${i}`);
    yield 500; // 暂停500毫秒
  }
}

// 任务2：打印字母
function* printLetters() {
  const letters = 'ABCDE';
  for (const letter of letters) {
    console.log(`任务2: 字母 ${letter}`);
    yield 300; // 暂停300毫秒
  }
}

// 添加任务到调度器
scheduler.add(printNumbers());
scheduler.add(printLetters());
```

## 9.2 Proxy与Reflect

### 9.2.1 Proxy基础

Proxy是ES6引入的一个特性，它允许我们拦截并自定义对对象的基本操作（如属性查找、赋值、枚举、函数调用等）。

```javascript
// 基本Proxy示例
const person = {
  name: '张三',
  age: 30
};

const personProxy = new Proxy(person, {
  // 拦截属性读取
  get(target, property) {
    console.log(`读取属性: ${property}`);
    return target[property];
  },
  
  // 拦截属性设置
  set(target, property, value) {
    console.log(`设置属性: ${property} = ${value}`);
    
    // 自定义验证逻辑
    if (property === 'age' && (typeof value !== 'number' || value < 0)) {
      throw new Error('年龄必须是非负数');
    }
    
    target[property] = value;
    return true; // 表示设置成功
  },
  
  // 拦截属性删除
  deleteProperty(target, property) {
    console.log(`删除属性: ${property}`);
    
    if (property === 'name') {
      throw new Error('不能删除name属性');
    }
    
    delete target[property];
    return true;
  },
  
  // 拦截属性检查
  has(target, property) {
    console.log(`检查属性是否存在: ${property}`);
    return property in target;
  }
});

// 测试代理
console.log(personProxy.name); // "读取属性: name" -> "张三"
personProxy.age = 31; // "设置属性: age = 31"
console.log(personProxy.age); // 31

try {
  personProxy.age = -5; // 抛出错误: 年龄必须是非负数
} catch (e) {
  console.error(e.message);
}

try {
  delete personProxy.name; // 抛出错误: 不能删除name属性
} catch (e) {
  console.error(e.message);
}

console.log('age' in personProxy); // "检查属性是否存在: age" -> true
```

### 9.2.2 Reflect API

Reflect是一个内置对象，它提供了拦截JavaScript操作的方法。这些方法与Proxy处理器的方法相同，但提供了更一致的API。

```javascript
const user = {
  name: '李四',
  _password: 'secret123'
};

const userProxy = new Proxy(user, {
  get(target, property) {
    // 使用Reflect.get获取属性值
    const value = Reflect.get(target, property);
    
    // 对私有属性进行特殊处理
    if (property.startsWith('_')) {
      throw new Error('无法访问私有属性');
    }
    
    return value;
  },
  
  set(target, property, value) {
    // 使用Reflect.set设置属性值
    if (property.startsWith('_')) {
      throw new Error('无法设置私有属性');
    }
    
    return Reflect.set(target, property, value);
  },
  
  // 拦截属性枚举
  ownKeys(target) {
    // 过滤掉私有属性
    return Reflect.ownKeys(target).filter(key => !key.startsWith('_'));
  }
});

console.log(userProxy.name); // "李四"

try {
  console.log(userProxy._password); // 抛出错误
} catch (e) {
  console.error(e.message);
}

console.log(Object.keys(userProxy)); // ["name"] (私有属性被过滤)
```

### 9.2.3 Proxy的高级应用

#### 1. 数据验证和类型检查

```javascript
function createTypeValidator(obj, schema) {
  return new Proxy(obj, {
    set(target, property, value) {
      if (schema[property]) {
        const type = schema[property];
        if (typeof value !== type) {
          throw new TypeError(`属性 ${property} 应该是 ${type} 类型`);
        }
      }
      
      return Reflect.set(target, property, value);
    }
  });
}

const productSchema = {
  name: 'string',
  price: 'number',
  inStock: 'boolean'
};

const product = createTypeValidator({}, productSchema);
product.name = '手机'; // 正确
product.price = 2999; // 正确
product.inStock = true; // 正确

try {
  product.price = '2999'; // 抛出错误
} catch (e) {
  console.error(e.message);
}
```

#### 2. 实现响应式数据

```javascript
function reactive(obj, onChange) {
  const handlers = {};
  
  return new Proxy(obj, {
    get(target, property) {
      // 创建依赖关系
      if (!handlers[property]) {
        handlers[property] = new Set();
      }
      
      // 假设我们有一个全局的依赖收集机制
      if (typeof window !== 'undefined' && window.currentEffect) {
        handlers[property].add(window.currentEffect);
      }
      
      return target[property];
    },
    
    set(target, property, value) {
      const oldValue = target[property];
      const result = Reflect.set(target, property, value);
      
      // 触发更新
      if (oldValue !== value && handlers[property]) {
        handlers[property].forEach(effect => effect());
        if (onChange) {
          onChange(property, oldValue, value);
        }
      }
      
      return result;
    }
  });
}

// 使用示例
const state = reactive({ count: 0 });

// 模拟一个effect函数
function effect(fn) {
  window.currentEffect = fn;
  fn();
  window.currentEffect = null;
}

effect(() => {
  console.log(`Count is: ${state.count}`);
}); // 当count变化时，这行代码会重新执行

state.count = 1; // 触发effect函数，打印 "Count is: 1"
state.count = 2; // 触发effect函数，打印 "Count is: 2"
```

#### 3. 实现观察者模式

```javascript
function observable(target) {
  const observers = new Map();
  
  return new Proxy(target, {
    set(obj, prop, value) {
      const oldValue = obj[prop];
      const result = Reflect.set(obj, prop, value);
      
      if (oldValue !== value && observers.has(prop)) {
        observers.get(prop).forEach(observer => {
          observer({ oldValue, newValue: value });
        });
      }
      
      return result;
    },
    
    subscribe(prop, observer) {
      if (!observers.has(prop)) {
        observers.set(prop, new Set());
      }
      observers.get(prop).add(observer);
      
      // 返回取消订阅函数
      return () => {
        if (observers.has(prop)) {
          observers.get(prop).delete(observer);
          if (observers.get(prop).size === 0) {
            observers.delete(prop);
          }
        }
      };
    }
  });
}

// 使用示例
const user = observable({ name: '王五', age: 25 });

const unsubscribe = user.subscribe('name', ({ oldValue, newValue }) => {
  console.log(`名字从 ${oldValue} 变为 ${newValue}`);
});

user.name = '赵六'; // 打印: 名字从 王五 变为 赵六

unsubscribe(); // 取消订阅
user.name = '钱七'; // 不会触发回调
```

## 9.3 模块与命名空间

### 9.3.1 ES模块（ES Modules）

ES6引入了官方的模块系统，使用`import`和`export`关键字来导入和导出模块。

```javascript
// math.js - 导出模块
export const PI = 3.14159;

export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

export default function multiply(a, b) {
  return a * b;
}

// main.js - 导入模块
import multiply, { add, subtract, PI } from './math.js';

console.log(PI); // 3.14159
console.log(add(5, 3)); // 8
console.log(subtract(5, 3)); // 2
console.log(multiply(5, 3)); // 15
```

### 9.3.2 CommonJS模块

CommonJS是Node.js使用的模块系统，使用`require`和`module.exports`。

```javascript
// math.js - CommonJS模块
const PI = 3.14159;

function add(a, b) {
  return a + b;
}

function subtract(a, b) {
  return a - b;
}

function multiply(a, b) {
  return a * b;
}

// 导出
module.exports = {
  PI,
  add,
  subtract,
  multiply
};

// main.js - 使用模块
const { PI, add, subtract, multiply } = require('./math.js');

console.log(PI); // 3.14159
console.log(add(5, 3)); // 8
console.log(subtract(5, 3)); // 2
console.log(multiply(5, 3)); // 15
```

### 9.3.3 命名空间模式

在大型JavaScript应用程序中，使用命名空间可以帮助组织代码，避免全局命名空间污染。

```javascript
// 创建命名空间
const MyApp = MyApp || {};

// 添加模块
MyApp.Utils = (function() {
  // 私有变量和函数
  let privateVar = '私有变量';
  
  function privateFunction() {
    console.log('私有函数');
  }
  
  // 公共API
  return {
    formatDate: function(date) {
      return date.toLocaleDateString();
    },
    
    debounce: function(func, wait) {
      let timeout;
      return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
      };
    },
    
    // 访问私有成员
    getPrivateVar: function() {
      return privateVar;
    }
  };
})();

// 添加另一个模块
MyApp.Data = (function() {
  // 私有变量
  const dataStore = {};
  
  return {
    set: function(key, value) {
      dataStore[key] = value;
    },
    
    get: function(key) {
      return dataStore[key];
    },
    
    remove: function(key) {
      delete dataStore[key];
    },
    
    getAll: function() {
      return { ...dataStore };
    }
  };
})();

// 使用命名空间
const today = new Date();
console.log(MyApp.Utils.formatDate(today)); // 格式化日期

MyApp.Data.set('user', { name: '用户1', age: 30 });
console.log(MyApp.Data.get('user')); // { name: '用户1', age: 30 }

console.log(MyApp.Utils.getPrivateVar()); // '私有变量'
```

## 9.4 内存管理与性能优化

### 9.4.1 JavaScript的内存管理

JavaScript具有自动垃圾回收机制，但了解其工作原理有助于编写更高效的代码。

```javascript
// 内存泄漏示例1：全局变量
var globalVar = { data: '大量数据' };

// 内存泄漏示例2：闭包
function createLeak() {
  const largeData = new Array(1000000).fill('数据');
  
  return function() {
    // 这个函数引用了largeData，导致largeData无法被回收
    console.log('函数执行');
  };
}

const leakyFunction = createLeak();

// 正确的闭包使用
function createNonLeak() {
  const largeData = new Array(1000000).fill('数据');
  
  return function() {
    // 不引用largeData，允许它被回收
    console.log('函数执行');
  };
}

const nonLeakyFunction = createNonLeak();

// 内存泄漏示例3：未清除的事件监听器
const button = document.getElementById('myButton');

// 添加事件监听器
function handleClick() {
  console.log('按钮点击');
}

button.addEventListener('click', handleClick);

// 在不需要时移除事件监听器
button.removeEventListener('click', handleClick);
```

### 9.4.2 性能优化技巧

#### 1. 使用适当的数据结构

```javascript
// 使用Map和Set提高查找性能
const arr = [1, 2, 3, 4, 5];
const set = new Set(arr);
const map = new Map(arr.map(item => [item, item * 2]));

// 数组查找 - O(n)
function findInArray(value) {
  return arr.includes(value); // 需要遍历整个数组
}

// Set查找 - O(1)
function findInSet(value) {
  return set.has(value); // 直接访问
}

// Map查找 - O(1)
function findInMap(key) {
  return map.has(key); // 直接访问
}
```

#### 2. 避免不必要的重复计算

```javascript
// 不好的做法：每次调用都重新计算
function calculateExpensiveValue(data) {
  // 假设这是一个耗时的计算
  let result = 0;
  for (let i = 0; i < 1000000; i++) {
    result += Math.sqrt(data);
  }
  return result;
}

function processData(items) {
  return items.map(item => {
    return {
      ...item,
      expensiveValue: calculateExpensiveValue(item.value) // 每个项都重新计算
    };
  });
}

// 好的做法：使用缓存
const memoCache = new Map();

function memoizedCalculateExpensiveValue(data) {
  if (memoCache.has(data)) {
    return memoCache.get(data);
  }
  
  // 计算并缓存结果
  let result = 0;
  for (let i = 0; i < 1000000; i++) {
    result += Math.sqrt(data);
  }
  
  memoCache.set(data, result);
  return result;
}

function processOptimizedData(items) {
  return items.map(item => {
    return {
      ...item,
      expensiveValue: memoizedCalculateExpensiveValue(item.value)
    };
  });
}
```

#### 3. 减少DOM操作

```javascript
// 不好的做法：频繁操作DOM
function createBadList(items) {
  const container = document.getElementById('container');
  
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    container.appendChild(li); // 每次添加都会触发重绘
  });
}

// 好的做法：使用文档片段
function createGoodList(items) {
  const container = document.getElementById('container');
  const fragment = document.createDocumentFragment();
  
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    fragment.appendChild(li); // 不会触发重绘
  });
  
  container.appendChild(fragment); // 只触发一次重绘
}

// 更好的做法：使用innerHTML
function createBestList(items) {
  const container = document.getElementById('container');
  const html = items.map(item => `<li>${item}</li>`).join('');
  container.innerHTML = html; // 只触发一次重绘
}
```

## 9.5 JavaScript中的函数式编程

### 9.5.1 函数式编程概念

函数式编程是一种编程范式，它将计算视为数学函数的求值，避免改变状态和可变数据。

```javascript
// 命令式编程
const numbers = [1, 2, 3, 4, 5];
const doubled = [];

for (let i = 0; i < numbers.length; i++) {
  doubled.push(numbers[i] * 2);
}

// 函数式编程
const doubledFunctional = numbers.map(num => num * 2);
```

### 9.5.2 纯函数与副作用

纯函数是函数式编程的核心概念，它满足两个条件：
1. 对于相同的输入，总是返回相同的输出
2. 没有副作用（不修改外部状态）

```javascript
// 纯函数
function add(a, b) {
  return a + b;
}

// 非纯函数（有副作用）
let total = 0;
function addToTotal(value) {
  total += value;
  return total;
}

// 将非纯函数转换为纯函数
function addToTotalPure(total, value) {
  return total + value;
}
```

### 9.5.3 高阶函数与函数组合

高阶函数是接受函数作为参数或返回函数的函数。

```javascript
// 高阶函数示例
function withLogging(fn) {
  return function(...args) {
    console.log(`调用函数 ${fn.name} 参数:`, args);
    const result = fn(...args);
    console.log(`函数 ${fn.name} 返回:`, result);
    return result;
  };
}

function multiply(a, b) {
  return a * b;
}

const loggedMultiply = withLogging(multiply);
loggedMultiply(3, 4); // 输出调用信息

// 函数组合
const compose = (...fns) => (initialValue) => 
  fns.reduceRight((acc, fn) => fn(acc), initialValue);

const addOne = x => x + 1;
const double = x => x * 2;
const toString = x => `结果: ${x}`;

const processNumber = compose(toString, double, addOne);

console.log(processNumber(3)); // "结果: 8"
```

### 9.5.4 函数式编程实践

```javascript
// 实现函数式的数据转换管道
const pipe = (...fns) => (initialValue) => 
  fns.reduce((acc, fn) => fn(acc), initialValue);

// 数据处理函数
const filterEven = numbers => numbers.filter(num => num % 2 === 0);
const multiplyByTwo = numbers => numbers.map(num => num * 2);
const sum = numbers => numbers.reduce((acc, num) => acc + num, 0);
const formatResult = total => `处理后的总和: ${total}`;

// 创建处理管道
const processNumbers = pipe(
  filterEven,
  multiplyByTwo,
  sum,
  formatResult
);

const numbers = [1, 2, 3, 4, 5, 6];
console.log(processNumbers(numbers)); // "处理后的总和: 36"

// 不可变数据操作
const updateUser = (users, userId, updates) => 
  users.map(user => 
    user.id === userId ? { ...user, ...updates } : user
  );

const users = [
  { id: 1, name: '用户1', age: 25 },
  { id: 2, name: '用户2', age: 30 }
];

const updatedUsers = updateUser(users, 1, { age: 26 });
console.log(updatedUsers[0].age); // 26
console.log(users[0].age); // 25 (原始数据不变)
```

## 9.6 元编程

元编程是指编写可以操作其他代码的代码，或者可以修改自身行为的代码。

```javascript
// 1. 使用Proxy实现属性拦截
const logger = {
  log(target, prop) {
    console.log(`访问 ${prop} 属性`);
    return target[prop];
  }
};

function addLogging(obj) {
  return new Proxy(obj, logger);
}

const data = { name: '元编程', version: '1.0' };
const loggedData = addLogging(data);

console.log(loggedData.name); // "访问 name 属性" -> "元编程"

// 2. 使用Reflect操作对象属性
const reflection = {
  get(target, prop) {
    return Reflect.get(target, prop);
  },
  
  set(target, prop, value) {
    console.log(`设置 ${prop} = ${value}`);
    return Reflect.set(target, prop, value);
  }
};

function addReflection(obj) {
  return new Proxy(obj, reflection);
}

const reflectedData = addReflection({ count: 0 });
reflectedData.count = 5; // "设置 count = 5"

// 3. 动态生成类
functioncreateClass(className, properties) {
  const classDefinition = {};
  
  Object.entries(properties).forEach(([key, value]) => {
    if (typeof value === 'function') {
      classDefinition[key] = value;
    } else {
      classDefinition[key] = {
        get() { return value; },
        set(newValue) { value = newValue; }
      };
    }
  });
  
  const DynamicClass = class {
    constructor() {
      Object.defineProperties(this, classDefinition);
    }
  };
  
  Object.defineProperty(DynamicClass, 'name', { value: className });
  return DynamicClass;
}

const User = createClass('User', {
  name: '',
  age: 0,
  
  greet() {
    return `你好，我是 ${this.name}，今年 ${this.age} 岁`;
  }
});

const user = new User();
user.name = '动态用户';
user.age = 30;
console.log(user.greet()); // "你好，我是 动态用户，今年 30 岁"
```

## 9.7 最佳实践

### 9.7.1 高级特性使用指南

1. **谨慎使用Proxy和Reflect**：虽然它们很强大，但可能会影响性能，应在需要时使用。
2. **合理使用生成器**：生成器适合处理异步流程和惰性计算，但不要滥用。
3. **模块化设计**：使用模块系统组织代码，避免全局命名空间污染。
4. **注意内存管理**：避免不必要的闭包和事件监听器，及时释放资源。
5. **考虑性能**：选择适当的数据结构和算法，避免不必要的重复计算。

### 9.7.2 代码风格建议

1. **保持函数纯度**：尽量编写纯函数，减少副作用。
2. **使用函数式编程思维**：考虑使用高阶函数和函数组合来简化代码。
3. **适当使用元编程**：元编程可以解决一些复杂问题，但也要考虑代码的可读性。
4. **错误处理**：使用适当的错误处理机制，避免应用崩溃。

## 9.8 总结与练习

### 9.8.1 本章要点

1. **生成器与迭代器**：理解JavaScript中的迭代协议和生成器函数的使用。
2. **Proxy与Reflect**：掌握如何使用Proxy拦截和自定义对象操作。
3. **模块与命名空间**：了解JavaScript中的模块系统和命名空间模式。
4. **内存管理与性能优化**：学习JavaScript的内存管理机制和性能优化技巧。
5. **函数式编程**：掌握函数式编程的核心概念和在JavaScript中的应用。
6. **元编程**：了解元编程的概念和基本实现方法。

### 9.8.2 实践练习

1. **练习1：自定义数据结构**
   - 使用Proxy创建一个只读对象
   - 实现一个验证对象，确保所有属性符合特定规则
   - 创建一个观察对象，记录所有属性的访问和修改

2. **练习2：生成器应用**
   - 创建一个生成器，按需读取大文件的内容
   - 实现一个异步任务队列，使用生成器控制执行顺序
   - 创建一个可取消的异步操作生成器

3. **练习3：函数式编程实践**
   - 使用函数式编程方式重构现有代码
   - 实现一个函数式的状态管理器
   - 创建一个工具库，包含常用的高阶函数

4. **练习4：性能优化**
   - 分析现有代码的性能瓶颈
   - 实现一个简单的缓存机制
   - 优化DOM操作，减少重绘和回流

通过本章的学习，你应该已经掌握了JavaScript的一些高级特性，这些知识将帮助你编写更高效、更灵活的代码。在下一章中，我们将探讨JavaScript的模块化与构建工具，了解如何组织和管理大型JavaScript项目。