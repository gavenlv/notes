#!/bin/bash

# 创建自定义Chart的脚本

echo "开始创建自定义Web应用Chart..."

# 1. 创建Chart
echo "1. 创建名为my-webapp的Chart..."
helm create my-webapp

# 2. 查看Chart结构
echo "2. 查看Chart结构..."
ls -la my-webapp

# 3. 验证Chart格式
echo "3. 验证Chart格式..."
helm lint my-webapp

# 4. 本地渲染模板（不部署）
echo "4. 本地渲染模板..."
helm template my-webapp ./my-webapp

echo "Chart创建完成！接下来可以编辑Chart文件来自定义应用。"