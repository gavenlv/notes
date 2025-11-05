#!/bin/bash

# Vault密码脚本
# 在实际使用中，应该从安全的地方获取密码，例如：
# 1. 环境变量
# 2. 密钥管理服务
# 3. 加密的密码文件

# 示例：从环境变量获取
if [[ -n "$ANSIBLE_VAULT_PASSWORD" ]]; then
    echo "$ANSIBLE_VAULT_PASSWORD"
    exit 0
fi

# 示例：从文件读取（确保文件权限安全）
VAULT_PASSWORD_FILE="./vault-password.txt"
if [[ -f "$VAULT_PASSWORD_FILE" ]]; then
    cat "$VAULT_PASSWORD_FILE"
    exit 0
fi

# 默认密码（仅用于开发环境）
echo "dev-password"