# 6. TypeScript装饰器与元编程

## 6.1 装饰器概述

装饰器是一种特殊类型的声明，它可以被附加到类声明、方法、访问器、属性或参数上。装饰器使用`@expression`形式，其中`expression`必须是一个函数，它会在运行时被调用，被装饰的声明信息作为参数传入。

### 6.1.1 为什么使用装饰器

1. **元编程**：装饰器允许我们编写可以修改其他代码的代码
2. **横切关注点**：用于处理日志、性能分析、事务管理等横切关注点
3. **代码复用**：将通用功能抽象为装饰器，可以在多个地方重用
4. **声明式编程**：通过装饰器可以以声明方式添加行为，而不是命令式

### 6.1.2 装饰器类型

TypeScript支持以下几种装饰器：

1. **类装饰器**：用于类声明
2. **方法装饰器**：用于方法声明
3. **访问器装饰器**：用于访问器声明
4. **属性装饰器**：用于属性声明
5. **参数装饰器**：用于参数声明

### 6.1.3 启用装饰器支持

要使用装饰器，需要在`tsconfig.json`中启用装饰器支持：

```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

## 6.2 类装饰器

类装饰器在类声明之前声明，用于监视、修改或替换类定义。

### 6.2.1 基本类装饰器

```typescript
// 基本类装饰器
function ClassDecorator(constructor: Function) {
    console.log("ClassDecorator called for:", constructor.name);
}

@ClassDecorator
class MyClass {
    constructor() {
        console.log("MyClass instantiated");
    }
}

// 类装饰器返回值可以替换类构造函数
function ClassReplacer<T extends { new(...args: any[]): {} }>(constructor: T) {
    return class extends constructor {
        newProperty = "New property";
        hello = "override";
    };
}

@ClassReplacer
class Greeter {
    property = "original property";
    hello = "original hello";
}

console.log(new Greeter()); // 包含新属性和覆盖的方法
```

### 6.2.2 实用类装饰器示例

```typescript
// 添加日志功能到类
function Logged(constructor: Function) {
    console.log(`Creating instance of ${constructor.name}`);
    
    return class extends constructor {
        constructor(...args: any[]) {
            super(...args);
            console.log(`Instance of ${constructor.name} created with args:`, args);
        }
    };
}

// 添加方法到类
function AddMethods(constructor: Function) {
    constructor.prototype.getTimestamp = function() {
        return new Date().toISOString();
    };
    
    constructor.prototype.getClassName = function() {
        return this.constructor.name;
    };
}

@Logged
@AddMethods
class User {
    constructor(public name: string) {}
}

const user = new User("Alice");
console.log(user.getTimestamp());
console.log(user.getClassName());
```

## 6.3 方法装饰器

方法装饰器声明在方法声明之前，用于监视、修改或替换方法定义。

### 6.3.1 基本方法装饰器

```typescript
// 基本方法装饰器
function MethodDecorator(
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
) {
    console.log("MethodDecorator called on:", target.constructor.name, propertyKey);
    console.log("Method descriptor:", descriptor);
}

class Example {
    @MethodDecorator
    greet(name: string) {
        return `Hello, ${name}!`;
    }
}
```

### 6.3.2 实用方法装饰器示例

```typescript
// 日志装饰器
function Log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        console.log(`Calling ${propertyKey} with args:`, args);
        const result = originalMethod.apply(this, args);
        console.log(`${propertyKey} returned:`, result);
        return result;
    };
    
    return descriptor;
}

// 性能监控装饰器
function Measure(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        const start = performance.now();
        const result = originalMethod.apply(this, args);
        const end = performance.now();
        
        console.log(`${propertyKey} took ${end - start} milliseconds`);
        return result;
    };
    
    return descriptor;
}

// 防抖装饰器
function Debounce(delay: number = 300) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let timeoutId: number;
        
        descriptor.value = function(...args: any[]) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                originalMethod.apply(this, args);
            }, delay);
        };
        
        return descriptor;
    };
}

// 节流装饰器
function Throttle(delay: number = 300) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let lastCall = 0;
        
        descriptor.value = function(...args: any[]) {
            const now = Date.now();
            if (now - lastCall >= delay) {
                lastCall = now;
                return originalMethod.apply(this, args);
            }
        };
        
        return descriptor;
    };
}

class Calculator {
    @Log
    @Measure
    add(a: number, b: number): number {
        return a + b;
    }
    
    @Debounce(500)
    search(query: string): void {
        console.log(`Searching for: ${query}`);
    }
    
    @Throttle(1000)
    handleClick(): void {
        console.log("Button clicked");
    }
}

const calculator = new Calculator();
calculator.add(5, 3);
calculator.search("TypeScript");
calculator.search("Decorators");
calculator.handleClick();
calculator.handleClick();
```

## 6.4 访问器装饰器

访问器装饰器声明在访问器之前，用于监视、修改或替换访问器定义。

```typescript
// 访问器装饰器
function AccessorDecorator(
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
) {
    console.log("AccessorDecorator called on:", target.constructor.name, propertyKey);
    
    const originalGetter = descriptor.get;
    const originalSetter = descriptor.set;
    
    if (originalGetter) {
        descriptor.get = function() {
            console.log(`Getting ${propertyKey}`);
            return originalGetter!.apply(this);
        };
    }
    
    if (originalSetter) {
        descriptor.set = function(value: any) {
            console.log(`Setting ${propertyKey} to:`, value);
            return originalSetter!.apply(this, [value]);
        };
    }
    
    return descriptor;
}

class Person {
    private _name: string = "";
    
    @AccessorDecorator
    get name(): string {
        return this._name;
    }
    
    set name(value: string) {
        this._name = value;
    }
}

const person = new Person();
person.name = "Alice";
console.log(person.name);
```

## 6.5 属性装饰器

属性装饰器声明在属性声明之前，用于监视属性的定义。

```typescript
// 属性装饰器
function PropertyDecorator(target: any, propertyKey: string) {
    console.log("PropertyDecorator called on:", target.constructor.name, propertyKey);
    
    // 可以在这里添加元数据
    Reflect.defineMetadata("required", true, target, propertyKey);
}

// 只读属性装饰器
function ReadOnly(target: any, propertyKey: string) {
    Object.defineProperty(target, propertyKey, {
        writable: false,
        configurable: true
    });
}

// 格式化装饰器
function Format(format: string) {
    return function(target: any, propertyKey: string) {
        let value: any;
        
        const getter = function() {
            return value;
        };
        
        const setter = function(newVal: any) {
            if (format === "uppercase") {
                value = newVal.toUpperCase();
            } else if (format === "lowercase") {
                value = newVal.toLowerCase();
            } else {
                value = newVal;
            }
        };
        
        Object.defineProperty(target, propertyKey, {
            get: getter,
            set: setter,
            enumerable: true,
            configurable: true
        });
    };
}

class Product {
    @PropertyDecorator
    id: number = 0;
    
    @ReadOnly
    createdAt: Date = new Date();
    
    @Format("uppercase")
    name: string = "";
}

const product = new Product();
product.id = 1;
product.name = "awesome product";
product.createdAt = new Date(); // 无法设置，因为createdAt是只读的

console.log(product.name); // "AWESOME PRODUCT"
```

## 6.6 参数装饰器

参数装饰器声明在参数声明之前，用于监视参数的定义。

```typescript
// 参数装饰器
function ParameterDecorator(
    target: any,
    methodName: string,
    parameterIndex: number
) {
    console.log("ParameterDecorator called on:", target.constructor.name, methodName, parameterIndex);
    
    // 可以在这里添加参数验证
    const existingRequiredParameters = Reflect.getMetadata("requiredParameters", target) || [];
    existingRequiredParameters.push(parameterIndex);
    Reflect.defineMetadata("requiredParameters", existingRequiredParameters, target);
}

// 必需参数装饰器
function Required(target: any, methodName: string, parameterIndex: number) {
    const existingRequiredParameters = Reflect.getMetadata("requiredParameters", target, methodName) || [];
    existingRequiredParameters.push(parameterIndex);
    Reflect.defineMetadata("requiredParameters", existingRequiredParameters, target, methodName);
}

// 验证方法装饰器
function Validate(target: any, methodName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        const requiredParameters = Reflect.getMetadata("requiredParameters", target, methodName) || [];
        
        for (const parameterIndex of requiredParameters) {
            if (args[parameterIndex] === undefined || args[parameterIndex] === null) {
                throw new Error(`Parameter ${parameterIndex} is required for method ${methodName}`);
            }
        }
        
        return originalMethod.apply(this, args);
    };
    
    return descriptor;
}

class UserService {
    @Validate
    createUser(@Required name: string, @Required email: string, age?: number): void {
        console.log(`Creating user: ${name}, ${email}, ${age}`);
    }
}

const userService = new UserService();
userService.createUser("Alice", "alice@example.com"); // 正常
// userService.createUser("", "alice@example.com"); // 抛出错误：name是必需的
```

## 6.7 装饰器工厂

装饰器工厂是一个返回装饰器函数的函数，允许我们自定义装饰器的行为。

```typescript
// 带参数的装饰器工厂
function AddProperty(propertyName: string, value: any) {
    return function(constructor: Function) {
        constructor.prototype[propertyName] = value;
    };
}

// 可配置的日志装饰器
function Loggable(logLevel: "debug" | "info" | "error" = "info") {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            if (logLevel === "debug") {
                console.debug(`[${logLevel.toUpperCase()}] Calling ${propertyKey} with args:`, args);
            } else if (logLevel === "info") {
                console.info(`[${logLevel.toUpperCase()}] Calling ${propertyKey}`);
            } else {
                console.error(`[${logLevel.toUpperCase()}] Calling ${propertyKey}`);
            }
            
            const result = originalMethod.apply(this, args);
            
            console.log(`${propertyKey} returned:`, result);
            return result;
        };
        
        return descriptor;
    };
}

// 验证装饰器工厂
function Validate(validator: (value: any) => boolean, errorMessage: string) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            for (let i = 0; i < args.length; i++) {
                if (!validator(args[i])) {
                    throw new Error(`Invalid argument at position ${i}: ${errorMessage}`);
                }
            }
            
            return originalMethod.apply(this, args);
        };
        
        return descriptor;
    };
}

@AddProperty("version", "1.0.0")
class API {
    @Loggable("debug")
    @Validate(
        (value: any) => typeof value === "string" && value.trim().length > 0,
        "URL must be a non-empty string"
    )
    fetch(url: string): string {
        return `Data from ${url}`;
    }
}

const api = new API();
console.log((api as any).version); // "1.0.0"
api.fetch("https://api.example.com");
```

## 6.8 元数据反射（Reflect Metadata）

反射是程序在运行时检查和修改其自身结构的能力。TypeScript通过`reflect-metadata`包提供元数据反射功能。

### 6.8.1 安装和配置

首先安装`reflect-metadata`包：

```bash
npm install reflect-metadata
```

然后在应用程序的入口点导入它：

```typescript
import "reflect-metadata";
```

### 6.8.2 使用反射元数据

```typescript
import "reflect-metadata";

// 定义元数据键
const DESIGN_TYPE = "design:type";
const DESIGN_PARAMTYPES = "design:paramtypes";
const DESIGN_RETURN_TYPE = "design:returntype";

// 自定义元数据键
const VALIDATION_RULES = "validation:rules";
const API_ENDPOINT = "api:endpoint";

// 定义元数据类型
interface ValidationRule {
    validate: (value: any) => boolean;
    message: string;
}

// 添加元数据的装饰器
function AddValidationRule(rule: ValidationRule) {
    return function(target: any, propertyKey: string) {
        const existingRules = Reflect.getMetadata(VALIDATION_RULES, target, propertyKey) || [];
        existingRules.push(rule);
        Reflect.defineMetadata(VALIDATION_RULES, existingRules, target, propertyKey);
    };
}

function ApiEndpoint(endpoint: string) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        Reflect.defineMetadata(API_ENDPOINT, endpoint, target, propertyKey);
    };
}

class UserController {
    @ApiEndpoint("/users")
    @AddValidationRule({
        validate: (value) => typeof value === "string" && value.length > 3,
        message: "Username must be a string with length > 3"
    })
    createUser(username: string, email: string): void {
        console.log(`Creating user ${username} with email ${email}`);
    }
}

// 检查元数据
const controller = new UserController();

// 获取方法的参数类型
const paramTypes = Reflect.getMetadata(DESIGN_PARAMTYPES, controller, "createUser");
console.log("Parameter types:", paramTypes); // [String, String]

// 获取方法的返回类型
const returnType = Reflect.getMetadata(DESIGN_RETURN_TYPE, controller, "createUser");
console.log("Return type:", returnType); // void

// 获取自定义元数据
const validationRules = Reflect.getMetadata(VALIDATION_RULES, controller, "createUser");
console.log("Validation rules:", validationRules);

const endpoint = Reflect.getMetadata(API_ENDPOINT, controller, "createUser");
console.log("API endpoint:", endpoint);

// 自动验证装饰器
function AutoValidate(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        const validationRules = Reflect.getMetadata(VALIDATION_RULES, target, propertyKey) || [];
        
        for (const rule of validationRules) {
            for (const arg of args) {
                if (!rule.validate(arg)) {
                    throw new Error(rule.message);
                }
            }
        }
        
        return originalMethod.apply(this, args);
    };
    
    return descriptor;
}

// 使用自动验证装饰器
class ValidatedController {
    @AutoValidate
    @ApiEndpoint("/validated-users")
    @AddValidationRule({
        validate: (value) => typeof value === "string" && value.length > 3,
        message: "Username must be a string with length > 3"
    })
    @AddValidationRule({
        validate: (value) => typeof value === "string" && value.includes("@"),
        message: "Email must be a valid email address"
    })
    createUser(username: string, email: string): void {
        console.log(`Creating user ${username} with email ${email}`);
    }
}

const validatedController = new ValidatedController();
validatedController.createUser("Alice", "alice@example.com"); // 正常
// validatedController.createUser("A", "alice@example.com"); // 抛出错误
```

## 6.9 实用装饰器示例

### 6.9.1 依赖注入装饰器

```typescript
import "reflect-metadata";

// 定义依赖注入元数据键
const INJECTABLE_METADATA_KEY = Symbol("injectable");
const INJECT_METADATA_KEY = Symbol("inject");

// 可注入装饰器
function Injectable() {
    return function<T extends { new(...args: any[]): {} }>(constructor: T) {
        Reflect.defineMetadata(INJECTABLE_METADATA_KEY, true, constructor);
        return constructor;
    };
}

// 注入装饰器
function Inject(token: any) {
    return function(target: any, propertyKey: string | symbol | undefined, parameterIndex: number) {
        const existingTokens = Reflect.getMetadata(INJECT_METADATA_KEY, target) || [];
        existingTokens[parameterIndex] = token;
        Reflect.defineMetadata(INJECT_METADATA_KEY, existingTokens, target);
    };
}

// 简单的服务容器
class Container {
    private services = new Map<any, any>();
    
    register<T>(token: new (...args: any[]) => T, implementation: T): void {
        this.services.set(token, implementation);
    }
    
    resolve<T>(token: new (...args: any[]) => T): T {
        const implementation = this.services.get(token);
        
        if (!implementation) {
            throw new Error(`No implementation registered for token`);
        }
        
        if (typeof implementation === "function") {
            // 检查是否是可注入的
            const isInjectable = Reflect.getMetadata(INJECTABLE_METADATA_KEY, implementation);
            
            if (isInjectable) {
                const tokens = Reflect.getMetadata(INJECT_METADATA_KEY, implementation) || [];
                const dependencies = tokens.map((token: any) => this.resolve(token));
                return new implementation(...dependencies);
            }
            
            return new implementation();
        }
        
        return implementation;
    }
}

// 定义服务接口
interface ILogger {
    log(message: string): void;
}

interface IDatabase {
    query(sql: string): any[];
}

// 实现服务
@Injectable()
class ConsoleLogger implements ILogger {
    log(message: string): void {
        console.log(`[LOG] ${message}`);
    }
}

@Injectable()
class MemoryDatabase implements IDatabase {
    private data: any[] = [];
    
    query(sql: string): any[] {
        console.log(`Executing query: ${sql}`);
        return this.data;
    }
    
    insert(data: any): void {
        this.data.push(data);
    }
}

@Injectable()
class UserService {
    constructor(
        @Inject(ConsoleLogger) private logger: ILogger,
        @Inject(MemoryDatabase) private database: IDatabase
    ) {}
    
    createUser(name: string): void {
        this.logger.log(`Creating user: ${name}`);
        this.database.insert({ name, createdAt: new Date() });
    }
    
    getUsers(): any[] {
        this.logger.log("Fetching users");
        return this.database.query("SELECT * FROM users");
    }
}

// 使用依赖注入
const container = new Container();
container.register(ConsoleLogger, new ConsoleLogger());
container.register(MemoryDatabase, new MemoryDatabase());

const userService = container.resolve(UserService);
userService.createUser("Alice");
const users = userService.getUsers();
```

### 6.9.2 ORM风格装饰器

```typescript
import "reflect-metadata";

// 定义ORM元数据键
const ENTITY_METADATA_KEY = Symbol("entity");
const COLUMN_METADATA_KEY = Symbol("column");
const PRIMARY_KEY_METADATA_KEY = Symbol("primaryKey");

// 实体装饰器
function Entity(tableName: string) {
    return function<T extends { new(...args: any[]): {} }>(constructor: T) {
        Reflect.defineMetadata(ENTITY_METADATA_KEY, tableName, constructor);
        return constructor;
    };
}

// 列装饰器
function Column(options: { type?: string; nullable?: boolean; length?: number } = {}) {
    return function(target: any, propertyKey: string) {
        Reflect.defineMetadata(COLUMN_METADATA_KEY, options, target, propertyKey);
    };
}

// 主键装饰器
function PrimaryKey(target: any, propertyKey: string) {
    Reflect.defineMetadata(PRIMARY_KEY_METADATA_KEY, true, target, propertyKey);
    Column({})(target, propertyKey);
}

// 简单的ORM基类
abstract class BaseModel {
    static getTableName(): string {
        return Reflect.getMetadata(ENTITY_METADATA_KEY, this) || this.name.toLowerCase();
    }
    
    static getColumns(): Record<string, any> {
        const columns: Record<string, any> = {};
        const prototype = this.prototype;
        const propertyNames = Object.getOwnPropertyNames(prototype);
        
        for (const propertyName of propertyNames) {
            const columnOptions = Reflect.getMetadata(COLUMN_METADATA_KEY, prototype, propertyName);
            const isPrimaryKey = Reflect.getMetadata(PRIMARY_KEY_METADATA_KEY, prototype, propertyName);
            
            if (columnOptions) {
                columns[propertyName] = {
                    ...columnOptions,
                    primaryKey: isPrimaryKey || false
                };
            }
        }
        
        return columns;
    }
    
    static getPrimaryKey(): string | null {
        const columns = this.getColumns();
        for (const [columnName, columnOptions] of Object.entries(columns)) {
            if (columnOptions.primaryKey) {
                return columnName;
            }
        }
        return null;
    }
    
    toJSON(): Record<string, any> {
        const result: Record<string, any> = {};
        const constructor = this.constructor as typeof BaseModel;
        const columns = constructor.getColumns();
        
        for (const columnName of Object.keys(columns)) {
            result[columnName] = (this as any)[columnName];
        }
        
        return result;
    }
    
    static fromJSON<T extends typeof BaseModel>(this: T, json: Record<string, any>): InstanceType<T> {
        const instance = new this() as InstanceType<T>;
        const columns = this.getColumns();
        
        for (const [columnName, columnOptions] of Object.entries(columns)) {
            if (json[columnName] !== undefined) {
                (instance as any)[columnName] = json[columnName];
            }
        }
        
        return instance;
    }
}

// 使用装饰器定义模型
@Entity("users")
class User extends BaseModel {
    @PrimaryKey
    @Column({ type: "number" })
    id: number = 0;
    
    @Column({ type: "string", length: 100, nullable: false })
    name: string = "";
    
    @Column({ type: "string", length: 255, nullable: false })
    email: string = "";
    
    @Column({ type: "string", length: 20, nullable: true })
    phone: string = "";
    
    @Column({ type: "date", nullable: false })
    createdAt: Date = new Date();
}

// 使用模型
console.log(`Table name: ${User.getTableName()}`);
console.log(`Columns:`, User.getColumns());
console.log(`Primary key:`, User.getPrimaryKey());

const userData = {
    id: 1,
    name: "Alice",
    email: "alice@example.com",
    phone: "123-456-7890",
    createdAt: new Date()
};

const user = User.fromJSON(userData);
console.log("User from JSON:", user);
console.log("User to JSON:", user.toJSON());
```

## 6.10 装饰器最佳实践

### 6.10.1 装饰器设计原则

1. **单一职责**：每个装饰器应该只做一件事
2. **可组合性**：装饰器应该可以与其他装饰器组合使用
3. **性能考虑**：装饰器在运行时会有开销，应谨慎使用
4. **元数据管理**：使用反射API管理元数据，保持一致性

### 6.10.2 装饰器组合顺序

装饰器的执行顺序是自下而上、自内而外的：

```typescript
function First(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log("First decorator");
}

function Second(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log("Second decorator");
}

class Example {
    @First
    @Second
    method() {}
}

// 输出：
// Second decorator
// First decorator
```

### 6.10.3 错误处理

```typescript
function SafeLog(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        try {
            console.log(`Calling ${propertyKey} with args:`, args);
            const result = originalMethod.apply(this, args);
            console.log(`${propertyKey} returned:`, result);
            return result;
        } catch (error) {
            console.error(`Error in ${propertyKey}:`, error);
            throw error;
        }
    };
    
    return descriptor;
}
```

## 6.11 实例：构建一个类型安全的REST API框架

让我们通过一个实际例子来应用装饰器和元编程的知识：

```typescript
import "reflect-metadata";

// 定义框架元数据键
const CONTROLLER_METADATA_KEY = Symbol("controller");
const ROUTE_METADATA_KEY = Symbol("route");
const MIDDLEWARE_METADATA_KEY = Symbol("middleware");
const BODY_METADATA_KEY = Symbol("body");
const PARAM_METADATA_KEY = Symbol("param");
const QUERY_METADATA_KEY = Symbol("query");

// HTTP方法枚举
enum HttpMethod {
    GET = "get",
    POST = "post",
    PUT = "put",
    DELETE = "delete",
    PATCH = "patch"
}

// 路由装饰器
function Controller(path: string = "") {
    return function<T extends { new(...args: any[]): {} }>(constructor: T) {
        Reflect.defineMetadata(CONTROLLER_METADATA_KEY, path, constructor);
        return constructor;
    };
}

// HTTP方法装饰器
function Get(path: string = "") {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingRoutes = Reflect.getMetadata(ROUTE_METADATA_KEY, target) || [];
        existingRoutes.push({
            method: HttpMethod.GET,
            path,
            handler: propertyKey
        });
        Reflect.defineMetadata(ROUTE_METADATA_KEY, existingRoutes, target);
        return descriptor;
    };
}

function Post(path: string = "") {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingRoutes = Reflect.getMetadata(ROUTE_METADATA_KEY, target) || [];
        existingRoutes.push({
            method: HttpMethod.POST,
            path,
            handler: propertyKey
        });
        Reflect.defineMetadata(ROUTE_METADATA_KEY, existingRoutes, target);
        return descriptor;
    };
}

function Put(path: string = "") {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingRoutes = Reflect.getMetadata(ROUTE_METADATA_KEY, target) || [];
        existingRoutes.push({
            method: HttpMethod.PUT,
            path,
            handler: propertyKey
        });
        Reflect.defineMetadata(ROUTE_METADATA_KEY, existingRoutes, target);
        return descriptor;
    };
}

function Delete(path: string = "") {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingRoutes = Reflect.getMetadata(ROUTE_METADATA_KEY, target) || [];
        existingRoutes.push({
            method: HttpMethod.DELETE,
            path,
            handler: propertyKey
        });
        Reflect.defineMetadata(ROUTE_METADATA_KEY, existingRoutes, target);
        return descriptor;
    };
}

// 参数装饰器
function Body() {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingBodyParams = Reflect.getMetadata(BODY_METADATA_KEY, target, propertyKey) || [];
        existingBodyParams.push(parameterIndex);
        Reflect.defineMetadata(BODY_METADATA_KEY, existingBodyParams, target, propertyKey);
    };
}

function Param(name: string) {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingParams = Reflect.getMetadata(PARAM_METADATA_KEY, target, propertyKey) || [];
        existingParams[parameterIndex] = { name };
        Reflect.defineMetadata(PARAM_METADATA_KEY, existingParams, target, propertyKey);
    };
}

function Query(name: string) {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingQueries = Reflect.getMetadata(QUERY_METADATA_KEY, target, propertyKey) || [];
        existingQueries[parameterIndex] = { name };
        Reflect.defineMetadata(QUERY_METADATA_KEY, existingQueries, target, propertyKey);
    };
}

// 中间件装饰器
function Middleware(...middlewares: Function[]) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingMiddlewares = Reflect.getMetadata(MIDDLEWARE_METADATA_KEY, target, propertyKey) || [];
        existingMiddlewares.push(...middlewares);
        Reflect.defineMetadata(MIDDLEWARE_METADATA_KEY, existingMiddlewares, target, propertyKey);
        return descriptor;
    };
}

// 请求/响应接口
interface Request {
    method: string;
    path: string;
    params: Record<string, string>;
    query: Record<string, string>;
    body: any;
}

interface Response {
    status(code: number): Response;
    json(data: any): void;
    send(data: string): void;
}

// 简单的路由器类
class Router {
    private routes: Array<{
        method: string;
        path: string;
        handler: Function;
        middlewares: Function[];
    }> = [];
    
    registerController(controller: any): void {
        const controllerPath = Reflect.getMetadata(CONTROLLER_METADATA_KEY, controller.constructor) || "";
        const routes = Reflect.getMetadata(ROUTE_METADATA_KEY, controller) || [];
        
        for (const route of routes) {
            const fullPath = `${controllerPath}${route.path}`;
            const middlewares = Reflect.getMetadata(MIDDLEWARE_METADATA_KEY, controller, route.handler) || [];
            
            this.routes.push({
                method: route.method,
                path: fullPath,
                handler: controller[route.handler].bind(controller),
                middlewares
            });
        }
    }
    
    findRoute(method: string, path: string): any {
        return this.routes.find(route => 
            route.method === method && this.matchPath(route.path, path)
        );
    }
    
    private matchPath(routePath: string, requestPath: string): boolean {
        // 简单的路径匹配，实际实现会更复杂
        if (routePath === requestPath) return true;
        
        // 处理参数路径，如 /users/:id
        const routeSegments = routePath.split('/');
        const requestSegments = requestPath.split('/');
        
        if (routeSegments.length !== requestSegments.length) return false;
        
        for (let i = 0; i < routeSegments.length; i++) {
            if (!routeSegments[i].startsWith(':') && routeSegments[i] !== requestSegments[i]) {
                return false;
            }
        }
        
        return true;
    }
    
    async handleRequest(request: Request, response: Response): Promise<void> {
        const route = this.findRoute(request.method, request.path);
        
        if (!route) {
            response.status(404).send("Not Found");
            return;
        }
        
        try {
            // 执行中间件
            for (const middleware of route.middlewares) {
                await middleware(request, response);
            }
            
            // 提取参数
            const params = this.extractParams(route.path, request.path);
            request.params = params;
            
            // 提取和处理方法参数
            const args = await this.resolveArguments(request, route.handler);
            
            // 执行路由处理器
            const result = await route.handler(...args);
            
            if (result !== undefined) {
                response.json(result);
            }
        } catch (error) {
            console.error("Error handling request:", error);
            response.status(500).send("Internal Server Error");
        }
    }
    
    private extractParams(routePath: string, requestPath: string): Record<string, string> {
        const params: Record<string, string> = {};
        const routeSegments = routePath.split('/');
        const requestSegments = requestPath.split('/');
        
        for (let i = 0; i < routeSegments.length; i++) {
            if (routeSegments[i].startsWith(':')) {
                const paramName = routeSegments[i].substring(1);
                params[paramName] = requestSegments[i];
            }
        }
        
        return params;
    }
    
    private async resolveArguments(request: Request, handler: Function): Promise<any[]> {
        const target = handler;
        const handlerName = handler.name;
        
        // 获取参数类型
        const paramTypes = Reflect.getMetadata("design:paramtypes", target, handlerName) || [];
        
        // 获取参数装饰器元数据
        const bodyParams = Reflect.getMetadata(BODY_METADATA_KEY, target, handlerName) || [];
        const routeParams = Reflect.getMetadata(PARAM_METADATA_KEY, target, handlerName) || [];
        const queryParams = Reflect.getMetadata(QUERY_METADATA_KEY, target, handlerName) || [];
        
        const args: any[] = [];
        
        for (let i = 0; i < paramTypes.length; i++) {
            if (bodyParams.includes(i)) {
                args.push(request.body);
            } else if (routeParams[i]) {
                const paramName = routeParams[i].name;
                args.push(request.params[paramName]);
            } else if (queryParams[i]) {
                const queryName = queryParams[i].name;
                args.push(request.query[queryName]);
            } else {
                args.push(undefined);
            }
        }
        
        return args;
    }
}

// 认证中间件
function authMiddleware(request: Request, response: Response): Promise<void> {
    return new Promise((resolve, reject) => {
        // 模拟认证逻辑
        const token = request.headers["authorization"];
        
        if (!token) {
            response.status(401).send("Unauthorized");
            return reject(new Error("Unauthorized"));
        }
        
        // 在实际应用中，这里会验证token
        console.log("User authenticated");
        resolve();
    });
}

// 日志中间件
function logMiddleware(request: Request, response: Response): Promise<void> {
    return new Promise((resolve) => {
        console.log(`${request.method} ${request.path}`);
        resolve();
    });
}

// 用户模型
interface User {
    id: number;
    name: string;
    email: string;
}

// 模拟数据库
const users: User[] = [
    { id: 1, name: "Alice", email: "alice@example.com" },
    { id: 2, name: "Bob", email: "bob@example.com" },
    { id: 3, name: "Charlie", email: "charlie@example.com" }
];

// 使用装饰器定义控制器
@Controller("/users")
class UserController {
    @Get()
    @Middleware(logMiddleware)
    getUsers(): User[] {
        return users;
    }
    
    @Get("/:id")
    @Middleware(logMiddleware)
    getUserById(@Param("id") id: string): User | undefined {
        const userId = parseInt(id, 10);
        return users.find(user => user.id === userId);
    }
    
    @Post()
    @Middleware(logMiddleware, authMiddleware)
    createUser(@Body() userData: Partial<User>): User {
        const newUser: User = {
            id: users.length + 1,
            name: userData.name || "",
            email: userData.email || ""
        };
        
        users.push(newUser);
        return newUser;
    }
    
    @Put("/:id")
    @Middleware(logMiddleware, authMiddleware)
    updateUser(@Param("id") id: string, @Body() userData: Partial<User>): User | undefined {
        const userId = parseInt(id, 10);
        const userIndex = users.findIndex(user => user.id === userId);
        
        if (userIndex === -1) {
            return undefined;
        }
        
        users[userIndex] = { ...users[userIndex], ...userData };
        return users[userIndex];
    }
    
    @Delete("/:id")
    @Middleware(logMiddleware, authMiddleware)
    deleteUser(@Param("id") id: string): boolean {
        const userId = parseInt(id, 10);
        const userIndex = users.findIndex(user => user.id === userId);
        
        if (userIndex === -1) {
            return false;
        }
        
        users.splice(userIndex, 1);
        return true;
    }
    
    @Get("/search")
    searchUsers(@Query("q") query: string): User[] {
        if (!query) return [];
        
        return users.filter(user => 
            user.name.toLowerCase().includes(query.toLowerCase()) ||
            user.email.toLowerCase().includes(query.toLowerCase())
        );
    }
}

// 使用路由器
const router = new Router();
router.registerController(new UserController());

// 模拟请求/响应对象
function createMockRequest(method: string, path: string, body?: any, query?: Record<string, string>): Request {
    return {
        method,
        path,
        params: {},
        query: query || {},
        body: body || {},
        headers: {}
    };
}

function createMockResponse(): Response {
    let statusCode = 200;
    let responseData: any;
    
    return {
        status(code: number): Response {
            statusCode = code;
            return this;
        },
        json(data: any): void {
            responseData = data;
            console.log(`Response (${statusCode}):`, responseData);
        },
        send(data: string): void {
            responseData = data;
            console.log(`Response (${statusCode}):`, responseData);
        }
    };
}

// 测试路由
async function testRoutes() {
    console.log("Testing routes:");
    
    // 获取所有用户
    const request1 = createMockRequest("get", "/users");
    const response1 = createMockResponse();
    await router.handleRequest(request1, response1);
    
    // 获取特定用户
    const request2 = createMockRequest("get", "/users/1");
    const response2 = createMockResponse();
    await router.handleRequest(request2, response2);
    
    // 创建用户
    const request3 = createMockRequest("post", "/users", { name: "David", email: "david@example.com" });
    const response3 = createMockResponse();
    await router.handleRequest(request3, response3);
    
    // 更新用户
    const request4 = createMockRequest("put", "/users/1", { name: "Alice Smith" });
    const response4 = createMockResponse();
    await router.handleRequest(request4, response4);
    
    // 搜索用户
    const request5 = createMockRequest("get", "/users/search", undefined, { q: "alice" });
    const response5 = createMockResponse();
    await router.handleRequest(request5, response5);
}

testRoutes();
```

## 6.12 总结

在这一章中，我们深入学习了TypeScript的装饰器和元编程：

- 理解了装饰器的概念、类型和使用场景
- 掌握了类装饰器、方法装饰器、访问器装饰器、属性装饰器和参数装饰器
- 学会了装饰器工厂和自定义装饰器的创建
- 探索了反射元数据和反射API的使用
- 学习了装饰器组合和最佳实践
- 构建了一个类型安全的REST API框架

装饰器和元编程是TypeScript的高级特性，它们使代码更加灵活、可扩展和声明式。掌握这些特性将帮助您构建更加优雅和强大的应用程序。

## 6.13 练习

1. 创建一个缓存装饰器，用于缓存函数的结果
2. 实现一个验证装饰器系统，支持多种验证规则
3. 构建一个事件驱动的系统，使用装饰器定义事件处理器
4. 创建一个ORM风格的装饰器系统，用于数据库操作

通过完成这些练习，您将加深对TypeScript装饰器和元编程的理解，并能够将其应用到实际项目中。