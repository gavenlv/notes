/**
 * 第四章示例代码：抽象工厂模式演示
 */

// 抽象产品：按钮
interface Button {
    void paint();
}

// 抽象产品：文本框
interface TextBox {
    void paint();
}

// 具体产品：Windows按钮
class WindowsButton implements Button {
    @Override
    public void paint() {
        System.out.println("渲染Windows风格按钮");
    }
}

// 具体产品：Mac按钮
class MacButton implements Button {
    @Override
    public void paint() {
        System.out.println("渲染Mac风格按钮");
    }
}

// 具体产品：Windows文本框
class WindowsTextBox implements TextBox {
    @Override
    public void paint() {
        System.out.println("渲染Windows风格文本框");
    }
}

// 具体产品：Mac文本框
class MacTextBox implements TextBox {
    @Override
    public void paint() {
        System.out.println("渲染Mac风格文本框");
    }
}

// 抽象工厂
interface GUIFactory {
    Button createButton();
    TextBox createTextBox();
}

// 具体工厂：Windows工厂
class WindowsFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }
    
    @Override
    public TextBox createTextBox() {
        return new WindowsTextBox();
    }
}

// 具体工厂：Mac工厂
class MacFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new MacButton();
    }
    
    @Override
    public TextBox createTextBox() {
        return new MacTextBox();
    }
}

// 抽象产品：手机
interface Phone {
    void assemble();
}

// 抽象产品：平板
interface Tablet {
    void assemble();
}

// 抽象产品：笔记本
interface Laptop {
    void assemble();
}

// 具体产品：苹果手机
class ApplePhone implements Phone {
    @Override
    public void assemble() {
        System.out.println("组装苹果手机");
    }
}

// 具体产品：三星手机
class SamsungPhone implements Phone {
    @Override
    public void assemble() {
        System.out.println("组装三星手机");
    }
}

// 具体产品：苹果平板
class AppleTablet implements Tablet {
    @Override
    public void assemble() {
        System.out.println("组装苹果平板");
    }
}

// 具体产品：三星平板
class SamsungTablet implements Tablet {
    @Override
    public void assemble() {
        System.out.println("组装三星平板");
    }
}

// 具体产品：苹果笔记本
class AppleLaptop implements Laptop {
    @Override
    public void assemble() {
        System.out.println("组装苹果笔记本");
    }
}

// 具体产品：三星笔记本
class SamsungLaptop implements Laptop {
    @Override
    public void assemble() {
        System.out.println("组装三星笔记本");
    }
}

// 抽象工厂
interface ElectronicsFactory {
    Phone createPhone();
    Tablet createTablet();
    Laptop createLaptop();
}

// 具体工厂：苹果工厂
class AppleFactory implements ElectronicsFactory {
    @Override
    public Phone createPhone() {
        return new ApplePhone();
    }
    
    @Override
    public Tablet createTablet() {
        return new AppleTablet();
    }
    
    @Override
    public Laptop createLaptop() {
        return new AppleLaptop();
    }
}

// 具体工厂：三星工厂
class SamsungFactory implements ElectronicsFactory {
    @Override
    public Phone createPhone() {
        return new SamsungPhone();
    }
    
    @Override
    public Tablet createTablet() {
        return new SamsungTablet();
    }
    
    @Override
    public Laptop createLaptop() {
        return new SamsungLaptop();
    }
}

// 工厂生产者
class FactoryProducer {
    public static ElectronicsFactory getFactory(String factoryType) {
        switch (factoryType.toLowerCase()) {
            case "apple":
                return new AppleFactory();
            case "samsung":
                return new SamsungFactory();
            default:
                throw new IllegalArgumentException("未知的工厂类型: " + factoryType);
        }
    }
}

// 单例抽象工厂实现
class SingletonElectronicsFactory {
    private static volatile SingletonElectronicsFactory instance;
    private ElectronicsFactory factory;
    
    private SingletonElectronicsFactory() {
        // 默认使用苹果工厂
        this.factory = new AppleFactory();
    }
    
    public static SingletonElectronicsFactory getInstance() {
        if (instance == null) {
            synchronized (SingletonElectronicsFactory.class) {
                if (instance == null) {
                    instance = new SingletonElectronicsFactory();
                }
            }
        }
        return instance;
    }
    
    public void setFactory(ElectronicsFactory factory) {
        this.factory = factory;
    }
    
    public Phone createPhone() {
        return factory.createPhone();
    }
    
    public Tablet createTablet() {
        return factory.createTablet();
    }
    
    public Laptop createLaptop() {
        return factory.createLaptop();
    }
}

// 主类 - 演示抽象工厂模式的使用
public class Chapter4Example {
    public static void main(String[] args) {
        System.out.println("=== 第四章：抽象工厂模式示例 ===\n");
        
        // 1. 跨平台UI组件演示
        System.out.println("1. 跨平台UI组件演示：");
        
        // Windows风格
        GUIFactory windowsFactory = new WindowsFactory();
        Button winButton = windowsFactory.createButton();
        TextBox winTextBox = windowsFactory.createTextBox();
        
        winButton.paint();
        winTextBox.paint();
        
        // Mac风格
        GUIFactory macFactory = new MacFactory();
        Button macButton = macFactory.createButton();
        TextBox macTextBox = macFactory.createTextBox();
        
        macButton.paint();
        macTextBox.paint();
        
        // 2. 电子产品家族演示
        System.out.println("\n2. 电子产品家族演示：");
        
        // 苹果产品族
        ElectronicsFactory appleFactory = FactoryProducer.getFactory("apple");
        Phone applePhone = appleFactory.createPhone();
        Tablet appleTablet = appleFactory.createTablet();
        Laptop appleLaptop = appleFactory.createLaptop();
        
        applePhone.assemble();
        appleTablet.assemble();
        appleLaptop.assemble();
        
        // 三星产品族
        ElectronicsFactory samsungFactory = FactoryProducer.getFactory("samsung");
        Phone samsungPhone = samsungFactory.createPhone();
        Tablet samsungTablet = samsungFactory.createTablet();
        Laptop samsungLaptop = samsungFactory.createLaptop();
        
        samsungPhone.assemble();
        samsungTablet.assemble();
        samsungLaptop.assemble();
        
        // 3. 单例工厂演示
        System.out.println("\n3. 单例工厂演示：");
        SingletonElectronicsFactory singletonFactory = SingletonElectronicsFactory.getInstance();
        
        // 使用默认的苹果工厂
        Phone phone1 = singletonFactory.createPhone();
        phone1.assemble();
        
        // 切换到三星工厂
        singletonFactory.setFactory(new SamsungFactory());
        Phone phone2 = singletonFactory.createPhone();
        phone2.assemble();
        
        System.out.println("\n=== 示例结束 ===");
    }
}