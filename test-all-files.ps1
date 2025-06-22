# ClickHouse Learning Tutorial - File Integrity Check
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ClickHouse Learning Tutorial - File Integrity Check" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Define required files list
$requiredFiles = @(
    # Day 1: Environment Setup
    "day1/notes/installation.md",
    "day1/code/docker-install.sh",
    "day1/code/install-native.sh", 
    "day1/code/benchmark.sh",
    "day1/code/check-config.sh",
    "day1/configs/config.xml",
    "day1/configs/users.xml",
    "day1/examples/quick-start.sql",
    
    # Day 2: Core Concepts
    "day2/notes/introduction.md",
    "day2/examples/basic-queries.sql",
    "day2/cheatsheets/clickhouse-commands.md",
    
    # Day 3: Cloud Deployment
    "day3/notes/aliyun-deployment.md",
    "day3/terraform/main.tf",
    "day3/terraform/variables.tf", 
    "day3/terraform/outputs.tf",
    "day3/terraform/user_data.sh",
    "day3/terraform/zookeeper_user_data.sh",
    "day3/terraform/setup_aliyun.ps1",
    "day3/terraform/generate-ssh-key.ps1",
    
    # Day 4: SQL Syntax and Data Types
    "day4/notes/sql-syntax.md",
    "day4/examples/data-types-demo.sql",
    
    # Day 5: Table Engines
    "day5/notes/table-engines.md",
    "day5/examples/table-engines-demo.sql",
    
    # Day 6: Query Optimization and Indexes
    "day6/notes/query-optimization.md",
    "day6/examples/optimization-demo.sql",
    
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
Write-Host "Learning Path Status" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

# Day 1 status check
$day1Files = @(
    "day1/notes/installation.md",
    "day1/code/docker-install.sh", 
    "day1/code/install-native.sh",
    "day1/examples/quick-start.sql"
)
$day1Complete = ($day1Files | ForEach-Object { Test-Path $_ }) -notcontains $false
if($day1Complete) {
    Write-Host "Day 1 - Environment Setup:     COMPLETE" -ForegroundColor Green
} else {
    Write-Host "Day 1 - Environment Setup:     PENDING" -ForegroundColor Red
}

# Day 2 status check  
$day2Files = @(
    "day2/notes/introduction.md",
    "day2/examples/basic-queries.sql"
)
$day2Complete = ($day2Files | ForEach-Object { Test-Path $_ }) -notcontains $false
if($day2Complete) {
    Write-Host "Day 2 - Core Concepts:         COMPLETE" -ForegroundColor Green
} else {
    Write-Host "Day 2 - Core Concepts:         PENDING" -ForegroundColor Red
}

# Day 3 status check
$day3Files = @(
    "day3/notes/aliyun-deployment.md",
    "day3/terraform/main.tf",
    "day3/terraform/setup_aliyun.ps1"
)
$day3Complete = ($day3Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day3Complete) {
    Write-Host "Day 3 - Cloud Deployment:      COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 3 - Cloud Deployment:      PENDING" -ForegroundColor Red
}

# Day 4 status check
$day4Files = @(
    "day4/notes/sql-syntax.md",
    "day4/examples/data-types-demo.sql"
)
$day4Complete = ($day4Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day4Complete) {
    Write-Host "Day 4 - SQL Syntax & Data Types: COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 4 - SQL Syntax & Data Types: PENDING" -ForegroundColor Red
}

# Day 5 status check
$day5Files = @(
    "day5/notes/table-engines.md",
    "day5/examples/table-engines-demo.sql"
)
$day5Complete = ($day5Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day5Complete) {
    Write-Host "Day 5 - Table Engines:           COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 5 - Table Engines:           PENDING" -ForegroundColor Red
}

# Day 6 status check
$day6Files = @(
    "day6/notes/query-optimization.md",
    "day6/examples/optimization-demo.sql"
)
$day6Complete = ($day6Files | ForEach-Object { Test-Path $_ }) -notcontains $false  
if($day6Complete) {
    Write-Host "Day 6 - Query Optimization:      COMPLETE" -ForegroundColor Green  
} else {
    Write-Host "Day 6 - Query Optimization:      PENDING" -ForegroundColor Red
}

Write-Host ""

# Show next steps recommendation
Write-Host "Next Steps Recommendation" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

if ($completionPercentage -eq 100) {
    Write-Host "1. Start Day 1 learning: Read day1/notes/installation.md" -ForegroundColor Green
    Write-Host "2. Run environment setup: Execute day1/code/docker-install.sh" -ForegroundColor Green  
    Write-Host "3. Verify installation: Run day1/examples/quick-start.sql" -ForegroundColor Green
    Write-Host "4. Learn core concepts: Read day2/notes/introduction.md" -ForegroundColor Green
    Write-Host "5. Deploy cloud cluster: Execute day3/terraform/setup_aliyun.ps1" -ForegroundColor Green
} else {
    Write-Host "Please ensure all required files are properly generated first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Check completed! Start your ClickHouse learning journey!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan 