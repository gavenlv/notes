# Terraform输出定义
# 阿里云ClickHouse集群输出信息

output "vpc_id" {
  description = "VPC ID"
  value       = alicloud_vpc.main.id
}

output "vswitch_id" {
  description = "交换机ID"
  value       = alicloud_vswitch.main.id
}

output "security_group_id" {
  description = "安全组ID"
  value       = alicloud_security_group.clickhouse.id
}

output "clickhouse_node1_public_ip" {
  description = "ClickHouse节点1公网IP"
  value       = alicloud_instance.clickhouse_node1.public_ip
}

output "clickhouse_node2_public_ip" {
  description = "ClickHouse节点2公网IP"
  value       = alicloud_instance.clickhouse_node2.public_ip
}

output "clickhouse_node3_public_ip" {
  description = "ClickHouse节点3公网IP"
  value       = alicloud_instance.clickhouse_node3.public_ip
}

output "clickhouse_node1_private_ip" {
  description = "ClickHouse节点1私网IP"
  value       = alicloud_instance.clickhouse_node1.private_ip
}

output "clickhouse_node2_private_ip" {
  description = "ClickHouse节点2私网IP"
  value       = alicloud_instance.clickhouse_node2.private_ip
}

output "clickhouse_node3_private_ip" {
  description = "ClickHouse节点3私网IP"
  value       = alicloud_instance.clickhouse_node3.private_ip
}

output "zookeeper_public_ip" {
  description = "ZooKeeper公网IP"
  value       = alicloud_instance.zookeeper.public_ip
}

output "zookeeper_private_ip" {
  description = "ZooKeeper私网IP"
  value       = alicloud_instance.zookeeper.private_ip
}

output "load_balancer_address" {
  description = "负载均衡器地址"
  value       = alicloud_slb_load_balancer.clickhouse.address
}

output "clickhouse_http_endpoint" {
  description = "ClickHouse HTTP端点"
  value       = "http://${alicloud_slb_load_balancer.clickhouse.address}:8123"
}

output "clickhouse_tcp_endpoint" {
  description = "ClickHouse TCP端点"
  value       = "${alicloud_slb_load_balancer.clickhouse.address}:9000"
}

output "ssh_commands" {
  description = "SSH连接命令"
  value = {
    node1     = "ssh -i clickhouse_key ubuntu@${alicloud_instance.clickhouse_node1.public_ip}"
    node2     = "ssh -i clickhouse_key ubuntu@${alicloud_instance.clickhouse_node2.public_ip}"
    node3     = "ssh -i clickhouse_key ubuntu@${alicloud_instance.clickhouse_node3.public_ip}"
    zookeeper = "ssh -i clickhouse_key ubuntu@${alicloud_instance.zookeeper.public_ip}"
  }
}

output "cluster_info" {
  description = "集群信息汇总"
  value = {
    cluster_name      = var.cluster_name
    environment       = var.environment
    region           = var.region
    nodes_count      = 3
    zookeeper_count  = 1
    load_balancer    = alicloud_slb_load_balancer.clickhouse.address
    http_port        = 8123
    tcp_port         = 9000
  }
}

output "connection_examples" {
  description = "连接示例"
  value = {
    curl_example = "curl '${alicloud_slb_load_balancer.clickhouse.address}:8123/?query=SELECT%20version()'"
    clickhouse_client = "clickhouse-client --host=${alicloud_slb_load_balancer.clickhouse.address} --port=9000"
    http_interface = "echo 'SELECT version()' | curl '${alicloud_slb_load_balancer.clickhouse.address}:8123/' --data-binary @-"
  }
}

output "monitoring_urls" {
  description = "监控URL"
  value = {
    system_metrics = "http://${alicloud_slb_load_balancer.clickhouse.address}:8123/play"
    cluster_status = "http://${alicloud_slb_load_balancer.clickhouse.address}:8123/?query=SELECT%20*%20FROM%20system.clusters"
  }
} 