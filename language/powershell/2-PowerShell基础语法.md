# 第2章：PowerShell基础语法

> **学习时长**: 4-5小时  
> **难度**: ⭐⭐  
> **前置知识**: 第1章

## 本章目标

学完本章后,你将能够:

- ✅ 理解Cmdlet命令结构(Verb-Noun)
- ✅ 使用Get-Help获取命令帮助
- ✅ 掌握命令别名系统
- ✅ 理解管道的基本概念
- ✅ 格式化输出结果
- ✅ 使用Tab补全提高效率

---

## 2.1 Cmdlet命令结构

### 2.1.1 什么是Cmdlet?

**Cmdlet** (发音: command-let) 是PowerShell的原生命令,遵循统一的命名规范。

**命名规则: Verb-Noun**

```powershell
# 格式: 动词-名词
Get-Process      # 获取进程
Stop-Service     # 停止服务
New-Item         # 创建项目
Set-Location     # 设置位置
Remove-Item      # 删除项目
```

**为什么使用这种命名?**

- ✅ **一致性**: 所有命令遵循相同模式
- ✅ **可预测**: 猜测命令名称很容易
- ✅ **易学习**: 记住动词,组合名词即可
- ✅ **自文档化**: 命令名本身就说明功能

### 2.1.2 常用动词

PowerShell定义了标准动词集:

| 动词 | 含义 | 示例 |
|------|------|------|
| **Get** | 获取资源 | `Get-Process`, `Get-Service` |
| **Set** | 设置/修改 | `Set-Location`, `Set-Content` |
| **New** | 创建新对象 | `New-Item`, `New-Object` |
| **Remove** | 删除资源 | `Remove-Item`, `Remove-Variable` |
| **Start** | 启动 | `Start-Service`, `Start-Process` |
| **Stop** | 停止 | `Stop-Service`, `Stop-Process` |
| **Out** | 输出数据 | `Out-File`, `Out-Host` |
| **Write** | 写入数据 | `Write-Host`, `Write-Output` |

**查看所有批准的动词**:

```powershell
Get-Verb

# 输出示例
Verb        AliasPrefix Group          Description
----        ----------- -----          -----------
Add         a           Common         Adds a resource to a container
Approve     ap          Lifecycle      Confirms the status of a resource
Clear       cl          Common         Removes all the resources from a container
...
```

**按组查看**:

```powershell
Get-Verb | Group-Object Group

# 按动词查找Cmdlet
Get-Command -Verb Get
Get-Command -Noun Process
Get-Command -Verb Get -Noun Service
```

### 2.1.3 Cmdlet vs 函数 vs 外部命令

```powershell
# Cmdlet - PowerShell原生命令(C#编写)
Get-Process

# 函数 - PowerShell脚本编写
function Get-MyInfo { Get-Date }

# 外部命令 - 可执行文件
ping.exe google.com
ipconfig.exe

# 查看命令类型
Get-Command Get-Process
Get-Command ping

# 输出
CommandType     Name            Version    Source
-----------     ----            -------    ------
Cmdlet          Get-Process     7.0.0.0    Microsoft.PowerShell.Management
Application     ping.exe        10.0.22... C:\Windows\system32\ping.exe
```

---

## 2.2 获取帮助

### 2.2.1 Get-Help命令

**基本用法**:

```powershell
# 获取命令帮助
Get-Help Get-Process

# 简洁帮助(默认)
Get-Help Get-Service

# 详细帮助
Get-Help Get-Process -Detailed

# 完整帮助
Get-Help Get-Process -Full

# 仅显示示例
Get-Help Get-Process -Examples

# 在线帮助(浏览器)
Get-Help Get-Process -Online

# 显示参数信息
Get-Help Get-Process -Parameter Name
```

**帮助内容结构**:

```powershell
Get-Help Get-Process

# 输出结构:
# NAME          - 命令名称
# SYNOPSIS      - 简要描述
# SYNTAX        - 语法结构
# DESCRIPTION   - 详细描述
# RELATED LINKS - 相关链接
# REMARKS       - 备注
```

### 2.2.2 更新帮助文档

**首次使用需要更新**:

```powershell
# 更新所有模块的帮助(需要管理员权限)
Update-Help

# 更新特定模块
Update-Help -Module Microsoft.PowerShell.Management

# 强制更新
Update-Help -Force

# 从本地路径更新
Update-Help -SourcePath C:\HelpFiles

# 下载帮助不安装
Save-Help -DestinationPath C:\HelpFiles
```

**常见错误处理**:

```powershell
# 如果Update-Help失败,可以跳过错误
Update-Help -ErrorAction SilentlyContinue

# 或指定语言
Update-Help -UICulture en-US
```

### 2.2.3 About主题

PowerShell概念性帮助:

```powershell
# 查看所有about主题
Get-Help about_*

# 查看特定主题
Get-Help about_Variables
Get-Help about_Arrays
Get-Help about_Operators
Get-Help about_Functions

# 常用主题
Get-Help about_Comparison_Operators  # 比较运算符
Get-Help about_Pipelines             # 管道
Get-Help about_Execution_Policies    # 执行策略
Get-Help about_Profiles              # Profile配置
```

---

## 2.3 命令发现

### 2.3.1 Get-Command

**查找命令**:

```powershell
# 列出所有命令
Get-Command

# 按类型筛选
Get-Command -CommandType Cmdlet
Get-Command -CommandType Function
Get-Command -CommandType Alias

# 按动词查找
Get-Command -Verb Get
Get-Command -Verb Set

# 按名词查找
Get-Command -Noun Process
Get-Command -Noun Service

# 组合查找
Get-Command -Verb Get -Noun Service

# 模糊匹配
Get-Command *process*
Get-Command Get-*Item*

# 按模块查找
Get-Command -Module Microsoft.PowerShell.Management
```

**查看命令详情**:

```powershell
# 查看命令定义
Get-Command Get-Process | Format-List *

# 查看参数
(Get-Command Get-Process).Parameters

# 查看参数集
(Get-Command Get-Process).ParameterSets
```

### 2.3.2 Get-Member

**探索对象成员**:

```powershell
# 查看对象的属性和方法
Get-Process | Get-Member

# 输出:
# TypeName: System.Diagnostics.Process
# Name              MemberType     Definition
# ----              ----------     ----------
# Kill              Method         void Kill()
# Start             Method         bool Start()
# ProcessName       Property       string ProcessName {get;}
# CPU               Property       double CPU {get;}
# ...

# 仅查看属性
Get-Process | Get-Member -MemberType Property

# 仅查看方法
Get-Process | Get-Member -MemberType Method

# 查看静态成员
[System.Math] | Get-Member -Static
```

---

## 2.4 别名系统

### 2.4.1 什么是别名?

**别名**是命令的快捷方式:

```powershell
# ls是Get-ChildItem的别名
ls
Get-ChildItem  # 等效

# dir也是Get-ChildItem的别名
dir

# pwd是Get-Location的别名
pwd
Get-Location  # 等效
```

**查看别名**:

```powershell
# 查看所有别名
Get-Alias

# 查看特定别名
Get-Alias ls
Get-Alias dir

# 查看命令的所有别名
Get-Alias -Definition Get-ChildItem

# 查找别名
Get-Alias | Where-Object {$_.Definition -eq "Get-Process"}
```

### 2.4.2 常用别名

| 别名 | 完整命令 | 说明 |
|------|----------|------|
| `ls, dir, gci` | `Get-ChildItem` | 列出文件 |
| `cd, chdir, sl` | `Set-Location` | 切换目录 |
| `pwd, gl` | `Get-Location` | 当前目录 |
| `cp, copy, cpi` | `Copy-Item` | 复制 |
| `mv, move, mi` | `Move-Item` | 移动 |
| `rm, del, erase` | `Remove-Item` | 删除 |
| `cat, type, gc` | `Get-Content` | 查看内容 |
| `echo, write` | `Write-Output` | 输出 |
| `man, help` | `Get-Help` | 帮助 |
| `cls, clear` | `Clear-Host` | 清屏 |

**兼容性别名**:

```powershell
# CMD兼容
dir, cd, copy, del, type, cls

# Bash兼容  
ls, pwd, cp, mv, rm, cat, man, clear

# PowerShell原生
gci, sl, gl, cpi, mi, ri, gc
```

### 2.4.3 创建自定义别名

```powershell
# 创建别名
Set-Alias -Name ll -Value Get-ChildItem

# 使用
ll

# 带参数的别名(需要函数)
function Get-ProcessByName { param($Name) Get-Process $Name }
Set-Alias -Name gp -Value Get-ProcessByName

# 查看新别名
Get-Alias ll

# 删除别名
Remove-Alias ll

# 导出别名
Export-Alias -Path aliases.txt

# 导入别名
Import-Alias -Path aliases.txt
```

**别名在Profile中持久化**:

```powershell
# 编辑Profile
notepad $PROFILE

# 添加别名
Set-Alias -Name ll -Value Get-ChildItem
Set-Alias -Name np -Value notepad.exe
```

---

## 2.5 参数

### 2.5.1 位置参数 vs 命名参数

**位置参数**:

```powershell
# 按位置传递
Get-Process notepad
# 等同于
Get-Process -Name notepad

# 多个位置参数
Copy-Item source.txt destination.txt
# 等同于
Copy-Item -Path source.txt -Destination destination.txt
```

**命名参数**:

```powershell
# 使用参数名(更清晰)
Get-Process -Name notepad

# 参数名可以缩写(只要唯一)
Get-Process -N notepad
Get-ChildItem -P C:\  # -Path

# 顺序无关
Get-ChildItem -Recurse -Path C:\Temp
Get-ChildItem -Path C:\Temp -Recurse  # 相同效果
```

### 2.5.2 开关参数

**开关参数**不需要值:

```powershell
# -Recurse是开关参数
Get-ChildItem -Path C:\ -Recurse

# -Force是开关参数
Remove-Item file.txt -Force

# 显式指定True/False
Get-ChildItem -Recurse:$true
Get-ChildItem -Recurse:$false
```

**常用开关参数**:

```powershell
-Force          # 强制执行
-Recurse        # 递归
-Confirm        # 确认操作
-WhatIf         # 模拟执行(不实际执行)
-Verbose        # 详细输出
-Debug          # 调试信息
```

### 2.5.3 通用参数

**所有Cmdlet都支持的参数**:

```powershell
# -Verbose: 详细输出
Get-Process -Verbose

# -Debug: 调试信息
Get-Process -Debug

# -ErrorAction: 错误处理
Get-Process -ErrorAction SilentlyContinue

# -WarningAction: 警告处理
Get-Process -WarningAction Continue

# -WhatIf: 预览操作(不执行)
Remove-Item file.txt -WhatIf

# -Confirm: 确认每个操作
Remove-Item *.txt -Confirm

# -OutVariable: 输出到变量
Get-Process -OutVariable procs
$procs  # 查看变量内容

# -OutBuffer: 输出缓冲区大小
Get-Process -OutBuffer 10
```

---

## 2.6 管道基础

### 2.6.1 什么是管道?

**管道** `|` 将一个命令的输出传递给另一个命令:

```powershell
# 基本管道
Get-Process | Where-Object {$_.CPU -gt 10}

# 多级管道
Get-Process | 
    Where-Object {$_.CPU -gt 10} | 
    Sort-Object CPU -Descending |
    Select-Object -First 5

# 管道传递的是对象,不是文本!
```

**PowerShell管道 vs Linux管道**:

| 特性 | PowerShell | Linux/Bash |
|------|-----------|------------|
| 传递内容 | .NET对象 | 纯文本 |
| 信息保留 | 完整属性和方法 | 仅文本 |
| 处理方式 | 属性访问 | 文本解析 |

### 2.6.2 管道示例

**文件操作**:

```powershell
# 查找大文件
Get-ChildItem C:\ -Recurse | 
    Where-Object {$_.Length -gt 100MB} |
    Sort-Object Length -Descending

# 批量重命名
Get-ChildItem *.txt | 
    Rename-Item -NewName {$_.Name -replace '.txt', '.log'}

# 删除空文件夹
Get-ChildItem -Directory -Recurse |
    Where-Object {(Get-ChildItem $_.FullName).Count -eq 0} |
    Remove-Item
```

**进程管理**:

```powershell
# 查找占用CPU高的进程
Get-Process | 
    Where-Object {$_.CPU -gt 100} |
    Select-Object Name, CPU, Id

# 停止特定进程
Get-Process notepad | Stop-Process

# 按内存排序
Get-Process |
    Sort-Object WS -Descending |
    Select-Object -First 10 Name, WS
```

---

## 2.7 格式化输出

### 2.7.1 Format命令

**Format-Table** (表格):

```powershell
# 默认表格
Get-Process | Format-Table

# 指定列
Get-Process | Format-Table Name, CPU, Id

# 自动调整列宽
Get-Process | Format-Table -AutoSize

# 包装文本
Get-Process | Format-Table -Wrap

# 自定义表头
Get-Process | Format-Table @{Label="Process";Expression={$_.Name}}, CPU
```

**Format-List** (列表):

```powershell
# 详细列表
Get-Process | Format-List

# 指定属性
Get-Process | Format-List Name, CPU, Id

# 查看所有属性
Get-Process | Format-List *
```

**Format-Wide** (宽格式):

```powershell
# 仅显示一个属性
Get-Process | Format-Wide Name

# 指定列数
Get-Process | Format-Wide Name -Column 3
```

**Format-Custom** (自定义):

```powershell
# 自定义格式
Get-Process | Format-Custom
```

### 2.7.2 Select-Object

**选择属性**:

```powershell
# 选择特定属性
Get-Process | Select-Object Name, CPU, Id

# 选择前N个
Get-Process | Select-Object -First 5

# 选择后N个
Get-Process | Select-Object -Last 5

# 跳过N个
Get-Process | Select-Object -Skip 5

# 去重
Get-Process | Select-Object ProcessName -Unique

# 计算属性
Get-Process | Select-Object Name, 
    @{Name="CPU(s)";Expression={$_.CPU}},
    @{Name="Memory(MB)";Expression={$_.WS/1MB}}
```

### 2.7.3 Out命令

```powershell
# 输出到主机
Get-Process | Out-Host

# 输出到文件
Get-Process | Out-File processes.txt

# 追加到文件
Get-Process | Out-File processes.txt -Append

# 输出到打印机
Get-Process | Out-Printer

# 输出到网格视图(GUI)
Get-Process | Out-GridView

# 输出到字符串
Get-Process | Out-String

# 输出到空(丢弃)
Get-Process | Out-Null
```

---

## 2.8 Tab补全

### 2.8.1 基本补全

```powershell
# 命令补全
Get-Pro<Tab>        # → Get-Process

# 参数补全
Get-Process -N<Tab> # → Get-Process -Name

# 文件路径补全
cd C:\Pro<Tab>      # → cd C:\Program Files\

# 枚举值补全
Get-Service -Status <Tab> # 循环显示可用值
```

### 2.8.2 高级补全

```powershell
# 参数值补全
Get-Process -Name <Tab>  # 显示运行的进程名

# 模块名补全
Import-Module <Tab>

# 历史命令补全
#<Tab>  # 循环历史命令

# PSReadLine增强(PowerShell 7+)
# Ctrl+Space: 智能补全
# F2: 菜单补全
```

---

## 2.9 实验:综合练习

### 实验1: 进程分析

```powershell
<#
.SYNOPSIS
    分析系统进程
.DESCRIPTION
    查找占用资源最多的进程并生成报告
#>

# 查找CPU占用最高的5个进程
Write-Host "`n=== Top 5 CPU Processes ===" -ForegroundColor Cyan
Get-Process | 
    Where-Object {$_.CPU -gt 0} |
    Sort-Object CPU -Descending |
    Select-Object -First 5 Name, CPU, Id |
    Format-Table -AutoSize

# 查找内存占用最高的5个进程
Write-Host "`n=== Top 5 Memory Processes ===" -ForegroundColor Cyan
Get-Process |
    Sort-Object WS -Descending |
    Select-Object -First 5 Name, 
        @{Name="Memory(MB)";Expression={[math]::Round($_.WS/1MB,2)}} |
    Format-Table -AutoSize

# 统计进程总数
$processCount = (Get-Process).Count
Write-Host "`nTotal Processes: $processCount" -ForegroundColor Green
```

### 实验2: 文件搜索工具

```powershell
<#
.SYNOPSIS
    搜索大文件
.DESCRIPTION
    查找指定目录下大于指定大小的文件
#>

param(
    [string]$Path = "C:\",
    [int]$SizeMB = 100
)

Write-Host "Searching for files larger than $SizeMB MB in $Path..." -ForegroundColor Yellow

Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object {$_.Length -gt ($SizeMB * 1MB)} |
    Select-Object FullName, 
        @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}},
        LastWriteTime |
    Sort-Object "Size(MB)" -Descending |
    Format-Table -AutoSize

Write-Host "`nSearch completed!" -ForegroundColor Green
```

---

## 2.10 课后练习

### 练习1: 命令探索

1. 使用`Get-Command`查找所有以"Set"开头的命令
2. 使用`Get-Help`查看`Get-Service`的帮助和示例
3. 找出`Get-ChildItem`的所有别名

### 练习2: 管道练习

编写命令完成以下任务:
1. 列出C盘根目录的所有文件夹
2. 按大小排序显示当前目录的文件
3. 查找所有.txt文件并统计数量

### 练习3: 格式化输出

使用不同的Format命令显示进程信息:
1. 用Format-Table显示进程名和CPU
2. 用Format-List显示单个进程的详细信息
3. 用Out-GridView以图形界面显示所有进程

---

## 2.11 本章小结

### 核心概念

✅ **Cmdlet**: Verb-Noun命名规范

✅ **Get-Help**: 获取命令帮助

✅ **别名**: 命令快捷方式

✅ **管道**: 对象传递,不是文本

✅ **格式化**: Format-*, Select-Object, Out-*

### 常用命令

```powershell
# 帮助和发现
Get-Help <command>
Get-Command <pattern>
Get-Member

# 别名
Get-Alias
Set-Alias

# 管道和格式化
<command> | Where-Object {condition}
<command> | Select-Object properties
<command> | Format-Table
<command> | Out-File
```

### 下一章预告

**第3章 - 变量与数据类型**,将学习:
- 📦 变量定义和使用
- 🔢 数据类型
- 📋 数组和哈希表
- 🔄 类型转换

---

[← 上一章](./1-PowerShell环境安装与配置.md) | [返回目录](./README.md) | [下一章: 变量与数据类型 →](./3-变量与数据类型.md)
