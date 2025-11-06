# 第12天：告警与通知系统

## 用户故事1：配置告警系统

**标题**：设置全面的告警系统

**描述**：配置Superset的告警系统，用于监控数据条件、图表阈值和系统性能，并提供自动通知。

**验收标准**：
- 告警系统已配置
- 告警条件已定义
- 告警阈值已设置
- 告警测试已实现
- 告警历史已跟踪

**分步指南**：

1. **告警配置设置**：
```python
# superset_config.py
# 告警系统配置
ALERT_CONFIG = {
    'enabled': True,
    'alert_types': [
        'chart_threshold',
        'data_quality',
        'system_performance',
        'custom_metric'
    ],
    'notification_channels': [
        'email',
        'slack',
        'webhook',
        'sms'
    ],
    'alert_cooldown': 300,  # 5分钟
    'max_alerts_per_hour': 10
}

# 告警阈值配置
ALERT_THRESHOLDS = {
    'sales_threshold': {
        'metric': 'total_sales',
        'operator': 'lt',
        'value': 10000,
        'time_window': '1 day',
        'notification_channels': ['email', 'slack']
    },
    'error_rate_threshold': {
        'metric': 'error_rate',
        'operator': 'gt',
        'value': 0.05,
        'time_window': '1 hour',
        'notification_channels': ['email', 'webhook']
    }
}
```

2. **告警条件定义**：
```sql
-- 销售监控的告警条件查询
SELECT 
    DATE(order_date) as alert_date,
    SUM(sales_amount) as daily_sales,
    COUNT(*) as order_count
FROM sales_data
WHERE order_date >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY DATE(order_date)
HAVING SUM(sales_amount) < 10000;

-- 数据质量告警条件
SELECT 
    'data_quality_alert' as alert_type,
    COUNT(*) as null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales_data) as null_percentage
FROM sales_data
WHERE customer_id IS NULL 
   OR order_date IS NULL 
   OR sales_amount IS NULL;
```

3. **告警测试和验证**：
```python
# 告警测试配置
ALERT_TESTING_CONFIG = {
    'test_mode': True,
    'test_notification_channel': 'email',
    'test_recipients': ['admin@example.com'],
    'test_frequency': 'daily',
    'test_time': '09:00'
}

# 告警验证函数
def validate_alert_condition(alert_config):
    """验证告警条件并测试通知"""
    
    # 测试告警条件
    condition_result = test_alert_condition(alert_config)
    
    # 发送测试通知
    if condition_result['triggered']:
        send_test_notification(alert_config)
    
    # 记录测试结果
    log_alert_test(alert_config, condition_result)
    
    return condition_result
```

**参考文档**：
- [告警配置](https://superset.apache.org/docs/using-superset/alerts)
- [告警类型](https://superset.apache.org/docs/using-superset/alerts#alert-types)

---

## 用户故事2：通知渠道设置

**标题**：配置多个通知渠道

**描述**：设置包括电子邮件、Slack、Webhook和SMS在内的各种通知渠道，用于告警传递。

**验收标准**：
- 电子邮件通知已配置
- Slack集成正常工作
- Webhook通知已设置
- SMS通知可用
- 通知模板已创建

**分步指南**：

1. **电子邮件通知设置**：
```python
# 电子邮件通知配置
EMAIL_NOTIFICATION_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_username': 'alerts@example.com',
    'smtp_password': 'secure_password',
    'smtp_use_tls': True,
    'from_email': 'alerts@example.com',
    'from_name': 'Superset Alerts'
}

# 电子邮件模板配置
EMAIL_TEMPLATES = {
    'alert_notification': {
        'subject': 'Superset Alert: {alert_name}',
        'template': 'alert_email_template.html',
        'variables': ['alert_name', 'alert_value', 'threshold', 'timestamp']
    },
    'daily_summary': {
        'subject': 'Daily Alert Summary - {date}',
        'template': 'daily_summary_template.html',
        'variables': ['date', 'alert_count', 'alert_details']
    }
}
```

2. **Slack集成**：
```python
# Slack通知配置
SLACK_CONFIG = {
    'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    'channel': '#alerts',
    'username': 'Superset Alerts',
    'icon_emoji': ':warning:',
    'message_template': {
        'text': 'Alert: {alert_name}',
        'attachments': [
            {
                'color': 'danger',
                'fields': [
                    {'title': 'Alert Value', 'value': '{alert_value}', 'short': True},
                    {'title': 'Threshold', 'value': '{threshold}', 'short': True},
                    {'title': 'Time', 'value': '{timestamp}', 'short': True}
                ]
            }
        ]
    }
}

# Slack通知函数
def send_slack_notification(alert_data):
    """发送告警通知到Slack"""
    import requests
    
    message = format_slack_message(alert_data)
    
    response = requests.post(
        SLACK_CONFIG['webhook_url'],
        json=message,
        headers={'Content-Type': 'application/json'}
    )
    
    return response.status_code == 200
```

3. **Webhook配置**：
```python
# Webhook通知配置
WEBHOOK_CONFIG = {
    'endpoints': {
        'pagerduty': {
            'url': 'https://events.pagerduty.com/v2/enqueue',
            'headers': {
                'Content-Type': 'application/json',
                'X-Routing-Key': 'your-routing-key'
            },
            'payload_template': {
                'routing_key': 'your-routing-key',
                'event_action': 'trigger',
                'payload': {
                    'summary': 'Superset Alert: {alert_name}',
                    'severity': 'warning',
                    'source': 'superset',
                    'custom_details': {
                        'alert_value': '{alert_value}',
                        'threshold': '{threshold}',
                        'timestamp': '{timestamp}'
                    }
                }
            }
        },
        'custom_api': {
            'url': 'https://api.example.com/alerts',
            'headers': {
                'Authorization': 'Bearer your-api-token',
                'Content-Type': 'application/json'
            },
            'payload_template': {
                'alert_name': '{alert_name}',
                'alert_value': '{alert_value}',
                'threshold': '{threshold}',
                'timestamp': '{timestamp}'
            }
        }
    }
}
```

**参考文档**：
- [通知渠道](https://superset.apache.org/docs/using-superset/alerts#notification-channels)
- [电子邮件配置](https://superset.apache.org/docs/installation/email-reports)

---

## 用户故事3：自定义告警规则

**标题**：创建自定义告警规则和条件

**描述**：为特定业务需求开发自定义告警规则，包括复杂条件、多指标告警和条件通知。

**验收标准**：
- 自定义告警规则已创建
- 支持复杂条件
- 多指标告警正常工作
- 条件通知已实现
- 告警规则可测试

**分步指南**：

1. **自定义告警规则定义**：
```python
# 自定义告警规则配置
CUSTOM_ALERT_RULES = {
    'sales_decline_alert': {
        'name': 'Sales Decline Alert',
        'description': 'Alert when sales decline by more than 20%',
        'query': """
            SELECT 
                DATE(order_date) as date,
                SUM(sales_amount) as daily_sales,
                LAG(SUM(sales_amount)) OVER (ORDER BY DATE(order_date)) as prev_day_sales
            FROM sales_data
            WHERE order_date >= CURRENT_DATE - INTERVAL '2 days'
            GROUP BY DATE(order_date)
            HAVING SUM(sales_amount) < LAG(SUM(sales_amount)) OVER (ORDER BY DATE(order_date)) * 0.8
        """,
        'condition': 'daily_sales < prev_day_sales * 0.8',
        'notification_channels': ['email', 'slack'],
        'severity': 'high'
    },
    
    'data_quality_alert': {
        'name': 'Data Quality Alert',
        'description': 'Alert when data quality issues are detected',
        'query': """
            SELECT 
                'data_quality' as alert_type,
                COUNT(*) as null_records,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales_data) as null_percentage
            FROM sales_data
            WHERE customer_id IS NULL 
               OR order_date IS NULL 
               OR sales_amount IS NULL
        """,
        'condition': 'null_percentage > 5',
        'notification_channels': ['email', 'webhook'],
        'severity': 'critical'
    }
}
```

2. **多指标告警规则**：
```python
# 多指标告警配置
MULTI_METRIC_ALERTS = {
    'performance_degradation': {
        'name': 'Performance Degradation Alert',
        'metrics': [
            {
                'name': 'query_response_time',
                'threshold': 30,
                'operator': 'gt'
            },
            {
                'name': 'cache_hit_ratio',
                'threshold': 0.8,
                'operator': 'lt'
            },
            {
                'name': 'error_rate',
                'threshold': 0.05,
                'operator': 'gt'
            }
        ],
        'condition': 'all',  # 所有指标必须触发
        'notification_channels': ['email', 'slack'],
        'severity': 'high'
    }
}

# 多指标告警评估
def evaluate_multi_metric_alert(alert_config):
    """评估多指标告警条件"""
    
    triggered_metrics = []
    
    for metric in alert_config['metrics']:
        current_value = get_metric_value(metric['name'])
        
        if evaluate_condition(current_value, metric['threshold'], metric['operator']):
            triggered_metrics.append(metric['name'])
    
    # 根据条件检查是否应该触发告警
    if alert_config['condition'] == 'all':
        return len(triggered_metrics) == len(alert_config['metrics'])
    elif alert_config['condition'] == 'any':
        return len(triggered_metrics) > 0
    
    return False
```

3. **条件通知规则**：
```python
# 条件通知配置
CONDITIONAL_NOTIFICATIONS = {
    'escalation_rules': {
        'level_1': {
            'condition': 'alert_count < 3',
            'notification_channels': ['email'],
            'recipients': ['analyst@example.com']
        },
        'level_2': {
            'condition': 'alert_count >= 3 AND alert_count < 5',
            'notification_channels': ['email', 'slack'],
            'recipients': ['manager@example.com']
        },
        'level_3': {
            'condition': 'alert_count >= 5',
            'notification_channels': ['email', 'slack', 'sms'],
            'recipients': ['director@example.com', 'oncall@example.com']
        }
    }
}

# 条件通知函数
def send_conditional_notification(alert_data):
    """根据升级规则发送通知"""
    
    alert_count = get_alert_count_in_window(hours=1)
    
    for level, rules in CONDITIONAL_NOTIFICATIONS['escalation_rules'].items():
        if evaluate_condition(alert_count, rules['condition']):
            for channel in rules['notification_channels']:
                send_notification(
                    channel=channel,
                    alert_data=alert_data,
                    recipients=rules['recipients']
                )
            break
```

**参考文档**：
- [自定义告警规则](https://superset.apache.org/docs/using-superset/alerts#custom-rules)
- [告警条件](https://superset.apache.org/docs/using-superset/alerts#conditions)

---

## 用户故事4：告警监控和管理

**标题**：监控和管理告警系统

**描述**：为告警系统实现全面的监控和管理功能，包括告警历史、性能跟踪和系统健康监控。

**验收标准**：
- 告警历史已跟踪
- 告警性能已监控
- 系统健康已跟踪
- 告警管理界面可用
- 告警分析已提供

**分步指南**：

1. **告警历史跟踪**：
```sql
-- 告警历史表
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    alert_name VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_value DECIMAL(10,2),
    threshold_value DECIMAL(10,2),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    notification_channels TEXT[],
    recipients TEXT[],
    status VARCHAR(20) DEFAULT 'active',
    severity VARCHAR(20),
    notes TEXT
);

-- 告警历史查询
SELECT 
    alert_name,
    COUNT(*) as trigger_count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - triggered_at))) as avg_resolution_time,
    MAX(triggered_at) as last_triggered
FROM alert_history
WHERE triggered_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY alert_name
ORDER BY trigger_count DESC;
```

2. **告警性能监控**：
```python
# 告警性能监控
ALERT_PERFORMANCE_MONITORING = {
    'enabled': True,
    'metrics': [
        'alert_frequency',
        'notification_delivery_rate',
        'false_positive_rate',
        'resolution_time',
        'alert_accuracy'
    ],
    'collection_interval': 300,  # 5分钟
    'retention_period': 90  # 天
}

# 告警性能跟踪
def track_alert_performance(alert_data):
    """跟踪告警性能指标"""
    
    metrics = {
        'alert_frequency': calculate_alert_frequency(alert_data['alert_name']),
        'delivery_rate': calculate_notification_delivery_rate(alert_data),
        'false_positive_rate': calculate_false_positive_rate(alert_data),
        'resolution_time': calculate_avg_resolution_time(alert_data['alert_name']),
        'accuracy': calculate_alert_accuracy(alert_data)
    }
    
    # 存储性能指标
    store_alert_performance_metrics(metrics)
    
    # 生成性能报告
    if should_generate_performance_report():
        generate_alert_performance_report()
    
    return metrics
```

3. **告警管理界面**：
```python
# 告警管理配置
ALERT_MANAGEMENT_CONFIG = {
    'dashboard_enabled': True,
    'features': [
        'alert_status_overview',
        'alert_history',
        'performance_metrics',
        'configuration_management',
        'test_alerts'
    ],
    'permissions': {
        'view_alerts': ['admin', 'analyst'],
        'configure_alerts': ['admin'],
        'test_alerts': ['admin', 'analyst'],
        'manage_notifications': ['admin']
    }
}

# 告警管理函数
def get_alert_dashboard_data():
    """获取告警管理仪表盘数据"""
    
    return {
        'active_alerts': get_active_alerts_count(),
        'alert_history': get_recent_alert_history(),
        'performance_metrics': get_alert_performance_metrics(),
        'notification_status': get_notification_delivery_status(),
        'system_health': get_alert_system_health()
    }

def manage_alert_configuration(alert_name, action, config):
    """管理告警配置"""
    
    if action == 'update':
        update_alert_configuration(alert_name, config)
    elif action == 'disable':
        disable_alert(alert_name)
    elif action == 'enable':
        enable_alert(alert_name)
    elif action == 'test':
        test_alert_configuration(alert_name)
    
    # 记录配置更改
    log_alert_configuration_change(alert_name, action, config)
```

**参考文档**：
- [告警管理](https://superset.apache.org/docs/using-superset/alerts#management)
- [告警监控](https://superset.apache.org/docs/installation/monitoring#alerts)

---

## 用户故事5：高级告警功能

**标题**：实现高级告警功能

**描述**：开发高级告警功能，包括告警关联、预测性告警和智能告警路由。

**验收标准**：
- 告警关联已实现
- 预测性告警已配置
- 智能路由已设置
- 告警抑制正常工作
- 高级分析可用

**分步指南**：

1. **告警关联**：
```python
# 告警关联配置
ALERT_CORRELATION_CONFIG = {
    'enabled': True,
    'correlation_rules': {
        'database_performance': {
            'primary_alert': 'high_query_time',
            'correlated_alerts': ['low_cache_hit_ratio', 'high_memory_usage'],
            'correlation_window': 300,  # 5分钟
            'action': 'suppress_correlated'
        },
        'data_pipeline': {
            'primary_alert': 'data_quality_issue',
            'correlated_alerts': ['missing_data', 'delayed_processing'],
            'correlation_window': 600,  # 10分钟
            'action': 'escalate_primary'
        }
    }
}

# 告警关联函数
def correlate_alerts(triggered_alert):
    """根据定义的规则关联告警"""
    
    for rule_name, rule in ALERT_CORRELATION_CONFIG['correlation_rules'].items():
        if triggered_alert['name'] == rule['primary_alert']:
            
            # 检查相关告警
            correlated_alerts = find_correlated_alerts(
                rule['correlated_alerts'],
                rule['correlation_window']
            )
            
            if correlated_alerts:
                handle_correlated_alerts(triggered_alert, correlated_alerts, rule)
    
    return True
```

2. **预测性告警**：
```python
# 预测性告警配置
PREDICTIVE_ALERTS_CONFIG = {
    'enabled': True,
    'prediction_models': {
        'sales_decline_prediction': {
            'metric': 'daily_sales',
            'prediction_window': 7,  # 天
            'confidence_threshold': 0.8,
            'training_data_days': 90,
            'algorithm': 'linear_regression'
        },
        'system_overload_prediction': {
            'metric': 'cpu_usage',
            'prediction_window': 1,  # 小时
            'confidence_threshold': 0.9,
            'training_data_days': 30,
            'algorithm': 'time_series_forecasting'
        }
    }
}

# 预测性告警函数
def generate_predictive_alerts():
    """基于历史数据生成预测性告警"""
    
    for model_name, model_config in PREDICTIVE_ALERTS_CONFIG['prediction_models'].items():
        
        # 获取历史数据
        historical_data = get_historical_metric_data(
            model_config['metric'],
            days=model_config['training_data_days']
        )
        
        # 生成预测
        prediction = generate_prediction(
            historical_data,
            model_config['algorithm'],
            model_config['prediction_window']
        )
        
        # 检查预测是否超过阈值
        if prediction['confidence'] >= model_config['confidence_threshold']:
            if prediction['trend'] == 'declining' and prediction['value'] < threshold:
                create_predictive_alert(model_name, prediction)
```

3. **智能告警路由**：
```python
# 智能路由配置
INTELLIGENT_ROUTING_CONFIG = {
    'enabled': True,
    'routing_rules': {
        'severity_based': {
            'critical': ['oncall@example.com', 'manager@example.com'],
            'high': ['analyst@example.com', 'manager@example.com'],
            'medium': ['analyst@example.com'],
            'low': ['analyst@example.com']
        },
        'time_based': {
            'business_hours': ['analyst@example.com', 'manager@example.com'],
            'after_hours': ['oncall@example.com'],
            'weekends': ['oncall@example.com']
        },
        'expertise_based': {
            'database_issues': ['dba@example.com'],
            'performance_issues': ['devops@example.com'],
            'data_quality': ['data_team@example.com']
        }
    }
}

# 智能路由函数
def route_alert_intelligently(alert_data):
    """根据智能规则路由告警"""
    
    recipients = set()
    
    # 基于严重性的路由
    severity_recipients = INTELLIGENT_ROUTING_CONFIG['routing_rules']['severity_based'].get(
        alert_data['severity'], []
    )
    recipients.update(severity_recipients)
    
    # 基于时间的路由
    current_time = datetime.now()
    if is_business_hours(current_time):
        time_recipients = INTELLIGENT_ROUTING_CONFIG['routing_rules']['time_based']['business_hours']
    elif is_after_hours(current_time):
        time_recipients = INTELLIGENT_ROUTING_CONFIG['routing_rules']['time_based']['after_hours']
    else:
        time_recipients = INTELLIGENT_ROUTING_CONFIG['routing_rules']['time_based']['weekends']
    
    recipients.update(time_recipients)
    
    # 基于专业知识的路由
    if 'database' in alert_data['alert_name'].lower():
        expertise_recipients = INTELLIGENT_ROUTING_CONFIG['routing_rules']['expertise_based']['database_issues']
        recipients.update(expertise_recipients)
    
    return list(recipients)
```

**参考文档**：
- [高级告警功能](https://superset.apache.org/docs/using-superset/alerts#advanced-features)
- [告警分析](https://superset.apache.org/docs/using-superset/alerts#analytics)

---

## 总结

本章节涵盖的关键告警和通知概念：
- **告警系统**：配置、条件、测试
- **通知渠道**：电子邮件、Slack、Webhook、SMS
- **自定义规则**：复杂条件、多指标告警
- **监控**：历史跟踪、性能监控
- **高级功能**：关联、预测性告警、智能路由

**后续步骤**：
- 配置告警系统
- 设置通知渠道
- 创建自定义告警规则
- 实现监控和管理
- 部署高级告警功能