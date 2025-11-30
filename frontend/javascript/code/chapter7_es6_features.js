// 第7章：ES6+新特性 - 示例代码

// ====================== 变量声明与作用域 ======================

// 1.1 let和const比较
function compareVarLetConst() {
    console.log('=== var/let/const 比较 ===');
    
    // 使用var存在的问题
    function varIssues() {
        if (true) {
            var x = 10;
        }
        console.log(x); // 10，var没有块级作用域
        
        for (var i = 0; i < 3; i++) {
            // 循环体
        }
        console.log('循环后的i:', i); // 3，因为i是同一个变量
        
        // 模拟事件处理中的问题
        const handlers = [];
        for (var j = 0; j < 3; j++) {
            handlers.push(function() {
                console.log('var循环中的j:', j); // 都是3
            });
        }
        
        handlers.forEach(handler => handler());
    }
    
    // 使用let解决问题
    function letSolutions() {
        if (true) {
            let x = 10;
        }
        // console.log(x); // ReferenceError: x is not defined，let有块级作用域
        
        for (let i = 0; i < 3; i++) {
            // 循环体
        }
        // console.log(i); // ReferenceError: i is not defined
        
        // 循环中的每个i都是新的变量
        const handlers = [];
        for (let j = 0; j < 3; j++) {
            handlers.push(function() {
                console.log('let循环中的j:', j); // 0, 1, 2
            });
        }
        
        handlers.forEach(handler => handler());
    }
    
    varIssues();
    letSolutions();
}

// 1.2 暂时性死区
function temporalDeadZone() {
    console.log('\n=== 暂时性死区（TDZ） ===');
    
    function tdzExample() {
        // console.log(a); // ReferenceError: a is not defined
        // let a = 10; // 在声明前访问a会报错
        
        // 先使用后声明会报错
        console.log(b); // undefined（变量提升）
        var b = 20;
        
        // console.log(c); // ReferenceError（暂时性死区）
        let c = 30;
    }
    
    function blockScope() {
        let x = 10;
        
        if (true) {
            let y = 20;
            console.log('块内访问x:', x); // 10，可以访问外层作用域
            console.log('块内访问y:', y); // 20
        }
        
        // console.log(y); // ReferenceError，无法访问内层作用域
    }
    
    // 不会直接执行以避免错误，仅展示概念
    // tdzExample();
    blockScope();
}

// 1.3 循环中的作用域
function loopScope() {
    console.log('\n=== 循环中的作用域 ===');
    
    // 模拟按钮点击事件
    const buttons = ['按钮1', '按钮2', '按钮3'];
    
    // 使用let - 每次循环都有新的变量
    for (let i = 0; i < buttons.length; i++) {
        setTimeout(function() {
            console.log(`let循环 - ${buttons[i]} 被点击`);
        }, 100);
    }
    
    // 如果使用var，每个按钮都会显示"按钮3 被点击"
}

// ====================== 箭头函数 ======================

// 2.1 基本语法
function arrowFunctionBasics() {
    console.log('\n=== 箭头函数基础语法 ===');
    
    // 传统函数
    function add(a, b) {
        return a + b;
    }
    
    // 箭头函数不同形式
    const arrow1 = (a, b) => {
        return a + b;
    };
    
    const arrow2 = (a, b) => a + b; // 单表达式
    
    const double = x => x * 2; // 单个参数
    
    const getRandom = () => Math.random(); // 无参数
    
    console.log('传统函数:', add(5, 3)); // 8
    console.log('箭头函数(完整):', arrow1(5, 3)); // 8
    console.log('箭头函数(简化):', arrow2(5, 3)); // 8
    console.log('箭头函数(单参数):', double(5)); // 10
    console.log('箭头函数(无参数):', getRandom().toFixed(4));
}

// 2.2 箭头函数的this
function arrowFunctionThis() {
    console.log('\n=== 箭头函数的this绑定 ===');
    
    const obj = {
        name: "对象",
        
        // 传统函数
        regularFunction: function() {
            console.log('传统方法中的this.name:', this.name); // "对象"
            
            setTimeout(function() {
                console.log('setTimeout内的this.name:', this.name || 'undefined/window'); // undefined/window
            }, 100);
            
            setTimeout(() => {
                console.log('setTimeout箭头函数内的this.name:', this.name); // "对象"
            }, 200);
        },
        
        // 箭头函数作为方法（不推荐）
        arrowMethod: () => {
            console.log('箭头方法内的this.name:', this.name || 'undefined/window'); // undefined/window
        },
        
        // 推荐的简写方法
        recommendedMethod() {
            console.log('推荐方法内的this.name:', this.name); // "对象"
        }
    };
    
    obj.regularFunction();
    obj.arrowMethod();
    obj.recommendedMethod();
}

// 2.3 实际应用
function arrowFunctionApplications() {
    console.log('\n=== 箭头函数的实际应用 ===');
    
    // 数组方法中的使用
    const numbers = [1, 2, 3, 4, 5];
    
    // 使用箭头函数简化代码
    const doubled = numbers.map(x => x * 2);
    const evens = numbers.filter(x => x % 2 === 0);
    const sum = numbers.reduce((acc, x) => acc + x, 0);
    
    console.log('原始数组:', numbers);
    console.log('翻倍:', doubled);
    console.log('偶数:', evens);
    console.log('总和:', sum);
    
    // 嵌套函数中的使用
    function Timer() {
        this.seconds = 0;
        
        setInterval(() => {
            this.seconds++;
            console.log(`计时: ${this.seconds} 秒`);
            
            if (this.seconds >= 5) {
                clearInterval(this.interval);
            }
        }, 1000);
        
        this.interval = setInterval(() => {
            // 上面的代码
        }, 1000);
    }
    
    const timer = new Timer();
}

// ====================== 模板字符串 ======================

// 3.1 基本语法
function templateStringBasics() {
    console.log('\n=== 模板字符串基本语法 ===');
    
    const name = "Alice";
    const age = 30;
    const greeting = `Hello, ${name}!`;
    console.log(greeting);
    
    const a = 10;
    const b = 20;
    const result = `${a} + ${b} = ${a + b}`;
    console.log(result); // "10 + 20 = 30"
    
    // 函数调用
    const upper = str => str.toUpperCase();
    const message = `${upper("hello")} world!`;
    console.log(message); // "HELLO world!"
    
    // 三元表达式
    const userAge = 18;
    const status = `${userAge >= 18 ? "成年" : "未成年"}`;
    console.log(status); // "成年"
}

// 3.2 多行字符串
function multilineStrings() {
    console.log('\n=== 多行字符串 ===');
    
    const multiline = `
        第一行
        第二行
        第三行
    `;
    console.log(multiline);
}

// 3.3 高级用法
function advancedTemplateStrings() {
    console.log('\n=== 模板字符串高级用法 ===');
    
    // 嵌套模板字符串
    const user = {
        name: "Bob",
        age: 30,
        address: {
            city: "北京",
            country: "中国"
        }
    };
    
    const userInfo = `
        用户信息:
        姓名: ${user.name}
        年龄: ${user.age}
        地址: ${user.address.city}, ${user.address.country}
    `;
    console.log(userInfo);
    
    // 条件渲染
    function formatProduct(product) {
        return `
            <div class="product">
                <h3>${product.name}</h3>
                <p>价格: ¥${product.price}</p>
                ${product.discount ? 
                    `<p class="discount">折扣: ${product.discount}%</p>` : 
                    ''}
                ${product.inStock ? 
                    '<button class="buy">购买</button>' : 
                    '<button disabled>缺货</button>'}
            </div>
        `;
    }
    
    const product1 = { name: "手机", price: 2999, discount: 10, inStock: true };
    console.log(formatProduct(product1));
}

// 3.4 标签模板字符串
function taggedTemplates() {
    console.log('\n=== 标签模板字符串 ===');
    
    function highlight(strings, ...values) {
        return strings.reduce((result, str, i) => {
            const value = i < values.length ? values[i] : '';
            return `${result}${str}<mark>${value}</mark>`;
        }, '');
    }
    
    const user = { name: "Bob", age: 30 };
    const highlighted = highlight`用户: ${user.name}, 年龄: ${user.age}`;
    console.log(highlighted);
}

// ====================== 解构赋值 ======================

// 4.1 数组解构
function arrayDestructuring() {
    console.log('\n=== 数组解构 ===');
    
    // 基本数组解构
    const colors = ["red", "green", "blue"];
    const [firstColor, secondColor, thirdColor] = colors;
    console.log(firstColor, secondColor, thirdColor); // "red" "green" "blue"
    
    // 忽略某些元素
    const [, , third] = colors;
    console.log(third); // "blue"
    
    // 使用默认值
    const [a, b, c, d = "yellow"] = colors;
    console.log(d); // "yellow"
    
    // 剩余元素
    const [primary, ...rest] = colors;
    console.log(primary, rest); // "red" ["green", "blue"]
    
    // 交换变量
    let x = 10, y = 20;
    [x, y] = [y, x];
    console.log(x, y); // 20 10
}

// 4.2 对象解构
function objectDestructuring() {
    console.log('\n=== 对象解构 ===');
    
    const person = {
        name: "Alice",
        age: 30,
        job: "developer"
    };
    
    // 基本对象解构
    const { name, age } = person;
    console.log(name, age); // "Alice" 30
    
    // 重命名变量
    const { name: fullName, age: years } = person;
    console.log(fullName, years); // "Alice" 30
    
    // 默认值
    const { name: personName, salary = 50000 } = person;
    console.log(personName, salary); // "Alice" 50000
    
    // 嵌套对象解构
    const employee = {
        id: 123,
        personal: {
            name: "Bob",
            address: {
                city: "北京",
                street: "中关村"
            }
        }
    };
    
    const { 
        personal: { 
            name: empName, 
            address: { 
                city, 
                street 
            } 
        } 
    } = employee;
    
    console.log(empName, city, street); // "Bob" "北京" "中关村"
}

// 4.3 函数参数解构
function functionParameterDestructuring() {
    console.log('\n=== 函数参数解构 ===');
    
    // 对象参数解构
    function displayUser({ name, age, location = "未知" }) {
        console.log(`${name}, ${age}岁, 来自${location}`);
    }
    
    displayUser({ name: "Carol", age: 25, location: "上海" });
    displayUser({ name: "David", age: 30 });
    
    // 数组参数解构
    function getFirstAndLast([first, , last]) {
        return { first, last };
    }
    
    const coords = getFirstAndLast([10, 20, 30, 40]);
    console.log(coords); // {first: 10, last: 40}
}

// ====================== 扩展运算符和剩余参数 ======================

// 5.1 扩展运算符
function spreadOperator() {
    console.log('\n=== 扩展运算符 ===');
    
    // 数组扩展
    const arr1 = [1, 2, 3];
    const arr2 = [4, 5, 6];
    const combined = [...arr1, ...arr2];
    console.log(combined); // [1, 2, 3, 4, 5, 6]
    
    // 对象扩展
    const user = {
        name: "Alice",
        age: 30
    };
    
    const updatedUser = {
        ...user,
        email: "alice@example.com"
    };
    console.log(updatedUser);
    
    // 函数参数扩展
    function add(...numbers) {
        return numbers.reduce((sum, num) => sum + num, 0);
    }
    
    console.log(add(1, 2, 3)); // 6
}

// 5.2 剩余参数
function restParameters() {
    console.log('\n=== 剩余参数 ===');
    
    function sum(first, second, ...rest) {
        console.log(`第一个参数: ${first}`);
        console.log(`第二个参数: ${second}`);
        console.log(`剩余参数: [${rest}]`);
        return first + second + rest.reduce((acc, val) => acc + val, 0);
    }
    
    console.log(sum(1, 2, 3, 4, 5)); // 15
    
    // 解构中的剩余参数
    const [first, ...rest] = [1, 2, 3, 4, 5];
    console.log(first, rest); // 1 [2, 3, 4, 5]
    
    const { a, b, ...others } = { a: 1, b: 2, c: 3, d: 4 };
    console.log(others); // { c: 3, d: 4 }
}

// ====================== 对象字面量增强 ======================

// 6.1 属性简写
function objectShorthand() {
    console.log('\n=== 对象属性简写 ===');
    
    const name = "Alice";
    const age = 30;
    
    // ES6简写
    const person = {
        name,
        age,
        greet() {
            return `Hello, I'm ${this.name}`;
        }
    };
    
    console.log(person.greet()); // "Hello, I'm Alice"
}

// 6.2 计算属性名
function computedPropertyNames() {
    console.log('\n=== 计算属性名 ===');
    
    const propName = "dynamicProp";
    const value = "dynamic value";
    
    const obj = {
        [propName]: value,
        ["computed" + "Prop"]: "computed value"
    };
    
    console.log(obj.dynamicProp); // "dynamic value"
    console.log(obj.computedProp); // "computed value"
    
    // 实际应用：基于条件创建属性
    function createObject(includeExtra) {
        const base = {
            id: 1,
            name: "基础对象"
        };
        
        return {
            ...base,
            ...(includeExtra ? { extra: "额外属性" } : {})
        };
    }
    
    const obj1 = createObject(true);
    const obj2 = createObject(false);
    
    console.log(obj1); // { id: 1, name: "基础对象", extra: "额外属性" }
    console.log(obj2); // { id: 1, name: "基础对象" }
}

// 6.3 方法定义和super
function objectMethodsAndSuper() {
    console.log('\n=== 对象方法定义和super ===');
    
    // 继承和super
    const parent = {
        greet() {
            return "Hello from parent";
        }
    };
    
    const child = {
        // 设置原型
        __proto__: parent,
        
        greet() {
            // 调用父类方法
            return super.greet() + " and from child";
        }
    };
    
    console.log(child.greet()); // "Hello from parent and from child"
}

// ====================== 新的数据结构 ======================

// 7.1 Symbol
function symbolBasics() {
    console.log('\n=== Symbol基础 ===');
    
    // 创建Symbol
    const sym1 = Symbol();
    const sym2 = Symbol("description");
    const sym3 = Symbol("description");
    
    console.log(sym1 === sym2); // false
    console.log(sym2 === sym3); // false
    console.log(sym2.description); // "description"
    console.log(sym3.description); // "description"
    
    // Symbol作为对象属性
    const idSymbol = Symbol("id");
    const user = {
        name: "Alice",
        [idSymbol]: 12345
    };
    
    console.log(user[idSymbol]); // 12345
    console.log(Object.keys(user)); // ["name"]
    console.log(Object.getOwnPropertySymbols(user)); // [Symbol(id)]
}

// 7.2 Set
function setOperations() {
    console.log('\n=== Set操作 ===');
    
    // 创建Set
    const set1 = new Set();
    const set2 = new Set([1, 2, 3, 3, 4]); // 自动去重
    console.log(set2); // Set {1, 2, 3, 4}
    
    // Set操作
    set1.add("a");
    set1.add("b");
    set1.add("a"); // 重复添加不会生效
    console.log(set1.has("b")); // true
    console.log(set1.size); // 2
    
    // 数组去重
    const arr = [1, 2, 2, 3, 4, 4, 5];
    const uniqueArr = [...new Set(arr)];
    console.log(uniqueArr); // [1, 2, 3, 4, 5]
    
    // 集合操作
    const setA = new Set([1, 2, 3]);
    const setB = new Set([3, 4, 5]);
    
    const union = new Set([...setA, ...setB]);
    console.log("并集:", [...union]); // [1, 2, 3, 4, 5]
    
    const intersection = new Set([...setA].filter(x => setB.has(x)));
    console.log("交集:", [...intersection]); // [3]
    
    const difference = new Set([...setA].filter(x => !setB.has(x)));
    console.log("差集(A-B):", [...difference]); // [1, 2]
}

// 7.3 Map
function mapOperations() {
    console.log('\n=== Map操作 ===');
    
    // 创建Map
    const map1 = new Map();
    const map2 = new Map([
        ["key1", "value1"],
        ["key2", "value2"]
    ]);
    
    // 设置和获取值
    map1.set("name", "Alice");
    map1.set("age", 30);
    
    console.log(map1.get("name")); // "Alice"
    console.log(map1.has("age")); // true
    console.log(map1.size); // 2
    
    // 遍历Map
    for (const [key, value] of map1) {
        console.log(`${key}: ${value}`);
    }
    
    // 实际应用：缓存
    const cache = new Map();
    
    function expensiveOperation(input) {
        if (cache.has(input)) {
            console.log("从缓存获取结果");
            return cache.get(input);
        }
        
        console.log("执行耗时操作...");
        const result = input * input;
        cache.set(input, result);
        return result;
    }
    
    console.log(expensiveOperation(5)); // 执行计算
    console.log(expensiveOperation(5)); // 从缓存获取
    console.log(expensiveOperation(10)); // 执行计算
    console.log(expensiveOperation(10)); // 从缓存获取
}

// ====================== 迭代器和生成器 ======================

// 8.1 迭代器
function iterators() {
    console.log('\n=== 迭代器 ===');
    
    // 获取数组的迭代器
    const myArray = ["a", "b", "c"];
    const iterator = myArray[Symbol.iterator]();
    
    // 手动迭代
    console.log(iterator.next()); // { value: "a", done: false }
    console.log(iterator.next()); // { value: "b", done: false }
    console.log(iterator.next()); // { value: "c", done: false }
    console.log(iterator.next()); // { value: undefined, done: true }
    
    // 实现自定义迭代器
    const range = {
        start: 1,
        end: 5,
        
        [Symbol.iterator]() {
            let current = this.start;
            const end = this.end;
            
            return {
                next() {
                    if (current <= end) {
                        return { value: current++, done: false };
                    } else {
                        return { done: true };
                    }
                }
            };
        }
    };
    
    for (const num of range) {
        console.log(num); // 1, 2, 3, 4, 5
    }
}

// 8.2 生成器
function generators() {
    console.log('\n=== 生成器 ===');
    
    // 基本生成器
    function* simpleGenerator() {
        yield 1;
        yield 2;
        yield 3;
    }
    
    for (const value of simpleGenerator()) {
        console.log(value); // 1, 2, 3
    }
    
    // 有限斐波那契数列
    function* limitedFibonacci(count) {
        let [prev, curr] = [0, 1];
        
        for (let i = 0; i < count; i++) {
            yield curr;
            [prev, curr] = [curr, prev + curr];
        }
    }
    
    console.log("前10个斐波那契数:");
    for (const num of limitedFibonacci(10)) {
        console.log(num);
    }
    
    // 生成器处理树形结构遍历
    class TreeNode {
        constructor(value, children = []) {
            this.value = value;
            this.children = children;
        }
        
        // 使用生成器实现深度优先遍历
        *[Symbol.iterator]() {
            yield this.value;
            
            for (const child of this.children) {
                yield* child;
            }
        }
    }
    
    // 构建树
    const tree = new TreeNode(1, [
        new TreeNode(2, [
            new TreeNode(4),
            new TreeNode(5)
        ]),
        new TreeNode(3, [
            new TreeNode(6),
            new TreeNode(7)
        ])
    ]);
    
    console.log("深度优先遍历树:");
    for (const value of tree) {
        console.log(value); // 1, 2, 4, 5, 3, 6, 7
    }
}

// ====================== 类与继承 ======================

// 9.1 基本类定义
function classBasics() {
    console.log('\n=== 类的基本定义 ===');
    
    class Person {
        // 构造函数
        constructor(name, age) {
            this.name = name;
            this.age = age;
        }
        
        // 实例方法
        greet() {
            return `Hello, I'm ${this.name}`;
        }
        
        // 获取器
        get info() {
            return `${this.name} is ${this.age} years old`;
        }
        
        // 静态方法
        static createAdult(name) {
            return new Person(name, 18);
        }
    }
    
    const alice = new Person("Alice", 30);
    console.log(alice.greet()); // "Hello, I'm Alice"
    console.log(alice.info); // "Alice is 30 years old"
    
    const bob = Person.createAdult("Bob");
    console.log(bob.age); // 18
    
    // 表达式形式定义类
    const MyClass = class MyInnerClass {
        constructor(value) {
            this.value = value;
        }
        
        getValue() {
            return this.value;
        }
    };
    
    const instance = new MyClass("类表达式");
    console.log(instance.getValue()); // "类表达式"
}

// 9.2 继承
function classInheritance() {
    console.log('\n=== 类继承 ===');
    
    // 基类
    class Animal {
        constructor(name) {
            this.name = name;
        }
        
        speak() {
            return `${this.name} makes a sound`;
        }
    }
    
    // 子类
    class Dog extends Animal {
        constructor(name, breed) {
            // 调用父类构造函数
            super(name);
            this.breed = breed;
        }
        
        // 重写父类方法
        speak() {
            return `${this.name} barks`;
        }
        
        // 新增方法
        fetch() {
            return `${this.name} is fetching`;
        }
    }
    
    const myDog = new Dog("Rex", "Golden Retriever");
    console.log(myDog.speak()); // "Rex barks"
    console.log(myDog.fetch()); // "Rex is fetching"
    
    // 调用父类方法
    class Cat extends Animal {
        speak() {
            // 使用super调用父类方法
            return super.speak() + " and purrs";
        }
    }
    
    const myCat = new Cat("Whiskers");
    console.log(myCat.speak()); // "Whiskers makes a sound and purrs"
}

// 9.3 高级类特性
function advancedClassFeatures() {
    console.log('\n=== 类的高级特性 ===');
    
    // 私有字段（ES2022）
    class BankAccount {
        // 私有字段以#开头
        #balance = 0;
        #owner;
        
        constructor(owner, initialBalance = 0) {
            this.#owner = owner;
            this.#balance = initialBalance;
        }
        
        deposit(amount) {
            if (amount <= 0) {
                throw new Error("存款金额必须大于0");
            }
            this.#balance += amount;
            return this.#balance;
        }
        
        get balance() {
            return this.#balance;
        }
        
        get owner() {
            return this.#owner;
        }
    }
    
    const account = new BankAccount("Alice", 1000);
    console.log(account.deposit(500)); // 1500
    console.log(account.balance); // 1500
    // console.log(account.#balance); // SyntaxError: Private field '#balance' must be declared in an enclosing class
    
    // 静态字段和方法
    class MathUtils {
        // 静态字段（ES2022）
        static PI = 3.14159;
        
        // 静态方法
        static circleArea(radius) {
            return (MathUtils.PI * radius * radius).toFixed(2);
        }
    }
    
    console.log(MathUtils.circleArea(5)); // "78.54"
    
    // 混入模式
    const canEat = {
        eat(food) {
            console.log(`${this.name} is eating ${food}`);
        }
    };
    
    const canWalk = {
        walk(distance) {
            console.log(`${this.name} walked ${distance} meters`);
        }
    };
    
    class Person {
        constructor(name) {
            this.name = name;
        }
    }
    
    // 使用Object.assign将混入应用到原型
    Object.assign(Person.prototype, canEat, canWalk);
    
    const john = new Person("John");
    john.eat("apple"); // "John is eating apple"
    john.walk(100); // "John walked 100 meters"
}

// ====================== 实际应用示例 ======================

// 10.1 用户卡片生成
function generateUserCards() {
    console.log('\n=== 用户卡片生成 ===');
    
    const users = [
        { id: 1, name: "张三", email: "zhangsan@example.com", avatar: "Z" },
        { id: 2, name: "李四", email: "lisi@example.com", avatar: "L" },
        { id: 3, name: "王五", email: "wangwu@example.com", avatar: "W" }
    ];
    
    // 使用ES6+特性生成用户卡片HTML
    const userCardsHTML = users.map(({ id, name, email, avatar }) => `
        <div class="user-card">
            <div class="user-avatar">${avatar}</div>
            <div>
                <h3>${name}</h3>
                <p>${email}</p>
            </div>
        </div>
    `).join('');
    
    console.log('用户卡片HTML:');
    console.log(userCardsHTML);
}

// 10.2 商品展示
function displayProducts() {
    console.log('\n=== 商品展示 ===');
    
    const products = [
        { 
            id: 1, 
            name: "智能手机", 
            price: 2999, 
            discount: 10, 
            inStock: true,
            description: "最新款智能手机，高性能处理器"
        },
        { 
            id: 2, 
            name: "无线耳机", 
            price: 299, 
            discount: null, 
            inStock: true,
            description: "高音质无线蓝牙耳机"
        },
        { 
            id: 3, 
            name: "智能手表", 
            price: 1299, 
            discount: 15, 
            inStock: false,
            description: "多功能智能手表，支持健康监测"
        }
    ];
    
    // 使用ES6+特性生成商品展示HTML
    const productsHTML = products.map(product => {
        const { id, name, price, discount, inStock, description } = product;
        const finalPrice = discount ? price * (1 - discount / 100) : price;
        
        return `
            <div class="product">
                <h3 class="product-title">${name}</h3>
                <p>${description}</p>
                <p class="product-price">
                    ¥${finalPrice.toFixed(2)}
                    ${discount ? `<span class="product-discount">省${(price - finalPrice).toFixed(2)}</span>` : ''}
                </p>
                <div class="product-stock ${inStock ? 'status-ok' : 'status-error'}">
                    ${inStock ? '✓ 有货' : '✗ 缺货'}
                </div>
            </div>
        `;
    }).join('');
    
    console.log('商品展示HTML:');
    console.log(productsHTML);
}

// 10.3 计算器实现
function implementCalculator() {
    console.log('\n=== 计算器实现 ===');
    
    class Calculator {
        constructor() {
            this.value = 0;
            this.previousValue = null;
            this.operation = null;
            this.waitingForNewValue = false;
        }
        
        inputDigit(digit) {
            if (this.waitingForNewValue) {
                this.value = 0;
                this.waitingForNewValue = false;
            }
            
            this.value = this.value * 10 + digit;
            return this.updateDisplay();
        }
        
        inputOperation(op) {
            const inputValue = this.value;
            
            if (this.previousValue === null) {
                this.previousValue = inputValue;
            } else if (this.operation) {
                const currentValue = this.previousValue || 0;
                const newValue = this.calculate(currentValue, inputValue, this.operation);
                
                this.value = newValue;
                this.previousValue = newValue;
            }
            
            this.waitingForNewValue = true;
            this.operation = op;
            return this.updateDisplay();
        }
        
        calculate(firstValue, secondValue, operation) {
            switch (operation) {
                case '+': return firstValue + secondValue;
                case '-': return firstValue - secondValue;
                case '×': return firstValue * secondValue;
                case '÷': return secondValue !== 0 ? firstValue / secondValue : 0;
                default: return secondValue;
            }
        }
        
        clear() {
            this.value = 0;
            this.previousValue = null;
            this.operation = null;
            this.waitingForNewValue = false;
            return this.updateDisplay();
        }
        
        updateDisplay() {
            return this.value;
        }
    }
    
    // 使用计算器
    const calc = new Calculator();
    
    // 计算 12 + 34 = 46
    calc.inputDigit(1);
    calc.inputDigit(2);
    calc.inputOperation('+');
    calc.inputDigit(3);
    calc.inputDigit(4);
    calc.inputOperation('=');
    
    console.log(`计算结果: ${calc.value}`); // 46
    
    // 清除并计算 5 × 6 = 30
    calc.clear();
    calc.inputDigit(5);
    calc.inputOperation('×');
    calc.inputDigit(6);
    calc.inputOperation('=');
    
    console.log(`计算结果: ${calc.value}`); // 30
}

// ====================== 运行所有示例 ======================

function runAllExamples() {
    compareVarLetConst();
    temporalDeadZone();
    loopScope();
    
    arrowFunctionBasics();
    arrowFunctionThis();
    arrowFunctionApplications();
    
    templateStringBasics();
    multilineStrings();
    advancedTemplateStrings();
    taggedTemplates();
    
    arrayDestructuring();
    objectDestructuring();
    functionParameterDestructuring();
    
    spreadOperator();
    restParameters();
    
    objectShorthand();
    computedPropertyNames();
    objectMethodsAndSuper();
    
    symbolBasics();
    setOperations();
    mapOperations();
    
    iterators();
    generators();
    
    classBasics();
    classInheritance();
    advancedClassFeatures();
    
    generateUserCards();
    displayProducts();
    implementCalculator();
}

// 导出主要函数以便测试
module.exports = {
    runAllExamples
};