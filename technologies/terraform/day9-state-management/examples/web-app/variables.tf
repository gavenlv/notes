# examples/web-app/variables.tf
variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "环境名称"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}

variable "backend_bucket" {
  description = "后端 S3 存储桶名称"
  type        = string
}

variable "dynamodb_table" {
  description = "DynamoDB 表名称"
  type        = string
}