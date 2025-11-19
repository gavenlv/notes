# 1. TypeScript简介与环境搭建

## 1.1 什么是TypeScript

TypeScript是Microsoft开发的开源编程语言，它是JavaScript的超集，添加了静态类型检查和最新的ECMAScript特性。简单来说，所有合法的JavaScript代码都是合法的TypeScript代码，但TypeScript提供了更强大的工具和功能。

### 1.1.1 TypeScript的起源与发展

TypeScript于2012年首次发布，由Anders Hejlsberg（C#首席架构师）领导的团队开发。它的创建初衷是为了解决JavaScript在大规模、复杂应用开发中遇到的挑战，如类型安全性差、IDE支持不足等问题。

随着时间的推移，TypeScript获得了广泛应用和强大社区支持，成为前端开发的主流选择之一。

### 1.1.2 为什么选择TypeScript

选择TypeScript有几个关键优势：

1. **静态类型检查**：在编译阶段发现潜在错误，减少运行时异常
2. **更好的IDE支持**：提供智能提示、重构、导航等功能
3. **代码可维护性**：类型注解使代码意图更清晰
4. **最新的ES特性**：可以使用最新的JavaScript特性，同时兼容旧环境
5. **更好的团队协作**：明确的类型定义有助于团队理解和维护代码

## 1.2 TypeScript vs JavaScript

让我们通过一个简单的例子来理解TypeScript和JavaScript的区别：

### JavaScript示例
```javascript
// JavaScript - 没有类型检查
function calculateArea(width, height) {
    return width * height;
}

// 可能的错误：传入字符串而不是数字
let result = calculateArea("10", 20); // 结果是 "200" (字符串拼接)
console.log(result); // 输出: "200"
```

### TypeScript示例
```typescript
// TypeScript - 有类型检查
function calculateArea(width: number, height: number): number {
    return width * height;
}

// 类型检查会捕获这个错误
let result = calculateArea("10", 20); // 编译错误：类型"string"不能分配给类型"number"
```

## 1.3 TypeScript的核心特性

### 1.3.1 静态类型

TypeScript最核心的特性是静态类型。我们可以为变量、函数参数和返回值指定类型：

```typescript
// 变量类型注解
let message: string = "Hello, TypeScript!";
let count: number = 10;
let isActive: boolean = true;

// 函数类型注解
function greet(name: string): string {
    return `Hello, ${name}!`;
}
```

### 1.3.2 类型推断

TypeScript能够根据上下文自动推断变量的类型，减少冗余的类型注解：

```typescript
// TypeScript可以推断出message的类型是string
let message = "Hello, TypeScript!"; // 不需要显式指定string类型

// 函数返回类型也可以被推断
function add(a: number, b: number) {
    return a + b; // TypeScript推断返回值类型为number
}
```

### 1.3.3 接口与类型别名

TypeScript提供了定义复杂类型结构的方式：

```typescript
// 接口定义
interface Person {
    name: string;
    age: number;
    greet(): string;
}

// 使用接口
let user: Person = {
    name: "Alice",
    age: 30,
    greet() {
        return `Hi, I'm ${this.name}`;
    }
};
```

### 1.3.4 类与继承

TypeScript提供了完整的面向对象编程支持：

```typescript
class Animal {
    protected name: string;

    constructor(name: string) {
        this.name = name;
    }

    move(distance: number = 0): void {
        console.log(`${this.name} moved ${distance}m`);
    }
}

class Dog extends Animal {
    constructor(name: string) {
        super(name);
    }

    bark(): void {
        console.log(`${this.name} barks!`);
    }
}

const dog = new Dog("Buddy");
dog.bark(); // Buddy barks!
dog.move(10); // Buddy moved 10m
```

## 1.4 TypeScript的生态系统

### 1.4.1 编译器(tsc)

TypeScript编译器(tsc)将TypeScript代码转换为JavaScript代码，可以在任何支持JavaScript的环境中运行。

### 1.4.2 DefinitelyTyped

DefinitelyTyped是一个社区驱动的项目，为JavaScript库提供TypeScript类型定义。通过`@types`包，我们可以为各种JavaScript库添加类型支持。

### 1.4.3 编辑器支持

主流编辑器如Visual Studio Code、WebStorm等都对TypeScript提供了优秀支持，包括：
- 智能提示
- 错误检查
- 重构功能
- 代码导航

## 1.5 安装与环境搭建

### 1.5.1 安装Node.js和npm

在开始使用TypeScript之前，需要安装Node.js和npm（Node包管理器）。访问[Node.js官网](https://nodejs.org/)下载并安装LTS版本。

安装完成后，可以通过以下命令验证安装：

```bash
node -v
npm -v
```

### 1.5.2 全局安装TypeScript

使用npm全局安装TypeScript编译器：

```bash
npm install -g typescript
```

安装完成后，验证TypeScript版本：

```bash
tsc -v
```

### 1.5.3 创建TypeScript项目

1. 创建项目目录
```bash
mkdir my-typescript-project
cd my-typescript-project
```

2. 初始化npm项目
```bash
npm init -y
```

3. 安装TypeScript作为开发依赖
```bash
npm install typescript --save-dev
```

4. 创建TypeScript配置文件
```bash
npx tsc --init
```

这会创建一个`tsconfig.json`文件，用于配置TypeScript编译选项。

### 1.5.4 配置TypeScript编译选项

`tsconfig.json`文件的基本配置如下：

```json
{
  "compilerOptions": {
    "target": "es6",                // 编译目标JavaScript版本
    "module": "commonjs",           // 模块系统
    "outDir": "./dist",             // 输出目录
    "rootDir": "./src",             // 源代码根目录
    "strict": true,                 // 启用所有严格类型检查选项
    "esModuleInterop": true,        // 允许更好的模块互操作性
    "skipLibCheck": true,           // 跳过声明文件检查
    "forceConsistentCasingInFileNames": true // 强制文件名大小写一致
  },
  "include": ["src/**/*"],          // 包含的文件
  "exclude": ["node_modules", "**/*.spec.ts"] // 排除的文件
}
```

## 1.6 开发工具设置

### 1.6.1 Visual Studio Code配置

Visual Studio Code是开发TypeScript应用的最佳选择。安装以下扩展以获得更好的开发体验：

- TypeScript Importer：自动导入模块
- TSLint：TypeScript代码检查工具
- Prettier：代码格式化工具
- Auto Rename Tag：自动重命名配对标签

### 1.6.2 配置任务和调试

在VS Code中，可以创建`tasks.json`来配置编译任务：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "type": "typescript",
            "tsconfig": "tsconfig.json",
            "option": "watch",
            "problemMatcher": [
                "$tsc-watch"
            ],
            "group": "build",
            "label": "tsc: watch - tsconfig.json"
        }
    ]
}
```

## 1.7 第一个TypeScript程序

让我们创建一个简单的TypeScript程序来体验开发流程。

### 1.7.1 创建源代码文件

在项目根目录创建`src`目录，并在其中创建`main.ts`文件：

```typescript
// src/main.ts
function greet(name: string): string {
    return `Hello, ${name}!`;
}

const user = "TypeScript";
console.log(greet(user));
```

### 1.7.2 编译TypeScript代码

使用以下命令编译TypeScript代码：

```bash
npx tsc
```

这会将`src/main.ts`编译为`dist/main.js`。

### 1.7.3 运行编译后的JavaScript代码

```bash
node dist/main.js
```

输出：
```
Hello, TypeScript!
```

### 1.7.4 监视模式

在开发过程中，可以使用监视模式自动编译修改的文件：

```bash
npx tsc -w
```

这样，每次保存TypeScript文件时，它都会自动重新编译。

## 1.8 TypeScript开发工作流

### 1.8.1 开发流程

典型的TypeScript开发流程如下：

1. 编写TypeScript代码
2. 使用IDE获得实时反馈和智能提示
3. 保存文件时自动编译（使用监视模式）
4. 测试JavaScript输出
5. 重复以上步骤

### 1.8.2 使用ts-node直接运行TypeScript

`ts-node`是一个可以直接运行TypeScript代码的工具，无需显式编译：

1. 安装ts-node
```bash
npm install -g ts-node
```

2. 直接运行TypeScript文件
```bash
ts-node src/main.ts
```

这对于快速原型开发和测试非常方便。

## 1.9 常见问题与解决方案

### 1.9.1 编译错误处理

常见的TypeScript编译错误及解决方法：

1. **类型不匹配错误**
```typescript
// 错误
let count: number = "hello"; // Type 'string' is not assignable to type 'number'

// 解决：确保类型匹配或使用类型断言
let count: number = parseInt("hello", 10) || 0;
```

2. **属性不存在错误**
```typescript
// 错误
const person = { name: "Alice" };
console.log(person.age); // Property 'age' does not exist on type '{ name: string; }'

// 解决：使用接口定义或可选属性
interface Person {
    name: string;
    age?: number; // 可选属性
}
```

### 1.9.2 性能优化

对于大型项目，可以考虑以下优化策略：

1. 增量编译：只编译修改过的文件
2. 项目引用：将大型项目分解为多个小项目
3. 使用`ts-loader`或`esbuild`加速构建过程

## 1.10 总结

TypeScript通过添加静态类型和其他高级特性，极大地增强了JavaScript的开发体验，使代码更可靠、更易维护。在这一章中，我们学习了：

- TypeScript是什么以及为什么选择它
- TypeScript与JavaScript的主要区别
- TypeScript的核心特性
- 如何搭建TypeScript开发环境
- 基本的TypeScript开发工作流

在接下来的章节中，我们将深入探索TypeScript的类型系统、面向对象编程、高级类型特性等主题，帮助您从TypeScript新手成长为专家。

## 1.11 练习

1. 创建一个TypeScript项目，配置适当的编译选项
2. 编写一个简单的TypeScript程序，包含函数、变量和基本类型
3. 尝试使用ts-node直接运行TypeScript代码
4. 创建一个接口定义一个复杂的对象类型，并使用它

通过完成这些练习，您将熟悉TypeScript的基本环境和开发流程，为后续学习打下坚实基础。