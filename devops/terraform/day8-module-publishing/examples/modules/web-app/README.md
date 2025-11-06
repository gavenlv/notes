# Web 应用模块

## 介绍

这个模块用于创建简单的 Web 应用程序 EC2 实例。

## 使用示例

```hcl
module "web_app" {
  source = "./modules/web-app"
  
  project_name  = "myapp"
  environment   = "dev"
  instance_type = "t2.micro"
  
  tags = {
    Owner = "team-a"
  }
}
```

## 输入变量

| 名称 | 描述 | 类型 | 默认值 |
|------|------|------|--------|
| project_name | 项目名称 | string | - |
| environment | 环境名称 | string | - |
| instance_type | EC2 实例类型 | string | t2.micro |
| tags | 资源标签 | map(string) | {} |

## 输出值

| 名称 | 描述 |
|------|------|
| instance_id | EC2 实例 ID |
| public_ip | EC2 实例公共 IP |

## 许可证

MIT License