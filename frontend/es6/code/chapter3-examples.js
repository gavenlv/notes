// 第3章：箭头函数与函数增强 - 代码示例

// 1. 传统函数与箭头函数的对比
console.log('=== 传统函数与箭头函数的对比 ===');

// 传统函数声明
function add(a, b) {
  return a + b;
}

// 函数表达式
const multiply = function(a, b) {
  return a * b;
};

// ES6箭头函数
const subtract = (a, b) => {
  return a - b;
};

// 简化形式
const divide = (a, b) => a / b;

console.log('add(5, 3):', add(5, 3));
console.log('multiply(5, 3):', multiply(5, 3));
console.log('subtract(5, 3):', subtract(5, 3));
console.log('divide(6, 3):', divide(6, 3));

// 2. 箭头函数的语法规则
console.log('\n=== 箭头函数的语法规则 ===');

// 基本语法
const greet = (name) => {
  return `Hello, ${name}!`;
};

// 单参数时可省略括号
const sayHello = name => `Hello, ${name}!`;

// 无参数时必须使用括号
const getRandom = () => Math.random();

// 多参数时必须使用括号
const sum = (a, b) => a + b;

// 函数体有多条语句时必须使用大括号
const calculate = (a, b) => {
  const sum = a + b;
  const difference = a - b;
  return { sum, difference };
};

// 返回对象字面量时需要用括号包裹
const createUser = (name, age) => ({ name, age });

console.log('greet("Alice"):', greet("Alice"));
console.log('sayHello("Bob"):', sayHello("Bob"));
console.log('getRandom():', getRandom());
console.log('sum(5, 3):', sum(5, 3));
console.log('calculate(10, 4):', calculate(10, 4));
console.log('createUser("Charlie", 25):', createUser("Charlie", 25));

// 3. 箭头函数中的this
console.log('\n=== 箭头函数中的this ===');

const person = {
  name: 'Alice',
  age: 30,
  
  // 传统函数中的this指向调用者
  sayNameTraditional: function() {
    console.log('Traditional function - this.name:', this.name);
    setTimeout(function() {
      console.log('Traditional callback - this.name:', this.name);
    }, 10);
  },
  
  // 箭头函数中的this继承自外层作用域
  sayNameArrow: function() {
    console.log('Outer function - this.name:', this.name);
    setTimeout(() => {
      console.log('Arrow callback - this.name:', this.name);
    }, 20);
  }
};

person.sayNameTraditional();
person.sayNameArrow();

// 4. 默认参数
console.log('\n=== 默认参数 ===');

// ES6默认参数
function greetWithDefault(name = 'Guest') {
  console.log(`Hello, ${name}!`);
}

greetWithDefault(); // 使用默认值
greetWithDefault('Alice'); // 使用传入值
greetWithDefault(undefined); // 使用默认值
greetWithDefault(null); // 使用null值

// 多个默认参数
function createPerson(name = 'Anonymous', age = 0, isActive = true) {
  return { name, age, isActive };
}

console.log(createPerson());
console.log(createPerson('Alice'));
console.log(createPerson('Bob', 30));
console.log(createPerson('Charlie', 40, false));

// 使用表达式作为默认值
function getRandomNumber(max = Math.random() * 100) {
  return Math.floor(max);
}

console.log('getRandomNumber():', getRandomNumber());
console.log('getRandomNumber(50):', getRandomNumber(50));

// 使用前面定义的参数作为后面参数的默认值
function createRectangle(width = 10, height = width) {
  return { width, height, area: width * height };
}

console.log(createRectangle());
console.log(createRectangle(5));
console.log(createRectangle(5, 8));

// 5. 剩余参数
console.log('\n=== 剩余参数 ===');

function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}

console.log('sum(1, 2, 3):', sum(1, 2, 3));
console.log('sum(1, 2, 3, 4, 5):', sum(1, 2, 3, 4, 5));
console.log('sum():', sum());

// 与普通参数混合使用
function greetMultiple(greeting, ...names) {
  names.forEach(name => {
    console.log(`${greeting}, ${name}!`);
  });
}

greetMultiple('Hello', 'Alice', 'Bob', 'Charlie');

// 6. 扩展运算符
console.log('\n=== 扩展运算符 ===');

// 函数调用中的扩展运算符
const numbers = [1, 5, 3, 9, 2];
console.log('Math.max(...numbers):', Math.max(...numbers));
console.log('Math.min(...numbers):', Math.min(...numbers));

// 数组合并
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2];
console.log('combined:', combined);

// 在数组中间插入元素
const parts = ['shoulders', 'knees'];
const body = ['head', ...parts, 'and', 'toes'];
console.log('body:', body);

// 对象扩展运算符
const personObj = { name: 'Alice', age: 30 };
const employee = { ...personObj, position: 'Developer' };
console.log('employee:', employee);

// 覆盖属性
const updatedPerson = { ...personObj, age: 31 };
console.log('updatedPerson:', updatedPerson);

// 7. 实际应用场景
console.log('\n=== 实际应用场景 ===');

// 函数参数处理
function log(level, message, ...data) {
  console.log(`[${level}] ${message}`, ...data);
}

log('INFO', 'User logged in', { id: 123, name: 'Alice' });

// 数组操作
const original = [1, 2, 3];
const copy = [...original];
const withNewElement = [...original, 4];
const withElementAtStart = [0, ...original];

console.log('copy:', copy);
console.log('withNewElement:', withNewElement);
console.log('withElementAtStart:', withElementAtStart);

// 对象操作
const defaults = { theme: 'light', fontSize: 16 };
const userSettings = { theme: 'dark' };
const finalSettings = { ...defaults, ...userSettings };
console.log('finalSettings:', finalSettings);

// 解构与剩余参数
const [first, second, ...rest] = [1, 2, 3, 4, 5];
console.log('first:', first, 'second:', second, 'rest:', rest);

const { name, ...otherProps } = { name: 'Alice', age: 30, city: 'New York' };
console.log('name:', name, 'otherProps:', otherProps);

// 8. 函数的name属性
console.log('\n=== 函数的name属性 ===');

function myFunction() {}
const myFunc = function() {};
const arrowFunc = () => {};
const obj = {
  myMethod() {},
  anotherMethod: function() {}
};

console.log('myFunction.name:', myFunction.name);
console.log('myFunc.name:', myFunc.name);
console.log('arrowFunc.name:', arrowFunc.name);
console.log('obj.myMethod.name:', obj.myMethod.name);
console.log('obj.anotherMethod.name:', obj.anotherMethod.name);

// 9. 练习1：使用箭头函数重构代码
console.log('\n=== 练习1：使用箭头函数重构代码 ===');

// 原始代码
function doubleNumbersOriginal(numbers) {
  return numbers.map(function(num) {
    return num * 2;
  });
}

function filterEvenNumbersOriginal(numbers) {
  return numbers.filter(function(num) {
    return num % 2 === 0;
  });
}

function sumNumbersOriginal(numbers) {
  return numbers.reduce(function(sum, num) {
    return sum + num;
  }, 0);
}

// 重构后的代码
const doubleNumbers = numbers => numbers.map(num => num * 2);
const filterEvenNumbers = numbers => numbers.filter(num => num % 2 === 0);
const sumNumbers = numbers => numbers.reduce((sum, num) => sum + num, 0);

const testNumbers = [1, 2, 3, 4, 5, 6];
console.log('doubleNumbers:', doubleNumbers(testNumbers));
console.log('filterEvenNumbers:', filterEvenNumbers(testNumbers));
console.log('sumNumbers:', sumNumbers(testNumbers));

// 10. 练习2：使用默认参数和剩余参数
console.log('\n=== 练习2：使用默认参数和剩余参数 ===');

// 创建一个函数，可以接受任意数量的数字参数，并返回它们的平均值
function average(...numbers) {
  if (numbers.length === 0) return 0;
  return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
}

console.log('average():', average());
console.log('average(1, 2, 3):', average(1, 2, 3));
console.log('average(1, 2, 3, 4, 5):', average(1, 2, 3, 4, 5));

// 11. 练习3：解决this绑定问题
console.log('\n=== 练习3：解决this绑定问题 ===');

// 原始代码（有问题）
const counterOriginal = {
  count: 0,
  start: function() {
    setInterval(function() {
      this.count++;
      console.log('Original counter:', this.count);
    }, 100);
  }
};

// 修复后的代码
const counter = {
  count: 0,
  start: function() {
    setInterval(() => {
      this.count++;
      console.log('Fixed counter:', this.count);
    }, 100);
  }
};

// 注意：为了演示，我们只运行3次计数器
counter.start();
setTimeout(() => {
  console.log('计数器演示结束');
}, 350);

// 12. 最佳实践示例
console.log('\n=== 最佳实践示例 ===');

// 使用对象参数处理多个可选参数
function createUser(options = {}) {
  const {
    name = 'Anonymous',
    age = 0,
    email = null,
    isActive = true
  } = options;
  
  return { name, age, email, isActive };
}

const user1 = createUser();
const user2 = createUser({ name: 'Alice', age: 30 });
const user3 = createUser({ name: 'Bob', email: 'bob@example.com' });

console.log('user1:', user1);
console.log('user2:', user2);
console.log('user3:', user3);

// 使用扩展运算符进行对象合并
const defaultConfig = { theme: 'light', lang: 'en', fontSize: 16 };
const userConfig = { theme: 'dark', fontSize: 18 };
const finalConfig = { ...defaultConfig, ...userConfig };
console.log('finalConfig:', finalConfig);

// 使用箭头函数处理数组
const users = [
  { id: 1, name: 'Alice', age: 30 },
  { id: 2, name: 'Bob', age: 25 },
  { id: 3, name: 'Charlie', age: 35 }
];

// 获取所有用户名
const userNames = users.map(user => user.name);
console.log('userNames:', userNames);

// 筛选年龄大于30的用户
const olderUsers = users.filter(user => user.age > 30);
console.log('olderUsers:', olderUsers);

// 计算所有用户的平均年龄
const averageAge = users.reduce((sum, user, _, { length }) => sum + user.age / length, 0);
console.log('averageAge:', averageAge.toFixed(2));

console.log('\n=== 第3章代码示例结束 ===');