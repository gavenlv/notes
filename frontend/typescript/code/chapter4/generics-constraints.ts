// 泛型约束示例
function demonstrateGenericsConstraints(): void {
    console.log("\n=== Generics Constraints Demo ===");
    
    // 基本约束：T必须具有length属性
    interface Lengthwise {
        length: number;
    }
    
    function logLength<T extends Lengthwise>(arg: T): void {
        console.log(arg.length);
    }
    
    logLength("hello"); // 5
    logLength([1, 2, 3, 4, 5]); // 5
    // logLength(123); // 错误：数字没有length属性
    
    // 约束属性：使用keyof操作符
    function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
        return obj[key];
    }
    
    const person = { name: "Alice", age: 30, email: "alice@example.com" };
    console.log(`getProperty(person, "name"): ${getProperty(person, "name")}`); // "Alice"
    console.log(`getProperty(person, "age"): ${getProperty(person, "age")}`); // 30
    // getProperty(person, "salary"); // 错误：'salary'不是Person的键
    
    // 类类型约束
    class BeeKeeper {
        hasMask: boolean = true;
    }
    
    class ZooKeeper {
        nametag: string = "Mikle";
    }
    
    class Animal {
        numLegs: number = 4;
    }
    
    class Bee extends Animal {
        keeper: BeeKeeper = new BeeKeeper();
    }
    
    class Lion extends Animal {
        keeper: ZooKeeper = new ZooKeeper();
    }
    
    function createInstance<T extends Animal>(c: new() => T): T {
        return new c();
    }
    
    const lion = createInstance(Lion);
    const bee = createInstance(Bee);
    
    console.log("Lion:", lion);
    console.log("Bee:", bee);
    
    // 泛型约束与工厂函数
    interface Identifiable {
        id: string;
    }
    
    function createWithId<T extends Identifiable>(constructor: new() => T, id: string): T {
        const instance = new constructor();
        instance.id = id;
        return instance;
    }
    
    class User implements Identifiable {
        id: string = "";
        name: string = "";
    }
    
    class Product implements Identifiable {
        id: string = "";
        title: string = "";
        price: number = 0;
    }
    
    const user = createWithId(User, "user123");
    user.name = "Alice";
    
    const product = createWithId(Product, "prod456");
    product.title = "Widget";
    product.price = 19.99;
    
    console.log("User:", user);
    console.log("Product:", product);
    
    // 约束泛型参数之间的关系
    function copyFields<T extends U, U>(target: T, source: U): void {
        for (const id in source) {
            if (target.hasOwnProperty(id)) {
                target[id] = source[id];
            }
        }
    }
    
    interface Circle {
        radius: number;
    }
    
    interface ColoredCircle extends Circle {
        color: string;
    }
    
    const circle: Circle = { radius: 10 };
    const coloredCircle: ColoredCircle = { radius: 5, color: "red" };
    
    copyFields(circle, coloredCircle); // 复制radius属性
    console.log("Circle after copy:", circle);
    
    // 泛型约束与条件类型
    interface Todo {
        title: string;
        description: string;
        completed: boolean;
    }
    
    type KeysOf<T> = keyof T;
    
    type TodoKeys = KeysOf<Todo>; // "title" | "description" | "completed"
    
    type ValuesOf<T> = T[keyof T];
    
    type TodoValues = ValuesOf<Todo>; // string | boolean
    
    // 更复杂的约束示例
    interface Validatable {
        validate(): boolean;
    }
    
    function validateAll<T extends Validatable>(items: T[]): boolean {
        return items.every(item => item.validate());
    }
    
    class UserInput implements Validatable {
        constructor(private value: string, private minLength: number) {}
        
        validate(): boolean {
            return this.value.length >= this.minLength;
        }
    }
    
    class EmailInput implements Validatable {
        constructor(private value: string) {}
        
        validate(): boolean {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
        }
    }
    
    const username = new UserInput("john123", 5);
    const shortUsername = new UserInput("joe", 5);
    const email = new EmailInput("user@example.com");
    const invalidEmail = new EmailInput("invalid-email");
    
    console.log(`Username valid: ${username.validate()}`); // true
    console.log(`Short username valid: ${shortUsername.validate()}`); // false
    console.log(`Email valid: ${email.validate()}`); // true
    console.log(`Invalid email valid: ${invalidEmail.validate()}`); // false
    
    const allValidInputs: Validatable[] = [username, email];
    const someInvalidInputs: Validatable[] = [shortUsername, invalidEmail];
    
    console.log(`All valid inputs validate: ${validateAll(allValidInputs)}`); // true
    console.log(`Some invalid inputs validate: ${validateAll(someInvalidInputs)}`); // false
    
    // 高级约束：使用条件类型创建类型安全的事件系统
    interface Event {
        type: string;
        timestamp: number;
    }
    
    interface ClickEvent extends Event {
        type: "click";
        x: number;
        y: number;
    }
    
    interface KeyboardEvent extends Event {
        type: "keydown" | "keyup";
        key: string;
        code: string;
    }
    
    interface EventTypeMap {
        click: ClickEvent;
        keydown: KeyboardEvent;
        keyup: KeyboardEvent;
    }
    
    function createEventListener<T extends keyof EventTypeMap>(
        eventType: T,
        handler: (event: EventTypeMap[T]) => void
    ): void {
        console.log(`Event listener for ${eventType} created`);
        
        // 模拟事件触发
        setTimeout(() => {
            let mockEvent: Event;
            
            switch (eventType) {
                case "click":
                    mockEvent = {
                        type: "click",
                        timestamp: Date.now(),
                        x: 100,
                        y: 200
                    } as EventTypeMap[T];
                    break;
                case "keydown":
                case "keyup":
                    mockEvent = {
                        type: eventType,
                        timestamp: Date.now(),
                        key: "Enter",
                        code: "Enter"
                    } as EventTypeMap[T];
                    break;
                default:
                    return;
            }
            
            handler(mockEvent as EventTypeMap[T]);
        }, 1000);
    }
    
    createEventListener("click", (event) => {
        console.log(`Click at (${event.x}, ${event.y})`);
    });
    
    createEventListener("keydown", (event) => {
        console.log(`Key pressed: ${event.key} (${event.code})`);
    });
    
    console.log("Event listeners will be triggered in 1 second...");
}

demonstrateGenericsConstraints();