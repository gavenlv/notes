#requires -version 5.1
<#
.SYNOPSIS
    Ansible Vault 管理脚本
.DESCRIPTION
    此脚本提供 Ansible Vault 文件的批量管理功能
.EXAMPLE
    .\vault_manager.ps1 -Action Encrypt -Path "C:\ansible\secrets"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Encrypt", "Decrypt", "View", "Rekey")]
    [string]$Action,
    
    [Parameter(Mandatory=$true)]
    [string]$Path,
    
    [string]$VaultId
)

function Invoke-AnsibleVault {
    param(
        [string]$Action,
        [string]$FilePath,
        [string]$VaultId
    )
    
    $vaultCmd = "ansible-vault"
    $args = @()
    
    switch ($Action) {
        "Encrypt" {
            $args = @("encrypt", $FilePath)
        }
        "Decrypt" {
            $args = @("decrypt", $FilePath)
        }
        "View" {
            $args = @("view", $FilePath)
        }
        "Rekey" {
            $args = @("rekey", $FilePath)
        }
    }
    
    if ($VaultId) {
        $args += "--vault-id"
        $args += $VaultId
    }
    
    try {
        & $vaultCmd $args
        Write-Host "成功执行 $Action 操作于 $FilePath" -ForegroundColor Green
    }
    catch {
        Write-Error "执行 $Action 操作失败: $_"
    }
}

# 主要逻辑
if (Test-Path $Path) {
    $files = Get-ChildItem -Path $Path -Recurse -File | Where-Object { $_.Extension -eq ".yml" -or $_.Extension -eq ".yaml" }
    
    foreach ($file in $files) {
        Write-Host "处理文件: $($file.FullName)" -ForegroundColor Yellow
        Invoke-AnsibleVault -Action $Action -FilePath $file.FullName -VaultId $VaultId
    }
} else {
    Write-Error "路径 $Path 不存在"
}