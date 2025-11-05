# VPC 模块

## 介绍

此模块创建一个基本的 VPC 配置，包括互联网网关和公共路由表。

## 使用示例

```hcl
module "vpc" {
  source = "./modules/vpc"
  
  name       = "production-vpc"
  cidr_block = "10.0.0.0/16"
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| name | VPC 名称 | string | - |
| cidr_block | VPC CIDR 块 | string | 10.0.0.0/16 |
| enable_dns_hostnames | 是否启用 DNS 主机名 | bool | true |

## 输出值

| 名称 | 描述 |
|------|------|
| vpc_id | VPC ID |
| internet_gateway_id | 互联网网关 ID |
| public_route_table_id | 公共路由表 ID |