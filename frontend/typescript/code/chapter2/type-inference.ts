// 类型推断示例
function demonstrateTypeInference(): void {
    console.log("\n=== Type Inference Demo ===");
    
    // 初始化变量时的类型推断
    let myString = "Hello, TypeScript"; // 推断为string类型
    let myNumber = 42;                  // 推断为number类型
    let myBoolean = true;               // 推断为boolean类型
    
    console.log(`Type of myString: ${typeof myString}`);
    console.log(`Type of myNumber: ${typeof myNumber}`);
    console.log(`Type of myBoolean: ${typeof myBoolean}`);
    
    // 函数返回值类型推断
    function add(a: number, b: number) {
        return a + b; // 推断返回类型为number
    }
    
    function greet(name: string) {
        return `Hello, ${name}`; // 推断返回类型为string
    }
    
    console.log(`Addition result: ${add(5, 3)}`);
    console.log(`Greeting: ${greet("Alice")}`);
    
    // 数组类型推断
    let numbers = [1, 2, 3, 4, 5]; // 推断为number[]
    let mixed = [1, "two", true];  // 推断为(number | string | boolean)[]
    
    console.log(`Numbers array: ${numbers}`);
    console.log(`Mixed array: ${mixed}`);
    
    // 对象类型推断
    let person = {
        name: "John Doe",
        age: 30,
        isActive: true
    }; // 推断为 { name: string; age: number; isActive: boolean; }
    
    console.log(`Person: ${JSON.stringify(person)}`);
    
    // 上下文类型推断
    let myAdd: (x: number, y: number) => number = function(x, y) { 
        return x + y; 
    }; // 参数类型从上下文推断
    
    console.log(`Contextual typing result: ${myAdd(10, 20)}`);
    
    // 最佳类型推断
    let zoo = [new Rhino(), new Elephant(), new Snake()];
    // zoo被推断为 Animal[]
    
    // 类型推断失败时的默认类型
    let myData = null; // 推断为any
    let myValue;        // 推断为any
    
    console.log(`Default any types: ${myData}, ${myValue}`);
}

// 示例类
class Animal {}
class Rhino extends Animal {}
class Elephant extends Animal {}
class Snake extends Animal {}

demonstrateTypeInference();