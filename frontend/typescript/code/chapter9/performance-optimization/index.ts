// 性能优化示例入口文件

import { 
    UserRole, 
    UserType, 
    ProcessingData,
    processData, 
    processItems, 
    formatValue, 
    processArrayItems, 
    processReadOnlyData,
    updateUser,
    User
} from './performance-tips';

/**
 * 演示类型别名代替接口
 */
function demonstrateTypeAliases() {
    console.log("=== 类型别名代替接口示例 ===");
    
    const userId: string = "user123";
    const status: UserType = 'admin';
    
    console.log(`用户ID: ${userId}, 状态: ${status}`);
}

/**
 * 演示处理复杂数据
 */
function demonstrateDataProcessing() {
    console.log("\n=== 数据处理示例 ===");
    
    const processingData: ProcessingData = {
        input: { key: 'value' },
        options: {
            strict: true,
            timeout: 5000,
            retries: 3
        },
        metadata: {
            source: 'user-input',
            timestamp: new Date()
        }
    };
    
    processData(processingData);
    console.log("数据处理完成");
}

/**
 * 演示格式化值
 */
function demonstrateValueFormatting() {
    console.log("\n=== 值格式化示例 ===");
    
    const values = [
        "  hello world  ",
        42.5678,
        true,
        new Date()
    ];
    
    values.forEach(value => {
        const formatted = formatValue(value);
        console.log(`原始值: ${JSON.stringify(value)} -> 格式化后: "${formatted}"`);
    });
}

/**
 * 演示项目处理
 */
function demonstrateItemProcessing() {
    console.log("\n=== 项目处理示例 ===");
    
    // 模拟一些数据
    const unknownData = [
        { id: '1', name: 'Item 1' },
        { id: '2', name: 'Item 2' },
        { id: '3', name: 'Item 3' },
        { id: '4', name: 'Item 4' }
    ];
    
    try {
        // 预先验证数据
        const items = processItems(unknownData);
        console.log(`成功处理 ${items.length} 个项目`);
        
        // 使用类型断言处理已知安全的数据
        processArrayItems(unknownData);
        console.log("使用类型断言处理完成");
        
    } catch (error) {
        console.error("处理项目时出错:", error);
    }
}

/**
 * 演示只读数据处理
 */
function demonstrateReadOnlyDataProcessing() {
    console.log("\n=== 只读数据处理示例 ===");
    
    const items = [
        { id: '1', name: 'Read-only Item 1' },
        { id: '2', name: 'Read-only Item 2' }
    ] as const; // 使数组成为只读
    
    processReadOnlyData(items);
    console.log("只读数据处理完成");
}

/**
 * 演示用户更新
 */
function demonstrateUserUpdate() {
    console.log("\n=== 用户更新示例 ===");
    
    // 模拟现有用户
    const existingUser: User = {
        id: '123',
        name: 'John Doe',
        email: 'john@example.com',
        role: 'user',
        createdAt: new Date('2023-01-01'),
        updatedAt: new Date('2023-01-01')
    };
    
    // 使用Partial<User>进行更新
    try {
        const updatedUser = updateUser('123', {
            name: 'John Smith',
            role: 'admin'
        });
        
        console.log("用户更新成功:");
        console.log(`名称: ${existingUser.name} -> ${updatedUser.name}`);
        console.log(`角色: ${existingUser.role} -> ${updatedUser.role}`);
        
    } catch (error) {
        console.error("更新用户失败:", error);
    }
}

/**
 * 运行所有示例
 */
function runAllExamples() {
    console.log("TypeScript性能优化示例");
    console.log("========================");
    
    demonstrateTypeAliases();
    demonstrateDataProcessing();
    demonstrateValueFormatting();
    demonstrateItemProcessing();
    demonstrateReadOnlyDataProcessing();
    demonstrateUserUpdate();
    
    console.log("\n=== 所有示例完成 ===");
}

// 运行示例
runAllExamples();