# 第10章：TypeScript与前端框架集成

## 章节概述

在前面的章节中，我们全面学习了TypeScript的核心概念和实践技巧。在这一章中，我们将探讨如何将TypeScript与流行的前端框架集成，包括React、Vue和Angular。我们将学习如何在这些框架中有效利用TypeScript的类型系统，提升开发体验和代码质量。

## 学习目标

- 掌握在React项目中使用TypeScript的方法和技巧
- 了解Vue 3与TypeScript的集成方式
- 探索Angular框架中的TypeScript应用
- 学习使用TypeScript开发前端组件和状态管理
- 掌握在前端项目中进行类型驱动开发的实践

---

## 10.1 React与TypeScript集成

### 10.1.1 React项目基础配置

创建React + TypeScript项目有多种方式：

1. **使用Create React App**：
   ```bash
   npx create-react-app my-app --template typescript
   ```

2. **使用Vite**（推荐）：
   ```bash
   npm create vite@latest my-react-app -- --template react-ts
   ```

3. **手动配置**：
   ```bash
   # 创建项目目录
   mkdir my-react-app
   cd my-react-app
   
   # 初始化npm项目
   npm init -y
   
   # 安装依赖
   npm install react react-dom
   npm install -D typescript @types/react @types/react-dom @types/node
   ```

### 10.1.2 React组件类型定义

#### 函数组件

```typescript
// 基本函数组件
interface GreetingProps {
    name: string;
    age?: number; // 可选属性
}

function Greeting({ name, age }: GreetingProps) {
    return (
        <div>
            <h1>Hello, {name}!</h1>
            {age && <p>You are {age} years old.</p>}
        </div>
    );
}

// 使用React.FC类型
const GreetingFC: React.FC<GreetingProps> = ({ name, age }) => {
    return (
        <div>
            <h1>Hello, {name}!</h1>
            {age && <p>You are {age} years old.</p>}
        </div>
    );
};

// 使用泛型的函数组件
interface ListProps<T> {
    items: T[];
    renderItem: (item: T) => React.ReactNode;
    keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
    return (
        <ul>
            {items.map(item => (
                <li key={keyExtractor(item)}>
                    {renderItem(item)}
                </li>
            ))}
        </ul>
    );
}
```

#### 类组件

```typescript
// 基本类组件
interface CounterState {
    count: number;
}

interface CounterProps {
    initialCount?: number;
    step?: number;
}

class Counter extends React.Component<CounterProps, CounterState> {
    constructor(props: CounterProps) {
        super(props);
        
        this.state = {
            count: props.initialCount || 0
        };
    }
    
    increment = () => {
        this.setState(prevState => ({
            count: prevState.count + (this.props.step || 1)
        }));
    }
    
    decrement = () => {
        this.setState(prevState => ({
            count: prevState.count - (this.props.step || 1)
        }));
    }
    
    render() {
        const { count } = this.state;
        
        return (
            <div>
                <p>Count: {count}</p>
                <button onClick={this.increment}>+</button>
                <button onClick={this.decrement}>-</button>
            </div>
        );
    }
}
```

### 10.1.3 Hooks与TypeScript

#### 自定义Hooks

```typescript
// 基本自定义Hook
function useCounter(initialValue = 0, step = 1) {
    const [count, setCount] = useState(initialValue);
    
    const increment = useCallback(() => {
        setCount(prevCount => prevCount + step);
    }, [step]);
    
    const decrement = useCallback(() => {
        setCount(prevCount => prevCount - step);
    }, [step]);
    
    const reset = useCallback(() => {
        setCount(initialValue);
    }, [initialValue]);
    
    return { count, increment, decrement, reset };
}

// 使用泛型的自定义Hook
function useApi<T>(url: string) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                const result = await response.json() as T;
                setData(result);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, [url]);
    
    return { data, loading, error };
}

// 使用自定义Hook
interface User {
    id: string;
    name: string;
    email: string;
}

function UserProfile({ userId }: { userId: string }) {
    const { data: user, loading, error } = useApi<User>(`/api/users/${userId}`);
    
    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;
    if (!user) return <p>No user found.</p>;
    
    return (
        <div>
            <h2>{user.name}</h2>
            <p>Email: {user.email}</p>
        </div>
    );
}
```

#### useState与TypeScript

```typescript
// 基本用法
const [count, setCount] = useState<number>(0);
const [name, setName] = useState<string>('');

// 使用接口
interface FormData {
    email: string;
    password: string;
    rememberMe: boolean;
}

const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    rememberMe: false
});

// 更新表单数据
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked, type } = e.target;
    
    setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
    }));
};
```

#### useReducer与TypeScript

```typescript
// 定义状态和动作类型
interface Todo {
    id: string;
    text: string;
    completed: boolean;
}

type TodoAction =
    | { type: 'ADD_TODO'; text: string }
    | { type: 'TOGGLE_TODO'; id: string }
    | { type: 'DELETE_TODO'; id: string }
    | { type: 'SET_FILTER'; filter: 'all' | 'active' | 'completed' };

interface TodoState {
    todos: Todo[];
    filter: 'all' | 'active' | 'completed';
}

// 定义reducer
const todoReducer = (
    state: TodoState,
    action: TodoAction
): TodoState => {
    switch (action.type) {
        case 'ADD_TODO':
            return {
                ...state,
                todos: [
                    ...state.todos,
                    {
                        id: Date.now().toString(),
                        text: action.text,
                        completed: false
                    }
                ]
            };
            
        case 'TOGGLE_TODO':
            return {
                ...state,
                todos: state.todos.map(todo =>
                    todo.id === action.id
                        ? { ...todo, completed: !todo.completed }
                        : todo
                )
            };
            
        case 'DELETE_TODO':
            return {
                ...state,
                todos: state.todos.filter(todo => todo.id !== action.id)
            };
            
        case 'SET_FILTER':
            return {
                ...state,
                filter: action.filter
            };
            
        default:
            return state;
    }
};

// 在组件中使用
function TodoApp() {
    const [state, dispatch] = useReducer(todoReducer, {
        todos: [],
        filter: 'all'
    });
    
    const [inputValue, setInputValue] = useState('');
    
    const handleAddTodo = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputValue.trim()) {
            dispatch({ type: 'ADD_TODO', text: inputValue });
            setInputValue('');
        }
    };
    
    const visibleTodos = state.todos.filter(todo => {
        switch (state.filter) {
            case 'active':
                return !todo.completed;
            case 'completed':
                return todo.completed;
            default:
                return true;
        }
    });
    
    return (
        <div>
            <form onSubmit={handleAddTodo}>
                <input
                    type="text"
                    value={inputValue}
                    onChange={e => setInputValue(e.target.value)}
                    placeholder="Add a new todo"
                />
                <button type="submit">Add</button>
            </form>
            
            <div>
                <button onClick={() => dispatch({ type: 'SET_FILTER', filter: 'all' })}>
                    All
                </button>
                <button onClick={() => dispatch({ type: 'SET_FILTER', filter: 'active' })}>
                    Active
                </button>
                <button onClick={() => dispatch({ type: 'SET_FILTER', filter: 'completed' })}>
                    Completed
                </button>
            </div>
            
            <ul>
                {visibleTodos.map(todo => (
                    <li key={todo.id}>
                        <span
                            style={{
                                textDecoration: todo.completed ? 'line-through' : 'none'
                            }}
                            onClick={() => dispatch({ type: 'TOGGLE_TODO', id: todo.id })}
                        >
                            {todo.text}
                        </span>
                        <button onClick={() => dispatch({ type: 'DELETE_TODO', id: todo.id })}>
                            Delete
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

### 10.1.4 React Context与TypeScript

```typescript
// 定义Context类型
interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
    isLoading: boolean;
}

// 创建Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Context Provider组件
interface AuthProviderProps {
    children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    
    useEffect(() => {
        // 检查用户是否已登录
        const checkAuthStatus = async () => {
            try {
                const token = localStorage.getItem('authToken');
                
                if (token) {
                    // 验证token并获取用户信息
                    const userData = await fetchUserData(token);
                    setUser(userData);
                }
            } catch (error) {
                console.error('Authentication error:', error);
                localStorage.removeItem('authToken');
            } finally {
                setIsLoading(false);
            }
        };
        
        checkAuthStatus();
    }, []);
    
    const login = async (email: string, password: string): Promise<boolean> => {
        setIsLoading(true);
        
        try {
            const response = await authenticateUser(email, password);
            
            if (response.success) {
                localStorage.setItem('authToken', response.token);
                setUser(response.user);
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        } finally {
            setIsLoading(false);
        }
    };
    
    const logout = () => {
        localStorage.removeItem('authToken');
        setUser(null);
    };
    
    const value: AuthContextType = {
        user,
        login,
        logout,
        isLoading
    };
    
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

// 自定义Hook使用Context
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    
    return context;
};

// 使用示例
function LoginForm() {
    const { login, isLoading } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        
        const success = await login(email, password);
        
        if (!success) {
            setError('Invalid email or password');
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Email:</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
            </div>
            <div>
                <label>Password:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
            </div>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <button type="submit" disabled={isLoading}>
                {isLoading ? 'Logging in...' : 'Log in'}
            </button>
        </form>
    );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { user, isLoading } = useAuth();
    
    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (!user) {
        return <LoginForm />;
    }
    
    return <>{children}</>;
}
```

---

## 10.2 Vue与TypeScript集成

### 10.2.1 Vue项目基础配置

创建Vue + TypeScript项目：

1. **使用Vue CLI**：
   ```bash
   vue create my-vue-app
   # 选择 "Manually select features" 然后选择TypeScript
   ```

2. **使用Vite**（推荐）：
   ```bash
   npm create vite@latest my-vue-app -- --template vue-ts
   ```

### 10.2.2 Vue组件与TypeScript

#### 选项式API

```vue
<!-- UserCard.vue -->
<template>
  <div class="user-card">
    <img :src="user.avatar" :alt="user.name" class="avatar" />
    <div class="user-info">
      <h3>{{ user.name }}</h3>
      <p>{{ user.email }}</p>
      <span class="role">{{ user.role }}</span>
    </div>
    <button @click="editUser">Edit</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar: string;
}

export default defineComponent({
  name: 'UserCard',
  props: {
    user: {
      type: Object as PropType<User>,
      required: true
    }
  },
  emits: ['edit'],
  methods: {
    editUser() {
      this.$emit('edit', this.user.id);
    }
  }
});
</script>

<style scoped>
.user-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-right: 16px;
}

.user-info {
  flex: 1;
}

.role {
  display: inline-block;
  padding: 4px 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
}
</style>
```

#### 组合式API

```vue
<!-- TodoList.vue -->
<template>
  <div class="todo-list">
    <h2>Todo List</h2>
    
    <form @submit.prevent="addTodo">
      <input v-model="newTodoText" placeholder="Add a new todo" />
      <button type="submit">Add</button>
    </form>
    
    <div class="filter-buttons">
      <button
        v-for="filter in filters"
        :key="filter.value"
        @click="activeFilter = filter.value"
        :class="{ active: activeFilter === filter.value }"
      >
        {{ filter.label }}
      </button>
    </div>
    
    <ul>
      <li
        v-for="todo in filteredTodos"
        :key="todo.id"
        :class="{ completed: todo.completed }"
      >
        <input
          type="checkbox"
          v-model="todo.completed"
        />
        <span>{{ todo.text }}</span>
        <button @click="deleteTodo(todo.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, reactive } from 'vue';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface Filter {
  value: 'all' | 'active' | 'completed';
  label: string;
}

export default defineComponent({
  name: 'TodoList',
  setup() {
    // 状态
    const todos = ref<Todo[]>([
      { id: '1', text: 'Learn Vue with TypeScript', completed: false },
      { id: '2', text: 'Build a project', completed: false }
    ]);
    
    const newTodoText = ref('');
    const activeFilter = ref<'all' | 'active' | 'completed'>('all');
    
    const filters = reactive<Filter[]>([
      { value: 'all', label: 'All' },
      { value: 'active', label: 'Active' },
      { value: 'completed', label: 'Completed' }
    ]);
    
    // 计算属性
    const filteredTodos = computed(() => {
      switch (activeFilter.value) {
        case 'active':
          return todos.value.filter(todo => !todo.completed);
        case 'completed':
          return todos.value.filter(todo => todo.completed);
        default:
          return todos.value;
      }
    });
    
    // 方法
    const addTodo = () => {
      if (newTodoText.value.trim()) {
        todos.value.push({
          id: Date.now().toString(),
          text: newTodoText.value,
          completed: false
        });
        newTodoText.value = '';
      }
    };
    
    const deleteTodo = (id: string) => {
      todos.value = todos.value.filter(todo => todo.id !== id);
    };
    
    return {
      todos,
      newTodoText,
      activeFilter,
      filters,
      filteredTodos,
      addTodo,
      deleteTodo
    };
  }
});
</script>

<style scoped>
.todo-list {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

form {
  display: flex;
  margin-bottom: 20px;
}

input[type="text"] {
  flex: 1;
  padding: 8px;
  margin-right: 8px;
}

.filter-buttons {
  margin-bottom: 20px;
}

.filter-buttons button {
  margin-right: 8px;
  padding: 4px 8px;
  border: 1px solid #ddd;
  background-color: #f5f5f5;
}

.filter-buttons button.active {
  background-color: #4285f4;
  color: white;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

li.completed span {
  text-decoration: line-through;
  color: #888;
}

li button {
  margin-left: auto;
  background-color: #ff5252;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>
```

### 10.2.3 Pinia状态管理与TypeScript

```typescript
// stores/user.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'user' | 'guest';
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null);
  const isLoading = ref(false);
  
  // 计算属性
  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  
  // 方法
  const login = async (email: string, password: string) => {
    isLoading.value = true;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟用户数据
      const userData: User = {
        id: '1',
        name: 'John Doe',
        email,
        role: 'user'
      };
      
      user.value = userData;
      
      // 保存token到localStorage
      localStorage.setItem('authToken', 'mock-token');
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      isLoading.value = false;
    }
  };
  
  const logout = () => {
    user.value = null;
    localStorage.removeItem('authToken');
  };
  
  const fetchUser = async () => {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      return;
    }
    
    isLoading.value = true;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 模拟获取用户数据
      const userData: User = {
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        role: 'user'
      };
      
      user.value = userData;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      isLoading.value = false;
    }
  };
  
  const updateProfile = async (updates: Partial<User>) => {
    if (!user.value) return;
    
    isLoading.value = true;
    
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 更新用户数据
      user.value = { ...user.value, ...updates };
      
      return true;
    } catch (error) {
      console.error('Profile update failed:', error);
      return false;
    } finally {
      isLoading.value = false;
    }
  };
  
  return {
    // 状态
    user,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    
    // 方法
    login,
    logout,
    fetchUser,
    updateProfile
  };
});
```

### 10.2.4 自定义组合函数

```typescript
// composables/useApi.ts
import { ref, computed } from 'vue';

interface ApiResponse<T> {
  data: T;
  error: string | null;
  loading: boolean;
}

export function useApi<T>(url: string) {
  const data = ref<T | null>(null);
  const error = ref<string | null>(null);
  const loading = ref(false);
  
  const fetchData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json() as T;
      data.value = result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading.value = false;
    }
  };
  
  return {
    data,
    error,
    loading,
    fetchData,
    isSuccess: computed(() => !loading.value && !error.value && !!data.value),
    isError: computed(() => !loading.value && !!error.value)
  };
}

// composables/usePagination.ts
export function usePagination<T>(items: T[], itemsPerPage = 10) {
  const currentPage = ref(1);
  
  const totalPages = computed(() => Math.ceil(items.length / itemsPerPage));
  
  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return items.slice(start, end);
  });
  
  const hasNextPage = computed(() => currentPage.value < totalPages.value);
  const hasPrevPage = computed(() => currentPage.value > 1);
  
  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++;
    }
  };
  
  const prevPage = () => {
    if (hasPrevPage.value) {
      currentPage.value--;
    }
  };
  
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };
  
  const resetPagination = () => {
    currentPage.value = 1;
  };
  
  return {
    currentPage,
    totalPages,
    paginatedItems,
    hasNextPage,
    hasPrevPage,
    nextPage,
    prevPage,
    goToPage,
    resetPagination
  };
}
```

---

## 10.3 Angular与TypeScript集成

### 10.3.1 Angular项目基础配置

Angular天生使用TypeScript，创建项目：

```bash
npm install -g @angular/cli
ng new my-angular-app --defaults
cd my-angular-app
```

Angular CLI自动配置了TypeScript环境。

### 10.3.2 Angular组件与TypeScript

```typescript
// src/app/user/user.component.ts
import { Component, Input, Output, EventEmitter } from '@angular/core';

// 接口定义
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
}

export interface UserRole {
  value: 'admin' | 'user' | 'guest';
  label: string;
}

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent {
  @Input() user!: User;
  @Input() editable = false;
  @Output() edit = new EventEmitter<string>();
  @Output() delete = new EventEmitter<string>();
  
  // 角色选项
  roleOptions: UserRole[] = [
    { value: 'admin', label: 'Administrator' },
    { value: 'user', label: 'Regular User' },
    { value: 'guest', label: 'Guest' }
  ];
  
  // 编辑状态
  isEditing = false;
  editedUser: User = { ...this.user };
  
  // 属性访问器，方便模板访问
  get isAdmin(): boolean {
    return this.user.role === 'admin';
  }
  
  // 方法
  startEditing(): void {
    this.isEditing = true;
    this.editedUser = { ...this.user };
  }
  
  cancelEditing(): void {
    this.isEditing = false;
  }
  
  saveUser(): void {
    // 这里会触发一个事件让父组件处理实际保存
    this.isEditing = false;
    this.user = { ...this.editedUser };
  }
  
  onEdit(): void {
    this.edit.emit(this.user.id);
  }
  
  onDelete(): void {
    this.delete.emit(this.user.id);
  }
}
```

```html
<!-- src/app/user/user.component.html -->
<div class="user-card" [class.editing]="isEditing">
  <div class="user-avatar" *ngIf="user.avatar; else placeholderAvatar">
    <img [src]="user.avatar" [alt]="user.name" />
  </div>
  <ng-template #placeholderAvatar>
    <div class="avatar-placeholder">{{ user.name.charAt(0) }}</div>
  </ng-template>
  
  <div class="user-info" *ngIf="!isEditing; else editingForm">
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
    <span class="role" [class.admin]="isAdmin">{{ roleOptions.find(r => r.value === user.role)?.label }}</span>
  </div>
  
  <ng-template #editingForm>
    <div class="user-form">
      <div class="form-group">
        <label for="name">Name:</label>
        <input id="name" type="text" [(ngModel)]="editedUser.name" />
      </div>
      
      <div class="form-group">
        <label for="email">Email:</label>
        <input id="email" type="email" [(ngModel)]="editedUser.email" />
      </div>
      
      <div class="form-group">
        <label for="role">Role:</label>
        <select id="role" [(ngModel)]="editedUser.role">
          <option *ngFor="let option of roleOptions" [value]="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>
  </ng-template>
  
  <div class="user-actions">
    <ng-container *ngIf="!isEditing">
      <button (click)="startEditing()" [disabled]="!editable">Edit</button>
      <button (click)="onDelete()" class="danger">Delete</button>
    </ng-container>
    
    <ng-container *ngIf="isEditing">
      <button (click)="saveUser()">Save</button>
      <button (click)="cancelEditing()">Cancel</button>
    </ng-container>
  </div>
</div>
```

### 10.3.3 Angular服务与依赖注入

```typescript
// src/app/services/user.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { User, UserRole } from '../user/user.component';

// API响应接口
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface UserListResponse extends ApiResponse<User[]> {
  total: number;
  page: number;
  limit: number;
}

export interface CreateUserRequest {
  name: string;
  email: string;
  role: UserRole['value'];
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly apiUrl = 'api/users';
  
  constructor(private http: HttpClient) {}
  
  // 获取用户列表
  getUsers(options?: {
    page?: number;
    limit?: number;
    role?: UserRole['value'];
    search?: string;
  }): Observable<UserListResponse> {
    let params = new HttpParams();
    
    if (options?.page) {
      params = params.set('page', options.page.toString());
    }
    
    if (options?.limit) {
      params = params.set('limit', options.limit.toString());
    }
    
    if (options?.role) {
      params = params.set('role', options.role);
    }
    
    if (options?.search) {
      params = params.set('search', options.search);
    }
    
    return this.http.get<UserListResponse>(this.apiUrl, { params }).pipe(
      catchError(this.handleError<UserListResponse>('getUsers'))
    );
  }
  
  // 获取单个用户
  getUser(id: string): Observable<User> {
    return this.http.get<ApiResponse<User>>(`${this.apiUrl}/${id}`).pipe(
      map(response => response.data),
      catchError(this.handleError<User>('getUser'))
    );
  }
  
  // 创建用户
  createUser(userData: CreateUserRequest): Observable<User> {
    return this.http.post<ApiResponse<User>>(this.apiUrl, userData).pipe(
      map(response => response.data),
      tap(user => console.log(`Created user: ${user.name}`)),
      catchError(this.handleError<User>('createUser'))
    );
  }
  
  // 更新用户
  updateUser(id: string, updates: Partial<User>): Observable<User> {
    return this.http.put<ApiResponse<User>>(`${this.apiUrl}/${id}`, updates).pipe(
      map(response => response.data),
      tap(user => console.log(`Updated user: ${user.name}`)),
      catchError(this.handleError<User>('updateUser'))
    );
  }
  
  // 删除用户
  deleteUser(id: string): Observable<boolean> {
    return this.http.delete<ApiResponse<null>>(`${this.apiUrl}/${id}`).pipe(
      map(response => response.success),
      tap(success => success ? console.log(`Deleted user with ID: ${id}`) : null),
      catchError(this.handleError<boolean>('deleteUser', false))
    );
  }
  
  // 错误处理
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed:`, error);
      
      // 可以在这里添加特定错误类型的处理
      if (error.status === 404) {
        return throwError('Resource not found');
      }
      
      if (error.status === 401) {
        return throwError('Unauthorized');
      }
      
      // 否则返回一个安全的默认值或抛出错误
      return of(result as T);
    };
  }
}
```

### 10.3.4 Angular路由与守卫

```typescript
// src/app/guards/auth.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}
  
  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.authService.isAuthenticated$.pipe(
      take(1),
      map(isAuthenticated => {
        if (isAuthenticated) {
          return true;
        }
        
        // 未认证，重定向到登录页
        this.router.navigate(['/login'], {
          queryParams: { returnUrl: state.url }
        });
        return false;
      })
    );
  }
}

// src/app/guards/role.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}
  
  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    const expectedRoles = next.data['roles'] as string[];
    
    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (!user) {
          this.router.navigate(['/login']);
          return false;
        }
        
        const hasRequiredRole = expectedRoles.some(role => user.roles.includes(role));
        
        if (hasRequiredRole) {
          return true;
        }
        
        // 没有必要的权限，重定向到403页面
        this.router.navigate(['/403']);
        return false;
      })
    );
  }
}
```

```typescript
// src/app/app-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { UserListComponent } from './user-list/user-list.component';
import { UserDetailComponent } from './user-detail/user-detail.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { AuthGuard } from './guards/auth.guard';
import { RoleGuard } from './guards/role.guard';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'users', 
    component: UserListComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin', 'manager'] }
  },
  { 
    path: 'users/:id', 
    component: UserDetailComponent,
    canActivate: [AuthGuard]
  },
  { path: '403', component: PageNotFoundComponent },
  { path: '**', redirectTo: '/404' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

---

## 10.4 状态管理与TypeScript

### 10.4.1 Redux/Redux Toolkit与TypeScript

```typescript
// store/slices/userSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

// 类型定义
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserState {
  users: User[];
  currentUser: User | null;
  isLoading: boolean;
  error: string | null;
}

// 初始状态
const initialState: UserState = {
  users: [],
  currentUser: null,
  isLoading: false,
  error: null
};

// 异步操作
export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (params?: { page?: number; limit?: number }) => {
    const response = await fetch(`/api/users?page=${params?.page || 1}&limit=${params?.limit || 10}`);
    const data = await response.json();
    return data.users as User[];
  }
);

export const fetchUserById = createAsyncThunk(
  'users/fetchUserById',
  async (id: string) => {
    const response = await fetch(`/api/users/${id}`);
    const data = await response.json();
    return data as User;
  }
);

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
    
    const data = await response.json();
    return data as User;
  }
);

// 创建slice
const userSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    // 同步操作
    clearError: (state) => {
      state.error = null;
    },
    setCurrentUser: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
    },
    clearCurrentUser: (state) => {
      state.currentUser = null;
    }
  },
  extraReducers: (builder) => {
    // fetchUsers
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.isLoading = false;
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch users';
      });
    
    // fetchUserById
    builder
      .addCase(fetchUserById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentUser = action.payload;
      })
      .addCase(fetchUserById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch user';
      });
    
    // createUser
    builder
      .addCase(createUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.users.push(action.payload);
      })
      .addCase(createUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to create user';
      });
  }
});

// 导出actions
export const { clearError, setCurrentUser, clearCurrentUser } = userSlice.actions;

// 导出reducer
export default userSlice.reducer;

// 导出selectors
export const selectUsers = (state: { users: UserState }) => state.users.users;
export const selectCurrentUser = (state: { users: UserState }) => state.users.currentUser;
export const selectUsersLoading = (state: { users: UserState }) => state.users.isLoading;
export const selectUsersError = (state: { users: UserState }) => state.users.error;

// 复杂selectors
export const selectUserById = (userId: string) => (state: { users: UserState }) => 
  state.users.users.find(user => user.id === userId);

export const selectUsersByRole = (role: User['role']) => (state: { users: UserState }) => 
  state.users.users.filter(user => user.role === role);

export const selectUsersCount = (state: { users: UserState }) => state.users.users.length;
```

```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';

// 配置store
export const store = configureStore({
  reducer: {
    users: userReducer
    // 其他reducers...
  },
  // 开发工具配置
  devTools: process.env.NODE_ENV !== 'production'
});

// 导出类型
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

```typescript
// hooks/redux.ts
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';

// 使用类型化的hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

```typescript
// components/UserList.tsx
import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchUsers, selectUsers, selectUsersLoading, selectUsersError } from '../store/slices/userSlice';

const UserList: React.FC = () => {
  const dispatch = useAppDispatch();
  const users = useAppSelector(selectUsers);
  const isLoading = useAppSelector(selectUsersLoading);
  const error = useAppSelector(selectUsersError);
  
  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      <h2>User List</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>
            {user.name} ({user.email}) - {user.role}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserList;
```

### 10.4.2 Zustand与TypeScript

```typescript
// stores/userStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// 类型定义
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

interface UserState {
  // 状态
  users: User[];
  currentUser: User | null;
  isLoading: boolean;
  error: string | null;
  
  // 操作
  fetchUsers: () => Promise<void>;
  fetchUserById: (id: string) => Promise<void>;
  createUser: (userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateUser: (id: string, updates: Partial<User>) => Promise<void>;
  deleteUser: (id: string) => Promise<void>;
  setCurrentUser: (user: User | null) => void;
  clearError: () => void;
}

// 创建store
export const useUserStore = create<UserState>()(
  devtools(
    (set, get) => ({
      // 初始状态
      users: [],
      currentUser: null,
      isLoading: false,
      error: null,
      
      // 操作
      fetchUsers: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch('/api/users');
          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch users');
          }
          
          set({ users: data.users, isLoading: false });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'An error occurred'
          });
        }
      },
      
      fetchUserById: async (id: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(`/api/users/${id}`);
          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch user');
          }
          
          set({ currentUser: data, isLoading: false });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'An error occurred'
          });
        }
      },
      
      createUser: async (userData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
          });
          
          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.message || 'Failed to create user');
          }
          
          set(state => ({
            users: [...state.users, data],
            isLoading: false
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'An error occurred'
          });
        }
      },
      
      updateUser: async (id, updates) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(`/api/users/${id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
          });
          
          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.message || 'Failed to update user');
          }
          
          set(state => ({
            users: state.users.map(user =>
              user.id === id ? { ...user, ...data } : user
            ),
            currentUser: state.currentUser?.id === id 
              ? { ...state.currentUser, ...data } 
              : state.currentUser,
            isLoading: false
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'An error occurred'
          });
        }
      },
      
      deleteUser: async (id) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(`/api/users/${id}`, {
            method: 'DELETE'
          });
          
          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to delete user');
          }
          
          set(state => ({
            users: state.users.filter(user => user.id !== id),
            currentUser: state.currentUser?.id === id ? null : state.currentUser,
            isLoading: false
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'An error occurred'
          });
        }
      },
      
      setCurrentUser: (user) => set({ currentUser: user }),
      clearError: () => set({ error: null })
    })
  )
);
```

```typescript
// hooks/useUser.ts
import { useUserStore } from '../stores/userStore';
import { useCallback } from 'react';
import { User } from '../stores/userStore';

// 自定义Hook封装用户相关操作
export const useUser = () => {
  const {
    users,
    currentUser,
    isLoading,
    error,
    fetchUsers,
    fetchUserById,
    createUser,
    updateUser,
    deleteUser,
    setCurrentUser,
    clearError
  } = useUserStore();
  
  // 派生状态
  const getUserById = useCallback((id: string) => {
    return users.find(user => user.id === id);
  }, [users]);
  
  const getUsersByRole = useCallback((role: User['role']) => {
    return users.filter(user => user.role === role);
  }, [users]);
  
  const userCount = users.length;
  
  return {
    // 状态
    users,
    currentUser,
    isLoading,
    error,
    userCount,
    
    // 操作
    fetchUsers,
    fetchUserById,
    createUser,
    updateUser,
    deleteUser,
    setCurrentUser,
    clearError,
    
    // 派生状态和操作
    getUserById,
    getUsersByRole
  };
};
```

---

## 10.5 类型驱动开发实战

### 10.5.1 设计类型优先的API

```typescript
// types/api.types.ts
// 基础API响应类型
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// 分页响应类型
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: number;
  page: number;
  limit: number;
  hasNextPage: boolean;
}

// API错误响应类型
export interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

// 用户相关类型
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: UserRole;
  status: UserStatus;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = 'admin' | 'manager' | 'member' | 'guest';
export type UserStatus = 'active' | 'inactive' | 'suspended';

export interface CreateUserRequest {
  name: string;
  email: string;
  role: UserRole;
  password: string;
}

export interface UpdateUserRequest {
  name?: string;
  email?: string;
  avatar?: string;
  role?: UserRole;
  status?: UserStatus;
}

export interface UserListParams {
  page?: number;
  limit?: number;
  role?: UserRole;
  status?: UserStatus;
  search?: string;
}
```

```typescript
// services/api.service.ts
import { ApiResponse, PaginatedResponse, ApiErrorResponse } from '../types/api.types';

// API客户端类
export class ApiService {
  private baseUrl: string;
  
  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }
  
  // 通用请求方法
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      // 使用类型断言，因为我们知道这是一个错误响应
      const errorResponse = data as ApiErrorResponse;
      throw new Error(errorResponse.error.message);
    }
    
    return data as T;
  }
  
  // GET请求
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }
  
  // POST请求
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    });
  }
  
  // PUT请求
  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  // DELETE请求
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE'
    });
  }
  
  // 带参数的GET请求
  async getWithParams<T>(endpoint: string, params: Record<string, any>): Promise<T> {
    const searchParams = new URLSearchParams();
    
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    }
    
    const url = `${endpoint}?${searchParams.toString()}`;
    return this.get<T>(url);
  }
}
```

### 10.5.2 类型驱动的组件开发

```typescript
// components/DataTable.tsx
import React, { useMemo } from 'react';

// 表格列定义类型
export interface TableColumn<T> {
  key: keyof T;
  title: string;
  width?: string | number;
  sortable?: boolean;
  render?: (value: any, record: T) => React.ReactNode;
  className?: string;
}

// 排序类型
export interface SortConfig {
  field?: string;
  direction?: 'asc' | 'desc';
}

// 分页类型
export interface Pagination {
  current: number;
  pageSize: number;
  total: number;
  onChange?: (page: number, pageSize: number) => void;
  showSizeChanger?: boolean;
}

// 数据表格组件属性
export interface DataTableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  rowKey?: keyof T | ((record: T) => string);
  onRow?: (record: T) => React.HTMLAttributes<HTMLElement>;
  sortConfig?: SortConfig;
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
  pagination?: Pagination | false;
}

function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  rowKey = 'id' as keyof T,
  onRow,
  sortConfig,
  onSort,
  pagination
}: DataTableProps<T>) {
  // 处理排序
  const { sortedData, renderSortIcon } = useMemo(() => {
    // 如果没有排序配置，直接返回原始数据
    if (!sortConfig?.field || !sortConfig?.direction) {
      return {
        sortedData: data,
        renderSortIcon: () => null
      };
    }
    
    // 排序数据
    const sorted = [...data].sort((a, b) => {
      const aValue = a[sortConfig.field as keyof T];
      const bValue = b[sortConfig.field as keyof T];
      
      if (aValue === bValue) return 0;
      
      const result = aValue > bValue ? 1 : -1;
      return sortConfig.direction === 'asc' ? result : -result;
    });
    
    // 渲染排序图标
    const renderIcon = (columnKey: keyof T) => {
      if (sortConfig.field !== columnKey) return null;
      
      return sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
    };
    
    return {
      sortedData: sorted,
      renderSortIcon: renderIcon
    };
  }, [data, sortConfig]);
  
  // 处理列头点击
  const handleHeaderClick = (columnKey: keyof T, sortable?: boolean) => {
    if (!sortable || !onSort) return;
    
    let direction: 'asc' | 'desc' = 'asc';
    
    if (sortConfig?.field === columnKey && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    onSort(columnKey as string, direction);
  };
  
  // 获取行键
  const getRowKey = (record: T): string => {
    if (typeof rowKey === 'function') {
      return rowKey(record);
    }
    return record[rowKey] as string;
  };
  
  // 渲染表格
  return (
    <div className="data-table">
      {loading && <div className="loading-indicator">Loading...</div>}
      
      <table className="data-table-table">
        <thead>
          <tr>
            {columns.map(column => (
              <th
                key={column.key as string}
                style={{ width: column.width }}
                className={column.className}
                onClick={() => handleHeaderClick(column.key, column.sortable)}
              >
                {column.title}
                {column.sortable && renderSortIcon(column.key)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map(record => {
            const key = getRowKey(record);
            const rowProps = onRow ? onRow(record) : {};
            
            return (
              <tr key={key} {...rowProps}>
                {columns.map(column => {
                  const value = record[column.key];
                  return (
                    <td key={column.key as string}>
                      {column.render ? column.render(value, record) : value}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
      
      {pagination && pagination.total > 0 && (
        <div className="data-table-pagination">
          <button
            disabled={pagination.current === 1}
            onClick={() => pagination.onChange?.(pagination.current - 1, pagination.pageSize)}
          >
            Previous
          </button>
          
          <span className="page-info">
            Page {pagination.current} of {Math.ceil(pagination.total / pagination.pageSize)}
          </span>
          
          <button
            disabled={pagination.current * pagination.pageSize >= pagination.total}
            onClick={() => pagination.onChange?.(pagination.current + 1, pagination.pageSize)}
          >
            Next
          </button>
          
          {pagination.showSizeChanger && (
            <select
              value={pagination.pageSize}
              onChange={e => {
                const newPageSize = Number(e.target.value);
                pagination.onChange?.(1, newPageSize);
              }}
            >
              <option value={10}>10 per page</option>
              <option value={20}>20 per page</option>
              <option value={50}>50 per page</option>
            </select>
          )}
        </div>
      )}
    </div>
  );
}

export default DataTable;
```

```typescript
// components/UserTable.tsx
import React, { useState } from 'react';
import DataTable, { TableColumn, SortConfig } from './DataTable';
import { User, UserRole } from '../types/api.types';
import { useUser } from '../hooks/useUser';

const UserTable: React.FC = () => {
  const { users, isLoading, error, fetchUsers, deleteUser } = useUser();
  const [sortConfig, setSortConfig] = useState<SortConfig>({});
  
  // 表格列定义
  const columns: TableColumn<User>[] = [
    {
      key: 'id',
      title: 'ID',
      width: '80px',
      sortable: true
    },
    {
      key: 'name',
      title: 'Name',
      sortable: true
    },
    {
      key: 'email',
      title: 'Email',
      sortable: true
    },
    {
      key: 'role',
      title: 'Role',
      width: '120px',
      sortable: true,
      render: (role: UserRole) => (
        <span className={`role-badge role-${role}`}>
          {role.charAt(0).toUpperCase() + role.slice(1)}
        </span>
      )
    },
    {
      key: 'status',
      title: 'Status',
      width: '120px',
      sortable: true,
      render: (status: string) => (
        <span className={`status-badge status-${status}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      )
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '150px',
      render: (_, record) => (
        <div className="action-buttons">
          <button>Edit</button>
          <button onClick={() => deleteUser(record.id)} className="danger">
            Delete
          </button>
        </div>
      )
    }
  ];
  
  // 处理排序
  const handleSort = (field: string, direction: 'asc' | 'desc') => {
    setSortConfig({ field, direction });
  };
  
  // 处理行点击
  const handleRowClick = (record: User) => {
    console.log('Row clicked:', record);
    return {
      onClick: () => {
        console.log('Row clicked:', record);
      },
      style: { cursor: 'pointer' }
    };
  };
  
  // 初始化数据
  React.useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);
  
  if (error) {
    return <div className="error-message">{error}</div>;
  }
  
  return (
    <div className="user-table-container">
      <h1>User Management</h1>
      
      <DataTable<User>
        data={users}
        columns={columns}
        loading={isLoading}
        onRow={handleRowClick}
        sortConfig={sortConfig}
        onSort={handleSort}
        pagination={{
          current: 1,
          pageSize: 10,
          total: users.length,
          onChange: (page, pageSize) => console.log(`Page changed to ${page}, pageSize ${pageSize}`),
          showSizeChanger: true
        }}
      />
    </div>
  );
};

export default UserTable;
```

---

## 本章小结

在本章中，我们探讨了TypeScript与三大主流前端框架的集成方式。从React的组合式API和Hooks，到Vue 3的组合式API和Pinia，再到Angular的依赖注入和模块化，我们学习了如何在不同的框架中充分利用TypeScript的类型系统。

主要收获包括：

1. 掌握了在React项目中使用TypeScript的方法，包括组件定义、Hooks使用和状态管理
2. 了解了Vue 3与TypeScript的集成，包括选项式API、组合式API和Pinia状态管理
3. 探索了Angular框架中的TypeScript应用，包括组件、服务、路由和守卫
4. 学习了使用Redux Toolkit和Zustand进行类型安全的状态管理
5. 掌握了类型驱动开发的方法，从类型设计到组件实现

通过这些知识，您现在可以在各种前端框架中自信地使用TypeScript，构建类型安全、可维护的应用程序。这标志着我们从TypeScript入门到专家的完整旅程的结束，但您的TypeScript学习之旅才刚刚开始。继续探索、实践和分享，您将成为一名真正的TypeScript专家！