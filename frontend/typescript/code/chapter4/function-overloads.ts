// 函数重载示例
function demonstrateFunctionOverloads(): void {
    console.log("\n=== Function Overloads Demo ===");
    
    // 基本函数重载
    function padLeft(value: string, padding: string): string;
    function padLeft(value: string, padding: number): string;
    
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
    
    // 在Node.js环境中模拟DOM操作
    // 实际使用中这些操作会在浏览器环境中执行
    console.log("Creating elements (simulated):");
    console.log("Created <a> element with href");
    console.log("Created <img> element with src");
    console.log("Created <input> element with type and name");
    console.log("Created generic element");
    
    // 数学函数重载
    function add(a: number, b: number): number;
    function add(a: string, b: string): string;
    function add(a: number[], b: number[]): number[];
    function add(a: any, b: any): any {
        if (typeof a === "number" && typeof b === "number") {
            return a + b;
        }
        if (typeof a === "string" && typeof b === "string") {
            return a + b;
        }
        if (Array.isArray(a) && Array.isArray(b)) {
            return a.concat(b);
        }
        throw new Error("Unsupported types for addition");
    }
    
    console.log(`add(5, 3): ${add(5, 3)}`);
    console.log(`add("Hello, ", "World!"): ${add("Hello, ", "World!")}`);
    console.log(`add([1, 2], [3, 4]): ${add([1, 2], [3, 4])}`);
    
    // 重载与泛型结合
    function processValue(value: string): string;
    function processValue(value: number): number;
    function processValue(value: boolean): boolean;
    function processValue<T>(value: T[]): T[];
    
    function processValue(value: any): any {
        if (typeof value === "string") {
            return value.toUpperCase();
        }
        if (typeof value === "number") {
            return value * 2;
        }
        if (typeof value === "boolean") {
            return !value;
        }
        if (Array.isArray(value)) {
            return value.slice().reverse();
        }
        return value;
    }
    
    console.log(`processValue("hello"): ${processValue("hello")}`);
    console.log(`processValue(10): ${processValue(10)}`);
    console.log(`processValue(true): ${processValue(true)}`);
    console.log(`processValue([1, 2, 3]): ${processValue([1, 2, 3])}`);
    
    // 实际应用：HTTP客户端重载
    interface RequestOptions {
        headers?: Record<string, string>;
        method?: string;
        body?: string;
    }
    
    interface HttpResponse {
        status: number;
        data: any;
    }
    
    function httpGet(url: string): Promise<HttpResponse>;
    function httpGet(url: string, options: RequestOptions): Promise<HttpResponse>;
    
    function httpGet(url: string, options?: RequestOptions): Promise<HttpResponse> {
        // 模拟HTTP GET请求
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    status: 200,
                    data: { message: `Data from ${url}` }
                });
            }, 100);
        });
    }
    
    // 使用重载的HTTP客户端
    httpGet("https://api.example.com/users").then(response => {
        console.log(`GET request status: ${response.status}`);
        console.log(`GET request data:`, response.data);
    });
    
    httpGet("https://api.example.com/users", {
        headers: { "Authorization": "Bearer token" },
        method: "GET"
    }).then(response => {
        console.log(`GET request with options status: ${response.status}`);
        console.log(`GET request with options data:`, response.data);
    });
    
    // 函数重载的最佳实践示例：安全的类型转换
    function convert(value: string): string;
    function convert(value: number): number;
    function convert(value: boolean): boolean;
    function convert(value: string | number | boolean): string | number | boolean {
        if (typeof value === "string") {
            // 尝试解析为数字，如果失败则返回原始字符串
            const parsed = parseFloat(value);
            return isNaN(parsed) ? value : parsed;
        }
        if (typeof value === "number") {
            return value;
        }
        if (typeof value === "boolean") {
            return value;
        }
        throw new Error("Unsupported type");
    }
    
    console.log(`convert("123"): ${convert("123")}`); // 123 (number)
    console.log(`convert("hello"): ${convert("hello")}`); // "hello" (string)
    console.log(`convert(42): ${convert(42)}`); // 42 (number)
    console.log(`convert(true): ${convert(true)}`); // true (boolean)
}

demonstrateFunctionOverloads();