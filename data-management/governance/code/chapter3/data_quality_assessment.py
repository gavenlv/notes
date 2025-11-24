#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量评估工具
用于评估数据集的六大质量维度：准确性、完整性、一致性、时效性、唯一性、有效性
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import json
import warnings
warnings.filterwarnings('ignore')

class DataQualityAssessment:
    """数据质量评估器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化评估器
        
        Args:
            df (pd.DataFrame): 待评估的数据集
        """
        self.df = df.copy()
        self.results = {}
        self.dimension_scores = {}
        
    def assess_completeness(self, columns: List[str] = None) -> Dict:
        """
        评估数据完整性
        
        Args:
            columns (List[str]): 要评估的列，如果为None则评估所有列
            
        Returns:
            Dict: 完整性评估结果
        """
        if columns is None:
            columns = self.df.columns.tolist()
        
        results = {
            'dimension': 'completeness',
            'column_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        total_cells = 0
        missing_cells = 0
        
        for col in columns:
            col_data = self.df[col]
            total_count = len(col_data)
            missing_count = col_data.isnull().sum()
            completeness_score = (1 - missing_count / total_count) * 100
            
            results['column_scores'][col] = {
                'score': completeness_score,
                'missing_count': missing_count,
                'total_count': total_count,
                'missing_percentage': (missing_count / total_count) * 100
            }
            
            total_cells += total_count
            missing_cells += missing_count
            
            # 识别完整性问题
            if completeness_score < 80:
                results['issues'].append({
                    'column': col,
                    'type': 'low_completeness',
                    'severity': 'high' if completeness_score < 60 else 'medium',
                    'description': f"列 {col} 的完整率仅为 {completeness_score:.2f}%"
                })
        
        results['overall_score'] = (1 - missing_cells / total_cells) * 100
        self.dimension_scores['completeness'] = results['overall_score']
        
        return results
    
    def assess_uniqueness(self, columns: List[str] = None) -> Dict:
        """
        评估数据唯一性
        
        Args:
            columns (List[str]): 要评估的列，如果为None则评估所有列
            
        Returns:
            Dict: 唯一性评估结果
        """
        if columns is None:
            columns = self.df.columns.tolist()
        
        results = {
            'dimension': 'uniqueness',
            'column_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        total_duplicates = 0
        total_records = len(self.df) * len(columns)
        
        for col in columns:
            col_data = self.df[col]
            duplicate_count = col_data.duplicated().sum()
            uniqueness_score = (1 - duplicate_count / len(col_data)) * 100
            
            results['column_scores'][col] = {
                'score': uniqueness_score,
                'duplicate_count': duplicate_count,
                'unique_count': col_data.nunique(),
                'total_count': len(col_data),
                'duplicate_percentage': (duplicate_count / len(col_data)) * 100
            }
            
            total_duplicates += duplicate_count
            
            # 识别唯一性问题
            if uniqueness_score < 95:
                results['issues'].append({
                    'column': col,
                    'type': 'low_uniqueness',
                    'severity': 'high' if uniqueness_score < 90 else 'medium',
                    'description': f"列 {col} 的唯一率仅为 {uniqueness_score:.2f}%"
                })
        
        results['overall_score'] = (1 - total_duplicates / total_records) * 100
        self.dimension_scores['uniqueness'] = results['overall_score']
        
        return results
    
    def assess_validity(self, column_rules: Dict[str, Dict] = None) -> Dict:
        """
        评估数据有效性
        
        Args:
            column_rules (Dict[str, Dict]): 列验证规则
                格式: {'列名': {'type': 'regex', 'pattern': '正则表达式', 'type': 'range', 'min': 最小值, 'max': 最大值}}
                
        Returns:
            Dict: 有效性评估结果
        """
        if column_rules is None:
            # 默认规则
            column_rules = self._infer_column_rules()
        
        results = {
            'dimension': 'validity',
            'column_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        total_records = 0
        valid_records = 0
        
        for col, rule in column_rules.items():
            if col not in self.df.columns:
                continue
                
            col_data = self.df[col].dropna()  # 排除空值
            total_count = len(col_data)
            valid_count = 0
            invalid_records = []
            
            for idx, value in col_data.items():
                if self._validate_value(value, rule):
                    valid_count += 1
                else:
                    invalid_records.append(idx)
            
            validity_score = (valid_count / total_count) * 100 if total_count > 0 else 100
            
            results['column_scores'][col] = {
                'score': validity_score,
                'valid_count': valid_count,
                'invalid_count': total_count - valid_count,
                'total_count': total_count,
                'invalid_percentage': ((total_count - valid_count) / total_count) * 100 if total_count > 0 else 0,
                'invalid_records': invalid_records[:10]  # 只记录前10个无效记录
            }
            
            total_records += total_count
            valid_records += valid_count
            
            # 识别有效性问题
            if validity_score < 90:
                results['issues'].append({
                    'column': col,
                    'type': 'low_validity',
                    'severity': 'high' if validity_score < 80 else 'medium',
                    'description': f"列 {col} 的有效率仅为 {validity_score:.2f}%"
                })
        
        results['overall_score'] = (valid_records / total_records) * 100 if total_records > 0 else 100
        self.dimension_scores['validity'] = results['overall_score']
        
        return results
    
    def assess_accuracy(self, reference_data: pd.DataFrame = None, key_columns: List[str] = None) -> Dict:
        """
        评估数据准确性（需要参考数据）
        
        Args:
            reference_data (pd.DataFrame): 参考数据集
            key_columns (List[str]): 用于匹配的键列
            
        Returns:
            Dict: 准确性评估结果
        """
        if reference_data is None or key_columns is None:
            # 如果没有参考数据，返回基于规则的准确性评估
            return self._assess_accuracy_by_rules()
        
        results = {
            'dimension': 'accuracy',
            'column_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        # 合并数据
        merged = pd.merge(
            self.df, reference_data, 
            on=key_columns, 
            suffixes=('_current', '_reference')
        )
        
        total_comparisons = 0
        accurate_comparisons = 0
        
        for col in self.df.columns:
            if col in key_columns or f"{col}_reference" not in merged.columns:
                continue
                
            current_col = f"{col}_current"
            reference_col = f"{col}_reference"
            
            # 只比较非空值
            comparison_mask = merged[current_col].notna() & merged[reference_col].notna()
            comparable_data = merged[comparison_mask]
            
            if len(comparable_data) == 0:
                continue
                
            accurate_count = (comparable_data[current_col] == comparable_data[reference_col]).sum()
            accuracy_score = (accurate_count / len(comparable_data)) * 100
            
            results['column_scores'][col] = {
                'score': accuracy_score,
                'accurate_count': accurate_count,
                'inaccurate_count': len(comparable_data) - accurate_count,
                'total_comparable': len(comparable_data),
                'inaccuracy_percentage': ((len(comparable_data) - accurate_count) / len(comparable_data)) * 100
            }
            
            total_comparisons += len(comparable_data)
            accurate_comparisons += accurate_count
            
            # 识别准确性问题
            if accuracy_score < 95:
                results['issues'].append({
                    'column': col,
                    'type': 'low_accuracy',
                    'severity': 'high' if accuracy_score < 90 else 'medium',
                    'description': f"列 {col} 的准确率仅为 {accuracy_score:.2f}%"
                })
        
        results['overall_score'] = (accurate_comparisons / total_comparisons) * 100 if total_comparisons > 0 else 100
        self.dimension_scores['accuracy'] = results['overall_score']
        
        return results
    
    def assess_consistency(self, consistency_rules: Dict[str, Dict] = None) -> Dict:
        """
        评估数据一致性
        
        Args:
            consistency_rules (Dict[str, Dict]): 一致性规则
                格式: {'rule_name': {'type': 'cross_column', 'columns': ['col1', 'col2'], 'logic': 'col1 > col2'}}
                
        Returns:
            Dict: 一致性评估结果
        """
        if consistency_rules is None:
            consistency_rules = self._infer_consistency_rules()
        
        results = {
            'dimension': 'consistency',
            'rule_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        total_checks = 0
        consistent_checks = 0
        
        for rule_name, rule in consistency_rules.items():
            rule_type = rule['type']
            
            if rule_type == 'cross_column':
                columns = rule['columns']
                logic = rule['logic']
                
                # 构建一致性检查表达式
                consistent_count = 0
                total_count = len(self.df)
                
                for idx, row in self.df.iterrows():
                    try:
                        # 安全地评估逻辑表达式
                        local_vars = {col: row[col] for col in columns}
                        if eval(logic, {"__builtins__": {}}, local_vars):
                            consistent_count += 1
                    except:
                        # 如果评估失败，视为不一致
                        pass
                
                consistency_score = (consistent_count / total_count) * 100
                
                results['rule_scores'][rule_name] = {
                    'score': consistency_score,
                    'consistent_count': consistent_count,
                    'inconsistent_count': total_count - consistent_count,
                    'total_count': total_count,
                    'inconsistency_percentage': ((total_count - consistent_count) / total_count) * 100
                }
                
                total_checks += total_count
                consistent_checks += consistent_count
                
                # 识别一致性问题
                if consistency_score < 95:
                    results['issues'].append({
                        'rule': rule_name,
                        'type': 'low_consistency',
                        'severity': 'high' if consistency_score < 90 else 'medium',
                        'description': f"规则 {rule_name} 的一致性仅为 {consistency_score:.2f}%"
                    })
            
            elif rule_type == 'date_logic':
                # 日期逻辑一致性检查
                columns = rule['columns']
                start_col = columns[0]
                end_col = columns[1]
                
                consistent_mask = (self.df[start_col] <= self.df[end_col]) | self.df[end_col].isna()
                consistent_count = consistent_mask.sum()
                total_count = len(self.df)
                
                consistency_score = (consistent_count / total_count) * 100
                
                results['rule_scores'][rule_name] = {
                    'score': consistency_score,
                    'consistent_count': consistent_count,
                    'inconsistent_count': total_count - consistent_count,
                    'total_count': total_count,
                    'inconsistency_percentage': ((total_count - consistent_count) / total_count) * 100
                }
                
                total_checks += total_count
                consistent_checks += consistent_count
                
                # 识别一致性问题
                if consistency_score < 95:
                    results['issues'].append({
                        'rule': rule_name,
                        'type': 'low_consistency',
                        'severity': 'high' if consistency_score < 90 else 'medium',
                        'description': f"日期逻辑规则 {rule_name} 的一致性仅为 {consistency_score:.2f}%"
                    })
        
        results['overall_score'] = (consistent_checks / total_checks) * 100 if total_checks > 0 else 100
        self.dimension_scores['consistency'] = results['overall_score']
        
        return results
    
    def assess_timeliness(self, date_column: str, threshold_days: int = 30) -> Dict:
        """
        评估数据时效性
        
        Args:
            date_column (str): 日期列名
            threshold_days (int): 时效性阈值（天数）
            
        Returns:
            Dict: 时效性评估结果
        """
        if date_column not in self.df.columns:
            return {
                'dimension': 'timeliness',
                'overall_score': 0,
                'error': f'列 {date_column} 不存在'
            }
        
        results = {
            'dimension': 'timeliness',
            'column_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        # 转换日期列
        try:
            date_series = pd.to_datetime(self.df[date_column], errors='coerce')
        except:
            return {
                'dimension': 'timeliness',
                'overall_score': 0,
                'error': f'无法转换列 {date_column} 为日期格式'
            }
        
        current_date = datetime.now()
        threshold_date = current_date - timedelta(days=threshold_days)
        
        # 计算时效性得分
        timely_records = (date_series >= threshold_date).sum()
        total_records = len(date_series.dropna())
        
        timeliness_score = (timely_records / total_records) * 100 if total_records > 0 else 100
        
        # 计算平均延迟天数
        delays = (current_date - date_series).dt.days
        avg_delay = delays.mean()
        max_delay = delays.max()
        
        results['column_scores'][date_column] = {
            'score': timeliness_score,
            'timely_count': timely_records,
            'outdated_count': total_records - timely_records,
            'total_count': total_records,
            'outdated_percentage': ((total_records - timely_records) / total_records) * 100 if total_records > 0 else 0,
            'average_delay_days': avg_delay,
            'max_delay_days': max_delay
        }
        
        results['overall_score'] = timeliness_score
        self.dimension_scores['timeliness'] = results['overall_score']
        
        # 识别时效性问题
        if timeliness_score < 90:
            results['issues'].append({
                'column': date_column,
                'type': 'low_timeliness',
                'severity': 'high' if timeliness_score < 80 else 'medium',
                'description': f"列 {date_column} 的时效性仅为 {timeliness_score:.2f}%"
            })
        
        return results
    
    def run_full_assessment(self, config: Dict = None) -> Dict:
        """
        运行全面的数据质量评估
        
        Args:
            config (Dict): 评估配置
            
        Returns:
            Dict: 完整的评估结果
        """
        if config is None:
            config = self._get_default_config()
        
        results = {
            'dataset_info': {
                'shape': self.df.shape,
                'columns': self.df.columns.tolist(),
                'data_types': self.df.dtypes.astype(str).to_dict(),
                'assessment_time': datetime.now().isoformat()
            },
            'dimension_results': {},
            'overall_score': 0,
            'recommendations': []
        }
        
        # 执行各维度评估
        if 'completeness' in config['dimensions']:
            results['dimension_results']['completeness'] = self.assess_completeness(
                config['completeness'].get('columns')
            )
        
        if 'uniqueness' in config['dimensions']:
            results['dimension_results']['uniqueness'] = self.assess_uniqueness(
                config['uniqueness'].get('columns')
            )
        
        if 'validity' in config['dimensions']:
            results['dimension_results']['validity'] = self.assess_validity(
                config['validity'].get('column_rules')
            )
        
        if 'accuracy' in config['dimensions']:
            accuracy_config = config['accuracy']
            results['dimension_results']['accuracy'] = self.assess_accuracy(
                accuracy_config.get('reference_data'),
                accuracy_config.get('key_columns')
            )
        
        if 'consistency' in config['dimensions']:
            results['dimension_results']['consistency'] = self.assess_consistency(
                config['consistency'].get('rules')
            )
        
        if 'timeliness' in config['dimensions']:
            timeliness_config = config['timeliness']
            results['dimension_results']['timeliness'] = self.assess_timeliness(
                timeliness_config.get('date_column'),
                timeliness_config.get('threshold_days', 30)
            )
        
        # 计算总体得分
        dimension_weights = config.get('dimension_weights', {
            'completeness': 0.25,
            'uniqueness': 0.15,
            'validity': 0.20,
            'accuracy': 0.25,
            'consistency': 0.10,
            'timeliness': 0.05
        })
        
        weighted_score = 0
        total_weight = 0
        
        for dimension, result in results['dimension_results'].items():
            if 'overall_score' in result:
                weight = dimension_weights.get(dimension, 1)
                weighted_score += result['overall_score'] * weight
                total_weight += weight
        
        results['overall_score'] = weighted_score / total_weight if total_weight > 0 else 0
        
        # 生成改进建议
        results['recommendations'] = self._generate_recommendations(results)
        
        # 保存结果
        self.results = results
        
        return results
    
    def generate_report(self, output_format: str = 'html', output_path: str = None) -> str:
        """
        生成数据质量报告
        
        Args:
            output_format (str): 输出格式 ('html', 'json', 'markdown')
            output_path (str): 输出路径
            
        Returns:
            str: 报告内容或文件路径
        """
        if not self.results:
            self.run_full_assessment()
        
        if output_format == 'html':
            report = self._generate_html_report()
        elif output_format == 'json':
            report = json.dumps(self.results, indent=2, ensure_ascii=False)
        elif output_format == 'markdown':
            report = self._generate_markdown_report()
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            return output_path
        
        return report
    
    def visualize_results(self, figsize: Tuple[int, int] = (15, 10), save_path: str = None):
        """
        可视化数据质量评估结果
        
        Args:
            figsize (Tuple[int, int]): 图形大小
            save_path (str): 保存路径
            
        Returns:
            None
        """
        if not self.results:
            self.run_full_assessment()
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('数据质量评估结果', fontsize=16)
        
        # 维度得分雷达图
        if self.dimension_scores:
            ax = axes[0, 0]
            self._plot_radar_chart(ax, self.dimension_scores)
            ax.set_title('各维度得分')
        
        # 维度得分柱状图
        if self.dimension_scores:
            ax = axes[0, 1]
            dimensions = list(self.dimension_scores.keys())
            scores = list(self.dimension_scores.values())
            colors = ['green' if score >= 90 else 'orange' if score >= 80 else 'red' for score in scores]
            
            ax.bar(dimensions, scores, color=colors)
            ax.set_ylim(0, 100)
            ax.set_title('各维度得分')
            ax.set_ylabel('得分 (%)')
        
        # 各维度问题数量
        if 'dimension_results' in self.results:
            ax = axes[0, 2]
            issue_counts = []
            dimensions = []
            
            for dimension, result in self.results['dimension_results'].items():
                if 'issues' in result:
                    issue_counts.append(len(result['issues']))
                    dimensions.append(dimension)
            
            if dimensions:
                ax.bar(dimensions, issue_counts, color='red')
                ax.set_title('各维度问题数量')
                ax.set_ylabel('问题数量')
        
        # 数据分布概览
        ax = axes[1, 0]
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            self.df[numeric_cols].hist(ax=ax, bins=20, alpha=0.7)
            ax.set_title('数值型数据分布')
        else:
            ax.text(0.5, 0.5, '无数值型数据', horizontalalignment='center', verticalalignment='center')
            ax.set_title('数据分布')
        
        # 缺失值热图
        ax = axes[1, 1]
        missing_data = self.df.isnull().sum()
        if missing_data.sum() > 0:
            missing_percent = (missing_data / len(self.df)) * 100
            missing_percent = missing_percent[missing_percent > 0].sort_values(ascending=False)
            
            if len(missing_percent) > 0:
                sns.barplot(x=missing_percent.values, y=missing_percent.index, ax=ax)
                ax.set_title('缺失值比例')
                ax.set_xlabel('缺失比例 (%)')
            else:
                ax.text(0.5, 0.5, '无缺失值', horizontalalignment='center', verticalalignment='center')
                ax.set_title('缺失值')
        else:
            ax.text(0.5, 0.5, '无缺失值', horizontalalignment='center', verticalalignment='center')
            ax.set_title('缺失值')
        
        # 综合评分
        ax = axes[1, 2]
        overall_score = self.results.get('overall_score', 0)
        colors = ['green' if overall_score >= 90 else 'orange' if overall_score >= 80 else 'red']
        ax.bar(['综合评分'], [overall_score], color=colors)
        ax.set_ylim(0, 100)
        ax.set_title(f'综合评分: {overall_score:.2f}')
        ax.set_ylabel('得分 (%)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    # 辅助方法
    def _infer_column_rules(self) -> Dict[str, Dict]:
        """推断列的验证规则"""
        rules = {}
        
        for col in self.df.columns:
            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue
                
            # 基于列名推断规则
            col_lower = col.lower()
            
            if 'email' in col_lower:
                rules[col] = {
                    'type': 'regex',
                    'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                }
            elif 'phone' in col_lower or 'tel' in col_lower:
                rules[col] = {
                    'type': 'regex',
                    'pattern': '^1[3-9][0-9]{9}$'  # 中国大陆手机号格式
                }
            elif 'age' in col_lower:
                rules[col] = {
                    'type': 'range',
                    'min': 0,
                    'max': 120
                }
            elif 'price' in col_lower or 'amount' in col_lower or 'cost' in col_lower:
                if col_data.dtype in ['int64', 'float64']:
                    min_val = col_data.min()
                    if min_val >= 0:
                        rules[col] = {
                            'type': 'range',
                            'min': 0,
                            'max': col_data.max() * 1.5
                        }
        
        return rules
    
    def _infer_consistency_rules(self) -> Dict[str, Dict]:
        """推断一致性规则"""
        rules = {}
        
        # 基于列名推断日期逻辑规则
        date_columns = []
        for col in self.df.columns:
            col_lower = col.lower()
            if 'date' in col_lower or 'time' in col_lower:
                date_columns.append(col)
        
        # 如果有开始和结束日期列
        start_date_cols = [col for col in date_columns if 'start' in col.lower() or 'begin' in col.lower()]
        end_date_cols = [col for col in date_columns if 'end' in col.lower() or 'finish' in col.lower()]
        
        for start_col in start_date_cols:
            for end_col in end_date_cols:
                if start_col in self.df.columns and end_col in self.df.columns:
                    rule_name = f"{start_col}_before_{end_col}"
                    rules[rule_name] = {
                        'type': 'date_logic',
                        'columns': [start_col, end_col]
                    }
        
        return rules
    
    def _validate_value(self, value: Any, rule: Dict) -> bool:
        """验证单个值是否符合规则"""
        rule_type = rule['type']
        
        if rule_type == 'regex':
            pattern = rule['pattern']
            return re.match(pattern, str(value)) is not None
        elif rule_type == 'range':
            min_val = rule.get('min')
            max_val = rule.get('max')
            
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
        elif rule_type == 'enum':
            valid_values = rule.get('values', [])
            return value in valid_values
        
        return True
    
    def _assess_accuracy_by_rules(self) -> Dict:
        """基于规则的准确性评估（当没有参考数据时）"""
        results = {
            'dimension': 'accuracy',
            'column_scores': {},
            'overall_score': 0,
            'issues': []
        }
        
        # 基于数据类型和内容评估准确性
        for col in self.df.columns:
            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue
                
            accuracy_score = 100  # 默认满分
            
            # 对数值型数据，检查异常值
            if col_data.dtype in ['int64', 'float64']:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                
                outliers = ((col_data < (q1 - 1.5 * iqr)) | (col_data > (q3 + 1.5 * iqr))).sum()
                outlier_rate = outliers / len(col_data)
                
                # 异常值比例超过5%时，降低准确性评分
                if outlier_rate > 0.05:
                    accuracy_score -= outlier_rate * 50
            
            results['column_scores'][col] = {
                'score': max(accuracy_score, 0),  # 确保得分不低于0
                'assessment_type': 'rule_based'
            }
        
        # 计算总体准确性得分
        if results['column_scores']:
            scores = [col_score['score'] for col_score in results['column_scores'].values()]
            results['overall_score'] = sum(scores) / len(scores)
        else:
            results['overall_score'] = 100
        
        self.dimension_scores['accuracy'] = results['overall_score']
        
        return results
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'dimensions': ['completeness', 'uniqueness', 'validity', 'accuracy', 'consistency'],
            'dimension_weights': {
                'completeness': 0.25,
                'uniqueness': 0.15,
                'validity': 0.20,
                'accuracy': 0.25,
                'consistency': 0.10,
                'timeliness': 0.05
            }
        }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if 'dimension_results' not in results:
            return recommendations
        
        # 基于各维度问题生成建议
        dimension_results = results['dimension_results']
        
        # 完整性问题
        if 'completeness' in dimension_results:
            completeness_issues = dimension_results['completeness'].get('issues', [])
            if completeness_issues:
                recommendations.append(
                    "建议实施数据完整性检查，在数据录入时验证必填字段，"
                    "并定期清理空值数据，提高数据完整性。"
                )
        
        # 唯一性问题
        if 'uniqueness' in dimension_results:
            uniqueness_issues = dimension_results['uniqueness'].get('issues', [])
            if uniqueness_issues:
                recommendations.append(
                    "建议实施重复数据检测机制，建立唯一约束，"
                    "并定期进行数据去重处理。"
                )
        
        # 有效性问题
        if 'validity' in dimension_results:
            validity_issues = dimension_results['validity'].get('issues', [])
            if validity_issues:
                recommendations.append(
                    "建议建立数据格式验证规则，在数据录入时进行实时验证，"
                    "并对现有数据进行格式标准化处理。"
                )
        
        # 准确性问题
        if 'accuracy' in dimension_results:
            accuracy_issues = dimension_results['accuracy'].get('issues', [])
            if accuracy_issues:
                recommendations.append(
                    "建议建立数据准确性检查机制，与权威数据源进行比对，"
                    "并实施数据审核流程确保数据准确性。"
                )
        
        # 一致性问题
        if 'consistency' in dimension_results:
            consistency_issues = dimension_results['consistency'].get('issues', [])
            if consistency_issues:
                recommendations.append(
                    "建议实施跨系统数据同步机制，建立数据一致性检查规则，"
                    "并定期执行一致性验证。"
                )
        
        # 时效性问题
        if 'timeliness' in dimension_results:
            timeliness_issues = dimension_results['timeliness'].get('issues', [])
            if timeliness_issues:
                recommendations.append(
                    "建议优化数据更新流程，实施增量更新机制，"
                    "并建立数据时效性监控确保数据及时更新。"
                )
        
        # 综合评分较低的建议
        overall_score = results.get('overall_score', 100)
        if overall_score < 80:
            recommendations.append(
                "数据质量整体水平较低，建议建立全面的数据质量管理体系，"
                "包括数据质量标准、流程、工具和组织架构。"
            )
        
        return recommendations
    
    def _generate_html_report(self) -> str:
        """生成HTML格式的报告"""
        if not self.results:
            return "<html><body>无评估结果</body></html>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>数据质量评估报告</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-width: 150px; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .bad {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .chart {{ height: 400px; margin: 20px 0; }}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div class="header">
                <h1>数据质量评估报告</h1>
                <p>评估时间: {self.results['dataset_info']['assessment_time']}</p>
                <p>数据集形状: {self.results['dataset_info']['shape']}</p>
            </div>
            
            <div class="section">
                <h2>总体评估</h2>
                <div class="metric">
                    <div>综合评分</div>
                    <div class="score {self._get_score_class(self.results['overall_score'])}">{self.results['overall_score']:.1f}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>维度评估结果</h2>
                <table>
                    <tr>
                        <th>维度</th>
                        <th>得分</th>
                        <th>问题数量</th>
                        <th>状态</th>
                    </tr>
        """
        
        # 添加维度结果表格
        for dimension, result in self.results.get('dimension_results', {}).items():
            if 'overall_score' in result:
                score = result['overall_score']
                issue_count = len(result.get('issues', []))
                status = "良好" if score >= 90 else "一般" if score >= 80 else "需改进"
                status_class = "good" if score >= 90 else "warning" if score >= 80 else "bad"
                
                html += f"""
                    <tr>
                        <td>{dimension}</td>
                        <td class="{self._get_score_class(score)}">{score:.1f}</td>
                        <td>{issue_count}</td>
                        <td class="{status_class}">{status}</td>
                    </tr>
                """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>问题详情</h2>
        """
        
        # 添加问题详情
        has_issues = False
        for dimension, result in self.results.get('dimension_results', {}).items():
            issues = result.get('issues', [])
            if issues:
                has_issues = True
                html += f"<h3>{dimension} 问题</h3><ul>"
                for issue in issues:
                    html += f"<li>{issue['description']}</li>"
                html += "</ul>"
        
        if not has_issues:
            html += "<p>未发现数据质量问题</p>"
        
        html += """
            </div>
            
            <div class="section">
                <h2>改进建议</h2>
                <ol>
        """
        
        # 添加改进建议
        for recommendation in self.results.get('recommendations', []):
            html += f"<li>{recommendation}</li>"
        
        html += """
                </ol>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self) -> str:
        """生成Markdown格式的报告"""
        if not self.results:
            return "# 数据质量评估报告\n\n无评估结果\n"
        
        md = f"""# 数据质量评估报告

## 基本信息

- **评估时间**: {self.results['dataset_info']['assessment_time']}
- **数据集形状**: {self.results['dataset_info']['shape']}

## 总体评估

- **综合评分**: {self.results['overall_score']:.1f} {self._get_score_emoji(self.results['overall_score'])}

## 维度评估结果

| 维度 | 得分 | 问题数量 | 状态 |
|------|------|----------|------|
"""
        
        # 添加维度结果表格
        for dimension, result in self.results.get('dimension_results', {}).items():
            if 'overall_score' in result:
                score = result['overall_score']
                issue_count = len(result.get('issues', []))
                status = "良好" if score >= 90 else "一般" if score >= 80 else "需改进"
                
                md += f"| {dimension} | {score:.1f} | {issue_count} | {status} |\n"
        
        md += "\n## 问题详情\n\n"
        
        # 添加问题详情
        has_issues = False
        for dimension, result in self.results.get('dimension_results', {}).items():
            issues = result.get('issues', [])
            if issues:
                has_issues = True
                md += f"### {dimension} 问题\n\n"
                for issue in issues:
                    md += f"- {issue['description']}\n"
                md += "\n"
        
        if not has_issues:
            md += "未发现数据质量问题\n\n"
        
        md += "## 改进建议\n\n"
        
        # 添加改进建议
        for recommendation in self.results.get('recommendations', []):
            md += f"1. {recommendation}\n"
        
        return md
    
    def _get_score_class(self, score: float) -> str:
        """根据得分获取CSS类名"""
        return "good" if score >= 90 else "warning" if score >= 80 else "bad"
    
    def _get_score_emoji(self, score: float) -> str:
        """根据得分获取表情符号"""
        return "🟢" if score >= 90 else "🟡" if score >= 80 else "🔴"
    
    def _plot_radar_chart(self, ax, dimensions_scores):
        """绘制雷达图"""
        if not dimensions_scores:
            ax.text(0.5, 0.5, '无数据', horizontalalignment='center', verticalalignment='center')
            return
        
        # 准备数据
        categories = list(dimensions_scores.keys())
        values = list(dimensions_scores.values())
        
        # 计算角度
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # 闭合图形
        values += values[:1]  # 闭合图形
        
        # 绘制雷达图
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('各维度得分')


# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['张三', '李四', '王五', '赵六', '钱七', '孙八', None, '周九', '吴十', '郑十一'],
        'email': [
            'zhangsan@example.com',
            'lisi@example.com',
            'wangwu@example.com',
            'zhaoliu@example.com',
            'qianqi@example.com',
            'sunba@example.com',
            'invalid-email',  # 无效邮箱
            'zhoujiu@example.com',
            'wushi@example.com',
            'zhengshiyi@example.com'
        ],
        'phone': [
            '13812345678',
            '13912345678',
            '13612345678',
            '13712345678',
            '13512345678',
            '13412345678',
            '13312345678',
            '13212345678',
            '13112345678',
            'invalid-phone'  # 无效手机号
        ],
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 200],  # 200是异常值
        'registration_date': [
            '2023-01-01',
            '2023-01-15',
            '2023-02-01',
            '2023-02-15',
            '2023-03-01',
            '2023-03-15',
            '2023-04-01',
            '2023-04-15',
            '2023-05-01',
            '2023-05-15'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # 创建评估器
    assessor = DataQualityAssessment(df)
    
    # 配置评估规则
    config = {
        'dimensions': ['completeness', 'uniqueness', 'validity', 'accuracy', 'consistency'],
        'completeness': {
            'columns': ['name', 'email', 'phone']
        },
        'uniqueness': {
            'columns': ['customer_id', 'email']
        },
        'validity': {
            'column_rules': {
                'email': {
                    'type': 'regex',
                    'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                },
                'phone': {
                    'type': 'regex',
                    'pattern': '^1[3-9][0-9]{9}$'
                },
                'age': {
                    'type': 'range',
                    'min': 0,
                    'max': 120
                }
            }
        },
        'timeliness': {
            'date_column': 'registration_date',
            'threshold_days': 365
        },
        'consistency': {
            'rules': {
                'age_range': {
                    'type': 'cross_column',
                    'columns': ['age'],
                    'logic': '0 <= age <= 120'
                }
            }
        }
    }
    
    # 运行评估
    results = assessor.run_full_assessment(config)
    
    # 生成报告
    html_report = assessor.generate_report('html')
    markdown_report = assessor.generate_report('markdown')
    
    # 保存报告
    with open('data_quality_report.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    with open('data_quality_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    # 可视化结果
    assessor.visualize_results(save_path='data_quality_visualization.png')
    
    print("数据质量评估完成！")
    print(f"综合评分: {results['overall_score']:.2f}")
    print(f"HTML报告: data_quality_report.html")
    print(f"Markdown报告: data_quality_report.md")
    print(f"可视化图表: data_quality_visualization.png")