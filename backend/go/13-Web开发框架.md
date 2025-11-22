# 第13章：Web开发框架

## 13.1 标准库HTTP服务器

### 13.1.1 基础HTTP服务器

```go
package main

import (
    "fmt"
    "log"
    "net/http"
)

func main() {
    // 注册路由处理函数
    http.HandleFunc("/", homeHandler)
    http.HandleFunc("/hello", helloHandler)
    http.HandleFunc("/api/users", usersHandler)
    
    // 启动服务器
    fmt.Println("服务器启动在 http://localhost:8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
    if r.URL.Path != "/" {
        http.NotFound(w, r)
        return
    }
    
    w.Header().Set("Content-Type", "text/html; charset=utf-8")
    fmt.Fprintf(w, `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Go Web Server</title>
        </head>
        <body>
            <h1>欢迎来到Go Web服务器</h1>
            <p>这是一个使用标准库构建的Web服务器</p>
            <ul>
                <li><a href="/hello">Hello页面</a></li>
                <li><a href="/api/users">用户API</a></li>
            </ul>
        </body>
        </html>
    `)
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
    name := r.URL.Query().Get("name")
    if name == "" {
        name = "World"
    }
    
    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
    fmt.Fprintf(w, "Hello, %s!\n", name)
}

func usersHandler(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        getUsers(w, r)
    case "POST":
        createUser(w, r)
    case "PUT":
        updateUser(w, r)
    case "DELETE":
        deleteUser(w, r)
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }
}

func getUsers(w http.ResponseWriter, r *http.Request) {
    users := []map[string]interface{}{
        {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
        {"id": 2, "name": "李四", "email": "lisi@example.com"},
    }
    
    w.Header().Set("Content-Type", "application/json")
    fmt.Fprintf(w, `{"users": %v}`, users)
}

func createUser(w http.ResponseWriter, r *http.Request) {
    // 这里应该解析请求体并创建用户
    w.Header().Set("Content-Type", "application/json")
    fmt.Fprintf(w, `{"message": "用户创建成功", "id": 3}`)
}
```

### 13.1.2 自定义路由器

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "strings"
)

type Router struct {
    routes map[string]http.HandlerFunc
}

func NewRouter() *Router {
    return &Router{
        routes: make(map[string]http.HandlerFunc),
    }
}

func (r *Router) Handle(pattern string, handler http.HandlerFunc) {
    r.routes[pattern] = handler
}

func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    // 查找匹配的路由
    for pattern, handler := range r.routes {
        if r.match(pattern, req.URL.Path) {
            handler(w, req)
            return
        }
    }
    
    // 未找到路由
    http.NotFound(w, req)
}

func (r *Router) match(pattern, path string) bool {
    if pattern == path {
        return true
    }
    
    // 简单的通配符匹配
    if strings.Contains(pattern, "*") {
        prefix := strings.TrimSuffix(pattern, "/*")
        return strings.HasPrefix(path, prefix)
    }
    
    return false
}

func main() {
    router := NewRouter()
    
    router.Handle("/", homeHandler)
    router.Handle("/about", aboutHandler)
    router.Handle("/api/*", apiHandler)
    
    fmt.Println("自定义路由器启动在 http://localhost:8080")
    log.Fatal(http.ListenAndServe(":8080", router))
}

func aboutHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "关于我们页面")
}

func apiHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "API路径: %s", r.URL.Path)
}
```

## 13.2 Gin框架入门

### 13.2.1 基础Gin应用

```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    // 创建Gin实例
    r := gin.Default()
    
    // 添加中间件
    r.Use(gin.Logger())
    r.Use(gin.Recovery())
    
    // 静态文件服务
    r.Static("/static", "./static")
    
    // 路由定义
    r.GET("/", homePage)
    r.GET("/hello", helloHandler)
    r.GET("/users/:id", getUser)
    r.POST("/users", createUser)
    r.PUT("/users/:id", updateUser)
    r.DELETE("/users/:id", deleteUser)
    
    // 启动服务器
    r.Run(":8080")
}

func homePage(c *gin.Context) {
    c.HTML(http.StatusOK, "index.html", gin.H{
        "title": "Gin Web应用",
        "message": "欢迎使用Gin框架",
    })
}

func helloHandler(c *gin.Context) {
    name := c.DefaultQuery("name", "World")
    c.JSON(http.StatusOK, gin.H{
        "message": "Hello " + name,
    })
}

func getUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{
        "id": id,
        "name": "用户" + id,
        "email": "user" + id + "@example.com",
    })
}

func createUser(c *gin.Context) {
    var user struct {
        Name  string `json:"name" binding:"required"`
        Email string `json:"email" binding:"required,email"`
    }
    
    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    
    c.JSON(http.StatusCreated, gin.H{
        "message": "用户创建成功",
        "user": user,
    })
}

func updateUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{
        "message": "用户更新成功",
        "id": id,
    })
}

func deleteUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{
        "message": "用户删除成功",
        "id": id,
    })
}
```

### 13.2.2 中间件开发

```go
package main

import (
    "fmt"
    "net/http"
    "time"
    "github.com/gin-gonic/gin"
)

// 认证中间件
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "未授权"})
            c.Abort()
            return
        }
        
        // 简单的token验证
        if token != "Bearer secret-token" {
            c.JSON(http.StatusForbidden, gin.H{"error": "令牌无效"})
            c.Abort()
            return
        }
        
        c.Next()
    }
}

// 日志中间件
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        c.Next()
        
        duration := time.Since(start)
        fmt.Printf("%s %s %s %v\n", 
            c.Request.Method, 
            c.Request.URL.Path, 
            c.ClientIP(), 
            duration)
    }
}

// 限流中间件
func RateLimitMiddleware(maxRequests int, window time.Duration) gin.HandlerFunc {
    requests := make(map[string][]time.Time)
    
    return func(c *gin.Context) {
        clientIP := c.ClientIP()
        now := time.Now()
        
        // 清理过期请求
        if clientRequests, exists := requests[clientIP]; exists {
            var validRequests []time.Time
            for _, reqTime := range clientRequests {
                if now.Sub(reqTime) < window {
                    validRequests = append(validRequests, reqTime)
                }
            }
            requests[clientIP] = validRequests
        }
        
        // 检查请求次数
        if len(requests[clientIP]) >= maxRequests {
            c.JSON(http.StatusTooManyRequests, gin.H{
                "error": "请求过于频繁，请稍后再试",
            })
            c.Abort()
            return
        }
        
        // 记录当前请求
        requests[clientIP] = append(requests[clientIP], now)
        c.Next()
    }
}

func main() {
    r := gin.Default()
    
    // 注册中间件
    r.Use(LoggerMiddleware())
    r.Use(RateLimitMiddleware(10, time.Minute))
    
    // 公开路由
    r.GET("/public", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "公开接口"})
    })
    
    // 需要认证的路由组
    api := r.Group("/api")
    api.Use(AuthMiddleware())
    {
        api.GET("/users", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"users": "用户列表"})
        })
        
        api.POST("/users", func(c *gin.Context) {
            c.JSON(http.StatusCreated, gin.H{"message": "用户创建成功"})
        })
    }
    
    r.Run(":8080")
}
```

## 13.3 Echo框架

### 13.3.1 Echo基础使用

```go
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

var users = []User{
    {ID: 1, Name: "张三", Email: "zhangsan@example.com"},
    {ID: 2, Name: "李四", Email: "lisi@example.com"},
}

func main() {
    // 创建Echo实例
    e := echo.New()
    
    // 中间件
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Use(middleware.CORS())
    
    // 路由
    e.GET("/", homeHandler)
    e.GET("/users", getUsers)
    e.GET("/users/:id", getUser)
    e.POST("/users", createUser)
    e.PUT("/users/:id", updateUser)
    e.DELETE("/users/:id", deleteUser)
    
    // 启动服务器
    e.Logger.Fatal(e.Start(":8080"))
}

func homeHandler(c echo.Context) error {
    return c.String(http.StatusOK, "欢迎使用Echo框架")
}

func getUsers(c echo.Context) error {
    return c.JSON(http.StatusOK, users)
}

func getUser(c echo.Context) error {
    id := c.Param("id")
    for _, user := range users {
        if fmt.Sprintf("%d", user.ID) == id {
            return c.JSON(http.StatusOK, user)
        }
    }
    return echo.ErrNotFound
}

func createUser(c echo.Context) error {
    var user User
    if err := c.Bind(&user); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, err.Error())
    }
    
    user.ID = len(users) + 1
    users = append(users, user)
    
    return c.JSON(http.StatusCreated, user)
}

func updateUser(c echo.Context) error {
    id := c.Param("id")
    var updatedUser User
    
    if err := c.Bind(&updatedUser); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, err.Error())
    }
    
    for i, user := range users {
        if fmt.Sprintf("%d", user.ID) == id {
            users[i] = updatedUser
            users[i].ID = user.ID
            return c.JSON(http.StatusOK, users[i])
        }
    }
    
    return echo.ErrNotFound
}

func deleteUser(c echo.Context) error {
    id := c.Param("id")
    
    for i, user := range users {
        if fmt.Sprintf("%d", user.ID) == id {
            users = append(users[:i], users[i+1:]...)
            return c.NoContent(http.StatusNoContent)
        }
    }
    
    return echo.ErrNotFound
}
```

## 13.4 模板渲染

### 13.4.1 HTML模板

```go
package main

import (
    "html/template"
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    
    // 加载模板
    r.LoadHTMLGlob("templates/*")
    
    // 静态文件
    r.Static("/assets", "./assets")
    
    r.GET("/", func(c *gin.Context) {
        data := gin.H{
            "title": "Go模板示例",
            "users": []map[string]string{
                {"name": "张三", "role": "管理员"},
                {"name": "李四", "role": "用户"},
                {"name": "王五", "role": "访客"},
            },
            "showWelcome": true,
        }
        
        c.HTML(http.StatusOK, "index.html", data)
    })
    
    r.Run(":8080")
}
```

### 13.4.2 模板文件 templates/index.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{.title}}</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <div class="container">
        <h1>{{.title}}</h1>
        
        {{if .showWelcome}}
        <div class="welcome">
            <p>欢迎使用我们的应用！</p>
        </div>
        {{end}}
        
        <h2>用户列表</h2>
        <table class="user-table">
            <thead>
                <tr>
                    <th>姓名</th>
                    <th>角色</th>
                </tr>
            </thead>
            <tbody>
                {{range .users}}
                <tr>
                    <td>{{.name}}</td>
                    <td>{{.role}}</td>
                </tr>
                {{end}}
            </tbody>
        </table>
        
        <div class="footer">
            <p>当前时间: {{now}}</p>
        </div>
    </div>
</body>
</html>
```

## 13.5 文件上传与下载

### 13.5.1 文件上传

```go
package main

import (
    "fmt"
    "net/http"
    "os"
    "path/filepath"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    
    // 文件上传路由
    r.POST("/upload", uploadHandler)
    r.GET("/download/:filename", downloadHandler)
    
    r.Run(":8080")
}

func uploadHandler(c *gin.Context) {
    // 单文件上传
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "文件上传失败"})
        return
    }
    
    // 创建上传目录
    uploadDir := "./uploads"
    if _, err := os.Stat(uploadDir); os.IsNotExist(err) {
        os.MkdirAll(uploadDir, 0755)
    }
    
    // 保存文件
    filename := filepath.Join(uploadDir, file.Filename)
    if err := c.SaveUploadedFile(file, filename); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "文件保存失败"})
        return
    }
    
    c.JSON(http.StatusOK, gin.H{
        "message": "文件上传成功",
        "filename": file.Filename,
        "size": file.Size,
    })
}

func downloadHandler(c *gin.Context) {
    filename := c.Param("filename")
    filepath := fmt.Sprintf("./uploads/%s", filename)
    
    // 检查文件是否存在
    if _, err := os.Stat(filepath); os.IsNotExist(err) {
        c.JSON(http.StatusNotFound, gin.H{"error": "文件不存在"})
        return
    }
    
    // 设置下载头
    c.Header("Content-Description", "File Transfer")
    c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filename))
    c.Header("Content-Type", "application/octet-stream")
    c.Header("Content-Transfer-Encoding", "binary")
    
    c.File(filepath)
}
```

## 13.6 最佳实践总结

1. **框架选择**：根据项目需求选择合适的框架（Gin、Echo等）
2. **中间件使用**：合理使用中间件处理通用逻辑
3. **错误处理**：统一错误处理机制
4. **路由组织**：使用路由分组管理相关路由
5. **模板渲染**：合理组织模板文件结构
6. **文件处理**：正确处理文件上传和下载的安全性问题