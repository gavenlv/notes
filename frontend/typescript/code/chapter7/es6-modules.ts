// ES6模块示例

// math.ts
// 命名导出
export const PI = 3.14159;

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
    
    getResult(): number {
        return this.result;
    }
    
    reset(): Calculator {
        this.result = 0;
        return this;
    }
}

// 可以在导出前定义，然后单独导出
function power(base: number, exponent: number): number {
    return Math.pow(base, exponent);
}

// 重命名导出
export { power as pow };

// 默认导出
export default class ScientificCalculator {
    static factorial(n: number): number {
        if (n <= 1) return 1;
        return n * ScientificCalculator.factorial(n - 1);
    }
    
    static fibonacci(n: number): number {
        if (n <= 1) return n;
        return ScientificCalculator.fibonacci(n - 1) + ScientificCalculator.fibonacci(n - 2);
    }
    
    static gcd(a: number, b: number): number {
        return b === 0 ? a : ScientificCalculator.gcd(b, a % b);
    }
    
    static lcm(a: number, b: number): number {
        return (a * b) / ScientificCalculator.gcd(a, b);
    }
}

// geometry.ts
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
    return PI * circle.radius * circle.radius;
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

// logger.ts
export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

export class Logger {
    constructor(private logLevel: LogLevel = LogLevel.INFO) {}
    
    debug(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.DEBUG) {
            console.debug(`[DEBUG] ${message}`, ...args);
        }
    }
    
    info(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.INFO) {
            console.info(`[INFO] ${message}`, ...args);
        }
    }
    
    warn(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.WARN) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }
    
    error(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.ERROR) {
            console.error(`[ERROR] ${message}`, ...args);
        }
    }
    
    setLogLevel(level: LogLevel): void {
        this.logLevel = level;
    }
}

// user.ts
export interface User {
    id: number;
    name: string;
    email: string;
    avatar?: string;
    createdAt: Date;
    updatedAt?: Date;
}

export interface CreateUserRequest {
    name: string;
    email: string;
    avatar?: string;
}

export interface UpdateUserRequest {
    name?: string;
    email?: string;
    avatar?: string;
}

export class UserService {
    private users: User[] = [];
    private nextId = 1;
    
    constructor(private logger: Logger) {}
    
    create(userData: CreateUserRequest): User {
        this.logger.debug(`Creating user with data:`, userData);
        
        // 检查邮箱是否已存在
        if (this.users.some(user => user.email === userData.email)) {
            throw new Error(`Email ${userData.email} already exists`);
        }
        
        const user: User = {
            id: this.nextId++,
            ...userData,
            createdAt: new Date()
        };
        
        this.users.push(user);
        this.logger.info(`User created with ID: ${user.id}`);
        
        return user;
    }
    
    findById(id: number): User | undefined {
        this.logger.debug(`Finding user with ID: ${id}`);
        return this.users.find(user => user.id === id);
    }
    
    findAll(): User[] {
        this.logger.debug("Finding all users");
        return [...this.users];
    }
    
    update(id: number, userData: UpdateUserRequest): User | undefined {
        this.logger.debug(`Updating user ${id} with data:`, userData);
        
        const userIndex = this.users.findIndex(user => user.id === id);
        
        if (userIndex === -1) {
            return undefined;
        }
        
        // 如果更新邮箱，检查邮箱是否已存在
        if (userData.email) {
            const existingUser = this.users.find(user => 
                user.email === userData.email && user.id !== id
            );
            
            if (existingUser) {
                throw new Error(`Email ${userData.email} already exists`);
            }
        }
        
        this.users[userIndex] = {
            ...this.users[userIndex],
            ...userData,
            updatedAt: new Date()
        };
        
        this.logger.info(`User updated with ID: ${id}`);
        return this.users[userIndex];
    }
    
    delete(id: number): boolean {
        this.logger.debug(`Deleting user with ID: ${id}`);
        
        const userIndex = this.users.findIndex(user => user.id === id);
        
        if (userIndex === -1) {
            return false;
        }
        
        this.users.splice(userIndex, 1);
        this.logger.info(`User deleted with ID: ${id}`);
        
        return true;
    }
}