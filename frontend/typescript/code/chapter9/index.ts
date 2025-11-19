// 第9章：TypeScript工程实践与最佳实践 - 主入口文件

// 导入项目结构示例
import { createContainer } from './project-structure/src/di-container';
import { Logger } from './project-structure/src/interfaces/logger.interface';
import { UserService } from './project-structure/src/services/user-service';

// 导入性能优化示例
import { 
    UserRole, 
    UserType, 
    ProcessingData,
    processData, 
    formatValue,
    updateUser
} from './performance-optimization/performance-tips';

/**
 * 演示项目结构示例
 */
async function demonstrateProjectStructure() {
    console.log("=== TypeScript项目结构示例 ===");
    
    // 创建依赖注入容器
    const container = createContainer();
    
    // 获取服务
    const logger = container.resolve<Logger>('logger');
    const userService = container.resolve<UserService>('userService');
    
    // 设置日志级别
    logger.setLevel('info');
    
    // 创建测试用户
    const userData = {
        name: '张三',
        email: 'zhangsan@example.com',
        role: 'admin' as UserType
    };
    
    try {
        const user = await userService.createUser(userData);
        console.log(`创建用户成功: ${user.name} (${user.email})`);
        
        // 获取用户
        const fetchedUser = await userService.getUserById(user.id);
        if (fetchedUser) {
            console.log(`获取用户成功: ${fetchedUser.name}`);
        }
        
        // 更新用户
        const updatedUser = await userService.updateUser(user.id, { name: '张三(已更新)' });
        console.log(`更新用户成功: ${updatedUser.name}`);
        
    } catch (error) {
        console.error('用户操作失败:', error);
    }
}

/**
 * 演示性能优化示例
 */
function demonstratePerformanceOptimization() {
    console.log("\n=== TypeScript性能优化示例 ===");
    
    // 演示类型别名
    const userId: string = "user123";
    const userRole: UserType = 'admin';
    console.log(`用户ID: ${userId}, 角色: ${userRole}`);
    
    // 演示数据处理
    const processingData: ProcessingData = {
        input: { key: 'value' },
        options: {
            strict: true,
            timeout: 5000
        }
    };
    processData(processingData);
    console.log("数据处理完成");
    
    // 演示值格式化
    const formattedString = formatValue("  hello world  ");
    const formattedNumber = formatValue(42.5678);
    console.log(`字符串格式化: "  hello world  " -> "${formattedString}"`);
    console.log(`数字格式化: 42.5678 -> "${formattedNumber}"`);
    
    // 演示用户更新
    const mockUser = {
        id: '123',
        name: 'John Doe',
        email: 'john@example.com',
        role: 'user' as UserType,
        createdAt: new Date(),
        updatedAt: new Date()
    };
    
    try {
        // 注意：这个函数在原始文件中需要findUserById函数，这里我们模拟一下
        console.log("模拟用户更新操作");
    } catch (error) {
        console.error("用户更新失败:", error);
    }
}

/**
 * 演示工程实践原则
 */
function demonstrateEngineeringPrinciples() {
    console.log("\n=== 工程实践原则示例 ===");
    
    // 1. 单一职责原则
    console.log("1. 单一职责原则: 每个类/模块只负责一个功能");
    console.log("   - Logger只负责日志记录");
    console.log("   - Database只负责数据存储");
    console.log("   - UserService只负责用户业务逻辑");
    
    // 2. 开放封闭原则
    console.log("\n2. 开放封闭原则: 对扩展开放，对修改封闭");
    console.log("   - 通过接口定义契约，允许不同实现");
    console.log("   - 添加新的日志实现不需要修改现有代码");
    
    // 3. 依赖倒置原则
    console.log("\n3. 依赖倒置原则: 高层模块不依赖低层模块，都依赖抽象");
    console.log("   - UserService依赖Logger和Database接口");
    console.log("   - 不依赖具体的ConsoleLogger或MemoryDatabase实现");
    
    // 4. 接口隔离原则
    console.log("\n4. 接口隔离原则: 客户端不应依赖不需要的接口");
    console.log("   - Logger接口只包含日志相关方法");
    console.log("   - Database接口只包含数据操作方法");
    
    // 5. 类型安全
    console.log("\n5. 类型安全: 使用TypeScript类型系统确保类型安全");
    console.log("   - 使用明确的类型定义");
    console.log("   - 使用类型守卫验证运行时类型");
    console.log("   - 使用泛型提高代码复用性");
    
    // 6. 代码组织
    console.log("\n6. 代码组织: 清晰的项目结构和模块划分");
    console.log("   - 按功能模块组织代码");
    console.log("   - 使用依赖注入管理组件");
    console.log("   - 清晰的导入导出规则");
}

/**
 * 运行所有示例
 */
async function runAllExamples() {
    console.log("TypeScript工程实践与最佳实践示例");
    console.log("================================");
    
    await demonstrateProjectStructure();
    demonstratePerformanceOptimization();
    demonstrateEngineeringPrinciples();
    
    console.log("\n=== 所有示例完成 ===");
    console.log("\n最佳实践总结:");
    console.log("1. 使用依赖注入实现松耦合");
    console.log("2. 优先使用接口定义契约");
    console.log("3. 适当使用类型别名和泛型");
    console.log("4. 使用类型守卫确保类型安全");
    console.log("5. 避免在热路径中进行复杂类型检查");
    console.log("6. 遵循SOLID原则设计类和模块");
    console.log("7. 使用明确的项目结构组织代码");
    console.log("8. 定期进行代码审查和重构");
}

// 运行示例
runAllExamples().catch(console.error);