// 简单的Scala宏示例

import scala.language.experimental.macros
import scala.reflect.macros.whitebox.Context

// 简单的宏定义
object SimpleMacro {
  // 宏方法声明
  def currentTime(): Long = macro currentTimeImpl
  
  // 宏实现
  def currentTimeImpl(c: Context): c.Expr[Long] = {
    import c.universe._
    
    // 生成当前时间的代码
    c.Expr[Long](q"System.currentTimeMillis()")
  }
}

// 带参数的宏
object ParameterizedMacro {
  // 宏方法声明
  def debug(code: Any): Unit = macro debugImpl
  
  // 宏实现
  def debugImpl(c: Context)(code: c.Expr[Any]): c.Expr[Unit] = {
    import c.universe._
    
    // 获取代码的文本表示
    val codeString = code.tree.toString()
    
    // 生成打印代码和值的代码
    c.Expr[Unit](q"""println($codeString + ": " + $code)""")
  }
}

// 条件编译宏
object ConditionalMacro {
  // 宏方法声明
  def ifDebug(code: Any): Unit = macro ifDebugImpl
  
  // 宏实现
  def ifDebugImpl(c: Context)(code: c.Expr[Any]): c.Expr[Unit] = {
    import c.universe._
    
    // 检查是否为调试模式
    val isDebug = System.getProperty("debug", "false").toBoolean
    
    if (isDebug) {
      // 如果是调试模式，执行代码
      c.Expr[Unit](q"($code)")
    } else {
      // 否则生成空代码
      c.Expr[Unit](q"()")
    }
  }
}

// 字符串插值优化宏
object StringInterpolationOptimization {
  // 快速字符串连接宏
  implicit class FastStringContext(sc: StringContext) {
    def fast(args: Any*): String = macro fastStringImpl
  }
  
  def fastStringImpl(c: Context)(args: c.Expr[Any]*): c.Expr[String] = {
    import c.universe._
    
    // 获取字符串片段
    val parts = c.prefix.tree match {
      case Apply(Select(Apply(Ident(TermName("StringContext")), _), TermName("apply")), List(Apply(_, List(litParts)))) =>
        litParts match {
          case List(Apply(_, List(Literal(Constant(constString))))) => List(constString)
          case _ => c.abort(c.enclosingPosition, "Invalid string context")
        }
      case _ => c.abort(c.enclosingPosition, "Invalid string context")
    }
    
    // 在实际应用中，这里会生成更高效的字符串连接代码
    // 这里只是一个简化的示例
    
    // 对于简单的字符串连接，使用StringBuilder
    if (args.size > 3) {
      val sbName = TermName(c.freshName("sb"))
      
      val sbInit = q"val $sbName = new StringBuilder()"
      val sbAppends = parts.zip(args).map { case (part, arg) =>
        q"$sbName.append($part).append($arg)"
      }
      val sbAppendLast = if (parts.size > args.size) {
        q"$sbName.append(${parts.last})"
      } else q""
      
      val code = q"""
        $sbInit
        ..$sbAppends
        $sbAppendLast
        $sbName.toString
      """
      
      c.Expr[String](code)
    } else {
      // 对于少量参数，使用普通的字符串连接
      val strings = parts.zip(args).map { case (part, arg) => 
        q"$part + $arg.toString"
      }
      
      val lastPart = if (parts.size > args.size) {
        q"+ ${parts.last}"
      } else q""
      
      val code = strings.reduceLeft { (acc, expr) => q"$acc + $expr" }
      val finalCode = if (lastPart.isEmpty) code else q"$code $lastPart"
      
      c.Expr[String](finalCode)
    }
  }
}

// 使用宏的示例
object MacroExamples {
  def demonstrate(): Unit = {
    // 使用currentTime宏
    val time = SimpleMacro.currentTime()
    println(s"Current time: $time")
    
    // 使用debug宏
    val x = 42
    val y = 13
    val sum = x + y
    ParameterizedMacro.debug(sum)
    
    // 使用ifDebug宏
    ConditionalMacro.ifDebug(println("This is debug output"))
    
    // 使用字符串插值优化宏
    val name = "Alice"
    val age = 30
    val email = "alice@example.com"
    
    // 使用fast字符串插值
    val message = fast"Name: $name, Age: $age, Email: $email, Active: true"
    println(message)
    
    println("\nNote: Macros require special setup to work:")
    println("1. Add scala-paradise plugin to your build")
    println("2. Enable macro paradise in your project")
    println("3. Some IDEs may not support macro expansion")
  }
}

// 模拟宏行为的函数（因为宏无法直接运行）
object MockMacroBehavior {
  // 模拟currentTime宏的行为
  def mockCurrentTime(): Long = {
    // 实际宏会生成System.currentTimeMillis()调用
    System.currentTimeMillis()
  }
  
  // 模拟debug宏的行为
  def mockDebug(code: Any): Unit = {
    // 实际宏会生成println(codeString + ": " + code)
    val codeString = code.toString()
    println(s"$codeString: $code")
  }
  
  // 模拟ifDebug宏的行为
  def mockIfDebug(code: => Unit): Unit = {
    // 实际宏会根据编译时决定是否包含代码
    val isDebug = System.getProperty("debug", "false").toBoolean
    if (isDebug) {
      code
    }
  }
  
  // 模拟fast字符串插值宏的行为
  implicit class MockFastStringContext(sc: StringContext) {
    def fast(args: Any*): String = {
      // 实际宏会生成高效的字符串连接代码
      if (args.size > 3) {
        val sb = new StringBuilder()
        val parts = sc.parts
        for (i <- args.indices) {
          sb.append(parts(i))
          sb.append(args(i))
        }
        if (parts.size > args.size) {
          sb.append(parts.last)
        }
        sb.toString()
      } else {
        // 使用普通字符串连接
        val strings = sc.parts.zip(args).map { case (part, arg) => 
          part + arg.toString
        }
        strings.mkString + (if (sc.parts.size > args.size) sc.parts.last else "")
      }
    }
  }
  
  def demonstrate(): Unit = {
    println("=== 模拟宏行为 ===")
    
    // 使用模拟的currentTime宏
    val time = mockCurrentTime()
    println(s"Current time: $time")
    
    // 使用模拟的debug宏
    val x = 42
    val y = 13
    val sum = x + y
    mockDebug(sum)
    
    // 使用模拟的ifDebug宏
    mockIfDebug(println("This is debug output"))
    
    // 使用模拟的字符串插值优化宏
    val name = "Bob"
    val age = 25
    val message = fast"Name: $name, Age: $age"
    println(message)
    
    println("\nThese are just simulations of what macros would generate at compile time.")
  }
}

// 主程序
object SimpleMacroDemo extends App {
  println("=== 宏示例 ===")
  
  // 因为宏需要特殊设置才能运行，我们使用模拟版本来演示
  MockMacroBehavior.demonstrate()
  
  println("\n要真正运行宏示例，你需要:")
  println("1. 在build.sbt中添加: addCompilerPlugin(\"org.scalamacros\" % \"paradise\" % \"2.1.1\" cross CrossVersion.full)")
  println("2. 启用: scalacOptions += \"-Ymacro-debug-lite\"")
  println("3. 使用支持宏的Scala版本")
  
  println("\nMacro examples demo completed!")
}