/**
 * 第一章示例代码：Java基础概念与环境搭建
 * 
 * 本文件包含第一章中介绍的所有示例代码，可以直接编译运行
 */

// 1. 最简单的HelloWorld程序
class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}

// 2. 包含基本信息输出的示例
class BasicInfo {
    public static void main(String[] args) {
        System.out.println("=== Java基础信息示例 ===");
        System.out.println("姓名：张三");
        System.out.println("年龄：25岁");
        System.out.println("爱好：编程、阅读、旅行");
        System.out.println("学习目标：掌握Java核心技术");
    }
}

// 3. 带方法调用的示例
class GreetingApp {
    public static void main(String[] args) {
        System.out.println("=== 欢迎学习Java ===");
        greetUser("李四");
        displayCurrentTime();
        showJavaFeatures();
    }
    
    /**
     * 向用户问好
     */
    public static void greetUser(String name) {
        System.out.println("你好，" + name + "！欢迎来到Java世界！");
    }
    
    /**
     * 显示当前时间
     */
    public static void displayCurrentTime() {
        java.util.Date now = new java.util.Date();
        System.out.println("当前时间：" + now);
    }
    
    /**
     * 展示Java主要特性
     */
    public static void showJavaFeatures() {
        System.out.println("\nJava主要特性：");
        System.out.println("- 面向对象编程");
        System.out.println("- 平台无关性");
        System.out.println("- 自动内存管理");
        System.out.println("- 强类型检查");
        System.out.println("- 多线程支持");
        System.out.println("- 丰富的类库");
    }
}

// 4. 环境信息检测示例
class EnvironmentCheck {
    public static void main(String[] args) {
        System.out.println("=== Java环境信息 ===");
        
        // Java版本信息
        System.out.println("Java版本: " + System.getProperty("java.version"));
        System.out.println("Java供应商: " + System.getProperty("java.vendor"));
        System.out.println("Java home: " + System.getProperty("java.home"));
        
        // 运行时信息
        System.out.println("操作系统名称: " + System.getProperty("os.name"));
        System.out.println("操作系统版本: " + System.getProperty("os.version"));
        System.out.println("操作系统架构: " + System.getProperty("os.arch"));
        
        // 用户信息
        System.out.println("用户名: " + System.getProperty("user.name"));
        System.out.println("用户目录: " + System.getProperty("user.dir"));
        System.out.println("临时目录: " + System.getProperty("java.io.tmpdir"));
        
        // 内存信息
        Runtime runtime = Runtime.getRuntime();
        System.out.println("最大内存: " + runtime.maxMemory() / (1024 * 1024) + " MB");
        System.out.println("总内存: " + runtime.totalMemory() / (1024 * 1024) + " MB");
        System.out.println("空闲内存: " + runtime.freeMemory() / (1024 * 1024) + " MB");
    }
}

// 5. 综合示例：学生信息管理系统
class StudentInfoSystem {
    public static void main(String[] args) {
        System.out.println("=== 学生信息管理系统演示 ===\n");
        
        // 创建几个学生对象并显示信息
        Student student1 = new Student("王五", 20, "计算机科学与技术", 85.5);
        Student student2 = new Student("赵六", 19, "软件工程", 92.0);
        
        student1.displayInfo();
        System.out.println(); // 空行
        student2.displayInfo();
        
        System.out.println("\n=== 系统统计 ===");
        System.out.println("学生总数: " + Student.getTotalStudents());
        System.out.println("平均成绩: " + String.format("%.2f", Student.getAverageGrade()));
    }
}

// 学生类定义
class Student {
    // 类变量（静态变量）
    private static int totalStudents = 0;
    private static double totalGrades = 0.0;
    
    // 实例变量
    private String name;
    private int age;
    private String major;
    private double grade;
    
    // 构造方法
    public Student(String name, int age, String major, double grade) {
        this.name = name;
        this.age = age;
        this.major = major;
        this.grade = grade;
        
        // 更新统计数据
        totalStudents++;
        totalGrades += grade;
    }
    
    // 实例方法：显示学生信息
    public void displayInfo() {
        System.out.println("学生姓名: " + name);
        System.out.println("年龄: " + age);
        System.out.println("专业: " + major);
        System.out.println("成绩: " + grade);
        System.out.println("是否优秀: " + (grade >= 90 ? "是" : "否"));
    }
    
    // 静态方法：获取学生总数
    public static int getTotalStudents() {
        return totalStudents;
    }
    
    // 静态方法：计算平均成绩
    public static double getAverageGrade() {
        return totalStudents > 0 ? totalGrades / totalStudents : 0.0;
    }
}

/*
 * 编译和运行说明：
 * 
 * 1. 编译所有类：
 *    javac chapter1_example.java
 * 
 * 2. 运行各个示例：
 *    java HelloWorld
 *    java BasicInfo
 *    java GreetingApp
 *    java EnvironmentCheck
 *    java StudentInfoSystem
 * 
 * 注意：由于一个.java文件中包含多个public类，只有与文件名相同的类可以是public的。
 * 在实际项目中，建议将每个类放在单独的文件中。
 */