# 第七章：Java多线程编程

## 目录
1. [多线程概述](#多线程概述)
2. [线程的创建方式](#线程的创建方式)
3. [线程的状态与生命周期](#线程的状态与生命周期)
4. [线程同步](#线程同步)
5. [线程间通信](#线程间通信)
6. [线程池](#线程池)
7. [并发工具类](#并发工具类)
8. [最佳实践](#最佳实践)
9. [常见陷阱与解决方案](#常见陷阱与解决方案)
10. [总结](#总结)

---

## 多线程概述

### 什么是进程和线程？

在计算机科学中，**进程**（Process）是指正在运行的程序实例，它拥有独立的内存空间和系统资源。而**线程**（Thread）是进程中的一个执行单元，是CPU调度和分派的基本单位。一个进程可以包含多个线程，这些线程共享进程的内存空间和资源。

### 为什么需要多线程？

1. **提高程序性能**：通过并发执行多个任务来提高程序的整体性能
2. **改善用户体验**：避免界面卡顿，保持应用程序响应性
3. **充分利用多核处理器**：现代CPU通常具有多个核心，多线程可以更好地利用硬件资源
4. **简化复杂任务**：将复杂的任务分解为多个简单的子任务并行处理

### Java多线程的优势

Java语言原生支持多线程编程，提供了丰富的API和工具来简化并发编程：
- 内置的线程安全机制
- 丰富的并发工具类
- 跨平台的一致性
- 强大的调试和监控工具

## 线程的创建方式

在Java中，有多种方式可以创建线程，每种方式都有其特点和适用场景。

### 方式一：继承Thread类

```java
// 自定义线程类
class MyThread extends Thread {
    private String threadName;
    
    public MyThread(String name) {
        this.threadName = name;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(threadName + " - 计数: " + i);
            try {
                // 模拟一些工作
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                System.out.println(threadName + " 被中断");
            }
        }
        System.out.println(threadName + " 执行完毕");
    }
}

// 使用示例
public class ThreadExample {
    public static void main(String[] args) {
        MyThread thread1 = new MyThread("线程1");
        MyThread thread2 = new MyThread("线程2");
        
        // 启动线程
        thread1.start();
        thread2.start();
        
        System.out.println("主线程继续执行...");
    }
}
```

**优点**：简单直接，易于理解和使用  
**缺点**：由于Java单继承的限制，如果继承了Thread类，就不能再继承其他类

### 方式二：实现Runnable接口

```java
// 实现Runnable接口
class MyRunnable implements Runnable {
    private String taskName;
    
    public MyRunnable(String name) {
        this.taskName = name;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(taskName + " - 执行任务 " + i);
            try {
                Thread.sleep(800);
            } catch (InterruptedException e) {
                System.out.println(taskName + " 被中断");
            }
        }
        System.out.println(taskName + " 任务完成");
    }
}

// 使用示例
public class RunnableExample {
    public static void main(String[] args) {
        MyRunnable task1 = new MyRunnable("任务1");
        MyRunnable task2 = new MyRunnable("任务2");
        
        // 创建线程对象并传入Runnable任务
        Thread thread1 = new Thread(task1);
        Thread thread2 = new Thread(task2);
        
        // 启动线程
        thread1.start();
        thread2.start();
        
        System.out.println("主线程执行其他任务...");
    }
}
```

**优点**：
- 避免了单继承的局限性
- 更好的面向对象设计，任务和线程分离
- 可以让多个线程共享同一个Runnable实例

**缺点**：相比继承Thread略显复杂

### 方式三：实现Callable接口

```java
import java.util.concurrent.Callable;
import java.util.concurrent.FutureTask;

// 实现Callable接口，可以返回结果并抛出异常
class MyCallable implements Callable<String> {
    private String jobName;
    
    public MyCallable(String name) {
        this.jobName = name;
    }
    
    @Override
    public String call() throws Exception {
        StringBuilder result = new StringBuilder();
        for (int i = 1; i <= 3; i++) {
            result.append(jobName).append(" 完成步骤 ").append(i).append("\n");
            Thread.sleep(1000); // 模拟工作
        }
        return result.toString() + jobName + " 全部完成";
    }
}

// 使用示例
public class CallableExample {
    public static void main(String[] args) {
        MyCallable job1 = new MyCallable("工作1");
        MyCallable job2 = new MyCallable("工作2");
        
        // 创建FutureTask包装Callable
        FutureTask<String> futureTask1 = new FutureTask<>(job1);
        FutureTask<String> futureTask2 = new FutureTask<>(job2);
        
        // 创建线程执行FutureTask
        Thread thread1 = new Thread(futureTask1);
        Thread thread2 = new Thread(futureTask2);
        
        // 启动线程
        thread1.start();
        thread2.start();
        
        try {
            // 获取执行结果
            String result1 = futureTask1.get(); // 阻塞等待结果
            String result2 = futureTask2.get();
            
            System.out.println("结果1:\n" + result1);
            System.out.println("结果2:\n" + result2);
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        System.out.println("主线程执行完毕");
    }
}
```

**优点**：
- 可以返回执行结果
- 可以抛出受检异常
- 支持取消操作

**缺点**：相对复杂，需要配合FutureTask使用

### 方式四：使用线程池

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

// 使用线程池的方式
public class ThreadPoolExample {
    public static void main(String[] args) {
        // 创建固定大小的线程池
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        // 提交任务到线程池
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("任务 " + taskId + " 开始执行，线程: " + 
                                 Thread.currentThread().getName());
                try {
                    Thread.sleep(2000); // 模拟工作
                    System.out.println("任务 " + taskId + " 执行完成");
                } catch (InterruptedException e) {
                    System.out.println("任务 " + taskId + " 被中断");
                }
            });
        }
        
        // 关闭线程池
        executor.shutdown();
        System.out.println("线程池已关闭，等待所有任务完成...");
    }
}
```

**优点**：
- 减少线程创建和销毁的开销
- 更好地控制系统的资源使用
- 提供了更灵活的任务管理方式

## 线程的状态与生命周期

Java线程在其生命周期中有多种状态，了解这些状态对于编写正确的多线程程序非常重要。

### 线程状态详解

Java线程主要有以下几种状态：

1. **NEW（新建）**：线程被创建但尚未启动
2. **RUNNABLE（可运行）**：线程正在Java虚拟机中执行
3. **BLOCKED（阻塞）**：线程被阻塞等待监视器锁
4. **WAITING（等待）**：线程无限期等待另一个线程执行特定操作
5. **TIMED_WAITING（超时等待）**：线程等待另一个线程执行操作，但设置了等待时间限制
6. **TERMINATED（终止）**：线程已退出

```java
public class ThreadStateExample {
    public static void main(String[] args) throws InterruptedException {
        Thread thread = new Thread(() -> {
            System.out.println("线程执行中...");
            try {
                Thread.sleep(3000); // TIMED_WAITING状态
                synchronized (ThreadStateExample.class) {
                    // 如果有其他线程持有锁，则进入BLOCKED状态
                    System.out.println("获取到锁，继续执行");
                }
            } catch (InterruptedException e) {
                System.out.println("线程被中断");
            }
        });
        
        System.out.println("初始状态: " + thread.getState()); // NEW
        
        thread.start();
        System.out.println("启动后状态: " + thread.getState()); // RUNNABLE
        
        Thread.sleep(1000);
        System.out.println("睡眠期间状态: " + thread.getState()); // TIMED_WAITING
        
        thread.join(); // 等待线程结束
        System.out.println("结束后状态: " + thread.getState()); // TERMINATED
    }
}
```

### 线程优先级

Java线程支持优先级设置，但需要注意的是，线程优先级只是给操作系统的一个建议，并不能保证高优先级的线程一定会先执行。

```java
public class ThreadPriorityExample {
    public static void main(String[] args) {
        Thread highPriority = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println("高优先级线程: " + i);
            }
        });
        
        Thread lowPriority = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println("低优先级线程: " + i);
            }
        });
        
        // 设置优先级
        highPriority.setPriority(Thread.MAX_PRIORITY); // 10
        lowPriority.setPriority(Thread.MIN_PRIORITY);  // 1
        
        highPriority.start();
        lowPriority.start();
    }
}
```

## 线程同步

在多线程环境中，当多个线程同时访问共享资源时，可能会出现数据不一致的问题。线程同步就是用来解决这类问题的机制。

### synchronized关键字

`synchronized`是Java中最基本的同步机制，它可以用于方法或代码块。

#### 同步方法

```java
class Counter {
    private int count = 0;
    
    // 同步方法 - 锁定当前实例(this)
    public synchronized void increment() {
        count++;
    }
    
    // 静态同步方法 - 锁定类对象(Counter.class)
    public static synchronized void staticMethod() {
        // 静态同步方法的示例
    }
    
    public int getCount() {
        return count;
    }
}

public class SynchronizedMethodExample {
    public static void main(String[] args) throws InterruptedException {
        Counter counter = new Counter();
        
        // 创建多个线程同时访问counter
        Thread[] threads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.increment();
                }
            });
        }
        
        // 启动所有线程
        for (Thread thread : threads) {
            thread.start();
        }
        
        // 等待所有线程完成
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("最终计数: " + counter.getCount()); // 应该是10000
    }
}
```

#### 同步代码块

```java
class BankAccount {
    private double balance;
    private final Object lock = new Object(); // 专用锁对象
    
    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }
    
    // 存款操作
    public void deposit(double amount) {
        synchronized (lock) { // 使用专用锁对象
            System.out.println(Thread.currentThread().getName() + 
                             " 正在存款: " + amount);
            double temp = balance;
            try {
                Thread.sleep(100); // 模拟处理时间
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            balance = temp + amount;
            System.out.println(Thread.currentThread().getName() + 
                             " 存款后余额: " + balance);
        }
    }
    
    // 取款操作
    public void withdraw(double amount) {
        synchronized (lock) { // 使用相同锁对象确保互斥
            System.out.println(Thread.currentThread().getName() + 
                             " 正在取款: " + amount);
            if (balance >= amount) {
                double temp = balance;
                try {
                    Thread.sleep(100); // 模拟处理时间
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                balance = temp - amount;
                System.out.println(Thread.currentThread().getName() + 
                                 " 取款后余额: " + balance);
            } else {
                System.out.println(Thread.currentThread().getName() + 
                                 " 余额不足，无法取款");
            }
        }
    }
    
    public double getBalance() {
        synchronized (lock) {
            return balance;
        }
    }
}

public class SynchronizedBlockExample {
    public static void main(String[] args) throws InterruptedException {
        BankAccount account = new BankAccount(1000.0);
        
        // 创建存款线程
        Thread depositThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                account.deposit(100);
            }
        }, "存款线程");
        
        // 创建取款线程
        Thread withdrawThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                account.withdraw(50);
            }
        }, "取款线程");
        
        // 启动线程
        depositThread.start();
        withdrawThread.start();
        
        // 等待线程完成
        depositThread.join();
        withdrawThread.join();
        
        System.out.println("最终余额: " + account.getBalance());
    }
}
```

### volatile关键字

`volatile`关键字用于确保变量的可见性，但它不能替代`synchronized`来实现原子性操作。

```java
class VolatileExample {
    // volatile确保变量在线程间的可见性
    private volatile boolean running = true;
    
    public void start() {
        Thread worker = new Thread(() -> {
            int counter = 0;
            while (running) {
                counter++;
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
            System.out.println("工作线程结束，计数: " + counter);
        });
        
        worker.start();
        
        // 主线程3秒后停止工作线程
        try {
            Thread.sleep(3000);
            running = false; // volatile确保这个变化对工作线程立即可见
            System.out.println("主线程设置running为false");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    public static void main(String[] args) {
        new VolatileExample().start();
    }
}
```

## 线程间通信

线程间通信是指多个线程之间协调工作的机制。Java提供了多种方式进行线程间通信。

### wait/notify机制

`wait()`、`notify()`和`notifyAll()`方法用于实现线程间的协作。

```java
import java.util.LinkedList;
import java.util.Queue;

class ProducerConsumerExample {
    private final Queue<Integer> queue = new LinkedList<>();
    private final int CAPACITY = 5;
    
    // 生产者方法
    public void produce() throws InterruptedException {
        int value = 0;
        while (true) {
            synchronized (this) {
                // 如果队列满了，生产者等待
                while (queue.size() == CAPACITY) {
                    System.out.println("队列已满，生产者等待...");
                    wait(); // 释放锁并等待
                }
                
                System.out.println("生产: " + value);
                queue.add(value++);
                
                // 通知消费者可以消费了
                notify();
                
                Thread.sleep(1000); // 模拟生产时间
            }
        }
    }
    
    // 消费者方法
    public void consume() throws InterruptedException {
        while (true) {
            synchronized (this) {
                // 如果队列为空，消费者等待
                while (queue.isEmpty()) {
                    System.out.println("队列为空，消费者等待...");
                    wait(); // 释放锁并等待
                }
                
                int value = queue.poll();
                System.out.println("消费: " + value);
                
                // 通知生产者可以生产了
                notify();
                
                Thread.sleep(1000); // 模拟消费时间
            }
        }
    }
    
    public static void main(String[] args) {
        ProducerConsumerExample example = new ProducerConsumerExample();
        
        // 生产者线程
        Thread producer = new Thread(() -> {
            try {
                example.produce();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        // 消费者线程
        Thread consumer = new Thread(() -> {
            try {
                example.consume();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        producer.start();
        consumer.start();
    }
}
```

### join方法

`join()`方法用于等待线程执行完毕。

```java
public class JoinExample {
    public static void main(String[] args) throws InterruptedException {
        Thread task1 = new Thread(() -> {
            for (int i = 1; i <= 3; i++) {
                System.out.println("任务1执行步骤 " + i);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            System.out.println("任务1完成");
        });
        
        Thread task2 = new Thread(() -> {
            for (int i = 1; i <= 3; i++) {
                System.out.println("任务2执行步骤 " + i);
                try {
                    Thread.sleep(800);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            System.out.println("任务2完成");
        });
        
        System.out.println("启动任务1和任务2");
        task1.start();
        task2.start();
        
        // 等待任务1完成
        task1.join();
        System.out.println("任务1已经完成，继续执行主线程");
        
        // 等待任务2完成
        task2.join();
        System.out.println("任务2已经完成，主线程结束");
    }
}
```

## 线程池

线程池是一种基于池化思想管理线程的工具，它可以有效地控制运行的线程数量，减少创建和销毁线程的开销。

### 线程池的类型

Java提供了几种常用的线程池：

#### 1. FixedThreadPool（固定大小线程池）

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class FixedThreadPoolExample {
    public static void main(String[] args) {
        // 创建固定大小为3的线程池
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        // 提交10个任务
        for (int i = 1; i <= 10; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("任务 " + taskId + " 开始执行，线程: " + 
                                 Thread.currentThread().getName());
                try {
                    Thread.sleep(2000); // 模拟工作
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("任务 " + taskId + " 执行完成");
            });
        }
        
        // 关闭线程池
        executor.shutdown();
        System.out.println("线程池已关闭");
    }
}
```

#### 2. CachedThreadPool（缓存线程池）

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CachedThreadPoolExample {
    public static void main(String[] args) {
        // 创建缓存线程池
        ExecutorService executor = Executors.newCachedThreadPool();
        
        // 提交多个任务
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("任务 " + taskId + " 开始执行，线程: " + 
                                 Thread.currentThread().getName());
                try {
                    Thread.sleep(3000); // 模拟工作
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("任务 " + taskId + " 执行完成");
            });
        }
        
        // 关闭线程池
        executor.shutdown();
        System.out.println("线程池已关闭");
    }
}
```

#### 3. SingleThreadExecutor（单线程池）

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SingleThreadExecutorExample {
    public static void main(String[] args) {
        // 创建单线程池
        ExecutorService executor = Executors.newSingleThreadExecutor();
        
        // 提交多个任务，它们会按顺序执行
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("任务 " + taskId + " 开始执行，线程: " + 
                                 Thread.currentThread().getName());
                try {
                    Thread.sleep(1000); // 模拟工作
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("任务 " + taskId + " 执行完成");
            });
        }
        
        // 关闭线程池
        executor.shutdown();
        System.out.println("线程池已关闭");
    }
}
```

#### 4. ScheduledThreadPool（定时线程池）

```java
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class ScheduledThreadPoolExample {
    public static void main(String[] args) {
        // 创建定时线程池
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
        
        // 延迟执行任务
        scheduler.schedule(() -> {
            System.out.println("延迟3秒执行的任务");
        }, 3, TimeUnit.SECONDS);
        
        // 定期执行任务
        scheduler.scheduleAtFixedRate(() -> {
            System.out.println("每2秒执行一次的任务 - " + System.currentTimeMillis());
        }, 1, 2, TimeUnit.SECONDS);
        
        // 延迟并定期执行任务
        scheduler.scheduleWithFixedDelay(() -> {
            System.out.println("上一个任务完成后延迟3秒执行 - " + System.currentTimeMillis());
            try {
                Thread.sleep(1000); // 模拟任务执行时间
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, 2, 3, TimeUnit.SECONDS);
        
        // 运行10秒后关闭
        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        scheduler.shutdown();
        System.out.println("定时线程池已关闭");
    }
}
```

### 自定义线程池

使用`ThreadPoolExecutor`可以创建自定义的线程池，更加灵活地控制线程池的行为。

```java
import java.util.concurrent.*;

public class CustomThreadPoolExample {
    public static void main(String[] args) {
        // 自定义线程池参数
        int corePoolSize = 2;        // 核心线程数
        int maximumPoolSize = 4;     // 最大线程数
        long keepAliveTime = 10;     // 空闲线程存活时间
        TimeUnit unit = TimeUnit.SECONDS; // 时间单位
        BlockingQueue<Runnable> workQueue = new ArrayBlockingQueue<>(2); // 工作队列
        ThreadFactory threadFactory = Executors.defaultThreadFactory(); // 线程工厂
        RejectedExecutionHandler handler = new ThreadPoolExecutor.CallerRunsPolicy(); // 拒绝策略
        
        // 创建自定义线程池
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            corePoolSize,
            maximumPoolSize,
            keepAliveTime,
            unit,
            workQueue,
            threadFactory,
            handler
        );
        
        // 提交多个任务
        for (int i = 1; i <= 10; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("任务 " + taskId + " 开始执行，线程: " + 
                                 Thread.currentThread().getName());
                try {
                    Thread.sleep(2000); // 模拟工作
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("任务 " + taskId + " 执行完成");
            });
        }
        
        // 关闭线程池
        executor.shutdown();
        try {
            // 等待所有任务完成
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
        
        System.out.println("自定义线程池已关闭");
    }
}
```

## 并发工具类

Java并发包(`java.util.concurrent`)提供了许多强大的并发工具类，大大简化了并发编程。

### CountDownLatch（倒计时门闩）

```java
import java.util.concurrent.CountDownLatch;

public class CountDownLatchExample {
    public static void main(String[] args) throws InterruptedException {
        // 创建倒计时门闩，计数为3
        CountDownLatch latch = new CountDownLatch(3);
        
        // 创建准备工作线程
        Thread prepare1 = new Thread(() -> {
            System.out.println("准备工作1开始...");
            try {
                Thread.sleep(2000);
                System.out.println("准备工作1完成");
                latch.countDown(); // 计数减1
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        Thread prepare2 = new Thread(() -> {
            System.out.println("准备工作2开始...");
            try {
                Thread.sleep(3000);
                System.out.println("准备工作2完成");
                latch.countDown(); // 计数减1
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        Thread prepare3 = new Thread(() -> {
            System.out.println("准备工作3开始...");
            try {
                Thread.sleep(1000);
                System.out.println("准备工作3完成");
                latch.countDown(); // 计数减1
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        // 启动准备线程
        prepare1.start();
        prepare2.start();
        prepare3.start();
        
        System.out.println("等待所有准备工作完成...");
        // 等待倒计时归零
        latch.await();
        System.out.println("所有准备工作完成，可以开始主任务了！");
    }
}
```

### CyclicBarrier（循环屏障）

```java
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

public class CyclicBarrierExample {
    public static void main(String[] args) {
        // 创建循环屏障，需要3个线程到达屏障
        CyclicBarrier barrier = new CyclicBarrier(3, () -> {
            // 当所有线程都到达屏障时执行的回调
            System.out.println("所有参与者都到达屏障，开始下一步工作！");
        });
        
        // 创建参与者线程
        for (int i = 1; i <= 3; i++) {
            final int participantId = i;
            new Thread(() -> {
                try {
                    System.out.println("参与者 " + participantId + " 开始第一阶段工作");
                    Thread.sleep((long) (Math.random() * 3000)); // 模拟工作
                    
                    System.out.println("参与者 " + participantId + " 第一阶段完成，等待其他参与者");
                    // 等待其他线程到达屏障
                    barrier.await();
                    
                    System.out.println("参与者 " + participantId + " 开始第二阶段工作");
                    Thread.sleep((long) (Math.random() * 2000)); // 模拟工作
                    
                    System.out.println("参与者 " + participantId + " 第二阶段完成，等待其他参与者");
                    // 再次等待其他线程到达屏障
                    barrier.await();
                    
                    System.out.println("参与者 " + participantId + " 所有工作完成");
                } catch (InterruptedException | BrokenBarrierException e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}
```

### Semaphore（信号量）

```java
import java.util.concurrent.Semaphore;

public class SemaphoreExample {
    public static void main(String[] args) {
        // 创建信号量，许可数为2
        Semaphore semaphore = new Semaphore(2);
        
        // 创建多个工作线程
        for (int i = 1; i <= 5; i++) {
            final int workerId = i;
            new Thread(() -> {
                try {
                    System.out.println("工作者 " + workerId + " 请求资源");
                    // 获取许可
                    semaphore.acquire();
                    
                    System.out.println("工作者 " + workerId + " 获得资源，开始工作");
                    Thread.sleep((long) (Math.random() * 5000)); // 模拟工作
                    System.out.println("工作者 " + workerId + " 工作完成，释放资源");
                    
                    // 释放许可
                    semaphore.release();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
    }
}
```

### ReadWriteLock（读写锁）

```java
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

class SharedResource {
    private String data = "初始数据";
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    // 读操作
    public String read() {
        lock.readLock().lock();
        try {
            System.out.println(Thread.currentThread().getName() + " 正在读取数据");
            Thread.sleep(1000); // 模拟读取时间
            return data;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        } finally {
            lock.readLock().unlock();
            System.out.println(Thread.currentThread().getName() + " 读取完成");
        }
    }
    
    // 写操作
    public void write(String newData) {
        lock.writeLock().lock();
        try {
            System.out.println(Thread.currentThread().getName() + " 正在写入数据");
            Thread.sleep(2000); // 模拟写入时间
            data = newData;
            System.out.println(Thread.currentThread().getName() + " 写入完成: " + data);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            lock.writeLock().unlock();
        }
    }
}

public class ReadWriteLockExample {
    public static void main(String[] args) {
        SharedResource resource = new SharedResource();
        
        // 创建读线程
        for (int i = 1; i <= 3; i++) {
            final int readerId = i;
            new Thread(() -> {
                String data = resource.read();
                System.out.println("读者 " + readerId + " 读取到: " + data);
            }, "Reader-" + readerId).start();
        }
        
        // 创建写线程
        new Thread(() -> {
            resource.write("更新后的数据");
        }, "Writer").start();
        
        // 再创建一些读线程
        for (int i = 4; i <= 6; i++) {
            final int readerId = i;
            new Thread(() -> {
                String data = resource.read();
                System.out.println("读者 " + readerId + " 读取到: " + data);
            }, "Reader-" + readerId).start();
        }
    }
}
```

## 最佳实践

编写高质量的多线程程序需要遵循一些最佳实践：

### 1. 避免共享可变状态

尽可能使用不可变对象或局部变量，减少共享可变状态的使用。

```java
// 不好的做法
class BadPractice {
    private int counter = 0; // 共享可变状态
    
    public void increment() {
        counter++; // 非线程安全
    }
}

// 好的做法
class GoodPractice {
    private final AtomicInteger counter = new AtomicInteger(0); // 使用原子类
    
    public void increment() {
        counter.incrementAndGet(); // 线程安全
    }
}
```

### 2. 正确使用同步机制

选择合适的同步机制，避免过度同步或同步不足。

```java
// 使用ConcurrentHashMap而不是Hashtable
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

class BestPracticeExample {
    // 推荐使用ConcurrentHashMap
    private final Map<String, String> concurrentMap = new ConcurrentHashMap<>();
    
    public void putValue(String key, String value) {
        concurrentMap.put(key, value); // 内部已同步，无需额外同步
    }
    
    public String getValue(String key) {
        return concurrentMap.get(key); // 线程安全
    }
}
```

### 3. 合理使用线程池

根据应用场景选择合适的线程池类型和参数。

```java
import java.util.concurrent.*;

public class ThreadPoolBestPractice {
    // CPU密集型任务使用固定大小线程池
    private static final ExecutorService cpuIntensivePool = 
        Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
    
    // IO密集型任务使用缓存线程池
    private static final ExecutorService ioIntensivePool = 
        Executors.newCachedThreadPool();
    
    // 定时任务使用ScheduledThreadPool
    private static final ScheduledExecutorService scheduledPool = 
        Executors.newScheduledThreadPool(2);
}
```

### 4. 正确处理异常

在线程中正确处理异常，避免因未捕获异常导致线程意外终止。

```java
public class ExceptionHandlingExample {
    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(2);
        
        // 设置未捕获异常处理器
        Thread.setDefaultUncaughtExceptionHandler((thread, exception) -> {
            System.err.println("线程 " + thread.getName() + " 发生未捕获异常: " + exception);
        });
        
        executor.submit(() -> {
            try {
                // 可能抛出异常的代码
                throw new RuntimeException("模拟异常");
            } catch (RuntimeException e) {
                System.err.println("捕获到异常: " + e.getMessage());
                // 进行适当的异常处理
            }
        });
        
        executor.shutdown();
    }
}
```

### 5. 避免死锁

设计时考虑锁的顺序，避免循环等待。

```java
class DeadlockAvoidance {
    private final Object lock1 = new Object();
    private final Object lock2 = new Object();
    
    public void method1() {
        // 总是以相同的顺序获取锁
        synchronized (lock1) {
            System.out.println("method1: 获取了lock1");
            synchronized (lock2) {
                System.out.println("method1: 获取了lock2");
            }
        }
    }
    
    public void method2() {
        // 保持相同的锁顺序
        synchronized (lock1) {
            System.out.println("method2: 获取了lock1");
            synchronized (lock2) {
                System.out.println("method2: 获取了lock2");
            }
        }
    }
}
```

## 常见陷阱与解决方案

### 1. 竞态条件

竞态条件发生在多个线程同时访问共享资源时，执行结果依赖于线程执行的特定顺序。

```java
// 有问题的代码
class RaceConditionExample {
    private int count = 0;
    
    public void increment() {
        count++; // 非原子操作，可能产生竞态条件
    }
    
    // 解决方案：使用同步或原子类
    private final AtomicInteger atomicCount = new AtomicInteger(0);
    
    public void safeIncrement() {
        atomicCount.incrementAndGet(); // 原子操作
    }
}
```

### 2. 活锁

活锁是指线程虽然没有被阻塞，但由于某些条件不满足，一直重复尝试执行某个操作。

```java
// 活锁示例
class LivelockExample {
    // 解决方案：引入随机性或退避机制
    public void transferMoney(Account from, Account to, int amount) {
        while (true) {
            if (from.lock.tryLock()) {
                try {
                    if (to.lock.tryLock()) {
                        try {
                            from.balance -= amount;
                            to.balance += amount;
                            break; // 成功转账，退出循环
                        } finally {
                            to.lock.unlock();
                        }
                    }
                } finally {
                    from.lock.unlock();
                }
            }
            
            // 引入随机退避，避免活锁
            try {
                Thread.sleep((long) (Math.random() * 10));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
```

### 3. 内存可见性问题

没有正确同步的情况下，一个线程对共享变量的修改可能对其他线程不可见。

```java
class VisibilityProblem {
    private boolean flag = false; // 可能存在可见性问题
    
    // 解决方案1：使用volatile
    private volatile boolean volatileFlag = false;
    
    // 解决方案2：使用同步
    private boolean syncFlag = false;
    
    public synchronized void setSyncFlag(boolean value) {
        syncFlag = value;
    }
    
    public synchronized boolean getSyncFlag() {
        return syncFlag;
    }
}
```

### 4. 上下文切换开销

频繁的线程切换会带来性能开销。

```java
// 不好的做法：创建过多线程
class TooManyThreadsExample {
    public void processData(List<Integer> data) {
        // 为每个数据项创建一个线程（不推荐）
        for (Integer item : data) {
            new Thread(() -> processItem(item)).start();
        }
    }
    
    private void processItem(Integer item) {
        // 处理单个数据项
    }
}

// 好的做法：使用线程池
class ThreadPoolExample {
    private final ExecutorService executor = 
        Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
    
    public void processData(List<Integer> data) {
        // 将任务提交到线程池
        for (Integer item : data) {
            executor.submit(() -> processItem(item));
        }
    }
    
    private void processItem(Integer item) {
        // 处理单个数据项
    }
}
```

## 总结

Java多线程编程是一个强大而复杂的主题，掌握它对于编写高性能、响应迅速的应用程序至关重要。在本章中，我们学习了：

1. **多线程基础概念**：理解进程与线程的区别，以及为什么需要多线程
2. **线程创建方式**：掌握继承Thread、实现Runnable、实现Callable以及使用线程池等多种创建线程的方法
3. **线程状态与生命周期**：深入了解线程的各种状态及其转换过程
4. **线程同步机制**：学会使用synchronized、volatile等关键字保证线程安全
5. **线程间通信**：掌握wait/notify、join等线程协作机制
6. **线程池技术**：了解不同类型线程池的特点和使用场景
7. **并发工具类**：熟悉CountDownLatch、CyclicBarrier、Semaphore等高级并发工具
8. **最佳实践**：遵循良好的编程习惯，避免常见陷阱

通过系统学习和实践这些概念，您将能够编写出高效、稳定、易于维护的多线程Java程序。记住，多线程编程需要大量的实践经验和深入理解，建议您在实际项目中不断练习和完善自己的技能。