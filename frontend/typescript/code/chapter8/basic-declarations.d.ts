// 基本声明文件示例

// 声明一个全局变量
declare const APP_VERSION: string;
declare const API_BASE_URL: string;

// 声明全局函数
declare function logMessage(level: string, message: string, ...args: any[]): void;
declare function formatDate(date: Date): string;

// 声明全局接口
declare interface User {
    id: number;
    name: string;
    email: string;
    role: 'admin' | 'user' | 'guest';
    createdAt: Date;
    updatedAt: Date;
}

// 声明全局类型
declare type Status = 'active' | 'inactive' | 'pending';
declare type Permissions = string[];

// 声明全局类
declare class Storage {
    constructor(namespace?: string);
    getItem(key: string): string | null;
    setItem(key: string, value: string): void;
    removeItem(key: string): void;
    clear(): void;
}

// 模块声明
declare module 'my-library' {
    export function initialize(): void;
    export function process(data: any): any;
    export const version: string;
    export type Result = { success: boolean; data?: any; error?: string };
}

// 通配符模块声明
declare module '*.json' {
    const value: any;
    export default value;
}

declare module '*.css' {
    const classes: { [key: string]: string };
    export default classes;
}