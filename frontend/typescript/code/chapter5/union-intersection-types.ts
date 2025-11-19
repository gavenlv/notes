// 联合类型和交叉类型示例
function demonstrateUnionIntersectionTypes(): void {
    console.log("=== Union and Intersection Types Demo ===");
    
    // 基本联合类型
    let value: string | number;
    value = "Hello";
    value = 42;
    
    function processValue(value: string | number): void {
        if (typeof value === "string") {
            console.log(`String length: ${value.length}`);
        } else {
            console.log(`Number doubled: ${value * 2}`);
        }
    }
    
    processValue("Hello, TypeScript!");
    processValue(42);
    
    // 字面量联合类型
    type Direction = "North" | "South" | "East" | "West";
    type EventName = "click" | "focus" | "blur";
    
    function setTheme(theme: "light" | "dark"): void {
        console.log(`Theme set to: ${theme}`);
    }
    
    function handleEvent(event: EventName): void {
        console.log(`Handling event: ${event}`);
    }
    
    setTheme("dark");
    handleEvent("click");
    
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
            animal.meow(); // TypeScript知道animal是Cat
        } else {
            animal.bark(); // TypeScript知道animal是Dog
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
    
    // 基本交叉类型
    interface Person {
        name: string;
        age: number;
    }
    
    interface Employee {
        employeeId: string;
        department: string;
    }
    
    // 交叉类型
    type PersonEmployee = Person & Employee;
    
    let personEmployee: PersonEmployee = {
        name: "Alice",
        age: 30,
        employeeId: "EMP123",
        department: "Engineering"
    };
    
    console.log("Person Employee:", personEmployee);
    
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
    
    // 可辨识联合类型
    interface Square {
        kind: "square";
        size: number;
    }
    
    interface Rectangle {
        kind: "rectangle";
        width: number;
        height: number;
    }
    
    interface Circle {
        kind: "circle";
        radius: number;
    }
    
    type Shape = Square | Rectangle | Circle;
    
    function area(shape: Shape): number {
        switch (shape.kind) {
            case "square":
                return shape.size * shape.size;
            case "rectangle":
                return shape.width * shape.height;
            case "circle":
                return Math.PI * shape.radius ** 2;
            default:
                // 确保所有情况都被处理
                const _exhaustiveCheck: never = shape;
                return _exhaustiveCheck;
        }
    }
    
    const square: Square = { kind: "square", size: 5 };
    const rectangle: Rectangle = { kind: "rectangle", width: 10, height: 20 };
    const circle: Circle = { kind: "circle", radius: 7 };
    
    console.log(`Square area: ${area(square)}`);
    console.log(`Rectangle area: ${area(rectangle)}`);
    console.log(`Circle area: ${area(circle)}`);
}

demonstrateUnionIntersectionTypes();