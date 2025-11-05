# 变量定义示例

# 字符串变量
variable "region" {
  description = "AWS 区域"
  type        = string
  default     = "us-west-2"
}

# 数字变量
variable "instance_count" {
  description = "实例数量"
  type        = number
  default     = 1
}

# 布尔变量
variable "enable_monitoring" {
  description = "是否启用监控"
  type        = bool
  default     = true
}

# 列表变量
variable "instance_types" {
  description = "实例类型列表"
  type        = list(string)
  default     = ["t2.micro", "t2.small", "t2.medium"]
}

# 映射变量
variable "ami_ids" {
  description = "不同区域的 AMI ID 映射"
  type        = map(string)
  default = {
    us-west-1 = "ami-0b000c9e6a0a0d0e0"
    us-west-2 = "ami-0c55b159cbfafe1d0"
    us-east-1 = "ami-0947d2ba4a522fdee"
  }
}

# 对象变量
variable "network_config" {
  description = "网络配置"
  type = object({
    vpc_cidr     = string
    subnet_cidrs = list(string)
  })
  default = {
    vpc_cidr     = "10.0.0.0/16"
    subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  }
}