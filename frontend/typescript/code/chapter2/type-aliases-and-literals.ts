// 类型别名和字面量类型示例
function demonstrateTypeAliasesAndLiterals(): void {
    console.log("\n=== Type Aliases and Literal Types Demo ===");
    
    // 基本类型别名
    type Name = string;
    type Age = number;
    type IsActive = boolean;
    
    // 对象类型别名
    type Person = {
        name: Name;
        age: Age;
        isActive: IsActive;
        greet(): string;
    };
    
    // 使用类型别名
    const john: Person = {
        name: "John",
        age: 30,
        isActive: true,
        greet() {
            return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
        }
    };
    
    console.log(john.greet());
    
    // 联合类型别名
    type Status = "pending" | "in-progress" | "completed" | "failed";
    
    interface Task {
        id: number;
        title: string;
        status: Status;
    }
    
    const tasks: Task[] = [
        { id: 1, title: "Learn TypeScript", status: "in-progress" },
        { id: 2, title: "Write Code Examples", status: "completed" },
        { id: 3, title: "Deploy Application", status: "pending" }
    ];
    
    console.log("Tasks:", tasks);
    
    // 函数类型别名
    type Calculator = (a: number, b: number) => number;
    
    const add: Calculator = (a, b) => a + b;
    const subtract: Calculator = (a, b) => a - b;
    const multiply: Calculator = (a, b) => a * b;
    const divide: Calculator = (a, b) => b !== 0 ? a / b : 0;
    
    console.log(`10 + 5 = ${add(10, 5)}`);
    console.log(`10 - 5 = ${subtract(10, 5)}`);
    console.log(`10 * 5 = ${multiply(10, 5)}`);
    console.log(`10 / 5 = ${divide(10, 5)}`);
    
    // 泛型类型别名
    type Container<T> = {
        value: T;
        getValue(): T;
        setValue(newValue: T): void;
    };
    
    function createContainer<T>(value: T): Container<T> {
        let currentValue = value;
        
        return {
            value: currentValue,
            getValue() {
                return currentValue;
            },
            setValue(newValue) {
                currentValue = newValue;
            }
        };
    }
    
    const stringContainer = createContainer("Hello");
    console.log("String container:", stringContainer.getValue());
    
    stringContainer.setValue("World");
    console.log("Updated string container:", stringContainer.getValue());
    
    const numberContainer = createContainer(42);
    console.log("Number container:", numberContainer.getValue());
    
    // 映射类型别名
    type Readonly<T> = {
        readonly [P in keyof T]: T[P];
    };
    
    type Partial<T> = {
        [P in keyof T]?: T[P];
    };
    
    interface User {
        id: number;
        name: string;
        email: string;
        password: string;
    }
    
    type ReadonlyUser = Readonly<User>;
    type PartialUser = Partial<User>;
    
    const user: ReadonlyUser = {
        id: 1,
        name: "Alice",
        email: "alice@example.com",
        password: "secret"
    };
    
    // user.id = 2; // 错误，只读属性不能修改
    
    const partialUser: PartialUser = {
        name: "Bob" // 只有name属性是必需的
    };
    
    console.log("Readonly user:", user);
    console.log("Partial user:", partialUser);
    
    // 字面量类型
    type Direction = "North" | "South" | "East" | "West";
    type DiceRoll = 1 | 2 | 3 | 4 | 5 | 6;
    type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
    
    function move(direction: Direction): void {
        console.log(`Moving ${direction}`);
    }
    
    function rollDice(): DiceRoll {
        return Math.floor(Math.random() * 6) + 1 as DiceRoll;
    }
    
    function makeRequest(url: string, method: HttpMethod): void {
        console.log(`Making ${method} request to ${url}`);
    }
    
    move("North");
    console.log(`Dice roll result: ${rollDice()}`);
    makeRequest("https://api.example.com/users", "GET");
    
    // 模板字面量类型 (TypeScript 4.1+)
    type EventName = `on${Capitalize<string>}`;
    
    // 使用模板字面量类型
    type ButtonEvent = `onClick` | `onDoubleClick`;
    type InputEvent = `onFocus` | `onBlur` | `onChange`;
    
    const buttonEvents: ButtonEvent[] = ["onClick", "onDoubleClick"];
    const inputEvents: InputEvent[] = ["onFocus", "onBlur", "onChange"];
    
    console.log("Button events:", buttonEvents);
    console.log("Input events:", inputEvents);
}

demonstrateTypeAliasesAndLiterals();