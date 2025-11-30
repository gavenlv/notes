// 生成器与迭代器示例
function* fibonacciGenerator(limit) {
    let a = 0;
    let b = 1;
    let count = 0;
    
    while (count < limit) {
        yield a;
        [a, b] = [b, a + b];
        count++;
    }
}

function generateFibonacci() {
    const limit = parseInt(document.getElementById('fibLimit').value, 10) || 10;
    const fibGen = fibonacciGenerator(limit);
    const result = [];
    
    for (const num of fibGen) {
        result.push(num);
    }
    
    showResult('iteratorResult', `斐波那契数列 (${limit}项):\n${result.join(', ')}`);
}

// 异步生成器示例
async function* asyncDataGenerator(urls) {
    for (const url of urls) {
        try {
            // 模拟异步获取数据
            const data = await new Promise(resolve => {
                setTimeout(() => resolve(`来自 ${url} 的数据`), 500);
            });
            
            yield data;
        } catch (error) {
            yield `错误: ${error.message}`;
        }
    }
}

async function testAsyncGenerator() {
    const urls = ['api.example.com/users', 'api.example.com/posts', 'api.example.com/comments'];
    const dataGen = asyncDataGenerator(urls);
    const results = [];
    
    for await (const data of dataGen) {
        results.push(data);
    }
    
    showResult('iteratorResult', `异步生成器结果:\n${results.join('\n')}`);
}

// Proxy与Reflect示例
function createValidatedObject(schema) {
    const obj = {};
    const observers = [];
    
    return new Proxy(obj, {
        get(target, prop) {
            console.log(`读取属性: ${prop}`);
            return Reflect.get(target, prop);
        },
        
        set(target, prop, value) {
            console.log(`设置属性: ${prop} = ${value}`);
            
            // 验证属性类型
            if (schema[prop] && typeof value !== schema[prop]) {
                throw new TypeError(`属性 ${prop} 应该是 ${schema[prop]} 类型`);
            }
            
            const oldValue = target[prop];
            const result = Reflect.set(target, prop, value);
            
            // 通知观察者
            observers.forEach(observer => {
                observer(prop, oldValue, value);
            });
            
            return result;
        },
        
        deleteProperty(target, prop) {
            console.log(`删除属性: ${prop}`);
            const oldValue = target[prop];
            const result = Reflect.deleteProperty(target, prop);
            
            // 通知观察者
            observers.forEach(observer => {
                observer(prop, oldValue, undefined);
            });
            
            return result;
        },
        
        subscribe(observer) {
            observers.push(observer);
            
            // 返回取消订阅函数
            return () => {
                const index = observers.indexOf(observer);
                if (index !== -1) {
                    observers.splice(index, 1);
                }
            };
        }
    });
}

// 创建验证对象
const userSchema = {
    name: 'string',
    age: 'number',
    email: 'string'
};

const validatedUser = createValidatedObject(userSchema);

// 订阅变化
const unsubscribe = validatedUser.subscribe((prop, oldValue, newValue) => {
    console.log(`属性 ${prop} 从 ${oldValue} 变为 ${newValue}`);
});

function setProxyProperty() {
    const propName = document.getElementById('propName').value;
    const propValue = document.getElementById('propValue').value;
    
    if (!propName) {
        showResult('proxyResult', '请输入属性名');
        return;
    }
    
    // 尝试自动推断类型
    let parsedValue = propValue;
    if (!isNaN(propValue) && propValue !== '') {
        parsedValue = parseFloat(propValue);
    } else if (propValue === 'true') {
        parsedValue = true;
    } else if (propValue === 'false') {
        parsedValue = false;
    }
    
    try {
        validatedUser[propName] = parsedValue;
        showResult('proxyResult', `成功设置 ${propName} = ${JSON.stringify(validatedUser[propName])}`);
    } catch (error) {
        showResult('proxyResult', `错误: ${error.message}`);
    }
}

function getProxyProperty() {
    const propName = document.getElementById('propName').value;
    
    if (!propName) {
        showResult('proxyResult', '请输入属性名');
        return;
    }
    
    if (propName in validatedUser) {
        showResult('proxyResult', `${propName} = ${JSON.stringify(validatedUser[propName])}`);
    } else {
        showResult('proxyResult', `属性 ${propName} 不存在`);
    }
}

// 函数式编程示例
const pipe = (...fns) => (initialValue) => 
    fns.reduce((acc, fn) => fn(acc), initialValue);

// 数据处理函数
const filterEven = numbers => numbers.filter(num => num % 2 === 0);
const multiplyByTwo = numbers => numbers.map(num => num * 2);
const sum = numbers => numbers.reduce((acc, num) => acc + num, 0);
const formatResult = (title, data) => `${title}: ${data}`;

// 创建处理管道
const processNumbers = pipe(
    filterEven,
    multiplyByTwo,
    sum,
    result => formatResult('处理结果', result)
);

const processNumbersDetails = pipe(
    filterEven,
    result => ({
        original: result,
        even: result,
        doubled: result.map(num => num * 2),
        sum: result.reduce((acc, num) => acc + num * 2, 0)
    })
);

function processFunctionalNumbers() {
    const input = document.getElementById('numberInput').value;
    
    if (!input) {
        showResult('functionalResult', '请输入数字');
        return;
    }
    
    try {
        const numbers = input.split(',').map(num => parseFloat(num.trim()));
        const result = processNumbers(numbers);
        const details = processNumbersDetails(numbers);
        
        showResult('functionalResult', `${result}\n\n详细信息:\n原始数组: [${numbers.join(', ')}]\n过滤后的偶数: [${details.even.join(', ')}]\n乘以2后: [${details.doubled.join(', ')}]\n总和: ${details.sum}`);
    } catch (error) {
        showResult('functionalResult', `错误: ${error.message}`);
    }
}

function generateRandomNumbers() {
    const count = 20;
    const numbers = Array.from({ length: count }, () => Math.floor(Math.random() * 100));
    document.getElementById('numberInput').value = numbers.join(', ');
    processFunctionalNumbers();
}

// 性能优化示例
function runPerformanceTest() {
    const arraySize = parseInt(document.getElementById('arraySize').value, 10) || 100000;
    const testArray = Array.from({ length: arraySize }, () => Math.floor(Math.random() * 100));
    const evenNumbers = testArray.filter(num => num % 2 === 0);
    
    // 测试1: 传统for循环
    const loopStart = performance.now();
    let sum1 = 0;
    for (let i = 0; i < evenNumbers.length; i++) {
        sum1 += evenNumbers[i] * 2;
    }
    const loopTime = performance.now() - loopStart;
    document.getElementById('loopTime').textContent = `${loopTime.toFixed(2)}ms`;
    
    // 测试2: 数组方法
    const methodStart = performance.now();
    const doubled = evenNumbers.map(num => num * 2);
    const sum2 = doubled.reduce((acc, num) => acc + num, 0);
    const methodTime = performance.now() - methodStart;
    document.getElementById('methodTime').textContent = `${methodTime.toFixed(2)}ms`;
    
    // 测试3: 函数式编程
    const functionalStart = performance.now();
    const sum3 = evenNumbers
        .map(num => num * 2)
        .reduce((acc, num) => acc + num, 0);
    const functionalTime = performance.now() - functionalStart;
    document.getElementById('functionalTime').textContent = `${functionalTime.toFixed(2)}ms`;
    
    // 绘制性能图表
    drawPerformanceChart([
        { method: '传统循环', time: loopTime },
        { method: '数组方法', time: methodTime },
        { method: '函数式方法', time: functionalTime }
    ]);
    
    showResult('performanceResult', `数组大小: ${arraySize}\n偶数数量: ${evenNumbers.length}\n结果总和: ${sum1} (所有方法结果一致)\n\n性能比较:\n传统循环: ${loopTime.toFixed(2)}ms\n数组方法: ${methodTime.toFixed(2)}ms\n函数式方法: ${functionalTime.toFixed(2)}ms`);
}

function drawPerformanceChart(data) {
    const canvas = document.getElementById('performanceChart');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // 清空画布
    ctx.clearRect(0, 0, width, height);
    
    // 找出最大值
    const maxTime = Math.max(...data.map(item => item.time));
    
    // 设置图表参数
    const padding = 40;
    const barWidth = (width - 2 * padding) / data.length * 0.6;
    const barSpacing = (width - 2 * padding) / data.length * 0.4;
    const chartHeight = height - 2 * padding;
    
    // 绘制坐标轴
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // 绘制柱状图
    data.forEach((item, index) => {
        const barHeight = (item.time / maxTime) * chartHeight;
        const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
        const y = height - padding - barHeight;
        
        // 绘制柱子
        ctx.fillStyle = `hsl(${index * 120}, 70%, 50%)`;
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // 绘制标签
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(item.method, x + barWidth / 2, height - padding + 15);
        
        // 绘制数值
        ctx.fillText(`${item.time.toFixed(2)}ms`, x + barWidth / 2, y - 5);
    });
}

// 内存使用测试
function runMemoryTest() {
    const size = 1000000;
    const before = performance.memory ? performance.memory.usedJSHeapSize : 'N/A';
    
    // 创建一个大数组
    const largeArray = Array.from({ length: size }, () => ({
        id: Math.random().toString(36),
        value: Math.random() * 1000
    }));
    
    const afterCreate = performance.memory ? performance.memory.usedJSHeapSize : 'N/A';
    
    // 处理数组
    const processed = largeArray.map(item => ({
        ...item,
        processed: true,
        doubleValue: item.value * 2
    }));
    
    const afterProcess = performance.memory ? performance.memory.usedJSHeapSize : 'N/A';
    
    // 清理数组
    largeArray.length = 0;
    
    const afterClear = performance.memory ? performance.memory.usedJSHeapSize : 'N/A';
    
    showResult('performanceResult', `内存使用测试:\n创建前: ${formatBytes(before)}\n创建后: ${formatBytes(afterCreate)}\n处理后: ${formatBytes(afterProcess)}\n清理后: ${formatBytes(afterClear)}\n\n处理对象数量: ${size}`);
}

function formatBytes(bytes) {
    if (bytes === 'N/A') return 'N/A';
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

// 元编程示例
function createDynamicClass() {
    const className = document.getElementById('className').value || 'DynamicUser';
    
    // 动态类定义
    const classDefinition = `
    class ${className} {
        constructor(data = {}) {
            this.id = data.id || Math.random().toString(36).substr(2, 9);
            this.name = data.name || '';
            this.age = data.age || 0;
            this.email = data.email || '';
            this.createdAt = new Date();
        }
        
        greet() {
            return \`你好，我是 \${this.name}\`;
        }
        
        getDetails() {
            return \`\${this.name} (\${this.age}) - \${this.email}\`;
        }
        
        static createRandom() {
            const names = ['张三', '李四', '王五', '赵六'];
            const domains = ['example.com', 'test.org', 'demo.net'];
            
            return new ${className}({
                name: names[Math.floor(Math.random() * names.length)],
                age: Math.floor(Math.random() * 50) + 18,
                email: \`user\${Math.floor(Math.random() * 1000)}@\${domains[Math.floor(Math.random() * domains.length)]}\`
            });
        }
    }`;
    
    // 动态创建类
    eval(classDefinition);
    
    // 存储类名以便后续使用
    window.dynamicClassName = className;
    
    showResult('metaprogrammingResult', `动态类 ${className} 创建成功！\n\n类定义:\n${classDefinition}`);
}

function testDynamicClass() {
    const className = window.dynamicClassName || 'DynamicUser';
    const DynamicClass = window[className];
    
    if (!DynamicClass) {
        showResult('metaprogrammingResult', `类 ${className} 不存在，请先创建类`);
        return;
    }
    
    // 创建实例
    const user1 = new DynamicClass({ name: '用户1', age: 30, email: 'user1@example.com' });
    const user2 = DynamicClass.createRandom();
    
    showResult('metaprogrammingResult', `${className} 测试结果:\n\n实例1:\n${user1.getDetails()}\n${user1.greet()}\n\n实例2 (随机生成):\n${user2.getDetails()}\n${user2.greet()}\n\n类方法调用:\n${className}.createRandom(): 可以创建随机用户实例`);
}

// 高级异步编程示例
async function runParallelTasks() {
    const start = performance.now();
    
    // 创建多个Promise任务
    const tasks = [
        new Promise(resolve => setTimeout(() => resolve('任务1完成'), 1000)),
        new Promise(resolve => setTimeout(() => resolve('任务2完成'), 1500)),
        new Promise(resolve => setTimeout(() => resolve('任务3完成'), 800)),
        new Promise((resolve, reject) => setTimeout(() => reject(new Error('任务4失败')), 1200))
    ];
    
    try {
        // 并行执行所有任务
        const results = await Promise.allSettled(tasks);
        const end = performance.now();
        
        const status = results.map(result => 
            result.status === 'fulfilled' ? result.value : `失败: ${result.reason.message}`
        );
        
        showResult('asyncResult', `并行任务结果:\n${status.join('\n')}\n\n总耗时: ${(end - start).toFixed(2)}ms`);
    } catch (error) {
        showResult('asyncResult', `并行任务执行错误: ${error.message}`);
    }
}

async function runConcurrentControl() {
    // 模拟一批URL
    const urls = Array.from({ length: 20 }, (_, i) => `https://api.example.com/data/${i + 1}`);
    
    // 限制并发数的函数
    async function limitConcurrency(tasks, limit) {
        const results = [];
        const executing = [];
        
        for (const task of tasks) {
            const promise = task().then(result => {
                executing.splice(executing.indexOf(promise), 1);
                return result;
            });
            
            results.push(promise);
            
            if (tasks.length >= limit) {
                executing.push(promise);
                
                if (executing.length >= limit) {
                    await Promise.race(executing);
                }
            }
        }
        
        return Promise.all(results);
    }
    
    // 创建任务函数
    const createTask = (url) => () => 
        new Promise(resolve => 
            setTimeout(() => resolve(`数据来自: ${url}`), Math.random() * 1000)
        );
    
    const start = performance.now();
    
    // 执行并发控制
    const tasks = urls.map(createTask);
    const results = await limitConcurrency(tasks, 5);
    const end = performance.now();
    
    showResult('asyncResult', `并发控制结果:\n处理了 ${urls.length} 个URL\n并发限制: 5\n\n前5个结果:\n${results.slice(0, 5).join('\n')}\n\n总耗时: ${(end - start).toFixed(2)}ms`);
}

async function runDataStream() {
    // 模拟数据流
    async function* dataStream(count) {
        for (let i = 1; i <= count; i++) {
            yield {
                id: i,
                value: Math.random() * 100,
                timestamp: Date.now()
            };
            
            // 模拟数据到达的延迟
            await new Promise(resolve => setTimeout(resolve, 200));
        }
    }
    
    // 处理数据流的函数
    async function processData(stream, filterFn, transformFn) {
        const results = [];
        
        for await (const data of stream) {
            if (filterFn(data)) {
                const transformed = transformFn(data);
                results.push(transformed);
                
                // 实时显示处理结果
                if (results.length % 3 === 0) {
                    showResult('asyncResult', `数据流处理中...\n已处理 ${results.length} 条数据\n最新处理: ${JSON.stringify(transformed)}`);
                }
            }
        }
        
        return results;
    }
    
    const start = performance.now();
    
    // 创建和处理数据流
    const stream = dataStream(10);
    const results = await processData(
        stream,
        data => data.value > 50,  // 只处理值大于50的数据
        data => ({               // 转换数据格式
            id: data.id,
            value: Math.round(data.value),
            time: new Date(data.timestamp).toLocaleTimeString()
        })
    );
    
    const end = performance.now();
    
    showResult('asyncResult', `数据流处理完成:\n\n处理结果:\n${results.map(r => `ID: ${r.id}, 值: ${r.value}, 时间: ${r.time}`).join('\n')}\n\n总处理数量: ${results.length}\n总耗时: ${(end - start).toFixed(2)}ms`);
}

// 辅助函数：在指定元素中显示结果
function showResult(elementId, content) {
    document.getElementById(elementId).textContent = content;
}