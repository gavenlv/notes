// Chapter10Example.java - 外观模式示例代码

// 子系统类 - CPU
class CPU {
    public void freeze() {
        System.out.println("CPU: Freezing processor.");
    }
    
    public void jump(long position) {
        System.out.println("CPU: Jumping to position " + position);
    }
    
    public void execute() {
        System.out.println("CPU: Executing instructions.");
    }
}

// 子系统类 - 内存
class Memory {
    public void load(long position, byte[] data) {
        System.out.println("Memory: Loading data at position " + position);
    }
}

// 子系统类 - 硬盘
class HardDrive {
    public byte[] read(long lba, int size) {
        System.out.println("HardDrive: Reading " + size + " bytes from LBA " + lba);
        return new byte[size];
    }
}

// 外观类 - 计算机启动器
class ComputerFacade {
    private CPU cpu;
    private Memory memory;
    private HardDrive hardDrive;
    
    public ComputerFacade() {
        this.cpu = new CPU();
        this.memory = new Memory();
        this.hardDrive = new HardDrive();
    }
    
    public void start() {
        System.out.println("ComputerFacade: Starting computer...");
        cpu.freeze();
        memory.load(0, hardDrive.read(0, 1024));
        cpu.jump(0);
        cpu.execute();
        System.out.println("ComputerFacade: Computer started successfully.");
    }
    
    public void shutdown() {
        System.out.println("ComputerFacade: Shutting down computer...");
        // 关闭逻辑
        System.out.println("ComputerFacade: Computer shut down successfully.");
    }
}

// 子系统类 - DVD播放器
class DvdPlayer {
    public void on() {
        System.out.println("DVD Player is on");
    }
    
    public void play(String movie) {
        System.out.println("DVD Player playing \"" + movie + "\"");
    }
    
    public void stop() {
        System.out.println("DVD Player stopped");
    }
    
    public void eject() {
        System.out.println("DVD Player eject");
    }
    
    public void off() {
        System.out.println("DVD Player is off");
    }
}

// 子系统类 - 投影仪
class Projector {
    public void on() {
        System.out.println("Projector is on");
    }
    
    public void wideScreenMode() {
        System.out.println("Projector in widescreen mode (16x9 aspect ratio)");
    }
    
    public void off() {
        System.out.println("Projector is off");
    }
}

// 子系统类 - 音响功放
class Amplifier {
    public void on() {
        System.out.println("Amplifier is on");
    }
    
    public void setDvd(DvdPlayer dvd) {
        System.out.println("Amplifier setting DVD player");
    }
    
    public void setSurroundSound() {
        System.out.println("Amplifier setting surround sound");
    }
    
    public void setVolume(int level) {
        System.out.println("Amplifier setting volume to " + level);
    }
    
    public void off() {
        System.out.println("Amplifier is off");
    }
}

// 子系统类 - 屏幕
class Screen {
    public void down() {
        System.out.println("Screen is going down");
    }
    
    public void up() {
        System.out.println("Screen is going up");
    }
}

// 子系统类 - 灯光
class TheaterLights {
    public void dim(int level) {
        System.out.println("Theater Ceiling Lights dimming to " + level + "%");
    }
    
    public void on() {
        System.out.println("Theater Ceiling Lights on");
    }
    
    public void off() {
        System.out.println("Theater Ceiling Lights off");
    }
}

// 子系统类 - 爆米花机
class PopcornPopper {
    public void on() {
        System.out.println("Popcorn Popper is on");
    }
    
    public void pop() {
        System.out.println("Popcorn Popper popping popcorn!");
    }
    
    public void off() {
        System.out.println("Popcorn Popper is off");
    }
}

// 外观类 - 家庭影院外观
class HomeTheaterFacade {
    private Amplifier amp;
    private DvdPlayer dvd;
    private Projector projector;
    private Screen screen;
    private TheaterLights lights;
    private PopcornPopper popper;
    
    public HomeTheaterFacade() {
        this.amp = new Amplifier();
        this.dvd = new DvdPlayer();
        this.projector = new Projector();
        this.screen = new Screen();
        this.lights = new TheaterLights();
        this.popper = new PopcornPopper();
    }
    
    public void watchMovie(String movie) {
        System.out.println("Get ready to watch a movie...");
        popper.on();
        popper.pop();
        lights.dim(10);
        screen.down();
        projector.on();
        projector.wideScreenMode();
        amp.on();
        amp.setDvd(dvd);
        amp.setSurroundSound();
        amp.setVolume(5);
        dvd.on();
        dvd.play(movie);
    }
    
    public void endMovie() {
        System.out.println("Shutting movie theater down...");
        popper.off();
        lights.on();
        screen.up();
        projector.off();
        amp.off();
        dvd.stop();
        dvd.eject();
        dvd.off();
    }
}

// 子系统类 - 连接管理器
class ConnectionManager {
    public void connect() {
        System.out.println("Connecting to database...");
    }
    
    public void disconnect() {
        System.out.println("Disconnecting from database...");
    }
}

// 子系统类 - 查询构建器
class QueryBuilder {
    public String buildSelectQuery(String table, String[] columns, String condition) {
        StringBuilder query = new StringBuilder("SELECT ");
        for (int i = 0; i < columns.length; i++) {
            query.append(columns[i]);
            if (i < columns.length - 1) {
                query.append(", ");
            }
        }
        query.append(" FROM ").append(table);
        if (condition != null && !condition.isEmpty()) {
            query.append(" WHERE ").append(condition);
        }
        return query.toString();
    }
}

// 子系统类 - 结果集处理器
class ResultSetProcessor {
    public void processResults(String queryResult) {
        System.out.println("Processing query results: " + queryResult);
    }
}

// 子系统类 - 事务管理器
class TransactionManager {
    public void beginTransaction() {
        System.out.println("Beginning transaction...");
    }
    
    public void commitTransaction() {
        System.out.println("Committing transaction...");
    }
    
    public void rollbackTransaction() {
        System.out.println("Rolling back transaction...");
    }
}

// 外观类 - 数据库访问外观
class DatabaseFacade {
    private ConnectionManager connectionManager;
    private QueryBuilder queryBuilder;
    private ResultSetProcessor resultSetProcessor;
    private TransactionManager transactionManager;
    
    public DatabaseFacade() {
        this.connectionManager = new ConnectionManager();
        this.queryBuilder = new QueryBuilder();
        this.resultSetProcessor = new ResultSetProcessor();
        this.transactionManager = new TransactionManager();
    }
    
    public void executeQuery(String table, String[] columns, String condition) {
        System.out.println("Executing database query through facade...");
        connectionManager.connect();
        transactionManager.beginTransaction();
        
        String query = queryBuilder.buildSelectQuery(table, columns, condition);
        System.out.println("Executing query: " + query);
        
        // 模拟查询执行和结果处理
        String result = "Sample query result";
        resultSetProcessor.processResults(result);
        
        transactionManager.commitTransaction();
        connectionManager.disconnect();
        System.out.println("Query executed successfully.\n");
    }
}

// 子系统类 - 库存管理
class InventoryService {
    public boolean checkStock(String productId, int quantity) {
        System.out.println("Checking stock for product " + productId + ": " + quantity + " units");
        // 模拟库存检查
        return true;
    }
    
    public void reserveStock(String productId, int quantity) {
        System.out.println("Reserving " + quantity + " units of product " + productId);
    }
    
    public void releaseStock(String productId, int quantity) {
        System.out.println("Releasing " + quantity + " units of product " + productId);
    }
}

// 子系统类 - 支付处理
class PaymentService {
    public boolean processPayment(double amount, String paymentMethod) {
        System.out.println("Processing payment of $" + amount + " using " + paymentMethod);
        // 模拟支付处理
        return true;
    }
    
    public void refundPayment(double amount) {
        System.out.println("Refunding $" + amount);
    }
}

// 子系统类 - 订单管理
class OrderService {
    public String createOrder(String customerId, String[] products) {
        System.out.println("Creating order for customer " + customerId);
        // 模拟订单创建
        return "ORDER-" + System.currentTimeMillis();
    }
    
    public void confirmOrder(String orderId) {
        System.out.println("Confirming order " + orderId);
    }
    
    public void cancelOrder(String orderId) {
        System.out.println("Canceling order " + orderId);
    }
}

// 子系统类 - 物流配送
class ShippingService {
    public String arrangeShipping(String orderId, String address) {
        System.out.println("Arranging shipping for order " + orderId + " to " + address);
        // 模拟物流安排
        return "SHIPPING-" + System.currentTimeMillis();
    }
    
    public void trackShipment(String trackingId) {
        System.out.println("Tracking shipment " + trackingId);
    }
}

// 外观类 - 订单处理外观
class OrderProcessingFacade {
    private InventoryService inventoryService;
    private PaymentService paymentService;
    private OrderService orderService;
    private ShippingService shippingService;
    
    public OrderProcessingFacade() {
        this.inventoryService = new InventoryService();
        this.paymentService = new PaymentService();
        this.orderService = new OrderService();
        this.shippingService = new ShippingService();
    }
    
    public String placeOrder(String customerId, String[] products, 
                            int[] quantities, double amount, 
                            String paymentMethod, String shippingAddress) {
        System.out.println("=== Placing Order ===");
        
        // 1. 检查库存
        for (int i = 0; i < products.length; i++) {
            if (!inventoryService.checkStock(products[i], quantities[i])) {
                System.out.println("Insufficient stock for product " + products[i]);
                return null;
            }
        }
        
        // 2. 预留库存
        for (int i = 0; i < products.length; i++) {
            inventoryService.reserveStock(products[i], quantities[i]);
        }
        
        // 3. 创建订单
        String orderId = orderService.createOrder(customerId, products);
        
        // 4. 处理支付
        if (!paymentService.processPayment(amount, paymentMethod)) {
            System.out.println("Payment failed, canceling order");
            orderService.cancelOrder(orderId);
            // 释放预留的库存
            for (int i = 0; i < products.length; i++) {
                inventoryService.releaseStock(products[i], quantities[i]);
            }
            return null;
        }
        
        // 5. 确认订单
        orderService.confirmOrder(orderId);
        
        // 6. 安排物流
        String trackingId = shippingService.arrangeShipping(orderId, shippingAddress);
        
        System.out.println("Order placed successfully!");
        System.out.println("Order ID: " + orderId);
        System.out.println("Tracking ID: " + trackingId);
        System.out.println("=====================\n");
        
        return orderId;
    }
}

// 主类 - 演示外观模式
public class Chapter10Example {
    public static void main(String[] args) {
        System.out.println("=== 第十章 外观模式示例 ===\n");
        
        // 示例1: 计算机启动外观
        System.out.println("1. 计算机启动外观示例:");
        ComputerFacade computer = new ComputerFacade();
        computer.start();
        System.out.println();
        
        // 示例2: 家庭影院外观
        System.out.println("2. 家庭影院外观示例:");
        HomeTheaterFacade homeTheater = new HomeTheaterFacade();
        homeTheater.watchMovie("Inception");
        homeTheater.endMovie();
        System.out.println();
        
        // 示例3: 数据库访问外观
        System.out.println("3. 数据库访问外观示例:");
        DatabaseFacade dbFacade = new DatabaseFacade();
        String[] columns = {"id", "name", "email"};
        dbFacade.executeQuery("users", columns, "age > 18");
        System.out.println();
        
        // 示例4: 订单处理外观
        System.out.println("4. 订单处理外观示例:");
        OrderProcessingFacade orderFacade = new OrderProcessingFacade();
        String[] products = {"Product-A", "Product-B"};
        int[] quantities = {2, 1};
        orderFacade.placeOrder("Customer-123", products, quantities, 99.99, "Credit Card", "123 Main St");
    }
}