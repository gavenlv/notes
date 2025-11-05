# 使用 Web 应用模块的示例

module "dev_web_app" {
  source = "./modules/web-app"

  project_name  = "webapp"
  environment   = "dev"
  vpc_cidr      = "10.1.0.0/16"
  subnet_cidr   = "10.1.1.0/24"
  instance_type = "t2.micro"
}

output "dev_web_app_info" {
  value = {
    instance_ip = module.dev_web_app.instance_public_ip
    vpc_id      = module.dev_web_app.vpc_id
  }
}