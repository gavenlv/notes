# 第1章：PowerShell环境安装与配置

> **学习时长**: 3-4小时  
> **难度**: ⭐  
> **前置知识**: 无需任何编程经验

## 本章目标

学完本章后,你将能够:

- ✅ 理解什么是PowerShell以及它的用途
- ✅ 区分Windows PowerShell和PowerShell Core
- ✅ 在Windows/Linux/macOS上安装PowerShell
- ✅ 配置PowerShell执行策略
- ✅ 使用Windows Terminal和VS Code
- ✅ 运行你的第一个PowerShell命令

---

## 1.1 什么是PowerShell?

### 1.1.1 PowerShell简介

**PowerShell**是微软开发的**任务自动化和配置管理框架**,它包含:

- 🖥️ **命令行Shell**: 可以执行命令的交互式环境
- 📝 **脚本语言**: 可以编写自动化脚本
- ⚙️ **配置管理**: 管理系统和应用程序
- 🔧 **管理工具**: 访问.NET框架和WMI

**PowerShell的特点**:

| 特点 | 说明 |
|------|------|
| **面向对象** | 处理的是.NET对象,不是纯文本 |
| **一致性** | 命令遵循统一的命名规则 |
| **可扩展** | 可以自定义命令和模块 |
| **跨平台** | PowerShell 7+支持Windows/Linux/macOS |
| **强大** | 可以管理本地和远程系统 |

### 1.1.2 PowerShell能做什么?

**日常任务**:
```powershell
# 查看系统信息
Get-ComputerInfo

# 管理进程
Get-Process | Where-Object {$_.CPU -gt 100}

# 批量重命名文件
Get-ChildItem *.txt | Rename-Item -NewName {$_.Name -replace '.txt','.log'}
```

**系统管理**:
- 用户和组管理
- 服务和进程管理
- 网络配置
- 磁盘和文件系统管理
- 注册表操作

**云服务管理**:
- Azure资源管理
- AWS服务操作
- Office 365管理
- Docker和Kubernetes

**自动化**:
- 定时任务
- 批量部署
- 日志分析
- 系统监控

---

## 1.2 PowerShell版本

### 1.2.1 Windows PowerShell vs PowerShell Core

**两个版本的对比**:

| 特性 | Windows PowerShell | PowerShell (Core) |
|------|-------------------|-------------------|
| **版本** | 5.1 (最终版本) | 7.x (持续更新) |
| **平台** | 仅Windows | Windows/Linux/macOS |
| **基础** | .NET Framework | .NET Core/.NET 6+ |
| **性能** | 较慢 | 更快 |
| **推荐** | ❌ 停止更新 | ✅ 推荐使用 |

**查看PowerShell版本**:

```powershell
# 查看详细版本信息
$PSVersionTable

# 输出示例
Name                           Value
----                           -----
PSVersion                      7.4.0
PSEdition                      Core
GitCommitId                    7.4.0
OS                             Microsoft Windows 10.0.22631
Platform                       Win32NT
PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0…}
PSRemotingProtocolVersion      2.3
SerializationVersion           1.1.0.1
WSManStackVersion              3.0
```

**选择建议**:

- ✅ **新项目**: 使用PowerShell 7+
- ✅ **学习**: 使用PowerShell 7+
- ⚠️ **旧脚本**: 可能需要Windows PowerShell 5.1
- ⚠️ **特定模块**: 某些旧模块仅支持Windows PowerShell

---

## 1.3 Windows上安装PowerShell

### 1.3.1 Windows PowerShell 5.1

Windows 10和Windows 11自带,无需安装。

**验证安装**:

```powershell
# 打开Windows PowerShell
# 方法1: Windows + X,选择"Windows PowerShell"
# 方法2: 搜索"Windows PowerShell"
# 方法3: Win + R,输入"powershell"

# 检查版本
$PSVersionTable.PSVersion
```

### 1.3.2 安装PowerShell 7+

**方法1: 使用Windows包管理器(winget) - 推荐**

```powershell
# 打开PowerShell或命令提示符
winget search Microsoft.PowerShell

# 安装PowerShell 7
winget install --id Microsoft.Powershell --source winget

# 验证安装
pwsh --version
```

**方法2: 下载MSI安装包**

1. 访问 [PowerShell GitHub Releases](https://github.com/PowerShell/PowerShell/releases)
2. 下载最新的`.msi`文件(例如:`PowerShell-7.4.0-win-x64.msi`)
3. 双击运行安装程序
4. 按照向导完成安装

**方法3: 使用Chocolatey**

```powershell
# 如果已安装Chocolatey
choco install powershell-core

# 升级
choco upgrade powershell-core
```

**安装后验证**:

```powershell
# 打开PowerShell 7
# 开始菜单搜索"PowerShell 7"
# 或者在终端输入
pwsh

# 查看版本
$PSVersionTable

# 查看安装路径
$PSHOME
```

---

## 1.4 Linux/macOS上安装PowerShell

### 1.4.1 Ubuntu/Debian

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y wget apt-transport-https software-properties-common

# 下载Microsoft仓库GPG密钥
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"

# 注册仓库
sudo dpkg -i packages-microsoft-prod.deb

# 更新包索引
sudo apt-get update

# 安装PowerShell
sudo apt-get install -y powershell

# 启动PowerShell
pwsh
```

### 1.4.2 macOS

**使用Homebrew**:

```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装PowerShell
brew install --cask powershell

# 启动PowerShell
pwsh
```

### 1.4.3 CentOS/RHEL

```bash
# 注册仓库
curl https://packages.microsoft.com/config/rhel/7/prod.repo | sudo tee /etc/yum.repos.d/microsoft.repo

# 安装PowerShell
sudo yum install -y powershell

# 启动
pwsh
```

---

## 1.5 配置PowerShell环境

### 1.5.1 执行策略

**什么是执行策略?**

执行策略是一种安全功能,决定PowerShell可以运行哪些脚本。

**执行策略级别**:

| 策略 | 说明 |
|------|------|
| **Restricted** | 默认,不允许运行任何脚本 |
| **AllSigned** | 只运行受信任发布者签名的脚本 |
| **RemoteSigned** | 本地脚本可运行,下载的脚本需签名(推荐) |
| **Unrestricted** | 运行所有脚本,下载的脚本会警告 |
| **Bypass** | 不阻止任何内容,无警告 |

**查看和设置执行策略**:

```powershell
# 查看当前执行策略
Get-ExecutionPolicy

# 查看所有作用域的执行策略
Get-ExecutionPolicy -List

# 设置执行策略(当前用户) - 推荐
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 设置执行策略(本机所有用户) - 需要管理员权限
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine

# 临时绕过执行策略运行脚本
powershell -ExecutionPolicy Bypass -File script.ps1
```

**实验:创建并运行第一个脚本**

```powershell
# 创建测试脚本
"Write-Host 'Hello, PowerShell!' -ForegroundColor Green" | Out-File test.ps1

# 尝试运行(如果策略是Restricted会失败)
.\test.ps1

# 设置执行策略后再运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\test.ps1

# 清理
Remove-Item test.ps1
```

### 1.5.2 配置文件(Profile)

**什么是Profile?**

Profile是PowerShell启动时自动执行的脚本,用于:
- 设置环境变量
- 加载常用模块
- 定义别名和函数
- 自定义提示符

**Profile类型**:

```powershell
# 查看所有Profile路径
$PROFILE | Get-Member -MemberType NoteProperty

# 当前用户,当前主机
$PROFILE.CurrentUserCurrentHost

# 当前用户,所有主机
$PROFILE.CurrentUserAllHosts

# 所有用户,当前主机
$PROFILE.AllUsersCurrentHost

# 所有用户,所有主机
$PROFILE.AllUsersAllHosts
```

**创建和编辑Profile**:

```powershell
# 检查Profile是否存在
Test-Path $PROFILE

# 如果不存在,创建Profile
if (!(Test-Path $PROFILE)) {
    New-Item -Path $PROFILE -ItemType File -Force
}

# 编辑Profile
notepad $PROFILE

# 或使用VS Code
code $PROFILE
```

**Profile示例内容**:

```powershell
# 欢迎消息
Write-Host "Welcome to PowerShell!" -ForegroundColor Cyan

# 设置别名
Set-Alias -Name ll -Value Get-ChildItem
Set-Alias -Name grep -Value Select-String

# 自定义函数
function Get-MyIP {
    (Invoke-WebRequest -Uri "https://api.ipify.org").Content
}

# 自定义提示符
function prompt {
    $currentPath = Get-Location
    "PS [$currentPath]> "
}

# 导入常用模块
# Import-Module posh-git
```

**重新加载Profile**:

```powershell
# 重新加载当前Profile
. $PROFILE

# 或重启PowerShell
```

---

## 1.6 推荐工具

### 1.6.1 Windows Terminal

**为什么使用Windows Terminal?**

- ✅ 现代化界面
- ✅ 多标签支持
- ✅ 支持多种Shell(PowerShell, CMD, WSL)
- ✅ 自定义配置
- ✅ GPU加速

**安装Windows Terminal**:

```powershell
# 使用winget
winget install Microsoft.WindowsTerminal

# 或从Microsoft Store安装
```

**配置Windows Terminal**:

```json
// 打开设置: Ctrl + ,
// 设置PowerShell 7为默认Shell
{
    "defaultProfile": "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
    "profiles": {
        "list": [
            {
                "guid": "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
                "name": "PowerShell 7",
                "source": "Windows.Terminal.PowershellCore",
                "commandline": "pwsh.exe",
                "colorScheme": "Campbell",
                "fontSize": 12,
                "fontFace": "Cascadia Code"
            }
        ]
    }
}
```

### 1.6.2 Visual Studio Code

**安装VS Code**:

```powershell
# 使用winget
winget install Microsoft.VisualStudioCode

# 或下载安装包
# https://code.visualstudio.com/
```

**安装PowerShell扩展**:

1. 打开VS Code
2. 按`Ctrl + Shift + X`打开扩展面板
3. 搜索"PowerShell"
4. 安装"PowerShell" (Microsoft官方)

**VS Code中运行PowerShell**:

```powershell
# 1. 创建.ps1文件
# 2. 按F5运行
# 3. 或使用集成终端: Ctrl + `
```

**推荐设置**:

```json
// settings.json
{
    "powershell.codeFormatting.preset": "OTBS",
    "powershell.integratedConsole.showOnStartup": false,
    "[powershell]": {
        "editor.formatOnSave": true,
        "editor.tabSize": 4
    }
}
```

---

## 1.7 第一个PowerShell命令

### 1.7.1 Hello World

**在控制台输出**:

```powershell
# 基本输出
Write-Host "Hello, PowerShell!"

# 带颜色输出
Write-Host "Hello, PowerShell!" -ForegroundColor Green

# 带背景色
Write-Host "Hello, PowerShell!" -ForegroundColor White -BackgroundColor Blue
```

**保存为脚本**:

创建文件`hello.ps1`:

```powershell
# hello.ps1
# 显示欢迎消息

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "   Welcome to PowerShell!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# 显示系统信息
Write-Host "`nSystem Information:" -ForegroundColor Yellow
Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Host "OS: $($PSVersionTable.OS)"
Write-Host "Computer Name: $env:COMPUTERNAME"
Write-Host "User: $env:USERNAME"

# 显示当前时间
Write-Host "`nCurrent Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-Host "`nHappy Scripting! 🚀" -ForegroundColor Magenta
```

**运行脚本**:

```powershell
# 方法1: 使用相对路径
.\hello.ps1

# 方法2: 使用绝对路径
C:\path\to\hello.ps1

# 方法3: 在当前会话中执行(点操作符)
. .\hello.ps1
```

### 1.7.2 基础命令

**获取帮助**:

```powershell
# 获取命令帮助
Get-Help Get-Process

# 显示示例
Get-Help Get-Process -Examples

# 详细帮助
Get-Help Get-Process -Detailed

# 完整帮助
Get-Help Get-Process -Full

# 在线帮助
Get-Help Get-Process -Online

# 更新帮助文档
Update-Help
```

**常用命令**:

```powershell
# 查看当前目录
Get-Location  # 或 pwd

# 列出文件
Get-ChildItem  # 或 ls, dir

# 切换目录
Set-Location C:\  # 或 cd C:\

# 创建目录
New-Item -Path "TestFolder" -ItemType Directory  # 或 mkdir TestFolder

# 创建文件
New-Item -Path "test.txt" -ItemType File

# 查看文件内容
Get-Content test.txt  # 或 cat test.txt, type test.txt

# 复制文件
Copy-Item test.txt test_copy.txt  # 或 cp

# 移动文件
Move-Item test.txt moved.txt  # 或 mv

# 删除文件
Remove-Item test_copy.txt  # 或 rm, del

# 查看进程
Get-Process

# 停止进程
Stop-Process -Name notepad

# 查看服务
Get-Service

# 启动/停止服务
Start-Service -Name ServiceName
Stop-Service -Name ServiceName
```

---

## 1.8 实验:环境验证

### 实验1: 验证安装

创建`check-environment.ps1`:

```powershell
<#
.SYNOPSIS
    验证PowerShell环境配置
.DESCRIPTION
    检查PowerShell版本、执行策略、Profile等配置
#>

Write-Host "`n=== PowerShell Environment Check ===" -ForegroundColor Cyan

# 1. PowerShell版本
Write-Host "`n1. PowerShell Version:" -ForegroundColor Yellow
Write-Host "   Version: $($PSVersionTable.PSVersion)"
Write-Host "   Edition: $($PSVersionTable.PSEdition)"
Write-Host "   OS: $($PSVersionTable.OS)"

# 2. 执行策略
Write-Host "`n2. Execution Policy:" -ForegroundColor Yellow
Get-ExecutionPolicy -List | Format-Table

# 3. Profile路径
Write-Host "3. Profile Paths:" -ForegroundColor Yellow
$PROFILE | Get-Member -MemberType NoteProperty | ForEach-Object {
    $name = $_.Name
    $path = $PROFILE.$name
    $exists = Test-Path $path
    Write-Host "   $name`: $path"
    Write-Host "   Exists: $exists"
}

# 4. 安装路径
Write-Host "`n4. Installation Path:" -ForegroundColor Yellow
Write-Host "   `$PSHOME: $PSHOME"

# 5. 环境变量
Write-Host "`n5. Key Environment Variables:" -ForegroundColor Yellow
Write-Host "   HOME: $env:HOME"
Write-Host "   USERPROFILE: $env:USERPROFILE"
Write-Host "   PSModulePath: $($env:PSModulePath -split ';' | Select-Object -First 1)"

# 6. 模块路径
Write-Host "`n6. Module Paths:" -ForegroundColor Yellow
$env:PSModulePath -split ';' | ForEach-Object {
    Write-Host "   - $_"
}

Write-Host "`n=== Check Complete ===" -ForegroundColor Green
```

**运行验证**:

```powershell
.\check-environment.ps1
```

---

## 1.9 常见问题

### 问题1: 脚本无法运行

**错误信息**:
```
.\script.ps1 : File .\script.ps1 cannot be loaded because running scripts is disabled on this system.
```

**解决方案**:
```powershell
# 设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题2: 找不到pwsh命令

**原因**: PowerShell 7未正确安装或未添加到PATH

**解决方案**:
```powershell
# 检查环境变量
$env:PATH -split ';' | Select-String -Pattern "PowerShell"

# 手动添加到PATH
$env:PATH += ";C:\Program Files\PowerShell\7"

# 永久添加(需要管理员权限)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\PowerShell\7", "Machine")
```

### 问题3: 中文乱码

**解决方案**:
```powershell
# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001

# 或在Profile中添加
$OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 1.10 课后练习

### 练习1: 安装和配置

1. 安装PowerShell 7 (如果还没安装)
2. 设置执行策略为`RemoteSigned`
3. 创建Profile并添加欢迎消息
4. 安装Windows Terminal

### 练习2: 第一个脚本

创建一个脚本`system-info.ps1`,显示:
- 计算机名
- 用户名
- PowerShell版本
- 操作系统
- 当前时间

### 练习3: 探索命令

使用`Get-Help`命令探索:
- `Get-Process`
- `Get-Service`
- `Get-ChildItem`

找出每个命令至少3个常用参数。

---

## 1.11 本章小结

### 核心知识点

✅ **PowerShell是什么**: 命令行Shell + 脚本语言 + 管理框架

✅ **版本选择**: 推荐使用PowerShell 7+

✅ **安装方式**: 
- Windows: winget/MSI
- Linux: apt/yum
- macOS: Homebrew

✅ **执行策略**: RemoteSigned (推荐)

✅ **Profile**: 启动时自动执行的脚本

✅ **推荐工具**: Windows Terminal + VS Code

### 基本命令

```powershell
# 帮助
Get-Help <command>

# 文件操作
Get-ChildItem, New-Item, Copy-Item, Remove-Item

# 系统信息
Get-Process, Get-Service, Get-ComputerInfo

# 输出
Write-Host, Write-Output
```

### 下一章预告

**第2章 - PowerShell基础语法**,将学习:
- 🔤 命令结构(Cmdlet)
- 📖 帮助系统
- 🔗 管道基础
- 📝 格式化输出

---

[← 返回目录](./README.md) | [下一章: PowerShell基础语法 →](./2-PowerShell基础语法.md)
