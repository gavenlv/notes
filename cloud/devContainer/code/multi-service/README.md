# 多服务微服务架构

这个示例演示如何使用DevContainer配置复杂的多服务微服务架构，包含网关、认证服务和API服务。

## 功能特性

- ✅ 微服务架构（网关、认证、API服务）
- ✅ 服务发现和负载均衡
- ✅ JWT认证机制
- ✅ PostgreSQL数据库
- ✅ Redis缓存
- ✅ 服务间通信
- ✅ 统一网关入口

## 快速开始

1. 在VS Code中打开此目录
2. 按`Ctrl+Shift+P`，输入"Reopen in Container"
3. 等待容器构建完成
4. 所有服务会自动启动
5. 访问 http://localhost:3000/health 检查网关状态

## 服务架构

```
客户端 → 网关服务 (3000) → 认证服务 (3001)
                    ↘ API服务 (3002)
                    ↘ PostgreSQL (5432)
                    ↘ Redis (6379)
```

## API端点

- `GET /health` - 网关健康检查
- `POST /auth/login` - 用户登录
- `POST /auth/verify` - 验证token
- `GET /api/products` - 获取产品列表
- `POST /api/products` - 创建产品

## 学习要点

通过这个示例，你可以学习：

1. 微服务架构设计
2. 网关模式实现
3. 服务间通信机制
4. 认证和授权实现
5. 多数据库配置
6. 缓存服务集成

## 开发流程

- 每个服务独立开发
- 通过网关统一访问
- 服务间通过内部网络通信
- 支持水平扩展