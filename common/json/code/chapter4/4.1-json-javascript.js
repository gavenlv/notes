// JSON与JavaScript交互示例
// 此文件展示了在JavaScript中如何创建、解析、修改和使用JSON数据

// ==================== 基本JSON操作 ====================

// 1. 将JavaScript对象转换为JSON字符串
function jsObjectToJson() {
    const user = {
        id: 123,
        name: "张三",
        email: "zhangsan@example.com",
        isActive: true,
        roles: ["user", "editor"],
        profile: {
            age: 30,
            city: "北京",
            bio: "JavaScript开发者，专注于前端技术。"
        }
    };
    
    // 使用JSON.stringify()将对象转换为JSON字符串
    const jsonString = JSON.stringify(user);
    console.log("基本JSON字符串:", jsonString);
    
    // 使用缩进格式化JSON
    const formattedJson = JSON.stringify(user, null, 2);
    console.log("格式化的JSON:", formattedJson);
    
    return { jsonString, formattedJson };
}

// 2. 将JSON字符串解析为JavaScript对象
function jsonToJsObject(jsonString) {
    try {
        // 使用JSON.parse()将JSON字符串解析为对象
        const user = JSON.parse(jsonString);
        console.log("解析后的对象:", user);
        
        // 访问对象属性
        console.log("用户名:", user.name);
        console.log("用户角色:", user.roles);
        console.log("用户所在城市:", user.profile.city);
        
        return user;
    } catch (error) {
        console.error("JSON解析错误:", error.message);
        return null;
    }
}

// 3. 使用replacer函数控制序列化过程
function jsonWithReplacer() {
    const product = {
        id: "prod_123",
        name: "智能手机",
        price: 3999.00,
        currency: "CNY",
        inStock: true,
        category: "电子产品",
        secretData: "这是不应该序列化的敏感信息",
        tags: ["新品", "热卖"],
        manufacturer: {
            name: "科技公司",
            country: "中国"
        }
    };
    
    // 定义replacer函数，控制哪些属性被序列化
    const replacer = function(key, value) {
        // 排除敏感数据
        if (key === "secretData") {
            return undefined;
        }
        
        // 格式化价格
        if (key === "price") {
            return `¥${value.toFixed(2)}`;
        }
        
        return value;
    };
    
    const jsonString = JSON.stringify(product, replacer, 2);
    console.log("使用replacer的JSON:", jsonString);
    
    return jsonString;
}

// 4. 使用reviver函数控制反序列化过程
function jsonWithReviver(jsonString) {
    const reviver = function(key, value) {
        // 自动转换日期字符串
        if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
            return new Date(value);
        }
        
        // 转换价格字符串回数字
        if (key === "price" && typeof value === 'string' && value.startsWith('¥')) {
            return parseFloat(value.substring(1));
        }
        
        return value;
    };
    
    const obj = JSON.parse(jsonString, reviver);
    console.log("使用reviver解析的对象:", obj);
    console.log("价格类型:", typeof obj.price);
    
    return obj;
}

// ==================== 高级JSON操作 ====================

// 5. 深度克隆对象
function deepCloneObject(originalObj) {
    // 使用JSON实现深度克隆
    const jsonString = JSON.stringify(originalObj);
    const clonedObj = JSON.parse(jsonString);
    
    console.log("原始对象:", originalObj);
    console.log("克隆对象:", clonedObj);
    
    // 修改克隆对象不影响原始对象
    clonedObj.name = "修改后的名字";
    console.log("修改后 - 原始对象:", originalObj);
    console.log("修改后 - 克隆对象:", clonedObj);
    
    // 注意：此方法的局限性
    // - 不能复制函数、undefined、Symbol
    // - 会丢失原型链
    // - Date对象会被转换为字符串
    
    return clonedObj;
}

// 6. 循环引用处理
function handleCircularReference() {
    const user = {
        id: 123,
        name: "张三"
    };
    
    // 创建循环引用
    user.self = user;
    
    try {
        // 直接序列化会导致错误
        JSON.stringify(user);
    } catch (error) {
        console.error("循环引用错误:", error.message);
        
        // 处理循环引用的解决方案
        const getCircularReplacer = () => {
            const seen = new WeakSet();
            return (key, value) => {
                if (typeof value === "object" && value !== null) {
                    if (seen.has(value)) {
                        return "[循环引用]";
                    }
                    seen.add(value);
                }
                return value;
            };
        };
        
        const safeJsonString = JSON.stringify(user, getCircularReplacer(), 2);
        console.log("处理循环引用的JSON:", safeJsonString);
        
        return safeJsonString;
    }
}

// 7. 大型JSON处理 - 流式处理
function processLargeJsonData() {
    // 模拟大型数据集
    const largeDataSet = Array.from({ length: 10000 }, (_, i) => ({
        id: i + 1,
        name: `用户${i + 1}`,
        email: `user${i + 1}@example.com`,
        isActive: Math.random() > 0.3,
        registrationDate: new Date(Date.now() - Math.floor(Math.random() * 365 * 24 * 60 * 60 * 1000)).toISOString(),
        profile: {
            age: Math.floor(Math.random() * 50) + 18,
            city: ["北京", "上海", "广州", "深圳", "杭州"][Math.floor(Math.random() * 5)],
            preferences: {
                theme: Math.random() > 0.5 ? "dark" : "light",
                notifications: Math.random() > 0.2,
                language: ["zh-CN", "en-US", "ja-JP"][Math.floor(Math.random() * 3)]
            }
        }
    }));
    
    console.time("序列化大型数据集");
    const jsonString = JSON.stringify(largeDataSet);
    console.timeEnd("序列化大型数据集");
    
    console.log("JSON大小:", jsonString.length / 1024 / 1024, "MB");
    
    // 流式处理函数
    function processJsonStream(jsonString, chunkSize = 1000) {
        const parsedArray = JSON.parse(jsonString);
        const totalItems = parsedArray.length;
        let processedCount = 0;
        
        // 分批处理数据
        function processNextChunk() {
            const end = Math.min(processedCount + chunkSize, totalItems);
            
            for (let i = processedCount; i < end; i++) {
                const item = parsedArray[i];
                // 执行处理逻辑
                item.processed = true;
                item.processTime = new Date().toISOString();
            }
            
            processedCount = end;
            console.log(`已处理: ${processedCount}/${totalItems} 项`);
            
            if (processedCount < totalItems) {
                // 使用setTimeout防止阻塞UI
                setTimeout(processNextChunk, 10);
            } else {
                console.log("所有数据处理完成");
                console.time("处理大型数据集");
                const processedJson = JSON.stringify(parsedArray);
                console.timeEnd("处理大型数据集");
            }
        }
        
        processNextChunk();
    }
    
    processJsonStream(jsonString);
    
    return jsonString;
}

// ==================== Web应用中的JSON示例 ====================

// 8. API请求与响应
async function fetchJsonData() {
    // 模拟API请求
    const mockFetch = (url, options) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                if (url.includes("/api/users")) {
                    resolve({
                        ok: true,
                        status: 200,
                        json: () => Promise.resolve({
                            data: [
                                { id: 1, name: "张三", email: "zhangsan@example.com" },
                                { id: 2, name: "李四", email: "lisi@example.com" },
                                { id: 3, name: "王五", email: "wangwu@example.com" }
                            ],
                            meta: {
                                total: 3,
                                page: 1,
                                perPage: 10
                            }
                        })
                    });
                } else if (url.includes("/api/users") && options.method === "POST") {
                    resolve({
                        ok: true,
                        status: 201,
                        json: () => Promise.resolve({
                            data: {
                                id: 4,
                                name: "赵六",
                                email: "zhaoliu@example.com",
                                createdAt: new Date().toISOString()
                            }
                        })
                    });
                }
            }, 500);
        });
    };
    
    try {
        // GET请求获取数据
        console.log("发送GET请求...");
        const response = await mockFetch("/api/users");
        
        if (response.ok) {
            const data = await response.json();
            console.log("获取的用户数据:", data);
            
            // 处理数据
            const users = data.data.map(user => ({
                ...user,
                displayName: user.name + " (" + user.email + ")"
            }));
            
            console.log("处理后的用户:", users);
        }
        
        // POST请求发送数据
        console.log("发送POST请求...");
        const newUser = {
            name: "赵六",
            email: "zhaoliu@example.com",
            isActive: true
        };
        
        const postResponse = await mockFetch("/api/users", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newUser)
        });
        
        if (postResponse.ok) {
            const createdUser = await postResponse.json();
            console.log("创建的用户:", createdUser);
        }
    } catch (error) {
        console.error("API请求错误:", error);
    }
}

// 9. 本地存储中的JSON
function localStorageJsonExample() {
    // 应用配置
    const appConfig = {
        theme: "dark",
        language: "zh-CN",
        notifications: {
            email: true,
            push: false,
            sms: true
        },
        userPreferences: {
            autoSave: true,
            showHints: true,
            compactView: false
        },
        lastLogin: new Date().toISOString(),
        sessionTimeout: 30 // 分钟
    };
    
    // 保存配置到本地存储
    try {
        localStorage.setItem("appConfig", JSON.stringify(appConfig));
        console.log("配置已保存到本地存储");
    } catch (error) {
        console.error("保存配置失败:", error.message);
    }
    
    // 从本地存储读取配置
    try {
        const storedConfig = localStorage.getItem("appConfig");
        if (storedConfig) {
            const config = JSON.parse(storedConfig);
            console.log("从本地存储读取的配置:", config);
            
            // 更新配置
            config.lastLogin = new Date().toISOString();
            config.userPreferences.showHints = false;
            
            // 保存更新后的配置
            localStorage.setItem("appConfig", JSON.stringify(config));
            console.log("配置已更新并保存");
        }
    } catch (error) {
        console.error("读取配置失败:", error.message);
    }
    
    // 处理本地存储容量问题
    function checkLocalStorageCapacity() {
        const testKey = "storage_test";
        const testData = { data: "x" };
        
        try {
            // 逐步增加数据量直到达到上限
            for (let i = 1; i <= 10000; i++) {
                testData.data = "x".repeat(i * 1000);
                localStorage.setItem(testKey, JSON.stringify(testData));
            }
        } catch (error) {
            console.log("本地存储大约容量限制:", i * 1000, "字符");
            localStorage.removeItem(testKey);
        }
    }
    
    checkLocalStorageCapacity();
}

// 10. IndexedDB中的JSON
function indexedDbJsonExample() {
    // 初始化IndexedDB
    const initIndexedDB = () => {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open("JsonExampleDB", 1);
            
            request.onerror = (event) => {
                console.error("IndexedDB打开失败:", event);
                reject(new Error("数据库打开失败"));
            };
            
            request.onsuccess = (event) => {
                const db = event.target.result;
                console.log("IndexedDB打开成功");
                resolve(db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // 创建对象存储
                if (!db.objectStoreNames.contains("users")) {
                    const userStore = db.createObjectStore("users", { keyPath: "id" });
                    userStore.createIndex("email", "email", { unique: true });
                    userStore.createIndex("name", "name", { unique: false });
                }
                
                if (!db.objectStoreNames.contains("products")) {
                    const productStore = db.createObjectStore("products", { keyPath: "id", autoIncrement: true });
                    productStore.createIndex("category", "category", { unique: false });
                }
            };
        });
    };
    
    // 添加数据到IndexedDB
    const addDataToIndexedDB = async (db) => {
        try {
            const transaction = db.transaction(["users", "products"], "readwrite");
            
            // 添加用户
            const userStore = transaction.objectStore("users");
            
            const users = [
                {
                    id: 1,
                    name: "张三",
                    email: "zhangsan@example.com",
                    profile: {
                        age: 30,
                        city: "北京",
                        preferences: {
                            theme: "dark",
                            notifications: true
                        }
                    },
                    createdAt: new Date().toISOString()
                },
                {
                    id: 2,
                    name: "李四",
                    email: "lisi@example.com",
                    profile: {
                        age: 25,
                        city: "上海",
                        preferences: {
                            theme: "light",
                            notifications: false
                        }
                    },
                    createdAt: new Date().toISOString()
                }
            ];
            
            users.forEach(user => {
                userStore.add(user);
            });
            
            // 添加产品
            const productStore = transaction.objectStore("products");
            
            const products = [
                {
                    name: "智能手机",
                    category: "电子产品",
                    price: 3999.00,
                    inStock: true,
                    tags: ["新品", "热卖"],
                    specs: {
                        brand: "TechBrand",
                        model: "X100",
                        screen: "6.1英寸"
                    }
                },
                {
                    name: "笔记本电脑",
                    category: "电子产品",
                    price: 8999.00,
                    inStock: true,
                    tags: ["高性能"],
                    specs: {
                        brand: "CompuBrand",
                        model: "ProBook",
                        screen: "15.6英寸",
                        cpu: "Intel i7"
                    }
                }
            ];
            
            products.forEach(product => {
                productStore.add(product);
            });
            
            await new Promise((resolve, reject) => {
                transaction.oncomplete = () => {
                    console.log("数据已添加到IndexedDB");
                    resolve();
                };
                
                transaction.onerror = (event) => {
                    console.error("添加数据失败:", event);
                    reject(new Error("添加数据失败"));
                };
            });
        } catch (error) {
            console.error("IndexedDB操作错误:", error);
        }
    };
    
    // 从IndexedDB查询数据
    const queryDataFromIndexedDB = async (db) => {
        try {
            const transaction = db.transaction(["users", "products"], "readonly");
            const userStore = transaction.objectStore("users");
            const productStore = transaction.objectStore("products");
            
            // 获取所有用户
            const getAllUsers = new Promise((resolve) => {
                const request = userStore.getAll();
                request.onsuccess = (event) => {
                    resolve(event.target.result);
                };
            });
            
            // 通过索引查询产品
            const getElectronics = new Promise((resolve) => {
                const index = productStore.index("category");
                const request = index.getAll("电子产品");
                request.onsuccess = (event) => {
                    resolve(event.target.result);
                };
            });
            
            const [users, electronics] = await Promise.all([getAllUsers, getElectronics]);
            
            console.log("查询到的用户:", users);
            console.log("查询到的电子产品:", electronics);
            
            // 将结果转换为JSON字符串
            const usersJson = JSON.stringify(users, null, 2);
            const electronicsJson = JSON.stringify(electronics, null, 2);
            
            console.log("用户JSON:", usersJson);
            console.log("电子产品JSON:", electronicsJson);
            
            return { users, electronics };
        } catch (error) {
            console.error("查询数据错误:", error);
            return { users: [], electronics: [] };
        }
    };
    
    // 执行IndexedDB示例
    (async () => {
        try {
            const db = await initIndexedDB();
            await addDataToIndexedDB(db);
            await queryDataFromIndexedDB(db);
        } catch (error) {
            console.error("IndexedDB示例执行失败:", error);
        }
    })();
}

// ==================== 错误处理与最佳实践 ====================

// 11. 错误处理
function jsonErrorHandling() {
    // 无效的JSON字符串示例
    const invalidJsonStrings = [
        '{ name: "张三" }',                // 键未使用引号
        '{ "name": "张三", }',              // 尾随逗号
        '{ "name": \'张三\' }',            // 值使用单引号
        '{ "undefined": undefined }',      // 不支持的值
        '{ "function": function(){} }',    // 不支持的值
        'not a json string',                // 完全不是JSON
        '{"date": new Date()}'             // 包含函数调用
    ];
    
    invalidJsonStrings.forEach((jsonString, index) => {
        console.log(`\n测试无效JSON #${index + 1}: ${jsonString}`);
        
        try {
            const parsed = JSON.parse(jsonString);
            console.log("解析结果:", parsed);
        } catch (error) {
            console.error("解析错误:", error.message);
            console.error("错误位置:", error);
            
            // 提供更友好的错误信息
            let friendlyMessage = "JSON格式错误: ";
            
            if (error.message.includes("Unexpected token")) {
                friendlyMessage += "意外字符，可能是键未使用引号或值使用了单引号";
            } else if (error.message.includes("Unexpected end")) {
                friendlyMessage += "JSON格式不完整，可能缺少括号或引号";
            } else if (error.message.includes("is not valid JSON")) {
                friendlyMessage += "输入的字符串不是有效的JSON格式";
            }
            
            console.log("友好错误提示:", friendlyMessage);
        }
    });
    
    // 安全的JSON解析函数
    function safeJsonParse(jsonString, defaultValue = null) {
        try {
            return JSON.parse(jsonString);
        } catch (error) {
            console.warn("JSON解析失败，使用默认值:", error.message);
            return defaultValue;
        }
    }
    
    // 使用安全解析
    const result1 = safeJsonParse('{"valid": true}', {});
    const result2 = safeJsonParse('{ invalid json }', { error: true });
    
    console.log("\n安全解析结果1:", result1);
    console.log("安全解析结果2:", result2);
}

// 12. 性能优化
function jsonPerformanceOptimization() {
    // 创建大型数据集用于性能测试
    const createLargeDataSet = (size) => {
        return Array.from({ length: size }, (_, i) => ({
            id: i,
            name: `项目${i}`,
            value: Math.random() * 100,
            tags: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, (_, j) => `标签${j}`),
            metadata: {
                createdAt: new Date(Date.now() - Math.floor(Math.random() * 365 * 24 * 60 * 60 * 1000)).toISOString(),
                active: Math.random() > 0.3
            }
        }));
    };
    
    const smallDataset = createLargeDataSet(100);
    const mediumDataset = createLargeDataSet(1000);
    const largeDataset = createLargeDataSet(10000);
    
    // 性能测试函数
    function performanceTest(dataset, name) {
        console.log(`\n性能测试 - ${name} (${dataset.length} 项):`);
        
        // 测试序列化性能
        console.time(`${name} - 序列化`);
        const jsonString = JSON.stringify(dataset);
        console.timeEnd(`${name} - 序列化`);
        console.log(`${name} - JSON大小: ${(jsonString.length / 1024).toFixed(2)} KB`);
        
        // 测试反序列化性能
        console.time(`${name} - 反序列化`);
        const parsedData = JSON.parse(jsonString);
        console.timeEnd(`${name} - 反序列化`);
        
        // 测试格式化性能
        console.time(`${name} - 格式化`);
        const formattedJson = JSON.stringify(dataset, null, 2);
        console.timeEnd(`${name} - 格式化`);
        
        return { jsonString, parsedData, formattedJson };
    }
    
    const smallResults = performanceTest(smallDataset, "小型数据集");
    const mediumResults = performanceTest(mediumDataset, "中型数据集");
    const largeResults = performanceTest(largeDataset, "大型数据集");
    
    // 性能优化技巧
    
    // 1. 对齐字段顺序以减少序列化大小
    function optimizeFieldOrder(dataset) {
        // 将常用字段放前面，相同类型的字段放一起
        return dataset.map(item => ({
            id: item.id,
            name: item.name,
            value: item.value,
            active: item.metadata.active,
            createdAt: item.metadata.createdAt,
            tags: item.tags
        }));
    }
    
    const optimizedDataset = optimizeFieldOrder(mediumDataset);
    const optimizedJson = JSON.stringify(optimizedDataset);
    const originalJson = JSON.stringify(mediumDataset);
    
    console.log(`\n字段顺序优化效果:`);
    console.log(`原始JSON大小: ${(originalJson.length / 1024).toFixed(2)} KB`);
    console.log(`优化后JSON大小: ${(optimizedJson.length / 1024).toFixed(2)} KB`);
    console.log(`节省空间: ${((1 - optimizedJson.length / originalJson.length) * 100).toFixed(2)}%`);
    
    // 2. 使用短字段名
    function useShortFieldNames(dataset) {
        return dataset.map(item => ({
            i: item.id,           // id -> i
            n: item.name,         // name -> n
            v: item.value,         // value -> v
            a: item.metadata.active,  // active -> a
            d: item.metadata.createdAt, // date -> d
            t: item.tags          // tags -> t
        }));
    }
    
    const shortFieldDataset = useShortFieldNames(mediumDataset);
    const shortFieldJson = JSON.stringify(shortFieldDataset);
    
    console.log(`\n短字段名优化效果:`);
    console.log(`原始JSON大小: ${(originalJson.length / 1024).toFixed(2)} KB`);
    console.log(`短字段名JSON大小: ${(shortFieldJson.length / 1024).toFixed(2)} KB`);
    console.log(`节省空间: ${((1 - shortFieldJson.length / originalJson.length) * 100).toFixed(2)}%`);
    
    // 注意：使用短字段名会降低可读性，适用于需要节省空间的场景
}

// ==================== 运行所有示例 ====================
function runAllExamples() {
    console.log("========== JSON与JavaScript交互示例 ==========");
    
    console.log("\n1. 基本JSON操作");
    const { jsonString, formattedJson } = jsObjectToJson();
    const parsedObj = jsonToJsObject(jsonString);
    
    console.log("\n2. 高级JSON操作");
    const replacerJson = jsonWithReplacer();
    const reviverObj = jsonWithReviver(replacerJson);
    
    console.log("\n3. 深度克隆");
    const originalObj = { a: 1, b: { c: 2 } };
    const clonedObj = deepCloneObject(originalObj);
    
    console.log("\n4. 循环引用处理");
    handleCircularReference();
    
    console.log("\n5. 大型JSON处理");
    processLargeJsonData();
    
    console.log("\n6. API请求与响应");
    fetchJsonData();
    
    console.log("\n7. 本地存储中的JSON");
    localStorageJsonExample();
    
    console.log("\n8. IndexedDB中的JSON");
    indexedDbJsonExample();
    
    console.log("\n9. 错误处理");
    jsonErrorHandling();
    
    console.log("\n10. 性能优化");
    jsonPerformanceOptimization();
    
    console.log("\n========== 所有示例执行完毕 ==========");
}

// 如果在Node.js环境中，直接运行示例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        jsObjectToJson,
        jsonToJsObject,
        jsonWithReplacer,
        jsonWithReviver,
        deepCloneObject,
        handleCircularReference,
        processLargeJsonData,
        fetchJsonData,
        localStorageJsonExample,
        indexedDbJsonExample,
        jsonErrorHandling,
        jsonPerformanceOptimization,
        runAllExamples
    };
} else {
    // 在浏览器环境中，可以选择运行示例
    console.log("JSON与JavaScript交互示例已加载。要运行所有示例，请调用 runAllExamples() 函数。");
}