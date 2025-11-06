#!/bin/bash
# 创建自定义Chart

# 创建新的Chart
helm create my-webapp

# 查看生成的Chart结构
ls -la my-webapp/

# 验证Chart格式
helm lint my-webapp/

# 在本地渲染模板查看效果（不安装）
helm template my-webapp ./my-webapp/

echo "Chart创建完成，您可以开始定制您的应用"