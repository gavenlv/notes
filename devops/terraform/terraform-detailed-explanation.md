# Terraform 详细讲解：核心概念与代码示例

本文档将详细讲解 Terraform 的核心概念，包括 resource、variable、output 等主要类型，并提供详细的代码示例和解释。

## 1. Terraform 基础概念

### 1.1 什么是 Terraform？

Terraform 是一个开源的基础设施即代码（Infrastructure as Code）工具，由 HashiCorp 开发。它使用声明式配置语言（HCL）来描述和配置云基础设施。

### 1.2 Terraform 工作流程

1. **编写配置**：使用 HCL 语言编写基础设施配置
2. **初始化**：`terraform init` - 下载提供商插件
3. **计划**：`terraform plan` - 预览将要进行的更改
4. **应用**：`terraform apply` - 执行配置更改
5. **销毁**：`terraform destroy` - 清理资源

## 2. Resource（资源）类型详解

Resource 是 Terraform 中最核心的概念，用于定义和管理基础设施资源。

### 2.1 Resource 基本语法

```hcl
resource "provider_type" "resource_name" {
  # 资源配置参数
  parameter1 = value1
  parameter2 = value2
  
  # 元参数（可选）
  count      = number
  for_each   = set
  depends_on = [resource.list]
  lifecycle {
    create_before_destroy = true
    prevent_destroy      = true
    ignore_changes       = [parameter]
  }
}
```

### 2.2 Resource 示例：AWS EC2 实例

```hcl
# 定义 AWS 提供商
provider "aws" {
  region = "us-west-2"
}

# 创建 VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main-vpc"
  }
}

# 创建子网
resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  
  tags = {
    Name = "main-subnet"
  }
}

# 创建安全组
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow web traffic"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "web-security-group"
  }
}

# 创建 EC2 实例
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.main.id
  
  vpc_security_group_ids = [aws_security_group.web.id]
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
              EOF
  
  tags = {
    Name = "web-server"
  }
  
  # 生命周期配置
  lifecycle {
    create_before_destroy = true
    ignore_changes       = [ami]
  }
}
```

### 2.3 Resource 元参数详解

#### count：创建多个相同资源
```hcl
resource "aws_instance" "web_servers" {
  count = 3
  
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  
  tags = {
    Name = "web-server-${count.index}"
  }
}
```

#### for_each：基于集合创建资源
```hcl
variable "server_configs" {
  type = map(object({
    instance_type = string
    ami           = string
  }))
  default = {
    web = {
      instance_type = "t2.micro"
      ami           = "ami-0c02fb55956c7d316"
    }
    app = {
      instance_type = "t2.small"
      ami           = "ami-0c02fb55956c7d316"
    }
  }
}

resource "aws_instance" "servers" {
  for_each = var.server_configs
  
  ami           = each.value.ami
  instance_type = each.value.instance_type
  
  tags = {
    Name = each.key
  }
}
```

#### depends_on：显式依赖关系
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

resource "aws_iam_role" "lambda" {
  name = "lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_lambda_function" "processor" {
  filename      = "lambda.zip"
  function_name = "data-processor"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  
  # 显式声明依赖关系
  depends_on = [
    aws_s3_bucket.data,
    aws_iam_role.lambda
  ]
}
```

## 3. Variable（变量）类型详解

Variable 用于参数化 Terraform 配置，使配置更加灵活和可重用。

### 3.1 Variable 基本语法

```hcl
variable "variable_name" {
  type        = data_type
  default     = default_value
  description = "变量描述"
  
  # 验证规则（可选）
  validation {
    condition     = validation_condition
    error_message = "错误提示信息"
  }
  
  # 敏感变量（可选）
  sensitive = true
}
```

### 3.2 Variable 类型示例

#### 基本类型变量
```hcl
# 字符串变量
variable "region" {
  type        = string
  default     = "us-west-2"
  description = "AWS 区域"
}

# 数字变量
variable "instance_count" {
  type        = number
  default     = 1
  description = "实例数量"
}

# 布尔变量
variable "enable_monitoring" {
  type        = bool
  default     = true
  description = "是否启用监控"
}

# 列表变量
variable "availability_zones" {
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b"]
  description = "可用区列表"
}

# 映射变量
variable "tags" {
  type = map(string)
  default = {
    Environment = "development"
    Project     = "terraform-demo"
    Owner       = "devops-team"
  }
  description = "资源标签"
}

# 对象变量
variable "database_config" {
  type = object({
    engine         = string
    engine_version = string
    instance_class = string
    storage_size   = number
    multi_az       = bool
  })
  default = {
    engine         = "mysql"
    engine_version = "8.0"
    instance_class = "db.t3.micro"
    storage_size   = 20
    multi_az       = false
  }
  description = "数据库配置"
}

# 集合变量
variable "security_groups" {
  type        = set(string)
  default     = ["sg-12345678", "sg-87654321"]
  description = "安全组ID集合"
}
```

#### 带验证的变量
```hcl
variable "instance_type" {
  type        = string
  default     = "t2.micro"
  description = "EC2 实例类型"
  
  validation {
    condition     = can(regex("^[t][23]\\.(micro|small|medium)$", var.instance_type))
    error_message = "实例类型必须是 t2.micro、t2.small、t2.medium、t3.micro、t3.small 或 t3.medium。"
  }
}

variable "cidr_block" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR 块"
  
  validation {
    condition     = can(cidrnetmask(var.cidr_block))
    error_message = "必须是有效的 CIDR 表示法。"
  }
}

variable "port_number" {
  type        = number
  default     = 80
  description = "端口号"
  
  validation {
    condition     = var.port_number > 0 && var.port_number <= 65535
    error_message = "端口号必须在 1-65535 范围内。"
  }
}
```

#### 敏感变量
```hcl
variable "database_password" {
  type        = string
  description = "数据库密码"
  sensitive   = true
}

variable "api_key" {
  type        = string
  description = "API 密钥"
  sensitive   = true
}
```

### 3.3 变量文件（terraform.tfvars）

```hcl
# terraform.tfvars
region           = "us-east-1"
instance_count   = 3
enable_monitoring = true

availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

tags = {
  Environment = "production"
  Project     = "ecommerce"
  Team        = "infrastructure"
}

database_config = {
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.medium"
  storage_size   = 100
  multi_az       = true
}
```

## 4. Output（输出）类型详解

Output 用于从 Terraform 配置中导出值，可以在其他配置中引用或显示给用户。

### 4.1 Output 基本语法

```hcl
output "output_name" {
  value       = expression
  description = "输出描述"
  
  # 敏感输出（可选）
  sensitive = true
  
  # 依赖关系（可选）
  depends_on = [resource.list]
}
```

### 4.2 Output 示例

#### 基本输出
```hcl
# 输出实例ID
output "instance_id" {
  value       = aws_instance.web_server.id
  description = "EC2 实例ID"
}

# 输出公共IP
output "public_ip" {
  value       = aws_instance.web_server.public_ip
  description = "EC2 实例公共IP地址"
}

# 输出私有IP
output "private_ip" {
  value       = aws_instance.web_server.private_ip
  description = "EC2 实例私有IP地址"
}

# 输出VPC ID
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

# 输出子网ID列表
output "subnet_ids" {
  value       = aws_subnet.main[*].id
  description = "子网ID列表"
}

# 输出安全组ID
output "security_group_id" {
  value       = aws_security_group.web.id
  description = "安全组ID"
}
```

#### 复杂输出
```hcl
# 输出实例详细信息
output "instance_details" {
  value = {
    id         = aws_instance.web_server.id
    public_ip  = aws_instance.web_server.public_ip
    private_ip = aws_instance.web_server.private_ip
    az         = aws_instance.web_server.availability_zone
    type       = aws_instance.web_server.instance_type
  }
  description = "EC2 实例详细信息"
}

# 输出多个实例的信息
output "all_instances" {
  value = {
    for instance in aws_instance.web_servers :
    instance.tags.Name => {
      id        = instance.id
      public_ip = instance.public_ip
      az        = instance.availability_zone
    }
  }
  description = "所有实例的信息"
}

# 输出负载均衡器DNS
output "load_balancer_dns" {
  value       = aws_lb.web.dns_name
  description = "负载均衡器DNS名称"
}

# 输出数据库连接信息
output "database_endpoint" {
  value       = aws_db_instance.main.endpoint
  description = "数据库连接端点"
  sensitive   = true
}

# 输出S3桶信息
output "s3_bucket_arn" {
  value       = aws_s3_bucket.data.arn
  description = "S3桶ARN"
}

output "s3_bucket_domain_name" {
  value       = aws_s3_bucket.data.bucket_domain_name
  description = "S3桶域名"
}
```

#### 条件输出
```hcl
# 根据条件输出不同的值
output "website_url" {
  value = var.enable_https ? 
    "https://${aws_cloudfront_distribution.web.domain_name}" : 
    "http://${aws_lb.web.dns_name}"
  description = "网站URL"
}

# 输出可选资源（如果存在）
output "optional_resource_id" {
  value = try(aws_optional_resource.example[0].id, null)
  description = "可选资源ID（如果存在）"
}
```

## 5. 其他重要类型

### 5.1 Data Source（数据源）

Data Source 用于从现有基础设施中读取数据，而不是创建新资源。

```hcl
# 获取最新的 Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# 获取可用区数据
data "aws_availability_zones" "available" {
  state = "available"
}

# 获取当前调用者信息
data "aws_caller_identity" "current" {}

# 使用数据源
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  
  availability_zone = data.aws_availability_zones.available.names[0]
  
  tags = {
    CreatedBy = data.aws_caller_identity.current.arn
  }
}

# 输出数据源信息
output "latest_ami_id" {
  value       = data.aws_ami.amazon_linux_2.id
  description = "最新的 Amazon Linux 2 AMI ID"
}

output "available_zones" {
  value       = data.aws_availability_zones.available.names
  description = "可用区列表"
}
```

### 5.2 Local Values（局部变量）

Local Values 用于在配置中定义可重用的表达式。

```hcl
# 定义局部变量
locals {
  # 基础配置
  project_name = "my-project"
  environment  = terraform.workspace
  
  # 计算值
  vpc_cidr = "10.${var.region_number}.0.0/16"
  
  # 复合标签
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "Terraform"
    CreatedAt   = timestamp()
  }
  
  # 基于条件的值
  instance_type = var.environment == "production" ? "t3.medium" : "t2.micro"
  
  # 列表操作
  all_subnets = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
  
  # 映射操作
  instance_configs = {
    for idx, config in var.instance_configs :
    "instance-${idx}" => {
      ami           = config.ami
      instance_type = config.type
      subnet_id     = element(aws_subnet.public[*].id, idx % length(aws_subnet.public))
    }
  }
}

# 使用局部变量
resource "aws_vpc" "main" {
  cidr_block = local.vpc_cidr
  tags       = local.common_tags
}

resource "aws_instance" "web" {
  for_each = local.instance_configs
  
  ami           = each.value.ami
  instance_type = each.value.instance_type
  subnet_id     = each.value.subnet_id
  
  tags = merge(local.common_tags, {
    Name = each.key
  })
}

# 输出局部变量
output "project_info" {
  value = {
    project_name = local.project_name
    environment  = local.environment
    vpc_cidr     = local.vpc_cidr
  }
}
```

### 5.3 Module（模块）

Module 用于组织和重用 Terraform 配置。

```hcl
# 调用子模块
module "vpc" {
  source = "./modules/vpc"
  
  # 模块参数
  vpc_name     = "main-vpc"
  vpc_cidr     = "10.0.0.0/16"
  azs          = ["us-west-2a", "us-west-2b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.10.0/24", "10.0.20.0/24"]
  
  # 标签
  tags = {
    Environment = "production"
    Project     = "ecommerce"
  }
}

module "ec2" {
  source = "./modules/ec2"
  
  # 依赖模块输出
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  private_subnet_ids  = module.vpc.private_subnet_ids
  security_group_id   = module.vpc.web_sg_id
  
  # EC2 配置
  instance_type = "t3.micro"
  instance_count = 2
  
  tags = {
    Environment = "production"
    Role        = "web-server"
  }
}

# 使用模块输出
output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "VPC ID"
}

output "web_instance_ips" {
  value       = module.ec2.instance_ips
  description = "Web 实例IP地址"
}

output "load_balancer_url" {
  value       = module.ec2.lb_dns_name
  description = "负载均衡器URL"
}
```

## 6. 完整示例：Web 应用基础设施

下面是一个完整的 Terraform 配置示例，展示如何组合使用各种类型：

```hcl
# main.tf

# 提供商配置
provider "aws" {
  region = var.region
}

# 数据源
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 局部变量
locals {
  project_name = "web-app"
  environment  = var.environment
  
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "Terraform"
  }
  
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# VPC 资源
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-vpc"
  })
}

# 子网资源
resource "aws_subnet" "public" {
  count = length(local.azs)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-public-${count.index}"
    Type = "public"
  })
}

resource "aws_subnet" "private" {
  count = length(local.azs)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = local.azs[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-private-${count.index}"
    Type = "private"
  })
}

# 安全组
resource "aws_security_group" "web" {
  name        = "${local.project_name}-web-sg"
  description = "Web服务器安全组"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = local.common_tags
}

# EC2 实例
resource "aws_instance" "web" {
  count = var.instance_count
  
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public[count.index % length(aws_subnet.public)].id
  
  vpc_security_group_ids = [aws_security_group.web.id]
  
  user_data = templatefile("${path.module}/user_data.sh", {
    environment = local.environment
  })
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-web-${count.index}"
  })
  
  lifecycle {
    create_before_destroy = true
  }
}

# 输出定义
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "subnet_ids" {
  value = {
    public  = aws_subnet.public[*].id
    private = aws_subnet.private[*].id
  }
  description = "子网ID列表"
}

output "instance_ips" {
  value = {
    for idx, instance in aws_instance.web :
    "web-${idx}" => {
      public_ip  = instance.public_ip
      private_ip = instance.private_ip
      az         = instance.availability_zone
    }
  }
  description = "实例IP地址信息"
}

output "security_group_id" {
  value       = aws_security_group.web.id
  description = "安全组ID"
}
```

```hcl
# variables.tf

variable "region" {
  type        = string
  default     = "us-west-2"
  description = "AWS 区域"
}

variable "environment" {
  type        = string
  default     = "development"
  description = "环境名称"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "环境必须是 development、staging 或 production。"
  }
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR 块"
}

variable "instance_count" {
  type        = number
  default     = 2
  description = "实例数量"
  
  validation {
    condition     = var.instance_count >= 1 && var.instance_count <= 10
    error_message = "实例数量必须在 1-10 范围内。"
  }
}

variable "instance_type" {
  type        = string
  default     = "t3.micro"
  description = "实例类型"
}

variable "admin_cidr" {
  type        = string
  default     = "10.0.0.0/8"
  description = "管理员CIDR块"
}
```

```bash
# user_data.sh
#!/bin/bash

# 安装和配置Web服务器
yum update -y
yum install -y httpd

systemctl start httpd
systemctl enable httpd

# 创建简单的首页
cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Web App</title>
</head>
<body>
    <h1>Welcome to ${environment} Environment!</h1>
    <p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>
    <p>Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)</p>
</body>
</html>
EOF

# 设置适当的权限
chown apache:apache /var/www/html/index.html
```

## 7. 总结

通过本文档的详细讲解，您应该已经掌握了 Terraform 的核心概念：

1. **Resource**：定义和管理基础设施资源的核心构建块
2. **Variable**：参数化配置，提高灵活性和可重用性
3. **Output**：导出配置值，便于引用和显示
4. **Data Source**：读取现有基础设施信息
5. **Local Values**：定义可重用的表达式
6. **Module**：组织和重用 Terraform 配置

每种类型都有其特定的语法和用途，合理组合使用这些类型可以创建出强大、灵活且可维护的基础设施代码。在实际使用中，建议遵循 Terraform 的最佳实践，如模块化设计、状态管理、版本控制等。