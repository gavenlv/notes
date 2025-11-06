# 基础Chart示例

## 📋 示例说明

这是Helm学习的基础Chart示例，对应教程的第1-2章内容。通过这个示例，你将学习到：

- Helm Chart的基本结构
- 模板语法和函数使用
- Values配置管理
- 基本的Kubernetes资源部署

## 🏗️ 项目结构

```
basic-chart/
├── Chart.yaml          # Chart元数据
├── values.yaml         # 默认配置值
├── templates/          # 模板文件目录
│   ├── _helpers.tpl   # 模板助手函数
│   ├── deployment.yaml # 部署模板
│   └── service.yaml   # 服务模板
└── README.md          # 本文件
```

## 🚀 快速开始

### 1. 环境准备

确保你已经安装了以下工具：
- Kubernetes集群（Minikube、Kind或云平台）
- Helm 3.8+ 版本
- kubectl命令行工具

### 2. 验证Chart语法

```bash
# 进入Chart目录
cd basic-chart

# 验证Chart语法
helm lint

# 输出应该显示：1 chart(s) linted, 0 chart(s) failed
```

### 3. 渲染模板预览

```bash
# 预览生成的Kubernetes资源
helm template my-release .

# 输出将显示所有生成的YAML资源
```

### 4. 部署到集群

```bash
# 部署应用
helm install my-release .

# 输出示例：
# NAME: my-release
# LAST DEPLOYED: Mon Jan 01 00:00:00 2023
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
```

### 5. 验证部署

```bash
# 查看发布状态
helm list

# 查看Pod状态
kubectl get pods -l app.kubernetes.io/name=basic-webapp

# 查看服务状态
kubectl get svc -l app.kubernetes.io/name=basic-webapp
```

### 6. 测试应用

```bash
# 端口转发到本地
kubectl port-forward svc/my-release-basic-webapp 8080:80

# 在浏览器中访问 http://localhost:8080
# 或使用curl测试
curl http://localhost:8080
```

### 7. 清理部署

```bash
# 卸载发布
helm uninstall my-release

# 确认资源已清理
kubectl get pods -l app.kubernetes.io/name=basic-webapp
```

## 🔧 配置说明

### Values文件结构

`values.yaml` 文件包含了所有可配置的参数：

```yaml
# 基础配置
replicaCount: 1          # Pod副本数量
image:
  repository: nginx      # 镜像仓库
  tag: ""                # 镜像标签（默认为Chart appVersion）

# 服务配置
service:
  type: ClusterIP        # 服务类型
  port: 80              # 服务端口

# 资源限制
resources: {}           # CPU和内存限制

# 自动扩缩容
autoscaling:
  enabled: false        # 是否启用自动扩缩容
```

### 自定义配置示例

```bash
# 使用自定义配置部署
helm install my-release . \
  --set replicaCount=3 \
  --set image.tag=1.21 \
  --set service.type=NodePort

# 使用values文件部署
helm install my-release . -f my-values.yaml
```

## 🧪 实验练习

### 练习1：基础部署

1. 使用默认配置部署应用
2. 验证应用正常运行
3. 测试端口转发访问
4. 查看生成的Kubernetes资源

### 练习2：配置修改

1. 修改副本数量为2
2. 更改服务类型为NodePort
3. 设置资源限制
4. 重新部署并验证更改

### 练习3：高级功能

1. 启用自动扩缩容
2. 配置环境变量
3. 启用ConfigMap和Secret
4. 测试所有功能

## 📚 学习要点

### 模板语法
- `{{ .Values.replicaCount }}` - 引用Values中的值
- `{{ include "basic-webapp.fullname" . }}` - 使用命名模板
- `{{- if .Values.autoscaling.enabled }}` - 条件判断

### 助手函数
- `_helpers.tpl` 包含可重用的模板函数
- 命名模板通过 `define` 和 `include` 使用
- 标签选择器确保资源正确关联

### 资源管理
- Deployment管理Pod副本
- Service暴露应用服务
- 可选的Ingress、ConfigMap、Secret等资源

## 🔍 故障排除

### 常见问题

1. **Chart验证失败**
   ```bash
   # 检查语法错误
   helm lint
   
   # 查看详细错误信息
   helm template my-release . --debug
   ```

2. **部署失败**
   ```bash
   # 查看发布状态
   helm status my-release
   
   # 查看Pod事件
   kubectl describe pod <pod-name>
   
   # 查看Pod日志
   kubectl logs <pod-name>
   ```

3. **服务无法访问**
   ```bash
   # 检查服务状态
   kubectl get svc
   
   # 检查端点
   kubectl get endpoints
   
   # 测试服务连接
   kubectl port-forward svc/<service-name> 8080:80
   ```

### 调试技巧

```bash
# 详细输出部署过程
helm install my-release . --dry-run --debug

# 查看生成的资源清单
helm get manifest my-release

# 查看配置值
helm get values my-release
```

## 📈 下一步学习

完成这个基础示例后，你可以：

1. **继续学习**：进入 `advanced-chart/` 目录学习高级特性
2. **实践扩展**：尝试修改配置，添加新功能
3. **实际应用**：将学到的知识应用到实际项目中

---

**💡 提示：这个示例是学习Helm的起点，建议完全理解后再进行更复杂的学习。**