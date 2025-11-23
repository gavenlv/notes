"""
第1章代码示例：数据治理成熟度评估工具
用于评估组织的数据治理成熟度水平，识别改进领域
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class DataGovernanceMaturityModel:
    """数据治理成熟度评估模型"""
    
    def __init__(self):
        # 定义评估维度和问题
        self.dimensions = {
            "数据质量": [
                "是否有明确的数据质量标准？",
                "是否有数据质量监控机制？",
                "是否有数据质量改进流程？",
                "是否有数据质量责任人？"
            ],
            "数据安全": [
                "是否有数据分类分级标准？",
                "是否有访问控制策略？",
                "是否有数据加密机制？",
                "是否有安全审计流程？"
            ],
            "数据标准": [
                "是否有统一的数据字典？",
                "是否有数据命名规范？",
                "是否有数据模型标准？",
                "是否有数据接口规范？"
            ],
            "元数据管理": [
                "是否有元数据管理平台？",
                "是否有数据血缘追踪？",
                "是否有业务元数据？",
                "是否有技术元数据？"
            ],
            "组织与责任": [
                "是否有数据治理委员会？",
                "是否有明确的数据责任人？",
                "是否有数据治理流程？",
                "是否有数据治理培训？"
            ]
        }
        
        # 定义成熟度等级
        self.maturity_levels = {
            1: "初始级：无明确流程，无计划性",
            2: "可重复级：有基本流程，但不可预测",
            3: "已定义级：有标准流程并文档化",
            4: "已管理级：有度量和控制的流程",
            5: "优化级：持续改进和创新"
        }
    
    def assess_maturity(self, scores: Dict[str, List[int]] = None) -> Dict[str, float]:
        """评估数据治理成熟度
        
        Args:
            scores: 预定义的评分数据，格式为 {维度: [评分列表]}
            
        Returns:
            包含各维度评分和总体评分的字典
        """
        results = {}
        
        if scores is None:
            # 如果没有提供评分，则使用模拟评分
            scores = self._generate_sample_scores()
        
        for dimension, dimension_scores in scores.items():
            if dimension in self.dimensions:
                # 计算维度平均分
                avg_score = sum(dimension_scores) / len(dimension_scores)
                results[dimension] = avg_score
                
                # 显示详细评分
                level = int(avg_score)
                print(f"{dimension}: {avg_score:.2f} ({self.maturity_levels[level]})")
        
        # 计算总体成熟度
        overall_score = sum(results.values()) / len(results)
        results["总体成熟度"] = overall_score
        
        return results
    
    def _generate_sample_scores(self) -> Dict[str, List[int]]:
        """生成示例评分数据，用于演示"""
        return {
            "数据质量": [3, 4, 2, 3],
            "数据安全": [4, 3, 3, 2],
            "数据标准": [2, 2, 3, 2],
            "元数据管理": [1, 2, 2, 1],
            "组织与责任": [3, 2, 3, 2]
        }
    
    def visualize_results(self, results: Dict[str, float]):
        """可视化评估结果"""
        # 准备数据
        dimensions = [k for k in results.keys() if k != "总体成熟度"]
        scores = [results[d] for d in dimensions]
        
        # 创建雷达图
        angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False).tolist()
        scores.append(scores[0])  # 闭合图形
        angles.append(angles[0])  # 闭合图形
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        ax.plot(angles, scores, 'o-', linewidth=2)
        ax.fill(angles, scores, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), dimensions)
        ax.set_ylim(0, 5)
        ax.grid(True)
        
        plt.title('数据治理成熟度评估结果', size=15)
        plt.tight_layout()
        plt.savefig('maturity_assessment_radar.png', dpi=300)
        plt.show()
        
        # 创建柱状图
        plt.figure(figsize=(10, 6))
        bars = plt.bar(dimensions, scores[:-1])  # 移除最后一个重复值
        
        # 添加颜色条表示成熟度等级
        for bar, score in zip(bars, scores[:-1]):
            if score < 2:
                color = 'red'
            elif score < 3:
                color = 'orange'
            elif score < 4:
                color = 'yellow'
            else:
                color = 'green'
            bar.set_color(color)
        
        plt.axhline(y=3, color='gray', linestyle='--', alpha=0.7)
        plt.text(len(dimensions)-0.5, 3, '基准线 (3.0)', ha='right')
        
        plt.title('数据治理成熟度各维度得分', size=15)
        plt.ylabel('得分 (1-5)')
        plt.ylim(0, 5)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('maturity_assessment_bar.png', dpi=300)
        plt.show()
    
    def generate_report(self, results: Dict[str, float]):
        """生成评估报告"""
        print("\n" + "="*60)
        print("数据治理成熟度评估报告")
        print("="*60)
        
        # 显示各维度得分
        for dimension, score in results.items():
            if dimension == "总体成熟度":
                continue
                
            level = int(score)
            print(f"\n{dimension}: {score:.2f} ({self.maturity_levels[level]})")
        
        # 总体评估
        overall_score = results["总体成熟度"]
        level = int(overall_score)
        print(f"\n总体成熟度: {overall_score:.2f} ({self.maturity_levels[level]})")
        
        # 改进建议
        print("\n改进建议:")
        weakest_dimension = min((k, v) for k, v in results.items() if k != "总体成熟度")[0]
        print(f"- 优先改进领域: {weakest_dimension}")
        
        if overall_score < 2:
            print("- 建议建立基本的数据治理框架和流程")
            print("- 优先实施: 数据治理委员会、基本数据质量监控")
        elif overall_score < 3:
            print("- 建议完善数据治理流程并文档化")
            print("- 优先实施: 数据标准制定、元数据管理")
        elif overall_score < 4:
            print("- 建议建立度量指标和控制机制")
            print("- 优先实施: 数据质量度量、安全审计")
        else:
            print("- 建议建立持续改进和创新机制")
            print("- 优先实施: 数据治理自动化、智能化分析")
        
        return overall_score


def run_assessment():
    """运行数据治理成熟度评估"""
    print("="*60)
    print("数据治理成熟度评估工具")
    print("="*60)
    print("评分说明：")
    print("1=完全没有实施")
    print("2=初步实施但不完整")
    print("3=基本实施并文档化")
    print("4=全面实施并有控制")
    print("5=全面实施并持续优化")
    
    # 创建评估器
    assessor = DataGovernanceMaturityModel()
    
    # 评估成熟度
    results = assessor.assess_maturity()
    
    # 可视化结果
    assessor.visualize_results(results)
    
    # 生成报告
    overall_score = assessor.generate_report(results)
    
    return results, overall_score


if __name__ == "__main__":
    # 运行评估
    results, overall_score = run_assessment()
    
    # 可以根据结果进行进一步分析或决策
    print(f"\n评估完成，总体成熟度评分: {overall_score:.2f}")
    
    # 如果总体成熟度低于3，建议制定改进计划
    if overall_score < 3:
        print("建议参考第10章：数据治理项目实施路线图，制定改进计划")