import java.util.HashMap;
import java.util.Map;

/**
 * 第六章：原型模式代码示例
 */

// 1. 基本原型模式示例
// 抽象原型类
interface Prototype {
    Prototype clone();
}

// 具体原型类
class Sheep implements Prototype {
    private String name;
    private String color;
    private int age;
    
    public Sheep(String name, String color, int age) {
        this.name = name;
        this.color = color;
        this.age = age;
    }
    
    // 实现克隆方法
    @Override
    public Prototype clone() {
        return new Sheep(this.name, this.color, this.age);
    }
    
    // Getter和Setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
    
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
    
    @Override
    public String toString() {
        return "Sheep{name='" + name + "', color='" + color + "', age=" + age + "}";
    }
}

// 2. 使用Java内置Cloneable接口的原型模式
class Employee implements Cloneable {
    private String name;
    private int age;
    private String department;
    private Address address; // 引用类型字段
    
    public Employee(String name, int age, String department) {
        this.name = name;
        this.age = age;
        this.department = department;
        this.address = new Address(); // 初始化地址
    }
    
    // 深拷贝实现
    @Override
    protected Object clone() throws CloneNotSupportedException {
        Employee cloned = (Employee) super.clone();
        // 对引用类型进行深拷贝
        cloned.address = (Address) this.address.clone();
        return cloned;
    }
    
    // 浅拷贝实现
    public Employee shallowCopy() throws CloneNotSupportedException {
        return (Employee) super.clone();
    }
    
    // Getter和Setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
    
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    
    public Address getAddress() { return address; }
    public void setAddress(Address address) { this.address = address; }
    
    @Override
    public String toString() {
        return "Employee{name='" + name + "', age=" + age + 
               ", department='" + department + "', address=" + address + "}";
    }
}

// 地址类
class Address implements Cloneable {
    private String street;
    private String city;
    private String zipCode;
    
    public Address() {
        this.street = "";
        this.city = "";
        this.zipCode = "";
    }
    
    public Address(String street, String city, String zipCode) {
        this.street = street;
        this.city = city;
        this.zipCode = zipCode;
    }
    
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
    
    // Getter和Setter方法
    public String getStreet() { return street; }
    public void setStreet(String street) { this.street = street; }
    
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    
    public String getZipCode() { return zipCode; }
    public void setZipCode(String zipCode) { this.zipCode = zipCode; }
    
    @Override
    public String toString() {
        return "Address{street='" + street + "', city='" + city + "', zipCode='" + zipCode + "'}";
    }
}

// 3. 原型管理器
class PrototypeManager {
    private Map<String, Prototype> prototypes = new HashMap<>();
    
    // 注册原型
    public void registerPrototype(String key, Prototype prototype) {
        prototypes.put(key, prototype);
    }
    
    // 获取原型并克隆
    public Prototype createPrototype(String key) {
        Prototype prototype = prototypes.get(key);
        if (prototype != null) {
            return prototype.clone();
        }
        return null;
    }
    
    // 取消注册
    public void unregisterPrototype(String key) {
        prototypes.remove(key);
    }
    
    // 获取所有注册的原型键
    public String[] getPrototypeKeys() {
        return prototypes.keySet().toArray(new String[0]);
    }
}

// 4. 图形编辑器示例
// 图形接口
interface Shape extends Cloneable, Prototype {
    void draw();
    Shape clone();
    String getType();
}

// 具体图形类 - 矩形
class Rectangle implements Shape {
    private int width;
    private int height;
    private String color;
    
    public Rectangle() {
        this.width = 0;
        this.height = 0;
        this.color = "white";
    }
    
    public Rectangle(Rectangle rectangle) {
        this.width = rectangle.width;
        this.height = rectangle.height;
        this.color = rectangle.color;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing Rectangle[width=" + width + ", height=" + height + ", color=" + color + "]");
    }
    
    @Override
    public Shape clone() {
        return new Rectangle(this);
    }
    
    @Override
    public String getType() {
        return "Rectangle";
    }
    
    // Getter和Setter方法
    public int getWidth() { return width; }
    public void setWidth(int width) { this.width = width; }
    
    public int getHeight() { return height; }
    public void setHeight(int height) { this.height = height; }
    
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
}

// 具体图形类 - 圆形
class Circle implements Shape {
    private int radius;
    private String color;
    
    public Circle() {
        this.radius = 0;
        this.color = "white";
    }
    
    public Circle(Circle circle) {
        this.radius = circle.radius;
        this.color = circle.color;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing Circle[radius=" + radius + ", color=" + color + "]");
    }
    
    @Override
    public Shape clone() {
        return new Circle(this);
    }
    
    @Override
    public String getType() {
        return "Circle";
    }
    
    // Getter和Setter方法
    public int getRadius() { return radius; }
    public void setRadius(int radius) { this.radius = radius; }
    
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
}

// 5. 文档模板系统
class DocumentTemplate implements Cloneable {
    private String title;
    private String content;
    private String author;
    private String[] tags;
    
    public DocumentTemplate(String title, String content, String author, String[] tags) {
        this.title = title;
        this.content = content;
        this.author = author;
        this.tags = tags != null ? tags.clone() : new String[0];
    }
    
    // 深拷贝实现
    @Override
    protected Object clone() throws CloneNotSupportedException {
        DocumentTemplate cloned = (DocumentTemplate) super.clone();
        // 对数组进行深拷贝
        cloned.tags = this.tags != null ? this.tags.clone() : null;
        return cloned;
    }
    
    // 创建基于模板的新文档
    public DocumentTemplate createNewDocument(String newTitle, String newAuthor) {
        try {
            DocumentTemplate newDoc = (DocumentTemplate) this.clone();
            newDoc.setTitle(newTitle);
            newDoc.setAuthor(newAuthor);
            return newDoc;
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException("无法克隆文档模板", e);
        }
    }
    
    // Getter和Setter方法
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    
    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }
    
    public String[] getTags() { return tags != null ? tags.clone() : null; }
    public void setTags(String[] tags) { this.tags = tags != null ? tags.clone() : null; }
    
    @Override
    public String toString() {
        return "DocumentTemplate{title='" + title + "', author='" + author + 
               "', tags=" + java.util.Arrays.toString(tags) + "}";
    }
}

// 6. 深拷贝示例
class Department implements Cloneable {
    private String name;
    private Employee[] employees;
    
    public Department(String name, Employee[] employees) {
        this.name = name;
        this.employees = employees != null ? employees.clone() : new Employee[0];
    }
    
    // 深拷贝实现
    @Override
    protected Object clone() throws CloneNotSupportedException {
        Department cloned = (Department) super.clone();
        // 对员工数组进行深拷贝
        if (this.employees != null) {
            cloned.employees = new Employee[this.employees.length];
            for (int i = 0; i < this.employees.length; i++) {
                cloned.employees[i] = (Employee) this.employees[i].clone();
            }
        }
        return cloned;
    }
    
    // Getter和Setter方法
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public Employee[] getEmployees() { 
        return employees != null ? employees.clone() : null; 
    }
    
    @Override
    public String toString() {
        return "Department{name='" + name + "', employeesCount=" + 
               (employees != null ? employees.length : 0) + "}";
    }
}

public class Chapter6Example {
    public static void main(String[] args) {
        System.out.println("=== 原型模式示例 ===\n");
        
        try {
            // 1. 基本原型模式示例
            System.out.println("1. 基本原型模式示例：");
            Sheep originalSheep = new Sheep("Dolly", "White", 3);
            System.out.println("原始羊：" + originalSheep);
            
            Sheep clonedSheep = (Sheep) originalSheep.clone();
            clonedSheep.setName("Dolly Clone");
            clonedSheep.setAge(1);
            System.out.println("克隆羊：" + clonedSheep);
            System.out.println();
            
            // 2. 浅拷贝与深拷贝示例
            System.out.println("2. 浅拷贝与深拷贝示例：");
            Employee originalEmployee = new Employee("张三", 30, "IT部");
            originalEmployee.getAddress().setStreet("中山路123号");
            originalEmployee.getAddress().setCity("北京");
            originalEmployee.getAddress().setZipCode("100000");
            
            // 浅拷贝
            Employee shallowCopy = originalEmployee.shallowCopy();
            shallowCopy.setName("张三(浅拷贝)");
            // 修改浅拷贝对象的地址信息
            shallowCopy.getAddress().setStreet("长安街456号");
            
            // 深拷贝
            Employee deepCopy = (Employee) originalEmployee.clone();
            deepCopy.setName("张三(深拷贝)");
            // 修改深拷贝对象的地址信息
            deepCopy.getAddress().setStreet("王府井789号");
            
            System.out.println("原始员工：" + originalEmployee);
            System.out.println("浅拷贝员工：" + shallowCopy);
            System.out.println("深拷贝员工：" + deepCopy);
            System.out.println();
            
            // 3. 原型管理器示例
            System.out.println("3. 原型管理器示例：");
            PrototypeManager manager = new PrototypeManager();
            manager.registerPrototype("sheep", new Sheep("原型羊", "Black", 2));
            manager.registerPrototype("circle", new Circle());
            manager.registerPrototype("rectangle", new Rectangle());
            
            Sheep sheepPrototype = (Sheep) manager.createPrototype("sheep");
            sheepPrototype.setName("从原型管理器创建的羊");
            System.out.println("从原型管理器创建的羊：" + sheepPrototype);
            
            Circle circlePrototype = (Circle) manager.createPrototype("circle");
            circlePrototype.setRadius(10);
            circlePrototype.setColor("Red");
            circlePrototype.draw();
            
            Rectangle rectPrototype = (Rectangle) manager.createPrototype("rectangle");
            rectPrototype.setWidth(20);
            rectPrototype.setHeight(15);
            rectPrototype.setColor("Blue");
            rectPrototype.draw();
            System.out.println();
            
            // 4. 图形编辑器示例
            System.out.println("4. 图形编辑器示例：");
            Circle originalCircle = new Circle();
            originalCircle.setRadius(5);
            originalCircle.setColor("Green");
            
            Circle clonedCircle = (Circle) originalCircle.clone();
            clonedCircle.setRadius(10);
            clonedCircle.setColor("Yellow");
            
            originalCircle.draw();
            clonedCircle.draw();
            System.out.println();
            
            // 5. 文档模板系统示例
            System.out.println("5. 文档模板系统示例：");
            String[] tags = {"模板", "示例", "原型模式"};
            DocumentTemplate template = new DocumentTemplate(
                "文档模板", 
                "这是一个文档模板的内容", 
                "作者", 
                tags
            );
            
            DocumentTemplate newDoc = template.createNewDocument("新文档", "新作者");
            newDoc.setContent("这是基于模板创建的新文档内容");
            
            System.out.println("模板文档：" + template);
            System.out.println("新文档：" + newDoc);
            System.out.println();
            
            // 6. 深拷贝示例
            System.out.println("6. 深拷贝示例：");
            Employee[] employees = {
                new Employee("员工1", 25, "开发部"),
                new Employee("员工2", 28, "测试部")
            };
            Department originalDept = new Department("技术部", employees);
            
            Department clonedDept = (Department) originalDept.clone();
            clonedDept.setName("技术部(克隆)");
            // 修改克隆部门中员工的信息
            if (clonedDept.getEmployees().length > 0) {
                clonedDept.getEmployees()[0].setAge(26);
            }
            
            System.out.println("原始部门：" + originalDept);
            System.out.println("克隆部门：" + clonedDept);
            
        } catch (CloneNotSupportedException e) {
            e.printStackTrace();
        }
    }
}