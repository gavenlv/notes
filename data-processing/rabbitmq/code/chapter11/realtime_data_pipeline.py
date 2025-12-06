#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第11章：RabbitMQ实时数据处理集成 - 数据流处理管道示例

本模块演示如何构建高性能的实时数据流处理管道，
包括数据接入、处理、聚合和输出的完整流程。
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid

try:
    import pika
except ImportError:
    print("请安装pika: pip install pika")
    pika = None

try:
    import redis
except ImportError:
    print("请安装redis: pip install redis")
    redis = None

# =============================================================================
# 1. 数据结构和枚举类定义
# =============================================================================

class DataType(Enum):
    """数据类型枚举"""
    SENSOR_DATA = "sensor"
    USER_EVENT = "user_event"
    SYSTEM_METRIC = "system_metric"
    BUSINESS_EVENT = "business_event"
    AUDIT_LOG = "audit_log"

class ProcessingStage(Enum):
    """处理阶段枚举"""
    INGESTION = "ingestion"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"
    OUTPUT = "output"

class QualityLevel(Enum):
    """数据质量等级"""
    EXCELLENT = 1.0
    GOOD = 0.8
    FAIR = 0.6
    POOR = 0.4
    INVALID = 0.0

@dataclass
class DataMessage:
    """数据消息结构"""
    message_id: str
    data_type: DataType
    timestamp: datetime
    source_id: str
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    quality_score: QualityLevel = QualityLevel.GOOD
    processed_stages: List[ProcessingStage] = None
    
    def __post_init__(self):
        if self.processed_stages is None:
            self.processed_stages = []
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

@dataclass
class ProcessingMetrics:
    """处理指标"""
    stage: ProcessingStage
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    error_count: int = 0
    avg_processing_time: float = 0.0
    throughput: float = 0.0

# =============================================================================
# 2. 消息队列连接器
# =============================================================================

class RabbitMQConnector:
    """RabbitMQ连接器"""
    
    def __init__(self, host='localhost', port=5672, username='admin', password='admin'):
        if pika is None:
            raise ImportError("pika库未安装，请运行: pip install pika")
            
        self.config = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'virtual_host': '/realtime_data'
        }
        self.connection = None
        self.channel = None
        self.exchanges = {}
        self.queues = {}
        
    def connect(self):
        """建立连接"""
        credentials = pika.PlainCredentials(self.config['username'], self.config['password'])
        parameters = pika.ConnectionParameters(
            host=self.config['host'],
            port=self.config['port'],
            credentials=credentials,
            virtual_host=self.config['virtual_host']
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # 声明基础交换器
        self.declare_exchanges()
        
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
            
    def declare_exchanges(self):
        """声明交换器"""
        exchanges = {
            'data_ingestion': {'type': 'topic', 'durable': True},
            'processing_pipeline': {'type': 'direct', 'durable': True},
            'aggregated_data': {'type': 'fanout', 'durable': True},
            'dead_letters': {'type': 'topic', 'durable': True}
        }
        
        for name, props in exchanges.items():
            self.channel.exchange_declare(
                exchange=name,
                exchange_type=props['type'],
                durable=props['durable']
            )
            self.exchanges[name] = props
            
    def declare_queue(self, queue_name: str, durable=True, arguments=None):
        """声明队列"""
        if arguments is None:
            arguments = {
                'x-message-ttl': 3600000,  # 1小时
                'x-dead-letter-exchange': 'dead_letters'
            }
            
        result = self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            arguments=arguments
        )
        self.queues[queue_name] = result.method.queue
        return result.method.queue
        
    def publish(self, exchange: str, routing_key: str, message: DataMessage, properties=None):
        """发布消息"""
        if properties is None:
            properties = pika.BasicProperties(
                message_id=message.message_id,
                timestamp=int(message.timestamp.timestamp()),
                delivery_mode=2,  # 持久化
                headers={
                    'data_type': message.data_type.value,
                    'source_id': message.source_id,
                    'quality_score': message.quality_score.value
                }
            )
            
        body = json.dumps(asdict(message), default=str, ensure_ascii=False)
        
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=properties
        )
        
    def consume(self, queue: str, callback: Callable, auto_ack=False):
        """消费消息"""
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=callback,
            auto_ack=auto_ack
        )

class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        if redis is None:
            raise ImportError("redis库未安装，请运行: pip install redis")
            
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
    def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        try:
            return self.client.get(key)
        except Exception:
            return None
            
    def set(self, key: str, value: str, ttl: int = 3600):
        """设置缓存值"""
        try:
            return self.client.setex(key, ttl, value)
        except Exception:
            return False
            
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            return bool(self.client.delete(key))
        except Exception:
            return False

# =============================================================================
# 3. 数据验证器
# =============================================================================

class DataValidator:
    """数据验证器基类"""
    
    def validate(self, message: DataMessage) -> bool:
        """验证消息数据"""
        try:
            # 基础验证
            if not self._validate_basic_fields(message):
                return False
                
            # 类型特定验证
            if not self._validate_type_specific(message):
                return False
                
            # 数据质量检查
            quality_score = self._calculate_quality_score(message)
            message.quality_score = quality_score
            
            return quality_score.value > 0.0
            
        except Exception as e:
            print(f"验证错误: {e}")
            return False
            
    def _validate_basic_fields(self, message: DataMessage) -> bool:
        """基础字段验证"""
        required_fields = ['message_id', 'data_type', 'timestamp', 'source_id', 'payload']
        
        for field in required_fields:
            if not hasattr(message, field) or getattr(message, field) is None:
                return False
                
        # 验证消息ID格式
        if not message.message_id or len(message.message_id) < 10:
            return False
            
        # 验证时间戳
        if isinstance(message.timestamp, datetime):
            now = datetime.now()
            if abs((message.timestamp - now).total_seconds()) > 86400:  # 24小时
                return False
                
        return True
        
    def _validate_type_specific(self, message: DataMessage) -> bool:
        """类型特定验证"""
        if message.data_type == DataType.SENSOR_DATA:
            return self._validate_sensor_data(message)
        elif message.data_type == DataType.USER_EVENT:
            return self._validate_user_event(message)
        elif message.data_type == DataType.SYSTEM_METRIC:
            return self._validate_system_metric(message)
        else:
            return True
            
    def _validate_sensor_data(self, message: DataMessage) -> bool:
        """传感器数据验证"""
        payload = message.payload
        
        # 必需字段检查
        required_sensor_fields = ['device_id', 'sensor_type', 'value', 'unit']
        for field in required_sensor_fields:
            if field not in payload:
                return False
                
        # 数值范围检查
        if 'value' in payload:
            try:
                value = float(payload['value'])
                if not (-1000 <= value <= 1000):  # 合理的传感器值范围
                    return False
            except (ValueError, TypeError):
                return False
                
        return True
        
    def _validate_user_event(self, message: DataMessage) -> bool:
        """用户事件验证"""
        payload = message.payload
        
        # 检查用户ID
        if 'user_id' not in payload:
            return False
            
        # 检查事件类型
        if 'event_type' not in payload:
            return False
            
        return True
        
    def _validate_system_metric(self, message: DataMessage) -> bool:
        """系统指标验证"""
        payload = message.payload
        
        # 检查指标名称
        if 'metric_name' not in payload:
            return False
            
        # 检查指标值
        if 'metric_value' not in payload:
            return False
            
        return True
        
    def _calculate_quality_score(self, message: DataMessage) -> QualityLevel:
        """计算数据质量分数"""
        score = 1.0
        
        # 基础完整性检查
        if not hasattr(message, 'metadata') or message.metadata is None:
            score -= 0.2
            
        # 数据新鲜度检查
        if hasattr(message, 'timestamp'):
            age = (datetime.now() - message.timestamp).total_seconds()
            if age > 3600:  # 1小时
                score -= 0.3
            elif age > 600:  # 10分钟
                score -= 0.1
                
        # 负载完整性检查
        if isinstance(message.payload, dict):
            expected_fields = self._get_expected_fields(message.data_type)
            missing_fields = set(expected_fields) - set(message.payload.keys())
            score -= len(missing_fields) * 0.1
            
        # 映射到质量等级
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.FAIR
        elif score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.INVALID
            
    def _get_expected_fields(self, data_type: DataType) -> List[str]:
        """获取预期字段列表"""
        field_mappings = {
            DataType.SENSOR_DATA: ['device_id', 'sensor_type', 'value', 'unit'],
            DataType.USER_EVENT: ['user_id', 'event_type', 'timestamp'],
            DataType.SYSTEM_METRIC: ['metric_name', 'metric_value', 'source'],
            DataType.BUSINESS_EVENT: ['event_name', 'event_data', 'timestamp'],
            DataType.AUDIT_LOG: ['action', 'user_id', 'resource', 'timestamp']
        }
        
        return field_mappings.get(data_type, [])

# =============================================================================
# 4. 数据转换器
# =============================================================================

class DataTransformer:
    """数据转换器"""
    
    def __init__(self):
        self.transformation_rules = {}
        self.setup_default_rules()
        
    def setup_default_rules(self):
        """设置默认转换规则"""
        self.transformation_rules = {
            DataType.SENSOR_DATA: self._transform_sensor_data,
            DataType.USER_EVENT: self._transform_user_event,
            DataType.SYSTEM_METRIC: self._transform_system_metric
        }
        
    def transform(self, message: DataMessage) -> DataMessage:
        """转换消息数据"""
        try:
            # 应用通用转换
            transformed_message = self._apply_common_transformations(message)
            
            # 应用类型特定转换
            if message.data_type in self.transformation_rules:
                transformed_message = self.transformation_rules[message.data_type](transformed_message)
                
            # 添加转换阶段记录
            if ProcessingStage.TRANSFORMATION not in transformed_message.processed_stages:
                transformed_message.processed_stages.append(ProcessingStage.TRANSFORMATION)
                
            return transformed_message
            
        except Exception as e:
            print(f"数据转换错误: {e}")
            return message
            
    def _apply_common_transformations(self, message: DataMessage) -> DataMessage:
        """应用通用转换"""
        # 时间戳标准化
        if isinstance(message.timestamp, str):
            message.timestamp = datetime.fromisoformat(message.timestamp)
            
        # 负载数据清理
        if isinstance(message.payload, dict):
            message.payload = self._clean_payload(message.payload)
            
        # 元数据丰富
        if message.metadata is None:
            message.metadata = {}
            
        message.metadata.update({
            'transformed_at': datetime.now().isoformat(),
            'transformer_version': '1.0',
            'message_hash': self._calculate_message_hash(message)
        })
        
        return message
        
    def _transform_sensor_data(self, message: DataMessage) -> DataMessage:
        """传感器数据转换"""
        payload = message.payload
        
        # 单位标准化
        if 'unit' in payload:
            payload['unit'] = self._normalize_unit(payload['unit'])
            
        # 数值类型转换
        if 'value' in payload:
            try:
                payload['value'] = float(payload['value'])
                payload['value_rounded'] = round(payload['value'], 2)
            except (ValueError, TypeError):
                payload['value'] = 0.0
                
        # 添加传感器元数据
        if 'device_id' in payload:
            payload['device_category'] = self._categorize_device(payload['device_id'])
            
        return message
        
    def _transform_user_event(self, message: DataMessage) -> DataMessage:
        """用户事件转换"""
        payload = message.payload
        
        # 事件时间标准化
        if 'event_timestamp' in payload:
            try:
                payload['event_timestamp'] = datetime.fromisoformat(payload['event_timestamp'])
            except:
                payload['event_timestamp'] = message.timestamp
                
        # 用户ID标准化
        if 'user_id' in payload:
            payload['user_id'] = str(payload['user_id']).strip().lower()
            
        # 添加事件分类
        if 'event_type' in payload:
            payload['event_category'] = self._categorize_event_type(payload['event_type'])
            
        return message
        
    def _transform_system_metric(self, message: DataMessage) -> DataMessage:
        """系统指标转换"""
        payload = message.payload
        
        # 指标值类型转换
        if 'metric_value' in payload:
            try:
                payload['metric_value'] = float(payload['metric_value'])
            except (ValueError, TypeError):
                payload['metric_value'] = 0.0
                
        # 添加指标元数据
        if 'metric_name' in payload:
            payload['metric_type'] = self._classify_metric_type(payload['metric_name'])
            payload['metric_unit'] = self._get_metric_unit(payload['metric_name'])
            
        return message
        
    def _clean_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """清理负载数据"""
        cleaned = {}
        
        for key, value in payload.items():
            # 跳过None值
            if value is None:
                continue
                
            # 字符串清理
            if isinstance(value, str):
                value = value.strip()
                if value:  # 非空字符串
                    cleaned[key] = value
            else:
                cleaned[key] = value
                
        return cleaned
        
    def _normalize_unit(self, unit: str) -> str:
        """标准化单位"""
        unit_mapping = {
            'celsius': '°C',
            'fahrenheit': '°F',
            'kelvin': 'K',
            'percent': '%',
            'milliseconds': 'ms',
            'seconds': 's',
            'bytes': 'B',
            'kilobytes': 'KB',
            'megabytes': 'MB'
        }
        
        unit_lower = unit.lower()
        return unit_mapping.get(unit_lower, unit)
        
    def _categorize_device(self, device_id: str) -> str:
        """设备分类"""
        if device_id.startswith('temp_'):
            return 'temperature_sensor'
        elif device_id.startswith('humid_'):
            return 'humidity_sensor'
        elif device_id.startswith('press_'):
            return 'pressure_sensor'
        else:
            return 'unknown_device'
            
    def _categorize_event_type(self, event_type: str) -> str:
        """事件类型分类"""
        if event_type in ['login', 'logout', 'session_start', 'session_end']:
            return 'session_event'
        elif event_type in ['click', 'view', 'purchase', 'search']:
            return 'user_interaction'
        elif event_type in ['api_call', 'service_request', 'database_query']:
            return 'system_event'
        else:
            return 'general_event'
            
    def _classify_metric_type(self, metric_name: str) -> str:
        """指标类型分类"""
        if 'cpu' in metric_name.lower() or 'processor' in metric_name.lower():
            return 'cpu_metric'
        elif 'memory' in metric_name.lower() or 'ram' in metric_name.lower():
            return 'memory_metric'
        elif 'disk' in metric_name.lower() or 'storage' in metric_name.lower():
            return 'disk_metric'
        elif 'network' in metric_name.lower() or 'bandwidth' in metric_name.lower():
            return 'network_metric'
        else:
            return 'general_metric'
            
    def _get_metric_unit(self, metric_name: str) -> str:
        """获取指标单位"""
        unit_mapping = {
            'cpu_usage': '%',
            'memory_usage': '%',
            'disk_usage': '%',
            'network_latency': 'ms',
            'response_time': 'ms',
            'throughput': 'req/s',
            'error_rate': '%',
            'temperature': '°C',
            'humidity': '%'
        }
        
        for key, unit in unit_mapping.items():
            if key in metric_name.lower():
                return unit
                
        return 'unit'
        
    def _calculate_message_hash(self, message: DataMessage) -> str:
        """计算消息哈希"""
        content = f"{message.message_id}{message.source_id}{message.timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()

# =============================================================================
# 5. 滑动窗口聚合器
# =============================================================================

class SlidingWindowAggregator:
    """滑动窗口聚合器"""
    
    def __init__(self, window_size_minutes=5, slide_interval_seconds=60):
        self.window_size = timedelta(minutes=window_size_minutes)
        self.slide_interval = timedelta(seconds=slide_interval_seconds)
        self.data_buffer = defaultdict(lambda: defaultdict(list))
        self.last_slide_time = datetime.now()
        
        # 聚合函数映射
        self.aggregation_functions = {
            'count': len,
            'sum': lambda values: sum(values),
            'avg': lambda values: sum(values) / len(values) if values else 0,
            'min': lambda values: min(values) if values else 0,
            'max': lambda values: max(values) if values else 0,
            'median': self._calculate_median,
            'stddev': self._calculate_stddev
        }
        
    def add_data(self, message: DataMessage):
        """添加数据到滑动窗口"""
        window_key = self._get_window_key(message.timestamp)
        data_key = self._get_data_key(message)
        
        # 添加数据到缓冲区
        self.data_buffer[window_key][data_key].append({
            'timestamp': message.timestamp,
            'value': self._extract_numeric_value(message),
            'message': message
        })
        
        # 清理过期数据
        self._cleanup_expired_data()
        
    def _get_window_key(self, timestamp: datetime) -> str:
        """获取窗口键"""
        window_start = timestamp.replace(
            minute=(timestamp.minute // 5) * 5,  # 5分钟窗口
            second=0,
            microsecond=0
        )
        return window_start.strftime('%Y%m%d%H%M')
        
    def _get_data_key(self, message: DataMessage) -> str:
        """获取数据键"""
        if message.data_type == DataType.SENSOR_DATA:
            return f"{message.payload.get('device_id', 'unknown')}_{message.payload.get('sensor_type', 'unknown')}"
        elif message.data_type == DataType.USER_EVENT:
            return f"{message.payload.get('user_id', 'unknown')}_{message.payload.get('event_type', 'unknown')}"
        else:
            return f"{message.source_id}_{message.data_type.value}"
            
    def _extract_numeric_value(self, message: DataMessage) -> Optional[float]:
        """提取数值"""
        if message.data_type == DataType.SENSOR_DATA:
            return message.payload.get('value')
        elif message.data_type == DataType.SYSTEM_METRIC:
            return message.payload.get('metric_value')
        else:
            return None
            
    def _cleanup_expired_data(self):
        """清理过期数据"""
        current_time = datetime.now()
        cutoff_time = current_time - (self.window_size * 2)  # 保留2倍窗口大小的数据
        
        expired_windows = []
        for window_key in self.data_buffer:
            window_time = datetime.strptime(window_key, '%Y%m%d%H%M')
            if window_time < cutoff_time:
                expired_windows.append(window_key)
                
        for window_key in expired_windows:
            del self.data_buffer[window_key]
            
    def should_slide(self) -> bool:
        """检查是否应该滑动窗口"""
        return datetime.now() - self.last_slide_time >= self.slide_interval
        
    def slide_window(self) -> Dict[str, Any]:
        """执行窗口滑动"""
        if not self.should_slide():
            return {}
            
        # 获取当前窗口数据
        current_window_key = self._get_window_key(datetime.now())
        window_data = self.data_buffer.get(current_window_key, {})
        
        # 计算聚合结果
        aggregated_results = {}
        for data_key, data_points in window_data.items():
            aggregated_results[data_key] = self._aggregate_data_points(data_points)
            
        # 添加窗口信息
        result = {
            'window_start': datetime.strptime(current_window_key, '%Y%m%d%H%M'),
            'window_end': datetime.strptime(current_window_key, '%Y%m%d%H%M') + self.window_size,
            'aggregated_data': aggregated_results,
            'data_point_count': sum(len(points) for points in window_data.values())
        }
        
        self.last_slide_time = datetime.now()
        return result
        
    def _aggregate_data_points(self, data_points: List[Dict]) -> Dict[str, Any]:
        """聚合数据点"""
        if not data_points:
            return {}
            
        # 提取数值
        values = [point['value'] for point in data_points if point['value'] is not None]
        
        if not values:
            return {}
            
        # 计算各种聚合值
        result = {}
        for agg_name, agg_func in self.aggregation_functions.items():
            try:
                result[agg_name] = agg_func(values)
            except Exception as e:
                result[agg_name] = 0.0
                
        # 添加时间范围信息
        timestamps = [point['timestamp'] for point in data_points]
        result['time_range'] = {
            'start': min(timestamps).isoformat(),
            'end': max(timestamps).isoformat()
        }
        
        return result
        
    def _calculate_median(self, values: List[float]) -> float:
        """计算中位数"""
        if not values:
            return 0.0
            
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
            
    def _calculate_stddev(self, values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0.0
            
        import statistics
        try:
            return statistics.stdev(values)
        except statistics.StatisticsError:
            return 0.0

# =============================================================================
# 6. 数据丰富服务
# =============================================================================

class DataEnrichmentService:
    """数据丰富服务"""
    
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
        self.enrichment_sources = {
            'geolocation': GeoLocationService(),
            'user_profile': UserProfileService(),
            'device_info': DeviceInfoService(),
            'business_context': BusinessContextService()
        }
        
    def enrich_message(self, message: DataMessage) -> DataMessage:
        """丰富消息数据"""
        try:
            enriched_metadata = {}
            
            # 根据数据类型进行相应的丰富
            if message.data_type == DataType.SENSOR_DATA:
                enriched_metadata.update(self._enrich_sensor_data(message))
            elif message.data_type == DataType.USER_EVENT:
                enriched_metadata.update(self._enrich_user_event(message))
            elif message.data_type == DataType.SYSTEM_METRIC:
                enriched_metadata.update(self._enrich_system_metric(message))
                
            # 更新消息元数据
            if message.metadata is None:
                message.metadata = {}
                
            message.metadata.update(enriched_metadata)
            message.metadata['enriched_at'] = datetime.now().isoformat()
            
            # 记录丰富阶段
            if ProcessingStage.ENRICHMENT not in message.processed_stages:
                message.processed_stages.append(ProcessingStage.ENRICHMENT)
                
            return message
            
        except Exception as e:
            print(f"数据丰富错误: {e}")
            return message
            
    def _enrich_sensor_data(self, message: DataMessage) -> Dict[str, Any]:
        """丰富传感器数据"""
        enrichment = {}
        
        device_id = message.payload.get('device_id')
        if device_id:
            # 获取设备信息
            device_info = self.enrichment_sources['device_info'].get_device_info(device_id)
            enrichment['device_info'] = device_info
            
            # 获取设备地理位置
            if device_info and 'location' in device_info:
                enrichment['geolocation'] = device_info['location']
                
        return enrichment
        
    def _enrich_user_event(self, message: DataMessage) -> Dict[str, Any]:
        """丰富用户事件"""
        enrichment = {}
        
        user_id = message.payload.get('user_id')
        if user_id:
            # 获取用户画像
            user_profile = self.enrichment_sources['user_profile'].get_user_profile(user_id)
            enrichment['user_profile'] = user_profile
            
            # 获取地理位置（如果有IP地址）
            if 'ip_address' in message.payload:
                geo_info = self.enrichment_sources['geolocation'].lookup(message.payload['ip_address'])
                enrichment['geolocation'] = geo_info
                
        return enrichment
        
    def _enrich_system_metric(self, message: DataMessage) -> Dict[str, Any]:
        """丰富系统指标"""
        enrichment = {}
        
        source = message.payload.get('source', message.source_id)
        
        # 添加业务上下文
        business_context = self.enrichment_sources['business_context'].get_context(source)
        enrichment['business_context'] = business_context
        
        return enrichment

# =============================================================================
# 7. 数据丰富源服务（模拟）
# =============================================================================

class GeoLocationService:
    """地理位置服务"""
    
    def __init__(self):
        self.geo_cache = {}
        
    def lookup(self, ip_address: str) -> Dict[str, Any]:
        """查找IP地址地理位置"""
        # 模拟地理位置数据
        return {
            'country': 'CN',
            'region': 'Beijing',
            'city': 'Beijing',
            'latitude': 39.9042,
            'longitude': 116.4074,
            'timezone': 'Asia/Shanghai'
        }

class UserProfileService:
    """用户画像服务"""
    
    def __init__(self):
        self.profile_cache = {}
        
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        # 模拟用户画像数据
        return {
            'age_group': '25-35',
            'gender': 'unknown',
            'interests': ['technology', 'data_analysis'],
            'subscription_level': 'premium',
            'last_active': datetime.now().isoformat(),
            'preferences': {
                'language': 'zh-CN',
                'notifications': True
            }
        }

class DeviceInfoService:
    """设备信息服务"""
    
    def __init__(self):
        self.device_cache = {}
        
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取设备信息"""
        # 模拟设备信息数据
        if device_id.startswith('temp_'):
            return {
                'device_type': 'temperature_sensor',
                'model': 'DHT22',
                'location': {
                    'building': 'Building A',
                    'floor': 3,
                    'room': 'Server Room'
                },
                'manufacturer': 'Adafruit',
                'specifications': {
                    'accuracy': '±0.5°C',
                    'range': '-40°C to 80°C'
                }
            }
        else:
            return {
                'device_type': 'unknown',
                'location': {
                    'building': 'Unknown',
                    'floor': 1,
                    'room': 'Unknown'
                }
            }

class BusinessContextService:
    """业务上下文服务"""
    
    def __init__(self):
        self.context_cache = {}
        
    def get_context(self, source: str) -> Dict[str, Any]:
        """获取业务上下文"""
        # 模拟业务上下文数据
        return {
            'service_name': source,
            'environment': 'production',
            'business_critical': source in ['payment_service', 'user_service'],
            'owner_team': 'backend_team',
            'sla_level': 'high' if source in ['payment_service', 'user_service'] else 'medium'
        }

# =============================================================================
# 8. 数据流处理编排器
# =============================================================================

class DataFlowOrchestrator:
    """数据流处理编排器"""
    
    def __init__(self, rabbitmq_config=None, redis_config=None):
        # 初始化组件
        self.rabbitmq = RabbitMQConnector(**(rabbitmq_config or {}))
        self.cache = RedisCache(**(redis_config or {}))
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.aggregator = SlidingWindowAggregator()
        self.enricher = DataEnrichmentService(self.cache)
        
        # 性能指标
        self.metrics = defaultdict(ProcessingMetrics)
        self.processing_stats = {
            'total_messages': 0,
            'successful_messages': 0,
            'failed_messages': 0,
            'avg_processing_time': 0.0
        }
        
        # 线程控制
        self.is_running = False
        self.processing_threads = []
        
    def start(self):
        """启动数据流处理"""
        print("🚀 启动实时数据流处理系统...")
        
        try:
            # 建立连接
            self.rabbitmq.connect()
            
            # 声明队列
            self.setup_queues()
            
            # 设置消费者
            self.setup_consumers()
            
            # 启动处理线程
            self.start_processing_threads()
            
            self.is_running = True
            print("✅ 数据流处理系统启动成功")
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            raise
            
    def stop(self):
        """停止数据流处理"""
        print("🛑 停止数据流处理系统...")
        
        self.is_running = False
        
        # 停止所有线程
        for thread in self.processing_threads:
            if thread.is_alive():
                thread.join(timeout=5)
                
        # 断开连接
        self.rabbitmq.disconnect()
        
        print("✅ 数据流处理系统已停止")
        
    def setup_queues(self):
        """设置队列"""
        queues = [
            ('raw_data_queue', 'data_ingestion', '*.raw.*'),
            ('validated_data_queue', 'processing_pipeline', '*.validated.*'),
            ('transformed_data_queue', 'processing_pipeline', '*.transformed.*'),
            ('aggregated_data_queue', 'aggregated_data', ''),
            ('output_queue', 'data_ingestion', '*.output.*')
        ]
        
        for queue_name, exchange, routing_key in queues:
            queue = self.rabbitmq.declare_queue(queue_name)
            self.rabbitmq.channel.queue_bind(
                exchange=exchange,
                queue=queue,
                routing_key=routing_key
            )
            
    def setup_consumers(self):
        """设置消费者"""
        # 原始数据消费者
        self.rabbitmq.channel.basic_qos(prefetch_count=10)
        
    def start_processing_threads(self):
        """启动处理线程"""
        # 数据验证线程
        validation_thread = threading.Thread(target=self.validation_worker, daemon=True)
        validation_thread.start()
        self.processing_threads.append(validation_thread)
        
        # 数据转换线程
        transformation_thread = threading.Thread(target=self.transformation_worker, daemon=True)
        transformation_thread.start()
        self.processing_threads.append(transformation_thread)
        
        # 聚合线程
        aggregation_thread = threading.Thread(target=self.aggregation_worker, daemon=True)
        aggregation_thread.start()
        self.processing_threads.append(aggregation_thread)
        
        # 丰富线程
        enrichment_thread = threading.Thread(target=self.enrichment_worker, daemon=True)
        enrichment_thread.start()
        self.processing_threads.append(enrichment_thread)
        
    def validation_worker(self):
        """数据验证工作线程"""
        while self.is_running:
            try:
                # 模拟从队列获取数据
                raw_messages = self.simulate_get_messages('raw_data_queue', batch_size=5)
                
                for message_data in raw_messages:
                    message = self.parse_message(message_data)
                    if message and self.validator.validate(message):
                        # 发送到验证后队列
                        self.rabbitmq.publish(
                            'processing_pipeline',
                            f'validated.{message.source_id}',
                            message
                        )
                        self.update_metrics(ProcessingStage.VALIDATION, success=True)
                    else:
                        self.update_metrics(ProcessingStage.VALIDATION, success=False)
                        
            except Exception as e:
                print(f"验证线程错误: {e}")
                
            time.sleep(0.1)
            
    def transformation_worker(self):
        """数据转换工作线程"""
        while self.is_running:
            try:
                validated_messages = self.simulate_get_messages('validated_data_queue', batch_size=5)
                
                for message_data in validated_messages:
                    message = self.parse_message(message_data)
                    if message:
                        transformed_message = self.transformer.transform(message)
                        # 发送到转换后队列
                        self.rabbitmq.publish(
                            'processing_pipeline',
                            f'transformed.{message.source_id}',
                            transformed_message
                        )
                        self.update_metrics(ProcessingStage.TRANSFORMATION, success=True)
                        
            except Exception as e:
                print(f"转换线程错误: {e}")
                
            time.sleep(0.1)
            
    def aggregation_worker(self):
        """聚合工作线程"""
        while self.is_running:
            try:
                transformed_messages = self.simulate_get_messages('transformed_data_queue', batch_size=10)
                
                for message_data in transformed_messages:
                    message = self.parse_message(message_data)
                    if message:
                        # 添加到聚合器
                        self.aggregator.add_data(message)
                        
                # 检查是否需要滑动窗口
                if self.aggregator.should_slide():
                    window_result = self.aggregator.slide_window()
                    if window_result:
                        # 发布聚合结果
                        self.publish_aggregated_result(window_result)
                        
                self.update_metrics(ProcessingStage.AGGREGATION, success=True)
                
            except Exception as e:
                print(f"聚合线程错误: {e}")
                
            time.sleep(1)
            
    def enrichment_worker(self):
        """数据丰富工作线程"""
        while self.is_running:
            try:
                # 获取需要丰富的数据
                enrichment_messages = self.simulate_get_messages('aggregated_data_queue', batch_size=3)
                
                for message_data in enrichment_messages:
                    message = self.parse_message(message_data)
                    if message:
                        enriched_message = self.enricher.enrich_message(message)
                        # 发送到输出队列
                        self.rabbitmq.publish(
                            'data_ingestion',
                            f'output.{message.source_id}',
                            enriched_message
                        )
                        self.update_metrics(ProcessingStage.ENRICHMENT, success=True)
                        
            except Exception as e:
                print(f"丰富线程错误: {e}")
                
            time.sleep(0.5)
            
    def simulate_get_messages(self, queue_name: str, batch_size: int = 1) -> List[str]:
        """模拟从队列获取消息（实际应用中替换为真实的RabbitMQ消费）"""
        # 这里模拟生成测试数据
        messages = []
        for i in range(batch_size):
            if self.should_generate_test_data():
                message = self.generate_test_message()
                messages.append(json.dumps(message))
        return messages
        
    def should_generate_test_data(self) -> bool:
        """判断是否应该生成测试数据"""
        return datetime.now().second % 3 == 0  # 每3秒生成一批数据
        
    def generate_test_message(self) -> Dict[str, Any]:
        """生成测试消息"""
        message_id = str(uuid.uuid4())
        data_types = list(DataType)
        data_type = data_types[datetime.now().second % len(data_types)]
        
        base_message = {
            'message_id': message_id,
            'data_type': data_type.value,
            'timestamp': datetime.now().isoformat(),
            'source_id': f'source_{datetime.now().second % 10}',
            'payload': {},
            'metadata': {'generated_at': datetime.now().isoformat()}
        }
        
        if data_type == DataType.SENSOR_DATA:
            base_message['payload'] = {
                'device_id': f'temp_sensor_{datetime.now().second % 5}',
                'sensor_type': 'temperature',
                'value': round(20 + (datetime.now().second % 10) * 0.5, 1),
                'unit': '°C'
            }
        elif data_type == DataType.USER_EVENT:
            base_message['payload'] = {
                'user_id': f'user_{datetime.now().second % 100}',
                'event_type': ['login', 'click', 'view', 'purchase'][datetime.now().second % 4],
                'ip_address': f'192.168.1.{datetime.now().second % 255}'
            }
        elif data_type == DataType.SYSTEM_METRIC:
            base_message['payload'] = {
                'metric_name': 'cpu_usage',
                'metric_value': round(50 + (datetime.now().second % 50), 1),
                'source': 'server_01'
            }
            
        return base_message
        
    def parse_message(self, message_data: str) -> Optional[DataMessage]:
        """解析消息"""
        try:
            data = json.loads(message_data)
            return DataMessage(**data)
        except Exception as e:
            print(f"消息解析错误: {e}")
            return None
            
    def publish_aggregated_result(self, window_result: Dict[str, Any]):
        """发布聚合结果"""
        aggregation_message = DataMessage(
            message_id=str(uuid.uuid4()),
            data_type=DataType.BUSINESS_EVENT,
            timestamp=datetime.now(),
            source_id='aggregation_engine',
            payload=window_result,
            metadata={
                'aggregation_type': 'sliding_window',
                'window_size_minutes': 5,
                'generated_at': datetime.now().isoformat()
            }
        )
        
        self.rabbitmq.publish(
            'aggregated_data',
            'aggregated.results',
            aggregation_message
        )
        
    def update_metrics(self, stage: ProcessingStage, success: bool = True, processing_time: float = 0.0):
        """更新处理指标"""
        if stage not in self.metrics:
            self.metrics[stage] = ProcessingMetrics(stage=stage, start_time=datetime.now())
            
        self.metrics[stage].message_count += 1
        if not success:
            self.metrics[stage].error_count += 1
            
        # 更新处理时间统计
        if processing_time > 0:
            current_avg = self.metrics[stage].avg_processing_time
            count = self.metrics[stage].message_count
            self.metrics[stage].avg_processing_time = (current_avg * (count - 1) + processing_time) / count
            
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        stats = self.processing_stats.copy()
        
        # 添加各阶段详细指标
        stats['stage_metrics'] = {}
        for stage, metrics in self.metrics.items():
            stats['stage_metrics'][stage.value] = {
                'message_count': metrics.message_count,
                'error_count': metrics.error_count,
                'success_rate': (metrics.message_count - metrics.error_count) / max(metrics.message_count, 1),
                'avg_processing_time': metrics.avg_processing_time
            }
            
        return stats
        
    def print_dashboard(self):
        """打印处理仪表板"""
        stats = self.get_processing_stats()
        
        print("\n" + "="*60)
        print("📊 实时数据流处理仪表板")
        print("="*60)
        print(f"📈 总处理消息数: {stats['total_messages']:,}")
        print(f"✅ 成功消息数: {stats['successful_messages']:,}")
        print(f"❌ 失败消息数: {stats['failed_messages']:,}")
        print(f"⏱️  平均处理时间: {stats['avg_processing_time']:.3f}s")
        
        print("\n📋 各阶段处理情况:")
        for stage_name, stage_stats in stats['stage_metrics'].items():
            print(f"  {stage_name}: {stage_stats['message_count']:,} 消息, "
                  f"{stage_stats['success_rate']:.1%} 成功率, "
                  f"{stage_stats['avg_processing_time']:.3f}s 平均耗时")
                  
        print("="*60)

# =============================================================================
# 9. 演示程序
# =============================================================================

def main():
    """主演示程序"""
    print("🎯 RabbitMQ实时数据流处理管道演示")
    print("="*50)
    
    # 配置
    rabbitmq_config = {
        'host': 'localhost',
        'port': 5672,
        'username': 'admin',
        'password': 'admin'
    }
    
    redis_config = {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
    
    # 创建编排器
    orchestrator = DataFlowOrchestrator(rabbitmq_config, redis_config)
    
    try:
        # 启动处理系统
        orchestrator.start()
        
        # 运行演示
        print("🔄 开始处理实时数据流...")
        print("⏰ 演示将运行30秒，显示实时处理统计")
        
        start_time = time.time()
        dashboard_interval = 5  # 每5秒显示一次仪表板
        
        while time.time() - start_time < 30:
            time.sleep(dashboard_interval)
            
            # 更新统计数据（模拟）
            orchestrator.processing_stats['total_messages'] += 50
            orchestrator.processing_stats['successful_messages'] += 48
            orchestrator.processing_stats['failed_messages'] += 2
            
            # 显示仪表板
            orchestrator.print_dashboard()
            
        print("\n🎉 演示完成！")
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示错误: {e}")
    finally:
        # 停止系统
        orchestrator.stop()

if __name__ == "__main__":
    main()