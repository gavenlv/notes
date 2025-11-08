# 完整测试流水线示例

## 项目概述

这是一个完整的Skaffold测试流水线示例，演示如何实现从代码质量检查到部署验证的完整测试流程。

## 目录结构

```
complete-testing-pipeline/
├── README.md                    # 项目说明
├── skaffold.yaml                # 主配置文件
├── Dockerfile                   # 应用镜像构建
├── app/                         # 应用源码
│   ├── main.go
│   ├── handlers.go
│   └── models.go
├── tests/                       # 测试文件
│   ├── unit/                    # 单元测试
│   │   ├── handlers_test.go
│   │   └── models_test.go
│   ├── integration/             # 集成测试
│   │   ├── api_test.go
│   │   └── database_test.go
│   ├── e2e/                     # 端到端测试
│   │   └── e2e_test.go
│   ├── image/                   # 镜像测试
│   │   ├── structure-tests.yaml
│   │   └── security-scan.sh
│   └── deployment/              # 部署测试
│       ├── health-check.sh
│       ├── api-test.sh
│       └── load-test.js
├── scripts/                     # 辅助脚本
│   ├── setup-test-env.sh
│   ├── load-test-data.sh
│   └── cleanup.sh
├── k8s/                         # Kubernetes资源
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
└── test-data/                   # 测试数据
    ├── fixtures/
    └── sample-data.json
```

## 测试阶段

### 阶段1：代码质量检查
- **语法检查**：go vet, gofmt
- **代码规范**：golangci-lint
- **安全扫描**：安全检查工具

### 阶段2：单元测试
- **业务逻辑测试**：覆盖率 >= 80%
- **错误处理测试**：边界条件验证
- **性能基准测试**：性能基准

### 阶段3：镜像验证
- **结构测试**：镜像内容验证
- **安全扫描**：漏洞检查
- **性能测试**：启动时间验证

### 阶段4：部署验证
- **健康检查**：服务可用性
- **API测试**：功能验证
- **负载测试**：性能验证

## 测试配置

### 环境配置
```yaml
# 测试环境变量
TEST_DATABASE_URL: postgresql://test:test@localhost:5432/test
TEST_API_URL: http://localhost:8080
TEST_TIMEOUT: 300s
```

### 资源配额
```yaml
# 测试资源限制
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## 快速开始

1. **运行完整测试流水线**
   ```bash
   skaffold test
   ```

2. **运行特定测试阶段**
   ```bash
   # 仅运行代码质量检查
   skaffold test --module=code-quality
   
   # 仅运行单元测试
   skaffold test --module=unit-tests
   
   # 仅运行镜像验证
   skaffold test --module=image-validation
   ```

3. **跳过特定测试**
   ```bash
   # 跳过性能测试
   skaffold test --skip-tests=performance-tests
   ```

4. **调试测试**
   ```bash
   # 详细日志输出
   skaffold test --verbosity debug
   
   # 增加超时时间
   skaffold test --timeout=30m
   ```

## 测试报告

### 测试结果格式
```json
{
  "test_suite": "unit-tests",
  "passed": 45,
  "failed": 2,
  "skipped": 0,
  "coverage": 85.3,
  "duration": "2m15s"
}
```

### 质量门禁
- **代码覆盖率**：≥ 80%
- **测试通过率**：100%
- **安全扫描**：无高危漏洞
- **性能基准**：符合要求

## 自定义测试

### 添加新的测试类型
1. 在 `tests/` 目录下创建新的测试目录
2. 编写测试脚本或配置文件
3. 在 `skaffold.yaml` 中添加测试配置
4. 更新测试依赖和资源

### 测试环境配置
```bash
# 设置测试环境变量
export TEST_ENVIRONMENT=development
export TEST_DATABASE_URL=postgresql://test:test@localhost:5432/test

# 启动测试环境
./scripts/setup-test-env.sh
```

## 故障排除

### 常见问题
1. **测试超时**：增加超时时间或优化测试用例
2. **资源不足**：调整测试资源配额
3. **网络问题**：检查网络连接和防火墙设置
4. **依赖问题**：确保测试依赖正确安装

### 调试技巧
```bash
# 详细日志
skaffold test --verbosity debug

# 检查测试环境
kubectl get pods -n test-namespace

# 查看测试日志
kubectl logs -f test-pod -n test-namespace
```

## 性能优化

### 测试并行化
```yaml
test:
  - name: parallel-tests
    # 并行运行测试
    concurrency: 4
    commands:
      - command: go test -p 4 ./...
        dir: ./app
```

### 资源优化
```yaml
# 优化测试资源使用
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

## 最佳实践

1. **测试隔离**：每个测试用例独立运行
2. **数据清理**：测试后清理测试数据
3. **资源管理**：合理分配测试资源
4. **错误处理**：完善的错误处理机制
5. **报告生成**：清晰的测试结果报告