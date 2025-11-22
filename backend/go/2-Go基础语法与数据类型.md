# 第2章：Go基础语法与数据类型

## 2.1 变量与常量

### 2.1.1 变量声明

Go语言提供了多种变量声明方式：

```go
package main

import "fmt"

func main() {
    // 方式1：标准声明
    var name string = "张三"
    
    // 方式2：类型推断
    var age = 25
    
    // 方式3：简短声明（只能在函数内使用）
    height := 175.5
    
    // 方式4：批量声明
    var (
        country = "中国"
        city    = "北京"
    )
    
    fmt.Printf("姓名: %s\n", name)
    fmt.Printf("年龄: %d\n", age)
    fmt.Printf("身高: %.1f\n", height)
    fmt.Printf("地址: %s%s\n", country, city)
}
```

### 2.1.2 常量声明

常量使用 `const` 关键字声明，值在编译时确定：

```go
package main

import "fmt"

func main() {
    // 单个常量声明
    const PI = 3.14159
    
    // 批量常量声明
    const (
        VERSION = "1.0.0"
        AUTHOR  = "Google"
    )
    
    // 枚举常量（使用iota）
    const (
        MONDAY = iota + 1
        TUESDAY
        WEDNESDAY
        THURSDAY
        FRIDAY
        SATURDAY
        SUNDAY
    )
    
    fmt.Printf("PI: %.5f\n", PI)
    fmt.Printf("版本: %s\n", VERSION)
    fmt.Printf("作者: %s\n", AUTHOR)
    fmt.Printf("星期一: %d\n", MONDAY)
    fmt.Printf("星期日: %d\n", SUNDAY)
}
```

## 2.2 基本数据类型

### 2.2.1 整数类型

Go语言提供了多种整数类型：

```go
package main

import (
    "fmt"
    "unsafe"
)

func main() {
    // 有符号整数
    var i8 int8 = 127
    var i16 int16 = 32767
    var i32 int32 = 2147483647
    var i64 int64 = 9223372036854775807
    var i int = 42 // 平台相关，32位或64位
    
    // 无符号整数
    var u8 uint8 = 255
    var u16 uint16 = 65535
    var u32 uint32 = 4294967295
    var u64 uint64 = 18446744073709551615
    var u uint = 42 // 平台相关
    
    // 特殊类型
    var r rune = '中' // int32的别名，用于Unicode字符
    var b byte = 'A'  // uint8的别名
    
    fmt.Printf("int8大小: %d字节\n", unsafe.Sizeof(i8))
    fmt.Printf("int64大小: %d字节\n", unsafe.Sizeof(i64))
    fmt.Printf("rune值: %c, 数值: %d\n", r, r)
    fmt.Printf("byte值: %c, 数值: %d\n", b, b)
}
```

### 2.2.2 浮点数类型

```go
package main

import (
    "fmt"
    "math"
)

func main() {
    var f32 float32 = 3.1415926
    var f64 float64 = 3.141592653589793
    
    // 科学计数法
    var scientific float64 = 1.23e-4
    
    fmt.Printf("float32: %.7f\n", f32)
    fmt.Printf("float64: %.15f\n", f64)
    fmt.Printf("科学计数法: %e\n", scientific)
    fmt.Printf("π的平方: %.2f\n", math.Pi*math.Pi)
}
```

### 2.2.3 布尔类型

```go
package main

import "fmt"

func main() {
    var isActive bool = true
    var isCompleted bool = false
    
    // 逻辑运算
    fmt.Printf("isActive: %t\n", isActive)
    fmt.Printf("isCompleted: %t\n", isCompleted)
    fmt.Printf("逻辑与: %t\n", isActive && isCompleted)
    fmt.Printf("逻辑或: %t\n", isActive || isCompleted)
    fmt.Printf("逻辑非: %t\n", !isActive)
}
```

### 2.2.4 字符串类型

```go
package main

import (
    "fmt"
    "strings"
)

func main() {
    // 字符串声明
    var str1 string = "Hello, "
    str2 := "World!"
    
    // 字符串拼接
    greeting := str1 + str2
    
    // 字符串长度
    length := len(greeting)
    
    // 字符串操作
    upper := strings.ToUpper(greeting)
    lower := strings.ToLower(greeting)
    contains := strings.Contains(greeting, "World")
    
    fmt.Printf("拼接结果: %s\n", greeting)
    fmt.Printf("字符串长度: %d\n", length)
    fmt.Printf("大写: %s\n", upper)
    fmt.Printf("小写: %s\n", lower)
    fmt.Printf("包含'World': %t\n", contains)
    
    // 遍历字符串
    fmt.Print("字符遍历: ")
    for i, ch := range greeting {
        fmt.Printf("[%d:%c] ", i, ch)
    }
    fmt.Println()
}
```

## 2.3 运算符

### 2.3.1 算术运算符

```go
package main

import "fmt"

func main() {
    a, b := 15, 7
    
    fmt.Printf("%d + %d = %d\n", a, b, a+b)
    fmt.Printf("%d - %d = %d\n", a, b, a-b)
    fmt.Printf("%d * %d = %d\n", a, b, a*b)
    fmt.Printf("%d / %d = %d\n", a, b, a/b)
    fmt.Printf("%d %% %d = %d\n", a, b, a%b)
    
    // 自增自减
    a++
    b--
    fmt.Printf("a++ = %d\n", a)
    fmt.Printf("b-- = %d\n", b)
}
```

### 2.3.2 比较运算符

```go
package main

import "fmt"

func main() {
    x, y := 10, 20
    
    fmt.Printf("%d == %d: %t\n", x, y, x == y)
    fmt.Printf("%d != %d: %t\n", x, y, x != y)
    fmt.Printf("%d > %d: %t\n", x, y, x > y)
    fmt.Printf("%d < %d: %t\n", x, y, x < y)
    fmt.Printf("%d >= %d: %t\n", x, y, x >= y)
    fmt.Printf("%d <= %d: %t\n", x, y, x <= y)
}
```

### 2.3.3 逻辑运算符

```go
package main

import "fmt"

func main() {
    a, b := true, false
    
    fmt.Printf("%t && %t: %t\n", a, b, a && b)
    fmt.Printf("%t || %t: %t\n", a, b, a || b)
    fmt.Printf("!%t: %t\n", a, !a)
}
```

### 2.3.4 位运算符

```go
package main

import "fmt"

func main() {
    a, b := 5, 3 // 二进制: 0101, 0011
    
    fmt.Printf("%d & %d = %d\n", a, b, a&b)  // 按位与: 0001 = 1
    fmt.Printf("%d | %d = %d\n", a, b, a|b)  // 按位或: 0111 = 7
    fmt.Printf("%d ^ %d = %d\n", a, b, a^b)  // 按位异或: 0110 = 6
    fmt.Printf("%d << 1 = %d\n", a, a<<1)    // 左移: 1010 = 10
    fmt.Printf("%d >> 1 = %d\n", a, a>>1)    // 右移: 0010 = 2
}
```

## 2.4 类型转换

Go语言要求显式类型转换：

```go
package main

import "fmt"

func main() {
    // 整数类型转换
    var i32 int32 = 100
    var i64 int64 = int64(i32)
    
    // 浮点数转换
    var f32 float32 = 3.14
    var f64 float64 = float64(f32)
    
    // 整数与浮点数转换
    var integer int = 42
    var float float64 = float64(integer)
    
    // 字符串与数字转换
    var str string = "123"
    // 注意：实际转换需要strconv包，这里只是示例
    
    fmt.Printf("int32转int64: %d -> %d\n", i32, i64)
    fmt.Printf("float32转float64: %.2f -> %.2f\n", f32, f64)
    fmt.Printf("int转float64: %d -> %.2f\n", integer, float)
    fmt.Printf("字符串: %s\n", str)
}
```

## 2.5 零值

Go语言中，未初始化的变量会有默认零值：

```go
package main

import "fmt"

func main() {
    var i int
    var f float64
    var b bool
    var s string
    
    fmt.Printf("int零值: %d\n", i)
    fmt.Printf("float64零值: %f\n", f)
    fmt.Printf("bool零值: %t\n", b)
    fmt.Printf("string零值: '%s'\n", s)
    
    // 验证零值是否为空
    if s == "" {
        fmt.Println("字符串零值为空字符串")
    }
    
    if !b {
        fmt.Println("布尔零值为false")
    }
}
```

## 2.6 实践练习

### 练习1：温度转换器

```go
package main

import "fmt"

func main() {
    // 摄氏温度转华氏温度
    celsius := 25.0
    fahrenheit := celsius*9/5 + 32
    
    fmt.Printf("摄氏温度: %.1f°C\n", celsius)
    fmt.Printf("华氏温度: %.1f°F\n", fahrenheit)
    
    // 华氏温度转摄氏温度
    fahrenheit2 := 77.0
    celsius2 := (fahrenheit2 - 32) * 5 / 9
    
    fmt.Printf("华氏温度: %.1f°F\n", fahrenheit2)
    fmt.Printf("摄氏温度: %.1f°C\n", celsius2)
}
```

### 练习2：位运算应用

```go
package main

import "fmt"

func main() {
    // 权限控制示例
    const (
        ReadPermission = 1 << iota  // 1 (二进制: 0001)
        WritePermission             // 2 (二进制: 0010)
        ExecutePermission           // 4 (二进制: 0100)
        AdminPermission             // 8 (二进制: 1000)
    )
    
    // 用户权限
    userPermission := ReadPermission | WritePermission
    adminPermission := ReadPermission | WritePermission | ExecutePermission | AdminPermission
    
    // 检查权限
    fmt.Printf("用户权限: %d\n", userPermission)
    fmt.Printf("有读权限: %t\n", userPermission&ReadPermission != 0)
    fmt.Printf("有执行权限: %t\n", userPermission&ExecutePermission != 0)
    
    fmt.Printf("管理员权限: %d\n", adminPermission)
    fmt.Printf("有所有权限: %t\n", adminPermission&(ReadPermission|WritePermission|ExecutePermission|AdminPermission) == 
        ReadPermission|WritePermission|ExecutePermission|AdminPermission)
}
```

### 练习3：字符串处理

```go
package main

import (
    "fmt"
    "strings"
)

func main() {
    text := "   Hello, Go Language!   "
    
    // 去除空格
    trimmed := strings.TrimSpace(text)
    
    // 大小写转换
    upper := strings.ToUpper(trimmed)
    lower := strings.ToLower(trimmed)
    
    // 字符串分割
    words := strings.Split(trimmed, " ")
    
    // 字符串替换
    replaced := strings.Replace(trimmed, "Go", "Golang", -1)
    
    fmt.Printf("原始文本: '%s'\n", text)
    fmt.Printf("去除空格: '%s'\n", trimmed)
    fmt.Printf("大写: '%s'\n", upper)
    fmt.Printf("小写: '%s'\n", lower)
    fmt.Printf("分割结果: %v\n", words)
    fmt.Printf("替换后: '%s'\n", replaced)
    
    // 判断前缀和后缀
    fmt.Printf("以'Hello'开头: %t\n", strings.HasPrefix(trimmed, "Hello"))
    fmt.Printf("以'!'结尾: %t\n", strings.HasSuffix(trimmed, "!"))
}
```

## 2.7 最佳实践

### 变量命名规范
1. 使用驼峰命名法：`userName`、`totalCount`
2. 包级变量使用有意义的名称
3. 局部变量可以使用简短名称
4. 常量使用大写字母和下划线：`MAX_SIZE`

### 类型选择建议
1. 整数：优先使用 `int`，除非有特殊需求
2. 浮点数：优先使用 `float64`
3. 字符串：使用 `string` 类型
4. 布尔值：使用 `bool` 类型

### 性能考虑
1. 避免不必要的类型转换
2. 使用合适的整数类型节省内存
3. 字符串拼接使用 `strings.Builder`（后续章节介绍）

## 2.8 常见问题与解决方案

### 问题1：类型不匹配错误
```go
var a int = 10
var b int32 = 20
// result := a + b // 错误：类型不匹配
result := int32(a) + b // 正确：显式转换
```

### 问题2：整数溢出
```go
var i8 int8 = 127
i8++ // 溢出，变为-128
```

### 问题3：浮点数精度问题
```go
var f1 float64 = 0.1
var f2 float64 = 0.2
fmt.Println(f1 + f2) // 0.30000000000000004
```

## 2.9 本章总结

本章我们深入学习了：
- 变量和常量的多种声明方式
- Go语言的基本数据类型及其特性
- 各种运算符的使用方法
- 类型转换的规则和注意事项
- 变量的零值概念

通过实践练习，我们掌握了温度转换、位运算权限控制、字符串处理等实用技能。下一章我们将学习流程控制和函数，这是编程的核心概念。

---

**下一章预告**：第3章将详细介绍条件语句、循环语句和函数的定义与使用。