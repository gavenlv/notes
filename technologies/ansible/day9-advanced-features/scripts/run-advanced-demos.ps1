# Day 9: 高级特性演示脚本
# 运行各种高级特性的演示

param(
    [string]$Demo = "all",
    [switch]$Verbose,
    [switch]$DryRun
)

# 颜色定义
$Colors = @{
    Info = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Header = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Show-Header {
    Write-ColorOutput "==========================================" "Header"
    Write-ColorOutput "    Day 9: Ansible 高级特性演示" "Header"
    Write-ColorOutput "==========================================" "Header"
    Write-Host ""
}

function Show-Menu {
    Write-ColorOutput "请选择要运行的演示:" "Info"
    Write-Host "1. 异步任务演示 (async-tasks-demo.yml)" -ForegroundColor White
    Write-Host "2. 委托执行演示 (delegation-demo.yml)" -ForegroundColor White
    Write-Host "3. 执行策略演示 (strategy-demo.yml)" -ForegroundColor White
    Write-Host "4. 高级循环演示 (advanced-loops-demo.yml)" -ForegroundColor White
    Write-Host "5. 运行所有演示" -ForegroundColor White
    Write-Host "6. 性能测试" -ForegroundColor White
    Write-Host "7. 错误处理测试" -ForegroundColor White
    Write-Host "0. 退出" -ForegroundColor White
    Write-Host ""
}

function Test-Ansible {
    try {
        $ansibleVersion = ansible --version 2>$null
        if ($ansibleVersion) {
            Write-ColorOutput "✓ Ansible 已安装" "Success"
            return $true
        }
    }
    catch {
        Write-ColorOutput "✗ Ansible 未安装或不在 PATH 中" "Error"
        return $false
    }
    return $false
}

function Run-AsyncDemo {
    Write-ColorOutput "运行异步任务演示..." "Info"
    
    if ($DryRun) {
        Write-ColorOutput "模拟运行: ansible-playbook examples/async-tasks-demo.yml --check" "Warning"
        return
    }
    
    try {
        $result = ansible-playbook examples/async-tasks-demo.yml
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 异步任务演示完成" "Success"
        } else {
            Write-ColorOutput "✗ 异步任务演示失败" "Error"
        }
    }
    catch {
        Write-ColorOutput "✗ 运行异步任务演示时出错: $_" "Error"
    }
}

function Run-DelegationDemo {
    Write-ColorOutput "运行委托执行演示..." "Info"
    
    if ($DryRun) {
        Write-ColorOutput "模拟运行: ansible-playbook examples/delegation-demo.yml --check" "Warning"
        return
    }
    
    try {
        $result = ansible-playbook examples/delegation-demo.yml
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 委托执行演示完成" "Success"
        } else {
            Write-ColorOutput "✗ 委托执行演示失败" "Error"
        }
    }
    catch {
        Write-ColorOutput "✗ 运行委托执行演示时出错: $_" "Error"
    }
}

function Run-StrategyDemo {
    Write-ColorOutput "运行执行策略演示..." "Info"
    
    if ($DryRun) {
        Write-ColorOutput "模拟运行: ansible-playbook examples/strategy-demo.yml --check" "Warning"
        return
    }
    
    try {
        $result = ansible-playbook examples/strategy-demo.yml
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 执行策略演示完成" "Success"
        } else {
            Write-ColorOutput "✗ 执行策略演示失败" "Error"
        }
    }
    catch {
        Write-ColorOutput "✗ 运行执行策略演示时出错: $_" "Error"
    }
}

function Run-AdvancedLoopsDemo {
    Write-ColorOutput "运行高级循环演示..." "Info"
    
    if ($DryRun) {
        Write-ColorOutput "模拟运行: ansible-playbook examples/advanced-loops-demo.yml --check" "Warning"
        return
    }
    
    try {
        $result = ansible-playbook examples/advanced-loops-demo.yml
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 高级循环演示完成" "Success"
        } else {
            Write-ColorOutput "✗ 高级循环演示失败" "Error"
        }
    }
    catch {
        Write-ColorOutput "✗ 运行高级循环演示时出错: $_" "Error"
    }
}

function Run-PerformanceTest {
    Write-ColorOutput "运行性能测试..." "Info"
    
    # 创建性能测试 Playbook
    $performanceTest = @"
---
- name: 性能测试
  hosts: localhost
  gather_facts: no
  vars:
    test_iterations: 100
    test_data: "{{ range(1, test_iterations + 1) | list }}"
  
  tasks:
    - name: 测试循环性能
      debug:
        msg: "处理项目 {{ item }}"
      loop: "{{ test_data }}"
      loop_control:
        label: "项目: {{ item }}"
        
    - name: 测试异步任务性能
      shell: "echo '异步任务 {{ item }}' && sleep 1"
      async: 60
      poll: 0
      loop: "{{ range(1, 11) | list }}"
      
    - name: 性能测试完成
      debug:
        msg: "性能测试完成 - 处理了 {{ test_iterations }} 个项目"
"@
    
    $performanceTest | Out-File -FilePath "examples/performance-test.yml" -Encoding UTF8
    
    if ($DryRun) {
        Write-ColorOutput "模拟运行: ansible-playbook examples/performance-test.yml --check" "Warning"
        return
    }
    
    try {
        $startTime = Get-Date
        $result = ansible-playbook examples/performance-test.yml
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 性能测试完成" "Success"
            Write-ColorOutput "执行时间: $($duration.TotalSeconds) 秒" "Info"
        } else {
            Write-ColorOutput "✗ 性能测试失败" "Error"
        }
    }
    catch {
        Write-ColorOutput "✗ 运行性能测试时出错: $_" "Error"
    }
}

function Run-ErrorHandlingTest {
    Write-ColorOutput "运行错误处理测试..." "Info"
    
    # 创建错误处理测试 Playbook
    $errorTest = @"
---
- name: 错误处理测试
  hosts: localhost
  gather_facts: no
  
  tasks:
    - name: 测试基本错误处理
      command: "exit {{ item }}"
      loop: [0, 1, 0, 1, 0]
      register: error_results
      ignore_errors: yes
      
    - name: 显示错误结果
      debug:
        msg: "任务 {{ index }}: {{ '成功' if item.rc == 0 else '失败' }}"
      loop: "{{ error_results.results }}"
      loop_control:
        index_var: index
        extended: yes
        
    - name: 测试 block/rescue/always
      block:
        - name: 可能失败的任务
          command: "exit 1"
        - name: 这个任务不会执行
          debug:
            msg: "这个任务不会执行"
      rescue:
        - name: 错误处理
          debug:
            msg: "捕获到错误，正在处理..."
      always:
        - name: 清理任务
          debug:
            msg: "执行清理任务"
            
    - name: 测试重试机制
      command: "exit {{ (ansible_date_time.epoch | int) % 3 }}"
      register: retry_result
      until: retry_result.rc == 0
      retries: 5
      delay: 2
      backoff: 2
      
    - name: 显示重试结果
      debug:
        msg: "重试任务最终结果: {{ '成功' if retry_result.rc == 0 else '失败' }}"
"@
    
    $errorTest | Out-File -FilePath "examples/error-handling-test.yml" -Encoding UTF8
    
    if ($DryRun) {
        Write-ColorOutput "模拟运行: ansible-playbook examples/error-handling-test.yml --check" "Warning"
        return
    }
    
    try {
        $result = ansible-playbook examples/error-handling-test.yml
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 错误处理测试完成" "Success"
        } else {
            Write-ColorOutput "✗ 错误处理测试失败" "Error"
        }
    }
    catch {
        Write-ColorOutput "✗ 运行错误处理测试时出错: $_" "Error"
    }
}

function Run-AllDemos {
    Write-ColorOutput "运行所有演示..." "Info"
    
    $demos = @(
        @{ Name = "异步任务演示"; Function = "Run-AsyncDemo" },
        @{ Name = "委托执行演示"; Function = "Run-DelegationDemo" },
        @{ Name = "执行策略演示"; Function = "Run-StrategyDemo" },
        @{ Name = "高级循环演示"; Function = "Run-AdvancedLoopsDemo" }
    )
    
    foreach ($demo in $demos) {
        Write-ColorOutput "运行 $($demo.Name)..." "Info"
        & $demo.Function
        Write-Host ""
    }
    
    Write-ColorOutput "所有演示完成！" "Success"
}

# 主程序
Show-Header

# 检查 Ansible
if (-not (Test-Ansible)) {
    Write-ColorOutput "请先安装 Ansible 或确保其在 PATH 中" "Error"
    exit 1
}

# 根据参数运行相应的演示
switch ($Demo.ToLower()) {
    "async" { Run-AsyncDemo }
    "delegation" { Run-DelegationDemo }
    "strategy" { Run-StrategyDemo }
    "loops" { Run-AdvancedLoopsDemo }
    "performance" { Run-PerformanceTest }
    "error" { Run-ErrorHandlingTest }
    "all" { Run-AllDemos }
    default {
        do {
            Show-Menu
            $choice = Read-Host "请输入选择 (0-7)"
            
            switch ($choice) {
                "1" { Run-AsyncDemo }
                "2" { Run-DelegationDemo }
                "3" { Run-StrategyDemo }
                "4" { Run-AdvancedLoopsDemo }
                "5" { Run-AllDemos }
                "6" { Run-PerformanceTest }
                "7" { Run-ErrorHandlingTest }
                "0" { 
                    Write-ColorOutput "退出程序" "Info"
                    exit 0 
                }
                default { 
                    Write-ColorOutput "无效选择，请重新输入" "Warning"
                }
            }
            
            if ($choice -ne "0") {
                Write-Host ""
                $continue = Read-Host "按 Enter 继续，或输入 'q' 退出"
                if ($continue -eq "q") {
                    Write-ColorOutput "退出程序" "Info"
                    exit 0
                }
            }
        } while ($choice -ne "0")
    }
}

Write-ColorOutput "Day 9 高级特性演示完成！" "Success" 