"""
故障演练与测试模块
Chapter 10: 故障处理与恢复

提供故障注入、故障演练、测试框架和恢复验证等功能
"""

import os
import sys
import time
import json
import threading
import random
import subprocess
import signal
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from contextlib import contextmanager
import psutil


class FaultType(Enum):
    """故障类型枚举"""
    SERVICE_DOWN = "service_down"
    SERVICE_RESTART = "service_restart"
    NETWORK_PARTITION = "network_partition"
    HIGH_LATENCY = "high_latency"
    PACKET_LOSS = "packet_loss"
    CPU_OVERLOAD = "cpu_overload"
    MEMORY_OVERLOAD = "memory_overload"
    DISK_FULL = "disk_full"
    DISK_SLOW = "disk_slow"
    RABBITMQ_QUEUE_FULL = "rabbitmq_queue_full"
    RABBITMQ_CLUSTER_SPLIT = "rabbitmq_cluster_split"
    RABBITMQ_NODE_DOWN = "rabbitmq_node_down"
    CONNECTION_TIMEOUT = "connection_timeout"
    AUTHENTICATION_FAILURE = "authentication_failure"


class FaultSeverity(Enum):
    """故障严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ScenarioPhase(Enum):
    """演练阶段枚举"""
    SETUP = "setup"
    INJECTION = "injection"
    DETECTION = "detection"
    RECOVERY = "recovery"
    VALIDATION = "validation"
    CLEANUP = "cleanup"
    COMPLETED = "completed"


@dataclass
class FaultInjection:
    """故障注入配置"""
    fault_type: FaultType
    severity: FaultSeverity
    target_component: str
    duration_seconds: int
    parameters: Dict[str, Any]
    enabled: bool = True


@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    fault_injections: List[FaultInjection]
    expected_behavior: Dict[str, Any]
    timeout_seconds: int = 300
    retries: int = 0
    enabled: bool = True


@dataclass
class TestExecution:
    """测试执行结果"""
    scenario_name: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime]
    phases: Dict[str, ScenarioPhase]
    results: Dict[str, Any]
    errors: List[str]
    metrics: Dict[str, float]


class SystemResourceManipulator:
    """系统资源操作器"""
    
    @staticmethod
    def cpu_overload(target_percentage: float, duration: int):
        """CPU过载故障注入"""
        def cpu_stress():
            start_time = time.time()
            while time.time() - start_time < duration:
                # 计算密集型任务
                for i in range(1000000):
                    _ = i ** 2
        
        # 创建多个线程来产生CPU负载
        thread_count = max(1, int(psutil.cpu_count() * target_percentage / 100))
        threads = []
        
        for _ in range(thread_count):
            thread = threading.Thread(target=cpu_stress)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 等待指定时间
        time.sleep(duration)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=1)
    
    @staticmethod
    def memory_overload(target_percentage: float, duration: int):
        """内存过载故障注入"""
        # 创建内存压力
        memory_eaters = []
        total_memory = psutil.virtual_memory().total
        target_bytes = total_memory * target_percentage / 100
        
        try:
            # 分配大量内存
            chunk_size = 1024 * 1024  # 1MB chunks
            chunks_needed = int(target_bytes / chunk_size)
            
            for i in range(chunks_needed):
                memory_eaters.append(b'x' * chunk_size)
                time.sleep(0.01)  # 逐渐分配
            
            # 保持内存占用
            time.sleep(duration)
            
        finally:
            # 清理内存
            memory_eaters.clear()
    
    @staticmethod
    def disk_full_simulation(target_path: str, duration: int):
        """磁盘满故障模拟"""
        try:
            # 创建大文件占满磁盘
            disk_usage = psutil.disk_usage(target_path)
            free_space = disk_usage.free
            
            # 创建一个接近满容量的文件
            file_path = os.path.join(target_path, '.fault_injection_large_file')
            chunk_size = 1024 * 1024  # 1MB
            max_size = free_space - 1024 * 1024  # 留1MB
            
            with open(file_path, 'wb') as f:
                written = 0
                start_time = time.time()
                
                while written < max_size and time.time() - start_time < duration:
                    size_to_write = min(chunk_size, max_size - written)
                    f.write(b'x' * size_to_write)
                    written += size_to_write
                    time.sleep(0.1)
            
            # 等待指定时间
            remaining_time = duration - (time.time() - start_time)
            if remaining_time > 0:
                time.sleep(remaining_time)
                
        except Exception:
            pass
        finally:
            # 清理大文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
    
    @staticmethod
    def disk_slow_simulation(duration: int, slowdown_factor: float = 10):
        """磁盘慢速故障模拟"""
        start_time = time.time()
        
        def slow_io():
            while time.time() - start_time < duration:
                try:
                    # 创建临时文件并频繁读写
                    temp_file = f'/tmp/slow_io_{threading.current_thread().ident}_{time.time()}.tmp'
                    with open(temp_file, 'wb') as f:
                        f.write(b'x' * 1024 * 1024)  # 1MB
                    
                    with open(temp_file, 'rb') as f:
                        _ = f.read()
                    
                    os.remove(temp_file)
                    
                    # 添加延迟
                    time.sleep(0.1 * slowdown_factor)
                    
                except Exception:
                    pass
        
        # 创建多个IO压力线程
        threads = []
        for _ in range(4):
            thread = threading.Thread(target=slow_io)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 等待完成
        for thread in threads:
            thread.join()


class NetworkFaultInjector:
    """网络故障注入器"""
    
    def __init__(self):
        self.platform = sys.platform
    
    def packet_loss(self, interface: str = 'eth0', loss_percentage: float = 50, duration: int = 30):
        """数据包丢失故障注入"""
        try:
            if self.platform == 'linux':
                # 使用tc (traffic control) 命令模拟丢包
                cmd = [
                    'sudo', 'tc', 'qdisc', 'add', 'dev', interface,
                    'root', 'netem', 'loss', f'{loss_percentage}%'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # 等待指定时间
                time.sleep(duration)
                
                # 清理规则
                cleanup_cmd = ['sudo', 'tc', 'qdisc', 'del', 'dev', interface, 'root']
                subprocess.run(cleanup_cmd, capture_output=True)
                
            elif self.platform == 'darwin':  # macOS
                # macOS网络故障注入相对复杂，这里提供一个简化的实现
                print("macOS平台的网络故障注入需要使用高级工具")
                
            elif self.platform == 'win32':
                # Windows网络故障注入需要特殊工具
                print("Windows平台的网络故障注入需要特殊工具")
                
        except Exception as e:
            print(f"网络故障注入失败: {e}")
    
    def latency_injection(self, interface: str = 'eth0', delay_ms: int = 1000, duration: int = 30):
        """网络延迟故障注入"""
        try:
            if self.platform == 'linux':
                # 使用tc命令注入延迟
                cmd = [
                    'sudo', 'tc', 'qdisc', 'add', 'dev', interface,
                    'root', 'netem', 'delay', f'{delay_ms}ms'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # 等待指定时间
                time.sleep(duration)
                
                # 清理规则
                cleanup_cmd = ['sudo', 'tc', 'qdisc', 'del', 'dev', interface, 'root']
                subprocess.run(cleanup_cmd, capture_output=True)
                
        except Exception as e:
            print(f"网络延迟注入失败: {e}")
    
    def bandwidth_limitation(self, interface: str = 'eth0', rate: str = '1mbit', duration: int = 30):
        """带宽限制故障注入"""
        try:
            if self.platform == 'linux':
                # 使用tc命令限制带宽
                cmd = [
                    'sudo', 'tc', 'qdisc', 'add', 'dev', interface,
                    'root', 'tbf', 'rate', rate, 'latency', '50ms', 'burst', '1540'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # 等待指定时间
                time.sleep(duration)
                
                # 清理规则
                cleanup_cmd = ['sudo', 'tc', 'qdisc', 'del', 'dev', interface, 'root']
                subprocess.run(cleanup_cmd, capture_output=True)
                
        except Exception as e:
            print(f"带宽限制注入失败: {e}")


class RabbitMQFaultInjector:
    """RabbitMQ故障注入器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5672)
        self.api_port = config.get('api_port', 15672)
        self.username = config.get('username', 'guest')
        self.password = config.get('password', 'guest')
    
    def queue_overflow(self, queue_name: str, message_count: int = 10000, duration: int = 60):
        """队列溢出故障注入"""
        try:
            import pika
            
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # 声明队列
            channel.queue_declare(queue=queue_name, durable=True)
            
            # 持续发送消息直到队列满
            messages_sent = 0
            start_time = time.time()
            
            while messages_sent < message_count and (time.time() - start_time) < duration:
                try:
                    message = f"fault_injection_message_{messages_sent}_{time.time()}"
                    
                    # 设置消息属性，使队列快速满载
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # 持久化
                            priority=0,
                            timestamp=int(time.time())
                        )
                    )
                    
                    messages_sent += 1
                    
                    # 如果队列已满，停止发送
                    if messages_sent % 1000 == 0:
                        time.sleep(0.1)
                        
                except Exception:
                    # 队列已满，停止发送
                    break
            
            connection.close()
            
            print(f"队列溢出注入完成，发送消息数: {messages_sent}")
            return messages_sent
            
        except Exception as e:
            print(f"队列溢出注入失败: {e}")
            return 0
    
    def connection_attack(self, attack_duration: int = 60, concurrent_connections: int = 100):
        """连接攻击故障注入"""
        import threading
        import pika
        
        connections = []
        channels = []
        connection_threads = []
        
        def create_connection():
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials
                )
                
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                
                connections.append(connection)
                channels.append(channel)
                
                # 保持连接活跃
                time.sleep(attack_duration)
                
            except Exception:
                pass
        
        try:
            # 创建大量并发连接
            for i in range(concurrent_connections):
                thread = threading.Thread(target=create_connection)
                thread.daemon = True
                thread.start()
                connection_threads.append(thread)
            
            # 等待攻击持续时间
            time.sleep(attack_duration)
            
        finally:
            # 清理连接
            for connection in connections:
                try:
                    connection.close()
                except Exception:
                pass
        
        print(f"连接攻击注入完成，创建连接数: {len(connections)}")
    
    def cluster_partition_simulation(self, affected_nodes: List[str], duration: int = 30):
        """集群分区故障模拟"""
        try:
            # 这里可以模拟集群节点间的网络隔离
            # 实际实现需要根据具体的集群管理工具进行调整
            
            print(f"开始集群分区模拟，影响节点: {affected_nodes}")
            
            # 模拟分区过程
            for node in affected_nodes:
                print(f"模拟节点 {node} 分区")
            
            # 等待指定时间
            time.sleep(duration)
            
            print("集群分区模拟结束")
            
        except Exception as e:
            print(f"集群分区模拟失败: {e}")


class FaultInjectionOrchestrator:
    """故障注入编排器"""
    
    def __init__(self, rabbitmq_config: Dict[str, Any]):
        self.rabbitmq_config = rabbitmq_config
        self.resource_manipulator = SystemResourceManipulator()
        self.network_injector = NetworkFaultInjector()
        self.rabbitmq_injector = RabbitMQFaultInjector(rabbitmq_config)
        
        # 故障注入映射
        self.fault_mapping = {
            FaultType.CPU_OVERLOAD: self._inject_cpu_overload,
            FaultType.MEMORY_OVERLOAD: self._inject_memory_overload,
            FaultType.DISK_FULL: self._inject_disk_full,
            FaultType.DISK_SLOW: self._inject_disk_slow,
            FaultType.PACKET_LOSS: self._inject_packet_loss,
            FaultType.HIGH_LATENCY: self._inject_high_latency,
            FaultType.RABBITMQ_QUEUE_FULL: self._inject_queue_full,
            FaultType.CONNECTION_TIMEOUT: self._inject_connection_timeout,
            FaultType.SERVICE_DOWN: self._inject_service_down
        }
    
    def inject_fault(self, fault_injection: FaultInjection) -> Dict[str, Any]:
        """执行故障注入"""
        fault_type = fault_injection.fault_type
        severity = fault_injection.severity
        target_component = fault_injection.target_component
        duration = fault_injection.duration_seconds
        parameters = fault_injection.parameters
        
        print(f"开始故障注入: {fault_type.value} (目标: {target_component}, 持续时间: {duration}秒)")
        
        try:
            if fault_type in self.fault_mapping:
                result = self.fault_mapping[fault_type](duration, parameters)
                print(f"故障注入完成: {fault_type.value}")
                return {
                    'success': True,
                    'fault_type': fault_type.value,
                    'duration': duration,
                    'target': target_component,
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'未知的故障类型: {fault_type.value}'
                }
        except Exception as e:
            print(f"故障注入异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'fault_type': fault_type.value
            }
    
    def _inject_cpu_overload(self, duration: int, parameters: Dict[str, Any]):
        """CPU过载注入"""
        target_percentage = parameters.get('target_percentage', 90)
        self.resource_manipulator.cpu_overload(target_percentage, duration)
    
    def _inject_memory_overload(self, duration: int, parameters: Dict[str, Any]):
        """内存过载注入"""
        target_percentage = parameters.get('target_percentage', 80)
        self.resource_manipulator.memory_overload(target_percentage, duration)
    
    def _inject_disk_full(self, duration: int, parameters: Dict[str, Any]):
        """磁盘满注入"""
        target_path = parameters.get('target_path', '/tmp')
        self.resource_manipulator.disk_full_simulation(target_path, duration)
    
    def _inject_disk_slow(self, duration: int, parameters: Dict[str, Any]):
        """磁盘慢速注入"""
        slowdown_factor = parameters.get('slowdown_factor', 5)
        self.resource_manipulator.disk_slow_simulation(duration, slowdown_factor)
    
    def _inject_packet_loss(self, duration: int, parameters: Dict[str, Any]):
        """数据包丢失注入"""
        interface = parameters.get('interface', 'eth0')
        loss_percentage = parameters.get('loss_percentage', 50)
        self.network_injector.packet_loss(interface, loss_percentage, duration)
    
    def _inject_high_latency(self, duration: int, parameters: Dict[str, Any]):
        """高延迟注入"""
        interface = parameters.get('interface', 'eth0')
        delay_ms = parameters.get('delay_ms', 1000)
        self.network_injector.latency_injection(interface, delay_ms, duration)
    
    def _inject_queue_full(self, duration: int, parameters: Dict[str, Any]):
        """队列满注入"""
        queue_name = parameters.get('queue_name', 'fault_injection_queue')
        message_count = parameters.get('message_count', 10000)
        messages_sent = self.rabbitmq_injector.queue_overflow(queue_name, message_count, duration)
        return {'messages_sent': messages_sent}
    
    def _inject_connection_timeout(self, duration: int, parameters: Dict[str, Any]):
        """连接超时注入"""
        concurrent_connections = parameters.get('concurrent_connections', 100)
        self.rabbitmq_injector.connection_attack(duration, concurrent_connections)
    
    def _inject_service_down(self, duration: int, parameters: Dict[str, Any]):
        """服务宕机注入"""
        # 这里可以实现服务停止逻辑
        service_name = parameters.get('service_name', 'rabbitmq')
        
        try:
            # Linux系统使用systemctl
            if sys.platform.startswith('linux'):
                # 停止服务
                cmd = ['sudo', 'systemctl', 'stop', service_name]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # 等待指定时间
                time.sleep(duration)
                
                # 重新启动服务
                start_cmd = ['sudo', 'systemctl', 'start', service_name]
                subprocess.run(start_cmd, check=True, capture_output=True)
                
                print(f"服务 {service_name} 故障注入完成")
            else:
                print(f"平台 {sys.platform} 不支持服务宕机注入")
                
        except Exception as e:
            print(f"服务宕机注入失败: {e}")


class FaultTestExecutor:
    """故障测试执行器"""
    
    def __init__(self, rabbitmq_config: Dict[str, Any]):
        self.rabbitmq_config = rabbitmq_config
        self.orchestrator = FaultInjectionOrchestrator(rabbitmq_config)
        self.execution_history: deque = deque(maxlen=100)
        
        # 监控回调
        self.monitoring_callbacks: List[Callable] = []
    
    def execute_scenario(self, scenario: TestScenario) -> TestExecution:
        """执行测试场景"""
        execution = TestExecution(
            scenario_name=scenario.name,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            phases={
                'setup': ScenarioPhase.PENDING,
                'injection': ScenarioPhase.PENDING,
                'detection': ScenarioPhase.PENDING,
                'recovery': ScenarioPhase.PENDING,
                'validation': ScenarioPhase.PENDING,
                'cleanup': ScenarioPhase.PENDING
            },
            results={},
            errors=[],
            metrics={}
        )
        
        try:
            print(f"\n开始执行测试场景: {scenario.name}")
            print(f"场景描述: {scenario.description}")
            print(f"超时设置: {scenario.timeout_seconds}秒")
            print("-" * 60)
            
            # 1. 设置阶段
            execution.phases['setup'] = ScenarioPhase.IN_PROGRESS
            setup_result = self._setup_scenario(scenario)
            execution.phases['setup'] = ScenarioPhase.COMPLETED
            execution.results['setup'] = setup_result
            
            # 2. 故障注入阶段
            execution.phases['injection'] = ScenarioPhase.IN_PROGRESS
            injection_result = self._inject_faults(scenario.fault_injections)
            execution.phases['injection'] = ScenarioPhase.COMPLETED
            execution.results['injection'] = injection_result
            
            # 3. 检测阶段
            execution.phases['detection'] = ScenarioPhase.IN_PROGRESS
            detection_result = self._detect_fault_impact()
            execution.phases['detection'] = ScenarioPhase.COMPLETED
            execution.results['detection'] = detection_result
            
            # 4. 恢复阶段
            execution.phases['recovery'] = ScenarioPhase.IN_PROGRESS
            recovery_result = self._perform_recovery()
            execution.phases['recovery'] = ScenarioPhase.COMPLETED
            execution.results['recovery'] = recovery_result
            
            # 5. 验证阶段
            execution.phases['validation'] = ScenarioPhase.IN_PROGRESS
            validation_result = self._validate_system_health()
            execution.phases['validation'] = ScenarioPhase.COMPLETED
            execution.results['validation'] = validation_result
            
            # 6. 清理阶段
            execution.phases['cleanup'] = ScenarioPhase.IN_PROGRESS
            cleanup_result = self._cleanup_scenario()
            execution.phases['cleanup'] = ScenarioPhase.COMPLETED
            execution.results['cleanup'] = cleanup_result
            
            # 评估整体结果
            execution.status = self._evaluate_execution_result(execution, scenario)
            execution.end_time = datetime.now()
            
            print(f"\n测试场景执行完成: {scenario.name}")
            print(f"执行状态: {execution.status.value}")
            print(f"执行时长: {(execution.end_time - execution.start_time).total_seconds():.2f}秒")
            
        except Exception as e:
            execution.status = TestStatus.FAILED
            execution.end_time = datetime.now()
            execution.errors.append(f"执行异常: {str(e)}")
            print(f"\n测试场景执行失败: {scenario.name}")
            print(f"错误: {str(e)}")
        
        finally:
            # 清理所有故障注入
            self._cleanup_all_faults()
        
        # 保存执行历史
        self.execution_history.append(execution)
        
        return execution
    
    def _setup_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """设置测试场景"""
        print("设置阶段...")
        
        # 记录初始系统状态
        initial_metrics = self._collect_system_metrics()
        
        return {
            'initial_metrics': initial_metrics,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _inject_faults(self, fault_injections: List[FaultInjection]) -> Dict[str, Any]:
        """执行故障注入"""
        print("故障注入阶段...")
        
        injection_results = []
        start_time = time.time()
        
        for fault in fault_injections:
            if not fault.enabled:
                continue
                
            print(f"  注入故障: {fault.fault_type.value}")
            result = self.orchestrator.inject_fault(fault)
            injection_results.append(result)
        
        return {
            'injection_results': injection_results,
            'total_injected': len(injection_results),
            'duration': time.time() - start_time,
            'success': True
        }
    
    def _detect_fault_impact(self) -> Dict[str, Any]:
        """检测故障影响"""
        print("故障检测阶段...")
        
        # 收集当前系统指标
        current_metrics = self._collect_system_metrics()
        
        # 计算影响程度
        impact_analysis = self._analyze_fault_impact(current_metrics)
        
        return {
            'current_metrics': current_metrics,
            'impact_analysis': impact_analysis,
            'detection_time': datetime.now().isoformat(),
            'success': True
        }
    
    def _perform_recovery(self) -> Dict[str, Any]:
        """执行恢复操作"""
        print("系统恢复阶段...")
        
        recovery_start_time = time.time()
        
        try:
            # 这里可以执行自定义恢复逻辑
            # 比如启动服务、清理故障、重新连接等
            
            # 模拟恢复过程
            time.sleep(5)
            
            recovery_time = time.time() - recovery_start_time
            
            return {
                'recovery_time': recovery_time,
                'recovery_successful': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'recovery_successful': False,
                'error': str(e),
                'recovery_time': time.time() - recovery_start_time
            }
    
    def _validate_system_health(self) -> Dict[str, Any]:
        """验证系统健康状态"""
        print("系统验证阶段...")
        
        # 收集验证指标
        validation_metrics = self._collect_system_metrics()
        
        # 进行健康检查
        health_check = self._perform_health_check()
        
        # 验证结果
        validation_passed = health_check.get('overall_status') == 'healthy'
        
        return {
            'validation_metrics': validation_metrics,
            'health_check': health_check,
            'validation_passed': validation_passed,
            'timestamp': datetime.now().isoformat()
        }
    
    def _cleanup_scenario(self) -> Dict[str, Any]:
        """清理测试场景"""
        print("清理阶段...")
        
        # 清理故障注入
        cleanup_success = True
        error_messages = []
        
        try:
            # 这里可以执行具体的清理逻辑
            # 比如删除测试队列、重置配置等
            
            return {
                'cleanup_successful': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'cleanup_successful': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _cleanup_all_faults(self):
        """清理所有故障注入"""
        try:
            # 这里可以添加清理各种故障注入的逻辑
            # 比如恢复网络设置、停止服务等
            pass
        except Exception:
            pass
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': dict(psutil.net_io_counters()._asdict()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _analyze_fault_impact(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """分析故障影响"""
        impact_score = 0
        impact_details = []
        
        # 分析CPU使用率
        if 'cpu_percent' in current_metrics:
            cpu_percent = current_metrics['cpu_percent']
            if cpu_percent > 90:
                impact_score += 30
                impact_details.append(f"CPU使用率过高: {cpu_percent}%")
            elif cpu_percent > 70:
                impact_score += 15
                impact_details.append(f"CPU使用率较高: {cpu_percent}%")
        
        # 分析内存使用率
        if 'memory_percent' in current_metrics:
            memory_percent = current_metrics['memory_percent']
            if memory_percent > 90:
                impact_score += 30
                impact_details.append(f"内存使用率过高: {memory_percent}%")
            elif memory_percent > 80:
                impact_score += 15
                impact_details.append(f"内存使用率较高: {memory_percent}%")
        
        # 分析磁盘使用率
        if 'disk_usage' in current_metrics:
            disk_usage = current_metrics['disk_usage']
            if disk_usage > 95:
                impact_score += 40
                impact_details.append(f"磁盘使用率过高: {disk_usage}%")
            elif disk_usage > 85:
                impact_score += 20
                impact_details.append(f"磁盘使用率较高: {disk_usage}%")
        
        return {
            'impact_score': impact_score,
            'impact_level': 'high' if impact_score > 50 else 'medium' if impact_score > 20 else 'low',
            'impact_details': impact_details
        }
    
    def _perform_health_check(self) -> Dict[str, Any]:
        """执行健康检查"""
        try:
            # 简单的健康检查
            metrics = self._collect_system_metrics()
            
            healthy_count = 0
            total_checks = 0
            
            # 检查CPU
            if 'cpu_percent' in metrics:
                total_checks += 1
                if metrics['cpu_percent'] < 80:
                    healthy_count += 1
            
            # 检查内存
            if 'memory_percent' in metrics:
                total_checks += 1
                if metrics['memory_percent'] < 80:
                    healthy_count += 1
            
            # 检查磁盘
            if 'disk_usage' in metrics:
                total_checks += 1
                if metrics['disk_usage'] < 80:
                    healthy_count += 1
            
            overall_status = 'healthy' if healthy_count == total_checks else 'degraded'
            
            return {
                'overall_status': overall_status,
                'healthy_checks': healthy_count,
                'total_checks': total_checks,
                'health_ratio': healthy_count / total_checks if total_checks > 0 else 0
            }
            
        except Exception as e:
            return {
                'overall_status': 'error',
                'error': str(e)
            }
    
    def _evaluate_execution_result(self, execution: TestExecution, scenario: TestScenario) -> TestStatus:
        """评估执行结果"""
        # 检查是否有严重错误
        if execution.errors:
            return TestStatus.FAILED
        
        # 检查阶段执行情况
        for phase_name, phase_status in execution.phases.items():
            if phase_status not in [ScenarioPhase.COMPLETED, ScenarioPhase.PENDING]:
                if phase_status != ScenarioPhase.COMPLETED:
                    return TestStatus.FAILED
        
        # 检查验证阶段结果
        validation_result = execution.results.get('validation', {})
        if not validation_result.get('validation_passed', False):
            return TestStatus.FAILED
        
        # 检查预期行为
        expected_behavior = scenario.expected_behavior
        actual_behavior = execution.results
        
        # 简化的预期行为验证
        if expected_behavior.get('should_detect_fault', True):
            detection_result = execution.results.get('detection', {})
            if not detection_result.get('success', False):
                return TestStatus.FAILED
        
        if expected_behavior.get('should_recover', True):
            recovery_result = execution.results.get('recovery', {})
            if not recovery_result.get('recovery_successful', False):
                return TestStatus.FAILED
        
        return TestStatus.PASSED
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return [asdict(exec) for exec in list(self.execution_history)[-limit:]]


class FaultInjectionDemo:
    """故障注入演示"""
    
    def __init__(self):
        # RabbitMQ配置
        self.rabbitmq_config = {
            'host': 'localhost',
            'port': 5672,
            'api_port': 15672,
            'username': 'guest',
            'password': 'guest'
        }
        
        # 创建测试执行器
        self.executor = FaultTestExecutor(self.rabbitmq_config)
    
    def create_sample_scenarios(self) -> List[TestScenario]:
        """创建示例测试场景"""
        scenarios = []
        
        # 场景1: CPU过载测试
        cpu_fault = FaultInjection(
            fault_type=FaultType.CPU_OVERLOAD,
            severity=FaultSeverity.HIGH,
            target_component='system',
            duration_seconds=30,
            parameters={'target_percentage': 95}
        )
        
        cpu_scenario = TestScenario(
            name="CPU过载测试",
            description="测试系统在CPU过载情况下的响应和恢复能力",
            fault_injections=[cpu_fault],
            expected_behavior={
                'should_detect_fault': True,
                'should_recover': True,
                'max_recovery_time': 60
            },
            timeout_seconds=120
        )
        scenarios.append(cpu_scenario)
        
        # 场景2: 内存压力测试
        memory_fault = FaultInjection(
            fault_type=FaultType.MEMORY_OVERLOAD,
            severity=FaultSeverity.HIGH,
            target_component='system',
            duration_seconds=30,
            parameters={'target_percentage': 90}
        )
        
        memory_scenario = TestScenario(
            name="内存压力测试",
            description="测试系统在内存压力情况下的响应和恢复能力",
            fault_injections=[memory_fault],
            expected_behavior={
                'should_detect_fault': True,
                'should_recover': True,
                'max_recovery_time': 60
            },
            timeout_seconds=120
        )
        scenarios.append(memory_scenario)
        
        # 场景3: 网络延迟测试
        latency_fault = FaultInjection(
            fault_type=FaultType.HIGH_LATENCY,
            severity=FaultSeverity.MEDIUM,
            target_component='network',
            duration_seconds=30,
            parameters={'interface': 'eth0', 'delay_ms': 2000}
        )
        
        latency_scenario = TestScenario(
            name="网络延迟测试",
            description="测试系统在网络高延迟情况下的响应能力",
            fault_injections=[latency_fault],
            expected_behavior={
                'should_detect_fault': True,
                'should_recover': True,
                'max_recovery_time': 30
            },
            timeout_seconds=90
        )
        scenarios.append(latency_scenario)
        
        # 场景4: 队列溢出测试
        queue_fault = FaultInjection(
            fault_type=FaultType.RABBITMQ_QUEUE_FULL,
            severity=FaultSeverity.CRITICAL,
            target_component='rabbitmq',
            duration_seconds=60,
            parameters={'queue_name': 'fault_test_queue', 'message_count': 5000}
        )
        
        queue_scenario = TestScenario(
            name="队列溢出测试",
            description="测试RabbitMQ队列溢出情况下的处理能力",
            fault_injections=[queue_fault],
            expected_behavior={
                'should_detect_fault': True,
                'should_recover': True,
                'max_recovery_time': 120
            },
            timeout_seconds=180
        )
        scenarios.append(queue_scenario)
        
        # 场景5: 复合故障测试
        composite_faults = [
            FaultInjection(
                fault_type=FaultType.CPU_OVERLOAD,
                severity=FaultSeverity.MEDIUM,
                target_component='system',
                duration_seconds=20,
                parameters={'target_percentage': 70}
            ),
            FaultInjection(
                fault_type=FaultType.PACKET_LOSS,
                severity=FaultSeverity.MEDIUM,
                target_component='network',
                duration_seconds=20,
                parameters={'interface': 'eth0', 'loss_percentage': 30}
            )
        ]
        
        composite_scenario = TestScenario(
            name="复合故障测试",
            description="测试系统在多重故障同时发生时的处理能力",
            fault_injections=composite_faults,
            expected_behavior={
                'should_detect_fault': True,
                'should_recover': True,
                'max_recovery_time': 90
            },
            timeout_seconds=150
        )
        scenarios.append(composite_scenario)
        
        return scenarios
    
    def demo_single_scenario(self, scenario: TestScenario):
        """演示单个测试场景"""
        print(f"\n{'='*60}")
        print(f"执行测试场景: {scenario.name}")
        print(f"{'='*60}")
        
        # 执行测试
        execution = self.executor.execute_scenario(scenario)
        
        # 显示结果
        self._display_execution_result(execution)
        
        return execution
    
    def _display_execution_result(self, execution: TestExecution):
        """显示执行结果"""
        duration = (execution.end_time - execution.start_time).total_seconds()
        
        print(f"\n执行结果:")
        print(f"  场景名称: {execution.scenario_name}")
        print(f"  执行状态: {execution.status.value}")
        print(f"  执行时长: {duration:.2f}秒")
        
        if execution.errors:
            print(f"  错误信息: {execution.errors}")
        
        print(f"\n阶段执行情况:")
        for phase, status in execution.phases.items():
            print(f"  {phase}: {status.value}")
        
        if execution.results:
            print(f"\n详细结果:")
            for phase, result in execution.results.items():
                if isinstance(result, dict):
                    print(f"  {phase}: {result.get('success', False)}")
    
    def demo_comprehensive_testing(self):
        """演示综合测试"""
        print("RabbitMQ 故障演练与测试系统演示")
        print("=" * 80)
        
        # 创建测试场景
        scenarios = self.create_sample_scenarios()
        
        print(f"创建了 {len(scenarios)} 个测试场景")
        
        # 让用户选择执行的场景
        print("\n可用的测试场景:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario.name} - {scenario.description}")
        
        print("\n建议执行顺序:")
        print("  1. CPU过载测试 (简单故障)")
        print("  2. 网络延迟测试 (网络相关)")
        print("  3. 内存压力测试 (资源相关)")
        print("  4. 队列溢出测试 (RabbitMQ相关)")
        print("  5. 复合故障测试 (复杂场景)")
        
        # 执行选择的场景
        selected_scenarios = [scenarios[0], scenarios[2], scenarios[3]]  # 默认选择前3个
        
        try:
            for scenario in selected_scenarios:
                self.demo_single_scenario(scenario)
                
                # 询问是否继续下一个场景
                response = input("\n是否继续下一个场景？(y/N): ").strip().lower()
                if response != 'y':
                    break
        
        except KeyboardInterrupt:
            print("\n测试被用户中断")
        
        # 显示测试历史
        print(f"\n{'='*50}")
        print("测试执行历史")
        print(f"{'='*50}")
        
        history = self.executor.get_execution_history(limit=5)
        for i, exec_record in enumerate(history, 1):
            print(f"{i}. {exec_record['scenario_name']}: {exec_record['status']}")
    
    def demo_stress_testing(self, iterations: int = 3):
        """演示压力测试"""
        print(f"\n{'='*60}")
        print(f"压力测试演示 - {iterations} 次迭代")
        print(f"{'='*60}")
        
        # 选择一个中等复杂度的场景进行压力测试
        cpu_scenario = TestScenario(
            name="CPU压力循环测试",
            description="连续执行CPU过载测试以验证系统稳定性",
            fault_injections=[
                FaultInjection(
                    fault_type=FaultType.CPU_OVERLOAD,
                    severity=FaultSeverity.MEDIUM,
                    target_component='system',
                    duration_seconds=15,
                    parameters={'target_percentage': 80}
                )
            ],
            expected_behavior={
                'should_detect_fault': True,
                'should_recover': True,
                'max_recovery_time': 30
            },
            timeout_seconds=60
        )
        
        passed_tests = 0
        failed_tests = 0
        
        for i in range(iterations):
            print(f"\n第 {i+1}/{iterations} 次压力测试")
            print("-" * 30)
            
            try:
                execution = self.executor.execute_scenario(cpu_scenario)
                
                if execution.status == TestStatus.PASSED:
                    passed_tests += 1
                    print("✓ 测试通过")
                else:
                    failed_tests += 1
                    print("✗ 测试失败")
                    
            except Exception as e:
                failed_tests += 1
                print(f"✗ 测试异常: {e}")
            
            # 测试间隔
            if i < iterations - 1:
                print("等待系统恢复...")
                time.sleep(10)
        
        print(f"\n压力测试完成:")
        print(f"  总测试数: {iterations}")
        print(f"  通过测试: {passed_tests}")
        print(f"  失败测试: {failed_tests}")
        print(f"  成功率: {(passed_tests/iterations)*100:.1f}%")


def main():
    """主函数"""
    demo = FaultInjectionDemo()
    
    try:
        print("选择演示模式:")
        print("1. 综合测试演示")
        print("2. 压力测试演示")
        print("3. 自定义场景测试")
        
        choice = input("请选择 (1-3): ").strip()
        
        if choice == '1':
            demo.demo_comprehensive_testing()
        elif choice == '2':
            demo.demo_stress_testing(iterations=3)
        elif choice == '3':
            # 让用户创建自定义场景
            print("自定义场景测试功能待实现")
        else:
            print("无效选择，执行综合测试演示")
            demo.demo_comprehensive_testing()
            
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示执行出错: {e}")


if __name__ == "__main__":
    main()