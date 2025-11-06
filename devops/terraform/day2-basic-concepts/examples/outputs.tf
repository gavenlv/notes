# 输出定义示例

# 输出 VPC 信息
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "创建的 VPC ID"
}

output "vpc_cidr" {
  value       = aws_vpc.main.cidr_block
  description = "VPC CIDR 块"
}

# 输出子网信息
output "subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "创建的子网 ID 列表"
}

output "subnet_cidrs" {
  value       = aws_subnet.public[*].cidr_block
  description = "子网 CIDR 块列表"
}

# 输出互联网网关信息
output "internet_gateway_id" {
  value       = aws_internet_gateway.main.id
  description = "互联网网关 ID"
}

# 输出本地文件路径
output "config_file_path" {
  value       = local_file.config.filename
  description = "生成的配置文件路径"
}