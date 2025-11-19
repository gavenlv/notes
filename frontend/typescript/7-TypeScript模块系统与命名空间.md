# 7. TypeScript模块系统与命名空间

## 7.1 模块系统概述

TypeScript的模块系统基于ES6模块标准，提供了强大的代码组织和封装机制。模块允许将代码分割成可重用的、独立的部分，每个模块都有自己的作用域，可以通过导入和导出来共享代码。

### 7.1.1 为什么使用模块

1. **代码组织**：将相关功能组织在一起，提高代码的可维护性
2. **封装性**：每个模块有自己的作用域，避免全局命名空间污染
3. **重用性**：模块可以在多个地方重用，提高开发效率
4. **依赖管理**：明确表示模块之间的依赖关系
5. **代码分割**：支持按需加载，提高应用程序性能

### 7.1.2 模块系统的发展

JavaScript的模块系统经历了几个发展阶段：

1. **早期无模块化**：使用全局变量和立即执行函数表达式(IIFE)
2. **CommonJS**：Node.js采用的模块系统，使用`require`和`module.exports`
3. **AMD (Asynchronous Module Definition)**：RequireJS等库采用的异步模块定义
4. **UMD (Universal Module Definition)**：同时支持CommonJS和AMD的通用模块定义
5. **ES6模块**：JavaScript官方标准模块系统，使用`import`和`export`

TypeScript完全支持ES6模块语法，并可以编译为其他模块格式。

## 7.2 ES6模块

ES6模块是JavaScript的官方模块系统，TypeScript完全支持并扩展了其功能。

### 7.2.1 导出(Export)

导出允许模块将变量、函数、类等暴露给其他模块使用。

```typescript
// math.ts
// 命名导出
export const PI = 3.14159;

export function add(a: number, b: number): number {
    return a + b;
}

export class Calculator {
    multiply(a: number, b: number): number {
        return a * b;
    }
}

// 可以在导出前定义，然后单独导出
function subtract(a: number, b: number): number {
    return a - b;
}

export { subtract };

// 可以重命名导出
function divide(a: number, b: number): number {
    return a / b;
}

export { divide as div };

// 默认导出
export default class ScientificCalculator {
    power(base: number, exponent: number): number {
        return Math.pow(base, exponent);
    }
}

// 重新导出
export { PI, add } from "./math";
export * from "./geometry";
```

### 7.2.2 导入(Import)

导入允许模块使用其他模块导出的内容。

```typescript
// main.ts
// 导入命名导出
import { PI, add, Calculator } from "./math";

// 使用重命名的导入
import { subtract as sub } from "./math";

// 导入默认导出
import ScientificCalculator from "./math";

// 导入所有导出到一个命名空间对象
import * as MathModule from "./math";

// 仅导入模块
import "./styles.css";

// 使用导入的内容
console.log(PI); // 3.14159
console.log(add(2, 3)); // 5

const calc = new Calculator();
console.log(calc.multiply(4, 5)); // 20

const scientificCalc = new ScientificCalculator();
console.log(scientificCalc.power(2, 3)); // 8

console.log(sub(10, 3)); // 7

console.log(MathModule.PI); // 3.14159
const mathCalc = new MathModule.Calculator();
console.log(mathCalc.multiply(3, 4)); // 12
```

### 7.2.3 导入/导出最佳实践

1. **避免命名冲突**：使用重命名导入/导出
2. **明确导入**：避免使用`import *`，除非确实需要所有导出
3. **默认导出**：一个模块只应该有一个默认导出
4. **重导出**：使用重导出创建模块的公共API

```typescript
// api/index.ts
// 重导出所有子模块的内容
export * from "./users";
export * from "./products";
export * from "./orders";

// 或者选择性地重导出
export { UserService } from "./users";
export { ProductService } from "./products";
export { OrderService } from "./orders";
```

## 7.3 模块解析

TypeScript的模块解析器决定了如何从导入语句中查找模块文件。

### 7.3.1 相对与绝对路径

```typescript
// 相对路径 - 以./或../开头
import { helper } from "./helper";
import { config } from "../config";

// 绝对路径 - 不以./或../开头，通常从node_modules查找
import { express } from "express";
import { Component } from "react";
```

### 7.3.2 模块解析策略

TypeScript支持两种模块解析策略：Node.js策略和Classic策略。

#### Node.js策略

这是TypeScript默认的解析策略，与Node.js的模块解析机制相同：

1. 尝试查找文件（如`./utils.ts`）
2. 如果没有找到，尝试查找目录（如`./utils`），然后在其中查找`index.ts`或`package.json`中指定的`main`字段

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "node"  // 默认值
  }
}
```

#### Classic策略

这是TypeScript早期的解析策略，主要用于与旧版TypeScript兼容：

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "classic"
  }
}
```

### 7.3.3 模块搜索路径

TypeScript允许配置额外的模块搜索路径：

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".", // 基础路径，相对于tsconfig.json文件
    "paths": {
      "@shared/*": ["src/shared/*"], // 路径映射
      "@utils/*": ["src/utils/*"],
      "@app/*": ["src/app/*"]
    },
    "rootDirs": ["src", "generated"] // 多个根目录
  }
}
```

使用路径映射：

```typescript
// 使用路径映射导入
import { Validator } from "@shared/validators";
import { Logger } from "@utils/logger";
import { AppComponent } from "@app/components/app.component";
```

## 7.4 命名空间（Namespaces）

命名空间是TypeScript早期用于组织代码的方式，类似于内部模块。在ES6模块流行之前，命名空间是TypeScript主要的代码组织方式。

### 7.4.1 基本命名空间

```typescript
// Geometry.ts
namespace Geometry {
    export interface Point {
        x: number;
        y: number;
    }
    
    export class Circle {
        constructor(public center: Point, public radius: number) {}
        
        area(): number {
            return Math.PI * this.radius * this.radius;
        }
    }
    
    export function distance(p1: Point, p2: Point): number {
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    // 嵌套命名空间
    namespace Shapes {
        export class Triangle {
            constructor(public vertices: Point[]) {}
        }
    }
}

// 使用命名空间
const point: Geometry.Point = { x: 0, y: 0 };
const circle = new Geometry.Circle(point, 5);
console.log(circle.area()); // 78.53981633974483

const triangle = new Geometry.Shapes.Triangle([
    { x: 0, y: 0 },
    { x: 1, y: 0 },
    { x: 0, y: 1 }
]);
```

### 7.4.2 分割命名空间

大型命名空间可以分割到多个文件中：

```typescript
// Geometry.Point.ts
namespace Geometry {
    export interface Point {
        x: number;
        y: number;
    }
}

// Geometry.Circle.ts
/// <reference path="Geometry.Point.ts" />
namespace Geometry {
    export class Circle {
        constructor(public center: Point, public radius: number) {}
        
        area(): number {
            return Math.PI * this.radius * this.radius;
        }
    }
}

// Geometry.ts
/// <reference path="Geometry.Point.ts" />
/// <reference path="Geometry.Circle.ts" />

// 使用命名空间
const point: Geometry.Point = { x: 0, y: 0 };
const circle = new Geometry.Circle(point, 5);
```

### 7.4.3 命名空间与模块的区别

| 特性 | 命名空间 | 模块 |
|-------|---------|-----|
| 语法 | `namespace X { ... }` | `import/export` |
| 编译输出 | 合并到同一个文件 | 生成多个文件 |
| 作用域 | 嵌套在全局命名空间中 | 独立的文件作用域 |
| 依赖关系 | 使用`/// <reference>` | 使用`import/export` |
| 推荐使用 | 旧项目或全局API | 新项目 |

在现代TypeScript开发中，推荐使用ES6模块而非命名空间。命名空间主要用于：
1. 与旧代码兼容
2. 创建全局API（如jQuery、Lodash等）
3. 组织内部工具函数

## 7.5 动态导入

动态导入允许在运行时按需加载模块，而不是在编译时静态导入。

### 7.5.1 基本动态导入

```typescript
// 静态导入 - 在编译时解析
import { heavyComputation } from "./heavyModule";

// 动态导入 - 在运行时解析
async function useDynamicImport() {
    // 模块只在需要时加载
    const { heavyComputation } = await import("./heavyModule");
    
    const result = heavyComputation(42);
    console.log(result);
}

// 或者使用.then语法
import("./heavyModule").then(module => {
    const result = module.heavyComputation(42);
    console.log(result);
});
```

### 7.5.2 动态导入的类型

TypeScript 2.4及以上版本支持为动态导入添加类型注解：

```typescript
async function useTypedDynamicImport() {
    // 为动态导入添加类型
    const module = await import("./heavyModule") as typeof import("./heavyModule");
    
    const result = module.heavyComputation(42);
    console.log(result);
}
```

### 7.5.3 动态导入的应用场景

1. **按需加载**：只在需要时加载模块，减少初始加载时间
2. **条件加载**：根据条件动态选择加载不同模块
3. **代码分割**：使用Webpack等打包工具实现代码分割
4. **懒加载路由**：在单页应用中懒加载路由组件

```typescript
// 按需加载示例
async function loadAdminPanel() {
    const isAdmin = checkIsAdmin();
    
    if (isAdmin) {
        const adminModule = await import("./admin");
        const adminPanel = new adminModule.AdminPanel();
        adminPanel.render();
    }
}

// 条件加载示例
async function loadLanguageModule(locale: string) {
    let module;
    
    switch (locale) {
        case "en":
            module = await import("./locales/en");
            break;
        case "zh":
            module = await import("./locales/zh");
            break;
        default:
            module = await import("./locales/en");
    }
    
    return module.strings;
}

// 代码分割示例
const routes = [
    {
        path: "/dashboard",
        component: () => import("./components/Dashboard").then(m => m.DashboardComponent)
    },
    {
        path: "/profile",
        component: () => import("./components/Profile").then(m => m.ProfileComponent)
    }
];
```

## 7.6 模块与命名空间的最佳实践

### 7.6.1 模块化原则

1. **单一职责**：每个模块应该只负责一个功能领域
2. **小而专注**：保持模块小而专注，易于理解和维护
3. **明确依赖**：明确表达模块之间的依赖关系
4. **避免循环依赖**：设计模块层次结构，避免循环依赖

### 7.6.2 导出策略

1. **命名导出**：用于导出多个功能
2. **默认导出**：用于导出主要功能
3. **重导出**：用于创建模块的公共API
4. **类型导出**：仅导出类型，不导出实现

```typescript
// utils/math.ts
// 实现细节（私有）
function internalHelper(x: number): number {
    return x * x;
}

// 类型导出
export type MathResult = number;

// 命名导出
export function add(a: number, b: number): MathResult {
    return a + b;
}

export function multiply(a: number, b: number): MathResult {
    return a * b;
}

// 默认导出
export default class Calculator {
    add(a: number, b: number): MathResult {
        return a + b;
    }
    
    multiply(a: number, b: number): MathResult {
        return a * b;
    }
}
```

### 7.6.3 导入策略

1. **明确导入**：只导入需要的内容
2. **按组导入**：将相关导入分组
3. **按字母排序**：便于查找和管理
4. **避免通配符导入**：除非确实需要所有导出

```typescript
// 导入分组
// Node.js内置模块
import { readFile, writeFile } from "fs";
import { join } from "path";

// 第三方库
import express from "express";
import { Request, Response } from "express";
import mongoose from "mongoose";

// 本地模块
import { UserService } from "../services/user.service";
import { Logger } from "../utils/logger";
import { User } from "../models/user.model";
import type { IUserDocument } from "../interfaces/user.interface";

// 类型导入
import type { IApiRequest, IApiResponse } from "../interfaces/api.interface";
```

## 7.7 实例：构建模块化的应用程序

让我们通过一个实际例子来应用模块系统和命名空间的知识：

```typescript
// src/models/user.model.ts
export interface User {
    id: number;
    name: string;
    email: string;
    avatar?: string;
    createdAt: Date;
}

export interface UserDocument extends User {
    updatedAt: Date;
}

// src/repositories/user.repository.ts
import type { User, UserDocument } from "../models/user.model";

export class UserRepository {
    private users: UserDocument[] = [];
    private nextId = 1;
    
    create(userData: Omit<User, "id" | "createdAt">): UserDocument {
        const user: UserDocument = {
            id: this.nextId++,
            ...userData,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        
        this.users.push(user);
        return user;
    }
    
    findById(id: number): UserDocument | undefined {
        return this.users.find(user => user.id === id);
    }
    
    findAll(): UserDocument[] {
        return [...this.users];
    }
    
    update(id: number, updates: Partial<Omit<User, "id" | "createdAt">>): UserDocument | undefined {
        const userIndex = this.users.findIndex(user => user.id === id);
        
        if (userIndex === -1) {
            return undefined;
        }
        
        this.users[userIndex] = {
            ...this.users[userIndex],
            ...updates,
            updatedAt: new Date()
        };
        
        return this.users[userIndex];
    }
    
    delete(id: number): boolean {
        const userIndex = this.users.findIndex(user => user.id === id);
        
        if (userIndex === -1) {
            return false;
        }
        
        this.users.splice(userIndex, 1);
        return true;
    }
}

// src/services/user.service.ts
import type { User, UserDocument } from "../models/user.model";
import { UserRepository } from "../repositories/user.repository";

export class UserService {
    constructor(private userRepository: UserRepository) {}
    
    async create(userData: Omit<User, "id" | "createdAt">): Promise<UserDocument> {
        // 验证用户数据
        if (!userData.email || !userData.name) {
            throw new Error("Name and email are required");
        }
        
        // 检查邮箱是否已存在
        const existingUsers = this.userRepository.findAll();
        if (existingUsers.some(user => user.email === userData.email)) {
            throw new Error("Email already exists");
        }
        
        return this.userRepository.create(userData);
    }
    
    async findById(id: number): Promise<UserDocument | undefined> {
        return this.userRepository.findById(id);
    }
    
    async findAll(): Promise<UserDocument[]> {
        return this.userRepository.findAll();
    }
    
    async update(id: number, updates: Partial<Omit<User, "id" | "createdAt">>): Promise<UserDocument | undefined> {
        // 检查用户是否存在
        const user = this.userRepository.findById(id);
        if (!user) {
            throw new Error("User not found");
        }
        
        // 如果更新邮箱，检查邮箱是否已存在
        if (updates.email && updates.email !== user.email) {
            const existingUsers = this.userRepository.findAll();
            if (existingUsers.some(u => u.email === updates.email)) {
                throw new Error("Email already exists");
            }
        }
        
        return this.userRepository.update(id, updates);
    }
    
    async delete(id: number): Promise<boolean> {
        // 检查用户是否存在
        const user = this.userRepository.findById(id);
        if (!user) {
            throw new Error("User not found");
        }
        
        return this.userRepository.delete(id);
    }
}

// src/controllers/user.controller.ts
import type { User, UserDocument } from "../models/user.model";
import { UserService } from "../services/user.service";
import { Logger } from "../utils/logger";

export class UserController {
    constructor(
        private userService: UserService,
        private logger: Logger
    ) {}
    
    async createUser(req: any, res: any): Promise<void> {
        try {
            const userData: Omit<User, "id" | "createdAt"> = req.body;
            const user = await this.userService.create(userData);
            
            this.logger.info(`User created with ID: ${user.id}`);
            res.status(201).json(user);
        } catch (error) {
            this.logger.error(`Error creating user: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async getUserById(req: any, res: any): Promise<void> {
        try {
            const userId = parseInt(req.params.id, 10);
            const user = await this.userService.findById(userId);
            
            if (!user) {
                return res.status(404).json({ error: "User not found" });
            }
            
            res.json(user);
        } catch (error) {
            this.logger.error(`Error fetching user: ${(error as Error).message}`);
            res.status(500).json({ error: "Internal server error" });
        }
    }
    
    async getAllUsers(req: any, res: any): Promise<void> {
        try {
            const users = await this.userService.findAll();
            res.json(users);
        } catch (error) {
            this.logger.error(`Error fetching users: ${(error as Error).message}`);
            res.status(500).json({ error: "Internal server error" });
        }
    }
    
    async updateUser(req: any, res: any): Promise<void> {
        try {
            const userId = parseInt(req.params.id, 10);
            const updates = req.body;
            
            const user = await this.userService.update(userId, updates);
            
            if (!user) {
                return res.status(404).json({ error: "User not found" });
            }
            
            this.logger.info(`User updated with ID: ${userId}`);
            res.json(user);
        } catch (error) {
            this.logger.error(`Error updating user: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async deleteUser(req: any, res: any): Promise<void> {
        try {
            const userId = parseInt(req.params.id, 10);
            const success = await this.userService.delete(userId);
            
            if (!success) {
                return res.status(404).json({ error: "User not found" });
            }
            
            this.logger.info(`User deleted with ID: ${userId}`);
            res.status(204).send();
        } catch (error) {
            this.logger.error(`Error deleting user: ${(error as Error).message}`);
            res.status(500).json({ error: "Internal server error" });
        }
    }
}

// src/routes/user.routes.ts
import { Router } from "express";
import { UserController } from "../controllers/user.controller";
import { UserService } from "../services/user.service";
import { UserRepository } from "../repositories/user.repository";
import { Logger } from "../utils/logger";

export function createUserRoutes(): Router {
    const router = Router();
    
    // 依赖注入
    const userRepository = new UserRepository();
    const userService = new UserService(userRepository);
    const logger = new Logger();
    const userController = new UserController(userService, logger);
    
    // 定义路由
    router.post("/", userController.createUser.bind(userController));
    router.get("/", userController.getAllUsers.bind(userController));
    router.get("/:id", userController.getUserById.bind(userController));
    router.put("/:id", userController.updateUser.bind(userController));
    router.delete("/:id", userController.deleteUser.bind(userController));
    
    return router;
}

// src/app.ts
import express from "express";
import { createUserRoutes } from "./routes/user.routes";

export class App {
    private app = express();
    
    constructor() {
        this.configureMiddleware();
        this.configureRoutes();
    }
    
    private configureMiddleware(): void {
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
    }
    
    private configureRoutes(): void {
        this.app.use("/api/users", createUserRoutes());
    }
    
    listen(port: number): void {
        this.app.listen(port, () => {
            console.log(`Server listening on port ${port}`);
        });
    }
}

// src/index.ts
import { App } from "./app";

const app = new App();
app.listen(3000);
```

## 7.8 总结

在这一章中，我们深入学习了TypeScript的模块系统和命名空间：

- 理解了模块系统的重要性和发展历程
- 掌握了ES6模块的导入导出语法和最佳实践
- 学习了TypeScript的模块解析策略和配置
- 探索了命名空间的概念和使用场景
- 了解了动态导入的语法和应用场景
- 构建了一个模块化的应用程序

模块化和命名空间是TypeScript代码组织的核心机制，掌握它们将帮助您构建更加清晰、可维护和可扩展的应用程序。

## 7.9 练习

1. 创建一个模块化的工具库，包含常用的字符串、数组、日期处理函数
2. 实现一个插件系统，使用模块和动态导入机制
3. 构建一个模块化的博客系统，包括文章、评论和用户模块
4. 创建一个类型安全的配置管理器，使用模块和命名空间

通过完成这些练习，您将加深对TypeScript模块系统和命名空间的理解，并能够将其应用到实际项目中。