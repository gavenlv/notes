#!/usr/bin/env python3
"""
JMX文件验证工具
用于验证JMeter测试计划的配置正确性
"""

import xml.etree.ElementTree as ET
import re
import json
from pathlib import Path

class JMXValidator:
    def __init__(self, jmx_file_path):
        self.jmx_file = jmx_file_path
        self.tree = None
        self.check_results = []
        
    def parse_jmx(self):
        """解析JMX文件"""
        try:
            self.tree = ET.parse(self.jmx_file)
            return True
        except Exception as e:
            print(f"解析JMX文件失败: {e}")
            return False
    
    def check_threadgroup_config(self):
        """检查线程组配置"""
        threadgroups = self.tree.findall(".//ThreadGroup")
        
        for tg in threadgroups:
            num_threads = tg.find(".//stringProp[@name='ThreadGroup.num_threads']")
            ramp_time = tg.find(".//stringProp[@name='ThreadGroup.ramp_time']")
            
            if num_threads is not None and ramp_time is not None:
                threads = int(num_threads.text) if num_threads.text.isdigit() else 0
                ramp = int(ramp_time.text) if ramp_time.text.isdigit() else 0
                
                # 检查ramp-up时间是否合理
                if threads > 0 and ramp == 0:
                    self.check_results.append({
                        'category': '线程组配置',
                        'issue': 'ramp-up时间过短',
                        'severity': '警告',
                        'suggestion': '增加ramp-up时间，避免瞬时高并发压力'
                    })
    
    def check_assertions(self):
        """检查断言配置"""
        assertions = self.tree.findall(".//ResponseAssertion")
        
        for assertion in assertions:
            test_strings = assertion.find(".//collectionProp[@name='Asserion.test_strings']")
            if test_strings is None or len(test_strings) == 0:
                self.check_results.append({
                    'category': '断言配置',
                    'issue': '断言缺少测试字符串',
                    'severity': '错误',
                    'suggestion': '为断言配置有效的测试字符串'
                })
    
    def check_listeners(self):
        """检查监听器配置"""
        # 检查是否有过多GUI监听器
        gui_listeners = []
        for guiclass in ['ViewResultsFullVisualizer', 'ViewResultsTree', 'SummaryReport']:
            listeners = self.tree.findall(f".//*[@guiclass='{guiclass}']")
            if listeners:
                gui_listeners.extend(listeners)
        
        if len(gui_listeners) > 2:
            self.check_results.append({
                'category': '监听器配置',
                'issue': 'GUI监听器过多',
                'severity': '建议',
                'suggestion': '减少GUI监听器数量，使用非GUI监听器提高性能'
            })
    
    def check_timers(self):
        """检查定时器配置"""
        timers = self.tree.findall(".//*[contains(@testclass, 'Timer')]")
        if len(timers) == 0:
            self.check_results.append({
                'category': '性能优化',
                'issue': '缺少定时器',
                'severity': '建议',
                'suggestion': '添加思考时间定时器，模拟真实用户行为'
            })
    
    def validate(self):
        """执行完整的验证"""
        if not self.parse_jmx():
            return False
            
        self.check_threadgroup_config()
        self.check_assertions()
        self.check_listeners()
        self.check_timers()
        
        return True
    
    def generate_validation_report(self):
        """生成验证报告"""
        if not self.validate():
            return None
            
        report = {
            'jmx_file': self.jmx_file,
            'check_date': str(Path(self.jmx_file).stat().st_mtime),
            'total_issues': len(self.check_results),
            'issues_by_severity': {
                '错误': len([r for r in self.check_results if r['severity'] == '错误']),
                '警告': len([r for r in self.check_results if r['severity'] == '警告']),
                '建议': len([r for r in self.check_results if r['severity'] == '建议'])
            },
            'detailed_results': self.check_results
        }
        
        # 保存报告
        report_file = f"validation_report_{Path(self.jmx_file).stem}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"验证报告已保存到: {report_file}")
        return report

# 使用示例
if __name__ == "__main__":
    validator = JMXValidator("test_plan.jmx")
    report = validator.generate_validation_report()
    if report:
        print(f"发现 {report['total_issues']} 个问题")
        for issue in report['detailed_results']:
            print(f"[{issue['severity']}] {issue['category']}: {issue['issue']}")