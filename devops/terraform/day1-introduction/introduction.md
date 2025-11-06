# Day 1: Terraform 简介与安装

## 什么是 Terraform？

Terraform 是由 HashiCorp 开发的一个开源工具，用于基础设施即代码（Infrastructure as Code, IaC）。它允许您使用声明式配置文件来定义和预配基础设施资源，如虚拟机、存储、网络接口等。

## 核心特性

### 声明式语法
Terraform 使用声明式语法，您只需描述所需的最终状态，而不需要指定如何达到该状态的步骤。

### 提供商无关
Terraform 支持多种云提供商（AWS、Azure、GCP、阿里云等）以及本地基础设施。

### 状态管理
Terraform 维护基础设施的状态，确保配置与实际资源保持同步。

### 执行计划
在应用更改之前，Terraform 会显示将要执行的操作，让您提前了解变更影响。

## 安装 Terraform

### Windows

1. 访问 [Terraform 下载页面](https://www.terraform.io/downloads.html)
2. 下载适用于 Windows 的 zip 文件
3. 解压到目录（例如 `C:\terraform`）
4. 将该目录添加到系统 PATH 环境变量

或者使用 Chocolatey：
```powershell
choco install terraform
```

### macOS

使用 Homebrew：
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

### Linux (Ubuntu/Debian)

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

## 验证安装

打开终端或命令提示符，运行以下命令：

```bash
terraform version
```

您应该看到类似以下的输出：
```
Terraform v1.5.0
on windows_amd64
```

## 第一个 Terraform 配置

创建一个新的项目目录：
```bash
mkdir terraform-demo
cd terraform-demo
```

创建一个名为 `main.tf` 的文件，内容如下：

```hcl
terraform {
  required_providers {
    local = {
      source = "hashicorp/local"
      version = "2.4.0"
    }
  }
}

resource "local_file" "example" {
  content  = "Hello, Terraform!"
  filename = "${path.module}/hello.txt"
}
```

初始化 Terraform：
```bash
terraform init
```

查看执行计划：
```bash
terraform plan
```

应用配置：
```bash
terraform apply
```

当提示确认时，输入 `yes`。

完成后，您会在当前目录下看到一个 `hello.txt` 文件。

清理资源：
```bash
terraform destroy
```

## 总结

今天我们学习了：

1. Terraform 的基本概念和核心特性
2. 如何在不同操作系统上安装 Terraform
3. 创建第一个简单的 Terraform 配置
4. 使用 `init`、`plan`、`apply` 和 `destroy` 命令

明天我们将深入学习 Terraform 的基础概念和配置语法。