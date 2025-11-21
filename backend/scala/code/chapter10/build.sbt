name := "library-management-system"

version := "1.0.0"

scalaVersion := "2.13.8"

libraryDependencies ++= {
  val akkaVersion = "2.6.19"
  val akkaHttpVersion = "10.2.9"
  val slickVersion = "3.3.3"
  val scalaTestVersion = "3.2.12"
  
  Seq(
    // Akka HTTP
    "com.typesafe.akka" %% "akka-http" % akkaHttpVersion,
    "com.typesafe.akka" %% "akka-http-spray-json" % akkaHttpVersion,
    "com.typesafe.akka" %% "akka-stream" % akkaVersion,
    "com.typesafe.akka" %% "akka-actor-typed" % akkaVersion,
    
    // 数据库
    "com.typesafe.slick" %% "slick" % slickVersion,
    "com.typesafe.slick" %% "slick-hikaricp" % slickVersion,
    "com.h2database" % "h2" % "2.1.212",
    "org.postgresql" % "postgresql" % "42.3.3", // 可选：PostgreSQL驱动
    
    // JSON
    "io.spray" %% "spray-json" % "1.3.6",
    
    // 日志
    "ch.qos.logback" % "logback-classic" % "1.2.11",
    "com.typesafe.akka" %% "akka-slf4j" % akkaVersion,
    
    // 配置
    "com.typesafe" % "config" % "1.4.2",
    
    // 测试
    "org.scalatest" %% "scalatest" % scalaTestVersion % Test,
    "com.typesafe.akka" %% "akka-http-testkit" % akkaHttpVersion % Test,
    "com.typesafe.akka" %% "akka-testkit" % akkaVersion % Test,
    "org.mockito" %% "mockito-scala" % "1.17.5" % Test
  )
}

// 测试选项
Test / parallelExecution := false

// 编译选项
scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xlint",
  "-Ywarn-dead-code",
  "-Ywarn-numeric-widen",
  "-Ywarn-value-discard"
)

// 资源目录
Compile / resourceDirectory := baseDirectory.value / "src" / "main" / "resources"

// 启动选项
Compile / run / javaOptions ++= Seq(
  "-Dconfig.file=src/main/resources/application.conf"
)