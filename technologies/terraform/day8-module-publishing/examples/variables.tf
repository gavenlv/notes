# examples/variables.tf
variable "project_name" {
  description = "项目名称"
  type        = string
  default     = "webapp"
}

variable "environment" {
  description = "环境名称"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "环境必须是 dev, test, 或 prod 之一。"
  }
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro"
  
  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro, t2.small, 或 t2.medium 之一。"
  }
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default     = {}
}