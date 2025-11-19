# 第6章 Java输入输出(I/O)操作

## 目录
1. [I/O概述](#1io概述)
2. [字节流](#2字节流)
3. [字符流](#3字符流)
4. [缓冲流](#4缓冲流)
5. [转换流](#5转换流)
6. [数据流](#6数据流)
7. [打印流](#7打印流)
8. [对象流](#8对象流)
9. [文件操作](#9文件操作)
10. [NIO(New I/O)](#10nionew-io)
11. [Path和Files类](#11path和files类)
12. [最佳实践](#12最佳实践)
13. [常见陷阱](#13常见陷阱)
14. [总结](#14总结)

---

## 1.I/O概述

### 1.1 什么是I/O

I/O(Input/Output)即输入/输出，是程序与外部设备进行数据交换的过程。在Java中，I/O操作主要包括：
- 从文件读取数据或将数据写入文件
- 从网络读取数据或将数据发送到网络
- 从控制台读取用户输入或将结果显示到控制台
- 与其他程序进行数据交换

### 1.2 Java I/O的发展历程

Java I/O经历了几个重要发展阶段：

1. **Java 1.0 - 传统I/O**：
   - 基于流(Stream)的I/O模型
   - 包含在`java.io`包中
   - 同步阻塞式I/O

2. **Java 1.4 - NIO(New I/O)**：
   - 引入了新的I/O模型
   - 基于通道(Channel)和缓冲区(Buffer)
   - 支持非阻塞I/O
   - 包含在`java.nio`包中

3. **Java 7 - NIO.2**：
   - 对NIO进行了增强
   - 引入了更便捷的文件操作API
   - 包含在`java.nio.file`包中

### 1.3 I/O流的分类

Java I/O流可以从不同角度进行分类：

#### 按数据流向分类：
- **输入流(InputStream/Reader)**：从数据源读取数据到程序
- **输出流(OutputStream/Writer)**：从程序写入数据到目标

#### 按处理数据单位分类：
- **字节流(Byte Stream)**：以字节为单位处理数据，用于处理二进制文件
  - InputStream/OutputStream及其子类
- **字符流(Character Stream)**：以字符为单位处理数据，用于处理文本文件
  - Reader/Writer及其子类

#### 按功能分类：
- **节点流(Node Stream)**：直接与数据源或目标连接的流
- **处理流(Processing Stream)**：对其他流进行包装，提供更多功能

### 1.4 I/O核心概念

#### 流(Stream)
流是数据传输的抽象，代表了数据的流动方向。在Java中，所有的I/O操作都是通过流来完成的。

#### 缓冲区(Buffer)
缓冲区是为了提高I/O效率而设计的内存区域，可以减少实际的物理读写次数。

#### 通道(Channel)
NIO中的概念，表示到实体（如硬件设备、文件、网络套接字）的开放连接。

---

## 2.字节流

### 2.1 字节流基础

字节流用于处理二进制数据，以字节为单位进行读写操作。所有字节流都继承自以下两个抽象类：
- `InputStream`：所有字节输入流的父类
- `OutputStream`：所有字节输出流的父类

### 2.2 FileInputStream和FileOutputStream

这两个类是最常用的字节流，用于文件的读写操作。

```java
import java.io.*;

public class ByteStreamExample {
    public static void main(String[] args) {
        // 写入文件
        writeFile();
        
        // 读取文件
        readFile();
        
        // 文件复制
        copyFile();
    }
    
    // 写入文件示例
    public static void writeFile() {
        try (FileOutputStream fos = new FileOutputStream("output.txt")) {
            String data = "Hello, World!\n这是一个测试文件。\n";
            byte[] bytes = data.getBytes("UTF-8");
            fos.write(bytes);
            System.out.println("文件写入成功");
        } catch (IOException e) {
            System.out.println("写入文件时出错：" + e.getMessage());
        }
    }
    
    // 读取文件示例
    public static void readFile() {
        try (FileInputStream fis = new FileInputStream("output.txt")) {
            int byteData;
            System.out.println("文件内容：");
            while ((byteData = fis.read()) != -1) {
                System.out.print((char) byteData);
            }
            System.out.println();
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
    }
    
    // 文件复制示例
    public static void copyFile() {
        try (FileInputStream fis = new FileInputStream("output.txt");
             FileOutputStream fos = new FileOutputStream("copy_output.txt")) {
            
            byte[] buffer = new byte[1024];
            int bytesRead;
            
            while ((bytesRead = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, bytesRead);
            }
            
            System.out.println("文件复制成功");
        } catch (IOException e) {
            System.out.println("文件复制时出错：" + e.getMessage());
        }
    }
}
```

### 2.3 ByteArrayInputStream和ByteArrayOutputStream

这两个类用于在内存中进行字节数组的读写操作。

```java
import java.io.*;

public class ByteArrayStreamExample {
    public static void main(String[] args) {
        try {
            // 创建字节数组输出流
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            
            // 写入数据
            String data = "这是一个测试数据";
            byte[] bytes = data.getBytes("UTF-8");
            baos.write(bytes);
            
            // 获取字节数组
            byte[] result = baos.toByteArray();
            System.out.println("字节数组长度：" + result.length);
            
            // 创建字节数组输入流
            ByteArrayInputStream bais = new ByteArrayInputStream(result);
            
            // 读取数据
            int byteData;
            System.out.print("读取的数据：");
            while ((byteData = bais.read()) != -1) {
                System.out.print((char) byteData);
            }
            System.out.println();
            
            baos.close();
            bais.close();
        } catch (IOException e) {
            System.out.println("操作时出错：" + e.getMessage());
        }
    }
}
```

### 2.4 BufferedInputStream和BufferedOutputStream

缓冲流可以显著提高I/O操作的性能。

```java
import java.io.*;

public class BufferedByteStreamExample {
    public static void main(String[] args) {
        // 创建大文件用于测试
        createLargeFile();
        
        // 比较普通流和缓冲流的性能
        comparePerformance();
    }
    
    // 创建大文件
    public static void createLargeFile() {
        try (FileOutputStream fos = new FileOutputStream("large_file.txt");
             BufferedOutputStream bos = new BufferedOutputStream(fos)) {
            
            String data = "这是一行测试数据\n";
            byte[] bytes = data.getBytes("UTF-8");
            
            // 写入10000行数据
            for (int i = 0; i < 10000; i++) {
                bos.write(bytes);
            }
            
            System.out.println("大文件创建成功");
        } catch (IOException e) {
            System.out.println("创建文件时出错：" + e.getMessage());
        }
    }
    
    // 性能比较
    public static void comparePerformance() {
        // 使用普通流
        long startTime = System.currentTimeMillis();
        try (FileInputStream fis = new FileInputStream("large_file.txt")) {
            int byteData;
            while ((byteData = fis.read()) != -1) {
                // 处理数据
            }
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
        long endTime = System.currentTimeMillis();
        System.out.println("普通流耗时：" + (endTime - startTime) + "ms");
        
        // 使用缓冲流
        startTime = System.currentTimeMillis();
        try (FileInputStream fis = new FileInputStream("large_file.txt");
             BufferedInputStream bis = new BufferedInputStream(fis)) {
            
            int byteData;
            while ((byteData = bis.read()) != -1) {
                // 处理数据
            }
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
        endTime = System.currentTimeMillis();
        System.out.println("缓冲流耗时：" + (endTime - startTime) + "ms");
    }
}
```

---

## 3.字符流

### 3.1 字符流基础

字符流用于处理文本数据，以字符为单位进行读写操作。所有字符流都继承自以下两个抽象类：
- `Reader`：所有字符输入流的父类
- `Writer`：所有字符输出流的父类

字符流在内部使用字符编码来处理字符与字节之间的转换，默认使用平台的默认编码。

### 3.2 FileReader和FileWriter

这两个类是最常用的字符流，用于文本文件的读写操作。

```java
import java.io.*;

public class CharacterStreamExample {
    public static void main(String[] args) {
        // 写入文本文件
        writeTextFile();
        
        // 读取文本文件
        readTextFile();
        
        // 文本文件复制
        copyTextFile();
    }
    
    // 写入文本文件
    public static void writeTextFile() {
        try (FileWriter fw = new FileWriter("text_output.txt")) {
            String data = "Hello, World!\n这是一个中文测试文件。\nSpecial characters: €£¥\n";
            fw.write(data);
            System.out.println("文本文件写入成功");
        } catch (IOException e) {
            System.out.println("写入文本文件时出错：" + e.getMessage());
        }
    }
    
    // 读取文本文件
    public static void readTextFile() {
        try (FileReader fr = new FileReader("text_output.txt")) {
            int charData;
            System.out.println("文本文件内容：");
            while ((charData = fr.read()) != -1) {
                System.out.print((char) charData);
            }
            System.out.println();
        } catch (IOException e) {
            System.out.println("读取文本文件时出错：" + e.getMessage());
        }
    }
    
    // 文本文件复制
    public static void copyTextFile() {
        try (FileReader fr = new FileReader("text_output.txt");
             FileWriter fw = new FileWriter("copy_text_output.txt")) {
            
            int charData;
            while ((charData = fr.read()) != -1) {
                fw.write(charData);
            }
            
            System.out.println("文本文件复制成功");
        } catch (IOException e) {
            System.out.println("文本文件复制时出错：" + e.getMessage());
        }
    }
}
```

### 3.3 InputStreamReader和OutputStreamWriter

这两个类是字节流和字符流之间的桥梁，可以在构造时指定字符编码。

```java
import java.io.*;

public class EncodingExample {
    public static void main(String[] args) {
        // 使用不同编码写入文件
        writeWithEncoding();
        
        // 使用不同编码读取文件
        readWithEncoding();
    }
    
    // 使用不同编码写入文件
    public static void writeWithEncoding() {
        try {
            // 使用UTF-8编码写入
            try (OutputStreamWriter osw = new OutputStreamWriter(
                    new FileOutputStream("utf8_file.txt"), "UTF-8")) {
                osw.write("Hello, 世界! 中文测试\n");
                System.out.println("UTF-8编码文件写入成功");
            }
            
            // 使用GBK编码写入
            try (OutputStreamWriter osw = new OutputStreamWriter(
                    new FileOutputStream("gbk_file.txt"), "GBK")) {
                osw.write("Hello, 世界! 中文测试\n");
                System.out.println("GBK编码文件写入成功");
            }
        } catch (IOException e) {
            System.out.println("写入文件时出错：" + e.getMessage());
        }
    }
    
    // 使用不同编码读取文件
    public static void readWithEncoding() {
        try {
            // 使用UTF-8编码读取
            try (InputStreamReader isr = new InputStreamReader(
                    new FileInputStream("utf8_file.txt"), "UTF-8")) {
                int charData;
                System.out.print("UTF-8文件内容：");
                while ((charData = isr.read()) != -1) {
                    System.out.print((char) charData);
                }
                System.out.println();
            }
            
            // 使用GBK编码读取
            try (InputStreamReader isr = new InputStreamReader(
                    new FileInputStream("gbk_file.txt"), "GBK")) {
                int charData;
                System.out.print("GBK文件内容：");
                while ((charData = isr.read()) != -1) {
                    System.out.print((char) charData);
                }
                System.out.println();
            }
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
    }
}
```

### 3.4 BufferedReader和BufferedWriter

缓冲字符流提供了按行读取等便利方法。

```java
import java.io.*;

public class BufferedCharacterStreamExample {
    public static void main(String[] args) {
        // 创建测试文件
        createTestFile();
        
        // 按行读取文件
        readByLines();
        
        // 写入多行数据
        writeMultipleLines();
    }
    
    // 创建测试文件
    public static void createTestFile() {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter("lines_test.txt"))) {
            bw.write("第一行数据");
            bw.newLine(); // 写入换行符
            bw.write("第二行数据");
            bw.newLine();
            bw.write("第三行数据");
            bw.newLine();
            System.out.println("测试文件创建成功");
        } catch (IOException e) {
            System.out.println("创建测试文件时出错：" + e.getMessage());
        }
    }
    
    // 按行读取文件
    public static void readByLines() {
        try (BufferedReader br = new BufferedReader(new FileReader("lines_test.txt"))) {
            String line;
            System.out.println("按行读取文件内容：");
            int lineNumber = 1;
            while ((line = br.readLine()) != null) {
                System.out.println("第" + lineNumber + "行：" + line);
                lineNumber++;
            }
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
    }
    
    // 写入多行数据
    public static void writeMultipleLines() {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter("multi_lines.txt"))) {
            bw.write("这是第一行");
            bw.newLine();
            bw.write("这是第二行");
            bw.newLine();
            bw.write("这是第三行");
            bw.newLine();
            
            // 使用printf方法
            bw.write(String.format("数字：%d，浮点数：%.2f", 42, 3.14159));
            bw.newLine();
            
            System.out.println("多行数据写入成功");
        } catch (IOException e) {
            System.out.println("写入多行数据时出错：" + e.getMessage());
        }
    }
}
```

---

## 4.缓冲流

### 4.1 缓冲流的作用

缓冲流通过在内存中创建缓冲区来减少实际的物理读写次数，从而提高I/O操作的性能。

### 4.2 缓冲字节流

```java
import java.io.*;

public class ByteBufferedStreamExample {
    public static void main(String[] args) {
        // 创建大文件用于测试
        createLargeBinaryFile();
        
        // 比较不同缓冲区大小的性能
        compareBufferSizes();
    }
    
    // 创建大二进制文件
    public static void createLargeBinaryFile() {
        try (BufferedOutputStream bos = new BufferedOutputStream(
                new FileOutputStream("binary_data.dat"))) {
            
            // 写入1MB的随机数据
            byte[] buffer = new byte[1024]; // 1KB缓冲区
            for (int i = 0; i < 1024; i++) { // 1024次 = 1MB
                // 填充随机数据
                for (int j = 0; j < buffer.length; j++) {
                    buffer[j] = (byte) (Math.random() * 256);
                }
                bos.write(buffer);
            }
            
            System.out.println("大二进制文件创建成功 (1MB)");
        } catch (IOException e) {
            System.out.println("创建二进制文件时出错：" + e.getMessage());
        }
    }
    
    // 比较不同缓冲区大小的性能
    public static void compareBufferSizes() {
        int[] bufferSizes = {128, 512, 1024, 2048, 4096, 8192};
        
        for (int bufferSize : bufferSizes) {
            long startTime = System.currentTimeMillis();
            
            try (BufferedInputStream bis = new BufferedInputStream(
                    new FileInputStream("binary_data.dat"), bufferSize)) {
                
                byte[] buffer = new byte[bufferSize];
                int bytesRead;
                long totalBytes = 0;
                
                while ((bytesRead = bis.read(buffer)) != -1) {
                    totalBytes += bytesRead;
                }
                
                long endTime = System.currentTimeMillis();
                System.out.printf("缓冲区大小：%5d 字节，读取 %d 字节，耗时：%d ms%n",
                        bufferSize, totalBytes, (endTime - startTime));
            } catch (IOException e) {
                System.out.println("读取文件时出错：" + e.getMessage());
            }
        }
    }
}
```

### 4.3 缓冲字符流

```java
import java.io.*;

public class CharacterBufferedStreamExample {
    public static void main(String[] args) {
        // 创建大型文本文件
        createLargeTextFile();
        
        // 比较BufferedReader和FileReader的性能
        compareReaderPerformance();
        
        // 使用mark和reset方法
        demonstrateMarkReset();
    }
    
    // 创建大型文本文件
    public static void createLargeTextFile() {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter("large_text.txt"))) {
            String line = "这是一行测试文本数据，用于性能测试。\n";
            
            // 写入10000行数据
            for (int i = 1; i <= 10000; i++) {
                bw.write(String.format("%05d: %s", i, line));
            }
            
            System.out.println("大型文本文件创建成功 (10000行)");
        } catch (IOException e) {
            System.out.println("创建文本文件时出错：" + e.getMessage());
        }
    }
    
    // 比较性能
    public static void compareReaderPerformance() {
        System.out.println("=== 性能比较 ===");
        
        // 使用FileReader逐字符读取
        long startTime = System.currentTimeMillis();
        try (FileReader fr = new FileReader("large_text.txt")) {
            int charData;
            long charCount = 0;
            while ((charData = fr.read()) != -1) {
                charCount++;
            }
            long endTime = System.currentTimeMillis();
            System.out.printf("FileReader逐字符读取：%d 字符，耗时：%d ms%n",
                    charCount, (endTime - startTime));
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
        
        // 使用BufferedReader逐字符读取
        startTime = System.currentTimeMillis();
        try (BufferedReader br = new BufferedReader(new FileReader("large_text.txt"))) {
            int charData;
            long charCount = 0;
            while ((charData = br.read()) != -1) {
                charCount++;
            }
            long endTime = System.currentTimeMillis();
            System.out.printf("BufferedReader逐字符读取：%d 字符，耗时：%d ms%n",
                    charCount, (endTime - startTime));
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
        
        // 使用BufferedReader按行读取
        startTime = System.currentTimeMillis();
        try (BufferedReader br = new BufferedReader(new FileReader("large_text.txt"))) {
            String line;
            long lineCount = 0;
            while ((line = br.readLine()) != null) {
                lineCount++;
            }
            long endTime = System.currentTimeMillis();
            System.out.printf("BufferedReader按行读取：%d 行，耗时：%d ms%n",
                    lineCount, (endTime - startTime));
        } catch (IOException e) {
            System.out.println("读取文件时出错：" + e.getMessage());
        }
    }
    
    // 演示mark和reset方法
    public static void demonstrateMarkReset() {
        System.out.println("\n=== mark和reset方法演示 ===");
        
        try (BufferedReader br = new BufferedReader(new FileReader("large_text.txt"))) {
            // 读取前几行
            System.out.println("读取前3行：");
            for (int i = 0; i < 3; i++) {
                System.out.println(br.readLine());
            }
            
            // 设置标记，可以回退最多1024个字符
            br.mark(1024);
            
            // 继续读取几行
            System.out.println("\n继续读取接下来的2行：");
            for (int i = 0; i < 2; i++) {
                System.out.println(br.readLine());
            }
            
            // 回退到标记位置
            br.reset();
            System.out.println("\n回退后重新读取：");
            for (int i = 0; i < 2; i++) {
                System.out.println(br.readLine());
            }
        } catch (IOException e) {
            System.out.println("操作时出错：" + e.getMessage());
        }
    }
}
```

---

## 5.转换流

### 5.1 InputStreamReader详解

InputStreamReader是字节流通向字符流的桥梁，它可以将字节流转换为字符流，并在转换过程中使用指定的字符集。

```java
import java.io.*;
import java.nio.charset.Charset;

public class InputStreamReaderExample {
    public static void main(String[] args) {
        // 演示不同字符集的转换
        demonstrateCharsetConversion();
        
        // 获取默认字符集信息
        showDefaultCharset();
    }
    
    // 演示不同字符集的转换
    public static void demonstrateCharsetConversion() {
        System.out.println("=== 字符集转换演示 ===");
        
        String text = "Hello, 世界! Привет мир! 🌍";
        
        try {
            // 使用不同的字符集写入文件
            String[] charsets = {"UTF-8", "UTF-16", "GBK"};
            
            for (String charset : charsets) {
                // 写入文件
                try (OutputStreamWriter osw = new OutputStreamWriter(
                        new FileOutputStream("charset_" + charset.toLowerCase() + ".txt"), charset)) {
                    osw.write(text);
                }
                
                // 读取文件
                try (InputStreamReader isr = new InputStreamReader(
                        new FileInputStream("charset_" + charset.toLowerCase() + ".txt"), charset)) {
                    
                    StringBuilder sb = new StringBuilder();
                    int charData;
                    while ((charData = isr.read()) != -1) {
                        sb.append((char) charData);
                    }
                    
                    System.out.printf("%s 编码读取结果：%s%n", charset, sb.toString());
                }
            }
        } catch (IOException e) {
            System.out.println("字符集转换时出错：" + e.getMessage());
        }
    }
    
    // 显示默认字符集信息
    public static void showDefaultCharset() {
        System.out.println("\n=== 默认字符集信息 ===");
        System.out.println("系统默认字符集：" + Charset.defaultCharset());
        System.out.println("可用字符集数量：" + Charset.availableCharsets().size());
        
        // 显示一些常用字符集
        String[] commonCharsets = {"UTF-8", "UTF-16", "GBK", "GB2312", "ISO-8859-1"};
        System.out.println("常用字符集支持情况：");
        for (String charsetName : commonCharsets) {
            try {
                Charset charset = Charset.forName(charsetName);
                System.out.println("  " + charsetName + " - " + charset.displayName());
            } catch (Exception e) {
                System.out.println("  " + charsetName + " - 不支持");
            }
        }
    }
}
```

### 5.2 OutputStreamWriter详解

OutputStreamWriter是字符流通向字节流的桥梁，它可以将字符流转换为字节流，并在转换过程中使用指定的字符集。

```java
import java.io.*;
import java.nio.charset.Charset;

public class OutputStreamWriterExample {
    public static void main(String[] args) {
        // 演示字符集编码
        demonstrateEncoding();
        
        // 演示缓冲区刷新
        demonstrateFlushing();
    }
    
    // 演示字符集编码
    public static void demonstrateEncoding() {
        System.out.println("=== 字符集编码演示 ===");
        
        String text = "English: Hello\n中文：你好\nРусский: Привет\nEmoji: 🌍🎉🚀";
        
        try {
            // 使用不同字符集编码
            String[] encodings = {"UTF-8", "UTF-16BE", "UTF-16LE", "GBK"};
            
            for (String encoding : encodings) {
                String fileName = "encoding_" + encoding.toLowerCase().replace("-", "_") + ".txt";
                
                try (OutputStreamWriter osw = new OutputStreamWriter(
                        new FileOutputStream(fileName), encoding)) {
                    osw.write(text);
                    // 获取编码后的字节数
                    System.out.printf("%s 编码后文件大小：%d 字节%n", encoding, new File(fileName).length());
                }
            }
        } catch (IOException e) {
            System.out.println("编码演示时出错：" + e.getMessage());
        }
    }
    
    // 演示缓冲区刷新
    public static void demonstrateFlushing() {
        System.out.println("\n=== 缓冲区刷新演示 ===");
        
        try {
            // 不使用flush的情况
            try (OutputStreamWriter osw = new OutputStreamWriter(
                    new FileOutputStream("no_flush.txt"))) {
                osw.write("这条消息可能不会立即写入文件");
                // 不调用flush，数据可能还在缓冲区中
                Thread.sleep(1000); // 等待1秒
                
                // 检查文件大小
                long fileSize = new File("no_flush.txt").length();
                System.out.println("未刷新时文件大小：" + fileSize + " 字节");
            }
            
            // 使用flush的情况
            try (OutputStreamWriter osw = new OutputStreamWriter(
                    new FileOutputStream("with_flush.txt"))) {
                osw.write("这条消息会被立即写入文件");
                osw.flush(); // 强制刷新缓冲区
                
                // 检查文件大小
                long fileSize = new File("with_flush.txt").length();
                System.out.println("刷新后文件大小：" + fileSize + " 字节");
            }
            
            Thread.sleep(1000); // 等待流自动关闭
            
        } catch (IOException | InterruptedException e) {
            System.out.println("刷新演示时出错：" + e.getMessage());
        }
    }
}
```

---

## 6.数据流

### 6.1 DataInputStream和DataOutputStream

数据流允许应用程序以与机器无关的方式从底层输入流中读取基本Java数据类型。

```java
import java.io.*;

public class DataStreamExample {
    public static void main(String[] args) {
        // 写入基本数据类型
        writePrimitiveData();
        
        // 读取基本数据类型
        readPrimitiveData();
        
        // 演示字节序问题
        demonstrateByteOrder();
    }
    
    // 写入基本数据类型
    public static void writePrimitiveData() {
        System.out.println("=== 写入基本数据类型 ===");
        
        try (DataOutputStream dos = new DataOutputStream(
                new FileOutputStream("primitive_data.dat"))) {
            
            // 写入各种基本数据类型
            dos.writeBoolean(true);
            dos.writeByte(127);
            dos.writeShort(32767);
            dos.writeInt(2147483647);
            dos.writeLong(9223372036854775807L);
            dos.writeFloat(3.14159f);
            dos.writeDouble(2.718281828459045);
            dos.writeChar('A');
            dos.writeUTF("Hello, 世界!");
            
            System.out.println("基本数据类型写入成功");
            System.out.println("文件大小：" + new File("primitive_data.dat").length() + " 字节");
            
        } catch (IOException e) {
            System.out.println("写入数据时出错：" + e.getMessage());
        }
    }
    
    // 读取基本数据类型
    public static void readPrimitiveData() {
        System.out.println("\n=== 读取基本数据类型 ===");
        
        try (DataInputStream dis = new DataInputStream(
                new FileInputStream("primitive_data.dat"))) {
            
            // 按照写入顺序读取数据
            System.out.println("Boolean: " + dis.readBoolean());
            System.out.println("Byte: " + dis.readByte());
            System.out.println("Short: " + dis.readShort());
            System.out.println("Int: " + dis.readInt());
            System.out.println("Long: " + dis.readLong());
            System.out.println("Float: " + dis.readFloat());
            System.out.println("Double: " + dis.readDouble());
            System.out.println("Char: " + dis.readChar());
            System.out.println("UTF: " + dis.readUTF());
            
        } catch (IOException e) {
            System.out.println("读取数据时出错：" + e.getMessage());
        }
    }
    
    // 演示字节序问题
    public static void demonstrateByteOrder() {
        System.out.println("\n=== 字节序演示 ===");
        
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream();
             DataOutputStream dos = new DataOutputStream(baos)) {
            
            // 写入一个整数
            int value = 0x12345678;
            dos.writeInt(value);
            
            // 获取字节数组
            byte[] bytes = baos.toByteArray();
            
            System.out.printf("原始整数值：0x%08X%n", value);
            System.out.print("字节序列：");
            for (int i = 0; i < bytes.length; i++) {
                System.out.printf("0x%02X ", bytes[i] & 0xFF);
            }
            System.out.println();
            
            // 解释字节序
            System.out.println("Java使用大端字节序(Big Endian)");
            System.out.println("最高有效字节存储在最低的内存地址");
            
        } catch (IOException e) {
            System.out.println("字节序演示时出错：" + e.getMessage());
        }
    }
}
```

### 6.2 数据流的实际应用

```java
import java.io.*;
import java.util.Date;

class Student implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private int age;
    private double score;
    private Date enrollmentDate;
    
    public Student(String name, int age, double score) {
        this.name = name;
        this.age = age;
        this.score = score;
        this.enrollmentDate = new Date();
    }
    
    // getters and setters
    public String getName() { return name; }
    public int getAge() { return age; }
    public double getScore() { return score; }
    public Date getEnrollmentDate() { return enrollmentDate; }
    
    @Override
    public String toString() {
        return String.format("Student{name='%s', age=%d, score=%.2f, enrollmentDate=%s}",
                name, age, score, enrollmentDate);
    }
}

public class StudentDataStreamExample {
    public static void main(String[] args) {
        // 保存学生数据
        saveStudents();
        
        // 加载学生数据
        loadStudents();
    }
    
    // 保存学生数据
    public static void saveStudents() {
        System.out.println("=== 保存学生数据 ===");
        
        Student[] students = {
            new Student("张三", 20, 85.5),
            new Student("李四", 21, 92.0),
            new Student("王五", 19, 78.5)
        };
        
        try (DataOutputStream dos = new DataOutputStream(
                new FileOutputStream("students.dat"))) {
            
            // 先写入学生数量
            dos.writeInt(students.length);
            
            // 写入每个学生的信息
            for (Student student : students) {
                dos.writeUTF(student.getName());
                dos.writeInt(student.getAge());
                dos.writeDouble(student.getScore());
                dos.writeLong(student.getEnrollmentDate().getTime());
            }
            
            System.out.println("学生数据保存成功");
            
        } catch (IOException e) {
            System.out.println("保存学生数据时出错：" + e.getMessage());
        }
    }
    
    // 加载学生数据
    public static void loadStudents() {
        System.out.println("\n=== 加载学生数据 ===");
        
        try (DataInputStream dis = new DataInputStream(
                new FileInputStream("students.dat"))) {
            
            // 先读取学生数量
            int count = dis.readInt();
            System.out.println("学生数量：" + count);
            
            // 读取每个学生的信息
            for (int i = 0; i < count; i++) {
                String name = dis.readUTF();
                int age = dis.readInt();
                double score = dis.readDouble();
                long dateInMillis = dis.readLong();
                Date enrollmentDate = new Date(dateInMillis);
                
                Student student = new Student(name, age, score);
                // 使用反射设置enrollmentDate字段（简化处理）
                System.out.println("加载学生：" + student);
            }
            
        } catch (IOException e) {
            System.out.println("加载学生数据时出错：" + e.getMessage());
        }
    }
}
```

---

## 7.打印流

### 7.1 PrintStream和PrintWriter

打印流提供了方便的打印方法，可以格式化输出各种数据类型。

```java
import java.io.*;
import java.util.Date;

public class PrintStreamExample {
    public static void main(String[] args) {
        // 标准输出流
        demonstrateStandardOutput();
        
        // 文件打印流
        demonstrateFilePrintStream();
        
        // 格式化输出
        demonstrateFormatting();
    }
    
    // 演示标准输出流
    public static void demonstrateStandardOutput() {
        System.out.println("=== 标准输出流演示 ===");
        
        // System.out就是PrintStream的一个实例
        System.out.println("使用println方法输出字符串");
        System.out.print("使用print方法输出不换行");
        System.out.println(" - 这是同一行");
        
        // 输出各种数据类型
        System.out.println("整数：" + 42);
        System.out.println("浮点数：" + 3.14159);
        System.out.println("布尔值：" + true);
        System.out.println("字符：" + 'A');
        System.out.println("对象：" + new Date());
    }
    
    // 演示文件打印流
    public static void demonstrateFilePrintStream() {
        System.out.println("\n=== 文件打印流演示 ===");
        
        try (PrintStream ps = new PrintStream("print_output.txt")) {
            // 输出各种数据类型
            ps.println("这是一个文件输出示例");
            ps.println("整数：" + 12345);
            ps.println("浮点数：" + 3.14159);
            ps.println("科学计数法：" + 1234567.89);
            
            // 使用printf格式化输出
            ps.printf("格式化输出 - 名字：%s，年龄：%d，分数：%.2f%n", "张三", 20, 85.5);
            
            System.out.println("文件打印流输出成功");
        } catch (IOException e) {
            System.out.println("文件打印时出错：" + e.getMessage());
        }
    }
    
    // 演示格式化输出
    public static void demonstrateFormatting() {
        System.out.println("\n=== 格式化输出演示 ===");
        
        // 整数格式化
        System.out.println("=== 整数格式化 ===");
        int number = 42;
        System.out.printf("默认：%d%n", number);
        System.out.printf("补零：%05d%n", number);
        System.out.printf("左对齐：%-10d|%n", number);
        System.out.printf("十六进制：%x%n", number);
        System.out.printf("八进制：%o%n", number);
        
        // 浮点数格式化
        System.out.println("\n=== 浮点数格式化 ===");
        double pi = Math.PI;
        System.out.printf("默认：%f%n", pi);
        System.out.printf("保留2位小数：%.2f%n", pi);
        System.out.printf("保留4位小数：%.4f%n", pi);
        System.out.printf("科学计数法：%e%n", pi);
        System.out.printf("右对齐：%10.2f|%n", pi);
        System.out.printf("左对齐：%-10.2f|%n", pi);
        
        // 字符串格式化
        System.out.println("\n=== 字符串格式化 ===");
        String name = "Java";
        System.out.printf("默认：%s%n", name);
        System.out.printf("指定宽度：%10s|%n", name);
        System.out.printf("左对齐：%-10s|%n", name);
        System.out.printf("截断：%.2s%n", name);
        
        // 日期时间格式化
        System.out.println("\n=== 日期时间格式化 ===");
        Date now = new Date();
        System.out.printf("完整日期时间：%tF %tT%n", now, now);
        System.out.printf("日期：%tF%n", now);
        System.out.printf("时间：%tT%n", now);
        System.out.printf("星期：%tA%n", now);
    }
}
```

### 7.2 PrintWriter详解

PrintWriter与PrintStream类似，但它是字符流，更适合处理文本输出。

```java
import java.io.*;
import java.util.Locale;

public class PrintWriterExample {
    public static void main(String[] args) {
        // 基本使用
        basicUsage();
        
        // 自动刷新
        demonstrateAutoFlush();
        
        // 国际化输出
        demonstrateInternationalization();
    }
    
    // 基本使用
    public static void basicUsage() {
        System.out.println("=== PrintWriter基本使用 ===");
        
        try (PrintWriter pw = new PrintWriter("printwriter_output.txt")) {
            // 输出各种数据类型
            pw.println("PrintWriter输出示例");
            pw.println("整数：" + 12345);
            pw.println("浮点数：" + 3.14159);
            
            // 使用printf方法
            pw.printf("姓名：%s，年龄：%d，成绩：%.2f%n", "李四", 21, 92.5);
            
            // 使用format方法（与printf相同）
            pw.format("格式化输出：%s - %d%n", "测试", 42);
            
            System.out.println("PrintWriter输出成功");
        } catch (IOException e) {
            System.out.println("PrintWriter输出时出错：" + e.getMessage());
        }
    }
    
    // 演示自动刷新
    public static void demonstrateAutoFlush() {
        System.out.println("\n=== 自动刷新演示 ===");
        
        try {
            // 不启用自动刷新
            PrintWriter pw1 = new PrintWriter(new FileWriter("no_autoflush.txt"), false);
            pw1.print("这条消息不会立即写入文件");
            // 检查文件大小
            long size1 = new File("no_autoflush.txt").length();
            System.out.println("未启用自动刷新时文件大小：" + size1 + " 字节");
            pw1.close(); // 关闭时才写入
            
            // 启用自动刷新
            PrintWriter pw2 = new PrintWriter(new FileWriter("autoflush.txt"), true);
            pw2.print("这条消息会立即写入文件");
            pw2.flush(); // 显式刷新
            // 检查文件大小
            long size2 = new File("autoflush.txt").length();
            System.out.println("启用自动刷新时文件大小：" + size2 + " 字节");
            pw2.close();
            
        } catch (IOException e) {
            System.out.println("自动刷新演示时出错：" + e.getMessage());
        }
    }
    
    // 演示国际化输出
    public static void demonstrateInternationalization() {
        System.out.println("\n=== 国际化输出演示 ===");
        
        try (PrintWriter pw = new PrintWriter("international_output.txt")) {
            // 使用不同地区的格式
            double number = 1234567.89;
            
            // 默认地区
            pw.printf("默认格式：%,.2f%n", number);
            
            // 美国地区
            pw.printf(Locale.US, "美国格式：%,.2f%n", number);
            
            // 德国地区
            pw.printf(Locale.GERMANY, "德国格式：%,.2f%n", number);
            
            // 中国地区
            pw.printf(Locale.CHINA, "中国格式：%,.2f%n", number);
            
            System.out.println("国际化输出成功");
        } catch (IOException e) {
            System.out.println("国际化输出时出错：" + e.getMessage());
        }
    }
}
```

---

## 8.对象流

### 8.1 对象序列化基础

对象序列化是将对象转换为字节序列的过程，反序列化则是将字节序列还原为对象的过程。

```java
import java.io.*;
import java.util.Date;

// 实现Serializable接口的类才能被序列化
class Person implements Serializable {
    // serialVersionUID用于版本控制
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;
    private transient String password; // transient字段不会被序列化
    private Date birthDate;
    
    public Person(String name, int age, String password) {
        this.name = name;
        this.age = age;
        this.password = password;
        this.birthDate = new Date();
    }
    
    // getters and setters
    public String getName() { return name; }
    public int getAge() { return age; }
    public String getPassword() { return password; }
    public Date getBirthDate() { return birthDate; }
    
    public void setPassword(String password) { this.password = password; }
    
    @Override
    public String toString() {
        return String.format("Person{name='%s', age=%d, password='%s', birthDate=%s}",
                name, age, password, birthDate);
    }
}

public class ObjectSerializationExample {
    public static void main(String[] args) {
        // 序列化对象
        serializeObject();
        
        // 反序列化对象
        deserializeObject();
    }
    
    // 序列化对象
    public static void serializeObject() {
        System.out.println("=== 对象序列化 ===");
        
        Person person = new Person("张三", 25, "secret123");
        System.out.println("序列化前的对象：" + person);
        
        try (ObjectOutputStream oos = new ObjectOutputStream(
                new FileOutputStream("person.ser"))) {
            
            oos.writeObject(person);
            System.out.println("对象序列化成功");
            
        } catch (IOException e) {
            System.out.println("对象序列化时出错：" + e.getMessage());
        }
    }
    
    // 反序列化对象
    public static void deserializeObject() {
        System.out.println("\n=== 对象反序列化 ===");
        
        try (ObjectInputStream ois = new ObjectInputStream(
                new FileInputStream("person.ser"))) {
            
            Person person = (Person) ois.readObject();
            System.out.println("反序列化后的对象：" + person);
            System.out.println("注意：password字段为null，因为它是transient的");
            
        } catch (IOException | ClassNotFoundException e) {
            System.out.println("对象反序列化时出错：" + e.getMessage());
        }
    }
}
```

### 8.2 自定义序列化

通过实现writeObject和readObject方法来自定义序列化过程。

```java
import java.io.*;

class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;
    private transient String password;
    private String department;
    
    public Employee(String name, int age, String password, String department) {
        this.name = name;
        this.age = age;
        this.password = password;
        this.department = department;
    }
    
    // 自定义序列化方法
    private void writeObject(ObjectOutputStream oos) throws IOException {
        // 执行默认序列化
        oos.defaultWriteObject();
        
        // 自定义加密密码字段
        String encryptedPassword = encrypt(password);
        oos.writeUTF(encryptedPassword);
        
        System.out.println("自定义序列化：密码已加密");
    }
    
    // 自定义反序列化方法
    private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {
        // 执行默认反序列化
        ois.defaultReadObject();
        
        // 自定义解密密码字段
        String encryptedPassword = ois.readUTF();
        this.password = decrypt(encryptedPassword);
        
        System.out.println("自定义反序列化：密码已解密");
    }
    
    // 简单的加密方法（仅作演示）
    private String encrypt(String plainText) {
        if (plainText == null) return null;
        StringBuilder sb = new StringBuilder();
        for (char c : plainText.toCharArray()) {
            sb.append((char) (c + 1)); // 简单的字符移位
        }
        return sb.toString();
    }
    
    // 简单的解密方法（仅作演示）
    private String decrypt(String encryptedText) {
        if (encryptedText == null) return null;
        StringBuilder sb = new StringBuilder();
        for (char c : encryptedText.toCharArray()) {
            sb.append((char) (c - 1)); // 简单的字符移位
        }
        return sb.toString();
    }
    
    @Override
    public String toString() {
        return String.format("Employee{name='%s', age=%d, password='%s', department='%s'}",
                name, age, password, department);
    }
    
    // getters
    public String getName() { return name; }
    public int getAge() { return age; }
    public String getPassword() { return password; }
    public String getDepartment() { return department; }
}

public class CustomSerializationExample {
    public static void main(String[] args) {
        // 自定义序列化
        customSerialize();
        
        // 自定义反序列化
        customDeserialize();
    }
    
    // 自定义序列化
    public static void customSerialize() {
        System.out.println("=== 自定义序列化 ===");
        
        Employee emp = new Employee("李四", 30, "mypassword", "IT部门");
        System.out.println("序列化前的对象：" + emp);
        
        try (ObjectOutputStream oos = new ObjectOutputStream(
                new FileOutputStream("employee.ser"))) {
            
            oos.writeObject(emp);
            System.out.println("员工对象序列化成功");
            
        } catch (IOException e) {
            System.out.println("员工对象序列化时出错：" + e.getMessage());
        }
    }
    
    // 自定义反序列化
    public static void customDeserialize() {
        System.out.println("\n=== 自定义反序列化 ===");
        
        try (ObjectInputStream ois = new ObjectInputStream(
                new FileInputStream("employee.ser"))) {
            
            Employee emp = (Employee) ois.readObject();
            System.out.println("反序列化后的对象：" + emp);
            System.out.println("密码已被正确解密");
            
        } catch (IOException | ClassNotFoundException e) {
            System.out.println("员工对象反序列化时出错：" + e.getMessage());
        }
    }
}
```

### 8.3 序列化集合和复杂对象

```java
import java.io.*;
import java.util.*;

class Course implements Serializable {
    private static final long serialVersionUID = 1L;
    private String courseName;
    private int credits;
    
    public Course(String courseName, int credits) {
        this.courseName = courseName;
        this.credits = credits;
    }
    
    @Override
    public String toString() {
        return String.format("Course{name='%s', credits=%d}", courseName, credits);
    }
    
    // getters
    public String getCourseName() { return courseName; }
    public int getCredits() { return credits; }
}

class StudentRecord implements Serializable {
    private static final long serialVersionUID = 1L;
    private String studentId;
    private String name;
    private List<Course> courses;
    private Map<String, Double> grades;
    
    public StudentRecord(String studentId, String name) {
        this.studentId = studentId;
        this.name = name;
        this.courses = new ArrayList<>();
        this.grades = new HashMap<>();
    }
    
    public void addCourse(Course course, double grade) {
        courses.add(course);
        grades.put(course.getCourseName(), grade);
    }
    
    @Override
    public String toString() {
        return String.format("StudentRecord{id='%s', name='%s', courses=%s, grades=%s}",
                studentId, name, courses, grades);
    }
    
    // getters
    public String getStudentId() { return studentId; }
    public String getName() { return name; }
    public List<Course> getCourses() { return courses; }
    public Map<String, Double> getGrades() { return grades; }
}

public class ComplexSerializationExample {
    public static void main(String[] args) {
        // 序列化复杂对象
        serializeComplexObject();
        
        // 反序列化复杂对象
        deserializeComplexObject();
    }
    
    // 序列化复杂对象
    public static void serializeComplexObject() {
        System.out.println("=== 序列化复杂对象 ===");
        
        // 创建学生记录
        StudentRecord record = new StudentRecord("2023001", "王五");
        
        // 添加课程和成绩
        record.addCourse(new Course("Java编程", 4), 95.0);
        record.addCourse(new Course("数据结构", 3), 88.5);
        record.addCourse(new Course("算法分析", 3), 92.0);
        
        System.out.println("序列化前的对象：" + record);
        
        try (ObjectOutputStream oos = new ObjectOutputStream(
                new FileOutputStream("student_record.ser"))) {
            
            oos.writeObject(record);
            System.out.println("学生记录序列化成功");
            
        } catch (IOException e) {
            System.out.println("学生记录序列化时出错：" + e.getMessage());
        }
    }
    
    // 反序列化复杂对象
    public static void deserializeComplexObject() {
        System.out.println("\n=== 反序列化复杂对象 ===");
        
        try (ObjectInputStream ois = new ObjectInputStream(
                new FileInputStream("student_record.ser"))) {
            
            StudentRecord record = (StudentRecord) ois.readObject();
            System.out.println("反序列化后的对象：" + record);
            
            // 验证集合是否正确恢复
            System.out.println("课程数量：" + record.getCourses().size());
            System.out.println("成绩数量：" + record.getGrades().size());
            
        } catch (IOException | ClassNotFoundException e) {
            System.out.println("学生记录反序列化时出错：" + e.getMessage());
        }
    }
}
```

---

## 9.文件操作

### 9.1 File类详解

File类用于表示文件和目录路径名的抽象表示形式。

```java
import java.io.*;
import java.util.Date;

public class FileClassExample {
    public static void main(String[] args) {
        // 基本文件操作
        basicFileOperations();
        
        // 目录操作
        directoryOperations();
        
        // 文件过滤
        fileFiltering();
    }
    
    // 基本文件操作
    public static void basicFileOperations() {
        System.out.println("=== 基本文件操作 ===");
        
        // 创建File对象
        File file = new File("test_file.txt");
        
        // 文件基本信息
        System.out.println("文件名：" + file.getName());
        System.out.println("绝对路径：" + file.getAbsolutePath());
        System.out.println("规范化路径：" + file.getPath());
        System.out.println("父目录：" + file.getParent());
        
        try {
            // 创建新文件
            if (file.createNewFile()) {
                System.out.println("文件创建成功");
            } else {
                System.out.println("文件已存在");
            }
            
            // 写入一些内容
            try (FileWriter writer = new FileWriter(file)) {
                writer.write("这是测试文件的内容\n第二行内容");
            }
            
            // 文件属性
            System.out.println("文件是否存在：" + file.exists());
            System.out.println("是否为文件：" + file.isFile());
            System.out.println("是否为目录：" + file.isDirectory());
            System.out.println("文件大小：" + file.length() + " 字节");
            System.out.println("最后修改时间：" + new Date(file.lastModified()));
            System.out.println("是否可读：" + file.canRead());
            System.out.println("是否可写：" + file.canWrite());
            System.out.println("是否隐藏：" + file.isHidden());
            
        } catch (IOException e) {
            System.out.println("文件操作时出错：" + e.getMessage());
        }
    }
    
    // 目录操作
    public static void directoryOperations() {
        System.out.println("\n=== 目录操作 ===");
        
        // 创建目录
        File dir = new File("test_directory");
        if (dir.mkdir()) {
            System.out.println("目录创建成功：" + dir.getAbsolutePath());
        } else {
            System.out.println("目录已存在或创建失败");
        }
        
        // 创建多级目录
        File multiDir = new File("parent/child/grandchild");
        if (multiDir.mkdirs()) {
            System.out.println("多级目录创建成功：" + multiDir.getAbsolutePath());
        } else {
            System.out.println("多级目录已存在或创建失败");
        }
        
        // 列出目录内容
        File parentDir = new File(".");
        String[] files = parentDir.list();
        if (files != null) {
            System.out.println("当前目录下的文件和目录：");
            for (String fileName : files) {
                System.out.println("  " + fileName);
            }
        }
        
        // 使用FileFilter列出特定文件
        File[] javaFiles = parentDir.listFiles(new FileFilter() {
            @Override
            public boolean accept(File file) {
                return file.isFile() && file.getName().endsWith(".java");
            }
        });
        
        if (javaFiles != null) {
            System.out.println("当前目录下的Java文件：");
            for (File javaFile : javaFiles) {
                System.out.println("  " + javaFile.getName());
            }
        }
    }
    
    // 文件过滤
    public static void fileFiltering() {
        System.out.println("\n=== 文件过滤 ===");
        
        File currentDir = new File(".");
        
        // 列出所有目录
        File[] directories = currentDir.listFiles(File::isDirectory);
        if (directories != null) {
            System.out.println("目录列表：");
            for (File dir : directories) {
                System.out.println("  " + dir.getName());
            }
        }
        
        // 列出大于1KB的文件
        File[] largeFiles = currentDir.listFiles(new FileFilter() {
            @Override
            public boolean accept(File file) {
                return file.isFile() && file.length() > 1024;
            }
        });
        
        if (largeFiles != null) {
            System.out.println("大于1KB的文件：");
            for (File file : largeFiles) {
                System.out.printf("  %s (%d 字节)%n", file.getName(), file.length());
            }
        }
        
        // 使用FilenameFilter
        String[] txtFiles = currentDir.list(new FilenameFilter() {
            @Override
            public boolean accept(File dir, String name) {
                return name.endsWith(".txt");
            }
        });
        
        if (txtFiles != null) {
            System.out.println("文本文件：");
            for (String fileName : txtFiles) {
                System.out.println("  " + fileName);
            }
        }
    }
}
```

### 9.2 RandomAccessFile

RandomAccessFile允许随机访问文件内容，可以在文件的任意位置进行读写操作。

```java
import java.io.*;

public class RandomAccessFileExample {
    public static void main(String[] args) {
        // 基本随机访问
        basicRandomAccess();
        
        // 数据记录操作
        recordOperations();
        
        // 文件指针操作
        filePointerOperations();
    }
    
    // 基本随机访问
    public static void basicRandomAccess() {
        System.out.println("=== 基本随机访问 ===");
        
        try (RandomAccessFile raf = new RandomAccessFile("random_access_test.dat", "rw")) {
            // 写入数据
            raf.writeUTF("Hello, World!");
            raf.writeInt(12345);
            raf.writeDouble(3.14159);
            raf.writeBoolean(true);
            
            System.out.println("文件长度：" + raf.length() + " 字节");
            
            // 移动到文件开始位置
            raf.seek(0);
            
            // 按写入顺序读取数据
            System.out.println("读取UTF：" + raf.readUTF());
            System.out.println("读取Int：" + raf.readInt());
            System.out.println("读取Double：" + raf.readDouble());
            System.out.println("读取Boolean：" + raf.readBoolean());
            
        } catch (IOException e) {
            System.out.println("随机访问文件时出错：" + e.getMessage());
        }
    }
    
    // 数据记录操作
    public static void recordOperations() {
        System.out.println("\n=== 数据记录操作 ===");
        
        try (RandomAccessFile raf = new RandomAccessFile("records.dat", "rw")) {
            // 定义固定长度的记录格式
            // 姓名(20字节) + 年龄(4字节) + 分数(8字节)
            
            // 写入第一条记录
            writeRecord(raf, 0, "张三", 20, 85.5);
            
            // 写入第二条记录
            writeRecord(raf, 32, "李四", 21, 92.0);
            
            // 写入第三条记录
            writeRecord(raf, 64, "王五", 19, 78.5);
            
            System.out.println("记录写入完成，文件大小：" + raf.length() + " 字节");
            
            // 读取特定记录
            System.out.println("读取第二条记录：");
            readRecord(raf, 32);
            
            // 修改第一条记录的分数
            System.out.println("修改第一条记录的分数为95.0：");
            raf.seek(28); // 分数的位置：20(姓名) + 4(年龄) + 4(偏移量) = 28
            raf.writeDouble(95.0);
            
            // 重新读取第一条记录
            System.out.println("修改后第一条记录：");
            readRecord(raf, 0);
            
        } catch (IOException e) {
            System.out.println("记录操作时出错：" + e.getMessage());
        }
    }
    
    // 写入记录
    private static void writeRecord(RandomAccessFile raf, long position,
                                  String name, int age, double score) throws IOException {
        raf.seek(position);
        
        // 写入姓名（固定20字节）
        byte[] nameBytes = new byte[20];
        byte[] originalBytes = name.getBytes("UTF-8");
        System.arraycopy(originalBytes, 0, nameBytes, 0, 
                        Math.min(originalBytes.length, nameBytes.length));
        raf.write(nameBytes);
        
        // 写入年龄和分数
        raf.writeInt(age);
        raf.writeDouble(score);
    }
    
    // 读取记录
    private static void readRecord(RandomAccessFile raf, long position) throws IOException {
        raf.seek(position);
        
        // 读取姓名
        byte[] nameBytes = new byte[20];
        raf.readFully(nameBytes);
        String name = new String(nameBytes, "UTF-8").trim();
        
        // 读取年龄和分数
        int age = raf.readInt();
        double score = raf.readDouble();
        
        System.out.printf("姓名：%s，年龄：%d，分数：%.1f%n", name, age, score);
    }
    
    // 文件指针操作
    public static void filePointerOperations() {
        System.out.println("\n=== 文件指针操作 ===");
        
        try (RandomAccessFile raf = new RandomAccessFile("pointer_test.dat", "rw")) {
            // 写入测试数据
            raf.writeUTF("第一条消息");
            raf.writeUTF("第二条消息");
            raf.writeUTF("第三条消息");
            
            System.out.println("文件长度：" + raf.length() + " 字节");
            System.out.println("当前位置：" + raf.getFilePointer());
            
            // 移动到文件开始
            raf.seek(0);
            System.out.println("移动到开始位置：" + raf.getFilePointer());
            
            // 跳过一部分数据
            raf.skipBytes(10);
            System.out.println("跳过10字节后位置：" + raf.getFilePointer());
            
            // 读取当前位置的数据
            System.out.println("当前位置数据：" + raf.readUTF());
            
            // 获取当前长度并扩展文件
            long currentLength = raf.length();
            raf.setLength(currentLength + 100); // 扩展文件
            System.out.println("扩展后文件长度：" + raf.length());
            
            // 移动到末尾并写入数据
            raf.seek(currentLength);
            raf.writeUTF("追加的消息");
            System.out.println("追加后文件长度：" + raf.length());
            
        } catch (IOException e) {
            System.out.println("文件指针操作时出错：" + e.getMessage());
        }
    }
}
```

---

## 10.NIO(New I/O)

### 10.1 NIO核心概念

NIO（New I/O）是Java 1.4引入的一套新的I/O API，提供了与传统I/O不同的工作方式：
- 基于通道（Channel）和缓冲区（Buffer）的I/O操作
- 支持非阻塞I/O模式
- 提供了选择器（Selector）用于多路复用

### 10.2 Buffer详解

Buffer是NIO中用于存储数据的容器，它本质上是一个数组。

```java
import java.nio.*;

public class BufferExample {
    public static void main(String[] args) {
        // ByteBuffer示例
        byteBufferExample();
        
        // CharBuffer示例
        charBufferExample();
        
        // Buffer状态操作
        bufferStateOperations();
    }
    
    // ByteBuffer示例
    public static void byteBufferExample() {
        System.out.println("=== ByteBuffer示例 ===");
        
        // 创建ByteBuffer
        ByteBuffer buffer = ByteBuffer.allocate(10);
        System.out.println("初始状态 - capacity: " + buffer.capacity() + 
                          ", position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
        
        // 写入数据
        buffer.put((byte) 1);
        buffer.put((byte) 2);
        buffer.put((byte) 3);
        System.out.println("写入3个字节后 - position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
        
        // 翻转缓冲区，准备读取
        buffer.flip();
        System.out.println("flip后 - position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
        
        // 读取数据
        while (buffer.hasRemaining()) {
            System.out.println("读取到：" + buffer.get());
        }
        System.out.println("读取完成后 - position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
        
        // 清空缓冲区，准备重新写入
        buffer.clear();
        System.out.println("clear后 - position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
    }
    
    // CharBuffer示例
    public static void charBufferExample() {
        System.out.println("\n=== CharBuffer示例 ===");
        
        // 创建CharBuffer
        CharBuffer buffer = CharBuffer.allocate(20);
        
        // 写入字符数据
        String text = "Hello, NIO!";
        buffer.put(text);
        System.out.println("写入文本：" + text);
        System.out.println("position: " + buffer.position());
        
        // 翻转准备读取
        buffer.flip();
        
        // 读取字符数据
        System.out.print("读取文本：");
        while (buffer.hasRemaining()) {
            System.out.print(buffer.get());
        }
        System.out.println();
        
        // 重新填充数据
        buffer.clear();
        buffer.put("重新写入");
        buffer.flip();
        
        System.out.print("重新读取：");
        while (buffer.hasRemaining()) {
            System.out.print(buffer.get());
        }
        System.out.println();
    }
    
    // Buffer状态操作
    public static void bufferStateOperations() {
        System.out.println("\n=== Buffer状态操作 ===");
        
        ByteBuffer buffer = ByteBuffer.allocate(10);
        
        // 写入数据
        for (int i = 1; i <= 5; i++) {
            buffer.put((byte) i);
        }
        System.out.println("写入5个字节后 - position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
        
        // mark和reset
        buffer.mark(); // 标记当前位置
        buffer.put((byte) 6);
        buffer.put((byte) 7);
        System.out.println("再写入2个字节后 - position: " + buffer.position());
        
        buffer.reset(); // 回到标记位置
        System.out.println("reset后 - position: " + buffer.position());
        
        // rewind回到开始位置
        buffer.rewind();
        System.out.println("rewind后 - position: " + buffer.position());
        
        // compact压缩缓冲区
        buffer.flip(); // 准备读取
        buffer.get(); // 读取一个字节
        System.out.println("读取一个字节后 - position: " + buffer.position() + 
                          ", remaining: " + buffer.remaining());
        
        buffer.compact(); // 压缩剩余数据到开始位置
        System.out.println("compact后 - position: " + buffer.position() + 
                          ", limit: " + buffer.limit());
    }
}
```

### 10.3 Channel详解

Channel类似于传统I/O中的流，但是它支持双向操作并且是非阻塞的。

```java
import java.io.*;
import java.nio.*;
import java.nio.channels.*;

public class ChannelExample {
    public static void main(String[] args) {
        // FileChannel示例
        fileChannelExample();
        
        // Channel间数据传输
        channelTransferExample();
    }
    
    // FileChannel示例
    public static void fileChannelExample() {
        System.out.println("=== FileChannel示例 ===");
        
        try {
            // 创建测试文件
            try (RandomAccessFile file = new RandomAccessFile("channel_test.txt", "rw")) {
                FileChannel channel = file.getChannel();
                
                // 写入数据
                String data = "Hello, FileChannel!\n这是测试数据。\n";
                ByteBuffer buffer = ByteBuffer.wrap(data.getBytes("UTF-8"));
                channel.write(buffer);
                System.out.println("数据写入完成");
                
                // 读取数据
                channel.position(0); // 移动到文件开始
                ByteBuffer readBuffer = ByteBuffer.allocate(1024);
                int bytesRead = channel.read(readBuffer);
                readBuffer.flip();
                
                byte[] bytes = new byte[bytesRead];
                readBuffer.get(bytes);
                String content = new String(bytes, "UTF-8");
                System.out.println("读取到的内容：\n" + content);
                
                // 获取文件信息
                System.out.println("文件大小：" + channel.size() + " 字节");
                System.out.println("当前position：" + channel.position());
            }
            
        } catch (IOException e) {
            System.out.println("FileChannel操作时出错：" + e.getMessage());
        }
    }
    
    // Channel间数据传输
    public static void channelTransferExample() {
        System.out.println("\n=== Channel间数据传输 ===");
        
        try {
            // 创建源文件
            try (RandomAccessFile sourceFile = new RandomAccessFile("source.txt", "rw")) {
                FileChannel sourceChannel = sourceFile.getChannel();
                
                // 写入大量数据
                StringBuilder data = new StringBuilder();
                for (int i = 0; i 