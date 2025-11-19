// 高级类型模式示例
function demonstrateAdvancedTypePatterns(): void {
    console.log("\n=== Advanced Type Patterns Demo ===");
    
    // 类型递归
    // 递归类型定义JSON值
    type JSONValue = 
        | string
        | number
        | boolean
        | null
        | JSONValue[]
        | { [key: string]: JSONValue };
    
    // 使用JSON类型
    const jsonData: JSONValue = {
        name: "Alice",
        age: 30,
        isActive: true,
        tags: ["developer", "typescript"],
        address: {
            street: "123 Main St",
            city: "New York",
            coordinates: [40.7128, 74.0060]
        },
        metadata: null
    };
    
    console.log("JSON data:", jsonData);
    
    // 递归类型定义树节点
    interface TreeNode<T> {
        value: T;
        children?: TreeNode<T>[];
    }
    
    // 创建树节点
    const tree: TreeNode<string> = {
        value: "root",
        children: [
            {
                value: "child1",
                children: [
                    { value: "grandchild1" },
                    { value: "grandchild2" }
                ]
            },
            {
                value: "child2",
                children: [
                    { value: "grandchild3" }
                ]
            }
        ]
    };
    
    // 递归函数处理树
    function traverseTree<T>(
        node: TreeNode<T>, 
        visitor: (value: T, depth: number) => void,
        depth: number = 0
    ): void {
        visitor(node.value, depth);
        
        if (node.children) {
            for (const child of node.children) {
                traverseTree(child, visitor, depth + 1);
            }
        }
    }
    
    console.log("Tree traversal:");
    traverseTree(tree, (value, depth) => {
        console.log(`${"  ".repeat(depth)}- ${value}`);
    });
    
    // 递归类型定义链表节点
    interface ListNode<T> {
        value: T;
        next: ListNode<T> | null;
    }
    
    // 创建链表
    const node3: ListNode<string> = { value: "Third", next: null };
    const node2: ListNode<string> = { value: "Second", next: node3 };
    const node1: ListNode<string> = { value: "First", next: node2 };
    
    // 递归函数处理链表
    function traverseList<T>(
        node: ListNode<T> | null,
        visitor: (value: T) => void
    ): void {
        if (node === null) return;
        
        visitor(node.value);
        traverseList(node.next, visitor);
    }
    
    console.log("List traversal:");
    traverseList(node1, value => console.log(value));
    
    // 品牌类型（Branded Types）
    // 品牌类型模式
    type Branded<T, B> = T & { __brand: B };
    
    // 创建品牌类型
    type UserId = Branded<string, "UserId">;
    type ProductId = Branded<string, "ProductId">;
    
    // 创建品牌值的工厂函数
    function createUserId(id: string): UserId {
        return id as UserId;
    }
    
    function createProductId(id: string): ProductId {
        return id as ProductId;
    }
    
    // 使用品牌类型
    const userId = createUserId("user123");
    const productId = createProductId("prod456");
    
    // 类型安全：不能混用
    function processUserId(id: UserId): void {
        console.log(`Processing user ID: ${id}`);
    }
    
    function processProductId(id: ProductId): void {
        console.log(`Processing product ID: ${id}`);
    }
    
    processUserId(userId);
    // processUserId(productId); // 错误：ProductId不能赋值给UserId
    
    processProductId(productId);
    // processProductId(userId); // 错误：UserId不能赋值给ProductId
    
    // 品牌类型与类型守卫
    function isUserId(value: string): value is UserId {
        return value.startsWith("user");
    }
    
    function processId(id: string) {
        if (isUserId(id)) {
            // 这里TypeScript知道id是UserId类型
            processUserId(id);
        } else {
            console.log("Processing generic ID");
        }
    }
    
    processId("user123"); // 识别为UserId
    processId("prod456"); // 不是UserId
    
    // 不透明类型（Opaque Types）
    // 不透明类型模式
    type Opaque<T, Token> = T & { readonly __opaque: Token };
    
    // 创建不透明类型
    type Meter = Opaque<number, "Meter">;
    type Second = Opaque<number, "Second">;
    
    // 创建不透明值的工厂函数
    function createMeters(value: number): Meter {
        return value as Meter;
    }
    
    function createSeconds(value: number): Second {
        return value as Second;
    }
    
    // 使用不透明类型
    const distance = createMeters(100);
    const time = createSeconds(10);
    
    // 类型安全：不能直接操作底层类型
    // distance + time; // 错误：Meter和Second不能直接相加
    
    // 提供安全的操作函数
    function calculateSpeed(distance: Meter, time: Second): number {
        // 可以通过类型断言访问底层值
        return (distance as number) / (time as number);
    }
    
    const speed = calculateSpeed(distance, time);
    console.log(`Speed: ${speed} meters per second`);
    
    // 类型级别的状态机
    type State = "Idle" | "Loading" | "Success" | "Error";
    
    type StateMachine = {
        [K in State]: {
            on: {
                [E in string]: K extends "Idle"
                    ? "Loading"
                    : K extends "Loading"
                        ? "Success" | "Error"
                        : K extends "Success"
                            ? "Idle"
                            : K extends "Error"
                                ? "Idle"
                                : never;
            };
        };
    };
    
    const stateMachine: StateMachine = {
        Idle: {
            on: {
                fetch: "Loading"
            }
        },
        Loading: {
            on: {
                success: "Success",
                error: "Error"
            }
        },
        Success: {
            on: {
                reset: "Idle"
            }
        },
        Error: {
            on: {
                retry: "Loading",
                reset: "Idle"
            }
        }
    };
    
    // 类型安全的Redux风格action创建器
    type ActionType<T extends string, P = undefined> = P extends undefined
        ? { type: T }
        : { type: T; payload: P };
    
    type UserAction = 
        | ActionType<"USER_FETCH_REQUEST">
        | ActionType<"USER_FETCH_SUCCESS", User>
        | ActionType<"USER_FETCH_ERROR", string>;
    
    const userActions = {
        fetchRequest: (): ActionType<"USER_FETCH_REQUEST"> => ({ type: "USER_FETCH_REQUEST" }),
        fetchSuccess: (user: User): ActionType<"USER_FETCH_SUCCESS", User> => ({
            type: "USER_FETCH_SUCCESS",
            payload: user
        }),
        fetchError: (error: string): ActionType<"USER_FETCH_ERROR", string> => ({
            type: "USER_FETCH_ERROR",
            payload: error
        })
    };
    
    // 类型安全的HTTP客户端
    type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
    
    type Endpoint<T = any> = {
        path: string;
        method: HttpMethod;
        request?: T;
        response?: any;
    };
    
    type ApiEndpoints = {
        users: Endpoint<undefined, User[]>;
        user: Endpoint<undefined, User>;
        createUser: Endpoint<Partial<User>, User>;
        updateUser: Endpoint<Partial<User>, User>;
        deleteUser: Endpoint<undefined, { success: boolean }>;
    };
    
    // 类型安全的API客户端函数
    function createApiClient<T extends Record<string, Endpoint>>(endpoints: T) {
        const client = {} as {
            [K in keyof T]: (
                params?: T[K]["request"]
            ) => Promise<T[K]["response"]>;
        };
        
        for (const key in endpoints) {
            const endpoint = endpoints[key];
            
            client[key] = async (params?: any) => {
                // 模拟API调用
                console.log(`${endpoint.method} ${endpoint.path}`, params || "");
                
                // 模拟响应
                if (key === "user") {
                    return {
                        id: 1,
                        name: "Alice",
                        email: "alice@example.com",
                        age: 30,
                        address: {
                            street: "123 Main St",
                            city: "New York",
                            country: "USA"
                        }
                    } as any;
                }
                
                return { success: true } as any;
            };
        }
        
        return client;
    }
    
    const apiEndpoints: ApiEndpoints = {
        users: { path: "/api/users", method: "GET" },
        user: { path: "/api/user/:id", method: "GET" },
        createUser: { path: "/api/users", method: "POST" },
        updateUser: { path: "/api/user/:id", method: "PUT" },
        deleteUser: { path: "/api/user/:id", method: "DELETE" }
    };
    
    const apiClient = createApiClient(apiEndpoints);
    
    // 使用类型安全的API客户端
    apiClient.user().then(user => {
        console.log("Fetched user:", user);
    });
    
    apiClient.createUser({ name: "Bob", email: "bob@example.com" }).then(user => {
        console.log("Created user:", user);
    });
    
    // 类型级的表单验证器
    type ValidationRule<T, E = string> = {
        validate: (value: T) => boolean;
        message: E;
    };
    
    type ValidationRules<T> = {
        [K in keyof T]?: ValidationRule<T[K], string>;
    };
    
    type ValidationErrors<T> = {
        [K in keyof T]?: string;
    };
    
    function validate<T>(data: T, rules: ValidationRules<T>): {
        isValid: boolean;
        errors: ValidationErrors<T>;
    } {
        const errors = {} as ValidationErrors<T>;
        let isValid = true;
        
        for (const key in rules) {
            const rule = rules[key];
            if (rule && !rule.validate(data[key])) {
                errors[key] = rule.message;
                isValid = false;
            }
        }
        
        return { isValid, errors };
    }
    
    interface FormData {
        name: string;
        email: string;
        age: number;
        password: string;
    }
    
    const formData: FormData = {
        name: "Alice",
        email: "alice@example.com",
        age: 30,
        password: "password123"
    };
    
    const formRules: ValidationRules<FormData> = {
        name: {
            validate: value => value.length > 0,
            message: "Name is required"
        },
        email: {
            validate: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            message: "Please enter a valid email"
        },
        age: {
            validate: value => value >= 18,
            message: "You must be at least 18 years old"
        },
        password: {
            validate: value => value.length >= 8,
            message: "Password must be at least 8 characters"
        }
    };
    
    const validation = validate(formData, formRules);
    console.log("Form validation:", validation);
}

demonstrateAdvancedTypePatterns();