# examples/main.tf
module "dev_web_app" {
  source = "./modules/web-app"
  
  project_name  = "webapp"
  environment   = "dev"
  instance_type = "t2.micro"
  
  tags = {
    Owner = "dev-team"
  }
}

output "web_app_info" {
  value = {
    instance_id = module.dev_web_app.instance_id
    public_ip   = module.dev_web_app.public_ip
  }
}