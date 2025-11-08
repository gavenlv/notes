# 第6章：并发编程

## 学习目标

通过本章的学习，您将掌握以下内容：

1. **并发基础概念**
   - 理解并发与并行的区别
   - 掌握线程、进程和ExecutionContext的基本概念
   - 学习Scala中的并发模型

2. **Future和Promise**
   - Future的基本使用和组合
   - Promise的创建和使用
   - 异步编程模式

3. **ExecutionContext详解**
   - ExecutionContext的作用和配置
   - 不同类型的ExecutionContext
   - 线程池管理和优化

4. **Actor模型**
   - Akka Actor基础概念
   - Actor通信和监督机制
   - 构建并发应用

5. **异步编程进阶**
   - async/await模式
   - 异步流处理
   - 错误处理和恢复

6. **STM和无锁编程**
   - 软件事务内存概念
   - 无锁数据结构
   - 原子操作和CAS

7. **并发编程最佳实践**
   - 性能优化技巧
   - 内存管理和泄漏避免
   - 调试和测试并发代码

## 环境要求

- Scala 2.13.x
- JDK 8或更高版本
- sbt 1.5.x或更高版本
- Akka 2.6.x（用于Actor示例）

## 章节内容

### 6.1 并发基础
- 并发与并行的概念
- 线程安全和同步
- Scala并发原语

### 6.2 Future和Promise详解
- Future的创建和使用
- Future组合和链式操作
- Promise的使用场景
- 异步回调处理

### 6.3 ExecutionContext深入
- ExecutionContext的作用机制
- 线程池配置和优化
- 阻塞操作处理

### 6.4 Actor模型实践
- Akka Actor基础
- Actor通信模式
- 监督策略和容错

### 6.5 异步编程模式
- 异步编程最佳实践
- 流式处理
- 异常处理机制

### 6.6 STM和无锁编程
- 软件事务内存
- 无锁数据结构实现
- 原子操作应用

### 6.7 并发编程最佳实践
- 性能优化技巧
- 内存泄漏避免
- 调试和测试方法

## 实践练习

### 练习1：构建简单的Future链
创建一个处理用户订单的Future链，包括用户验证、订单创建和支付处理。

### 练习2：实现自定义ExecutionContext
创建一个针对CPU密集型任务优化的ExecutionContext。

### 练习3：Actor通信系统
使用Akka Actor构建一个简单的聊天系统。

### 练习4：无锁计数器
实现一个线程安全的无锁计数器。

## 代码示例结构

```
src/main/scala/06-concurrent-programming/
├── FutureExamples.scala          # Future基本使用示例
├── PromiseExamples.scala         # Promise使用示例
├── ExecutionContextExamples.scala # ExecutionContext使用示例
├── ActorExamples.scala           # Akka Actor使用示例
├── AsyncExamples.scala           # 异步编程示例
├── STMExamples.scala             # STM和无锁编程示例
└── PerformanceExamples.scala     # 性能优化示例
```

### 代码示例说明

#### 1. FutureExamples.scala
展示了Future的基本使用方法，包括：
- Future的创建和基本操作
- Future的回调处理（onSuccess, onFailure, onComplete）
- Future的组合（flatMap, map）
- Future的链式操作
- Future的错误恢复（recover, recoverWith）
- Future序列操作（sequence, traverse）
- Future的超时处理

#### 2. PromiseExamples.scala
展示了Promise的使用方法，包括：
- Promise的创建和基本使用
- 将异步操作转换为Future
- Promise的失败处理
- 使用Promise实现回调转Future
- Promise的超时处理
- 手动完成Promise
- Promise的链式操作
- Promise与Future的组合使用

#### 3. ExecutionContextExamples.scala
展示了ExecutionContext的使用方法，包括：
- 不同类型的ExecutionContext（固定线程池、缓存线程池等）
- 自定义ExecutionContext的创建
- 阻塞操作的正确处理方式
- scala.concurrent.blocking的使用
- ExecutionContext的配置和优化

#### 4. ActorExamples.scala
展示了Akka Actor的基本使用方法，包括：
- Actor的定义和创建
- Actor消息传递机制
- Actor行为和状态管理
- Actor监督和错误处理
- Actor系统管理
- 不同Actor之间的通信

#### 5. AsyncExamples.scala
展示了异步编程的高级特性，包括：
- 传统的Future组合方式
- for-comprehension语法糖
- 异步错误处理
- 并行执行多个Future
- 批量操作处理
- 超时处理机制
- 异步流处理基础

#### 6. STMExamples.scala
展示了STM和无锁编程的概念，包括：
- 简单的STM实现
- 银行账户并发操作示例
- 无锁计数器实现
- 生产者-消费者模式
- 读写锁的使用
- 原子操作和CAS

#### 7. PerformanceExamples.scala
展示了并发编程的性能优化技巧，包括：
- Future性能优化
- 并发集合的使用和性能对比
- ExecutionContext优化配置
- 内存优化技巧
- 并发处理性能对比
- 阻塞操作优化

## 学习建议

1. **循序渐进**：从基础的Future开始，逐步学习更复杂的并发概念
2. **动手实践**：每个概念都要通过代码实践来加深理解
3. **关注性能**：理解不同并发模式的性能特点
4. **错误处理**：重视并发代码的错误处理和恢复机制
5. **调试技巧**：学习并发代码的调试方法

## 扩展阅读

- 《Scala并发编程》
- Akka官方文档
- 《Java并发编程实战》
- 《深入理解JVM并发编程》