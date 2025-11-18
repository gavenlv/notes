// 基础ES6示例
const greeting = (name) => `Hello, ${name}!`;
console.log(greeting('World'));

// 使用let和const
let counter = 0;
const PI = 3.14159;

// 箭头函数
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(num => num * 2);
console.log('Doubled numbers:', doubled);

// 模板字符串
const user = {
  name: 'Alice',
  age: 30,
  occupation: 'Developer'
};

const userInfo = `
  Name: ${user.name}
  Age: ${user.age}
  Occupation: ${user.occupation}
`;

console.log(userInfo);

// 解构赋值
const { name, age } = user;
console.log(`Name: ${name}, Age: ${age}`);

// 对象字面量增强
const id = 123;
const createUser = (name, email) => ({
  id,
  name,
  email,
  // 方法简写
  getInfo() {
    return `${this.name} (${this.email})`;
  }
});

const newUser = createUser('Bob', 'bob@example.com');
console.log(newUser.getInfo());

// 类
class Person {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
  
  introduce() {
    return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
  }
  
  static compareAge(person1, person2) {
    return person1.age - person2.age;
  }
}

const alice = new Person('Alice', 30);
const bob = new Person('Bob', 25);
console.log(alice.introduce());
console.log(`Age difference: ${Person.compareAge(alice, bob)} years`);

// 数组方法
const fruits = ['apple', 'banana', 'orange'];
const hasApple = fruits.includes('apple');
const firstLongFruit = fruits.find(fruit => fruit.length > 5);

console.log(`Has apple: ${hasApple}`);
console.log(`First long fruit: ${firstLongFruit}`);

// Promise示例
const fetchUserData = (userId) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (userId > 0) {
        resolve({
          id: userId,
          name: `User ${userId}`,
          email: `user${userId}@example.com`
        });
      } else {
        reject(new Error('Invalid user ID'));
      }
    }, 1000);
  });
};

fetchUserData(1)
  .then(user => {
    console.log('User data:', user);
    return fetchUserData(2);
  })
  .then(user => {
    console.log('Second user data:', user);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });

// 展开运算符
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2];
console.log('Combined array:', combined);

const originalUser = { name: 'Alice', age: 30 };
const updatedUser = { ...originalUser, email: 'alice@example.com' };
console.log('Updated user:', updatedUser);

// 默认参数
const greet = (name = 'Guest', greeting = 'Hello') => {
  return `${greeting}, ${name}!`;
};

console.log(greet());
console.log(greet('Bob'));
console.log(greet('Charlie', 'Hi'));

// 剩余参数
const sum = (...numbers) => {
  return numbers.reduce((total, num) => total + num, 0);
};

console.log('Sum of 1, 2, 3, 4, 5:', sum(1, 2, 3, 4, 5));