// Vue + TypeScript 用户类型定义

/**
 * 用户接口
 */
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * 创建用户数据接口
 */
export interface CreateUserData {
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  password: string;
}

/**
 * 更新用户数据接口
 */
export interface UpdateUserData {
  name?: string;
  email?: string;
  role?: 'admin' | 'user' | 'guest';
  avatar?: string;
}

/**
 * 用户统计接口
 */
export interface UserStats {
  total: number;
  admin: number;
  user: number;
  guest: number;
}

/**
 * 分页参数接口
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

/**
 * 分页结果接口
 */
export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

/**
 * 过滤参数接口
 */
export interface UserFilters {
  role?: string;
  search?: string;
}

/**
 * 类型守卫：检查是否为User对象
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
    ['admin', 'user', 'guest'].includes(obj.role) &&
    typeof obj.createdAt === 'string' &&
    typeof obj.updatedAt === 'string'
  );
}

/**
 * 类型守卫：检查是否为CreateUserData对象
 */
export function isCreateUserData(obj: any): obj is CreateUserData {
  return (
    obj !== null &&
    typeof obj === 'object' &&
    'name' in obj &&
    'email' in obj &&
    'role' in obj &&
    'password' in obj &&
    typeof obj.name === 'string' &&
    typeof obj.email === 'string' &&
    ['admin', 'user', 'guest'].includes(obj.role) &&
    typeof obj.password === 'string'
  );
}