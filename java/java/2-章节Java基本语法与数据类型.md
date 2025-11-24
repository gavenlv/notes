# 第2章：Java基本语法与数据类型

## 2.1 Java程序基本结构

### 2.1.1 程序入口
每个Java应用程序都必须有一个main方法作为程序的入口点：
```java
public static void main(String[] args) {
    // 程序代码
}
```

### 2.1.2 基本语法元素
- **标识符**：类名、变量名、方法名等的名称
- **关键字**：具有特殊含义的保留字，如public、class、static等
- **注释**：单行注释(//)、多行注释(/* */)、文档注释(/** */)
- **语句**：以分号(;)结尾的代码行

## 2.2 变量与常量

### 2.2.1 变量声明
Java是强类型语言，每个变量在使用前必须声明其类型：
```java
int age;           // 声明一个整型变量
double salary;     // 声明一个双精度浮点型变量
String name;       // 声明一个字符串变量
```

### 2.2.2 变量初始化
```java
int age = 25;                    // 声明并初始化
double salary = 5000.50;         // 声明并初始化
String name = "张三";             // 声明并初始化
```

### 2.2.3 常量定义
使用final关键字定义常量：
```java
final double PI = 3.14159;       // 数学常数π
final int MAX_SIZE = 100;        // 最大大小
```

## 2.3 基本数据类型

Java提供了8种基本数据类型，分为四类：

### 2.3.1 整数类型

| 类型 | 位数 | 范围 | 默认值 |
|------|------|------|--------|
| byte | 8位 | -128 到 127 | 0 |
| short | 16位 | -32,768 到 32,767 | 0 |
| int | 32位 | -2,147,483,648 到 2,147,483,647 | 0 |
| long | 64位 | -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807 | 0L |

```java
byte b = 127;
short s = 32767;
int i = 2147483647;
long l = 9223372036854775807L;  // 注意long类型需要加L后缀
```

### 2.3.2 浮点类型

| 类型 | 位数 | 精度 | 默认值 |
|------|------|------|--------|
| float | 32位 | 6-7位有效数字 | 0.0f |
| double | 64位 | 15位有效数字 | 0.0d |

```java
float f = 3.14f;        // float类型需要加f后缀
double d = 3.14159265;  // double是默认的浮点类型
```

### 2.3.3 字符类型
```java
char c1 = 'A';          // 字符字面量用单引号
char c2 = '\u0041';     // Unicode字符
char c3 = 65;           // ASCII码值
```

### 2.3.4 布尔类型
```java
boolean flag1 = true;
boolean flag2 = false;
```

## 2.4 类型转换

### 2.4.1 自动类型转换（隐式转换）
Java会自动进行安全的类型转换，转换方向为：
byte → short → int → long → float → double
char → int → long → float → double

```java
int i = 100;
long l = i;        // 自动转换
float f = i;       // 自动转换
```

### 2.4.2 强制类型转换（显式转换）
当需要进行可能丢失精度的转换时，必须使用强制类型转换：
```java
double d = 123.456;
int i = (int) d;   // 强制转换，结果为123，小数部分被截断
```

### 2.4.3 包装类
每种基本数据类型都有对应的包装类：

| 基本类型 | 包装类 |
|----------|--------|
| byte | Byte |
| short | Short |
| int | Integer |
| long | Long |
| float | Float |
| double | Double |
| char | Character |
| boolean | Boolean |

```java
Integer intObj = new Integer(100);  // 装箱
int value = intObj.intValue();      // 拆箱

// 自动装箱和拆箱（Java 5+）
Integer autoBoxed = 100;            // 自动装箱
int autoUnboxed = autoBoxed;        // 自动拆箱
```

## 2.5 运算符

### 2.5.1 算术运算符
```java
int a = 10, b = 3;
int sum = a + b;        // 加法：13
int diff = a - b;       // 减法：7
int product = a * b;    // 乘法：30
int quotient = a / b;   // 除法：3（整数除法）
int remainder = a % b;  // 取余：1
```

### 2.5.2 关系运算符
```java
int x = 5, y = 10;
boolean result1 = x > y;   // 大于：false
boolean result2 = x < y;   // 小于：true
boolean result3 = x >= 5;  // 大于等于：true
boolean result4 = x <= y;  // 小于等于：true
boolean result5 = x == y;  // 等于：false
boolean result6 = x != y;  // 不等于：true
```

### 2.5.3 逻辑运算符
```java
boolean flag1 = true, flag2 = false;
boolean result1 = flag1 && flag2;  // 逻辑与：false
boolean result2 = flag1 || flag2;  // 逻辑或：true
boolean result3 = !flag1;          // 逻辑非：false
```

### 2.5.4 位运算符
```java
int a = 5;   // 二进制：101
int b = 3;   // 二进制：011
int result1 = a & b;   // 按位与：001 (1)
int result2 = a | b;   // 按位或：111 (7)
int result3 = a ^ b;   // 按位异或：110 (6)
int result4 = ~a;      // 按位取反：...11111010 (-6)
int result5 = a << 1;  // 左移一位：1010 (10)
int result6 = a >> 1;  // 右移一位：010 (2)
```

### 2.5.5 赋值运算符
```java
int x = 10;
x += 5;    // 等价于 x = x + 5
x -= 3;    // 等价于 x = x - 3
x *= 2;    // 等价于 x = x * 2
x /= 4;    // 等价于 x = x / 4
x %= 3;    // 等价于 x = x % 3
```

### 2.5.6 条件运算符（三元运算符）
```java
int a = 10, b = 20;
int max = (a > b) ? a : b;  // 如果a>b为真，返回a，否则返回b
```

## 2.6 字符串类型

### 2.6.1 String类
String是Java中最重要的类之一，用于表示字符串：
```java
String str1 = "Hello";           // 字符串字面量
String str2 = new String("World"); // 使用构造方法
String str3 = str1 + " " + str2;  // 字符串连接
```

### 2.6.2 常用String方法
```java
String text = "Hello World";
int length = text.length();           // 获取长度：11
char ch = text.charAt(0);             // 获取指定位置字符：'H'
String upper = text.toUpperCase();    // 转大写："HELLO WORLD"
String lower = text.toLowerCase();    // 转小写："hello world"
boolean contains = text.contains("World"); // 是否包含："true"
String replaced = text.replace("World", "Java"); // 替换："Hello Java"
```

### 2.6.3 StringBuilder和StringBuffer
对于频繁修改的字符串，应使用StringBuilder（单线程）或StringBuffer（多线程）：
```java
StringBuilder sb = new StringBuilder();
sb.append("Hello");
sb.append(" ");
sb.append("World");
String result = sb.toString();  // "Hello World"
```

## 2.7 数组

### 2.7.1 一维数组
```java
// 声明和初始化
int[] numbers = new int[5];        // 声明并分配空间
int[] values = {1, 2, 3, 4, 5};    // 声明并初始化
String[] names = new String[]{"张三", "李四", "王五"};

// 访问数组元素
numbers[0] = 10;                   // 给第一个元素赋值
int first = numbers[0];            // 获取第一个元素的值

// 数组长度
int length = numbers.length;
```

### 2.7.2 多维数组
```java
// 二维数组
int[][] matrix = new int[3][4];    // 3行4列
int[][] data = {{1, 2}, {3, 4}, {5, 6}};  // 初始化

// 访问二维数组元素
matrix[0][0] = 10;
int value = matrix[0][0];
```

### 2.7.3 数组遍历
```java
int[] numbers = {1, 2, 3, 4, 5};

// 传统for循环
for (int i = 0; i < numbers.length; i++) {
    System.out.println(numbers[i]);
}

// 增强for循环（for-each）
for (int num : numbers) {
    System.out.println(num);
}
```

## 2.8 控制流程语句

### 2.8.1 条件语句

#### if语句
```java
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
```

#### switch语句
```java
int day = 3;
switch (day) {
    case 1:
        System.out.println("星期一");
        break;
    case 2:
        System.out.println("星期二");
        break;
    case 3:
        System.out.println("星期三");
        break;
    default:
        System.out.println("其他");
        break;
}
```

### 2.8.2 循环语句

#### for循环
```java
// 计算1到100的和
int sum = 0;
for (int i = 1; i <= 100; i++) {
    sum += i;
}
System.out.println("和为：" + sum);
```

#### while循环
```java
int i = 1;
int sum = 0;
while (i <= 100) {
    sum += i;
    i++;
}
System.out.println("和为：" + sum);
```

#### do-while循环
```java
int i = 1;
int sum = 0;
do {
    sum += i;
    i++;
} while (i <= 100);
System.out.println("和为：" + sum);
```

### 2.8.3 跳转语句
```java
// break语句 - 跳出循环
for (int i = 1; i <= 10; i++) {
    if (i == 5) {
        break;  // 当i等于5时跳出循环
    }
    System.out.println(i);
}

// continue语句 - 跳过当前循环迭代
for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) {
        continue;  // 跳过偶数
    }
    System.out.println(i);  // 只输出奇数
}
```

## 2.9 输入输出

### 2.9.1 标准输出
```java
System.out.println("Hello World");     // 输出并换行
System.out.print("Hello ");            // 输出不换行
System.out.printf("姓名：%s，年龄：%d", "张三", 25);  // 格式化输出
```

### 2.9.2 标准输入（Scanner类）
```java
import java.util.Scanner;

Scanner scanner = new Scanner(System.in);

// 读取整数
System.out.print("请输入一个整数：");
int number = scanner.nextInt();

// 读取字符串
System.out.print("请输入姓名：");
String name = scanner.next();  // 读取单个单词
// String name = scanner.nextLine();  // 读取整行

scanner.close();
```

## 2.10 最佳实践

### 2.10.1 命名规范
```java
// 类名：大驼峰命名法
class StudentInfo {
    // 常量：全大写，单词间用下划线分隔
    private static final int MAX_AGE = 150;
    
    // 成员变量：小驼峰命名法
    private String studentName;
    private int studentAge;
    
    // 方法名：小驼峰命名法
    public void setStudentName(String studentName) {
        // 局部变量：小驼峰命名法
        String trimmedName = studentName.trim();
        this.studentName = trimmedName;
    }
}
```

### 2.10.2 变量声明和初始化
```java
// 好的做法：在使用前声明并初始化
int count = 0;
String message = "Hello";

// 避免的做法：声明但不初始化
int uninitializedValue;  // 可能导致编译错误
```

### 2.10.3 类型选择建议
- 对于整数，优先使用int类型
- 对于浮点数，优先使用double类型
- 对于单个字符，使用char类型
- 对于字符串，使用String类
- 对于布尔值，使用boolean类型

## 2.11 常见错误和注意事项

### 2.11.1 数值溢出
```java
// 错误示例：整数溢出
int maxInt = Integer.MAX_VALUE;
int overflow = maxInt + 1;  // 结果为负数

// 正确做法：使用long类型
long safeValue = (long) maxInt + 1;
```

### 2.11.2 浮点数比较
```java
// 错误示例：直接比较浮点数
double a = 0.1 + 0.2;
double b = 0.3;
if (a == b) {  // 可能不相等
    System.out.println("相等");
}

// 正确做法：使用误差范围比较
double epsilon = 1e-10;
if (Math.abs(a - b) < epsilon) {
    System.out.println("相等");
}
```

### 2.11.3 数组越界
```java
int[] numbers = {1, 2, 3};
// 错误示例：数组越界
// int value = numbers[3];  // ArrayIndexOutOfBoundsException

// 正确做法：检查数组边界
if (index >= 0 && index < numbers.length) {
    int value = numbers[index];
}
```

## 2.12 总结

本章详细介绍了Java的基本语法和数据类型，包括变量声明、基本数据类型、类型转换、运算符、字符串处理、数组操作以及控制流程语句。掌握了这些基础知识，就可以编写简单的Java程序了。

下一章我们将深入学习面向对象编程的核心概念，包括类、对象、封装、继承和多态等重要特性。

## 2.13 练习题

1. 编写一个程序，计算并输出圆的面积和周长（半径由用户输入）
2. 创建一个数组，存储10个学生的成绩，计算平均分、最高分和最低分
3. 编写一个程序，判断用户输入的年份是否为闰年
4. 实现一个简单的计算器程序，支持加减乘除运算
5. 编写一个程序，统计一段文本中各个字母出现的次数

通过本章的学习，您应该能够：
- 理解Java基本语法结构
- 掌握各种数据类型的使用方法
- 熟练运用运算符进行计算
- 处理字符串和数组操作
- 使用控制流程语句控制程序执行
- 避免常见的编程错误