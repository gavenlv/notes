// 装饰器工厂示例
import "reflect-metadata";

// 带参数的装饰器工厂
function AddProperty(propertyName: string, value: any) {
    return function(constructor: Function) {
        console.log(`Adding property ${propertyName} with value:`, value);
        constructor.prototype[propertyName] = value;
    };
}

// 可配置的日志装饰器工厂
function Loggable(logLevel: "debug" | "info" | "error" = "info") {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            if (logLevel === "debug") {
                console.debug(`[${logLevel.toUpperCase()}] [${target.constructor.name}] Calling ${propertyKey} with args:`, args);
            } else if (logLevel === "info") {
                console.info(`[${logLevel.toUpperCase()}] [${target.constructor.name}] Calling ${propertyKey}`);
            } else {
                console.error(`[${logLevel.toUpperCase()}] [${target.constructor.name}] Calling ${propertyKey}`);
            }
            
            const result = originalMethod.apply(this, args);
            
            console.log(`[${target.constructor.name}] ${propertyKey} returned:`, result);
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
                    throw new Error(`Invalid argument at position ${i} for method ${propertyKey}: ${errorMessage}`);
                }
            }
            
            return originalMethod.apply(this, args);
        };
        
        return descriptor;
    };
}

// 缓存装饰器工厂，可配置缓存策略
function Cache(options: { ttl?: number; keyGenerator?: (...args: any[]) => string } = {}) {
    const { ttl = 60000, keyGenerator } = options;
    
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        const cache = new Map<string, { value: any; timestamp: number }>();
        
        descriptor.value = function(...args: any[]) {
            const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
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

// 重试装饰器工厂，可配置重试策略
function Retry(options: {
    maxAttempts?: number;
    delay?: number;
    backoff?: "linear" | "exponential";
    shouldRetry?: (error: Error) => boolean;
} = {}) {
    const {
        maxAttempts = 3,
        delay = 1000,
        backoff = "linear",
        shouldRetry = () => true
    } = options;
    
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
                    
                    // 检查是否应该重试
                    if (!shouldRetry(lastError) || attempt >= maxAttempts) {
                        throw lastError;
                    }
                    
                    // 计算延迟时间
                    let currentDelay = delay;
                    if (backoff === "exponential") {
                        currentDelay = delay * Math.pow(2, attempt - 1);
                    }
                    
                    await new Promise(resolve => setTimeout(resolve, currentDelay));
                }
            }
            
            throw lastError;
        };
        
        return descriptor;
    };
}

// 权限检查装饰器工厂
function RequirePermission(permission: string, options: { allowAdmin?: boolean } = {}) {
    const { allowAdmin = true } = options;
    
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            const userPermissions = (this as any).permissions || [];
            const userRole = (this as any).role || "";
            
            // 管理员拥有所有权限
            if (allowAdmin && userRole === "admin") {
                return originalMethod.apply(this, args);
            }
            
            if (!userPermissions.includes(permission)) {
                throw new Error(`Permission '${permission}' required to access ${propertyKey}`);
            }
            
            return originalMethod.apply(this, args);
        };
        
        return descriptor;
    };
}

// 防抖装饰器工厂，可配置防抖策略
function Debounce(options: { delay?: number; immediate?: boolean; leading?: boolean } = {}) {
    const { delay = 300, immediate = false, leading = false } = options;
    
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let timeoutId: NodeJS.Timeout;
        let result: any;
        
        descriptor.value = function(...args: any[]) {
            const callNow = immediate && !timeoutId;
            
            // 如果是leading模式，确保在防抖期间的第一次调用立即执行
            if (leading && !timeoutId) {
                result = originalMethod.apply(this, args);
            }
            
            clearTimeout(timeoutId);
            
            timeoutId = setTimeout(() => {
                timeoutId = undefined;
                
                // 如果不是immediate或leading模式，则正常执行
                if (!immediate && !leading) {
                    result = originalMethod.apply(this, args);
                }
            }, delay);
            
            // immediate模式，如果已经有timer，则返回上一次的结果
            if (callNow) {
                return result;
            }
        };
        
        return descriptor;
    };
}

// 节流装饰器工厂，可配置节流策略
function Throttle(options: { delay?: number; trailing?: boolean; leading?: boolean } = {}) {
    const { delay = 300, trailing = true, leading = true } = options;
    
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        let lastCall = 0;
        let timeoutId: NodeJS.Timeout;
        let result: any;
        
        descriptor.value = function(...args: any[]) {
            const now = Date.now();
            const shouldCall = now - lastCall >= delay;
            
            // leading模式，确保第一次调用立即执行
            if (leading && shouldCall) {
                lastCall = now;
                result = originalMethod.apply(this, args);
            }
            
            // trailing模式，确保在节流期间结束后执行最后一次调用
            if (trailing && !timeoutId) {
                timeoutId = setTimeout(() => {
                    timeoutId = undefined;
                    if (!leading) {
                        result = originalMethod.apply(this, args);
                    }
                }, delay - (now - lastCall));
            }
            
            return result;
        };
        
        return descriptor;
    };
}

// 使用装饰器工厂的示例类
@AddProperty("version", "1.0.0")
class APIClient {
    @Loggable("debug")
    @Cache({ ttl: 5000, keyGenerator: (endpoint: string, params: any) => `${endpoint}:${JSON.stringify(params)}` })
    @Retry({ 
        maxAttempts: 3, 
        delay: 1000, 
        backoff: "exponential",
        shouldRetry: (error) => (error as any).status >= 500
    })
    async fetch(endpoint: string, params: any = {}): Promise<any> {
        console.log(`Fetching ${endpoint} with params:`, params);
        
        // 模拟API调用
        if (Math.random() < 0.3) {
            throw new Error("Network error");
        }
        
        return { data: `Response from ${endpoint}`, params };
    }
    
    @Loggable("info")
    @Validate(
        (value: any) => typeof value === "string" && value.trim().length > 0,
        "URL must be a non-empty string"
    )
    postData(url: string, data: any): any {
        console.log(`Posting data to ${url}:`, data);
        return { success: true, url, data };
    }
    
    @RequirePermission("admin", { allowAdmin: true })
    @Loggable("error")
    deleteData(resourceId: string): any {
        console.log(`Deleting resource: ${resourceId}`);
        return { success: true, deletedId: resourceId };
    }
    
    @Debounce({ delay: 500, immediate: false, leading: false })
    @Loggable("info")
    search(query: string): void {
        console.log(`Searching for: ${query}`);
    }
    
    @Throttle({ delay: 1000, trailing: true, leading: true })
    @Loggable("info")
    trackEvent(eventName: string, data: any = {}): void {
        console.log(`Tracking event: ${eventName} with data:`, data);
    }
}

// 用户类，用于测试权限装饰器
class User {
    constructor(
        public role: string,
        public permissions: string[]
    ) {}
}

// 测试装饰器工厂
async function testDecoratorFactories() {
    console.log("=== Testing Decorator Factories ===");
    
    const apiClient = new APIClient() as any;
    
    // 测试添加的属性
    console.log("API client version:", apiClient.version);
    
    // 测试缓存
    console.log("\n=== Testing cache decorator ===");
    await apiClient.fetch("/users", { page: 1 });
    await apiClient.fetch("/users", { page: 1 }); // 应该使用缓存
    await apiClient.fetch("/users", { page: 2 }); // 新请求，不应该使用缓存
    
    // 测试重试
    console.log("\n=== Testing retry decorator ===");
    try {
        await apiClient.fetch("/unstable", {});
    } catch (error) {
        console.log("Final error after retries:", (error as Error).message);
    }
    
    // 测试验证
    console.log("\n=== Testing validate decorator ===");
    try {
        apiClient.postData("https://api.example.com/data", { name: "Test" });
    } catch (error) {
        console.log("Validation error:", (error as Error).message);
    }
    
    try {
        apiClient.postData("", { name: "Test" });
    } catch (error) {
        console.log("Validation error:", (error as Error).message);
    }
    
    // 测试权限
    console.log("\n=== Testing permission decorator ===");
    
    // 创建管理员用户
    const adminUser = new User("admin", ["read", "write"]);
    const adminClient = Object.assign(apiClient, adminUser);
    
    try {
        adminClient.deleteData("123");
    } catch (error) {
        console.log("Admin should not get error");
    }
    
    // 创建普通用户
    const regularUser = new User("user", ["read"]);
    const regularClient = Object.assign(apiClient, regularUser);
    
    try {
        regularClient.deleteData("123");
    } catch (error) {
        console.log("Regular user should get error:", (error as Error).message);
    }
    
    // 测试防抖
    console.log("\n=== Testing debounce decorator ===");
    apiClient.search("TypeScript");
    apiClient.search("JavaScript"); // 应该被防抖
    apiClient.search("Decorators"); // 应该被防抖
    
    setTimeout(() => {
        apiClient.search("Async"); // 应该在500ms后执行
    }, 600);
    
    // 测试节流
    console.log("\n=== Testing throttle decorator ===");
    apiClient.trackEvent("page_view", { page: "home" });
    apiClient.trackEvent("page_view", { page: "about" }); // 应该被节流
    apiClient.trackEvent("button_click", { button: "submit" }); // 应该被节流
    
    setTimeout(() => {
        apiClient.trackEvent("page_view", { page: "contact" }); // 应该在1秒后执行
    }, 1100);
}

// 执行测试
testDecoratorFactories().then(() => {
    console.log("\nDecorator factories demo completed!");
});