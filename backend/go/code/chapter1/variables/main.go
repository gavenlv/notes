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