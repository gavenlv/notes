package taskflow

// 文档生成工具实现
object Documentation {
  
  // 1. 文档元素特质
  sealed trait DocumentElement
  case class Text(content: String) extends DocumentElement
  case class CodeBlock(language: String, content: String) extends DocumentElement
  case class Heading(level: Int, content: String) extends DocumentElement
  case class ListItem(content: String) extends DocumentElement
  case class Link(text: String, url: String) extends DocumentElement
  case class Image(alt: String, url: String) extends DocumentElement
  case object LineBreak extends DocumentElement
  case class Table(headers: List[String], rows: List[List[String]]) extends DocumentElement
  
  // 2. 文档页面
  case class DocumentPage(
    title: String,
    elements: List[DocumentElement],
    metadata: Map[String, String] = Map.empty
  )
  
  // 3. API文档生成器
  object ApiDocumentationGenerator {
    
    // API端点信息
    case class ApiEndpoint(
      method: String,
      path: String,
      description: String,
      parameters: List[ApiParameter],
      responses: List[ApiResponse],
      tags: List[String] = List.empty
    )
    
    // API参数信息
    case class ApiParameter(
      name: String,
      in: String, // path, query, body, header
      required: Boolean,
      dataType: String,
      description: String
    )
    
    // API响应信息
    case class ApiResponse(
      statusCode: Int,
      description: String,
      schema: Option[String] = None
    )
    
    // 生成API文档页面
    def generateApiDocs(endpoints: List[ApiEndpoint]): DocumentPage = {
      val elements = ListBuffer[DocumentElement]()
      
      // 添加标题
      elements += Heading(1, "API 文档")
      elements += Text("本系统提供以下 RESTful API 接口。")
      elements += LineBreak
      
      // 按标签分组
      val groupedEndpoints = endpoints.groupBy(_.tags.headOption.getOrElse("未分类"))
      
      groupedEndpoints.foreach { case (tag, eps) =>
        elements += Heading(2, tag)
        
        eps.foreach { endpoint =>
          elements += Heading(3, s"${endpoint.method} ${endpoint.path}")
          elements += Text(endpoint.description)
          elements += LineBreak
          
          // 参数表格
          if (endpoint.parameters.nonEmpty) {
            elements += Heading(4, "参数")
            val paramHeaders = List("名称", "位置", "必需", "类型", "描述")
            val paramRows = endpoint.parameters.map(p => 
              List(p.name, p.in, if (p.required) "是" else "否", p.dataType, p.description)
            )
            elements += Table(paramHeaders, paramRows)
            elements += LineBreak
          }
          
          // 响应表格
          if (endpoint.responses.nonEmpty) {
            elements += Heading(4, "响应")
            val responseHeaders = List("状态码", "描述", "Schema")
            val responseRows = endpoint.responses.map(r => 
              List(r.statusCode.toString, r.description, r.schema.getOrElse(""))
            )
            elements += Table(responseHeaders, responseRows)
            elements += LineBreak
          }
        }
      }
      
      DocumentPage(
        "API 文档",
        elements.toList,
        Map("author" -> "TaskFlow Team", "version" -> "1.0")
      )
    }
    
    // 生成示例API端点数据
    def generateSampleEndpoints(): List[ApiEndpoint] = {
      List(
        ApiEndpoint(
          "POST",
          "/api/users/register",
          "用户注册接口",
          List(
            ApiParameter("username", "body", true, "string", "用户名"),
            ApiParameter("email", "body", true, "string", "邮箱地址"),
            ApiParameter("password", "body", true, "string", "密码")
          ),
          List(
            ApiResponse(201, "注册成功", Some("User")),
            ApiResponse(400, "请求参数错误"),
            ApiResponse(409, "用户名或邮箱已存在")
          ),
          List("用户管理")
        ),
        ApiEndpoint(
          "GET",
          "/api/users/{userId}",
          "获取用户信息",
          List(
            ApiParameter("userId", "path", true, "string", "用户ID")
          ),
          List(
            ApiResponse(200, "获取成功", Some("User")),
            ApiResponse(404, "用户不存在")
          ),
          List("用户管理")
        ),
        ApiEndpoint(
          "POST",
          "/api/projects",
          "创建项目",
          List(
            ApiParameter("name", "body", true, "string", "项目名称"),
            ApiParameter("description", "body", false, "string", "项目描述")
          ),
          List(
            ApiResponse(201, "创建成功", Some("Project")),
            ApiResponse(400, "请求参数错误"),
            ApiResponse(401, "未授权")
          ),
          List("项目管理")
        ),
        ApiEndpoint(
          "PUT",
          "/api/tasks/{taskId}/status",
          "更新任务状态",
          List(
            ApiParameter("taskId", "path", true, "string", "任务ID"),
            ApiParameter("status", "body", true, "string", "新状态")
          ),
          List(
            ApiResponse(200, "更新成功", Some("Task")),
            ApiResponse(400, "状态值无效"),
            ApiResponse(404, "任务不存在")
          ),
          List("任务管理")
        )
      )
    }
  }
  
  // 4. 领域模型文档生成器
  object DomainModelDocumentationGenerator {
    
    // 模型字段信息
    case class ModelField(
      name: String,
      fieldType: String,
      description: String,
      required: Boolean = true
    )
    
    // 模型信息
    case class DomainModel(
      name: String,
      description: String,
      fields: List[ModelField],
      relationships: List[String] = List.empty
    )
    
    // 生成领域模型文档
    def generateModelDocs(models: List[DomainModel]): DocumentPage = {
      val elements = ListBuffer[DocumentElement]()
      
      elements += Heading(1, "领域模型文档")
      elements += Text("本文档描述了系统中的核心领域模型及其关系。")
      elements += LineBreak
      
      models.foreach { model =>
        elements += Heading(2, model.name)
        elements += Text(model.description)
        elements += LineBreak
        
        // 字段表格
        elements += Heading(3, "字段")
        val fieldHeaders = List("名称", "类型", "必需", "描述")
        val fieldRows = model.fields.map(f => 
          List(f.name, f.fieldType, if (f.required) "是" else "否", f.description)
        )
        elements += Table(fieldHeaders, fieldRows)
        elements += LineBreak
        
        // 关系
        if (model.relationships.nonEmpty) {
          elements += Heading(3, "关系")
          model.relationships.foreach(rel => elements += ListItem(rel))
          elements += LineBreak
        }
      }
      
      DocumentPage(
        "领域模型文档",
        elements.toList,
        Map("author" -> "TaskFlow Team", "version" -> "1.0")
      )
    }
    
    // 生成示例领域模型数据
    def generateSampleModels(): List[DomainModel] = {
      List(
        DomainModel(
          "User",
          "系统用户实体，代表系统的使用者。",
          List(
            ModelField("id", "String", "用户唯一标识符"),
            ModelField("username", "String", "用户名，用于登录"),
            ModelField("email", "String", "用户邮箱地址"),
            ModelField("profile", "UserProfile", "用户个人资料"),
            ModelField("createdAt", "Long", "账户创建时间戳")
          ),
          List("一个用户可以创建多个项目", "一个用户可以分配到多个任务")
        ),
        DomainModel(
          "Project",
          "项目实体，用于组织和管理任务。",
          List(
            ModelField("id", "String", "项目唯一标识符"),
            ModelField("name", "String", "项目名称"),
            ModelField("description", "String", "项目描述", required = false),
            ModelField("ownerId", "String", "项目拥有者ID"),
            ModelField("createdAt", "Long", "项目创建时间戳"),
            ModelField("updatedAt", "Long", "项目更新时间戳")
          ),
          List("一个项目可以包含多个任务", "一个项目有一个拥有者（用户）")
        ),
        DomainModel(
          "Task",
          "任务实体，代表需要完成的工作单元。",
          List(
            ModelField("id", "String", "任务唯一标识符"),
            ModelField("title", "String", "任务标题"),
            ModelField("description", "String", "任务描述", required = false),
            ModelField("priority", "Priority", "任务优先级"),
            ModelField("status", "TaskStatus", "任务状态"),
            ModelField("assigneeId", "String", "任务负责人ID", required = false),
            ModelField("reporterId", "String", "任务报告人ID"),
            ModelField("projectId", "String", "所属项目ID"),
            ModelField("dueDate", "Long", "截止日期时间戳", required = false),
            ModelField("createdAt", "Long", "任务创建时间戳"),
            ModelField("updatedAt", "Long", "任务更新时间戳")
          ),
          List("一个任务属于一个项目", "一个任务有一个报告人（用户）", "一个任务可以有一个负责人（用户）")
        )
      )
    }
  }
  
  // 5. 架构文档生成器
  object ArchitectureDocumentationGenerator {
    
    // 组件信息
    case class Component(
      name: String,
      description: String,
      responsibilities: List[String],
      technologies: List[String]
    )
    
    // 生成架构文档
    def generateArchitectureDocs(components: List[Component]): DocumentPage = {
      val elements = ListBuffer[DocumentElement]()
      
      elements += Heading(1, "系统架构文档")
      elements += Text("本文档描述了 TaskFlow 系统的整体架构设计。")
      elements += LineBreak
      
      elements += Heading(2, "架构概览")
      elements += Text("TaskFlow 采用分层架构设计，主要包括以下几个层次：")
      elements += LineBreak
      
      // 添加架构图（文本表示）
      elements ++= List(
        Text("┌─────────────────────────────────────────────┐"),
        Text("│              表现层 (Presentation Layer)     │"),
        Text("│           (Web API, CLI, GUI)               │"),
        Text("└─────────────────┬───────────────────────────┘"),
        Text("                  │"),
        Text("┌─────────────────▼───────────────────────────┐"),
        Text("│              应用层 (Application Layer)      │"),
        Text("│         (Services, Use Cases)               │"),
        Text("└─────────────────┬───────────────────────────┘"),
        Text("                  │"),
        Text("┌─────────────────▼───────────────────────────┐"),
        Text("│              领域层 (Domain Layer)           │"),
        Text("│       (Entities, Value Objects)             │"),
        Text("└─────────────────┬───────────────────────────┘"),
        Text("                  │"),
        Text("┌─────────────────▼───────────────────────────┐"),
        Text("│              基础设施层 (Infrastructure)     │"),
        Text("│        (Repositories, Adapters)             │"),
        Text("└─────────────────────────────────────────────┘"),
        LineBreak
      )
      
      components.foreach { component =>
        elements += Heading(2, component.name)
        elements += Text(component.description)
        elements += LineBreak
        
        elements += Heading(3, "职责")
        component.responsibilities.foreach(resp => elements += ListItem(resp))
        elements += LineBreak
        
        elements += Heading(3, "技术栈")
        component.technologies.foreach(tech => elements += ListItem(tech))
        elements += LineBreak
      }
      
      DocumentPage(
        "系统架构文档",
        elements.toList,
        Map("author" -> "TaskFlow Team", "version" -> "1.0")
      )
    }
    
    // 生成示例组件数据
    def generateSampleComponents(): List[Component] = {
      List(
        Component(
          "表现层",
          "负责处理用户交互，包括 Web API、命令行界面和其他客户端接口。",
          List(
            "接收用户请求",
            "解析和验证输入数据",
            "格式化输出响应",
            "处理认证和授权"
          ),
          List("Akka HTTP", "circe", "Scala")
        ),
        Component(
          "应用层",
          "包含应用程序的核心业务逻辑，协调领域对象和基础设施组件。",
          List(
            "实现用例",
            "管理事务边界",
            "处理跨领域关注点",
            "编排领域服务"
          ),
          List("Scala", "Cats Effect", "ZIO")
        ),
        Component(
          "领域层",
          "包含核心业务规则和领域知识，是系统中最核心的部分。",
          List(
            "定义领域实体和值对象",
            "实现领域服务",
            "封装业务规则",
            "确保一致性约束"
          ),
          List("Scala", "类型系统")
        ),
        Component(
          "基础设施层",
          "提供技术实现细节，如数据库访问、外部服务集成等。",
          List(
            "持久化领域对象",
            "集成外部系统",
            "处理技术关注点",
            "实现适配器模式"
          ),
          List("PostgreSQL", "Doobie", "Redis", "Akka")
        )
      )
    }
  }
  
  // 6. Markdown文档渲染器
  object MarkdownRenderer {
    
    // 将文档页面渲染为Markdown格式
    def renderToMarkdown(page: DocumentPage): String = {
      val sb = new StringBuilder()
      
      // 添加元数据
      page.metadata.foreach { case (key, value) =>
        sb.append(s"<!-- $key: $value -->\n")
      }
      sb.append("\n")
      
      // 添加标题
      sb.append(s"# ${page.title}\n\n")
      
      // 渲染元素
      page.elements.foreach {
        case Text(content) => sb.append(s"$content\n\n")
        case CodeBlock(language, content) =>
          sb.append(s"```$language\n$content\n```\n\n")
        case Heading(level, content) =>
          val hashes = "#" * level
          sb.append(s"$hashes $content\n\n")
        case ListItem(content) => sb.append(s"- $content\n")
        case Link(text, url) => sb.append(s"[$text]($url)")
        case Image(alt, url) => sb.append(s"![$alt]($url)")
        case LineBreak => sb.append("\n")
        case Table(headers, rows) =>
          // 表头
          sb.append("| ")
          sb.append(headers.mkString(" | "))
          sb.append(" |\n")
          
          // 分隔线
          sb.append("| ")
          sb.append(headers.map(_ => "---").mkString(" | "))
          sb.append(" |\n")
          
          // 数据行
          rows.foreach { row =>
            sb.append("| ")
            sb.append(row.mkString(" | "))
            sb.append(" |\n")
          }
          sb.append("\n")
      }
      
      sb.toString
    }
    
    // 保存Markdown文档到文件
    def saveToFile(page: DocumentPage, filePath: String): Unit = {
      val markdown = renderToMarkdown(page)
      val writer = new PrintWriter(new File(filePath))
      try {
        writer.write(markdown)
        println(s"文档已保存到: $filePath")
      } finally {
        writer.close()
      }
    }
  }
  
  // 7. HTML文档渲染器
  object HtmlRenderer {
    
    // 将文档页面渲染为HTML格式
    def renderToHtml(page: DocumentPage): String = {
      val sb = new StringBuilder()
      
      // HTML头部
      sb.append("<!DOCTYPE html>\n")
      sb.append("<html lang=\"zh-CN\">\n")
      sb.append("<head>\n")
      sb.append("  <meta charset=\"UTF-8\">\n")
      sb.append(s"  <title>${page.title}</title>\n")
      sb.append("  <style>\n")
      sb.append("    body { font-family: Arial, sans-serif; margin: 40px; }\n")
      sb.append("    h1, h2, h3 { color: #333; }\n")
      sb.append("    table { border-collapse: collapse; width: 100%; margin: 20px 0; }\n")
      sb.append("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
      sb.append("    th { background-color: #f2f2f2; }\n")
      sb.append("    pre { background-color: #f5f5f5; padding: 10px; overflow-x: auto; }\n")
      sb.append("  </style>\n")
      sb.append("</head>\n")
      sb.append("<body>\n")
      
      // 添加标题
      sb.append(s"<h1>${page.title}</h1>\n")
      
      // 添加元数据
      if (page.metadata.nonEmpty) {
        sb.append("<div style=\"background-color: #f0f0f0; padding: 10px; margin-bottom: 20px;\">\n")
        sb.append("<strong>文档信息:</strong><br/>\n")
        page.metadata.foreach { case (key, value) =>
          sb.append(s"$key: $value<br/>\n")
        }
        sb.append("</div>\n")
      }
      
      // 渲染元素
      page.elements.foreach {
        case Text(content) => sb.append(s"<p>$content</p>\n")
        case CodeBlock(language, content) =>
          sb.append("<pre><code>")
          sb.append(content.replace("<", "&lt;").replace(">", "&gt;"))
          sb.append("</code></pre>\n")
        case Heading(1, content) => sb.append(s"<h1>$content</h1>\n")
        case Heading(2, content) => sb.append(s"<h2>$content</h2>\n")
        case Heading(3, content) => sb.append(s"<h3>$content</h3>\n")
        case ListItem(content) => sb.append(s"<li>$content</li>\n")
        case Link(text, url) => sb.append(s"""<a href="$url">$text</a>""")
        case Image(alt, url) => sb.append(s"""<img src="$url" alt="$alt">\n""")
        case LineBreak => sb.append("<br/>\n")
        case Table(headers, rows) =>
          sb.append("<table>\n")
          // 表头
          sb.append("<thead>\n<tr>\n")
          headers.foreach(header => sb.append(s"<th>$header</th>\n"))
          sb.append("</tr>\n</thead>\n")
          
          // 数据行
          sb.append("<tbody>\n")
          rows.foreach { row =>
            sb.append("<tr>\n")
            row.foreach(cell => sb.append(s"<td>$cell</td>\n"))
            sb.append("</tr>\n")
          }
          sb.append("</tbody>\n")
          sb.append("</table>\n")
      }
      
      // HTML尾部
      sb.append("</body>\n")
      sb.append("</html>")
      
      sb.toString
    }
    
    // 保存HTML文档到文件
    def saveToFile(page: DocumentPage, filePath: String): Unit = {
      val html = renderToHtml(page)
      val writer = new PrintWriter(new File(filePath))
      try {
        writer.write(html)
        println(s"文档已保存到: $filePath")
      } finally {
        writer.close()
      }
    }
  }
  
  // 8. 文档生成主程序
  def main(args: Array[String]): Unit = {
    println("=== TaskFlow 文档生成器 ===")
    
    // 创建输出目录
    val docsDir = "docs"
    new File(docsDir).mkdirs()
    
    // 生成API文档
    println("生成API文档...")
    val apiEndpoints = ApiDocumentationGenerator.generateSampleEndpoints()
    val apiDocPage = ApiDocumentationGenerator.generateApiDocs(apiEndpoints)
    MarkdownRenderer.saveToFile(apiDocPage, s"$docsDir/api.md")
    HtmlRenderer.saveToFile(apiDocPage, s"$docsDir/api.html")
    
    // 生成领域模型文档
    println("生成领域模型文档...")
    val domainModels = DomainModelDocumentationGenerator.generateSampleModels()
    val modelDocPage = DomainModelDocumentationGenerator.generateModelDocs(domainModels)
    MarkdownRenderer.saveToFile(modelDocPage, s"$docsDir/models.md")
    HtmlRenderer.saveToFile(modelDocPage, s"$docsDir/models.html")
    
    // 生成架构文档
    println("生成架构文档...")
    val components = ArchitectureDocumentationGenerator.generateSampleComponents()
    val archDocPage = ArchitectureDocumentationGenerator.generateArchitectureDocs(components)
    MarkdownRenderer.saveToFile(archDocPage, s"$docsDir/architecture.md")
    HtmlRenderer.saveToFile(archDocPage, s"$docsDir/architecture.html")
    
    println("所有文档已生成完成！")
    println(s"文档保存在: $docsDir/")
  }
}