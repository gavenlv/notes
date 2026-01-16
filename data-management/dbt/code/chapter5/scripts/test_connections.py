#!/usr/bin/env python3
"""
第5章：数据源与连接配置 - 连接测试脚本
用于测试dbt项目中的数据库连接配置
"""

import os
import sys
import yaml
import subprocess
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('connection_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ConnectionTester:
    """数据库连接测试器"""
    
    def __init__(self, profiles_path='profiles.yml', project_path='.'):
        self.profiles_path = profiles_path
        self.project_path = project_path
        self.results = {}
        
    def load_profiles(self):
        """加载profiles.yml配置文件"""
        try:
            with open(self.profiles_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"配置文件 {self.profiles_path} 不存在")
            return None
        except yaml.YAMLError as e:
            logger.error(f"YAML解析错误: {e}")
            return None
    
    def get_targets(self, profiles):
        """获取所有目标环境配置"""
        if not profiles or 'dbt_chapter5' not in profiles:
            logger.error("未找到dbt_chapter5配置")
            return []
            
        dbt_config = profiles['dbt_chapter5']
        return dbt_config.get('outputs', {}).keys()
    
    def test_dbt_connection(self, target):
        """使用dbt debug测试连接"""
        logger.info(f"测试 {target} 环境连接...")
        
        try:
            # 运行dbt debug命令
            result = subprocess.run(
                ['dbt', 'debug', '--target', target],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return {
                'success': success,
                'output': output,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"{target} 连接测试超时")
            return {
                'success': False,
                'output': '连接测试超时',
                'returncode': -1
            }
        except Exception as e:
            logger.error(f"{target} 连接测试异常: {e}")
            return {
                'success': False,
                'output': str(e),
                'returncode': -1
            }
    
    def test_source_connections(self, target):
        """测试数据源连接"""
        logger.info(f"测试 {target} 环境数据源连接...")
        
        try:
            # 运行dbt source freshness检查
            result = subprocess.run(
                ['dbt', 'source', 'freshness', '--target', target],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return {
                'success': success,
                'output': output,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"{target} 数据源测试超时")
            return {
                'success': False,
                'output': '数据源测试超时',
                'returncode': -1
            }
        except Exception as e:
            logger.error(f"{target} 数据源测试异常: {e}")
            return {
                'success': False,
                'output': str(e),
                'returncode': -1
            }
    
    def test_model_compilation(self, target):
        """测试模型编译"""
        logger.info(f"测试 {target} 环境模型编译...")
        
        try:
            # 运行dbt compile命令
            result = subprocess.run(
                ['dbt', 'compile', '--target', target],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return {
                'success': success,
                'output': output,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"{target} 模型编译测试超时")
            return {
                'success': False,
                'output': '模型编译测试超时',
                'returncode': -1
            }
        except Exception as e:
            logger.error(f"{target} 模型编译测试异常: {e}")
            return {
                'success': False,
                'output': str(e),
                'returncode': -1
            }
    
    def run_all_tests(self):
        """运行所有连接测试"""
        logger.info("开始数据库连接测试...")
        
        profiles = self.load_profiles()
        if not profiles:
            return False
        
        targets = self.get_targets(profiles)
        if not targets:
            logger.error("未找到任何目标环境配置")
            return False
        
        logger.info(f"找到目标环境: {', '.join(targets)}")
        
        for target in targets:
            logger.info(f"\n=== 测试 {target} 环境 ===")
            
            self.results[target] = {}
            
            # 测试基础连接
            self.results[target]['connection'] = self.test_dbt_connection(target)
            
            # 如果基础连接成功，测试数据源连接
            if self.results[target]['connection']['success']:
                self.results[target]['source_freshness'] = self.test_source_connections(target)
                self.results[target]['model_compilation'] = self.test_model_compilation(target)
            else:
                logger.warning(f"{target} 基础连接失败，跳过其他测试")
                self.results[target]['source_freshness'] = {'success': False, 'output': '基础连接失败'}
                self.results[target]['model_compilation'] = {'success': False, 'output': '基础连接失败'}
        
        return True
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'summary': self.generate_summary()
        }
        
        # 保存JSON报告
        with open('connection_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成HTML报告
        self.generate_html_report(report)
        
        return report
    
    def generate_summary(self):
        """生成测试摘要"""
        summary = {
            'total_targets': len(self.results),
            'successful_connections': 0,
            'failed_connections': 0,
            'successful_sources': 0,
            'failed_sources': 0,
            'successful_compilations': 0,
            'failed_compilations': 0
        }
        
        for target, results in self.results.items():
            if results['connection']['success']:
                summary['successful_connections'] += 1
            else:
                summary['failed_connections'] += 1
            
            if results['source_freshness']['success']:
                summary['successful_sources'] += 1
            else:
                summary['failed_sources'] += 1
            
            if results['model_compilation']['success']:
                summary['successful_compilations'] += 1
            else:
                summary['failed_compilations'] += 1
        
        return summary
    
    def generate_html_report(self, report):
        """生成HTML格式的报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dbt连接测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .target {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .success {{ background: #d4edda; border-color: #c3e6cb; }}
        .failure {{ background: #f8d7da; border-color: #f5c6cb; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
        .success-test {{ border-color: #28a745; }}
        .failure-test {{ border-color: #dc3545; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>dbt连接测试报告</h1>
    <p>测试时间: {report['timestamp']}</p>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <p>总目标环境: {report['summary']['total_targets']}</p>
        <p>成功连接: {report['summary']['successful_connections']}</p>
        <p>失败连接: {report['summary']['failed_connections']}</p>
        <p>成功数据源: {report['summary']['successful_sources']}</p>
        <p>失败数据源: {report['summary']['failed_sources']}</p>
        <p>成功编译: {report['summary']['successful_compilations']}</p>
        <p>失败编译: {report['summary']['failed_compilations']}</p>
    </div>
    
    <h2>详细结果</h2>
"""
        
        for target, results in report['results'].items():
            target_class = 'success' if results['connection']['success'] else 'failure'
            html_content += f"""
    <div class="target {target_class}">
        <h3>{target} 环境</h3>
        
        <div class="test-result {'success-test' if results['connection']['success'] else 'failure-test'}">
            <h4>基础连接测试</h4>
            <p>状态: {'✅ 成功' if results['connection']['success'] else '❌ 失败'}</p>
            <pre>{results['connection']['output']}</pre>
        </div>
        
        <div class="test-result {'success-test' if results['source_freshness']['success'] else 'failure-test'}">
            <h4>数据源新鲜度测试</h4>
            <p>状态: {'✅ 成功' if results['source_freshness']['success'] else '❌ 失败'}</p>
            <pre>{results['source_freshness']['output']}</pre>
        </div>
        
        <div class="test-result {'success-test' if results['model_compilation']['success'] else 'failure-test'}">
            <h4>模型编译测试</h4>
            <p>状态: {'✅ 成功' if results['model_compilation']['success'] else '❌ 失败'}</p>
            <pre>{results['model_compilation']['output']}</pre>
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open('connection_test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def print_results(self):
        """打印测试结果"""
        logger.info("\n" + "="*50)
        logger.info("连接测试结果")
        logger.info("="*50)
        
        for target, results in self.results.items():
            logger.info(f"\n{target}:")
            logger.info(f"  基础连接: {'✅ 成功' if results['connection']['success'] else '❌ 失败'}")
            logger.info(f"  数据源: {'✅ 成功' if results['source_freshness']['success'] else '❌ 失败'}")
            logger.info(f"  模型编译: {'✅ 成功' if results['model_compilation']['success'] else '❌ 失败'}")

def main():
    """主函数"""
    # 检查dbt是否安装
    try:
        subprocess.run(['dbt', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("dbt未安装或不在PATH中")
        sys.exit(1)
    
    # 创建测试器
    tester = ConnectionTester()
    
    # 运行测试
    if tester.run_all_tests():
        # 生成报告
        report = tester.generate_report()
        
        # 打印结果
        tester.print_results()
        
        # 输出报告文件位置
        logger.info("\n测试报告已生成:")
        logger.info("  - connection_test_report.json (JSON格式)")
        logger.info("  - connection_test_report.html (HTML格式)")
        logger.info("  - connection_test.log (详细日志)")
        
        # 检查总体成功率
        summary = report['summary']
        total_tests = summary['total_targets'] * 3  # 每个环境3个测试
        successful_tests = (summary['successful_connections'] + 
                          summary['successful_sources'] + 
                          summary['successful_compilations'])
        
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        if success_rate >= 0.8:
            logger.info(f"\n✅ 测试通过! 成功率: {success_rate:.1%}")
            sys.exit(0)
        else:
            logger.error(f"\n❌ 测试失败! 成功率: {success_rate:.1%}")
            sys.exit(1)
    else:
        logger.error("测试执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()