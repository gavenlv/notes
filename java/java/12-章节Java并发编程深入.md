# 第12章 Java并发编程深入

## 本章概述

并发编程是Java语言的重要特性之一，也是Java高级工程师必须掌握的核心技能。本章将深入探讨Java并发编程的高级主题，包括线程池、并发集合、原子类、显式锁、并发工具类等内容，帮助读者深入理解并发编程的原理和最佳实践。

## 目录

1. [线程池详解](#线程池详解)
2. [并发集合框架](#并发集合框架)
3. [原子类与无锁编程](#原子类与无锁编程)
4. [显式锁机制](#显式锁机制)
5. [并发工具类](#并发工具类)
6. [并发设计模式](#并发设计模式)
7. [性能优化与最佳实践](#性能优化与最佳实践)
8. [常见并发问题及解决方案](#常见并发问题及解决方案)
9. [实践案例](#实践案例)

## 线程池详解

线程池是并发编程中的重要概念，它能够有效管理线程资源，避免频繁创建和销毁线程带来的性能开销。

### 线程池的核心概念

线程池通过复用已创建的线程来执行任务，主要解决了以下问题：
1. 线程生命周期开销：线程的创建和销毁需要时间
2. 资源消耗：每个线程都会占用一定的内存和其他资源
3. 稳定性：过多的线程可能导致系统不稳定

### ThreadPoolExecutor详解

ThreadPoolExecutor是Java线程池的核心实现类，其构造函数包含以下核心参数：

```java
public ThreadPoolExecutor(int corePoolSize,
                          int maximumPoolSize,
                          long keepAliveTime,
                          TimeUnit unit,
                          BlockingQueue<Runnable> workQueue,
                          ThreadFactory threadFactory,
                          RejectedExecutionHandler handler)
```

#### 参数说明

- corePoolSize：核心线程数
- maximumPoolSize：最大线程数
- keepAliveTime：空闲线程存活时间
- unit：keepAliveTime的时间单位
- workQueue：工作队列
- threadFactory：线程工厂
- handler：拒绝策略

### 线程池的工作流程

1. 如果当前运行的线程少于corePoolSize，则创建新线程来执行任务
2. 如果运行的线程等于或多于corePoolSize，则将任务加入BlockingQueue
3. 如果BlockingQueue已满，则创建新的线程来处理任务
4. 如果创建的线程数量超过maximumPoolSize，则执行拒绝策略

### 常见的线程池类型

#### FixedThreadPool
固定大小的线程池，适用于负载较重、长时间运行的应用。

```java
ExecutorService executor = Executors.newFixedThreadPool(4);
```

#### CachedThreadPool
可根据需要创建新线程的线程池，适用于执行大量短期异步任务的程序。

```java
ExecutorService executor = Executors.newCachedThreadPool();
```

#### SingleThreadExecutor
单线程的Executor，确保所有任务都在同一个线程中按顺序执行。

```java
ExecutorService executor = Executors.newSingleThreadExecutor();
```

#### ScheduledThreadPool
支持定时及周期性任务执行的线程池。

```java
ScheduledExecutorService executor = Executors.newScheduledThreadPool(4);
```

### 线程池的拒绝策略

1. **AbortPolicy**：直接抛出RejectedExecutionException异常
2. **CallerRunsPolicy**：由调用线程处理该任务
3. **DiscardPolicy**：直接丢弃任务
4. **DiscardOldestPolicy**：丢弃队列中最老的任务，然后重新提交被拒绝的任务

## 并发集合框架

Java并发包（java.util.concurrent）提供了丰富的并发集合类，它们在多线程环境下具有更好的性能和安全性。

### ConcurrentHashMap

ConcurrentHashMap是线程安全的HashMap实现，它通过分段锁或CAS操作来保证线程安全。

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("key1", 1);
Integer value = map.get("key1");
```

### CopyOnWriteArrayList

CopyOnWriteArrayList是线程安全的List实现，适用于读多写少的场景。

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("item1");
String item = list.get(0);
```

### BlockingQueue

BlockingQueue是一个支持阻塞操作的队列接口，常用于生产者-消费者模式。

```java
// ArrayBlockingQueue
BlockingQueue<String> queue = new ArrayBlockingQueue<>(10);

// 生产者
queue.put("item");

// 消费者
String item = queue.take();
```

### ConcurrentLinkedQueue

ConcurrentLinkedQueue是一个基于链表的无界线程安全队列，采用非阻塞算法实现。

```java
ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("item");
String item = queue.poll();
```

## 原子类与无锁编程

原子类（Atomic Classes）提供了原子操作，避免了使用锁带来的性能开销。

### 基本类型原子类

#### AtomicInteger
```java
AtomicInteger atomicInt = new AtomicInteger(0);
int newValue = atomicInt.incrementAndGet();
```

#### AtomicLong
```java
AtomicLong atomicLong = new AtomicLong(0L);
long newValue = atomicLong.incrementAndGet();
```

#### AtomicBoolean
```java
AtomicBoolean atomicBoolean = new AtomicBoolean(false);
boolean newValue = atomicBoolean.compareAndSet(false, true);
```

### 引用类型原子类

#### AtomicReference
```java
AtomicReference<String> atomicRef = new AtomicReference<>("initial");
String newValue = atomicRef.getAndSet("new");
```

#### AtomicReferenceFieldUpdater
```java
public class Node {
    private volatile String value;
    private static final AtomicReferenceFieldUpdater<Node, String> valueUpdater =
        AtomicReferenceFieldUpdater.newUpdater(Node.class, String.class, "value");
    
    public void updateValue(String newValue) {
        valueUpdater.compareAndSet(this, null, newValue);
    }
}
```

### 字段更新器

#### AtomicIntegerFieldUpdater
```java
public class Counter {
    volatile int count;
    private static final AtomicIntegerFieldUpdater<Counter> countUpdater =
        AtomicIntegerFieldUpdater.newUpdater(Counter.class, "count");
    
    public void increment() {
        countUpdater.incrementAndGet(this);
    }
}
```

## 显式锁机制

Java 5引入了java.util.concurrent.locks包，提供了比synchronized更灵活的锁机制。

### ReentrantLock

ReentrantLock是一个可重入的互斥锁，提供了比synchronized更丰富的功能。

```java
ReentrantLock lock = new ReentrantLock();

// 获取锁
lock.lock();
try {
    // 临界区代码
} finally {
    // 释放锁
    lock.unlock();
}
```

#### 公平锁与非公平锁
```java
// 公平锁
ReentrantLock fairLock = new ReentrantLock(true);

// 非公平锁
ReentrantLock nonFairLock = new ReentrantLock(false);
```

#### 条件变量
```java
ReentrantLock lock = new ReentrantLock();
Condition condition = lock.newCondition();

// 等待
lock.lock();
try {
    while (!conditionMet) {
        condition.await();
    }
} finally {
    lock.unlock();
}

// 通知
lock.lock();
try {
    conditionMet = true;
    condition.signalAll();
} finally {
    lock.unlock();
}
```

### ReadWriteLock

ReadWriteLock维护了一对相关的锁，一个用于只读操作，一个用于写入操作。

```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();
Lock readLock = rwLock.readLock();
Lock writeLock = rwLock.writeLock();

// 读操作
readLock.lock();
try {
    // 读取数据
} finally {
    readLock.unlock();
}

// 写操作
writeLock.lock();
try {
    // 修改数据
} finally {
    writeLock.unlock();
}
```

### StampedLock

StampedLock是Java 8引入的新的锁机制，支持乐观读锁，性能优于ReadWriteLock。

```java
StampedLock stampedLock = new StampedLock();

// 乐观读
long stamp = stampedLock.tryOptimisticRead();
// 读取数据
if (!stampedLock.validate(stamp)) {
    // 升级为悲观读锁
    stamp = stampedLock.readLock();
    try {
        // 重新读取数据
    } finally {
        stampedLock.unlockRead(stamp);
    }
}
```

## 并发工具类

Java并发包提供了丰富的工具类，用于解决常见的并发问题。

### CountDownLatch

CountDownLatch允许一个或多个线程等待其他线程完成操作。

```java
CountDownLatch latch = new CountDownLatch(3);

// 工作线程
Thread worker1 = new Thread(() -> {
    // 执行任务
    latch.countDown();
});

// 等待线程
latch.await(); // 等待计数器归零
```

### CyclicBarrier

CyclicBarrier用于让一组线程等待彼此到达一个共同的屏障点。

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    // 所有线程都到达屏障点后执行的代码
});

Thread thread1 = new Thread(() -> {
    // 执行任务
    barrier.await(); // 等待其他线程
});
```

### Semaphore

Semaphore用于控制同时访问特定资源的线程数量。

```java
Semaphore semaphore = new Semaphore(2); // 允许2个线程同时访问

semaphore.acquire(); // 获取许可
try {
    // 访问资源
} finally {
    semaphore.release(); // 释放许可
}
```

### Phaser

Phaser是Java 7引入的更灵活的同步屏障，支持动态注册和注销参与者。

```java
Phaser phaser = new Phaser(3); // 3个参与者

Thread thread1 = new Thread(() -> {
    // 执行第一阶段任务
    phaser.arriveAndAwaitAdvance(); // 到达并等待其他线程
    
    // 执行第二阶段任务
    phaser.arriveAndAwaitAdvance(); // 到达并等待其他线程
});
```

## 并发设计模式

并发设计模式是解决并发问题的经典解决方案。

### 生产者-消费者模式

```java
public class ProducerConsumerExample {
    private final BlockingQueue<String> queue = new ArrayBlockingQueue<>(10);
    
    class Producer implements Runnable {
        @Override
        public void run() {
            try {
                for (int i = 0; i < 100; i++) {
                    queue.put("item" + i);
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    class Consumer implements Runnable {
        @Override
        public void run() {
            try {
                while (true) {
                    String item = queue.take();
                    System.out.println("Consumed: " + item);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
```

### Future模式

```java
ExecutorService executor = Executors.newFixedThreadPool(4);
Future<String> future = executor.submit(() -> {
    // 执行耗时操作
    Thread.sleep(1000);
    return "result";
});

// 获取结果
try {
    String result = future.get(5, TimeUnit.SECONDS);
    System.out.println(result);
} catch (TimeoutException e) {
    future.cancel(true);
}
```

### Fork/Join模式

```java
public class ForkJoinExample extends RecursiveTask<Integer> {
    private final int[] array;
    private final int start;
    private final int end;
    
    public ForkJoinExample(int[] array, int start, int end) {
        this.array = array;
        this.start = start;
        this.end = end;
    }
    
    @Override
    protected Integer compute() {
        if (end - start <= 10) {
            // 直接计算
            int sum = 0;
            for (int i = start; i < end; i++) {
                sum += array[i];
            }
            return sum;
        } else {
            // 分割任务
            int mid = (start + end) / 2;
            ForkJoinExample leftTask = new ForkJoinExample(array, start, mid);
            ForkJoinExample rightTask = new ForkJoinExample(array, mid, end);
            
            leftTask.fork();
            rightTask.fork();
            
            return leftTask.join() + rightTask.join();
        }
    }
}
```

## 性能优化与最佳实践

### 线程池配置优化

1. **合理设置核心线程数**：根据CPU核心数和任务类型确定
2. **选择合适的队列**：ArrayBlockingQueue、LinkedBlockingQueue或SynchronousQueue
3. **设置适当的拒绝策略**：根据业务需求选择合适的拒绝策略

### 减少锁竞争

1. **缩小锁的范围**：只在必要时加锁
2. **使用读写锁**：读多写少的场景使用读写锁
3. **使用无锁数据结构**：如ConcurrentHashMap、AtomicInteger等

### 避免死锁

1. **按固定顺序获取锁**：所有线程以相同顺序获取锁
2. **使用超时机制**：tryLock方法避免无限等待
3. **避免嵌套锁**：尽量减少锁的嵌套使用

## 常见并发问题及解决方案

### 线程安全问题

#### 问题描述
多个线程同时访问共享资源时可能出现数据不一致的问题。

#### 解决方案
1. 使用synchronized关键字
2. 使用显式锁（ReentrantLock等）
3. 使用原子类（AtomicInteger等）
4. 使用线程安全的集合类（ConcurrentHashMap等）

### 死锁问题

#### 问题描述
两个或多个线程互相等待对方释放锁，导致所有线程都无法继续执行。

#### 解决方案
1. 按固定顺序获取锁
2. 使用超时机制
3. 使用死锁检测工具

### 活锁问题

#### 问题描述
线程不断尝试解决冲突，但始终无法取得进展。

#### 解决方案
1. 引入随机性
2. 使用回退机制

### 饥饿问题

#### 问题描述
某些线程因为资源总是被其他线程抢占而无法执行。

#### 解决方案
1. 使用公平锁
2. 合理分配资源

## 实践案例

### 案例1：高并发订单处理系统

#### 需求分析
设计一个能够处理高并发订单的系统，要求：
1. 支持每秒处理10000+订单
2. 保证订单处理的原子性
3. 防止重复处理同一订单

#### 设计方案
```java
public class OrderProcessor {
    private final ExecutorService executor = 
        new ThreadPoolExecutor(
            50,  // 核心线程数
            100, // 最大线程数
            60L, // 空闲线程存活时间
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(1000), // 工作队列
            new ThreadFactory() {
                private final AtomicInteger threadNumber = new AtomicInteger(1);
                @Override
                public Thread newThread(Runnable r) {
                    Thread t = new Thread(r, "OrderProcessor-" + threadNumber.getAndIncrement());
                    t.setDaemon(false);
                    return t;
                }
            },
            new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
        );
    
    private final ConcurrentHashMap<String, Boolean> processedOrders = new ConcurrentHashMap<>();
    
    public void processOrder(Order order) {
        // 防止重复处理
        if (processedOrders.putIfAbsent(order.getId(), Boolean.TRUE) != null) {
            return; // 订单已处理
        }
        
        executor.submit(() -> {
            try {
                // 处理订单逻辑
                doProcessOrder(order);
            } catch (Exception e) {
                // 记录错误日志
                System.err.println("Error processing order: " + order.getId() + ", error: " + e.getMessage());
                // 移除处理标记，允许重试
                processedOrders.remove(order.getId());
            }
        });
    }
    
    private void doProcessOrder(Order order) {
        // 模拟订单处理
        System.out.println("Processing order: " + order.getId());
        try {
            Thread.sleep(100); // 模拟处理时间
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        System.out.println("Order processed: " + order.getId());
    }
}
```

### 案例2：缓存系统设计

#### 需求分析
设计一个线程安全的LRU缓存，要求：
1. 支持并发读写
2. 实现LRU淘汰策略
3. 支持设置过期时间

#### 设计方案
```java
public class ThreadSafeLRUCache<K, V> {
    private final int capacity;
    private final ConcurrentHashMap<K, Node<K, V>> cache;
    private final ConcurrentLinkedQueue<K> accessQueue;
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    public ThreadSafeLRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new ConcurrentHashMap<>();
        this.accessQueue = new ConcurrentLinkedQueue<>();
    }
    
    public V get(K key) {
        Node<K, V> node = cache.get(key);
        if (node == null) {
            return null;
        }
        
        // 更新访问时间
        node.setLastAccessTime(System.currentTimeMillis());
        // 移动到队列末尾
        accessQueue.remove(key);
        accessQueue.offer(key);
        
        return node.getValue();
    }
    
    public void put(K key, V value) {
        if (cache.size() >= capacity) {
            // 淘汰最久未使用的元素
            K oldestKey = accessQueue.poll();
            if (oldestKey != null) {
                cache.remove(oldestKey);
            }
        }
        
        Node<K, V> node = new Node<>(key, value, System.currentTimeMillis());
        cache.put(key, node);
        accessQueue.offer(key);
    }
    
    static class Node<K, V> {
        private final K key;
        private final V value;
        private long lastAccessTime;
        
        public Node(K key, V value, long lastAccessTime) {
            this.key = key;
            this.value = value;
            this.lastAccessTime = lastAccessTime;
        }
        
        // getter和setter方法
        public K getKey() { return key; }
        public V getValue() { return value; }
        public long getLastAccessTime() { return lastAccessTime; }
        public void setLastAccessTime(long lastAccessTime) { this.lastAccessTime = lastAccessTime; }
    }
}
```

## 总结

Java并发编程是一个复杂但重要的主题。通过本章的学习，你应该掌握了以下内容：

1. 线程池的原理和使用方法
2. 并发集合框架的特性和应用场景
3. 原子类与无锁编程的优势
4. 显式锁机制的灵活性
5. 并发工具类的使用场景
6. 并发设计模式的实践
7. 性能优化和最佳实践
8. 常见并发问题的识别和解决

在实际开发中，合理使用并发编程技术可以显著提升系统性能，但也需要注意线程安全、死锁、资源竞争等问题。建议在实践中不断积累经验，深入理解并发编程的原理和最佳实践。