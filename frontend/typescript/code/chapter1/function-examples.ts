// 函数示例
// 1. 基本函数定义
function add(a: number, b: number): number {
    return a + b;
}

// 2. 可选参数
function greet(name: string, greeting?: string): string {
    if (greeting) {
        return `${greeting}, ${name}!`;
    }
    return `Hello, ${name}!`;
}

// 3. 默认参数
function createMultiplier(multiplier: number = 2): (value: number) => number {
    return function(value: number): number {
        return value * multiplier;
    };
}

// 4. 剩余参数
function sum(...numbers: number[]): number {
    return numbers.reduce((total, current) => total + current, 0);
}

// 5. 函数重载
function combine(a: string, b: string): string;
function combine(a: number, b: number): number;
function combine(a: string | number, b: string | number): string | number {
    if (typeof a === "string" && typeof b === "string") {
        return a + b;
    }
    if (typeof a === "number" && typeof b === "number") {
        return a + b;
    }
    throw new Error("Invalid arguments");
}

// 6. 箭头函数
const multiply = (a: number, b: number): number => a * b;

// 7. 函数类型
type MathOperation = (a: number, b: number) => number;
let operation: MathOperation;

operation = add;
console.log("Addition:", operation(5, 3));

operation = multiply;
console.log("Multiplication:", operation(5, 3));

// 8. 回调函数
function processData(data: number[], callback: (result: number) => void): void {
    const result = data.reduce((sum, current) => sum + current, 0);
    callback(result);
}

// 9. 异步函数
async function fetchData(url: string): Promise<any> {
    // 模拟API调用
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ data: "Some data from API" });
        }, 1000);
    });
}

// 10. 递归函数
function factorial(n: number): number {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// 调用所有函数
console.log("Function Examples:");
console.log("===================");

console.log("add(5, 3):", add(5, 3));
console.log('greet("Alice"):', greet("Alice"));
console.log('greet("Bob", "Good morning"):', greet("Bob", "Good morning"));

const double = createMultiplier(2);
console.log("double(5):", double(5));

const triple = createMultiplier(3);
console.log("triple(5):", triple(5));

console.log("sum(1, 2, 3, 4, 5):", sum(1, 2, 3, 4, 5));

console.log('combine("Hello", "World"):', combine("Hello", "World"));
console.log("combine(10, 20):", combine(10, 20));

console.log("multiply(5, 3):", multiply(5, 3));

processData([10, 20, 30], (result) => {
    console.log("Callback result:", result);
});

fetchData("https://api.example.com/data").then(data => {
    console.log("Fetched data:", data);
});

console.log("factorial(5):", factorial(5));