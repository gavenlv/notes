// 第6章：异步编程与Promise - 示例代码

// ====================== 异步编程基础 ======================

// 1.1 同步与异步执行
function demonstrateSyncVsAsync() {
    console.log("=== 同步执行示例 ===");
    console.log("开始");
    
    // 模拟耗时操作（同步）
    const start = new Date().getTime();
    while (new Date().getTime() - start < 1000) {
        // 空循环，模拟耗时操作
    }
    
    console.log("耗时操作完成");
    console.log("结束");
    
    console.log("\n=== 异步执行示例 ===");
    console.log("开始");
    
    // 异步操作
    setTimeout(function() {
        console.log("异步操作完成");
    }, 1000);
    
    console.log("结束");
}

// 1.2 常见的异步操作
function commonAsyncOperations() {
    // setTimeout
    console.log("设置定时器，2秒后执行");
    setTimeout(function() {
        console.log("定时器执行了！");
    }, 2000);
    
    // setInterval
    let counter = 0;
    console.log("设置重复定时器，每秒执行一次");
    const intervalId = setInterval(function() {
        counter++;
        console.log(`定时器执行次数: ${counter}`);
        
        if (counter >= 5) {
            clearInterval(intervalId);
            console.log("定时器已停止");
        }
    }, 1000);
}

// ====================== 回调函数 ======================

// 2.1 基本回调函数
function basicCallbackExample() {
    function process(value, callback) {
        const result = `处理后的值: ${value}`;
        callback(result);
    }
    
    process("原始数据", function(result) {
        console.log(`回调函数接收到: ${result}`);
    });
}

// 2.2 异步回调
function asyncCallbackExample() {
    function asyncProcess(value, callback) {
        console.log("开始异步处理...");
        
        setTimeout(function() {
            const result = `异步处理 ${value}`;
            callback(result);
        }, 1000);
    }
    
    asyncProcess("数据", function(result) {
        console.log(`异步回调接收到: ${result}`);
    });
}

// 2.3 回调地狱
function callbackHell() {
    function step1(callback) {
        setTimeout(function() {
            console.log("步骤1完成");
            callback("结果1");
        }, 500);
    }
    
    function step2(data, callback) {
        setTimeout(function() {
            console.log(`步骤2完成，输入: ${data}`);
            callback("结果2");
        }, 500);
    }
    
    function step3(data, callback) {
        setTimeout(function() {
            console.log(`步骤3完成，输入: ${data}`);
            callback("最终结果");
        }, 500);
    }
    
    step1(function(result1) {
        step2(result1, function(result2) {
            step3(result2, function(finalResult) {
                console.log(`完成: ${finalResult}`);
            });
        });
    });
}

// 2.4 回调函数的错误处理
function callbackErrorHandling() {
    function fetchData(success, callback) {
        setTimeout(function() {
            if (success) {
                callback(null, { id: 1, name: "数据" });
            } else {
                callback(new Error("获取数据失败"));
            }
        }, 1000);
    }
    
    fetchData(true, function(error, data) {
        if (error) {
            console.error(`错误: ${error.message}`);
            return;
        }
        
        console.log(`成功: ${JSON.stringify(data)}`);
    });
    
    fetchData(false, function(error, data) {
        if (error) {
            console.error(`错误: ${error.message}`);
            return;
        }
        
        console.log(`成功: ${JSON.stringify(data)}`);
    });
}

// ====================== Promise基础 ======================

// 3.1 创建和使用Promise
function createAndUsePromise() {
    // 创建Promise
    const promise = new Promise(function(resolve, reject) {
        const success = Math.random() > 0.5;
        
        setTimeout(function() {
            if (success) {
                resolve("操作成功");
            } else {
                reject(new Error("操作失败"));
            }
        }, 1000);
    });
    
    // 使用Promise
    promise
        .then(function(result) {
            console.log(`Promise状态: fulfilled，结果: ${result}`);
        })
        .catch(function(error) {
            console.log(`Promise状态: rejected，错误: ${error.message}`);
        });
}

// 3.2 Promise链式调用
function promiseChaining() {
    function step1(data) {
        return new Promise(function(resolve) {
            setTimeout(function() {
                const result = `${data} -> 步骤1处理`;
                console.log(`步骤1完成: ${result}`);
                resolve(result);
            }, 500);
        });
    }
    
    function step2(data) {
        return new Promise(function(resolve) {
            setTimeout(function() {
                const result = `${data} -> 步骤2处理`;
                console.log(`步骤2完成: ${result}`);
                resolve(result);
            }, 500);
        });
    }
    
    function step3(data) {
        return new Promise(function(resolve) {
            setTimeout(function() {
                const result = `${data} -> 步骤3处理`;
                console.log(`步骤3完成: ${result}`);
                resolve(result);
            }, 500);
        });
    }
    
    step1("初始数据")
        .then(step2)
        .then(step3)
        .then(function(finalResult) {
            console.log(`最终结果: ${finalResult}`);
        })
        .catch(function(error) {
            console.error(`错误: ${error.message}`);
        });
}

// 3.3 Promise错误处理
function promiseErrorHandling() {
    const successPromise = new Promise(function(resolve) {
        setTimeout(function() {
            resolve("成功数据");
        }, 500);
    });
    
    const failurePromise = new Promise(function(resolve, reject) {
        setTimeout(function() {
            reject(new Error("失败原因"));
        }, 500);
    });
    
    successPromise
        .then(function(result) {
            console.log(`成功Promise结果: ${result}`);
        })
        .catch(function(error) {
            console.error(`成功Promise错误: ${error.message}`);
        });
    
    failurePromise
        .then(function(result) {
            console.log(`失败Promise结果: ${result}`);
        })
        .catch(function(error) {
            console.error(`失败Promise错误: ${error.message}`);
        });
}

// ====================== async/await ======================

// 4.1 async函数基础
function asyncFunctionBasics() {
    // async函数总是返回Promise
    async function fetchData() {
        return "从async函数返回的数据";
    }
    
    fetchData().then(data => console.log(`async函数返回: ${data}`));
    
    // 直接返回Promise
    async function fetchWithPromise() {
        return new Promise(function(resolve) {
            setTimeout(function() {
                resolve("Promise解析的数据");
            }, 1000);
        });
    }
    
    fetchWithPromise().then(data => console.log(`async函数中的Promise: ${data}`));
}

// 4.2 await示例
function awaitExample() {
    function getData() {
        return new Promise(function(resolve) {
            setTimeout(function() {
                resolve("异步获取的数据");
            }, 1000);
        });
    }
    
    async function processData() {
        console.log("开始处理...");
        const data = await getData();
        console.log(`获取到数据: ${data}`);
        return `处理后的${data}`;
    }
    
    processData().then(result => console.log(`最终结果: ${result}`));
}

// 4.3 async错误处理
function asyncErrorHandling() {
    async function fetchData(success) {
        return new Promise(function(resolve, reject) {
            setTimeout(function() {
                if (success) {
                    resolve("成功数据");
                } else {
                    reject(new Error("获取数据失败"));
                }
            }, 1000);
        });
    }
    
    async function processSuccess() {
        try {
            const data = await fetchData(true);
            console.log(`成功处理: ${data}`);
        } catch (error) {
            console.error(`捕获错误: ${error.message}`);
        }
    }
    
    async function processFailure() {
        try {
            const data = await fetchData(false);
            console.log(`成功处理: ${data}`);
        } catch (error) {
            console.error(`捕获错误: ${error.message}`);
        }
    }
    
    processSuccess();
    processFailure();
}

// 4.4 并行与顺序执行
function parallelVsSequential() {
    // 并行执行
    async function parallelExecution() {
        console.log("开始并行获取所有数据...");
        const startTime = Date.now();
        
        const [users, posts, comments] = await Promise.all([
            fetchUsers(),
            fetchPosts(),
            fetchComments()
        ]);
        
        const endTime = Date.now();
        console.log(`所有数据获取完成，耗时: ${endTime - startTime}ms`);
        
        return { users, posts, comments };
    }
    
    // 顺序执行
    async function sequentialExecution() {
        console.log("开始顺序处理...");
        const startTime = Date.now();
        
        const result1 = await step1();
        const result2 = await step2(result1);
        const result3 = await step3(result2);
        
        const endTime = Date.now();
        console.log(`所有步骤完成，耗时: ${endTime - startTime}ms`);
        
        return result3;
    }
    
    // 辅助函数
    function fetchUsers() {
        return new Promise(function(resolve) {
            setTimeout(function() {
                console.log("获取用户完成");
                resolve([{ id: 1, name: "张三" }]);
            }, 1000);
        });
    }
    
    function fetchPosts() {
        return new Promise(function(resolve) {
            setTimeout(function() {
                console.log("获取文章完成");
                resolve([{ id: 1, title: "文章1" }]);
            }, 800);
        });
    }
    
    function fetchComments() {
        return new Promise(function(resolve) {
            setTimeout(function() {
                console.log("获取评论完成");
                resolve([{ id: 1, content: "评论1" }]);
            }, 1200);
        });
    }
    
    function step1() {
        return new Promise(function(resolve) {
            setTimeout(function() {
                console.log("步骤1完成");
                resolve("步骤1的结果");
            }, 800);
        });
    }
    
    function step2(data) {
        return new Promise(function(resolve) {
            setTimeout(function() {
                console.log(`步骤2完成，输入: ${data}`);
                resolve(`处理${data}后的结果`);
            }, 600);
        });
    }
    
    function step3(data) {
        return new Promise(function(resolve) {
            setTimeout(function() {
                console.log(`步骤3完成，输入: ${data}`);
                resolve(`最终处理${data}后的结果`);
            }, 1000);
        });
    }
    
    // 执行示例
    parallelExecution().then(result => {
        console.log(`并行执行结果: ${JSON.stringify(result)}`);
    });
    
    sequentialExecution().then(result => {
        console.log(`顺序执行结果: ${result}`);
    });
}

// ====================== Promise方法 ======================

// 5.1 Promise.resolve和Promise.reject
function promiseResolveReject() {
    // Promise.resolve
    const valuePromise = Promise.resolve("普通值");
    valuePromise.then(value => console.log(`解析普通值: ${value}`));
    
    // 解析Promise
    const originalPromise = new Promise(resolve => 
        setTimeout(() => resolve("原始Promise的值"), 1000)
    );
    const wrappedPromise = Promise.resolve(originalPromise);
    wrappedPromise.then(value => console.log(`解析Promise: ${value}`));
    
    // Promise.reject
    Promise.reject(new Error("拒绝的原因"))
        .catch(error => console.error(`捕获错误: ${error.message}`));
}

// 5.2 Promise组合方法
function promiseCombinationMethods() {
    // Promise.all
    const promise1 = Promise.resolve(3);
    const promise2 = new Promise(resolve => setTimeout(() => resolve(5), 1000));
    const promise3 = Promise.resolve(10);
    
    Promise.all([promise1, promise2, promise3])
        .then(values => {
            console.log(`Promise.all结果: [${values.join(', ')}]`);
        })
        .catch(error => {
            console.error(`Promise.all错误: ${error.message}`);
        });
    
    // Promise.race
    const race1 = new Promise(resolve => setTimeout(() => resolve("第一个完成"), 500));
    const race2 = new Promise(resolve => setTimeout(() => resolve("第二个完成"), 1000));
    
    Promise.race([race1, race2])
        .then(value => {
            console.log(`Promise.race结果: ${value}`);
        });
    
    // Promise.allSettled
    const settled1 = Promise.resolve(3);
    const settled2 = new Promise((resolve, reject) => setTimeout(() => reject("失败"), 1000));
    const settled3 = Promise.resolve(10);
    
    Promise.allSettled([settled1, settled2, settled3])
        .then(results => {
            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    console.log(`Promise ${index + 1} 成功: ${result.value}`);
                } else {
                    console.log(`Promise ${index + 1} 失败: ${result.reason}`);
                }
            });
        });
}

// ====================== 实际应用示例 ======================

// 6.1 网络请求
function networkRequests() {
    // 模拟fetch请求
    function mockFetch(url) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (url.includes('users/1')) {
                    resolve({
                        ok: true,
                        json: () => Promise.resolve({ id: 1, name: '张三', email: 'zhangsan@example.com' })
                    });
                } else if (url.includes('posts')) {
                    resolve({
                        ok: true,
                        json: () => Promise.resolve([
                            { id: 1, title: '张三的文章1', userId: 1 },
                            { id: 2, title: '张三的文章2', userId: 1 }
                        ])
                    });
                } else if (url.includes('comments')) {
                    resolve({
                        ok: true,
                        json: () => Promise.resolve([
                            { id: 1, content: '评论1', postId: 1 },
                            { id: 2, content: '评论2', postId: 2 }
                        ])
                    });
                } else {
                    reject(new Error('不支持的URL'));
                }
            }, 800);
        });
    }
    
    // 使用Promise链处理
    function fetchWithPromiseChain() {
        mockFetch('https://api.example.com/users/1')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP错误: ${response.status}`);
                return response.json();
            })
            .then(user => {
                console.log(`获取用户: ${JSON.stringify(user)}`);
                return mockFetch(`https://api.example.com/posts?userId=${user.id}`);
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP错误: ${response.status}`);
                return response.json();
            })
            .then(posts => {
                console.log(`获取文章: ${JSON.stringify(posts)}`);
                const postIds = posts.map(post => post.id).join(',');
                return mockFetch(`https://api.example.com/comments?postId=${postIds}`);
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP错误: ${response.status}`);
                return response.json();
            })
            .then(comments => {
                console.log(`获取评论: ${JSON.stringify(comments)}`);
            })
            .catch(error => {
                console.error(`请求失败: ${error.message}`);
            });
    }
    
    // 使用async/await处理
    async function fetchWithAsyncAwait() {
        try {
            const userResponse = await mockFetch('https://api.example.com/users/1');
            if (!userResponse.ok) throw new Error(`HTTP错误: ${userResponse.status}`);
            const user = await userResponse.json();
            console.log(`获取用户: ${JSON.stringify(user)}`);
            
            const postsResponse = await mockFetch(`https://api.example.com/posts?userId=${user.id}`);
            if (!postsResponse.ok) throw new Error(`HTTP错误: ${postsResponse.status}`);
            const posts = await postsResponse.json();
            console.log(`获取文章: ${JSON.stringify(posts)}`);
            
            const postIds = posts.map(post => post.id).join(',');
            const commentsResponse = await mockFetch(`https://api.example.com/comments?postId=${postIds}`);
            if (!commentsResponse.ok) throw new Error(`HTTP错误: ${commentsResponse.status}`);
            const comments = await commentsResponse.json();
            console.log(`获取评论: ${JSON.stringify(comments)}`);
            
            return { user, posts, comments };
        } catch (error) {
            console.error(`请求失败: ${error.message}`);
            throw error;
        }
    }
    
    fetchWithPromiseChain();
    fetchWithAsyncAwait();
}

// 6.2 文件操作
function fileOperations() {
    // 模拟文件读取
    function readFile(filename) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (filename.endsWith('.txt')) {
                    resolve(`文件内容: ${filename}`);
                } else {
                    reject(new Error('不支持的文件类型'));
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
                console.log(`成功读取: ${filename}`);
            } catch (error) {
                results.push({ filename, error: error.message });
                console.error(`读取失败: ${filename} - ${error.message}`);
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
    
    const files = ['file1.txt', 'file2.txt', 'document.txt', 'image.jpg'];
    
    readFilesInOrder(files).then(results => {
        console.log('顺序读取结果:', results);
    });
    
    readFilesInParallel(files).then(results => {
        console.log('并行读取结果:', results);
    });
}

// ====================== 高级技巧 ======================

// 7.1 超时处理
function timeoutHandling() {
    function withTimeout(promise, timeout) {
        return Promise.race([
            promise,
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error("操作超时")), timeout)
            )
        ]);
    }
    
    // 快速操作
    const fastOperation = new Promise(resolve => 
        setTimeout(() => resolve("快速操作完成"), 800)
    );
    
    // 慢速操作
    const slowOperation = new Promise(resolve => 
        setTimeout(() => resolve("慢速操作完成"), 2000)
    );
    
    // 测试快速操作（1秒超时）
    withTimeout(fastOperation, 1000)
        .then(result => {
            console.log(`快速操作结果: ${result}`);
        })
        .catch(error => {
            console.error(`快速操作错误: ${error.message}`);
        });
    
    // 测试慢速操作（1秒超时）
    withTimeout(slowOperation, 1000)
        .then(result => {
            console.log(`慢速操作结果: ${result}`);
        })
        .catch(error => {
            console.error(`慢速操作错误: ${error.message}`);
        });
}

// 7.2 重试机制
function retryMechanism() {
    function retry(promiseGenerator, maxAttempts = 3, delay = 500) {
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
                            console.log(`尝试 ${attempt} 失败，${delay}ms后重试...`);
                            setTimeout(tryAgain, delay);
                        }
                    });
            }
            
            tryAgain();
        });
    }
    
    function unreliableOperation() {
        return new Promise((resolve, reject) => {
            const success = Math.random() > 0.7; // 30%成功率
            
            if (success) {
                resolve("操作成功");
            } else {
                reject(new Error("操作失败"));
            }
        });
    }
    
    retry(() => unreliableOperation(), 5, 800)
        .then(result => {
            console.log(`最终结果: ${result}`);
        })
        .catch(error => {
            console.error(`所有尝试均失败: ${error.message}`);
        });
}

// 7.3 缓存Promise结果
function promiseMemoization() {
    function memoize(promiseGenerator) {
        let cachedPromise = null;
        
        return function(...args) {
            if (cachedPromise) {
                console.log("使用缓存结果");
                return cachedPromise;
            }
            
            console.log("发起新请求");
            cachedPromise = promiseGenerator(...args)
                .finally(() => {
                    // 5秒后清除缓存
                    setTimeout(() => {
                        cachedPromise = null;
                        console.log("缓存已清除");
                    }, 5000);
                });
            
            return cachedPromise;
        };
    }
    
    const fetchUserMemoized = memoize(userId => 
        new Promise(resolve => 
            setTimeout(() => resolve({ id: userId, name: `用户${userId}` }), 1000)
        )
    );
    
    // 第一次调用
    fetchUserMemoized(123).then(user => {
        console.log(`第一次调用结果: ${JSON.stringify(user)}`);
    });
    
    // 第二次调用（使用缓存）
    setTimeout(() => {
        fetchUserMemoized(123).then(user => {
            console.log(`第二次调用结果: ${JSON.stringify(user)}`);
        });
    }, 1500);
    
    // 不同用户（新请求）
    setTimeout(() => {
        fetchUserMemoized(456).then(user => {
            console.log(`不同用户结果: ${JSON.stringify(user)}`);
        });
    }, 2000);
}

// 7.4 并发限制
function concurrentLimit() {
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
            
            console.log(`开始执行，当前并发数: ${this.running}`);
            
            promiseGenerator()
                .then(result => {
                    console.log(`执行成功，结果: ${result}`);
                    resolve(result);
                })
                .catch(error => {
                    console.error(`执行失败，错误: ${error.message}`);
                    reject(error);
                })
                .finally(() => {
                    this.running--;
                    console.log(`执行完成，当前并发数: ${this.running}`);
                    this.process();
                });
        }
    }
    
    const pool = new PromisePool(2); // 最多同时执行2个请求
    
    const urls = [
        'https://api.example.com/data1',
        'https://api.example.com/data2',
        'https://api.example.com/data3',
        'https://api.example.com/data4',
        'https://api.example.com/data5'
    ];
    
    const promises = urls.map((url, index) => 
        pool.add(() => 
            new Promise(resolve => 
                setTimeout(() => resolve(`数据${index + 1}`), Math.random() * 2000 + 500)
            )
        )
    );
    
    Promise.all(promises)
        .then(results => {
            console.log(`所有请求完成: [${results.join(', ')}]`);
        })
        .catch(error => {
            console.error(`请求失败: ${error.message}`);
        });
}

// ====================== 动画序列 ======================

// 8.1 动画序列
function animationSequence() {
    // 创建Promise封装的动画函数
    function animate(element, duration, properties) {
        return new Promise(resolve => {
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
    
    // 顺序动画
    async function sequentialAnimation(box) {
        box.style.left = '20px';
        box.style.top = '20px';
        
        await animate(box, 1000, { left: 200 });
        console.log('右移动画完成');
        
        await animate(box, 1000, { top: 150 });
        console.log('下移动画完成');
        
        await animate(box, 1000, { left: 20 });
        console.log('左移动画完成');
        
        await animate(box, 1000, { top: 20 });
        console.log('上移动画完成');
        
        console.log('顺序动画完成！');
    }
    
    // 并行动画
    async function parallelAnimation(box) {
        box.style.left = '20px';
        box.style.top = '20px';
        
        await Promise.all([
            animate(box, 2000, { left: 200 }),
            animate(box, 2000, { top: 150 })
        ]);
        
        console.log('并行动画完成！');
    }
    
    // 假设有一个元素
    const box = document.createElement('div');
    box.style.position = 'absolute';
    box.style.width = '100px';
    box.style.height = '100px';
    box.style.backgroundColor = '#e74c3c';
    box.style.color = 'white';
    box.style.display = 'flex';
    box.style.alignItems = 'center';
    box.style.justifyContent = 'center';
    box.style.left = '20px';
    box.style.top = '20px';
    box.textContent = '动画方块';
    
    // 在实际应用中，需要将元素添加到DOM中
    // document.body.appendChild(box);
    
    // 执行动画（如果元素在DOM中）
    // sequentialAnimation(box);
    // parallelAnimation(box);
}

// 8.2 进度指示器
function progressIndicator() {
    async function progressDemo() {
        let progress = 0;
        
        function updateProgress() {
            return new Promise(resolve => {
                setTimeout(() => {
                    progress += Math.random() * 15;
                    if (progress > 100) progress = 100;
                    
                    // 在实际应用中，更新进度条
                    console.log(`进度: ${progress.toFixed(1)}%`);
                    
                    resolve(progress);
                }, 300);
            });
        }
        
        while (progress < 100) {
            await updateProgress();
        }
        
        console.log('进度演示完成！');
    }
    
    progressDemo();
}

// ====================== 性能优化 ======================

// 9.1 避免不必要的await
function optimizeAsyncExecution() {
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
    
    // 辅助函数
    function fetchUser() {
        return new Promise(resolve => 
            setTimeout(() => resolve({ id: 1, name: '张三' }), 1000)
        );
    }
    
    function fetchPosts() {
        return new Promise(resolve => 
            setTimeout(() => resolve([{ id: 1, title: '文章1' }]), 800)
        );
    }
    
    function fetchComments() {
        return new Promise(resolve => 
            setTimeout(() => resolve([{ id: 1, content: '评论1' }]), 1200)
        );
    }
}

// 9.2 使用Promise.allSettled代替Promise.all
function allSettledVsAll() {
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
            console.log('用户信息:', profile.value);
        }
        
        if (preferences.status === 'fulfilled') {
            console.log('用户偏好:', preferences.value);
        }
        
        // 处理失败的操作但不影响其他操作
        if (notifications.status === 'rejected') {
            console.warn('获取通知失败:', notifications.reason.message);
        }
        
        return results;
    }
    
    // 辅助函数
    function fetchUserProfile() {
        return new Promise(resolve => 
            setTimeout(() => resolve({ name: '张三', email: 'zhang@example.com' }), 800)
        );
    }
    
    function fetchUserPreferences() {
        return new Promise(resolve => 
            setTimeout(() => resolve({ theme: 'dark', language: 'zh-CN' }), 600)
        );
    }
    
    function fetchUserNotifications() {
        return new Promise((resolve, reject) => 
            setTimeout(() => reject(new Error('通知服务不可用')), 500)
        );
    }
    
    function fetchUserActivity() {
        return new Promise(resolve => 
            setTimeout(() => resolve({ lastLogin: '2023-06-01', postsCount: 5 }), 1000)
        );
    }
    
    fetchMultipleDataSomeMayFail();
}

// 9.3 延迟执行
function delayedExecution() {
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
    
    // 模拟fetch重试（在实际应用中使用真实URL）
    fetchWithRetry('https://api.example.com/data', 3, 1000)
        .then(data => console.log('获取数据成功:', data))
        .catch(error => console.error('获取数据失败:', error.message));
}