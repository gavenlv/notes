# 第9章：与Java互操作

Scala与Java的互操作性是其最强大的特性之一。由于Scala编译为Java字节码并在JVM上运行，Scala代码可以无缝使用Java类库，同时Java代码也可以调用Scala代码。本章将深入探讨Scala与Java之间的互操作技巧和最佳实践。

## 9.1 在Scala中使用Java类库

### 9.1.1 导入和使用Java类

Scala可以直接使用Java标准库和第三方库中的类：

```scala
// 导入Java类
import java.util.{ArrayList, HashMap, List as JList, Map as JMap}
import java.io.{File, FileInputStream}
import java.nio.file.{Files, Paths}
import java.time.{LocalDate, LocalDateTime}
import java.util.concurrent.{Executors, Future as JFuture}

// 使用Java集合
object JavaCollectionsInScala {
  def demo(): Unit = {
    // 创建Java列表
    val javaList = new ArrayList[String]()
    javaList.add("Scala")
    javaList.add("Java")
    javaList.add("Kotlin")
    
    // 在Scala中使用Java列表
    println("Java list size: " + javaList.size())
    println("Element at index 0: " + javaList.get(0))
    
    // 转换为Scala集合
    val scalaList: List[String] = javaList.asScala.toList
    println("Scala list: " + scalaList)
    
    // 创建Java映射
    val javaMap = new HashMap[String, Integer]()
    javaMap.put("one", 1)
    javaMap.put("two", 2)
    javaMap.put("three", 3)
    
    // 转换为Scala映射
    val scalaMap: Map[String, Int] = javaMap.asScala.toMap
    println("Scala map: " + scalaMap)
  }
}
```

### 9.1.2 Java集合转换

Scala提供了与Java集合之间的自动转换：

```scala
import scala.jdk.CollectionConverters._

object CollectionConversion {
  def demonstrate(): Unit = {
    // Scala集合转Java集合
    val scalaList = List("apple", "banana", "cherry")
    val javaList: java.util.List[String] = scalaList.asJava
    
    val scalaMap = Map("x" -> 1, "y" -> 2, "z" -> 3)
    val javaMap: java.util.Map[String, Int] = scalaMap.asJava
    
    val scalaSet = Set(1, 2, 3, 4, 5)
    val javaSet: java.util.Set[Int] = scalaSet.asJava
    
    println("Converted Java list: " + javaList)
    println("Converted Java map: " + javaMap)
    println("Converted Java set: " + javaSet)
    
    // Java集合转Scala集合
    val anotherJavaList = new java.util.ArrayList[String]()
    anotherJavaList.add("dog")
    anotherJavaList.add("cat")
    anotherJavaList.add("mouse")
    
    val backToScala: List[String] = anotherJavaList.asScala.toList
    println("Back to Scala list: " + backToScala)
  }
}
```

### 9.1.3 使用Java时间API

```scala
import java.time._
import java.time.format.DateTimeFormatter

object JavaTimeAPI {
  def demonstrate(): Unit = {
    // 当前日期和时间
    val today = LocalDate.now()
    val now = LocalDateTime.now()
    
    println(s"Today: $today")
    println(s"Now: $now")
    
    // 创建特定日期
    val birthday = LocalDate.of(1990, Month.JANUARY, 15)
    println(s"Birthday: $birthday")
    
    // 日期计算
    val nextWeek = today.plusWeeks(1)
    val lastMonth = today.minusMonths(1)
    
    println(s"Next week: $nextWeek")
    println(s"Last month: $lastMonth")
    
    // 格式化日期
    val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
    val formattedDateTime = now.format(formatter)
    println(s"Formatted datetime: $formattedDateTime")
    
    // 解析日期
    val parsedDate = LocalDate.parse("2023-12-25")
    println(s"Parsed date: $parsedDate")
    
    // 计算两个日期之间的天数
    val daysBetween = java.time.temporal.ChronoUnit.DAYS.between(birthday, today)
    println(s"Days between birthday and today: $daysBetween")
  }
}
```

### 9.1.4 Java异常处理

Scala对Java异常进行了包装，使其更符合函数式编程风格：

```scala
import java.io.{FileNotFoundException, FileReader, IOException}

object JavaExceptions {
  def readFileTraditional(filepath: String): String = {
    try {
      val reader = new FileReader(filepath)
      val content = reader.read().toString
      reader.close()
      content
    } catch {
      case ex: FileNotFoundException => s"File not found: ${ex.getMessage}"
      case ex: IOException => s"IO error: ${ex.getMessage}"
    }
  }
  
  // 使用Try包装Java异常
  import scala.util.{Try, Success, Failure}
  
  def readFileFunctional(filepath: String): Try[String] = Try {
    val reader = new FileReader(filepath)
    val content = reader.read().toString
    reader.close()
    content
  }
  
  def demonstrate(): Unit = {
    val fileExists = "existing_file.txt"  // 假设此文件存在
    val fileNotExists = "non_existing_file.txt"  // 此文件不存在
    
    // 传统方式
    println("Traditional exception handling:")
    println(readFileTraditional(fileExists))
    println(readFileTraditional(fileNotExists))
    
    // 函数式方式
    println("\nFunctional exception handling:")
    val result1 = readFileFunctional(fileExists)
    val result2 = readFileFunctional(fileNotExists)
    
    result1 match {
      case Success(content) => println(s"File content: $content")
      case Failure(ex) => println(s"Error reading file: ${ex.getMessage}")
    }
    
    result2 match {
      case Success(content) => println(s"File content: $content")
      case Failure(ex) => println(s"Error reading file: ${ex.getMessage}")
    }
  }
}
```

## 9.2 在Java中使用Scala代码

### 9.2.1 从Java调用Scala代码

```scala
// 在Scala中定义的类，将被Java调用
// 文件: scala/com/example/ScalaClass.scala

package com.example

class ScalaClass(private var name: String) {
  // 公共方法
  def getName: String = name
  
  def setName(name: String): Unit = {
    this.name = name
  }
  
  // 带默认参数的方法
  def greet(greeting: String = "Hello"): String = s"$greeting, $name!"
  
  // 使用Scala特性
  def processList[T](list: List[T]): List[T] = list.filter(_ != null)
  
  // 选项类型
  def findElement[T](list: List[T], element: T): Option[T] = list.find(_ == element)
  
  // 元组返回值
  def divideAndRemainder(dividend: Int, divisor: Int): (Int, Int) = (dividend / divisor, dividend % divisor)
}

// Scala对象（单例）
object ScalaUtils {
  def add(a: Int, b: Int): Int = a + b
  
  def multiply(a: Int, b: Int): Int = a * b
  
  def factorial(n: Int): BigInt = {
    if (n <= 1) 1
    else n * factorial(n - 1)
  }
}

// Scala case class
case class Person(name: String, age: Int) {
  def isAdult: Boolean = age >= 18
  
  def greet: String = s"Hi, I'm $name and I'm $age years old"
}
```

```java
// 在Java中调用Scala代码
// 文件: src/main/java/com/example/JavaCaller.java

package com.example;

import scala.collection.JavaConverters;
import scala.collection.immutable.List;
import scala.Option;
import scala.Tuple2;

public class JavaCaller {
    public static void main(String[] args) {
        // 创建Scala类的实例
        ScalaClass scalaObj = new ScalaClass("Alice");
        
        // 调用Scala方法
        System.out.println("Name: " + scalaObj.getName());
        
        // 使用默认参数
        System.out.println("Greeting with default: " + scalaObj.greet());
        
        // 提供参数
        System.out.println("Greeting with custom: " + scalaObj.greet("Hi there"));
        
        // 修改状态
        scalaObj.setName("Bob");
        System.out.println("New name: " + scalaObj.getName());
        
        // 调用Scala对象的方法
        int sum = ScalaUtils.add(5, 3);
        int product = ScalaUtils.multiply(4, 7);
        System.out.println("Sum: " + sum + ", Product: " + product);
        
        // 调用返回Scala类型的方法
        // 1. 处理Scala List
        java.util.List<String> javaList = java.util.Arrays.asList("A", null, "B", null, "C");
        List<String> scalaList = JavaConverters.asScalaBuffer(javaList).toList();
        List<String> filteredList = scalaObj.processList(scalaList);
        
        // 转换回Java集合
        java.util.List<String> filteredJavaList = JavaConverters.seqAsJavaList(filteredList);
        System.out.println("Filtered list: " + filteredJavaList);
        
        // 2. 处理Option类型
        Option<String> found = scalaObj.findElement(scalaList, "B");
        if (found.isDefined()) {
            System.out.println("Found: " + found.get());
        } else {
            System.out.println("Not found");
        }
        
        // 3. 处理元组
        Tuple2<Integer, Integer> result = scalaObj.divideAndRemainder(17, 5);
        int quotient = result._1();
        int remainder = result._2();
        System.out.println("17 / 5 = " + quotient + " remainder " + remainder);
        
        // 使用Scala case class
        Person person = new Person("Charlie", 25);
        System.out.println("Person name: " + person.name());
        System.out.println("Person age: " + person.age());
        System.out.println("Is adult: " + person.isAdult());
        System.out.println(person.greet());
    }
}
```

### 9.2.2 在Java中使用Scala特性

```scala
// 高级Scala特性，供Java调用
package com.example

import scala.concurrent._
import ExecutionContext.Implicits.global
import scala.util.{Success, Failure}

object AdvancedScalaFeatures {
  // 高阶函数
  def processItems[T, R](items: List[T], processor: T => R): List[R] = {
    items.map(processor)
  }
  
  // 模式匹配
  def describeNumber(num: Int): String = num match {
    case 0 => "Zero"
    case x if x > 0 => s"Positive: $x"
    case x => s"Negative: $x"
  }
  
  // Future异步操作
  def asyncOperation(input: String): Future[String] = Future {
    Thread.sleep(1000)  // 模拟耗时操作
    s"Processed: $input"
  }
  
  // 隐式转换
  implicit class StringOps(s: String) {
    def shout: String = s.toUpperCase + "!"
  }
  
  // 使用隐式转换
  def useStringOps(input: String): String = input.shout
}
```

```java
// 在Java中使用高级Scala特性
package com.example;

import scala.collection.JavaConverters;
import scala.collection.immutable.List;
import scala.concurrent.Future;
import scala.concurrent.Await;
import scala.concurrent.duration.Duration;
import scala.util.Failure;
import scala.util.Success;
import scala.util.Try;

public class AdvancedJavaCaller {
    public static void main(String[] args) throws Exception {
        // 使用高阶函数
        java.util.List<Integer> numbers = java.util.Arrays.asList(1, 2, 3, 4, 5);
        List<Integer> scalaNumbers = JavaConverters.asScalaBuffer(numbers).toList();
        
        // 定义处理器函数
        List<Integer> squared = AdvancedScalaFeatures.processItems(scalaNumbers, 
            x -> x * x);
        
        // 转换回Java集合
        java.util.List<Integer> squaredJava = JavaConverters.seqAsJavaList(squared);
        System.out.println("Squared numbers: " + squaredJava);
        
        // 使用模式匹配结果
        System.out.println("Describe 0: " + AdvancedScalaFeatures.describeNumber(0));
        System.out.println("Describe 10: " + AdvancedScalaFeatures.describeNumber(10));
        System.out.println("Describe -5: " + AdvancedScalaFeatures.describeNumber(-5));
        
        // 处理Future
        Future<String> futureResult = AdvancedScalaFeatures.asyncOperation("Java Input");
        
        // 等待Future完成
        String result = Await.result(futureResult, Duration.Inf());
        System.out.println("Async result: " + result);
        
        // 使用隐式转换（需要通过特定的包装器方法）
        String shoutingResult = AdvancedScalaFeatures.useStringOps("hello from java");
        System.out.println("Shouting result: " + shoutingResult);
    }
}
```

## 9.3 Scala与Java的转换细节

### 9.3.1 基本类型转换

Scala基本类型与Java基本类型之间的转换：

```scala
object TypeConversion {
  // Scala值类型与Java包装类型的转换
  def demonstrateTypeConversion(): Unit = {
    // Scala Int -> java.lang.Integer
    val scalaInt: Int = 42
    val javaInteger: java.lang.Integer = java.lang.Integer.valueOf(scalaInt)
    
    // java.lang.Integer -> Scala Int
    val backToInt: Int = javaInteger.intValue()
    
    // 类似地，其他基本类型也可以这样转换：
    val scalaDouble: Double = 3.14
    val javaDouble: java.lang.Double = java.lang.Double.valueOf(scalaDouble)
    
    val scalaBoolean: Boolean = true
    val javaBoolean: java.lang.Boolean = java.lang.Boolean.valueOf(scalaBoolean)
    
    println(s"Scala Int: $scalaInt, Java Integer: $javaInteger")
    println(s"Back to Int: $backToInt")
    println(s"Scala Double: $scalaDouble, Java Double: $javaDouble")
    println(s"Scala Boolean: $scalaBoolean, Java Boolean: $javaBoolean")
  }
  
  // 数组转换
  def demonstrateArrayConversion(): Unit = {
    // Scala数组 -> Java数组
    val scalaArray: Array[String] = Array("Scala", "Java", "Kotlin")
    val javaArray: java.lang.reflect.Array = java.util.Arrays.copyOf(scalaArray, scalaArray.length)
    
    // Java数组 -> Scala数组
    val anotherJavaArray = java.lang.reflect.Array.newInstance(classOf[String], 3)
    java.lang.reflect.Array.set(anotherJavaArray, 0, "One")
    java.lang.reflect.Array.set(anotherJavaArray, 1, "Two")
    java.lang.reflect.Array.set(anotherJavaArray, 2, "Three")
    
    // 使用JavaConverters进行更方便的转换
    val javaList = new java.util.ArrayList[String]()
    javaList.add("A")
    javaList.add("B")
    javaList.add("C")
    
    val scalaArrayFromList = javaList.toArray(Array.empty[String])
    println(s"Scala array from Java list: ${scalaArrayFromList.mkString(", ")}")
  }
}
```

### 9.3.2 函数与接口转换

Scala函数可以轻松转换为Java接口：

```scala
import java.util.function.{Consumer, Function, Predicate}
import java.util.{Comparator, List as JList, ArrayList}
import scala.jdk.FunctionConverters._

object FunctionInterfaceConversion {
  // Scala函数转Java函数接口
  def demonstrateConversion(): Unit = {
    val javaList: JList[String] = new ArrayList[String]()
    javaList.add("apple")
    javaList.add("banana")
    javaList.add("cherry")
    
    // 1. Scala函数转Java Consumer
    val scalaConsumer: String => Unit = println
    val javaConsumer: Consumer[String] = scalaConsumer.asJava
    javaList.forEach(javaConsumer)
    
    // 2. Scala函数转Java Function
    val scalaFunction: String => Int = _.length
    val javaFunction: Function[String, Integer] = scalaFunction.asJava
    javaList.stream().map(javaFunction).forEach(System.out::println)
    
    // 3. Scala函数转Java Predicate
    val scalaPredicate: String => Boolean = _.length > 5
    val javaPredicate: Predicate[String] = scalaPredicate.asJava
    javaList.removeIf(javaPredicate)
    println(s"After removal: $javaList")
    
    // 4. Scala函数转Java Comparator
    val scalaComparator: (String, String) => Int = (a, b) => a.length - b.length
    val javaComparator: Comparator[String] = scalaComparator.asJava
    javaList.sort(javaComparator)
    println(s"After sorting: $javaList")
  }
  
  // Java接口转Scala函数
  def javaToScalaConversion(): Unit = {
    val javaList: JList[String] = new ArrayList[String]()
    javaList.add("first")
    javaList.add("second")
    javaList.add("third")
    
    // Java Consumer转Scala函数
    val javaConsumer: Consumer[String] = System.out::println
    val scalaConsumer: String => Unit = javaConsumer.asScala
    javaList.forEach(javaConsumer)
    
    // Java Function转Scala函数
    val javaFunction: Function[String, Integer] = String::length
    val scalaFunction: String => Int = javaFunction.asScala
    val lengths = javaList.stream().map(javaFunction).toArray()
    println(s"Lengths: ${lengths.mkString(", ")}")
  }
}
```

### 9.3.3 注解处理

Scala类和方法可以像Java一样使用注解：

```scala
import java.beans.{BeanProperty, Transient}
import javax.annotation.{PostConstruct, PreDestroy}
import javax.persistence.{Entity, Id, Column}

// 使用Java标准注解
class Person(
  @BeanProperty var name: String,
  @BeanProperty var age: Int,
  @Transient private var secret: String
) {
  @PostConstruct
  def init(): Unit = {
    println("Person bean initialized")
  }
  
  @PreDestroy
  def cleanup(): Unit = {
    println("Person bean cleaned up")
  }
}

// 使用JPA注解
@Entity
class User(
  @Id
  @Column(name = "user_id")
  var id: Long,
  
  @Column(name = "username")
  var username: String,
  
  @Column(name = "password")
  var password: String
) {
  // JPA需要无参构造器
  def this() = this(0, "", "")
}

// 自定义注解
class MyAnnotation(value: String) extends scala.annotation.StaticAnnotation

@MyAnnotation("This is a class annotation")
class AnnotatedClass {
  @MyAnnotation("This is a method annotation")
  def annotatedMethod(): String = "Annotated method"
}

object AnnotationExample {
  def demonstrate(): Unit = {
    val person = new Person("Alice", 30, "My secret")
    println(s"Person: ${person.getName}, Age: ${person.getAge}")
    
    val user = new User(1, "john", "password")
    println(s"User: ${user.username}")
    
    val annotatedClass = new AnnotatedClass()
    println(annotatedClass.annotatedMethod())
  }
}
```

## 9.4 使用Java第三方库

### 9.4.1 使用Spring框架

```scala
import org.springframework.stereotype.{Component, Service}
import org.springframework.beans.factory.annotation.{Autowired, Value}
import org.springframework.context.annotation.{Configuration, ComponentScan}
import org.springframework.web.bind.annotation.{RestController, RequestMethod, RequestMapping}
import org.springframework.http.ResponseEntity

// Spring组件
@Component
class ScalaComponent {
  def doSomething(): String = "Something done in Scala"
}

@Service
class ScalaService {
  @Autowired
  private val component: ScalaComponent = null
  
  def process(): String = s"Processed by ${component.doSomething()}"
}

// Spring配置
@Configuration
@ComponentScan(Array("com.example"))
class ScalaConfig

// Spring REST控制器
@RestController
@RequestMapping(Array("/api"))
class ScalaController {
  
  @Value("${app.message}")
  private val defaultMessage: String = "Hello from Scala"
  
  @RequestMapping(value = Array("/hello"), method = Array(RequestMethod.GET))
  def hello(): ResponseEntity[String] = {
    ResponseEntity.ok(defaultMessage)
  }
  
  @RequestMapping(value = Array("/process"), method = Array(RequestMethod.GET))
  def process(): ResponseEntity[String] = {
    val service = new ScalaService()
    ResponseEntity.ok(service.process())
  }
}
```

### 9.4.2 使用Jackson进行JSON处理

```scala
import com.fasterxml.jackson.annotation.{JsonProperty, JsonIgnoreProperties}
import com.fasterxml.jackson.databind.{ObjectMapper, SerializationFeature}
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import com.fasterxml.jackson.module.scala.experimental.ScalaObjectMapper

// JSON序列化的类
@JsonIgnoreProperties(ignoreUnknown = true)
case class User(
  @JsonProperty("id") id: Long,
  @JsonProperty("name") name: String,
  @JsonProperty("email") email: String,
  @JsonProperty("roles") roles: List[String]
)

object JsonExample {
  // 创建配置了Scala模块的ObjectMapper
  val mapper = new ObjectMapper() with ScalaObjectMapper
  mapper.registerModule(DefaultScalaModule)
  mapper.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false)
  
  def serializeToJson(obj: AnyRef): String = {
    mapper.writeValueAsString(obj)
  }
  
  def deserializeFromJson[T](json: String, clazz: Class[T]): T = {
    mapper.readValue(json, clazz)
  }
  
  def demonstrate(): Unit = {
    // 创建用户对象
    val user = User(1, "John Doe", "john@example.com", List("user", "admin"))
    
    // 序列化为JSON
    val userJson = serializeToJson(user)
    println(s"Serialized user: $userJson")
    
    // 反序列化回对象
    val parsedUser = deserializeFromJson(userJson, classOf[User])
    println(s"Parsed user: $parsedUser")
    
    // 处理集合
    val users = List(
      User(1, "Alice", "alice@example.com", List("user")),
      User(2, "Bob", "bob@example.com", List("user", "admin")),
      User(3, "Charlie", "charlie@example.com", List("admin"))
    )
    
    val usersJson = serializeToJson(users)
    println(s"Serialized users: $usersJson")
    
    // 反序列化集合
    import scala.collection.JavaConverters._
    val parsedUsers = mapper.readValue(usersJson, classOf[List[User]])
    println(s"Parsed users: ${parsedUsers.mkString(", ")}")
  }
}
```

### 9.4.3 使用Apache Kafka

```scala
import java.util.{Collections, Properties}
import org.apache.kafka.clients.consumer.{ConsumerConfig, ConsumerRecord, KafkaConsumer}
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerConfig, ProducerRecord}
import scala.jdk.CollectionConverters._

// Kafka生产者
class ScalaKafkaProducer(bootstrapServers: String) {
  private val props = new Properties()
  props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers)
  props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer")
  props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer")
  
  private val producer = new KafkaProducer[String, String](props)
  
  def sendMessage(topic: String, key: String, value: String): Unit = {
    val record = new ProducerRecord[String, String](topic, key, value)
    producer.send(record)
    println(s"Sent message: $key -> $value")
  }
  
  def close(): Unit = producer.close()
}

// Kafka消费者
class ScalaKafkaConsumer(bootstrapServers: String, groupId: String, topic: String) {
  private val props = new Properties()
  props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers)
  props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId)
  props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer")
  props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer")
  props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest")
  
  private val consumer = new KafkaConsumer[String, String](props)
  
  def startConsuming(): Unit = {
    consumer.subscribe(Collections.singletonList(topic))
    
    new Thread(() => {
      while (true) {
        val records = consumer.poll(100).asScala
        for (record <- records) {
          println(s"Received message: ${record.key()} -> ${record.value()}")
        }
      }
    }).start()
  }
  
  def close(): Unit = consumer.close()
}

// Kafka使用示例
object KafkaExample {
  def demonstrate(): Unit = {
    val bootstrapServers = "localhost:9092"
    val topic = "scala-kafka-test"
    
    // 创建生产者
    val producer = new ScalaKafkaProducer(bootstrapServers)
    
    // 发送消息
    producer.sendMessage(topic, "key1", "Scala message 1")
    producer.sendMessage(topic, "key2", "Scala message 2")
    producer.sendMessage(topic, "key3", "Scala message 3")
    
    // 创建消费者
    val consumer = new ScalaKafkaConsumer(bootstrapServers, "scala-group", topic)
    consumer.startConsuming()
    
    // 等待一段时间以便接收消息
    Thread.sleep(2000)
    
    // 清理资源
    producer.close()
    consumer.close()
  }
}
```

## 9.5 构建与打包混合项目

### 9.5.1 在Maven项目中使用Scala

在Maven项目中使用Scala需要配置Scala Maven插件：

```xml
<!-- pom.xml -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>java-scala-mixed</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <scala.version>2.13.8</scala.version>
        <scala.maven.plugin.version>4.6.1</scala.maven.plugin.version>
    </properties>
    
    <dependencies>
        <!-- Scala library -->
        <dependency>
            <groupId>org.scala-lang</groupId>
            <artifactId>scala-library</artifactId>
            <version>${scala.version}</version>
        </dependency>
        
        <!-- 其他依赖 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.7.0</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <!-- Scala Maven Plugin -->
            <plugin>
                <groupId>net.alchim31.maven</groupId>
                <artifactId>scala-maven-plugin</artifactId>
                <version>${scala.maven.plugin.version}</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>compile</goal>
                            <goal>testCompile</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <scalaVersion>${scala.version}</scalaVersion>
                    <args>
                        <arg>-deprecation</arg>
                        <arg>-feature</arg>
                        <arg>-unchecked</arg>
                        <arg>-Xlint</arg>
                    </args>
                </configuration>
            </plugin>
            
            <!-- Maven Compiler Plugin (for Java) -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### 9.5.2 在sbt项目中使用Java

在sbt项目中使用Java相对简单，因为sbt默认支持混合源代码：

```scala
// build.sbt
name := "scala-java-mixed"
version := "1.0.0"
scalaVersion := "2.13.8"

// 自动编译Java源代码
javacOptions ++= Seq("-source", "1.8", "-target", "1.8")

// 库依赖
libraryDependencies ++= Seq(
  "org.springframework.boot" %% "spring-boot-starter-web" % "2.7.0"
)
```

目录结构应该如下：
```
project/
├── build.sbt
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/java/
│   │   │       └── JavaClass.java
│   │   └── scala/
│   │       └── com/example/scala/
│   │           └── ScalaClass.scala
│   └── test/
│       ├── java/
│       └── scala/
```

### 9.5.3 使用Gradle构建混合项目

使用Gradle构建混合项目的配置：

```groovy
// build.gradle
plugins {
    id 'scala'
    id 'java'
    id 'application'
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.scala-lang:scala-library:2.13.8'
    
    // 其他依赖
    implementation 'org.springframework.boot:spring-boot-starter-web:2.7.0'
}

// Java编译设置
sourceCompatibility = '1.8'

tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
}

// Scala编译设置
tasks.withType(ScalaCompile) {
    scalaCompileOptions.additionalParameters = [
        "-deprecation",
        "-feature",
        "-unchecked",
        "-Xlint"
    ]
}

// 指定主类
mainClassName = 'com.example.Main'
```

## 9.6 最佳实践与技巧

### 9.6.1 隐式转换与类型适配

```scala
import java.time.{LocalDate, LocalDateTime}
import java.util.{Date, List as JList}
import scala.jdk.CollectionConverters._

// 创建隐式转换类，方便Java和Scala类型之间的转换
object JavaConversions {
  // Java Date -> Scala LocalDate
  implicit def dateToLocalDate(date: Date): LocalDate = {
    date.toInstant.atZone(java.time.ZoneId.systemDefault()).toLocalDate
  }
  
  // LocalDate -> Java Date
  implicit def localDateToDate(date: LocalDate): Date = {
    java.sql.Date.valueOf(date)
  }
  
  // Java List -> Scala List
  implicit def javaListToScalaList[T](javaList: JList[T]): List[T] = {
    javaList.asScala.toList
  }
  
  // Scala List -> Java List
  implicit def scalaListToJavaList[T](scalaList: List[T]): JList[T] = {
    scalaList.asJava
  }
}

// 隐式类添加额外方法
import JavaConversions._

object ConversionHelper {
  // 隐式类增强Java集合
  implicit class RichJavaList[T](list: JList[T]) {
    def filter(predicate: T => Boolean): JList[T] = {
      val filtered = list.asScala.filter(predicate)
      filtered.asJava
    }
    
    def map[R](mapper: T => R): JList[R] = {
      val mapped = list.asScala.map(mapper)
      mapped.asJava
    }
  }
  
  // 隐式类增强Java字符串
  implicit class RichJavaString(str: String) {
    def isPalindrome: Boolean = str == str.reverse
    
    def wordCount: Int = str.split("\\s+").length
    
    def capitalizeWords: String = {
      str.split("\\s+").map(_.capitalize).mkString(" ")
    }
  }
}

object ConversionExample {
  import ConversionHelper._
  
  def demonstrate(): Unit = {
    // 使用隐式转换
    val javaDate = new Date()
    val scalaDate: LocalDate = javaDate  // 自动转换
    println(s"Converted date: $scalaDate")
    
    // 使用隐式类
    val javaList: JList[String] = new java.util.ArrayList()
    javaList.add("apple")
    javaList.add("banana")
    javaList.add("cherry")
    
    // 使用增强的方法
    val filtered = javaList.filter(_.length > 5)
    val mapped = javaList.map(_.toUpperCase)
    
    println(s"Filtered: ${filtered}")
    println(s"Mapped: ${mapped}")
    
    // 使用字符串增强
    val sentence = "hello world from scala"
    println(s"Is palindrome: ${sentence.isPalindrome}")
    println(s"Word count: ${sentence.wordCount}")
    println(s"Capitalized: ${sentence.capitalizeWords}")
  }
}
```

### 9.6.2 设计适合Java互操作的Scala API

设计容易被Java使用的Scala API需要考虑以下几点：

```scala
// 好的实践：设计对Java友好的API
object JavaFriendlyAPI {
  // 1. 避免Scala特有类型在公共API中
  // 不好：返回Option类型，Java需要额外处理
  def findUserBad(id: Long): Option[User] = {
    if (id == 1) Some(User("Alice", 30)) 
    else None
  }
  
  // 好：返回可空类型
  def findUserGood(id: Long): User = {
    if (id == 1) User("Alice", 30) 
    else null
  }
  
  // 或者提供重载版本
  def findUser(id: Long): Option[User] = {
    if (id == 1) Some(User("Alice", 30)) 
    else None
  }
  
  def findUserNullable(id: Long): User = {
    findUser(id).orNull
  }
  
  // 2. 提供工厂方法而非构造函数重载
  // 不好：使用默认参数
  class BadConfig private (host: String, port: Int, timeout: Int) {
    // ...
  }
  object BadConfig {
    def apply(host: String, port: Int = 8080, timeout: Int = 5000): BadConfig = {
      new BadConfig(host, port, timeout)
    }
  }
  
  // 好：提供明确的工厂方法
  class GoodConfig private (host: String, port: Int, timeout: Int) {
    // ...
  }
  object GoodConfig {
    def create(host: String): GoodConfig = create(host, 8080)
    
    def create(host: String, port: Int): GoodConfig = create(host, port, 5000)
    
    def create(host: String, port: Int, timeout: Int): GoodConfig = {
      new GoodConfig(host, port, timeout)
    }
  }
  
  // 3. 避免位置参数在Java中不易使用
  // 不好：多个位置参数
  def processBad(user: String, age: Int, active: Boolean, role: String): String = {
    s"User: $user, Age: $age, Active: $active, Role: $role"
  }
  
  // 好：使用构建器模式
  class UserProcessor {
    private var user: String = ""
    private var age: Int = 0
    private var active: Boolean = false
    private var role: String = ""
    
    def withUser(user: String): UserProcessor = {
      this.user = user
      this
    }
    
    def withAge(age: Int): UserProcessor = {
      this.age = age
      this
    }
    
    def withActive(active: Boolean): UserProcessor = {
      this.active = active
      this
    }
    
    def withRole(role: String): UserProcessor = {
      this.role = role
      this
    }
    
    def process(): String = {
      s"User: $user, Age: $age, Active: $active, Role: $role"
    }
  }
  
  // 4. 提供Java友式的集合处理
  // 不好：返回Scala集合
  def getUsersBad(): List[User] = {
    List(User("Alice", 30), User("Bob", 25))
  }
  
  // 好：返回Java集合或提供转换方法
  def getUsers(): java.util.List[User] = {
    import scala.jdk.CollectionConverters._
    getUsersBad().asJava
  }
  
  // 或者同时提供两种版本
  def getUsersAsScala(): List[User] = {
    getUsersBad()
  }
  
  def getUsersAsJava(): java.util.List[User] = {
    import scala.jdk.CollectionConverters._
    getUsersAsScala().asJava
  }
  
  // 5. 避免在公共API中使用Scala特定特性如隐式参数
  // 不好：使用隐式参数
  def processWithImplicit(data: String)(implicit formatter: String => String): String = {
    formatter(data)
  }
  
  // 好：使用显式参数
  def processWithFormatter(data: String, formatter: String => String): String = {
    formatter(data)
  }
  
  // 或者提供重载版本
  def process(data: String): String = {
    processWithFormatter(data, identity)
  }
}

case class User(name: String, age: Int)
```

### 9.6.3 性能考虑

Scala与Java互操作时的性能考虑：

```scala
object PerformanceConsiderations {
  // 1. 集合转换开销
  def collectionConversionOverhead(): Unit = {
    val scalaList = List.range(0, 1000000)
    
    // 避免不必要的转换
    // 不好：在循环中反复转换
    def inefficientProcessing(): Int = {
      var sum = 0
      for (i <- 0 until 100) {
        val javaList = scalaList.asJava  // 每次都创建新的Java列表
        // 处理javaList...
        sum += javaList.size()
      }
      sum
    }
    
    // 好：转换一次，多次使用
    def efficientProcessing(): Int = {
      val javaList = scalaList.asJava  // 转换一次
      var sum = 0
      for (i <- 0 until 100) {
        // 使用已转换的javaList
        sum += javaList.size()
      }
      sum
    }
  }
  
  // 2. boxing/unboxing开销
  def boxingUnboxingOverhead(): Unit = {
    // Scala基本类型与Java包装类型的转换
    
    // 不好：在密集循环中反复装箱/拆箱
    def inefficientSum(): Int = {
      val javaList = new java.util.ArrayList[Integer]()
      javaList.add(1)
      javaList.add(2)
      javaList.add(3)
      
      var sum = 0
      for (i <- 0 until javaList.size()) {
        sum += javaList.get(i)  // 每次访问都需要拆箱
      }
      sum
    }
    
    // 好：批量转换为Scala类型后处理
    def efficientSum(): Int = {
      import scala.jdk.CollectionConverters._
      val javaList = new java.util.ArrayList[Integer]()
      javaList.add(1)
      javaList.add(2)
      javaList.add(3)
      
      val scalaList = javaList.asScala.toList  // 转换一次
      scalaList.sum  // 使用Scala的高效实现
    }
  }
  
  // 3. 函数与接口转换开销
  def functionInterfaceOverhead(): Unit = {
    val javaList = new java.util.ArrayList[String]()
    javaList.add("one")
    javaList.add("two")
    javaList.add("three")
    
    // 不好：每次调用都创建新的函数对象
    def inefficientFilter(): java.util.List[String] = {
      javaList.removeIf(new java.util.function.Predicate[String] {
        def test(s: String): Boolean = s.length > 3
      })
      javaList
    }
    
    // 好：重用函数对象
    val lengthPredicate = new java.util.function.Predicate[String] {
      def test(s: String): Boolean = s.length > 3
    }
    
    def efficientFilter(): java.util.List[String] = {
      javaList.removeIf(lengthPredicate)
      javaList
    }
  }
  
  // 4. 避免使用反射进行类型转换
  def reflectionOverhead(): Unit = {
    // 不好：使用反射进行类型转换
    def inefficientConversion(obj: Any): Int = {
      obj match {
        case i: Int => i
        case j: java.lang.Integer => j.intValue()
        case s: String => s.toInt
        case _ => 0
      }
    }
    
    // 好：使用明确的类型处理
    def efficientConversionInt(i: Int): Int = i
    def efficientConversionInteger(j: java.lang.Integer): Int = j.intValue()
    def efficientConversionString(s: String): Int = s.toInt
    
    // 或者使用特化方法
    def efficientConversion[T](obj: T)(implicit converter: T => Int): Int = {
      converter(obj)
    }
  }
}
```

## 总结

Scala与Java的互操作性使得开发人员可以充分利用两种语言的优势：

1. **从Scala角度**：
   - 可以无缝使用Java丰富的生态系统
   - 可以逐步将Java代码迁移到Scala
   - 可以与现有Java系统无缝集成

2. **从Java角度**：
   - 可以利用Scala的函数式特性
   - 可以使用Scala的高级抽象
   - 可以在Java项目中逐步引入Scala

3. **最佳实践**：
   - 设计API时考虑互操作性
   - 注意性能影响，尤其是在集合转换上
   - 使用适当的构建工具支持混合语言项目
   - 保持代码风格的一致性

通过掌握这些互操作技巧，开发人员可以构建结合Java和Scala优势的强大应用程序。

在下一章中，我们将通过一个完整的实战项目，应用前面学到的所有Scala知识。