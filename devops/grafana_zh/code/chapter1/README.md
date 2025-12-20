# 第1章：Grafana基础概念和安装 - 代码示例

## 概述

本目录包含第1章教程的完整可运行代码示例，帮助您快速搭建Grafana开发环境。

## 快速开始

### 1. 启动Grafana

```bash
# 进入chapter1目录
cd chapter1

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 2. 访问Grafana

- **URL**: http://localhost:3000
- **用户名**: admin
- **密码**: admin123

### 3. 验证安装

访问Grafana后，您应该能够：
- 登录到管理界面
- 查看默认的Home仪表板
- 访问数据源配置页面

## 文件说明

### docker-compose.yml

完整的Docker Compose配置，包含：
- Grafana主服务
- 测试数据生成器（演示用）
- 数据卷和网络配置

### grafana.ini

Grafana配置文件，包含：
- 基础服务配置
- 安全设置
- 日志配置
- 插件设置

## 扩展配置

### 添加数据源

在Grafana界面中添加测试数据源：

1. 左侧菜单 → Configuration → Data sources
2. 点击 "Add data source"
3. 选择 "TestData DB"
4. 配置名称："TestData"
5. 点击 "Save & Test"

### 创建示例仪表板

```bash
# 使用API创建示例仪表板
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(curl -X POST -H "Content-Type: application/json" -d '{"name":"apikey","role":"Admin"}' http://admin:admin123@localhost:3000/api/auth/keys | jq -r .key)" \
  -d '{
    "dashboard": {
      "id": null,
      "title": "示例仪表板",
      "tags": ["tutorial"],
      "timezone": "browser",
      "panels": [
        {
          "id": 1,
          "title": "CPU使用率",
          "type": "stat",
          "targets": [
            {
              "datasource": "TestData",
              "refId": "A",
              "scenarioId": "random_walk"
            }
          ]
        }
      ]
    },
    "overwrite": false
  }'
```

## 故障排除

### 端口冲突

如果3000端口被占用，修改`docker-compose.yml`：

```yaml
ports:
  - "3001:3000"  # 改为其他端口
```

### 权限问题

在Linux系统上，可能需要调整文件权限：

```bash
sudo chown -R 472:472 ./grafana_data/
```

### 内存不足

如果遇到内存问题，可以限制容器内存：

```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

## 生产环境建议

对于生产环境，建议：

1. 修改默认密码
2. 启用HTTPS
3. 使用PostgreSQL数据库
4. 配置备份策略
5. 设置监控和告警

## 清理环境

```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（谨慎操作）
docker-compose down -v
```

## 下一步

完成本章节后，您可以继续：
1. 学习第2章：数据源配置和连接
2. 探索Grafana的基本功能
3. 创建自己的第一个仪表板