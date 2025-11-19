// 高级声明文件示例

// 声明合并示例
interface Box {
    height: number;
    width: number;
}

interface Box {
    scale: number;
}

// 类和接口声明合并
class Calculation {
    private result: number = 0;
}

interface Calculation {
    add(value: number): Calculation;
    subtract(value: number): Calculation;
    getResult(): number;
}

// 泛型声明
declare interface Repository<T, ID = string> {
    findById(id: ID): Promise<T | null>;
    save(entity: T): Promise<T>;
    update(id: ID, updateData: Partial<T>): Promise<T>;
    delete(id: ID): Promise<boolean>;
    findMany(options?: { limit?: number; offset?: number }): Promise<T[]>;
}

// 条件类型声明
declare function fetch<T>(url: string): T extends string 
    ? Promise<string> 
    : T extends object 
        ? Promise<T> 
        : Promise<any>;

// 映射类型
declare type DeepPartial<T> = {
    [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// 函数重载声明
declare function createElement(tag: string, props: any, ...children: any[]): any;
declare function createElement(tag: string, props: any): any;
declare function createElement(tag: string): any;

// 复杂的命名空间声明
declare namespace Database {
    interface ConnectionOptions {
        host: string;
        port: number;
        database: string;
        username: string;
        password: string;
        ssl?: boolean;
        pool?: {
            min: number;
            max: number;
        };
    }
    
    interface QueryResult<T = any> {
        rows: T[];
        rowCount: number;
        command: string;
    }
    
    class Connection {
        constructor(options: ConnectionOptions);
        connect(): Promise<void>;
        disconnect(): Promise<void>;
        query<T = any>(sql: string, params?: any[]): Promise<QueryResult<T>>;
        transaction<T>(callback: (connection: Connection) => Promise<T>): Promise<T>;
    }
    
    interface ORM {
        define<T>(name: string, schema: Record<keyof T, any>): Repository<T>;
        sync(): Promise<void>;
        drop(): Promise<void>;
    }
    
    function connect(options: ConnectionOptions): Promise<Connection>;
    function createORM(): ORM;
}

// 模块扩展
declare module "express" {
    interface Request {
        user?: {
            id: string;
            role: string;
            permissions: string[];
        };
        pagination?: {
            page: number;
            limit: number;
            offset: number;
        };
    }
    
    interface Response {
        success<T>(data: T): void;
        error(message: string, statusCode?: number): void;
    }
}

// 扩展全局对象
declare global {
    interface Window {
        gtag: (command: string, targetId: string, config?: any) => void;
        analytics: {
            track(event: string, properties?: Record<string, any>): void;
            identify(userId: string, traits?: Record<string, any>): void;
        };
        ENVIRONMENT: 'development' | 'staging' | 'production';
    }
    
    namespace NodeJS {
        interface ProcessEnv {
            NODE_ENV: 'development' | 'production' | 'test';
            API_HOST: string;
            API_KEY: string;
            DB_HOST: string;
            DB_PORT: string;
            DB_NAME: string;
            DB_USER: string;
            DB_PASSWORD: string;
        }
    }
}