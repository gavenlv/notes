// 项目入口文件

import { createContainer } from './di-container';
import { Logger } from './interfaces/logger.interface';
import { UserService } from './services/user-service';
import { isUser, CreateUserData } from './types/user.types';

/**
 * 初始化应用程序
 */
async function initializeApp() {
    console.log("=== TypeScript工程实践示例 ===");
    
    // 创建依赖注入容器
    const container = createContainer();
    
    // 获取服务
    const logger = container.resolve<Logger>('logger');
    const userService = container.resolve<UserService>('userService');
    
    // 设置日志级别
    logger.setLevel('info');
    
    // 创建一些测试用户
    console.log("\n1. 创建测试用户");
    const testUsers: CreateUserData[] = [
        { name: '张三', email: 'zhangsan@example.com', role: 'admin' },
        { name: '李四', email: 'lisi@example.com', role: 'manager' },
        { name: '王五', email: 'wangwu@example.com', role: 'member' }
    ];
    
    const createdUsers = [];
    
    for (const userData of testUsers) {
        try {
            const user = await userService.createUser(userData);
            createdUsers.push(user);
            console.log(`✓ 创建用户: ${user.name} (${user.email})`);
        } catch (error) {
            console.error(`✗ 创建用户失败: ${error}`);
        }
    }
    
    // 获取用户列表
    console.log("\n2. 获取用户列表");
    try {
        const users = await userService.getUsers();
        console.log(`找到 ${users.length} 个用户:`);
        users.forEach(user => {
            console.log(`- ${user.name} (${user.email}, 角色: ${user.role})`);
        });
    } catch (error) {
        console.error(`✗ 获取用户列表失败: ${error}`);
    }
    
    // 更新用户信息
    console.log("\n3. 更新用户信息");
    if (createdUsers.length > 0) {
        const firstUser = createdUsers[0];
        try {
            const updatedUser = await userService.updateUser(firstUser.id, {
                name: `${firstUser.name} (已更新)`
            });
            console.log(`✓ 用户更新成功: ${updatedUser.name}`);
        } catch (error) {
            console.error(`✗ 用户更新失败: ${error}`);
        }
    }
    
    // 使用类型守卫
    console.log("\n4. 使用类型守卫");
    const unknownData = { 
        id: 'test-id', 
        name: '测试用户', 
        email: 'test@example.com', 
        role: 'member', 
        createdAt: new Date(), 
        updatedAt: new Date() 
    };
    
    if (isUser(unknownData)) {
        console.log(`✓ 未知数据是有效的用户对象: ${unknownData.name}`);
    } else {
        console.log(`✗ 未知数据不是有效的用户对象`);
    }
    
    // 删除用户
    console.log("\n5. 删除用户");
    if (createdUsers.length > 1) {
        const userToDelete = createdUsers[1];
        try {
            await userService.deleteUser(userToDelete.id);
            console.log(`✓ 用户删除成功: ${userToDelete.name}`);
        } catch (error) {
            console.error(`✗ 用户删除失败: ${error}`);
        }
    }
    
    // 获取更新后的用户列表
    console.log("\n6. 获取更新后的用户列表");
    try {
        const remainingUsers = await userService.getUsers();
        console.log(`剩余 ${remainingUsers.length} 个用户:`);
        remainingUsers.forEach(user => {
            console.log(`- ${user.name} (${user.email}, 角色: ${user.role})`);
        });
    } catch (error) {
        console.error(`✗ 获取用户列表失败: ${error}`);
    }
    
    console.log("\n=== 示例完成 ===");
}

// 运行应用程序
initializeApp().catch(console.error);

// 导出容器供其他模块使用
export { createContainer };