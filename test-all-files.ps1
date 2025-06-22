# 技术学习教程 - 文件完整性检查
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  技术学习教程 - 文件完整性检查" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Define required files list
$requiredFiles = @(
    # ClickHouse Day 1: Environment Setup
    "clickhouse/day1/notes/installation.md",
    "clickhouse/day1/code/docker-install.sh",
    "clickhouse/day1/code/install-native.sh", 
    "clickhouse/day1/code/benchmark.sh",
    "clickhouse/day1/code/check-config.sh",
    "clickhouse/day1/configs/config.xml",
    "clickhouse/day1/configs/users.xml",
    "clickhouse/day1/examples/quick-start.sql",
    
    # ClickHouse Day 2: Core Concepts
    "clickhouse/day2/notes/introduction.md",
    "clickhouse/day2/examples/basic-queries.sql",
    "clickhouse/day2/cheatsheets/clickhouse-commands.md",
    
    # ClickHouse Day 3: Cloud Deployment
    "clickhouse/day3/notes/aliyun-deployment.md",
    "clickhouse/day3/terraform/main.tf",
    "clickhouse/day3/terraform/variables.tf", 
    "clickhouse/day3/terraform/outputs.tf",
    "clickhouse/day3/terraform/user_data.sh",
    "clickhouse/day3/terraform/zookeeper_user_data.sh",
    "clickhouse/day3/terraform/setup_aliyun.ps1",
    "clickhouse/day3/terraform/generate-ssh-key.ps1",
    
    # ClickHouse Day 4: SQL Syntax and Data Types
    "clickhouse/day4/notes/sql-syntax.md",
    "clickhouse/day4/examples/data-types-demo.sql",
    
    # ClickHouse Day 5: Table Engines
    "clickhouse/day5/notes/table-engines.md",
    "clickhouse/day5/examples/table-engines-demo.sql",
    
    # ClickHouse Day 6: Query Optimization and Indexes
    "clickhouse/day6/notes/query-optimization.md",
    "clickhouse/day6/examples/optimization-demo.sql",
    
    # ClickHouse Day 7: Data Import/Export
    "clickhouse/day7/notes/data-import-export.md",
    "clickhouse/day7/examples/import-export-demo.sql",
    "clickhouse/day7/data/sample_users.csv",
    "clickhouse/day7/data/events.json",
    "clickhouse/day7/code/import-export-tools.ps1",
    
    # ClickHouse Day 8: Cluster Management and Distributed
    "clickhouse/day8/notes/cluster-management.md",
    "clickhouse/day8/examples/cluster-demo.sql",
    "clickhouse/day8/configs/cluster-config.xml",
    "clickhouse/day8/configs/docker-compose.yml",
    "clickhouse/day8/scripts/test-cluster.ps1",
    
    # ClickHouse Day 9: Monitoring and Operations
    "clickhouse/day9/notes/monitoring-operations.md",
    "clickhouse/day9/examples/monitoring-demo.sql",
    "clickhouse/day9/configs/monitoring-config.xml",
    "clickhouse/day9/configs/prometheus.yml",
    "clickhouse/day9/scripts/monitoring-check.ps1",
    
    # ClickHouse Day 11: Security and Access Control
    "clickhouse/day11/notes/security-access-control.md",
    "clickhouse/day11/examples/security-demo.sql",
    "clickhouse/day11/configs/security-config.xml",
    "clickhouse/day11/scripts/security-setup.ps1",
    
    # Technology directories (planned)
    "technologies/docker/.gitkeep",
    "technologies/k8s/.gitkeep", 
    "technologies/doris/.gitkeep",
    "technologies/flink/.gitkeep",
    "technologies/airflow/.gitkeep",
    
    # Project root files
    "README.md",
    "test-all-files.ps1"
)

# Check file existence
$existingFiles = @()
$missingFiles = @()

Write-Host "Checking file integrity..." -ForegroundColor Green
Write-Host ""

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $existingFiles += $file
        Write-Host "OK   $file" -ForegroundColor Green
    } else {
        $missingFiles += $file  
        Write-Host "MISS $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Display statistics
$totalFiles = $requiredFiles.Count
$existingCount = $existingFiles.Count
$missingCount = $missingFiles.Count
$completionPercentage = [math]::Round(($existingCount / $totalFiles) * 100, 2)

Write-Host "Project Integrity Report" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Total files:     $totalFiles" -ForegroundColor White
Write-Host "Existing files:  $existingCount" -ForegroundColor Green  
Write-Host "Missing files:   $missingCount" -ForegroundColor Red
Write-Host "Completion:      $completionPercentage%" -ForegroundColor $(if($completionPercentage -eq 100) { "Green" } else { "Yellow" })
Write-Host ""

# Display project status
if ($completionPercentage -eq 100) {
    Write-Host "SUCCESS! All files exist. Ready to start learning!" -ForegroundColor Green
} elseif ($completionPercentage -ge 80) {
    Write-Host "WARNING: Project mostly complete but some files missing" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Project incomplete, please check file generation" -ForegroundColor Red
}

Write-Host ""

# Display learning path status
Write-Host "ClickHouse Learning Path Status" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

# ClickHouse Day 1 status check
$day1Files = @(
    "clickhouse/day1/notes/installation.md",
    "clickhouse/day1/code/docker-install.sh", 
    "clickhouse/day1/code/install-native.sh",
    "clickhouse/day1/examples/quick-start.sql"
)
$day1Complete = ($day1Files | ForEach-Object { Test-Path $_ }) -notcontains $false
if($day1Complete) {
    Write-Host "Day 1 - Environment Setup:        COMPLETE" -ForegroundColor Green
} else {
    Write-Host "Day 1 - Environment Setup:        PENDING" -ForegroundColor Red
}

# ClickHouse Day 2 status check  
$day2Files = @(
    "clickhouse/day2/notes/introduction.md",
    "clickhouse/day2/examples/basic-queries.sql"
)
$day2Complete = ($day2Files | ForEach-Object { Test-Path $_ }) -notcontains $false
if($day2Complete) {
    Write-Host "Day 2 - Core Concepts:            COMPLETE" -ForegroundColor Green
} else {
    Write-Host "Day 2 - Core Concepts:            PENDING" -ForegroundColor Red
}

# ClickHouse Day 3 status check
$day3Files = @(
    "clickhouse/day3/notes/aliyun-deployment.md",
    "clickhouse/day3/terraform/main.tf",
    "clickhouse/day3/terraform/setup_aliyun.ps1"
)
$day3Complete = ($day3Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day3Complete) {
    Write-Host "Day 3 - Cloud Deployment:         COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 3 - Cloud Deployment:         PENDING" -ForegroundColor Red
}

# ClickHouse Day 4 status check
$day4Files = @(
    "clickhouse/day4/notes/sql-syntax.md",
    "clickhouse/day4/examples/data-types-demo.sql"
)
$day4Complete = ($day4Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day4Complete) {
    Write-Host "Day 4 - SQL Syntax & Data Types:  COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 4 - SQL Syntax & Data Types:  PENDING" -ForegroundColor Red
}

# ClickHouse Day 5 status check
$day5Files = @(
    "clickhouse/day5/notes/table-engines.md",
    "clickhouse/day5/examples/table-engines-demo.sql"
)
$day5Complete = ($day5Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day5Complete) {
    Write-Host "Day 5 - Table Engines:            COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 5 - Table Engines:            PENDING" -ForegroundColor Red
}

# ClickHouse Day 6 status check
$day6Files = @(
    "clickhouse/day6/notes/query-optimization.md",
    "clickhouse/day6/examples/optimization-demo.sql"
)
$day6Complete = ($day6Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day6Complete) {
    Write-Host "Day 6 - Query Optimization:       COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 6 - Query Optimization:       PENDING" -ForegroundColor Red
}

# ClickHouse Day 7 status check
$day7Files = @(
    "clickhouse/day7/notes/data-import-export.md",
    "clickhouse/day7/examples/import-export-demo.sql",
    "clickhouse/day7/data/sample_users.csv",
    "clickhouse/day7/code/import-export-tools.ps1"
)
$day7Complete = ($day7Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day7Complete) {
    Write-Host "Day 7 - Data Import/Export:       COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 7 - Data Import/Export:       PENDING" -ForegroundColor Red
}

# ClickHouse Day 8 status check
$day8Files = @(
    "clickhouse/day8/notes/cluster-management.md",
    "clickhouse/day8/examples/cluster-demo.sql",
    "clickhouse/day8/configs/cluster-config.xml",
    "clickhouse/day8/scripts/test-cluster.ps1"
)
$day8Complete = ($day8Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day8Complete) {
    Write-Host "Day 8 - Cluster Management:       COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 8 - Cluster Management:       PENDING" -ForegroundColor Red
}

# ClickHouse Day 9 status check
$day9Files = @(
    "clickhouse/day9/notes/monitoring-operations.md",
    "clickhouse/day9/examples/monitoring-demo.sql",
    "clickhouse/day9/configs/monitoring-config.xml",
    "clickhouse/day9/scripts/monitoring-check.ps1"
)
$day9Complete = ($day9Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day9Complete) {
    Write-Host "Day 9 - Monitoring & Operations:  COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 9 - Monitoring & Operations:  PENDING" -ForegroundColor Red
}

# ClickHouse Day 11 status check
$day11Files = @(
    "clickhouse/day11/notes/security-access-control.md",
    "clickhouse/day11/examples/security-demo.sql",
    "clickhouse/day11/configs/security-config.xml",
    "clickhouse/day11/scripts/security-setup.ps1"
)
$day11Complete = ($day11Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day11Complete) {
    Write-Host "Day 11 - Security & Access Control: COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 11 - Security & Access Control: PENDING" -ForegroundColor Red
}

Write-Host ""

# Technology Stack Status
Write-Host "Technology Stack Status" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

$techDirs = @("docker", "k8s", "doris", "flink", "airflow")
foreach ($tech in $techDirs) {
    if (Test-Path "technologies/$tech") {
        Write-Host "$tech - Directory Created:       READY" -ForegroundColor Cyan
    } else {
        Write-Host "$tech - Directory Created:       MISSING" -ForegroundColor Red
    }
}

Write-Host ""

# Show next steps recommendation
Write-Host "Next Steps Recommendation" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

if ($day11Complete) {
    Write-Host "1. Continue with Day 12: Data Backup & Recovery" -ForegroundColor Green
    Write-Host "2. Practice Day 11 security configurations" -ForegroundColor Green
} elseif ($day9Complete) {
    Write-Host "1. Start Day 11 learning: Security and Access Control" -ForegroundColor Green
    Write-Host "2. Review monitoring configurations from Day 9" -ForegroundColor Green
} else {
    Write-Host "1. Start ClickHouse learning: Read clickhouse/day1/notes/installation.md" -ForegroundColor Green
    Write-Host "2. Setup environment: Execute clickhouse/day1/code/docker-install.sh" -ForegroundColor Green  
    Write-Host "3. Verify installation: Run clickhouse/day1/examples/quick-start.sql" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Check completed! Continue your learning journey!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan 