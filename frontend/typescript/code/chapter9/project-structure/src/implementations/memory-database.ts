// 内存数据库实现

import { Database, QueryOptions } from '../interfaces/database.interface';

/**
 * 内存数据库实现类
 * 用于开发和测试环境
 */
export class MemoryDatabase implements Database {
    private collections: Map<string, any[]> = new Map();
    
    /**
     * 构造函数
     * @param initialData 初始数据（可选）
     */
    constructor(initialData?: Record<string, any[]>) {
        if (initialData) {
            for (const [collection, data] of Object.entries(initialData)) {
                this.collections.set(collection, [...data]);
            }
        }
    }
    
    /**
     * 获取集合，如果不存在则创建
     * @param collection 集合名称
     * @returns 集合数组
     */
    private getCollection(collection: string): any[] {
        if (!this.collections.has(collection)) {
            this.collections.set(collection, []);
        }
        return this.collections.get(collection)!;
    }
    
    /**
     * 创建查询过滤函数
     * @param query 查询条件
     * @returns 过滤函数
     */
    private createFilter(query: Record<string, any>): (item: any) => boolean {
        return (item) => {
            for (const [key, value] of Object.entries(query)) {
                if (item[key] !== value) {
                    return false;
                }
            }
            return true;
        };
    }
    
    /**
     * 创建排序函数
     * @param sort 排序条件
     * @returns 排序函数
     */
    private createSorter(sort: Record<string, 1 | -1>): (a: any, b: any) => number {
        return (a, b) => {
            for (const [key, direction] of Object.entries(sort)) {
                if (a[key] < b[key]) return -1 * direction;
                if (a[key] > b[key]) return 1 * direction;
            }
            return 0;
        };
    }
    
    /**
     * 查找单个文档
     * @param collection 集合名称
     * @param query 查询条件
     * @returns 查找结果或null
     */
    async findOne<T>(collection: string, query: Record<string, any>): Promise<T | null> {
        const coll = this.getCollection(collection);
        const filter = this.createFilter(query);
        
        const result = coll.find(filter);
        return result ? { ...result } : null;
    }
    
    /**
     * 查找多个文档
     * @param collection 集合名称
     * @param query 查询条件
     * @param options 查询选项
     * @returns 查找结果数组
     */
    async findMany<T>(
        collection: string, 
        query: Record<string, any>, 
        options?: QueryOptions
    ): Promise<T[]> {
        const coll = this.getCollection(collection);
        const filter = this.createFilter(query);
        
        let results = coll.filter(filter);
        
        // 排序
        if (options?.sort) {
            results.sort(this.createSorter(options.sort));
        }
        
        // 分页
        if (options?.offset) {
            results = results.slice(options.offset);
        }
        
        if (options?.limit) {
            results = results.slice(0, options.limit);
        }
        
        return results.map(item => ({ ...item }));
    }
    
    /**
     * 插入文档
     * @param collection 集合名称
     * @param document 文档数据
     * @returns 插入的文档
     */
    async insert<T>(collection: string, document: T): Promise<T> {
        const coll = this.getCollection(collection);
        
        // 确保文档有id
        if (!('id' in document)) {
            (document as any).id = this.generateId();
        }
        
        coll.push({ ...document });
        return { ...document };
    }
    
    /**
     * 更新文档
     * @param collection 集合名称
     * @param query 查询条件
     * @param update 更新数据
     * @returns 是否成功更新
     */
    async update(
        collection: string, 
        query: Record<string, any>, 
        update: Record<string, any>
    ): Promise<boolean> {
        const coll = this.getCollection(collection);
        const filter = this.createFilter(query);
        
        let updated = false;
        
        for (let i = 0; i < coll.length; i++) {
            if (filter(coll[i])) {
                coll[i] = { ...coll[i], ...update };
                updated = true;
                break; // 只更新第一个匹配的文档
            }
        }
        
        return updated;
    }
    
    /**
     * 删除文档
     * @param collection 集合名称
     * @param query 查询条件
     * @returns 是否成功删除
     */
    async delete(collection: string, query: Record<string, any>): Promise<boolean> {
        const coll = this.getCollection(collection);
        const filter = this.createFilter(query);
        
        const initialLength = coll.length;
        
        for (let i = coll.length - 1; i >= 0; i--) {
            if (filter(coll[i])) {
                coll.splice(i, 1);
                break; // 只删除第一个匹配的文档
            }
        }
        
        return coll.length < initialLength;
    }
    
    /**
     * 执行自定义查询
     * @param query 查询语句或参数
     * @returns 查询结果
     */
    async executeQuery<T>(query: any): Promise<T> {
        // 对于内存数据库，这个方法可以执行更复杂的查询
        // 这里只是一个简单的示例实现
        if (typeof query === 'function') {
            return query(this.collections);
        }
        
        throw new Error('Unsupported query type');
    }
    
    /**
     * 清空所有集合或指定集合
     * @param collection 集合名称（可选）
     */
    clear(collection?: string): void {
        if (collection) {
            this.collections.set(collection, []);
        } else {
            this.collections.clear();
        }
    }
    
    /**
     * 获取所有集合名称
     * @returns 集合名称数组
     */
    getCollectionNames(): string[] {
        return Array.from(this.collections.keys());
    }
    
    /**
     * 生成随机ID
     * @returns 随机ID
     */
    private generateId(): string {
        return Math.random().toString(36).substring(2, 9);
    }
}