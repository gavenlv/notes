// 模块化应用程序示例
// src/models/user.model.ts
export interface User {
    id: number;
    name: string;
    email: string;
    avatar?: string;
    createdAt: Date;
    updatedAt?: Date;
}

export interface UserDocument extends User {
    updatedAt: Date;
}

export interface CreateUserRequest {
    name: string;
    email: string;
    avatar?: string;
}

export interface UpdateUserRequest {
    name?: string;
    email?: string;
    avatar?: string;
}

export interface UserSearchParams {
    name?: string;
    email?: string;
    page?: number;
    limit?: number;
}

export interface PaginatedResult<T> {
    data: T[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
}

// src/repositories/base.repository.ts
export interface IRepository<T, ID> {
    create(entity: Omit<T, 'id" | "createdAt">): T;
    findById(id: ID): T | undefined;
    findAll(): T[];
    update(id: ID, updates: Partial<Omit<T, 'id" | "createdAt">>): T | undefined;
    delete(id: ID): boolean;
}

// src/repositories/user.repository.ts
import type { 
    User, 
    UserDocument, 
    CreateUserRequest, 
    UpdateUserRequest, 
    UserSearchParams, 
    PaginatedResult 
} from '../models/user.model';
import type { IRepository } from './base.repository';
import { Logger, LogLevel } from '../utils/logger';

export class UserRepository implements IRepository<UserDocument, number> {
    private users: UserDocument[] = [];
    private nextId = 1;
    
    constructor(private logger: Logger) {}
    
    create(userData: Omit<User, 'id" | "createdAt">): UserDocument {
        this.logger.debug(`Creating user with data:`, userData);
        
        const user: UserDocument = {
            id: this.nextId++,
            ...userData,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        
        this.users.push(user);
        this.logger.info(`User created with ID: ${user.id}`);
        
        return user;
    }
    
    findById(id: number): UserDocument | undefined {
        this.logger.debug(`Finding user with ID: ${id}`);
        return this.users.find(user => user.id === id);
    }
    
    findAll(): UserDocument[] {
        this.logger.debug("Finding all users");
        return [...this.users];
    }
    
    search(params: UserSearchParams): PaginatedResult<UserDocument> {
        this.logger.debug(`Searching users with params:`, params);
        
        let filteredUsers = this.users;
        
        // 按名称过滤
        if (params.name) {
            const name = params.name.toLowerCase();
            filteredUsers = filteredUsers.filter(user => 
                user.name.toLowerCase().includes(name)
            );
        }
        
        // 按邮箱过滤
        if (params.email) {
            const email = params.email.toLowerCase();
            filteredUsers = filteredUsers.filter(user => 
                user.email.toLowerCase().includes(email)
            );
        }
        
        // 分页
        const page = params.page || 1;
        const limit = params.limit || 10;
        const startIndex = (page - 1) * limit;
        const endIndex = startIndex + limit;
        const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
        
        const totalPages = Math.ceil(filteredUsers.length / limit);
        
        const result: PaginatedResult<UserDocument> = {
            data: paginatedUsers,
            total: filteredUsers.length,
            page,
            limit,
            totalPages
        };
        
        this.logger.debug(`Search result: ${result.data.length} of ${result.total} users (page ${page}/${result.totalPages})`);
        
        return result;
    }
    
    update(id: number, updates: UpdateUserRequest): UserDocument | undefined {
        this.logger.debug(`Updating user ${id} with:`, updates);
        
        const userIndex = this.users.findIndex(user => user.id === id);
        
        if (userIndex === -1) {
            this.logger.warn(`User with ID ${id} not found`);
            return undefined;
        }
        
        // 如果更新邮箱，检查邮箱是否已存在
        if (updates.email) {
            const existingUser = this.users.find(user => 
                user.email === updates.email && user.id !== id
            );
            
            if (existingUser) {
                throw new Error(`Email ${updates.email} already exists`);
            }
        }
        
        this.users[userIndex] = {
            ...this.users[userIndex],
            ...updates,
            updatedAt: new Date()
        };
        
        this.logger.info(`User updated with ID: ${id}`);
        return this.users[userIndex];
    }
    
    delete(id: number): boolean {
        this.logger.debug(`Deleting user with ID: ${id}`);
        
        const userIndex = this.users.findIndex(user => user.id === id);
        
        if (userIndex === -1) {
            this.logger.warn(`User with ID ${id} not found`);
            return false;
        }
        
        const deletedUser = this.users[userIndex];
        this.users.splice(userIndex, 1);
        
        this.logger.info(`User deleted with ID: ${id}:`, deletedUser);
        return true;
    }
    
    findByEmail(email: string): UserDocument | undefined {
        this.logger.debug(`Finding user by email: ${email}`);
        return this.users.find(user => user.email === email);
    }
    
    count(): number {
        this.logger.debug("Counting users");
        return this.users.length;
    }
}

// src/services/user.service.ts
import type { 
    User, 
    UserDocument, 
    CreateUserRequest, 
    UpdateUserRequest, 
    UserSearchParams, 
    PaginatedResult 
} from '../models/user.model';
import type { UserRepository } from '../repositories/user.repository';
import { Logger, LogLevel } from '../utils/logger';

export class UserService {
    constructor(
        private userRepository: UserRepository
    ) {}
    
    async create(userData: CreateUserRequest): Promise<UserDocument> {
        // 验证用户数据
        if (!userData.name || userData.name.trim().length === 0) {
            throw new Error("Name is required");
        }
        
        if (!userData.email || userData.email.trim().length === 0) {
            throw new Error("Email is required");
        }
        
        if (!this.isValidEmail(userData.email)) {
            throw new Error("Email format is invalid");
        }
        
        // 检查邮箱是否已存在
        const existingUser = this.userRepository.findByEmail(userData.email);
        if (existingUser) {
            throw new Error(`Email ${userData.email} already exists`);
        }
        
        return this.userRepository.create(userData);
    }
    
    async findById(id: number): Promise<UserDocument | undefined> {
        if (id <= 0) {
            throw new Error("User ID must be a positive number");
        }
        
        return this.userRepository.findById(id);
    }
    
    async findAll(): Promise<UserDocument[]> {
        return this.userRepository.findAll();
    }
    
    async search(params: UserSearchParams): Promise<PaginatedResult<UserDocument>> {
        // 验证搜索参数
        if (params.page && params.page < 1) {
            throw new Error("Page must be a positive number");
        }
        
        if (params.limit && params.limit < 1) {
            throw new Error("Limit must be a positive number");
        }
        
        if (params.limit && params.limit > 100) {
            throw new Error("Limit cannot exceed 100");
        }
        
        return this.userRepository.search(params);
    }
    
    async update(id: number, updates: UpdateUserRequest): Promise<UserDocument | undefined> {
        // 验证ID
        if (id <= 0) {
            throw new Error("User ID must be a positive number");
        }
        
        // 验证更新数据
        if (updates.name !== undefined) {
            if (!updates.name || updates.name.trim().length === 0) {
                throw new Error("Name cannot be empty");
            }
        }
        
        if (updates.email !== undefined) {
            if (!updates.email || updates.email.trim().length === 0) {
                throw new Error("Email cannot be empty");
            }
            
            if (!this.isValidEmail(updates.email)) {
                throw new Error("Email format is invalid");
            }
        }
        
        // 检查用户是否存在
        const user = await this.findById(id);
        if (!user) {
            throw new Error(`User with ID ${id} not found`);
        }
        
        return this.userRepository.update(id, updates);
    }
    
    async delete(id: number): Promise<boolean> {
        if (id <= 0) {
            throw new Error("User ID must be a positive number");
        }
        
        // 检查用户是否存在
        const user = await this.findById(id);
        if (!user) {
            throw new Error(`User with ID ${id} not found`);
        }
        
        return this.userRepository.delete(id);
    }
    
    async count(): Promise<number> {
        return this.userRepository.count();
    }
    
    private isValidEmail(email: string): boolean {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// src/controllers/user.controller.ts
import type { 
    UserDocument, 
    CreateUserRequest, 
    UpdateUserRequest, 
    UserSearchParams,
    PaginatedResult 
} from '../models/user.model';
import type { UserService } from '../services/user.service';
import { Logger, LogLevel } from '../utils/logger';

export interface IRequest {
    params: Record<string, string>;
    query: Record<string, string>;
    body: any;
    user?: any;
}

export interface IResponse {
    status(code: number): IResponse;
    json(data: any): void;
    send(data: any): void;
}

export class UserController {
    constructor(
        private userService: UserService,
        private logger: Logger
    ) {}
    
    async createUser(req: IRequest, res: IResponse): Promise<void> {
        try {
            const userData: CreateUserRequest = req.body;
            const user = await this.userService.create(userData);
            
            this.logger.info(`User created with ID: ${user.id}`);
            res.status(201).json(user);
        } catch (error) {
            this.logger.error(`Error creating user: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async getUserById(req: IRequest, res: IResponse): Promise<void> {
        try {
            const id = parseInt(req.params.id, 10);
            const user = await this.userService.findById(id);
            
            if (!user) {
                return res.status(404).json({ error: "User not found" });
            }
            
            res.json(user);
        } catch (error) {
            this.logger.error(`Error fetching user: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async getAllUsers(req: IRequest, res: IResponse): Promise<void> {
        try {
            const users = await this.userService.findAll();
            res.json(users);
        } catch (error) {
            this.logger.error(`Error fetching users: ${(error as Error).message}`);
            res.status(500).json({ error: "Internal server error" });
        }
    }
    
    async searchUsers(req: IRequest, res: IResponse): Promise<void> {
        try {
            const params: UserSearchParams = {
                name: req.query.name as string,
                email: req.query.email as string,
                page: req.query.page ? parseInt(req.query.page as string, 10) : undefined,
                limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined
            };
            
            const result = await this.userService.search(params);
            res.json(result);
        } catch (error) {
            this.logger.error(`Error searching users: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async updateUser(req: IRequest, res: IResponse): Promise<void> {
        try {
            const id = parseInt(req.params.id, 10);
            const updates: UpdateUserRequest = req.body;
            
            const user = await this.userService.update(id, updates);
            
            if (!user) {
                return res.status(404).json({ error: "User not found" });
            }
            
            this.logger.info(`User updated with ID: ${id}`);
            res.json(user);
        } catch (error) {
            this.logger.error(`Error updating user: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async deleteUser(req: IRequest, res: IResponse): Promise<void> {
        try {
            const id = parseInt(req.params.id, 10);
            const success = await this.userService.delete(id);
            
            if (!success) {
                return res.status(404).json({ error: "User not found" });
            }
            
            this.logger.info(`User deleted with ID: ${id}`);
            res.status(204).send();
        } catch (error) {
            this.logger.error(`Error deleting user: ${(error as Error).message}`);
            res.status(400).json({ error: (error as Error).message });
        }
    }
    
    async getUserCount(req: IRequest, res: IResponse): Promise<void> {
        try {
            const count = await this.userService.count();
            res.json({ count });
        } catch (error) {
            this.logger.error(`Error counting users: ${(error as Error).message}`);
            res.status(500).json({ error: "Internal server error" });
        }
    }
}

// src/middleware/auth.middleware.ts
import type { IRequest, IResponse } from '../controllers/user.controller';
import { Logger, LogLevel } from '../utils/logger';
import type { UserService } from '../services/user.service';

export function createAuthMiddleware(userService: UserService, logger: Logger) {
    return function authMiddleware(req: IRequest, res: IResponse, next: () => void): void {
        const token = req.headers.authorization;
        
        if (!token) {
            logger.warn("Missing authorization token");
            return res.status(401).json({ error: "Unauthorized: Missing token" });
        }
        
        // 简化的token验证，实际应用中会更复杂
        try {
            const userId = parseToken(token);
            
            if (!userId) {
                logger.warn("Invalid token");
                return res.status(401).json({ error: "Unauthorized: Invalid token" });
            }
            
            userService.findById(userId).then(user => {
                if (!user) {
                    logger.warn(`User not found for token: ${token}`);
                    return res.status(401).json({ error: "Unauthorized: User not found" });
                }
                
                req.user = user;
                logger.debug(`User authenticated: ${user.email}`);
                next();
            }).catch(error => {
                logger.error(`Error during authentication: ${(error as Error).message}`);
                res.status(500).json({ error: "Internal server error" });
            });
        } catch (error) {
            logger.error(`Error parsing token: ${(error as Error).message}`);
            res.status(401).json({ error: "Unauthorized: Invalid token format" });
        }
    };
    
    function parseToken(token: string): number | null {
        // 简化的token解析，实际应用中会使用JWT等
        if (token.startsWith("Bearer ")) {
            const tokenValue = token.substring(7);
            
            try {
                // 模拟从token中提取用户ID
                const payload = JSON.parse(atob(tokenValue));
                return payload.userId || null;
            } catch {
                return null;
            }
        }
        
        return null;
    }
}

// src/middleware/logging.middleware.ts
import type { IRequest, IResponse } from '../controllers/user.controller';
import { Logger, LogLevel } from '../utils/logger';

export function createLoggingMiddleware(logger: Logger) {
    return function loggingMiddleware(req: IRequest, res: IResponse, next: () => void): void {
        const { method, path } = req;
        const timestamp = new Date().toISOString();
        
        logger.info(`${timestamp} - ${method} ${path}`);
        
        // 记录响应状态
        const originalSend = res.send.bind(res);
        const originalJson = res.json.bind(res);
        
        res.send = function(data?: any): IResponse {
            logger.info(`${method} ${path} - ${res.statusCode}`);
            return originalSend(data);
        };
        
        res.json = function(data?: any): IResponse {
            logger.info(`${method} ${path} - ${res.statusCode}`);
            return originalJson(data);
        };
        
        next();
    };
}

// src/routes/user.routes.ts
import type { IRequest, IResponse } from '../controllers/user.controller';
import type { UserController } from '../controllers/user.controller';
import { Logger, LogLevel } from '../utils/logger';
import { createAuthMiddleware } from '../middleware/auth.middleware';
import { createLoggingMiddleware } from '../middleware/logging.middleware';

export function createUserRoutes(
    userController: UserController,
    userService: UserService,
    logger: Logger
): {
    path: string;
    handler: (req: IRequest, res: IResponse) => void | Promise<void>;
    method: string;
}[] {
    const authMiddleware = createAuthMiddleware(userService, logger);
    const loggingMiddleware = createLoggingMiddleware(logger);
    
    return [
        {
            path: "/",
            handler: userController.getAllUsers.bind(userController),
            method: "get"
        },
        {
            path: "/",
            handler: userController.createUser.bind(userController),
            method: "post"
        },
        {
            path: "/search",
            handler: userController.searchUsers.bind(userController),
            method: "get"
        },
        {
            path: "/count",
            handler: userController.getUserCount.bind(userController),
            method: "get"
        },
        {
            path: "/:id",
            handler: userController.getUserById.bind(userController),
            method: "get"
        },
        {
            path: "/:id",
            handler: userController.updateUser.bind(userController),
            method: "put"
        },
        {
            path: "/:id",
            handler: userController.deleteUser.bind(userController),
            method: "delete"
        }
    ];
}

// src/app.ts
import { Logger, LogLevel } from './utils/logger';
import { UserRepository } from './repositories/user.repository';
import { UserService } from './services/user.service';
import { UserController, IRequest, IResponse } from './controllers/user.controller';
import { createUserRoutes } from './routes/user.routes';

export class App {
    private userController: UserController;
    private routes: {
        path: string;
        handler: (req: IRequest, res: IResponse) => void | Promise<void>;
        method: string;
    }[] = [];
    
    constructor() {
        // 依赖注入
        const logger = new Logger(LogLevel.INFO);
        const userRepository = new UserRepository(logger);
        const userService = new UserService(userRepository);
        this.userController = new UserController(userService, logger);
        
        // 初始化路由
        this.routes = createUserRoutes(this.userController, userService, logger);
    }
    
    async handleRequest(method: string, path: string, body?: any, query?: Record<string, string>, headers?: Record<string, string>): Promise<any> {
        // 查找匹配的路由
        const route = this.routes.find(r => 
            r.method === method.toLowerCase() && this.matchPath(r.path, path)
        );
        
        if (!route) {
            return {
                status: 404,
                data: { error: "Not Found" }
            };
        }
        
        // 创建请求和响应对象
        const req: IRequest = {
            params: this.extractParams(route.path, path),
            query: query || {},
            body: body || {},
            headers: headers || {}
        };
        
        let responseData: any;
        let statusCode = 200;
        
        // 模拟响应对象
        const res: IResponse = {
            status: (code: number) => {
                statusCode = code;
                return res;
            },
            json: (data: any) => {
                responseData = data;
            },
            send: (data: any) => {
                responseData = data;
            }
        };
        
        try {
            // 执行路由处理器
            await route.handler(req, res);
            
            return {
                status: statusCode,
                data: responseData
            };
        } catch (error) {
            return {
                status: 500,
                data: { error: "Internal Server Error" }
            };
        }
    }
    
    private matchPath(routePath: string, requestPath: string): boolean {
        // 简单的路径匹配，实际实现会更复杂
        if (routePath === requestPath) return true;
        
        // 处理参数路径，如 /users/:id
        const routeSegments = routePath.split('/');
        const requestSegments = requestPath.split('/');
        
        if (routeSegments.length !== requestSegments.length) return false;
        
        for (let i = 0; i < routeSegments.length; i++) {
            if (!routeSegments[i].startsWith(':') && routeSegments[i] !== requestSegments[i]) {
                return false;
            }
        }
        
        return true;
    }
    
    private extractParams(routePath: string, requestPath: string): Record<string, string> {
        const params: Record<string, string> = {};
        const routeSegments = routePath.split('/');
        const requestSegments = requestPath.split('/');
        
        for (let i = 0; i < routeSegments.length; i++) {
            if (routeSegments[i].startsWith(':')) {
                const paramName = routeSegments[i].substring(1);
                params[paramName] = requestSegments[i];
            }
        }
        
        return params;
    }
    
    // 获取所有路由信息
    getRoutesInfo() {
        return this.routes.map(route => ({
            method: route.method,
            path: route.path
        }));
    }
}

// 测试模块化应用程序
async function testModularApplication() {
    console.log("=== Testing Modular Application ===");
    
    // 创建应用实例
    const app = new App();
    
    // 显示路由信息
    console.log("Available routes:");
    console.table(app.getRoutesInfo());
    
    // 测试路由
    console.log("\n=== Testing Routes ===");
    
    // 测试获取所有用户
    console.log("\n1. Getting all users:");
    const getAllUsersResult = await app.handleRequest("get", "/users");
    console.log("Status:", getAllUsersResult.status);
    console.log("Data:", getAllUsersResult.data);
    
    // 测试创建用户
    console.log("\n2. Creating a user:");
    const createUserResult = await app.handleRequest("post", "/users", {
        name: "Alice",
        email: "alice@example.com"
    });
    console.log("Status:", createUserResult.status);
    console.log("Data:", createUserResult.data);
    
    // 测试搜索用户
    console.log("\n3. Searching users:");
    const searchUsersResult = await app.handleRequest("get", "/users/search", undefined, { name: "alice" });
    console.log("Status:", searchUsersResult.status);
    console.log("Data:", searchUsersResult.data);
    
    // 测试获取特定用户
    console.log("\n4. Getting user by ID:");
    const getUserResult = await app.handleRequest("get", "/users/1");
    console.log("Status:", getUserResult.status);
    console.log("Data:", getUserResult.data);
    
    // 测试更新用户
    console.log("\n5. Updating user:");
    const updateUserResult = await app.handleRequest("put", "/users/1", {
        name: "Alice Smith"
    });
    console.log("Status:", updateUserResult.status);
    console.log("Data:", updateUserResult.data);
    
    // 测试删除用户
    console.log("\n6. Deleting user:");
    const deleteUserResult = await app.handleRequest("delete", "/users/1");
    console.log("Status:", deleteUserResult.status);
    console.log("Data:", deleteUserResult.data);
    
    // 测试错误处理
    console.log("\n=== Testing Error Handling ===");
    
    // 测试无效请求
    console.log("\n7. Invalid request:");
    const invalidRequestResult = await app.handleRequest("get", "/invalid");
    console.log("Status:", invalidRequestResult.status);
    console.log("Data:", invalidRequestResult.data);
    
    // 测试创建无效用户
    console.log("\n8. Creating invalid user:");
    const createUserErrorResult = await app.handleRequest("post", "/users", {
        name: "", // 空名称
        email: "invalid-email" // 无效邮箱
    });
    console.log("Status:", createUserErrorResult.status);
    console.log("Data:", createUserErrorResult.data);
    
    // 测试更新不存在的用户
    console.log("\n9. Updating non-existent user:");
    const updateUserErrorResult = await app.handleRequest("put", "/users/999", {
        name: "Updated Name"
    });
    console.log("Status:", updateUserErrorResult.status);
    console.log("Data:", updateUserErrorResult.data);
}

// 导出测试函数
export { testModularApplication };

// 如果直接运行此文件，执行测试
if (require.main === module) {
    testModularApplication().catch(error => {
        console.error("Error testing modular application:", error);
    });
}