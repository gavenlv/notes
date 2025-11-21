import scala.collection.immutable._
import scala.collection.mutable

object CollectionBasics {
  def main(args: Array[String]): Unit = {
    // 不可变集合
    // List
    val list1 = List(1, 2, 3, 4, 5)
    val list2 = 0 :: list1
    val list3 = list1 :+ 6
    val list4 = list1 ++ List(6, 7, 8)
    
    println(s"list1: $list1")
    println(s"list2: $list2")
    println(s"list3: $list3")
    println(s"list4: $list4")
    
    // Vector
    val vector1 = Vector(1, 2, 3, 4, 5)
    val vector2 = vector1.updated(2, 99)
    val vector3 = 0 +: vector1
    val vector4 = vector1 :+ 6
    
    println(s"vector1: $vector1")
    println(s"vector2: $vector2")
    println(s"vector3: $vector3")
    println(s"vector4: $vector4")
    
    // Set
    val set1 = Set(1, 2, 3, 4, 5)
    val set2 = Set(3, 4, 5, 6, 7)
    val unionSet = set1.union(set2)
    val intersectionSet = set1.intersect(set2)
    val diffSet = set1.diff(set2)
    
    println(s"set1: $set1")
    println(s"set2: $set2")
    println(s"union: $unionSet")
    println(s"intersection: $intersectionSet")
    println(s"difference: $diffSet")
    
    // Map
    val map1 = Map("one" -> 1, "two" -> 2, "three" -> 3)
    val map2 = map1 + ("four" -> 4)
    val map3 = map1 - "two"
    val map4 = map1.updated("two", 22)
    
    println(s"map1: $map1")
    println(s"map2: $map2")
    println(s"map3: $map3")
    println(s"map4: $map4")
    
    // 可变集合
    // Buffer
    val buffer1 = mutable.Buffer(1, 2, 3)
    buffer1 += 4
    buffer1 += (5, 6)
    buffer1 ++= List(7, 8, 9)
    buffer1 -= 3
    
    println(s"buffer1: $buffer1")
    
    // ListBuffer
    val listBuffer = mutable.ListBuffer(1, 2, 3)
    listBuffer.prepend(0)
    listBuffer.append(4)
    
    println(s"listBuffer: $listBuffer")
    
    // ArrayBuffer
    val arrayBuffer = mutable.ArrayBuffer(1, 2, 3)
    arrayBuffer(0) = 10
    arrayBuffer.insert(1, 99)
    
    println(s"arrayBuffer: $arrayBuffer")
    
    // 可变Set
    val mutableSet = mutable.Set(1, 2, 3)
    mutableSet += 4
    mutableSet -= 2
    mutableSet ++= Set(5, 6, 7)
    
    println(s"mutableSet: $mutableSet")
    
    // 可变Map
    val mutableMap = mutable.Map("one" -> 1, "two" -> 2, "three" -> 3)
    mutableMap("four") = 4
    mutableMap += ("five" -> 5)
    mutableMap -= "two"
    
    println(s"mutableMap: $mutableMap")
  }
}