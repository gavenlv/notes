# Day 7: ClickHouse Data Import/Export Tools

param(
    [string]$Operation = "help",
    [string]$InputFile = "",
    [string]$OutputFile = ""
)

Write-Host "ClickHouse Data Import/Export Tools" -ForegroundColor Green

function Show-Help {
    Write-Host "Usage: .\import-export-tools.ps1 -Operation <operation>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Operations:" -ForegroundColor Cyan
    Write-Host "  help           - Show this help"
    Write-Host "  create-sample  - Create sample data"
    Write-Host "  test-formats   - Test various formats"
    Write-Host ""
}

function Test-ClickHouse {
    try {
        $result = clickhouse-client --query="SELECT 1" 2>$null
        return ($result -eq "1")
    }
    catch {
        return $false
    }
}

function Create-SampleData {
    Write-Host "Creating sample data..." -ForegroundColor Blue
    
    $query = "CREATE DATABASE IF NOT EXISTS analytics; 
              CREATE TABLE IF NOT EXISTS analytics.user_analytics (
                  user_id UInt32,
                  event_date Date,
                  page_views UInt32,
                  session_duration UInt32,
                  country String,
                  device_type String,
                  revenue Decimal(10, 2)
              ) ENGINE = MergeTree()
              ORDER BY (user_id, event_date)"
    
    clickhouse-client --query="$query"
    Write-Host "Sample data creation completed" -ForegroundColor Green
}

switch ($Operation.ToLower()) {
    "create-sample" {
        if (Test-ClickHouse) {
            Create-SampleData
        } else {
            Write-Host "ClickHouse not available" -ForegroundColor Red
        }
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
}

Write-Host "Operation completed!" -ForegroundColor Green 