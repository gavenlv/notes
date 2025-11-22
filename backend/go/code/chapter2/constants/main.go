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