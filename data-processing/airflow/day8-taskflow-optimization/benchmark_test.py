#!/usr/bin/env python3
"""
Airflow性能基准测试脚本

该脚本提供了一套完整的性能测试框架，用于评估Airflow任务和DAG的性能表现。
"""

import time
import psutil
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Callable, Any
from contextlib import contextmanager
from dataclasses import dataclass, asdict


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    execution_time: float = 0.0
    cpu_percent: float = 0.0
    memory_usage_mb: float = 0.0
    memory_delta_mb: float = 0.0
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    network_sent_bytes: int = 0
    network_recv_bytes: int = 0
    success: bool = True
    error_message: str = ""


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[PerformanceMetrics] = []
        
    @contextmanager
    def monitor_performance(self):
        """性能监控上下文管理器"""
        # 获取初始系统状态
        process = psutil.Process()
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info()
        initial_io = process.io_counters()
        initial_net = psutil.net_io_counters()
        start_time = time.time()
        
        metrics = PerformanceMetrics()
        
        try:
            yield metrics
            metrics.success = True
        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            self.logger.error(f"测试执行失败: {e}")
        finally:
            # 计算执行时间
            end_time = time.time()
            metrics.execution_time = end_time - start_time
            
            # 获取最终系统状态
            final_cpu = process.cpu_percent()
            final_memory = process.memory_info()
            final_io = process.io_counters()
            final_net = psutil.net_io_counters()
            
            # 计算资源使用情况
            metrics.cpu_percent = final_cpu
            metrics.memory_usage_mb = final_memory.rss / 1024 / 1024
            metrics.memory_delta_mb = (final_memory.rss - initial_memory.rss) / 1024 / 1024
            metrics.io_read_bytes = final_io.read_bytes - initial_io.read_bytes
            metrics.io_write_bytes = final_io.write_bytes - initial_io.write_bytes
            metrics.network_sent_bytes = final_net.bytes_sent - initial_net.bytes_sent
            metrics.network_recv_bytes = final_net.bytes_recv - initial_net.bytes_recv
            
            # 记录指标
            self.metrics_history.append(metrics)
    
    def run_test_suite(self, test_functions: Dict[str, Callable]) -> Dict[str, PerformanceMetrics]:
        """运行测试套件"""
        results = {}
        
        for test_name, test_func in test_functions.items():
            self.logger.info(f"运行测试: {test_name}")
            
            with self.monitor_performance() as metrics:
                test_func()
                
            results[test_name] = metrics
            self.logger.info(f"测试完成: {test_name}, 执行时间: {metrics.execution_time:.2f}s")
        
        return results
    
    def generate_report(self, results: Dict[str, PerformanceMetrics]) -> str:
        """生成性能测试报告"""
        report_lines = [
            "=" * 80,
            "Airflow性能基准测试报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ]
        
        # 汇总统计
        total_tests = len(results)
        successful_tests = sum(1 for m in results.values() if m.success)
        failed_tests = total_tests - successful_tests
        
        report_lines.extend([
            "测试摘要:",
            f"  总测试数: {total_tests}",
            f"  成功测试: {successful_tests}",
            f"  失败测试: {failed_tests}",
            ""
        ])
        
        # 详细结果
        report_lines.append("详细结果:")
        report_lines.append("-" * 80)
        
        for test_name, metrics in results.items():
            status = "✓ PASS" if metrics.success else "✗ FAIL"
            report_lines.append(f"{test_name}: {status}")
            
            if metrics.success:
                report_lines.extend([
                    f"  执行时间: {metrics.execution_time:.4f} 秒",
                    f"  CPU使用率: {metrics.cpu_percent:.2f}%",
                    f"  内存使用: {metrics.memory_usage_mb:.2f} MB",
                    f"  内存增量: {metrics.memory_delta_mb:.2f} MB",
                    f"  IO读取: {metrics.io_read_bytes:,} 字节",
                    f"  IO写入: {metrics.io_write_bytes:,} 字节",
                    f"  网络发送: {metrics.network_sent_bytes:,} 字节",
                    f"  网络接收: {metrics.network_recv_bytes:,} 字节",
                ])
            else:
                report_lines.append(f"  错误信息: {metrics.error_message}")
            
            report_lines.append("")
        
        # 性能分析
        if successful_tests > 0:
            execution_times = [m.execution_time for m in results.values() if m.success]
            avg_execution_time = sum(execution_times) / len(execution_times)
            max_execution_time = max(execution_times)
            min_execution_time = min(execution_times)
            
            report_lines.extend([
                "性能分析:",
                f"  平均执行时间: {avg_execution_time:.4f} 秒",
                f"  最长执行时间: {max_execution_time:.4f} 秒",
                f"  最短执行时间: {min_execution_time:.4f} 秒",
                ""
            ])
        
        report_lines.append("=" * 80)
        return "\n".join(report_lines)


# 示例测试函数
def sample_cpu_intensive_task():
    """CPU密集型任务示例"""
    total = 0
    for i in range(1000000):
        total += i * i
    return total


def sample_io_intensive_task():
    """IO密集型任务示例"""
    # 模拟文件读写操作
    data = "x" * 1024 * 1024  # 1MB数据
    for _ in range(10):
        # 模拟写入操作
        with open("temp_test_file.txt", "w") as f:
            f.write(data)
        # 模拟读取操作
        with open("temp_test_file.txt", "r") as f:
            _ = f.read()
    
    # 清理临时文件
    import os
    if os.path.exists("temp_test_file.txt"):
        os.remove("temp_test_file.txt")


def sample_memory_intensive_task():
    """内存密集型任务示例"""
    # 创建大量数据对象
    data_list = []
    for i in range(100000):
        data_list.append({"id": i, "value": f"data_item_{i}"})
    
    # 处理数据
    processed_count = 0
    for item in data_list:
        if "item" in item["value"]:
            processed_count += 1
    
    return processed_count


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Airflow性能基准测试")
    parser.add_argument(
        "--test-suite",
        choices=["all", "cpu", "io", "memory"],
        default="all",
        help="选择要运行的测试套件"
    )
    parser.add_argument(
        "--output",
        default="benchmark_report.txt",
        help="测试报告输出文件路径"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 定义测试函数映射
    test_suites = {
        "cpu": {
            "CPU密集型任务测试": sample_cpu_intensive_task
        },
        "io": {
            "IO密集型任务测试": sample_io_intensive_task
        },
        "memory": {
            "内存密集型任务测试": sample_memory_intensive_task
        }
    }
    
    # 根据参数选择测试套件
    if args.test_suite == "all":
        selected_tests = {}
        for suite in test_suites.values():
            selected_tests.update(suite)
    else:
        selected_tests = test_suites[args.test_suite]
    
    # 运行基准测试
    benchmark = PerformanceBenchmark()
    results = benchmark.run_test_suite(selected_tests)
    
    # 生成报告
    report = benchmark.generate_report(results)
    print(report)
    
    # 保存报告到文件
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n测试报告已保存到: {args.output}")


if __name__ == "__main__":
    main()