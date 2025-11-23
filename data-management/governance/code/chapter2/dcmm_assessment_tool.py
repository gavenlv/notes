"""
第2章代码示例：DCMM数据管理能力成熟度评估工具
用于评估组织数据管理能力成熟度，制定改进计划
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

class DCMMAssessmentTool:
    """DCMM成熟度评估工具"""
    
    def __init__(self):
        # DCMM八大能力域
        self.capability_domains = {
            "数据战略": {
                "description": "制定和执行组织数据战略，确保数据管理与业务战略一致",
                "practices": {
                    "1级": [
                        "有基本的数据需求",
                        "有初步的数据应用"
                    ],
                    "2级": [
                        "有数据战略规划",
                        "有数据战略执行计划",
                        "有基本的资源配置"
                    ],
                    "3级": [
                        "有完整的数据战略体系",
                        "有战略评估机制",
                        "有战略优化流程"
                    ],
                    "4级": [
                        "有战略量化指标",
                        "有战略监控机制",
                        "有战略改进措施"
                    ],
                    "5级": [
                        "有战略创新能力",
                        "有战略引领作用",
                        "有最佳实践推广"
                    ]
                }
            },
            "数据治理": {
                "description": "建立数据治理组织、流程和制度，确保数据有序管理",
                "practices": {
                    "1级": [
                        "有基本的数据管理活动",
                        "有数据责任划分"
                    ],
                    "2级": [
                        "有数据治理组织",
                        "有数据治理制度",
                        "有数据治理流程"
                    ],
                    "3级": [
                        "有完善的治理体系",
                        "有制度执行监督",
                        "有治理效果评估"
                    ],
                    "4级": [
                        "有治理量化指标",
                        "有治理监控机制",
                        "有治理改进措施"
                    ],
                    "5级": [
                        "有治理创新能力",
                        "有治理最佳实践",
                        "有治理行业标准"
                    ]
                }
            },
            "数据架构": {
                "description": "设计和管理数据架构，确保数据结构合理和流转高效",
                "practices": {
                    "1级": [
                        "有基本的数据存储",
                        "有简单的数据应用"
                    ],
                    "2级": [
                        "有数据架构设计",
                        "有数据架构管理",
                        "有架构评估机制"
                    ],
                    "3级": [
                        "有完善的架构体系",
                        "有架构标准规范",
                        "有架构治理机制"
                    ],
                    "4级": [
                        "有架构量化指标",
                        "有架构监控机制",
                        "有架构优化措施"
                    ],
                    "5级": [
                        "有架构创新能力",
                        "有架构最佳实践",
                        "有架构行业标准"
                    ]
                }
            },
            "数据标准": {
                "description": "制定和实施数据标准，确保数据一致性和互操作性",
                "practices": {
                    "1级": [
                        "有基本的数据定义",
                        "有简单的数据规范"
                    ],
                    "2级": [
                        "有数据标准体系",
                        "有标准制定流程",
                        "有标准实施机制"
                    ],
                    "3级": [
                        "有完善的标准体系",
                        "有标准管理平台",
                        "有标准执行监督"
                    ],
                    "4级": [
                        "有标准量化指标",
                        "有标准监控机制",
                        "有标准改进措施"
                    ],
                    "5级": [
                        "有标准创新能力",
                        "有标准最佳实践",
                        "有标准行业标准"
                    ]
                }
            },
            "数据质量": {
                "description": "建立数据质量管理体系，确保数据满足业务需求",
                "practices": {
                    "1级": [
                        "有基本的数据检查",
                        "有简单的质量问题识别"
                    ],
                    "2级": [
                        "有数据质量标准",
                        "有质量检查流程",
                        "有质量改进措施"
                    ],
                    "3级": [
                        "有完善的质量体系",
                        "有质量监控机制",
                        "有质量评估机制"
                    ],
                    "4级": [
                        "有质量量化指标",
                        "有质量预测能力",
                        "有质量优化措施"
                    ],
                    "5级": [
                        "有质量创新能力",
                        "有质量最佳实践",
                        "有质量行业标准"
                    ]
                }
            },
            "数据安全": {
                "description": "建立数据安全管理体系，确保数据保密性、完整性和可用性",
                "practices": {
                    "1级": [
                        "有基本的安全措施",
                        "有简单的访问控制"
                    ],
                    "2级": [
                        "有数据安全策略",
                        "有安全管理制度",
                        "有安全技术措施"
                    ],
                    "3级": [
                        "有完善的安全体系",
                        "有安全管理平台",
                        "有安全监督机制"
                    ],
                    "4级": [
                        "有安全量化指标",
                        "有安全监控机制",
                        "有安全改进措施"
                    ],
                    "5级": [
                        "有安全创新能力",
                        "有安全最佳实践",
                        "有安全行业标准"
                    ]
                }
            },
            "数据应用": {
                "description": "开发和应用数据产品，发挥数据价值",
                "practices": {
                    "1级": [
                        "有基本的数据使用",
                        "有简单的数据分析"
                    ],
                    "2级": [
                        "有数据应用策略",
                        "有应用开发流程",
                        "有应用管理机制"
                    ],
                    "3级": [
                        "有完善的应用体系",
                        "有应用平台支撑",
                        "有应用评估机制"
                    ],
                    "4级": [
                        "有应用量化指标",
                        "有应用监控机制",
                        "有应用优化措施"
                    ],
                    "5级": [
                        "有应用创新能力",
                        "有应用最佳实践",
                        "有应用行业标准"
                    ]
                }
            },
            "数据生存周期": {
                "description": "管理数据全生命周期，确保数据有序流转和有效利用",
                "practices": {
                    "1级": [
                        "有基本的数据存储",
                        "有简单的数据使用"
                    ],
                    "2级": [
                        "有生命周期规划",
                        "有生命周期管理",
                        "有生命周期制度"
                    ],
                    "3级": [
                        "有完善的生命周期体系",
                        "有生命周期平台",
                        "有生命周期监督"
                    ],
                    "4级": [
                        "有生命周期量化指标",
                        "有生命周期监控",
                        "有生命周期优化"
                    ],
                    "5级": [
                        "有生命周期创新",
                        "有生命周期最佳实践",
                        "有生命周期行业标准"
                    ]
                }
            }
        }
    
    def assess_maturity_level(self, domain_scores):
        """
        根据各能力域得分计算整体成熟度等级
        
        Args:
            domain_scores: 各能力域得分字典 {domain: score}
            
        Returns:
            整体成熟度等级和各能力域等级
        """
        # 计算各能力域的成熟度等级
        domain_levels = {}
        for domain, score in domain_scores.items():
            if score <= 20:
                level = 1
            elif score <= 40:
                level = 2
            elif score <= 60:
                level = 3
            elif score <= 80:
                level = 4
            else:
                level = 5
            domain_levels[domain] = level
        
        # 计算整体成熟度等级
        overall_score = sum(domain_scores.values()) / len(domain_scores)
        if overall_score <= 20:
            overall_level = 1
        elif overall_score <= 40:
            overall_level = 2
        elif overall_score <= 60:
            overall_level = 3
        elif overall_score <= 80:
            overall_level = 4
        else:
            overall_level = 5
        
        return overall_level, domain_levels
    
    def generate_improvement_plan(self, domain_levels):
        """
        根据成熟度评估结果生成改进计划
        
        Args:
            domain_levels: 各能力域等级字典 {domain: level}
            
        Returns:
            改进计划字典
        """
        improvement_plan = {}
        
        for domain, current_level in domain_levels.items():
            target_level = min(current_level + 1, 5)  # 目标为下一级
            domain_info = self.capability_domains[domain]
            
            # 获取当前级别已实施和下一级别待实施的最佳实践
            current_practices = domain_info["practices"][f"{current_level}级"]
            target_practices = domain_info["practices"][f"{target_level}级"]
            
            improvement_plan[domain] = {
                "current_level": current_level,
                "target_level": target_level,
                "description": domain_info["description"],
                "current_practices": current_practices,
                "target_practices": target_practices,
                "improvement_actions": self._generate_improvement_actions(domain, current_level, target_level)
            }
        
        return improvement_plan
    
    def _generate_improvement_actions(self, domain, current_level, target_level):
        """生成改进行动计划"""
        actions = []
        
        if domain == "数据战略":
            if current_level <= 2 and target_level >= 3:
                actions.extend([
                    "制定完整的数据战略规划文档",
                    "建立数据战略执行监督机制",
                    "设立数据战略评估指标体系"
                ])
        
        elif domain == "数据治理":
            if current_level <= 2 and target_level >= 3:
                actions.extend([
                    "完善数据治理组织架构",
                    "建立数据治理制度和流程",
                    "实施数据治理监督和评估机制"
                ])
        
        elif domain == "数据质量":
            if current_level <= 2 and target_level >= 3:
                actions.extend([
                    "建立完善的数据质量管理体系",
                    "实施数据质量监控平台",
                    "制定数据质量评估机制"
                ])
        
        # 其他域的改进行动...
        
        return actions
    
    def generate_report(self, domain_scores, improvement_plan):
        """生成DCMM评估报告"""
        overall_level, domain_levels = self.assess_maturity_level(domain_scores)
        
        report = {
            "overall_level": overall_level,
            "domain_levels": domain_levels,
            "domain_scores": domain_scores,
            "improvement_plan": improvement_plan,
            "level_description": self._get_level_description(overall_level)
        }
        
        return report
    
    def _get_level_description(self, level):
        """获取成熟度等级描述"""
        descriptions = {
            1: "初始级：数据管理活动无序，依赖于个人经验，缺乏统一的标准和流程。",
            2: "受管理级：开始有计划地进行数据管理，但实施不系统，效果不稳定。",
            3: "已定义级：有标准化的流程和制度，数据管理活动得到有效推广。",
            4: "量化管理级：有量化的指标和监控机制，数据管理效果可度量和控制。",
            5: "优化级：持续创新和优化，数据管理达到行业领先水平。"
        }
        return descriptions.get(level, "未知级别")
    
    def visualize_results(self, domain_scores):
        """可视化DCMM评估结果"""
        # 准备数据
        domains = list(domain_scores.keys())
        scores = list(domain_scores.values())
        
        # 创建柱状图
        plt.figure(figsize=(12, 6))
        bars = plt.bar(domains, scores)
        
        # 添加颜色表示成熟度等级
        for bar, score in zip(bars, scores):
            if score <= 20:
                color = 'red'
            elif score <= 40:
                color = 'orange'
            elif score <= 60:
                color = 'yellow'
            elif score <= 80:
                color = 'lightgreen'
            else:
                color = 'green'
            bar.set_color(color)
        
        # 添加数据标签
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                    f'{score}', ha='center', va='bottom')
        
        # 添加水平线表示成熟度等级
        plt.axhline(y=20, color='red', linestyle='--', alpha=0.7, label='1级')
        plt.axhline(y=40, color='orange', linestyle='--', alpha=0.7, label='2级')
        plt.axhline(y=60, color='yellow', linestyle='--', alpha=0.7, label='3级')
        plt.axhline(y=80, color='lightgreen', linestyle='--', alpha=0.7, label='4级')
        plt.axhline(y=100, color='green', linestyle='-', alpha=0.7, label='5级')
        
        plt.title('DCMM数据管理能力成熟度评估结果', size=15)
        plt.ylabel('得分 (0-100)')
        plt.ylim(0, 100)
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig('dcmm_assessment_results.png', dpi=300)
        plt.show()
    
    def visualize_radar(self, domain_scores):
        """创建雷达图显示各能力域成熟度"""
        # 准备数据
        domains = list(domain_scores.keys())
        scores = list(domain_scores.values())
        
        # 转换为等级（1-5）
        levels = []
        for score in scores:
            if score <= 20:
                level = 1
            elif score <= 40:
                level = 2
            elif score <= 60:
                level = 3
            elif score <= 80:
                level = 4
            else:
                level = 5
            levels.append(level)
        
        # 创建雷达图
        angles = np.linspace(0, 2*np.pi, len(domains), endpoint=False).tolist()
        levels.append(levels[0])  # 闭合图形
        angles.append(angles[0])  # 闭合图形
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.plot(angles, levels, 'o-', linewidth=2)
        ax.fill(angles, levels, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), domains)
        ax.set_ylim(0, 5)
        ax.grid(True)
        
        # 添加等级标签
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1级', '2级', '3级', '4级', '5级'])
        
        plt.title('DCMM数据管理能力成熟度雷达图', size=15)
        plt.tight_layout()
        plt.savefig('dcmm_assessment_radar.png', dpi=300)
        plt.show()
    
    def export_report(self, report, filename="dcmm_assessment_report.json"):
        """导出评估报告到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"DCMM评估报告已导出到: {filename}")


def interactive_assessment():
    """交互式DCMM评估"""
    print("="*60)
    print("DCMM数据管理能力成熟度评估工具")
    print("="*60)
    
    assessor = DCMMAssessmentTool()
    domain_scores = {}
    
    # 评估各能力域
    for domain in assessor.capability_domains.keys():
        print(f"\n评估能力域: {domain}")
        print(f"描述: {assessor.capability_domains[domain]['description']}")
        print("-" * 40)
        
        # 获取评估分数
        while True:
            try:
                score = int(input(f"请输入{domain}的成熟度分数(0-100): "))
                if 0 <= score <= 100:
                    break
                else:
                    print("请输入0-100之间的数字")
            except ValueError:
                print("请输入有效的数字")
        
        domain_scores[domain] = score
    
    # 生成评估报告
    improvement_plan = assessor.generate_improvement_plan(
        assessor.assess_maturity_level(domain_scores)[1]
    )
    report = assessor.generate_report(domain_scores, improvement_plan)
    
    # 显示评估结果
    print("\n" + "="*60)
    print("DCMM评估结果")
    print("="*60)
    
    print(f"\n整体成熟度等级: {report['overall_level']}级")
    print(f"等级描述: {report['level_description']}")
    
    print("\n各能力域成熟度:")
    for domain, level in report['domain_levels'].items():
        score = domain_scores[domain]
        print(f"  {domain}: {level}级 ({score}分)")
    
    # 显示改进计划
    print("\n改进计划:")
    for domain, plan in report['improvement_plan'].items():
        print(f"\n{domain} (从{plan['current_level']}级提升到{plan['target_level']}级):")
        print(f"  描述: {plan['description']}")
        print(f"  待实施的最佳实践:")
        for practice in plan['target_practices']:
            print(f"    - {practice}")
        print(f"  改进行动:")
        for action in plan['improvement_actions']:
            print(f"    - {action}")
    
    # 可视化结果
    print("\n正在生成可视化图表...")
    assessor.visualize_results(domain_scores)
    assessor.visualize_radar(domain_scores)
    
    # 导出报告
    assessor.export_report(report)
    
    return report


def sample_assessment():
    """示例DCMM评估"""
    print("="*60)
    print("DCMM数据管理能力成熟度评估示例")
    print("="*60)
    
    assessor = DCMMAssessmentTool()
    
    # 模拟评估得分
    domain_scores = {
        "数据战略": 45,
        "数据治理": 35,
        "数据架构": 40,
        "数据标准": 30,
        "数据质量": 55,
        "数据安全": 50,
        "数据应用": 45,
        "数据生存周期": 40
    }
    
    print("\n各能力域模拟得分:")
    for domain, score in domain_scores.items():
        print(f"  {domain}: {score}分")
    
    # 生成评估报告
    improvement_plan = assessor.generate_improvement_plan(
        assessor.assess_maturity_level(domain_scores)[1]
    )
    report = assessor.generate_report(domain_scores, improvement_plan)
    
    # 显示评估结果
    print("\n" + "="*60)
    print("DCMM评估结果")
    print("="*60)
    
    print(f"\n整体成熟度等级: {report['overall_level']}级")
    print(f"等级描述: {report['level_description']}")
    
    print("\n各能力域成熟度:")
    for domain, level in report['domain_levels'].items():
        score = domain_scores[domain]
        print(f"  {domain}: {level}级 ({score}分)")
    
    # 可视化结果
    print("\n正在生成可视化图表...")
    assessor.visualize_results(domain_scores)
    assessor.visualize_radar(domain_scores)
    
    # 导出报告
    assessor.export_report(report)
    
    return report


if __name__ == "__main__":
    # 选择运行模式
    print("请选择运行模式:")
    print("1. 交互式评估")
    print("2. 示例评估")
    
    choice = input("请输入选择(1或2): ")
    
    if choice == "1":
        interactive_assessment()
    else:
        sample_assessment()
    
    print("\nDCMM评估完成！")