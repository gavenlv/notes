# Day 3: 资源管理与状态

## 资源依赖关系

Terraform 能够自动分析资源之间的依赖关系，确保按正确的顺序创建和销毁资源。

### 隐式依赖

当一个资源引用另一个资源的属性时，Terraform 会自动创建依赖关系。

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id  # 隐式依赖
  cidr_block = "10.0.1.0/24"
}
```

### 显式依赖

使用 `depends_on` 元参数显式指定依赖关系。

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-example-bucket"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"

  depends_on = [aws_s3_bucket.example]  # 显式依赖
}
```

## 状态管理

Terraform 状态文件（terraform.tfstate）记录了实际基础设施与配置之间的映射关系。

### 状态文件的作用

1. 映射资源配置到实际资源
2. 记录资源的元数据
3. 提高性能（避免每次都查询API）
4. 支持协作（通过远程状态）

### 本地状态 vs 远程状态

默认情况下，Terraform 使用本地状态文件。在团队环境中，应使用远程状态。

```hcl
terraform {
  backend "s3" {
    bucket = "my-terraform-state-bucket"
    key    = "network/terraform.tfstate"
    region = "us-west-2"
  }
}
```

## 资源生命周期

### 创建资源

```bash
terraform apply
```

### 更新资源

修改配置后再次运行：
```bash
terraform apply
```

### 销毁资源

```bash
terraform destroy
```

### 仅计划变更

```bash
terraform plan
```

## 导入现有资源

将现有基础设施导入 Terraform 管理：

```bash
terraform import aws_instance.example i-1234567890abcdef0
```

## 实践练习

创建一个包含 VPC、子网和安全组的网络基础设施，并管理其状态。

### 配置文件

以下是我们将在练习中使用的配置文件结构：

```
examples/
├── main.tf      # 主要资源定义
├── variables.tf # 变量定义
├── outputs.tf   # 输出定义
└── backend.tf   # 后端配置
```

#### 变量定义 (variables.tf)

首先，我们定义需要的变量：

```hcl
# variables.tf
variable "region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
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

variable "ami_id" {
  description = "AMI ID"
  type        = string
  default     = "ami-0c55b159cbfafe1d0"  # Amazon Linux 2
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}
```

#### 后端配置 (backend.tf)

接下来，我们配置 Terraform 后端以管理状态：

```hcl
# backend.tf
# 本地后端（默认）
# terraform {
#   backend "local" {
#     path = "terraform.tfstate"
#   }
# }

# S3 后端配置（用于远程状态存储）
# 需要先手动创建 S3 存储桶和 DynamoDB 表
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "day3/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

# Azure Storage 后端配置示例
# terraform {
#   backend "azurerm" {
#     storage_account_name = "myterraformstorage"
#     container_name       = "terraform-state"
#     key                  = "day3/terraform.tfstate"
#   }
# }

# Google Cloud Storage 后端配置示例
# terraform {
#   backend "gcs" {
#     bucket = "my-terraform-state-bucket"
#     prefix = "day3"
#   }
# }
```

#### 主要资源定义 (main.tf)

现在，我们定义基础设施的主要资源，包括资源依赖关系：

```hcl
# main.tf
# 创建 VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "MainVPC"
  }
}

# 创建互联网网关（依赖 VPC）
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "MainIGW"
  }
}

# 创建路由表（依赖 VPC）
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "PublicRouteTable"
  }
}

# 创建子网（依赖 VPC）
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "PublicSubnet"
  }
}

# 关联路由表和子网（依赖两者）
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# 创建安全组（依赖 VPC）
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  # HTTP 访问
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS 访问
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH 访问（仅来自 VPC 内部）
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # 允许所有出站流量
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "WebServerSG"
  }
}

# 创建 EC2 实例（依赖子网和安全组）
resource "aws_instance" "web" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true

  tags = {
    Name = "WebServer"
  }

  # 显式依赖（虽然隐式依赖已存在）
  depends_on = [
    aws_route_table_association.public
  ]
}
```

#### 输出定义 (outputs.tf)

最后，我们定义输出值以便在应用后获取重要信息：

```hcl
# outputs.tf
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "创建的 VPC ID"
}

output "vpc_cidr" {
  value       = aws_vpc.main.cidr_block
  description = "VPC CIDR 块"
}

output "internet_gateway_id" {
  value       = aws_internet_gateway.main.id
  description = "互联网网关 ID"
}

output "subnet_id" {
  value       = aws_subnet.public.id
  description = "公共子网 ID"
}

output "subnet_cidr" {
  value       = aws_subnet.public.cidr_block
  description = "子网 CIDR 块"
}

output "route_table_id" {
  value       = aws_route_table.public.id
  description = "路由表 ID"
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

output "instance_private_ip" {
  value       = aws_instance.web.private_ip
  description = "EC2 实例私有 IP"
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

4. 查看状态：
   ```bash
   terraform show
   ```

5. 列出状态中的资源：
   ```bash
   terraform state list
   ```

6. 查看特定资源状态：
   ```bash
   terraform state show aws_vpc.main
   ```

7. 销毁资源：
   ```bash
   terraform destroy
   ```

## 状态操作命令

### 查看状态

```bash
terraform show
```

### 列出状态中的资源

```bash
terraform state list
```

### 查看特定资源状态

```bash
terraform state show aws_vpc.main
```

### 移除状态中的资源（不删除实际资源）

```bash
terraform state rm aws_instance.example
```

### 将资源移动到不同地址

```bash
terraform state mv aws_instance.old aws_instance.new
```

## 总结

今天我们学习了：

1. 资源依赖关系（隐式和显式）
2. 状态管理的重要性及本地/远程状态的区别
3. 资源生命周期管理
4. 如何导入现有资源
5. 状态操作命令的使用

明天我们将学习变量、输出和模块的使用。