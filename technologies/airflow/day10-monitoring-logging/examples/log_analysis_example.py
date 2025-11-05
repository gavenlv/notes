#!/usr/bin/env python3
"""
Airflow日志分析示例脚本

这个脚本演示了如何分析Airflow任务日志，提取有用信息，
并生成报告或触发告警。
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AirflowLogAnalyzer:
    """Airflow日志分析器"""
    
    def __init__(self, log_directory: str):
        """
        初始化日志分析器
        
        Args:
            log_directory: Airflow日志目录路径
        """
        self.log_directory = log_directory
        self.log_patterns = {
            'error': re.compile(r'(ERROR|CRITICAL)'),
            'warning': re.compile(r'WARNING'),
            'duration': re.compile(r'Finished \[(.*?)\]'),
            'task_state': re.compile(r'Marking task as (SUCCESS|FAILED|UPSTREAM_FAILED)'),
        }
        
    def scan_logs(self, days_back: int = 7) -> List[str]:
        """
        扫描指定天数内的日志文件
        
        Args:
            days_back: 回溯天数
            
        Returns:
            日志文件路径列表
        """
        logger.info(f"Scanning logs from last {days_back} days")
        cutoff_date = datetime.now() - timedelta(days=days_back)
        log_files = []
        
        for root, dirs, files in os.walk(self.log_directory):
            for file in files:
                if file.endswith('.log'):
                    file_path = os.path.join(root, file)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_modified >= cutoff_date:
                        log_files.append(file_path)
                        
        logger.info(f"Found {len(log_files)} log files")
        return log_files
    
    def analyze_task_performance(self, log_files: List[str]) -> Dict:
        """
        分析任务性能
        
        Args:
            log_files: 日志文件列表
            
        Returns:
            性能分析结果
        """
        logger.info("Analyzing task performance")
        performance_data = defaultdict(list)
        task_durations = {}
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 提取任务持续时间
                duration_matches = self.log_patterns['duration'].findall(content)
                if duration_matches:
                    for match in duration_matches:
                        try:
                            # 解析时间戳计算持续时间
                            timestamps = match.split(' -> ')
                            if len(timestamps) == 2:
                                start_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S')
                                end_time = datetime.strptime(timestamps[1], '%Y-%m-%d %H:%M:%S')
                                duration = (end_time - start_time).total_seconds()
                                
                                # 从文件路径提取DAG和任务信息
                                path_parts = log_file.split(os.sep)
                                if len(path_parts) >= 3:
                                    dag_id = path_parts[-4]
                                    task_id = path_parts[-3]
                                    key = f"{dag_id}.{task_id}"
                                    performance_data[key].append(duration)
                        except Exception as e:
                            logger.warning(f"Error parsing duration in {log_file}: {e}")
                            
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
                
        # 计算统计数据
        stats = {}
        for task_key, durations in performance_data.items():
            if durations:
                stats[task_key] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'p95_duration': sorted(durations)[int(0.95 * len(durations))]
                }
                
        return stats
    
    def count_log_levels(self, log_files: List[str]) -> Dict[str, int]:
        """
        统计日志级别分布
        
        Args:
            log_files: 日志文件列表
            
        Returns:
            日志级别统计
        """
        logger.info("Counting log levels")
        level_counts = Counter()
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if self.log_patterns['error'].search(line):
                            level_counts['ERROR'] += 1
                        elif self.log_patterns['warning'].search(line):
                            level_counts['WARNING'] += 1
                        else:
                            level_counts['INFO'] += 1
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
                
        return dict(level_counts)
    
    def detect_failures(self, log_files: List[str]) -> List[Dict]:
        """
        检测任务失败
        
        Args:
            log_files: 日志文件列表
            
        Returns:
            失败任务列表
        """
        logger.info("Detecting task failures")
        failures = []
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                failure_matches = self.log_patterns['task_state'].findall(content)
                if 'FAILED' in failure_matches:
                    # 提取失败信息
                    path_parts = log_file.split(os.sep)
                    if len(path_parts) >= 4:
                        failure_info = {
                            'dag_id': path_parts[-4],
                            'task_id': path_parts[-3],
                            'execution_date': path_parts[-2],
                            'try_number': path_parts[-1].replace('.log', ''),
                            'log_file': log_file
                        }
                        failures.append(failure_info)
                        
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
                
        return failures
    
    def generate_report(self, days_back: int = 7) -> Dict:
        """
        生成日志分析报告
        
        Args:
            days_back: 分析天数
            
        Returns:
            分析报告
        """
        logger.info("Generating log analysis report")
        log_files = self.scan_logs(days_back)
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'period_days': days_back,
            'total_log_files': len(log_files),
            'performance_stats': self.analyze_task_performance(log_files),
            'log_level_distribution': self.count_log_levels(log_files),
            'failures': self.detect_failures(log_files)
        }
        
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Airflow Log Analyzer')
    parser.add_argument('--log-dir', required=True, help='Airflow log directory')
    parser.add_argument('--days', type=int, default=7, help='Days to analyze (default: 7)')
    parser.add_argument('--output', help='Output JSON file for report')
    
    args = parser.parse_args()
    
    # 创建分析器实例
    analyzer = AirflowLogAnalyzer(args.log_dir)
    
    # 生成报告
    report = analyzer.generate_report(args.days)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2, default=str))
        
    # 打印摘要
    print("\n=== Airflow Log Analysis Summary ===")
    print(f"Period: Last {args.days} days")
    print(f"Total log files analyzed: {report['total_log_files']}")
    print(f"Error logs: {report['log_level_distribution'].get('ERROR', 0)}")
    print(f"Warning logs: {report['log_level_distribution'].get('WARNING', 0)}")
    print(f"Failed tasks: {len(report['failures'])}")
    
    if report['failures']:
        print("\nRecent failures:")
        for failure in report['failures'][:5]:  # 显示最近5个失败
            print(f"  - DAG: {failure['dag_id']}, Task: {failure['task_id']}")

if __name__ == '__main__':
    main()