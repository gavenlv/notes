# 第9章：TypeScript工程实践与最佳实践

## 章节概述

在前面的章节中，我们学习了TypeScript的核心概念和语法。在这一章中，我们将探讨如何在大型项目中有效地应用TypeScript，以及遵循哪些最佳实践来构建可维护、可扩展的应用程序。我们将涵盖项目架构、性能优化、代码组织、测试策略等方面的实践经验。

## 学习目标

- 掌握大型TypeScript项目的架构设计原则
- 学会配置和优化TypeScript编译器
- 了解代码组织与模块化策略
- 掌握性能优化技巧
- 学会设置TypeScript项目的测试环境
- 理解团队协作中的TypeScript最佳实践

---

## 9.1 项目架构设计

### 9.1.1 单体仓库与多仓库策略

在选择项目结构时，我们需要考虑是使用单体仓库（monorepo）还是多仓库（multi-repo）策略。

**单体仓库的优势：**
- 代码共享和重用更容易
- 原子提交和跨项目重构
- 统一的工具链和依赖管理
- 简化的CI/CD流水线

**单体仓库的劣势：**
- 构建和测试时间可能更长
- 工具链配置更复杂
- 版本管理挑战

**多仓库的优势：**
- 独立的版本控制和发布周期
- 更简单的项目结构
- 更灵活的部署选项

**多仓库的劣势：**
- 代码共享困难
- 依赖管理复杂
- 跨项目一致性难保证

### 9.1.2 推荐的项目结构

对于大型TypeScript项目，我们推荐以下目录结构：

```
my-project/
├── src/
│   ├── components/          # 可重用UI组件
│   ├── hooks/              # 自定义React钩子（如果适用）
│   ├── services/           # 业务逻辑服务
│   ├── utils/              # 工具函数
│   ├── types/              # 类型定义
│   ├── constants/          # 常量定义
│   ├── store/              # 状态管理
│   ├── routes/             # 路由配置
│   └── pages/              # 页面组件
├── tests/                  # 测试文件
├── docs/                   # 文档
├── scripts/                # 构建和部署脚本
├── config/                 # 配置文件
└── package.json
```

### 9.1.3 模块化设计原则

1. **单一职责原则**：每个模块只负责一个功能
2. **开放封闭原则**：模块应该对扩展开放，对修改封闭
3. **依赖倒置原则**：高层模块不应该依赖低层模块，都应该依赖抽象
4. **接口隔离原则**：客户端不应该依赖于它不需要的接口

---

## 9.2 TypeScript编译器配置

### 9.2.1 tsconfig.json详解

tsconfig.json是TypeScript项目的核心配置文件，控制编译器的行为。

```json
{
  "compilerOptions": {
    /* 基本选项 */
    "target": "ES2020",                    // 指定ECMAScript目标版本
    "module": "ESNext",                    // 指定模块代码生成方式
    "lib": ["ES2020", "DOM"],              // 指定要包含在编译中的库文件
    "outDir": "./dist",                    // 重定向输出目录
    "rootDir": "./src",                    // 指定输入文件根目录
    "strict": true,                        // 启用所有严格类型检查选项
    "esModuleInterop": true,               // 允许使用export/import导入导出CommonJS模块
    
    /* 模块解析选项 */
    "moduleResolution": "node",            // 指定模块解析策略
    "baseUrl": "./",                       // 用于解析非相对模块名称的基目录
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/utils/*": ["src/utils/*"]
    },                                     // 模块名称到基于baseUrl的路径映射
    
    /* 代码生成选项 */
    "declaration": true,                   // 生成相应的'.d.ts'文件
    "declarationMap": true,                // 为每个'.d.ts'文件生成对应的'sourcemap'
    "sourceMap": true,                     // 生成相应的'.map'文件
    "removeComments": true,                // 删除编译后所有的注释
    "noEmit": false,                       // 不生成输出文件
    "importHelpers": true,                 // 从tslib导入辅助函数
    
    /* 严格类型检查选项 */
    "strict": true,                        // 启用所有严格类型检查选项
    "noImplicitAny": true,                 // 在表达式和声明上有隐含的any类型时报错
    "strictNullChecks": true,              // 严格的null检查
    "strictFunctionTypes": true,           // 严格的函数类型
    "noImplicitReturns": true,            // 并不是所有函数中的代码路径都返回值时报错
    "noImplicitThis": true,                // 当this表达式的值为any类型时报错
    "noUnusedLocals": true,                // 有未使用的变量时报错
    "noUnusedParameters": true,            // 有未使用的参数时报错
    
    /* 额外检查 */
    "noFallthroughCasesInSwitch": true,   // 报告switch语句的fallthrough错误
    "noUncheckedIndexedAccess": true,      // 对索引访问使用严格检查
    
    /* 高级选项 */
    "skipLibCheck": true,                  // 跳过对声明文件的类型检查
    "forceConsistentCasingInFileNames": true, // 禁止对同一个文件使用不一致的大小写引用
    "resolveJsonModule": true              // 允许导入.json文件
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.spec.ts",
    "**/*.test.ts"
  ]
}
```

### 9.2.2 生产环境与开发环境配置

我们可以为不同环境创建不同的TypeScript配置：

```json
// tsconfig.base.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "baseUrl": "./",
    "paths": {
      "@/*": ["src/*"]
    },
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "exclude": ["node_modules", "dist"]
}
```

```json
// tsconfig.dev.json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist/dev",
    "sourceMap": true,
    "removeComments": false,
    "noUnusedLocals": false,
    "noUnusedParameters": false
  },
  "include": ["src/**/*"]
}
```

```json
// tsconfig.prod.json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist/prod",
    "sourceMap": false,
    "removeComments": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "declaration": false
  },
  "include": ["src/**/*"]
}
```

### 9.2.3 编译器性能优化

1. **使用增量编译**：
   ```json
   {
     "compilerOptions": {
       "incremental": true,
       "tsBuildInfoFile": "./dist/.tsbuildinfo"
     }
   }
   ```

2. **使用项目引用**：
   ```json
   // tsconfig.json
   {
     "files": [],
     "references": [
       { "path": "./packages/core" },
       { "path": "./packages/utils" },
       { "path": "./packages/web" }
     ]
   }
   
   // packages/core/tsconfig.json
   {
     "extends": "../../tsconfig.base.json",
     "compilerOptions": {
       "composite": true,
       "outDir": "../../dist/core"
     },
     "references": [
       { "path": "../utils" }
     ]
   }
   ```

3. **使用更快的工具**：
   - esbuild：用于快速转换和打包
   - swc：使用Rust编写的TypeScript/JavaScript编译器
   - sucrase：更快的TypeScript转换器

---

## 9.3 代码组织与模块化

### 9.3.1 依赖注入模式

依赖注入（Dependency Injection）是实现松耦合代码的有效方式：

```typescript
// 定义服务接口
interface Logger {
    log(message: string): void;
}

interface Database {
    query<T>(sql: string, params?: any[]): Promise<T[]>;
}

// 实现服务
class ConsoleLogger implements Logger {
    log(message: string): void {
        console.log(message);
    }
}

class PostgreSQLDatabase implements Database {
    constructor(private connectionString: string) {}
    
    async query<T>(sql: string, params?: any[]): Promise<T[]> {
        // 实际数据库查询逻辑
        return [];
    }
}

// 使用依赖注入的类
class UserRepository {
    constructor(
        private db: Database,
        private logger: Logger
    ) {}
    
    async getUserById(id: string): Promise<User | null> {
        this.logger.log(`Fetching user with id: ${id}`);
        const users = await this.db.query<User[]>(
            'SELECT * FROM users WHERE id = $1',
            [id]
        );
        return users.length > 0 ? users[0] : null;
    }
}

// 使用IoC容器
class DIContainer {
    private services: Map<string, any> = new Map();
    
    register<T>(name: string, implementation: new (...args: any[]) => T): void {
        this.services.set(name, implementation);
    }
    
    resolve<T>(name: string): T {
        const Service = this.services.get(name);
        if (!Service) {
            throw new Error(`Service ${name} not registered`);
        }
        return new Service();
    }
}

// 配置容器
const container = new DIContainer();
container.register('logger', ConsoleLogger);
container.register('database', () => new PostgreSQLDatabase('postgres://...'));
container.register('userRepository', UserRepository);

// 使用
const logger = container.resolve<Logger>('logger');
const db = container.resolve<Database>('database');
const userRepository = new UserRepository(db, logger);
```

### 9.3.2 工厂模式与抽象工厂

工厂模式可以帮助我们创建对象，而无需指定具体的类：

```typescript
// 产品接口
interface Button {
    render(): void;
}

interface Checkbox {
    render(): void;
}

// 具体产品
class WindowsButton implements Button {
    render(): void {
        console.log('Render Windows button');
    }
}

class WindowsCheckbox implements Checkbox {
    render(): void {
        console.log('Render Windows checkbox');
    }
}

class MacOSButton implements Button {
    render(): void {
        console.log('Render macOS button');
    }
}

class MacOSCheckbox implements Checkbox {
    render(): void {
        console.log('Render macOS checkbox');
    }
}

// 抽象工厂接口
interface GUIFactory {
    createButton(): Button;
    createCheckbox(): Checkbox;
}

// 具体工厂
class WindowsFactory implements GUIFactory {
    createButton(): Button {
        return new WindowsButton();
    }
    
    createCheckbox(): Checkbox {
        return new WindowsCheckbox();
    }
}

class MacOSFactory implements GUIFactory {
    createButton(): Button {
        return new MacOSButton();
    }
    
    createCheckbox(): Checkbox {
        return new MacOSCheckbox();
    }
}

// 应用程序类
class Application {
    constructor(private factory: GUIFactory) {}
    
    createUI(): void {
        const button = this.factory.createButton();
        const checkbox = this.factory.createCheckbox();
        
        button.render();
        checkbox.render();
    }
}

// 客户端代码
function configureApplication(): Application {
    const osName = navigator.userAgent.includes('Windows') ? 'windows' : 'macos';
    const factory = osName === 'windows' 
        ? new WindowsFactory() 
        : new MacOSFactory();
    
    return new Application(factory);
}

const app = configureApplication();
app.createUI();
```

### 9.3.3 模块导入策略

1. **使用路径映射**：
   ```typescript
   import { UserService } from '@/services/user-service';
   import { Button } from '@/components/ui/button';
   ```

2. **使用桶文件（barrel files）**：
   ```typescript
   // services/index.ts
   export { UserService } from './user-service';
   export { ProductService } from './product-service';
   export { OrderService } from './order-service';
   
   // 在其他地方导入
   import { UserService, ProductService } from '@/services';
   ```

3. **使用动态导入**：
   ```typescript
   async function loadAdminPanel() {
       const { AdminPanel } = await import('@/components/admin/admin-panel');
       return <AdminPanel />;
   }
   ```

---

## 9.4 性能优化技巧

### 9.4.1 编译时性能优化

1. **避免过度类型使用**：
   ```typescript
   // 避免
   type DeepNested<T> = {
       [K in keyof T]: T[K] extends object 
           ? DeepNested<T[K]> & { extra: string }
           : T[K];
   };
   
   // 适当使用
   type PartialUser = Partial<User>;
   ```

2. **使用类型别名代替接口**（在某些情况下）：
   ```typescript
   // 对于简单的类型别名，类型别名更轻量
   type UserId = string;
   type Status = 'active' | 'inactive';
   ```

3. **优化泛型使用**：
   ```typescript
   // 避免
   function processData<T, U, V, W>(a: T, b: U, c: V, d: W): void { }
   
   // 更好
   interface ProcessDataOptions {
       paramA: string;
       paramB: number;
       paramC: boolean;
       paramD: any[];
   }
   
   function processData(options: ProcessDataOptions): void { }
   ```

### 9.4.2 运行时性能优化

1. **使用类型守卫避免类型断言**：
   ```typescript
   // 避免
   function processValue(value: unknown) {
       const user = value as User; // 不安全
       console.log(user.name);
   }
   
   // 更好
   function isUser(value: unknown): value is User {
       return (
           value !== null &&
           typeof value === 'object' &&
           'id' in value &&
           'name' in value &&
           typeof (value as any).name === 'string'
       );
   }
   
   function processValue(value: unknown) {
       if (isUser(value)) {
           console.log(value.name); // 安全
       }
   }
   ```

2. **使用枚举替代字符串字面量**（在某些情况下）：
   ```typescript
   // 使用枚举
   enum UserRole {
       Admin = 'admin',
       User = 'user',
       Guest = 'guest'
   }
   
   // 使用常量对象（有时更轻量）
   const UserRole = {
       Admin: 'admin' as const,
       User: 'user' as const,
       Guest: 'guest' as const
   } as const;
   
   type UserRole = typeof UserRole[keyof typeof UserRole];
   ```

3. **避免在热路径中使用复杂类型检查**：
   ```typescript
   // 避免在循环中进行复杂的类型检查
   function processItems(items: unknown[]): Item[] {
       return items.filter(isItem).map(transformItem);
   }
   
   // 预先验证
   function processItems(items: unknown[]): Item[] {
       if (!items.every(isItem)) {
           throw new Error('All items must be valid Item instances');
       }
       
       // 现在可以安全使用items作为Item[]
       return (items as Item[]).map(transformItem);
   }
   ```

### 9.4.3 代码分割与懒加载

1. **使用动态导入实现路由级代码分割**：
   ```typescript
   import { lazy } from 'react';
   
   const HomePage = lazy(() => import('@/pages/home-page'));
   const AboutPage = lazy(() => import('@/pages/about-page'));
   const ContactPage = lazy(() => import('@/pages/contact-page'));
   
   // 在路由配置中使用
   const routes = [
       { path: '/', component: HomePage },
       { path: '/about', component: AboutPage },
       { path: '/contact', component: ContactPage }
   ];
   ```

2. **使用条件导入**：
   ```typescript
   async function initializeService() {
       let ServiceClass: any;
       
       if (process.env.NODE_ENV === 'production') {
           const module = await import('@/services/production-service');
           ServiceClass = module.ProductionService;
       } else {
           const module = await import('@/services/development-service');
           ServiceClass = module.DevelopmentService;
       }
       
       return new ServiceClass();
   }
   ```

---

## 9.5 测试策略

### 9.5.1 设置TypeScript测试环境

1. **使用Jest配置TypeScript**：
   ```json
   // jest.config.js
   module.exports = {
       preset: 'ts-jest',
       testEnvironment: 'node',
       roots: ['<rootDir>/src'],
       testMatch: [
           '**/__tests__/**/*.+(ts|tsx|js)',
           '**/*.(test|spec).+(ts|tsx|js)'
       ],
       transform: {
           '^.+\\.(ts|tsx)$': 'ts-jest'
       },
       collectCoverageFrom: [
           'src/**/*.{ts,tsx}',
           '!src/**/*.d.ts'
       ],
       coverageDirectory: 'coverage',
       coverageReporters: ['text', 'lcov', 'html']
   };
   ```

2. **设置测试类型定义**：
   ```typescript
   // test-setup.ts
   import '@testing-library/jest-dom';
   
   // 扩展Jest匹配器
   declare global {
       namespace jest {
           interface Matchers<R> {
               toBeValidUser(): R;
           }
       }
   }
   
   // 自定义匹配器实现
   expect.extend({
       toBeValidUser(received: unknown) {
           if (isUser(received)) {
               return {
                   message: () => `expected ${received} not to be a valid user`,
                   pass: true
               };
           } else {
               return {
                   message: () => `expected ${received} to be a valid user`,
                   pass: false
               };
           }
       }
   });
   ```

### 9.5.2 测试类型

1. **测试类型定义**：
   ```typescript
   // user.test.ts
   import { User, UserRole } from '@/types';
   
   // 使用ExpectTypeOf（来自ts-expect库）
   import { expectTypeOf } from 'ts-expect';
   
   test('User type should have required properties', () => {
       expectTypeOf<User>()
           .toHaveProperty('id')
           .toEqualTypeOf<string>();
           
       expectTypeOf<User>()
           .toHaveProperty('role')
           .toEqualTypeOf<UserRole>();
   });
   
   test('User factory should return valid User type', () => {
       const user = createUser('John', 'john@example.com', 'user');
       
       expectTypeOf(user).toEqualTypeOf<User>();
   });
   ```

2. **测试类型守卫**：
   ```typescript
   // type-guards.test.ts
   import { isUser, isProduct } from '@/type-guards';
   
   test('isUser should correctly identify User objects', () => {
       const validUser = { id: '1', name: 'John', email: 'john@example.com' };
       const invalidUser = { name: 'John' };
       
       if (isUser(validUser)) {
           // TypeScript应该知道validUser是User类型
           expect(validUser.id).toBe('1');
           expectTypeOf(validUser).toEqualTypeOf<User>();
       }
       
       expect(isUser(invalidUser)).toBe(false);
   });
   ```

### 9.5.3 测试实际代码

1. **测试服务类**：
   ```typescript
   // user-service.test.ts
   import { UserService } from '@/services/user-service';
   import { MockUserRepository } from '../mocks/mock-user-repository';
   import { MockLogger } from '../mocks/mock-logger';
   
   describe('UserService', () => {
       let userService: UserService;
       let userRepository: MockUserRepository;
       let logger: MockLogger;
       
       beforeEach(() => {
           userRepository = new MockUserRepository();
           logger = new MockLogger();
           userService = new UserService(userRepository, logger);
       });
       
       it('should create a new user', async () => {
           const userData = {
               name: 'John Doe',
               email: 'john@example.com',
               role: 'user' as const
           };
           
           const user = await userService.createUser(userData);
           
           expect(user.id).toBeDefined();
           expect(user.name).toBe(userData.name);
           expect(user.email).toBe(userData.email);
           expect(user.role).toBe(userData.role);
           expect(user.createdAt).toBeInstanceOf(Date);
           
           // 验证用户已保存到仓库
           const savedUser = await userRepository.findById(user.id);
           expect(savedUser).toEqual(user);
       });
       
       it('should update an existing user', async () => {
           // 创建初始用户
           const user = await userService.createUser({
               name: 'Jane Doe',
               email: 'jane@example.com',
               role: 'user' as const
           });
           
           // 更新用户
           const updates = { name: 'Jane Smith' };
           const updatedUser = await userService.updateUser(user.id, updates);
           
           expect(updatedUser.name).toBe('Jane Smith');
           expect(updatedUser.email).toBe(user.email); // 未更改的字段保持不变
           
           // 验证日志被调用
           expect(logger.log).toHaveBeenCalledWith(
               expect.stringContaining('updated')
           );
       });
   });
   ```

2. **测试API端点**：
   ```typescript
   // user-api.test.ts
   import request from 'supertest';
   import app from '@/app';
   import { setupTestDatabase, cleanupTestDatabase } from '../test-utils';
   
   describe('User API', () => {
       beforeAll(async () => {
           await setupTestDatabase();
       });
       
       afterAll(async () => {
           await cleanupTestDatabase();
       });
       
       it('should create a new user via POST /api/users', async () => {
           const userData = {
               name: 'John Doe',
               email: 'john@example.com',
               role: 'user'
           };
           
           const response = await request(app)
               .post('/api/users')
               .send(userData)
               .expect(201);
               
           expect(response.body).toMatchObject({
               id: expect.any(String),
               name: userData.name,
               email: userData.email,
               role: userData.role
           });
       });
       
       it('should return user details via GET /api/users/:id', async () => {
           // 首先创建一个用户
           const createResponse = await request(app)
               .post('/api/users')
               .send({
                   name: 'Jane Doe',
                   email: 'jane@example.com',
                   role: 'user'
               })
               .expect(201);
               
           const userId = createResponse.body.id;
           
           // 然后获取用户详情
           const getResponse = await request(app)
               .get(`/api/users/${userId}`)
               .expect(200);
               
           expect(getResponse.body).toEqual(createResponse.body);
       });
   });
   ```

---

## 9.6 团队协作中的最佳实践

### 9.6.1 代码风格与规范

1. **使用ESLint和Prettier**：
   ```json
   // .eslintrc.json
   {
       "extends": [
           "@typescript-eslint/recommended",
           "prettier"
       ],
       "parser": "@typescript-eslint/parser",
       "plugins": ["@typescript-eslint"],
       "rules": {
           "@typescript-eslint/no-unused-vars": "error",
           "@typescript-eslint/explicit-function-return-type": "warn",
           "@typescript-eslint/no-explicit-any": "warn",
           "@typescript-eslint/prefer-const": "error"
       }
   }
   ```

2. **创建团队类型指南**：
   ```markdown
   # TypeScript类型指南
   
   ## 命名约定
   - 类型名称使用PascalCase
   - 接口名使用描述性名称，如`IUserProfile`或直接`UserProfile`
   - 类型别名用于简单类型，接口用于复杂对象
   
   ## 类型定义最佳实践
   - 优先使用接口而不是类型别名（除非需要联合类型等）
   - 避免使用`any`，使用`unknown`或更具体的类型
   - 使用泛型提高代码复用性
   ```

### 9.6.2 代码审查流程

1. **TypeScript代码审查清单**：
   - 所有函数都有明确的返回类型吗？
   - 是否存在未处理的null/undefined情况？
   - 是否过度使用了类型断言？
   - 泛型使用是否恰当？
   - 是否有重复的类型定义？
   - 类型定义是否足够具体但又不过于严格？

2. **Pull Request模板**：
   ```markdown
   ## 变更描述
   简要描述此PR所做的变更
   
   ## 类型变更
   - [ ] 新增了类型定义
   - [ ] 修改了现有类型定义
   - [ ] 移除了类型定义
   
   ## 测试
   - [ ] 添加了单元测试
   - [ ] 测试覆盖率未降低
   - [ ] 所有测试通过
   
   ## 类型检查
   - [ ] TypeScript编译无错误
   - [ ] ESLint检查无错误
   ```

### 9.6.3 知识共享与文档

1. **创建类型文档**：
   ```typescript
   /**
    * 用户服务接口
    * 提供用户管理的核心功能
    */
   export interface IUserService {
       /**
        * 创建新用户
        * @param userData 用户数据，不包含id和创建时间
        * @returns 创建成功的用户对象
        * @throws {ValidationError} 当用户数据无效时
        * @throws {DuplicateError} 当邮箱已存在时
        * @example
        * ```typescript
        * const user = await userService.createUser({
        *   name: 'John Doe',
        *   email: 'john@example.com',
        *   role: UserRole.User
        * });
        * ```
        */
       createUser(userData: CreateUserData): Promise<User>;
   }
   ```

2. **维护架构决策记录（ADR）**：
   ```markdown
   # ADR-001: 选择状态管理方案
   
   ## 状态
   已接受
   
   ## 背景
   我们需要为应用选择一个合适的状态管理方案
   
   ## 决策
   选择Zustand作为状态管理库，而不是Redux或MobX
   
   ## 后果
   - 减少了样板代码
   - 提高了开发效率
   - 学习曲线较平缓
   - 与TypeScript集成良好
   ```

---

## 9.7 实战项目：构建一个完整的TypeScript应用

让我们应用以上最佳实践来构建一个完整的TypeScript应用。

### 9.7.1 项目结构

```
task-manager/
├── src/
│   ├── components/           # UI组件
│   │   ├── common/           # 通用组件
│   │   ├── task/             # 任务相关组件
│   │   └── user/             # 用户相关组件
│   ├── pages/                # 页面组件
│   ├── services/             # 服务层
│   │   ├── task.service.ts
│   │   └── user.service.ts
│   ├── store/                # 状态管理
│   │   ├── index.ts
│   │   ├── task-store.ts
│   │   └── user-store.ts
│   ├── types/                # 类型定义
│   │   ├── task.types.ts
│   │   ├── user.types.ts
│   │   └── api.types.ts
│   ├── utils/                # 工具函数
│   ├── constants/            # 常量
│   └── main.ts               # 应用入口
├── tests/                    # 测试文件
├── docs/                     # 文档
├── scripts/                  # 构建脚本
├── config/                   # 配置文件
└── package.json
```

### 9.7.2 类型定义

```typescript
// types/task.types.ts
export interface Task {
    id: string;
    title: string;
    description?: string;
    status: TaskStatus;
    priority: TaskPriority;
    assignee?: string; // 用户ID
    creatorId: string;
    createdAt: Date;
    updatedAt: Date;
    dueDate?: Date;
    tags: string[];
}

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface CreateTaskData {
    title: string;
    description?: string;
    priority: TaskPriority;
    assignee?: string;
    dueDate?: Date;
    tags: string[];
}

export interface UpdateTaskData extends Partial<CreateTaskData> {
    status?: TaskStatus;
}

// 类型守卫
export function isTask(value: unknown): value is Task {
    return (
        value !== null &&
        typeof value === 'object' &&
        'id' in value &&
        'title' in value &&
        typeof (value as any).id === 'string' &&
        typeof (value as any).title === 'string' &&
        ['todo', 'in_progress', 'review', 'done'].includes((value as any).status)
    );
}
```

```typescript
// types/user.types.ts
export interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
    role: UserRole;
    createdAt: Date;
    updatedAt: Date;
}

export type UserRole = 'admin' | 'manager' | 'member';

export interface CreateUserData {
    name: string;
    email: string;
    role: UserRole;
}
```

### 9.7.3 服务层

```typescript
// services/task.service.ts
import { Task, CreateTaskData, UpdateTaskData } from '../types/task.types';
import { HttpClient } from './http-client';

export class TaskService {
    constructor(private http: HttpClient) {}
    
    async getTasks(): Promise<Task[]> {
        return this.http.get<Task[]>('/api/tasks');
    }
    
    async getTask(id: string): Promise<Task | null> {
        try {
            return await this.http.get<Task>(`/api/tasks/${id}`);
        } catch (error) {
            if (error.statusCode === 404) {
                return null;
            }
            throw error;
        }
    }
    
    async createTask(taskData: CreateTaskData): Promise<Task> {
        return this.http.post<Task>('/api/tasks', taskData);
    }
    
    async updateTask(id: string, updates: UpdateTaskData): Promise<Task> {
        return this.http.put<Task>(`/api/tasks/${id}`, updates);
    }
    
    async deleteTask(id: string): Promise<void> {
        return this.http.delete(`/api/tasks/${id}`);
    }
    
    async assignTask(taskId: string, userId: string): Promise<Task> {
        return this.http.put<Task>(`/api/tasks/${taskId}/assign`, { userId });
    }
}
```

### 9.7.4 状态管理

```typescript
// store/task-store.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Task, TaskStatus } from '../types/task.types';
import { TaskService } from '../services/task.service';

interface TaskState {
    tasks: Task[];
    loading: boolean;
    error: string | null;
    
    // Actions
    fetchTasks: () => Promise<void>;
    fetchTask: (id: string) => Promise<Task | null>;
    createTask: (taskData: CreateTaskData) => Promise<void>;
    updateTask: (id: string, updates: UpdateTaskData) => Promise<void>;
    deleteTask: (id: string) => Promise<void>;
    filterByStatus: (status: TaskStatus) => Task[];
    clearError: () => void;
}

export const useTaskStore = create<TaskState>()(
    devtools((set, get) => ({
        tasks: [],
        loading: false,
        error: null,
        
        fetchTasks: async () => {
            set({ loading: true, error: null });
            try {
                const taskService = new TaskService(new HttpClient());
                const tasks = await taskService.getTasks();
                set({ tasks, loading: false });
            } catch (error) {
                set({
                    loading: false,
                    error: error instanceof Error ? error.message : 'Failed to fetch tasks'
                });
            }
        },
        
        fetchTask: async (id) => {
            try {
                const taskService = new TaskService(new HttpClient());
                const task = await taskService.getTask(id);
                
                if (task) {
                    set(state => ({
                        tasks: state.tasks.some(t => t.id === id)
                            ? state.tasks.map(t => t.id === id ? task : t)
                            : [...state.tasks, task]
                    }));
                }
                
                return task;
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to fetch task'
                });
                return null;
            }
        },
        
        createTask: async (taskData) => {
            set({ loading: true, error: null });
            try {
                const taskService = new TaskService(new HttpClient());
                const newTask = await taskService.createTask(taskData);
                
                set(state => ({
                    tasks: [...state.tasks, newTask],
                    loading: false
                }));
            } catch (error) {
                set({
                    loading: false,
                    error: error instanceof Error ? error.message : 'Failed to create task'
                });
            }
        },
        
        updateTask: async (id, updates) => {
            try {
                const taskService = new TaskService(new HttpClient());
                const updatedTask = await taskService.updateTask(id, updates);
                
                set(state => ({
                    tasks: state.tasks.map(t => t.id === id ? updatedTask : t)
                }));
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to update task'
                });
            }
        },
        
        deleteTask: async (id) => {
            try {
                const taskService = new TaskService(new HttpClient());
                await taskService.deleteTask(id);
                
                set(state => ({
                    tasks: state.tasks.filter(t => t.id !== id)
                }));
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : 'Failed to delete task'
                });
            }
        },
        
        filterByStatus: (status) => {
            const { tasks } = get();
            return tasks.filter(task => task.status === status);
        },
        
        clearError: () => set({ error: null })
    }))
);
```

### 9.7.5 组件

```typescript
// components/task/TaskCard.tsx
import React from 'react';
import { Task } from '../../types/task.types';
import { TaskPriorityBadge } from './TaskPriorityBadge';
import { TaskStatusBadge } from './TaskStatusBadge';

interface TaskCardProps {
    task: Task;
    onEdit?: (task: Task) => void;
    onDelete?: (id: string) => void;
    onStatusChange?: (id: string, status: Task['status']) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
    task,
    onEdit,
    onDelete,
    onStatusChange
}) => {
    const handleDelete = () => {
        if (onDelete && window.confirm('确定要删除这个任务吗？')) {
            onDelete(task.id);
        }
    };
    
    const handleStatusChange = (status: Task['status']) => {
        if (onStatusChange) {
            onStatusChange(task.id, status);
        }
    };
    
    return (
        <div className="task-card">
            <div className="task-header">
                <h3 className="task-title">{task.title}</h3>
                <div className="task-badges">
                    <TaskPriorityBadge priority={task.priority} />
                    <TaskStatusBadge status={task.status} />
                </div>
            </div>
            
            {task.description && (
                <p className="task-description">{task.description}</p>
            )}
            
            <div className="task-meta">
                {task.dueDate && (
                    <div className="task-due-date">
                        截止日期: {formatDate(task.dueDate)}
                    </div>
                )}
                {task.tags.length > 0 && (
                    <div className="task-tags">
                        {task.tags.map(tag => (
                            <span key={tag} className="task-tag">
                                {tag}
                            </span>
                        ))}
                    </div>
                )}
            </div>
            
            <div className="task-actions">
                <button 
                    className="btn btn-secondary" 
                    onClick={() => onEdit && onEdit(task)}
                >
                    编辑
                </button>
                
                <select 
                    value={task.status} 
                    onChange={(e) => handleStatusChange(e.target.value as Task['status'])}
                    className="status-select"
                >
                    <option value="todo">待办</option>
                    <option value="in_progress">进行中</option>
                    <option value="review">审核中</option>
                    <option value="done">已完成</option>
                </select>
                
                <button 
                    className="btn btn-danger" 
                    onClick={handleDelete}
                >
                    删除
                </button>
            </div>
        </div>
    );
};

function formatDate(date: Date): string {
    return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}
```

### 9.7.6 测试

```typescript
// services/task.service.test.ts
import { TaskService } from '../services/task.service';
import { MockHttpClient } from '../mocks/mock-http-client';
import { CreateTaskData, UpdateTaskData, TaskStatus } from '../types/task.types';

describe('TaskService', () => {
    let taskService: TaskService;
    let httpClient: MockHttpClient;
    
    beforeEach(() => {
        httpClient = new MockHttpClient();
        taskService = new TaskService(httpClient);
    });
    
    describe('getTasks', () => {
        it('should return tasks from API', async () => {
            const mockTasks = [
                {
                    id: '1',
                    title: 'Test Task',
                    status: 'todo' as TaskStatus,
                    priority: 'medium',
                    creatorId: 'user1',
                    createdAt: new Date(),
                    updatedAt: new Date(),
                    tags: []
                }
            ];
            
            httpClient.get.mockResolvedValue(mockTasks);
            
            const tasks = await taskService.getTasks();
            
            expect(tasks).toEqual(mockTasks);
            expect(httpClient.get).toHaveBeenCalledWith('/api/tasks');
        });
    });
    
    describe('createTask', () => {
        it('should create a new task', async () => {
            const taskData: CreateTaskData = {
                title: 'New Task',
                priority: 'high',
                tags: []
            };
            
            const createdTask = {
                ...taskData,
                id: 'new-id',
                status: 'todo' as TaskStatus,
                creatorId: 'user1',
                createdAt: new Date(),
                updatedAt: new Date()
            };
            
            httpClient.post.mockResolvedValue(createdTask);
            
            const result = await taskService.createTask(taskData);
            
            expect(result).toEqual(createdTask);
            expect(httpClient.post).toHaveBeenCalledWith('/api/tasks', taskData);
        });
    });
    
    describe('updateTask', () => {
        it('should update an existing task', async () => {
            const taskId = '1';
            const updates: UpdateTaskData = {
                status: 'in_progress'
            };
            
            const updatedTask = {
                id: taskId,
                title: 'Test Task',
                status: 'in_progress' as TaskStatus,
                priority: 'medium',
                creatorId: 'user1',
                createdAt: new Date(),
                updatedAt: new Date(),
                tags: []
            };
            
            httpClient.put.mockResolvedValue(updatedTask);
            
            const result = await taskService.updateTask(taskId, updates);
            
            expect(result).toEqual(updatedTask);
            expect(httpClient.put).toHaveBeenCalledWith(`/api/tasks/${taskId}`, updates);
        });
    });
});
```

---

## 本章小结

在本章中，我们探讨了TypeScript工程实践与最佳实践的多个方面。从项目架构设计到性能优化，从测试策略到团队协作，我们学习了如何构建高质量、可维护的TypeScript应用程序。

主要收获包括：

1. 理解了如何设计大型TypeScript项目的架构
2. 掌握了TypeScript编译器的配置与优化技巧
3. 学会了如何组织代码和实现模块化
4. 了解了性能优化的实用方法
5. 掌握了TypeScript项目的测试策略
6. 理解了团队协作中的最佳实践

通过应用这些实践，您将能够构建更加健壮、可扩展和高效的TypeScript应用程序。在最后一章中，我们将探讨TypeScript与前端框架的集成，进一步巩固TypeScript在实际项目中的应用。