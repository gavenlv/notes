# 变量定义

variable "region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "VPC CIDR 块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "子网 CIDR 块"
  type        = string
  default     = "10.0.1.0/24"
}

variable "ami_id" {
  description = "AMI ID"
  type        = string
  default     = "ami-0c55b159cbfafe1d0"  # Amazon Linux 2
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
}