# examples/environments/prod/variables.tf
variable "instance_type" {
  description = "实例类型"
  type        = string
}

variable "db_password" {
  description = "数据库密码"
  type        = string
  sensitive   = true
}