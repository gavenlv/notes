// 第4章：对象与数组 - 示例代码

// ====================== 对象基础 ======================

// 1.1 对象创建方式

// 1. 对象字面量
const person = {
  name: "张三",
  age: 30,
  isStudent: false,
  greet: function() {
    return "你好，我是" + this.name;
  },
  // ES6简写方法
  introduce() {
    return `我是${this.name}，今年${this.age}岁`;
  }
};

// 2. 构造函数
function Car(brand, model, year) {
  this.brand = brand;
  this.model = model;
  this.year = year;
  this.start = function() {
    console.log(`${this.brand} ${this.model} 启动了！`);
  };
}

const myCar = new Car("特斯拉", "Model 3", 2023);

// 3. Object.create()
const personPrototype = {
  greet: function() {
    return `你好，我是${this.firstName} ${this.lastName}`;
  }
};

const john = Object.create(personPrototype);
john.firstName = "约翰";
john.lastName = "史密斯";

// 1.2 属性操作

// 添加属性
person.job = "前端开发";
person["salary"] = 15000;

// 访问属性
console.log(person.name); // 点表示法
console.log(person["job"]); // 方括号表示法

// 修改属性
person.age = 31;

// 删除属性
delete person.isStudent;

// 1.3 属性枚举
const book = {
  title: "JavaScript高级程序设计",
  author: "尼古拉斯·泽卡斯",
  year: 2019,
  isbn: "978-7-115-51766-1"
};

// for...in循环
for (const prop in book) {
  console.log(prop + ": " + book[prop]);
}

// Object.keys()、Object.values()、Object.entries()
const keys = Object.keys(book);
const values = Object.values(book);
const entries = Object.entries(book);

// 1.4 属性特性
const employee = {};

Object.defineProperty(employee, "id", {
  value: 12345,
  writable: false,
  enumerable: true,
  configurable: true
});

// 使用getter和setter
const product = {
  _price: 100,
  
  get price() {
    return this._price;
  },
  
  set price(newPrice) {
    if (typeof newPrice === "number" && newPrice > 0) {
      this._price = newPrice;
    }
  }
};

console.log(product.price); // 100
product.price = 200;
console.log(product.price); // 200
product.price = -50; // 不会设置负值
console.log(product.price); // 200

// ====================== 对象方法 ======================

// 2.1 Object静态方法

// Object.assign() - 对象复制
const source = { a: 1, b: 2 };
const target = { c: 3 };
Object.assign(target, source);
console.log(target); // {c: 3, a: 1, b: 2}

// Object.is() - 值比较
console.log(Object.is(100, 100)); // true
console.log(Object.is(NaN, NaN)); // true
console.log(Object.is(+0, -0)); // false

// Object.freeze() - 冻结对象
const frozen = { prop: "值" };
Object.freeze(frozen);
frozen.prop = "新值"; // 静默失败
console.log(frozen.prop); // "值"

// Object.seal() - 密封对象
const sealed = { prop: "值" };
Object.seal(sealed);
sealed.prop = "新值"; // 可以修改
sealed.newProp = "新属性"; // 静默失败
console.log(sealed); // {prop: "新值"}

// ====================== 数组基础 ======================

// 3.1 数组创建方式

// 1. 数组字面量
const fruits = ["苹果", "香蕉", "橙子"];
const mixed = [1, "字符串", true, null, {a: 1}, [1, 2, 3]];

// 2. Array构造函数
const arr1 = new Array(); // 空数组
const arr2 = new Array(3); // 长度为3的空数组
const arr3 = new Array(1, 2, 3); // [1, 2, 3]

// 3. Array.of()和Array.from()
const arr4 = Array.of(5); // [5]
const chars = Array.from("hello"); // ["h", "e", "l", "l", "o"]

// 从类数组对象创建数组
const arrayLike = {0: "a", 1: "b", 2: "c", length: 3};
const arr5 = Array.from(arrayLike); // ["a", "b", "c"]

// 3.2 数组访问和修改

// 访问元素
console.log(fruits[0]); // "苹果"
console.log(fruits[1]); // "香蕉"

// 修改元素
fruits[0] = "草莓";

// 添加元素
fruits[fruits.length] = "葡萄";

// 3.3 数组长度
fruits.length = 5; // 增加长度，创建空位
console.log(fruits); // ["草莓", "香蕉", "橙子", "葡萄", <1 empty item>]

fruits.length = 3; // 减少长度，截断数组
console.log(fruits); // ["草莓", "香蕉", "橙子"]

// ====================== 数组方法 ======================

// 4.1 添加和删除元素

const numbers = [1, 2, 3];

// push() - 在末尾添加
numbers.push(4, 5);
console.log(numbers); // [1, 2, 3, 4, 5]

// pop() - 删除并返回末尾元素
const last = numbers.pop();
console.log(last); // 5
console.log(numbers); // [1, 2, 3, 4]

// unshift() - 在开头添加
numbers.unshift(0);
console.log(numbers); // [0, 1, 2, 3, 4]

// shift() - 删除并返回开头元素
const first = numbers.shift();
console.log(first); // 0
console.log(numbers); // [1, 2, 3, 4]

// splice() - 在中间添加/删除元素
numbers.splice(1, 1, 2.5); // 在索引1处删除1个元素，并插入2.5
console.log(numbers); // [1, 2.5, 3, 4]

// 4.2 查找和过滤

const data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// find() - 返回第一个满足条件的元素
const evenNumber = data.find(num => num % 2 === 0);
console.log(evenNumber); // 2

// findIndex() - 返回第一个满足条件的元素的索引
const evenIndex = data.findIndex(num => num % 2 === 0);
console.log(evenIndex); // 1

// indexOf() - 返回指定元素的第一个索引
console.log(data.indexOf(5)); // 4
console.log(data.indexOf(11)); // -1 (不存在)

// includes() - 检查是否包含某个元素
console.log(data.includes(5)); // true
console.log(data.includes(11)); // false

// filter() - 返回所有满足条件的元素组成的新数组
const evenNumbers = data.filter(num => num % 2 === 0);
console.log(evenNumbers); // [2, 4, 6, 8, 10]

// 4.3 转换方法

// map() - 对每个元素执行函数，返回新数组
const doubled = data.map(num => num * 2);
console.log(doubled); // [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

// reduce() - 将数组减少为单个值
const sum = data.reduce((acc, num) => acc + num, 0);
console.log(sum); // 55

// 找出最大值
const max = data.reduce((max, current) => current > max ? current : max);
console.log(max); // 10

// 4.4 其他有用方法

// every() - 检查是否所有元素都满足条件
const allPositive = data.every(num => num > 0);
console.log(allPositive); // true

// some() - 检查是否有元素满足条件
const hasEven = data.some(num => num % 2 === 0);
console.log(hasEven); // true

// slice() - 提取数组的一部分
const slice = data.slice(2, 7);
console.log(slice); // [3, 4, 5, 6, 7]

// concat() - 连接数组
const moreNumbers = [11, 12, 13];
const combined = data.concat(moreNumbers);
console.log(combined); // [1, 2, ..., 10, 11, 12, 13]

// join() - 将数组元素连接成字符串
const words = ["JavaScript", "is", "awesome"];
const sentence = words.join(" ");
console.log(sentence); // "JavaScript is awesome"

// 4.5 ES6数组方法

// 扩展运算符(...)
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combinedES6 = [...arr1, ...arr2];
console.log(combinedES6); // [1, 2, 3, 4, 5, 6]

// 解构赋值
const [firstNum, secondNum, ...rest] = data;
console.log(firstNum); // 1
console.log(secondNum); // 2
console.log(rest); // [3, 4, 5, 6, 7, 8, 9, 10]

// ====================== 对象与数组的实际应用 ======================

// 5.1 复杂数据结构
const company = {
  name: "科技创新公司",
  founded: 2010,
  employees: [
    {
      id: 1,
      name: "张三",
      position: "前端开发",
      department: "技术部",
      skills: ["HTML", "CSS", "JavaScript", "React"],
      contact: {
        email: "zhangsan@example.com",
        phone: "138-0000-0001"
      }
    },
    {
      id: 2,
      name: "李四",
      position: "后端开发",
      department: "技术部",
      skills: ["Node.js", "Python", "数据库"],
      contact: {
        email: "lisi@example.com",
        phone: "138-0000-0002"
      }
    },
    {
      id: 3,
      name: "王五",
      position: "产品经理",
      department: "产品部",
      skills: ["产品设计", "需求分析", "项目管理"],
      contact: {
        email: "wangwu@example.com",
        phone: "138-0000-0003"
      }
    }
  ],
  departments: [
    {
      name: "技术部",
      manager: "赵经理",
      budget: 500000
    },
    {
      name: "产品部",
      manager: "钱经理",
      budget: 300000
    }
  ]
};

// 5.2 数据查询和分析

// 获取所有技术部员工
const techEmployees = company.employees.filter(
  employee => employee.department === "技术部"
);

// 获取所有技能并去重
const allSkills = company.employees
  .flatMap(employee => employee.skills)
  .filter((skill, index, self) => self.indexOf(skill) === index);

// 计算每个部门的员工数量
const departmentCounts = company.employees.reduce((result, employee) => {
  result[employee.department] = (result[employee.department] || 0) + 1;
  return result;
}, {});

// 5.3 数据转换

// 将员工数组转换为以ID为键的对象
const employeesById = company.employees.reduce((result, employee) => {
  result[employee.id] = employee;
  return result;
}, {});

// 提取所有员工姓名
const employeeNames = company.employees.map(employee => employee.name);

// 创建部门-员工映射
const departmentToEmployees = company.employees.reduce((result, employee) => {
  const dept = employee.department;
  if (!result[dept]) {
    result[dept] = [];
  }
  result[dept].push(employee.name);
  return result;
}, {});

// 5.4 实用工具函数

// 对象深拷贝
function deepClone(obj) {
  if (obj === null || typeof obj !== "object") {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime());
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item));
  }
  
  const cloned = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  
  return cloned;
}

// 数组去重
function uniqueArray(arr) {
  return [...new Set(arr)];
}

// 数组分组
function groupBy(array, key) {
  return array.reduce((result, item) => {
    const group = typeof key === "function" ? key(item) : item[key];
    if (!result[group]) {
      result[group] = [];
    }
    result[group].push(item);
    return result;
  }, {});
}

// 数组扁平化
function flattenArray(arr) {
  return arr.reduce((flat, item) => {
    return flat.concat(Array.isArray(item) ? flattenArray(item) : item);
  }, []);
}

// ====================== 最佳实践 ======================

// 6.1 对象使用最佳实践

// 使用有意义的属性名
const user = {
  firstName: "约翰",
  lastName: "史密斯",
  birthDate: new Date(1990, 5, 15)
};

// 不好的做法
// const u = {
//   fn: "约翰",
//   ln: "史密斯",
//   bd: new Date(1990, 5, 15)
// };

// 使用简洁的对象方法
const calculator = {
  add(a, b) {
    return a + b;
  },
  
  subtract(a, b) {
    return a - b;
  }
};

// 6.2 数组使用最佳实践

// 使用扩展运算符代替concat
const newArray = [...array1, ...array2];

// 使用Array.from代替slice
const arrayLike = {0: 'a', 1: 'b', 2: 'c', length: 3};
const array = Array.from(arrayLike);

// 使用includes代替indexOf检查元素是否存在
if (array.includes(item)) { /*...*/ }

// 6.3 性能考虑

// 避免在循环中修改数组长度
// 不好的做法
// for (let i = 0; i < arr.length; i++) {
//   if (condition) arr.splice(i, 1);
// }

// 好的做法
const filtered = arr.filter(item => !condition);

// 使用for循环而不是forEach在性能关键的代码中
for (let i = 0; i < largeArray.length; i++) {
  // 处理元素
}

// 6.4 安全性考虑

// 防止原型污染
function safeMerge(target, source) {
  const result = Object.assign({}, target);
  
  Object.keys(source).forEach(key => {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      return;
    }
    result[key] = source[key];
  });
  
  return result;
}

// 检查对象是否为普通对象
function isPlainObject(obj) {
  return obj && typeof obj === 'object' && obj.constructor === Object;
}