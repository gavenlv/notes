#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark示例运行器
用于运行和测试Spark示例代码，并提供基本的性能分析。

使用方式:
python run_examples.py [示例名称]

示例名称:
- wordcount: 运行WordCount示例
- pi: 运行Pi估计器示例
- sales: 运行销售分析示例
- iris: 运行鸢尾花分类示例
- all: 运行所有示例
"""

import os
import sys
import subprocess
import time
import importlib.util
from pathlib import Path

def run_command(cmd, description):
    """运行命令并测量执行时间"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print("输出:")
    print(result.stdout)
    
    if result.stderr:
        print("错误:")
        print(result.stderr)
    
    print(f"\n执行时间: {end_time - start_time:.2f}秒")
    print(f"返回码: {result.returncode}")
    
    return result.returncode == 0, end_time - start_time

def run_python_script(script_path, description, spark_args=None):
    """运行Python脚本"""
    cmd = f"python {script_path}"
    if spark_args:
        cmd = f"spark-submit {spark_args} {script_path}"
    
    return run_command(cmd, description)

def run_example(example_name):
    """运行指定的示例"""
    base_dir = Path(__file__).parent
    
    if example_name == "wordcount":
        script_path = base_dir / "code/core-examples/wordcount.py"
        return run_python_script(script_path, "WordCount示例")
    
    elif example_name == "pi":
        script_path = base_dir / "code/core-examples/pi_estimator.py"
        spark_args = "--master local[*]"
        return run_python_script(script_path, "Pi估计器示例", spark_args)
    
    elif example_name == "sales":
        script_path = base_dir / "code/sql-examples/sales_analysis.py"
        return run_python_script(script_path, "销售分析示例")
    
    elif example_name == "iris":
        script_path = base_dir / "code/mlib-examples/iris_classification.py"
        return run_python_script(script_path, "鸢尾花分类示例")
    
    elif example_name == "config_optimizer":
        script_path = base_dir / "code/performance-tuning/spark_config_optimizer.py"
        return run_python_script(script_path, "Spark配置优化器示例")
    
    else:
        print(f"未知的示例名称: {example_name}")
        return False, 0

def run_all_examples():
    """运行所有示例"""
    examples = ["wordcount", "pi", "sales", "iris"]
    results = []
    
    print("运行所有Spark示例...")
    
    for example in examples:
        success, duration = run_example(example)
        results.append((example, success, duration))
        
        if not success:
            print(f"示例 {example} 执行失败，跳过后续示例")
            break
    
    # 打印总结
    print(f"\n{'='*60}")
    print("执行总结")
    print(f"{'='*60}")
    
    total_time = 0
    for example, success, duration in results:
        status = "成功" if success else "失败"
        print(f"{example:<20} {status:<10} {duration:.2f}秒")
        total_time += duration
    
    print(f"\n总执行时间: {total_time:.2f}秒")
    print(f"成功执行的示例: {sum(1 for _, success, _ in results if success)}/{len(results)}")
    
    return all(success for _, success, _ in results)

def check_environment():
    """检查运行环境"""
    print("检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("错误: 需要Python 3.6或更高版本")
        return False
    
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查PySpark
    try:
        import pyspark
        print(f"PySpark版本: {pyspark.__version__}")
    except ImportError:
        print("警告: PySpark未安装，部分示例可能无法运行")
        print("安装命令: pip install pyspark")
    
    # 检查示例文件
    base_dir = Path(__file__).parent
    core_examples_dir = base_dir / "code/core-examples"
    sql_examples_dir = base_dir / "code/sql-examples"
    mlib_examples_dir = base_dir / "code/mlib-examples"
    performance_dir = base_dir / "code/performance-tuning"
    
    required_files = [
        core_examples_dir / "wordcount.py",
        core_examples_dir / "pi_estimator.py",
        sql_examples_dir / "sales_analysis.py",
        mlib_examples_dir / "iris_classification.py",
        performance_dir / "spark_config_optimizer.py"
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print("警告: 以下示例文件缺失:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    
    print("环境检查完成")
    return True

def print_usage():
    """打印使用说明"""
    print("Spark示例运行器")
    print("=" * 50)
    print("用法:")
    print("  python run_examples.py [示例名称]")
    print("")
    print("可用的示例:")
    print("  wordcount      - 运行WordCount示例")
    print("  pi             - 运行Pi估计器示例")
    print("  sales          - 运行销售分析示例")
    print("  iris           - 运行鸢尾花分类示例")
    print("  config_optimizer - 运行Spark配置优化器示例")
    print("  all            - 运行所有示例")
    print("")
    print("示例:")
    print("  python run_examples.py wordcount")
    print("  python run_examples.py all")

def main():
    """主函数"""
    # 检查环境
    if not check_environment():
        print("环境检查失败，请解决上述问题后重试")
        return
    
    # 处理命令行参数
    if len(sys.argv) < 2:
        print_usage()
        return
    
    example_name = sys.argv[1].lower()
    
    if example_name == "help" or example_name == "-h" or example_name == "--help":
        print_usage()
    elif example_name == "all":
        run_all_examples()
    else:
        success, _ = run_example(example_name)
        
        if success:
            print(f"\n示例 {example_name} 执行成功!")
        else:
            print(f"\n示例 {example_name} 执行失败!")

if __name__ == "__main__":
    main()