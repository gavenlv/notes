/**
 * MapExamples.scala
 * 
 * 演示Scala中映射（Map）的使用方法
 * 包括不可变Map、可变Map、SortedMap等
 */

// 不可变Map示例
object ImmutableMapDemo {
  def run(): Unit = {
    println("=== 不可变Map示例 ===")
    
    // 创建Map
    val map1 = Map("a" -> 1, "b" -> 2, "c" -> 3)
    val map2 = Map(("x", 10), ("y", 20), ("z", 30))
    val emptyMap = Map.empty[String, Int]
    
    println(s"map1: $map1")
    println(s"map2: $map2")
    println(s"emptyMap: $emptyMap")
    
    // 基本操作
    println(s"map1大小: ${map1.size}")
    println(s"map1是否包含键'a': ${map1.contains("a")}")
    println(s"map1中键'b'的值: ${map1("b")}")
    
    // 安全获取值
    println(s"安全获取存在的键: ${map1.get("a")}")
    println(s"安全获取不存在的键: ${map1.get("d")}")
    
    // 添加键值对（返回新Map）
    val newMap = map1 + ("d" -> 4)
    println(s"添加键值对'd'->4: $newMap")
    
    // 更新键值对
    val updatedMap = map1 + ("b" -> 20)
    println(s"更新键'b'的值为20: $updatedMap")
    
    // 删除键值对
    val removedMap = map1 - "b"
    println(s"删除键'b': $removedMap")
    
    // 批量操作
    val batchAddedMap = map1 ++ Map("d" -> 4, "e" -> 5)
    println(s"批量添加键值对: $batchAddedMap")
    
    val batchRemovedMap = map1 -- List("a", "c")
    println(s"批量删除键: $batchRemovedMap")
    
    // 遍历Map
    println("遍历map1:")
    map1.foreach { case (key, value) => println(s"  $key -> $value") }
  }
}

// 可变Map示例
object MutableMapDemo {
  def run(): Unit = {
    println("\n=== 可变Map示例 ===")
    
    import scala.collection.mutable.Map
    
    // 创建可变Map
    val mutableMap = Map("name" -> "Alice", "age" -> 30)
    
    println(s"初始mutableMap: $mutableMap")
    
    // 添加键值对（直接修改原Map）
    mutableMap += ("city" -> "Beijing")
    println(s"添加键值对'city'->'Beijing'后: $mutableMap")
    
    // 更新键值对
    mutableMap("age") = 31
    println(s"更新'age'为31后: $mutableMap")
    
    // 删除键值对
    mutableMap -= "city"
    println(s"删除'city'键后: $mutableMap")
    
    // 批量操作
    mutableMap ++= Map("country" -> "China", "job" -> "Engineer")
    println(s"批量添加键值对后: $mutableMap")
    
    mutableMap --= List("job", "age")
    println(s"批量删除键后: $mutableMap")
    
    // 获取或默认值
    println(s"获取'name'的值: ${mutableMap("name")}")
    println(s"获取不存在的键的默认值: ${mutableMap.getOrElse("salary", 0)}")
  }
}

// SortedMap示例
object SortedMapDemo {
  def run(): Unit = {
    println("\n=== SortedMap示例 ===")
    
    import scala.collection.immutable.SortedMap
    
    // 创建SortedMap
    val sortedMap = SortedMap("banana" -> 2, "apple" -> 1, "cherry" -> 3, "date" -> 4)
    
    println(s"sortedMap: $sortedMap")  // 键自动排序
    
    // 添加键值对
    val newSortedMap = sortedMap + ("elderberry" -> 5)
    println(s"添加键值对后: $newSortedMap")
    
    // 获取边界元素
    println(s"第一个键值对: ${sortedMap.firstKey} -> ${sortedMap(sortedMap.firstKey)}")
    println(s"最后一个键值对: ${sortedMap.lastKey} -> ${sortedMap(sortedMap.lastKey)}")
    
    // 范围操作
    println(s"键在'banana'之前的元素: ${sortedMap.rangeUntil("banana")}")
    println(s"键在'cherry'之后的元素: ${sortedMap.rangeFrom("cherry")}")
  }
}

// LinkedHashMap示例
object LinkedHashMapDemo {
  def run(): Unit = {
    println("\n=== LinkedHashMap示例 ===")
    
    import scala.collection.mutable.LinkedHashMap
    
    // 创建LinkedHashMap（保持插入顺序）
    val linkedMap = LinkedHashMap("first" -> 1, "second" -> 2, "third" -> 3)
    
    println(s"linkedMap: $linkedMap")
    
    // 添加键值对（保持插入顺序）
    linkedMap += ("fourth" -> 4)
    linkedMap += ("fifth" -> 5)
    println(s"添加键值对后: $linkedMap")
    
    // 遍历（按插入顺序）
    println("按插入顺序遍历:")
    linkedMap.foreach { case (key, value) => println(s"  $key -> $value") }
  }
}

// HashMap示例（可变）
object HashMapDemo {
  def run(): Unit = {
    println("\n=== HashMap示例 ===")
    
    import scala.collection.mutable.HashMap
    
    // 创建HashMap
    val hashMap = HashMap("red" -> "#FF0000", "green" -> "#00FF00", "blue" -> "#0000FF")
    
    println(s"hashMap: $hashMap")
    
    // 添加键值对
    hashMap += ("yellow" -> "#FFFF00")
    println(s"添加yellow后: $hashMap")
    
    // 更新键值对
    hashMap("red") = "#FF0000FF"  // 添加alpha通道
    println(s"更新red的值后: $hashMap")
    
    // 获取值
    println(s"green的值: ${hashMap("green")}")
    println(s"magenta的默认值: ${hashMap.getOrElseUpdate("magenta", "#FF00FF")}")
    
    // 转换操作
    val keys = hashMap.keys
    val values = hashMap.values
    println(s"所有键: ${keys.mkString(", ")}")
    println(s"所有值: ${values.mkString(", ")}")
  }
}

// 主程序入口
object MapExamplesDemo extends App {
  ImmutableMapDemo.run()
  MutableMapDemo.run()
  SortedMapDemo.run()
  LinkedHashMapDemo.run()
  HashMapDemo.run()
}