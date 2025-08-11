#!/usr/bin/env python3
"""
数据质量检查运行器
支持多场景、多数据库的数据质量检查
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加核心模块到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import DataQualityEngine
from core.config_manager import ConfigManager
from core.database_adapters import DatabaseAdapterFactory


def setup_logging(level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data_quality.log')
        ]
    )


def list_scenarios(config_manager: ConfigManager):
    """列出可用场景"""
    scenarios = config_manager.get_available_scenarios()
    print("可用的数据质量测试场景:")
    print("=" * 50)
    
    for scenario in scenarios:
        scenario_config = config_manager.get_scenario_config(scenario)
        description = scenario_config.get('description', '无描述')
        enabled = scenario_config.get('enabled', True)
        status = "✓" if enabled else "✗"
        print(f"  {status} {scenario:<20} - {description}")
    
    print(f"\n总共 {len(scenarios)} 个场景")


def list_databases():
    """列出支持的数据库类型"""
    databases = DatabaseAdapterFactory.get_supported_types()
    print("支持的数据库类型:")
    print("=" * 30)
    
    for db_type in databases:
        requirements = DatabaseAdapterFactory.get_adapter_requirements(db_type)
        req_str = ", ".join(requirements) if requirements else "无额外依赖"
        print(f"  • {db_type:<15} ({req_str})")
    
    print(f"\n总共支持 {len(databases)} 种数据库")


def test_database_connection(config_manager: ConfigManager, database_name: str = None):
    """测试数据库连接"""
    db_config = config_manager.get_database_config(database_name)
    db_type = db_config.get('type', 'clickhouse')
    
    print(f"测试 {db_type} 数据库连接...")
    print(f"主机: {db_config.get('host', 'unknown')}")
    print(f"端口: {db_config.get('port', 'unknown')}")
    print(f"数据库: {db_config.get('database', 'unknown')}")
    
    try:
        from core.database_adapters import test_database_connection
        success = test_database_connection(db_type, db_config)
        
        if success:
            print("✓ 数据库连接成功")
            return True
        else:
            print("✗ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {e}")
        return False


def run_scenario(engine: DataQualityEngine, scenario_name: str, database_config: dict = None):
    """运行指定场景"""
    print(f"开始执行数据质量场景: {scenario_name}")
    print("=" * 50)
    
    try:
        summary = engine.run_scenario(scenario_name, database_config)
        
        print("\n执行完成！")
        print("=" * 50)
        
        # 打印摘要
        print("执行摘要:")
        print(f"  场景: {summary.get('scenario', 'unknown')}")
        print(f"  环境: {summary.get('environment', 'unknown')}")
        print(f"  状态: {summary.get('status', 'unknown')}")
        print(f"  持续时间: {summary.get('duration', 0):.2f}秒")
        
        stats = summary.get('summary', {})
        print(f"  总规则数: {stats.get('total_rules', 0)}")
        print(f"  通过规则数: {stats.get('passed_rules', 0)}")
        print(f"  失败规则数: {stats.get('failed_rules', 0)}")
        print(f"  错误规则数: {stats.get('error_rules', 0)}")
        print(f"  通过率: {stats.get('pass_rate', 0)}%")
        
        # 确定退出码
        failed_count = stats.get('failed_rules', 0)
        error_count = stats.get('error_rules', 0)
        
        if failed_count > 0 or error_count > 0:
            print(f"\n❌ 发现 {failed_count} 个失败和 {error_count} 个错误")
            return 1
        else:
            print("\n✅ 所有数据质量检查通过")
            return 0
            
    except Exception as e:
        print(f"\n❌ 场景执行失败: {e}")
        return 1


def validate_config(config_manager: ConfigManager):
    """验证配置"""
    print("验证配置文件...")
    print("=" * 30)
    
    errors = config_manager.validate_config()
    
    if not errors:
        print("✓ 配置验证通过")
        
        # 显示配置摘要
        summary = config_manager.get_config_summary()
        print("\n配置摘要:")
        print(f"  环境: {summary.get('environment', 'unknown')}")
        print(f"  配置文件: {summary.get('config_path', 'unknown')}")
        print(f"  数据库类型: {summary.get('database_type', 'unknown')}")
        print(f"  数据库主机: {summary.get('database_host', 'unknown')}")
        print(f"  最大并行数: {summary.get('max_parallel_jobs', 5)}")
        print(f"  报告格式: {', '.join(summary.get('report_formats', []))}")
        print(f"  规则路径: {', '.join(summary.get('rules_paths', []))}")
        print(f"  可用场景: {len(summary.get('available_scenarios', []))}")
        
        return True
    else:
        print("✗ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='数据质量检查工具 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --list-scenarios                    # 列出所有可用场景
  %(prog)s --list-databases                    # 列出支持的数据库类型
  %(prog)s --test-connection                   # 测试默认数据库连接
  %(prog)s --validate-config                   # 验证配置文件
  %(prog)s --scenario clickhouse_smoke_test    # 运行ClickHouse冒烟测试
  %(prog)s --scenario mysql_regression --env prod  # 在生产环境运行MySQL回归测试
        """
    )
    
    # 通用参数
    parser.add_argument('--config', '-c', 
                       help='配置文件路径 (默认: configs/data-quality-config.yml)')
    parser.add_argument('--env', '-e', default='default',
                       help='环境名称 (default, dev, test, prod)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='日志级别')
    
    # 功能参数
    parser.add_argument('--list-scenarios', action='store_true',
                       help='列出所有可用的测试场景')
    parser.add_argument('--list-databases', action='store_true', 
                       help='列出支持的数据库类型')
    parser.add_argument('--test-connection', action='store_true',
                       help='测试数据库连接')
    parser.add_argument('--validate-config', action='store_true',
                       help='验证配置文件')
    
    # 执行参数
    parser.add_argument('--scenario', '-s',
                       help='要执行的场景名称')
    parser.add_argument('--database',
                       help='数据库名称（覆盖默认配置）')
    parser.add_argument('--output-dir', '-o',
                       help='报告输出目录')
    parser.add_argument('--max-workers', type=int,
                       help='最大并行执行数')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager(args.config, args.env)
        
        # 处理列表命令
        if args.list_scenarios:
            list_scenarios(config_manager)
            return 0
        
        if args.list_databases:
            list_databases()
            return 0
        
        if args.validate_config:
            success = validate_config(config_manager)
            return 0 if success else 1
        
        if args.test_connection:
            success = test_database_connection(config_manager, args.database)
            return 0 if success else 1
        
        # 处理场景执行
        if args.scenario:
            # 初始化数据质量引擎
            engine = DataQualityEngine(args.config, args.env)
            
            # 覆盖配置
            if args.output_dir:
                engine.config_manager.set_config_value('report.output_dir', args.output_dir)
            
            if args.max_workers:
                engine.config_manager.set_config_value('execution.max_parallel_jobs', args.max_workers)
            
            # 获取数据库配置
            database_config = None
            if args.database:
                database_config = config_manager.get_database_config(args.database)
            
            # 运行场景
            return run_scenario(engine, args.scenario, database_config)
        
        # 如果没有指定任何操作，显示帮助
        parser.print_help()
        return 0
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
        return 130
    except Exception as e:
        print(f"执行失败: {e}")
        logging.exception("执行异常")
        return 1


if __name__ == "__main__":
    sys.exit(main())

