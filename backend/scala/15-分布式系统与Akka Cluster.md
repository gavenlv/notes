# 第15章：分布式系统与Akka Cluster

## 15.1 分布式系统基础

### 15.1.1 分布式系统概念

分布式系统是由一组通过网络通信的独立计算机组成，这些计算机对于用户来说就像一个单一的系统。Scala在分布式系统开发中有天然的优势，特别是通过Akka框架。

```scala
// 分布式系统的基本概念示例

// 1. CAP定理
// CAP定理指出，分布式系统无法同时满足以下三个保证：
// - 一致性（Consistency）：所有节点在同一时间具有相同的数据
// - 可用性（Availability）：每个请求都会收到响应
// - 分区容错性（Partition Tolerance）：系统在网络分区的情况下仍能继续运行

sealed trait CAPProperty
case object Consistency extends CAPProperty
case object Availability extends CAPProperty
case object PartitionTolerance extends CAPProperty

// 2. 分布式系统设计模式
object DistributedPatterns {
  // 主从模式
  case class MasterNode(id: String, workers: List[String])
  case class WorkerNode(id: String, master: String)
  
  // 对等网络
  case class PeerNode(id: String, peers: List[String])
  
  // 分区模式
  case class PartitionNode(id: String, partition: Int, replicas: List[String])
  
  // 命令查询职责分离（CQRS）
  sealed trait Command
  sealed trait Query
  
  case class CreateEntity(id: String, data: String) extends Command
  case class UpdateEntity(id: String, data: String) extends Command
  case class GetEntity(id: String) extends Query
  case class ListEntities() extends Query
}

// 3. 消息传递模式
object MessagingPatterns {
  // 点对点消息
  case class PointToPointMessage(from: String, to: String, payload: Any)
  
  // 发布-订阅
  case class PublishMessage(topic: String, message: Any)
  case class SubscribeRequest(topic: String, subscriber: String)
  
  // 请求-响应
  case class Request(id: String, payload: Any, replyTo: String)
  case class Response(id: String, payload: Any, inReplyTo: String)
  
  // 工作队列
  case class WorkTask(id: String, payload: Any)
  case class WorkResult(id: String, result: Any)
}
```

### 15.1.2 分布式数据一致性

```scala
// 分布式数据一致性模型

object ConsistencyModels {
  // 1. 强一致性
  object StrongConsistency {
    case class DataItem(key: String, value: Any, version: Long)
    
    class StronglyConsistentStore {
      private val store = scala.collection.mutable.Map.empty[String, DataItem]
      
      def get(key: String): Option[DataItem] = store.get(key)
      
      def put(key: String, value: Any): Unit = {
        val currentVersion = store.get(key).map(_.version).getOrElse(0L)
        store(key) = DataItem(key, value, currentVersion + 1)
      }
      
      def compareAndSet(key: String, expectedVersion: Long, newValue: Any): Boolean = {
        store.get(key) match {
          case Some(item) if item.version == expectedVersion =>
            store(key) = item.copy(value = newValue, version = expectedVersion + 1)
            true
          case _ => false
        }
      }
    }
  }
  
  // 2. 最终一致性
  object EventualConsistency {
    case class ReplicatedData(key: String, value: Any, timestamp: Long)
    
    class EventuallyConsistentStore(nodeId: String) {
      private val store = scala.collection.mutable.Map.empty[String, ReplicatedData]
      private val pendingUpdates = scala.collection.mutable.Queue.empty[(String, ReplicatedData)]
      
      def get(key: String): Option[Any] = store.get(key).map(_.value)
      
      def put(key: String, value: Any): Unit = {
        val newData = ReplicatedData(key, value, System.currentTimeMillis())
        store(key) = newData
        pendingUpdates.enqueue((key, newData))
      }
      
      def replicateTo(otherNode: EventuallyConsistentStore): Unit = {
        while (pendingUpdates.nonEmpty) {
          val (key, data) = pendingUpdates.dequeue()
          otherNode.receiveUpdate(key, data)
        }
      }
      
      def receiveUpdate(key: String, data: ReplicatedData): Unit = {
        store.get(key) match {
          case None =>
            store(key) = data
          case Some(existingData) if data.timestamp > existingData.timestamp =>
            store(key) = data
          case _ => // 忽略旧数据
        }
      }
    }
  }
  
  // 3. 冲突解决策略
  object ConflictResolution {
    // 最后写入获胜（LWW）
    def lastWriteWins[T](oldData: (T, Long), newData: (T, Long)): (T, Long) = {
      if (oldData._2 > newData._2) oldData else newData
    }
    
    // 向量时钟
    case class VectorClock(entries: Map[String, Long]) {
      def increment(nodeId: String): VectorClock = {
        val currentVersion = entries.getOrElse(nodeId, 0L)
        VectorClock(entries + (nodeId -> (currentVersion + 1)))
      }
      
      def update(other: VectorClock): VectorClock = {
        val mergedEntries = entries.keySet.union(other.entries.keySet).map { key =>
          val maxVersion = math.max(entries.getOrElse(key, 0L), other.entries.getOrElse(key, 0L))
          key -> maxVersion
        }.toMap
        
        VectorClock(mergedEntries)
      }
      
      def happenedBefore(other: VectorClock): Boolean = {
        entries.forall { case (key, version) =>
          version <= other.entries.getOrElse(key, 0L)
        } && entries != other.entries
      }
      
      def concurrent(other: VectorClock): Boolean = {
        !happenedBefore(other) && !other.happenedBefore(this)
      }
    }
    
    // CRDT示例：G-Counter（仅增长计数器）
    case class GCounter(counters: Map[String, Long]) {
      def increment(nodeId: String): GCounter = {
        val currentCount = counters.getOrElse(nodeId, 0L)
        GCounter(counters + (nodeId -> (currentCount + 1)))
      }
      
      def value: Long = counters.values.sum
      
      def merge(other: GCounter): GCounter = {
        val mergedCounters = counters.keySet.union(other.counters.keySet).map { key =>
          key -> math.max(counters.getOrElse(key, 0L), other.counters.getOrElse(key, 0L))
        }.toMap
        
        GCounter(mergedCounters)
      }
    }
  }
}
```

## 15.2 Akka简介

### 15.2.1 Actor模型基础

Actor模型是Akka框架的核心，它提供了一种并发编程的高级别抽象。

```scala
// Actor模型基础概念

// 1. 消息定义
sealed trait ActorMessage
case class Greeting(who: String) extends ActorMessage
case class GreetResponse(message: String) extends ActorMessage
case class GetCount() extends ActorMessage
case class CountResponse(count: Int) extends ActorMessage

// 2. Actor定义
import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, Props}

class GreeterActor extends Actor with ActorLogging {
  private var greetingCount = 0
  
  def receive = {
    case Greeting(who) =>
      greetingCount += 1
      val message = s"Hello, $who! (Total greetings: $greetingCount)"
      log.info(message)
      sender() ! GreetResponse(message)
      
    case GetCount() =>
      sender() ! CountResponse(greetingCount)
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 3. 使用Actor
object ActorExample {
  def main(args: Array[String]): Unit = {
    // 创建Actor系统
    val system = ActorSystem("GreetingSystem")
    
    // 创建Actor
    val greeter = system.actorOf(Props[GreeterActor], "greeter")
    
    // 发送消息
    import scala.concurrent.duration._
    import akka.pattern.ask
    import akka.util.Timeout
    implicit val timeout: Timeout = Timeout(5.seconds)
    
    // 发送问候消息
    val future1 = (greeter ? Greeting("Alice")).mapTo[GreetResponse]
    val future2 = (greeter ? Greeting("Bob")).mapTo[GreetResponse]
    
    // 等待并处理响应
    import scala.concurrent.ExecutionContext.Implicits.global
    future1.foreach(response => println(s"Alice received: ${response.message}"))
    future2.foreach(response => println(s"Bob received: ${response.message}"))
    
    // 获取计数
    val countFuture = (greeter ? GetCount()).mapTo[CountResponse]
    countFuture.foreach(response => println(s"Total greetings: ${response.count}"))
    
    Thread.sleep(2000)  // 等待异步操作完成
    
    // 关闭Actor系统
    system.terminate()
  }
}
```

### 15.2.2 Akka Typed API

```scala
// Akka Typed API（类型安全的Actor）

import akka.actor.typed.{ActorRef, ActorSystem, Behavior, PostStop}
import akka.actor.typed.scaladsl.{AbstractBehavior, ActorContext, Behaviors}

// 1. 定义消息类型
sealed trait GreeterCommand
case class Greet(whom: String, replyTo: ActorRef[Greeted]) extends GreeterCommand
case class Greeted(whom: String, from: ActorRef[Greet]) extends GreeterCommand

// 2. 定义Actor行为
class GreeterActor(context: ActorContext[GreeterCommand]) 
  extends AbstractBehavior[GreeterCommand](context) {
  
  def onMessage(msg: GreeterCommand): Behavior[GreeterCommand] = {
    msg match {
      case Greet(whom, replyTo) =>
        context.log.info("Hello {}!", whom)
        replyTo ! Greeted(whom, context.self)
        this
        
      case Greeted(whom, from) =>
        context.log.info("Greeting from {} to {}", from.path.name, whom)
        this
    }
  }
}

object GreeterActor {
  def apply(): Behavior[GreeterCommand] =
    Behaviors.setup(context => new GreeterActor(context))
}

// 3. 使用Typed Actor
object TypedActorExample {
  def main(args: Array[String]): Unit = {
    val system = ActorSystem(GreeterActor(), "GreeterSystem")
    
    // 使用ActorRef调用Actor
    import akka.actor.typed.scaladsl.AskPattern._
    import scala.concurrent.duration._
    import scala.util.Success
    import scala.util.Failure
    
    implicit val timeout: akka.util.Timeout = 3.seconds
    implicit val scheduler = system.scheduler
    
    val greeter = system
    val response = greeter ? (replyTo => Greet("Charles", replyTo))
    
    import system.executionContext
    response.onComplete {
      case Success(Greeted(whom, from)) =>
        println(s"Received greeting from ${from.path.name} to $whom")
        system.terminate()
        
      case Failure(ex) =>
        println(s"Failed to get greeting: ${ex.getMessage}")
        system.terminate()
    }
  }
}
```

### 15.2.3 Actor生命周期

```scala
// Actor生命周期管理

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, Props, Terminated}
import scala.concurrent.duration._

// 1. 生命周期钩子
class LifecycleActor extends Actor with ActorLogging {
  // 构造函数
  log.info("LifecycleActor constructor called")
  
  // preStart：在Actor开始处理消息前调用
  override def preStart(): Unit = {
    log.info("preStart called")
    super.preStart()
  }
  
  // postStop：在Actor停止后调用
  override def postStop(): Unit = {
    log.info("postStop called")
    super.postStop()
  }
  
  // preRestart：在重启前调用
  override def preRestart(reason: Throwable, message: Option[Any]): Unit = {
    log.info(s"preRestart called due to: ${reason.getMessage}")
    super.preRestart(reason, message)
  }
  
  // postRestart：在重启后调用
  override def postRestart(reason: Throwable): Unit = {
    log.info(s"postRestart called due to: ${reason.getMessage}")
    super.postRestart(reason)
  }
  
  // 消息处理
  def receive = {
    case "normal" =>
      log.info("Processing normal message")
      
    case "crash" =>
      log.warning("Simulating a crash")
      throw new RuntimeException("Simulated actor crash")
      
    case msg =>
      log.info(s"Received unknown message: $msg")
  }
}

// 2. 监督策略
import akka.actor.{OneForOneStrategy, SupervisorStrategy}

class SupervisorActor extends Actor with ActorLogging {
  // 子Actor
  private val child = context.actorOf(Props[LifecycleActor], "lifecycleChild")
  
  // 定义监督策略
  override def supervisorStrategy: SupervisorStrategy = OneForOneStrategy(maxNrOfRetries = 3, withinTimeRange = 1.minute) {
    case _: RuntimeException => 
      log.warning("Restarting child due to RuntimeException")
      SupervisorStrategy.restart
      
    case _: IllegalArgumentException => 
      log.warning("Stopping child due to IllegalArgumentException")
      SupervisorStrategy.stop
      
    case _: Exception => 
      log.warning("Escalating exception to parent")
      SupervisorStrategy.escalate
  }
  
  def receive = {
    case msg => 
      log.info(s"Forwarding message to child: $msg")
      child.forward(msg)
  }
}

// 3. Actor死亡监视
class WatcherActor extends Actor with ActorLogging {
  def receive = {
    case "start" =>
      val child = context.actorOf(Props[LifecycleActor], "watchedChild")
      context.watch(child)  // 监视子Actor
      child ! "normal"
      child ! "crash"  // 将导致子Actor重启
      
    case Terminated(actorRef) =>
      log.warning(s"Actor ${actorRef.path.name} has terminated")
      
    case msg =>
      log.info(s"Received unknown message: $msg")
  }
}

// 4. 生命周期示例
object LifecycleExample {
  def main(args: Array[String]): Unit = {
    val system = ActorSystem("LifecycleSystem")
    
    // 创建监督者
    val supervisor = system.actorOf(Props[SupervisorActor], "supervisor")
    
    // 发送消息测试生命周期
    supervisor ! "normal"
    supervisor ! "crash"  // 将触发重启
    supervisor ! "normal"  // 重启后应能正常处理
    
    // 创建监视者
    val watcher = system.actorOf(Props[WatcherActor], "watcher")
    watcher ! "start"
    
    Thread.sleep(2000)
    system.terminate()
  }
}
```

## 15.3 Akka Cluster

### 15.3.1 集群基础

Akka Cluster提供了一种构建分布式Actor系统的方式，允许Actor分布在多个节点上。

```scala
// Akka Cluster基础

// 1. 配置文件 (application.conf)
/*
akka {
  actor {
    provider = "cluster"
  }
  
  remote {
    artery {
      enabled = on
      transport = tcp
      canonical {
        hostname = "127.0.0.1"
        port = 2551
      }
    }
  }
  
  cluster {
    seed-nodes = [
      "akka://ClusterSystem@127.0.0.1:2551",
      "akka://ClusterSystem@127.0.0.1:2552"
    ]
    
    downing-provider-class = "akka.cluster.sbr.SplitBrainResolverProvider"
  }
}
*/

// 2. 集群成员管理
import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, Props}
import akka.cluster.{Cluster, ClusterEvent, Member, MemberStatus}
import akka.cluster.ClusterEvent._

class ClusterListenerActor extends Actor with ActorLogging {
  private val cluster = Cluster(context.system)
  
  // 订阅集群事件
  override def preStart(): Unit = {
    cluster.subscribe(
      self,
      initialStateMode = InitialStateAsEvents,
      classOf[MemberEvent],
      classOf[UnreachableMember]
    )
  }
  
  override def postStop(): Unit = {
    cluster.unsubscribe(self)
    super.postStop()
  }
  
  def receive = {
    case MemberUp(member) =>
      log.info("Member is Up: {}", member.address)
      
    case UnreachableMember(member) =>
      log.warning("Member detected as unreachable: {}", member.address)
      
    case MemberRemoved(member, previousStatus) =>
      log.info("Member is Removed: {} after {}", member.address, previousStatus)
      
    case MemberEvent(member, MemberStatus.Leaving) =>
      log.info("Member is Leaving: {}", member.address)
      
    case MemberEvent(member, MemberStatus.Exiting) =>
      log.info("Member is Exiting: {}", member.address)
      
    case MemberEvent(member, MemberStatus.Down) =>
      log.info("Member is Down: {}", member.address)
      
    case msg =>
      log.warning(s"Received unknown cluster event: $msg")
  }
}

// 3. 集群单例
import akka.cluster.singleton.{ClusterSingletonManager, ClusterSingletonManagerSettings}
import akka.cluster.singleton.{ClusterSingletonProxy, ClusterSingletonProxySettings}

// 单例Actor
class ClusterSingletonActor extends Actor with ActorLogging {
  private var counter = 0
  
  def receive = {
    case "increment" =>
      counter += 1
      log.info(s"Counter incremented to: $counter")
      sender() ! counter
      
    case "get" =>
      log.info(s"Current counter: $counter")
      sender() ! counter
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 启动集群单例
object ClusterSingletonExample {
  def setupClusterSingleton(system: ActorSystem): ActorRef = {
    // 设置单例管理器
    val singletonManager = system.actorOf(
      ClusterSingletonManager.props(
        Props[ClusterSingletonActor],
        terminationMessage = PoisonPill,
        settings = ClusterSingletonManagerSettings(system)
      ),
      "counterSingleton"
    )
    
    // 设置单例代理，允许任何节点与单例交互
    val singletonProxy = system.actorOf(
      ClusterSingletonProxy.props(
        singletonManagerPath = "/user/counterSingleton",
        settings = ClusterSingletonProxySettings(system)
      ),
      "counterProxy"
    )
    
    singletonProxy
  }
}

// 4. 集群路由
import akka.routing._
import akka.cluster.routing.{ClusterRouterGroup, ClusterRouterGroupSettings}
import akka.routing.ConsistentHashingRouter.{ConsistentHashingGroup, ConsistentHashingPool}

// 定义集群路由消息
sealed trait ClusterRouteeMessage
case class ClusterRouteeMessage(id: String, payload: Any) extends ClusterRouteeMessage

// 集群路由Actor
class ClusterRouteeActor extends Actor with ActorLogging {
  def receive = {
    case ClusterRouteeMessage(id, payload) =>
      log.info(s"Processing message with id: $id, payload: $payload")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 设置集群路由
object ClusterRoutingExample {
  def setupClusterRouting(system: ActorSystem): ActorRef = {
    // 集群路由组
    val clusterRouter = system.actorOf(
      ClusterRouterGroup(
        ConsistentHashingGroup(
          List("/user/routee")
        ),
        ClusterRouterGroupSettings(
          totalInstances = 100,
          allowLocalRoutees = false,
          useRole = None
        )
      ).props(),
      "clusterRouter"
    )
    
    clusterRouter
  }
}

// 5. 集群分片
import akka.cluster.sharding.{ClusterSharding, ClusterShardingSettings, Entity, ShardRegion}

// 分片实体
case class Counter(id: String, count: Int)

// 分片消息
sealed trait CounterCommand
case class Increment(id: String) extends CounterCommand
case class Decrement(id: String) extends CounterCommand
case class Get(id: String) extends CounterCommand
case class Value(id: String, count: Int)

// 分片实体Actor
class CounterEntity extends Actor with ActorLogging {
  private var count = 0
  
  def receive = {
    case Increment(_) =>
      count += 1
      log.info(s"Counter incremented to: $count")
      
    case Decrement(_) =>
      count -= 1
      log.info(s"Counter decremented to: $count")
      
    case Get(id) =>
      sender() ! Value(id, count)
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 设置集群分片
object ClusterShardingExample {
  def setupClusterSharding(system: ActorSystem): ActorRef = {
    val shardRegion = ClusterSharding(system).start(
      typeName = "Counter",
      entityProps = Props[CounterEntity],
      settings = ClusterShardingSettings(system),
      extractEntityId = ShardRegion.extractEntityId,
      extractShardId = ShardRegion.extractShardId
    )
    
    shardRegion
  }
}
```

### 15.3.2 分布式数据

```scala
// Akka Distributed Data (CRDT)

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, Props}
import akka.cluster.ddata._
import akka.cluster.ddata.Replicator._
import akka.cluster.Cluster

// 1. OR-Set (Observe-Remove Set)
sealed trait ORSetCommand
case class AddElement[T](key: String, element: T) extends ORSetCommand
case class RemoveElement[T](key: String, element: T) extends ORSetCommand
case class GetElements[T](key: String) extends ORSetCommand
case class ElementsResponse[T](key: String, elements: Set[T])

class ORSetActor extends Actor with ActorLogging {
  implicit val cluster: Cluster = Cluster(context.system)
  implicit val node: SelfUniqueAddress = DistributedData(context.system).selfUniqueAddress
  
  private val replicator = DistributedData(context.system).replicator
  private implicit val timeout = akka.util.Timeout(3.seconds)
  
  def receive = {
    case AddElement(key, element: Any) =>
      val update = Update(key, ORSet.empty[Any], WriteLocal)(_ + element)
      replicator ! update
      
    case RemoveElement(key, element: Any) =>
      val update = Update(key, ORSet.empty[Any], WriteLocal)(_ - element)
      replicator ! update
      
    case GetElements(key) =>
      replicator ! Get(key, ReadLocal)
      
    case GetSuccess(key, value: ORSet[Any]) =>
      sender() ! ElementsResponse(key, value.elements)
      
    case GetFailure(key, _) =>
      log.warning(s"Failed to get OR-Set for key: $key")
      
    case NotFound(key, _) =>
      log.warning(s"OR-Set not found for key: $key")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 2. PN-Counter (Positive-Negative Counter)
sealed trait PNCounterCommand
case class IncrementCounter(key: String) extends PNCounterCommand
case class DecrementCounter(key: String) extends PNCounterCommand
case class GetCounter(key: String) extends PNCounterCommand
case class CounterResponse(key: String, value: Long)

class PNCounterActor extends Actor with ActorLogging {
  implicit val cluster: Cluster = Cluster(context.system)
  implicit val node: SelfUniqueAddress = DistributedData(context.system).selfUniqueAddress
  
  private val replicator = DistributedData(context.system).replicator
  private implicit val timeout = akka.util.Timeout(3.seconds)
  
  def receive = {
    case IncrementCounter(key) =>
      val update = Update(key, PNCounter.empty, WriteLocal)(_.increment(node))
      replicator ! update
      
    case DecrementCounter(key) =>
      val update = Update(key, PNCounter.empty, WriteLocal)(_.decrement(node))
      replicator ! update
      
    case GetCounter(key) =>
      replicator ! Get(key, ReadLocal)
      
    case GetSuccess(key, value: PNCounter) =>
      sender() ! CounterResponse(key, value.value)
      
    case GetFailure(key, _) =>
      log.warning(s"Failed to get PN-Counter for key: $key")
      
    case NotFound(key, _) =>
      log.warning(s"PN-Counter not found for key: $key")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 3. LWW-Register (Last-Writer-Wins Register)
sealed trait LWWRegisterCommand
case class SetValue[T](key: String, value: T) extends LWWRegisterCommand
case class GetValue[T](key: String) extends LWWRegisterCommand
case class ValueResponse[T](key: String, value: T)

class LWWRegisterActor extends Actor with ActorLogging {
  implicit val cluster: Cluster = Cluster(context.system)
  implicit val node: SelfUniqueAddress = DistributedData(context.system).selfUniqueAddress
  
  private val replicator = DistributedData(context.system).replicator
  private implicit val timeout = akka.util.Timeout(3.seconds)
  
  def receive = {
    case SetValue(key, value) =>
      val update = Update(key, LWWRegister.empty[Any], WriteLocal)(_.withValue(node, value))
      replicator ! update
      
    case GetValue(key) =>
      replicator ! Get(key, ReadLocal)
      
    case GetSuccess(key, value: LWWRegister[Any]) =>
      sender() ! ValueResponse(key, value.value)
      
    case GetFailure(key, _) =>
      log.warning(s"Failed to get LWW-Register for key: $key")
      
    case NotFound(key, _) =>
      log.warning(s"LWW-Register not found for key: $key")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 4. OR-Map (Observed-Removed Map)
sealed trait ORMapCommand
case class PutMapEntry[K, V](key: String, mapKey: K, value: V) extends ORMapCommand
case class RemoveMapEntry[K](key: String, mapKey: K) extends ORMapCommand
case class GetMapEntries[K, V](key: String) extends ORMapCommand
case class MapEntriesResponse[K, V](key: String, entries: Map[K, V])

class ORMapActor extends Actor with ActorLogging {
  implicit val cluster: Cluster = Cluster(context.system)
  implicit val node: SelfUniqueAddress = DistributedData(context.system).selfUniqueAddress
  
  private val replicator = DistributedData(context.system).replicator
  private implicit val timeout = akka.util.Timeout(3.seconds)
  
  def receive = {
    case PutMapEntry(key, mapKey, value) =>
      val update = Update(key, ORMap.empty[String, ORSet[Any]], WriteLocal) { 
        map => 
          val set = map.getOrElse(mapKey, ORSet.empty[Any])
          map + (mapKey -> (set + value))
      }
      replicator ! update
      
    case RemoveMapEntry(key, mapKey) =>
      val update = Update(key, ORMap.empty[String, ORSet[Any]], WriteLocal)(_ - mapKey)
      replicator ! update
      
    case GetMapEntries(key) =>
      replicator ! Get(key, ReadLocal)
      
    case GetSuccess(key, value: ORMap[String, ORSet[Any]]) =>
      val entries = value.entries.map { case (k, v) => (k, v.elements.head) }.toMap
      sender() ! MapEntriesResponse(key, entries)
      
    case GetFailure(key, _) =>
      log.warning(s"Failed to get OR-Map for key: $key")
      
    case NotFound(key, _) =>
      log.warning(s"OR-Map not found for key: $key")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}
```

## 15.4 Akka Streams

### 15.4.1 流基础

Akka Streams提供了一种处理和转换数据流的方式，具有背压支持。

```scala
// Akka Streams基础

import akka.actor.ActorSystem
import akka.stream.scaladsl.{Flow, Keep, RunnableGraph, Sink, Source}
import akka.{Done, NotUsed}
import scala.concurrent.Future

// 1. 基本流概念
object BasicStreams {
  def runBasicExample(implicit system: ActorSystem): Unit = {
    implicit val ec = system.dispatcher
    
    // Source - 数据源
    val source: Source[Int, NotUsed] = Source(1 to 100)
    
    // Flow - 数据转换
    val filterFlow: Flow[Int, Int, NotUsed] = Flow[Int].filter(_ % 2 == 0)
    val mapFlow: Flow[Int, String, NotUsed] = Flow[Int].map(n => s"Number: $n")
    
    // Sink - 数据接收端
    val sink: Sink[String, Future[Done]] = Sink.foreach[String](println)
    
    // 连接Source、Flow和Sink
    val runnableGraph: RunnableGraph[NotUsed] = 
      source.via(filterFlow).via(mapFlow).to(sink)
    
    // 运行流
    runnableGraph.run()
  }
}

// 2. 背压处理
object BackpressureHandling {
  def runBackpressureExample(implicit system: ActorSystem): Unit = {
    implicit val ec = system.dispatcher
    
    // 快速生产者
    val fastProducer = Source.unfold(0) { state =>
      Thread.sleep(10)  // 模拟快速生产
      Some((state + 1, state + 1))
    }.take(100)
    
    // 慢速消费者
    val slowConsumer = Sink.foreach[Int] { value =>
      Thread.sleep(100)  // 模拟慢速消费
      println(s"Processed: $value")
    }
    
    // 运行流，背压会自动处理
    fastProducer.runWith(slowConsumer)
  }
}

// 3. 流组合
object StreamComposition {
  def runStreamCompositionExample(implicit system: ActorSystem): Unit = {
    implicit val ec = system.dispatcher
    
    // merge - 合并两个流
    val source1 = Source(1 to 5)
    val source2 = Source(6 to 10)
    
    val mergedSource: Source[Int, NotUsed] = source1.merge(source2)
    
    // zip - 组合两个流
    val zippedSource: Source[(Int, String), NotUsed] = 
      source1.zip(source2.map(n => s"Value: $n"))
    
    // concat - 连接两个流
    val concatenatedSource: Source[Int, NotUsed] = source1.concat(source2)
    
    // 运行示例
    println("=== Merged Source ===")
    mergedSource.runWith(Sink.foreach(println))
    
    Thread.sleep(1000)
    
    println("\n=== Zipped Source ===")
    zippedSource.runWith(Sink.foreach(println))
    
    Thread.sleep(1000)
    
    println("\n=== Concatenated Source ===")
    concatenatedSource.runWith(Sink.foreach(println))
  }
}

// 4. 动态流控制
object DynamicFlowControl {
  def runDynamicFlowControlExample(implicit system: ActorSystem): Unit = {
    implicit val ec = system.dispatcher
    
    // 使用throttle控制流速率
    val throttledFlow = Flow[Int]
      .throttle(1, 1.second, 1, ThrottleMode.shaping)
    
    Source(1 to 10)
      .via(throttledFlow)
      .runWith(Sink.foreach(println))
    
    // 使用grouped处理批次
    val batchFlow = Flow[Int]
      .grouped(3)  // 每批3个元素
    
    Source(1 to 10)
      .via(batchFlow)
      .runWith(Sink.foreach(batch => println(s"Batch: $batch")))
    
    // 使用sliding处理滑动窗口
    val slidingFlow = Flow[Int]
      .sliding(3, 1)  // 窗口大小3，滑动步长1
    
    Source(1 to 7)
      .via(slidingFlow)
      .runWith(Sink.foreach(window => println(s"Window: $window")))
  }
}

// 5. 错误处理
object ErrorHandling {
  def runErrorHandlingExample(implicit system: ActorSystem): Unit = {
    implicit val ec = system.dispatcher
    
    // recover - 恢复处理
    val recoverFlow = Flow[String]
      .map(s => s.toInt)
      .recover { case _: NumberFormatException => -1 }
    
    Source(List("1", "2", "abc", "4", "5"))
      .via(recoverFlow)
      .runWith(Sink.foreach(n => println(s"Processed: $n")))
    
    // recoverWithRetries - 带重试的恢复
    val retryFlow = Flow[String]
      .map(s => s.toInt)
      .recoverWithRetries(attempts = 3, {
        case _: NumberFormatException => 
          Source.single(-1)
      })
    
    Source(List("1", "2", "abc", "4", "5"))
      .via(retryFlow)
      .runWith(Sink.foreach(n => println(s"Processed with retry: $n")))
  }
}

// 6. 自定义处理阶段
object CustomStages {
  def runCustomStagesExample(implicit system: ActorSystem): Unit = {
    import akka.stream.stage.{GraphStage, GraphStageLogic, InHandler, OutHandler}
    import akka.stream.{Attributes, Inlet, Outlet}
    
    // 自定义过滤阶段
    class EvenFilter extends GraphStage[FlowShape[Int, Int]] {
      val in = Inlet[Int]("EvenFilter.in")
      val out = Outlet[Int]("EvenFilter.out")
      
      override val shape = FlowShape(in, out)
      
      override def createLogic(inheritedAttributes: Attributes): GraphStageLogic = 
        new GraphStageLogic(shape) {
          setHandler(in, new InHandler {
            override def onPush(): Unit = {
              val elem = grab(in)
              if (elem % 2 == 0) {
                push(out, elem)
              } else {
                pull(in)
              }
            }
          })
          
          setHandler(out, new OutHandler {
            override def onPull(): Unit = {
              pull(in)
            }
          })
        }
    }
    
    val evenFilterFlow = Flow.fromGraph(new EvenFilter)
    
    Source(1 to 10)
      .via(evenFilterFlow)
      .runWith(Sink.foreach(println))
  }
}

// 7. 流到Actor的集成
import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, Props}
import akka.pattern.ask
import akka.stream.scaladsl.{Flow, Sink, Source}
import akka.util.Timeout
import scala.concurrent.Future
import scala.concurrent.duration._

// Actor接收流数据
class StreamReceiverActor extends Actor with ActorLogging {
  def receive = {
    case msg: String => 
      log.info(s"Received stream message: $msg")
      
    case "completed" => 
      log.info("Stream completed")
      
    case msg => 
      log.warning(s"Received unknown message: $msg")
  }
}

object ActorStreamIntegration {
  def runActorStreamIntegrationExample(implicit system: ActorSystem): Unit = {
    implicit val ec = system.dispatcher
    implicit val timeout: Timeout = Timeout(5.seconds)
    
    // 创建Actor
    val receiver = system.actorOf(Props[StreamReceiverActor], "streamReceiver")
    
    // 创建Actor Sink
    val actorSink: Sink[String, Future[Done]] = Sink.actorRefWithBackpressure(
      receiver,
      onInitMessage = "init",
      ackMessage = "ack",
      onCompleteMessage = "completed",
      onFailureMessage = (ex: Throwable) => s"error: ${ex.getMessage}"
    )
    
    // 运行流到Actor
    Source(1 to 10)
      .map(n => s"Item $n")
      .runWith(actorSink)
    
    // 从Actor创建流
    def actorSource(ref: ActorRef): Source[String, NotUsed] = {
      Source.unfoldAsync(1) { count =>
        if (count > 5) {
          Future.successful(None)
        } else {
          (ref ? s"Request $count").mapTo[String].map(response => Some((count + 1, response)))
        }
      }
    }
  }
}

// 运行所有示例
object AkkaStreamsExample {
  def main(args: Array[String]): Unit = {
    implicit val system: ActorSystem = ActorSystem("AkkaStreamsExample")
    
    BasicStreams.runBasicExample
    Thread.sleep(1000)
    
    BackpressureHandling.runBackpressureExample
    Thread.sleep(2000)
    
    StreamComposition.runStreamCompositionExample
    Thread.sleep(1000)
    
    DynamicFlowControl.runDynamicFlowControlExample
    Thread.sleep(2000)
    
    ErrorHandling.runErrorHandlingExample
    Thread.sleep(1000)
    
    CustomStages.runCustomStagesExample
    Thread.sleep(1000)
    
    ActorStreamIntegration.runActorStreamIntegrationExample
    
    system.terminate()
  }
}
```

## 15.5 Akka HTTP

### 15.5.1 HTTP服务器

```scala
// Akka HTTP服务器

import akka.actor.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.model._
import akka.http.scaladsl.server.Directives._
import akka.stream.ActorMaterializer
import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport._
import spray.json.DefaultJsonProtocol._
import scala.concurrent.Future

// 1. 基本HTTP服务器
object BasicHttpServer {
  // 定义数据模型和JSON格式
  case class Item(id: Int, name: String, price: Double)
  implicit val itemFormat = jsonFormat3(Item)
  
  // 模拟数据存储
  var items = Map(
    1 -> Item(1, "Apple", 0.99),
    2 -> Item(2, "Banana", 0.59),
    3 -> Item(3, "Orange", 0.79)
  )
  
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("MyServer")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // 定义路由
    val route = 
      path("hello") {
        get {
          complete(HttpEntity(ContentTypes.`text/html(UTF-8)`, "<h1>Say hello to akka-http</h1>"))
        }
      } ~
      path("items") {
        get {
          complete(items.values.toList)
        } ~
        post {
          entity(as[Item]) { item =>
            items = items + (item.id -> item)
            complete(StatusCodes.Created, item)
          }
        }
      } ~
      pathPrefix("item" / IntNumber) { id =>
        get {
          complete(items.get(id))
        } ~
        delete {
          items = items - id
          complete(StatusCodes.NoContent)
        }
      }
    
    // 启动服务器
    val bindingFuture = Http().bindAndHandle(route, "localhost", 8080)
    
    println(s"Server online at http://localhost:8080/")
    
    sys.addShutdownHook {
      bindingFuture.flatMap(_.unbind()).onComplete(_ => system.terminate())
    }
  }
}

// 2. 文件上传处理
object FileUploadServer {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("FileUploadServer")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    val route = 
      path("upload") {
        (post & extractRequest) { request =>
          val fileDestination = "uploads/"
          val uploadedFile = request.entity.dataBytes.runWith(FileIO.toPath(Paths.get(fileDestination)))
          
          onComplete(uploadedFile) { result =>
            complete {
              result match {
                case Success(ioResult) =>
                  val fileSize = ioResult.count
                  s"File uploaded successfully. Size: $fileSize bytes"
                case Failure(ex) =>
                  StatusCodes.InternalServerError -> s"File upload failed: ${ex.getMessage}"
              }
            }
          }
        }
      }
    
    val bindingFuture = Http().bindAndHandle(route, "localhost", 8080)
    
    println(s"File server online at http://localhost:8080/upload")
    
    sys.addShutdownHook {
      bindingFuture.flatMap(_.unbind()).onComplete(_ => system.terminate())
    }
  }
}

// 3. WebSocket服务器
import akka.http.scaladsl.model.ws.{Message, TextMessage}
import akka.stream.scaladsl.{Flow, Keep, Sink, Source}

object WebSocketServer {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("WebSocketServer")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // 定义WebSocket消息处理
    def greeterWebSocket: Flow[Message, Message, Any] = 
      Flow[Message].collect {
        case TextMessage.Strict(text) => 
          TextMessage.Strict(s"Hello, $text!")
        case tm: TextMessage.Streamed =>
          tm.textStream.runFold("")(_ + _).map(txt => TextMessage.Strict(s"Hello, $txt!"))
      }
    
    val route = 
      path("websocket") {
        get {
          handleWebSocketMessages(greeterWebSocket)
        }
      } ~
      path("chat") {
        get {
          handleWebSocketMessages(chatFlow)
        }
      }
    
    // 聊天流
    def chatFlow: Flow[Message, Message, Any] = {
      val (chatSink, chatSource) = 
        MergeHub.source[String]
          .map(TextMessage.Strict)
          .toMat(BroadcastHub.sink[String])(Keep.both)
          .run()
      
      Flow[Message]
        .mapAsync(1) {
          case TextMessage.Strict(text) => Future.successful(text)
          case tm: TextMessage.Streamed => 
            tm.textStream.runFold("")(_ + _)
        }
        .via(chatSink)
        .via(chatSource)
        .map(TextMessage(_))
    }
    
    val bindingFuture = Http().bindAndHandle(route, "localhost", 8080)
    
    println(s"WebSocket server online at http://localhost:8080/websocket")
    println(s"Chat server online at http://localhost:8080/chat")
    
    sys.addShutdownHook {
      bindingFuture.flatMap(_.unbind()).onComplete(_ => system.terminate())
    }
  }
}

// 4. HTTP客户端
object HttpClientExample {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("HttpClientExample")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // GET请求
    val responseFuture: Future[HttpResponse] = 
      Http().singleRequest(HttpRequest(uri = "http://localhost:8080/items"))
    
    responseFuture.foreach { response =>
      println(s"Status code: ${response.status}")
      response.entity.dataBytes.runFold("")(_.utf8String + _.utf8String).foreach { body =>
        println(s"Response body: $body")
      }
    }
    
    // POST请求
    val item = Item(4, "Grape", 1.99)
    val entity = HttpEntity(ContentTypes.`application/json`, itemFormat.write(item).compactPrint)
    
    val postRequest = HttpRequest(
      method = HttpMethods.POST,
      uri = "http://localhost:8080/items",
      entity = entity
    )
    
    Http().singleRequest(postRequest).foreach { response =>
      println(s"POST status: ${response.status}")
    }
  }
}

// 5. 健康检查和监控
object HealthCheckServer {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("HealthCheckServer")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // 模拟服务状态
    var databaseStatus = "UP"
    var cacheStatus = "UP"
    var externalServiceStatus = "UP"
    
    val healthRoute = 
      path("health") {
        get {
          val overallStatus = if (databaseStatus == "UP" && cacheStatus == "UP" && externalServiceStatus == "UP") {
            "UP"
          } else {
            "DOWN"
          }
          
          val healthJson = s"""
            |{
            |  "status": "$overallStatus",
            |  "components": {
            |    "database": {"status": "$databaseStatus"},
            |    "cache": {"status": "$cacheStatus"},
            |    "externalService": {"status": "$externalServiceStatus"}
            |  }
            |}
          """.stripMargin
          
          complete(HttpEntity(ContentTypes.`application/json`, healthJson))
        }
      } ~
      path("metrics") {
        get {
          val runtime = Runtime.getRuntime
          val memoryUsage = runtime.totalMemory() - runtime.freeMemory()
          
          val metricsJson = s"""
            |{
            |  "memory": {
            |    "used": ${memoryUsage / 1024 / 1024},
            |    "total": ${runtime.totalMemory() / 1024 / 1024}
            |  },
            |  "processors": ${runtime.availableProcessors()}
            |}
          """.stripMargin
          
          complete(HttpEntity(ContentTypes.`application/json`, metricsJson))
        }
      }
    
    val bindingFuture = Http().bindAndHandle(healthRoute, "localhost", 8080)
    
    println(s"Health check server online at http://localhost:8080/health")
    println(s"Metrics available at http://localhost:8080/metrics")
    
    sys.addShutdownHook {
      bindingFuture.flatMap(_.unbind()).onComplete(_ => system.terminate())
    }
  }
}
```

## 15.6 实战案例

### 15.6.1 分布式计数器服务

```scala
// 分布式计数器服务示例

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, PoisonPill, Props}
import akka.cluster.Cluster
import akka.cluster.ddata.{DistributedData, ORSet, ORSetKey}
import akka.cluster.ddata.Replicator._
import akka.cluster.sharding.{ClusterSharding, ClusterShardingSettings, Entity, ShardRegion}
import akka.pattern.ask
import akka.util.Timeout
import scala.concurrent.duration._
import scala.util.{Success, Failure}

// 1. 计数器实体
sealed trait CounterCommand
case class IncrementCounter(counterId: String, delta: Long = 1) extends CounterCommand
case class DecrementCounter(counterId: String, delta: Long = 1) extends CounterCommand
case class GetCounterValue(counterId: String) extends CounterCommand
case class CounterValue(counterId: String, value: Long) extends CounterCommand
case class ResetCounter(counterId: String) extends CounterCommand

class CounterEntity extends Actor with ActorLogging {
  private var count = 0L
  
  def receive = {
    case IncrementCounter(counterId, delta) =>
      count += delta
      log.info(s"Counter $counterId incremented by $delta to $count")
      
    case DecrementCounter(counterId, delta) =>
      count -= delta
      log.info(s"Counter $counterId decremented by $delta to $count")
      
    case GetCounterValue(counterId) =>
      sender() ! CounterValue(counterId, count)
      
    case ResetCounter(counterId) =>
      count = 0L
      log.info(s"Counter $counterId reset to 0")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 2. 计数器服务
object CounterService {
  def setupSharding(system: ActorSystem): ActorRef = {
    val extractEntityId: ShardRegion.ExtractEntityId = {
      case cmd: CounterCommand => (cmd match {
        case IncrementCounter(id, _) => id
        case DecrementCounter(id, _) => id
        case GetCounterValue(id) => id
        case ResetCounter(id) => id
      }, cmd)
    }
    
    val extractShardId: ShardRegion.ExtractShardId = {
      case cmd: CounterCommand => (cmd match {
        case IncrementCounter(id, _) => id
        case DecrementCounter(id, _) => id
        case GetCounterValue(id) => id
        case ResetCounter(id) => id
      }).hashCode.abs % 10 toString
    }
    
    ClusterSharding(system).start(
      typeName = "Counter",
      entityProps = Props[CounterEntity],
      settings = ClusterShardingSettings(system),
      extractEntityId = extractEntityId,
      extractShardId = extractShardId
    )
  }
  
  // 使用计数器
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("CounterSystem")
    implicit val timeout: Timeout = 3.seconds
    implicit val ec = system.dispatcher
    
    val cluster = Cluster(system)
    
    // 等待集群形成
    Thread.sleep(5000)
    
    // 设置分片
    val shardingRegion = setupSharding(system)
    
    // 创建一些计数器
    import akka.pattern.pipe
    import system.dispatcher
    
    // 增加计数器
    for (i <- 1 to 5) {
      shardingRegion ! IncrementCounter(s"counter$i", 1)
    }
    
    // 获取计数器值
    for (i <- 1 to 5) {
      val future = shardingRegion ? GetCounterValue(s"counter$i")
      future.onComplete {
        case Success(CounterValue(id, value)) =>
          println(s"Counter $id value: $value")
        case Success(other) =>
          println(s"Unexpected response: $other")
        case Failure(ex) =>
          println(s"Failed to get counter value: ${ex.getMessage}")
      }
    }
    
    Thread.sleep(3000)
    system.terminate()
  }
}

// 3. 分布式计数器（使用CRDT）
sealed trait DistributedCounterCommand
case class DistributedIncrement(counterId: String, delta: Long = 1) extends DistributedCounterCommand
case class DistributedDecrement(counterId: String, delta: Long = 1) extends DistributedCounterCommand
case class DistributedGetValue(counterId: String) extends DistributedCounterCommand
case class DistributedValue(counterId: String, value: Long) extends DistributedCounterCommand

class DistributedCounterService extends Actor with ActorLogging {
  implicit val cluster: Cluster = Cluster(context.system)
  implicit val node: SelfUniqueAddress = DistributedData(context.system).selfUniqueAddress
  
  private val replicator = DistributedData(context.system).replicator
  private implicit val timeout = Timeout(3.seconds)
  
  private def counterKey(id: String): ORSetKey[String] = ORSetKey("counter-" + id)
  
  def receive = {
    case DistributedIncrement(counterId, delta) =>
      val key = counterKey(counterId)
      val update = Update(key, ORSet.empty[String], WriteLocal, consistency = WriteAll)(_.add(node.toString))
      replicator ! update
      
    case DistributedDecrement(counterId, delta) =>
      val key = counterKey(counterId)
      val update = Update(key, ORSet.empty[String], WriteLocal, consistency = WriteAll)(_.add(node.toString))
      replicator ! update
      
    case DistributedGetValue(counterId) =>
      val key = counterKey(counterId)
      replicator ! Get(key, ReadLocal, request = Some((sender(), counterId)))
      
    case GetSuccess(key, value: ORSet[String], request) =>
      request match {
        case Some((originalSender, counterId)) =>
          originalSender ! DistributedValue(counterId, value.size.toLong)
        case _ =>
          log.warning(s"Received GetSuccess without original sender for key: $key")
      }
      
    case GetFailure(key, request) =>
      log.warning(s"Failed to get counter for key: $key")
      
    case NotFound(key, request) =>
      request match {
        case Some((originalSender, counterId)) =>
          originalSender ! DistributedValue(counterId, 0L)
        case _ =>
          log.warning(s"Received NotFound without original sender for key: $key")
      }
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 4. 计数器API服务
object CounterAPIService {
  import akka.http.scaladsl.Http
  import akka.http.scaladsl.model.StatusCodes
  import akka.http.scaladsl.server.Directives._
  import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport._
  import spray.json.DefaultJsonProtocol._
  
  case class CounterResponse(counterId: String, value: Long)
  case class CounterRequest(counterId: String, delta: Option[Long])
  
  implicit val counterResponseFormat = jsonFormat2(CounterResponse)
  implicit val counterRequestFormat = jsonFormat2(CounterRequest)
  
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("CounterAPIService")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    implicit val timeout: Timeout = 3.seconds
    
    // 设置分片
    val shardingRegion = CounterService.setupSharding(system)
    
    // API路由
    val route = 
      pathPrefix("counter" / Segment) { counterId =>
        get {
          val future = (shardingRegion ? GetCounterValue(counterId)).mapTo[CounterValue]
          onSuccess(future) { counterValue =>
            complete(CounterResponse(counterValue.counterId, counterValue.value))
          }
        } ~
        post {
          entity(as[CounterRequest]) { request =>
            val delta = request.delta.getOrElse(1L)
            shardingRegion ! IncrementCounter(request.counterId, delta)
            complete(StatusCodes.OK, CounterResponse(request.counterId, delta))
          }
        } ~
        delete {
          shardingRegion ! ResetCounter(counterId)
          complete(StatusCodes.OK, CounterResponse(counterId, 0))
        }
      }
    
    // 启动HTTP服务器
    val bindingFuture = Http().bindAndHandle(route, "localhost", 8080)
    
    println(s"Counter API server online at http://localhost:8080/counter/<counterId>")
    
    sys.addShutdownHook {
      bindingFuture.flatMap(_.unbind()).onComplete(_ => system.terminate())
    }
  }
}
```

### 15.6.2 实时数据流处理

```scala
// 实时数据流处理示例

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, PoisonPill, Props}
import akka.kafka.{ConsumerSettings, ProducerSettings, Subscriptions}
import akka.kafka.scaladsl.{Consumer, Producer}
import akka.stream.ActorMaterializer
import akka.stream.scaladsl.{Flow, Keep, Sink, Source}
import akka.util.Timeout
import org.apache.kafka.clients.consumer.{ConsumerConfig, ConsumerRecord}
import org.apache.kafka.clients.producer.ProducerRecord
import org.apache.kafka.common.serialization.{StringDeserializer, StringSerializer}
import spray.json._
import scala.concurrent.duration._
import scala.concurrent.Future
import scala.util.{Success, Failure}

// 1. 数据模型
case class Event(id: String, timestamp: Long, source: String, data: String)

object EventJsonProtocol extends DefaultJsonProtocol {
  implicit val eventFormat = jsonFormat4(Event)
}
import EventJsonProtocol._

// 2. Kafka消费者
object KafkaEventConsumer {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("KafkaEventConsumer")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // Kafka消费者设置
    val consumerSettings = ConsumerSettings(system, new StringDeserializer, new StringDeserializer)
      .withBootstrapServers("localhost:9092")
      .withGroupId("event-processor-group")
      .withProperty(ConsumerConfig.AUTO_OFFSET_RESET, "latest")
    
    // 从Kafka读取事件
    val kafkaSource = Consumer
      .plainSource(consumerSettings, Subscriptions.topics("events"))
      .map(record => {
        // 解析JSON
        val event = record.value().parseJson.convertTo[Event]
        event
      })
    
    // 处理事件的流
    val eventProcessingFlow = Flow[Event]
      .filter(_.source == "sensor") // 只处理传感器事件
      .map(event => {
        // 处理事件
        val processedData = s"Processed: ${event.data}"
        event.copy(data = processedData)
      })
    
    // 输出到控制台
    val consoleSink = Sink.foreach[Event](event => 
      println(s"Processed event: ${event.id}, source: ${event.source}, data: ${event.data}")
    )
    
    // 连接流并运行
    val runnableGraph = kafkaSource
      .via(eventProcessingFlow)
      .to(consoleSink)
    
    runnableGraph.run()
  }
}

// 3. Kafka生产者
object KafkaEventProducer {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("KafkaEventProducer")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // Kafka生产者设置
    val producerSettings = ProducerSettings(system, new StringSerializer, new StringSerializer)
      .withBootstrapServers("localhost:9092")
    
    // 生成事件的源
    val eventSource = Source
      .tick(0.seconds, 1.seconds, "tick")
      .zipWithIndex
      .map {
        case (_, index) =>
          val source = if (index % 2 == 0) "sensor" else "system"
          Event(
            id = s"event-${index}",
            timestamp = System.currentTimeMillis(),
            source = source,
            data = s"Sample data from $source"
          )
      }
    
    // 转换为Kafka记录
    val kafkaFlow = Flow[Event]
      .map(event => new ProducerRecord[String, String]("events", event.id, event.toJson.compactPrint))
    
    // 连接流到Kafka生产者
    val runnableGraph = eventSource
      .via(kafkaFlow)
      .to(Producer.plainSink(producerSettings))
    
    runnableGraph.run()
    
    println("Event producer started. Publishing events to Kafka topic 'events'")
  }
}

// 4. 实时流处理
object RealTimeStreamProcessor {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("RealTimeStreamProcessor")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    implicit val timeout: Timeout = 30.seconds
    
    // Kafka消费者设置
    val consumerSettings = ConsumerSettings(system, new StringDeserializer, new StringDeserializer)
      .withBootstrapServers("localhost:9092")
      .withGroupId("stream-processor-group")
    
    // Kafka生产者设置
    val producerSettings = ProducerSettings(system, new StringSerializer, new StringSerializer)
      .withBootstrapServers("localhost:9092")
    
    // 复杂流处理管道
    val processingPipeline = Consumer
      .plainSource(consumerSettings, Subscriptions.topics("events"))
      .map(record => record.value().parseJson.convertTo[Event])
      .groupBy(20, _.source) // 按源分组
      .sliding(10, 1) // 滑动窗口，窗口大小10，滑动步长1
      .map { window =>
        // 在窗口内聚合事件
        val count = window.size
        val sources = window.map(_.source).distinct.mkString(", ")
        val avgTimestamp = window.map(_.timestamp).sum / count
        
        // 创建聚合结果
        s"Window of $count events from sources [$sources], avg timestamp: $avgTimestamp"
      }
      .mergeSubstreams
      .map(result => new ProducerRecord[String, String]("processed-events", "window", result))
      .to(Producer.plainSink(producerSettings))
    
    processingPipeline.run()
    
    println("Real-time stream processor started")
  }
}

// 5. 处理错误和重试
object RobustStreamProcessor {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("RobustStreamProcessor")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // 模拟错误源
    val errorSource = Source
      .tick(0.seconds, 1.seconds, "tick")
      .zipWithIndex
      .map {
        case (_, index) =>
          if (index % 5 == 0) {
            throw new RuntimeException(s"Simulated error at index $index")
          } else {
            s"Event $index"
          }
      }
    
    // 错误处理流
    val errorHandlingFlow = Flow[String]
      .map(event => {
        // 模拟可能失败的处理
        if (event.contains("3")) {
          throw new RuntimeException("Special processing error")
        } else {
          s"Processed: $event"
        }
      })
      .recoverWithRetries(attempts = 3, {
        case ex: RuntimeException =>
          println(s"Processing failed: ${ex.getMessage}, will retry")
          Source.single("Recovered event")
      })
    
    // 死信队列处理
    val deadLetterSink = Sink.foreach[String](event => 
      println(s"DEAD LETTER: $event")
    )
    
    val normalSink = Sink.foreach[String](event => 
      println(s"SUCCESS: $event")
    )
    
    // 分流到正常流和死信队列
    val (normalFlow, deadLetterFlow) = 
      errorSource
        .via(errorHandlingFlow)
        .alsoTo(Sink.foreach(_ => ())) // 触发处理
        .toMat(normalSink)(Keep.right)
        .watchTermination()(Keep.both)
    
    // 启动流
    normalFlow
    
    println("Robust stream processor started with error handling")
  }
}

// 6. 动态流控制
object DynamicStreamControl {
  def main(args: Array[String]): Unit = {
    implicit val system = ActorSystem("DynamicStreamControl")
    implicit val materializer = ActorMaterializer()
    implicit val ec = system.dispatcher
    
    // 快速事件源
    val fastSource = Source
      .tick(0.millis, 100.millis, "event")
      .zipWithIndex
      .map { case (_, index) => s"Fast event $index" }
    
    // 流控制 - 节流
    val throttledFlow = Flow[String]
      .throttle(1, 1.second, 1, akka.stream.ThrottleMode.shaping)
    
    // 批处理
    val batchFlow = Flow[String]
      .grouped(5) // 每批5个元素
    
    // 动态速率控制
    val dynamicThrottlingFlow = Flow[String]
      .zipWithIndex
      .map {
        case (event, index) =>
          val delay = if (index < 10) 1000 else if (index < 30) 500 else 200
          (event, delay)
      }
      .throttle(1, 1.second, 1, akka.stream.ThrottleMode.shaping)
      .map { case (event, _) => event }
    
    // 运行示例
    fastSource
      .via(dynamicThrottlingFlow)
      .runWith(Sink.foreach(event => println(s"Processed: $event")))
    
    println("Dynamic stream control example started")
  }
}
```

本章详细介绍了分布式系统与Akka Cluster的核心概念和实践，包括Actor模型、Akka Cluster、Akka Streams和Akka HTTP等。通过这些技术，可以构建高度可扩展、高可用的分布式系统，处理实时数据流，并提供高性能的HTTP服务。在实际项目中，Akka生态系统为Scala开发者提供了强大的工具，用于构建复杂的分布式应用程序。