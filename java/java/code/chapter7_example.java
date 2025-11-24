import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.*;

/**
 * 第七章：Java多线程编程 - 完整示例代码
 * 
 * 本文件包含了Java多线程编程的主要概念和实用示例，涵盖了：
 * 1. 线程的创建方式
 * 2. 线程同步机制
 * 3. 线程间通信
 * 4. 线程池使用
 * 5. 并发工具类
 * 6. 综合示例：生产者消费者模型和银行账户系统
 */

// 示例1：继承Thread类创建线程
class ThreadCreationExample1 extends Thread {
    private String threadName;
    
    public ThreadCreationExample1(String name) {
        this.threadName = name;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(threadName + " - 计数: " + i);
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                System.out.println(threadName + " 被中断");
                return;
            }
        }
        System.out.println(threadName + " 执行完毕");
    }
    
    public static void demonstrate() {
        System.out.println("=== 继承Thread类创建线程 ===");
        ThreadCreationExample1 thread1 = new ThreadCreationExample1("线程1");
        ThreadCreationExample1 thread2 = new ThreadCreationExample1("线程2");
        
        thread1.start();
        thread2.start();
        
        try {
            thread1.join();
            thread2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例2：实现Runnable接口创建线程
class ThreadCreationExample2 implements Runnable {
    private String taskName;
    
    public ThreadCreationExample2(String name) {
        this.taskName = name;
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(taskName + " - 执行任务 " + i);
            try {
                Thread.sleep(400);
            } catch (InterruptedException e) {
                System.out.println(taskName + " 被中断");
                return;
            }
        }
        System.out.println(taskName + " 任务完成");
    }
    
    public static void demonstrate() {
        System.out.println("=== 实现Runnable接口创建线程 ===");
        ThreadCreationExample2 task1 = new ThreadCreationExample2("任务1");
        ThreadCreationExample2 task2 = new ThreadCreationExample2("任务2");
        
        Thread thread1 = new Thread(task1);
        Thread thread2 = new Thread(task2);
        
        thread1.start();
        thread2.start();
        
        try {
            thread1.join();
            thread2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例3：实现Callable接口创建线程
class ThreadCreationExample3 implements Callable<String> {
    private String jobName;
    
    public ThreadCreationExample3(String name) {
        this.jobName = name;
    }
    
    @Override
    public String call() throws Exception {
        StringBuilder result = new StringBuilder();
        for (int i = 1; i <= 3; i++) {
            result.append(jobName).append(" 完成步骤 ").append(i).append("\n");
            Thread.sleep(600);
        }
        return result.toString() + jobName + " 全部完成";
    }
    
    public static void demonstrate() {
        System.out.println("=== 实现Callable接口创建线程 ===");
        ThreadCreationExample3 job1 = new ThreadCreationExample3("工作1");
        ThreadCreationExample3 job2 = new ThreadCreationExample3("工作2");
        
        FutureTask<String> futureTask1 = new FutureTask<>(job1);
        FutureTask<String> futureTask2 = new FutureTask<>(job2);
        
        Thread thread1 = new Thread(futureTask1);
        Thread thread2 = new Thread(futureTask2);
        
        thread1.start();
        thread2.start();
        
        try {
            String result1 = futureTask1.get();
            String result2 = futureTask2.get();
            
            System.out.println("结果1:\n" + result1);
            System.out.println("结果2:\n" + result2);
        } catch (Exception e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例4：使用线程池
class ThreadPoolExample {
    public static void demonstrate() {
        System.out.println("=== 使用线程池 ===");
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            executor.submit(() -> {
                System.out.println("任务 " + taskId + " 开始执行，线程: " + 
                                 Thread.currentThread().getName());
                try {
                    Thread.sleep(1000);
                    System.out.println("任务 " + taskId + " 执行完成");
                } catch (InterruptedException e) {
                    System.out.println("任务 " + taskId + " 被中断");
                }
            });
        }
        
        executor.shutdown();
        try {
            if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
        System.out.println("线程池示例完成\n");
    }
}

// 示例5：synchronized同步方法
class SynchronizedMethodExample {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public int getCount() {
        return count;
    }
    
    public static void demonstrate() {
        System.out.println("=== synchronized同步方法 ===");
        SynchronizedMethodExample counter = new SynchronizedMethodExample();
        
        Thread[] threads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.increment();
                }
            });
        }
        
        for (Thread thread : threads) {
            thread.start();
        }
        
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        System.out.println("最终计数: " + counter.getCount());
        System.out.println();
    }
}

// 示例6：synchronized同步代码块
class BankAccount {
    private double balance;
    private final Object lock = new Object();
    
    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }
    
    public void deposit(double amount) {
        synchronized (lock) {
            System.out.println(Thread.currentThread().getName() + 
                             " 正在存款: " + amount);
            double temp = balance;
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            balance = temp + amount;
            System.out.println(Thread.currentThread().getName() + 
                             " 存款后余额: " + balance);
        }
    }
    
    public void withdraw(double amount) {
        synchronized (lock) {
            System.out.println(Thread.currentThread().getName() + 
                             " 正在取款: " + amount);
            if (balance >= amount) {
                double temp = balance;
                try {
                    Thread.sleep(100);
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

class SynchronizedBlockExample {
    public static void demonstrate() {
        System.out.println("=== synchronized同步代码块 ===");
        BankAccount account = new BankAccount(1000.0);
        
        Thread depositThread = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                account.deposit(100);
            }
        }, "存款线程");
        
        Thread withdrawThread = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                account.withdraw(50);
            }
        }, "取款线程");
        
        depositThread.start();
        withdrawThread.start();
        
        try {
            depositThread.join();
            withdrawThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("最终余额: " + account.getBalance());
        System.out.println();
    }
}

// 示例7：volatile关键字
class VolatileExample {
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
        
        try {
            Thread.sleep(2000);
            running = false;
            System.out.println("主线程设置running为false");
            worker.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== volatile关键字 ===");
        new VolatileExample().start();
        System.out.println();
    }
}

// 示例8：wait/notify机制
class ProducerConsumerExample {
    private final Queue<Integer> queue = new LinkedList<>();
    private final int CAPACITY = 3;
    
    public void produce() throws InterruptedException {
        int value = 0;
        while (value < 10) {
            synchronized (this) {
                while (queue.size() == CAPACITY) {
                    System.out.println("队列已满，生产者等待...");
                    wait();
                }
                
                System.out.println("生产: " + value);
                queue.add(value++);
                notify();
                Thread.sleep(500);
            }
        }
    }
    
    public void consume() throws InterruptedException {
        while (true) {
            synchronized (this) {
                while (queue.isEmpty()) {
                    System.out.println("队列为空，消费者等待...");
                    wait();
                }
                
                int value = queue.poll();
                System.out.println("消费: " + value);
                
                if (value >= 9) {
                    break;
                }
                
                notify();
                Thread.sleep(800);
            }
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== wait/notify机制 ===");
        ProducerConsumerExample example = new ProducerConsumerExample();
        
        Thread producer = new Thread(() -> {
            try {
                example.produce();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        Thread consumer = new Thread(() -> {
            try {
                example.consume();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        producer.start();
        consumer.start();
        
        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例9：CountDownLatch
class CountDownLatchExample {
    public static void demonstrate() {
        System.out.println("=== CountDownLatch ===");
        CountDownLatch latch = new CountDownLatch(3);
        
        Thread prepare1 = new Thread(() -> {
            System.out.println("准备工作1开始...");
            try {
                Thread.sleep(1000);
                System.out.println("准备工作1完成");
                latch.countDown();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        Thread prepare2 = new Thread(() -> {
            System.out.println("准备工作2开始...");
            try {
                Thread.sleep(1500);
                System.out.println("准备工作2完成");
                latch.countDown();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        Thread prepare3 = new Thread(() -> {
            System.out.println("准备工作3开始...");
            try {
                Thread.sleep(800);
                System.out.println("准备工作3完成");
                latch.countDown();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        prepare1.start();
        prepare2.start();
        prepare3.start();
        
        try {
            System.out.println("等待所有准备工作完成...");
            latch.await();
            System.out.println("所有准备工作完成，可以开始主任务了！");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例10：CyclicBarrier
class CyclicBarrierExample {
    public static void demonstrate() {
        System.out.println("=== CyclicBarrier ===");
        CyclicBarrier barrier = new CyclicBarrier(3, () -> {
            System.out.println("所有参与者都到达屏障，开始下一步工作！");
        });
        
        for (int i = 1; i <= 3; i++) {
            final int participantId = i;
            new Thread(() -> {
                try {
                    System.out.println("参与者 " + participantId + " 开始第一阶段工作");
                    Thread.sleep((long) (Math.random() * 1000));
                    
                    System.out.println("参与者 " + participantId + " 第一阶段完成，等待其他参与者");
                    barrier.await();
                    
                    System.out.println("参与者 " + participantId + " 开始第二阶段工作");
                    Thread.sleep((long) (Math.random() * 1000));
                    
                    System.out.println("参与者 " + participantId + " 第二阶段完成，等待其他参与者");
                    barrier.await();
                    
                    System.out.println("参与者 " + participantId + " 所有工作完成");
                } catch (InterruptedException | BrokenBarrierException e) {
                    e.printStackTrace();
                }
            }).start();
        }
        
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例11：Semaphore
class SemaphoreExample {
    public static void demonstrate() {
        System.out.println("=== Semaphore ===");
        Semaphore semaphore = new Semaphore(2);
        
        for (int i = 1; i <= 5; i++) {
            final int workerId = i;
            new Thread(() -> {
                try {
                    System.out.println("工作者 " + workerId + " 请求资源");
                    semaphore.acquire();
                    
                    System.out.println("工作者 " + workerId + " 获得资源，开始工作");
                    Thread.sleep((long) (Math.random() * 2000));
                    System.out.println("工作者 " + workerId + " 工作完成，释放资源");
                    
                    semaphore.release();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
        
        try {
            Thread.sleep(8000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 示例12：ReadWriteLock
class SharedResource {
    private String data = "初始数据";
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    public String read() {
        lock.readLock().lock();
        try {
            System.out.println(Thread.currentThread().getName() + " 正在读取数据");
            Thread.sleep(500);
            return data;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        } finally {
            lock.readLock().unlock();
            System.out.println(Thread.currentThread().getName() + " 读取完成");
        }
    }
    
    public void write(String newData) {
        lock.writeLock().lock();
        try {
            System.out.println(Thread.currentThread().getName() + " 正在写入数据");
            Thread.sleep(1000);
            data = newData;
            System.out.println(Thread.currentThread().getName() + " 写入完成: " + data);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            lock.writeLock().unlock();
        }
    }
}

class ReadWriteLockExample {
    public static void demonstrate() {
        System.out.println("=== ReadWriteLock ===");
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
        
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println();
    }
}

// 综合示例1：生产者消费者模型
class ProductionConsumerSystem {
    private final BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(5);
    private final AtomicInteger producedCount = new AtomicInteger(0);
    private final AtomicInteger consumedCount = new AtomicInteger(0);
    private volatile boolean producing = true;
    
    class Producer implements Runnable {
        @Override
        public void run() {
            try {
                while (producing || !queue.isEmpty()) {
                    if (producedCount.get() >= 20) {
                        producing = false;
                        break;
                    }
                    
                    int item = producedCount.incrementAndGet();
                    queue.put(item);
                    System.out.println("生产者生产了: " + item + "，队列大小: " + queue.size());
                    Thread.sleep(300);
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
                while (producing || !queue.isEmpty()) {
                    Integer item = queue.poll(1, TimeUnit.SECONDS);
                    if (item != null) {
                        int count = consumedCount.incrementAndGet();
                        System.out.println("消费者消费了: " + item + "，总计消费: " + count);
                        Thread.sleep(500);
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== 综合示例1：生产者消费者模型 ===");
        ProductionConsumerSystem system = new ProductionConsumerSystem();
        
        ExecutorService executor = Executors.newFixedThreadPool(4);
        executor.submit(system.new Producer());
        executor.submit(system.new Producer());
        executor.submit(system.new Consumer());
        executor.submit(system.new Consumer());
        
        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        executor.shutdown();
        try {
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
        System.out.println("生产者消费者系统演示完成\n");
    }
}

// 综合示例2：银行账户系统
class BankSystem {
    static class Account {
        private final String accountId;
        private double balance;
        private final ReadWriteLock lock = new ReentrantReadWriteLock();
        
        public Account(String accountId, double initialBalance) {
            this.accountId = accountId;
            this.balance = initialBalance;
        }
        
        public void deposit(double amount) {
            lock.writeLock().lock();
            try {
                System.out.println(Thread.currentThread().getName() + 
                                 " 正在向账户 " + accountId + " 存款: " + amount);
                balance += amount;
                System.out.println("账户 " + accountId + " 存款后余额: " + balance);
            } finally {
                lock.writeLock().unlock();
            }
        }
        
        public boolean withdraw(double amount) {
            lock.writeLock().lock();
            try {
                System.out.println(Thread.currentThread().getName() + 
                                 " 正在从账户 " + accountId + " 取款: " + amount);
                if (balance >= amount) {
                    balance -= amount;
                    System.out.println("账户 " + accountId + " 取款后余额: " + balance);
                    return true;
                } else {
                    System.out.println("账户 " + accountId + " 余额不足，无法取款");
                    return false;
                }
            } finally {
                lock.writeLock().unlock();
            }
        }
        
        public double getBalance() {
            lock.readLock().lock();
            try {
                return balance;
            } finally {
                lock.readLock().unlock();
            }
        }
        
        public String getAccountId() {
            return accountId;
        }
    }
    
    static class TransferService {
        public static void transfer(Account from, Account to, double amount) {
            // 避免死锁：总是先锁定ID较小的账户
            Account firstLock = from.getAccountId().compareTo(to.getAccountId()) < 0 ? from : to;
            Account secondLock = from.getAccountId().compareTo(to.getAccountId()) < 0 ? to : from;
            double actualAmount = from.getAccountId().compareTo(to.getAccountId()) < 0 ? amount : amount;
            
            synchronized (firstLock) {
                synchronized (secondLock) {
                    if (from.withdraw(amount)) {
                        to.deposit(amount);
                        System.out.println("转账完成: " + amount + " 从 " + from.getAccountId() + " 到 " + to.getAccountId());
                    } else {
                        System.out.println("转账失败: " + from.getAccountId() + " 余额不足");
                    }
                }
            }
        }
    }
    
    public static void demonstrate() {
        System.out.println("=== 综合示例2：银行账户系统 ===");
        Account account1 = new Account("ACC001", 1000.0);
        Account account2 = new Account("ACC002", 500.0);
        
        // 创建多个线程进行存款、取款和转账操作
        ExecutorService executor = Executors.newFixedThreadPool(6);
        
        // 存款操作
        for (int i = 0; i < 3; i++) {
            final int taskId = i;
            executor.submit(() -> {
                account1.deposit(100);
                account2.deposit(50);
            });
        }
        
        // 取款操作
        for (int i = 0; i < 2; i++) {
            final int taskId = i;
            executor.submit(() -> {
                account1.withdraw(200);
                account2.withdraw(100);
            });
        }
        
        // 转账操作
        executor.submit(() -> {
            TransferService.transfer(account1, account2, 300);
        });
        
        executor.submit(() -> {
            TransferService.transfer(account2, account1, 150);
        });
        
        executor.shutdown();
        try {
            if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
        
        System.out.println("最终账户余额:");
        System.out.println("账户 ACC001: " + account1.getBalance());
        System.out.println("账户 ACC002: " + account2.getBalance());
        System.out.println("银行账户系统演示完成\n");
    }
}

// 主类 - 运行所有示例
public class Chapter7Example {
    public static void main(String[] args) {
        System.out.println("第七章：Java多线程编程 - 完整示例");
        System.out.println("=====================================");
        
        // 运行各个示例
        ThreadCreationExample1.demonstrate();
        ThreadCreationExample2.demonstrate();
        ThreadCreationExample3.demonstrate();
        ThreadPoolExample.demonstrate();
        SynchronizedMethodExample.demonstrate();
        SynchronizedBlockExample.demonstrate();
        VolatileExample.demonstrate();
        ProducerConsumerExample.demonstrate();
        CountDownLatchExample.demonstrate();
        CyclicBarrierExample.demonstrate();
        SemaphoreExample.demonstrate();
        ReadWriteLockExample.demonstrate();
        ProductionConsumerSystem.demonstrate();
        BankSystem.demonstrate();
        
        System.out.println("所有示例运行完成!");
    }
}