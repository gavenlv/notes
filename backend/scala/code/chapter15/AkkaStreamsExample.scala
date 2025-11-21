// Akka Streams示例

import akka.actor.ActorSystem
import akka.stream.scaladsl.{Flow, Keep, RunnableGraph, Sink, Source}
import akka.stream.{ActorMaterializer, ThrottleMode}
import akka.{Done, NotUsed}
import spray.json._

import java.nio.file.Paths
import scala.concurrent.Future
import scala.util.{Success, Failure}

// 1. 基本流概念
object BasicStreams {
  def runBasicExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("=== Basic Stream Demo ===")
    
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
  def runBackpressureExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("\n=== Backpressure Handling Demo ===")
    
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
  def runStreamCompositionExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("\n=== Stream Composition Demo ===")
    
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
    println("--- Merged Source ---")
    mergedSource.take(10).runWith(Sink.foreach(println))
    
    Thread.sleep(1000)
    
    println("\n--- Zipped Source ---")
    zippedSource.runWith(Sink.foreach(println))
    
    Thread.sleep(1000)
    
    println("\n--- Concatenated Source ---")
    concatenatedSource.runWith(Sink.foreach(println))
    
    Thread.sleep(1000)
  }
}

// 4. 动态流控制
object DynamicFlowControl {
  def runDynamicFlowControlExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("\n=== Dynamic Flow Control Demo ===")
    
    // 使用throttle控制流速率
    val throttledFlow = Flow[Int]
      .throttle(1, 1.second, 1, ThrottleMode.shaping)
    
    println("--- Throttled Flow ---")
    Source(1 to 5)
      .via(throttledFlow)
      .runWith(Sink.foreach(n => println(s"Throttled: $n")))
    
    // 使用grouped处理批次
    val batchFlow = Flow[Int]
      .grouped(3)  // 每批3个元素
    
    println("\n--- Batched Flow ---")
    Source(1 to 10)
      .via(batchFlow)
      .runWith(Sink.foreach(batch => println(s"Batch: $batch")))
    
    // 使用sliding处理滑动窗口
    val slidingFlow = Flow[Int]
      .sliding(3, 1)  // 窗口大小3，滑动步长1
    
    println("\n--- Sliding Window Flow ---")
    Source(1 to 7)
      .via(slidingFlow)
      .runWith(Sink.foreach(window => println(s"Window: $window")))
  }
}

// 5. 错误处理
object ErrorHandling {
  def runErrorHandlingExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("\n=== Error Handling Demo ===")
    
    // recover - 恢复处理
    val recoverFlow = Flow[String]
      .map(s => s.toInt)
      .recover { case _: NumberFormatException => -1 }
    
    println("--- Recover Flow ---")
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
    
    println("\n--- Retry Flow ---")
    Source(List("1", "2", "abc", "4", "5"))
      .via(retryFlow)
      .runWith(Sink.foreach(n => println(s"Processed with retry: $n")))
  }
}

// 6. 文件处理
object FileProcessing {
  def runFileProcessingExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    import java.nio.file.Files
    import java.io.PrintWriter
    
    println("\n=== File Processing Demo ===")
    
    // 创建临时文件
    val tempFile = Files.createTempFile("streams-example", ".txt")
    val writer = new PrintWriter(tempFile.toFile)
    (1 to 100).foreach(i => writer.println(s"Line $i: The quick brown fox jumps over the lazy dog"))
    writer.close()
    
    // 从文件读取
    val fileSource = Source.fromIterator(() => 
      scala.io.Source.fromFile(tempFile.toFile).getLines()
    )
    
    println("--- File Stream Processing ---")
    fileSource
      .filter(_.contains("lazy"))
      .map(_.toUpperCase)
      .take(5)
      .runWith(Sink.foreach(println))
    
    // 写入文件
    val outputPath = tempFile.getParent.resolve("output.txt")
    val outputPath2 = tempFile.getParent.resolve("output2.txt")
    
    val lines = List("Line 1: Hello World", "Line 2: Akka Streams", "Line 3: File Processing")
    val fileSink = FileIO.toPath(outputPath)
    
    println("\n--- Writing to File ---")
    Source(lines)
      .map(line => ByteString(s"$line\n"))
      .runWith(fileSink)
      .onComplete {
        case Success(_) => println(s"Successfully wrote to $outputPath")
        case Failure(ex) => println(s"Failed to write: ${ex.getMessage}")
      }
    
    // 使用其他方法写入
    Source(lines)
      .runWith(FileIO.toPath(outputPath2))
      .onComplete {
        case Success(_) => println(s"Successfully wrote to $outputPath2")
        case Failure(ex) => println(s"Failed to write: ${ex.getMessage}")
      }
  }
}

// 7. JSON处理
object JsonProcessing {
  // 简单的JSON协议
  case class Person(id: Int, name: String, age: Int)
  
  object PersonJsonProtocol extends DefaultJsonProtocol {
    implicit val personFormat = jsonFormat3(Person)
  }
  
  def runJsonProcessingExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    import PersonJsonProtocol._
    
    println("\n=== JSON Processing Demo ===")
    
    // 创建人员数据
    val people = List(
      Person(1, "Alice", 30),
      Person(2, "Bob", 25),
      Person(3, "Charlie", 35),
      Person(4, "Diana", 28),
      Person(5, "Eve", 32)
    )
    
    // 转换为JSON
    val jsonFlow = Flow[Person].map(_.toJson.compactPrint)
    
    println("--- People to JSON ---")
    Source(people)
      .via(jsonFlow)
      .runWith(Sink.foreach(json => println(json)))
    
    Thread.sleep(1000)
    
    // 从JSON解析
    val parseFlow = Flow[String].map(_.parseJson.convertTo[Person])
    
    println("\n--- JSON to People ---")
    Source(people)
      .map(_.toJson.compactPrint)
      .via(parseFlow)
      .filter(_.age >= 30)
      .runWith(Sink.foreach(person => println(s"${person.name} is ${person.age} years old")))
  }
}

// 8. 自定义处理阶段
object CustomStages {
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
  
  // 自定义聚合阶段
  class RunningAverage extends GraphStage[FlowShape[Int, Double]] {
    val in = Inlet[Int]("RunningAverage.in")
    val out = Outlet[Double]("RunningAverage.out")
    
    override val shape = FlowShape(in, out)
    
    override def createLogic(inheritedAttributes: Attributes): GraphStageLogic = {
      var sum = 0L
      var count = 0L
      
      new GraphStageLogic(shape) {
        setHandler(in, new InHandler {
          override def onPush(): Unit = {
            val elem = grab(in)
            sum += elem
            count += 1
            push(out, sum.toDouble / count)
          }
        })
        
        setHandler(out, new OutHandler {
          override def onPull(): Unit = {
            pull(in)
          }
        })
      }
    }
  }
  
  def runCustomStagesExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("\n=== Custom Stages Demo ===")
    
    // 使用自定义过滤阶段
    val evenFilterFlow = Flow.fromGraph(new EvenFilter)
    
    println("--- Even Filter Stage ---")
    Source(1 to 10)
      .via(evenFilterFlow)
      .runWith(Sink.foreach(println))
    
    Thread.sleep(1000)
    
    // 使用自定义聚合阶段
    val runningAverageFlow = Flow.fromGraph(new RunningAverage)
    
    println("\n--- Running Average Stage ---")
    Source(1 to 10)
      .via(runningAverageFlow)
      .runWith(Sink.foreach(avg => println(f"Average: $avg%.2f")))
  }
}

// 9. 动态流图
object DynamicGraph {
  import akka.stream.scaladsl.{Broadcast, Concat, GraphDSL, Merge}
  import GraphDSL.Implicits._
  
  def runDynamicGraphExample(implicit system: ActorSystem, materializer: ActorMaterializer): Unit = {
    import system.dispatcher
    
    println("\n=== Dynamic Graph Demo ===")
    
    // 创建动态流图
    val dynamicGraph = RunnableGraph.fromGraph(GraphDSL.create() { implicit builder =>
      import GraphDSL.Implicits._
      
      // 创建组件
      val source1 = Source(1 to 5)
      val source2 = Source(6 to 10)
      val broadcast = builder.add(Broadcast[Int](2))
      val merge = builder.add(Merge[Int](2))
      val doubleFlow = Flow[Int].map(_ * 2)
      val tripleFlow = Flow[Int].map(_ * 3)
      val sumFlow = Flow[(Int, Int)].map { case (a, b) => a + b }
      val concat = builder.add(Concat[Int]())
      val sink = Sink.foreach[(Int, Int)](println)
      
      // 连接组件
      source1 ~> broadcast.in
      broadcast.out(0) ~> doubleFlow ~> merge.in(0)
      broadcast.out(1) ~> tripleFlow ~> merge.in(1)
      merge.out ~> sumFlow ~> sink
      
      source2 ~> concat.in(0)
      merge.out ~> concat.in(1)
      concat.out ~> Sink.foreach(println)
      
      ClosedShape
    })
    
    dynamicGraph.run()
  }
}

// 运行所有示例
object AkkaStreamsExample {
  def main(args: Array[String]): Unit = {
    implicit val system: ActorSystem = ActorSystem("AkkaStreamsExample")
    implicit val materializer: ActorMaterializer = ActorMaterializer()
    
    try {
      BasicStreams.runBasicExample
      Thread.sleep(1000)
      
      BackpressureHandling.runBackpressureExample
      Thread.sleep(3000)
      
      StreamComposition.runStreamCompositionExample
      
      DynamicFlowControl.runDynamicFlowControlExample
      Thread.sleep(5000)
      
      ErrorHandling.runErrorHandlingExample
      Thread.sleep(1000)
      
      FileProcessing.runFileProcessingExample
      Thread.sleep(1000)
      
      JsonProcessing.runJsonProcessingExample
      Thread.sleep(1000)
      
      CustomStages.runCustomStagesExample
      Thread.sleep(1000)
      
      DynamicGraph.runDynamicGraphExample
      Thread.sleep(2000)
      
    } finally {
      system.terminate()
    }
  }
}