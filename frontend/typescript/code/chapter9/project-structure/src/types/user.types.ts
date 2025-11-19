// 用户相关类型定义

/**
 * 用户角色枚举
 */
export type UserRole = 'admin' | 'manager' | 'member';

/**
 * 用户接口
 */
export interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
    role: UserRole;
    createdAt: Date;
    updatedAt: Date;
}

/**
 * 创建用户数据
 */
export interface CreateUserData {
    name: string;
    email: string;
    role: UserRole;
    avatar?: string;
}

/**
 * 更新用户数据
 */
export interface UpdateUserData extends Partial<CreateUserData> {}

/**
 * 用户状态
 */
export type UserStatus = 'active' | 'inactive' | 'suspended';

/**
 * 用户详情
 */
export interface UserDetails extends User {
    status: UserStatus;
    lastLoginAt?: Date;
    department?: string;
    title?: string;
}

/**
 * 用户查询选项
 */
export interface UserQueryOptions {
    limit?: number;
    offset?: number;
    role?: UserRole;
    status?: UserStatus;
    department?: string;
}

/**
 * 用户分页结果
 */
export interface UserPaginatedResult {
    users: User[];
    total: number;
    limit: number;
    offset: number;
    hasMore: boolean;
}

/**
 * 类型守卫：检查是否为User对象
 * @param obj 要检查的对象
 * @returns 是否为User对象
 */
export function isUser(obj: any): obj is User {
    return (
        obj !== null &&
        typeof obj === 'object' &&
        'id' in obj &&
        'name' in obj &&
        'email' in obj &&
        'role' in obj &&
        'createdAt' in obj &&
        'updatedAt' in obj &&
        typeof obj.id === 'string' &&
        typeof obj.name === 'string' &&
        typeof obj.email === 'string' &&
        ['admin', 'manager', 'member'].includes(obj.role) &&
        obj.createdAt instanceof Date &&
        obj.updatedAt instanceof Date
    );
}

/**
 * 类型守卫：检查是否为CreateUserData对象
 * @param obj 要检查的对象
 * @returns 是否为CreateUserData对象
 */
export function isCreateUserData(obj: any): obj is CreateUserData {
    return (
        obj !== null &&
        typeof obj === 'object' &&
        'name' in obj &&
        'email' in obj &&
        'role' in obj &&
        typeof obj.name === 'string' &&
        typeof obj.email === 'string' &&
        ['admin', 'manager', 'member'].includes(obj.role)
    );
}