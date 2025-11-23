"""
第2章代码示例：自定义数据治理框架设计器
用于设计和构建适合组织的数据治理框架
"""

import pandas as pd
import json
from typing import Dict, List, Any
from datetime import datetime
import matplotlib.pyplot as plt
from IPython.display import display, HTML

class CustomGovernanceFramework:
    """自定义数据治理框架设计器"""
    
    def __init__(self, org_name, industry, size):
        """初始化框架设计器
        
        Args:
            org_name: 组织名称
            industry: 行业
            size: 组织规模 (小型/中型/大型)
        """
        self.org_name = org_name
        self.industry = industry
        self.size = size
        self.framework_components = {}
    
    def design_governance_structure(self):
        """设计治理组织结构"""
        # 基于组织规模设计不同层次的治理组织
        if self.size == "小型":
            governance_structure = {
                "决策层": ["数据治理负责人"],
                "管理层": ["业务代表", "IT代表"],
                "执行层": ["数据管理员", "数据开发人员"]
            }
        elif self.size == "中型":
            governance_structure = {
                "决策层": ["数据治理委员会", "首席数据官"],
                "管理层": ["业务数据负责人", "技术数据负责人", "数据治理办公室"],
                "执行层": ["数据管理员", "数据质量专员", "数据安全专员"]
            }
        else:  # 大型
            governance_structure = {
                "决策层": ["数据治理委员会", "首席数据官", "业务部门主管"],
                "管理层": ["业务数据负责人", "技术数据负责人", "数据治理办公室", 
                           "数据安全委员会", "数据架构委员会"],
                "执行层": ["领域数据管家", "数据质量分析师", "数据安全专家", 
                           "元数据管理专家", "数据开发工程师"]
            }
        
        self.framework_components["治理组织结构"] = governance_structure
        return governance_structure
    
    def define_governance_domains(self):
        """定义治理域"""
        # 基于行业特点确定重点治理域
        base_domains = [
            "数据质量管理",
            "数据安全管理",
            "元数据管理",
            "主数据管理"
        ]
        
        # 根据行业添加特定治理域
        if self.industry in ["金融", "保险", "证券"]:
            industry_specific_domains = [
                "数据合规管理",
                "数据隐私保护",
                "数据风险评估"
            ]
        elif self.industry in ["制造", "能源", "交通"]:
            industry_specific_domains = [
                "产品数据管理",
                "供应链数据管理",
                "设备数据管理"
            ]
        elif self.industry in ["零售", "电商", "消费"]:
            industry_specific_domains = [
                "客户数据管理",
                "营销数据管理",
                "用户体验数据管理"
            ]
        else:  # 通用
            industry_specific_domains = [
                "业务数据管理",
                "分析数据管理",
                "数据生命周期管理"
            ]
        
        governance_domains = base_domains + industry_specific_domains
        self.framework_components["治理域"] = governance_domains
        return governance_domains
    
    def establish_governance_processes(self):
        """建立治理流程"""
        governance_processes = {
            "决策流程": {
                "治理政策制定": ["需求分析", "草案编写", "评审", "发布"],
                "标准制定": ["调研", "编写", "评审", "批准", "发布"],
                "冲突解决": ["问题识别", "影响分析", "解决方案", "实施"]
            },
            "管理流程": {
                "数据质量监控": ["检查", "报告", "分析", "改进"],
                "数据安全审计": ["评估", "整改", "验证", "报告"],
                "元数据管理": ["收集", "整合", "更新", "发布"]
            },
            "执行流程": {
                "数据访问控制": ["申请", "审批", "授权", "审计"],
                "数据问题处理": "报告, 分析, 解决, 验证",
                "数据变更管理": ["需求", "影响分析", "实施", "验证"]
            }
        }
        
        self.framework_components["治理流程"] = governance_processes
        return governance_processes
    
    def define_governance_policies(self):
        """定义治理政策"""
        governance_policies = {
            "数据质量管理政策": {
                "目的": "确保数据满足业务需求",
                "范围": "组织内所有数据",
                "责任": "数据质量专员负责",
                "措施": [
                    "建立数据质量标准",
                    "实施数据质量监控",
                    "定期评估数据质量"
                ]
            },
            "数据安全管理政策": {
                "目的": "保护数据资产安全",
                "范围": "所有敏感和关键数据",
                "责任": "数据安全专员负责",
                "措施": [
                    "数据分类分级",
                    "访问控制机制",
                    "安全审计机制"
                ]
            },
            "元数据管理政策": {
                "目的": "确保数据可发现、可理解",
                "范围": "所有数据资产",
                "责任": "元数据管理员负责",
                "措施": [
                    "建立元数据标准",
                    "实施元数据管理平台",
                    "维护元数据完整性"
                ]
            },
            "数据访问政策": {
                "目的": "规范数据访问行为",
                "范围": "所有数据访问活动",
                "责任": "数据管理员负责",
                "措施": [
                    "权限申请流程",
                    "访问审计机制",
                    "违规处罚措施"
                ]
            }
        }
        
        # 根据行业添加特定政策
        if self.industry in ["金融", "保险", "证券"]:
            governance_policies["数据合规政策"] = {
                "目的": "满足监管合规要求",
                "范围": "所有业务数据",
                "责任": "合规专员负责",
                "措施": [
                    "合规性评估",
                    "监管报告生成",
                    "合规审计执行"
                ]
            }
        
        self.framework_components["治理政策"] = governance_policies
        return governance_policies
    
    def define_metrics_and_kpis(self):
        """定义度量指标和KPI"""
        metrics_kpis = {
            "数据质量指标": {
                "完整性": "非空值比例",
                "准确性": "错误记录比例",
                "一致性": "跨系统一致率",
                "及时性": "数据更新延迟"
            },
            "数据安全指标": {
                "安全事件数量": "季度内安全事件总数",
                "违规访问次数": "季度内违规访问次数",
                "权限合规率": "权限设置合规比例",
                "加密覆盖率": "敏感数据加密比例"
            },
            "数据使用效率指标": {
                "数据查找时间": "平均数据发现时间",
                "数据申请处理时间": "平均申请处理时间",
                "数据重复率": "重复数据资产比例",
                "数据使用率": "数据资产使用频率"
            },
            "治理效果指标": {
                "治理覆盖率": "纳入治理的数据资产比例",
                "问题解决时间": "平均问题解决时间",
                "用户满意度": "治理服务满意度",
                "治理ROI": "治理投资回报率"
            }
        }
        
        self.framework_components["度量指标"] = metrics_kpis
        return metrics_kpis
    
    def create_implementation_roadmap(self, timeframe_months=12):
        """创建实施路线图"""
        # 基于组织规模和时间框架设计实施路线图
        if self.size == "小型":
            phases = [
                {
                    "phase": 1,
                    "duration_months": 3,
                    "focus": "基础建设",
                    "activities": [
                        "任命数据治理负责人",
                        "建立基本数据质量标准",
                        "实施简单的元数据管理"
                    ]
                },
                {
                    "phase": 2,
                    "duration_months": 3,
                    "focus": "体系完善",
                    "activities": [
                        "完善治理流程",
                        "实施数据安全控制",
                        "建立数据质量监控"
                    ]
                },
                {
                    "phase": 3,
                    "duration_months": 6,
                    "focus": "全面推广",
                    "activities": [
                        "推广治理制度",
                        "培训数据管理人员",
                        "建立持续改进机制"
                    ]
                }
            ]
        elif self.size == "中型":
            phases = [
                {
                    "phase": 1,
                    "duration_months": 3,
                    "focus": "规划与启动",
                    "activities": [
                        "组建数据治理委员会",
                        "制定治理战略",
                        "选择治理工具"
                    ]
                },
                {
                    "phase": 2,
                    "duration_months": 3,
                    "focus": "标准与流程建设",
                    "activities": [
                        "制定数据标准",
                        "建立治理流程",
                        "实施元数据管理"
                    ]
                },
                {
                    "phase": 3,
                    "duration_months": 3,
                    "focus": "试点实施",
                    "activities": [
                        "选择试点领域",
                        "实施治理机制",
                        "评估试点效果"
                    ]
                },
                {
                    "phase": 4,
                    "duration_months": 3,
                    "focus": "全面推广",
                    "activities": [
                        "推广成功经验",
                        "完善治理体系",
                        "建立度量机制"
                    ]
                }
            ]
        else:  # 大型
            phases = [
                {
                    "phase": 1,
                    "duration_months": 3,
                    "focus": "战略规划",
                    "activities": [
                        "评估治理现状",
                        "制定治理战略",
                        "组建治理组织"
                    ]
                },
                {
                    "phase": 2,
                    "duration_months": 3,
                    "focus": "框架设计",
                    "activities": [
                        "设计治理框架",
                        "制定治理政策",
                        "选择技术平台"
                    ]
                },
                {
                    "phase": 3,
                    "duration_months": 3,
                    "focus": "试点实施",
                    "activities": [
                        "选择试点项目",
                        "实施治理机制",
                        "评估试点效果"
                    ]
                },
                {
                    "phase": 4,
                    "duration_months": 3,
                    "focus": "全面推广",
                    "activities": [
                        "扩展实施范围",
                        "完善治理体系",
                        "建立度量机制"
                    ]
                }
            ]
        
        self.framework_components["实施路线图"] = phases
        return phases
    
    def generate_framework_document(self):
        """生成框架文档"""
        # 设计各组件
        governance_structure = self.design_governance_structure()
        governance_domains = self.define_governance_domains()
        governance_processes = self.establish_governance_processes()
        governance_policies = self.define_governance_policies()
        metrics_kpis = self.define_metrics_and_kpis()
        implementation_roadmap = self.create_implementation_roadmap()
        
        # 生成文档
        framework_document = {
            "组织名称": self.org_name,
            "行业": self.industry,
            "组织规模": self.size,
            "框架版本": "1.0",
            "创建时间": datetime.now().strftime('%Y-%m-%d'),
            "组件": self.framework_components
        }
        
        return framework_document
    
    def visualize_implementation_roadmap(self):
        """可视化实施路线图"""
        roadmap = self.framework_components.get("实施路线图", [])
        if not roadmap:
            return
        
        # 准备数据
        phases = [f"阶段{p['phase']}" for p in roadmap]
        durations = [p['duration_months'] for p in roadmap]
        focuses = [p['focus'] for p in roadmap]
        
        # 创建甘特图
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 设置颜色
        colors = ['blue', 'green', 'orange', 'red']
        start_time = 0
        
        bars = []
        for i, (phase, duration, focus) in enumerate(zip(phases, durations, focuses)):
            # 计算开始和结束时间
            start = start_time
            end = start + duration
            
            # 创建水平条
            bar = ax.barh(phase, duration, left=start, color=colors[i % len(colors)], alpha=0.7)
            bars.append(bar)
            
            # 添加活动描述
            activities_text = '\n'.join([f"• {act}" for act in roadmap[i]['activities'][:3]])
            ax.text(start + duration/2, i, f"{focus}\n{activities_text}", 
                    ha='center', va='center', color='white', fontsize=9, weight='bold')
            
            start_time = end
        
        # 设置图表
        ax.set_xlabel('月份')
        ax.set_title(f'{self.org_name}数据治理实施路线图', fontsize=14, weight='bold')
        ax.set_yticks(phases)
        ax.set_xlim(0, sum(durations))
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(f'{self.org_name}_implementation_roadmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_governance_structure(self):
        """可视化治理组织结构"""
        structure = self.framework_components.get("治理组织结构", {})
        if not structure:
            return
        
        # 创建组织结构图
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 设置层级位置
        levels = list(structure.keys())
        level_y = {level: i for i, level in enumerate(reversed(levels))}
        
        # 为每个层级创建矩形和文本
        for level, roles in structure.items():
            y = level_y[level]
            role_count = len(roles)
            
            # 计算每个角色的位置
            x_start = (10 - role_count) / 2
            for i, role in enumerate(roles):
                x = x_start + i
                width = 0.8
                height = 0.6
                
                # 绘制矩形
                rect = plt.Rectangle((x, y), width, height, 
                                 facecolor='skyblue', edgecolor='black', alpha=0.7)
                ax.add_patch(rect)
                
                # 添加文本
                ax.text(x + width/2, y + height/2, role, 
                        ha='center', va='center', fontsize=9, weight='bold')
                
                # 添加连线到上一层
                if level != "执行层":
                    for j in range(role_count):
                        ax.plot([x + width/2, x + width/2], [y, y - 0.4], 
                               'k-', alpha=0.5)
        
        # 设置图表
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.5, len(levels) - 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'{self.org_name}数据治理组织结构', fontsize=14, weight='bold')
        
        # 添加层级标签
        for level, y in level_y.items():
            ax.text(-0.5, y + 0.3, level, ha='right', va='center', 
                   fontsize=10, weight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.org_name}_governance_structure.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def display_framework_summary(self):
        """显示框架摘要"""
        if not self.framework_components:
            self.generate_framework_document()
        
        # 创建HTML摘要
        html = f"""
        <h1>{self.org_name} 数据治理框架摘要</h1>
        <p><b>行业:</b> {self.industry}</p>
        <p><b>组织规模:</b> {self.size}</p>
        
        <h2>治理域</h2>
        <ul>
        """
        
        for domain in self.framework_components.get("治理域", []):
            html += f"<li>{domain}</li>"
        
        html += """
        </ul>
        
        <h2>治理组织结构</h2>
        <table border="1" style="width:100%; border-collapse: collapse;">
        <tr>
        """
        
        for level in self.framework_components.get("治理组织结构", {}).keys():
            html += f"<th>{level}</th>"
        
        html += "</tr><tr>"
        
        for level in self.framework_components.get("治理组织结构", {}).values():
            roles = "<br>".join(level)
            html += f"<td>{roles}</td>"
        
        html += """
        </tr>
        </table>
        
        <h2>关键政策</h2>
        <ul>
        """
        
        for policy in self.framework_components.get("治理政策", {}).keys():
            html += f"<li>{policy}</li>"
        
        html += """
        </ul>
        
        <h2>实施阶段</h2>
        <table border="1" style="width:100%; border-collapse: collapse;">
        <tr><th>阶段</th><th>持续时间(月)</th><th>重点</th></tr>
        """
        
        for phase in self.framework_components.get("实施路线图", []):
            html += f"""
            <tr>
            <td>阶段{phase['phase']}</td>
            <td>{phase['duration_months']}</td>
            <td>{phase['focus']}</td>
            </tr>
            """
        
        html += "</table>"
        
        display(HTML(html))
    
    def export_framework(self, filename=None):
        """导出框架文档"""
        if filename is None:
            filename = f"{self.org_name}_数据治理框架.json"
        
        framework_document = self.generate_framework_document()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(framework_document, f, ensure_ascii=False, indent=2)
        
        print(f"数据治理框架文档已导出到: {filename}")
        return filename


def interactive_framework_builder():
    """交互式框架构建器"""
    print("="*60)
    print("自定义数据治理框架设计器")
    print("="*60)
    
    # 获取组织信息
    org_name = input("请输入组织名称: ")
    print("请选择行业:")
    print("1. 金融/保险/证券")
    print("2. 制造/能源/交通")
    print("3. 零售/电商/消费")
    print("4. 其他")
    
    industry_choice = input("请输入选择(1-4): ")
    industry_map = {
        "1": "金融",
        "2": "制造",
        "3": "零售",
        "4": "通用"
    }
    industry = industry_map.get(industry_choice, "通用")
    
    print("\n请选择组织规模:")
    print("1. 小型(<500人)")
    print("2. 中型(500-5000人)")
    print("3. 大型(>5000人)")
    
    size_choice = input("请输入选择(1-3): ")
    size_map = {
        "1": "小型",
        "2": "中型",
        "3": "大型"
    }
    size = size_map.get(size_choice, "中型")
    
    # 创建框架设计器
    framework = CustomGovernanceFramework(org_name, industry, size)
    
    # 生成框架文档
    framework_document = framework.generate_framework_document()
    
    # 显示摘要
    print("\n正在生成框架摘要...")
    framework.display_framework_summary()
    
    # 可视化组织结构
    print("\n正在生成组织结构图...")
    framework.visualize_governance_structure()
    
    # 可视化实施路线图
    print("\n正在生成实施路线图...")
    framework.visualize_implementation_roadmap()
    
    # 导出框架文档
    filename = framework.export_framework()
    
    return framework


def sample_framework_builder():
    """示例框架构建器"""
    print("="*60)
    print("自定义数据治理框架设计示例")
    print("="*60)
    
    # 创建框架设计器
    framework = CustomGovernanceFramework(
        org_name="示例科技公司",
        industry="金融",
        size="中型"
    )
    
    # 生成框架文档
    framework_document = framework.generate_framework_document()
    
    # 显示关键组件
    print("\n1. 治理组织结构:")
    structure = framework_document["组件"]["治理组织结构"]
    for level, roles in structure.items():
        print(f"  {level}: {', '.join(roles)}")
    
    print("\n2. 治理域:")
    domains = framework_document["组件"]["治理域"]
    for domain in domains:
        print(f"  - {domain}")
    
    print("\n3. 治理政策概览:")
    policies = framework_document["组件"]["治理政策"]
    for policy, details in policies.items():
        print(f"  - {policy}: {details['目的']}")
    
    print("\n4. 实施路线图:")
    roadmap = framework_document["组件"]["实施路线图"]
    for phase in roadmap:
        print(f"  阶段{phase['phase']}: {phase['focus']} ({phase['duration_months']}个月)")
        print("    主要活动:")
        for activity in phase['activities'][:2]:  # 只显示前两个活动
            print(f"      - {activity}")
    
    # 可视化组织结构
    print("\n正在生成组织结构图...")
    framework.visualize_governance_structure()
    
    # 可视化实施路线图
    print("\n正在生成实施路线图...")
    framework.visualize_implementation_roadmap()
    
    # 导出框架文档
    filename = framework.export_framework()
    
    return framework


if __name__ == "__main__":
    # 选择运行模式
    print("请选择运行模式:")
    print("1. 交互式框架构建")
    print("2. 示例框架构建")
    
    choice = input("请输入选择(1或2): ")
    
    if choice == "1":
        interactive_framework_builder()
    else:
        sample_framework_builder()
    
    print("\n数据治理框架设计完成！")