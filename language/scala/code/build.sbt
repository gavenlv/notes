// Scala项目构建配置
name := "scala-learning-guide"

version := "1.0.0"

scalaVersion := "2.13.10"

// 编译器选项
scalacOptions ++= Seq(
  "-deprecation",           // 显示废弃警告
  "-feature",              // 显示语言特性警告
  "-unchecked",            // 显示未检查警告
  "-Xfatal-warnings",      // 将警告视为错误
  "-language:implicitConversions",
  "-language:higherKinds",
  "-language:postfixOps"
)

// 依赖库
libraryDependencies ++= Seq(
  // 测试框架
  "org.scalatest" %% "scalatest" % "3.2.15" % Test,
  "org.scalacheck" %% "scalacheck" % "1.17.0" % Test,
  
  // JSON处理
  "io.circe" %% "circe-core" % "0.14.5",
  "io.circe" %% "circe-generic" % "0.14.5",
  "io.circe" %% "circe-parser" % "0.14.5",
  
  // HTTP客户端
  "com.softwaremill.sttp.client3" %% "core" % "3.8.15",
  
  // 数据库访问
  "org.scalikejdbc" %% "scalikejdbc" % "4.0.0",
  "com.h2database" % "h2" % "2.1.214" % Test,
  
  // 并发编程
  "com.typesafe.akka" %% "akka-actor-typed" % "2.8.4",
  "com.typesafe.akka" %% "akka-stream" % "2.8.4",
  
  // 配置管理
  "com.typesafe" % "config" % "1.4.2",
  
  // 日志
  "ch.qos.logback" % "logback-classic" % "1.4.7",
  "com.typesafe.scala-logging" %% "scala-logging" % "3.9.5"
)

// 运行配置
fork in run := true
connectInput in run := true
outputStrategy := Some(StdoutOutput)

// 测试配置
Test / fork := true
Test / parallelExecution := false

// 代码格式化和检查
addCommandAlias("fmt", "all scalafmtSbt scalafmt test:scalafmt")
addCommandAlias("check", "all scalafmtSbtCheck scalafmtCheck test:scalafmtCheck")

// 项目结构
lazy val root = (project in file("."))
  .settings(
    // 源代码目录
    scalaSource in Compile := baseDirectory.value / "src" / "main" / "scala",
    scalaSource in Test := baseDirectory.value / "src" / "test" / "scala",
    
    // 资源文件
    resourceDirectory in Compile := baseDirectory.value / "src" / "main" / "resources",
    resourceDirectory in Test := baseDirectory.value / "src" / "test" / "resources"
  )

// 自定义任务
lazy val runAllExamples = taskKey[Unit]("运行所有章节的示例")

runAllExamples := {
  val chapters = (1 to 8).map(i => s"chapter$i")
  chapters.foreach { chapter =>
    println(s"运行 $chapter 示例...")
    (runMain in Compile).toTask(s" $chapter.Examples").value
  }
}

// 打包配置
mainClass in (Compile, packageBin) := Some("chapter1.HelloWorld")

// 发布配置
publishMavenStyle := true
publishTo := Some("Local Maven Repository" at file("~/.m2/repository").toURI.toURL.toString)