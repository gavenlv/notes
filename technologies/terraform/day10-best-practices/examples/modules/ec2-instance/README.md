# EC2 实例模块

## 介绍

此模块创建一个 EC2 实例。

## 使用示例

```hcl
module "web_server" {
  source = "./modules/ec2-instance"
  
  ami_id        = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
  subnet_id     = "subnet-12345678"
  
  tags = {
    Environment = "dev"
  }
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| ami_id | AMI ID | string | - |
| instance_type | 实例类型 | string | t2.micro |
| subnet_id | 子网 ID | string | - |
| tags | 资源标签 | map(string) | {} |

## 输出值

| 名称 | 描述 |
|------|------|
| instance_id | 实例 ID |
| public_ip | 公共 IP 地址 |