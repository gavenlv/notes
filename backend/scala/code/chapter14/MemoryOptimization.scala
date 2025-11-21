// 内存优化示例

import java.lang.ref.{Reference, WeakReference, SoftReference, PhantomReference, ReferenceQueue}
import java.util.concurrent.{ConcurrentHashMap, TimeUnit}
import scala.concurrent._
import scala.concurrent.duration._

object MemoryOptimization {
  
  // 1. 对象池模式
  object ObjectPooling {
    import java.util.concurrent.atomic.AtomicInteger
    import java.util.concurrent.ConcurrentLinkedQueue
    
    class ObjectPool[T <: AnyRef](create: () => T, reset: T => Unit = (_: T) => ()) {
      private val pool = new ConcurrentLinkedQueue[T]()
      private val created = new AtomicInteger(0)
      private val borrowed = new AtomicInteger(0)
      private val returned = new AtomicInteger(0)
      
      def borrow(): T = {
        val obj = pool.poll()
        if (obj != null) {
          borrowed.incrementAndGet()
          obj
        } else {
          created.incrementAndGet()
          create()
        }
      }
      
      def returnObject(obj: T): Unit = {
        reset(obj)
        pool.offer(obj)
        returned.incrementAndGet()
      }
      
      def stats(): (Int, Int, Int) = {
        (created.get(), borrowed.get(), returned.get())
      }
      
      def clear(): Unit = {
        pool.clear()
      }
    }
    
    def demonstrateObjectPool(): Unit = {
      println("=== Object Pool Demo ===")
      
      // 字节数组池
      val byteArrayPool = new ObjectPool[Array[Byte]](
        () => Array.ofDim[Byte](1024),
        array => java.util.Arrays.fill(array.asInstanceOf[Array[AnyRef]], null)
      )
      
      // 使用池中的对象
      val objects = (1 to 100).map(_ => byteArrayPool.borrow())
      
      println(s"Pool stats: created=${byteArrayPool.stats()._1}, borrowed=${byteArrayPool.stats()._2}")
      
      // 归还对象
      objects.foreach(byteArrayPool.returnObject)
      
      println(s"Pool stats after return: created=${byteArrayPool.stats()._1}, returned=${byteArrayPool.stats()._3}")
      
      // 再次借用
      val reusedObjects = (1 to 100).map(_ => byteArrayPool.borrow())
      
      println(s"Pool stats after reuse: created=${byteArrayPool.stats()._1}, borrowed=${byteArrayPool.stats()._2}")
      
      // 归还所有对象
      reusedObjects.foreach(byteArrayPool.returnObject)
      
      // 清理池
      byteArrayPool.clear()
    }
  }
  
  // 2. 弱引用示例
  object WeakReferences {
    import java.util.WeakHashMap
    import scala.jdk.CollectionConverters._
    
    def demonstrateWeakReferences(): Unit = {
      println("\n=== Weak References Demo ===")
      
      // 创建大对象
      val largeObject = Array.ofDim[Byte](10 * 1024 * 1024)  // 10MB
      
      // 创建弱引用
      val weakRef = new WeakReference(largeObject)
      
      println(s"Before GC: weakRef.get = ${weakRef.get() != null}")
      
      // 清除强引用
      // largeObject = null  // 实际上不能重新赋值val
      
      System.gc()
      Thread.sleep(1000)
      
      println(s"After GC: weakRef.get = ${weakRef.get() != null}")
      
      // 弱引用Map
      val weakMap = new WeakHashMap[String, Array[Byte]]()
      
      // 添加对象
      weakMap.put("key1", Array.ofDim[Byte](1024))
      weakMap.put("key2", Array.ofDim[Byte](1024))
      
      println(s"Weak map size before GC: ${weakMap.size()}")
      
      System.gc()
      Thread.sleep(1000)
      
      println(s"Weak map size after GC: ${weakMap.size()}")
      
      // 转换为Scala Map使用
      val scalaWeakMap = weakMap.asScala
      println(s"Scala weak map: ${scalaWeakMap.keys}")
    }
    
    def compareMapMemoryUsage(): Unit = {
      println("\n=== Map Memory Usage Comparison ===")
      
      // 普通HashMap
      val regularMap = scala.collection.mutable.Map[String, Array[Byte]]()
      
      for (i <- 1 to 1000) {
        regularMap(s"key$i") = Array.ofDim[Byte](1024)
      }
      
      // WeakHashMap
      val weakMap = new java.util.WeakHashMap[String, Array[Byte]]()
      
      for (i <- 1 to 1000) {
        weakMap.put(s"key$i", Array.ofDim[Byte](1024))
      }
      
      // 获取内存使用情况
      val runtime = Runtime.getRuntime
      
      System.gc()
      Thread.sleep(1000)
      val beforeWeak = runtime.totalMemory() - runtime.freeMemory()
      
      // 清除WeakHashMap中的引用
      for (i <- 1 to 1000) {
        weakMap.remove(s"key$i")
      }
      
      System.gc()
      Thread.sleep(1000)
      val afterWeak = runtime.totalMemory() - runtime.freeMemory()
      
      println(s"Memory released by WeakHashMap: ${(beforeWeak - afterWeak) / 1024} KB")
      
      // 清除普通Map
      regularMap.clear()
      
      System.gc()
      Thread.sleep(1000)
      val afterRegular = runtime.totalMemory() - runtime.freeMemory()
      
      println(s"Memory released by regular Map: ${(beforeWeak - afterRegular) / 1024} KB")
    }
  }
  
  // 3. 软引用示例
  object SoftReferences {
    def demonstrateSoftReferences(): Unit = {
      println("\n=== Soft References Demo ===")
      
      // 创建软引用
      val softRef = new SoftReference(Array.ofDim[Byte](10 * 1024 * 1024))
      
      println(s"Before memory pressure: softRef.get = ${softRef.get() != null}")
      
      // 创建内存压力
      val memoryHogs = Array.fill(50)(Array.ofDim[Byte](10 * 1024 * 1024))
      
      System.gc()
      Thread.sleep(1000)
      
      println(s"After memory pressure: softRef.get = ${softRef.get() != null}")
      
      // 清理内存
      memoryHogs(0) = null  // 释放一些内存
      
      System.gc()
      Thread.sleep(1000)
      
      println(s"After releasing some memory: softRef.get = ${softRef.get() != null}")
    }
  }
  
  // 4. 虚引用示例
  object PhantomReferences {
    def demonstratePhantomReferences(): Unit = {
      println("\n=== Phantom References Demo ===")
      
      // 创建引用队列
      val refQueue = new ReferenceQueue[Array[Byte]]()
      
      // 创建虚引用
      val largeObject = Array.ofDim[Byte](5 * 1024 * 1024)
      val phantomRef = new PhantomReference(largeObject, refQueue)
      
      println(s"Phantom reference created: ${phantumRef != null}")
      println(s"Phantom reference get: ${phantomRef.get()}")
      
      // 清除强引用
      // largeObject = null  // 实际上不能重新赋值val
      
      System.gc()
      Thread.sleep(1000)
      
      // 检查引用队列
      val ref = refQueue.poll()
      println(s"Reference in queue: ${ref != null}")
      println(s"Reference equals phantomRef: ${ref == phantomRef}")
    }
  }
  
  // 5. 内存高效的数据结构
  object MemoryEfficientStructures {
    // 使用原始类型集合
    def demonstratePrimitiveCollections(): Unit = {
      println("\n=== Primitive Collections Demo ===")
      
      // 使用Array[Int]而不是List[Int]
      val array = Array.ofDim[Int](1000000)
      
      for (i <- array.indices) {
        array(i) = i
      }
      
      // 使用Java的原始类型集合
      import java.util.ArrayList
      val javaArrayList = new java.util.ArrayList[Int]()
      
      for (i <- 1 to 1000000) {
        javaArrayList.add(i)
      }
      
      println(s"Array length: ${array.length}")
      println(s"Java array list size: ${javaArrayList.size()}")
      
      // 比较内存使用
      val runtime = Runtime.getRuntime
      
      System.gc()
      val before = runtime.totalMemory() - runtime.freeMemory()
      
      // 装箱的Integers
      val boxedArray = Array.fill(1000000)(Integer.valueOf(1))
      
      System.gc()
      val afterBoxed = runtime.totalMemory() - runtime.freeMemory()
      
      // 原始ints
      val primitiveArray = Array.fill(1000000)(1)
      
      System.gc()
      val afterPrimitive = runtime.totalMemory() - runtime.freeMemory()
      
      println(s"Boxed integers memory: ${(afterBoxed - before) / 1024} KB")
      println(s"Primitive integers memory: ${(afterPrimitive - afterBoxed) / 1024} KB")
      println(s"Memory savings: ${((afterBoxed - afterPrimitive) / 1024)} KB")
    }
    
    // 使用更紧凑的集合实现
    def demonstrateCompactCollections(): Unit = {
      println("\n=== Compact Collections Demo ===")
      
      // Vector比List更节省内存
      val list = List.range(0, 1000000)
      val vector = Vector.range(0, 1000000)
      
      // 获取内存使用情况
      val runtime = Runtime.getRuntime
      
      System.gc()
      val beforeList = runtime.totalMemory() - runtime.freeMemory()
      
      val listCopy = list.map(_ * 2)
      
      System.gc()
      val afterList = runtime.totalMemory() - runtime.freeMemory()
      
      System.gc()
      val beforeVector = runtime.totalMemory() - runtime.freeMemory()
      
      val vectorCopy = vector.map(_ * 2)
      
      System.gc()
      val afterVector = runtime.totalMemory() - runtime.freeMemory()
      
      println(s"List memory usage: ${(afterList - beforeList) / 1024} KB")
      println(s"Vector memory usage: ${(afterVector - beforeVector) / 1024} KB")
    }
    
    // 使用flyweight模式减少对象数量
    object FlyweightPattern {
      sealed trait Color {
        def name: String
        def rgb: (Int, Int, Int)
      }
      
      object Color {
        case object Red extends Color {
          val name = "Red"
          val rgb = (255, 0, 0)
        }
        
        case object Green extends Color {
          val name = "Green"
          val rgb = (0, 255, 0)
        }
        
        case object Blue extends Color {
          val name = "Blue"
          val rgb = (0, 0, 255)
        }
        
        def fromString(s: String): Color = s.toLowerCase match {
          case "red" => Red
          case "green" => Green
          case "blue" => Blue
          case _ => throw new IllegalArgumentException(s"Unknown color: $s")
        }
      }
      
      def demonstrateFlyweight(): Unit = {
        // 使用共享的颜色对象而不是每次创建新对象
        val pixels = Array.fill(1000000)(Color.Red)
        println(s"Created ${pixels.length} pixels with shared color objects")
        
        // 比较使用新对象
        case class CustomColor(name: String, rgb: (Int, Int, Int))
        val customPixels = Array.fill(1000000)(CustomColor("Red", (255, 0, 0)))
        println(s"Created ${customPixels.length} pixels with custom color objects")
      }
    }
  }
  
  // 6. 内存泄漏检测
  object MemoryLeakDetection {
    // 闭包导致内存泄漏
    def closureLeak(): () => Unit = {
      val largeArray = Array.ofDim[Byte](10 * 1024 * 1024) // 10MB
      
      // 闭包持有largeArray的引用
      () => {
        println(s"Large array length: ${largeArray.length}")
      }
    }
    
    // 使用弱引用避免内存泄漏
    def avoidClosureLeak(): () => Unit = {
      val largeArray = Array.ofDim[Byte](10 * 1024 * 1024)
      val weakRef = new WeakReference(largeArray)
      
      () => {
        val array = weakRef.get()
        if (array != null) {
          println(s"Large array length: ${array.length}")
        } else {
          println("Array has been garbage collected")
        }
      }
    }
    
    def demonstrateClosureLeak(): Unit = {
      println("\n=== Closure Leak Demo ===")
      
      val runtime = Runtime.getRuntime
      
      // 创建闭包
      val leakyClosure = closureLeak()
      
      System.gc()
      val before = runtime.totalMemory() - runtime.freeMemory()
      
      // 清除引用
      // leakyClosure = null  // 实际上不能重新赋值val
      
      System.gc()
      Thread.sleep(1000)
      val after = runtime.totalMemory() - runtime.freeMemory()
      
      println(s"Memory before: ${before / 1024} KB")
      println(s"Memory after: ${after / 1024} KB")
      
      // 使用弱引用
      val nonLeakyClosure = avoidClosureLeak()
      
      System.gc()
      val beforeWeak = runtime.totalMemory() - runtime.freeMemory()
      
      // 清除引用
      // nonLeakyClosure = null  // 实际上不能重新赋值val
      
      System.gc()
      Thread.sleep(1000)
      val afterWeak = runtime.totalMemory() - runtime.freeMemory()
      
      println(s"Memory with weak ref before: ${beforeWeak / 1024} KB")
      println(s"Memory with weak ref after: ${afterWeak / 1024} KB")
    }
    
    // 集合持有对象导致内存泄漏
    def collectionLeak(): Unit = {
      println("\n=== Collection Leak Demo ===")
      
      import scala.collection.mutable
      
      val cache = mutable.Map[String, Any]()
      
      // 添加大量对象到缓存
      for (i <- 1 to 1000) {
        val largeObject = Array.ofDim[Byte](1024)
        cache(s"key$i") = largeObject
      }
      
      println(s"Cache size: ${cache.size}")
      
      // 手动清理
      cache.clear()
      System.gc()
      println("Cache cleared and garbage collected")
    }
    
    // 使用弱引用集合避免内存泄漏
    def avoidCollectionLeak(): Unit = {
      println("\n=== Weak Collection Demo ===")
      
      import java.util.WeakHashMap
      import scala.jdk.CollectionConverters._
      
      val weakCache = new WeakHashMap[String, Array[Byte]]()
      
      // 添加对象到弱引用缓存
      for (i <- 1 to 1000) {
        val largeObject = Array.ofDim[Byte](1024)
        weakCache.put(s"key$i", largeObject)
      }
      
      println(s"Weak cache size: ${weakCache.size()}")
      
      System.gc()
      Thread.sleep(1000)
      println(s"Weak cache size after GC: ${weakCache.size()}")
    }
  }
  
  // 7. 内存分析工具
  def analyzeMemoryUsage(): Unit = {
    println("\n=== Memory Analysis Demo ===")
    
    val runtime = Runtime.getRuntime
    
    // 获取内存信息
    val totalMemory = runtime.totalMemory()
    val freeMemory = runtime.freeMemory()
    val usedMemory = totalMemory - freeMemory
    val maxMemory = runtime.maxMemory()
    
    println(s"Max memory: ${maxMemory / (1024 * 1024)} MB")
    println(s"Total memory: ${totalMemory / (1024 * 1024)} MB")
    println(s"Used memory: ${usedMemory / (1024 * 1024)} MB")
    println(s"Free memory: ${freeMemory / (1024 * 1024)} MB")
    println(s"Memory usage: ${(usedMemory.toDouble / maxMemory) * 100}%")
    
    // 测试内存分配
    System.gc()
    Thread.sleep(100)
    val before = runtime.totalMemory() - runtime.freeMemory()
    
    // 分配内存
    val arrays = Array.fill(100)(Array.ofDim[Byte](1024 * 1024)) // 100MB
    
    val after = runtime.totalMemory() - runtime.freeMemory()
    
    println(s"Memory allocated: ${(after - before) / (1024 * 1024)} MB")
    println(s"Expected: 100 MB")
    
    // 释放内存
    for (i <- arrays.indices) {
      arrays(i) = null
    }
    
    System.gc()
    Thread.sleep(1000)
    val afterGC = runtime.totalMemory() - runtime.freeMemory()
    
    println(s"Memory after GC: ${afterGC / (1024 * 1024)} MB")
    println(s"Memory released: ${((after - afterGC) / (1024 * 1024))} MB")
  }
  
  def runAll(): Unit = {
    ObjectPooling.demonstrateObjectPool()
    WeakReferences.demonstrateWeakReferences()
    WeakReferences.compareMapMemoryUsage()
    SoftReferences.demonstrateSoftReferences()
    PhantomReferences.demonstratePhantomReferences()
    MemoryEfficientStructures.demonstratePrimitiveCollections()
    MemoryEfficientStructures.demonstrateCompactCollections()
    MemoryEfficientStructures.FlyweightPattern.demonstrateFlyweight()
    MemoryLeakDetection.demonstrateClosureLeak()
    MemoryLeakDetection.collectionLeak()
    MemoryLeakDetection.avoidCollectionLeak()
    analyzeMemoryUsage()
  }
}