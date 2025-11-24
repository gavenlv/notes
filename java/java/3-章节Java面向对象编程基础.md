# 第3章 Java面向对象编程基础

## 目录
1. [面向对象编程概述](#1面向对象编程概述)
2. [类和对象](#2类和对象)
3. [封装](#3封装)
4. [继承](#4继承)
5. [多态](#5多态)
6. [抽象类和接口](#6抽象类和接口)
7. [包和访问修饰符](#7包和访问修饰符)
8. [最佳实践](#8最佳实践)
9. [总结](#9总结)

---

## 1.面向对象编程概述

### 1.1 什么是面向对象编程

面向对象编程（Object-Oriented Programming，简称OOP）是一种编程范式，它将现实世界中的事物抽象为程序中的对象，通过对象之间的交互来解决问题。面向对象编程的核心思想是将数据和操作数据的方法封装在一起，形成一个独立的实体——对象。

### 1.2 面向对象的三大特征

面向对象编程有三个核心特征：
1. **封装（Encapsulation）**：将数据和操作数据的方法组合在一个单元中，隐藏内部实现细节。
2. **继承（Inheritance）**：允许一个类继承另一个类的属性和方法，实现代码复用。
3. **多态（Polymorphism）**：同一个接口可以有不同的实现方式，提高代码灵活性。

### 1.3 面向对象的优势

- 提高代码的可维护性和可扩展性
- 增强代码的复用性
- 降低软件开发的复杂度
- 更符合人类认知习惯

---

## 2.类和对象

### 2.1 类的概念

类（Class）是对具有相同属性和行为的一组对象的抽象描述。类定义了对象的属性（成员变量）和行为（成员方法）。

### 2.2 对象的概念

对象（Object）是类的一个实例。每个对象都有自己的状态（属性值）和行为（方法）。

### 2.3 类的定义

```java
// 定义一个简单的类
public class Person {
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
```

### 2.4 对象的创建和使用

```java
public class ObjectDemo {
    public static void main(String[] args) {
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
```

### 2.5 构造方法

构造方法是一种特殊的方法，用于初始化对象。构造方法的特点：
- 方法名与类名相同
- 没有返回值类型
- 在创建对象时自动调用

```java
public class Student {
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

// 测试构造方法
public class ConstructorTest {
    public static void main(String[] args) {
        // 使用不同的构造方法创建对象
        Student s1 = new Student();
        Student s2 = new Student("王五");
        Student s3 = new Student("赵六", 20, "计算机科学");
        
        s1.displayInfo();
        s2.displayInfo();
        s3.displayInfo();
    }
}
```

---

## 3.封装

### 3.1 封装的概念

封装是指将对象的属性和操作这些属性的方法结合成一个独立的单位，并尽可能隐藏对象的内部实现细节，只对外提供公共的访问接口。

### 3.2 访问修饰符

Java提供了四种访问修饰符来控制类、成员变量和成员方法的访问权限：

| 修饰符 | 同一个类 | 同一个包 | 不同包的子类 | 不同包的非子类 |
|--------|----------|----------|--------------|----------------|
| private | ✓ | ✗ | ✗ | ✗ |
| default | ✓ | ✓ | ✗ | ✗ |
| protected | ✓ | ✓ | ✓ | ✗ |
| public | ✓ | ✓ | ✓ | ✓ |

### 3.3 Getter和Setter方法

通过Getter和Setter方法来访问和修改私有属性，这是封装的一种体现：

```java
public class BankAccount {
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

// 测试封装
public class EncapsulationTest {
    public static void main(String[] args) {
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
```

---

## 4.继承

### 4.1 继承的概念

继承是面向对象编程的一个重要特性，它允许一个类（子类）继承另一个类（父类）的属性和方法，从而实现代码复用。

### 4.2 继承的语法

```java
class 子类名 extends 父类名 {
    // 子类特有的属性和方法
}
```

### 4.3 继承示例

```java
// 父类：动物类
public class Animal {
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
public class Dog extends Animal {
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
public class Cat extends Animal {
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

// 测试继承
public class InheritanceTest {
    public static void main(String[] args) {
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
```

### 4.4 super关键字

super关键字用于引用父类的成员：

```java
public class Vehicle {
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

public class Car extends Vehicle {
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

// 测试super关键字
public class SuperTest {
    public static void main(String[] args) {
        Car car = new Car("丰田", "红色", 4);
        car.start();
        car.displayInfo();
        car.openTrunk();
    }
}
```

---

## 5.多态

### 5.1 多态的概念

多态是指同一个接口可以有不同的实现方式。在Java中，多态主要体现在：
1. 方法重载（Overloading）
2. 方法重写（Overriding）
3. 父类引用指向子类对象

### 5.2 方法重载

方法重载是指在同一个类中，方法名相同但参数列表不同（参数类型、个数或顺序不同）：

```java
public class Calculator {
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

// 测试方法重载
public class OverloadTest {
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        
        System.out.println("整数相加：" + calc.add(5, 3));
        System.out.println("浮点数相加：" + calc.add(5.5, 3.2));
        System.out.println("三个整数相加：" + calc.add(1, 2, 3));
        System.out.println("字符串连接：" + calc.add("Hello", "World"));
        System.out.println("整数相减：" + calc.subtract(10, 3));
        System.out.println("浮点数相减：" + calc.subtract(10.5, 3.2));
    }
}
```

### 5.3 方法重写

方法重写是指子类重新定义父类中已有的方法：

```java
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

// 测试多态
public class PolymorphismTest {
    public static void main(String[] args) {
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
```

### 5.4 instanceof操作符

instanceof操作符用于判断对象是否属于某个类或其子类：

```java
public class InstanceofTest {
    public static void main(String[] args) {
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
```

---

## 6.抽象类和接口

### 6.1 抽象类

抽象类是不能被实例化的类，通常包含抽象方法（没有具体实现的方法）。抽象类使用abstract关键字声明：

```java
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

// 测试抽象类
public class AbstractClassTest {
    public static void main(String[] args) {
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
```

### 6.2 接口

接口是一种完全抽象的类，它只包含常量和抽象方法。从Java 8开始，接口可以包含默认方法和静态方法：

```java
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

// 测试接口
public class InterfaceTest {
    public static void main(String[] args) {
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
```

### 6.3 接口与抽象类的区别

| 特性 | 抽象类 | 接口 |
|------|--------|------|
| 关键字 | abstract class | interface |
| 继承/实现 | extends（单继承） | implements（多实现） |
| 成员变量 | 可以有各种访问修饰符 | 只能是public static final |
| 方法 | 可以有具体方法和抽象方法 | Java 8前只能是抽象方法，之后可有默认方法和静态方法 |
| 构造方法 | 可以有构造方法 | 不能有构造方法 |
| 访问修饰符 | 可以使用各种访问修饰符 | 方法默认是public abstract |

---

## 7.包和访问修饰符

### 7.1 包的概念

包（Package）是Java中组织类和接口的一种机制，类似于文件夹的作用。包可以帮助避免命名冲突，并控制访问权限。

### 7.2 包的声明和使用

```java
// 文件路径：com/company/project/util/MathUtils.java
package com.company.project.util;

public class MathUtils {
    // 计算两个数的最大公约数
    public static int gcd(int a, int b) {
        if (b == 0) return a;
        return gcd(b, a % b);
    }
    
    // 计算两个数的最小公倍数
    public static int lcm(int a, int b) {
        return (a * b) / gcd(a, b);
    }
    
    // 判断一个数是否为质数
    public static boolean isPrime(int n) {
        if (n <= 1) return false;
        if (n <= 3) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        
        for (int i = 5; i * i 