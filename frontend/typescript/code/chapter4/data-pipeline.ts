// 类型安全的数据处理管道示例
function demonstrateDataPipeline(): void {
    console.log("\n=== Data Pipeline Demo ===");
    
    // 定义管道操作的基本类型
    type PipeOperation<T, R> = (input: T) => R;
    
    // 基本管道操作函数
    class Pipeline<T> {
        constructor(private value: T) {}
        
        pipe<U>(operation: PipeOperation<T, U>): Pipeline<U> {
            return new Pipeline(operation(this.value));
        }
        
        getResult(): T {
            return this.value;
        }
    }
    
    // 常用管道操作
    const operations = {
        // 数据过滤
        filter: <T>(predicate: (item: T) => boolean) => 
            (data: T[]): T[] => data.filter(predicate),
        
        // 数据映射
        map: <T, U>(transform: (item: T) => U) => 
            (data: T[]): U[] => data.map(transform),
        
        // 数据扁平化
        flat: <T>(data: T[][]): T[] => data.flat(),
        
        // 数据排序
        sort: <T>(compareFn?: (a: T, b: T) => number) => 
            (data: T[]): T[] => [...data].sort(compareFn),
        
        // 数据分组
        groupBy: <T, K extends keyof T>(key: K) => 
            (data: T[]): Record<string, T[]> => 
                data.reduce((groups, item) => {
                    const groupKey = String(item[key]);
                    if (!groups[groupKey]) groups[groupKey] = [];
                    groups[groupKey].push(item);
                    return groups;
                }, {} as Record<string, T[]>),
        
        // 数据聚合
        reduce: <T, U>(reducer: (acc: U, item: T) => U, initialValue: U) => 
            (data: T[]): U => data.reduce(reducer, initialValue),
        
        // 数据统计
        count: <T>(data: T[]): number => data.length,
        
        // 数据求和
        sum: (data: number[]): number => data.reduce((sum, num) => sum + num, 0),
        
        // 取平均值
        average: (data: number[]): number => {
            if (data.length === 0) return 0;
            return data.reduce((sum, num) => sum + num, 0) / data.length;
        },
        
        // 获取最大值
        max: <T>(data: T[]): T | undefined => {
            if (data.length === 0) return undefined;
            return data.reduce((max, item) => (item > max ? item : max), data[0]);
        },
        
        // 获取最小值
        min: <T>(data: T[]): T | undefined => {
            if (data.length === 0) return undefined;
            return data.reduce((min, item) => (item < min ? item : min), data[0]);
        }
    };
    
    // 数据类型定义
    interface Product {
        id: number;
        name: string;
        price: number;
        category: string;
        inStock: boolean;
    }
    
    interface SalesData {
        productId: number;
        quantity: number;
        date: Date;
        amount: number;
    }
    
    // 示例数据
    const products: Product[] = [
        { id: 1, name: "Laptop", price: 999, category: "Electronics", inStock: true },
        { id: 2, name: "Smartphone", price: 699, category: "Electronics", inStock: true },
        { id: 3, name: "Headphones", price: 99, category: "Electronics", inStock: false },
        { id: 4, name: "Book", price: 19, category: "Books", inStock: true },
        { id: 5, name: "Shirt", price: 29, category: "Clothing", inStock: true },
        { id: 6, name: "Jeans", price: 49, category: "Clothing", inStock: false }
    ];
    
    const salesData: SalesData[] = [
        { productId: 1, quantity: 2, date: new Date("2023-01-15"), amount: 1998 },
        { productId: 2, quantity: 3, date: new Date("2023-01-16"), amount: 2097 },
        { productId: 4, quantity: 5, date: new Date("2023-01-17"), amount: 95 },
        { productId: 5, quantity: 10, date: new Date("2023-01-18"), amount: 290 },
        { productId: 1, quantity: 1, date: new Date("2023-01-19"), amount: 999 }
    ];
    
    // 使用管道处理产品数据
    const expensiveProducts = new Pipeline(products)
        .pipe(operations.filter(p => p.price > 50))
        .pipe(operations.sort((a, b) => b.price - a.price))
        .pipe(operations.map(p => `${p.name}: $${p.price}`))
        .getResult();
    
    console.log("Expensive products:", expensiveProducts);
    
    // 使用管道统计各分类的产品数量
    const productsByCategory = new Pipeline(products)
        .pipe(operations.groupBy("category"))
        .pipe(operations.map((groups: Record<string, Product[]>, key: string) => ({
            category: key,
            count: groups[key].length
        })))
        .pipe(operations.sort((a, b) => b.count - a.count))
        .getResult();
    
    console.log("Products by category:", productsByCategory);
    
    // 使用管道计算销售数据统计
    const salesStats = new Pipeline(salesData)
        .pipe(operations.map(s => s.amount))
        .pipe(data => ({
            total: operations.sum(data),
            average: operations.average(data),
            max: operations.max(data),
            min: operations.min(data),
            count: operations.count(data)
        }))
        .getResult();
    
    console.log("Sales statistics:", salesStats);
    
    // 组合多个管道操作
    const highValueSales = new Pipeline(salesData)
        .pipe(operations.filter(s => s.amount > 1000))
        .pipe(operations.map(s => ({
            productId: s.productId,
            amount: s.amount,
            date: s.date.toISOString().split('T')[0]
        })))
        .pipe(operations.sort((a, b) => b.amount - a.amount))
        .getResult();
    
    console.log("High value sales:", highValueSales);
    
    // 扩展管道支持更多操作
    const advancedOperations = {
        // 连接操作
        join: <T>(separator: string) => (data: T[]): string => data.join(separator),
        
        // 获取唯一值
        unique: <T>(data: T[]): T[] => [...new Set(data)],
        
        // 分块操作
        chunk: <T>(size: number) => (data: T[]): T[][] => {
            const chunks: T[][] = [];
            for (let i = 0; i < data.length; i += size) {
                chunks.push(data.slice(i, i + size));
            }
            return chunks;
        },
        
        // 获取前N个元素
        take: <T>(count: number) => (data: T[]): T[] => data.slice(0, count),
        
        // 跳过前N个元素
        skip: <T>(count: number) => (data: T[]): T[] => data.slice(count),
        
        // 查找匹配条件的第一个元素
        find: <T>(predicate: (item: T) => boolean) => (data: T[]): T | undefined => 
            data.find(predicate),
        
        // 检查是否所有元素满足条件
        every: <T>(predicate: (item: T) => boolean) => (data: T[]): boolean => 
            data.every(predicate),
        
        // 检查是否有元素满足条件
        some: <T>(predicate: (item: T) => boolean) => (data: T[]): boolean => 
            data.some(predicate)
    };
    
    // 使用高级操作
    const productNames = new Pipeline(products)
        .pipe(operations.map(p => p.name))
        .pipe(advancedOperations.unique)
        .pipe(advancedOperations.join(", "))
        .getResult();
    
    console.log("Product names:", productNames);
    
    const productChunks = new Pipeline(products)
        .pipe(advancedOperations.chunk(2))
        .getResult();
    
    console.log("Product chunks:", productChunks);
    
    // 创建可重用的管道函数
    const createProductPipeline = (products: Product[]) => {
        return {
            getExpensive: (priceThreshold: number = 50) => 
                new Pipeline(products)
                    .pipe(operations.filter(p => p.price > priceThreshold))
                    .pipe(operations.sort((a, b) => b.price - a.price))
                    .getResult(),
            
            getByCategory: (category: string) => 
                new Pipeline(products)
                    .pipe(operations.filter(p => p.category === category))
                    .pipe(operations.sort((a, b) => a.name.localeCompare(b.name)))
                    .getResult(),
            
            getInStock: () => 
                new Pipeline(products)
                    .pipe(operations.filter(p => p.inStock))
                    .getResult(),
            
            getStatistics: () => 
                new Pipeline(products)
                    .pipe(data => ({
                        total: data.length,
                        inStock: data.filter(p => p.inStock).length,
                        outOfStock: data.filter(p => !p.inStock).length,
                        categories: [...new Set(data.map(p => p.category))].length,
                        averagePrice: data.reduce((sum, p) => sum + p.price, 0) / data.length,
                        maxPrice: Math.max(...data.map(p => p.price)),
                        minPrice: Math.min(...data.map(p => p.price))
                    }))
                    .getResult()
        };
    };
    
    const productPipeline = createProductPipeline(products);
    
    console.log("Expensive products:", productPipeline.getExpensive(100));
    console.log("Electronics products:", productPipeline.getByCategory("Electronics"));
    console.log("Products in stock:", productPipeline.getInStock());
    console.log("Product statistics:", productPipeline.getStatistics());
    
    console.log("Data pipeline demo completed!");
}

demonstrateDataPipeline();