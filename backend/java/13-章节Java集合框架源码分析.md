# 第13章 Java集合框架源码分析

## 本章概述

Java集合框架是Java语言中最常用的API之一，也是Java程序员必须深入理解的核心组件。本章将从源码层面深入分析Java集合框架的设计思想和实现原理，包括List、Set、Map等核心接口及其主要实现类，帮助读者更好地理解和使用这些集合类。

## 目录

1. [集合框架概述](#集合框架概述)
2. [ArrayList源码分析](#arraylist源码分析)
3. [LinkedList源码分析](#linkedlist源码分析)
4. [HashMap源码分析](#hashmap源码分析)
5. [ConcurrentHashMap源码分析](#concurrenthashmap源码分析)
6. [HashSet与TreeSet源码分析](#hashset与treeset源码分析)
7. [设计模式在集合框架中的应用](#设计模式在集合框架中的应用)
8. [性能优化与最佳实践](#性能优化与最佳实践)
9. [实践案例](#实践案例)

## 集合框架概述

Java集合框架包含了一系列接口和实现类，提供了存储和操作对象组的统一方式。主要接口包括：

- Collection：集合层次结构的根接口
- List：有序集合，允许重复元素
- Set：不允许重复元素的集合
- Map：键值对映射，不继承Collection接口

### 核心设计原则

1. **接口与实现分离**：通过接口定义行为，具体实现提供不同特性
2. **算法复用**：Collections工具类提供通用算法
3. **性能权衡**：不同的实现类针对不同场景进行优化

## ArrayList源码分析

ArrayList是最常用的List实现类，底层基于动态数组实现。

### 数据结构

```java
public class ArrayList<E> extends AbstractList<E>
        implements List<E>, RandomAccess, Cloneable, java.io.Serializable {
    // 默认初始容量
    private static final int DEFAULT_CAPACITY = 10;
    
    // 空数组实例
    private static final Object[] EMPTY_ELEMENTDATA = {};
    
    // 默认容量的空数组实例
    private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
    
    // 存储元素的数组
    transient Object[] elementData;
    
    // 集合大小
    private int size;
}
```

### 扩容机制

```java
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    // 扩容为原来的1.5倍
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    // 复制数组
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

### 关键方法分析

#### add方法
```java
public boolean add(E e) {
    // 确保容量足够
    ensureCapacityInternal(size + 1);
    // 添加元素
    elementData[size++] = e;
    return true;
}
```

#### get方法
```java
public E get(int index) {
    // 检查索引范围
    rangeCheck(index);
    // 直接通过数组下标访问
    return elementData(index);
}
```

#### remove方法
```java
public E remove(int index) {
    rangeCheck(index);
    
    modCount++;
    E oldValue = elementData(index);
    
    int numMoved = size - index - 1;
    if (numMoved > 0)
        // 数组拷贝移动元素
        System.arraycopy(elementData, index+1, elementData, index, numMoved);
    elementData[--size] = null; // 清除引用，帮助GC
    
    return oldValue;
}
```

### 特性总结

1. **优点**：随机访问快，尾部插入删除效率高
2. **缺点**：中间插入删除需要移动大量元素
3. **适用场景**：频繁读取、尾部操作的场景

## LinkedList源码分析

LinkedList是基于双向链表实现的List，同时也实现了Deque接口。

### 数据结构

```java
public class LinkedList<E>
    extends AbstractSequentialList<E>
    implements List<E>, Deque<E>, Cloneable, java.io.Serializable {
    
    // 链表大小
    transient int size = 0;
    
    // 头节点
    transient Node<E> first;
    
    // 尾节点
    transient Node<E> last;
    
    // 节点内部类
    private static class Node<E> {
        E item;
        Node<E> next;
        Node<E> prev;
        
        Node(Node<E> prev, E element, Node<E> next) {
            this.item = element;
            this.next = next;
            this.prev = prev;
        }
    }
}
```

### 关键方法分析

#### add方法
```java
public boolean add(E e) {
    linkLast(e);
    return true;
}

void linkLast(E e) {
    final Node<E> l = last;
    final Node<E> newNode = new Node<>(l, e, null);
    last = newNode;
    if (l == null)
        first = newNode;
    else
        l.next = newNode;
    size++;
    modCount++;
}
```

#### get方法
```java
public E get(int index) {
    checkElementIndex(index);
    return node(index).item;
}

Node<E> node(int index) {
    // 根据索引位置决定从前还是从后遍历
    if (index < (size >> 1)) {
        Node<E> x = first;
        for (int i = 0; i < index; i++)
            x = x.next;
        return x;
    } else {
        Node<E> x = last;
        for (int i = size - 1; i > index; i--)
            x = x.prev;
        return x;
    }
}
```

#### remove方法
```java
public E remove(int index) {
    checkElementIndex(index);
    return unlink(node(index));
}

E unlink(Node<E> x) {
    final E element = x.item;
    final Node<E> next = x.next;
    final Node<E> prev = x.prev;
    
    if (prev == null) {
        first = next;
    } else {
        prev.next = next;
        x.prev = null;
    }
    
    if (next == null) {
        last = prev;
    } else {
        next.prev = prev;
        x.next = null;
    }
    
    x.item = null;
    size--;
    modCount++;
    return element;
}
```

### 特性总结

1. **优点**：插入删除效率高，不需要移动元素
2. **缺点**：随机访问慢，需要遍历链表
3. **适用场景**：频繁插入删除、不需要随机访问的场景

## HashMap源码分析

HashMap是Java中最常用的Map实现类，基于哈希表实现。

### 数据结构

在Java 8之前，HashMap采用数组+链表的方式实现；Java 8及以后，当链表长度超过阈值时会转换为红黑树。

```java
public class HashMap<K,V> extends AbstractMap<K,V>
    implements Map<K,V>, Cloneable, Serializable {
    
    // 默认初始容量
    static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; // 16
    
    // 最大容量
    static final int MAXIMUM_CAPACITY = 1 << 30;
    
    // 默认负载因子
    static final float DEFAULT_LOAD_FACTOR = 0.75f;
    
    // 链表转红黑树的阈值
    static final int TREEIFY_THRESHOLD = 8;
    
    // 红黑树转链表的阈值
    static final int UNTREEIFY_THRESHOLD = 6;
    
    // 转换为红黑树的最小容量
    static final int MIN_TREEIFY_CAPACITY = 64;
    
    // 存储节点的数组
    transient Node<K,V>[] table;
    
    // 键值对数量
    transient int size;
    
    // 扩容阈值
    int threshold;
    
    // 负载因子
    final float loadFactor;
    
    // 节点内部类
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;
        
        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
        
        public final K getKey()        { return key; }
        public final V getValue()      { return value; }
        public final String toString() { return key + "=" + value; }
        
        public final int hashCode() {
            return Objects.hashCode(key) ^ Objects.hashCode(value);
        }
        
        public final V setValue(V newValue) {
            V oldValue = value;
            value = newValue;
            return oldValue;
        }
    }
}
```

### 哈希函数

```java
static final int hash(Object key) {
    int h;
    // 高低位异或，减少哈希冲突
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

### put方法分析

```java
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}

final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
               boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    // 初始化数组
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    // 计算索引，如果桶为空则直接放入
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        // 如果第一个节点就是目标节点
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        // 如果是红黑树节点
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {
            // 遍历链表
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    // 插入新节点
                    p.next = newNode(hash, key, value, null);
                    // 如果链表长度超过阈值，转换为红黑树
                    if (binCount >= TREEIFY_THRESHOLD - 1)
                        treeifyBin(tab, hash);
                    break;
                }
                // 如果找到相同的key
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
        // 如果找到了相同的key，更新value
        if (e != null) {
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
            afterNodeAccess(e);
            return oldValue;
        }
    }
    ++modCount;
    // 如果元素数量超过阈值，扩容
    if (++size > threshold)
        resize();
    afterNodeInsertion(evict);
    return null;
}
```

### get方法分析

```java
public V get(Object key) {
    Node<K,V> e;
    return (e = getNode(hash(key), key)) == null ? null : e.value;
}

final Node<K,V> getNode(int hash, Object key) {
    Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (first = tab[(n - 1) & hash]) != null) {
        // 检查第一个节点
        if (first.hash == hash &&
            ((k = first.key) == key || (key != null && key.equals(k))))
            return first;
        // 遍历链表或红黑树
        if ((e = first.next) != null) {
            if (first instanceof TreeNode)
                return ((TreeNode<K,V>)first).getTreeNode(hash, key);
            do {
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    return e;
            } while ((e = e.next) != null);
        }
    }
    return null;
}
```

### resize方法分析

```java
final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;
    
    if (oldCap > 0) {
        // 如果原容量达到最大值，不再扩容
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        // 容量翻倍
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                 oldCap >= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr << 1; // 阈值也翻倍
    }
    else if (oldThr > 0)
        newCap = oldThr;
    else {
        // 使用默认值初始化
        newCap = DEFAULT_INITIAL_CAPACITY;
        newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
    }
    
    if (newThr == 0) {
        float ft = (float)newCap * loadFactor;
        newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                  (int)ft : Integer.MAX_VALUE);
    }
    threshold = newThr;
    
    // 创建新数组
    @SuppressWarnings({"rawtypes","unchecked"})
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    table = newTab;
    
    // 迁移数据
    if (oldTab != null) {
        for (int j = 0; j < oldCap; ++j) {
            Node<K,V> e;
            if ((e = oldTab[j]) != null) {
                oldTab[j] = null;
                // 如果只有一个节点，直接迁移
                if (e.next == null)
                    newTab[e.hash & (newCap - 1)] = e;
                // 如果是红黑树节点
                else if (e instanceof TreeNode)
                    ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                else {
                    // 链表节点迁移
                    Node<K,V> loHead = null, loTail = null;
                    Node<K,V> hiHead = null, hiTail = null;
                    Node<K,V> next;
                    do {
                        next = e.next;
                        // 根据hash值决定节点在新数组中的位置
                        if ((e.hash & oldCap) == 0) {
                            if (loTail == null)
                                loHead = e;
                            else
                                loTail.next = e;
                            loTail = e;
                        }
                        else {
                            if (hiTail == null)
                                hiHead = e;
                            else
                                hiTail.next = e;
                            hiTail = e;
                        }
                    } while ((e = next) != null);
                    
                    // 放置低链表
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;
                    }
                    // 放置高链表
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;
                    }
                }
            }
        }
    }
    return newTab;
}
```

### 特性总结

1. **优点**：查询、插入、删除平均时间复杂度为O(1)
2. **缺点**：哈希冲突会影响性能，扩容时需要重新哈希
3. **适用场景**：快速查找、插入、删除的场景

## ConcurrentHashMap源码分析

ConcurrentHashMap是线程安全的HashMap实现，在Java 8中进行了重大改进。

### 数据结构

ConcurrentHashMap采用了与HashMap类似的结构，但在并发控制上做了很多优化。

```java
public class ConcurrentHashMap<K,V> extends AbstractMap<K,V>
    implements ConcurrentMap<K,V>, Serializable {
    
    // 节点类型
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        volatile V val;
        volatile Node<K,V> next;
        // ... 其他方法
    }
    
    // 转换为红黑树的节点
    static final class TreeNode<K,V> extends Node<K,V> {
        TreeNode<K,V> parent;
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;
        boolean red;
        // ... 其他方法
    }
    
    // 转换为红黑树的表头节点
    static final class TreeBin<K,V> extends Node<K,V> {
        TreeNode<K,V> root;
        volatile TreeNode<K,V> first;
        volatile Thread waiter;
        volatile int lockState;
        // ... 其他方法
    }
}
```

### CAS操作与synchronized结合

ConcurrentHashMap使用CAS操作和synchronized关键字相结合的方式来保证线程安全：

```java
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());
    int binCount = 0;
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            // 使用CAS操作插入节点
            if (casTabAt(tab, i, null,
                         new Node<K,V>(hash, key, value, null)))
                break;
        }
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);
        else {
            V oldVal = null;
            // 使用synchronized锁定头节点
            synchronized (f) {
                if (tabAt(tab, i) == f) {
                    if (fh >= 0) {
                        binCount = 1;
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            if (e.hash == hash &&
                                ((ek = e.key) == key ||
                                 (ek != null && key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            Node<K,V> pred = e;
                            if ((e = e.next) == null) {
                                pred.next = new Node<K,V>(hash, key,
                                                          value, null);
                                break;
                            }
                        }
                    }
                    else if (f instanceof TreeBin) {
                        Node<K,V> p;
                        binCount = 2;
                        if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key,
                                                              value)) != null) {
                            oldVal = p.val;
                            if (!onlyIfAbsent)
                                p.val = value;
                        }
                    }
                }
            }
            if (binCount != 0) {
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);
    return null;
}
```

### 特性总结

1. **优点**：线程安全，高性能，支持高并发
2. **缺点**：相比HashMap稍复杂，内存占用略高
3. **适用场景**：多线程环境下需要高性能的Map操作

## HashSet与TreeSet源码分析

### HashSet

HashSet是基于HashMap实现的Set接口，不允许重复元素。

```java
public class HashSet<E>
    extends AbstractSet<E>
    implements Set<E>, Cloneable, java.io.Serializable {
    
    // 内部使用HashMap存储元素
    private transient HashMap<E,Object> map;
    
    // 虚拟值，用于填充HashMap的value
    private static final Object PRESENT = new Object();
    
    public HashSet() {
        map = new HashMap<>();
    }
    
    public boolean add(E e) {
        // 将元素作为key存入HashMap，value为PRESENT
        return map.put(e, PRESENT)==null;
    }
    
    public boolean contains(Object o) {
        return map.containsKey(o);
    }
    
    public boolean remove(Object o) {
        return map.remove(o)==PRESENT;
    }
}
```

### TreeSet

TreeSet是基于TreeMap实现的有序Set，元素按照自然顺序或自定义比较器排序。

```java
public class TreeSet<E> extends AbstractSet<E>
    implements NavigableSet<E>, Cloneable, java.io.Serializable {
    
    // 内部使用TreeMap存储元素
    private transient NavigableMap<E,Object> m;
    
    // 虚拟值
    private static final Object PRESENT = new Object();
    
    public TreeSet() {
        this(new TreeMap<E,Object>());
    }
    
    TreeSet(NavigableMap<E,Object> m) {
        this.m = m;
    }
    
    public boolean add(E e) {
        return m.put(e, PRESENT)==null;
    }
    
    public boolean remove(Object o) {
        return m.remove(o)==PRESENT;
    }
}
```

## 设计模式在集合框架中的应用

### 迭代器模式

集合框架广泛使用迭代器模式，提供统一的遍历接口。

```java
public interface Iterator<E> {
    boolean hasNext();
    E next();
    default void remove() {
        throw new UnsupportedOperationException("remove");
    }
}

// ArrayList的迭代器实现
private class Itr implements Iterator<E> {
    int cursor;
    int lastRet = -1;
    int expectedModCount = modCount;
    
    public boolean hasNext() {
        return cursor != size;
    }
    
    @SuppressWarnings("unchecked")
    public E next() {
        checkForComodification();
        int i = cursor;
        if (i >= size)
            throw new NoSuchElementException();
        Object[] elementData = ArrayList.this.elementData;
        if (i >= elementData.length)
            throw new ConcurrentModificationException();
        cursor = i + 1;
        return (E) elementData[lastRet = i];
    }
}
```

### 适配器模式

Collections工具类中的很多方法使用了适配器模式，将一种类型的集合转换为另一种类型。

```java
// 将List转换为不可修改的List
public static <T> List<T> unmodifiableList(List<? extends T> list) {
    return (list instanceof RandomAccess ?
            new UnmodifiableRandomAccessList<>(list) :
            new UnmodifiableList<>(list));
}
```

### 装饰器模式

Collections工具类提供了多种装饰器方法，为集合增加额外的功能。

```java
// 同步包装器
public static <T> Collection<T> synchronizedCollection(Collection<T> c) {
    return new SynchronizedCollection<>(c);
}

// 只读包装器
public static <T> Collection<T> unmodifiableCollection(Collection<? extends T> c) {
    return new UnmodifiableCollection<>(c);
}
```

## 性能优化与最佳实践

### 选择合适的集合类型

1. **频繁随机访问**：使用ArrayList
2. **频繁插入删除**：使用LinkedList
3. **唯一性要求**：使用HashSet
4. **排序要求**：使用TreeSet
5. **键值对存储**：使用HashMap
6. **线程安全要求**：使用ConcurrentHashMap

### 合理设置初始容量

```java
// 如果大致知道元素数量，设置合理的初始容量避免频繁扩容
List<String> list = new ArrayList<>(1000);
Map<String, Integer> map = new HashMap<>(512);
```

### 使用增强for循环

```java
// 推荐：增强for循环
for (String item : list) {
    // 处理元素
}

// 不推荐：传统for循环（对于LinkedList性能较差）
for (int i = 0; i < list.size(); i++) {
    String item = list.get(i);
    // 处理元素
}
```

### 避免在循环中删除元素

```java
// 错误的做法
for (String item : list) {
    if (shouldRemove(item)) {
        list.remove(item); // 可能抛出ConcurrentModificationException
    }
}

// 正确的做法
Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String item = iterator.next();
    if (shouldRemove(item)) {
        iterator.remove();
    }
}
```

## 实践案例

### 案例1：高效的去重统计

```java
public class EfficientDeduplication {
    /**
     * 统计用户访问次数，去重并记录访问时间
     */
    public static Map<String, UserVisitInfo> deduplicateAndCount(List<UserVisitRecord> records) {
        // 使用LinkedHashMap保持插入顺序
        Map<String, UserVisitInfo> userVisits = new LinkedHashMap<>();
        
        for (UserVisitRecord record : records) {
            String userId = record.getUserId();
            UserVisitInfo info = userVisits.get(userId);
            
            if (info == null) {
                info = new UserVisitInfo(userId);
                userVisits.put(userId, info);
            }
            
            info.incrementVisitCount();
            info.updateLastVisitTime(record.getVisitTime());
        }
        
        return userVisits;
    }
    
    static class UserVisitRecord {
        private String userId;
        private long visitTime;
        
        // 构造函数、getter和setter方法
        public UserVisitRecord(String userId, long visitTime) {
            this.userId = userId;
            this.visitTime = visitTime;
        }
        
        public String getUserId() { return userId; }
        public long getVisitTime() { return visitTime; }
    }
    
    static class UserVisitInfo {
        private String userId;
        private int visitCount;
        private long lastVisitTime;
        
        public UserVisitInfo(String userId) {
            this.userId = userId;
            this.visitCount = 0;
            this.lastVisitTime = 0;
        }
        
        public void incrementVisitCount() {
            this.visitCount++;
        }
        
        public void updateLastVisitTime(long visitTime) {
            if (visitTime > this.lastVisitTime) {
                this.lastVisitTime = visitTime;
            }
        }
        
        // getter方法
        public String getUserId() { return userId; }
        public int getVisitCount() { return visitCount; }
        public long getLastVisitTime() { return lastVisitTime; }
    }
}
```

### 案例2：线程安全的缓存实现

```java
public class ThreadSafeCache<K, V> {
    private final ConcurrentHashMap<K, CacheEntry<V>> cache;
    private final int maxSize;
    private final long expireTimeMillis;
    
    public ThreadSafeCache(int maxSize, long expireTimeSeconds) {
        this.cache = new ConcurrentHashMap<>();
        this.maxSize = maxSize;
        this.expireTimeMillis = expireTimeSeconds * 1000;
    }
    
    public V get(K key) {
        CacheEntry<V> entry = cache.get(key);
        if (entry == null) {
            return null;
        }
        
        // 检查是否过期
        if (System.currentTimeMillis() - entry.getCreateTime() > expireTimeMillis) {
            cache.remove(key);
            return null;
        }
        
        return entry.getValue();
    }
    
    public void put(K key, V value) {
        // 检查缓存大小，如果超过限制则清除最旧的条目
        if (cache.size() >= maxSize) {
            clearExpiredEntries();
            if (cache.size() >= maxSize) {
                removeOldestEntry();
            }
        }
        
        cache.put(key, new CacheEntry<>(value, System.currentTimeMillis()));
    }
    
    private void clearExpiredEntries() {
        long currentTime = System.currentTimeMillis();
        cache.entrySet().removeIf(entry -> 
            currentTime - entry.getValue().getCreateTime() > expireTimeMillis);
    }
    
    private void removeOldestEntry() {
        // 找到最旧的条目并删除
        Optional<Map.Entry<K, CacheEntry<V>>> oldest = cache.entrySet()
            .stream()
            .min(Comparator.comparingLong(e -> e.getValue().getCreateTime()));
        
        oldest.ifPresent(entry -> cache.remove(entry.getKey()));
    }
    
    static class CacheEntry<V> {
        private final V value;
        private final long createTime;
        
        public CacheEntry(V value, long createTime) {
            this.value = value;
            this.createTime = createTime;
        }
        
        public V getValue() { return value; }
        public long getCreateTime() { return createTime; }
    }
}
```

## 总结

通过对Java集合框架源码的深入分析，我们可以看到：

1. **设计精妙**：集合框架体现了良好的面向对象设计原则，接口与实现分离，提供了丰富的扩展点。

2. **性能优化**：各种集合类都有针对性的性能优化，如ArrayList的动态扩容、HashMap的哈希函数优化、ConcurrentHashMap的并发控制等。

3. **适用场景明确**：不同的集合类适用于不同的场景，正确选择集合类对程序性能至关重要。

4. **线程安全考虑**：从早期的Vector和Hashtable到现在的ConcurrentHashMap，Java在并发控制方面不断演进，提供了更好的性能和更细粒度的锁控制。

5. **设计模式应用**：集合框架中广泛应用了迭代器模式、适配器模式、装饰器模式等设计模式，提高了代码的可扩展性和可维护性。

在实际开发中，我们应该：
- 深入理解各种集合类的特点和适用场景
- 根据实际需求选择合适的集合类
- 注意线程安全问题，特别是在并发环境中
- 合理设置初始容量，避免频繁扩容
- 利用Collections工具类提供的便捷方法
- 在性能敏感的场景中，考虑使用专门的并发集合类

通过深入理解集合框架的源码实现，我们不仅能更好地使用这些工具，还能在遇到性能问题时快速定位原因并找到解决方案。