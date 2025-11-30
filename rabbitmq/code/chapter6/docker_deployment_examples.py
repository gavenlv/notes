"""
第6章：RabbitMQ Docker化部署 - 代码示例
====================

本文件包含了RabbitMQ Docker化部署的各种示例代码，包括：
1. 单节点Docker部署和管理
2. Docker Compose集群部署
3. 配置文件生成和管理
4. 数据备份和恢复脚本
5. 监控和性能测试工具
"""

import os
import sys
import json
import time
import logging
import subprocess
import docker
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DockerConfig:
    """Docker配置类"""
    image: str = "rabbitmq:3.11-management"
    container_name: str = "rabbitmq-server"
    amqp_port: int = 5672
    management_port: int = 15672
    username: str = "admin"
    password: str = "admin123"
    vhost: str = "/"
    memory_limit: str = "1g"
    cpu_limit: str = "1.0"
    volume_name: str = "rabbitmq_data"
    network_name: str = "rabbitmq_network"


class DockerManager:
    """Docker管理器类"""
    
    def __init__(self, config: DockerConfig):
        self.config = config
        self.client = docker.from_env()
        self.volume = None
        self.container = None
        
    def create_volume(self) -> None:
        """创建数据卷"""
        try:
            self.volume = self.client.volumes.create(name=self.config.volume_name)
            logger.info(f"创建数据卷: {self.config.volume_name}")
        except Exception as e:
            logger.error(f"创建数据卷失败: {e}")
            
    def create_network(self) -> None:
        """创建Docker网络"""
        try:
            network = self.client.networks.create(
                self.config.network_name,
                driver="bridge",
                ipam=docker.types.IPAMConfig(
                    driver="default",
                    config=[docker.types.IPAMSubnet(subnet="172.20.0.0/16")]
                )
            )
            logger.info(f"创建网络: {self.config.network_name}")
            return network
        except Exception as e:
            logger.error(f"创建网络失败: {e}")
            return None
            
    def deploy_single_node(self, enable_monitoring: bool = True) -> None:
        """部署单节点RabbitMQ"""
        try:
            # 创建数据卷和网络
            self.create_volume()
            network = self.create_network()
            
            # 配置环境变量
            env_vars = {
                "RABBITMQ_DEFAULT_USER": self.config.username,
                "RABBITMQ_DEFAULT_PASS": self.config.password,
                "RABBITMQ_DEFAULT_VHOST": self.config.vhost,
                "RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS": "+MBas agecbf"
            }
            
            # 端口映射
            port_mapping = {
                self.config.amqp_port: 5672,
                self.config.management_port: 15672
            }
            
            # 挂载配置
            volumes = {
                f"{self.config.volume_name}": {"bind": "/var/lib/rabbitmq", "mode": "rw"}
            }
            
            # 资源限制
            mem_limit = self.config.memory_limit
            nano_cpus = int(float(self.config.cpu_limit) * 1e9)
            
            # 启动容器
            self.container = self.client.containers.run(
                image=self.config.image,
                name=self.config.container_name,
                environment=env_vars,
                ports=port_mapping,
                volumes=volumes,
                mem_limit=mem_limit,
                nano_cpus=nano_cpus,
                detach=True,
                restart_policy={"Name": "unless-stopped"},
                network=self.config.network_name if network else None,
                healthcheck={
                    "test": ["CMD", "rabbitmq-diagnostics", "ping"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "40s"
                }
            )
            
            logger.info(f"启动RabbitMQ容器: {self.config.container_name}")
            
            # 等待容器启动
            self.wait_for_ready()
            
            # 启用监控插件
            if enable_monitoring:
                self.enable_prometheus_plugin()
                
        except Exception as e:
            logger.error(f"部署单节点失败: {e}")
            raise
            
    def wait_for_ready(self, timeout: int = 300) -> None:
        """等待RabbitMQ服务就绪"""
        logger.info("等待RabbitMQ服务启动...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 检查容器状态
                container = self.client.containers.get(self.config.container_name)
                if container.status == "running":
                    # 检查健康状态
                    health_status = container.attrs.get("State", {}).get("Health", {})
                    if health_status.get("Status") == "healthy":
                        logger.info("RabbitMQ服务启动成功")
                        return
                    else:
                        logger.info("等待健康检查通过...")
                time.sleep(5)
            except Exception as e:
                logger.warning(f"检查服务状态失败: {e}")
                time.sleep(5)
                
        raise Exception("RabbitMQ服务启动超时")
        
    def enable_prometheus_plugin(self) -> None:
        """启用Prometheus监控插件"""
        try:
            result = self.container.exec_run("rabbitmq-plugins enable rabbitmq_prometheus")
            if result.exit_code == 0:
                logger.info("启用Prometheus监控插件成功")
            else:
                logger.error(f"启用插件失败: {result.output.decode()}")
        except Exception as e:
            logger.error(f"启用监控插件异常: {e}")
            
    def check_status(self) -> Dict[str, Any]:
        """检查RabbitMQ状态"""
        try:
            container = self.client.containers.get(self.config.container_name)
            
            status = {
                "container_status": container.status,
                "running": container.status == "running",
                "cpu_usage": self._get_container_stats(container, "cpu_percent"),
                "memory_usage": self._get_container_stats(container, "memory_usage"),
                "health_status": container.attrs.get("State", {}).get("Health", {}).get("Status"),
                "logs": self._get_recent_logs(container)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"检查状态失败: {e}")
            return {"error": str(e)}
            
    def _get_container_stats(self, container, metric: str) -> float:
        """获取容器统计信息"""
        try:
            stats = container.stats(stream=False)
            
            if metric == "cpu_percent":
                # 计算CPU使用率
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                           stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                              stats["precpu_stats"]["system_cpu_usage"]
                num_cpus = len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                
                if system_delta > 0:
                    return (cpu_delta / system_delta) * num_cpus * 100.0
                    
            elif metric == "memory_usage":
                # 内存使用量
                return stats["memory_stats"]["usage"] / 1024 / 1024  # MB
                
            return 0.0
        except:
            return 0.0
            
    def _get_recent_logs(self, container, tail: int = 50) -> str:
        """获取最近的日志"""
        try:
            return container.logs(tail=tail).decode()
        except:
            return ""
            
    def stop(self) -> None:
        """停止RabbitMQ容器"""
        try:
            if self.container:
                self.container.stop()
                logger.info("停止RabbitMQ容器成功")
        except Exception as e:
            logger.error(f"停止容器失败: {e}")
            
    def remove(self) -> None:
        """删除RabbitMQ容器"""
        try:
            if self.container:
                self.container.remove(force=True)
                logger.info("删除RabbitMQ容器成功")
        except Exception as e:
            logger.error(f"删除容器失败: {e}")
            
    def cleanup(self) -> None:
        """清理所有资源"""
        try:
            self.remove()
            
            # 删除网络
            try:
                network = self.client.networks.get(self.config.network_name)
                network.remove()
            except:
                pass
                
            # 删除数据卷
            try:
                volume = self.client.volumes.get(self.config.volume_name)
                volume.remove()
            except:
                pass
                
            logger.info("清理资源完成")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")


class ComposeManager:
    """Docker Compose管理器"""
    
    def __init__(self, project_name: str = "rabbitmq"):
        self.project_name = project_name
        self.compose_file = "docker-compose.yml"
        self.services = {}
        self.volumes = {}
        self.networks = {}
        
    def generate_basic_compose(self, config: DockerConfig) -> Dict[str, Any]:
        """生成基本的Compose配置"""
        self.services = {
            "rabbitmq": {
                "image": config.image,
                "container_name": config.container_name,
                "ports": [f"{config.amqp_port}:5672", f"{config.management_port}:15672"],
                "environment": {
                    "RABBITMQ_DEFAULT_USER": config.username,
                    "RABBITMQ_DEFAULT_PASS": config.password,
                    "RABBITMQ_DEFAULT_VHOST": config.vhost
                },
                "volumes": [
                    f"{config.volume_name}:/var/lib/rabbitmq",
                    "./config:/etc/rabbitmq/conf.d"
                ],
                "restart": "unless-stopped",
                "networks": ["rabbitmq_network"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "memory": config.memory_limit,
                            "cpus": config.cpu_limit
                        },
                        "reservations": {
                            "memory": "512M",
                            "cpus": "0.5"
                        }
                    }
                },
                "healthcheck": {
                    "test": ["CMD", "rabbitmq-diagnostics", "ping"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "40s"
                }
            }
        }
        
        self.volumes = {
            config.volume_name: {"driver": "local"}
        }
        
        self.networks = {
            "rabbitmq_network": {"driver": "bridge"}
        }
        
        return self._build_compose_config()
        
    def generate_cluster_compose(self, node_count: int = 3) -> Dict[str, Any]:
        """生成集群Compose配置"""
        # 重置配置
        self.services = {}
        self.volumes = {}
        self.networks = {
            "rabbitmq_cluster": {"driver": "bridge"}
        }
        
        # 创建镜像策略
        policy_name = "ha-all"
        policy_pattern = ".*"
        policy_definition = {
            "ha-mode": "all",
            "ha-sync-mode": "automatic"
        }
        
        # 添加监控服务
        self._add_monitoring_services()
        
        # 创建集群节点
        for i in range(node_count):
            node_name = f"rabbitmq-node{i+1}"
            node_port = 5672 + i
            mgmt_port = 15672 + i
            
            # 设置节点配置
            if i == 0:
                # 主节点 - 创建用户和策略
                environment = {
                    "RABBITMQ_ERLANG_COOKIE": "RABBITMQ_SECRET_COOKIE",
                    "RABBITMQ_DEFAULT_USER": "admin",
                    "RABBITMQ_DEFAULT_PASS": "admin123",
                    "RABBITMQ_DEFAULT_VHOST": "/"
                }
                
                # 健康检查前等待初始化
                healthcheck = {
                    "test": ["CMD-SHELL", "rabbitmq-diagnostics ping && rabbitmqctl node_health_check"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "120s"
                }
            else:
                # 从节点
                environment = {
                    "RABBITMQ_ERLANG_COOKIE": "RABBITMQ_SECRET_COOKIE"
                }
                
                healthcheck = {
                    "test": ["CMD", "rabbitmq-diagnostics", "ping"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "60s"
                }
            
            self.services[node_name] = {
                "image": "rabbitmq:3.11-management",
                "environment": environment,
                "volumes": [f"rabbitmq_data{i+1}:/var/lib/rabbitmq"],
                "networks": ["rabbitmq_cluster"],
                "healthcheck": healthcheck,
                "deploy": {
                    "placement": {
                        "constraints": [f"node.hostname == node{i+1}"]
                    },
                    "resources": {
                        "limits": {"memory": "1G", "cpus": "1.0"},
                        "reservations": {"memory": "512M", "cpus": "0.5"}
                    }
                },
                "depends_on": [f"rabbitmq-node{i}" if i > 0 else ""] if i > 0 else []
            }
            
            if i == 0:
                self.services[node_name]["ports"] = [f"{node_port}:5672", f"{mgmt_port}:15672"]
            
            # 添加数据卷
            self.volumes[f"rabbitmq_data{i+1}"] = {"driver": "local"}
            
        return self._build_compose_config()
        
    def _add_monitoring_services(self) -> None:
        """添加监控服务"""
        # Prometheus监控
        self.services["prometheus"] = {
            "image": "prom/prometheus:latest",
            "container_name": "rabbitmq-prometheus",
            "ports": ["9090:9090"],
            "volumes": [
                "./prometheus.yml:/etc/prometheus/prometheus.yml",
                "prometheus_data:/prometheus"
            ],
            "networks": ["rabbitmq_cluster"],
            "restart": "unless-stopped"
        }
        
        # Grafana可视化
        self.services["grafana"] = {
            "image": "grafana/grafana:latest",
            "container_name": "rabbitmq-grafana",
            "ports": ["3000:3000"],
            "environment": {
                "GF_SECURITY_ADMIN_PASSWORD": "admin123"
            },
            "volumes": ["grafana_data:/var/lib/grafana"],
            "networks": ["rabbitmq_cluster"],
            "restart": "unless-stopped"
        }
        
        # 添加监控相关卷
        self.volumes["prometheus_data"] = {"driver": "local"}
        self.volumes["grafana_data"] = {"driver": "local"}
        
    def _build_compose_config(self) -> Dict[str, Any]:
        """构建Compose配置"""
        config = {
            "version": "3.8",
            "services": self.services,
            "volumes": self.volumes,
            "networks": self.networks
        }
        return config
        
    def save_compose_file(self, config: Dict[str, Any], filename: str = None) -> None:
        """保存Compose文件"""
        if filename is None:
            filename = self.compose_file
            
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
        logger.info(f"保存Compose文件: {filename}")
        
    def up(self, detached: bool = True) -> None:
        """启动服务"""
        cmd = ["docker-compose", "-p", self.project_name]
        
        if detached:
            cmd.append("-d")
            
        cmd.extend(["up"])
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("服务启动成功")
        except subprocess.CalledProcessError as e:
            logger.error(f"服务启动失败: {e.stderr}")
            raise
            
    def down(self) -> None:
        """停止服务"""
        cmd = ["docker-compose", "-p", self.project_name, "down", "-v"]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("服务停止成功")
        except subprocess.CalledProcessError as e:
            logger.error(f"服务停止失败: {e.stderr}")
            raise
            
    def logs(self, service: str = None, tail: int = 100) -> str:
        """查看日志"""
        cmd = ["docker-compose", "-p", self.project_name, "logs"]
        
        if service:
            cmd.append(service)
            
        cmd.extend(["--tail", str(tail)])
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"获取日志失败: {e.stderr}")
            return ""
            
    def ps(self) -> str:
        """查看服务状态"""
        cmd = ["docker-compose", "-p", self.project_name, "ps"]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"获取服务状态失败: {e.stderr}")
            return ""


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
    def generate_rabbitmq_conf(self, config: DockerConfig) -> None:
        """生成RabbitMQ配置文件"""
        conf_content = f"""# RabbitMQ配置文件

# 默认用户和虚拟主机
default_user = {config.username}
default_pass = {config.password}
default_vhost = {config.vhost}

# 连接设置
default_connection_limit = 1000
heartbeat = 30

# 队列设置
default_queue_type = classic
default_queue_durable = true

# 内存设置
vm_memory_high_watermark = 0.6
vm_memory_high_watermark_paging_ratio = 0.5

# 磁盘设置
disk_free_limit = 1GB

# 网络设置
tcp_listen_options.backlog = 128
tcp_listen_options.nodelay = true
tcp_listen_options.exit_on_close = false

# 日志设置
log.file.level = info
log.console = true
log.console.level = info

# SSL设置
ssl_options.verify = verify_none
ssl_options.fail_if_no_peer_cert = false
"""
        
        conf_file = self.config_dir / "rabbitmq.conf"
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(conf_content)
            
        logger.info(f"生成配置文件: {conf_file}")
        
    def generate_advanced_conf(self) -> None:
        """生成高级配置文件"""
        advanced_content = """[
  {rabbit,
    [
      {log_levels,
        [
          {connection, debug},
          {mirroring, info},
          {authentication_failure_detailed, true},
          {default, info}
        ]
      },
      {reverse_dns_lookups, false},
      {backing_queue_module, rabbit_PRIORITIES_queue}
    ]
  }
].
"""
        
        advanced_file = self.config_dir / "advanced.config"
        with open(advanced_file, 'w', encoding='utf-8') as f:
            f.write(advanced_content)
            
        logger.info(f"生成高级配置文件: {advanced_file}")
        
    def generate_prometheus_config(self) -> None:
        """生成Prometheus配置"""
        prometheus_content = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq-node1:15692']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

rule_files:
  - "rabbitmq_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
"""
        
        prometheus_file = self.config_dir / "prometheus.yml"
        with open(prometheus_file, 'w', encoding='utf-8') as f:
            f.write(prometheus_content)
            
        logger.info(f"生成Prometheus配置: {prometheus_file}")
        
    def generate_grafana_dashboard(self) -> Dict[str, Any]:
        """生成Grafana仪表板配置"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "RabbitMQ Overview",
                "tags": ["rabbitmq", "messaging"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Connection Count",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rabbitmq_connections",
                                "legendFormat": "{{state}}"
                            }
                        ],
                        "yAxes": [{"label": "Connections"}]
                    },
                    {
                        "id": 2,
                        "title": "Queue Depth",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rabbitmq_queue_messages",
                                "legendFormat": "{{queue}}"
                            }
                        ],
                        "yAxes": [{"label": "Messages"}]
                    },
                    {
                        "id": 3,
                        "title": "Message Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rabbitmq_channel_messages",
                                "legendFormat": "{{direction}}"
                            }
                        ],
                        "yAxes": [{"label": "Messages/sec"}]
                    },
                    {
                        "id": 4,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rabbitmq_process_resident_memory_bytes",
                                "legendFormat": "Memory"
                            }
                        ],
                        "yAxes": [{"label": "Bytes"}]
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            }
        }
        
        dashboard_file = self.config_dir / "grafana_dashboard.json"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2)
            
        logger.info(f"生成Grafana仪表板: {dashboard_file}")
        return dashboard


class BackupManager:
    """备份管理器"""
    
    def __init__(self, container_name: str, backup_dir: str = "./backup"):
        self.container_name = container_name
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self) -> str:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"rabbitmq_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        # 创建临时工作目录
        temp_dir = Path(f"/tmp/rabbitmq_backup_{timestamp}")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 导出定义
            self._export_definitions(temp_dir)
            
            # 导出用户和权限
            self._export_users_and_permissions(temp_dir)
            
            # 导出策略
            self._export_policies(temp_dir)
            
            # 创建压缩包
            self._create_tar_archive(temp_dir, backup_path)
            
            logger.info(f"备份创建成功: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            raise
        finally:
            # 清理临时目录
            self._cleanup_temp_dir(temp_dir)
            
    def _export_definitions(self, temp_dir: Path) -> None:
        """导出定义"""
        cmd = ["docker", "exec", self.container_name, 
               "rabbitmqctl", "export_definitions", 
               f"/tmp/definitions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"导出定义失败: {result.stderr}")
            
        # 复制文件到临时目录
        copy_cmd = ["docker", "cp", 
                   f"{self.container_name}:/tmp/definitions_*.json", 
                   str(temp_dir)]
        subprocess.run(copy_cmd, check=True)
        
    def _export_users_and_permissions(self, temp_dir: Path) -> None:
        """导出用户和权限"""
        cmd = ["docker", "exec", self.container_name, "rabbitmqctl", "list_users"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        users_file = temp_dir / "users.txt"
        with open(users_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            
        cmd = ["docker", "exec", self.container_name, "rabbitmqctl", "list_permissions"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        permissions_file = temp_dir / "permissions.txt"
        with open(permissions_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            
    def _export_policies(self, temp_dir: Path) -> None:
        """导出策略"""
        cmd = ["docker", "exec", self.container_name, "rabbitmqctl", "list_policies"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        policies_file = temp_dir / "policies.txt"
        with open(policies_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            
    def _create_tar_archive(self, source_dir: Path, backup_path: Path) -> None:
        """创建tar压缩包"""
        cmd = ["tar", "-czf", str(backup_path), "-C", str(source_dir.parent), source_dir.name]
        subprocess.run(cmd, check=True)
        
    def _cleanup_temp_dir(self, temp_dir: Path) -> None:
        """清理临时目录"""
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            
    def restore_backup(self, backup_path: str) -> None:
        """恢复备份"""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
        # 解压备份文件
        temp_dir = Path(f"/tmp/rabbitmq_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 解压备份
            cmd = ["tar", "-xzf", str(backup_file), "-C", str(temp_dir)]
            subprocess.run(cmd, check=True)
            
            # 停止RabbitMQ
            self._stop_container()
            
            # 恢复配置（如果需要）
            self._restore_definitions(temp_dir)
            
            # 重启RabbitMQ
            self._start_container()
            
            # 导入定义
            self._import_definitions(temp_dir)
            
            logger.info("备份恢复成功")
            
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            raise
        finally:
            # 清理临时目录
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                
    def _stop_container(self) -> None:
        """停止容器"""
        cmd = ["docker", "stop", self.container_name]
        subprocess.run(cmd, check=True)
        
    def _start_container(self) -> None:
        """启动容器"""
        cmd = ["docker", "start", self.container_name]
        subprocess.run(cmd, check=True)
        
    def _restore_definitions(self, temp_dir: Path) -> None:
        """恢复定义文件"""
        # 这里可以添加自定义的恢复逻辑
        pass
        
    def _import_definitions(self, temp_dir: Path) -> None:
        """导入定义"""
        # 查找定义文件
        def_files = list(temp_dir.glob("definitions_*.json"))
        if def_files:
            def_file = def_files[0]
            # 复制文件到容器
            copy_cmd = ["docker", "cp", str(def_file), 
                       f"{self.container_name}:/tmp/definitions.json"]
            subprocess.run(copy_cmd, check=True)
            
            # 导入定义
            cmd = ["docker", "exec", self.container_name,
                   "rabbitmqctl", "import_definitions", "/tmp/definitions.json"]
            subprocess.run(cmd, check=True)
            
    def cleanup_old_backups(self, days: int = 30) -> None:
        """清理旧备份"""
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob("rabbitmq_backup_*.tar.gz"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                logger.info(f"删除旧备份: {backup_file}")


class PerformanceTester:
    """性能测试工具"""
    
    def __init__(self, container_name: str = "rabbitmq-server"):
        self.container_name = container_name
        
    def run_perf_test(self, producers: int = 10, consumers: int = 10, 
                     rate: int = 1000, duration: int = 300) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info(f"开始性能测试: 生产者={producers}, 消费者={consumers}, 速率={rate}/s, 持续时间={duration}s")
        
        # 构建测试命令
        test_cmd = [
            "docker", "run", "--rm", "--network", "host",
            "pivotalrabbit/perf-test",
            "--uri", f"amqp://admin:admin123@localhost:5672",
            "--producers", str(producers),
            "--consumers", str(consumers),
            "--rate", str(rate),
            "--time-limit", str(duration),
            "--publishing-interval", "10",
            "--confirm-rate", str(rate)
        ]
        
        # 执行测试
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, 
                                  timeout=duration + 60)
            
            if result.returncode == 0:
                # 解析测试结果
                output = result.stdout
                metrics = self._parse_perf_output(output)
                
                logger.info("性能测试完成")
                return {
                    "success": True,
                    "metrics": metrics,
                    "output": output
                }
            else:
                logger.error(f"性能测试失败: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("性能测试超时")
            return {"success": False, "error": "测试超时"}
        except Exception as e:
            logger.error(f"性能测试异常: {e}")
            return {"success": False, "error": str(e)}
            
    def _parse_perf_output(self, output: str) -> Dict[str, float]:
        """解析性能测试输出"""
        metrics = {}
        
        # 解析各种指标
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 提取速率信息
            if "confirmed" in line.lower() and "rate" in line.lower():
                if "publishing" in line.lower():
                    try:
                        # 提取发布速率
                        rate = float(line.split()[-2])  # 假设格式为 "XXX msgs/sec"
                        metrics["publish_rate"] = rate
                    except:
                        pass
                elif "consuming" in line.lower():
                    try:
                        # 提取消费速率
                        rate = float(line.split()[-2])
                        metrics["consume_rate"] = rate
                    except:
                        pass
                        
            # 提取消息数量
            if "total" in line.lower() and ("msgs" in line.lower() or "messages" in line.lower()):
                try:
                    # 提取总消息数
                    total = int(line.split()[-2])
                    metrics["total_messages"] = total
                except:
                    pass
                    
            # 提取延迟信息
            if "latency" in line.lower():
                try:
                    # 提取平均延迟
                    parts = line.split()
                    latency = float(parts[-2])  # 假设格式为 "XXX ms"
                    metrics["avg_latency_ms"] = latency
                except:
                    pass
                    
        return metrics
        
    def test_resource_usage(self, duration: int = 60) -> Dict[str, Any]:
        """测试资源使用情况"""
        logger.info(f"测试资源使用情况，持续时间: {duration}秒")
        
        # 运行docker stats命令
        cmd = ["docker", "stats", "--no-stream", self.container_name]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # 解析stats输出
                return self._parse_docker_stats(result.stdout)
            else:
                logger.error(f"获取资源使用情况失败: {result.stderr}")
                return {}
        except Exception as e:
            logger.error(f"测试资源使用失败: {e}")
            return {}
            
    def _parse_docker_stats(self, stats_output: str) -> Dict[str, float]:
        """解析docker stats输出"""
        # 简单的解析实现
        lines = stats_output.strip().split('\n')
        
        if len(lines) < 2:
            return {}
            
        # 解析表头和数值
        headers = lines[0].split()
        values = lines[1].split()
        
        metrics = {}
        for i, header in enumerate(headers):
            if i < len(values):
                if header.lower() in ['cpu', '%']:
                    try:
                        metrics['cpu_percent'] = float(values[i].rstrip('%'))
                    except:
                        pass
                elif header.lower() in ['mem', 'mem_perc']:
                    try:
                        metrics['memory_percent'] = float(values[i].rstrip('%'))
                    except:
                        pass
                elif header.lower() == 'mem_usage':
                    metrics['memory_usage'] = values[i]
                    
        return metrics


def main():
    """主函数 - 演示各种Docker部署功能"""
    print("=== RabbitMQ Docker化部署演示 ===")
    
    # 配置Docker管理器
    config = DockerConfig(
        image="rabbitmq:3.11-management",
        container_name="rabbitmq-docker-demo",
        memory_limit="1g",
        cpu_limit="1.0"
    )
    
    while True:
        print("\n请选择要演示的功能:")
        print("1. 单节点Docker部署")
        print("2. Docker Compose集群部署")
        print("3. 生成配置文件")
        print("4. 性能测试")
        print("5. 备份和恢复")
        print("6. 监控和状态检查")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-6): ").strip()
        
        if choice == "1":
            demo_single_node_deployment(config)
        elif choice == "2":
            demo_cluster_deployment()
        elif choice == "3":
            demo_config_generation()
        elif choice == "4":
            demo_performance_testing()
        elif choice == "5":
            demo_backup_restore()
        elif choice == "6":
            demo_monitoring()
        elif choice == "0":
            print("演示结束")
            break
        else:
            print("无效选择，请重试")


def demo_single_node_deployment(config: DockerConfig):
    """演示单节点部署"""
    print("\n=== 单节点Docker部署演示 ===")
    
    manager = DockerManager(config)
    
    try:
        # 部署单节点
        print("1. 启动单节点RabbitMQ...")
        manager.deploy_single_node()
        
        # 检查状态
        print("2. 检查服务状态...")
        status = manager.check_status()
        print(f"服务状态: {status}")
        
        # 等待用户确认
        input("\n按Enter键继续...")
        
    except Exception as e:
        print(f"部署失败: {e}")
    finally:
        # 清理资源
        print("3. 清理资源...")
        manager.cleanup()


def demo_cluster_deployment():
    """演示集群部署"""
    print("\n=== Docker Compose集群部署演示 ===")
    
    compose_manager = ComposeManager("rabbitmq-cluster")
    
    try:
        # 生成集群配置
        print("1. 生成集群配置...")
        cluster_config = compose_manager.generate_cluster_compose(3)
        
        # 保存配置文件
        compose_file = "docker-compose-cluster.yml"
        compose_manager.save_compose_file(cluster_config, compose_file)
        
        print(f"2. 集群配置文件已生成: {compose_file}")
        print("3. 部署命令:")
        print(f"   docker-compose -p rabbitmq-cluster -f {compose_file} up -d")
        print("4. 查看状态命令:")
        print(f"   docker-compose -p rabbitmq-cluster ps")
        print("5. 查看日志命令:")
        print(f"   docker-compose -p rabbitmq-cluster logs -f rabbitmq-node1")
        
    except Exception as e:
        print(f"集群配置生成失败: {e}")


def demo_config_generation():
    """演示配置生成"""
    print("\n=== 配置文件生成演示 ===")
    
    config = DockerConfig()
    config_manager = ConfigManager("./docker_config")
    
    try:
        # 生成各种配置文件
        print("1. 生成RabbitMQ配置文件...")
        config_manager.generate_rabbitmq_conf(config)
        
        print("2. 生成高级配置...")
        config_manager.generate_advanced_conf()
        
        print("3. 生成Prometheus配置...")
        config_manager.generate_prometheus_config()
        
        print("4. 生成Grafana仪表板...")
        config_manager.generate_grafana_dashboard()
        
        print("5. 配置文件已生成在 ./docker_config/ 目录下")
        
    except Exception as e:
        print(f"配置文件生成失败: {e}")


def demo_performance_testing():
    """演示性能测试"""
    print("\n=== 性能测试演示 ===")
    
    tester = PerformanceTester("rabbitmq-server")
    
    try:
        # 运行基本性能测试
        print("1. 运行基本性能测试...")
        result = tester.run_perf_test(
            producers=5,
            consumers=5,
            rate=500,
            duration=60
        )
        
        if result["success"]:
            print("性能测试结果:")
            for key, value in result["metrics"].items():
                print(f"  {key}: {value}")
        else:
            print(f"性能测试失败: {result['error']}")
            
        # 测试资源使用
        print("\n2. 测试资源使用情况...")
        resource_usage = tester.test_resource_usage()
        if resource_usage:
            print("资源使用情况:")
            for key, value in resource_usage.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"性能测试失败: {e}")


def demo_backup_restore():
    """演示备份和恢复"""
    print("\n=== 备份和恢复演示 ===")
    
    backup_manager = BackupManager("rabbitmq-server", "./docker_backup")
    
    try:
        # 创建备份
        print("1. 创建备份...")
        backup_path = backup_manager.create_backup()
        print(f"备份已创建: {backup_path}")
        
        # 清理旧备份
        print("2. 清理30天前的旧备份...")
        backup_manager.cleanup_old_backups(30)
        
        print("3. 恢复备份命令:")
        print(f"   backup_manager.restore_backup('{backup_path}')")
        
    except Exception as e:
        print(f"备份操作失败: {e}")


def demo_monitoring():
    """演示监控功能"""
    print("\n=== 监控功能演示 ===")
    
    config = DockerConfig()
    manager = DockerManager(config)
    
    try:
        print("1. 部署带监控的RabbitMQ...")
        manager.deploy_single_node(enable_monitoring=True)
        
        print("2. 检查服务状态...")
        status = manager.check_status()
        print(f"服务状态: {status}")
        
        # 显示访问信息
        print("3. 访问信息:")
        print(f"   RabbitMQ管理界面: http://localhost:{config.management_port}")
        print(f"   用户名: {config.username}")
        print(f"   密码: {config.password}")
        print(f"   AMQP端口: {config.amqp_port}")
        print(f"   Prometheus指标: http://localhost:{config.management_port}/metrics")
        
        input("\n按Enter键继续...")
        
    except Exception as e:
        print(f"监控演示失败: {e}")
    finally:
        manager.cleanup()


if __name__ == "__main__":
    main()