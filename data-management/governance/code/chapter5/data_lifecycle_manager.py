#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据生命周期管理系统
功能：实现数据全生命周期的自动化管理，包括存储优化、保留合规、归档和处置
作者：数据治理团队
日期：2023-11-23
"""

import pandas as pd
import numpy as np
import json
import datetime
import time
import random
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import schedule
import warnings
warnings.filterwarnings('ignore')
from typing import Dict, List, Tuple, Any, Optional

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class DataStorageStrategy:
    """数据存储策略类"""
    
    def __init__(self):
        self.tier_config = {
            "hot": {
                "access_frequency": "每天多次",
                "performance_requirement": "毫秒级响应",
                "storage_type": "SSD/NVMe",
                "retention_period": "6-12个月",
                "cost_per_gb": 10  # 每GB每月成本
            },
            "warm": {
                "access_frequency": "每周几次",
                "performance_requirement": "秒级响应",
                "storage_type": "SSD/HDD混合",
                "retention_period": "1-3年",
                "cost_per_gb": 5
            },
            "cold": {
                "access_frequency": "每月几次或更少",
                "performance_requirement": "分钟级响应",
                "storage_type": "HDD/磁带",
                "retention_period": "3年以上",
                "cost_per_gb": 1
            }
        }
    
    def recommend_storage_tier(self, data_characteristics):
        """根据数据特征推荐存储层级"""
        age_months = data_characteristics.get("age_months", 0)
        access_frequency = data_characteristics.get("access_frequency", 0)
        business_criticality = data_characteristics.get("business_criticality", "medium")
        
        if age_months < 6 and access_frequency > 30 and business_criticality == "high":
            return "hot"
        elif age_months < 36 and access_frequency > 4:
            return "warm"
        else:
            return "cold"
    
    def optimize_storage_allocation(self, data_inventory):
        """优化存储分配"""
        recommendations = []
        
        for data_item in data_inventory:
            current_tier = data_item.get("current_tier", "warm")
            recommended_tier = self.recommend_storage_tier(data_item)
            
            if current_tier != recommended_tier:
                recommendations.append({
                    "data_id": data_item["id"],
                    "current_tier": current_tier,
                    "recommended_tier": recommended_tier,
                    "estimated_savings": data_item.get("size_gb", 0) * (
                        self.tier_config[current_tier]["cost_per_gb"] - 
                        self.tier_config[recommended_tier]["cost_per_gb"]
                    ),
                    "performance_impact": self._calculate_performance_impact(current_tier, recommended_tier)
                })
        
        return recommendations
    
    def _calculate_performance_impact(self, current_tier, recommended_tier):
        """计算性能影响"""
        tier_performance = {"hot": 1, "warm": 2, "cold": 3}  # 数字越小性能越好
        current = tier_performance[current_tier]
        recommended = tier_performance[recommended_tier]
        
        if recommended > current:
            return "性能下降"
        elif recommended < current:
            return "性能提升"
        else:
            return "无变化"

class DataRetentionPolicy:
    """数据保留政策类"""
    
    def __init__(self):
        self.retention_rules = {
            "customer_data": {
                "default_retention": 2555,  # 7年(天)
                "minimum_retention": 1825,  # 5年
                "maximum_retention": 3650,  # 10年
                "legal_requirements": ["GDPR", "CCPA", "数据保护法"],
                "business_reason": "客户关系管理、合规审计",
                "disposal_method": "安全删除",
                "disapproval_required": False
            },
            "transaction_data": {
                "default_retention": 2555,  # 7年
                "minimum_retention": 1825,  # 5年
                "maximum_retention": 3650,  # 10年
                "legal_requirements": ["税法", "会计准则"],
                "business_reason": "财务审计、税务申报",
                "disposal_method": "安全删除+认证",
                "disapproval_required": True
            },
            "employee_data": {
                "default_retention": 2555,  # 7年
                "minimum_retention": 1825,  # 5年
                "maximum_retention": 3650,  # 10年
                "legal_requirements": ["劳动法", "平等就业法"],
                "business_reason": "人力资源、法律合规",
                "disposal_method": "安全删除+认证",
                "disapproval_required": True
            },
            "analytics_data": {
                "default_retention": 1095,  # 3年
                "minimum_retention": 365,   # 1年
                "maximum_retention": 1825,  # 5年
                "legal_requirements": [],
                "business_reason": "业务分析、趋势预测",
                "disposal_method": "删除",
                "disapproval_required": False
            },
            "email_communications": {
                "default_retention": 1825,  # 5年
                "minimum_retention": 730,   # 2年
                "maximum_retention": 3650,  # 10年
                "legal_requirements": ["证据法", "通信法"],
                "business_reason": "业务记录、法律证据",
                "disposal_method": "安全删除",
                "disapproval_required": False
            }
        }
    
    def assess_retention_compliance(self, data_inventory):
        """评估保留合规性"""
        compliance_report = {
            "compliant_items": [],
            "non_compliant_items": [],
            "items_nearing_disposal": [],
            "items_on_hold": [],
            "retention_summary": {}
        }
        
        current_date = datetime.datetime.now()
        
        for data_item in data_inventory:
            data_type = data_item.get("type", "unknown")
            creation_date = datetime.datetime.strptime(data_item.get("created_date", current_date.strftime("%Y-%m-%d")), "%Y-%m-%d")
            
            # 获取保留规则
            rule = self.retention_rules.get(data_type)
            if not rule:
                compliance_report["non_compliant_items"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "reason": "未定义的数据类型",
                    "severity": "高"
                })
                continue
            
            # 计算数据年龄
            age_days = (current_date - creation_date).days
            
            # 检查是否有保留锁定
            on_hold = data_item.get("on_hold", False)
            hold_reason = data_item.get("hold_reason", "")
            
            if on_hold:
                compliance_report["items_on_hold"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "hold_reason": hold_reason,
                    "hold_expiry": data_item.get("hold_expiry", "无期限")
                })
                continue
            
            # 检查保留合规性
            min_retention = rule["minimum_retention"]
            max_retention = rule["maximum_retention"]
            
            if age_days < min_retention:
                compliance_report["compliant_items"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "data_type": data_type,
                    "age_days": age_days,
                    "min_retention_days": min_retention,
                    "status": "未到最低保留期"
                })
            elif age_days >= min_retention and age_days < max_retention:
                compliance_report["compliant_items"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "data_type": data_type,
                    "age_days": age_days,
                    "min_retention_days": min_retention,
                    "max_retention_days": max_retention,
                    "status": "合规保留中"
                })
            elif age_days >= max_retention:
                # 检查是否需要审批才能处置
                if rule["disapproval_required"]:
                    status = "需要审批处置"
                    severity = "中"
                else:
                    status = "可处置"
                    severity = "低"
                
                compliance_report["non_compliant_items"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "data_type": data_type,
                    "age_days": age_days,
                    "max_retention_days": max_retention,
                    "status": status,
                    "severity": severity,
                    "disposal_method": rule["disposal_method"]
                })
            
            # 检查接近处置期的项目
            days_until_disposal = max_retention - age_days
            if 0 < days_until_disposal <= 90:  # 90天内到期
                compliance_report["items_nearing_disposal"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "data_type": data_type,
                    "age_days": age_days,
                    "days_until_disposal": days_until_disposal,
                    "disposal_method": rule["disposal_method"],
                    "approval_required": rule["disapproval_required"]
                })
        
        # 生成保留摘要
        compliance_report["retention_summary"] = {
            "total_items": len(data_inventory),
            "compliant_items": len(compliance_report["compliant_items"]),
            "non_compliant_items": len(compliance_report["non_compliant_items"]),
            "items_nearing_disposal": len(compliance_report["items_nearing_disposal"]),
            "items_on_hold": len(compliance_report["items_on_hold"]),
            "compliance_rate": len(compliance_report["compliant_items"]) / len(data_inventory) * 100 if len(data_inventory) > 0 else 0
        }
        
        return compliance_report

class DataDestructionMethods:
    """数据销毁方法类"""
    
    def __init__(self):
        self.destruction_methods = {
            "logical_deletion": {
                "description": "逻辑删除(仅标记为已删除)",
                "effectiveness": "低",
                "recovery_possible": "是",
                "suitable_for": ["测试数据", "临时数据"],
                "cost": 0.1
            },
            "standard_deletion": {
                "description": "标准删除(文件系统删除)",
                "effectiveness": "中",
                "recovery_possible": "可能",
                "suitable_for": ["非敏感业务数据", "过期日志"],
                "cost": 0.5
            },
            "secure_deletion": {
                "description": "安全删除(多次覆写)",
                "effectiveness": "高",
                "recovery_possible": "极难",
                "suitable_for": ["个人数据", "内部敏感数据"],
                "cost": 5
            },
            "crypto_shredding": {
                "description": "加密销毁(销毁密钥)",
                "effectiveness": "极高",
                "recovery_possible": "几乎不可能",
                "suitable_for": ["高度敏感数据", "加密存储数据"],
                "cost": 8
            },
            "physical_destruction": {
                "description": "物理销毁(销毁存储介质)",
                "effectiveness": "绝对",
                "recovery_possible": "不可能",
                "suitable_for": ["绝密数据", "关键基础设施"],
                "cost": 20
            }
        }
    
    def recommend_destruction_method(self, data_classification, storage_type, compliance_requirements):
        """推荐销毁方法"""
        # 基于数据分类的推荐
        if data_classification in ["绝密", "顶级机密"]:
            recommended_method = "physical_destruction"
        elif data_classification in ["机密", "高度敏感"]:
            recommended_method = "crypto_shredding"
        elif data_classification in ["内部", "受限"]:
            recommended_method = "secure_deletion"
        elif data_classification in ["公开", "内部公开"]:
            recommended_method = "standard_deletion"
        else:
            recommended_method = "logical_deletion"
        
        # 考虑存储类型的影响
        if storage_type == "云存储" and data_classification in ["内部", "受限"]:
            recommended_method = "crypto_shredding"
        elif storage_type == "磁带存储" and data_classification in ["机密", "高度敏感"]:
            recommended_method = "physical_destruction"
        
        # 考虑合规要求的影响
        if compliance_requirements == "GDPR" and data_classification in ["个人数据", "高度敏感"]:
            recommended_method = "crypto_shredding"  # GDPR强调被遗忘权
        elif compliance_requirements == "HIPAA" and data_classification in ["受保护健康信息"]:
            recommended_method = "secure_deletion"
        
        method_details = self.destruction_methods.get(recommended_method, {})
        
        return {
            "recommended_method": recommended_method,
            "method_details": method_details,
            "estimated_cost": method_details.get("cost", 1)
        }

class DataLifecycleManager:
    """数据生命周期管理器主类"""
    
    def __init__(self):
        self.storage_strategy = DataStorageStrategy()
        self.retention_policy = DataRetentionPolicy()
        self.destruction_methods = DataDestructionMethods()
        
        self.data_inventory = []
        self.lifecycle_events = []
        self.alert_thresholds = {
            "storage_utilization": 85,  # 存储利用率阈值(%)
            "retention_compliance": 90,  # 保留合规率阈值(%)
            "cost_savings_opportunity": 1000  # 成本节约机会阈值(元)
        }
    
    def register_data_asset(self, data_id, name, data_type, owner, size_gb, 
                          classification, storage_location, creation_date, 
                          business_value="medium", access_pattern="unknown"):
        """注册数据资产"""
        data_asset = {
            "id": data_id,
            "name": name,
            "type": data_type,
            "owner": owner,
            "size_gb": size_gb,
            "classification": classification,
            "storage_location": storage_location,
            "creation_date": creation_date,
            "business_value": business_value,
            "access_pattern": access_pattern,
            "current_storage_tier": self.storage_strategy.recommend_storage_tier({
                "age_months": 0,
                "access_frequency": 0,
                "business_criticality": business_value
            }),
            "last_access_date": None,
            "access_count_30_days": 0,
            "access_count_90_days": 0,
            "on_hold": False,
            "hold_reason": None,
            "hold_expiry": None,
            "status": "active",
            "last_modified": datetime.datetime.now().isoformat()
        }
        
        self.data_inventory.append(data_asset)
        
        # 记录生命周期事件
        self._record_lifecycle_event(data_id, "registered", {
            "storage_tier": data_asset["current_storage_tier"]
        })
        
        return data_asset
    
    def simulate_usage_patterns(self, days=30):
        """模拟使用模式"""
        current_date = datetime.datetime.now()
        
        for asset in self.data_inventory:
            # 根据访问模式生成模拟访问
            if asset["access_pattern"] == "frequent":
                access_frequency = 15  # 平均每天15次
            elif asset["access_pattern"] == "regular":
                access_frequency = 5   # 平均每天5次
            elif asset["access_pattern"] == "occasional":
                access_frequency = 1   # 平均每天1次
            else:  # rare or unknown
                access_frequency = 0.1  # 平均10天1次
            
            # 生成过去30天的访问记录
            for day in range(days):
                date = current_date - datetime.timedelta(days=day)
                day_accesses = np.random.poisson(access_frequency)
                
                # 更新访问计数
                if day < 30:
                    asset["access_count_30_days"] += day_accesses
                if day < 90:
                    asset["access_count_90_days"] += day_accesses
                
                # 记录最后访问日期
                if day_accesses > 0:
                    asset["last_access_date"] = date.strftime("%Y-%m-%d")
                
                # 记录访问事件
                for _ in range(day_accesses):
                    self._record_lifecycle_event(asset["id"], "access", {
                        "date": date.strftime("%Y-%m-%d"),
                        "access_type": "read"
                    })
        
        return f"已模拟{days}天的使用模式"
    
    def run_lifecycle_analysis(self):
        """运行生命周期分析"""
        analysis_results = {
            "storage_optimization": self._analyze_storage_optimization(),
            "retention_compliance": self._analyze_retention_compliance(),
            "cost_optimization": self._analyze_cost_optimization(),
            "recommendations": []
        }
        
        # 生成综合推荐
        recommendations = []
        
        # 存储优化推荐
        storage_rec = self._generate_storage_recommendations(analysis_results["storage_optimization"])
        recommendations.extend(storage_rec)
        
        # 合规性推荐
        compliance_rec = self._generate_compliance_recommendations(analysis_results["retention_compliance"])
        recommendations.extend(compliance_rec)
        
        # 成本优化推荐
        cost_rec = self._generate_cost_recommendations(analysis_results["cost_optimization"])
        recommendations.extend(cost_rec)
        
        analysis_results["recommendations"] = recommendations
        
        return analysis_results
    
    def generate_lifecycle_dashboard(self, analysis_results):
        """生成生命周期仪表板"""
        dashboard_data = {}
        
        # 存储分布图
        dashboard_data["storage_distribution"] = self._prepare_storage_distribution_data()
        
        # 合规性状态图
        dashboard_data["compliance_status"] = self._prepare_compliance_status_data(analysis_results["retention_compliance"])
        
        # 成本优化图
        dashboard_data["cost_optimization"] = self._prepare_cost_optimization_data(analysis_results["cost_optimization"])
        
        # 预警信息
        dashboard_data["alerts"] = self._generate_alerts(analysis_results)
        
        return dashboard_data
    
    def visualize_lifecycle_dashboard(self, dashboard_data):
        """可视化生命周期仪表板"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('数据生命周期管理仪表板', fontsize=16)
        
        # 1. 存储分布饼图
        storage_data = dashboard_data["storage_distribution"]
        axes[0, 0].pie(storage_data["values"], labels=storage_data["labels"], autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('数据存储层级分布')
        
        # 2. 合规性状态条形图
        compliance_data = dashboard_data["compliance_status"]
        axes[0, 1].bar(compliance_data["categories"], compliance_data["values"], color=['green', 'orange', 'red', 'blue'])
        axes[0, 1].set_title('数据保留合规性状态')
        axes[0, 1].set_ylabel('数据量(GB)')
        axes[0, 1].set_ylim(0, max(compliance_data["values"]) * 1.2 if compliance_data["values"] else 10)
        
        # 3. 成本优化条形图
        cost_data = dashboard_data["cost_optimization"]
        axes[1, 0].bar(cost_data["categories"], cost_data["values"])
        axes[1, 0].set_title('潜在月度成本节约')
        axes[1, 0].set_ylabel('成本节约(元)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 生命周期阶段分布图
        lifecycle_data = self._prepare_lifecycle_stages_data()
        axes[1, 1].pie(lifecycle_data["values"], labels=lifecycle_data["labels"], autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('数据生命周期阶段分布')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # 显示预警信息
        alerts = dashboard_data["alerts"]
        if alerts:
            alert_text = "\n".join([f"• {alert}" for alert in alerts])
            fig.text(0.5, 0.01, f"预警信息:\n{alert_text}", ha='center', fontsize=10, 
                    bbox={"facecolor":"yellow", "alpha":0.3, "pad":5})
        
        plt.savefig('data_lifecycle_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return "仪表板已生成并保存为 data_lifecycle_dashboard.png"
    
    def _record_lifecycle_event(self, data_id, event_type, details):
        """记录生命周期事件"""
        event = {
            "data_id": data_id,
            "event_type": event_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "details": details
        }
        self.lifecycle_events.append(event)
    
    def _analyze_storage_optimization(self):
        """分析存储优化机会"""
        # 更新数据资产的年龄和存储层级
        current_date = datetime.datetime.now()
        
        for asset in self.data_inventory:
            # 计算年龄
            if asset.get("creation_date"):
                creation_date = datetime.datetime.strptime(asset["creation_date"], "%Y-%m-%d")
                age_days = (current_date - creation_date).days
                asset["age_days"] = age_days
                asset["age_months"] = age_days // 30
            else:
                asset["age_days"] = 0
                asset["age_months"] = 0
            
            # 重新评估存储层级
            recommended_tier = self.storage_strategy.recommend_storage_tier({
                "age_months": asset["age_months"],
                "access_frequency": asset.get("access_count_90_days", 0),
                "business_criticality": asset["business_value"]
            })
            
            asset["recommended_storage_tier"] = recommended_tier
        
        # 使用存储策略优化工具
        storage_optimization = self.storage_strategy.optimize_storage_allocation(self.data_inventory)
        
        return storage_optimization
    
    def _analyze_retention_compliance(self):
        """分析保留合规性"""
        # 更新数据资产的保留状态
        current_date = datetime.datetime.now()
        
        for asset in self.data_inventory:
            data_type = asset["type"]
            rule = self.retention_policy.retention_rules.get(data_type, {})
            
            if rule:
                asset["retention_min_days"] = rule.get("minimum_retention", 365)
                asset["retention_max_days"] = rule.get("maximum_retention", 1825)
                asset["retention_status"] = self._determine_retention_status(asset)
        
        # 使用保留政策评估工具
        compliance_analysis = self.retention_policy.assess_retention_compliance(self.data_inventory)
        
        return compliance_analysis
    
    def _analyze_cost_optimization(self):
        """分析成本优化机会"""
        cost_analysis = {
            "storage_savings": 0,
            "retention_savings": 0,
            "total_savings": 0,
            "opportunities": []
        }
        
        # 存储成本节约
        storage_optimization = self._analyze_storage_optimization()
        for rec in storage_optimization:
            if rec.get("estimated_savings", 0) > 0:
                cost_analysis["storage_savings"] += rec["estimated_savings"]
                cost_analysis["opportunities"].append({
                    "type": "存储优化",
                    "data_id": rec["data_id"],
                    "action": f"从{rec['current_tier']}迁移到{rec['recommended_tier']}",
                    "estimated_savings": rec["estimated_savings"]
                })
        
        cost_analysis["total_savings"] = cost_analysis["storage_savings"] + cost_analysis["retention_savings"]
        
        return cost_analysis
    
    def _generate_storage_recommendations(self, storage_optimization):
        """生成存储优化推荐"""
        recommendations = []
        
        for rec in storage_optimization:
            if rec.get("estimated_savings", 0) > 0:  # 只有能节省成本才推荐
                recommendation = {
                    "data_id": rec["data_id"],
                    "action": "存储层级迁移",
                    "details": f"将数据从{rec['current_tier']}迁移到{rec['recommended_tier']}",
                    "estimated_savings": rec["estimated_savings"],
                    "performance_impact": rec["performance_impact"],
                    "automation_ready": rec["performance_impact"] != "性能下降",
                    "requires_approval": rec["performance_impact"] == "性能下降",
                    "priority": "高" if rec["estimated_savings"] > 100 else "中"
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_compliance_recommendations(self, retention_compliance):
        """生成合规性推荐"""
        recommendations = []
        
        # 对非合规项生成推荐
        for item in retention_compliance["non_compliant_items"]:
            if item["status"] == "可处置":
                recommendation = {
                    "data_id": item["data_id"],
                    "action": "数据处置",
                    "details": f"处置已超过最大保留期({item['max_retention_days']}天)的数据",
                    "estimated_savings": item["size_gb"] * 0.1 * 12,  # 估算年度存储成本
                    "automation_ready": True,
                    "requires_approval": False,
                    "priority": "高"
                }
                recommendations.append(recommendation)
            elif item["status"] == "需要审批处置":
                recommendation = {
                    "data_id": item["data_id"],
                    "action": "数据处置审批",
                    "details": f"请求审批处置已超过最大保留期({item['max_retention_days']}天)的数据",
                    "estimated_savings": item["size_gb"] * 0.1 * 12,  # 估算年度存储成本
                    "automation_ready": False,
                    "requires_approval": True,
                    "priority": "高"
                }
                recommendations.append(recommendation)
        
        # 对接近处置期的项生成推荐
        for item in retention_compliance["items_nearing_disposal"]:
            if not item["approval_required"]:
                recommendation = {
                    "data_id": item["data_id"],
                    "action": "计划数据处置",
                    "details": f"计划在{item['days_until_disposal']}天后处置数据",
                    "estimated_savings": 0,  # 未来节约
                    "automation_ready": False,
                    "requires_approval": False,
                    "priority": "中"
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_cost_recommendations(self, cost_optimization):
        """生成成本优化推荐"""
        recommendations = []
        
        for opportunity in cost_optimization["opportunities"]:
            # 只推荐高成本节约机会
            if opportunity["estimated_savings"] >= self.alert_thresholds["cost_savings_opportunity"]:
                recommendation = {
                    "data_id": opportunity["data_id"],
                    "action": opportunity["action"],
                    "details": f"执行{opportunity['type']}操作可节约{opportunity['estimated_savings']:.2f}元",
                    "estimated_savings": opportunity["estimated_savings"],
                    "automation_ready": opportunity["type"] == "存储优化",
                    "requires_approval": opportunity["type"] == "数据处置",
                    "priority": "高" if opportunity["estimated_savings"] > 5000 else "中"
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _determine_retention_status(self, asset):
        """确定保留状态"""
        age_days = asset.get("age_days", 0)
        min_days = asset.get("retention_min_days", 365)
        max_days = asset.get("retention_max_days", 1825)
        
        if asset.get("on_hold", False):
            return "保留锁定"
        elif age_days < min_days:
            return "保留期内"
        elif age_days >= max_days:
            rule = self.retention_policy.retention_rules.get(asset["type"], {})
            if rule.get("disapproval_required", False):
                return "需要审批处置"
            else:
                return "可处置"
        else:
            return "保留期内"
    
    def _prepare_storage_distribution_data(self):
        """准备存储分布数据"""
        tier_counts = {"hot": 0, "warm": 0, "cold": 0}
        
        for asset in self.data_inventory:
            tier = asset["current_storage_tier"]
            if tier in tier_counts:
                tier_counts[tier] += asset["size_gb"]
        
        return {
            "labels": list(tier_counts.keys()),
            "values": list(tier_counts.values())
        }
    
    def _prepare_compliance_status_data(self, compliance_analysis):
        """准备合规状态数据"""
        compliant_volume = sum(item["size_gb"] for item in compliance_analysis["compliant_items"])
        non_compliant_volume = sum(item["size_gb"] for item in compliance_analysis["non_compliant_items"])
        nearing_disposal_volume = sum(item["size_gb"] for item in compliance_analysis["items_nearing_disposal"])
        on_hold_volume = sum(asset["size_gb"] for asset in self.data_inventory if asset.get("on_hold", False))
        
        return {
            "categories": ["合规", "不合规", "接近处置", "保留锁定"],
            "values": [compliant_volume, non_compliant_volume, nearing_disposal_volume, on_hold_volume]
        }
    
    def _prepare_cost_optimization_data(self, cost_analysis):
        """准备成本优化数据"""
        storage_savings = cost_analysis["storage_savings"]
        retention_savings = cost_analysis["retention_savings"]
        
        return {
            "categories": ["存储优化", "数据处置"],
            "values": [storage_savings, retention_savings]
        }
    
    def _prepare_lifecycle_stages_data(self):
        """准备生命周期阶段数据"""
        stage_counts = {"创建": 0, "使用": 0, "归档": 0, "待处置": 0}
        
        for asset in self.data_inventory:
            tier = asset["current_storage_tier"]
            
            if asset.get("on_hold", False):
                stage = "保留锁定"
            elif asset.get("retention_status", "") in ["可处置", "需要审批处置"]:
                stage = "待处置"
            elif tier == "hot":
                stage = "使用"
            elif tier == "cold":
                stage = "归档"
            else:
                stage = "使用"
            
            if stage in stage_counts:
                stage_counts[stage] += 1
            else:
                stage_counts[stage] = 1
        
        return {
            "labels": list(stage_counts.keys()),
            "values": list(stage_counts.values())
        }
    
    def _generate_alerts(self, analysis_results):
        """生成预警信息"""
        alerts = []
        
        # 存储利用率预警
        storage_distribution = self._prepare_storage_distribution_data()
        total_size = sum(storage_distribution["values"])
        hot_storage_size = storage_distribution["values"][0]  # 假设第一个是hot存储
        hot_utilization = (hot_storage_size / total_size) * 100 if total_size > 0 else 0
        
        if hot_utilization > self.alert_thresholds["storage_utilization"]:
            alerts.append(f"热存储利用率({hot_utilization:.1f}%)超过阈值({self.alert_thresholds['storage_utilization']}%)")
        
        # 合规性预警
        compliance_analysis = analysis_results["retention_compliance"]
        compliance_rate = compliance_analysis["retention_summary"]["compliance_rate"]
        
        if compliance_rate < self.alert_thresholds["retention_compliance"]:
            alerts.append(f"数据保留合规率({compliance_rate:.1f}%)低于阈值({self.alert_thresholds['retention_compliance']}%)")
        
        return alerts

def main():
    """主函数"""
    print("=" * 50)
    print("数据生命周期管理系统")
    print("=" * 50)
    
    # 创建数据生命周期管理器
    lifecycle_manager = DataLifecycleManager()
    
    # 注册示例数据资产
    sample_data = [
        {"id": "CUST001", "name": "客户基本信息表", "type": "customer_data", "owner": "销售部", "size_gb": 50, "classification": "内部", "storage_location": "数据库服务器A", "creation_date": "2020-01-15", "business_value": "高", "access_pattern": "frequent"},
        {"id": "TRANS001", "name": "交易记录表", "type": "transaction_data", "owner": "财务部", "size_gb": 200, "classification": "机密", "storage_location": "数据库服务器B", "creation_date": "2018-03-20", "business_value": "高", "access_pattern": "regular"},
        {"id": "ANAL001", "name": "用户行为分析数据", "type": "analytics_data", "owner": "数据团队", "size_gb": 300, "classification": "内部", "storage_location": "数据仓库", "creation_date": "2019-05-10", "business_value": "中", "access_pattern": "occasional"},
        {"id": "EMPL001", "name": "员工信息表", "type": "employee_data", "owner": "人力资源部", "size_gb": 20, "classification": "机密", "storage_location": "HR系统", "creation_date": "2017-08-25", "business_value": "高", "access_pattern": "rare"},
        {"id": "EMAIL001", "name": "历史邮件归档", "type": "email_communications", "owner": "IT部门", "size_gb": 500, "classification": "内部", "storage_location": "邮件服务器", "creation_date": "2017-01-05", "business_value": "低", "access_pattern": "rare"},
        {"id": "PROD001", "name": "产品销售数据", "type": "analytics_data", "owner": "产品部", "size_gb": 150, "classification": "内部公开", "storage_location": "商业智能平台", "creation_date": "2021-02-14", "business_value": "高", "access_pattern": "regular"},
        {"id": "FINC001", "name": "财务报表数据", "type": "financial_data", "owner": "财务部", "size_gb": 80, "classification": "机密", "storage_location": "财务系统", "creation_date": "2019-11-30", "business_value": "高", "access_pattern": "frequent"},
        {"id": "MKTG001", "name": "营销活动数据", "type": "analytics_data", "owner": "市场部", "size_gb": 120, "classification": "内部", "storage_location": "营销系统", "creation_date": "2020-07-22", "business_value": "中", "access_pattern": "occasional"}
    ]
    
    print("注册数据资产...")
    for data in sample_data:
        lifecycle_manager.register_data_asset(**data)
    
    print(f"已注册 {len(lifecycle_manager.data_inventory)} 个数据资产")
    
    # 模拟使用模式
    print("\n模拟使用模式...")
    result = lifecycle_manager.simulate_usage_patterns(days=60)
    print(result)
    
    # 运行生命周期分析
    print("\n运行生命周期分析...")
    analysis_results = lifecycle_manager.run_lifecycle_analysis()
    
    print(f"\n存储优化机会: {len(analysis_results['storage_optimization'])}")
    print(f"合规性问题: {len(analysis_results['retention_compliance']['non_compliant_items'])}")
    print(f"潜在月度成本节约: {analysis_results['cost_optimization']['total_savings']:.2f}元")
    
    # 显示主要推荐
    print("\n主要推荐:")
    for i, rec in enumerate(analysis_results['recommendations'][:5]):  # 只显示前5个推荐
        print(f"{i+1}. [{rec['priority']}] {rec['action']} - {rec['details']}")
        print(f"   预估节约: {rec['estimated_savings']:.2f}元 | 自动化: {'是' if rec['automation_ready'] else '否'} | 需审批: {'是' if rec['requires_approval'] else '否'}")
    
    # 生成并显示仪表板
    print("\n生成生命周期仪表板...")
    dashboard_data = lifecycle_manager.generate_lifecycle_dashboard(analysis_results)
    dashboard_result = lifecycle_manager.visualize_lifecycle_dashboard(dashboard_data)
    print(dashboard_result)
    
    # 显示预警信息
    if dashboard_data['alerts']:
        print("\n预警信息:")
        for alert in dashboard_data['alerts']:
            print(f"- {alert}")
    else:
        print("\n当前无预警信息")
    
    print("\n分析完成!")

if __name__ == "__main__":
    main()