// React + TypeScript 用户类型定义

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
 * 创建用户表单数据接口
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
 * 用户状态接口
 */
export interface UserState {
  users: User[];
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

/**
 * 用户操作接口
 */
export interface UserActions {
  fetchUsers: () => Promise<void>;
  fetchUser: (id: string) => Promise<User | null>;
  createUser: (userData: CreateUserData) => Promise<User>;
  updateUser: (id: string, updates: UpdateUserData) => Promise<User>;
  deleteUser: (id: string) => Promise<boolean>;
  setCurrentUser: (user: User | null) => void;
  clearError: () => void;
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