#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL云服务与容器化代码示例
包含AWS RDS、阿里云RDS、Docker容器化、Kubernetes部署等功能的演示

使用方法:
    python 10-MySQL云服务与容器化.py [选项]

示例:
    python 10-MySQL云服务与容器化.py --demo aws_rds
    python 10-MySQL云服务与容器化.py --demo aliyun_rds
    python 10-MySQL云服务与容器化.py --demo docker_mysql
    python 10-MySQL云服务与容器化.py --demo kubernetes_mysql
    python 10-MySQL云服务与容器化.py --demo all
"""

import sys
import os
import json
import time
import subprocess
import logging
import argparse
import yaml
from typing import Dict, List, Optional, Tuple

# 云服务SDK
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("警告: AWS SDK (boto3) 未安装，AWS相关功能将不可用")
    boto3 = None

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkrds.request.v20140815 import CreateDBInstanceRequest, DescribeDBInstancesRequest
    from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
except ImportError:
    print("警告: 阿里云SDK 未安装，阿里云相关功能将不可用")
    AcsClient = None

try:
    from tencentcloud.common import credential
    from tencentcloud.cdb.v20170320 import cdb_client, models
except ImportError:
    print("警告: 腾讯云SDK 未安装，腾讯云相关功能将不可用")
    cdb_client = None

# Docker和Kubernetes相关
try:
    import docker
except ImportError:
    print("警告: Docker SDK 未安装，Docker相关功能将不可用")
    docker = None

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
except ImportError:
    print("警告: Kubernetes Python客户端未安装，Kubernetes相关功能将不可用")
    client = None

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mysql_cloud_container.log')
    ]
)
logger = logging.getLogger(__name__)

class CloudMySQLManager:
    """云MySQL管理基类"""
    
    def __init__(self, config):
        """
        初始化云MySQL管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.region = config.get('region', 'us-east-1')
    
    def check_credentials(self) -> bool:
        """
        检查凭证是否有效
        
        Returns:
            凭证是否有效
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def list_instances(self) -> List[Dict]:
        """
        列出所有实例
        
        Returns:
            实例列表
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def create_instance(self, instance_config: Dict) -> Dict:
        """
        创建实例
        
        Args:
            instance_config: 实例配置
            
        Returns:
            创建的实例信息
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def delete_instance(self, instance_id: str) -> bool:
        """
        删除实例
        
        Args:
            instance_id: 实例ID
            
        Returns:
            是否删除成功
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def get_connection_info(self, instance_id: str) -> Dict:
        """
        获取实例连接信息
        
        Args:
            instance_id: 实例ID
            
        Returns:
            连接信息
        """
        raise NotImplementedError("子类必须实现此方法")

class AWSRDSManager(CloudMySQLManager):
    """AWS RDS MySQL管理器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        if not boto3:
            raise ImportError("需要安装boto3库: pip install boto3")
        
        # 初始化AWS客户端
        self.rds_client = boto3.client(
            'rds',
            region_name=self.region,
            aws_access_key_id=config.get('access_key_id'),
            aws_secret_access_key=config.get('secret_access_key')
        )
    
    def check_credentials(self) -> bool:
        """检查AWS凭证是否有效"""
        try:
            self.rds_client.describe_db_instances(MaxRecords=1)
            return True
        except ClientError as e:
            logger.error(f"AWS凭证验证失败: {e}")
            return False
    
    def list_instances(self) -> List[Dict]:
        """列出所有RDS实例"""
        try:
            response = self.rds_client.describe_db_instances()
            instances = []
            
            for db_instance in response.get('DBInstances', []):
                if db_instance.get('Engine') == 'mysql':
                    instances.append({
                        'id': db_instance.get('DBInstanceIdentifier'),
                        'engine': db_instance.get('Engine'),
                        'engine_version': db_instance.get('EngineVersion'),
                        'instance_class': db_instance.get('DBInstanceClass'),
                        'status': db_instance.get('DBInstanceStatus'),
                        'endpoint': db_instance.get('Endpoint', {}).get('Address'),
                        'port': db_instance.get('Endpoint', {}).get('Port'),
                        'storage': db_instance.get('AllocatedStorage'),
                        'multi_az': db_instance.get('MultiAZ'),
                        'publicly_accessible': db_instance.get('PubliclyAccessible'),
                        'created_time': db_instance.get('InstanceCreateTime').isoformat() if db_instance.get('InstanceCreateTime') else None
                    })
            
            return instances
        except ClientError as e:
            logger.error(f"获取RDS实例列表失败: {e}")
            return []
    
    def create_instance(self, instance_config: Dict) -> Dict:
        """创建RDS实例"""
        try:
            # 创建实例参数
            params = {
                'DBInstanceIdentifier': instance_config.get('identifier'),
                'DBInstanceClass': instance_config.get('instance_class', 'db.t3.micro'),
                'Engine': 'mysql',
                'MasterUsername': instance_config.get('username', 'admin'),
                'MasterUserPassword': instance_config.get('password'),
                'AllocatedStorage': instance_config.get('storage_size', 20),
                'BackupRetentionPeriod': instance_config.get('backup_retention', 7),
                'MultiAZ': instance_config.get('multi_az', False),
                'PubliclyAccessible': instance_config.get('publicly_accessible', False),
                'StorageType': instance_config.get('storage_type', 'gp2'),
                'EngineVersion': instance_config.get('engine_version', '8.0.35')
            }
            
            # 添加可选参数
            if 'vpc_security_group_ids' in instance_config:
                params['VpcSecurityGroupIds'] = instance_config['vpc_security_group_ids']
            
            if 'db_subnet_group_name' in instance_config:
                params['DBSubnetGroupName'] = instance_config['db_subnet_group_name']
            
            if 'tags' in instance_config:
                params['Tags'] = instance_config['tags']
            
            # 创建实例
            response = self.rds_client.create_db_instance(**params)
            db_instance = response.get('DBInstance')
            
            return {
                'id': db_instance.get('DBInstanceIdentifier'),
                'status': db_instance.get('DBInstanceStatus'),
                'endpoint': db_instance.get('Endpoint', {}).get('Address'),
                'port': db_instance.get('Endpoint', {}).get('Port'),
                'created_time': db_instance.get('InstanceCreateTime').isoformat() if db_instance.get('InstanceCreateTime') else None
            }
        except ClientError as e:
            logger.error(f"创建RDS实例失败: {e}")
            return {}
    
    def delete_instance(self, instance_id: str, skip_final_snapshot: bool = False) -> bool:
        """删除RDS实例"""
        try:
            self.rds_client.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=skip_final_snapshot
            )
            logger.info(f"已提交删除RDS实例请求: {instance_id}")
            return True
        except ClientError as e:
            logger.error(f"删除RDS实例失败: {e}")
            return False
    
    def get_connection_info(self, instance_id: str) -> Dict:
        """获取RDS实例连接信息"""
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=instance_id
            )
            db_instance = response.get('DBInstances', [{}])[0]
            endpoint = db_instance.get('Endpoint', {})
            
            return {
                'host': endpoint.get('Address'),
                'port': endpoint.get('Port'),
                'username': db_instance.get('MasterUsername'),
                'status': db_instance.get('DBInstanceStatus')
            }
        except ClientError as e:
            logger.error(f"获取RDS实例连接信息失败: {e}")
            return {}
    
    def wait_for_instance_available(self, instance_id: str, timeout: int = 1800) -> bool:
        """
        等待实例变为可用状态
        
        Args:
            instance_id: 实例ID
            timeout: 超时时间（秒）
            
        Returns:
            是否成功等待到可用状态
        """
        try:
            waiter = self.rds_client.get_waiter('db_instance_available')
            waiter.wait(
                DBInstanceIdentifier=instance_id,
                WaiterConfig={'Delay': 30, 'MaxAttempts': timeout // 30}
            )
            logger.info(f"RDS实例 {instance_id} 已变为可用状态")
            return True
        except Exception as e:
            logger.error(f"等待RDS实例可用超时: {e}")
            return False
    
    def create_read_replica(self, source_instance_id: str, replica_config: Dict) -> Dict:
        """创建只读副本"""
        try:
            params = {
                'DBInstanceIdentifier': replica_config.get('identifier'),
                'SourceDBInstanceIdentifier': source_instance_id,
                'DBInstanceClass': replica_config.get('instance_class', 'db.t3.micro'),
                'PubliclyAccessible': replica_config.get('publicly_accessible', False)
            }
            
            if 'tags' in replica_config:
                params['Tags'] = replica_config['tags']
            
            response = self.rds_client.create_db_instance_read_replica(**params)
            db_instance = response.get('DBInstance')
            
            return {
                'id': db_instance.get('DBInstanceIdentifier'),
                'status': db_instance.get('DBInstanceStatus'),
                'source_id': db_instance.get('ReadReplicaSourceDBInstanceIdentifier')
            }
        except ClientError as e:
            logger.error(f"创建只读副本失败: {e}")
            return {}
    
    def create_snapshot(self, instance_id: str, snapshot_id: str) -> Dict:
        """创建手动快照"""
        try:
            response = self.rds_client.create_db_snapshot(
                DBInstanceIdentifier=instance_id,
                DBSnapshotIdentifier=snapshot_id
            )
            db_snapshot = response.get('DBSnapshot')
            
            return {
                'id': db_snapshot.get('DBSnapshotIdentifier'),
                'status': db_snapshot.get('Status'),
                'instance_id': db_snapshot.get('DBInstanceIdentifier'),
                'created_time': db_snapshot.get('SnapshotCreateTime').isoformat() if db_snapshot.get('SnapshotCreateTime') else None
            }
        except ClientError as e:
            logger.error(f"创建快照失败: {e}")
            return {}
    
    def demo_aws_rds(self):
        """演示AWS RDS功能"""
        print("\n===== AWS RDS MySQL演示 =====")
        
        try:
            # 1. 检查凭证
            print("\n1. 检查AWS凭证:")
            if not self.check_credentials():
                print("  AWS凭证验证失败，请检查access_key和secret_key")
                return
            
            print("  ✅ AWS凭证验证成功")
            
            # 2. 列出现有实例
            print("\n2. 列出现有RDS实例:")
            instances = self.list_instances()
            
            if instances:
                for instance in instances:
                    print(f"  - {instance['id']}")
                    print(f"    引擎: {instance['engine']} {instance['engine_version']}")
                    print(f"    规格: {instance['instance_class']}")
                    print(f"    状态: {instance['status']}")
                    print(f"    端点: {instance['endpoint']}:{instance['port']}")
                    print(f"    存储空间: {instance['storage']}GB")
                    print(f"    多可用区: {'是' if instance['multi_az'] else '否'}")
                    print(f"    创建时间: {instance['created_time']}")
                    print()
            else:
                print("  没有找到MySQL实例")
            
            # 3. 创建新实例（仅演示，不实际创建）
            print("\n3. 创建新RDS实例（演示模式，不实际创建）:")
            instance_config = {
                'identifier': f'demo-mysql-{int(time.time())}',
                'instance_class': 'db.t3.micro',
                'username': 'admin',
                'password': 'DemoPassword123!',
                'storage_size': 20,
                'backup_retention': 7,
                'multi_az': False,
                'publicly_accessible': False,
                'engine_version': '8.0.35',
                'tags': [
                    {'Key': 'Environment', 'Value': 'Demo'},
                    {'Key': 'Owner', 'Value': 'MySQL教程'}
                ]
            }
            
            print("  实例配置:")
            for key, value in instance_config.items():
                if key != 'password':
                    print(f"    {key}: {value}")
                else:
                    print(f"    {key}: {'*' * len(value)}")
            
            # 取消注释下面这行可以实际创建实例
            # result = self.create_instance(instance_config)
            # print(f"  创建结果: {result['id']} - 状态: {result['status']}")
            
            print("  [演示模式] 实际创建需要取消代码注释并确保有足够的AWS权限")
            
            # 4. 获取实例连接信息（使用第一个可用实例）
            if instances:
                print("\n4. 获取实例连接信息:")
                example_instance = instances[0]
                connection_info = self.get_connection_info(example_instance['id'])
                
                print(f"  实例ID: {example_instance['id']}")
                print(f"  连接地址: {connection_info['host']}")
                print(f"  端口: {connection_info['port']}")
                print(f"  用户名: {connection_info['username']}")
                print(f"  状态: {connection_info['status']}")
                
                # 5. 连接示例代码
                print("\n5. Python连接示例:")
                connection_code = f'''
import pymysql

# 连接AWS RDS MySQL
connection = pymysql.connect(
    host="{connection_info['host']}",
    port={connection_info['port']},
    user="{connection_info['username']}",
    password="您的密码",
    database="您的数据库名"
)

# 使用连接
with connection.cursor() as cursor:
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL版本: {version[0]}")

connection.close()
'''
                print(connection_code)
                
                # 6. 创建只读副本（仅演示）
                print("\n6. 创建只读副本（演示模式）:")
                replica_config = {
                    'identifier': f"{example_instance['id']}-replica",
                    'instance_class': example_instance['instance_class'],
                    'publicly_accessible': False
                }
                
                print("  副本配置:")
                for key, value in replica_config.items():
                    print(f"    {key}: {value}")
                
                # 取消注释下面这行可以实际创建副本
                # replica_result = self.create_read_replica(example_instance['id'], replica_config)
                # print(f"  副本创建结果: {replica_result['id']} - 状态: {replica_result['status']}")
                
                print("  [演示模式] 实际创建需要取消代码注释")
                
                # 7. 创建快照（仅演示）
                print("\n7. 创建快照（演示模式）:")
                snapshot_id = f"{example_instance['id']}-snapshot-{int(time.time())}"
                
                print(f"  快照ID: {snapshot_id}")
                
                # 取消注释下面这行可以实际创建快照
                # snapshot_result = self.create_snapshot(example_instance['id'], snapshot_id)
                # print(f"  快照创建结果: {snapshot_result['id']} - 状态: {snapshot_result['status']}")
                
                print("  [演示模式] 实际创建需要取消代码注释")
            
            print("\n✅ AWS RDS MySQL演示完成")
            
        except Exception as e:
            logger.error(f"AWS RDS演示失败: {e}")

class AliyunRDSManager(CloudMySQLManager):
    """阿里云RDS MySQL管理器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        if not AcsClient:
            raise ImportError("需要安装阿里云SDK: pip install aliyun-python-sdk-core aliyun-python-sdk-rds")
        
        # 初始化阿里云客户端
        self.client = AcsClient(
            config.get('access_key_id'),
            config.get('access_key_secret'),
            self.region
        )
    
    def check_credentials(self) -> bool:
        """检查阿里云凭证是否有效"""
        try:
            request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
            request.set_PageSize(1)
            self.client.do_action_with_exception(request)
            return True
        except (ServerException, ClientException) as e:
            logger.error(f"阿里云凭证验证失败: {e}")
            return False
    
    def list_instances(self) -> List[Dict]:
        """列出所有RDS实例"""
        try:
            request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
            request.set_PageSize(100)
            
            instances = []
            response = self.client.do_action_with_exception(request)
            data = json.loads(response)
            
            for item in data.get('Items', {}).get('DBInstance', []):
                if 'mysql' in item.get('Engine', '').lower():
                    instances.append({
                        'id': item.get('DBInstanceId'),
                        'engine': item.get('Engine'),
                        'engine_version': item.get('EngineVersion'),
                        'instance_class': item.get('DBInstanceClass'),
                        'status': item.get('DBInstanceStatus'),
                        'region': item.get('RegionId'),
                        'zone_id': item.get('ZoneId'),
                        'storage': item.get('DBInstanceStorage'),
                        'create_time': item.get('CreateTime'),
                        'expire_time': item.get('ExpireTime'),
                        'instance_type': item.get('InstanceType')
                    })
            
            return instances
        except (ServerException, ClientException) as e:
            logger.error(f"获取阿里云RDS实例列表失败: {e}")
            return []
    
    def create_instance(self, instance_config: Dict) -> Dict:
        """创建RDS实例"""
        try:
            request = CreateDBInstanceRequest.CreateDBInstanceRequest()
            
            # 设置请求参数
            request.set_Engine('MySQL')
            request.set_EngineVersion(instance_config.get('engine_version', '8.0'))
            request.set_DBInstanceClass(instance_config.get('instance_class', 'mysql.n2.small.1'))
            request.set_DBInstanceStorage(instance_config.get('storage_size', 20))
            request.set_DBInstanceStorageType(instance_config.get('storage_type', 'cloud_essd'))
            request.set_SecurityIPList(instance_config.get('security_ip_list', '0.0.0.0/0'))
            request.set_PayType(instance_config.get('pay_type', 'Postpaid'))
            request.set_InstanceNetworkType(instance_config.get('instance_network_type', 'VPC'))
            
            if 'zone_id' in instance_config:
                request.set_ZoneId(instance_config['zone_id'])
            
            if 'vpc_id' in instance_config:
                request.set_VPCId(instance_config['vpc_id'])
            
            if 'vswitch_id' in instance_config:
                request.set_VSwitchId(instance_config['vswitch_id'])
            
            # 发送请求
            response = self.client.do_action_with_exception(request)
            data = json.loads(response)
            
            return {
                'id': data.get('DBInstanceId'),
                'order_id': data.get('OrderId')
            }
        except (ServerException, ClientException) as e:
            logger.error(f"创建阿里云RDS实例失败: {e}")
            return {}
    
    def delete_instance(self, instance_id: str) -> bool:
        """删除RDS实例"""
        # 阿里云删除实例需要使用其他API，这里只提供框架
        logger.info(f"删除阿里云RDS实例: {instance_id}")
        return True
    
    def get_connection_info(self, instance_id: str) -> Dict:
        """获取RDS实例连接信息"""
        # 阿里云获取连接信息需要使用其他API，这里只提供框架
        return {
            'host': f'{instance_id}.mysql.rds.aliyuncs.com',
            'port': 3306,
            'username': 'root',
            'status': 'Unknown'
        }
    
    def demo_aliyun_rds(self):
        """演示阿里云RDS功能"""
        print("\n===== 阿里云RDS MySQL演示 =====")
        
        try:
            # 1. 检查凭证
            print("\n1. 检查阿里云凭证:")
            if not self.check_credentials():
                print("  阿里云凭证验证失败，请检查access_key_id和access_key_secret")
                return
            
            print("  ✅ 阿里云凭证验证成功")
            
            # 2. 列出现有实例
            print("\n2. 列出现有RDS实例:")
            instances = self.list_instances()
            
            if instances:
                for instance in instances:
                    print(f"  - {instance['id']}")
                    print(f"    引擎: {instance['engine']} {instance['engine_version']}")
                    print(f"    规格: {instance['instance_class']}")
                    print(f"    状态: {instance['status']}")
                    print(f"    区域: {instance['region']}")
                    print(f"    可用区: {instance['zone_id']}")
                    print(f"    存储空间: {instance['storage']}GB")
                    print(f"    创建时间: {instance['create_time']}")
                    print(f"    实例类型: {instance['instance_type']}")
                    print()
            else:
                print("  没有找到MySQL实例")
            
            # 3. 创建新实例（仅演示，不实际创建）
            print("\n3. 创建新RDS实例（演示模式，不实际创建）:")
            instance_config = {
                'engine_version': '8.0',
                'instance_class': 'mysql.n2.small.1',
                'storage_size': 20,
                'storage_type': 'cloud_essd',
                'security_ip_list': '0.0.0.0/0',
                'pay_type': 'Postpaid',
                'instance_network_type': 'VPC',
                'zone_id': 'cn-hangzhou-h'  # 替换为实际可用区
            }
            
            print("  实例配置:")
            for key, value in instance_config.items():
                print(f"    {key}: {value}")
            
            # 取消注释下面这行可以实际创建实例
            # result = self.create_instance(instance_config)
            # print(f"  创建结果: 实例ID {result['id']}, 订单ID {result['order_id']}")
            
            print("  [演示模式] 实际创建需要取消代码注释并确保有足够的阿里云权限")
            
            # 4. 连接示例代码
            if instances:
                print("\n4. Python连接示例:")
                example_instance = instances[0]
                connection_info = self.get_connection_info(example_instance['id'])
                
                connection_code = f'''
import pymysql

# 连接阿里云RDS MySQL
connection = pymysql.connect(
    host="{connection_info['host']}",
    port={connection_info['port']},
    user="{connection_info['username']}",
    password="您的密码",
    database="您的数据库名"
)

# 使用连接
with connection.cursor() as cursor:
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL版本: {version[0]}")

connection.close()
'''
                print(connection_code)
            
            print("\n✅ 阿里云RDS MySQL演示完成")
            
        except Exception as e:
            logger.error(f"阿里云RDS演示失败: {e}")

class DockerMySQLManager:
    """Docker MySQL管理器"""
    
    def __init__(self, config=None):
        """
        初始化Docker MySQL管理器
        
        Args:
            config: 配置字典
        """
        if not docker:
            raise ImportError("需要安装Docker SDK: pip install docker")
        
        self.docker_client = docker.from_env()
        self.config = config or {}
        self.default_image = self.config.get('image', 'mysql:8.0')
    
    def list_containers(self, all_containers: bool = False) -> List[Dict]:
        """
        列出MySQL容器
        
        Args:
            all_containers: 是否列出所有容器（包括停止的）
            
        Returns:
            容器列表
        """
        try:
            containers = self.docker_client.containers.list(all=all_containers)
            mysql_containers = []
            
            for container in containers:
                image_name = container.image.tags[0] if container.image.tags else ""
                if "mysql" in image_name.lower():
                    mysql_containers.append({
                        'id': container.short_id,
                        'name': container.name,
                        'status': container.status,
                        'image': image_name,
                        'ports': container.ports,
                        'created': container.attrs['Created'],
                        'labels': container.labels
                    })
            
            return mysql_containers
        except Exception as e:
            logger.error(f"获取Docker容器列表失败: {e}")
            return []
    
    def run_container(self, container_config: Dict) -> str:
        """
        运行MySQL容器
        
        Args:
            container_config: 容器配置
            
        Returns:
            容器ID
        """
        try:
            # 环境变量
            environment = {
                'MYSQL_ROOT_PASSWORD': container_config.get('root_password', 'my-secret-pw')
            }
            
            if 'database' in container_config:
                environment['MYSQL_DATABASE'] = container_config['database']
            
            if 'user' in container_config:
                environment['MYSQL_USER'] = container_config['user']
            
            if 'password' in container_config:
                environment['MYSQL_PASSWORD'] = container_config['password']
            
            # 端口映射
            ports = {}
            if 'port' in container_config:
                ports['3306/tcp'] = ('0.0.0.0', container_config['port'])
            
            # 卷映射
            volumes = {}
            if 'data_volume' in container_config:
                volumes[container_config['data_volume']] = {'bind': '/var/lib/mysql', 'mode': 'rw'}
            
            if 'config_volume' in container_config:
                volumes[container_config['config_volume']] = {'bind': '/etc/mysql/conf.d', 'mode': 'ro'}
            
            # 运行容器
            container = self.docker_client.containers.run(
                image=container_config.get('image', self.default_image),
                name=container_config.get('name'),
                environment=environment,
                ports=ports,
                volumes=volumes,
                detach=True,
                restart_policy={"Name": container_config.get('restart_policy', 'no')}
            )
            
            logger.info(f"启动MySQL容器: {container.short_id} ({container.name})")
            return container.short_id
            
        except Exception as e:
            logger.error(f"启动MySQL容器失败: {e}")
            return ""
    
    def stop_container(self, container_id: str) -> bool:
        """
        停止容器
        
        Args:
            container_id: 容器ID
            
        Returns:
            是否成功停止
        """
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
            logger.info(f"已停止容器: {container_id}")
            return True
        except Exception as e:
            logger.error(f"停止容器失败: {e}")
            return False
    
    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """
        删除容器
        
        Args:
            container_id: 容器ID
            force: 是否强制删除
            
        Returns:
            是否成功删除
        """
        try:
            container = self.docker_client.containers.get(container_id)
            container.remove(force=force)
            logger.info(f"已删除容器: {container_id}")
            return True
        except Exception as e:
            logger.error(f"删除容器失败: {e}")
            return False
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """
        获取容器日志
        
        Args:
            container_id: 容器ID
            tail: 获取最后几行日志
            
        Returns:
            容器日志
        """
        try:
            container = self.docker_client.containers.get(container_id)
            return container.logs(tail=tail, timestamps=True).decode('utf-8')
        except Exception as e:
            logger.error(f"获取容器日志失败: {e}")
            return ""
    
    def exec_command(self, container_id: str, command: List[str]) -> Tuple[int, str]:
        """
        在容器中执行命令
        
        Args:
            container_id: 容器ID
            command: 命令列表
            
        Returns:
            (退出码, 输出)
        """
        try:
            container = self.docker_client.containers.get(container_id)
            result = container.exec_run(command)
            return result.exit_code, result.output.decode('utf-8')
        except Exception as e:
            logger.error(f"执行容器命令失败: {e}")
            return 1, str(e)
    
    def demo_docker_mysql(self):
        """演示Docker MySQL功能"""
        print("\n===== Docker MySQL演示 =====")
        
        try:
            # 1. 列出现有容器
            print("\n1. 列出现有MySQL容器:")
            containers = self.list_containers()
            
            if containers:
                for container in containers:
                    print(f"  - {container['name']} ({container['id']})")
                    print(f"    状态: {container['status']}")
                    print(f"    镜像: {container['image']}")
                    if container['ports']:
                        print(f"    端口: {container['ports']}")
                    print(f"    创建时间: {container['created']}")
                    print()
            else:
                print("  没有找到MySQL容器")
            
            # 2. 创建MySQL容器
            print("\n2. 创建MySQL容器:")
            container_config = {
                'name': f'mysql-demo-{int(time.time())}',
                'image': 'mysql:8.0',
                'root_password': 'DemoPassword123!',
                'database': 'demo_db',
                'user': 'demo_user',
                'password': 'DemoUserPassword123!',
                'port': 33306,  # 使用非标准端口避免冲突
                'restart_policy': 'unless-stopped'
            }
            
            print("  容器配置:")
            for key, value in container_config.items():
                if key == 'password' or key == 'root_password':
                    print(f"    {key}: {'*' * len(str(value))}")
                else:
                    print(f"    {key}: {value}")
            
            # 检查是否有可用的数据卷路径
            import tempfile
            data_dir = tempfile.mkdtemp(prefix='mysql_data_')
            container_config['data_volume'] = data_dir
            print(f"    数据目录: {data_dir}")
            
            try:
                # 创建容器
                container_id = self.run_container(container_config)
                
                if container_id:
                    print(f"  ✅ 容器创建成功: {container_id}")
                    
                    # 等待容器启动
                    print("\n3. 等待MySQL服务启动...")
                    time.sleep(30)
                    
                    # 检查容器状态
                    containers = self.list_containers()
                    for container in containers:
                        if container['id'].startswith(container_id):
                            print(f"  容器状态: {container['status']}")
                            break
                    
                    # 4. 获取容器日志
                    print("\n4. 获取容器日志（最后10行）:")
                    logs = self.get_container_logs(container_id, 10)
                    if logs:
                        print("  日志内容:")
                        for line in logs.split('\n')[-10:]:
                            if line.strip():
                                print(f"    {line}")
                    
                    # 5. 在容器中执行命令
                    print("\n5. 在容器中执行命令:")
                    
                    # 检查MySQL版本
                    exit_code, output = self.exec_command(container_id, ['mysql', '--version'])
                    if exit_code == 0:
                        print(f"  MySQL版本: {output.strip()}")
                    
                    # 连接MySQL并创建测试表
                    mysql_commands = [
                        'mysql',
                        '-u', 'root',
                        f'-p{container_config["root_password"]}',
                        '-e', 'CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50));'
                    ]
                    exit_code, output = self.exec_command(container_id, mysql_commands)
                    if exit_code == 0:
                        print("  ✅ 创建测试表成功")
                    
                    # 插入测试数据
                    insert_commands = [
                        'mysql',
                        '-u', 'root',
                        f'-p{container_config["root_password"]}',
                        '-e', 'INSERT INTO test_table (name) VALUES ("Docker测试");'
                    ]
                    exit_code, output = self.exec_command(container_id, insert_commands)
                    if exit_code == 0:
                        print("  ✅ 插入测试数据成功")
                    
                    # 查询测试数据
                    select_commands = [
                        'mysql',
                        '-u', 'root',
                        f'-p{container_config["root_password"]}',
                        '-e', 'SELECT * FROM test_table;'
                    ]
                    exit_code, output = self.exec_command(container_id, select_commands)
                    if exit_code == 0:
                        print("  查询结果:")
                        for line in output.strip().split('\n'):
                            if line.strip():
                                print(f"    {line}")
                    
                    # 6. Python连接示例
                    print("\n6. Python连接示例:")
                    connection_code = f'''
import pymysql

# 连接Docker中的MySQL
connection = pymysql.connect(
    host="localhost",
    port={container_config['port']},
    user="root",
    password="{container_config['root_password']}",
    database="{container_config['database']}"
)

# 使用连接
with connection.cursor() as cursor:
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL版本: {version[0]}")

connection.close()
'''
                    print(connection_code)
                    
                    # 7. 清理演示容器
                    print("\n7. 清理演示容器:")
                    self.stop_container(container_id)
                    self.remove_container(container_id)
                    print(f"  ✅ 已停止并删除容器: {container_id}")
                    
                    # 清理临时目录
                    import shutil
                    shutil.rmtree(data_dir)
                    print(f"  ✅ 已清理临时数据目录: {data_dir}")
                
                else:
                    print("  ❌ 容器创建失败")
                    
            except Exception as e:
                print(f"  ❌ 容器操作出错: {e}")
                
                # 尝试清理
                if 'container_id' in locals() and container_id:
                    try:
                        self.stop_container(container_id)
                        self.remove_container(container_id)
                    except:
                        pass
            
            print("\n✅ Docker MySQL演示完成")
            
        except Exception as e:
            logger.error(f"Docker MySQL演示失败: {e}")

class KubernetesMySQLManager:
    """Kubernetes MySQL管理器"""
    
    def __init__(self, config=None):
        """
        初始化Kubernetes MySQL管理器
        
        Args:
            config: 配置字典
        """
        if not client:
            raise ImportError("需要安装Kubernetes Python客户端: pip install kubernetes")
        
        self.config = config or {}
        
        try:
            # 加载kubeconfig
            if 'kubeconfig_path' in self.config:
                config.load_kube_config(config_file=self.config['kubeconfig_path'])
            else:
                config.load_kube_config()  # 默认路径
            
            # 初始化API客户端
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            
        except Exception as e:
            logger.error(f"初始化Kubernetes客户端失败: {e}")
            raise
    
    def list_deployments(self, namespace: str = 'default') -> List[Dict]:
        """
        列出MySQL部署
        
        Args:
            namespace: 命名空间
            
        Returns:
            部署列表
        """
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            mysql_deployments = []
            
            for deployment in deployments.items:
                # 检查部署是否使用了MySQL镜像
                if deployment.spec.template.spec.containers:
                    for container in deployment.spec.template.spec.containers:
                        if 'mysql' in container.image.lower():
                            mysql_deployments.append({
                                'name': deployment.metadata.name,
                                'namespace': deployment.metadata.namespace,
                                'image': container.image,
                                'replicas': deployment.spec.replicas,
                                'available_replicas': deployment.status.available_replicas or 0,
                                'created': deployment.metadata.creation_timestamp.isoformat() if deployment.metadata.creation_timestamp else None
                            })
                            break
            
            return mysql_deployments
        except ApiException as e:
            logger.error(f"获取Kubernetes部署列表失败: {e}")
            return []
    
    def list_statefulsets(self, namespace: str = 'default') -> List[Dict]:
        """
        列出MySQL StatefulSet
        
        Args:
            namespace: 命名空间
            
        Returns:
            StatefulSet列表
        """
        try:
            statefulsets = self.apps_v1.list_namespaced_stateful_set(namespace=namespace)
            mysql_statefulsets = []
            
            for statefulset in statefulsets.items:
                # 检查StatefulSet是否使用了MySQL镜像
                if statefulset.spec.template.spec.containers:
                    for container in statefulset.spec.template.spec.containers:
                        if 'mysql' in container.image.lower():
                            mysql_statefulsets.append({
                                'name': statefulset.metadata.name,
                                'namespace': statefulset.metadata.namespace,
                                'image': container.image,
                                'replicas': statefulset.spec.replicas,
                                'ready_replicas': statefulset.status.ready_replicas or 0,
                                'created': statefulset.metadata.creation_timestamp.isoformat() if statefulset.metadata.creation_timestamp else None
                            })
                            break
            
            return mysql_statefulsets
        except ApiException as e:
            logger.error(f"获取Kubernetes StatefulSet列表失败: {e}")
            return []
    
    def list_services(self, namespace: str = 'default') -> List[Dict]:
        """
        列出MySQL服务
        
        Args:
            namespace: 命名空间
            
        Returns:
            服务列表
        """
        try:
            services = self.v1.list_namespaced_service(namespace=namespace)
            mysql_services = []
            
            for service in services.items:
                # 检查服务是否关联到MySQL应用
                selector = service.spec.selector or {}
                if 'app' in selector and 'mysql' in selector['app'].lower():
                    mysql_services.append({
                        'name': service.metadata.name,
                        'namespace': service.metadata.namespace,
                        'type': service.spec.type,
                        'cluster_ip': service.spec.cluster_ip,
                        'external_ip': service.status.load_balancer.ingress[0].ip if (
                            service.status.load_balancer and service.status.load_balancer.ingress
                        ) else None,
                        'ports': [
                            {
                                'name': port.name,
                                'port': port.port,
                                'target_port': port.target_port,
                                'protocol': port.protocol
                            }
                            for port in (service.spec.ports or [])
                        ],
                        'created': service.metadata.creation_timestamp.isoformat() if service.metadata.creation_timestamp else None
                    })
            
            return mysql_services
        except ApiException as e:
            logger.error(f"获取Kubernetes服务列表失败: {e}")
            return []
    
    def create_namespace(self, name: str) -> bool:
        """
        创建命名空间
        
        Args:
            name: 命名空间名称
            
        Returns:
            是否创建成功
        """
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=name)
            )
            self.v1.create_namespace(namespace)
            logger.info(f"创建命名空间: {name}")
            return True
        except ApiException as e:
            if e.status == 409:  # 已存在
                logger.info(f"命名空间已存在: {name}")
                return True
            logger.error(f"创建命名空间失败: {e}")
            return False
    
    def create_secret(self, namespace: str, name: str, data: Dict) -> bool:
        """
        创建Secret
        
        Args:
            namespace: 命名空间
            name: Secret名称
            data: 数据字典
            
        Returns:
            是否创建成功
        """
        try:
            # 将字符串值转换为base64
            import base64
            secret_data = {
                key: base64.b64encode(value.encode()).decode()
                for key, value in data.items()
            }
            
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                type='Opaque',
                data=secret_data
            )
            
            self.v1.create_namespaced_secret(namespace, secret)
            logger.info(f"创建Secret: {namespace}/{name}")
            return True
        except ApiException as e:
            logger.error(f"创建Secret失败: {e}")
            return False
    
    def create_configmap(self, namespace: str, name: str, data: Dict) -> bool:
        """
        创建ConfigMap
        
        Args:
            namespace: 命名空间
            name: ConfigMap名称
            data: 数据字典
            
        Returns:
            是否创建成功
        """
        try:
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                data=data
            )
            
            self.v1.create_namespaced_config_map(namespace, configmap)
            logger.info(f"创建ConfigMap: {namespace}/{name}")
            return True
        except ApiException as e:
            logger.error(f"创建ConfigMap失败: {e}")
            return False
    
    def create_pvc(self, namespace: str, name: str, size: str, storage_class: str = None) -> bool:
        """
        创建PersistentVolumeClaim
        
        Args:
            namespace: 命名空间
            name: PVC名称
            size: 存储大小
            storage_class: 存储类
            
        Returns:
            是否创建成功
        """
        try:
            pvc = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=['ReadWriteOnce'],
                    resources=client.V1ResourceRequirements(
                        requests={'storage': size}
                    )
                )
            )
            
            if storage_class:
                pvc.spec.storage_class_name = storage_class
            
            self.v1.create_namespaced_persistent_volume_claim(namespace, pvc)
            logger.info(f"创建PVC: {namespace}/{name}")
            return True
        except ApiException as e:
            logger.error(f"创建PVC失败: {e}")
            return False
    
    def create_statefulset_mysql(self, namespace: str, name: str, config: Dict) -> bool:
        """
        创建MySQL StatefulSet
        
        Args:
            namespace: 命名空间
            name: StatefulSet名称
            config: 配置字典
            
        Returns:
            是否创建成功
        """
        try:
            # 容器环境变量
            env_vars = [
                client.V1EnvVar(
                    name='MYSQL_ROOT_PASSWORD',
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name='mysql-secret',
                            key='mysql-root-password'
                        )
                    )
                )
            ]
            
            if 'database' in config:
                env_vars.append(
                    client.V1EnvVar(name='MYSQL_DATABASE', value=config['database'])
                )
            
            if 'user' in config and 'password' in config:
                env_vars.extend([
                    client.V1EnvVar(name='MYSQL_USER', value=config['user']),
                    client.V1EnvVar(
                        name='MYSQL_PASSWORD',
                        value_from=client.V1EnvVarSource(
                            secret_key_ref=client.V1SecretKeySelector(
                                name='mysql-secret',
                                key='mysql-password'
                            )
                        )
                    )
                ])
            
            # 容器配置
            container = client.V1Container(
                name='mysql',
                image=config.get('image', 'mysql:8.0'),
                ports=[client.V1ContainerPort(container_port=3306)],
                env=env_vars,
                volume_mounts=[
                    client.V1VolumeMount(
                        name='mysql-data',
                        mount_path='/var/lib/mysql'
                    )
                ]
            )
            
            # 如果有配置文件，添加ConfigMap挂载
            if 'configmap' in config:
                container.volume_mounts.append(
                    client.V1VolumeMount(
                        name='mysql-config',
                        mount_path='/etc/mysql/conf.d',
                        read_only=True
                    )
                )
            
            # Pod模板
            pod_template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={'app': name}
                ),
                spec=client.V1PodSpec(containers=[container])
            )
            
            # 卷配置
            volume_templates = [
                client.V1PersistentVolumeClaim(
                    metadata=client.V1ObjectMeta(name='mysql-data'),
                    spec=client.V1PersistentVolumeClaimSpec(
                        access_modes=['ReadWriteOnce'],
                        resources=client.V1ResourceRequirements(
                            requests={'storage': config.get('storage_size', '20Gi')}
                        )
                    )
                )
            ]
            
            # 如果有配置文件，添加ConfigMap卷
            if 'configmap' in config:
                pod_template.spec.volumes = [
                    client.V1Volume(
                        name='mysql-config',
                        config_map=client.V1ConfigMapVolumeSource(
                            name='mysql-config'
                        )
                    )
                ]
            
            # StatefulSet配置
            statefulset = client.V1StatefulSet(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                spec=client.V1StatefulSetSpec(
                    service_name=name,
                    replicas=config.get('replicas', 1),
                    selector=client.V1LabelSelector(
                        match_labels={'app': name}
                    ),
                    template=pod_template,
                    volume_claim_templates=volume_templates
                )
            )
            
            self.apps_v1.create_namespaced_stateful_set(namespace, statefulset)
            logger.info(f"创建StatefulSet: {namespace}/{name}")
            return True
            
        except ApiException as e:
            logger.error(f"创建StatefulSet失败: {e}")
            return False
    
    def create_service_mysql(self, namespace: str, name: str, service_type: str = 'ClusterIP') -> bool:
        """
        创建MySQL服务
        
        Args:
            namespace: 命名空间
            name: 服务名称
            service_type: 服务类型
            
        Returns:
            是否创建成功
        """
        try:
            service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                spec=client.V1ServiceSpec(
                    selector={'app': name},
                    ports=[client.V1ServicePort(port=3306, target_port=3306)],
                    type=service_type
                )
            )
            
            self.v1.create_namespaced_service(namespace, service)
            logger.info(f"创建服务: {namespace}/{name}")
            return True
            
        except ApiException as e:
            logger.error(f"创建服务失败: {e}")
            return False
    
    def demo_kubernetes_mysql(self):
        """演示Kubernetes MySQL功能"""
        print("\n===== Kubernetes MySQL演示 =====")
        
        try:
            # 1. 检查连接
            print("\n1. 检查Kubernetes连接:")
            try:
                self.v1.get_api_resources()
                print("  ✅ Kubernetes连接成功")
            except Exception as e:
                print(f"  ❌ Kubernetes连接失败: {e}")
                return
            
            # 2. 列出现有资源
            print("\n2. 列出现有MySQL资源:")
            
            # 列出StatefulSet
            statefulsets = self.list_statefulsets()
            if statefulsets:
                print("  StatefulSet:")
                for statefulset in statefulsets:
                    print(f"    - {statefulset['name']}/{statefulset['namespace']}")
                    print(f"      镜像: {statefulset['image']}")
                    print(f"      副本: {statefulset['ready_replicas']}/{statefulset['replicas']}")
                    print(f"      创建时间: {statefulset['created']}")
            else:
                print("  没有找到MySQL StatefulSet")
            
            # 列出服务
            services = self.list_services()
            if services:
                print("  服务:")
                for service in services:
                    print(f"    - {service['name']}/{service['namespace']}")
                    print(f"      类型: {service['type']}")
                    print(f"      集群IP: {service['cluster_ip']}")
                    if service['external_ip']:
                        print(f"      外部IP: {service['external_ip']}")
                    if service['ports']:
                        print(f"      端口: {', '.join([f\"{p['port']}->{p['target_port']}\" for p in service['ports']])}")
            else:
                print("  没有找到MySQL服务")
            
            # 3. 创建命名空间（仅演示）
            print("\n3. 创建命名空间（演示模式）:")
            namespace_name = f'mysql-demo-{int(time.time())}'
            print(f"  命名空间: {namespace_name}")
            
            # 取消注释下面这行可以实际创建命名空间
            # self.create_namespace(namespace_name)
            # print(f"  ✅ 命名空间创建成功: {namespace_name}")
            
            print("  [演示模式] 实际创建需要取消代码注释")
            
            # 4. 创建Secret（仅演示）
            print("\n4. 创建Secret（演示模式）:")
            secret_data = {
                'mysql-root-password': 'DemoRootPassword123!',
                'mysql-user-password': 'DemoUserPassword123!'
            }
            
            print("  Secret数据:")
            for key, value in secret_data.items():
                print(f"    {key}: {'*' * len(value)}")
            
            # 取消注释下面这行可以实际创建Secret
            # self.create_secret(namespace_name, 'mysql-secret', secret_data)
            # print(f"  ✅ Secret创建成功: mysql-secret")
            
            print("  [演示模式] 实际创建需要取消代码注释")
            
            # 5. 创建ConfigMap（仅演示）
            print("\n5. 创建ConfigMap（演示模式）:")
            config_data = {
                'my.cnf': '''
[mysqld]
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
max_connections=1000
innodb_buffer_pool_size=256M
slow_query_log=1
long_query_time=2
'''
            }
            
            print("  ConfigMap内容:")
            for key, value in config_data.items():
                print(f"    {key}:")
                for line in value.strip().split('\n')[:3]:  # 只显示前3行
                    print(f"      {line}")
                print("      ...")
            
            # 取消注释下面这行可以实际创建ConfigMap
            # self.create_configmap(namespace_name, 'mysql-config', config_data)
            # print(f"  ✅ ConfigMap创建成功: mysql-config")
            
            print("  [演示模式] 实际创建需要取消代码注释")
            
            # 6. 创建StatefulSet（仅演示）
            print("\n6. 创建StatefulSet（演示模式）:")
            statefulset_config = {
                'image': 'mysql:8.0',
                'replicas': 1,
                'storage_size': '20Gi',
                'database': 'demo_db',
                'user': 'demo_user',
                'password': 'DemoUserPassword123!',
                'configmap': 'mysql-config'
            }
            
            print("  StatefulSet配置:")
            for key, value in statefulset_config.items():
                if key == 'password':
                    print(f"    {key}: {'*' * len(str(value))}")
                else:
                    print(f"    {key}: {value}")
            
            # 取消注释下面这行可以实际创建StatefulSet
            # self.create_statefulset_mysql(namespace_name, 'mysql-demo', statefulset_config)
            # print(f"  ✅ StatefulSet创建成功: mysql-demo")
            
            print("  [演示模式] 实际创建需要取消代码注释")
            
            # 7. 创建服务（仅演示）
            print("\n7. 创建服务（演示模式）:")
            service_type = 'ClusterIP'  # 或 'LoadBalancer'
            print(f"  服务类型: {service_type}")
            
            # 取消注释下面这行可以实际创建服务
            # self.create_service_mysql(namespace_name, 'mysql-demo-service', service_type)
            # print(f"  ✅ 服务创建成功: mysql-demo-service")
            
            print("  [演示模式] 实际创建需要取消代码注释")
            
            # 8. YAML配置示例
            print("\n8. YAML配置示例:")
            yaml_example = '''
apiVersion: v1
kind: Namespace
metadata:
  name: mysql-demo

---
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: mysql-demo
type: Opaque
data:
  # echo -n 'DemoRootPassword123!' | base64
  mysql-root-password: RGVtb1Jvb3RQYXNzd29yZDEyMyE=
  # echo -n 'DemoUserPassword123!' | base64
  mysql-user-password: RGVtb1VzZXJQYXNzd29yZDEyMyE=

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: mysql-demo
data:
  my.cnf: |
    [mysqld]
    character-set-server=utf8mb4
    collation-server=utf8mb4_unicode_ci
    max_connections=1000
    innodb_buffer_pool_size=256M
    slow_query_log=1
    long_query_time=2

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-demo
  namespace: mysql-demo
spec:
  serviceName: mysql-demo
  replicas: 1
  selector:
    matchLabels:
      app: mysql-demo
  template:
    metadata:
      labels:
        app: mysql-demo
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        - name: MYSQL_DATABASE
          value: demo_db
        - name: MYSQL_USER
          value: demo_user
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-user-password
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
          readOnly: true
      volumes:
      - name: mysql-config
        configMap:
          name: mysql-config
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi

---
apiVersion: v1
kind: Service
metadata:
  name: mysql-demo-service
  namespace: mysql-demo
spec:
  selector:
    app: mysql-demo
  ports:
  - port: 3306
    targetPort: 3306
  type: ClusterIP
'''
            
            print("  完整的Kubernetes YAML配置:")
            print("  " + "\n  ".join(yaml_example.split('\n')[:20]))
            print("  ...")
            
            # 9. Helm Chart示例
            print("\n9. Helm Chart示例:")
            helm_example = '''
# 使用Helm部署MySQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 自定义values.yaml
cat > mysql-values.yaml << EOF
auth:
  rootPassword: "DemoRootPassword123!"
  database: "demo_db"
  username: "demo_user"
  password: "DemoUserPassword123!"

primary:
  persistence:
    enabled: true
    size: 20Gi
  configuration: |
    [mysqld]
    character-set-server=utf8mb4
    collation-server=utf8mb4_unicode_ci

service:
  type: ClusterIP
  port: 3306

metrics:
  enabled: true
EOF

# 部署MySQL
helm install mysql-demo bitnami/mysql \
  --namespace mysql-demo \
  --create-namespace \
  --values mysql-values.yaml

# 获取root密码
kubectl get secret --namespace mysql-demo mysql-demo \
  -o jsonpath="{.data.mysql-root-password}" | base64 -d

# 转发端口
kubectl port-forward --namespace mysql-demo svc/mysql-demo 3306:3306 &

# 连接MySQL
mysql -h 127.0.0.1 -P 3306 -u root -p
'''
            
            print("  Helm部署命令:")
            print("  " + "\n  ".join(helm_example.split('\n')[:30]))
            print("  ...")
            
            print("\n✅ Kubernetes MySQL演示完成")
            
        except Exception as e:
            logger.error(f"Kubernetes MySQL演示失败: {e}")

def get_default_config():
    """获取默认配置"""
    return {
        'aws': {
            'access_key_id': '',
            'secret_access_key': '',
            'region': 'us-east-1'
        },
        'aliyun': {
            'access_key_id': '',
            'access_key_secret': '',
            'region': 'cn-hangzhou'
        },
        'tencent': {
            'secret_id': '',
            'secret_key': '',
            'region': 'ap-guangzhou'
        },
        'docker': {
            'image': 'mysql:8.0',
            'data_dir': '/tmp/mysql_data'
        },
        'kubernetes': {
            'kubeconfig_path': None  # 默认路径
        }
    }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MySQL云服务与容器化演示')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--demo', 
                        choices=['aws_rds', 'aliyun_rds', 'docker_mysql', 'kubernetes_mysql', 'all'], 
                        default='all', 
                        help='选择要运行的演示')
    
    args = parser.parse_args()
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = get_default_config()
    
    try:
        # 运行演示
        if args.demo == 'aws_rds' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("AWS RDS MySQL演示")
            print("=" * 50)
            try:
                demo = AWSRDSManager(config.get('aws', {}))
                demo.demo_aws_rds()
            except Exception as e:
                print(f"AWS RDS演示跳过: {e}")
            
            if args.demo != 'all':
                return
        
        if args.demo == 'aliyun_rds' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("阿里云RDS MySQL演示")
            print("=" * 50)
            try:
                demo = AliyunRDSManager(config.get('aliyun', {}))
                demo.demo_aliyun_rds()
            except Exception as e:
                print(f"阿里云RDS演示跳过: {e}")
            
            if args.demo != 'all':
                return
        
        if args.demo == 'docker_mysql' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("Docker MySQL演示")
            print("=" * 50)
            try:
                demo = DockerMySQLManager(config.get('docker', {}))
                demo.demo_docker_mysql()
            except Exception as e:
                print(f"Docker MySQL演示跳过: {e}")
            
            if args.demo != 'all':
                return
        
        if args.demo == 'kubernetes_mysql' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("Kubernetes MySQL演示")
            print("=" * 50)
            try:
                demo = KubernetesMySQLManager(config.get('kubernetes', {}))
                demo.demo_kubernetes_mysql()
            except Exception as e:
                print(f"Kubernetes MySQL演示跳过: {e}")
            
            if args.demo != 'all':
                return
        
        print("\n" + "=" * 50)
        print("所有演示完成")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"运行演示失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()