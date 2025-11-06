# Deployment Script for MyApp

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [string]$Tag = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Function to display usage
function Show-Usage {
    Write-Host "Usage: deploy.ps1 [-Environment <development|staging|production>] [-Tag <version>] [-Help]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Environment  Set environment (development|staging|production) [default: development]" -ForegroundColor Yellow
    Write-Host "  -Tag          Set deployment tag/version" -ForegroundColor Yellow
    Write-Host "  -Help         Display this help message" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 -Environment staging" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 -Environment production -Tag v1.0.0" -ForegroundColor Yellow
}

# Check if help is requested
if ($Help) {
    Show-Usage
    exit 0
}

# Validate environment
$validEnvironments = @("development", "staging", "production")
if ($validEnvironments -notcontains $Environment) {
    Write-Error "Invalid environment. Must be development, staging, or production."
    exit 1
}

Write-Host "Starting deployment to $Environment environment..." -ForegroundColor Green

# Determine inventory file
$inventoryFile = "inventory\$Environment"

# Check if inventory file exists
if (-not (Test-Path $inventoryFile)) {
    Write-Error "Inventory file $inventoryFile not found."
    exit 1
}

# Build extra vars
$extraVars = ""
if ($Tag) {
    $extraVars = "--extra-vars app_version=$Tag"
}

# Run Ansible playbook
Write-Host "Running deployment playbook..." -ForegroundColor Green
$command = "ansible-playbook -i $inventoryFile playbooks/site.yml $extraVars"
Write-Host "Executing: $command" -ForegroundColor Cyan

Invoke-Expression $command

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
} else {
    Write-Error "Deployment failed!"
    exit 1
}