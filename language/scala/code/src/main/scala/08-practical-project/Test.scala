package taskflow

// 测试代码实现
object Test {
  
  // 1. 测试框架基础
  trait TestSuite {
    def name: String
    def run(): TestResult
  }
  
  // 2. 测试结果
  sealed trait TestResult
  case object TestPassed extends TestResult
  case class TestFailed(message: String, cause: Option[Throwable] = None) extends TestResult
  case object TestSkipped extends TestResult
  
  // 3. 断言工具
  object Assertions {
    def assertTrue(condition: Boolean, message: String = "Expected true, but was false"): TestResult = {
      if (condition) TestPassed else TestFailed(message)
    }
    
    def assertFalse(condition: Boolean, message: String = "Expected false, but was true"): TestResult = {
      if (!condition) TestPassed else TestFailed(message)
    }
    
    def assertEquals[T](expected: T, actual: T, message: String = ""): TestResult = {
      if (expected == actual) TestPassed else TestFailed(
        if (message.isEmpty) s"Expected $expected, but was $actual" else message
      )
    }
    
    def assertNotEquals[T](expected: T, actual: T, message: String = ""): TestResult = {
      if (expected != actual) TestPassed else TestFailed(
        if (message.isEmpty) s"Expected not $expected, but was equal" else message
      )
    }
    
    def assertThrows[T <: Throwable](expectedType: Class[T])(test: => Any): TestResult = {
      try {
        test
        TestFailed(s"Expected exception of type ${expectedType.getSimpleName}, but no exception was thrown")
      } catch {
        case e if expectedType.isInstance(e) => TestPassed
        case e => TestFailed(s"Expected exception of type ${expectedType.getSimpleName}, but got ${e.getClass.getSimpleName}")
      }
    }
  }
  
  // 4. 测试报告
  case class TestReport(
    suiteName: String,
    totalTests: Int,
    passedTests: Int,
    failedTests: Int,
    skippedTests: Int,
    duration: Long,
    failures: List[String]
  ) {
    def successRate: Double = if (totalTests > 0) passedTests.toDouble / totalTests else 0.0
  }
  
  // 5. 测试运行器
  object TestRunner {
    def runSuite(suite: TestSuite): TestReport = {
      println(s"运行测试套件: ${suite.name}")
      
      val startTime = System.nanoTime()
      val result = suite.run()
      val endTime = System.nanoTime()
      val duration = (endTime - startTime) / 1000000 // 转换为毫秒
      
      result match {
        case TestPassed =>
          TestReport(suite.name, 1, 1, 0, 0, duration, Nil)
        case TestFailed(message, _) =>
          TestReport(suite.name, 1, 0, 1, 0, duration, List(message))
        case TestSkipped =>
          TestReport(suite.name, 1, 0, 0, 1, duration, Nil)
      }
    }
    
    def runSuites(suites: List[TestSuite]): List[TestReport] = {
      suites.map(runSuite)
    }
    
    def printReport(report: TestReport): Unit = {
      println("=" * 50)
      println(s"测试套件: ${report.suiteName}")
      println(s"总测试数: ${report.totalTests}")
      println(s"通过: ${report.passedTests}")
      println(s"失败: ${report.failedTests}")
      println(s"跳过: ${report.skippedTests}")
      println(f"成功率: ${report.successRate * 100}%.2f%%")
      println(s"耗时: ${report.duration}ms")
      
      if (report.failures.nonEmpty) {
        println("失败详情:")
        report.failures.foreach(failure => println(s"  - $failure"))
      }
      println("=" * 50)
    }
    
    def printSummary(reports: List[TestReport]): Unit = {
      val totalTests = reports.map(_.totalTests).sum
      val totalPassed = reports.map(_.passedTests).sum
      val totalFailed = reports.map(_.failedTests).sum
      val totalSkipped = reports.map(_.skippedTests).sum
      val totalTime = reports.map(_.duration).sum
      val allFailures = reports.flatMap(_.failures)
      
      println("\n" + "=" * 60)
      println("                           测试总结")
      println("=" * 60)
      println(s"总套件数: ${reports.length}")
      println(s"总测试数: $totalTests")
      println(s"通过: $totalPassed")
      println(s"失败: $totalFailed")
      println(s"跳过: $totalSkipped")
      println(f"整体成功率: ${if (totalTests > 0) totalPassed.toDouble / totalTests * 100 else 0}%.2f%%")
      println(s"总耗时: ${totalTime}ms")
      
      if (allFailures.nonEmpty) {
        println("\n所有失败:")
        allFailures.foreach(failure => println(s"  - $failure"))
      }
      
      if (totalFailed == 0) {
        println("\n🎉 所有测试都通过了!")
      } else {
        println(s"\n❌ 有 $totalFailed 个测试失败.")
      }
      println("=" * 60)
    }
  }
  
  // 6. 领域模型测试套件
  class DomainModelTestSuite extends TestSuite {
    import DomainModel._
    import Assertions._
    
    def name: String = "DomainModelTestSuite"
    
    def run(): TestResult = {
      println("测试领域模型...")
      
      // 测试用户模型
      val userId = UserId("user-001")
      val username = Username("alice")
      val email = Email("alice@example.com")
      val profile = UserProfile("Alice", "Smith", email, Some("+1234567890"), None)
      val user = User(userId, username, profile, System.currentTimeMillis())
      
      // 验证用户模型属性
      val test1 = assertEquals("Alice Smith", user.displayName, "用户显示名称应该正确")
      if (test1 != TestPassed) return test1
      
      val test2 = assertTrue(user.isActive, "新用户应该是活跃的")
      if (test2 != TestPassed) return test2
      
      // 测试项目模型
      val projectId = ProjectId("project-001")
      val project = Project(
        projectId,
        "TaskFlow Development",
        Some("Task management system development"),
        userId,
        System.currentTimeMillis(),
        System.currentTimeMillis()
      )
      
      val test3 = assertEquals("TaskFlow Development", project.name, "项目名称应该正确")
      if (test3 != TestPassed) return test3
      
      // 测试任务模型
      val taskId = TaskId("task-001")
      val task = Task(
        taskId,
        "Implement domain model",
        Some("Create all domain models for the task management system"),
        Priority.High,
        TaskStatus.Todo,
        Some(userId),
        userId,
        projectId,
        Some(System.currentTimeMillis() + 7 * 24 * 60 * 60 * 1000), // 一周后到期
        System.currentTimeMillis(),
        System.currentTimeMillis()
      )
      
      val test4 = assertEquals("Implement domain model", task.title, "任务标题应该正确")
      if (test4 != TestPassed) return test4
      
      val test5 = assertEquals(Priority.High, task.priority, "任务优先级应该正确")
      if (test5 != TestPassed) return test5
      
      // 测试值对象
      val test6 = assertEquals("alice@example.com", email.value, "邮箱值应该正确")
      if (test6 != TestPassed) return test6
      
      TestPassed
    }
  }
  
  // 7. Repository层测试套件
  class RepositoryTestSuite extends TestSuite {
    import DomainModel._
    import Repository._
    import Assertions._
    
    def name: String = "RepositoryTestSuite"
    
    def run(): TestResult = {
      println("测试Repository层...")
      
      // 测试用户Repository
      val userRepo = new InMemoryUserRepository
      
      val userId = UserId("user-001")
      val username = Username("alice")
      val email = Email("alice@example.com")
      val profile = UserProfile("Alice", "Smith", email, Some("+1234567890"), None)
      val user = User(userId, username, profile, System.currentTimeMillis())
      
      // 保存用户
      val savedUser = userRepo.save(user)
      val test1 = assertEquals(user, savedUser, "保存的用户应该与原用户相同")
      if (test1 != TestPassed) return test1
      
      // 根据ID查找用户
      val foundUser = userRepo.findById("user-001")
      val test2 = assertTrue(foundUser.isDefined, "应该能找到保存的用户")
      if (test2 != TestPassed) return test2
      
      val test3 = assertEquals(user, foundUser.get, "找到的用户应该与原用户相同")
      if (test3 != TestPassed) return test3
      
      // 根据用户名查找用户
      val userByUsername = userRepo.findByUsername(username)
      val test4 = assertTrue(userByUsername.isDefined, "应该能根据用户名找到用户")
      if (test4 != TestPassed) return test4
      
      // 根据邮箱查找用户
      val userByEmail = userRepo.findByEmail(email)
      val test5 = assertTrue(userByEmail.isDefined, "应该能根据邮箱找到用户")
      if (test5 != TestPassed) return test5
      
      // 测试任务Repository
      val taskRepo = new InMemoryTaskRepository
      
      val projectId = ProjectId("project-001")
      val taskId = TaskId("task-001")
      val task = Task(
        taskId,
        "Test Task",
        Some("Test task description"),
        Priority.Medium,
        TaskStatus.Todo,
        Some(userId),
        userId,
        projectId,
        Some(System.currentTimeMillis() + 7 * 24 * 60 * 60 * 1000),
        System.currentTimeMillis(),
        System.currentTimeMillis()
      )
      
      // 保存任务
      val savedTask = taskRepo.save(task)
      val test6 = assertEquals(task, savedTask, "保存的任务应该与原任务相同")
      if (test6 != TestPassed) return test6
      
      // 根据项目ID查找任务
      val tasksByProject = taskRepo.findByProjectId(projectId)
      val test7 = assertTrue(tasksByProject.nonEmpty, "应该能找到项目相关的任务")
      if (test7 != TestPassed) return test7
      
      // 测试分页
      val pageRequest = PageRequest(0, 10)
      val taskPage = taskRepo.findTasksWithPagination(pageRequest)
      val test8 = assertTrue(taskPage.content.nonEmpty, "分页查询应该返回结果")
      if (test8 != TestPassed) return test8
      
      TestPassed
    }
  }
  
  // 8. Service层测试套件
  class ServiceTestSuite extends TestSuite {
    import DomainModel._
    import Repository._
    import Service._
    import Assertions._
    
    def name: String = "ServiceTestSuite"
    
    def run(): TestResult = {
      println("测试Service层...")
      
      // 设置测试依赖
      val userRepo = new InMemoryUserRepository
      val projectRepo = new InMemoryProjectRepository
      val taskRepo = new InMemoryTaskRepository
      val transactionManager = new SimpleTransactionManager
      
      val userService = new UserServiceImpl(userRepo, transactionManager)
      val projectService = new ProjectServiceImpl(projectRepo, userRepo, transactionManager)
      val taskService = new TaskServiceImpl(taskRepo, userRepo, projectRepo, transactionManager)
      
      // 测试用户注册
      val registerResult = userService.registerUser("bob", "bob@example.com", "Bob", "Johnson")
      val test1 = assertTrue(registerResult.isRight, "用户注册应该成功")
      if (test1 != TestPassed) return test1
      
      val user = registerResult.right.get
      val userId = user.id.value
      
      // 测试重复用户名注册
      val duplicateResult = userService.registerUser("bob", "other@example.com", "Other", "User")
      val test2 = assertTrue(duplicateResult.isLeft, "重复用户名注册应该失败")
      if (test2 != TestPassed) return test2
      
      // 测试项目创建
      val projectResult = projectService.createProject("Test Project", Some("A test project"), userId)
      val test3 = assertTrue(projectResult.isRight, "项目创建应该成功")
      if (test3 != TestPassed) return test3
      
      val project = projectResult.right.get
      val projectId = project.id.value
      
      // 测试任务创建
      val taskResult = taskService.createTask(
        "Test Task",
        Some("A test task"),
        Priority.High,
        Some(userId),
        userId,
        projectId
      )
      
      val test4 = assertTrue(taskResult.isRight, "任务创建应该成功")
      if (test4 != TestPassed) return test4
      
      val task = taskResult.right.get
      val taskId = task.id.value
      
      // 测试任务状态更新
      val statusResult = taskService.changeTaskStatus(taskId, TaskStatus.InProgress)
      val test5 = assertTrue(statusResult.isRight, "任务状态更新应该成功")
      if (test5 != TestPassed) return test5
      
      val updatedTask = statusResult.right.get
      val test6 = assertEquals(TaskStatus.InProgress, updatedTask.status, "任务状态应该更新为进行中")
      if (test6 != TestPassed) return test6
      
      // 测试获取任务
      val getTaskResult = taskService.getTask(taskId)
      val test7 = assertTrue(getTaskResult.isRight, "获取任务应该成功")
      if (test7 != TestPassed) return test7
      
      TestPassed
    }
  }
  
  // 9. API层测试套件
  class APITestSuite extends TestSuite {
    import API._
    import Assertions._
    
    def name: String = "APITestSuite"
    
    def run(): TestResult = {
      println("测试API层...")
      
      // 创建模拟的依赖
      val mockUserService = new MockUserService
      val userRoutes = new UserRoutes(mockUserService)
      
      // 测试用户注册API
      val registerRequest = HttpRequest(
        "POST",
        "/users/register",
        Map("Content-Type" -> "application/json"),
        Some("""{"username": "testuser", "email": "test@example.com", "firstName": "Test", "lastName": "User"}""")
      )
      
      val registerResponse = userRoutes.handle(registerRequest)
      val test1 = assertEquals(201, registerResponse.statusCode, "用户注册应该返回201状态码")
      if (test1 != TestPassed) return test1
      
      // 测试获取用户列表API
      val getUsersRequest = HttpRequest(
        "GET",
        "/users?page=0&size=10",
        Map("Content-Type" -> "application/json"),
        None
      )
      
      val getUsersResponse = userRoutes.handle(getUsersRequest)
      val test2 = assertEquals(200, getUsersResponse.statusCode, "获取用户列表应该返回200状态码")
      if (test2 != TestPassed) return test2
      
      // 测试错误处理
      val invalidRequest = HttpRequest(
        "POST",
        "/users/register",
        Map("Content-Type" -> "application/json"),
        Some("""{"invalid": "json"}""")
      )
      
      val invalidResponse = userRoutes.handle(invalidRequest)
      val test3 = assertEquals(400, invalidResponse.statusCode, "无效请求应该返回400状态码")
      if (test3 != TestPassed) return test3
      
      TestPassed
    }
  }
  
  // 10. Mock服务实现（用于测试）
  class MockUserService extends Service.UserService {
    import DomainModel._
    import Repository._
    import Service._
    
    def registerUser(username: String, email: String, firstName: String, lastName: String): ServiceResult[User] = {
      val userId = UserId(s"user-${System.currentTimeMillis()}")
      val profile = UserProfile(firstName, lastName, Email(email), None, None)
      val user = User(userId, Username(username), profile, System.currentTimeMillis())
      Right(user)
    }
    
    def updateUser(userId: String, updates: UserUpdate): ServiceResult[User] = {
      Left(NotFoundError("Not implemented in mock"))
    }
    
    def deactivateUser(userId: String): ServiceResult[Boolean] = {
      Right(true)
    }
    
    def getUser(userId: String): ServiceResult[User] = {
      val profile = UserProfile("Test", "User", Email("test@example.com"), None, None)
      val user = User(UserId(userId), Username("testuser"), profile, System.currentTimeMillis())
      Right(user)
    }
    
    def authenticate(username: String, password: String): ServiceResult[User] = {
      Left(NotFoundError("Not implemented in mock"))
    }
    
    def changePassword(userId: String, oldPassword: String, newPassword: String): ServiceResult[Boolean] = {
      Right(true)
    }
    
    def getUsers(pageable: PageRequest): ServiceResult[Page[User]] = {
      val profile = UserProfile("Test", "User", Email("test@example.com"), None, None)
      val user = User(UserId("user-001"), Username("testuser"), profile, System.currentTimeMillis())
      val page = Page(List(user), pageable.page, pageable.size, 1)
      Right(page)
    }
  }
  
  // 11. 性能测试套件
  class PerformanceTestSuite extends TestSuite {
    import DomainModel._
    import Repository._
    import Service._
    import Assertions._
    
    def name: String = "PerformanceTestSuite"
    
    def run(): TestResult = {
      println("运行性能测试...")
      
      // 创建大量测试数据
      val userRepo = new InMemoryUserRepository
      val taskRepo = new InMemoryTaskRepository
      
      val startTime = System.currentTimeMillis()
      
      // 插入1000个用户
      for (i <- 1 to 1000) {
        val userId = UserId(s"user-$i")
        val username = Username(s"user$i")
        val email = Email(s"user$i@example.com")
        val profile = UserProfile(s"First$i", s"Last$i", email, None, None)
        val user = User(userId, username, profile, System.currentTimeMillis())
        userRepo.save(user)
      }
      
      val insertTime = System.currentTimeMillis() - startTime
      println(s"插入1000个用户耗时: ${insertTime}ms")
      
      // 查询性能测试
      val queryStartTime = System.currentTimeMillis()
      val allUsers = userRepo.findAll()
      val queryTime = System.currentTimeMillis() - queryStartTime
      println(s"查询${allUsers.length}个用户耗时: ${queryTime}ms")
      
      val test1 = assertTrue(insertTime < 5000, "插入1000个用户应该在5秒内完成")
      if (test1 != TestPassed) return test1
      
      val test2 = assertTrue(queryTime < 1000, "查询1000个用户应该在1秒内完成")
      if (test2 != TestPassed) return test2
      
      TestPassed
    }
  }
  
  // 12. 集成测试套件
  class IntegrationTestSuite extends TestSuite {
    import DomainModel._
    import Repository._
    import Service._
    import Main._
    
    def name: String = "IntegrationTestSuite"
    
    def run(): TestResult = {
      println("运行集成测试...")
      
      // 使用应用程序模块中的真实组件
      val userService = AppModule.userService
      val projectService = AppModule.projectService
      val taskService = AppModule.taskService
      
      // 测试完整的用户->项目->任务流程
      val registerResult = userService.registerUser("integration", "integration@example.com", "Integration", "Test")
      if (registerResult.isLeft) {
        return TestFailed(s"用户注册失败: ${registerResult.left.get}")
      }
      
      val user = registerResult.right.get
      val userId = user.id.value
      
      val projectResult = projectService.createProject("Integration Test Project", Some("Project for integration testing"), userId)
      if (projectResult.isLeft) {
        return TestFailed(s"项目创建失败: ${projectResult.left.get}")
      }
      
      val project = projectResult.right.get
      val projectId = project.id.value
      
      val taskResult = taskService.createTask(
        "Integration Test Task",
        Some("Task for integration testing"),
        Priority.Medium,
        Some(userId),
        userId,
        projectId
      )
      
      if (taskResult.isLeft) {
        return TestFailed(s"任务创建失败: ${taskResult.left.get}")
      }
      
      val task = taskResult.right.get
      val taskId = task.id.value
      
      // 验证整个流程
      val verifyTaskResult = taskService.getTask(taskId)
      if (verifyTaskResult.isLeft) {
        return TestFailed(s"任务验证失败: ${verifyTaskResult.left.get}")
      }
      
      val verifiedTask = verifyTaskResult.right.get
      if (verifiedTask.title != "Integration Test Task") {
        return TestFailed(s"任务标题不匹配: expected 'Integration Test Task', got '${verifiedTask.title}'")
      }
      
      TestPassed
    }
  }
  
  // 13. 测试主程序
  def main(args: Array[String]): Unit = {
    println("=== TaskFlow 测试套件 ===")
    
    // 创建所有测试套件
    val testSuites = List(
      new DomainModelTestSuite,
      new RepositoryTestSuite,
      new ServiceTestSuite,
      new APITestSuite,
      new PerformanceTestSuite,
      new IntegrationTestSuite
    )
    
    // 运行所有测试
    val reports = TestRunner.runSuites(testSuites)
    
    // 打印详细报告
    reports.foreach(TestRunner.printReport)
    
    // 打印总结
    TestRunner.printSummary(reports)
    
    // 检查是否有失败的测试
    val failedCount = reports.map(_.failedTests).sum
    if (failedCount > 0) {
      println(s"\n⚠️  警告: 有 $failedCount 个测试失败!")
      sys.exit(1)
    } else {
      println("\n✅ 所有测试都通过了!")
      sys.exit(0)
    }
  }
}