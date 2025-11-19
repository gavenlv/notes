// 工具类型示例
function demonstrateUtilityTypes(): void {
    console.log("\n=== Utility Types Demo ===");
    
    // Partial<T>
    interface Todo {
        title: string;
        description: string;
        completed: boolean;
    }
    
    function updateTodo(id: number, fieldsToUpdate: Partial<Todo>): void {
        // 实现更新逻辑
        console.log(`Updating todo ${id} with:`, fieldsToUpdate);
    }
    
    updateTodo(1, { completed: true });
    updateTodo(2, { title: "Updated title", description: "Updated description" });
    
    // Required<T>
    interface PartialTodo {
        title: string;
        description?: string;
        completed?: boolean;
    }
    
    const requiredTodo: Required<PartialTodo> = {
        title: "Complete TypeScript tutorial",
        description: "Finish all chapters and examples",
        completed: false
    };
    
    console.log("Required todo:", requiredTodo);
    
    // Readonly<T>
    interface Configuration {
        apiUrl: string;
        timeout: number;
        retries: number;
    }
    
    const config: Readonly<Configuration> = {
        apiUrl: "https://api.example.com",
        timeout: 5000,
        retries: 3
    };
    
    console.log("Config:", config);
    // config.apiUrl = "https://new-api.example.com"; // 错误：只读属性
    
    // Pick<T, K>
    interface User {
        id: number;
        name: string;
        email: string;
        age: number;
        address: {
            street: string;
            city: string;
            country: string;
        };
    }
    
    type UserContactInfo = Pick<User, "name" | "email">;
    
    const contactInfo: UserContactInfo = {
        name: "Alice",
        email: "alice@example.com"
    };
    
    console.log("Contact info:", contactInfo);
    
    // Omit<T, K>
    type UserCredentials = Omit<User, "id" | "age" | "address">;
    
    const credentials: UserCredentials = {
        name: "Bob",
        email: "bob@example.com"
    };
    
    console.log("Credentials:", credentials);
    
    // Record<K, T>
    type PageInfo = {
        title: string;
        url: string;
        description?: string;
    };
    
    type PageMap = Record<string, PageInfo>;
    
    const pageMap: PageMap = {
        home: { title: "Home", url: "/home", description: "Welcome to our site" },
        about: { title: "About", url: "/about" },
        contact: { title: "Contact", url: "/contact" }
    };
    
    console.log("Page map:", pageMap);
    
    // Exclude<T, U>
    type Primitive = string | number | boolean;
    type NonStringPrimitive = Exclude<Primitive, string>; // number | boolean
    
    const numValue: NonStringPrimitive = 42;
    const boolValue: NonStringPrimitive = true;
    
    console.log("Non-string primitives:", { numValue, boolValue });
    
    // Extract<T, U>
    type StringOrNumber = string | number;
    type JustString = Extract<StringOrNumber, string>; // string
    
    const stringValue: JustString = "Hello, TypeScript";
    console.log("String value:", stringValue);
    
    // NonNullable<T>
    type MaybeString = string | null | undefined;
    type DefinitelyString = NonNullable<MaybeString>; // string
    
    const definitelyString: DefinitelyString = "This is definitely a string";
    console.log("Definitely string:", definitelyString);
    
    // ReturnType<T>
    function createUser(): User {
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
        };
    }
    
    type CreateUserReturn = ReturnType<typeof createUser>; // User
    
    const user: CreateUserReturn = createUser();
    console.log("Created user:", user);
    
    // InstanceType<T>
    class UserClass {
        constructor(
            public name: string,
            public email: string,
            public age: number
        ) {}
        
        greet(): string {
            return `Hello, my name is ${this.name} and I'm ${this.age} years old`;
        }
    }
    
    type UserInstance = InstanceType<typeof UserClass>; // UserClass
    
    const userInstance: UserInstance = new UserClass(
        "Bob",
        "bob@example.com",
        25
    );
    
    console.log("User instance:", userInstance);
    console.log(userInstance.greet());
    
    // Parameters<T>
    function updateUser(
        id: number,
        updates: Partial<User>,
        options?: { notify?: boolean; validate?: boolean }
    ): void {
        // 实现更新逻辑
        console.log(`Updating user ${id} with:`, updates);
        console.log("Options:", options || {});
    }
    
    type UpdateUserParams = Parameters<typeof updateUser>;
    // type UpdateUserParams = [
    //   number,
    //   Partial<User>,
    //   { notify?: boolean; validate?: boolean } | undefined
    // ]
    
    // 使用参数类型
    const updateUserParams: UpdateUserParams = [
        1,
        { name: "Updated Name" },
        { notify: true, validate: true }
    ];
    
    updateUser(...updateUserParams);
    
    // ThisParameterType<T>
    function toHex(this: number): string {
        return this.toString(16);
    }
    
    type ToHexThisType = ThisParameterType<typeof toHex>; // number
    
    function numberToHex(value: number): string {
        return toHex.call(value); // 显式指定this类型
    }
    
    console.log(`Number 255 to hex: ${numberToHex(255)}`); // "ff"
    
    // OmitThisParameter<T, U>
    const boundToHex = function(this: number): string {
        return this.toString(16);
    }.bind(15); // 绑定this为15
    
    type BoundToHex = OmitThisParameter<typeof boundToHex>; // () => string
    
    const hexValue: BoundToHex = boundToHex;
    console.log(`Bound to hex: ${hexValue()}`); // "f"
    
    // 组合使用工具类型
    // 创建一个部分用户更新类型，排除id和敏感字段
    type UserUpdate = Omit<Partial<User>, "id"> & {
        id: number;
    };
    
    const userUpdate: UserUpdate = {
        id: 1,
        name: "Updated Name",
        email: "updated@example.com"
    };
    
    console.log("User update:", userUpdate);
    
    // 创建一个只读的用户选择器类型
    type UserSelector = Pick<User, "id" | "name" | "email">;
    type ReadonlyUserSelector = Readonly<UserSelector>;
    
    const userSelector: ReadonlyUserSelector = {
        id: 1,
        name: "Alice",
        email: "alice@example.com"
    };
    
    console.log("Readonly user selector:", userSelector);
    
    // 使用工具类型创建高级类型
    type DeepPartial<T> = {
        [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
    };
    
    interface TreeNode {
        value: string;
        left?: TreeNode;
        right?: TreeNode;
    }
    
    type PartialTreeNode = DeepPartial<TreeNode>;
    
    const partialTree: PartialTreeNode = {
        value: "root",
        left: {
            value: "left child"
            // right和left的right等都是可选的
        }
    };
    
    console.log("Partial tree:", partialTree);
    
    // 工具类型与函数结合
    function createObjectWithDefaults<T extends Record<string, any>>(
        defaults: T
    ): <U extends DeepPartial<T>>(overrides?: U) => T & U {
        return function<U extends DeepPartial<T>>(overrides?: U): T & U {
            return { ...defaults, ...overrides } as T & U;
        };
    }
    
    const defaultUser = {
        name: "Anonymous",
        email: "anonymous@example.com",
        age: 18,
        address: {
            street: "Unknown",
            city: "Unknown",
            country: "Unknown"
        }
    };
    
    const createUser = createObjectWithDefaults(defaultUser);
    
    const user1 = createUser({
        name: "Alice",
        age: 30
    });
    
    const user2 = createUser({
        name: "Bob",
        email: "bob@example.com",
        address: {
            city: "New York"
        }
    });
    
    console.log("User 1:", user1);
    console.log("User 2:", user2);
    
    // 工具类型与类结合
    class Entity<T extends Record<string, any>> {
        constructor(public data: T) {}
        
        get<K extends keyof T>(key: K): T[K] {
            return this.data[key];
        }
        
        set<K extends keyof T>(key: K, value: T[K]): void {
            this.data[key] = value;
        }
        
        update<P extends DeepPartial<T>>(updates: P): void {
            this.data = { ...this.data, ...updates };
        }
        
        pick<K extends keyof T>(keys: K[]): Pick<T, K> {
            const result = {} as Pick<T, K>;
            for (const key of keys) {
                result[key] = this.data[key];
            }
            return result;
        }
        
        omit<K extends keyof T>(keys: K[]): Omit<T, K> {
            const result = { ...this.data };
            for (const key of keys) {
                delete result[key];
            }
            return result as Omit<T, K>;
        }
    }
    
    const userEntity = new Entity(user);
    
    console.log("Name:", userEntity.get("name"));
    userEntity.set("age", 31);
    userEntity.update({ email: "newemail@example.com" });
    
    const basicInfo = userEntity.pick(["id", "name", "email"]);
    const noAddress = userEntity.omit(["address"]);
    
    console.log("Updated user:", userEntity.data);
    console.log("Basic info:", basicInfo);
    console.log("No address:", noAddress);
}

demonstrateUtilityTypes();