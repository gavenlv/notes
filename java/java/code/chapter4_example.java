/**
 * 第四章：Java集合框架详解 - 完整示例代码
 * 
 * 本文件包含了Java集合框架的主要概念和使用示例：
 * 1. Collection接口及其实现
 * 2. List接口及其实现（ArrayList, LinkedList, Vector）
 * 3. Set接口及其实现（HashSet, LinkedHashSet, TreeSet）
 * 4. Queue接口及其实现（LinkedList, PriorityQueue）
 * 5. Map接口及其实现（HashMap, LinkedHashMap, TreeMap, Hashtable）
 * 6. 集合工具类（Collections, Arrays）
 * 7. 并发集合（ConcurrentHashMap, CopyOnWriteArrayList）
 * 8. 最佳实践和常见陷阱
 */

// 导入必要的包
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Function;

// 主类
public class Chapter4Example {
    
    // 1. Collection接口示例
    public static void demonstrateCollection() {
        System.out.println("=== Collection接口示例 ===");
        
        // 使用ArrayList作为Collection的实现
        Collection<String> collection = new ArrayList<>();
        
        // 添加元素
        collection.add("Apple");
        collection.add("Banana");
        collection.add("Orange");
        System.out.println("添加元素后：" + collection);
        
        // 获取集合大小
        System.out.println("集合大小：" + collection.size());
        
        // 判断是否包含元素
        System.out.println("是否包含Apple：" + collection.contains("Apple"));
        
        // 删除元素
        collection.remove("Banana");
        System.out.println("删除Banana后：" + collection);
        
        // 判断是否为空
        System.out.println("集合是否为空：" + collection.isEmpty());
        
        // 批量操作
        Collection<String> moreFruits = Arrays.asList("Grape", "Mango");
        collection.addAll(moreFruits);
        System.out.println("批量添加后：" + collection);
        
        // 使用迭代器遍历
        Iterator<String> iterator = collection.iterator();
        System.out.print("使用迭代器遍历：");
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println();
        
        // 转换为数组
        Object[] array = collection.toArray();
        System.out.println("转换为数组：" + Arrays.toString(array));
        
        // 清空集合
        collection.clear();
        System.out.println("清空后：" + collection);
        System.out.println();
    }
    
    // 2. List接口示例
    public static void demonstrateList() {
        System.out.println("=== List接口示例 ===");
        
        // ArrayList示例
        System.out.println("--- ArrayList示例 ---");
        List<String> arrayList = new ArrayList<>();
        arrayList.add("Apple");
        arrayList.add("Banana");
        arrayList.add("Orange");
        arrayList.add(1, "Grape"); // 在索引1处插入
        System.out.println("添加元素后：" + arrayList);
        System.out.println("索引0的元素：" + arrayList.get(0));
        System.out.println("索引2的元素：" + arrayList.get(2));
        arrayList.set(1, "Mango");
        System.out.println("修改后：" + arrayList);
        arrayList.remove(0);
        System.out.println("删除索引0后：" + arrayList);
        
        // LinkedList示例
        System.out.println("\n--- LinkedList示例 ---");
        LinkedList<String> linkedList = new LinkedList<>();
        linkedList.add("Apple");
        linkedList.add("Banana");
        linkedList.add("Orange");
        System.out.println("添加元素后：" + linkedList);
        linkedList.addFirst("Mango");
        linkedList.addLast("Grape");
        System.out.println("在头部和尾部添加后：" + linkedList);
        System.out.println("第一个元素：" + linkedList.getFirst());
        System.out.println("最后一个元素：" + linkedList.getLast());
        linkedList.removeFirst();
        linkedList.removeLast();
        System.out.println("删除首尾元素后：" + linkedList);
        
        // Vector示例
        System.out.println("\n--- Vector示例 ---");
        Vector<String> vector = new Vector<>();
        vector.add("Apple");
        vector.add("Banana");
        vector.add("Orange");
        System.out.println("添加元素后：" + vector);
        vector.addElement("Grape");
        System.out.println("使用addElement添加后：" + vector);
        System.out.println("第一个元素：" + vector.firstElement());
        System.out.println("最后一个元素：" + vector.lastElement());
        System.out.println();
    }
    
    // 3. Set接口示例
    public static void demonstrateSet() {
        System.out.println("=== Set接口示例 ===");
        
        // HashSet示例
        System.out.println("--- HashSet示例 ---");
        Set<String> hashSet = new HashSet<>();
        hashSet.add("Apple");
        hashSet.add("Banana");
        hashSet.add("Orange");
        hashSet.add("Apple"); // 重复元素不会被添加
        System.out.println("HashSet：" + hashSet);
        hashSet.add(null);
        hashSet.add(null); // 重复的null也不会被添加
        System.out.println("添加null后：" + hashSet);
        
        // LinkedHashSet示例
        System.out.println("\n--- LinkedHashSet示例 ---");
        Set<String> linkedHashSet = new LinkedHashSet<>();
        linkedHashSet.add("Apple");
        linkedHashSet.add("Banana");
        linkedHashSet.add("Orange");
        linkedHashSet.add("Apple"); // 重复元素
        System.out.println("LinkedHashSet（保持插入顺序）：" + linkedHashSet);
        
        // TreeSet示例
        System.out.println("\n--- TreeSet示例 ---");
        TreeSet<Integer> treeSet = new TreeSet<>();
        treeSet.add(5);
        treeSet.add(2);
        treeSet.add(8);
        treeSet.add(1);
        treeSet.add(3);
        System.out.println("TreeSet（自然排序）：" + treeSet);
        System.out.println("第一个元素：" + treeSet.first());
        System.out.println("最后一个元素：" + treeSet.last());
        System.out.println("小于5的最大元素：" + treeSet.lower(5));
        System.out.println("大于5的最小元素：" + treeSet.higher(5));
        System.out.println();
    }
    
    // 4. Queue接口示例
    public static void demonstrateQueue() {
        System.out.println("=== Queue接口示例 ===");
        
        // LinkedList实现Queue
        System.out.println("--- LinkedList实现Queue ---");
        Queue<String> queue = new LinkedList<>();
        queue.offer("Task1");
        queue.offer("Task2");
        queue.offer("Task3");
        System.out.println("入队后：" + queue);
        System.out.println("队首元素：" + queue.peek());
        System.out.println("队列大小：" + queue.size());
        while (!queue.isEmpty()) {
            String task = queue.poll();
            System.out.println("处理任务：" + task + "，剩余任务数：" + queue.size());
        }
        
        // PriorityQueue示例
        System.out.println("\n--- PriorityQueue示例 ---");
        PriorityQueue<Integer> priorityQueue = new PriorityQueue<>();
        priorityQueue.offer(5);
        priorityQueue.offer(2);
        priorityQueue.offer(8);
        priorityQueue.offer(1);
        priorityQueue.offer(3);
        System.out.println("优先队列：" + priorityQueue);
        System.out.print("按优先级出队：");
        while (!priorityQueue.isEmpty()) {
            System.out.print(priorityQueue.poll() + " ");
        }
        System.out.println();
        System.out.println();
    }
    
    // 5. Map接口示例
    public static void demonstrateMap() {
        System.out.println("=== Map接口示例 ===");
        
        // HashMap示例
        System.out.println("--- HashMap示例 ---");
        Map<String, Integer> hashMap = new HashMap<>();
        hashMap.put("Apple", 10);
        hashMap.put("Banana", 5);
        hashMap.put("Orange", 8);
        hashMap.put("Grape", 15);
        System.out.println("HashMap：" + hashMap);
        hashMap.put("Apple", 12);
        System.out.println("更新Apple后：" + hashMap);
        System.out.println("Apple的数量：" + hashMap.get("Apple"));
        System.out.println("不存在的键：" + hashMap.get("Mango"));
        System.out.println("Mango的数量（默认0）：" + hashMap.getOrDefault("Mango", 0));
        
        // LinkedHashMap示例
        System.out.println("\n--- LinkedHashMap示例 ---");
        Map<String, Integer> linkedHashMap = new LinkedHashMap<>();
        linkedHashMap.put("Apple", 10);
        linkedHashMap.put("Banana", 5);
        linkedHashMap.put("Orange", 8);
        linkedHashMap.put("Grape", 15);
        System.out.println("LinkedHashMap（保持插入顺序）：" + linkedHashMap);
        
        // TreeMap示例
        System.out.println("\n--- TreeMap示例 ---");
        Map<String, Integer> treeMap = new TreeMap<>();
        treeMap.put("Banana", 5);
        treeMap.put("Apple", 10);
        treeMap.put("Orange", 8);
        treeMap.put("Grape", 15);
        System.out.println("TreeMap（自然排序）：" + treeMap);
        
        // Hashtable示例
        System.out.println("\n--- Hashtable示例 ---");
        Hashtable<String, Integer> hashtable = new Hashtable<>();
        hashtable.put("Apple", 10);
        hashtable.put("Banana", 5);
        hashtable.put("Orange", 8);
        System.out.println("Hashtable：" + hashtable);
        System.out.println();
    }
    
    // 6. 集合工具类示例
    public static void demonstrateCollectionsUtils() {
        System.out.println("=== 集合工具类示例 ===");
        
        // Collections工具类
        System.out.println("--- Collections工具类 ---");
        List<Integer> list = new ArrayList<>();
        list.add(5);
        list.add(2);
        list.add(8);
        list.add(1);
        list.add(3);
        System.out.println("原列表：" + list);
        Collections.sort(list);
        System.out.println("排序后：" + list);
        Collections.reverse(list);
        System.out.println("反转后：" + list);
        Collections.shuffle(list);
        System.out.println("混洗后：" + list);
        System.out.println("最大值：" + Collections.max(list));
        System.out.println("最小值：" + Collections.min(list));
        
        // Arrays工具类
        System.out.println("\n--- Arrays工具类 ---");
        int[] array = {5, 2, 8, 1, 3};
        System.out.println("原数组：" + Arrays.toString(array));
        Arrays.sort(array);
        System.out.println("排序后：" + Arrays.toString(array));
        int index = Arrays.binarySearch(array, 5);
        System.out.println("二分查找5的位置：" + index);
        System.out.println();
    }
    
    // 7. 并发集合示例
    public static void demonstrateConcurrentCollections() {
        System.out.println("=== 并发集合示例 ===");
        
        // ConcurrentHashMap示例
        System.out.println("--- ConcurrentHashMap示例 ---");
        ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();
        concurrentMap.put("Apple", 10);
        concurrentMap.put("Banana", 5);
        concurrentMap.put("Orange", 8);
        System.out.println("ConcurrentHashMap：" + concurrentMap);
        concurrentMap.putIfAbsent("Grape", 15);
        System.out.println("putIfAbsent后：" + concurrentMap);
        concurrentMap.replace("Apple", 10, 12);
        System.out.println("replace后：" + concurrentMap);
        
        // CopyOnWriteArrayList示例
        System.out.println("\n--- CopyOnWriteArrayList示例 ---");
        CopyOnWriteArrayList<String> cowList = new CopyOnWriteArrayList<>();
        cowList.add("Apple");
        cowList.add("Banana");
        cowList.add("Orange");
        System.out.println("CopyOnWriteArrayList：" + cowList);
        System.out.println();
    }
    
    // 8. 最佳实践示例
    public static void demonstrateBestPractices() {
        System.out.println("=== 最佳实践示例 ===");
        
        // 使用泛型避免类型转换
        List<String> stringList = new ArrayList<>();
        stringList.add("Hello");
        String str = stringList.get(0); // 不需要类型转换
        System.out.println("使用泛型：" + str);
        
        // 初始化集合容量
        List<Integer> list = new ArrayList<>(1000); // 预设容量
        System.out.println("预设容量的列表创建成功");
        
        // 使用增强for循环遍历
        System.out.print("增强for循环遍历：");
        for (String s : stringList) {
            System.out.print(s + " ");
        }
        System.out.println();
        
        // 使用isEmpty()而不是size()==0
        if (stringList.isEmpty()) {
            System.out.println("列表为空");
        } else {
            System.out.println("列表不为空");
        }
        
        // 使用迭代器删除元素
        List<Integer> numbers = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        Iterator<Integer> iterator = numbers.iterator();
        while (iterator.hasNext()) {
            if (iterator.next() % 2 == 0) {
                iterator.remove(); // 安全删除
            }
        }
        System.out.println("删除偶数后：" + numbers);
        
        // 使用Collections工具类
        List<Integer> unsorted = Arrays.asList(5, 2, 8, 1, 3);
        Collections.sort(unsorted);
        System.out.println("排序后：" + unsorted);
        System.out.println();
    }
    
    // 9. 常见陷阱示例
    public static void demonstrateCommonPitfalls() {
        System.out.println("=== 常见陷阱示例 ===");
        
        // 正确的做法：使用迭代器删除元素
        List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        Iterator<Integer> iterator = list.iterator();
        while (iterator.hasNext()) {
            if (iterator.next() % 2 == 0) {
                iterator.remove();
            }
        }
        System.out.println("正确删除偶数后：" + list);
        
        // 正确：使用equals比较字符串
        List<String> stringList = new ArrayList<>();
        stringList.add(new String("Hello"));
        String target = new String("Hello");
        boolean found = false;
        for (String s : stringList) {
            if (s.equals(target)) {
                found = true;
                break;
            }
        }
        System.out.println("正确比较结果：" + found);
        
        // 使用泛型避免类型转换
        List<String> genericList = new ArrayList<>();
        genericList.add("Hello");
        String str = genericList.get(0); // 不需要类型转换
        System.out.println("使用泛型避免类型转换：" + str);
        System.out.println();
    }
    
    // 综合示例：学生成绩管理系统
    public static void studentGradeManagementSystem() {
        System.out.println("=== 综合示例：学生成绩管理系统 ===");
        
        // 使用HashMap存储学生信息
        Map<String, Student> students = new HashMap<>();
        
        // 添加学生
        students.put("001", new Student("001", "张三", 85, 90, 78));
        students.put("002", new Student("002", "李四", 92, 88, 95));
        students.put("003", new Student("003", "王五", 78, 82, 85));
        
        // 显示所有学生
        System.out.println("所有学生信息：");
        for (Map.Entry<String, Student> entry : students.entrySet()) {
            System.out.println(entry.getValue());
        }
        
        // 按平均分排序（使用TreeMap）
        TreeMap<Double, List<Student>> sortedByAverage = new TreeMap<>(Collections.reverseOrder());
        for (Student student : students.values()) {
            double average = student.getAverageScore();
            sortedByAverage.computeIfAbsent(average, k -> new ArrayList<>()).add(student);
        }
        
        System.out.println("\n按平均分排序的学生：");
        for (Map.Entry<Double, List<Student>> entry : sortedByAverage.entrySet()) {
            System.out.println("平均分：" + entry.getKey());
            for (Student student : entry.getValue()) {
                System.out.println("  " + student);
            }
        }
        
        // 查找特定学生
        Student student = students.get("002");
        if (student != null) {
            System.out.println("\n查找学生002：" + student);
        }
        
        // 统计信息
        DoubleSummaryStatistics stats = students.values().stream()
                .mapToDouble(Student::getAverageScore)
                .summaryStatistics();
        
        System.out.println("\n成绩统计：");
        System.out.println("最高平均分：" + stats.getMax());
        System.out.println("最低平均分：" + stats.getMin());
        System.out.println("平均分：" + stats.getAverage());
        System.out.println("学生总数：" + stats.getCount());
        System.out.println();
    }
    
    // 学生类
    static class Student {
        private String id;
        private String name;
        private int mathScore;
        private int englishScore;
        private int scienceScore;
        
        public Student(String id, String name, int mathScore, int englishScore, int scienceScore) {
            this.id = id;
            this.name = name;
            this.mathScore = mathScore;
            this.englishScore = englishScore;
            this.scienceScore = scienceScore;
        }
        
        public double getAverageScore() {
            return (mathScore + englishScore + scienceScore) / 3.0;
        }
        
        @Override
        public String toString() {
            return String.format("学生[ID=%s, 姓名=%s, 数学=%d, 英语=%d, 科学=%d, 平均=%.2f]",
                    id, name, mathScore, englishScore, scienceScore, getAverageScore());
        }
        
        // Getters
        public String getId() { return id; }
        public String getName() { return name; }
        public int getMathScore() { return mathScore; }
        public int getEnglishScore() { return englishScore; }
        public int getScienceScore() { return scienceScore; }
    }
    
    // 主方法
    public static void main(String[] args) {
        System.out.println("第四章：Java集合框架详解 - 完整示例代码");
        System.out.println("========================================");
        
        // 演示各个集合类型的使用
        demonstrateCollection();
        demonstrateList();
        demonstrateSet();
        demonstrateQueue();
        demonstrateMap();
        demonstrateCollectionsUtils();
        demonstrateConcurrentCollections();
        demonstrateBestPractices();
        demonstrateCommonPitfalls();
        
        // 综合示例
        studentGradeManagementSystem();
        
        System.out.println("所有示例演示完毕！");
    }
}