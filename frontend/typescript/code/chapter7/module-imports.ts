// 模块导入示例
import { PI, add, subtract, Calculator, pow as power } from './math';
import ScientificCalculator from './math';
import { Point, Circle, Rectangle, Triangle, distance, circleArea, rectangleArea, triangleArea } from './geometry';
import { Logger, LogLevel } from './logger';
import type { User, CreateUserRequest, UpdateUserRequest } from './user';

// 测试数学模块
function testMathModule() {
    console.log("=== Testing Math Module ===");
    console.log(`PI value: ${PI}`);
    console.log(`add(5, 3): ${add(5, 3)}`);
    console.log(`subtract(10, 4): ${subtract(10, 4)}`);
    console.log(`power(2, 3): ${power(2, 3)}`);
    
    const calc = new Calculator();
    console.log(`Chain calculation: ${calc.add(10).multiply(2).subtract(5).getResult()}`);
    
    const scientificResult = ScientificCalculator.factorial(5);
    console.log(`5! = ${scientificResult}`);
}

// 测试几何模块
function testGeometryModule() {
    console.log("\n=== Testing Geometry Module ===");
    
    const point1: Point = { x: 0, y: 0 };
    const point2: Point = { x: 3, y: 4 };
    
    console.log(`Distance between points: ${distance(point1, point2)}`);
    
    const circle: Circle = { center: { x: 0, y: 0 }, radius: 5 };
    console.log(`Circle area: ${circleArea(circle)}`);
    
    const rectangle: Rectangle = { 
        topLeft: { x: 0, y: 0 }, 
        bottomRight: { x: 10, y: 5 } 
    };
    console.log(`Rectangle area: ${rectangleArea(rectangle)}`);
    
    const triangle: Triangle = [
        { x: 0, y: 0 },
        { x: 4, y: 0 },
        { x: 2, y: 3 }
    ];
    console.log(`Triangle area: ${triangleArea(triangle)}`);
}

// 测试日志模块
function testLoggerModule() {
    console.log("\n=== Testing Logger Module ===");
    
    const logger = new Logger(LogLevel.DEBUG);
    
    logger.debug("This is a debug message");
    logger.info("This is an info message");
    logger.warn("This is a warning message");
    logger.error("This is an error message");
    
    // 设置不同的日志级别
    logger.setLogLevel(LogLevel.WARN);
    console.log("\nAfter setting log level to WARN:");
    
    logger.debug("This debug message won't be shown");
    logger.info("This info message won't be shown");
    logger.warn("This warning will be shown");
    logger.error("This error will be shown");
}

// 测试用户模块
function testUserModule() {
    console.log("\n=== Testing User Module ===");
    
    const logger = new Logger(LogLevel.INFO);
    const userService = new UserService(logger);
    
    // 创建用户
    const user1Data: CreateUserRequest = {
        name: "Alice",
        email: "alice@example.com",
        avatar: "alice.jpg"
    };
    
    const user1 = userService.create(user1Data);
    console.log("Created user:", user1);
    
    const user2Data: CreateUserRequest = {
        name: "Bob",
        email: "bob@example.com"
    };
    
    const user2 = userService.create(user2Data);
    console.log("Created user:", user2);
    
    // 查找用户
    const foundUser = userService.findById(1);
    console.log("Found user by ID 1:", foundUser);
    
    // 查找所有用户
    const allUsers = userService.findAll();
    console.log("All users:", allUsers);
    
    // 更新用户
    const updatedUser = userService.update(1, {
        name: "Alice Smith",
        avatar: "alice-smith.jpg"
    });
    console.log("Updated user:", updatedUser);
    
    // 尝试重复邮箱
    try {
        userService.create({
            name: "Charlie",
            email: "alice@example.com"
        });
    } catch (error) {
        console.log("Error creating user with duplicate email:", (error as Error).message);
    }
    
    // 删除用户
    const deleted = userService.delete(2);
    console.log("User deleted:", deleted);
    
    const remainingUsers = userService.findAll();
    console.log("Remaining users:", remainingUsers);
}

// 导入到命名空间
import * as MathModule from './math';
import * as GeometryModule from './geometry';
import * as LoggerModule from './logger';

function testNamespaceImports() {
    console.log("\n=== Testing Namespace Imports ===");
    
    // 使用命名空间导入
    console.log(`MathModule.PI: ${MathModule.PI}`);
    console.log(`MathModule.add(2, 3): ${MathModule.add(2, 3)}`);
    
    const namespaceCalc = new MathModule.Calculator();
    console.log(`Namespace chain calculation: ${namespaceCalc.add(5).multiply(3).getResult()}`);
    
    const namespacePoint: GeometryModule.Point = { x: 1, y: 1 };
    const namespaceCircle: GeometryModule.Circle = { center: namespacePoint, radius: 2 };
    console.log(`Namespace circle area: ${GeometryModule.circleArea(namespaceCircle)}`);
    
    const namespaceLogger = new LoggerModule.Logger(LoggerModule.LogLevel.INFO);
    namespaceLogger.info("Logging with namespace import");
}

// 动态导入示例
async function testDynamicImports() {
    console.log("\n=== Testing Dynamic Imports ===");
    
    // 动态导入模块
    console.log("Dynamically importing math module...");
    const mathModule = await import('./math');
    console.log(`Dynamic add result: ${mathModule.add(10, 20)}`);
    
    console.log("Dynamically importing geometry module...");
    const geometryModule = await import('./geometry');
    
    const dynamicPoint: typeof geometryModule.Point = { x: 0, y: 0 };
    const dynamicCircle: typeof geometryModule.Circle = { center: dynamicPoint, radius: 5 };
    console.log(`Dynamic circle area: ${geometryModule.circleArea(dynamicCircle)}`);
    
    // 条件导入
    const useAdvancedMath = Math.random() > 0.5;
    
    if (useAdvancedMath) {
        console.log("Loading advanced math features...");
        // 这里可以动态导入更高级的数学模块
        // const advancedMath = await import('./advanced-math');
    } else {
        console.log("Using basic math features");
    }
}

// 重新导出示例
// api/index.ts
// export * from './user-api';
// export * from './product-api';
// export * from './order-api';

// 选择性重新导出
// api/index.ts
// export { UserService } from './user-api';
// export { ProductService } from './product-api';
// export { OrderService } from './order-api';

// 默认导出示例
// api/user-service.ts
// export default class UserService {
//     // 实现
// }

// main.ts
// import UserService from './api/user-service';

// 模块与命名空间的组合
// 有时可能需要将模块内容添加到命名空间中
// 在实际项目中，这种模式不推荐，但在与旧代码集成时可能有用

namespace App {
    export namespace Models {
        // 从模块中导入并重新导出
        export type { User, CreateUserRequest, UpdateUserRequest } from './user';
        export type { Product } from './product';
        export type { Order } from './order';
    }
    
    export namespace Services {
        export { Logger, LogLevel } from './logger';
        export { UserService } from './user';
    }
    
    export namespace Utils {
        export { PI, add, subtract, multiply, divide, Calculator, ScientificCalculator, pow as power } from './math';
        export { Point, Circle, Rectangle, Triangle, distance, circleArea, rectangleArea, triangleArea } from './geometry';
    }
}

function testNamespaceModuleCombination() {
    console.log("\n=== Testing Namespace Module Combination ===");
    
    // 使用组合的命名空间
    const userData: App.Models.CreateUserRequest = {
        name: "David",
        email: "david@example.com"
    };
    
    const appLogger = new App.Services.Logger(App.Services.LogLevel.INFO);
    appLogger.info("Using combined namespace and module system");
    
    const appMathCalc = new App.Utils.Calculator();
    const result = appMathCalc.add(10).multiply(2).getResult();
    console.log(`Combined namespace calculation: ${result}`);
}

// 执行所有测试
function runAllTests() {
    testMathModule();
    testGeometryModule();
    testLoggerModule();
    testUserModule();
    testNamespaceImports();
    testDynamicImports();
    testNamespaceModuleCombination();
}

// 导出测试函数供外部使用
export {
    testMathModule,
    testGeometryModule,
    testLoggerModule,
    testUserModule,
    testNamespaceImports,
    testDynamicImports,
    testNamespaceModuleCombination,
    runAllTests
};

// 如果直接运行此文件，执行所有测试
if (require.main === module) {
    runAllTests();
}