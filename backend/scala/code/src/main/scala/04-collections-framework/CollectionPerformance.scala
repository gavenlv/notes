/**
 * CollectionPerformance.scala
 * 
 * 演示Scala集合性能调优的方法
 * 包括集合选择指南、性能基准测试和内存使用优化
 */

// 集合性能测试工具
object CollectionPerformanceTest {
  def timeOperation[T](operation: => T): (T, Long) = {
    val start = System.nanoTime()
    val result = operation
    val end = System.nanoTime()
    (result, (end - start) / 1000000)  // 转换为毫秒
  }
  
  def memoryUsage[T](operation: => T): (T, Long) = {
    val runtime = Runtime.getRuntime
    // 请求垃圾回收以获得更准确的内存使用情况
    runtime.gc()
    val before = runtime.totalMemory() - runtime.freeMemory()
    val result = operation
    runtime.gc()
    val after = runtime.totalMemory() - runtime.freeMemory()
    (result, after - before)
  }
}

// 不同集合类型的性能对比
object CollectionTypePerformanceDemo {
  def run(): Unit = {
    println("=== 不同集合类型的性能对比 ===")
    
    val testSize = 100000
    
    // List性能测试
    println("\n1. List性能测试:")
    val list = (1 to testSize).toList
    
    val (_, listAccessTime) = CollectionPerformanceTest.timeOperation {
      list(testSize / 2)  // 访问中间元素
    }
    println(s"  访问中间元素耗时: ${listAccessTime}ms")
    
    val (_, listPrependTime) = CollectionPerformanceTest.timeOperation {
      0 :: list  // 在头部添加元素
    }
    println(s"  在头部添加元素耗时: ${listPrependTime}ms")
    
    // Vector性能测试
    println("\n2. Vector性能测试:")
    val vector = (1 to testSize).toVector
    
    val (_, vectorAccessTime) = CollectionPerformanceTest.timeOperation {
      vector(testSize / 2)  // 访问中间元素
    }
    println(s"  访问中间元素耗时: ${vectorAccessTime}ms")
    
    val (_, vectorPrependTime) = CollectionPerformanceTest.timeOperation {
      0 +: vector  // 在头部添加元素
    }
    println(s"  在头部添加元素耗时: ${vectorPrependTime}ms")
    
    // ArrayBuffer性能测试
    println("\n3. ArrayBuffer性能测试:")
    import scala.collection.mutable.ArrayBuffer
    val arrayBuffer = ArrayBuffer((1 to testSize): _*)
    
    val (_, bufferAccessTime) = CollectionPerformanceTest.timeOperation {
      arrayBuffer(testSize / 2)  // 访问中间元素
    }
    println(s"  访问中间元素耗时: ${bufferAccessTime}ms")
    
    val (_, bufferUpdateTime) = CollectionPerformanceTest.timeOperation {
      arrayBuffer(testSize / 2) = -1  // 更新中间元素
    }
    println(s"  更新中间元素耗时: ${bufferUpdateTime}ms")
    
    // Array性能测试
    println("\n4. Array性能测试:")
    val array = (1 to testSize).toArray
    
    val (_, arrayAccessTime) = CollectionPerformanceTest.timeOperation {
      array(testSize / 2)  // 访问中间元素
    }
    println(s"  访问中间元素耗时: ${arrayAccessTime}ms")
    
    val (_, arrayUpdateTime) = CollectionPerformanceTest.timeOperation {
      array(testSize / 2) = -1  // 更新中间元素
    }
    println(s"  更新中间元素耗时: ${arrayUpdateTime}ms")
  }
}

// Set类型性能对比
object SetPerformanceDemo {
  def run(): Unit = {
    println("\n=== Set类型性能对比 ===")
    
    val testSize = 100000
    
    // 不可变Set
    println("\n1. 不可变Set性能:")
    val immutableSet = (1 to testSize).toSet
    
    val (_, immutableContainsTime) = CollectionPerformanceTest.timeOperation {
      immutableSet.contains(testSize / 2)
    }
    println(s"  包含检查耗时: ${immutableContainsTime}ms")
    
    val (_, immutableAddTime) = CollectionPerformanceTest.timeOperation {
      immutableSet + (testSize + 1)
    }
    println(s"  添加元素耗时: ${immutableAddTime}ms")
    
    // 可变HashSet
    println("\n2. 可变HashSet性能:")
    import scala.collection.mutable.HashSet
    val mutableSet = HashSet((1 to testSize): _*)
    
    val (_, mutableContainsTime) = CollectionPerformanceTest.timeOperation {
      mutableSet.contains(testSize / 2)
    }
    println(s"  包含检查耗时: ${mutableContainsTime}ms")
    
    val (_, mutableAddTime) = CollectionPerformanceTest.timeOperation {
      mutableSet += (testSize + 1)
    }
    println(s"  添加元素耗时: ${mutableAddTime}ms")
    
    // BitSet性能
    println("\n3. BitSet性能:")
    import scala.collection.immutable.BitSet
    val bitSet = BitSet((1 to 10000 by 2): _*)  // 奇数集合
    
    val (_, bitSetContainsTime) = CollectionPerformanceTest.timeOperation {
      bitSet.contains(5001)
    }
    println(s"  包含检查耗时: ${bitSetContainsTime}ms")
    
    val (_, bitSetAddTime) = CollectionPerformanceTest.timeOperation {
      bitSet + 10000
    }
    println(s"  添加元素耗时: ${bitSetAddTime}ms")
  }
}

// Map类型性能对比
object MapPerformanceDemo {
  def run(): Unit = {
    println("\n=== Map类型性能对比 ===")
    
    val testSize = 100000
    
    // 不可变Map
    println("\n1. 不可变Map性能:")
    val immutableMap = (1 to testSize).map(i => s"key$i" -> i).toMap
    
    val (_, immutableGetTime) = CollectionPerformanceTest.timeOperation {
      immutableMap.get(s"key${testSize / 2}")
    }
    println(s"  获取值耗时: ${immutableGetTime}ms")
    
    val (_, immutableAddTime) = CollectionPerformanceTest.timeOperation {
      immutableMap + ("newKey" -> (testSize + 1))
    }
    println(s"  添加键值对耗时: ${immutableAddTime}ms")
    
    // 可变HashMap
    println("\n2. 可变HashMap性能:")
    import scala.collection.mutable.HashMap
    val mutableMap = HashMap((1 to testSize).map(i => s"key$i" -> i): _*)
    
    val (_, mutableGetTime) = CollectionPerformanceTest.timeOperation {
      mutableMap.get(s"key${testSize / 2}")
    }
    println(s"  获取值耗时: ${mutableGetTime}ms")
    
    val (_, mutableAddTime) = CollectionPerformanceTest.timeOperation {
      mutableMap += ("newKey" -> (testSize + 1))
    }
    println(s"  添加键值对耗时: ${mutableAddTime}ms")
    
    // SortedMap性能
    println("\n3. SortedMap性能:")
    import scala.collection.immutable.SortedMap
    val sortedMap = SortedMap((1 to testSize).map(i => s"key$i" -> i): _*)
    
    val (_, sortedGetTime) = CollectionPerformanceTest.timeOperation {
      sortedMap.get(s"key${testSize / 2}")
    }
    println(s"  获取值耗时: ${sortedGetTime}ms")
  }
}

// 内存使用优化示例
object MemoryOptimizationDemo {
  def run(): Unit = {
    println("\n=== 内存使用优化示例 ===")
    
    // 1. 使用View避免中间集合
    println("\n1. 使用View优化内存:")
    val largeList = (1 to 1000000).toList
    
    // 不使用View - 创建多个中间集合
    val (_, withoutViewMemory) = CollectionPerformanceTest.memoryUsage {
      largeList
        .map(_ + 1)
        .map(_ * 2)
        .filter(_ % 3 == 0)
        .take(1000)
    }
    
    // 使用View - 避免中间集合
    val (_, withViewMemory) = CollectionPerformanceTest.memoryUsage {
      largeList
        .view
        .map(_ + 1)
        .map(_ * 2)
        .filter(_ % 3 == 0)
        .take(1000)
        .toList
    }
    
    println(s"  不使用View的内存使用: ${withoutViewMemory / 1024}KB")
    println(s"  使用View的内存使用: ${withViewMemory / 1024}KB")
    println(f"  内存节省: ${(withoutViewMemory - withViewMemory).toDouble / withoutViewMemory * 100}%.2f%%")
    
    // 2. 选择合适的数据结构
    println("\n2. 数据结构选择优化:")
    
    // 使用List存储大量元素
    val (_, listMemory) = CollectionPerformanceTest.memoryUsage {
      (1 to 10000).toList
    }
    
    // 使用Vector存储大量元素
    val (_, vectorMemory) = CollectionPerformanceTest.memoryUsage {
      (1 to 10000).toVector
    }
    
    // 使用Array存储大量元素
    val (_, arrayMemory) = CollectionPerformanceTest.memoryUsage {
      (1 to 10000).toArray
    }
    
    println(s"  List内存使用: ${listMemory / 1024}KB")
    println(s"  Vector内存使用: ${vectorMemory / 1024}KB")
    println(s"  Array内存使用: ${arrayMemory / 1024}KB")
  }
}

// 集合选择指南示例
object CollectionSelectionGuideDemo {
  def run(): Unit = {
    println("\n=== 集合选择指南示例 ===")
    
    println("""
    集合选择指南:
    
    1. 序列(Seq)选择:
       - List: 适用于头部频繁添加/删除，不适用于随机访问
       - Vector: 适用于随机访问和更新，性能均衡
       - Array/ArrayBuffer: 适用于频繁的随机访问和更新
    
    2. 集合(Set)选择:
       - Set: 适用于去重和包含检查
       - HashSet: 适用于频繁的添加/删除操作
       - BitSet: 适用于小整数集合，内存效率高
    
    3. 映射(Map)选择:
       - Map: 适用于不可变键值对映射
       - HashMap: 适用于频繁的键值对操作
       - SortedMap: 适用于需要排序的键值对
    
    4. 性能考虑:
       - 避免在循环中创建大型集合
       - 使用View进行链式操作
       - 根据访问模式选择合适的数据结构
       - 考虑内存使用和垃圾回收
    """)
    
    // 实际应用场景演示
    println("实际应用场景演示:")
    
    // 场景1: 频繁在头部添加元素 - 使用List
    def prependScenario(): Unit = {
      println("\n场景1: 频繁在头部添加元素")
      val elements = (1 to 1000).toList
      var list = List.empty[Int]
      
      val (_, time) = CollectionPerformanceTest.timeOperation {
        elements.foreach(e => list = e :: list)
      }
      
      println(s"  使用List耗时: ${time}ms")
    }
    
    // 场景2: 频繁随机访问 - 使用Vector
    def randomAccessScenario(): Unit = {
      println("\n场景2: 频繁随机访问")
      val vector = (1 to 10000).toVector
      val indices = (1 to 1000).map(_ => scala.util.Random.nextInt(10000))
      
      val (_, vectorTime) = CollectionPerformanceTest.timeOperation {
        indices.map(vector(_)).sum
      }
      
      val list = (1 to 10000).toList
      val (_, listTime) = CollectionPerformanceTest.timeOperation {
        indices.map(list(_)).sum
      }
      
      println(s"  Vector随机访问耗时: ${vectorTime}ms")
      println(s"  List随机访问耗时: ${listTime}ms")
    }
    
    // 场景3: 频繁查找元素 - 使用HashSet
    def lookupScenario(): Unit = {
      println("\n场景3: 频繁查找元素")
      val elements = (1 to 10000).toList
      val set = elements.toSet
      import scala.collection.mutable.HashSet
      val hashSet = HashSet(elements: _*)
      
      val searchElements = (1 to 1000).map(_ => scala.util.Random.nextInt(10000) + 1)
      
      val (_, setTime) = CollectionPerformanceTest.timeOperation {
        searchElements.count(set.contains)
      }
      
      val (_, hashSetTime) = CollectionPerformanceTest.timeOperation {
        searchElements.count(hashSet.contains)
      }
      
      println(s"  Set查找耗时: ${setTime}ms")
      println(s"  HashSet查找耗时: ${hashSetTime}ms")
    }
    
    prependScenario()
    randomAccessScenario()
    lookupScenario()
  }
}

// 主程序入口
object CollectionPerformanceDemo extends App {
  CollectionTypePerformanceDemo.run()
  SetPerformanceDemo.run()
  MapPerformanceDemo.run()
  MemoryOptimizationDemo.run()
  CollectionSelectionGuideDemo.run()
}