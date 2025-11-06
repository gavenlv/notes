# Terraform 配置示例 - 创建本地文件

# 指定所需提供商及其版本
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "2.4.0"
    }
  }
}

# 定义一个本地文件资源
resource "local_file" "example" {
  content  = "Hello, Terraform!"
  filename = "${path.module}/hello.txt"
}

# 输出文件路径
output "file_path" {
  value = local_file.example.filename
}

# 输出文件内容
output "file_content" {
  value = local_file.example.content
}