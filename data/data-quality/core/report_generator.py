#!/usr/bin/env python3
"""
报告生成器
生成多格式的数据质量检查报告，特别是自动化测试风格的HTML报告
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """数据质量报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化报告生成器
        
        Args:
            config: 全局配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.report_config = config.get('report', {})
        
    def generate_reports(self, results: List[Dict[str, Any]], summary: Dict[str, Any]) -> List[str]:
        """
        生成所有格式的报告
        
        Args:
            results: 检查结果列表
            summary: 执行摘要
            
        Returns:
            List[str]: 生成的报告文件路径列表
        """
        report_files = []
        output_dir = self.report_config.get('output_dir', 'reports')
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scenario_name = summary.get('scenario', 'unknown')
        
        # 根据配置生成不同格式的报告
        formats = self.report_config.get('formats', ['json', 'html'])
        
        if 'json' in formats:
            json_file = self._generate_json_report(results, summary, output_dir, timestamp, scenario_name)
            if json_file:
                report_files.append(json_file)
        
        if 'html' in formats:
            html_file = self._generate_html_report(results, summary, output_dir, timestamp, scenario_name)
            if html_file:
                report_files.append(html_file)
        
        if 'txt' in formats:
            txt_file = self._generate_text_report(results, summary, output_dir, timestamp, scenario_name)
            if txt_file:
                report_files.append(txt_file)
        
        if 'csv' in formats:
            csv_file = self._generate_csv_report(results, summary, output_dir, timestamp, scenario_name)
            if csv_file:
                report_files.append(csv_file)
        
        if 'xml' in formats:
            xml_file = self._generate_xml_report(results, summary, output_dir, timestamp, scenario_name)
            if xml_file:
                report_files.append(xml_file)
        
        self.logger.info(f"生成了 {len(report_files)} 个报告文件")
        return report_files
    
    def _generate_json_report(self, results: List[Dict], summary: Dict, output_dir: str, 
                            timestamp: str, scenario_name: str) -> Optional[str]:
        """生成JSON格式报告"""
        try:
            filename = f"data_quality_report_{scenario_name}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            report_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'scenario': scenario_name,
                    'environment': summary.get('environment', 'unknown'),
                    'version': '2.0.0'
                },
                'summary': summary,
                'results': results,
                'statistics': self._calculate_statistics(results),
                'recommendations': self._generate_recommendations(results)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"JSON报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生成JSON报告失败: {e}")
            return None
    
    def _generate_html_report(self, results: List[Dict], summary: Dict, output_dir: str, 
                            timestamp: str, scenario_name: str) -> Optional[str]:
        """生成自动化测试风格的HTML报告"""
        try:
            filename = f"data_quality_report_{scenario_name}_{timestamp}.html"
            filepath = os.path.join(output_dir, filename)
            
            # 计算统计信息
            stats = self._calculate_statistics(results)
            
            html_content = self._create_html_template(summary, results, stats, scenario_name, timestamp)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生成HTML报告失败: {e}")
            return None
    
    def _create_html_template(self, summary: Dict, results: List[Dict], stats: Dict, 
                            scenario_name: str, timestamp: str) -> str:
        """创建HTML模板"""
        
        # 获取摘要信息
        total_rules = summary.get('summary', {}).get('total_rules', 0)
        passed_rules = summary.get('summary', {}).get('passed_rules', 0)
        failed_rules = summary.get('summary', {}).get('failed_rules', 0)
        error_rules = summary.get('summary', {}).get('error_rules', 0)
        pass_rate = summary.get('summary', {}).get('pass_rate', 0)
        duration = summary.get('duration', 0)
        environment = summary.get('environment', 'unknown')
        
        # 确定整体状态
        overall_status = "success" if failed_rules == 0 and error_rules == 0 else "failure"
        status_icon = "✅" if overall_status == "success" else "❌"
        status_text = "PASSED" if overall_status == "success" else "FAILED"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据质量检查报告 - {scenario_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .status-success {{
            background-color: #28a745;
            color: white;
        }}
        
        .status-failure {{
            background-color: #dc3545;
            color: white;
        }}
        
        .status-warning {{
            background-color: #ffc107;
            color: #212529;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .summary-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .value.success {{ color: #28a745; }}
        .value.danger {{ color: #dc3545; }}
        .value.warning {{ color: #ffc107; }}
        .value.info {{ color: #17a2b8; }}
        
        .progress-bar {{
            width: 100%;
            height: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background-color: #28a745;
            transition: width 0.3s ease;
        }}
        
        .section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .section-header {{
            background-color: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .section-header h2 {{
            font-size: 1.5em;
            color: #495057;
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        .test-results {{
            margin-bottom: 20px;
        }}
        
        .test-item {{
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .test-header {{
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.2s;
        }}
        
        .test-header:hover {{
            background-color: #f8f9fa;
        }}
        
        .test-header.passed {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
        }}
        
        .test-header.failed {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
        }}
        
        .test-header.error {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        
        .test-name {{
            font-weight: 600;
            font-size: 1.1em;
        }}
        
        .test-status {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .test-details {{
            padding: 20px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            display: none;
        }}
        
        .test-details.show {{
            display: block;
        }}
        
        .detail-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .detail-item {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #007bff;
        }}
        
        .detail-item .label {{
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .detail-item .value {{
            font-size: 1.2em;
            margin-top: 5px;
        }}
        
        .sql-query {{
            background-color: #f1f3f4;
            border: 1px solid #dadce0;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        
        .recommendations {{
            background-color: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .recommendations h3 {{
            color: #0056b3;
            margin-bottom: 15px;
        }}
        
        .recommendations ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .recommendations li {{
            padding: 8px 0;
            border-bottom: 1px solid #b3d9ff;
        }}
        
        .recommendations li:last-child {{
            border-bottom: none;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .toggle-icon {{
            transition: transform 0.2s;
        }}
        
        .toggle-icon.expanded {{
            transform: rotate(180deg);
        }}
        
        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            
            .detail-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>
                {status_icon} 数据质量检查报告
                <span class="status-badge status-{overall_status}">{status_text}</span>
            </h1>
            <div class="subtitle">
                场景: {scenario_name} | 环境: {environment} | 生成时间: {timestamp}
            </div>
        </div>
        
        <!-- 摘要统计 -->
        <div class="summary-grid">
            <div class="summary-card">
                <h3>总规则数</h3>
                <div class="value info">{total_rules}</div>
                <div class="label">Total Rules</div>
            </div>
            <div class="summary-card">
                <h3>通过数</h3>
                <div class="value success">{passed_rules}</div>
                <div class="label">Passed</div>
            </div>
            <div class="summary-card">
                <h3>失败数</h3>
                <div class="value danger">{failed_rules}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card">
                <h3>错误数</h3>
                <div class="value warning">{error_rules}</div>
                <div class="label">Errors</div>
            </div>
            <div class="summary-card">
                <h3>通过率</h3>
                <div class="value success">{pass_rate}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pass_rate}%"></div>
                </div>
                <div class="label">Pass Rate</div>
            </div>
            <div class="summary-card">
                <h3>执行时长</h3>
                <div class="value info">{duration:.2f}s</div>
                <div class="label">Duration</div>
            </div>
        </div>
        
        <!-- 按类别统计 -->
        {self._generate_category_stats_html(summary)}
        
        <!-- 测试结果详情 -->
        <div class="section">
            <div class="section-header">
                <h2>测试结果详情</h2>
            </div>
            <div class="section-content">
                <div class="test-results">
                    {self._generate_test_results_html(results)}
                </div>
            </div>
        </div>
        
        <!-- 建议 -->
        {self._generate_recommendations_html(results)}
        
        <!-- 页脚 -->
        <div class="footer">
            <p>数据质量框架 v2.0.0 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // 切换测试详情显示
        function toggleTestDetails(element) {{
            const details = element.nextElementSibling;
            const icon = element.querySelector('.toggle-icon');
            
            if (details.classList.contains('show')) {{
                details.classList.remove('show');
                icon.classList.remove('expanded');
            }} else {{
                details.classList.add('show');
                icon.classList.add('expanded');
            }}
        }}
        
        // 自动展开失败的测试
        document.addEventListener('DOMContentLoaded', function() {{
            const failedTests = document.querySelectorAll('.test-header.failed, .test-header.error');
            failedTests.forEach(function(test) {{
                const details = test.nextElementSibling;
                const icon = test.querySelector('.toggle-icon');
                details.classList.add('show');
                icon.classList.add('expanded');
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _generate_category_stats_html(self, summary: Dict) -> str:
        """生成类别统计HTML"""
        category_stats = summary.get('category_stats', {})
        if not category_stats:
            return ""
        
        html = """
        <div class="section">
            <div class="section-header">
                <h2>按类别统计</h2>
            </div>
            <div class="section-content">
                <div class="detail-grid">
        """
        
        for category, stats in category_stats.items():
            total = stats.get('total', 0)
            passed = stats.get('passed', 0)
            failed = stats.get('failed', 0)
            error = stats.get('error', 0)
            pass_rate = round(passed / total * 100, 1) if total > 0 else 0
            
            html += f"""
                    <div class="detail-item">
                        <div class="label">{category.upper()}</div>
                        <div class="value">总数: {total}</div>
                        <div style="font-size: 0.9em; margin-top: 5px;">
                            <span style="color: #28a745;">✓ {passed}</span> |
                            <span style="color: #dc3545;">✗ {failed}</span> |
                            <span style="color: #ffc107;">⚠ {error}</span>
                        </div>
                        <div class="progress-bar" style="margin-top: 8px;">
                            <div class="progress-fill" style="width: {pass_rate}%"></div>
                        </div>
                        <div style="font-size: 0.8em; color: #666; margin-top: 3px;">{pass_rate}% 通过</div>
                    </div>
            """
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_test_results_html(self, results: List[Dict]) -> str:
        """生成测试结果HTML"""
        html = ""
        
        for i, result in enumerate(results, 1):
            rule_name = result.get('rule_name', f'规则 #{i}')
            rule_type = result.get('rule_type', 'unknown')
            category = result.get('category', 'unknown')
            priority = result.get('priority', 'medium')
            status = result.get('status', 'ERROR')
            description = result.get('description', '')
            duration = result.get('duration', 0)
            
            # 确定状态样式
            if status == 'COMPLETED':
                check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                if check_result == 'PASS':
                    status_class = 'passed'
                    status_icon = '✅'
                    status_text = 'PASSED'
                else:
                    status_class = 'failed'
                    status_icon = '❌'
                    status_text = 'FAILED'
            else:
                status_class = 'error'
                status_icon = '⚠️'
                status_text = 'ERROR'
            
            html += f"""
            <div class="test-item">
                <div class="test-header {status_class}" onclick="toggleTestDetails(this)">
                    <div>
                        <div class="test-name">{rule_name}</div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 3px;">
                            {rule_type} | {category} | {priority} 优先级
                        </div>
                    </div>
                    <div class="test-status">
                        <span>{status_icon} {status_text}</span>
                        <span class="toggle-icon">⌄</span>
                    </div>
                </div>
                <div class="test-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="label">规则类型</div>
                            <div class="value">{rule_type}</div>
                        </div>
                        <div class="detail-item">
                            <div class="label">类别</div>
                            <div class="value">{category}</div>
                        </div>
                        <div class="detail-item">
                            <div class="label">优先级</div>
                            <div class="value">{priority}</div>
                        </div>
                        <div class="detail-item">
                            <div class="label">执行时长</div>
                            <div class="value">{duration:.3f}s</div>
                        </div>
            """
            
            # 添加检查结果详情
            if status == 'COMPLETED':
                result_data = result.get('result', {})
                for key, value in result_data.items():
                    if key != 'check_result' and value != 0:
                        html += f"""
                        <div class="detail-item">
                            <div class="label">{key}</div>
                            <div class="value">{value}</div>
                        </div>
                        """
            elif status == 'ERROR':
                error_msg = result.get('error', '未知错误')
                html += f"""
                        <div class="detail-item">
                            <div class="label">错误信息</div>
                            <div class="value" style="color: #dc3545;">{error_msg}</div>
                        </div>
                """
            
            html += """
                    </div>
            """
            
            # 添加描述
            if description:
                html += f"""
                    <div style="margin-top: 15px;">
                        <strong>描述:</strong> {description}
                    </div>
                """
            
            # 添加SQL查询
            sql_query = result.get('sql_query', '')
            if sql_query:
                html += f"""
                    <div class="sql-query">
{sql_query}
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        return html
    
    def _generate_recommendations_html(self, results: List[Dict]) -> str:
        """生成建议HTML"""
        recommendations = self._generate_recommendations(results)
        if not recommendations:
            return ""
        
        html = """
        <div class="section">
            <div class="section-header">
                <h2>改进建议</h2>
            </div>
            <div class="section-content">
                <div class="recommendations">
                    <h3>📋 建议采取的行动</h3>
                    <ul>
        """
        
        for rec in recommendations:
            html += f"<li>• {rec}</li>"
        
        html += """
                    </ul>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_text_report(self, results: List[Dict], summary: Dict, output_dir: str, 
                            timestamp: str, scenario_name: str) -> Optional[str]:
        """生成文本格式报告"""
        try:
            filename = f"data_quality_report_{scenario_name}_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"数据质量检查报告 - {scenario_name}\n")
                f.write("=" * 50 + "\n\n")
                
                # 摘要
                f.write("执行摘要:\n")
                f.write(f"  场景: {scenario_name}\n")
                f.write(f"  环境: {summary.get('environment', 'unknown')}\n")
                f.write(f"  时间: {timestamp}\n")
                f.write(f"  状态: {summary.get('status', 'UNKNOWN')}\n")
                f.write(f"  持续时间: {summary.get('duration', 0):.2f}秒\n\n")
                
                # 统计信息
                stats = summary.get('summary', {})
                f.write("统计信息:\n")
                f.write(f"  总规则数: {stats.get('total_rules', 0)}\n")
                f.write(f"  通过规则数: {stats.get('passed_rules', 0)}\n")
                f.write(f"  失败规则数: {stats.get('failed_rules', 0)}\n")
                f.write(f"  错误规则数: {stats.get('error_rules', 0)}\n")
                f.write(f"  通过率: {stats.get('pass_rate', 0)}%\n\n")
                
                # 详细结果
                f.write("详细结果:\n")
                f.write("-" * 50 + "\n")
                
                for i, result in enumerate(results, 1):
                    rule_name = result.get('rule_name', f'规则 #{i}')
                    status = result.get('status', 'ERROR')
                    
                    f.write(f"\n{i}. {rule_name}\n")
                    f.write(f"   状态: {status}\n")
                    f.write(f"   类型: {result.get('rule_type', 'unknown')}\n")
                    f.write(f"   类别: {result.get('category', 'unknown')}\n")
                    f.write(f"   优先级: {result.get('priority', 'medium')}\n")
                    f.write(f"   时长: {result.get('duration', 0):.3f}秒\n")
                    
                    if status == 'COMPLETED':
                        check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                        f.write(f"   结果: {check_result}\n")
                        
                        if check_result == 'FAIL':
                            result_data = result.get('result', {})
                            f.write("   失败详情:\n")
                            for key, value in result_data.items():
                                if key != 'check_result' and value != 0:
                                    f.write(f"     {key}: {value}\n")
                    else:
                        f.write(f"   错误: {result.get('error', '未知错误')}\n")
            
            self.logger.info(f"文本报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生成文本报告失败: {e}")
            return None
    
    def _generate_csv_report(self, results: List[Dict], summary: Dict, output_dir: str, 
                           timestamp: str, scenario_name: str) -> Optional[str]:
        """生成CSV格式报告"""
        try:
            import csv
            
            filename = f"data_quality_report_{scenario_name}_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入头部
                headers = [
                    '规则名称', '规则类型', '类别', '优先级', '状态', '检查结果', 
                    '执行时长(秒)', '描述', '错误信息'
                ]
                writer.writerow(headers)
                
                # 写入数据
                for result in results:
                    row = [
                        result.get('rule_name', ''),
                        result.get('rule_type', ''),
                        result.get('category', ''),
                        result.get('priority', ''),
                        result.get('status', ''),
                        result.get('result', {}).get('check_result', '') if result.get('status') == 'COMPLETED' else '',
                        result.get('duration', 0),
                        result.get('description', ''),
                        result.get('error', '') if result.get('status') == 'ERROR' else ''
                    ]
                    writer.writerow(row)
            
            self.logger.info(f"CSV报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生成CSV报告失败: {e}")
            return None
    
    def _generate_xml_report(self, results: List[Dict], summary: Dict, output_dir: str, 
                           timestamp: str, scenario_name: str) -> Optional[str]:
        """生成XML格式报告（JUnit风格）"""
        try:
            filename = f"data_quality_report_{scenario_name}_{timestamp}.xml"
            filepath = os.path.join(output_dir, filename)
            
            total_rules = summary.get('summary', {}).get('total_rules', 0)
            failed_rules = summary.get('summary', {}).get('failed_rules', 0)
            error_rules = summary.get('summary', {}).get('error_rules', 0)
            duration = summary.get('duration', 0)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<testsuite name="{scenario_name}" tests="{total_rules}" failures="{failed_rules}" errors="{error_rules}" time="{duration:.3f}">\n')
                
                for result in results:
                    rule_name = result.get('rule_name', 'unknown')
                    duration = result.get('duration', 0)
                    status = result.get('status', 'ERROR')
                    
                    f.write(f'  <testcase name="{rule_name}" time="{duration:.3f}">\n')
                    
                    if status == 'COMPLETED':
                        check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                        if check_result == 'FAIL':
                            f.write(f'    <failure message="Data quality check failed">\n')
                            f.write(f'      {result.get("description", "")}\n')
                            f.write(f'    </failure>\n')
                    elif status == 'ERROR':
                        f.write(f'    <error message="{result.get("error", "Unknown error")}">\n')
                        f.write(f'      {result.get("description", "")}\n')
                        f.write(f'    </error>\n')
                    
                    f.write('  </testcase>\n')
                
                f.write('</testsuite>\n')
            
            self.logger.info(f"XML报告已生成: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"生成XML报告失败: {e}")
            return None
    
    def _calculate_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """计算统计信息"""
        stats = {
            'total_rules': len(results),
            'passed_rules': 0,
            'failed_rules': 0,
            'error_rules': 0,
            'avg_duration': 0,
            'by_type': {},
            'by_category': {},
            'by_priority': {}
        }
        
        total_duration = 0
        
        for result in results:
            # 状态统计
            status = result.get('status', 'ERROR')
            if status == 'COMPLETED':
                check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                if check_result == 'PASS':
                    stats['passed_rules'] += 1
                else:
                    stats['failed_rules'] += 1
            else:
                stats['error_rules'] += 1
            
            # 时长统计
            duration = result.get('duration', 0)
            total_duration += duration
            
            # 按类型统计
            rule_type = result.get('rule_type', 'unknown')
            stats['by_type'][rule_type] = stats['by_type'].get(rule_type, 0) + 1
            
            # 按类别统计
            category = result.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # 按优先级统计
            priority = result.get('priority', 'medium')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        stats['avg_duration'] = total_duration / len(results) if results else 0
        stats['pass_rate'] = round(stats['passed_rules'] / stats['total_rules'] * 100, 2) if stats['total_rules'] > 0 else 0
        
        return stats
    
    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        failed_count = len([r for r in results if r.get('status') == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
        error_count = len([r for r in results if r.get('status') == 'ERROR'])
        
        if failed_count > 0:
            recommendations.append(f"有 {failed_count} 个数据质量检查失败，建议检查数据源和数据处理流程")
        
        if error_count > 0:
            recommendations.append(f"有 {error_count} 个规则执行错误，建议检查规则配置和数据库连接")
        
        # 分析失败类型
        completeness_failures = len([r for r in results if r.get('rule_type') == 'completeness' and r.get('result', {}).get('check_result') == 'FAIL'])
        accuracy_failures = len([r for r in results if r.get('rule_type') == 'accuracy' and r.get('result', {}).get('check_result') == 'FAIL'])
        consistency_failures = len([r for r in results if r.get('rule_type') == 'consistency' and r.get('result', {}).get('check_result') == 'FAIL'])
        
        if completeness_failures > 0:
            recommendations.append("发现数据完整性问题，建议检查数据采集和ETL流程")
        
        if accuracy_failures > 0:
            recommendations.append("发现数据准确性问题，建议验证数据验证规则和业务逻辑")
        
        if consistency_failures > 0:
            recommendations.append("发现数据一致性问题，建议检查数据关联关系和引用完整性")
        
        # 高优先级失败
        high_priority_failures = len([r for r in results if r.get('priority') == 'high' and r.get('result', {}).get('check_result') == 'FAIL'])
        if high_priority_failures > 0:
            recommendations.append(f"有 {high_priority_failures} 个高优先级规则失败，建议优先处理")
        
        if not recommendations:
            recommendations.append("所有数据质量检查通过，数据质量良好")
        
        return recommendations

