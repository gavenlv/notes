# examples/s3-backend-setup/variables.tf
variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "bucket_name" {
  description = "S3 存储桶名称"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB 表名称"
  type        = string
  default     = "terraform-state-locks"
}