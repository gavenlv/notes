// 命名空间示例

// 基本命名空间
namespace Geometry {
    export interface Point {
        x: number;
        y: number;
    }
    
    export interface Circle {
        center: Point;
        radius: number;
    }
    
    export interface Rectangle {
        topLeft: Point;
        bottomRight: Point;
    }
    
    export interface Triangle {
        vertices: [Point, Point, Point];
    }
    
    export function distance(p1: Point, p2: Point): number {
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    export function circleArea(circle: Circle): number {
        return Math.PI * circle.radius * circle.radius;
    }
    
    export function rectangleArea(rectangle: Rectangle): number {
        const width = rectangle.bottomRight.x - rectangle.topLeft.x;
        const height = rectangle.bottomRight.y - rectangle.topLeft.y;
        return width * height;
    }
    
    export function triangleArea(triangle: Triangle): number {
        const [p1, p2, p3] = triangle.vertices;
        return Math.abs(
            (p1.x * (p2.y - p3.y) + 
             p2.x * (p3.y - p1.y) + 
             p3.x * (p1.y - p2.y)) / 2
        );
    }
    
    // 嵌套命名空间
    namespace Shapes {
        export class Triangle {
            constructor(public vertices: Geometry.Point[]) {
                if (vertices.length !== 3) {
                    throw new Error("A triangle must have exactly 3 vertices");
                }
            }
            
            area(): number {
                const [p1, p2, p3] = this.vertices as [Geometry.Point, Geometry.Point, Geometry.Point];
                return Math.abs(
                    (p1.x * (p2.y - p3.y) + 
                     p2.x * (p3.y - p1.y) + 
                     p3.x * (p1.y - p2.y)) / 2
                );
            }
            
            perimeter(): number {
                let perimeter = 0;
                for (let i = 0; i < 3; i++) {
                    const p1 = this.vertices[i];
                    const p2 = this.vertices[(i + 1) % 3];
                    perimeter += Geometry.distance(p1, p2);
                }
                return perimeter;
            }
        }
        
        export class Quadrilateral {
            constructor(public vertices: Geometry.Point[]) {
                if (vertices.length !== 4) {
                    throw new Error("A quadrilateral must have exactly 4 vertices");
                }
            }
            
            area(): number {
                const [p1, p2, p3, p4] = this.vertices as [
                    Geometry.Point, Geometry.Point, 
                    Geometry.Point, Geometry.Point
                ];
                
                // 使用鞋带公式计算面积
                return Math.abs(
                    (p1.x * p2.y + p2.x * p3.y + p3.x * p4.y + p4.x * p1.y) -
                    (p1.y * p2.x + p2.y * p3.x + p3.y * p4.x + p4.y * p1.x)
                ) / 2;
            }
            
            perimeter(): number {
                let perimeter = 0;
                for (let i = 0; i < 4; i++) {
                    const p1 = this.vertices[i];
                    const p2 = this.vertices[(i + 1) % 4];
                    perimeter += Geometry.distance(p1, p2);
                }
                return perimeter;
            }
        }
    }
}

// 数学命名空间
namespace Math {
    export const PI = 3.141592653589793;
    export const E = 2.718281828459045;
    
    export function add(a: number, b: number): number {
        return a + b;
    }
    
    export function subtract(a: number, b: number): number {
        return a - b;
    }
    
    export function multiply(a: number, b: number): number {
        return a * b;
    }
    
    export function divide(a: number, b: number): number {
        if (b === 0) {
            throw new Error("Division by zero");
        }
        return a / b;
    }
    
    export function power(base: number, exponent: number): number {
        return Math.pow(base, exponent);
    }
    
    export function sqrt(value: number): number {
        if (value < 0) {
            throw new Error("Square root of negative number");
        }
        return Math.sqrt(value);
    }
    
    export function factorial(n: number): number {
        if (n < 0) {
            throw new Error("Factorial of negative number");
        }
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    
    export function fibonacci(n: number): number {
        if (n < 0) {
            throw new Error("Fibonacci of negative number");
        }
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    export function gcd(a: number, b: number): number {
        a = Math.abs(a);
        b = Math.abs(b);
        return b === 0 ? a : gcd(b, a % b);
    }
    
    export function lcm(a: number, b: number): number {
        return Math.abs(a * b) / gcd(a, b);
    }
    
    export class Calculator {
        private result: number = 0;
        
        add(value: number): Calculator {
            this.result += value;
            return this;
        }
        
        subtract(value: number): Calculator {
            this.result -= value;
            return this;
        }
        
        multiply(value: number): Calculator {
            this.result *= value;
            return this;
        }
        
        divide(value: number): Calculator {
            if (value === 0) {
                throw new Error("Division by zero");
            }
            this.result /= value;
            return this;
        }
        
        power(exponent: number): Calculator {
            this.result = Math.pow(this.result, exponent);
            return this;
        }
        
        sqrt(): Calculator {
            if (this.result < 0) {
                throw new Error("Square root of negative number");
            }
            this.result = Math.sqrt(this.result);
            return this;
        }
        
        getResult(): number {
            return this.result;
        }
        
        reset(): Calculator {
            this.result = 0;
            return this;
        }
    }
    
    // 嵌套命名空间用于数学公式
    namespace Formulas {
        export function quadraticEquation(a: number, b: number, c: number): number[] {
            if (a === 0) {
                throw new Error("Coefficient a cannot be 0");
            }
            
            const discriminant = b * b - 4 * a * c;
            
            if (discriminant < 0) {
                return []; // 无实数根
            } else if (discriminant === 0) {
                return [-b / (2 * a)]; // 一个实数根
            } else {
                const sqrtDiscriminant = Math.sqrt(discriminant);
                return [
                    (-b + sqrtDiscriminant) / (2 * a),
                    (-b - sqrtDiscriminant) / (2 * a)
                ]; // 两个实数根
            }
        }
        
        export function circleCircumference(radius: number): number {
            return 2 * PI * radius;
        }
        
        export function circleArea(radius: number): number {
            return PI * radius * radius;
        }
        
        export function sphereSurfaceArea(radius: number): number {
            return 4 * PI * radius * radius;
        }
        
        export function sphereVolume(radius: number): number {
            return (4 / 3) * PI * Math.pow(radius, 3);
        }
        
        export function pythagorean(a: number, b: number): number {
            return Math.sqrt(a * a + b * b);
        }
    }
}

// 日志命名空间
namespace Logger {
    export enum LogLevel {
        DEBUG = 0,
        INFO = 1,
        WARN = 2,
        ERROR = 3
    }
    
    export interface LogEntry {
        level: LogLevel;
        message: string;
        timestamp: Date;
        context?: any;
    }
    
    export class Logger {
        private logLevel: LogLevel = LogLevel.INFO;
        private logs: LogEntry[] = [];
        private maxLogEntries = 1000;
        
        constructor(logLevel?: LogLevel, maxLogEntries?: number) {
            if (logLevel !== undefined) {
                this.logLevel = logLevel;
            }
            
            if (maxLogEntries !== undefined) {
                this.maxLogEntries = maxLogEntries;
            }
        }
        
        private log(level: LogLevel, message: string, context?: any): void {
            if (level < this.logLevel) {
                return;
            }
            
            const logEntry: LogEntry = {
                level,
                message,
                timestamp: new Date(),
                context
            };
            
            this.addLog(logEntry);
            this.outputLog(logEntry);
        }
        
        private addLog(logEntry: LogEntry): void {
            this.logs.push(logEntry);
            
            // 限制日志条目数量
            if (this.logs.length > this.maxLogEntries) {
                this.logs = this.logs.slice(-this.maxLogEntries);
            }
        }
        
        private outputLog(logEntry: LogEntry): void {
            const levelString = LogLevel[logEntry.level];
            const timestamp = logEntry.timestamp.toISOString();
            
            let output = `[${timestamp}] [${levelString}] ${logEntry.message}`;
            
            if (logEntry.context) {
                output += ` ${JSON.stringify(logEntry.context)}`;
            }
            
            switch (logEntry.level) {
                case LogLevel.DEBUG:
                    console.debug(output);
                    break;
                case LogLevel.INFO:
                    console.info(output);
                    break;
                case LogLevel.WARN:
                    console.warn(output);
                    break;
                case LogLevel.ERROR:
                    console.error(output);
                    break;
            }
        }
        
        debug(message: string, context?: any): void {
            this.log(LogLevel.DEBUG, message, context);
        }
        
        info(message: string, context?: any): void {
            this.log(LogLevel.INFO, message, context);
        }
        
        warn(message: string, context?: any): void {
            this.log(LogLevel.WARN, message, context);
        }
        
        error(message: string, context?: any): void {
            this.log(LogLevel.ERROR, message, context);
        }
        
        setLogLevel(level: LogLevel): void {
            this.logLevel = level;
        }
        
        getLogs(level?: LogLevel): LogEntry[] {
            if (level === undefined) {
                return [...this.logs];
            }
            
            return this.logs.filter(log => log.level === level);
        }
        
        clearLogs(): void {
            this.logs = [];
        }
        
        exportLogs(): LogEntry[] {
            return [...this.logs];
        }
    }
}

// 测试命名空间功能
function testGeometryNamespace() {
    console.log("=== Testing Geometry Namespace ===");
    
    // 使用基本几何功能
    const point1: Geometry.Point = { x: 0, y: 0 };
    const point2: Geometry.Point = { x: 3, y: 4 };
    
    console.log(`Distance between points: ${Geometry.distance(point1, point2)}`);
    
    const circle: Geometry.Circle = { center: point1, radius: 5 };
    console.log(`Circle area: ${Geometry.circleArea(circle)}`);
    
    // 使用嵌套命名空间
    const triangle = new Geometry.Shapes.Triangle([
        { x: 0, y: 0 },
        { x: 4, y: 0 },
        { x: 0, y: 3 }
    ]);
    
    console.log(`Triangle area: ${triangle.area()}`);
    console.log(`Triangle perimeter: ${triangle.perimeter()}`);
    
    const quadrilateral = new Geometry.Shapes.Quadrilateral([
        { x: 0, y: 0 },
        { x: 4, y: 0 },
        { x: 4, y: 3 },
        { x: 0, y: 3 }
    ]);
    
    console.log(`Quadrilateral area: ${quadrilateral.area()}`);
    console.log(`Quadrilateral perimeter: ${quadrilateral.perimeter()}`);
}

function testMathNamespace() {
    console.log("\n=== Testing Math Namespace ===");
    
    // 使用基本数学功能
    console.log(`PI: ${Math.PI}`);
    console.log(`E: ${Math.E}`);
    console.log(`add(5, 3): ${Math.add(5, 3)}`);
    console.log(`factorial(5): ${Math.factorial(5)}`);
    console.log(`fibonacci(10): ${Math.fibonacci(10)}`);
    
    // 使用计算器类
    const calc = new Math.Calculator();
    console.log(`Chain calculation: ${calc.add(10).multiply(2).subtract(5).getResult()}`);
    
    // 使用嵌套命名空间中的公式
    const roots = Math.Formulas.quadraticEquation(1, -5, 6);
    console.log(`Quadratic equation roots: ${roots}`);
    
    console.log(`Circle circumference (r=5): ${Math.Formulas.circleCircumference(5)}`);
    console.log(`Circle area (r=5): ${Math.Formulas.circleArea(5)}`);
    console.log(`Pythagorean theorem (3,4): ${Math.Formulas.pythagorean(3, 4)}`);
}

function testLoggerNamespace() {
    console.log("\n=== Testing Logger Namespace ===");
    
    const logger = new Logger(Logger.LogLevel.DEBUG);
    
    logger.debug("This is a debug message");
    logger.info("This is an info message");
    logger.warn("This is a warning message");
    logger.error("This is an error message");
    
    // 设置不同的日志级别
    logger.setLogLevel(Logger.LogLevel.WARN);
    
    console.log("\nAfter setting log level to WARN:");
    
    logger.debug("This debug message won't be shown");
    logger.info("This info message won't be shown");
    logger.warn("This warning will be shown");
    logger.error("This error will be shown");
    
    // 获取日志
    const allLogs = logger.getLogs();
    console.log(`Total logs: ${allLogs.length}`);
    
    const errorLogs = logger.getLogs(Logger.LogLevel.ERROR);
    console.log(`Error logs: ${errorLogs.length}`);
}

// 命名空间别名
type GeoPoint = Geometry.Point;
type GeoCircle = Geometry.Circle;
const mathPI = Math.PI;
const LogLevel = Logger.LogLevel;

function testNamespaceAliases() {
    console.log("\n=== Testing Namespace Aliases ===");
    
    const point: GeoPoint = { x: 1, y: 1 };
    const circle: GeoCircle = { center: point, radius: 3 };
    
    console.log(`Circle area: ${Geometry.circleArea(circle)}`);
    console.log(`PI value from alias: ${mathPI}`);
    console.log(`LogLevel from alias: ${LogLevel.DEBUG}`);
}

// 全局命名空间扩展
// 扩展String接口
declare global {
    interface String {
        toPascalCase(): string;
        toCamelCase(): string;
        toSnakeCase(): string;
        toKebabCase(): string;
    }
}

String.prototype.toPascalCase = function(): string {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

String.prototype.toCamelCase = function(): string {
    return this.charAt(0).toLowerCase() + this.slice(1);
};

String.prototype.toSnakeCase = function(): string {
    return this.replace(/([A-Z])/g, '_$1').toLowerCase();
};

String.prototype.toKebabCase = function(): string {
    return this.replace(/([A-Z])/g, '-$1').toLowerCase();
};

function testGlobalNamespaceExtension() {
    console.log("\n=== Testing Global Namespace Extension ===");
    
    const pascal = "helloWorld".toPascalCase();
    console.log(`"helloWorld".toPascalCase(): "${pascal}"`);
    
    const camel = "HelloWorld".toCamelCase();
    console.log(`"HelloWorld".toCamelCase(): "${camel}"`);
    
    const snake = "HelloWorld".toSnakeCase();
    console.log(`"HelloWorld".toSnakeCase(): "${snake}"`);
    
    const kebab = "HelloWorld".toKebabCase();
    console.log(`"HelloWorld".toKebabCase(): "${kebab}"`);
}

// 执行所有测试
function runAllTests() {
    testGeometryNamespace();
    testMathNamespace();
    testLoggerNamespace();
    testNamespaceAliases();
    testGlobalNamespaceExtension();
}

// 导出测试函数供外部使用
export {
    testGeometryNamespace,
    testMathNamespace,
    testLoggerNamespace,
    testNamespaceAliases,
    testGlobalNamespaceExtension,
    runAllTests
};

// 如果直接运行此文件，执行所有测试
if (require.main === module) {
    runAllTests();
}