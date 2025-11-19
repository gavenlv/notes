// 基本类型示例
function demonstrateBasicTypes(): void {
    console.log("=== Basic Types Demo ===");
    
    // 布尔值
    let isDone: boolean = false;
    console.log(`Boolean: ${isDone}`);
    
    // 数字
    let decimal: number = 6;
    let hex: number = 0xf00d;
    let binary: number = 0b1010;
    let octal: number = 0o744;
    console.log(`Numbers: ${decimal}, ${hex}, ${binary}, ${octal}`);
    
    // 字符串
    let color: string = "blue";
    let fullName: string = `John Doe`;
    let age: number = 37;
    let sentence: string = `Hello, my name is ${fullName}.
I'll be ${age + 1} years old next month.`;
    console.log(sentence);
    
    // 数组
    let list1: number[] = [1, 2, 3];
    let list2: Array<number> = [4, 5, 6];
    console.log(`Arrays: ${list1}, ${list2}`);
    
    // 元组
    let x: [string, number];
    x = ["hello", 10]; // 正确
    console.log(`Tuple: ${x[0]}, ${x[1]}`);
    
    // 枚举
    enum Color {Red, Green, Blue}
    let c: Color = Color.Green;
    console.log(`Enum: ${c}`);
    
    enum Status {
        Success = 200,
        NotFound = 404,
        Error = 500
    }
    console.log(`Status codes: ${Status.Success}, ${Status.NotFound}, ${Status.Error}`);
    
    // any类型
    let notSure: any = 4;
    notSure = "maybe a string";
    notSure = false;
    console.log(`Any type: ${notSure}`);
    
    // void类型
    function warnUser(): void {
        console.log("This is a warning message");
    }
    warnUser();
    
    // null和undefined
    let u: undefined = undefined;
    let n: null = null;
    console.log(`Null and undefined: ${u}, ${n}`);
    
    // never类型
    function error(message: string): never {
        throw new Error(message);
    }
    
    // object类型
    let obj: object = {prop: 0};
    console.log(`Object: ${JSON.stringify(obj)}`);
}

demonstrateBasicTypes();