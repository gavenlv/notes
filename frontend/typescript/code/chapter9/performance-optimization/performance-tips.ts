// TypeScript性能优化示例

/**
 * 1. 使用类型别名代替接口（对于简单类型）
 */

// 好 - 对于简单类型使用类型别名
type UserId = string;
type Status = 'active' | 'inactive' | 'pending';
type UserRoles = 'admin' | 'user' | 'guest';

// 避免 - 对于简单类型使用接口
// interface UserId extends String {}
// interface Status {}

/**
 * 2. 避免过度嵌套的泛型
 */

// 避免 - 过度使用泛型
// function processComplexData<T, U, V, W, X>(a: T, b: U, c: V, d: W, e: X): void {
//     // ...
// }

// 好 - 使用接口或类型别名组合相关参数
interface ProcessingData {
    input: any;
    options: ProcessingOptions;
    metadata?: Record<string, any>;
}

interface ProcessingOptions {
    strict?: boolean;
    timeout?: number;
    retries?: number;
}

function processData(data: ProcessingData): void {
    // 处理逻辑
}

/**
 * 3. 使用字面量类型而不是枚举（在某些情况下）
 */

// 好 - 使用常量对象
const UserRole = {
    ADMIN: 'admin' as const,
    USER: 'user' as const,
    GUEST: 'guest' as const
} as const;

type UserRole = typeof UserRole[keyof typeof UserRole];

// 或者直接使用字面量类型
type UserType = 'admin' | 'user' | 'guest';

// 避免 - 在不需要的情况下使用枚举
// enum UserRole {
//     ADMIN = 'admin',
//     USER = 'user',
//     GUEST = 'guest'
// }

/**
 * 4. 优化条件类型使用
 */

// 好 - 简单的条件类型
type NonNullable<T> = T extends null | undefined ? never : T;

// 避免 - 复杂嵌套的条件类型
// type ComplexType<T> = T extends string 
//     ? T extends `${infer Prefix}_${infer Suffix}` 
//         ? { prefix: Prefix; suffix: Suffix } 
//         : T 
//     : T extends number 
//         ? T extends 0 ? 'zero' : 'non-zero' 
//         : never;

/**
 * 5. 预先验证数据，避免在热路径中进行复杂类型检查
 */

// 好 - 预先验证，然后使用断言
function processItems(items: unknown[]): Item[] {
    // 一次性验证所有项目
    if (!items.every(isItem)) {
        throw new Error('All items must be valid Item instances');
    }
    
    // 现在可以安全使用items作为Item[]
    return items as Item[];
}

// 避免 - 在循环中重复检查
// function processItems(items: unknown[]): Item[] {
//     return items.map(item => {
//         if (isItem(item)) {
//             return transformItem(item);
//         } else {
//             throw new Error('Invalid item');
//         }
//     });
// }

// 类型守卫函数
function isItem(value: unknown): value is Item {
    return (
        value !== null &&
        typeof value === 'object' &&
        'id' in value &&
        'name' in value &&
        typeof (value as any).id === 'string' &&
        typeof (value as any).name === 'string'
    );
}

interface Item {
    id: string;
    name: string;
}

function transformItem(item: Item): Item {
    // 转换逻辑
    return item;
}

/**
 * 6. 使用索引签名而不是映射类型（对于动态对象）
 */

// 好 - 对于动态对象使用索引签名
interface DynamicData {
    [key: string]: unknown;
}

function processDynamicData(data: DynamicData): void {
    // 处理逻辑
}

// 避免 - 对于完全动态的对象使用映射类型
// type DynamicData = { [K in string]: unknown };

/**
 * 7. 使用函数重载而不是复杂的联合类型
 */

// 好 - 使用函数重载
function formatValue(value: string): string;
function formatValue(value: number): string;
function formatValue(value: boolean): string;
function formatValue(value: Date): string;
function formatValue(value: string | number | boolean | Date): string {
    if (typeof value === 'string') {
        return value.trim();
    } else if (typeof value === 'number') {
        return value.toFixed(2);
    } else if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
    } else if (value instanceof Date) {
        return value.toISOString();
    }
    return String(value);
}

// 避免 - 复杂的函数内部类型判断
// function formatValue(value: string | number | boolean | Date): string {
//     if (typeof value === 'string') {
//         return value.trim();
//     } else if (typeof value === 'number') {
//         return value.toFixed(2);
//     } else if (typeof value === 'boolean') {
//         return value ? 'Yes' : 'No';
//     } else if (value instanceof Date) {
//         return value.toISOString();
//     }
//     return String(value);
// }

/**
 * 8. 使用类型断言而不是类型守卫（在性能关键路径）
 */

// 好 - 在性能关键路径使用断言（前提是确保类型安全）
function processArrayItems(items: unknown[]): void {
    // 如果已经确保所有元素都是Item类型
    const itemArray = items as Item[];
    
    for (const item of itemArray) {
        // 直接访问属性，无需检查
        console.log(item.id, item.name);
    }
}

// 避免 - 在性能关键路径使用守卫
// function processArrayItems(items: unknown[]): void {
//     for (const item of items) {
//         if (isItem(item)) {
//             console.log(item.id, item.name);
//         }
//     }
// }

/**
 * 9. 使用ReadOnlyArray代替Array（对于只读数据）
 */

// 好 - 对于只读数据使用只读数组
function processReadOnlyData(data: ReadonlyArray<Item>): void {
    // data[0] = newItem; // 编译错误
    // data.push(newItem); // 编译错误
    
    // 可以读取数据
    const firstItem = data[0];
    console.log(firstItem?.name);
}

// 避免 - 对于只读数据使用普通数组
// function processReadOnlyData(data: Item[]): void {
//     // data[0] = newItem; // 可能导致意外的修改
//     // data.push(newItem); // 可能导致意外的修改
// }

/**
 * 10. 使用Partial<T>代替可选属性（对于更新操作）
 */

// 好 - 对于更新操作使用Partial
function updateUser(id: string, updates: Partial<User>): User {
    const existingUser = findUserById(id);
    if (!existingUser) {
        throw new Error(`User with id ${id} not found`);
    }
    
    return { ...existingUser, ...updates, updatedAt: new Date() };
}

// 避免 - 定义专门的部分更新接口
// interface UserUpdate {
//     name?: string;
//     email?: string;
//     role?: UserRole;
// }

interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
    createdAt: Date;
    updatedAt: Date;
}

function findUserById(id: string): User | null {
    // 实现查找逻辑
    return null;
}

export {
    UserRole,
    UserType,
    Item,
    User,
    ProcessingData,
    ProcessingOptions,
    processData,
    processItems,
    formatValue,
    processArrayItems,
    processReadOnlyData,
    updateUser
};