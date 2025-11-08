# 简单Web应用示例

这是Skaffold教程的第一个示例，展示如何创建一个简单的Web应用并使用Skaffold进行自动化构建和部署。

## 项目结构

```
simple-web-app/
├── app.py                 # Flask应用代码
├── requirements.txt       # Python依赖
├── Dockerfile           # Docker镜像构建文件
├── k8s/                 # Kubernetes资源配置
│   ├── deployment.yaml  # 部署配置
│   └── service.yaml     # 服务配置
└── skaffold.yaml       # Skaffold配置文件
```

## 应用说明

这是一个简单的Flask Web应用，提供：
- 根路径 `/`：显示欢迎信息和版本
- 健康检查 `/health`：返回应用健康状态

## 快速开始

### 1. 前置要求

确保已安装：
- Skaffold
- Docker
- Kubernetes集群（如Minikube）
- kubectl

### 2. 启动应用

```bash
# 进入项目目录
cd simple-web-app

# 启动Skaffold开发模式
skaffold dev
```

Skaffold将自动：
1. 构建Docker镜像
2. 部署到Kubernetes集群
3. 监听文件变更并自动重新构建部署
4. 设置端口转发

### 3. 测试应用

在另一个终端中测试应用：

```bash
# 测试根路径
curl http://localhost:5000

# 测试健康检查
curl http://localhost:5000/health
```

### 4. 修改代码测试热重载

尝试修改 `app.py` 中的返回信息，Skaffold会自动检测变更并重新部署。

## 详细说明

### app.py

```python
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    version = os.getenv('VERSION', '1.0.0')
    return f'Hello from Skaffold! Version: {version}'

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

ENV FLASK_APP=app.py
ENV VERSION=1.0.0

EXPOSE 5000

CMD ["python", "app.py"]
```

### skaffold.yaml

```yaml
apiVersion: skaffold/v4beta7
kind: Config
metadata:
  name: simple-web-app

build:
  artifacts:
  - image: simple-web-app
    docker:
      dockerfile: Dockerfile

  tagPolicy:
    gitCommit: {}

deploy:
  kubectl:
    manifests:
    - k8s/deployment.yaml
    - k8s/service.yaml

portForward:
- resourceType: deployment
  resourceName: simple-web-app
  port: 5000
  localPort: 5000
```

## 高级功能

### 调试模式

```bash
# 启用详细日志
skaffold dev -v debug

# 只构建不部署
skaffold build

# 只部署不构建
skaffold deploy
```

### 清理资源

```bash
# 停止开发模式并清理资源
skaffold delete
```

## 故障排除

### 常见问题

1. **端口被占用**：修改 `skaffold.yaml` 中的 `localPort`
2. **镜像构建失败**：检查Dockerfile语法
3. **部署失败**：检查Kubernetes集群状态

### 调试技巧

```bash
# 查看应用日志
kubectl logs -l app=simple-web-app

# 查看Pod状态
kubectl get pods

# 检查服务
kubectl get services
```

## 下一步

掌握这个基础示例后，可以继续学习：
1. 多组件应用（code/01-basic-concepts/multi-artifacts/）
2. 开发模式优化（code/01-basic-concepts/dev-mode/）
3. 配置文件详解（code/02-configuration/）