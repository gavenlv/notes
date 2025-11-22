# 第1章：Go语言基础与环境搭建

## 1.1 Go语言简介

### 什么是Go语言？
Go语言（又称Golang）是Google开发的一种静态强类型、编译型、并发型，并具有垃圾回收功能的编程语言。它于2009年正式发布，由Robert Griesemer、Rob Pike和Ken Thompson三位计算机科学大牛设计。

### Go语言的设计哲学
1. **简洁性**：语法简洁，易于学习和使用
2. **高效性**：编译速度快，执行效率高
3. **并发性**：原生支持并发编程
4. **安全性**：强类型，内存安全
5. **跨平台**：支持多种操作系统和架构

### Go语言的应用场景
- 网络服务开发
- 云计算和微服务
- 分布式系统
- 命令行工具
- 区块链开发
- 数据处理和分析

## 1.2 环境搭建

### 1.2.1 安装Go

#### Windows系统安装
1. 访问 [Go官网下载页面](https://golang.org/dl/)
2. 下载Windows版本的安装包（.msi文件）
3. 双击安装包，按提示完成安装
4. 验证安装：打开命令提示符，输入 `go version`

#### macOS系统安装
```bash
# 使用Homebrew安装
brew install go

# 或者下载官方安装包
# 访问 https://golang.org/dl/ 下载macOS版本
```

#### Linux系统安装
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install golang-go

# CentOS/RHEL
sudo yum install golang

# 或者下载二进制包手动安装
wget https://golang.org/dl/go1.19.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
```

### 1.2.2 环境变量配置

Go需要配置以下环境变量：
- **GOROOT**：Go的安装目录
- **GOPATH**：工作目录（包含src、bin、pkg）
- **PATH**：添加Go的bin目录

#### Windows配置
```cmd
# 设置GOROOT（通常自动设置）
setx GOROOT "C:\Go"

# 设置GOPATH（工作目录）
setx GOPATH "%USERPROFILE%\go"

# 添加PATH
setx PATH "%PATH%;%GOROOT%\bin;%GOPATH%\bin"
```

#### Linux/macOS配置
```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin

# 使配置生效
source ~/.bashrc
```

### 1.2.3 验证安装

打开终端/命令提示符，执行以下命令验证安装：

```bash
go version
```

应该看到类似这样的输出：
```
go version go1.19.3 windows/amd64
```

## 1.3 第一个Go程序

### 1.3.1 创建项目目录

```bash
# 创建项目目录
mkdir -p $GOPATH/src/hello-world
cd $GOPATH/src/hello-world
```

### 1.3.2 编写第一个程序

创建 `main.go` 文件：

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
    fmt.Println("欢迎来到Go语言世界！")
}
```

### 1.3.3 程序结构解析

1. **package main**：包声明，main包是程序的入口
2. **import "fmt"**：导入fmt包，用于输入输出
3. **func main()**：主函数，程序执行的入口点
4. **fmt.Println()**：打印输出到控制台

### 1.3.4 编译和运行

#### 方式1：直接运行
```bash
go run main.go
```

#### 方式2：先编译后运行
```bash
# 编译
go build main.go

# 运行生成的可执行文件
./main.exe  # Windows: main.exe
```

#### 方式3：安装到GOPATH/bin
```bash
go install

# 然后可以直接运行
hello-world
```

## 1.4 Go模块（Go Modules）

Go Modules是Go语言的依赖管理系统，从Go 1.11开始引入。

### 1.4.1 初始化模块

```bash
# 在项目根目录执行
go mod init hello-world
```

这会创建 `go.mod` 文件：

```go
module hello-world

go 1.19
```

### 1.4.2 添加依赖

```bash
# 添加依赖
go get github.com/gin-gonic/gin

# 查看依赖
go list -m all

# 清理不需要的依赖
go mod tidy
```

## 1.5 开发工具推荐

### 1.5.1 代码编辑器

1. **Visual Studio Code**（推荐）
   - 安装Go扩展
   - 支持代码补全、调试、测试

2. **GoLand**（JetBrains出品）
   - 专业的Go IDE
   - 功能全面但需要付费

3. **Vim/Neovim**
   - 配置vim-go插件
   - 适合命令行爱好者

### 1.5.2 VS Code配置

1. 安装VS Code
2. 安装Go扩展
3. 安装必要的工具：
   ```bash
   # 在VS Code中按Ctrl+Shift+P，输入Go: Install/Update Tools
   # 选择所有工具并安装
   ```

## 1.6 基础语法概览

### 1.6.1 变量声明

```go
package main

import "fmt"

func main() {
    // 方式1：使用var关键字
    var name string = "Go语言"
    
    // 方式2：类型推断
    var version = 1.19
    
    // 方式3：简短声明（只能在函数内使用）
    author := "Google"
    
    fmt.Println("语言:", name)
    fmt.Println("版本:", version)
    fmt.Println("开发者:", author)
}
```

### 1.6.2 基本数据类型

```go
package main

import "fmt"

func main() {
    // 整数类型
    var age int = 25
    var score int32 = 95
    
    // 浮点数
    var price float64 = 19.99
    
    // 布尔类型
    var isActive bool = true
    
    // 字符串
    var message string = "Hello, Go!"
    
    fmt.Printf("年龄: %d\n", age)
    fmt.Printf("分数: %d\n", score)
    fmt.Printf("价格: %.2f\n", price)
    fmt.Printf("激活状态: %t\n", isActive)
    fmt.Printf("消息: %s\n", message)
}
```

## 1.7 实践练习

### 练习1：个人信息打印

创建一个程序，打印你的个人信息：

```go
package main

import "fmt"

func main() {
    name := "张三"
    age := 28
    height := 175.5
    isStudent := false
    
    fmt.Println("=== 个人信息 ===")
    fmt.Printf("姓名: %s\n", name)
    fmt.Printf("年龄: %d岁\n", age)
    fmt.Printf("身高: %.1fcm\n", height)
    fmt.Printf("学生身份: %t\n", isStudent)
}
```

### 练习2：简单计算器

```go
package main

import "fmt"

func main() {
    a := 15
    b := 7
    
    fmt.Printf("%d + %d = %d\n", a, b, a+b)
    fmt.Printf("%d - %d = %d\n", a, b, a-b)
    fmt.Printf("%d * %d = %d\n", a, b, a*b)
    fmt.Printf("%d / %d = %d\n", a, b, a/b)
    fmt.Printf("%d %% %d = %d\n", a, b, a%b)
}
```

## 1.8 常见问题与解决方案

### 问题1：go command not found
**原因**：Go没有正确安装或PATH环境变量未设置
**解决方案**：检查安装路径，确保PATH包含Go的bin目录

### 问题2：import cycle not allowed
**原因**：包之间存在循环依赖
**解决方案**：重构代码，消除循环依赖

### 问题3：undefined: function
**原因**：函数未定义或导入包不正确
**解决方案**：检查函数名拼写和包导入

## 1.9 本章总结

本章我们学习了：
- Go语言的基本概念和特点
- 在不同操作系统上安装Go环境
- 编写、编译和运行第一个Go程序
- Go模块的基本使用方法
- 推荐开发工具和配置
- 基础语法和数据类型

通过本章的学习，你已经成功搭建了Go开发环境，并能够编写简单的Go程序。下一章我们将深入学习Go的基础语法和数据类型。

---

**下一章预告**：第2章将详细介绍Go的基础语法、数据类型、运算符和控制结构。