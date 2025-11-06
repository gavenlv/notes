# 全栈应用开发环境

这个示例演示如何使用DevContainer配置一个完整的多服务全栈应用开发环境，包含前端、后端和数据库。

## 功能特性

- ✅ 多服务架构（前端、后端、数据库）
- ✅ Docker Compose编排
- ✅ Vue 3 + Vite前端
- ✅ Node.js + Express后端
- ✅ PostgreSQL数据库
- ✅ 热重载开发环境
- ✅ 自动端口转发

## 快速开始

1. 在VS Code中打开此目录
2. 按`Ctrl+Shift+P`，输入"Reopen in Container"
3. 等待容器构建完成（首次构建需要一些时间）
4. 所有服务会自动启动
5. 访问 http://localhost:3000 查看前端应用
6. 访问 http://localhost:5000/health 检查后端健康状态

## 文件说明

- `.devcontainer/devcontainer.json` - 主要配置文件
- `.devcontainer/docker-compose.yml` - 多服务编排配置
- `.devcontainer/Dockerfile` - 后端服务Dockerfile
- `server.js` - 后端API服务器
- `client/` - 前端Vue应用
- `package.json` - 后端依赖配置

## 服务架构

```
前端 (Vue 3)    →   后端 (Node.js)    →   数据库 (PostgreSQL)
  ↓                    ↓                       ↓
localhost:3000    localhost:5000         localhost:5432
```

## 学习要点

通过这个示例，你可以学习：

1. 多服务DevContainer配置
2. Docker Compose编排技巧
3. 前后端分离架构
4. 数据库服务集成
5. 服务间通信和依赖管理
6. 开发环境的热重载配置

## 开发流程

- 前端修改自动热重载
- 后端修改自动重启
- 数据库数据持久化
- 所有服务在统一环境中运行