#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ故障处理与恢复 - 代码示例
=====================================

本文件包含RabbitMQ故障处理与恢复的完整示例代码，涵盖：
- 故障检测机制
- 故障处理策略
- 数据备份与恢复
- 灾难恢复流程
- 性能故障诊断
- 故障预防策略

作者：RabbitMQ学习团队
版本：1.0.0
"""

import json
import time
import logging
import asyncio
import psutil
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pika
from pathlib import Path
import shutil


class FaultType(Enum):
    """故障类型枚举"""
    NODE_DOWN = "node_down"
    QUEUE_FULL = "queue_full"
    MEMORY_HIGH = "memory_high"
    DISK_LOW = "disk_low"
    CONNECTION_LOST = "connection_lost"
    MESSAGE_TIMEOUT = "message_timeout"
    CLUSTER_PARTITION = "cluster_partition"


class RecoveryStrategy(Enum):
    """恢复策略枚举"""
    IMMEDIATE_RESTART = "immediate_restart"
    GRACEFUL_RESTART = "graceful_restart"
    FAILOVER = "failover"
    DATA_RESTORE = "data_restore"
    CLUSTER_REBUILD = "cluster_rebuild"


@dataclass
class FaultInfo:
    """故障信息数据类"""
    fault_id: str
    fault_type: FaultType
    description: str
    node: str
    timestamp: datetime
    severity: str
    affected_queues: List[str]
    affected_connections: int
    metrics_snapshot: Dict[str, Any]


@dataclass
class BackupInfo:
    """备份信息数据类"""
    backup_id: str
    timestamp: datetime
    node: str
    backup_type: str
    file_path: str
    size_mb: float
    checksum: str
    metadata: Dict[str, Any]


@dataclass
class RecoveryConfig:
    """恢复配置数据类"""
    auto_recovery: bool
    max_recovery_attempts: int
    recovery_timeout: int
    backup_retention_days: int
    health_check_interval: int
    alert_thresholds: Dict[str, float]


class FaultDetector:
    """故障检测器"""
    
    def __init__(self, connection_params: pika.ConnectionParameters):
        self.connection_params = connection_params
        self.logger = logging.getLogger(__name__)
        self.last_health_status = {}
        
    async def detect_node_failures(self) -> List[FaultInfo]:
        """检测节点故障"""
        faults = []
        
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            # 检查集群状态
            cluster_status = await self._check_cluster_status(channel)
            
            for node in cluster_status.get('nodes', []):
                if not node.get('running', False):
                    fault = FaultInfo(
                        fault_id=self._generate_fault_id(),
                        fault_type=FaultType.NODE_DOWN,
                        description=f"节点 {node['name']} 已停止运行",
                        node=node['name'],
                        timestamp=datetime.now(),
                        severity="critical",
                        affected_queues=node.get('queues', []),
                        affected_connections=node.get('connection_count', 0),
                        metrics_snapshot=await self._collect_node_metrics(node['name'])
                    )
                    faults.append(fault)
                    
            connection.close()
            
        except Exception as e:
            self.logger.error(f"节点故障检测失败: {e}")
            
        return faults
    
    async def detect_resource_issues(self) -> List[FaultInfo]:
        """检测资源问题"""
        faults = []
        
        try:
            # 检查系统资源
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            if cpu_percent > 90:
                fault = FaultInfo(
                    fault_id=self._generate_fault_id(),
                    fault_type=FaultType.MEMORY_HIGH,
                    description=f"CPU使用率过高: {cpu_percent}%",
                    node="localhost",
                    timestamp=datetime.now(),
                    severity="warning",
                    affected_queues=[],
                    affected_connections=0,
                    metrics_snapshot={'cpu_percent': cpu_percent}
                )
                faults.append(fault)
                
            if memory.percent > 85:
                fault = FaultInfo(
                    fault_id=self._generate_fault_id(),
                    fault_type=FaultType.MEMORY_HIGH,
                    description=f"内存使用率过高: {memory.percent}%",
                    node="localhost",
                    timestamp=datetime.now(),
                    severity="critical",
                    affected_queues=[],
                    affected_connections=0,
                    metrics_snapshot={'memory_percent': memory.percent}
                )
                faults.append(fault)
                
            if disk.percent > 90:
                fault = FaultInfo(
                    fault_id=self._generate_fault_id(),
                    fault_type=FaultType.DISK_LOW,
                    description=f"磁盘使用率过高: {disk.percent}%",
                    node="localhost",
                    timestamp=datetime.now(),
                    severity="critical",
                    affected_queues=[],
                    affected_connections=0,
                    metrics_snapshot={'disk_percent': disk.percent}
                )
                faults.append(fault)
                
        except Exception as e:
            self.logger.error(f"资源问题检测失败: {e}")
            
        return faults
    
    async def detect_queue_issues(self) -> List[FaultInfo]:
        """检测队列问题"""
        faults = []
        
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            # 获取所有队列信息
            queues = channel.queue_declare(queue='', passive=True)
            queue_info = channel.queue_declare(queue='', passive=True)
            
            # 检查队列深度
            queue_depth = queue_info.method.message_count
            
            if queue_depth > 1000:  # 阈值可配置
                fault = FaultInfo(
                    fault_id=self._generate_fault_id(),
                    fault_type=FaultType.QUEUE_FULL,
                    description=f"队列过深: {queue_depth} 条消息",
                    node="localhost",
                    timestamp=datetime.now(),
                    severity="warning",
                    affected_queues=[''],
                    affected_connections=0,
                    metrics_snapshot={'queue_depth': queue_depth}
                )
                faults.append(fault)
                
            connection.close()
            
        except Exception as e:
            self.logger.error(f"队列问题检测失败: {e}")
            
        return faults
    
    async def _check_cluster_status(self, channel) -> Dict[str, Any]:
        """检查集群状态"""
        try:
            # 尝试获取集群状态
            result = channel.queue_declare(queue='cluster_status_check', passive=True)
            return {'nodes': [{'name': 'localhost', 'running': True, 'queues': [], 'connection_count': 0}]}
        except:
            return {'nodes': []}
    
    async def _collect_node_metrics(self, node: str) -> Dict[str, Any]:
        """收集节点指标"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    def _generate_fault_id(self) -> str:
        """生成故障ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]


class FaultRecoveryManager:
    """故障恢复管理器"""
    
    def __init__(self, connection_params: pika.ConnectionParameters, config: RecoveryConfig):
        self.connection_params = connection_params
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.recovery_attempts = {}
        
    async def handle_fault(self, fault: FaultInfo) -> bool:
        """处理故障"""
        self.logger.info(f"开始处理故障: {fault.fault_id} - {fault.description}")
        
        # 检查是否自动恢复
        if not self.config.auto_recovery:
            self.logger.info("自动恢复已禁用，等待手动处理")
            return False
        
        # 获取恢复策略
        strategy = self._determine_recovery_strategy(fault)
        
        # 执行恢复
        success = await self._execute_recovery_strategy(fault, strategy)
        
        if success:
            self.logger.info(f"故障恢复成功: {fault.fault_id}")
        else:
            self.logger.error(f"故障恢复失败: {fault.fault_id}")
            
        return success
    
    def _determine_recovery_strategy(self, fault: FaultInfo) -> RecoveryStrategy:
        """确定恢复策略"""
        if fault.fault_type == FaultType.NODE_DOWN:
            return RecoveryStrategy.FAILOVER
        elif fault.fault_type == FaultType.MEMORY_HIGH:
            return RecoveryStrategy.GRACEFUL_RESTART
        elif fault.fault_type == FaultType.DISK_LOW:
            return RecoveryStrategy.IMMEDIATE_RESTART
        elif fault.fault_type == FaultType.QUEUE_FULL:
            return RecoveryStrategy.DATA_RESTORE
        else:
            return RecoveryStrategy.IMMEDIATE_RESTART
    
    async def _execute_recovery_strategy(self, fault: FaultInfo, strategy: RecoveryStrategy) -> bool:
        """执行恢复策略"""
        try:
            if strategy == RecoveryStrategy.IMMEDIATE_RESTART:
                return await self._immediate_restart(fault)
            elif strategy == RecoveryStrategy.GRACEFUL_RESTART:
                return await self._graceful_restart(fault)
            elif strategy == RecoveryStrategy.FAILOVER:
                return await self._failover(fault)
            elif strategy == RecoveryStrategy.DATA_RESTORE:
                return await self._data_restore(fault)
            else:
                return False
        except Exception as e:
            self.logger.error(f"恢复策略执行失败: {e}")
            return False
    
    async def _immediate_restart(self, fault: FaultInfo) -> bool:
        """立即重启"""
        self.logger.info("执行立即重启...")
        
        # 模拟重启过程
        await asyncio.sleep(2)
        
        # 验证服务是否恢复
        return await self._verify_service_health(fault.node)
    
    async def _graceful_restart(self, fault: FaultInfo) -> bool:
        """优雅重启"""
        self.logger.info("执行优雅重启...")
        
        # 先尝试清理资源
        await self._cleanup_resources()
        
        # 等待连接正常关闭
        await asyncio.sleep(5)
        
        # 重新启动服务
        return await self._immediate_restart(fault)
    
    async def _failover(self, fault: FaultInfo) -> bool:
        """故障转移"""
        self.logger.info("执行故障转移...")
        
        # 检查备用节点
        backup_node = await self._find_backup_node()
        
        if backup_node:
            # 切换流量到备用节点
            await self._redirect_traffic(backup_node)
            return True
        
        return False
    
    async def _data_restore(self, fault: FaultInfo) -> bool:
        """数据恢复"""
        self.logger.info("执行数据恢复...")
        
        # 查找最新备份
        backup = await self._find_latest_backup(fault.node)
        
        if backup:
            return await self._restore_from_backup(backup)
        
        return False
    
    async def _verify_service_health(self, node: str) -> bool:
        """验证服务健康状态"""
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            # 尝试基本操作
            channel.queue_declare(queue='health_check', passive=True)
            
            connection.close()
            return True
        except:
            return False
    
    async def _cleanup_resources(self) -> None:
        """清理资源"""
        # 清理临时队列
        # 关闭空闲连接
        pass
    
    async def _find_backup_node(self) -> Optional[str]:
        """查找备用节点"""
        # 模拟查找备用节点
        return "backup-node-01"
    
    async def _redirect_traffic(self, backup_node: str) -> None:
        """重定向流量"""
        self.logger.info(f"将流量重定向到备用节点: {backup_node}")
    
    async def _find_latest_backup(self, node: str) -> Optional[BackupInfo]:
        """查找最新备份"""
        # 模拟查找备份
        return BackupInfo(
            backup_id="backup_001",
            timestamp=datetime.now() - timedelta(hours=1),
            node=node,
            backup_type="full",
            file_path="/backups/full_backup_001.tar.gz",
            size_mb=1024.0,
            checksum="abc123",
            metadata={}
        )
    
    async def _restore_from_backup(self, backup: BackupInfo) -> bool:
        """从备份恢复"""
        self.logger.info(f"从备份恢复: {backup.backup_id}")
        
        try:
            # 模拟恢复过程
            await asyncio.sleep(3)
            return True
        except Exception as e:
            self.logger.error(f"备份恢复失败: {e}")
            return False


class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_dir: str = "/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    async def create_backup(self, node: str, backup_type: str = "incremental") -> BackupInfo:
        """创建备份"""
        backup_id = self._generate_backup_id()
        timestamp = datetime.now()
        
        # 创建备份文件
        backup_file = self.backup_dir / f"{backup_type}_backup_{backup_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        try:
            # 模拟备份过程
            await self._perform_backup(backup_file)
            
            # 计算校验和
            checksum = await self._calculate_checksum(backup_file)
            
            # 获取文件大小
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=timestamp,
                node=node,
                backup_type=backup_type,
                file_path=str(backup_file),
                size_mb=size_mb,
                checksum=checksum,
                metadata={'created_by': 'fault_recovery_system'}
            )
            
            # 保存备份信息
            await self._save_backup_info(backup_info)
            
            self.logger.info(f"备份创建成功: {backup_id}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"备份创建失败: {e}")
            raise
    
    async def restore_backup(self, backup_info: BackupInfo) -> bool:
        """恢复备份"""
        try:
            backup_file = Path(backup_info.file_path)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_file}")
            
            # 验证校验和
            checksum = await self._calculate_checksum(backup_file)
            if checksum != backup_info.checksum:
                raise ValueError("备份文件校验和不匹配")
            
            # 执行恢复
            await self._perform_restore(backup_file, backup_info.node)
            
            self.logger.info(f"备份恢复成功: {backup_info.backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"备份恢复失败: {e}")
            return False
    
    async def list_backups(self, node: Optional[str] = None) -> List[BackupInfo]:
        """列出备份"""
        # 模拟返回备份列表
        return [
            BackupInfo(
                backup_id="backup_001",
                timestamp=datetime.now() - timedelta(hours=2),
                node=node or "localhost",
                backup_type="full",
                file_path="/backups/full_backup_001.tar.gz",
                size_mb=1024.0,
                checksum="abc123",
                metadata={}
            )
        ]
    
    async def cleanup_old_backups(self, retention_days: int = 7) -> int:
        """清理过期备份"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cleaned_count = 0
        
        backups = await self.list_backups()
        
        for backup in backups:
            if backup.timestamp < cutoff_date:
                backup_path = Path(backup.file_path)
                if backup_path.exists():
                    backup_path.unlink()
                    cleaned_count += 1
        
        self.logger.info(f"清理了 {cleaned_count} 个过期备份")
        return cleaned_count
    
    async def _perform_backup(self, backup_file: Path) -> None:
        """执行备份"""
        # 模拟备份过程
        await asyncio.sleep(2)
        
        # 创建模拟备份文件
        with open(backup_file, 'w') as f:
            f.write("模拟RabbitMQ数据备份内容")
    
    async def _perform_restore(self, backup_file: Path, node: str) -> None:
        """执行恢复"""
        # 模拟恢复过程
        await asyncio.sleep(3)
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def _save_backup_info(self, backup_info: BackupInfo) -> None:
        """保存备份信息"""
        info_file = self.backup_dir / "backup_info.json"
        
        # 模拟保存
        backup_data = asdict(backup_info)
        backup_data['timestamp'] = backup_info.timestamp.isoformat()
        
        # 实际实现中应该保存到文件或数据库
        pass
    
    def _generate_backup_id(self) -> str:
        """生成备份ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]


class DisasterRecoveryPlanner:
    """灾难恢复规划器"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.logger = logging.getLogger(__name__)
        self.recovery_plans = {}
    
    async def create_recovery_plan(self, disaster_type: str, plan_config: Dict[str, Any]) -> str:
        """创建恢复计划"""
        plan_id = hashlib.md5(f"{disaster_type}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        recovery_plan = {
            'plan_id': plan_id,
            'disaster_type': disaster_type,
            'created_at': datetime.now().isoformat(),
            'steps': plan_config.get('steps', []),
            'estimated_time': plan_config.get('estimated_time', 0),
            'required_resources': plan_config.get('required_resources', []),
            'backup_requirements': plan_config.get('backup_requirements', {}),
            'validation_steps': plan_config.get('validation_steps', [])
        }
        
        self.recovery_plans[plan_id] = recovery_plan
        self.logger.info(f"创建恢复计划: {plan_id}")
        
        return plan_id
    
    async def execute_recovery_plan(self, plan_id: str, disaster_context: Dict[str, Any]) -> bool:
        """执行恢复计划"""
        if plan_id not in self.recovery_plans:
            raise ValueError(f"恢复计划不存在: {plan_id}")
        
        plan = self.recovery_plans[plan_id]
        self.logger.info(f"开始执行恢复计划: {plan_id}")
        
        try:
            for step in plan['steps']:
                step_name = step.get('name')
                step_action = step.get('action')
                
                self.logger.info(f"执行步骤: {step_name}")
                
                # 根据动作类型执行相应操作
                if step_action == 'backup_check':
                    await self._validate_backup_requirements(step.get('requirements', {}))
                elif step_action == 'service_restart':
                    await self._restart_services(step.get('services', []))
                elif step_action == 'data_restore':
                    await self._restore_data(step.get('backup_id'))
                elif step_action == 'health_check':
                    result = await self._perform_health_checks(step.get('checks', []))
                    if not result:
                        raise Exception("健康检查失败")
                elif step_action == 'validation':
                    result = await self._run_validation_steps(step.get('validations', []))
                    if not result:
                        raise Exception("验证步骤失败")
                
                # 记录步骤完成
                self.logger.info(f"步骤完成: {step_name}")
            
            self.logger.info(f"恢复计划执行成功: {plan_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复计划执行失败: {e}")
            return False
    
    async def validate_recovery_plan(self, plan_id: str) -> Tuple[bool, List[str]]:
        """验证恢复计划"""
        if plan_id not in self.recovery_plans:
            return False, ["恢复计划不存在"]
        
        plan = self.recovery_plans[plan_id]
        issues = []
        
        # 检查计划完整性
        if not plan.get('steps'):
            issues.append("恢复计划缺少步骤")
        
        # 检查步骤顺序
        steps = plan.get('steps', [])
        for i, step in enumerate(steps):
            if not step.get('name'):
                issues.append(f"步骤 {i} 缺少名称")
            if not step.get('action'):
                issues.append(f"步骤 {i} 缺少动作")
        
        return len(issues) == 0, issues
    
    async def _validate_backup_requirements(self, requirements: Dict[str, Any]) -> None:
        """验证备份要求"""
        backup_type = requirements.get('type')
        age_limit = requirements.get('max_age_hours', 24)
        
        backups = await self.backup_manager.list_backups()
        recent_backups = [b for b in backups if 
                         (datetime.now() - b.timestamp).total_seconds() < age_limit * 3600]
        
        if not recent_backups:
            raise Exception(f"找不到满足要求的备份 (类型: {backup_type}, 年龄限制: {age_limit}小时)")
    
    async def _restart_services(self, services: List[str]) -> None:
        """重启服务"""
        for service in services:
            self.logger.info(f"重启服务: {service}")
            await asyncio.sleep(1)  # 模拟重启时间
    
    async def _restore_data(self, backup_id: str) -> None:
        """恢复数据"""
        backups = await self.backup_manager.list_backups()
        backup = next((b for b in backups if b.backup_id == backup_id), None)
        
        if not backup:
            raise Exception(f"备份不存在: {backup_id}")
        
        await self.backup_manager.restore_backup(backup)
    
    async def _perform_health_checks(self, checks: List[str]) -> bool:
        """执行健康检查"""
        for check in checks:
            # 模拟健康检查
            await asyncio.sleep(0.5)
        
        return True
    
    async def _run_validation_steps(self, validations: List[str]) -> bool:
        """运行验证步骤"""
        for validation in validations:
            # 模拟验证
            await asyncio.sleep(0.5)
        
        return True


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, connection_params: pika.ConnectionParameters):
        self.connection_params = connection_params
        self.logger = logging.getLogger(__name__)
        self.performance_history = []
    
    async def analyze_performance_issues(self) -> List[Dict[str, Any]]:
        """分析性能问题"""
        issues = []
        
        try:
            # 收集性能指标
            metrics = await self._collect_performance_metrics()
            
            # 分析吞吐量问题
            throughput_issues = self._analyze_throughput(metrics)
            issues.extend(throughput_issues)
            
            # 分析延迟问题
            latency_issues = self._analyze_latency(metrics)
            issues.extend(latency_issues)
            
            # 分析内存使用
            memory_issues = self._analyze_memory_usage(metrics)
            issues.extend(memory_issues)
            
            # 分析队列性能
            queue_issues = self._analyze_queue_performance(metrics)
            issues.extend(queue_issues)
            
        except Exception as e:
            self.logger.error(f"性能分析失败: {e}")
        
        return issues
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
                'rabbitmq_metrics': await self._get_rabbitmq_metrics(channel)
            }
            
            connection.close()
            return metrics
            
        except Exception as e:
            self.logger.error(f"指标收集失败: {e}")
            return {}
    
    async def _get_rabbitmq_metrics(self, channel) -> Dict[str, Any]:
        """获取RabbitMQ指标"""
        try:
            # 模拟RabbitMQ指标
            return {
                'queue_depth': 100,
                'message_rate': 50.0,
                'connection_count': 10,
                'channel_count': 25,
                'memory_usage_mb': 512
            }
        except Exception as e:
            self.logger.error(f"RabbitMQ指标获取失败: {e}")
            return {}
    
    def _analyze_throughput(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析吞吐量问题"""
        issues = []
        
        rabbitmq_metrics = metrics.get('rabbitmq_metrics', {})
        message_rate = rabbitmq_metrics.get('message_rate', 0)
        
        if message_rate < 10:  # 低于阈值
            issues.append({
                'type': 'low_throughput',
                'severity': 'warning',
                'description': f"消息处理速率过低: {message_rate} msg/s",
                'recommendation': "检查消费者处理能力和队列配置"
            })
        
        return issues
    
    def _analyze_latency(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析延迟问题"""
        issues = []
        
        # 模拟延迟分析
        simulated_latency = 100  # ms
        
        if simulated_latency > 50:  # 延迟过高
            issues.append({
                'type': 'high_latency',
                'severity': 'warning',
                'description': f"消息延迟过高: {simulated_latency}ms",
                'recommendation': "检查网络延迟和消费者处理能力"
            })
        
        return issues
    
    def _analyze_memory_usage(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析内存使用"""
        issues = []
        
        memory_percent = metrics.get('memory_percent', 0)
        
        if memory_percent > 80:
            issues.append({
                'type': 'high_memory_usage',
                'severity': 'critical',
                'description': f"系统内存使用率过高: {memory_percent}%",
                'recommendation': "考虑增加内存或优化应用程序内存使用"
            })
        
        rabbitmq_memory = metrics.get('rabbitmq_metrics', {}).get('memory_usage_mb', 0)
        if rabbitmq_memory > 1024:  # 1GB
            issues.append({
                'type': 'high_rabbitmq_memory',
                'severity': 'warning',
                'description': f"RabbitMQ内存使用过高: {rabbitmq_memory}MB",
                'recommendation': "检查队列深度和消息大小"
            })
        
        return issues
    
    def _analyze_queue_performance(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析队列性能"""
        issues = []
        
        rabbitmq_metrics = metrics.get('rabbitmq_metrics', {})
        queue_depth = rabbitmq_metrics.get('queue_depth', 0)
        
        if queue_depth > 1000:
            issues.append({
                'type': 'queue_overflow',
                'severity': 'critical',
                'description': f"队列深度过深: {queue_depth} 条消息",
                'recommendation': "增加消费者数量或检查消费者处理能力"
            })
        
        return issues


class FaultRecoverySystem:
    """故障恢复系统主类"""
    
    def __init__(self, connection_params: pika.ConnectionParameters):
        self.connection_params = connection_params
        self.config = RecoveryConfig(
            auto_recovery=True,
            max_recovery_attempts=3,
            recovery_timeout=300,
            backup_retention_days=7,
            health_check_interval=30,
            alert_thresholds={
                'cpu_percent': 80.0,
                'memory_percent': 85.0,
                'disk_percent': 90.0,
                'queue_depth': 1000
            }
        )
        
        # 初始化组件
        self.fault_detector = FaultDetector(connection_params)
        self.recovery_manager = FaultRecoveryManager(connection_params, self.config)
        self.backup_manager = BackupManager()
        self.dr_planner = DisasterRecoveryPlanner(self.backup_manager)
        self.performance_analyzer = PerformanceAnalyzer(connection_params)
        
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    async def start_monitoring(self):
        """启动监控"""
        self.is_running = self.config.auto_recovery
        self.logger.info("故障恢复系统启动")
        
        while self.is_running:
            try:
                # 检测故障
                faults = await self._detect_all_faults()
                
                for fault in faults:
                    self.logger.warning(f"检测到故障: {fault.description}")
                    
                    # 处理故障
                    success = await self.recovery_manager.handle_fault(fault)
                    
                    if not success:
                        self.logger.error(f"故障处理失败: {fault.fault_id}")
                
                # 分析性能问题
                await self._analyze_performance_periodically()
                
                # 等待下次检查
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"监控过程出错: {e}")
                await asyncio.sleep(5)
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        self.logger.info("故障恢复系统停止")
    
    async def _detect_all_faults(self) -> List[FaultInfo]:
        """检测所有故障"""
        all_faults = []
        
        # 检测节点故障
        node_faults = await self.fault_detector.detect_node_failures()
        all_faults.extend(node_faults)
        
        # 检测资源问题
        resource_faults = await self.fault_detector.detect_resource_issues()
        all_faults.extend(resource_faults)
        
        # 检测队列问题
        queue_faults = await self.fault_detector.detect_queue_issues()
        all_faults.extend(queue_faults)
        
        return all_faults
    
    async def _analyze_performance_periodically(self):
        """定期分析性能"""
        # 每10次健康检查进行一次性能分析
        if hasattr(self, '_check_count'):
            self._check_count += 1
        else:
            self._check_count = 1
        
        if self._check_count % 10 == 0:
            issues = await self.performance_analyzer.analyze_performance_issues()
            
            for issue in issues:
                self.logger.warning(f"性能问题: {issue['description']}")
                if issue.get('recommendation'):
                    self.logger.info(f"建议: {issue['recommendation']}")


async def main():
    """主函数 - 交互式演示"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # RabbitMQ连接参数
    connection_params = pika.ConnectionParameters('localhost')
    
    # 创建故障恢复系统
    fault_system = FaultRecoverySystem(connection_params)
    
    print("RabbitMQ故障处理与恢复系统")
    print("=" * 50)
    print("1. 启动自动监控")
    print("2. 手动创建备份")
    print("3. 列出备份")
    print("4. 执行恢复")
    print("5. 创建恢复计划")
    print("6. 性能分析")
    print("7. 退出")
    
    while True:
        try:
            choice = input("\n请选择操作 (1-7): ").strip()
            
            if choice == '1':
                print("启动自动故障监控...")
                await fault_system.start_monitoring()
                
            elif choice == '2':
                print("创建备份...")
                backup_info = await fault_system.backup_manager.create_backup("localhost", "full")
                print(f"备份创建成功: {backup_info.backup_id}")
                
            elif choice == '3':
                print("列出备份...")
                backups = await fault_system.backup_manager.list_backups()
                for backup in backups:
                    print(f"- {backup.backup_id}: {backup.timestamp} ({backup.size_mb:.1f}MB)")
                    
            elif choice == '4':
                print("执行数据恢复...")
                backups = await fault_system.backup_manager.list_backups()
                if backups:
                    success = await fault_system.backup_manager.restore_backup(backups[0])
                    print(f"恢复结果: {'成功' if success else '失败'}")
                else:
                    print("没有可用的备份")
                    
            elif choice == '5':
                print("创建灾难恢复计划...")
                plan_config = {
                    'steps': [
                        {'name': '验证备份', 'action': 'backup_check', 'requirements': {'type': 'full', 'max_age_hours': 24}},
                        {'name': '重启服务', 'action': 'service_restart', 'services': ['rabbitmq']},
                        {'name': '数据恢复', 'action': 'data_restore', 'backup_id': 'backup_001'},
                        {'name': '健康检查', 'action': 'health_check', 'checks': ['connection', 'queue']},
                        {'name': '验证恢复', 'action': 'validation', 'validations': ['message_flow']}
                    ],
                    'estimated_time': 1800,
                    'required_resources': ['backup_files', 'system_access'],
                    'backup_requirements': {'type': 'full', 'max_age_hours': 24}
                }
                
                plan_id = await fault_system.dr_planner.create_recovery_plan("complete_failure", plan_config)
                print(f"恢复计划创建成功: {plan_id}")
                
                # 执行计划
                success = await fault_system.dr_planner.execute_recovery_plan(plan_id, {})
                print(f"计划执行结果: {'成功' if success else '失败'}")
                
            elif choice == '6':
                print("执行性能分析...")
                issues = await fault_system.performance_analyzer.analyze_performance_issues()
                
                if issues:
                    print("发现以下性能问题:")
                    for issue in issues:
                        print(f"- [{issue['severity']}] {issue['description']}")
                        print(f"  建议: {issue['recommendation']}")
                else:
                    print("没有发现性能问题")
                    
            elif choice == '7':
                print("退出系统")
                fault_system.stop_monitoring()
                break
                
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n用户中断")
            fault_system.stop_monitoring()
            break
        except Exception as e:
            print(f"操作出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())