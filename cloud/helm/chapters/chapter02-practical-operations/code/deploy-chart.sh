#!/bin/bash

# 部署自定义Web应用Chart的脚本

echo "开始部署my-webapp Chart..."

# 1. 验证Chart格式
echo "1. 验证Chart格式..."
helm lint my-webapp

# 2. 本地渲染模板（不部署）
echo "2. 本地渲染模板..."
helm template my-webapp ./my-webapp

# 3. 安装Chart到Kubernetes集群
echo "3. 安装Chart到Kubernetes集群..."
helm install my-webapp ./my-webapp

# 4. 查看部署状态
echo "4. 查看部署状态..."
helm list

# 5. 获取Release状态详情
echo "5. 获取Release状态详情..."
helm status my-webapp

echo "Chart部署完成！"