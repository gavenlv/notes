#!/bin/bash

# 管理复杂Chart依赖和Hooks的脚本

echo "开始管理复杂Chart的依赖和Hooks..."

# 1. 添加bitnami仓库
echo "1. 添加bitnami仓库..."
helm repo add bitnami https://charts.bitnami.com/bitnami

# 2. 更新仓库
echo "2. 更新仓库..."
helm repo update

# 3. 构建依赖
echo "3. 构建依赖..."
helm dependency build complex-app

# 4. 验证Chart
echo "4. 验证Chart..."
helm lint complex-app

# 5. 安装Chart（会触发Hooks）
echo "5. 安装Chart..."
helm install complex-app ./complex-app

# 6. 查看Hooks执行情况
echo "6. 查看Hooks执行情况..."
kubectl get jobs

echo "依赖管理和Hooks演示完成！"