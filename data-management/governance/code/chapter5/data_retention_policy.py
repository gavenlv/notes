#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据保留政策工具
功能：实现数据保留政策管理，合规性评估，法律保留申请，处置计划制定
作者：数据治理团队
日期：2023-11-23
"""

import pandas as pd
import numpy as np
import datetime
import json
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class DataRetentionPolicyTool:
    """数据保留政策工具类"""
    
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
        
        self.hold_reasons = {
            "legal_hold": "法律诉讼或监管调查",
            "audit_hold": "内部或外部审计",
            "regulatory_hold": "监管调查",
            "business_hold": "业务需要延长保留"
        }
    
    def assess_retention_compliance(self, data_inventory):
        """评估保留合规性"""
        compliance_report = {
            "compliant_items": [],
            "non_compliant_items": [],
            "items_nearing_disposal": [],
            "items_on_hold": [],
            "retention_summary": {},
            "compliance_by_type": {}
        }
        
        current_date = datetime.datetime.now()
        
        for data_item in data_inventory:
            data_type = data_item.get("type", "unknown")
            creation_date = datetime.datetime.strptime(
                data_item.get("created_date", current_date.strftime("%Y-%m-%d")), 
                "%Y-%m-%d"
            )
            
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
                    "data_type": data_type,
                    "age_days": age_days,
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
                    "status": "未到最低保留期",
                    "days_until_min": min_retention - age_days
                })
            elif age_days >= min_retention and age_days < max_retention:
                compliance_report["compliant_items"].append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "data_type": data_type,
                    "age_days": age_days,
                    "min_retention_days": min_retention,
                    "max_retention_days": max_retention,
                    "status": "合规保留中",
                    "days_until_disposal": max_retention - age_days
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
                    "disposal_method": rule["disposal_method"],
                    "days_over_retention": age_days - max_retention
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
        total_items = len(data_inventory)
        compliant_count = len(compliance_report["compliant_items"])
        non_compliant_count = len(compliance_report["non_compliant_items"])
        nearing_disposal_count = len(compliance_report["items_nearing_disposal"])
        on_hold_count = len(compliance_report["items_on_hold"])
        
        compliance_report["retention_summary"] = {
            "total_items": total_items,
            "compliant_items": compliant_count,
            "non_compliant_items": non_compliant_count,
            "items_nearing_disposal": nearing_disposal_count,
            "items_on_hold": on_hold_count,
            "compliance_rate": compliant_count / total_items * 100 if total_items > 0 else 0,
            "over_retention_items": len([item for item in compliance_report["non_compliant_items"] if item["status"] in ["可处置", "需要审批处置"]])
        }
        
        # 按数据类型统计合规性
        compliance_by_type = {}
        for data_type in self.retention_rules.keys():
            type_items = [item for item in data_inventory if item.get("type") == data_type]
            type_total = len(type_items)
            if type_total > 0:
                type_compliant = len([item for item in compliance_report["compliant_items"] if item["data_type"] == data_type])
                type_non_compliant = len([item for item in compliance_report["non_compliant_items"] if item["data_type"] == data_type])
                
                compliance_by_type[data_type] = {
                    "total": type_total,
                    "compliant": type_compliant,
                    "non_compliant": type_non_compliant,
                    "compliance_rate": type_compliant / type_total * 100
                }
        
        compliance_report["compliance_by_type"] = compliance_by_type
        
        return compliance_report
    
    def apply_legal_hold(self, data_ids, hold_reason, hold_duration_days=None, requested_by=""):
        """应用法律保留"""
        hold_requests = []
        
        if hold_reason not in self.hold_reasons:
            return {"error": f"无效的保留原因。有效原因: {list(self.hold_reasons.keys())}"}
        
        for data_id in data_ids:
            hold_expiry = None
            if hold_duration_days:
                expiry_date = datetime.datetime.now() + datetime.timedelta(days=hold_duration_days)
                hold_expiry = expiry_date.strftime("%Y-%m-%d")
            
            hold_request = {
                "data_id": data_id,
                "hold_id": f"hold_{int(datetime.datetime.now().timestamp())}_{data_id}",
                "hold_reason": hold_reason,
                "hold_applied_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "hold_expiry_date": hold_expiry,
                "requested_by": requested_by,
                "status": "已应用",
                "notes": self.hold_reasons[hold_reason]
            }
            
            hold_requests.append(hold_request)
        
        return hold_requests
    
    def plan_disposal_activities(self, items_for_disposal):
        """规划处置活动"""
        disposal_plan = {
            "immediate_disposal": [],
            "approval_required": [],
            "disposal_timeline": {},
            "estimated_disposal_volume": 0,
            "disposal_methods_summary": {}
        }
        
        total_volume = 0
        disposal_methods_count = {}
        
        for item in items_for_disposal:
            data_type = item.get("data_type", "unknown")
            rule = self.retention_rules.get(data_type, {})
            disposal_method = rule.get("disposal_method", "删除")
            approval_required = rule.get("disapproval_required", False)
            
            volume = item.get("size_gb", 0)
            total_volume += volume
            
            # 计数处置方法
            if disposal_method not in disposal_methods_count:
                disposal_methods_count[disposal_method] = {"count": 0, "volume": 0}
            disposal_methods_count[disposal_method]["count"] += 1
            disposal_methods_count[disposal_method]["volume"] += volume
            
            if approval_required:
                disposal_plan["approval_required"].append({
                    "data_id": item["data_id"],
                    "data_name": item.get("data_name", "未知"),
                    "data_type": data_type,
                    "disposal_method": disposal_method,
                    "volume": volume,
                    "reason": item.get("reason", "超过最大保留期"),
                    "age_days": item.get("age_days", 0)
                })
            else:
                disposal_plan["immediate_disposal"].append({
                    "data_id": item["data_id"],
                    "data_name": item.get("data_name", "未知"),
                    "data_type": data_type,
                    "disposal_method": disposal_method,
                    "volume": volume,
                    "age_days": item.get("age_days", 0)
                })
        
        # 创建处置时间线
        disposal_plan["disposal_timeline"] = self._create_disposal_timeline(
            disposal_plan["immediate_disposal"],
            disposal_plan["approval_required"]
        )
        
        disposal_plan["estimated_disposal_volume"] = total_volume
        disposal_plan["disposal_methods_summary"] = disposal_methods_count
        
        return disposal_plan
    
    def _create_disposal_timeline(self, immediate_items, approval_items):
        """创建处置时间线"""
        # 创建4周的时间线
        timeline = {
            "week_1": {"items": [], "volume": 0},
            "week_2": {"items": [], "volume": 0},
            "week_3": {"items": [], "volume": 0},
            "week_4": {"items": [], "volume": 0}
        }
        
        # 第一周：处置不需要审批的小型数据项
        week1_items = [item for item in immediate_items if item["volume"] <= 100]
        for item in week1_items[:10]:  # 限制为10项以避免超载
            timeline["week_1"]["items"].append(item)
            timeline["week_1"]["volume"] += item["volume"]
        
        # 第二周：处置需要审批的小型数据项
        week2_items = [item for item in approval_items if item["volume"] <= 50]
        for item in week2_items[:5]:  # 限制为5项
            timeline["week_2"]["items"].append(item)
            timeline["week_2"]["volume"] += item["volume"]
        
        # 第三周：处置不需要审批的中型数据项
        week3_items = [item for item in immediate_items if item["volume"] > 100 and item["volume"] <= 500]
        for item in week3_items[:5]:  # 限制为5项
            timeline["week_3"]["items"].append(item)
            timeline["week_3"]["volume"] += item["volume"]
        
        # 第四周：处置大型数据项和剩余项目
        remaining_immediate = [item for item in immediate_items if item not in timeline["week_1"]["items"] and item not in timeline["week_3"]["items"]]
        remaining_approval = [item for item in approval_items if item not in timeline["week_2"]["items"]]
        
        for item in remaining_immediate[:3]:  # 限制为3项
            timeline["week_4"]["items"].append(item)
            timeline["week_4"]["volume"] += item["volume"]
        
        for item in remaining_approval[:2]:  # 限制为2项
            timeline["week_4"]["items"].append(item)
            timeline["week_4"]["volume"] += item["volume"]
        
        return timeline
    
    def visualize_compliance_status(self, compliance_report):
        """可视化合规状态"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('数据保留合规性分析', fontsize=16)
        
        # 1. 合规性状态饼图
        summary = compliance_report["retention_summary"]
        labels = ['合规', '不合规', '接近处置', '保留锁定']
        sizes = [
            summary["compliant_items"],
            summary["non_compliant_items"],
            summary["items_nearing_disposal"],
            summary["items_on_hold"]
        ]
        colors = ['green', 'red', 'orange', 'blue']
        
        axes[0, 0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('数据保留合规状态分布')
        
        # 2. 按数据类型的合规性
        if compliance_report["compliance_by_type"]:
            types = list(compliance_report["compliance_by_type"].keys())
            compliance_rates = [
                compliance_report["compliance_by_type"][t]["compliance_rate"] 
                for t in types
            ]
            
            axes[0, 1].bar(types, compliance_rates, color='skyblue')
            axes[0, 1].set_title('各数据类型合规率')
            axes[0, 1].set_ylabel('合规率(%)')
            axes[0, 1].set_ylim(0, 100)
            axes[0, 1].tick_params(axis='x', rotation=45)
        else:
            axes[0, 1].text(0.5, 0.5, '无数据类型信息', ha='center', va='center', 
                          transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('各数据类型合规率')
        
        # 3. 不合规数据年龄分布
        if compliance_report["non_compliant_items"]:
            over_retention_items = [
                item for item in compliance_report["non_compliant_items"] 
                if "days_over_retention" in item
            ]
            
            if over_retention_items:
                ages = [item["age_days"] for item in over_retention_items]
                over_days = [item["days_over_retention"] for item in over_retention_items]
                
                axes[1, 0].scatter(ages, over_days, alpha=0.7, color='red')
                axes[1, 0].set_title('不合规数据年龄与超期天数分布')
                axes[1, 0].set_xlabel('数据年龄(天)')
                axes[1, 0].set_ylabel('超期天数(天)')
            else:
                axes[1, 0].text(0.5, 0.5, '无超期数据', ha='center', va='center', 
                              transform=axes[1, 0].transAxes)
                axes[1, 0].set_title('不合规数据年龄与超期天数分布')
        else:
            axes[1, 0].text(0.5, 0.5, '无不合规数据', ha='center', va='center', 
                          transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('不合规数据年龄与超期天数分布')
        
        # 4. 接近处置期的项目
        if compliance_report["items_nearing_disposal"]:
            items = compliance_report["items_nearing_disposal"]
            names = [item["data_id"][:8] + "..." for item in items[:10]]  # 只显示前10个
            days = [item["days_until_disposal"] for item in items[:10]]
            
            axes[1, 1].barh(names, days, color='orange')
            axes[1, 1].set_title('接近处置期的数据(前10项)')
            axes[1, 1].set_xlabel('距离处置天数')
        else:
            axes[1, 1].text(0.5, 0.5, '无接近处置期的数据', ha='center', va='center', 
                          transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('接近处置期的数据')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig('data_retention_compliance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return "合规性分析图表已保存为 data_retention_compliance.png"
    
    def generate_retention_report(self, compliance_report, disposal_plan=None):
        """生成保留合规报告"""
        report = {
            "report_id": f"retention_report_{int(datetime.datetime.now().timestamp())}",
            "generated_at": datetime.datetime.now().isoformat(),
            "compliance_summary": compliance_report["retention_summary"],
            "compliance_by_type": compliance_report["compliance_by_type"],
            "compliant_items": compliance_report["compliant_items"][:10],  # 只包含前10项
            "non_compliant_items": compliance_report["non_compliant_items"][:10],  # 只包含前10项
            "items_nearing_disposal": compliance_report["items_nearing_disposal"][:10],  # 只包含前10项
            "items_on_hold": compliance_report["items_on_hold"][:10],  # 只包含前10项
            "disposal_plan": disposal_plan,
            "recommendations": self._generate_recommendations(compliance_report)
        }
        
        return report
    
    def _generate_recommendations(self, compliance_report):
        """生成推荐措施"""
        recommendations = []
        
        summary = compliance_report["retention_summary"]
        
        # 总体合规率推荐
        if summary["compliance_rate"] < 80:
            recommendations.append({
                "priority": "高",
                "category": "整体合规性",
                "recommendation": "数据保留合规率低于80%，建议立即审查并改进数据保留政策执行"
            })
        elif summary["compliance_rate"] < 90:
            recommendations.append({
                "priority": "中",
                "category": "整体合规性",
                "recommendation": "数据保留合规率低于90%，建议定期审查数据保留政策执行情况"
            })
        
        # 超期数据推荐
        if summary["over_retention_items"] > 0:
            recommendations.append({
                "priority": "高",
                "category": "超期数据",
                "recommendation": f"发现{summary['over_retention_items']}项超期数据，建议立即启动处置流程"
            })
        
        # 接近处置期数据推荐
        if summary["items_nearing_disposal"] > 0:
            recommendations.append({
                "priority": "中",
                "category": "处置计划",
                "recommendation": f"发现{summary['items_nearing_disposal']}项即将达到处置期的数据，建议制定处置计划"
            })
        
        # 按类型合规性推荐
        for data_type, stats in compliance_report["compliance_by_type"].items():
            if stats["compliance_rate"] < 80:
                recommendations.append({
                    "priority": "中",
                    "category": "类型合规性",
                    "recommendation": f"{data_type}类型数据合规率仅为{stats['compliance_rate']:.1f}%，建议重点审查此类数据"
                })
        
        return recommendations

def generate_sample_data_inventory():
    """生成示例数据清单"""
    current_date = datetime.datetime.now()
    inventory = []
    
    sample_data = [
        {"id": "CUST001", "name": "客户基本信息表", "type": "customer_data", "size_gb": 50,
         "created_date": (current_date - datetime.timedelta(days=1000)).strftime("%Y-%m-%d"),
         "on_hold": False},
        
        {"id": "TRANS001", "name": "交易记录表", "type": "transaction_data", "size_gb": 200,
         "created_date": (current_date - datetime.timedelta(days=3000)).strftime("%Y-%m-%d"),
         "on_hold": False},
        
        {"id": "ANAL001", "name": "用户行为分析数据", "type": "analytics_data", "size_gb": 300,
         "created_date": (current_date - datetime.timedelta(days=1500)).strftime("%Y-%m-%d"),
         "on_hold": False},
        
        {"id": "EMPL001", "name": "员工信息表", "type": "employee_data", "size_gb": 20,
         "created_date": (current_date - datetime.timedelta(days=2000)).strftime("%Y-%m-%d"),
         "on_hold": False},
        
        {"id": "EMAIL001", "name": "历史邮件归档", "type": "email_communications", "size_gb": 500,
         "created_date": (current_date - datetime.timedelta(days=2500)).strftime("%Y-%m-%d"),
         "on_hold": False},
        
        {"id": "FINC001", "name": "财务报表数据", "type": "financial_data", "size_gb": 80,
         "created_date": (current_date - datetime.timedelta(days=1800)).strftime("%Y-%m-%d"),
         "on_hold": False},
        
        {"id": "LEGAL001", "name": "诉讼相关数据", "type": "customer_data", "size_gb": 120,
         "created_date": (current_date - datetime.timedelta(days=1200)).strftime("%Y-%m-%d"),
         "on_hold": True, "hold_reason": "法律诉讼", "hold_expiry": (current_date + datetime.timedelta(days=365)).strftime("%Y-%m-%d")},
         
        {"id": "AUDIT001", "name": "审计相关数据", "type": "transaction_data", "size_gb": 150,
         "created_date": (current_date - datetime.timedelta(days=800)).strftime("%Y-%m-%d"),
         "on_hold": True, "hold_reason": "审计", "hold_expiry": (current_date + datetime.timedelta(days=180)).strftime("%Y-%m-%d")},
         
        {"id": "OLD001", "name": "过期销售数据", "type": "analytics_data", "size_gb": 100,
         "created_date": (current_date - datetime.timedelta(days=2200)).strftime("%Y-%m-%d"),
         "on_hold": False},
         
        {"id": "NEW001", "name": "新产品分析数据", "type": "analytics_data", "size_gb": 60,
         "created_date": (current_date - datetime.timedelta(days=100)).strftime("%Y-%m-%d"),
         "on_hold": False}
    ]
    
    for data in sample_data:
        inventory.append(data)
    
    return inventory

def main():
    """主函数"""
    print("=" * 50)
    print("数据保留政策工具")
    print("=" * 50)
    
    # 创建保留政策工具
    retention_tool = DataRetentionPolicyTool()
    
    # 生成示例数据清单
    print("生成示例数据清单...")
    data_inventory = generate_sample_data_inventory()
    print(f"生成了 {len(data_inventory)} 个数据资产")
    
    # 评估保留合规性
    print("\n评估数据保留合规性...")
    compliance_report = retention_tool.assess_retention_compliance(data_inventory)
    
    # 显示合规性摘要
    summary = compliance_report["retention_summary"]
    print(f"\n合规性摘要:")
    print(f"- 总数据项: {summary['total_items']}")
    print(f"- 合规项: {summary['compliant_items']}")
    print(f"- 不合规项: {summary['non_compliant_items']}")
    print(f"- 接近处置期: {summary['items_nearing_disposal']}")
    print(f"- 保留锁定: {summary['items_on_hold']}")
    print(f"- 合规率: {summary['compliance_rate']:.1f}%")
    
    # 显示按类型的合规性
    print("\n各数据类型合规性:")
    for data_type, stats in compliance_report["compliance_by_type"].items():
        print(f"- {data_type}: {stats['compliant']}/{stats['total']} 项合规 ({stats['compliance_rate']:.1f}%)")
    
    # 显示不合规项目
    if compliance_report["non_compliant_items"]:
        print("\n不合规项目示例:")
        for i, item in enumerate(compliance_report["non_compliant_items"][:5]):  # 只显示前5个
            print(f"{i+1}. ID: {item['data_id']}, 名称: {item['data_name']}, 状态: {item['status']}")
    
    # 应用法律保留
    print("\n应用法律保留...")
    hold_data_ids = ["CUST001", "TRANS001"]  # 示例数据ID
    hold_result = retention_tool.apply_legal_hold(
        hold_data_ids, 
        "legal_hold", 
        hold_duration_days=365, 
        requested_by="法务部门"
    )
    
    print(f"应用了 {len(hold_result)} 个法律保留")
    for hold in hold_result:
        print(f"- 数据ID: {hold['data_id']}, 原因: {hold['hold_reason']}, 到期日期: {hold['hold_expiry_date']}")
    
    # 创建处置计划
    print("\n创建数据处置计划...")
    disposal_candidates = [
        {
            "data_id": item["data_id"],
            "data_name": item["data_name"],
            "data_type": item["data_type"],
            "age_days": item["age_days"],
            "size_gb": item.get("size_gb", 0),
            "reason": item["status"]
        }
        for item in compliance_report["non_compliant_items"]
        if item["status"] in ["可处置", "需要审批处置"]
    ]
    
    if disposal_candidates:
        disposal_plan = retention_tool.plan_disposal_activities(disposal_candidates)
        
        print(f"\n处置计划摘要:")
        print(f"- 立即处置项目: {len(disposal_plan['immediate_disposal'])}")
        print(f"- 需要审批项目: {len(disposal_plan['approval_required'])}")
        print(f"- 预计处置总量: {disposal_plan['estimated_disposal_volume']}GB")
        
        print("\n处置方法汇总:")
        for method, stats in disposal_plan["disposal_methods_summary"].items():
            print(f"- {method}: {stats['count']} 项, {stats['volume']}GB")
    
    # 可视化合规状态
    print("\n生成合规状态可视化...")
    viz_result = retention_tool.visualize_compliance_status(compliance_report)
    print(viz_result)
    
    # 生成保留报告
    print("\n生成数据保留合规报告...")
    report = retention_tool.generate_retention_report(compliance_report, disposal_plan if 'disposal_plan' in locals() else None)
    
    report_file = f"retention_compliance_report_{int(datetime.datetime.now().timestamp())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"合规报告已保存为 {report_file}")
    
    # 显示推荐措施
    if report["recommendations"]:
        print("\n推荐措施:")
        for i, rec in enumerate(report["recommendations"]):
            print(f"{i+1}. [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    else:
        print("\n当前无特别推荐措施")
    
    print("\n分析完成!")

if __name__ == "__main__":
    main()