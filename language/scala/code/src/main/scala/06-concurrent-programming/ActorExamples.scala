import akka.actor.typed.{ActorSystem, Behavior}
import akka.actor.typed.scaladsl.{AbstractBehavior, ActorContext, Behaviors}
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.AbstractBehavior
import scala.concurrent.duration._
import scala.language.postfixOps

// 定义消息类型
object CounterActor {
  sealed trait Command
  case object Increment extends Command
  case object Decrement extends Command
  case object GetCount extends Command
  case class CountResponse(count: Int)
  
  def apply(): Behavior[Command] = Behaviors.setup { context =>
    new CounterActor(context)
  }
}

class CounterActor(context: ActorContext[CounterActor.Command]) 
  extends AbstractBehavior[CounterActor.Command](context) {
  
  private var count = 0
  
  override def onMessage(msg: CounterActor.Command): Behavior[CounterActor.Command] = {
    msg match {
      case CounterActor.Increment =>
        count += 1
        context.log.info(s"计数器增加到: $count")
        this
        
      case CounterActor.Decrement =>
        count -= 1
        context.log.info(s"计数器减少到: $count")
        this
        
      case CounterActor.GetCount =>
        context.log.info(s"当前计数: $count")
        this
    }
  }
}

// 计算器Actor
object CalculatorActor {
  sealed trait Command
  case class Add(x: Int, y: Int, replyTo: akka.actor.typed.ActorRef[Result]) extends Command
  case class Subtract(x: Int, y: Int, replyTo: akka.actor.typed.ActorRef[Result]) extends Command
  case class Multiply(x: Int, y: Int, replyTo: akka.actor.typed.ActorRef[Result]) extends Command
  case class Divide(x: Int, y: Int, replyTo: akka.actor.typed.ActorRef[Result]) extends Command
  
  sealed trait Result
  case class CalculationResult(result: Double) extends Result
  case object DivisionByZero extends Result
  
  def apply(): Behavior[Command] = Behaviors.receive { (context, message) =>
    message match {
      case Add(x, y, replyTo) =>
        replyTo ! CalculationResult(x + y)
        Behaviors.same
        
      case Subtract(x, y, replyTo) =>
        replyTo ! CalculationResult(x - y)
        Behaviors.same
        
      case Multiply(x, y, replyTo) =>
        replyTo ! CalculationResult(x * y)
        Behaviors.same
        
      case Divide(x, y, replyTo) =>
        if (y != 0) {
          replyTo ! CalculationResult(x.toDouble / y)
        } else {
          replyTo ! DivisionByZero
        }
        Behaviors.same
    }
  }
}

// 监督Actor示例
object SupervisorActor {
  sealed trait Command
  case object StartChild extends Command
  case class FailChild(message: String) extends Command
  
  def apply(): Behavior[Command] = Behaviors.setup { context =>
    var child: akka.actor.typed.ActorRef[ChildActor.Command] = null
    
    Behaviors.receiveMessage {
      case StartChild =>
        child = context.spawn(ChildActor(), "child")
        context.log.info("子Actor已创建")
        Behaviors.same
        
      case FailChild(message) =>
        if (child != null) {
          child ! ChildActor.Fail(message)
        }
        Behaviors.same
    }
  }
}

object ChildActor {
  sealed trait Command
  case class Fail(message: String) extends Command
  
  def apply(): Behavior[Command] = Behaviors.receive { (context, message) =>
    message match {
      case Fail(message) =>
        context.log.info(s"子Actor即将失败: $message")
        throw new RuntimeException(message)
    }
  }
}

// 主示例程序
object ActorExamples {
  def main(args: Array[String]): Unit = {
    println("=== Akka Actor 基本使用示例 ===")
    
    // 1. 创建Actor系统和CounterActor
    val counterSystem = ActorSystem(CounterActor(), "counter-system")
    
    // 发送消息
    counterSystem ! CounterActor.Increment
    counterSystem ! CounterActor.Increment
    counterSystem ! CounterActor.Decrement
    counterSystem ! CounterActor.GetCount
    
    // 等待处理
    Thread.sleep(1000)
    
    // 2. 使用CalculatorActor
    val calculatorSystem = ActorSystem(CalculatorActor(), "calculator-system")
    val calculatorActor = calculatorSystem
    
    // 创建回复Actor
    val replyActor = calculatorSystem.systemActorOf(
      Behaviors.receive[CalculatorActor.Result] { (context, message) =>
        message match {
          case CalculatorActor.CalculationResult(result) =>
            context.log.info(s"计算结果: $result")
            Behaviors.same
          case CalculatorActor.DivisionByZero =>
            context.log.info("除零错误")
            Behaviors.same
        }
      },
      "reply-actor"
    )
    
    // 发送计算消息
    calculatorActor ! CalculatorActor.Add(10, 5, replyActor)
    calculatorActor ! CalculatorActor.Subtract(10, 5, replyActor)
    calculatorActor ! CalculatorActor.Multiply(10, 5, replyActor)
    calculatorActor ! CalculatorActor.Divide(10, 2, replyActor)
    calculatorActor ! CalculatorActor.Divide(10, 0, replyActor)
    
    // 等待处理
    Thread.sleep(1000)
    
    // 3. 简单的Actor交互示例
    println("\n--- Actor交互示例 ---")
    val greeterSystem = ActorSystem(Greeter(), "greeter-system")
    
    val helloActor = greeterSystem
    val greetActor = greeterSystem.systemActorOf(GreetActor(), "greet-actor")
    
    // 发送问候消息
    helloActor ! Hello("Alice", greetActor)
    
    // 等待处理
    Thread.sleep(1000)
    
    // 关闭Actor系统
    counterSystem.terminate()
    calculatorSystem.terminate()
    greeterSystem.terminate()
    
    println("所有Actor示例完成")
  }
}

// 问候Actor示例
object Greeter {
  sealed trait Command
  case class Hello(name: String, replyTo: akka.actor.typed.ActorRef[GreetActor.Command]) extends Command
  
  def apply(): Behavior[Command] = Behaviors.receive { (context, message) =>
    message match {
      case Hello(name, replyTo) =>
        context.log.info(s"收到问候请求: $name")
        replyTo ! GreetActor.Greet(s"Hello, $name!")
        Behaviors.same
    }
  }
}

object GreetActor {
  sealed trait Command
  case class Greet(message: String) extends Command
  
  def apply(): Behavior[Command] = Behaviors.receive { (context, message) =>
    message match {
      case Greet(message) =>
        context.log.info(s"收到问候: $message")
        Behaviors.same
    }
  }
}