// 基本类型示例
function demonstrateBasicTypes(): void {
    // 字符串类型
    let message: string = "Hello, TypeScript!";
    message = "Hello, World!"; // 有效
    
    // 数字类型
    let count: number = 10;
    count = 20.5; // 有效，整数和浮点数都是number类型
    
    // 布尔类型
    let isActive: boolean = true;
    isActive = false; // 有效
    
    // 数组类型
    let numbers: number[] = [1, 2, 3, 4, 5];
    let strings: Array<string> = ["hello", "world", "typescript"];
    
    // 元组类型 - 固定长度和类型的数组
    let person: [string, number] = ["Alice", 30];
    
    // 枚举类型
    enum Color {
        Red,        // 默认值为0
        Green = 1,  // 显式设置值为1
        Blue = 2    // 显式设置值为2
    }
    let c: Color = Color.Blue; // 值为2
    
    // Any类型 - 可以是任何类型
    let notSure: any = 4;
    notSure = "can be a string";
    notSure = false; // 也可以是布尔值
    
    // Void类型 - 通常用于函数返回值
    function logMessage(): void {
        console.log("This is a log message");
    }
    
    // Null 和 Undefined
    let u: undefined = undefined;
    let n: null = null;
    
    // Never类型 - 表示永不返回的函数
    function error(message: string): never {
        throw new Error(message);
    }
    
    // Object类型
    let obj: object = { name: "Alice" };
    
    // 打印所有类型
    console.log("message:", message);
    console.log("count:", count);
    console.log("isActive:", isActive);
    console.log("numbers:", numbers);
    console.log("strings:", strings);
    console.log("person:", person);
    console.log("Color.Blue:", c);
    console.log("notSure:", notSure);
    console.log("u:", u);
    console.log("n:", n);
    console.log("obj:", obj);
    
    // 调用void函数
    logMessage();
}

// 调用函数
demonstrateBasicTypes();