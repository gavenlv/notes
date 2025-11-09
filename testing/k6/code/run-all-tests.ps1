# k6测试脚本 - Windows PowerShell版本
# 作者：k6学习指南
# 描述：运行所有章节的测试脚本

Write-Host "=== k6性能测试套件 ===" -ForegroundColor Cyan
Write-Host "开始时间: $(Get-Date)"
Write-Host ""

# 检查k6是否安装
if (-not (Get-Command k6 -ErrorAction SilentlyContinue)) {
    Write-Host "错误: k6未安装，请先安装k6" -ForegroundColor Red
    Write-Host "安装方法: https://k6.io/docs/getting-started/installation/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ k6已安装，版本: $(k6 version)" -ForegroundColor Green
Write-Host ""

# 测试计数器
$TotalTests = 0
$PassedTests = 0
$FailedTests = 0

# 运行测试函数
function Run-Test {
    param(
        [string]$TestFile,
        [string]$TestName
    )
    
    Write-Host "▶ 运行测试: $TestName" -ForegroundColor Blue
    Write-Host "文件: $TestFile"
    
    if (-not (Test-Path $TestFile)) {
        Write-Host "⚠ 测试文件不存在: $TestFile" -ForegroundColor Yellow
        return $false
    }
    
    $TotalTests = $script:TotalTests + 1
    $script:TotalTests = $TotalTests
    
    try {
        # 运行测试（限制时间为2分钟）
        $process = Start-Process -FilePath "k6" -ArgumentList "run", "$TestFile", "--no-summary", "--no-usage-report" -PassThru -NoNewWindow
        
        # 等待进程完成，最多2分钟
        $process | Wait-Process -Timeout 120 -ErrorAction SilentlyContinue
        
        if ($process.HasExited) {
            if ($process.ExitCode -eq 0) {
                Write-Host "✓ 测试通过: $TestName" -ForegroundColor Green
                $script:PassedTests = $script:PassedTests + 1
                return $true
            } else {
                Write-Host "✗ 测试失败: $TestName" -ForegroundColor Red
                $script:FailedTests = $script:FailedTests + 1
                return $false
            }
        } else {
            # 超时，终止进程
            $process | Stop-Process -Force
            Write-Host "⚠ 测试超时: $TestName (2分钟限制)" -ForegroundColor Yellow
            $script:FailedTests = $script:FailedTests + 1
            return $false
        }
    } catch {
        Write-Host "✗ 测试执行错误: $TestName" -ForegroundColor Red
        Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
        $script:FailedTests = $script:FailedTests + 1
        return $false
    }
    
    Write-Host ""
}

# 第1章测试
Write-Host "=== 第1章：基础概念与环境搭建 ===" -ForegroundColor Cyan
Run-Test -TestFile "chapter1/1-first-test.js" -TestName "第一个k6测试"
Run-Test -TestFile "chapter1/experiment1-basic-validation.js" -TestName "基础环境验证实验"

# 第2章测试
Write-Host "=== 第2章：脚本编写基础 ===" -ForegroundColor Cyan
Run-Test -TestFile "chapter2/basic-script-structure.js" -TestName "脚本基本结构"
Run-Test -TestFile "chapter2/http-requests.js" -TestName "HTTP请求示例"
Run-Test -TestFile "chapter2/checks-and-validations.js" -TestName "检查点和验证"
Run-Test -TestFile "chapter2/groups.js" -TestName "分组功能"
Run-Test -TestFile "chapter2/experiment2-api-scenario.js" -TestName "完整API测试场景"

# 第3章测试
Write-Host "=== 第3章：高级功能与性能测试 ===" -ForegroundColor Cyan
Run-Test -TestFile "chapter3/custom-metrics.js" -TestName "自定义指标"
Run-Test -TestFile "chapter3/scenarios-executors.js" -TestName "场景和执行器"

# 注意：以下测试文件可能运行时间较长，可根据需要取消注释
# Run-Test -TestFile "chapter3/experiment3-ecommerce-scenario.js" -TestName "电商网站综合性能测试"

# 第4章测试
Write-Host "=== 第4章：最佳实践与生产环境部署 ===" -ForegroundColor Cyan
Run-Test -TestFile "chapter4/production-framework.js" -TestName "生产级测试框架"

# 显示测试结果
Write-Host "=== 测试结果汇总 ===" -ForegroundColor Cyan
Write-Host "总测试数: $TotalTests"
Write-Host "通过: $PassedTests" -ForegroundColor Green
Write-Host "失败: $FailedTests" -ForegroundColor Red

if ($FailedTests -eq 0) {
    Write-Host "🎉 所有测试通过！" -ForegroundColor Green
} else {
    Write-Host "⚠ 有 $FailedTests 个测试失败" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "结束时间: $(Get-Date)"

# 退出码
if ($FailedTests -eq 0) {
    exit 0
} else {
    exit 1
}