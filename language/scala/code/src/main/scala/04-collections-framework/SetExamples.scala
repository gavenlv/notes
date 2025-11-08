/**
 * SetExamples.scala
 * 
 * 演示Scala中集合（Set）的使用方法
 * 包括不可变Set、可变Set、SortedSet等
 */

// 不可变Set示例
object ImmutableSetDemo {
  def run(): Unit = {
    println("=== 不可变Set示例 ===")
    
    // 创建Set
    val set1 = Set(1, 2, 3, 4, 5)
    val set2 = Set(4, 5, 6, 7, 8)
    val emptySet = Set.empty[String]
    
    println(s"set1: $set1")
    println(s"set2: $set2")
    println(s"emptySet: $emptySet")
    
    // 基本操作
    println(s"set1大小: ${set1.size}")
    println(s"set1是否包含3: ${set1.contains(3)}")
    println(s"set1是否为空: ${set1.isEmpty}")
    
    // 添加元素（返回新Set）
    val newSet = set1 + 6
    println(s"添加元素6: $newSet")
    
    // 删除元素
    val removedSet = set1 - 3
    println(s"删除元素3: $removedSet")
    
    // 集合运算
    println(s"set1与set2的并集: ${set1.union(set2)}")
    println(s"set1与set2的交集: ${set1.intersect(set2)}")
    println(s"set1与set2的差集: ${set1.diff(set2)}")
    
    // 子集判断
    val subset = Set(1, 2)
    println(s"subset是否为set1的子集: ${subset.subsetOf(set1)}")
  }
}

// 可变Set示例
object MutableSetDemo {
  def run(): Unit = {
    println("\n=== 可变Set示例 ===")
    
    import scala.collection.mutable.Set
    
    // 创建可变Set
    val mutableSet = Set(1, 2, 3, 4, 5)
    
    println(s"初始mutableSet: $mutableSet")
    
    // 添加元素（直接修改原Set）
    mutableSet += 6
    println(s"添加元素6后: $mutableSet")
    
    // 添加多个元素
    mutableSet ++= List(7, 8, 9)
    println(s"添加多个元素后: $mutableSet")
    
    // 删除元素
    mutableSet -= 3
    println(s"删除元素3后: $mutableSet")
    
    // 删除多个元素
    mutableSet --= List(1, 2)
    println(s"删除多个元素后: $mutableSet")
    
    // 清空Set
    mutableSet.clear()
    println(s"清空后: $mutableSet")
  }
}

// SortedSet示例
object SortedSetDemo {
  def run(): Unit = {
    println("\n=== SortedSet示例 ===")
    
    import scala.collection.immutable.SortedSet
    
    // 创建SortedSet
    val sortedSet = SortedSet(5, 2, 8, 1, 9, 3)
    
    println(s"sortedSet: $sortedSet")  // 自动排序
    
    // 添加元素
    val newSortedSet = sortedSet + 0
    println(s"添加元素0后: $newSortedSet")
    
    // 删除元素
    val removedSortedSet = sortedSet - 5
    println(s"删除元素5后: $removedSortedSet")
    
    // 获取边界元素
    println(s"最小元素: ${sortedSet.first}")
    println(s"最大元素: ${sortedSet.last}")
    
    // 范围操作
    println(s"小于5的元素: ${sortedSet.rangeUntil(5)}")
    println(s"大于等于5的元素: ${sortedSet.rangeFrom(5)}")
  }
}

// BitSet示例
object BitSetDemo {
  def run(): Unit = {
    println("\n=== BitSet示例 ===")
    
    import scala.collection.immutable.BitSet
    
    // 创建BitSet
    val bitSet1 = BitSet(1, 3, 5, 7, 9)
    val bitSet2 = BitSet(2, 4, 6, 8, 10)
    
    println(s"bitSet1: $bitSet1")
    println(s"bitSet2: $bitSet2")
    
    // 集合运算
    println(s"bitSet1与bitSet2的并集: ${bitSet1.union(bitSet2)}")
    println(s"bitSet1与bitSet2的交集: ${bitSet1.intersect(bitSet2)}")
    
    // 添加元素
    val newBitSet = bitSet1 + 11
    println(s"添加元素11后: $newBitSet")
    
    // 删除元素
    val removedBitSet = bitSet1 - 3
    println(s"删除元素3后: $removedBitSet")
  }
}

// HashSet示例（可变）
object HashSetDemo {
  def run(): Unit = {
    println("\n=== HashSet示例 ===")
    
    import scala.collection.mutable.HashSet
    
    // 创建HashSet
    val hashSet = HashSet("apple", "banana", "orange")
    
    println(s"hashSet: $hashSet")
    
    // 添加元素
    hashSet += "grape"
    println(s"添加grape后: $hashSet")
    
    // 删除元素
    hashSet -= "banana"
    println(s"删除banana后: $hashSet")
    
    // 批量操作
    hashSet ++= List("kiwi", "mango")
    println(s"批量添加后: $hashSet")
    
    // 查找操作
    println(s"是否包含apple: ${hashSet.contains("apple")}")
    println(s"HashSet大小: ${hashSet.size}")
  }
}

// 主程序入口
object SetExamplesDemo extends App {
  ImmutableSetDemo.run()
  MutableSetDemo.run()
  SortedSetDemo.run()
  BitSetDemo.run()
  HashSetDemo.run()
}