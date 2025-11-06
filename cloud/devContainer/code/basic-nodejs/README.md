# 基础Node.js开发环境

这是DevContainer教程的第一个示例，演示如何配置基础的Node.js开发环境。

## 功能特性

- ✅ Node.js 18 运行环境
- ✅ Express.js Web框架
- ✅ ESLint代码检查
- ✅ Prettier代码格式化
- ✅ 自动端口转发(3000, 8080)
- ✅ 开发工具扩展自动安装

## 快速开始

1. 在VS Code中打开此目录
2. 按`Ctrl+Shift+P`，输入"Reopen in Container"
3. 等待容器构建完成
4. 运行 `npm run dev` 启动服务器
5. 访问 http://localhost:3000

## 文件说明

- `.devcontainer/devcontainer.json` - DevContainer配置文件
- `package.json` - Node.js项目配置
- `index.js` - 示例Express服务器
- `.eslintrc.js` - ESLint配置

## 学习要点

通过这个示例，你可以学习：

1. 基础DevContainer配置语法
2. 如何配置开发环境
3. 端口转发机制
4. 自动安装扩展和工具
5. 容器化开发的工作流程