// 映射类型示例
function demonstrateMappedTypes(): void {
    console.log("\n=== Mapped Types Demo ===");
    
    // 基本映射类型
    interface User {
        id: number;
        name: string;
        email: string;
        age: number;
    }
    
    // 将所有属性变为可选
    type Partial<T> = {
        [P in keyof T]?: T[P];
    };
    
    // 将所有属性变为只读
    type Readonly<T> = {
        readonly [P in keyof T]: T[P];
    };
    
    type PartialUser = Partial<User>;
    type ReadonlyUser = Readonly<User>;
    
    const partialUser: PartialUser = {
        name: "Alice"
    };
    
    const readonlyUser: ReadonlyUser = {
        id: 1,
        name: "Bob",
        email: "bob@example.com",
        age: 30
    };
    
    console.log("Partial user:", partialUser);
    console.log("Readonly user:", readonlyUser);
    
    // 自定义映射类型
    type Stringify<T> = {
        [K in keyof T]: string;
    };
    
    type StringifiedUser = Stringify<User>;
    
    // 添加前缀到所有键名
    type AddPrefix<T, P extends string> = {
        [K in keyof T as `${P}${Capitalize<string & K>`]?: T[K];
    };
    
    type PrefixedUser = AddPrefix<User, "get">;
    
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
    
    // 条件映射类型
    type PickProperties<T, K> = {
        [P in keyof T as T[P] extends K ? P : never]: T[P];
    };
    
    type StringProperties = PickProperties<User, string>;
    // 等价于: { name: string; email: string; }
    
    // 条件映射：选择符合条件类型的属性
    type TypeOfProperties<T, Type> = {
        [P in keyof T as T[P] extends Type ? P : never]: T[P];
    };
    
    type UserStringProperties = TypeOfProperties<User, string>;
    type UserNumberProperties = TypeOfProperties<User, number>;
    
    const stringProps: UserStringProperties = {
        name: "Alice",
        email: "alice@example.com"
    };
    
    const numberProps: UserNumberProperties = {
        id: 123,
        age: 30
    };
    
    console.log("String properties:", stringProps);
    console.log("Number properties:", numberProps);
    
    // 提取必需属性
    type RequiredKeys<T> = {
        [K in keyof T]-?: {} extends Pick<T, K> ? never : K
    }[keyof T];
    
    // 提取可选属性
    type OptionalKeys<T> = {
        [K in keyof T]-?: {} extends Pick<T, K> ? K : never
    }[keyof T];
    
    interface PartialUser {
        id: number;
        name?: string;
        email?: string;
    }
    
    type PartialUserRequiredKeys = RequiredKeys<PartialUser>; // "id"
    type PartialUserOptionalKeys = OptionalKeys<PartialUser>; // "name" | "email"
    
    // 倒转可选性
    type InvertPartial<T> = {
        [P in keyof T]-?: T[P];
    } & {
        [P in keyof T]?: T[P];
    }[keyof T];
    
    type InvertedPartialUser = InvertPartial<PartialUser>;
    
    // 映射类型与条件类型结合
    type Mutable<T> = {
        -readonly [P in keyof T]: T[P];
    };
    
    type MutableReadonlyUser = Mutable<ReadonlyUser>;
    
    // 深度映射类型
    type DeepPartial<T> = {
        [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
    };
    
    interface TreeNode {
        value: string;
        left?: TreeNode;
        right?: TreeNode;
    }
    
    type PartialTreeNode = DeepPartial<TreeNode>;
    
    // 深度Readonly
    type DeepReadonly<T> = {
        readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
    };
    
    type ReadonlyTreeNode = DeepReadonly<TreeNode>;
    
    // 键重映射
    type Getters<T> = {
        [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
    };
    
    type UserGetters = Getters<User>;
    
    const user: User = {
        id: 1,
        name: "Alice",
        email: "alice@example.com",
        age: 30
    };
    
    const userGetters: UserGetters = {
        getId: () => user.id,
        getName: () => user.name,
        getEmail: () => user.email,
        getAge: () => user.age
    };
    
    console.log("User getters:");
    console.log(`ID: ${userGetters.getId()}`);
    console.log(`Name: ${userGetters.getName()}`);
    console.log(`Email: ${userGetters.getEmail()}`);
    console.log(`Age: ${userGetters.getAge()}`);
    
    // 值转换映射
    type TransformValues<T, R> = {
        [P in keyof T]: R;
    };
    
    type UserStringified = TransformValues<User, string>;
    
    const stringifiedUser: UserStringified = {
        id: "1",
        name: "Alice",
        email: "alice@example.com",
        age: "30"
    };
    
    console.log("Stringified user:", stringifiedUser);
    
    // 创建基于另一个接口的接口
    type FromPicker<T, K extends keyof T> = {
        [P in K]: T[P];
    };
    
    type UserBasicInfo = FromPicker<User, "id" | "name">;
    
    const basicUser: UserBasicInfo = {
        id: 1,
        name: "Alice"
    };
    
    console.log("Basic user info:", basicUser);
    
    // 高级映射：创建类型安全的API客户端
    interface ApiEndpoints {
        getUser: {
            method: "GET";
            url: "/users/:id";
            params: { id: string };
            response: User;
        };
        createUser: {
            method: "POST";
            url: "/users";
            params: {};
            body: Partial<User>;
            response: User;
        };
        updateUser: {
            method: "PUT";
            url: "/users/:id";
            params: { id: string };
            body: Partial<User>;
            response: User;
        };
        deleteUser: {
            method: "DELETE";
            url: "/users/:id";
            params: { id: string };
            response: { success: boolean };
        };
    }
    
    type ApiClient = {
        [K in keyof ApiEndpoints]: (
            params: ApiEndpoints[K]["params"],
            body?: ApiEndpoints[K]["body"]
        ) => Promise<ApiEndpoints[K]["response"]>;
    };
    
    // 模拟API客户端实现
    const apiClient: ApiClient = {
        getUser: async (params) => {
            console.log(`Getting user with ID: ${params.id}`);
            return {
                id: 1,
                name: "Alice",
                email: "alice@example.com",
                age: 30
            };
        },
        createUser: async (params, body) => {
            console.log("Creating user:", body);
            return {
                id: 2,
                name: "Bob",
                email: "bob@example.com",
                age: 25
            };
        },
        updateUser: async (params, body) => {
            console.log(`Updating user ${params.id}:`, body);
            return {
                id: 1,
                name: "Alice Smith",
                email: "alice.smith@example.com",
                age: 31
            };
        },
        deleteUser: async (params) => {
            console.log(`Deleting user with ID: ${params.id}`);
            return { success: true };
        }
    };
    
    // 使用类型安全的API客户端
    apiClient.getUser({ id: "1" }).then(user => {
        console.log("User retrieved:", user);
    });
    
    apiClient.createUser({}, { name: "Charlie", email: "charlie@example.com" }).then(user => {
        console.log("User created:", user);
    });
    
    apiClient.updateUser({ id: "1" }, { age: 32 }).then(user => {
        console.log("User updated:", user);
    });
    
    apiClient.deleteUser({ id: "2" }).then(result => {
        console.log("Delete result:", result);
    });
}

demonstrateMappedTypes();