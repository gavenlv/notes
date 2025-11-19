// 接口示例
// 1. 基本接口定义
interface Person {
    name: string;
    age: number;
    isStudent: boolean;
}

// 2. 可选属性
interface Car {
    make: string;
    model: string;
    year?: number; // 可选属性
    color?: string; // 可选属性
}

// 3. 只读属性
interface Point {
    readonly x: number; // 只读属性
    readonly y: number; // 只读属性
}

// 4. 函数类型接口
interface SearchFunc {
    (source: string, subString: string): boolean;
}

// 5. 可索引类型接口
interface StringArray {
    [index: number]: string;
}

// 6. 类类型接口
interface ClockInterface {
    currentTime: Date;
    setTime(d: Date): void;
}

// 7. 继承接口
interface Shape {
    color: string;
}

interface Square extends Shape {
    sideLength: number;
}

// 8. 混合类型接口
interface Counter {
    (start: number): string; // 函数类型
    interval: number;        // 属性
    reset(): void;          // 方法
}

// 9. 实现接口的类
class Clock implements ClockInterface {
    currentTime: Date = new Date();
    setTime(d: Date) {
        this.currentTime = d;
    }
    constructor(h: number, m: number) {}
}

// 使用接口
function demonstrateInterfaces(): void {
    // 1. 基本接口使用
    const person: Person = {
        name: "Alice",
        age: 30,
        isStudent: false
    };
    console.log("Person:", person);

    // 2. 可选属性
    const car: Car = {
        make: "Toyota",
        model: "Corolla"
        // year和color是可选的，可以不提供
    };
    console.log("Car:", car);

    // 3. 只读属性
    const point: Point = { x: 10, y: 20 };
    console.log("Point:", point);
    // point.x = 30; // 错误，x是只读属性

    // 4. 函数类型接口
    let mySearch: SearchFunc = function(source: string, subString: string): boolean {
        return source.search(subString) > -1;
    };
    console.log('Search result:', mySearch("Hello, World", "World"));

    // 5. 可索引类型
    let myArray: StringArray = ["Bob", "Alice", "Eve"];
    console.log("Array:", myArray);
    console.log("Element at index 1:", myArray[1]);

    // 6. 实现接口的类
    const clock = new Clock(10, 30);
    clock.setTime(new Date());
    console.log("Clock time:", clock.currentTime);

    // 7. 继承接口
    const square: Square = {
        color: "blue",
        sideLength: 10
    };
    console.log("Square:", square);

    // 8. 混合类型接口
    function getCounter(): Counter {
        let counter = (function(start: number) {
            return start.toString();
        }) as Counter;
        
        counter.interval = 123;
        counter.reset = function() {
            console.log("Counter reset");
        };
        
        return counter;
    }
    
    let c = getCounter();
    console.log("Counter function result:", c(10));
    console.log("Counter interval:", c.interval);
    c.reset();
}

// 调用函数
demonstrateInterfaces();