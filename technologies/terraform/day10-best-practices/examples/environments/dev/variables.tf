# examples/environments/dev/variables.tf
variable "instance_type" {
  description = "实例类型"
  type        = string
  default     = "t2.micro"
}