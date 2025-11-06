# Day 9: Terraform 状态管理

## 学习目标

完成本章后，您将能够：
- 理解 Terraform 状态文件的作用和重要性
- 掌握本地状态和远程状态的区别
- 配置和使用 S3 和 DynamoDB 进行远程状态存储
- 实现状态锁定以防止并发修改
- 管理状态文件的版本和备份
- 使用 `terraform import` 导入现有资源到状态文件

## Terraform 状态概述

Terraform 状态文件（默认为 `terraform.tfstate`）是 Terraform 用来存储有关托管基础设施的元数据的文件。它包含资源与配置的映射关系，使 Terraform 能够了解当前基础设施的状态。

### 状态文件的重要性

1. **资源映射**：将配置中的资源与实际创建的云资源进行映射
2. **依赖关系**：跟踪资源之间的依赖关系
3. **性能优化**：避免每次运行时都查询所有资源的状态
4. **协作**：允许多个团队成员共享基础设施状态

## 本地状态 vs 远程状态

### 本地状态

本地状态文件存储在运行 Terraform 命令的机器上。这种方式适合个人开发或测试环境，但在团队协作中存在以下问题：

- 状态文件不同步，可能导致资源冲突
- 缺乏状态锁定，可能造成并发修改问题
- 状态文件容易丢失，导致基础设施状态不可知

### 远程状态

远程状态将状态文件存储在共享存储中（如 S3），解决了本地状态的诸多问题：

- 状态文件集中管理，团队成员可以共享
- 支持状态锁定，防止并发修改
- 提供状态文件版本管理和备份

## 配置 S3 远程状态

### 创建 S3 存储桶和 DynamoDB 表

在使用 S3 作为远程状态存储之前，需要先创建 S3 存储桶和 DynamoDB 表用于状态锁定。

```hcl
# s3-backend-setup/main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state-bucket-unique-id"
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### 配置后端

在 Terraform 配置中添加后端配置：

```hcl
# main.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket-unique-id"
    key            = "terraform/state.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-west-2"
}

# 其他资源配置...
```

### 初始化远程状态

配置后端后，需要重新初始化 Terraform：

```bash
terraform init
```

系统会提示是否迁移本地状态到远程状态，输入 `yes` 确认迁移。

## 状态锁定

状态锁定是远程状态的重要特性，防止多个用户同时修改基础设施导致冲突。

当启用 DynamoDB 表用于状态锁定后，Terraform 会在执行修改操作时自动获取锁，并在操作完成后释放锁。

### 手动解锁

如果由于异常情况导致锁未被正确释放，可以使用以下命令手动解锁：

```bash
terraform force-unlock LOCK_ID
```

LOCK_ID 可以从 DynamoDB 表中查询获得。

## 状态文件管理

### 状态文件版本管理

启用 S3 版本控制后，每次状态文件更新都会创建新版本，可以回滚到之前的版本。

### 状态文件备份

定期备份状态文件到其他存储位置，防止数据丢失。

### 状态文件加密

S3 后端支持服务器端加密，确保状态文件在存储时被加密。

## 导入现有资源

使用 `terraform import` 命令可以将现有云资源导入到 Terraform 状态文件中。

### 导入步骤

1. 在配置文件中添加资源定义：

```hcl
resource "aws_instance" "imported_instance" {
  # 配置参数...
}
```

2. 执行导入命令：

```bash
terraform import aws_instance.imported_instance i-1234567890abcdef0
```

3. 调整配置以匹配实际资源状态

4. 运行 `terraform plan` 确保配置与实际状态一致

## 实践练习

### 目录结构

```
day9-state-management/
├── examples/
│   ├── s3-backend-setup/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── web-app/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── state-management.md
```

### 配置 S3 后端设置

创建 `examples/s3-backend-setup/main.tf`：

```hcl
provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

创建 `examples/s3-backend-setup/variables.tf`：

```hcl
variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "bucket_name" {
  description = "S3 存储桶名称"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB 表名称"
  type        = string
  default     = "terraform-state-locks"
}
```

创建 `examples/s3-backend-setup/outputs.tf`：

```hcl
output "s3_bucket_name" {
  value = aws_s3_bucket.terraform_state.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}
```

### 配置 Web 应用

创建 `examples/web-app/main.tf`：

```hcl
terraform {
  backend "s3" {
    bucket         = var.backend_bucket
    key            = "web-app/terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = var.dynamodb_table
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  
  tags = {
    Name        = "web-app-instance"
    Environment = var.environment
  }
}
```

创建 `examples/web-app/variables.tf`：

```hcl
variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "环境名称"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}

variable "backend_bucket" {
  description = "后端 S3 存储桶名称"
  type        = string
}

variable "dynamodb_table" {
  description = "DynamoDB 表名称"
  type        = string
}
```

创建 `examples/web-app/outputs.tf`：

```hcl
output "instance_id" {
  value = aws_instance.web.id
}

output "public_ip" {
  value = aws_instance.web.public_ip
}
```

### 使用步骤

1. 首先创建 S3 存储桶和 DynamoDB 表：
   ```bash
   cd examples/s3-backend-setup
   terraform init
   terraform apply -var="bucket_name=my-unique-terraform-state-bucket"
   ```

2. 记录输出的存储桶名称和 DynamoDB 表名称

3. 部署 Web 应用并使用远程状态：
   ```bash
   cd ../web-app
   terraform init
   terraform apply -var="backend_bucket=上一步的存储桶名称" -var="dynamodb_table=上一步的表名称"
   ```

通过以上步骤，您将学会如何配置和使用 Terraform 远程状态，实现安全的团队协作基础设施管理。