// Pinia 用户状态管理

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// 用户接口
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

// 用户统计
export interface UserStats {
  total: number;
  admin: number;
  user: number;
  guest: number;
}

// 分页参数
export interface PaginationParams {
  page: number;
  limit: number;
}

// 分页结果
export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// 过滤参数
export interface UserFilters {
  role?: string;
  search?: string;
}

// 创建用户数据
export interface CreateUserRequest {
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  password: string;
}

// 定义用户store
export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref<User[]>([]);
  const currentUser = ref<User | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref<PaginationParams>({
    page: 1,
    limit: 10
  });
  const totalUsers = ref(0);
  const totalPages = ref(0);
  const filters = ref<UserFilters>({});

  // 计算属性
  const isAuthenticated = computed(() => !!currentUser.value);
  const isAdmin = computed(() => currentUser.value?.role === 'admin');
  
  const userStats = computed<UserStats>(() => ({
    total: users.value.length,
    admin: users.value.filter(user => user.role === 'admin').length,
    user: users.value.filter(user => user.role === 'user').length,
    guest: users.value.filter(user => user.role === 'guest').length
  }));

  const filteredUsers = computed(() => {
    let result = users.value;
    
    if (filters.value.role) {
      result = result.filter(user => user.role === filters.value.role);
    }
    
    if (filters.value.search) {
      const searchTerm = filters.value.search.toLowerCase();
      result = result.filter(user =>
        user.name.toLowerCase().includes(searchTerm) ||
        user.email.toLowerCase().includes(searchTerm)
      );
    }
    
    return result;
  });

  // 获取用户列表
  const fetchUsers = async (params?: Partial<PaginationParams & UserFilters>): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const queryParams = new URLSearchParams();
      
      // 添加分页参数
      const page = params?.page ?? pagination.value.page;
      const limit = params?.limit ?? pagination.value.limit;
      
      queryParams.append('page', page.toString());
      queryParams.append('limit', limit.toString());
      
      // 添加过滤参数
      if (params?.role || filters.value.role) {
        queryParams.append('role', params?.role || filters.value.role);
      }
      
      if (params?.search || filters.value.search) {
        queryParams.append('search', params?.search || filters.value.search);
      }
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // 模拟API响应
      const mockUsers: User[] = Array.from({ length: limit }, (_, i) => ({
        id: `user-${page}-${i}`,
        name: `用户 ${page}-${i + 1}`,
        email: `user${page}${i + 1}@example.com`,
        role: ['admin', 'user', 'guest'][Math.floor(Math.random() * 3)] as User['role'],
        avatar: `https://picsum.photos/seed/user-${page}-${i}/100/100.jpg`,
        createdAt: new Date(Date.now() - Math.floor(Math.random() * 10000000000)).toISOString(),
        updatedAt: new Date(Date.now() - Math.floor(Math.random() * 100000000)).toISOString()
      }));
      
      // 更新状态
      users.value = mockUsers;
      totalUsers.value = 50; // 模拟总数
      totalPages.value = Math.ceil(totalUsers.value / limit);
      pagination.value = { page, limit };
      
      // 更新过滤条件
      if (params?.role) filters.value.role = params.role;
      if (params?.search) filters.value.search = params.search;
      
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch users';
    } finally {
      isLoading.value = false;
    }
  };

  // 获取单个用户
  const fetchUser = async (id: string): Promise<User | null> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 模拟从现有用户中查找
      const user = users.value.find(u => u.id === id);
      
      if (user) {
        currentUser.value = user;
        return user;
      }
      
      // 如果找不到，模拟API返回
      const mockUser: User = {
        id,
        name: `用户 ${id}`,
        email: `${id}@example.com`,
        role: 'user',
        avatar: `https://picsum.photos/seed/${id}/100/100.jpg`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      currentUser.value = mockUser;
      return mockUser;
      
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch user';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // 创建用户
  const createUser = async (userData: CreateUserRequest): Promise<User> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const newUser: User = {
        id: `user-${Date.now()}`,
        name: userData.name,
        email: userData.email,
        role: userData.role,
        avatar: `https://picsum.photos/seed/user-${Date.now()}/100/100.jpg`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      // 添加到用户列表
      users.value.unshift(newUser);
      totalUsers.value += 1;
      
      return newUser;
      
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create user';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 更新用户
  const updateUser = async (id: string, updates: Partial<User>): Promise<User> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const userIndex = users.value.findIndex(u => u.id === id);
      
      if (userIndex === -1) {
        throw new Error('User not found');
      }
      
      // 更新用户
      const updatedUser: User = {
        ...users.value[userIndex],
        ...updates,
        updatedAt: new Date().toISOString()
      };
      
      users.value[userIndex] = updatedUser;
      
      // 更新当前用户
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser;
      }
      
      return updatedUser;
      
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update user';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 删除用户
  const deleteUser = async (id: string): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const userIndex = users.value.findIndex(u => u.id === id);
      
      if (userIndex === -1) {
        throw new Error('User not found');
      }
      
      // 删除用户
      users.value.splice(userIndex, 1);
      totalUsers.value -= 1;
      
      // 清除当前用户
      if (currentUser.value?.id === id) {
        currentUser.value = null;
      }
      
      return true;
      
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete user';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 设置过滤条件
  const setFilters = (newFilters: Partial<UserFilters>): void => {
    filters.value = { ...filters.value, ...newFilters };
  };

  // 清除过滤条件
  const clearFilters = (): void => {
    filters.value = {};
  };

  // 设置当前用户
  const setCurrentUser = (user: User | null): void => {
    currentUser.value = user;
  };

  // 清除当前用户
  const clearCurrentUser = (): void => {
    currentUser.value = null;
  };

  // 清除错误
  const clearError = (): void => {
    error.value = null;
  };

  // 重置状态
  const resetState = (): void => {
    users.value = [];
    currentUser.value = null;
    isLoading.value = false;
    error.value = null;
    pagination.value = { page: 1, limit: 10 };
    totalUsers.value = 0;
    totalPages.value = 0;
    filters.value = {};
  };

  return {
    // 状态
    users,
    currentUser,
    isLoading,
    error,
    pagination,
    totalUsers,
    totalPages,
    filters,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    userStats,
    filteredUsers,
    
    // 方法
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    setFilters,
    clearFilters,
    setCurrentUser,
    clearCurrentUser,
    clearError,
    resetState
  };
});