// 类型兼容性示例
function demonstrateTypeCompatibility(): void {
    console.log("\n=== Type Compatibility Demo ===");
    
    // 基本兼容性
    interface Named {
        name: string;
    }
    
    let person: Named = { name: "Alice" }; // 兼容
    // let x: Named = { name: "Alice", age: 30 }; // 在严格模式下，多余属性会报错
    
    // 结构化类型
    interface Person {
        name: string;
        age: number;
    }
    
    interface Employee {
        name: string;
        age: number;
        jobTitle: string;
    }
    
    // Employee兼容Person，因为它至少有Person的所有属性
    let employee: Employee = {
        name: "Bob",
        age: 30,
        jobTitle: "Developer"
    };
    
    let person: Person = employee; // 兼容
    console.log("Person assigned from Employee:", person);
    
    // 函数兼容性
    let fn1 = (x: number) => x + x;
    let fn2: (x: number) => number = fn1; // 兼容
    
    // 函数参数双向协变
    interface Event {
        timestamp: number;
    }
    
    interface MouseEvent extends Event {
        x: number;
        y: number;
    }
    
    let mouseEventHandler = (event: MouseEvent) => {
        console.log(`Mouse clicked at (${event.x}, ${event.y})`);
    };
    
    let eventHandler: (event: Event) => void = mouseEventHandler; // 兼容，参数类型更具体
    
    // 反过来也兼容
    let genericHandler = (event: Event) => {
        console.log(`Event at ${event.timestamp}`);
    };
    
    let mouseEventHandler2: (event: MouseEvent) => void = genericHandler; // 也兼容
    
    // 枚举兼容性
    enum Status {
        Pending,
        Approved,
        Rejected
    }
    
    enum HttpStatus {
        Ok = 200,
        NotFound = 404,
        ServerError = 500
    }
    
    let status = Status.Approved;
    let httpStatus = HttpStatus.Ok;
    
    // 枚举与数字兼容
    let numericValue: number = status; // 可以将枚举赋值给数字
    status = httpStatus; // 可以将数字赋值给枚举
    
    console.log(`Status values: ${status}, ${numericValue}`);
    
    // 类兼容性
    class Animal {
        feet: number;
        constructor(name: string, numFeet: number) {
            // ...
        }
    }
    
    class Size {
        feet: number;
        constructor(numFeet: number) {
            // ...
        }
    }
    
    let a: Animal;
    let s: Size;
    
    a = s; // OK，因为它们都有相同类型的feet属性
    s = a; // OK
    
    // 泛型兼容性
    interface Empty<T> {}
    let x: Empty<number>;
    let y: Empty<string>;
    
    x = y; // OK，因为Empty没有使用T
    
    interface NotEmpty<T> {
        data: T;
    }
    
    let notEmptyX: NotEmpty<number>;
    let notEmptyY: NotEmpty<string>;
    
    // notEmptyX = notEmptyY; // 错误，类型不兼容
    
    // 子类型与超类型
    interface Parent {
        name: string;
    }
    
    interface Child extends Parent {
        age: number;
    }
    
    function processParent(parent: Parent): void {
        console.log(`Processing parent: ${parent.name}`);
    }
    
    const child: Child = {
        name: "Alice",
        age: 10
    };
    
    processParent(child); // 子类型可以赋值给超类型
    
    // 逆变与协变
    type EventCallback<T> = (event: T) => void;
    
    type BaseEvent = {
        type: string;
    };
    
    type ClickEvent = BaseEvent & {
        x: number;
        y: number;
    };
    
    let baseEventHandler: EventCallback<BaseEvent> = (event) => {
        console.log(`Base event: ${event.type}`);
    };
    
    let clickEventHandler: EventCallback<ClickEvent> = (event) => {
        console.log(`Click at (${event.x}, ${event.y})`);
    };
    
    // 函数参数类型是逆变的
    // 可以将处理更广泛事件的函数赋给处理更具体事件的函数
    clickEventHandler = baseEventHandler; // OK
    
    // 但不能反过来
    // baseEventHandler = clickEventHandler; // 错误
    
    // 示例使用
    console.log("Demonstrating function parameter contravariance:");
    clickEventHandler({ type: "click", x: 10, y: 20 }); // 使用baseEventHandler处理click事件
}

demonstrateTypeCompatibility();