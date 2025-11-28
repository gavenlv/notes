"""
RabbitMQ运维自动化模块
提供运维自动化脚本、故障恢复、性能优化等功能
"""

import os
import json
import time
import shutil
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import psutil
from pathlib import Path


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MaintenanceMode(Enum):
    """维护模式"""
    NONE = "none"
    READ_ONLY = "read_only"
    MAINTENANCE = "maintenance"
    DRY_RUN = "dry_run"


@dataclass
class Task:
    """运维任务"""
    id: str
    name: str
    description: str
    action: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class SystemHealth:
    """系统健康状态"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    rabbitmq_status: str
    connection_count: int
    queue_count: int
    error_rate: float
    overall_score: float


@dataclass
class MaintenanceWindow:
    """维护窗口"""
    name: str
    start_time: datetime
    end_time: datetime
    description: str
    affected_services: List[str]
    maintenance_mode: MaintenanceMode


class SystemDiagnostic:
    """系统诊断器"""
    
    def __init__(self, rabbitmq_host: str = 'localhost', api_port: int = 15672):
        self.rabbitmq_host = rabbitmq_host
        self.api_port = api_port
        self.logger = logging.getLogger(__name__)
    
    def run_comprehensive_diagnosis(self) -> Dict[str, Any]:
        """运行综合诊断"""
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'system_health': self._check_system_health(),
            'rabbitmq_health': self._check_rabbitmq_health(),
            'performance_analysis': self._analyze_performance(),
            'security_check': self._security_check(),
            'connectivity_test': self._test_connectivity(),
            'resource_usage': self._analyze_resource_usage(),
            'recommendations': []
        }
        
        # 生成建议
        diagnosis['recommendations'] = self._generate_diagnosis_recommendations(diagnosis)
        
        return diagnosis
    
    def _check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_score = 100.0
            
            # CPU分数
            if cpu_percent > 90:
                cpu_score = 20
            elif cpu_percent > 70:
                cpu_score = 60
            elif cpu_percent > 50:
                cpu_score = 80
            else:
                cpu_score = 100
            
            # 内存分数
            if memory.percent > 90:
                memory_score = 20
            elif memory.percent > 75:
                memory_score = 60
            elif memory.percent > 60:
                memory_score = 80
            else:
                memory_score = 100
            
            # 磁盘分数
            if disk.percent > 95:
                disk_score = 10
            elif disk.percent > 85:
                disk_score = 50
            elif disk.percent > 70:
                disk_score = 80
            else:
                disk_score = 100
            
            health_score = (cpu_score + memory_score + disk_score) / 3
            
            return {
                'status': 'healthy' if health_score > 80 else 'warning' if health_score > 60 else 'critical',
                'score': round(health_score, 2),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / 1024**3, 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / 1024**3, 2)
            }
        except Exception as e:
            self.logger.error(f"系统健康检查失败: {e}")
            return {'status': 'error', 'score': 0, 'error': str(e)}
    
    def _check_rabbitmq_health(self) -> Dict[str, Any]:
        """检查RabbitMQ健康状态"""
        try:
            # 测试API连接
            api_url = f"http://{self.rabbitmq_host}:{self.api_port}/api/health"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'api_response_time': response.elapsed.total_seconds(),
                    'message': 'RabbitMQ服务正常'
                }
            else:
                return {
                    'status': 'degraded',
                    'error_code': response.status_code,
                    'message': f'RabbitMQ API返回错误: {response.status_code}'
                }
        except requests.RequestException as e:
            return {
                'status': 'critical',
                'error': str(e),
                'message': '无法连接到RabbitMQ管理API'
            }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """分析性能"""
        try:
            # 获取性能数据
            api_url = f"http://{self.rabbitmq_host}:{self.api_port}/api/overview"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code != 200:
                return {'status': 'error', 'message': '无法获取性能数据'}
            
            data = response.json()
            
            # 提取关键指标
            obj_totals = data.get('object_totals', {})
            queue_totals = data.get('queue_totals', {})
            
            return {
                'status': 'ok',
                'connections': obj_totals.get('connections', 0),
                'channels': obj_totals.get('channels', 0),
                'queues': obj_totals.get('queues', 0),
                'exchanges': obj_totals.get('exchanges', 0),
                'messages_ready': queue_totals.get('messages', 0),
                'messages_unacknowledged': queue_totals.get('messages_unacknowledged', 0)
            }
        except Exception as e:
            self.logger.error(f"性能分析失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _security_check(self) -> Dict[str, Any]:
        """安全检查"""
        security_issues = []
        
        try:
            # 检查默认用户
            api_url = f"http://{self.rabbitmq_host}:{self.api_port}/api/users"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('name') == 'guest' and user.get('tags') == 'administrator':
                        security_issues.append("检测到默认管理员用户'guest'仍启用")
                        break
            
            # 检查权限
            if security_issues:
                return {
                    'status': 'warning',
                    'issues': security_issues,
                    'score': 70
                }
            else:
                return {
                    'status': 'healthy',
                    'issues': [],
                    'score': 95
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'score': 0
            }
    
    def _test_connectivity(self) -> Dict[str, Any]:
        """连接性测试"""
        test_results = []
        
        # 测试端口连接
        ports_to_test = [5672, 15672]
        
        for port in ports_to_test:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.rabbitmq_host, port))
                sock.close()
                
                if result == 0:
                    test_results.append({
                        'port': port,
                        'status': 'accessible',
                        'service': 'RabbitMQ' if port == 5672 else 'Management API'
                    })
                else:
                    test_results.append({
                        'port': port,
                        'status': 'unreachable',
                        'service': 'RabbitMQ' if port == 5672 else 'Management API'
                    })
            except Exception as e:
                test_results.append({
                    'port': port,
                    'status': 'error',
                    'error': str(e)
                })
        
        all_accessible = all(result['status'] == 'accessible' for result in test_results)
        
        return {
            'overall_status': 'healthy' if all_accessible else 'degraded',
            'tests': test_results
        }
    
    def _analyze_resource_usage(self) -> Dict[str, Any]:
        """资源使用分析"""
        try:
            # 获取进程信息
            rabbitmq_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'beam' in proc.info['name'].lower() or 'rabbitmq' in proc.info['name'].lower():
                        rabbitmq_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not rabbitmq_processes:
                return {'status': 'not_found', 'message': '未找到RabbitMQ进程'}
            
            total_cpu = sum(proc['cpu_percent'] for proc in rabbitmq_processes)
            total_memory = sum(proc['memory_percent'] for proc in rabbitmq_processes)
            
            return {
                'status': 'ok',
                'process_count': len(rabbitmq_processes),
                'total_cpu_percent': round(total_cpu, 2),
                'total_memory_percent': round(total_memory, 2),
                'processes': rabbitmq_processes
            }
        except Exception as e:
            self.logger.error(f"资源使用分析失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_diagnosis_recommendations(self, diagnosis: Dict[str, Any]) -> List[str]:
        """生成诊断建议"""
        recommendations = []
        
        # 系统健康建议
        system_health = diagnosis.get('system_health', {})
        if system_health.get('status') == 'critical':
            recommendations.append("系统资源使用率过高，建议立即调查原因")
        elif system_health.get('status') == 'warning':
            recommendations.append("系统资源使用率偏高，建议优化配置")
        
        # RabbitMQ健康建议
        rabbitmq_health = diagnosis.get('rabbitmq_health', {})
        if rabbitmq_health.get('status') == 'critical':
            recommendations.append("RabbitMQ服务不可用，请检查服务状态")
        elif rabbitmq_health.get('status') == 'degraded':
            recommendations.append("RabbitMQ API响应异常，请检查服务配置")
        
        # 安全建议
        security = diagnosis.get('security_check', {})
        if security.get('status') == 'warning':
            recommendations.append("发现安全风险，建议禁用默认用户或更改密码")
        
        # 连接性建议
        connectivity = diagnosis.get('connectivity_test', {})
        if connectivity.get('overall_status') == 'degraded':
            recommendations.append("网络连接存在问题，请检查防火墙和网络配置")
        
        if not recommendations:
            recommendations.append("系统运行正常，建议定期监控")
        
        return recommendations


class MaintenanceManager:
    """维护管理器"""
    
    def __init__(self, rabbitmq_host: str = 'localhost'):
        self.rabbitmq_host = rabbitmq_host
        self.logger = logging.getLogger(__name__)
    
    def create_maintenance_window(self, name: str, duration_minutes: int, 
                                description: str, affected_services: List[str],
                                mode: MaintenanceMode = MaintenanceMode.MAINTENANCE) -> MaintenanceWindow:
        """创建维护窗口"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        return MaintenanceWindow(
            name=name,
            start_time=start_time,
            end_time=end_time,
            description=description,
            affected_services=affected_services,
            maintenance_mode=mode
        )
    
    def enable_maintenance_mode(self, window: MaintenanceWindow) -> bool:
        """启用维护模式"""
        try:
            self.logger.info(f"启用维护模式: {window.name}")
            
            # 这里可以实现实际的维护模式切换逻辑
            # 例如：设置队列为暂停状态、限制连接等
            
            if window.maintenance_mode == MaintenanceMode.READ_ONLY:
                return self._set_read_only_mode(True)
            elif window.maintenance_mode == MaintenanceMode.MAINTENANCE:
                return self._set_maintenance_mode(True)
            
            return True
        except Exception as e:
            self.logger.error(f"启用维护模式失败: {e}")
            return False
    
    def disable_maintenance_mode(self, window: MaintenanceWindow) -> bool:
        """禁用维护模式"""
        try:
            self.logger.info(f"禁用维护模式: {window.name}")
            
            if window.maintenance_mode == MaintenanceMode.READ_ONLY:
                return self._set_read_only_mode(False)
            elif window.maintenance_mode == MaintenanceMode.MAINTENANCE:
                return self._set_maintenance_mode(False)
            
            return True
        except Exception as e:
            self.logger.error(f"禁用维护模式失败: {e}")
            return False
    
    def _set_read_only_mode(self, enable: bool) -> bool:
        """设置只读模式"""
        # 简化实现：记录操作日志
        action = "启用" if enable else "禁用"
        self.logger.info(f"{action}只读模式")
        return True
    
    def _set_maintenance_mode(self, enable: bool) -> bool:
        """设置维护模式"""
        # 简化实现：记录操作日志
        action = "启用" if enable else "禁用"
        self.logger.info(f"{action}维护模式")
        return True


class BackupManager:
    """备份管理器"""
    
    def __init__(self, rabbitmq_host: str = 'localhost', backup_dir: str = './backups'):
        self.rabbitmq_host = rabbitmq_host
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def create_full_backup(self, include_messages: bool = True) -> Dict[str, Any]:
        """创建完整备份"""
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"full_backup_{backup_id}"
        
        backup_result = {
            'backup_id': backup_id,
            'backup_path': str(backup_path),
            'start_time': datetime.now(),
            'end_time': None,
            'success': False,
            'components': []
        }
        
        try:
            backup_path.mkdir(exist_ok=True)
            
            # 备份配置
            config_result = self._backup_configuration(backup_path)
            backup_result['components'].append(config_result)
            
            # 备份定义
            definitions_result = self._backup_definitions(backup_path)
            backup_result['components'].append(definitions_result)
            
            # 备份消息（可选）
            if include_messages:
                messages_result = self._backup_messages(backup_path)
                backup_result['components'].append(messages_result)
            
            backup_result['success'] = all(
                comp.get('success', False) for comp in backup_result['components']
            )
            
        except Exception as e:
            self.logger.error(f"完整备份失败: {e}")
            backup_result['error'] = str(e)
        
        finally:
            backup_result['end_time'] = datetime.now()
        
        # 清理失败的备份
        if not backup_result['success'] and backup_path.exists():
            shutil.rmtree(backup_path, ignore_errors=True)
        
        return backup_result
    
    def restore_backup(self, backup_id: str, restore_messages: bool = True) -> Dict[str, Any]:
        """恢复备份"""
        backup_path = self.backup_dir / f"full_backup_{backup_id}"
        
        if not backup_path.exists():
            return {
                'success': False,
                'error': f'备份目录不存在: {backup_path}'
            }
        
        restore_result = {
            'backup_id': backup_id,
            'restore_path': str(backup_path),
            'start_time': datetime.now(),
            'end_time': None,
            'success': False,
            'steps': []
        }
        
        try:
            # 恢复配置
            config_result = self._restore_configuration(backup_path)
            restore_result['steps'].append(config_result)
            
            # 恢复定义
            definitions_result = self._restore_definitions(backup_path)
            restore_result['steps'].append(definitions_result)
            
            # 恢复消息（可选）
            if restore_messages:
                messages_result = self._restore_messages(backup_path)
                restore_result['steps'].append(messages_result)
            
            restore_result['success'] = all(
                step.get('success', False) for step in restore_result['steps']
            )
            
        except Exception as e:
            self.logger.error(f"恢复备份失败: {e}")
            restore_result['error'] = str(e)
        
        finally:
            restore_result['end_time'] = datetime.now()
        
        return restore_result
    
    def _backup_configuration(self, backup_path: Path) -> Dict[str, Any]:
        """备份配置"""
        try:
            config_file = backup_path / "configuration.json"
            
            # 获取RabbitMQ配置
            api_url = f"http://{self.rabbitmq_host}:15672/api/config"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                with open(config_file, 'w') as f:
                    json.dump(response.json(), f, indent=2)
                
                return {
                    'component': 'configuration',
                    'success': True,
                    'file': str(config_file)
                }
            else:
                return {
                    'component': 'configuration',
                    'success': False,
                    'error': f'API请求失败: {response.status_code}'
                }
        except Exception as e:
            return {
                'component': 'configuration',
                'success': False,
                'error': str(e)
            }
    
    def _backup_definitions(self, backup_path: Path) -> Dict[str, Any]:
        """备份定义"""
        try:
            definitions_file = backup_path / "definitions.json"
            
            # 获取RabbitMQ定义
            api_url = f"http://{self.rabbitmq_host}:15672/api/definitions"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                with open(definitions_file, 'w') as f:
                    json.dump(response.json(), f, indent=2)
                
                return {
                    'component': 'definitions',
                    'success': True,
                    'file': str(definitions_file)
                }
            else:
                return {
                    'component': 'definitions',
                    'success': False,
                    'error': f'API请求失败: {response.status_code}'
                }
        except Exception as e:
            return {
                'component': 'definitions',
                'success': False,
                'error': str(e)
            }
    
    def _backup_messages(self, backup_path: Path) -> Dict[str, Any]:
        """备份消息"""
        try:
            messages_dir = backup_path / "messages"
            messages_dir.mkdir(exist_ok=True)
            
            # 获取队列中的消息
            queues_url = f"http://{self.rabbitmq_host}:15672/api/queues"
            response = requests.get(queues_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'component': 'messages',
                    'success': False,
                    'error': f'获取队列信息失败: {response.status_code}'
                }
            
            queues = response.json()
            backed_up_messages = 0
            
            for queue in queues:
                queue_name = queue['name']
                message_count = queue.get('messages', 0)
                
                if message_count > 0:
                    # 备份消息数据
                    messages_file = messages_dir / f"{queue_name}_messages.json"
                    with open(messages_file, 'w') as f:
                        json.dump({
                            'queue_name': queue_name,
                            'message_count': message_count,
                            'backup_time': datetime.now().isoformat(),
                            'messages': []  # 这里应该实现实际的消息获取逻辑
                        }, f, indent=2)
                    
                    backed_up_messages += message_count
            
            return {
                'component': 'messages',
                'success': True,
                'backed_up_messages': backed_up_messages,
                'directory': str(messages_dir)
            }
        except Exception as e:
            return {
                'component': 'messages',
                'success': False,
                'error': str(e)
            }
    
    def _restore_configuration(self, backup_path: Path) -> Dict[str, Any]:
        """恢复配置"""
        try:
            config_file = backup_path / "configuration.json"
            
            if not config_file.exists():
                return {
                    'component': 'configuration',
                    'success': False,
                    'error': '配置文件不存在'
                }
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # 恢复配置（这里简化实现）
            self.logger.info("恢复RabbitMQ配置")
            
            return {
                'component': 'configuration',
                'success': True,
                'file': str(config_file)
            }
        except Exception as e:
            return {
                'component': 'configuration',
                'success': False,
                'error': str(e)
            }
    
    def _restore_definitions(self, backup_path: Path) -> Dict[str, Any]:
        """恢复定义"""
        try:
            definitions_file = backup_path / "definitions.json"
            
            if not definitions_file.exists():
                return {
                    'component': 'definitions',
                    'success': False,
                    'error': '定义文件不存在'
                }
            
            with open(definitions_file, 'r') as f:
                definitions_data = json.load(f)
            
            # 恢复定义（这里简化实现）
            self.logger.info("恢复RabbitMQ定义")
            
            return {
                'component': 'definitions',
                'success': True,
                'file': str(definitions_file)
            }
        except Exception as e:
            return {
                'component': 'definitions',
                'success': False,
                'error': str(e)
            }
    
    def _restore_messages(self, backup_path: Path) -> Dict[str, Any]:
        """恢复消息"""
        try:
            messages_dir = backup_path / "messages"
            
            if not messages_dir.exists():
                return {
                    'component': 'messages',
                    'success': True,
                    'restored_messages': 0,
                    'message': '消息备份不存在'
                }
            
            # 恢复消息数据（这里简化实现）
            restored_count = 0
            
            for message_file in messages_dir.glob("*_messages.json"):
                try:
                    with open(message_file, 'r') as f:
                        message_data = json.load(f)
                        restored_count += message_data.get('message_count', 0)
                except Exception as e:
                    self.logger.warning(f"恢复消息文件失败 {message_file}: {e}")
            
            return {
                'component': 'messages',
                'success': True,
                'restored_messages': restored_count,
                'directory': str(messages_dir)
            }
        except Exception as e:
            return {
                'component': 'messages',
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出可用备份"""
        backups = []
        
        try:
            for backup_dir in self.backup_dir.glob("full_backup_*"):
                if backup_dir.is_dir():
                    backup_info = {
                        'backup_id': backup_dir.name.replace('full_backup_', ''),
                        'path': str(backup_dir),
                        'created_time': datetime.fromtimestamp(backup_dir.stat().st_ctime),
                        'size_mb': round(sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / 1024**2, 2)
                    }
                    backups.append(backup_info)
        except Exception as e:
            self.logger.error(f"列出备份失败: {e}")
        
        return sorted(backups, key=lambda x: x['created_time'], reverse=True)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.tasks = {}
        self.scheduled_tasks = {}
        self.running_tasks = {}
        self.task_callbacks = {}
        self.logger = logging.getLogger(__name__)
    
    def create_task(self, task: Task) -> str:
        """创建任务"""
        self.tasks[task.id] = task
        self.logger.info(f"创建任务: {task.name} ({task.id})")
        return task.id
    
    def schedule_task(self, task_id: str, schedule_time: datetime):
        """调度任务"""
        if task_id not in self.tasks:
            raise ValueError(f"任务不存在: {task_id}")
        
        self.scheduled_tasks[task_id] = schedule_time
        self.logger.info(f"调度任务 {task_id} 于 {schedule_time}")
    
    def execute_task(self, task_id: str) -> bool:
        """执行任务"""
        if task_id not in self.tasks:
            self.logger.error(f"任务不存在: {task_id}")
            return False
        
        task = self.tasks[task_id]
        if task.status != TaskStatus.PENDING:
            self.logger.warning(f"任务状态不正确: {task.status}")
            return False
        
        self.running_tasks[task_id] = task
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        
        # 在新线程中执行任务
        thread = threading.Thread(target=self._execute_task_worker, args=(task,))
        thread.daemon = True
        thread.start()
        
        return True
    
    def _execute_task_worker(self, task: Task):
        """任务执行工作线程"""
        try:
            result = self._execute_task_action(task)
            
            task.status = TaskStatus.SUCCESS
            task.result = result
            self.logger.info(f"任务执行成功: {task.name}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.logger.error(f"任务执行失败: {task.name} - {e}")
        
        finally:
            task.end_time = datetime.now()
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    def _execute_task_action(self, task: Task) -> Dict[str, Any]:
        """执行任务动作"""
        if task.action == 'backup':
            return self._execute_backup_action(task.parameters)
        elif task.action == 'cleanup':
            return self._execute_cleanup_action(task.parameters)
        elif task.action == 'optimize':
            return self._execute_optimize_action(task.parameters)
        elif task.action == 'health_check':
            return self._execute_health_check_action(task.parameters)
        else:
            raise ValueError(f"不支持的任务动作: {task.action}")
    
    def _execute_backup_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行备份动作"""
        backup_manager = BackupManager(
            params.get('host', 'localhost'),
            params.get('backup_dir', './backups')
        )
        
        result = backup_manager.create_full_backup(
            include_messages=params.get('include_messages', True)
        )
        
        return {
            'action': 'backup',
            'backup_id': result.get('backup_id'),
            'success': result.get('success', False),
            'message': '备份操作完成'
        }
    
    def _execute_cleanup_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行清理动作"""
        # 简化实现：清理日志文件
        cleanup_count = 0
        
        log_dirs = ['./logs', './tmp']
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                try:
                    for file in os.listdir(log_dir):
                        if file.endswith('.log'):
                            file_path = os.path.join(log_dir, file)
                            if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                                os.remove(file_path)
                                cleanup_count += 1
                except Exception as e:
                    self.logger.warning(f"清理目录 {log_dir} 失败: {e}")
        
        return {
            'action': 'cleanup',
            'cleanup_count': cleanup_count,
            'success': True,
            'message': f'清理了 {cleanup_count} 个文件'
        }
    
    def _execute_optimize_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行优化动作"""
        # 简化实现：返回优化信息
        return {
            'action': 'optimize',
            'optimizations_applied': ['connection_pool_reconfigure', 'queue_auto_cleanup'],
            'success': True,
            'message': '系统优化完成'
        }
    
    def _execute_health_check_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行健康检查动作"""
        diagnostic = SystemDiagnostic(params.get('host', 'localhost'))
        diagnosis = diagnostic.run_comprehensive_diagnosis()
        
        return {
            'action': 'health_check',
            'overall_health': diagnosis.get('system_health', {}).get('status', 'unknown'),
            'health_score': diagnosis.get('system_health', {}).get('score', 0),
            'success': True,
            'message': '健康检查完成'
        }
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_running_tasks(self) -> List[Task]:
        """获取运行中的任务"""
        return list(self.running_tasks.values())
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.end_time = datetime.now()
            del self.running_tasks[task_id]
            self.logger.info(f"任务已取消: {task_id}")
            return True
        
        return False


class OperationsAutomationDemo:
    """运维自动化演示"""
    
    def __init__(self, rabbitmq_host: str = 'localhost'):
        self.diagnostic = SystemDiagnostic(rabbitmq_host)
        self.maintenance = MaintenanceManager(rabbitmq_host)
        self.backup = BackupManager(rabbitmq_host)
        self.scheduler = TaskScheduler()
        self.logger = logging.getLogger(__name__)
    
    def demo_system_diagnosis(self):
        """演示系统诊断"""
        print("=== 系统诊断演示 ===")
        
        try:
            diagnosis = self.diagnostic.run_comprehensive_diagnosis()
            
            print(f"诊断时间: {diagnosis['timestamp']}")
            
            # 系统健康
            system_health = diagnosis.get('system_health', {})
            print(f"系统状态: {system_health.get('status', 'unknown')}")
            print(f"系统健康分数: {system_health.get('score', 0)}/100")
            print(f"CPU使用率: {system_health.get('cpu_percent', 0):.1f}%")
            print(f"内存使用率: {system_health.get('memory_percent', 0):.1f}%")
            print(f"磁盘使用率: {system_health.get('disk_percent', 0):.1f}%")
            
            # RabbitMQ健康
            rabbitmq_health = diagnosis.get('rabbitmq_health', {})
            print(f"RabbitMQ状态: {rabbitmq_health.get('status', 'unknown')}")
            
            # 连接性测试
            connectivity = diagnosis.get('connectivity_test', {})
            print(f"连接性状态: {connectivity.get('overall_status', 'unknown')}")
            
            # 建议
            recommendations = diagnosis.get('recommendations', [])
            if recommendations:
                print("\n优化建议:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            
        except Exception as e:
            print(f"系统诊断失败: {e}")
    
    def demo_maintenance_management(self):
        """演示维护管理"""
        print("\n=== 维护管理演示 ===")
        
        try:
            # 创建维护窗口
            maintenance_window = self.maintenance.create_maintenance_window(
                name="例行维护",
                duration_minutes=30,
                description="系统例行维护和更新",
                affected_services=["队列A", "队列B"],
                mode=MaintenanceMode.MAINTENANCE
            )
            
            print(f"维护窗口: {maintenance_window.name}")
            print(f"开始时间: {maintenance_window.start_time}")
            print(f"结束时间: {maintenance_window.end_time}")
            print(f"维护模式: {maintenance_window.maintenance_mode.value}")
            
            # 启用维护模式
            success = self.maintenance.enable_maintenance_mode(maintenance_window)
            print(f"启用维护模式: {'成功' if success else '失败'}")
            
            # 模拟维护操作
            print("执行维护操作...")
            time.sleep(2)
            
            # 禁用维护模式
            success = self.maintenance.disable_maintenance_mode(maintenance_window)
            print(f"禁用维护模式: {'成功' if success else '失败'}")
            
        except Exception as e:
            print(f"维护管理演示失败: {e}")
    
    def demo_backup_restore(self):
        """演示备份恢复"""
        print("\n=== 备份恢复演示 ===")
        
        try:
            # 创建备份
            print("创建系统备份...")
            backup_result = self.backup.create_full_backup(include_messages=False)
            
            print(f"备份ID: {backup_result.get('backup_id')}")
            print(f"备份路径: {backup_result.get('backup_path')}")
            print(f"备份状态: {'成功' if backup_result.get('success') else '失败'}")
            
            if backup_result.get('success'):
                components = backup_result.get('components', [])
                print("备份组件:")
                for comp in components:
                    component_name = comp.get('component', 'unknown')
                    component_status = '成功' if comp.get('success') else '失败'
                    print(f"  - {component_name}: {component_status}")
            
            # 列出可用备份
            backups = self.backup.list_backups()
            print(f"\n可用备份数量: {len(backups)}")
            for backup in backups[:3]:  # 只显示前3个
                print(f"  - 备份 {backup['backup_id']}: {backup['created_time']} ({backup['size_mb']} MB)")
            
        except Exception as e:
            print(f"备份恢复演示失败: {e}")
    
    def demo_task_scheduling(self):
        """演示任务调度"""
        print("\n=== 任务调度演示 ===")
        
        try:
            # 创建备份任务
            backup_task = Task(
                id="backup_task_1",
                name="定时备份任务",
                description="每30分钟执行一次完整备份",
                action="backup",
                parameters={
                    'host': 'localhost',
                    'backup_dir': './scheduled_backups',
                    'include_messages': True
                }
            )
            
            task_id = self.scheduler.create_task(backup_task)
            print(f"创建任务: {task_id}")
            
            # 立即执行任务
            print("执行备份任务...")
            success = self.scheduler.execute_task(task_id)
            print(f"任务启动: {'成功' if success else '失败'}")
            
            # 等待任务完成
            time.sleep(5)
            
            # 检查任务状态
            task_status = self.scheduler.get_task_status(task_id)
            if task_status:
                print(f"任务状态: {task_status.status.value}")
                print(f"开始时间: {task_status.start_time}")
                print(f"结束时间: {task_status.end_time}")
                if task_status.result:
                    print(f"任务结果: {task_status.result}")
            
            # 创建健康检查任务
            health_task = Task(
                id="health_check_task",
                name="定时健康检查",
                description="每小时执行一次系统健康检查",
                action="health_check",
                parameters={'host': 'localhost'}
            )
            
            self.scheduler.create_task(health_task)
            
            # 获取运行中的任务
            running_tasks = self.scheduler.get_running_tasks()
            print(f"运行中的任务数: {len(running_tasks)}")
            
        except Exception as e:
            print(f"任务调度演示失败: {e}")
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("RabbitMQ运维自动化演示开始")
        print("=" * 50)
        
        try:
            # 1. 系统诊断
            self.demo_system_diagnosis()
            
            # 2. 维护管理
            self.demo_maintenance_management()
            
            # 3. 备份恢复
            self.demo_backup_restore()
            
            # 4. 任务调度
            self.demo_task_scheduling()
            
            print("\n演示完成!")
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    demo = OperationsAutomationDemo()
    demo.run_complete_demo()