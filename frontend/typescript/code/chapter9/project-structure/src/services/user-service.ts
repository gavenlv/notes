// 用户服务示例 - 依赖注入与抽象

import { User, UserRole, CreateUserData } from '../types/user.types';
import { Logger } from '../interfaces/logger.interface';
import { Database } from '../interfaces/database.interface';

/**
 * 用户服务类
 * 负责处理用户相关的业务逻辑
 */
export class UserService {
    constructor(
        private db: Database,
        private logger: Logger
    ) {}

    /**
     * 创建新用户
     * @param userData 用户数据
     * @returns 创建的用户
     */
    async createUser(userData: CreateUserData): Promise<User> {
        this.logger.log(`Creating new user: ${userData.email}`);
        
        // 检查邮箱是否已存在
        const existingUser = await this.db.findOne<User>('users', { email: userData.email });
        if (existingUser) {
            throw new Error(`User with email ${userData.email} already exists`);
        }
        
        // 创建新用户
        const now = new Date();
        const newUser: User = {
            id: this.generateId(),
            ...userData,
            createdAt: now,
            updatedAt: now
        };
        
        const result = await this.db.insert('users', newUser);
        this.logger.log(`User created with ID: ${result.id}`);
        
        return newUser;
    }

    /**
     * 根据ID获取用户
     * @param id 用户ID
     * @returns 用户信息或null
     */
    async getUserById(id: string): Promise<User | null> {
        this.logger.log(`Fetching user with ID: ${id}`);
        
        return this.db.findOne<User>('users', { id });
    }

    /**
     * 更新用户信息
     * @param id 用户ID
     * @param updates 更新数据
     * @returns 更新后的用户信息
     */
    async updateUser(id: string, updates: Partial<CreateUserData>): Promise<User> {
        this.logger.log(`Updating user with ID: ${id}`);
        
        const user = await this.getUserById(id);
        if (!user) {
            throw new Error(`User with ID ${id} not found`);
        }
        
        const updatedUser: User = {
            ...user,
            ...updates,
            updatedAt: new Date()
        };
        
        await this.db.update('users', { id }, updatedUser);
        this.logger.log(`User ${id} updated successfully`);
        
        return updatedUser;
    }

    /**
     * 删除用户
     * @param id 用户ID
     * @returns 是否成功删除
     */
    async deleteUser(id: string): Promise<boolean> {
        this.logger.log(`Deleting user with ID: ${id}`);
        
        const user = await this.getUserById(id);
        if (!user) {
            throw new Error(`User with ID ${id} not found`);
        }
        
        const result = await this.db.delete('users', { id });
        this.logger.log(`User ${id} deleted: ${result}`);
        
        return result;
    }

    /**
     * 获取用户列表
     * @param options 查询选项
     * @returns 用户列表
     */
    async getUsers(options?: {
        limit?: number;
        offset?: number;
        role?: UserRole;
    }): Promise<User[]> {
        this.logger.log('Fetching users list');
        
        const query: any = {};
        if (options?.role) {
            query.role = options.role;
        }
        
        return this.db.findMany<User>('users', query, options);
    }

    /**
     * 生成唯一ID
     * @returns 随机生成的ID
     */
    private generateId(): string {
        return Math.random().toString(36).substring(2, 9);
    }
}