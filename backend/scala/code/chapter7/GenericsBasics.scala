// 泛型基础示例

// 1. 泛型类
class Box[T](val content: T) {
  def getContent: T = content
  def isContentEqual(other: Box[T]): Boolean = this.content == other.content
  
  override def toString: String = s"Box($content)"
}

// 泛型类使用示例
object GenericsBasics extends App {
  // 字符串盒子
  val stringBox = new Box("Hello Scala")
  println(stringBox)
  println(stringBox.getContent)
  
  // 整数盒子
  val intBox = new Box(42)
  println(intBox)
  println(intBox.getContent)
  
  // 相等性比较
  val anotherIntBox = new Box(42)
  println(intBox.isContentEqual(anotherIntBox)) // true
}

// 2. 泛型方法
object GenericMethods {
  // 泛型方法 - 交换元组元素
  def swap[T, S](tuple: (T, S)): (S, T) = (tuple._2, tuple._1)
  
  // 泛型方法 - 找到列表中的中间元素
  def middleElement[T](list: List[T]): Option[T] = {
    if (list.isEmpty) None
    else Some(list(list.length / 2))
  }
  
  // 泛型方法 - 创建包含N个相同元素的列表
  def repeat[T](element: T, count: Int): List[T] = List.fill(count)(element)
  
  // 泛型方法 - 合并两个列表
  def mergeLists[T](list1: List[T], list2: List[T]): List[T] = list1 ::: list2
  
  def demonstrate(): Unit = {
    // 交换元组元素
    val intString = (42, "Answer")
    val swapped = swap(intString)
    println(s"Original: $intString, Swapped: $swapped")
    
    // 找到中间元素
    val numbers = List(1, 2, 3, 4, 5)
    println(s"Middle of $numbers: ${middleElement(numbers)}")
    
    val chars = List('a', 'b', 'c', 'd')
    println(s"Middle of $chars: ${middleElement(chars)}")
    
    // 重复元素
    val repeated = repeat("Scala", 3)
    println(s"Repeated 'Scala' 3 times: $repeated")
    
    // 合并列表
    val merged = mergeLists(List(1, 2, 3), List(4, 5, 6))
    println(s"Merged list: $merged")
  }
}

// 3. 多个类型参数
class Pair[T, S](val first: T, val second: S) {
  def swap: Pair[S, T] = new Pair(second, first)
  
  override def toString: String = s"Pair($first, $second)"
}

object MultiTypeParams {
  def demonstrate(): Unit = {
    val stringIntPair = new Pair("Age", 30)
    println(stringIntPair)
    println(s"Swapped: ${stringIntPair.swap}")
    
    val booleanCharPair = new Pair(true, 'X')
    println(booleanCharPair)
  }
}