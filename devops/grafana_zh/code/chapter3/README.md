# 第3章：仪表板创建和面板配置 - 代码示例

## 概述

本目录包含第3章教程的完整可运行代码示例，演示如何创建和配置Grafana仪表板及各种面板类型。

## 快速开始

### 1. 启动服务

```bash
# 进入chapter3目录
cd chapter3

# 启动Grafana和测试数据生成器
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 2. 访问Grafana

- **URL**: http://localhost:3000
- **用户名**: admin
- **密码**: admin123

### 3. 生成测试数据

测试数据生成器会自动运行，生成模拟的监控数据：

```bash
# 查看数据生成器日志
docker-compose logs testdata-generator
```

## 仪表板示例

### 基础仪表板创建

1. **创建新仪表板**: 左侧菜单 → Create → Dashboard
2. **添加面板**: 点击"Add new panel"
3. **配置数据源**: 选择"TestData"数据源
4. **选择场景**: 使用不同的测试数据场景

### 面板类型示例

#### 统计面板 (Stat)

- **用途**: 显示单个重要指标
- **示例**: CPU使用率、内存使用率
- **配置**: 数值显示、颜色阈值、背景颜色

#### 时间序列面板 (Time Series)

- **用途**: 显示时间序列数据趋势
- **示例**: 系统负载趋势、应用响应时间
- **配置**: 线条样式、点大小、图例位置

#### 表格面板 (Table)

- **用途**: 以表格形式显示数据
- **示例**: 应用性能指标、错误统计
- **配置**: 列排序、颜色编码、链接

#### 仪表盘面板 (Gauge)

- **用途**: 类似汽车仪表盘的显示
- **示例**: 磁盘使用率、服务健康度
- **配置**: 阈值范围、颜色渐变、单位显示

#### 饼图面板 (Pie Chart)

- **用途**: 显示各部分占比
- **示例**: 流量分布、错误类型分布
- **配置**: 饼图样式、标签显示、颜色主题

## 面板配置示例

### 统计面板配置

```json
{
  "targets": [
    {
      "datasource": "TestData",
      "scenarioId": "random_walk",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "color": {
        "mode": "thresholds"
      },
      "thresholds": {
        "steps": [
          {"color": "green", "value": null},
          {"color": "red", "value": 80}
        ]
      },
      "unit": "percent"
    }
  }
}
```

### 时间序列面板配置

```json
{
  "targets": [
    {
      "datasource": "TestData", 
      "scenarioId": "random_walk",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "drawStyle": "line",
        "lineInterpolation": "linear",
        "barAlignment": 0,
        "lineWidth": 1,
        "fillOpacity": 10,
        "gradientMode": "none",
        "spanNulls": false
      }
    }
  }
}
```

## 高级功能

### 变量使用

创建仪表板变量实现动态过滤：

1. **仪表板设置** → Variables
2. **添加变量**: 
   - Name: `application`
   - Type: Query
   - Query: `web-api,auth-service,database-service,cache-service`

### 面板链接

配置面板链接实现导航：

1. **面板编辑** → Links
2. **添加链接**:
   - Title: "查看详情"
   - URL: `/d/another-dashboard`
   - Open in new tab: true

### 告警集成

在面板中集成告警：

1. **面板编辑** → Alert
2. **配置告警规则**:
   - Condition: when avg() of query(A) is above 80
   - Evaluate every: 1m
   - For: 5m

## 示例仪表板

### 系统监控仪表板

包含以下面板：
- CPU使用率统计面板
- 内存使用趋势图
- 磁盘空间仪表盘
- 网络流量表格

### 应用性能仪表板

包含以下面板：
- 响应时间趋势图
- 错误率统计
- 请求量分布饼图
- 性能指标表格

### 业务指标仪表板

包含以下面板：
- 收入趋势图
- 用户增长统计
- 转化率仪表盘
- 地域分布饼图

## 最佳实践

### 仪表板设计原则

1. **简洁明了**: 每个仪表板聚焦一个主题
2. **层次分明**: 重要指标放在显眼位置
3. **一致性**: 使用统一的颜色和样式
4. **可操作性**: 包含必要的交互功能

### 性能优化

1. **查询优化**: 限制查询时间范围
2. **面板数量**: 控制单个仪表板的面板数量
3. **数据聚合**: 使用数据源层面的聚合
4. **缓存配置**: 启用查询结果缓存

## 故障排除

### 面板显示异常

- 检查数据源连接
- 验证查询语法
- 确认时间范围设置
- 查看浏览器控制台错误

### 性能问题

- 减少面板数量
- 优化查询语句
- 增加查询间隔
- 启用数据缓存

### 样式问题

- 检查CSS配置
- 验证颜色设置
- 确认单位格式
- 测试不同浏览器

## 生产环境建议

1. **权限控制**: 设置适当的访问权限
2. **版本管理**: 使用Git管理仪表板配置
3. **备份策略**: 定期备份重要仪表板
4. **监控告警**: 监控仪表板使用情况

## 清理环境

```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（谨慎操作）
docker-compose down -v
```

## 下一步

完成本章节后，您可以继续：
1. 学习第4章：查询语言和数据处理
2. 创建复杂的多数据源仪表板
3. 探索高级面板功能和插件
4. 优化仪表板性能和用户体验