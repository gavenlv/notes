# examples/modules/ec2-instance/outputs.tf
output "instance_id" {
  description = "实例 ID"
  value       = aws_instance.main.id
}

output "public_ip" {
  description = "公共 IP 地址"
  value       = aws_instance.main.public_ip
}