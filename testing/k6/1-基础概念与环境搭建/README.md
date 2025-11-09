# 第1章：k6基础概念与环境搭建

## 1.1 什么是k6？

k6是一个开源的、现代化的性能测试工具，专注于开发者的体验和可维护性。与传统的性能测试工具不同，k6使用JavaScript作为脚本语言，使得测试脚本更加易于编写和维护。

### 核心特性

- **开发者友好**：使用JavaScript编写测试脚本
- **高性能**：基于Go语言开发，单机可模拟数十万用户
- **云原生**：支持Docker容器化部署
- **丰富的指标**：提供详细的性能指标和报告
- **CI/CD集成**：与GitLab、Jenkins等工具无缝集成

### 与传统工具对比

| 特性 | k6 | JMeter | Gatling |
|------|----|--------|---------|
| 脚本语言 | JavaScript | Java/Groovy | Scala |
| 学习曲线 | 平缓 | 陡峭 | 中等 |
| 性能 | 高 | 中 | 高 |
| 资源消耗 | 低 | 高 | 中 |
| 报告功能 | 丰富 | 基本 | 丰富 |

## 1.2 k6架构解析

### 核心组件

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   测试脚本      │───▶│    k6引擎       │───▶│   目标系统      │
│  (JavaScript)   │    │   (Go语言)      │    │  (Web服务)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   指标收集      │    │   虚拟用户      │    │   结果输出      │
│   (Metrics)    │    │   (VUs)        │    │   (Reports)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 关键概念

1. **虚拟用户（VUs）**：模拟真实用户的行为
2. **迭代（Iterations）**：每个虚拟用户执行的测试循环
3. **阈值（Thresholds）**：定义测试通过/失败的标准
4. **指标（Metrics）**：收集的性能数据（响应时间、错误率等）

## 1.3 环境搭建

### 安装方法

#### 方式一：二进制安装（推荐）

```bash
# Windows
scoop install k6

# macOS
brew install k6

# Linux
# Ubuntu/Debian
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# CentOS/RHEL
sudo dnf install https://dl.k6.io/rpm/repo.rpm
sudo dnf install k6
```

#### 方式二：Docker安装

```bash
# 拉取官方镜像
docker pull grafana/k6:latest

# 运行测试
docker run -i grafana/k6 run - <script.js
```

#### 方式三：包管理器

```bash
# npm (Node.js)
npm install -g k6

# yarn
yarn global add k6
```

### 验证安装

```bash
k6 version
```

输出类似：
```
k6 v0.50.0 ((devel), go1.21.0, darwin/arm64)
```

## 1.4 第一个k6测试

让我们创建一个简单的测试脚本来验证环境：

```javascript
// 1-first-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

// 测试配置
export const options = {
  vus: 1,          // 1个虚拟用户
  duration: '30s', // 测试持续30秒
};

// 默认函数 - 每个虚拟用户都会执行
export default function () {
  // 发送HTTP GET请求到测试服务器
  const response = http.get('https://httpbin.test.k6.io/get');
  
  // 验证响应
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // 等待1秒
  sleep(1);
}
```

运行测试：

```bash
k6 run 1-first-test.js
```

## 1.5 测试结果解读

运行测试后，您将看到类似以下的输出：

```
          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: 1-first-test.js
     output: -

  scenarios: (100.00%) 1 scenario, 1 max VUs, 1m0s max duration (incl. graceful stop):
           * default: 1 looping VUs for 30s (gracefulStop: 30s)


running (0m30.1s), 0/1 VUs, 30 complete and 0 interrupted iterations
default ✓ [ 100% ] 1 VUs  30s

     ✓ status is 200
     ✓ response time < 500ms

     checks.........................: 100.00% ✓ 60       ✗ 0
     data_received..................: 15 kB   498 B/s
     data_sent......................: 5.0 kB  166 B/s
     http_req_blocked...............: avg=18.75ms  min=1.73µs  med=5.5µs   max=562.88ms p(90)=562.88ms p(95)=562.88ms
     http_req_connecting............: avg=18.75ms  min=0s      med=0s      max=562.88ms p(90)=562.88ms p(95)=562.88ms
     http_req_duration..............: avg=223.8ms  min=219.85ms med=222.34ms max=237.66ms p(90)=230.42ms p(95)=234.04ms
       { expected_response:true }...: avg=223.8ms  min=219.85ms med=222.34ms max=237.66ms p(90)=230.42ms p(95)=234.04ms
     http_req_failed................: 0.00%   ✓ 0        ✗ 30
     http_req_receiving.............: avg=100.08µs min=74.29µs  med=96.35µs  max=202.35µs p(90)=129.15µs p(95)=165.75µs
     http_req_sending...............: avg=70.42µs  min=52.02µs  med=67.52µs  max=112.51µs p(90)=93.26µs  p(95)=102.88µs
     http_req_tls_handshaking.......: avg=0s       min=0s       med=0s       max=0s       p(90)=0s       p(95)=0s
     http_req_waiting...............: avg=223.63ms min=219.66ms med=222.18ms max=237.5ms  p(90)=230.28ms p(95)=233.89ms
     http_reqs......................: 30      0.996293/s
     iteration_duration.............: avg=1.22s    min=1.22s    med=1.22s    max=1.24s    p(90)=1.23s    p(95)=1.23s
     iterations.....................: 30      0.996293/s
     vus............................: 1       min=1      max=1
     vus_max........................: 1       min=1      max=1
```

### 关键指标说明

- **http_req_duration**: HTTP请求的总持续时间
- **http_reqs**: 完成的HTTP请求总数
- **iterations**: 完成的迭代次数
- **checks**: 检查点的通过率
- **data_received/sent**: 接收/发送的数据量

## 1.6 实验：基础环境验证

### 实验目标
验证k6安装是否成功，理解基本测试流程。

### 实验步骤

1. 创建测试脚本
2. 运行测试
3. 分析结果
4. 修改参数重新测试

### 实验代码

```javascript
// 实验1：基础环境验证
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },  // 10秒内增加到5个用户
    { duration: '20s', target: 5 },  // 保持5个用户20秒
    { duration: '10s', target: 0 },  // 10秒内减少到0个用户
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%的请求响应时间小于500ms
    http_req_failed: ['rate<0.01'],   // 请求失败率小于1%
  },
};

export default function () {
  const response = http.get('https://httpbin.test.k6.io/get');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has request headers': (r) => r.json().headers !== undefined,
  });
}
```

### 实验结果分析

观察不同阶段的性能指标变化，理解负载模式对系统性能的影响。

## 总结

本章我们学习了：
- k6的基本概念和特性
- k6的安装和环境搭建
- 创建和运行第一个测试脚本
- 测试结果的解读和分析

下一章我们将深入k6脚本的编写，学习如何创建更复杂的测试场景。