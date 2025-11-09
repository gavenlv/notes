# k6代码示例目录

本目录包含所有k6学习指南中的代码示例，可以直接运行和测试。

## 目录结构

```
code/
├── chapter1/          # 第1章代码示例
│   ├── 1-first-test.js
│   └── experiment1-basic-validation.js
├── chapter2/          # 第2章代码示例
│   ├── basic-script-structure.js
│   ├── http-requests.js
│   ├── checks-and-validations.js
│   ├── groups.js
│   └── experiment2-api-scenario.js
├── chapter3/          # 第3章代码示例
│   ├── custom-metrics.js
│   ├── scenarios-executors.js
│   ├── test-data-management.js
│   ├── performance-test-types.js
│   ├── error-handling.js
│   └── experiment3-ecommerce-scenario.js
├── chapter4/          # 第4章代码示例
│   ├── utils/
│   │   ├── http-utils.js
│   │   └── validation-utils.js
│   ├── config/
│   │   └── test-config.js
│   ├── production-framework.js
│   └── experiment4-production-framework.js
└── run-all-tests.sh   # 批量运行所有测试的脚本
```

## 快速开始

### 运行单个测试

```bash
# 运行第1章的测试
k6 run code/chapter1/1-first-test.js

# 运行第2章的API场景测试
k6 run code/chapter2/experiment2-api-scenario.js

# 运行第3章的综合场景测试
k6 run code/chapter3/experiment3-ecommerce-scenario.js
```

### 运行所有测试

```bash
# 在Linux/macOS上
chmod +x code/run-all-tests.sh
./code/run-all-tests.sh

# 在Windows上
powershell -File code\run-all-tests.ps1
```

## 代码示例说明

### 第1章：基础概念与环境搭建

- `1-first-test.js` - 最简单的k6测试脚本
- `experiment1-basic-validation.js` - 基础环境验证实验

### 第2章：脚本编写基础

- `basic-script-structure.js` - k6脚本基本结构
- `http-requests.js` - HTTP请求的各种方法
- `checks-and-validations.js` - 检查点和验证
- `groups.js` - 分组功能使用
- `experiment2-api-scenario.js` - 完整API测试场景

### 第3章：高级功能与性能测试

- `custom-metrics.js` - 自定义指标使用
- `scenarios-executors.js` - 场景和执行器配置
- `test-data-management.js` - 测试数据管理
- `performance-test-types.js` - 各种性能测试类型
- `error-handling.js` - 高级错误处理
- `experiment3-ecommerce-scenario.js` - 电商网站综合性能测试

### 第4章：最佳实践与生产环境部署

- `utils/` - 工具函数库
- `config/` - 配置文件
- `production-framework.js` - 生产级测试框架
- `experiment4-production-framework.js` - 完整生产框架示例

## 环境要求

- k6 v0.50.0+
- Node.js (可选，用于部分高级功能)
- 网络连接（用于访问测试API）

## 测试服务器

代码示例中使用的测试服务器：
- `https://httpbin.test.k6.io` - k6官方的测试服务器
- `https://test.k6.io` - k6演示网站

如果您有自己的API需要测试，可以修改代码中的URL指向您的服务。

## 自定义配置

大多数代码示例都支持通过环境变量进行配置：

```bash
# 设置测试环境
export ENV=production

# 设置自定义API地址
export BASE_URL=https://your-api.example.com

# 设置认证令牌
export API_TOKEN=your-token-here

# 运行测试
k6 run code/chapter2/experiment2-api-scenario.js
```

## 问题排查

如果遇到问题，请检查：

1. k6是否正确安装：`k6 version`
2. 网络连接是否正常
3. 测试服务器是否可访问
4. 环境变量是否正确设置

## 贡献

欢迎提交问题和改进建议！