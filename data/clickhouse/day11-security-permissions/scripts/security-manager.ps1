# ClickHouse Day 11: 安全管理和审计脚本
# 用于管理用户权限、监控安全事件和执行安全审计

param(
    [string]$ClickHouseHost = "localhost",
    [int]$ClickHousePort = 8123,
    [string]$Database = "default",
    [string]$User = "default",
    [string]$Password = "",
    [string]$Action = "audit", # audit, users, permissions, security, alerts
    [string]$TargetUser = "",
    [string]$TargetRole = "",
    [int]$Days = 7
)

# ===============================================
# 配置和初始化
# ===============================================

$ClickHouseUrl = "http://${ClickHouseHost}:${ClickHousePort}"
$Headers = @{}
if ($User -and $Password) {
    $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes("${User}:${Password}"))
    $Headers["Authorization"] = "Basic $encodedCreds"
}

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

# 执行ClickHouse查询函数
function Invoke-ClickHouseQuery {
    param(
        [string]$Query,
        [string]$Format = "JSONEachRow",
        [switch]$Silent = $false
    )
    
    try {
        $body = @{
            query = $Query
            database = $Database
            default_format = $Format
        }
        
        $response = Invoke-RestMethod -Uri $ClickHouseUrl -Method Post -Body $body -Headers $Headers -ContentType "application/x-www-form-urlencoded"
        return $response
    }
    catch {
        if (-not $Silent) {
            Write-ColorOutput "查询执行失败: $($_.Exception.Message)" "Red"
        }
        return $null
    }
}

# ===============================================
# 用户管理功能
# ===============================================

function Show-UserManagement {
    Write-ColorOutput "`n=== 用户管理概览 ===" "Cyan"
    
    # 显示所有用户
    Write-ColorOutput "`n--- 系统用户列表 ---" "Yellow"
    $usersQuery = @"
SELECT 
    name as user_name,
    auth_type,
    host_ip,
    host_names_regexp,
    default_roles_list,
    default_database
FROM system.users
ORDER BY name
"@
    
    $users = Invoke-ClickHouseQuery -Query $usersQuery -Format "TSV"
    if ($users) {
        Write-ColorOutput $users "White"
    }
    
    # 显示所有角色
    Write-ColorOutput "`n--- 系统角色列表 ---" "Yellow"
    $rolesQuery = @"
SELECT 
    name as role_name,
    granted_roles_list
FROM system.roles
ORDER BY name
"@
    
    $roles = Invoke-ClickHouseQuery -Query $rolesQuery -Format "TSV"
    if ($roles) {
        Write-ColorOutput $roles "Green"
    }
}

function Show-UserDetails {
    param([string]$UserName)
    
    if (-not $UserName) {
        Write-ColorOutput "请指定用户名 -TargetUser <username>" "Red"
        return
    }
    
    Write-ColorOutput "`n=== 用户详细信息: $UserName ===" "Cyan"
    
    # 用户基本信息
    $userInfoQuery = @"
SELECT 
    name,
    auth_type,
    host_ip,
    host_names_regexp,
    default_roles_list,
    granted_roles_list,
    default_database,
    grantees_list
FROM system.users
WHERE name = '$UserName'
"@
    
    $userInfo = Invoke-ClickHouseQuery -Query $userInfoQuery -Format "TSV"
    if ($userInfo) {
        Write-ColorOutput "用户基本信息:" "Yellow"
        Write-ColorOutput $userInfo "White"
    }
    
    # 用户权限
    Write-ColorOutput "`n用户权限:" "Yellow"
    $permissionsQuery = @"
SELECT 
    access_type,
    database,
    table,
    column,
    is_partial_revoke,
    grant_option
FROM system.grants
WHERE user_name = '$UserName'
ORDER BY access_type, database, table
"@
    
    $permissions = Invoke-ClickHouseQuery -Query $permissionsQuery -Format "TSV"
    if ($permissions) {
        Write-ColorOutput $permissions "Green"
    } else {
        Write-ColorOutput "用户没有直接权限（可能通过角色获得权限）" "Yellow"
    }
    
    # 用户会话历史
    Write-ColorOutput "`n最近会话历史:" "Yellow"
    $sessionsQuery = @"
SELECT 
    event_type,
    event_time,
    client_address,
    client_hostname,
    interface,
    session_id
FROM system.session_log
WHERE user = '$UserName'
AND event_date >= today() - $Days
ORDER BY event_time DESC
LIMIT 10
"@
    
    $sessions = Invoke-ClickHouseQuery -Query $sessionsQuery -Format "TSV"
    if ($sessions) {
        Write-ColorOutput $sessions "Cyan"
    }
}

function Show-PermissionsMatrix {
    Write-ColorOutput "`n=== 权限矩阵 ===" "Cyan"
    
    $permissionsQuery = @"
SELECT 
    if(user_name != '', user_name, role_name) as principal,
    if(user_name != '', 'USER', 'ROLE') as principal_type,
    access_type,
    database,
    table,
    if(column != '', column, '*') as column_access
FROM system.grants
WHERE (user_name != '' OR role_name != '')
ORDER BY principal, access_type, database, table
"@
    
    $permissions = Invoke-ClickHouseQuery -Query $permissionsQuery -Format "TSV"
    if ($permissions) {
        Write-ColorOutput $permissions "White"
    }
}

# ===============================================
# 安全审计功能
# ===============================================

function Show-SecurityAudit {
    Write-ColorOutput "`n=== 安全审计报告 ===" "Cyan"
    
    # 登录活动分析
    Write-ColorOutput "`n--- 登录活动分析 (最近 $Days 天) ---" "Yellow"
    $loginQuery = @"
SELECT 
    user,
    event_type,
    count() as event_count,
    uniq(client_address) as unique_ips,
    min(event_time) as first_event,
    max(event_time) as last_event
FROM system.session_log
WHERE event_date >= today() - $Days
GROUP BY user, event_type
ORDER BY user, event_type
"@
    
    $loginActivity = Invoke-ClickHouseQuery -Query $loginQuery -Format "TSV"
    if ($loginActivity) {
        Write-ColorOutput $loginActivity "White"
    }
    
    # 失败登录分析
    Write-ColorOutput "`n--- 失败登录分析 ---" "Yellow"
    $failedLoginsQuery = @"
SELECT 
    user,
    client_address,
    count() as failed_attempts,
    max(event_time) as last_attempt
FROM system.session_log
WHERE event_type = 'LoginFailure'
AND event_date >= today() - $Days
GROUP BY user, client_address
HAVING failed_attempts > 3
ORDER BY failed_attempts DESC
"@
    
    $failedLogins = Invoke-ClickHouseQuery -Query $failedLoginsQuery -Format "TSV"
    if ($failedLogins) {
        Write-ColorOutput $failedLogins "Red"
    } else {
        Write-ColorOutput "没有发现异常登录失败" "Green"
    }
    
    # 权限变更审计
    Write-ColorOutput "`n--- 权限变更审计 ---" "Yellow"
    $permissionChangesQuery = @"
SELECT 
    user,
    client_address,
    event_time,
    left(query, 100) as permission_operation
FROM system.query_log
WHERE (query ILIKE '%CREATE USER%' 
    OR query ILIKE '%DROP USER%'
    OR query ILIKE '%ALTER USER%'
    OR query ILIKE '%GRANT%'
    OR query ILIKE '%REVOKE%'
    OR query ILIKE '%CREATE ROLE%'
    OR query ILIKE '%DROP ROLE%')
AND event_date >= today() - $Days
AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 20
"@
    
    $permissionChanges = Invoke-ClickHouseQuery -Query $permissionChangesQuery -Format "TSV"
    if ($permissionChanges) {
        Write-ColorOutput $permissionChanges "Magenta"
    }
    
    # 数据访问模式分析
    Write-ColorOutput "`n--- 数据访问模式分析 ---" "Yellow"
    $dataAccessQuery = @"
SELECT 
    user,
    extractAll(query, 'FROM\\s+([\\w\\.]+)')[1] as accessed_table,
    count() as access_count,
    sum(read_rows) as total_rows_read,
    formatReadableSize(sum(read_bytes)) as total_bytes_read,
    avg(query_duration_ms) as avg_duration_ms
FROM system.query_log
WHERE type = 'QueryFinish'
AND event_date >= today() - $Days
AND query ILIKE '%SELECT%'
AND accessed_table != ''
GROUP BY user, accessed_table
HAVING access_count > 10
ORDER BY access_count DESC
LIMIT 20
"@
    
    $dataAccess = Invoke-ClickHouseQuery -Query $dataAccessQuery -Format "TSV"
    if ($dataAccess) {
        Write-ColorOutput $dataAccess "Cyan"
    }
}

function Show-SecurityAlerts {
    Write-ColorOutput "`n=== 安全告警检查 ===" "Cyan"
    
    # 检查可疑查询模式
    Write-ColorOutput "`n--- 可疑查询模式检测 ---" "Yellow"
    $suspiciousQuery = @"
SELECT 
    'Suspicious Query Pattern' as alert_type,
    user,
    client_address,
    event_time,
    left(query, 100) as suspicious_query,
    'Potential SQL injection or data exfiltration' as description
FROM system.query_log
WHERE (query ILIKE '%UNION%SELECT%' 
    OR query ILIKE '%OR%1=1%'
    OR query ILIKE '%DROP%TABLE%'
    OR query ILIKE '%DELETE%FROM%'
    OR query ILIKE '%UPDATE%SET%'
    OR query ILIKE '%TRUNCATE%')
AND event_date >= today() - $Days
AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 10
"@
    
    $suspiciousQueries = Invoke-ClickHouseQuery -Query $suspiciousQuery -Format "TSV"
    if ($suspiciousQueries) {
        Write-ColorOutput $suspiciousQueries "Red"
    } else {
        Write-ColorOutput "✅ 没有发现可疑查询模式" "Green"
    }
    
    # 检查异常登录
    Write-ColorOutput "`n--- 异常登录检测 ---" "Yellow"
    $anomalousLoginsQuery = @"
SELECT 
    'Anomalous Login' as alert_type,
    user,
    client_address,
    event_time,
    'Login from unusual IP or time' as description
FROM (
    SELECT 
        user,
        client_address,
        event_time,
        count() OVER (PARTITION BY user, client_address) as ip_frequency
    FROM system.session_log
    WHERE event_type = 'LoginSuccess'
    AND event_date >= today() - $Days
) 
WHERE ip_frequency = 1  -- 只登录过一次的IP
ORDER BY event_time DESC
LIMIT 10
"@
    
    $anomalousLogins = Invoke-ClickHouseQuery -Query $anomalousLoginsQuery -Format "TSV"
    if ($anomalousLogins) {
        Write-ColorOutput $anomalousLogins "Yellow"
    } else {
        Write-ColorOutput "✅ 没有发现异常登录" "Green"
    }
    
    # 检查权限提升
    Write-ColorOutput "`n--- 权限提升检测 ---" "Yellow"
    $privilegeEscalationQuery = @"
SELECT 
    'Privilege Escalation' as alert_type,
    user,
    client_address,
    event_time,
    'User granted elevated privileges' as description
FROM system.query_log
WHERE (query ILIKE '%GRANT%ALL%'
    OR query ILIKE '%GRANT%SYSTEM%'
    OR query ILIKE '%GRANT%ACCESS MANAGEMENT%')
AND event_date >= today() - $Days
AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 10
"@
    
    $privilegeEscalation = Invoke-ClickHouseQuery -Query $privilegeEscalationQuery -Format "TSV"
    if ($privilegeEscalation) {
        Write-ColorOutput $privilegeEscalation "Red"
    } else {
        Write-ColorOutput "✅ 没有发现权限提升行为" "Green"
    }
    
    # 检查数据泄露风险
    Write-ColorOutput "`n--- 数据泄露风险检测 ---" "Yellow"
    $dataLeakageQuery = @"
SELECT 
    'Data Leakage Risk' as alert_type,
    user,
    client_address,
    event_time,
    concat('Large data export: ', formatReadableSize(read_bytes)) as description
FROM system.query_log
WHERE type = 'QueryFinish'
AND event_date >= today() - $Days
AND read_bytes > 1000000000  -- 大于1GB的查询
AND query ILIKE '%SELECT%'
ORDER BY read_bytes DESC
LIMIT 10
"@
    
    $dataLeakage = Invoke-ClickHouseQuery -Query $dataLeakageQuery -Format "TSV"
    if ($dataLeakage) {
        Write-ColorOutput $dataLeakage "Red"
    } else {
        Write-ColorOutput "✅ 没有发现大量数据导出" "Green"
    }
}

function Show-SecurityMetrics {
    Write-ColorOutput "`n=== 安全指标统计 ===" "Cyan"
    
    # 用户活跃度统计
    Write-ColorOutput "`n--- 用户活跃度统计 ---" "Yellow"
    $userActivityQuery = @"
SELECT 
    user,
    count() as total_queries,
    count(DISTINCT toDate(event_time)) as active_days,
    count(DISTINCT client_address) as unique_ips,
    formatReadableSize(sum(read_bytes)) as total_data_read,
    avg(query_duration_ms) as avg_query_duration
FROM system.query_log
WHERE type = 'QueryFinish'
AND event_date >= today() - $Days
GROUP BY user
ORDER BY total_queries DESC
"@
    
    $userActivity = Invoke-ClickHouseQuery -Query $userActivityQuery -Format "TSV"
    if ($userActivity) {
        Write-ColorOutput $userActivity "White"
    }
    
    # 安全事件统计
    Write-ColorOutput "`n--- 安全事件统计 ---" "Yellow"
    $securityStatsQuery = @"
SELECT 
    'Total Users' as metric,
    toString(count()) as value
FROM system.users

UNION ALL

SELECT 
    'Active Users (${Days}d)' as metric,
    toString(count(DISTINCT user)) as value
FROM system.query_log
WHERE event_date >= today() - $Days

UNION ALL

SELECT 
    'Failed Logins (${Days}d)' as metric,
    toString(count()) as value
FROM system.session_log
WHERE event_type = 'LoginFailure'
AND event_date >= today() - $Days

UNION ALL

SELECT 
    'Permission Changes (${Days}d)' as metric,
    toString(count()) as value
FROM system.query_log
WHERE (query ILIKE '%GRANT%' OR query ILIKE '%REVOKE%')
AND event_date >= today() - $Days

UNION ALL

SELECT 
    'System Queries (${Days}d)' as metric,
    toString(count()) as value
FROM system.query_log
WHERE query ILIKE '%system.%'
AND event_date >= today() - $Days
"@
    
    $securityStats = Invoke-ClickHouseQuery -Query $securityStatsQuery -Format "TSV"
    if ($securityStats) {
        Write-ColorOutput $securityStats "Cyan"
    }
}

# ===============================================
# 用户管理操作
# ===============================================

function New-ClickHouseUser {
    param(
        [string]$UserName,
        [string]$Password,
        [string]$Profile = "default",
        [string]$AllowedIP = "127.0.0.1"
    )
    
    if (-not $UserName -or -not $Password) {
        Write-ColorOutput "请提供用户名和密码" "Red"
        return
    }
    
    Write-ColorOutput "创建用户: $UserName" "Yellow"
    
    $createUserQuery = @"
CREATE USER $UserName 
IDENTIFIED WITH sha256_password BY '$Password'
HOST IP '$AllowedIP'
SETTINGS PROFILE '$Profile'
"@
    
    $result = Invoke-ClickHouseQuery -Query $createUserQuery -Silent
    if ($result -ne $null) {
        Write-ColorOutput "✅ 用户 $UserName 创建成功" "Green"
    } else {
        Write-ColorOutput "❌ 用户创建失败" "Red"
    }
}

function Remove-ClickHouseUser {
    param([string]$UserName)
    
    if (-not $UserName) {
        Write-ColorOutput "请提供用户名" "Red"
        return
    }
    
    Write-ColorOutput "删除用户: $UserName" "Yellow"
    Write-ColorOutput "⚠️  这是一个危险操作，请确认！" "Red"
    $confirmation = Read-Host "输入 'YES' 确认删除用户 $UserName"
    
    if ($confirmation -eq "YES") {
        $dropUserQuery = "DROP USER IF EXISTS $UserName"
        $result = Invoke-ClickHouseQuery -Query $dropUserQuery -Silent
        if ($result -ne $null) {
            Write-ColorOutput "✅ 用户 $UserName 删除成功" "Green"
        } else {
            Write-ColorOutput "❌ 用户删除失败" "Red"
        }
    } else {
        Write-ColorOutput "操作已取消" "Yellow"
    }
}

function Grant-ClickHousePermission {
    param(
        [string]$UserName,
        [string]$Permission = "SELECT",
        [string]$Database = "*",
        [string]$Table = "*"
    )
    
    if (-not $UserName) {
        Write-ColorOutput "请提供用户名" "Red"
        return
    }
    
    Write-ColorOutput "授予权限: $Permission ON $Database.$Table TO $UserName" "Yellow"
    
    $grantQuery = "GRANT $Permission ON $Database.$Table TO $UserName"
    $result = Invoke-ClickHouseQuery -Query $grantQuery -Silent
    if ($result -ne $null) {
        Write-ColorOutput "✅ 权限授予成功" "Green"
    } else {
        Write-ColorOutput "❌ 权限授予失败" "Red"
    }
}

# ===============================================
# 密码生成和安全工具
# ===============================================

function New-SecurePassword {
    param([int]$Length = 16)
    
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    
    return $password
}

function Get-PasswordHash {
    param([string]$Password)
    
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Password)
    $hash = $sha256.ComputeHash($bytes)
    $hashString = [System.BitConverter]::ToString($hash) -replace '-', ''
    
    return $hashString.ToLower()
}

function Test-PasswordStrength {
    param([string]$Password)
    
    $score = 0
    $feedback = @()
    
    if ($Password.Length -ge 8) { $score += 1 } else { $feedback += "密码长度至少8位" }
    if ($Password -cmatch '[a-z]') { $score += 1 } else { $feedback += "需要包含小写字母" }
    if ($Password -cmatch '[A-Z]') { $score += 1 } else { $feedback += "需要包含大写字母" }
    if ($Password -match '\d') { $score += 1 } else { $feedback += "需要包含数字" }
    if ($Password -match '[!@#$%^&*(),.?":{}|<>]') { $score += 1 } else { $feedback += "需要包含特殊字符" }
    
    $strength = switch ($score) {
        0 { "很弱" }
        1 { "弱" }
        2 { "一般" }
        3 { "良好" }
        4 { "强" }
        5 { "很强" }
    }
    
    Write-ColorOutput "密码强度: $strength ($score/5)" $(if ($score -ge 4) { "Green" } elseif ($score -ge 2) { "Yellow" } else { "Red" })
    
    if ($feedback.Count -gt 0) {
        Write-ColorOutput "改进建议:" "Yellow"
        foreach ($item in $feedback) {
            Write-ColorOutput "  - $item" "White"
        }
    }
}

# ===============================================
# 主函数
# ===============================================

function Show-Help {
    Write-ColorOutput @"
ClickHouse 安全管理脚本使用说明:

参数:
  -ClickHouseHost    ClickHouse 服务器地址 (默认: localhost)
  -ClickHousePort    ClickHouse HTTP 端口 (默认: 8123)
  -Database          数据库名称 (默认: default)
  -User              用户名 (默认: default)
  -Password          密码 (默认: 空)
  -Action            操作类型 (默认: audit)
  -TargetUser        目标用户名
  -TargetRole        目标角色名
  -Days              分析天数 (默认: 7)

操作类型:
  audit             - 执行安全审计
  users             - 用户管理
  permissions       - 权限管理
  security          - 安全指标
  alerts            - 安全告警
  password          - 密码工具

示例:
  .\security-manager.ps1 -Action audit -Days 30
  .\security-manager.ps1 -Action users -TargetUser john_doe
  .\security-manager.ps1 -Action permissions
  .\security-manager.ps1 -Action alerts
"@ "White"
}

function Main {
    Write-ColorOutput "ClickHouse 安全管理工具" "Cyan"
    Write-ColorOutput "连接到: $ClickHouseUrl" "White"
    Write-ColorOutput "操作: $Action" "White"
    Write-ColorOutput "=" * 50 "White"
    
    # 测试连接
    try {
        $testQuery = "SELECT version()"
        $version = Invoke-ClickHouseQuery -Query $testQuery -Format "TabSeparated"
        Write-ColorOutput "ClickHouse 版本: $version" "Green"
    }
    catch {
        Write-ColorOutput "无法连接到 ClickHouse 服务器: $($_.Exception.Message)" "Red"
        return
    }
    
    switch ($Action.ToLower()) {
        "audit" {
            Show-SecurityAudit
        }
        "users" {
            if ($TargetUser) {
                Show-UserDetails -UserName $TargetUser
            } else {
                Show-UserManagement
            }
        }
        "permissions" {
            Show-PermissionsMatrix
        }
        "security" {
            Show-SecurityMetrics
        }
        "alerts" {
            Show-SecurityAlerts
        }
        "password" {
            $newPassword = New-SecurePassword -Length 16
            Write-ColorOutput "生成的安全密码: $newPassword" "Green"
            Write-ColorOutput "SHA256 哈希: $(Get-PasswordHash -Password $newPassword)" "Cyan"
            Test-PasswordStrength -Password $newPassword
        }
        "help" {
            Show-Help
        }
        default {
            Write-ColorOutput "未知操作: $Action" "Red"
            Show-Help
        }
    }
    
    Write-ColorOutput "`n安全管理操作完成!" "Cyan"
}

# ===============================================
# 执行脚本
# ===============================================

# 检查帮助参数
if ($args -contains "-help" -or $args -contains "--help" -or $args -contains "/?") {
    Show-Help
    return
}

# 执行主函数
Main 