// Chapter9Example.java - 装饰器模式代码示例
import java.util.HashMap;
import java.util.Map;

// 组件接口 - 咖啡
interface Coffee {
    String getDescription();
    double getCost();
}

// 具体组件 - 简单咖啡
class SimpleCoffee implements Coffee {
    @Override
    public String getDescription() {
        return "Simple coffee";
    }
    
    @Override
    public double getCost() {
        return 2.0;
    }
}

// 装饰器抽象类
abstract class CoffeeDecorator implements Coffee {
    protected Coffee coffee;
    
    public CoffeeDecorator(Coffee coffee) {
        this.coffee = coffee;
    }
    
    @Override
    public String getDescription() {
        return coffee.getDescription();
    }
    
    @Override
    public double getCost() {
        return coffee.getCost();
    }
}

// 具体装饰器 - 牛奶
class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) {
        super(coffee);
    }
    
    @Override
    public String getDescription() {
        return coffee.getDescription() + ", milk";
    }
    
    @Override
    public double getCost() {
        return coffee.getCost() + 0.5;
    }
}

// 具体装饰器 - 糖
class SugarDecorator extends CoffeeDecorator {
    public SugarDecorator(Coffee coffee) {
        super(coffee);
    }
    
    @Override
    public String getDescription() {
        return coffee.getDescription() + ", sugar";
    }
    
    @Override
    public double getCost() {
        return coffee.getCost() + 0.3;
    }
}

// 具体装饰器 - 奶油
class WhipDecorator extends CoffeeDecorator {
    public WhipDecorator(Coffee coffee) {
        super(coffee);
    }
    
    @Override
    public String getDescription() {
        return coffee.getDescription() + ", whip";
    }
    
    @Override
    public double getCost() {
        return coffee.getCost() + 0.7;
    }
}

// 组件接口 - 通知服务
interface Notifier {
    void send(String message);
}

// 具体组件 - 基础邮件通知
class EmailNotifier implements Notifier {
    @Override
    public void send(String message) {
        System.out.println("Sending email with message: " + message);
    }
}

// 装饰器抽象类
abstract class NotifierDecorator implements Notifier {
    protected Notifier notifier;
    
    public NotifierDecorator(Notifier notifier) {
        this.notifier = notifier;
    }
    
    @Override
    public void send(String message) {
        notifier.send(message);
    }
}

// 具体装饰器 - 短信通知
class SMSDecorator extends NotifierDecorator {
    public SMSDecorator(Notifier notifier) {
        super(notifier);
    }
    
    @Override
    public void send(String message) {
        super.send(message);
        sendSMS(message);
    }
    
    private void sendSMS(String message) {
        System.out.println("Sending SMS with message: " + message);
    }
}

// 具体装饰器 - Facebook通知
class FacebookDecorator extends NotifierDecorator {
    public FacebookDecorator(Notifier notifier) {
        super(notifier);
    }
    
    @Override
    public void send(String message) {
        super.send(message);
        sendFacebook(message);
    }
    
    private void sendFacebook(String message) {
        System.out.println("Sending Facebook message with message: " + message);
    }
}

// 具体装饰器 - Slack通知
class SlackDecorator extends NotifierDecorator {
    public SlackDecorator(Notifier notifier) {
        super(notifier);
    }
    
    @Override
    public void send(String message) {
        super.send(message);
        sendSlack(message);
    }
    
    private void sendSlack(String message) {
        System.out.println("Sending Slack message with message: " + message);
    }
}

// 组件接口 - 请求处理器
interface RequestHandler {
    String handle(String request);
}

// 具体组件 - 基础处理器
class BasicHandler implements RequestHandler {
    @Override
    public String handle(String request) {
        return "Basic handling: " + request;
    }
}

// 装饰器抽象类
abstract class HandlerDecorator implements RequestHandler {
    protected RequestHandler handler;
    
    public HandlerDecorator(RequestHandler handler) {
        this.handler = handler;
    }
    
    @Override
    public String handle(String request) {
        return handler.handle(request);
    }
}

// 具体装饰器 - 日志装饰器
class LoggingDecorator extends HandlerDecorator {
    public LoggingDecorator(RequestHandler handler) {
        super(handler);
    }
    
    @Override
    public String handle(String request) {
        System.out.println("LOG: Handling request: " + request);
        String result = super.handle(request);
        System.out.println("LOG: Request handled with result: " + result);
        return result;
    }
}

// 具体装饰器 - 认证装饰器
class AuthDecorator extends HandlerDecorator {
    public AuthDecorator(RequestHandler handler) {
        super(handler);
    }
    
    @Override
    public String handle(String request) {
        // 简化的认证检查
        if (!request.contains("auth_token")) {
            return "ERROR: Authentication required";
        }
        return super.handle(request);
    }
}

// 具体装饰器 - 缓存装饰器
class CacheDecorator extends HandlerDecorator {
    private Map<String, String> cache = new HashMap<>();
    
    public CacheDecorator(RequestHandler handler) {
        super(handler);
    }
    
    @Override
    public String handle(String request) {
        if (cache.containsKey(request)) {
            System.out.println("CACHE: Returning cached result for: " + request);
            return cache.get(request);
        }
        
        String result = super.handle(request);
        cache.put(request, result);
        System.out.println("CACHE: Caching result for: " + request);
        return result;
    }
}

// 具体装饰器 - 压缩装饰器
class CompressionDecorator extends HandlerDecorator {
    public CompressionDecorator(RequestHandler handler) {
        super(handler);
    }
    
    @Override
    public String handle(String request) {
        String result = super.handle(request);
        String compressed = compress(result);
        System.out.println("COMPRESS: Compressed result from " + result.length() + " to " + compressed.length() + " characters");
        return compressed;
    }
    
    private String compress(String data) {
        // 简化的压缩实现
        return data.replaceAll("\\s+", " ");
    }
}

// 组件接口 - 图形组件
interface Graphic {
    void draw();
}

// 具体组件 - 简单文本
class TextView implements Graphic {
    private String text;
    
    public TextView(String text) {
        this.text = text;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing text: " + text);
    }
}

// 具体组件 - 简单图片
class ImageView implements Graphic {
    private String imageFile;
    
    public ImageView(String imageFile) {
        this.imageFile = imageFile;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing image: " + imageFile);
    }
}

// 装饰器抽象类
abstract class GraphicDecorator implements Graphic {
    protected Graphic graphic;
    
    public GraphicDecorator(Graphic graphic) {
        this.graphic = graphic;
    }
    
    @Override
    public void draw() {
        graphic.draw();
    }
}

// 具体装饰器 - 边框装饰器
class BorderDecorator extends GraphicDecorator {
    public BorderDecorator(Graphic graphic) {
        super(graphic);
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing border");
        super.draw();
        System.out.println("Border drawn");
    }
}

// 具体装饰器 - 滚动条装饰器
class ScrollDecorator extends GraphicDecorator {
    public ScrollDecorator(Graphic graphic) {
        super(graphic);
    }
    
    @Override
    public void draw() {
        System.out.println("Adding scroll bar");
        super.draw();
        System.out.println("Scroll bar added");
    }
}

// 具体装饰器 - 颜色装饰器
class ColorDecorator extends GraphicDecorator {
    private String color;
    
    public ColorDecorator(Graphic graphic, String color) {
        super(graphic);
        this.color = color;
    }
    
    @Override
    public void draw() {
        System.out.println("Setting color to " + color);
        super.draw();
        System.out.println("Color " + color + " applied");
    }
}

// 主类 - 演示装饰器模式的各种应用
public class Chapter9Example {
    public static void main(String[] args) {
        System.out.println("=== 装饰器模式示例 ===\n");
        
        // 示例1: 咖啡制作装饰器模式
        System.out.println("1. 咖啡制作装饰器模式:");
        Coffee coffee = new SimpleCoffee();
        printCoffeeInfo(coffee);
        
        coffee = new MilkDecorator(coffee);
        printCoffeeInfo(coffee);
        
        coffee = new WhipDecorator(coffee);
        printCoffeeInfo(coffee);
        
        coffee = new SugarDecorator(coffee);
        printCoffeeInfo(coffee);
        System.out.println();
        
        // 示例2: 通知服务装饰器模式
        System.out.println("2. 通知服务装饰器模式:");
        Notifier notifier = new EmailNotifier();
        notifier = new SMSDecorator(notifier);
        notifier = new FacebookDecorator(notifier);
        
        notifier.send("Hello World!");
        System.out.println();
        
        // 示例3: Web请求处理装饰器模式
        System.out.println("3. Web请求处理装饰器模式:");
        RequestHandler handler = new BasicHandler();
        handler = new LoggingDecorator(handler);
        handler = new AuthDecorator(handler);
        handler = new CacheDecorator(handler);
        handler = new CompressionDecorator(handler);
        
        System.out.println("处理带认证的请求:");
        String result1 = handler.handle("GET /api/data auth_token=abc123");
        System.out.println("Result: " + result1);
        System.out.println();
        
        System.out.println("处理不带认证的请求:");
        String result2 = handler.handle("GET /api/data");
        System.out.println("Result: " + result2);
        System.out.println();
        
        System.out.println("再次处理相同请求(测试缓存):");
        String result3 = handler.handle("GET /api/data auth_token=abc123");
        System.out.println("Result: " + result3);
        System.out.println();
        
        // 示例4: 图形界面组件装饰器模式
        System.out.println("4. 图形界面组件装饰器模式:");
        Graphic textView = new TextView("Hello Decorator!");
        textView = new BorderDecorator(textView);
        textView = new ScrollDecorator(textView);
        textView = new ColorDecorator(textView, "red");
        
        textView.draw();
        System.out.println();
    }
    
    private static void printCoffeeInfo(Coffee coffee) {
        System.out.println("Coffee: " + coffee.getDescription() + " | Cost: $" + coffee.getCost());
    }
}