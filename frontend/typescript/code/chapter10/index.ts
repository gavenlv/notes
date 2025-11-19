// 第10章：TypeScript与前端框架集成 - 主入口文件

// 导入React集成示例
import { ReactExample } from './react-integration/react-example';

// 导入Vue集成示例
import { VueExample } from './vue-integration/vue-example';

/**
 * 演示React与TypeScript集成
 */
function demonstrateReactIntegration() {
    console.log("=== React与TypeScript集成示例 ===");
    
    const example = new ReactExample();
    example.runExamples();
}

/**
 * 演示Vue与TypeScript集成
 */
function demonstrateVueIntegration() {
    console.log("\n=== Vue与TypeScript集成示例 ===");
    
    const example = new VueExample();
    example.runExamples();
}

/**
 * 演示Angular与TypeScript集成
 */
function demonstrateAngularIntegration() {
    console.log("\n=== Angular与TypeScript集成示例 ===");
    
    console.log("1. 组件定义:");
    console.log(`
    // 用户组件
    export interface User {
      id: string;
      name: string;
      email: string;
      role: 'admin' | 'user' | 'guest';
    }
    
    @Component({
      selector: 'app-user',
      templateUrl: './user.component.html',
      styleUrls: ['./user.component.css']
    })
    export class UserComponent implements OnInit {
      @Input() user: User;
      @Output() edit = new EventEmitter<string>();
      
      ngOnInit(): void {
        console.log('Component initialized');
      }
      
      onEdit(): void {
        this.edit.emit(this.user.id);
      }
    }
    `);
    
    console.log("2. 服务定义:");
    console.log(`
    // 用户服务
    @Injectable({
      providedIn: 'root'
    })
    export class UserService {
      private users: User[] = [];
      
      constructor(private http: HttpClient) {}
      
      getUsers(): Observable<User[]> {
        return this.http.get<User[]>('/api/users');
      }
      
      createUser(userData: CreateUserRequest): Observable<User> {
        return this.http.post<User>('/api/users', userData);
      }
    }
    `);
    
    console.log("3. 路由配置:");
    console.log(`
    // 路由配置
    const routes: Routes = [
      { 
        path: 'users', 
        component: UserListComponent,
        canActivate: [AuthGuard]
      },
      { 
        path: 'users/:id', 
        component: UserDetailComponent,
        resolve: { user: UserResolverService }
      }
    ];
    `);
    
    console.log("4. 表单处理:");
    console.log(`
    // 响应式表单
    export class UserFormComponent implements OnInit {
      userForm: FormGroup;
      
      constructor(private fb: FormBuilder) {}
      
      ngOnInit(): void {
        this.userForm = this.fb.group({
          name: ['', [Validators.required]],
          email: ['', [Validators.required, Validators.email]],
          role: ['user', Validators.required]
        });
      }
      
      onSubmit(): void {
        if (this.userForm.valid) {
          const userData: CreateUserRequest = this.userForm.value;
          // 提交表单数据
        }
      }
    }
    `);
}

/**
 * 演示状态管理
 */
function demonstrateStateManagement() {
    console.log("\n=== 状态管理与TypeScript集成示例 ===");
    
    console.log("1. Redux Toolkit:");
    console.log(`
    // 用户状态slice
    const userSlice = createSlice({
      name: 'users',
      initialState,
      reducers: {
        setCurrentUser: (state, action: PayloadAction<User | null>) => {
          state.currentUser = action.payload;
        }
      },
      extraReducers: (builder) => {
        builder
          .addCase(fetchUsers.pending, (state) => {
            state.loading = true;
          })
          .addCase(fetchUsers.fulfilled, (state, action) => {
            state.users = action.payload;
            state.loading = false;
          });
      }
    });
    `);
    
    console.log("2. Pinia:");
    console.log(`
    // 用户store
    export const useUserStore = defineStore('user', () => {
      const users = ref<User[]>([]);
      const currentUser = ref<User | null>(null);
      const loading = ref(false);
      
      const fetchUsers = async () => {
        loading.value = true;
        try {
          const data = await api.getUsers();
          users.value = data;
        } finally {
          loading.value = false;
        }
      };
      
      return { users, currentUser, loading, fetchUsers };
    });
    `);
    
    console.log("3. Zustand:");
    console.log(`
    // 用户store
    interface UserState {
      users: User[];
      currentUser: User | null;
      loading: boolean;
      fetchUsers: () => Promise<void>;
      setCurrentUser: (user: User | null) => void;
    }
    
    export const useUserStore = create<UserState>()(
      devtools(
        (set, get) => ({
          users: [],
          currentUser: null,
          loading: false,
          
          fetchUsers: async () => {
            set({ loading: true });
            try {
              const users = await api.getUsers();
              set({ users, loading: false });
            } catch (error) {
              set({ loading: false });
            }
          },
          
          setCurrentUser: (user) => set({ currentUser: user })
        })
      )
    );
    `);
}

/**
 * 演示类型驱动开发
 */
function demonstrateTypeDrivenDevelopment() {
    console.log("\n=== 类型驱动开发示例 ===");
    
    console.log("1. 定义类型优先:");
    console.log(`
    // 首先定义API类型
    interface ApiResponse<T> {
      data: T;
      success: boolean;
      message?: string;
    }
    
    interface User {
      id: string;
      name: string;
      email: string;
      role: 'admin' | 'user' | 'guest';
    }
    
    interface CreateUserRequest {
      name: string;
      email: string;
      role: User['role'];
      password: string;
    }
    
    // 然后实现API服务
    class UserService {
      async createUser(userData: CreateUserRequest): Promise<ApiResponse<User>> {
        // 实现创建用户逻辑
      }
    }
    `);
    
    console.log("2. 类型安全的组件:");
    console.log(`
    // 泛型表格组件
    interface TableColumn<T> {
      key: keyof T;
      title: string;
      render?: (value: any, record: T) => React.ReactNode;
    }
    
    interface DataTableProps<T> {
      data: T[];
      columns: TableColumn<T>[];
      rowKey: keyof T | ((record: T) => string);
    }
    
    function DataTable<T extends Record<string, any>>({
      data,
      columns,
      rowKey
    }: DataTableProps<T>) {
      // 实现表格逻辑
    }
    `);
    
    console.log("3. 类型守卫:");
    console.log(`
    // 类型守卫函数
    function isUser(obj: any): obj is User {
      return (
        obj !== null &&
        typeof obj === 'object' &&
        'id' in obj &&
        'name' in obj &&
        'email' in obj &&
        ['admin', 'user', 'guest'].includes(obj.role)
      );
    }
    
    // 使用类型守卫
    function processUser(user: unknown): User {
      if (isUser(user)) {
        return user; // TypeScript知道这是User类型
      }
      
      throw new Error('Invalid user data');
    }
    `);
}

/**
 * 演示最佳实践
 */
function demonstrateBestPractices() {
    console.log("\n=== TypeScript与前端框架集成最佳实践 ===");
    
    console.log("1. 类型定义组织:");
    console.log(`
    - 按功能模块组织类型文件
    - 使用类型别名和接口的适当场景
    - 避免使用any，使用unknown或具体类型
    - 使用泛型提高代码复用性
    `);
    
    console.log("2. 组件设计:");
    console.log(`
    - 使用明确的props类型定义
    - 使用泛型组件提高复用性
    - 为事件处理器定义明确的类型
    - 使用forwardRef正确暴露ref
    `);
    
    console.log("3. 状态管理:");
    console.log(`
    - 使用类型安全的状态管理库
    - 为状态和actions定义明确的类型
    - 使用派生选择器避免重复计算
    - 为异步操作定义类型
    `);
    
    console.log("4. 代码组织:");
    console.log(`
    - 使用导入类型减少编译开销
    - 合理使用命名空间和模块
    - 避免循环依赖
    - 使用路径映射简化导入路径
    `);
    
    console.log("5. 性能优化:");
    console.log(`
    - 避免在热路径中进行复杂类型检查
    - 使用React.memo/V3的memo优化组件渲染
    - 使用useMemo和useCallback缓存计算结果
    - 合理使用TypeScript的编译选项
    `);
}

/**
 * 运行所有示例
 */
function runAllExamples() {
    console.log("TypeScript与前端框架集成示例");
    console.log("================================");
    
    demonstrateReactIntegration();
    demonstrateVueIntegration();
    demonstrateAngularIntegration();
    demonstrateStateManagement();
    demonstrateTypeDrivenDevelopment();
    demonstrateBestPractices();
    
    console.log("\n=== 所有示例完成 ===");
    console.log("\n总结:");
    console.log("1. TypeScript为前端框架提供了强大的类型支持");
    console.log("2. 合理使用类型可以提高代码质量和开发效率");
    console.log("3. 类型驱动开发有助于设计更可靠的系统");
    console.log("4. 选择合适的类型定义策略对大型项目至关重要");
    console.log("5. 类型安全的状态管理可以减少运行时错误");
    console.log("6. 最佳实践可以最大化TypeScript的价值");
    
    console.log("\n通过本章学习，您应该能够:");
    console.log("- 在React项目中有效使用TypeScript");
    console.log("- 在Vue项目中有效使用TypeScript");
    console.log("- 了解Angular与TypeScript的集成方式");
    console.log("- 实现类型安全的状态管理");
    console.log("- 应用类型驱动开发方法");
    console.log("- 遵循TypeScript与前端框架集成的最佳实践");
}

// 运行示例
runAllExamples();