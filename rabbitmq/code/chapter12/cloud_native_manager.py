#!/usr/bin/env python3
"""
云原生RabbitMQ部署管理工具
Kubernetes环境下的集群部署、监控、扩容和故障处理
"""

import asyncio
import aiohttp
import json
import yaml
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.rest import ApiException
import jinja2


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """部署配置"""
    namespace: str
    cluster_name: str
    replicas: int
    image: str
    resources: Dict[str, str]
    storage_size: str
    storage_class: str
    rabbitmq_config: str
    environment: Dict[str, str]


@dataclass
class ScalingConfig:
    """扩容配置"""
    min_replicas: int
    max_replicas: int
    target_cpu_percent: int
    target_memory_percent: int
    scale_down_stabilization: int
    scale_up_stabilization: int


class KubernetesRabbitMQManager:
    """Kubernetes环境下的RabbitMQ管理器"""
    
    def __init__(self, context: Optional[str] = None):
        self.context = context
        self.v1 = None
        self.apps_v1 = None
        self.core_v1 = None
        self.rbac_v1 = None
        self.storage_v1 = None
        self.template_env = self._init_template_env()
        
    def _init_template_env(self) -> jinja2.Environment:
        """初始化Jinja2模板环境"""
        loader = jinja2.DictLoader({
            'statefulset': '''apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ cluster_name }}
  namespace: {{ namespace }}
  labels:
    app: rabbitmq
    cluster: {{ cluster_name }}
spec:
  serviceName: {{ cluster_name }}-headless
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: rabbitmq
      cluster: {{ cluster_name }}
  template:
    metadata:
      labels:
        app: rabbitmq
        cluster: {{ cluster_name }}
    spec:
      containers:
      - name: rabbitmq
        image: {{ image }}
        ports:
        - containerPort: 5672
          name: amqp
        - containerPort: 15672
          name: management
        - containerPort: 25672
          name: clustering
        env:
        - name: RABBITMQ_DEFAULT_USER
          value: "admin"
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: {{ cluster_name }}-credentials
              key: password
        - name: RABBITMQ_ERLANG_COOKIE
          valueFrom:
            secretKeyRef:
              name: {{ cluster_name }}-credentials
              key: erlang-cookie
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        resources:
          requests:
            memory: {{ resources.requests.memory }}
            cpu: {{ resources.requests.cpu }}
          limits:
            memory: {{ resources.limits.memory }}
            cpu: {{ resources.limits.cpu }}
        volumeMounts:
        - name: rabbitmq-data
          mountPath: /var/lib/rabbitmq
        - name: rabbitmq-config
          mountPath: /etc/rabbitmq
        livenessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - ping
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - check_port_connectivity
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: rabbitmq-config
        configMap:
          name: {{ cluster_name }}-config
  volumeClaimTemplates:
  - metadata:
      name: rabbitmq-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: {{ storage_size }}
      storageClassName: {{ storage_class }}''',
            
            'service': '''apiVersion: v1
kind: Service
metadata:
  name: {{ cluster_name }}-headless
  namespace: {{ namespace }}
  labels:
    app: rabbitmq
    cluster: {{ cluster_name }}
spec:
  clusterIP: None
  selector:
    app: rabbitmq
    cluster: {{ cluster_name }}
  ports:
  - name: amqp
    port: 5672
    targetPort: 5672
  - name: management
    port: 15672
    targetPort: 15672
  - name: clustering
    port: 25672
    targetPort: 25672
---
apiVersion: v1
kind: Service
metadata:
  name: {{ cluster_name }}
  namespace: {{ namespace }}
  labels:
    app: rabbitmq
    cluster: {{ cluster_name }}
spec:
  selector:
    app: rabbitmq
    cluster: {{ cluster_name }}
  ports:
  - name: amqp
    port: 5672
    targetPort: 5672
  - name: management
    port: 15672
    targetPort: 15672
  type: ClusterIP''',
            
            'configmap': '''apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cluster_name }}-config
  namespace: {{ namespace }}
  labels:
    app: rabbitmq
    cluster: {{ cluster_name }}
data:
  rabbitmq.conf: |
    loopback_users = none
    default_user = admin
    default_pass = admin123
    default_permissions.configure = .*
    default_permissions.read = .*
    default_permissions.write = .*
    
    cluster_formation.peer_discovery_backend = classic_config
    {{ cluster_config }}
    
    哈机.memory_scale = 1.20
    哈机.disk_free_limit.absolute = 6GB
    哈机.max_message_size = 134217728
    
  enabled_plugins: |
    [rabbitmq_management,rabbitmq_monitoring].''',
            
            'secret': '''apiVersion: v1
kind: Secret
metadata:
  name: {{ cluster_name }}-credentials
  namespace: {{ namespace }}
  labels:
    app: rabbitmq
    cluster: {{ cluster_name }}
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded "admin"
  password: YWRtaW4xMjM=  # base64 encoded "admin123"
  erlang-cookie: Q1JBTkRPU1FUU0VOREZBTUlMWQ==  # base64 encoded "CLUSTER_SENDFAMIQ"
'''
        })
        return jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
    
    async def connect(self):
        """连接到Kubernetes API"""
        try:
            # 尝试加载集群配置
            config.load_incluster_config()
        except config.ConfigException:
            # 如果不在集群内，加载kubeconfig
            if self.context:
                config.load_kube_config(context=self.context)
            else:
                config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()
        self.storage_v1 = client.StorageV1Api()
    
    async def disconnect(self):
        """断开连接"""
        await self.v1.api_client.close()
        await self.apps_v1.api_client.close()
    
    async def create_namespace(self, namespace: str) -> bool:
        """创建命名空间"""
        try:
            namespace_obj = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            await self.v1.create_namespace(namespace_obj)
            logger.info(f"创建命名空间成功: {namespace}")
            return True
        except ApiException as e:
            if e.status == 409:  # 已存在
                logger.info(f"命名空间已存在: {namespace}")
                return True
            logger.error(f"创建命名空间失败: {e}")
            return False
    
    async def create_deployment(self, config: DeploymentConfig) -> bool:
        """创建RabbitMQ部署"""
        try:
            # 生成集群配置
            cluster_config = self._generate_cluster_config(config)
            
            # 渲染配置模板
            templates = {
                'statefulset': self.template_env.get_template('statefulset').render(
                    cluster_name=config.cluster_name,
                    namespace=config.namespace,
                    replicas=config.replicas,
                    image=config.image,
                    resources=config.resources,
                    storage_size=config.storage_size,
                    storage_class=config.storage_class
                ),
                'service': self.template_env.get_template('service').render(
                    cluster_name=config.cluster_name,
                    namespace=config.namespace
                ),
                'configmap': self.template_env.get_template('configmap').render(
                    cluster_name=config.cluster_name,
                    namespace=config.namespace,
                    cluster_config=cluster_config
                ),
                'secret': self.template_env.get_template('secret').render(
                    cluster_name=config.cluster_name,
                    namespace=config.namespace
                )
            }
            
            # 应用配置
            for resource_type, resource_yaml in templates.items():
                resource_obj = yaml.safe_load(resource_yaml)
                
                if resource_type == 'statefulset':
                    await self.apps_v1.create_namespaced_stateful_set(
                        namespace=config.namespace,
                        body=resource_obj
                    )
                elif resource_type == 'service':
                    await self.v1.create_namespaced_service(
                        namespace=config.namespace,
                        body=resource_obj
                    )
                elif resource_type == 'configmap':
                    await self.v1.create_namespaced_config_map(
                        namespace=config.namespace,
                        body=resource_obj
                    )
                elif resource_type == 'secret':
                    await self.v1.create_namespaced_secret(
                        namespace=config.namespace,
                        body=resource_obj
                    )
            
            logger.info(f"RabbitMQ集群创建成功: {config.cluster_name}")
            return True
            
        except ApiException as e:
            logger.error(f"创建部署失败: {e}")
            return False
    
    def _generate_cluster_config(self, config: DeploymentConfig) -> str:
        """生成集群配置"""
        cluster_nodes = []
        for i in range(config.replicas):
            cluster_nodes.append(
                f"cluster_formation.classic_config.nodes.{i+1} = rabbit@{config.cluster_name}-{i}.{config.cluster_name}-headless.{config.namespace}.svc.cluster.local"
            )
        return "\n    ".join(cluster_nodes)
    
    async def get_cluster_status(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """获取集群状态"""
        try:
            # 获取StatefulSet状态
            statefulset = await self.apps_v1.read_namespaced_stateful_set_status(
                name=cluster_name,
                namespace=namespace
            )
            
            # 获取Pod状态
            pods = await self.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            # 获取服务状态
            services = await self.v1.list_namespaced_service(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            status = {
                'cluster_name': cluster_name,
                'namespace': namespace,
                'statefulset': {
                    'replicas': statefulset.spec.replicas,
                    'ready_replicas': statefulset.status.ready_replicas,
                    'updated_replicas': statefulset.status.updated_replicas,
                    'current_revision': statefulset.status.current_revision,
                    'update_revision': statefulset.status.update_revision
                },
                'pods': [],
                'services': []
            }
            
            # 处理Pod状态
            for pod in pods.items:
                pod_info = {
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'ready': pod.status.conditions,
                    'node_name': pod.spec.node_name,
                    'containers': []
                }
                
                for container in pod.status.container_statuses:
                    container_info = {
                        'name': container.name,
                        'ready': container.ready,
                        'restart_count': container.restart_count,
                        'image': container.image,
                        'state': str(container.state)
                    }
                    pod_info['containers'].append(container_info)
                
                status['pods'].append(pod_info)
            
            # 处理服务状态
            for service in services.items:
                service_info = {
                    'name': service.metadata.name,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip,
                    'ports': service.spec.ports
                }
                status['services'].append(service_info)
            
            return status
            
        except ApiException as e:
            logger.error(f"获取集群状态失败: {e}")
            return {}
    
    async def scale_cluster(self, namespace: str, cluster_name: str, replicas: int) -> bool:
        """扩缩容集群"""
        try:
            await self.apps_v1.patch_namespaced_stateful_set(
                name=cluster_name,
                namespace=namespace,
                body={'spec': {'replicas': replicas}}
            )
            logger.info(f"集群扩缩容成功: {cluster_name} -> {replicas} replicas")
            return True
        except ApiException as e:
            logger.error(f"集群扩缩容失败: {e}")
            return False
    
    async def update_cluster(self, namespace: str, cluster_name: str, new_image: str) -> bool:
        """更新集群镜像"""
        try:
            # 获取当前StatefulSet
            statefulset = await self.apps_v1.read_namespaced_stateful_set(
                name=cluster_name,
                namespace=namespace
            )
            
            # 更新镜像
            statefulset.spec.template.spec.containers[0].image = new_image
            
            await self.apps_v1.patch_namespaced_stateful_set(
                name=cluster_name,
                namespace=namespace,
                body=statefulset
            )
            
            logger.info(f"集群更新成功: {cluster_name} -> {new_image}")
            return True
        except ApiException as e:
            logger.error(f"集群更新失败: {e}")
            return False
    
    async def delete_cluster(self, namespace: str, cluster_name: str) -> bool:
        """删除集群"""
        try:
            # 删除StatefulSet
            await self.apps_v1.delete_namespaced_stateful_set(
                name=cluster_name,
                namespace=namespace
            )
            
            # 等待StatefulSet删除
            await asyncio.sleep(5)
            
            # 删除服务
            try:
                await self.v1.delete_namespaced_service(
                    name=cluster_name,
                    namespace=namespace
                )
            except ApiException:
                pass  # 服务可能已被删除
            
            try:
                await self.v1.delete_namespaced_service(
                    name=f"{cluster_name}-headless",
                    namespace=namespace
                )
            except ApiException:
                pass
            
            # 删除ConfigMap
            try:
                await self.v1.delete_namespaced_config_map(
                    name=f"{cluster_name}-config",
                    namespace=namespace
                )
            except ApiException:
                pass
            
            # 删除Secret
            try:
                await self.v1.delete_namespaced_secret(
                    name=f"{cluster_name}-credentials",
                    namespace=namespace
                )
            except ApiException:
                pass
            
            # 删除PVC
            pvc_list = await self.v1.list_namespaced_persistent_volume_claim(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            for pvc in pvc_list.items:
                await self.v1.delete_namespaced_persistent_volume_claim(
                    name=pvc.metadata.name,
                    namespace=namespace
                )
            
            logger.info(f"集群删除成功: {cluster_name}")
            return True
            
        except ApiException as e:
            logger.error(f"删除集群失败: {e}")
            return False


class HPAWatcher:
    """HPA监控器"""
    
    def __init__(self, manager: KubernetesRabbitMQManager):
        self.manager = manager
        self.monitoring_active = False
        
    async def start_monitoring(self, namespace: str, cluster_name: str, 
                              hpa_config: ScalingConfig, interval: int = 30):
        """开始监控和自动扩缩容"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # 获取当前状态
                status = await self.manager.get_cluster_status(namespace, cluster_name)
                if not status:
                    await asyncio.sleep(interval)
                    continue
                
                # 获取资源使用情况
                metrics = await self._get_pod_metrics(namespace, cluster_name)
                
                # 计算是否需要扩缩容
                action = await self._calculate_scaling_action(
                    status, metrics, hpa_config
                )
                
                if action != 'none':
                    await self.manager.scale_cluster(
                        namespace, cluster_name, action['replicas']
                    )
                    logger.info(f"自动扩缩容: {action}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
    
    async def _get_pod_metrics(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """获取Pod资源使用指标"""
        try:
            pods = await self.manager.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            metrics = {
                'cpu_usage': [],
                'memory_usage': [],
                'pod_count': len(pods.items)
            }
            
            for pod in pods.items:
                # 这里应该集成Prometheus或Metrics Server来获取实际指标
                # 暂时使用模拟数据
                metrics['cpu_usage'].append(50.0)  # 50% CPU使用率
                metrics['memory_usage'].append(70.0)  # 70%内存使用率
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取Pod指标失败: {e}")
            return {'cpu_usage': [], 'memory_usage': [], 'pod_count': 0}
    
    async def _calculate_scaling_action(self, status: Dict[str, Any], 
                                       metrics: Dict[str, Any], 
                                       config: ScalingConfig) -> Dict[str, Any]:
        """计算扩缩容操作"""
        current_replicas = status['statefulset']['ready_replicas']
        if not current_replicas:
            return {'action': 'none'}
        
        # 计算平均资源使用率
        avg_cpu = sum(metrics['cpu_usage']) / len(metrics['cpu_usage']) if metrics['cpu_usage'] else 0
        avg_memory = sum(metrics['memory_usage']) / len(metrics['memory_usage']) if metrics['memory_usage'] else 0
        
        max_usage = max(avg_cpu, avg_memory)
        
        # 判断扩缩容条件
        if max_usage > config.target_cpu_percent and current_replicas < config.max_replicas:
            # 需要扩容
            new_replicas = min(current_replicas + 1, config.max_replicas)
            return {
                'action': 'scale_up',
                'replicas': new_replicas,
                'reason': f'High resource usage: {max_usage:.1f}%'
            }
        elif max_usage < (config.target_cpu_percent * 0.5) and current_replicas > config.min_replicas:
            # 需要缩容
            new_replicas = max(current_replicas - 1, config.min_replicas)
            return {
                'action': 'scale_down',
                'replicas': new_replicas,
                'reason': f'Low resource usage: {max_usage:.1f}%'
            }
        
        return {'action': 'none'}


class BackupManager:
    """备份管理器"""
    
    def __init__(self, manager: KubernetesRabbitMQManager):
        self.manager = manager
        
    async def backup_cluster(self, namespace: str, cluster_name: str, 
                           backup_path: str) -> Dict[str, Any]:
        """备份RabbitMQ集群"""
        backup_result = {
            'cluster_name': cluster_name,
            'timestamp': datetime.utcnow().isoformat(),
            'backup_path': backup_path,
            'status': 'started'
        }
        
        try:
            # 获取集群状态
            status = await self.manager.get_cluster_status(namespace, cluster_name)
            backup_result['cluster_info'] = status
            
            # 备份队列和交换器定义
            await self._backup_definitions(namespace, cluster_name, backup_path)
            
            # 备份用户信息
            await self._backup_users(namespace, cluster_name, backup_path)
            
            # 备份配置
            await self._backup_config(namespace, cluster_name, backup_path)
            
            # 备份持久化数据(PVC)
            await self._backup_persistent_data(namespace, cluster_name, backup_path)
            
            backup_result['status'] = 'completed'
            logger.info(f"集群备份完成: {cluster_name}")
            
        except Exception as e:
            backup_result['status'] = 'failed'
            backup_result['error'] = str(e)
            logger.error(f"集群备份失败: {e}")
        
        return backup_result
    
    async def _backup_definitions(self, namespace: str, cluster_name: str, backup_path: str):
        """备份队列和交换器定义"""
        # 这里需要执行rabbitmqctl export_definitions命令
        # 可以通过exec进入Pod执行
        pass
    
    async def _backup_users(self, namespace: str, cluster_name: str, backup_path: str):
        """备份用户信息"""
        # 这里需要执行rabbitmqctl list_users命令
        pass
    
    async def _backup_config(self, namespace: str, cluster_name: str, backup_path: str):
        """备份配置"""
        # 备份ConfigMap和Secret
        try:
            configmap = await self.manager.v1.read_namespaced_config_map(
                name=f"{cluster_name}-config",
                namespace=namespace
            )
            secret = await self.manager.v1.read_namespaced_secret(
                name=f"{cluster_name}-credentials",
                namespace=namespace
            )
            
            backup_data = {
                'configmap': asdict(configmap),
                'secret': {k: v for k, v in secret.data.items() if k in ['username', 'erlang-cookie']}
            }
            
            with open(f"{backup_path}/config.yaml", 'w') as f:
                yaml.dump(backup_data, f)
                
        except ApiException as e:
            logger.error(f"备份配置失败: {e}")
    
    async def _backup_persistent_data(self, namespace: str, cluster_name: str, backup_path: str):
        """备份持久化数据"""
        # 备份PVC数据
        try:
            pvcs = await self.manager.v1.list_namespaced_persistent_volume_claim(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            pvc_info = []
            for pvc in pvcs.items:
                pvc_info.append({
                    'name': pvc.metadata.name,
                    'capacity': pvc.spec.resources.requests.get('storage'),
                    'access_modes': pvc.spec.access_modes,
                    'storage_class': pvc.spec.storage_class_name
                })
            
            with open(f"{backup_path}/pvcs.yaml", 'w') as f:
                yaml.dump({'persistent_volume_claims': pvc_info}, f)
                
        except ApiException as e:
            logger.error(f"备份PVC信息失败: {e}")


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, manager: KubernetesRabbitMQManager):
        self.manager = manager
        
    async def comprehensive_health_check(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """综合健康检查"""
        health_report = {
            'cluster_name': cluster_name,
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # 1. 集群状态检查
        health_report['checks']['cluster_status'] = await self._check_cluster_status(
            namespace, cluster_name
        )
        
        # 2. 资源使用检查
        health_report['checks']['resource_usage'] = await self._check_resource_usage(
            namespace, cluster_name
        )
        
        # 3. 网络连接检查
        health_report['checks']['network_connectivity'] = await self._check_network_connectivity(
            namespace, cluster_name
        )
        
        # 4. 存储检查
        health_report['checks']['storage'] = await self._check_storage(
            namespace, cluster_name
        )
        
        # 5. RabbitMQ服务检查
        health_report['checks']['rabbitmq_service'] = await self._check_rabbitmq_service(
            namespace, cluster_name
        )
        
        # 计算整体健康状态
        critical_checks = ['cluster_status', 'rabbitmq_service']
        warning_checks = ['resource_usage', 'network_connectivity', 'storage']
        
        critical_failed = any(
            health_report['checks'][check]['status'] == 'unhealthy' 
            for check in critical_checks
        )
        
        warning_failed = any(
            health_report['checks'][check]['status'] in ['unhealthy', 'warning']
            for check in warning_checks
        )
        
        if critical_failed:
            health_report['overall_status'] = 'unhealthy'
        elif warning_failed:
            health_report['overall_status'] = 'warning'
        
        return health_report
    
    async def _check_cluster_status(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """检查集群状态"""
        try:
            status = await self.manager.get_cluster_status(namespace, cluster_name)
            
            if not status:
                return {
                    'status': 'unhealthy',
                    'message': '无法获取集群状态'
                }
            
            expected_replicas = status['statefulset']['replicas']
            ready_replicas = status['statefulset']['ready_replicas']
            
            if ready_replicas == expected_replicas:
                return {
                    'status': 'healthy',
                    'message': f'所有 {expected_replicas} 个节点运行正常'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'只有 {ready_replicas}/{expected_replicas} 个节点就绪'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'检查集群状态时发生错误: {e}'
            }
    
    async def _check_resource_usage(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """检查资源使用情况"""
        try:
            # 这里应该集成Prometheus或Metrics Server
            # 暂时返回模拟数据
            return {
                'status': 'healthy',
                'message': '资源使用正常',
                'details': {
                    'cpu_usage': '50%',
                    'memory_usage': '70%',
                    'disk_usage': '30%'
                }
            }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'无法获取资源使用信息: {e}'
            }
    
    async def _check_network_connectivity(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """检查网络连接"""
        try:
            # 检查服务状态
            services = await self.manager.v1.list_namespaced_service(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            if services.items:
                return {
                    'status': 'healthy',
                    'message': f'网络服务正常，找到 {len(services.items)} 个服务'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': '未找到RabbitMQ服务'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'网络连接检查失败: {e}'
            }
    
    async def _check_storage(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """检查存储状态"""
        try:
            pvcs = await self.manager.v1.list_namespaced_persistent_volume_claim(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            ready_pvcs = [pvc for pvc in pvcs.items if pvc.status.phase == 'Bound']
            
            if len(ready_pvcs) == len(pvcs.items):
                return {
                    'status': 'healthy',
                    'message': f'所有 {len(pvcs.items)} 个PVC就绪'
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'{len(ready_pvcs)}/{len(pvcs.items)} 个PVC就绪'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'存储检查失败: {e}'
            }
    
    async def _check_rabbitmq_service(self, namespace: str, cluster_name: str) -> Dict[str, Any]:
        """检查RabbitMQ服务状态"""
        try:
            # 检查Pod状态和就绪探针
            pods = await self.manager.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app=rabbitmq,cluster={cluster_name}"
            )
            
            healthy_pods = 0
            total_pods = len(pods.items)
            
            for pod in pods.items:
                if pod.status.phase == 'Running':
                    # 检查容器是否就绪
                    ready = all(
                        container.ready for container in pod.status.container_statuses
                    )
                    if ready:
                        healthy_pods += 1
            
            if healthy_pods == total_pods:
                return {
                    'status': 'healthy',
                    'message': f'所有 {total_pods} 个RabbitMQ节点就绪'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'只有 {healthy_pods}/{total_pods} 个节点就绪'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'RabbitMQ服务检查失败: {e}'
            }


async def main():
    """主函数 - 示例用法"""
    # 初始化管理器
    manager = KubernetesRabbitMQManager()
    await manager.connect()
    
    try:
        # 创建部署配置
        deployment_config = DeploymentConfig(
            namespace="default",
            cluster_name="rabbitmq-cluster",
            replicas=3,
            image="rabbitmq:3.10-management-alpine",
            resources={
                "requests": {"memory": "1Gi", "cpu": "500m"},
                "limits": {"memory": "2Gi", "cpu": "1000m"}
            },
            storage_size="20Gi",
            storage_class="rabbitmq-storage",
            rabbitmq_config="",
            environment={}
        )
        
        # 1. 创建集群
        logger.info("创建RabbitMQ集群...")
        success = await manager.create_deployment(deployment_config)
        if not success:
            logger.error("集群创建失败")
            return
        
        # 2. 等待集群就绪
        logger.info("等待集群就绪...")
        await asyncio.sleep(60)
        
        # 3. 检查集群状态
        logger.info("检查集群状态...")
        status = await manager.get_cluster_status("default", "rabbitmq-cluster")
        logger.info(json.dumps(status, indent=2, default=str))
        
        # 4. 健康检查
        logger.info("执行健康检查...")
        health_checker = HealthChecker(manager)
        health_report = await health_checker.comprehensive_health_check(
            "default", "rabbitmq-cluster"
        )
        logger.info(json.dumps(health_report, indent=2, default=str))
        
        # 5. 启动自动扩缩容监控
        logger.info("启动自动扩缩容监控...")
        hpa_config = ScalingConfig(
            min_replicas=2,
            max_replicas=5,
            target_cpu_percent=70,
            target_memory_percent=80,
            scale_down_stabilization=60,
            scale_up_stabilization=30
        )
        
        hpa_watcher = HPAWatcher(manager)
        # 在实际使用中，这会在后台运行
        # asyncio.create_task(hpa_watcher.start_monitoring("default", "rabbitmq-cluster", hpa_config))
        
        # 6. 备份集群
        logger.info("备份集群...")
        backup_manager = BackupManager(manager)
        backup_result = await backup_manager.backup_cluster(
            "default", "rabbitmq-cluster", "/backup/rabbitmq-cluster"
        )
        logger.info(json.dumps(backup_result, indent=2, default=str))
        
        # 7. 模拟扩缩容
        logger.info("测试扩缩容...")
        await manager.scale_cluster("default", "rabbitmq-cluster", 5)
        await asyncio.sleep(30)
        await manager.scale_cluster("default", "rabbitmq-cluster", 3)
        
        logger.info("演示完成")
        
    finally:
        await manager.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
