# 2. TypeScript基础类型系统

## 2.1 类型系统概述

TypeScript的核心优势在于其强大的类型系统。类型系统是一种用于对程序中的值进行分类和检查的机制，它可以在编译时捕获潜在错误，提高代码的健壮性和可维护性。

### 2.1.1 为什么需要类型系统

1. **错误预防**：在编译阶段发现潜在的类型错误，避免运行时异常
2. **代码文档**：类型注解可以作为自文档化代码，提高代码可读性
3. **IDE支持**：提供智能提示、重构和导航功能
4. **重构安全**：在进行代码重构时，类型检查可以确保修改不会引入新错误

### 2.1.2 TypeScript的类型特点

- **静态类型**：类型检查发生在编译阶段
- **类型推断**：不需要总是显式指定类型，TypeScript可以自动推断
- **结构化类型**：基于结构的类型兼容性，而非名义上的类型兼容性
- **渐进式**：可以逐步为JavaScript代码添加类型

## 2.2 基本类型

TypeScript继承了JavaScript的所有基本类型，并添加了额外的类型检查。

### 2.2.1 布尔值（boolean）

布尔值是最基本的数据类型，只有两个值：`true`和`false`。

```typescript
let isDone: boolean = false;
let isEnabled: boolean = true;

// 条件语句中的使用
if (isDone) {
    console.log("Task completed!");
}
```

### 2.2.2 数字（number）

TypeScript中的数字类型都是浮点数，支持十进制、十六进制、八进制和二进制字面量。

```typescript
let decimal: number = 6;        // 十进制
let hex: number = 0xf00d;        // 十六进制
let binary: number = 0b1010;    // 二进制
let octal: number = 0o744;      // 八进制
let float: number = 3.14;       // 浮点数
```

### 2.2.3 字符串（string）

可以使用双引号、单引号或反引号定义字符串。

```typescript
let name: string = "Alice";
let greeting: string = 'Hello, World!';

// 模板字符串
let message: string = `Hello, ${name}! Today is ${new Date().toLocaleDateString()}.`;
```

### 2.2.4 数组（Array）

数组有两种定义方式：

```typescript
// 方式一：在元素类型后面接上[]
let list1: number[] = [1, 2, 3];

// 方式二：使用数组泛型
let list2: Array<number> = [1, 2, 3];

// 混合类型数组
let mixed: (string | number)[] = [1, "two", 3, "four"];
```

### 2.2.5 元组（Tuple）

元组类型允许表示一个已知元素数量和类型的数组，各元素的类型不必相同。

```typescript
// 定义一个元组类型
let person: [string, number] = ["Alice", 30];

// 访问元素
console.log(person[0]); // "Alice"
console.log(person[1]); // 30

// 越界访问会报错
// console.log(person[2]); // 错误：长度为"2"的类型不存在索引"2"

// 可以添加额外元素，但类型必须符合联合类型
person.push(25); // 可以，number是string | number的一部分
// person.push(true); // 错误：boolean不是string | number的一部分
```

## 2.3 特殊类型

TypeScript提供了一些特殊类型用于更精确的类型控制。

### 2.3.1 枚举（enum）

枚举类型是对JavaScript标准数据类型的一个补充，它用于定义数值集合。

```typescript
// 数字枚举
enum Color {
    Red,    // 默认值为0
    Green,  // 默认值为1
    Blue    // 默认值为2
}

let c: Color = Color.Green;
console.log(c); // 1

// 字符串枚举
enum Direction {
    Up = "UP",
    Down = "DOWN",
    Left = "LEFT",
    Right = "RIGHT"
}

// 常量枚举
const enum Enum {
    A = 1,
    B = 2 * Enum.A
}
```

### 2.3.2 any类型

`any`类型用于表示任意类型，可以绕过类型检查。

```typescript
let notSure: any = 4;
notSure = "maybe a string";
notSure = false; // 完全合法

// any类型的数组
let list: any[] = [1, true, "free"];
list[1] = 100;
```

**最佳实践**：尽量避免使用`any`类型，它会使类型检查失去意义。如果需要更灵活的类型，可以考虑使用`unknown`类型。

### 2.3.3 unknown类型

`unknown`类型是TypeScript 3.0引入的新类型，它是`any`类型的安全替代品。

```typescript
let value: unknown = 42;

// 错误：无法调用unknown类型的方法
// value.toFixed(2); // 错误

// 需要类型检查后才能使用
if (typeof value === "number") {
    // 在这个代码块中，TypeScript知道value是number类型
    console.log(value.toFixed(2)); // 正确
}

// 类型断言
let valueAsString: string = (value as unknown) as string;
```

### 2.3.4 void类型

`void`类型表示没有任何类型，通常用于函数返回值。

```typescript
function logMessage(message: string): void {
    console.log(message);
    // 不需要return语句，或者return一个空值
    // return; // 合法
    // return undefined; // 合法
}

// void类型的变量
let unusable: void = undefined;
unusable = undefined; // 合法
// unusable = null; // 严格模式下会报错
```

### 2.3.5 null和undefined

TypeScript中有两个特殊的原始类型：`null`和`undefined`。

```typescript
let u: undefined = undefined;
let n: null = null;

// 默认情况下，null和undefined是所有类型的子类型
// 可以赋值给其他类型
let num: number = undefined;
let str: string = null;

// 但在严格模式下，只有void和它们各自可以赋值
```

### 2.3.6 never类型

`never`类型表示永不存在的值的类型。

```typescript
// 返回never的函数
function error(message: string): never {
    throw new Error(message);
}

// 返回never的函数
function infiniteLoop(): never {
    while (true) {}
}

// never类型是所有类型的子类型，可以赋值给任何类型
let num: number = error("Something went wrong"); // 合法
```

### 2.3.7 object类型

`object`类型表示非原始类型。

```typescript
let obj: object = { prop: 0 };
// obj.prop; // 错误：object类型没有prop属性

// 更具体的对象类型
let person: { name: string; age: number } = {
    name: "Alice",
    age: 30
};
```

## 2.4 类型注解与类型推断

TypeScript的类型系统基于两种机制：类型注解和类型推断。

### 2.4.1 类型注解

类型注解是显式地为变量、函数参数或返回值指定类型。

```typescript
// 变量类型注解
let name: string = "Alice";
let age: number = 30;
let isActive: boolean = true;

// 函数参数和返回值类型注解
function greet(name: string): string {
    return `Hello, ${name}!`;
}

// 对象类型注解
let person: {
    name: string;
    age: number;
    greet: () => string;
} = {
    name: "Bob",
    age: 25,
    greet() {
        return `Hi, I'm ${this.name}`;
    }
};
```

### 2.4.2 类型推断

类型推断是TypeScript根据上下文自动推断变量或函数返回值的类型。

```typescript
// TypeScript推断出message是string类型
let message = "Hello, TypeScript!"; // 不需要显式指定string类型

// TypeScript推断出numbers是number[]类型
let numbers = [1, 2, 3, 4, 5];

// TypeScript推断出函数返回值是number类型
function add(a: number, b: number) {
    return a + b; // 推断返回类型为number
}
```

### 2.4.3 最佳实践

1. **何时使用类型注解**：
   - 函数参数
   - 函数返回值（当返回类型不明显时）
   - 复杂对象类型
   - 初始化后可能变化的变量

2. **何时依赖类型推断**：
   - 简单变量初始化
   - 明确的返回值类型
   - 已有类型的衍生

## 2.5 联合类型与交叉类型

### 2.5.1 联合类型（Union Types）

联合类型表示一个值可以是几种类型之一。

```typescript
// 基本联合类型
let value: string | number;
value = "Hello";
value = 42;

// 函数参数联合类型
function processValue(value: string | number): void {
    if (typeof value === "string") {
        console.log(value.toUpperCase()); // TypeScript知道这里是string
    } else {
        console.log(value.toFixed(2)); // TypeScript知道这里是number
    }
}

// 字面量联合类型
type Direction = "North" | "South" | "East" | "West";
let direction: Direction = "North";
// direction = "Northeast"; // 错误
```

### 2.5.2 交叉类型（Intersection Types）

交叉类型将多个类型合并为一个类型。

```typescript
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
```

### 2.5.3 类型守卫

类型守卫是一些表达式，它们在运行时会检查类型，并在特定作用域内缩小类型范围。

```typescript
// typeof 类型守卫
function processValue(value: string | number): void {
    if (typeof value === "string") {
        // 在这个分支中，TypeScript知道value是string类型
        console.log(value.toUpperCase());
    } else {
        // 在这个分支中，TypeScript知道value是number类型
        console.log(value.toFixed(2));
    }
}

// in 操作符类型守卫
interface Cat {
    meow(): void;
}

interface Dog {
    bark(): void;
}

function makeSound(animal: Cat | Dog): void {
    if ("meow" in animal) {
        animal.meow(); // TypeScript知道animal是Cat
    } else {
        animal.bark(); // TypeScript知道animal是Dog
    }
}

// 自定义类型守卫
function isCat(animal: Cat | Dog): animal is Cat {
    return (animal as Cat).meow !== undefined;
}

function animalSound(animal: Cat | Dog): void {
    if (isCat(animal)) {
        animal.meow(); // TypeScript知道animal是Cat
    } else {
        animal.bark(); // TypeScript知道animal是Dog
    }
}
```

## 2.6 类型别名

类型别名用于给一个类型起个新名字，可以用于原始类型、联合类型、交叉类型等。

```typescript
// 基本类型别名
type Name = string;
type Age = number;

// 对象类型别名
type Person = {
    name: Name;
    age: Age;
    greet(): string;
};

// 联合类型别名
type ID = string | number;

// 函数类型别名
type Greeter = (name: string) => string;

// 泛型类型别名
type Container<T> = { value: T };

// 使用类型别名
const john: Person = {
    name: "John",
    age: 30,
    greet() {
        return `Hello, I'm ${this.name}`;
    }
};

const userId: ID = "USER123";
const productId: ID = 456;

const sayHello: Greeter = (name) => `Hello, ${name}!`;

const numberContainer: Container<number> = { value: 42 };
```

## 2.7 字面量类型

字面量类型允许指定一个值必须为某个特定的字符串、数字或布尔值。

```typescript
// 字符串字面量类型
type Theme = "light" | "dark";
type EventName = "click" | "focus" | "blur";

// 数字字面量类型
type DiceRoll = 1 | 2 | 3 | 4 | 5 | 6;

// 布尔字面量类型
type Success = true;
type Failure = false;

// 使用字面量类型
function setTheme(theme: Theme): void {
    document.body.className = theme;
}

setTheme("light"); // 正确
// setTheme("blue"); // 错误："blue"不是Theme类型
```

## 2.8 类型断言

类型断言是一种告诉TypeScript编译器"相信我，我知道我在做什么"的方式。

### 2.8.1 尖括号语法

```typescript
let someValue: any = "this is a string";
let strLength: number = (<string>someValue).length;

// 注意：在JSX中不能使用尖括号语法
```

### 2.8.2 as语法

```typescript
let someValue: any = "this is a string";
let strLength: number = (someValue as string).length;

// as语法在JSX中也可以使用
```

### 2.8.3 非空断言操作符

非空断言操作符`!`用于断言操作对象不是`null`或`undefined`。

```typescript
// 可选属性
interface Person {
    name: string;
    age?: number;
}

function getAge(person: Person): number {
    // 使用非空断言告诉TypeScriptage属性不是undefined
    return person.age!;
}

// 在可能为null或undefined的值上使用
function getElementById(id: string): HTMLElement {
    const element = document.getElementById(id);
    return element!; // 断言element不是null
}
```

## 2.9 类型兼容性

TypeScript的类型兼容性基于结构子类型，即如果类型X的成员至少与类型Y相同，则X兼容Y。

### 2.9.1 基本兼容性

```typescript
interface Named {
    name: string;
}

let person: Named = { name: "Alice" }; // 兼容
// let x: Named = { name: "Alice", age: 30 }; // 兼容，有额外的属性
// let y: Named = { age: 30 }; // 不兼容，缺少必需属性

// 函数兼容性
let greet = (name: string) => `Hello, ${name}!`;
let fn: (name: string) => string = greet; // 兼容
```

### 2.9.2 函数参数双向协变

```typescript
// 参数类型是双向协变的
type EventHandler = (event: Event) => void;

// 更具体的事件类型
type MouseEvent = {
    type: "click";
    x: number;
    y: number;
} & Event;

// 更通用的事件类型
type UIEvent = {
    type: string;
} & Event;

let mouseHandler: (event: MouseEvent) => void = (event) => {
    console.log(`Mouse clicked at ${event.x}, ${event.y}`);
};

// 由于双向协变，可以赋值
let eventHandler: EventHandler = mouseHandler;

// 也可以反过来
let genericHandler: EventHandler = (event) => {
    console.log(`Event type: ${event.type}`);
};

let mouseEventHandler: (event: MouseEvent) => void = genericHandler;
```

## 2.10 类型操作符

### 2.10.1 keyof 操作符

`keyof`操作符用于获取一个类型的所有键。

```typescript
interface Person {
    name: string;
    age: number;
    address: string;
}

type PersonKeys = keyof Person; // "name" | "age" | "address"

function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

let person: Person = {
    name: "Alice",
    age: 30,
    address: "123 Main St"
};

let name = getProperty(person, "name"); // 类型是string
let age = getProperty(person, "age");   // 类型是number
// let wrong = getProperty(person, "salary"); // 错误：不是Person的键
```

### 2.10.2 typeof 操作符

`typeof`操作符用于获取一个值或表达式的类型。

```typescript
let person = {
    name: "Alice",
    age: 30
};

type PersonType = typeof person; // { name: string; age: number; }

function greet(name: string) {
    return `Hello, ${name}!`;
}

type GreetFunction = typeof greet; // (name: string) => string
```

### 2.10.3 instanceof 操作符

`instanceof`操作符用于检查一个对象是否是某个类的实例。

```typescript
class Car {
    constructor(public brand: string) {}
}

class Bike {
    constructor(public brand: string) {}
}

function getBrand(vehicle: Car | Bike): string {
    if (vehicle instanceof Car) {
        // TypeScript知道vehicle是Car类型
        return `Car brand: ${vehicle.brand}`;
    } else {
        // TypeScript知道vehicle是Bike类型
        return `Bike brand: ${vehicle.brand}`;
    }
}
```

## 2.11 最佳实践

### 2.11.1 类型选择原则

1. **优先使用更具体的类型**：避免过度使用`any`，尽可能使用更具体的类型
2. **合理使用类型推断**：当类型明显时，让TypeScript推断类型
3. **善用联合类型和交叉类型**：提高代码的灵活性和复用性

### 2.11.2 类型安全性原则

1. **避免类型断言滥用**：只在确信类型正确时使用
2. **使用类型守卫**：通过类型守卫提供类型安全的操作
3. **启用严格模式**：在`tsconfig.json`中设置`"strict": true`

### 2.11.3 代码组织原则

1. **使用类型别名**：为复杂类型定义别名，提高可读性
2. **集中定义类型**：将相关类型定义放在一起
3. **文档化复杂类型**：为复杂类型添加注释说明

## 2.12 实例：构建类型安全的配置系统

让我们通过一个实际例子来应用所学的类型系统知识。

```typescript
// 定义配置类型
interface DatabaseConfig {
    host: string;
    port: number;
    username: string;
    password: string;
    database: string;
}

interface ServerConfig {
    port: number;
    host: string;
    ssl: boolean;
}

interface AppConfig {
    name: string;
    version: string;
    environment: "development" | "staging" | "production";
    database: DatabaseConfig;
    server: ServerConfig;
}

// 类型安全的配置加载函数
function loadConfig(): AppConfig {
    const config: unknown = require("./config.json");
    
    // 类型守卫函数
    function isAppConfig(obj: any): obj is AppConfig {
        return (
            typeof obj === "object" &&
            obj !== null &&
            typeof obj.name === "string" &&
            typeof obj.version === "string" &&
            ["development", "staging", "production"].includes(obj.environment) &&
            typeof obj.database === "object" &&
            typeof obj.database.host === "string" &&
            typeof obj.database.port === "number" &&
            typeof obj.database.username === "string" &&
            typeof obj.database.password === "string" &&
            typeof obj.database.database === "string" &&
            typeof obj.server === "object" &&
            typeof obj.server.port === "number" &&
            typeof obj.server.host === "string" &&
            typeof obj.server.ssl === "boolean"
        );
    }
    
    if (!isAppConfig(config)) {
        throw new Error("Invalid configuration");
    }
    
    return config;
}

// 使用配置
function initializeApp(): void {
    const config = loadConfig();
    
    console.log(`Starting ${config.name} v${config.version}`);
    console.log(`Environment: ${config.environment}`);
    
    // TypeScript知道这些属性的类型
    console.log(`Server: ${config.server.host}:${config.server.port}`);
    console.log(`Database: ${config.database.host}:${config.database.port}`);
}
```

## 2.13 总结

在这一章中，我们深入学习了TypeScript的基础类型系统：

- 理解了类型系统的重要性和特点
- 掌握了TypeScript的基本类型和特殊类型
- 学会了类型注解和类型推断的使用方法
- 探索了联合类型、交叉类型和类型守卫
- 了解了类型别名、字面量类型和类型断言
- 掌握了类型兼容性和类型操作符的使用

类型系统是TypeScript的核心，掌握这些基础知识将为后续学习高级类型特性和设计模式打下坚实基础。

## 2.14 练习

1. 创建一个类型安全的表单验证系统，包含各种类型的输入字段
2. 实现一个类型安全的日志记录器，支持不同级别的日志
3. 构建一个类型安全的事件系统，处理不同类型的事件
4. 创建一个类型安全的配置管理器，支持环境特定的配置

通过完成这些练习，您将加深对TypeScript类型系统的理解，并能够将其应用到实际项目中。