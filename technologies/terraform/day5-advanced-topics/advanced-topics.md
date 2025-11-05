# Day 5: 高级主题与最佳实践

## 工作区 (Workspaces)

Terraform 工作区允许您管理同一基础架构配置的多个实例。

### 工作区命令

```bash
# 列出所有工作区
terraform workspace list

# 创建新工作区
terraform workspace new dev

# 切换工作区
terraform workspace select dev

# 显示当前工作区
terraform workspace show
```

### 在配置中使用工作区

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-${terraform.workspace}"
  }
}
```

### 工作区状态文件

工作区的状态文件存储在不同的路径下：
- 默认工作区：`terraform.tfstate`
- 命名工作区：`terraform.tfstate.d/<workspace-name>/terraform.tfstate`

## 策略即代码 (Policy as Code)

使用 Sentinel 或 OPA (Open Policy Agent) 实施策略控制。

### Sentinel 示例

```sentinel
import "tfplan"

# 限制实例类型
allowed_types = [
  "t2.micro",
  "t2.small",
  "t2.medium",
]

main = rule {
  all tfplan.resources.aws_instance as _, instances {
    all instances as _, instance {
      instance.applied.instance_type in allowed_types
    }
  }
}
```

## 远程执行与 CI/CD

### GitHub Actions 示例

```yaml
name: Terraform CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

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

    - name: Terraform Validate
      run: terraform validate

    - name: Terraform Plan
      run: terraform plan -no-color
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

    - name: Terraform Apply
      if: github.ref == 'refs/heads/main' && github.event_name == 'push'
      run: terraform apply -auto-approve
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 状态管理最佳实践

### 启用状态锁定

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "network/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

### 状态备份

```bash
# 手动备份状态文件
terraform state pull > backup.tfstate

# 恢复状态文件
terraform state push backup.tfstate
```

## 复杂表达式与函数

### 条件表达式

```hcl
resource "aws_instance" "example" {
  instance_type = var.environment == "production" ? "m5.large" : "t2.micro"
  ami           = var.ami_id
}
```

### 循环和迭代

```hcl
variable "subnets" {
  type = list(object({
    cidr_block = string
    az         = string
  }))
}

resource "aws_subnet" "public" {
  count = length(var.subnets)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnets[count.index].cidr_block
  availability_zone = var.subnets[count.index].az
}
```

### 自定义函数（Terraform 0.12+）

```hcl
locals {
  # 合并标签
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  # 处理 CIDR 块
  subnet_cidrs = [
    cidrsubnet(var.vpc_cidr, 8, 1),
    cidrsubnet(var.vpc_cidr, 8, 2),
    cidrsubnet(var.vpc_cidr, 8, 3)
  ]
}
```

## 调试技巧

### 启用详细日志

```bash
export TF_LOG=DEBUG
terraform apply
```

### 使用 console 命令

```bash
terraform console
> var.region
> aws_vpc.main.id
```

### 输出调试信息

```hcl
output "debug_info" {
  value = {
    region      = var.region
    vpc_id      = aws_vpc.main.id
    subnet_ids  = aws_subnet.public[*].id
    instance_id = aws_instance.web.id
  }
}
```

## 性能优化

### 并行处理

```hcl
provider "aws" {
  region = var.region

  # 增加最大并发数
  max_retries = 5
}

terraform {
  # 设置并行处理数量
  parallelism = 10
}
```

### 跳过特定资源刷新

```bash
terraform plan -refresh=false
```

## 模块测试

### 使用 Terratest

```go
package test

import (
  "testing"

  "github.com/gruntwork-io/terratest/modules/terraform"
  "github.com/stretchr/testify/assert"
)

func TestTerraformModule(t *testing.T) {
  terraformOptions := &terraform.Options{
    TerraformDir: "../examples",
  }

  defer terraform.Destroy(t, terraformOptions)
  terraform.InitAndApply(t, terraformOptions)

  instanceID := terraform.Output(t, terraformOptions, "instance_id")
  assert.NotEmpty(t, instanceID)
}
```

## 实践练习

多环境部署实践，使用工作区和变量文件管理不同环境。

### 目录结构

以下是我们将在练习中使用的目录结构：

```
examples/
├── main.tf                              # 主配置文件
├── variables.tf                         # 变量定义
├── outputs.tf                           # 输出定义
├── backend.tf                           # 后端配置
├── terraform.tfvars                     # 默认变量文件
├── dev.tfvars                           # 开发环境变量文件
├── prod.tfvars                          # 生产环境变量文件
└── policy/
    └── restrict-instance-types.sentinel # 策略文件
```

### 配置文件详解

#### 变量定义文件 (examples/variables.tf)

首先，我们定义项目所需的变量：

```hcl
# examples/variables.tf
# 多环境部署变量定义

variable "project_name" {
  description = "项目名称"
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

variable "environment" {
  description = "环境名称"
  type        = string
}
```

#### 后端配置文件 (examples/backend.tf)

接下来，我们配置远程后端以安全存储状态文件：

```hcl
# examples/backend.tf
# 后端配置示例

terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "multi-env/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

#### 主配置文件 (examples/main.tf)

然后，我们定义主要的AWS资源：

```hcl
# examples/main.tf
# 多环境部署主要配置

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

#### 输出定义文件 (examples/outputs.tf)

我们定义输出变量以便在部署后获取资源信息：

```hcl
# examples/outputs.tf
# 多环境部署输出定义

output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_id" {
  value = aws_subnet.main.id
}

output "instance_id" {
  value = aws_instance.web.id
}

output "instance_public_ip" {
  value = aws_instance.web.public_ip
}
```

#### 环境变量文件

我们为不同环境创建特定的变量文件：

```hcl
# examples/dev.tfvars
# 开发环境变量文件

project_name  = "myapp"
environment   = "dev"
instance_type = "t2.micro"
```

```hcl
# examples/prod.tfvars
# 生产环境变量文件

project_name  = "myapp"
environment   = "prod"
instance_type = "m5.large"
```

### 策略文件

我们使用 Sentinel 策略来实施基础设施策略：

```sentinel
# examples/policy/restrict-instance-types.sentinel
# Sentinel 策略示例：限制实例类型

import "tfplan"

# 允许的实例类型列表
allowed_types = [
  "t2.micro",
  "t2.small",
  "t2.medium",
  "m5.large",
  "m5.xlarge",
]

# 主策略规则
main = rule {
  # 检查所有 aws_instance 资源
  all tfplan.resources.aws_instance as _, instances {
    # 检查每个实例
    all instances as _, instance {
      # 确保实例类型在允许列表中
      instance.applied.instance_type in allowed_types
    }
  }
}

# 附加规则：生产环境必须使用特定实例类型
production_instances = rule {
  # 仅在生产环境中应用
  terraform.workspace == "prod" ? 
    all tfplan.resources.aws_instance as _, instances {
      all instances as _, instance {
        # 生产环境必须使用 m5.large 或更大的实例
        instance.applied.instance_type in ["m5.large", "m5.xlarge", "m5.2xlarge"]
      }
    }
    : true
}
```

### 使用步骤

1. 初始化 Terraform：
   ```bash
   terraform init
   ```


2. 创建工作区：
   ```bash
   terraform workspace new dev
   terraform workspace new prod
   ```


3. 部署到开发环境：
   ```bash
   terraform workspace select dev
   terraform apply -var-file=dev.tfvars
   ```


4. 部署到生产环境：
   ```bash
   terraform workspace select prod
   terraform apply -var-file=prod.tfvars
   ```


## 总结

今天我们学习了：

1. 工作区的使用和管理
2. 策略即代码的概念和实现
3. CI/CD 集成方法
4. 状态管理最佳实践
5. 复杂表达式和调试技巧
6. 性能优化策略
7. 模块测试方法
8. 多环境部署示例

这完成了我们从入门到专家级别的 Terraform 学习之旅。您现在已经掌握了 Terraform 的核心概念和高级特性，可以在实际项目中应用这些知识。