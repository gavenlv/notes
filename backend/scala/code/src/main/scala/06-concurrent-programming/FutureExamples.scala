import scala.concurrent.{Future, Await, ExecutionContext}
import scala.concurrent.duration._
import scala.util.{Success, Failure, Random}
import scala.language.postfixOps

// 使用默认的全局ExecutionContext
import ExecutionContext.Implicits.global

object FutureExamples {
  // 模拟耗时操作
  def longRunningComputation(n: Int): Int = {
    Thread.sleep(Random.nextInt(1000))
    n * n
  }
  
  // 模拟可能失败的操作
  def riskyOperation(n: Int): Int = {
    if (n < 0) throw new IllegalArgumentException("Negative number not allowed")
    Thread.sleep(Random.nextInt(500))
    n * 2
  }
  
  def main(args: Array[String]): Unit = {
    println("=== Future 基本使用示例 ===")
    
    // 1. 创建Future
    val future1 = Future {
      longRunningComputation(5)
    }
    
    val future2 = Future {
      longRunningComputation(3)
    }
    
    // 2. 使用回调处理结果
    future1.onComplete {
      case Success(result) => println(s"Future1完成，结果: $result")
      case Failure(exception) => println(s"Future1失败，异常: ${exception.getMessage}")
    }
    
    // 3. Future组合
    val combinedFuture = for {
      result1 <- future1
      result2 <- future2
    } yield result1 + result2
    
    combinedFuture.foreach(result => println(s"组合结果: $result"))
    
    // 4. Future转换
    val transformedFuture = future1.map(_ * 2)
    transformedFuture.foreach(result => println(s"转换结果: $result"))
    
    // 5. Future链式操作
    val chainedFuture = future1
      .flatMap(x => Future(longRunningComputation(x)))
      .filter(_ > 10)
    
    chainedFuture.onComplete {
      case Success(result) => println(s"链式操作结果: $result")
      case Failure(exception) => println(s"链式操作失败: ${exception.getMessage}")
    }
    
    // 6. 处理可能失败的Future
    val riskyFuture = Future {
      riskyOperation(-5)
    }
    
    riskyFuture.recover {
      case _: IllegalArgumentException => -1
    }.foreach(result => println(s"恢复后的结果: $result"))
    
    // 7. Future序列操作
    val futures = (1 to 5).map(i => Future(longRunningComputation(i))).toList
    val futureSequence = Future.sequence(futures)
    
    futureSequence.foreach { results =>
      println(s"序列操作结果: ${results.mkString(", ")}")
      println(s"总和: ${results.sum}")
    }
    
    // 8. Future遍历操作
    val futureTraverse = Future.traverse(1 to 3)(i => Future(longRunningComputation(i)))
    
    futureTraverse.foreach { results =>
      println(s"遍历操作结果: ${results.mkString(", ")}")
    }
    
    // 等待所有Future完成（仅用于演示，实际代码中应避免）
    Thread.sleep(3000)
    
    println("\n=== Future 工具方法示例 ===")
    
    // 9. Future.firstCompletedOf
    val futureA = Future {
      Thread.sleep(2000)
      "A完成"
    }
    
    val futureB = Future {
      Thread.sleep(1000)
      "B完成"
    }
    
    val firstCompleted = Future.firstCompletedOf(Seq(futureA, futureB))
    firstCompleted.foreach(result => println(s"第一个完成的任务: $result"))
    
    // 10. Future.fold
    val numbers = (1 to 3).map(i => Future(i))
    val folded = Future.foldLeft(numbers)(0)(_ + _)
    folded.foreach(result => println(s"折叠结果: $result"))
    
    // 等待所有示例完成
    Thread.sleep(3000)
    println("所有Future示例完成")
  }
}