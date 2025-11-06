# examples/modules/ec2-instance/variables.tf
variable "ami_id" {
  description = "AMI ID"
  type        = string
}

variable "instance_type" {
  description = "实例类型"
  type        = string
  default     = "t2.micro"
  
  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro, t2.small, 或 t2.medium 之一。"
  }
}

variable "subnet_id" {
  description = "子网 ID"
  type        = string
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default     = {}
}