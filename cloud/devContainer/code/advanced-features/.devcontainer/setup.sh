#!/bin/bash

# 高级特性设置脚本

echo "🚀 设置高级DevContainer环境..."

# 安装Node.js工具
npm install -g nodemon concurrently

# 安装Python工具
pip install --user pipenv black flake8

# 创建示例项目
mkdir -p examples

# 创建多语言项目示例
cat > examples/multi-language.md << 'EOF'
# 多语言开发环境示例

这个环境支持：
- Node.js 18
- Python 3.11
- Docker in Docker
- Git
- 开发工具

## 可用命令
- node --version
- python --version
- docker --version
- git --version
EOF

# 创建开发工具脚本
cat > dev-tools.sh << 'EOF'
#!/bin/bash

echo "=== 开发环境信息 ==="
echo "Node.js: $(node --version)"
echo "Python: $(python --version)"
echo "Docker: $(docker --version)"
echo "Git: $(git --version)"
echo "=================="
EOF

chmod +x dev-tools.sh

echo "✅ 高级环境设置完成！"
./dev-tools.sh