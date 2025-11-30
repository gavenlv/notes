/**
 * 第三章示例代码：工厂方法模式演示
 */

// 抽象产品：图形接口
interface Shape {
    void draw();
}

// 具体产品：圆形
class Circle implements Shape {
    @Override
    public void draw() {
        System.out.println("绘制圆形");
    }
}

// 具体产品：矩形
class Rectangle implements Shape {
    @Override
    public void draw() {
        System.out.println("绘制矩形");
    }
}

// 具体产品：正方形
class Square implements Shape {
    @Override
    public void draw() {
        System.out.println("绘制正方形");
    }
}

// 抽象工厂
abstract class ShapeFactory {
    // 工厂方法
    public abstract Shape createShape();
    
    // 通用方法
    public void displayShapeInfo() {
        Shape shape = createShape();
        shape.draw();
    }
}

// 具体工厂：圆形工厂
class CircleFactory extends ShapeFactory {
    @Override
    public Shape createShape() {
        return new Circle();
    }
}

// 具体工厂：矩形工厂
class RectangleFactory extends ShapeFactory {
    @Override
    public Shape createShape() {
        return new Rectangle();
    }
}

// 具体工厂：正方形工厂
class SquareFactory extends ShapeFactory {
    @Override
    public Shape createShape() {
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
    @Override
    public void makeSound() {
        System.out.println("汪汪叫");
    }
}

// 具体产品：猫
class Cat extends Animal {
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
interface Logger {
    void log(String message);
}

class ConsoleLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println("控制台日志: " + message);
    }
}

class FileLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println("文件日志: " + message);
    }
}

class DatabaseLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println("数据库日志: " + message);
    }
}

class LoggerFactory {
    public static Logger getLogger(String type) {
        switch (type.toLowerCase()) {
            case "console":
                return new ConsoleLogger();
            case "file":
                return new FileLogger();
            case "database":
                return new DatabaseLogger();
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
    
    public Shape createShape(String type) {
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
        Logger consoleLogger = LoggerFactory.getLogger("console");
        Logger fileLogger = LoggerFactory.getLogger("file");
        Logger databaseLogger = LoggerFactory.getLogger("database");
        
        consoleLogger.log("这是一条控制台日志");
        fileLogger.log("这是一条文件日志");
        databaseLogger.log("这是一条数据库日志");
        
        // 4. 单例工厂演示
        System.out.println("\n4. 单例工厂演示：");
        SingletonShapeFactory singletonFactory = SingletonShapeFactory.getInstance();
        Shape circle = singletonFactory.createShape("circle");
        Shape rectangle = singletonFactory.createShape("rectangle");
        Shape square = singletonFactory.createShape("square");
        
        circle.draw();
        rectangle.draw();
        square.draw();
        
        System.out.println("\n=== 示例结束 ===");
    }
}