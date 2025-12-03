/**
 * 第三章示例代码：工厂方法模式演示
 */

// 抽象产品：图形接口
interface GraphicShape {
    void draw();
}

// 具体产品：圆形
class Circle implements GraphicShape {
    private int x, y, radius;
    
    public Circle() {
        // 默认构造函数
    }
    
    public Circle(int x, int y, int radius) {
        this.x = x;
        this.y = y;
        this.radius = radius;
    }
    
    @Override
    public void draw() {
        if (x != 0 || y != 0 || radius != 0) {
            System.out.println("绘制圆形，坐标: (" + x + ", " + y + ")，半径: " + radius);
        } else {
            System.out.println("绘制圆形");
        }
    }
}

// 具体产品：矩形
class Rectangle implements GraphicShape {
    @Override
    public void draw() {
        System.out.println("绘制矩形");
    }
}

// 具体产品：正方形
class Square implements GraphicShape {
    @Override
    public void draw() {
        System.out.println("绘制正方形");
    }
}

// 抽象工厂
abstract class ShapeFactory {
    // 工厂方法
    public abstract GraphicShape createShape();
    
    // 通用方法
    public void displayShapeInfo() {
        GraphicShape shape = createShape();
        shape.draw();
    }
}

// 具体工厂：圆形工厂
class CircleFactory extends ShapeFactory {
    @Override
    public GraphicShape createShape() {
        return new Circle();
    }
}

// 具体工厂：矩形工厂
class RectangleFactory extends ShapeFactory {
    @Override
    public GraphicShape createShape() {
        return new Rectangle();
    }
}

// 具体工厂：正方形工厂
class SquareFactory extends ShapeFactory {
    @Override
    public GraphicShape createShape() {
        return new Square();
    }
}

// 参数化工厂示例
// 抽象产品：动物接口
abstract class Animal {
    public abstract void makeSound();
}

// 具体产品：狗
class Dog extends Animal {
    private String name;
    private int age;
    private String breed;
    
    public Dog() {
        // 默认构造函数
        super(); // 调用父类的无参构造函数
    }
    
    public Dog(String name, int age, String breed) {
        super(); // 调用父类的无参构造函数
        this.name = name;
        this.age = age;
        this.breed = breed;
    }
    
    @Override
    public void makeSound() {
        System.out.println("汪汪叫");
    }
}

// 具体产品：猫
class Cat extends Animal {
    private String name;
    private int age;
    private boolean isIndoor;
    
    public Cat() {
        // 默认构造函数
        super(); // 调用父类的无参构造函数
    }
    
    public Cat(String name, int age, boolean isIndoor) {
        super(); // 调用父类的无参构造函数
        this.name = name;
        this.age = age;
        this.isIndoor = isIndoor;
    }
    
    @Override
    public void makeSound() {
        System.out.println("喵喵叫");
    }
}

// 抽象工厂
abstract class AnimalFactory {
    public abstract Animal createAnimal(String type);
}

// 具体工厂
class SimpleAnimalFactory extends AnimalFactory {
    @Override
    public Animal createAnimal(String type) {
        switch (type.toLowerCase()) {
            case "dog":
                return new Dog();
            case "cat":
                return new Cat();
            default:
                throw new IllegalArgumentException("未知的动物类型: " + type);
        }
    }
}

// 静态工厂方法示例
interface AppLogger {
    void log(String message);
}

class ConsoleAppLogger implements AppLogger {
    @Override
    public void log(String message) {
        System.out.println("控制台日志: " + message);
    }
}

class FileAppLogger implements AppLogger {
    @Override
    public void log(String message) {
        System.out.println("文件日志: " + message);
    }
}

class DatabaseAppLogger implements AppLogger {
    @Override
    public void log(String message) {
        System.out.println("数据库日志: " + message);
    }
}

class LoggerFactory {
    public static AppLogger getLogger(String type) {
        switch (type.toLowerCase()) {
            case "console":
                return new ConsoleAppLogger();
            case "file":
                return new FileAppLogger();
            case "database":
                return new DatabaseAppLogger();
            default:
                throw new IllegalArgumentException("未知的日志类型: " + type);
        }
    }
}

// 单例工厂示例
class SingletonShapeFactory {
    private static volatile SingletonShapeFactory instance;
    
    private SingletonShapeFactory() {}
    
    public static SingletonShapeFactory getInstance() {
        if (instance == null) {
            synchronized (SingletonShapeFactory.class) {
                if (instance == null) {
                    instance = new SingletonShapeFactory();
                }
            }
        }
        return instance;
    }
    
    public GraphicShape createShape(String type) {
        switch (type.toLowerCase()) {
            case "circle":
                return new Circle();
            case "rectangle":
                return new Rectangle();
            case "square":
                return new Square();
            default:
                throw new IllegalArgumentException("未知的图形类型: " + type);
        }
    }
}

// 主类 - 演示工厂方法模式的使用
public class Chapter3Example {
    public static void main(String[] args) {
        System.out.println("=== 第三章：工厂方法模式示例 ===\n");
        
        // 1. 基本工厂方法模式演示
        System.out.println("1. 基本工厂方法模式演示：");
        ShapeFactory circleFactory = new CircleFactory();
        ShapeFactory rectangleFactory = new RectangleFactory();
        ShapeFactory squareFactory = new SquareFactory();
        
        circleFactory.displayShapeInfo();
        rectangleFactory.displayShapeInfo();
        squareFactory.displayShapeInfo();
        
        // 2. 参数化工厂演示
        System.out.println("\n2. 参数化工厂演示：");
        AnimalFactory animalFactory = new SimpleAnimalFactory();
        Animal dog = animalFactory.createAnimal("dog");
        Animal cat = animalFactory.createAnimal("cat");
        
        dog.makeSound();
        cat.makeSound();
        
        // 3. 静态工厂方法演示
        System.out.println("\n3. 静态工厂方法演示：");
        AppLogger consoleLogger = LoggerFactory.getLogger("console");
        AppLogger fileLogger = LoggerFactory.getLogger("file");
        AppLogger databaseLogger = LoggerFactory.getLogger("database");
        
        consoleLogger.log("这是一条控制台日志");
        fileLogger.log("这是一条文件日志");
        databaseLogger.log("这是一条数据库日志");
        
        // 4. 单例工厂演示
        System.out.println("\n4. 单例工厂演示：");
        SingletonShapeFactory singletonFactory = SingletonShapeFactory.getInstance();
        GraphicShape circle = singletonFactory.createShape("circle");
        GraphicShape rectangle = singletonFactory.createShape("rectangle");
        GraphicShape square = singletonFactory.createShape("square");
        
        circle.draw();
        rectangle.draw();
        square.draw();
        
        System.out.println("\n=== 示例结束 ===");
    }
}