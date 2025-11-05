# 后端配置示例

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