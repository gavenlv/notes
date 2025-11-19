// 联合类型和交叉类型示例
function demonstrateUnionAndIntersectionTypes(): void {
    console.log("\n=== Union and Intersection Types Demo ===");
    
    // 联合类型示例
    function padLeft(value: string, padding: string | number): string {
        if (typeof padding === "number") {
            return Array(padding + 1).join(" ") + value;
        }
        if (typeof padding === "string") {
            return padding + value;
        }
        throw new Error(`Expected string or number, got '${typeof padding}'.`);
    }
    
    console.log(padLeft("Hello", 4));      // "    Hello"
    console.log(padLeft("Hello", ">>>")); // ">>>Hello"
    
    // 字面量联合类型
    type Theme = "light" | "dark";
    type EventName = "click" | "focus" | "blur";
    
    function setTheme(theme: Theme): void {
        console.log(`Theme set to: ${theme}`);
    }
    
    function handleEvent(event: EventName): void {
        console.log(`Handling event: ${event}`);
    }
    
    setTheme("dark");
    handleEvent("click");
    
    // 交叉类型示例
    interface BusinessPartner {
        name: string;
        credit: number;
    }
    
    interface Identity {
        id: number;
        name: string;
    }
    
    interface Contact {
        email: string;
        phone: string;
    }
    
    type Employee = Identity & BusinessPartner & Contact;
    
    let emp: Employee = {
        id: 100,
        name: "John Doe",
        credit: 7000,
        email: "john.doe@example.com",
        phone: "555-123-4567"
    };
    
    console.log("Employee:", emp);
    
    // 使用交叉类型扩展接口
    interface ColorWheel {
        color: string;
    }
    
    interface Cicle {
        radius: number;
    }
    
    type ColorfulCircle = ColorWheel & Cicle;
    
    let cc: ColorfulCircle = {
        color: "red",
        radius: 10
    };
    
    console.log("Colorful Circle:", cc);
    
    // 联合类型与交叉类型的结合使用
    type EitherStringOrNumber = string | number;
    type BothStringAndNumber = string & number; // 实际上是never
    
    // 类型守卫
    function processValue(value: string | number): void {
        if (typeof value === "string") {
            console.log(`String length: ${value.length}`);
        } else {
            console.log(`Number doubled: ${value * 2}`);
        }
    }
    
    processValue("Hello, TypeScript!");
    processValue(42);
    
    // 自定义类型守卫
    interface Cat {
        meow(): void;
    }
    
    interface Dog {
        bark(): void;
    }
    
    function isCat(animal: Cat | Dog): animal is Cat {
        return (animal as Cat).meow !== undefined;
    }
    
    function makeSound(animal: Cat | Dog): void {
        if (isCat(animal)) {
            animal.meow();
        } else {
            animal.bark();
        }
    }
    
    // 实现接口的类
    class PersianCat implements Cat {
        meow(): void {
            console.log("Persian cat says: Meow!");
        }
    }
    
    class GoldenRetriever implements Dog {
        bark(): void {
            console.log("Golden Retriever says: Woof!");
        }
    }
    
    const cat = new PersianCat();
    const dog = new GoldenRetriever();
    
    makeSound(cat);
    makeSound(dog);
}

demonstrateUnionAndIntersectionTypes();