#!/usr/bin/env python3
"""
Airflow性能分析工具

该脚本用于分析Airflow任务执行日志和性能数据，生成详细的性能分析报告。
"""

import re
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class TaskExecutionRecord:
    """任务执行记录"""
    dag_id: str
    task_id: str
    execution_date: datetime
    start_date: datetime
    end_date: datetime
    duration: float
    state: str
    try_number: int
    hostname: str
    pool: str
    queue: str
    priority_weight: int


@dataclass
class PerformanceAnalysis:
    """性能分析结果"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_duration: float
    median_duration: float
    longest_duration: float
    shortest_duration: float
    success_rate: float
    retry_rate: float
    most_frequent_dags: List[Tuple[str, int]]
    slowest_tasks: List[Tuple[str, str, float]]
    fastest_tasks: List[Tuple[str, str, float]]
    duration_distribution: Dict[str, int]
    hourly_execution_pattern: Dict[int, int]
    resource_utilization: Dict[str, float]


class LogParser:
    """日志解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 定义日志模式
        self.task_pattern = re.compile(
            r'\[(?P<timestamp>[^\]]+)\] \{(?P<module>[^}]+)\} (?P<level>\w+) - '
            r'Executing <Task\((?P<task_type>[^)]+)\): (?P<task_id>[^>]+)> on (?P<execution_date>[^(]+)'
        )
        
        self.duration_pattern = re.compile(
            r'Finished \[TaskDuration\]: Task ran from (?P<start>[^ ]+) to (?P<end>[^ ]+) '
            r'\((?P<duration>[\d.]+) seconds\)'
        )
    
    def parse_log_file(self, log_file_path: str) -> List[TaskExecutionRecord]:
        """解析日志文件"""
        records = []
        current_record = None
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 查找任务执行开始记录
                    task_match = self.task_pattern.search(line)
                    if task_match:
                        if current_record:
                            records.append(current_record)
                        
                        # 解析时间戳
                        timestamp_str = task_match.group('timestamp')
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        except ValueError:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        current_record = {
                            'timestamp': timestamp,
                            'task_id': task_match.group('task_id'),
                            'task_type': task_match.group('task_type'),
                            'execution_date': task_match.group('execution_date').strip()
                        }
                        continue
                    
                    # 查找执行时间记录
                    duration_match = self.duration_pattern.search(line)
                    if duration_match and current_record:
                        start_str = duration_match.group('start')
                        end_str = duration_match.group('end')
                        duration = float(duration_match.group('duration'))
                        
                        # 更新当前记录
                        current_record.update({
                            'start_time': start_str,
                            'end_time': end_str,
                            'duration': duration
                        })
                        
                        # 创建任务执行记录
                        try:
                            record = TaskExecutionRecord(
                                dag_id="unknown",  # 从日志中无法直接获取
                                task_id=current_record['task_id'],
                                execution_date=datetime.strptime(
                                    current_record['execution_date'], 
                                    '%Y-%m-%d %H:%M:%S%z'
                                ),
                                start_date=datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S'),
                                end_date=datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S'),
                                duration=duration,
                                state="success",  # 假设成功
                                try_number=1,
                                hostname="unknown",
                                pool="default",
                                queue="default",
                                priority_weight=1
                            )
                            records.append(record)
                        except Exception as e:
                            self.logger.warning(f"解析日志行 {line_num} 时出错: {e}")
                        
                        current_record = None
                        
        except FileNotFoundError:
            self.logger.error(f"日志文件未找到: {log_file_path}")
        except Exception as e:
            self.logger.error(f"解析日志文件时出错: {e}")
        
        return records


class DatabaseAnalyzer:
    """数据库分析器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def fetch_task_executions(self, 
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> List[TaskExecutionRecord]:
        """从数据库获取任务执行记录"""
        records = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建查询语句
                query = """
                    SELECT 
                        dag_id, task_id, execution_date, start_date, end_date,
                        duration, state, try_number, hostname, pool, queue, priority_weight
                    FROM task_instance
                    WHERE 1=1
                """
                params = []
                
                if start_date:
                    query += " AND execution_date >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND execution_date <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY execution_date DESC"
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    try:
                        record = TaskExecutionRecord(
                            dag_id=row[0],
                            task_id=row[1],
                            execution_date=datetime.fromisoformat(row[2]),
                            start_date=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
                            end_date=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                            duration=float(row[5]) if row[5] else 0.0,
                            state=row[6] or "unknown",
                            try_number=int(row[7]) if row[7] else 1,
                            hostname=row[8] or "unknown",
                            pool=row[9] or "default",
                            queue=row[10] or "default",
                            priority_weight=int(row[11]) if row[11] else 1
                        )
                        records.append(record)
                    except Exception as e:
                        self.logger.warning(f"解析数据库记录时出错: {e}")
                        
        except Exception as e:
            self.logger.error(f"查询数据库时出错: {e}")
        
        return records


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_task_executions(self, records: List[TaskExecutionRecord]) -> PerformanceAnalysis:
        """分析任务执行记录"""
        if not records:
            return PerformanceAnalysis(
                total_tasks=0, successful_tasks=0, failed_tasks=0,
                average_duration=0, median_duration=0, longest_duration=0, shortest_duration=0,
                success_rate=0, retry_rate=0,
                most_frequent_dags=[], slowest_tasks=[], fastest_tasks=[],
                duration_distribution={}, hourly_execution_pattern={},
                resource_utilization={}
            )
        
        # 基础统计
        total_tasks = len(records)
        successful_tasks = sum(1 for r in records if r.state.lower() == 'success')
        failed_tasks = sum(1 for r in records if r.state.lower() == 'failed')
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        # 重试率
        total_tries = sum(r.try_number for r in records)
        retry_rate = (total_tries - total_tasks) / total_tasks if total_tasks > 0 else 0
        
        # 执行时间统计
        durations = [r.duration for r in records if r.duration > 0]
        average_duration = sum(durations) / len(durations) if durations else 0
        median_duration = sorted(durations)[len(durations)//2] if durations else 0
        longest_duration = max(durations) if durations else 0
        shortest_duration = min(durations) if durations else 0
        
        # DAG频率统计
        dag_counts = defaultdict(int)
        for record in records:
            dag_counts[record.dag_id] += 1
        most_frequent_dags = sorted(dag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 最慢和最快任务
        sorted_records = sorted(records, key=lambda x: x.duration, reverse=True)
        slowest_tasks = [(r.dag_id, r.task_id, r.duration) for r in sorted_records[:10]]
        fastest_tasks = [(r.dag_id, r.task_id, r.duration) for r in sorted(sorted_records, key=lambda x: x.duration)[:10]]
        
        # 执行时间分布
        duration_distribution = self._calculate_duration_distribution(durations)
        
        # 小时执行模式
        hourly_pattern = self._calculate_hourly_pattern(records)
        
        # 资源利用率（简化版）
        resource_utilization = self._calculate_resource_utilization(records)
        
        return PerformanceAnalysis(
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            average_duration=average_duration,
            median_duration=median_duration,
            longest_duration=longest_duration,
            shortest_duration=shortest_duration,
            success_rate=success_rate,
            retry_rate=retry_rate,
            most_frequent_dags=most_frequent_dags,
            slowest_tasks=slowest_tasks,
            fastest_tasks=fastest_tasks,
            duration_distribution=duration_distribution,
            hourly_execution_pattern=hourly_pattern,
            resource_utilization=resource_utilization
        )
    
    def _calculate_duration_distribution(self, durations: List[float]) -> Dict[str, int]:
        """计算执行时间分布"""
        distribution = {
            '<1s': 0, '1-5s': 0, '5-30s': 0, '30s-1m': 0,
            '1-5m': 0, '5-30m': 0, '>30m': 0
        }
        
        for duration in durations:
            if duration < 1:
                distribution['<1s'] += 1
            elif duration < 5:
                distribution['1-5s'] += 1
            elif duration < 30:
                distribution['5-30s'] += 1
            elif duration < 60:
                distribution['30s-1m'] += 1
            elif duration < 300:
                distribution['1-5m'] += 1
            elif duration < 1800:
                distribution['5-30m'] += 1
            else:
                distribution['>30m'] += 1
        
        return distribution
    
    def _calculate_hourly_pattern(self, records: List[TaskExecutionRecord]) -> Dict[int, int]:
        """计算小时执行模式"""
        hourly_counts = defaultdict(int)
        
        for record in records:
            hour = record.execution_date.hour
            hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    def _calculate_resource_utilization(self, records: List[TaskExecutionRecord]) -> Dict[str, float]:
        """计算资源利用率（简化版）"""
        # 这里只是一个简化的示例，在实际应用中应该基于更复杂的指标
        utilization = {
            'cpu_utilization': 0.0,
            'memory_utilization': 0.0,
            'disk_io_utilization': 0.0,
            'network_utilization': 0.0
        }
        
        # 基于任务数量和执行时间的简单估算
        if records:
            avg_duration = sum(r.duration for r in records) / len(records)
            utilization['cpu_utilization'] = min(100.0, avg_duration * 2)
            utilization['memory_utilization'] = min(100.0, len(records) * 0.5)
        
        return utilization


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_text_report(self, analysis: PerformanceAnalysis) -> str:
        """生成文本格式的性能分析报告"""
        report_lines = [
            "=" * 80,
            "Airflow性能分析报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ]
        
        # 基础统计
        report_lines.extend([
            "基础统计:",
            "-" * 40,
            f"总任务数: {analysis.total_tasks:,}",
            f"成功任务: {analysis.successful_tasks:,}",
            f"失败任务: {analysis.failed_tasks:,}",
            f"成功率: {analysis.success_rate*100:.2f}%",
            f"平均执行时间: {analysis.average_duration:.2f} 秒",
            f"中位执行时间: {analysis.median_duration:.2f} 秒",
            f"最长执行时间: {analysis.longest_duration:.2f} 秒",
            f"最短执行时间: {analysis.shortest_duration:.2f} 秒",
            f"重试率: {analysis.retry_rate*100:.2f}%",
            ""
        ])
        
        # 最频繁的DAG
        if analysis.most_frequent_dags:
            report_lines.append("最频繁的DAG:")
            report_lines.append("-" * 40)
            for dag_id, count in analysis.most_frequent_dags[:5]:
                report_lines.append(f"  {dag_id}: {count} 次执行")
            report_lines.append("")
        
        # 最慢的任务
        if analysis.slowest_tasks:
            report_lines.append("执行时间最长的任务:")
            report_lines.append("-" * 40)
            for dag_id, task_id, duration in analysis.slowest_tasks[:5]:
                report_lines.append(f"  {dag_id}.{task_id}: {duration:.2f} 秒")
            report_lines.append("")
        
        # 最快的任务
        if analysis.fastest_tasks:
            report_lines.append("执行时间最短的任务:")
            report_lines.append("-" * 40)
            for dag_id, task_id, duration in analysis.fastest_tasks[:5]:
                report_lines.append(f"  {dag_id}.{task_id}: {duration:.2f} 秒")
            report_lines.append("")
        
        # 执行时间分布
        if analysis.duration_distribution:
            report_lines.append("执行时间分布:")
            report_lines.append("-" * 40)
            for range_name, count in analysis.duration_distribution.items():
                percentage = (count / analysis.total_tasks) * 100 if analysis.total_tasks > 0 else 0
                report_lines.append(f"  {range_name:>8}: {count:>6} ({percentage:>6.2f}%)")
            report_lines.append("")
        
        # 小时执行模式
        if analysis.hourly_execution_pattern:
            report_lines.append("小时执行模式:")
            report_lines.append("-" * 40)
            for hour in range(24):
                count = analysis.hourly_execution_pattern.get(hour, 0)
                bar = "█" * (count // 10) if count > 0 else ""
                report_lines.append(f"  {hour:02d}:00 {count:>6} {bar}")
            report_lines.append("")
        
        # 资源利用率
        if analysis.resource_utilization:
            report_lines.append("资源利用率估计:")
            report_lines.append("-" * 40)
            for resource, utilization in analysis.resource_utilization.items():
                bar = "█" * int(utilization / 5)
                report_lines.append(f"  {resource}: {utilization:>6.2f}% [{bar:<20}]")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        return "\n".join(report_lines)
    
    def generate_visualization(self, analysis: PerformanceAnalysis, output_dir: str = "."):
        """生成可视化图表"""
        try:
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建图形
            fig = plt.figure(figsize=(15, 12))
            
            # 1. 执行时间分布饼图
            ax1 = plt.subplot(2, 3, 1)
            if analysis.duration_distribution:
                labels = list(analysis.duration_distribution.keys())
                sizes = list(analysis.duration_distribution.values())
                # 过滤掉0值
                non_zero_items = [(label, size) for label, size in zip(labels, sizes) if size > 0]
                if non_zero_items:
                    labels, sizes = zip(*non_zero_items)
                    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                    ax1.set_title('执行时间分布')
            
            # 2. 小时执行模式柱状图
            ax2 = plt.subplot(2, 3, 2)
            if analysis.hourly_execution_pattern:
                hours = list(range(24))
                counts = [analysis.hourly_execution_pattern.get(h, 0) for h in hours]
                ax2.bar(hours, counts)
                ax2.set_xlabel('小时')
                ax2.set_ylabel('任务数量')
                ax2.set_title('小时执行模式')
                ax2.set_xticks(range(0, 24, 2))
            
            # 3. 最慢任务条形图
            ax3 = plt.subplot(2, 3, 3)
            if analysis.slowest_tasks:
                task_names = [f"{dag}.{task}" for dag, task, _ in analysis.slowest_tasks[:10]]
                durations = [duration for _, _, duration in analysis.slowest_tasks[:10]]
                y_pos = range(len(task_names))
                ax3.barh(y_pos, durations)
                ax3.set_yticks(y_pos)
                ax3.set_yticklabels([name[:20] + "..." if len(name) > 20 else name for name in task_names])
                ax3.set_xlabel('执行时间 (秒)')
                ax3.set_title('执行时间最长的任务')
            
            # 4. 资源利用率雷达图
            ax4 = plt.subplot(2, 3, 4, projection='polar')
            if analysis.resource_utilization:
                resources = list(analysis.resource_utilization.keys())
                values = list(analysis.resource_utilization.values())
                angles = [n / float(len(resources)) * 2 * 3.141593 for n in range(len(resources))]
                angles += angles[:1]  # 闭合图形
                values += values[:1]  # 闭合图形
                
                ax4.plot(angles, values, 'o-', linewidth=2)
                ax4.fill(angles, values, alpha=0.25)
                ax4.set_xticks(angles[:-1])
                ax4.set_xticklabels(resources)
                ax4.set_ylim(0, 100)
                ax4.set_title('资源利用率')
            
            # 5. 成功率和重试率
            ax5 = plt.subplot(2, 3, 5)
            categories = ['成功率', '重试率']
            values = [analysis.success_rate * 100, analysis.retry_rate * 100]
            bars = ax5.bar(categories, values, color=['green', 'orange'])
            ax5.set_ylabel('百分比 (%)')
            ax5.set_title('任务成功率 vs 重试率')
            
            # 在柱状图上添加数值标签
            for bar, value in zip(bars, values):
                ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{value:.1f}%', ha='center', va='bottom')
            
            # 6. DAG频率分布
            ax6 = plt.subplot(2, 3, 6)
            if analysis.most_frequent_dags:
                dag_names = [dag for dag, _ in analysis.most_frequent_dags[:10]]
                counts = [count for _, count in analysis.most_frequent_dags[:10]]
                y_pos = range(len(dag_names))
                ax6.barh(y_pos, counts)
                ax6.set_yticks(y_pos)
                ax6.set_yticklabels([name[:15] + "..." if len(name) > 15 else name for name in dag_names])
                ax6.set_xlabel('执行次数')
                ax6.set_title('最频繁的DAG')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/performance_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"可视化图表已保存到: {output_dir}/performance_analysis.png")
            
        except Exception as e:
            self.logger.error(f"生成可视化图表时出错: {e}")


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Airflow性能分析工具")
    parser.add_argument(
        "--source",
        choices=["log", "database"],
        default="database",
        help="数据源类型"
    )
    parser.add_argument(
        "--log-file",
        default="airflow.log",
        help="Airflow日志文件路径"
    )
    parser.add_argument(
        "--db-path",
        default="airflow.db",
        help="Airflow数据库路径"
    )
    parser.add_argument(
        "--start-date",
        help="开始日期 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        help="结束日期 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--output",
        default="performance_report.txt",
        help="性能报告输出文件路径"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="生成可视化图表"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="可视化图表输出目录"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 解析日期参数
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            logger.error("无效的开始日期格式，请使用 YYYY-MM-DD")
            return
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
            # 设置为当天的最后一刻
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            logger.error("无效的结束日期格式，请使用 YYYY-MM-DD")
            return
    
    # 获取任务执行记录
    records = []
    
    if args.source == "log":
        logger.info(f"解析日志文件: {args.log_file}")
        parser = LogParser()
        records = parser.parse_log_file(args.log_file)
    else:
        logger.info(f"从数据库获取数据: {args.db_path}")
        analyzer = DatabaseAnalyzer(args.db_path)
        records = analyzer.fetch_task_executions(start_date, end_date)
    
    logger.info(f"共获取到 {len(records)} 条任务执行记录")
    
    if not records:
        logger.warning("没有找到任何任务执行记录")
        return
    
    # 执行性能分析
    logger.info("开始性能分析...")
    performance_analyzer = PerformanceAnalyzer()
    analysis = performance_analyzer.analyze_task_executions(records)
    
    # 生成报告
    logger.info("生成性能分析报告...")
    report_generator = ReportGenerator()
    report_text = report_generator.generate_text_report(analysis)
    
    # 输出报告
    print(report_text)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    logger.info(f"性能报告已保存到: {args.output}")
    
    # 生成可视化图表
    if args.visualize:
        logger.info("生成可视化图表...")
        report_generator.generate_visualization(analysis, args.output_dir)


if __name__ == "__main__":
    main()