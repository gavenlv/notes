#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第11章：RabbitMQ与实时数据处理集成 - 事件驱动微服务架构示例

本模块演示如何构建基于RabbitMQ的事件驱动微服务系统，
包括事件发布订阅、Saga事务管理、CQRS模式和事件溯源。
"""

import asyncio
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import weakref
import weakref

try:
    import pika
except ImportError:
    print("请安装pika: pip install pika")
    pika = None

# =============================================================================
# 1. 事件驱动架构核心组件
# =============================================================================

class EventType(Enum):
    """事件类型枚举"""
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"
    PRODUCT_STOCK_LOW = "product.stock_low"
    PRODUCT_OUT_OF_STOCK = "product.out_of_stock"
    PAYMENT_PROCESSED = "payment.processed"
    NOTIFICATION_SENT = "notification.sent"

class EventStatus(Enum):
    """事件状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class SagaStatus(Enum):
    """Saga事务状态"""
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    occurred_at: datetime
    version: int
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if isinstance(self.occurred_at, str):
            self.occurred_at = datetime.fromisoformat(self.occurred_at)
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SagaStep:
    """Saga步骤"""
    step_id: str
    service_name: str
    action: str
    compensating_action: Optional[str] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: EventStatus = EventStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None

@dataclass
class SagaTransaction:
    """Saga事务"""
    saga_id: str
    saga_type: str
    aggregate_id: str
    status: SagaStatus
    steps: List[SagaStep]
    started_at: datetime
    completed_at: Optional[datetime] = None
    compensation_actions: List[str] = None
    
    def __post_init__(self):
        if self.compensation_actions is None:
            self.compensation_actions = []

# =============================================================================
# 2. 事件存储（Event Store）
# =============================================================================

class EventStore:
    """事件存储实现"""
    
    def __init__(self):
        self.events: Dict[str, List[DomainEvent]] = defaultdict(list)
        self.event_streams: Dict[str, str] = {}  # aggregate_id -> stream_name
        
    def append_events(self, aggregate_id: str, stream_name: str, events: List[DomainEvent]):
        """追加事件到事件流"""
        if aggregate_id not in self.events:
            self.event_streams[aggregate_id] = stream_name
            
        for event in events:
            # 设置事件版本
            event.version = len(self.events[aggregate_id]) + 1
            self.events[aggregate_id].append(event)
            
        print(f"📝 存储了 {len(events)} 个事件到流 {stream_name} (聚合ID: {aggregate_id})")
        
    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        """获取聚合的所有事件"""
        return self.events.get(aggregate_id, [])
        
    def get_events_by_stream(self, stream_name: str) -> List[DomainEvent]:
        """根据流名称获取事件"""
        events = []
        for agg_id, stream in self.event_streams.items():
            if stream == stream_name:
                events.extend(self.events[agg_id])
        return events
        
    def get_events_by_type(self, event_type: EventType) -> List[DomainEvent]:
        """根据事件类型获取事件"""
        all_events = []
        for event_list in self.events.values():
            all_events.extend([event for event in event_list if event.event_type == event_type])
        return all_events

# =============================================================================
# 3. 事件总线（Event Bus）
# =============================================================================

class EventBus:
    """事件总线"""
    
    def __init__(self, rabbitmq_connector):
        self.connector = rabbitmq_connector
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_handlers: Dict[str, Callable] = {}
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """订阅事件"""
        self.subscribers[event_type].append(handler)
        print(f"📡 订阅事件: {event_type.value}")
        
    def publish_event(self, event: DomainEvent):
        """发布事件"""
        try:
            # 通过RabbitMQ发布事件
            routing_key = f"{event.event_type.value}.{event.aggregate_type.lower()}"
            
            self.connector.publish(
                exchange='domain_events',
                routing_key=routing_key,
                message=event,
                properties=None
            )
            
            print(f"🚀 发布事件: {event.event_type.value} (聚合ID: {event.aggregate_id})")
            
        except Exception as e:
            print(f"❌ 事件发布失败: {e}")
            
    def publish_local(self, event: DomainEvent):
        """本地发布事件（直接调用处理器）"""
        handlers = self.subscribers.get(event.event_type, [])
        
        print(f"🔔 本地广播事件: {event.event_type.value} (处理程序数: {len(handlers)})")
        
        for handler in handlers:
            try:
                asyncio.create_task(handler(event))
            except Exception as e:
                print(f"❌ 事件处理器错误: {e}")

# =============================================================================
# 4. CQRS读写分离
# =============================================================================

class QueryModel:
    """查询模型基类"""
    
    def __init__(self):
        self.projections: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
    def update_projection(self, aggregate_id: str, projection_data: Dict[str, Any]):
        """更新投影"""
        self.projections[aggregate_id].update(projection_data)
        
    def get_projection(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """获取投影"""
        return self.projections.get(aggregate_id)
        
    def get_all_projections(self) -> Dict[str, Dict[str, Any]]:
        """获取所有投影"""
        return dict(self.projections)

class UserQueryModel(QueryModel):
    """用户查询模型"""
    
    def __init__(self):
        super().__init__()
        
    def handle_user_registered(self, event: DomainEvent):
        """处理用户注册事件"""
        user_data = {
            'user_id': event.aggregate_id,
            'email': event.payload.get('email'),
            'status': 'active',
            'created_at': event.occurred_at.isoformat(),
            'last_activity': event.occurred_at.isoformat()
        }
        self.update_projection(event.aggregate_id, user_data)
        
    def handle_user_updated(self, event: DomainEvent):
        """处理用户更新事件"""
        self.update_projection(event.aggregate_id, {
            'last_updated': event.occurred_at.isoformat(),
            **{f'updated_{k}': v for k, v in event.payload.items()}
        })

class OrderQueryModel(QueryModel):
    """订单查询模型"""
    
    def __init__(self):
        super().__init__()
        
    def handle_order_created(self, event: DomainEvent):
        """处理订单创建事件"""
        order_data = {
            'order_id': event.aggregate_id,
            'user_id': event.payload.get('user_id'),
            'status': 'created',
            'items': event.payload.get('items', []),
            'total_amount': event.payload.get('total_amount'),
            'created_at': event.occurred_at.isoformat()
        }
        self.update_projection(event.aggregate_id, order_data)
        
    def handle_order_paid(self, event: DomainEvent):
        """处理订单支付事件"""
        self.update_projection(event.aggregate_id, {
            'status': 'paid',
            'paid_at': event.occurred_at.isoformat(),
            'payment_method': event.payload.get('payment_method')
        })
        
    def handle_order_shipped(self, event: DomainEvent):
        """处理订单发货事件"""
        self.update_projection(event.aggregate_id, {
            'status': 'shipped',
            'shipped_at': event.occurred_at.isoformat(),
            'tracking_number': event.payload.get('tracking_number')
        })

class CQRSQuerySide:
    """CQRS查询端"""
    
    def __init__(self):
        self.query_models = {
            'user': UserQueryModel(),
            'order': OrderQueryModel()
        }
        
        # 事件类型到查询模型的映射
        self.event_handlers = {
            EventType.USER_REGISTERED: self._handle_user_event,
            EventType.USER_UPDATED: self._handle_user_event,
            EventType.ORDER_CREATED: self._handle_order_event,
            EventType.ORDER_PAID: self._handle_order_event,
            EventType.ORDER_SHIPPED: self._handle_order_event
        }
        
    def _handle_user_event(self, event: DomainEvent):
        """处理用户事件"""
        model = self.query_models['user']
        if event.event_type == EventType.USER_REGISTERED:
            model.handle_user_registered(event)
        elif event.event_type == EventType.USER_UPDATED:
            model.handle_user_updated(event)
            
    def _handle_order_event(self, event: DomainEvent):
        """处理订单事件"""
        model = self.query_models['order']
        if event.event_type == EventType.ORDER_CREATED:
            model.handle_order_created(event)
        elif event.event_type == EventType.ORDER_PAID:
            model.handle_order_paid(event)
        elif event.event_type == EventType.ORDER_SHIPPED:
            model.handle_order_shipped(event)
            
    def handle_event(self, event: DomainEvent):
        """处理事件更新查询模型"""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            handler(event)
            
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.query_models['user'].get_projection(user_id)
        
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单信息"""
        return self.query_models['order'].get_projection(order_id)
        
    def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有订单"""
        all_orders = self.query_models['order'].get_all_projections()
        return [order for order in all_orders.values() if order.get('user_id') == user_id]

# =============================================================================
# 5. Saga事务管理器
# =============================================================================

class SagaManager:
    """Saga事务管理器"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.sagas: Dict[str, SagaTransaction] = {}
        self.saga_definitions = {}
        self.setup_saga_definitions()
        
    def setup_saga_definitions(self):
        """设置Saga定义"""
        # 订单创建Saga定义
        self.saga_definitions['order_creation'] = {
            'steps': [
                {
                    'service': 'inventory_service',
                    'action': 'reserve_stock',
                    'compensating_action': 'release_stock'
                },
                {
                    'service': 'payment_service',
                    'action': 'process_payment',
                    'compensating_action': 'refund_payment'
                },
                {
                    'service': 'notification_service',
                    'action': 'send_order_confirmation',
                    'compensating_action': 'send_order_cancellation'
                },
                {
                    'service': 'order_service',
                    'action': 'create_order',
                    'compensating_action': 'cancel_order'
                }
            ]
        }
        
    def start_saga(self, saga_type: str, aggregate_id: str, initial_data: Dict[str, Any]) -> str:
        """启动Saga事务"""
        saga_id = str(uuid.uuid4())
        
        # 创建Saga步骤
        steps = []
        saga_def = self.saga_definitions.get(saga_type, {})
        for i, step_def in enumerate(saga_def.get('steps', [])):
            step = SagaStep(
                step_id=f"{saga_id}_step_{i}",
                service_name=step_def['service'],
                action=step_def['action'],
                compensating_action=step_def.get('compensating_action')
            )
            steps.append(step)
            
        # 创建Saga事务
        saga = SagaTransaction(
            saga_id=saga_id,
            saga_type=saga_type,
            aggregate_id=aggregate_id,
            status=SagaStatus.STARTING,
            steps=steps,
            started_at=datetime.now()
        )
        
        self.sagas[saga_id] = saga
        
        print(f"🚀 启动Saga: {saga_type} (ID: {saga_id}, 聚合ID: {aggregate_id})")
        
        # 开始执行第一个步骤
        asyncio.create_task(self.execute_next_step(saga_id))
        
        return saga_id
        
    async def execute_next_step(self, saga_id: str):
        """执行Saga的下一个步骤"""
        saga = self.sagas.get(saga_id)
        if not saga:
            return
            
        # 查找下一个待执行的步骤
        current_step = None
        for step in saga.steps:
            if step.status == EventStatus.PENDING:
                current_step = step
                break
                
        if not current_step:
            # 所有步骤都已执行完成
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.now()
            print(f"✅ Saga完成: {saga_id}")
            
            # 发送Saga完成事件
            await self.send_saga_completed_event(saga)
            return
            
        # 执行当前步骤
        try:
            current_step.status = EventStatus.PROCESSING
            print(f"⚡ 执行步骤: {current_step.action} (服务: {current_step.service_name})")
            
            # 模拟步骤执行
            result = await self.execute_step_action(current_step)
            
            current_step.status = EventStatus.COMPLETED
            current_step.result = result
            
            # 继续执行下一步
            await asyncio.sleep(0.1)  # 模拟异步处理延迟
            await self.execute_next_step(saga_id)
            
        except Exception as e:
            current_step.status = EventStatus.FAILED
            current_step.error_message = str(e)
            
            print(f"❌ 步骤执行失败: {current_step.action} - {e}")
            
            # 根据错误处理策略决定是否重试或补偿
            if current_step.retry_count < current_step.max_retries:
                current_step.status = EventStatus.RETRYING
                current_step.retry_count += 1
                print(f"🔄 重试步骤: {current_step.action} (第{current_step.retry_count}次)")
                await asyncio.sleep(1)
                await self.execute_next_step(saga_id)
            else:
                # 开始补偿操作
                await self.start_compensation(saga_id)
                
    async def execute_step_action(self, step: SagaStep) -> Dict[str, Any]:
        """执行步骤操作"""
        # 模拟不同服务的操作
        if step.service_name == 'inventory_service':
            if step.action == 'reserve_stock':
                await asyncio.sleep(0.5)  # 模拟库存预留耗时
                return {'reservation_id': f"RES_{uuid.uuid4().hex[:8]}", 'status': 'reserved'}
            elif step.action == 'release_stock':
                await asyncio.sleep(0.3)
                return {'status': 'released'}
                
        elif step.service_name == 'payment_service':
            if step.action == 'process_payment':
                await asyncio.sleep(1.0)  # 模拟支付处理耗时
                return {'transaction_id': f"TXN_{uuid.uuid4().hex[:8]}", 'status': 'completed'}
            elif step.action == 'refund_payment':
                await asyncio.sleep(0.8)
                return {'refund_id': f"REF_{uuid.uuid4().hex[:8]}", 'status': 'refunded'}
                
        elif step.service_name == 'notification_service':
            if step.action == 'send_order_confirmation':
                await asyncio.sleep(0.2)
                return {'message_id': f"MSG_{uuid.uuid4().hex[:8]}", 'status': 'sent'}
            elif step.action == 'send_order_cancellation':
                await asyncio.sleep(0.2)
                return {'message_id': f"MSG_{uuid.uuid4().hex[:8]}", 'status': 'cancelled'}
                
        elif step.service_name == 'order_service':
            if step.action == 'create_order':
                await asyncio.sleep(0.3)
                return {'order_id': f"ORD_{uuid.uuid4().hex[:8]}", 'status': 'created'}
            elif step.action == 'cancel_order':
                await asyncio.sleep(0.3)
                return {'status': 'cancelled'}
                
        # 默认返回
        await asyncio.sleep(0.1)
        return {'status': 'completed'}
        
    async def start_compensation(self, saga_id: str):
        """开始Saga补偿操作"""
        saga = self.sagas.get(saga_id)
        if not saga:
            return
            
        saga.status = SagaStatus.COMPENSATING
        print(f"🔄 开始补偿Saga: {saga_id}")
        
        # 按相反顺序执行补偿操作
        for step in reversed(saga.steps):
            if step.status == EventStatus.COMPLETED and step.compensating_action:
                try:
                    print(f"🔧 执行补偿: {step.compensating_action}")
                    result = await self.execute_compensation_action(step)
                    saga.compensation_actions.append(step.compensating_action)
                    
                except Exception as e:
                    print(f"❌ 补偿操作失败: {step.compensating_action} - {e}")
                    
        saga.status = SagaStatus.COMPENSATED
        saga.completed_at = datetime.now()
        print(f"🔄 Saga补偿完成: {saga_id}")
        
    async def execute_compensation_action(self, step: SagaStep) -> Dict[str, Any]:
        """执行补偿操作"""
        # 重用步骤执行逻辑，但使用补偿操作
        original_action = step.action
        step.action = step.compensating_action
        
        try:
            result = await self.execute_step_action(step)
            return result
        finally:
            step.action = original_action
            
    async def send_saga_completed_event(self, saga: SagaTransaction):
        """发送Saga完成事件"""
        completion_event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.ORDER_CREATED,  # 使用适当的事件类型
            aggregate_id=saga.aggregate_id,
            aggregate_type='saga',
            occurred_at=datetime.now(),
            version=1,
            payload={
                'saga_id': saga.saga_id,
                'saga_type': saga.saga_type,
                'status': saga.status.value,
                'completed_steps': len([s for s in saga.steps if s.status == EventStatus.COMPLETED]),
                'total_steps': len(saga.steps)
            }
        )
        
        self.event_bus.publish_local(completion_event)

# =============================================================================
# 6. 微服务实现示例
# =============================================================================

class InventoryService:
    """库存服务"""
    
    def __init__(self, event_bus: EventBus, event_store: EventStore):
        self.event_bus = event_bus
        self.event_store = event_store
        self.inventory = defaultdict(int)  # product_id -> quantity
        
    async def reserve_stock(self, order_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """预留库存"""
        reservation_id = f"RES_{uuid.uuid4().hex[:8]}"
        
        # 模拟库存检查和预留
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            if self.inventory[product_id] >= quantity:
                self.inventory[product_id] -= quantity
                
                # 发布库存预留事件
                reserve_event = DomainEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.PRODUCT_STOCK_LOW,
                    aggregate_id=product_id,
                    aggregate_type='product',
                    occurred_at=datetime.now(),
                    version=1,
                    payload={
                        'reservation_id': reservation_id,
                        'order_id': order_id,
                        'quantity_reserved': quantity,
                        'remaining_stock': self.inventory[product_id]
                    }
                )
                
                self.event_store.append_events(
                    product_id,
                    f"product-{product_id}",
                    [reserve_event]
                )
                
                self.event_bus.publish_local(reserve_event)
            else:
                # 库存不足
                out_of_stock_event = DomainEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.PRODUCT_OUT_OF_STOCK,
                    aggregate_id=product_id,
                    aggregate_type='product',
                    occurred_at=datetime.now(),
                    version=1,
                    payload={
                        'order_id': order_id,
                        'requested_quantity': quantity,
                        'available_quantity': self.inventory[product_id]
                    }
                )
                
                self.event_store.append_events(
                    product_id,
                    f"product-{product_id}",
                    [out_of_stock_event]
                )
                
                self.event_bus.publish_local(out_of_stock_event)
                
                raise Exception(f"库存不足: 产品 {product_id}")
                
        return {'reservation_id': reservation_id, 'status': 'reserved'}
        
    def add_stock(self, product_id: str, quantity: int):
        """添加库存"""
        self.inventory[product_id] += quantity

class PaymentService:
    """支付服务"""
    
    def __init__(self, event_bus: EventBus, event_store: EventStore):
        self.event_bus = event_bus
        self.event_store = event_store
        
    async def process_payment(self, order_id: str, payment_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理支付"""
        transaction_id = f"TXN_{uuid.uuid4().hex[:8]}"
        
        # 模拟支付处理
        await asyncio.sleep(1.0)  # 模拟支付API调用
        
        # 发布支付成功事件
        payment_event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PAYMENT_PROCESSED,
            aggregate_id=order_id,
            aggregate_type='order',
            occurred_at=datetime.now(),
            version=1,
            payload={
                'transaction_id': transaction_id,
                'amount': payment_info.get('amount'),
                'payment_method': payment_info.get('payment_method'),
                'status': 'completed'
            }
        )
        
        self.event_store.append_events(
            order_id,
            f"order-{order_id}",
            [payment_event]
        )
        
        self.event_bus.publish_local(payment_event)
        
        return {'transaction_id': transaction_id, 'status': 'completed'}

class NotificationService:
    """通知服务"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe(EventType.ORDER_CREATED, self.handle_order_created)
        
    async def send_order_confirmation(self, order_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """发送订单确认"""
        message_id = f"MSG_{uuid.uuid4().hex[:8]}"
        
        # 模拟发送通知
        print(f"📧 发送订单确认邮件给 {user_info.get('email')} (订单: {order_id})")
        await asyncio.sleep(0.2)
        
        # 发布通知发送事件
        notification_event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.NOTIFICATION_SENT,
            aggregate_id=order_id,
            aggregate_type='notification',
            occurred_at=datetime.now(),
            version=1,
            payload={
                'message_id': message_id,
                'notification_type': 'order_confirmation',
                'recipient': user_info.get('email'),
                'status': 'sent'
            }
        )
        
        self.event_bus.publish_local(notification_event)
        
        return {'message_id': message_id, 'status': 'sent'}
        
    async def handle_order_created(self, event: DomainEvent):
        """处理订单创建事件"""
        # 自动发送确认邮件
        order_data = event.payload
        user_info = {'email': 'customer@example.com'}  # 模拟用户信息
        
        await self.send_order_confirmation(event.aggregate_id, user_info)

class OrderService:
    """订单服务"""
    
    def __init__(self, event_bus: EventBus, event_store: EventStore):
        self.event_bus = event_bus
        self.event_store = event_store
        self.saga_manager = None  # 将在外部设置
        
    def set_saga_manager(self, saga_manager: SagaManager):
        """设置Saga管理器"""
        self.saga_manager = saga_manager
        
    async def create_order(self, user_id: str, items: List[Dict[str, Any]], payment_info: Dict[str, Any]) -> str:
        """创建订单"""
        order_id = str(uuid.uuid4())
        
        # 计算订单总价
        total_amount = sum(item['price'] * item['quantity'] for item in items)
        
        # 启动Saga事务
        saga_id = self.saga_manager.start_saga(
            saga_type='order_creation',
            aggregate_id=order_id,
            initial_data={
                'user_id': user_id,
                'items': items,
                'total_amount': total_amount,
                'payment_info': payment_info
            }
        )
        
        return order_id

# =============================================================================
# 7. 事件驱动微服务编排器
# =============================================================================

class EventDrivenMicroserviceOrchestrator:
    """事件驱动微服务编排器"""
    
    def __init__(self, rabbitmq_config=None):
        # 初始化核心组件
        self.rabbitmq = None  # 在实际环境中初始化
        self.event_store = EventStore()
        self.event_bus = EventBus(self.rabbitmq) if self.rabbitmq else None
        self.query_side = CQRSQuerySide()
        self.saga_manager = SagaManager(self.event_bus) if self.event_bus else None
        
        # 初始化微服务
        self.inventory_service = InventoryService(self.event_bus, self.event_store)
        self.payment_service = PaymentService(self.event_bus, self.event_store)
        self.notification_service = NotificationService(self.event_bus)
        self.order_service = OrderService(self.event_bus, self.event_store)
        
        # 连接服务
        self.order_service.set_saga_manager(self.saga_manager)
        
        # 设置事件处理器
        self.setup_event_handlers()
        
        # 性能指标
        self.metrics = {
            'events_published': 0,
            'events_consumed': 0,
            'sagas_started': 0,
            'sagas_completed': 0,
            'processing_time': defaultdict(float)
        }
        
        self.is_running = False
        
    def setup_event_handlers(self):
        """设置事件处理器"""
        if not self.event_bus:
            return
            
        # 注册CQRS查询端事件处理器
        event_handler_mapping = {
            EventType.USER_REGISTERED: self.query_side.handle_event,
            EventType.USER_UPDATED: self.query_side.handle_event,
            EventType.ORDER_CREATED: self.query_side.handle_event,
            EventType.ORDER_PAID: self.query_side.handle_event,
            EventType.ORDER_SHIPPED: self.query_side.handle_event
        }
        
        for event_type, handler in event_handler_mapping.items():
            self.event_bus.subscribe(event_type, handler)
            
    async def create_order_workflow(self, user_id: str, items: List[Dict[str, Any]], payment_info: Dict[str, Any]) -> Dict[str, Any]:
        """创建订单工作流程"""
        print(f"🛒 开始创建订单流程 - 用户: {user_id}")
        
        start_time = time.time()
        
        try:
            # 1. 创建订单（这会启动Saga事务）
            order_id = await self.order_service.create_order(user_id, items, payment_info)
            
            # 2. 手动执行库存预留步骤（演示用）
            await self.inventory_service.reserve_stock(order_id, items)
            
            # 3. 手动执行支付处理步骤（演示用）
            await self.payment_service.process_payment(order_id, payment_info)
            
            # 4. 手动执行通知发送步骤（演示用）
            await self.notification_service.send_order_confirmation(order_id, {'email': 'customer@example.com'})
            
            # 等待所有异步操作完成
            await asyncio.sleep(2)
            
            processing_time = time.time() - start_time
            
            result = {
                'order_id': order_id,
                'status': 'created',
                'processing_time': processing_time,
                'user_id': user_id,
                'items_count': len(items),
                'total_amount': sum(item['price'] * item['quantity'] for item in items)
            }
            
            self.metrics['events_published'] += 4  # 假设发布了4个事件
            self.metrics['sagas_started'] += 1
            self.metrics['processing_time']['create_order'] += processing_time
            
            print(f"✅ 订单创建成功: {order_id} (耗时: {processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ 订单创建失败: {e}")
            
            return {
                'order_id': None,
                'status': 'failed',
                'error': str(e),
                'processing_time': processing_time
            }
            
    async def run_workflow_simulation(self):
        """运行工作流程模拟"""
        print("🎯 开始事件驱动微服务工作流程演示")
        print("="*50)
        
        # 添加一些测试库存
        self.inventory_service.add_stock('product_1', 100)
        self.inventory_service.add_stock('product_2', 50)
        self.inventory_service.add_stock('product_3', 25)
        
        # 模拟订单数据
        test_orders = [
            {
                'user_id': 'user_123',
                'items': [
                    {'product_id': 'product_1', 'quantity': 2, 'price': 29.99},
                    {'product_id': 'product_2', 'quantity': 1, 'price': 99.99}
                ],
                'payment_info': {'amount': 159.97, 'payment_method': 'credit_card'}
            },
            {
                'user_id': 'user_456',
                'items': [
                    {'product_id': 'product_3', 'quantity': 3, 'price': 49.99}
                ],
                'payment_info': {'amount': 149.97, 'payment_method': 'paypal'}
            },
            {
                'user_id': 'user_789',
                'items': [
                    {'product_id': 'product_1', 'quantity': 5, 'price': 29.99}
                ],
                'payment_info': {'amount': 149.95, 'payment_method': 'bank_transfer'}
            }
        ]
        
        # 执行订单创建工作流程
        results = []
        for i, order_data in enumerate(test_orders, 1):
            print(f"\n📦 处理订单 {i}")
            result = await self.create_order_workflow(**order_data)
            results.append(result)
            
            # 等待一下再处理下一个订单
            await asyncio.sleep(1)
            
        # 显示最终结果
        await self.display_results(results)
        
    async def display_results(self, results: List[Dict[str, Any]]):
        """显示处理结果"""
        print("\n" + "="*50)
        print("📊 事件驱动微服务工作流程演示结果")
        print("="*50)
        
        # 统计信息
        successful_orders = [r for r in results if r['status'] == 'created']
        failed_orders = [r for r in results if r['status'] == 'failed']
        
        print(f"✅ 成功创建的订单: {len(successful_orders)}/{len(results)}")
        print(f"❌ 失败的订单: {len(failed_orders)}")
        
        # 订单详情
        print(f"\n📋 订单详情:")
        for i, result in enumerate(successful_orders, 1):
            print(f"  {i}. 订单ID: {result['order_id']}")
            print(f"     用户: {result['user_id']}")
            print(f"     商品数量: {result['items_count']}")
            print(f"     总金额: ${result['total_amount']:.2f}")
            print(f"     处理时间: {result['processing_time']:.2f}s")
            
        # 事件存储信息
        print(f"\n📚 事件存储统计:")
        for aggregate_id, events in self.event_store.events.items():
            print(f"  聚合 {aggregate_id}: {len(events)} 个事件")
            
        # 查询端统计
        print(f"\n📈 CQRS查询端统计:")
        user_projections = self.query_side.query_models['user'].get_all_projections()
        order_projections = self.query_side.query_models['order'].get_all_projections()
        
        print(f"  用户投影: {len(user_projections)} 个")
        print(f"  订单投影: {len(order_projections)} 个")
        
        # 演示用户和订单查询
        if user_projections:
            sample_user_id = list(user_projections.keys())[0]
            user_data = self.query_side.get_user(sample_user_id)
            if user_data:
                print(f"\n👤 示例用户数据: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
                
        if order_projections:
            sample_order_id = list(order_projections.keys())[0]
            order_data = self.query_side.get_order(sample_order_id)
            if order_data:
                print(f"\n🛒 示例订单数据: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
                
        print("="*50)

# =============================================================================
# 8. 演示程序
# =============================================================================

async def main():
    """主演示程序"""
    print("🎯 事件驱动微服务架构演示")
    print("="*50)
    print("本演示展示了基于RabbitMQ的事件驱动微服务架构，")
    print("包括事件发布订阅、Saga事务管理、CQRS模式等核心功能。")
    print("="*50)
    
    # 创建编排器
    orchestrator = EventDrivenMicroserviceOrchestrator()
    
    try:
        orchestrator.is_running = True
        
        # 运行工作流程模拟
        await orchestrator.run_workflow_simulation()
        
        print(f"\n🎉 事件驱动微服务架构演示完成！")
        print(f"系统展示了如何构建高内聚、低耦合的微服务系统。")
        
    except Exception as e:
        print(f"❌ 演示错误: {e}")
    finally:
        orchestrator.is_running = False

if __name__ == "__main__":
    # 运行异步主程序
    asyncio.run(main())