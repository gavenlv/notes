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