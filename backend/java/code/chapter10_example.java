import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.lang.annotation.*;

/**
 * 第十章：Java反射机制 - 完整示例代码
 * 
 * 本示例涵盖了Java反射的所有核心概念和最佳实践：
 * 1. Class类的使用
 * 2. 构造器反射
 * 3. 方法反射
 * 4. 字段反射
 * 5. 数组反射
 * 6. 注解反射
 * 7. 泛型反射
 * 8. 动态代理
 * 9. 性能优化
 * 10. 综合示例：通用对象序列化器
 */

// 1. 自定义注解用于演示注解反射
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.FIELD, ElementType.METHOD})
@interface MyAnnotation {
    String value() default "";
    int count() default 0;
}

// 2. 带有注解的示例类
@MyAnnotation(value = "测试类", count = 5)
class Person {
    @MyAnnotation(value = "姓名字段")
    private String name;
    
    @MyAnnotation(value = "年龄字段")
    private int age;
    
    public Person() {}
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @MyAnnotation(value = "获取姓名方法", count = 1)
    public String getName() {
        return name;
    }
    
    @MyAnnotation(value = "设置姓名方法", count = 2)
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        this.age = age;
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

// 3. 带有泛型的示例类
class GenericContainer<T> {
    private List<T> items = new ArrayList<>();
    private Map<String, T> namedItems = new HashMap<>();
    
    public void addItem(T item) {
        items.add(item);
    }
    
    public void addNamedItem(String name, T item) {
        namedItems.put(name, item);
    }
    
    public List<T> getItems() {
        return items;
    }
    
    public Map<String, T> getNamedItems() {
        return namedItems;
    }
}

// 4. 接口用于动态代理示例
interface Calculator {
    int add(int a, int b);
    int multiply(int a, int b);
}

// 5. 接口实现类
class CalculatorImpl implements Calculator {
    @Override
    public int add(int a, int b) {
        System.out.println("执行加法运算: " + a + " + " + b);
        return a + b;
    }
    
    @Override
    public int multiply(int a, int b) {
        System.out.println("执行乘法运算: " + a + " * " + b);
        return a * b;
    }
}

// 6. 动态代理调用处理器
class CalculatorInvocationHandler implements InvocationHandler {
    private Object target;
    
    public CalculatorInvocationHandler(Object target) {
        this.target = target;
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("方法调用前: " + method.getName());
        long startTime = System.currentTimeMillis();
        
        // 调用目标方法
        Object result = method.invoke(target, args);
        
        long endTime = System.currentTimeMillis();
        System.out.println("方法调用后: " + method.getName() + ", 耗时: " + (endTime - startTime) + "ms");
        
        return result;
    }
}

// 7. 反射工具类 - 缓存反射对象以提高性能
class ReflectionCache {
    private static final Map<String, Method> methodCache = new ConcurrentHashMap<>();
    private static final Map<String, Field> fieldCache = new ConcurrentHashMap<>();
    private static final Map<String, Constructor<?>> constructorCache = new ConcurrentHashMap<>();
    
    public static Method getMethod(Class<?> clazz, String methodName, Class<?>... paramTypes) 
            throws NoSuchMethodException {
        String key = clazz.getName() + "#" + methodName + "(" + Arrays.toString(paramTypes) + ")";
        return methodCache.computeIfAbsent(key, k -> {
            try {
                return clazz.getMethod(methodName, paramTypes);
            } catch (NoSuchMethodException e) {
                throw new RuntimeException(e);
            }
        });
    }
    
    public static Field getField(Class<?> clazz, String fieldName) throws NoSuchFieldException {
        String key = clazz.getName() + "." + fieldName;
        return fieldCache.computeIfAbsent(key, k -> {
            try {
                return clazz.getDeclaredField(fieldName);
            } catch (NoSuchFieldException e) {
                throw new RuntimeException(e);
            }
        });
    }
    
    @SuppressWarnings("unchecked")
    public static <T> Constructor<T> getConstructor(Class<T> clazz, Class<?>... paramTypes) 
            throws NoSuchMethodException {
        String key = clazz.getName() + "(" + Arrays.toString(paramTypes) + ")";
        return (Constructor<T>) constructorCache.computeIfAbsent(key, k -> {
            try {
                return clazz.getConstructor(paramTypes);
            } catch (NoSuchMethodException e) {
                throw new RuntimeException(e);
            }
        });
    }
}

// 8. 安全访问工具类
class AccessibleUtils {
    private static final Set<Member> accessibleMembers = ConcurrentHashMap.newKeySet();
    
    public static void makeAccessible(AccessibleObject object) {
        if (!accessibleMembers.contains(object)) {
            object.setAccessible(true);
            accessibleMembers.add((Member) object);
        }
    }
}

// 9. 通用对象序列化器 - 使用反射实现对象到Map的转换
class ObjectSerializer {
    public static Map<String, Object> serialize(Object obj) throws Exception {
        Map<String, Object> result = new HashMap<>();
        Class<?> clazz = obj.getClass();
        
        // 处理类注解
        MyAnnotation classAnnotation = clazz.getAnnotation(MyAnnotation.class);
        if (classAnnotation != null) {
            result.put("@classAnnotation", classAnnotation.value() + "(count=" + classAnnotation.count() + ")");
        }
        
        // 处理字段
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            makeAccessible(field);
            
            String fieldName = field.getName();
            Object fieldValue = field.get(obj);
            result.put(fieldName, fieldValue);
            
            // 处理字段注解
            MyAnnotation fieldAnnotation = field.getAnnotation(MyAnnotation.class);
            if (fieldAnnotation != null) {
                result.put(fieldName + "@annotation", fieldAnnotation.value());
            }
        }
        
        return result;
    }
    
    public static <T> T deserialize(Map<String, Object> data, Class<T> clazz) throws Exception {
        // 使用无参构造器创建实例
        Constructor<T> constructor = ReflectionCache.getConstructor(clazz);
        T obj = constructor.newInstance();
        
        // 设置字段值
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            String fieldName = entry.getKey();
            Object fieldValue = entry.getValue();
            
            // 跳过注解信息
            if (fieldName.endsWith("@annotation") || fieldName.equals("@classAnnotation")) {
                continue;
            }
            
            try {
                Field field = ReflectionCache.getField(clazz, fieldName);
                makeAccessible(field);
                field.set(obj, fieldValue);
            } catch (NoSuchFieldException e) {
                // 忽略不存在的字段
                System.out.println("警告: 字段 " + fieldName + " 不存在于类 " + clazz.getSimpleName());
            }
        }
        
        return obj;
    }
}

// 10. 性能测试工具类
class PerformanceTest {
    public static void testDirectCall() {
        String str = "Hello World";
        int iterations = 100000;
        
        long start = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            str.substring(0, 5);
        }
        long directTime = System.nanoTime() - start;
        
        System.out.println("直接调用耗时: " + directTime / 1000000 + "ms");
    }
    
    public static void testReflectionCall() throws Exception {
        String str = "Hello World";
        int iterations = 100000;
        
        Method method = ReflectionCache.getMethod(String.class, "substring", int.class, int.class);
        
        // 首次调用（包含查找开销）
        long start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {  // 减少次数以避免超时
            method.invoke(str, 0, 5);
        }
        long firstCallTime = System.nanoTime() - start;
        
        // 缓存后调用
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            method.invoke(str, 0, 5);
        }
        long cachedCallTime = System.nanoTime() - start;
        
        System.out.println("反射首次调用耗时: " + firstCallTime / 1000000 + "ms");
        System.out.println("反射缓存调用耗时: " + cachedCallTime / 1000000 + "ms");
    }
}

// 11. 泛型反射示例
class GenericReflectionExample {
    public static void analyzeGenericType(Field field) {
        System.out.println("分析字段: " + field.getName());
        Type genericType = field.getGenericType();
        
        if (genericType instanceof ParameterizedType) {
            ParameterizedType paramType = (ParameterizedType) genericType;
            Type[] actualTypes = paramType.getActualTypeArguments();
            
            System.out.println("  原始类型: " + paramType.getRawType());
            for (int i = 0; i < actualTypes.length; i++) {
                System.out.println("  类型参数[" + i + "]: " + actualTypes[i]);
            }
        } else {
            System.out.println("  非参数化类型: " + genericType);
        }
    }
    
    public static void demonstrateGenericReflection() throws Exception {
        Field itemsField = GenericContainer.class.getDeclaredField("items");
        Field namedItemsField = GenericContainer.class.getDeclaredField("namedItems");
        
        System.out.println("=== 泛型反射示例 ===");
        analyzeGenericType(itemsField);
        analyzeGenericType(namedItemsField);
    }
}

// 12. 数组反射示例
class ArrayReflectionExample {
    public static void demonstrateArrayReflection() {
        System.out.println("=== 数组反射示例 ===");
        
        // 创建一维数组
        Object intArray = Array.newInstance(int.class, 5);
        for (int i = 0; i < 5; i++) {
            Array.set(intArray, i, i * 10);
        }
        
        System.out.println("一维数组内容:");
        int length = Array.getLength(intArray);
        for (int i = 0; i < length; i++) {
            System.out.print(Array.getInt(intArray, i) + " ");
        }
        System.out.println();
        
        // 创建二维数组
        Object matrix = Array.newInstance(int.class, 2, 3);
        Object row0 = Array.get(matrix, 0);
        Object row1 = Array.get(matrix, 1);
        
        for (int i = 0; i < 3; i++) {
            Array.set(row0, i, i + 1);
            Array.set(row1, i, i + 4);
        }
        
        System.out.println("二维数组内容:");
        for (int i = 0; i < 2; i++) {
            Object row = Array.get(matrix, i);
            for (int j = 0; j < 3; j++) {
                System.out.print(Array.getInt(row, j) + " ");
            }
            System.out.println();
        }
        
        // 获取数组信息
        System.out.println("数组类型: " + intArray.getClass().getComponentType());
        System.out.println("数组长度: " + Array.getLength(intArray));
    }
}

// 13. 注解反射示例
class AnnotationReflectionExample {
    public static void demonstrateAnnotationReflection() throws Exception {
        System.out.println("=== 注解反射示例 ===");
        
        Class<Person> clazz = Person.class;
        
        // 获取类注解
        MyAnnotation classAnnotation = clazz.getAnnotation(MyAnnotation.class);
        if (classAnnotation != null) {
            System.out.println("类注解: " + classAnnotation.value() + " (count=" + classAnnotation.count() + ")");
        }
        
        // 获取字段注解
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            MyAnnotation fieldAnnotation = field.getAnnotation(MyAnnotation.class);
            if (fieldAnnotation != null) {
                System.out.println("字段 " + field.getName() + " 的注解: " + fieldAnnotation.value());
            }
        }
        
        // 获取方法注解
        Method[] methods = clazz.getDeclaredMethods();
        for (Method method : methods) {
            MyAnnotation methodAnnotation = method.getAnnotation(MyAnnotation.class);
            if (methodAnnotation != null) {
                System.out.println("方法 " + method.getName() + " 的注解: " + methodAnnotation.value() + 
                                 " (count=" + methodAnnotation.count() + ")");
            }
        }
    }
}

// 14. 动态代理示例
class DynamicProxyExample {
    public static void demonstrateDynamicProxy() {
        System.out.println("=== 动态代理示例 ===");
        
        // 创建目标对象
        Calculator target = new CalculatorImpl();
        
        // 创建代理对象
        Calculator proxy = (Calculator) Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            new CalculatorInvocationHandler(target)
        );
        
        // 通过代理对象调用方法
        int sum = proxy.add(10, 20);
        int product = proxy.multiply(5, 6);
        
        System.out.println("加法结果: " + sum);
        System.out.println("乘法结果: " + product);
    }
}

// 15. 综合示例：对象序列化和反序列化
class SerializationExample {
    public static void demonstrateSerialization() throws Exception {
        System.out.println("=== 对象序列化示例 ===");
        
        // 创建对象
        Person person = new Person("张三", 25);
        System.out.println("原始对象: " + person);
        
        // 序列化
        Map<String, Object> serializedData = ObjectSerializer.serialize(person);
        System.out.println("序列化数据: " + serializedData);
        
        // 反序列化
        Person deserializedPerson = ObjectSerializer.deserialize(serializedData, Person.class);
        System.out.println("反序列化对象: " + deserializedPerson);
        
        // 验证对象相等性
        System.out.println("对象相等: " + person.toString().equals(deserializedPerson.toString()));
    }
}

// 主测试类
public class Chapter10Example {
    public static void main(String[] args) {
        System.out.println("第十章：Java反射机制 示例程序");
        System.out.println("=====================================");
        
        try {
            // 1. Class类基本使用
            System.out.println("\n1. Class类基本使用:");
            Class<String> stringClass = String.class;
            System.out.println("类名: " + stringClass.getName());
            System.out.println("简单类名: " + stringClass.getSimpleName());
            System.out.println("是否为接口: " + stringClass.isInterface());
            System.out.println("是否为数组: " + stringClass.isArray());
            
            // 2. 获取Class对象的不同方式
            System.out.println("\n2. 获取Class对象的不同方式:");
            Class<?> clazz1 = "Hello".getClass();
            Class<?> clazz2 = Class.forName("java.lang.Integer");
            Class<?> clazz3 = Integer.TYPE;  // 基本类型
            System.out.println("通过getClass(): " + clazz1.getSimpleName());
            System.out.println("通过forName(): " + clazz2.getSimpleName());
            System.out.println("基本类型: " + clazz3.getSimpleName());
            
            // 3. 构造器反射
            System.out.println("\n3. 构造器反射:");
            Constructor<String> constructor = String.class.getConstructor(byte[].class);
            String str = constructor.newInstance("Hello".getBytes());
            System.out.println("通过反射创建的字符串: " + str);
            
            // 4. 方法反射
            System.out.println("\n4. 方法反射:");
            Method substringMethod = String.class.getMethod("substring", int.class, int.class);
            String result = (String) substringMethod.invoke("Hello World", 0, 5);
            System.out.println("通过反射调用substring: " + result);
            
            // 5. 字段反射
            System.out.println("\n5. 字反射:");
            Field[] fields = Person.class.getDeclaredFields();
            System.out.println("Person类的字段数量: " + fields.length);
            for (Field field : fields) {
                System.out.println("  字段: " + field.getName() + " (类型: " + field.getType().getSimpleName() + ")");
            }
            
            // 6. 数组反射示例
            ArrayReflectionExample.demonstrateArrayReflection();
            
            // 7. 注解反射示例
            AnnotationReflectionExample.demonstrateAnnotationReflection();
            
            // 8. 泛型反射示例
            GenericReflectionExample.demonstrateGenericReflection();
            
            // 9. 动态代理示例
            DynamicProxyExample.demonstrateDynamicProxy();
            
            // 10. 对象序列化示例
            SerializationExample.demonstrateSerialization();
            
            // 11. 性能测试
            System.out.println("\n11. 性能测试:");
            PerformanceTest.testDirectCall();
            PerformanceTest.testReflectionCall();
            
            System.out.println("\n所有示例执行完毕!");
            
        } catch (Exception e) {
            System.err.println("示例执行出错: " + e.getMessage());
            e.printStackTrace();
        }
    }
}