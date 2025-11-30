// Chapter8Example.java - 桥接模式代码示例

// 实现化角色 - 绘图API
interface DrawAPI {
    void drawCircle(int radius, int x, int y);
}

// 具体实现化角色 - 红色圆形绘制
class RedCircle implements DrawAPI {
    @Override
    public void drawCircle(int radius, int x, int y) {
        System.out.println("Drawing Circle[ color: red, radius: " + radius + ", x: " + x + ", y: " + y + "]");
    }
}

// 具体实现化角色 - 绿色圆形绘制
class GreenCircle implements DrawAPI {
    @Override
    public void drawCircle(int radius, int x, int y) {
        System.out.println("Drawing Circle[ color: green, radius: " + radius + ", x: " + x + ", y: " + y + "]");
    }
}

// 抽象化角色 - 形状抽象类
abstract class Shape {
    protected DrawAPI drawAPI;
    
    protected Shape(DrawAPI drawAPI) {
        this.drawAPI = drawAPI;
    }
    
    public abstract void draw();
}

// 扩充抽象化角色 - 圆形
class Circle extends Shape {
    private int x, y, radius;
    
    public Circle(int x, int y, int radius, DrawAPI drawAPI) {
        super(drawAPI);
        this.x = x;
        this.y = y;
        this.radius = radius;
    }
    
    @Override
    public void draw() {
        drawAPI.drawCircle(radius, x, y);
    }
}

// 实现化角色 - 设备接口
interface Device {
    boolean isEnabled();
    void enable();
    void disable();
    int getVolume();
    void setVolume(int percent);
    int getChannel();
    void setChannel(int channel);
    void printStatus();
}

// 具体实现化角色 - 收音机
class Radio implements Device {
    private boolean on = false;
    private int volume = 30;
    private int channel = 1;
    
    @Override
    public boolean isEnabled() {
        return on;
    }
    
    @Override
    public void enable() {
        on = true;
    }
    
    @Override
    public void disable() {
        on = false;
    }
    
    @Override
    public int getVolume() {
        return volume;
    }
    
    @Override
    public void setVolume(int percent) {
        if (percent > 100) {
            this.volume = 100;
        } else if (percent < 0) {
            this.volume = 0;
        } else {
            this.volume = percent;
        }
    }
    
    @Override
    public int getChannel() {
        return channel;
    }
    
    @Override
    public void setChannel(int channel) {
        this.channel = channel;
    }
    
    @Override
    public void printStatus() {
        System.out.println("------------------------------------");
        System.out.println("| I'm radio.");
        System.out.println("| I'm " + (on ? "enabled" : "disabled"));
        System.out.println("| Current volume is " + volume + "%");
        System.out.println("| Current channel is " + channel);
        System.out.println("------------------------------------\n");
    }
}

// 具体实现化角色 - 电视机
class Tv implements Device {
    private boolean on = false;
    private int volume = 30;
    private int channel = 1;
    
    @Override
    public boolean isEnabled() {
        return on;
    }
    
    @Override
    public void enable() {
        on = true;
    }
    
    @Override
    public void disable() {
        on = false;
    }
    
    @Override
    public int getVolume() {
        return volume;
    }
    
    @Override
    public void setVolume(int percent) {
        if (percent > 100) {
            this.volume = 100;
        } else if (percent < 0) {
            this.volume = 0;
        } else {
            this.volume = percent;
        }
    }
    
    @Override
    public int getChannel() {
        return channel;
    }
    
    @Override
    public void setChannel(int channel) {
        this.channel = channel;
    }
    
    @Override
    public void printStatus() {
        System.out.println("------------------------------------");
        System.out.println("| I'm TV set.");
        System.out.println("| I'm " + (on ? "enabled" : "disabled"));
        System.out.println("| Current volume is " + volume + "%");
        System.out.println("| Current channel is " + channel);
        System.out.println("------------------------------------\n");
    }
}

// 抽象化角色 - 远程控制器
abstract class RemoteControl {
    protected Device device;
    
    protected RemoteControl(Device device) {
        this.device = device;
    }
    
    public void togglePower() {
        if (device.isEnabled()) {
            device.disable();
        } else {
            device.enable();
        }
    }
    
    public void volumeDown() {
        device.setVolume(device.getVolume() - 10);
    }
    
    public void volumeUp() {
        device.setVolume(device.getVolume() + 10);
    }
    
    public void channelDown() {
        device.setChannel(device.getChannel() - 1);
    }
    
    public void channelUp() {
        device.setChannel(device.getChannel() + 1);
    }
    
    public abstract void mute();
}

// 扩充抽象化角色 - 基础远程控制器
class BasicRemote extends RemoteControl {
    public BasicRemote(Device device) {
        super(device);
    }
    
    @Override
    public void mute() {
        device.setVolume(0);
    }
}

// 扩充抽象化角色 - 高级远程控制器
class AdvancedRemote extends BasicRemote {
    public AdvancedRemote(Device device) {
        super(device);
    }
    
    @Override
    public void mute() {
        device.setVolume(0);
    }
    
    public void setChannel(int channel) {
        device.setChannel(channel);
    }
}

// 实现化角色 - 操作系统绘图接口
interface OSRenderer {
    void renderButton(String text);
    void renderTextBox(String text);
    void renderDialog(String title);
}

// 具体实现化角色 - Windows渲染器
class WindowsRenderer implements OSRenderer {
    @Override
    public void renderButton(String text) {
        System.out.println("Windows风格按钮: [" + text + "]");
    }
    
    @Override
    public void renderTextBox(String text) {
        System.out.println("Windows风格文本框: [" + text + "]");
    }
    
    @Override
    public void renderDialog(String title) {
        System.out.println("Windows风格对话框: {" + title + "}");
    }
}

// 具体实现化角色 - Mac渲染器
class MacRenderer implements OSRenderer {
    @Override
    public void renderButton(String text) {
        System.out.println("Mac风格按钮: [" + text + "]");
    }
    
    @Override
    public void renderTextBox(String text) {
        System.out.println("Mac风格文本框: [" + text + "]");
    }
    
    @Override
    public void renderDialog(String title) {
        System.out.println("Mac风格对话框: {" + title + "}");
    }
}

// 抽象化角色 - UI组件抽象类
abstract class UIComponent {
    protected OSRenderer renderer;
    
    protected UIComponent(OSRenderer renderer) {
        this.renderer = renderer;
    }
    
    public abstract void display();
}

// 扩充抽象化角色 - 按钮组件
class Button extends UIComponent {
    private String text;
    
    public Button(OSRenderer renderer, String text) {
        super(renderer);
        this.text = text;
    }
    
    @Override
    public void display() {
        renderer.renderButton(text);
    }
}

// 扩充抽象化角色 - 文本框组件
class TextBox extends UIComponent {
    private String text;
    
    public TextBox(OSRenderer renderer, String text) {
        super(renderer);
        this.text = text;
    }
    
    @Override
    public void display() {
        renderer.renderTextBox(text);
    }
}

// 扩充抽象化角色 - 对话框组件
class Dialog extends UIComponent {
    private String title;
    
    public Dialog(OSRenderer renderer, String title) {
        super(renderer);
        this.title = title;
    }
    
    @Override
    public void display() {
        renderer.renderDialog(title);
    }
}

// 实现化角色 - 数据库驱动接口
interface DatabaseDriver {
    void connect();
    void executeQuery(String sql);
    void executeUpdate(String sql);
    void close();
}

// 具体实现化角色 - MySQL驱动
class MySQLDriverImpl implements DatabaseDriver {
    @Override
    public void connect() {
        System.out.println("连接到MySQL数据库");
    }
    
    @Override
    public void executeQuery(String sql) {
        System.out.println("MySQL查询: " + sql);
    }
    
    @Override
    public void executeUpdate(String sql) {
        System.out.println("MySQL更新: " + sql);
    }
    
    @Override
    public void close() {
        System.out.println("关闭MySQL连接");
    }
}

// 具体实现化角色 - PostgreSQL驱动
class PostgreSQLDriverImpl implements DatabaseDriver {
    @Override
    public void connect() {
        System.out.println("连接到PostgreSQL数据库");
    }
    
    @Override
    public void executeQuery(String sql) {
        System.out.println("PostgreSQL查询: " + sql);
    }
    
    @Override
    public void executeUpdate(String sql) {
        System.out.println("PostgreSQL更新: " + sql);
    }
    
    @Override
    public void close() {
        System.out.println("关闭PostgreSQL连接");
    }
}

// 抽象化角色 - 数据访问对象
abstract class DAO {
    protected DatabaseDriver driver;
    
    protected DAO(DatabaseDriver driver) {
        this.driver = driver;
    }
    
    public abstract void save(Object entity);
    public abstract Object findById(int id);
    public abstract void delete(int id);
}

// 扩充抽象化角色 - 用户DAO
class UserDAO extends DAO {
    public UserDAO(DatabaseDriver driver) {
        super(driver);
    }
    
    @Override
    public void save(Object entity) {
        driver.connect();
        driver.executeUpdate("INSERT INTO users VALUES (...)");
        driver.close();
    }
    
    @Override
    public Object findById(int id) {
        driver.connect();
        driver.executeQuery("SELECT * FROM users WHERE id = " + id);
        driver.close();
        return new Object(); // 简化示例
    }
    
    @Override
    public void delete(int id) {
        driver.connect();
        driver.executeUpdate("DELETE FROM users WHERE id = " + id);
        driver.close();
    }
}

// 扩充抽象化角色 - 产品DAO
class ProductDAO extends DAO {
    public ProductDAO(DatabaseDriver driver) {
        super(driver);
    }
    
    @Override
    public void save(Object entity) {
        driver.connect();
        driver.executeUpdate("INSERT INTO products VALUES (...)");
        driver.close();
    }
    
    @Override
    public Object findById(int id) {
        driver.connect();
        driver.executeQuery("SELECT * FROM products WHERE id = " + id);
        driver.close();
        return new Object(); // 简化示例
    }
    
    @Override
    public void delete(int id) {
        driver.connect();
        driver.executeUpdate("DELETE FROM products WHERE id = " + id);
        driver.close();
    }
}

// 主类 - 演示桥接模式的各种应用
public class Chapter8Example {
    public static void main(String[] args) {
        System.out.println("=== 桥接模式示例 ===\n");
        
        // 示例1: 图形绘制桥接模式
        System.out.println("1. 图形绘制桥接模式:");
        Shape redCircle = new Circle(100, 100, 10, new RedCircle());
        Shape greenCircle = new Circle(100, 100, 10, new GreenCircle());
        
        redCircle.draw();
        greenCircle.draw();
        System.out.println();
        
        // 示例2: 设备遥控器桥接模式
        System.out.println("2. 设备遥控器桥接模式:");
        testDevice(new Tv());
        testDevice(new Radio());
        System.out.println();
        
        // 示例3: 跨平台UI组件桥接模式
        System.out.println("3. 跨平台UI组件桥接模式:");
        UIComponent winButton = new Button(new WindowsRenderer(), "确定");
        UIComponent macButton = new Button(new MacRenderer(), "确定");
        UIComponent winDialog = new Dialog(new WindowsRenderer(), "提示");
        UIComponent macDialog = new Dialog(new MacRenderer(), "提示");
        
        winButton.display();
        macButton.display();
        winDialog.display();
        macDialog.display();
        System.out.println();
        
        // 示例4: 数据库访问桥接模式
        System.out.println("4. 数据库访问桥接模式:");
        DAO userDAO = new UserDAO(new MySQLDriverImpl());
        DAO productDAO = new ProductDAO(new PostgreSQLDriverImpl());
        
        userDAO.save(new Object());
        productDAO.findById(1);
        System.out.println();
    }
    
    public static void testDevice(Device device) {
        System.out.println("测试设备类型: " + device.getClass().getSimpleName());
        BasicRemote basicRemote = new BasicRemote(device);
        basicRemote.togglePower();
        basicRemote.volumeUp();
        basicRemote.channelUp();
        device.printStatus();
        
        AdvancedRemote advancedRemote = new AdvancedRemote(device);
        advancedRemote.mute();
        device.printStatus();
    }
}