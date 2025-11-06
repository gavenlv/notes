# 阿里云ClickHouse集群Terraform配置
# 作者: ClickHouse学习教程
# 版本: 1.0

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.210"
    }
  }
}

# 配置阿里云Provider
provider "alicloud" {
  region = var.region
}

# 数据源：获取可用区
data "alicloud_zones" "default" {
  available_disk_category     = "cloud_efficiency"
  available_resource_creation = "VSwitch"
}

# 数据源：获取实例规格
data "alicloud_instance_types" "default" {
  availability_zone = data.alicloud_zones.default.zones.0.id
  cpu_core_count    = 4
  memory_size       = 8
}

# 数据源：获取镜像
data "alicloud_images" "default" {
  most_recent = true
  owners      = "system"
  name_regex  = "^ubuntu_20_04_x64*"
}

# VPC
resource "alicloud_vpc" "main" {
  vpc_name   = "clickhouse-vpc"
  cidr_block = "10.0.0.0/8"
  
  tags = {
    Name        = "ClickHouse Cluster VPC"
    Environment = var.environment
    Project     = "ClickHouse Learning"
  }
}

# 交换机
resource "alicloud_vswitch" "main" {
  vswitch_name = "clickhouse-vswitch"
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.1.0/24"
  zone_id      = data.alicloud_zones.default.zones.0.id
  
  tags = {
    Name        = "ClickHouse Cluster VSwitch"
    Environment = var.environment
  }
}

# 安全组
resource "alicloud_security_group" "clickhouse" {
  name   = "clickhouse-sg"
  vpc_id = alicloud_vpc.main.id
  
  tags = {
    Name        = "ClickHouse Security Group"
    Environment = var.environment
  }
}

# 安全组规则 - SSH
resource "alicloud_security_group_rule" "ssh" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "22/22"
  priority          = 1
  security_group_id = alicloud_security_group.clickhouse.id
  cidr_ip           = "0.0.0.0/0"
}

# 安全组规则 - ClickHouse HTTP
resource "alicloud_security_group_rule" "clickhouse_http" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "8123/8123"
  priority          = 1
  security_group_id = alicloud_security_group.clickhouse.id
  cidr_ip           = "0.0.0.0/0"
}

# 安全组规则 - ClickHouse TCP
resource "alicloud_security_group_rule" "clickhouse_tcp" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "9000/9000"
  priority          = 1
  security_group_id = alicloud_security_group.clickhouse.id
  cidr_ip           = "0.0.0.0/0"
}

# 安全组规则 - ClickHouse 集群通信
resource "alicloud_security_group_rule" "clickhouse_cluster" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "9009/9009"
  priority          = 1
  security_group_id = alicloud_security_group.clickhouse.id
  cidr_ip           = "10.0.0.0/8"
}

# Key Pair
resource "alicloud_key_pair" "default" {
  key_pair_name = "clickhouse-keypair"
  public_key    = file("${path.module}/clickhouse_key.pub")
}

# ClickHouse节点1
resource "alicloud_instance" "clickhouse_node1" {
  instance_name        = "clickhouse-node1"
  image_id             = data.alicloud_images.default.images.0.id
  instance_type        = data.alicloud_instance_types.default.instance_types.0.id
  security_groups      = [alicloud_security_group.clickhouse.id]
  vswitch_id           = alicloud_vswitch.main.id
  key_name             = alicloud_key_pair.default.key_pair_name
  
  system_disk_category = "cloud_efficiency"
  system_disk_size     = 40
  
  # 数据盘
  data_disks {
    name     = "clickhouse-data"
    size     = 100
    category = "cloud_efficiency"
  }
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    node_id = "1"
    cluster_name = var.cluster_name
    shard_num = "1"
    replica_num = "1"
  }))
  
  tags = {
    Name        = "ClickHouse Node 1"
    Environment = var.environment
    Role        = "clickhouse-server"
  }
}

# ClickHouse节点2
resource "alicloud_instance" "clickhouse_node2" {
  instance_name        = "clickhouse-node2"
  image_id             = data.alicloud_images.default.images.0.id
  instance_type        = data.alicloud_instance_types.default.instance_types.0.id
  security_groups      = [alicloud_security_group.clickhouse.id]
  vswitch_id           = alicloud_vswitch.main.id
  key_name             = alicloud_key_pair.default.key_pair_name
  
  system_disk_category = "cloud_efficiency"
  system_disk_size     = 40
  
  # 数据盘
  data_disks {
    name     = "clickhouse-data"
    size     = 100
    category = "cloud_efficiency"
  }
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    node_id = "2"
    cluster_name = var.cluster_name
    shard_num = "2"
    replica_num = "1"
  }))
  
  tags = {
    Name        = "ClickHouse Node 2"
    Environment = var.environment
    Role        = "clickhouse-server"
  }
}

# ClickHouse节点3（副本）
resource "alicloud_instance" "clickhouse_node3" {
  instance_name        = "clickhouse-node3"
  image_id             = data.alicloud_images.default.images.0.id
  instance_type        = data.alicloud_instance_types.default.instance_types.0.id
  security_groups      = [alicloud_security_group.clickhouse.id]
  vswitch_id           = alicloud_vswitch.main.id
  key_name             = alicloud_key_pair.default.key_pair_name
  
  system_disk_category = "cloud_efficiency"
  system_disk_size     = 40
  
  # 数据盘
  data_disks {
    name     = "clickhouse-data"
    size     = 100
    category = "cloud_efficiency"
  }
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    node_id = "3"
    cluster_name = var.cluster_name
    shard_num = "1"
    replica_num = "2"
  }))
  
  tags = {
    Name        = "ClickHouse Node 3"
    Environment = var.environment
    Role        = "clickhouse-server"
  }
}

# ZooKeeper节点（用于ClickHouse副本协调）
resource "alicloud_instance" "zookeeper" {
  instance_name        = "clickhouse-zookeeper"
  image_id             = data.alicloud_images.default.images.0.id
  instance_type        = data.alicloud_instance_types.default.instance_types.0.id
  security_groups      = [alicloud_security_group.clickhouse.id]
  vswitch_id           = alicloud_vswitch.main.id
  key_name             = alicloud_key_pair.default.key_pair_name
  
  system_disk_category = "cloud_efficiency"
  system_disk_size     = 20
  
  user_data = base64encode(file("${path.module}/zookeeper_user_data.sh"))
  
  tags = {
    Name        = "ZooKeeper for ClickHouse"
    Environment = var.environment
    Role        = "zookeeper"
  }
}

# 负载均衡器
resource "alicloud_slb_load_balancer" "clickhouse" {
  load_balancer_name = "clickhouse-lb"
  vswitch_id         = alicloud_vswitch.main.id
  load_balancer_spec = "slb.s2.small"
  
  tags = {
    Name        = "ClickHouse Load Balancer"
    Environment = var.environment
  }
}

# 负载均衡监听器 - HTTP
resource "alicloud_slb_listener" "clickhouse_http" {
  load_balancer_id = alicloud_slb_load_balancer.clickhouse.id
  backend_port     = 8123
  frontend_port    = 8123
  protocol         = "tcp"
  bandwidth        = -1
  
  health_check_type     = "tcp"
  health_check_timeout  = 10
  healthy_threshold     = 2
  unhealthy_threshold   = 2
}

# 负载均衡监听器 - TCP
resource "alicloud_slb_listener" "clickhouse_tcp" {
  load_balancer_id = alicloud_slb_load_balancer.clickhouse.id
  backend_port     = 9000
  frontend_port    = 9000
  protocol         = "tcp"
  bandwidth        = -1
  
  health_check_type     = "tcp"
  health_check_timeout  = 10
  healthy_threshold     = 2
  unhealthy_threshold   = 2
}

# 添加后端服务器到负载均衡器
resource "alicloud_slb_backend_server" "clickhouse_nodes" {
  load_balancer_id = alicloud_slb_load_balancer.clickhouse.id
  
  backend_servers {
    server_id = alicloud_instance.clickhouse_node1.id
    weight    = 100
  }
  
  backend_servers {
    server_id = alicloud_instance.clickhouse_node2.id
    weight    = 100
  }
  
  backend_servers {
    server_id = alicloud_instance.clickhouse_node3.id
    weight    = 100
  }
} 