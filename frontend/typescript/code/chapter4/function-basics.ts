// 函数基础示例
function demonstrateFunctionBasics(): void {
    console.log("=== Function Basics Demo ===");
    
    // 函数声明
    function add(x: number, y: number): number {
        return x + y;
    }
    
    // 函数表达式
    const subtract = function(x: number, y: number): number {
        return x - y;
    };
    
    // 箭头函数
    const multiply = (x: number, y: number): number => {
        return x * y;
    };
    
    // 简化的箭头函数
    const divide = (x: number, y: number): number => x / y;
    
    console.log(`add(5, 3): ${add(5, 3)}`);
    console.log(`subtract(5, 3): ${subtract(5, 3)}`);
    console.log(`multiply(5, 3): ${multiply(5, 3)}`);
    console.log(`divide(6, 3): ${divide(6, 3)}`);
    
    // 完整的函数类型
    let myAdd: (x: number, y: number) => number = function(x: number, y: number): number { 
        return x + y; 
    };
    
    // 使用类型别名
    type MathOperation = (x: number, y: number) => number;
    let myOperation: MathOperation = (x, y) => x * y;
    
    // 接口定义函数类型
    interface MathFunction {
        (x: number, y: number): number;
    }
    
    let myMathFunction: MathFunction = (x, y) => x - y;
    
    console.log(`myAdd(10, 20): ${myAdd(10, 20)}`);
    console.log(`myOperation(10, 20): ${myOperation(10, 20)}`);
    console.log(`myMathFunction(10, 20): ${myMathFunction(10, 20)}`);
    
    // 函数作为参数
    function calculate(a: number, b: number, operation: MathOperation): number {
        return operation(a, b);
    }
    
    console.log(`calculate(5, 3, add): ${calculate(5, 3, add)}`);
    console.log(`calculate(5, 3, subtract): ${calculate(5, 3, subtract)}`);
    console.log(`calculate(5, 3, multiply): ${calculate(5, 3, multiply)}`);
    
    // 函数作为返回值
    function getOperation(operator: string): MathOperation {
        switch (operator) {
            case "add":
                return (a, b) => a + b;
            case "subtract":
                return (a, b) => a - b;
            case "multiply":
                return (a, b) => a * b;
            case "divide":
                return (a, b) => b !== 0 ? a / b : 0;
            default:
                throw new Error(`Unknown operator: ${operator}`);
        }
    }
    
    const addOperation = getOperation("add");
    const multiplyOperation = getOperation("multiply");
    
    console.log(`addOperation(7, 8): ${addOperation(7, 8)}`);
    console.log(`multiplyOperation(7, 8): ${multiplyOperation(7, 8)}`);
}

demonstrateFunctionBasics();