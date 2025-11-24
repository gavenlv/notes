/**
 * 第二章示例代码：Java基本语法与数据类型
 * 
 * 本文件包含第二章中介绍的所有示例代码，可以直接编译运行
 */

import java.util.Scanner;

// 1. 基本数据类型示例
class DataTypesDemo {
    public static void main(String[] args) {
        System.out.println("=== 基本数据类型示例 ===");
        
        // 整数类型
        byte b = 127;
        short s = 32767;
        int i = 2147483647;
        long l = 9223372036854775807L;
        
        System.out.println("byte: " + b);
        System.out.println("short: " + s);
        System.out.println("int: " + i);
        System.out.println("long: " + l);
        
        // 浮点类型
        float f = 3.14159f;
        double d = 3.141592653589793;
        
        System.out.println("float: " + f);
        System.out.println("double: " + d);
        
        // 字符类型
        char c1 = 'A';
        char c2 = '\u0041';
        char c3 = 65;
        
        System.out.println("char1: " + c1);
        System.out.println("char2: " + c2);
        System.out.println("char3: " + c3);
        
        // 布尔类型
        boolean flag1 = true;
        boolean flag2 = false;
        
        System.out.println("boolean1: " + flag1);
        System.out.println("boolean2: " + flag2);
    }
}

// 2. 类型转换示例
class TypeConversionDemo {
    public static void main(String[] args) {
        System.out.println("=== 类型转换示例 ===");
        
        // 自动类型转换
        int intValue = 100;
        long longValue = intValue;        // int -> long
        float floatValue = intValue;      // int -> float
        double doubleValue = intValue;    // int -> double
        
        System.out.println("自动类型转换:");
        System.out.println("int to long: " + longValue);
        System.out.println("int to float: " + floatValue);
        System.out.println("int to double: " + doubleValue);
        
        // 强制类型转换
        double d = 123.456;
        int i = (int) d;                  // double -> int，小数部分被截断
        
        System.out.println("\n强制类型转换:");
        System.out.println("double: " + d);
        System.out.println("强制转换为int: " + i);
        
        // 包装类示例
        Integer intObj = new Integer(100);  // 装箱
        int value = intObj.intValue();      // 拆箱
        
        System.out.println("\n包装类示例:");
        System.out.println("Integer对象: " + intObj);
        System.out.println("拆箱后的值: " + value);
        
        // 自动装箱和拆箱
        Integer autoBoxed = 100;            // 自动装箱
        int autoUnboxed = autoBoxed;        // 自动拆箱
        
        System.out.println("自动装箱: " + autoBoxed);
        System.out.println("自动拆箱: " + autoUnboxed);
    }
}

// 3. 运算符示例
class OperatorsDemo {
    public static void main(String[] args) {
        System.out.println("=== 运算符示例 ===");
        
        // 算术运算符
        int a = 10, b = 3;
        System.out.println("算术运算符:");
        System.out.println(a + " + " + b + " = " + (a + b));
        System.out.println(a + " - " + b + " = " + (a - b));
        System.out.println(a + " * " + b + " = " + (a * b));
        System.out.println(a + " / " + b + " = " + (a / b));
        System.out.println(a + " % " + b + " = " + (a % b));
        
        // 关系运算符
        System.out.println("\n关系运算符:");
        System.out.println(a + " > " + b + " = " + (a > b));
        System.out.println(a + " < " + b + " = " + (a < b));
        System.out.println(a + " >= " + b + " = " + (a >= b));
        System.out.println(a + " <= " + b + " = " + (a <= b));
        System.out.println(a + " == " + b + " = " + (a == b));
        System.out.println(a + " != " + b + " = " + (a != b));
        
        // 逻辑运算符
        boolean flag1 = true, flag2 = false;
        System.out.println("\n逻辑运算符:");
        System.out.println(flag1 + " && " + flag2 + " = " + (flag1 && flag2));
        System.out.println(flag1 + " || " + flag2 + " = " + (flag1 || flag2));
        System.out.println("!" + flag1 + " = " + (!flag1));
        
        // 位运算符
        int x = 5, y = 3;
        System.out.println("\n位运算符:");
        System.out.println(x + " & " + y + " = " + (x & y));
        System.out.println(x + " | " + y + " = " + (x | y));
        System.out.println(x + " ^ " + y + " = " + (x ^ y));
        System.out.println("~" + x + " = " + (~x));
        System.out.println(x + " << 1 = " + (x << 1));
        System.out.println(x + " >> 1 = " + (x >> 1));
        
        // 赋值运算符
        int z = 10;
        System.out.println("\n赋值运算符:");
        System.out.println("初始值: " + z);
        System.out.println("z += 5: " + (z += 5));
        System.out.println("z -= 3: " + (z -= 3));
        System.out.println("z *= 2: " + (z *= 2));
        System.out.println("z /= 4: " + (z /= 4));
        System.out.println("z %= 3: " + (z %= 3));
        
        // 条件运算符
        int max = (a > b) ? a : b;
        System.out.println("\n条件运算符:");
        System.out.println("max(" + a + ", " + b + ") = " + max);
    }
}

// 4. 字符串操作示例
class StringDemo {
    public static void main(String[] args) {
        System.out.println("=== 字符串操作示例 ===");
        
        // String类
        String str1 = "Hello";
        String str2 = new String("World");
        String str3 = str1 + " " + str2;
        
        System.out.println("字符串连接: " + str3);
        
        // 常用String方法
        String text = "Hello World";
        System.out.println("\n字符串操作:");
        System.out.println("原字符串: " + text);
        System.out.println("长度: " + text.length());
        System.out.println("第一个字符: " + text.charAt(0));
        System.out.println("转大写: " + text.toUpperCase());
        System.out.println("转小写: " + text.toLowerCase());
        System.out.println("是否包含'World': " + text.contains("World"));
        System.out.println("替换'World'为'Java': " + text.replace("World", "Java"));
        
        // StringBuilder示例
        StringBuilder sb = new StringBuilder();
        sb.append("Hello");
        sb.append(" ");
        sb.append("World");
        sb.append("!");
        
        System.out.println("\nStringBuilder操作:");
        System.out.println("构建的字符串: " + sb.toString());
        System.out.println("反转后: " + sb.reverse().toString());
    }
}

// 5. 数组操作示例
class ArrayDemo {
    public static void main(String[] args) {
        System.out.println("=== 数组操作示例 ===");
        
        // 一维数组
        int[] numbers = {1, 2, 3, 4, 5};
        String[] names = new String[]{"张三", "李四", "王五"};
        
        System.out.println("一维数组:");
        System.out.print("numbers数组: ");
        for (int i = 0; i < numbers.length; i++) {
            System.out.print(numbers[i] + " ");
        }
        System.out.println();
        
        System.out.print("names数组: ");
        for (String name : names) {
            System.out.print(name + " ");
        }
        System.out.println();
        
        // 多维数组
        int[][] matrix = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
        
        System.out.println("\n二维数组:");
        for (int i = 0; i < matrix.length; i++) {
            for (int j = 0; j < matrix[i].length; j++) {
                System.out.print(matrix[i][j] + " ");
            }
            System.out.println();
        }
        
        // 数组操作示例
        int[] scores = {85, 92, 78, 96, 88};
        int sum = 0;
        int max = scores[0];
        int min = scores[0];
        
        for (int score : scores) {
            sum += score;
            if (score > max) max = score;
            if (score < min) min = score;
        }
        
        double average = (double) sum / scores.length;
        
        System.out.println("\n成绩统计:");
        System.out.println("成绩数组: " + java.util.Arrays.toString(scores));
        System.out.println("总分: " + sum);
        System.out.println("平均分: " + String.format("%.2f", average));
        System.out.println("最高分: " + max);
        System.out.println("最低分: " + min);
    }
}

// 6. 控制流程语句示例
class ControlFlowDemo {
    public static void main(String[] args) {
        System.out.println("=== 控制流程语句示例 ===");
        
        // 条件语句
        int score = 85;
        System.out.println("分数: " + score);
        if (score >= 90) {
            System.out.println("等级: 优秀");
        } else if (score >= 80) {
            System.out.println("等级: 良好");
        } else if (score >= 60) {
            System.out.println("等级: 及格");
        } else {
            System.out.println("等级: 不及格");
        }
        
        // switch语句
        int day = 3;
        System.out.println("\n星期: " + day);
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
            case 4:
                System.out.println("星期四");
                break;
            case 5:
                System.out.println("星期五");
                break;
            case 6:
                System.out.println("星期六");
                break;
            case 7:
                System.out.println("星期日");
                break;
            default:
                System.out.println("无效的星期");
                break;
        }
        
        // 循环语句
        System.out.println("\n循环语句示例:");
        
        // for循环
        System.out.print("for循环 (1-5): ");
        for (int i = 1; i <= 5; i++) {
            System.out.print(i + " ");
        }
        System.out.println();
        
        // while循环
        System.out.print("while循环 (1-5): ");
        int i = 1;
        while (i <= 5) {
            System.out.print(i + " ");
            i++;
        }
        System.out.println();
        
        // do-while循环
        System.out.print("do-while循环 (1-5): ");
        int j = 1;
        do {
            System.out.print(j + " ");
            j++;
        } while (j <= 5);
        System.out.println();
        
        // 跳转语句
        System.out.println("\n跳转语句示例:");
        System.out.print("break示例 (1-10，遇到5时跳出): ");
        for (int k = 1; k <= 10; k++) {
            if (k == 5) {
                break;
            }
            System.out.print(k + " ");
        }
        System.out.println();
        
        System.out.print("continue示例 (1-10，跳过偶数): ");
        for (int k = 1; k <= 10; k++) {
            if (k % 2 == 0) {
                continue;
            }
            System.out.print(k + " ");
        }
        System.out.println();
    }
}

// 7. 综合示例：简单计算器
class SimpleCalculator {
    public static void main(String[] args) {
        System.out.println("=== 简单计算器 ===");
        
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("请输入第一个数字: ");
        double num1 = scanner.nextDouble();
        
        System.out.print("请输入运算符 (+, -, *, /): ");
        String operator = scanner.next();
        
        System.out.print("请输入第二个数字: ");
        double num2 = scanner.nextDouble();
        
        double result = 0;
        boolean validOperator = true;
        
        switch (operator) {
            case "+":
                result = num1 + num2;
                break;
            case "-":
                result = num1 - num2;
                break;
            case "*":
                result = num1 * num2;
                break;
            case "/":
                if (num2 != 0) {
                    result = num1 / num2;
                } else {
                    System.out.println("错误：除数不能为零！");
                    validOperator = false;
                }
                break;
            default:
                System.out.println("错误：无效的运算符！");
                validOperator = false;
                break;
        }
        
        if (validOperator) {
            System.out.println("计算结果: " + num1 + " " + operator + " " + num2 + " = " + result);
        }
        
        scanner.close();
    }
}

// 8. 综合示例：学生成绩管理系统
class StudentGradeSystem {
    public static void main(String[] args) {
        System.out.println("=== 学生成绩管理系统 ===");
        
        Scanner scanner = new Scanner(System.in);
        
        // 输入学生数量
        System.out.print("请输入学生数量: ");
        int studentCount = scanner.nextInt();
        
        // 创建数组存储学生姓名和成绩
        String[] names = new String[studentCount];
        double[] grades = new double[studentCount];
        
        // 输入学生信息
        for (int i = 0; i < studentCount; i++) {
            System.out.print("请输入第" + (i + 1) + "个学生的姓名: ");
            names[i] = scanner.next();
            
            System.out.print("请输入" + names[i] + "的成绩: ");
            grades[i] = scanner.nextDouble();
        }
        
        // 显示所有学生信息
        System.out.println("\n=== 学生成绩列表 ===");
        for (int i = 0; i < studentCount; i++) {
            System.out.println("姓名: " + names[i] + ", 成绩: " + grades[i]);
        }
        
        // 计算统计信息
        double sum = 0;
        double max = grades[0];
        double min = grades[0];
        
        for (double grade : grades) {
            sum += grade;
            if (grade > max) max = grade;
            if (grade < min) min = grade;
        }
        
        double average = sum / studentCount;
        
        // 显示统计结果
        System.out.println("\n=== 统计结果 ===");
        System.out.println("总分: " + sum);
        System.out.println("平均分: " + String.format("%.2f", average));
        System.out.println("最高分: " + max);
        System.out.println("最低分: " + min);
        
        // 显示等级分布
        System.out.println("\n=== 等级分布 ===");
        int excellent = 0, good = 0, fair = 0, poor = 0;
        
        for (double grade : grades) {
            if (grade >= 90) {
                excellent++;
            } else if (grade >= 80) {
                good++;
            } else if (grade >= 60) {
                fair++;
            } else {
                poor++;
            }
        }
        
        System.out.println("优秀 (90-100): " + excellent + "人");
        System.out.println("良好 (80-89): " + good + "人");
        System.out.println("及格 (60-79): " + fair + "人");
        System.out.println("不及格 (0-59): " + poor + "人");
        
        scanner.close();
    }
}

/*
 * 编译和运行说明：
 * 
 * 1. 编译所有类：
 *    javac chapter2_example.java
 * 
 * 2. 运行各个示例：
 *    java DataTypesDemo
 *    java TypeConversionDemo
 *    java OperatorsDemo
 *    java StringDemo
 *    java ArrayDemo
 *    java ControlFlowDemo
 *    java SimpleCalculator  (需要用户输入)
 *    java StudentGradeSystem  (需要用户输入)
 * 
 * 注意：由于一个.java文件中包含多个public类，只有与文件名相同的类可以是public的。
 * 在实际项目中，建议将每个类放在单独的文件中。
 */