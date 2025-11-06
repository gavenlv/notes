# examples/modules/ec2-instance/main.tf
resource "aws_instance" "main" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id
  
  tags = merge(
    var.tags,
    {
      Name = "ec2-instance"
    }
  )
}