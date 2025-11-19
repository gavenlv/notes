// 数据库接口

/**
 * 查询选项
 */
export interface QueryOptions {
    limit?: number;
    offset?: number;
    sort?: Record<string, 1 | -1>;
}

/**
 * 数据库接口
 * 定义了基本的数据库操作
 */
export interface Database {
    /**
     * 查找单个文档
     * @param collection 集合名称
     * @param query 查询条件
     * @returns 查找结果或null
     */
    findOne<T>(collection: string, query: Record<string, any>): Promise<T | null>;
    
    /**
     * 查找多个文档
     * @param collection 集合名称
     * @param query 查询条件
     * @param options 查询选项
     * @returns 查找结果数组
     */
    findMany<T>(
        collection: string, 
        query: Record<string, any>, 
        options?: QueryOptions
    ): Promise<T[]>;
    
    /**
     * 插入文档
     * @param collection 集合名称
     * @param document 文档数据
     * @returns 插入的文档
     */
    insert<T>(collection: string, document: T): Promise<T>;
    
    /**
     * 更新文档
     * @param collection 集合名称
     * @param query 查询条件
     * @param update 更新数据
     * @returns 是否成功更新
     */
    update(
        collection: string, 
        query: Record<string, any>, 
        update: Record<string, any>
    ): Promise<boolean>;
    
    /**
     * 删除文档
     * @param collection 集合名称
     * @param query 查询条件
     * @returns 是否成功删除
     */
    delete(collection: string, query: Record<string, any>): Promise<boolean>;
    
    /**
     * 执行自定义查询
     * @param query 查询语句或参数
     * @returns 查询结果
     */
    executeQuery<T>(query: any): Promise<T>;
}