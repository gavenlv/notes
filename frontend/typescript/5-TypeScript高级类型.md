# 5. TypeScript高级类型

## 5.1 联合类型（Union Types）

联合类型表示一个值可以是几种类型之一，使用`|`符号分隔各种类型。

### 5.1.1 基本联合类型

```typescript
// 基本联合类型
let value: string | number;
value = "Hello";
value = 42;

// 函数参数联合类型
function processValue(value: string | number): void {
    if (typeof value === "string") {
        console.log(value.toUpperCase()); // TypeScript知道这里是string
    } else {
        console.log(value.toFixed(2)); // TypeScript知道这里是number
    }
}

// 字面量联合类型
type Direction = "North" | "South" | "East" | "West";
let direction: Direction = "North";
// direction = "Northeast"; // 错误："Northeast"不是Direction类型
```

### 5.1.2 联合类型与类型守卫

类型守卫是运行时检查，确保在特定代码块中类型是特定的类型。

```typescript
// typeof 类型守卫
function padLeft(value: string, padding: string | number): string {
    if (typeof padding === "number") {
        return Array(padding + 1).join(" ") + value;
    }
    return padding + value;
}

// 自定义类型守卫
interface Cat {
    meow(): void;
}

interface Dog {
    bark(): void;
}

function isCat(animal: Cat | Dog): animal is Cat {
    return (animal as Cat).meow !== undefined;
}

function makeSound(animal: Cat | Dog): void {
    if (isCat(animal)) {
        animal.meow(); // TypeScript知道animal是Cat
    } else {
        animal.bark(); // TypeScript知道animal是Dog
    }
}
```

### 5.1.3 可辨识联合类型

可辨识联合类型是包含共同字面量类型属性的联合类型，有助于类型安全的类型区分。

```typescript
interface Square {
    kind: "square";
    size: number;
}

interface Rectangle {
    kind: "rectangle";
    width: number;
    height: number;
}

interface Circle {
    kind: "circle";
    radius: number;
}

type Shape = Square | Rectangle | Circle;

function area(shape: Shape): number {
    switch (shape.kind) {
        case "square":
            return shape.size * shape.size;
        case "rectangle":
            return shape.width * shape.height;
        case "circle":
            return Math.PI * shape.radius ** 2;
        default:
            // 确保所有情况都被处理
            const _exhaustiveCheck: never = shape;
            return _exhaustiveCheck;
    }
}
```

## 5.2 交叉类型（Intersection Types）

交叉类型将多个类型合并为一个类型，使用`&`符号连接类型。

### 5.2.1 基本交叉类型

```typescript
interface Person {
    name: string;
    age: number;
}

interface Employee {
    employeeId: string;
    department: string;
}

// 交叉类型
type PersonEmployee = Person & Employee;

let personEmployee: PersonEmployee = {
    name: "Alice",
    age: 30,
    employeeId: "EMP123",
    department: "Engineering"
};
```

### 5.2.2 交叉类型与同名属性

当交叉类型中的同名属性类型不同时，结果将是这些类型的交叉类型（通常是never）。

```typescript
interface A {
    value: number;
}

interface B {
    value: string;
}

// AB的value属性是never类型，因为number和string没有交集
type AB = A & B;
// const ab: AB = { value: 42 }; // 错误：number不能赋值给never
```

## 5.3 条件类型（Conditional Types）

条件类型根据条件选择一种类型，语法类似于JavaScript中的三元运算符。

### 5.3.1 基本条件类型

```typescript
// 基本条件类型
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 使用条件类型创建函数返回类型
function process<T>(value: T): T extends string ? string : number {
    if (typeof value === "string") {
        return value.toUpperCase() as any;
    }
    return value as any;
}

const result1 = process("hello"); // string
const result2 = process(42);      // number
```

### 5.3.2 分布式条件类型

当条件类型作用于联合类型时，它会变成分布式条件类型。

```typescript
// 分布式条件类型
type ToArray<T> = T extends any ? T[] : never;

type StringOrNumberArray = ToArray<string | number>;
// 结果：string[] | number[]

// 提取字符串类型
type ExtractString<T> = T extends string ? T : never;

type StringTypes = ExtractString<string | number | boolean>;
// 结果：string
```

### 5.3.3 条件类型与infer关键字

`infer`关键字可以从泛型类型中推断出部分类型。

```typescript
// 使用infer推断函数返回类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

function greet(name: string): string {
    return `Hello, ${name}`;
}

type GreetReturnType = ReturnType<typeof greet>; // string

// 使用infer推断数组元素类型
type ElementOf<T> = T extends (infer U)[] ? U : never;

type StringArrayElement = ElementOf<string[]>; // string

// 使用infer推断Promise值类型
type UnpackPromise<T> = T extends Promise<infer U> ? U : never;

type PromiseValue = UnpackPromise<Promise<string>>; // string
```

## 5.4 映射类型（Mapped Types）

映射类型基于旧类型创建新类型，遍历旧类型的所有属性并应用转换。

### 5.4.1 基本映射类型

```typescript
// 将所有属性变为可选
type Partial<T> = {
    [P in keyof T]?: T[P];
};

// 将所有属性变为只读
type Readonly<T> = {
    readonly [P in keyof T]: T[P];
};

interface User {
    id: number;
    name: string;
    email: string;
}

type PartialUser = Partial<User>;
type ReadonlyUser = Readonly<User>;

// 等价于：
// {
//     id?: number;
//     name?: string;
//     email?: string;
// }

// 等价于：
// {
//     readonly id: number;
//     readonly name: string;
//     readonly email: string;
// }
```

### 5.4.2 自定义映射类型

```typescript
// 将所有属性变为字符串类型
type Stringify<T> = {
    [K in keyof T]: string;
};

type StringifiedUser = Stringify<User>;
// 等价于：
// {
//     id: string;
//     name: string;
//     email: string;
// }

// 添加前缀到所有键名
type AddPrefix<T, P extends string> = {
    [K in keyof T as `${P}${Capitalize<string & K}`>]: T[K];
};

type PrefixedUser = AddPrefix<User, "get">;
// 等价于：
// {
//     getId: number;
//     getName: string;
//     getEmail: string;
// }
```

### 5.4.3 条件映射类型

```typescript
// 将所有可选属性变为必需，必需属性变为可选
type InvertPartial<T> = {
    [P in keyof T]-?: T[P];
} & {
    [P in keyof T]?: T[P];
}[keyof T];

type InvertedUser = InvertPartial<User>;

// 提取必需属性
type RequiredKeys<T> = {
    [K in keyof T]-?: {} extends Pick<T, K> ? never : K
}[keyof T];

type UserRequiredKeys = RequiredKeys<User>; // "id" | "name" | "email"

// 提取可选属性
type OptionalKeys<T> = {
    [K in keyof T]-?: {} extends Pick<T, K> ? K : never
}[keyof T];

interface PartialUser {
    id: number;
    name?: string;
    email?: string;
}

type UserOptionalKeys = OptionalKeys<PartialUser>; // "name" | "email"
```

## 5.5 模板字面量类型

TypeScript 4.1引入了模板字面量类型，允许使用字符串字面量作为类型。

### 5.1.1 基本模板字面量类型

```typescript
// 基本模板字面量类型
type EventName = `on${Capitalize<string>}`;

// 使用模板字面量类型
type ButtonEvent = `onClick` | `onDoubleClick`;
type InputEvent = `onFocus` | `onBlur` | `onChange`;

const buttonEvents: ButtonEvent[] = ["onClick", "onDoubleClick"];
const inputEvents: InputEvent[] = ["onFocus", "onBlur", "onChange"];
```

### 5.5.2 内置字符串操作类型

TypeScript提供了一些内置的字符串操作类型：

```typescript
// Uppercase - 转换为大写
type Upper = Uppercase<"hello">; // "HELLO"

// Lowercase - 转换为小写
type Lower = Lowercase<"HELLO">; // "hello"

// Capitalize - 首字母大写
type CapitalizeType = Capitalize<"hello">; // "Hello"

// Uncapitalize - 首字母小写
type UncapitalizeType = Uncapitalize<"Hello">; // "hello"

// 组合使用
type EventName<T extends string> = `on${Capitalize<T>}`;
type OnClick = EventName<"click">; // "onClick"
type OnFocus = EventName<"focus">; // "onFocus"
```

### 5.5.3 高级模板字面量类型

```typescript
// 使用模板字面量类型创建CSS属性
type CSSProperties = {
    [K in keyof CSSStyleDeclaration as K extends string
        ? K extends `webkit${string}`
            ? `-${Uncapitalize<K>}`
            : K
        : never]: CSSStyleDeclaration[K];
};

// 使用模板字面量类型创建API端点
type ApiEndpoint = `/api/${string}`;
type UserEndpoint = ApiEndpoint & (`/users/${string}` | `/user/${number}`);

const getUser: UserEndpoint = "/api/user/123";
const getAllUsers: UserEndpoint = "/api/users";
// const invalidEndpoint: UserEndpoint = "/api/products"; // 错误

// 使用模板字面量类型创建状态机类型
type Event<T extends string> = `${T}_START` | `${T}_SUCCESS` | `${T}_ERROR`;
type Events = Event<"FETCH_USER"> | Event("CREATE_USER");

const fetchUserStart: Events = "FETCH_USER_START";
const createUserSuccess: Events = "CREATE_USER_SUCCESS";
// const invalidEvent: Events = "DELETE_USER_ERROR"; // 错误
```

## 5.6 索引访问类型（Indexed Access Types）

索引访问类型允许使用`T[K]`语法访问类型`T`的属性`K`的类型。

### 5.6.1 基本索引访问类型

```typescript
interface Person {
    name: string;
    age: number;
    address: {
        street: string;
        city: string;
    };
}

type NameType = Person["name"]; // string
type AgeType = Person["age"]; // number
type AddressType = Person["address"]; // { street: string; city: string; }

// 联合键类型
type NameOrAgeType = Person["name" | "age"]; // string | number
```

### 5.6.2 keyof与索引访问类型

```typescript
type PersonKeys = keyof Person; // "name" | "age" | "address"
type PersonValues = Person[keyof Person]; // string | number | { street: string; city: string }

// 创建类型安全的属性访问函数
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

const person: Person = {
    name: "Alice",
    age: 30,
    address: {
        street: "123 Main St",
        city: "New York"
    }
};

const name = getProperty(person, "name"); // string
const age = getProperty(person, "age"); // number
// const invalid = getProperty(person, "salary"); // 错误：'salary'不是Person的键
```

### 5.6.3 深度索引访问类型

```typescript
// 深度索引访问
type AddressCity = Person["address"]["city"]; // string

// 使用嵌套的keyof
type AddressKeys = keyof Person["address"]; // "street" | "city"

// 创建深度属性访问函数
function getNestedProperty<T, K1 extends keyof T, K2 extends keyof T[K1]>(
    obj: T, 
    key1: K1, 
    key2: K2
): T[K1][K2] {
    return obj[key1][key2];
}

const city = getNestedProperty(person, "address", "city"); // string
```

## 5.7 工具类型（Utility Types）

TypeScript提供了一系列内置的工具类型，用于常见的类型转换。

### 5.7.1 Partial

`Partial<T>`将类型`T`的所有属性变为可选。

```typescript
interface Todo {
    title: string;
    description: string;
    completed: boolean;
}

function updateTodo(id: number, fieldsToUpdate: Partial<Todo>): void {
    // 实现更新逻辑
}

updateTodo(1, { completed: true });
```

### 5.7.2 Required

`Required<T>`将类型`T`的所有属性变为必需。

```typescript
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
```

### 5.7.3 Readonly

`Readonly<T>`将类型`T`的所有属性变为只读。

```typescript
const config: Readonly<Configuration> = {
    apiUrl: "https://api.example.com",
    timeout: 5000
};

// config.apiUrl = "https://new-api.example.com"; // 错误：只读属性
```

### 5.7.4 Pick

`Pick<T, K>`从类型`T`中选择一组属性`K`来创建新类型。

```typescript
interface User {
    id: number;
    name: string;
    email: string;
    age: number;
}

type UserContactInfo = Pick<User, "name" | "email">;
// 等价于：
// {
//     name: string;
//     email: string;
// }
```

### 5.7.5 Omit

`Omit<T, K>`从类型`T`中排除一组属性`K`来创建新类型。

```typescript
type UserCredentials = Omit<User, "id" | "age">;
// 等价于：
// {
//     name: string;
//     email: string;
// }
```

### 5.7.6 Record

`Record<K, T>`创建一个类型，其属性名的类型为`K`，属性值的类型为`T`。

```typescript
type PageInfo = {
    title: string;
    url: string;
};

type PageMap = Record<string, PageInfo>;

const pageMap: PageMap = {
    home: { title: "Home", url: "/home" },
    about: { title: "About", url: "/about" },
    contact: { title: "Contact", url: "/contact" }
};
```

### 5.7.7 Exclude

`Exclude<T, U>`从类型`T`中排除可以赋值给`U`的类型。

```typescript
type Primitive = string | number | boolean;
type NonStringPrimitive = Exclude<Primitive, string>; // number | boolean
```

### 5.7.8 Extract

`Extract<T, U>`从类型`T`中提取可以赋值给`U`的类型。

```typescript
type StringOrNumber = string | number;
type JustString = Extract<StringOrNumber, string>; // string
```

### 5.7.9 NonNullable

`NonNullable<T>`从类型`T`中排除`null`和`undefined`。

```typescript
type MaybeString = string | null | undefined;
type DefinitelyString = NonNullable<MaybeString>; // string
```

### 5.7.10 ReturnType

`ReturnType<T>`获取函数类型`T`的返回类型。

```typescript
function createUser(): User {
    return { id: 1, name: "Alice", email: "alice@example.com", age: 30 };
}

type CreateUserReturn = ReturnType<typeof createUser>; // User
```

### 5.7.11 InstanceType

`InstanceType<T>`获取构造函数类型`T`的实例类型。

```typescript
class UserClass {
    constructor(public name: string, public age: number) {}
}

type UserInstance = InstanceType<typeof UserClass>; // UserClass

const user = new UserClass("Alice", 30); // UserInstance
```

## 5.8 高级类型模式

### 5.8.1 类型递归

TypeScript支持递归类型，用于定义自引用的类型结构。

```typescript
// 递归类型定义JSON值
type JSONValue = 
    | string
    | number
    | boolean
    | null
    | JSONValue[]
    | { [key: string]: JSONValue };

// 递归类型定义树节点
interface TreeNode<T> {
    value: T;
    children?: TreeNode<T>[];
}

// 递归类型定义链表节点
interface ListNode<T> {
    value: T;
    next: ListNode<T> | null;
}
```

### 5.8.2 品牌类型（Branded Types）

品牌类型是一种创建名义类型的技术，通过添加唯一标识符使类型不同，即使底层类型相同。

```typescript
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
// const same: UserId = productId; // 错误：ProductId不能赋值给UserId

// 品牌类型与类型守卫
function isUserId(value: string): value is UserId {
    return value.startsWith("user");
}

function processId(id: string) {
    if (isUserId(id)) {
        // 这里TypeScript知道id是UserId类型
        console.log("Processing user ID");
    } else {
        console.log("Processing generic ID");
    }
}
```

### 5.8.3 不透明类型（Opaque Types）

不透明类型与品牌类型类似，但用于创建完全抽象的类型。

```typescript
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
```

## 5.9 实例：构建类型安全的状态管理系统

让我们通过一个实际例子来应用高级类型特性：

```typescript
// 基础类型定义
interface State {
    user: UserState;
    products: ProductState;
    ui: UIState;
}

interface UserState {
    currentUser: User | null;
    isLoading: boolean;
    error: string | null;
}

interface ProductState {
    items: Product[];
    filter: string;
    isLoading: boolean;
}

interface UIState {
    sidebarOpen: boolean;
    theme: "light" | "dark";
    notifications: Notification[];
}

// 定义动作类型
interface BaseAction {
    type: string;
}

interface UserAction extends BaseAction {
    type: "USER_LOGIN_REQUEST" | "USER_LOGIN_SUCCESS" | "USER_LOGIN_ERROR" | "USER_LOGOUT";
    payload?: User | string;
}

interface ProductAction extends BaseAction {
    type: "PRODUCT_FETCH_REQUEST" | "PRODUCT_FETCH_SUCCESS" | "PRODUCT_FILTER_CHANGE";
    payload?: Product[] | string;
}

interface UIAction extends BaseAction {
    type: "UI_TOGGLE_SIDEBAR" | "UI_SET_THEME" | "UI_ADD_NOTIFICATION";
    payload?: "light" | "dark" | Notification;
}

type AppAction = UserAction | ProductAction | UIAction;

// 创建动作工厂函数
type ActionFactory<T extends string, P = undefined> = P extends undefined
    ? { type: T }
    : { type: T; payload: P };

const userActions = {
    loginRequest: (): ActionFactory<"USER_LOGIN_REQUEST"> => ({ type: "USER_LOGIN_REQUEST" }),
    loginSuccess: (user: User): ActionFactory<"USER_LOGIN_SUCCESS", User> => ({
        type: "USER_LOGIN_SUCCESS",
        payload: user
    }),
    loginError: (error: string): ActionFactory<"USER_LOGIN_ERROR", string> => ({
        type: "USER_LOGIN_ERROR",
        payload: error
    }),
    logout: (): ActionFactory<"USER_LOGOUT"> => ({ type: "USER_LOGOUT" })
};

// 定义Reducer类型
type Reducer<S, A extends BaseAction> = (
    state: S,
    action: A
) => S;

// 创建类型安全的reducer
function createUserReducer(): Reducer<UserState, UserAction> {
    const initialState: UserState = {
        currentUser: null,
        isLoading: false,
        error: null
    };
    
    return (state = initialState, action): UserState => {
        switch (action.type) {
            case "USER_LOGIN_REQUEST":
                return {
                    ...state,
                    isLoading: true,
                    error: null
                };
            
            case "USER_LOGIN_SUCCESS":
                return {
                    ...state,
                    currentUser: action.payload as User,
                    isLoading: false,
                    error: null
                };
            
            case "USER_LOGIN_ERROR":
                return {
                    ...state,
                    currentUser: null,
                    isLoading: false,
                    error: action.payload as string
                };
            
            case "USER_LOGOUT":
                return {
                    ...state,
                    currentUser: null,
                    isLoading: false,
                    error: null
                };
            
            default:
                // 确保所有动作都被处理
                const _exhaustiveCheck: never = action;
                return state;
        }
    };
}

// 创建选择器类型
type Selector<S, R> = (state: S) => R;

// 创建类型安全的选择器
const userSelectors = {
    getCurrentUser: (state: State): State["user"]["currentUser"] => state.user.currentUser,
    isLoggedIn: (state: State): boolean => state.user.currentUser !== null,
    isLoading: (state: State): boolean => state.user.isLoading,
    getError: (state: State): State["user"]["error"] => state.user.error
};

// 创建异步动作类型
type AsyncAction<T, P = any> = {
    type: T;
    payload?: P;
    meta: {
        async: boolean;
    };
};

// 创建类型安全的中间件
function createAsyncMiddleware<S, A extends BaseAction>() {
    return (store: {
        dispatch: (action: A) => void;
        getState: () => S;
    }) => (next: (action: A) => void) => (action: A) => {
        // 检查是否是异步动作
        if ("meta" in action && action.meta && action.meta.async) {
            // 处理异步动作
            console.log("Async action detected:", action);
        }
        
        return next(action);
    };
}

// 创建类型安全的Store类
class Store<S, A extends BaseAction> {
    private state: S;
    private reducers: Array<Reducer<S, A>> = [];
    private middlewares: Array<(store: Store<S, A>) => (next: (action: A) => void) => (action: A) => void> = [];
    private listeners: Array<(state: S) => void> = [];
    
    constructor(
        initialState: S,
        reducers: Array<Reducer<S, A>>,
        middlewares?: Array<(store: Store<S, A>) => (next: (action: A) => void) => (action: A) => void>
    ) {
        this.state = initialState;
        this.reducers = reducers;
        
        if (middlewares) {
            this.middlewares = middlewares;
        }
    }
    
    getState(): S {
        return this.state;
    }
    
    dispatch(action: A): void {
        // 应用中间件
        let dispatch: (action: A) => void = (action) => {
            // 应用所有reducer
            this.state = this.reducers.reduce(
                (currentState, reducer) => reducer(currentState, action),
                this.state
            );
            
            // 通知所有监听器
            this.listeners.forEach(listener => listener(this.state));
        };
        
        // 应用中间件链
        this.middlewares.forEach(middleware => {
            const middlewareDispatch = middleware(this);
            dispatch = middlewareDispatch(dispatch);
        });
        
        // 执行动作
        dispatch(action);
    }
    
    subscribe(listener: (state: S) => void): () => void {
        this.listeners.push(listener);
        
        return () => {
            const index = this.listeners.indexOf(listener);
            if (index >= 0) {
                this.listeners.splice(index, 1);
            }
        };
    }
    
    // 创建类型选择器
    createSelector<R>(selector: Selector<S, R>): () => R {
        return () => selector(this.state);
    }
}

// 使用示例
function createStateManagementDemo(): void {
    // 初始状态
    const initialState: State = {
        user: {
            currentUser: null,
            isLoading: false,
            error: null
        },
        products: {
            items: [],
            filter: "",
            isLoading: false
        },
        ui: {
            sidebarOpen: false,
            theme: "light",
            notifications: []
        }
    };
    
    // 创建store
    const store = new Store(
        initialState,
        [createUserReducer()],
        [createAsyncMiddleware()]
    );
    
    // 创建选择器
    const selectCurrentUser = store.createSelector(userSelectors.getCurrentUser);
    const selectIsLoggedIn = store.createSelector(userSelectors.isLoggedIn);
    const selectIsLoading = store.createSelector(userSelectors.isLoading);
    
    // 订阅状态变化
    const unsubscribe = store.subscribe((state) => {
        console.log("State updated:", state);
    });
    
    // 派发动作
    store.dispatch(userActions.loginRequest());
    store.dispatch(userActions.loginSuccess({ 
        id: 1, 
        name: "Alice", 
        email: "alice@example.com",
        age: 30 
    }));
    
    // 使用选择器
    console.log("Current user:", selectCurrentUser());
    console.log("Is logged in:", selectIsLoggedIn());
    console.log("Is loading:", selectIsLoading());
    
    // 取消订阅
    unsubscribe();
}

createStateManagementDemo();
```

## 5.10 最佳实践

### 5.10.1 类型设计原则

1. **优先使用组合而非继承**：使用联合类型和交叉类型构建复杂类型
2. **保持类型简单**：避免过度复杂的类型定义
3. **使用类型守卫**：通过运行时检查缩小类型范围
4. **利用工具类型**：重用内置工具类型而非重新实现

### 5.10.2 条件类型使用指南

1. **避免过度嵌套**：深层嵌套的条件类型难以理解和维护
2. **使用infer提取类型**：利用infer关键字提取泛型中的类型信息
3. **提供默认情况**：始终为条件类型提供默认分支

### 5.10.3 映射类型使用指南

1. **保持映射逻辑简单**：避免在映射类型中使用复杂逻辑
2. **使用as重映射**：利用as关键字重映射键名
3. **组合使用映射类型**：通过组合多个映射类型创建复杂转换

## 5.11 总结

在这一章中，我们深入学习了TypeScript的高级类型系统：

- 掌握了联合类型和交叉类型的使用
- 理解了条件类型、映射类型和模板字面量类型
- 探索了索引访问类型和工具类型
- 学习了高级类型模式如品牌类型和递归类型
- 构建了一个类型安全的状态管理系统

高级类型是TypeScript的强大特性，掌握它们将帮助您编写更加类型安全、灵活和可维护的代码。

## 5.12 练习

1. 创建一个类型安全的表单验证系统，使用高级类型定义验证规则
2. 实现一个类型安全的路由系统，支持动态路由参数
3. 构建一个类型安全的事件系统，使用可辨识联合类型处理不同事件
4. 创建一个类型安全的配置管理器，使用映射类型和条件类型处理配置选项

通过完成这些练习，您将加深对TypeScript高级类型的理解，并能够将其应用到实际项目中。