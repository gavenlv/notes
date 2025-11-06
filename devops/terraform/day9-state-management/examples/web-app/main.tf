# examples/web-app/main.tf
terraform {
  backend "s3" {
    bucket         = var.backend_bucket
    key            = "web-app/terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = var.dynamodb_table
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type
  
  tags = {
    Name        = "web-app-instance"
    Environment = var.environment
  }
}