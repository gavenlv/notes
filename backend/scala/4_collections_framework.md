# 第4章：集合框架 (Collections Framework)

## 4.1 简介

Scala的集合框架是Scala标准库中最重要和最常用的组件之一。它提供了丰富的数据结构，包括序列（Seq）、集合（Set）和映射（Map），以及对这些数据结构的各种操作。

Scala集合框架的主要特点：
- **不可变和可变集合**：提供了不可变（immutable）和可变（mutable）两种版本的集合
- **丰富的操作**：提供了大量的高阶函数，如map、filter、fold等
- **类型安全**：利用Scala的类型系统确保类型安全
- **性能优化**：针对不同的使用场景进行了性能优化

## 4.2 序列（Seq）

序列是元素的有序集合，可以通过索引访问元素。

### 4.2.1 List（列表）

List是不可变的链表结构，支持高效的头部插入和删除操作。

```scala
// 创建List
val list1 = List(1, 2, 3, 4, 5)
val list2 = 1 :: 2 :: 3 :: Nil

// 基本操作
val head = list1.head        // 获取第一个元素
val tail = list1.tail        // 获取除第一个元素外的其余元素
val appended = list1 :+ 6    // 在末尾添加元素
val prepended = 0 +: list1   // 在开头添加元素
```

### 4.2.2 Vector（向量）

Vector是不可变的索引序列，支持高效的随机访问和更新操作。

```scala
// 创建Vector
val vector = Vector(1, 2, 3, 4, 5)

// 访问元素
val element = vector(2)  // 获取索引为2的元素

// 更新元素（返回新的Vector）
val updated = vector.updated(2, 10)
```

### 4.2.3 Array（数组）

Array是可变的序列，支持高效的随机访问。

```scala
// 创建Array
val array = Array(1, 2, 3, 4, 5)

// 访问和修改元素
val element = array(2)
array(2) = 10
```

## 4.3 集合（Set）

Set是不包含重复元素的集合。

### 4.3.1 不可变Set

```scala
// 创建Set
val set = Set(1, 2, 3, 4, 5)

// 基本操作
val added = set + 6          // 添加元素
val removed = set - 3        // 删除元素
val union = set ++ Set(6, 7) // 并集
val intersect = set & Set(3, 4, 5) // 交集
```

### 4.3.2 可变Set

```scala
import scala.collection.mutable

// 创建可变Set
val mutableSet = mutable.Set(1, 2, 3, 4, 5)

// 修改操作
mutableSet += 6      // 添加元素
mutableSet -= 3      // 删除元素
mutableSet ++= Set(7, 8) // 批量添加
```

## 4.4 映射（Map）

Map是键值对的集合。

### 4.4.1 不可变Map

```scala
// 创建Map
val map = Map("a" -> 1, "b" -> 2, "c" -> 3)

// 基本操作
val value = map("a")           // 获取值
val updated = map + ("d" -> 4) // 添加键值对
val removed = map - "b"        // 删除键值对
```

### 4.4.2 可变Map

```scala
import scala.collection.mutable

// 创建可变Map
val mutableMap = mutable.Map("a" -> 1, "b" -> 2, "c" -> 3)

// 修改操作
mutableMap("d") = 4    // 添加或更新键值对
mutableMap += ("e" -> 5) // 添加键值对
mutableMap -= "b"      // 删除键值对
```

## 4.5 集合操作

Scala集合提供了丰富的高阶函数来操作集合。

### 4.5.1 映射操作

```scala
val numbers = List(1, 2, 3, 4, 5)

// map操作
val doubled = numbers.map(_ * 2)

// flatMap操作
val nested = List(List(1, 2), List(3, 4), List(5, 6))
val flattened = nested.flatMap(identity)
```

### 4.5.2 过滤操作

```scala
val numbers = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// filter操作
val evens = numbers.filter(_ % 2 == 0)

// filterNot操作
val odds = numbers.filterNot(_ % 2 == 0)
```

### 4.5.3 折叠操作

```scala
val numbers = List(1, 2, 3, 4, 5)

// fold操作
val sum = numbers.fold(0)(_ + _)

// foldLeft操作
val sumLeft = numbers.foldLeft(0)(_ + _)

// foldRight操作
val sumRight = numbers.foldRight(0)(_ + _)
```

## 4.6 并行集合

Scala提供了并行集合，可以利用多核处理器并行处理集合元素。

```scala
// 创建并行集合
val parallelList = List(1, 2, 3, 4, 5).par

// 并行操作
val result = parallelList.map(_ * 2)
```

## 4.7 惰性集合

Scala提供了惰性集合，只有在需要时才计算元素。

```scala
// 创建惰性列表
val lazyList = LazyList.from(1).take(10)

// 创建视图
val view = List(1, 2, 3, 4, 5).view.map(_ * 2)
```

## 4.8 性能考虑

在使用Scala集合时，需要注意以下性能考虑：

1. **选择合适的集合类型**：根据使用场景选择List、Vector、Set、Map等
2. **不可变vs可变**：不可变集合更安全但可能有性能开销
3. **批量操作**：使用批量操作而不是循环单个元素
4. **视图和并行集合**：在适当时候使用视图和并行集合提高性能

## 4.9 总结

Scala的集合框架提供了丰富而强大的功能，是Scala编程的基础。掌握集合框架的使用对于编写高效、简洁的Scala代码至关重要。