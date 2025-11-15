#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第9章：数据质量治理与组织架构 - 代码示例
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import json


class GovernanceAssessment:
    """数据治理成熟度评估"""
    
    def __init__(self):
        # 治理维度权重
        self.dimensions = {
            'data_strategy': 0.20,      # 数据战略
            'organization': 0.15,       # 组织架构
            'policies': 0.20,           # 政策制度
            'processes': 0.15,          # 流程标准
            'technology': 0.15,         # 技术工具
            'culture': 0.15             # 文化意识
        }
        
        # 评估标准
        self.criteria = {
            'data_strategy': [
                '缺乏明确的数据战略',
                '有初步的数据战略意识',
                '制定了数据战略但执行不到位',
                '有完善的数据战略并有效执行',
                '数据战略持续优化并引领业务'
            ],
            'organization': [
                '无专门的数据管理组织',
                '有兼职数据管理人员',
                '设立了专职数据管理岗位',
                '建立了完整的数据管理组织体系',
                '组织架构灵活高效并持续优化'
            ],
            'policies': [
                '无数据相关政策制度',
                '有零散的数据管理要求',
                '建立了基础的数据政策体系',
                '政策制度覆盖全面并有效执行',
                '政策体系持续完善并行业领先'
            ],
            'processes': [
                '数据管理流程混乱',
                '有基本的数据管理流程',
                '建立了标准化的数据管理流程',
                '流程实现了系统化管理',
                '流程持续优化并自动化'
            ],
            'technology': [
                '主要依靠手工管理',
                '使用简单的工具辅助',
                '配备了专业的数据管理工具',
                '工具集成度高并有效支撑',
                '采用了先进的智能化工具'
            ],
            'culture': [
                '缺乏数据质量意识',
                '部分人员有数据质量意识',
                '多数员工具备数据质量意识',
                '形成了良好的数据文化氛围',
                '数据驱动成为核心企业文化'
            ]
        }
    
    def assess_maturity(self, scores: Dict[str, int]) -> Dict:
        """
        评估数据治理成熟度
        
        Args:
            scores: 各维度评分 (1-5分)
            
        Returns:
            评估结果字典
        """
        if not all(dim in scores for dim in self.dimensions.keys()):
            raise ValueError("缺少必要的评估维度评分")
        
        # 计算加权总分
        total_score = sum(
            scores[dim] * self.dimensions[dim] 
            for dim in self.dimensions.keys()
        )
        
        # 确定成熟度等级
        if total_score >= 4.5:
            level = "优化级"
            description = "治理能力行业领先，持续优化改进"
        elif total_score >= 3.5:
            level = "管理级"
            description = "治理体系相对完善，有效支撑业务"
        elif total_score >= 2.5:
            level = "定义级"
            description = "建立了基本治理框架，需要持续完善"
        elif total_score >= 1.5:
            level = "初始级"
            description = "治理能力较弱，需要系统性建设"
        else:
            level = "无序级"
            description = "缺乏治理体系，管理混乱"
        
        # 各维度详细评分
        dimension_details = {}
        for dim, score in scores.items():
            dimension_details[dim] = {
                'score': score,
                'weight': self.dimensions[dim],
                'weighted_score': score * self.dimensions[dim],
                'description': self.criteria[dim][score-1]
            }
        
        return {
            'total_score': round(total_score, 2),
            'maturity_level': level,
            'description': description,
            'dimensions': dimension_details
        }


class OrganizationDesign:
    """数据管理组织架构设计"""
    
    def __init__(self):
        # 角色职责定义
        self.roles = {
            'ChiefDataOfficer': {
                'title': '首席数据官',
                'responsibilities': [
                    '制定企业数据战略',
                    '推动数据治理体系建设',
                    '协调跨部门数据合作',
                    '监督数据质量管理工作',
                    '促进数据价值实现'
                ],
                'reporting_lines': ['CEO'],
                'key_metrics': [
                    '数据治理成熟度',
                    '数据资产价值增长率',
                    '数据驱动决策占比'
                ]
            },
            'DataGovernanceManager': {
                'title': '数据治理经理',
                'responsibilities': [
                    '制定数据治理政策',
                    '建立数据标准体系',
                    '推进数据质量管理',
                    '组织数据治理培训',
                    '监控治理执行情况'
                ],
                'reporting_lines': ['ChiefDataOfficer'],
                'key_metrics': [
                    '政策执行覆盖率',
                    '数据标准符合率',
                    '治理问题解决率'
                ]
            },
            'DataQualityManager': {
                'title': '数据质量经理',
                'responsibilities': [
                    '建立数据质量管理体系',
                    '制定质量评估标准',
                    '监控数据质量指标',
                    '推动质量问题整改',
                    '组织质量文化建设'
                ],
                'reporting_lines': ['DataGovernanceManager'],
                'key_metrics': [
                    '数据质量指数',
                    '质量问题发现及时率',
                    '质量问题解决率'
                ]
            },
            'DataSteward': {
                'title': '数据管家',
                'responsibilities': [
                    '负责特定业务领域数据',
                    '执行数据质量规则',
                    '处理数据质量问题',
                    '维护数据标准规范',
                    '提供数据业务支持'
                ],
                'reporting_lines': ['DataQualityManager'],
                'key_metrics': [
                    '负责数据质量水平',
                    '问题处理及时率',
                    '业务满意度'
                ]
            }
        }
    
    def design_organization(self, company_size: str, industry: str) -> Dict:
        """
        设计适合的组织架构
        
        Args:
            company_size: 公司规模 ('small', 'medium', 'large')
            industry: 行业类型
            
        Returns:
            组织架构设计方案
        """
        org_structure = {
            'company_size': company_size,
            'industry': industry,
            'recommended_roles': [],
            'structure_chart': {},
            'implementation_phases': []
        }
        
        if company_size == 'small':
            # 小型企业架构
            org_structure['recommended_roles'] = [
                'DataGovernanceManager', 
                'DataQualityManager'
            ]
            org_structure['structure_chart'] = {
                'Executive': ['DataGovernanceManager'],
                'DataGovernanceManager': ['DataQualityManager'],
                'DataQualityManager': ['Business Analysts']
            }
            org_structure['implementation_phases'] = [
                '第一阶段：设立数据治理岗位',
                '第二阶段：建立基础管理制度',
                '第三阶段：完善质量监控体系'
            ]
            
        elif company_size == 'medium':
            # 中型企业架构
            org_structure['recommended_roles'] = [
                'ChiefDataOfficer',
                'DataGovernanceManager', 
                'DataQualityManager',
                '2-3 DataStewards'
            ]
            org_structure['structure_chart'] = {
                'Executive': ['ChiefDataOfficer'],
                'ChiefDataOfficer': ['DataGovernanceManager'],
                'DataGovernanceManager': ['DataQualityManager'],
                'DataQualityManager': ['DataStewards']
            }
            org_structure['implementation_phases'] = [
                '第一阶段：设立首席数据官',
                '第二阶段：建立治理组织体系',
                '第三阶段：完善质量管理体系',
                '第四阶段：推广数据文化建设'
            ]
            
        else:  # large
            # 大型企业架构
            org_structure['recommended_roles'] = [
                'ChiefDataOfficer',
                'DataGovernanceManager', 
                'DataQualityManager',
                'DataStewards (按业务领域配置)',
                'DataEngineers',
                'DataAnalysts'
            ]
            org_structure['structure_chart'] = {
                'Executive': ['ChiefDataOfficer'],
                'ChiefDataOfficer': ['DataGovernanceManager', 'DataEngineeringLead', 'DataAnalyticsLead'],
                'DataGovernanceManager': ['DataQualityManager'],
                'DataQualityManager': ['DataStewards'],
                'DataEngineeringLead': ['DataEngineers'],
                'DataAnalyticsLead': ['DataAnalysts']
            }
            org_structure['implementation_phases'] = [
                '第一阶段：顶层设计和组织架构',
                '第二阶段：制度建设和流程规范',
                '第三阶段：工具平台和标准体系',
                '第四阶段：团队能力和文化建设',
                '第五阶段：持续优化和创新发展'
            ]
        
        return org_structure


class ManufacturingCaseStudy:
    """制造业数据质量治理案例"""
    
    def __init__(self):
        self.company_info = {
            'name': '华泰制造有限公司',
            'industry': '汽车零部件制造',
            'employees': 5000,
            'revenue': '50亿人民币'
        }
        
        # 治理前的问题
        self.pre_governance_issues = {
            'data_silos': '各部门数据独立管理，难以共享',
            'inconsistent_standards': '相同业务含义的数据定义不一致',
            'poor_quality': '客户数据缺失率30%，产品数据错误率15%',
            'no_governance': '缺乏统一的数据管理政策和流程',
            'low_awareness': '员工数据质量意识淡薄'
        }
        
        # 治理措施
        self.governance_measures = {
            'organizational': '成立数据治理委员会，设立专职数据管理岗位',
            'strategic': '制定三年数据治理战略规划',
            'policy': '建立数据标准、质量、安全管理制度',
            'technical': '引入数据治理平台，实现数据统一管理',
            'cultural': '开展数据质量培训，建立激励机制'
        }
        
        # 治理效果
        self.post_governance_results = {
            'quality_improvement': '数据质量指数从65分提升到88分',
            'cost_reduction': '因数据问题导致的业务损失降低60%',
            'efficiency_gain': '数据处理效率提升40%',
            'decision_support': '数据驱动决策占比从20%提升到70%',
            'compliance': '满足行业监管要求，通过ISO认证'
        }
    
    def generate_case_report(self) -> Dict:
        """生成案例报告"""
        return {
            'company_info': self.company_info,
            'challenges': self.pre_governance_issues,
            'solutions': self.governance_measures,
            'results': self.post_governance_results,
            'lessons_learned': [
                '高层支持是成功的关键因素',
                '循序渐进比一步到位更有效',
                '技术和管理要双管齐下',
                '文化建设需要长期坚持',
                '持续改进是保持效果的保障'
            ]
        }


def main():
    """主函数 - 演示数据治理与组织架构代码示例"""
    print("=== 第9章：数据质量治理与组织架构 代码示例 ===\n")
    
    # 1. 数据治理成熟度评估示例
    print("1. 数据治理成熟度评估示例")
    print("-" * 40)
    
    governance_assessment = GovernanceAssessment()
    
    # 模拟某企业的治理评分
    company_scores = {
        'data_strategy': 3,
        'organization': 2,
        'policies': 3,
        'processes': 2,
        'technology': 3,
        'culture': 2
    }
    
    assessment_result = governance_assessment.assess_maturity(company_scores)
    
    print(f"治理总分: {assessment_result['total_score']}")
    print(f"成熟度等级: {assessment_result['maturity_level']}")
    print(f"等级描述: {assessment_result['description']}")
    print("\n各维度详情:")
    for dim, details in assessment_result['dimensions'].items():
        print(f"  {dim}: {details['score']}分 (权重{details['weight']}) - {details['description']}")
    
    print("\n" + "="*60 + "\n")
    
    # 2. 组织架构设计示例
    print("2. 数据管理组织架构设计示例")
    print("-" * 40)
    
    org_design = OrganizationDesign()
    
    # 为中型企业设计组织架构
    medium_company_org = org_design.design_organization('medium', '制造业')
    
    print(f"公司规模: {medium_company_org['company_size']}")
    print(f"所属行业: {medium_company_org['industry']}")
    print(f"推荐角色: {', '.join(medium_company_org['recommended_roles'])}")
    print("组织架构图:")
    for manager, reports in medium_company_org['structure_chart'].items():
        print(f"  {manager} -> {', '.join(reports)}")
    print("实施阶段:")
    for phase in medium_company_org['implementation_phases']:
        print(f"  {phase}")
    
    print("\n" + "="*60 + "\n")
    
    # 3. 制造业案例研究
    print("3. 制造业数据质量治理案例")
    print("-" * 40)
    
    case_study = ManufacturingCaseStudy()
    case_report = case_study.generate_case_report()
    
    print(f"案例企业: {case_report['company_info']['name']}")
    print(f"所属行业: {case_report['company_info']['industry']}")
    print(f"员工规模: {case_report['company_info']['employees']}人")
    print(f"年营收: {case_report['company_info']['revenue']}")
    
    print("\n治理前面临的主要挑战:")
    for challenge, description in case_report['challenges'].items():
        print(f"  - {description}")
    
    print("\n采取的主要治理措施:")
    for measure, description in case_report['solutions'].items():
        print(f"  - {description}")
    
    print("\n治理取得的主要成效:")
    for result, description in case_report['results'].items():
        print(f"  - {description}")
    
    print("\n经验总结:")
    for lesson in case_report['lessons_learned']:
        print(f"  - {lesson}")


if __name__ == "__main__":
    main()