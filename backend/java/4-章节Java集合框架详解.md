# 第4章 Java集合框架详解

## 目录
1. [集合框架概述](#1集合框架概述)
2. [Collection接口](#2collection接口)
3. [List接口及实现类](#3list接口及实现类)
4. [Set接口及实现类](#4set接口及实现类)
5. [Queue接口及实现类](#5queue接口及实现类)
6. [Map接口及实现类](#6map接口及实现类)
7. [集合工具类](#7集合工具类)
8. [并发集合](#8并发集合)
9. [最佳实践](#9最佳实践)
10. [总结](#10总结)

---

## 1.集合框架概述

### 1.1 什么是集合框架

Java集合框架（Java Collections Framework，JCF）是为表示和操作集合而规定的一种统一的架构。它包含以下内容：

- **接口**：定义了集合的抽象数据类型
- **实现类**：提供了接口的具体实现
- **算法**：实现了对集合进行排序、搜索等操作的静态方法

### 1.2 集合框架的层次结构

```
        Iterable (接口)
            ↑
        Collection (接口)
        ↙        ↘
    List (接口)   Set (接口)   Queue (接口)
       ↑            ↑            ↑
  ArrayList    HashSet      LinkedList
  LinkedList   TreeSet      PriorityQueue
  Vector       LinkedHashSet

        Map (接口)
         ↙    ↓    ↘
   HashMap  TreeMap  LinkedHashMap
   Hashtable
```

### 1.3 集合框架的优势

1. **减少编程工作量**：提供现成的数据结构和算法
2. **提高程序速度和质量**：高性能的实现
3. **允许互操作**：不同API之间可以传递集合
4. **易于学习和使用**：统一的架构和API

---

## 2.Collection接口

### 2.1 Collection接口概述

Collection是集合框架的根接口，定义了所有集合类型都具有的基本操作。

### 2.2 Collection接口的主要方法

```java
public interface Collection<E> extends Iterable<E> {
    // 基本操作
    boolean add(E element);           // 添加元素
    boolean remove(Object o);         // 删除元素
    boolean contains(Object o);       // 判断是否包含元素
    int size();                       // 获取集合大小
    boolean isEmpty();                // 判断是否为空
    void clear();                     // 清空集合
    
    // 批量操作
    boolean addAll(Collection<? extends E> c);    // 添加集合
    boolean removeAll(Collection<?> c);           // 删除集合中的元素
    boolean retainAll(Collection<?> c);           // 保留集合中的元素
    boolean containsAll(Collection<?> c);         // 判断是否包含集合中的所有元素
    
    // 数组转换
    Object[] toArray();                           // 转换为数组
    <T> T[] toArray(T[] a);                       // 转换为指定类型数组
    
    // 迭代器
    Iterator<E> iterator();                       // 获取迭代器
}
```

### 2.3 Collection接口使用示例

```java
import java.util.*;

public class CollectionDemo {
    public static void main(String[] args) {
        // 创建Collection实例（使用ArrayList）
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
    }
}
```

---

## 3.List接口及实现类

### 3.1 List接口概述

List是一个有序集合（也称为序列），允许重复元素。可以通过索引访问元素。

### 3.2 List接口的主要方法

```java
public interface List<E> extends Collection<E> {
    // 位置访问
    E get(int index);                 // 获取指定位置元素
    E set(int index, E element);      // 设置指定位置元素
    void add(int index, E element);   // 在指定位置插入元素
    E remove(int index);              // 删除指定位置元素
    
    // 搜索操作
    int indexOf(Object o);            // 返回第一次出现的位置
    int lastIndexOf(Object o);        // 返回最后一次出现的位置
    
    // 列表迭代器
    ListIterator<E> listIterator();   // 获取列表迭代器
    ListIterator<E> listIterator(int index); // 从指定位置获取列表迭代器
    
    // 子列表
    List<E> subList(int fromIndex, int toIndex); // 获取子列表
}
```

### 3.3 ArrayList

ArrayList是基于动态数组实现的List，支持快速随机访问。

```java
import java.util.*;

public class ArrayListDemo {
    public static void main(String[] args) {
        // 创建ArrayList
        List<String> list = new ArrayList<>();
        
        // 添加元素
        list.add("Apple");
        list.add("Banana");
        list.add("Orange");
        list.add(1, "Grape"); // 在索引1处插入
        System.out.println("添加元素后：" + list);
        
        // 访问元素
        System.out.println("索引0的元素：" + list.get(0));
        System.out.println("索引2的元素：" + list.get(2));
        
        // 修改元素
        list.set(1, "Mango");
        System.out.println("修改后：" + list);
        
        // 删除元素
        String removed = list.remove(0);
        System.out.println("删除的元素：" + removed);
        System.out.println("删除后：" + list);
        
        // 搜索元素
        System.out.println("Apple的位置：" + list.indexOf("Apple"));
        System.out.println("Orange的位置：" + list.lastIndexOf("Orange"));
        
        // 遍历方式
        System.out.println("=== 遍历方式 ===");
        // 1. 增强for循环
        System.out.print("增强for循环：");
        for (String fruit : list) {
            System.out.print(fruit + " ");
        }
        System.out.println();
        
        // 2. 普通for循环
        System.out.print("普通for循环：");
        for (int i = 0; i < list.size(); i++) {
            System.out.print(list.get(i) + " ");
        }
        System.out.println();
        
        // 3. 迭代器
        System.out.print("迭代器：");
        Iterator<String> iterator = list.iterator();
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println();
        
        // 4. 列表迭代器
        System.out.print("列表迭代器（反向）：");
        ListIterator<String> listIterator = list.listIterator(list.size());
        while (listIterator.hasPrevious()) {
            System.out.print(listIterator.previous() + " ");
        }
        System.out.println();
        
        // 子列表
        List<String> subList = list.subList(0, 2);
        System.out.println("子列表：" + subList);
        
        // 转换为数组
        String[] array = list.toArray(new String[0]);
        System.out.println("转换为数组：" + Arrays.toString(array));
    }
}
```

### 3.4 LinkedList

LinkedList是基于双向链表实现的List，支持高效的插入和删除操作。

```java
import java.util.*;

public class LinkedListDemo {
    public static void main(String[] args) {
        // 创建LinkedList
        LinkedList<String> linkedList = new LinkedList<>();
        
        // 添加元素
        linkedList.add("Apple");
        linkedList.add("Banana");
        linkedList.add("Orange");
        System.out.println("添加元素后：" + linkedList);
        
        // 在头部和尾部添加
        linkedList.addFirst("Mango");
        linkedList.addLast("Grape");
        System.out.println("在头部和尾部添加后：" + linkedList);
        
        // 在指定位置插入
        linkedList.add(2, "Kiwi");
        System.out.println("在索引2插入后：" + linkedList);
        
        // 访问元素
        System.out.println("第一个元素：" + linkedList.getFirst());
        System.out.println("最后一个元素：" + linkedList.getLast());
        System.out.println("索引2的元素：" + linkedList.get(2));
        
        // 修改元素
        linkedList.set(1, "Pineapple");
        System.out.println("修改索引1后：" + linkedList);
        
        // 删除元素
        String removedFirst = linkedList.removeFirst();
        String removedLast = linkedList.removeLast();
        String removedIndex = linkedList.remove(1);
        System.out.println("删除的第一个元素：" + removedFirst);
        System.out.println("删除的最后一个元素：" + removedLast);
        System.out.println("删除索引1的元素：" + removedIndex);
        System.out.println("删除后：" + linkedList);
        
        // 栈操作（LIFO）
        linkedList.push("Watermelon"); // 压栈
        System.out.println("压栈后：" + linkedList);
        String popped = linkedList.pop(); // 弹栈
        System.out.println("弹栈元素：" + popped);
        System.out.println("弹栈后：" + linkedList);
        
        // 队列操作（FIFO）
        linkedList.offer("Strawberry"); // 入队
        System.out.println("入队后：" + linkedList);
        String polled = linkedList.poll(); // 出队
        System.out.println("出队元素：" + polled);
        System.out.println("出队后：" + linkedList);
    }
}
```

### 3.5 Vector

Vector是线程安全的动态数组，与ArrayList类似但性能较低。

```java
import java.util.*;

public class VectorDemo {
    public static void main(String[] args) {
        // 创建Vector
        Vector<String> vector = new Vector<>();
        
        // 添加元素
        vector.add("Apple");
        vector.add("Banana");
        vector.add("Orange");
        System.out.println("添加元素后：" + vector);
        
        // Vector特有的方法
        vector.addElement("Grape");
        System.out.println("使用addElement添加后：" + vector);
        
        // 访问元素
        System.out.println("第一个元素：" + vector.firstElement());
        System.out.println("最后一个元素：" + vector.lastElement());
        System.out.println("索引1的元素：" + vector.elementAt(1));
        
        // 容量相关
        System.out.println("当前容量：" + vector.capacity());
        System.out.println("大小：" + vector.size());
        
        // 删除元素
        vector.removeElementAt(1);
        System.out.println("删除索引1后：" + vector);
        
        vector.removeAllElements();
        System.out.println("清空后：" + vector);
    }
}
```

---

## 4.Set接口及实现类

### 4.1 Set接口概述

Set是一个不包含重复元素的集合。它模拟了数学上的集合概念。

### 4.2 HashSet

HashSet是基于哈希表实现的Set，不保证元素的顺序。

```java
import java.util.*;

public class HashSetDemo {
    public static void main(String[] args) {
        // 创建HashSet
        Set<String> set = new HashSet<>();
        
        // 添加元素
        set.add("Apple");
        set.add("Banana");
        set.add("Orange");
        set.add("Apple"); // 重复元素不会被添加
        System.out.println("添加元素后：" + set);
        
        // 添加null元素
        set.add(null);
        set.add(null); // 重复的null也不会被添加
        System.out.println("添加null后：" + set);
        
        // 删除元素
        set.remove("Banana");
        System.out.println("删除Banana后：" + set);
        
        // 判断是否包含元素
        System.out.println("是否包含Orange：" + set.contains("Orange"));
        System.out.println("是否包含Banana：" + set.contains("Banana"));
        
        // 遍历
        System.out.print("遍历HashSet：");
        for (String fruit : set) {
            System.out.print(fruit + " ");
        }
        System.out.println();
        
        // 批量操作
        Set<String> otherSet = new HashSet<>();
        otherSet.add("Grape");
        otherSet.add("Mango");
        otherSet.add("Orange");
        
        // 并集
        Set<String> union = new HashSet<>(set);
        union.addAll(otherSet);
        System.out.println("并集：" + union);
        
        // 交集
        Set<String> intersection = new HashSet<>(set);
        intersection.retainAll(otherSet);
        System.out.println("交集：" + intersection);
        
        // 差集
        Set<String> difference = new HashSet<>(set);
        difference.removeAll(otherSet);
        System.out.println("差集：" + difference);
    }
}
```

### 4.3 LinkedHashSet

LinkedHashSet是基于链表和哈希表实现的Set，维护元素的插入顺序。

```java
import java.util.*;

public class LinkedHashSetDemo {
    public static void main(String[] args) {
        // 创建LinkedHashSet
        Set<String> linkedHashSet = new LinkedHashSet<>();
        
        // 添加元素
        linkedHashSet.add("Apple");
        linkedHashSet.add("Banana");
        linkedHashSet.add("Orange");
        linkedHashSet.add("Grape");
        linkedHashSet.add("Apple"); // 重复元素
        System.out.println("LinkedHashSet（保持插入顺序）：" + linkedHashSet);
        
        // 删除元素
        linkedHashSet.remove("Banana");
        System.out.println("删除Banana后：" + linkedHashSet);
        
        // 遍历
        System.out.print("遍历LinkedHashSet：");
        for (String fruit : linkedHashSet) {
            System.out.print(fruit + " ");
        }
        System.out.println();
    }
}
```

### 4.4 TreeSet

TreeSet是基于红黑树实现的Set，可以对元素进行排序。

```java
import java.util.*;

public class TreeSetDemo {
    public static void main(String[] args) {
        // 创建TreeSet（自然排序）
        TreeSet<Integer> treeSet = new TreeSet<>();
        
        // 添加元素
        treeSet.add(5);
        treeSet.add(2);
        treeSet.add(8);
        treeSet.add(1);
        treeSet.add(3);
        System.out.println("TreeSet（自然排序）：" + treeSet);
        
        // 添加重复元素
        treeSet.add(2);
        System.out.println("添加重复元素后：" + treeSet);
        
        // 基本操作
        System.out.println("第一个元素：" + treeSet.first());
        System.out.println("最后一个元素：" + treeSet.last());
        System.out.println("小于5的最大元素：" + treeSet.lower(5));
        System.out.println("大于5的最小元素：" + treeSet.higher(5));
        System.out.println("小于等于5的最大元素：" + treeSet.floor(5));
        System.out.println("大于等于5的最小元素：" + treeSet.ceiling(5));
        
        // 子集操作
        System.out.println("2到5之间的元素：" + treeSet.subSet(2, 5));
        System.out.println("小于5的元素：" + treeSet.headSet(5));
        System.out.println("大于等于5的元素：" + treeSet.tailSet(5));
        
        // 字符串排序
        TreeSet<String> stringSet = new TreeSet<>();
        stringSet.add("Banana");
        stringSet.add("Apple");
        stringSet.add("Orange");
        stringSet.add("Grape");
        System.out.println("字符串TreeSet：" + stringSet);
        
        // 自定义排序（按长度排序）
        TreeSet<String> customSet = new TreeSet<>((s1, s2) -> s1.length() - s2.length());
        customSet.addAll(Arrays.asList("Banana", "Apple", "Orange", "Grape", "Kiwi"));
        System.out.println("按长度排序：" + customSet);
    }
}
```

---

## 5.Queue接口及实现类

### 5.1 Queue接口概述

Queue是队列接口，通常按照FIFO（先进先出）的原则对元素进行排序。

### 5.2 Queue接口的主要方法

```java
public interface Queue<E> extends Collection<E> {
    // 插入操作
    boolean add(E e);        // 插入元素，队列满时抛出异常
    boolean offer(E e);      // 插入元素，队列满时返回false
    
    // 删除操作
    E remove();              // 删除并返回队首元素，队列空时抛出异常
    E poll();                // 删除并返回队首元素，队列空时返回null
    
    // 检查操作
    E element();             // 返回队首元素，队列空时抛出异常
    E peek();                // 返回队首元素，队列空时返回null
}
```

### 5.3 LinkedList实现Queue

```java
import java.util.*;

public class QueueDemo {
    public static void main(String[] args) {
        // 使用LinkedList作为队列
        Queue<String> queue = new LinkedList<>();
        
        // 入队操作
        queue.offer("Task1");
        queue.offer("Task2");
        queue.offer("Task3");
        System.out.println("入队后：" + queue);
        
        // 查看队首元素
        System.out.println("队首元素：" + queue.peek());
        System.out.println("队列大小：" + queue.size());
        
        // 出队操作
        while (!queue.isEmpty()) {
            String task = queue.poll();
            System.out.println("处理任务：" + task + "，剩余任务数：" + queue.size());
        }
        
        // 测试异常情况
        System.out.println("空队列peek：" + queue.peek()); // 返回null
        System.out.println("空队列poll：" + queue.poll()); // 返回null
    }
}
```

### 5.4 PriorityQueue

PriorityQueue是一个基于优先堆的无界优先队列。

```java
import java.util.*;

public class PriorityQueueDemo {
    public static void main(String[] args) {
        // 创建默认优先级队列（最小堆）
        PriorityQueue<Integer> priorityQueue = new PriorityQueue<>();
        
        // 添加元素
        priorityQueue.offer(5);
        priorityQueue.offer(2);
        priorityQueue.offer(8);
        priorityQueue.offer(1);
        priorityQueue.offer(3);
        System.out.println("优先队列：" + priorityQueue);
        
        // 按优先级出队
        System.out.print("按优先级出队：");
        while (!priorityQueue.isEmpty()) {
            System.out.print(priorityQueue.poll() + " ");
        }
        System.out.println();
        
        // 自定义比较器（最大堆）
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>((a, b) -> b - a);
        maxHeap.offer(5);
        maxHeap.offer(2);
        maxHeap.offer(8);
        maxHeap.offer(1);
        maxHeap.offer(3);
        System.out.print("最大堆出队：");
        while (!maxHeap.isEmpty()) {
            System.out.print(maxHeap.poll() + " ");
        }
        System.out.println();
        
        // 字符串按长度排序
        PriorityQueue<String> stringQueue = new PriorityQueue<>((s1, s2) -> s1.length() - s2.length());
        stringQueue.offer("Banana");
        stringQueue.offer("Apple");
        stringQueue.offer("Orange");
        stringQueue.offer("Grape");
        stringQueue.offer("Kiwi");
        
        System.out.print("按长度优先级出队：");
        while (!stringQueue.isEmpty()) {
            System.out.print(stringQueue.poll() + " ");
        }
        System.out.println();
    }
}
```

---

## 6.Map接口及实现类

### 6.1 Map接口概述

Map是一个存储键值对的集合，每个键最多只能映射到一个值。

### 6.2 Map接口的主要方法

```java
public interface Map<K,V> {
    // 基本操作
    V put(K key, V value);           // 存放键值对
    V get(Object key);               // 获取值
    V remove(Object key);            // 删除键值对
    boolean containsKey(Object key); // 判断是否包含键
    boolean containsValue(Object value); // 判断是否包含值
    int size();                      // 获取大小
    boolean isEmpty();               // 判断是否为空
    void clear();                    // 清空
    
    // 批量操作
    void putAll(Map<? extends K, ? extends V> m); // 批量存放
    
    // 视图
    Set<K> keySet();                 // 获取键的集合
    Collection<V> values();          // 获取值的集合
    Set<Map.Entry<K,V>> entrySet();  // 获取键值对的集合
}
```

### 6.3 HashMap

HashMap是基于哈希表实现的Map，不保证映射的顺序。

```java
import java.util.*;

public class HashMapDemo {
    public static void main(String[] args) {
        // 创建HashMap
        Map<String, Integer> map = new HashMap<>();
        
        // 添加键值对
        map.put("Apple", 10);
        map.put("Banana", 5);
        map.put("Orange", 8);
        map.put("Grape", 15);
        System.out.println("HashMap：" + map);
        
        // 添加重复键（会覆盖原值）
        map.put("Apple", 12);
        System.out.println("更新Apple后：" + map);
        
        // 获取值
        System.out.println("Apple的数量：" + map.get("Apple"));
        System.out.println("不存在的键：" + map.get("Mango")); // 返回null
        
        // 获取值（带默认值）
        System.out.println("Mango的数量（默认0）：" + map.getOrDefault("Mango", 0));
        
        // 判断是否包含键或值
        System.out.println("是否包含键Apple：" + map.containsKey("Apple"));
        System.out.println("是否包含值10：" + map.containsValue(10));
        
        // 删除键值对
        Integer removed = map.remove("Banana");
        System.out.println("删除的Banana数量：" + removed);
        System.out.println("删除后：" + map);
        
        // 遍历方式
        System.out.println("=== 遍历方式 ===");
        
        // 1. 遍历键
        System.out.print("遍历键：");
        for (String key : map.keySet()) {
            System.out.print(key + " ");
        }
        System.out.println();
        
        // 2. 遍历值
        System.out.print("遍历值：");
        for (Integer value : map.values()) {
            System.out.print(value + " ");
        }
        System.out.println();
        
        // 3. 遍历键值对
        System.out.print("遍历键值对：");
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.print(entry.getKey() + "=" + entry.getValue() + " ");
        }
        System.out.println();
        
        // 4. 使用迭代器
        System.out.print("使用迭代器：");
        Iterator<Map.Entry<String, Integer>> iterator = map.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<String, Integer> entry = iterator.next();
            System.out.print(entry.getKey() + "=" + entry.getValue() + " ");
        }
        System.out.println();
        
        // 批量操作
        Map<String, Integer> otherMap = new HashMap<>();
        otherMap.put("Mango", 7);
        otherMap.put("Kiwi", 3);
        map.putAll(otherMap);
        System.out.println("批量添加后：" + map);
        
        // 计算操作
        map.compute("Apple", (key, value) -> value + 5);
        System.out.println("Apple计算后：" + map);
        
        map.computeIfAbsent("Pineapple", key -> 20);
        System.out.println("计算不存在的键后：" + map);
        
        map.computeIfPresent("Orange", (key, value) -> value * 2);
        System.out.println("计算存在的键后：" + map);
    }
}
```

### 6.4 LinkedHashMap

LinkedHashMap是保持插入顺序的HashMap。

```java
import java.util.*;

public class LinkedHashMapDemo {
    public static void main(String[] args) {
        // 创建LinkedHashMap
        Map<String, Integer> linkedMap = new LinkedHashMap<>();
        
        // 添加键值对
        linkedMap.put("Apple", 10);
        linkedMap.put("Banana", 5);
        linkedMap.put("Orange", 8);
        linkedMap.put("Grape", 15);
        System.out.println("LinkedHashMap（保持插入顺序）：" + linkedMap);
        
        // 遍历
        System.out.print("遍历LinkedHashMap：");
        for (Map.Entry<String, Integer> entry : linkedMap.entrySet()) {
            System.out.print(entry.getKey() + "=" + entry.getValue() + " ");
        }
        System.out.println();
        
        // 访问顺序模式
        Map<String, Integer> accessOrderMap = new LinkedHashMap<>(16, 0.75f, true);
        accessOrderMap.put("A", 1);
        accessOrderMap.put("B", 2);
        accessOrderMap.put("C", 3);
        
        // 访问元素会改变顺序
        accessOrderMap.get("A");
        accessOrderMap.get("C");
        System.out.println("访问顺序模式：" + accessOrderMap);
    }
}
```

### 6.5 TreeMap

TreeMap是基于红黑树实现的Map，可以对键进行排序。

```java
import java.util.*;

public class TreeMapDemo {
    public static void main(String[] args) {
        // 创建TreeMap（自然排序）
        Map<String, Integer> treeMap = new TreeMap<>();
        
        // 添加键值对
        treeMap.put("Banana", 5);
        treeMap.put("Apple", 10);
        treeMap.put("Orange", 8);
        treeMap.put("Grape", 15);
        System.out.println("TreeMap（自然排序）：" + treeMap);
        
        // 基本操作
        System.out.println("第一个键值对：" + treeMap.firstEntry());
        System.out.println("最后一个键值对：" + treeMap.lastEntry());
        System.out.println("小于Orange的最大键值对：" + treeMap.lowerEntry("Orange"));
        System.out.println("大于Orange的最小键值对：" + treeMap.higherEntry("Orange"));
        
        // 子Map操作
        System.out.println("A到O之间的键值对：" + treeMap.subMap("A", "O"));
        System.out.println("小于O的键值对：" + treeMap.headMap("O"));
        System.out.println("大于等于O的键值对：" + treeMap.tailMap("O"));
        
        // 数字键排序
        Map<Integer, String> numberMap = new TreeMap<>();
        numberMap.put(3, "Three");
        numberMap.put(1, "One");
        numberMap.put(4, "Four");
        numberMap.put(2, "Two");
        System.out.println("数字键排序：" + numberMap);
        
        // 自定义排序
        Map<String, Integer> customMap = new TreeMap<>((s1, s2) -> s1.length() - s2.length());
        customMap.put("Banana", 5);
        customMap.put("Apple", 10);
        customMap.put("Orange", 8);
        customMap.put("Grape", 15);
        customMap.put("Kiwi", 3);
        System.out.println("按键长度排序：" + customMap);
    }
}
```

### 6.6 Hashtable

Hashtable是线程安全的哈希表，不支持null键和值。

```java
import java.util.*;

public class HashtableDemo {
    public static void main(String[] args) {
        // 创建Hashtable
        Hashtable<String, Integer> hashtable = new Hashtable<>();
        
        // 添加键值对
        hashtable.put("Apple", 10);
        hashtable.put("Banana", 5);
        hashtable.put("Orange", 8);
        System.out.println("Hashtable：" + hashtable);
        
        // Hashtable不支持null键和值
        try {
            hashtable.put(null, 10); // 抛出NullPointerException
        } catch (NullPointerException e) {
            System.out.println("不能放入null键");
        }
        
        try {
            hashtable.put("Mango", null); // 抛出NullPointerException
        } catch (NullPointerException e) {
            System.out.println("不能放入null值");
        }
        
        // 遍历
        System.out.print("遍历Hashtable：");
        for (Map.Entry<String, Integer> entry : hashtable.entrySet()) {
            System.out.print(entry.getKey() + "=" + entry.getValue() + " ");
        }
        System.out.println();
    }
}
```

---

## 7.集合工具类

### 7.1 Collections工具类

Collections类提供了大量操作集合的静态方法。

```java
import java.util.*;

public class CollectionsDemo {
    public static void main(String[] args) {
        // 创建列表
        List<Integer> list = new ArrayList<>();
        list.add(5);
        list.add(2);
        list.add(8);
        list.add(1);
        list.add(3);
        System.out.println("原列表：" + list);
        
        // 排序
        Collections.sort(list);
        System.out.println("排序后：" + list);
        
        // 反转
        Collections.reverse(list);
        System.out.println("反转后：" + list);
        
        // 混洗
        Collections.shuffle(list);
        System.out.println("混洗后：" + list);
        
        // 查找最大最小值
        System.out.println("最大值：" + Collections.max(list));
        System.out.println("最小值：" + Collections.min(list));
        
        // 填充
        List<String> stringList = new ArrayList<>(Arrays.asList("A", "B", "C", "D"));
        Collections.fill(stringList, "X");
        System.out.println("填充后：" + stringList);
        
        // 复制
        List<String> source = Arrays.asList("1", "2", "3");
        List<String> dest = new ArrayList<>(Arrays.asList("A", "B", "C", "D", "E"));
        Collections.copy(dest, source);
        System.out.println("复制后：" + dest);
        
        // 二分查找（需要先排序）
        List<Integer> sortedList = new ArrayList<>(Arrays.asList(1, 2, 3, 5, 8));
        int index = Collections.binarySearch(sortedList, 5);
        System.out.println("二分查找5的位置：" + index);
        
        // 创建不可变集合
        List<String> immutableList = Collections.unmodifiableList(Arrays.asList("A", "B", "C"));
        System.out.println("不可变列表：" + immutableList);
        
        // 创建同步集合
        List<Integer> syncList = Collections.synchronizedList(new ArrayList<>());
        syncList.add(1);
        syncList.add(2);
        System.out.println("同步列表：" + syncList);
        
        // 创建空集合
        List<String> emptyList = Collections.emptyList();
        Set<Integer> emptySet = Collections.emptySet();
        Map<String, Integer> emptyMap = Collections.emptyMap();
        System.out.println("空列表：" + emptyList);
        System.out.println("空集合：" + emptySet);
        System.out.println("空映射：" + emptyMap);
    }
}
```

### 7.2 Arrays工具类

Arrays类提供了操作数组的静态方法。

```java
import java.util.*;

public class ArraysDemo {
    public static void main(String[] args) {
        // 创建数组
        int[] array = {5, 2, 8, 1, 3};
        System.out.println("原数组：" + Arrays.toString(array));
        
        // 排序
        Arrays.sort(array);
        System.out.println("排序后：" + Arrays.toString(array));
        
        // 查找
        int index = Arrays.binarySearch(array, 5);
        System.out.println("二分查找5的位置：" + index);
        
        // 填充
        int[] fillArray = new int[5];
        Arrays.fill(fillArray, 7);
        System.out.println("填充后：" + Arrays.toString(fillArray));
        
        // 比较
        int[] array1 = {1, 2, 3};
        int[] array2 = {1, 2, 3};
        System.out.println("数组比较：" + Arrays.equals(array1, array2));
        
        // 复制
        int[] copyArray = Arrays.copyOf(array, 10);
        System.out.println("复制数组：" + Arrays.toString(copyArray));
        
        // 转换为列表
        String[] stringArray = {"Apple", "Banana", "Orange"};
        List<String> stringList = Arrays.asList(stringArray);
        System.out.println("数组转列表：" + stringList);
        
        // 多维数组
        int[][] matrix = {{1, 2}, {3, 4}, {5, 6}};
        System.out.println("多维数组：" + Arrays.deepToString(matrix));
    }
}
```

---

## 8.并发集合

### 8.1 ConcurrentHashMap

ConcurrentHashMap是线程安全的HashMap。

```java
import java.util.concurrent.*;
import java.util.*;

public class ConcurrentHashMapDemo {
    public static void main(String[] args) {
        // 创建ConcurrentHashMap
        ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();
        
        // 添加键值对
        concurrentMap.put("Apple", 10);
        concurrentMap.put("Banana", 5);
        concurrentMap.put("Orange", 8);
        System.out.println("ConcurrentHashMap：" + concurrentMap);
        
        // 原子操作
        concurrentMap.putIfAbsent("Grape", 15);
        System.out.println("putIfAbsent后：" + concurrentMap);
        
        concurrentMap.replace("Apple", 10, 12);
        System.out.println("replace后：" + concurrentMap);
        
        // 计算操作
        concurrentMap.computeIfAbsent("Mango", key -> 7);
        System.out.println("computeIfAbsent后：" + concurrentMap);
        
        concurrentMap.computeIfPresent("Orange", (key, value) -> value + 2);
        System.out.println("computeIfPresent后：" + concurrentMap);
        
        // 并发测试
        ExecutorService executor = Executors.newFixedThreadPool(10);
        
        // 多线程同时添加元素
        for (int i = 0; i < 10; i++) {
            final int taskId = i;
            executor.submit(() -> {
                concurrentMap.put("Task" + taskId, taskId);
                System.out.println("线程" + taskId + "添加了Task" + taskId);
            });
        }
        
        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("并发操作后：" + concurrentMap);
    }
}
```

### 8.2 CopyOnWriteArrayList

CopyOnWriteArrayList是线程安全的List实现。

```java
import java.util.concurrent.*;
import java.util.*;

public class CopyOnWriteArrayListDemo {
    public static void main(String[] args) {
        // 创建CopyOnWriteArrayList
        CopyOnWriteArrayList<String> cowList = new CopyOnWriteArrayList<>();
        
        // 添加元素
        cowList.add("Apple");
        cowList.add("Banana");
        cowList.add("Orange");
        System.out.println("CopyOnWriteArrayList：" + cowList);
        
        // 并发读写测试
        ExecutorService executor = Executors.newFixedThreadPool(5);
        
        // 启动读线程
        for (int i = 0; i < 3; i++) {
            executor.submit(() -> {
                for (String fruit : cowList) {
                    System.out.println(Thread.currentThread().getName() + "读取：" + fruit);
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            });
        }
        
        // 启动写线程
        executor.submit(() -> {
            cowList.add("Grape");
            cowList.add("Mango");
            System.out.println(Thread.currentThread().getName() + "写入了新元素");
        });
        
        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("最终列表：" + cowList);
    }
}
```

---

## 9.最佳实践

### 9.1 选择合适的集合类型

1. **需要按索引访问**：使用List（ArrayList或LinkedList）
2. **不允许重复元素**：使用Set（HashSet、LinkedHashSet或TreeSet）
3. **需要键值对映射**：使用Map（HashMap、LinkedHashMap或TreeMap）
4. **需要线程安全**：使用并发集合或Collections.synchronizedXxx()
5. **需要排序**：使用TreeSet或TreeMap

### 9.2 性能考虑

1. **频繁随机访问**：使用ArrayList
2. **频繁插入删除**：使用LinkedList
3. **频繁查找**：使用HashSet
4. **需要排序**：使用TreeSet或TreeMap
5. **高并发环境**：使用并发集合

### 9.3 编程建议

```java
import java.util.*;

public class BestPracticesDemo {
    public static void main(String[] args) {
        // 1. 使用泛型避免类型转换
        List<String> stringList = new ArrayList<>();
        stringList.add("Hello");
        // 不需要类型转换
        String str = stringList.get(0);
        
        // 2. 初始化集合容量
        List<Integer> list = new ArrayList<>(1000); // 预设容量
        
        // 3. 使用增强for循环遍历
        for (String s : stringList) {
            System.out.println(s);
        }
        
        // 4. 使用isEmpty()而不是size()==0
        if (stringList.isEmpty()) {
            System.out.println("列表为空");
        }
        
        // 5. 使用contains()检查元素是否存在
        if (stringList.contains("Hello")) {
            System.out.println("包含Hello");
        }
        
        // 6. 使用迭代器删除元素
        List<Integer> numbers = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        Iterator<Integer> iterator = numbers.iterator();
        while (iterator.hasNext()) {
            if (iterator.next() % 2 == 0) {
                iterator.remove(); // 安全删除
            }
        }
        System.out.println("删除偶数后：" + numbers);
        
        // 7. 使用Collections工具类
        List<Integer> unsorted = Arrays.asList(5, 2, 8, 1, 3);
        Collections.sort(unsorted);
        System.out.println("排序后：" + unsorted);
        
        // 8. 避免在循环中重复创建集合
        List<List<String>> listOfLists = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            listOfLists.add(new ArrayList<>()); // 在循环外创建更好
        }
    }
}
```

### 9.4 常见陷阱

```java
import java.util.*;

public class CommonPitfallsDemo {
    public static void main(String[] args) {
        // 1. 错误：在遍历时修改集合
        List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
        /*
        // 错误的做法 - 会抛出ConcurrentModificationException
        for (Integer num : list) {
            if (num % 2 == 0) {
                list.remove(num); // 错误！
            }
        }
        */
        
        // 正确的做法：使用迭代器
        Iterator<Integer> iterator = list.iterator();
        while (iterator.hasNext()) {
            if (iterator.next() % 2 == 0) {
                iterator.remove();
            }
        }
        System.out.println("正确删除偶数后：" + list);
        
        // 2. 错误：使用==比较字符串
        List<String> stringList = new ArrayList<>();
        stringList.add(new String("Hello"));
        String target = new String("Hello");
        
        // 错误：使用==比较
        // System.out.println(stringList.contains(target)); // 可能返回false
        
        // 正确：使用equals比较
        boolean found = false;
        for (String s : stringList) {
            if (s.equals(target)) {
                found = true;
                break;
            }
        }
        System.out.println("正确比较结果：" + found);
        
        // 3. 错误：忘记泛型类型
        // List list = new ArrayList(); // 不推荐
        // list.add("Hello");
        // String str = (String) list.get(0); // 需要类型转换
        
        // 正确：使用泛型
        List<String> genericList = new ArrayList<>();
        genericList.add("Hello");
        String str = genericList.get(0); // 不需要类型转换
        
        // 4. 错误：修改不可变集合
        List<String> immutableList = Collections.unmodifiableList(Arrays.asList("A", "B", "C"));
        try {
            immutableList.add("D"); // 抛出UnsupportedOperationException
        } catch (UnsupportedOperationException e) {
            System.out.println("不能修改不可变集合");
        }
    }
}
```

---

## 10.总结

Java集合框架是Java编程中最重要的组成部分之一，掌握好集合框架对于编写高质量的Java程序至关重要。

### 10.1 核心要点回顾

1. **Collection接口**：所有集合的根接口
2. **List接口**：有序集合，允许重复元素
3. **Set接口**：不允许重复元素的集合
4. **Queue接口**：队列接口，支持FIFO操作
5. **Map接口**：键值对映射接口

### 10.2 实现类选择指南

| 接口 | 常用实现类 | 特点 | 适用场景 |
|------|------------|------|----------|
| List | ArrayList | 动态数组，随机访问快 | 频繁随机访问 |
| List | LinkedList | 双向链表，插入删除快 | 频繁插入删除 |
| Set | HashSet | 哈希表，查找快 | 快速查找，不允许重复 |
| Set | LinkedHashSet | 保持插入顺序 | 需要保持插入顺序 |
| Set | TreeSet | 红黑树，自动排序 | 需要排序 |
| Map | HashMap | 哈希表，查找快 | 快速键值对查找 |
| Map | LinkedHashMap | 保持插入顺序 | 需要保持插入顺序 |
| Map | TreeMap | 红黑树，按键排序 | 需要按键排序 |

### 10.3 学习建议

1. **理解概念**：深入理解每种集合的特点和适用场景
2. **动手实践**：通过编写代码来掌握各种集合的使用方法
3. **性能分析**：了解不同集合的时间复杂度和空间复杂度
4. **最佳实践**：遵循Java集合框架的最佳实践
5. **并发安全**：在多线程环境中选择合适的并发集合

通过本章的学习，你应该能够：
- 理解Java集合框架的整体架构
- 掌握各种集合接口和实现类的使用方法
- 根据实际需求选择合适的集合类型
- 编写高效、安全的集合操作代码
- 避免常见的集合使用陷阱

在后续章节中，我们将继续学习Java的其他重要特性，包括异常处理、输入输出、多线程编程等。