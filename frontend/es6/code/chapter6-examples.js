// 第6章：对象与数组的增强 - 代码示例

// ===== 6.1 对象字面量增强 =====

// 6.1.1 属性简写
console.log('=== 6.1.1 属性简写 ===');

// ES5
var name = 'Alice';
var age = 25;
var personES5 = {
  name: name,
  age: age
};

// ES6
const nameES6 = 'Alice';
const ageES6 = 25;
const personES6 = {
  name: nameES6,  // 属性名与变量名相同，可简写
  age: ageES6
};

console.log('ES5方式:', personES5);
console.log('ES6方式:', personES6);

// 6.1.2 方法简写
console.log('\n=== 6.1.2 方法简写 ===');

// ES5
var calculatorES5 = {
  add: function(a, b) {
    return a + b;
  },
  subtract: function(a, b) {
    return a - b;
  }
};

// ES6
const calculatorES6 = {
  add(a, b) {
    return a + b;
  },
  subtract(a, b) {
    return a - b;
  }
};

console.log('ES5加法:', calculatorES5.add(5, 3));
console.log('ES6加法:', calculatorES6.add(5, 3));
console.log('ES5减法:', calculatorES5.subtract(5, 3));
console.log('ES6减法:', calculatorES6.subtract(5, 3));

// 6.1.3 计算属性名
console.log('\n=== 6.1.3 计算属性名 ===');

// ES5
var prop = 'name';
var personES5_2 = {};
personES5_2[prop] = 'Alice';

// ES6
const propES6 = 'name';
const prefix = 'user';
const personES6_2 = {
  [propES6]: 'Alice',
  [`${prefix}Id`]: 123,
  ['full' + 'Name']: 'Alice Smith'
};

console.log('ES5方式:', personES5_2);
console.log('ES6方式:', personES6_2);

// ===== 6.2 数组新增方法 =====

// 6.2.1 Array.from()
console.log('\n=== 6.2.1 Array.from() ===');

// 从类数组对象创建数组
const arrayLike = {
  0: 'a',
  1: 'b',
  2: 'c',
  length: 3
};
const arr1 = Array.from(arrayLike);
console.log('从类数组对象创建数组:', arr1);

// 从字符串创建数组
const str = 'hello';
const arr2 = Array.from(str);
console.log('从字符串创建数组:', arr2);

// 使用映射函数
const arr3 = Array.from([1, 2, 3], x => x * 2);
console.log('使用映射函数:', arr3);

// 从Set创建数组
const set = new Set([1, 2, 3, 2, 1]);
const arr4 = Array.from(set);
console.log('从Set创建数组:', arr4);

// 6.2.2 Array.of()
console.log('\n=== 6.2.2 Array.of() ===');

// Array构造函数的问题
const arr5 = new Array(3); // 创建一个长度为3的空数组
console.log('new Array(3):', arr5);

const arr6 = new Array(1, 2, 3); // 创建包含1, 2, 3的数组
console.log('new Array(1, 2, 3):', arr6);

// Array.of解决了这个问题
const arr7 = Array.of(3); // 创建包含3的数组
console.log('Array.of(3):', arr7);

const arr8 = Array.of(1, 2, 3); // 创建包含1, 2, 3的数组
console.log('Array.of(1, 2, 3):', arr8);

// 6.2.3 find() 和 findIndex()
console.log('\n=== 6.2.3 find() 和 findIndex() ===');

const numbers = [5, 12, 8, 130, 44];

// find示例
const found = numbers.find(element => element > 10);
console.log('find()结果:', found);

// findIndex示例
const foundIndex = numbers.findIndex(element => element > 10);
console.log('findIndex()结果:', foundIndex);

// 查找对象
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' },
  { id: 3, name: 'Charlie' }
];

const user = users.find(u => u.id === 2);
console.log('找到的用户:', user);

const userIndex = users.findIndex(u => u.id === 2);
console.log('用户索引:', userIndex);

// 6.2.4 fill()
console.log('\n=== 6.2.4 fill() ===');

const arr9 = [1, 2, 3, 4];
arr9.fill(0);
console.log('fill(0):', arr9);

const arr10 = [1, 2, 3, 4];
arr10.fill(0, 1, 3); // 从索引1开始，到索引3（不包括3）结束
console.log('fill(0, 1, 3):', arr10);

// 创建指定长度并填充的数组
const arr11 = Array(5).fill(0);
console.log('Array(5).fill(0):', arr11);

// 填充对象
const arr12 = Array(3).fill({});
arr12[0].name = 'Alice';
console.log('填充对象问题:', arr12);

// 解决方案：使用map
const arr13 = Array(3).fill().map(() => ({}));
arr13[0].name = 'Alice';
console.log('填充对象解决方案:', arr13);

// 6.2.5 copyWithin()
console.log('\n=== 6.2.5 copyWithin() ===');

const arr14 = [1, 2, 3, 4, 5];
arr14.copyWithin(0, 3); // 从索引3开始复制，到索引0开始粘贴
console.log('copyWithin(0, 3):', arr14);

const arr15 = [1, 2, 3, 4, 5];
arr15.copyWithin(1, 3, 5); // 从索引3开始到索引5（不包括5）结束复制，到索引1开始粘贴
console.log('copyWithin(1, 3, 5):', arr15);

const arr16 = [1, 2, 3, 4, 5];
arr16.copyWithin(-2, 0); // 从索引0开始复制，到倒数第二个位置开始粘贴
console.log('copyWithin(-2, 0):', arr16);

// 6.2.6 entries(), keys(), values()
console.log('\n=== 6.2.6 entries(), keys(), values() ===');

const arr17 = ['a', 'b', 'c'];

// entries() 返回键值对迭代器
console.log('entries():');
for (const [index, value] of arr17.entries()) {
  console.log(`  ${index}: ${value}`);
}

// keys() 返回键迭代器
console.log('keys():');
for (const key of arr17.keys()) {
  console.log(`  ${key}`);
}

// values() 返回值迭代器
console.log('values():');
for (const value of arr17.values()) {
  console.log(`  ${value}`);
}

// 6.2.7 includes()
console.log('\n=== 6.2.7 includes() ===');

const arr18 = [1, 2, 3, NaN];

console.log('includes(2):', arr18.includes(2));
console.log('includes(4):', arr18.includes(4));

// 与indexOf的区别：includes能正确识别NaN
console.log('includes(NaN):', arr18.includes(NaN));
console.log('indexOf(NaN):', arr18.indexOf(NaN));

// 可指定起始位置
console.log('includes(2, 1):', arr18.includes(2, 1));
console.log('includes(2, 2):', arr18.includes(2, 2));

// ===== 6.3 对象新增方法 =====

// 6.3.1 Object.assign()
console.log('\n=== 6.3.1 Object.assign() ===');

// 基本用法
const target = { a: 1, b: 2 };
const source = { b: 3, c: 4 };

const returnedTarget = Object.assign(target, source);

console.log('目标对象:', target);
console.log('返回值:', returnedTarget);
console.log('目标对象 === 返回值:', target === returnedTarget);

// 多个源对象
const obj1 = { a: 1 };
const obj2 = { b: 2 };
const obj3 = { c: 3 };

const obj = Object.assign(obj1, obj2, obj3);
console.log('合并多个对象:', obj);
console.log('obj1也被修改:', obj1);

// 浅拷贝
const original = { a: 1, b: { c: 2 } };
const copy = Object.assign({}, original);
console.log('浅拷贝:', copy);

copy.b.c = 3;
console.log('修改拷贝后，原始对象:', original); // 原始对象也被改变，因为是浅拷贝

// 合并具有相同属性的对象
const o1 = { a: 1, b: 1, c: 1 };
const o2 = { b: 2, c: 2 };
const o3 = { c: 3 };

const obj4 = Object.assign({}, o1, o2, o3);
console.log('相同属性合并:', obj4); // 后面的属性会覆盖前面的

// 6.3.2 Object.is()
console.log('\n=== 6.3.2 Object.is() ===');

// 与===的区别
console.log('Object.is(25, 25):', Object.is(25, 25));
console.log('Object.is("foo", "foo"):', Object.is('foo', 'foo'));
console.log('Object.is("foo", "bar"):', Object.is('foo', 'bar'));
console.log('Object.is(null, null):', Object.is(null, null));

console.log('Object.is(0, -0):', Object.is(0, -0));
console.log('0 === -0:', 0 === -0);

console.log('Object.is(NaN, NaN):', Object.is(NaN, NaN));
console.log('NaN === NaN:', NaN === NaN);

console.log('Object.is(-0, 0):', Object.is(-0, 0));
console.log('Object.is(0, 0):', Object.is(0, 0));

// 6.3.3 Object.getOwnPropertyDescriptors()
console.log('\n=== 6.3.3 Object.getOwnPropertyDescriptors() ===');

const obj5 = {
  a: 1,
  get b() { return 2; },
  set c(value) { this.a = value; }
};

const descriptors = Object.getOwnPropertyDescriptors(obj5);
console.log('属性描述符:', descriptors);

// 6.3.4 Object.setPrototypeOf() 和 Object.getPrototypeOf()
console.log('\n=== 6.3.4 Object.setPrototypeOf() 和 Object.getPrototypeOf() ===');

const obj6 = {};
const prototypeObj = { a: 1 };

// 设置原型
Object.setPrototypeOf(obj6, prototypeObj);
console.log('设置原型后，obj6.a:', obj6.a);

// 获取原型
const proto = Object.getPrototypeOf(obj6);
console.log('获取的原型 === prototypeObj:', proto === prototypeObj);

// 与__proto__的区别
const obj7 = {};
obj7.__proto__ = prototypeObj;
console.log('使用__proto__设置原型后，obj7.a:', obj7.a);

// 6.3.5 Object.keys(), Object.values(), Object.entries()
console.log('\n=== 6.3.5 Object.keys(), Object.values(), Object.entries() ===');

const obj8 = {
  a: 1,
  b: 2,
  c: 3
};

// Object.keys() - 获取键数组
const keys = Object.keys(obj8);
console.log('Object.keys():', keys);

// Object.values() - 获取值数组
const values = Object.values(obj8);
console.log('Object.values():', values);

// Object.entries() - 获取键值对数组
const entries = Object.entries(obj8);
console.log('Object.entries():', entries);

// 遍历对象
console.log('使用Object.entries()遍历对象:');
for (const [key, value] of Object.entries(obj8)) {
  console.log(`  ${key}: ${value}`);
}

// ===== 6.4 迭代器与for...of循环 =====

// 6.4.1 迭代器协议
console.log('\n=== 6.4.1 迭代器协议 ===');

// 创建一个简单的迭代器
function createIterator(array) {
  let index = 0;
  
  return {
    next() {
      if (index < array.length) {
        return { value: array[index++], done: false };
      } else {
        return { done: true };
      }
    }
  };
}

const iterator = createIterator(['a', 'b', 'c']);
console.log('iterator.next():', iterator.next());
console.log('iterator.next():', iterator.next());
console.log('iterator.next():', iterator.next());
console.log('iterator.next():', iterator.next());

// 6.4.2 可迭代协议
console.log('\n=== 6.4.2 可迭代协议 ===');

// 创建一个可迭代对象
const myIterable = {
  data: ['a', 'b', 'c'],
  [Symbol.iterator]() {
    let index = 0;
    const data = this.data;
    
    return {
      next() {
        if (index < data.length) {
          return { value: data[index++], done: false };
        } else {
          return { done: true };
        }
      }
    };
  }
};

// 使用for...of遍历
console.log('使用for...of遍历可迭代对象:');
for (const item of myIterable) {
  console.log(`  ${item}`);
}

// 使用扩展运算符
console.log('使用扩展运算符:', [...myIterable]);

// 使用解构赋值
const [first, second] = myIterable;
console.log('使用解构赋值:', first, second);

// 6.4.3 for...of循环
console.log('\n=== 6.4.3 for...of循环 ===');

// 遍历数组
const arr19 = ['a', 'b', 'c'];
console.log('遍历数组:');
for (const item of arr19) {
  console.log(`  ${item}`);
}

// 遍历字符串
const str2 = 'hello';
console.log('遍历字符串:');
for (const char of str2) {
  console.log(`  ${char}`);
}

// 遍历Map
const map = new Map([
  ['a', 1],
  ['b', 2],
  ['c', 3]
]);

console.log('遍历Map:');
for (const [key, value] of map) {
  console.log(`  ${key}: ${value}`);
}

// 遍历Set
const set2 = new Set(['a', 'b', 'c']);
console.log('遍历Set:');
for (const item of set2) {
  console.log(`  ${item}`);
}

// 6.4.4 内置迭代器
console.log('\n=== 6.4.4 内置迭代器 ===');

// entries() 返回键值对迭代器
const arr20 = ['a', 'b', 'c'];
console.log('使用entries():');
for (const [index, value] of arr20.entries()) {
  console.log(`  ${index}: ${value}`);
}

// keys() 返回键迭代器
console.log('使用keys():');
for (const key of arr20.keys()) {
  console.log(`  ${key}`);
}

// values() 返回值迭代器
console.log('使用values():');
for (const value of arr20.values()) {
  console.log(`  ${value}`);
}

// ===== 6.5 实际应用场景 =====

// 6.5.1 对象属性简写和方法简写
console.log('\n=== 6.5.1 对象属性简写和方法简写 ===');

// API请求示例
function fetchUserData(userId) {
  // 模拟API请求
  return new Promise(resolve => {
    setTimeout(() => {
      const data = { id: userId, name: 'Alice', email: 'alice@example.com' };
      resolve(data);
    }, 100);
  }).then(data => {
    // 使用属性简写
    return {
      id: data.id,
      name: data.name,
      email: data.email
    };
  });
}

// 使用方法简写
const userService = {
  baseUrl: '/api/users',
  
  // 方法简写
  async getUser(id) {
    // 模拟API请求
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ id, name: 'User ' + id });
      }, 50);
    });
  },
  
  async createUser(userData) {
    // 模拟API请求
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ id: Date.now(), ...userData });
      }, 50);
    });
  },
  
  async updateUser(id, userData) {
    // 模拟API请求
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ id, ...userData });
      }, 50);
    });
  }
};

// 使用示例
userService.getUser(1).then(user => console.log('获取用户:', user));
userService.createUser({ name: 'Bob', email: 'bob@example.com' }).then(user => console.log('创建用户:', user));
userService.updateUser(1, { name: 'Alice Smith' }).then(user => console.log('更新用户:', user));

// 6.5.2 数组方法的应用
console.log('\n=== 6.5.2 数组方法的应用 ===');

// 数据处理示例
const users2 = [
  { id: 1, name: 'Alice', age: 25, active: true },
  { id: 2, name: 'Bob', age: 30, active: false },
  { id: 3, name: 'Charlie', age: 35, active: true },
  { id: 4, name: 'David', age: 28, active: true }
];

// 使用find查找特定用户
const activeUser = users2.find(user => user.id === 3);
console.log('查找ID为3的用户:', activeUser);

// 使用findIndex查找特定用户的索引
const bobIndex = users2.findIndex(user => user.name === 'Bob');
console.log('Bob的索引:', bobIndex);

// 使用includes检查是否存在特定用户
const userIds = users2.map(user => user.id);
console.log('是否存在ID为3的用户:', userIds.includes(3));

// 使用entries获取索引和值
console.log('使用entries遍历用户:');
for (const [index, user] of users2.entries()) {
  console.log(`  ${index}: ${user.name}`);
}

// 使用Array.from处理类数组对象
function getArguments() {
  return Array.from(arguments).map(arg => arg.toUpperCase());
}
console.log('处理函数参数:', getArguments('a', 'b', 'c'));

// 使用fill创建数组并初始化
const matrix = Array(5).fill(null).map(() => Array(5).fill(0));
console.log('5x5矩阵:', matrix);

// 6.5.3 对象方法的应用
console.log('\n=== 6.5.3 对象方法的应用 ===');

// 配置合并示例
const defaultConfig = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3,
  headers: {
    'Content-Type': 'application/json'
  }
};

const userConfig = {
  timeout: 10000,
  headers: {
    'Authorization': 'Bearer token123'
  }
};

// 使用Object.assign合并配置
const config = Object.assign({}, defaultConfig, userConfig);
console.log('合并后的配置:', config);

// 使用展开运算符合并配置（ES2018+）
const config2 = { ...defaultConfig, ...userConfig };
console.log('使用展开运算符合并的配置:', config2);

// 使用Object.keys遍历对象属性
console.log('使用Object.keys遍历配置:');
for (const key of Object.keys(config)) {
  console.log(`  ${key}: ${config[key]}`);
}

// 使用Object.entries遍历对象键值对
console.log('使用Object.entries遍历配置:');
for (const [key, value] of Object.entries(config)) {
  console.log(`  ${key}:`, value);
}

// 使用Object.values获取对象值数组
const configValues = Object.values(config);
console.log('配置值数组:', configValues);

// 6.5.4 迭代器的应用
console.log('\n=== 6.5.4 迭代器的应用 ===');

// 自定义迭代器示例：斐波那契数列
class Fibonacci {
  constructor(limit) {
    this.limit = limit;
  }
  
  [Symbol.iterator]() {
    let a = 0, b = 1, count = 0;
    
    return {
      next: () => {
        if (count++ < this.limit) {
          const value = a;
          [a, b] = [b, a + b];
          return { value, done: false };
        } else {
          return { done: true };
        }
      }
    };
  }
}

const fib = new Fibonacci(10);
console.log('斐波那契数列前10项:');
for (const num of fib) {
  console.log(`  ${num}`);
}

// 自定义可迭代对象：范围
class Range {
  constructor(start, end, step = 1) {
    this.start = start;
    this.end = end;
    this.step = step;
  }
  
  [Symbol.iterator]() {
    let current = this.start;
    
    return {
      next: () => {
        if (current <= this.end) {
          const value = current;
          current += this.step;
          return { value, done: false };
        } else {
          return { done: true };
        }
      }
    };
  }
}

const range = new Range(1, 5);
console.log('范围1-5:', [...range]);

// ===== 6.6 实践练习 =====

// 练习1：对象字面量增强
console.log('\n=== 练习1：对象字面量增强 ===');

function createPerson(name, age, job) {
  const id = `person_${name}_${age}`;
  
  return {
    name,  // 属性简写
    age,   // 属性简写
    job,
    introduce() {  // 方法简写
      return `Hi, I'm ${this.name}, ${this.age} years old, and I work as a ${this.job}.`;
    },
    [id]: true  // 计算属性名
  };
}

const person = createPerson('Alice', 30, 'developer');
console.log('创建的人物:', person);
console.log('介绍:', person.introduce());

// 练习2：数组方法应用
console.log('\n=== 练习2：数组方法应用 ===');

const students = [
  { id: 1, name: 'Alice', score: 85, active: true },
  { id: 2, name: 'Bob', score: 92, active: false },
  { id: 3, name: 'Charlie', score: 78, active: true },
  { id: 4, name: 'David', score: 95, active: true },
  { id: 5, name: 'Eve', score: 88, active: false }
];

// 1. 找到第一个活跃且分数大于80的学生
const activeHighScoreStudent = students.find(student => student.active && student.score > 80);
console.log('第一个活跃且分数大于80的学生:', activeHighScoreStudent);

// 2. 找到分数最高的学生的索引
const highestScoreIndex = students.findIndex(student => 
  student.score === Math.max(...students.map(s => s.score))
);
console.log('分数最高的学生的索引:', highestScoreIndex);

// 3. 检查是否存在id为5的学生
const hasStudentWithId5 = students.some(student => student.id === 5);
console.log('是否存在id为5的学生:', hasStudentWithId5);

// 4. 创建一个包含所有活跃学生分数的数组
const activeStudentScores = students
  .filter(student => student.active)
  .map(student => student.score);
console.log('所有活跃学生的分数:', activeStudentScores);

// 5. 创建一个5x5的矩阵，初始值为0
const matrix5x5 = Array(5).fill(null).map(() => Array(5).fill(0));
console.log('5x5矩阵:', matrix5x5);

// 练习3：对象方法应用
console.log('\n=== 练习3：对象方法应用 ===');

function mergeConfigs(...configs) {
  // 使用Object.assign合并所有配置
  const merged = Object.assign({}, ...configs);
  
  // 输出合并后配置的键
  console.log('配置键:', Object.keys(merged));
  
  // 输出合并后配置的值
  console.log('配置值:', Object.values(merged));
  
  // 输出合并后配置的键值对
  console.log('配置键值对:');
  for (const [key, value] of Object.entries(merged)) {
    console.log(`  ${key}: ${value}`);
  }
  
  return merged;
}

const config1 = { a: 1, b: 2 };
const config2 = { b: 3, c: 4 };
const config3 = { d: 5 };

const mergedConfig = mergeConfigs(config1, config2, config3);
console.log('合并后的配置:', mergedConfig);

// 练习4：自定义迭代器
console.log('\n=== 练习4：自定义迭代器 ===');

class PrimeNumbers {
  constructor(max) {
    this.max = max;
  }
  
  [Symbol.iterator]() {
    let current = 2;
    
    return {
      next: () => {
        // 找到下一个质数
        while (current <= this.max && !this.isPrime(current)) {
          current++;
        }
        
        if (current <= this.max) {
          return { value: current++, done: false };
        } else {
          return { done: true };
        }
      }
    };
  }
  
  isPrime(num) {
    if (num <= 1) return false;
    if (num <= 3) return true;
    
    if (num % 2 === 0 || num % 3 === 0) return false;
    
    for (let i = 5; i * i <= num; i += 6) {
      if (num % i === 0 || num % (i + 2) === 0) return false;
    }
    
    return true;
  }
}

const primes = new PrimeNumbers(20);
console.log('20以内的质数:');
for (const prime of primes) {
  console.log(`  ${prime}`);
}

// 使用扩展运算符转换为数组
const primesArray = [...new PrimeNumbers(20)];
console.log('质数数组:', primesArray);

// 使用解构赋值获取前几个质数
const [firstPrime, secondPrime, thirdPrime] = new PrimeNumbers(20);
console.log('前三个质数:', firstPrime, secondPrime, thirdPrime);

console.log('\n=== 第6章代码示例结束 ===');