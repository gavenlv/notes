// 动态导入示例
import { Logger, LogLevel } from './logger';
import type { User, CreateUserRequest, UpdateUserRequest } from './user';

// 模拟一个重度计算模块
// heavy-module.ts
interface HeavyModule {
    expensiveComputation(n: number): number;
    fibonacci(n: number): number;
    factorial(n: number): number;
}

// locale-strings.ts
interface LocaleStrings {
    greeting: string;
    farewell: string;
    thankYou: string;
    sorry: string;
    [key: string]: string;
}

// 模拟不同语言的本地化字符串
const localeData = {
    en: {
        greeting: "Hello",
        farewell: "Goodbye",
        thankYou: "Thank you",
        sorry: "Sorry"
    },
    zh: {
        greeting: "你好",
        farewell: "再见",
        thankYou: "谢谢",
        sorry: "对不起"
    },
    es: {
        greeting: "Hola",
        farewell: "Adiós",
        thankYou: "Gracias",
        sorry: "Lo siento"
    },
    fr: {
        greeting: "Bonjour",
        farewell: "Au revoir",
        thankYou: "Merci",
        sorry": "Désolé"
    }
};

// 模拟路由组件
interface RouteComponent {
    render(): string;
    cleanup?(): void;
}

class NotFoundComponent implements RouteComponent {
    render(): string {
        return "404 - Page Not Found";
    }
}

class HomeComponent implements RouteComponent {
    render(): string {
        return "Welcome to our website!";
    }
}

class AboutComponent implements RouteComponent {
    render(): string {
        return "About Us: We are a company that values quality and innovation.";
    }
}

class ContactComponent implements RouteComponent {
    render(): string {
        return "Contact Us: Email us at contact@example.com or call 123-456-7890";
    }
}

class DashboardComponent implements RouteComponent {
    private data?: any;
    
    constructor() {
        this.loadData();
    }
    
    private async loadData(): Promise<void> {
        // 模拟异步数据加载
        await new Promise(resolve => setTimeout(resolve, 1000));
        this.data = {
            users: 100,
            orders: 250,
            revenue: 12500
        };
    }
    
    render(): string {
        if (!this.data) {
            return "Loading dashboard...";
        }
        
        return `Dashboard: ${this.data.users} users, ${this.data.orders} orders, $${this.data.revenue} revenue`;
    }
    
    cleanup(): void {
        this.data = undefined;
    }
}

class ProfileComponent implements RouteComponent {
    constructor(private userId: string) {}
    
    async loadUserData(): Promise<{ name: string; email: string; joinDate: Date }> {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 模拟用户数据
        return {
            name: `User ${this.userId}`,
            email: `user${this.userId}@example.com`,
            joinDate: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000) // 1年前
        };
    }
    
    async render(): Promise<string> {
        const userData = await this.loadUserData();
        return `Profile: ${userData.name}, ${userData.email}, Joined: ${userData.joinDate.toDateString()}`;
    }
}

// 测试基本动态导入
async function testBasicDynamicImport() {
    console.log("=== Testing Basic Dynamic Import ===");
    
    // 动态导入重度计算模块
    console.log("Loading heavy module...");
    const heavyModule = await import('./heavy-module') as HeavyModule;
    
    console.log("Heavy module loaded!");
    console.log(`Expensive computation result: ${heavyModule.expensiveComputation(100)}`);
    console.log(`Fibonacci(20): ${heavyModule.fibonacci(20)}`);
    console.log(`Factorial(10): ${heavyModule.factorial(10)}`);
}

// 测试条件动态导入
async function testConditionalDynamicImport() {
    console.log("\n=== Testing Conditional Dynamic Import ===");
    
    const locales = ["en", "zh", "es", "fr"];
    const selectedLocale = locales[Math.floor(Math.random() * locales.length)];
    
    console.log(`Selected locale: ${selectedLocale}`);
    
    // 根据条件动态导入不同的本地化字符串
    let localeStrings: LocaleStrings;
    
    switch (selectedLocale) {
        case "en":
            localeStrings = localeData.en;
            break;
        case "zh":
            localeStrings = localeData.zh;
            break;
        case "es":
            localeStrings = localeData.es;
            break;
        case "fr":
            localeStrings = localeData.fr;
            break;
        default:
            localeStrings = localeData.en;
    }
    
    console.log(`Greeting: ${localeStrings.greeting}`);
    console.log(`Farewell: ${localeStrings.farewell}`);
    console.log(`Thank you: ${localeStrings.thankYou}`);
    console.log(`Sorry: ${localeStrings.sorry}`);
}

// 测试路由懒加载
async function testRouteLazyLoading() {
    console.log("\n=== Testing Route Lazy Loading ===");
    
    // 模拟路由配置
    const routes = [
        { path: "/", component: () => Promise.resolve(new HomeComponent()) },
        { path: "/about", component: () => Promise.resolve(new AboutComponent()) },
        { path: "/contact", component: () => Promise.resolve(new ContactComponent()) },
        { 
            path: "/dashboard", 
            component: () => Promise.resolve(new DashboardComponent()),
            preload: true // 预加载
        },
        { 
            path: "/profile/:id", 
            component: (id: string) => Promise.resolve(new ProfileComponent(id)) 
        }
    ];
    
    // 模拟导航到不同路由
    const navigationPaths = ["/", "/about", "/contact", "/dashboard", "/profile/123"];
    
    for (const path of navigationPaths) {
        console.log(`Navigating to: ${path}`);
        
        const route = routes.find(r => {
            if (r.path === "/profile/:id") {
                return path.startsWith("/profile/");
            }
            return r.path === path;
        });
        
        if (!route) {
            const component = new NotFoundComponent();
            console.log(component.render());
            continue;
        }
        
        let component: RouteComponent;
        
        if (route.path === "/profile/:id") {
            const id = path.split("/").pop() || "";
            component = await route.component(id);
        } else {
            component = await route.component();
        }
        
        // 检查组件是否有异步render方法
        if (component.render.constructor.name === "AsyncFunction") {
            const renderResult = await (component.render as () => Promise<string>)();
            console.log(renderResult);
        } else {
            console.log(component.render());
        }
        
        // 调用清理方法
        if (component.cleanup) {
            component.cleanup();
        }
    }
}

// 测试插件系统
async function testPluginSystem() {
    console.log("\n=== Testing Plugin System ===");
    
    interface Plugin {
        name: string;
        version: string;
        init(): void;
        execute(data: any): any;
        destroy?(): void;
    }
    
    // 模拟插件
    const availablePlugins: Record<string, () => Promise<Plugin>> = {
        logger: async () => {
            const logger = new Logger(LogLevel.INFO);
            
            return {
                name: "Logger Plugin",
                version: "1.0.0",
                init() {
                    logger.info("Logger plugin initialized");
                },
                execute(data: any) {
                    logger.info("Plugin execution:", data);
                    return data;
                },
                destroy() {
                    logger.info("Logger plugin destroyed");
                }
            };
        },
        
        validator: async () => {
            return {
                name: "Validator Plugin",
                version: "1.0.0",
                init() {
                    console.log("Validator plugin initialized");
                },
                execute(data: any) {
                    if (!data || typeof data !== "object") {
                        throw new Error("Invalid data: must be an object");
                    }
                    
                    if (!data.id || typeof data.id !== "string") {
                        throw new Error("Invalid data: id must be a string");
                    }
                    
                    return data;
                },
                destroy() {
                    console.log("Validator plugin destroyed");
                }
            };
        },
        
        transformer: async () => {
            return {
                name: "Transformer Plugin",
                version: "1.0.0",
                init() {
                    console.log("Transformer plugin initialized");
                },
                execute(data: any) {
                    if (typeof data === "object" && data !== null) {
                        // 添加时间戳
                        return {
                            ...data,
                            timestamp: new Date().toISOString(),
                            transformed: true
                        };
                    }
                    
                    return data;
                },
                destroy() {
                    console.log("Transformer plugin destroyed");
                }
            };
        }
    };
    
    // 动态加载和使用插件
    const pluginNames = ["logger", "validator", "transformer"];
    const loadedPlugins: Plugin[] = [];
    
    try {
        for (const pluginName of pluginNames) {
            console.log(`Loading plugin: ${pluginName}`);
            
            // 动态加载插件
            const pluginFactory = availablePlugins[pluginName];
            if (!pluginFactory) {
                console.error(`Plugin ${pluginName} not found`);
                continue;
            }
            
            const plugin = await pluginFactory();
            
            // 初始化插件
            plugin.init();
            
            loadedPlugins.push(plugin);
        }
        
        // 使用插件处理数据
        const testData = { id: "12345", name: "Test Data" };
        
        let processedData = testData;
        
        for (const plugin of loadedPlugins) {
            console.log(`Executing plugin: ${plugin.name}`);
            processedData = plugin.execute(processedData);
        }
        
        console.log("Final processed data:", processedData);
        
    } finally {
        // 清理插件
        for (const plugin of loadedPlugins) {
            if (plugin.destroy) {
                plugin.destroy();
            }
        }
    }
}

// 测试模块热重载模拟
async function testModuleHotReload() {
    console.log("\n=== Testing Module Hot Reload Simulation ===");
    
    // 模拟模块版本
    interface ModuleInfo {
        version: number;
        loadTime: Date;
        content: any;
    }
    
    const moduleCache = new Map<string, ModuleInfo>();
    
    // 模拟动态加载模块
    async function loadModule<T>(moduleName: string, moduleFactory: () => Promise<T>): Promise<T> {
        // 检查模块是否已缓存
        if (moduleCache.has(moduleName)) {
            const cachedModule = moduleCache.get(moduleName)!;
            console.log(`Loading ${moduleName} from cache (version ${cachedModule.version})`);
            return cachedModule.content;
        }
        
        // 加载新模块
        console.log(`Loading ${moduleName} from disk`);
        const moduleContent = await moduleFactory();
        
        // 缓存模块
        moduleCache.set(moduleName, {
            version: 1,
            loadTime: new Date(),
            content: moduleContent
        });
        
        return moduleContent;
    }
    
    // 模拟模块更新
    async function updateModule<T>(moduleName: string, moduleFactory: () => Promise<T>): Promise<T> {
        console.log(`Updating module: ${moduleName}`);
        
        // 模拟模块更新
        const moduleContent = await moduleFactory();
        
        // 更新缓存
        const currentVersion = moduleCache.has(moduleName) 
            ? moduleCache.get(moduleName)!.version 
            : 0;
        
        moduleCache.set(moduleName, {
            version: currentVersion + 1,
            loadTime: new Date(),
            content: moduleContent
        });
        
        console.log(`Module ${moduleName} updated to version ${currentVersion + 1}`);
        return moduleContent;
    }
    
    // 模拟工具模块
    interface UtilsModule {
        formatDate(date: Date): string;
        capitalize(str: string): string;
        random(min: number, max: number): number;
    }
    
    let utilsModuleVersion = 0;
    
    const createUtilsModule = async (): Promise<UtilsModule> => {
        utilsModuleVersion++;
        
        return {
            formatDate(date: Date): string {
                return date.toISOString().split('T')[0]; // 版本1的格式
            },
            
            capitalize(str: string): string {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
            
            random(min: number, max: number): number {
                return Math.floor(Math.random() * (max - min + 1)) + min;
            },
            
            // 添加版本信息
            version: utilsModuleVersion
        } as any;
    };
    
    // 加载和使用模块
    const utils1 = await loadModule("utils", createUtilsModule);
    console.log("Date format:", utils1.formatDate(new Date()));
    console.log("Capitalized:", utils1.capitalize("hello world"));
    console.log("Random number:", utils1.random(1, 10));
    console.log("Module version:", (utils1 as any).version);
    
    // 模拟模块更新
    setTimeout(async () => {
        console.log("\nModule update occurred!");
        
        const utils2 = await updateModule("utils", createUtilsModule);
        console.log("Updated date format:", utils2.formatDate(new Date()));
        console.log("Updated capitalized:", utils2.capitalize("hello world"));
        console.log("Updated random number:", utils2.random(1, 10));
        console.log("Updated module version:", (utils2 as any).version);
    }, 2000);
}

// 测试类型安全的动态导入
async function testTypedDynamicImports() {
    console.log("\n=== Testing Typed Dynamic Imports ===");
    
    // 为动态导入添加类型注解
    const typedImport = async <T>(modulePath: string): Promise<T> => {
        const module = await import(modulePath) as any;
        return module.default || module;
    };
    
    // 使用类型化动态导入
    try {
        // 导入用户服务
        const UserService = await typedImport<typeof import('./user')>('./user-service');
        
        const logger = new Logger(LogLevel.INFO);
        const userService = new UserService(logger);
        
        const userData: CreateUserRequest = {
            name: "John Doe",
            email: "john.doe@example.com"
        };
        
        const createdUser = userService.create(userData);
        console.log("Created user:", createdUser);
        
        // 导入用户仓库
        const UserRepository = await typedImport<typeof import('./user')>('./user-repository');
        const userRepository = new UserRepository();
        
        const userFromRepo = userRepository.findById(createdUser.id);
        console.log("User from repository:", userFromRepo);
        
    } catch (error) {
        console.error("Error in typed dynamic import:", error);
    }
}

// 测试动态导入的性能
async function testDynamicImportPerformance() {
    console.log("\n=== Testing Dynamic Import Performance ===");
    
    const iterations = 100;
    const results: number[] = [];
    
    for (let i = 0; i < iterations; i++) {
        const startTime = performance.now();
        
        // 动态导入一个简单模块
        await import('./math');
        
        const endTime = performance.now();
        results.push(endTime - startTime);
    }
    
    const averageTime = results.reduce((sum, time) => sum + time, 0) / results.length;
    const minTime = Math.min(...results);
    const maxTime = Math.max(...results);
    
    console.log(`Average dynamic import time: ${averageTime.toFixed(2)}ms`);
    console.log(`Min dynamic import time: ${minTime.toFixed(2)}ms`);
    console.log(`Max dynamic import time: ${maxTime.toFixed(2)}ms`);
    
    // 比较静态导入
    const staticImportStartTime = performance.now();
    
    for (let i = 0; i < iterations; i++) {
        // 模拟使用静态导入的内容
        const result = Math.random() * 100;
    }
    
    const staticImportEndTime = performance.now();
    const staticImportTime = staticImportEndTime - staticImportStartTime;
    
    console.log(`Static import time for ${iterations} iterations: ${staticImportTime.toFixed(2)}ms`);
    console.log(`Average static import time per iteration: ${(staticImportTime / iterations).toFixed(4)}ms`);
}

// 执行所有测试
async function runAllTests() {
    await testBasicDynamicImport();
    await testConditionalDynamicImport();
    await testRouteLazyLoading();
    await testPluginSystem();
    await testModuleHotReload();
    await testTypedDynamicImports();
    await testDynamicImportPerformance();
}

// 导出测试函数供外部使用
export {
    testBasicDynamicImport,
    testConditionalDynamicImport,
    testRouteLazyLoading,
    testPluginSystem,
    testModuleHotReload,
    testTypedDynamicImports,
    testDynamicImportPerformance,
    runAllTests
};

// 如果直接运行此文件，执行所有测试
if (require.main === module) {
    runAllTests();
}