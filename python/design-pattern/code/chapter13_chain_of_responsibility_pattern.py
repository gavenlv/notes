"""
责任链模式 (Chain of Responsibility Pattern) 示例代码

责任链模式避免请求发送者与接收者耦合在一起，让多个对象都有可能接收请求，将这些对象连接成一条链，并且沿着这条链传递请求，直到有对象处理它为止。
"""

from abc import ABC, abstractmethod
from typing import Optional


class Handler(ABC):
    """处理者抽象类"""
    
    def __init__(self):
        self._next_handler: Optional[Handler] = None
    
    def set_next(self, handler: 'Handler') -> 'Handler':
        """设置下一个处理者"""
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request) -> Optional[str]:
        """处理请求"""
        pass
    
    def _handle_next(self, request) -> Optional[str]:
        """传递给下一个处理者"""
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class ConcreteHandlerA(Handler):
    """具体处理者A"""
    
    def handle(self, request) -> Optional[str]:
        if request == "A":
            return f"处理者A处理请求: {request}"
        else:
            print("处理者A无法处理，传递给下一个处理者")
            return self._handle_next(request)


class ConcreteHandlerB(Handler):
    """具体处理者B"""
    
    def handle(self, request) -> Optional[str]:
        if request == "B":
            return f"处理者B处理请求: {request}"
        else:
            print("处理者B无法处理，传递给下一个处理者")
            return self._handle_next(request)


class ConcreteHandlerC(Handler):
    """具体处理者C"""
    
    def handle(self, request) -> Optional[str]:
        if request == "C":
            return f"处理者C处理请求: {request}"
        else:
            print("处理者C无法处理，传递给下一个处理者")
            return self._handle_next(request)


# 测试基础责任链模式
def test_basic_chain():
    """测试基础责任链模式"""
    print("=== 责任链模式测试 - 基础示例 ===\n")
    
    # 创建处理者链
    handler_a = ConcreteHandlerA()
    handler_b = ConcreteHandlerB()
    handler_c = ConcreteHandlerC()
    
    # 构建责任链: A -> B -> C
    handler_a.set_next(handler_b).set_next(handler_c)
    
    # 测试不同请求
    requests = ["A", "B", "C", "D"]
    
    for request in requests:
        print(f"\n处理请求: {request}")
        result = handler_a.handle(request)
        if result:
            print(result)
        else:
            print("没有处理者能够处理该请求")


# 实际应用示例：日志记录器
def test_logger_chain():
    """测试日志记录器责任链"""
    print("\n=== 责任链模式应用 - 日志记录器示例 ===\n")
    
    class LogLevel:
        """日志级别"""
        DEBUG = 1
        INFO = 2
        WARNING = 3
        ERROR = 4
        CRITICAL = 5
    
    class Logger(ABC):
        """日志记录器抽象类"""
        
        def __init__(self, level):
            self._level = level
            self._next_logger: Optional[Logger] = None
        
        def set_next(self, logger: 'Logger') -> 'Logger':
            self._next_logger = logger
            return logger
        
        def log_message(self, level, message):
            """记录日志"""
            if self._level <= level:
                self._write(message)
            
            if self._next_logger:
                self._next_logger.log_message(level, message)
        
        @abstractmethod
        def _write(self, message):
            """写入日志"""
            pass
    
    class ConsoleLogger(Logger):
        """控制台日志记录器"""
        
        def _write(self, message):
            print(f"控制台日志: {message}")
    
    class FileLogger(Logger):
        """文件日志记录器"""
        
        def _write(self, message):
            print(f"文件日志: {message}")
    
    class EmailLogger(Logger):
        """邮件日志记录器"""
        
        def _write(self, message):
            print(f"邮件日志: {message}")
    
    # 创建日志记录器链
    console_logger = ConsoleLogger(LogLevel.DEBUG)
    file_logger = FileLogger(LogLevel.INFO)
    email_logger = EmailLogger(LogLevel.ERROR)
    
    # 构建责任链: 控制台 -> 文件 -> 邮件
    console_logger.set_next(file_logger).set_next(email_logger)
    
    # 测试不同级别的日志
    print("记录DEBUG级别日志:")
    console_logger.log_message(LogLevel.DEBUG, "这是一条调试信息")
    
    print("\n记录INFO级别日志:")
    console_logger.log_message(LogLevel.INFO, "这是一条普通信息")
    
    print("\n记录WARNING级别日志:")
    console_logger.log_message(LogLevel.WARNING, "这是一条警告信息")
    
    print("\n记录ERROR级别日志:")
    console_logger.log_message(LogLevel.ERROR, "这是一条错误信息")
    
    print("\n记录CRITICAL级别日志:")
    console_logger.log_message(LogLevel.CRITICAL, "这是一条严重错误信息")


# 实际应用示例：审批系统
def test_approval_system():
    """测试审批系统责任链"""
    print("\n=== 责任链模式应用 - 审批系统示例 ===\n")
    
    class PurchaseRequest:
        """采购请求类"""
        
        def __init__(self, amount, purpose):
            self.amount = amount
            self.purpose = purpose
        
        def __str__(self):
            return f"采购请求: 金额{self.amount}元，用途: {self.purpose}"
    
    class Approver(ABC):
        """审批者抽象类"""
        
        def __init__(self, name, approval_limit):
            self.name = name
            self.approval_limit = approval_limit
            self._supervisor: Optional[Approver] = None
        
        def set_supervisor(self, supervisor: 'Approver'):
            self._supervisor = supervisor
        
        def process_request(self, request: PurchaseRequest):
            """处理审批请求"""
            if request.amount <= self.approval_limit:
                self._approve(request)
            elif self._supervisor:
                print(f"{self.name}无法审批，转交给{self._supervisor.name}")
                self._supervisor.process_request(request)
            else:
                self._reject(request)
        
        def _approve(self, request):
            print(f"{self.name}批准了{request}")
        
        def _reject(self, request):
            print(f"{self.name}拒绝了{request}（超出审批权限）")
    
    class Director(Approver):
        """总监（审批限额：5000元）"""
        
        def __init__(self, name):
            super().__init__(name, 5000)
    
    class Manager(Approver):
        """经理（审批限额：10000元）"""
        
        def __init__(self, name):
            super().__init__(name, 10000)
    
    class VicePresident(Approver):
        """副总裁（审批限额：50000元）"""
        
        def __init__(self, name):
            super().__init__(name, 50000)
    
    class President(Approver):
        """总裁（审批限额：无限制）"""
        
        def __init__(self, name):
            super().__init__(name, float('inf'))
    
    # 创建审批者链
    director = Director("张总监")
    manager = Manager("李经理")
    vp = VicePresident("王副总裁")
    president = President("赵总裁")
    
    # 构建责任链: 总监 -> 经理 -> 副总裁 -> 总裁
    director.set_supervisor(manager)
    manager.set_supervisor(vp)
    vp.set_supervisor(president)
    
    # 测试不同金额的采购请求
    requests = [
        PurchaseRequest(3000, "购买办公用品"),
        PurchaseRequest(8000, "购买服务器"),
        PurchaseRequest(25000, "公司团建"),
        PurchaseRequest(100000, "购买新办公楼")
    ]
    
    for request in requests:
        print(f"\n处理{request}")
        director.process_request(request)


# 实际应用示例：过滤器链
def test_filter_chain():
    """测试过滤器链责任链"""
    print("\n=== 责任链模式应用 - 过滤器链示例 ===\n")
    
    class Filter(ABC):
        """过滤器抽象类"""
        
        def __init__(self):
            self._next_filter: Optional[Filter] = None
        
        def set_next(self, filter_obj: 'Filter') -> 'Filter':
            self._next_filter = filter_obj
            return filter_obj
        
        def do_filter(self, request, response, filter_chain):
            """执行过滤"""
            pass
    
    class AuthenticationFilter(Filter):
        """认证过滤器"""
        
        def do_filter(self, request, response, filter_chain):
            print("认证过滤器: 检查用户认证")
            if request.get("user") == "admin":
                print("认证过滤器: 认证通过")
                if self._next_filter:
                    self._next_filter.do_filter(request, response, filter_chain)
                else:
                    filter_chain.do_filter(request, response)
            else:
                print("认证过滤器: 认证失败")
                response["error"] = "认证失败"
    
    class LoggingFilter(Filter):
        """日志过滤器"""
        
        def do_filter(self, request, response, filter_chain):
            print("日志过滤器: 记录请求日志")
            if self._next_filter:
                self._next_filter.do_filter(request, response, filter_chain)
            else:
                filter_chain.do_filter(request, response)
    
    class ValidationFilter(Filter):
        """验证过滤器"""
        
        def do_filter(self, request, response, filter_chain):
            print("验证过滤器: 验证请求参数")
            if request.get("data"):
                print("验证过滤器: 参数验证通过")
                if self._next_filter:
                    self._next_filter.do_filter(request, response, filter_chain)
                else:
                    filter_chain.do_filter(request, response)
            else:
                print("验证过滤器: 参数验证失败")
                response["error"] = "参数验证失败"
    
    class FilterChain:
        """过滤器链"""
        
        def __init__(self):
            self.filters = []
        
        def add_filter(self, filter_obj: Filter):
            self.filters.append(filter_obj)
        
        def do_filter(self, request, response):
            """执行过滤器链"""
            if self.filters:
                # 构建责任链
                for i in range(len(self.filters) - 1):
                    self.filters[i].set_next(self.filters[i + 1])
                
                # 从第一个过滤器开始执行
                self.filters[0].do_filter(request, response, self)
            else:
                self._process_request(request, response)
        
        def _process_request(self, request, response):
            """处理请求"""
            print("处理请求: 执行业务逻辑")
            response["result"] = "请求处理成功"
    
    # 测试过滤器链
    filter_chain = FilterChain()
    filter_chain.add_filter(AuthenticationFilter())
    filter_chain.add_filter(LoggingFilter())
    filter_chain.add_filter(ValidationFilter())
    
    # 测试认证失败的请求
    print("测试认证失败的请求:")
    request1 = {"user": "guest", "data": "test"}
    response1 = {}
    filter_chain.do_filter(request1, response1)
    print(f"响应: {response1}")
    
    # 测试参数验证失败的请求
    print("\n测试参数验证失败的请求:")
    request2 = {"user": "admin"}
    response2 = {}
    filter_chain.do_filter(request2, response2)
    print(f"响应: {response2}")
    
    # 测试成功的请求
    print("\n测试成功的请求:")
    request3 = {"user": "admin", "data": "test"}
    response3 = {}
    filter_chain.do_filter(request3, response3)
    print(f"响应: {response3}")


if __name__ == "__main__":
    test_basic_chain()
    test_logger_chain()
    test_approval_system()
    test_filter_chain()
    
    print("\n=== 责任链模式总结 ===")
    print("优点：")
    print("- 降低耦合度：请求发送者不需要知道哪个对象处理请求")
    print("- 增强了给对象指派职责的灵活性：可以动态地改变链中的成员")
    print("- 增加新的请求处理类很方便：无需修改原有代码")
    print("\n缺点：")
    print("- 不能保证请求一定被接收：可能到达链的末端都得不到处理")
    print("- 系统性能将受到一定影响：可能需要在链中进行多次传递")
    print("- 调试不太方便：采用类似递归的方式，调试时逻辑可能比较复杂")
    print("\n适用场景：")
    print("- 有多个对象可以处理一个请求，哪个对象处理由运行时决定")
    print("- 在不明确指定接收者的情况下，向多个对象中的一个提交一个请求")
    print("- 可动态指定一组对象处理请求")
