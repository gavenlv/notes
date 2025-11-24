#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据归档策略工具
功能：实现数据归档策略的制定和执行，识别归档候选，创建归档计划
作者：数据治理团队
日期：2023-11-23
"""

import pandas as pd
import numpy as np
import datetime
import json
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class DataArchiveStrategy:
    """数据归档策略类"""
    
    def __init__(self):
        self.archive_criteria = {
            "time_based": {
                "transactional_data": 36,  # 36个月后归档
                "customer_data": 60,       # 60个月后归档
                "financial_data": 84,      # 84个月后归档
                "analytics_data": 24,      # 24个月后归档
                "email_data": 48          # 48个月后归档
            },
            "access_frequency": {
                "low": 30,    # 30天内访问少于1次
                "medium": 90,  # 90天内访问少于3次
                "high": 365    # 365天内访问少于10次
            },
            "business_value": {
                "critical": "不归档或特殊归档",
                "important": "长期保留",
                "useful": "标准归档",
                "minimal": "快速归档或删除"
            }
        }
        
        self.archive_storage = {
            "standard": {
                "cost_factor": 0.3,  # 相对于热存储的成本比例
                "access_time": "分钟级",
                "recovery_time": "小时级",
                "suitability": "一般业务数据"
            },
            "deep": {
                "cost_factor": 0.1,
                "access_time": "小时级",
                "recovery_time": "天级",
                "suitability": "历史数据、备份数据"
            },
            "cold": {
                "cost_factor": 0.05,
                "access_time": "天级",
                "recovery_time": "周级",
                "suitability": "极少访问的数据"
            }
        }
    
    def identify_candidates_for_archiving(self, data_inventory):
        """识别归档候选数据"""
        candidates = []
        current_date = datetime.datetime.now()
        
        for data_item in data_inventory:
            # 时间标准检查
            data_type = data_item.get("type", "analytics_data")
            age_months = (current_date - datetime.datetime.strptime(
                data_item.get("created_date", current_date.strftime("%Y-%m-%d")), 
                "%Y-%m-%d"
            )).days // 30
            
            time_based_eligible = age_months >= self.archive_criteria["time_based"].get(data_type, 24)
            
            # 访问频率检查
            access_count = data_item.get("access_count_last_90_days", 0)
            access_based_eligible = access_count <= self.archive_criteria["access_frequency"]["low"]
            
            # 业务价值检查
            business_value = data_item.get("business_value", "useful")
            business_value_eligible = business_value in ["useful", "minimal"]
            
            # 综合判断
            if (time_based_eligible and access_based_eligible and business_value_eligible) or \
               (age_months >= self.archive_criteria["time_based"].get(data_type, 24) * 1.5):
                
                # 推荐归档存储类型
                archive_type = self._recommend_archive_type(data_item)
                
                candidates.append({
                    "data_id": data_item["id"],
                    "data_name": data_item.get("name", "未知"),
                    "data_type": data_type,
                    "age_months": age_months,
                    "access_count_last_90_days": access_count,
                    "business_value": business_value,
                    "size_gb": data_item.get("size_gb", 0),
                    "recommended_archive_type": archive_type,
                    "estimated_monthly_savings": data_item.get("size_gb", 0) * self.archive_storage[archive_type]["cost_factor"],
                    "last_access_date": data_item.get("last_access_date", "未知")
                })
        
        # 按预期节省金额排序
        candidates.sort(key=lambda x: x["estimated_monthly_savings"], reverse=True)
        
        return candidates
    
    def _recommend_archive_type(self, data_item):
        """推荐归档存储类型"""
        access_count = data_item.get("access_count_last_90_days", 0)
        business_value = data_item.get("business_value", "useful")
        
        if access_count == 0 and business_value == "minimal":
            return "cold"
        elif access_count <= 3:
            return "deep"
        else:
            return "standard"
    
    def create_archive_plan(self, candidates, budget_constraint=None, capacity_constraint=None):
        """创建归档计划"""
        plan = {
            "selected_for_archiving": [],
            "estimated_monthly_savings": 0,
            "total_size_to_archive": 0,
            "implementation_schedule": [],
            "unselected_reasons": {}
        }
        
        total_size = 0
        total_savings = 0
        
        for candidate in candidates:
            size = candidate["size_gb"]
            savings = candidate["estimated_monthly_savings"]
            
            # 检查预算约束
            if budget_constraint and total_size + size > budget_constraint:
                plan["unselected_reasons"][candidate["data_id"]] = "超出预算约束"
                continue
            
            # 检查容量约束
            if capacity_constraint and total_size + size > capacity_constraint:
                plan["unselected_reasons"][candidate["data_id"]] = "超出容量约束"
                continue
            
            plan["selected_for_archiving"].append(candidate)
            total_size += size
            total_savings += savings
        
        plan["estimated_monthly_savings"] = total_savings
        plan["total_size_to_archive"] = total_size
        
        # 创建实施计划
        plan["implementation_schedule"] = self._create_implementation_schedule(
            plan["selected_for_archiving"]
        )
        
        return plan
    
    def _create_implementation_schedule(self, selected_items):
        """创建实施计划"""
        # 按大小和业务影响排序
        sorted_items = sorted(selected_items, 
                            key=lambda x: (x.get("business_impact", "medium"), x["size_gb"]),
                            reverse=True)
        
        schedule = []
        weekly_capacity = 1000  # 每周可归档的数据量(GB)
        current_week = 1
        current_week_size = 0
        current_week_items = []
        
        for item in sorted_items:
            if current_week_size + item["size_gb"] <= weekly_capacity:
                current_week_items.append(item)
                current_week_size += item["size_gb"]
            else:
                if current_week_items:
                    schedule.append({
                        "week": current_week,
                        "items": current_week_items,
                        "total_size": current_week_size
                    })
                    current_week += 1
                    current_week_size = item["size_gb"]
                    current_week_items = [item]
        
        # 添加最后一周的项目
        if current_week_items:
            schedule.append({
                "week": current_week,
                "items": current_week_items,
                "total_size": current_week_size
            })
        
        return schedule
    
    def simulate_archive_execution(self, archive_plan):
        """模拟归档执行"""
        execution_log = {
            "execution_id": f"archive_exec_{int(datetime.datetime.now().timestamp())}",
            "start_time": datetime.datetime.now().isoformat(),
            "total_items_planned": len(archive_plan["selected_for_archiving"]),
            "total_size_planned": archive_plan["total_size_to_archive"],
            "planned_savings": archive_plan["estimated_monthly_savings"],
            "weekly_results": [],
            "overall_summary": {}
        }
        
        total_executed = 0
        total_size_executed = 0
        total_failures = 0
        
        for week_schedule in archive_plan["implementation_schedule"]:
            week = week_schedule["week"]
            items = week_schedule["items"]
            planned_size = week_schedule["total_size"]
            
            # 模拟本周执行情况(95%成功率)
            success_rate = 0.95
            successful_items = []
            failed_items = []
            
            executed_size = 0
            for item in items:
                if random.random() < success_rate:
                    successful_items.append(item)
                    executed_size += item["size_gb"]
                else:
                    failed_items.append(item)
                    total_failures += 1
            
            week_result = {
                "week": week,
                "planned_items": len(items),
                "successful_items": len(successful_items),
                "failed_items": len(failed_items),
                "planned_size_gb": planned_size,
                "executed_size_gb": executed_size,
                "execution_rate": len(successful_items) / len(items) * 100 if items else 0,
                "size_execution_rate": executed_size / planned_size * 100 if planned_size > 0 else 0,
                "estimated_savings_this_week": sum(item["estimated_monthly_savings"] for item in successful_items)
            }
            
            execution_log["weekly_results"].append(week_result)
            total_executed += len(successful_items)
            total_size_executed += executed_size
        
        # 生成总体摘要
        execution_log["end_time"] = datetime.datetime.now().isoformat()
        execution_log["overall_summary"] = {
            "items_executed": total_executed,
            "items_failed": total_failures,
            "size_executed_gb": total_size_executed,
            "size_failure_gb": archive_plan["total_size_to_archive"] - total_size_executed,
            "overall_item_success_rate": total_executed / archive_plan["total_items_planned"] * 100,
            "overall_size_success_rate": total_size_executed / archive_plan["total_size_to_archive"] * 100,
            "actual_monthly_savings": sum(week["estimated_savings_this_week"] for week in execution_log["weekly_results"]),
            "planned_vs_actual_savings": sum(week["estimated_savings_this_week"] for week in execution_log["weekly_results"]) / archive_plan["estimated_monthly_savings"] * 100
        }
        
        return execution_log
    
    def visualize_archive_plan(self, archive_plan, execution_log=None):
        """可视化归档计划"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('数据归档计划分析', fontsize=16)
        
        # 1. 每周归档量图
        weeks = [f"第{week['week']}周" for week in archive_plan["implementation_schedule"]]
        sizes = [week["total_size"] for week in archive_plan["implementation_schedule"]]
        
        axes[0, 0].bar(weeks, sizes, color='skyblue')
        axes[0, 0].set_title('每周归档数据量计划')
        axes[0, 0].set_ylabel('数据量(GB)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. 归档类型分布图
        if archive_plan["selected_for_archiving"]:
            archive_types = {}
            for item in archive_plan["selected_for_archiving"]:
                archive_type = item["recommended_archive_type"]
                archive_types[archive_type] = archive_types.get(archive_type, 0) + item["size_gb"]
            
            axes[0, 1].pie(list(archive_types.values()), labels=list(archive_types.keys()), 
                         autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('归档存储类型分布')
        else:
            axes[0, 1].text(0.5, 0.5, '无归档数据', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('归档存储类型分布')
        
        # 3. 成本节约分析图
        data_ids = [item["data_id"][:8] + "..." for item in archive_plan["selected_for_archiving"][:10]]  # 只显示前10个
        savings = [item["estimated_monthly_savings"] for item in archive_plan["selected_for_archiving"][:10]]
        
        axes[1, 0].bar(data_ids, savings, color='green')
        axes[1, 0].set_title('前10个归档项目的月度成本节约')
        axes[1, 0].set_ylabel('节约金额(元)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 执行结果(如果有执行日志)
        if execution_log:
            weeks = [f"第{week['week']}周" for week in execution_log["weekly_results"]]
            success_rates = [week["execution_rate"] for week in execution_log["weekly_results"]]
            
            axes[1, 1].plot(weeks, success_rates, marker='o', color='red')
            axes[1, 1].set_title('每周归档执行成功率')
            axes[1, 1].set_ylabel('执行成功率(%)')
            axes[1, 1].set_ylim(0, 100)
            axes[1, 1].tick_params(axis='x', rotation=45)
        else:
            axes[1, 1].text(0.5, 0.5, '尚无执行结果', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('归档执行结果')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig('data_archive_plan.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return "归档计划图表已保存为 data_archive_plan.png"
    
    def generate_archive_report(self, archive_plan, execution_log=None):
        """生成归档报告"""
        report = {
            "report_id": f"archive_report_{int(datetime.datetime.now().timestamp())}",
            "generated_at": datetime.datetime.now().isoformat(),
            "plan_summary": {
                "total_items": len(archive_plan["selected_for_archiving"]),
                "total_size_gb": archive_plan["total_size_to_archive"],
                "estimated_monthly_savings": archive_plan["estimated_monthly_savings"],
                "implementation_weeks": len(archive_plan["implementation_schedule"])
            },
            "implementation_schedule": archive_plan["implementation_schedule"],
            "execution_results": None,
            "recommendations": []
        }
        
        # 添加执行结果(如果有)
        if execution_log:
            report["execution_results"] = {
                "execution_summary": execution_log["overall_summary"],
                "weekly_details": execution_log["weekly_results"]
            }
            
            # 基于执行结果添加推荐
            if execution_log["overall_summary"]["overall_item_success_rate"] < 95:
                report["recommendations"].append("归档执行成功率偏低，建议增加预处理和测试时间")
            
            if execution_log["overall_summary"]["overall_size_success_rate"] < 90:
                report["recommendations"].append("部分大数据集归档失败，建议优化大数据集归档流程")
        
        # 添加一般推荐
        if archive_plan["estimated_monthly_savings"] > 10000:
            report["recommendations"].append("归档成本节约显著，建议考虑扩大归档范围")
        
        if len(archive_plan["unselected_reasons"]) > 0:
            report["recommendations"].append("部分数据因约束条件未能归档，建议重新评估约束条件")
        
        return report

def generate_sample_data_inventory():
    """生成示例数据清单"""
    current_date = datetime.datetime.now()
    inventory = []
    
    sample_data = [
        {"id": "DATA001", "name": "2020年客户交易记录", "type": "transactional_data", "size_gb": 150, 
         "business_value": "useful", "access_count_last_90_days": 2,
         "created_date": (current_date - datetime.timedelta(days=1000)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=45)).strftime("%Y-%m-%d")},
        
        {"id": "DATA002", "name": "2019年销售分析报告", "type": "analytics_data", "size_gb": 50,
         "business_value": "minimal", "access_count_last_90_days": 0,
         "created_date": (current_date - datetime.timedelta(days=1200)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=300)).strftime("%Y-%m-%d")},
         
        {"id": "DATA003", "name": "2018年客户行为数据", "type": "customer_data", "size_gb": 200,
         "business_value": "useful", "access_count_last_90_days": 1,
         "created_date": (current_date - datetime.timedelta(days=1800)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=120)).strftime("%Y-%m-%d")},
         
        {"id": "DATA004", "name": "2021年产品使用日志", "type": "analytics_data", "size_gb": 80,
         "business_value": "important", "access_count_last_90_days": 15,
         "created_date": (current_date - datetime.timedelta(days=600)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=10)).strftime("%Y-%m-%d")},
         
        {"id": "DATA005", "name": "2017年财务报表数据", "type": "financial_data", "size_gb": 120,
         "business_value": "important", "access_count_last_90_days": 0,
         "created_date": (current_date - datetime.timedelta(days=2100)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=500)).strftime("%Y-%m-%d")},
         
        {"id": "DATA006", "name": "2019年邮件归档", "type": "email_data", "size_gb": 300,
         "business_value": "minimal", "access_count_last_90_days": 0,
         "created_date": (current_date - datetime.timedelta(days=1400)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days)=400).strftime("%Y-%m-%d")},
         
        {"id": "DATA007", "name": "2018年客户服务记录", "type": "customer_data", "size_gb": 90,
         "business_value": "useful", "access_count_last_90_days": 5,
         "created_date": (current_date - datetime.timedelta(days=1600)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=60)).strftime("%Y-%m-%d")},
         
        {"id": "DATA008", "name": "2020年系统操作日志", "type": "analytics_data", "size_gb": 250,
         "business_value": "minimal", "access_count_last_90_days": 1,
         "created_date": (current_date - datetime.timedelta(days=900)).strftime("%Y-%m-%d"),
         "last_access_date": (current_date - datetime.timedelta(days=30)).strftime("%Y-%m-%d")},
    ]
    
    for data in sample_data:
        inventory.append(data)
    
    return inventory

def main():
    """主函数"""
    print("=" * 50)
    print("数据归档策略工具")
    print("=" * 50)
    
    # 创建归档策略工具
    archive_strategy = DataArchiveStrategy()
    
    # 生成示例数据清单
    print("生成示例数据清单...")
    data_inventory = generate_sample_data_inventory()
    print(f"生成了 {len(data_inventory)} 个数据资产")
    
    # 识别归档候选
    print("\n识别归档候选数据...")
    candidates = archive_strategy.identify_candidates_for_archiving(data_inventory)
    print(f"识别到 {len(candidates)} 个归档候选数据")
    
    # 显示候选数据摘要
    if candidates:
        print("\n候选数据摘要:")
        for i, candidate in enumerate(candidates[:5]):  # 只显示前5个
            print(f"{i+1}. ID: {candidate['data_id']}, 名称: {candidate['data_name']}")
            print(f"   类型: {candidate['data_type']}, 大小: {candidate['size_gb']}GB, "
                  f"月度节约: {candidate['estimated_monthly_savings']:.2f}元")
    
    # 创建归档计划
    print("\n创建归档计划...")
    archive_plan = archive_strategy.create_archive_plan(candidates)
    
    print(f"\n归档计划摘要:")
    print(f"- 选中归档项目数: {len(archive_plan['selected_for_archiving'])}")
    print(f"- 总归档数据量: {archive_plan['total_size_to_archive']}GB")
    print(f"- 预计月度成本节约: {archive_plan['estimated_monthly_savings']:.2f}元")
    print(f"- 实施周数: {len(archive_plan['implementation_schedule'])}")
    
    # 模拟执行归档
    print("\n模拟归档执行...")
    execution_log = archive_strategy.simulate_archive_execution(archive_plan)
    
    print(f"\n归档执行摘要:")
    summary = execution_log["overall_summary"]
    print(f"- 项目执行成功率: {summary['overall_item_success_rate']:.1f}%")
    print(f"- 数据量执行成功率: {summary['overall_size_success_rate']:.1f}%")
    print(f"- 实际月度节约: {summary['actual_monthly_savings']:.2f}元")
    print(f"- 计划vs实际节约率: {summary['planned_vs_actual_savings']:.1f}%")
    
    # 可视化归档计划
    print("\n生成归档计划可视化...")
    viz_result = archive_strategy.visualize_archive_plan(archive_plan, execution_log)
    print(viz_result)
    
    # 生成归档报告
    print("\n生成归档报告...")
    report = archive_strategy.generate_archive_report(archive_plan, execution_log)
    report_file = f"archive_report_{int(datetime.datetime.now().timestamp())}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"归档报告已保存为 {report_file}")
    print("\n报告摘要:")
    print(f"- 总项目数: {report['plan_summary']['total_items']}")
    print(f"- 总数据量: {report['plan_summary']['total_size_gb']}GB")
    print(f"- 预计月度节约: {report['plan_summary']['estimated_monthly_savings']:.2f}元")
    print(f"- 实施周数: {report['plan_summary']['implementation_weeks']}")
    
    if report['recommendations']:
        print("\n推荐措施:")
        for i, rec in enumerate(report['recommendations']):
            print(f"{i+1}. {rec}")
    
    print("\n分析完成!")

if __name__ == "__main__":
    # 需要导入random模块
    import random
    main()