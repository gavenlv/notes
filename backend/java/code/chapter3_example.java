/**
 * 第三章示例代码：Java面向对象编程基础
 * 
 * 本文件包含第三章中介绍的所有示例代码，可以直接编译运行
 */

// 1. 基本类和对象示例
class Person {
    // 成员变量（属性）
    private String name;
    private int age;
    
    // 构造方法
    public Person() {
        // 默认构造方法
    }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 成员方法（行为）
    public void setName(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
    
    public void setAge(int age) {
        if (age > 0) {
            this.age = age;
        }
    }
    
    public int getAge() {
        return age;
    }
    
    public void introduce() {
        System.out.println("我的名字是：" + name + "，今年" + age + "岁");
    }
}

class ObjectDemo {
    public static void main(String[] args) {
        System.out.println("=== 对象创建和使用示例 ===");
        // 创建Person对象
        Person person1 = new Person();
        person1.setName("张三");
        person1.setAge(25);
        
        Person person2 = new Person("李四", 30);
        
        // 使用对象
        person1.introduce();
        person2.introduce();
    }
}

// 2. 构造方法示例
class Student {
    private String name;
    private int age;
    private String major;
    
    // 无参构造方法
    public Student() {
        System.out.println("调用无参构造方法");
    }
    
    // 有参构造方法
    public Student(String name) {
        this.name = name;
        System.out.println("调用一个参数的构造方法");
    }
    
    // 多个参数的构造方法
    public Student(String name, int age, String major) {
        this.name = name;
        this.age = age;
        this.major = major;
        System.out.println("调用三个参数的构造方法");
    }
    
    // Getter和Setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
    
    public String getMajor() { return major; }
    public void setMajor(String major) { this.major = major; }
    
    public void displayInfo() {
        System.out.println("姓名：" + name + "，年龄：" + age + "，专业：" + major);
    }
}

class ConstructorTest {
    public static void main(String[] args) {
        System.out.println("\n=== 构造方法示例 ===");
        // 使用不同的构造方法创建对象
        Student s1 = new Student();
        Student s2 = new Student("王五");
        Student s3 = new Student("赵六", 20, "计算机科学");
        
        s1.displayInfo();
        s2.displayInfo();
        s3.displayInfo();
    }
}

// 3. 封装示例
class BankAccount {
    // 私有属性
    private String accountNumber;
    private double balance;
    private String ownerName;
    
    // 构造方法
    public BankAccount(String accountNumber, String ownerName) {
        this.accountNumber = accountNumber;
        this.ownerName = ownerName;
        this.balance = 0.0;
    }
    
    // Getter方法
    public String getAccountNumber() {
        return accountNumber;
    }
    
    public String getOwnerName() {
        return ownerName;
    }
    
    public double getBalance() {
        return balance;
    }
    
    // Setter方法
    public void setOwnerName(String ownerName) {
        if (ownerName != null && !ownerName.isEmpty()) {
            this.ownerName = ownerName;
        }
    }
    
    // 业务方法
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println("存款成功，当前余额：" + balance);
        } else {
            System.out.println("存款金额必须大于0");
        }
    }
    
    public void withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            System.out.println("取款成功，当前余额：" + balance);
        } else if (amount > balance) {
            System.out.println("余额不足");
        } else {
            System.out.println("取款金额必须大于0");
        }
    }
    
    public void displayInfo() {
        System.out.println("账户号：" + accountNumber);
        System.out.println("账户名：" + ownerName);
        System.out.println("余额：" + balance);
    }
}

class EncapsulationTest {
    public static void main(String[] args) {
        System.out.println("\n=== 封装示例 ===");
        BankAccount account = new BankAccount("123456789", "张三");
        
        // 通过公共方法操作私有属性
        account.deposit(1000);
        account.withdraw(200);
        account.displayInfo();
        
        // 无法直接访问私有属性
        // account.balance = 10000; // 编译错误
        
        // 通过setter方法修改属性
        account.setOwnerName("李四");
        System.out.println("修改后的账户名：" + account.getOwnerName());
    }
}

// 4. 继承示例
// 父类：动物类
class Animal {
    protected String name;
    protected int age;
    
    public Animal() {
        System.out.println("Animal构造方法被调用");
    }
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
        System.out.println("Animal有参构造方法被调用");
    }
    
    public void eat() {
        System.out.println(name + "正在吃东西");
    }
    
    public void sleep() {
        System.out.println(name + "正在睡觉");
    }
    
    public void move() {
        System.out.println(name + "正在移动");
    }
    
    // Getter和Setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}

// 子类：狗类
class Dog extends Animal {
    private String breed; // 品种
    
    public Dog() {
        System.out.println("Dog构造方法被调用");
    }
    
    public Dog(String name, int age, String breed) {
        super(name, age); // 调用父类构造方法
        this.breed = breed;
        System.out.println("Dog有参构造方法被调用");
    }
    
    // 子类特有方法
    public void bark() {
        System.out.println(name + "汪汪叫");
    }
    
    // 重写父类方法
    @Override
    public void move() {
        System.out.println(name + "正在跑步");
    }
    
    // Getter和Setter方法
    public String getBreed() { return breed; }
    public void setBreed(String breed) { this.breed = breed; }
}

// 子类：猫类
class Cat extends Animal {
    private boolean hasLongHair; // 是否长毛
    
    public Cat() {
        System.out.println("Cat构造方法被调用");
    }
    
    public Cat(String name, int age, boolean hasLongHair) {
        super(name, age);
        this.hasLongHair = hasLongHair;
        System.out.println("Cat有参构造方法被调用");
    }
    
    // 子类特有方法
    public void meow() {
        System.out.println(name + "喵喵叫");
    }
    
    // 重写父类方法
    @Override
    public void move() {
        System.out.println(name + "正在优雅地走路");
    }
    
    // Getter和Setter方法
    public boolean isHasLongHair() { return hasLongHair; }
    public void setHasLongHair(boolean hasLongHair) { this.hasLongHair = hasLongHair; }
}

class InheritanceTest {
    public static void main(String[] args) {
        System.out.println("\n=== 继承示例 ===");
        System.out.println("=== 创建Dog对象 ===");
        Dog dog = new Dog("旺财", 3, "金毛");
        dog.eat();    // 继承自父类
        dog.sleep();  // 继承自父类
        dog.move();   // 重写的方法
        dog.bark();   // 子类特有方法
        
        System.out.println("\n=== 创建Cat对象 ===");
        Cat cat = new Cat("咪咪", 2, true);
        cat.eat();         // 继承自父类
        cat.sleep();       // 继承自父类
        cat.move();        // 重写的方法
        cat.meow();        // 子类特有方法
        System.out.println("是否长毛：" + cat.isHasLongHair());
    }
}

// 5. super关键字示例
class Vehicle {
    protected String brand;
    protected String color;
    
    public Vehicle() {
        System.out.println("Vehicle默认构造方法");
    }
    
    public Vehicle(String brand, String color) {
        this.brand = brand;
        this.color = color;
        System.out.println("Vehicle有参构造方法");
    }
    
    public void start() {
        System.out.println(brand + "车辆启动");
    }
    
    public void stop() {
        System.out.println(brand + "车辆停止");
    }
}

class Car extends Vehicle {
    private int doors;
    
    public Car() {
        super(); // 调用父类默认构造方法
        System.out.println("Car默认构造方法");
    }
    
    public Car(String brand, String color, int doors) {
        super(brand, color); // 调用父类有参构造方法
        this.doors = doors;
        System.out.println("Car有参构造方法");
    }
    
    // 重写父类方法
    @Override
    public void start() {
        super.start(); // 调用父类方法
        System.out.println("汽车发动机启动");
    }
    
    public void openTrunk() {
        System.out.println("打开后备箱");
    }
    
    public void displayInfo() {
        System.out.println("品牌：" + super.brand); // 访问父类属性
        System.out.println("颜色：" + color);       // 直接访问（继承的属性）
        System.out.println("车门数：" + doors);
    }
}

class SuperTest {
    public static void main(String[] args) {
        System.out.println("\n=== super关键字示例 ===");
        Car car = new Car("丰田", "红色", 4);
        car.start();
        car.displayInfo();
        car.openTrunk();
    }
}

// 6. 方法重载示例
class Calculator {
    // 加法运算 - 整数
    public int add(int a, int b) {
        return a + b;
    }
    
    // 加法运算 - 浮点数
    public double add(double a, double b) {
        return a + b;
    }
    
    // 加法运算 - 三个整数
    public int add(int a, int b, int c) {
        return a + b + c;
    }
    
    // 加法运算 - 字符串连接
    public String add(String a, String b) {
        return a + b;
    }
    
    // 减法运算
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public double subtract(double a, double b) {
        return a - b;
    }
}

class OverloadTest {
    public static void main(String[] args) {
        System.out.println("\n=== 方法重载示例 ===");
        Calculator calc = new Calculator();
        
        System.out.println("整数相加：" + calc.add(5, 3));
        System.out.println("浮点数相加：" + calc.add(5.5, 3.2));
        System.out.println("三个整数相加：" + calc.add(1, 2, 3));
        System.out.println("字符串连接：" + calc.add("Hello", "World"));
        System.out.println("整数相减：" + calc.subtract(10, 3));
        System.out.println("浮点数相减：" + calc.subtract(10.5, 3.2));
    }
}

// 7. 多态示例
// 抽象形状类
abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 抽象方法 - 计算面积
    public abstract double calculateArea();
    
    // 抽象方法 - 计算周长
    public abstract double calculatePerimeter();
    
    // 具体方法
    public void displayInfo() {
        System.out.println("颜色：" + color);
        System.out.println("面积：" + calculateArea());
        System.out.println("周长：" + calculatePerimeter());
    }
}

// 圆形类
class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double calculatePerimeter() {
        return 2 * Math.PI * radius;
    }
    
    public double getRadius() {
        return radius;
    }
}

// 矩形类
class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double calculateArea() {
        return width * height;
    }
    
    @Override
    public double calculatePerimeter() {
        return 2 * (width + height);
    }
    
    public double getWidth() {
        return width;
    }
    
    public double getHeight() {
        return height;
    }
}

// 三角形类
class Triangle extends Shape {
    private double side1;
    private double side2;
    private double side3;
    
    public Triangle(String color, double side1, double side2, double side3) {
        super(color);
        this.side1 = side1;
        this.side2 = side2;
        this.side3 = side3;
    }
    
    @Override
    public double calculateArea() {
        // 使用海伦公式计算三角形面积
        double s = (side1 + side2 + side3) / 2;
        return Math.sqrt(s * (s - side1) * (s - side2) * (s - side3));
    }
    
    @Override
    public double calculatePerimeter() {
        return side1 + side2 + side3;
    }
    
    public double getSide1() {
        return side1;
    }
    
    public double getSide2() {
        return side2;
    }
    
    public double getSide3() {
        return side3;
    }
}

class PolymorphismTest {
    public static void main(String[] args) {
        System.out.println("\n=== 多态示例 ===");
        // 父类引用指向不同的子类对象
        Shape[] shapes = {
            new Circle("红色", 5.0),
            new Rectangle("蓝色", 4.0, 6.0),
            new Triangle("绿色", 3.0, 4.0, 5.0)
        };
        
        System.out.println("=== 形状信息 ===");
        for (Shape shape : shapes) {
            shape.displayInfo();
            System.out.println("-------------------");
        }
    }
}

// 8. instanceof操作符示例
class InstanceofTest {
    public static void main(String[] args) {
        System.out.println("\n=== instanceof操作符示例 ===");
        Shape circle = new Circle("红色", 5.0);
        Shape rectangle = new Rectangle("蓝色", 4.0, 6.0);
        Shape triangle = new Triangle("绿色", 3.0, 4.0, 5.0);
        
        Shape[] shapes = {circle, rectangle, triangle};
        
        System.out.println("=== 使用instanceof判断对象类型 ===");
        for (Shape shape : shapes) {
            if (shape instanceof Circle) {
                Circle c = (Circle) shape; // 向下转型
                System.out.println("这是一个圆形，半径：" + c.getRadius());
            } else if (shape instanceof Rectangle) {
                Rectangle r = (Rectangle) shape; // 向下转型
                System.out.println("这是一个矩形，宽：" + r.getWidth() + "，高：" + r.getHeight());
            } else if (shape instanceof Triangle) {
                Triangle t = (Triangle) shape; // 向下转型
                System.out.println("这是一个三角形，三边长分别为：" + 
                    t.getSide1() + ", " + t.getSide2() + ", " + t.getSide3());
            }
        }
    }
}

// 9. 抽象类示例
// 抽象员工类
abstract class Employee {
    protected String name;
    protected int id;
    protected double baseSalary;
    
    public Employee(String name, int id, double baseSalary) {
        this.name = name;
        this.id = id;
        this.baseSalary = baseSalary;
    }
    
    // 具体方法
    public void displayInfo() {
        System.out.println("员工ID：" + id);
        System.out.println("员工姓名：" + name);
        System.out.println("基本工资：" + baseSalary);
    }
    
    // 抽象方法 - 计算总工资
    public abstract double calculateTotalSalary();
    
    // 抽象方法 - 显示职位信息
    public abstract void displayPositionInfo();
    
    // Getter和Setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    
    public double getBaseSalary() { return baseSalary; }
    public void setBaseSalary(double baseSalary) { this.baseSalary = baseSalary; }
}

// 全职员工类
class FullTimeEmployee extends Employee {
    private double bonus;
    private String department;
    
    public FullTimeEmployee(String name, int id, double baseSalary, double bonus, String department) {
        super(name, id, baseSalary);
        this.bonus = bonus;
        this.department = department;
    }
    
    @Override
    public double calculateTotalSalary() {
        return baseSalary + bonus;
    }
    
    @Override
    public void displayPositionInfo() {
        System.out.println("职位：全职员工");
        System.out.println("部门：" + department);
        System.out.println("奖金：" + bonus);
    }
    
    public double getBonus() { return bonus; }
    public void setBonus(double bonus) { this.bonus = bonus; }
    
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
}

// 兼职员工类
class PartTimeEmployee extends Employee {
    private double hourlyRate;
    private int hoursWorked;
    
    public PartTimeEmployee(String name, int id, double hourlyRate, int hoursWorked) {
        super(name, id, 0); // 兼职员工没有基本工资
        this.hourlyRate = hourlyRate;
        this.hoursWorked = hoursWorked;
    }
    
    @Override
    public double calculateTotalSalary() {
        return hourlyRate * hoursWorked;
    }
    
    @Override
    public void displayPositionInfo() {
        System.out.println("职位：兼职员工");
        System.out.println("小时工资：" + hourlyRate);
        System.out.println("工作小时数：" + hoursWorked);
    }
    
    public double getHourlyRate() { return hourlyRate; }
    public void setHourlyRate(double hourlyRate) { this.hourlyRate = hourlyRate; }
    
    public int getHoursWorked() { return hoursWorked; }
    public void setHoursWorked(int hoursWorked) { this.hoursWorked = hoursWorked; }
}

class AbstractClassTest {
    public static void main(String[] args) {
        System.out.println("\n=== 抽象类示例 ===");
        Employee[] employees = {
            new FullTimeEmployee("张三", 1001, 8000, 2000, "技术部"),
            new PartTimeEmployee("李四", 2001, 50, 80)
        };
        
        System.out.println("=== 员工工资信息 ===");
        for (Employee employee : employees) {
            employee.displayInfo();
            employee.displayPositionInfo();
            System.out.println("总工资：" + employee.calculateTotalSalary());
            System.out.println("-------------------");
        }
    }
}

// 10. 接口示例
// 可飞行接口
interface Flyable {
    // 常量
    int MAX_ALTITUDE = 10000;
    
    // 抽象方法
    void fly();
    void land();
    
    // 默认方法（Java 8+）
    default void checkWeather() {
        System.out.println("检查天气状况...");
    }
    
    // 静态方法（Java 8+）
    static void displayFlightRules() {
        System.out.println("遵守飞行规则，确保安全飞行");
    }
}

// 可游泳接口
interface Swimmable {
    void swim();
    void dive();
}

// 可奔跑接口
interface Runnable {
    void run();
    void jump();
    
    // 默认方法
    default void warmUp() {
        System.out.println("进行热身运动...");
    }
}

// 鸟类（实现Flyable接口）
class Bird implements Flyable {
    private String species;
    
    public Bird(String species) {
        this.species = species;
    }
    
    @Override
    public void fly() {
        System.out.println(species + "正在飞翔，最大高度可达" + MAX_ALTITUDE + "米");
    }
    
    @Override
    public void land() {
        System.out.println(species + "安全着陆");
    }
    
    public String getSpecies() {
        return species;
    }
}

// 鱼类（实现Swimmable接口）
class Fish implements Swimmable {
    private String type;
    
    public Fish(String type) {
        this.type = type;
    }
    
    @Override
    public void swim() {
        System.out.println(type + "在水中游动");
    }
    
    @Override
    public void dive() {
        System.out.println(type + "潜入水底");
    }
    
    public String getType() {
        return type;
    }
}

// 猎豹类（实现Runnable接口）
class Cheetah implements Runnable {
    private String name;
    
    public Cheetah(String name) {
        this.name = name;
    }
    
    @Override
    public void run() {
        System.out.println(name + "以超快速度奔跑");
    }
    
    @Override
    public void jump() {
        System.out.println(name + "跳跃障碍物");
    }
    
    public String getName() {
        return name;
    }
}

// 鸭子类（实现多个接口）
class Duck implements Flyable, Swimmable, Runnable {
    private String name;
    
    public Duck(String name) {
        this.name = name;
    }
    
    @Override
    public void fly() {
        System.out.println(name + "展翅飞翔");
    }
    
    @Override
    public void land() {
        System.out.println(name + "轻盈着陆");
    }
    
    @Override
    public void swim() {
        System.out.println(name + "在水面游泳");
    }
    
    @Override
    public void dive() {
        System.out.println(name + "潜入水中觅食");
    }
    
    @Override
    public void run() {
        System.out.println(name + "在陆地上快跑");
    }
    
    @Override
    public void jump() {
        System.out.println(name + "跳跃到岸边");
    }
    
    // 重写默认方法
    @Override
    public void warmUp() {
        System.out.println(name + "整理羽毛，准备活动");
    }
    
    public String getName() {
        return name;
    }
}

class InterfaceTest {
    public static void main(String[] args) {
        System.out.println("\n=== 接口示例 ===");
        System.out.println("=== 接口功能展示 ===");
        
        // 使用Flyable接口
        Flyable bird = new Bird("老鹰");
        bird.checkWeather(); // 调用默认方法
        bird.fly();
        bird.land();
        Flyable.displayFlightRules(); // 调用静态方法
        
        System.out.println();
        
        // 使用Swimmable接口
        Swimmable fish = new Fish("金鱼");
        fish.swim();
        fish.dive();
        
        System.out.println();
        
        // 使用Runnable接口
        Runnable cheetah = new Cheetah("猎豹");
        cheetah.warmUp(); // 调用默认方法
        cheetah.run();
        cheetah.jump();
        
        System.out.println();
        
        // 使用多重接口
        Duck duck = new Duck("唐老鸭");
        duck.warmUp(); // 调用重写的默认方法
        duck.fly();
        duck.swim();
        duck.run();
        duck.land();
        duck.dive();
        duck.jump();
    }
}

/*
 * 编译和运行说明：
 * 
 * 1. 编译所有类：
 *    javac chapter3_example.java
 * 
 * 2. 运行各个示例：
 *    java ObjectDemo
 *    java ConstructorTest
 *    java EncapsulationTest
 *    java InheritanceTest
 *    java SuperTest
 *    java OverloadTest
 *    java PolymorphismTest
 *    java InstanceofTest
 *    java AbstractClassTest
 *    java InterfaceTest
 * 
 * 注意：由于一个.java文件中包含多个public类，只有与文件名相同的类可以是public的。
 * 在实际项目中，建议将每个类放在单独的文件中。
 */