#!/bin/bash
# Helm安装脚本

# 对于Windows用户，建议使用Chocolatey:
# choco install kubernetes-helm

# 对于macOS用户，使用Homebrew:
# brew install helm

# 对于Linux用户，使用官方脚本:
# curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo "Helm安装完成"
echo "验证安装:"
helm version