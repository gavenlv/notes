#!/usr/bin/env python3
"""
JMeter性能分析工具
用于分析JMeter测试结果，提供优化建议
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os

class JMeterPerformanceAnalyzer:
    def __init__(self, jtl_file_path):
        self.jtl_file = jtl_file_path
        self.data = None
        self.optimization_suggestions = []
        
    def load_data(self):
        """加载JMeter测试结果数据"""
        try:
            self.data = pd.read_csv(self.jtl_file)
            print(f"成功加载数据，共 {len(self.data)} 条记录")
            return True
        except Exception as e:
            print(f"加载数据失败: {e}")
            return False
    
    def analyze_performance(self):
        """分析性能指标"""
        if self.data is None:
            print("请先加载数据")
            return
            
        metrics = {
            'total_requests': len(self.data),
            'success_rate': (self.data['success'] == 'true').sum() / len(self.data) * 100,
            'error_rate': (self.data['success'] == 'false').sum() / len(self.data) * 100,
            'avg_response_time': self.data['elapsed'].mean(),
            'p95_response_time': self.data['elapsed'].quantile(0.95),
            'p99_response_time': self.data['elapsed'].quantile(0.99),
            'throughput': len(self.data) / (self.data['timeStamp'].max() - self.data['timeStamp'].min()) * 1000
        }
        
        return metrics
    
    def generate_suggestions(self, metrics):
        """生成优化建议"""
        suggestions = []
        
        # 响应时间优化建议
        if metrics['avg_response_time'] > 1000:
            suggestions.append({
                'category': '响应时间',
                'issue': '平均响应时间超过1秒',
                'severity': '警告',
                'suggestion': '检查服务器配置、数据库查询优化、代码优化'
            })
        
        # 错误率优化建议
        if metrics['error_rate'] > 5:
            suggestions.append({
                'category': '错误率',
                'issue': '错误率超过5%',
                'severity': '错误',
                'suggestion': '检查应用程序错误、网络连接、超时设置'
            })
        
        # 吞吐量优化建议
        if metrics['throughput'] < 10:
            suggestions.append({
                'category': '吞吐量',
                'issue': '吞吐量较低',
                'severity': '建议',
                'suggestion': '考虑增加并发用户数、优化服务器配置'
            })
            
        return suggestions
    
    def create_performance_report(self):
        """创建性能报告"""
        metrics = self.analyze_performance()
        suggestions = self.generate_suggestions(metrics)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'data_file': self.jtl_file,
            'performance_metrics': metrics,
            'optimization_suggestions': suggestions,
            'summary': {
                'total_requests': len(self.data),
                'test_duration': (self.data['timeStamp'].max() - self.data['timeStamp'].min()) / 1000,
                'overall_status': '需要优化' if metrics['error_rate'] > 5 or metrics['p95_response_time'] > 3000 else '良好'
            }
        }
        
        # 保存报告
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"性能报告已保存到: {report_file}")
        return report

# 使用示例
if __name__ == "__main__":
    analyzer = JMeterPerformanceAnalyzer("test_results.jtl")
    if analyzer.load_data():
        report = analyzer.create_performance_report()
        print("性能分析完成!")