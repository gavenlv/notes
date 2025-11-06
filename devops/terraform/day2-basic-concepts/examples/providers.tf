# 提供商配置示例

# 指定所需的提供商及其版本
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
  
  # 指定 Terraform 版本要求
  required_version = ">= 1.0"
}

# AWS 提供商配置
provider "aws" {
  region = var.region
  
  # 可以通过环境变量设置访问密钥
  # access_key = var.aws_access_key
  # secret_key = var.aws_secret_key
  
  # 或者使用共享凭证文件
  # shared_credentials_files = ["~/.aws/credentials"]
  # profile                  = "default"
}

# 本地提供商配置（用于本地文件操作）
provider "local" {
  # 本地提供商通常不需要特殊配置
}