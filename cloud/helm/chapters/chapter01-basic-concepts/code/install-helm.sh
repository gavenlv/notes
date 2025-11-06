#!/bin/bash

# Helm安装脚本 - 支持多种操作系统

echo "开始安装Helm..."

# 检测操作系统类型
OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == "Linux" ]]; then
    echo "检测到Linux系统"
    # 使用官方脚本安装
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
elif [[ "$OS_TYPE" == "Darwin" ]]; then
    echo "检测到macOS系统"
    # 使用Homebrew安装
    brew install helm
elif [[ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]] || [[ "$(expr substr $(uname -s) 1 9)" == "CYGWIN_NT" ]]; then
    echo "检测到Windows系统 (Git Bash)"
    # 使用Chocolatey安装
    choco install kubernetes-helm
else
    echo "未识别的操作系统类型: $OS_TYPE"
    echo "请参考Helm官方文档手动安装: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo "Helm安装完成！"

# 验证安装
echo "验证Helm安装..."
helm version

if [ $? -eq 0 ]; then
    echo "Helm安装成功！"
else
    echo "Helm安装失败，请检查错误信息。"
    exit 1
fi