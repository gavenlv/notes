# examples/environments/prod/main.tf
provider "aws" {
  region = "us-west-2"
}

module "vpc" {
  source = "../../modules/vpc"
  
  name       = "prod-vpc"
  cidr_block = "10.2.0.0/16"
}

module "web_server" {
  source = "../../modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  subnet_id     = module.vpc.public_subnets[0]
  
  tags = {
    Environment = "prod"
  }
}

output "web_server_ip" {
  value = module.web_server.public_ip
}