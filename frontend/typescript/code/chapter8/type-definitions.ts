// 类型定义示例

// 基础类型定义
export interface BaseUser {
    id: string;
    name: string;
    email: string;
    avatar?: string;
    createdAt: Date;
    updatedAt: Date;
}

// 泛型接口定义
export interface Repository<T, ID = string> {
    findById(id: ID): Promise<T | null>;
    findMany(options?: { limit?: number; offset?: number }): Promise<T[]>;
    create(data: Omit<T, 'id'>): Promise<T>;
    update(id: ID, data: Partial<T>): Promise<T>;
    delete(id: ID): Promise<boolean>;
}

// 条件类型定义
export type ApiResponse<T> = T extends string 
    ? { status: 'success', data: string }
    : T extends number
        ? { status: 'success', data: number }
        : { status: 'success', data: T };

// 映射类型定义
export type Optional<T> = {
    [K in keyof T]?: T[K];
};

export type Required<T> = {
    [K in keyof T]-?: T[K];
};

// 高级映射类型
export type DeepPartial<T> = {
    [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Nullable<T> = {
    [P in keyof T]: T[P] | null;
};

// 联合类型定义
export type Status = 'active' | 'inactive' | 'pending' | 'archived';

export type UserRole = 'admin' | 'editor' | 'viewer';

// 复杂接口定义
export interface User extends BaseUser {
    role: UserRole;
    status: Status;
    profile: {
        bio?: string;
        website?: string;
        location?: string;
    };
    preferences: {
        theme: 'light' | 'dark' | 'auto';
        language: string;
        notifications: boolean;
    };
    lastLoginAt?: Date;
}

// 函数类型定义
export type EventHandler<T = any> = (data: T) => void;
export type AsyncEventHandler<T = any> = (data: T) => Promise<void>;
export type ErrorHandler = (error: Error) => void;

// 事件系统类型定义
export interface TypedEventEmitter<TEvents extends Record<string, any[]>> {
    on<TEventName extends keyof TEvents>(
        event: TEventName,
        listener: (...args: TEvents[TEventName]) => void
    ): this;
    
    off<TEventName extends keyof TEvents>(
        event: TEventName,
        listener: (...args: TEvents[TEventName]) => void
    ): this;
    
    once<TEventName extends keyof TEvents>(
        event: TEventName,
        listener: (...args: TEvents[TEventName]) => void
    ): this;
    
    emit<TEventName extends keyof TEvents>(
        event: TEventName,
        ...args: TEvents[TEventName]
    ): boolean;
}

// 应用事件类型定义
export interface AppEvents {
    'user:login': [user: User];
    'user:logout': [];
    'user:updated': [user: User];
    'error': [error: Error];
    'notification': [message: string, type: 'info' | 'warning' | 'error' | 'success'];
}

// 类型守卫
export function isUser(obj: any): obj is User {
    return obj && 
           typeof obj.id === 'string' &&
           typeof obj.name === 'string' &&
           typeof obj.email === 'string' &&
           ['admin', 'editor', 'viewer'].includes(obj.role) &&
           ['active', 'inactive', 'pending', 'archived'].includes(obj.status);
}

// 类型工厂
export function createUser(name: string, email: string, role: UserRole): Omit<User, 'id' | 'createdAt' | 'updatedAt'> {
    const now = new Date();
    return {
        name,
        email,
        role,
        status: 'active',
        profile: {},
        preferences: {
            theme: 'auto',
            language: 'en',
            notifications: true
        },
        avatar: undefined,
        lastLoginAt: undefined
    };
}