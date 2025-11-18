# 第9章：Promise与异步编程

## 9.1 异步编程的挑战

### 9.1.1 回调函数的问题

在JavaScript中，异步编程一直是一个重要的话题。在ES6之前，我们主要通过回调函数来处理异步操作，但这会导致一些问题：

#### 回调地狱（Callback Hell）

```javascript
// 回调地狱示例
getData(function(a) {
    getMoreData(a, function(b) {
        getMoreData(b, function(c) {
            getMoreData(c, function(d) {
                getMoreData(d, function(e) {
                    console.log(e);
                });
            });
        });
    });
});
```

#### 错误处理困难

```javascript
// 回调函数中的错误处理复杂
try {
    getData(function(data) {
        try {
            getMoreData(data, function(moreData) {
                try {
                    console.log(moreData);
                } catch (error) {
                    handleError(error);
                }
            });
        } catch (error) {
            handleError(error);
        }
    });
} catch (error) {
    handleError(error);
}
```

### 9.1.2 Promise的诞生

Promise是异步编程的一种解决方案，比传统的回调函数更加合理和强大。它由社区最早提出和实现，ES6将其写进了语言标准，统一了用法，原生提供了Promise对象。

## 9.2 Promise基础

### 9.2.1 Promise的概念与状态

Promise代表一个异步操作的最终完成或失败，以及其结果值。一个Promise对象有以下几种状态：

- **pending（进行中）**：初始状态，既不是成功，也不是失败状态
- **fulfilled（已成功）**：意味着操作成功完成
- **rejected（已失败）**：意味着操作失败

Promise的状态一旦改变，就不会再变，任何时候都可以得到这个结果。

```javascript
// Promise状态示例
const promise = new Promise(function(resolve, reject) {
    // 异步操作代码
    if (/* 异步操作成功 */) {
        resolve(value); // 将Promise的状态从pending变为fulfilled
    } else {
        reject(error); // 将Promise的状态从pending变为rejected
    }
});
```

### 9.2.2 创建Promise

```javascript
// 基本Promise创建
const myPromise = new Promise((resolve, reject) => {
    setTimeout(() => {
        const success = Math.random() > 0.5;
        if (success) {
            resolve("操作成功！");
        } else {
            reject(new Error("操作失败！"));
        }
    }, 1000);
});

// 使用Promise
myPromise
    .then(result => console.log(result))
    .catch(error => console.error(error.message));
```

### 9.2.3 Promise.prototype.then()

`then()`方法是Promise实例的核心方法，用于指定fulfilled状态和rejected状态的回调函数。

```javascript
// then方法示例
promise.then(
    value => {
        // fulfilled状态的回调函数
        console.log("成功:", value);
    },
    error => {
        // rejected状态的回调函数（可选）
        console.error("失败:", error);
    }
);

// 链式调用
promise
    .then(value => {
        console.log("第一步:", value);
        return value + 1; // 返回值会传递给下一个then
    })
    .then(value => {
        console.log("第二步:", value);
        return value * 2;
    })
    .then(value => {
        console.log("最终结果:", value);
    });
```

### 9.2.4 Promise.prototype.catch()

`catch()`方法是`.then(null, rejection)`的别名，用于指定发生错误时的回调函数。

```javascript
// catch方法示例
promise
    .then(result => console.log(result))
    .catch(error => console.error(error));

// 错误会沿着Promise链向下传递，直到被catch捕获
promise
    .then(result => {
        console.log(result);
        throw new Error("中间发生错误");
    })
    .then(result => {
        console.log("这不会执行");
    })
    .catch(error => {
        console.error("捕获错误:", error.message);
    });
```

### 9.2.5 Promise.prototype.finally()

`finally()`方法用于指定不管Promise对象最后状态如何，都会执行的操作。

```javascript
// finally方法示例
promise
    .then(result => console.log("成功:", result))
    .catch(error => console.error("失败:", error))
    .finally(() => {
        console.log("无论如何都会执行");
        // 适合做清理工作，如隐藏加载动画
    });
```

## 9.3 Promise进阶

### 9.3.1 Promise.resolve()

`Promise.resolve()`方法将现有值转换为Promise对象。

```javascript
// Promise.resolve示例
const resolvedPromise = Promise.resolve("成功");
resolvedPromise.then(value => console.log(value)); // "成功"

// 等同于
const resolvedPromise2 = new Promise(resolve => resolve("成功"));

// 如果参数是Promise实例，则原封不动地返回
const originalPromise = new Promise(resolve => resolve("原始"));
const samePromise = Promise.resolve(originalPromise);
console.log(originalPromise === samePromise); // true

// 参数是thenable对象
const thenable = {
    then: function(resolve, reject) {
        resolve("thenable对象");
    }
};
Promise.resolve(thenable).then(value => console.log(value)); // "thenable对象"
```

### 9.3.2 Promise.reject()

`Promise.reject()`方法返回一个新的Promise实例，该实例的状态为rejected。

```javascript
// Promise.reject示例
const rejectedPromise = Promise.reject(new Error("失败"));
rejectedPromise.catch(error => console.error(error.message)); // "失败"

// 等同于
const rejectedPromise2 = new Promise((resolve, reject) => {
    reject(new Error("失败"));
});
```

### 9.3.3 Promise.all()

`Promise.all()`方法将多个Promise实例包装成一个新的Promise实例。

```javascript
// Promise.all示例
const promise1 = Promise.resolve(3);
const promise2 = new Promise(resolve => setTimeout(() => resolve('foo'), 1000));
const promise3 = Promise.resolve(42);

Promise.all([promise1, promise2, promise3])
    .then(values => {
        console.log(values); // [3, "foo", 42]
    })
    .catch(error => {
        console.error("至少有一个Promise被rejected:", error);
    });

// 如果其中一个Promise被rejected，整个Promise.all立即被rejected
const promise4 = Promise.resolve(3);
const promise5 = Promise.reject(new Error("失败"));
const promise6 = Promise.resolve(42);

Promise.all([promise4, promise5, promise6])
    .then(values => {
        console.log("这不会执行");
    })
    .catch(error => {
        console.error("捕获错误:", error.message); // "失败"
    });
```

### 9.3.4 Promise.race()

`Promise.race()`方法同样是将多个Promise实例包装成一个新的Promise实例。

```javascript
// Promise.race示例
const promise1 = new Promise(resolve => setTimeout(() => resolve('one'), 500));
const promise2 = new Promise(resolve => setTimeout(() => resolve('two'), 100));

Promise.race([promise1, promise2])
    .then(value => {
        console.log(value); // "two" - 因为promise2更快完成
    });

// 如果有非Promise值，会直接使用Promise.resolve()转换
const promise3 = "three";
const promise4 = new Promise(resolve => setTimeout(() => resolve('four'), 100));

Promise.race([promise3, promise4])
    .then(value => {
        console.log(value); // "three" - 因为非Promise值立即完成
    });
```

### 9.3.5 Promise.allSettled()

`Promise.allSettled()`方法返回一个在所有给定的Promise都已经fulfilled或rejected后的Promise，并带有一个对象数组，每个对象表示对应的Promise结果。

```javascript
// Promise.allSettled示例
const promise1 = Promise.resolve(3);
const promise2 = new Promise((resolve, reject) => 
    setTimeout(() => reject(new Error("失败")), 1000)
);
const promise3 = Promise.resolve(42);

Promise.allSettled([promise1, promise2, promise3])
    .then(results => {
        results.forEach((result, i) => {
            if (result.status === 'fulfilled') {
                console.log(`Promise ${i}: ${result.value}`);
            } else {
                console.log(`Promise ${i}: ${result.reason.message}`);
            }
        });
    });
// 输出:
// Promise 0: 3
// Promise 1: 失败
// Promise 2: 42
```

## 9.4 Promise链式调用

### 9.4.1 链式调用原理

Promise的链式调用是通过`then()`方法返回新的Promise实例实现的。

```javascript
// Promise链式调用原理
new Promise(resolve => resolve(1))
    .then(value => {
        console.log(value); // 1
        return value + 1; // 返回值会被Promise.resolve()包装
    })
    .then(value => {
        console.log(value); // 2
        return new Promise(resolve => setTimeout(() => resolve(value + 1), 1000));
    })
    .then(value => {
        console.log(value); // 3
    });
```

### 9.4.2 错误传播

在Promise链中，错误会沿着链向下传播，直到被捕获。

```javascript
// 错误传播示例
new Promise((resolve, reject) => {
    reject(new Error("初始错误"));
})
    .then(value => {
        console.log("这不会执行");
    })
    .then(value => {
        console.log("这也不会执行");
    })
    .catch(error => {
        console.error("捕获错误:", error.message); // "初始错误"
        return "恢复后的值";
    })
    .then(value => {
        console.log("恢复后的值:", value); // "恢复后的值"
    });
```

### 9.4.3 嵌套Promise与扁平化

```javascript
// 嵌套Promise
function getUser(id) {
    return new Promise(resolve => {
        setTimeout(() => resolve({ id, name: "用户" + id }), 100);
    });
}

function getPosts(userId) {
    return new Promise(resolve => {
        setTimeout(() => resolve([
            { id: 1, title: "文章1", userId },
            { id: 2, title: "文章2", userId }
        ]), 100);
    });
}

// 嵌套Promise（不推荐）
getUser(1)
    .then(user => {
        getPosts(user.id)
            .then(posts => {
                console.log("用户:", user);
                console.log("文章:", posts);
            });
    });

// 扁平化Promise链（推荐）
getUser(1)
    .then(user => {
        console.log("用户:", user);
        return getPosts(user.id);
    })
    .then(posts => {
        console.log("文章:", posts);
    });
```

## 9.5 异步函数（Async/Await）

### 9.5.1 Async函数基础

Async函数是ES2017引入的，它是Generator函数的语法糖，使得异步操作更加方便。

```javascript
// async函数基本语法
async function fetchData() {
    return "数据";
}

// async函数返回Promise
fetchData().then(data => console.log(data)); // "数据"

// 等同于
function fetchDataEquivalent() {
    return Promise.resolve("数据");
}
```

### 9.5.2 Await表达式

`await`操作符用于等待一个Promise对象，它只能在async函数内部使用。

```javascript
// await基本用法
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function example() {
    console.log("开始");
    await delay(1000); // 等待1秒
    console.log("1秒后");
    
    const result = await Promise.resolve("结果");
    console.log(result); // "结果"
    
    try {
        const errorResult = await Promise.reject(new Error("错误"));
    } catch (error) {
        console.error(error.message); // "错误"
    }
}

example();
```

### 9.5.3 Async/Await错误处理

```javascript
// async/await错误处理
async function fetchDataWithErrorHandling() {
    try {
        const data = await fetchData();
        console.log(data);
        return data;
    } catch (error) {
        console.error("获取数据失败:", error);
        // 可以返回默认值或重新抛出错误
        return null;
        // 或者 throw error;
    } finally {
        console.log("清理工作");
    }
}

// 多个await的错误处理
async function fetchMultipleData() {
    try {
        const user = await getUser(1);
        const posts = await getPosts(user.id);
        const comments = await getComments(posts[0].id);
        
        return { user, posts, comments };
    } catch (error) {
        console.error("获取数据失败:", error);
        throw error; // 重新抛出错误，让调用者处理
    }
}
```

### 9.5.4 并行处理

```javascript
// 串行处理（不推荐）
async function sequential() {
    console.time("sequential");
    const result1 = await fetchData1(); // 等待完成
    const result2 = await fetchData2(); // 等待完成
    const result3 = await fetchData3(); // 等待完成
    console.timeEnd("sequential");
    return [result1, result2, result3];
}

// 并行处理（推荐）
async function parallel() {
    console.time("parallel");
    const [result1, result2, result3] = await Promise.all([
        fetchData1(),
        fetchData2(),
        fetchData3()
    ]);
    console.timeEnd("parallel");
    return [result1, result2, result3];
}

// 部分并行处理
async function partialParallel() {
    const user = await getUser(1);
    const [posts, comments] = await Promise.all([
        getPosts(user.id),
        getComments(user.id)
    ]);
    
    return { user, posts, comments };
}
```

## 9.6 实际应用场景

### 9.6.1 API请求处理

```javascript
// 使用Promise处理API请求
function fetchUser(id) {
    return new Promise((resolve, reject) => {
        fetch(`/api/users/${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => resolve(data))
            .catch(error => reject(error));
    });
}

// 使用async/await处理API请求
async function fetchUserWithAsync(id) {
    try {
        const response = await fetch(`/api/users/${id}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const userData = await response.json();
        return userData;
    } catch (error) {
        console.error("获取用户数据失败:", error);
        throw error;
    }
}

// 使用示例
async function displayUser(id) {
    try {
        const user = await fetchUserWithAsync(id);
        document.getElementById("user-name").textContent = user.name;
        document.getElementById("user-email").textContent = user.email;
    } catch (error) {
        document.getElementById("error-message").textContent = 
            `获取用户数据失败: ${error.message}`;
    }
}
```

### 9.6.2 文件操作

```javascript
// 使用Promise封装文件读取
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        
        reader.readAsText(file);
    });
}

// 使用async/await处理多个文件
async function processFiles(files) {
    const results = [];
    
    for (const file of files) {
        try {
            const content = await readFileAsText(file);
            results.push({ name: file.name, content });
        } catch (error) {
            console.error(`读取文件 ${file.name} 失败:`, error);
            results.push({ name: file.name, error: error.message });
        }
    }
    
    return results;
}

// 并行处理文件
async function processFilesInParallel(files) {
    const promises = Array.from(files).map(file => 
        readFileAsText(file)
            .then(content => ({ name: file.name, content }))
            .catch(error => ({ name: file.name, error: error.message }))
    );
    
    return Promise.all(promises);
}
```

### 9.6.3 超时处理

```javascript
// Promise超时处理
function withTimeout(promise, timeoutMs) {
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error("操作超时")), timeoutMs);
    });
    
    return Promise.race([promise, timeoutPromise]);
}

// 使用示例
async function fetchDataWithTimeout() {
    try {
        const data = await withTimeout(fetchData(), 5000);
        return data;
    } catch (error) {
        if (error.message === "操作超时") {
            console.error("请求超时，请重试");
        } else {
            console.error("请求失败:", error);
        }
        throw error;
    }
}

// 可取消的Promise
function makeCancelable(promise) {
    let isCanceled = false;
    
    const wrappedPromise = new Promise((resolve, reject) => {
        promise
            .then(value => {
                if (isCanceled) {
                    reject(new Error("Promise被取消"));
                } else {
                    resolve(value);
                }
            })
            .catch(error => {
                if (isCanceled) {
                    reject(new Error("Promise被取消"));
                } else {
                    reject(error);
                }
            });
    });
    
    return {
        promise: wrappedPromise,
        cancel() {
            isCanceled = true;
        }
    };
}
```

### 9.6.4 重试机制

```javascript
// Promise重试机制
function retry(fn, maxAttempts = 3, delayMs = 1000) {
    return new Promise((resolve, reject) => {
        let attempt = 1;
        
        function attemptOperation() {
            fn()
                .then(resolve)
                .catch(error => {
                    if (attempt < maxAttempts) {
                        attempt++;
                        console.log(`尝试失败，${delayMs}ms后重试 (${attempt}/${maxAttempts})`);
                        setTimeout(attemptOperation, delayMs);
                    } else {
                        reject(new Error(`操作失败，已尝试${maxAttempts}次: ${error.message}`));
                    }
                });
        }
        
        attemptOperation();
    });
}

// 使用示例
async function fetchWithRetry() {
    try {
        const data = await retry(() => fetchUnreliableData(), 5, 2000);
        console.log("获取数据成功:", data);
        return data;
    } catch (error) {
        console.error("最终失败:", error.message);
        throw error;
    }
}
```

## 9.7 实践练习

### 练习1：实现一个简单的Promise队列

```javascript
// 实现一个Promise队列，按顺序执行异步任务
class PromiseQueue {
    constructor() {
        this.queue = [];
        this.running = false;
    }
    
    add(promiseCreator) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                promiseCreator,
                resolve,
                reject
            });
            
            if (!this.running) {
                this.processQueue();
            }
        });
    }
    
    async processQueue() {
        this.running = true;
        
        while (this.queue.length > 0) {
            const { promiseCreator, resolve, reject } = this.queue.shift();
            
            try {
                const result = await promiseCreator();
                resolve(result);
            } catch (error) {
                reject(error);
            }
        }
        
        this.running = false;
    }
}

// 使用示例
const queue = new PromiseQueue();

queue.add(() => delay(1000).then(() => "任务1完成"))
    .then(result => console.log(result));

queue.add(() => delay(500).then(() => "任务2完成"))
    .then(result => console.log(result));

queue.add(() => delay(800).then(() => "任务3完成"))
    .then(result => console.log(result));
```

### 练习2：实现Promise缓存

```javascript
// 实现一个Promise缓存，避免重复请求
class PromiseCache {
    constructor() {
        this.cache = new Map();
    }
    
    get(key, promiseCreator) {
        // 如果缓存中存在且Promise未完成，返回缓存的Promise
        if (this.cache.has(key)) {
            const cachedPromise = this.cache.get(key);
            
            // 检查Promise是否已完成
            return cachedPromise.catch(() => {
                // 如果Promise失败，从缓存中删除并重新创建
                this.cache.delete(key);
                return this.createAndCache(key, promiseCreator);
            });
        }
        
        // 创建新的Promise并缓存
        return this.createAndCache(key, promiseCreator);
    }
    
    createAndCache(key, promiseCreator) {
        const promise = promiseCreator();
        this.cache.set(key, promise);
        
        // Promise完成后从缓存中删除（可选）
        promise.finally(() => {
            // 如果不需要永久缓存，可以取消注释下面这行
            // this.cache.delete(key);
        });
        
        return promise;
    }
    
    // 清除特定缓存
    delete(key) {
        return this.cache.delete(key);
    }
    
    // 清除所有缓存
    clear() {
        this.cache.clear();
    }
}

// 使用示例
const cache = new PromiseCache();

function fetchUserData(userId) {
    return cache.get(`user-${userId}`, () => {
        console.log(`发起用户${userId}的请求`);
        return fetch(`/api/users/${userId}`).then(res => res.json());
    });
}

// 第一次调用会发起请求
fetchUserData(1).then(user => console.log(user));

// 第二次调用会使用缓存，不会发起新请求
fetchUserData(1).then(user => console.log(user));
```

### 练习3：实现并发限制

```javascript
// 实现一个并发限制器，限制同时运行的Promise数量
class ConcurrencyLimiter {
    constructor(maxConcurrency) {
        this.maxConcurrency = maxConcurrency;
        this.running = 0;
        this.queue = [];
    }
    
    async add(promiseCreator) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                promiseCreator,
                resolve,
                reject
            });
            
            this.process();
        });
    }
    
    async process() {
        if (this.running >= this.maxConcurrency || this.queue.length === 0) {
            return;
        }
        
        this.running++;
        const { promiseCreator, resolve, reject } = this.queue.shift();
        
        try {
            const result = await promiseCreator();
            resolve(result);
        } catch (error) {
            reject(error);
        } finally {
            this.running--;
            this.process(); // 处理队列中的下一个任务
        }
    }
}

// 使用示例
const limiter = new ConcurrencyLimiter(3); // 最多同时运行3个Promise

// 创建10个任务，但只有3个会同时运行
for (let i = 1; i <= 10; i++) {
    limiter.add(() => {
        console.log(`任务${i}开始`);
        return delay(Math.random() * 2000 + 1000).then(() => {
            console.log(`任务${i}完成`);
            return `任务${i}的结果`;
        });
    }).then(result => {
        console.log(result);
    });
}
```

## 9.8 最佳实践

### 9.8.1 错误处理最佳实践

```javascript
// 1. 总是使用catch或try/catch处理错误
// 不推荐
fetchData().then(data => console.log(data));

// 推荐
fetchData()
    .then(data => console.log(data))
    .catch(error => console.error(error));

// 或者使用async/await
async function getData() {
    try {
        const data = await fetchData();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}

// 2. 在Promise链的末尾总是添加catch
// 不推荐
fetchData()
    .then(data => processData(data))
    .then(result => saveData(result));

// 推荐
fetchData()
    .then(data => processData(data))
    .then(result => saveData(result))
    .catch(error => handleError(error));

// 3. 不要混合使用回调函数和Promise
// 不推荐
function fetchUser(id, callback) {
    fetch(`/api/users/${id}`)
        .then(response => response.json())
        .then(user => callback(null, user))
        .catch(error => callback(error));
}

// 推荐
function fetchUser(id) {
    return fetch(`/api/users/${id}`)
        .then(response => response.json());
}
```

### 9.8.2 代码组织最佳实践

```javascript
// 1. 将复杂的异步逻辑封装到函数中
// 不推荐
async function displayUserPosts() {
    try {
        const userResponse = await fetch('/api/users/1');
        const user = await userResponse.json();
        
        const postsResponse = await fetch(`/api/users/${user.id}/posts`);
        const posts = await postsResponse.json();
        
        for (const post of posts) {
            const commentsResponse = await fetch(`/api/posts/${post.id}/comments`);
            const comments = await commentsResponse.json();
            
            post.comments = comments;
        }
        
        renderPosts(posts);
    } catch (error) {
        console.error(error);
    }
}

// 推荐
async function getUser(id) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
}

async function getUserPosts(userId) {
    const response = await fetch(`/api/users/${userId}/posts`);
    return response.json();
}

async function getPostComments(postId) {
    const response = await fetch(`/api/posts/${postId}/comments`);
    return response.json();
}

async function addCommentsToPosts(posts) {
    const postsWithComments = await Promise.all(
        posts.map(async post => {
            const comments = await getPostComments(post.id);
            return { ...post, comments };
        })
    );
    
    return postsWithComments;
}

async function displayUserPosts() {
    try {
        const user = await getUser(1);
        const posts = await getUserPosts(user.id);
        const postsWithComments = await addCommentsToPosts(posts);
        
        renderPosts(postsWithComments);
    } catch (error) {
        console.error(error);
    }
}

// 2. 使用函数组合来处理数据流
const pipe = (...fns) => (value) => fns.reduce((acc, fn) => fn(acc), value);

// 使用示例
const processUserData = pipe(
    getUser,
    user => getUserPosts(user.id),
    addCommentsToPosts,
    renderPosts
);

processUserData(1).catch(console.error);
```

### 9.8.3 性能优化最佳实践

```javascript
// 1. 并行处理独立的异步操作
// 不推荐（串行处理）
async function fetchUserData(userId) {
    const user = await getUser(userId);
    const posts = await getUserPosts(userId);
    const comments = await getUserComments(userId);
    
    return { user, posts, comments };
}

// 推荐（并行处理）
async function fetchUserData(userId) {
    const [user, posts, comments] = await Promise.all([
        getUser(userId),
        getUserPosts(userId),
        getUserComments(userId)
    ]);
    
    return { user, posts, comments };
}

// 2. 使用缓存避免重复请求
const userCache = new Map();

async function getUserWithCache(id) {
    if (userCache.has(id)) {
        return userCache.get(id);
    }
    
    const user = await getUser(id);
    userCache.set(id, user);
    return user;
}

// 3. 对于大量数据，考虑分批处理
async function processLargeDataset(items, batchSize = 10) {
    const results = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        const batchResults = await Promise.all(
            batch.map(item => processItem(item))
        );
        results.push(...batchResults);
        
        // 可选：添加延迟以避免过载
        if (i + batchSize < items.length) {
            await delay(100);
        }
    }
    
    return results;
}
```

## 9.9 常见问题与解决方案

### 9.9.1 Promise未处理拒绝警告

```javascript
// 问题：未处理的Promise拒绝会导致警告
Promise.reject(new Error("未处理的错误"));

// 解决方案1：总是添加catch处理
Promise.reject(new Error("未处理的错误"))
    .catch(error => console.error(error));

// 解决方案2：全局处理未捕获的Promise拒绝
if (typeof window !== 'undefined') {
    window.addEventListener('unhandledrejection', event => {
        console.error('未处理的Promise拒绝:', event.reason);
        // 可选：阻止默认行为
        event.preventDefault();
    });
}

// Node.js环境
if (typeof process !== 'undefined') {
    process.on('unhandledRejection', (reason, promise) => {
        console.error('未处理的Promise拒绝:', reason);
    });
}
```

### 9.9.2 循环中的异步操作

```javascript
// 问题：在循环中使用await会导致串行执行
async function processItems(items) {
    for (const item of items) {
        await processItem(item); // 串行执行，效率低
    }
}

// 解决方案：使用Promise.all并行执行
async function processItems(items) {
    const promises = items.map(item => processItem(item));
    await Promise.all(promises);
}

// 或者使用for...of配合并发控制
async function processItemsWithLimit(items, limit = 5) {
    const results = [];
    const executing = [];
    
    for (const item of items) {
        const promise = processItem(item).then(result => {
            results.push(result);
            // 从执行队列中移除已完成的Promise
            executing.splice(executing.indexOf(promise), 1);
        });
        
        executing.push(promise);
        
        // 如果达到并发限制，等待其中一个完成
        if (executing.length >= limit) {
            await Promise.race(executing);
        }
    }
    
    // 等待所有剩余的Promise完成
    await Promise.all(executing);
    
    return results;
}
```

### 9.9.3 异步函数中的返回值问题

```javascript
// 问题：在async函数中忘记await
async function fetchUserData() {
    const user = getUser(1); // 忘记await，返回Promise而不是用户数据
    console.log(user); // Promise对象
    
    // 后续代码可能会出错
    console.log(user.name); // undefined
}

// 解决方案：确保正确使用await
async function fetchUserData() {
    const user = await getUser(1); // 正确使用await
    console.log(user); // 用户数据对象
    
    console.log(user.name); // 正确访问用户名
}

// 问题：在非async函数中使用await
function processData() {
    const data = await fetchData(); // 语法错误
}

// 解决方案：将函数标记为async
async function processData() {
    const data = await fetchData(); // 正确
}
```

### 9.9.4 内存泄漏问题

```javascript
// 问题：长时间运行的Promise可能导致内存泄漏
function createLeakyPromise() {
    const data = new Array(1000000).fill(0); // 大量数据
    
    return new Promise(resolve => {
        // 如果Promise长时间未解决，data会一直占用内存
        setTimeout(() => {
            resolve(data);
        }, 60000); // 1分钟后解决
    });
}

// 解决方案：及时释放不需要的引用
function createNonLeakyPromise() {
    return new Promise(resolve => {
        // 在Promise内部创建数据，而不是在外部
        const data = new Array(1000000).fill(0);
        
        setTimeout(() => {
            resolve(data);
            // 解决后，data会被垃圾回收
        }, 60000);
    });
}

// 或者使用WeakMap/WeakSet来存储不需要长期持有的引用
const pendingOperations = new WeakMap();

function processData(data) {
    const operation = { id: Date.now() };
    pendingOperations.set(operation, data);
    
    return new Promise(resolve => {
        setTimeout(() => {
            const data = pendingOperations.get(operation);
            resolve(data);
            // 操作完成后，WeakMap中的引用会被自动清理
        }, 1000);
    });
}
```

## 9.10 总结

Promise和async/await是现代JavaScript异步编程的核心工具。它们提供了更优雅、更强大的方式来处理异步操作，避免了回调地狱，使代码更加清晰和可维护。

### 关键要点：

1. **Promise基础**：理解Promise的三种状态（pending、fulfilled、rejected）和基本用法
2. **Promise链**：掌握Promise链式调用和错误传播机制
3. **Promise方法**：熟练使用Promise.all、Promise.race、Promise.allSettled等实用方法
4. **Async/Await**：使用async/await编写更直观的异步代码
5. **错误处理**：正确处理异步操作中的错误
6. **性能优化**：并行处理、缓存和并发控制等优化技术
7. **最佳实践**：遵循代码组织和错误处理的最佳实践

Promise和async/await不仅解决了回调函数的问题，还为JavaScript异步编程提供了坚实的基础。掌握这些概念对于现代Web开发至关重要，它们是构建高效、可维护的异步应用程序的关键工具。