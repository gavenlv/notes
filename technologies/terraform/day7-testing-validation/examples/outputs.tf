# examples/outputs.tf
output "instance_id" {
  value = aws_instance.web.id
}

output "instance_ip" {
  value = aws_instance.web.public_ip
  
  precondition {
    condition     = aws_instance.web.public_ip != null
    error_message = "实例必须具有公共 IP 地址。"
  }
}