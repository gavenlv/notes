import java.util.ArrayList;
import java.util.List;

/**
 * 第二十章 状态模式示例代码
 */

// ==================== 基本状态模式实现 ====================

// 抽象状态类
abstract class State {
    public abstract void handle(Context context);
}

// 具体状态A
class ConcreteStateA extends State {
    @Override
    public void handle(Context context) {
        System.out.println("处理状态A的逻辑");
        // 切换到状态B
        context.setState(new ConcreteStateB());
    }
}

// 具体状态B
class ConcreteStateB extends State {
    @Override
    public void handle(Context context) {
        System.out.println("处理状态B的逻辑");
        // 切换到状态A
        context.setState(new ConcreteStateA());
    }
}

// 上下文类
class Context {
    private State state;
    
    public Context() {
        // 初始化为状态A
        this.state = new ConcreteStateA();
    }
    
    public void setState(State state) {
        this.state = state;
    }
    
    public State getState() {
        return state;
    }
    
    public void request() {
        // 委托给当前状态处理
        state.handle(this);
    }
}

// ==================== 订单处理系统 ====================

// 订单状态接口
interface OrderState {
    void pay(OrderContext context);
    void cancel(OrderContext context);
    void ship(OrderContext context);
    void receive(OrderContext context);
    void complete(OrderContext context);
    String getStateName();
}

// 待支付状态
class UnpaidState implements OrderState {
    @Override
    public void pay(OrderContext context) {
        System.out.println("订单已支付");
        context.setState(new PaidState());
    }
    
    @Override
    public void cancel(OrderContext context) {
        System.out.println("订单已取消");
        context.setState(new CancelledState());
    }
    
    @Override
    public void ship(OrderContext context) {
        System.out.println("错误：未支付的订单不能发货");
    }
    
    @Override
    public void receive(OrderContext context) {
        System.out.println("错误：未支付的订单不能收货");
    }
    
    @Override
    public void complete(OrderContext context) {
        System.out.println("错误：未支付的订单不能完成");
    }
    
    @Override
    public String getStateName() {
        return "待支付";
    }
}

// 已支付状态
class PaidState implements OrderState {
    @Override
    public void pay(OrderContext context) {
        System.out.println("错误：订单已支付");
    }
    
    @Override
    public void cancel(OrderContext context) {
        System.out.println("订单已取消");
        context.setState(new CancelledState());
    }
    
    @Override
    public void ship(OrderContext context) {
        System.out.println("订单已发货");
        context.setState(new ShippedState());
    }
    
    @Override
    public void receive(OrderContext context) {
        System.out.println("错误：已支付但未发货的订单不能收货");
    }
    
    @Override
    public void complete(OrderContext context) {
        System.out.println("错误：已支付但未发货的订单不能完成");
    }
    
    @Override
    public String getStateName() {
        return "已支付";
    }
}

// 已发货状态
class ShippedState implements OrderState {
    @Override
    public void pay(OrderContext context) {
        System.out.println("错误：已发货的订单不能再次支付");
    }
    
    @Override
    public void cancel(OrderContext context) {
        System.out.println("错误：已发货的订单不能取消");
    }
    
    @Override
    public void ship(OrderContext context) {
        System.out.println("错误：订单已发货");
    }
    
    @Override
    public void receive(OrderContext context) {
        System.out.println("订单已收货");
        context.setState(new ReceivedState());
    }
    
    @Override
    public void complete(OrderContext context) {
        System.out.println("错误：未收货的订单不能完成");
    }
    
    @Override
    public String getStateName() {
        return "已发货";
    }
}

// 已收货状态
class ReceivedState implements OrderState {
    @Override
    public void pay(OrderContext context) {
        System.out.println("错误：已收货的订单不能支付");
    }
    
    @Override
    public void cancel(OrderContext context) {
        System.out.println("错误：已收货的订单不能取消");
    }
    
    @Override
    public void ship(OrderContext context) {
        System.out.println("错误：已收货的订单不能再次发货");
    }
    
    @Override
    public void receive(OrderContext context) {
        System.out.println("错误：订单已收货");
    }
    
    @Override
    public void complete(OrderContext context) {
        System.out.println("订单已完成");
        context.setState(new CompletedState());
    }
    
    @Override
    public String getStateName() {
        return "已收货";
    }
}

// 已完成状态
class CompletedState implements OrderState {
    @Override
    public void pay(OrderContext context) {
        System.out.println("错误：已完成的订单不能支付");
    }
    
    @Override
    public void cancel(OrderContext context) {
        System.out.println("错误：已完成的订单不能取消");
    }
    
    @Override
    public void ship(OrderContext context) {
        System.out.println("错误：已完成的订单不能发货");
    }
    
    @Override
    public void receive(OrderContext context) {
        System.out.println("错误：已完成的订单不能收货");
    }
    
    @Override
    public void complete(OrderContext context) {
        System.out.println("错误：订单已完成");
    }
    
    @Override
    public String getStateName() {
        return "已完成";
    }
}

// 已取消状态
class CancelledState implements OrderState {
    @Override
    public void pay(OrderContext context) {
        System.out.println("错误：已取消的订单不能支付");
    }
    
    @Override
    public void cancel(OrderContext context) {
        System.out.println("错误：订单已取消");
    }
    
    @Override
    public void ship(OrderContext context) {
        System.out.println("错误：已取消的订单不能发货");
    }
    
    @Override
    public void receive(OrderContext context) {
        System.out.println("错误：已取消的订单不能收货");
    }
    
    @Override
    public void complete(OrderContext context) {
        System.out.println("错误：已取消的订单不能完成");
    }
    
    @Override
    public String getStateName() {
        return "已取消";
    }
}

// 订单上下文
class OrderContext {
    private OrderState state;
    private String orderId;
    
    public OrderContext(String orderId) {
        this.orderId = orderId;
        // 默认状态为待支付
        this.state = new UnpaidState();
        System.out.println("创建订单: " + orderId + "，当前状态: " + state.getStateName());
    }
    
    public void setState(OrderState state) {
        this.state = state;
        System.out.println("订单 " + orderId + " 状态变更为: " + state.getStateName());
    }
    
    public OrderState getState() {
        return state;
    }
    
    public String getOrderId() {
        return orderId;
    }
    
    // 支付订单
    public void pay() {
        System.out.println("尝试支付订单 " + orderId);
        state.pay(this);
    }
    
    // 取消订单
    public void cancel() {
        System.out.println("尝试取消订单 " + orderId);
        state.cancel(this);
    }
    
    // 发货
    public void ship() {
        System.out.println("尝试发货订单 " + orderId);
        state.ship(this);
    }
    
    // 收货
    public void receive() {
        System.out.println("尝试收货订单 " + orderId);
        state.receive(this);
    }
    
    // 完成订单
    public void complete() {
        System.out.println("尝试完成订单 " + orderId);
        state.complete(this);
    }
}

// ==================== 交通信号灯示例 ====================

// 交通信号灯状态接口
interface TrafficLightState {
    void handle(TrafficLightContext context);
    String getColor();
}

// 红灯状态
class RedLightState implements TrafficLightState {
    @Override
    public void handle(TrafficLightContext context) {
        System.out.println("红灯亮起，车辆停止通行...");
        // 模拟等待时间
        try {
            Thread.sleep(1000); // 减少等待时间用于演示
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // 切换到绿灯
        context.setState(new GreenLightState());
    }
    
    @Override
    public String getColor() {
        return "红色";
    }
}

// 绿灯状态
class GreenLightState implements TrafficLightState {
    @Override
    public void handle(TrafficLightContext context) {
        System.out.println("绿灯亮起，车辆可以通行...");
        // 模拟等待时间
        try {
            Thread.sleep(1000); // 减少等待时间用于演示
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // 切换到黄灯
        context.setState(new YellowLightState());
    }
    
    @Override
    public String getColor() {
        return "绿色";
    }
}

// 黄灯状态
class YellowLightState implements TrafficLightState {
    @Override
    public void handle(TrafficLightContext context) {
        System.out.println("黄灯亮起，准备变换信号...");
        // 模拟等待时间
        try {
            Thread.sleep(1000); // 减少等待时间用于演示
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        // 切换到红灯
        context.setState(new RedLightState());
    }
    
    @Override
    public String getColor() {
        return "黄色";
    }
}

// 交通信号灯上下文
class TrafficLightContext {
    private TrafficLightState state;
    
    public TrafficLightContext() {
        // 初始状态为红灯
        this.state = new RedLightState();
    }
    
    public void setState(TrafficLightState state) {
        this.state = state;
    }
    
    public TrafficLightState getState() {
        return state;
    }
    
    public void change() {
        System.out.println("当前信号灯颜色: " + state.getColor());
        state.handle(this);
    }
}

// ==================== 主类 ====================
public class Chapter20Example {
    public static void main(String[] args) {
        System.out.println("=== 状态模式示例 ===\n");
        
        // 基本状态模式示例
        basicStateExample();
        
        System.out.println("\n=== 订单处理系统示例 ===\n");
        orderProcessingExample();
        
        System.out.println("\n=== 交通信号灯示例 ===\n");
        trafficLightExample();
    }
    
    /**
     * 基本状态模式示例
     */
    public static void basicStateExample() {
        System.out.println("1. 基本状态模式示例:");
        Context context = new Context();
        
        // 执行多次请求，观察状态切换
        for (int i = 0; i < 5; i++) {
            System.out.println("第" + (i+1) + "次请求:");
            context.request();
            System.out.println();
        }
    }
    
    /**
     * 订单处理系统示例
     */
    public static void orderProcessingExample() {
        System.out.println("2. 订单处理系统示例:");
        // 创建订单
        OrderContext order = new OrderContext("ORD20230701001");
        
        // 尝试操作
        order.pay();      // 支付
        order.ship();     // 发货
        order.receive();  // 收货
        order.complete(); // 完成
        
        System.out.println("\n--- 测试异常状态转换 ---");
        OrderContext order2 = new OrderContext("ORD20230701002");
        order2.cancel();  // 取消订单
        order2.ship();    // 尝试对已取消订单发货
    }
    
    /**
     * 交通信号灯示例
     */
    public static void trafficLightExample() {
        System.out.println("3. 交通信号灯示例:");
        TrafficLightContext light = new TrafficLightContext();
        
        // 模拟几个周期的信号灯变化
        for (int i = 0; i < 6; i++) {
            light.change();
            System.out.println();
        }
    }
}