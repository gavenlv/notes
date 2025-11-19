// 高级泛型特性示例
function demonstrateAdvancedGenerics(): void {
    console.log("\n=== Advanced Generics Demo ===");
    
    // 条件类型
    type IsString<T> = T extends string ? true : false;
    
    type Test1 = IsString<string>; // true
    type Test2 = IsString<number>; // false
    
    // 使用条件类型创建类型安全的函数
    function process<T>(value: T): T extends string ? string : number {
        if (typeof value === "string") {
            return value.toUpperCase() as any;
        }
        return value as any;
    }
    
    const result1 = process("hello"); // string
    const result2 = process(42);      // number
    
    console.log(`process("hello"): ${result1} (type: ${typeof result1})`);
    console.log(`process(42): ${result2} (type: ${typeof result2})`);
    
    // 条件类型与泛型约束结合
    type NonNullable<T> = T extends null | undefined ? never : T;
    
    function filterNullable<T>(value: T): NonNullable<T> {
        return value as NonNullable<T>;
    }
    
    const filtered1 = filterNullable("hello"); // string
    // const filtered2 = filterNullable(null);    // never
    // const filtered3 = filterNullable(undefined); // never
    
    console.log(`filterNullable("hello"): ${filtered1}`);
    
    // 分布式条件类型
    type ToArray<T> = T extends any ? T[] : never;
    
    type StringOrNumberArray = ToArray<string | number>;
    // 结果: string[] | number[]
    
    // 映射类型
    type Readonly<T> = {
        readonly [P in keyof T]: T[P];
    };
    
    type Partial<T> = {
        [P in keyof T]?: T[P];
    };
    
    interface User {
        id: number;
        name: string;
        email: string;
    }
    
    type ReadonlyUser = Readonly<User>;
    type PartialUser = Partial<User>;
    
    const user: User = {
        id: 1,
        name: "Alice",
        email: "alice@example.com"
    };
    
    const readonlyUser: ReadonlyUser = user;
    const partialUser: PartialUser = {
        name: "Bob"
    };
    
    console.log("User:", user);
    console.log("Partial user:", partialUser);
    
    // 自定义映射类型
    type Stringify<T> = {
        [K in keyof T]: string;
    };
    
    type StringifiedUser = Stringify<User>;
    
    // 创建修改后的接口
    type ModifiedUser = {
        readonly id: number;
        name?: string;
        email: string;
    };
    
    // 等价于：
    type ModifiedUserEquivalent = {
        readonly [P in "id"]: User[P];
    } & {
        [P in "name"]?: User[P];
    } & {
        [P in "email"]: User[P];
    };
    
    // 使用infer关键字进行类型推断
    type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;
    
    function greet(name: string): string {
        return `Hello, ${name}`;
    }
    
    type GreetReturnType = ReturnType<typeof greet>; // string
    
    // 提取函数参数类型
    type Parameters<T> = T extends (...args: infer P) => any ? P : never;
    
    type GreetParameters = Parameters<typeof greet>; // [string]
    
    // 提取数组元素类型
    type ElementOf<T> = T extends (infer U)[] ? U : never;
    
    type StringArrayElement = ElementOf<string[]>; // string
    
    // 提取Promise的值类型
    type UnpackPromise<T> = T extends Promise<infer U> ? U : never;
    
    type PromiseValue = UnpackPromise<Promise<string>>; // string
    
    // 条件类型中的递归
    type DeepPartial<T> = {
        [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
    };
    
    interface TreeNode {
        value: string;
        left?: TreeNode;
        right?: TreeNode;
    }
    
    type PartialTreeNode = DeepPartial<TreeNode>;
    // {
    //     value?: string;
    //     left?: {
    //         value?: string;
    //         left?: TreeNode;
    //         right?: TreeNode;
    //     };
    //     right?: {
    //         value?: string;
    //         left?: TreeNode;
    //         right?: TreeNode;
    //     };
    // }
    
    // 高级泛型应用：类型安全的状态管理
    type StateUpdater<T> = (prevState: T) => T;
    
    type Reducer<T, A> = (state: T, action: A) => T;
    
    type ActionType<T> = {
        type: string;
        payload?: T;
    };
    
    interface State {
        count: number;
        user: {
            name: string;
            age: number;
        } | null;
    }
    
    type IncrementAction = ActionType<undefined> & { type: "INCREMENT" };
    type DecrementAction = ActionType<undefined> & { type: "DECREMENT" };
    type SetUserAction = ActionType<State["user"]> & { type: "SET_USER" };
    
    type AppActions = IncrementAction | DecrementAction | SetUserAction;
    
    const appReducer: Reducer<State, AppActions> = (state, action) => {
        switch (action.type) {
            case "INCREMENT":
                return { ...state, count: state.count + 1 };
            case "DECREMENT":
                return { ...state, count: state.count - 1 };
            case "SET_USER":
                return { ...state, user: action.payload || null };
            default:
                // 不应该到达这里
                const _exhaustiveCheck: never = action;
                return state;
        }
    };
    
    // 创建类型安全的store
    class Store<T, A> {
        private state: T;
        private reducer: Reducer<T, A>;
        private listeners: Array<(state: T) => void> = [];
        
        constructor(initialState: T, reducer: Reducer<T, A>) {
            this.state = initialState;
            this.reducer = reducer;
        }
        
        getState(): T {
            return this.state;
        }
        
        dispatch(action: A): void {
            this.state = this.reducer(this.state, action);
            this.listeners.forEach(listener => listener(this.state));
        }
        
        subscribe(listener: (state: T) => void): () => void {
            this.listeners.push(listener);
            
            // 返回取消订阅函数
            return () => {
                const index = this.listeners.indexOf(listener);
                if (index >= 0) {
                    this.listeners.splice(index, 1);
                }
            };
        }
    }
    
    const appStore = new Store(
        {
            count: 0,
            user: null
        },
        appReducer
    );
    
    // 订阅状态变化
    const unsubscribe = appStore.subscribe(state => {
        console.log("State updated:", state);
    });
    
    // 派发动作
    appStore.dispatch({ type: "INCREMENT" });
    appStore.dispatch({ type: "INCREMENT" });
    appStore.dispatch({ type: "SET_USER", payload: { name: "Alice", age: 30 } });
    appStore.dispatch({ type: "DECREMENT" });
    
    // 取消订阅
    unsubscribe();
    
    // 高级泛型应用：类型安全的API客户端
    interface ApiResponse<T = any> {
        data: T;
        status: number;
        message: string;
    }
    
    interface ApiEndpoint {
        url: string;
        method: "GET" | "POST" | "PUT" | "DELETE";
    }
    
    type ApiConfig = {
        [K in string]: ApiEndpoint;
    };
    
    type ApiClient<T extends ApiConfig> = {
        [K in keyof T]: (
            ...args: T[K]["method"] extends "GET" 
                ? [params?: Record<string, any>] 
                : [data: any, params?: Record<string, any>]
        ) => Promise<ApiResponse>;
    };
    
    // 定义API配置
    const apiConfig: ApiConfig = {
        getUser: {
            url: "/users/:id",
            method: "GET"
        },
        createUser: {
            url: "/users",
            method: "POST"
        },
        updateUser: {
            url: "/users/:id",
            method: "PUT"
        },
        deleteUser: {
            url: "/users/:id",
            method: "DELETE"
        }
    };
    
    // 创建API客户端
    function createApiClient<T extends ApiConfig>(config: T): ApiClient<T> {
        const client = {} as ApiClient<T>;
        
        for (const key in config) {
            const endpoint = config[key];
            
            client[key] = async (...args: any[]) => {
                // 模拟API调用
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve({
                            data: { message: `Called ${endpoint.method} ${endpoint.url}` },
                            status: 200,
                            message: "Success"
                        });
                    }, 100);
                });
            };
        }
        
        return client;
    }
    
    const apiClient = createApiClient(apiConfig);
    
    // 使用类型安全的API客户端
    apiClient.getUser({ id: "123" }).then(response => {
        console.log("Get user response:", response);
    });
    
    apiClient.createUser({ name: "Alice", email: "alice@example.com" }).then(response => {
        console.log("Create user response:", response);
    });
    
    console.log("Advanced generics demo completed!");
}

demonstrateAdvancedGenerics();