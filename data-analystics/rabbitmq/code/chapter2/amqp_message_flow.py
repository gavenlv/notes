#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第2章：AMQP协议深入理解
AMQP消息流分析和监控工具

功能：
- 监控AMQP连接状态
- 跟踪消息路由路径
- 分析消息性能指标
- 调试消息流问题
- 生成消息流报告

作者：RabbitMQ学习教程
创建时间：2025年11月
"""

import pika
import time
import json
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import queue


@dataclass
class MessageFlow:
    """消息流记录"""
    message_id: str
    timestamp: float
    event_type: str  # publish, route, consume, ack, reject, expire
    source: str  # publish, queue, exchange
    destination: str  # exchange, queue, consumer
    routing_key: str
    properties: Dict[str, Any]
    payload_size: int
    processing_time: Optional[float] = None


@dataclass
class ConnectionStats:
    """连接统计信息"""
    connection_id: str
    created_time: float
    channel_count: int
    message_count: int
    error_count: int
    last_activity: float
    status: str  # connected, disconnected, error


class AMQPFlowAnalyzer:
    """AMQP消息流分析器"""
    
    def __init__(self, host='localhost', port=5672, max_history=10000):
        self.host = host
        self.port = port
        self.max_history = max_history
        self.connection = None
        self.channel = None
        
        # 消息流历史
        self.message_flows: deque = deque(maxlen=max_history)
        self.connection_stats: Dict[str, ConnectionStats] = {}
        
        # 性能统计
        self.performance_metrics = {
            'total_messages': 0,
            'total_throughput': 0,
            'average_latency': 0,
            'error_rate': 0,
            'connections_active': 0
        }
        
        # 监控线程
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """建立连接"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    heartbeat=30,
                    blocked_connection_timeout=10,
                    connection_attempts=3,
                    retry_delay=5
                )
            )
            self.channel = self.connection.channel()
            
            # 设置连接状态回调
            self.connection.add_on_connection_blocked_callback(self._on_connection_blocked)
            self.connection.add_on_connection_unblocked_callback(self._on_connection_unblocked)
            self.connection.add_on_connection_closed_callback(self._on_connection_closed)
            
            self.logger.info(f"✅ 连接到 RabbitMQ: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 连接失败: {e}")
            return False
    
    def _on_connection_blocked(self, connection):
        """连接被阻塞回调"""
        self.logger.warning("⚠️ 连接被阻塞")
        self._update_connection_stats('blocked')
    
    def _on_connection_unblocked(self, connection):
        """连接解除阻塞回调"""
        self.logger.info("✅ 连接已解除阻塞")
        self._update_connection_stats('connected')
    
    def _on_connection_closed(self, connection, reply_code, reply_text):
        """连接关闭回调"""
        self.logger.warning(f"🔌 连接关闭: {reply_code} - {reply_text}")
        self._update_connection_stats('disconnected', error=True)
    
    def _update_connection_stats(self, status: str, error: bool = False):
        """更新连接统计"""
        if self.connection:
            conn_id = id(self.connection)
            
            if conn_id in self.connection_stats:
                stats = self.connection_stats[conn_id]
                stats.status = status
                stats.last_activity = time.time()
                if error:
                    stats.error_count += 1
            else:
                stats = ConnectionStats(
                    connection_id=str(conn_id),
                    created_time=time.time(),
                    channel_count=1,
                    message_count=0,
                    error_count=1 if error else 0,
                    last_activity=time.time(),
                    status=status
                )
                self.connection_stats[conn_id] = stats
    
    def setup_monitoring_queues(self):
        """设置监控队列"""
        # 创建监控交换机
        self.channel.exchange_declare(
            exchange='monitoring_exchange',
            exchange_type='topic',
            durable=True,
            auto_delete=False
        )
        
        # 创建监控队列
        monitoring_queues = {
            'flow_tracking_queue': {'durable': True, 'auto_delete': False},
            'performance_metrics_queue': {'durable': True, 'auto_delete': False},
            'connection_alerts_queue': {'durable': True, 'auto_delete': False}
        }
        
        for queue_name, args in monitoring_queues.items():
            self.channel.queue_declare(queue=queue_name, **args)
            self.channel.queue_bind(
                exchange='monitoring_exchange',
                queue=queue_name,
                routing_key=f'monitor.{queue_name}'
            )
        
        self.logger.info("✅ 监控队列创建完成")
    
    def instrument_producer(self, exchange_name: str = '', queue_name: str = None):
        """为生产者添加监控"""
        
        def instrumented_publish(method, properties, body):
            """被监控的发布方法"""
            try:
                # 记录发布事件
                flow = MessageFlow(
                    message_id=properties.message_id or f"msg-{int(time.time() * 1000)}",
                    timestamp=time.time(),
                    event_type='publish',
                    source='producer',
                    destination=exchange_name or queue_name,
                    routing_key=properties.correlation_id or '',
                    properties=asdict(properties),
                    payload_size=len(body)
                )
                
                self.message_flows.append(flow)
                self.performance_metrics['total_messages'] += 1
                
                self.logger.info(f"📤 监控发布: {flow.message_id}")
                
                # 调用原始发布方法
                return method()
                
            except Exception as e:
                self.logger.error(f"❌ 发布监控失败: {e}")
                return method()
        
        return instrumented_publish
    
    def track_message_routing(self, exchange_name: str, routing_key: str, properties: pika.BasicProperties):
        """跟踪消息路由"""
        flow = MessageFlow(
            message_id=properties.message_id or f"route-{int(time.time() * 1000)}",
            timestamp=time.time(),
            event_type='route',
            source=exchange_name,
            destination=routing_key,
            routing_key=routing_key,
            properties=asdict(properties),
            payload_size=0
        )
        
        self.message_flows.append(flow)
        self.logger.info(f"🔄 跟踪路由: {exchange_name} -> {routing_key}")
    
    def track_message_consumption(self, channel, method, properties, body):
        """跟踪消息消费"""
        flow = MessageFlow(
            message_id=properties.message_id or f"cons-{int(time.time() * 1000)}",
            timestamp=time.time(),
            event_type='consume',
            source=method.routing_key,
            destination='consumer',
            routing_key=method.routing_key,
            properties=asdict(properties),
            payload_size=len(body)
        )
        
        self.message_flows.append(flow)
        self.performance_metrics['total_messages'] += 1
        
        self.logger.info(f"📥 跟踪消费: {flow.message_id}")
        
        return channel.basic_consume(
            queue=method.routing_key,
            on_message_callback=self._consume_with_tracking,
            auto_ack=False
        )
    
    def _consume_with_tracking(self, channel, method, properties, body):
        """带跟踪的消费回调"""
        start_time = time.time()
        
        try:
            # 记录消费事件
            flow = MessageFlow(
                message_id=properties.message_id or f"consumed-{int(time.time() * 1000)}",
                timestamp=time.time(),
                event_type='consume',
                source=method.routing_key,
                destination='consumer',
                routing_key=method.routing_key,
                properties=asdict(properties),
                payload_size=len(body)
            )
            
            self.message_flows.append(flow)
            
            # 模拟消息处理
            time.sleep(0.1)  # 模拟处理时间
            
            processing_time = time.time() - start_time
            flow.processing_time = processing_time
            
            # 确认消息
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
            # 记录确认事件
            ack_flow = MessageFlow(
                message_id=f"{flow.message_id}_ack",
                timestamp=time.time(),
                event_type='ack',
                source='consumer',
                destination=method.routing_key,
                routing_key=method.routing_key,
                properties=asdict(properties),
                payload_size=len(body),
                processing_time=processing_time
            )
            
            self.message_flows.append(ack_flow)
            
            self.logger.info(f"✅ 消费确认: {flow.message_id} (处理时间: {processing_time:.3f}s)")
            
        except Exception as e:
            self.logger.error(f"❌ 消费失败: {e}")
            # 拒绝消息
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # 记录拒绝事件
            nack_flow = MessageFlow(
                message_id=f"{flow.message_id}_nack",
                timestamp=time.time(),
                event_type='reject',
                source='consumer',
                destination=method.routing_key,
                routing_key=method.routing_key,
                properties=asdict(properties),
                payload_size=len(body)
            )
            
            self.message_flows.append(nack_flow)
    
    def analyze_message_flow(self, message_id: str = None, time_window: int = 60):
        """分析消息流"""
        current_time = time.time()
        start_time = current_time - time_window
        
        # 过滤消息流
        flows = [
            flow for flow in self.message_flows
            if flow.timestamp >= start_time and
               (message_id is None or message_id in flow.message_id)
        ]
        
        if not flows:
            self.logger.warning("⚠️ 未找到符合条件的消息流")
            return None
        
        # 分析统计
        analysis = {
            'total_events': len(flows),
            'time_window': time_window,
            'event_types': defaultdict(int),
            'source_distribution': defaultdict(int),
            'destination_distribution': defaultdict(int),
            'routing_keys': defaultdict(int),
            'processing_times': [],
            'payload_sizes': [],
            'latency_analysis': {}
        }
        
        for flow in flows:
            analysis['event_types'][flow.event_type] += 1
            analysis['source_distribution'][flow.source] += 1
            analysis['destination_distribution'][flow.destination] += 1
            analysis['routing_keys'][flow.routing_key] += 1
            
            if flow.processing_time:
                analysis['processing_times'].append(flow.processing_time)
            
            if flow.payload_size > 0:
                analysis['payload_sizes'].append(flow.payload_size)
        
        # 计算性能指标
        if analysis['processing_times']:
            analysis['avg_processing_time'] = sum(analysis['processing_times']) / len(analysis['processing_times'])
            analysis['max_processing_time'] = max(analysis['processing_times'])
            analysis['min_processing_time'] = min(analysis['processing_times'])
        
        if analysis['payload_sizes']:
            analysis['avg_payload_size'] = sum(analysis['payload_sizes']) / len(analysis['payload_sizes'])
            analysis['total_payload_size'] = sum(analysis['payload_sizes'])
        
        analysis['throughput'] = len(flows) / time_window
        
        return analysis
    
    def generate_flow_report(self, analysis: Dict[str, Any]):
        """生成消息流报告"""
        print("\n📊 AMQP消息流分析报告")
        print("=" * 80)
        
        if not analysis:
            print("❌ 无分析数据")
            return
        
        print(f"📅 分析时间窗口: {analysis['time_window']}秒")
        print(f"📈 总事件数: {analysis['total_events']}")
        print(f"⚡ 吞吐量: {analysis['throughput']:.2f} 事件/秒")
        
        # 事件类型分布
        print(f"\n📋 事件类型分布:")
        for event_type, count in analysis['event_types'].items():
            percentage = (count / analysis['total_events']) * 100
            print(f"   {event_type}: {count} ({percentage:.1f}%)")
        
        # 源分布
        print(f"\n📤 消息源分布:")
        for source, count in analysis['source_distribution'].items():
            percentage = (count / analysis['total_events']) * 100
            print(f"   {source}: {count} ({percentage:.1f}%)")
        
        # 目标分布
        print(f"\n📥 消息目标分布:")
        for dest, count in analysis['destination_distribution'].items():
            percentage = (count / analysis['total_events']) * 100
            print(f"   {dest}: {count} ({percentage:.1f}%)")
        
        # 性能分析
        if 'avg_processing_time' in analysis:
            print(f"\n⏱️ 性能分析:")
            print(f"   平均处理时间: {analysis['avg_processing_time']:.3f}秒")
            print(f"   最大处理时间: {analysis['max_processing_time']:.3f}秒")
            print(f"   最小处理时间: {analysis['min_processing_time']:.3f}秒")
        
        if 'avg_payload_size' in analysis:
            print(f"\n📦 负载分析:")
            print(f"   平均负载大小: {analysis['avg_payload_size']:.1f}字节")
            print(f"   总负载大小: {analysis['total_payload_size']:.1f}字节")
        
        # 路由键统计
        print(f"\n🔑 路由键使用统计:")
        for routing_key, count in sorted(analysis['routing_keys'].items(), 
                                       key=lambda x: x[1], reverse=True):
            percentage = (count / analysis['total_events']) * 100
            print(f"   {routing_key}: {count} ({percentage:.1f}%)")
    
    def start_monitoring(self):
        """启动监控"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("🚀 消息流监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("⏹️ 消息流监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 检查连接状态
                if not self.connection or not self.connection.is_open:
                    self.logger.warning("⚠️ 连接已断开，尝试重连...")
                    time.sleep(5)
                    continue
                
                # 更新性能指标
                self._update_performance_metrics()
                
                # 检查异常情况
                self._check_anomalies()
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ 监控循环错误: {e}")
                time.sleep(5)
    
    def _update_performance_metrics(self):
        """更新性能指标"""
        current_time = time.time()
        
        # 活跃连接数
        active_connections = sum(
            1 for stats in self.connection_stats.values()
            if stats.status == 'connected' and 
               current_time - stats.last_activity < 30
        )
        
        self.performance_metrics['connections_active'] = active_connections
        
        # 错误率
        total_errors = sum(stats.error_count for stats in self.connection_stats.values())
        total_operations = self.performance_metrics['total_messages'] + total_errors
        
        if total_operations > 0:
            self.performance_metrics['error_rate'] = total_errors / total_operations
    
    def _check_anomalies(self):
        """检查异常情况"""
        current_time = time.time()
        
        # 检查长时间无活动的连接
        for stats in self.connection_stats.values():
            if (stats.status == 'connected' and 
                current_time - stats.last_activity > 60):
                self.logger.warning(f"⚠️ 连接 {stats.connection_id} 长时间无活动")
    
    def get_connection_info(self):
        """获取连接信息"""
        if not self.connection:
            return None
        
        info = {
            'is_open': self.connection.is_open,
            'is_closed': self.connection.is_closed,
            'has_open_channels': len(self.connection._channels) > 0,
            'socket_timeout': self.connection.socket_timeout,
            'heartbeat': self.connection.heartbeat,
            'connected_time': getattr(self.connection, '_tune_connection', {}).get('start_time')
        }
        
        return info
    
    def run_flow_demonstration(self):
        """运行消息流演示"""
        print("\n🎬 AMQP消息流演示")
        print("=" * 60)
        
        if not self.connect():
            return False
        
        try:
            # 设置监控
            self.setup_monitoring_queues()
            self.start_monitoring()
            
            # 创建测试交换机和队列
            self.channel.exchange_declare(
                exchange='demo_exchange',
                exchange_type='topic',
                durable=True
            )
            
            self.channel.queue_declare(queue='demo_queue', durable=True)
            self.channel.queue_bind(
                exchange='demo_exchange',
                queue='demo_queue',
                routing_key='demo.*'
            )
            
            print("✅ 测试环境设置完成")
            
            # 发送测试消息
            print("\n📤 发送测试消息...")
            for i in range(10):
                properties = pika.BasicProperties(
                    message_id=f'demo-{i}',
                    timestamp=time.time(),
                    priority=i % 3,
                    correlation_id=f'corr-{i}',
                    content_type='application/json'
                )
                
                self.channel.basic_publish(
                    exchange='demo_exchange',
                    routing_key=f'demo.{i % 2}',
                    body=json.dumps({
                        'id': i,
                        'data': f'test_data_{i}',
                        'timestamp': time.time()
                    }),
                    properties=properties
                )
                
                # 跟踪路由
                self.track_message_routing('demo_exchange', f'demo.{i % 2}', properties)
                print(f"   发送消息 {i}: demo.{i % 2}")
                
                time.sleep(0.1)
            
            # 启动消费者
            print("\n📥 启动消息消费...")
            self.channel.basic_consume(
                queue='demo_queue',
                on_message_callback=self._consume_with_tracking,
                auto_ack=False
            )
            
            # 开始消费
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.channel.stop_consuming()
            
            # 等待一些消息处理完成
            time.sleep(2)
            
            # 停止监控
            self.stop_monitoring()
            
            # 分析消息流
            analysis = self.analyze_message_flow(time_window=30)
            if analysis:
                self.generate_flow_report(analysis)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 演示失败: {e}")
            return False
        
        finally:
            self.close()
    
    def close(self):
        """关闭连接"""
        if self.monitoring_active:
            self.stop_monitoring()
            
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.logger.info("🔒 连接已关闭")


def interactive_flow_analysis():
    """交互式消息流分析"""
    print("\n🎯 交互式AMQP消息流分析")
    print("=" * 60)
    
    analyzer = AMQPFlowAnalyzer()
    
    while True:
        print("\n请选择操作:")
        print("1. 启动消息流监控")
        print("2. 运行演示")
        print("3. 分析消息流")
        print("4. 查看连接信息")
        print("5. 查看性能指标")
        print("6. 导出报告")
        print("7. 退出")
        
        choice = input("\n请输入选择 (1-7): ").strip()
        
        if choice == '1':
            if analyzer.connect():
                analyzer.start_monitoring()
                print("✅ 监控已启动，按 Ctrl+C 停止")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    analyzer.stop_monitoring()
                    analyzer.close()
                    print("✅ 监控已停止")
        
        elif choice == '2':
            analyzer.run_flow_demonstration()
        
        elif choice == '3':
            time_window = int(input("请输入分析时间窗口(秒，默认60): ") or "60")
            message_id = input("请输入要分析的消息ID(留空分析所有): ").strip() or None
            
            analysis = analyzer.analyze_message_flow(
                message_id=message_id,
                time_window=time_window
            )
            if analysis:
                analyzer.generate_flow_report(analysis)
        
        elif choice == '4':
            info = analyzer.get_connection_info()
            if info:
                print("\n🔌 连接信息:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ 无连接信息")
        
        elif choice == '5':
            print("\n📊 性能指标:")
            for key, value in analyzer.performance_metrics.items():
                print(f"   {key}: {value}")
        
        elif choice == '6':
            filename = input("请输入文件名: ").strip() or f"flow_report_{int(time.time())}.json"
            analysis = analyzer.analyze_message_flow()
            
            with open(filename, 'w', encoding='utf-8') as f:
                report = {
                    'timestamp': time.time(),
                    'performance_metrics': analyzer.performance_metrics,
                    'analysis': analysis
                }
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 报告已导出到: {filename}")
        
        elif choice == '7':
            print("👋 退出分析")
            break
        
        else:
            print("❌ 无效选择")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AMQP消息流分析器")
    parser.add_argument('--host', default='localhost', help='RabbitMQ主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ端口')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = AMQPFlowAnalyzer(host=args.host, port=args.port)
    
    if args.interactive:
        interactive_flow_analysis()
    elif args.demo:
        analyzer.run_flow_demonstration()
    else:
        # 运行完整分析
        analyzer.run_flow_demonstration()