# Java 学习笔记

## 概述

Java是一种面向对象的编程语言，由Sun Microsystems（现为Oracle）于1995年推出。Java具有跨平台性、安全性和稳定性等特点，广泛应用于企业级应用开发、Android移动开发、大数据处理等领域。

## 目录结构

```
java/
├── basics/                 # Java基础
│   ├── syntax.md          # 基本语法
│   ├── variables.md       # 变量和数据类型
│   ├── operators.md       # 运算符
│   ├── control-flow.md    # 控制流
│   └── arrays.md          # 数组
├── oop/                    # 面向对象编程
│   ├── classes.md         # 类和对象
│   ├── inheritance.md     # 继承
│   ├── polymorphism.md    # 多态
│   ├── encapsulation.md   # 封装
│   ├── abstract.md        # 抽象类和接口
│   └── inner-classes.md   # 内部类
├── collections/             # 集合框架
│   ├── list.md            # List接口和实现
│   ├── set.md             # Set接口和实现
│   ├── map.md             # Map接口和实现
│   ├── queue.md           # Queue接口和实现
│   └── iterators.md       # 迭代器
├── exceptions/              # 异常处理
│   ├── try-catch.md       # try-catch-finally
│   ├── exception-types.md # 异常类型
│   ├── custom-exceptions.md # 自定义异常
│   └── best-practices.md  # 异常处理最佳实践
├── io/                      # 输入输出
│   ├── streams.md         # 流
│   ├── file-io.md         # 文件操作
│   ├── nio.md             # NIO
│   └── serialization.md   # 序列化
├── concurrency/             # 并发编程
│   ├── threads.md         # 线程基础
│   ├── synchronization.md # 同步
│   ├── executors.md       # 线程池
│   ├── concurrent-collections.md # 并发集合
│   └── locks.md           # 锁机制
├── generics/               # 泛型
│   ├── basics.md          # 泛型基础
│   ├── wildcards.md       # 通配符
│   ├── type-erasure.md    # 类型擦除
│   └── generic-methods.md # 泛型方法
├── reflection/             # 反射
│   ├── class-objects.md   # Class对象
│   ├── fields.md          # 字段反射
│   ├── methods.md         # 方法反射
│   └── constructors.md    # 构造器反射
├── annotations/            # 注解
│   ├── built-in.md        # 内置注解
│   ├── custom.md          # 自定义注解
│   └── meta-annotations.md # 元注解
├── functional/             # 函数式编程
│   ├── lambda.md          # Lambda表达式
│   ├── streams-api.md     # Streams API
│   ├── optional.md        # Optional类
│   └── functional-interfaces.md # 函数式接口
├── jdbc/                   # 数据库连接
│   ├── basics.md          # JDBC基础
│   ├── connection.md      # 连接管理
│   ├── statements.md      # 语句执行
│   ├── result-sets.md     # 结果集处理
│   └── connection-pool.md # 连接池
├── frameworks/             # 框架
│   ├── spring.md          # Spring框架
│   ├── spring-boot.md     # Spring Boot
│   ├── hibernate.md       # Hibernate
│   ├── mybatis.md         # MyBatis
│   └── maven.md           # Maven构建工具
├── testing/                # 测试
│   ├── junit.md           # JUnit测试框架
│   ├── mockito.md         # Mockito模拟框架
│   ├── test-driven.md     # 测试驱动开发
│   └── integration.md     # 集成测试
├── design-patterns/         # 设计模式
│   ├── creational.md      # 创建型模式
│   ├── structural.md      # 结构型模式
│   ├── behavioral.md      # 行为型模式
│   └── examples.md        # 示例实现
├── performance/            # 性能优化
│   ├── jvm.md             # JVM原理
│   ├── memory.md          # 内存管理
│   ├── gc.md              # 垃圾回收
│   ├── profiling.md       # 性能分析
│   └── tuning.md          # JVM调优
└── tools/                  # 工具和资源
    ├── ide.md             # IDE使用
    ├── debugging.md       # 调试技巧
    ├── build-tools.md     # 构建工具
    └── version-control.md # 版本控制
```

## 学习路径

### 初学者路径
1. **Java基础语法** - 了解Java的基本语法和结构
2. **变量和数据类型** - 掌握基本数据类型和引用类型
3. **控制流** - 学习条件语句和循环
4. **数组** - 了解数组的使用方法
5. **方法** - 学习方法的定义和调用

### 进阶路径
1. **面向对象编程** - 掌握类、对象、继承、多态等概念
2. **异常处理** - 学习如何处理程序中的异常
3. **集合框架** - 掌握List、Set、Map等集合的使用
4. **泛型** - 了解泛型的概念和应用
5. **I/O操作** - 学习文件读写和流处理

### 高级路径
1. **并发编程** - 掌握多线程编程和同步机制
2. **反射和注解** - 了解Java的元编程能力
3. **JVM原理** - 深入理解Java虚拟机的工作原理
4. **设计模式** - 学习常用的设计模式
5. **框架应用** - 掌握Spring等主流框架的使用

## 常见问题

### Q: Java中的==和equals()有什么区别？
A: ==和equals()的主要区别：
- ==比较基本类型时比较值，比较引用类型时比较内存地址
- equals()是Object类的方法，默认行为与==相同
- String、Integer等类重写了equals()方法，比较的是内容值
- 自定义类可以重写equals()方法实现自定义比较逻辑

### Q: 什么是Java的自动装箱和拆箱？
A: 自动装箱和拆箱是Java 5引入的特性：
- 自动装箱：基本类型自动转换为对应的包装类
- 自动拆箱：包装类自动转换为对应的基本类型
- 例如：Integer i = 100;（装箱）int j = i;（拆箱）
- 注意：装箱和拆箱可能影响性能，特别是在循环中

### Q: Java中的异常处理机制是怎样的？
A: Java异常处理机制包括：
- try块：包含可能抛出异常的代码
- catch块：捕获并处理特定类型的异常
- finally块：无论是否发生异常都会执行的代码
- throw关键字：手动抛出异常
- throws关键字：声明方法可能抛出的异常
- 异常层次：Throwable > Error > Exception > RuntimeException

## 资源链接

- [Oracle Java官方文档](https://docs.oracle.com/en/java/)
- [Java SE 11文档](https://docs.oracle.com/en/java/javase/11/)
- [Baeldung Java教程](https://www.baeldung.com/java)
- [Java设计模式](https://refactoring.guru/design-patterns/java)
- [Effective Java中文版](https://book.douban.com/subject/30412517/)

## 代码示例

### 基本语法

```java
// HelloWorld.java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        // 变量声明
        int age = 25;
        double height = 175.5;
        boolean isStudent = true;
        char grade = 'A';
        String name = "Alice";
        
        // 常量
        final double PI = 3.14159;
        
        // 输出变量
        System.out.println("Name: " + name + ", Age: " + age);
        System.out.printf("Name: %s, Age: %d, Height: %.1f%n", name, age, height);
    }
}
```

### 控制流

```java
public class ControlFlow {
    public static void main(String[] args) {
        // if-else语句
        int score = 85;
        if (score >= 90) {
            System.out.println("优秀");
        } else if (score >= 80) {
            System.out.println("良好");
        } else if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }
        
        // switch语句
        char grade = 'B';
        switch (grade) {
            case 'A':
                System.out.println("优秀");
                break;
            case 'B':
                System.out.println("良好");
                break;
            case 'C':
                System.out.println("及格");
                break;
            default:
                System.out.println("未知等级");
        }
        
        // for循环
        for (int i = 1; i <= 10; i++) {
            System.out.print(i + " ");
        }
        System.out.println();
        
        // 增强for循环
        String[] names = {"Alice", "Bob", "Charlie"};
        for (String name : names) {
            System.out.println(name);
        }
        
        // while循环
        int count = 0;
        while (count < 5) {
            System.out.println("Count: " + count);
            count++;
        }
        
        // do-while循环
        int number;
        do {
            number = (int) (Math.random() * 10);
            System.out.println("Generated number: " + number);
        } while (number != 0);
    }
}
```

### 类和对象

```java
// Person.java
public class Person {
    // 实例变量
    private String name;
    private int age;
    
    // 静态变量
    private static int count = 0;
    
    // 构造方法
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
        count++;
    }
    
    // 实例方法
    public void introduce() {
        System.out.println("My name is " + name + ", I'm " + age + " years old.");
    }
    
    // getter和setter方法
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        if (age > 0) {
            this.age = age;
        }
    }
    
    // 静态方法
    public static int getCount() {
        return count;
    }
    
    // 重写toString方法
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

// 使用Person类
public class PersonDemo {
    public static void main(String[] args) {
        Person person1 = new Person("Alice", 25);
        Person person2 = new Person("Bob", 30);
        
        person1.introduce();
        person2.introduce();
        
        System.out.println("Total persons: " + Person.getCount());
        
        // 使用getter和setter
        System.out.println(person1.getName());
        person2.setAge(31);
        System.out.println(person2);
    }
}
```

### 继承和多态

```java
// 基类 Animal
public class Animal {
    protected String name;
    
    public Animal(String name) {
        this.name = name;
    }
    
    public void eat() {
        System.out.println(name + " is eating.");
    }
    
    public void sleep() {
        System.out.println(name + " is sleeping.");
    }
    
    // 可能被子类重写的方法
    public void makeSound() {
        System.out.println(name + " makes a sound.");
    }
}

// 子类 Dog
public class Dog extends Animal {
    private String breed;
    
    public Dog(String name, String breed) {
        super(name); // 调用父类构造方法
        this.breed = breed;
    }
    
    // 重写父类方法
    @Override
    public void makeSound() {
        System.out.println(name + " barks.");
    }
    
    // 子类特有方法
    public void wagTail() {
        System.out.println(name + " wags its tail.");
    }
    
    public String getBreed() {
        return breed;
    }
}

// 子类 Cat
public class Cat extends Animal {
    public Cat(String name) {
        super(name);
    }
    
    @Override
    public void makeSound() {
        System.out.println(name + " meows.");
    }
    
    public void purr() {
        System.out.println(name + " purrs.");
    }
}

// 多态示例
public class AnimalDemo {
    public static void main(String[] args) {
        // 多态：父类引用指向子类对象
        Animal myDog = new Dog("Rex", "German Shepherd");
        Animal myCat = new Cat("Whiskers");
        
        // 调用重写的方法，会执行子类的实现
        myDog.makeSound(); // Rex barks.
        myCat.makeSound(); // Whiskers meows.
        
        // 调用继承的方法
        myDog.eat(); // Rex is eating.
        myCat.sleep(); // Whiskers is sleeping.
        
        // 类型检查和转换
        if (myDog instanceof Dog) {
            Dog dog = (Dog) myDog; // 向下转型
            dog.wagTail(); // Rex wags its tail.
            System.out.println("Breed: " + dog.getBreed());
        }
        
        // 多态数组
        Animal[] animals = {
            new Dog("Buddy", "Labrador"),
            new Cat("Mittens"),
            new Dog("Max", "Beagle")
        };
        
        for (Animal animal : animals) {
            animal.makeSound(); // 根据实际对象类型调用相应方法
        }
    }
}
```

### 接口和抽象类

```java
// 接口 Flyable
public interface Flyable {
    // 接口中的变量默认是 public static final
    double MAX_ALTITUDE = 10000.0;
    
    // 接口中的方法默认是 public abstract
    void fly();
    
    // Java 8中的默认方法
    default void takeOff() {
        System.out.println("Taking off...");
    }
    
    // Java 8中的静态方法
    static void displayFlightInfo() {
        System.out.println("Maximum altitude: " + MAX_ALTITUDE + " meters");
    }
}

// 接口 Swimmable
public interface Swimmable {
    void swim();
}

// 抽象类 Animal
public abstract class Animal {
    protected String name;
    
    public Animal(String name) {
        this.name = name;
    }
    
    // 具体方法
    public void eat() {
        System.out.println(name + " is eating.");
    }
    
    // 抽象方法，子类必须实现
    public abstract void makeSound();
}

// 实现多个接口的类
public class Duck extends Animal implements Flyable, Swimmable {
    public Duck(String name) {
        super(name);
    }
    
    @Override
    public void makeSound() {
        System.out.println(name + " quacks.");
    }
    
    @Override
    public void fly() {
        System.out.println(name + " is flying.");
    }
    
    @Override
    public void swim() {
        System.out.println(name + " is swimming.");
    }
}

// 使用接口和抽象类
public class InterfaceDemo {
    public static void main(String[] args) {
        Duck duck = new Duck("Donald");
        
        // 调用继承的方法
        duck.eat();
        duck.makeSound();
        
        // 调用接口实现的方法
        duck.takeOff(); // 默认方法
        duck.fly();
        duck.swim();
        
        // 调用接口静态方法
        Flyable.displayFlightInfo();
        
        // 接口引用
        Flyable flyable = duck;
        flyable.fly();
        // flyable.swim(); // 错误，Flyable接口没有swim方法
        
        Swimmable swimmable = duck;
        swimmable.swim();
        // swimmable.fly(); // 错误，Swimmable接口没有fly方法
    }
}
```

### 集合框架

```java
import java.util.*;

public class CollectionsDemo {
    public static void main(String[] args) {
        // List - 有序集合，允许重复元素
        List<String> list = new ArrayList<>();
        list.add("Apple");
        list.add("Banana");
        list.add("Orange");
        list.add("Apple"); // 允许重复
        
        System.out.println("List: " + list);
        System.out.println("Element at index 1: " + list.get(1));
        System.out.println("Index of 'Apple': " + list.indexOf("Apple"));
        
        // 遍历List
        for (String fruit : list) {
            System.out.println(fruit);
        }
        
        // 使用迭代器
        Iterator<String> iterator = list.iterator();
        while (iterator.hasNext()) {
            System.out.println(iterator.next());
        }
        
        // Set - 无序集合，不允许重复元素
        Set<String> set = new HashSet<>();
        set.add("Red");
        set.add("Green");
        set.add("Blue");
        set.add("Red"); // 重复元素不会被添加
        
        System.out.println("Set: " + set);
        System.out.println("Contains 'Green': " + set.contains("Green"));
        
        // 遍历Set
        for (String color : set) {
            System.out.println(color);
        }
        
        // Map - 键值对集合
        Map<String, Integer> map = new HashMap<>();
        map.put("Alice", 25);
        map.put("Bob", 30);
        map.put("Charlie", 35);
        
        System.out.println("Map: " + map);
        System.out.println("Alice's age: " + map.get("Alice"));
        System.out.println("Contains key 'Bob': " + map.containsKey("Bob"));
        
        // 遍历Map
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
        
        // 只遍历键
        for (String key : map.keySet()) {
            System.out.println(key);
        }
        
        // 只遍历值
        for (Integer value : map.values()) {
            System.out.println(value);
        }
        
        // Queue - 队列
        Queue<String> queue = new LinkedList<>();
        queue.offer("First");
        queue.offer("Second");
        queue.offer("Third");
        
        System.out.println("Queue: " + queue);
        System.out.println("Peek: " + queue.peek()); // 查看队首元素但不移除
        System.out.println("Poll: " + queue.poll()); // 移除并返回队首元素
        System.out.println("Queue after poll: " + queue);
        
        // 泛型集合
        List<Person> people = new ArrayList<>();
        people.add(new Person("Alice", 25));
        people.add(new Person("Bob", 30));
        
        for (Person person : people) {
            System.out.println(person.getName() + " is " + person.getAge() + " years old.");
        }
        
        // 使用Collections工具类
        List<Integer> numbers = new ArrayList<>();
        numbers.add(5);
        numbers.add(2);
        numbers.add(8);
        numbers.add(1);
        numbers.add(9);
        
        System.out.println("Original list: " + numbers);
        Collections.sort(numbers);
        System.out.println("Sorted list: " + numbers);
        Collections.reverse(numbers);
        System.out.println("Reversed list: " + numbers);
        System.out.println("Max: " + Collections.max(numbers));
        System.out.println("Min: " + Collections.min(numbers));
    }
}
```

### 异常处理

```java
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

// 自定义异常
class InvalidAgeException extends Exception {
    public InvalidAgeException(String message) {
        super(message);
    }
}

public class ExceptionDemo {
    
    // 方法声明可能抛出的异常
    public static void validateAge(int age) throws InvalidAgeException {
        if (age < 0 || age > 150) {
            throw new InvalidAgeException("Age must be between 0 and 150");
        }
        System.out.println("Valid age: " + age);
    }
    
    public static void readFile(String filename) {
        FileReader reader = null;
        try {
            File file = new File(filename);
            reader = new FileReader(file);
            
            // 读取文件内容
            int character;
            while ((character = reader.read()) != -1) {
                System.out.print((char) character);
            }
        } catch (FileNotFoundException e) {
            System.out.println("File not found: " + e.getMessage());
        } catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
        } finally {
            // 确保资源被关闭
            try {
                if (reader != null) {
                    reader.close();
                }
            } catch (IOException e) {
                System.out.println("Error closing reader: " + e.getMessage());
            }
        }
    }
    
    public static void parseDate(String dateString) {
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
        try {
            Date date = format.parse(dateString);
            System.out.println("Parsed date: " + date);
        } catch (ParseException e) {
            System.out.println("Error parsing date: " + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        // try-catch块
        try {
            int result = 10 / 0; // 会抛出ArithmeticException
        } catch (ArithmeticException e) {
            System.out.println("Cannot divide by zero: " + e.getMessage());
        }
        
        // 多个catch块
        try {
            String str = null;
            System.out.println(str.length()); // 会抛出NullPointerException
        } catch (NullPointerException e) {
            System.out.println("Null reference: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("General exception: " + e.getMessage());
        }
        
        // try-with-resources (Java 7+)
        try (FileReader autoReader = new FileReader("example.txt")) {
            // 读取文件
            int character;
            while ((character = autoReader.read()) != -1) {
                System.out.print((char) character);
            }
        } catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
        }
        // 自动关闭资源，无需finally块
        
        // 抛出和处理自定义异常
        try {
            validateAge(-5);
        } catch (InvalidAgeException e) {
            System.out.println("Invalid age: " + e.getMessage());
        }
        
        try {
            validateAge(200);
        } catch (InvalidAgeException e) {
            System.out.println("Invalid age: " + e.getMessage());
        }
        
        try {
            validateAge(25);
        } catch (InvalidAgeException e) {
            System.out.println("Invalid age: " + e.getMessage());
        }
        
        // 调用可能抛出异常的方法
        readFile("nonexistent.txt");
        parseDate("2023-13-01"); // 无效日期
        parseDate("2023-01-01"); // 有效日期
    }
}
```

### 泛型

```java
// 泛型类
public class Box<T> {
    private T content;
    
    public void setContent(T content) {
        this.content = content;
    }
    
    public T getContent() {
        return content;
    }
    
    // 泛型方法
    public <U> void inspect(U u) {
        System.out.println("Type: " + u.getClass().getName());
        System.out.println("Value: " + u);
    }
}

// 泛型接口
public interface Container<T> {
    void add(T item);
    T get(int index);
    int size();
}

// 实现泛型接口
public class MyList<T> implements Container<T> {
    private Object[] elements = new Object[10];
    private int size = 0;
    
    @Override
    public void add(T item) {
        if (size < elements.length) {
            elements[size++] = item;
        } else {
            // 扩容逻辑
            Object[] newElements = new Object[elements.length * 2];
            System.arraycopy(elements, 0, newElements, 0, elements.length);
            elements = newElements;
            elements[size++] = item;
        }
    }
    
    @SuppressWarnings("unchecked")
    @Override
    public T get(int index) {
        if (index >= 0 && index < size) {
            return (T) elements[index];
        }
        throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
    }
    
    @Override
    public int size() {
        return size;
    }
}

// 通配符使用
public class WildcardDemo {
    // 使用无界通配符
    public static void printList(List<?> list) {
        for (Object elem : list) {
            System.out.print(elem + " ");
        }
        System.out.println();
    }
    
    // 使用上界通配符
    public static double sumOfList(List<? extends Number> list) {
        double sum = 0.0;
        for (Number n : list) {
            sum += n.doubleValue();
        }
        return sum;
    }
    
    // 使用下界通配符
    public static void addNumbers(List<? super Integer> list) {
        for (int i = 1; i <= 5; i++) {
            list.add(i);
        }
    }
    
    public static void main(String[] args) {
        // 使用泛型类
        Box<String> stringBox = new Box<>();
        stringBox.setContent("Hello");
        System.out.println("String box content: " + stringBox.getContent());
        
        Box<Integer> integerBox = new Box<>();
        integerBox.setContent(123);
        System.out.println("Integer box content: " + integerBox.getContent());
        
        // 调用泛型方法
        stringBox.inspect("Generic method test");
        integerBox.inspect(456);
        
        // 使用泛型接口实现
        MyList<String> stringList = new MyList<>();
        stringList.add("Apple");
        stringList.add("Banana");
        stringList.add("Orange");
        
        System.out.println("String list size: " + stringList.size());
        for (int i = 0; i < stringList.size(); i++) {
            System.out.println(stringList.get(i));
        }
        
        // 使用通配符
        List<String> stringList2 = Arrays.asList("A", "B", "C");
        List<Integer> integerList2 = Arrays.asList(1, 2, 3);
        
        printList(stringList2);
        printList(integerList2);
        
        System.out.println("Sum of integer list: " + sumOfList(integerList2));
        System.out.println("Sum of double list: " + sumOfList(Arrays.asList(1.1, 2.2, 3.3)));
        
        List<Number> numberList = new ArrayList<>();
        addNumbers(numberList);
        System.out.println("Number list after adding integers: " + numberList);
    }
}
```

### Lambda表达式和Stream API

```java
import java.util.*;
import java.util.function.*;
import java.util.stream.Collectors;

public class LambdaStreamDemo {
    public static void main(String[] args) {
        // Lambda表达式
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");
        
        // 使用匿名内部类
        Collections.sort(names, new Comparator<String>() {
            @Override
            public int compare(String a, String b) {
                return a.compareTo(b);
            }
        });
        
        // 使用Lambda表达式
        Collections.sort(names, (a, b) -> a.compareTo(b));
        
        // 更简洁的方法引用
        Collections.sort(names, String::compareTo);
        
        System.out.println("Sorted names: " + names);
        
        // 函数式接口
        Predicate<String> nameFilter = name -> name.startsWith("A");
        Function<String, Integer> nameLength = String::length;
        Consumer<String> namePrinter = System.out::println;
        Supplier<String> nameSupplier = () -> "Default Name";
        
        System.out.println("Names starting with 'A':");
        names.stream()
            .filter(nameFilter)
            .forEach(namePrinter);
        
        System.out.println("\nName lengths:");
        names.stream()
            .map(nameLength)
            .forEach(System.out::println);
        
        // Stream API
        List<Person> people = Arrays.asList(
            new Person("Alice", 25, "Engineer"),
            new Person("Bob", 30, "Manager"),
            new Person("Charlie", 35, "Engineer"),
            new Person("David", 28, "Designer"),
            new Person("Eve", 32, "Manager")
        );
        
        // 过滤和映射
        List<String> engineerNames = people.stream()
            .filter(person -> "Engineer".equals(person.getJob()))
            .map(Person::getName)
            .collect(Collectors.toList());
        
        System.out.println("\nEngineers: " + engineerNames);
        
        // 排序和限制
        List<Person> sortedByAge = people.stream()
            .sorted(Comparator.comparing(Person::getAge))
            .limit(3)
            .collect(Collectors.toList());
        
        System.out.println("\nTop 3 youngest people:");
        sortedByAge.forEach(person -> 
            System.out.println(person.getName() + " (" + person.getAge() + ")"));
        
        // 分组
        Map<String, List<Person>> peopleByJob = people.stream()
            .collect(Collectors.groupingBy(Person::getJob));
        
        System.out.println("\nPeople grouped by job:");
        peopleByJob.forEach((job, jobPeople) -> {
            System.out.println(job + ": " + 
                jobPeople.stream()
                    .map(Person::getName)
                    .collect(Collectors.joining(", ")));
        });
        
        // 聚合操作
        OptionalDouble averageAge = people.stream()
            .mapToInt(Person::getAge)
            .average();
        
        System.out.println("\nAverage age: " + 
            (averageAge.isPresent() ? averageAge.getAsDouble() : "N/A"));
        
        // 查找操作
        Optional<Person> firstEngineer = people.stream()
            .filter(person -> "Engineer".equals(person.getJob()))
            .findFirst();
        
        firstEngineer.ifPresent(person -> 
            System.out.println("\nFirst engineer: " + person.getName()));
        
        // 自定义收集器
        String namesString = people.stream()
            .map(Person::getName)
            .collect(Collectors.joining(", ", "[", "]"));
        
        System.out.println("\nAll names: " + namesString);
        
        // 并行流
        long startTime = System.currentTimeMillis();
        long count = people.parallelStream()
            .filter(person -> person.getAge() > 25)
            .count();
        long endTime = System.currentTimeMillis();
        
        System.out.println("\nNumber of people older than 25: " + count);
        System.out.println("Parallel processing time: " + (endTime - startTime) + "ms");
    }
    
    // 辅助类
    static class Person {
        private String name;
        private int age;
        private String job;
        
        public Person(String name, int age, String job) {
            this.name = name;
            this.age = age;
            this.job = job;
        }
        
        public String getName() {
            return name;
        }
        
        public int getAge() {
            return age;
        }
        
        public String getJob() {
            return job;
        }
    }
}
```

## 最佳实践

1. **代码风格**
   - 遵循Java命名规范（类名首字母大写，方法和变量名首字母小写）
   - 使用有意义的变量和方法名
   - 适当添加注释和文档
   - 保持代码简洁和可读性

2. **面向对象设计**
   - 遵循SOLID原则
   - 使用接口和抽象类实现多态
   - 避免过度继承，优先使用组合
   - 合理使用访问修饰符

3. **异常处理**
   - 使用具体的异常类型而不是通用异常
   - 在适当的地方处理异常，不要捕获所有异常
   - 提供有意义的错误信息
   - 使用try-with-resources管理资源

4. **性能优化**
   - 避免不必要的对象创建
   - 使用StringBuilder处理字符串拼接
   - 合理使用集合类
   - 注意自动装箱和拆箱的性能影响

5. **并发编程**
   - 使用线程安全的数据结构
   - 避免使用同步块，优先使用并发工具
   - 注意死锁和竞态条件
   - 合理使用线程池

## 贡献指南

欢迎对本学习笔记进行贡献！请遵循以下指南：

1. 确保内容准确、清晰、实用
2. 使用规范的Markdown格式
3. 代码示例需要完整且可运行
4. 添加适当的注释和说明
5. 保持目录结构的一致性

## 注意事项

- 注意Java版本差异，不同版本可能有不同的特性
- 在企业级开发中，注意安全性和性能问题
- 了解JVM的工作原理有助于编写更好的Java代码
- 持续关注Java新版本的特性和改进
- 在实际项目中，遵循团队和公司的编码规范

---

*最后更新: 2023年*