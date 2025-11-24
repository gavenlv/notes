# Terraform变量定义
# 阿里云ClickHouse集群配置

variable "region" {
  description = "阿里云地域"
  type        = string
  default     = "cn-beijing"
}

variable "environment" {
  description = "环境标识"
  type        = string
  default     = "learning"
}

variable "cluster_name" {
  description = "ClickHouse集群名称"
  type        = string
  default     = "clickhouse-cluster"
}

variable "instance_type" {
  description = "ECS实例规格"
  type        = string
  default     = "ecs.c6.large"
}

variable "system_disk_size" {
  description = "系统盘大小(GB)"
  type        = number
  default     = 40
}

variable "data_disk_size" {
  description = "数据盘大小(GB)"
  type        = number
  default     = 100
}

variable "clickhouse_version" {
  description = "ClickHouse版本"
  type        = string
  default     = "22.8.5.29"
}

variable "zookeeper_version" {
  description = "ZooKeeper版本"
  type        = string
  default     = "3.8.0"
}

variable "allowed_cidr_blocks" {
  description = "允许访问的CIDR块列表"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_monitoring" {
  description = "是否启用监控"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "备份保留天数"
  type        = number
  default     = 7
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default = {
    Project     = "ClickHouse Learning"
    Environment = "learning"
    Owner       = "student"
  }
} 