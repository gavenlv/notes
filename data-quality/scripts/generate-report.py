#!/usr/bin/env python3
"""
Data Quality Report Generator
Generates comprehensive reports from data quality check results
"""

import json
import csv
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

class ReportGenerator:
    def __init__(self, results_file: str):
        self.results = self._load_results(results_file)
    
    def _load_results(self, results_file: str) -> List[Dict[str, Any]]:
        """Load results from JSON file"""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Results file {results_file} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing results file: {e}")
            sys.exit(1)
    
    def generate_csv_report(self, output_path: str) -> str:
        """Generate CSV report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(output_path, f"quality_report_{timestamp}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Rule Name', 'Status', 'Check Result', 'Timestamp', 'Error'])
            
            for result in self.results:
                check_result = ''
                error = ''
                
                if result['status'] == 'COMPLETED':
                    check_result = result.get('result', {}).get('check_result', '')
                elif result['status'] == 'ERROR':
                    error = result.get('error', '')
                
                writer.writerow([
                    result['rule_name'],
                    result['status'],
                    check_result,
                    result['timestamp'],
                    error
                ])
        
        return csv_file
    
    def generate_html_report(self, output_path: str) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = os.path.join(output_path, f"quality_report_{timestamp}.html")
        
        total_checks = len(self.results)
        completed_checks = len([r for r in self.results if r['status'] == 'COMPLETED'])
        passed_checks = len([r for r in self.results if r['status'] == 'COMPLETED' and r['result'].get('check_result') == 'PASS'])
        failed_checks = len([r for r in self.results if r['status'] == 'COMPLETED' and r['result'].get('check_result') == 'FAIL'])
        error_checks = len([r for r in self.results if r['status'] == 'ERROR'])
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Data Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .check {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .pass {{ background-color: #d4edda; border-color: #c3e6cb; }}
        .fail {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        .error {{ background-color: #fff3cd; border-color: #ffeaa7; }}
        .metrics {{ font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Data Quality Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Checks: {total_checks}</p>
        <p>Completed: {completed_checks}</p>
        <p>Passed: {passed_checks}</p>
        <p>Failed: {failed_checks}</p>
        <p>Errors: {error_checks}</p>
    </div>
    
    <div class="checks">
        <h2>Detailed Results</h2>
"""
        
        for result in self.results:
            status_class = 'pass'
            if result['status'] == 'ERROR':
                status_class = 'error'
            elif result['status'] == 'COMPLETED' and result['result'].get('check_result') == 'FAIL':
                status_class = 'fail'
            
            html_content += f"""
        <div class="check {status_class}">
            <h3>{result['rule_name']}</h3>
            <p><strong>Status:</strong> {result['status']}</p>
            <p><strong>Timestamp:</strong> {result['timestamp']}</p>
"""
            
            if result['status'] == 'COMPLETED':
                check_data = result['result']
                html_content += f'<p><strong>Result:</strong> {check_data.get("check_result", "UNKNOWN")}</p>'
                html_content += '<div class="metrics"><strong>Metrics:</strong><br>'
                for key, value in check_data.items():
                    if key != 'check_result':
                        html_content += f'  {key}: {value}<br>'
                html_content += '</div>'
            else:
                html_content += f'<p><strong>Error:</strong> {result.get("error", "Unknown error")}</p>'
            
            html_content += '</div>'
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file
    
    def generate_all_reports(self, output_path: str = "reports") -> Dict[str, str]:
        """Generate all report formats"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        reports = {}
        
        # Generate CSV report
        reports['csv'] = self.generate_csv_report(output_path)
        
        # Generate HTML report
        reports['html'] = self.generate_html_report(output_path)
        
        return reports

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate data quality reports')
    parser.add_argument('--results', required=True, 
                       help='Results JSON file path')
    parser.add_argument('--output', default='reports', 
                       help='Output directory for reports')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.results)
    reports = generator.generate_all_reports(args.output)
    
    print("Reports generated:")
    for format_type, file_path in reports.items():
        print(f"  {format_type.upper()}: {file_path}")

if __name__ == "__main__":
    main() 