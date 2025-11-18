# NPM从入门到专家教程

本教程将带你从零开始，逐步掌握Node Package Manager (NPM) 的核心概念、基本操作和高级技巧，最终成为NPM专家。

## 教程目录

### 第1章：NPM基础入门
- [1-NPM基础入门.md](./1-NPM基础入门.md)
- NPM简介与历史
- Node.js与NPM的关系
- NPM安装与配置
- 基本命令介绍
- 开发环境搭建

### 第2章：NPM包管理详解
- [2-NPM包管理详解.md](./2-NPM包管理详解.md)
- 包的安装与卸载
- 全局包与本地包
- 包的更新与版本控制
- 包的搜索与信息查看
- 常用命令详解

### 第3章：NPM脚本与生命周期
- [3-NPM脚本与生命周期.md](./3-NPM脚本与生命周期.md)
- NPM脚本基础
- 生命周期脚本
- 脚本参数与环境变量
- 常用自动化任务
- 脚本调试与优化

### 第4章：NPM依赖管理
- [4-NPM依赖管理.md](./4-NPM依赖管理.md)
- 依赖类型详解
- package-lock.json文件
- 依赖冲突解决
- 依赖审计与安全
- 最佳实践

### 第5章：NPM版本管理与发布
- [5-NPM版本管理与发布.md](./5-NPM版本管理与发布.md)
- 语义化版本控制
- 版本管理最佳实践
- 包发布流程
- 包更新与维护
- 版本回滚与问题解决

### 第6章：NPM高级配置与优化
- [6-NPM高级配置与优化.md](./6-NPM高级配置与优化.md)
- NPM配置文件详解
- 镜像源配置与优化
- 缓存管理与清理
- 网络代理配置
- 性能优化技巧

### 第7章：NPM安全与最佳实践
- [7-NPM安全与最佳实践.md](./7-NPM安全与最佳实践.md)
- 包安全审计
- 漏洞检测与修复
- 安全最佳实践
- 私有包管理
- 许可证管理

### 第8章：NPM生态系统与工具
- [8-NPM生态系统与工具.md](./8-NPM生态系统与工具.md)
- NPM注册表与镜像
- 常用NPM工具介绍
- 包管理器对比（Yarn, pnpm等）
- NPM API使用
- 社区资源与贡献

### 第9章：NPM性能优化与调试
- [9-NPM性能优化与调试.md](./9-NPM性能优化与调试.md)
- 安装性能优化
- 依赖分析与优化
- 调试技巧与工具
- 常见问题解决
- 性能监控与分析

### 第10章：NPM企业级应用与实战
- [10-NPM企业级应用与实战.md](./10-NPM企业级应用与实战.md)
- 企业级包管理策略
- 私有NPM注册表搭建
- CI/CD集成
- 大型项目依赖管理
- 实战案例分析

## 代码示例

每章都配有完整的可运行代码示例，位于 [code](./code) 目录中：

- [第1章代码示例](./code/chapter1-examples.js) - NPM基础入门示例
- [第2章代码示例](./code/chapter2-examples.js) - NPM包管理详解示例
- [第3章代码示例](./code/chapter3-examples.js) - NPM脚本与生命周期示例
- [第4章代码示例](./code/chapter4-examples.js) - NPM依赖管理示例
- [第5章代码示例](./code/chapter5-examples.js) - NPM版本管理与发布示例
- [第6章代码示例](./code/chapter6-examples.js) - NPM高级配置与优化示例
- [第7章代码示例](./code/chapter7-examples.js) - NPM安全与最佳实践示例
- [第8章代码示例](./code/chapter8-examples.js) - NPM生态系统与工具示例
- [第9章代码示例](./code/chapter9-examples.js) - NPM性能优化与调试示例
- [第10章代码示例](./code/chapter10-examples.js) - NPM企业级应用与实战示例

## 学习路径建议

1. **初学者路径**：第1章 → 第2章 → 第3章 → 第4章
2. **进阶路径**：第5章 → 第6章 → 第7章 → 第8章
3. **专家路径**：第9章 → 第10章 + 实战项目

## 快速开始

### 安装NPM

NPM通常随Node.js一起安装，您可以从[Node.js官网](https://nodejs.org/)下载安装包。

验证安装：
```bash
npm --version
```

### 创建第一个项目

```bash
# 创建项目目录
mkdir my-npm-project
cd my-npm-project

# 初始化项目
npm init -y

# 安装依赖
npm install lodash

# 创建入口文件
echo "const _ = require('lodash');
console.log(_.chunk([1, 2, 3, 4], 2));" > index.js

# 运行项目
node index.js
```

## 学习环境要求

- Node.js 16.x 或更高版本
- NPM 8.x 或更高版本
- 代码编辑器（推荐VS Code）
- 终端/命令行工具
- Git（用于版本控制）

## 如何使用本教程

1. 按照章节顺序学习，每章包含理论知识和实践示例
2. 运行每章的代码示例，加深理解
3. 完成每章的练习题，巩固所学知识
4. 参考最佳实践，应用到实际项目中

## 常见问题

### Q: NPM和Yarn有什么区别？
A: NPM是Node.js的默认包管理器，Yarn是Facebook开发的替代品。两者功能相似，但Yarn在性能和安全性方面有一些优势。

### Q: 如何解决依赖冲突？
A: 可以使用`npm ls`查看依赖树，使用`npm dedupe`去重依赖，或者使用`npm install package@version`指定特定版本。

### Q: 如何发布私有包？
A: 可以使用NPM的企业版服务，或者搭建私有仓库如Verdaccio。

### Q: 如何提高NPM安装速度？
A: 可以使用淘宝镜像源，启用缓存，或者使用Yarn/pnpm等替代包管理器。

## 参考资源

- [NPM官方文档](https://docs.npmjs.com/)
- [Node.js官方文档](https://nodejs.org/docs/)
- [语义化版本控制](https://semver.org/)
- [NPM注册表](https://www.npmjs.com/)

## 贡献指南

欢迎提交问题报告、改进建议或直接贡献内容！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本教程采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。