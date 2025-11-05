# Web 应用模块输出定义

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "subnet_id" {
  value       = aws_subnet.public.id
  description = "子网 ID"
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