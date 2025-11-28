#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第3章：交换机类型深入研究
消息分类与智能路由演示

功能：
- 智能消息分类系统
- 多级路由决策树
- 动态交换机配置
- 消息优先级处理
- 实时路由监控

作者：RabbitMQ学习教程
创建时间：2025年11月
"""

import pika
import time
import json
import threading
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import re


class MessageClassification(Enum):
    """消息分类枚举"""
    SYSTEM = "system"
    BUSINESS = "business"
    AUDIT = "audit"
    ANALYTICS = "analytics"
    SECURITY = "security"
    PERFORMANCE = "performance"


class RouteStrategy(Enum):
    """路由策略枚举"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    PRIORITY_BASED = "priority_based"
    CONTENT_BASED = "content_based"


@dataclass
class ClassificationRule:
    """分类规则"""
    name: str
    pattern: str
    classification: MessageClassification
    priority: int
    weight: float
    enabled: bool = True


@dataclass
class RouteDecision:
    """路由决策"""
    message_id: str
    classification: MessageClassification
    target_exchange: str
    target_queues: List[str]
    priority: int
    processing_time: float
    reason: str


class MessageClassifier:
    """消息分类器"""
    
    def __init__(self):
        self.rules: List[ClassificationRule] = []
        self.statistics = {
            'total_classified': 0,
            'classification_counts': defaultdict(int),
            'rule_hits': defaultdict(int),
            'processing_times': deque(maxlen=1000)
        }
        
        # 初始化默认分类规则
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认分类规则"""
        default_rules = [
            ClassificationRule(
                name="System Logs",
                pattern="system\\..*\\.(error|warning|info)",
                classification=MessageClassification.SYSTEM,
                priority=1,
                weight=1.0
            ),
            ClassificationRule(
                name="Business Events",
                pattern="business\\..*\\.(order|payment|user)",
                classification=MessageClassification.BUSINESS,
                priority=1,
                weight=1.0
            ),
            ClassificationRule(
                name="Security Events",
                pattern="security\\..*\\.(auth|permission|threat)",
                classification=MessageClassification.SECURITY,
                priority=3,
                weight=1.5
            ),
            ClassificationRule(
                name="Analytics Data",
                pattern="analytics\\..*\\.(metric|event|stat)",
                classification=MessageClassification.ANALYTICS,
                priority=1,
                weight=0.8
            ),
            ClassificationRule(
                name="Audit Trail",
                pattern="audit\\..*\\.(create|update|delete|login)",
                classification=MessageClassification.AUDIT,
                priority=2,
                weight=1.2
            )
        ]
        
        self.rules.extend(default_rules)
    
    def add_rule(self, rule: ClassificationRule):
        """添加分类规则"""
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda x: x.priority)
    
    def classify_message(self, message_id: str, routing_key: str, content: str) -> RouteDecision:
        """分类消息"""
        start_time = time.time()
        
        best_rule = None
        best_score = 0
        classification = MessageClassification.SYSTEM
        
        # 应用分类规则
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            if re.match(rule.pattern, routing_key):
                score = rule.priority * rule.weight
                if score > best_score:
                    best_score = score
                    best_rule = rule
                    classification = rule.classification
        
        processing_time = time.time() - start_time
        
        # 更新统计
        self.statistics['total_classified'] += 1
        self.statistics['classification_counts'][classification.value] += 1
        if best_rule:
            self.statistics['rule_hits'][best_rule.name] += 1
        self.statistics['processing_times'].append(processing_time)
        
        # 生成路由决策
        route_decision = self._generate_route_decision(
            message_id, classification, routing_key, processing_time
        )
        
        return route_decision
    
    def _generate_route_decision(self, message_id: str, classification: MessageClassification,
                                routing_key: str, processing_time: float) -> RouteDecision:
        """生成路由决策"""
        
        # 基于分类决定目标交换机和队列
        exchange_mapping = {
            MessageClassification.SYSTEM: ('system.processor', ['system_error', 'system_warning', 'system_info']),
            MessageClassification.BUSINESS: ('business.processor', ['order_processor', 'payment_processor', 'user_processor']),
            MessageClassification.SECURITY: ('security.processor', ['auth_events', 'threat_detection', 'audit_security']),
            MessageClassification.AUDIT: ('audit.processor', ['audit_trail', 'compliance_log']),
            MessageClassification.ANALYTICS: ('analytics.processor', ['metrics_collector', 'event_processor', 'stat_analyzer']),
            MessageClassification.PERFORMANCE: ('performance.processor', ['performance_monitor', 'bottleneck_detector'])
        }
        
        target_exchange, target_queues = exchange_mapping.get(
            classification, ('default.processor', ['default_queue'])
        )
        
        # 提取消息优先级
        priority = self._extract_priority(routing_key, classification)
        
        # 生成路由原因
        reason = f"Classification: {classification.value}, Priority: {priority}"
        
        return RouteDecision(
            message_id=message_id,
            classification=classification,
            target_exchange=target_exchange,
            target_queues=target_queues,
            priority=priority,
            processing_time=processing_time,
            reason=reason
        )
    
    def _extract_priority(self, routing_key: str, classification: MessageClassification) -> int:
        """提取消息优先级"""
        # 基于分类设置默认优先级
        priority_mapping = {
            MessageClassification.SECURITY: 9,
            MessageClassification.SYSTEM: 7,
            MessageClassification.BUSINESS: 5,
            MessageClassification.AUDIT: 6,
            MessageClassification.ANALYTICS: 3,
            MessageClassification.PERFORMANCE: 4
        }
        
        default_priority = priority_mapping.get(classification, 5)
        
        # 如果路由键包含优先级信息，提取它
        priority_pattern = r'priority=(\d+)'
        match = re.search(priority_pattern, routing_key)
        if match:
            return min(int(match.group(1)), 10)
        
        return default_priority
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取分类统计"""
        avg_processing_time = (
            sum(self.statistics['processing_times']) / len(self.statistics['processing_times'])
            if self.statistics['processing_times'] else 0
        )
        
        return {
            'total_classified': self.statistics['total_classified'],
            'classification_distribution': dict(self.statistics['classification_counts']),
            'rule_usage': dict(self.statistics['rule_hits']),
            'average_processing_time': avg_processing_time,
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules if r.enabled])
        }


class MessageClassificationDemo:
    """消息分类演示"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.classifier = MessageClassifier()
        self.route_history: deque = deque(maxlen=100)
        
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
                    heartbeat=30
                )
            )
            self.channel = self.connection.channel()
            
            self.logger.info(f"✅ 连接到 RabbitMQ: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 连接失败: {e}")
            return False
    
    def setup_classification_environment(self):
        """设置分类环境"""
        print("\n🏗️ 设置消息分类环境")
        print("=" * 50)
        
        # 创建分类交换机
        classification_exchanges = [
            'classification.router',
            'system.processor',
            'business.processor',
            'security.processor',
            'analytics.processor',
            'audit.processor',
            'performance.processor'
        ]
        
        for exchange in classification_exchanges:
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type='topic',
                durable=True
            )
        
        # 创建目标处理器队列
        processor_queues = [
            ('system_error', 'system.processor', 'system.*.error'),
            ('system_warning', 'system.processor', 'system.*.warning'),
            ('system_info', 'system.processor', 'system.*.info'),
            ('order_processor', 'business.processor', 'business.*.order.*'),
            ('payment_processor', 'business.processor', 'business.*.payment.*'),
            ('user_processor', 'business.processor', 'business.*.user.*'),
            ('auth_events', 'security.processor', 'security.*.auth.*'),
            ('threat_detection', 'security.processor', 'security.*.threat.*'),
            ('audit_security', 'security.processor', 'security.*.audit.*'),
            ('audit_trail', 'audit.processor', 'audit.*.create'),
            ('compliance_log', 'audit.processor', 'audit.*.delete'),
            ('metrics_collector', 'analytics.processor', 'analytics.*.metric.*'),
            ('event_processor', 'analytics.processor', 'analytics.*.event.*'),
            ('stat_analyzer', 'analytics.processor', 'analytics.*.stat.*'),
            ('performance_monitor', 'performance.processor', 'performance.*.monitor.*'),
            ('bottleneck_detector', 'performance.processor', 'performance.*.bottleneck.*')
        ]
        
        for queue_name, exchange_name, routing_key in processor_queues:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )
        
        print("✅ 分类环境设置完成")
        print(f"   创建了 {len(classification_exchanges)} 个交换机")
        print(f"   创建了 {len(processor_queues)} 个处理器队列")
    
    def generate_test_messages(self) -> List[Dict[str, Any]]:
        """生成测试消息"""
        test_messages = [
            {
                'routing_key': 'system.database.error',
                'content': 'Database connection failed',
                'classification': 'system',
                'expected_queue': 'system_error'
            },
            {
                'routing_key': 'business.order.create priority=8',
                'content': 'New order created: Order-001',
                'classification': 'business',
                'expected_queue': 'order_processor'
            },
            {
                'routing_key': 'security.auth.failure',
                'content': 'Authentication failed for user 12345',
                'classification': 'security',
                'expected_queue': 'auth_events'
            },
            {
                'routing_key': 'audit.user.create',
                'content': 'User 12345 was created',
                'classification': 'audit',
                'expected_queue': 'audit_trail'
            },
            {
                'routing_key': 'analytics.metric.memory',
                'content': 'Memory usage: 85%',
                'classification': 'analytics',
                'expected_queue': 'metrics_collector'
            },
            {
                'routing_key': 'business.payment.process',
                'content': 'Payment processed successfully',
                'classification': 'business',
                'expected_queue': 'payment_processor'
            },
            {
                'routing_key': 'system.cpu.warning',
                'content': 'CPU usage high: 95%',
                'classification': 'system',
                'expected_queue': 'system_warning'
            },
            {
                'routing_key': 'security.threat.detection',
                'content': 'Suspicious activity detected from IP 192.168.1.100',
                'classification': 'security',
                'expected_queue': 'threat_detection'
            },
            {
                'routing_key': 'analytics.event.user_action',
                'content': 'User performed search action',
                'classification': 'analytics',
                'expected_queue': 'event_processor'
            },
            {
                'routing_key': 'performance.bottleneck.database',
                'content': 'Database query bottleneck detected',
                'classification': 'performance',
                'expected_queue': 'bottleneck_detector'
            }
        ]
        
        return test_messages
    
    def classify_and_route_message(self, message: Dict[str, Any]) -> bool:
        """分类并路由消息"""
        try:
            # 生成消息ID
            message_id = str(uuid.uuid4())
            
            # 使用分类器进行分类
            route_decision = self.classifier.classify_message(
                message_id=message_id,
                routing_key=message['routing_key'],
                content=message['content']
            )
            
            # 创建消息属性
            properties = pika.BasicProperties(
                message_id=message_id,
                timestamp=time.time(),
                priority=route_decision.priority,
                headers={
                    'classification': route_decision.classification.value,
                    'expected_queue': message['expected_queue']
                }
            )
            
            # 发送消息到分类路由器
            classification_body = json.dumps({
                'original_routing_key': message['routing_key'],
                'content': message['content'],
                'expected_queue': message['expected_queue'],
                'route_decision': asdict(route_decision)
            }, ensure_ascii=False)
            
            # 发布到分类路由器
            self.channel.basic_publish(
                exchange='classification.router',
                routing_key=message['routing_key'],
                body=classification_body,
                properties=properties
            )
            
            # 记录路由历史
            self.route_history.append({
                'timestamp': time.time(),
                'message_id': message_id,
                'routing_key': message['routing_key'],
                'classification': route_decision.classification.value,
                'target_exchange': route_decision.target_exchange,
                'expected_queue': message['expected_queue'],
                'priority': route_decision.priority,
                'processing_time': route_decision.processing_time
            })
            
            print(f"📤 分类并路由消息:")
            print(f"   路由键: {message['routing_key']}")
            print(f"   分类: {route_decision.classification.value}")
            print(f"   目标交换机: {route_decision.target_exchange}")
            print(f"   预期队列: {message['expected_queue']}")
            print(f"   优先级: {route_decision.priority}")
            print(f"   处理时间: {route_decision.processing_time:.3f}s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 分类路由失败: {e}")
            return False
    
    def simulate_routing_chain(self):
        """模拟路由处理链"""
        print("\n🔗 模拟路由处理链")
        print("=" * 50)
        
        # 生成并分类消息
        test_messages = self.generate_test_messages()
        
        print(f"📊 开始处理 {len(test_messages)} 条消息")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 消息 {i}/{len(test_messages)} ---")
            
            # 分类并路由
            success = self.classify_and_route_message(message)
            
            if success:
                print(f"   ✅ 成功分类并路由")
            else:
                print(f"   ❌ 分类路由失败")
            
            # 模拟消息处理延迟
            time.sleep(0.5)
        
        print(f"\n📈 处理完成")
        self.show_routing_statistics()
    
    def show_routing_statistics(self):
        """显示路由统计"""
        print("\n📊 路由统计报告")
        print("=" * 50)
        
        # 获取分类器统计
        classifier_stats = self.classifier.get_statistics()
        
        print(f"📈 分类统计:")
        print(f"   总处理消息数: {classifier_stats['total_classified']}")
        print(f"   平均处理时间: {classifier_stats['average_processing_time']:.3f}s")
        print(f"   激活规则数: {classifier_stats['enabled_rules']}/{classifier_stats['total_rules']}")
        
        print(f"\n📊 分类分布:")
        for classification, count in classifier_stats['classification_distribution'].items():
            percentage = (count / classifier_stats['total_classified']) * 100
            print(f"   {classification}: {count} ({percentage:.1f}%)")
        
        print(f"\n🎯 规则使用情况:")
        for rule_name, hits in classifier_stats['rule_usage'].items():
            print(f"   {rule_name}: {hits} 次命中")
        
        # 显示路由历史摘要
        if self.route_history:
            print(f"\n🕒 最近路由历史:")
            recent_routes = list(self.route_history)[-5:]  # 最近5条
            for route in recent_routes:
                print(f"   {route['routing_key']} -> {route['classification']} -> {route['expected_queue']}")
    
    def interactive_classification_demo(self):
        """交互式分类演示"""
        print("\n🎯 交互式消息分类演示")
        print("=" * 60)
        
        if not self.connect():
            return
        
        try:
            # 设置分类环境
            self.setup_classification_environment()
            
            while True:
                print("\n请选择操作:")
                print("1. 运行标准分类演示")
                print("2. 添加自定义分类规则")
                print("3. 查看分类统计")
                print("4. 手动分类消息")
                print("5. 清理环境")
                print("6. 退出")
                
                choice = input("\n请输入选择 (1-6): ").strip()
                
                if choice == '1':
                    self.simulate_routing_chain()
                    
                elif choice == '2':
                    self.add_custom_rule()
                    
                elif choice == '3':
                    self.show_routing_statistics()
                    
                elif choice == '4':
                    self.manual_classification()
                    
                elif choice == '5':
                    self.cleanup_environment()
                    
                elif choice == '6':
                    print("👋 退出分类演示")
                    break
                    
                else:
                    print("❌ 无效选择")
                
                input("\n按回车键继续...")
                
        except Exception as e:
            self.logger.error(f"❌ 演示失败: {e}")
        
        finally:
            self.close()
    
    def add_custom_rule(self):
        """添加自定义分类规则"""
        print("\n➕ 添加自定义分类规则")
        print("=" * 40)
        
        try:
            rule_name = input("规则名称: ").strip()
            pattern = input("匹配模式 (正则表达式): ").strip()
            
            print("\n分类类型:")
            print("1. system - 系统")
            print("2. business - 业务")
            print("3. security - 安全")
            print("4. audit - 审计")
            print("5. analytics - 分析")
            print("6. performance - 性能")
            
            type_choice = input("请选择分类类型 (1-6): ").strip()
            classification_map = {
                '1': MessageClassification.SYSTEM,
                '2': MessageClassification.BUSINESS,
                '3': MessageClassification.SECURITY,
                '4': MessageClassification.AUDIT,
                '5': MessageClassification.ANALYTICS,
                '6': MessageClassification.PERFORMANCE
            }
            
            if type_choice not in classification_map:
                print("❌ 无效的分类类型")
                return
            
            priority = int(input("优先级 (1-10): ").strip() or "1")
            weight = float(input("权重 (0.1-2.0): ").strip() or "1.0")
            
            # 创建新规则
            new_rule = ClassificationRule(
                name=rule_name,
                pattern=pattern,
                classification=classification_map[type_choice],
                priority=priority,
                weight=weight
            )
            
            # 添加规则
            self.classifier.add_rule(new_rule)
            
            print(f"✅ 已添加规则: {rule_name}")
            print(f"   模式: {pattern}")
            print(f"   分类: {classification_map[type_choice].value}")
            print(f"   优先级: {priority}")
            print(f"   权重: {weight}")
            
        except Exception as e:
            print(f"❌ 添加规则失败: {e}")
    
    def manual_classification(self):
        """手动分类消息"""
        print("\n✋ 手动分类消息")
        print("=" * 40)
        
        try:
            routing_key = input("输入路由键: ").strip()
            content = input("输入消息内容: ").strip()
            
            if not routing_key or not content:
                print("❌ 路由键和内容不能为空")
                return
            
            # 生成分类决策
            message_id = str(uuid.uuid4())
            route_decision = self.classifier.classify_message(
                message_id=message_id,
                routing_key=routing_key,
                content=content
            )
            
            print(f"\n📋 分类结果:")
            print(f"   消息ID: {message_id}")
            print(f"   分类: {route_decision.classification.value}")
            print(f"   目标交换机: {route_decision.target_exchange}")
            print(f"   目标队列: {route_decision.target_queues}")
            print(f"   优先级: {route_decision.priority}")
            print(f"   处理时间: {route_decision.processing_time:.3f}s")
            print(f"   决策原因: {route_decision.reason}")
            
        except Exception as e:
            print(f"❌ 分类失败: {e}")
    
    def cleanup_environment(self):
        """清理环境"""
        print("\n🧹 清理分类环境")
        print("=" * 40)
        
        # 清理交换机
        exchanges_to_cleanup = [
            'classification.router', 'system.processor', 'business.processor',
            'security.processor', 'analytics.processor', 'audit.processor',
            'performance.processor'
        ]
        
        for exchange in exchanges_to_cleanup:
            try:
                self.channel.exchange_delete(exchange=exchange)
                print(f"✅ 删除交换机: {exchange}")
            except Exception as e:
                self.logger.warning(f"⚠️ 删除交换机失败 {exchange}: {e}")
        
        # 清理队列
        queues_to_cleanup = [
            'system_error', 'system_warning', 'system_info',
            'order_processor', 'payment_processor', 'user_processor',
            'auth_events', 'threat_detection', 'audit_security',
            'audit_trail', 'compliance_log',
            'metrics_collector', 'event_processor', 'stat_analyzer',
            'performance_monitor', 'bottleneck_detector'
        ]
        
        for queue in queues_to_cleanup:
            try:
                self.channel.queue_delete(queue=queue)
                print(f"✅ 删除队列: {queue}")
            except Exception as e:
                self.logger.warning(f"⚠️ 删除队列失败 {queue}: {e}")
        
        print("✅ 清理完成")
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            print("🔌 连接已关闭")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="消息分类演示工具")
    parser.add_argument('--host', default='localhost', help='RabbitMQ主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ端口')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    # 创建分类器
    classifier_demo = MessageClassificationDemo(host=args.host, port=args.port)
    
    if args.interactive:
        classifier_demo.interactive_classification_demo()
    else:
        # 运行标准演示
        classifier_demo.interactive_classification_demo()