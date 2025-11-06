# examples/modules/vpc/variables.tf
variable "name" {
  description = "VPC 名称"
  type        = string
}

variable "cidr_block" {
  description = "VPC CIDR 块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_dns_hostnames" {
  description = "是否启用 DNS 主机名"
  type        = bool
  default     = true
}