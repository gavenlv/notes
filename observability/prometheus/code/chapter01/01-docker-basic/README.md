# Prometheus Docker基础示例

这是最简单的Prometheus Docker运行方式。

## 快速开始

### 1. 启动Prometheus

```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest
```

**Windows PowerShell:**
```powershell
docker run -d `
  --name prometheus `
  -p 9090:9090 `
  -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml `
  prom/prometheus:latest
```

### 2. 访问Prometheus

打开浏览器：http://localhost:3000

**默认凭据：**
- 用户名：`admin`
- 密码：`admin`（首次登录会要求修改）

### 3. 停止Prometheus

```bash
docker stop prometheus
docker rm prometheus
```

## 配置说明

`prometheus.yml` 包含：
- **global**：全局配置（采集间隔、评估间隔、外部标签）
- **scrape_configs**：抓取配置（监控Prometheus自身）

## 验证

访问 http://localhost:9090/targets 查看目标状态。

执行查询：
```promql
prometheus_build_info
up
```

## 常用命令

```bash
# 查看日志
docker logs prometheus

# 查看日志（实时）
docker logs -f prometheus

# 重启容器
docker restart prometheus

# 进入容器
docker exec -it prometheus sh

# 检查配置
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
```
