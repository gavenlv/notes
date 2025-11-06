# 输出定义文件

# 输出工作目录路径
output "working_directory" {
  value = path.module
  description = "当前工作目录路径"
}

# 输出 Terraform 版本
output "terraform_version" {
  value = terraform.version
  description = "Terraform 版本信息"
}