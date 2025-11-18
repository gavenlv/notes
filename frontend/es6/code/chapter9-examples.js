// 第9章：Promise与异步编程 - 代码示例

// ===== 9.1 异步编程的挑战 =====

// 回调地狱示例
function callbackHellExample() {
    function getData(callback) {
        setTimeout(() => {
            callback({ id: 1, name: "数据1" });
        }, 500);
    }
    
    function getMoreData(data, callback) {
        setTimeout(() => {
            callback({ ...data, detail: "详细信息" });
        }, 500);
    }
    
    // 回调地狱
    getData(function(a) {
        getMoreData(a, function(b) {
            getMoreData(b, function(c) {
                getMoreData(c, function(d) {
                    getMoreData(d, function(e) {
                        console.log("回调地狱结果:", e);
                    });
                });
            });
        });
    });
}

// ===== 9.2 Promise基础 =====

// Promise基本创建
function basicPromiseExample() {
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

    myPromise
        .then(result => console.log("成功:", result))
        .catch(error => console.error("失败:", error.message));
}

// Promise状态示例
function promiseStatesExample() {
    console.log("=== Promise状态示例 ===");
    
    // pending状态
    const pendingPromise = new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve("已完成");
        }, 1000);
    });
    console.log("初始状态:", pendingPromise); // Promise { <pending> }
    
    // fulfilled状态
    const fulfilledPromise = Promise.resolve("成功");
    console.log("已完成状态:", fulfilledPromise); // Promise { "成功" }
    
    // rejected状态
    const rejectedPromise = Promise.reject(new Error("失败"));
    console.log("已拒绝状态:", rejectedPromise); // Promise { <rejected> Error: 失败 }
}

// Promise链式调用
function promiseChainingExample() {
    console.log("=== Promise链式调用 ===");
    
    Promise.resolve(1)
        .then(value => {
            console.log("第一步:", value);
            return value + 1;
        })
        .then(value => {
            console.log("第二步:", value);
            return value * 2;
        })
        .then(value => {
            console.log("最终结果:", value);
        });
}

// ===== 9.3 Promise进阶 =====

// Promise.all示例
function promiseAllExample() {
    console.log("=== Promise.all示例 ===");
    
    const promise1 = Promise.resolve(3);
    const promise2 = new Promise(resolve => setTimeout(() => resolve('foo'), 1000));
    const promise3 = Promise.resolve(42);
    
    Promise.all([promise1, promise2, promise3])
        .then(values => {
            console.log("Promise.all结果:", values);
        })
        .catch(error => {
            console.error("至少有一个Promise被rejected:", error);
        });
}

// Promise.race示例
function promiseRaceExample() {
    console.log("=== Promise.race示例 ===");
    
    const promise1 = new Promise(resolve => setTimeout(() => resolve('one'), 500));
    const promise2 = new Promise(resolve => setTimeout(() => resolve('two'), 100));
    
    Promise.race([promise1, promise2])
        .then(value => {
            console.log("Promise.race结果:", value);
        });
}

// Promise.allSettled示例
function promiseAllSettledExample() {
    console.log("=== Promise.allSettled示例 ===");
    
    const promise1 = Promise.resolve(3);
    const promise2 = new Promise((resolve, reject) => 
        setTimeout(() => reject(new Error("失败")), 1000)
    );
    const promise3 = Promise.resolve(42);
    
    Promise.allSettled([promise1, promise2, promise3])
        .then(results => {
            console.log("Promise.allSettled结果:");
            results.forEach((result, i) => {
                if (result.status === 'fulfilled') {
                    console.log(`Promise ${i}: ${result.value}`);
                } else {
                    console.log(`Promise ${i}: ${result.reason.message}`);
                }
            });
        });
}

// ===== 9.4 Promise链式调用 =====

// 链式调用原理
function chainingPrincipleExample() {
    console.log("=== 链式调用原理 ===");
    
    new Promise(resolve => resolve(1))
        .then(value => {
            console.log(value); // 1
            return value + 1;
        })
        .then(value => {
            console.log(value); // 2
            return new Promise(resolve => setTimeout(() => resolve(value + 1), 1000));
        })
        .then(value => {
            console.log(value); // 3
        });
}

// 错误传播
function errorPropagationExample() {
    console.log("=== 错误传播 ===");
    
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
            console.error("捕获错误:", error.message);
            return "恢复后的值";
        })
        .then(value => {
            console.log("恢复后的值:", value);
        });
}

// ===== 9.5 异步函数（Async/Await） =====

// async函数基本语法
function asyncFunctionBasics() {
    console.log("=== async函数基本语法 ===");
    
    async function fetchData() {
        return "数据";
    }
    
    fetchData().then(data => console.log("async函数返回:", data));
}

// await基本用法
async function awaitBasicsExample() {
    console.log("=== await基本用法 ===");
    
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    console.log("开始");
    await delay(1000);
    console.log("1秒后");
    
    const result = await Promise.resolve("结果");
    console.log(result);
    
    try {
        const errorResult = await Promise.reject(new Error("错误"));
    } catch (error) {
        console.error(error.message);
    }
}

// 串行vs并行处理
async function serialVsParallelExample() {
    console.log("=== 串行vs并行处理 ===");
    
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function fetchData1() {
        return delay(1000).then(() => "数据1");
    }
    
    function fetchData2() {
        return delay(1000).then(() => "数据2");
    }
    
    function fetchData3() {
        return delay(1000).then(() => "数据3");
    }
    
    // 串行处理
    console.time("串行处理");
    const result1 = await fetchData1();
    const result2 = await fetchData2();
    const result3 = await fetchData3();
    console.timeEnd("串行处理");
    console.log("串行结果:", [result1, result2, result3]);
    
    // 并行处理
    console.time("并行处理");
    const [result4, result5, result6] = await Promise.all([
        fetchData1(),
        fetchData2(),
        fetchData3()
    ]);
    console.timeEnd("并行处理");
    console.log("并行结果:", [result4, result5, result6]);
}

// ===== 9.6 实际应用场景 =====

// API请求处理
async function apiRequestExample() {
    console.log("=== API请求处理 ===");
    
    // 模拟API请求
    function fetchUser(id) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (id === 1) {
                    resolve({ id, name: "张三", email: "zhangsan@example.com" });
                } else {
                    reject(new Error("用户不存在"));
                }
            }, 1000);
        });
    }
    
    // 使用async/await处理API请求
    async function fetchUserWithAsync(id) {
        try {
            const user = await fetchUser(id);
            console.log("获取用户成功:", user);
            return user;
        } catch (error) {
            console.error("获取用户数据失败:", error.message);
            throw error;
        }
    }
    
    // 使用示例
    try {
        const user = await fetchUserWithAsync(1);
        console.log("用户信息:", user);
        
        // 尝试获取不存在的用户
        await fetchUserWithAsync(2);
    } catch (error) {
        console.log("捕获到错误:", error.message);
    }
}

// 文件操作（模拟）
async function fileOperationExample() {
    console.log("=== 文件操作（模拟） ===");
    
    // 模拟文件读取
    function readFileAsText(file) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (file.endsWith(".txt")) {
                    resolve(`文件 ${file} 的内容`);
                } else {
                    reject(new Error("不支持的文件类型"));
                }
            }, 500);
        });
    }
    
    // 处理多个文件
    async function processFiles(files) {
        const results = [];
        
        for (const file of files) {
            try {
                const content = await readFileAsText(file);
                results.push({ name: file, content });
            } catch (error) {
                console.error(`读取文件 ${file} 失败:`, error.message);
                results.push({ name: file, error: error.message });
            }
        }
        
        return results;
    }
    
    // 并行处理文件
    async function processFilesInParallel(files) {
        const promises = files.map(file => 
            readFileAsText(file)
                .then(content => ({ name: file, content }))
                .catch(error => ({ name: file, error: error.message }))
        );
        
        return Promise.all(promises);
    }
    
    const files = ["document.txt", "image.jpg", "notes.txt"];
    
    console.log("串行处理文件:");
    const serialResults = await processFiles(files);
    console.log(serialResults);
    
    console.log("并行处理文件:");
    const parallelResults = await processFilesInParallel(files);
    console.log(parallelResults);
}

// 超时处理
async function timeoutExample() {
    console.log("=== 超时处理 ===");
    
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Promise超时处理
    function withTimeout(promise, timeoutMs) {
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error("操作超时")), timeoutMs);
        });
        
        return Promise.race([promise, timeoutPromise]);
    }
    
    // 使用示例
    try {
        console.log("开始一个2秒的操作，设置1秒超时");
        const result = await withTimeout(delay(2000), 1000);
        console.log("结果:", result);
    } catch (error) {
        console.error("捕获错误:", error.message);
    }
    
    try {
        console.log("开始一个500毫秒的操作，设置1秒超时");
        const result = await withTimeout(delay(500), 1000);
        console.log("结果:", result);
    } catch (error) {
        console.error("捕获错误:", error.message);
    }
}

// 重试机制
async function retryExample() {
    console.log("=== 重试机制 ===");
    
    let attemptCount = 0;
    
    function unreliableOperation() {
        attemptCount++;
        console.log(`尝试第 ${attemptCount} 次`);
        
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (attemptCount >= 3) {
                    resolve("成功！");
                } else {
                    reject(new Error("操作失败"));
                }
            }, 500);
        });
    }
    
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
    
    try {
        const result = await retry(unreliableOperation, 5, 500);
        console.log("最终结果:", result);
    } catch (error) {
        console.error("最终失败:", error.message);
    }
}

// ===== 9.7 实践练习 =====

// 练习1：实现一个简单的Promise队列
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

// 练习2：实现Promise缓存
class PromiseCache {
    constructor() {
        this.cache = new Map();
    }
    
    get(key, promiseCreator) {
        if (this.cache.has(key)) {
            const cachedPromise = this.cache.get(key);
            
            return cachedPromise.catch(() => {
                this.cache.delete(key);
                return this.createAndCache(key, promiseCreator);
            });
        }
        
        return this.createAndCache(key, promiseCreator);
    }
    
    createAndCache(key, promiseCreator) {
        const promise = promiseCreator();
        this.cache.set(key, promise);
        
        return promise;
    }
    
    delete(key) {
        return this.cache.delete(key);
    }
    
    clear() {
        this.cache.clear();
    }
}

// 练习3：实现并发限制
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
            this.process();
        }
    }
}

// ===== 9.9 常见问题与解决方案 =====

// 全局处理未捕获的Promise拒绝
function setupGlobalErrorHandling() {
    if (typeof window !== 'undefined') {
        window.addEventListener('unhandledrejection', event => {
            console.error('未处理的Promise拒绝:', event.reason);
            event.preventDefault();
        });
    }
    
    if (typeof process !== 'undefined') {
        process.on('unhandledRejection', (reason, promise) => {
            console.error('未处理的Promise拒绝:', reason);
        });
    }
}

// 循环中的异步操作
async function loopAsyncOperations() {
    console.log("=== 循环中的异步操作 ===");
    
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function processItem(item) {
        return delay(Math.random() * 1000).then(() => `处理完成: ${item}`);
    }
    
    const items = ['项目1', '项目2', '项目3', '项目4', '项目5'];
    
    // 串行处理
    console.time("串行处理");
    for (const item of items) {
        const result = await processItem(item);
        console.log(result);
    }
    console.timeEnd("串行处理");
    
    // 并行处理
    console.time("并行处理");
    const promises = items.map(item => processItem(item));
    const results = await Promise.all(promises);
    console.log(results);
    console.timeEnd("并行处理");
}

// ===== 运行所有示例 =====

function runAllExamples() {
    console.log("开始运行Promise与异步编程示例...\n");
    
    // 设置全局错误处理
    setupGlobalErrorHandling();
    
    // 运行各个示例
    callbackHellExample();
    
    setTimeout(() => {
        basicPromiseExample();
    }, 2000);
    
    setTimeout(() => {
        promiseStatesExample();
    }, 3000);
    
    setTimeout(() => {
        promiseChainingExample();
    }, 4000);
    
    setTimeout(() => {
        promiseAllExample();
    }, 5000);
    
    setTimeout(() => {
        promiseRaceExample();
    }, 6000);
    
    setTimeout(() => {
        promiseAllSettledExample();
    }, 7000);
    
    setTimeout(() => {
        chainingPrincipleExample();
    }, 8000);
    
    setTimeout(() => {
        errorPropagationExample();
    }, 9000);
    
    setTimeout(() => {
        asyncFunctionBasics();
    }, 10000);
    
    setTimeout(() => {
        awaitBasicsExample();
    }, 11000);
    
    setTimeout(() => {
        serialVsParallelExample();
    }, 13000);
    
    setTimeout(() => {
        apiRequestExample();
    }, 16000);
    
    setTimeout(() => {
        fileOperationExample();
    }, 18000);
    
    setTimeout(() => {
        timeoutExample();
    }, 20000);
    
    setTimeout(() => {
        retryExample();
    }, 22000);
    
    setTimeout(() => {
        console.log("=== Promise队列示例 ===");
        const queue = new PromiseQueue();
        
        function delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        
        queue.add(() => delay(1000).then(() => "任务1完成"))
            .then(result => console.log(result));
        
        queue.add(() => delay(500).then(() => "任务2完成"))
            .then(result => console.log(result));
        
        queue.add(() => delay(800).then(() => "任务3完成"))
            .then(result => console.log(result));
    }, 24000);
    
    setTimeout(() => {
        console.log("=== Promise缓存示例 ===");
        const cache = new PromiseCache();
        
        function fetchUserData(userId) {
            return cache.get(`user-${userId}`, () => {
                console.log(`发起用户${userId}的请求`);
                return new Promise(resolve => {
                    setTimeout(() => resolve({ id: userId, name: `用户${userId}` }), 500);
                });
            });
        }
        
        // 第一次调用会发起请求
        fetchUserData(1).then(user => console.log(user));
        
        // 第二次调用会使用缓存，不会发起新请求
        setTimeout(() => {
            fetchUserData(1).then(user => console.log(user));
        }, 100);
    }, 26000);
    
    setTimeout(() => {
        console.log("=== 并发限制示例 ===");
        const limiter = new ConcurrencyLimiter(3);
        
        function delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        
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
    }, 28000);
    
    setTimeout(() => {
        loopAsyncOperations();
    }, 30000);
}

// 导出所有函数和类
export {
    // 基础示例
    callbackHellExample,
    basicPromiseExample,
    promiseStatesExample,
    promiseChainingExample,
    
    // 进阶示例
    promiseAllExample,
    promiseRaceExample,
    promiseAllSettledExample,
    chainingPrincipleExample,
    errorPropagationExample,
    
    // Async/Await示例
    asyncFunctionBasics,
    awaitBasicsExample,
    serialVsParallelExample,
    
    // 实际应用
    apiRequestExample,
    fileOperationExample,
    timeoutExample,
    retryExample,
    
    // 实践练习类
    PromiseQueue,
    PromiseCache,
    ConcurrencyLimiter,
    
    // 问题解决方案
    setupGlobalErrorHandling,
    loopAsyncOperations,
    
    // 运行所有示例
    runAllExamples
};

// 如果直接运行此文件，则执行所有示例
if (typeof window !== 'undefined') {
    // 浏览器环境
    window.runPromiseExamples = runAllExamples;
    console.log("在浏览器控制台中运行 runPromiseExamples() 来查看所有示例");
} else if (typeof module !== 'undefined' && module.exports) {
    // Node.js环境
    module.exports = {
        callbackHellExample,
        basicPromiseExample,
        promiseStatesExample,
        promiseChainingExample,
        promiseAllExample,
        promiseRaceExample,
        promiseAllSettledExample,
        chainingPrincipleExample,
        errorPropagationExample,
        asyncFunctionBasics,
        awaitBasicsExample,
        serialVsParallelExample,
        apiRequestExample,
        fileOperationExample,
        timeoutExample,
        retryExample,
        PromiseQueue,
        PromiseCache,
        ConcurrencyLimiter,
        setupGlobalErrorHandling,
        loopAsyncOperations,
        runAllExamples
    };
}