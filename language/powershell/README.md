# PowerShell 学习笔记

## 概述

PowerShell是微软开发的跨平台任务自动化和配置管理框架，包括命令行shell和脚本语言。它基于.NET框架，提供了强大的管理Windows系统和其他平台的能力。PowerShell结合了命令行的灵活性和脚本编程的强大功能，是系统管理员和DevOps工程师的重要工具。

## 目录结构

```
powershell/
├── basics/                 # PowerShell基础
│   ├── introduction.md    # PowerShell介绍
│   ├── installation.md    # 安装和配置
│   ├── console.md         # 控制台基础
│   ├── commands.md        # 基本命令
│   └── help-system.md     # 帮助系统
├── syntax/                 # 语法基础
│   ├── variables.md       # 变量
│   ├── operators.md       # 运算符
│   ├── data-types.md      # 数据类型
│   ├── arrays.md          # 数组
│   ├── hash-tables.md     # 哈希表
│   └── objects.md         # 对象
├── flow-control/           # 流程控制
│   ├── conditional.md     # 条件语句
│   ├── loops.md           # 循环
│   ├── switch.md          # Switch语句
│   └── error-handling.md  # 错误处理
├── functions/              # 函数
│   ├── function-basics.md # 函数基础
│   ├── parameters.md      # 参数
│   ├── output.md          # 输出处理
│   ├── scope.md           # 作用域
│   └── advanced.md        # 高级函数
├── modules/                # 模块
│   ├── module-basics.md   # 模块基础
│   ├── creating-modules.md # 创建模块
│   ├── importing.md       # 导入模块
│   └── publishing.md      # 发布模块
├── scripts/                # 脚本
│   ├── script-basics.md   # 脚本基础
│   ├── parameters.md      # 脚本参数
│   ├── execution-policy.md # 执行策略
│   └── profiling.md       # 性能分析
├── files-and-folders/      # 文件和文件夹操作
│   ├── navigation.md      # 导航
│   ├── reading-writing.md # 读写操作
│   ├── permissions.md     # 权限管理
│   └── compression.md     # 压缩和解压
├── registry/               # 注册表操作
│   ├── registry-basics.md # 注册表基础
│   ├── reading.md         # 读取注册表
│   ├── writing.md         # 写入注册表
│   └── backup-restore.md  # 备份和恢复
├── wmi-cim/                # WMI和CIM
│   ├── wmi-basics.md      # WMI基础
│   ├── cim-basics.md      # CIM基础
│   ├── querying.md        # 查询
│   └── classes.md         # 类和方法
├── active-directory/       # Active Directory
│   ├── ad-basics.md       # AD基础
│   ├── users-groups.md    # 用户和组
│   ├── computers.md       # 计算机
│   └── gpo.md             # 组策略
├── exchange/               # Exchange管理
│   ├── exchange-basics.md # Exchange基础
│   ├── mailboxes.md       # 邮箱管理
│   ├── transport.md       # 传输规则
│   └── databases.md       # 数据库管理
├── sharepoint/             # SharePoint管理
│   ├── sp-basics.md       # SharePoint基础
│   ├── sites.md           # 站点管理
│   ├── lists.md           # 列表管理
│   └── permissions.md     # 权限管理
├── azure/                  # Azure管理
│   ├── az-basics.md       # Azure基础
│   ├── modules.md         # Azure模块
│   ├── resources.md       # 资源管理
│   └── automation.md      # 自动化
├── security/               # 安全
│   ├── security-basics.md # 安全基础
│   ├── certificates.md    # 证书管理
│   ├── encryption.md      # 加密
│   └── auditing.md        # 审计
├── remoting/               # 远程管理
│   ├── remoting-basics.md # 远程管理基础
│   ├── sessions.md        # 会话管理
│   ├── jobs.md            # 后台作业
│   └── ssl.md             # SSL配置
├── dsc/                    # 期望状态配置
│   ├── dsc-basics.md      # DSC基础
│   ├── resources.md       # 资源
│   ├── configurations.md  # 配置
│   └── pull-server.md     # 拉取服务器
├── gui/                    # GUI开发
│   ├── winforms.md        # Windows Forms
│   ├── wpf.md             # WPF
│   ├── dialogs.md         # 对话框
│   └── controls.md        # 控件
├── testing/                # 测试
│   ├── pester.md          # Pester测试框架
│   ├── unit-tests.md      # 单元测试
│   ├── integration.md     # 集成测试
│   └── ci-cd.md           # CI/CD集成
├── performance/            # 性能优化
│   ├── profiling.md       # 性能分析
│   ├── optimization.md    # 优化技巧
│   ├── memory.md          # 内存管理
│   └── threading.md       # 多线程
├── logging/                # 日志记录
│   ├── logging-basics.md  # 日志基础
│   ├── event-log.md       # 事件日志
│   ├── file-log.md        # 文件日志
│   └── centralized.md     # 集中化日志
└── advanced/               # 高级主题
    ├── classes.md         # PowerShell类
    ├── enums.md          # 枚举
    ├── reflection.md      # 反射
    ├── interop.md        # 互操作
    └── cross-platform.md # 跨平台
```

## 学习路径

### 初学者路径
1. **PowerShell基础** - 了解PowerShell的安装、基本概念和命令
2. **语法基础** - 学习变量、数据类型、运算符等基本语法
3. **流程控制** - 掌握条件语句和循环
4. **函数和脚本** - 学习如何编写函数和脚本
5. **文件和文件夹操作** - 掌握基本的文件系统操作

### 进阶路径
1. **模块管理** - 学习如何使用和创建PowerShell模块
2. **错误处理** - 掌握PowerShell的错误处理机制
3. **对象和管道** - 深入理解PowerShell的对象模型和管道
4. **远程管理** - 学习PowerShell的远程管理功能
5. **WMI和CIM** - 掌握使用WMI和CIM管理Windows系统

### 高级路径
1. **Active Directory管理** - 学习使用PowerShell管理AD
2. **期望状态配置(DSC)** - 掌握PowerShell DSC的使用
3. **GUI开发** - 学习使用PowerShell创建图形界面
4. **测试和调试** - 掌握PowerShell的测试和调试技巧
5. **跨平台和云管理** - 学习PowerShell在Linux和Azure中的应用

## 常见问题

### Q: PowerShell和CMD有什么区别？
A: PowerShell和CMD的主要区别：
- PowerShell基于对象，CMD基于文本
- PowerShell功能更强大，支持复杂的脚本和编程
- PowerShell有丰富的命令集(Cmdlet)，CMD命令较少
- PowerShell支持.NET框架集成，CMD不支持
- PowerShell有管道功能，CMD的管道功能有限
- PowerShell跨平台，CMD仅限Windows

### Q: 如何设置PowerShell的执行策略？
A: PowerShell执行策略的设置方法：
- 查看当前执行策略：`Get-ExecutionPolicy`
- 设置执行策略：`Set-ExecutionPolicy <策略名称>`
- 常见策略：Restricted(默认)、AllSigned、RemoteSigned、Unrestricted
- 可以针对不同作用域设置：Process、CurrentUser、LocalMachine
- 策略优先级：Process > CurrentUser > LocalMachine

### Q: PowerShell中的管道是什么？
A: PowerShell管道是一种将命令输出作为另一个命令输入的机制：
- 使用管道符`|`连接命令
- 管道传递的是.NET对象，不是纯文本
- 支持对象属性的自动访问
- 可以使用`Select-Object`选择特定属性
- 可以使用`Where-Object`过滤对象
- 支持管道参数绑定

## 资源链接

- [Microsoft PowerShell文档](https://docs.microsoft.com/zh-cn/powershell/)
- [PowerShell Gallery](https://www.powershellgallery.com/)
- [PowerShell GitHub仓库](https://github.com/PowerShell/PowerShell)
- [PowerShell 博客](https://devblogs.microsoft.com/powershell/)
- [PowerShell Magazine](https://www.powershellmagazine.com/)

## 代码示例

### 基本语法

```powershell
# 注释
# 这是单行注释
<#
这是多行注释
可以跨越多行
#>

# 变量
$name = "John"  # 字符串
$age = 30       # 整数
$price = 19.99  # 浮点数
$isAvailable = $true  # 布尔值
$nullValue = $null     # 空值

# 使用变量
Write-Host "Name: $name, Age: $age"

# 强类型变量
[int]$number = 42
[string]$text = "Hello"
[datetime]$date = Get-Date

# 数组
$simpleArray = 1, 2, 3, 4, 5
$anotherArray = @("Apple", "Banana", "Orange")
$emptyArray = @()

# 访问数组元素
Write-Host $simpleArray[0]  # 输出: 1
Write-Host $anotherArray[1] # 输出: Banana

# 数组操作
$anotherArray += "Grape"  # 添加元素
$anotherArray = $anotherArray[0..1] + $anotherArray[3..4]  # 删除元素

# 哈希表
$person = @{
    Name = "Alice"
    Age = 30
    City = "New York"
}

# 访问哈希表元素
Write-Host $person.Name  # 输出: Alice
Write-Host $person["Age"] # 输出: 30

# 哈希表操作
$person.Email = "alice@example.com"  # 添加元素
$person.Remove("City")  # 删除元素
```

### 运算符

```powershell
# 算术运算符
$a = 10
$b = 3

$sum = $a + $b        # 加法: 13
$diff = $a - $b       # 减法: 7
$product = $a * $b    # 乘法: 30
$quotient = $a / $b   # 除法: 3.333...
$remainder = $a % $b   # 取余: 1

# 比较运算符
$eqResult = $a -eq $b    # 等于: False
$neResult = $a -ne $b    # 不等于: True
$gtResult = $a -gt $b    # 大于: True
$geResult = $a -ge $b    # 大于等于: True
$ltResult = $a -lt $b    # 小于: False
$leResult = $a -le $b    # 小于等于: False

# 字符串比较运算符
$str1 = "PowerShell"
$str2 = "powershell"

$ceqResult = $str1 -ceq $str2  # 区分大小写等于: False
$ieqResult = $str1 -ieq $str2  # 不区分大小写等于: True
$likeResult = $str1 -like "*Shell"  # 通配符匹配: True
$matchResult = $str1 -match "Power" # 正则表达式匹配: True

# 逻辑运算符
$x = $true
$y = $false

$andResult = $x -and $y  # 逻辑与: False
$orResult = $x -or $y    # 逻辑或: True
$notResult = -not $x     # 逻辑非: False
$xorResult = $x -xor $y  # 逻辑异或: True

# 赋值运算符
$num = 10
$num += 5    # 加法赋值: 15
$num -= 3    # 减法赋值: 12
$num *= 2    # 乘法赋值: 24
$num /= 4    # 除法赋值: 6
$num %= 4    # 取余赋值: 2

# 其他运算符
$range = 1..5           # 范围运算符: 1, 2, 3, 4, 5
$format = "{0} + {1} = {2}" -f 5, 3, 8  # 格式运算符
$join = "a", "b", "c" -join ","         # 连接运算符: "a,b,c"
$split = "a,b,c" -split ","             # 分割运算符: "a", "b", "c"
```

### 流程控制

```powershell
# If-Else语句
$age = 25

if ($age -lt 18) {
    Write-Host "未成年人"
}
elseif ($age -lt 60) {
    Write-Host "成年人"
}
else {
    Write-Host "老年人"
}

# Switch语句
$day = "Monday"

switch ($day) {
    "Monday" { Write-Host "星期一" }
    "Tuesday" { Write-Host "星期二" }
    "Wednesday" { Write-Host "星期三" }
    "Thursday" { Write-Host "星期四" }
    "Friday" { Write-Host "星期五" }
    default { Write-Host "周末" }
}

# Switch语句与通配符
$file = "document.txt"

switch -Wildcard ($file) {
    "*.txt" { Write-Host "文本文件" }
    "*.jpg" { Write-Host "图片文件" }
    "*.mp3" { Write-Host "音频文件" }
    default { Write-Host "未知文件类型" }
}

# For循环
for ($i = 1; $i -le 5; $i++) {
    Write-Host "计数: $i"
}

# ForEach循环
$fruits = "Apple", "Banana", "Orange"

foreach ($fruit in $fruits) {
    Write-Host "水果: $fruit"
}

# ForEach-Object (管道)
1..5 | ForEach-Object {
    Write-Host "数字: $_"
}

# While循环
$count = 0
while ($count -lt 5) {
    Write-Host "计数: $count"
    $count++
}

# Do-While循环
$count = 0
do {
    Write-Host "计数: $count"
    $count++
} while ($count -lt 5)

# Do-Until循环
$count = 0
do {
    Write-Host "计数: $count"
    $count++
} until ($count -ge 5)

# Break和Continue
for ($i = 1; $i -le 10; $i++) {
    if ($i -eq 5) {
        continue  # 跳过5
    }
    
    if ($i -eq 8) {
        break     # 在8处停止
    }
    
    Write-Host $i
}
# 输出: 1, 2, 3, 4, 6, 7
```

### 函数

```powershell
# 基本函数
function Say-Hello {
    Write-Host "Hello, World!"
}

Say-Hello

# 带参数的函数
function Greet-Person {
    param(
        [string]$Name,
        [int]$Age
    )
    
    Write-Host "Hello, $Name! You are $Age years old."
}

Greet-Person -Name "Alice" -Age 30

# 参数类型和验证
function Add-Numbers {
    param(
        [Parameter(Mandatory=$true)]
        [int]$Number1,
        
        [Parameter(Mandatory=$true)]
        [int]$Number2,
        
        [ValidateSet("Add", "Subtract", "Multiply", "Divide")]
        [string]$Operation = "Add"
    )
    
    switch ($Operation) {
        "Add" { return $Number1 + $Number2 }
        "Subtract" { return $Number1 - $Number2 }
        "Multiply" { return $Number1 * $Number2 }
        "Divide" { 
            if ($Number2 -eq 0) {
                throw "Cannot divide by zero."
            }
            return $Number1 / $Number2 
        }
    }
}

$result = Add-Numbers -Number1 10 -Number2 5 -Operation "Multiply"
Write-Host "Result: $result"

# 管道输入
function Get-FileStats {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline=$true)]
        [System.IO.FileInfo]$File
    )
    
    process {
        $stats = Get-ItemProperty $File.FullName
        [PSCustomObject]@{
            Name = $stats.Name
            Size = $stats.Length
            LastModified = $stats.LastWriteTime
        }
    }
}

# 使用管道
Get-ChildItem *.txt | Get-FileStats

# 返回多个值
function Get-SystemInfo {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem
    $cs = Get-CimInstance -ClassName Win32_ComputerSystem
    
    return @{
        OS = $os.Caption
        Version = $os.Version
        ComputerName = $cs.Name
        TotalMemory = $cs.TotalPhysicalMemory
    }
}

$info = Get-SystemInfo
Write-Host "OS: $($info.OS)"
Write-Host "Computer: $($info.ComputerName)"

# 高级函数
function Get-AdvancedProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false, Position=0)]
        [string]$Name = "*",
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("Running", "Stopped", "All")]
        [string]$Status = "All",
        
        [Parameter(Mandatory=$false)]
        [switch]$IncludeMemory
    )
    
    begin {
        Write-Verbose "开始获取进程信息"
        $processes = @()
    }
    
    process {
        Write-Verbose "处理进程名称: $Name"
        
        switch ($Status) {
            "Running" { $filter = { $_.ProcessName -like $Name -and $_.Responding } }
            "Stopped" { $filter = { $_.ProcessName -like $Name -and -not $_.Responding } }
            "All" { $filter = { $_.ProcessName -like $Name } }
        }
        
        $matchingProcesses = Get-Process | Where-Object $filter
        
        foreach ($process in $matchingProcesses) {
            $processInfo = [PSCustomObject]@{
                Name = $process.ProcessName
                ID = $process.Id
                Status = if ($process.Responding) { "Running" } else { "Stopped" }
            }
            
            if ($IncludeMemory) {
                $processInfo | Add-Member -NotePropertyName "Memory(MB)" -NotePropertyValue ([math]::Round($process.WorkingSet64 / 1MB, 2))
            }
            
            $processes += $processInfo
        }
    }
    
    end {
        Write-Verbose "完成获取进程信息"
        return $processes
    }
}

# 使用高级函数
Get-AdvancedProcess -Name "powershell" -Status "Running" -IncludeMemory -Verbose
```

### 文件和文件夹操作

```powershell
# 获取当前目录
$currentDir = Get-Location
Write-Host "当前目录: $currentDir"

# 列出目录内容
Get-ChildItem  # 当前目录
Get-ChildItem C:\Windows  # 指定目录
Get-ChildItem -Path C:\Windows -Filter "*.exe"  # 过滤文件
Get-ChildItem -Path C:\Windows -Recurse  # 递归列出

# 创建目录
New-Item -Path "C:\Temp\NewFolder" -ItemType Directory
mkdir "C:\Temp\AnotherFolder"  # 简写

# 创建文件
New-Item -Path "C:\Temp\test.txt" -ItemType File -Value "Hello, PowerShell!"

# 读取文件内容
$content = Get-Content "C:\Temp\test.txt"
Write-Host $content

# 读取文件所有内容作为单个字符串
$contentAll = Get-Content "C:\Temp\test.txt" -Raw

# 逐行读取文件
Get-Content "C:\Temp\test.txt" | ForEach-Object {
    Write-Host "行: $_"
}

# 写入文件
Set-Content -Path "C:\Temp\output.txt" -Value "这是新内容"
"这是另一行内容" | Set-Content "C:\Temp\output.txt"

# 添加内容到文件
Add-Content -Path "C:\Temp\output.txt" -Value "这是追加的内容"

# 复制文件或目录
Copy-Item -Path "C:\Temp\test.txt" -Destination "C:\Temp\backup\test.txt"
Copy-Item -Path "C:\Temp\NewFolder" -Destination "C:\Temp\backup\" -Recurse

# 移动文件或目录
Move-Item -Path "C:\Temp\test.txt" -Destination "C:\Temp\moved\test.txt"

# 重命名文件或目录
Rename-Item -Path "C:\Temp\test.txt" -NewName "renamed.txt"

# 删除文件或目录
Remove-Item -Path "C:\Temp\test.txt"
Remove-Item -Path "C:\Temp\NewFolder" -Recurse -Force  # 递归删除目录

# 检查文件或目录是否存在
$fileExists = Test-Path "C:\Temp\test.txt"
if ($fileExists) {
    Write-Host "文件存在"
} else {
    Write-Host "文件不存在"
}

# 获取文件属性
$fileInfo = Get-Item "C:\Temp\test.txt"
Write-Host "文件大小: $($fileInfo.Length) 字节"
Write-Host "创建时间: $($fileInfo.CreationTime)"
Write-Host "修改时间: $($fileInfo.LastWriteTime)"

# 设置文件属性
$fileInfo.IsReadOnly = $true  # 设置为只读

# 查找文件
$files = Get-ChildItem -Path C:\ -Recurse -Filter "*.log" -ErrorAction SilentlyContinue
Write-Host "找到 $($files.Count) 个日志文件"

# 计算目录大小
$directorySize = (Get-ChildItem -Path C:\Temp -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "目录大小: $([math]::Round($directorySize / 1MB, 2)) MB"

# 压缩文件
Compress-Archive -Path "C:\Temp\NewFolder" -DestinationPath "C:\Temp\NewFolder.zip"

# 解压文件
Expand-Archive -Path "C:\Temp\NewFolder.zip" -DestinationPath "C:\Temp\Extracted"
```

### 注册表操作

```powershell
# 列出注册表项
Get-ChildItem -Path "HKLM:\SOFTWARE"
Get-ChildItem -Path "HKCU:\Software"

# 获取注册表项的属性
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"

# 获取特定的注册表值
$version = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" -Name "CurrentVersion"
Write-Host "Windows版本: $($version.CurrentVersion)"

# 创建新的注册表项
New-Item -Path "HKCU:\Software\MyApp"

# 创建或设置注册表值
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Version" -Value "1.0" -PropertyType String
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "InstallDate" -Value (Get-Date) -PropertyType String
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "MaxUsers" -Value 100 -PropertyType DWord
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Enabled" -Value 1 -PropertyType Binary

# 修改注册表值
Set-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Version" -Value "1.1"

# 删除注册表值
Remove-ItemProperty -Path "HKCU:\Software\MyApp" -Name "MaxUsers"

# 删除注册表项
Remove-Item -Path "HKCU:\Software\MyApp" -Recurse

# 检查注册表项是否存在
$keyExists = Test-Path "HKCU:\Software\MyApp"
if ($keyExists) {
    Write-Host "注册表项存在"
} else {
    Write-Host "注册表项不存在"
}

# 搜索注册表
$foundItems = Get-ChildItem -Path "HKLM:\SOFTWARE" -Recurse -ErrorAction SilentlyContinue | 
              Where-Object { $_.Property -contains "DisplayName" }

foreach ($item in $foundItems) {
    $properties = Get-ItemProperty -Path $item.PSPath
    if ($properties.DisplayName) {
        Write-Host "找到应用程序: $($properties.DisplayName)"
    }
}

# 备份注册表项
$backupPath = "C:\Temp\RegistryBackup.reg"
reg export "HKCU:\Software\MyApp" $backupPath

# 恢复注册表项
reg import $backupPath

# 处理远程计算机的注册表
$remoteComputer = "Server01"
Invoke-Command -ComputerName $remoteComputer -ScriptBlock {
    Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"
}
```

### WMI和CIM操作

```powershell
# 使用WMI获取系统信息
$osInfo = Get-WmiObject -Class Win32_OperatingSystem
Write-Host "操作系统: $($osInfo.Caption)"
Write-Host "版本: $($osInfo.Version)"
Write-Host "安装日期: $($osInfo.InstallDate)"

# 使用CIM获取系统信息（推荐）
$osInfo = Get-CimInstance -ClassName Win32_OperatingSystem
Write-Host "操作系统: $($osInfo.Caption)"
Write-Host "版本: $($osInfo.Version)"
Write-Host "安装日期: $($osInfo.InstallDate)"

# 获取计算机系统信息
$csInfo = Get-CimInstance -ClassName Win32_ComputerSystem
Write-Host "计算机名: $($csInfo.Name)"
Write-Host "制造商: $($csInfo.Manufacturer)"
Write-Host "型号: $($csInfo.Model)"
Write-Host "总内存: $([math]::Round($csInfo.TotalPhysicalMemory / 1GB, 2)) GB"

# 获取BIOS信息
$biosInfo = Get-CimInstance -ClassName Win32_BIOS
Write-Host "BIOS版本: $($biosInfo.SMBIOSBIOSVersion)"
Write-Host "发布日期: $($biosInfo.ReleaseDate)"

# 获取处理器信息
$cpuInfo = Get-CimInstance -ClassName Win32_Processor
Write-Host "处理器: $($cpuInfo.Name)"
Write-Host "核心数: $($cpuInfo.NumberOfCores)"
Write-Host "逻辑处理器: $($cpuInfo.NumberOfLogicalProcessors)"

# 获取磁盘信息
$diskInfo = Get-CimInstance -ClassName Win32_LogicalDisk
foreach ($disk in $diskInfo) {
    $size = [math]::Round($disk.Size / 1GB, 2)
    $freeSpace = [math]::Round($disk.FreeSpace / 1GB, 2)
    $usedSpace = $size - $freeSpace
    $usedPercent = [math]::Round(($usedSpace / $size) * 100, 2)
    
    Write-Host "驱动器 $($disk.DeviceID): 大小 $size GB, 已用 $usedPercent%, 剩余 $freeSpace GB"
}

# 获取服务信息
$services = Get-CimInstance -ClassName Win32_Service | Where-Object { $_.State -eq "Running" }
Write-Host "正在运行的服务数量: $($services.Count)"

# 获取进程信息
$processes = Get-CimInstance -ClassName Win32_Process | Sort-Object -Property WorkingSetSize -Descending | Select-Object -First 10
foreach ($process in $processes) {
    $memory = [math]::Round($process.WorkingSetSize / 1MB, 2)
    Write-Host "进程: $($process.Name), 内存使用: $memory MB"
}

# 使用WQL查询
$wqlQuery = "SELECT * FROM Win32_Service WHERE State='Running' AND StartMode='Auto'"
$autoServices = Get-CimInstance -Query $wqlQuery
Write-Host "自动启动的服务数量: $($autoServices.Count)"

# 使用Filter参数
$runningServices = Get-CimInstance -ClassName Win32_Service -Filter "State='Running'"
Write-Host "正在运行的服务数量: $($runningServices.Count)"

# 调用WMI方法
$notepad = Get-CimInstance -ClassName Win32_Process -Filter "Name='notepad.exe'"
if ($notepad) {
    $result = Invoke-CimMethod -InputObject $notepad -MethodName Terminate
    Write-Host "记事本进程已终止，返回值: $($result.ReturnValue)"
}

# 创建新进程
$newProcess = New-CimInstance -ClassName Win32_Process -Property @{
    CommandLine = "notepad.exe"
} -ClientOnly
$result = Invoke-CimMethod -InputObject $newProcess -MethodName Create
Write-Host "新进程ID: $($result.ProcessId)"

# 远程计算机上的WMI操作
$remoteComputer = "Server01"
$remoteOS = Get-CimInstance -ClassName Win32_OperatingSystem -ComputerName $remoteComputer
Write-Host "远程计算机操作系统: $($remoteOS.Caption)"

# 使用CIM会话进行远程操作
$cimSession = New-CimSession -ComputerName $remoteComputer
$remoteServices = Get-CimInstance -ClassName Win32_Service -CimSession $cimSession
Write-Host "远程计算机服务数量: $($remoteServices.Count)"
Remove-CimSession -CimSession $cimSession
```

### Active Directory管理

```powershell
# 导入Active Directory模块
Import-Module ActiveDirectory

# 获取域信息
$domain = Get-ADDomain
Write-Host "域名称: $($domain.DNSRoot)"
Write-Host "域控制器: $($domain.ReplicaDirectoryServers)"

# 获取域控制器信息
$domainControllers = Get-ADDomainController
foreach ($dc in $domainControllers) {
    Write-Host "域控制器: $($dc.Name), 操作系统: $($dc.OperatingSystem)"
}

# 获取用户信息
$user = Get-ADUser -Identity "jsmith" -Properties *
Write-Host "用户名: $($user.Name)"
Write-Host "电子邮件: $($user.EmailAddress)"
Write-Host "部门: $($user.Department)"
Write-Host "创建日期: $($user.whenCreated)"

# 搜索用户
$users = Get-ADUser -Filter "Department -eq 'IT'" -Properties Department, Title
foreach ($user in $users) {
    Write-Host "用户: $($user.Name), 部门: $($user.Department), 职位: $($user.Title)"
}

# 创建新用户
$newUser = New-ADUser -Name "张三" -GivenName "三" -Surname "张" `
    -SamAccountName "zhangsan" -UserPrincipalName "zhangsan@contoso.com" `
    -Path "OU=Users,OU=IT,DC=contoso,DC=com" `
    -AccountPassword (ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force) `
    -Enabled $true -PassThru

Write-Host "新用户已创建: $($newUser.Name)"

# 修改用户属性
Set-ADUser -Identity "zhangsan" -Department "IT" -Title "系统管理员" `
    -Office "北京" -EmailAddress "zhangsan@contoso.com"

# 禁用用户账户
Disable-ADAccount -Identity "zhangsan"

# 启用用户账户
Enable-ADAccount -Identity "zhangsan"

# 重置用户密码
Set-ADAccountPassword -Identity "zhangsan" -Reset -NewPassword (ConvertTo-SecureString "NewP@ssw0rd" -AsPlainText -Force)

# 获取组信息
$group = Get-ADGroup -Identity "IT Department"
Write-Host "组名: $($group.Name)"
Write-Host "组成员数量: $($group.Member.Count)"

# 创建新组
New-ADGroup -Name "新项目组" -SamAccountName "NewProjectTeam" -GroupScope Global `
    -GroupCategory Security -Path "OU=Groups,OU=IT,DC=contoso,DC=com"

# 将用户添加到组
Add-ADGroupMember -Identity "IT Department" -Members "zhangsan"

# 从组中移除用户
Remove-ADGroupMember -Identity "IT Department" -Members "zhangsan" -Confirm:$false

# 获取计算机信息
$computer = Get-ADComputer -Identity "PC01" -Properties *
Write-Host "计算机名: $($computer.Name)"
Write-Host "操作系统: $($computer.OperatingSystem)"
Write-Host "最后登录时间: $($computer.lastLogonDate)"

# 搜索计算机
$computers = Get-ADComputer -Filter "OperatingSystem -like '*Windows 10*'" -Properties OperatingSystem, LastLogonDate
foreach ($computer in $computers) {
    Write-Host "计算机: $($computer.Name), 操作系统: $($computer.OperatingSystem), 最后登录: $($computer.LastLogonDate)"
}

# 获取组织单位信息
$ous = Get-ADOrganizationalUnit -Filter * -Properties *
foreach ($ou in $ous) {
    Write-Host "OU: $($ou.Name), 路径: $($ou.DistinguishedName)"
}

# 创建组织单位
New-ADOrganizationalUnit -Name "新部门" -Path "DC=contoso,DC=com" -ProtectedFromAccidentalDeletion $false

# 获取用户组成员
$groupMembers = Get-ADGroupMember -Identity "IT Department"
foreach ($member in $groupMembers) {
    Write-Host "成员: $($member.Name), 类型: $($member.ObjectClass)"
}

# 查找过期账户
$expiredAccounts = Search-ADAccount -AccountExpired -UsersOnly
foreach ($account in $expiredAccounts) {
    Write-Host "过期账户: $($account.Name), 过期时间: $($account.AccountExpirationDate)"
}

# 查找禁用账户
$disabledAccounts = Search-ADAccount -AccountDisabled -UsersOnly
foreach ($account in $disabledAccounts) {
    Write-Host "禁用账户: $($account.Name)"
}

# 查找长时间未登录的账户
$staleAccounts = Search-ADAccount -AccountInactive -TimeSpan 90.00:00:00 -UsersOnly
foreach ($account in $staleAccounts) {
    Write-Host "非活动账户: $($account.Name), 最后登录: $($account.LastLogonDate)"
}

# 导出用户信息到CSV
Get-ADUser -Filter * -Properties Department, Title, EmailAddress | 
    Select-Object Name, SamAccountName, Department, Title, EmailAddress | 
    Export-Csv -Path "C:\Temp\ADUsers.csv" -NoTypeInformation

# 从CSV导入用户信息
$users = Import-Csv -Path "C:\Temp\NewUsers.csv"
foreach ($user in $users) {
    $password = ConvertTo-SecureString $user.Password -AsPlainText -Force
    New-ADUser -Name $user.Name -GivenName $user.FirstName -Surname $user.LastName `
        -SamAccountName $user.SamAccountName -UserPrincipalName $user.UserPrincipalName `
        -Department $user.Department -Title $user.Title `
        -AccountPassword $password -Enabled $true
}
```

### 错误处理

```powershell
# 使用Try-Catch处理错误
try {
    # 可能出错的代码
    $result = 1 / 0
}
catch {
    # 处理错误
    Write-Host "发生错误: $($_.Exception.Message)"
}
finally {
    # 无论是否出错都会执行的代码
    Write-Host "操作完成"
}

# 捕获特定类型的错误
try {
    Get-Content "C:\NonExistentFile.txt"
}
catch [System.Management.Automation.ItemNotFoundException] {
    Write-Host "文件未找到"
}
catch {
    Write-Host "其他错误: $($_.Exception.GetType().FullName)"
}

# 使用ErrorAction参数控制错误处理
# ErrorAction的值: Continue (默认), Stop, SilentlyContinue, Inquire, Ignore

# Stop: 将错误转换为终止错误，可以被Try-Catch捕获
try {
    Get-ChildItem "C:\NonExistentFolder" -ErrorAction Stop
}
catch {
    Write-Host "捕获到错误: $($_.Exception.Message)"
}

# SilentlyContinue: 静默忽略错误
Get-ChildItem "C:\NonExistentFolder" -ErrorAction SilentlyContinue
Write-Host "即使出错也会继续执行"

# Inquire: 询问用户如何处理错误
# Get-ChildItem "C:\NonExistentFolder" -ErrorAction Inquire

# Ignore: 完全忽略错误，不添加到$Error变量
Get-ChildItem "C:\NonExistentFolder" -ErrorAction Ignore

# 使用$Error变量查看错误历史
Write-Host "最近的错误数量: $($Error.Count)"
if ($Error.Count -gt 0) {
    Write-Host "最近的错误: $($Error[0].Exception.Message)"
}

# 清除错误历史
$Error.Clear()

# 使用$?检查上一个命令是否成功
Get-Process "NonExistentProcess" -ErrorAction SilentlyContinue
if ($?) {
    Write-Host "命令执行成功"
} else {
    Write-Host "命令执行失败"
}

# 使用$LastExitCode检查外部程序的退出代码
cmd /c "exit 1"
if ($LastExitCode -eq 0) {
    Write-Host "外部程序执行成功"
} else {
    Write-Host "外部程序执行失败，退出代码: $LastExitCode"
}

# 抛出自定义错误
function Divide-Numbers {
    param(
        [int]$Dividend,
        [int]$Divisor
    )
    
    if ($Divisor -eq 0) {
        throw "除数不能为零"
    }
    
    return $Dividend / $Divisor
}

try {
    $result = Divide-Numbers -Dividend 10 -Divisor 0
}
catch {
    Write-Host "自定义错误: $($_.Exception.Message)"
}

# 使用Write-Error写入非终止错误
function Test-File {
    param(
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "文件不存在: $Path"
        return
    }
    
    Write-Host "文件存在: $Path"
}

Test-File "C:\NonExistentFile.txt"
Write-Host "即使出错也会继续执行"

# 使用Trap处理错误
function Test-Trap {
    trap {
        Write-Host "捕获到错误: $($_.Exception.Message)"
        continue  # 继续执行
    }
    
    Write-Host "开始执行"
    Get-Content "C:\NonExistentFile.txt"
    Write-Host "结束执行"
}

Test-Trap

# 使用Throw终止执行
function Test-Throw {
    Write-Host "开始执行"
    throw "手动抛出错误"
    Write-Host "这行不会执行"
}

try {
    Test-Throw
}
catch {
    Write-Host "捕获到错误: $($_.Exception.Message)"
}
```

## 最佳实践

1. **脚本编写**
   - 使用一致的命名约定和代码风格
   - 添加适当的注释和文档
   - 使用参数验证确保输入安全
   - 实现错误处理机制

2. **性能优化**
   - 使用管道处理大量数据
   - 避免不必要的循环和嵌套
   - 使用Filter函数而不是函数处理管道
   - 限制返回的属性数量

3. **安全考虑**
   - 遵循最小权限原则
   - 安全处理敏感信息
   - 使用参数化命令防止注入攻击
   - 实施适当的执行策略

4. **可维护性**
   - 将复杂脚本分解为模块和函数
   - 使用版本控制系统管理脚本
   - 编写单元测试验证功能
   - 保持代码简洁和可读性

5. **跨平台兼容**
   - 使用跨平台的PowerShell命令
   - 避免使用特定于Windows的功能
   - 测试脚本在不同平台上的表现
   - 使用条件语句处理平台差异

## 贡献指南

欢迎对本学习笔记进行贡献！请遵循以下指南：

1. 确保内容准确、清晰、实用
2. 使用规范的Markdown格式
3. 代码示例需要完整且可运行
4. 添加适当的注释和说明
5. 保持目录结构的一致性

## 注意事项

- PowerShell版本差异可能导致某些功能不可用
- 执行策略可能限制脚本的运行
- 远程管理需要适当的权限配置
- Active Directory操作需要相应的权限
- 跨平台使用时注意命令和功能的兼容性

---

*最后更新: 2023年*