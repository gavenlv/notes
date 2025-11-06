# 后端配置示例

terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "multi-env/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}