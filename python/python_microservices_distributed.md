# Python微服务架构与分布式系统指南

## 1. 微服务架构基础与设计原则

### 1.1 微服务架构核心概念

微服务架构是一种将应用程序构建为一组小型服务的架构风格，每个服务运行在自己的进程中，并通过轻量级机制（通常是HTTP API）进行通信。以下是微服务架构的核心概念与实现示例。

```python
# 微服务基础框架
import json
import time
import asyncio
import uuid
import inspect
from typing import Dict, Any, Callable, List, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    version: str
    host: str
    port: int
    health_check_path: str = "/health"
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

class ServiceRegistry(ABC):
    """服务注册中心接口"""
    
    @abstractmethod
    async def register(self, service: ServiceInfo) -> bool:
        """注册服务"""
        pass
    
    @abstractmethod
    async def deregister(self, service_name: str, service_id: str) -> bool:
        """注销服务"""
        pass
    
    @abstractmethod
    async def discover(self, service_name: str) -> List[ServiceInfo]:
        """发现服务"""
        pass
    
    @abstractmethod
    async def health_check(self, service_name: str) -> Dict[str, Any]:
        """健康检查"""
        pass

# 内存实现的服务注册中心（仅用于演示）
class InMemoryServiceRegistry(ServiceRegistry):
    """内存实现的服务注册中心"""
    
    def __init__(self):
        self.services = {}  # service_name -> {service_id: ServiceInfo}
        self.service_instances = {}  # service_id -> (service_name, ServiceInfo)
    
    async def register(self, service: ServiceInfo) -> bool:
        """注册服务"""
        service_id = str(uuid.uuid4())
        
        if service.name not in self.services:
            self.services[service.name] = {}
        
        self.services[service.name][service_id] = service
        self.service_instances[service_id] = (service.name, service)
        
        print(f"服务注册成功: {service.name} ({service.host}:{service.port}) - ID: {service_id}")
        return True
    
    async def deregister(self, service_name: str, service_id: str) -> bool:
        """注销服务"""
        if service_name in self.services and service_id in self.services[service_name]:
            del self.services[service_name][service_id]
            
            if not self.services[service_name]:
                del self.services[service_name]
            
            if service_id in self.service_instances:
                del self.service_instances[service_id]
            
            print(f"服务注销成功: {service_name} - ID: {service_id}")
            return True
        
        return False
    
    async def discover(self, service_name: str) -> List[ServiceInfo]:
        """发现服务"""
        if service_name in self.services:
            return list(self.services[service_name].values())
        return []
    
    async def health_check(self, service_name: str) -> Dict[str, Any]:
        """健康检查"""
        if service_name in self.services:
            instances = self.services[service_name]
            return {
                "service": service_name,
                "instances": len(instances),
                "details": [
                    {
                        "id": service_id,
                        "host": instance.host,
                        "port": instance.port,
                        "metadata": instance.metadata
                    }
                    for service_id, instance in instances.items()
                ]
            }
        return {"error": f"Service {service_name} not found"}

# 微服务基类
class MicroService:
    """微服务基类"""
    
    def __init__(self, name: str, version: str = "1.0.0", host: str = "127.0.0.1", port: int = 8000):
        self.name = name
        self.version = version
        self.host = host
        self.port = port
        self.service_info = ServiceInfo(
            name=name,
            version=version,
            host=host,
            port=port,
            metadata={}
        )
        self.endpoints = {}  # path -> (method, handler)
        self.middleware = []  # 中间件
        self.running = False
        self.registry = None  # 服务注册中心
    
    def register_with(self, registry: ServiceRegistry):
        """设置服务注册中心"""
        self.registry = registry
    
    def route(self, path: str, method: str = "GET"):
        """装饰器：注册路由"""
        def decorator(handler):
            self.endpoints[path] = (method.upper(), handler)
            return handler
        return decorator
    
    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self.middleware.append(middleware)
    
    async def register_service(self) -> bool:
        """注册服务"""
        if self.registry:
            return await self.registry.register(self.service_info)
        return False
    
    async def deregister_service(self) -> bool:
        """注销服务"""
        if self.registry:
            # 在实际实现中，应该保存注册时返回的service_id
            return await self.registry.deregister(self.name, "unknown")
        return False
    
    async def start(self):
        """启动服务"""
        if not self.endpoints:
            print(f"警告: 服务 {self.name} 没有注册任何端点")
        
        # 注册服务
        await self.register_service()
        
        self.running = True
        print(f"微服务 {self.name} v{self.version} 启动在 http://{self.host}:{self.port}")
        
        try:
            # 这里应该启动HTTP服务器，简化实现
            await self.serve()
        except Exception as e:
            print(f"服务启动失败: {e}")
        finally:
            await self.deregister_service()
    
    async def stop(self):
        """停止服务"""
        self.running = False
        await self.deregister_service()
        print(f"微服务 {self.name} 已停止")
    
    async def serve(self):
        """服务主循环（简化实现）"""
        while self.running:
            await asyncio.sleep(1)
    
    async def handle_request(self, method: str, path: str, body: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理请求"""
        # 查找匹配的路由
        handler = None
        for route_path, (route_method, route_handler) in self.endpoints.items():
            if route_path == path and route_method == method.upper():
                handler = route_handler
                break
        
        if not handler:
            return {"error": f"Path {path} not found for method {method}"}
        
        # 执行中间件
        request = {"method": method, "path": path, "body": body}
        for middleware in self.middleware:
            request = await middleware(request)
            if not request:  # 中间件可能中断请求
                return {"error": "Request blocked by middleware"}
        
        # 调用处理器
        try:
            if inspect.iscoroutinefunction(handler):
                return await handler(request)
            else:
                return handler(request)
        except Exception as e:
            return {"error": f"Handler error: {str(e)}"}

# API网关
class APIGateway:
    """API网关"""
    
    def __init__(self, registry: ServiceRegistry, host: str = "127.0.0.1", port: int = 8080):
        self.registry = registry
        self.host = host
        self.port = port
        self.routes = {}  # path -> service_name
        self.middleware = []
        self.running = False
        self.load_balancer = LoadBalancer()
    
    def add_route(self, path: str, service_name: str):
        """添加路由"""
        self.routes[path] = service_name
        print(f"添加网关路由: {path} -> {service_name}")
    
    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self.middleware.append(middleware)
    
    async def start(self):
        """启动网关"""
        self.running = True
        print(f"API网关启动在 http://{self.host}:{self.port}")
        
        try:
            # 这里应该启动HTTP服务器，简化实现
            await self.serve()
        except Exception as e:
            print(f"网关启动失败: {e}")
    
    async def stop(self):
        """停止网关"""
        self.running = False
        print("API网关已停止")
    
    async def serve(self):
        """网关主循环（简化实现）"""
        while self.running:
            await asyncio.sleep(1)
    
    async def forward_request(self, path: str, method: str, body: Dict[str, Any] = None) -> Dict[str, Any]:
        """转发请求到后端服务"""
        # 查找路由
        service_name = None
        for route_path, name in self.routes.items():
            if path.startswith(route_path):
                service_name = name
                break
        
        if not service_name:
            return {"error": f"No route found for {path}"}
        
        # 发现服务实例
        instances = await self.registry.discover(service_name)
        if not instances:
            return {"error": f"No instances found for service {service_name}"}
        
        # 负载均衡选择实例
        instance = self.load_balancer.select_instance(instances)
        if not instance:
            return {"error": f"Load balancer failed to select instance for {service_name}"}
        
        # 执行中间件
        request = {"method": method, "path": path, "body": body}
        for middleware in self.middleware:
            request = await middleware(request)
            if not request:
                return {"error": "Request blocked by middleware"}
        
        # 转发请求（简化实现）
        print(f"转发请求 {method} {path} 到 {service_name} ({instance.host}:{instance.port})")
        
        # 在实际实现中，这里会发送HTTP请求到选中的服务实例
        return {"message": f"Request forwarded to {service_name}"}

# 负载均衡器
class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.counters = {}  # service_name -> counter
    
    def select_instance(self, instances: List[ServiceInfo]) -> Optional[ServiceInfo]:
        """选择实例"""
        if not instances:
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin(instances)
        elif self.strategy == "random":
            return self._random(instances)
        elif self.strategy == "least_connections":
            return self._least_connections(instances)
        else:
            return instances[0]
    
    def _round_robin(self, instances: List[ServiceInfo]) -> ServiceInfo:
        """轮询算法"""
        service_name = instances[0].name
        
        if service_name not in self.counters:
            self.counters[service_name] = 0
        
        index = self.counters[service_name] % len(instances)
        self.counters[service_name] += 1
        
        return instances[index]
    
    def _random(self, instances: List[ServiceInfo]) -> ServiceInfo:
        """随机算法"""
        import random
        return random.choice(instances)
    
    def _least_connections(self, instances: List[ServiceInfo]) -> ServiceInfo:
        """最少连接算法（简化实现）"""
        # 在实际实现中，应该跟踪每个实例的连接数
        # 这里返回第一个实例作为示例
        return instances[0]

# 演示微服务架构
async def demo_microservices_architecture():
    """演示微服务架构"""
    
    print("=== 微服务架构演示 ===")
    
    # 创建服务注册中心
    registry = InMemoryServiceRegistry()
    
    # 创建用户服务
    user_service = MicroService("user-service", "1.0.0", "127.0.0.1", 8001)
    user_service.register_with(registry)
    
    @user_service.route("/users", "GET")
    async def get_users(request):
        """获取用户列表"""
        return {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
            ]
        }
    
    @user_service.route("/users/{id}", "GET")
    async def get_user(request):
        """获取单个用户"""
        # 简化实现，从路径中提取ID
        user_id = 1  # 实际应该从request.path中提取
        
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        }
    
    # 创建订单服务
    order_service = MicroService("order-service", "1.0.0", "127.0.0.1", 8002)
    order_service.register_with(registry)
    
    @order_service.route("/orders", "GET")
    async def get_orders(request):
        """获取订单列表"""
        return {
            "orders": [
                {"id": 101, "user_id": 1, "total": 99.99, "status": "completed"},
                {"id": 102, "user_id": 2, "total": 49.99, "status": "processing"},
                {"id": 103, "user_id": 1, "total": 149.99, "status": "shipped"}
            ]
        }
    
    @order_service.route("/orders", "POST")
    async def create_order(request):
        """创建订单"""
        body = request.get("body", {})
        user_id = body.get("user_id")
        items = body.get("items", [])
        total = sum(item.get("price", 0) * item.get("quantity", 0) for item in items)
        
        return {
            "id": 104,
            "user_id": user_id,
            "items": items,
            "total": total,
            "status": "created"
        }
    
    # 创建产品服务
    product_service = MicroService("product-service", "1.0.0", "127.0.0.1", 8003)
    product_service.register_with(registry)
    
    @product_service.route("/products", "GET")
    async def get_products(request):
        """获取产品列表"""
        return {
            "products": [
                {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
                {"id": 2, "name": "Mouse", "price": 19.99, "stock": 50},
                {"id": 3, "name": "Keyboard", "price": 49.99, "stock": 30}
            ]
        }
    
    # 创建API网关
    gateway = APIGateway(registry, "127.0.0.1", 8080)
    gateway.add_route("/api/users", "user-service")
    gateway.add_route("/api/orders", "order-service")
    gateway.add_route("/api/products", "product-service")
    
    # 添加认证中间件
    async def auth_middleware(request):
        """认证中间件"""
        # 在实际实现中，这里会验证JWT令牌或其他认证信息
        print(f"认证中间件: 验证请求 {request['method']} {request['path']}")
        return request
    
    # 添加日志中间件
    async def logging_middleware(request):
        """日志中间件"""
        print(f"请求日志: {time.strftime('%Y-%m-%d %H:%M:%S')} {request['method']} {request['path']}")
        return request
    
    gateway.add_middleware(auth_middleware)
    gateway.add_middleware(logging_middleware)
    
    # 在实际实现中，这会在单独线程中运行
    # user_task = asyncio.create_task(user_service.start())
    # order_task = asyncio.create_task(order_service.start())
    # product_task = asyncio.create_task(product_service.start())
    # gateway_task = asyncio.create_task(gateway.start())
    #
    # await asyncio.sleep(1)  # 等待服务启动
    #
    # # 测试服务发现
    # print("\n=== 测试服务发现 ===")
    # services = ["user-service", "order-service", "product-service"]
    # for service_name in services:
    #     instances = await registry.discover(service_name)
    #     print(f"{service_name}: {len(instances)} 个实例")
    #     for instance in instances:
    #         print(f"  - {instance.host}:{instance.port}")
    #
    # # 测试API网关
    # print("\n=== 测试API网关 ===")
    # test_requests = [
    #     ("GET", "/api/users", None),
    #     ("GET", "/api/orders", None),
    #     ("POST", "/api/orders", {"user_id": 1, "items": [{"id": 1, "price": 999.99, "quantity": 1}]}),
    #     ("GET", "/api/products", None)
    # ]
    #
    # for method, path, body in test_requests:
    #     response = await gateway.forward_request(method, path, body)
    #     print(f"请求: {method} {path}")
    #     print(f"响应: {response}")
    #     print()
    #
    # # 测试负载均衡
    # print("\n=== 测试负载均衡 ===")
    # for _ in range(5):
    #     response = await gateway.forward_request("GET", "/api/users")
    #     print(f"请求转发结果: {response['message']}")
    #     await asyncio.sleep(0.1)
    #
    # # 停止服务
    # await asyncio.sleep(1)
    # await user_service.stop()
    # await order_service.stop()
    # await product_service.stop()
    # await gateway.stop()

asyncio.run(demo_microservices_architecture())
```

## 2. RPC通信框架实现

### 2.1 基于HTTP的RPC框架

```python
import asyncio
import json
import uuid
import time
import inspect
from typing import Dict, Any, Callable, List, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# RPC消息类型
@dataclass
class RPCRequest:
    """RPC请求"""
    id: str
    method: str
    params: Dict[str, Any]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RPCRequest':
        """从字典创建"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            method=data.get("method", ""),
            params=data.get("params", {}),
            timestamp=data.get("timestamp", time.time())
        )

@dataclass
class RPCResponse:
    """RPC响应"""
    id: str
    result: Any
    error: Optional[str]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RPCResponse':
        """从字典创建"""
        return cls(
            id=data.get("id", ""),
            result=data.get("result", None),
            error=data.get("error", None),
            timestamp=data.get("timestamp", time.time())
        )

# RPC服务接口
class RPCService(ABC):
    """RPC服务接口"""
    
    @abstractmethod
    async def call(self, method: str, params: Dict[str, Any]) -> Any:
        """调用远程方法"""
        pass
    
    @abstractmethod
    async def register(self, method: str, handler: Callable) -> bool:
        """注册方法"""
        pass

# HTTP RPC实现
class HTTPRPCClient(RPCService):
    """基于HTTP的RPC客户端"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None  # 在实际实现中，这里应该是aiohttp.ClientSession
    
    async def call(self, method: str, params: Dict[str, Any]) -> Any:
        """调用远程方法"""
        request_id = str(uuid.uuid4())
        request = RPCRequest(
            id=request_id,
            method=method,
            params=params,
            timestamp=time.time()
        )
        
        # 在实际实现中，这里会发送HTTP请求
        print(f"发送RPC请求: {method} -> {self.base_url}/rpc")
        print(f"请求数据: {request.to_dict()}")
        
        # 模拟响应
        response = RPCResponse(
            id=request_id,
            result={"status": "success", "method": method},
            error=None,
            timestamp=time.time()
        )
        
        print(f"收到RPC响应: {response.to_dict()}")
        
        if response.error:
            raise Exception(response.error)
        
        return response.result
    
    async def register(self, method: str, handler: Callable) -> bool:
        """注册方法（客户端通常不实现）"""
        raise NotImplementedError("客户端不支持注册方法")

class HTTPRPCServer(RPCService):
    """基于HTTP的RPC服务器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8081):
        self.host = host
        self.port = port
        self.handlers = {}  # method -> handler
        self.running = False
    
    async def call(self, method: str, params: Dict[str, Any]) -> Any:
        """调用远程方法（服务器内部调用）"""
        if method in self.handlers:
            handler = self.handlers[method]
            if inspect.iscoroutinefunction(handler):
                return await handler(params)
            else:
                return handler(params)
        else:
            raise ValueError(f"Method {method} not found")
    
    async def register(self, method: str, handler: Callable) -> bool:
        """注册方法"""
        self.handlers[method] = handler
        print(f"注册RPC方法: {method}")
        return True
    
    def register_method(self, method: str):
        """装饰器：注册方法"""
        def decorator(handler):
            asyncio.create_task(self.register(method, handler))
            return handler
        return decorator
    
    async def start(self):
        """启动RPC服务器"""
        self.running = True
        print(f"HTTP RPC服务器启动: http://{self.host}:{self.port}/rpc")
        
        try:
            # 这里应该启动HTTP服务器，简化实现
            await self.serve()
        except Exception as e:
            print(f"服务器启动失败: {e}")
    
    async def stop(self):
        """停止RPC服务器"""
        self.running = False
        print("HTTP RPC服务器已停止")
    
    async def serve(self):
        """服务器主循环（简化实现）"""
        while self.running:
            await asyncio.sleep(1)
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理RPC请求"""
        try:
            # 解析请求
            request = RPCRequest.from_dict(request_data)
            
            # 调用方法
            result = await self.call(request.method, request.params)
            
            # 构建响应
            response = RPCResponse(
                id=request.id,
                result=result,
                error=None,
                timestamp=time.time()
            )
            
            return response.to_dict()
        
        except Exception as e:
            # 构建错误响应
            error_id = request_data.get("id", str(uuid.uuid4()))
            response = RPCResponse(
                id=error_id,
                result=None,
                error=str(e),
                timestamp=time.time()
            )
            
            return response.to_dict()

# RPC代理类
class RPCProxy:
    """RPC代理类，用于透明调用远程方法"""
    
    def __init__(self, client: RPCService, prefix: str = ""):
        self.client = client
        self.prefix = prefix
    
    def __getattr__(self, name: str) -> Callable:
        """动态方法调用"""
        method_name = f"{self.prefix}.{name}" if self.prefix else name
        
        async def method(*args, **kwargs):
            # 将位置参数转换为关键字参数
            params = {}
            
            # 如果方法签名定义了参数名，可以尝试映射
            if args and not kwargs:
                params = {"args": args}
            elif args and kwargs:
                params = {"args": args, **kwargs}
            else:
                params = kwargs
            
            return await self.client.call(method_name, params)
        
        return method

# 高级RPC功能 - 批量调用
class BatchRPC:
    """批量RPC调用"""
    
    def __init__(self, client: RPCService):
        self.client = client
        self.requests = []
    
    def add_call(self, method: str, params: Dict[str, Any] = None) -> str:
        """添加RPC调用"""
        if params is None:
            params = {}
        
        request_id = str(uuid.uuid4())
        self.requests.append({
            "id": request_id,
            "method": method,
            "params": params
        })
        
        return request_id
    
    async def execute(self) -> List[Any]:
        """执行批量调用"""
        if not self.requests:
            return []
        
        # 在实际实现中，这里会发送批量请求
        print(f"执行批量RPC调用，共 {len(self.requests)} 个请求")
        
        # 模拟响应
        results = []
        for request in self.requests:
            response = RPCResponse(
                id=request["id"],
                result={"status": "success", "method": request["method"]},
                error=None,
                timestamp=time.time()
            )
            results.append(response.result)
        
        # 清空请求列表
        self.requests = []
        
        return results

# 高级RPC功能 - 超时和重试
class ReliableRPC:
    """可靠的RPC客户端，支持超时和重试"""
    
    def __init__(self, client: RPCService, max_retries: int = 3, timeout: float = 5.0):
        self.client = client
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def call(self, method: str, params: Dict[str, Any]) -> Any:
        """带重试的RPC调用"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # 在实际实现中，这里会设置超时
                result = await asyncio.wait_for(
                    self.client.call(method, params),
                    timeout=self.timeout
                )
                return result
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 0.5 * (2 ** attempt)  # 指数退避
                    print(f"RPC调用失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"RPC调用失败，已达到最大重试次数: {e}")
        
        raise last_exception

# 演示RPC框架
async def demo_rpc_framework():
    """演示RPC框架"""
    
    print("=== RPC框架演示 ===")
    
    # 创建RPC服务器
    server = HTTPRPCServer(host="127.0.0.1", port=8081)
    
    # 注册RPC方法
    @server.register_method("user.get")
    async def get_user(params):
        """获取用户"""
        user_id = params.get("id", 1)
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        }
    
    @server.register_method("user.create")
    async def create_user(params):
        """创建用户"""
        name = params.get("name")
        email = params.get("email")
        
        if not name or not email:
            raise ValueError("Name and email are required")
        
        user_id = 100  # 模拟数据库自增ID
        return {
            "id": user_id,
            "name": name,
            "email": email,
            "created_at": time.time()
        }
    
    @server.register_method("product.list")
    async def list_products(params):
        """获取产品列表"""
        limit = params.get("limit", 10)
        offset = params.get("offset", 0)
        
        # 模拟数据库查询
        products = []
        for i in range(1, limit + 1):
            product_id = offset + i
            products.append({
                "id": product_id,
                "name": f"Product {product_id}",
                "price": 9.99 * product_id,
                "stock": 100 - product_id
            })
        
        return {
            "products": products,
            "total": 100,  # 模拟总数
            "limit": limit,
            "offset": offset
        }
    
    # 启动服务器（在实际使用中，这会在单独线程中运行）
    # server_task = asyncio.create_task(server.start())
    # await asyncio.sleep(1)  # 等待服务器启动
    
    # 创建RPC客户端
    client = HTTPRPCClient("http://127.0.0.1:8081")
    
    # 直接调用
    print("\n=== 直接RPC调用 ===")
    try:
        user = await client.call("user.get", {"id": 1})
        print(f"获取用户: {user}")
        
        new_user = await client.call("user.create", {"name": "Alice", "email": "alice@example.com"})
        print(f"创建用户: {new_user}")
        
        products = await client.call("product.list", {"limit": 5})
        print(f"获取产品列表: {products}")
    
    except Exception as e:
        print(f"RPC调用失败: {e}")
    
    # 使用代理
    print("\n=== 使用RPC代理 ===")
    user_proxy = RPCProxy(client, "user")
    
    try:
        user = await user_proxy.get(id=2)
        print(f"通过代理获取用户: {user}")
        
        new_user = await user_proxy.create(name="Bob", email="bob@example.com")
        print(f"通过代理创建用户: {new_user}")
    
    except Exception as e:
        print(f"代理调用失败: {e}")
    
    # 批量调用
    print("\n=== 批量RPC调用 ===")
    batch = BatchRPC(client)
    
    batch.add_call("user.get", {"id": 1})
    batch.add_call("user.get", {"id": 2})
    batch.add_call("product.list", {"limit": 3})
    
    try:
        results = await batch.execute()
        print(f"批量调用结果: {results}")
    except Exception as e:
        print(f"批量调用失败: {e}")
    
    # 可靠RPC调用
    print("\n=== 可靠RPC调用 ===")
    reliable_client = ReliableRPC(client, max_retries=2, timeout=1.0)
    
    try:
        user = await reliable_client.call("user.get", {"id": 3})
        print(f"可靠调用获取用户: {user}")
    except Exception as e:
        print(f"可靠调用失败: {e}")
    
    # 停止服务器
    # await server.stop()

asyncio.run(demo_rpc_framework())
```

### 2.2 高级消息队列与分布式事件系统

```python
import asyncio
import json
import uuid
import time
from typing import Dict, Any, List, Callable, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import threading
from collections import defaultdict

# 消息类型
class MessageType(Enum):
    """消息类型枚举"""
    COMMAND = "command"
    EVENT = "event"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"

@dataclass
class Message:
    """消息类"""
    id: str
    type: MessageType
    topic: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: float
    reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["type"] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=MessageType(data.get("type", "event")),
            topic=data.get("topic", ""),
            payload=data.get("payload", {}),
            headers=data.get("headers", {}),
            timestamp=data.get("timestamp", time.time()),
            reply_to=data.get("reply_to", None)
        )

# 消息处理器
class MessageHandler(ABC):
    """消息处理器基类"""
    
    @abstractmethod
    async def handle(self, message: Message) -> Optional[Message]:
        """处理消息"""
        pass

# 消息队列接口
class MessageQueue(ABC):
    """消息队列接口"""
    
    @abstractmethod
    async def publish(self, topic: str, message: Message) -> bool:
        """发布消息"""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, handler: MessageHandler) -> str:
        """订阅主题"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        pass

# 内存消息队列实现（仅用于演示）
class InMemoryMessageQueue(MessageQueue):
    """内存消息队列实现"""
    
    def __init__(self):
        self.subscriptions = defaultdict(list)  # topic -> [(subscription_id, handler), ...]
        self.subscription_handlers = {}  # subscription_id -> handler
        self.lock = threading.Lock()
        self.running = False
        self.loop = None
    
    async def publish(self, topic: str, message: Message) -> bool:
        """发布消息"""
        print(f"发布消息到主题 {topic}: {message.id}")
        
        # 获取订阅者
        subscribers = []
        with self.lock:
            if topic in self.subscriptions:
                subscribers = [handler for _, handler in self.subscriptions[topic]]
        
        # 异步通知所有订阅者
        tasks = []
        for handler in subscribers:
            task = asyncio.create_task(self._notify_subscriber(handler, message))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return True
    
    async def _notify_subscriber(self, handler: MessageHandler, message: Message):
        """通知订阅者"""
        try:
            response = await handler.handle(message)
            if response and message.reply_to:
                # 处理响应消息
                await self.publish(message.reply_to, response)
        except Exception as e:
            print(f"通知订阅者失败: {e}")
    
    async def subscribe(self, topic: str, handler: MessageHandler) -> str:
        """订阅主题"""
        subscription_id = str(uuid.uuid4())
        
        with self.lock:
            self.subscriptions[topic].append((subscription_id, handler))
            self.subscription_handlers[subscription_id] = handler
        
        print(f"订阅主题 {topic}: {subscription_id}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        with self.lock:
            # 从所有主题中移除订阅
            removed = False
            for topic, subscriptions in self.subscriptions.items():
                for i, (sub_id, _) in enumerate(subscriptions):
                    if sub_id == subscription_id:
                        subscriptions.pop(i)
                        removed = True
                        break
                
                if removed:
                    break
            
            if subscription_id in self.subscription_handlers:
                del self.subscription_handlers[subscription_id]
        
        if removed:
            print(f"取消订阅: {subscription_id}")
        
        return removed

# 事件总线
class EventBus:
    """事件总线"""
    
    def __init__(self, message_queue: MessageQueue):
        self.message_queue = message_queue
        self.command_handlers = {}
        self.query_handlers = {}
    
    async def publish_event(self, topic: str, payload: Dict[str, Any], headers: Dict[str, str] = None):
        """发布事件"""
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            topic=topic,
            payload=payload,
            headers=headers or {},
            timestamp=time.time()
        )
        
        return await self.message_queue.publish(topic, message)
    
    async def send_command(self, topic: str, payload: Dict[str, Any], headers: Dict[str, str] = None):
        """发送命令"""
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COMMAND,
            topic=topic,
            payload=payload,
            headers=headers or {},
            timestamp=time.time()
        )
        
        return await self.message_queue.publish(topic, message)
    
    async def send_query(self, topic: str, payload: Dict[str, Any], reply_to: str = None, headers: Dict[str, str] = None):
        """发送查询"""
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.QUERY,
            topic=topic,
            payload=payload,
            headers=headers or {},
            timestamp=time.time(),
            reply_to=reply_to
        )
        
        return await self.message_queue.publish(topic, message)
    
    def register_command_handler(self, topic: str, handler: MessageHandler) -> str:
        """注册命令处理器"""
        self.command_handlers[topic] = handler
        return asyncio.create_task(self.message_queue.subscribe(topic, handler))
    
    def register_query_handler(self, topic: str, handler: MessageHandler) -> str:
        """注册查询处理器"""
        self.query_handlers[topic] = handler
        return asyncio.create_task(self.message_queue.subscribe(topic, handler))
    
    def register_event_handler(self, topic: str, handler: MessageHandler) -> str:
        """注册事件处理器"""
        return asyncio.create_task(self.message_queue.subscribe(topic, handler))

# 特定领域的消息处理器
class UserEventHandler(MessageHandler):
    """用户事件处理器"""
    
    def __init__(self, user_service):
        self.user_service = user_service
    
    async def handle(self, message: Message) -> Optional[Message]:
        """处理用户事件"""
        if message.topic == "user.created":
            user_data = message.payload
            await self.user_service.on_user_created(user_data)
            print(f"处理用户创建事件: {user_data.get('name')}")
        
        elif message.topic == "user.updated":
            user_data = message.payload
            await self.user_service.on_user_updated(user_data)
            print(f"处理用户更新事件: {user_data.get('name')}")
        
        elif message.topic == "user.deleted":
            user_id = message.payload.get("id")
            await self.user_service.on_user_deleted(user_id)
            print(f"处理用户删除事件: {user_id}")
        
        return None  # 事件通常不需要响应

class UserCommandHandler(MessageHandler):
    """用户命令处理器"""
    
    def __init__(self, user_service):
        self.user_service = user_service
    
    async def handle(self, message: Message) -> Optional[Message]:
        """处理用户命令"""
        try:
            if message.topic == "user.create":
                user_data = message.payload
                user = await self.user_service.create_user(user_data)
                
                # 发布用户创建事件
                await self.user_service.event_bus.publish_event(
                    "user.created", 
                    user
                )
                
                return Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.RESPONSE,
                    topic="user.create.response",
                    payload={"user": user, "success": True},
                    headers={},
                    timestamp=time.time(),
                    reply_to=message.reply_to
                )
            
            elif message.topic == "user.update":
                user_id = message.payload.get("id")
                user_data = message.payload.get("data")
                user = await self.user_service.update_user(user_id, user_data)
                
                # 发布用户更新事件
                await self.user_service.event_bus.publish_event(
                    "user.updated",
                    user
                )
                
                return Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.RESPONSE,
                    topic="user.update.response",
                    payload={"user": user, "success": True},
                    headers={},
                    timestamp=time.time(),
                    reply_to=message.reply_to
                )
            
            elif message.topic == "user.delete":
                user_id = message.payload.get("id")
                await self.user_service.delete_user(user_id)
                
                # 发布用户删除事件
                await self.user_service.event_bus.publish_event(
                    "user.deleted",
                    {"id": user_id}
                )
                
                return Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.RESPONSE,
                    topic="user.delete.response",
                    payload={"success": True},
                    headers={},
                    timestamp=time.time(),
                    reply_to=message.reply_to
                )
            
        except Exception as e:
            return Message(
                id=str(uuid.uuid4()),
                type=MessageType.ERROR,
                topic="user.error",
                payload={"error": str(e)},
                headers={},
                timestamp=time.time(),
                reply_to=message.reply_to
            )
        
        return None

class UserQueryHandler(MessageHandler):
    """用户查询处理器"""
    
    def __init__(self, user_service):
        self.user_service = user_service
    
    async def handle(self, message: Message) -> Optional[Message]:
        """处理用户查询"""
        try:
            if message.topic == "user.get":
                user_id = message.payload.get("id")
                user = await self.user_service.get_user(user_id)
                
                return Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.RESPONSE,
                    topic="user.get.response",
                    payload={"user": user},
                    headers={},
                    timestamp=time.time(),
                    reply_to=message.reply_to
                )
            
            elif message.topic == "user.list":
                filters = message.payload.get("filters", {})
                users = await self.user_service.list_users(filters)
                
                return Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.RESPONSE,
                    topic="user.list.response",
                    payload={"users": users},
                    headers={},
                    timestamp=time.time(),
                    reply_to=message.reply_to
                )
        
        except Exception as e:
            return Message(
                id=str(uuid.uuid4()),
                type=MessageType.ERROR,
                topic="user.error",
                payload={"error": str(e)},
                headers={},
                timestamp=time.time(),
                reply_to=message.reply_to
            )
        
        return None

# 用户服务
class UserService:
    """用户服务"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.users = {}
        self.next_id = 1
    
    async def create_user(self, user_data):
        """创建用户"""
        user_id = self.next_id
        self.next_id += 1
        
        user = {
            "id": user_id,
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "created_at": time.time()
        }
        
        self.users[user_id] = user
        return user
    
    async def update_user(self, user_id, user_data):
        """更新用户"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        user = self.users[user_id]
        
        if "name" in user_data:
            user["name"] = user_data["name"]
        
        if "email" in user_data:
            user["email"] = user_data["email"]
        
        user["updated_at"] = time.time()
        return user
    
    async def delete_user(self, user_id):
        """删除用户"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        del self.users[user_id]
    
    async def get_user(self, user_id):
        """获取用户"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        return self.users[user_id]
    
    async def list_users(self, filters=None):
        """获取用户列表"""
        users = list(self.users.values())
        
        # 应用过滤器
        if filters:
            if "name" in filters:
                name_filter = filters["name"].lower()
                users = [u for u in users if name_filter in u["name"].lower()]
            
            if "email" in filters:
                email_filter = filters["email"].lower()
                users = [u for u in users if email_filter in u["email"].lower()]
        
        return users
    
    async def on_user_created(self, user_data):
        """用户创建事件处理"""
        print(f"用户创建事件处理: {user_data.get('name')} ({user_data.get('id')})")
        # 可以在这里发送欢迎邮件等
    
    async def on_user_updated(self, user_data):
        """用户更新事件处理"""
        print(f"用户更新事件处理: {user_data.get('name')} ({user_data.get('id')})")
        # 可以在这里记录审计日志等
    
    async def on_user_deleted(self, user_id):
        """用户删除事件处理"""
        print(f"用户删除事件处理: {user_id}")
        # 可以在这里清理相关数据等

# 分布式事务管理器
class DistributedTransactionManager:
    """分布式事务管理器"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.transactions = {}  # transaction_id -> transaction_info
    
    async def begin_transaction(self) -> str:
        """开始事务"""
        transaction_id = str(uuid.uuid4())
        self.transactions[transaction_id] = {
            "id": transaction_id,
            "status": "active",
            "operations": [],
            "created_at": time.time()
        }
        
        # 发布事务开始事件
        await self.event_bus.publish_event(
            "transaction.began",
            {"transaction_id": transaction_id}
        )
        
        return transaction_id
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """提交事务"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        if transaction["status"] != "active":
            return False
        
        # 提交所有操作
        for operation in transaction["operations"]:
            await self._execute_operation(operation, "commit")
        
        # 更新事务状态
        transaction["status"] = "committed"
        transaction["committed_at"] = time.time()
        
        # 发布事务提交事件
        await self.event_bus.publish_event(
            "transaction.committed",
            {"transaction_id": transaction_id}
        )
        
        return True
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """回滚事务"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        if transaction["status"] != "active":
            return False
        
        # 回滚所有操作
        for operation in reversed(transaction["operations"]):
            await self._execute_operation(operation, "rollback")
        
        # 更新事务状态
        transaction["status"] = "rolled_back"
        transaction["rolled_back_at"] = time.time()
        
        # 发布事务回滚事件
        await self.event_bus.publish_event(
            "transaction.rolled_back",
            {"transaction_id": transaction_id}
        )
        
        return True
    
    async def add_operation(self, transaction_id: str, operation_type: str, operation_data: Dict[str, Any]) -> bool:
        """添加操作到事务"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        if transaction["status"] != "active":
            return False
        
        operation = {
            "type": operation_type,
            "data": operation_data,
            "timestamp": time.time()
        }
        
        transaction["operations"].append(operation)
        
        # 发布操作添加事件
        await self.event_bus.publish_event(
            "transaction.operation_added",
            {
                "transaction_id": transaction_id,
                "operation_type": operation_type,
                "operation_data": operation_data
            }
        )
        
        return True
    
    async def _execute_operation(self, operation: Dict[str, Any], phase: str):
        """执行操作"""
        operation_type = operation["type"]
        operation_data = operation["data"]
        
        # 发布操作执行事件
        await self.event_bus.publish_event(
            "transaction.operation_executed",
            {
                "operation_type": operation_type,
                "operation_data": operation_data,
                "phase": phase
            }
        )
        
        print(f"执行操作 {operation_type} (阶段: {phase})")
        # 在实际实现中，这里会调用相应的服务执行操作

# 演示分布式事件系统
async def demo_distributed_event_system():
    """演示分布式事件系统"""
    
    print("=== 分布式事件系统演示 ===")
    
    # 创建消息队列
    message_queue = InMemoryMessageQueue()
    
    # 创建事件总线
    event_bus = EventBus(message_queue)
    
    # 创建用户服务
    user_service = UserService(event_bus)
    
    # 注册处理器
    user_command_handler = UserCommandHandler(user_service)
    user_query_handler = UserQueryHandler(user_service)
    user_event_handler = UserEventHandler(user_service)
    
    event_bus.register_command_handler("user.create", user_command_handler)
    event_bus.register_command_handler("user.update", user_command_handler)
    event_bus.register_command_handler("user.delete", user_command_handler)
    
    event_bus.register_query_handler("user.get", user_query_handler)
    event_bus.register_query_handler("user.list", user_query_handler)
    
    event_bus.register_event_handler("user.created", user_event_handler)
    event_bus.register_event_handler("user.updated", user_event_handler)
    event_bus.register_event_handler("user.deleted", user_event_handler)
    
    # 创建分布式事务管理器
    transaction_manager = DistributedTransactionManager(event_bus)
    
    # 模拟分布式事务
    print("\n=== 分布式事务演示 ===")
    
    # 开始事务
    transaction_id = await transaction_manager.begin_transaction()
    print(f"开始事务: {transaction_id}")
    
    # 添加操作
    await transaction_manager.add_operation(
        transaction_id,
        "create_user",
        {"name": "Alice", "email": "alice@example.com"}
    )
    
    await transaction_manager.add_operation(
        transaction_id,
        "create_user",
        {"name": "Bob", "email": "bob@example.com"}
    )
    
    # 提交事务
    await transaction_manager.commit_transaction(transaction_id)
    print(f"提交事务: {transaction_id}")
    
    # 模拟事件驱动操作
    print("\n=== 事件驱动操作演示 ===")
    
    # 发布用户创建事件
    await event_bus.publish_event(
        "user.created",
        {"id": 1, "name": "Charlie", "email": "charlie@example.com"}
    )
    
    # 发送命令
    await event_bus.send_command(
        "user.create",
        {"name": "David", "email": "david@example.com"}
    )
    
    # 发送查询
    await event_bus.send_query(
        "user.get",
        {"id": 1}
    )
    
    # 等待一段时间，让所有事件处理完成
    await asyncio.sleep(1)

asyncio.run(demo_distributed_event_system())
```

## 3. 服务发现与配置管理

### 3.1 服务注册与发现机制

```python
import asyncio
import json
import time
import uuid
import socket
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import random

# 服务状态
class ServiceStatus(Enum):
    """服务状态枚举"""
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"

@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    name: str
    version: str
    host: str
    port: int
    status: ServiceStatus
    health_check_url: str
    metadata: Dict[str, Any]
    last_heartbeat: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInstance':
        """从字典创建"""
        status = ServiceStatus(data.get("status", "RUNNING"))
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            version=data.get("version"),
            host=data.get("host"),
            port=data.get("port"),
            status=status,
            health_check_url=data.get("health_check_url", ""),
            metadata=data.get("metadata", {}),
            last_heartbeat=data.get("last_heartbeat", time.time())
        )

# 健康检查结果
@dataclass
class HealthCheckResult:
    """健康检查结果"""
    service_id: str
    healthy: bool
    response_time: float
    message: str
    timestamp: float

# 服务注册中心接口
class ServiceRegistry(ABC):
    """服务注册中心接口"""
    
    @abstractmethod
    async def register(self, service: ServiceInstance) -> bool:
        """注册服务"""
        pass
    
    @abstractmethod
    async def deregister(self, service_id: str) -> bool:
        """注销服务"""
        pass
    
    @abstractmethod
    async def discover(self, service_name: str) -> List[ServiceInstance]:
        """发现服务"""
        pass
    
    @abstractmethod
    async def heartbeat(self, service_id: str) -> bool:
        """发送心跳"""
        pass
    
    @abstractmethod
    async def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """获取服务实例"""
        pass
    
    @abstractmethod
    async def update_service_status(self, service_id: str, status: ServiceStatus) -> bool:
        """更新服务状态"""
        pass

# 健康检查器
class HealthChecker:
    """健康检查器"""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
    
    async def check(self, service: ServiceInstance) -> HealthCheckResult:
        """检查服务健康状态"""
        start_time = time.time()
        
        try:
            # 在实际实现中，这里会发送HTTP请求到服务的健康检查端点
            # 这里只是模拟
            await asyncio.sleep(0.1)  # 模拟网络延迟
            
            # 模拟健康检查结果
            healthy = random.random() > 0.1  # 90%的概率健康
            response_time = time.time() - start_time
            
            if healthy:
                message = "Service is healthy"
            else:
                message = "Service is unhealthy"
            
            return HealthCheckResult(
                service_id=service.id,
                healthy=healthy,
                response_time=response_time,
                message=message,
                timestamp=time.time()
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_id=service.id,
                healthy=False,
                response_time=time.time() - start_time,
                message=f"Health check failed: {str(e)}",
                timestamp=time.time()
            )

# 基于内存的服务注册中心（仅用于演示）
class InMemoryServiceRegistry(ServiceRegistry):
    """基于内存的服务注册中心"""
    
    def __init__(self):
        self.services = {}  # service_id -> ServiceInstance
        self.service_names = {}  # service_name -> {service_id}
        self.lock = threading.Lock()
    
    async def register(self, service: ServiceInstance) -> bool:
        """注册服务"""
        with self.lock:
            # 如果服务已存在，先注销
            if service.id in self.services:
                await self.deregister(service.id)
            
            # 注册服务
            self.services[service.id] = service
            
            if service.name not in self.service_names:
                self.service_names[service.name] = set()
            
            self.service_names[service.name].add(service.id)
        
        print(f"服务注册成功: {service.name} ({service.host}:{service.port}) - ID: {service.id}")
        return True
    
    async def deregister(self, service_id: str) -> bool:
        """注销服务"""
        with self.lock:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # 从服务名称映射中移除
            if service.name in self.service_names:
                self.service_names[service.name].discard(service_id)
                
                if not self.service_names[service.name]:
                    del self.service_names[service.name]
            
            # 从服务实例中移除
            del self.services[service_id]
        
        print(f"服务注销成功: {service.name} - ID: {service_id}")
        return True
    
    async def discover(self, service_name: str) -> List[ServiceInstance]:
        """发现服务"""
        with self.lock:
            if service_name not in self.service_names:
                return []
            
            service_ids = self.service_names[service_name]
            return [self.services[service_id] for service_id in service_ids]
    
    async def heartbeat(self, service_id: str) -> bool:
        """发送心跳"""
        with self.lock:
            if service_id not in self.services:
                return False
            
            # 更新心跳时间
            self.services[service_id].last_heartbeat = time.time()
            return True
    
    async def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """获取服务实例"""
        with self.lock:
            return self.services.get(service_id)
    
    async def update_service_status(self, service_id: str, status: ServiceStatus) -> bool:
        """更新服务状态"""
        with self.lock:
            if service_id not in self.services:
                return False
            
            self.services[service_id].status = status
            return True
    
    async def get_all_services(self) -> List[ServiceInstance]:
        """获取所有服务"""
        with self.lock:
            return list(self.services.values())

# 服务发现客户端
class ServiceDiscovery:
    """服务发现客户端"""
    
    def __init__(self, registry: ServiceRegistry, refresh_interval: float = 30.0):
        self.registry = registry
        self.refresh_interval = refresh_interval
        self.cache = {}  # service_name -> [ServiceInstance]
        self.cache_time = {}  # service_name -> timestamp
        self.lock = threading.Lock()
        self.running = False
        self.refresh_task = None
    
    async def discover(self, service_name: str, use_cache: bool = True) -> List[ServiceInstance]:
        """发现服务"""
        with self.lock:
            # 检查缓存
            if use_cache and service_name in self.cache:
                cache_time = self.cache_time.get(service_name, 0)
                if time.time() - cache_time < self.refresh_interval:
                    return self.cache[service_name]
        
        # 从注册中心获取服务
        services = await self.registry.discover(service_name)
        
        # 更新缓存
        with self.lock:
            self.cache[service_name] = services
            self.cache_time[service_name] = time.time()
        
        return services
    
    async def start_refresh_task(self):
        """启动刷新任务"""
        if self.running:
            return
        
        self.running = True
        self.refresh_task = asyncio.create_task(self._refresh_cache())
    
    async def stop_refresh_task(self):
        """停止刷新任务"""
        self.running = False
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
    
    async def _refresh_cache(self):
        """刷新缓存任务"""
        while self.running:
            try:
                with self.lock:
                    service_names = list(self.cache.keys())
                
                for service_name in service_names:
                    services = await self.registry.discover(service_name)
                    
                    with self.lock:
                        self.cache[service_name] = services
                        self.cache_time[service_name] = time.time()
                
                # 等待下一次刷新
                await asyncio.sleep(self.refresh_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"刷新服务缓存失败: {e}")
                await asyncio.sleep(5)  # 错误后短暂等待

# 负载均衡器
class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.counters = {}  # service_name -> index
    
    def select(self, services: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """选择服务实例"""
        if not services:
            return None
        
        # 只选择健康的服务
        healthy_services = [
            service for service in services 
            if service.status == ServiceStatus.RUNNING
        ]
        
        if not healthy_services:
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin(healthy_services)
        elif self.strategy == "random":
            return self._random(healthy_services)
        elif self.strategy == "weighted":
            return self._weighted(healthy_services)
        else:
            return healthy_services[0]
    
    def _round_robin(self, services: List[ServiceInstance]) -> ServiceInstance:
        """轮询算法"""
        service_name = services[0].name
        
        if service_name not in self.counters:
            self.counters[service_name] = 0
        
        index = self.counters[service_name] % len(services)
        self.counters[service_name] += 1
        
        return services[index]
    
    def _random(self, services: List[ServiceInstance]) -> ServiceInstance:
        """随机算法"""
        return random.choice(services)
    
    def _weighted(self, services: List[ServiceInstance]) -> ServiceInstance:
        """加权算法（基于元数据中的权重）"""
        weights = []
        for service in services:
            weight = service.metadata.get("weight", 1)
            weights.append(weight)
        
        total_weight = sum(weights)
        if total_weight <= 0:
            return services[0]
        
        r = random.uniform(0, total_weight)
        
        up_to = 0
        for service, weight in zip(services, weights):
            up_to += weight
            if r <= up_to:
                return service
        
        return services[0]

# 服务客户端
class ServiceClient:
    """服务客户端"""
    
    def __init__(self, 
                 service_name: str, 
                 discovery: ServiceDiscovery,
                 load_balancer: LoadBalancer = None):
        self.service_name = service_name
        self.discovery = discovery
        self.load_balancer = load_balancer or LoadBalancer()
    
    async def get_service_instance(self) -> Optional[ServiceInstance]:
        """获取服务实例"""
        services = await self.discovery.discover(self.service_name)
        return self.load_balancer.select(services)
    
    async def call_service(self, path: str, method: str = "GET", 
                          data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """调用服务"""
        instance = await self.get_service_instance()
        if not instance:
            return None
        
        # 在实际实现中，这里会发送HTTP请求
        url = f"http://{instance.host}:{instance.port}{path}"
        print(f"调用服务: {method} {url}")
        
        # 模拟响应
        return {
            "service": self.service_name,
            "instance_id": instance.id,
            "path": path,
            "method": method,
            "timestamp": time.time()
        }

# 服务注册器
class ServiceRegistrar:
    """服务注册器"""
    
    def __init__(self, 
                 service_name: str, 
                 version: str, 
                 host: str, 
                 port: int,
                 registry: ServiceRegistry,
                 health_check_url: str = "/health",
                 metadata: Dict[str, Any] = None):
        self.service_name = service_name
        self.version = version
        self.host = host
        self.port = port
        self.health_check_url = health_check_url
        self.metadata = metadata or {}
        self.registry = registry
        self.service_id = str(uuid.uuid4())
        self.instance = None
        self.running = False
        self.heartbeat_task = None
    
    async def register(self) -> bool:
        """注册服务"""
        # 获取本地IP
        local_ip = self.host or self._get_local_ip()
        
        # 创建服务实例
        self.instance = ServiceInstance(
            id=self.service_id,
            name=self.service_name,
            version=self.version,
            host=local_ip,
            port=self.port,
            status=ServiceStatus.STARTING,
            health_check_url=self.health_check_url,
            metadata=self.metadata,
            last_heartbeat=time.time()
        )
        
        # 注册服务
        success = await self.registry.register(self.instance)
        if success:
            # 更新状态为运行中
            await self.registry.update_service_status(self.service_id, ServiceStatus.RUNNING)
            
            # 启动心跳任务
            self.running = True
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        return success
    
    async def deregister(self) -> bool:
        """注销服务"""
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # 更新状态为停止中
        if self.instance:
            await self.registry.update_service_status(self.service_id, ServiceStatus.STOPPING)
            
            # 注销服务
            return await self.registry.deregister(self.service_id)
        
        return False
    
    def _get_local_ip(self) -> str:
        """获取本地IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                # 发送心跳
                await self.registry.heartbeat(self.service_id)
                
                # 等待下一次心跳
                await asyncio.sleep(10)  # 10秒心跳间隔
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"心跳发送失败: {e}")
                await asyncio.sleep(5)  # 错误后短暂等待

# 配置管理器
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.config_cache = {}  # service_name -> config
    
    async def get_config(self, service_name: str) -> Dict[str, Any]:
        """获取服务配置"""
        # 检查缓存
        if service_name in self.config_cache:
            return self.config_cache[service_name]
        
        # 从注册中心获取配置
        services = await self.registry.discover(service_name)
        if services:
            # 从第一个服务的元数据中获取配置
            service = services[0]
            config = service.metadata.get("config", {})
            
            # 缓存配置
            self.config_cache[service_name] = config
            
            return config
        
        return {}
    
    async def update_config(self, service_name: str, config: Dict[str, Any]) -> bool:
        """更新服务配置"""
        services = await self.registry.discover(service_name)
        
        for service in services:
            # 更新每个服务实例的配置
            service.metadata["config"] = config
        
        # 更新缓存
        self.config_cache[service_name] = config
        
        return True
    
    def clear_cache(self, service_name: str = None):
        """清除配置缓存"""
        if service_name:
            self.config_cache.pop(service_name, None)
        else:
            self.config_cache.clear()

# 演示服务发现与配置管理
async def demo_service_discovery_config():
    """演示服务发现与配置管理"""
    
    print("=== 服务发现与配置管理演示 ===")
    
    # 创建服务注册中心
    registry = InMemoryServiceRegistry()
    
    # 创建配置管理器
    config_manager = ConfigManager(registry)
    
    # 创建服务发现客户端
    discovery = ServiceDiscovery(registry, refresh_interval=5.0)
    await discovery.start_refresh_task()
    
    # 创建负载均衡器
    load_balancer = LoadBalancer(strategy="round_robin")
    
    # 创建服务客户端
    user_service_client = ServiceClient("user-service", discovery, load_balancer)
    
    # 注册服务
    user_service_registrar = ServiceRegistrar(
        service_name="user-service",
        version="1.0.0",
        host="127.0.0.1",
        port=8001,
        registry=registry,
        health_check_url="/health",
        metadata={
            "weight": 2,
            "region": "us-east-1",
            "config": {
                "max_connections": 100,
                "timeout": 5.0
            }
        }
    )
    
    # 注册第二个用户服务实例
    user_service_registrar2 = ServiceRegistrar(
        service_name="user-service",
        version="1.0.0",
        host="127.0.0.1",
        port=8002,
        registry=registry,
        health_check_url="/health",
        metadata={
            "weight": 1,
            "region": "us-west-1",
            "config": {
                "max_connections": 50,
                "timeout": 3.0
            }
        }
    )
    
    # 注册订单服务
    order_service_registrar = ServiceRegistrar(
        service_name="order-service",
        version="1.0.0",
        host="127.0.0.1",
        port=8003,
        registry=registry,
        health_check_url="/health",
        metadata={
            "weight": 1,
            "region": "us-east-1",
            "config": {
                "max_orders": 1000,
                "timeout": 10.0
            }
        }
    )
    
    # 注册服务
    await user_service_registrar.register()
    await user_service_registrar2.register()
    await order_service_registrar.register()
    
    # 测试服务发现
    print("\n=== 测试服务发现 ===")
    user_services = await discovery.discover("user-service")
    print(f"发现的用户服务实例数量: {len(user_services)}")
    for service in user_services:
        print(f"  - {service.host}:{service.port} (权重: {service.metadata.get('weight', 1)})")
    
    # 测试服务客户端
    print("\n=== 测试服务客户端 ===")
    for i in range(5):
        result = await user_service_client.call_service("/users", "GET")
        if result:
            print(f"调用结果 {i+1}: {result['instance_id']}")
        await asyncio.sleep(0.1)
    
    # 测试配置管理
    print("\n=== 测试配置管理 ===")
    config = await config_manager.get_config("user-service")
    print(f"用户服务配置: {config}")
    
    # 更新配置
    new_config = {
        "max_connections": 200,
        "timeout": 8.0,
        "new_feature": True
    }
    await config_manager.update_config("user-service", new_config)
    
    # 再次获取配置
    config = await config_manager.get_config("user-service")
    print(f"更新后的用户服务配置: {config}")
    
    # 测试健康检查
    print("\n=== 测试健康检查 ===")
    health_checker = HealthChecker()
    
    for service in user_services:
        result = await health_checker.check(service)
        print(f"健康检查 {service.id}: {'健康' if result.healthy else '不健康'} "
              f"(响应时间: {result.response_time:.3f}s)")
    
    # 停止服务注册
    await user_service_registrar.deregister()
    await user_service_registrar2.deregister()
    await order_service_registrar.deregister()
    
    # 停止服务发现
    await discovery.stop_refresh_task()

asyncio.run(demo_service_discovery_config())
```

这份Python微服务架构与分布式系统指南涵盖了微服务架构基础与设计原则、RPC通信框架实现、服务发现与配置管理等高级主题。通过这份指南，您可以掌握构建可扩展、高可用的微服务架构的核心技能，设计并实现分布式系统中的服务通信、服务发现和负载均衡等关键组件。