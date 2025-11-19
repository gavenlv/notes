// 类型断言示例
function demonstrateTypeAssertions(): void {
    console.log("\n=== Type Assertions Demo ===");
    
    // 基本类型断言
    let someValue: any = "this is a string";
    let strLength: number = (someValue as string).length;
    console.log(`String length (as syntax): ${strLength}`);
    
    let someValue2: any = "this is another string";
    let strLength2: number = (<string>someValue2).length;
    console.log(`String length (angle bracket syntax): ${strLength2}`);
    
    // 联合类型中的断言
    interface Cat {
        meow(): void;
    }
    
    interface Dog {
        bark(): void;
    }
    
    function makeSound(animal: Cat | Dog): void {
        // 使用类型断言调用特定方法
        if ((animal as Cat).meow) {
            (animal as Cat).meow();
        } else {
            (animal as Dog).bark();
        }
    }
    
    // 实现接口的类
    class TabbyCat implements Cat {
        meow(): void {
            console.log("Tabby cat: Meow!");
        }
    }
    
    class Poodle implements Dog {
        bark(): void {
            console.log("Poodle: Woof!");
        }
    }
    
    const cat = new TabbyCat();
    const dog = new Poodle();
    
    makeSound(cat);
    makeSound(dog);
    
    // DOM元素类型断言
    const inputElement = document.getElementById("username") as HTMLInputElement;
    if (inputElement) {
        inputElement.value = "default";
        console.log(`Input value set to: ${inputElement.value}`);
    }
    
    // 非空断言操作符
    interface User {
        name: string;
        address?: {
            street: string;
            city: string;
        };
    }
    
    function getUserAddress(user: User): string {
        // 使用非空断言告诉TypeScript address属性不是undefined
        const address = user.address!;
        return `${address.street}, ${address.city}`;
    }
    
    const user: User = {
        name: "John Doe",
        address: {
            street: "123 Main St",
            city: "New York"
        }
    };
    
    console.log(`User address: ${getUserAddress(user)}`);
    
    // 可能导致错误的非空断言
    const userWithoutAddress: User = {
        name: "Jane Doe"
    };
    
    try {
        // 这行代码会在运行时出错
        const address = getUserAddress(userWithoutAddress);
        console.log(`User address: ${address}`);
    } catch (e) {
        console.error("Error:", e.message);
    }
    
    // 更安全的替代方案 - 可选链操作符
    function safeGetUserAddress(user: User): string | undefined {
        return user.address?.street ? 
            `${user.address.street}, ${user.address.city}` : 
            undefined;
    }
    
    const safeAddress = safeGetUserAddress(userWithoutAddress);
    console.log(`Safe address: ${safeAddress || "Address not available"}`);
    
    // 双重断言
    interface Event {
        type: string;
        timestamp: number;
    }
    
    interface MouseEvent extends Event {
        x: number;
        y: number;
    }
    
    function handleEvent(event: Event): void {
        // 双重断言：先断言为any，再断言为目标类型
        const mouseEvent = event as any as MouseEvent;
        console.log(`Mouse clicked at (${mouseEvent.x}, ${mouseEvent.y})`);
    }
    
    // 注意：双重断言可能很危险，因为编译器不进行类型检查
    // 只有在确信类型正确时才使用
    
    // 对象字面量断言
    const config = {
        apiUrl: "https://api.example.com",
        timeout: 5000
    } as const; // 使对象属性变为只读
    
    console.log("API URL:", config.apiUrl);
    // config.apiUrl = "https://new-api.example.com"; // 错误：只读属性
    
    // 常量断言与字面量类型
    type Direction = "North" | "South" | "East" | "West";
    
    const directions1: Direction[] = ["North", "South", "East", "West"]; // 类型是Direction[]
    const directions2 = ["North", "South", "East", "West"] as const;      // 类型是readonly ["North", "South", "East", "West"]
    
    console.log("Directions 1:", directions1);
    console.log("Directions 2:", directions2);
}

demonstrateTypeAssertions();