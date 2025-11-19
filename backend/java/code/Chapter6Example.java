import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;

/**
 * 第六章：Java输入输出(I/O)操作 - 完整示例代码
 * 
 * 本文件包含了Java I/O操作的主要概念和实用示例，涵盖了：
 * 1. 字节流和字符流操作
 * 2. 缓冲流的使用
 * 3. 转换流的应用
 * 4. 数据流和打印流
 * 5. 对象序列化
 * 6. 文件操作
 * 7. NIO相关操作
 * 8. 综合示例：文件管理和数据处理系统
 */

// 示例1：字节流基础操作
class ByteStreamDemo {
    public static void demonstrate() {
        System.out.println("=== 字节流基础操作 ===");
        
        try {
            // FileOutputStream示例
            try (FileOutputStream fos = new FileOutputStream("byte_output.txt")) {
                String data = "Hello, Byte Stream!";
                byte[] bytes = data.getBytes();
                fos.write(bytes);
                System.out.println("数据已写入byte_output.txt");
            }
            
            // FileInputStream示例
            try (FileInputStream fis = new FileInputStream("byte_output.txt")) {
                int data;
                System.out.print("从文件读取的数据: ");
                while ((data = fis.read()) != -1) {
                    System.out.print((char) data);
                }
                System.out.println();
            }
            
            // 文件复制示例
            try (FileInputStream fis = new FileInputStream("byte_output.txt");
                 FileOutputStream fos = new FileOutputStream("byte_copy.txt")) {
                byte[] buffer = new byte[1024];
                int bytesRead;
                while ((bytesRead = fis.read(buffer)) != -1) {
                    fos.write(buffer, 0, bytesRead);
                }
                System.out.println("文件复制完成: byte_output.txt -> byte_copy.txt");
            }
            
        } catch (IOException e) {
            System.err.println("字节流操作出错: " + e.getMessage());
        }
    }
}

// 示例2：字符流操作
class CharacterStreamDemo {
    public static void demonstrate() {
        System.out.println("\n=== 字符流操作 ===");
        
        try {
            // FileWriter示例
            try (FileWriter fw = new FileWriter("char_output.txt")) {
                fw.write("Hello, Character Stream!\n");
                fw.write("这是中文测试内容。\n");
                System.out.println("字符数据已写入char_output.txt");
            }
            
            // FileReader示例
            try (FileReader fr = new FileReader("char_output.txt")) {
                int data;
                System.out.print("从文件读取的字符数据:\n");
                while ((data = fr.read()) != -1) {
                    System.out.print((char) data);
                }
                System.out.println();
            }
            
            // 使用指定编码
            try (OutputStreamWriter osw = new OutputStreamWriter(
                    new FileOutputStream("encoded_output.txt"), "UTF-8")) {
                osw.write("UTF-8编码测试: Hello, 世界!");
                System.out.println("UTF-8编码数据已写入encoded_output.txt");
            }
            
        } catch (IOException e) {
            System.err.println("字符流操作出错: " + e.getMessage());
        }
    }
}

// 示例3：缓冲流操作
class BufferedStreamDemo {
    public static void demonstrate() {
        System.out.println("\n=== 缓冲流操作 ===");
        
        try {
            // 创建测试数据
            try (BufferedWriter bw = new BufferedWriter(new FileWriter("buffer_test.txt"))) {
                for (int i = 1; i <= 1000; i++) {
                    bw.write("这是第" + i + "行数据\n");
                }
                System.out.println("测试数据已写入buffer_test.txt");
            }
            
            // 使用缓冲流读取
            long startTime = System.currentTimeMillis();
            try (BufferedReader br = new BufferedReader(new FileReader("buffer_test.txt"))) {
                String line;
                int lineCount = 0;
                while ((line = br.readLine()) != null) {
                    lineCount++;
                }
                long endTime = System.currentTimeMillis();
                System.out.println("缓冲流读取" + lineCount + "行数据，耗时: " + (endTime - startTime) + "ms");
            }
            
            // 对比无缓冲流
            startTime = System.currentTimeMillis();
            try (FileReader fr = new FileReader("buffer_test.txt")) {
                int data;
                long charCount = 0;
                while ((data = fr.read()) != -1) {
                    charCount++;
                }
                long endTime = System.currentTimeMillis();
                System.out.println("无缓冲流读取" + charCount + "个字符，耗时: " + (endTime - startTime) + "ms");
            }
            
        } catch (IOException e) {
            System.err.println("缓冲流操作出错: " + e.getMessage());
        }
    }
}

// 示例4：数据流操作
class DataStreamDemo {
    public static void demonstrate() {
        System.out.println("\n=== 数据流操作 ===");
        
        try {
            // 写入基本数据类型
            try (DataOutputStream dos = new DataOutputStream(new FileOutputStream("data_output.dat"))) {
                dos.writeBoolean(true);
                dos.writeByte(127);
                dos.writeChar('A');
                dos.writeShort(32767);
                dos.writeInt(2147483647);
                dos.writeLong(9223372036854775807L);
                dos.writeFloat(3.14159f);
                dos.writeDouble(2.718281828459045);
                dos.writeUTF("Hello, Data Stream!");
                System.out.println("基本数据类型已写入data_output.dat");
            }
            
            // 读取基本数据类型
            try (DataInputStream dis = new DataInputStream(new FileInputStream("data_output.dat"))) {
                System.out.println("读取的数据:");
                System.out.println("Boolean: " + dis.readBoolean());
                System.out.println("Byte: " + dis.readByte());
                System.out.println("Char: " + dis.readChar());
                System.out.println("Short: " + dis.readShort());
                System.out.println("Int: " + dis.readInt());
                System.out.println("Long: " + dis.readLong());
                System.out.println("Float: " + dis.readFloat());
                System.out.println("Double: " + dis.readDouble());
                System.out.println("UTF: " + dis.readUTF());
            }
            
        } catch (IOException e) {
            System.err.println("数据流操作出错: " + e.getMessage());
        }
    }
}

// 示例5：对象序列化
class SerializationDemo implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;
    private transient String password; // 不会被序列化
    
    public SerializationDemo(String name, int age, String password) {
        this.name = name;
        this.age = age;
        this.password = password;
    }
    
    public static void demonstrate() {
        System.out.println("\n=== 对象序列化 ===");
        
        SerializationDemo obj = new SerializationDemo("张三", 25, "secret123");
        System.out.println("序列化前对象: " + obj);
        
        try {
            // 序列化
            try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("object.ser"))) {
                oos.writeObject(obj);
                System.out.println("对象已序列化到object.ser");
            }
            
            // 反序列化
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("object.ser"))) {
                SerializationDemo deserializedObj = (SerializationDemo) ois.readObject();
                System.out.println("反序列化后对象: " + deserializedObj);
                System.out.println("注意: password字段为null，因为它是transient的");
            }
            
        } catch (IOException | ClassNotFoundException e) {
            System.err.println("对象序列化操作出错: " + e.getMessage());
        }
    }
    
    @Override
    public String toString() {
        return "SerializationDemo{name='" + name + "', age=" + age + ", password='" + password + "'}";
    }
}

// 示例6：文件操作
class FileOperationDemo {
    public static void demonstrate() {
        System.out.println("\n=== 文件操作 ===");
        
        try {
            // 创建文件
            File file = new File("test_file.txt");
            if (file.createNewFile()) {
                System.out.println("文件创建成功: " + file.getAbsolutePath());
            } else {
                System.out.println("文件已存在: " + file.getAbsolutePath());
            }
            
            // 写入内容
            try (FileWriter writer = new FileWriter(file)) {
                writer.write("这是测试文件内容\n第二行内容\n");
            }
            
            // 获取文件信息
            System.out.println("文件信息:");
            System.out.println("  名称: " + file.getName());
            System.out.println("  路径: " + file.getPath());
            System.out.println("  绝对路径: " + file.getAbsolutePath());
            System.out.println("  大小: " + file.length() + " 字节");
            System.out.println("  是否可读: " + file.canRead());
            System.out.println("  是否可写: " + file.canWrite());
            
            // 创建目录
            File dir = new File("test_directory");
            if (dir.mkdir()) {
                System.out.println("目录创建成功: " + dir.getAbsolutePath());
            }
            
            // 列出当前目录内容
            File currentDir = new File(".");
            String[] files = currentDir.list();
            if (files != null) {
                System.out.println("当前目录文件数量: " + files.length);
            }
            
        } catch (IOException e) {
            System.err.println("文件操作出错: " + e.getMessage());
        }
    }
}

// 示例7：NIO操作
class NIODemo {
    public static void demonstrate() {
        System.out.println("\n=== NIO操作 ===");
        
        try {
            // ByteBuffer示例
            System.out.println("1. ByteBuffer操作:");
            ByteBuffer buffer = ByteBuffer.allocate(10);
            System.out.println("  初始状态 - capacity: " + buffer.capacity() + 
                             ", position: " + buffer.position() + 
                             ", limit: " + buffer.limit());
            
            // 写入数据
            buffer.put((byte) 1);
            buffer.put((byte) 2);
            buffer.put((byte) 3);
            System.out.println("  写入3个字节后 - position: " + buffer.position() + 
                             ", limit: " + buffer.limit());
            
            // 翻转准备读取
            buffer.flip();
            System.out.println("  flip后 - position: " + buffer.position() + 
                             ", limit: " + buffer.limit());
            
            // 读取数据
            System.out.print("  读取数据: ");
            while (buffer.hasRemaining()) {
                System.out.print(buffer.get() + " ");
            }
            System.out.println();
            
            // FileChannel示例
            System.out.println("\n2. FileChannel操作:");
            try (RandomAccessFile file = new RandomAccessFile("nio_test.txt", "rw");
                 FileChannel channel = file.getChannel()) {
                
                // 写入数据
                String data = "Hello, NIO World!";
                ByteBuffer writeBuffer = ByteBuffer.wrap(data.getBytes());
                channel.write(writeBuffer);
                System.out.println("  数据已写入nio_test.txt");
                
                // 读取数据
                channel.position(0); // 回到文件开始
                ByteBuffer readBuffer = ByteBuffer.allocate(1024);
                channel.read(readBuffer);
                readBuffer.flip();
                
                byte[] bytes = new byte[readBuffer.remaining()];
                readBuffer.get(bytes);
                String content = new String(bytes);
                System.out.println("  读取数据: " + content);
            }
            
        } catch (IOException e) {
            System.err.println("NIO操作出错: " + e.getMessage());
        }
    }
}

// 示例8：打印流操作
class PrintStreamDemo {
    public static void demonstrate() {
        System.out.println("\n=== 打印流操作 ===");
        
        try {
            // PrintWriter示例
            try (PrintWriter pw = new PrintWriter("print_output.txt")) {
                pw.println("PrintWriter测试");
                pw.println("整数: " + 42);
                pw.println("浮点数: " + 3.14159);
                pw.printf("格式化输出: %s - %d - %.2f%n", "测试", 123, 45.67);
                System.out.println("数据已写入print_output.txt");
            }
            
            // 读取并显示内容
            try (BufferedReader br = new BufferedReader(new FileReader("print_output.txt"))) {
                String line;
                System.out.println("文件内容:");
                while ((line = br.readLine()) != null) {
                    System.out.println("  " + line);
                }
            }
            
        } catch (IOException e) {
            System.err.println("打印流操作出错: " + e.getMessage());
        }
    }
}

// 综合示例：文件管理和数据处理系统
class FileManagementSystem {
    private String basePath;
    
    public FileManagementSystem(String basePath) {
        this.basePath = basePath;
        new File(basePath).mkdirs(); // 确保基础目录存在
    }
    
    // 创建文件
    public boolean createFile(String fileName, String content) {
        try {
            File file = new File(basePath, fileName);
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
                writer.write(content);
            }
            return true;
        } catch (IOException e) {
            System.err.println("创建文件失败: " + e.getMessage());
            return false;
        }
    }
    
    // 读取文件
    public String readFile(String fileName) {
        try {
            File file = new File(basePath, fileName);
            if (!file.exists()) {
                return "文件不存在: " + fileName;
            }
            
            StringBuilder content = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    content.append(line).append("\n");
                }
            }
            return content.toString();
        } catch (IOException e) {
            return "读取文件失败: " + e.getMessage();
        }
    }
    
    // 复制文件
    public boolean copyFile(String sourceFile, String destFile) {
        try {
            File src = new File(basePath, sourceFile);
            File dest = new File(basePath, destFile);
            
            try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream(src));
                 BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(dest))) {
                
                byte[] buffer = new byte[1024];
                int bytesRead;
                while ((bytesRead = bis.read(buffer)) != -1) {
                    bos.write(buffer, 0, bytesRead);
                }
            }
            return true;
        } catch (IOException e) {
            System.err.println("复制文件失败: " + e.getMessage());
            return false;
        }
    }
    
    // 列出目录内容
    public List<String> listFiles() {
        File dir = new File(basePath);
        File[] files = dir.listFiles();
        List<String> fileList = new ArrayList<>();
        
        if (files != null) {
            for (File file : files) {
                fileList.add(file.getName() + (file.isDirectory() ? " (目录)" : " (" + file.length() + " 字节)"));
            }
        }
        return fileList;
    }
    
    // 删除文件
    public boolean deleteFile(String fileName) {
        File file = new File(basePath, fileName);
        return file.delete();
    }
    
    // 序列化对象到文件
    public <T extends Serializable> boolean saveObject(T obj, String fileName) {
        try {
            File file = new File(basePath, fileName);
            try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(file))) {
                oos.writeObject(obj);
            }
            return true;
        } catch (IOException e) {
            System.err.println("保存对象失败: " + e.getMessage());
            return false;
        }
    }
    
    // 从文件反序列化对象
    @SuppressWarnings("unchecked")
    public <T extends Serializable> T loadObject(String fileName) {
        try {
            File file = new File(basePath, fileName);
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                return (T) ois.readObject();
            }
        } catch (IOException | ClassNotFoundException e) {
            System.err.println("加载对象失败: " + e.getMessage());
            return null;
        }
    }
    
    public static void demonstrate() {
        System.out.println("\n=== 综合示例：文件管理和数据处理系统 ===");
        
        FileManagementSystem fms = new FileManagementSystem("fms_data");
        
        // 创建测试文件
        fms.createFile("test1.txt", "这是第一个测试文件\n包含多行内容");
        fms.createFile("test2.txt", "这是第二个测试文件\n也包含多行内容");
        System.out.println("创建了测试文件");
        
        // 读取文件
        System.out.println("读取test1.txt内容:");
        System.out.println(fms.readFile("test1.txt"));
        
        // 复制文件
        fms.copyFile("test1.txt", "test1_backup.txt");
        System.out.println("已复制test1.txt为test1_backup.txt");
        
        // 列出文件
        System.out.println("当前目录文件列表:");
        for (String file : fms.listFiles()) {
            System.out.println("  " + file);
        }
        
        // 序列化对象
        Map<String, Integer> testData = new HashMap<>();
        testData.put("key1", 100);
        testData.put("key2", 200);
        testData.put("key3", 300);
        
        fms.saveObject(testData, "test_data.ser");
        System.out.println("已序列化测试数据到test_data.ser");
        
        // 反序列化对象
        Map<String, Integer> loadedData = fms.loadObject("test_data.ser");
        System.out.println("反序列化数据: " + loadedData);
        
        // 清理测试文件
        fms.deleteFile("test1.txt");
        fms.deleteFile("test2.txt");
        fms.deleteFile("test1_backup.txt");
        fms.deleteFile("test_data.ser");
        System.out.println("测试文件已清理");
    }
}

// 主类 - 运行所有示例
public class Chapter6Example {
    public static void main(String[] args) {
        System.out.println("第六章：Java输入输出(I/O)操作 - 完整示例");
        System.out.println("========================================");
        
        // 运行各个示例
        ByteStreamDemo.demonstrate();
        CharacterStreamDemo.demonstrate();
        BufferedStreamDemo.demonstrate();
        DataStreamDemo.demonstrate();
        SerializationDemo.demonstrate();
        FileOperationDemo.demonstrate();
        NIODemo.demonstrate();
        PrintStreamDemo.demonstrate();
        FileManagementSystem.demonstrate();
        
        System.out.println("\n所有示例运行完成!");
    }
    
    @Override
    public String toString() {
        return "Chapter6Example{}";
    }
}