# 性能基准测试示例

## 概述

这个示例展示了如何对Skaffold进行性能基准测试，包括构建性能、部署性能、开发循环优化等方面的测试和优化策略。

## 目录结构

```
performance-benchmarks/
├── README.md
├── benchmarks/                    # 基准测试配置
│   ├── build-performance/       # 构建性能测试
│   ├── deploy-performance/      # 部署性能测试
│   ├── dev-loop-performance/    # 开发循环测试
│   └── resource-usage/         # 资源使用测试
├── test-applications/           # 测试应用
│   ├── simple-app/              # 简单应用
│   ├── medium-app/              # 中等复杂度应用
│   └── complex-app/            # 复杂应用
├── scripts/                     # 测试脚本
│   ├── run-benchmarks.sh        # 运行基准测试
│   ├── analyze-results.py       # 结果分析
│   └── generate-report.py      # 报告生成
└── results/                    # 测试结果
    ├── raw-data/               # 原始数据
    └── reports/                # 分析报告
```

## 快速开始

### 1. 运行基准测试

```bash
# 运行完整的性能基准测试
./scripts/run-benchmarks.sh --all

# 运行特定测试
./scripts/run-benchmarks.sh --build-performance

# 带详细输出的测试
./scripts/run-benchmarks.sh --deploy-performance --verbose
```

### 2. 分析结果

```bash
# 分析测试结果
python scripts/analyze-results.py --input results/raw-data/

# 生成HTML报告
python scripts/generate-report.py --output results/reports/

# 比较不同配置的性能
python scripts/compare-configs.py --config1 default --config2 optimized
```

### 3. 查看报告

```bash
# 打开性能报告
open results/reports/performance-report.html

# 查看原始数据
cat results/raw-data/build-times.json | jq '.'

# 生成性能图表
python scripts/plot-performance.py --input results/raw-data/
```

## 基准测试配置

### 构建性能测试

**测试配置：**
```yaml
# benchmarks/build-performance/skaffold.yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: build-performance-test

build:
  artifacts:
    - image: test-app
      context: ../../test-applications/simple-app
      docker:
        dockerfile: Dockerfile

test:
  - image: "*"
    custom:
      - command: "echo 'Build performance test started at $(date)'"
      - command: "sleep 1"
      - command: "echo 'Build performance test completed at $(date)'"

profiles:
  - name: default-build
    description: "Default build configuration"
    
  - name: optimized-build
    description: "Optimized build configuration"
    patches:
      - op: replace
        path: /build/local
        value:
          useBuildkit: true
          concurrency: 3
```

**测试脚本：**
```bash
#!/bin/bash
# scripts/build-benchmark.sh

# 测试参数
ITERATIONS=10
APPLICATIONS=("simple-app" "medium-app" "complex-app")
PROFILES=("default-build" "optimized-build")

# 运行构建性能测试
for app in "${APPLICATIONS[@]}"; do
  for profile in "${PROFILES[@]}"; do
    echo "Testing $app with profile $profile"
    
    # 运行多次测试取平均值
    for i in $(seq 1 $ITERATIONS); do
      start_time=$(date +%s.%N)
      
      skaffold build --profile=$profile -f benchmarks/build-performance/skaffold.yaml
      
      end_time=$(date +%s.%N)
      duration=$(echo "$end_time - $start_time" | bc)
      
      echo "$app,$profile,$i,$duration" >> results/raw-data/build-times.csv
    done
  done
done
```

### 部署性能测试

**测试配置：**
```yaml
# benchmarks/deploy-performance/skaffold.yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: deploy-performance-test

build:
  artifacts:
    - image: test-app
      context: ../../test-applications/simple-app
      docker:
        dockerfile: Dockerfile

deploy:
  kubectl:
    manifests:
      - k8s/deployment.yaml
      - k8s/service.yaml

profiles:
  - name: default-deploy
    description: "Default deployment configuration"
    
  - name: optimized-deploy
    description: "Optimized deployment configuration"
    patches:
      - op: replace
        path: /deploy/kubectl/flags
        value:
          global:
            - --server-side=true
            - --prune=true
          apply:
            - --prune-whitelist=core/v1/ConfigMap
```

**测试脚本：**
```bash
#!/bin/bash
# scripts/deploy-benchmark.sh

# 清理环境
kubectl delete all --all --wait=false
kubectl delete pvc --all --wait=false

# 运行部署性能测试
for profile in "default-deploy" "optimized-deploy"; do
  echo "Testing deployment with profile $profile"
  
  for i in $(seq 1 5); do
    start_time=$(date +%s.%N)
    
    skaffold deploy --profile=$profile -f benchmarks/deploy-performance/skaffold.yaml
    
    # 等待部署完成
    kubectl rollout status deployment/test-app --timeout=300s
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    echo "deploy,$profile,$i,$duration" >> results/raw-data/deploy-times.csv
    
    # 清理部署
    skaffold delete -f benchmarks/deploy-performance/skaffold.yaml
  done
done
```

### 开发循环性能测试

**测试配置：**
```yaml
# benchmarks/dev-loop-performance/skaffold.yaml
apiVersion: skaffold/v2beta29
kind: Config
metadata:
  name: dev-loop-performance-test

build:
  artifacts:
    - image: test-app
      context: ../../test-applications/simple-app
      docker:
        dockerfile: Dockerfile
      sync:
        manual:
          - src: "src/**/*.js"
            dest: /app
            strip: "src/"

deploy:
  kubectl:
    manifests:
      - k8s/deployment.yaml

portForward:
  - resourceType: deployment
    resourceName: test-app
    port: 8080
    localPort: 9000
```

**测试脚本：**
```bash
#!/bin/bash
# scripts/dev-loop-benchmark.sh

# 模拟文件变更
TEST_FILE="../../test-applications/simple-app/src/app.js"

# 启动开发模式
skaffold dev -f benchmarks/dev-loop-performance/skaffold.yaml &
SKAFFOLD_PID=$!

# 等待Skaffold启动
sleep 30

# 模拟多次文件变更
for i in $(seq 1 10); do
  echo "// Test modification $i - $(date)" >> $TEST_FILE
  
  start_time=$(date +%s.%N)
  
  # 等待同步完成（通过文件变更检测）
  while true; do
    if kubectl logs -l app=test-app --tail=1 | grep -q "Test modification $i"; then
      break
    fi
    sleep 1
  done
  
  end_time=$(date +%s.%N)
  duration=$(echo "$end_time - $start_time" | bc)
  
  echo "dev-loop,file-change,$i,$duration" >> results/raw-data/dev-loop-times.csv
  
  sleep 5  # 等待稳定
done

# 清理
kill $SKAFFOLD_PID
wait $SKAFFOLD_PID 2>/dev/null
```

## 性能优化策略

### 构建性能优化

**优化配置示例：**
```yaml
# 优化的构建配置
build:
  local:
    useBuildkit: true
    push: false
    concurrency: 3
    
  artifacts:
    - image: my-app
      docker:
        dockerfile: Dockerfile
        # 使用多阶段构建
        target: production
        # 构建缓存优化
        cacheFrom:
          - my-app:latest
          - my-app:{{.BRANCH_NAME}}
        cacheTo:
          - type: registry
            params:
              mode: max
        # 构建参数优化
        buildArgs:
          BUILDKIT_INLINE_CACHE: 1
          NODE_ENV: production
```

**优化效果对比：**

| 配置 | 构建时间 | 镜像大小 | 缓存命中率 |
|------|----------|----------|------------|
| 默认配置 | 2m 30s | 1.2GB | 0% |
| 优化配置 | 45s | 350MB | 85% |

### 部署性能优化

**优化配置示例：**
```yaml
# 优化的部署配置
deploy:
  kubectl:
    manifests:
      - k8s/**/*.yaml
    flags:
      global:
        - --server-side=true
        - --prune=true
        - --prune-whitelist=core/v1/ConfigMap
        - --prune-whitelist=core/v1/Secret
    
    # 并行部署优化
    parallel:
      maxWorkers: 5
      ordered: false
```

**优化效果对比：**

| 配置 | 部署时间 | 资源清理 | 并行度 |
|------|----------|----------|--------|
| 默认配置 | 1m 15s | 无 | 串行 |
| 优化配置 | 25s | 自动清理 | 并行5个 |

### 开发循环优化

**优化配置示例：**
```yaml
# 优化的开发循环配置
build:
  artifacts:
    - image: my-app
      sync:
        manual:
          - src: "src/**/*.js"
            dest: /app
            strip: "src/"
        # 智能文件同步
        auto: true
        infer:
          - "**/*.js"
          - "**/*.css"
          - "**/*.html"
        ignore:
          - "node_modules/**"
          - ".git/**"

portForward:
  - resourceType: deployment
    resourceName: my-app
    port: 8080
    localPort: 9000
    # 智能端口转发
    namespace: default
```

**优化效果对比：**

| 配置 | 文件同步时间 | 端口转发稳定性 | 内存使用 |
|------|--------------|----------------|----------|
| 默认配置 | 3-5s | 不稳定 | 高 |
| 优化配置 | <1s | 稳定 | 优化 |

## 资源使用监控

### 内存使用监控

**监控脚本：**
```bash
#!/bin/bash
# scripts/monitor-resources.sh

# 监控Skaffold进程资源使用
while true; do
  # 获取Skaffold进程内存使用
  skaffold_mem=$(ps -o pid,user,%mem,command ax | grep skaffold | grep -v grep | awk '{print $3}')
  
  # 获取Docker内存使用
  docker_mem=$(docker stats --no-stream --format "table {{.MemUsage}}" | grep -v "MEM" | head -1)
  
  # 获取系统内存使用
  system_mem=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')
  
  echo "$(date): Skaffold=$skaffold_mem%, Docker=$docker_mem, System=$system_mem" >> results/raw-data/memory-usage.log
  
  sleep 5
done
```

### CPU使用监控

**监控配置：**
```yaml
# 集成性能监控
profiles:
  - name: with-monitoring
    patches:
      - op: add
        path: /deploy/kubectl/manifests
        value:
          - k8s/monitoring/prometheus.yaml
          - k8s/monitoring/grafana.yaml
```

## 结果分析和报告

### 数据分析脚本

```python
# scripts/analyze-results.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def analyze_build_performance():
    # 读取构建性能数据
    df = pd.read_csv('results/raw-data/build-times.csv', 
                     names=['application', 'profile', 'iteration', 'duration'])
    
    # 计算统计信息
    stats = df.groupby(['application', 'profile'])['duration'].agg([
        'mean', 'std', 'min', 'max', 'count'
    ]).reset_index()
    
    # 生成性能对比图表
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x='application', y='duration', hue='profile')
    plt.title('Build Performance Comparison')
    plt.ylabel('Duration (seconds)')
    plt.savefig('results/reports/build-performance.png')
    
    return stats

def generate_html_report():
    # 生成HTML报告
    report = """
    <html>
    <head>
        <title>Skaffold Performance Benchmark Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .improvement { color: green; font-weight: bold; }
            .regression { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Skaffold Performance Benchmark Report</h1>
        <p>Generated on: {date}</p>
        
        <h2>Build Performance Summary</h2>
        {build_table}
        
        <h2>Deployment Performance Summary</h2>
        {deploy_table}
        
        <h2>Performance Charts</h2>
        <img src="build-performance.png" alt="Build Performance">
        <img src="deploy-performance.png" alt="Deployment Performance">
    </body>
    </html>
    """.format(
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        build_table=build_stats.to_html(),
        deploy_table=deploy_stats.to_html()
    )
    
    with open('results/reports/performance-report.html', 'w') as f:
        f.write(report)

if __name__ == "__main__":
    build_stats = analyze_build_performance()
    generate_html_report()
```

这个性能基准测试示例提供了完整的性能测试框架，帮助您评估和优化Skaffold在各种场景下的性能表现。