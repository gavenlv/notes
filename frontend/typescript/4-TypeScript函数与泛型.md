# 4. TypeScript函数与泛型

## 4.1 函数概述

函数是JavaScript中的一等公民，TypeScript在此基础上添加了类型注解、重载等特性，使函数更加强大和安全。

### 4.1.1 函数声明

在TypeScript中，可以声明函数的类型，包括参数类型和返回值类型：

```typescript
// 函数声明
function add(x: number, y: number): number {
    return x + y;
}

// 函数表达式
const subtract = function(x: number, y: number): number {
    return x - y;
};

// 箭头函数
const multiply = (x: number, y: number): number => {
    return x * y;
};

// 简化的箭头函数
const divide = (x: number, y: number): number => x / y;
```

### 4.1.2 完整的函数类型

一个完整的函数类型包括参数类型和返回值类型：

```typescript
// 完整的函数类型
let myAdd: (x: number, y: number) => number = function(x: number, y: number): number { 
    return x + y; 
};

// 使用类型别名
type MathOperation = (x: number, y: number) => number;
let myOperation: MathOperation = (x, y) => x * y;

// 接口定义函数类型
interface MathFunction {
    (x: number, y: number): number;
}

let myMathFunction: MathFunction = (x, y) => x - y;
```

## 4.2 函数参数

### 4.2.1 参数类型注解

函数参数可以有类型注解，确保传入的参数类型正确：

```typescript
function greet(name: string, age: number): string {
    return `Hello, ${name}! You are ${age} years old.`;
}

greet("Alice", 30); // 正确
// greet("Alice", "thirty"); // 错误：参数类型不匹配
```

### 4.2.2 可选参数

在参数名后面使用`?`标记参数为可选：

```typescript
function buildName(firstName: string, lastName?: string): string {
    if (lastName) {
        return `${firstName} ${lastName}`;
    } else {
        return firstName;
    }
}

console.log(buildName("John", "Doe")); // "John Doe"
console.log(buildName("John")); // "John"
```

**注意**：可选参数必须跟在必需参数后面。

### 4.2.3 默认参数

可以为参数提供默认值：

```typescript
function greet(name: string, greeting: string = "Hello"): string {
    return `${greeting}, ${name}!`;
}

console.log(greet("Alice")); // "Hello, Alice!"
console.log(greet("Alice", "Hi")); // "Hi, Alice!"

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
```

### 4.2.4 剩余参数

使用`...`操作符收集多个参数到一个数组中：

```typescript
function sum(...numbers: number[]): number {
    return numbers.reduce((total, current) => total + current, 0);
}

console.log(sum(1, 2, 3, 4, 5)); // 15
console.log(sum(10, 20)); // 30

// 混合普通参数和剩余参数
function greetPeople(greeting: string, ...names: string[]): string {
    return `${greeting}, ${names.join(", ")}!`;
}

console.log(greetPeople("Hello", "Alice", "Bob", "Charlie")); // "Hello, Alice, Bob, Charlie!"
```

## 4.3 函数返回值

### 4.3.1 返回值类型注解

函数返回值可以有类型注解：

```typescript
function add(x: number, y: number): number {
    return x + y;
}

function getRandomNumber(): number {
    return Math.floor(Math.random() * 100);
}

function getGreeting(name: string): string {
    return `Hello, ${name}!`;
}

function isEven(num: number): boolean {
    return num % 2 === 0;
}

function log(message: string): void {
    console.log(message);
    // 没有返回语句，返回undefined
}
```

### 4.3.2 返回值类型推断

如果函数有明确的返回语句，TypeScript可以推断出返回值类型：

```typescript
function add(x: number, y: number) { // 推断返回类型为number
    return x + y;
}

function greet(name: string) { // 推断返回类型为string
    return `Hello, ${name}!`;
}

// 如果函数有多个返回路径，TypeScript会推断出联合类型
function processValue(value: number) { // 推断返回类型为number | string
    if (value > 0) {
        return value * 2; // 返回number
    } else {
        return "Value is not positive"; // 返回string
    }
}
```

### 4.3.3 never返回类型

`never`类型表示函数永不返回：

```typescript
function error(message: string): never {
    throw new Error(message);
}

function infiniteLoop(): never {
    while (true) {}
}
```

## 4.4 函数重载

函数重载允许一个函数接受不同数量或类型的参数，做出不同的处理：

```typescript
// 函数重载声明
function padLeft(value: string, padding: string): string;
function padLeft(value: string, padding: number): string;

// 函数实现
function padLeft(value: string, padding: string | number): string {
    if (typeof padding === "number") {
        return Array(padding + 1).join(" ") + value;
    }
    if (typeof padding === "string") {
        return padding + value;
    }
    throw new Error(`Expected string or number, got '${typeof padding}'.`);
}

console.log(padLeft("Hello", 4)); // "    Hello"
console.log(padLeft("Hello", ">>>")); // ">>>Hello"

// 更复杂的重载示例
function createElement(tag: string): Element;
function createElement(tag: "a", href: string): HTMLAnchorElement;
function createElement(tag: "img", src: string): HTMLImageElement;
function createElement(tag: "input", type: string, name: string): HTMLInputElement;

function createElement(tag: string, ...args: any[]): Element {
    if (tag === "a" && args.length === 1) {
        const element = document.createElement("a") as HTMLAnchorElement;
        element.href = args[0];
        return element;
    }
    
    if (tag === "img" && args.length === 1) {
        const element = document.createElement("img") as HTMLImageElement;
        element.src = args[0];
        return element;
    }
    
    if (tag === "input" && args.length === 2) {
        const element = document.createElement("input") as HTMLInputElement;
        element.type = args[0];
        element.name = args[1];
        return element;
    }
    
    return document.createElement(tag);
}

const link = createElement("a", "https://example.com");
const image = createElement("img", "/path/to/image.jpg");
const input = createElement("input", "text", "username");
```

## 4.5 泛型（Generics）概述

泛型是TypeScript的核心特性之一，允许我们编写可重用的组件，这些组件可以支持多种数据类型。

### 4.5.1 为什么需要泛型

```typescript
// 不使用泛型，函数只能处理特定类型
function identity(arg: number): number {
    return arg;
}

// 使用泛型，函数可以处理任何类型
function identity<T>(arg: T): T {
    return arg;
}

let output1 = identity<string>("myString"); // 类型是string
let output2 = identity<number>(123);        // 类型是number

// 类型推断，不需要显式指定类型
let output3 = identity("myString");        // 推断类型为string
let output4 = identity(123);               // 推断类型为number
```

### 4.5.2 泛型函数

```typescript
// 泛型函数
function reverse<T>(array: T[]): T[] {
    return array.slice().reverse();
}

console.log(reverse([1, 2, 3, 4, 5])); // [5, 4, 3, 2, 1]
console.log(reverse(["a", "b", "c"]));   // ["c", "b", "a"]

// 多个泛型参数
function pair<T, U>(first: T, second: U): [T, U] {
    return [first, second];
}

let pair1 = pair(1, "one");     // [number, string]
let pair2 = pair("a", 2);       // [string, number]
let pair3 = pair(true, false);  // [boolean, boolean]
```

## 4.6 泛型接口

接口也可以使用泛型：

```typescript
// 泛型接口
interface Box<T> {
    value: T;
    getValue(): T;
    setValue(value: T): void;
}

class NumberBox implements Box<number> {
    constructor(private _value: number) {}
    
    get value(): number {
        return this._value;
    }
    
    getValue(): number {
        return this._value;
    }
    
    setValue(value: number): void {
        this._value = value;
    }
}

const numberBox = new NumberBox(42);
console.log(numberBox.getValue()); // 42

class StringBox implements Box<string> {
    constructor(private _value: string) {}
    
    get value(): string {
        return this._value;
    }
    
    getValue(): string {
        return this._value;
    }
    
    setValue(value: string): void {
        this._value = value;
    }
}

const stringBox = new StringBox("Hello");
console.log(stringBox.getValue()); // "Hello"

// 泛型接口用于函数
interface Comparator<T> {
    (a: T, b: T): number;
}

const numberComparator: Comparator<number> = (a, b) => a - b;
const stringComparator: Comparator<string> = (a, b) => a.localeCompare(b);

console.log(numberComparator(5, 3));  // 2 (5 > 3)
console.log(stringComparator("apple", "banana")); // -1 ("apple" < "banana")
```

## 4.7 泛型类

类也可以使用泛型：

```typescript
// 泛型类
class GenericStorage<T> {
    private items: T[] = [];
    
    addItem(item: T): void {
        this.items.push(item);
    }
    
    getItem(index: number): T {
        return this.items[index];
    }
    
    getAllItems(): T[] {
        return [...this.items];
    }
    
    removeItem(index: number): void {
        if (index >= 0 && index < this.items.length) {
            this.items.splice(index, 1);
        }
    }
}

// 字符串存储
const stringStorage = new GenericStorage<string>();
stringStorage.addItem("hello");
stringStorage.addItem("world");
console.log(stringStorage.getAllItems()); // ["hello", "world"]

// 数字存储
const numberStorage = new GenericStorage<number>();
numberStorage.addItem(1);
numberStorage.addItem(2);
numberStorage.addItem(3);
console.log(numberStorage.getAllItems()); // [1, 2, 3]

// 泛型约束
interface Lengthwise {
    length: number;
}

class Collection<T extends Lengthwise> {
    private items: T[] = [];
    
    addItem(item: T): void {
        this.items.push(item);
    }
    
    getTotalLength(): number {
        return this.items.reduce((total, item) => total + item.length, 0);
    }
}

const stringCollection = new Collection<string>();
stringCollection.addItem("hello");
stringCollection.addItem("world");
console.log(stringCollection.getTotalLength()); // 10

// 数组集合
const arrayCollection = new Collection<string[]>();
arrayCollection.addItem(["a", "b"]);
arrayCollection.addItem(["c", "d", "e"]);
console.log(arrayCollection.getTotalLength()); // 5 (2 + 3)
```

## 4.8 泛型约束

泛型约束可以限制泛型类型的范围：

### 4.8.1 基本约束

```typescript
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

// 约束属性
interface Person {
    name: string;
    age: number;
}

function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

const person = { name: "Alice", age: 30 };
console.log(getProperty(person, "name")); // "Alice"
console.log(getProperty(person, "age"));  // 30
// getProperty(person, "salary"); // 错误：'salary'不是Person的键
```

### 4.8.2 类类型约束

```typescript
// 类类型约束
function create<T>(c: { new(): T }): T {
    return new c();
}

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

// 创建Lion实例
const lion = create(Lion);
console.log(lion.numLegs); // 4
console.log(lion.keeper.nametag); // "Mikle"

// 创建Bee实例
const bee = create(Bee);
console.log(bee.numLegs); // 4
console.log(bee.keeper.hasMask); // true
```

## 4.9 高级泛型特性

### 4.9.1 条件类型

条件类型表示根据条件选择不同的类型：

```typescript
// 基本条件类型
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 使用条件类型创建类型安全的函数
function process<T>(value: T): T extends string ? string : number {
    if (typeof value === "string") {
        return value.toUpperCase() as any;
    }
    return value as any;
}

const result1 = process("hello"); // string
const result2 = process(42);      // number

// 条件类型与泛型约束结合
type NonNullable<T> = T extends null | undefined ? never : T;

function filterNullable<T>(value: T): NonNullable<T> {
    return value as NonNullable<T>;
}

const filtered1 = filterNullable("hello"); // string
const filtered2 = filterNullable(null);    // never
const filtered3 = filterNullable(undefined); // never
```

### 4.9.2 映射类型

映射类型基于旧类型创建新类型：

```typescript
// 基本映射类型
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
}

type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;

// 创建修改后的接口
type ModifiedUser = {
    readonly id: number;
    name?: string;
    email: string;
};

// 等价于：
type ModifiedUserEquivalent = {
    readonly [P in "id"]: User[P];
} & {
    [P in "name"]?: User[P];
} & {
    [P in "email"]: User[P];
};

// 自定义映射类型
type Stringify<T> = {
    [K in keyof T]: string;
};

type StringifiedUser = Stringify<User>;
// 等价于：
// {
//     id: string;
//     name: string;
//     email: string;
// }
```

### 4.9.3 高级类型推断

```typescript
// 使用infer关键字进行类型推断
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

function greet(name: string): string {
    return `Hello, ${name}`;
}

type GreetReturnType = ReturnType<typeof greet>; // string

// 提取函数参数类型
type Parameters<T> = T extends (...args: infer P) => any ? P : never;

type GreetParameters = Parameters<typeof greet>; // [string]

// 提取数组元素类型
type ElementOf<T> = T extends (infer U)[] ? U : never;

type StringArrayElement = ElementOf<string[]>; // string

// 提取Promise的值类型
type UnpackPromise<T> = T extends Promise<infer U> ? U : never;

type PromiseValue = UnpackPromise<Promise<string>>; // string

// 条件类型中的递归
type DeepPartial<T> = {
    [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

interface TreeNode {
    value: string;
    left?: TreeNode;
    right?: TreeNode;
}

type PartialTreeNode = DeepPartial<TreeNode>;
// {
//     value?: string;
//     left?: {
//         value?: string;
//         left?: TreeNode;
//         right?: TreeNode;
//     };
//     right?: {
//         value?: string;
//         left?: TreeNode;
//         right?: TreeNode;
//     };
// }
```

## 4.10 函数与泛型的最佳实践

### 4.10.1 选择何时使用泛型

1. **当函数需要处理多种类型但逻辑相同时**：使用泛型
2. **当类型之间的关系很重要时**：使用泛型约束
3. **当函数逻辑依赖于类型特性时**：使用泛型

```typescript
// 好的泛型使用
function map<T, U>(array: T[], transform: (item: T) => U): U[] {
    return array.map(transform);
}

const numbers = [1, 2, 3, 4, 5];
const strings = map(numbers, num => num.toString()); // string[]
const doubled = map(numbers, num => num * 2);       // number[]

// 不必要的泛型使用
// 这个函数只处理数字，不需要泛型
function add<T extends number>(a: T, b: T): T {
    return (a + b) as T;
}

// 更好的实现
function addNumbers(a: number, b: number): number {
    return a + b;
}
```

### 4.10.2 泛型命名约定

1. **T**：表示类型参数
2. **K, V**：表示键值对
3. **E**：表示元素
4. **R**：表示返回值

```typescript
// 好的命名约定
interface Dictionary<K, V> {
    get(key: K): V | undefined;
    set(key: K, value: V): void;
    has(key: K): boolean;
}

function filter<T>(array: T[], predicate: (item: T) => boolean): T[] {
    return array.filter(predicate);
}

function pipe<T, U, V>(
    value: T,
    fn1: (x: T) => U,
    fn2: (x: U) => V
): V {
    return fn2(fn1(value));
}
```

### 4.10.3 避免过度使用泛型

```typescript
// 过度使用泛型
function processData<T, U, V, W>(data: T, processor: (x: T) => U, transformer: (x: U) => V, formatter: (x: V) => W): W {
    return formatter(transformer(processor(data)));
}

// 更简洁的实现
function processData<T, R>(data: T, processors: Array<(x: any) => any>): R {
    return processors.reduce((acc, processor) => processor(acc), data) as R;
}

// 甚至更好的实现 - 分离关注点
function process<T, U>(data: T, processor: (x: T) => U): U {
    return processor(data);
}

function pipe<T, U>(value: T, fn1: (x: T) => U): U;
function pipe<T, U, V>(value: T, fn1: (x: T) => U, fn2: (x: U) => V): V;
function pipe<T, U, V, W>(value: T, fn1: (x: T) => U, fn2: (x: U) => V, fn3: (x: V) => W): W;
function pipe<T>(value: T, ...fns: Array<(x: any) => any>): any {
    return fns.reduce((acc, fn) => fn(acc), value);
}
```

## 4.11 实例：构建类型安全的数据处理管道

让我们通过一个实际例子来应用函数和泛型的知识：

```typescript
// 定义管道操作的基本类型
type PipeOperation<T, R> = (input: T) => R;

// 基本管道操作函数
class Pipeline<T> {
    constructor(private value: T) {}
    
    pipe<U>(operation: PipeOperation<T, U>): Pipeline<U> {
        return new Pipeline(operation(this.value));
    }
    
    getResult(): T {
        return this.value;
    }
}

// 常用管道操作
const operations = {
    // 数据过滤
    filter: <T>(predicate: (item: T) => boolean) => 
        (data: T[]): T[] => data.filter(predicate),
    
    // 数据映射
    map: <T, U>(transform: (item: T) => U) => 
        (data: T[]): U[] => data.map(transform),
    
    // 数据扁平化
    flat: <T>(data: T[][]): T[] => data.flat(),
    
    // 数据排序
    sort: <T>(compareFn?: (a: T, b: T) => number) => 
        (data: T[]): T[] => [...data].sort(compareFn),
    
    // 数据分组
    groupBy: <T, K extends keyof T>(key: K) => 
        (data: T[]): Record<string, T[]> => 
            data.reduce((groups, item) => {
                const groupKey = String(item[key]);
                if (!groups[groupKey]) groups[groupKey] = [];
                groups[groupKey].push(item);
                return groups;
            }, {} as Record<string, T[]>),
    
    // 数据聚合
    reduce: <T, U>(reducer: (acc: U, item: T) => U, initialValue: U) => 
        (data: T[]): U => data.reduce(reducer, initialValue),
    
    // 数据统计
    count: <T>(data: T[]): number => data.length,
    
    // 数据求和
    sum: (data: number[]): number => data.reduce((sum, num) => sum + num, 0),
    
    // 取平均值
    average: (data: number[]): number => {
        if (data.length === 0) return 0;
        return data.reduce((sum, num) => sum + num, 0) / data.length;
    },
    
    // 获取最大值
    max: <T>(data: T[]): T | undefined => {
        if (data.length === 0) return undefined;
        return data.reduce((max, item) => (item > max ? item : max), data[0]);
    },
    
    // 获取最小值
    min: <T>(data: T[]): T | undefined => {
        if (data.length === 0) return undefined;
        return data.reduce((min, item) => (item < min ? item : min), data[0]);
    }
};

// 数据类型定义
interface Product {
    id: number;
    name: string;
    price: number;
    category: string;
    inStock: boolean;
}

interface SalesData {
    productId: number;
    quantity: number;
    date: Date;
    amount: number;
}

// 使用示例
function demonstrateDataPipeline(): void {
    // 示例数据
    const products: Product[] = [
        { id: 1, name: "Laptop", price: 999, category: "Electronics", inStock: true },
        { id: 2, name: "Smartphone", price: 699, category: "Electronics", inStock: true },
        { id: 3, name: "Headphones", price: 99, category: "Electronics", inStock: false },
        { id: 4, name: "Book", price: 19, category: "Books", inStock: true },
        { id: 5, name: "Shirt", price: 29, category: "Clothing", inStock: true },
        { id: 6, name: "Jeans", price: 49, category: "Clothing", inStock: false }
    ];
    
    const salesData: SalesData[] = [
        { productId: 1, quantity: 2, date: new Date("2023-01-15"), amount: 1998 },
        { productId: 2, quantity: 3, date: new Date("2023-01-16"), amount: 2097 },
        { productId: 4, quantity: 5, date: new Date("2023-01-17"), amount: 95 },
        { productId: 5, quantity: 10, date: new Date("2023-01-18"), amount: 290 },
        { productId: 1, quantity: 1, date: new Date("2023-01-19"), amount: 999 }
    ];
    
    // 使用管道处理产品数据
    const expensiveProducts = new Pipeline(products)
        .pipe(operations.filter(p => p.price > 50))
        .pipe(operations.sort((a, b) => b.price - a.price))
        .pipe(operations.map(p => `${p.name}: $${p.price}`))
        .getResult();
    
    console.log("Expensive products:", expensiveProducts);
    
    // 使用管道统计各分类的产品数量
    const productsByCategory = new Pipeline(products)
        .pipe(operations.groupBy("category"))
        .pipe(operations.map((groups, key) => ({
            category: key,
            count: groups.length
        })))
        .pipe(operations.sort((a, b) => b.count - a.count))
        .getResult();
    
    console.log("Products by category:", productsByCategory);
    
    // 使用管道计算销售数据统计
    const salesStats = new Pipeline(salesData)
        .pipe(operations.map(s => s.amount))
        .pipe(data => ({
            total: operations.sum(data),
            average: operations.average(data),
            max: operations.max(data),
            min: operations.min(data),
            count: operations.count(data)
        }))
        .getResult();
    
    console.log("Sales statistics:", salesStats);
    
    // 组合多个管道操作
    const highValueSales = new Pipeline(salesData)
        .pipe(operations.filter(s => s.amount > 1000))
        .pipe(operations.map(s => ({
            productId: s.productId,
            amount: s.amount,
            date: s.date.toISOString().split('T')[0]
        })))
        .pipe(operations.sort((a, b) => b.amount - a.amount))
        .getResult();
    
    console.log("High value sales:", highValueSales);
}

// 扩展管道支持异步操作
class AsyncPipeline<T> {
    constructor(private value: T) {}
    
    async pipe<U>(operation: PipeOperation<T, U>): Promise<AsyncPipeline<U>> {
        const result = await operation(this.value);
        return new AsyncPipeline(result);
    }
    
    async getResult(): Promise<T> {
        return this.value;
    }
}

// 异步操作
const asyncOperations = {
    // 异步获取数据
    fetch: async <T>(url: string): Promise<T[]> => {
        // 模拟API调用
        return new Promise(resolve => {
            setTimeout(() => {
                resolve([] as T[]); // 空数组作为示例
            }, 1000);
        });
    },
    
    // 异步过滤
    filter: <T>(predicate: (item: T) => Promise<boolean>) => 
        async (data: T[]): Promise<T[]> => {
            const results = await Promise.all(data.map(async item => ({
                item,
                shouldKeep: await predicate(item)
            })));
            
            return results
                .filter(result => result.shouldKeep)
                .map(result => result.item);
        }
};

// 使用异步管道
async function demonstrateAsyncPipeline(): Promise<void> {
    const products: Product[] = [
        { id: 1, name: "Laptop", price: 999, category: "Electronics", inStock: true },
        { id: 2, name: "Smartphone", price: 699, category: "Electronics", inStock: true },
        { id: 3, name: "Headphones", price: 99, category: "Electronics", inStock: false },
        { id: 4, name: "Book", price: 19, category: "Books", inStock: true },
        { id: 5, name: "Shirt", price: 29, category: "Clothing", inStock: true },
        { id: 6, name: "Jeans", price: 49, category: "Clothing", inStock: false }
    ];
    
    // 使用异步管道处理数据
    const result = await new AsyncPipeline(products)
        .pipe(asyncOperations.filter(async product => {
            // 模拟异步验证库存状态
            await new Promise(resolve => setTimeout(resolve, 100));
            return product.inStock && product.price > 50;
        }))
        .pipe(operations.map(p => p.name))
        .pipe(operations.sort())
        .getResult();
    
    console.log("Available expensive products (async):", result);
}

// 调用演示函数
demonstrateDataPipeline();
demonstrateAsyncPipeline();
```

## 4.12 总结

在这一章中，我们深入学习了TypeScript的函数和泛型：

- 理解了函数的类型注解、参数类型和返回值类型
- 掌握了函数重载、可选参数和默认参数的使用
- 学会了泛型的基本概念和语法
- 探索了泛型接口、泛型类和泛型约束
- 了解了高级泛型特性如条件类型和映射类型
- 构建了一个类型安全的数据处理管道

函数和泛型是TypeScript的核心特性，它们使代码更加灵活、可重用和类型安全。掌握这些特性将帮助您编写更加健壮和可维护的代码。

## 4.13 练习

1. 创建一个类型安全的事件系统，支持事件发布和订阅
2. 实现一个泛型的缓存类，支持不同的键值类型
3. 构建一个类型安全的表单处理系统，使用泛型处理不同类型的表单数据
4. 创建一个类型安全的API客户端，使用泛型处理不同的响应类型

通过完成这些练习，您将加深对TypeScript函数和泛型的理解，并能够将其应用到实际项目中。