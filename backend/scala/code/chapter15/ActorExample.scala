// Actor模型基础示例

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, PoisonPill, Props}
import akka.pattern.ask
import akka.util.Timeout
import scala.concurrent.Await
import scala.concurrent.duration._
import scala.language.postfixOps
import scala.util.{Success, Failure}

// 1. 消息定义
sealed trait GreetingMessage
case class Greet(who: String) extends GreetingMessage
case class GreetResponse(message: String) extends GreetingMessage
case class GetCount() extends GreetingMessage
case class CountResponse(count: Int) extends GreetingMessage

// 2. Greeter Actor
class GreeterActor extends Actor with ActorLogging {
  private var greetingCount = 0
  
  def receive = {
    case Greet(who) =>
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

// 3. 监督策略Actor
class SupervisorActor extends Actor with ActorLogging {
  // 子Actor
  private val child = context.actorOf(Props[GreeterActor], "greeterChild")
  
  // 定义监督策略
  override def supervisorStrategy = 
    akka.actor.OneForOneStrategy(maxNrOfRetries = 3, withinTimeRange = 1.minute) {
      case _: RuntimeException => 
        log.warning("Restarting child due to RuntimeException")
        akka.actor.SupervisorStrategy.restart
        
      case _: IllegalArgumentException => 
        log.warning("Stopping child due to IllegalArgumentException")
        akka.actor.SupervisorStrategy.stop
        
      case _: Exception => 
        log.warning("Escalating exception to parent")
        akka.actor.SupervisorStrategy.escalate
    }
  
  def receive = {
    case msg => 
      log.info(s"Forwarding message to child: $msg")
      child.forward(msg)
  }
}

// 4. 周期任务Actor
class PeriodicTaskActor extends Actor with ActorLogging {
  import context.dispatcher
  
  override def preStart(): Unit = {
    // 使用调度器发送周期性消息
    context.system.scheduler.schedule(
      initialDelay = 0.seconds,
      interval = 1.second,
      receiver = self,
      message = "tick"
    )
  }
  
  private var tickCount = 0
  
  def receive = {
    case "tick" =>
      tickCount += 1
      log.info(s"Tick #$tickCount")
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 5. 路由Actor
import akka.routing.RoundRobinPool

class WorkerActor extends Actor with ActorLogging {
  def receive = {
    case work: String =>
      val result = work.toUpperCase
      log.info(s"Processed work: $work -> $result")
      sender() ! result
      
    case msg =>
      log.warning(s"Received unknown message: $msg")
  }
}

// 6. Actor生命周期
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

// 7. 示例运行器
object ActorExample {
  def main(args: Array[String]): Unit = {
    // 创建Actor系统
    val system = ActorSystem("GreetingSystem")
    implicit val timeout = Timeout(5 seconds)
    import system.dispatcher
    
    println("=== Basic Actor Demo ===")
    
    // 创建Actor
    val greeter = system.actorOf(Props[GreeterActor], "greeter")
    
    // 发送消息
    val future1 = (greeter ? Greet("Alice")).mapTo[GreetResponse]
    val future2 = (greeter ? Greet("Bob")).mapTo[GreetResponse]
    
    // 等待并处理响应
    future1.onComplete {
      case Success(response) => println(s"Alice received: ${response.message}")
      case Failure(ex) => println(s"Failed: ${ex.getMessage}")
    }
    
    future2.onComplete {
      case Success(response) => println(s"Bob received: ${response.message}")
      case Failure(ex) => println(s"Failed: ${ex.getMessage}")
    }
    
    // 获取计数
    val countFuture = (greeter ? GetCount()).mapTo[CountResponse]
    countFuture.onComplete {
      case Success(response) => println(s"Total greetings: ${response.count}")
      case Failure(ex) => println(s"Failed: ${ex.getMessage}")
    }
    
    // 等待之前的操作完成
    Thread.sleep(2000)
    
    println("\n=== Supervisor Demo ===")
    
    // 创建监督者
    val supervisor = system.actorOf(Props[SupervisorActor], "supervisor")
    
    // 发送消息测试生命周期
    supervisor ! "normal"
    Thread.sleep(1000)
    
    // 测试重启
    supervisor ! "crash"  // 将触发子Actor重启
    Thread.sleep(1000)
    
    // 重启后应能正常处理
    supervisor ! "normal"
    Thread.sleep(1000)
    
    println("\n=== Periodic Task Demo ===")
    
    // 创建周期任务Actor
    val periodicTask = system.actorOf(Props[PeriodicTaskActor], "periodicTask")
    
    // 让它运行几秒钟
    Thread.sleep(5000)
    
    // 停止Actor
    system.stop(periodicTask)
    
    println("\n=== Routing Demo ===")
    
    // 创建路由器
    val router = system.actorOf(
      RoundRobinPool(3).props(Props[WorkerActor]),
      "workerRouter"
    )
    
    // 发送多个工作项
    val workItems = List("task1", "task2", "task3", "task4", "task5")
    workItems.foreach { work =>
      router ! work
    }
    
    // 等待工作完成
    Thread.sleep(2000)
    
    println("\n=== Lifecycle Demo ===")
    
    // 创建生命周期Actor
    val lifecycleActor = system.actorOf(Props[LifecycleActor], "lifecycleActor")
    
    // 发送正常消息
    lifecycleActor ! "normal"
    Thread.sleep(1000)
    
    // 发送崩溃消息
    lifecycleActor ! "crash"  // 将触发重启
    Thread.sleep(1000)
    
    // 重启后再次发送正常消息
    lifecycleActor ! "normal"
    Thread.sleep(1000)
    
    // 停止Actor
    system.stop(lifecycleActor)
    Thread.sleep(1000)
    
    // 关闭Actor系统
    system.terminate()
  }
}