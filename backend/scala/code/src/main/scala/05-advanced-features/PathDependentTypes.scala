// 路径依赖类型示例

// 数据库连接示例
class Database {
  // 抽象类型成员
  type Key
  type Value
  
  // 具体实现
  private var data: Map[Key, Value] = Map.empty
  
  // 方法返回路径依赖类型
  def createKey(): Key = ???
  def getValue(key: Key): Option[Value] = data.get(key)
  def setValue(key: Key, value: Value): Unit = data = data + (key -> value)
}

// 更具体的数据库实现
class StringDatabase {
  // 具体化抽象类型
  type Key = String
  type Value = String
  
  private var data: Map[Key, Value] = Map.empty
  
  def createKey(): Key = java.util.UUID.randomUUID().toString
  def getValue(key: Key): Option[Value] = data.get(key)
  def setValue(key: Key, value: Value): Unit = data = data + (key -> value)
}

// 路径依赖类型的使用
class Graph {
  class Node {
    var connectedNodes: List[Node] = List.empty
    def connectTo(node: Node): Unit = {
      connectedNodes = node :: connectedNodes
    }
  }
  
  val nodes: List[Node] = List.fill(3)(new Node)
  
  // 注意：graph1.Node 和 graph2.Node 是不同的类型
  def getNode: Node = new Node
}

// 依赖方法类型示例
trait Container {
  type T
  val value: T
}

object PathDependentTypes {
  def main(args: Array[String]): Unit = {
    // 基本路径依赖类型示例
    val db1 = new StringDatabase
    val db2 = new StringDatabase
    
    val key1 = db1.createKey()
    val key2 = db2.createKey()
    
    db1.setValue(key1, "value1")
    db2.setValue(key2, "value2")
    
    println(db1.getValue(key1)) // 输出: Some(value1)
    println(db2.getValue(key2)) // 输出: Some(value2)
    
    // 路径依赖类型不能混用
    // db1.setValue(key2, "wrong") // 编译错误！
    
    // 图形节点示例
    val graph1 = new Graph
    val graph2 = new Graph
    
    val node1 = graph1.getNode
    val node2 = graph1.getNode
    
    node1.connectTo(node2) // 同一图中的节点可以连接
    
    // node1.connectTo(graph2.getNode) // 编译错误！不同图中的节点不能连接
    
    // 类型投影示例
    val container = new Container {
      type T = Int
      val value = 42
    }
    
    println(container.value) // 输出: 42
    
    // 使用类型投影访问类型
    def processContainer(c: Container): c.T = c.value
    println(processContainer(container)) // 输出: 42
  }
}