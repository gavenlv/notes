/**
 * 第二章示例代码：单例模式的各种实现方式演示
 */

// 1. 饿汉式单例模式
class EagerSingleton {
    // 在类加载时就完成实例化
    private static final EagerSingleton INSTANCE = new EagerSingleton();
    
    // 私有构造方法，防止外部实例化
    private EagerSingleton() {}
    
    // 提供全局访问点
    public static EagerSingleton getInstance() {
        return INSTANCE;
    }
    
    public void showMessage() {
        System.out.println("这是饿汉式单例模式");
    }
}

// 2. 懒汉式单例模式（线程不安全）
class LazySingleton {
    private static LazySingleton instance;
    
    private LazySingleton() {}
    
    public static LazySingleton getInstance() {
        if (instance == null) {
            instance = new LazySingleton();
        }
        return instance;
    }
    
    public void showMessage() {
        System.out.println("这是懒汉式单例模式（线程不安全）");
    }
}

// 3. 线程安全的懒汉式单例模式
class ThreadSafeLazySingleton {
    private static ThreadSafeLazySingleton instance;
    
    private ThreadSafeLazySingleton() {}
    
    // 同步方法，保证线程安全
    public static synchronized ThreadSafeLazySingleton getInstance() {
        if (instance == null) {
            instance = new ThreadSafeLazySingleton();
        }
        return instance;
    }
    
    public void showMessage() {
        System.out.println("这是线程安全的懒汉式单例模式");
    }
}

// 4. 双重检查锁定单例模式
class DoubleCheckLockingSingleton {
    // volatile关键字确保多线程环境下的可见性
    private static volatile DoubleCheckLockingSingleton instance;
    
    private DoubleCheckLockingSingleton() {}
    
    public static DoubleCheckLockingSingleton getInstance() {
        // 第一次检查
        if (instance == null) {
            synchronized (DoubleCheckLockingSingleton.class) {
                // 第二次检查
                if (instance == null) {
                    instance = new DoubleCheckLockingSingleton();
                }
            }
        }
        return instance;
    }
    
    public void showMessage() {
        System.out.println("这是双重检查锁定单例模式");
    }
}

// 5. 静态内部类单例模式
class StaticInnerClassSingleton {
    
    private StaticInnerClassSingleton() {}
    
    // 静态内部类
    private static class SingletonHolder {
        private static final StaticInnerClassSingleton INSTANCE = new StaticInnerClassSingleton();
    }
    
    public static StaticInnerClassSingleton getInstance() {
        return SingletonHolder.INSTANCE;
    }
    
    public void showMessage() {
        System.out.println("这是静态内部类单例模式");
    }
}

// 6. 枚举单例模式
enum EnumSingleton {
    INSTANCE;
    
    public void showMessage() {
        System.out.println("这是枚举单例模式");
    }
    
    public void doSomething() {
        System.out.println("执行某些操作");
    }
}

// 7. 防止反射破坏的单例模式
class ReflectionSafeSingleton {
    private static volatile ReflectionSafeSingleton instance;
    
    private ReflectionSafeSingleton() {
        // 防止反射破坏单例
        if (instance != null) {
            throw new RuntimeException("不能通过反射创建实例！");
        }
    }
    
    public static ReflectionSafeSingleton getInstance() {
        if (instance == null) {
            synchronized (ReflectionSafeSingleton.class) {
                if (instance == null) {
                    instance = new ReflectionSafeSingleton();
                }
            }
        }
        return instance;
    }
    
    public void showMessage() {
        System.out.println("这是防反射破坏的单例模式");
    }
}

// 8. 实际应用：日志记录器
class Logger {
    private static volatile Logger instance;
    private StringBuilder logContent;
    
    private Logger() {
        logContent = new StringBuilder();
    }
    
    public static Logger getInstance() {
        if (instance == null) {
            synchronized (Logger.class) {
                if (instance == null) {
                    instance = new Logger();
                }
            }
        }
        return instance;
    }
    
    public void log(String message) {
        logContent.append(new java.util.Date()).append(": ").append(message).append("\n");
        System.out.println("LOG: " + message);
    }
    
    public String getLogContent() {
        return logContent.toString();
    }
}

// 主类 - 演示各种单例模式的使用
public class Chapter2Example {
    public static void main(String[] args) {
        System.out.println("=== 第二章：单例模式示例 ===\n");
        
        // 1. 饿汉式单例模式演示
        System.out.println("1. 饿汉式单例模式演示：");
        EagerSingleton eager1 = EagerSingleton.getInstance();
        EagerSingleton eager2 = EagerSingleton.getInstance();
        System.out.println("eager1 == eager2: " + (eager1 == eager2)); // true
        eager1.showMessage();
        
        // 2. 懒汉式单例模式演示
        System.out.println("\n2. 懒汉式单例模式演示：");
        LazySingleton lazy1 = LazySingleton.getInstance();
        LazySingleton lazy2 = LazySingleton.getInstance();
        System.out.println("lazy1 == lazy2: " + (lazy1 == lazy2)); // true
        lazy1.showMessage();
        
        // 3. 线程安全的懒汉式单例模式演示
        System.out.println("\n3. 线程安全的懒汉式单例模式演示：");
        ThreadSafeLazySingleton threadSafe1 = ThreadSafeLazySingleton.getInstance();
        ThreadSafeLazySingleton threadSafe2 = ThreadSafeLazySingleton.getInstance();
        System.out.println("threadSafe1 == threadSafe2: " + (threadSafe1 == threadSafe2)); // true
        threadSafe1.showMessage();
        
        // 4. 双重检查锁定单例模式演示
        System.out.println("\n4. 双重检查锁定单例模式演示：");
        DoubleCheckLockingSingleton doubleCheck1 = DoubleCheckLockingSingleton.getInstance();
        DoubleCheckLockingSingleton doubleCheck2 = DoubleCheckLockingSingleton.getInstance();
        System.out.println("doubleCheck1 == doubleCheck2: " + (doubleCheck1 == doubleCheck2)); // true
        doubleCheck1.showMessage();
        
        // 5. 静态内部类单例模式演示
        System.out.println("\n5. 静态内部类单例模式演示：");
        StaticInnerClassSingleton staticInner1 = StaticInnerClassSingleton.getInstance();
        StaticInnerClassSingleton staticInner2 = StaticInnerClassSingleton.getInstance();
        System.out.println("staticInner1 == staticInner2: " + (staticInner1 == staticInner2)); // true
        staticInner1.showMessage();
        
        // 6. 枚举单例模式演示
        System.out.println("\n6. 枚举单例模式演示：");
        EnumSingleton enum1 = EnumSingleton.INSTANCE;
        EnumSingleton enum2 = EnumSingleton.INSTANCE;
        System.out.println("enum1 == enum2: " + (enum1 == enum2)); // true
        enum1.showMessage();
        enum1.doSomething();
        
        // 7. 防反射破坏的单例模式演示
        System.out.println("\n7. 防反射破坏的单例模式演示：");
        ReflectionSafeSingleton reflectionSafe1 = ReflectionSafeSingleton.getInstance();
        ReflectionSafeSingleton reflectionSafe2 = ReflectionSafeSingleton.getInstance();
        System.out.println("reflectionSafe1 == reflectionSafe2: " + (reflectionSafe1 == reflectionSafe2)); // true
        reflectionSafe1.showMessage();
        
        // 8. 实际应用：日志记录器演示
        System.out.println("\n8. 实际应用：日志记录器演示：");
        Logger logger = Logger.getInstance();
        logger.log("系统启动");
        logger.log("用户登录");
        logger.log("数据查询");
        System.out.println("日志内容：\n" + logger.getLogContent());
        
        System.out.println("\n=== 示例结束 ===");
    }
}