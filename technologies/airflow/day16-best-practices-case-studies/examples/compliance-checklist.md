# Apache Airflow 合规性检查清单

## 1. 概述

### 1.1 目的
本文档旨在为Apache Airflow生产环境提供全面的合规性检查清单，确保系统符合各种行业标准和法规要求，包括但不限于GDPR、HIPAA、SOX、PCI DSS等。

### 1.2 适用范围
本检查清单适用于所有运行Apache Airflow的环境，包括开发、测试、预生产和生产环境。

### 1.3 合规性框架
```yaml
# 合规性框架映射
compliance_frameworks:
  gdpr:
    name: "General Data Protection Regulation"
    scope: "数据保护和隐私"
    applicable: true
    
  hipaa:
    name: "Health Insurance Portability and Accountability Act"
    scope: "医疗健康数据保护"
    applicable: false
    
  sox:
    name: "Sarbanes-Oxley Act"
    scope: "财务报告和内部控制"
    applicable: true
    
  pci_dss:
    name: "Payment Card Industry Data Security Standard"
    scope: "支付卡数据安全"
    applicable: false
    
  iso_27001:
    name: "ISO/IEC 27001"
    scope: "信息安全管理体系"
    applicable: true
    
  soc_2:
    name: "Service Organization Control 2"
    scope: "服务组织控制"
    applicable: true
```

## 2. 数据保护合规性

### 2.1 数据分类和标记
```yaml
# 数据分类策略
data_classification:
  public:
    description: "公开数据，可对外发布"
    examples: ["公开文档", "营销材料"]
    protection_level: "最低"
    
  internal:
    description: "内部数据，仅限公司内部使用"
    examples: ["内部报告", "员工手册"]
    protection_level: "低"
    
  confidential:
    description: "机密数据，需要授权访问"
    examples: ["客户信息", "财务数据", "商业计划"]
    protection_level: "中"
    
  restricted:
    description: "受限数据，严格控制访问"
    examples: ["个人身份信息(PII)", "健康信息", "支付卡数据"]
    protection_level: "高"
    
  # 数据标记实现
  data_tagging:
    enabled: true
    method: "元数据标记"
    tags:
      - "PII"
      - "PHI"
      - "PCI"
      - "FINANCIAL"
      - "CONFIDENTIAL"
```

### 2.2 数据处理合规性
```python
# data_compliance.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

class DataComplianceChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_rules = self._load_compliance_rules()
        
    def check_data_processing_compliance(self, data_info: Dict) -> Dict:
        """检查数据处理合规性"""
        compliance_report = {
            'timestamp': datetime.now().isoformat(),
            'data_id': data_info.get('id'),
            'checks': {},
            'violations': [],
            'recommendations': []
        }
        
        # 检查数据分类合规性
        compliance_report['checks']['data_classification'] = self._check_data_classification(data_info)
        
        # 检查数据处理目的合规性
        compliance_report['checks']['processing_purpose'] = self._check_processing_purpose(data_info)
        
        # 检查数据保留合规性
        compliance_report['checks']['data_retention'] = self._check_data_retention(data_info)
        
        # 检查数据传输合规性
        compliance_report['checks']['data_transfer'] = self._check_data_transfer(data_info)
        
        # 检查数据访问合规性
        compliance_report['checks']['data_access'] = self._check_data_access(data_info)
        
        # 汇总违规项
        for check_name, check_result in compliance_report['checks'].items():
            if not check_result['compliant']:
                compliance_report['violations'].extend(check_result['violations'])
                compliance_report['recommendations'].extend(check_result['recommendations'])
                
        compliance_report['overall_compliant'] = len(compliance_report['violations']) == 0
        
        return compliance_report
        
    def _check_data_classification(self, data_info: Dict) -> Dict:
        """检查数据分类合规性"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        data_tags = data_info.get('tags', [])
        processing_purpose = data_info.get('purpose')
        
        # 检查PII数据处理
        if 'PII' in data_tags:
            if not processing_purpose or 'consent' not in processing_purpose:
                result['compliant'] = False
                result['violations'].append("PII数据处理缺少用户同意")
                result['recommendations'].append("获取用户明确同意后再处理PII数据")
                
        # 检查敏感数据加密
        if any(tag in data_tags for tag in ['PII', 'PHI', 'FINANCIAL']):
            if not data_info.get('encrypted', False):
                result['compliant'] = False
                result['violations'].append("敏感数据未加密")
                result['recommendations'].append("对敏感数据实施加密存储和传输")
                
        return result
        
    def _check_processing_purpose(self, data_info: Dict) -> Dict:
        """检查数据处理目的合规性"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        purpose = data_info.get('purpose', '')
        allowed_purposes = [
            'consent', 'contract', 'legal_obligation', 
            'vital_interests', 'public_task', 'legitimate_interests'
        ]
        
        if purpose not in allowed_purposes:
            result['compliant'] = False
            result['violations'].append(f"数据处理目的 '{purpose}' 不符合合规要求")
            result['recommendations'].append("使用合法的处理目的，如用户同意、合同履行等")
            
        return result
        
    def _check_data_retention(self, data_info: Dict) -> Dict:
        """检查数据保留合规性"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        created_date = data_info.get('created_date')
        retention_period = data_info.get('retention_period')
        data_tags = data_info.get('tags', [])
        
        if created_date and retention_period:
            created = datetime.fromisoformat(created_date)
            retention_days = self._parse_retention_period(retention_period)
            expiry_date = created + timedelta(days=retention_days)
            
            # 检查是否超过保留期限
            if datetime.now() > expiry_date:
                result['compliant'] = False
                result['violations'].append("数据已超过保留期限")
                result['recommendations'].append("立即删除过期数据")
                
            # 检查敏感数据保留期限
            if 'PII' in data_tags and retention_days > 365:
                result['compliant'] = False
                result['violations'].append("PII数据保留期限过长")
                result['recommendations'].append("将PII数据保留期限限制在1年以内")
                
        return result
        
    def _check_data_transfer(self, data_info: Dict) -> Dict:
        """检查数据传输合规性"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        transfer_info = data_info.get('transfer', {})
        destination = transfer_info.get('destination')
        encryption = transfer_info.get('encryption', False)
        data_tags = data_info.get('tags', [])
        
        # 检查跨境数据传输
        if destination and self._is_cross_border_transfer(destination):
            if 'PII' in data_tags and not transfer_info.get('adequacy_decision', False):
                result['compliant'] = False
                result['violations'].append("跨境PII数据传输缺少充分性认定")
                result['recommendations'].append("获取跨境数据传输的充分性认定或实施适当保障措施")
                
        # 检查传输加密
        if any(tag in data_tags for tag in ['PII', 'PHI', 'FINANCIAL']):
            if not encryption:
                result['compliant'] = False
                result['violations'].append("敏感数据传输未加密")
                result['recommendations'].append("对敏感数据传输实施端到端加密")
                
        return result
        
    def _check_data_access(self, data_info: Dict) -> Dict:
        """检查数据访问合规性"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        access_controls = data_info.get('access_controls', {})
        data_tags = data_info.get('tags', [])
        access_log = data_info.get('access_log', [])
        
        # 检查访问控制
        if 'PII' in data_tags:
            if not access_controls.get('role_based_access', False):
                result['compliant'] = False
                result['violations'].append("PII数据缺少基于角色的访问控制")
                result['recommendations'].append("实施基于角色的访问控制(RBAC)")
                
        # 检查访问日志
        if any(tag in data_tags for tag in ['PII', 'PHI', 'FINANCIAL']):
            if not access_log:
                result['compliant'] = False
                result['violations'].append("敏感数据访问缺少日志记录")
                result['recommendations'].append("启用详细的访问日志记录")
                
        return result
        
    def _load_compliance_rules(self) -> Dict:
        """加载合规性规则"""
        # 从配置文件加载合规性规则
        return {
            'gdpr': {
                'data_retention': 365,  # PII数据保留期限(天)
                'consent_required': True,
                'right_to_erasure': True
            },
            'sox': {
                'audit_trail': True,
                'data_integrity': True
            }
        }
        
    def _parse_retention_period(self, period: str) -> int:
        """解析保留期限"""
        if period.endswith('d'):
            return int(period[:-1])
        elif period.endswith('m'):
            return int(period[:-1]) * 30
        elif period.endswith('y'):
            return int(period[:-1]) * 365
        else:
            return int(period)
            
    def _is_cross_border_transfer(self, destination: str) -> bool:
        """检查是否为跨境传输"""
        # 简化实现，实际应根据地理位置判断
        cross_border_destinations = ['EU', 'US', 'CN', 'JP']
        return destination in cross_border_destinations

# 使用示例
def check_airflow_data_compliance():
    """检查Airflow数据合规性"""
    checker = DataComplianceChecker()
    
    # 示例数据信息
    data_info = {
        'id': 'dag_run_12345',
        'tags': ['PII', 'CONFIDENTIAL'],
        'purpose': 'consent',
        'created_date': '2023-01-01T00:00:00',
        'retention_period': '365d',
        'encrypted': True,
        'transfer': {
            'destination': 'US',
            'encryption': True,
            'adequacy_decision': False
        },
        'access_controls': {
            'role_based_access': True
        },
        'access_log': [
            {'user': 'admin', 'timestamp': '2023-01-01T10:00:00', 'action': 'read'},
            {'user': 'analyst', 'timestamp': '2023-01-01T11:00:00', 'action': 'read'}
        ]
    }
    
    # 执行合规性检查
    report = checker.check_data_processing_compliance(data_info)
    
    # 输出检查结果
    print(f"合规性检查报告:")
    print(f"  总体合规: {report['overall_compliant']}")
    print(f"  违规项数: {len(report['violations'])}")
    
    if report['violations']:
        print("  违规详情:")
        for violation in report['violations']:
            print(f"    - {violation}")
            
    if report['recommendations']:
        print("  建议措施:")
        for recommendation in report['recommendations']:
            print(f"    - {recommendation}")
            
    return report
```

## 3. 安全控制合规性

### 3.1 身份认证和访问控制
```yaml
# 身份认证和访问控制配置
authentication_access_control:
  # 身份提供者
  identity_provider:
    type: "LDAP"
    server: "ldap://ldap.company.com"
    base_dn: "dc=company,dc=com"
    bind_dn: "cn=admin,dc=company,dc=com"
    
  # 多因素认证
  mfa:
    enabled: true
    methods:
      - "totp"  # 基于时间的一次性密码
      - "sms"   # 短信验证码
      - "email" # 邮件验证码
      
  # 角色基础访问控制(RBAC)
  rbac:
    enabled: true
    roles:
      # 管理员角色
      admin:
        permissions:
          - "can_read"
          - "can_edit"
          - "can_delete"
          - "can_manage_users"
          - "can_manage_roles"
        description: "系统管理员，拥有所有权限"
        
      # 开发者角色
      developer:
        permissions:
          - "can_read"
          - "can_edit"
        description: "DAG开发者，可以创建和编辑工作流"
        
      # 操作员角色
      operator:
        permissions:
          - "can_read"
          - "can_trigger"
        description: "操作员，可以触发和监控工作流"
        
      # 审计员角色
      auditor:
        permissions:
          - "can_read"
        description: "审计员，只能查看和审计系统"
        
  # 访问日志
  access_logging:
    enabled: true
    log_level: "info"
    retention_days: 365
```

### 3.2 数据加密
```bash
#!/bin/bash
# encryption_compliance.sh

# 数据加密合规性检查脚本

# 检查配置
LOG_FILE="/var/log/airflow/encryption_compliance.log"
AIRFLOW_CONFIG="/opt/airflow/airflow.cfg"

# 检查静态数据加密
check_data_at_rest_encryption() {
    echo "$(date): Checking data at rest encryption..." >> $LOG_FILE
    
    # 检查数据库加密
    db_encryption=$(grep -c "sql_alchemy_conn.*sslmode=require" $AIRFLOW_CONFIG)
    if [ $db_encryption -eq 0 ]; then
        echo "$(date): WARNING - Database connection not using SSL" >> $LOG_FILE
    else
        echo "$(date): Database connection uses SSL" >> $LOG_FILE
    fi
    
    # 检查文件系统加密
    fs_encrypted=$(mount | grep /opt/airflow | grep -c encrypt)
    if [ $fs_encrypted -eq 0 ]; then
        echo "$(date): WARNING - File system not encrypted" >> $LOG_FILE
    else
        echo "$(date): File system is encrypted" >> $LOG_FILE
    fi
    
    # 检查密钥管理
    key_management=$(grep -c "fernet_key" $AIRFLOW_CONFIG)
    if [ $key_management -eq 0 ]; then
        echo "$(date): CRITICAL - Fernet key not configured" >> $LOG_FILE
    else
        echo "$(date): Fernet key is configured" >> $LOG_FILE
    fi
}

# 检查传输中数据加密
check_data_in_transit_encryption() {
    echo "$(date): Checking data in transit encryption..." >> $LOG_FILE
    
    # 检查Web服务器HTTPS
    https_enabled=$(grep -c "web_server_ssl_cert" $AIRFLOW_CONFIG)
    if [ $https_enabled -eq 0 ]; then
        echo "$(date): WARNING - HTTPS not enabled for web server" >> $LOG_FILE
    else
        echo "$(date): HTTPS is enabled for web server" >> $LOG_FILE
    fi
    
    # 检查API HTTPS
    api_https=$(grep -c "api_ssl_cert" $AIRFLOW_CONFIG)
    if [ $api_https -eq 0 ]; then
        echo "$(date): WARNING - HTTPS not enabled for API" >> $LOG_FILE
    else
        echo "$(date): HTTPS is enabled for API" >> $LOG_FILE
    fi
    
    # 检查内部通信加密
    internal_encryption=$(grep -c "celery_ssl_active.*True" $AIRFLOW_CONFIG)
    if [ $internal_encryption -eq 0 ]; then
        echo "$(date): WARNING - Internal communication not encrypted" >> $LOG_FILE
    else
        echo "$(date): Internal communication is encrypted" >> $LOG_FILE
    fi
}

# 检查密钥轮换
check_key_rotation() {
    echo "$(date): Checking key rotation..." >> $LOG_FILE
    
    # 检查密钥轮换策略
    key_rotation_config=$(grep "fernet_key" $AIRFLOW_CONFIG | wc -l)
    if [ $key_rotation_config -gt 1 ]; then
        echo "$(date): Multiple Fernet keys configured (key rotation enabled)" >> $LOG_FILE
    else
        echo "$(date): WARNING - Key rotation not configured" >> $LOG_FILE
    fi
    
    # 检查密钥存储安全
    key_storage_secure=$(ls -l $AIRFLOW_CONFIG | grep -c "\-rw-------")
    if [ $key_storage_secure -eq 0 ]; then
        echo "$(date): WARNING - Configuration file permissions not secure" >> $LOG_FILE
    else
        echo "$(date): Configuration file permissions are secure" >> $LOG_FILE
    fi
}

# 主检查函数
main() {
    echo "$(date): Starting encryption compliance check" >> $LOG_FILE
    
    check_data_at_rest_encryption
    check_data_in_transit_encryption
    check_key_rotation
    
    echo "$(date): Encryption compliance check completed" >> $LOG_FILE
}

# 执行检查
main
```

## 4. 审计和监控合规性

### 4.1 审计日志要求
```python
# audit_compliance.py
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

class AuditComplianceChecker:
    def __init__(self, log_directory: str = "/var/log/airflow"):
        self.log_directory = log_directory
        self.logger = logging.getLogger(__name__)
        self.audit_requirements = self._load_audit_requirements()
        
    def check_audit_compliance(self) -> Dict:
        """检查审计合规性"""
        compliance_report = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'violations': [],
            'recommendations': []
        }
        
        # 检查审计日志配置
        compliance_report['checks']['audit_logging'] = self._check_audit_logging()
        
        # 检查日志保留策略
        compliance_report['checks']['log_retention'] = self._check_log_retention()
        
        # 检查日志完整性
        compliance_report['checks']['log_integrity'] = self._check_log_integrity()
        
        # 检查审计跟踪
        compliance_report['checks']['audit_trail'] = self._check_audit_trail()
        
        # 汇总违规项
        for check_name, check_result in compliance_report['checks'].items():
            if not check_result['compliant']:
                compliance_report['violations'].extend(check_result['violations'])
                compliance_report['recommendations'].extend(check_result['recommendations'])
                
        compliance_report['overall_compliant'] = len(compliance_report['violations']) == 0
        
        return compliance_report
        
    def _check_audit_logging(self) -> Dict:
        """检查审计日志配置"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        # 检查是否启用了审计日志
        audit_enabled = self._is_audit_logging_enabled()
        if not audit_enabled:
            result['compliant'] = False
            result['violations'].append("审计日志未启用")
            result['recommendations'].append("在Airflow配置中启用审计日志")
            
        # 检查日志级别
        log_level = self._get_log_level()
        if log_level not in ['INFO', 'DEBUG']:
            result['compliant'] = False
            result['violations'].append(f"日志级别 {log_level} 不符合审计要求")
            result['recommendations'].append("将日志级别设置为INFO或DEBUG")
            
        # 检查关键事件日志
        critical_events = self._check_critical_events_logging()
        if not critical_events['compliant']:
            result['compliant'] = False
            result['violations'].extend(critical_events['violations'])
            result['recommendations'].extend(critical_events['recommendations'])
            
        return result
        
    def _check_log_retention(self) -> Dict:
        """检查日志保留策略"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        # 根据不同合规框架检查保留期限
        frameworks = {
            'sox': 365,      # SOX要求至少1年
            'gdpr': 730,     # GDPR建议至少2年
            'iso_27001': 365 # ISO 27001要求至少1年
        }
        
        current_retention = self._get_current_retention_period()
        
        for framework, required_days in frameworks.items():
            if current_retention < required_days:
                result['compliant'] = False
                result['violations'].append(f"{framework}要求日志保留{required_days}天，当前为{current_retention}天")
                result['recommendations'].append(f"将日志保留期限更新为至少{required_days}天以满足{framework}要求")
                
        return result
        
    def _check_log_integrity(self) -> Dict:
        """检查日志完整性"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        # 检查日志文件权限
        permission_issues = self._check_log_file_permissions()
        if permission_issues:
            result['compliant'] = False
            result['violations'].extend(permission_issues)
            result['recommendations'].append("修正日志文件权限以防止未授权访问")
            
        # 检查日志签名
        signature_issues = self._check_log_signatures()
        if signature_issues:
            result['compliant'] = False
            result['violations'].extend(signature_issues)
            result['recommendations'].append("实施日志签名机制以确保完整性")
            
        return result
        
    def _check_audit_trail(self) -> Dict:
        """检查审计跟踪"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        # 检查关键操作跟踪
        critical_operations = [
            'user_login', 'user_logout', 'dag_create', 
            'dag_update', 'dag_delete', 'task_execution',
            'config_change', 'permission_change'
        ]
        
        missing_operations = self._find_missing_audit_trail(critical_operations)
        if missing_operations:
            result['compliant'] = False
            for operation in missing_operations:
                result['violations'].append(f"缺少关键操作的审计跟踪: {operation}")
                result['recommendations'].append(f"为{operation}操作启用审计跟踪")
                
        return result
        
    def _is_audit_logging_enabled(self) -> bool:
        """检查是否启用了审计日志"""
        # 检查Airflow配置
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('/opt/airflow/airflow.cfg')
            
            # 检查日志配置
            if config.has_section('logging'):
                logging_level = config.get('logging', 'logging_level', fallback='INFO')
                return logging_level in ['INFO', 'DEBUG']
            return False
        except Exception:
            return False
            
    def _get_log_level(self) -> str:
        """获取当前日志级别"""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('/opt/airflow/airflow.cfg')
            
            if config.has_section('logging'):
                return config.get('logging', 'logging_level', fallback='WARNING')
            return 'WARNING'
        except Exception:
            return 'UNKNOWN'
            
    def _get_current_retention_period(self) -> int:
        """获取当前日志保留期限"""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('/opt/airflow/airflow.cfg')
            
            if config.has_section('logging'):
                retention_days = config.getint('logging', 'log_retention_days', fallback=30)
                return retention_days
            return 30
        except Exception:
            return 30
            
    def _check_critical_events_logging(self) -> Dict:
        """检查关键事件日志"""
        result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        # 检查关键事件是否被记录
        critical_events = [
            '用户登录/登出',
            'DAG创建/更新/删除',
            '任务执行',
            '配置变更',
            '权限变更'
        ]
        
        # 这里应该检查实际的日志内容
        # 简化实现，假设都已记录
        return result
        
    def _check_log_file_permissions(self) -> List[str]:
        """检查日志文件权限"""
        import os
        issues = []
        
        try:
            # 检查日志目录权限
            log_dir_stat = os.stat(self.log_directory)
            if log_dir_stat.st_mode & 0o777 != 0o755:
                issues.append("日志目录权限不正确")
                
            # 检查日志文件权限
            for log_file in os.listdir(self.log_directory):
                if log_file.endswith('.log'):
                    file_path = os.path.join(self.log_directory, log_file)
                    file_stat = os.stat(file_path)
                    if file_stat.st_mode & 0o777 != 0o644:
                        issues.append(f"日志文件 {log_file} 权限不正确")
                        
        except Exception as e:
            issues.append(f"检查日志文件权限时出错: {str(e)}")
            
        return issues
        
    def _check_log_signatures(self) -> List[str]:
        """检查日志签名"""
        # 简化实现，实际应该检查日志签名机制
        return []  # 假设没有问题
        
    def _find_missing_audit_trail(self, critical_operations: List[str]) -> List[str]:
        """查找缺失的审计跟踪"""
        # 简化实现，实际应该检查审计日志
        return []  # 假设没有缺失
        
    def _load_audit_requirements(self) -> Dict:
        """加载审计要求"""
        return {
            'sox': {
                'log_retention_days': 365,
                'required_events': [
                    'user_authentication',
                    'configuration_changes',
                    'data_access'
                ]
            },
            'gdpr': {
                'log_retention_days': 730,
                'required_events': [
                    'data_processing',
                    'data_access',
                    'data_deletion'
                ]
            }
        }

# 使用示例
def run_audit_compliance_check():
    """运行审计合规性检查"""
    checker = AuditComplianceChecker()
    
    # 执行检查
    report = checker.check_audit_compliance()
    
    # 输出结果
    print("审计合规性检查报告:")
    print(f"  检查时间: {report['timestamp']}")
    print(f"  总体合规: {report['overall_compliant']}")
    print(f"  违规项数: {len(report['violations'])}")
    
    if report['violations']:
        print("  违规详情:")
        for violation in report['violations']:
            print(f"    - {violation}")
            
    if report['recommendations']:
        print("  建议措施:")
        for recommendation in report['recommendations']:
            print(f"    - {recommendation}")
            
    return report
```

### 4.2 监控和报告
```yaml
# monitoring_compliance.yaml
monitoring_compliance:
  # 监控指标
  metrics:
    # 安全指标
    security_metrics:
      - name: "failed_login_attempts"
        description: "失败的登录尝试次数"
        threshold: 5
        time_window: "1h"
        
      - name: "unauthorized_access_attempts"
        description: "未授权访问尝试次数"
        threshold: 1
        time_window: "1h"
        
      - name: "data_access_violations"
        description: "数据访问违规次数"
        threshold: 0
        time_window: "1h"
        
    # 合规性指标
    compliance_metrics:
      - name: "audit_log_completeness"
        description: "审计日志完整性"
        threshold: 99.9
        unit: "percentage"
        
      - name: "data_encryption_rate"
        description: "数据加密率"
        threshold: 100
        unit: "percentage"
        
      - name: "access_control_violations"
        description: "访问控制违规次数"
        threshold: 0
        time_window: "1h"
        
  # 告警配置
  alerts:
    # 安全告警
    security_alerts:
      - name: "security_breach_detected"
        condition: "failed_login_attempts > 5"
        severity: "critical"
        notification_channels: ["email", "sms", "slack"]
        
      - name: "unauthorized_data_access"
        condition: "unauthorized_access_attempts > 0"
        severity: "high"
        notification_channels: ["email", "slack"]
        
    # 合规性告警
    compliance_alerts:
      - name: "compliance_violation_detected"
        condition: "access_control_violations > 0"
        severity: "high"
        notification_channels: ["email", "compliance_team"]
        
      - name: "audit_log_incomplete"
        condition: "audit_log_completeness < 99.9"
        severity: "medium"
        notification_channels: ["email"]
        
  # 报告要求
  reporting:
    # 日报
    daily_reports:
      enabled: true
      recipients: ["security-team@company.com", "compliance-team@company.com"]
      content:
        - "安全事件摘要"
        - "合规性指标状态"
        - "审计日志统计"
        
    # 周报
    weekly_reports:
      enabled: true
      recipients: ["management@company.com", "compliance-officer@company.com"]
      content:
        - "一周安全态势"
        - "合规性趋势分析"
        - "风险评估报告"
        
    # 月报
    monthly_reports:
      enabled: true
      recipients: ["executives@company.com", "audit-committee@company.com"]
      content:
        - "月度合规性总结"
        - "安全控制有效性评估"
        - "改进措施建议"
```

## 5. 隐私保护合规性

### 5.1 数据主体权利
```python
# privacy_compliance.py
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

class PrivacyComplianceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.privacy_requests_file = "/opt/airflow/data/privacy_requests.json"
        self.user_data_directory = "/opt/airflow/data/user_data"
        
    def handle_data_subject_request(self, request: Dict) -> Dict:
        """处理数据主体请求"""
        response = {
            'request_id': request.get('request_id'),
            'timestamp': datetime.now().isoformat(),
            'request_type': request.get('request_type'),
            'status': 'processing',
            'actions_taken': [],
            'errors': []
        }
        
        try:
            request_type = request.get('request_type')
            
            if request_type == 'right_to_access':
                response.update(self._handle_right_to_access(request))
            elif request_type == 'right_to_rectification':
                response.update(self._handle_right_to_rectification(request))
            elif request_type == 'right_to_erasure':
                response.update(self._handle_right_to_erasure(request))
            elif request_type == 'right_to_data_portability':
                response.update(self._handle_right_to_data_portability(request))
            elif request_type == 'right_to_restriction':
                response.update(self._handle_right_to_restriction(request))
            elif request_type == 'right_to_object':
                response.update(self._handle_right_to_object(request))
            else:
                response['status'] = 'error'
                response['errors'].append(f"未知的请求类型: {request_type}")
                
        except Exception as e:
            self.logger.error(f"处理数据主体请求时出错: {str(e)}")
            response['status'] = 'error'
            response['errors'].append(str(e))
            
        # 记录请求处理
        self._log_privacy_request(response)
        
        return response
        
    def _handle_right_to_access(self, request: Dict) -> Dict:
        """处理访问权请求"""
        result = {
            'status': 'completed',
            'actions_taken': ['已确认用户身份', '已收集用户数据'],
            'data_summary': {}
        }
        
        user_id = request.get('user_id')
        if not user_id:
            result['status'] = 'error'
            result['errors'] = ['缺少用户ID']
            return result
            
        # 收集用户数据
        user_data = self._collect_user_data(user_id)
        result['data_summary'] = user_data
        
        # 生成数据报告
        report_path = self._generate_data_report(user_id, user_data)
        result['actions_taken'].append(f'数据报告已生成: {report_path}')
        
        return result
        
    def _handle_right_to_rectification(self, request: Dict) -> Dict:
        """处理更正权请求"""
        result = {
            'status': 'completed',
            'actions_taken': ['已确认用户身份', '已验证更正请求'],
            'rectifications': []
        }
        
        user_id = request.get('user_id')
        corrections = request.get('corrections', [])
        
        if not user_id:
            result['status'] = 'error'
            result['errors'] = ['缺少用户ID']
            return result
            
        # 应用更正
        for correction in corrections:
            field = correction.get('field')
            old_value = correction.get('old_value')
            new_value = correction.get('new_value')
            
            if self._apply_data_correction(user_id, field, old_value, new_value):
                result['rectifications'].append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value,
                    'status': 'completed'
                })
                result['actions_taken'].append(f'已更正字段: {field}')
            else:
                result['rectifications'].append({
                    'field': field,
                    'old_value': old_value,
                    'new_value': new_value,
                    'status': 'failed'
                })
                result['actions_taken'].append(f'更正字段失败: {field}')
                
        return result
        
    def _handle_right_to_erasure(self, request: Dict) -> Dict:
        """处理删除权请求"""
        result = {
            'status': 'completed',
            'actions_taken': ['已确认用户身份', '已验证删除请求'],
            'deletions': []
        }
        
        user_id = request.get('user_id')
        if not user_id:
            result['status'] = 'error'
            result['errors'] = ['缺少用户ID']
            return result
            
        # 删除用户数据
        deleted_data = self._delete_user_data(user_id)
        result['deletions'] = deleted_data
        result['actions_taken'].append(f'已删除 {len(deleted_data)} 项用户数据')
        
        # 记录删除操作
        self._log_data_deletion(user_id, deleted_data)
        
        return result
        
    def _handle_right_to_data_portability(self, request: Dict) -> Dict:
        """处理数据可携权请求"""
        result = {
            'status': 'completed',
            'actions_taken': ['已确认用户身份', '已收集可携数据'],
            'portable_data': {}
        }
        
        user_id = request.get('user_id')
        if not user_id:
            result['status'] = 'error'
            result['errors'] = ['缺少用户ID']
            return result
            
        # 收集可携数据
        portable_data = self._collect_portable_data(user_id)
        result['portable_data'] = portable_data
        
        # 生成可携数据文件
        file_path = self._generate_portable_data_file(user_id, portable_data)
        result['actions_taken'].append(f'可携数据文件已生成: {file_path}')
        
        return result
        
    def _handle_right_to_restriction(self, request: Dict) -> Dict:
        """处理限制处理权请求"""
        result = {
            'status': 'completed',
            'actions_taken': ['已确认用户身份', '已实施处理限制'],
            'restrictions': []
        }
        
        user_id = request.get('user_id')
        if not user_id:
            result['status'] = 'error'
            result['errors'] = ['缺少用户ID']
            return result
            
        # 实施处理限制
        restriction_result = self._implement_processing_restriction(user_id)
        result['restrictions'] = restriction_result
        result['actions_taken'].append('已实施数据处理限制')
        
        return result
        
    def _handle_right_to_object(self, request: Dict) -> Dict:
        """处理反对权请求"""
        result = {
            'status': 'completed',
            'actions_taken': ['已确认用户身份', '已处理反对请求'],
            'objections': []
        }
        
        user_id = request.get('user_id')
        objection_type = request.get('objection_type')
        
        if not user_id:
            result['status'] = 'error'
            result['errors'] = ['缺少用户ID']
            return result
            
        # 处理反对请求
        objection_result = self._process_objection(user_id, objection_type)
        result['objections'] = objection_result
        result['actions_taken'].append(f'已处理 {objection_type} 反对请求')
        
        return result
        
    def _collect_user_data(self, user_id: str) -> Dict:
        """收集用户数据"""
        # 简化实现，实际应从数据库和日志中收集
        return {
            'personal_info': {
                'name': 'John Doe',
                'email': 'john.doe@example.com'
            },
            'processing_activities': [
                {
                    'activity': 'DAG execution',
                    'timestamp': '2023-01-01T10:00:00',
                    'purpose': 'Data processing'
                }
            ],
            'data_sources': ['user_input', 'system_generated']
        }
        
    def _generate_data_report(self, user_id: str, user_data: Dict) -> str:
        """生成数据报告"""
        report_path = f"/opt/airflow/reports/{user_id}_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'data_summary': user_data
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        return report_path
        
    def _apply_data_correction(self, user_id: str, field: str, old_value: str, new_value: str) -> bool:
        """应用数据更正"""
        # 简化实现，实际应更新数据库
        try:
            # 这里应该实现实际的数据更正逻辑
            self.logger.info(f"Applied correction for user {user_id}: {field} from {old_value} to {new_value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply correction: {str(e)}")
            return False
            
    def _delete_user_data(self, user_id: str) -> List[Dict]:
        """删除用户数据"""
        # 简化实现，实际应删除数据库记录和文件
        deleted_items = [
            {'type': 'user_profile', 'status': 'deleted'},
            {'type': 'processing_logs', 'status': 'deleted'},
            {'type': 'audit_records', 'status': 'retained_for_compliance'}
        ]
        
        return deleted_items
        
    def _log_data_deletion(self, user_id: str, deleted_data: List[Dict]):
        """记录数据删除操作"""
        deletion_log = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'deleted_data': deleted_data
        }
        
        # 写入删除日志
        with open("/opt/airflow/logs/data_deletion.log", 'a') as f:
            f.write(json.dumps(deletion_log) + '\n')
            
    def _collect_portable_data(self, user_id: str) -> Dict:
        """收集可携数据"""
        # 简化实现，实际应收集结构化数据
        return {
            'user_profile': {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'created_at': '2023-01-01T00:00:00'
            },
            'processing_history': [
                {
                    'task': 'data_processing_job',
                    'started_at': '2023-01-01T10:00:00',
                    'completed_at': '2023-01-01T10:05:00',
                    'status': 'success'
                }
            ]
        }
        
    def _generate_portable_data_file(self, user_id: str, portable_data: Dict) -> str:
        """生成可携数据文件"""
        file_path = f"/opt/airflow/portable_data/{user_id}_portable_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(file_path, 'w') as f:
            json.dump(portable_data, f, indent=2)
            
        return file_path
        
    def _implement_processing_restriction(self, user_id: str) -> List[Dict]:
        """实施处理限制"""
        # 简化实现，实际应更新访问控制
        restrictions = [
            {'type': 'processing_suspension', 'status': 'applied'},
            {'type': 'data_access_limitation', 'status': 'applied'}
        ]
        
        return restrictions
        
    def _process_objection(self, user_id: str, objection_type: str) -> List[Dict]:
        """处理反对请求"""
        # 简化实现，实际应根据反对类型采取措施
        objections = [
            {'type': objection_type, 'status': 'processed', 'action_taken': 'restriction_applied'}
        ]
        
        return objections
        
    def _log_privacy_request(self, response: Dict):
        """记录隐私请求"""
        # 读取现有请求记录
        requests = []
        try:
            with open(self.privacy_requests_file, 'r') as f:
                requests = json.load(f)
        except FileNotFoundError:
            pass
        except Exception:
            pass
            
        # 添加新请求
        requests.append(response)
        
        # 保存请求记录
        with open(self.privacy_requests_file, 'w') as f:
            json.dump(requests, f, indent=2)

# 使用示例
def handle_privacy_request_example():
    """处理隐私请求示例"""
    manager = PrivacyComplianceManager()
    
    # 示例访问权请求
    access_request = {
        'request_id': 'req_001',
        'request_type': 'right_to_access',
        'user_id': 'user_12345'
    }
    
    # 处理请求
    response = manager.handle_data_subject_request(access_request)
    
    # 输出结果
    print("隐私请求处理结果:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    return response
```

## 6. 第三方服务合规性

### 6.1 供应商管理
```yaml
# vendor_compliance.yaml
vendor_compliance:
  # 供应商评估
  vendor_assessment:
    # 评估标准
    evaluation_criteria:
      - name: "数据保护能力"
        weight: 30
        requirements:
          - "实施适当的技术和组织措施"
          - "提供数据处理协议"
          - "具备数据泄露响应能力"
          
      - name: "安全控制"
        weight: 25
        requirements:
          - "通过ISO 27001认证"
          - "实施访问控制"
          - "定期安全评估"
          
      - name: "合规性"
        weight: 20
        requirements:
          - "符合GDPR要求"
          - "符合行业特定法规"
          - "提供合规性证明"
          
      - name: "业务连续性"
        weight: 15
        requirements:
          - "灾难恢复计划"
          - "业务连续性计划"
          - "服务水平协议(SLA)"
          
      - name: "透明度"
        weight: 10
        requirements:
          - "定期报告"
          - "审计权"
          - "变更通知"
          
  # 供应商监控
  vendor_monitoring:
    # 监控频率
    monitoring_frequency:
      critical_vendors: "monthly"    # 关键供应商每月监控
      important_vendors: "quarterly" # 重要供应商每季度监控
      general_vendors: "annually"    # 一般供应商每年监控
      
    # 监控指标
    monitoring_metrics:
      - name: "安全事件数量"
        threshold: 0
        time_window: "1 month"
        
      - name: "服务可用性"
        threshold: 99.9
        unit: "percentage"
        
      - name: "数据泄露事件"
        threshold: 0
        time_window: "1 year"
        
      - name: "合规性审计结果"
        threshold: "pass"
        
  # 合同要求
  contract_requirements:
    # 数据保护条款
    data_protection_clauses:
      - "数据处理限制"
      - "安全措施要求"
      - "数据泄露通知"
      - "数据删除义务"
      - "子处理器管理"
      
    # 审计权条款
    audit_rights:
      - "年度安全审计权"
      - "合规性审计权"
      - "现场检查权"
      - "审计报告提供"
      
    # 终止条款
    termination_clauses:
      - "重大违约终止权"
      - "数据保护违规终止权"
      - "合规性违规终止权"
      - "便利终止权"
```

### 6.2 数据处理协议
```python
# data_processing_agreement.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class DataProcessingAgreementManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dpa_directory = "/opt/airflow/compliance/dpas"
        self.dpa_template = self._load_dpa_template()
        
    def create_data_processing_agreement(self, vendor_info: Dict) -> Dict:
        """创建数据处理协议"""
        dpa = {
            'agreement_id': f"dpa_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'vendor': vendor_info,
            'effective_date': datetime.now().isoformat(),
            'expiry_date': (datetime.now() + timedelta(days=365)).isoformat(),
            'status': 'draft',
            'sections': {}
        }
        
        # 填充协议各部分
        dpa['sections']['parties'] = self._generate_parties_section(vendor_info)
        dpa['sections']['scope'] = self._generate_scope_section(vendor_info)
        dpa['sections']['data_processing'] = self._generate_data_processing_section(vendor_info)
        dpa['sections']['security_measures'] = self._generate_security_measures_section(vendor_info)
        dpa['sections']['subprocessors'] = self._generate_subprocessors_section(vendor_info)
        dpa['sections']['data_subject_rights'] = self._generate_data_subject_rights_section()
        dpa['sections']['data_breach'] = self._generate_data_breach_section()
        dpa['sections']['audit'] = self._generate_audit_section()
        dpa['sections']['liability'] = self._generate_liability_section()
        dpa['sections']['termination'] = self._generate_termination_section()
        
        # 保存协议
        self._save_dpa(dpa)
        
        return dpa
        
    def review_data_processing_agreement(self, agreement_id: str) -> Dict:
        """审查数据处理协议"""
        dpa = self._load_dpa(agreement_id)
        if not dpa:
            return {'error': '协议未找到'}
            
        review_result = {
            'agreement_id': agreement_id,
            'reviewed_at': datetime.now().isoformat(),
            'compliance_status': 'pending',
            'findings': [],
            'recommendations': []
        }
        
        # 检查各部分合规性
        review_result['findings'].extend(self._review_parties_section(dpa['sections']['parties']))
        review_result['findings'].extend(self._review_scope_section(dpa['sections']['scope']))
        review_result['findings'].extend(self._review_data_processing_section(dpa['sections']['data_processing']))
        review_result['findings'].extend(self._review_security_measures_section(dpa['sections']['security_measures']))
        review_result['findings'].extend(self._review_subprocessors_section(dpa['sections']['subprocessors']))
        review_result['findings'].extend(self._review_data_subject_rights_section(dpa['sections']['data_subject_rights']))
        review_result['findings'].extend(self._review_data_breach_section(dpa['sections']['data_breach']))
        review_result['findings'].extend(self._review_audit_section(dpa['sections']['audit']))
        review_result['findings'].extend(self._review_liability_section(dpa['sections']['liability']))
        review_result['findings'].extend(self._review_termination_section(dpa['sections']['termination']))
        
        # 确定总体合规状态
        critical_findings = [f for f in review_result['findings'] if f.get('severity') == 'critical']
        if not critical_findings:
            review_result['compliance_status'] = 'compliant'
        else:
            review_result['compliance_status'] = 'non_compliant'
            review_result['recommendations'] = self._generate_recommendations(critical_findings)
            
        # 记录审查结果
        self._log_dpa_review(review_result)
        
        return review_result
        
    def _generate_parties_section(self, vendor_info: Dict) -> Dict:
        """生成当事方部分"""
        return {
            'data_controller': {
                'name': 'Your Company Name',
                'address': 'Your Company Address',
                'contact': 'privacy@yourcompany.com'
            },
            'data_processor': {
                'name': vendor_info.get('name'),
                'address': vendor_info.get('address'),
                'contact': vendor_info.get('contact')
            }
        }
        
    def _generate_scope_section(self, vendor_info: Dict) -> Dict:
        """生成范围部分"""
        return {
            'purpose': '数据处理服务',
            'duration': '自协议生效之日起一年',
            'data_categories': vendor_info.get('data_categories', []),
            'data_subject_categories': vendor_info.get('data_subject_categories', [])
        }
        
    def _generate_data_processing_section(self, vendor_info: Dict) -> Dict:
        """生成数据处理部分"""
        return {
            'processing_activities': vendor_info.get('processing_activities', []),
            'processing_restrictions': [
                '仅按数据控制方的书面指示处理数据',
                '不得为其他目的处理数据',
                '处理完成后删除或返还数据'
            ],
            'documentation_requirements': [
                '记录所有处理活动',
                '提供处理记录',
                '协助数据保护影响评估'
            ]
        }
        
    def _generate_security_measures_section(self, vendor_info: Dict) -> Dict:
        """生成安全措施部分"""
        return {
            'technical_measures': [
                '加密传输和存储',
                '访问控制',
                '定期安全测试',
                '漏洞管理'
            ],
            'organizational_measures': [
                '员工保密协议',
                '安全培训',
                '事件响应计划',
                '定期风险评估'
            ],
            'certifications': vendor_info.get('security_certifications', [])
        }
        
    def _generate_subprocessors_section(self, vendor_info: Dict) -> Dict:
        """生成子处理者部分"""
        return {
            'subprocessor_requirement': '使用子处理者需事先获得书面同意',
            'subprocessor_list': vendor_info.get('subprocessors', []),
            'subprocessor_obligations': [
                '对子处理者进行尽职调查',
                '确保子处理者遵守相同义务',
                '对子处理者的违规行为承担责任'
            ]
        }
        
    def _generate_data_subject_rights_section(self) -> Dict:
        """生成数据主体权利部分"""
        return {
            'assistance_obligation': '协助数据控制方履行数据主体权利',
            'supported_rights': [
                '访问权',
                '更正权',
                '删除权',
                '限制处理权',
                '数据可携权',
                '反对权'
            ],
            'response_time': '30天内响应数据主体请求'
        }
        
    def _generate_data_breach_section(self) -> Dict:
        """生成数据泄露部分"""
        return {
            'notification_requirement': '发现数据泄露后24小时内通知数据控制方',
            'notification_content': [
                '泄露性质描述',
                '受影响数据类别',
                '受影响数据主体数量',
                '已采取或建议采取的措施'
            ],
            'cooperation_obligation': '配合数据控制方进行泄露调查和补救'
        }
        
    def _generate_audit_section(self) -> Dict:
        """生成审计部分"""
        return {
            'audit_right': '数据控制方有权进行审计',
            'audit_frequency': '每年一次',
            'audit_types': ['文件审查', '现场检查', '技术测试'],
            'audit_cooperation': '数据处理方应配合审计工作'
        }
        
    def _generate_liability_section(self) -> Dict:
        """生成责任部分"""
        return {
            'liability_cap': '年度费用的两倍，最高不超过100万欧元',
            'exclusions': ['间接损失', '利润损失', '商誉损失'],
            'insurance_requirement': '购买足够的责任保险'
        }
        
    def _generate_termination_section(self) -> Dict:
        """生成终止部分"""
        return {
            'termination_reasons': [
                '重大违约',
                '数据保护违规',
                '破产清算',
                '便利终止'
            ],
            'data_handling_on_termination': [
                '删除所有数据',
                '提供删除证明',
                '返还必要数据'
            ]
        }
        
    def _review_parties_section(self, parties_section: Dict) -> List[Dict]:
        """审查当事方部分"""
        findings = []
        
        # 检查必要信息
        if not parties_section.get('data_controller', {}).get('name'):
            findings.append({
                'section': 'parties',
                'issue': '缺少数据控制方名称',
                'severity': 'critical'
            })
            
        if not parties_section.get('data_processor', {}).get('name'):
            findings.append({
                'section': 'parties',
                'issue': '缺少数据处理方名称',
                'severity': 'critical'
            })
            
        return findings
        
    def _review_scope_section(self, scope_section: Dict) -> List[Dict]:
        """审查范围部分"""
        findings = []
        
        # 检查必要信息
        if not scope_section.get('data_categories'):
            findings.append({
                'section': 'scope',
                'issue': '未定义数据类别',
                'severity': 'high'
            })
            
        return findings
        
    def _review_data_processing_section(self, processing_section: Dict) -> List[Dict]:
        """审查数据处理部分"""
        findings = []
        
        # 检查处理活动
        if not processing_section.get('processing_activities'):
            findings.append({
                'section': 'data_processing',
                'issue': '未定义处理活动',
                'severity': 'high'
            })
            
        return findings
        
    def _review_security_measures_section(self, security_section: Dict) -> List[Dict]:
        """审查安全措施部分"""
        findings = []
        
        # 检查技术措施
        if not security_section.get('technical_measures'):
            findings.append({
                'section': 'security_measures',
                'issue': '未定义技术安全措施',
                'severity': 'critical'
            })
            
        return findings
        
    def _review_subprocessors_section(self, subprocessors_section: Dict) -> List[Dict]:
        """审查子处理者部分"""
        findings = []
        
        # 检查子处理者要求
        if not subprocessors_section.get('subprocessor_requirement'):
            findings.append({
                'section': 'subprocessors',
                'issue': '未定义子处理者使用要求',
                'severity': 'high'
            })
            
        return findings
        
    def _review_data_subject_rights_section(self, rights_section: Dict) -> List[Dict]:
        """审查数据主体权利部分"""
        findings = []
        
        # 检查支持的权利
        if not rights_section.get('supported_rights'):
            findings.append({
                'section': 'data_subject_rights',
                'issue': '未定义支持的数据主体权利',
                'severity': 'high'
            })
            
        return findings
        
    def _review_data_breach_section(self, breach_section: Dict) -> List[Dict]:
        """审查数据泄露部分"""
        findings = []
        
        # 检查通知要求
        if not breach_section.get('notification_requirement'):
            findings.append({
                'section': 'data_breach',
                'issue': '未定义数据泄露通知要求',
                'severity': 'critical'
            })
            
        return findings
        
    def _review_audit_section(self, audit_section: Dict) -> List[Dict]:
        """审查审计部分"""
        findings = []
        
        # 检查审计权
        if not audit_section.get('audit_right'):
            findings.append({
                'section': 'audit',
                'issue': '未定义审计权',
                'severity': 'high'
            })
            
        return findings
        
    def _review_liability_section(self, liability_section: Dict) -> List[Dict]:
        """审查责任部分"""
        findings = []
        
        # 检查责任限制
        if not liability_section.get('liability_cap'):
            findings.append({
                'section': 'liability',
                'issue': '未定义责任限制',
                'severity': 'medium'
            })
            
        return findings
        
    def _review_termination_section(self, termination_section: Dict) -> List[Dict]:
        """审查终止部分"""
        findings = []
        
        # 检查终止原因
        if not termination_section.get('termination_reasons'):
            findings.append({
                'section': 'termination',
                'issue': '未定义终止原因',
                'severity': 'high'
            })
            
        return findings
        
    def _generate_recommendations(self, critical_findings: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for finding in critical_findings:
            section = finding.get('section', 'unknown')
            issue = finding.get('issue', 'unknown issue')
            recommendations.append(f"在{section}部分修正问题: {issue}")
            
        return recommendations
        
    def _load_dpa_template(self) -> Dict:
        """加载DPA模板"""
        # 简化实现，实际应从文件加载
        return {
            'version': '1.0',
            'template_sections': [
                'parties', 'scope', 'data_processing', 'security_measures',
                'subprocessors', 'data_subject_rights', 'data_breach',
                'audit', 'liability', 'termination'
            ]
        }
        
    def _save_dpa(self, dpa: Dict):
        """保存DPA"""
        filename = f"{dpa['agreement_id']}.json"
        filepath = f"{self.dpa_directory}/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(dpa, f, indent=2)
            
    def _load_dpa(self, agreement_id: str) -> Optional[Dict]:
        """加载DPA"""
        filename = f"{agreement_id}.json"
        filepath = f"{self.dpa_directory}/{filename}"
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"加载DPA时出错: {str(e)}")
            return None
            
    def _log_dpa_review(self, review_result: Dict):
        """记录DPA审查"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'review_result': review_result
        }
        
        with open(f"{self.dpa_directory}/review_log.json", 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# 使用示例
def create_dpa_example():
    """创建DPA示例"""
    manager = DataProcessingAgreementManager()
    
    # 供应商信息
    vendor_info = {
        'name': 'Cloud Service Provider Inc.',
        'address': '123 Cloud Street, Cloud City',
        'contact': 'legal@cloudprovider.com',
        'data_categories': ['personal_data', 'usage_data'],
        'data_subject_categories': ['customers', 'employees'],
        'processing_activities': ['data_storage', 'data_processing', 'data_analysis'],
        'security_certifications': ['ISO 27001', 'SOC 2']
    }
    
    # 创建DPA
    dpa = manager.create_data_processing_agreement(vendor_info)
    
    # 审查DPA
    review_result = manager.review_data_processing_agreement(dpa['agreement_id'])
    
    # 输出结果
    print("DPA创建和审查结果:")
    print(json.dumps({
        'dpa': dpa['agreement_id'],
        'review_status': review_result['compliance_status'],
        'findings': review_result['findings'],
        'recommendations': review_result['recommendations']
    }, indent=2, ensure_ascii=False))
    
    return dpa, review_result
```

## 7. 合规性监控和报告

### 7.1 合规性仪表板
```python
# compliance_dashboard.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import matplotlib.pyplot as plt
import pandas as pd

class ComplianceDashboard:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_directory = "/opt/airflow/compliance/data"
        self.report_directory = "/opt/airflow/compliance/reports"
        
    def generate_compliance_dashboard(self) -> Dict:
        """生成合规性仪表板"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'overview': {},
            'metrics': {},
            'trends': {},
            'alerts': [],
            'recommendations': []
        }
        
        # 生成概览
        dashboard['overview'] = self._generate_overview()
        
        # 生成指标
        dashboard['metrics'] = self._generate_metrics()
        
        # 生成趋势
        dashboard['trends'] = self._generate_trends()
        
        # 生成警报
        dashboard['alerts'] = self._generate_alerts()
        
        # 生成建议
        dashboard['recommendations'] = self._generate_recommendations(dashboard['alerts'])
        
        # 生成可视化报告
        self._generate_visualization_report(dashboard)
        
        return dashboard
        
    def _generate_overview(self) -> Dict:
        """生成概览"""
        return {
            'total_compliance_frameworks': 5,
            'active_frameworks': 4,
            'compliance_score': 92.5,  # 百分比
            'last_assessment': '2023-12-01',
            'next_assessment': '2024-01-01',
            'critical_issues': 2,
            'high_issues': 5,
            'medium_issues': 12,
            'low_issues': 25
        }
        
    def _generate_metrics(self) -> Dict:
        """生成指标"""
        return {
            'data_protection': {
                'encryption_rate': 98.7,
                'access_control_compliance': 95.2,
                'data_breach_incidents': 0,
                'dpa_compliance': 100
            },
            'privacy_compliance': {
                'data_subject_requests_handled': 23,
                'average_response_time_hours': 18.5,
                'request_satisfaction_rate': 96.3,
                'privacy_training_completion': 94.1
            },
            'security_controls': {
                'vulnerability_scan_compliance': 100,
                'penetration_test_completion': 100,
                'security_incident_response_time_minutes': 15,
                'security_awareness_training_completion': 97.8
            },
            'audit_compliance': {
                'log_completeness': 99.8,
                'audit_trail_integrity': 100,
                'regulatory_report_submission': 100,
                'internal_audit_findings': 3
            }
        }
        
    def _generate_trends(self) -> Dict:
        """生成趋势"""
        # 简化实现，实际应从历史数据生成
        return {
            'compliance_score_trend': [89.5, 90.2, 91.8, 92.5],
            'security_incidents_trend': [5, 3, 2, 0],
            'data_breach_trend': [1, 0, 0, 0],
            'audit_findings_trend': [8, 6, 4, 3]
        }
        
    def _generate_alerts(self) -> List[Dict]:
        """生成警报"""
        alerts = []
        
        # 检查关键指标
        metrics = self._generate_metrics()
        
        # 数据保护警报
        if metrics['data_protection']['encryption_rate'] < 95:
            alerts.append({
                'type': 'data_protection',
                'severity': 'high',
                'message': '加密率低于95%',
                'timestamp': datetime.now().isoformat()
            })
            
        # 隐私合规警报
        if metrics['privacy_compliance']['average_response_time_hours'] > 24:
            alerts.append({
                'type': 'privacy_compliance',
                'severity': 'medium',
                'message': '数据主体请求响应时间超过24小时',
                'timestamp': datetime.now().isoformat()
            })
            
        # 安全控制警报
        if metrics['security_controls']['security_incident_response_time_minutes'] > 30:
            alerts.append({
                'type': 'security_controls',
                'severity': 'high',
                'message': '安全事件响应时间超过30分钟',
                'timestamp': datetime.now().isoformat()
            })
            
        return alerts
        
    def _generate_recommendations(self, alerts: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for alert in alerts:
            if alert['type'] == 'data_protection' and alert['severity'] == 'high':
                recommendations.append('加强数据加密措施，确保所有敏感数据都得到适当加密')
            elif alert['type'] == 'privacy_compliance' and alert['severity'] == 'medium':
                recommendations.append('优化数据主体请求处理流程，缩短响应时间')
            elif alert['type'] == 'security_controls' and alert['severity'] == 'high':
                recommendations.append('改进安全事件响应流程，缩短响应时间')
                
        # 通用建议
        recommendations.extend([
            '定期进行合规性评估和审计',
            '加强员工合规性培训',
            '更新和维护数据处理协议',
            '实施持续监控和告警机制'
        ])
        
        return recommendations
        
    def _generate_visualization_report(self, dashboard: Dict):
        """生成可视化报告"""
        try:
            # 创建合规性分数趋势图
            plt.figure(figsize=(12, 8))
            
            # 子图1: 合规性分数趋势
            plt.subplot(2, 2, 1)
            trend_data = dashboard['trends']['compliance_score_trend']
            plt.plot(trend_data, marker='o')
            plt.title('合规性分数趋势')
            plt.ylabel('分数 (%)')
            plt.grid(True)
            
            # 子图2: 安全事件趋势
            plt.subplot(2, 2, 2)
            incident_trend = dashboard['trends']['security_incidents_trend']
            plt.plot(incident_trend, marker='s', color='red')
            plt.title('安全事件趋势')
            plt.ylabel('事件数量')
            plt.grid(True)
            
            # 子图3: 合规性指标雷达图
            plt.subplot(2, 2, 3, projection='polar')
            metrics = dashboard['metrics']
            categories = ['数据保护', '隐私合规', '安全控制', '审计合规']
            values = [
                metrics['data_protection']['encryption_rate'] / 100,
                metrics['privacy_compliance']['request_satisfaction_rate'] / 100,
                metrics['security_controls']['security_awareness_training_completion'] / 100,
                metrics['audit_compliance']['log_completeness'] / 100
            ]
            
            # 闭合雷达图
            values += values[:1]
            categories += categories[:1]
            
            # 计算角度
            angles = [n / float(len(categories) - 1) * 2 * 3.14159 for n in range(len(categories) - 1)]
            angles += angles[:1]
            
            plt.plot(angles, values, 'o-', linewidth=2)
            plt.fill(angles, values, alpha=0.25)
            plt.title('合规性指标雷达图')
            plt.xticks(angles[:-1], categories[:-1])
            
            # 子图4: 问题严重性分布
            plt.subplot(2, 2, 4)
            overview = dashboard['overview']
            severity_counts = [
                overview['critical_issues'],
                overview['high_issues'],
                overview['medium_issues'],
                overview['low_issues']
            ]
            severity_labels = ['严重', '高', '中', '低']
            colors = ['red', 'orange', 'yellow', 'green']
            
            plt.bar(severity_labels, severity_counts, color=colors)
            plt.title('问题严重性分布')
            plt.ylabel('问题数量')
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            report_path = f"{self.report_directory}/compliance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(report_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"合规性仪表板报告已生成