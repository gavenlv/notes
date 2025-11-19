# 第1章：Java基础概念与环境搭建

## 1.1 Java简介

### 1.1.1 什么是Java
Java是一种广泛使用的计算机编程语言，拥有跨平台、面向对象、泛型编程的特性，广泛应用于企业级Web应用开发和移动应用开发。Java由Sun Microsystems公司于1995年推出，后被Oracle公司收购。

### 1.1.2 Java的特点
- **简单性**：Java语言相对简单，易于学习和使用。
- **面向对象**：Java是一门面向对象的语言，支持封装、继承和多态。
- **健壮性**：Java强制要求对变量进行初始化，提供垃圾回收机制，避免内存泄漏。
- **安全性**：Java提供了安全管理机制，防止恶意代码的入侵。
- **跨平台性**：Java程序可以在不同的操作系统上运行，实现了"一次编写，到处运行"的理念。
- **多线程**：Java内置了多线程的支持，使得程序可以并发执行。
- **分布式**：Java为Internet的分布式环境而设计。

### 1.1.3 Java的应用领域
- **桌面应用程序**：如企业级管理系统、媒体播放器等。
- **Web应用程序**：如电商网站、社交平台等。
- **移动应用**：Android应用开发的主要语言。
- **企业级应用**：银行系统、ERP系统等大型企业应用。
- **大数据处理**：Hadoop、Spark等大数据框架主要使用Java开发。
- **云计算**：许多云服务平台使用Java构建。

## 1.2 Java发展历史

Java的发展历程大致可分为以下几个阶段：
1. **1991年**：James Gosling领导的团队开始开发Oak语言（Java的前身）。
2. **1995年**：正式发布Java 1.0版本。
3. **1998年**：发布Java 1.2版本，引入Swing图形界面库。
4. **2004年**：发布Java 1.5（Java 5），引入泛型、注解等重要特性。
5. **2006年**：Java开源，建立OpenJDK项目。
6. **2014年**：发布Java 8，引入Lambda表达式和Stream API。
7. **2018年**：Java进入快速迭代周期，每6个月发布一个新版本。

## 1.3 Java虚拟机(JVM)和Java运行机制

### 1.3.1 JVM概述
Java虚拟机（JVM）是Java程序运行的核心组件，它是一个虚拟的计算机，负责执行Java字节码。JVM屏蔽了底层操作系统和硬件的差异，实现了Java的跨平台特性。

### 1.3.2 Java程序运行流程
1. 编写Java源代码（.java文件）
2. 使用javac编译器将源代码编译成字节码（.class文件）
3. JVM加载字节码并解释执行或即时编译执行

### 1.3.3 JVM架构
JVM主要包括以下组件：
- **类加载器**：负责加载.class文件
- **运行时数据区**：包括方法区、堆、栈、程序计数器等
- **执行引擎**：解释执行字节码或将其编译成本地机器码
- **本地接口**：提供与本地方法库交互的接口

## 1.4 JDK、JRE和JVM的关系

### 1.4.1 基本概念
- **JVM（Java Virtual Machine）**：Java虚拟机，负责执行Java字节码
- **JRE（Java Runtime Environment）**：Java运行时环境，包含JVM和运行Java程序所需的类库
- **JDK（Java Development Kit）**：Java开发工具包，包含JRE和开发工具（编译器、调试器等）

### 1.4.2 关系图
```
JDK
├── JRE
│   ├── JVM
│   └── 类库
└── 开发工具（javac、java、javadoc等）
```

## 1.5 Java开发环境搭建

### 1.5.1 下载和安装JDK

#### Windows系统安装步骤：
1. 访问Oracle官网下载JDK安装包（推荐使用OpenJDK）
2. 双击安装包，按照提示完成安装
3. 配置环境变量：
   - JAVA_HOME：指向JDK安装目录
   - PATH：添加%JAVA_HOME%\bin

#### macOS系统安装步骤：
1. 推荐使用Homebrew安装：`brew install openjdk`
2. 或者从官网下载.dmg安装包进行安装

#### Linux系统安装步骤：
1. Ubuntu/Debian：`sudo apt install openjdk-11-jdk`
2. CentOS/RHEL：`sudo yum install java-11-openjdk-devel`

### 1.5.2 验证安装
打开命令行窗口，输入以下命令验证安装：
```bash
java -version
javac -version
```

如果正确显示版本信息，则说明安装成功。

### 1.5.3 配置环境变量

#### Windows环境变量配置：
1. 右键"此电脑" -> "属性" -> "高级系统设置"
2. 点击"环境变量"
3. 在系统变量中新建：
   - 变量名：JAVA_HOME
   - 变量值：JDK安装路径（如C:\Program Files\Java\jdk-11.0.1）
4. 编辑PATH变量，添加：%JAVA_HOME%\bin

#### macOS/Linux环境变量配置：
在~/.bashrc或~/.zshrc中添加：
```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
export PATH=$JAVA_HOME/bin:$PATH
```

## 1.6 第一个Java程序

### 1.6.1 Hello World示例
创建一个名为HelloWorld.java的文件，输入以下代码：

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

### 1.6.2 编译和运行
在命令行中执行以下命令：
```bash
# 编译Java源文件
javac HelloWorld.java

# 运行编译后的字节码文件
java HelloWorld
```

### 1.6.3 代码解析
- `public class HelloWorld`：定义一个公共类，类名必须与文件名一致
- `public static void main(String[] args)`：程序入口点，main方法
- `System.out.println()`：向控制台输出信息

## 1.7 Java开发工具

### 1.7.1 集成开发环境(IDE)
- **IntelliJ IDEA**：JetBrains出品，功能强大，社区版免费
- **Eclipse**：老牌IDE，插件丰富，完全免费
- **NetBeans**：Oracle官方IDE，对Java EE支持良好
- **Visual Studio Code**：轻量级编辑器，通过插件支持Java开发

### 1.7.2 构建工具
- **Maven**：基于项目对象模型(POM)的项目管理工具
- **Gradle**：基于Groovy的构建工具，配置更灵活

### 1.7.3 版本控制系统
- **Git**：分布式版本控制系统，主流选择

## 1.8 Java程序结构

### 1.8.1 基本结构要素
1. **包声明**：使用package关键字声明包
2. **导入语句**：使用import关键字导入其他包中的类
3. **类声明**：使用class关键字定义类
4. **方法**：类中定义的方法，包括main方法作为程序入口

### 1.8.2 示例代码
```java
// 包声明
package com.example.demo;

// 导入语句
import java.util.Date;

// 类声明
public class DemoApplication {
    // main方法 - 程序入口
    public static void main(String[] args) {
        // 方法体
        System.out.println("当前时间：" + new Date());
        greetUser("张三");
    }
    
    // 自定义方法
    public static void greetUser(String name) {
        System.out.println("你好，" + name + "！欢迎学习Java！");
    }
}
```

## 1.9 最佳实践建议

### 1.9.1 命名规范
- **类名**：采用大驼峰命名法，如UserService
- **方法名**：采用小驼峰命名法，如getUserInfo()
- **常量**：全部大写，单词间用下划线分隔，如MAX_SIZE
- **变量名**：采用小驼峰命名法，如userName

### 1.9.2 代码风格
- 使用4个空格缩进（而非Tab）
- 每行代码不超过120个字符
- 合理使用空行分隔代码块
- 添加必要的注释说明

### 1.9.3 学习建议
1. 从基础语法开始，循序渐进
2. 多动手实践，编写小程序验证概念
3. 阅读优秀的开源项目代码
4. 参与实际项目开发积累经验

## 1.10 总结

本章介绍了Java的基本概念、发展历程以及开发环境的搭建过程。我们了解了JVM、JRE和JDK之间的关系，并通过Hello World程序体验了Java程序的编写、编译和运行过程。下一章我们将深入学习Java的基本语法和数据类型。

## 1.11 练习题

1. 下载并安装JDK，配置好环境变量
2. 编写一个Java程序，输出个人信息（姓名、年龄、爱好）
3. 研究不同版本JDK的区别，了解Java的发展趋势
4. 尝试使用不同的IDE创建Java项目，比较它们的特点

通过本章的学习，您应该能够：
- 理解Java的基本概念和特点
- 成功搭建Java开发环境
- 编写、编译和运行简单的Java程序
- 了解Java开发工具和最佳实践