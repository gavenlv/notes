# Web 应用模块 EC2 实例配置

resource "aws_instance" "web" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Hello from ${var.project_name} ${var.environment}</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "${var.project_name}-${var.environment}-web"
  }
}