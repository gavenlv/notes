// 第10章：ES6+新特性与最佳实践 - 代码示例

// ===== 10.1 ES2016-ES2022新特性 =====

// 10.1.1 ES2016 (ECMAScript 7)

// Array.prototype.includes()
console.log('=== Array.prototype.includes() ===');
const fruits = ['apple', 'banana', 'orange'];
console.log(fruits.includes('banana')); // true
console.log(fruits.includes('grape')); // false
console.log([NaN].includes(NaN)); // true
console.log([NaN].indexOf(NaN)); // -1

// 指数运算符 (**)
console.log('\n=== 指数运算符 ===');
console.log(2 ** 3); // 8
let x = 2;
x **= 3;
console.log(x); // 8

// 10.1.2 ES2017 (ECMAScript 8)

// async/await
console.log('\n=== async/await ===');
// 模拟API请求
function fetch(url) {
    return new Promise(resolve => {
        setTimeout(() => {
            if (url.includes('users')) {
                resolve({
                    json: () => Promise.resolve({ id: 1, name: '张三' })
                });
            } else if (url.includes('posts')) {
                resolve({
                    json: () => Promise.resolve([{ id: 1, title: '文章1' }, { id: 2, title: '文章2' }])
                });
            }
        }, 500);
    });
}

// 使用Promise链
function fetchUserData(userId) {
    return fetch(`/api/users/${userId}`)
        .then(response => response.json())
        .then(user => {
            return fetch(`/api/posts/${user.id}`)
                .then(response => response.json())
                .then(posts => ({ user, posts }));
        });
}

// 使用async/await
async function fetchUserDataAsync(userId) {
    const userResponse = await fetch(`/api/users/${userId}`);
    const user = await userResponse.json();
    
    const postsResponse = await fetch(`/api/posts/${user.id}`);
    const posts = await postsResponse.json();
    
    return { user, posts };
}

// 测试
fetchUserData(1).then(result => console.log('Promise链结果:', result));
fetchUserDataAsync(1).then(result => console.log('async/await结果:', result));

// Object.values()
console.log('\n=== Object.values() ===');
const person = {
    name: '张三',
    age: 30,
    job: '工程师'
};
console.log(Object.values(person)); // ['张三', 30, '工程师']

// Object.entries()
console.log('\n=== Object.entries() ===');
console.log(Object.entries(person));
Object.entries(person).forEach(([key, value]) => {
    console.log(`${key}: ${value}`);
});

// String.prototype.padStart() 和 String.prototype.padEnd()
console.log('\n=== String padding ===');
console.log('7'.padStart(2, '0')); // '07'
console.log('hello'.padStart(10, '*')); // '*****hello'
console.log('7'.padEnd(2, '0')); // '70'
console.log('hello'.padEnd(10, '*')); // 'hello*****'

// 格式化数字
const formatNumber = (num) => num.toString().padStart(5, '0');
console.log(formatNumber(42)); // '00042'

// 10.1.3 ES2018 (ECMAScript 9)

// 异步迭代
console.log('\n=== 异步迭代 ===');
const asyncIterable = {
    [Symbol.asyncIterator]() {
        let i = 0;
        return {
            next() {
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve({
                            value: i++,
                            done: i > 3
                        });
                    }, 100);
                });
            }
        };
    }
};

// 使用for-await-of循环
(async function() {
    console.log('开始异步迭代:');
    for await (const num of asyncIterable) {
        console.log(num);
    }
})();

// Promise.prototype.finally()
console.log('\n=== Promise.prototype.finally() ===');
function simulateApiCall(success) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (success) {
                resolve('数据加载成功');
            } else {
                reject('数据加载失败');
            }
        }, 500);
    });
}

simulateApiCall(true)
    .then(result => console.log('成功:', result))
    .catch(error => console.log('错误:', error))
    .finally(() => console.log('请求完成'));

// 对象休息/展开属性
console.log('\n=== 对象休息/展开属性 ===');
const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3 };
console.log(obj2); // { a: 1, b: 2, c: 3 }

const { a, ...rest } = obj2;
console.log(a); // 1
console.log(rest); // { b: 2, c: 3 }

// 10.1.4 ES2019 (ECMAScript 10)

// Array.prototype.flat() 和 Array.prototype.flatMap()
console.log('\n=== Array flat 和 flatMap ===');
const nestedArray = [1, [2, 3], [4, [5]]];
console.log(nestedArray.flat()); // [1, 2, 3, 4, [5]]
console.log(nestedArray.flat(2)); // [1, 2, 3, 4, 5]

const sentences = [
    '这是一个句子',
    '这是另一个句子',
    '还有第三个句子'
];
const words = sentences.flatMap(sentence => sentence.split(' '));
console.log(words); // ['这是一个', '句子', '这是', '另一个', '句子', '还有', '第三个', '句子']

// Object.fromEntries()
console.log('\n=== Object.fromEntries() ===');
const entries = [
    ['name', '张三'],
    ['age', 30],
    ['job', '工程师']
];
const obj = Object.fromEntries(entries);
console.log(obj); // { name: '张三', age: 30, job: '工程师' }

// String.prototype.trimStart() 和 String.prototype.trimEnd()
console.log('\n=== String trimStart 和 trimEnd ===');
const str = '  hello world  ';
console.log(str.trimStart()); // 'hello world  '
console.log(str.trimEnd()); // '  hello world'
console.log(str.trim()); // 'hello world'

// 可选的catch绑定
console.log('\n=== 可选的catch绑定 ===');
try {
    // 可能出错的代码
    JSON.parse('invalid json');
} catch {
    console.log('发生错误，但没有使用错误参数');
}

// 10.1.5 ES2020 (ECMAScript 11)

// 可选链操作符 (?.)
console.log('\n=== 可选链操作符 ===');
const user = {
    name: '张三',
    address: {
        city: '北京'
    }
};

const city = user?.address?.city;
console.log(city); // '北京'

const zipCode = user?.address?.zipCode;
console.log(zipCode); // undefined

// 空值合并运算符 (??)
console.log('\n=== 空值合并运算符 ===');
const settings = {
    port: 0,
    timeout: null,
    retries: undefined
};

const port = settings.port ?? 3000;
console.log(port); // 0 (0不是null或undefined)

const timeout = settings.timeout ?? 5000;
console.log(timeout); // 5000 (null触发默认值)

const retries = settings.retries ?? 3;
console.log(retries); // 3 (undefined触发默认值)

// BigInt
console.log('\n=== BigInt ===');
const bigIntValue = 9007199254740991n;
console.log(bigIntValue + 1n); // 9007199254740992n

// String.prototype.matchAll()
console.log('\n=== String.prototype.matchAll() ===');
const regex = /t(e)(st(\d?))/g;
const str2 = 'test1test2';
const matches = str2.matchAll(regex);

for (const match of matches) {
    console.log(match);
}

// 10.1.6 ES2021 (ECMAScript 12)

// String.prototype.replaceAll()
console.log('\n=== String.prototype.replaceAll() ===');
const message = 'apple, banana, apple, orange';
const newMessage = message.replaceAll('apple', 'grape');
console.log(newMessage); // 'grape, banana, grape, orange'

// Promise.any()
console.log('\n=== Promise.any() ===');
const promise1 = Promise.reject('失败1');
const promise2 = Promise.reject('失败2');
const promise3 = Promise.resolve('成功');

Promise.any([promise1, promise2, promise3])
    .then(result => console.log('Promise.any结果:', result))
    .catch(error => console.log('所有Promise都失败:', error));

// 逻辑赋值运算符
console.log('\n=== 逻辑赋值运算符 ===');
let x1 = 0;
x1 ||= 5;
console.log(x1); // 5

let y1 = 5;
y1 &&= 0;
console.log(y1); // 0

let z1 = null;
z1 ??= 10;
console.log(z1); // 10

// 数字分隔符
console.log('\n=== 数字分隔符 ===');
const billion = 1_000_000_000;
const bytes = 0b1111_1111;
const hex = 0xFF_FF_FF_FF;

console.log(billion); // 1000000000
console.log(bytes); // 255
console.log(hex); // 4294967295

// 10.1.7 ES2022 (ECMAScript 13)

// 类字段
console.log('\n=== 类字段 ===');
class Person {
    // 公共字段
    name = '未知';
    age = 0;
    
    // 私有字段（以#开头）
    #id = Math.random().toString(36).substr(2, 9);
    #secret = '这是一个秘密';
    
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    // 私有方法
    #getSecret() {
        return this.#secret;
    }
    
    // 公共方法可以访问私有字段和方法
    getInfo() {
        return `${this.name} (ID: ${this.#id}): ${this.#getSecret()}`;
    }
}

const person2 = new Person('张三', 30);
console.log(person2.getInfo()); // '张三 (ID: abc123): 这是一个秘密'

// Array.prototype.at()
console.log('\n=== Array.prototype.at() ===');
const arr = ['a', 'b', 'c', 'd', 'e'];
console.log(arr.at(0)); // 'a'
console.log(arr.at(2)); // 'c'
console.log(arr.at(-1)); // 'e' (最后一个元素)
console.log(arr.at(-2)); // 'd' (倒数第二个元素)

// Object.hasOwn()
console.log('\n=== Object.hasOwn() ===');
const obj3 = { name: '张三' };
const objWithNullProto = Object.create(null);
objWithNullProto.name = '李四';

console.log(Object.hasOwn(obj3, 'name')); // true
console.log(Object.hasOwn(objWithNullProto, 'name')); // true

// Error对象的cause属性
console.log('\n=== Error对象的cause属性 ===');
try {
    try {
        JSON.parse('invalid json');
    } catch (error) {
        throw new Error('处理数据失败', { cause: error });
    }
} catch (error) {
    console.log(error.message); // '处理数据失败'
    console.log(error.cause.message); // 'Unexpected token i in JSON at position 0'
}

// ===== 10.2 性能优化技巧 =====

// 防抖和节流
console.log('\n=== 防抖和节流 ===');
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function throttle(func, interval) {
    let lastTime = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastTime >= interval) {
            func.apply(this, args);
            lastTime = now;
        }
    };
}

// 使用示例
const debouncedSearch = debounce((query) => {
    console.log('搜索:', query);
}, 300);

const throttledScroll = throttle(() => {
    console.log('滚动事件处理');
}, 100);

// 模拟搜索输入
debouncedSearch('a');
debouncedSearch('ap');
debouncedSearch('app');
setTimeout(() => debouncedSearch('apple'), 400);

// 模拟滚动事件
for (let i = 0; i < 5; i++) {
    throttledScroll();
}

// ===== 10.3 代码风格与最佳实践 =====

// 使用现代JavaScript特性
console.log('\n=== 使用现代JavaScript特性 ===');
function processUser(user) {
    // 使用解构赋值
    const { name, age, email } = user;
    console.log(`用户: ${name}, 年龄: ${age}, 邮箱: ${email}`);
    
    // 使用展开运算符更新对象
    const updatedUser = { ...user, lastLogin: new Date() };
    console.log('更新后的用户:', updatedUser);
}

processUser({ name: '张三', age: 30, email: 'zhangsan@example.com' });

// 函数式编程原则
console.log('\n=== 函数式编程原则 ===');
const numbers = [1, 2, 3, 4, 5];

// 使用map和filter
const doubled = numbers.map(n => n * 2);
const evenNumbers = numbers.filter(n => n % 2 === 0);
console.log('原数组:', numbers);
console.log('翻倍:', doubled);
console.log('偶数:', evenNumbers);

// 函数组合
const compose = (f, g) => x => f(g(x));
const addOne = x => x + 1;
const double = x => x * 2;
const addOneThenDouble = compose(double, addOne);
console.log('先加1再翻倍:', addOneThenDouble(3)); // 8

// ===== 10.4 实战项目案例 =====

// 现代化待办事项应用
console.log('\n=== 现代化待办事项应用 ===');
class TodoApp {
    constructor() {
        this.todos = JSON.parse(localStorage.getItem('todos')) || [];
        this.filter = 'all'; // all, active, completed
        this.nextId = this.todos.length > 0 ? Math.max(...this.todos.map(t => parseInt(t.id))) + 1 : 1;
    }
    
    addTodo(text) {
        const todo = {
            id: this.nextId++,
            text,
            completed: false,
            createdAt: new Date().toISOString()
        };
        
        this.todos = [...this.todos, todo];
        this.saveTodos();
        return todo;
    }
    
    toggleTodo(id) {
        this.todos = this.todos.map(todo =>
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        );
        this.saveTodos();
    }
    
    deleteTodo(id) {
        this.todos = this.todos.filter(todo => todo.id !== id);
        this.saveTodos();
    }
    
    setFilter(filter) {
        this.filter = filter;
    }
    
    getFilteredTodos() {
        switch (this.filter) {
            case 'active':
                return this.todos.filter(todo => !todo.completed);
            case 'completed':
                return this.todos.filter(todo => todo.completed);
            default:
                return this.todos;
        }
    }
    
    getStats() {
        const total = this.todos.length;
        const completed = this.todos.filter(todo => todo.completed).length;
        const active = total - completed;
        
        return { total, completed, active };
    }
    
    saveTodos() {
        localStorage.setItem('todos', JSON.stringify(this.todos));
    }
}

// 使用示例
const todoApp = new TodoApp();
console.log('添加待办事项:', todoApp.addTodo('学习ES6+新特性'));
console.log('添加待办事项:', todoApp.addTodo('完成项目'));
console.log('所有待办事项:', todoApp.getFilteredTodos());

todoApp.toggleTodo(1);
console.log('切换第一个待办事项状态后:', todoApp.getFilteredTodos());

todoApp.setFilter('completed');
console.log('已完成的待办事项:', todoApp.getFilteredTodos());

console.log('统计信息:', todoApp.getStats());

// ===== 10.5 常见问题与解决方案 =====

// 异步操作问题：使用async/await避免回调地狱
console.log('\n=== 异步操作问题解决方案 ===');
async function fetchData() {
    try {
        const a = await new Promise(resolve => setTimeout(() => resolve('数据A'), 300));
        const b = await new Promise(resolve => setTimeout(() => resolve('数据B'), 200));
        const c = await new Promise(resolve => setTimeout(() => resolve('数据C'), 100));
        console.log('获取的数据:', { a, b, c });
        return { a, b, c };
    } catch (error) {
        console.error('获取数据失败:', error);
        return null;
    }
}

fetchData();

// this绑定问题：使用箭头函数
console.log('\n=== this绑定问题解决方案 ===');
const obj = {
    name: '张三',
    greet: function() {
        console.log(`Hello, ${this.name}`);
        
        // 使用箭头函数
        setTimeout(() => {
            console.log(`Goodbye, ${this.name}`); // this继承自外层作用域
        }, 100);
    }
};

obj.greet();

// 内存泄漏问题：提供清理方法
console.log('\n=== 内存泄漏问题解决方案 ===');
class Component {
    constructor() {
        this.data = new Array(100).fill(0);
        
        // 绑定方法并保存引用
        this.handleResize = this.handleResize.bind(this);
        this.updateData = this.updateData.bind(this);
        
        // 添加事件监听器
        window.addEventListener('resize', this.handleResize);
        
        // 设置定时器
        this.timer = setInterval(this.updateData, 1000);
        
        console.log('组件已创建');
    }
    
    handleResize() {
        console.log('处理窗口大小变化');
    }
    
    updateData() {
        console.log('更新数据');
    }
    
    // 提供清理方法
    destroy() {
        // 移除事件监听器
        window.removeEventListener('resize', this.handleResize);
        
        // 清除定时器
        clearInterval(this.timer);
        
        // 清空数据
        this.data = null;
        
        console.log('组件已销毁');
    }
}

// 使用示例
const component = new Component();
setTimeout(() => component.destroy(), 3000);

// 性能问题：批量操作DOM
console.log('\n=== 性能问题解决方案 ===');
function addItems(count) {
    // 创建文档片段
    const fragment = document.createDocumentFragment();
    
    for (let i = 0; i < count; i++) {
        const item = document.createElement('div');
        item.textContent = `Item ${i}`;
        fragment.appendChild(item);
    }
    
    // 一次性添加到DOM
    // document.body.appendChild(fragment);
    console.log(`创建了${count}个DOM元素，使用文档片段一次性添加`);
}

addItems(10);

console.log('\n=== 第10章示例代码结束 ===');