# Skaffold 代码示例

本目录包含Skaffold教程中使用的所有代码示例，从基础到高级，涵盖各种构建和部署场景。

## 目录结构

```
code/
├── 01-basic-concepts/          # 第1章：基础概念代码示例
│   ├── simple-web-app/         # 简单Web应用
│   ├── multi-artifacts/        # 多组件应用
│   └── dev-mode/              # 开发模式示例
├── 02-configuration/           # 第2章：配置文件详解
│   ├── docker-builder/        # Docker构建器
│   ├── jib-builder/          # Jib构建器（Java）
│   ├── helm-deployment/      # Helm部署
│   └── kustomize-deployment/ # Kustomize部署
├── 03-build-system/           # 第3章：构建系统
│   ├── local-build/          # 本地构建
│   ├── cloud-build/          # 云构建
│   ├── kaniko/               # Kaniko构建
│   └── build-optimization/   # 构建优化
├── 04-deployment-strategies/  # 第4章：部署策略
│   ├── multi-env/            # 多环境部署
│   ├── blue-green/          # 蓝绿部署
│   └── canary/              # 金丝雀部署
├── 05-testing-validation/     # 第5章：测试和验证
│   ├── structure-tests/      # 结构测试
│   ├── integration-tests/    # 集成测试
│   └── custom-tests/         # 自定义测试
├── 06-advanced-features/      # 第6章：高级特性
│   ├── file-sync/           # 文件同步
│   ├── port-forwarding/     # 端口转发
│   └── debugging/           # 调试支持
├── 07-cicd-integration/      # 第7章：CI/CD集成
│   ├── jenkins/             # Jenkins集成
│   ├── gitlab-ci/           # GitLab CI集成
│   └── github-actions/      # GitHub Actions集成
└── 08-practical-project/     # 第8章：实战项目
    ├── microservices/       # 微服务项目
    └── production-ready/    # 生产就绪项目
```

## 运行说明

### 前置要求

1. **安装Skaffold**：参考第1章安装指南
2. **安装Docker**：确保Docker守护进程运行
3. **配置Kubernetes集群**：本地（如Minikube）或云集群
4. **必要的工具**：kubectl, helm, docker-compose等

### 运行示例

每个示例目录都包含完整的配置和说明：

```bash
# 进入示例目录
cd code/01-basic-concepts/simple-web-app

# 启动开发模式
skaffold dev

# 或构建和部署
skaffold run

# 清理资源
skaffold delete
```

### 环境变量配置

某些示例可能需要环境变量：

```bash
# 设置镜像仓库（如果需要推送镜像）
export DOCKER_REGISTRY=your-registry.example.com

# 设置Kubernetes上下文（如果有多个集群）
export KUBE_CONTEXT=your-cluster

# 设置环境变量
export ENV=development
```

## 代码质量

所有代码示例都遵循生产级别的标准：

- **安全性**：包含安全最佳实践
- **性能**：优化配置和构建策略
- **可维护性**：清晰的代码结构和注释
- **可扩展性**：易于修改和扩展

## 故障排除

### 常见问题

1. **镜像构建失败**：检查Dockerfile语法和依赖
2. **部署失败**：检查Kubernetes资源配置
3. **网络问题**：检查端口转发和防火墙设置

### 调试工具

```bash
# 查看详细日志
skaffold dev -v debug

# 诊断问题
skaffold diagnose

# 渲染配置文件
skaffold render --output rendered.yaml
```

## 贡献指南

如果您发现任何问题或有改进建议，欢迎提交Issue或Pull Request。

## 许可证

本代码示例遵循MIT许可证。

---

**开始探索Skaffold的强大功能吧！**