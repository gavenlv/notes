// 函数参数示例
function demonstrateFunctionParameters(): void {
    console.log("\n=== Function Parameters Demo ===");
    
    // 参数类型注解
    function greet(name: string, age: number): string {
        return `Hello, ${name}! You are ${age} years old.`;
    }
    
    console.log(greet("Alice", 30));
    
    // 可选参数
    function buildName(firstName: string, lastName?: string): string {
        if (lastName) {
            return `${firstName} ${lastName}`;
        } else {
            return firstName;
        }
    }
    
    console.log(buildName("John", "Doe")); // "John Doe"
    console.log(buildName("John")); // "John"
    
    // 默认参数
    function greet2(name: string, greeting: string = "Hello"): string {
        return `${greeting}, ${name}!`;
    }
    
    console.log(greet2("Alice")); // "Hello, Alice!"
    console.log(greet2("Alice", "Hi")); // "Hi, Alice!"
    
    // 默认参数不必在可选参数之前
    function createFullName(firstName: string, lastName: string = "Smith", middleName?: string): string {
        if (middleName) {
            return `${firstName} ${middleName} ${lastName}`;
        } else {
            return `${firstName} ${lastName}`;
        }
    }
    
    console.log(createFullName("John")); // "John Smith"
    console.log(createFullName("John", "Doe")); // "John Doe"
    console.log(createFullName("John", "Doe", "Michael")); // "John Michael Doe"
    
    // 剩余参数
    function sum(...numbers: number[]): number {
        return numbers.reduce((total, current) => total + current, 0);
    }
    
    console.log(`sum(1, 2, 3, 4, 5): ${sum(1, 2, 3, 4, 5)}`); // 15
    console.log(`sum(10, 20): ${sum(10, 20)}`); // 30
    
    // 混合普通参数和剩余参数
    function greetPeople(greeting: string, ...names: string[]): string {
        return `${greeting}, ${names.join(", ")}!`;
    }
    
    console.log(greetPeople("Hello", "Alice", "Bob", "Charlie")); // "Hello, Alice, Bob, Charlie!"
    
    // 函数参数的解构
    interface Person {
        name: string;
        age: number;
        address?: {
            street: string;
            city: string;
        };
    }
    
    function introducePerson({ name, age, address }: Person): string {
        let intro = `I'm ${name} and I'm ${age} years old`;
        if (address) {
            intro += `. I live at ${address.street}, ${address.city}`;
        }
        return intro;
    }
    
    const person1: Person = { name: "Alice", age: 30 };
    const person2: Person = { 
        name: "Bob", 
        age: 25, 
        address: { street: "123 Main St", city: "New York" } 
    };
    
    console.log(introducePerson(person1));
    console.log(introducePerson(person2));
    
    // 参数重命名
    function printCoordinates({ x: horizontal, y: vertical }: { x: number; y: number }): void {
        console.log(`Horizontal: ${horizontal}, Vertical: ${vertical}`);
    }
    
    printCoordinates({ x: 10, y: 20 });
    
    // 函数参数默认值与解构结合
    function createUser({ 
        name = "Anonymous", 
        age = 18, 
        isAdmin = false 
    }: { name?: string; age?: number; isAdmin?: boolean } = {}): string {
        return `${name} (${age} years old) - ${isAdmin ? "Admin" : "Regular User"}`;
    }
    
    console.log(createUser()); // 使用所有默认值
    console.log(createUser({ name: "Alice" })); // 只提供name
    console.log(createUser({ name: "Bob", age: 25 })); // 提供name和age
    console.log(createUser({ name: "Charlie", isAdmin: true })); // 提供name和isAdmin
}

demonstrateFunctionParameters();