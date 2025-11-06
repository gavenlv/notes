# 第2章：Chart开发详解

## 🎯 本章目标

- 深入理解Chart的结构和组成
- 掌握模板语法和函数使用
- 学会values管理和配置覆盖
- 理解依赖管理和子Chart

## 📚 Chart结构详解

### 2.1 Chart标准结构

一个完整的Chart包含以下核心文件：

```
myapp-chart/
├── Chart.yaml          # Chart元数据
├── values.yaml         # 默认配置值
├── values.schema.json  # 配置验证模式（可选）
├── templates/          # 模板文件目录
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── _helpers.tpl    # 模板助手函数
│   └── tests/         # 测试文件
│       └── test-connection.yaml
├── charts/            # 依赖的子Chart
├── crds/              # 自定义资源定义（可选）
└── README.md          # Chart说明文档
```

### 2.2 Chart.yaml详解

**Chart.yaml** 是Chart的元数据文件，定义了Chart的基本信息：

```yaml
apiVersion: v2  # Chart API版本
name: myapp     # Chart名称
description: A Helm chart for Kubernetes
type: application  # Chart类型（application或library）
version: 0.1.0    # Chart版本（遵循语义化版本）
appVersion: 1.16.0 # 应用版本

# 依赖管理
dependencies:
  - name: mysql
    version: "8.8.26"
    repository: "https://charts.bitnami.com/bitnami"
    condition: mysql.enabled

# 维护者信息
maintainers:
  - name: your-name
    email: your-email@example.com

# Chart关键字（用于搜索）
keywords:
  - web
  - application
  - kubernetes

# 源文件链接
sources:
  - https://github.com/your-org/myapp

# 图标
icon: https://example.com/icon.png

# 注释
annotations:
  artifacthub.io/changes: |
    - "Initial release"
```

### 2.3 values.yaml详解

**values.yaml** 定义了Chart的默认配置值：

```yaml
# 全局配置
global:
  # 全局镜像拉取策略
  imagePullSecrets: []
  # 全局存储类
  storageClass: ""

# 副本数配置
replicaCount: 1

# 镜像配置
image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: ""

# 服务配置
service:
  type: ClusterIP
  port: 80

# 资源限制
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

# 自动扩缩容配置
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

# 节点选择器
nodeSelector: {}

# 容忍度配置
tolerations: []

# 亲和性配置
affinity: {}
```

## 🔧 模板语法深入

### 2.4 Go模板基础

Helm使用Go模板语言，支持变量、函数和控制结构：

#### 变量插值
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
```

#### 条件判断
```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Release.Name }}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Release.Name }}-deployment
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
{{- end }}
```

#### 循环结构
```yaml
{{- range .Values.imagePullSecrets }}
- name: {{ . }}
{{- end }}
```

### 2.5 模板函数

Helm提供了丰富的内置函数：

#### 字符串函数
```yaml
# 默认值
image: {{ .Values.image.tag | default "latest" }}

# 大写转换
name: {{ .Values.appName | upper }}

# 截取字符串
shortName: {{ .Values.appName | trunc 10 }}

# 替换字符
className: {{ .Values.appName | replace "-" "_" }}
```

#### 数学函数
```yaml
# 数学运算
replicas: {{ mul .Values.replicaCount 2 }}

# 加法
port: {{ add .Values.service.port 1000 }}
```

#### 日期和时间函数
```yaml
# 当前时间戳
annotations:
  deployTime: {{ now | date "2006-01-02 15:04:05" }}
```

#### 列表函数
```yaml
# 列表长度
{{ if gt (len .Values.envVars) 0 }}
env:
{{- range .Values.envVars }}
  - name: {{ .name }}
    value: {{ .value }}
{{- end }}
{{- end }}
```

### 2.6 模板助手函数

在 `_helpers.tpl` 中定义可重用的模板函数：

```tpl
{{/*
生成完整的应用名称
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
生成标签选择器
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
生成通用标签
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

## 🎛️ Values管理高级技巧

### 2.7 多环境配置管理

#### 环境特定的values文件
```bash
# 开发环境配置
values-dev.yaml
# 测试环境配置  
values-test.yaml
# 生产环境配置
values-prod.yaml
```

**values-dev.yaml**
```yaml
replicaCount: 1
image:
  tag: "latest"
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

**values-prod.yaml**
```yaml
replicaCount: 3
image:
  tag: "v1.0.0"
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
```

### 2.8 配置验证

使用JSON Schema验证values配置：

**values.schema.json**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10
    },
    "image": {
      "type": "object",
      "properties": {
        "repository": {
          "type": "string"
        },
        "tag": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9._-]+$"
        }
      },
      "required": ["repository"]
    }
  },
  "required": ["replicaCount", "image"]
}
```

## 📦 依赖管理

### 2.9 依赖声明

在Chart.yaml中声明依赖：

```yaml
dependencies:
  - name: postgresql
    version: "11.6.12"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    tags:
      - database
  - name: redis
    version: "16.8.8"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
    tags:
      - cache
```

### 2.10 依赖管理命令

```bash
# 下载依赖到charts目录
helm dependency update

# 构建依赖（生成Chart.lock）
helm dependency build

# 列出依赖
helm dependency list

# 下载依赖到特定目录
helm dependency update --dependency-update
```

## 🧪 实验：创建完整的Chart

### 实验1：创建基础Web应用Chart

```bash
# 创建Chart骨架
helm create my-webapp
cd my-webapp

# 查看生成的文件结构
tree .
```

**修改Chart.yaml**
```yaml
apiVersion: v2
name: my-webapp
description: A Helm chart for a simple web application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

**修改values.yaml**
```yaml
# 默认配置
replicaCount: 2

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "1.21"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix
```

### 实验2：模板开发和测试

```bash
# 模板语法检查
helm lint

# 渲染模板（预览生成的YAML）
helm template my-release .

# 渲染模板并保存到文件
helm template my-release . --output-dir ./rendered

# 安装到本地集群进行测试
helm install my-release . --dry-run --debug

# 实际部署
helm install my-release .

# 升级部署
helm upgrade my-release . --set replicaCount=3

# 查看部署状态
helm status my-release
```

### 实验3：values覆盖测试

```bash
# 使用values文件覆盖
helm install my-release . -f values-dev.yaml

# 命令行参数覆盖
helm install my-release . --set replicaCount=3 --set image.tag=latest

# 多文件覆盖（后面的文件优先级更高）
helm install my-release . -f values-base.yaml -f values-override.yaml

# 验证values配置
helm install my-release . --dry-run --debug --set invalid.config=test
```

## 📝 本章总结

### 关键知识点

1. **Chart结构**：标准文件组织和作用
2. **模板语法**：变量、条件、循环、函数
3. **Values管理**：多环境配置和验证
4. **依赖管理**：子Chart的声明和使用
5. **模板助手**：可重用的模板函数

### 实践技能

- ✅ 能够创建完整的Chart结构
- ✅ 掌握模板语法和函数使用
- ✅ 能够管理多环境配置
- ✅ 能够处理Chart依赖关系
- ✅ 能够进行模板测试和验证

### 最佳实践

1. **语义化版本**：遵循semver规范
2. **模板简化**：使用助手函数减少重复代码
3. **配置验证**：使用JSON Schema验证values
4. **文档完整**：提供清晰的README说明
5. **测试充分**：包含完整的测试用例

### 下一步学习

在下一章中，我们将深入学习Helm的高级特性和模板引擎，包括模板函数的高级用法、流程控制、命名模板等高级功能。

---

**💡 提示：完成本章学习后，建议进入 `code/advanced-chart/` 目录进行实践练习，巩固所学知识。**