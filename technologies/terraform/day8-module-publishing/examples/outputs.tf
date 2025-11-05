# examples/outputs.tf
output "web_app_instance_id" {
  value = module.dev_web_app.instance_id
}

output "web_app_public_ip" {
  value = module.dev_web_app.public_ip
}