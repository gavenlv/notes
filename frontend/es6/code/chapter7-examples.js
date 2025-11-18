// 第7章：类与继承 - 代码示例

// 7.1.1 类的基本语法
console.log('=== 7.1.1 类的基本语法 ===');

// ES5构造函数方式
function PersonES5(name, age) {
  this.name = name;
  this.age = age;
}

PersonES5.prototype.sayHello = function() {
  return `Hello, my name is ${this.name} and I'm ${this.age} years old.`;
};

// ES6类方式
class Person {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }

  sayHello() {
    return `Hello, my name is ${this.name} and I'm ${this.age} years old.`;
  }
}

// 使用类创建实例
const alice = new Person('Alice', 30);
console.log(alice.sayHello()); // "Hello, my name is Alice and I'm 30 years old."

// 7.1.2 类声明与类表达式
console.log('\n=== 7.1.2 类声明与类表达式 ===');

// 类声明
class PersonDeclaration {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
}

// 类表达式（匿名）
const PersonExpression = class {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
};

// 类表达式（命名）
const PersonNamedExpression = class PersonClass {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
  
  getClassName() {
    return PersonClass.name;
  }
};

const personNamed = new PersonNamedExpression('Bob', 25);
console.log(personNamed.getClassName()); // "PersonClass"

// 7.1.3 类的特性
console.log('\n=== 7.1.3 类的特性 ===');

// 类的方法是不可枚举的
class PersonEnumeration {
  constructor(name) {
    this.name = name;
  }
  
  sayHello() {
    return `Hello, I'm ${this.name}`;
  }
}

const personEnum = new PersonEnumeration('Alice');
console.log('使用for...in遍历:');
for (const key in personEnum) {
  console.log(key); // 只会输出 "name"，不会输出 "sayHello"
}

console.log('使用Object.keys():');
console.log(Object.keys(personEnum)); // ["name"]
console.log('使用Object.getOwnPropertyNames():');
console.log(Object.getOwnPropertyNames(personEnum.__proto__)); // ["constructor", "sayHello"]

// 7.2.1 基本继承语法
console.log('\n=== 7.2.1 基本继承语法 ===');

class Animal {
  constructor(name) {
    this.name = name;
  }
  
  speak() {
    return `${this.name} makes a noise.`;
  }
}

class Dog extends Animal {
  speak() {
    return `${this.name} barks.`;
  }
}

const dog = new Dog('Rex');
console.log(dog.speak()); // "Rex barks."

// 7.2.2 super关键字
console.log('\n=== 7.2.2 super关键字 ===');

class AnimalSuper {
  constructor(name) {
    this.name = name;
  }
  
  speak() {
    return `${this.name} makes a noise.`;
  }
}

class DogSuper extends AnimalSuper {
  constructor(name, breed) {
    super(name); // 调用父类的构造函数
    this.breed = breed;
  }
  
  speak() {
    // 调用父类的speak方法
    return `${super.speak()} It's a ${this.breed}.`;
  }
  
  fetch() {
    return `${this.name} is fetching.`;
  }
}

const dogSuper = new DogSuper('Rex', 'Golden Retriever');
console.log(dogSuper.speak()); // "Rex makes a noise. It's a Golden Retriever."
console.log(dogSuper.fetch()); // "Rex is fetching."

// 7.2.3 继承中的方法覆盖
console.log('\n=== 7.2.3 继承中的方法覆盖 ===');

class Vehicle {
  constructor(speed) {
    this.speed = speed;
  }
  
  accelerate(amount) {
    this.speed += amount;
    return `Speed increased to ${this.speed} km/h.`;
  }
  
  brake(amount) {
    this.speed = Math.max(0, this.speed - amount);
    return `Speed decreased to ${this.speed} km/h.`;
  }
}

class Car extends Vehicle {
  constructor(speed, fuel) {
    super(speed);
    this.fuel = fuel;
  }
  
  accelerate(amount) {
    // 检查燃料是否足够
    if (this.fuel <= 0) {
      return "Cannot accelerate: no fuel!";
    }
    
    // 调用父类的accelerate方法
    const result = super.accelerate(amount);
    
    // 消耗燃料
    this.fuel -= amount * 0.1;
    
    return `${result} Fuel remaining: ${this.fuel.toFixed(1)}L.`;
  }
  
  refuel(amount) {
    this.fuel += amount;
    return `Refueled. Fuel now: ${this.fuel}L.`;
  }
}

const car = new Car(0, 50);
console.log(car.accelerate(20)); // "Speed increased to 20 km/h. Fuel remaining: 48.0L."
console.log(car.accelerate(30)); // "Speed increased to 50 km/h. Fuel remaining: 45.0L."
console.log(car.brake(10)); // "Speed decreased to 40 km/h."
console.log(car.refuel(20)); // "Refueled. Fuel now: 65.0L."

// 7.2.4 继承中的静态方法和属性
console.log('\n=== 7.2.4 继承中的静态方法和属性 ===');

class Shape {
  static count = 0;
  
  constructor() {
    Shape.count++;
  }
  
  static getCount() {
    return `Total shapes created: ${Shape.count}`;
  }
  
  area() {
    throw new Error('Must implement area method');
  }
}

class Circle extends Shape {
  constructor(radius) {
    super();
    this.radius = radius;
  }
  
  area() {
    return Math.PI * this.radius ** 2;
  }
  
  static getCircleCount() {
    // 调用父类的静态方法
    return `${super.getCount()} (including circles)`;
  }
}

class Rectangle extends Shape {
  constructor(width, height) {
    super();
    this.width = width;
    this.height = height;
  }
  
  area() {
    return this.width * this.height;
  }
}

const circle = new Circle(5);
const rectangle = new Rectangle(4, 6);

console.log(Shape.getCount()); // "Total shapes created: 2"
console.log(Circle.getCircleCount()); // "Total shapes created: 2 (including circles)"
console.log(circle.area()); // 78.53981633974483
console.log(rectangle.area()); // 24

// 7.3.1 静态方法
console.log('\n=== 7.3.1 静态方法 ===');

class MathUtils {
  static add(a, b) {
    return a + b;
  }
  
  static multiply(a, b) {
    return a * b;
  }
  
  // 静态方法可以调用其他静态方法
  static power(base, exponent) {
    let result = 1;
    for (let i = 0; i < exponent; i++) {
      result = this.multiply(result, base);
    }
    return result;
  }
  
  // 静态方法不能访问实例属性或方法
  static getPi() {
    // return this.radius; // 错误：静态方法不能访问实例属性
    return Math.PI;
  }
}

// 调用静态方法
console.log(MathUtils.add(5, 3)); // 8
console.log(MathUtils.multiply(4, 6)); // 24
console.log(MathUtils.power(2, 3)); // 8
console.log(MathUtils.getPi()); // 3.141592653589793

const math = new MathUtils();
// math.add(5, 3); // 错误：实例不能调用静态方法

// 7.3.2 静态属性
console.log('\n=== 7.3.2 静态属性 ===');

class Counter {
  static count = 0;
  
  constructor() {
    Counter.count++;
  }
  
  static getCount() {
    return Counter.count;
  }
  
  static reset() {
    Counter.count = 0;
  }
}

const counter1 = new Counter();
const counter2 = new Counter();
const counter3 = new Counter();

console.log(Counter.getCount()); // 3
console.log(Counter.count); // 3

Counter.reset();
console.log(Counter.getCount()); // 0

// 7.3.3 静态块
console.log('\n=== 7.3.3 静态块 ===');

class DatabaseConnection {
  static connectionPool = [];
  static maxConnections = 5;
  
  static {
    // 静态初始化块
    console.log('Initializing database connection pool...');
    
    // 初始化连接池
    for (let i = 0; i < this.maxConnections; i++) {
      this.connectionPool.push({
        id: i,
        active: false,
        created: new Date()
      });
    }
    
    console.log(`Database connection pool initialized with ${this.connectionPool.length} connections.`);
  }
  
  static getConnection() {
    const connection = this.connectionPool.find(conn => !conn.active);
    
    if (connection) {
      connection.active = true;
      return connection;
    }
    
    throw new Error('No available connections in the pool');
  }
  
  static releaseConnection(connectionId) {
    const connection = this.connectionPool.find(conn => conn.id === connectionId);
    
    if (connection) {
      connection.active = false;
      return true;
    }
    
    return false;
  }
}

const conn1 = DatabaseConnection.getConnection();
console.log(`Connection ${conn1.id} acquired`);

DatabaseConnection.releaseConnection(conn1.id);
console.log(`Connection ${conn1.id} released`);

// 7.4.1 私有字段
console.log('\n=== 7.4.1 私有字段 ===');

class BankAccount {
  #balance = 0; // 私有字段
  #transactions = []; // 私有字段
  
  constructor(initialBalance) {
    if (initialBalance > 0) {
      this.#balance = initialBalance;
    }
  }
  
  deposit(amount) {
    if (amount <= 0) {
      throw new Error('Deposit amount must be positive');
    }
    
    this.#balance += amount;
    this.#transactions.push({
      type: 'deposit',
      amount,
      timestamp: new Date()
    });
    
    return this.#balance;
  }
  
  withdraw(amount) {
    if (amount <= 0) {
      throw new Error('Withdrawal amount must be positive');
    }
    
    if (amount > this.#balance) {
      throw new Error('Insufficient funds');
    }
    
    this.#balance -= amount;
    this.#transactions.push({
      type: 'withdrawal',
      amount,
      timestamp: new Date()
    });
    
    return this.#balance;
  }
  
  getBalance() {
    return this.#balance;
  }
  
  getTransactionHistory() {
    // 返回交易历史的副本，防止外部修改
    return [...this.#transactions];
  }
}

const account = new BankAccount(100);
account.deposit(50);
account.withdraw(30);

console.log(account.getBalance()); // 120
console.log(account.getTransactionHistory()); // 交易历史数组

// account.#balance; // 语法错误：私有字段只能在类内部访问
// account.#transactions; // 语法错误：私有字段只能在类内部访问

// 7.4.2 私有方法
console.log('\n=== 7.4.2 私有方法 ===');

class DataProcessor {
  #data = [];
  #errors = [];
  
  constructor(data) {
    this.#data = data;
  }
  
  process() {
    try {
      this.#validate();
      this.#transform();
      this.#save();
      return { success: true, data: this.#data };
    } catch (error) {
      this.#errors.push(error);
      return { success: false, errors: this.#errors };
    }
  }
  
  // 私有方法：验证数据
  #validate() {
    if (!Array.isArray(this.#data)) {
      throw new Error('Data must be an array');
    }
    
    if (this.#data.length === 0) {
      throw new Error('Data array cannot be empty');
    }
  }
  
  // 私有方法：转换数据
  #transform() {
    this.#data = this.#data.map(item => {
      if (typeof item === 'string') {
        return item.trim().toLowerCase();
      }
      return item;
    });
  }
  
  // 私有方法：保存数据
  #save() {
    // 模拟保存操作
    console.log('Data saved successfully');
  }
}

const processor = new DataProcessor(['  Item 1  ', 'ITEM 2', 'Item 3']);
const result = processor.process();

console.log(result); // { success: true, data: ['item 1', 'item 2', 'item 3'] }

// processor.#validate(); // 语法错误：私有方法只能在类内部调用

// 7.4.3 私有字段的继承
console.log('\n=== 7.4.3 私有字段的继承 ===');

class Parent {
  #privateField = 'parent private';
  publicField = 'parent public';
  
  getPrivateField() {
    return this.#privateField;
  }
}

class Child extends Parent {
  #privateField = 'child private';
  publicField = 'child public';
  
  getChildPrivateField() {
    return this.#privateField;
  }
  
  // 尝试访问父类的私有字段
  // getParentPrivateField() {
  //   return this.#privateField; // 错误：无法访问父类的私有字段
  // }
}

const child = new Child();
console.log(child.getChildPrivateField()); // "child private"
console.log(child.getPrivateField()); // "parent private"
console.log(child.publicField); // "child public"

// 7.5.1 组件系统
console.log('\n=== 7.5.1 组件系统 ===');

// 注意：这个示例在浏览器环境中运行效果更好
// 这里只展示类定义部分

class Component {
  constructor(element, options = {}) {
    this.element = element;
    this.options = { ...this.defaultOptions, ...options };
    this.state = {};
    this.init();
  }
  
  get defaultOptions() {
    return {
      className: 'component',
      visible: true
    };
  }
  
  init() {
    console.log(`Initializing component with class: ${this.options.className}`);
    this.render();
    this.bindEvents();
  }
  
  render() {
    // 默认渲染逻辑
    console.log(`Rendering component, visible: ${this.options.visible}`);
  }
  
  bindEvents() {
    // 默认事件绑定
    console.log('Binding events for component');
  }
  
  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.render();
  }
  
  show() {
    this.options.visible = true;
    this.render();
  }
  
  hide() {
    this.options.visible = false;
    this.render();
  }
}

class Button extends Component {
  get defaultOptions() {
    return {
      ...super.defaultOptions,
      className: 'btn',
      text: 'Button',
      onClick: null
    };
  }
  
  render() {
    super.render();
    console.log(`Rendering button with text: ${this.options.text}`);
  }
  
  bindEvents() {
    super.bindEvents();
    if (this.options.onClick) {
      console.log('Binding click event to button');
    }
  }
  
  setText(text) {
    this.options.text = text;
    this.render();
  }
}

// 模拟DOM元素
const mockElement = { addEventListener: () => {} };

const button = new Button(mockElement, {
  text: 'Click me',
  onClick: () => console.log('Button clicked')
});

button.setText('New text');
button.hide();
button.show();

// 7.5.2 数据模型
console.log('\n=== 7.5.2 数据模型 ===');

class UserModel {
  #id;
  #name;
  #email;
  #createdAt;
  #updatedAt;
  
  constructor({ id, name, email }) {
    this.#id = id || this.#generateId();
    this.#name = name;
    this.#email = email;
    this.#createdAt = new Date();
    this.#updatedAt = new Date();
  }
  
  // 私有方法：生成ID
  #generateId() {
    return Math.random().toString(36).substr(2, 9);
  }
  
  // 私有方法：验证邮箱
  #validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
  
  // 公共方法：获取用户信息
  getInfo() {
    return {
      id: this.#id,
      name: this.#name,
      email: this.#email,
      createdAt: this.#createdAt,
      updatedAt: this.#updatedAt
    };
  }
  
  // 公共方法：更新用户名
  updateName(newName) {
    if (!newName || newName.trim() === '') {
      throw new Error('Name cannot be empty');
    }
    
    this.#name = newName.trim();
    this.#updatedAt = new Date();
    return this.getInfo();
  }
  
  // 公共方法：更新邮箱
  updateEmail(newEmail) {
    if (!this.#validateEmail(newEmail)) {
      throw new Error('Invalid email format');
    }
    
    this.#email = newEmail;
    this.#updatedAt = new Date();
    return this.getInfo();
  }
  
  // 静态方法：从API响应创建用户实例
  static fromApiResponse(data) {
    return new UserModel({
      id: data.id,
      name: data.name,
      email: data.email
    });
  }
  
  // 静态方法：验证用户数据
  static validateUserData(data) {
    const errors = [];
    
    if (!data.name || data.name.trim() === '') {
      errors.push('Name is required');
    }
    
    if (!data.email) {
      errors.push('Email is required');
    } else {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!re.test(data.email)) {
        errors.push('Invalid email format');
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// 使用示例
const user = new UserModel({
  name: 'John Doe',
  email: 'john@example.com'
});

console.log(user.getInfo());
// 更新用户信息
user.updateName('Jane Doe');
user.updateEmail('jane@example.com');
console.log(user.getInfo());

// 从API响应创建用户
const apiResponse = {
  id: 'user123',
  name: 'API User',
  email: 'api@example.com'
};

const apiUser = UserModel.fromApiResponse(apiResponse);
console.log(apiUser.getInfo());

// 验证用户数据
const userData = {
  name: '',
  email: 'invalid-email'
};

const validation = UserModel.validateUserData(userData);
console.log(validation.isValid); // false
console.log(validation.errors); // ["Name is required", "Invalid email format"]

// 7.7.1 类设计原则
console.log('\n=== 7.7.1 类设计原则 ===');

// 单一职责原则：每个类应该只有一个引起变化的原因
class User {
  constructor(id, name, email) {
    this.id = id;
    this.name = name;
    this.email = email;
  }
  
  updateProfile(newData) {
    // 更新用户信息的逻辑
    console.log('Updating user profile');
  }
}

class UserRepository {
  save(user) {
    // 保存用户到数据库的逻辑
    console.log('Saving user to database');
  }
  
  findById(id) {
    // 从数据库查找用户的逻辑
    console.log(`Finding user by ID: ${id}`);
  }
}

class UserValidator {
  validate(user) {
    // 验证用户数据的逻辑
    console.log('Validating user data');
    return { isValid: true };
  }
}

// 开闭原则：对扩展开放，对修改关闭
class Shape {
  area() {
    throw new Error('Must implement area method');
  }
}

class Circle extends Shape {
  constructor(radius) {
    super();
    this.radius = radius;
  }
  
  area() {
    return Math.PI * this.radius ** 2;
  }
}

class Rectangle extends Shape {
  constructor(width, height) {
    super();
    this.width = width;
    this.height = height;
  }
  
  area() {
    return this.width * this.height;
  }
}

const circleShape = new Circle(5);
const rectangleShape = new Rectangle(4, 6);

console.log(`Circle area: ${circleShape.area()}`);
console.log(`Rectangle area: ${rectangleShape.area()}`);

// 7.7.2 使用私有字段封装内部状态
console.log('\n=== 7.7.2 使用私有字段封装内部状态 ===');

class Counter {
  #count = 0;
  
  increment() {
    this.#count++;
    return this.#count;
  }
  
  decrement() {
    this.#count--;
    return this.#count;
  }
  
  getCount() {
    return this.#count;
  }
}

const counter = new Counter();
console.log(counter.increment()); // 1
console.log(counter.increment()); // 2
console.log(counter.decrement()); // 1
console.log(counter.getCount()); // 1

// counter.#count = 100; // 语法错误：私有字段只能在类内部访问

// 7.8.2 如何实现多重继承
console.log('\n=== 7.8.2 如何实现多重继承 ===');

// 使用组合模式实现多重继承
class FlyBehavior {
  fly() {
    return `${this.name} is flying`;
  }
}

class SwimBehavior {
  swim() {
    return `${this.name} is swimming`;
  }
}

class Duck {
  constructor(name) {
    this.name = name;
    this.flyBehavior = new FlyBehavior();
    this.swimBehavior = new SwimBehavior();
  }
  
  fly() {
    return this.flyBehavior.fly.call(this);
  }
  
  swim() {
    return this.swimBehavior.swim.call(this);
  }
}

const duck = new Duck('Donald');
console.log(duck.fly()); // "Donald is flying"
console.log(duck.swim()); // "Donald is swimming"

// 7.8.3 如何实现抽象类
console.log('\n=== 7.8.3 如何实现抽象类 ===');

// 使用构造函数检查实现抽象类
class ShapeAbstract {
  constructor() {
    if (new.target === ShapeAbstract) {
      throw new Error('Cannot instantiate abstract class');
    }
  }
  
  area() {
    throw new Error('Must implement area method');
  }
}

class CircleAbstract extends ShapeAbstract {
  constructor(radius) {
    super();
    this.radius = radius;
  }
  
  area() {
    return Math.PI * this.radius ** 2;
  }
}

// const shape = new ShapeAbstract(); // 错误：不能实例化抽象类
const circleAbstract = new CircleAbstract(5);
console.log(circleAbstract.area()); // 78.53981633974483

// 7.8.4 如何实现私有方法的继承
console.log('\n=== 7.8.4 如何实现私有方法的继承 ===');

// 使用命名约定实现受保护方法
class ParentProtected {
  constructor() {
    this._protectedMethod = this._protectedMethod.bind(this);
  }
  
  // 使用下划线前缀表示受保护的方法
  _protectedMethod() {
    return 'Protected method from parent';
  }
  
  publicMethod() {
    return this._protectedMethod();
  }
}

class ChildProtected extends ParentProtected {
  childMethod() {
    return this._protectedMethod(); // 可以访问受保护的方法
  }
}

const childProtected = new ChildProtected();
console.log(childProtected.childMethod()); // "Protected method from parent"

// 练习1：创建一个简单的游戏角色类
console.log('\n=== 练习1：创建一个简单的游戏角色类 ===');

class Character {
  static charactersCount = 0;
  
  #id;
  #name;
  #health;
  #attack;
  
  constructor(name, health, attack) {
    this.#id = this.#generateId();
    this.#name = name;
    this.#health = health;
    this.#attack = attack;
    Character.charactersCount++;
  }
  
  // 私有方法：生成ID
  #generateId() {
    return Math.random().toString(36).substr(2, 9);
  }
  
  get id() {
    return this.#id;
  }
  
  get name() {
    return this.#name;
  }
  
  get health() {
    return this.#health;
  }
  
  get attack() {
    return this.#attack;
  }
  
  attack(target) {
    console.log(`${this.#name} attacks ${target.name} for ${this.#attack} damage!`);
    return target.takeDamage(this.#attack);
  }
  
  takeDamage(amount) {
    this.#health = Math.max(0, this.#health - amount);
    console.log(`${this.#name} takes ${amount} damage, remaining health: ${this.#health}`);
    return this.#health;
  }
  
  isAlive() {
    return this.#health > 0;
  }
  
  getInfo() {
    return {
      id: this.#id,
      name: this.#name,
      health: this.#health,
      attack: this.#attack,
      alive: this.isAlive()
    };
  }
}

class Warrior extends Character {
  #armor;
  #rage = false;
  
  constructor(name, health, attack, armor) {
    super(name, health, attack);
    this.#armor = armor;
  }
  
  get armor() {
    return this.#armor;
  }
  
  get rage() {
    return this.#rage;
  }
  
  takeDamage(amount) {
    // 考虑护甲值减少伤害
    const reducedDamage = Math.max(1, amount - this.#armor);
    return super.takeDamage(reducedDamage);
  }
  
  rage() {
    this.#rage = true;
    console.log(`${this.name} enters rage mode! Attack power increased!`);
    // 狂暴模式下增加攻击力
    const originalAttack = this.attack;
    // 这里只是演示，实际应用中可能需要更复杂的实现
    return originalAttack * 1.5;
  }
  
  getInfo() {
    return {
      ...super.getInfo(),
      armor: this.#armor,
      rage: this.#rage
    };
  }
}

// 创建角色实例
const hero = new Character('Hero', 100, 20);
const monster = new Character('Monster', 80, 15);

console.log('Characters created:');
console.log(hero.getInfo());
console.log(monster.getInfo());
console.log(`Total characters: ${Character.charactersCount}`);

// 战斗模拟
hero.attack(monster);
monster.attack(hero);

// 创建战士
const warrior = new Warrior('Warrior', 120, 25, 5);
console.log('Warrior created:');
console.log(warrior.getInfo());

// 战士战斗
warrior.attack(monster);
monster.attack(warrior);

// 战士狂暴
warrior.rage();
warrior.attack(monster);

// 练习2：实现一个简单的表单验证器类
console.log('\n=== 练习2：实现一个简单的表单验证器类 ===');

class FormValidator {
  #errors = {};
  
  constructor(formElement, rules) {
    this.formElement = formElement;
    this.rules = rules;
  }
  
  validate() {
    this.#errors = {};
    
    for (const fieldName in this.rules) {
      const field = this.formElement[fieldName];
      const fieldRules = this.rules[fieldName];
      
      this.#validateField(fieldName, field, fieldRules);
    }
    
    return Object.keys(this.#errors).length === 0;
  }
  
  showErrors() {
    for (const fieldName in this.#errors) {
      console.error(`${fieldName}: ${this.#errors[fieldName]}`);
    }
  }
  
  clearErrors() {
    this.#errors = {};
  }
  
  // 私有方法：验证单个字段
  #validateField(fieldName, field, rules) {
    const value = field.value || '';
    
    for (const rule of rules) {
      const error = rule(value);
      if (error) {
        this.#errors[fieldName] = error;
        break; // 只显示第一个错误
      }
    }
  }
  
  getErrors() {
    return { ...this.#errors };
  }
}

class LoginFormValidator extends FormValidator {
  constructor(formElement) {
    super(formElement, {
      email: [
        value => !value ? 'Email is required' : '',
        value => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 'Invalid email format' : ''
      ],
      password: [
        value => !value ? 'Password is required' : '',
        value => value.length < 8 ? 'Password must be at least 8 characters' : ''
      ]
    });
  }
  
  showErrors() {
    const errors = this.getErrors();
    
    if (Object.keys(errors).length === 0) {
      console.log('Form is valid!');
      return;
    }
    
    console.log('Form validation errors:');
    
    for (const fieldName in errors) {
      const friendlyName = this.#getFriendlyFieldName(fieldName);
      console.error(`${friendlyName}: ${errors[fieldName]}`);
    }
  }
  
  // 私有方法：获取友好的字段名
  #getFriendlyFieldName(fieldName) {
    const fieldNames = {
      email: 'Email',
      password: 'Password'
    };
    
    return fieldNames[fieldName] || fieldName;
  }
}

// 模拟表单元素
const mockForm = {
  email: { value: 'test@example.com' },
  password: { value: 'password123' }
};

// 创建并使用表单验证器
const loginValidator = new LoginFormValidator(mockForm);
const isValid = loginValidator.validate();

console.log(`Form is valid: ${isValid}`);
loginValidator.showErrors();

// 测试无效表单
mockForm.email.value = 'invalid-email';
mockForm.password.value = '123';

const isInvalid = loginValidator.validate();
console.log(`Form is valid: ${isInvalid}`);
loginValidator.showErrors();

// 练习3：实现一个简单的数据缓存类
console.log('\n=== 练习3：实现一个简单的数据缓存类 ===');

class Cache {
  #data = new Map();
  #maxSize = 100;
  #ttl = 60000; // 默认60秒
  
  constructor(maxSize = 100, defaultTtl = 60000) {
    this.#maxSize = maxSize;
    this.#ttl = defaultTtl;
  }
  
  set(key, value, ttl = this.#ttl) {
    // 如果缓存已满，淘汰最旧的条目
    if (this.#data.size >= this.#maxSize) {
      this.#evictOldest();
    }
    
    const expiresAt = Date.now() + ttl;
    this.#data.set(key, {
      value,
      expiresAt,
      createdAt: Date.now()
    });
  }
  
  get(key) {
    if (!this.#data.has(key)) {
      return undefined;
    }
    
    const item = this.#data.get(key);
    
    // 检查是否过期
    if (this.#isExpired(key)) {
      this.#data.delete(key);
      return undefined;
    }
    
    return item.value;
  }
  
  delete(key) {
    return this.#data.delete(key);
  }
  
  clear() {
    this.#data.clear();
  }
  
  // 私有方法：检查缓存是否过期
  #isExpired(key) {
    if (!this.#data.has(key)) {
      return true;
    }
    
    const item = this.#data.get(key);
    return Date.now() > item.expiresAt;
  }
  
  // 私有方法：淘汰最旧的缓存
  #evictOldest() {
    let oldestKey = null;
    let oldestTime = Infinity;
    
    for (const [key, item] of this.#data) {
      if (item.createdAt < oldestTime) {
        oldestKey = key;
        oldestTime = item.createdAt;
      }
    }
    
    if (oldestKey) {
      this.#data.delete(oldestKey);
    }
  }
  
  // 静态方法：创建LRU缓存
  static createLRUCache(maxSize) {
    return new LRUCache(maxSize);
  }
  
  // 获取缓存统计信息
  getStats() {
    return {
      size: this.#data.size,
      maxSize: this.#maxSize,
      ttl: this.#ttl
    };
  }
}

// LRU缓存实现
class LRUCache extends Cache {
  constructor(maxSize = 100) {
    super(maxSize, Infinity); // LRU缓存不过期
    this.#accessOrder = new Map();
  }
  
  get(key) {
    const value = super.get(key);
    
    if (value !== undefined) {
      // 更新访问顺序
      this.#accessOrder.delete(key);
      this.#accessOrder.set(key, Date.now());
    }
    
    return value;
  }
  
  set(key, value) {
    super.set(key, value);
    
    // 更新访问顺序
    this.#accessOrder.delete(key);
    this.#accessOrder.set(key, Date.now());
  }
  
  delete(key) {
    this.#accessOrder.delete(key);
    return super.delete(key);
  }
  
  clear() {
    this.#accessOrder.clear();
    return super.clear();
  }
  
  // 重写淘汰方法，使用LRU策略
  #evictOldest() {
    if (this.#accessOrder.size === 0) {
      return;
    }
    
    // 找到最久未访问的键
    let oldestKey = this.#accessOrder.keys().next().value;
    
    if (oldestKey) {
      this.delete(oldestKey);
    }
  }
}

class AsyncCache extends Cache {
  constructor(maxSize = 100, defaultTtl = 60000) {
    super(maxSize, defaultTtl);
    this.#pendingRequests = new Map();
  }
  
  async getAsync(key, loader) {
    // 首先尝试从缓存获取
    const cachedValue = this.get(key);
    if (cachedValue !== undefined) {
      return cachedValue;
    }
    
    // 检查是否已有正在进行的请求
    if (this.#pendingRequests.has(key)) {
      return this.#pendingRequests.get(key);
    }
    
    // 创建并缓存新的请求
    const promise = loader().then(value => {
      this.set(key, value);
      this.#pendingRequests.delete(key);
      return value;
    }).catch(error => {
      this.#pendingRequests.delete(key);
      throw error;
    });
    
    this.#pendingRequests.set(key, promise);
    return promise;
  }
}

// 使用示例
const cache = new Cache(5, 1000); // 最大5个条目，1秒过期

cache.set('user:1', { name: 'Alice', age: 30 });
cache.set('user:2', { name: 'Bob', age: 25 });

console.log(cache.get('user:1')); // { name: 'Alice', age: 30 }
console.log(cache.get('user:2')); // { name: 'Bob', age: 25 }

// 等待过期后再次获取
setTimeout(() => {
  console.log('After expiration:');
  console.log(cache.get('user:1')); // undefined
  console.log(cache.getStats());
}, 1100);

// 异步缓存示例
const asyncCache = new AsyncCache();

// 模拟异步数据加载函数
function loadUser(id) {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({ id, name: `User ${id}`, loaded: true });
    }, 500);
  });
}

// 使用异步缓存
asyncCache.getAsync('user:3', () => loadUser(3)).then(user => {
  console.log('Async cache result:', user);
});

// 再次获取，将从缓存中读取
asyncCache.getAsync('user:3', () => loadUser(3)).then(user => {
  console.log('Async cache result (from cache):', user);
});