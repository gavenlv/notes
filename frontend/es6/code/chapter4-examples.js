// 第4章：解构赋值与扩展运算符 - 代码示例

// ===== 4.1 数组解构 =====

// 基本数组解构
console.log('===== 基本数组解构 =====');
const [x, y, z] = [1, 2, 3];
console.log(x); // 1
console.log(y); // 2
console.log(z); // 3

// 数组解构的高级用法
console.log('\n===== 数组解构的高级用法 =====');

// 跳过某些元素
const [first, , third] = [1, 2, 3, 4];
console.log(first); // 1
console.log(third); // 3

// 使用剩余元素
const [head, ...tail] = [1, 2, 3, 4, 5];
console.log(head); // 1
console.log(tail); // [2, 3, 4, 5]

// 设置默认值
const [a = 10, b = 20] = [1];
console.log(a); // 1
console.log(b); // 20 (使用默认值)

// 交换变量
let m = 5, n = 10;
[m, n] = [n, m];
console.log(m); // 10
console.log(n); // 5

// 嵌套数组解构
const [p, [q, r], s] = [1, [2, 3], 4];
console.log(p); // 1
console.log(q); // 2
console.log(r); // 3
console.log(s); // 4

// 函数返回值解构
console.log('\n===== 函数返回值解构 =====');
function getCoordinates() {
  return [10, 20];
}

const [xCoord, yCoord] = getCoordinates();
console.log(xCoord); // 10
console.log(yCoord); // 20

// ===== 4.2 对象解构 =====

// 基本对象解构
console.log('\n===== 基本对象解构 =====');
const person = {
  name: 'Alice',
  age: 30,
  city: 'New York'
};

const { name, age } = person;
console.log(name); // 'Alice'
console.log(age); // 30

// 对象解构的高级用法
console.log('\n===== 对象解构的高级用法 =====');

// 重命名变量
const user = {
  name: 'Bob',
  age: 25
};
const { name: userName, age: userAge } = user;
console.log(userName); // 'Bob'
console.log(userAge); // 25

// 设置默认值
const settings = {
  theme: 'dark'
};
const { theme, language = 'en' } = settings;
console.log(theme); // 'dark'
console.log(language); // 'en' (使用默认值)

// 嵌套对象解构
const employee = {
  id: 123,
  personal: {
    name: 'Charlie',
    contact: {
      email: 'charlie@example.com',
      phone: '123-456-7890'
    }
  }
};
const { 
  personal: { 
    name: empName, 
    contact: { email } 
  } 
} = employee;
console.log(empName); // 'Charlie'
console.log(email); // 'charlie@example.com'

// 解构不存在的属性
const { nonExistent = 'default value' } = {};
console.log(nonExistent); // 'default value'

// 结合剩余运算符
const { a, b, ...rest } = { a: 1, b: 2, c: 3, d: 4 };
console.log(a); // 1
console.log(b); // 2
console.log(rest); // { c: 3, d: 4 }

// 函数参数解构
console.log('\n===== 函数参数解构 =====');
function displayPersonDestructured({ name, age }) {
  console.log(`Name: ${name}, Age: ${age}`);
}

displayPersonDestructured({ name: 'David', age: 40 });

// 带默认值的解构参数
function createUser({ name = 'Anonymous', age = 0, isActive = true } = {}) {
  console.log(`Created user: ${name}, Age: ${age}, Active: ${isActive}`);
}

createUser(); // 使用所有默认值
createUser({ name: 'Eve' }); // 只覆盖name
createUser({ name: 'Frank', age: 35, isActive: false }); // 覆盖所有值

// ===== 4.3 解构的默认值 =====

// 数组解构的默认值
console.log('\n===== 数组解构的默认值 =====');

// 基本默认值
const [a1 = 1, b1 = 2, c1 = 3] = [10, 20];
console.log(a1); // 10
console.log(b1); // 20
console.log(c1); // 3 (使用默认值)

// 表达式作为默认值
function getDefaultX() {
  console.log('getDefaultX called');
  return 10;
}
function getDefaultY() {
  console.log('getDefaultY called');
  return 20;
}

const [x1 = getDefaultX(), y1 = getDefaultY()] = [5];
console.log(x1); // 5
console.log(y1); // 20 (getDefaultY被调用)

// 引用前面定义的变量作为默认值
const [first1, second1 = first1 * 2] = [5];
console.log(first1); // 5
console.log(second1); // 10

// 对象解构的默认值
console.log('\n===== 对象解构的默认值 =====');

// 基本默认值
const { a2 = 10, b2 = 20 } = { a: 5 };
console.log(a2); // 5
console.log(b2); // 20 (使用默认值)

// 重命名并设置默认值
const { x: newX = 100, y: newY = 200 } = { x: 50 };
console.log(newX); // 50
console.log(newY); // 200 (使用默认值)

// 嵌套对象中的默认值
const user1 = {
  name: 'Grace',
  details: {
    age: 28
  }
};
const { 
  name, 
  details: { 
    age, 
    city = 'Unknown' 
  } 
} = user1;
console.log(name); // 'Grace'
console.log(age); // 28
console.log(city); // 'Unknown' (使用默认值)

// 函数作为默认值
function getDefaultEmail() {
  return 'default@example.com';
}
const { email = getDefaultEmail() } = {};
console.log(email); // 'default@example.com'

// ===== 4.4 扩展运算符的应用 =====

// 数组扩展运算符
console.log('\n===== 数组扩展运算符 =====');

// 函数调用中的扩展运算符
function add(a, b, c) {
  return a + b + c;
}
const numbers = [1, 2, 3];
console.log(add(...numbers)); // 6

// 数组合并
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2];
console.log(combined); // [1, 2, 3, 4, 5, 6]

// 在数组中间插入元素
const parts = ['shoulders', 'knees'];
const body = ['head', ...parts, 'and', 'toes'];
console.log(body); // ['head', 'shoulders', 'knees', 'and', 'toes']

// 数组复制
const original = [1, 2, 3];
const copy = [...original];
console.log(copy); // [1, 2, 3]
console.log(original === copy); // false (不同的数组对象)

// 字符串转换为字符数组
const str = 'hello';
const chars = [...str];
console.log(chars); // ['h', 'e', 'l', 'l', 'o']

// 对象扩展运算符
console.log('\n===== 对象扩展运算符 =====');

// 对象合并
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const merged = { ...obj1, ...obj2 };
console.log(merged); // { a: 1, b: 2, c: 3, d: 4 }

// 对象复制
const originalObj = { x: 10, y: 20 };
const copyObj = { ...originalObj };
console.log(copyObj); // { x: 10, y: 20 }
console.log(originalObj === copyObj); // false (不同的对象)

// 覆盖属性
const base = { a: 1, b: 2, c: 3 };
const override = { ...base, b: 20, c: 30 };
console.log(override); // { a: 1, b: 20, c: 30 }

// 添加新属性
const extended = { ...base, d: 4, e: 5 };
console.log(extended); // { a: 1, b: 2, c: 3, d: 4, e: 5 }

// 结合解构和扩展运算符
const { a3, ...rest1 } = { a: 1, b: 2, c: 3, d: 4 };
console.log(a3); // 1
console.log(rest1); // { b: 2, c: 3, d: 4 }

// 函数参数中的扩展运算符
console.log('\n===== 函数参数中的扩展运算符 =====');

// 函数定义中的剩余参数
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}
console.log(sum(1, 2, 3, 4, 5)); // 15

// 与普通参数结合
function greet(greeting, ...names) {
  names.forEach(name => {
    console.log(`${greeting}, ${name}!`);
  });
}
greet('Hello', 'Alice', 'Bob', 'Charlie');

// 函数调用中的扩展运算符
const numbersArray = [1, 2, 3, 4, 5];
console.log(Math.max(...numbersArray)); // 5
console.log(Math.min(...numbersArray)); // 1

// 结合使用
function multiplyAndSum(multiplier, ...numbers) {
  const multiplied = numbers.map(num => num * multiplier);
  return multiplied.reduce((sum, num) => sum + num, 0);
}
console.log(multiplyAndSum(2, 1, 2, 3)); // (1*2 + 2*2 + 3*2) = 12

// ===== 4.5 实际应用场景 =====

// 数据处理和转换
console.log('\n===== 数据处理和转换 =====');

// 提取API响应中的有用数据
const apiResponse = {
  data: {
    users: [
      { id: 1, name: 'Alice', age: 30, city: 'New York' },
      { id: 2, name: 'Bob', age: 25, city: 'Los Angeles' },
      { id: 3, name: 'Charlie', age: 35, city: 'Chicago' }
    ],
    pagination: {
      page: 1,
      limit: 10,
      total: 3
    }
  },
  status: 'success'
};

// 提取用户数据和分页信息
const { 
  data: { 
    users, 
    pagination: { page, limit, total } 
  } 
} = apiResponse;

console.log('Users:', users); // 用户数组
console.log('Pagination:', { page, limit, total }); // 1, 10, 3

// 转换数据格式
const formattedUsers = users.map(({ id, name, age }) => ({
  userId: id,
  fullName: name,
  yearsOld: age
}));
console.log('Formatted users:', formattedUsers);

// 配置对象处理
console.log('\n===== 配置对象处理 =====');

// 默认配置
const defaultConfig = {
  theme: 'light',
  language: 'en',
  fontSize: 16,
  showNotifications: true,
  autoSave: false
};

// 用户配置
const userConfig = {
  theme: 'dark',
  fontSize: 18,
  autoSave: true
};

// 合并配置
const finalConfig = { ...defaultConfig, ...userConfig };
console.log('Final config:', finalConfig);

// 函数中使用配置
function initializeApp(config = {}) {
  const {
    theme = 'light',
    language = 'en',
    fontSize = 16,
    showNotifications = true,
    autoSave = false
  } = config;
  
  console.log(`Initializing app with theme: ${theme}, language: ${language}`);
  // 应用初始化逻辑...
}

initializeApp(finalConfig);

// 数组操作
console.log('\n===== 数组操作 =====');

// 数组去重
const numbers2 = [1, 2, 3, 2, 4, 5, 1, 6];
const uniqueNumbers = [...new Set(numbers2)];
console.log('Unique numbers:', uniqueNumbers); // [1, 2, 3, 4, 5, 6]

// 数组排序
const users2 = [
  { name: 'Alice', age: 30 },
  { name: 'Bob', age: 25 },
  { name: 'Charlie', age: 35 }
];

// 按年龄排序
const sortedByAge = [...users2].sort((a, b) => a.age - b.age);
console.log('Sorted by age:', sortedByAge);

// 按名称排序
const sortedByName = [...users2].sort((a, b) => a.name.localeCompare(b.name));
console.log('Sorted by name:', sortedByName);

// 数组分块
function chunk(array, size) {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

const numbers3 = [1, 2, 3, 4, 5, 6, 7, 8, 9];
const chunked = chunk(numbers3, 3);
console.log('Chunked array:', chunked); // [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

// ===== 4.6 练习解答 =====

// 练习1：数组解构
console.log('\n===== 练习1解答：数组解构 =====');
const colors = ['red', 'green', 'blue', 'yellow', 'purple'];

// 1. 提取第一个和第三个颜色
const [primaryColor, , secondaryColor] = colors;
console.log('Primary and secondary colors:', primaryColor, secondaryColor);

// 2. 提取第一个颜色，并将剩余颜色放入一个新数组
const [firstColor, ...remainingColors] = colors;
console.log('First color:', firstColor);
console.log('Remaining colors:', remainingColors);

// 3. 提取第二个颜色，并为第四个颜色设置默认值'orange'
const [, secondColor, , fourthColor = 'orange'] = colors;
console.log('Second color:', secondColor);
console.log('Fourth color:', fourthColor);

// 练习2：对象解构
console.log('\n===== 练习2解答：对象解构 =====');
const product = {
  id: 'p123',
  name: 'Wireless Headphones',
  price: 99.99,
  category: 'Electronics',
  specs: {
    color: 'Black',
    weight: '250g',
    battery: '20 hours'
  },
  reviews: [
    { rating: 5, comment: 'Excellent!' },
    { rating: 4, comment: 'Good value' }
  ]
};

// 1. 提取产品的id、name和price
const { id, name, price } = product;
console.log('Product basic info:', { id, name, price });

// 2. 提取产品的颜色和电池寿命
const { specs: { color, battery } } = product;
console.log('Product specs:', { color, battery });

// 3. 提取第一个评论的评分
const { reviews: [{ rating }] } = product;
console.log('First review rating:', rating);

// 练习3：扩展运算符应用
console.log('\n===== 练习3解答：扩展运算符应用 =====');

// 1. 合并两个数组，不修改原数组
const arr3 = [1, 2, 3];
const arr4 = [4, 5, 6];
const mergedArray = [...arr3, ...arr4];
console.log('Merged array:', mergedArray);
console.log('Original arrays unchanged:', arr3, arr4);

// 2. 创建一个新对象，包含原对象的所有属性，并添加一个新属性
const user2 = { name: 'Alice', age: 30 };
const userWithStatus = { ...user2, status: 'active' };
console.log('User with status:', userWithStatus);

// 3. 创建一个函数，接受任意数量的参数并返回它们的平均值
function average(...numbers) {
  if (numbers.length === 0) return 0;
  const sum = numbers.reduce((total, num) => total + num, 0);
  return sum / numbers.length;
}

console.log('Average of 1, 2, 3, 4, 5:', average(1, 2, 3, 4, 5));
console.log('Average of 10, 20:', average(10, 20));
console.log('Average of no numbers:', average());

console.log('\n===== 第4章示例代码结束 =====');