# 第2章：JavaScript语法与数据类型

## 2.1 JavaScript基础语法

### 2.1.1 语句与表达式

JavaScript代码由一系列语句组成，语句是执行操作的指令，而表达式是能产生值的代码片段。

**语句示例：**
```javascript
// 声明语句
let x = 10;
const y = 20;
var z = 30;

// 条件语句
if (x > 5) {
    console.log('x大于5');
}

// 循环语句
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// 函数声明语句
function greet(name) {
    return 'Hello, ' + name;
}
```

**表达式示例：**
```javascript
// 算术表达式
10 + 5          // 结果: 15
x * y           // 结果: 200

// 字符串表达式
'Hello' + ', ' + 'World'  // 结果: "Hello, World"

// 逻辑表达式
x > 5 && y < 25  // 结果: true

// 函数调用表达式
console.log('Hello')  // 输出: Hello

// 对象创建表达式
new Date()  // 创建一个新的Date对象
```

### 2.1.2 标识符命名规则

标识符是用来命名变量、函数、属性等的名称。JavaScript标识符必须遵循以下规则：

1. 必须以字母、下划线(_)或美元符号($)开头
2. 后续字符可以是字母、数字、下划线或美元符号
3. 不能使用JavaScript保留字作为标识符
4. 区分大小写

```javascript
// 有效的标识符
let userName;
let _privateVariable;
let $specialValue;
let counter123;

// 无效的标识符
// let 123abc;  // 以数字开头
// let user-name;  // 包含连字符
// let var;  // 使用保留字
```

### 2.1.3 代码风格与规范

良好的代码风格可以提高代码的可读性和可维护性：

**变量命名风格：**
- 使用驼峰命名法：`userName`, `firstName`, `getDate`
- 常量使用全大写字母和下划线：`MAX_LENGTH`, `PI`
- 私有变量使用下划线前缀：`_internalMethod`

**缩进与格式：**
```javascript
// 推荐：使用一致的缩进（2或4个空格）
function calculatePrice(quantity, unitPrice) {
    if (quantity > 10) {
        return quantity * unitPrice * 0.9; // 10%折扣
    } else {
        return quantity * unitPrice;
    }
}

// 不推荐：不一致的缩进
function calculatePrice(quantity, unitPrice) {
if (quantity > 10) {
 return quantity * unitPrice * 0.9;
} else {
        return quantity * unitPrice;
}
}
```

## 2.2 变量声明

JavaScript提供了三种变量声明方式：`var`、`let`和`const`。

### 2.2.1 var声明

`var`是JavaScript最早的变量声明方式，具有函数作用域和变量提升特性。

```javascript
// var声明的变量可以在声明前使用（变量提升）
console.log(myVar);  // undefined (不会报错)
var myVar = 10;
console.log(myVar);  // 10

// var具有函数作用域，不是块级作用域
function testVar() {
    if (true) {
        var x = 10;  // 在if块内声明
    }
    console.log(x);  // 10 (仍然可以访问)
}
testVar();

// 全局作用域中的var会创建全局对象属性
var globalVar = 'I am global';
console.log(window.globalVar);  // 'I am global'
```

### 2.2.2 let声明

`let`是ES6引入的新的变量声明方式，具有块级作用域，不允许重复声明。

```javascript
// let声明的变量不能在声明前使用（暂时性死区）
// console.log(myLet);  // ReferenceError: Cannot access 'myLet' before initialization
let myLet = 20;
console.log(myLet);  // 20

// let具有块级作用域
function testLet() {
    if (true) {
        let x = 10;  // 在if块内声明
    }
    // console.log(x);  // ReferenceError: x is not defined
}
testLet();

// let不允许重复声明
let a = 1;
// let a = 2;  // SyntaxError: Identifier 'a' has already been declared
```

### 2.2.3 const声明

`const`用于声明常量，具有块级作用域，声明后不能重新赋值。

```javascript
// const声明必须初始化
const PI = 3.14159;
console.log(PI);  // 3.14159

// const声明后不能重新赋值
// PI = 3.14;  // TypeError: Assignment to constant variable

// 对于对象和数组，const保护的是引用，不是内容
const user = { name: '张三', age: 25 };
user.age = 26;  // 允许修改对象属性
console.log(user);  // { name: '张三', age: 26 }

// 但是不能重新赋值整个对象
// user = { name: '李四', age: 30 };  // TypeError: Assignment to constant variable

// const具有块级作用域
if (true) {
    const blockVar = 'I am block scoped';
}
// console.log(blockVar);  // ReferenceError: blockVar is not defined
```

### 2.2.4 变量声明的最佳实践

1. **默认使用`const`**：如果变量不会被重新赋值，使用`const`声明
2. **需要重新赋值时使用`let`**：只有确定变量会被重新赋值时才使用`let`
3. **避免使用`var`**：在现代JavaScript中，`var`已经很少使用
4. **声明时即初始化**：避免声明变量而不初始化

```javascript
// 推荐的变量声明方式
const MAX_ATTEMPTS = 3;
let attempts = 0;
const users = [];
const config = {
    apiUrl: 'https://api.example.com',
    timeout: 5000
};

// 不推荐的变量声明方式
var maxAttempts;
var attempts;
var users = [];
var config;
config = {
    apiUrl: 'https://api.example.com',
    timeout: 5000
};
```

## 2.3 JavaScript数据类型

JavaScript是一种动态类型语言，变量可以保存任何类型的数据。JavaScript有7种基本数据类型和1种复杂数据类型。

### 2.3.1 基本数据类型

#### undefined类型

`undefined`表示变量已声明但未赋值：

```javascript
let uninitializedVar;
console.log(uninitializedVar);  // undefined
console.log(typeof uninitializedVar);  // undefined

// 函数没有返回值时默认返回undefined
function noReturn() {
    // 没有return语句
}
console.log(noReturn());  // undefined

// 对象不存在的属性
const obj = {};
console.log(obj.nonExistentProperty);  // undefined
```

#### null类型

`null`表示"无"或"空"值，是一个特殊的对象：

```javascript
let nullVar = null;
console.log(nullVar);  // null
console.log(typeof nullVar);  // object (这是一个历史遗留问题)

// null和undefined的区别
console.log(null == undefined);  // true (值相等)
console.log(null === undefined);  // false (类型不同)
```

#### boolean类型

`boolean`类型只有两个值：`true`和`false`：

```javascript
let isTrue = true;
let isFalse = false;

// 其他类型转换为boolean的规则
console.log(Boolean(0));        // false
console.log(Boolean(""));       // false
console.log(Boolean(null));     // false
console.log(Boolean(undefined)); // false
console.log(Boolean(NaN));      // false

console.log(Boolean(1));        // true
console.log.Boolean("hello"));  // true
console.log(Boolean({}));       // true
console.log(Boolean([]));       // true
```

#### number类型

`number`类型用于表示整数和浮点数：

```javascript
// 整数
let integer = 42;
let negativeInteger = -17;
let octalLiteral = 0o52;  // 42的八进制表示
let hexLiteral = 0x2A;    // 42的十六进制表示
let binaryLiteral = 0b101010;  // 42的二进制表示

// 浮点数
let float = 3.14;
let scientificNotation = 5.67e-3;  // 0.00567

// 特殊数值
console.log(Number.MAX_VALUE);    // 最大可表示数
console.log(Number.MIN_VALUE);    // 最小可表示数
console.log(Number.MAX_SAFE_INTEGER);  // 最大安全整数
console.log(Number.MIN_SAFE_INTEGER);  // 最小安全整数

console.log(Infinity);      // 正无穷
console.log(-Infinity);     // 负无穷
console.log(NaN);           // Not a Number

// NaN的特性
console.log(NaN === NaN);   // false
console.log(isNaN(NaN));    // true
console.log(Number.isNaN(NaN));  // true
console.log(Number.isFinite(42));  // true
console.log(Number.isFinite(Infinity));  // false
```

#### string类型

`string`类型用于表示文本数据：

```javascript
// 字符串字面量
let singleQuoteString = 'Hello, world!';
let doubleQuoteString = "Hello, world!";
let templateString = `Hello, world!`;

// 模板字符串（ES6）
let name = 'JavaScript';
let greeting = `Hello, ${name}!`;
console.log(greeting);  // Hello, JavaScript!

// 多行字符串
let multiLineString = `
这是第一行
这是第二行
这是第三行
`;
console.log(multiLineString);

// 字符串属性和方法
let text = 'Hello, JavaScript!';
console.log(text.length);  // 17

console.log(text.toUpperCase());  // 'HELLO, JAVASCRIPT!'
console.log(text.toLowerCase());  // 'hello, javascript!'

console.log(text.substring(0, 5));  // 'Hello'
console.log(text.slice(-10));       // 'JavaScript!'

console.log(text.split(', '));      // ['Hello', 'JavaScript!']
console.log(text.replace('JavaScript', 'World'));  // 'Hello, World!'

console.log(text.includes('Script'));  // true
console.log(text.startsWith('Hello'));  // true
console.log(text.endsWith('!'));        // true

// 字符串的不可变性
let str = 'hello';
str[0] = 'H';  // 不会改变字符串
console.log(str);  // 'hello'
str = str.toUpperCase();  // 创建新字符串
console.log(str);  // 'HELLO'
```

#### symbol类型

`symbol`是ES6引入的新类型，用于创建唯一的标识符：

```javascript
// 创建symbol
let symbol1 = Symbol();
let symbol2 = Symbol('description');
let symbol3 = Symbol('description');

console.log(typeof symbol1);  // symbol

// symbol是唯一的
console.log(symbol2 === symbol3);  // false

// symbol作为对象属性
let idSymbol = Symbol('id');
let user = {
    name: '张三',
    [idSymbol]: 12345  // 使用symbol作为属性键
};

console.log(user[idSymbol]);  // 12345
console.log(user['id']);      // undefined (无法用字符串访问symbol属性)

// 获取对象的symbol属性
console.log(Object.getOwnPropertySymbols(user));  // [Symbol(id)]
```

#### bigint类型

`bigint`是ES10引入的类型，用于表示任意精度的整数：

```javascript
// 创建bigint
let bigIntLiteral = 9007199254740991n;  // n后缀表示bigint
let bigIntFromNumber = BigInt(9007199254740991);
let bigIntFromString = BigInt('9007199254740991');

// bigInt运算
let bigInt1 = 123456789012345678901234567890n;
let bigInt2 = 987654321098765432109876543210n;

console.log(bigInt1 + bigInt2);
console.log(bigInt1 * bigInt2);

// bigInt与number的区别
console.log(Number.MAX_SAFE_INTEGER);  // 9007199254740991
console.log(Number.MAX_SAFE_INTEGER + 1);  // 9007199254740992
console.log(Number.MAX_SAFE_INTEGER + 2);  // 9007199254740992 (精度丢失)

console.log(9007199254740991n + 1n);  // 9007199254740992n
console.log(9007199254740991n + 2n);  // 9007199254740993n (无精度丢失)

// bigInt不能与number混合运算
// let mixed = 123n + 456;  // TypeError
let mixed = 123n + BigInt(456);  // 正确
```

### 2.3.2 复杂数据类型

#### object类型

`object`是JavaScript中唯一的复杂数据类型，用于存储键值对集合：

```javascript
// 对象字面量
let person = {
    name: '张三',
    age: 25,
    city: '北京',
    // 方法
    greet: function() {
        return '你好，我是' + this.name;
    },
    // ES6简写方法
    getInfo() {
        return `${this.name}，${this.age}岁，来自${this.city}`;
    }
};

// 访问属性
console.log(person.name);        // 点表示法
console.log(person['age']);      // 括号表示法

// 调用方法
console.log(person.greet());
console.log(person.getInfo());

// 添加新属性
person.email = 'zhangsan@example.com';

// 删除属性
delete person.email;

// 检查属性是否存在
console.log('name' in person);              // true
console.log('email' in person);             // false
console.log(person.hasOwnProperty('name'));  // true

// 获取所有属性
console.log(Object.keys(person));    // ['name', 'age', 'city', 'greet', 'getInfo']
console.log(Object.values(person));  // 属性值数组
console.log(Object.entries(person)); // 键值对数组
```

#### 数组（特殊的对象）

数组是特殊的对象，用于存储有序的数据集合：

```javascript
// 创建数组
let emptyArray = [];
let fruits = ['苹果', '香蕉', '橙子'];
let mixedArray = [1, 'hello', true, null, undefined, {name: '对象'}, [1, 2, 3]];

// 数组长度
console.log(fruits.length);  // 3

// 访问元素（从0开始索引）
console.log(fruits[0]);  // '苹果'
console.log(fruits[1]);  // '香蕉'

// 修改元素
fruits[1] = '葡萄';
console.log(fruits);  // ['苹果', '葡萄', '橙子']

// 添加元素
fruits.push('芒果');        // 添加到末尾
fruits.unshift('草莓');      // 添加到开头

// 删除元素
let lastFruit = fruits.pop();    // 删除并返回最后一个元素
let firstFruit = fruits.shift(); // 删除并返回第一个元素

// 数组方法
console.log(fruits.join(', '));  // 用逗号连接数组元素
console.log(fruits.slice(1, 3)); // 返回索引1到3（不包括3）的元素
console.log(fruits.indexOf('橙子')); // 返回元素索引

// 数组迭代
fruits.forEach(function(fruit, index) {
    console.log(`${index}: ${fruit}`);
});

let upperFruits = fruits.map(fruit => fruit.toUpperCase());
console.log(upperFruits);

let filteredFruits = fruits.filter(fruit => fruit.includes('果'));
console.log(filteredFruits);
```

#### 函数（特殊的对象）

函数是可执行的对象，可以作为值传递和存储：

```javascript
// 函数声明
function add(a, b) {
    return a + b;
}

// 函数表达式
const multiply = function(a, b) {
    return a * b;
};

// 箭头函数
const subtract = (a, b) => a - b;

// 函数作为值
const operations = {
    add: add,
    multiply: multiply,
    subtract: subtract,
    // 对象方法
    calculate(a, b, operation) {
        return this[operation](a, b);
    }
};

console.log(operations.calculate(5, 3, 'add'));      // 8
console.log(operations.calculate(5, 3, 'multiply')); // 15
console.log(operations.calculate(5, 3, 'subtract')); // 2

// 函数作为参数
function calculate(a, b, operation) {
    return operation(a, b);
}

console.log(calculate(10, 5, add));        // 15
console.log(calculate(10, 5, multiply));   // 50
console.log(calculate(10, 5, subtract));    // 5
```

## 2.4 类型转换

JavaScript是一种动态类型语言，会在运行时自动进行类型转换。

### 2.4.1 隐式类型转换

JavaScript会在某些操作中自动进行类型转换：

```javascript
// 字符串连接
console.log('Hello' + ' ' + 'World');  // 'Hello World'
console.log('Hello' + 5);              // 'Hello5'
console.log('5' + 5);                  // '55'

// 算术运算
console.log('5' * 2);      // 10
console.log('5' - 2);      // 3
console.log('5' / 2);      // 2.5
console.log('5' % 2);      // 1

// 比较运算
console.log('5' == 5);     // true (值相等)
console.log('5' === 5);    // false (类型不同)
console.log('5' != 5);     // false
console.log('5' !== 5);    // true

// 逻辑运算
console.log('hello' && 0);     // 0
console.log('hello' && 5);     // 5
console.log('hello' || 0);     // 'hello'
console.log('hello' || 5);     // 'hello'
console.log(0 && 'hello');     // 0
console.log(0 || 'hello');     // 'hello'

// 条件语句中的类型转换
if ('') {
    console.log('空字符串为真');
} else {
    console.log('空字符串为假');
}

if (0) {
    console.log('0为真');
} else {
    console.log('0为假');
}
```

### 2.4.2 显式类型转换

可以使用内置函数进行显式类型转换：

```javascript
// 转换为字符串
let num = 42;
let str1 = String(num);     // '42'
let str2 = num.toString();  // '42'
let str3 = num + '';        // '42'

// 转换为数字
let str = '123';
let num1 = Number(str);    // 123
let num2 = parseInt(str);   // 123
let num3 = parseFloat(str); // 123

console.log(Number(''));        // 0
console.log(Number(' '));       // 0
console.log(Number('123abc'));  // NaN
console.log(parseInt('123abc')); // 123
console.log(parseFloat('123.45abc')); // 123.45

// 转换为布尔值
console.log(Boolean(0));        // false
console.log(Boolean(''));       // false
console.log(Boolean(null));     // false
console.log(Boolean(undefined)); // false
console.log(Boolean(NaN));      // false

console.log(Boolean(1));        // true
console.log(Boolean('hello'));  // true
console.log(Boolean({}));       // true
console.log(Boolean([]));       // true

// 一元运算符进行类型转换
console.log(+'123');    // 123
console.log(+true);     // 1
console.log(+false);    // 0
console.log(+'hello');  // NaN
```

## 2.5 运算符

JavaScript提供了多种运算符用于执行各种操作。

### 2.5.1 算术运算符

```javascript
// 基本算术运算
let a = 10, b = 3;

console.log(a + b);    // 13 (加法)
console.log(a - b);    // 7  (减法)
console.log(a * b);    // 30 (乘法)
console.log(a / b);    // 3.333... (除法)
console.log(a % b);    // 1  (取余)
console.log(a ** b);   // 1000 (幂运算)

// 自增和自减
let x = 5;
console.log(x++);  // 5 (先返回，后自增)
console.log(x);    // 6

console.log(++x);  // 7 (先自增，后返回)
console.log(x);    // 7

console.log(x--);  // 7 (先返回，后自减)
console.log(x);    // 6

console.log(--x);  // 5 (先自减，后返回)
console.log(x);    // 5
```

### 2.5.2 赋值运算符

```javascript
let x = 10;

// 基本赋值
x = 5;
console.log(x);  // 5

// 算术赋值
x += 3;  // 等同于 x = x + 3
console.log(x);  // 8

x -= 2;  // 等同于 x = x - 2
console.log(x);  // 6

x *= 2;  // 等同于 x = x * 2
console.log(x);  // 12

x /= 3;  // 等同于 x = x / 3
console.log(x);  // 4

x %= 2;  // 等同于 x = x % 2
console.log(x);  // 0

x **= 3;  // 等同于 x = x ** 3
console.log(x);  // 0
```

### 2.5.3 比较运算符

```javascript
let a = 5, b = '5';

// 相等比较
console.log(a == b);   // true  (值相等，进行类型转换)
console.log(a === b);  // false (值和类型都相等)

console.log(a != b);   // false (值不相等，进行类型转换)
console.log(a !== b);  // true  (值或类型不相等)

// 大小比较
console.log(5 > 3);    // true
console.log(5 >= 3);   // true
console.log(5 < 3);    // false
console.log(5 <= 3);   // false

// 比较的注意事项
console.log('10' > '2');   // false (字符串按字典序比较)
console.log(10 > '2');      // true (数字比较)
console.log('a' > 'A');     // true (Unicode码比较)
console.log('a'.charCodeAt(0));  // 97
console.log('A'.charCodeAt(0));  // 65
```

### 2.5.4 逻辑运算符

```javascript
// 逻辑与 (&&)
console.log(true && true);    // true
console.log(true && false);   // false
console.log(false && true);   // false
console.log(false && false);  // false

// 短路特性
console.log(true && console.log('执行'));  // 执行
console.log(false && console.log('不执行')); // 不执行

// 逻辑或 (||)
console.log(true || true);    // true
console.log(true || false);   // true
console.log(false || true);   // true
console.log(false || false);  // false

// 短路特性
console.log(true || console.log('不执行')); // 不执行
console.log(false || console.log('执行'));  // 执行

// 逻辑非 (!)
console.log(!true);   // false
console.log(!false);  // true
console.log(!0);      // true
console.log(!'');     // true
console.log(!'hello'); // false

// 实际应用示例
// 设置默认值
function greet(name) {
    // 如果name为假值，使用默认值'Guest'
    name = name || 'Guest';
    console.log('Hello, ' + name);
}

greet('Alice');  // Hello, Alice
greet();         // Hello, Guest

// 安全访问对象属性
const user = {
    name: '张三'
    // 没有 age 属性
};

const age = user.age || 25;  // 如果 user.age 不存在或为假值，使用 25
console.log(age);  // 25
```

### 2.5.5 位运算符

```javascript
// 按位与 (&)
console.log(5 & 3);  // 1
// 5 = 0101
// 3 = 0011
// ----------
//     0001 = 1

// 按位或 (|)
console.log(5 | 3);  // 7
// 5 = 0101
// 3 = 0011
// ----------
//     0111 = 7

// 按位异或 (^)
console.log(5 ^ 3);  // 6
// 5 = 0101
// 3 = 0011
// ----------
//     0110 = 6

// 按位非 (~)
console.log(~5);  // -6
// 5 = 0000000000000101
// ~5 = 1111111111111010 = -6 (二进制补码)

// 左移 (<<)
console.log(5 << 1);  // 10 (5 * 2^1)

// 右移 (>>)
console.log(5 >> 1);  // 2 (整数除法，向下取整)

// 无符号右移 (>>>)
console.log(-5 >>> 1);  // 2147483645

// 实际应用：快速判断奇偶数
function isEven(num) {
    return (num & 1) === 0;  // 如果最后一位是0，则为偶数
}

console.log(isEven(4));  // true
console.log(isEven(5));  // false

// 实际应用：权限管理
const READ_PERMISSION = 1;    // 001
const WRITE_PERMISSION = 2;   // 010
const EXECUTE_PERMISSION = 4; // 100

let userPermissions = READ_PERMISSION | WRITE_PERMISSION; // 011 = 3

console.log(userPermissions & READ_PERMISSION);    // 1 (有读权限)
console.log(userPermissions & WRITE_PERMISSION);   // 2 (有写权限)
console.log(userPermissions & EXECUTE_PERMISSION); // 0 (无执行权限)
```

### 2.5.6 条件（三元）运算符

```javascript
// 基本语法: condition ? value_if_true : value_if_false
let age = 18;
let message = age >= 18 ? '成年人' : '未成年人';
console.log(message);  // 成年人

// 链式三元运算
let score = 85;
let grade = score >= 90 ? 'A' : 
            score >= 80 ? 'B' : 
            score >= 70 ? 'C' : 
            score >= 60 ? 'D' : 'F';
console.log(grade);  // B

// 作为函数返回值
function getGreeting(hour) {
    return hour < 12 ? '早上好' : 
           hour < 18 ? '下午好' : '晚上好';
}

console.log(getGreeting(9));   // 早上好
console.log(getGreeting(14));  // 下午好
console.log(getGreeting(20));  // 晚上好
```

## 2.6 条件语句

### 2.6.1 if语句

```javascript
// 基本if语句
let score = 85;

if (score >= 60) {
    console.log('及格了！');
}

// if-else语句
if (score >= 60) {
    console.log('及格了！');
} else {
    console.log('不及格！');
}

// if-else if-else语句
if (score >= 90) {
    console.log('优秀');
} else if (score >= 80) {
    console.log('良好');
} else if (score >= 70) {
    console.log('中等');
} else if (score >= 60) {
    console.log('及格');
} else {
    console.log('不及格');
}

// 嵌套if语句
let age = 20;
let hasLicense = true;

if (age >= 18) {
    if (hasLicense) {
        console.log('可以开车');
    } else {
        console.log('需要先考取驾照');
    }
} else {
    console.log('年龄不够');
}
```

### 2.6.2 switch语句

```javascript
// 基本switch语句
let dayOfWeek = 3;
let dayName;

switch (dayOfWeek) {
    case 0:
        dayName = '星期日';
        break;
    case 1:
        dayName = '星期一';
        break;
    case 2:
        dayName = '星期二';
        break;
    case 3:
        dayName = '星期三';
        break;
    case 4:
        dayName = '星期四';
        break;
    case 5:
        dayName = '星期五';
        break;
    case 6:
        dayName = '星期六';
        break;
    default:
        dayName = '未知';
        break;
}

console.log(dayName);  // 星期三

// 多个case使用相同代码
let grade = 'B';

switch (grade) {
    case 'A':
    case 'B':
        console.log('优秀');
        break;
    case 'C':
    case 'D':
        console.log('及格');
        break;
    case 'F':
        console.log('不及格');
        break;
    default:
        console.log('未知成绩');
}

// 使用表达式
let age = 25;
switch (true) {
    case age < 18:
        console.log('未成年');
        break;
    case age >= 18 && age < 60:
        console.log('成年');
        break;
    case age >= 60:
        console.log('老年');
        break;
    default:
        console.log('无效年龄');
}
```

## 2.7 循环语句

### 2.7.1 for循环

```javascript
// 基本for循环
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// 计算1到100的和
let sum = 0;
for (let i = 1; i <= 100; i++) {
    sum += i;
}
console.log('1到100的和:', sum);  // 5050

// 遍历数组
let fruits = ['苹果', '香蕉', '橙子'];
for (let i = 0; i < fruits.length; i++) {
    console.log(`水果${i + 1}: ${fruits[i]}`);
}

// 省略表达式
let i = 0;
for (; i < 3; i++) {
    console.log(i);  // 0, 1, 2
}

// 无限循环（不推荐）
// for (;;) {
//     console.log('这是一个无限循环');
// }
```

### 2.7.2 while循环

```javascript
// 基本while循环
let count = 0;
while (count < 5) {
    console.log(count);
    count++;
}

// 计算阶乘
function factorial(n) {
    let result = 1;
    let i = n;
    
    while (i > 0) {
        result *= i;
        i--;
    }
    
    return result;
}

console.log('5的阶乘:', factorial(5));  // 120

// 输入验证
let userInput;
while (!userInput || userInput.trim() === '') {
    userInput = prompt('请输入您的姓名:');
}

console.log('您好, ' + userInput);
```

### 2.7.3 do-while循环

```javascript
// 基本do-while循环
let i = 0;
do {
    console.log(i);
    i++;
} while (i < 3);

// 至少执行一次
let isValidInput = false;
let input;

do {
    input = prompt('请输入一个有效的数字:');
    isValidInput = !isNaN(input) && input.trim() !== '';
} while (!isValidInput);

console.log('您输入的数字是:', input);
```

### 2.7.4 for-in和for-of循环

```javascript
// for-in循环 - 遍历对象属性
let person = {
    name: '张三',
    age: 30,
    city: '北京'
};

console.log('使用for-in遍历对象:');
for (let key in person) {
    console.log(`${key}: ${person[key]}`);
}

// for-in循环 - 遍历数组索引
let colors = ['红色', '绿色', '蓝色'];

console.log('使用for-in遍历数组索引:');
for (let index in colors) {
    console.log(`索引${index}: ${colors[index]}`);
}

// for-of循环 - 遍历数组值
console.log('使用for-of遍历数组值:');
for (let color of colors) {
    console.log(color);
}

// for-of循环 - 遍历字符串
for (let char of 'JavaScript') {
    console.log(char);
}

// for-of循环 - 遍历Map和Set
let mySet = new Set([1, 2, 3, 4]);
console.log('遍历Set:');
for (let value of mySet) {
    console.log(value);
}

let myMap = new Map([
    ['name', '李四'],
    ['age', 25]
]);

console.log('遍历Map:');
for (let [key, value] of myMap) {
    console.log(`${key}: ${value}`);
}
```

### 2.7.5 break和continue

```javascript
// break - 跳出循环
for (let i = 0; i < 10; i++) {
    if (i === 5) {
        break;  // 当i等于5时，跳出循环
    }
    console.log(i);  // 输出0,1,2,3,4
}

// continue - 跳过当前迭代
for (let i = 0; i < 10; i++) {
    if (i % 2 === 0) {
        continue;  // 跳过偶数
    }
    console.log(i);  // 输出1,3,5,7,9
}

// 标记循环 - 用于嵌套循环
outerLoop: for (let i = 0; i < 3; i++) {
    innerLoop: for (let j = 0; j < 3; j++) {
        console.log(`i=${i}, j=${j}`);
        
        if (i === 1 && j === 1) {
            break outerLoop;  // 跳出外层循环
        }
    }
}
```

## 2.8 异常处理

### 2.8.1 try-catch语句

```javascript
// 基本try-catch
try {
    // 可能出错的代码
    let result = 10 / 0;  // Infinity，不会出错
    console.log(result);
    
    // 下面这行会出错
    console.log(undefinedVariable);
} catch (error) {
    // 处理错误
    console.error('发生错误:', error.message);
}

// 使用finally
try {
    console.log('尝试执行操作');
    // 模拟一个可能失败的操作
    let success = Math.random() > 0.5;
    if (!success) {
        throw new Error('操作失败');
    }
    console.log('操作成功');
} catch (error) {
    console.error('捕获到错误:', error.message);
} finally {
    console.log('无论成功或失败，都会执行finally块');
}
```

### 2.8.2 throw语句

```javascript
// 抛出自定义错误
function validateAge(age) {
    if (typeof age !== 'number') {
        throw new TypeError('年龄必须是数字');
    }
    
    if (age < 0) {
        throw new RangeError('年龄不能为负数');
    }
    
    if (age > 150) {
        throw new RangeError('年龄看起来不合理');
    }
    
    return true;
}

// 测试年龄验证
function testAgeValidation(age) {
    try {
        validateAge(age);
        console.log(`${age} 是一个有效的年龄`);
    } catch (error) {
        console.error(`验证年龄 ${age} 时出错:`, error.message);
    }
}

testAgeValidation(25);   // 有效
testAgeValidation(-5);   // RangeError
testAgeValidation('abc'); // TypeError
testAgeValidation(200);  // RangeError

// 抛出不同类型的错误
function processData(data) {
    if (data === null || data === undefined) {
        throw new Error('数据不能为空');
    }
    
    if (typeof data !== 'object') {
        throw new TypeError('数据必须是对象');
    }
    
    if (!data.id) {
        throw new Error('数据缺少必需的id字段');
    }
    
    console.log('数据处理成功');
}

try {
    processData({ name: '测试数据' });
} catch (error) {
    console.error('数据处理出错:', error.message);
}
```

## 2.9 最佳实践

### 2.9.1 变量命名最佳实践

```javascript
// 好的变量命名
let userName = '张三';
let isLoggedIn = true;
let maxRetryCount = 3;
let userData = { name: '李四', age: 25 };
let calculateTotalPrice = function() { /* ... */ };

// 使用描述性常量
const API_BASE_URL = 'https://api.example.com';
const MAX_FILE_SIZE = 5 * 1024 * 1024;  // 5MB
const DEFAULT_TIMEOUT = 3000;  // 3秒

// 不好的变量命名
let n = '张三';
let b = true;
let mrc = 3;
let d = { name: '李四', age: 25 };
let ct = function() { /* ... */ };
```

### 2.9.2 类型检查最佳实践

```javascript
// 使用typeof检查基本类型
function processValue(value) {
    if (typeof value === 'string') {
        console.log('处理字符串:', value.toUpperCase());
    } else if (typeof value === 'number') {
        console.log('处理数字:', value * 2);
    } else if (typeof value === 'boolean') {
        console.log('处理布尔值:', !value);
    } else {
        console.log('未知类型');
    }
}

// 使用Array.isArray检查数组
function processArray(data) {
    if (Array.isArray(data)) {
        data.forEach(item => console.log(item));
    } else {
        console.log('参数不是数组');
    }
}

// 使用instanceof检查对象类型
function processObject(obj) {
    if (obj instanceof Date) {
        console.log('日期对象:', obj.toLocaleDateString());
    } else if (obj instanceof RegExp) {
        console.log('正则表达式对象:', obj);
    } else {
        console.log('普通对象:', obj);
    }
}

// 检查null
function checkNull(value) {
    if (value === null) {
        console.log('值为null');
    } else {
        console.log('值不为null');
    }
}

// 检查undefined
function checkUndefined(value) {
    if (value === undefined) {
        console.log('值为undefined');
    } else {
        console.log('值不为undefined');
    }
}

// 检查空值（null或undefined）
function checkNullish(value) {
    if (value == null) {  // 使用 == 同时检查null和undefined
        console.log('值为null或undefined');
    } else {
        console.log('值不为null或undefined');
    }
}
```

### 2.9.3 条件判断最佳实践

```javascript
// 使用有意义的变量名
let hasAdminPermission = true;
let isUserLoggedIn = false;

// 清晰的条件判断
if (hasAdminPermission && isUserLoggedIn) {
    console.log('管理员已登录，可以访问管理功能');
}

// 使用常量代替魔法数字
const MAX_LOGIN_ATTEMPTS = 3;
let loginAttempts = 2;

if (loginAttempts >= MAX_LOGIN_ATTEMPTS) {
    console.log('登录尝试次数过多，账户被锁定');
}

// 使用早期返回模式
function authenticateUser(username, password) {
    // 输入验证
    if (!username || !password) {
        return { success: false, message: '用户名和密码不能为空' };
    }
    
    if (username.length < 3) {
        return { success: false, message: '用户名太短' };
    }
    
    if (password.length < 6) {
        return { success: false, message: '密码太短' };
    }
    
    // 主要逻辑
    // ... 验证用户凭据
    
    return { success: true, message: '认证成功' };
}
```

### 2.9.4 循环优化最佳实践

```javascript
// 缓存数组长度
let items = /* 大数组 */;
for (let i = 0, len = items.length; i < len; i++) {
    // 处理items[i]
}

// 使用for...of遍历数组
let numbers = [1, 2, 3, 4, 5];
for (let number of numbers) {
    console.log(number);
}

// 避免在循环中创建函数
// 不推荐
// for (let i = 0; i < buttons.length; i++) {
//     buttons[i].onclick = function() {
//         console.log('按钮' + i + '被点击');
//     };
// }

// 推荐
for (let i = 0; i < buttons.length; i++) {
    (function(index) {
        buttons[index].onclick = function() {
            console.log('按钮' + index + '被点击');
        };
    })(i);
}
```

## 2.10 总结

本章详细介绍了JavaScript的语法和数据类型，包括：

1. JavaScript基础语法：语句、表达式、标识符和代码风格
2. 变量声明：var、let和const的区别及使用场景
3. JavaScript数据类型：7种基本类型和1种复杂类型
4. 类型转换：隐式转换和显式转换
5. 运算符：算术、赋值、比较、逻辑、位运算和条件运算符
6. 条件语句：if语句和switch语句
7. 循环语句：for、while、do-while、for-in和for-of
8. 异常处理：try-catch-finally和throw
9. 最佳实践：变量命名、类型检查、条件判断和循环优化

掌握这些基础知识是成为JavaScript专家的第一步。在下一章中，我们将深入学习JavaScript的函数与作用域。

## 2.11 练习

1. 创建一个程序，根据用户输入的年龄显示不同的问候语（儿童、青少年、成年人、老年人）。
2. 编写一个函数，计算一个数字数组的平均值、最大值和最小值。
3. 实现一个简单的计算器，支持加、减、乘、除运算。
4. 编写一个程序，判断一个年份是否是闰年。
5. 创建一个函数，接受一个字符串，返回该字符串中每个字符出现的次数。

## 2.12 参考资料

- [MDN JavaScript指南](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Guide)
- [JavaScript.info](https://javascript.info/)
- [You Don't Know JS Yet (book series)](https://github.com/getify/You-Dont-Know-JS)
- [JavaScript数据类型与类型转换](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Data_structures)