/**
 * ParallelCollections.scala
 * 
 * 演示Scala并行集合的使用方法
 * 包括并行集合的创建、使用和性能对比
 */

import scala.collection.parallel.CollectionConverters._

// 并行集合基础示例
object ParallelCollectionsBasicsDemo {
  def run(): Unit = {
    println("=== 并行集合基础示例 ===")
    
    // 创建大型数据集
    val largeList = (1 to 1000000).toList
    val largeVector = (1 to 1000000).toVector
    
    // 转换为并行集合
    val parallelList = largeList.par
    val parallelVector = largeVector.par
    
    println(s"原始List大小: ${largeList.size}")
    println(s"并行List大小: ${parallelList.size}")
    println(s"原始Vector大小: ${largeVector.size}")
    println(s"并行Vector大小: ${parallelVector.size}")
    
    // 基本操作
    val parMapResult = parallelList.map(_ * 2)
    println(s"并行map操作结果大小: ${parMapResult.size}")
    
    val parFilterResult = parallelList.filter(_ % 2 == 0)
    println(s"并行filter操作结果大小: ${parFilterResult.size}")
  }
}

// 并行集合性能对比示例
object ParallelPerformanceDemo {
  def timeOperation[T](operation: => T): (T, Long) = {
    val start = System.currentTimeMillis()
    val result = operation
    val end = System.currentTimeMillis()
    (result, end - start)
  }
  
  def run(): Unit = {
    println("\n=== 并行集合性能对比示例 ===")
    
    // 创建中等大小的数据集
    val mediumList = (1 to 100000).toList
    
    // 串行操作
    val (serialResult, serialTime) = timeOperation {
      mediumList.map(x => Thread.sleep(0); x * x).filter(_ % 2 == 0).sum
    }
    
    // 并行操作
    val (parallelResult, parallelTime) = timeOperation {
      mediumList.par.map(x => Thread.sleep(0); x * x).filter(_ % 2 == 0).sum
    }
    
    println(s"串行操作耗时: ${serialTime}ms, 结果: $serialResult")
    println(s"并行操作耗时: ${parallelTime}ms, 结果: $parallelResult")
    println(f"性能提升: ${serialTime.toDouble / parallelTime.toDouble}%.2fx")
  }
}

// 并行集合的副作用示例
object ParallelSideEffectsDemo {
  def run(): Unit = {
    println("\n=== 并行集合的副作用示例 ===")
    
    import scala.collection.mutable.ListBuffer
    
    val results = ListBuffer[Int]()
    
    // 并行操作中的副作用可能导致问题
    val parallelList = (1 to 100).par
    
    // 不推荐的做法：在并行操作中修改外部状态
    parallelList.foreach { x =>
      results += x * 2  // 可能导致竞态条件
    }
    
    println(s"并行操作后的结果数量: ${results.size}")
    println(s"前10个结果: ${results.take(10).toList}")
    
    // 推荐的做法：使用纯函数操作
    val pureResult = parallelList.map(_ * 2).seq.toList.sorted
    println(s"纯函数操作结果数量: ${pureResult.size}")
    println(s"前10个结果: ${pureResult.take(10)}")
  }
}

// 并行集合的聚合操作示例
object ParallelAggregationDemo {
  def run(): Unit = {
    println("\n=== 并行集合的聚合操作示例 ===")
    
    val numbers = (1 to 100000).par
    
    // 并行求和
    val sum = numbers.sum
    println(s"并行求和结果: $sum")
    
    // 并行最大值
    val max = numbers.max
    println(s"并行最大值: $max")
    
    // 并行最小值
    val min = numbers.min
    println(s"并行最小值: $min")
    
    // 并行计数
    val count = numbers.count(_ % 2 == 0)
    println(s"偶数个数: $count")
    
    // 并行折叠操作
    val foldResult = numbers.fold(0)(_ + _)
    println(s"并行fold结果: $foldResult")
    
    // 并行reduce操作
    val reduceResult = numbers.reduce(_ + _)
    println(s"并行reduce结果: $reduceResult")
  }
}

// 并行集合的分组操作示例
object ParallelGroupingDemo {
  def run(): Unit = {
    println("\n=== 并行集合的分组操作示例 ===")
    
    case class Employee(name: String, department: String, salary: Double)
    
    val employees = (1 to 10000).map { i =>
      Employee(
        s"Employee$i",
        if (i % 3 == 0) "Engineering" else if (i % 3 == 1) "Marketing" else "Sales",
        30000 + (i % 50) * 1000
      )
    }.par
    
    // 并行分组
    val groupedByDept = employees.groupBy(_.department)
    println("各部门员工数量:")
    groupedByDept.foreach { case (dept, emps) =>
      println(s"  $dept: ${emps.size}")
    }
    
    // 并行聚合
    val avgSalaries = employees.aggregate(Map.empty[String, (Double, Int)])(
      // 序列阶段：累加每个部门的工资总和和人数
      (acc, emp) => {
        val (sum, count) = acc.getOrElse(emp.department, (0.0, 0))
        acc + (emp.department -> (sum + emp.salary, count + 1))
      },
      // 组合阶段：合并不同分区的结果
      (acc1, acc2) => {
        acc2.foldLeft(acc1) { case (acc, (dept, (sum2, count2))) =>
          val (sum1, count1) = acc.getOrElse(dept, (0.0, 0))
          acc + (dept -> (sum1 + sum2, count1 + count2))
        }
      }
    ).mapValues { case (sum, count) => sum / count }
    
    println("\n各部门平均工资:")
    avgSalaries.foreach { case (dept, avgSalary) =>
      println(f"  $dept: $$${avgSalary}%.2f")
    }
  }
}

// 并行集合的注意事项示例
object ParallelConsiderationsDemo {
  def run(): Unit = {
    println("\n=== 并行集合的注意事项示例 ===")
    
    // 1. 小数据集不适合并行处理
    val smallList = (1 to 10).toList
    val parallelSmall = smallList.par
    
    println("小数据集(10个元素)的并行处理可能不如串行处理高效")
    
    // 2. 数据结构的选择影响并行性能
    val arrayList = (1 to 100000).toArray.par
    val vectorList = (1 to 100000).toVector.par
    
    val (_, arrayTime) = timeOperation(arrayList.map(_ * 2).sum)
    val (_, vectorTime) = timeOperation(vectorList.map(_ * 2).sum)
    
    println(s"Array并行处理时间: ${arrayTime}ms")
    println(s"Vector并行处理时间: ${vectorTime}ms")
    
    // 3. 并行级别的控制
    println(s"默认并行级别: ${parallelList.tasksupport.parallelismLevel}")
    
    // 4. 线程安全的重要性
    import java.util.concurrent.atomic.AtomicInteger
    val atomicCounter = new AtomicInteger(0)
    
    (1 to 1000).par.foreach { _ =>
      atomicCounter.incrementAndGet()  // 原子操作
    }
    
    println(s"原子计数器最终值: ${atomicCounter.get()}")
  }
}

// 主程序入口
object ParallelCollectionsDemo extends App {
  ParallelCollectionsBasicsDemo.run()
  ParallelPerformanceDemo.run()
  ParallelSideEffectsDemo.run()
  ParallelAggregationDemo.run()
  ParallelGroupingDemo.run()
  ParallelConsiderationsDemo.run()
}