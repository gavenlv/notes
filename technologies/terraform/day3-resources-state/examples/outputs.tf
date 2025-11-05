# 输出定义

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "创建的 VPC ID"
}

output "vpc_cidr" {
  value       = aws_vpc.main.cidr_block
  description = "VPC CIDR 块"
}

output "internet_gateway_id" {
  value       = aws_internet_gateway.main.id
  description = "互联网网关 ID"
}

output "subnet_id" {
  value       = aws_subnet.public.id
  description = "公共子网 ID"
}

output "subnet_cidr" {
  value       = aws_subnet.public.cidr_block
  description = "子网 CIDR 块"
}

output "route_table_id" {
  value       = aws_route_table.public.id
  description = "路由表 ID"
}

output "security_group_id" {
  value       = aws_security_group.web.id
  description = "安全组 ID"
}

output "instance_id" {
  value       = aws_instance.web.id
  description = "EC2 实例 ID"
}

output "instance_public_ip" {
  value       = aws_instance.web.public_ip
  description = "EC2 实例公共 IP"
}

output "instance_private_ip" {
  value       = aws_instance.web.private_ip
  description = "EC2 实例私有 IP"
}