// 第2章：JavaScript语法与数据类型 - 外部JavaScript文件示例

// 创建命名空间对象
const chapter2Examples = {
    // 2.1 JavaScript基础语法
    demonstrateStatementsExpressions() {
        let output = '=== 语句与表达式演示 ===\n\n';
        
        // 语句示例
        output += '--- 语句示例 ---\n';
        
        // 声明语句
        let x = 10;
        const y = 20;
        output += `let x = ${x}; // 声明语句\n`;
        output += `const y = ${y}; // 常量声明语句\n\n`;
        
        // 条件语句
        let condition = x > 5;
        output += `if (${x} > 5) { /* 条件语句 */ }\n`;
        output += `条件 ${x} > 5 的结果: ${condition}\n\n`;
        
        // 循环语句
        output += '--- 循环语句示例 ---\n';
        let sum = 0;
        for (let i = 1; i <= 5; i++) {
            sum += i;
            if (i < 5) output += i + ' + ';
            else output += i + ' = ' + sum + '\n';
        }
        output += '\n';
        
        // 表达式示例
        output += '--- 表达式示例 ---\n';
        let expr1 = 10 + 5; // 算术表达式
        output += `10 + 5 = ${expr1}\n`;
        
        let expr2 = x * y; // 变量表达式
        output += `${x} * ${y} = ${expr2}\n`;
        
        let expr3 = 'Hello' + ', ' + 'World'; // 字符串表达式
        output += `'Hello' + ', ' + 'World' = "${expr3}"\n`;
        
        let expr4 = x > 5 && y < 25; // 逻辑表达式
        output += `${x} > 5 && ${y} < 25 = ${expr4}\n`;
        
        // 函数调用表达式
        function greet(name) {
            return '你好，' + name + '！';
        }
        
        let expr5 = greet('JavaScript');
        output += `greet('JavaScript') = "${expr5}"\n`;
        
        return output;
    },
    
    demonstrateIdentifiers() {
        let output = '=== 标识符命名演示 ===\n\n';
        
        // 有效的标识符
        output += '--- 有效的标识符 ---\n';
        let userName = '张三';
        let _privateVariable = '私有变量';
        let $specialValue = '特殊值';
        let counter123 = 123;
        
        output += `userName = "${userName}"\n`;
        output += `_privateVariable = "${_privateVariable}"\n`;
        output += `$specialValue = "${$specialValue}"\n`;
        output += `counter123 = ${counter123}\n\n`;
        
        // 命名风格示例
        output += '--- 命名风格示例 ---\n';
        // 驼峰命名法
        let firstName = 'John';
        let lastName = 'Doe';
        let getFullName = function() {
            return firstName + ' ' + lastName;
        };
        
        output += `驼峰命名法: firstName = "${firstName}", lastName = "${lastName}"\n`;
        output += `函数命名: getFullName() = "${getFullName()}"\n\n`;
        
        // 常量命名
        const MAX_LENGTH = 100;
        const PI = 3.14159;
        
        output += `常量命名: MAX_LENGTH = ${MAX_LENGTH}, PI = ${PI}\n\n`;
        
        // 私有变量命名
        let _internalMethod = function() {
            return '内部方法';
        };
        
        output += `私有变量命名: _internalMethod() = "${_internalMethod()}"\n\n`;
        
        // 保留字说明
        output += '--- 保留字说明 ---\n';
        output += 'JavaScript有一些保留字不能用作标识符，例如:\n';
        output += 'var, let, const, function, if, else, for, while, break, continue\n';
        output += 'return, try, catch, finally, throw, new, this, class, extends\n';
        output += 'import, export, default, static, async, await 等等...\n';
        
        return output;
    },
    
    // 2.2 变量声明
    demonstrateVarDeclaration() {
        let output = '=== var声明演示 ===\n\n';
        
        // 变量提升
        output += '--- 变量提升 ---\n';
        // 提前访问var变量
        output += 'var声明的变量可以在声明前访问(值为undefined):\n';
        output += `console.log(myVar); // ${typeof myVar}\n`;
        var myVar = 10;
        output += `var myVar = ${myVar};\n`;
        output += `console.log(myVar); // ${myVar}\n\n`;
        
        // 函数作用域
        output += '--- 函数作用域 ---\n';
        
        function testVarScope() {
            if (true) {
                var x = 10; // 在if块内声明
                output += `在if块内声明: var x = ${x}\n`;
            }
            output += `在if块外仍可访问: x = ${x}\n`;
        }
        
        testVarScope();
        output += '\n';
        
        // 重复声明
        output += '--- 重复声明 ---\n';
        var repeatVar = '第一次声明';
        output += `var repeatVar = "${repeatVar}"\n`;
        
        var repeatVar = '第二次声明'; // 允许重复声明
        output += `var repeatVar = "${repeatVar}" (允许重复声明)\n\n`;
        
        // 全局属性
        output += '--- 全局属性 ---\n';
        var globalVar = 'I am global';
        output += `var globalVar = "${globalVar}"\n`;
        output += `window.globalVar = "${window.globalVar}" (var在全局作用域创建全局属性)\n\n`;
        
        return output;
    },
    
    demonstrateLetDeclaration() {
        let output = '=== let声明演示 ===\n\n';
        
        // 暂时性死区
        output += '--- 暂时性死区 ---\n';
        output += 'let声明的变量不能在声明前使用:\n';
        
        try {
            // 下面这行会报错，注释掉以防止整个脚本停止
            // console.log(myLet); // ReferenceError: Cannot access 'myLet' before initialization
            let myLet = 20;
            output += `let myLet = ${myLet};\n`;
        } catch (error) {
            output += `错误: ${error.message}\n`;
        }
        
        output += '\n';
        
        // 块级作用域
        output += '--- 块级作用域 ---\n';
        
        function testLetScope() {
            if (true) {
                let x = 10; // 在if块内声明
                output += `在if块内声明: let x = ${x}\n`;
            }
            
            try {
                // 下面这行会报错
                // console.log(x); // ReferenceError: x is not defined
                output += '在if块外无法访问x (会报错)\n';
            } catch (error) {
                output += `错误: ${error.message}\n`;
            }
        }
        
        testLetScope();
        output += '\n';
        
        // 不允许重复声明
        output += '--- 不允许重复声明 ---\n';
        let uniqueLet = 1;
        output += `let uniqueLet = ${uniqueLet}\n`;
        
        try {
            // 下面这行会报错
            // let uniqueLet = 2; // SyntaxError: Identifier 'uniqueLet' has already been declared
            output += '尝试重复声明let变量会报错\n';
        } catch (error) {
            output += `错误: ${error.message}\n`;
        }
        
        output += '\n';
        
        return output;
    },
    
    demonstrateConstDeclaration() {
        let output = '=== const声明演示 ===\n\n';
        
        // 必须初始化
        output += '--- 必须初始化 ---\n';
        const PI = 3.14159;
        output += `const PI = ${PI}; (const声明必须初始化)\n\n`;
        
        // 不能重新赋值
        output += '--- 不能重新赋值 ---\n';
        
        try {
            // 下面这行会报错
            // PI = 3.14; // TypeError: Assignment to constant variable
            output += '尝试重新赋值const变量会报错\n';
        } catch (error) {
            output += `错误: ${error.message}\n`;
        }
        
        output += '\n';
        
        // 对象和数组的特殊情况
        output += '--- 对象和数组的特殊情况 ---\n';
        const user = { name: '张三', age: 25 };
        output += `const user = ${JSON.stringify(user)};\n`;
        
        user.age = 26; // 允许修改对象属性
        output += `user.age = 26; (允许修改对象属性) ${JSON.stringify(user)}\n`;
        
        try {
            // 下面这行会报错
            // user = { name: '李四', age: 30 }; // TypeError: Assignment to constant variable
            output += '尝试重新赋值整个对象会报错\n';
        } catch (error) {
            output += `错误: ${error.message}\n`;
        }
        
        output += '\n';
        
        // 块级作用域
        output += '--- 块级作用域 ---\n';
        
        function testConstScope() {
            if (true) {
                const blockVar = 'I am block scoped';
                output += `在if块内声明: const blockVar = "${blockVar}"\n`;
            }
            
            try {
                // 下面这行会报错
                // console.log(blockVar); // ReferenceError: blockVar is not defined
                output += '在if块外无法访问blockVar (会报错)\n';
            } catch (error) {
                output += `错误: ${error.message}\n`;
            }
        }
        
        testConstScope();
        output += '\n';
        
        return output;
    },
    
    compareVariableDeclarations() {
        let output = '=== 变量声明对比 ===\n\n';
        
        // 作用域对比
        output += '--- 作用域对比 ---\n';
        
        function scopeComparison() {
            if (true) {
                var varVar = 'var变量';
                let letVar = 'let变量';
                const constVar = 'const变量';
                output += `在if块内: varVar="${varVar}", letVar="${letVar}", constVar="${constVar}"\n`;
            }
            
            output += `在if块外: varVar="${varVar}" (var具有函数作用域)\n`;
            
            try {
                // 下面这行会报错
                // console.log(letVar); // ReferenceError: letVar is not defined
                output += '在if块外: letVar无法访问 (let具有块级作用域)\n';
            } catch (error) {
                output += `在if块外访问letVar: 错误 - ${error.message}\n`;
            }
            
            try {
                // 下面这行会报错
                // console.log(constVar); // ReferenceError: constVar is not defined
                output += '在if块外: constVar无法访问 (const具有块级作用域)\n';
            } catch (error) {
                output += `在if块外访问constVar: 错误 - ${error.message}\n`;
            }
        }
        
        scopeComparison();
        output += '\n';
        
        // 变量提升对比
        output += '--- 变量提升对比 ---\n';
        output += 'var: 变量提升，值为undefined\n';
        output += 'let: 变量提升，但暂时性死区，访问会报错\n';
        output += 'const: 变量提升，但暂时性死区，访问会报错\n\n';
        
        // 重复声明对比
        output += '--- 重复声明对比 ---\n';
        output += 'var: 允许重复声明\n';
        output += 'let: 不允许重复声明\n';
        output += 'const: 不允许重复声明\n\n';
        
        // 初始化要求对比
        output += '--- 初始化要求对比 ---\n';
        output += 'var: 可以声明不初始化 (默认值为undefined)\n';
        output += 'let: 可以声明不初始化 (默认值为undefined)\n';
        output += 'const: 必须初始化\n\n';
        
        // 推荐用法
        output += '--- 推荐用法 ---\n';
        output += '1. 默认使用const，如果变量不会被重新赋值\n';
        output += '2. 需要重新赋值时使用let\n';
        output += '3. 避免使用var\n';
        output += '4. 声明时即初始化\n';
        
        return output;
    },
    
    // 2.3 JavaScript数据类型
    demonstrateBasicTypes() {
        let output = '=== 基本数据类型演示 ===\n\n';
        
        // undefined类型
        output += '--- undefined类型 ---\n';
        let undefinedVar;
        output += `let undefinedVar; // ${undefinedVar}\n`;
        output += `typeof undefinedVar: ${typeof undefinedVar}\n`;
        
        function noReturn() {
            // 没有return语句
        }
        output += `没有return的函数返回: ${noReturn()}\n\n`;
        
        // null类型
        output += '--- null类型 ---\n';
        let nullVar = null;
        output += `let nullVar = null; // ${nullVar}\n`;
        output += `typeof nullVar: ${typeof nullVar} (历史遗留问题)\n`;
        output += `null == undefined: ${null == undefined}\n`;
        output += `null === undefined: ${null === undefined}\n\n`;
        
        // boolean类型
        output += '--- boolean类型 ---\n';
        let isTrue = true;
        let isFalse = false;
        output += `let isTrue = ${isTrue};\n`;
        output += `let isFalse = ${isFalse};\n\n`;
        
        output += '其他类型转换为boolean:\n';
        output += `Boolean(0): ${Boolean(0)}\n`;
        output += `Boolean(""): ${Boolean("")}\n`;
        output += `Boolean(null): ${Boolean(null)}\n`;
        output += `Boolean(undefined): ${Boolean(undefined)}\n`;
        output += `Boolean(NaN): ${Boolean(NaN)}\n`;
        output += `Boolean(1): ${Boolean(1)}\n`;
        output += `Boolean("hello"): ${Boolean("hello")}\n`;
        output += `Boolean({}): ${Boolean({})}\n`;
        output += `Boolean([]): ${Boolean([])}\n\n`;
        
        // number类型
        output += '--- number类型 ---\n';
        let integer = 42;
        let floatNum = 3.14;
        let octalLiteral = 0o52; // 42的八进制
        let hexLiteral = 0x2A;   // 42的十六进制
        let binaryLiteral = 0b101010; // 42的二进制
        
        output += `let integer = ${integer};\n`;
        output += `let floatNum = ${floatNum};\n`;
        output += `let octalLiteral = ${octalLiteral}; // 八进制\n`;
        output += `let hexLiteral = ${hexLiteral}; // 十六进制\n`;
        output += `let binaryLiteral = ${binaryLiteral}; // 二进制\n\n`;
        
        // 特殊数值
        output += '特殊数值:\n';
        output += `Infinity: ${Infinity}\n`;
        output.println(`-Infinity: ${-Infinity}\n`);
        output += `NaN: ${NaN}\n`;
        output += `NaN === NaN: ${NaN === NaN}\n`;
        output += `isNaN(NaN): ${isNaN(NaN)}\n\n`;
        
        // string类型
        output += '--- string类型 ---\n';
        let singleQuote = 'Hello, world!';
        let doubleQuote = "Hello, world!";
        let templateString = `Hello, world!`;
        
        output += `let singleQuote = '${singleQuote}';\n`;
        output += `let doubleQuote = "${doubleQuote}";\n`;
        output += `let templateString = \`${templateString}\`;\n\n`;
        
        // 模板字符串
        let name = 'JavaScript';
        let greeting = `Hello, ${name}!`;
        output += `模板字符串: \`${greeting}\`\n\n`;
        
        // symbol类型
        output += '--- symbol类型 ---\n';
        let symbol1 = Symbol();
        let symbol2 = Symbol('description');
        let symbol3 = Symbol('description');
        
        output += `let symbol1 = Symbol();\n`;
        output += `let symbol2 = Symbol('description');\n`;
        output += `symbol2 === symbol3: ${symbol2 === symbol3} (每个symbol都是唯一的)\n\n`;
        
        // bigint类型
        output += '--- bigint类型 ---\n';
        let bigIntLiteral = 9007199254740991n;
        let bigIntFromNumber = BigInt(9007199254740991);
        
        output += `let bigIntLiteral = ${bigIntLiteral}n;\n`;
        output += `let bigIntFromNumber = BigInt(9007199254740991); // ${bigIntFromNumber}\n\n`;
        
        output += '大数精度对比:\n';
        output += `Number.MAX_SAFE_INTEGER + 1: ${Number.MAX_SAFE_INTEGER + 1}\n`;
        output += `Number.MAX_SAFE_INTEGER + 2: ${Number.MAX_SAFE_INTEGER + 2} (精度丢失)\n`;
        output += `9007199254740991n + 1n: ${9007199254740991n + 1n}\n`;
        output += `9007199254740991n + 2n: ${9007199254740991n + 2n} (无精度丢失)\n\n`;
        
        return output;
    },
    
    demonstrateComplexTypes() {
        let output = '=== 复杂数据类型演示 ===\n\n';
        
        // object类型
        output += '--- object类型 ---\n';
        let person = {
            name: '张三',
            age: 25,
            city: '北京',
            greet: function() {
                return '你好，我是' + this.name;
            },
            getInfo() {
                return `${this.name}，${this.age}岁，来自${this.city}`;
            }
        };
        
        output += `let person = ${JSON.stringify(person, null, 2)};\n\n`;
        
        // 访问属性
        output += '访问属性:\n';
        output += `person.name: ${person.name}\n`;
        output += `person['age']: ${person['age']}\n\n`;
        
        // 调用方法
        output += '调用方法:\n';
        output += `person.greet(): ${person.greet()}\n`;
        output += `person.getInfo(): ${person.getInfo()}\n\n`;
        
        // 动态属性
        output += '动态属性操作:\n';
        person.email = 'zhangsan@example.com';
        output += `添加email: person.email = ${person.email}\n`;
        
        delete person.email;
        output += `删除email: person.email = ${person.email}\n\n`;
        
        // 数组类型
        output += '--- 数组类型 ---\n';
        let emptyArray = [];
        let fruits = ['苹果', '香蕉', '橙子'];
        let mixedArray = [1, 'hello', true, null, undefined, {name: '对象'}, [1, 2, 3]];
        
        output += `let fruits = [${fruits.map(f => `'${f}'`).join(', ')}];\n`;
        output += `fruits.length: ${fruits.length}\n`;
        output += `fruits[0]: ${fruits[0]}\n\n`;
        
        // 数组方法
        output += '数组方法:\n';
        output += `fruits.join(', '): "${fruits.join(', ')}"\n`;
        output += `fruits.indexOf('橙子'): ${fruits.indexOf('橙子')}\n`;
        
        let upperFruits = fruits.map(fruit => fruit.toUpperCase());
        output += `fruits.map(fruit => fruit.toUpperCase()): [${upperFruits.map(f => `'${f}'`).join(', ')}]\n\n`;
        
        // 函数类型
        output += '--- 函数类型 ---\n';
        
        // 函数声明
        function add(a, b) {
            return a + b;
        }
        
        // 函数表达式
        const multiply = function(a, b) {
            return a * b;
        };
        
        // 箭头函数
        const subtract = (a, b) => a - b;
        
        output += `function add(a, b) { return a + b; }\n`;
        output += `const multiply = function(a, b) { return a * b; };\n`;
        output += `const subtract = (a, b) => a - b;\n\n`;
        
        output += '函数调用结果:\n';
        output += `add(5, 3): ${add(5, 3)}\n`;
        output += `multiply(5, 3): ${multiply(5, 3)}\n`;
        output += `subtract(5, 3): ${subtract(5, 3)}\n\n`;
        
        // 函数作为值
        const operations = {
            add: add,
            multiply: multiply,
            subtract: subtract
        };
        
        output += '函数作为值:\n';
        output += `const operations = ${JSON.stringify(Object.keys(operations))};\n`;
        output += `operations.calculate = function(a, b, operation) { return this[operation](a, b); };\n`;
        
        // 添加calculate方法
        operations.calculate = function(a, b, operation) {
            return this[operation](a, b);
        };
        
        output += `operations.calculate(5, 3, 'add'): ${operations.calculate(5, 3, 'add')}\n`;
        output += `operations.calculate(5, 3, 'multiply'): ${operations.calculate(5, 3, 'multiply')}\n\n`;
        
        return output;
    },
    
    demonstrateTypeChecking() {
        let output = '=== 类型检查演示 ===\n\n';
        
        // 使用typeof检查基本类型
        output += '--- 使用typeof检查基本类型 ---\n';
        
        let undefinedVar;
        let nullVar = null;
        let booleanVar = true;
        let numberVar = 42;
        let stringVar = 'hello';
        let symbolVar = Symbol();
        let bigIntVar = 123n;
        let objectVar = { name: 'object' };
        let arrayVar = [1, 2, 3];
        let functionVar = function() {};
        
        output += `typeof undefinedVar: ${typeof undefinedVar}\n`;
        output += `typeof nullVar: ${typeof nullVar} (特殊情况)\n`;
        output += `typeof booleanVar: ${typeof booleanVar}\n`;
        output += `typeof numberVar: ${typeof numberVar}\n`;
        output += `typeof stringVar: ${typeof stringVar}\n`;
        output += `typeof symbolVar: ${typeof symbolVar}\n`;
        output += `typeof bigIntVar: ${typeof bigIntVar}\n`;
        output += `typeof objectVar: ${typeof objectVar}\n`;
        output += `typeof arrayVar: ${typeof arrayVar} (数组也是object)\n`;
        output += `typeof functionVar: ${typeof functionVar}\n\n`;
        
        // 使用Array.isArray检查数组
        output += '--- 使用Array.isArray检查数组 ---\n';
        output += `Array.isArray(arrayVar): ${Array.isArray(arrayVar)}\n`;
        output += `Array.isArray(objectVar): ${Array.isArray(objectVar)}\n\n`;
        
        // 使用instanceof检查对象类型
        output += '--- 使用instanceof检查对象类型 ---\n';
        let dateVar = new Date();
        let regexVar = /test/;
        
        output += `dateVar instanceof Date: ${dateVar instanceof Date}\n`;
        output += `regexVar instanceof RegExp: ${regexVar instanceof RegExp}\n`;
        output += `arrayVar instanceof Array: ${arrayVar instanceof Array}\n`;
        output += `objectVar instanceof Object: ${objectVar instanceof Object}\n\n`;
        
        // 检查null
        output += '--- 检查null ---\n';
        output += `nullVar === null: ${nullVar === null}\n`;
        output += `nullVar == null: ${nullVar == null}\n`;
        output += `undefinedVar == null: ${undefinedVar == null}\n\n`;
        
        // 检查undefined
        output += '--- 检查undefined ---\n';
        output += `undefinedVar === undefined: ${undefinedVar === undefined}\n`;
        output += `nullVar === undefined: ${nullVar === undefined}\n\n`;
        
        // 检查空值（null或undefined）
        output += '--- 检查空值（null或undefined）---\n';
        output += `nullVar == null: ${nullVar == null}\n`;
        output += `undefinedVar == null: ${undefinedVar == null}\n`;
        output += `booleanVar == null: ${booleanVar == null}\n\n`;
        
        // 实用类型检查函数
        output += '--- 实用类型检查函数 ---\n';
        
        // 检查是否为空值
        function isNullish(value) {
            return value == null;
        }
        
        // 检查是否为真值
        function isTruthy(value) {
            return !!value;
        }
        
        // 检查是否为数字
        function isNumber(value) {
            return typeof value === 'number' && !isNaN(value);
        }
        
        // 检查是否为整数
        function isInteger(value) {
            return Number.isInteger(value);
        }
        
        // 检查是否为字符串
        function isString(value) {
            return typeof value === 'string';
        }
        
        // 检查是否为函数
        function isFunction(value) {
            return typeof value === 'function';
        }
        
        // 检查是否为普通对象（非数组、函数等）
        function isPlainObject(value) {
            return value !== null && 
                   typeof value === 'object' && 
                   !Array.isArray(value) && 
                   !(value instanceof Date) && 
                   !(value instanceof RegExp) &&
                   !(value instanceof Error) &&
                   typeof value !== 'function';
        }
        
        output += `isNullish(null): ${isNullish(null)}\n`;
        output += `isNullish(undefined): ${isNullish(undefined)}\n`;
        output += `isNullish(0): ${isNullish(0)}\n\n`;
        
        output += `isTruthy(true): ${isTruthy(true)}\n`;
        output += `isTruthy(false): ${isTruthy(false)}\n`;
        output += `isTruthy(0): ${isTruthy(0)}\n`;
        output += `isTruthy(''): ${isTruthy('')}\n`;
        output += `isTruthy('hello'): ${isTruthy('hello')}\n\n`;
        
        output += `isNumber(42): ${isNumber(42)}\n`;
        output += `isNumber(NaN): ${isNumber(NaN)}\n`;
        output += `isNumber('42'): ${isNumber('42')}\n\n`;
        
        output += `isInteger(42): ${isInteger(42)}\n`;
        output += `isInteger(42.5): ${isInteger(42.5)}\n`;
        output += `isInteger('42'): ${isInteger('42')}\n\n`;
        
        output += `isString('hello'): ${isString('hello')}\n`;
        output += `isString(42): ${isString(42)}\n\n`;
        
        output += `isFunction(function() {}): ${isFunction(function() {})}\n`;
        output += `isFunction({}): ${isFunction({})}\n\n`;
        
        output += `isPlainObject({}): ${isPlainObject({})}\n`;
        output += `isPlainObject([]): ${isPlainObject([])}\n`;
        output += `isPlainObject(new Date()): ${isPlainObject(new Date())}\n`;
        
        return output;
    },
    
    // 2.4 类型转换
    demonstrateImplicitConversion() {
        let output = '=== 隐式类型转换演示 ===\n\n';
        
        // 字符串连接
        output += '--- 字符串连接 ---\n';
        output += `'Hello' + ' ' + 'World': "${'Hello' + ' ' + 'World'}"\n`;
        output += `'Hello' + 5: "${'Hello' + 5}"\n`;
        output += `'5' + 5: "${'5' + 5}"\n\n`;
        
        // 算术运算
        output += '--- 算术运算 ---\n';
        output += `'5' * 2: ${'5' * 2}\n`;
        output += `'5' - 2: ${'5' - 2}\n`;
        output += `'5' / 2: ${'5' / 2}\n`;
        output += `'5' % 2: ${'5' % 2}\n\n`;
        
        // 比较运算
        output += '--- 比较运算 ---\n';
        output += `'5' == 5: ${'5' == 5} (值相等)\n`;
        output += `'5' === 5: ${'5' === 5} (严格相等)\n`;
        output += `'5' != 5: ${'5' != 5}\n`;
        output += `'5' !== 5: ${'5' !== 5}\n\n`;
        
        // 逻辑运算
        output += '--- 逻辑运算 ---\n';
        output += `'hello' && 0: ${'hello' && 0}\n`;
        output += `'hello' && 5: ${'hello' && 5}\n`;
        output += `'hello' || 0: ${'hello' || 0}\n`;
        output += `'hello' || 5: ${'hello' || 5}\n`;
        output += `0 && 'hello': ${0 && 'hello'}\n`;
        output += `0 || 'hello': ${0 || 'hello'}\n\n`;
        
        // 条件语句中的类型转换
        output += '--- 条件语句中的类型转换 ---\n';
        output += `if ('') { console.log('空字符串为真'); } else { console.log('空字符串为假'); }\n`;
        output += `结果: 空字符串为假\n\n`;
        
        output += `if (0) { console.log('0为真'); } else { console.log('0为假'); }\n`;
        output += `结果: 0为假\n\n`;
        
        // 常见的隐式转换陷阱
        output += '--- 常见的隐式转换陷阱 ---\n';
        output += `[] + []: ${[] + []} (空数组转为空字符串)\n`;
        output += `[] + {}: ${[] + {}} (对象转为[object Object])\n`;
        output += `{} + []: ${({} + [])} (对象转为[object Object])\n`;
        output += `{} + {}: ${({} + {})} (对象转为[object Object][object Object])\n\n`;
        
        output += `0 == '': ${0 == ''}\n`;
        output += `0 == false: ${0 == false}\n`;
        output.println(`false == '': ${false == ''}\n`);
        output += `null == undefined: ${null == undefined}\n\n`;
        
        // 一元运算符进行类型转换
        output += '--- 一元运算符进行类型转换 ---\n';
        output += `+'123': ${+'123'} (转为数字)\n`;
        output += `+true: ${+true} (转为数字)\n`;
        output += `+false: ${+false} (转为数字)\n`;
        output += `+'hello': ${+'hello'} (转为NaN)\n\n`;
        
        return output;
    },
    
    demonstrateExplicitConversion() {
        let output = '=== 显式类型转换演示 ===\n\n';
        
        // 转换为字符串
        output += '--- 转换为字符串 ---\n';
        let num = 42;
        let bool = true;
        let obj = { a: 1 };
        let arr = [1, 2, 3];
        
        output += `let num = ${num};\n`;
        output += `let bool = ${bool};\n`;
        output += `let obj = ${JSON.stringify(obj)};\n`;
        output += `let arr = ${JSON.stringify(arr)};\n\n`;
        
        output += `String(num): "${String(num)}"\n`;
        output += `num.toString(): "${num.toString()}"\n`;
        output += `num + '': "${num + ''}"\n\n`;
        
        output += `String(bool): "${String(bool)}"\n`;
        output += `bool.toString(): "${bool.toString()}"\n`;
        output += `bool + '': "${bool + ''}"\n\n`;
        
        output += `String(obj): "${String(obj)}"\n`;
        output += `obj.toString(): "${obj.toString()}"\n\n`;
        
        output += `String(arr): "${String(arr)}"\n`;
        output += `arr.toString(): "${arr.toString()}"\n`;
        output += `arr.join(','): "${arr.join(',')}"\n\n`;
        
        // 转换为数字
        output += '--- 转换为数字 ---\n';
        let strNum = '123';
        let strFloat = '123.45';
        let strInvalid = '123abc';
        let emptyStr = '';
        let spaceStr = '   ';
        
        output += `let strNum = '${strNum}';\n`;
        output += `let strFloat = '${strFloat}';\n`;
        output += `let strInvalid = '${strInvalid}';\n`;
        output += `let emptyStr = '${emptyStr}';\n`;
        output += `let spaceStr = '${spaceStr}';\n\n`;
        
        output += `Number(strNum): ${Number(strNum)}\n`;
        output += `parseInt(strNum): ${parseInt(strNum)}\n`;
        output += `parseFloat(strNum): ${parseFloat(strNum)}\n\n`;
        
        output += `Number(strFloat): ${Number(strFloat)}\n`;
        output += `parseInt(strFloat): ${parseInt(strFloat)}\n`;
        output += `parseFloat(strFloat): ${parseFloat(strFloat)}\n\n`;
        
        output += `Number(strInvalid): ${Number(strInvalid)}\n`;
        output += `parseInt(strInvalid): ${parseInt(strInvalid)}\n`;
        output += `parseFloat(strInvalid): ${parseFloat(strInvalid)}\n\n`;
        
        output += `Number(emptyStr): ${Number(emptyStr)}\n`;
        output += `parseInt(emptyStr): ${parseInt(emptyStr)}\n`;
        output += `parseFloat(emptyStr): ${parseFloat(emptyStr)}\n\n`;
        
        output += `Number(spaceStr): ${Number(spaceStr)}\n`;
        output += `parseInt(spaceStr): ${parseInt(spaceStr)}\n`;
        output += `parseFloat(spaceStr): ${parseFloat(spaceStr)}\n\n`;
        
        // 进制转换
        output += '--- 进制转换 ---\n';
        let binaryStr = '1010';
        let octalStr = '12';
        let hexStr = 'A';
        
        output += `let binaryStr = '${binaryStr}'; // 二进制\n`;
        output += `let octalStr = '${octalStr}'; // 八进制\n`;
        output += `let hexStr = '${hexStr}'; // 十六进制\n\n`;
        
        output += `parseInt(binaryStr, 2): ${parseInt(binaryStr, 2)}\n`;
        output += `parseInt(octalStr, 8): ${parseInt(octalStr, 8)}\n`;
        output += `parseInt(hexStr, 16): ${parseInt(hexStr, 16)}\n\n`;
        
        output += `(10).toString(2): ${(10).toString(2)} // 二进制\n`;
        output += `(10).toString(8): ${(10).toString(8)} // 八进制\n`;
        output += `(10).toString(16): ${(10).toString(16)} // 十六进制\n\n`;
        
        // 转换为布尔值
        output += '--- 转换为布尔值 ---\n';
        output += `Boolean(0): ${Boolean(0)}\n`;
        output += `Boolean(""): ${Boolean("")}\n`;
        output += `Boolean(null): ${Boolean(null)}\n`;
        output += `Boolean(undefined): ${Boolean(undefined)}\n`;
        output += `Boolean(NaN): ${Boolean(NaN)}\n\n`;
        
        output += `Boolean(1): ${Boolean(1)}\n`;
        output += `Boolean(-1): ${Boolean(-1)}\n`;
        output += `Boolean("hello"): ${Boolean("hello")}\n`;
        output += `Boolean({}): ${Boolean({})}\n`;
        output += `Boolean([]): ${Boolean([])}\n`;
        output += `Boolean(function() {}): ${Boolean(function() {})}\n\n`;
        
        // 使用双重否定转为布尔值
        output += '--- 使用双重否定转为布尔值 ---\n';
        output += `!!0: ${!!0}\n`;
        output += `!!"hello": ${!!"hello"}\n`;
        output += `!!null: ${!!null}\n`;
        output += `!!{}: ${!!{}}\n\n`;
        
        // 解析JSON
        output += '--- 解析JSON ---\n';
        let jsonStr = '{"name":"张三","age":25}';
        let invalidJsonStr = '{"name":"张三","age":}';
        
        output += `let jsonStr = '${jsonStr}';\n`;
        output += `let invalidJsonStr = '${invalidJsonStr}';\n\n`;
        
        try {
            let data = JSON.parse(jsonStr);
            output += `JSON.parse(jsonStr): ${JSON.stringify(data)}\n`;
        } catch (error) {
            output += `JSON.parse(jsonStr) 错误: ${error.message}\n`;
        }
        
        try {
            let data = JSON.parse(invalidJsonStr);
            output += `JSON.parse(invalidJsonStr): ${JSON.stringify(data)}\n`;
        } catch (error) {
            output += `JSON.parse(invalidJsonStr) 错误: ${error.message}\n`;
        }
        
        return output;
    },
    
    // 2.5 运算符
    demonstrateArithmeticOperators(num1, num2) {
        let output = '=== 算术运算符演示 ===\n\n';
        
        output += `let a = ${num1}, b = ${num2};\n\n`;
        
        output += '--- 基本算术运算 ---\n';
        output += `a + b: ${num1 + num2} (加法)\n`;
        output += `a - b: ${num1 - num2} (减法)\n`;
        output += `a * b: ${num1 * num2} (乘法)\n`;
        output += `a / b: ${num1 / num2} (除法)\n`;
        output += `a % b: ${num1 % num2} (取余)\n`;
        output += `a ** b: ${num1 ** num2} (幂运算)\n\n`;
        
        // 自增和自减
        output += '--- 自增和自减 ---\n';
        let x = num1;
        output += `let x = ${x};\n`;
        output += `x++ (后自增): ${x++}, x现在是${x}\n`;
        output += `++x (前自增): ${++x}, x现在是${x}\n`;
        output += `x-- (后自减): ${x--}, x现在是${x}\n`;
        output += `--x (前自减): ${--x}, x现在是${x}\n\n`;
        
        return output;
    },
    
    demonstrateComparisonOperators(value1, value2) {
        let output = '=== 比较运算符演示 ===\n\n';
        
        output += `let a = ${typeof value1 === 'string' ? `'${value1}'` : value1}, b = ${typeof value2 === 'string' ? `'${value2}'` : value2};\n\n`;
        
        output += '--- 相等比较 ---\n';
        output += `a == b: ${value1 == value2} (值相等，进行类型转换)\n`;
        output += `a === b: ${value1 === value2} (严格相等)\n`;
        output += `a != b: ${value1 != value2} (值不相等，进行类型转换)\n`;
        output += `a !== b: ${value1 !== value2} (严格不相等)\n\n`;
        
        output += '--- 大小比较 ---\n';
        output += `a > b: ${value1 > value2}\n`;
        output += `a >= b: ${value1 >= value2}\n`;
        output += `a < b: ${value1 < value2}\n`;
        output += `a <= b: ${value1 <= value2}\n\n`;
        
        // 特殊情况比较
        output += '--- 特殊情况比较 ---\n';
        output += `null == undefined: ${null == undefined}\n`;
        output += `null === undefined: ${null === undefined}\n`;
        output += `NaN == NaN: ${NaN == NaN}\n`;
        output += `NaN === NaN: ${NaN === NaN}\n\n`;
        
        output += `0 == '': ${0 == ''}\n`;
        output += `0 === '': ${0 === ''}\n`;
        output += `false == '': ${false == ''}\n`;
        output += `false === '': ${false === ''}\n\n`;
        
        // 对象比较
        output += '--- 对象比较 ---\n';
        let obj1 = { a: 1 };
        let obj2 = { a: 1 };
        let obj3 = obj1;
        
        output += `let obj1 = {a: 1}, obj2 = {a: 1}, obj3 = obj1;\n`;
        output += `obj1 == obj2: ${obj1 == obj2} (不同对象)\n`;
        output += `obj1 === obj2: ${obj1 === obj2} (不同对象)\n`;
        output += `obj1 == obj3: ${obj1 == obj3} (同一对象)\n`;
        output += `obj1 === obj3: ${obj1 === obj3} (同一对象)\n\n`;
        
        return output;
    },
    
    demonstrateLogicalOperators(value1, value2) {
        let output = '=== 逻辑运算符演示 ===\n\n';
        
        // 解析输入值
        let val1, val2;
        
        if (value1 === 'true') val1 = true;
        else if (value1 === 'false') val1 = false;
        else if (value1 === '0') val1 = 0;
        else if (value1 === '1') val1 = 1;
        else if (value1 === "''") val1 = '';
        else if (value1 === "'hello'") val1 = 'hello';
        
        if (value2 === 'true') val2 = true;
        else if (value2 === 'false') val2 = false;
        else if (value2 === '0') val2 = 0;
        else if (value2 === '1') val2 = 1;
        else if (value2 === "''") val2 = '';
        else if (value2 === "'hello'") val2 = 'hello';
        
        output += `let a = ${typeof val1 === 'string' ? `'${val1}'` : val1}, b = ${typeof val2 === 'string' ? `'${val2}'` : val2};\n`;
        output += `Boolean(a): ${Boolean(val1)}, Boolean(b): ${Boolean(val2)}\n\n`;
        
        output += '--- 逻辑与 (&&) ---\n';
        let andResult = val1 && val2;
        output += `a && b: ${typeof andResult === 'string' ? `'${andResult}'` : andResult}\n`;
        output += `短路特性: 如果a为假值，则结果为a；否则结果为b\n\n`;
        
        output += '--- 逻辑或 (||) ---\n';
        let orResult = val1 || val2;
        output += `a || b: ${typeof orResult === 'string' ? `'${orResult}'` : orResult}\n`;
        output += `短路特性: 如果a为真值，则结果为a；否则结果为b\n\n`;
        
        output += '--- 逻辑非 (!) ---\n';
        output += `!a: ${!val1}\n`;
        output += `!b: ${!val2}\n`;
        output += `!!a: ${!!val1} (转为布尔值)\n\n`;
        
        // 实际应用示例
        output += '--- 实际应用示例 ---\n';
        
        // 默认值设置
        function greet(name) {
            name = name || 'Guest';
            return 'Hello, ' + name;
        }
        
        output += `greet('Alice'): ${greet('Alice')}\n`;
        output += `greet(): ${greet()}\n\n`;
        
        // 安全访问对象属性
        const user = {
            name: '张三'
            // 没有 age 属性
        };
        
        const age = user.age || 25;
        output += `const user = { name: '张三' };\n`;
        output += `const age = user.age || 25; // ${age}\n\n`;
        
        return output;
    },
    
    demonstrateBitwiseOperators(num1, num2) {
        let output = '=== 位运算符演示 ===\n\n';
        
        output += `let a = ${num1}, b = ${num2};\n`;
        output += `a 的二进制: ${num1.toString(2)}\n`;
        output += `b 的二进制: ${num2.toString(2)}\n\n`;
        
        output += '--- 基本位运算 ---\n';
        let andResult = num1 & num2;
        output += `a & b (按位与): ${andResult} (二进制: ${andResult.toString(2)})\n`;
        
        let orResult = num1 | num2;
        output += `a | b (按位或): ${orResult} (二进制: ${orResult.toString(2)})\n`;
        
        let xorResult = num1 ^ num2;
        output += `a ^ b (按位异或): ${xorResult} (二进制: ${xorResult.toString(2)})\n`;
        
        let notResult = ~num1;
        output += `~a (按位非): ${notResult} (二进制补码)\n\n`;
        
        output += '--- 移位运算 ---\n';
        let leftShiftResult = num1 << 1;
        output += `a << 1 (左移1位): ${leftShiftResult} (${num1} * 2^1)\n`;
        
        let rightShiftResult = num1 >> 1;
        output += `a >> 1 (右移1位): ${rightShiftResult} (除以2向下取整)\n`;
        
        let unsignedRightShiftResult = num1 >>> 1;
        output += `a >>> 1 (无符号右移1位): ${unsignedRightShiftResult}\n\n`;
        
        // 实际应用示例
        output += '--- 实际应用示例 ---\n';
        
        // 快速判断奇偶数
        function isEven(num) {
            return (num & 1) === 0;  // 如果最后一位是0，则为偶数
        }
        
        output += `isEven(${num1}): ${isEven(num1)} (${num1}是${isEven(num1) ? '偶数' : '奇数'})\n`;
        output += `isEven(${num2}): ${isEven(num2)} (${num2}是${isEven(num2) ? '偶数' : '奇数'})\n\n`;
        
        // 权限管理
        const READ_PERMISSION = 1;    // 001
        const WRITE_PERMISSION = 2;   // 010
        const EXECUTE_PERMISSION = 4; // 100
        
        let userPermissions = READ_PERMISSION | WRITE_PERMISSION; // 011 = 3
        
        output += '权限管理示例:\n';
        output += `READ_PERMISSION = ${READ_PERMISSION} (二进制: ${READ_PERMISSION.toString(2)})\n`;
        output += `WRITE_PERMISSION = ${WRITE_PERMISSION} (二进制: ${WRITE_PERMISSION.toString(2)})\n`;
        output += `EXECUTE_PERMISSION = ${EXECUTE_PERMISSION} (二进制: ${EXECUTE_PERMISSION.toString(2)})\n\n`;
        
        output += `userPermissions = READ_PERMISSION | WRITE_PERMISSION = ${userPermissions} (二进制: ${userPermissions.toString(2)})\n`;
        output += `userPermissions & READ_PERMISSION: ${userPermissions & READ_PERMISSION} (有读权限)\n`;
        output += `userPermissions & WRITE_PERMISSION: ${userPermissions & WRITE_PERMISSION} (有写权限)\n`;
        output += `userPermissions & EXECUTE_PERMISSION: ${userPermissions & EXECUTE_PERMISSION} (无执行权限)\n\n`;
        
        return output;
    },
    
    demonstrateTernaryOperator(value, type) {
        let output = '=== 三元运算符演示 ===\n\n';
        
        if (type === 'age') {
            let age = parseInt(value);
            output += `let age = ${age};\n\n`;
            
            // 基本三元运算符
            let message = age >= 18 ? '成年人' : '未成年人';
            output += `age >= 18 ? '成年人' : '未成年人': "${message}"\n\n`;
            
            // 链式三元运算符
            let grade = age >= 60 ? '老年人' : 
                       age >= 18 ? '成年人' : '未成年人';
            output += `age >= 60 ? '老年人' : age >= 18 ? '成年人' : '未成年人': "${grade}"\n\n`;
            
        } else if (type === 'score') {
            let score = parseInt(value);
            output += `let score = ${score};\n\n`;
            
            // 多级三元运算符
            let grade = score >= 90 ? 'A' : 
                       score >= 80 ? 'B' : 
                       score >= 70 ? 'C' : 
                       score >= 60 ? 'D' : 'F';
            output += `score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F': "${grade}"\n\n`;
            
            // 对应的成绩描述
            let gradeDesc = score >= 90 ? '优秀' : 
                          score >= 80 ? '良好' : 
                          score >= 70 ? '中等' : 
                          score >= 60 ? '及格' : '不及格';
            output += `score >= 90 ? '优秀' : ... : "${gradeDesc}"\n\n`;
        }
        
        // 作为函数返回值
        function getGreeting(hour) {
            return hour < 12 ? '早上好' : 
                   hour < 18 ? '下午好' : '晚上好';
        }
        
        output += '--- 作为函数返回值 ---\n';
        output += `function getGreeting(hour) {\n`;
        output += `    return hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好';\n`;
        output += `}\n\n`;
        
        output += `getGreeting(9): "${getGreeting(9)}"\n`;
        output += `getGreeting(14): "${getGreeting(14)}"\n`;
        output += `getGreeting(20): "${getGreeting(20)}"\n\n`;
        
        // 嵌套使用
        output += '--- 嵌套使用 ---\n';
        let age = parseInt(value);
        let hasLicense = true;
        let canDrive = age >= 18 ? 
                      (hasLicense ? '可以开车' : '需要考取驾照') : 
                      '年龄不够';
        output += `let canDrive = age >= 18 ? (hasLicense ? '可以开车' : '需要考取驾照') : '年龄不够';\n`;
        output += `结果: "${canDrive}"\n\n`;
        
        return output;
    },
    
    // 2.6 条件语句
    demonstrateIfStatement(score, age) {
        let output = '=== if语句演示 ===\n\n';
        
        // 基本if语句
        output += `if (${score} >= 60) {\n`;
        if (score >= 60) {
            output += `    console.log('及格了！'); // 已执行\n`;
        } else {
            output += `    // 条件不满足，不执行\n`;
        }
        output += `}\n\n`;
        
        // if-else语句
        output += `if (${score} >= 60) {\n`;
        output += `    console.log('及格了！');\n`;
        output += `} else {\n`;
        output += `    console.log('不及格！');\n`;
        output += `}\n`;
        output += `结果: "${score >= 60 ? '及格了！' : '不及格！'}"\n\n`;
        
        // if-else if-else语句
        output += `if (${score} >= 90) {\n`;
        output += `    console.log('优秀');\n`;
        output += `} else if (${score} >= 80) {\n`;
        output += `    console.log('良好');\n`;
        output += `} else if (${score} >= 70) {\n`;
        output += `    console.log('中等');\n`;
        output += `} else if (${score} >= 60) {\n`;
        output += `    console.log('及格');\n`;
        output += `} else {\n`;
        output += `    console.log('不及格');\n`;
        output += `}\n`;
        
        let grade;
        if (score >= 90) {
            grade = '优秀';
        } else if (score >= 80) {
            grade = '良好';
        } else if (score >= 70) {
            grade = '中等';
        } else if (score >= 60) {
            grade = '及格';
        } else {
            grade = '不及格';
        }
        output += `结果: "${grade}"\n\n`;
        
        // 嵌套if语句
        output += '--- 嵌套if语句 ---\n';
        output += `if (${age} >= 18) {\n`;
        if (age >= 18) {
            output += `    if (${true}) { // hasLicense = true\n`;
            output += `        console.log('可以开车');\n`;
            output += `    } else {\n`;
            output += `        console.log('需要先考取驾照');\n`;
            output += `    }\n`;
            output += `} else {\n`;
            output += `    console.log('年龄不够');\n`;
            output += `}\n`;
        
        let drivingStatus;
        if (age >= 18) {
            if (true) { // hasLicense = true
                drivingStatus = '可以开车';
            } else {
                drivingStatus = '需要先考取驾照';
            }
        } else {
            drivingStatus = '年龄不够';
        }
        output += `结果: "${drivingStatus}"\n\n`;
        
        // 使用逻辑运算符简化if语句
        output += '--- 使用逻辑运算符简化if语句 ---\n';
        let hasPermission = true;
        
        // 传统写法
        output += `// 传统写法\n`;
        output += `if (hasPermission) {\n`;
        output += `    console.log('有权限访问');\n`;
        output += `}\n`;
        
        // 简化写法
        output += `// 简化写法\n`;
        output += `hasPermission && console.log('有权限访问'); // 如果hasPermission为true，则执行console.log\n`;
        output += `执行: ${hasPermission ? '"有权限访问" (已执行)' : '未执行'}\n\n`;
        
        return output;
    },
    
    demonstrateSwitchStatement(day, grade) {
        let output = '=== switch语句演示 ===\n\n';
        
        // 基本switch语句
        output += `--- 基本switch语句 ---\n`;
        output += `switch (${day}) {\n`;
        
        let dayName;
        switch (day) {
            case 0:
                dayName = '星期日';
                output += `    case 0: dayName = '星期日'; break;\n`;
                break;
            case 1:
                dayName = '星期一';
                output += `    case 1: dayName = '星期一'; break;\n`;
                break;
            case 2:
                dayName = '星期二';
                output += `    case 2: dayName = '星期二'; break;\n`;
                break;
            case 3:
                dayName = '星期三';
                output += `    case 3: dayName = '星期三'; break;\n`;
                break;
            case 4:
                dayName = '星期四';
                output += `    case 4: dayName = '星期四'; break;\n`;
                break;
            case 5:
                dayName = '星期五';
                output += `    case 5: dayName = '星期五'; break;\n`;
                break;
            case 6:
                dayName = '星期六';
                output += `    case 6: dayName = '星期六'; break;\n`;
                break;
            default:
                dayName = '未知';
                output += `    default: dayName = '未知'; break;\n`;
                break;
        }
        output += `}\n`;
        output += `结果: "${dayName}"\n\n`;
        
        // 多个case使用相同代码
        output += '--- 多个case使用相同代码 ---\n';
        output += `switch ('${grade}') {\n`;
        
        let gradeDesc;
        switch (grade) {
            case 'A':
            case 'B':
                gradeDesc = '优秀';
                output += `    case 'A':\n`;
                output += `    case 'B': console.log('优秀'); break;\n`;
                break;
            case 'C':
            case 'D':
                gradeDesc = '及格';
                output += `    case 'C':\n`;
                output += `    case 'D': console.log('及格'); break;\n`;
                break;
            case 'F':
                gradeDesc = '不及格';
                output += `    case 'F': console.log('不及格'); break;\n`;
                break;
            default:
                gradeDesc = '未知成绩';
                output += `    default: console.log('未知成绩'); break;\n`;
                break;
        }
        output += `}\n`;
        output += `结果: "${gradeDesc}"\n\n`;
        
        // 使用表达式
        output += '--- 使用表达式 ---\n';
        let age = 25;
        output += `let age = ${age};\n`;
        output += `switch (true) {\n`;
        output += `    case age < 18:\n`;
        output += `        console.log('未成年'); break;\n`;
        output += `    case age >= 18 && age < 60:\n`;
        output += `        console.log('成年'); break;\n`;
        output += `    case age >= 60:\n`;
        output += `        console.log('老年'); break;\n`;
        output += `    default:\n`;
        output += `        console.log('无效年龄'); break;\n`;
        output += `}\n`;
        
        let ageDesc;
        switch (true) {
            case age < 18:
                ageDesc = '未成年';
                break;
            case age >= 18 && age < 60:
                ageDesc = '成年';
                break;
            case age >= 60:
                ageDesc = '老年';
                break;
            default:
                ageDesc = '无效年龄';
                break;
        }
        output += `结果: "${ageDesc}"\n\n`;
        
        return output;
    },
    
    // 2.7 循环语句
    demonstrateForLoop(start, end, step) {
        let output = '=== for循环演示 ===\n\n';
        
        // 基本for循环
        output += '--- 基本for循环 ---\n';
        output += `for (let i = ${start}; i < ${end}; i += ${step}) {\n`;
        output += `    console.log(i);\n`;
        output += `}\n`;
        output += '输出: ';
        
        for (let i = start; i < end; i += step) {
            if (i > start) output += ', ';
            output += i;
        }
        output += '\n\n';
        
        // 计算1到n的和
        output += '--- 计算1到n的和 ---\n';
        let sum = 0;
        for (let i = 1; i <= 10; i++) {
            sum += i;
        }
        output += `let sum = 0;\n`;
        output += `for (let i = 1; i <= 10; i++) {\n`;
        output += `    sum += i;\n`;
        output += `}\n`;
        output += `结果: sum = ${sum}\n\n`;
        
        // 遍历数组
        output += '--- 遍历数组 ---\n';
        let fruits = ['苹果', '香蕉', '橙子'];
        output += `let fruits = [${fruits.map(f => `'${f}'`).join(', ')}];\n`;
        output += `for (let i = 0; i < fruits.length; i++) {\n`;
        output += `    console.log(\`水果\${i + 1}: \${fruits[i]}\`);\n`;
        output += `}\n`;
        output += '输出:\n';
        
        for (let i = 0; i < fruits.length; i++) {
            output += `水果${i + 1}: ${fruits[i]}\n`;
        }
        output += '\n';
        
        // 省略表达式
        output += '--- 省略表达式 ---\n';
        output += `let i = 0;\n`;
        output += `for (; i < 3; i++) {\n`;
        output += `    console.log(i);\n`;
        output += `}\n`;
        output += '输出: ';
        
        let i = 0;
        for (; i < 3; i++) {
            if (i > 0) output += ', ';
            output += i;
        }
        output += '\n\n';
        
        return output;
    },
    
    demonstrateWhileLoop(number) {
        let output = '=== while循环演示 ===\n\n';
        
        // 基本while循环
        output += '--- 基本while循环 ---\n';
        output += `let count = 0;\n`;
        output += `while (count < ${number}) {\n`;
        output += `    console.log(count);\n`;
        output += `    count++;\n`;
        output += `}\n`;
        output += '输出: ';
        
        let count = 0;
        while (count < number) {
            if (count > 0) output += ', ';
            output += count;
            count++;
        }
        output += '\n\n';
        
        // 计算阶乘
        output += '--- 计算阶乘 ---\n';
        function factorial(n) {
            let result = 1;
            let i = n;
            
            output += `function factorial(${n}) {\n`;
            output += `    let result = 1;\n`;
            output += `    let i = ${n};\n\n`;
            
            while (i > 0) {
                output += `    result *= i; // ${result} * ${i} = ${result * i}\n`;
                result *= i;
                i--;
            }
            
            output += `    return ${result};\n`;
            output += `}\n\n`;
            
            return result;
        }
        
        let factResult = factorial(number);
        output += `${number}的阶乘: ${factResult}\n\n`;
        
        // 输入验证
        output += '--- 输入验证 ---\n';
        output += `let isValidInput = false;\n`;
        output += `let input;\n\n`;
        output += `do {\n`;
        output += `    input = prompt('请输入一个有效的数字:');\n`;
        output += `    isValidInput = !isNaN(input) && input.trim() !== '';\n`;
        output += `} while (!isValidInput);\n\n`;
        output += `console.log('您输入的数字是:', input);\n\n`;
        output += '注意: 在实际网页中，这会弹出对话框要求用户输入\n';
        output += '在这个演示中，我们假设用户输入了一个有效的数字\n\n';
        
        return output;
    },
    
    demonstrateDoWhileLoop(number) {
        let output = '=== do-while循环演示 ===\n\n';
        
        // 基本do-while循环
        output += '--- 基本do-while循环 ---\n';
        output += `let i = ${number};\n`;
        output += `do {\n`;
        output += `    console.log(i);\n`;
        output += `    i++;\n`;
        output += `} while (i < ${number + 3});\n`;
        output += '输出: ';
        
        let i = number;
        do {
            if (i > number) output += ', ';
            output += i;
            i++;
        } while (i < number + 3);
        output += '\n\n';
        
        // 至少执行一次的示例
        output += '--- 至少执行一次的示例 ---\n';
        output += `let isValidInput = false;\n`;
        output += `let input;\n\n`;
        output += `do {\n`;
        output += `    input = prompt('请输入一个有效的数字:');\n`;
        output += `    isValidInput = !isNaN(input) && input.trim() !== '';\n`;
        output += `    if (!isValidInput) {\n`;
        output += `        console.log('输入无效，请重新输入');\n`;
        output += `    }\n`;
        output += `} while (!isValidInput);\n\n`;
        output += `console.log('您输入的数字是:', input);\n\n`;
        output += '这个例子展示了do-while循环至少执行一次的特性，\n';
        output += '即使用户第一次输入就有效，代码块至少会执行一次。\n\n';
        
        return output;
    },
    
    demonstrateForInOfLoop() {
        let output = '=== for-in和for-of循环演示 ===\n\n';
        
        // for-in循环 - 遍历对象属性
        output += '--- for-in循环 - 遍历对象属性 ---\n';
        let person = {
            name: '张三',
            age: 30,
            city: '北京'
        };
        
        output += `let person = ${JSON.stringify(person)};\n`;
        output += `for (let key in person) {\n`;
        output += `    console.log(\`\${key}: \${person[key]}\`);\n`;
        output += `}\n`;
        output += '输出:\n';
        
        for (let key in person) {
            output += `${key}: ${person[key]}\n`;
        }
        output += '\n';
        
        // for-in循环 - 遍历数组索引
        output += '--- for-in循环 - 遍历数组索引 ---\n';
        let colors = ['红色', '绿色', '蓝色'];
        output += `let colors = [${colors.map(c => `'${c}'`).join(', ')}];\n`;
        output += `for (let index in colors) {\n`;
        output += `    console.log(\`索引\${index}: \${colors[index]}\`);\n`;
        output += `}\n`;
        output += '输出:\n';
        
        for (let index in colors) {
            output += `索引${index}: ${colors[index]}\n`;
        }
        output += '\n';
        
        // for-of循环 - 遍历数组值
        output += '--- for-of循环 - 遍历数组值 ---\n';
        output += `for (let color of colors) {\n`;
        output += `    console.log(color);\n`;
        output += `}\n`;
        output += '输出:\n';
        
        for (let color of colors) {
            output += `${color}\n`;
        }
        output += '\n';
        
        // for-of循环 - 遍历字符串
        output += '--- for-of循环 - 遍历字符串 ---\n';
        let text = 'JavaScript';
        output += `let text = '${text}';\n`;
        output += `for (let char of text) {\n`;
        output += `    console.log(char);\n`;
        output += `}\n`;
        output += '输出: ';
        
        for (let char of text) {
            output += char + ' ';
        }
        output += '\n\n';
        
        // for-of循环 - 遍历Map和Set
        output += '--- for-of循环 - 遍历Map和Set ---\n';
        let mySet = new Set([1, 2, 3, 4]);
        output += `let mySet = new Set([1, 2, 3, 4]);\n`;
        output += `for (let value of mySet) {\n`;
        output += `    console.log(value);\n`;
        output += `}\n`;
        output += 'Set输出: ';
        
        for (let value of mySet) {
            output += value + ' ';
        }
        output += '\n';
        
        let myMap = new Map([
            ['name', '李四'],
            ['age', 25]
        ]);
        output += `\nlet myMap = new Map([['name', '李四'], ['age', 25]]);\n`;
        output += `for (let [key, value] of myMap) {\n`;
        output += `    console.log(\`\${key}: \${value}\`);\n`;
        output += `}\n`;
        output += 'Map输出:\n';
        
        for (let [key, value] of myMap) {
            output += `${key}: ${value}\n`;
        }
        output += '\n';
        
        // for-in与for-of的区别
        output += '--- for-in与for-of的区别 ---\n';
        let array = [10, 20, 30];
        array.customProperty = '自定义属性';
        
        output += `let array = [10, 20, 30];\n`;
        output += `array.customProperty = '自定义属性';\n\n`;
        
        output += 'for-in遍历（包含自定义属性，索引是字符串）:\n';
        for (let index in array) {
            output += `${index}: ${array[index]}\n`;
        }
        
        output += '\nfor-of遍历（只遍历数组元素，值是实际值）:\n';
        for (let value of array) {
            output += `${value}\n`;
        }
        output += '\n';
        
        return output;
    },
    
    demonstrateBreakContinue(limit) {
        let output = '=== break和continue演示 ===\n\n';
        
        // break - 跳出循环
        output += '--- break - 跳出循环 ---\n';
        output += `for (let i = 0; i < ${limit}; i++) {\n`;
        output += `    if (i === 5) {\n`;
        output += `        break; // 当i等于5时，跳出循环\n`;
        output += `    }\n`;
        output += `    console.log(i);\n`;
        output += `}\n`;
        output += '输出: ';
        
        for (let i = 0; i < limit; i++) {
            if (i === 5) {
                break;
            }
            if (i > 0) output += ', ';
            output += i;
        }
        output += '\n\n';
        
        // continue - 跳过当前迭代
        output += '--- continue - 跳过当前迭代 ---\n';
        output += `for (let i = 0; i < ${limit}; i++) {\n`;
        output += `    if (i % 2 === 0) {\n`;
        output += `        continue; // 跳过偶数\n`;
        output += `    }\n`;
        output += `    console.log(i);\n`;
        output += `}\n`;
        output += '输出（仅奇数）: ';
        
        for (let i = 0; i < limit; i++) {
            if (i % 2 === 0) {
                continue;
            }
            if (i > 1) output += ', ';
            output += i;
        }
        output += '\n\n';
        
        // 标记循环 - 用于嵌套循环
        output += '--- 标记循环 - 用于嵌套循环 ---\n';
        output += `outerLoop: for (let i = 0; i < 3; i++) {\n`;
        output += `    innerLoop: for (let j = 0; j < 3; j++) {\n`;
        output += `        console.log(\`i=\${i}, j=\${j}\`);\n`;
        output += `        \n`;
        output += `        if (i === 1 && j === 1) {\n`;
        output += `            break outerLoop; // 跳出外层循环\n`;
        output += `        }\n`;
        output += `    }\n`;
        output += `}\n`;
        output += '输出:\n';
        
        outerLoop: for (let i = 0; i < 3; i++) {
            innerLoop: for (let j = 0; j < 3; j++) {
                output += `i=${i}, j=${j}\n`;
                
                if (i === 1 && j === 1) {
                    output += '(跳出外层循环)\n';
                    break outerLoop;
                }
            }
        }
        output += '\n';
        
        // continue与标记
        output += '--- continue与标记 ---\n';
        output += `outerLoop: for (let i = 0; i < 3; i++) {\n`;
        output += `    for (let j = 0; j < 3; j++) {\n`;
        output += `        if (i === 1 && j === 1) {\n`;
        output += `            continue outerLoop; // 跳过外层循环的当前迭代\n`;
        output += `        }\n`;
        output += `        console.log(\`i=\${i}, j=\${j}\`);\n`;
        output += `    }\n`;
        output += `}\n`;
        output += '输出:\n';
        
        outerLoop: for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (i === 1 && j === 1) {
                    output += `(跳过i=${i}, j=${j}并继续外层循环)\n`;
                    continue outerLoop;
                }
                output += `i=${i}, j=${j}\n`;
            }
        }
        output += '\n';
        
        return output;
    },
    
    // 2.8 异常处理
    demonstrateTryCatch() {
        let output = '=== try-catch语句演示 ===\n\n';
        
        // 基本try-catch
        output += '--- 基本try-catch ---\n';
        output += `try {\n`;
        output += `    // 可能出错的代码\n`;
        output += `    let result = 10 / 0; // Infinity，不会出错\n`;
        output += `    console.log(result);\n`;
        output += `    \n`;
        output += `    // 下面这行会出错\n`;
        output += `    console.log(undefinedVariable);\n`;
        output += `} catch (error) {\n`;
        output += `    // 处理错误\n`;
        output += `    console.error('发生错误:', error.message);\n`;
        output += `}\n\n`;
        
        // 使用finally
        output += '--- 使用finally ---\n';
        output += `try {\n`;
        output += `    console.log('尝试执行操作');\n`;
        output += `    // 模拟一个可能失败的操作\n`;
        output += `    let success = Math.random() > 0.5;\n`;
        output += `    if (!success) {\n`;
        output += `        throw new Error('操作失败');\n`;
        output += `    }\n`;
        output += `    console.log('操作成功');\n`;
        output += `} catch (error) {\n`;
        output += `    console.error('捕获到错误:', error.message);\n`;
        output += `} finally {\n`;
        output += `    console.log('无论成功或失败，都会执行finally块');\n`;
        output += `}\n\n`;
        
        // 实际演示
        output += '实际演示:\n';
        
        try {
            console.log('尝试执行操作');
            // 模拟一个可能失败的操作
            let success = Math.random() > 0.5;
            if (!success) {
                throw new Error('操作失败');
            }
            console.log('操作成功');
            output += '操作成功\n';
        } catch (error) {
            console.error('捕获到错误:', error.message);
            output += `捕获到错误: ${error.message}\n`;
        } finally {
            console.log('无论成功或失败，都会执行finally块');
            output += '无论成功或失败，都会执行finally块\n';
        }
        output += '\n';
        
        // 嵌套try-catch
        output += '--- 嵌套try-catch ---\n';
        output += `try {\n`;
        output += `    console.log('外层try');\n`;
        output += `    \n`;
        output += `    try {\n`;
        output += `        console.log('内层try');\n`;
        output += `        // 内层错误\n`;
        output += `        throw new Error('内层错误');\n`;
        output += `    } catch (innerError) {\n`;
        output += `        console.log('捕获内层错误:', innerError.message);\n`;
        output += `        // 重新抛出错误\n`;
        output += `        throw innerError;\n`;
        output += `    }\n`;
        output += `} catch (outerError) {\n`;
        output += `    console.log('捕获外层错误:', outerError.message);\n`;
        output += `}\n\n`;
        
        return output;
    },
    
    demonstrateThrowStatement(age) {
        let output = '=== throw语句演示 ===\n\n';
        
        // 抛出自定义错误
        output += '--- 抛出自定义错误 ---\n';
        output += `function validateAge(age) {\n`;
        output += `    if (typeof age !== 'number') {\n`;
        output += `        throw new TypeError('年龄必须是数字');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    if (age < 0) {\n`;
        output += `        throw new RangeError('年龄不能为负数');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    if (age > 150) {\n`;
        output += `        throw new RangeError('年龄看起来不合理');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    return true;\n`;
        output += `}\n\n`;
        
        // 测试年龄验证
        output += `--- 测试年龄验证 ---\n`;
        
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
        
        function testAgeValidation(age) {
            try {
                validateAge(age);
                output += `${age} 是一个有效的年龄\n`;
            } catch (error) {
                output += `验证年龄 ${age} 时出错: ${error.message}\n`;
            }
        }
        
        output += `验证年龄 ${age}:\n`;
        testAgeValidation(age);
        output += '\n';
        
        output += `验证年龄 -5:\n`;
        testAgeValidation(-5);
        output += '\n';
        
        output += `验证年龄 'abc':\n`;
        testAgeValidation('abc');
        output += '\n';
        
        output += `验证年龄 200:\n`;
        testAgeValidation(200);
        output += '\n';
        
        // 抛出不同类型的错误
        output += '--- 抛出不同类型的错误 ---\n';
        output += `function processData(data) {\n`;
        output += `    if (data === null || data === undefined) {\n`;
        output += `        throw new Error('数据不能为空');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    if (typeof data !== 'object') {\n`;
        output += `        throw new TypeError('数据必须是对象');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    if (!data.id) {\n`;
        output += `        throw new Error('数据缺少必需的id字段');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    console.log('数据处理成功');\n`;
        output += `}\n\n`;
        
        function processData(data) {
            if (data === null || data === undefined) {
                throw new Error('数据不能为空');
            }
            
            if (typeof data !== 'object') {
                throw new TypeError('数据必须是对象');
            }
            
            if (!data.id) {
                throw new Error('数据缺少必需的id字段');
            }
            
            return '数据处理成功';
        }
        
        function testProcessData(data) {
            try {
                const result = processData(data);
                output += `${result}\n`;
            } catch (error) {
                output += `数据处理出错: ${error.message}\n`;
            }
        }
        
        output += `测试数据处理: { name: '测试数据' }\n`;
        testProcessData({ name: '测试数据' });
        output += '\n';
        
        // 自定义错误类型
        output += '--- 自定义错误类型 ---\n';
        output += `class ValidationError extends Error {\n`;
        output += `    constructor(message) {\n`;
        output += `        super(message);\n`;
        output += `        this.name = 'ValidationError';\n`;
        output += `    }\n`;
        output += `}\n\n`;
        
        output += `function validateUser(user) {\n`;
        output += `    if (!user.name) {\n`;
        output += `        throw new ValidationError('用户名不能为空');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    if (!user.email) {\n`;
        output += `        throw new ValidationError('邮箱不能为空');\n`;
        output += `    }\n`;
        output += `    \n`;
        output += `    return true;\n`;
        output += `}\n\n`;
        
        class ValidationError extends Error {
            constructor(message) {
                super(message);
                this.name = 'ValidationError';
            }
        }
        
        function validateUser(user) {
            if (!user.name) {
                throw new ValidationError('用户名不能为空');
            }
            
            if (!user.email) {
                throw new ValidationError('邮箱不能为空');
            }
            
            return true;
        }
        
        function testValidateUser(user) {
            try {
                validateUser(user);
                output += `用户验证成功: ${JSON.stringify(user)}\n`;
            } catch (error) {
                output += `用户验证失败: ${error.name} - ${error.message}\n`;
            }
        }
        
        output += `测试用户验证: { email: 'test@example.com' }\n`;
        testValidateUser({ email: 'test@example.com' });
        output += '\n';
        
        return output;
    }
};

// 创建练习命名空间
const chapter2Exercises = {
    // 简单计算器
    calculate(num1, num2, operation) {
        let result;
        
        switch (operation) {
            case '+':
                result = num1 + num2;
                break;
            case '-':
                result = num1 - num2;
                break;
            case '*':
                result = num1 * num2;
                break;
            case '/':
                if (num2 === 0) {
                    return '错误：除数不能为0';
                }
                result = num1 / num2;
                break;
            case '%':
                result = num1 % num2;
                break;
            default:
                return '错误：不支持的运算符';
        }
        
        return `${num1} ${operation} ${num2} = ${result}`;
    },
    
    // 闰年判断
    checkLeapYear(year) {
        // 闰年规则：
        // 1. 能被4整除但不能被100整除，或者
        // 2. 能被400整除
        let isLeapYear = (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
        
        let result = `${year}年`;
        
        if (isLeapYear) {
            result += '是闰年（有366天，2月份有29天）';
        } else {
            result += '不是闰年（有365天，2月份有28天）';
        }
        
        return result;
    },
    
    // 字符统计
    countCharacters(str) {
        // 创建空对象用于存储字符计数
        const charCount = {};
        
        // 遍历字符串中的每个字符
        for (let char of str) {
            // 忽略空格（可选）
            if (char === ' ') continue;
            
            // 如果字符已存在，计数加1；否则初始化为1
            if (charCount[char]) {
                charCount[char]++;
            } else {
                charCount[char] = 1;
            }
        }
        
        // 生成结果字符串
        let result = `字符串 "${str}" 中的字符统计:\n`;
        result += '--------------------------------\n';
        
        // 按字母顺序排序
        const sortedChars = Object.keys(charCount).sort();
        
        // 显示每个字符及其出现次数
        for (let char of sortedChars) {
            result += `'${char}': ${charCount[char]}次\n`;
        }
        
        result += '--------------------------------\n';
        result += `总字符数（不计空格）: ${str.replace(/\s/g, '').length}\n`;
        result += `唯一字符数: ${sortedChars.length}`;
        
        return result;
    }
};

// 在控制台输出示例
console.log('chapter2_syntax_and_types.js 已加载');
console.log('可用的示例函数:', Object.keys(chapter2Examples));
console.log('可用的练习函数:', Object.keys(chapter2Exercises));