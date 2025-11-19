// 属性和参数装饰器示例
import "reflect-metadata";

// 属性装饰器
function PropertyDecorator(target: any, propertyKey: string) {
    console.log("PropertyDecorator called on:", target.constructor.name, propertyKey);
    
    // 可以添加元数据
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

// 验证装饰器
function Validate(validator: (value: any) => boolean, errorMessage: string) {
    return function(target: any, propertyKey: string) {
        let value: any;
        
        const getter = function() {
            return value;
        };
        
        const setter = function(newVal: any) {
            if (!validator(newVal)) {
                throw new Error(`Invalid value for ${propertyKey}: ${errorMessage}`);
            }
            value = newVal;
        };
        
        Object.defineProperty(target, propertyKey, {
            get: getter,
            set: setter,
            enumerable: true,
            configurable: true
        });
    };
}

// 延迟计算装饰器
function Lazy<T>(factory: () => T) {
    return function(target: any, propertyKey: string) {
        let value: T | undefined;
        let computed = false;
        
        const getter = function() {
            if (!computed) {
                value = factory.call(this);
                computed = true;
            }
            return value;
        };
        
        Object.defineProperty(target, propertyKey, {
            get: getter,
            enumerable: true,
            configurable: true
        });
    };
}

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

// 类型检查装饰器
function TypeCheck(type: "string" | "number" | "boolean") {
    return function(target: any, methodName: string, parameterIndex: number) {
        const existingTypeChecks = Reflect.getMetadata("typeChecks", target, methodName) || [];
        existingTypeChecks[parameterIndex] = type;
        Reflect.defineMetadata("typeChecks", existingTypeChecks, target, methodName);
    };
}

// 验证方法装饰器
function ValidateParameters(target: any, methodName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        // 检查必需参数
        const requiredParameters = Reflect.getMetadata("requiredParameters", target, methodName) || [];
        
        for (const parameterIndex of requiredParameters) {
            if (args[parameterIndex] === undefined || args[parameterIndex] === null) {
                throw new Error(`Parameter ${parameterIndex} is required for method ${methodName}`);
            }
        }
        
        // 检查类型
        const typeChecks = Reflect.getMetadata("typeChecks", target, methodName) || [];
        
        for (const [index, expectedType] of Object.entries(typeChecks)) {
            const paramIndex = parseInt(index);
            const actualType = typeof args[paramIndex];
            
            if (actualType !== expectedType) {
                throw new Error(`Parameter ${paramIndex} should be of type ${expectedType}, but got ${actualType}`);
            }
        }
        
        return originalMethod.apply(this, args);
    };
    
    return descriptor;
}

// 依赖注入装饰器
function Inject(token: any) {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingTokens = Reflect.getMetadata("injectTokens", target, propertyKey) || [];
        existingTokens[parameterIndex] = token;
        Reflect.defineMetadata("injectTokens", existingTokens, target, propertyKey);
    };
}

// 测试属性装饰器
class Product {
    @PropertyDecorator
    id: number = 0;
    
    @ReadOnly
    createdAt: Date = new Date();
    
    @Format("uppercase")
    name: string = "";
    
    @Format("lowercase")
    category: string = "";
    
    @Validate(
        value => value >= 0,
        "Price must be non-negative"
    )
    price: number = 0;
    
    @Validate(
        value => value >= 0 && value <= 100,
        "Discount must be between 0 and 100"
    )
    discount: number = 0;
    
    @Lazy(function() {
        // 模拟昂贵的计算
        console.log("Calculating discounted price...");
        return this.price * (1 - this.discount / 100);
    })
    discountedPrice: number = 0;
    
    getPrice(): number {
        return this.price;
    }
    
    getDiscountedPrice(): number {
        return this.discountedPrice;
    }
}

// 测试参数装饰器
class UserService {
    @ValidateParameters
    createUser(
        @Required name: string,
        @TypeCheck("string") email: string,
        @Required age: number,
        @TypeCheck("boolean") isActive: boolean = true
    ): void {
        console.log(`Creating user: ${name}, ${email}, ${age}, isActive: ${isActive}`);
    }
    
    @ValidateParameters
    updateUser(
        @Required id: number,
        @TypeCheck("string") name?: string,
        @TypeCheck("string") email?: string
    ): void {
        console.log(`Updating user ${id} with name: ${name}, email: ${email}`);
    }
    
    @ValidateParameters
    search(
        @TypeCheck("string") query: string,
        @TypeCheck("number") limit: number = 10
    ): void {
        console.log(`Searching for: ${query}, limit: ${limit}`);
    }
}

// 测试依赖注入
class Logger {
    log(message: string): void {
        console.log(`[LOG] ${message}`);
    }
}

class Database {
    query(sql: string): any[] {
        console.log(`Executing query: ${sql}`);
        return [{ id: 1, name: "Alice" }];
    }
}

class UserRepository {
    constructor(
        @Inject(Logger) private logger: Logger,
        @Inject(Database) private database: Database
    ) {}
    
    findUser(id: number): any {
        this.logger.log(`Finding user with id: ${id}`);
        return this.database.query(`SELECT * FROM users WHERE id = ${id}`)[0];
    }
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
        
        // 检查是否有注入参数
        const paramTypes = Reflect.getMetadata("design:paramtypes", token) || [];
        const tokens: any[] = [];
        
        // 获取构造函数参数上的注入装饰器信息
        if (paramTypes.length > 0) {
            // 这里简化处理，实际实现会更复杂
            for (let i = 0; i < paramTypes.length; i++) {
                tokens.push(implementation);
            }
        }
        
        return new token(...tokens);
    }
}

// 使用示例
console.log("=== Property Decorators Demo ===");
const product = new Product();
product.id = 1;
product.name = "Awesome Product";
product.category = "ELECTRONICS";
product.price = 99.99;
product.discount = 10;

console.log("Product:", {
    id: product.id,
    name: product.name,
    category: product.category,
    price: product.price,
    discount: product.discount,
    createdAt: product.createdAt
});

// 第一次访问折扣价格，会触发计算
console.log("Discounted price (first access):", product.getDiscountedPrice());

// 第二次访问折扣价格，使用缓存值
console.log("Discounted price (second access):", product.getDiscountedPrice());

try {
    product.discount = 150; // 会抛出错误
} catch (error) {
    console.error("Error setting discount:", (error as Error).message);
}

try {
    product.price = -10; // 会抛出错误
} catch (error) {
    console.error("Error setting price:", (error as Error).message);
}

try {
    product.createdAt = new Date(); // 会抛出错误，因为是只读属性
} catch (error) {
    console.error("Error setting createdAt:", (error as Error).message);
}

console.log("\n=== Parameter Decorators Demo ===");
const userService = new UserService();

try {
    userService.createUser("Alice", "alice@example.com", 30);
} catch (error) {
    console.error("Error creating user:", (error as Error).message);
}

try {
    userService.createUser("", "alice@example.com", 30);
} catch (error) {
    console.error("Error creating user (empty name):", (error as Error).message);
}

try {
    userService.createUser("Alice", "alice@example.com", 30, "true");
} catch (error) {
    console.error("Error creating user (wrong type):", (error as Error).message);
}

try {
    userService.search("TypeScript");
} catch (error) {
    console.error("Error searching:", (error as Error).message);
}

console.log("\n=== Dependency Injection Demo ===");
const container = new Container();
container.register(Logger, new Logger());
container.register(Database, new Database());

try {
    // 简化的依赖注入实现
    const logger = new Logger();
    const database = new Database();
    const userRepository = new UserRepository(logger, database);
    
    const user = userRepository.findUser(1);
    console.log("Found user:", user);
} catch (error) {
    console.error("Error in dependency injection:", (error as Error).message);
}

console.log("Property and Parameter decorators demo completed!");