/**
 * 第一章示例代码：展示面向对象基本原则的应用
 * 包含封装、继承、多态等基本概念
 */

// 基础动物类 - 展示封装性
class Animal {
    protected String name;
    protected int age;
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 封装：使用getter/setter方法访问私有属性
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
    
    // 基础行为方法
    public void eat() {
        System.out.println(name + " 正在吃东西...");
    }
    
    // 可被重写的虚方法
    public void makeSound() {
        System.out.println("动物发出声音");
    }
}

// 继承示例：狗类继承自动物类
class Dog extends Animal {
    private String breed; // 品种
    
    public Dog(String name, int age, String breed) {
        super(name, age); // 调用父类构造方法
        this.breed = breed;
    }
    
    // 多态：重写父类方法
    @Override
    public void makeSound() {
        System.out.println(name + " 汪汪叫");
    }
    
    // 子类特有的方法
    public void wagTail() {
        System.out.println(name + " 摇尾巴");
    }
    
    public String getBreed() {
        return breed;
    }
}

// 继承示例：猫类继承自动物类
class Cat extends Animal {
    private boolean isIndoor; // 是否为室内猫
    
    public Cat(String name, int age, boolean isIndoor) {
        super(name, age);
        this.isIndoor = isIndoor;
    }
    
    // 多态：重写父类方法
    @Override
    public void makeSound() {
        System.out.println(name + " 喵喵叫");
    }
    
    // 子类特有的方法
    public void climb() {
        System.out.println(name + " 爬树");
    }
    
    public boolean isIndoor() {
        return isIndoor;
    }
}

// 接口示例：展示接口的使用
interface Playable {
    void play();
}

// 实现接口的类
class Toy {
    public void play() {
        System.out.println("玩具被玩耍");
    }
}

// 主类 - 演示程序入口
public class Chapter1Example {
    public static void main(String[] args) {
        System.out.println("=== 第一章：设计模式基础概念示例 ===\n");
        
        // 创建不同的动物对象
        Dog dog = new Dog("旺财", 3, "金毛");
        Cat cat = new Cat("咪咪", 2, true);
        
        // 展示多态性：同样的方法调用产生不同的行为
        System.out.println("1. 多态性演示：");
        dog.makeSound(); // 输出：旺财 汪汪叫
        cat.makeSound(); // 输出：咪咪 喵喵叫
        
        // 展示继承和封装
        System.out.println("\n2. 继承和封装演示：");
        System.out.println("狗狗的名字：" + dog.getName());
        System.out.println("猫咪的年龄：" + cat.getAge());
        System.out.println("狗狗的品种：" + dog.getBreed());
        System.out.println("是否为室内猫：" + cat.isIndoor());
        
        // 调用各自的方法
        System.out.println("\n3. 特有方法演示：");
        dog.wagTail(); // 狗特有的方法
        cat.climb();   // 猫特有的方法
        
        // 展示向上转型和动态绑定
        System.out.println("\n4. 向上转型演示：");
        Animal[] animals = {dog, cat};
        for (Animal animal : animals) {
            animal.makeSound(); // 运行时决定调用哪个方法
        }
        
        System.out.println("\n=== 示例结束 ===");
    }
}