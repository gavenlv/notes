#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第8章：元数据质量与评估 代码示例
本文件包含元数据质量与评估的实用代码示例，可直接运行
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# ====================
# 8.1 元数据质量框架
# ====================

class MetadataQualityFramework:
    """
    元数据质量框架
    提供元数据质量评估的全面框架
    """
    
    def __init__(self):
        self.quality_dimensions = {
            "accuracy": {
                "name": "准确性",
                "description": "元数据内容与实际情况一致的程度",
                "weight": 0.25,
                "metrics": [
                    {
                        "name": "description_accuracy",
                        "description": "描述准确性",
                        "type": "percentage",
                        "target": 0.95
                    },
                    {
                        "name": "schema_accuracy",
                        "description": "结构准确性",
                        "type": "percentage",
                        "target": 0.98
                    }
                ]
            },
            "completeness": {
                "name": "完整性",
                "description": "元数据覆盖数据资产的完整程度",
                "weight": 0.20,
                "metrics": [
                    {
                        "name": "required_fields_complete",
                        "description": "必填字段完整率",
                        "type": "percentage",
                        "target": 0.90
                    },
                    {
                        "name": "coverage",
                        "description": "资产覆盖率",
                        "type": "percentage",
                        "target": 0.85
                    }
                ]
            },
            "consistency": {
                "name": "一致性",
                "description": "元数据遵循标准规范的程度",
                "weight": 0.20,
                "metrics": [
                    {
                        "name": "naming_convention",
                        "description": "命名规范遵守率",
                        "type": "percentage",
                        "target": 0.90
                    },
                    {
                        "name": "format_consistency",
                        "description": "格式一致性",
                        "type": "percentage",
                        "target": 0.95
                    }
                ]
            },
            "timeliness": {
                "name": "时效性",
                "description": "元数据反映最新变化的速度",
                "weight": 0.15,
                "metrics": [
                    {
                        "name": "update_frequency",
                        "description": "更新频率",
                        "type": "frequency",
                        "target": "daily"
                    },
                    {
                        "name": "update_lag",
                        "description": "更新延迟",
                        "type": "duration",
                        "target": "1h"
                    }
                ]
            },
            "understandability": {
                "name": "可理解性",
                "description": "用户对元数据的理解程度",
                "weight": 0.10,
                "metrics": [
                    {
                        "name": "user_rating",
                        "description": "用户评分",
                        "type": "score",
                        "target": 4.0
                    },
                    {
                        "name": "clarity_score",
                        "description": "清晰度评分",
                        "type": "score",
                        "target": 4.0
                    }
                ]
            },
            "accessibility": {
                "name": "可访问性",
                "description": "获取元数据的难易程度",
                "weight": 0.10,
                "metrics": [
                    {
                        "name": "availability",
                        "description": "可用性",
                        "type": "percentage",
                        "target": 0.99
                    },
                    {
                        "name": "response_time",
                        "description": "响应时间",
                        "type": "duration",
                        "target": "500ms"
                    }
                ]
            }
        }
    
    def calculate_dimension_score(self, dimension_name, metric_scores):
        """计算维度得分"""
        if dimension_name not in self.quality_dimensions:
            return 0
        
        dimension = self.quality_dimensions[dimension_name]
        metrics = dimension["metrics"]
        
        total_weighted_score = 0
        total_weight = 0
        
        for metric in metrics:
            metric_name = metric["name"]
            if metric_name in metric_scores:
                score = metric_scores[metric_name]
                target = metric["target"]
                
                # 根据指标类型计算得分
                if metric["type"] == "percentage":
                    # 百分比指标：score/target
                    normalized_score = min(score / target, 1.0)
                elif metric["type"] == "score":
                    # 评分指标：score/max_score(5)
                    normalized_score = min(score / 5.0, 1.0)
                elif metric["type"] == "duration":
                    # 持续时间指标：target/score
                    normalized_score = min(target / score, 1.0) if score > 0 else 1.0
                elif metric["type"] == "frequency":
                    # 频率指标：需要转换为数值进行比较
                    score_value = self._frequency_to_value(score)
                    target_value = self._frequency_to_value(target)
                    normalized_score = min(score_value / target_value, 1.0)
                else:
                    normalized_score = 0
                
                total_weighted_score += normalized_score
                total_weight += 1
        
        return total_weighted_score / total_weight if total_weight > 0 else 0
    
    def _frequency_to_value(self, frequency):
        """将频率转换为数值"""
        frequency_values = {
            "real-time": 1000,
            "hourly": 24,
            "daily": 1,
            "weekly": 1/7,
            "monthly": 1/30,
            "quarterly": 1/90,
            "yearly": 1/365
        }
        return frequency_values.get(frequency.lower(), 0)
    
    def calculate_overall_score(self, dimension_scores):
        """计算总体质量得分"""
        total_weighted_score = 0
        total_weight = 0
        
        for dimension_name, dimension in self.quality_dimensions.items():
            weight = dimension["weight"]
            score = dimension_scores.get(dimension_name, 0)
            
            total_weighted_score += score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0
    
    def get_quality_level(self, score):
        """根据得分确定质量等级"""
        if score >= 0.9:
            return "优秀"
        elif score >= 0.8:
            return "良好"
        elif score >= 0.7:
            return "中等"
        elif score >= 0.6:
            return "及格"
        else:
            return "不合格"


# ====================
# 8.2 自动化质量检查器
# ====================

class MetadataQualityChecker:
    """
    元数据质量检查器
    提供自动化元数据质量检查功能
    """
    
    def __init__(self):
        self.check_rules = {
            "completeness": {
                "required_fields": [
                    "name",
                    "description",
                    "owner",
                    "schema"
                ],
                "check_function": self._check_completeness
            },
            "accuracy": {
                "patterns": {
                    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                    "url": r'^https?://.+',
                    "phone": r'^\+?[\d\s-]{10,}$'
                },
                "check_function": self._check_accuracy
            },
            "consistency": {
                "naming_conventions": {
                    "table": r'^tbl_[a-z_]+$',
                    "view": r'^vw_[a-z_]+$',
                    "column": r'^[a-z_]+$'
                },
                "check_function": self._check_consistency
            },
            "format": {
                "field_length_limits": {
                    "name": 100,
                    "description": 500
                },
                "check_function": self._check_format
            },
            "reference": {
                "check_function": self._check_references
            }
        }
        
        self.quality_issues = []
    
    def check_metadata(self, metadata_item):
        """检查单个元数据项的质量"""
        issues = []
        
        # 执行各类检查
        for rule_name, rule_config in self.check_rules.items():
            check_function = rule_config["check_function"]
            rule_issues = check_function(metadata_item, rule_config)
            issues.extend(rule_issues)
        
        return issues
    
    def _check_completeness(self, metadata_item, rule_config):
        """检查完整性"""
        issues = []
        required_fields = rule_config["required_fields"]
        
        for field in required_fields:
            if field not in metadata_item or not metadata_item[field]:
                issues.append({
                    "type": "completeness",
                    "severity": "high",
                    "field": field,
                    "message": f"必填字段 '{field}' 缺失或为空"
                })
        
        return issues
    
    def _check_accuracy(self, metadata_item, rule_config):
        """检查准确性"""
        issues = []
        patterns = rule_config["patterns"]
        
        # 检查字段值的格式
        for field_name, field_value in metadata_item.items():
            if not field_value or not isinstance(field_value, str):
                continue
                
            for pattern_name, pattern in patterns.items():
                if pattern_name in field_name.lower():
                    if not re.match(pattern, field_value):
                        issues.append({
                            "type": "accuracy",
                            "severity": "medium",
                            "field": field_name,
                            "message": f"字段 '{field_name}' 的值 '{field_value}' 不符合 {pattern_name} 格式要求"
                        })
        
        return issues
    
    def _check_consistency(self, metadata_item, rule_config):
        """检查一致性"""
        issues = []
        naming_conventions = rule_config["naming_conventions"]
        
        # 检查命名规范
        for convention_name, pattern in naming_conventions.items():
            field_name = None
            
            # 根据规范类型确定要检查的字段
            if convention_name == "table" and "table_name" in metadata_item:
                field_name = "table_name"
            elif convention_name == "view" and "view_name" in metadata_item:
                field_name = "view_name"
            elif convention_name == "column" and "column_name" in metadata_item:
                field_name = "column_name"
            elif "name" in metadata_item:  # 通用名称字段
                field_name = "name"
            
            if field_name and field_name in metadata_item:
                if not re.match(pattern, metadata_item[field_name]):
                    issues.append({
                        "type": "consistency",
                        "severity": "medium",
                        "field": field_name,
                        "message": f"字段 '{field_name}' 的命名不符合 {convention_name} 规范"
                    })
        
        return issues
    
    def _check_format(self, metadata_item, rule_config):
        """检查格式"""
        issues = []
        field_length_limits = rule_config["field_length_limits"]
        
        # 检查字段长度限制
        for field_name, max_length in field_length_limits.items():
            if field_name in metadata_item and metadata_item[field_name]:
                value_length = len(str(metadata_item[field_name]))
                if value_length > max_length:
                    issues.append({
                        "type": "format",
                        "severity": "low",
                        "field": field_name,
                        "message": f"字段 '{field_name}' 长度 {value_length} 超过限制 {max_length}"
                    })
        
        return issues
    
    def _check_references(self, metadata_item, rule_config):
        """检查引用有效性"""
        issues = []
        
        # 检查引用字段是否存在
        if "references" in metadata_item:
            for ref in metadata_item["references"]:
                if "ref_type" not in ref or "ref_id" not in ref:
                    issues.append({
                        "type": "reference",
                        "severity": "high",
                        "field": "references",
                        "message": "引用项缺少 ref_type 或 ref_id"
                    })
        
        return issues
    
    def batch_check(self, metadata_list):
        """批量检查元数据质量"""
        all_issues = []
        
        for metadata_item in metadata_list:
            item_id = metadata_item.get("id", "unknown")
            issues = self.check_metadata(metadata_item)
            
            # 添加项目ID到问题中
            for issue in issues:
                issue["metadata_id"] = item_id
            
            all_issues.extend(issues)
        
        return all_issues
    
    def generate_quality_report(self, metadata_list):
        """生成质量报告"""
        issues = self.batch_check(metadata_list)
        
        # 统计问题
        issue_stats = {
            "total": len(issues),
            "by_type": {},
            "by_severity": {
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "by_field": {}
        }
        
        for issue in issues:
            # 按类型统计
            issue_type = issue["type"]
            if issue_type not in issue_stats["by_type"]:
                issue_stats["by_type"][issue_type] = 0
            issue_stats["by_type"][issue_type] += 1
            
            # 按严重程度统计
            severity = issue["severity"]
            issue_stats["by_severity"][severity] += 1
            
            # 按字段统计
            field = issue["field"]
            if field not in issue_stats["by_field"]:
                issue_stats["by_field"][field] = 0
            issue_stats["by_field"][field] += 1
        
        # 计算质量得分
        total_items = len(metadata_list)
        items_with_issues = len(set(issue["metadata_id"] for issue in issues))
        
        quality_score = 0
        if total_items > 0:
            quality_score = max(0, 1.0 - (items_with_issues / total_items))
        
        return {
            "summary": {
                "total_items": total_items,
                "items_with_issues": items_with_issues,
                "total_issues": issue_stats["total"],
                "quality_score": quality_score,
                "quality_level": self._get_quality_level(quality_score)
            },
            "issue_statistics": issue_stats,
            "issues": issues
        }
    
    def _get_quality_level(self, score):
        """根据得分确定质量等级"""
        if score >= 0.95:
            return "优秀"
        elif score >= 0.85:
            return "良好"
        elif score >= 0.75:
            return "中等"
        elif score >= 0.65:
            return "及格"
        else:
            return "不合格"


# ====================
# 8.3 用户反馈系统
# ====================

class MetadataFeedbackSystem:
    """
    元数据反馈系统
    收集和管理用户对元数据的反馈
    """
    
    def __init__(self):
        self.feedback = {}  # metadata_id -> feedback list
        self.feedback_stats = {}  # 统计信息
        self.feedback_notifications = []  # 待处理的通知
    
    def add_feedback(self, metadata_id, user_id, feedback_type, rating, comment=""):
        """添加反馈"""
        if metadata_id not in self.feedback:
            self.feedback[metadata_id] = []
        
        feedback_item = {
            "id": len(self.feedback[metadata_id]) + 1,
            "user_id": user_id,
            "type": feedback_type,  # accuracy, completeness, usefulness, clarity
            "rating": rating,  # 1-5
            "comment": comment,
            "timestamp": datetime.now(),
            "status": "open"  # open, reviewed, resolved
        }
        
        self.feedback[metadata_id].append(feedback_item)
        
        # 更新统计信息
        self._update_stats(metadata_id)
        
        # 检查是否需要通知
        self._check_for_notification(metadata_id, feedback_item)
        
        return feedback_item
    
    def _update_stats(self, metadata_id):
        """更新统计信息"""
        if metadata_id not in self.feedback:
            return
        
        feedback_list = self.feedback[metadata_id]
        
        # 按类型分组
        type_stats = {}
        overall_ratings = []
        
        for item in feedback_list:
            feedback_type = item["type"]
            rating = item["rating"]
            
            if feedback_type not in type_stats:
                type_stats[feedback_type] = {
                    "count": 0,
                    "total_rating": 0,
                    "avg_rating": 0
                }
            
            type_stats[feedback_type]["count"] += 1
            type_stats[feedback_type]["total_rating"] += rating
            overall_ratings.append(rating)
        
        # 计算平均分
        for feedback_type, stats in type_stats.items():
            stats["avg_rating"] = stats["total_rating"] / stats["count"]
        
        # 计算总体平均分
        overall_avg = sum(overall_ratings) / len(overall_ratings) if overall_ratings else 0
        
        self.feedback_stats[metadata_id] = {
            "total_feedback": len(feedback_list),
            "type_stats": type_stats,
            "overall_avg_rating": overall_avg,
            "last_updated": datetime.now()
        }
    
    def _check_for_notification(self, metadata_id, feedback_item):
        """检查是否需要通知"""
        # 低评分反馈需要通知
        if feedback_item["rating"] <= 2:
            notification = {
                "metadata_id": metadata_id,
                "feedback_id": feedback_item["id"],
                "type": "low_rating",
                "message": f"元数据 {metadata_id} 收到低评分反馈 ({feedback_item['rating']}/5): {feedback_item['comment']}",
                "timestamp": datetime.now(),
                "status": "unread"
            }
            self.feedback_notifications.append(notification)
    
    def get_metadata_feedback(self, metadata_id):
        """获取元数据的所有反馈"""
        return self.feedback.get(metadata_id, [])
    
    def get_metadata_stats(self, metadata_id):
        """获取元数据的统计信息"""
        return self.feedback_stats.get(metadata_id, {})
    
    def get_all_notifications(self, status=None):
        """获取通知"""
        if status:
            return [n for n in self.feedback_notifications if n["status"] == status]
        return self.feedback_notifications
    
    def mark_notification_read(self, notification_id):
        """标记通知为已读"""
        for notification in self.feedback_notifications:
            if notification.get("id") == notification_id:
                notification["status"] = "read"
                return True
        return False
    
    def get_quality_trend(self, metadata_id, days=30):
        """获取质量趋势"""
        if metadata_id not in self.feedback:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = [
            f for f in self.feedback[metadata_id]
            if f["timestamp"] > cutoff_date
        ]
        
        if len(recent_feedback) < 2:
            return None
        
        # 按时间排序
        recent_feedback.sort(key=lambda x: x["timestamp"])
        
        # 计算趋势
        first_half = recent_feedback[:len(recent_feedback)//2]
        second_half = recent_feedback[len(recent_feedback)//2:]
        
        first_avg = sum(f["rating"] for f in first_half) / len(first_half)
        second_avg = sum(f["rating"] for f in second_half) / len(second_half)
        
        trend = "stable"
        if second_avg > first_avg + 0.5:
            trend = "improving"
        elif second_avg < first_avg - 0.5:
            trend = "declining"
        
        return {
            "metadata_id": metadata_id,
            "trend": trend,
            "change": second_avg - first_avg,
            "period_days": days,
            "data_points": len(recent_feedback)
        }
    
    def generate_quality_report(self):
        """生成质量报告"""
        report = {
            "generated_at": datetime.now(),
            "summary": {
                "total_metadata_items": len(self.feedback),
                "total_feedback": sum(len(feedback) for feedback in self.feedback.values()),
                "avg_rating": 0
            },
            "top_issues": [],
            "recent_trends": []
        }
        
        # 计算总体平均分
        all_ratings = []
        for feedback_list in self.feedback.values():
            for feedback in feedback_list:
                all_ratings.append(feedback["rating"])
        
        if all_ratings:
            report["summary"]["avg_rating"] = sum(all_ratings) / len(all_ratings)
        
        # 找出评分最低的元数据
        low_rated_items = []
        for metadata_id, feedback_list in self.feedback.items():
            if feedback_list:
                avg_rating = sum(f["rating"] for f in feedback_list) / len(feedback_list)
                low_rated_items.append({
                    "metadata_id": metadata_id,
                    "avg_rating": avg_rating,
                    "feedback_count": len(feedback_list)
                })
        
        low_rated_items.sort(key=lambda x: x["avg_rating"])
        report["top_issues"] = low_rated_items[:5]
        
        # 获取最近趋势
        for metadata_id in list(self.feedback.keys())[:10]:  # 限制数量
            trend = self.get_quality_trend(metadata_id)
            if trend:
                report["recent_trends"].append(trend)
        
        return report


# ====================
# 8.4 质量改进系统
# ====================

class MetadataQualityImprovement:
    """
    元数据质量改进系统
    提供质量改进流程和策略
    """
    
    def __init__(self):
        self.improvement_actions = []
        self.action_status = {}
        self.quality_metrics_history = {}
    
    def analyze_quality_issues(self, quality_report):
        """分析质量问题并识别改进机会"""
        issues = quality_report["issues"]
        analysis = {
            "issue_patterns": {},
            "priority_issues": [],
            "improvement_areas": []
        }
        
        # 分析问题模式
        for issue in issues:
            issue_type = issue["type"]
            field = issue["field"]
            severity = issue["severity"]
            
            key = f"{issue_type}_{field}"
            if key not in analysis["issue_patterns"]:
                analysis["issue_patterns"][key] = {
                    "type": issue_type,
                    "field": field,
                    "count": 0,
                    "severity_distribution": {"high": 0, "medium": 0, "low": 0}
                }
            
            analysis["issue_patterns"][key]["count"] += 1
            analysis["issue_patterns"][key]["severity_distribution"][severity] += 1
        
        # 识别优先问题（高频率或高严重程度）
        for key, pattern in analysis["issue_patterns"].items():
            priority_score = (
                pattern["count"] * 0.3 +
                pattern["severity_distribution"]["high"] * 1.0 +
                pattern["severity_distribution"]["medium"] * 0.5 +
                pattern["severity_distribution"]["low"] * 0.1
            )
            
            analysis["priority_issues"].append({
                "pattern": key,
                "priority_score": priority_score,
                "details": pattern
            })
        
        # 按优先级排序
        analysis["priority_issues"].sort(key=lambda x: x["priority_score"], reverse=True)
        
        # 识别改进领域
        improvement_areas = {}
        for issue in analysis["priority_issues"]:
            issue_type = issue["details"]["type"]
            if issue_type not in improvement_areas:
                improvement_areas[issue_type] = {
                    "type": issue_type,
                    "total_issues": 0,
                    "affected_fields": [],
                    "recommendations": []
                }
            
            improvement_areas[issue_type]["total_issues"] += issue["details"]["count"]
            field = issue["details"]["field"]
            if field not in improvement_areas[issue_type]["affected_fields"]:
                improvement_areas[issue_type]["affected_fields"].append(field)
        
        # 为每个改进领域生成建议
        for area_type, area in improvement_areas.items():
            area["recommendations"] = self._generate_recommendations(area_type)
        
        analysis["improvement_areas"] = list(improvement_areas.values())
        
        return analysis
    
    def _generate_recommendations(self, issue_type):
        """为问题类型生成改进建议"""
        recommendations_map = {
            "completeness": [
                "设置必填字段的默认值",
                "实施元数据完整性检查",
                "定期审核未完成的元数据字段",
                "为数据所有者设置完整性KPI"
            ],
            "accuracy": [
                "建立元数据审核流程",
                "实施数据源自动验证",
                "定期更新过期元数据",
                "建立专家评审机制"
            ],
            "consistency": [
                "强化命名规范执行",
                "实施自动化格式检查",
                "建立元数据标准模板",
                "定期进行一致性审核"
            ],
            "format": [
                "设置字段长度限制",
                "实施自动化格式验证",
                "为用户提供格式指导",
                "建立格式标准文档"
            ],
            "reference": [
                "实施引用完整性检查",
                "建立自动引用更新机制",
                "定期验证引用有效性",
                "建立引用变更通知流程"
            ]
        }
        
        return recommendations_map.get(issue_type, ["实施人工审核流程", "建立质量监控机制"])
    
    def create_improvement_plan(self, quality_analysis):
        """创建改进计划"""
        plan = {
            "created_at": datetime.now(),
            "summary": {
                "total_areas": len(quality_analysis["improvement_areas"]),
                "high_priority_count": 0
            },
            "improvement_actions": []
        }
        
        # 为每个改进领域创建行动项
        for i, area in enumerate(quality_analysis["improvement_areas"]):
            for j, recommendation in enumerate(area["recommendations"][:2]):  # 每个领域选择前2个建议
                action = {
                    "id": f"action_{i}_{j}",
                    "area": area["type"],
                    "description": recommendation,
                    "priority": "high" if area["total_issues"] > 5 else "medium",
                    "status": "planned",
                    "estimated_effort": self._estimate_effort(area["type"], recommendation),
                    "responsible": "data_governance_team",
                    "due_date": datetime.now() + timedelta(weeks=4),
                    "created_at": datetime.now()
                }
                
                plan["improvement_actions"].append(action)
                
                if action["priority"] == "high":
                    plan["summary"]["high_priority_count"] += 1
                
                # 保存行动项
                self.improvement_actions.append(action)
                self.action_status[action["id"]] = action
        
        # 按优先级排序
        plan["improvement_actions"].sort(key=lambda x: (0 if x["priority"] == "high" else 1, x["due_date"]))
        
        return plan
    
    def _estimate_effort(self, area_type, recommendation):
        """估算工作量"""
        effort_map = {
            ("completeness", "设置必填字段的默认值"): "low",
            ("completeness", "实施元数据完整性检查"): "medium",
            ("completeness", "定期审核未完成的元数据字段"): "medium",
            ("completeness", "为数据所有者设置完整性KPI"): "medium",
            
            ("accuracy", "建立元数据审核流程"): "high",
            ("accuracy", "实施数据源自动验证"): "high",
            ("accuracy", "定期更新过期元数据"): "medium",
            ("accuracy", "建立专家评审机制"): "high",
            
            ("consistency", "强化命名规范执行"): "medium",
            ("consistency", "实施自动化格式检查"): "medium",
            ("consistency", "建立元数据标准模板"): "medium",
            ("consistency", "定期进行一致性审核"): "medium",
            
            ("format", "设置字段长度限制"): "low",
            ("format", "实施自动化格式验证"): "medium",
            ("format", "为用户提供格式指导"): "low",
            ("format", "建立格式标准文档"): "low",
            
            ("reference", "实施引用完整性检查"): "medium",
            ("reference", "建立自动引用更新机制"): "high",
            ("reference", "定期验证引用有效性"): "medium",
            ("reference", "建立引用变更通知流程"): "medium"
        }
        
        return effort_map.get((area_type, recommendation), "medium")
    
    def update_action_status(self, action_id, new_status, comments=""):
        """更新行动项状态"""
        if action_id in self.action_status:
            action = self.action_status[action_id]
            action["status"] = new_status
            action["last_updated"] = datetime.now()
            
            if comments:
                if "comments" not in action:
                    action["comments"] = []
                action["comments"].append({
                    "timestamp": datetime.now(),
                    "comment": comments
                })
            
            return True
        return False
    
    def track_progress(self):
        """跟踪改进进度"""
        total_actions = len(self.improvement_actions)
        completed_actions = sum(1 for action in self.improvement_actions if action.get("status") == "completed")
        in_progress_actions = sum(1 for action in self.improvement_actions if action.get("status") == "in_progress")
        
        progress_percentage = (completed_actions / total_actions) * 100 if total_actions > 0 else 0
        
        # 按区域统计
        area_progress = {}
        for action in self.improvement_actions:
            area = action.get("area", "unknown")
            if area not in area_progress:
                area_progress[area] = {
                    "total": 0,
                    "completed": 0,
                    "in_progress": 0
                }
            
            area_progress[area]["total"] += 1
            if action.get("status") == "completed":
                area_progress[area]["completed"] += 1
            elif action.get("status") == "in_progress":
                area_progress[area]["in_progress"] += 1
        
        # 计算各区域完成百分比
        for area, stats in area_progress.items():
            stats["completion_percentage"] = (stats["completed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        
        return {
            "overall": {
                "total_actions": total_actions,
                "completed_actions": completed_actions,
                "in_progress_actions": in_progress_actions,
                "progress_percentage": progress_percentage
            },
            "by_area": area_progress
        }
    
    def measure_quality_impact(self, before_score, after_score):
        """测量质量改进影响"""
        if before_score is None or after_score is None:
            return None
        
        improvement = after_score - before_score
        improvement_percentage = (improvement / before_score) * 100 if before_score > 0 else 0
        
        return {
            "before_score": before_score,
            "after_score": after_score,
            "improvement": improvement,
            "improvement_percentage": improvement_percentage,
            "impact_level": self._assess_impact_level(improvement_percentage)
        }
    
    def _assess_impact_level(self, improvement_percentage):
        """评估影响级别"""
        if improvement_percentage >= 20:
            return "significant"
        elif improvement_percentage >= 10:
            return "moderate"
        elif improvement_percentage >= 5:
            return "minor"
        else:
            return "negligible"


# ====================
# 8.5 质量指标体系
# ====================

class MetadataQualityMetrics:
    """
    元数据质量指标体系
    提供全面的质量指标定义和计算
    """
    
    def __init__(self):
        self.metrics_definitions = {
            "accuracy": {
                "name": "准确性指标",
                "description": "衡量元数据与实际数据的一致程度",
                "metrics": [
                    {
                        "id": "accuracy_description",
                        "name": "描述准确性",
                        "formula": "correct_descriptions / total_descriptions",
                        "unit": "percentage",
                        "target": 0.95
                    },
                    {
                        "id": "accuracy_schema",
                        "name": "结构准确性",
                        "formula": "correct_schemas / total_schemas",
                        "unit": "percentage",
                        "target": 0.98
                    }
                ]
            },
            "completeness": {
                "name": "完整性指标",
                "description": "衡量元数据覆盖数据资产的完整程度",
                "metrics": [
                    {
                        "id": "completeness_required_fields",
                        "name": "必填字段完整率",
                        "formula": "filled_required_fields / total_required_fields",
                        "unit": "percentage",
                        "target": 0.90
                    },
                    {
                        "id": "completeness_coverage",
                        "name": "资产覆盖率",
                        "formula": "metadata_covered_assets / total_assets",
                        "unit": "percentage",
                        "target": 0.85
                    }
                ]
            },
            "consistency": {
                "name": "一致性指标",
                "description": "衡量元数据遵循标准规范的程度",
                "metrics": [
                    {
                        "id": "consistency_naming",
                        "name": "命名规范遵守率",
                        "formula": "correctly_named_items / total_items",
                        "unit": "percentage",
                        "target": 0.90
                    },
                    {
                        "id": "consistency_format",
                        "name": "格式一致性",
                        "formula": "consistently_formatted_items / total_items",
                        "unit": "percentage",
                        "target": 0.95
                    }
                ]
            },
            "timeliness": {
                "name": "时效性指标",
                "description": "衡量元数据更新及时性",
                "metrics": [
                    {
                        "id": "timeliness_update_frequency",
                        "name": "更新频率达标率",
                        "formula": "frequently_updated_items / total_items",
                        "unit": "percentage",
                        "target": 0.90
                    },
                    {
                        "id": "timeliness_lag",
                        "name": "平均更新延迟",
                        "formula": "total_update_delay / total_updates",
                        "unit": "hours",
                        "target": 24
                    }
                ]
            },
            "accessibility": {
                "name": "可访问性指标",
                "description": "衡量元数据获取的便利性",
                "metrics": [
                    {
                        "id": "accessibility_availability",
                        "name": "系统可用性",
                        "formula": "uptime / total_time",
                        "unit": "percentage",
                        "target": 0.99
                    },
                    {
                        "id": "accessibility_response_time",
                        "name": "平均响应时间",
                        "formula": "total_response_time / total_requests",
                        "unit": "milliseconds",
                        "target": 500
                    }
                ]
            },
            "usability": {
                "name": "可用性指标",
                "description": "衡量用户对元数据的满意程度",
                "metrics": [
                    {
                        "id": "usability_user_rating",
                        "name": "用户满意度评分",
                        "formula": "total_user_ratings / total_ratings",
                        "unit": "score",
                        "target": 4.0
                    },
                    {
                        "id": "usability_findability",
                        "name": "数据可发现性",
                        "formula": "successful_searches / total_searches",
                        "unit": "percentage",
                        "target": 0.80
                    }
                ]
            }
        }
        
        self.metric_values = {}  # 存储指标值的历史记录
    
    def calculate_metric_value(self, metric_id, data):
        """计算特定指标的值"""
        # 查找指标定义
        metric_definition = None
        for category, category_info in self.metrics_definitions.items():
            for metric in category_info["metrics"]:
                if metric["id"] == metric_id:
                    metric_definition = metric
                    break
            if metric_definition:
                break
        
        if not metric_definition:
            return None
        
        # 根据指标类型和公式计算值
        formula = metric_definition["formula"]
        
        # 这里简化实现，实际应用中应该解析公式并计算
        # 下面是示例计算逻辑
        if metric_id == "accuracy_description":
            correct = data.get("correct_descriptions", 0)
            total = data.get("total_descriptions", 1)
            return correct / total if total > 0 else 0
        
        elif metric_id == "completeness_required_fields":
            filled = data.get("filled_required_fields", 0)
            total = data.get("total_required_fields", 1)
            return filled / total if total > 0 else 0
        
        elif metric_id == "consistency_naming":
            correct = data.get("correctly_named_items", 0)
            total = data.get("total_items", 1)
            return correct / total if total > 0 else 0
        
        elif metric_id == "timeliness_lag":
            total_delay = data.get("total_update_delay", 0)
            total_updates = data.get("total_updates", 1)
            return total_delay / total_updates if total_updates > 0 else 0
        
        elif metric_id == "usability_user_rating":
            total_rating = data.get("total_user_ratings", 0)
            total_count = data.get("total_ratings", 1)
            return total_rating / total_count if total_count > 0 else 0
        
        # 默认返回0
        return 0
    
    def record_metric_value(self, metric_id, value, timestamp=None):
        """记录指标值"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if metric_id not in self.metric_values:
            self.metric_values[metric_id] = []
        
        self.metric_values[metric_id].append({
            "value": value,
            "timestamp": timestamp
        })
    
    def get_metric_trend(self, metric_id, days=30):
        """获取指标趋势"""
        if metric_id not in self.metric_values:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_values = [
            entry for entry in self.metric_values[metric_id]
            if entry["timestamp"] > cutoff_date
        ]
        
        if len(recent_values) < 2:
            return None
        
        # 按时间排序
        recent_values.sort(key=lambda x: x["timestamp"])
        
        # 计算趋势
        first_value = recent_values[0]["value"]
        last_value = recent_values[-1]["value"]
        
        change = last_value - first_value
        change_percentage = (change / first_value) * 100 if first_value != 0 else 0
        
        # 确定趋势方向
        if abs(change_percentage) < 5:
            trend = "stable"
        elif change_percentage > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "metric_id": metric_id,
            "trend": trend,
            "change": change,
            "change_percentage": change_percentage,
            "first_value": first_value,
            "last_value": last_value,
            "period_days": days,
            "data_points": len(recent_values)
        }
    
    def generate_metrics_report(self, date_range=None):
        """生成指标报告"""
        report = {
            "generated_at": datetime.now(),
            "date_range": date_range,
            "summary": {
                "total_metrics": sum(len(category["metrics"]) for category in self.metrics_definitions.values()),
                "metrics_with_target_met": 0,
                "overall_compliance": 0
            },
            "categories": {},
            "trends": {},
            "recommendations": []
        }
        
        # 收集当前指标值
        current_values = {}
        for category, category_info in self.metrics_definitions.items():
            report["categories"][category] = {
                "name": category_info["name"],
                "metrics": []
            }
            
            for metric in category_info["metrics"]:
                metric_id = metric["id"]
                
                # 获取最新值
                if metric_id in self.metric_values and self.metric_values[metric_id]:
                    latest_value = self.metric_values[metric_id][-1]["value"]
                    current_values[metric_id] = latest_value
                    
                    target = metric["target"]
                    met_target = self._check_target_met(latest_value, target, metric["unit"])
                    
                    if met_target:
                        report["summary"]["metrics_with_target_met"] += 1
                    
                    metric_info = {
                        "id": metric_id,
                        "name": metric["name"],
                        "current_value": latest_value,
                        "target": target,
                        "unit": metric["unit"],
                        "target_met": met_target
                    }
                    
                    report["categories"][category]["metrics"].append(metric_info)
        
        # 计算总体合规性
        total_metrics = report["summary"]["total_metrics"]
        metrics_with_values = len(current_values)
        metrics_met_target = report["summary"]["metrics_with_target_met"]
        
        if metrics_with_values > 0:
            report["summary"]["overall_compliance"] = metrics_met_target / metrics_with_values
        
        # 获取趋势
        for metric_id in current_values:
            trend = self.get_metric_trend(metric_id)
            if trend:
                report["trends"][metric_id] = trend
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _check_target_met(self, value, target, unit):
        """检查指标是否达到目标"""
        if unit == "percentage" or unit == "score":
            return value >= target
        elif unit == "hours" or unit == "milliseconds":
            return value <= target
        else:
            return value >= target
    
    def _generate_recommendations(self, report):
        """基于报告生成建议"""
        recommendations = []
        
        # 找出未达标的关键指标
        for category, category_info in report["categories"].items():
            for metric in category_info["metrics"]:
                if not metric["target_met"]:
                    recommendations.append({
                        "priority": "high",
                        "metric_id": metric["id"],
                        "metric_name": metric["name"],
                        "current_value": metric["current_value"],
                        "target": metric["target"],
                        "recommendation": f"改进{metric['name']}，当前值{metric['current_value']:.2f}未达到目标{metric['target']}"
                    })
        
        # 基于趋势的建议
        for metric_id, trend in report["trends"].items():
            if trend["trend"] == "decreasing" and abs(trend["change_percentage"]) > 10:
                recommendations.append({
                    "priority": "medium",
                    "metric_id": metric_id,
                    "trend": trend,
                    "recommendation": f"指标{metric_id}呈下降趋势({trend['change_percentage']:.1f}%)，需要关注和改进"
                })
        
        return recommendations


# ====================
# 示例使用代码
# ====================

def demo_quality_framework():
    """演示质量框架使用"""
    print("=== 元数据质量框架演示 ===")
    
    framework = MetadataQualityFramework()
    
    # 计算维度得分
    metric_scores = {
        "description_accuracy": 0.85,
        "schema_accuracy": 0.92,
        "required_fields_complete": 0.88,
        "coverage": 0.75,
        "naming_convention": 0.80,
        "format_consistency": 0.90,
        "update_frequency": "daily",
        "update_lag": 30 * 60,  # 30分钟（秒）
        "user_rating": 3.5,
        "clarity_score": 3.8,
        "availability": 0.98,
        "response_time": 400  # 毫秒
    }
    
    # 计算各维度得分
    dimension_scores = {}
    for dimension_name in framework.quality_dimensions:
        dimension_score = framework.calculate_dimension_score(dimension_name, metric_scores)
        dimension_scores[dimension_name] = dimension_score
        print(f"{framework.quality_dimensions[dimension_name]['name']}: {dimension_score:.2f}")
    
    # 计算总体得分
    overall_score = framework.calculate_overall_score(dimension_scores)
    quality_level = framework.get_quality_level(overall_score)
    
    print(f"\n总体质量得分: {overall_score:.2f}")
    print(f"质量等级: {quality_level}")


def demo_quality_checker():
    """演示质量检查器使用"""
    print("\n=== 元数据质量检查器演示 ===")
    
    quality_checker = MetadataQualityChecker()
    
    # 测试元数据
    test_metadata = [
        {
            "id": "table_001",
            "name": "tbl_customer",
            "description": "客户基本信息表，包含客户的基本联系信息和个人资料",
            "owner": "销售部门",
            "schema": {
                "customer_id": {"type": "string", "description": "客户唯一标识"},
                "name": {"type": "string", "description": "客户姓名"},
                "email": {"type": "string", "description": "电子邮箱"},
                "phone": {"type": "string", "description": "联系电话"}
            }
        },
        {
            "id": "table_002",
            "name": "CustomerOrders",  # 命名不符合规范
            "description": "",  # 描述为空
            "owner": "sales@company.com",
            "schema": {
                "order_id": {"type": "string", "description": "订单ID"},
                "customer_id": {"type": "string", "description": "客户ID"},
                "amount": {"type": "decimal", "description": "订单金额"}
            },
            "references": [
                {"ref_type": "table", "ref_id": "tbl_customer"}  # 正常引用
            ]
        },
        {
            "id": "table_003",
            "name": "vw_order_summary",
            "description": "订单汇总视图，显示各类订单的统计信息" * 10,  # 描述过长
            "owner": "销售部门",
            "schema": {
                "order_type": {"type": "string", "description": "订单类型"},
                "count": {"type": "integer", "description": "数量"},
                "total_amount": {"type": "decimal", "description": "总金额"}
            },
            "references": [
                {"type": "table"}  # 引用不完整
            ]
        }
    ]
    
    # 生成质量报告
    quality_report = quality_checker.generate_quality_report(test_metadata)
    
    print(f"元数据质量报告")
    print(f"================")
    print(f"总项目数: {quality_report['summary']['total_items']}")
    print(f"有问题的项目数: {quality_report['summary']['items_with_issues']}")
    print(f"总问题数: {quality_report['summary']['total_issues']}")
    print(f"质量得分: {quality_report['summary']['quality_score']:.2f}")
    print(f"质量等级: {quality_report['summary']['quality_level']}")
    
    print(f"\n问题类型分布:")
    for issue_type, count in quality_report['issue_statistics']['by_type'].items():
        print(f"- {issue_type}: {count}")
    
    print(f"\n严重程度分布:")
    for severity, count in quality_report['issue_statistics']['by_severity'].items():
        print(f"- {severity}: {count}")
    
    print(f"\n具体问题:")
    for issue in quality_report['issues'][:5]:  # 显示前5个问题
        print(f"- {issue['severity']}: {issue['message']} (元数据ID: {issue['metadata_id']}, 字段: {issue['field']})")


def demo_feedback_system():
    """演示反馈系统使用"""
    print("\n=== 元数据反馈系统演示 ===")
    
    feedback_system = MetadataFeedbackSystem()
    
    # 添加用户反馈
    feedback_system.add_feedback("table_001", "user1", "accuracy", 5, "元数据描述准确，字段类型正确")
    feedback_system.add_feedback("table_001", "user2", "completeness", 4, "大部分字段都有描述，但缺少业务含义")
    feedback_system.add_feedback("table_002", "user3", "accuracy", 2, "描述不准确，实际字段与描述不符")
    feedback_system.add_feedback("table_002", "user4", "usefulness", 3, "信息有帮助但不够详细")
    feedback_system.add_feedback("table_003", "user5", "clarity", 4, "描述清晰，但过于冗长")
    
    # 获取元数据反馈
    metadata_feedback = feedback_system.get_metadata_feedback("table_001")
    print(f"table_001 的反馈:")
    for feedback in metadata_feedback:
        print(f"- 用户 {feedback['user_id']}: {feedback['type']} {feedback['rating']}/5 - {feedback['comment']}")
    
    # 获取元数据统计
    metadata_stats = feedback_system.get_metadata_stats("table_001")
    print(f"\ntable_001 的统计:")
    print(f"- 总反馈数: {metadata_stats['total_feedback']}")
    print(f"- 总体平均分: {metadata_stats['overall_avg_rating']:.2f}")
    
    # 获取通知
    notifications = feedback_system.get_all_notifications(status="unread")
    if notifications:
        print(f"\n未读通知:")
        for notification in notifications:
            print(f"- {notification['message']} ({notification['timestamp'].strftime('%Y-%m-%d')})")
    
    # 获取质量趋势
    trend = feedback_system.get_quality_trend("table_001", days=30)
    if trend:
        print(f"\n质量趋势: {trend['trend']}")
        print(f"变化: {trend['change']:.2f}")
    
    # 生成质量报告
    quality_report = feedback_system.generate_quality_report()
    print(f"\n质量报告摘要:")
    print(f"- 总元数据项: {quality_report['summary']['total_metadata_items']}")
    print(f"- 总反馈数: {quality_report['summary']['total_feedback']}")
    print(f"- 总体平均分: {quality_report['summary']['avg_rating']:.2f}")
    
    print("\n评分最低的元数据项:")
    for item in quality_report['top_issues']:
        print(f"- {item['metadata_id']}: {item['avg_rating']:.2f} ({item['feedback_count']} 条反馈)")


def demo_quality_improvement():
    """演示质量改进系统使用"""
    print("\n=== 元数据质量改进系统演示 ===")
    
    improvement_system = MetadataQualityImprovement()
    
    # 模拟质量报告
    mock_quality_report = {
        "summary": {
            "total_items": 100,
            "items_with_issues": 30,
            "quality_score": 0.7
        },
        "issues": [
            {"type": "completeness", "field": "description", "severity": "high", "metadata_id": "1"},
            {"type": "completeness", "field": "description", "severity": "medium", "metadata_id": "2"},
            {"type": "completeness", "field": "owner", "severity": "high", "metadata_id": "3"},
            {"type": "accuracy", "field": "schema", "severity": "medium", "metadata_id": "4"},
            {"type": "accuracy", "field": "schema", "severity": "medium", "metadata_id": "5"},
            {"type": "consistency", "field": "name", "severity": "low", "metadata_id": "6"},
            {"type": "consistency", "field": "name", "severity": "low", "metadata_id": "7"},
            {"type": "format", "field": "description", "severity": "low", "metadata_id": "8"},
            {"type": "reference", "field": "references", "severity": "high", "metadata_id": "9"}
        ]
    }
    
    # 分析质量问题
    quality_analysis = improvement_system.analyze_quality_issues(mock_quality_report)
    print(f"质量问题分析:")
    print(f"- 问题模式数: {len(quality_analysis['issue_patterns'])}")
    print(f"- 优先问题数: {len(quality_analysis['priority_issues'])}")
    print(f"- 改进领域数: {len(quality_analysis['improvement_areas'])}")
    
    print("\n优先问题 (前3):")
    for i, issue in enumerate(quality_analysis["priority_issues"][:3]):
        print(f"{i+1}. {issue['pattern']} (优先级分数: {issue['priority_score']:.2f})")
        print(f"   - 类型: {issue['details']['type']}, 字段: {issue['details']['field']}")
        print(f"   - 数量: {issue['details']['count']}")
        print(f"   - 严重程度分布: 高:{issue['details']['severity_distribution']['high']} 中:{issue['details']['severity_distribution']['medium']} 低:{issue['details']['severity_distribution']['low']}")
    
    # 创建改进计划
    improvement_plan = improvement_system.create_improvement_plan(quality_analysis)
    print(f"\n改进计划:")
    print(f"- 总行动项: {improvement_plan['summary']['total_areas'] * 2}")  # 每个领域2个行动项
    print(f"- 高优先级行动: {improvement_plan['summary']['high_priority_count']}")
    
    print("\n行动项 (前5):")
    for i, action in enumerate(improvement_plan["improvement_actions"][:5]):
        print(f"{i+1}. {action['description']}")
        print(f"   - 领域: {action['area']}, 优先级: {action['priority']}")
        print(f"   - 工作量: {action['estimated_effort']}, 截止日期: {action['due_date'].strftime('%Y-%m-%d')}")
    
    # 更新行动状态
    if improvement_plan["improvement_actions"]:
        first_action_id = improvement_plan["improvement_actions"][0]["id"]
        improvement_system.update_action_status(first_action_id, "in_progress", "开始实施自动化检查")
        
        second_action_id = improvement_plan["improvement_actions"][1]["id"]
        improvement_system.update_action_status(second_action_id, "completed", "已设置字段长度限制")
    
    # 跟踪进度
    progress = improvement_system.track_progress()
    print(f"\n改进进度:")
    print(f"- 总体进度: {progress['overall']['progress_percentage']:.1f}% ({progress['overall']['completed_actions']}/{progress['overall']['total_actions']})")
    print(f"- 进行中: {progress['overall']['in_progress_actions']}")
    
    print("\n各领域进度:")
    for area, stats in progress["by_area"].items():
        print(f"- {area}: {stats['completion_percentage']:.1f}% ({stats['completed']}/{stats['total']})")
    
    # 测量质量影响
    before_score = 0.7
    after_score = 0.85  # 假设改进后的得分
    
    impact = improvement_system.measure_quality_impact(before_score, after_score)
    print(f"\n质量影响:")
    print(f"- 改进前得分: {impact['before_score']:.2f}")
    print(f"- 改进后得分: {impact['after_score']:.2f}")
    print(f"- 改进幅度: {impact['improvement_percentage']:.1f}%")
    print(f"- 影响级别: {impact['impact_level']}")


def demo_quality_metrics():
    """演示质量指标体系使用"""
    print("\n=== 元数据质量指标体系演示 ===")
    
    metrics_system = MetadataQualityMetrics()
    
    # 记录一些指标值
    metrics_system.record_metric_value("accuracy_description", 0.85, datetime.now() - timedelta(days=7))
    metrics_system.record_metric_value("accuracy_description", 0.87, datetime.now() - timedelta(days=3))
    metrics_system.record_metric_value("accuracy_description", 0.90, datetime.now())
    
    metrics_system.record_metric_value("completeness_required_fields", 0.78, datetime.now() - timedelta(days=7))
    metrics_system.record_metric_value("completeness_required_fields", 0.82, datetime.now() - timedelta(days=3))
    metrics_system.record_metric_value("completeness_required_fields", 0.85, datetime.now())
    
    metrics_system.record_metric_value("consistency_naming", 0.88, datetime.now() - timedelta(days=7))
    metrics_system.record_metric_value("consistency_naming", 0.90, datetime.now() - timedelta(days=3))
    metrics_system.record_metric_value("consistency_naming", 0.91, datetime.now())
    
    # 获取指标趋势
    accuracy_trend = metrics_system.get_metric_trend("accuracy_description")
    if accuracy_trend:
        print(f"描述准确性趋势:")
        print(f"- 趋势: {accuracy_trend['trend']}")
        print(f"- 变化: {accuracy_trend['change_percentage']:.2f}%")
        print(f"- 当前值: {accuracy_trend['last_value']:.2f}, 目标值前: {accuracy_trend['first_value']:.2f}")
    
    # 生成指标报告
    metrics_report = metrics_system.generate_metrics_report()
    print(f"\n元数据质量指标报告:")
    print(f"- 总指标数: {metrics_report['summary']['total_metrics']}")
    print(f"- 达标指标数: {metrics_report['summary']['metrics_with_target_met']}")
    print(f"- 总体合规性: {metrics_report['summary']['overall_compliance']:.2f}")
    
    print("\n各类指标情况:")
    for category, category_info in metrics_report["categories"].items():
        print(f"\n{category_info['name']}:")
        for metric in category_info["metrics"]:
            status = "✓" if metric["target_met"] else "✗"
            print(f"  {status} {metric['name']}: {metric['current_value']:.2f} (目标: {metric['target']})")
    
    print("\n建议:")
    for rec in metrics_report["recommendations"]:
        print(f"- {rec['priority'].upper()}: {rec['recommendation']}")


def main():
    """主函数，运行所有演示"""
    demo_quality_framework()
    demo_quality_checker()
    demo_feedback_system()
    demo_quality_improvement()
    demo_quality_metrics()


if __name__ == "__main__":
    main()