// 接口基础示例
function demonstrateInterfaceBasics(): void {
    console.log("=== Interface Basics Demo ===");
    
    // 基本接口定义
    interface Person {
        name: string;
        age: number;
        greet(): string;
    }
    
    // 使用接口
    const person: Person = {
        name: "Alice",
        age: 30,
        greet() {
            return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
        }
    };
    
    console.log(person.greet());
    
    // 可选属性
    interface Car {
        make: string;
        model: string;
        year?: number; // 可选属性
        color?: string; // 可选属性
    }
    
    const car1: Car = {
        make: "Toyota",
        model: "Corolla"
        // year和color是可选的，可以不提供
    };
    
    const car2: Car = {
        make: "Honda",
        model: "Civic",
        year: 2020,
        color: "Red"
    };
    
    console.log("Car 1:", car1);
    console.log("Car 2:", car2);
    
    // 只读属性
    interface Point {
        readonly x: number; // 只读属性
        readonly y: number; // 只读属性
    }
    
    const point: Point = { x: 10, y: 20 };
    console.log(`Point coordinates: (${point.x}, ${point.y})`);
    
    // point.x = 30; // 错误，x是只读属性
    
    // 函数类型接口
    interface SearchFunc {
        (source: string, subString: string): boolean;
    }
    
    const mySearch: SearchFunc = function(source: string, subString: string): boolean {
        return source.search(subString) > -1;
    };
    
    console.log(`Search result: ${mySearch("Hello, World", "World")}`);
    
    // 可索引类型接口
    interface StringArray {
        [index: number]: string;
    }
    
    const myArray: StringArray = ["Bob", "Alice", "Eve"];
    console.log(`Element at index 1: ${myArray[1]}`);
    
    // 对象索引签名
    interface Dictionary {
        [key: string]: string;
    }
    
    const myDict: Dictionary = {
        "name": "Alice",
        "email": "alice@example.com"
    };
    
    console.log(`Name from dictionary: ${myDict["name"]}`);
}

demonstrateInterfaceBasics();