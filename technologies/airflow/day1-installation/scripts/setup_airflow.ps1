# Airflow 安装脚本 (Windows PowerShell)
# 此脚本将设置 Python 虚拟环境并安装 Airflow

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    White = "White"
}

# 打印带颜色的消息
function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Info {
    param([string]$Message)
    Write-ColorMessage "[INFO] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorMessage "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorMessage "[ERROR] $Message" "Red"
}

# 检查 Python 版本
function Test-PythonVersion {
    Write-Info "检查 Python 版本..."
    
    try {
        $pythonCmd = Get-Command python -ErrorAction Stop
        $pythonVersion = & python --version 2>&1
        Write-Info "找到 Python: $pythonVersion"
        
        # 检查版本是否满足要求 (3.8+)
        $versionParts = $pythonVersion -split ' '
        if ($versionParts.Length -ge 2) {
            $versionString = $versionParts[1]
            $versionNumbers = $versionString -split '\.'
            $major = [int]$versionNumbers[0]
            $minor = [int]$versionNumbers[1]
            
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 8)) {
                Write-Info "Python 版本检查通过: $versionString"
                return $true
            } else {
                Write-Error "Python 版本过低: $versionString，需要 3.8 或更高版本"
                return $false
            }
        } else {
            Write-Error "无法解析 Python 版本"
            return $false
        }
    } catch {
        Write-Error "Python 未安装或不在 PATH 中，请先安装 Python 3.8+"
        return $false
    }
}

# 创建虚拟环境
function New-VirtualEnvironment {
    Write-Info "创建 Python 虚拟环境..."
    
    $venvDir = "airflow-env"
    
    if (Test-Path $venvDir) {
        Write-Warning "虚拟环境 $venvDir 已存在，跳过创建"
    } else {
        try {
            & python -m venv $venvDir
            Write-Info "虚拟环境创建成功: $venvDir"
        } catch {
            Write-Error "创建虚拟环境失败: $_"
            return $false
        }
    }
    
    # 激活虚拟环境
    try {
        & "$venvDir\Scripts\Activate.ps1"
        Write-Info "虚拟环境已激活"
        return $true
    } catch {
        Write-Warning "无法激活虚拟环境，请手动执行: .\$venvDir\Scripts\Activate.ps1"
        return $false
    }
}

# 升级 pip
function Update-Pip {
    Write-Info "升级 pip..."
    
    try {
        & python -m pip install --upgrade pip
        Write-Info "pip 升级完成"
        return $true
    } catch {
        Write-Error "pip 升级失败: $_"
        return $false
    }
}

# 安装 Airflow
function Install-Airflow {
    Write-Info "安装 Apache Airflow..."
    
    try {
        # 安装 Airflow
        & pip install apache-airflow
        Write-Info "Airflow 安装完成"
        
        # 安装常用的提供者包
        Write-Info "安装 Airflow 提供者包..."
        & pip install apache-airflow-providers-postgres
        & pip install apache-airflow-providers-amazon
        & pip install apache-airflow-providers-docker
        
        Write-Info "Airflow 提供者包安装完成"
        return $true
    } catch {
        Write-Error "Airflow 安装失败: $_"
        return $false
    }
}

# 设置 Airflow 主目录
function Set-AirflowHome {
    Write-Info "设置 Airflow 主目录..."
    
    $airflowHomeDir = "$env:USERPROFILE\airflow"
    
    if (!(Test-Path $airflowHomeDir)) {
        New-Item -ItemType Directory -Path $airflowHomeDir -Force | Out-Null
        Write-Info "创建 Airflow 主目录: $airflowHomeDir"
    } else {
        Write-Warning "Airflow 主目录已存在: $airflowHomeDir"
    }
    
    # 设置环境变量
    [System.Environment]::SetEnvironmentVariable('AIRFLOW_HOME', $airflowHomeDir, 'User')
    $env:AIRFLOW_HOME = $airflowHomeDir
    Write-Info "AIRFLOW_HOME 环境变量已设置为: $airflowHomeDir"
    
    # 创建必要的子目录
    $dagsDir = Join-Path $airflowHomeDir "dags"
    $logsDir = Join-Path $airflowHomeDir "logs"
    $pluginsDir = Join-Path $airflowHomeDir "plugins"
    
    New-Item -ItemType Directory -Path $dagsDir -Force | Out-Null
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    New-Item -ItemType Directory -Path $pluginsDir -Force | Out-Null
    
    Write-Info "Airflow 目录结构创建完成"
    return $true
}

# 初始化 Airflow 数据库
function Initialize-AirflowDatabase {
    Write-Info "初始化 Airflow 数据库..."
    
    try {
        & airflow db init
        Write-Info "Airflow 数据库初始化完成"
        return $true
    } catch {
        Write-Error "Airflow 数据库初始化失败: $_"
        return $false
    }
}

# 创建管理员用户
function New-AdminUser {
    Write-Info "创建 Airflow 管理员用户..."
    
    try {
        & airflow users create `
            --username admin `
            --firstname Admin `
            --lastname User `
            --role Admin `
            --email admin@example.com `
            --password admin
        
        Write-Info "管理员用户创建完成 (用户名: admin, 密码: admin)"
        return $true
    } catch {
        Write-Warning "管理员用户创建可能失败，请手动创建或使用默认账户"
        return $false
    }
}

# 显示完成信息
function Show-CompletionInfo {
    Write-Info "Airflow 安装完成！"
    Write-Host ""
    Write-Info "下一步操作："
    Write-Host "1. 激活虚拟环境: .\airflow-env\Scripts\Activate.ps1"
    Write-Host "2. 启动 Airflow Web 服务器: airflow webserver --port 8080"
    Write-Host "3. 在新终端启动调度器: airflow scheduler"
    Write-Host "4. 访问 Web UI: http://localhost:8080"
    Write-Host "5. 使用管理员账户登录 (用户名: admin, 密码: admin)"
    Write-Host ""
    Write-Info "或者使用 standalone 模式同时启动 Web 服务器和调度器："
    Write-Host "airflow standalone"
}

# 主函数
function Main {
    Write-Info "开始安装 Apache Airflow..."
    
    if (!(Test-PythonVersion)) {
        return
    }
    
    if (!(New-VirtualEnvironment)) {
        return
    }
    
    if (!(Update-Pip)) {
        return
    }
    
    if (!(Install-Airflow)) {
        return
    }
    
    if (!(Set-AirflowHome)) {
        return
    }
    
    if (!(Initialize-AirflowDatabase)) {
        return
    }
    
    New-AdminUser
    Show-CompletionInfo
    
    Write-Info "安装脚本执行完成！"
}

# 执行主函数
Main