# Playwright CodeGen 扩展专题示例

这个目录包含了Playwright CodeGen扩展功能的完整示例和演示，涵盖了从基础用法到高级特性的所有方面。

## 📋 目录结构

```
examples/
├── package.json                    # 项目配置和依赖
├── README.md                      # 这个文件
├── codegen-demo.js                # 基础演示示例
├── codegen-advanced-demo.js       # 高级演示示例
├── codegen-workflow.js            # 工作流自动化示例
├── codegen-integration-demo.js    # 集成演示示例
├── codegen-best-practices.js      # 最佳实践示例
├── codegen-troubleshooting.js     # 故障排除示例
├── codegen-demo-runner.js         # 统一演示运行器
├── codegen-custom-commands.js     # 自定义命令工具
├── codegen.config.js              # CodeGen配置文件
├── run-all-demos.js               # 运行所有演示的脚本
└── generated-tests/               # 生成的测试文件（运行时创建）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 运行演示

#### 运行所有演示
```bash
npm run all
# 或者
node run-all-demos.js
```

#### 运行特定演示
```bash
# 基础演示
npm run demo

# 高级演示
npm run advanced

# 工作流演示
npm run workflow

# 集成演示
npm run integration

# 最佳实践
npm run best-practices

# 故障排除
npm run troubleshooting
```

#### 交互式演示运行器
```bash
npm run runner
# 或者
node codegen-demo-runner.js
```

### 3. 清理生成的文件

```bash
node run-all-demos.js --cleanup
```

## 📖 演示内容

### 🔧 基础演示 (codegen-demo.js)
- 基本CodeGen使用
- 表单交互录制
- 复杂用户交互
- 等待和断言
- iframe处理
- 移动端模拟
- 网络请求录制
- 最佳实践模式

### 🎯 高级演示 (codegen-advanced-demo.js)
- 移动端设备录制
- 地理位置和本地化测试
- 网络请求拦截和修改
- 认证状态保持
- 多标签页和弹窗处理
- 文件上传和下载
- 截图和视频录制
- 性能分析和监控
- 跨浏览器测试自动化
- 自定义CodeGen配置

### 🔄 工作流演示 (codegen-workflow.js)
- 测试套件创建
- 响应式设计测试
- 跨浏览器测试
- 国际化测试
- 性能测试集成
- 可访问性测试
- API测试集成
- 数据库测试
- 工作流管理和调度

### 🔗 集成演示 (codegen-integration-demo.js)
- CI/CD管道集成
- 测试管理工具集成
- 性能测试工具集成
- 监控工具集成
- 容器化平台集成
- GitHub Actions集成
- TestRail集成
- Lighthouse集成
- Datadog集成
- Docker集成

### 📚 最佳实践 (codegen-best-practices.js)
- 数据属性选择器使用
- 页面对象模式
- 等待策略
- 断言最佳实践
- 动态内容处理
- 测试数据管理
- 代码组织结构
- 性能优化
- 可维护性指南

### 🔧 故障排除 (codegen-troubleshooting.js)
- 录制问题诊断
- 选择器问题分析
- 时间问题处理
- 环境问题排查
- 系统信息收集
- 快速修复方案
- 常见问题解答

## 🛠️ 配置文件

### CodeGen配置 (codegen.config.js)
包含以下配置模块：
- 基本配置
- 设备模拟
- 地理位置
- 本地化
- 网络设置
- 认证配置
- 录制选项
- 代码生成设置
- 环境配置
- 测试数据
- 高级配置

### 自定义命令 (codegen-custom-commands.js)
提供以下工具类：
- CodegenCommandBuilder: 构建和执行codegen命令
- BatchCodegenExecutor: 批量执行多个配置
- 预设配置模板
- 工具函数集合

## 🎮 使用示例

### 基础CodeGen使用
```javascript
const { CodegenDemo } = require('./codegen-demo');

const demo = new CodegenDemo();
await demo.runAllDemos();
```

### 高级配置
```javascript
const { AdvancedCodegenDemo } = require('./codegen-advanced-demo');

const demo = new AdvancedCodegenDemo();
await demo.runMobileDeviceDemo();
await demo.runNetworkInterceptionDemo();
```

### 工作流自动化
```javascript
const { CodegenWorkflowManager } = require('./codegen-workflow');

const workflow = new CodegenWorkflowManager();
await workflow.createTestSuite('电商网站测试套件');
await workflow.runResponsiveDesignTests();
```

### 集成演示
```javascript
const { CodegenIntegrationManager } = require('./codegen-integration-demo');

const integration = new CodegenIntegrationManager();
await integration.setupCIPipeline();
await integration.integrateWithTestRail();
```

## 📊 生成的文件

运行演示后，会在以下目录生成测试文件：

- `generated-tests/` - 基础演示生成的测试
- `advanced-tests/` - 高级演示生成的测试
- `workflow-tests/` - 工作流演示生成的测试
- `integration-tests/` - 集成演示生成的测试
- `best-practice-tests/` - 最佳实践演示生成的测试
- `troubleshooting-tests/` - 故障排除演示生成的测试

## 🔍 故障排除

### 常见问题

1. **模块未找到错误**
   - 确保已运行 `npm install`
   - 检查Playwright是否已安装

2. **演示运行失败**
   - 检查网络连接
   - 确保目标网站可访问
   - 查看控制台输出获取详细信息

3. **生成的测试文件错误**
   - 检查输出目录权限
   - 确保磁盘空间充足

### 调试模式

运行演示时添加调试信息：
```bash
DEBUG=1 node codegen-demo.js
```

## 📚 学习资源

### 官方文档
- [Playwright CodeGen文档](https://playwright.dev/docs/codegen)
- [Playwright测试指南](https://playwright.dev/docs/intro)
- [Playwright API参考](https://playwright.dev/docs/api/class-playwright)

### 最佳实践
- 使用数据属性选择器而非CSS类名
- 采用页面对象模式组织代码
- 使用适当的等待策略避免脆弱测试
- 保持测试代码的可维护性和可读性

## 🤝 贡献

欢迎提交问题和改进建议！请确保：
- 遵循现有代码风格
- 添加适当的注释和文档
- 测试所有更改
- 更新相关文档

## 📄 许可证

MIT License - 详见项目根目录的LICENSE文件