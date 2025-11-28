#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5章：元数据治理与管理 代码示例
本文件包含元数据治理与管理的实用代码示例，可直接运行
"""

import json
from datetime import datetime, timedelta
from enum import Enum

# ====================
# 5.1 元数据治理策略类
# ====================

class MetadataGovernanceStrategy:
    """
    元数据治理策略定义
    包含命名规范、所有权要求、分类标准等治理策略
    """
    def __init__(self):
        self.policies = {
            "naming": {
                "convention": "snake_case",
                "prefix": {
                    "table": "tbl_",
                    "view": "vw_",
                    "procedure": "sp_"
                }
            },
            "ownership": {
                "data_steward_required": True,
                "technical_owner_required": True,
                "business_owner_required": True
            },
            "classification": {
                "sensitivity_levels": ["public", "internal", "confidential", "restricted"],
                "data_categories": ["PII", "Financial", "Health", "Operational"]
            },
            "retention": {
                "default_retention_days": 2555,  # 7年
                "archive_after_days": 1095,     # 3年
                "delete_after_days": 3650       # 10年
            },
            "access_control": {
                "rbac_enabled": True,
                "default_permissions": "read",
                "approval_required_for_write": True
            }
        }
    
    def validate_naming(self, metadata_type, name):
        """验证命名是否符合规范"""
        policy = self.policies["naming"]
        expected_prefix = policy["prefix"].get(metadata_type, "")
        
        if expected_prefix and not name.startswith(expected_prefix):
            return False, f"{metadata_type}名称应以'{expected_prefix}'为前缀"
            
        if policy["convention"] == "snake_case" and "_" not in name:
            return False, "名称应使用snake_case命名规范"
            
        return True, "命名符合规范"
    
    def check_ownership(self, owners):
        """检查所有权信息是否完整"""
        policy = self.policies["ownership"]
        missing = []
        
        if policy.get("data_steward_required") and "data_steward" not in owners:
            missing.append("数据管理员")
        if policy.get("technical_owner_required") and "technical_owner" not in owners:
            missing.append("技术负责人")
        if policy.get("business_owner_required") and "business_owner" not in owners:
            missing.append("业务负责人")
            
        return len(missing) == 0, missing
    
    def classify_data(self, sensitivity, categories):
        """数据分类验证"""
        valid_sensitivity = sensitivity in self.policies["classification"]["sensitivity_levels"]
        valid_categories = all(cat in self.policies["classification"]["data_categories"] for cat in categories)
        
        return valid_sensitivity and valid_categories


# ====================
# 5.2 元数据治理组织管理
# ====================

class DataGovernanceOrganization:
    """
    数据治理组织结构管理
    定义角色、职责和权限管理
    """
    def __init__(self):
        self.roles = {
            "committee": {
                "name": "数据治理委员会",
                "responsibilities": [
                    "制定数据治理策略和方向",
                    "审批重要数据资产决策",
                    "监督治理执行情况",
                    "解决跨部门数据争议"
                ],
                "meeting_frequency": "季度"
            },
            "steward": {
                "name": "数据管理员",
                "responsibilities": [
                    "定义业务术语和数据标准",
                    "维护数据质量和完整性",
                    "监控数据使用情况",
                    "处理数据相关问题"
                ],
                "skills": ["业务领域知识", "数据管理", "沟通能力", "问题解决"]
            },
            "architect": {
                "name": "数据架构师",
                "responsibilities": [
                    "设计数据架构和模型",
                    "制定技术标准和规范",
                    "评估新技术和工具",
                    "优化数据性能"
                ],
                "skills": ["数据建模", "系统设计", "技术架构", "性能优化"]
            },
            "analyst": {
                "name": "数据质量分析师",
                "responsibilities": [
                    "定义数据质量规则",
                    "监控数据质量指标",
                    "识别和分析数据问题",
                    "报告质量改进建议"
                ],
                "skills": ["数据分析", "质量评估", "规则设计", "报告生成"]
            }
        }
    
    def get_role_responsibilities(self, role):
        """获取角色职责"""
        return self.roles.get(role, {}).get("responsibilities", [])
    
    def get_required_skills(self, role):
        """获取角色所需技能"""
        return self.roles.get(role, {}).get("skills", [])
    
    def assign_steward(self, data_domain, steward_name, contact_info):
        """分配数据管理员"""
        assignment = {
            "data_domain": data_domain,
            "steward_name": steward_name,
            "contact_info": contact_info,
            "assignment_date": datetime.now().isoformat(),
            "status": "active"
        }
        return assignment
    
    def define_role_permissions(self, role):
        """定义角色权限"""
        permissions = {
            "committee": ["approve_policies", "resolve_disputes", "oversight"],
            "steward": ["define_standards", "manage_metadata", "approve_changes"],
            "architect": ["design_models", "set_technical_standards", "approve_technical_changes"],
            "analyst": ["monitor_quality", "define_rules", "report_issues"]
        }
        return permissions.get(role, [])


# ====================
# 5.3 元数据生命周期管理
# ====================

class MetadataLifecycleStatus(Enum):
    """元数据生命周期状态"""
    DRAFT = "草稿"
    PENDING_APPROVAL = "待审批"
    ACTIVE = "活跃"
    UNDER_REVIEW = "审查中"
    ARCHIVED = "已归档"
    DEPRECATED = "已废弃"
    DELETED = "已删除"

class MetadataLifecycleManager:
    """元数据生命周期管理"""
    
    def __init__(self):
        self.lifecycle_rules = {
            "draft_max_days": 30,         # 草稿状态最长天数
            "approval_max_days": 14,      # 审批最长天数
            "review_interval_days": 180,  # 审查间隔天数
            "archive_inactive_days": 365, # 不活跃数据归档天数
            "delete_after_archive_days": 1825  # 归档后删除天数
        }
    
    def create_metadata(self, metadata_id, creator):
        """创建元数据"""
        metadata = {
            "id": metadata_id,
            "creator": creator,
            "created_at": datetime.now(),
            "status": MetadataLifecycleStatus.DRAFT,
            "status_history": [{
                "status": MetadataLifecycleStatus.DRAFT,
                "changed_at": datetime.now(),
                "changed_by": creator,
                "comment": "元数据创建"
            }],
            "last_reviewed": None,
            "next_review_date": None
        }
        return metadata
    
    def submit_for_approval(self, metadata, submitter, comment="提交审批"):
        """提交审批"""
        if metadata["status"] != MetadataLifecycleStatus.DRAFT:
            raise ValueError("只有草稿状态的元数据可以提交审批")
        
        metadata["status"] = MetadataLifecycleStatus.PENDING_APPROVAL
        metadata["status_history"].append({
            "status": MetadataLifecycleStatus.PENDING_APPROVAL,
            "changed_at": datetime.now(),
            "changed_by": submitter,
            "comment": comment
        })
        return metadata
    
    def approve_metadata(self, metadata, approver, comment="审批通过"):
        """审批通过"""
        if metadata["status"] != MetadataLifecycleStatus.PENDING_APPROVAL:
            raise ValueError("只有待审批状态的元数据可以审批")
        
        metadata["status"] = MetadataLifecycleStatus.ACTIVE
        metadata["status_history"].append({
            "status": MetadataLifecycleStatus.ACTIVE,
            "changed_at": datetime.now(),
            "changed_by": approver,
            "comment": comment
        })
        
        # 设置下次审查日期
        review_interval = timedelta(days=self.lifecycle_rules["review_interval_days"])
        metadata["last_reviewed"] = datetime.now()
        metadata["next_review_date"] = datetime.now() + review_interval
        
        return metadata
    
    def reject_metadata(self, metadata, approver, reason):
        """审批拒绝"""
        if metadata["status"] != MetadataLifecycleStatus.PENDING_APPROVAL:
            raise ValueError("只有待审批状态的元数据可以拒绝")
        
        metadata["status"] = MetadataLifecycleStatus.DRAFT
        metadata["status_history"].append({
            "status": MetadataLifecycleStatus.DRAFT,
            "changed_at": datetime.now(),
            "changed_by": approver,
            "comment": f"审批拒绝: {reason}"
        })
        return metadata


# ====================
# 5.4 元数据版本管理
# ====================

class MetadataVersionManager:
    """元数据版本管理"""
    
    def __init__(self):
        self.versions = {}  # metadata_id -> list of versions
        self.current_versions = {}  # metadata_id -> current version id
    
    def create_version(self, metadata_id, content, changed_by, change_description=""):
        """创建新版本"""
        version_id = f"{metadata_id}_v{len(self.versions.get(metadata_id, [])) + 1}"
        version = {
            "version_id": version_id,
            "metadata_id": metadata_id,
            "content": content,
            "changed_by": changed_by,
            "changed_at": datetime.now(),
            "change_description": change_description,
            "version_number": len(self.versions.get(metadata_id, [])) + 1
        }
        
        if metadata_id not in self.versions:
            self.versions[metadata_id] = []
        
        self.versions[metadata_id].append(version)
        self.current_versions[metadata_id] = version_id
        
        return version
    
    def get_version(self, metadata_id, version_number=None):
        """获取指定版本"""
        if metadata_id not in self.versions:
            return None
        
        if version_number is None:
            # 返回当前版本
            current_version_id = self.current_versions[metadata_id]
            for version in self.versions[metadata_id]:
                if version["version_id"] == current_version_id:
                    return version
        else:
            # 返回指定版本号
            for version in self.versions[metadata_id]:
                if version["version_number"] == version_number:
                    return version
        
        return None
    
    def get_version_history(self, metadata_id):
        """获取版本历史"""
        return self.versions.get(metadata_id, [])
    
    def compare_versions(self, metadata_id, version1, version2):
        """比较两个版本"""
        v1 = self.get_version(metadata_id, version1)
        v2 = self.get_version(metadata_id, version2)
        
        if not v1 or not v2:
            return None
        
        # 这里可以实现更复杂的差异比较逻辑
        differences = {
            "metadata_id": metadata_id,
            "version1": {
                "number": v1["version_number"],
                "changed_at": v1["changed_at"],
                "changed_by": v1["changed_by"]
            },
            "version2": {
                "number": v2["version_number"],
                "changed_at": v2["changed_at"],
                "changed_by": v2["changed_by"]
            }
        }
        
        # 简单的内容差异比较
        if v1["content"] != v2["content"]:
            differences["content_changed"] = True
        else:
            differences["content_changed"] = False
        
        return differences


# ====================
# 5.5 元数据安全管理
# ====================

class SensitivityLevel(Enum):
    """敏感度级别"""
    PUBLIC = "公开"
    INTERNAL = "内部"
    CONFIDENTIAL = "机密"
    RESTRICTED = "限制"

class MetadataSecurityManager:
    """元数据安全管理"""
    
    def __init__(self):
        self.user_roles = {}  # user_id -> [roles]
        self.role_permissions = {  # role -> [permissions]
            "admin": ["read", "write", "delete", "approve", "manage_users"],
            "steward": ["read", "write", "approve"],
            "analyst": ["read", "write"],
            "viewer": ["read"]
        }
        self.metadata_sensitivity = {}  # metadata_id -> sensitivity_level
        self.access_log = []  # 访问日志
    
    def assign_role(self, user_id, role):
        """分配用户角色"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        if role not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role)
        
        return True
    
    def check_permission(self, user_id, action, metadata_id=None):
        """检查用户权限"""
        if user_id not in self.user_roles:
            return False
        
        user_roles = self.user_roles[user_id]
        
        # 管理员拥有所有权限
        if "admin" in user_roles:
            return True
        
        # 检查角色权限
        for role in user_roles:
            if role in self.role_permissions:
                if action in self.role_permissions[role]:
                    # 如果涉及特定元数据，检查敏感度限制
                    if metadata_id and metadata_id in self.metadata_sensitivity:
                        sensitivity = self.metadata_sensitivity[metadata_id]
                        # 只有管理员可以访问RESTRICTED级别
                        if sensitivity == SensitivityLevel.RESTRICTED and role != "admin":
                            return False
                        # 只有管理员和管理员可以访问CONFIDENTIAL级别
                        if sensitivity == SensitivityLevel.CONFIDENTIAL and role not in ["admin", "steward"]:
                            return False
                    return True
        
        return False
    
    def set_sensitivity(self, metadata_id, sensitivity_level, changed_by):
        """设置元数据敏感度"""
        if not self.check_permission(changed_by, "write", metadata_id):
            raise PermissionError("无权限设置敏感度")
        
        self.metadata_sensitivity[metadata_id] = sensitivity_level
        
        # 记录操作
        self._log_access(changed_by, "set_sensitivity", metadata_id, 
                        f"设置敏感度为 {sensitivity_level.value}")
        
        return True
    
    def access_metadata(self, user_id, metadata_id, action="read"):
        """访问元数据"""
        if not self.check_permission(user_id, action, metadata_id):
            raise PermissionError(f"用户 {user_id} 无权限对元数据 {metadata_id} 执行 {action} 操作")
        
        # 记录访问日志
        self._log_access(user_id, action, metadata_id, "访问成功")
        
        return True
    
    def _log_access(self, user_id, action, metadata_id, result):
        """记录访问日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "metadata_id": metadata_id,
            "result": result,
            "ip_address": "127.0.0.1"  # 在实际应用中应获取真实IP
        }
        self.access_log.append(log_entry)
        
        # 在实际应用中，这里应该将日志写入持久化存储
        # 如数据库或日志文件


# ====================
# 5.6 合规性管理
# ====================

class ComplianceManager:
    """合规性管理"""
    
    def __init__(self):
        self.regulations = {
            "GDPR": {
                "name": "通用数据保护条例",
                "requirements": [
                    "数据最小化",
                    "目的限制",
                    "存储限制",
                    "准确性",
                    "完整性",
                    "问责制"
                ],
                "data_subject_rights": [
                    "访问权",
                    "更正权",
                    "删除权（被遗忘权）",
                    "限制处理权",
                    "数据可携带权",
                    "反对权"
                ]
            },
            "CCPA": {
                "name": "加州消费者隐私法案",
                "requirements": [
                    "透明度",
                    "消费者控制",
                    "数据安全",
                    "企业问责"
                ],
                "data_subject_rights": [
                    "知情权",
                    "删除权",
                    "选择退出权",
                    "非歧视权"
                ]
            }
        }
        
        self.compliance_checks = {
            "data_retention": self._check_retention_policy,
            "data_classification": self._check_classification,
            "access_control": self._check_access_control,
            "audit_trail": self._check_audit_trail
        }
    
    def get_regulation_info(self, regulation_code):
        """获取法规信息"""
        return self.regulations.get(regulation_code, {})
    
    def check_compliance(self, metadata, regulations=["GDPR"]):
        """检查合规性"""
        compliance_results = {}
        
        for regulation in regulations:
            if regulation in self.regulations:
                # 执行合规性检查
                results = self._run_compliance_checks(metadata, regulation)
                compliance_results[regulation] = results
        
        return compliance_results
    
    def _run_compliance_checks(self, metadata, regulation):
        """执行合规性检查"""
        checks = {}
        
        for check_name, check_func in self.compliance_checks.items():
            try:
                result = check_func(metadata, regulation)
                checks[check_name] = {
                    "passed": result["passed"],
                    "message": result["message"],
                    "details": result.get("details", {})
                }
            except Exception as e:
                checks[check_name] = {
                    "passed": False,
                    "message": f"检查失败: {str(e)}",
                    "details": {}
                }
        
        return checks
    
    def _check_retention_policy(self, metadata, regulation):
        """检查数据保留策略"""
        # 简化的检查逻辑
        if "retention_policy" in metadata and "retention_days" in metadata["retention_policy"]:
            retention_days = metadata["retention_policy"]["retention_days"]
            if retention_days <= 0:
                return {"passed": False, "message": "保留天数必须大于0"}
            
            # 对于GDPR，检查保留期限是否合理
            if regulation == "GDPR" and retention_days > 365 * 7:  # 7年
                return {
                    "passed": False, 
                    "message": "GDPR要求数据保留期限不超过必要时间",
                    "details": {"retention_days": retention_days, "max_recommended": 365 * 7}
                }
            
            return {"passed": True, "message": "数据保留策略符合要求"}
        
        return {"passed": False, "message": "缺少数据保留策略"}
    
    def _check_classification(self, metadata, regulation):
        """检查数据分类"""
        if "classification" not in metadata:
            return {"passed": False, "message": "缺少数据分类"}
        
        classification = metadata["classification"]
        if "sensitivity" not in classification:
            return {"passed": False, "message": "缺少敏感度分类"}
        
        # 对于GDPR，检查是否标识了个人数据
        if regulation == "GDPR":
            if "personal_data" not in classification:
                return {"passed": False, "message": "GDPR要求标识个人数据"}
        
        return {"passed": True, "message": "数据分类符合要求"}
    
    def _check_access_control(self, metadata, regulation):
        """检查访问控制"""
        if "access_control" not in metadata:
            return {"passed": False, "message": "缺少访问控制配置"}
        
        access_control = metadata["access_control"]
        if "allowed_roles" not in access_control:
            return {"passed": False, "message": "未定义允许的角色"}
        
        # 对于敏感数据，检查是否有适当的限制
        if metadata.get("classification", {}).get("sensitivity") in ["confidential", "restricted"]:
            if "approval_required" not in access_control or not access_control["approval_required"]:
                return {"passed": False, "message": "敏感数据需要审批流程"}
        
        return {"passed": True, "message": "访问控制配置合理"}
    
    def _check_audit_trail(self, metadata, regulation):
        """检查审计跟踪"""
        # 在实际应用中，这里会检查实际的审计日志
        # 这里只是检查元数据中是否定义了审计要求
        if "audit_requirements" not in metadata:
            return {"passed": False, "message": "缺少审计要求定义"}
        
        return {"passed": True, "message": "审计要求已定义"}
    
    def generate_compliance_report(self, compliance_results):
        """生成合规报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_regulations": len(compliance_results),
                "overall_status": "compliant"
            },
            "details": {}
        }
        
        for regulation, checks in compliance_results.items():
            passed_checks = sum(1 for check in checks.values() if check["passed"])
            total_checks = len(checks)
            status = "compliant" if passed_checks == total_checks else "non_compliant"
            
            if status == "non_compliant" and report["summary"]["overall_status"] == "compliant":
                report["summary"]["overall_status"] = "non_compliant"
            
            report["details"][regulation] = {
                "status": status,
                "passed_checks": passed_checks,
                "total_checks": total_checks,
                "checks": checks
            }
        
        return report


# ====================
# 示例使用代码
# ====================

def demo_governance_strategy():
    """演示元数据治理策略使用"""
    print("=== 元数据治理策略演示 ===")
    
    strategy = MetadataGovernanceStrategy()
    
    # 验证命名
    is_valid, message = strategy.validate_naming("table", "customer_data")
    print(f"命名验证: {is_valid}, {message}")
    
    # 检查所有权
    owners = {"data_steward": "张三", "technical_owner": "李四"}
    has_complete_ownership, missing = strategy.check_ownership(owners)
    print(f"所有权完整: {has_complete_ownership}, 缺失: {missing}")
    
    # 数据分类
    is_classified = strategy.classify_data("internal", ["Operational"])
    print(f"数据分类有效: {is_classified}")


def demo_organization():
    """演示治理组织管理"""
    print("\n=== 治理组织管理演示 ===")
    
    org = DataGovernanceOrganization()
    
    # 查看数据管理员职责
    steward_responsibilities = org.get_role_responsibilities("steward")
    print("数据管理员职责:")
    for resp in steward_responsibilities:
        print(f"- {resp}")
    
    # 分配数据管理员
    assignment = org.assign_steward("客户数据", "王五", "wangwu@company.com")
    print(f"\n数据管理员分配: {assignment}")
    
    # 查看角色权限
    permissions = org.define_role_permissions("steward")
    print(f"\n数据管理员权限: {permissions}")


def demo_lifecycle():
    """演示元数据生命周期管理"""
    print("\n=== 元数据生命周期管理演示 ===")
    
    lifecycle_manager = MetadataLifecycleManager()
    
    # 创建元数据
    metadata = lifecycle_manager.create_metadata("customer_metadata", "张三")
    print(f"创建元数据: 状态={metadata['status'].value}")
    
    # 提交审批
    metadata = lifecycle_manager.submit_for_approval(metadata, "张三")
    print(f"提交审批: 状态={metadata['status'].value}")
    
    # 审批通过
    metadata = lifecycle_manager.approve_metadata(metadata, "李四", "元数据定义清晰")
    print(f"审批通过: 状态={metadata['status'].value}, 下次审查={metadata['next_review_date'].strftime('%Y-%m-%d')}")


def demo_version_management():
    """演示版本管理"""
    print("\n=== 元数据版本管理演示 ===")
    
    version_manager = MetadataVersionManager()
    
    # 创建几个版本
    v1 = version_manager.create_version("product_metadata", {"name": "产品", "description": "产品描述"}, "张三", "初始版本")
    v2 = version_manager.create_version("product_metadata", {"name": "产品", "description": "产品详细描述"}, "李四", "更新描述")
    v3 = version_manager.create_version("product_metadata", {"name": "产品", "description": "产品详细描述", "category": "电子产品"}, "王五", "添加分类")
    
    # 获取当前版本
    current = version_manager.get_version("product_metadata")
    print(f"当前版本: {current['version_id']}, 描述: {current['content']['description']}")
    
    # 查看版本历史
    history = version_manager.get_version_history("product_metadata")
    print("\n版本历史:")
    for version in history:
        print(f"- {version['version_id']}: {version['change_description']} ({version['changed_by']}, {version['changed_at'].strftime('%Y-%m-%d')})")


def demo_security():
    """演示元数据安全管理"""
    print("\n=== 元数据安全管理演示 ===")
    
    security = MetadataSecurityManager()
    
    # 分配角色
    security.assign_role("user1", "analyst")
    security.assign_role("user2", "steward")
    security.assign_role("admin1", "admin")
    
    # 设置元数据敏感度
    security.set_sensitivity("customer_data", SensitivityLevel.CONFIDENTIAL, "admin1")
    security.set_sensitivity("product_data", SensitivityLevel.INTERNAL, "admin1")
    
    # 测试访问权限
    try:
        security.access_metadata("user1", "customer_data", "read")  # 应该失败
    except PermissionError as e:
        print(f"访问失败: {e}")
    
    try:
        security.access_metadata("user2", "customer_data", "read")  # 应该成功
        print("user2 访问 customer_data 成功")
    except PermissionError as e:
        print(f"访问失败: {e}")


def demo_compliance():
    """演示合规性管理"""
    print("\n=== 合规性管理演示 ===")
    
    compliance_manager = ComplianceManager()
    
    # 获取GDPR信息
    gdpr_info = compliance_manager.get_regulation_info("GDPR")
    print(f"GDPR: {gdpr_info['name']}")
    print(f"要求数量: {len(gdpr_info['requirements'])}")
    
    # 测试元数据
    test_metadata = {
        "retention_policy": {"retention_days": 1825},  # 5年
        "classification": {
            "sensitivity": "confidential",
            "personal_data": True,
            "category": "customer_pii"
        },
        "access_control": {
            "allowed_roles": ["steward", "admin"],
            "approval_required": True
        },
        "audit_requirements": {
            "log_access": True,
            "log_changes": True,
            "retention_days": 2555
        }
    }
    
    # 检查合规性
    compliance_results = compliance_manager.check_compliance(test_metadata, ["GDPR", "CCPA"])
    
    # 生成合规报告
    report = compliance_manager.generate_compliance_report(compliance_results)
    print(f"\n合规状态: {report['summary']['overall_status']}")
    print(f"检查的法规数量: {report['summary']['total_regulations']}")
    
    for regulation, details in report["details"].items():
        print(f"\n{regulation}: {details['status']}")
        print(f"通过检查: {details['passed_checks']}/{details['total_checks']}")
        
        for check_name, result in details["checks"].items():
            status_icon = "✓" if result["passed"] else "✗"
            print(f"  {status_icon} {check_name}: {result['message']}")


def main():
    """主函数，运行所有演示"""
    demo_governance_strategy()
    demo_organization()
    demo_lifecycle()
    demo_version_management()
    demo_security()
    demo_compliance()


if __name__ == "__main__":
    main()