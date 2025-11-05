# Day 2: Terraform 基础概念与配置语法

## Terraform 配置语言 (HCL)

Terraform 使用 HashiCorp 配置语言 (HCL) 来定义基础设施。HCL 的设计目标是既对人类友好，又对机器友好。

## 基本语法结构

### 资源 (Resources)

资源是 Terraform 中最重要的元素，代表基础设施中的一个组件。

```hcl
resource "类型" "名称" {
  配置参数 = 值
  # ...
}
```

示例：
```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "HelloWorld"
  }
}
```

### 提供商 (Providers)

提供商是 Terraform 与基础设施 API 交互的插件。

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}
```

### 变量 (Variables)

变量允许您在配置中使用参数化值。

```hcl
variable "instance_type" {
  description = "EC2实例类型"
  type        = string
  default     = "t2.micro"
}

resource "aws_instance" "example" {
  instance_type = var.instance_type
  # ...
}
```

### 输出 (Outputs)

输出允许您从 Terraform 配置中导出数据。

```hcl
output "instance_ip" {
  value = aws_instance.example.public_ip
}
```

## 配置文件组织

### 推荐的文件结构

```
terraform-project/
├── main.tf          # 主要资源定义
├── variables.tf     # 变量定义
├── outputs.tf       # 输出定义
├── providers.tf     # 提供商配置
└── terraform.tfvars # 变量值（不提交到版本控制）
```

## 数据类型

### 基本类型

- `string`: 字符串
- `number`: 数字
- `bool`: 布尔值

### 复杂类型

- `list(...)`: 列表
- `map(...)`: 映射
- `object({...})`: 对象
- `tuple([...])`: 元组

示例：
```hcl
variable "example_list" {
  type = list(string)
  default = ["one", "two", "three"]
}

variable "example_map" {
  type = map(string)
  default = {
    key1 = "value1"
    key2 = "value2"
  }
}
```

## 表达式和函数

### 引用其他值

```hcl
resource "aws_instance" "example" {
  # 引用变量
  instance_type = var.instance_type
  
  # 引用其他资源的属性
  subnet_id = aws_subnet.main.id
  
  # 引用数据源
  ami = data.aws_ami.ubuntu.id
}
```

### 常用函数

```hcl
# 字符串函数
upper("hello")          # "HELLO"
lower("HELLO")          # "hello"

# 列表函数
length(var.list)        # 列表长度
element(var.list, 0)    # 获取列表第一个元素

# 条件函数
condition ? true_val : false_val
```

## 实践练习

让我们创建一个简单的 AWS 基础设施来练习所学概念。

### 练习目标

1. 创建一个 VPC 和两个子网
2. 使用变量定义区域和网络配置
3. 输出创建的资源信息
4. 使用本地文件提供程序创建配置文件

### 配置文件

以下是我们将在练习中使用的配置文件结构：

```
examples/
├── main.tf      # 主要资源定义
├── variables.tf # 变量定义
├── outputs.tf   # 输出定义
└── providers.tf # 提供商配置
```

#### 提供商配置 (providers.tf)

首先，我们需要配置 Terraform 所需的提供商：

```hcl
# providers.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.4.0"
    }
  }
  
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.region
}

provider "local" {
  # 本地提供商通常不需要特殊配置
}
```

#### 变量定义 (variables.tf)

接下来，我们定义需要的变量：

```hcl
# variables.tf
variable "region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "instance_count" {
  description = "实例数量"
  type        = number
  default     = 1
}

variable "enable_monitoring" {
  description = "是否启用监控"
  type        = bool
  default     = true
}

variable "instance_types" {
  description = "实例类型列表"
  type        = list(string)
  default     = ["t2.micro", "t2.small", "t2.medium"]
}

variable "ami_ids" {
  description = "不同区域的 AMI ID 映射"
  type        = map(string)
  default = {
    us-west-1 = "ami-0b000c9e6a0a0d0e0"
    us-west-2 = "ami-0c55b159cbfafe1d0"
    us-east-1 = "ami-0947d2ba4a522fdee"
  }
}

variable "network_config" {
  description = "网络配置"
  type = object({
    vpc_cidr     = string
    subnet_cidrs = list(string)
  })
  default = {
    vpc_cidr     = "10.0.0.0/16"
    subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  }
}
```

#### 主要资源定义 (main.tf)

现在，我们定义基础设施的主要资源：

```hcl
# main.tf
resource "aws_vpc" "main" {
  cidr_block = var.network_config.vpc_cidr

  tags = {
    Name = "MainVPC"
  }
}

resource "aws_subnet" "public" {
  count = length(var.network_config.subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.network_config.subnet_cidrs[count.index]
  availability_zone = "${var.region}${count.index == 0 ? "a" : "b"}"

  tags = {
    Name = "PublicSubnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "MainIGW"
  }
}

resource "local_file" "config" {
  content  = <<-EOF
    VPC ID: ${aws_vpc.main.id}
    Region: ${var.region}
    Subnets: ${join(", ", aws_subnet.public[*].id)}
  EOF
  filename = "${path.module}/network-config.txt"
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

output "subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "创建的子网 ID 列表"
}

output "subnet_cidrs" {
  value       = aws_subnet.public[*].cidr_block
  description = "子网 CIDR 块列表"
}

output "internet_gateway_id" {
  value       = aws_internet_gateway.main.id
  description = "互联网网关 ID"
}

output "config_file_path" {
  value       = local_file.config.filename
  description = "生成的配置文件路径"
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

4. 查看生成的配置文件：
   ```bash
   cat network-config.txt
   ```

5. 销毁资源：
   ```bash
   terraform destroy
   ```

## 总结

今天我们学习了：

1. Terraform 配置语言 (HCL) 的基本语法
2. 资源、提供商、变量和输出的概念
3. 推荐的配置文件组织方式
4. 基本数据类型和表达式
5. 通过实践练习巩固了所学知识

明天我们将深入学习资源管理与状态的概念。