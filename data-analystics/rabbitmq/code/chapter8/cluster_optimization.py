#!/usr/bin/env python3
"""
第8章：集群优化示例
 RabbitMQ 集群性能优化和配置调优工具
"""

import time
import threading
import json
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import logging
import heapq
import uuid
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class OptimizationType(Enum):
    """优化类型"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RELIABILITY = "reliability"
    MEMORY = "memory"
    BALANCED = "balanced"


class NetworkType(Enum):
    """网络类型"""
    GIGABIT = "gigabit"
    TEN_GIGABIT = "10gigabit"
    INFINIBAND = "infiniband"
    LOCALHOST = "localhost"


@dataclass
class NodeConfig:
    """节点配置"""
    name: str
    host: str
    port: int
    rabbitmq_version: str = "3.8.0"
    erlang_version: str = "23.0"
    cpu_cores: int = 4
    memory_gb: int = 8
    disk_gb: int = 100
    network_type: NetworkType = NetworkType.GIGABIT
    role: str = "disc"  # "disc", "ram"
    management_enabled: bool = True


@dataclass
class ClusterMetrics:
    """集群指标"""
    timestamp: float
    total_nodes: int
    running_nodes: int
    total_queues: int
    total_connections: int
    total_channels: int
    total_messages: int
    ready_messages: int
    unacked_messages: int
    memory_usage_bytes: int
    disk_usage_bytes: int
    cpu_usage_percent: float
    network_io_mbps: float
    cluster_load: float
    queue_depth_avg: float
    message_rate_in: float
    message_rate_out: float


@dataclass
class OptimizationResult:
    """优化结果"""
    optimization_type: str
    before_metrics: ClusterMetrics
    after_metrics: ClusterMetrics
    improvement_percent: float
    applied_settings: Dict[str, Any]
    performance_gain: float
    timestamp: float


class ClusterOptimizer:
    """集群优化器"""
    
    def __init__(self):
        self.node_configs = {}
        self.optimization_history = []
        self.current_metrics = None
        self.optimization_rules = {
            'memory_optimization': self._optimize_memory,
            'cpu_optimization': self._optimize_cpu,
            'disk_optimization': self._optimize_disk,
            'network_optimization': self._optimize_network,
            'queue_optimization': self._optimize_queues,
            'connection_optimization': self._optimize_connections,
            'cluster_balance': self._balance_cluster_load
        }
    
    def add_node(self, node_config: NodeConfig):
        """添加节点"""
        self.node_configs[node_config.name] = node_config
        print(f"添加节点: {node_config.name} ({node_config.host}:{node_config.port})")
    
    def analyze_current_state(self) -> Dict[str, Any]:
        """分析当前集群状态"""
        if not self.node_configs:
            return {'error': '没有配置节点'}
        
        analysis = {
            'cluster_info': {
                'total_nodes': len(self.node_configs),
                'roles': self._analyze_node_roles(),
                'resource_distribution': self._analyze_resource_distribution(),
                'network_topology': self._analyze_network_topology()
            },
            'performance_baseline': {
                'estimated_throughput': self._estimate_throughput(),
                'estimated_latency': self._estimate_latency(),
                'max_capacity': self._estimate_max_capacity()
            },
            'recommendations': self._generate_cluster_recommendations()
        }
        
        return analysis
    
    def _analyze_node_roles(self) -> Dict[str, int]:
        """分析节点角色分布"""
        roles = defaultdict(int)
        for config in self.node_configs.values():
            roles[config.role] += 1
        return dict(roles)
    
    def _analyze_resource_distribution(self) -> Dict[str, Any]:
        """分析资源分布"""
        total_cpu = sum(node.cpu_cores for node in self.node_configs.values())
        total_memory = sum(node.memory_gb for node in self.node_configs.values())
        total_disk = sum(node.disk_gb for node in self.node_configs.values())
        
        return {
            'cpu_distribution': [node.cpu_cores for node in self.node_configs.values()],
            'memory_distribution': [node.memory_gb for node in self.node_configs.values()],
            'disk_distribution': [node.disk_gb for node in self.node_configs.values()],
            'avg_cpu_per_node': total_cpu / len(self.node_configs),
            'avg_memory_per_node': total_memory / len(self.node_configs),
            'avg_disk_per_node': total_disk / len(self.node_configs)
        }
    
    def _analyze_network_topology(self) -> Dict[str, Any]:
        """分析网络拓扑"""
        network_types = defaultdict(int)
        for config in self.node_configs.values():
            network_types[config.network_type.value] += 1
        
        return {
            'network_types': dict(network_types),
            'mixed_networks': len(set(config.network_type for config in self.node_configs.values())) > 1
        }
    
    def _estimate_throughput(self) -> float:
        """估算集群吞吐量"""
        total_cpu = sum(node.cpu_cores for node in self.node_configs.values())
        total_memory = sum(node.memory_gb for node in self.node_configs.values())
        
        # 基于CPU和内存估算吞吐量
        cpu_factor = min(total_cpu / 8, 1.0)  # 标准化到8核心
        memory_factor = min(total_memory / 32, 1.0)  # 标准化到32GB
        
        # 基础吞吐量估算：每个CPU核心约1000消息/秒
        base_throughput = total_cpu * 1000
        optimized_throughput = base_throughput * cpu_factor * memory_factor
        
        return optimized_throughput
    
    def _estimate_latency(self) -> float:
        """估算集群延迟"""
        # 基于网络类型估算基础延迟
        network_latencies = {
            NetworkType.LOCALHOST: 0.001,    # 1ms
            NetworkType.GIGABIT: 0.010,      # 10ms
            NetworkType.TEN_GIGABIT: 0.005,  # 5ms
            NetworkType.INFINIBAND: 0.001    # 1ms
        }
        
        # 计算加权平均延迟
        total_weight = 0
        weighted_latency = 0
        
        for config in self.node_configs.values():
            weight = config.cpu_cores * config.memory_gb  # CPU和内存作为权重
            latency = network_latencies[config.network_type]
            weighted_latency += weight * latency
            total_weight += weight
        
        avg_latency = weighted_latency / total_weight if total_weight > 0 else 0.1
        
        # 添加节点间通信延迟
        node_communication_factor = max(1.0, (len(self.node_configs) - 1) * 0.1)
        
        return avg_latency * node_communication_factor
    
    def _estimate_max_capacity(self) -> Dict[str, int]:
        """估算集群最大容量"""
        total_memory = sum(node.memory_gb for node in self.node_configs.values())
        total_disk = sum(node.disk_gb for node in self.node_configs.values())
        
        # 基于内存和磁盘估算容量
        # 假设每GB内存可存储约10万条消息（1KB大小）
        memory_capacity = total_memory * 100000
        
        # 假设每GB磁盘可存储约100万条消息
        disk_capacity = total_disk * 1000000
        
        return {
            'memory_based_capacity': memory_capacity,
            'disk_based_capacity': disk_capacity,
            'max_safe_capacity': min(memory_capacity, disk_capacity)
        }
    
    def _generate_cluster_recommendations(self) -> List[str]:
        """生成集群建议"""
        recommendations = []
        
        # 检查节点数量
        if len(self.node_configs) < 3:
            recommendations.append("建议至少部署3个节点以保证高可用性")
        
        # 检查角色分布
        roles = self._analyze_node_roles()
        if roles.get('ram', 0) > len(self.node_configs) * 0.5:
            recommendations.append("RAM节点比例过高，建议增加磁盘节点")
        
        if roles.get('disc', 0) == len(self.node_configs):
            recommendations.append("所有节点都是磁盘节点，可考虑部分节点改为RAM以提高性能")
        
        # 检查资源均衡
        resource_dist = self._analyze_resource_distribution()
        cpu_variance = statistics.variance(resource_dist['cpu_distribution'])
        memory_variance = statistics.variance(resource_dist['memory_distribution'])
        
        if cpu_variance > 2:
            recommendations.append("CPU配置不均衡，建议统一节点配置")
        
        if memory_variance > 4:
            recommendations.append("内存配置不均衡，建议统一节点配置")
        
        # 检查网络类型
        topology = self._analyze_network_topology()
        if topology['mixed_networks']:
            recommendations.append("混合网络类型可能影响性能，建议统一网络规格")
        
        return recommendations
    
    def optimize_cluster(self, 
                        optimization_type: OptimizationType,
                        target_improvement: float = 0.2,
                        apply_settings: bool = True) -> OptimizationResult:
        """优化集群"""
        print(f"开始{optimization_type.value}优化...")
        
        # 获取优化前指标
        before_metrics = self._collect_cluster_metrics()
        
        # 选择优化策略
        strategies = self._get_optimization_strategies(optimization_type)
        applied_settings = {}
        
        print(f"应用优化策略: {', '.join(strategies.keys())}")
        
        # 应用优化设置
        for strategy_name, strategy_func in strategies.items():
            settings = strategy_func(target_improvement)
            applied_settings.update(settings)
            print(f"  - {strategy_name}: {settings}")
        
        # 模拟等待优化生效
        time.sleep(2)
        
        # 获取优化后指标
        after_metrics = self._collect_cluster_metrics()
        
        # 计算改进幅度
        improvement_percent = self._calculate_improvement(before_metrics, after_metrics)
        performance_gain = after_metrics.message_rate_in - before_metrics.message_rate_in
        
        result = OptimizationResult(
            optimization_type=optimization_type.value,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement_percent=improvement_percent,
            applied_settings=applied_settings,
            performance_gain=performance_gain,
            timestamp=time.time()
        )
        
        self.optimization_history.append(result)
        
        print(f"✅ {optimization_type.value}优化完成")
        print(f"  性能提升: {improvement_percent:.1%}")
        print(f"  吞吐量提升: {performance_gain:.0f} 消息/秒")
        print()
        
        return result
    
    def _get_optimization_strategies(self, opt_type: OptimizationType) -> Dict[str, Callable]:
        """获取优化策略"""
        strategies = {}
        
        if opt_type == OptimizationType.THROUGHPUT:
            strategies.update({
                'memory_optimization': self._optimize_memory,
                'cpu_optimization': self._optimize_cpu,
                'network_optimization': self._optimize_network,
                'queue_optimization': self._optimize_queues
            })
        elif opt_type == OptimizationType.LATENCY:
            strategies.update({
                'network_optimization': self._optimize_network,
                'connection_optimization': self._optimize_connections,
                'cluster_balance': self._balance_cluster_load
            })
        elif opt_type == OptimizationType.RELIABILITY:
            strategies.update({
                'disk_optimization': self._optimize_disk,
                'cluster_balance': self._balance_cluster_load,
                'queue_optimization': self._optimize_queues
            })
        elif opt_type == OptimizationType.MEMORY:
            strategies.update({
                'memory_optimization': self._optimize_memory,
                'queue_optimization': self._optimize_queues
            })
        elif opt_type == OptimizationType.BALANCED:
            strategies.update(self.optimization_rules)
        
        return strategies
    
    def _optimize_memory(self, target_improvement: float) -> Dict[str, Any]:
        """内存优化"""
        settings = {
            'vm_memory_high_watermark': 0.7,  # 降低内存水位
            'vm_memory_calculation_strategy': 'rss',  # 使用RSS计算
            'disk_free_limit': 100000000,  # 100MB磁盘限制
            'queue_index_embed_messages': True,  # 嵌入消息到索引
            'lazy_queue_persistent': False  # 禁用懒队列持久化
        }
        
        print(f"内存优化: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _optimize_cpu(self, target_improvement: float) -> Dict[str, Any]:
        """CPU优化"""
        settings = {
            'process_limit': 1000,  # 增加进程限制
            'max_connections': 2000,  # 增加连接限制
            'heartbeat': 30,  # 延长心跳间隔
            'connection_backlog': 50,  # 增加连接积压
            'channel_max': 1000,  # 增加通道限制
            'use_cpu_quota': False  # 禁用CPU配额
        }
        
        print(f"CPU优化: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _optimize_disk(self, target_improvement: float) -> Dict[str, Any]:
        """磁盘优化"""
        settings = {
            'disk_free_limit': 1000000000,  # 1GB磁盘限制
            'disk_monitor_interval': 5000,  # 5秒监控间隔
            'queue_index_embed_messages': False,  # 不嵌入消息
            'msg_store_file_size': 16777216,  # 16MB文件大小
            'lazy_queue_persistent': True,  # 启用懒队列
            'lazy_queue_use_disk': True  # 使用磁盘存储
        }
        
        print(f"磁盘优化: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _optimize_network(self, target_improvement: float) -> Dict[str, Any]:
        """网络优化"""
        settings = {
            'network_frame_max': 131072,  # 128KB最大帧
            'network_handshake_timeout': 10000,  # 10秒握手超时
            'network_server_properties': {
                'capabilities': ['connection.blocked', 'authentication_failure_close'],
                'product': 'RabbitMQ',
                'version': '3.8.0',
                'platform': 'Erlang/OTP',
                'copyright': 'Copyright (C) 2007-2023 Pivotal Software, Inc.',
                'information': 'Licensed under the MPL 2.0. Website: https://rabbitmq.com'
            }
        }
        
        print(f"网络优化: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _optimize_queues(self, target_improvement: float) -> Dict[str, Any]:
        """队列优化"""
        settings = {
            'default_queue_type': 'classic',  # 使用经典队列
            'queue_master_locator': 'client-local',  # 客户端本地定位
            'mirroring_sync_batch_size': 100,  # 镜像同步批大小
            'classic_queue_mirroring_sync_timeout': 60000,  # 60秒同步超时
            'lazy_queue_threshold': 10000,  # 10000条消息启用懒队列
            'dead_letter_exchange': 'dlx',  # 启用死信交换
            'dead_letter_routing_key': '#'  # 死信路由键
        }
        
        print(f"队列优化: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _optimize_connections(self, target_improvement: float) -> Dict[str, Any]:
        """连接优化"""
        settings = {
            'connection_max_channels': 500,  # 最大通道数
            'channel_keepalive_duration': 2000,  # 2秒通道保活
            'heartbeat_timeout': 30,  # 30秒心跳超时
            'connection_timeout': 30000,  # 30秒连接超时
            'channel_flow_control': True,  # 启用通道流控制
            'channel_operation_timeout': 15000  # 15秒操作超时
        }
        
        print(f"连接优化: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _balance_cluster_load(self, target_improvement: float) -> Dict[str, Any]:
        """平衡集群负载"""
        settings = {
            'queue_leader_locator': 'min-masters',  # 最少主节点
            'classic_queue_mirroring_master_policy': 'exactly',
            'mirroring_parameters': 'queues with policy',
            'cluster_formation_target': 3,  # 目标3节点集群
            'force_peer_down_on_failed_health_check': True,  # 健康检查失败时强制下线
            'health_check_timeout': 30000  # 30秒健康检查超时
        }
        
        print(f"负载均衡: 预计提升 {target_improvement * 100:.0f}% 性能")
        return settings
    
    def _collect_cluster_metrics(self) -> ClusterMetrics:
        """收集集群指标"""
        # 模拟收集指标
        return ClusterMetrics(
            timestamp=time.time(),
            total_nodes=len(self.node_configs),
            running_nodes=len(self.node_configs),
            total_queues=100,
            total_connections=500,
            total_channels=1000,
            total_messages=10000,
            ready_messages=8000,
            unacked_messages=2000,
            memory_usage_bytes=2 * 1024 * 1024 * 1024,  # 2GB
            disk_usage_bytes=20 * 1024 * 1024 * 1024,  # 20GB
            cpu_usage_percent=45.5,
            network_io_mbps=100.0,
            cluster_load=0.65,
            queue_depth_avg=100.0,
            message_rate_in=5000.0,
            message_rate_out=4800.0
        )
    
    def _calculate_improvement(self, before: ClusterMetrics, after: ClusterMetrics) -> float:
        """计算改进幅度"""
        # 基于吞吐量改进计算
        throughput_improvement = (after.message_rate_in - before.message_rate_in) / before.message_rate_in
        
        # 基于延迟改进计算（延迟降低是改进）
        latency_improvement = (before.cpu_usage_percent - after.cpu_usage_percent) / 100.0
        
        # 综合评分
        overall_improvement = (throughput_improvement + latency_improvement) / 2
        
        return max(0.0, overall_improvement)
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """获取优化历史"""
        return self.optimization_history
    
    def generate_optimization_report(self) -> str:
        """生成优化报告"""
        if not self.optimization_history:
            return "没有优化历史记录"
        
        report = []
        report.append("# RabbitMQ 集群优化报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("## 优化历史")
        for result in self.optimization_history:
            report.append(f"### {result.optimization_type.title()}优化")
            report.append(f"- 时间: {datetime.fromtimestamp(result.timestamp).strftime('%H:%M:%S')}")
            report.append(f"- 性能提升: {result.improvement_percent:.1%}")
            report.append(f"- 吞吐量提升: {result.performance_gain:.0f} 消息/秒")
            report.append(f"- 应用设置: {len(result.applied_settings)} 项")
            report.append("")
        
        # 统计信息
        if self.optimization_history:
            total_improvements = [r.improvement_percent for r in self.optimization_history]
            avg_improvement = sum(total_improvements) / len(total_improvements)
            max_improvement = max(total_improvements)
            
            report.append("## 优化统计")
            report.append(f"- 总优化次数: {len(self.optimization_history)}")
            report.append(f"- 平均性能提升: {avg_improvement:.1%}")
            report.append(f"- 最大性能提升: {max_improvement:.1%}")
        
        return "\n".join(report)


class ClusterBenchmarker:
    """集群基准测试器"""
    
    def __init__(self, cluster_optimizer: ClusterOptimizer):
        self.cluster_optimizer = cluster_optimizer
        self.test_results = []
    
    def run_cluster_benchmark(self,
                            test_type: str = "throughput",
                            duration: int = 60,
                            message_count: int = 10000,
                            message_size: int = 1024,
                            concurrent_producers: int = 10,
                            concurrent_consumers: int = 10) -> Dict[str, Any]:
        """运行集群基准测试"""
        print(f"开始集群基准测试:")
        print(f"  测试类型: {test_type}")
        print(f"  持续时间: {duration}秒")
        print(f"  消息数量: {message_count}")
        print(f"  消息大小: {message_size}字节")
        print(f"  并发生产者: {concurrent_producers}")
        print(f"  并发消费者: {concurrent_consumers}")
        print()
        
        start_time = time.time()
        metrics_collection = []
        
        # 模拟基准测试
        def collect_metrics():
            end_time = start_time + duration
            while time.time() < end_time:
                metrics = self._simulate_cluster_metrics()
                metrics_collection.append(metrics)
                time.sleep(1)  # 每秒收集一次
        
        # 启动指标收集
        metrics_thread = threading.Thread(target=collect_metrics)
        metrics_thread.start()
        
        # 模拟测试负载
        self._simulate_test_load(
            test_type, message_count, message_size,
            concurrent_producers, concurrent_consumers
        )
        
        # 等待指标收集完成
        metrics_thread.join()
        
        # 分析结果
        result = self._analyze_benchmark_results(metrics_collection, duration, test_type)
        
        print("✅ 集群基准测试完成:")
        print(f"  总耗时: {duration}秒")
        print(f"  平均吞吐量: {result['avg_throughput']:.2f} 消息/秒")
        print(f"  峰值吞吐量: {result['peak_throughput']:.2f} 消息/秒")
        print(f"  平均延迟: {result['avg_latency']:.4f} 秒")
        print(f"  95%延迟: {result['latency_p95']:.4f} 秒")
        print(f"  错误率: {result['error_rate']:.2%}")
        print(f"  CPU使用率: {result['avg_cpu_usage']:.1f}%")
        print(f"  内存使用率: {result['avg_memory_usage']:.1f}%")
        print()
        
        self.test_results.append(result)
        return result
    
    def _simulate_cluster_metrics(self) -> Dict[str, float]:
        """模拟集群指标"""
        import random
        
        return {
            'timestamp': time.time(),
            'throughput_in': random.uniform(4500, 5500),
            'throughput_out': random.uniform(4400, 5400),
            'latency': random.uniform(0.05, 0.15),
            'cpu_usage': random.uniform(40, 60),
            'memory_usage': random.uniform(60, 80),
            'disk_usage': random.uniform(30, 50),
            'connection_count': random.uniform(450, 550),
            'channel_count': random.uniform(900, 1100),
            'queue_count': 100,
            'message_count': random.uniform(9500, 10500)
        }
    
    def _simulate_test_load(self, 
                          test_type: str,
                          message_count: int,
                          message_size: int,
                          concurrent_producers: int,
                          concurrent_consumers: int):
        """模拟测试负载"""
        import random
        import threading
        
        def producer():
            messages_per_producer = message_count // concurrent_producers
            for i in range(messages_per_producer):
                # 模拟发送延迟
                time.sleep(random.uniform(0.01, 0.05))
                
                # 模拟不同测试类型的负载模式
                if test_type == "burst":
                    if i % 10 == 0:  # 每10条消息爆发
                        time.sleep(random.uniform(0.1, 0.3))
                elif test_type == "sustained":
                    time.sleep(0.02)  # 持续负载
                elif test_type == "high_throughput":
                    time.sleep(random.uniform(0.005, 0.01))  # 高吞吐量
        
        def consumer():
            # 模拟消费延迟
            for i in range(message_count // concurrent_consumers):
                time.sleep(random.uniform(0.01, 0.03))
        
        threads = []
        
        # 启动生产者线程
        for i in range(concurrent_producers):
            thread = threading.Thread(target=producer)
            threads.append(thread)
            thread.start()
        
        # 启动消费者线程
        for i in range(concurrent_consumers):
            thread = threading.Thread(target=consumer)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
    
    def _analyze_benchmark_results(self, 
                                 metrics_collection: List[Dict[str, float]], 
                                 duration: int,
                                 test_type: str) -> Dict[str, Any]:
        """分析基准测试结果"""
        if not metrics_collection:
            return {}
        
        # 计算平均值
        throughputs_in = [m['throughput_in'] for m in metrics_collection]
        throughputs_out = [m['throughput_out'] for m in metrics_collection]
        latencies = [m['latency'] for m in metrics_collection]
        cpu_usages = [m['cpu_usage'] for m in metrics_collection]
        memory_usages = [m['memory_usage'] for m in metrics_collection]
        
        result = {
            'test_type': test_type,
            'duration': duration,
            'avg_throughput': statistics.mean(throughputs_in),
            'peak_throughput': max(throughputs_in),
            'min_throughput': min(throughputs_in),
            'avg_latency': statistics.mean(latencies),
            'latency_p95': self._calculate_percentile(latencies, 95),
            'latency_p99': self._calculate_percentile(latencies, 99),
            'avg_cpu_usage': statistics.mean(cpu_usages),
            'max_cpu_usage': max(cpu_usages),
            'avg_memory_usage': statistics.mean(memory_usages),
            'max_memory_usage': max(memory_usages),
            'error_rate': 0.01,  # 假设1%错误率
            'total_messages': sum(throughputs_in) * duration,
            'stability_score': self._calculate_stability_score(throughputs_in)
        }
        
        return result
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _calculate_stability_score(self, throughputs: List[float]) -> float:
        """计算稳定性评分"""
        if not throughputs:
            return 0.0
        
        mean_throughput = statistics.mean(throughputs)
        variance = statistics.variance(throughputs)
        
        # 稳定性评分：方差越小分数越高
        stability_score = max(0, 100 - (variance / mean_throughput) * 10)
        return min(100, stability_score)
    
    def compare_optimizations(self, 
                            before_optimization: List[OptimizationType],
                            after_optimization: List[OptimizationType]) -> Dict[str, Any]:
        """对比优化效果"""
        print("开始优化前后对比测试...")
        
        # 优化前测试
        print("测试优化前性能...")
        before_results = []
        for opt_type in before_optimization:
            result = self.cluster_optimizer.optimize_cluster(opt_type, apply_settings=False)
            benchmark_result = self.run_cluster_benchmark("throughput", 30, 5000)
            before_results.append({
                'optimization': opt_type.value,
                'benchmark': benchmark_result
            })
        
        # 优化后测试
        print("测试优化后性能...")
        after_results = []
        for opt_type in after_optimization:
            result = self.cluster_optimizer.optimize_cluster(opt_type, apply_settings=True)
            benchmark_result = self.run_cluster_benchmark("throughput", 30, 5000)
            after_results.append({
                'optimization': opt_type.value,
                'benchmark': benchmark_result
            })
        
        # 对比分析
        comparison = self._analyze_optimization_comparison(before_results, after_results)
        
        print("✅ 优化对比测试完成:")
        for opt_name, metrics in comparison.items():
            print(f"  {opt_name}:")
            print(f"    吞吐量提升: {metrics['throughput_improvement']:.1%}")
            print(f"    延迟改善: {metrics['latency_improvement']:.1%}")
            print(f"    CPU优化: {metrics['cpu_optimization']:.1f}%")
        
        return comparison
    
    def _analyze_optimization_comparison(self, 
                                       before_results: List[Dict[str, Any]],
                                       after_results: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """分析优化对比"""
        comparison = {}
        
        for i, (before, after) in enumerate(zip(before_results, after_results)):
            opt_name = after['optimization']
            
            before_benchmark = before['benchmark']
            after_benchmark = after['benchmark']
            
            # 计算各项指标改进
            throughput_improvement = (
                (after_benchmark['avg_throughput'] - before_benchmark['avg_throughput']) 
                / before_benchmark['avg_throughput']
            )
            
            latency_improvement = (
                (before_benchmark['avg_latency'] - after_benchmark['avg_latency'])
                / before_benchmark['avg_latency']
            )
            
            cpu_optimization = before_benchmark['avg_cpu_usage'] - after_benchmark['avg_cpu_usage']
            
            comparison[opt_name] = {
                'throughput_improvement': throughput_improvement,
                'latency_improvement': latency_improvement,
                'cpu_optimization': cpu_optimization
            }
        
        return comparison


class ClusterOptimizationDemo:
    """集群优化演示"""
    
    def __init__(self):
        self.cluster_optimizer = ClusterOptimizer()
        self.cluster_benchmarker = ClusterBenchmarker(self.cluster_optimizer)
        self._setup_demo_cluster()
    
    def _setup_demo_cluster(self):
        """设置演示集群"""
        # 创建演示节点
        nodes = [
            NodeConfig("node1", "rabbitmq-1.example.com", 5672, 
                      cpu_cores=8, memory_gb=16, disk_gb=200, role="disc"),
            NodeConfig("node2", "rabbitmq-2.example.com", 5672, 
                      cpu_cores=8, memory_gb=16, disk_gb=200, role="disc"),
            NodeConfig("node3", "rabbitmq-3.example.com", 5672, 
                      cpu_cores=4, memory_gb=8, disk_gb=100, role="ram"),
            NodeConfig("node4", "rabbitmq-4.example.com", 5672, 
                      cpu_cores=4, memory_gb=8, disk_gb=100, role="ram")
        ]
        
        for node in nodes:
            self.cluster_optimizer.add_node(node)
        
        print(f"✅ 演示集群已设置: {len(nodes)} 个节点")
        print()
    
    def demonstrate_cluster_analysis(self):
        """演示集群分析"""
        print("=== 集群状态分析演示 ===")
        print()
        
        # 分析当前状态
        analysis = self.cluster_optimizer.analyze_current_state()
        
        print("📊 集群信息:")
        cluster_info = analysis['cluster_info']
        print(f"  总节点数: {cluster_info['total_nodes']}")
        print(f"  角色分布: {cluster_info['roles']}")
        
        print("\n💻 资源分布:")
        resources = cluster_info['resource_distribution']
        print(f"  CPU分布: {resources['cpu_distribution']}")
        print(f"  内存分布: {resources['memory_distribution']} GB")
        print(f"  平均CPU/节点: {resources['avg_cpu_per_node']:.1f}")
        print(f"  平均内存/节点: {resources['avg_memory_per_node']:.1f} GB")
        
        print("\n🌐 网络拓扑:")
        topology = cluster_info['network_topology']
        print(f"  网络类型: {topology['network_types']}")
        print(f"  混合网络: {topology['mixed_networks']}")
        
        print("\n🚀 性能基线:")
        performance = analysis['performance_baseline']
        print(f"  估算吞吐量: {performance['estimated_throughput']:.0f} 消息/秒")
        print(f"  估算延迟: {performance['estimated_latency']:.4f} 秒")
        print(f"  最大容量: {performance['max_capacity']['max_safe_capacity']:,} 消息")
        
        print("\n💡 优化建议:")
        recommendations = analysis['recommendations']
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print()
        return analysis
    
    def demonstrate_optimization_strategies(self):
        """演示优化策略"""
        print("=== 集群优化策略演示 ===")
        print()
        
        optimization_types = [
            OptimizationType.THROUGHPUT,
            OptimizationType.LATENCY,
            OptimizationType.MEMORY,
            OptimizationType.BALANCED
        ]
        
        results = []
        
        for opt_type in optimization_types:
            print(f"执行 {opt_type.value} 优化...")
            result = self.cluster_optimizer.optimize_cluster(opt_type)
            results.append(result)
        
        # 显示优化历史
        print("📈 优化历史:")
        history = self.cluster_optimizer.get_optimization_history()
        for result in history:
            print(f"  {result.optimization_type}: {result.improvement_percent:.1%} 提升")
        
        print()
        return results
    
    def demonstrate_benchmark_testing(self):
        """演示基准测试"""
        print("=== 集群基准测试演示 ===")
        print()
        
        test_types = ["throughput", "latency", "burst"]
        all_results = []
        
        for test_type in test_types:
            print(f"运行 {test_type} 测试...")
            result = self.cluster_benchmarker.run_cluster_benchmark(
                test_type=test_type,
                duration=30,  # 30秒测试
                message_count=5000,
                message_size=1024,
                concurrent_producers=5,
                concurrent_consumers=5
            )
            all_results.append(result)
        
        # 分析测试结果
        print("📊 测试结果总结:")
        for result in all_results:
            print(f"  {result['test_type']} 测试:")
            print(f"    平均吞吐量: {result['avg_throughput']:.0f} 消息/秒")
            print(f"    平均延迟: {result['avg_latency']:.4f} 秒")
            print(f"    稳定性评分: {result['stability_score']:.1f}/100")
        
        print()
        return all_results
    
    def demonstrate_optimization_comparison(self):
        """演示优化对比"""
        print("=== 优化前后对比演示 ===")
        print()
        
        before_types = [OptimizationType.MEMORY]
        after_types = [OptimizationType.THROUGHPUT, OptimizationType.LATENCY]
        
        comparison = self.cluster_benchmarker.compare_optimizations(
            before_optimization=before_types,
            after_optimization=after_types
        )
        
        print("✅ 优化对比完成")
        print()
        return comparison
    
    def demonstrate_complete_workflow(self):
        """演示完整工作流程"""
        print("🚀 RabbitMQ 集群优化完整流程演示")
        print("=" * 50)
        print()
        
        try:
            # 1. 集群分析
            analysis = self.demonstrate_cluster_analysis()
            
            # 2. 优化策略演示
            optimization_results = self.demonstrate_optimization_strategies()
            
            # 3. 基准测试演示
            benchmark_results = self.demonstrate_benchmark_testing()
            
            # 4. 优化对比演示
            comparison_results = self.demonstrate_optimization_comparison()
            
            # 5. 生成报告
            report = self.cluster_optimizer.generate_optimization_report()
            print("📋 优化报告:")
            print(report)
            
            # 6. 提供最终建议
            print("\n🎯 最终优化建议:")
            if benchmark_results:
                best_test = max(benchmark_results, key=lambda r: r['stability_score'])
                print(f"  最佳稳定性测试: {best_test['test_type']} (评分: {best_test['stability_score']:.1f})")
            
            if optimization_results:
                best_optimization = max(optimization_results, key=lambda r: r.improvement_percent)
                print(f"  最佳优化策略: {best_optimization.optimization_type} (提升: {best_optimization.improvement_percent:.1%})")
            
            print("\n🎉 集群优化演示完成!")
            
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"\n程序执行错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # 运行集群优化演示
    demo = ClusterOptimizationDemo()
    demo.demonstrate_complete_workflow()