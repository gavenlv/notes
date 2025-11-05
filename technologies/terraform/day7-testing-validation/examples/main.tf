# examples/main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = var.instance_type

  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Environment = var.environment
  }
}