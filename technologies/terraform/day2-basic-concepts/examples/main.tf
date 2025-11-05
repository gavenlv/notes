# 资源定义示例

# 创建一个 VPC
resource "aws_vpc" "main" {
  cidr_block = var.network_config.vpc_cidr

  tags = {
    Name = "MainVPC"
  }
}

# 创建子网
resource "aws_subnet" "public" {
  count = length(var.network_config.subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.network_config.subnet_cidrs[count.index]
  availability_zone = "${var.region}${count.index == 0 ? "a" : "b"}"

  tags = {
    Name = "PublicSubnet-${count.index + 1}"
  }
}

# 创建互联网网关
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "MainIGW"
  }
}

# 创建本地文件示例
resource "local_file" "config" {
  content  = <<-EOF
    VPC ID: ${aws_vpc.main.id}
    Region: ${var.region}
    Subnets: ${join(", ", aws_subnet.public[*].id)}
  EOF
  filename = "${path.module}/network-config.txt"
}