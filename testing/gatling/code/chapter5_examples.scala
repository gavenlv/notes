import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.core.structure._
import io.gatling.http.protocol.HttpProtocolBuilder
import scala.concurrent.duration._
import scala.util.Random
import java.util.UUID

class Chapter5DataProcessingAndAssertions {

  val httpProtocol: HttpProtocolBuilder = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  // ==================== 实验1：CSV数据读取与使用 ====================
  
  /**
   * 实验1.1：基本CSV数据读取
   * 目标：演示如何从CSV文件读取数据并在请求中使用
   */
  val csvFeederExperiment = {
    // 创建CSV数据源
    val userFeeder = csv("users.csv").circular // 循环读取
    
    val scn = scenario("CSV Data Reading")
      .feed(userFeeder) // 将数据源注入到场景中
      .exec(
        http("Get User by ID")
          .get("/users/${userId}") // 使用CSV中的userId变量
          .check(status.is(200))
          .check(jsonPath("$.name").is("${userName}")) // 验证返回的用户名与CSV中的匹配
          .check(jsonPath("$.email").is("${userEmail}")) // 验证邮箱
      )
      .exec(session => {
        // 打印Session中的数据，用于调试
        println(s"User ID: ${session("userId").as[String]}")
        println(s"User Name: ${session("userName").as[String]}")
        println(s"User Email: ${session("userEmail").as[String]}")
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(5))
    ).protocols(httpProtocol)
  }
  
  /**
   * 实验1.2：随机CSV数据读取
   * 目标：演示如何随机读取CSV数据，避免顺序效应
   */
  val randomCsvFeederExperiment = {
    val userFeeder = csv("users.csv").random // 随机读取
    
    val scn = scenario("Random CSV Data Reading")
      .feed(userFeeder)
      .exec(
        http("Get Random User")
          .get("/users/${userId}")
          .check(status.is(200))
          .check(jsonPath("$.id").is("${userId}"))
      )
      .pause(1, 3) // 随机暂停1-3秒
    
    setUp(
      scn.inject(rampUsers(10) during (5 seconds))
    ).protocols(httpProtocol)
  }
  
  /**
   * 实验1.3：多CSV数据源组合
   * 目标：演示如何同时使用多个CSV数据源
   */
  val multipleCsvFeederExperiment = {
    val userFeeder = csv("users.csv").circular
    val postFeeder = csv("posts.csv").random
    
    val scn = scenario("Multiple CSV Data Sources")
      .feed(userFeeder)
      .feed(postFeeder)
      .exec(
        http("Get User")
          .get("/users/${userId}")
          .check(status.is(200))
          .check(jsonPath("$.name").saveAs("actualUserName"))
      )
      .exec(
        http("Get Post")
          .get("/posts/${postId}")
          .check(status.is(200))
          .check(jsonPath("$.title").saveAs("actualPostTitle"))
      )
      .exec(session => {
        // 验证数据一致性
        val expectedUserName = session("userName").as[String]
        val actualUserName = session("actualUserName").as[String]
        val expectedPostTitle = session("postTitle").as[String]
        val actualPostTitle = session("actualPostTitle").as[String]
        
        println(s"Expected User Name: $expectedUserName, Actual: $actualUserName")
        println(s"Expected Post Title: $expectedPostTitle, Actual: $actualPostTitle")
        
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(3))
    ).protocols(httpProtocol)
  }

  // ==================== 实验2：JSON响应数据提取 ====================
  
  /**
   * 实验2.1：基本JSONPath提取
   * 目标：演示如何从JSON响应中提取数据
   */
  val jsonPathExtractionExperiment = {
    val scn = scenario("JSON Path Extraction")
      .exec(
        http("Get User Details")
          .get("/users/1")
          .check(status.is(200))
          .check(jsonPath("$.id").saveAs("userId"))
          .check(jsonPath("$.name").saveAs("userName"))
          .check(jsonPath("$.email").saveAs("userEmail"))
          .check(jsonPath("$.address.city").saveAs("userCity"))
      )
      .exec(
        http("Get User Posts")
          .get("/posts?userId=${userId}") // 使用提取的userId
          .check(status.is(200))
          .check(jsonPath("$[*]").count.saveAs("postCount"))
          .check(jsonPath("$[0].title").saveAs("firstPostTitle"))
      )
      .exec(session => {
        println(s"User: ${session("userName").as[String]} from ${session("userCity").as[String]}")
        println(s"Post Count: ${session("postCount").as[Int]}")
        println(s"First Post: ${session("firstPostTitle").as[String]}")
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }
  
  /**
   * 实验2.2：JSON数组提取
   * 目标：演示如何提取和处理JSON数组数据
   */
  val jsonArrayExtractionExperiment = {
    val scn = scenario("JSON Array Extraction")
      .exec(
        http("Get All Users")
          .get("/users")
          .check(status.is(200))
          .check(jsonPath("$[*].name").findAll.saveAs("userNames"))
          .check(jsonPath("$[*].email").findAll.saveAs("userEmails"))
      )
      .exec(
        http("Get All Posts")
          .get("/posts")
          .check(status.is(200))
          .check(jsonPath("$[*].title").findAll.saveAs("postTitles"))
      )
      .exec(session => {
        val userNames = session("userNames").as[Seq[String]]
        val userEmails = session("userEmails").as[Seq[String]]
        val postTitles = session("postTitles").as[Seq[String]]
        
        println(s"Found ${userNames.length} users:")
        userNames.zip(userEmails).foreach { case (name, email) =>
          println(s"  - $name ($email)")
        }
        
        println(s"Found ${postTitles.length} posts")
        postTitles.take(3).foreach(title => println(s"  - $title"))
        
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }
  
  /**
   * 实验2.3：条件JSON提取
   * 目标：演示如何使用条件表达式提取特定JSON数据
   */
  val conditionalJsonExtractionExperiment = {
    val scn = scenario("Conditional JSON Extraction")
      .exec(
        http("Get All Users")
          .get("/users")
          .check(status.is(200))
          // 提取所有用户名
          .check(jsonPath("$[*].name").findAll.saveAs("allUserNames"))
          // 提取包含特定字符的用户名
          .check(jsonPath("$[?(@.name =~ /.*[Ss].*/)].name").findAll.saveAs("usersWithS"))
      )
      .exec(session => {
        val allUserNames = session("allUserNames").as[Seq[String]]
        val usersWithS = session("usersWithS").as[Seq[String]]
        
        println(s"Total users: ${allUserNames.length}")
        println(s"Users with 'S' in name: ${usersWithS.length}")
        usersWithS.foreach(name => println(s"  - $name"))
        
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }

  // ==================== 实验3：自定义断言实现 ====================
  
  /**
   * 实验3.1：基本断言验证
   * 目标：演示如何实现基本的断言验证
   */
  val basicAssertionExperiment = {
    val scn = scenario("Basic Assertions")
      .exec(
        http("Get User")
          .get("/users/1")
          .check(status.is(200)) // 验证状态码
          .check(responseTimeInMillis.lt(1000)) // 验证响应时间
          .check(jsonPath("$.id").is(1)) // 验证JSON字段
          .check(jsonPath("$.name").exists) // 验证字段存在
      )
      .exec(
        http("Get Non-existent User")
          .get("/users/999")
          .check(status.is(404)) // 验证404状态码
      )
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }
  
  /**
   * 实验3.2：自定义业务逻辑断言
   * 目标：演示如何实现自定义的业务逻辑断言
   */
  val customBusinessAssertionExperiment = {
    val scn = scenario("Custom Business Logic Assertions")
      .exec(
        http("Get User")
          .get("/users/1")
          .check(status.is(200))
          .check(jsonPath("$.name").saveAs("userName"))
          .check(jsonPath("$.email").saveAs("userEmail"))
      )
      .exec(session => {
        val userName = session("userName").as[String]
        val userEmail = session("userEmail").as[String]
        
        // 自定义业务逻辑验证：检查用户名和邮箱是否匹配预期格式
        val nameValid = userName.nonEmpty && userName.split(" ").length >= 2
        val emailValid = userEmail.contains("@") && userEmail.contains(".")
        
        if (!nameValid) {
          println(s"Warning: Invalid user name format: $userName")
        }
        
        if (!emailValid) {
          println(s"Warning: Invalid email format: $userEmail")
        }
        
        // 将验证结果保存到Session
        session.set("nameValid", nameValid).set("emailValid", emailValid)
      })
      .exec(session => {
        // 使用Session中的验证结果进行后续操作
        val nameValid = session("nameValid").as[Boolean]
        val emailValid = session("emailValid").as[Boolean]
        
        if (nameValid && emailValid) {
          println("User data validation passed")
        } else {
          println("User data validation failed")
        }
        
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }
  
  /**
   * 实验3.3：数据一致性断言
   * 目标：演示如何验证不同API之间的数据一致性
   */
  val dataConsistencyAssertionExperiment = {
    val scn = scenario("Data Consistency Assertions")
      .exec(
        http("Get User Details")
          .get("/users/1")
          .check(status.is(200))
          .check(jsonPath("$.id").saveAs("userId"))
          .check(jsonPath("$.name").saveAs("userName"))
          .check(jsonPath("$.email").saveAs("userEmail"))
      )
      .exec(
        http("Get User Posts")
          .get("/posts?userId=${userId}")
          .check(status.is(200))
          .check(jsonPath("$[*]").count.saveAs("postCount"))
          .check(jsonPath("$[*].title").findAll.saveAs("postTitles"))
      )
      .exec(session => {
        val userId = session("userId").as[Int]
        val userName = session("userName").as[String]
        val userEmail = session("userEmail").as[String]
        val postCount = session("postCount").as[Int]
        val postTitles = session("postTitles").as[Seq[String]]
        
        // 数据一致性验证
        println(s"User ID: $userId, Name: $userName, Email: $userEmail")
        println(s"Post Count: $postCount")
        
        // 验证用户ID是否为正数
        val userIdValid = userId > 0
        println(s"User ID validation: $userIdValid")
        
        // 验证用户名不为空
        val userNameValid = userName.nonEmpty
        println(s"User name validation: $userNameValid")
        
        // 验证邮箱格式
        val emailValid = userEmail.contains("@") && userEmail.contains(".")
        println(s"Email validation: $emailValid")
        
        // 验证帖子数量是否合理
        val postCountValid = postCount >= 0
        println(s"Post count validation: $postCountValid")
        
        // 验证帖子标题不为空
        val postTitlesValid = postTitles.forall(_.nonEmpty)
        println(s"Post titles validation: $postTitlesValid")
        
        // 综合验证结果
        val allValid = userIdValid && userNameValid && emailValid && postCountValid && postTitlesValid
        println(s"Overall data consistency: $allValid")
        
        session.set("allValid", allValid)
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }

  // ==================== 高级数据处理示例 ====================
  
  /**
   * 高级示例1：动态数据生成
   * 目标：演示如何在测试中动态生成数据
   */
  val dynamicDataGenerationExperiment = {
    // 自定义Feeder生成随机数据
    val randomUserFeeder = Iterator.continually(Map(
      "userId" -> Random.nextInt(100) + 1,
      "sessionId" -> UUID.randomUUID().toString,
      "timestamp" -> System.currentTimeMillis()
    ))
    
    val scn = scenario("Dynamic Data Generation")
      .feed(randomUserFeeder)
      .exec(
        http("Get Random User")
          .get("/users/${userId}")
          .check(status.is(200))
          .check(jsonPath("$.name").saveAs("userName"))
      )
      .exec(session => {
        println(s"Session ID: ${session("sessionId").as[String]}")
        println(s"Timestamp: ${session("timestamp").as[Long]}")
        println(s"User ID: ${session("userId").as[Int]}")
        println(s"User Name: ${session("userName").as[String]}")
        session
      })
    
    setUp(
      scn.inject(rampUsers(5) during (10 seconds))
    ).protocols(httpProtocol)
  }
  
  /**
   * 高级示例2：数据转换与处理
   * 目标：演示如何在测试中转换和处理数据
   */
  val dataTransformationExperiment = {
    val scn = scenario("Data Transformation")
      .exec(
        http("Get User")
          .get("/users/1")
          .check(status.is(200))
          .check(jsonPath("$.name").saveAs("originalName"))
          .check(jsonPath("$.email").saveAs("originalEmail"))
      )
      .exec(session => {
        // 数据转换
        val originalName = session("originalName").as[String]
        val originalEmail = session("originalEmail").as[String]
        
        // 转换为大写
        val upperName = originalName.toUpperCase
        // 提取域名
        val domain = originalEmail.substring(originalEmail.indexOf("@") + 1)
        
        println(s"Original Name: $originalName -> Upper Name: $upperName")
        println(s"Original Email: $originalEmail -> Domain: $domain")
        
        session
          .set("upperName", upperName)
          .set("domain", domain)
      })
      .exec(session => {
        // 使用转换后的数据
        val upperName = session("upperName").as[String]
        val domain = session("domain").as[String]
        
        println(f"Processed data: $upperName%-20s | $domain")
        
        session
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }
  
  /**
   * 高级示例3：复杂断言与验证
   * 目标：演示如何实现复杂的断言和验证逻辑
   */
  val complexAssertionExperiment = {
    val scn = scenario("Complex Assertions")
      .exec(
        http("Get All Users")
          .get("/users")
          .check(status.is(200))
          .check(jsonPath("$[*]").count.saveAs("userCount"))
          .check(jsonPath("$[*].name").findAll.saveAs("userNames"))
          .check(jsonPath("$[*].email").findAll.saveAs("userEmails"))
      )
      .exec(
        http("Get All Posts")
          .get("/posts")
          .check(status.is(200))
          .check(jsonPath("$[*]").count.saveAs("postCount"))
          .check(jsonPath("$[*].userId").findAll.saveAs("postUserIds"))
      )
      .exec(session => {
        val userCount = session("userCount").as[Int]
        val userNames = session("userNames").as[Seq[String]]
        val userEmails = session("userEmails").as[Seq[String]]
        val postCount = session("postCount").as[Int]
        val postUserIds = session("postUserIds").as[Seq[Int]]
        
        // 复杂验证逻辑
        println(s"Total users: $userCount")
        println(s"Total posts: $postCount")
        
        // 验证用户名不为空
        val allNamesValid = userNames.forall(_.nonEmpty)
        println(s"All user names valid: $allNamesValid")
        
        // 验证邮箱格式
        val allEmailsValid = userEmails.forall(email => email.contains("@") && email.contains("."))
        println(s"All emails valid: $allEmailsValid")
        
        // 验证帖子数量是否合理
        val postCountReasonable = postCount > 0 && postCount > userCount
        println(s"Post count reasonable: $postCountReasonable")
        
        // 验证帖子中的用户ID是否在有效范围内
        val validPostUserIds = postUserIds.forall(id => id >= 1 && id <= userCount)
        println(s"All post user IDs valid: $validPostUserIds")
        
        // 计算每个用户的平均帖子数
        val avgPostsPerUser = postCount.toDouble / userCount
        println(f"Average posts per user: $avgPostsPerUser%.2f")
        
        // 综合验证结果
        val allValid = allNamesValid && allEmailsValid && postCountReasonable && validPostUserIds
        println(s"Overall validation result: $allValid")
        
        session.set("allValid", allValid)
      })
    
    setUp(
      scn.inject(atOnceUsers(1))
    ).protocols(httpProtocol)
  }
}