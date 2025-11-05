# Day 4: 模块化与最佳实践

## 模块概述

模块是 Terraform 中组织和重用代码的基本单位。每个 Terraform 配置都是一个模块，可以调用其他模块。

### 模块的优点

1. **可重用性**：编写一次，在多处使用
2. **可维护性**：集中管理基础设施组件
3. **可测试性**：独立测试模块功能
4. **团队协作**：不同团队可以开发和维护不同的模块

## 创建模块

### 模块结构

```
terraform-modules/
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
└── examples/
    └── main.tf
```

### 简单模块示例

创建一个 VPC 模块：

```hcl
# modules/vpc/variables.tf
variable "vpc_cidr" {
  description = "VPC CIDR 块"
  type        = string
}

variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}
```

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project_name}-${var.environment}-igw"
    Project     = var.project_name
    Environment = var.environment
  }
}
```

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "vpc_cidr" {
  value       = aws_vpc.main.cidr_block
  description = "VPC CIDR 块"
}

output "internet_gateway_id" {
  value       = aws_internet_gateway.main.id
  description = "互联网网关 ID"
}
```

## 使用模块

### 本地模块

```hcl
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr     = "10.0.0.0/16"
  project_name = "myproject"
  environment  = "dev"
}

output "vpc_info" {
  value = {
    id   = module.vpc.vpc_id
    cidr = module.vpc.vpc_cidr
  }
}
```

### 远程模块

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

## 模块版本控制

### Git 标签版本

```hcl
module "vpc" {
  source = "git::https://github.com/example/terraform-aws-vpc.git?ref=v1.0.0"
}
```

### GitHub 版本

```hcl
module "vpc" {
  source = "github.com/example/terraform-aws-vpc?ref=v1.0.0"
}
```

### Bitbucket 版本

```hcl
module "vpc" {
  source = "bitbucket.org/example/terraform-aws-vpc?ref=v1.0.0"
}
```

## 最佳实践

### 1. 变量验证

```hcl
variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"

  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro, t2.small 或 t2.medium 之一。"
  }
}
```

### 2. 输出敏感信息

```hcl
output "database_password" {
  value       = aws_db_instance.default.password
  description = "数据库密码"
  sensitive   = true
}
```

### 3. 使用 locals 简化表达式

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  name_prefix = "${var.project_name}-${var.environment}"
}
```

### 4. 条件资源创建

```hcl
resource "aws_instance" "web" {
  count = var.create_instance ? 1 : 0

  ami           = var.ami_id
  instance_type = var.instance_type

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-web-${count.index}"
    }
  )
}
```

### 5. 循环创建资源

```hcl
variable "subnets" {
  description = "子网配置列表"
  type = list(object({
    cidr_block = string
    az         = string
  }))
  default = [
    { cidr_block = "10.0.1.0/24", az = "us-west-2a" },
    { cidr_block = "10.0.2.0/24", az = "us-west-2b" }
  ]
}

resource "aws_subnet" "public" {
  count = length(var.subnets)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnets[count.index].cidr_block
  availability_zone = var.subnets[count.index].az

  tags = {
    Name = "${local.name_prefix}-subnet-${count.index}"
  }
}
```

## 实践练习

创建一个完整的 Web 应用程序模块，包含 VPC、子网、安全组和 EC2 实例。

### 模块结构

以下是我们将在练习中使用的模块结构：

```
examples/
├── main.tf                    # 使用模块的主配置
└── modules/
    └── web-app/               # Web 应用模块
        ├── main.tf            # 主要资源定义
        ├── variables.tf       # 输入变量
        ├── outputs.tf         # 输出值
        ├── security.tf        # 安全组配置
        ├── ec2.tf             # EC2 实例配置
        └── README.md          # 模块说明文档
```

### 模块实现

#### 模块变量定义 (modules/web-app/variables.tf)

首先，我们定义模块所需的变量：

```hcl
# modules/web-app/variables.tf
# Web 应用模块变量定义

variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR 块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "子网 CIDR 块"
  type        = string
  default     = "10.0.1.0/24"
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

variable "ami_id" {
  description = "AMI ID"
  type        = string
  default     = "ami-0c55b159cbfafe1d0"
}
```

#### 模块主要资源定义 (modules/web-app/main.tf)

接下来，我们定义 VPC 和网络相关资源：

```hcl
# modules/web-app/main.tf
# Web 应用模块主要资源定义

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.environment}-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
```

#### 模块安全组配置 (modules/web-app/security.tf)

然后，我们定义安全组规则：

```hcl
# modules/web-app/security.tf
# Web 应用模块安全组配置

resource "aws_security_group" "web" {
  name        = "${var.project_name}-${var.environment}-web-sg"
  description = "Web 服务器安全组"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-web-sg"
  }
}
```

#### 模块 EC2 实例配置 (modules/web-app/ec2.tf)

接着，我们定义 EC2 实例资源：

```hcl
# modules/web-app/ec2.tf
# Web 应用模块 EC2 实例配置

resource "aws_instance" "web" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello from ${var.project_name} ${var.environment}</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "${var.project_name}-${var.environment}-web"
  }
}
```

#### 模块输出定义 (modules/web-app/outputs.tf)

最后，我们定义模块的输出值：

```hcl
# modules/web-app/outputs.tf
# Web 应用模块输出定义

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "subnet_id" {
  value       = aws_subnet.public.id
  description = "子网 ID"
}

output "security_group_id" {
  value       = aws_security_group.web.id
  description = "安全组 ID"
}

output "instance_id" {
  value       = aws_instance.web.id
  description = "EC2 实例 ID"
}

output "instance_public_ip" {
  value       = aws_instance.web.public_ip
  description = "EC2 实例公共 IP"
}
```

### 使用模块

现在，我们可以在主配置文件中使用这个模块：

```hcl
# examples/main.tf
# 使用 Web 应用模块的示例

module "dev_web_app" {
  source = "./modules/web-app"

  project_name  = "webapp"
  environment   = "dev"
  vpc_cidr      = "10.1.0.0/16"
  subnet_cidr   = "10.1.1.0/24"
  instance_type = "t2.micro"
}

output "dev_web_app_info" {
  value = {
    instance_ip = module.dev_web_app.instance_public_ip
    vpc_id      = module.dev_web_app.vpc_id
  }
}
```

### 执行步骤

1. 初始化 Terraform：
   ```bash
   terraform init
   ```

2. 查看执行计划：
   ```bash
   terraform plan
   ```

3. 应用配置：
   ```bash
   terraform apply
   ```

4. 销毁资源：
   ```bash
   terraform destroy
   ```

## 总结

今天我们学习了：

1. 模块的概念和优点
2. 如何创建和使用模块
3. 模块版本控制方法
4. Terraform 最佳实践
5. 完整的 Web 应用程序模块示例

明天我们将学习 Terraform 的高级主题，包括工作区、策略即代码和 CI/CD 集成。