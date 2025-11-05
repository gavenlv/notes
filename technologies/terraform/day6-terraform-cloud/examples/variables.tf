# examples/variables.tf
# Terraform Cloud 变量定义示例

variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
}

variable "region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}