# Terraform 学习资源

本目录包含完整的 Terraform 学习资料，从基础概念到高级实践。

## 文档结构

### 📚 主要学习文档

- **[terraform-complete-guide.md](terraform-complete-guide.md)** - Terraform 完整指南：从入门到专家
  - 整合了所有学习内容，提供系统化的学习路径
  - 包含基础概念、高级特性、最佳实践等完整内容

- **[terraform-detailed-explanation.md](terraform-detailed-explanation.md)** - Terraform 核心概念详细讲解
  - 深入讲解 Resource、Variable、Output 等核心概念
  - 提供详细的代码示例和解释

### 📁 目录说明

```
devops/terraform/
├── README.md                          # 本文件
├── terraform-complete-guide.md        # 完整学习指南
├── terraform-detailed-explanation.md  # 核心概念详解
└── examples/                          # 示例代码目录
    ├── basic/                         # 基础示例
    ├── advanced/                      # 高级示例
    └── modules/                       # 模块示例
```

## 学习路径建议

### 🚀 初学者路径
1. 阅读 `terraform-complete-guide.md` 的前 3 个章节
2. 学习基础概念和配置语法
3. 实践简单的资源创建

### 📈 进阶学习路径
1. 深入学习变量、模块和状态管理
2. 学习高级特性和最佳实践
3. 实践复杂的基础设施部署

### 🏆 专家路径
1. 掌握 Terraform Cloud 和团队协作
2. 学习测试验证和模块发布
3. 实施企业级最佳实践

## 快速开始

### 安装 Terraform

#### Windows
```powershell
choco install terraform
```

#### macOS
```bash
brew install hashicorp/tap/terraform
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install terraform
```

### 验证安装
```bash
terraform version
```

### 第一个配置

创建 `main.tf` 文件：
```hcl
terraform {
  required_providers {
    local = {
      source = "hashicorp/local"
      version = "2.4.0"
    }
  }
}

resource "local_file" "example" {
  content  = "Hello, Terraform!"
  filename = "hello.txt"
}
```

执行命令：
```bash
terraform init
terraform plan
terraform apply
```

## 核心概念

### 🔧 Resource（资源）
- 定义和管理基础设施组件
- 支持 count、for_each 等元参数
- 生命周期管理

### 📊 Variable（变量）
- 参数化配置
- 支持多种数据类型
- 验证规则和敏感变量

### 📤 Output（输出）
- 导出配置值
- 支持复杂数据结构
- 敏感输出保护

### 🔄 Data Source（数据源）
- 读取现有基础设施信息
- 动态获取资源数据

### 🧩 Module（模块）
- 组织和重用配置
- 模块化设计
- 版本控制

## 最佳实践

### 代码组织
- 使用标准文件结构
- 模块化设计
- 环境分离

### 安全实践
- 敏感数据管理
- 最小权限原则
- 状态文件加密

### 性能优化
- 并行执行
- 资源复用
- 监控告警

## 相关资源

- [Terraform 官方文档](https://www.terraform.io/docs)
- [HashiCorp 学习平台](https://learn.hashicorp.com/terraform)
- [Terraform Registry](https://registry.terraform.io/)

## 贡献

欢迎提交问题和改进建议！

## 许可证

本学习资料遵循 MIT 许可证。