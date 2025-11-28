"""
自动故障转移与恢复管理模块
Chapter 10: 故障处理与恢复

提供自动故障检测、故障转移、恢复管理和故障恢复策略等功能
"""

import os
import sys
import time
import json
import threading
import queue
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil
import requests


class FailoverStrategy(Enum):
    """故障转移策略枚举"""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    LEAST_LOAD = "least_load"
    GEOGRAPHIC = "geographic"


class FailoverState(Enum):
    """故障转移状态枚举"""
    NORMAL = "normal"
    FAILOVER_IN_PROGRESS = "failover_in_progress"
    RECOVERY_IN_PROGRESS = "recovery_in_progress"
    DEGRADED = "degraded"
    EMERGENCY = "emergency"


class HealthLevel(Enum):
    """健康等级枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class ServiceEndpoint:
    """服务端点"""
    name: str
    host: str
    port: int
    api_port: int
    username: str
    password: str
    priority: int = 1
    weight: float = 1.0
    region: str = "default"
    is_primary: bool = False
    is_healthy: bool = True
    last_check: Optional[datetime] = None
    response_time: float = 0.0
    error_count: int = 0
    consecutive_failures: int = 0


@dataclass
class FailoverEvent:
    """故障转移事件"""
    event_type: str
    timestamp: datetime
    source_endpoint: str
    target_endpoint: str
    reason: str
    duration: float
    success: bool
    details: Dict[str, Any]


@dataclass
class FailoverConfiguration:
    """故障转移配置"""
    strategy: FailoverStrategy
    max_failover_time: int = 30  # 秒
    health_check_interval: int = 10  # 秒
    consecutive_failure_threshold: int = 3
    recovery_timeout: int = 300  # 5分钟
    enable_auto_recovery: bool = True
    enable_load_balancing: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def check_endpoint_health(self, endpoint: ServiceEndpoint) -> Tuple[bool, float, str]:
        """检查端点健康状态"""
        try:
            start_time = time.time()
            
            # 检查API连通性
            url = f"http://{endpoint.host}:{endpoint.api_port}/api/overview"
            auth = (endpoint.username, endpoint.password)
            
            response = requests.get(url, auth=auth, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                endpoint.last_check = datetime.now()
                endpoint.response_time = response_time
                endpoint.error_count = 0
                endpoint.is_healthy = True
                
                return True, response_time, "服务健康"
            else:
                endpoint.is_healthy = False
                endpoint.error_count += 1
                return False, response_time, f"API返回状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            endpoint.is_healthy = False
            endpoint.error_count += 1
            return False, self.timeout * 1000, "连接超时"
        except requests.exceptions.ConnectionError:
            endpoint.is_healthy = False
            endpoint.error_count += 1
            return False, 0, "连接错误"
        except Exception as e:
            endpoint.is_healthy = False
            endpoint.error_count += 1
            return False, 0, f"检查失败: {str(e)}"


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过熔断器调用函数"""
        current_time = time.time()
        
        # 检查是否应该尝试半开状态
        if self.state == "OPEN":
            if self.last_failure_time and current_time - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("熔断器开启，调用被拒绝")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        """成功时的处理"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
        self.failure_count = 0
    
    def on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def get_state(self) -> str:
        """获取当前状态"""
        return self.state


class FailoverManager:
    """故障转移管理器"""
    
    def __init__(self, config: FailoverConfiguration):
        self.config = config
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.health_checker = HealthChecker()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.current_state = FailoverState.NORMAL
        self.active_endpoint: Optional[ServiceEndpoint] = None
        self.failover_history: deque = deque(maxlen=1000)
        self.metrics = defaultdict(int)
        
        # 线程安全
        self.lock = threading.RLock()
        
        # 事件回调
        self.event_callbacks: List[Callable] = []
        
        # 初始化日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger("failover_manager")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def add_endpoint(self, endpoint: ServiceEndpoint):
        """添加服务端点"""
        with self.lock:
            self.endpoints[endpoint.name] = endpoint
            
            # 为每个端点创建熔断器
            if self.config.enable_circuit_breaker:
                self.circuit_breakers[endpoint.name] = CircuitBreaker(
                    failure_threshold=self.config.circuit_breaker_threshold,
                    timeout=self.config.circuit_breaker_timeout
                )
            
            self.logger.info(f"添加服务端点: {endpoint.name} ({endpoint.host}:{endpoint.port})")
            
            # 如果是主要端点，设置为活跃端点
            if endpoint.is_primary and not self.active_endpoint:
                self.active_endpoint = endpoint
                self.logger.info(f"设置主要端点为活跃端点: {endpoint.name}")
    
    def remove_endpoint(self, name: str):
        """移除服务端点"""
        with self.lock:
            if name in self.endpoints:
                endpoint = self.endpoints[name]
                
                # 如果移除的是当前活跃端点，需要故障转移
                if self.active_endpoint and self.active_endpoint.name == name:
                    self.logger.warning(f"移除当前活跃端点: {name}")
                    self._initiate_failover()
                
                del self.endpoints[name]
                
                # 移除熔断器
                if name in self.circuit_breakers:
                    del self.circuit_breakers[name]
                
                self.logger.info(f"移除服务端点: {name}")
    
    def _initiate_failover(self):
        """启动故障转移"""
        if self.current_state == FailoverState.FAILOVER_IN_PROGRESS:
            self.logger.warning("故障转移已在进行中")
            return
        
        self.logger.info("启动故障转移流程")
        
        failover_start_time = time.time()
        self.current_state = FailoverState.FAILOVER_IN_PROGRESS
        
        # 触发事件回调
        self._trigger_event_callbacks('failover_started', {
            'current_endpoint': self.active_endpoint.name if self.active_endpoint else None,
            'available_endpoints': [ep.name for ep in self.endpoints.values() if ep.is_healthy]
        })
        
        try:
            # 选择新的活跃端点
            new_endpoint = self._select_failover_target()
            
            if new_endpoint:
                success = self._perform_failover(new_endpoint)
                
                # 记录故障转移事件
                event = FailoverEvent(
                    event_type="failover",
                    timestamp=datetime.now(),
                    source_endpoint=self.active_endpoint.name if self.active_endpoint else "none",
                    target_endpoint=new_endpoint.name,
                    reason="主动故障转移",
                    duration=time.time() - failover_start_time,
                    success=success,
                    details={}
                )
                
                self.failover_history.append(event)
                
                if success:
                    self.current_state = FailoverState.NORMAL
                    self.logger.info(f"故障转移成功: {new_endpoint.name}")
                else:
                    self.current_state = FailoverState.EMERGENCY
                    self.logger.error(f"故障转移失败: {new_endpoint.name}")
            else:
                self.current_state = FailoverState.EMERGENCY
                self.logger.error("没有可用的故障转移目标端点")
                
        except Exception as e:
            self.current_state = FailoverState.EMERGENCY
            self.logger.error(f"故障转移过程异常: {e}")
        
        # 触发事件回调
        self._trigger_event_callbacks('failover_completed', {
            'success': self.current_state == FailoverState.NORMAL,
            'new_endpoint': self.active_endpoint.name if self.active_endpoint else None
        })
    
    def _select_failover_target(self) -> Optional[ServiceEndpoint]:
        """选择故障转移目标"""
        healthy_endpoints = [
            ep for ep in self.endpoints.values() 
            if ep.is_healthy and ep.name != (self.active_endpoint.name if self.active_endpoint else None)
        ]
        
        if not healthy_endpoints:
            return None
        
        # 根据策略选择目标
        if self.config.strategy == FailoverStrategy.PRIORITY_BASED:
            # 基于优先级
            return max(healthy_endpoints, key=lambda ep: ep.priority)
        elif self.config.strategy == FailoverStrategy.LEAST_LOAD:
            # 基于响应时间和错误率
            def load_score(ep):
                response_factor = ep.response_time / 1000 if ep.response_time > 0 else 1
                error_factor = (ep.consecutive_failures + 1) / 10
                return response_factor + error_factor
            
            return min(healthy_endpoints, key=load_score)
        elif self.config.strategy == FailoverStrategy.GEOGRAPHIC:
            # 地理分布（简单实现）
            current_region = self.active_endpoint.region if self.active_endpoint else "default"
            regional_endpoints = [ep for ep in healthy_endpoints if ep.region == current_region]
            if regional_endpoints:
                return max(regional_endpoints, key=lambda ep: ep.priority)
            else:
                return max(healthy_endpoints, key=lambda ep: ep.priority)
        else:
            # 轮询
            if self.active_endpoint:
                current_index = list(self.endpoints.keys()).index(self.active_endpoint.name)
                next_index = (current_index + 1) % len(self.endpoints)
                for i in range(len(self.endpoints)):
                    candidate_name = list(self.endpoints.keys())[(current_index + i + 1) % len(self.endpoints)]
                    candidate = self.endpoints[candidate_name]
                    if candidate in healthy_endpoints:
                        return candidate
            
            return healthy_endpoints[0]
    
    def _perform_failover(self, target_endpoint: ServiceEndpoint) -> bool:
        """执行故障转移"""
        try:
            # 验证目标端点健康状态
            is_healthy, response_time, message = self.health_checker.check_endpoint_health(target_endpoint)
            
            if not is_healthy:
                self.logger.warning(f"目标端点健康检查失败: {target_endpoint.name} - {message}")
                return False
            
            # 执行故障转移操作
            self.logger.info(f"执行故障转移到: {target_endpoint.name}")
            
            # 这里可以执行具体的故障转移逻辑，比如：
            # 1. 更新配置文件
            # 2. 重启服务
            # 3. 更新DNS记录
            # 4. 通知负载均衡器
            
            # 模拟故障转移过程
            time.sleep(2)
            
            # 更新活跃端点
            old_endpoint = self.active_endpoint
            self.active_endpoint = target_endpoint
            
            self.logger.info(f"故障转移完成: {old_endpoint.name if old_endpoint else 'none'} -> {target_endpoint.name}")
            
            # 重置目标端点的错误计数
            target_endpoint.consecutive_failures = 0
            target_endpoint.error_count = 0
            
            return True
            
        except Exception as e:
            self.logger.error(f"故障转移执行失败: {e}")
            return False
    
    def check_health_and_manage_failover(self):
        """检查健康状态并管理故障转移"""
        with self.lock:
            failed_endpoints = []
            
            # 检查所有端点健康状态
            for name, endpoint in self.endpoints.items():
                try:
                    is_healthy, response_time, message = self.health_checker.check_endpoint_health(endpoint)
                    
                    if not is_healthy:
                        endpoint.consecutive_failures += 1
                        
                        self.logger.warning(f"端点健康检查失败: {name} - {message} (连续失败: {endpoint.consecutive_failures})")
                        
                        # 检查是否需要故障转移
                        if (endpoint.consecutive_failures >= self.config.consecutive_failure_threshold or
                            endpoint.name == (self.active_endpoint.name if self.active_endpoint else None)):
                            failed_endpoints.append(endpoint)
                    else:
                        endpoint.consecutive_failures = 0
                        
                except Exception as e:
                    self.logger.error(f"健康检查异常: {name} - {e}")
                    failed_endpoints.append(endpoint)
            
            # 处理失败的端点
            if failed_endpoints:
                self._handle_failed_endpoints(failed_endpoints)
    
    def _handle_failed_endpoints(self, failed_endpoints: List[ServiceEndpoint]):
        """处理失败的端点"""
        for endpoint in failed_endpoints:
            if endpoint.name == (self.active_endpoint.name if self.active_endpoint else None):
                # 当前活跃端点失败，启动故障转移
                self.logger.warning(f"活跃端点失败，启动故障转移: {endpoint.name}")
                self._initiate_failover()
            else:
                # 非活跃端点失败，记录日志
                self.logger.warning(f"备用端点失败: {endpoint.name}")
    
    def start_monitoring(self):
        """启动健康监控"""
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("故障转移监控已启动")
    
    def stop_monitoring(self):
        """停止健康监控"""
        self.monitoring_thread = None
        self.logger.info("故障转移监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while threading.current_thread() == self.monitoring_thread:
            try:
                self.check_health_and_manage_failover()
                time.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
                time.sleep(5)
    
    def get_failover_status(self) -> Dict[str, Any]:
        """获取故障转移状态"""
        with self.lock:
            healthy_count = sum(1 for ep in self.endpoints.values() if ep.is_healthy)
            total_count = len(self.endpoints)
            
            return {
                'current_state': self.current_state.value,
                'active_endpoint': self.active_endpoint.name if self.active_endpoint else None,
                'total_endpoints': total_count,
                'healthy_endpoints': healthy_count,
                'unhealthy_endpoints': total_count - healthy_count,
                'endpoints': [
                    {
                        'name': ep.name,
                        'host': ep.host,
                        'port': ep.port,
                        'is_healthy': ep.is_healthy,
                        'is_primary': ep.is_primary,
                        'priority': ep.priority,
                        'response_time': ep.response_time,
                        'consecutive_failures': ep.consecutive_failures,
                        'last_check': ep.last_check.isoformat() if ep.last_check else None
                    }
                    for ep in self.endpoints.values()
                ],
                'recent_events': [
                    asdict(event) for event in list(self.failover_history)[-10:]
                ],
                'metrics': dict(self.metrics)
            }
    
    def add_event_callback(self, callback: Callable):
        """添加事件回调"""
        self.event_callbacks.append(callback)
    
    def _trigger_event_callbacks(self, event_type: str, data: Dict[str, Any]):
        """触发事件回调"""
        for callback in self.event_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(f"事件回调执行失败: {e}")
    
    def manual_failover(self, target_name: str) -> bool:
        """手动故障转移"""
        with self.lock:
            if target_name not in self.endpoints:
                self.logger.error(f"目标端点不存在: {target_name}")
                return False
            
            target_endpoint = self.endpoints[target_name]
            
            if not target_endpoint.is_healthy:
                self.logger.error(f"目标端点不健康: {target_name}")
                return False
            
            self.logger.info(f"执行手动故障转移: {target_name}")
            return self._perform_failover(target_endpoint)


class BackupManager:
    """备份管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_dir = config.get('backup_dir', './backups')
        self.retention_days = config.get('retention_days', 30)
        self.auto_backup_interval = config.get('auto_backup_interval', 3600)  # 1小时
        self.backup_metadata = []
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 线程安全
        self.lock = threading.RLock()
    
    def create_backup(self, backup_type: str = 'full') -> Dict[str, Any]:
        """创建备份"""
        backup_id = f"{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, backup_id)
        
        backup_info = {
            'backup_id': backup_id,
            'backup_type': backup_type,
            'created_at': datetime.now().isoformat(),
            'backup_path': backup_path,
            'files': [],
            'size_bytes': 0,
            'status': 'in_progress'
        }
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            if backup_type == 'full':
                self._backup_configuration(backup_path)
                self._backup_data_directories(backup_path)
                self._backup_logs(backup_path)
            elif backup_type == 'configuration':
                self._backup_configuration(backup_path)
            elif backup_type == 'data':
                self._backup_data_directories(backup_path)
            elif backup_type == 'logs':
                self._backup_logs(backup_path)
            
            # 计算备份大小
            backup_info['size_bytes'] = self._calculate_backup_size(backup_path)
            backup_info['status'] = 'completed'
            
            # 保存备份元数据
            self.backup_metadata.append(backup_info)
            self._save_backup_metadata()
            
            self._cleanup_old_backups()
            
            return backup_info
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            self.backup_metadata.append(backup_info)
            return backup_info
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """恢复备份"""
        backup_info = self._find_backup_by_id(backup_id)
        
        if not backup_info:
            return {'success': False, 'error': f'备份不存在: {backup_id}'}
        
        if backup_info['status'] != 'completed':
            return {'success': False, 'error': f'备份状态异常: {backup_info["status"]}'}
        
        try:
            backup_path = backup_info['backup_path']
            
            if backup_info['backup_type'] in ['full', 'configuration']:
                self._restore_configuration(backup_path)
            
            if backup_info['backup_type'] in ['full', 'data']:
                self._restore_data_directories(backup_path)
            
            if backup_info['backup_type'] in ['full', 'logs']:
                self._restore_logs(backup_path)
            
            return {'success': True, 'message': '备份恢复成功'}
            
        except Exception as e:
            return {'success': False, 'error': f'备份恢复失败: {str(e)}'}
    
    def _backup_configuration(self, backup_path: str):
        """备份配置文件"""
        config_dirs = ['/etc/rabbitmq', './config', './rabbitmq.conf']
        
        for config_dir in config_dirs:
            if os.path.exists(config_dir):
                import shutil
                if os.path.isdir(config_dir):
                    dest = os.path.join(backup_path, os.path.basename(config_dir))
                    shutil.copytree(config_dir, dest)
                else:
                    dest = os.path.join(backup_path, os.path.basename(config_dir))
                    shutil.copy2(config_dir, dest)
    
    def _backup_data_directories(self, backup_path: str):
        """备份数据目录"""
        data_dirs = ['/var/lib/rabbitmq/mnesia', './data', './mnesia']
        
        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                import shutil
                dest = os.path.join(backup_path, os.path.basename(data_dir))
                shutil.copytree(data_dir, dest, ignore=shutil.ignore_patterns('*.tmp', '*.log'))
    
    def _backup_logs(self, backup_path: str):
        """备份日志文件"""
        log_dirs = ['/var/log/rabbitmq', './logs']
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                import shutil
                dest = os.path.join(backup_path, os.path.basename(log_dir))
                shutil.copytree(log_dir, dest)
    
    def _restore_configuration(self, backup_path: str):
        """恢复配置文件"""
        # 实现配置恢复逻辑
        pass
    
    def _restore_data_directories(self, backup_path: str):
        """恢复数据目录"""
        # 实现数据恢复逻辑
        pass
    
    def _restore_logs(self, backup_path: str):
        """恢复日志文件"""
        # 实现日志恢复逻辑
        pass
    
    def _calculate_backup_size(self, backup_path: str) -> int:
        """计算备份大小"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(backup_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    def _save_backup_metadata(self):
        """保存备份元数据"""
        metadata_file = os.path.join(self.backup_dir, 'backup_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.backup_metadata, f, indent=2, ensure_ascii=False)
    
    def _find_backup_by_id(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """根据ID查找备份"""
        for backup_info in self.backup_metadata:
            if backup_info['backup_id'] == backup_id:
                return backup_info
        return None
    
    def _cleanup_old_backups(self):
        """清理过期备份"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        remaining_backups = []
        for backup_info in self.backup_metadata:
            backup_date = datetime.fromisoformat(backup_info['created_at'])
            if backup_date > cutoff_date:
                remaining_backups.append(backup_info)
            else:
                # 删除过期备份文件和目录
                import shutil
                if os.path.exists(backup_info['backup_path']):
                    shutil.rmtree(backup_info['backup_path'])
        
        self.backup_metadata = remaining_backups
        self._save_backup_metadata()


class DisasterRecoveryOrchestrator:
    """灾难恢复编排器"""
    
    def __init__(self, failover_config: FailoverConfiguration, backup_config: Dict[str, Any]):
        self.failover_manager = FailoverManager(failover_config)
        self.backup_manager = BackupManager(backup_config)
        
        # 恢复策略
        self.recovery_strategies = {
            'auto_failover': self._auto_failover_strategy,
            'backup_restore': self._backup_restore_strategy,
            'partial_recovery': self._partial_recovery_strategy
        }
        
        # 恢复计划
        self.recovery_plans = {}
    
    def add_recovery_plan(self, plan_name: str, plan_steps: List[Dict[str, Any]]):
        """添加恢复计划"""
        self.recovery_plans[plan_name] = {
            'name': plan_name,
            'steps': plan_steps,
            'created_at': datetime.now().isoformat(),
            'executed_steps': [],
            'status': 'pending'
        }
    
    def execute_recovery_plan(self, plan_name: str, trigger_reason: str = "") -> Dict[str, Any]:
        """执行恢复计划"""
        if plan_name not in self.recovery_plans:
            return {'success': False, 'error': f'恢复计划不存在: {plan_name}'}
        
        plan = self.recovery_plans[plan_name]
        plan['status'] = 'in_progress'
        plan['executed_at'] = datetime.now().isoformat()
        plan['trigger_reason'] = trigger_reason
        
        execution_results = []
        
        try:
            for step in plan['steps']:
                step_name = step.get('name', 'unknown')
                step_type = step.get('type', 'unknown')
                
                self.failover_manager.logger.info(f"执行恢复步骤: {step_name}")
                
                if step_type in self.recovery_strategies:
                    result = self.recovery_strategies[step_type](step)
                    execution_results.append({
                        'step_name': step_name,
                        'step_type': step_type,
                        'success': result.get('success', False),
                        'result': result,
                        'executed_at': datetime.now().isoformat()
                    })
                else:
                    execution_results.append({
                        'step_name': step_name,
                        'step_type': step_type,
                        'success': False,
                        'error': f'未知步骤类型: {step_type}',
                        'executed_at': datetime.now().isoformat()
                    })
            
            plan['executed_steps'] = execution_results
            plan['status'] = 'completed'
            
            # 检查是否所有步骤都成功
            all_success = all(step['success'] for step in execution_results)
            
            return {
                'success': all_success,
                'plan_name': plan_name,
                'execution_results': execution_results,
                'completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            plan['status'] = 'failed'
            plan['error'] = str(e)
            
            return {
                'success': False,
                'plan_name': plan_name,
                'error': str(e),
                'executed_steps': execution_results,
                'failed_at': datetime.now().isoformat()
            }
    
    def _auto_failover_strategy(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """自动故障转移策略"""
        try:
            self.failover_manager.check_health_and_manage_failover()
            return {'success': True, 'message': '自动故障转移执行完成'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _backup_restore_strategy(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """备份恢复策略"""
        try:
            backup_id = step_config.get('backup_id')
            if not backup_id:
                return {'success': False, 'error': '未指定备份ID'}
            
            result = self.backup_manager.restore_backup(backup_id)
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _partial_recovery_strategy(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """部分恢复策略"""
        try:
            # 部分恢复逻辑，比如只恢复特定服务或功能
            recovery_type = step_config.get('recovery_type', 'basic')
            
            if recovery_type == 'basic_services':
                # 恢复基础服务
                return {'success': True, 'message': '基础服务恢复完成'}
            elif recovery_type == 'critical_queues':
                # 恢复关键队列
                return {'success': True, 'message': '关键队列恢复完成'}
            else:
                return {'success': False, 'error': f'未知的部分恢复类型: {recovery_type}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class FailoverDemo:
    """故障转移演示"""
    
    def __init__(self):
        # 故障转移配置
        failover_config = FailoverConfiguration(
            strategy=FailoverStrategy.PRIORITY_BASED,
            max_failover_time=30,
            health_check_interval=5,
            consecutive_failure_threshold=2,
            enable_auto_recovery=True,
            enable_circuit_breaker=True
        )
        
        # 备份配置
        backup_config = {
            'backup_dir': './failover_backups',
            'retention_days': 7,
            'auto_backup_interval': 300
        }
        
        # 创建故障转移管理器
        self.failover_manager = FailoverManager(failover_config)
        self.backup_manager = BackupManager(backup_config)
        self.orchestrator = DisasterRecoveryOrchestrator(failover_config, backup_config)
        
        # 添加事件回调
        self.failover_manager.add_event_callback(self._failover_event_callback)
    
    def _failover_event_callback(self, event_type: str, data: Dict[str, Any]):
        """故障转移事件回调"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] 故障转移事件: {event_type}")
        print(f"  数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("-" * 50)
    
    def demo_endpoint_management(self):
        """演示端点管理"""
        print("=" * 60)
        print("服务端点管理演示")
        print("=" * 60)
        
        # 添加服务端点
        endpoints = [
            ServiceEndpoint(
                name="primary",
                host="rabbitmq-primary.example.com",
                port=5672,
                api_port=15672,
                username="admin",
                password="admin123",
                priority=10,
                is_primary=True
            ),
            ServiceEndpoint(
                name="secondary",
                host="rabbitmq-secondary.example.com",
                port=5672,
                api_port=15672,
                username="admin",
                password="admin123",
                priority=5
            ),
            ServiceEndpoint(
                name="tertiary",
                host="rabbitmq-tertiary.example.com",
                port=5672,
                api_port=15672,
                username="admin",
                password="admin123",
                priority=1
            )
        ]
        
        for endpoint in endpoints:
            self.failover_manager.add_endpoint(endpoint)
            print(f"添加端点: {endpoint.name} ({endpoint.host}:{endpoint.port})")
        
        # 显示当前状态
        status = self.failover_manager.get_failover_status()
        print(f"\n当前状态: {status['current_state']}")
        print(f"活跃端点: {status['active_endpoint']}")
        print(f"健康端点数: {status['healthy_endpoints']}/{status['total_endpoints']}")
        
        return status
    
    def demo_health_monitoring(self):
        """演示健康监控"""
        print("\n" + "=" * 60)
        print("健康监控演示")
        print("=" * 60)
        
        # 启动监控
        self.failover_manager.start_monitoring()
        
        try:
            print("开始健康监控，运行30秒...")
            time.sleep(30)
        except KeyboardInterrupt:
            print("监控被中断")
        finally:
            self.failover_manager.stop_monitoring()
        
        # 显示状态
        status = self.failover_manager.get_failover_status()
        print(f"\n监控结束 - 当前状态: {status['current_state']}")
        print(f"端点状态:")
        for endpoint in status['endpoints']:
            print(f"  {endpoint['name']}: {'健康' if endpoint['is_healthy'] else '不健康'} "
                  f"(响应时间: {endpoint['response_time']:.2f}ms)")
        
        return status
    
    def demo_failover_simulation(self):
        """演示故障转移模拟"""
        print("\n" + "=" * 60)
        print("故障转移模拟演示")
        print("=" * 60)
        
        # 手动故障转移
        print("执行手动故障转移到 secondary...")
        success = self.failover_manager.manual_failover("secondary")
        
        if success:
            print("手动故障转移成功")
        else:
            print("手动故障转移失败")
        
        # 显示状态变化
        status = self.failover_manager.get_failover_status()
        print(f"新状态: {status['current_state']}")
        print(f"新活跃端点: {status['active_endpoint']}")
        
        # 显示最近事件
        if status['recent_events']:
            print("最近故障转移事件:")
            for event in status['recent_events'][-3:]:
                print(f"  {event['event_type']}: {event['source_endpoint']} -> "
                      f"{event['target_endpoint']} ({'成功' if event['success'] else '失败'})")
        
        return status
    
    def demo_backup_operations(self):
        """演示备份操作"""
        print("\n" + "=" * 60)
        print("备份操作演示")
        print("=" * 60)
        
        # 创建备份
        print("创建完整备份...")
        backup_info = self.backup_manager.create_backup('full')
        
        if backup_info['status'] == 'completed':
            print(f"备份创建成功: {backup_info['backup_id']}")
            print(f"备份大小: {backup_info['size_bytes'] / 1024:.2f} KB")
        else:
            print(f"备份创建失败: {backup_info.get('error', '未知错误')}")
        
        # 显示备份列表
        print(f"\n当前备份列表:")
        for backup in self.backup_manager.backup_metadata[-3:]:  # 最近3个
            print(f"  {backup['backup_id']}: {backup['backup_type']} "
                  f"({backup['status']}) - {backup['created_at']}")
        
        return backup_info
    
    def demo_disaster_recovery(self):
        """演示灾难恢复"""
        print("\n" + "=" * 60)
        print("灾难恢复演示")
        print("=" * 60)
        
        # 创建恢复计划
        recovery_plan = [
            {
                'name': '自动故障转移',
                'type': 'auto_failover',
                'timeout': 30
            },
            {
                'name': '备份恢复',
                'type': 'backup_restore',
                'backup_id': 'full_latest',
                'timeout': 300
            },
            {
                'name': '服务恢复验证',
                'type': 'partial_recovery',
                'recovery_type': 'basic_services',
                'timeout': 60
            }
        ]
        
        self.orchestrator.add_recovery_plan('full_recovery', recovery_plan)
        print("创建灾难恢复计划: full_recovery")
        
        # 执行恢复计划
        print("执行灾难恢复计划...")
        result = self.orchestrator.execute_recovery_plan(
            'full_recovery', 
            trigger_reason='演示灾难恢复'
        )
        
        print(f"恢复计划执行结果: {'成功' if result['success'] else '失败'}")
        
        if result['success']:
            print("恢复步骤执行详情:")
            for step_result in result['execution_results']:
                status = "成功" if step_result['success'] else "失败"
                print(f"  {step_result['step_name']}: {status}")
        else:
            print(f"恢复失败: {result.get('error', '未知错误')}")
        
        return result
    
    def run_comprehensive_demo(self):
        """运行综合演示"""
        print("RabbitMQ 故障转移与恢复系统综合演示")
        print("=" * 80)
        
        try:
            # 1. 端点管理
            self.demo_endpoint_management()
            
            # 2. 健康监控
            self.demo_health_monitoring()
            
            # 3. 故障转移模拟
            self.demo_failover_simulation()
            
            # 4. 备份操作
            self.demo_backup_operations()
            
            # 5. 灾难恢复
            self.demo_disaster_recovery()
            
            print("\n" + "=" * 80)
            print("演示完成")
            print("=" * 80)
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
        except Exception as e:
            print(f"\n演示执行出错: {e}")


def main():
    """主函数"""
    demo = FailoverDemo()
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main()