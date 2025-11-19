// 方法装饰器示例
import "reflect-metadata";

// 日志装饰器
function Log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
        console.log(`[${target.constructor.name}] Calling ${propertyKey} with args:`, args);
        const result = originalMethod.apply(this, args);
        console.log(`[${target.constructor.name}] ${propertyKey} returned:`, result);
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
        
        console.log(`[${target.constructor.name}] ${propertyKey} took ${end - start} milliseconds`);
        return result;
    };
    
    return descriptor;
}

// 防抖装饰器
function Debounce(delay: number = 300) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let timeoutId: NodeJS.Timeout;
        
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

// 错误处理装饰器
function Catch(handler?: (error: Error) => void) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            try {
                const result = originalMethod.apply(this, args);
                
                // 如果返回Promise，处理Promise的catch
                if (result && typeof result.catch === "function") {
                    return result.catch((error: Error) => {
                        console.error(`[${target.constructor.name}] Error in ${propertyKey}:`, error);
                        if (handler) {
                            handler(error);
                        }
                        throw error;
                    });
                }
                
                return result;
            } catch (error) {
                console.error(`[${target.constructor.name}] Error in ${propertyKey}:`, error);
                if (handler) {
                    handler(error as Error);
                }
                throw error;
            }
        };
        
        return descriptor;
    };
}

// 重试装饰器
function Retry(maxAttempts: number = 3, delay: number = 1000) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = async function(...args: any[]) {
            let lastError: Error;
            
            for (let attempt = 1; attempt <= maxAttempts; attempt++) {
                try {
                    return await originalMethod.apply(this, args);
                } catch (error) {
                    lastError = error as Error;
                    console.warn(`[${target.constructor.name}] Attempt ${attempt} failed for ${propertyKey}:`, error);
                    
                    if (attempt < maxAttempts) {
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                }
            }
            
            throw lastError;
        };
        
        return descriptor;
    };
}

// 缓存装饰器
function Cache(ttl: number = 60000) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        const cache = new Map<string, { value: any; timestamp: number }>();
        
        descriptor.value = function(...args: any[]) {
            const key = JSON.stringify(args);
            const cached = cache.get(key);
            
            if (cached && Date.now() - cached.timestamp < ttl) {
                console.log(`[${target.constructor.name}] Cache hit for ${propertyKey} with args:`, args);
                return cached.value;
            }
            
            console.log(`[${target.constructor.name}] Cache miss for ${propertyKey} with args:`, args);
            const result = originalMethod.apply(this, args);
            
            cache.set(key, {
                value: result,
                timestamp: Date.now()
            });
            
            return result;
        };
        
        return descriptor;
    };
}

// 权限检查装饰器
function RequirePermission(permission: string) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            const userPermissions = (this as any).permissions || [];
            
            if (!userPermissions.includes(permission)) {
                throw new Error(`Permission '${permission}' required to access ${propertyKey}`);
            }
            
            return originalMethod.apply(this, args);
        };
        
        return descriptor;
    };
}

// 创建一个装饰器应用的示例类
class Calculator {
    @Log
    @Measure
    add(a: number, b: number): number {
        // 模拟一些计算
        return a + b;
    }
    
    @Log
    @Cache(5000) // 缓存5秒
    @Measure
    fibonacci(n: number): number {
        if (n <= 1) return n;
        return this.fibonacci(n - 1) + this.fibonacci(n - 2);
    }
    
    @Debounce(500) // 防抖500毫秒
    @Log
    search(query: string): void {
        console.log(`Searching for: ${query}`);
    }
    
    @Throttle(1000) // 节流1秒
    @Log
    handleClick(): void {
        console.log("Button clicked");
    }
    
    @Catch((error) => console.log("Handled error:", error.message))
    riskyOperation(successRate: number = 0.5): string {
        if (Math.random() < successRate) {
            return "Operation succeeded";
        }
        throw new Error("Operation failed");
    }
    
    @Retry(3, 1000) // 重试3次，间隔1秒
    @Log
    async unreliableApiCall(shouldFail: boolean = false): Promise<string> {
        if (shouldFail && Math.random() < 0.8) {
            throw new Error("API call failed");
        }
        return "API call succeeded";
    }
    
    @RequirePermission("admin")
    @Log
    adminOperation(): string {
        return "Admin operation completed";
    }
}

class User {
    constructor(public permissions: string[]) {}
}

// 创建一个装饰器应用的示例类
class SearchService {
    @Debounce(300)
    @Log
    search(query: string): void {
        console.log(`Performing search for: ${query}`);
    }
}

// 使用装饰器
const calculator = new Calculator();

// 测试基本装饰器
console.log("=== Testing basic decorators ===");
calculator.add(5, 3);
calculator.fibonacci(10);
calculator.fibonacci(10); // 第二次调用应该使用缓存

// 测试防抖
console.log("\n=== Testing debounce ===");
const searchService = new SearchService();
searchService.search("TypeScript");
searchService.search("JavaScript"); // 应该被防抖
searchService.search("Decorators"); // 应该被防抖

setTimeout(() => {
    searchService.search("Async"); // 应该在300ms后执行
}, 400);

// 测试节流
console.log("\n=== Testing throttle ===");
calculator.handleClick();
calculator.handleClick(); // 应该被节流
calculator.handleClick(); // 应该被节流

setTimeout(() => {
    calculator.handleClick(); // 应该在1秒后执行
}, 1100);

// 测试错误处理
console.log("\n=== Testing error handling ===");
try {
    calculator.riskyOperation(0); // 总是失败
} catch (error) {
    console.log("Caught error:", (error as Error).message);
}

try {
    calculator.riskyOperation(1); // 总是成功
} catch (error) {
    console.log("This should not happen");
}

// 测试重试
console.log("\n=== Testing retry ===");
calculator.unreliableApiCall(true).then(result => {
    console.log("Result:", result);
}).catch(error => {
    console.log("Final error:", (error as Error).message);
});

// 测试权限检查
console.log("\n=== Testing permission check ===");
const adminUser = new User(["admin"]);
const regularUser = new User(["user"]);

// 动态设置权限以测试装饰器
const adminCalculator = calculator as any;
adminCalculator.permissions = adminUser.permissions;

try {
    adminCalculator.adminOperation();
} catch (error) {
    console.log("Admin should not get error");
}

// 更改为普通用户权限
adminCalculator.permissions = regularUser.permissions;

try {
    adminCalculator.adminOperation();
} catch (error) {
    console.log("Regular user should get error:", (error as Error).message);
}

console.log("Method decorators demo completed!");