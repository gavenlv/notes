// 反射示例

import scala.reflect.runtime.universe._
import scala.reflect.runtime.{currentMirror => cm}
import scala.util.{Try, Success, Failure}

// 基本反射示例
object BasicReflection {
  // 用于演示的类
  case class Person(name: String, age: Int) {
    def greet(): String = s"Hello, my name is $name and I'm $age years old"
    
    private def secret(): String = "This is a secret method"
  }

  def demonstrate(): Unit = {
    // 获取Person的TypeTag
    val personType = typeTag[Person]
    
    // 获取类型信息
    println(s"Type: ${personType.tpe}")
    println(s"TypeSymbol: ${personType.tpe.typeSymbol}")
    println(s"TypeArgs: ${personType.tpe.typeArgs}")
    
    // 获取类的成员
    val members = personType.tpe.members.sorted
    println("\nClass members:")
    members.foreach { member =>
      println(s"- ${member.name}: ${member.typeSignature}")
    }
    
    // 创建实例
    val constructor = personType.tpe.decl(termNames.CONSTRUCTOR).asMethod
    val personMirror = cm.reflect(cm.classTag[Person].runtimeClass)
    val constructorMirror = personMirror.reflectConstructor(constructor)
    
    val person = constructorMirror.apply("Alice", 30).asInstanceOf[Person]
    println(s"\nCreated person: $person")
    
    // 调用方法
    val greetMethod = personType.tpe.decl(TermName("greet")).asMethod
    val instanceMirror = cm.reflect(person)
    val greetMirror = instanceMirror.reflectMethod(greetMethod)
    
    val greeting = greetMirror.apply()
    println(s"Greeting: $greeting")
    
    // 访问字段
    val nameField = personType.tpe.decl(TermName("name")).asTerm.accessed.asTerm
    val nameValue = instanceMirror.reflectField(nameField).get
    println(s"Name field value: $nameValue")
  }
}

// 高级反射示例
object AdvancedReflection {
  // 用于演示的复杂类
  class ComplexClass {
    private var privateField = "private value"
    
    def publicMethod(input: String): String = s"Processed: $input"
    
    private def privateMethod(input: Int): Int = input * 2
    
    def overloadedMethod(input: String): String = s"String: $input"
    def overloadedMethod(input: Int): Int = input * 3
  }

  // 动态方法调用
  def dynamicMethodCall(): Unit = {
    val instance = new ComplexClass()
    val instanceMirror = cm.reflect(instance)
    val classSymbol = instanceMirror.symbol
    
    // 获取所有方法
    val methods = classSymbol.info.decls.filter(_.isMethod)
    println("Available methods:")
    methods.foreach { method =>
      println(s"- ${method.name}: ${method.typeSignature}")
    }
    
    // 动态调用publicMethod
    val method = classSymbol.info.decl(TermName("publicMethod")).asMethod
    val methodMirror = instanceMirror.reflectMethod(method)
    val result = methodMirror.apply("reflection test")
    println(s"\nDynamic method call result: $result")
  }
  
  // 动态字段访问
  def dynamicFieldAccess(): Unit = {
    val instance = new ComplexClass()
    val instanceMirror = cm.reflect(instance)
    val classSymbol = instanceMirror.symbol
    
    // 获取所有字段
    val fields = classSymbol.info.decls.filter(_.isTerm)
    println("Available fields:")
    fields.foreach { field =>
      println(s"- ${field.name}: ${field.typeSignature}")
    }
    
    // 动态访问privateField
    val field = classSymbol.info.decl(TermName("privateField")).asTerm.accessed.asTerm
    val fieldMirror = instanceMirror.reflectField(field)
    val value = fieldMirror.get
    println(s"\nPrivate field value: $value")
    
    // 修改私有字段
    fieldMirror.set("new private value")
    val newValue = fieldMirror.get
    println(s"Modified private field value: $newValue")
  }
  
  // 类型检查和转换
  def typeCheckingAndCasting(): Unit = {
    val values: List[Any] = List("string", 42, 3.14, List(1, 2, 3))
    
    values.foreach { value =>
      val valueType = cm.reflect(value).symbol.toType
      println(s"Value: $value, Type: $valueType")
      
      // 检查是否为字符串
      if (valueType <:< typeOf[String]) {
        val stringValue = value.asInstanceOf[String]
        println(s"  Upper case: ${stringValue.toUpperCase}")
      }
      
      // 检查是否为数字
      if (valueType <:< typeOf[Int]) {
        val intValue = value.asInstanceOf[Int]
        println(s"  Square: ${intValue * intValue}")
      }
      
      // 检查是否为列表
      if (valueType <:< typeOf[List[_]]) {
        val listValue = value.asInstanceOf[List[_]]
        println(s"  List size: ${listValue.size}")
      }
    }
  }
  
  // 处理重载方法
  def overloadedMethods(): Unit = {
    val instance = new ComplexClass()
    val instanceMirror = cm.reflect(instance)
    val classSymbol = instanceMirror.symbol
    
    // 获取重载方法
    val overloadedMethods = classSymbol.info.member(TermName("overloadedMethod")).asTerm.alternatives
    println("Overloaded methods:")
    overloadedMethods.foreach { method =>
      println(s"- ${method.asMethod.typeSignature}")
    }
    
    // 调用字符串版本
    val stringMethod = overloadedMethods.find { method =>
      val params = method.asMethod.paramLists.flatten
      params.nonEmpty && params.head.typeSignature <:< typeOf[String]
    }.get.asMethod
    
    val stringResult = instanceMirror.reflectMethod(stringMethod).apply("overloaded test")
    println(s"String overload result: $stringResult")
    
    // 调用整数版本
    val intMethod = overloadedMethods.find { method =>
      val params = method.asMethod.paramLists.flatten
      params.nonEmpty && params.head.typeSignature <:< typeOf[Int]
    }.get.asMethod
    
    val intResult = instanceMirror.reflectMethod(intMethod).apply(42)
    println(s"Int overload result: $intResult")
  }
  
  def demonstrate(): Unit = {
    println("=== 动态方法调用 ===")
    dynamicMethodCall()
    
    println("\n=== 动态字段访问 ===")
    dynamicFieldAccess()
    
    println("\n=== 类型检查和转换 ===")
    typeCheckingAndCasting()
    
    println("\n=== 处理重载方法 ===")
    overloadedMethods()
  }
}

// 泛型类型反射
object GenericReflection {
  // 泛型类
  class Container[T](private val value: T) {
    def getValue: T = value
    
    def setValue(newValue: T): Unit = {
      val field = this.getClass.getDeclaredField("value")
      field.setAccessible(true)
      field.set(this, newValue)
    }
  }
  
  // 处理泛型类型
  def processGenericType(): Unit = {
    val intContainer = new Container(42)
    val stringContainer = new Container("hello")
    
    // 获取泛型类型信息
    val intContainerType = cm.reflect(intContainer).symbol.toType
    val stringContainerType = cm.reflect(stringContainer).symbol.toType
    
    println(s"Int container type: $intContainerType")
    println(s"String container type: $stringContainerType")
    
    // 获取类型参数
    val intContainerTypeArgs = intContainerType.typeArgs
    val stringContainerTypeArgs = stringContainerType.typeArgs
    
    println(s"Int container type args: $intContainerTypeArgs")
    println(s"String container type args: $stringContainerTypeArgs")
    
    // 根据类型参数执行不同的操作
    processContainer(intContainer)
    processContainer(stringContainer)
  }
  
  def processContainer(container: Any): Unit = {
    val containerType = cm.reflect(container).symbol.toType
    
    if (containerType.typeArgs.nonEmpty) {
      val typeArg = containerType.typeArgs.head
      
      // 使用TypeTag获取类型信息
      typeArg match {
        case t if t <:< typeOf[Int] =>
          val value = container.asInstanceOf[Container[Int]].getValue
          println(s"Int container value doubled: ${value * 2}")
          
        case t if t <:< typeOf[String] =>
          val value = container.asInstanceOf[Container[String]].getValue
          println(s"String container value uppercased: ${value.toUpperCase}")
          
        case t =>
          println(s"Unsupported container type: $t")
      }
    }
  }
  
  def demonstrate(): Unit = {
    processGenericType()
  }
}

// 自定义注解
class Deprecated(reason: String) extends scala.annotation.StaticAnnotation
class Author(name: String, date: String = "") extends scala.annotation.StaticAnnotation
class Test extends scala.annotation.StaticAnnotation
class PerformanceTest extends scala.annotation.StaticAnnotation
class Doc(description: String) extends scala.annotation.StaticAnnotation

// 使用注解的类和方法
@Author("John Doe", "2023-01-01")
class AnnotatedClass {
  @Doc("Get current value")
  def getValue(): Int = 42
  
  @Deprecated("Use newGetValue instead")
  @Author("Jane Smith")
  def oldGetValue(): Int = 42
  
  @Doc("Get current value using new implementation")
  def newGetValue(): Int = 100
  
  @Test
  def testMethod(): Unit = {
    println("This is a test method")
  }
  
  @PerformanceTest
  @Test
  def performanceTest(): Unit = {
    println("This is a performance test method")
  }
}

// 注解处理示例
object AnnotationProcessing {
  // 读取类上的注解
  def readClassAnnotations(): Unit = {
    val classSymbol = typeOf[AnnotatedClass].typeSymbol.asClass
    
    println("Class annotations:")
    classSymbol.annotations.foreach { annotation =>
      println(s"- ${annotation.tree}")
    }
  }
  
  // 读取方法上的注解
  def readMethodAnnotations(): Unit = {
    val classSymbol = typeOf[AnnotatedClass].typeSymbol.asClass
    
    println("\nMethod annotations:")
    classSymbol.decls.foreach { member =>
      if (member.isMethod) {
        val method = member.asMethod
        println(s"${method.name}:")
        method.annotations.foreach { annotation =>
          println(s"  - ${annotation.tree}")
        }
      }
    }
  }
  
  // 处理特定注解
  def processAnnotations(): Unit = {
    val classSymbol = typeOf[AnnotatedClass].typeSymbol.asClass
    
    println("\nProcessing specific annotations:")
    
    // 处理Deprecated注解
    classSymbol.decls.foreach { member =>
      if (member.isMethod) {
        val method = member.asMethod
        
        method.annotations.foreach { annotation =>
          annotation.tree match {
            case Apply(Select(New(Ident(TypeName("Deprecated"))), termNames.CONSTRUCTOR), 
                       List(Literal(Constant(reason)))) =>
              println(s"Method ${method.name} is deprecated: $reason")
              
            case Apply(Select(New(Ident(TypeName("Author"))), termNames.CONSTRUCTOR), args) =>
              val name = args.head match { case Literal(Constant(name)) => name }
              val date = if (args.length > 1) {
                args(1) match { case Literal(Constant(date)) => date }
              } else {
                "unknown"
              }
              println(s"Method ${method.name} author: $name, date: $date")
              
            case _ => // 其他注解
          }
        }
      }
    }
  }
  
  // 检查注解是否存在
  def checkAnnotationExists(): Unit = {
    val classSymbol = typeOf[AnnotatedClass].typeSymbol.asClass
    
    println("\nChecking annotation existence:")
    
    classSymbol.decls.foreach { member =>
      if (member.isMethod) {
        val method = member.asMethod
        
        // 检查是否有Test注解
        val hasTest = method.annotations.exists { annotation =>
          annotation.tree.tpe <:< typeOf[Test]
        }
        
        if (hasTest) {
          println(s"Method ${method.name} has @Test annotation")
        }
        
        // 检查是否有PerformanceTest注解
        val hasPerformanceTest = method.annotations.exists { annotation =>
          annotation.tree.tpe <:< typeOf[PerformanceTest]
        }
        
        if (hasPerformanceTest) {
          println(s"Method ${method.name} has @PerformanceTest annotation")
        }
      }
    }
  }
  
  def demonstrate(): Unit = {
    readClassAnnotations()
    readMethodAnnotations()
    processAnnotations()
    checkAnnotationExists()
  }
}

// 反射与宏的局限性
object ReflectionLimitations {
  def demonstrate(): Unit = {
    println("=== Reflection Limitations ===")
    
    // 1. 类型擦除
    val list = List(1, 2, 3)
    val listType = typeOf[List[Int]]
    
    println(s"Type of List[Int]: $listType")
    println(s"Type args: ${listType.typeArgs}")
    
    // 运行时无法获取泛型类型信息
    val runtimeList = List(1, 2, 3)
    val runtimeListType = runtimeList.getClass.getTypeParameters
    println(s"Runtime type parameters: ${runtimeListType.mkString(", ")}")
    
    // 2. 性能影响
    println("\n=== Performance Impact ===")
    println("Reflection is slower than direct calls")
    println("Type checks add overhead")
    println("Generated code may not be optimized")
    
    // 3. 安全考虑
    println("\n=== Security Considerations ===")
    println("Reflection can violate encapsulation")
    println("Private fields and methods can be accessed")
    println("This can lead to security vulnerabilities")
    
    // 4. 调试困难
    println("\n=== Debugging Difficulties ===")
    println("Reflection errors can be cryptic")
    println("Stack traces may be unclear")
    println("IDE support may be limited")
  }
}

// 主程序
object ReflectionExamplesDemo extends App {
  println("=== 基本反射示例 ===")
  BasicReflection.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 高级反射示例 ===")
  AdvancedReflection.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 泛型类型反射 ===")
  GenericReflection.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 注解处理示例 ===")
  AnnotationProcessing.demonstrate()
  
  Thread.sleep(500)
  
  println("\n=== 反射与宏的局限性 ===")
  ReflectionLimitations.demonstrate()
  
  println("\nReflection examples demo completed!")
}