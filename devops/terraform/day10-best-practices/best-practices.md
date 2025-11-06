# Day 10: Terraform 最佳实践

## 学习目标

完成本章后，您将能够：
- 掌握 Terraform 项目结构组织的最佳实践
- 理解命名规范和代码风格指南
- 学会使用模块化设计提高代码复用性
- 掌握变量和输出管理的最佳实践
- 了解安全性和权限管理建议
- 熟悉版本控制和协作工作流程
- 掌握测试和验证策略

## 项目结构组织

良好的项目结构有助于团队协作和代码维护。推荐的项目结构如下：

```
terraform-project/
├── modules/
│   ├── module1/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── module2/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
├── scripts/
│   ├── deploy.sh
│   └── destroy.sh
├── tests/
│   ├── unit/
│   └── integration/
├── README.md
└── versions.tf
```

### 模块目录 (modules/)

存放可复用的 Terraform 模块，每个模块应包含完整的资源定义、变量和输出。

### 环境目录 (environments/)

按环境组织配置，每个环境目录包含该环境特定的配置文件。

### 脚本目录 (scripts/)

存放自动化部署和管理脚本。

### 测试目录 (tests/)

存放各种类型的测试代码。

## 命名规范

### 资源命名

遵循云服务商的命名规范，通常使用小写字母、数字和连字符：

```hcl
resource "aws_instance" "web_server" {
  # ...
}

resource "aws_s3_bucket" "logs_bucket" {
  # ...
}
```

### 变量命名

使用下划线分隔的小写字母：

```hcl
variable "instance_type" {
  # ...
}

variable "environment_name" {
  # ...
}
```

### 输出命名

清晰描述输出内容：

```hcl
output "web_server_public_ip" {
  # ...
}

output "database_endpoint" {
  # ...
}
```

## 代码风格指南

### 文件组织

1. 将资源配置、变量定义和输出定义分别放在不同的文件中
2. 按照资源类型或功能对资源进行分组
3. 在文件顶部添加注释说明文件用途

### 注释规范

```hcl
# 创建 VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main-vpc"
  }
}

# Web 子网 - 公共子网
resource "aws_subnet" "web" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  
  tags = {
    Name = "web-subnet"
  }
}
```

### 格式化

使用 `terraform fmt` 命令保持代码格式一致。

## 模块化设计

### 模块设计原则

1. **单一职责**：每个模块应专注于一个特定的功能
2. **接口清晰**：明确定义输入变量和输出值
3. **文档完整**：提供详细的 README 文档
4. **版本管理**：使用语义化版本控制

### 模块使用示例

```hcl
module "vpc" {
  source = "../modules/vpc"
  
  name            = "production-vpc"
  cidr_block      = "10.0.0.0/16"
  enable_dns_hostnames = true
}

module "web_server" {
  source = "../modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnets[0]
  
  tags = {
    Environment = "production"
  }
}
```

## 变量和输出管理

### 变量验证

使用 validation 块确保输入符合预期：

```hcl
variable "environment" {
  description = "环境名称"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "环境必须是 dev, staging, 或 prod 之一。"
  }
}
```

### 敏感信息处理

使用 ` sensitive = true` 标记敏感变量：

```hcl
variable "db_password" {
  description = "数据库密码"
  type        = string
  sensitive   = true
}
```

### 输出文档

为每个输出添加描述：

```hcl
output "load_balancer_dns" {
  description = "负载均衡器 DNS 名称"
  value       = aws_lb.main.dns_name
}
```

## 安全性和权限管理

### 最小权限原则

为 Terraform 使用的 AWS 凭证分配最小必要权限。

### 状态文件保护

1. 启用 S3 服务器端加密
2. 启用 S3 版本控制
3. 启用状态锁定
4. 限制对状态文件的访问权限

### 密码和密钥管理

避免在代码中硬编码密码和密钥，使用以下方式：

1. AWS Secrets Manager
2. AWS Systems Manager Parameter Store
3. HashiCorp Vault

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "production/db/password"
}

resource "aws_db_instance" "main" {
  # ...
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```

## 版本控制和协作

### Git 工作流程

1. 使用分支进行功能开发
2. 通过 Pull Request 进行代码审查
3. 在合并前运行自动化测试

### .gitignore 配置

```gitignore
# Terraform 忽略文件
.terraform/
*.tfstate
*.tfstate.*
crash.log
core
```

### 提交信息规范

使用明确的提交信息描述变更内容：

```
feat: 添加 VPC 模块
fix: 修复安全组规则
docs: 更新 README 文档
```

## 测试和验证策略

### 单元测试

使用 Terratest 框架测试单个模块：

```go
func TestVPCModule(t *testing.T) {
  terraformOptions := &terraform.Options{
    TerraformDir: "../modules/vpc",
    Vars: map[string]interface{}{
      "cidr_block": "10.0.0.0/16",
    },
  }
  
  defer terraform.Destroy(t, terraformOptions)
  terraform.InitAndApply(t, terraformOptions)
  
  // 验证 VPC 是否创建成功
  vpcID := terraform.Output(t, terraformOptions, "vpc_id")
  assert.NotEmpty(t, vpcID)
}
```

### 集成测试

测试多个模块协同工作的情况。

### 端到端测试

模拟真实部署场景，验证整个系统的功能。

## CI/CD 集成

### 流水线阶段

1. **代码检出**
2. **依赖安装**
3. **代码格式化检查**
4. **静态分析**
5. **单元测试**
6. **计划阶段** (`terraform plan`)
7. **审批阶段**
8. **应用阶段** (`terraform apply`)

### GitHub Actions 示例

```yaml
name: Terraform CI/CD
on:
  push:
    branches:
      - main
  pull_request:

jobs:
  terraform:
    name: Terraform
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1

      - name: Terraform Format
        run: terraform fmt -check

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: terraform plan -input=false

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve -input=false
```

## 性能优化

### 并行处理

利用 Terraform 的并行处理能力：

```hcl
provider "aws" {
  region = "us-west-2"
  # 增加最大并发数
  max_retries = 5
}
```

### 资源依赖优化

明确指定资源依赖关系，避免不必要的依赖：

```hcl
resource "aws_instance" "web" {
  # ...
}

resource "aws_ebs_volume" "data" {
  # ...
}

# 明确指定依赖关系
resource "aws_volume_attachment" "data_attach" {
  instance_id  = aws_instance.web.id
  volume_id    = aws_ebs_volume.data.id
  device_name  = "/dev/sdh"
  
  depends_on = [
    aws_instance.web,
    aws_ebs_volume.data
  ]
}
```

## 监控和日志

### 基础设施监控

集成 CloudWatch 或其他监控解决方案：

```hcl
resource "aws_cloudwatch_metric_alarm" "cpu_utilization" {
  alarm_name          = "high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "CPU 利用率超过 80%"
  alarm_actions       = [aws_sns_topic.alarm.arn]
  
  dimensions = {
    InstanceId = aws_instance.web.id
  }
}
```

### 日志收集

配置基础设施日志收集：

```hcl
resource "aws_cloudwatch_log_group" "app_logs" {
  name = "/aws/ec2/app-logs"
  retention_in_days = 30
}
```

## 实践练习

### 目录结构

```
day10-best-practices/
├── examples/
│   ├── modules/
│   │   ├── vpc/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── README.md
│   │   └── ec2-instance/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       └── README.md
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── terraform.tfvars
│   │   └── prod/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── terraform.tfvars
│   └── tests/
│       └── vpc_test.go
├── scripts/
│   ├── deploy.sh
│   └── destroy.sh
└── best-practices.md
```

### 创建 VPC 模块

创建 `examples/modules/vpc/variables.tf`：

```hcl
variable "name" {
  description = "VPC 名称"
  type        = string
}

variable "cidr_block" {
  description = "VPC CIDR 块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_dns_hostnames" {
  description = "是否启用 DNS 主机名"
  type        = bool
  default     = true
}
```

创建 `examples/modules/vpc/main.tf`：

```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  
  tags = {
    Name = var.name
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.name}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "${var.name}-public-rt"
  }
}
```

创建 `examples/modules/vpc/outputs.tf`：

```hcl
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "internet_gateway_id" {
  description = "互联网网关 ID"
  value       = aws_internet_gateway.main.id
}

output "public_route_table_id" {
  description = "公共路由表 ID"
  value       = aws_route_table.public.id
}
```

创建 `examples/modules/vpc/README.md`：

```markdown
# VPC 模块

## 介绍

此模块创建一个基本的 VPC 配置，包括互联网网关和公共路由表。

## 使用示例

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  name       = "production-vpc"
  cidr_block = "10.0.0.0/16"
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| name | VPC 名称 | string | - |
| cidr_block | VPC CIDR 块 | string | 10.0.0.0/16 |
| enable_dns_hostnames | 是否启用 DNS 主机名 | bool | true |

## 输出值

| 名称 | 描述 |
|------|------|
| vpc_id | VPC ID |
| internet_gateway_id | 互联网网关 ID |
| public_route_table_id | 公共路由表 ID |
```

### 创建 EC2 实例模块

创建 `examples/modules/ec2-instance/variables.tf`：

```hcl
variable "ami_id" {
  description = "AMI ID"
  type        = string
}

variable "instance_type" {
  description = "实例类型"
  type        = string
  default     = "t2.micro"
  
  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro, t2.small, 或 t2.medium 之一。"
  }
}

variable "subnet_id" {
  description = "子网 ID"
  type        = string
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default     = {}
}
```

创建 `examples/modules/ec2-instance/main.tf`：

```hcl
resource "aws_instance" "main" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id
  
  tags = merge(
    var.tags,
    {
      Name = "ec2-instance"
    }
  )
}
```

创建 `examples/modules/ec2-instance/outputs.tf`：

```hcl
output "instance_id" {
  description = "实例 ID"
  value       = aws_instance.main.id
}

output "public_ip" {
  description = "公共 IP 地址"
  value       = aws_instance.main.public_ip
}
```

创建 `examples/modules/ec2-instance/README.md`：

```markdown
# EC2 实例模块

## 介绍

此模块创建一个 EC2 实例。

## 使用示例

```hcl
module "web_server" {
  source = "./modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
  subnet_id     = "subnet-12345678"
  
  tags = {
    Environment = "dev"
  }
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| ami_id | AMI ID | string | - |
| instance_type | 实例类型 | string | t2.micro |
| subnet_id | 子网 ID | string | - |
| tags | 资源标签 | map(string) | {} |

## 输出值

| 名称 | 描述 |
|------|------|
| instance_id | 实例 ID |
| public_ip | 公共 IP 地址 |
```

### 开发环境配置

创建 `examples/environments/dev/main.tf`：

```hcl
provider "aws" {
  region = "us-west-2"
}

module "vpc" {
  source = "../../modules/vpc"
  
  name       = "dev-vpc"
  cidr_block = "10.1.0.0/16"
}

module "web_server" {
  source = "../../modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnets[0]
  
  tags = {
    Environment = "dev"
  }
}

output "web_server_ip" {
  value = module.web_server.public_ip
}
```

创建 `examples/environments/dev/variables.tf`：

```hcl
variable "instance_type" {
  description = "实例类型"
  type        = string
  default     = "t2.micro"
}
```

创建 `examples/environments/dev/terraform.tfvars`：

```hcl
instance_type = "t2.micro"
```

### 生产环境配置

创建 `examples/environments/prod/main.tf`：

```hcl
provider "aws" {
  region = "us-west-2"
}

module "vpc" {
  source = "../../modules/vpc"
  
  name       = "prod-vpc"
  cidr_block = "10.2.0.0/16"
}

module "web_server" {
  source = "../../modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnets[0]
  
  tags = {
    Environment = "prod"
  }
}

output "web_server_ip" {
  value = module.web_server.public_ip
}
```

创建 `examples/environments/prod/variables.tf`：

```hcl
variable "instance_type" {
  description = "实例类型"
  type        = string
}

variable "db_password" {
  description = "数据库密码"
  type        = string
  sensitive   = true
}
```

创建 `examples/environments/prod/terraform.tfvars`：

```hcl
instance_type = "t2.small"
```

### 部署脚本

创建 `scripts/deploy.sh`：

```bash
#!/bin/bash

set -e

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
  echo "请指定环境 (dev|staging|prod)"
  exit 1
fi

echo "部署 $ENVIRONMENT 环境..."

cd examples/environments/$ENVIRONMENT
terraform init
terraform plan -out=tfplan
terraform apply tfplan

echo "$ENVIRONMENT 环境部署完成"
```

创建 `scripts/destroy.sh`：

```bash
#!/bin/bash

set -e

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
  echo "请指定环境 (dev|staging|prod)"
  exit 1
fi

echo "销毁 $ENVIRONMENT 环境..."

cd examples/environments/$ENVIRONMENT
terraform destroy -auto-approve

echo "$ENVIRONMENT 环境已销毁"
```

### 测试代码

创建 `examples/tests/vpc_test.go`：

```go
package test

import (
  "testing"
  
  "github.com/gruntwork-io/terratest/modules/terraform"
  "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
  terraformOptions := &terraform.Options{
    TerraformDir: "../modules/vpc",
    Vars: map[string]interface{}{
      "name":       "test-vpc",
      "cidr_block": "10.0.0.0/16",
    },
  }
  
  defer terraform.Destroy(t, terraformOptions)
  terraform.InitAndApply(t, terraformOptions)
  
  // 验证 VPC 是否创建成功
  vpcID := terraform.Output(t, terraformOptions, "vpc_id")
  assert.NotEmpty(t, vpcID)
  
  // 验证互联网网关是否创建成功
  igwID := terraform.Output(t, terraformOptions, "internet_gateway_id")
  assert.NotEmpty(t, igwID)
}
```

通过以上实践练习，您将掌握 Terraform 最佳实践的核心要点，能够在实际项目中应用这些原则来构建高质量、可维护的基础设施即代码。