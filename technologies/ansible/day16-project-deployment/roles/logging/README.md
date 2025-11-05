# Logging Role

此角色用于在Ansible Day16项目中配置集中式日志管理系统。

## 功能特性

- 部署Elasticsearch作为日志存储和搜索引擎
- 配置Logstash作为日志收集和处理管道
- 安装Kibana作为日志可视化界面
- 支持Filebeat作为轻量级日志 shipper
- 配置日志保留策略
- 设置安全认证和访问控制

## 支持的日志组件

- Elasticsearch
- Logstash
- Kibana
- Filebeat

## 默认变量

```yaml
# 日志组件配置
logging_components:
  - elasticsearch
  - logstash
  - kibana
  - filebeat

# Elasticsearch配置
elasticsearch_version: "7.17.0"
elasticsearch_port: 9200
elasticsearch_data_dir: "/var/lib/elasticsearch"
elasticsearch_config_dir: "/etc/elasticsearch"

# Logstash配置
logstash_version: "7.17.0"
logstash_port: 5044
logstash_config_dir: "/etc/logstash"

# Kibana配置
kibana_version: "7.17.0"
kibana_port: 5601
kibana_config_dir: "/etc/kibana"

# Filebeat配置
filebeat_version: "7.17.0"
filebeat_config_dir: "/etc/filebeat"
```

## 使用示例

```yaml
- hosts: logging_servers
  roles:
    - role: logging
```

## 许可证

MIT