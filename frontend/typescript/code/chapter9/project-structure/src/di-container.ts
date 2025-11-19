// 依赖注入容器

import { Logger } from './interfaces/logger.interface';
import { Database } from './interfaces/database.interface';
import { ConsoleLogger } from './implementations/console-logger';
import { MemoryDatabase } from './implementations/memory-database';
import { UserService } from './services/user-service';

/**
 * 服务实例类型
 */
type ServiceInstance = any;

/**
 * 服务工厂函数类型
 */
type ServiceFactory<T> = (container: DIContainer) => T;

/**
 * 依赖注入容器
 * 负责管理服务的注册和解析
 */
export class DIContainer {
    private services: Map<string, ServiceInstance> = new Map();
    private factories: Map<string, ServiceFactory<any>> = new Map();
    private singletons: Map<string, boolean> = new Map();
    
    /**
     * 注册服务实例
     * @param name 服务名称
     * @param instance 服务实例
     * @param isSingleton 是否为单例
     */
    registerInstance<T>(name: string, instance: T, isSingleton = true): void {
        this.services.set(name, instance);
        this.singletons.set(name, isSingleton);
    }
    
    /**
     * 注册服务类
     * @param name 服务名称
     * @param ServiceClass 服务类
     * @param isSingleton 是否为单例
     */
    registerClass<T>(name: string, ServiceClass: new (...args: any[]) => T, isSingleton = true): void {
        this.registerFactory(name, () => new ServiceClass(), isSingleton);
    }
    
    /**
     * 注册服务工厂
     * @param name 服务名称
     * @param factory 工厂函数
     * @param isSingleton 是否为单例
     */
    registerFactory<T>(name: string, factory: ServiceFactory<T>, isSingleton = true): void {
        this.factories.set(name, factory);
        this.singletons.set(name, isSingleton);
    }
    
    /**
     * 解析服务
     * @param name 服务名称
     * @returns 服务实例
     */
    resolve<T>(name: string): T {
        // 检查是否已经解析过单例
        if (this.singletons.get(name) && this.services.has(name)) {
            return this.services.get(name) as T;
        }
        
        // 检查是否有工厂函数
        const factory = this.factories.get(name);
        if (!factory) {
            throw new Error(`Service ${name} not registered`);
        }
        
        // 创建实例
        const instance = factory(this);
        
        // 如果是单例，缓存实例
        if (this.singletons.get(name)) {
            this.services.set(name, instance);
        }
        
        return instance;
    }
    
    /**
     * 尝试解析服务
     * @param name 服务名称
     * @returns 服务实例或null
     */
    tryResolve<T>(name: string): T | null {
        try {
            return this.resolve<T>(name);
        } catch {
            return null;
        }
    }
    
    /**
     * 检查服务是否已注册
     * @param name 服务名称
     * @returns 是否已注册
     */
    isRegistered(name: string): boolean {
        return this.factories.has(name) || this.services.has(name);
    }
    
    /**
     * 移除服务注册
     * @param name 服务名称
     */
    unregister(name: string): void {
        this.services.delete(name);
        this.factories.delete(name);
        this.singletons.delete(name);
    }
    
    /**
     * 清空所有注册
     */
    clear(): void {
        this.services.clear();
        this.factories.clear();
        this.singletons.clear();
    }
    
    /**
     * 获取已注册的服务名称
     * @returns 服务名称数组
     */
    getRegisteredNames(): string[] {
        const names = new Set<string>();
        
        for (const name of this.services.keys()) {
            names.add(name);
        }
        
        for (const name of this.factories.keys()) {
            names.add(name);
        }
        
        return Array.from(names);
    }
}

/**
 * 创建预配置的容器
 * @returns 配置好的容器
 */
export function createContainer(): DIContainer {
    const container = new DIContainer();
    
    // 注册基础服务
    container.registerClass('logger', ConsoleLogger);
    container.registerFactory('database', () => new MemoryDatabase());
    
    // 注册业务服务
    container.registerFactory(
        'userService', 
        (container) => new UserService(
            container.resolve<Database>('database'),
            container.resolve<Logger>('logger')
        )
    );
    
    return container;
}