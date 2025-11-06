# Day 8: Terraform 模块发布和版本管理

## 今日学习目标

- 学习如何发布 Terraform 模块
- 掌握版本控制和语义化版本管理
- 了解模块注册表的使用
- 学习模块文档编写最佳实践
- 掌握模块版本兼容性管理

## 模块发布概述

Terraform 模块可以通过多种方式发布和共享：

1. **公共注册表**：HashiCorp Terraform Registry
2. **私有注册表**：Terraform Cloud/Enterprise 私有模块注册表
3. **Git 仓库**：直接从 Git 仓库引用模块
4. **本地路径**：本地文件系统中的模块

## 发布到公共注册表

### 准备模块

要发布到公共注册表，模块需要满足以下要求：

1. 托管在 GitHub、GitLab 或 Bitbucket 上
2. 遵循特定的仓库命名约定
3. 包含必要的文件和文档

### 仓库命名约定

```
# GitHub
github.com/{organization}/{repository}

# 符合注册表要求的命名
terraform-{provider}-{name}
# 例如：terraform-aws-web-app
```

### 必需文件

```
module-repo/
├── README.md          # 模块说明文档
├── main.tf           # 主要资源定义
├── variables.tf      # 输入变量
├── outputs.tf       # 输出值
├── LICENSE           # 许可证文件
└── CHANGELOG.md      # 变更日志
```

### 示例模块结构

```hcl
# main.tf
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type
  
  tags = var.tags
}

# variables.tf
variable "ami_id" {
  description = "AMI ID"
  type        = string
  default     = "ami-0c55b159cbfafe1d0"
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default     = {}
}

# outputs.tf
output "instance_id" {
  value = aws_instance.web.id
}

output "public_ip" {
  value = aws_instance.web.public_ip
}
```

## 版本管理

### Git 标签和版本控制

使用 Git 标签来管理模块版本：

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# 创建预发布版本
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

### 语义化版本控制

遵循语义化版本控制规范：

- **主版本号**：不兼容的API修改
- **次版本号**：向后兼容的功能性新增
- **修订号**：向后兼容的问题修正

```
v1.2.3
│ │ │
│ │ └─ 修订版本 (bug fixes)
│ └─── 次版本 (new features)
└───── 主版本 (breaking changes)
```

## 使用模块

### 从公共注册表引用

```hcl
module "web_app" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "3.2.0"
  
  name = "my-web-app"
  instance_type = "t2.micro"
}
```

### 从 Git 仓库引用

```hcl
module "web_app" {
  source = "github.com/username/terraform-aws-web-app.git"
  # 或指定特定版本
  source = "github.com/username/terraform-aws-web-app.git?ref=v1.0.0"
}
```

## 私有模块注册表

### Terraform Cloud 私有注册表

Terraform Cloud 提供私有模块注册表功能：

1. 模块自动发布到组织的私有注册表
2. 支持版本控制和访问控制
3. 与工作区集成

### 配置私有模块

```hcl
module "private_module" {
  source  = "app.terraform.io/{organization}/{module-name}/{provider}"
  version = "1.0.0"
  
  # 模块变量
}
```

## 模块文档最佳实践

### README.md 结构

```markdown
# Terraform AWS Web App Module

## 介绍

这个模块用于创建 AWS 上的 Web 应用程序基础设施。

## 使用示例

```hcl
module "web_app" {
  source = "terraform-aws-modules/ec2-instance/aws"
  
  name          = "my-web-app"
  instance_type = "t2.micro"
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| instance_type | EC2 实例类型 | string | t2.micro |

## 输出值

| 名称 | 描述 |
|------|------|
| instance_id | EC2 实例 ID |

## 许可证

MIT License
```

## CHANGELOG.md 示例

```markdown
# 变更日志

## 1.2.0 (2023-06-01)

### 新增功能
* 添加对新实例类型的支持

### 修复问题
* 修复安全组规则配置问题

## 1.1.0 (2023-05-15)

### 新增功能
* 添加标签支持
* 添加输出值

### 破坏性变更
* 移除旧的变量配置
```

## 实践练习

### 目录结构

```
examples/
├── main.tf                    # 使用模块的主配置
└── modules/
    └── web-app/              # Web 应用模块
        ├── main.tf           # 主要资源定义
        ├── variables.tf      # 输入变量
        ├── outputs.tf       # 输出值
        ├── README.md         # 模块说明文档
        └── CHANGELOG.md      # 变更日志
```

### 模块实现

#### 模块变量定义 (examples/modules/web-app/variables.tf)

```hcl
# examples/modules/web-app/variables.tf
variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
  
  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro, t2.small, 或 t2.medium 之一。"
  }
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default     = {}
}
```

#### 模块资源定义 (examples/modules/web-app/main.tf)

```hcl
# examples/modules/web-app/main.tf
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  
  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}"
      Environment = var.environment
    }
  )
}
```

#### 模块输出定义 (examples/modules/web-app/outputs.tf)

```hcl
# examples/modules/web-app/outputs.tf
output "instance_id" {
  value = aws_instance.web.id
}

output "public_ip" {
  value = aws_instance.web.public_ip
}
```

#### 模块文档 (examples/modules/web-app/README.md)

```markdown
# Web 应用模块

## 介绍

这个模块用于创建简单的 Web 应用程序 EC2 实例。

## 使用示例

```hcl
module "web_app" {
  source = "./modules/web-app"
  
  project_name  = "myapp"
  environment   = "dev"
  instance_type = "t2.micro"
  
  tags = {
    Owner = "team-a"
  }
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| project_name | 项目名称 | string | - |
| environment | 环境名称 | string | - |
| instance_type | EC2 实例类型 | string | t2.micro |
| tags | 资源标签 | map(string) | {} |

## 输出值

| 名称 | 描述 |
|------|------|
| instance_id | EC2 实例 ID |
| public_ip | EC2 实例公共 IP |

## 许可证

MIT License
```

### 使用模块

```hcl
# examples/main.tf
module "dev_web_app" {
  source = "./modules/web-app"
  
  project_name  = "webapp"
  environment   = "dev"
  instance_type = "t2.micro"
  
  tags = {
    Owner = "dev-team"
  }
}

output "web_app_info" {
  value = {
    instance_id = module.dev_web_app.instance_id
    public_ip   = module.dev_web_app.public_ip
  }
}
```

## 版本发布流程

### 1. 准备发布

```bash
# 更新 CHANGELOG.md
# 更新模块代码
# 提交更改
git add .
git commit -m "Prepare for v1.0.0 release"
```

### 2. 创建版本标签

```bash
# 创建并推送标签
git tag v1.0.0
git push origin v1.0.0
```

### 3. 验证发布

```bash
# 在另一个目录测试模块
mkdir test-module
cd test-module

# 创建测试配置
cat > main.tf << EOF
module "test" {
  source = "github.com/username/terraform-module.git?ref=v1.0.0"
  
  # 模块变量
}
EOF

# 初始化和测试
terraform init
terraform plan
```

## 总结

今天我们学习了：

1. Terraform 模块发布的方式
2. 版本控制和语义化版本管理
3. 模块注册表的使用
4. 模块文档编写最佳实践
5. 模块版本兼容性管理

明天我们将学习 Terraform 与 CI/CD 流水线的集成。