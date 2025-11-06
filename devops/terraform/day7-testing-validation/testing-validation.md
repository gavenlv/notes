# Day 7: Terraform 测试和验证最佳实践

## 今日学习目标

- 学习 Terraform 测试的不同类型
- 掌握单元测试和集成测试的方法
- 了解 Terratest 框架的使用
- 学习如何验证基础设施配置
- 掌握调试和故障排除技巧

## Terraform 测试概述

Terraform 测试是确保基础设施代码质量和可靠性的关键环节。主要有以下几种测试类型：

1. **单元测试**：验证单个模块或组件的功能
2. **集成测试**：验证多个组件协同工作的效果
3. **端到端测试**：验证整个基础设施部署流程
4. **合规性测试**：验证基础设施是否符合安全和合规要求

## 单元测试

单元测试关注于验证单个 Terraform 模块的功能。通常使用以下方法：

### 输入验证

通过变量验证确保输入参数符合预期：

```hcl
# variables.tf
variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  
  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro, t2.small, 或 t2.medium 之一。"
  }
}
```

### 输出验证

确保模块输出符合预期格式：

```hcl
# outputs.tf
output "instance_ip" {
  value = aws_instance.web.public_ip
  
  precondition {
    condition     = aws_instance.web.public_ip != null
    error_message = "实例必须具有公共 IP 地址。"
  }
}
```

## 集成测试

集成测试验证多个模块或组件之间的交互。通常使用 Terratest 框架进行：

### Terratest 简介

Terratest 是一个 Go 语言编写的测试框架，专门用于测试基础设施代码。

### 示例测试代码

```go
// main_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestTerraformModule(t *testing.T) {
    // 配置 Terraform 选项
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples",
        Vars: map[string]interface{}{
            "instance_type": "t2.micro",
        },
    }

    // 清理资源
    defer terraform.Destroy(t, terraformOptions)

    // 部署基础设施
    terraform.InitAndApply(t, terraformOptions)

    // 获取输出
    instanceIP := terraform.Output(t, terraformOptions, "instance_ip")

    // 验证输出
    assert.NotEmpty(t, instanceIP)
}
```

## 端到端测试

端到端测试模拟真实的部署场景，验证整个基础设施的部署流程。

### 测试流程

1. 准备测试环境
2. 执行部署
3. 验证资源
4. 清理资源

### 示例端到端测试

```go
// e2e_test.go
package test

import (
    "testing"
    "time"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/http-helper"
)

func TestEndToEndDeployment(t *testing.T) {
    // 配置选项
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples",
        Vars: map[string]interface{}{
            "environment": "test",
        },
    }

    // 清理
    defer terraform.Destroy(t, terraformOptions)

    // 部署
    terraform.InitAndApply(t, terraformOptions)

    // 获取实例 IP
    instanceIP := terraform.Output(t, terraformOptions, "instance_ip")

    // 等待服务启动
    time.Sleep(30 * time.Second)

    // 验证 HTTP 服务
    http_helper.HttpGetWithRetry(t, fmt.Sprintf("http://%s", instanceIP), 200, "Hello", 30, 5*time.Second)
}
```

## 合规性测试

合规性测试确保基础设施符合安全和合规要求。

### 使用 Sentinel 进行策略检查

```sentinel
# restrict-instance-types.sentinel
import "tfplan"

allowed_types = ["t2.micro", "t2.small", "t2.medium"]

main = rule {
    all tfplan.resources.aws_instance as _, instances {
        all instances as _, instance {
            instance.applied.instance_type in allowed_types
        }
    }
}
```

## 实践练习

### 目录结构

```
examples/
├── main.tf           # 主配置文件
├── variables.tf      # 变量定义
├── outputs.tf       # 输出定义
└── test/
    ├── main_test.go  # 单元测试
    └── e2e_test.go   # 端到端测试
```

### 配置文件

#### 变量定义 (examples/variables.tf)

```hcl
# examples/variables.tf
variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
  
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "环境必须是 dev, test, 或 prod 之一。"
  }
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
```

#### 主配置文件 (examples/main.tf)

```hcl
# examples/main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type

  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Environment = var.environment
  }
}
```

#### 输出定义 (examples/outputs.tf)

```hcl
# examples/outputs.tf
output "instance_id" {
  value = aws_instance.web.id
}

output "instance_ip" {
  value = aws_instance.web.public_ip
  
  precondition {
    condition     = aws_instance.web.public_ip != null
    error_message = "实例必须具有公共 IP 地址。"
  }
}
```

### 测试代码

#### 单元测试 (examples/test/main_test.go)

```go
// examples/test/main_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestInstanceTypeValidation(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "..",
        Vars: map[string]interface{}{
            "project_name":  "test-project",
            "environment":   "dev",
            "instance_type": "invalid-type",
        },
    }

    // 预期部署会失败
    _, err := terraform.InitAndPlanE(t, terraformOptions)
    assert.Error(t, err)
}

func TestValidInstanceType(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "..",
        Vars: map[string]interface{}{
            "project_name":  "test-project",
            "environment":   "dev",
            "instance_type": "t2.micro",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    
    terraform.InitAndApply(t, terraformOptions)
    
    instanceID := terraform.Output(t, terraformOptions, "instance_id")
    assert.NotEmpty(t, instanceID)
}
```

### 执行测试

1. 安装依赖：
   ```bash
   go mod init terraform-test
   go mod tidy
   ```

2. 运行单元测试：
   ```bash
   go test -v ./test
   ```

3. 运行特定测试：
   ```bash
   go test -v ./test -run TestValidInstanceType
   ```

## 调试和故障排除

### 使用 TF_LOG 进行调试

```bash
export TF_LOG=DEBUG
terraform apply
```

### 使用 Terraform Console

```bash
terraform console
> var.instance_type
> aws_instance.web.*.id
```

## 总结

今天我们学习了：

1. Terraform 测试的不同类型
2. 单元测试和集成测试的方法
3. Terratest 框架的使用
4. 合规性测试和策略实施
5. 调试和故障排除技巧

明天我们将学习 Terraform 的模块发布和版本管理。