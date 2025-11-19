// 泛型基础示例
function demonstrateGenericsBasics(): void {
    console.log("\n=== Generics Basics Demo ===");
    
    // 基本泛型函数
    function identity<T>(arg: T): T {
        return arg;
    }
    
    let output1 = identity<string>("myString");
    let output2 = identity<number>(123);
    
    console.log(`identity<string>("myString"): ${output1}`);
    console.log(`identity<number>(123): ${output2}`);
    
    // 类型推断，不需要显式指定类型
    let output3 = identity("myString");
    let output4 = identity(123);
    
    console.log(`identity("myString") (inferred): ${output3}`);
    console.log(`identity(123) (inferred): ${output4}`);
    
    // 多个泛型参数
    function pair<T, U>(first: T, second: U): [T, U] {
        return [first, second];
    }
    
    let pair1 = pair(1, "one");
    let pair2 = pair("a", 2);
    let pair3 = pair(true, false);
    
    console.log(`pair(1, "one"): ${pair1}`);
    console.log(`pair("a", 2): ${pair2}`);
    console.log(`pair(true, false): ${pair3}`);
    
    // 泛型函数示例：reverse数组
    function reverse<T>(array: T[]): T[] {
        return array.slice().reverse();
    }
    
    console.log(`reverse([1, 2, 3, 4, 5]): ${reverse([1, 2, 3, 4, 5])}`);
    console.log(`reverse(["a", "b", "c"]): ${reverse(["a", "b", "c"])}`);
    
    // 泛型函数示例：查找数组中的元素
    function findFirst<T>(array: T[], predicate: (item: T) => boolean): T | undefined {
        for (const item of array) {
            if (predicate(item)) {
                return item;
            }
        }
        return undefined;
    }
    
    const numbers = [1, 2, 3, 4, 5];
    const strings = ["apple", "banana", "cherry"];
    
    const foundNumber = findFirst(numbers, n => n > 3);
    const foundString = findFirst(strings, s => s.startsWith("b"));
    
    console.log(`findFirst(numbers, n => n > 3): ${foundNumber}`);
    console.log(`findFirst(strings, s => s.startsWith("b")): ${foundString}`);
    
    // 泛型函数示例：合并两个对象
    function merge<T, U>(obj1: T, obj2: U): T & U {
        return { ...obj1, ...obj2 };
    }
    
    const person = { name: "Alice", age: 30 };
    const employee = { employeeId: "EMP123", department: "Engineering" };
    
    const personEmployee = merge(person, employee);
    console.log("Merged object:", personEmployee);
    
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
    console.log(`String container value: ${stringContainer.getValue()}`);
    
    stringContainer.setValue("World");
    console.log(`Updated string container value: ${stringContainer.getValue()}`);
    
    const numberContainer = createContainer(42);
    console.log(`Number container value: ${numberContainer.getValue()}`);
    
    numberContainer.setValue(100);
    console.log(`Updated number container value: ${numberContainer.getValue()}`);
    
    // 泛型接口
    interface Response<T> {
        data: T;
        status: number;
        message: string;
    }
    
    function createResponse<T>(data: T, status: number = 200, message: string = "Success"): Response<T> {
        return { data, status, message };
    }
    
    const userResponse = createResponse({ id: 1, name: "Alice" });
    const errorResponse = createResponse(null, 404, "Not Found");
    
    console.log("User response:", userResponse);
    console.log("Error response:", errorResponse);
    
    // 泛型类
    class Collection<T> {
        private items: T[] = [];
        
        add(item: T): void {
            this.items.push(item);
        }
        
        remove(index: number): T | undefined {
            if (index >= 0 && index < this.items.length) {
                return this.items.splice(index, 1)[0];
            }
            return undefined;
        }
        
        find(predicate: (item: T) => boolean): T | undefined {
            return this.items.find(predicate);
        }
        
        getAll(): T[] {
            return [...this.items];
        }
        
        count(): number {
            return this.items.length;
        }
    }
    
    const stringCollection = new Collection<string>();
    stringCollection.add("hello");
    stringCollection.add("world");
    stringCollection.add("typescript");
    
    console.log("String collection:", stringCollection.getAll());
    console.log(`Collection count: ${stringCollection.count()}`);
    
    const foundString = stringCollection.find(s => s.startsWith("t"));
    console.log(`Found string: ${foundString}`);
    
    stringCollection.remove(1);
    console.log("Collection after removal:", stringCollection.getAll());
    
    // 泛型约束示例将在下一节详细介绍
    console.log("Generics basics demo completed!");
}

demonstrateGenericsBasics();