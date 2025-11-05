# Day 6: Terraform Cloud 和企业功能

## 今日学习目标

- 了解 Terraform Cloud 的核心功能
- 学习如何在 Terraform Cloud 中管理基础设施
- 掌握远程操作和状态管理
- 理解工作区和变量管理
- 学习团队协作和权限管理

## Terraform Cloud 简介

Terraform Cloud 是 HashiCorp 提供的托管服务，用于基础设施即代码的协作和自动化。它提供了许多企业级功能，包括：

- 远程状态管理
- 协作功能
- 访问控制
- 私有模块注册表
- 成本估算
- 安全策略实施

## 核心概念

### 工作区 (Workspaces)

工作区是 Terraform Cloud 中的基本组织单元，用于隔离不同的基础设施环境。

### 远程操作

Terraform Cloud 支持两种操作模式：
- CLI 驱动模式：在本地运行 Terraform，但将状态存储在云端
- 远程操作模式：在 Terraform Cloud 中完全执行 Terraform 命令

### 变量和密钥管理

Terraform Cloud 提供安全的变量和密钥存储，支持敏感数据的加密存储。

## 实践练习

### 目录结构

```
examples/
├── main.tf           # 主配置文件
└── variables.tf      # 变量定义
```

### 配置文件详解

#### 变量定义文件 (examples/variables.tf)

```hcl
# examples/variables.tf
# Terraform Cloud 变量定义示例

variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}
```

#### 主配置文件 (examples/main.tf)

```hcl
# examples/main.tf
# Terraform Cloud 主配置示例

provider "aws" {
  region = var.region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "${var.project_name}-${var.environment}-subnet"
  }
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  subnet_id     = aws_subnet.main.id

  tags = {
    Name        = "${var.project_name}-${var.environment}-web"
    Environment = var.environment
  }
}
```

### Terraform Cloud 配置

#### 1. 创建 Terraform Cloud 账户

首先，访问 [Terraform Cloud](https://app.terraform.io/) 并创建一个账户。

#### 2. 安装 Terraform CLI

确保您的系统上安装了 Terraform CLI。

#### 3. 配置凭据

创建一个用户令牌并配置 CLI：

```bash
terraform login
```

#### 4. 配置后端

在您的 Terraform 配置中添加云块：

```hcl
# backend.tf
terraform {
  cloud {
    organization = "your-organization"

    workspaces {
      name = "your-workspace"
    }
  }
}
```

### 使用步骤

1. 在 Terraform Cloud 中创建组织和工作区
2. 配置工作区变量
3. 在本地初始化 Terraform：
   ```bash
   terraform init
   ```
4. 查看执行计划：
   ```bash
   terraform plan
   ```
5. 应用配置：
   ```bash
   terraform apply
   ```

## 总结

今天我们学习了：

1. Terraform Cloud 的核心功能
2. 工作区和远程操作的概念
3. 变量和密钥管理
4. 团队协作和权限管理
5. Terraform Cloud 的实际使用方法

明天我们将学习 Terraform 的测试和验证最佳实践。