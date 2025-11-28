// 第1章：JavaScript基础概念与环境搭建 - 外部JavaScript文件示例

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM已加载完成');
    
    // 添加一些页面加载时的初始化代码
    initializePage();
});

// 页面初始化函数
function initializePage() {
    console.log('页面正在初始化...');
    
    // 添加页面加载时间
    const loadTimeElement = document.createElement('p');
    loadTimeElement.textContent = '页面加载时间: ' + new Date().toLocaleString();
    loadTimeElement.style.color = '#666';
    loadTimeElement.style.fontStyle = 'italic';
    
    // 查找第一个容器并添加加载时间
    const firstContainer = document.querySelector('.container');
    if (firstContainer) {
        firstContainer.appendChild(loadTimeElement);
    }
    
    console.log('页面初始化完成');
}

// 这是一个用于演示目的的函数
function demonstrateBasicConcepts() {
    // 变量声明
    let greeting = 'Hello, ';
    let target = 'JavaScript';
    
    // 字符串连接
    let message = greeting + target + '!';
    console.log(message);
    
    // 数值计算
    let x = 10;
    let y = 5;
    let sum = x + y;
    let product = x * y;
    
    console.log(`${x} + ${y} = ${sum}`);
    console.log(`${x} * ${y} = ${product}`);
    
    // 布尔值
    let isJavaScriptFun = true;
    let isJavaScriptHard = false;
    
    console.log('JavaScript有趣吗?', isJavaScriptFun);
    console.log('JavaScript难学吗?', isJavaScriptHard);
    
    // 数组
    let colors = ['红色', '绿色', '蓝色'];
    console.log('颜色数组:', colors);
    console.log('第一个颜色:', colors[0]);
    
    // 对象
    let person = {
        name: '张三',
        age: 30,
        city: '北京'
    };
    
    console.log('用户对象:', person);
    console.log('用户姓名:', person.name);
    
    return {
        message: message,
        sum: sum,
        product: product,
        colors: colors,
        person: person
    };
}

// 这个函数演示了如何从外部JavaScript文件操作DOM
function updatePageWithCurrentTime() {
    // 查找页面中的时间显示元素（如果存在）
    let timeDisplay = document.getElementById('current-time');
    
    if (timeDisplay) {
        // 更新时间显示
        timeDisplay.textContent = '当前时间: ' + new Date().toLocaleTimeString();
    } else {
        // 如果不存在，创建一个
        timeDisplay = document.createElement('div');
        timeDisplay.id = 'current-time';
        timeDisplay.textContent = '当前时间: ' + new Date().toLocaleTimeString();
        timeDisplay.style.padding = '10px';
        timeDisplay.style.backgroundColor = '#f0f0f0';
        timeDisplay.style.margin = '10px 0';
        timeDisplay.style.borderRadius = '5px';
        
        // 添加到页面body的末尾
        document.body.appendChild(timeDisplay);
    }
}

// 每秒更新一次时间
setInterval(updatePageWithCurrentTime, 1000);

// 演示不同类型的函数声明
// 1. 函数声明
function functionDeclaration(name) {
    return '你好, ' + name + '! (函数声明方式)';
}

// 2. 函数表达式
const functionExpression = function(name) {
    return '你好, ' + name + '! (函数表达式方式)';
};

// 3. 箭头函数
const arrowFunction = (name) => {
    return '你好, ' + name + '! (箭头函数方式)';
};

// 更简洁的箭头函数（单行返回）
const conciseArrowFunction = (name) => `你好, ${name}! (简洁箭头函数方式)`;

// 测试不同类型的函数
function testDifferentFunctionTypes() {
    const name = '学习者';
    
    console.log(functionDeclaration(name));
    console.log(functionExpression(name));
    console.log(arrowFunction(name));
    console.log(conciseArrowFunction(name));
}

// 演示作用域概念
function demonstrateScope() {
    // 全局变量
    let globalVar = '我是全局变量';
    
    function outerFunction() {
        // 外部函数的局部变量
        let outerVar = '我是外部函数的变量';
        
        function innerFunction() {
            // 内部函数的局部变量
            let innerVar = '我是内部函数的变量';
            
            console.log(innerVar);  // 可以访问
            console.log(outerVar);  // 可以访问
            console.log(globalVar); // 可以访问
        }
        
        innerFunction();
        
        console.log(outerVar);  // 可以访问
        // console.log(innerVar);  // 不能访问，会报错
    }
    
    outerFunction();
    
    console.log(globalVar); // 可以访问
    // console.log(outerVar);  // 不能访问，会报错
    // console.log(innerVar);  // 不能访问，会报错
}

// 演示立即执行函数表达式(IIFE)
function demonstrateIIFE() {
    // 这是一个IIFE，会立即执行
    (function() {
        let immediateVar = '我是IIFE中的变量';
        console.log(immediateVar);
    })();
    
    // 下面这行会报错，因为immediateVar只在IIFE内部可见
    // console.log(immediateVar);
    
    // 带参数的IIFE
    (function(name) {
        console.log(`IIFE接收到的参数是: ${name}`);
    })('JavaScript');
}

// 演示数组操作
function demonstrateArrayMethods() {
    let numbers = [1, 2, 3, 4, 5];
    console.log('原始数组:', numbers);
    
    // 数组长度
    console.log('数组长度:', numbers.length);
    
    // 添加元素到末尾
    numbers.push(6);
    console.log('push(6)后:', numbers);
    
    // 移除末尾元素
    let lastElement = numbers.pop();
    console.log('pop()移除的元素:', lastElement);
    console.log('pop()后的数组:', numbers);
    
    // 添加元素到开头
    numbers.unshift(0);
    console.log('unshift(0)后:', numbers);
    
    // 移除开头元素
    let firstElement = numbers.shift();
    console.log('shift()移除的元素:', firstElement);
    console.log('shift()后的数组:', numbers);
    
    // 数组切片
    let slice = numbers.slice(1, 4); // 从索引1开始到索引4（不包括4）
    console.log('slice(1,4):', slice);
    console.log('原数组未被修改:', numbers);
    
    // 数组拼接
    let moreNumbers = [6, 7, 8];
    let concatenated = numbers.concat(moreNumbers);
    console.log('concat([6,7,8]):', concatenated);
    
    // 数组查找
    let indexOfThree = numbers.indexOf(3);
    console.log('indexOf(3):', indexOfThree);
    
    // 数组是否包含元素
    let hasFour = numbers.includes(4);
    console.log('includes(4):', hasFour);
    
    // 数组过滤
    let evenNumbers = numbers.filter(num => num % 2 === 0);
    console.log('filter(num => num % 2 === 0):', evenNumbers);
    
    // 数组映射
    let doubledNumbers = numbers.map(num => num * 2);
    console.log('map(num => num * 2):', doubledNumbers);
    
    // 数组归约
    let sum = numbers.reduce((acc, num) => acc + num, 0);
    console.log('reduce((acc,num) => acc+num, 0):', sum);
    
    return {
        original: numbers,
        filtered: evenNumbers,
        mapped: doubledNumbers,
        sum: sum
    };
}

// 演示对象操作
function demonstrateObjectMethods() {
    // 创建对象
    let car = {
        brand: '丰田',
        model: '卡罗拉',
        year: 2022,
        color: '白色',
        isRunning: false,
        
        // 对象方法
        start: function() {
            this.isRunning = true;
            return `${this.brand} ${this.model} 已经启动`;
        },
        
        stop: function() {
            this.isRunning = false;
            return `${this.brand} ${this.model} 已经熄火`;
        },
        
        // 使用ES6简写的方法
        getInfo() {
            return `${this.year}年款 ${this.brand} ${this.model}，颜色：${this.color}`;
        }
    };
    
    console.log('汽车对象:', car);
    console.log('汽车信息:', car.getInfo());
    
    // 启动汽车
    console.log(car.start());
    console.log('汽车是否在运行:', car.isRunning);
    
    // 停止汽车
    console.log(car.stop());
    console.log('汽车是否在运行:', car.isRunning);
    
    // 添加新属性
    car.mileage = 5000;
    console.log('添加里程后的汽车:', car);
    
    // 删除属性
    delete car.color;
    console.log('删除颜色属性后的汽车:', car);
    
    // 获取所有键
    let keys = Object.keys(car);
    console.log('对象的所有键:', keys);
    
    // 获取所有值
    let values = Object.values(car);
    console.log('对象的所有值:', values);
    
    // 获取所有键值对
    let entries = Object.entries(car);
    console.log('对象的所有键值对:', entries);
    
    return car;
}

// 演示类型转换
function demonstrateTypeConversion() {
    console.log('=== 类型转换演示 ===');
    
    // 字符串转数字
    let strNum1 = '123';
    let num1 = Number(strNum1);
    console.log(`Number('${strNum1}') = ${num1}, 类型: ${typeof num1}`);
    
    let strNum2 = '456.78';
    let num2 = parseFloat(strNum2);
    console.log(`parseFloat('${strNum2}') = ${num2}, 类型: ${typeof num2}`);
    
    let strNum3 = '789';
    let num3 = parseInt(strNum3);
    console.log(`parseInt('${strNum3}') = ${num3}, 类型: ${typeof num3}`);
    
    // 数字转字符串
    let num = 42;
    let str1 = String(num);
    console.log(`String(${num}) = '${str1}', 类型: ${typeof str1}`);
    
    let str2 = num.toString();
    console.log(`(${num}).toString() = '${str2}', 类型: ${typeof str2}`);
    
    let str3 = num + '';
    console.log(`${num} + '' = '${str3}', 类型: ${typeof str3}`);
    
    // 布尔值转换
    console.log('Boolean(0) =', Boolean(0));
    console.log('Boolean("") =', Boolean(''));
    console.log('Boolean(null) =', Boolean(null));
    console.log('Boolean(undefined) =', Boolean(undefined));
    console.log('Boolean(NaN) =', Boolean(NaN));
    console.log('Boolean(42) =', Boolean(42));
    console.log('Boolean("hello") =', Boolean('hello'));
    console.log('Boolean({}) =', Boolean({}));
    console.log('Boolean([]) =', Boolean([]));
    
    // 隐式类型转换
    console.log('5 + "5" =', 5 + "5"); // 字符串连接
    console.log('5 * "5" =', 5 * "5"); // 数字乘法
    console.log('5 == "5" =', 5 == "5"); // 值相等
    console.log('5 === "5" =', 5 === "5"); // 严格相等
}

// 演示错误处理
function demonstrateErrorHandling() {
    console.log('=== 错误处理演示 ===');
    
    // try-catch示例
    try {
        // 尝试执行可能出错的代码
        let result = riskyOperation();
        console.log('操作结果:', result);
    } catch (error) {
        console.error('捕获到错误:', error.message);
    } finally {
        console.log('无论是否出错，都会执行的finally块');
    }
    
    // 自定义错误
    function validateAge(age) {
        if (typeof age !== 'number') {
            throw new TypeError('年龄必须是数字');
        }
        
        if (age < 0) {
            throw new RangeError('年龄不能为负数');
        }
        
        if (age > 150) {
            throw new RangeError('年龄看起来不合理');
        }
        
        return true;
    }
    
    // 测试年龄验证
    const testAges = [25, -5, 'thirty', 200];
    
    for (let age of testAges) {
        try {
            validateAge(age);
            console.log(`${age} 是一个有效的年龄`);
        } catch (error) {
            console.error(`验证年龄 ${age} 时出错:`, error.message);
        }
    }
}

// 模拟一个可能出错的操作
function riskyOperation() {
    // 50%的概率出错
    if (Math.random() > 0.5) {
        throw new Error('这是一个随机错误');
    }
    
    return '操作成功完成';
}

// 导出一些函数供其他文件使用（如果需要）
// 在浏览器环境中，我们可以将这些函数添加到全局对象中
window.JSBasicsExamples = {
    demonstrateBasicConcepts,
    testDifferentFunctionTypes,
    demonstrateScope,
    demonstrateIIFE,
    demonstrateArrayMethods,
    demonstrateObjectMethods,
    demonstrateTypeConversion,
    demonstrateErrorHandling
};

// 在控制台输出示例
console.log('chapter1_javascript_basics.js 已加载');
console.log('可用的示例函数:', Object.keys(window.JSBasicsExamples));