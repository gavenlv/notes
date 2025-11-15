#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第10章：数据质量未来趋势与新技术 - 代码示例
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class IntelligentDataQualityAssessor:
    """智能化数据质量评估器"""
    
    def __init__(self):
        # 质量维度权重
        self.dimension_weights = {
            'completeness': 0.2,     # 完整性
            'accuracy': 0.25,        # 准确性
            'consistency': 0.15,     # 一致性
            'timeliness': 0.15,      # 及时性
            'uniqueness': 0.15,      # 唯一性
            'validity': 0.1         # 有效性
        }
        
        # 自适应阈值
        self.adaptive_thresholds = {}
    
    def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
        """计算完整性得分"""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness_rate = (total_cells - missing_cells) / total_cells
        return round(completeness_rate, 4)
    
    def _calculate_accuracy_score(self, df: pd.DataFrame, reference_data: pd.DataFrame = None) -> float:
        """计算准确性得分"""
        if reference_data is None:
            # 使用启发式方法估算准确性
            accuracy_indicators = []
            
            # 检查数值字段的合理性
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                # 检查是否有异常大的数值
                max_val = df[col].max()
                if max_val > 1e10:  # 假设超过1e10可能是异常值
                    accuracy_indicators.append(0.8)
                else:
                    accuracy_indicators.append(1.0)
            
            # 检查日期字段的合理性
            date_cols = df.select_dtypes(include=['datetime64']).columns
            for col in date_cols:
                # 检查是否在未来或过于久远
                future_dates = (df[col] > datetime.now() + timedelta(days=365)).sum()
                past_dates = (df[col] < datetime.now() - timedelta(days=365*100)).sum()
                if future_dates > 0 or past_dates > 0:
                    accuracy_indicators.append(0.8)
                else:
                    accuracy_indicators.append(1.0)
            
            return round(np.mean(accuracy_indicators) if accuracy_indicators else 0.9, 4)
        else:
            # 与参考数据对比计算准确性
            common_cols = set(df.columns) & set(reference_data.columns)
            if not common_cols:
                return 0.5
            
            match_count = 0
            total_count = 0
            
            for col in common_cols:
                match_count += (df[col] == reference_data[col]).sum()
                total_count += len(df)
            
            return round(match_count / total_count, 4) if total_count > 0 else 0.0
    
    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """计算一致性得分"""
        consistency_scores = []
        
        # 检查同一字段在不同记录中的格式一致性
        for col in df.columns:
            sample_values = df[col].dropna().head(100)  # 取样本检查
            if len(sample_values) == 0:
                continue
                
            # 对于字符串字段，检查格式一致性
            if df[col].dtype == 'object':
                # 检查是否都是相似长度
                lengths = sample_values.astype(str).str.len()
                std_length = lengths.std()
                mean_length = lengths.mean()
                
                if mean_length > 0:
                    consistency_ratio = 1 - min(std_length / mean_length, 1)
                    consistency_scores.append(max(consistency_ratio, 0))
            
            # 对于数值字段，检查分布的一致性
            elif df[col].dtype in ['int64', 'float64']:
                # 使用变异系数衡量一致性
                cv = df[col].std() / (df[col].mean() + 1e-8)  # 避免除零
                consistency_scores.append(max(1 - min(cv / 2, 1), 0))  # 假设CV<2为良好
        
        return round(np.mean(consistency_scores) if consistency_scores else 0.9, 4)
    
    def _calculate_timeliness_score(self, df: pd.DataFrame, timestamp_col: str = None) -> float:
        """计算及时性得分"""
        if timestamp_col and timestamp_col in df.columns:
            # 如果有时间戳列，检查数据的新鲜度
            latest_time = pd.to_datetime(df[timestamp_col]).max()
            current_time = datetime.now()
            time_diff_hours = (current_time - latest_time).total_seconds() / 3600
            
            # 假设24小时内为满分，超过一周为最低分
            if time_diff_hours <= 24:
                return 1.0
            elif time_diff_hours <= 168:  # 一周内
                return max(1 - (time_diff_hours - 24) / 144, 0.1)
            else:
                return 0.1
        else:
            # 没有时间戳信息，默认给中等分数
            return 0.7
    
    def _calculate_uniqueness_score(self, df: pd.DataFrame) -> float:
        """计算唯一性得分"""
        duplicate_rows = df.duplicated().sum()
        uniqueness_rate = 1 - (duplicate_rows / len(df))
        return round(uniqueness_rate, 4)
    
    def _calculate_validity_score(self, df: pd.DataFrame) -> float:
        """计算有效性得分"""
        validity_scores = []
        
        for col in df.columns:
            # 检查数据类型的有效性
            if df[col].dtype == 'object':
                # 对字符串字段，检查是否包含大量无效字符
                invalid_chars_ratio = df[col].astype(str).str.contains(r'[^\w\s\-_.@]').mean()
                validity_scores.append(1 - invalid_chars_ratio)
            else:
                # 对数值字段，检查NaN比例
                nan_ratio = df[col].isnull().mean()
                validity_scores.append(1 - nan_ratio)
        
        return round(np.mean(validity_scores) if validity_scores else 0.9, 4)
    
    def assess_quality(self, df: pd.DataFrame, reference_data: pd.DataFrame = None, 
                      timestamp_col: str = None) -> Dict:
        """
        智能化评估数据质量
        
        Args:
            df: 待评估的数据框
            reference_data: 参考数据（用于准确性评估）
            timestamp_col: 时间戳列名（用于及时性评估）
            
        Returns:
            质量评估结果字典
        """
        # 计算各个维度得分
        completeness = self._calculate_completeness_score(df)
        accuracy = self._calculate_accuracy_score(df, reference_data)
        consistency = self._calculate_consistency_score(df)
        timeliness = self._calculate_timeliness_score(df, timestamp_col)
        uniqueness = self._calculate_uniqueness_score(df)
        validity = self._calculate_validity_score(df)
        
        # 计算综合得分
        dimensions = {
            'completeness': completeness,
            'accuracy': accuracy,
            'consistency': consistency,
            'timeliness': timeliness,
            'uniqueness': uniqueness,
            'validity': validity
        }
        
        overall_score = sum(
            dimensions[dim] * self.dimension_weights[dim] 
            for dim in dimensions
        )
        
        return {
            'overall_score': round(overall_score, 4),
            'dimensions': dimensions,
            'assessment_time': datetime.now().isoformat(),
            'record_count': len(df)
        }


class DeepAnomalyDetector:
    """深度异常检测器"""
    
    def __init__(self):
        self.anomaly_patterns = {}
        self.model_params = {}
    
    def detect_statistical_anomalies(self, df: pd.DataFrame, threshold: float = 3.0) -> Dict:
        """
        基于统计学的异常检测
        
        Args:
            df: 数据框
            threshold: Z-score阈值
            
        Returns:
            异常检测结果
        """
        anomalies = {}
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            # 计算Z-score
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            anomaly_indices = df[z_scores > threshold].index.tolist()
            
            if anomaly_indices:
                anomalies[col] = {
                    'anomaly_count': len(anomaly_indices),
                    'anomaly_indices': anomaly_indices[:10],  # 只显示前10个
                    'anomaly_values': df.loc[anomaly_indices[:10], col].tolist()
                }
        
        return {
            'method': 'statistical_zscore',
            'threshold': threshold,
            'anomalies': anomalies,
            'total_anomalies': sum(len(v['anomaly_indices']) for v in anomalies.values())
        }
    
    def detect_isolation_forest_anomalies(self, df: pd.DataFrame, contamination: float = 0.1) -> Dict:
        """
        基于孤立森林的异常检测
        
        Args:
            df: 数据框
            contamination: 异常值比例预期
            
        Returns:
            异常检测结果
        """
        try:
            from sklearn.ensemble import IsolationForest
            
            # 选择数值列进行分析
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                return {'method': 'isolation_forest', 'error': 'No numeric columns found'}
            
            # 初始化孤立森林模型
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            
            # 训练模型并预测
            predictions = iso_forest.fit_predict(numeric_df)
            
            # 获取异常点索引 (-1表示异常)
            anomaly_indices = np.where(predictions == -1)[0].tolist()
            
            return {
                'method': 'isolation_forest',
                'contamination': contamination,
                'anomaly_count': len(anomaly_indices),
                'anomaly_indices': anomaly_indices[:20],  # 显示前20个
                'anomaly_percentage': len(anomaly_indices) / len(df) * 100
            }
            
        except ImportError:
            return {'method': 'isolation_forest', 'error': 'scikit-learn not installed'}
        except Exception as e:
            return {'method': 'isolation_forest', 'error': str(e)}
    
    def detect_pattern_anomalies(self, df: pd.DataFrame) -> Dict:
        """
        基于模式识别的异常检测
        
        Args:
            df: 数据框
            
        Returns:
            模式异常检测结果
        """
        pattern_anomalies = {}
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # 分析字符串模式
                value_counts = df[col].value_counts()
                
                # 检测极低频的异常值
                threshold = len(df) * 0.001  # 占比小于0.1%视为异常
                rare_values = value_counts[value_counts < threshold]
                
                if len(rare_values) > 0:
                    pattern_anomalies[col] = {
                        'rare_value_count': len(rare_values),
                        'rare_values': rare_values.head(10).to_dict()
                    }
        
        return {
            'method': 'pattern_recognition',
            'anomalies': pattern_anomalies,
            'total_columns_with_anomalies': len(pattern_anomalies)
        }


class DataLineageTracker:
    """数据血缘追踪器"""
    
    def __init__(self):
        self.lineage_graph = {}
        self.data_operations = []
    
    def record_data_source(self, source_id: str, source_info: Dict):
        """记录数据源信息"""
        self.lineage_graph[source_id] = {
            'type': 'source',
            'info': source_info,
            'created_at': datetime.now().isoformat()
        }
    
    def record_transformation(self, transform_id: str, input_sources: List[str], 
                           output_dataset: str, transform_info: Dict):
        """记录数据转换过程"""
        self.lineage_graph[transform_id] = {
            'type': 'transformation',
            'input_sources': input_sources,
            'output_dataset': output_dataset,
            'info': transform_info,
            'created_at': datetime.now().isoformat()
        }
        
        # 记录操作历史
        self.data_operations.append({
            'operation_id': transform_id,
            'type': 'transformation',
            'inputs': input_sources,
            'output': output_dataset,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_data_sink(self, sink_id: str, input_transforms: List[str], sink_info: Dict):
        """记录数据汇信息"""
        self.lineage_graph[sink_id] = {
            'type': 'sink',
            'input_transforms': input_transforms,
            'info': sink_info,
            'created_at': datetime.now().isoformat()
        }
    
    def get_lineage_trace(self, dataset_id: str) -> Dict:
        """获取指定数据集的血缘追踪信息"""
        trace = {
            'dataset_id': dataset_id,
            'ancestors': [],
            'descendants': [],
            'full_lineage': {}
        }
        
        # 向上追溯血缘
        def trace_ancestors(node_id, ancestors_list):
            node = self.lineage_graph.get(node_id, {})
            if node.get('type') == 'transformation':
                for input_source in node.get('input_sources', []):
                    ancestors_list.append(input_source)
                    trace_ancestors(input_source, ancestors_list)
            elif node.get('type') == 'source':
                ancestors_list.append(node_id)
        
        # 向下追溯影响
        def trace_descendants(node_id, descendants_list):
            for key, node in self.lineage_graph.items():
                if node.get('type') == 'transformation' and node_id in node.get('input_sources', []):
                    descendants_list.append(key)
                    trace_descendants(key, descendants_list)
                elif node.get('type') == 'sink' and node_id in node.get('input_transforms', []):
                    descendants_list.append(key)
        
        trace_ancestors(dataset_id, trace['ancestors'])
        trace_descendants(dataset_id, trace['descendants'])
        trace['full_lineage'] = self.lineage_graph
        
        return trace
    
    def visualize_lineage(self, dataset_id: str) -> str:
        """生成血缘关系可视化文本"""
        trace = self.get_lineage_trace(dataset_id)
        
        visualization = f"数据血缘追踪图 - 数据集: {dataset_id}\n"
        visualization += "=" * 50 + "\n"
        
        # 显示祖先节点
        if trace['ancestors']:
            visualization += "上游数据源:\n"
            for ancestor in trace['ancestors']:
                node_info = self.lineage_graph.get(ancestor, {})
                node_type = node_info.get('type', 'unknown')
                visualization += f"  ← {ancestor} [{node_type}]\n"
        
        # 显示当前节点
        visualization += f"\n当前数据集: {dataset_id}\n"
        
        # 显示后代节点
        if trace['descendants']:
            visualization += "\n下游影响:\n"
            for descendant in trace['descendants']:
                node_info = self.lineage_graph.get(descendant, {})
                node_type = node_info.get('type', 'unknown')
                visualization += f"  → {descendant} [{node_type}]\n"
        
        return visualization


def simulate_data_quality_future_demo():
    """模拟数据质量未来技术演示"""
    print("=== 第10章：数据质量未来趋势与新技术 代码示例 ===\n")
    
    # 1. 智能化数据质量评估示例
    print("1. 智能化数据质量评估示例")
    print("-" * 40)
    
    # 创建模拟数据
    np.random.seed(42)
    demo_data = pd.DataFrame({
        'id': range(1, 1001),
        'name': [f'user_{i}' for i in range(1, 1001)],
        'age': np.random.randint(18, 80, 1000),
        'salary': np.random.normal(50000, 15000, 1000),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 1000),
        'join_date': pd.date_range('2020-01-01', periods=1000, freq='D'),
        'email': [f'user{i}@company.com' for i in range(1, 1001)]
    })
    
    # 添加一些数据质量问题
    # 1. 添加缺失值
    demo_data.loc[np.random.choice(demo_data.index, 50, replace=False), 'age'] = np.nan
    demo_data.loc[np.random.choice(demo_data.index, 30, replace=False), 'salary'] = np.nan
    
    # 2. 添加异常值
    demo_data.loc[np.random.choice(demo_data.index, 5, replace=False), 'age'] = [150, -5, 200, -10, 180]
    demo_data.loc[np.random.choice(demo_data.index, 5, replace=False), 'salary'] = [1e9, -50000, 2e9, -100000, 3e9]
    
    # 3. 添加重复记录
    duplicate_rows = demo_data.sample(20)
    demo_data = pd.concat([demo_data, duplicate_rows], ignore_index=True)
    
    # 使用智能评估器评估数据质量
    quality_assessor = IntelligentDataQualityAssessor()
    quality_report = quality_assessor.assess_quality(demo_data, timestamp_col='join_date')
    
    print(f"数据集记录数: {quality_report['record_count']}")
    print(f"数据质量综合得分: {quality_report['overall_score']}")
    print("\n各维度得分:")
    for dimension, score in quality_report['dimensions'].items():
        print(f"  {dimension}: {score}")
    
    print("\n" + "="*60 + "\n")
    
    # 2. 深度异常检测示例
    print("2. 深度异常检测示例")
    print("-" * 40)
    
    anomaly_detector = DeepAnomalyDetector()
    
    # 统计学异常检测
    stat_anomalies = anomaly_detector.detect_statistical_anomalies(demo_data, threshold=3.0)
    print("基于Z-score的统计异常检测:")
    print(f"  发现异常值数量: {stat_anomalies['total_anomalies']}")
    if stat_anomalies['anomalies']:
        print("  异常字段详情:")
        for col, details in list(stat_anomalies['anomalies'].items())[:3]:  # 只显示前3个
            print(f"    {col}: {details['anomaly_count']}个异常值")
    
    # 孤立森林异常检测
    iso_anomalies = anomaly_detector.detect_isolation_forest_anomalies(demo_data, contamination=0.05)
    print("\n基于孤立森林的异常检测:")
    if 'error' in iso_anomalies:
        print(f"  错误: {iso_anomalies['error']}")
    else:
        print(f"  发现异常值数量: {iso_anomalies['anomaly_count']}")
        print(f"  异常值占比: {iso_anomalies['anomaly_percentage']:.2f}%")
    
    # 模式异常检测
    pattern_anomalies = anomaly_detector.detect_pattern_anomalies(demo_data)
    print("\n基于模式识别的异常检测:")
    print(f"  发现异常的字段数: {pattern_anomalies['total_columns_with_anomalies']}")
    if pattern_anomalies['anomalies']:
        print("  异常字段详情:")
        for col, details in list(pattern_anomalies['anomalies'].items())[:3]:
            print(f"    {col}: {details['rare_value_count']}个罕见值")
    
    print("\n" + "="*60 + "\n")
    
    # 3. 数据血缘追踪示例
    print("3. 数据血缘追踪示例")
    print("-" * 40)
    
    lineage_tracker = DataLineageTracker()
    
    # 记录数据源
    lineage_tracker.record_data_source('source_db', {
        'type': 'MySQL Database',
        'host': 'db.company.com',
        'database': 'hr_system'
    })
    
    lineage_tracker.record_data_source('api_source', {
        'type': 'REST API',
        'endpoint': 'https://api.company.com/employees'
    })
    
    # 记录数据转换过程
    lineage_tracker.record_transformation('etl_process_1', 
                                        ['source_db', 'api_source'],
                                        'cleaned_employee_data',
                                        {
                                            'steps': ['data_extraction', 'data_cleaning', 'data_validation'],
                                            'tools': ['pandas', 'numpy']
                                        })
    
    lineage_tracker.record_transformation('aggregation_process', 
                                        ['etl_process_1'],
                                        'employee_summary',
                                        {
                                            'steps': ['grouping', 'aggregation', 'calculation'],
                                            'metrics': ['avg_salary', 'dept_count', 'age_distribution']
                                        })
    
    # 记录数据汇
    lineage_tracker.record_data_sink('data_warehouse', 
                                   ['aggregation_process'],
                                   {
                                       'type': 'Snowflake',
                                       'schema': 'analytics',
                                       'table': 'employee_summary'
                                   })
    
    lineage_tracker.record_data_sink('dashboard', 
                                   ['etl_process_1'],
                                   {
                                       'type': 'Tableau Server',
                                       'dashboard': 'Employee Analytics'
                                   })
    
    # 可视化血缘关系
    lineage_visualization = lineage_tracker.visualize_lineage('employee_summary')
    print(lineage_visualization)
    
    print("="*60)
    print("数据质量未来趋势与新技术演示完成!")


if __name__ == "__main__":
    simulate_data_quality_future_demo()