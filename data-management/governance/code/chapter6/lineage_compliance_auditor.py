#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
血缘合规性审计工具
功能：检查数据血缘的合规性，生成审计报告和建议
作者：数据治理团队
日期：2023-11-23
"""

import json
import datetime
import uuid
import re
from typing import Dict, List, Tuple, Any, Optional, Set
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class LineageComplianceAuditor:
    """血缘合规性审计器"""
    
    def __init__(self, lineage_graph=None, compliance_rules=None):
        """初始化血缘合规性审计器"""
        self.lineage_graph = lineage_graph if lineage_graph is not nx.DiGraph() else nx.DiGraph()
        
        # 加载默认合规规则
        self.compliance_rules = compliance_rules if compliance_rules else self._load_default_rules()
        
        # 审计日志
        self.audit_logs = []
    
    def _load_default_rules(self):
        """加载默认合规规则"""
        return {
            "completeness": {
                "description": "数据血缘完整性检查",
                "enabled": True,
                "severity": "高",
                "check_function": self._check_lineage_completeness,
                "params": {
                    "min_upstream_dependencies": 1,
                    "min_downstream_dependencies": 1,
                    "exclude_systems": ["sandbox", "development"]
                }
            },
            "documentation": {
                "description": "数据血缘文档化检查",
                "enabled": True,
                "severity": "中",
                "check_function": self._check_lineage_documentation,
                "params": {
                    "require_description": True,
                    "require_owner": True,
                    "require_tags": False
                }
            },
            "sensitive_data": {
                "description": "敏感数据处理检查",
                "enabled": True,
                "severity": "高",
                "check_function": self._check_sensitive_data_handling,
                "params": {
                    "sensitive_keywords": ["ssn", "password", "credit_card", "pii", "personal"],
                    "require_encryption": True,
                    "require_access_log": True
                }
            },
            "approval_process": {
                "description": "血缘关系审批流程检查",
                "enabled": True,
                "severity": "中",
                "check_function": self._check_approval_process,
                "params": {
                    "require_approval_for_production": True,
                    "require_approval_for_sensitive_data": True,
                    "approval_window_days": 90
                }
            },
            "data_retention": {
                "description": "数据保留政策检查",
                "enabled": True,
                "severity": "中",
                "check_function": self._check_data_retention,
                "params": {
                    "max_retention_days": {
                        "pii": 2555,  # 7年
                        "financial": 2555,  # 7年
                        "general": 1095  # 3年
                    }
                }
            },
            "access_control": {
                "description": "访问控制检查",
                "enabled": True,
                "severity": "高",
                "check_function": self._check_access_control,
                "params": {
                    "require_role_based_access": True,
                    "require_audit_log": True,
                    "public_systems": ["reporting", "dashboard"]
                }
            }
        }
    
    def add_compliance_rule(self, rule_name, rule_config):
        """添加自定义合规规则"""
        self.compliance_rules[rule_name] = rule_config
    
    def remove_compliance_rule(self, rule_name):
        """移除合规规则"""
        if rule_name in self.compliance_rules:
            del self.compliance_rules[rule_name]
            return True
        return False
    
    def enable_rule(self, rule_name):
        """启用合规规则"""
        if rule_name in self.compliance_rules:
            self.compliance_rules[rule_name]["enabled"] = True
            return True
        return False
    
    def disable_rule(self, rule_name):
        """禁用合规规则"""
        if rule_name in self.compliance_rules:
            self.compliance_rules[rule_name]["enabled"] = False
            return True
        return False
    
    def run_compliance_audit(self, scope="all", custom_rules=None):
        """运行合规性审计"""
        audit_id = str(uuid.uuid4())
        audit_start_time = datetime.datetime.now()
        
        # 获取审计范围内的对象
        if scope == "all":
            audit_objects = list(self.lineage_graph.nodes())
        elif isinstance(scope, list):
            audit_objects = scope
        else:
            # 假设scope是系统名或对象类型
            audit_objects = [
                node_id for node_id, node_data in self.lineage_graph.nodes(data=True)
                if node_data.get("system_name") == scope or node_data.get("object_type") == scope
            ]
        
        # 使用自定义规则或默认规则
        rules_to_check = custom_rules if custom_rules else self.compliance_rules
        
        # 初始化审计结果
        audit_results = {
            "audit_id": audit_id,
            "start_time": audit_start_time.isoformat(),
            "end_time": None,
            "scope": scope,
            "objects_audited": len(audit_objects),
            "rules_checked": len([rule for rule in rules_to_check.values() if rule["enabled"]]),
            "overall_compliance_score": 0,
            "violations": {},
            "rule_results": {},
            "recommendations": [],
            "summary": {}
        }
        
        total_violations = 0
        total_possible_violations = 0
        
        # 运行每个合规规则检查
        for rule_name, rule_config in rules_to_check.items():
            if not rule_config.get("enabled", True):
                continue
            
            # 运行规则检查
            try:
                rule_result = rule_config["check_function"](audit_objects, rule_config.get("params", {}))
                
                # 统计违规数量
                violations_count = len(rule_result.get("violations", []))
                total_violations += violations_count
                total_possible_violations += len(audit_objects)  # 每个对象最多一个违规
                
                # 记录规则结果
                audit_results["rule_results"][rule_name] = {
                    "description": rule_config["description"],
                    "severity": rule_config["severity"],
                    "violations_count": violations_count,
                    "violations": rule_result.get("violations", []),
                    "compliance_rate": 1.0 - (violations_count / len(audit_objects)) if audit_objects else 1.0
                }
                
                # 收集所有违规
                if violations_count > 0:
                    audit_results["violations"][rule_name] = rule_result.get("violations", [])
                
                # 记录审计日志
                self._log_audit_event(
                    "rule_check",
                    rule_name,
                    "success" if violations_count == 0 else "violations_detected",
                    f"检查了{len(audit_objects)}个对象，发现{violations_count}个违规"
                )
                
            except Exception as e:
                # 记录规则检查错误
                audit_results["rule_results"][rule_name] = {
                    "description": rule_config["description"],
                    "severity": rule_config["severity"],
                    "error": str(e),
                    "compliance_rate": 0
                }
                
                self._log_audit_event(
                    "rule_check",
                    rule_name,
                    "error",
                    str(e)
                )
                
                # 将错误计入违规
                total_violations += len(audit_objects)
                total_possible_violations += len(audit_objects)
        
        # 计算总体合规分数
        if total_possible_violations > 0:
            audit_results["overall_compliance_score"] = max(0, 1.0 - (total_violations / total_possible_violations))
        
        # 生成建议
        audit_results["recommendations"] = self._generate_audit_recommendations(audit_results)
        
        # 生成摘要
        audit_results["summary"] = {
            "total_objects": len(audit_objects),
            "total_violations": total_violations,
            "compliance_level": self._get_compliance_level(audit_results["overall_compliance_score"]),
            "high_severity_violations": sum(
                len(result.get("violations", []))
                for result in audit_results["rule_results"].values()
                if result.get("severity") == "高"
            ),
            "rules_with_violations": len([
                rule_name for rule_name, result in audit_results["rule_results"].items()
                if result.get("violations_count", 0) > 0
            ])
        }
        
        audit_results["end_time"] = datetime.datetime.now().isoformat()
        
        # 记录审计完成
        self._log_audit_event(
            "audit_completion",
            audit_id,
            "success",
            f"审计完成，合规分数: {audit_results['overall_compliance_score']:.2f}"
        )
        
        return audit_results
    
    def _check_lineage_completeness(self, audit_objects, params):
        """检查血缘完整性"""
        violations = []
        
        min_upstream = params.get("min_upstream_dependencies", 1)
        min_downstream = params.get("min_downstream_dependencies", 1)
        exclude_systems = params.get("exclude_systems", [])
        
        for obj_id in audit_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            node_data = self.lineage_graph.nodes[obj_id]
            system_name = node_data.get("system_name", "unknown")
            
            # 跳过排除的系统
            if system_name in exclude_systems:
                continue
            
            # 检查上游依赖
            upstream_count = len(list(self.lineage_graph.predecessors(obj_id)))
            if upstream_count < min_upstream:
                violations.append({
                    "object_id": obj_id,
                    "object_name": node_data.get("name", obj_id),
                    "system": system_name,
                    "violation_type": "insufficient_upstream_dependencies",
                    "description": f"对象有{upstream_count}个上游依赖，少于要求的{min_upstream}个",
                    "severity": "高"
                })
            
            # 检查下游依赖
            downstream_count = len(list(self.lineage_graph.successors(obj_id)))
            if downstream_count < min_downstream:
                violations.append({
                    "object_id": obj_id,
                    "object_name": node_data.get("name", obj_id),
                    "system": system_name,
                    "violation_type": "insufficient_downstream_dependencies",
                    "description": f"对象有{downstream_count}个下游依赖，少于要求的{min_downstream}个",
                    "severity": "中"
                })
        
        return {"violations": violations}
    
    def _check_lineage_documentation(self, audit_objects, params):
        """检查血缘文档化"""
        violations = []
        
        require_description = params.get("require_description", True)
        require_owner = params.get("require_owner", True)
        require_tags = params.get("require_tags", False)
        
        for obj_id in audit_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            node_data = self.lineage_graph.nodes[obj_id]
            object_name = node_data.get("name", obj_id)
            
            # 检查描述
            if require_description:
                description = node_data.get("description", "")
                if not description or len(description.strip()) < 10:
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "violation_type": "missing_description",
                        "description": "数据对象缺少详细描述（至少10个字符）",
                        "severity": "中"
                    })
            
            # 检查所有者
            if require_owner:
                owner = node_data.get("owner", "")
                if not owner:
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "violation_type": "missing_owner",
                        "description": "数据对象缺少所有者信息",
                        "severity": "中"
                    })
            
            # 检查标签
            if require_tags:
                tags = node_data.get("tags", [])
                if not tags:
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "violation_type": "missing_tags",
                        "description": "数据对象缺少标签",
                        "severity": "低"
                    })
        
        return {"violations": violations}
    
    def _check_sensitive_data_handling(self, audit_objects, params):
        """检查敏感数据处理"""
        violations = []
        
        sensitive_keywords = params.get("sensitive_keywords", [])
        require_encryption = params.get("require_encryption", True)
        require_access_log = params.get("require_access_log", True)
        
        for obj_id in audit_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            node_data = self.lineage_graph.nodes[obj_id]
            object_name = node_data.get("name", obj_id)
            
            # 检查是否包含敏感数据
            has_sensitive_data = False
            
            # 检查名称中是否包含敏感关键词
            name_lower = object_name.lower()
            if any(keyword in name_lower for keyword in sensitive_keywords):
                has_sensitive_data = True
            
            # 检查描述中是否包含敏感关键词
            description = node_data.get("description", "").lower()
            if any(keyword in description for keyword in sensitive_keywords):
                has_sensitive_data = True
            
            # 检查属性中是否标记为敏感
            properties = node_data.get("properties", {})
            if properties.get("sensitive", False) or properties.get("contains_pii", False):
                has_sensitive_data = True
            
            if has_sensitive_data:
                # 检查加密
                if require_encryption and not properties.get("encrypted", False):
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "violation_type": "sensitive_data_not_encrypted",
                        "description": "包含敏感数据但未加密",
                        "severity": "高"
                    })
                
                # 检查访问日志
                if require_access_log and not properties.get("access_log_enabled", False):
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "violation_type": "sensitive_data_no_access_log",
                        "description": "包含敏感数据但未启用访问日志",
                        "severity": "中"
                    })
                
                # 检查适当的权限控制
                if not properties.get("restricted_access", False):
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "violation_type": "sensitive_data_no_restricted_access",
                        "description": "包含敏感数据但未限制访问权限",
                        "severity": "高"
                    })
        
        return {"violations": violations}
    
    def _check_approval_process(self, audit_objects, params):
        """检查审批流程"""
        violations = []
        
        require_approval_for_production = params.get("require_approval_for_production", True)
        require_approval_for_sensitive_data = params.get("require_approval_for_sensitive_data", True)
        approval_window_days = params.get("approval_window_days", 90)
        
        for obj_id in audit_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            node_data = self.lineage_graph.nodes[obj_id]
            object_name = node_data.get("name", obj_id)
            system_name = node_data.get("system_name", "unknown")
            
            # 检查生产环境对象的审批
            if require_approval_for_production and system_name == "production":
                approval_info = node_data.get("approval", {})
                if not approval_info.get("approved", False):
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "system": system_name,
                        "violation_type": "production_object_not_approved",
                        "description": "生产环境对象未经审批",
                        "severity": "高"
                    })
                else:
                    # 检查审批是否过期
                    approval_date_str = approval_info.get("approval_date")
                    if approval_date_str:
                        try:
                            approval_date = datetime.datetime.strptime(approval_date_str, "%Y-%m-%d")
                            days_since_approval = (datetime.datetime.now() - approval_date).days
                            
                            if days_since_approval > approval_window_days:
                                violations.append({
                                    "object_id": obj_id,
                                    "object_name": object_name,
                                    "system": system_name,
                                    "violation_type": "production_object_approval_expired",
                                    "description": f"生产环境对象审批已过期（{days_since_approval}天）",
                                    "severity": "中"
                                })
                        except ValueError:
                            violations.append({
                                "object_id": obj_id,
                                "object_name": object_name,
                                "system": system_name,
                                "violation_type": "invalid_approval_date",
                                "description": "审批日期格式无效",
                                "severity": "中"
                            })
            
            # 检查敏感数据对象的审批
            if require_approval_for_sensitive_data:
                properties = node_data.get("properties", {})
                is_sensitive = (
                    properties.get("sensitive", False) or 
                    properties.get("contains_pii", False)
                )
                
                if is_sensitive:
                    approval_info = node_data.get("approval", {})
                    if not approval_info.get("approved", False):
                        violations.append({
                            "object_id": obj_id,
                            "object_name": object_name,
                            "violation_type": "sensitive_data_not_approved",
                            "description": "包含敏感数据的对象未经审批",
                            "severity": "高"
                        })
        
        # 检查血缘关系的审批
        for source_id, target_id, edge_data in self.lineage_graph.edges(data=True):
            if source_id in audit_objects and target_id in audit_objects:
                transformation_type = edge_data.get("transformation_type", "unknown")
                
                # 检查转换的审批
                approval_info = edge_data.get("approval", {})
                if not approval_info.get("approved", False):
                    violations.append({
                        "source_object_id": source_id,
                        "target_object_id": target_id,
                        "transformation_type": transformation_type,
                        "violation_type": "transformation_not_approved",
                        "description": f"数据转换 {transformation_type} 未经审批",
                        "severity": "中"
                    })
        
        return {"violations": violations}
    
    def _check_data_retention(self, audit_objects, params):
        """检查数据保留政策"""
        violations = []
        
        max_retention_days = params.get("max_retention_days", {})
        
        for obj_id in audit_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            node_data = self.lineage_graph.nodes[obj_id]
            object_name = node_data.get("name", obj_id)
            object_type = node_data.get("object_type", "unknown")
            
            # 获取创建日期
            created_date_str = node_data.get("created_date")
            if not created_date_str:
                continue
            
            try:
                created_date = datetime.datetime.strptime(created_date_str, "%Y-%m-%d")
                days_since_creation = (datetime.datetime.now() - created_date).days
                
                # 确定保留期限
                properties = node_data.get("properties", {})
                data_category = properties.get("data_category", "general")
                
                if data_category in max_retention_days:
                    max_days = max_retention_days[data_category]
                    
                    if days_since_creation > max_days:
                        violations.append({
                            "object_id": obj_id,
                            "object_name": object_name,
                            "data_category": data_category,
                            "violation_type": "data_retention_exceeded",
                            "description": f"数据保留期限超过政策（{days_since_creation}天 > {max_days}天）",
                            "severity": "中"
                        })
                
            except ValueError:
                violations.append({
                    "object_id": obj_id,
                    "object_name": object_name,
                    "violation_type": "invalid_created_date",
                    "description": "创建日期格式无效",
                    "severity": "低"
                })
        
        return {"violations": violations}
    
    def _check_access_control(self, audit_objects, params):
        """检查访问控制"""
        violations = []
        
        require_role_based_access = params.get("require_role_based_access", True)
        require_audit_log = params.get("require_audit_log", True)
        public_systems = params.get("public_systems", [])
        
        for obj_id in audit_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            node_data = self.lineage_graph.nodes[obj_id]
            object_name = node_data.get("name", obj_id)
            system_name = node_data.get("system_name", "unknown")
            
            # 检查基于角色的访问控制
            if require_role_based_access and system_name not in public_systems:
                access_control = node_data.get("access_control", {})
                
                if not access_control.get("role_based", False):
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "system": system_name,
                        "violation_type": "no_role_based_access",
                        "description": "未实施基于角色的访问控制",
                        "severity": "高"
                    })
                else:
                    # 检查是否有定义的角色
                    roles = access_control.get("roles", [])
                    if not roles:
                        violations.append({
                            "object_id": obj_id,
                            "object_name": object_name,
                            "system": system_name,
                            "violation_type": "no_defined_roles",
                            "description": "启用了基于角色的访问控制但未定义角色",
                            "severity": "中"
                        })
            
            # 检查审计日志
            if require_audit_log:
                properties = node_data.get("properties", {})
                
                if not properties.get("audit_log_enabled", False):
                    violations.append({
                        "object_id": obj_id,
                        "object_name": object_name,
                        "system": system_name,
                        "violation_type": "no_audit_log",
                        "description": "未启用访问审计日志",
                        "severity": "中"
                    })
        
        return {"violations": violations}
    
    def _get_compliance_level(self, compliance_score):
        """根据合规分数确定合规级别"""
        if compliance_score >= 0.95:
            return "优秀"
        elif compliance_score >= 0.85:
            return "良好"
        elif compliance_score >= 0.7:
            return "一般"
        elif compliance_score >= 0.5:
            return "较差"
        else:
            return "不合格"
    
    def _generate_audit_recommendations(self, audit_results):
        """生成审计建议"""
        recommendations = []
        
        # 基于总体合规分数的建议
        compliance_score = audit_results["overall_compliance_score"]
        
        if compliance_score < 0.7:
            recommendations.append({
                "priority": "高",
                "category": "整体改进",
                "description": "合规分数低于70%，建议制定全面的改进计划",
                "action_items": [
                    "成立数据治理改进工作组",
                    "制定短期和长期改进目标",
                    "分配足够的资源和预算",
                    "定期跟踪改进进展"
                ]
            })
        elif compliance_score < 0.85:
            recommendations.append({
                "priority": "中",
                "category": "持续改进",
                "description": "合规分数在70%-85%之间，建议持续改进",
                "action_items": [
                    "关注主要违规领域",
                    "实施预防性措施",
                    "加强培训和意识",
                    "定期审查合规性"
                ]
            })
        
        # 基于具体规则违规的建议
        for rule_name, rule_result in audit_results["rule_results"].items():
            if rule_result.get("violations_count", 0) > 0:
                # 为每个违规规则生成特定建议
                rule_recommendations = self._generate_rule_recommendations(rule_name, rule_result)
                recommendations.extend(rule_recommendations)
        
        # 去重并按优先级排序
        unique_recommendations = {}
        for rec in recommendations:
            rec_key = f"{rec['category']}_{rec['description']}"
            if rec_key not in unique_recommendations:
                unique_recommendations[rec_key] = rec
        
        # 转换为列表并按优先级排序
        result = list(unique_recommendations.values())
        priority_order = {"高": 1, "中": 2, "低": 3}
        result.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return result
    
    def _generate_rule_recommendations(self, rule_name, rule_result):
        """为特定规则生成建议"""
        recommendations = []
        
        if rule_name == "completeness":
            recommendations.append({
                "priority": "高",
                "category": "血缘完整性",
                "description": "提高数据血缘的完整性和覆盖范围",
                "action_items": [
                    "实施自动化血缘捕获工具",
                    "建立血缘数据质量检查机制",
                    "定期审查血缘覆盖率",
                    "为缺失血缘关系的对象补充关系"
                ]
            })
        
        elif rule_name == "documentation":
            recommendations.append({
                "priority": "中",
                "category": "血缘文档化",
                "description": "改善数据血缘的文档化程度",
                "action_items": [
                    "为所有数据对象添加描述",
                    "指定数据所有者和负责人",
                    "实施标签和分类体系",
                    "定期更新和维护文档"
                ]
            })
        
        elif rule_name == "sensitive_data":
            recommendations.append({
                "priority": "高",
                "category": "敏感数据管理",
                "description": "加强敏感数据的识别、保护和管理",
                "action_items": [
                    "实施敏感数据自动识别",
                    "确保敏感数据加密存储",
                    "启用敏感数据访问日志",
                    "限制敏感数据访问权限"
                ]
            })
        
        elif rule_name == "approval_process":
            recommendations.append({
                "priority": "中",
                "category": "审批流程",
                "description": "完善数据血缘关系的审批流程",
                "action_items": [
                    "建立数据变更审批工作流",
                    "定期审查和更新审批状态",
                    "为生产环境强制要求审批",
                    "为敏感数据实施额外审批"
                ]
            })
        
        elif rule_name == "data_retention":
            recommendations.append({
                "priority": "中",
                "category": "数据保留",
                "description": "确保数据保留政策得到执行",
                "action_items": [
                    "实施数据保留策略监控",
                    "定期审查数据保留期限",
                    "自动化过期数据归档和删除",
                    "制定特殊数据的保留例外政策"
                ]
            })
        
        elif rule_name == "access_control":
            recommendations.append({
                "priority": "高",
                "category": "访问控制",
                "description": "强化数据访问控制和审计",
                "action_items": [
                    "实施基于角色的访问控制",
                    "定期审查访问权限设置",
                    "启用访问行为审计日志",
                    "实施访问异常检测和响应"
                ]
            })
        
        return recommendations
    
    def _log_audit_event(self, event_type, target, status, details):
        """记录审计事件"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "target": target,
            "status": status,
            "details": details
        }
        
        self.audit_logs.append(log_entry)
    
    def get_compliance_trends(self, audits=None):
        """获取合规趋势分析"""
        if audits is None:
            audits = self.audit_logs
        
        # 筛选审计完成事件
        audit_completion_logs = [
            log for log in audits 
            if log["event_type"] == "audit_completion"
        ]
        
        # 如果没有足够的审计历史，返回空结果
        if len(audit_completion_logs) < 2:
            return {
                "trend": "insufficient_data",
                "message": "需要至少两次审计结果来分析趋势",
                "data_points": len(audit_completion_logs)
            }
        
        # 解析合规分数
        compliance_scores = []
        audit_dates = []
        
        for log in audit_completion_logs:
            # 从详情中提取合规分数
            details = log["details"]
            match = re.search(r'合规分数: (\d+\.\d+)', details)
            if match:
                score = float(match.group(1))
                compliance_scores.append(score)
                audit_dates.append(log["timestamp"])
        
        if len(compliance_scores) < 2:
            return {
                "trend": "insufficient_data",
                "message": "解析出的合规分数不足以分析趋势",
                "data_points": len(compliance_scores)
            }
        
        # 计算趋势
        if len(compliance_scores) >= 3:
            # 如果有3个或更多数据点，计算线性趋势
            recent_scores = compliance_scores[-3:]
            
            # 简单线性趋势计算
            x = list(range(len(recent_scores)))
            y = recent_scores
            
            # 计算斜率
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            if n * sum_x2 - sum_x ** 2 != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
                
                if slope > 0.01:
                    trend = "improving"
                    message = "合规性呈上升趋势"
                elif slope < -0.01:
                    trend = "declining"
                    message = "合规性呈下降趋势"
                else:
                    trend = "stable"
                    message = "合规性保持稳定"
            else:
                trend = "stable"
                message = "合规性保持稳定"
        else:
            # 只有两个数据点，简单比较
            if compliance_scores[-1] > compliance_scores[-2]:
                trend = "improving"
                message = "最新合规分数较上次有所提高"
            elif compliance_scores[-1] < compliance_scores[-2]:
                trend = "declining"
                message = "最新合规分数较上次有所下降"
            else:
                trend = "stable"
                message = "最新合规分数与上次持平"
        
        return {
            "trend": trend,
            "message": message,
            "current_score": compliance_scores[-1],
            "previous_score": compliance_scores[-2],
            "score_change": compliance_scores[-1] - compliance_scores[-2],
            "audit_dates": audit_dates,
            "compliance_scores": compliance_scores
        }
    
    def visualize_compliance_results(self, audit_results, output_file="compliance_audit.png"):
        """可视化合规审计结果"""
        plt.figure(figsize=(15, 10))
        
        # 1. 总体合规分数
        plt.subplot(2, 2, 1)
        score = audit_results["overall_compliance_score"]
        level = self._get_compliance_level(score)
        
        # 创建彩色背景
        if level == "优秀":
            color = 'green'
        elif level == "良好":
            color = 'lightgreen'
        elif level == "一般":
            color = 'yellow'
        elif level == "较差":
            color = 'orange'
        else:
            color = 'red'
        
        plt.bar(["总体合规分数"], [score * 100], color=color)
        plt.ylim(0, 100)
        plt.title(f"总体合规分数: {score*100:.1f}% ({level})")
        plt.ylabel("分数 (%)")
        
        # 2. 各规则合规率
        plt.subplot(2, 2, 2)
        rule_names = []
        compliance_rates = []
        
        for rule_name, rule_result in audit_results["rule_results"].items():
            rule_names.append(rule_name)
            compliance_rates.append(rule_result.get("compliance_rate", 0) * 100)
        
        # 截断长规则名
        rule_names_display = [name[:10] + "..." if len(name) > 10 else name for name in rule_names]
        
        plt.barh(rule_names_display, compliance_rates, color='skyblue')
        plt.xlim(0, 100)
        plt.title("各规则合规率")
        plt.xlabel("合规率 (%)")
        
        # 3. 严重程度分布
        plt.subplot(2, 2, 3)
        severity_counts = {"高": 0, "中": 0, "低": 0}
        
        for rule_name, rule_result in audit_results["rule_results"].items():
            severity = rule_result.get("severity", "中")
            violations_count = rule_result.get("violations_count", 0)
            severity_counts[severity] += violations_count
        
        labels = list(severity_counts.keys())
        sizes = list(severity_counts.values())
        colors = ['red', 'orange', 'yellow']
        
        if sum(sizes) > 0:
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        else:
            plt.text(0.5, 0.5, '无违规', ha='center', va='center', transform=plt.gca().transAxes)
        
        plt.title("违规严重程度分布")
        
        # 4. 合规趋势（如果有历史数据）
        plt.subplot(2, 2, 4)
        trends = self.get_compliance_trends()
        
        if "compliance_scores" in trends and len(trends["compliance_scores"]) > 1:
            scores = trends["compliance_scores"]
            x = list(range(len(scores)))
            plt.plot(x, scores, marker='o', linestyle='-', color='blue')
            plt.xticks(x, [f"审计{i+1}" for i in x])
            plt.ylim(0, 1)
            plt.title("合规分数趋势")
            plt.ylabel("合规分数")
            
            # 添加趋势线
            if len(scores) >= 3:
                z = np.polyfit(x, scores, 1)
                p = np.poly1d(z)
                plt.plot(x, p(x), "r--", alpha=0.7)
        else:
            plt.text(0.5, 0.5, '无历史数据', ha='center', va='center', transform=plt.gca().transAxes)
            plt.title("合规分数趋势")
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"合规审计图表已保存为 {output_file}"
    
    def generate_compliance_report(self, audit_results, output_file=None):
        """生成合规审计报告"""
        report = {
            "report_id": str(uuid.uuid4()),
            "report_type": "compliance_audit",
            "generated_at": datetime.datetime.now().isoformat(),
            "audit_id": audit_results["audit_id"],
            "executive_summary": {
                "overall_compliance_score": audit_results["overall_compliance_score"],
                "compliance_level": self._get_compliance_level(audit_results["overall_compliance_score"]),
                "total_violations": audit_results["summary"]["total_violations"],
                "high_severity_violations": audit_results["summary"]["high_severity_violations"],
                "rules_with_violations": audit_results["summary"]["rules_with_violations"]
            },
            "detailed_results": {
                "rule_results": audit_results["rule_results"],
                "violations_by_object": self._group_violations_by_object(audit_results["violations"])
            },
            "recommendations": audit_results["recommendations"],
            "trends_analysis": self.get_compliance_trends(),
            "appendix": {
                "audit_scope": audit_results["scope"],
                "objects_audited": audit_results["objects_audited"],
                "rules_checked": audit_results["rules_checked"],
                "audit_period": {
                    "start_time": audit_results["start_time"],
                    "end_time": audit_results["end_time"]
                }
            }
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            report["output_file"] = output_file
        
        return report
    
    def _group_violations_by_object(self, violations):
        """按对象分组违规"""
        violations_by_object = {}
        
        for rule_name, rule_violations in violations.items():
            for violation in rule_violations:
                object_id = violation.get("object_id", "unknown")
                
                if object_id not in violations_by_object:
                    violations_by_object[object_id] = {
                        "object_name": violation.get("object_name", object_id),
                        "system": violation.get("system", "unknown"),
                        "violations": []
                    }
                
                violations_by_object[object_id]["violations"].append({
                    "rule": rule_name,
                    "violation_type": violation.get("violation_type", "unknown"),
                    "description": violation.get("description", "N/A"),
                    "severity": violation.get("severity", "中")
                })
        
        return violations_by_object

def create_sample_lineage_graph():
    """创建示例血缘图"""
    graph = nx.DiGraph()
    
    # 添加数据对象
    objects = [
        {"id": "prod.customers", "name": "customers", "type": "table", "system": "production", 
         "description": "客户信息表", "owner": "数据团队", "created_date": "2020-01-15",
         "properties": {"sensitive": True, "encrypted": True, "access_log_enabled": True, "data_category": "pii"},
         "approval": {"approved": True, "approval_date": "2020-01-10"}},
        
        {"id": "prod.orders", "name": "orders", "type": "table", "system": "production", 
         "description": "订单信息表", "owner": "数据团队", "created_date": "2020-01-15",
         "properties": {"sensitive": False, "data_category": "general"},
         "approval": {"approved": True, "approval_date": "2020-01-10"}},
        
        {"id": "staging.customer_orders", "name": "customer_orders", "type": "table", "system": "staging", 
         "description": "客户订单汇总表", "owner": "ETL团队", "created_date": "2021-03-20",
         "properties": {"data_category": "general"},
         "approval": {"approved": True, "approval_date": "2021-03-15"}},
        
        {"id": "dw.sales_summary", "name": "sales_summary", "type": "view", "system": "analytics", 
         "description": "销售汇总视图", "owner": "分析团队", "created_date": "2021-06-10",
         "properties": {"data_category": "general"},
         "access_control": {"role_based": True, "roles": ["analyst", "manager"]}},
        
        {"id": "reports.monthly_report", "name": "monthly_report", "type": "report", "system": "reporting", 
         "description": "月度销售报告", "owner": "报表团队", "created_date": "2022-01-05",
         "properties": {"data_category": "general"}},
        
        {"id": "dev.test_table", "name": "test_table", "type": "table", "system": "development", 
         "description": "", "owner": "开发团队", "created_date": "2022-03-01",
         "properties": {"data_category": "general"}},
         
        {"id": "prod.sensitive_data", "name": "sensitive_data", "type": "table", "system": "production", 
         "description": "敏感数据表", "owner": "数据团队", "created_date": "2019-06-15",
         "properties": {"sensitive": True, "contains_pii": True, "data_category": "pii"},
         "approval": {"approved": False}},
         
        {"id": "prod.legacy_table", "name": "legacy_table", "type": "table", "system": "production", 
         "description": "遗留系统数据表", "owner": "维护团队", "created_date": "2018-01-01",
         "properties": {"data_category": "financial"},
         "approval": {"approved": True, "approval_date": "2017-12-20"}}
    ]
    
    for obj in objects:
        graph.add_node(
            obj["id"],
            name=obj["name"],
            object_type=obj["type"],
            system_name=obj["system"],
            description=obj["description"],
            owner=obj["owner"],
            created_date=obj["created_date"],
            properties=obj.get("properties", {}),
            access_control=obj.get("access_control", {}),
            approval=obj.get("approval", {})
        )
    
    # 添加血缘关系
    relationships = [
        {"source": "prod.customers", "target": "staging.customer_orders", "type": "etl", 
         "approval": {"approved": True, "approval_date": "2021-03-15"}},
        {"source": "prod.orders", "target": "staging.customer_orders", "type": "etl", 
         "approval": {"approved": True, "approval_date": "2021-03-15"}},
        {"source": "staging.customer_orders", "target": "dw.sales_summary", "type": "aggregation"},
        {"source": "dw.sales_summary", "target": "reports.monthly_report", "type": "reporting"},
        {"source": "prod.customers", "target": "dw.sales_summary", "type": "direct_query"}
    ]
    
    for rel in relationships:
        graph.add_edge(
            rel["source"],
            rel["target"],
            transformation_type=rel["type"],
            approval=rel.get("approval", {})
        )
    
    return graph

def main():
    """主函数"""
    print("=" * 50)
    print("血缘合规性审计工具")
    print("=" * 50)
    
    # 创建示例血缘图
    print("创建示例血缘图...")
    lineage_graph = create_sample_lineage_graph()
    
    # 创建合规性审计器
    auditor = LineageComplianceAuditor(lineage_graph)
    
    print(f"血缘图包含 {lineage_graph.number_of_nodes()} 个节点和 {lineage_graph.number_of_edges()} 条边")
    
    # 运行合规性审计
    print("\n运行合规性审计...")
    audit_results = auditor.run_compliance_audit(scope="all")
    
    # 显示审计摘要
    print(f"\n审计摘要:")
    print(f"- 审计ID: {audit_results['audit_id']}")
    print(f"- 审计对象数: {audit_results['objects_audited']}")
    print(f"- 检查规则数: {audit_results['rules_checked']}")
    print(f"- 总体合规分数: {audit_results['overall_compliance_score']:.2f}")
    print(f"- 合规级别: {audit_results['summary']['compliance_level']}")
    print(f"- 总违规数: {audit_results['summary']['total_violations']}")
    print(f"- 高严重性违规数: {audit_results['summary']['high_severity_violations']}")
    print(f"- 有违规的规则数: {audit_results['summary']['rules_with_violations']}")
    
    # 显示各规则的结果
    print("\n各规则检查结果:")
    for rule_name, rule_result in audit_results["rule_results"].items():
        if "error" in rule_result:
            print(f"- {rule_name}: 错误 - {rule_result['error']}")
        else:
            print(f"- {rule_name}: {rule_result['violations_count']} 个违规, 合规率: {rule_result['compliance_rate']:.2f}")
            
            # 显示部分违规详情
            if rule_result.get("violations"):
                print("  部分违规:")
                for violation in rule_result["violations"][:2]:  # 只显示前2个
                    print(f"    - {violation.get('object_name', 'unknown')}: {violation.get('description', 'N/A')}")
    
    # 显示推荐措施
    print("\n推荐措施 (前5条):")
    for i, rec in enumerate(audit_results["recommendations"][:5]):
        print(f"{i+1}. [{rec['priority']}] {rec['category']}: {rec['description']}")
        print("   措施:")
        for action in rec["action_items"][:2]:  # 只显示前2个措施
            print(f"     - {action}")
    
    # 可视化审计结果
    print("\n生成审计结果可视化...")
    viz_result = auditor.visualize_compliance_audit_results(audit_results, "compliance_audit_results.png")
    print(viz_result)
    
    # 生成合规报告
    print("\n生成合规审计报告...")
    report = auditor.generate_compliance_report(audit_results, "compliance_audit_report.json")
    print("报告已生成")
    
    # 分析合规趋势
    print("\n分析合规趋势...")
    trends = auditor.get_compliance_trends()
    print(f"趋势: {trends['trend']} - {trends['message']}")
    if "current_score" in trends:
        print(f"当前分数: {trends['current_score']:.2f}")
        print(f"上次分数: {trends['previous_score']:.2f}")
        print(f"分数变化: {trends['score_change']:+.2f}")
    
    # 自定义审计 - 只审计生产环境
    print("\n运行自定义审计 - 只审计生产环境...")
    custom_audit_results = auditor.run_compliance_audit(scope="production")
    
    print(f"生产环境审计结果:")
    print(f"- 审计对象数: {custom_audit_results['objects_audited']}")
    print(f"- 总体合规分数: {custom_audit_results['overall_compliance_score']:.2f}")
    print(f"- 违规数: {custom_audit_results['summary']['total_violations']}")
    
    print("\n分析完成!")

if __name__ == "__main__":
    import numpy as np  # 用于趋势分析
    main()