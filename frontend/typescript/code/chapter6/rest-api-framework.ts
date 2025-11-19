// 基于装饰器的REST API框架示例
import "reflect-metadata";

// 定义框架元数据键
const CONTROLLER_METADATA_KEY = Symbol("controller");
const ROUTE_METADATA_KEY = Symbol("route");
const MIDDLEWARE_METADATA_KEY = Symbol("middleware");
const BODY_METADATA_KEY = Symbol("body");
const PARAM_METADATA_KEY = Symbol("param");
const QUERY_METADATA_KEY = Symbol("query");
const HEADER_METADATA_KEY = Symbol("header");
const RESPONSE_METADATA_KEY = Symbol("response");

// HTTP方法枚举
enum HttpMethod {
    GET = "get",
    POST = "post",
    PUT = "put",
    DELETE = "delete",
    PATCH = "patch"
}

// HTTP状态码枚举
enum HttpStatus {
    OK = 200,
    CREATED = 201,
    NO_CONTENT = 204,
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    INTERNAL_SERVER_ERROR = 500
}

// 请求/响应接口
interface Request {
    method: string;
    path: string;
    params: Record<string, string>;
    query: Record<string, string>;
    headers: Record<string, string>;
    body: any;
}

interface Response {
    status(code: number): Response;
    json(data: any): void;
    send(data: any): void;
    header(name: string, value: string): Response;
}

// 中间件函数类型
type MiddlewareFunction = (req: Request, res: Response, next: () => void) => void;

// 路由接口
interface Route {
    method: HttpMethod;
    path: string;
    handler: string; // 方法名
    middlewares: MiddlewareFunction[];
}

// 控制器元数据接口
interface ControllerMetadata {
    path: string;
    middlewares: MiddlewareFunction[];
}

// 控制器装饰器
function Controller(path: string = "", ...middlewares: MiddlewareFunction[]) {
    return function<T extends { new(...args: any[]): {} }>(constructor: T) {
        const metadata: ControllerMetadata = {
            path,
            middlewares
        };
        
        Reflect.defineMetadata(CONTROLLER_METADATA_KEY, metadata, constructor);
        return constructor;
    };
}

// HTTP方法装饰器
function Get(path: string = "", ...middlewares: MiddlewareFunction[]) {
    return createRouteDecorator(HttpMethod.GET, path, middlewares);
}

function Post(path: string = "", ...middlewares: MiddlewareFunction[]) {
    return createRouteDecorator(HttpMethod.POST, path, middlewares);
}

function Put(path: string = "", ...middlewares: MiddlewareFunction[]) {
    return createRouteDecorator(HttpMethod.PUT, path, middlewares);
}

function Delete(path: string = "", ...middlewares: MiddlewareFunction[]) {
    return createRouteDecorator(HttpMethod.DELETE, path, middlewares);
}

function Patch(path: string = "", ...middlewares: MiddlewareFunction[]) {
    return createRouteDecorator(HttpMethod.PATCH, path, middlewares);
}

// 创建路由装饰器的辅助函数
function createRouteDecorator(method: HttpMethod, path: string, middlewares: MiddlewareFunction[]) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingRoutes = Reflect.getMetadata(ROUTE_METADATA_KEY, target) || [];
        
        existingRoutes.push({
            method,
            path,
            handler: propertyKey,
            middlewares
        });
        
        Reflect.defineMetadata(ROUTE_METADATA_KEY, existingRoutes, target);
        return descriptor;
    };
}

// 参数装饰器
function Body() {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingBodyParams = Reflect.getMetadata(BODY_METADATA_KEY, target, propertyKey) || [];
        existingBodyParams.push(parameterIndex);
        Reflect.defineMetadata(BODY_METADATA_KEY, existingBodyParams, target, propertyKey);
    };
}

function Param(name: string) {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingParams = Reflect.getMetadata(PARAM_METADATA_KEY, target, propertyKey) || [];
        existingParams[parameterIndex] = { name };
        Reflect.defineMetadata(PARAM_METADATA_KEY, existingParams, target, propertyKey);
    };
}

function Query(name: string) {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingQueries = Reflect.getMetadata(QUERY_METADATA_KEY, target, propertyKey) || [];
        existingQueries[parameterIndex] = { name };
        Reflect.defineMetadata(QUERY_METADATA_KEY, existingQueries, target, propertyKey);
    };
}

function Header(name: string) {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingHeaders = Reflect.getMetadata(HEADER_METADATA_KEY, target, propertyKey) || [];
        existingHeaders[parameterIndex] = { name };
        Reflect.defineMetadata(HEADER_METADATA_KEY, existingHeaders, target, propertyKey);
    };
}

function Response() {
    return function(target: any, propertyKey: string, parameterIndex: number) {
        const existingResponses = Reflect.getMetadata(RESPONSE_METADATA_KEY, target, propertyKey) || [];
        existingResponses.push(parameterIndex);
        Reflect.defineMetadata(RESPONSE_METADATA_KEY, existingResponses, target, propertyKey);
    };
}

// 中间件装饰器
function Middleware(...middlewares: MiddlewareFunction[]) {
    return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const existingMiddlewares = Reflect.getMetadata(MIDDLEWARE_METADATA_KEY, target, propertyKey) || [];
        existingMiddlewares.push(...middlewares);
        Reflect.defineMetadata(MIDDLEWARE_METADATA_KEY, existingMiddlewares, target, propertyKey);
        return descriptor;
    };
}

// 路由器类
class Router {
    private routes: Route[] = [];
    private controllers: any[] = [];
    
    registerController(controller: any): void {
        this.controllers.push(controller);
        
        const controllerMetadata = Reflect.getMetadata(CONTROLLER_METADATA_KEY, controller.constructor);
        const controllerPath = controllerMetadata ? controllerMetadata.path : "";
        const controllerMiddlewares = controllerMetadata ? controllerMetadata.middlewares : [];
        
        const routes = Reflect.getMetadata(ROUTE_METADATA_KEY, controller) || [];
        
        for (const route of routes) {
            const fullPath = `${controllerPath}${route.path}`;
            
            // 合并控制器级别的中间件和方法级别的中间件
            const middlewares = [
                ...controllerMiddlewares,
                ...route.middlewares
            ];
            
            this.routes.push({
                method: route.method,
                path: fullPath,
                handler: route.handler,
                middlewares
            });
        }
    }
    
    findRoute(method: string, path: string): Route | null {
        for (const route of this.routes) {
            if (route.method === method && this.matchPath(route.path, path)) {
                return route;
            }
        }
        return null;
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
    
    async handleRequest(request: Request, response: Response): Promise<void> {
        const route = this.findRoute(request.method, request.path);
        
        if (!route) {
            response.status(HttpStatus.NOT_FOUND).send("Not Found");
            return;
        }
        
        try {
            // 查找处理该路由的控制器
            const controller = this.controllers.find(ctrl => {
                const controllerMetadata = Reflect.getMetadata(CONTROLLER_METADATA_KEY, ctrl.constructor);
                const controllerPath = controllerMetadata ? controllerMetadata.path : "";
                const fullPath = `${controllerPath}${route.path}`;
                
                return this.routes.some(r => 
                    r.handler === route.handler && 
                    r.method === route.method && 
                    r.path === fullPath
                );
            });
            
            if (!controller) {
                response.status(HttpStatus.INTERNAL_SERVER_ERROR).send("Controller not found");
                return;
            }
            
            // 提取路径参数
            const params = this.extractParams(route.path, request.path);
            request.params = params;
            
            // 执行中间件
            for (const middleware of route.middlewares) {
                await this.executeMiddleware(middleware, request, response);
            }
            
            // 解析方法参数
            const args = await this.resolveArguments(request, response, controller, route.handler);
            
            // 执行路由处理器
            const result = await controller[route.handler](...args);
            
            // 处理返回结果
            if (result !== undefined) {
                response.status(HttpStatus.OK).json(result);
            } else {
                response.status(HttpStatus.NO_CONTENT).send();
            }
        } catch (error) {
            console.error("Error handling request:", error);
            response.status(HttpStatus.INTERNAL_SERVER_ERROR).send("Internal Server Error");
        }
    }
    
    private async executeMiddleware(
        middleware: MiddlewareFunction, 
        request: Request, 
        response: Response
    ): Promise<void> {
        return new Promise((resolve, reject) => {
            middleware(request, response, () => {
                resolve();
            });
        });
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
    
    private async resolveArguments(
        request: Request, 
        response: Response, 
        controller: any, 
        handlerName: string
    ): Promise<any[]> {
        const target = controller;
        const handlerName = handlerName;
        
        // 获取参数类型
        const paramTypes = Reflect.getMetadata("design:paramtypes", target, handlerName) || [];
        
        // 获取参数装饰器元数据
        const bodyParams = Reflect.getMetadata(BODY_METADATA_KEY, target, handlerName) || [];
        const routeParams = Reflect.getMetadata(PARAM_METADATA_KEY, target, handlerName) || [];
        const queryParams = Reflect.getMetadata(QUERY_METADATA_KEY, target, handlerName) || [];
        const headerParams = Reflect.getMetadata(HEADER_METADATA_KEY, target, handlerName) || [];
        const responseParams = Reflect.getMetadata(RESPONSE_METADATA_KEY, target, handlerName) || [];
        
        const args: any[] = [];
        
        for (let i = 0; i < paramTypes.length; i++) {
            if (bodyParams.includes(i)) {
                args.push(request.body);
            } else if (routeParams[i]) {
                const paramName = routeParams[i].name;
                args.push(request.params[paramName]);
            } else if (queryParams[i]) {
                const queryName = queryParams[i].name;
                args.push(request.query[queryName]);
            } else if (headerParams[i]) {
                const headerName = headerParams[i].name;
                args.push(request.headers[headerName]);
            } else if (responseParams.includes(i)) {
                args.push(response);
            } else {
                args.push(undefined);
            }
        }
        
        return args;
    }
}

// 中间件实现
const authMiddleware: MiddlewareFunction = (req, res, next) => {
    const token = req.headers["authorization"];
    
    if (!token) {
        res.status(HttpStatus.UNAUTHORIZED).send("Unauthorized");
        return;
    }
    
    // 在实际应用中，这里会验证token
    console.log("User authenticated");
    next();
};

const loggingMiddleware: MiddlewareFunction = (req, res, next) => {
    console.log(`${req.method} ${req.path}`);
    next();
};

const corsMiddleware: MiddlewareFunction = (req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
    next();
};

// 定义数据模型
interface User {
    id: number;
    name: string;
    email: string;
    createdAt: Date;
}

interface CreateUserRequest {
    name: string;
    email: string;
}

interface UpdateUserRequest {
    name?: string;
    email?: string;
}

// 模拟数据库
const users: User[] = [
    { id: 1, name: "Alice", email: "alice@example.com", createdAt: new Date() },
    { id: 2, name: "Bob", email: "bob@example.com", createdAt: new Date() }
];

// 控制器实现
@Controller("/users", corsMiddleware)
class UserController {
    @Get()
    @Middleware(loggingMiddleware)
    async getUsers(): Promise<User[]> {
        console.log("Getting all users");
        return users;
    }
    
    @Get("/:id")
    @Middleware(loggingMiddleware)
    async getUserById(@Param("id") id: string): Promise<User | null> {
        console.log(`Getting user with ID: ${id}`);
        const userId = parseInt(id, 10);
        return users.find(user => user.id === userId) || null;
    }
    
    @Post()
    @Middleware(authMiddleware, loggingMiddleware)
    async createUser(@Body() userData: CreateUserRequest): Promise<User> {
        console.log("Creating user:", userData);
        const newUser: User = {
            id: users.length + 1,
            name: userData.name,
            email: userData.email,
            createdAt: new Date()
        };
        users.push(newUser);
        return newUser;
    }
    
    @Put("/:id")
    @Middleware(authMiddleware, loggingMiddleware)
    async updateUser(@Param("id") id: string, @Body() userData: UpdateUserRequest): Promise<User | null> {
        console.log(`Updating user ${id} with:`, userData);
        const userId = parseInt(id, 10);
        const userIndex = users.findIndex(user => user.id === userId);
        
        if (userIndex === -1) {
            return null;
        }
        
        users[userIndex] = { ...users[userIndex], ...userData };
        return users[userIndex];
    }
    
    @Delete("/:id")
    @Middleware(authMiddleware, loggingMiddleware)
    async deleteUser(@Param("id") id: string): Promise<{ success: boolean }> {
        console.log(`Deleting user with ID: ${id}`);
        const userId = parseInt(id, 10);
        const userIndex = users.findIndex(user => user.id === userId);
        
        if (userIndex === -1) {
            return { success: false };
        }
        
        users.splice(userIndex, 1);
        return { success: true };
    }
    
    @Get("/search")
    async searchUsers(@Query("q") query: string): Promise<User[]> {
        console.log(`Searching users with query: ${query}`);
        if (!query) return [];
        
        return users.filter(user => 
            user.name.toLowerCase().includes(query.toLowerCase()) ||
            user.email.toLowerCase().includes(query.toLowerCase())
        );
    }
}

// 模拟请求/响应对象
function createMockRequest(method: string, path: string, body?: any, query?: Record<string, string>, headers?: Record<string, string>): Request {
    return {
        method,
        path,
        params: {},
        query: query || {},
        body: body || {},
        headers: headers || {}
    };
}

function createMockResponse(): Response {
    let statusCode = 200;
    let responseData: any;
    const responseHeaders: Record<string, string> = {};
    
    return {
        status(code: number): Response {
            statusCode = code;
            return this;
        },
        json(data: any): void {
            responseData = data;
            console.log(`Response (${statusCode}):`, responseData);
        },
        send(data: any): void {
            responseData = data;
            console.log(`Response (${statusCode}):`, responseData);
        },
        header(name: string, value: string): Response {
            responseHeaders[name] = value;
            return this;
        }
    };
}

// 测试路由
async function testRoutes() {
    console.log("=== Testing REST API Framework ===");
    
    const router = new Router();
    const userController = new UserController();
    
    // 注册控制器
    router.registerController(userController);
    
    // 测试路由
    console.log("\n=== Testing GET /users ===");
    const request1 = createMockRequest("get", "/users");
    const response1 = createMockResponse();
    await router.handleRequest(request1, response1);
    
    console.log("\n=== Testing GET /users/1 ===");
    const request2 = createMockRequest("get", "/users/1");
    const response2 = createMockResponse();
    await router.handleRequest(request2, response2);
    
    console.log("\n=== Testing POST /users ===");
    const request3 = createMockRequest("post", "/users", { name: "Charlie", email: "charlie@example.com" }, undefined, { authorization: "Bearer token" });
    const response3 = createMockResponse();
    await router.handleRequest(request3, response3);
    
    console.log("\n=== Testing PUT /users/1 ===");
    const request4 = createMockRequest("put", "/users/1", { name: "Alice Smith" }, undefined, { authorization: "Bearer token" });
    const response4 = createMockResponse();
    await router.handleRequest(request4, response4);
    
    console.log("\n=== Testing DELETE /users/2 ===");
    const request5 = createMockRequest("delete", "/users/2", undefined, undefined, { authorization: "Bearer token" });
    const response5 = createMockResponse();
    await router.handleRequest(request5, response5);
    
    console.log("\n=== Testing GET /users/search?q=alice ===");
    const request6 = createMockRequest("get", "/users/search", undefined, { q: "alice" });
    const response6 = createMockResponse();
    await router.handleRequest(request6, response6);
    
    console.log("\n=== Testing unauthorized request ===");
    const request7 = createMockRequest("post", "/users", { name: "Dave", email: "dave@example.com" });
    const response7 = createMockResponse();
    await router.handleRequest(request7, response7);
    
    console.log("\n=== Testing not found route ===");
    const request8 = createMockRequest("get", "/products");
    const response8 = createMockResponse();
    await router.handleRequest(request8, response8);
}

// 执行测试
testRoutes();

console.log("\nREST API framework demo completed!");