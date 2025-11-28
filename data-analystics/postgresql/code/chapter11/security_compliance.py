#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL第11章：安全与合规管理
================================

本模块实现PostgreSQL数据库的安全合规管理功能，包括：
- GDPR、SOX等法规合规检查
- 数据分类和标记管理
- 合规报告生成
- 风险评估和管理
- 合规监控和告警
"""

import os
import sys
import json
import hashlib
import logging
import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_compliance.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    """合规状态枚举"""
    COMPLIANT = "合规"
    NON_COMPLIANT = "不合规"
    PARTIAL_COMPLIANT = "部分合规"
    NEEDS_REVIEW = "需要审查"
    NOT_APPLICABLE = "不适用"

class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    CRITICAL = "严重风险"

@dataclass
class ComplianceCheck:
    """合规检查项"""
    check_id: str
    regulation: str  # 法规名称 (GDPR, SOX, HIPAA等)
    requirement: str  # 具体要求
    current_status: ComplianceStatus
    risk_level: RiskLevel
    description: str
    remediation_steps: List[str]
    last_checked: datetime.datetime
    responsible_party: str

@dataclass
class DataClassification:
    """数据分类"""
    table_name: str
    column_name: str
    data_type: str
    classification_level: str  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    contains_pii: bool  # 包含个人识别信息
    contains_phi: bool  # 包含受保护健康信息
    contains_financial: bool  # 包含财务信息
    encryption_required: bool
    retention_period: int  # 保留天数

class SecurityComplianceManager:
    """安全合规管理器"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        初始化安全合规管理器
        
        Args:
            db_config: 数据库配置字典
        """
        self.db_config = db_config
        self.compliance_checks: List[ComplianceCheck] = []
        self.data_classifications: List[DataClassification] = []
        self.audit_log = []
        
    def connect_database(self):
        """连接数据库"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def discover_data_classifications(self) -> List[DataClassification]:
        """
        自动发现数据分类
        
        Returns:
            数据分类列表
        """
        logger.info("开始数据分类发现...")
        
        try:
            with self.connect_database() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 查询所有表和列信息
                    query = """
                    SELECT 
                        schemaname,
                        tablename,
                        columnname,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                    ORDER BY schemaname, tablename, ordinal_position
                    """
                    cur.execute(query)
                    columns = cur.fetchall()
                    
                    classifications = []
                    for col in columns:
                        classification = self._classify_column(
                            col['tablename'], 
                            col['columnname'], 
                            col['data_type']
                        )
                        if classification:
                            classifications.append(classification)
                    
                    self.data_classifications = classifications
                    logger.info(f"发现 {len(classifications)} 个数据分类")
                    return classifications
                    
        except Exception as e:
            logger.error(f"数据分类发现失败: {e}")
            raise
    
    def _classify_column(self, table_name: str, column_name: str, data_type: str) -> Optional[DataClassification]:
        """根据列名和数据类型分类数据"""
        
        column_lower = column_name.lower()
        
        # 个人识别信息(PII)检测模式
        pii_patterns = [
            'email', 'phone', 'mobile', 'address', 'ssn', 'social_security',
            'passport', 'driver_license', 'national_id', 'name', 'first_name',
            'last_name', 'full_name', 'birth', 'birthday', 'age'
        ]
        
        # 受保护健康信息(PHI)检测模式
        phi_patterns = [
            'medical', 'health', 'diagnosis', 'treatment', 'medication',
            'allergy', 'disease', 'condition', 'blood_type', 'weight',
            'height', 'insurance', 'patient_id', 'doctor_id'
        ]
        
        # 财务信息检测模式
        financial_patterns = [
            'credit_card', 'debit_card', 'card_number', 'cvv', 'bank_account',
            'routing_number', 'iban', 'swift', 'payment', 'transaction',
            'salary', 'income', 'account_balance', 'balance', 'amount',
            'price', 'cost', 'fee', 'charge', 'refund'
        ]
        
        # 检查PII
        contains_pii = any(pattern in column_lower for pattern in pii_patterns)
        
        # 检查PHI
        contains_phi = any(pattern in column_lower for pattern in phi_patterns)
        
        # 检查财务信息
        contains_financial = any(pattern in column_lower for pattern in financial_patterns)
        
        # 特殊列检测
        if column_lower in ['id', 'uuid', 'created_at', 'updated_at', 'timestamp']:
            contains_pii = contains_phi = contains_financial = False
        
        # 确定分类级别
        if contains_phi:
            classification_level = "RESTRICTED"
        elif contains_financial or contains_pii:
            classification_level = "CONFIDENTIAL"
        elif data_type in ['text', 'varchar', 'char']:
            classification_level = "INTERNAL"
        else:
            classification_level = "PUBLIC"
        
        # 确定是否需要加密
        encryption_required = classification_level in ["CONFIDENTIAL", "RESTRICTED"]
        
        # 确定保留期限
        retention_periods = {
            "PUBLIC": 365,
            "INTERNAL": 2555,  # 7年
            "CONFIDENTIAL": 3650,  # 10年
            "RESTRICTED": 7300   # 20年
        }
        retention_period = retention_periods.get(classification_level, 365)
        
        if contains_pii or contains_phi or contains_financial:
            return DataClassification(
                table_name=table_name,
                column_name=column_name,
                data_type=data_type,
                classification_level=classification_level,
                contains_pii=contains_pii,
                contains_phi=contains_phi,
                contains_financial=contains_financial,
                encryption_required=encryption_required,
                retention_period=retention_period
            )
        
        return None
    
    def run_gdpr_compliance_check(self) -> List[ComplianceCheck]:
        """
        运行GDPR合规检查
        
        Returns:
            合规检查结果列表
        """
        logger.info("开始GDPR合规检查...")
        
        gdpr_checks = []
        
        try:
            # 1. 数据最小化检查
            sensitive_data_check = self._check_data_minimization()
            gdpr_checks.append(sensitive_data_check)
            
            # 2. 数据主体权利检查
            data_subject_rights_check = self._check_data_subject_rights()
            gdpr_checks.append(data_subject_rights_check)
            
            # 3. 数据保留检查
            data_retention_check = self._check_data_retention()
            gdpr_checks.append(data_retention_check)
            
            # 4. 数据转移检查
            data_transfer_check = self._check_data_transfer()
            gdpr_checks.append(data_transfer_check)
            
            # 5. 数据安全检查
            data_security_check = self._check_data_security()
            gdpr_checks.append(data_security_check)
            
            # 6. 同意管理检查
            consent_management_check = self._check_consent_management()
            gdpr_checks.append(consent_management_check)
            
            self.compliance_checks.extend(gdpr_checks)
            return gdpr_checks
            
        except Exception as e:
            logger.error(f"GDPR合规检查失败: {e}")
            raise
    
    def _check_data_minimization(self) -> ComplianceCheck:
        """检查数据最小化"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查是否有不必要的敏感数据
                    cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE column_name IN ('ssn', 'social_security', 'credit_card', 'bank_account')
                    AND table_schema NOT IN ('information_schema', 'pg_catalog')
                    """)
                    sensitive_columns = cur.fetchone()[0]
                    
                    status = ComplianceStatus.COMPLIANT if sensitive_columns == 0 else ComplianceStatus.NEEDS_REVIEW
                    risk_level = RiskLevel.HIGH if sensitive_columns > 0 else RiskLevel.LOW
                    
                    return ComplianceCheck(
                        check_id="GDPR_DATA_MINIMIZATION",
                        regulation="GDPR",
                        requirement="数据最小化原则 - 只收集必要的数据",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"发现 {sensitive_columns} 个敏感数据列",
                        remediation_steps=[
                            "审查数据收集的必要性",
                            "删除不必要的历史数据",
                            "实施数据分类和标记"
                        ] if sensitive_columns > 0 else [
                            "继续监控数据收集",
                            "定期审查数据需求"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="数据保护官"
                    )
        except Exception as e:
            logger.error(f"数据最小化检查失败: {e}")
            raise
    
    def _check_data_subject_rights(self) -> ComplianceCheck:
        """检查数据主体权利"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查是否有数据访问、更新和删除功能
                    tables_with_audit = []
                    
                    # 简化的检查，实际应该检查具体的访问控制机制
                    cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema LIKE '%security%' OR table_name LIKE '%audit%'
                    """)
                    audit_count = cur.fetchone()[0]
                    
                    status = ComplianceStatus.COMPLIANT if audit_count > 0 else ComplianceStatus.NEEDS_REVIEW
                    risk_level = RiskLevel.MEDIUM if audit_count == 0 else RiskLevel.LOW
                    
                    return ComplianceCheck(
                        check_id="GDPR_DATA_SUBJECT_RIGHTS",
                        regulation="GDPR",
                        requirement="数据主体权利 - 访问、更正、删除、限制处理的权利",
                        current_status=status,
                        risk_level=risk_level,
                        description="检查数据主体权利实现情况",
                        remediation_steps=[
                            "实施数据访问请求流程",
                            "建立数据更正机制",
                            "创建数据删除功能"
                        ] if audit_count == 0 else [
                            "测试数据主体权利实现",
                            "优化访问流程"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="数据保护官"
                    )
        except Exception as e:
            logger.error(f"数据主体权利检查失败: {e}")
            raise
    
    def _check_data_retention(self) -> ComplianceCheck:
        """检查数据保留策略"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查是否有数据保留和清理机制
                    cur.execute("""
                    SELECT COUNT(*) 
                    FROM pg_stat_user_tables 
                    WHERE last_vacuum_time < CURRENT_DATE - INTERVAL '1 month'
                    """)
                    stale_tables = cur.fetchone()[0]
                    
                    total_tables = self._get_total_user_tables()
                    retention_ratio = (total_tables - stale_tables) / max(total_tables, 1)
                    
                    if retention_ratio > 0.8:
                        status = ComplianceStatus.COMPLIANT
                        risk_level = RiskLevel.LOW
                    elif retention_ratio > 0.5:
                        status = ComplianceStatus.PARTIAL_COMPLIANT
                        risk_level = RiskLevel.MEDIUM
                    else:
                        status = ComplianceStatus.NON_COMPLIANT
                        risk_level = RiskLevel.HIGH
                    
                    return ComplianceCheck(
                        check_id="GDPR_DATA_RETENTION",
                        regulation="GDPR",
                        requirement="数据保留 - 制定并实施数据保留和删除政策",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"数据维护比率: {retention_ratio:.2%}",
                        remediation_steps=[
                            "制定明确的数据保留政策",
                            "实施自动化数据清理",
                            "建立数据归档机制"
                        ] if retention_ratio < 0.8 else [
                            "继续执行保留政策",
                            "定期审查保留期限"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="数据管理员"
                    )
        except Exception as e:
            logger.error(f"数据保留检查失败: {e}")
            raise
    
    def _check_data_transfer(self) -> ComplianceCheck:
        """检查数据转移合规性"""
        try:
            # GDPR数据转移检查（简化实现）
            return ComplianceCheck(
                check_id="GDPR_DATA_TRANSFER",
                regulation="GDPR",
                requirement="数据转移 - 确保跨境数据传输合规",
                current_status=ComplianceStatus.NEEDS_REVIEW,
                risk_level=RiskLevel.MEDIUM,
                description="检查数据传输机制和合规性",
                remediation_steps=[
                    "审查数据转移协议",
                    "确保充足的保障措施",
                    "记录数据转移活动"
                ],
                last_checked=datetime.datetime.now(),
                responsible_party="法务部门"
            )
        except Exception as e:
            logger.error(f"数据转移检查失败: {e}")
            raise
    
    def _check_data_security(self) -> ComplianceCheck:
        """检查数据安全措施"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查SSL、加密等安全配置
                    cur.execute("""
                    SELECT current_setting('ssl', true) as ssl_enabled,
                           current_setting('password_encryption', true) as password_encryption
                    """)
                    security_settings = cur.fetchone()
                    
                    ssl_enabled = security_settings[0] == 'on'
                    password_encrypted = security_settings[1] != 'off'
                    
                    if ssl_enabled and password_encrypted:
                        status = ComplianceStatus.COMPLIANT
                        risk_level = RiskLevel.LOW
                    elif ssl_enabled or password_encrypted:
                        status = ComplianceStatus.PARTIAL_COMPLIANT
                        risk_level = RiskLevel.MEDIUM
                    else:
                        status = ComplianceStatus.NON_COMPLIANT
                        risk_level = RiskLevel.HIGH
                    
                    return ComplianceCheck(
                        check_id="GDPR_DATA_SECURITY",
                        regulation="GDPR",
                        requirement="数据安全 - 实施适当的技术和组织安全措施",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"SSL启用: {ssl_enabled}, 密码加密: {password_encrypted}",
                        remediation_steps=[
                            "启用SSL/TLS加密",
                            "实施强密码策略",
                            "配置访问控制和审计"
                        ] if not (ssl_enabled and password_encrypted) else [
                            "定期安全审计",
                            "监控安全事件"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="安全团队"
                    )
        except Exception as e:
            logger.error(f"数据安全检查失败: {e}")
            raise
    
    def _check_consent_management(self) -> ComplianceCheck:
        """检查同意管理机制"""
        try:
            # 同意管理检查（简化实现）
            return ComplianceCheck(
                check_id="GDPR_CONSENT_MANAGEMENT",
                regulation="GDPR",
                requirement="同意管理 - 确保有有效的同意机制",
                current_status=ComplianceStatus.NEEDS_REVIEW,
                risk_level=RiskLevel.MEDIUM,
                description="检查用户同意管理实现情况",
                remediation_steps=[
                    "实施明确同意机制",
                    "记录同意历史",
                    "提供撤回同意的选项"
                ],
                last_checked=datetime.datetime.now(),
                responsible_party="产品团队"
            )
        except Exception as e:
            logger.error(f"同意管理检查失败: {e}")
            raise
    
    def _get_total_user_tables(self) -> int:
        """获取用户表总数"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    """)
                    return cur.fetchone()[0]
        except:
            return 0
    
    def run_sox_compliance_check(self) -> List[ComplianceCheck]:
        """
        运行SOX合规检查
        
        Returns:
            合规检查结果列表
        """
        logger.info("开始SOX合规检查...")
        
        sox_checks = []
        
        try:
            # 1. 访问控制检查
            access_control_check = self._check_sox_access_control()
            sox_checks.append(access_control_check)
            
            # 2. 审计日志检查
            audit_log_check = self._check_sox_audit_logging()
            sox_checks.append(audit_log_check)
            
            # 3. 数据完整性检查
            data_integrity_check = self._check_sox_data_integrity()
            sox_checks.append(data_integrity_check)
            
            # 4. 变更管理检查
            change_management_check = self._check_sox_change_management()
            sox_checks.append(change_management_check)
            
            # 5. 分离职责检查
            segregation_duties_check = self._check_sox_segregation_duties()
            sox_checks.append(segregation_duties_check)
            
            self.compliance_checks.extend(sox_checks)
            return sox_checks
            
        except Exception as e:
            logger.error(f"SOX合规检查失败: {e}")
            raise
    
    def _check_sox_access_control(self) -> ComplianceCheck:
        """检查SOX访问控制"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查超级用户权限
                    cur.execute("""
                    SELECT COUNT(*) FROM pg_roles 
                    WHERE rolsuper = true AND rolname NOT IN ('postgres')
                    """)
                    super_users = cur.fetchone()[0]
                    
                    status = ComplianceStatus.COMPLIANT if super_users == 0 else ComplianceStatus.NEEDS_REVIEW
                    risk_level = RiskLevel.HIGH if super_users > 0 else RiskLevel.LOW
                    
                    return ComplianceCheck(
                        check_id="SOX_ACCESS_CONTROL",
                        regulation="SOX",
                        requirement="访问控制 - 实施适当的访问权限管理",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"发现 {super_users} 个超级用户账户",
                        remediation_steps=[
                            "移除不必要的超级用户权限",
                            "实施基于角色的访问控制",
                            "定期审查用户权限"
                        ] if super_users > 0 else [
                            "监控访问权限使用",
                            "维护最小权限原则"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="系统管理员"
                    )
        except Exception as e:
            logger.error(f"SOX访问控制检查失败: {e}")
            raise
    
    def _check_sox_audit_logging(self) -> ComplianceCheck:
        """检查SOX审计日志"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查审计日志配置
                    cur.execute("""
                    SELECT current_setting('log_statement', true) as log_statement,
                           current_setting('log_destination', true) as log_destination
                    """)
                    logging_settings = cur.fetchone()
                    
                    log_statement = logging_settings[0]
                    log_destination = logging_settings[1]
                    
                    logging_enabled = log_statement != 'none' and 'stderr' in log_destination
                    
                    status = ComplianceStatus.COMPLIANT if logging_enabled else ComplianceStatus.NON_COMPLIANT
                    risk_level = RiskLevel.HIGH if not logging_enabled else RiskLevel.LOW
                    
                    return ComplianceCheck(
                        check_id="SOX_AUDIT_LOGGING",
                        regulation="SOX",
                        requirement="审计日志 - 记录所有重要系统活动",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"日志记录配置: {log_statement}, 日志目的地: {log_destination}",
                        remediation_steps=[
                            "启用详细的日志记录",
                            "配置适当的日志目的地",
                            "确保日志完整性保护"
                        ] if not logging_enabled else [
                            "定期审查日志内容",
                            "确保日志留存政策"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="系统管理员"
                    )
        except Exception as e:
            logger.error(f"SOX审计日志检查失败: {e}")
            raise
    
    def _check_sox_data_integrity(self) -> ComplianceCheck:
        """检查SOX数据完整性"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查数据约束
                    cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.check_constraints cc
                    JOIN information_schema.constraint_column_usage ccu 
                      ON cc.constraint_name = ccu.constraint_name
                    """)
                    constraints_count = cur.fetchone()[0]
                    
                    # 检查外键约束
                    cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.table_constraints tc
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    """)
                    foreign_keys = cur.fetchone()[0]
                    
                    integrity_score = (constraints_count + foreign_keys) / max(1, self._get_total_user_tables())
                    
                    if integrity_score > 0.8:
                        status = ComplianceStatus.COMPLIANT
                        risk_level = RiskLevel.LOW
                    elif integrity_score > 0.5:
                        status = ComplianceStatus.PARTIAL_COMPLIANT
                        risk_level = RiskLevel.MEDIUM
                    else:
                        status = ComplianceStatus.NON_COMPLIANT
                        risk_level = RiskLevel.HIGH
                    
                    return ComplianceCheck(
                        check_id="SOX_DATA_INTEGRITY",
                        regulation="SOX",
                        requirement="数据完整性 - 确保数据准确性和完整性",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"数据完整性比率: {integrity_score:.2%}",
                        remediation_steps=[
                            "增加数据约束和验证",
                            "实施外键完整性",
                            "建立数据验证流程"
                        ] if integrity_score < 0.8 else [
                            "维护数据约束",
                            "监控数据质量"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="数据库管理员"
                    )
        except Exception as e:
            logger.error(f"SOX数据完整性检查失败: {e}")
            raise
    
    def _check_sox_change_management(self) -> ComplianceCheck:
        """检查SOX变更管理"""
        try:
            return ComplianceCheck(
                check_id="SOX_CHANGE_MANAGEMENT",
                regulation="SOX",
                requirement="变更管理 - 实施变更管理流程",
                current_status=ComplianceStatus.NEEDS_REVIEW,
                risk_level=RiskLevel.MEDIUM,
                description="检查变更管理流程实现情况",
                remediation_steps=[
                    "建立变更管理流程",
                    "记录所有数据库变更",
                    "实施变更审批机制"
                ],
                last_checked=datetime.datetime.now(),
                responsible_party="变更管理团队"
            )
        except Exception as e:
            logger.error(f"SOX变更管理检查失败: {e}")
            raise
    
    def _check_sox_segregation_duties(self) -> ComplianceCheck:
        """检查SOX分离职责"""
        try:
            with self.connect_database() as conn:
                with conn.cursor() as cur:
                    # 检查职责分离
                    cur.execute("""
                    SELECT COUNT(*) FROM pg_roles 
                    WHERE rolcreaterole = true AND rolcreatedb = true
                    """)
                    admin_roles = cur.fetchone()[0]
                    
                    status = ComplianceStatus.COMPLIANT if admin_roles <= 1 else ComplianceStatus.NEEDS_REVIEW
                    risk_level = RiskLevel.MEDIUM if admin_roles > 1 else RiskLevel.LOW
                    
                    return ComplianceCheck(
                        check_id="SOX_SEGREGATION_DUTIES",
                        regulation="SOX",
                        requirement="分离职责 - 分离不相容的职责",
                        current_status=status,
                        risk_level=risk_level,
                        description=f"发现 {admin_roles} 个具有管理权限的账户",
                        remediation_steps=[
                            "分离创建角色和数据库的权限",
                            "实施职责分离政策",
                            "定期审查权限分配"
                        ] if admin_roles > 1 else [
                            "监控权限使用",
                            "维护分离职责"
                        ],
                        last_checked=datetime.datetime.now(),
                        responsible_party="安全团队"
                    )
        except Exception as e:
            logger.error(f"SOX分离职责检查失败: {e}")
            raise
    
    def generate_compliance_report(self, output_format: str = "html") -> str:
        """
        生成合规报告
        
        Args:
            output_format: 输出格式 (html, pdf, json)
            
        Returns:
            合规报告内容
        """
        logger.info(f"生成{output_format.upper()}格式的合规报告...")
        
        try:
            # 计算整体合规分数
            total_checks = len(self.compliance_checks)
            compliant_checks = sum(1 for check in self.compliance_checks if check.current_status == ComplianceStatus.COMPLIANT)
            compliance_score = (compliant_checks / max(total_checks, 1)) * 100
            
            # 按法规分组统计
            regulation_stats = {}
            for check in self.compliance_checks:
                if check.regulation not in regulation_stats:
                    regulation_stats[check.regulation] = {'total': 0, 'compliant': 0}
                regulation_stats[check.regulation]['total'] += 1
                if check.current_status == ComplianceStatus.COMPLIANT:
                    regulation_stats[check.regulation]['compliant'] += 1
            
            if output_format.lower() == "html":
                return self._generate_html_report(compliance_score, regulation_stats)
            elif output_format.lower() == "json":
                return self._generate_json_report(compliance_score, regulation_stats)
            else:
                raise ValueError(f"不支持的报告格式: {output_format}")
                
        except Exception as e:
            logger.error(f"合规报告生成失败: {e}")
            raise
    
    def _generate_html_report(self, compliance_score: float, regulation_stats: Dict) -> str:
        """生成HTML格式报告"""
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>PostgreSQL安全合规报告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { display: flex; justify-content: space-around; margin: 20px 0; }
                .metric { text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                .regulation-section { margin: 20px 0; }
                .check-item { padding: 10px; margin: 5px 0; border-left: 4px solid #ddd; }
                .compliant { border-left-color: #4CAF50; background-color: #f1f8e9; }
                .non-compliant { border-left-color: #f44336; background-color: #ffebee; }
                .partial-compliant { border-left-color: #ff9800; background-color: #fff3e0; }
                .needs-review { border-left-color: #2196F3; background-color: #e3f2fd; }
                .risk-low { color: #4CAF50; }
                .risk-medium { color: #ff9800; }
                .risk-high { color: #f44336; }
                .risk-critical { color: #9c27b0; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PostgreSQL安全合规报告</h1>
                <p>生成时间: {{ report_time }}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h2>{{ "%.1f"|format(compliance_score) }}%</h2>
                    <p>整体合规分数</p>
                </div>
                <div class="metric">
                    <h2>{{ total_checks }}</h2>
                    <p>总检查项目</p>
                </div>
                <div class="metric">
                    <h2>{{ compliant_checks }}</h2>
                    <p>合规项目</p>
                </div>
            </div>
            
            <h2>法规合规统计</h2>
            <table>
                <tr>
                    <th>法规</th>
                    <th>合规比率</th>
                    <th>合规项目/总项目</th>
                </tr>
                {% for regulation, stats in regulation_stats.items() %}
                <tr>
                    <td>{{ regulation }}</td>
                    <td>{{ "%.1f"|format((stats.compliant / stats.total) * 100) }}%</td>
                    <td>{{ stats.compliant }}/{{ stats.total }}</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>详细检查结果</h2>
            {% for check in compliance_checks %}
            <div class="check-item {{ check.current_status.value.lower().replace(' ', '-') }}">
                <h3>{{ check.check_id }} - {{ check.requirement }}</h3>
                <p><strong>法规:</strong> {{ check.regulation }}</p>
                <p><strong>状态:</strong> {{ check.current_status.value }}</p>
                <p><strong>风险等级:</strong> <span class="risk-{{ check.risk_level.value.lower().replace('风险', '').replace(' ', '-') }}">{{ check.risk_level.value }}</span></p>
                <p><strong>描述:</strong> {{ check.description }}</p>
                <p><strong>负责方:</strong> {{ check.responsible_party }}</p>
                {% if check.remediation_steps %}
                <p><strong>整改建议:</strong></p>
                <ul>
                    {% for step in check.remediation_steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </body>
        </html>
        """
        
        template = Template(html_template)
        return template.render(
            report_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            compliance_score=compliance_score,
            total_checks=total_checks,
            compliant_checks=compliant_checks,
            regulation_stats=regulation_stats,
            compliance_checks=self.compliance_checks
        )
    
    def _generate_json_report(self, compliance_score: float, regulation_stats: Dict) -> str:
        """生成JSON格式报告"""
        
        report_data = {
            "report_metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "report_version": "1.0",
                "database_compliance_manager": "PostgreSQL Security Compliance Manager"
            },
            "overall_compliance": {
                "compliance_score": compliance_score,
                "total_checks": len(self.compliance_checks),
                "compliant_checks": sum(1 for check in self.compliance_checks if check.current_status == ComplianceStatus.COMPLIANT),
                "compliance_percentage": (sum(1 for check in self.compliance_checks if check.current_status == ComplianceStatus.COMPLIANT) / max(len(self.compliance_checks), 1)) * 100
            },
            "regulation_breakdown": regulation_stats,
            "detailed_checks": []
        }
        
        for check in self.compliance_checks:
            check_data = {
                "check_id": check.check_id,
                "regulation": check.regulation,
                "requirement": check.requirement,
                "status": check.current_status.value,
                "risk_level": check.risk_level.value,
                "description": check.description,
                "responsible_party": check.responsible_party,
                "last_checked": check.last_checked.isoformat(),
                "remediation_steps": check.remediation_steps
            }
            report_data["detailed_checks"].append(check_data)
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def save_data_classifications_to_file(self, filename: str):
        """保存数据分类到文件"""
        try:
            data = []
            for classification in self.data_classifications:
                data.append({
                    "table_name": classification.table_name,
                    "column_name": classification.column_name,
                    "data_type": classification.data_type,
                    "classification_level": classification.classification_level,
                    "contains_pii": classification.contains_pii,
                    "contains_phi": classification.contains_phi,
                    "contains_financial": classification.contains_financial,
                    "encryption_required": classification.encryption_required,
                    "retention_period": classification.retention_period
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"数据分类已保存到 {filename}")
            
        except Exception as e:
            logger.error(f"保存数据分类失败: {e}")
            raise
    
    def create_compliance_dashboard(self):
        """创建合规仪表板"""
        try:
            # 创建数据
            compliance_data = {
                'Regulation': [],
                'Compliance_Score': [],
                'Total_Checks': [],
                'Compliant_Checks': []
            }
            
            regulation_stats = {}
            for check in self.compliance_checks:
                if check.regulation not in regulation_stats:
                    regulation_stats[check.regulation] = {'total': 0, 'compliant': 0}
                regulation_stats[check.regulation]['total'] += 1
                if check.current_status == ComplianceStatus.COMPLIANT:
                    regulation_stats[check.regulation]['compliant'] += 1
            
            for regulation, stats in regulation_stats.items():
                compliance_data['Regulation'].append(regulation)
                compliance_data['Total_Checks'].append(stats['total'])
                compliance_data['Compliant_Checks'].append(stats['compliant'])
                compliance_data['Compliance_Score'].append((stats['compliant'] / stats['total']) * 100)
            
            # 创建图表
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('PostgreSQL安全合规仪表板', fontsize=16, fontweight='bold')
            
            # 1. 法规合规分数柱状图
            bars = ax1.bar(compliance_data['Regulation'], compliance_data['Compliance_Score'])
            ax1.set_title('法规合规分数')
            ax1.set_ylabel('合规分数 (%)')
            ax1.set_ylim(0, 100)
            ax1.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='目标线 (80%)')
            ax1.legend()
            
            # 添加数值标签
            for bar, score in zip(bars, compliance_data['Compliance_Score']):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score:.1f}%', ha='center', va='bottom')
            
            # 2. 检查项目分布饼图
            status_counts = {}
            for check in self.compliance_checks:
                status = check.current_status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            colors = ['#4CAF50', '#f44336', '#ff9800', '#2196F3', '#9E9E9E']
            ax2.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%',
                   colors=colors[:len(status_counts)])
            ax2.set_title('合规状态分布')
            
            # 3. 风险等级分布
            risk_counts = {}
            for check in self.compliance_checks:
                risk = check.risk_level.value
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            ax3.bar(risk_counts.keys(), risk_counts.values(), 
                   color=['#4CAF50', '#FF9800', '#F44336', '#9C27B0'])
            ax3.set_title('风险等级分布')
            ax3.set_ylabel('检查项目数量')
            
            # 4. 合规趋势（如果有历史数据）
            # 这里可以添加时间序列数据
            compliance_data_df = pd.DataFrame(compliance_data)
            if len(compliance_data_df) > 0:
                ax4.barh(compliance_data_df['Regulation'], compliance_data_df['Compliance_Score'])
                ax4.set_title('法规合规分数详情')
                ax4.set_xlabel('合规分数 (%)')
                ax4.axvline(x=80, color='r', linestyle='--', alpha=0.7, label='目标线')
                ax4.legend()
            
            plt.tight_layout()
            
            # 保存图表
            plt.savefig('security_compliance_dashboard.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            logger.info("合规仪表板已生成并保存为 security_compliance_dashboard.png")
            
        except Exception as e:
            logger.error(f"创建合规仪表板失败: {e}")
            raise

def main():
    """主函数 - 演示用法"""
    
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'password'
    }
    
    try:
        # 创建合规管理器
        compliance_manager = SecurityComplianceManager(db_config)
        
        # 1. 发现数据分类
        print("=== 数据分类发现 ===")
        data_classifications = compliance_manager.discover_data_classifications()
        for classification in data_classifications[:5]:  # 显示前5个
            print(f"表: {classification.table_name}, 列: {classification.column_name}, "
                  f"分类: {classification.classification_level}, "
                  f"包含PII: {classification.contains_pii}")
        
        # 2. 运行GDPR合规检查
        print("\n=== GDPR合规检查 ===")
        gdpr_checks = compliance_manager.run_gdpr_compliance_check()
        for check in gdpr_checks:
            print(f"检查: {check.check_id}, 状态: {check.current_status.value}, "
                  f"风险: {check.risk_level.value}")
        
        # 3. 运行SOX合规检查
        print("\n=== SOX合规检查 ===")
        sox_checks = compliance_manager.run_sox_compliance_check()
        for check in sox_checks:
            print(f"检查: {check.check_id}, 状态: {check.current_status.value}, "
                  f"风险: {check.risk_level.value}")
        
        # 4. 生成合规报告
        print("\n=== 生成合规报告 ===")
        html_report = compliance_manager.generate_compliance_report("html")
        with open("compliance_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        print("HTML报告已生成: compliance_report.html")
        
        json_report = compliance_manager.generate_compliance_report("json")
        with open("compliance_report.json", "w", encoding="utf-8") as f:
            f.write(json_report)
        print("JSON报告已生成: compliance_report.json")
        
        # 5. 保存数据分类
        print("\n=== 保存数据分类 ===")
        compliance_manager.save_data_classifications_to_file("data_classifications.json")
        
        # 6. 创建仪表板
        print("\n=== 创建合规仪表板 ===")
        compliance_manager.create_compliance_dashboard()
        
        print("\n=== 合规检查完成 ===")
        print("所有检查项目:")
        for check in compliance_manager.compliance_checks:
            print(f"- {check.check_id} ({check.regulation}): {check.current_status.value}")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
