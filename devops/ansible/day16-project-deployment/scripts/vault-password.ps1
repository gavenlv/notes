# Vault密码脚本 (PowerShell版本)

# 从环境变量获取
if ($env:ANSIBLE_VAULT_PASSWORD) {
    Write-Output $env:ANSIBLE_VAULT_PASSWORD
    exit 0
}

# 从文件读取（确保文件权限安全）
$vaultPasswordFile = ".\vault-password.txt"
if (Test-Path $vaultPasswordFile) {
    Get-Content $vaultPasswordFile
    exit 0
}

# 默认密码（仅用于开发环境）
Write-Output "dev-password"