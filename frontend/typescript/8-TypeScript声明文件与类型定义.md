# 第8章：TypeScript声明文件与类型定义

## 章节概述

TypeScript的声明文件是连接JavaScript生态系统和TypeScript类型系统的桥梁。在本章中，我们将深入探讨如何使用声明文件为现有的JavaScript库添加类型信息，如何创建自己的类型定义，以及如何利用这些类型定义来提升代码质量和开发体验。

## 学习目标

- 理解声明文件的作用和重要性
- 掌握声明文件的语法和结构
- 学会为JavaScript库创建类型定义
- 了解如何发布和维护类型定义包
- 掌握高级类型声明技巧

---

## 8.1 声明文件基础

### 8.1.1 什么是声明文件

声明文件（以`.d.ts`为扩展名）是TypeScript中的一种特殊文件，它只包含类型声明信息而不包含实际的JavaScript代码。这些文件告诉TypeScript编译器一个模块或库的形状，但不生成任何JavaScript输出。

### 8.1.2 为什么需要声明文件

1. **类型安全**：为JavaScript库提供类型检查
2. **开发体验**：IDE中的自动补全和错误提示
3. **文档作用**：类型即文档，清晰展示API结构
4. **迁移支持**：逐步将JavaScript项目迁移到TypeScript

### 8.1.3 声明文件的基本结构

```typescript
// 示例：lodash库的简化声明

// 声明一个函数
declare function get<T>(object: T, path: string | string[]): any;

// 声明一个命名空间
declare namespace _ {
    function capitalize(string: string): string;
    function camelCase(string: string): string;
}

// 声明一个模块
declare module "lodash" {
    export = _;
}
```

---

## 8.2 声明文件的语法

### 8.2.1 全局声明

全局声明不需要导入即可在整个项目中使用：

```typescript
// global.d.ts
// 声明一个全局变量
declare const APP_VERSION: string;

// 声明一个全局函数
declare function greet(name: string): void;

// 声明一个全局类
declare class Logger {
    constructor(level: string);
    log(message: string): void;
}

// 声明一个全局接口
declare interface User {
    id: number;
    name: string;
}
```

### 8.2.2 模块声明

模块声明为特定模块提供类型信息：

```typescript
// 为现有模块添加声明
declare module "some-library" {
    export function initialize(): void;
    export function process<T>(data: T): T;
    export const version: string;
}

// 使用通配符声明
declare module "*.txt" {
    const content: string;
    export default content;
}

declare module "*.svg" {
    const content: string;
    export default content;
}
```

### 8.2.3 声明合并

声明合并允许我们将多个声明合并为一个：

```typescript
// 接口声明合并
interface Box {
    height: number;
    width: number;
}

interface Box {
    scale: number;
}

// 类和接口声明合并
class Calculator {
    // 类实现
}

interface Calculator {
    // 接口扩展
    multiply(x: number, y: number): number;
}
```

---

## 8.3 创建自定义声明文件

### 8.3.1 为简单的JavaScript库创建声明

假设我们有以下JavaScript库：

```javascript
// math-utils.js
function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

module.exports = { add, subtract, multiply };
```

我们可以创建以下声明文件：

```typescript
// math-utils.d.ts
declare module 'math-utils' {
    export function add(a: number, b: number): number;
    export function subtract(a: number, b: number): number;
    export function multiply(a: number, b: number): number;
}
```

### 8.3.2 处理复杂的库结构

对于更复杂的库，我们可能需要更详细的声明：

```typescript
// api-client.d.ts
declare namespace ApiClient {
    interface RequestOptions {
        method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
        headers?: Record<string, string>;
        body?: any;
        timeout?: number;
    }

    interface Response<T = any> {
        data: T;
        status: number;
        statusText: string;
        headers: Record<string, string>;
    }

    interface ApiError {
        message: string;
        code: string;
        details?: any;
    }

    class Client {
        constructor(baseURL: string, options?: RequestOptions);
        
        get<T = any>(url: string, options?: RequestOptions): Promise<Response<T>>;
        post<T = any>(url: string, data?: any, options?: RequestOptions): Promise<Response<T>>;
        put<T = any>(url: string, data?: any, options?: RequestOptions): Promise<Response<T>>;
        delete<T = any>(url: string, options?: RequestOptions): Promise<Response<T>>;
        
        setAuth(token: string): void;
        clearAuth(): void;
    }
}

declare module "api-client" {
    export = ApiClient;
}
```

---

## 8.4 声明文件的发布与维护

### 8.4.1 发布到DefinitelyTyped

DefinitelyTyped是最大的TypeScript声明仓库，包含了大量流行库的类型定义。

1. **安装TypeScript和dts-gen工具**：
   ```bash
   npm install -g typescript dts-gen
   ```

2. **生成初始声明文件**：
   ```bash
   dts-gen -m <module-name>
   ```

3. **提交到DefinitelyTyped**：
   - Fork DefinitelyTyped仓库
   - 添加或修改类型定义
   - 提交Pull Request

### 8.4.2 作为独立包发布

如果你想为库提供官方类型定义：

1. **在库中包含类型定义**：
   - 在`package.json`中指定`"types"`或`"typings"`字段
   - 提供类型定义文件

2. **创建独立的类型包**：
   ```json
   // package.json
   {
     "name": "@types/library-name",
     "types": "index.d.ts"
   }
   ```

### 8.4.3 维护声明文件的最佳实践

1. **保持类型定义与库同步**
2. **提供详尽的JSDoc注释**
3. **使用严格类型检查**
4. **处理边界情况和错误类型**
5. **提供测试用例**

---

## 8.5 高级类型声明技巧

### 8.5.1 使用泛型

```typescript
// 泛型接口
interface Repository<T, ID = string> {
    findById(id: ID): Promise<T | null>;
    save(entity: T): Promise<T>;
    update(id: ID, updateData: Partial<T>): Promise<T>;
    delete(id: ID): Promise<boolean>;
}

// 泛型函数
declare function createRepository<T, ID = string>(
    collection: string,
    idKey: keyof T
): Repository<T, ID>;
```

### 8.5.2 使用条件类型

```typescript
// 条件类型声明
declare function fetch<T>(url: string): T extends string 
    ? Promise<string> 
    : T extends object 
        ? Promise<T> 
        : Promise<any>;

// 映射类型
declare type DeepPartial<T> = {
    [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
```

### 8.5.3 使用模块增强

```typescript
// 扩展现有模块
declare module "express" {
    interface Request {
        user?: {
            id: string;
            role: string;
        };
    }
}

// 扩展全局对象
declare global {
    interface Window {
        gtag: (command: string, targetId: string, config?: any) => void;
    }
}
```

---

## 8.6 类型定义示例

### 8.6.1 事件系统类型定义

```typescript
// event-emitter.d.ts
declare class EventEmitter {
    constructor();
    
    on(event: string, listener: (...args: any[]) => void): this;
    once(event: string, listener: (...args: any[]) => void): this;
    off(event: string, listener: (...args: any[]) => void): this;
    emit(event: string, ...args: any[]): boolean;
    
    removeAllListeners(event?: string): this;
    listenerCount(event: string): number;
}

// 使用泛型提供更具体的事件类型
declare class TypedEventEmitter<TEvents extends Record<string, any[]>> {
    on<TEventName extends keyof TEvents>(
        event: TEventName,
        listener: (...args: TEvents[TEventName]) => void
    ): this;
    
    emit<TEventName extends keyof TEvents>(
        event: TEventName,
        ...args: TEvents[TEventName]
    ): boolean;
}
```

### 8.6.2 数据库ORM类型定义

```typescript
// orm-types.d.ts
declare namespace ORM {
    interface Model<T = any> {
        new(): T;
        findOne(options?: FindOneOptions): Promise<T | null>;
        findMany(options?: FindManyOptions): Promise<T[]>;
        create(data: Partial<T>): Promise<T>;
        update(id: string | number, data: Partial<T>): Promise<T>;
        delete(id: string | number): Promise<boolean>;
    }
    
    interface FindOneOptions {
        where?: Record<string, any>;
        include?: string[];
        select?: string[];
        order?: Record<string, 'ASC' | 'DESC'>;
    }
    
    interface FindManyOptions extends FindOneOptions {
        limit?: number;
        offset?: number;
    }
    
    interface Database {
        connect(): Promise<void>;
        disconnect(): Promise<void>;
        transaction<T>(callback: () => Promise<T>): Promise<T>;
        getRepository<T>(model: Model<T>): Repository<T>;
    }
    
    interface Repository<T> {
        findOne(options?: FindOneOptions): Promise<T | null>;
        findMany(options?: FindManyOptions): Promise<T[]>;
        create(data: Partial<T>): Promise<T>;
        update(id: string | number, data: Partial<T>): Promise<T>;
        delete(id: string | number): Promise<boolean>;
    }
}
```

---

## 8.7 实战项目：构建日志库的类型定义

让我们为一个小型JavaScript日志库创建完整的类型定义。

### 8.7.1 库的实现

```javascript
// logger.js
(function(global) {
    'use strict';
    
    const LOG_LEVELS = {
        DEBUG: 0,
        INFO: 1,
        WARN: 2,
        ERROR: 3,
        FATAL: 4
    };
    
    let currentLogLevel = LOG_LEVELS.INFO;
    
    function Logger(name) {
        this.name = name;
    }
    
    Logger.prototype.debug = function(message, meta) {
        if (currentLogLevel <= LOG_LEVELS.DEBUG) {
            console.log(`[DEBUG] [${this.name}] ${message}`, meta || '');
        }
    };
    
    Logger.prototype.info = function(message, meta) {
        if (currentLogLevel <= LOG_LEVELS.INFO) {
            console.info(`[INFO] [${this.name}] ${message}`, meta || '');
        }
    };
    
    Logger.prototype.warn = function(message, meta) {
        if (currentLogLevel <= LOG_LEVELS.WARN) {
            console.warn(`[WARN] [${this.name}] ${message}`, meta || '');
        }
    };
    
    Logger.prototype.error = function(message, meta) {
        if (currentLogLevel <= LOG_LEVELS.ERROR) {
            console.error(`[ERROR] [${this.name}] ${message}`, meta || '');
        }
    };
    
    Logger.prototype.fatal = function(message, meta) {
        if (currentLogLevel <= LOG_LEVELS.FATAL) {
            console.error(`[FATAL] [${this.name}] ${message}`, meta || '');
        }
    };
    
    function createLogger(name) {
        return new Logger(name);
    }
    
    function setLogLevel(level) {
        if (typeof level === 'string') {
            currentLogLevel = LOG_LEVELS[level.toUpperCase()];
        } else {
            currentLogLevel = level;
        }
    }
    
    function getLogger(name) {
        return new Logger(name);
    }
    
    const loggerAPI = {
        createLogger,
        setLogLevel,
        getLogger,
        LOG_LEVELS
    };
    
    // 支持不同的模块系统
    if (typeof exports !== 'undefined') {
        if (typeof module !== 'undefined' && module.exports) {
            exports = module.exports = loggerAPI;
        }
        exports.loggerAPI = loggerAPI;
    } else {
        global.Logger = loggerAPI;
    }
    
})(typeof window !== 'undefined' ? window : this);
```

### 8.7.2 声明文件创建

```typescript
// logger.d.ts
declare namespace LoggerAPI {
    type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
    
    type Meta = Record<string, any> | string;
    
    interface Logger {
        name: string;
        debug(message: string, meta?: Meta): void;
        info(message: string, meta?: Meta): void;
        warn(message: string, meta?: Meta): void;
        error(message: string, meta?: Meta): void;
        fatal(message: string, meta?: Meta): void;
    }
    
    interface LoggerAPI {
        LOG_LEVELS: {
            DEBUG: number;
            INFO: number;
            WARN: number;
            ERROR: number;
            FATAL: number;
        };
        createLogger(name: string): Logger;
        getLogger(name: string): Logger;
        setLogLevel(level: LogLevel | number): void;
    }
}

declare module 'logger' {
    export = LoggerAPI;
}

// 全局声明（如果库直接暴露到全局）
declare global {
    const Logger: LoggerAPI.LoggerAPI;
}
```

### 8.7.3 使用示例

```typescript
// 使用声明的日志库
import { createLogger, setLogLevel, LOG_LEVELS } from 'logger';

// 创建日志实例
const logger = createLogger('MyApp');

// 设置日志级别
setLogLevel('DEBUG'); // 使用字符串
setLogLevel(LOG_LEVELS.INFO); // 使用常量

// 使用日志方法
logger.debug('Application starting', { version: '1.0.0' });
logger.info('User logged in', { userId: '123' });
logger.warn('Disk space low', { usage: '85%' });
logger.error('Database connection failed', { error: 'Connection timeout' });
```

---

## 8.8 最佳实践与技巧

### 8.8.1 声明文件组织

1. **分离声明和实现**：保持`.d.ts`文件与`.js`文件分离
2. **模块化组织**：按功能模块组织声明文件
3. **避免全局污染**：优先使用模块声明而非全局声明
4. **版本控制**：确保声明文件与库版本一致

### 8.8.2 类型定义质量

1. **类型完整性**：提供完整的类型覆盖
2. **使用泛型**：增加类型复用性
3. **文档注释**：提供清晰的JSDoc注释
4. **边界处理**：处理特殊情况和错误类型

### 8.8.3 性能考虑

1. **避免过度泛型**：复杂泛型可能影响编译性能
2. **模块化导入**：使用导入类型减少编译负载
3. **精确声明**：避免过于宽泛的类型声明

---

## 8.9 类型定义的测试

### 8.9.1 类型测试文件

```typescript
// logger-tests.ts
import { createLogger, setLogLevel, LOG_LEVELS } from 'logger';

// 类型测试：Logger实例
const logger = createLogger('test');
logger.debug('message', { data: 'value' });
logger.info('message', 'metadata');
logger.warn('message');
logger.error('message', { error: 'details' });
logger.fatal('message');

// 类型测试：设置日志级别
setLogLevel('DEBUG');
setLogLevel(LOG_LEVELS.INFO);

// 类型错误测试（这些应该导致类型错误）：
// logger.debug(123); // 错误：参数应该是string
// setLogLevel('INVALID'); // 错误：无效的日志级别
```

### 8.9.2 使用类型检查工具

```bash
# 使用TypeScript编译器检查类型
npx tsc logger-tests.ts --noEmit

# 使用dtslint进行更严格的检查
npm install -g dtslint
dtslint logger/
```

---

## 8.10 常见问题与解决方案

### 8.10.1 解决类型冲突

当多个声明文件定义了相同的名称时，可能会发生冲突：

```typescript
// 解决方案1：使用模块命名空间
declare module 'library-a' {
    interface Config {
        timeout: number;
    }
}

declare module 'library-b' {
    interface Config {
        retries: number;
    }
}

// 解决方案2：使用类型别名
type LibraryAConfig = import('library-a').Config;
type LibraryBConfig = import('library-b').Config;
```

### 8.10.2 处理动态属性

对于具有动态属性的库：

```typescript
// 不好的声明：所有属性都是any
declare class DynamicObject {
    [key: string]: any;
}

// 好的声明：使用索引签名和已知属性
declare class DynamicObject {
    id: string;
    name: string;
    [key: string]: unknown;
}
```

### 8.10.3 处理回调函数

```typescript
// 简单回调
declare function fetchData(callback: (data: any) => void): void;

// 带泛型的回调
declare function fetchData<T>(callback: (data: T) => void): void;

// 使用函数重载处理不同类型的回调
declare function process(callback: (error: Error | null, result?: string) => void): void;
declare function process(): Promise<string>;
```

---

## 本章小结

本章我们深入探讨了TypeScript声明文件与类型定义的各个方面。从基础语法到高级技巧，从创建简单的类型定义到构建复杂的类型系统，我们学习了如何有效地为JavaScript库添加类型信息。

掌握了这些技能后，您将能够：

1. 为现有JavaScript库创建类型定义
2. 发布和维护高质量的声明文件
3. 处理复杂的类型声明场景
4. 利用TypeScript的类型系统提升代码质量

在下一章中，我们将探讨TypeScript的工程实践与最佳实践，进一步巩固我们对TypeScript的理解和应用能力。