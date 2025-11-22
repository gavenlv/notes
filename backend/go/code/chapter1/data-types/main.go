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