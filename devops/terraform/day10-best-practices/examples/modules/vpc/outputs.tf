# examples/modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "internet_gateway_id" {
  description = "互联网网关 ID"
  value       = aws_internet_gateway.main.id
}

output "public_route_table_id" {
  description = "公共路由表 ID"
  value       = aws_route_table.public.id
}