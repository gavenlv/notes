# 第6章：异步编程与Promise

## 1. 异步编程基础

### 1.1 同步与异步

在JavaScript中，代码执行有两种方式：同步和异步。

**同步（Synchronous）**：代码按照顺序逐行执行，前一行代码执行完毕后才会执行下一行代码。如果某行代码执行时间长，会阻塞后续代码的执行。

**异步（Asynchronous）**：不会等待代码执行完成，而是继续执行后续代码。当异步操作完成时，通过回调函数处理结果。

```javascript
// 同步代码示例
console.log("开始");
console.log("中间");
console.log("结束");
// 输出: 开始 -> 中间 -> 结束

// 异步代码示例
console.log("开始");
setTimeout(function() {
    console.log("异步操作");
}, 1000);
console.log("结束");
// 输出: 开始 -> 结束 -> 异步操作（1秒后）
```

### 1.2 为什么需要异步编程

JavaScript是单线程语言，一次只能做一件事。如果所有操作都是同步的，长时间运行的操作（如网络请求、文件操作、定时器等）会阻塞整个程序，导致界面无响应。

```javascript
// 模拟长时间运行的操作
console.log("开始");

// 模拟耗时2秒的操作
const start = new Date().getTime();
while (new Date().getTime() - start < 2000) {
    // 空循环，模拟耗时操作
}
console.log("耗时操作完成");

console.log("结束");
// 这期间整个程序会被阻塞，无法响应其他操作
```

异步编程允许我们在等待长时间操作完成时继续执行其他代码，提高程序的响应性和效率。

### 1.3 异步编程的应用场景

1. **网络请求**：从服务器获取数据
2. **文件操作**：读取或写入文件
3. **定时器**：setTimeout、setInterval
4. **用户交互**：等待用户点击或输入
5. **动画**：CSS动画或JavaScript动画
6. **数据库操作**：查询或更新数据库
7. **Web API**：调用浏览器提供的API

## 2. 回调函数

### 2.1 回调函数基础

回调函数是作为参数传递给另一个函数的函数，在外部函数执行完毕后被调用执行。

```javascript
// 基本回调函数
function greeting(name, callback) {
    console.log(`Hello, ${name}!`);
    callback();
}

greeting("Alice", function() {
    console.log("回调函数被调用");
});
// 输出: Hello, Alice!
//      回调函数被调用
```

### 2.2 异步回调

在异步操作中，回调函数用于处理操作完成后的结果。

```javascript
// 使用setTimeout演示异步回调
console.log("开始");

setTimeout(function() {
    console.log("异步操作完成");
}, 1000);

console.log("结束");
// 输出: 开始 -> 结束 -> 异步操作完成（1秒后）
```

### 2.3 回调地狱

当多个异步操作需要依次执行时，嵌套的回调函数会形成"回调地狱"，代码难以阅读和维护。

```javascript
// 回调地狱示例
getData(function(a) {
    getMoreData(a, function(b) {
        getMoreData(b, function(c) {
            getMoreData(c, function(d) {
                getMoreData(d, function(e) {
                    console.log("最终结果: " + e);
                });
            });
        });
    });
});

// 这种代码难以阅读和维护，错误处理也很复杂
```

### 2.4 回调函数的错误处理

在回调模式中，通常使用第一个参数传递错误对象。

```javascript
function fetchData(callback) {
    // 模拟可能失败的异步操作
    setTimeout(function() {
        const success = Math.random() > 0.5; // 50%的成功率
        
        if (success) {
            callback(null, { id: 1, name: "数据" });
        } else {
            callback(new Error("获取数据失败"));
        }
    }, 1000);
}

fetchData(function(error, data) {
    if (error) {
        console.error("错误:", error.message);
        return;
    }
    
    console.log("数据:", data);
});
```

## 3. Promise基础

### 3.1 什么是Promise

Promise是异步编程的一种解决方案，它是一个对象，表示异步操作的最终完成或失败，以及其结果值。

Promise有三种状态：

1. **pending（待定）**：初始状态，既不是成功，也不是失败。
2. **fulfilled（已成功）**：操作成功完成。
3. **rejected（已失败）**：操作失败。

状态一旦改变，就不可再次改变。

### 3.2 创建Promise

使用`Promise`构造函数创建Promise实例：

```javascript
const promise = new Promise(function(resolve, reject) {
    // 异步操作
    setTimeout(function() {
        const success = Math.random() > 0.5;
        
        if (success) {
            resolve("操作成功");
        } else {
            reject(new Error("操作失败"));
        }
    }, 1000);
});
```

### 3.3 使用Promise

使用`then()`方法处理Promise成功的结果，使用`catch()`方法处理失败的结果。

```javascript
promise
    .then(function(result) {
        console.log("成功:", result);
    })
    .catch(function(error) {
        console.error("失败:", error.message);
    });
```

### 3.4 Promise链

`then()`方法返回一个新的Promise，可以链式调用。

```javascript
fetchData()
    .then(function(data) {
        console.log("第一步:", data);
        return processData(data); // 返回一个新的Promise
    })
    .then(function(result) {
        console.log("第二步:", result);
        return saveData(result); // 返回一个新的Promise
    })
    .then(function(finalResult) {
        console.log("最终结果:", finalResult);
    })
    .catch(function(error) {
        console.error("错误:", error.message);
    });
```

### 3.5 Promise的静态方法

#### 3.5.1 Promise.resolve()

创建一个已解决的Promise。

```javascript
const resolvedPromise = Promise.resolve("成功的结果");
resolvedPromise.then(result => console.log(result)); // "成功的结果"

// Promise.resolve可以包装非Promise值
const value = "普通值";
const wrappedPromise = Promise.resolve(value);
wrappedPromise.then(result => console.log(result)); // "普通值"
```

#### 3.5.2 Promise.reject()

创建一个已拒绝的Promise。

```javascript
const rejectedPromise = Promise.reject(new Error("失败的原因"));
rejectedPromise.catch(error => console.error(error.message)); // "失败的原因"
```

#### 3.5.3 Promise.all()

等待所有Promise完成，如果任何一个Promise失败，则整个Promise失败。

```javascript
const promise1 = Promise.resolve(3);
const promise2 = new Promise(resolve => setTimeout(() => resolve(5), 1000));
const promise3 = Promise.resolve(10);

Promise.all([promise1, promise2, promise3])
    .then(values => {
        console.log(values); // [3, 5, 10] (promise2需要1秒完成)
    })
    .catch(error => {
        console.error("至少一个Promise失败:", error.message);
    });
```

#### 3.5.4 Promise.race()

返回一个新的Promise，当第一个Promise解决或拒绝时，新的Promise就会解决或拒绝。

```javascript
const promise1 = new Promise(resolve => setTimeout(() => resolve("第一个完成"), 500));
const promise2 = new Promise(resolve => setTimeout(() => resolve("第二个完成"), 100));

Promise.race([promise1, promise2])
    .then(value => {
        console.log(value); // "第二个完成" (先完成)
    });
```

#### 3.5.5 Promise.allSettled()

等待所有Promise完成，无论成功或失败，返回每个Promise的结果对象。

```javascript
const promise1 = Promise.resolve(3);
const promise2 = new Promise((resolve, reject) => setTimeout(() => reject("失败"), 1000));
const promise3 = Promise.resolve(10);

Promise.allSettled([promise1, promise2, promise3])
    .then(results => {
        results.forEach((result, index) => {
            if (result.status === "fulfilled") {
                console.log(`Promise ${index + 1} 成功:`, result.value);
            } else {
                console.log(`Promise ${index + 1} 失败:`, result.reason);
            }
        });
        /*
        输出:
        Promise 1 成功: 3
        Promise 2 失败: 失败
        Promise 3 成功: 10
        */
    });
```

## 4. async/await

### 4.1 什么是async/await

async/await是建立在Promise之上的语法糖，使异步代码看起来像同步代码，更易读和理解。

- `async`关键字用于声明一个异步函数
- `await`关键字用于等待Promise解决

### 4.2 async函数

```javascript
// async函数总是返回Promise
async function fetchData() {
    return "数据";
}

// 等同于
function fetchData() {
    return Promise.resolve("数据");
}

// 调用async函数
fetchData().then(data => console.log(data)); // "数据"
```

### 4.3 await关键字

await只能在async函数内部使用，用于等待Promise解决。

```javascript
function getData() {
    return new Promise(resolve => {
        setTimeout(() => resolve("从服务器获取的数据"), 1000);
    });
}

async function processData() {
    console.log("开始处理");
    
    // 等待getData()Promise解决
    const data = await getData();
    console.log("获取到数据:", data);
    
    // 可以继续使用await等待其他Promise
    const result = await someOtherAsyncOperation();
    console.log("处理结果:", result);
    
    return "最终结果";
}

processData().then(finalResult => console.log(finalResult));
```

### 4.4 错误处理

在async/await中，使用`try...catch`语句处理错误。

```javascript
async function fetchWithErrorHandling() {
    try {
        const data = await mightFailOperation();
        const result = await processData(data);
        return result;
    } catch (error) {
        console.error("发生错误:", error.message);
        // 可以返回默认值或重新抛出错误
        return "默认值";
        // throw error; // 重新抛出错误
    }
}
```

### 4.5 并行处理

使用`Promise.all()`与async/await结合处理多个并行异步操作。

```javascript
async function fetchMultipleData() {
    try {
        console.log("开始获取数据");
        
        // 并行获取所有数据
        const [users, posts, comments] = await Promise.all([
            fetchUsers(),
            fetchPosts(),
            fetchComments()
        ]);
        
        console.log("所有数据获取完成");
        return { users, posts, comments };
    } catch (error) {
        console.error("获取数据失败:", error.message);
    }
}
```

### 4.6 顺序处理

如果需要按顺序执行多个异步操作，使用多个await语句。

```javascript
async function processSequentially() {
    try {
        // 顺序执行，每个操作等待前一个完成
        const user = await fetchUser();
        const profile = await fetchProfile(user.id);
        const permissions = await fetchPermissions(profile.role);
        
        return { user, profile, permissions };
    } catch (error) {
        console.error("顺序处理失败:", error.message);
    }
}
```

## 5. 实际应用示例

### 5.1 网络请求

使用fetch API和Promise处理HTTP请求。

```javascript
// 使用Promise处理fetch
function fetchUser(userId) {
    return fetch(`https://api.example.com/users/${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status}`);
            }
            return response.json();
        });
}

// 使用async/await处理fetch
async function fetchUserAsync(userId) {
    try {
        const response = await fetch(`https://api.example.com/users/${userId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("获取用户失败:", error.message);
        throw error; // 可以重新抛出错误让调用者处理
    }
}

// 使用示例
fetchUser(123)
    .then(user => console.log("用户信息:", user))
    .catch(error => console.error("错误:", error.message));

// 或者使用async/await
async function displayUser(userId) {
    try {
        const user = await fetchUserAsync(userId);
        console.log("用户信息:", user);
        // 更新UI显示用户信息
        updateUserUI(user);
    } catch (error) {
        console.error("显示用户失败:", error.message);
        showErrorUI(error.message);
    }
}
```

### 5.2 文件操作

```javascript
// 模拟文件读取（在实际应用中使用FileReader API）
function readFile(filename) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // 模拟文件读取
            if (filename.endsWith('.txt')) {
                resolve(`文件内容: ${filename}`);
            } else {
                reject(new Error("不支持的文件类型"));
            }
        }, 500);
    });
}

// 顺序读取多个文件
async function readFilesInOrder(filenames) {
    const results = [];
    
    for (const filename of filenames) {
        try {
            const content = await readFile(filename);
            results.push({ filename, content });
        } catch (error) {
            console.error(`读取文件 ${filename} 失败:`, error.message);
            results.push({ filename, error: error.message });
        }
    }
    
    return results;
}

// 并行读取多个文件
async function readFilesInParallel(filenames) {
    const promises = filenames.map(filename => 
        readFile(filename)
            .then(content => ({ filename, content }))
            .catch(error => ({ filename, error: error.message }))
    );
    
    return Promise.all(promises);
}
```

### 5.3 动画序列

```javascript
// 创建Promise封装的动画函数
function animate(element, duration, properties) {
    return new Promise(resolve => {
        // 使用简单的动画实现（实际应用中可能使用CSS动画或动画库）
        const startTime = Date.now();
        const startValues = {};
        
        // 保存初始值
        for (const prop in properties) {
            startValues[prop] = parseFloat(element.style[prop]) || 0;
        }
        
        function update() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 更新样式
            for (const prop in properties) {
                const start = startValues[prop];
                const end = properties[prop];
                element.style[prop] = start + (end - start) * progress + 'px';
            }
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                resolve();
            }
        }
        
        update();
    });
}

// 使用async/await创建动画序列
async function runAnimationSequence() {
    const element = document.getElementById('animated-element');
    
    try {
        // 依次执行动画
        await animate(element, 1000, { left: 200 });
        await animate(element, 1000, { top: 200 });
        await animate(element, 1000, { left: 0 });
        await animate(element, 1000, { top: 0 });
        
        console.log("动画序列完成");
    } catch (error) {
        console.error("动画执行失败:", error.message);
    }
}
```

## 6. 高级技巧与模式

### 6.1 超时处理

为Promise添加超时功能。

```javascript
function withTimeout(promise, timeout) {
    return Promise.race([
        promise,
        new Promise((_, reject) => 
            setTimeout(() => reject(new Error("操作超时")), timeout)
        )
    ]);
}

// 使用示例
const slowOperation = new Promise(resolve => 
    setTimeout(() => resolve("完成"), 3000)
);

withTimeout(slowOperation, 2000)
    .then(result => console.log(result))
    .catch(error => console.error(error.message)); // "操作超时"
```

### 6.2 重试机制

实现自动重试失败的Promise。

```javascript
function retry(promiseGenerator, maxAttempts = 3, delay = 1000) {
    return new Promise((resolve, reject) => {
        let attempt = 0;
        
        function tryAgain() {
            attempt++;
            
            promiseGenerator()
                .then(resolve)
                .catch(error => {
                    if (attempt >= maxAttempts) {
                        reject(error);
                    } else {
                        setTimeout(tryAgain, delay);
                    }
                });
        }
        
        tryAgain();
    });
}

// 使用示例
function unreliableOperation() {
    return new Promise((resolve, reject) => {
        const success = Math.random() > 0.7; // 30%成功率
        
        if (success) {
            resolve("成功");
        } else {
            reject(new Error("失败"));
        }
    });
}

retry(() => unreliableOperation(), 5, 500)
    .then(result => console.log(result))
    .catch(error => console.error("所有尝试均失败:", error.message));
```

### 6.3 缓存Promise结果

避免重复执行相同的异步操作。

```javascript
function memoize(promiseGenerator) {
    let cachedPromise = null;
    
    return function(...args) {
        if (cachedPromise) {
            return cachedPromise;
        }
        
        cachedPromise = promiseGenerator(...args)
            .finally(() => {
                // 可选：在一段时间后清除缓存
                setTimeout(() => {
                    cachedPromise = null;
                }, 5000);
            });
        
        return cachedPromise;
    };
}

// 使用示例
const fetchUserMemoized = memoize(userId => 
    fetch(`https://api.example.com/users/${userId}`).then(res => res.json())
);

// 第一次调用会发起网络请求
fetchUserMemoized(123).then(user => console.log(user));

// 第二次调用会使用缓存的结果
fetchUserMemoized(123).then(user => console.log(user));
```

### 6.4 限流并发请求

限制同时执行的Promise数量。

```javascript
class PromisePool {
    constructor(maxConcurrent = 3) {
        this.maxConcurrent = maxConcurrent;
        this.running = 0;
        this.queue = [];
    }
    
    add(promiseGenerator) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                promiseGenerator,
                resolve,
                reject
            });
            
            this.process();
        });
    }
    
    process() {
        if (this.running >= this.maxConcurrent || this.queue.length === 0) {
            return;
        }
        
        this.running++;
        const { promiseGenerator, resolve, reject } = this.queue.shift();
        
        promiseGenerator()
            .then(resolve)
            .catch(reject)
            .finally(() => {
                this.running--;
                this.process();
            });
    }
}

// 使用示例
const pool = new PromisePool(2); // 最多同时执行2个请求

const urls = [
    'https://api.example.com/data1',
    'https://api.example.com/data2',
    'https://api.example.com/data3',
    'https://api.example.com/data4',
    'https://api.example.com/data5'
];

const promises = urls.map(url => 
    pool.add(() => fetch(url).then(res => res.json()))
);

Promise.all(promises)
    .then(results => console.log("所有请求完成", results))
    .catch(error => console.error("请求失败", error));
```

## 7. 错误处理最佳实践

### 7.1 全局错误处理

```javascript
// 处理未捕获的Promise拒绝
window.addEventListener('unhandledrejection', event => {
    console.error('未处理的Promise拒绝:', event.reason);
    // 可以在这里记录错误或显示用户友好的错误信息
    event.preventDefault(); // 防止错误在控制台显示
});
```

### 7.2 错误分类和处理策略

```javascript
class NetworkError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.name = "NetworkError";
        this.statusCode = statusCode;
    }
}

class ValidationError extends Error {
    constructor(message, field) {
        super(message);
        this.name = "ValidationError";
        this.field = field;
    }
}

async function robustFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new NetworkError(`HTTP错误: ${response.status}`, response.status);
        }
        
        return await response.json();
    } catch (error) {
        if (error instanceof NetworkError) {
            // 网络错误处理
            if (error.statusCode >= 500) {
                throw new Error("服务器错误，请稍后重试");
            } else if (error.statusCode === 404) {
                throw new Error("请求的资源不存在");
            } else {
                throw new Error("网络请求失败");
            }
        } else if (error instanceof TypeError) {
            // 网络连接问题
            throw new Error("无法连接到服务器，请检查网络连接");
        } else {
            // 重新抛出其他错误
            throw error;
        }
    }
}

// 使用示例
async function fetchUserData(userId) {
    try {
        const userData = await robustFetch(`https://api.example.com/users/${userId}`);
        
        // 验证数据
        if (!userData.email) {
            throw new ValidationError("用户缺少邮箱字段", "email");
        }
        
        return userData;
    } catch (error) {
        // 显示用户友好的错误信息
        if (error instanceof ValidationError) {
            showUserError(`数据验证失败: ${error.message}`);
        } else {
            showUserError(error.message);
        }
        
        // 记录详细错误
        logError(error);
        
        throw error; // 可以选择重新抛出或返回默认值
    }
}
```

## 8. 性能优化

### 8.1 避免不必要的await

```javascript
// 不好的做法：顺序等待不相关的操作
async function fetchAllDataSequentially() {
    const user = await fetchUser();
    const posts = await fetchPosts();
    const comments = await fetchComments();
    
    return { user, posts, comments };
}

// 好的做法：并行执行不相关的操作
async function fetchAllDataParallel() {
    // 同时发起所有请求
    const [user, posts, comments] = await Promise.all([
        fetchUser(),
        fetchPosts(),
        fetchComments()
    ]);
    
    return { user, posts, comments };
}
```

### 8.2 使用Promise.allSettled代替Promise.all

```javascript
// 当不关心个别操作失败时，使用Promise.allSettled
async function fetchMultipleDataSomeMayFail() {
    const results = await Promise.allSettled([
        fetchUserProfile(),
        fetchUserPreferences(),
        fetchUserNotifications(),
        fetchUserActivity()
    ]);
    
    const [profile, preferences, notifications, activity] = results;
    
    // 处理成功的结果
    if (profile.status === 'fulfilled') {
        displayUserProfile(profile.value);
    }
    
    if (preferences.status === 'fulfilled') {
        applyUserPreferences(preferences.value);
    }
    
    // 处理失败的操作但不影响其他操作
    if (notifications.status === 'rejected') {
        console.warn('获取通知失败:', notifications.reason.message);
    }
    
    return results;
}
```

### 8.3 延迟执行

```javascript
// 创建一个延迟执行的Promise
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 使用示例
async function fetchWithRetry(url, maxRetries = 3, initialDelay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fetch(url).then(res => res.json());
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            
            // 指数退避策略
            const waitTime = initialDelay * Math.pow(2, i);
            await delay(waitTime);
            console.log(`第${i + 1}次重试...`);
        }
    }
}
```

## 9. 总结

本章我们学习了JavaScript异步编程的核心概念和技术：

1. **异步编程基础**：理解同步与异步的区别，以及为什么需要异步编程
2. **回调函数**：了解回调函数的使用方式和回调地狱问题
3. **Promise基础**：掌握Promise的创建、使用和各种状态管理
4. **async/await**：使用现代语法编写更清晰的异步代码
5. **实际应用**：将异步编程应用于网络请求、文件操作和动画等场景
6. **高级技巧**：实现超时、重试、缓存和并发控制等高级模式
7. **错误处理**：采用最佳实践处理异步操作中的错误
8. **性能优化**：通过并行执行和合理的错误处理提高应用性能

异步编程是JavaScript开发的核心技能，掌握Promise和async/await将帮助你构建高效、可维护的异步代码。在下一章中，我们将学习ES6+的新特性，进一步提升JavaScript编程能力。