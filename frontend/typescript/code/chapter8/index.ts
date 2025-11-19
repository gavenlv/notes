// 第8章：TypeScript声明文件与类型定义 - 主入口文件

// 导入示例模块
import { User, UserRole, createUser } from './type-definitions';
import { UserService } from './usage-examples';

// 模拟Repository实现
class MockUserRepository {
    private users: Map<string, User> = new Map();
    
    async findById(id: string): Promise<User | null> {
        return this.users.get(id) || null;
    }
    
    async findMany(options?: { limit?: number; offset?: number }): Promise<User[]> {
        const allUsers = Array.from(this.users.values());
        if (!options) return allUsers;
        
        const { limit, offset = 0 } = options;
        return allUsers.slice(offset, offset + limit);
    }
    
    async create(userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>): Promise<User> {
        const id = Math.random().toString(36).substring(2, 9);
        const now = new Date();
        
        const user: User = {
            id,
            ...userData,
            createdAt: now,
            updatedAt: now
        };
        
        this.users.set(id, user);
        return user;
    }
    
    async update(id: string, updates: Partial<User>): Promise<User> {
        const existingUser = await this.findById(id);
        if (!existingUser) {
            throw new Error(`User with id ${id} not found`);
        }
        
        const updatedUser: User = {
            ...existingUser,
            ...updates,
            updatedAt: new Date()
        };
        
        this.users.set(id, updatedUser);
        return updatedUser;
    }
    
    async delete(id: string): Promise<boolean> {
        return this.users.delete(id);
    }
}

// 使用示例
async function runExamples() {
    console.log("=== TypeScript声明文件与类型定义示例 ===");
    
    // 创建用户服务
    const userRepository = new MockUserRepository();
    const userService = new UserService(userRepository);
    
    // 创建用户
    console.log("\n1. 创建用户");
    const adminUserData = createUser('Admin User', 'admin@example.com', 'admin');
    const adminUser = await userService.createUser(adminUserData);
    console.log(`Created admin user: ${adminUser.name} (${adminUser.id})`);
    
    // 查找用户
    console.log("\n2. 查找用户");
    const foundUser = await userService.getUserById(adminUser.id);
    if (foundUser) {
        console.log(`Found user: ${foundUser.name} with role ${foundUser.role}`);
    }
    
    // 更新用户
    console.log("\n3. 更新用户");
    const updatedUser = await userService.updateUser(adminUser.id, {
        status: 'active',
        lastLoginAt: new Date()
    });
    console.log(`Updated user status to ${updatedUser.status}`);
    
    // 列出用户
    console.log("\n4. 列出用户");
    const users = await userService.findUsers();
    console.log(`Found ${users.length} users`);
    
    // 使用类型守卫
    console.log("\n5. 使用类型守卫");
    const unknownData = { id: 'test', name: 'Test User', role: 'admin', status: 'active', email: 'test@example.com' };
    
    if (isUser(unknownData)) {
        console.log("Data is valid User:", unknownData.name);
    } else {
        console.log("Data is not a valid User");
    }
    
    // 使用类型别名和条件类型
    console.log("\n6. 使用类型别名和条件类型");
    type UserResponse = ApiResponse<User>;
    
    const successResponse: UserResponse = {
        status: 'success',
        data: adminUser
    };
    
    console.log("Response status:", successResponse.status);
    console.log("Response user:", successResponse.data.name);
}

// 导入类型守卫
function isUser(obj: any): obj is User {
    return obj && 
           typeof obj.id === 'string' &&
           typeof obj.name === 'string' &&
           typeof obj.email === 'string' &&
           ['admin', 'editor', 'viewer'].includes(obj.role) &&
           ['active', 'inactive', 'pending', 'archived'].includes(obj.status);
}

// 定义 ApiResponse 类型
type ApiResponse<T> = {
    status: 'success';
    data: T;
};

// 运行示例
runExamples().catch(console.error);