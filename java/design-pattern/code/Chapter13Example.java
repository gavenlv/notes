// Chapter13Example.java - 责任链模式示例代码

// 请求类
class Request {
    private String type;
    private String content;
    private int level;
    
    public Request(String type, String content, int level) {
        this.type = type;
        this.content = content;
        this.level = level;
    }
    
    public String getType() { return type; }
    public String getContent() { return content; }
    public int getLevel() { return level; }
}

// 抽象处理者
abstract class Handler {
    protected Handler nextHandler;
    
    public void setNext(Handler handler) {
        this.nextHandler = handler;
    }
    
    public abstract void handleRequest(Request request);
}

// 具体处理者A
class ConcreteHandlerA extends Handler {
    @Override
    public void handleRequest(Request request) {
        if (request.getType().equals("A")) {
            System.out.println("ConcreteHandlerA 处理请求: " + request.getContent());
        } else if (nextHandler != null) {
            nextHandler.handleRequest(request);
        } else {
            System.out.println("无法处理请求: " + request.getContent());
        }
    }
}

// 具体处理者B
class ConcreteHandlerB extends Handler {
    @Override
    public void handleRequest(Request request) {
        if (request.getType().equals("B")) {
            System.out.println("ConcreteHandlerB 处理请求: " + request.getContent());
        } else if (nextHandler != null) {
            nextHandler.handleRequest(request);
        } else {
            System.out.println("无法处理请求: " + request.getContent());
        }
    }
}

// 具体处理者C
class ConcreteHandlerC extends Handler {
    @Override
    public void handleRequest(Request request) {
        if (request.getType().equals("C")) {
            System.out.println("ConcreteHandlerC 处理请求: " + request.getContent());
        } else if (nextHandler != null) {
            nextHandler.handleRequest(request);
        } else {
            System.out.println("无法处理请求: " + request.getContent());
        }
    }
}

// 请假请求类
class LeaveRequest {
    private String employee;
    private int days;
    private String reason;
    
    public LeaveRequest(String employee, int days, String reason) {
        this.employee = employee;
        this.days = days;
        this.reason = reason;
    }
    
    public String getEmployee() { return employee; }
    public int getDays() { return days; }
    public String getReason() { return reason; }
}

// 抽象审批者
abstract class Approver {
    protected Approver successor;
    protected String name;
    
    public Approver(String name) {
        this.name = name;
    }
    
    public void setSuccessor(Approver successor) {
        this.successor = successor;
    }
    
    public abstract void processRequest(LeaveRequest request);
}

// 主管审批者
class Supervisor extends Approver {
    public Supervisor(String name) {
        super(name);
    }
    
    @Override
    public void processRequest(LeaveRequest request) {
        if (request.getDays() <= 3) {
            System.out.println("主管 " + name + " 批准了 " + 
                request.getEmployee() + " 的请假申请 (" + 
                request.getDays() + " 天)");
        } else if (successor != null) {
            successor.processRequest(request);
        } else {
            System.out.println("请假申请未被批准: " + request.getEmployee() + 
                " 的 " + request.getDays() + " 天请假申请");
        }
    }
}

// 经理审批者
class Manager extends Approver {
    public Manager(String name) {
        super(name);
    }
    
    @Override
    public void processRequest(LeaveRequest request) {
        if (request.getDays() <= 7) {
            System.out.println("经理 " + name + " 批准了 " + 
                request.getEmployee() + " 的请假申请 (" + 
                request.getDays() + " 天)");
        } else if (successor != null) {
            successor.processRequest(request);
        } else {
            System.out.println("请假申请未被批准: " + request.getEmployee() + 
                " 的 " + request.getDays() + " 天请假申请");
        }
    }
}

// 总经理审批者
class GeneralManager extends Approver {
    public GeneralManager(String name) {
        super(name);
    }
    
    @Override
    public void processRequest(LeaveRequest request) {
        if (request.getDays() <= 15) {
            System.out.println("总经理 " + name + " 批准了 " + 
                request.getEmployee() + " 的请假申请 (" + 
                request.getDays() + " 天)");
        } else {
            System.out.println("请假天数过多，需要董事会批准: " + 
                request.getEmployee() + " 的 " + request.getDays() + " 天请假申请");
        }
    }
}

// 日志级别枚举
enum LogLevel {
    INFO(1), DEBUG(2), ERROR(3);
    
    private int level;
    
    LogLevel(int level) {
        this.level = level;
    }
    
    public int getLevel() {
        return level;
    }
}

// 抽象日志处理器
abstract class Logger {
    protected LogLevel level;
    protected Logger nextLogger;
    
    public Logger(LogLevel level) {
        this.level = level;
    }
    
    public void setNextLogger(Logger nextLogger) {
        this.nextLogger = nextLogger;
    }
    
    public void logMessage(LogLevel level, String message) {
        if (this.level.getLevel() <= level.getLevel()) {
            write(message);
        }
        if (nextLogger != null) {
            nextLogger.logMessage(level, message);
        }
    }
    
    protected abstract void write(String message);
}

// 控制台日志处理器
class ConsoleLogger extends Logger {
    public ConsoleLogger(LogLevel level) {
        super(level);
    }
    
    @Override
    protected void write(String message) {
        System.out.println("Console Logger: " + message);
    }
}

// 文件日志处理器
class FileLogger extends Logger {
    public FileLogger(LogLevel level) {
        super(level);
    }
    
    @Override
    protected void write(String message) {
        System.out.println("File Logger: " + message);
    }
}

// 错误日志处理器
class ErrorLogger extends Logger {
    public ErrorLogger(LogLevel level) {
        super(level);
    }
    
    @Override
    protected void write(String message) {
        System.out.println("Error Logger: " + message);
    }
}

// 请求类
class WebRequest {
    private String url;
    private String method;
    private java.util.Map<String, String> headers;
    private String body;
    
    public WebRequest(String url, String method) {
        this.url = url;
        this.method = method;
        this.headers = new java.util.HashMap<>();
    }
    
    public String getUrl() { return url; }
    public String getMethod() { return method; }
    public java.util.Map<String, String> getHeaders() { return headers; }
    public String getBody() { return body; }
    public void setBody(String body) { this.body = body; }
}

// 响应类
class WebResponse {
    private int statusCode;
    private String body;
    
    public WebResponse() {
        this.statusCode = 200;
        this.body = "";
    }
    
    public int getStatusCode() { return statusCode; }
    public void setStatusCode(int statusCode) { this.statusCode = statusCode; }
    public String getBody() { return body; }
    public void setBody(String body) { this.body = body; }
}

// 抽象过滤器
abstract class Filter {
    protected Filter nextFilter;
    
    public void setNext(Filter nextFilter) {
        this.nextFilter = nextFilter;
    }
    
    public void doFilter(WebRequest request, WebResponse response) {
        if (process(request, response)) {
            if (nextFilter != null) {
                nextFilter.doFilter(request, response);
            }
        }
    }
    
    protected abstract boolean process(WebRequest request, WebResponse response);
}

// 认证过滤器
class AuthenticationFilter extends Filter {
    @Override
    protected boolean process(WebRequest request, WebResponse response) {
        String authHeader = request.getHeaders().get("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            System.out.println("认证失败: 缺少有效的认证头");
            response.setStatusCode(401);
            response.setBody("Unauthorized");
            return false;
        }
        System.out.println("认证成功");
        return true;
    }
}

// 日志过滤器
class LoggingFilter extends Filter {
    @Override
    protected boolean process(WebRequest request, WebResponse response) {
        System.out.println("记录日志: " + request.getMethod() + " " + request.getUrl());
        return true;
    }
}

// 权限过滤器
class AuthorizationFilter extends Filter {
    @Override
    protected boolean process(WebRequest request, WebResponse response) {
        // 简化的权限检查
        if (request.getUrl().contains("/admin") && 
            !"admin".equals(request.getHeaders().get("Role"))) {
            System.out.println("权限不足: 无法访问管理接口");
            response.setStatusCode(403);
            response.setBody("Forbidden");
            return false;
        }
        System.out.println("权限检查通过");
        return true;
    }
}

// 主类 - 演示责任链模式
public class Chapter13Example {
    public static void main(String[] args) {
        System.out.println("=== 第十三章 责任链模式示例 ===\n");
        
        // 示例1: 基本责任链
        System.out.println("1. 基本责任链示例:");
        Handler handlerA = new ConcreteHandlerA();
        Handler handlerB = new ConcreteHandlerB();
        Handler handlerC = new ConcreteHandlerC();
        
        // 构建责任链: A -> B -> C
        handlerA.setNext(handlerB);
        handlerB.setNext(handlerC);
        
        // 测试不同类型的请求
        Request reqA = new Request("A", "类型A的请求", 1);
        Request reqB = new Request("B", "类型B的请求", 2);
        Request reqC = new Request("C", "类型C的请求", 3);
        Request reqD = new Request("D", "类型D的请求(无法处理)", 4);
        
        handlerA.handleRequest(reqA);
        handlerA.handleRequest(reqB);
        handlerA.handleRequest(reqC);
        handlerA.handleRequest(reqD);
        System.out.println();
        
        // 示例2: 请假审批责任链
        System.out.println("2. 请假审批责任链示例:");
        Approver supervisor = new Supervisor("张主管");
        Approver manager = new Manager("李经理");
        Approver generalManager = new GeneralManager("王总经理");
        
        // 构建审批链: 主管 -> 经理 -> 总经理
        supervisor.setSuccessor(manager);
        manager.setSuccessor(generalManager);
        
        // 测试不同的请假申请
        LeaveRequest req1 = new LeaveRequest("小明", 2, "生病");
        LeaveRequest req2 = new LeaveRequest("小红", 5, "旅游");
        LeaveRequest req3 = new LeaveRequest("小刚", 10, "家庭事务");
        LeaveRequest req4 = new LeaveRequest("小李", 20, "长期休假");
        
        supervisor.processRequest(req1);
        supervisor.processRequest(req2);
        supervisor.processRequest(req3);
        supervisor.processRequest(req4);
        System.out.println();
        
        // 示例3: 日志处理责任链
        System.out.println("3. 日志处理责任链示例:");
        Logger errorLogger = new ErrorLogger(LogLevel.ERROR);
        Logger fileLogger = new FileLogger(LogLevel.DEBUG);
        Logger consoleLogger = new ConsoleLogger(LogLevel.INFO);
        
        // 构建日志链: ErrorLogger -> FileLogger -> ConsoleLogger
        errorLogger.setNextLogger(fileLogger);
        fileLogger.setNextLogger(consoleLogger);
        
        // 测试不同级别的日志
        errorLogger.logMessage(LogLevel.INFO, "这是一条普通信息日志");
        errorLogger.logMessage(LogLevel.DEBUG, "这是一条调试日志");
        errorLogger.logMessage(LogLevel.ERROR, "这是一条错误日志");
        System.out.println();
        
        // 示例4: Web请求过滤器责任链
        System.out.println("4. Web请求过滤器责任链示例:");
        Filter authFilter = new AuthenticationFilter();
        Filter logFilter = new LoggingFilter();
        Filter authzFilter = new AuthorizationFilter();
        
        // 构建过滤器链: 认证 -> 日志 -> 权限
        authFilter.setNext(logFilter);
        logFilter.setNext(authzFilter);
        
        // 测试成功的请求
        System.out.println("--- 成功的请求 ---");
        WebRequest request1 = new WebRequest("/api/users", "GET");
        request1.getHeaders().put("Authorization", "Bearer token123");
        request1.getHeaders().put("Role", "user");
        WebResponse response1 = new WebResponse();
        authFilter.doFilter(request1, response1);
        
        // 测试失败的请求（缺少认证）
        System.out.println("\n--- 缺少认证的请求 ---");
        WebRequest request2 = new WebRequest("/api/users", "POST");
        WebResponse response2 = new WebResponse();
        authFilter.doFilter(request2, response2);
        System.out.println("响应状态码: " + response2.getStatusCode());
        System.out.println("响应内容: " + response2.getBody());
        
        // 测试失败的请求（权限不足）
        System.out.println("\n--- 权限不足的请求 ---");
        WebRequest request3 = new WebRequest("/admin/users", "DELETE");
        request3.getHeaders().put("Authorization", "Bearer token123");
        request3.getHeaders().put("Role", "user");
        WebResponse response3 = new WebResponse();
        authFilter.doFilter(request3, response3);
        System.out.println("响应状态码: " + response3.getStatusCode());
        System.out.println("响应内容: " + response3.getBody());
    }
}