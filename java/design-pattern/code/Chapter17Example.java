import java.util.*;

// 抽象中介者
abstract class Mediator {
    public abstract void sendMessage(String message, Colleague colleague);
}

// 抽象同事类
abstract class Colleague {
    protected Mediator mediator;
    
    public Colleague(Mediator mediator) {
        this.mediator = mediator;
    }
    
    public abstract void receiveMessage(String message);
    public abstract void sendMessage(String message);
}

// 具体中介者
class ConcreteMediator extends Mediator {
    private Colleague colleague1;
    private Colleague colleague2;
    
    public void setColleague1(Colleague colleague1) {
        this.colleague1 = colleague1;
    }
    
    public void setColleague2(Colleague colleague2) {
        this.colleague2 = colleague2;
    }
    
    @Override
    public void sendMessage(String message, Colleague colleague) {
        if (colleague == colleague1) {
            colleague2.receiveMessage(message);
        } else {
            colleague1.receiveMessage(message);
        }
    }
}

// 具体同事类1
class ConcreteColleague1 extends Colleague {
    public ConcreteColleague1(Mediator mediator) {
        super(mediator);
    }
    
    @Override
    public void receiveMessage(String message) {
        System.out.println("ConcreteColleague1收到消息: " + message);
    }
    
    @Override
    public void sendMessage(String message) {
        System.out.println("ConcreteColleague1发送消息: " + message);
        mediator.sendMessage(message, this);
    }
}

// 具体同事类2
class ConcreteColleague2 extends Colleague {
    public ConcreteColleague2(Mediator mediator) {
        super(mediator);
    }
    
    @Override
    public void receiveMessage(String message) {
        System.out.println("ConcreteColleague2收到消息: " + message);
    }
    
    @Override
    public void sendMessage(String message) {
        System.out.println("ConcreteColleague2发送消息: " + message);
        mediator.sendMessage(message, this);
    }
}

// 用户类（聊天室示例）
class User {
    private String name;
    private ChatRoom chatRoom;
    
    public User(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
    
    public void setChatRoom(ChatRoom chatRoom) {
        this.chatRoom = chatRoom;
    }
    
    // 发送消息给所有人
    public void sendMessage(String message) {
        if (chatRoom != null) {
            chatRoom.sendMessage(this, message);
        }
    }
    
    // 发送私信
    public void sendPrivateMessage(User toUser, String message) {
        if (chatRoom != null) {
            chatRoom.sendPrivateMessage(this, toUser, message);
        }
    }
    
    // 接收消息
    public void receiveMessage(User fromUser, String message) {
        System.out.println("[" + name + "] 收到来自 [" + fromUser.getName() + "] 的消息: " + message);
    }
    
    // 接收私信
    public void receivePrivateMessage(User fromUser, String message) {
        System.out.println("[" + name + "] 收到来自 [" + fromUser.getName() + "] 的私信: " + message);
    }
}

// 聊天室中介者
class ChatRoom {
    private List<User> users;
    
    public ChatRoom() {
        this.users = new ArrayList<>();
    }
    
    // 添加用户
    public void addUser(User user) {
        users.add(user);
        user.setChatRoom(this);
    }
    
    // 发送消息给所有用户
    public void sendMessage(User fromUser, String message) {
        System.out.println("[聊天室] " + fromUser.getName() + ": " + message);
        for (User user : users) {
            if (user != fromUser) {
                user.receiveMessage(fromUser, message);
            }
        }
    }
    
    // 发送私信
    public void sendPrivateMessage(User fromUser, User toUser, String message) {
        System.out.println("[私信] " + fromUser.getName() + " -> " + toUser.getName() + ": " + message);
        toUser.receivePrivateMessage(fromUser, message);
    }
}

// GUI组件基类
abstract class Component {
    protected MediatorGUI mediator;
    
    public Component(MediatorGUI mediator) {
        this.mediator = mediator;
    }
    
    public abstract void update();
    public abstract void click();
}

// 按钮组件
class Button extends Component {
    private String text;
    private boolean enabled;
    
    public Button(MediatorGUI mediator, String text) {
        super(mediator);
        this.text = text;
        this.enabled = true;
    }
    
    public void setText(String text) {
        this.text = text;
    }
    
    public String getText() {
        return text;
    }
    
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
    
    public boolean isEnabled() {
        return enabled;
    }
    
    @Override
    public void update() {
        System.out.println("按钮 [" + text + "] 状态更新");
    }
    
    @Override
    public void click() {
        if (enabled) {
            System.out.println("点击按钮 [" + text + "]");
            mediator.buttonClicked(this);
        } else {
            System.out.println("按钮 [" + text + "] 已禁用，无法点击");
        }
    }
}

// 文本框组件
class TextBox extends Component {
    private String text;
    private boolean enabled;
    
    public TextBox(MediatorGUI mediator) {
        super(mediator);
        this.text = "";
        this.enabled = true;
    }
    
    public void setText(String text) {
        if (enabled) {
            this.text = text;
            System.out.println("文本框内容设置为: " + text);
            mediator.textBoxChanged(this);
        }
    }
    
    public String getText() {
        return text;
    }
    
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
    
    public boolean isEnabled() {
        return enabled;
    }
    
    @Override
    public void update() {
        System.out.println("文本框内容更新");
    }
    
    @Override
    public void click() {
        System.out.println("点击文本框");
        mediator.textBoxClicked(this);
    }
}

// 标签组件
class Label extends Component {
    private String text;
    
    public Label(MediatorGUI mediator, String text) {
        super(mediator);
        this.text = text;
    }
    
    public void setText(String text) {
        this.text = text;
        System.out.println("标签内容更新为: " + text);
    }
    
    public String getText() {
        return text;
    }
    
    @Override
    public void update() {
        System.out.println("标签 [" + text + "] 更新");
    }
    
    @Override
    public void click() {
        System.out.println("点击标签 [" + text + "]");
        mediator.labelClicked(this);
    }
}

// GUI中介者
class MediatorGUI {
    private Button loginButton;
    private Button logoutButton;
    private TextBox usernameTextBox;
    private TextBox passwordTextBox;
    private Label statusLabel;
    
    public void setLoginButton(Button loginButton) {
        this.loginButton = loginButton;
    }
    
    public void setLogoutButton(Button logoutButton) {
        this.logoutButton = logoutButton;
    }
    
    public void setUsernameTextBox(TextBox usernameTextBox) {
        this.usernameTextBox = usernameTextBox;
    }
    
    public void setPasswordTextBox(TextBox passwordTextBox) {
        this.passwordTextBox = passwordTextBox;
    }
    
    public void setStatusLabel(Label statusLabel) {
        this.statusLabel = statusLabel;
    }
    
    // 按钮点击事件处理
    public void buttonClicked(Button button) {
        if (button == loginButton) {
            handleLogin();
        } else if (button == logoutButton) {
            handleLogout();
        }
    }
    
    // 文本框内容变化事件处理
    public void textBoxChanged(TextBox textBox) {
        if (textBox == usernameTextBox || textBox == passwordTextBox) {
            // 检查用户名和密码是否为空来启用/禁用登录按钮
            boolean hasUsername = usernameTextBox.getText() != null && !usernameTextBox.getText().isEmpty();
            boolean hasPassword = passwordTextBox.getText() != null && !passwordTextBox.getText().isEmpty();
            loginButton.setEnabled(hasUsername && hasPassword);
        }
    }
    
    // 文本框点击事件处理
    public void textBoxClicked(TextBox textBox) {
        // 文本框被点击时的处理逻辑
        System.out.println("文本框被点击");
    }
    
    // 标签点击事件处理
    public void labelClicked(Label label) {
        // 标签被点击时的处理逻辑
        System.out.println("标签被点击");
    }
    
    // 登录处理
    private void handleLogin() {
        String username = usernameTextBox.getText();
        String password = passwordTextBox.getText();
        
        // 简单的登录验证
        if ("admin".equals(username) && "123456".equals(password)) {
            statusLabel.setText("登录成功");
            loginButton.setEnabled(false);
            logoutButton.setEnabled(true);
            usernameTextBox.setEnabled(false);
            passwordTextBox.setEnabled(false);
        } else {
            statusLabel.setText("登录失败：用户名或密码错误");
        }
    }
    
    // 登出处理
    private void handleLogout() {
        statusLabel.setText("已登出");
        loginButton.setEnabled(true);
        logoutButton.setEnabled(false);
        usernameTextBox.setEnabled(true);
        passwordTextBox.setEnabled(true);
        usernameTextBox.setText("");
        passwordTextBox.setText("");
    }
}

// 飞机类（飞机管制系统示例）
class Aircraft {
    private String callSign;
    private int altitude;
    private int speed;
    private AirTrafficControl atc;
    
    public Aircraft(String callSign, AirTrafficControl atc) {
        this.callSign = callSign;
        this.atc = atc;
        this.altitude = 0;
        this.speed = 0;
    }
    
    public String getCallSign() {
        return callSign;
    }
    
    public int getAltitude() {
        return altitude;
    }
    
    public void setAltitude(int altitude) {
        this.altitude = altitude;
        // 通知ATC高度变化
        atc.notifyAltitudeChange(this);
    }
    
    public int getSpeed() {
        return speed;
    }
    
    public void setSpeed(int speed) {
        this.speed = speed;
        // 通知ATC速度变化
        atc.notifySpeedChange(this);
    }
    
    // 接收来自其他飞机的消息
    public void receiveMessage(Aircraft from, String message) {
        System.out.println("[" + callSign + "] 收到来自 [" + from.getCallSign() + "] 的消息: " + message);
    }
    
    // 发送消息给其他飞机
    public void sendMessage(Aircraft to, String message) {
        atc.sendMessage(this, to, message);
    }
    
    // 接收ATC指令
    public void receiveATCInstruction(String instruction) {
        System.out.println("[" + callSign + "] 收到ATC指令: " + instruction);
    }
}

// 空中交通管制中心
class AirTrafficControl {
    private List<Aircraft> aircrafts;
    private Map<Aircraft, Integer> altitudes;
    private Map<Aircraft, Integer> speeds;
    
    public AirTrafficControl() {
        this.aircrafts = new ArrayList<>();
        this.altitudes = new HashMap<>();
        this.speeds = new HashMap<>();
    }
    
    // 注册飞机
    public void registerAircraft(Aircraft aircraft) {
        aircrafts.add(aircraft);
        altitudes.put(aircraft, aircraft.getAltitude());
        speeds.put(aircraft, aircraft.getSpeed());
        System.out.println("ATC: 飞机 [" + aircraft.getCallSign() + "] 已注册");
    }
    
    // 高度变化通知
    public void notifyAltitudeChange(Aircraft aircraft) {
        int newAltitude = aircraft.getAltitude();
        Integer oldAltitude = altitudes.get(aircraft);
        
        if (oldAltitude != null && oldAltitude != newAltitude) {
            System.out.println("ATC: 飞机 [" + aircraft.getCallSign() + "] 高度从 " + oldAltitude + " 变更为 " + newAltitude);
            
            // 检查是否有冲突风险
            checkAltitudeConflict(aircraft, newAltitude);
            
            altitudes.put(aircraft, newAltitude);
        }
    }
    
    // 速度变化通知
    public void notifySpeedChange(Aircraft aircraft) {
        int newSpeed = aircraft.getSpeed();
        Integer oldSpeed = speeds.get(aircraft);
        
        if (oldSpeed != null && oldSpeed != newSpeed) {
            System.out.println("ATC: 飞机 [" + aircraft.getCallSign() + "] 速度从 " + oldSpeed + " 变更为 " + newSpeed);
            speeds.put(aircraft, newSpeed);
        }
    }
    
    // 检查高度冲突
    private void checkAltitudeConflict(Aircraft aircraft, int newAltitude) {
        for (Aircraft otherAircraft : aircrafts) {
            if (otherAircraft != aircraft) {
                int otherAltitude = altitudes.get(otherAircraft);
                // 如果高度差小于1000英尺，发出警告
                if (Math.abs(newAltitude - otherAltitude) < 1000) {
                    String warning = "警告：与飞机 [" + otherAircraft.getCallSign() + 
                                   "] 高度接近，当前高度差: " + Math.abs(newAltitude - otherAltitude) + " 英尺";
                    aircraft.receiveATCInstruction(warning);
                }
            }
        }
    }
    
    // 发送消息
    public void sendMessage(Aircraft from, Aircraft to, String message) {
        System.out.println("ATC: 转发消息 [" + from.getCallSign() + "] -> [" + to.getCallSign() + "]");
        to.receiveMessage(from, message);
    }
    
    // 发送广播消息
    public void broadcastMessage(Aircraft from, String message) {
        System.out.println("ATC: 广播消息 [" + from.getCallSign() + "]: " + message);
        for (Aircraft aircraft : aircrafts) {
            if (aircraft != from) {
                aircraft.receiveMessage(from, message);
            }
        }
    }
}

public class Chapter17Example {
    public static void main(String[] args) {
        System.out.println("=== 中介者模式示例 ===\n");
        
        // 1. 基本中介者模式示例
        System.out.println("1. 基本中介者模式示例:");
        basicMediatorExample();
        
        // 2. 聊天室系统示例
        System.out.println("\n2. 聊天室系统示例:");
        chatRoomExample();
        
        // 3. GUI组件交互系统示例
        System.out.println("\n3. GUI组件交互系统示例:");
        guiMediatorExample();
        
        // 4. 飞机管制系统示例
        System.out.println("\n4. 飞机管制系统示例:");
        airTrafficControlExample();
    }
    
    // 基本中介者模式示例
    public static void basicMediatorExample() {
        ConcreteMediator mediator = new ConcreteMediator();
        ConcreteColleague1 colleague1 = new ConcreteColleague1(mediator);
        ConcreteColleague2 colleague2 = new ConcreteColleague2(mediator);
        
        mediator.setColleague1(colleague1);
        mediator.setColleague2(colleague2);
        
        colleague1.sendMessage("Hello from colleague1!");
        colleague2.sendMessage("Hello from colleague2!");
    }
    
    // 聊天室系统示例
    public static void chatRoomExample() {
        ChatRoom chatRoom = new ChatRoom();
        
        User user1 = new User("张三");
        User user2 = new User("李四");
        User user3 = new User("王五");
        
        chatRoom.addUser(user1);
        chatRoom.addUser(user2);
        chatRoom.addUser(user3);
        
        user1.sendMessage("大家好！");
        user2.sendPrivateMessage(user3, "你好，王五！");
    }
    
    // GUI组件交互系统示例
    public static void guiMediatorExample() {
        MediatorGUI mediator = new MediatorGUI();
        
        Button loginButton = new Button(mediator, "登录");
        Button logoutButton = new Button(mediator, "登出");
        TextBox usernameTextBox = new TextBox(mediator);
        TextBox passwordTextBox = new TextBox(mediator);
        Label statusLabel = new Label(mediator, "请登录");
        
        mediator.setLoginButton(loginButton);
        mediator.setLogoutButton(logoutButton);
        mediator.setUsernameTextBox(usernameTextBox);
        mediator.setPasswordTextBox(passwordTextBox);
        mediator.setStatusLabel(statusLabel);
        
        // 初始状态下登出按钮应该是禁用的
        logoutButton.setEnabled(false);
        
        // 测试输入用户名和密码
        System.out.println("--- 输入用户名 ---");
        usernameTextBox.setText("admin");
        
        System.out.println("\n--- 输入密码 ---");
        passwordTextBox.setText("123456");
        
        // 测试登录
        System.out.println("\n--- 点击登录按钮 ---");
        loginButton.click();
        
        // 测试登出
        System.out.println("\n--- 点击登出按钮 ---");
        logoutButton.click();
    }
    
    // 飞机管制系统示例
    public static void airTrafficControlExample() {
        AirTrafficControl atc = new AirTrafficControl();
        
        Aircraft aircraft1 = new Aircraft("CA101", atc);
        Aircraft aircraft2 = new Aircraft("CA202", atc);
        Aircraft aircraft3 = new Aircraft("CA303", atc);
        
        atc.registerAircraft(aircraft1);
        atc.registerAircraft(aircraft2);
        atc.registerAircraft(aircraft3);
        
        // 设置飞机高度
        System.out.println("\n--- 飞机设置高度 ---");
        aircraft1.setAltitude(10000);  // 10000英尺
        aircraft2.setAltitude(10500);  // 10500英尺（与飞机1高度接近，会触发警告）
        aircraft3.setAltitude(20000);  // 20000英尺
        
        // 飞机之间发送消息
        System.out.println("\n--- 飞机之间发送消息 ---");
        aircraft1.sendMessage(aircraft2, "请求保持当前高度");
        aircraft2.sendMessage(aircraft1, "收到，保持当前高度");
    }
}