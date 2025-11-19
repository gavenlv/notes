# 3. TypeScript接口与类

## 3.1 接口（Interface）概述

接口是TypeScript中非常重要的概念，它定义了一个对象应该具有的结构。接口只定义成员的签名，不包含实现，这使得代码更加模块化和可维护。

### 3.1.1 为什么需要接口

1. **契约定义**：接口定义了对象必须遵循的契约
2. **类型安全**：编译时检查确保对象符合接口定义
3. **代码抽象**：隐藏实现细节，只暴露必要的接口
4. **多态支持**：不同对象可以实现相同接口，以不同方式表现

### 3.1.2 接口与类型别名的区别

在TypeScript中，接口和类型别名都可以用来定义对象结构，但它们有一些关键区别：

1. **继承**：接口支持继承，类型别名不支持
2. **合并**：接口可以自动合并，类型别名不能
3. **用途**：接口主要用于定义对象形状，类型别名更灵活，可以定义联合类型、交叉类型等

```typescript
// 接口
interface Person {
    name: string;
    age: number;
}

// 接口继承
interface Employee extends Person {
    employeeId: string;
}

// 类型别名
type PersonType = {
    name: string;
    age: number;
};

// 类型别名可以通过交叉类型实现类似继承的效果
type EmployeeType = PersonType & {
    employeeId: string;
};
```

## 3.2 接口定义与使用

### 3.2.1 基本接口定义

```typescript
// 基本接口
interface User {
    name: string;
    age: number;
}

// 使用接口
const user: User = {
    name: "Alice",
    age: 30
};
```

### 3.2.2 可选属性

接口属性可以使用`?`标记为可选：

```typescript
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
```

### 3.2.3 只读属性

接口属性可以使用`readonly`标记为只读：

```typescript
interface Point {
    readonly x: number; // 只读属性
    readonly y: number; // 只读属性
}

const point: Point = { x: 10, y: 20 };
// point.x = 30; // 错误，x是只读属性

// 使用readonly关键字创建不可变数组
interface ReadonlyArray<T> {
    readonly length: number;
    readonly [n: number]: T;
}

let readonlyArray: ReadonlyArray<number> = [1, 2, 3, 4];
// readonlyArray[0] = 5; // 错误，元素是只读的
// readonlyArray.push(5); // 错误，数组是只读的
```

### 3.2.4 函数类型接口

接口可以定义函数类型：

```typescript
interface SearchFunc {
    (source: string, subString: string): boolean;
}

const mySearch: SearchFunc = function(source: string, subString: string): boolean {
    return source.search(subString) > -1;
};

console.log(mySearch("Hello, World", "World")); // true
```

### 3.2.5 可索引类型接口

接口可以描述能够通过索引得到的类型，如数组或对象：

```typescript
// 字符串索引签名
interface StringArray {
    [index: number]: string;
}

const myArray: StringArray = ["Bob", "Alice", "Eve"];
console.log(myArray[1]); // "Alice"

// 对象索引签名
interface Dictionary {
    [key: string]: string;
}

const myDict: Dictionary = {
    "name": "Alice",
    "email": "alice@example.com"
};

console.log(myDict["name"]); // "Alice"
```

### 3.2.6 类类型接口

接口可以描述类的公共部分：

```typescript
interface ClockInterface {
    currentTime: Date;
    setTime(d: Date): void;
}

class Clock implements ClockInterface {
    currentTime: Date = new Date();
    
    setTime(d: Date) {
        this.currentTime = d;
    }
    
    constructor(h: number, m: number) {}
}
```

### 3.2.7 继承接口

接口可以相互继承：

```typescript
// 单继承
interface Shape {
    color: string;
}

interface Square extends Shape {
    sideLength: number;
}

const square: Square = {
    color: "blue",
    sideLength: 10
};

// 多继承
interface Person {
    name: string;
}

interface Employee {
    employeeId: string;
}

interface Manager extends Person, Employee {
    teamSize: number;
}

const manager: Manager = {
    name: "John",
    employeeId: "EMP123",
    teamSize: 5
};
```

### 3.2.8 混合类型接口

接口可以描述多种类型的组合：

```typescript
interface Counter {
    (start: number): string; // 函数类型
    interval: number;       // 属性
    reset(): void;          // 方法
}

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
console.log(c(10)); // "10"
console.log(c.interval); // 123
c.reset(); // "Counter reset"
```

## 3.3 类（Class）概述

类是面向对象编程的核心概念，TypeScript扩展了JavaScript的类，添加了类型注解和其他面向对象特性。

### 3.3.1 类的基本组成

```typescript
class Person {
    // 属性
    private name: string;
    protected age: number;
    public gender: string;
    
    // 静态属性
    static species: string = "Homo sapiens";
    
    // 构造函数
    constructor(name: string, age: number, gender: string) {
        this.name = name;
        this.age = age;
        this.gender = gender;
    }
    
    // 方法
    public introduce(): string {
        return `I'm ${this.name}, ${this.age} years old.`;
    }
    
    // 静态方法
    static getSpecies(): string {
        return Person.species;
    }
}
```

### 3.3.2 访问修饰符

TypeScript提供了三种访问修饰符：

1. **public（公共）**：默认修饰符，可以在任何地方访问
2. **private（私有）**：只能在定义它的类中访问
3. **protected（受保护）**：可以在定义它的类及其子类中访问

```typescript
class Animal {
    public name: string;          // 公共属性，默认值
    private age: number;          // 私有属性
    protected gender: string;     // 受保护属性
    readonly id: number;          // 只读属性
    
    constructor(name: string, age: number, gender: string, id: number) {
        this.name = name;
        this.age = age;
        this.gender = gender;
        this.id = id;
    }
    
    public getInfo(): string {    // 公共方法
        return `${this.name} is ${this.age} years old.`;
    }
    
    private calculateBirthYear(): number {  // 私有方法
        return new Date().getFullYear() - this.age;
    }
    
    protected getGender(): string {         // 受保护方法
        return this.gender;
    }
}

const animal = new Animal("Dog", 5, "male", 1);
console.log(animal.name);       // 可以访问公共属性
// console.log(animal.age);      // 错误，无法访问私有属性
// console.log(animal.gender);   // 错误，无法访问受保护属性
console.log(animal.id);         // 可以访问只读属性
```

### 3.3.3 参数属性

参数属性是一种简化代码的方式，可以在构造函数参数中直接声明和初始化属性：

```typescript
// 传统方式
class Person {
    private name: string;
    public age: number;
    protected gender: string;
    
    constructor(name: string, age: number, gender: string) {
        this.name = name;
        this.age = age;
        this.gender = gender;
    }
}

// 使用参数属性
class PersonWithParams {
    constructor(
        private name: string,
        public age: number,
        protected gender: string
    ) {}
    
    public getInfo(): string {
        return `${this.name} is ${this.age} years old.`;
    }
}
```

## 3.4 类的继承

TypeScript支持类的继承，允许一个类继承另一个类的属性和方法。

### 3.4.1 基本继承

```typescript
class Animal {
    protected name: string;
    
    constructor(name: string) {
        this.name = name;
    }
    
    public move(distance: number = 0): void {
        console.log(`${this.name} moved ${distance}m.`);
    }
}

class Dog extends Animal {
    constructor(name: string) {
        // 调用父类构造函数
        super(name);
    }
    
    public bark(): void {
        console.log(`${this.name} barks!`);
    }
    
    // 重写父类方法
    public move(distance: number = 5): void {
        console.log(`${this.name} is running...`);
        super.move(distance); // 调用父类方法
    }
}

const dog = new Dog("Buddy");
dog.bark();    // "Buddy barks!"
dog.move(20);  // "Buddy is running..." 和 "Buddy moved 20m."
```

### 3.4.2 抽象类

抽象类是供其他类继承的基类，不能直接实例化。抽象类可以包含抽象方法，这些方法不包含实现，必须在派生类中实现。

```typescript
// 抽象类
abstract class Shape {
    abstract area(): number; // 抽象方法，没有实现
    
    // 普通方法
    display(): void {
        console.log(`This is a shape with area ${this.area()}`);
    }
}

// 继承抽象类的具体类
class Circle extends Shape {
    constructor(private radius: number) {
        super();
    }
    
    // 实现抽象方法
    area(): number {
        return Math.PI * this.radius * this.radius;
    }
}

class Rectangle extends Shape {
    constructor(private width: number, private height: number) {
        super();
    }
    
    area(): number {
        return this.width * this.height;
    }
}

const circle = new Circle(5);
circle.display(); // "This is a shape with area 78.53981633974483"

const rectangle = new Rectangle(10, 20);
rectangle.display(); // "This is a shape with area 200"
```

## 3.5 存取器（Getters和Setters）

TypeScript支持通过getters和setters来控制对对象成员的访问：

```typescript
class Employee {
    private _fullName: string = "";
    
    get fullName(): string {
        return this._fullName;
    }
    
    set fullName(newName: string) {
        if (newName.length > 0) {
            this._fullName = newName;
        } else {
            throw new Error("Name cannot be empty");
        }
    }
    
    private _salary: number = 0;
    
    get salary(): number {
        return this._salary;
    }
    
    set salary(newSalary: number) {
        if (newSalary >= 0) {
            this._salary = newSalary;
        } else {
            throw new Error("Salary cannot be negative");
        }
    }
}

const employee = new Employee();
employee.fullName = "John Doe";
console.log(employee.fullName); // "John Doe"

employee.salary = 50000;
console.log(employee.salary); // 50000

// employee.fullName = ""; // 错误：抛出异常
// employee.salary = -1000; // 错误：抛出异常
```

## 3.6 类实现接口

类可以使用`implements`关键字来实现一个或多个接口：

```typescript
// 定义接口
interface ClockInterface {
    currentTime: Date;
    setTime(d: Date): void;
}

interface Alarm {
    alarmTime: Date;
    setAlarm(time: Date): void;
    ring(): void;
}

// 实现多个接口
class DigitalClock implements ClockInterface, Alarm {
    currentTime: Date = new Date();
    alarmTime: Date = new Date();
    
    setTime(d: Date): void {
        this.currentTime = d;
    }
    
    setAlarm(time: Date): void {
        this.alarmTime = time;
    }
    
    ring(): void {
        console.log("Alarm is ringing!");
    }
}

const digitalClock = new DigitalClock();
digitalClock.setTime(new Date());
digitalClock.setAlarm(new Date(Date.now() + 3600000)); // 1小时后
digitalClock.ring(); // "Alarm is ringing!"
```

## 3.7 静态成员

类可以有静态成员，这些成员属于类本身，而不是类的实例：

```typescript
class MathHelper {
    // 静态属性
    static PI: number = 3.14159;
    
    // 静态方法
    static calculateCircumference(radius: number): number {
        return 2 * MathHelper.PI * radius;
    }
    
    static calculateArea(radius: number): number {
        return MathHelper.PI * radius * radius;
    }
    
    // 实例方法
    calculateDiameter(radius: number): number {
        return 2 * radius;
    }
}

// 使用静态成员
console.log(MathHelper.PI); // 3.14159
console.log(MathHelper.calculateCircumference(5)); // 31.4159
console.log(MathHelper.calculateArea(5)); // 78.53975

// 使用实例方法需要创建实例
const mathHelper = new MathHelper();
console.log(mathHelper.calculateDiameter(5)); // 10
```

## 3.8 构造函数签名

在TypeScript中，类既是值又是类型：

```typescript
class Greeter {
    static standardGreeting = "Hello, there";
    greeting: string;
    
    constructor(message?: string) {
        this.greeting = message || Greeter.standardGreeting;
    }
    
    greet() {
        return `Hello, ${this.greeting}`;
    }
}

let greeter: Greeter; // Greeter是类的类型
greeter = new Greeter("world");
console.log(greeter.greet()); // "Hello, world"

let greeterMaker: typeof Greeter; // typeof Greeter是类的构造函数类型
greeterMaker = Greeter;
greeterMaker.standardGreeting = "Hey there!";

let greeter2: Greeter = new greeterMaker();
console.log(greeter2.greet()); // "Hello, Hey there!"
```

## 3.9 接口与类的最佳实践

### 3.9.1 接口设计原则

1. **接口隔离原则**：不应该强迫客户端依赖于它们不使用的接口
2. **单一职责原则**：一个接口应该只负责一个功能领域
3. **依赖倒置原则**：高层模块不应该依赖于低层模块，两者都应该依赖于抽象

```typescript
// 好的接口设计
interface FileReader {
    read(path: string): Promise<string>;
}

interface FileWriter {
    write(path: string, content: string): Promise<void>;
}

interface FileSystem extends FileReader, FileWriter {
    delete(path: string): Promise<void>;
    exists(path: string): Promise<boolean>;
}

// 不好的接口设计（违反接口隔离原则）
interface FileSystemAll {
    read(path: string): Promise<string>;
    write(path: string, content: string): Promise<void>;
    delete(path: string): Promise<void>;
    exists(path: string): Promise<boolean>;
    compress(path: string): Promise<void>;
    decompress(path: string): Promise<void>;
    upload(url: string, path: string): Promise<void>;
    download(url: string, path: string): Promise<void>;
}
```

### 3.9.2 类设计原则

1. **单一职责原则**：一个类应该只有一个引起变化的原因
2. **开闭原则**：对扩展开放，对修改关闭
3. **里氏替换原则**：子类型必须能够替换它们的基类型
4. **依赖倒置原则**：依赖于抽象，不依赖于具体实现

```typescript
// 好的类设计
abstract class Shape {
    abstract area(): number;
    abstract perimeter(): number;
    
    display(): void {
        console.log(`Area: ${this.area()}, Perimeter: ${this.perimeter()}`);
    }
}

class Circle extends Shape {
    constructor(private radius: number) {
        super();
    }
    
    area(): number {
        return Math.PI * this.radius * this.radius;
    }
    
    perimeter(): number {
        return 2 * Math.PI * this.radius;
    }
}

class Rectangle extends Shape {
    constructor(private width: number, private height: number) {
        super();
    }
    
    area(): number {
        return this.width * this.height;
    }
    
    perimeter(): number {
        return 2 * (this.width + this.height);
    }
}
```

## 3.10 实例：构建一个类型安全的表单验证系统

让我们通过一个实际例子来应用接口和类的知识：

```typescript
// 定义验证规则接口
interface ValidationRule<T = any> {
    validate(value: T): boolean;
    getErrorMessage(): string;
}

// 必填验证规则
class RequiredRule implements ValidationRule {
    validate(value: any): boolean {
        return value !== null && value !== undefined && value !== "";
    }
    
    getErrorMessage(): string {
        return "This field is required";
    }
}

// 长度验证规则
class LengthRule implements ValidationRule<string> {
    constructor(
        private minLength: number,
        private maxLength: number
    ) {}
    
    validate(value: string): boolean {
        return value.length >= this.minLength && value.length <= this.maxLength;
    }
    
    getErrorMessage(): string {
        return `Length must be between ${this.minLength} and ${this.maxLength}`;
    }
}

// 正则表达式验证规则
class RegexRule implements ValidationRule<string> {
    constructor(
        private pattern: RegExp,
        private errorMessage: string = "Invalid format"
    ) {}
    
    validate(value: string): boolean {
        return this.pattern.test(value);
    }
    
    getErrorMessage(): string {
        return this.errorMessage;
    }
}

// 表单字段接口
interface FormField<T = any> {
    name: string;
    value: T;
    rules: ValidationRule<T>[];
    errors: string[];
    validate(): boolean;
}

// 表单字段实现
class TextField implements FormField<string> {
    public errors: string[] = [];
    
    constructor(
        public name: string,
        public value: string,
        public rules: ValidationRule<string>[]
    ) {}
    
    validate(): boolean {
        this.errors = [];
        
        for (const rule of this.rules) {
            if (!rule.validate(this.value)) {
                this.errors.push(rule.getErrorMessage());
            }
        }
        
        return this.errors.length === 0;
    }
}

// 表单接口
interface Form {
    fields: Map<string, FormField>;
    addField<T>(field: FormField<T>): void;
    getField(name: string): FormField | undefined;
    validate(): boolean;
    getErrors(): Record<string, string[]>;
}

// 表单实现
class MyForm implements Form {
    public fields: Map<string, FormField> = new Map();
    
    addField<T>(field: FormField<T>): void {
        this.fields.set(field.name, field);
    }
    
    getField(name: string): FormField | undefined {
        return this.fields.get(name);
    }
    
    validate(): boolean {
        let isValid = true;
        
        for (const field of this.fields.values()) {
            if (!field.validate()) {
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    getErrors(): Record<string, string[]> {
        const errors: Record<string, string[]> = {};
        
        for (const [name, field] of this.fields.entries()) {
            if (field.errors.length > 0) {
                errors[name] = field.errors;
            }
        }
        
        return errors;
    }
}

// 使用示例
function createLoginForm(): Form {
    const form = new MyForm();
    
    // 添加用户名字段
    const usernameField = new TextField(
        "username",
        "",
        [
            new RequiredRule(),
            new LengthRule(3, 20)
        ]
    );
    form.addField(usernameField);
    
    // 添加密码字段
    const passwordField = new TextField(
        "password",
        "",
        [
            new RequiredRule(),
            new LengthRule(8, 50),
            new RegexRule(
                /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
                "Password must contain at least one uppercase letter, one lowercase letter, and one number"
            )
        ]
    );
    form.addField(passwordField);
    
    // 添加邮箱字段
    const emailField = new TextField(
        "email",
        "",
        [
            new RequiredRule(),
            new RegexRule(
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                "Please enter a valid email address"
            )
        ]
    );
    form.addField(emailField);
    
    return form;
}

// 测试表单
const loginForm = createLoginForm();

// 设置字段值
(loginForm.getField("username") as TextField).value = "user";
(loginForm.getField("password") as TextField).value = "Password123";
(loginForm.getField("email") as TextField).value = "user@example.com";

// 验证表单
const isValid = loginForm.validate();
const errors = loginForm.getErrors();

console.log("Form is valid:", isValid);
console.log("Form errors:", errors);
```

## 3.11 总结

在这一章中，我们深入学习了TypeScript的接口和类：

- 理解了接口的概念、定义和不同类型
- 掌握了类的定义、访问修饰符和继承机制
- 学会了抽象类、存取器和静态成员的使用
- 探索了接口与类的关系和最佳实践
- 构建了一个实际的表单验证系统

接口和类是TypeScript面向对象编程的基础，掌握它们将帮助您编写更加模块化、可维护和可扩展的代码。

## 3.12 练习

1. 创建一个类型安全的日志记录系统，使用接口定义不同的日志记录器
2. 实现一个银行账户管理系统，使用抽象类和继承
3. 构建一个类型安全的事件系统，支持发布-订阅模式
4. 创建一个类型安全的数据访问层，使用接口和类抽象数据访问逻辑

通过完成这些练习，您将加深对TypeScript接口和类的理解，并能够将其应用到实际项目中。