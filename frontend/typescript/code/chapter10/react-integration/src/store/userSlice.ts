// Redux Toolkit 用户状态管理

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

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

// 用户状态接口
export interface UserState {
  users: User[];
  currentUser: User | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  filters: {
    role?: string;
    search?: string;
  };
}

// 初始状态
const initialState: UserState = {
  users: [],
  currentUser: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  },
  filters: {}
};

// 异步操作：获取用户列表
export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (params: { page?: number; limit?: number; role?: string; search?: string }) => {
    const { page = 1, limit = 10, role, search } = params;
    
    // 构建查询参数
    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    });
    
    if (role) {
      queryParams.append('role', role);
    }
    
    if (search) {
      queryParams.append('search', search);
    }
    
    const response = await fetch(`/api/users?${queryParams.toString()}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    
    const data = await response.json();
    return data as {
      users: User[];
      total: number;
      page: number;
      totalPages: number;
    };
  }
);

// 异步操作：获取单个用户
export const fetchUserById = createAsyncThunk(
  'users/fetchUserById',
  async (id: string) => {
    const response = await fetch(`/api/users/${id}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    
    const user = await response.json() as User;
    return user;
  }
);

// 异步操作：创建用户
export const createUser = createAsyncThunk(
  'users/createUser',
  async (userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>) => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
      throw new Error('Failed to create user');
    }
    
    const user = await response.json() as User;
    return user;
  }
);

// 异步操作：更新用户
export const updateUser = createAsyncThunk(
  'users/updateUser',
  async ({ id, updates }: { id: string; updates: Partial<User> }) => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updates)
    });
    
    if (!response.ok) {
      throw new Error('Failed to update user');
    }
    
    const user = await response.json() as User;
    return user;
  }
);

// 异步操作：删除用户
export const deleteUser = createAsyncThunk(
  'users/deleteUser',
  async (id: string) => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete user');
    }
    
    return id;
  }
);

// 创建用户slice
const userSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    // 同步操作：设置当前用户
    setCurrentUser: (state, action: PayloadAction<User | null>) => {
      state.currentUser = action.payload;
    },
    
    // 同步操作：清除错误
    clearError: (state) => {
      state.error = null;
    },
    
    // 同步操作：设置过滤条件
    setFilters: (state, action: PayloadAction<Partial<UserState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    
    // 同步操作：清除过滤条件
    clearFilters: (state) => {
      state.filters = {};
    },
    
    // 同步操作：设置分页
    setPagination: (state, action: PayloadAction<Partial<UserState['pagination']>>) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    
    // 同步操作：重置状态
    resetUserState: (state) => {
      state = { ...initialState };
      return state;
    }
  },
  extraReducers: (builder) => {
    // fetchUsers
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload.users;
        state.pagination = {
          page: action.payload.page,
          limit: action.payload.users.length,
          total: action.payload.total,
          totalPages: action.payload.totalPages
        };
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch users';
      });
    
    // fetchUserById
    builder
      .addCase(fetchUserById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentUser = action.payload;
      })
      .addCase(fetchUserById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch user';
      });
    
    // createUser
    builder
      .addCase(createUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createUser.fulfilled, (state, action) => {
        state.loading = false;
        state.users.push(action.payload);
        // 如果是第一页，增加总数
        if (state.pagination.page === 1) {
          state.pagination.total += 1;
        }
      })
      .addCase(createUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create user';
      });
    
    // updateUser
    builder
      .addCase(updateUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUser.fulfilled, (state, action) => {
        state.loading = false;
        // 更新用户列表中的用户
        const index = state.users.findIndex(user => user.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
        // 更新当前用户（如果是同一个用户）
        if (state.currentUser && state.currentUser.id === action.payload.id) {
          state.currentUser = action.payload;
        }
      })
      .addCase(updateUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update user';
      });
    
    // deleteUser
    builder
      .addCase(deleteUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteUser.fulfilled, (state, action) => {
        state.loading = false;
        // 从用户列表中删除用户
        state.users = state.users.filter(user => user.id !== action.payload);
        // 减少总数
        state.pagination.total = Math.max(0, state.pagination.total - 1);
        // 如果删除的是当前用户，清除当前用户
        if (state.currentUser && state.currentUser.id === action.payload) {
          state.currentUser = null;
        }
      })
      .addCase(deleteUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete user';
      });
  }
});

// 导出actions
export const {
  setCurrentUser,
  clearError,
  setFilters,
  clearFilters,
  setPagination,
  resetUserState
} = userSlice.actions;

// 导出reducer
export default userSlice.reducer;

// 选择器
export const selectUsers = (state: { users: UserState }) => state.users.users;
export const selectCurrentUser = (state: { users: UserState }) => state.users.currentUser;
export const selectUsersLoading = (state: { users: UserState }) => state.users.loading;
export const selectUsersError = (state: { users: UserState }) => state.users.error;
export const selectUsersPagination = (state: { users: UserState }) => state.users.pagination;
export const selectUsersFilters = (state: { users: UserState }) => state.users.filters;

// 派生选择器
export const selectUserById = (userId: string) => (state: { users: UserState }) =>
  state.users.users.find(user => user.id === userId);

export const selectUsersByRole = (role: string) => (state: { users: UserState }) =>
  state.users.users.filter(user => user.role === role);

export const selectFilteredUsers = (state: { users: UserState }) => {
  const { users, filters } = state.users;
  let filteredUsers = users;
  
  if (filters.role) {
    filteredUsers = filteredUsers.filter(user => user.role === filters.role);
  }
  
  if (filters.search) {
    const searchTerm = filters.search.toLowerCase();
    filteredUsers = filteredUsers.filter(user =>
      user.name.toLowerCase().includes(searchTerm) ||
      user.email.toLowerCase().includes(searchTerm)
    );
  }
  
  return filteredUsers;
};