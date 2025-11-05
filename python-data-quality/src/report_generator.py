"""
Cucumber-style HTML Report Generator for Data Quality Framework
Generates rich, visual reports with detailed test results.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
from jinja2 import Template


class CucumberStyleReport:
    """Generates cucumber-style HTML reports for data quality checks."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # HTML template for cucumber-style reports
        self.html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Quality Report - {{ timestamp }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #007bff;
        }
        .summary-card.passed { border-left-color: #28a745; }
        .summary-card.failed { border-left-color: #dc3545; }
        .summary-card.skipped { border-left-color: #ffc107; }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 2em;
            font-weight: bold;
        }
        .rule-results {
            margin-top: 30px;
        }
        .rule-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .rule-header {
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: between;
            align-items: center;
        }
        .rule-header.passed { background: #d4edda; border-left: 4px solid #28a745; }
        .rule-header.failed { background: #f8d7da; border-left: 4px solid #dc3545; }
        .rule-header.skipped { background: #fff3cd; border-left: 4px solid #ffc107; }
        .rule-content {
            padding: 20px;
        }
        .details-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .details-table th,
        .details-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        .details-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .badge.passed { background: #28a745; color: white; }
        .badge.failed { background: #dc3545; color: white; }
        .badge.skipped { background: #ffc107; color: black; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Data Quality Report</h1>
            <p class="timestamp">Generated on: {{ timestamp }}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{{ total_rules }}</h3>
                <p>Total Rules</p>
            </div>
            <div class="summary-card passed">
                <h3>{{ passed_rules }}</h3>
                <p>Passed</p>
            </div>
            <div class="summary-card failed">
                <h3>{{ failed_rules }}</h3>
                <p>Failed</p>
            </div>
            <div class="summary-card skipped">
                <h3>{{ skipped_rules }}</h3>
                <p>Skipped</p>
            </div>
            <div class="summary-card">
                <h3>{{ success_rate }}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
        
        <div class="rule-results">
            <h2>Rule Results</h2>
            {% for result in results %}
            <div class="rule-card">
                <div class="rule-header {{ result.status }}">
                    <div>
                        <h3>{{ result.rule_name }}</h3>
                        <p>{{ result.description }}</p>
                    </div>
                    <span class="badge {{ result.status }}">{{ result.status|upper }}</span>
                </div>
                <div class="rule-content">
                    <p><strong>Type:</strong> {{ result.rule_type }}</p>
                    <p><strong>Execution Time:</strong> {{ result.execution_time_seconds }} seconds</p>
                    
                    {% if result.details %}
                    <h4>Details:</h4>
                    <table class="details-table">
                        {% for key, value in result.details.items() %}
                        <tr>
                            <th>{{ key }}</th>
                            <td>{{ value }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                    
                    {% if result.error %}
                    <div style="background: #f8d7da; padding: 10px; border-radius: 4px; margin-top: 10px;">
                        <strong>Error:</strong> {{ result.error }}
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """
    
    def generate_report(self, results: List[Dict[str, Any]], report_name: Optional[str] = None) -> str:
        """Generate cucumber-style HTML report.
        
        Args:
            results: List of rule execution results
            report_name: Custom report name (optional)
            
        Returns:
            Path to generated report file
        """
        # Process results and calculate statistics
        processed_results = self._process_results(results)
        stats = self._calculate_statistics(processed_results)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = report_name or f"data_quality_report_{timestamp}.html"
        report_path = self.output_dir / filename
        
        # Render HTML template
        template = Template(self.html_template)
        html_content = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            results=processed_results,
            **stats
        )
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated report: {report_path}")
        return str(report_path)
    
    def _process_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw results into format suitable for reporting.
        
        Args:
            results: Raw rule execution results
            
        Returns:
            Processed results
        """
        processed = []
        
        for result in results:
            # Determine status
            if result.get('skipped', False):
                status = 'skipped'
            elif not result.get('success', False):
                status = 'failed'
            else:
                # Check specific success conditions based on rule type
                status = self._determine_rule_status(result)
            
            processed_result = {
                'rule_name': result.get('rule_name', 'Unknown'),
                'rule_type': result.get('rule_type', 'generic'),
                'description': self._get_rule_description(result),
                'status': status,
                'execution_time_seconds': result.get('execution_time_seconds', 0),
                'timestamp': result.get('timestamp', ''),
                'details': self._extract_details(result),
                'error': result.get('error')
            }
            
            processed.append(processed_result)
        
        return processed
    
    def _determine_rule_status(self, result: Dict[str, Any]) -> str:
        """Determine the status of a rule based on its results.
        
        Args:
            result: Rule execution result
            
        Returns:
            'passed' or 'failed'
        """
        rule_type = result.get('rule_type')
        
        if rule_type == 'completeness':
            return 'passed' if result.get('within_tolerance', False) else 'failed'
        
        elif rule_type == 'accuracy':
            return 'passed' if result.get('meets_threshold', True) else 'failed'
        
        elif rule_type == 'custom_sql':
            return 'passed' if result.get('matches_expectation', True) else 'failed'
        
        else:
            return 'passed' if result.get('success', False) else 'failed'
    
    def _get_rule_description(self, result: Dict[str, Any]) -> str:
        """Extract rule description from results.
        
        Args:
            result: Rule execution result
            
        Returns:
            Rule description
        """
        rule_type = result.get('rule_type')
        
        if rule_type == 'completeness':
            table = result.get('table', 'Unknown')
            return f"Completeness check for table: {table}"
        
        elif rule_type == 'accuracy':
            table = result.get('table', 'Unknown')
            column = result.get('column', 'Unknown')
            return f"Accuracy check for {table}.{column}"
        
        elif rule_type == 'custom_sql':
            return "Custom SQL validation"
        
        else:
            return "Generic data quality check"
    
    def _extract_details(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant details for reporting.
        
        Args:
            result: Rule execution result
            
        Returns:
            Dictionary of details
        """
        details = {}
        rule_type = result.get('rule_type')
        
        if rule_type == 'completeness':
            details.update({
                'Table': result.get('table'),
                'Actual Rows': result.get('actual_row_count'),
                'Expected Rows': result.get('expected_row_count'),
                'Within Tolerance': result.get('within_tolerance', False),
                'Tolerance': f"{result.get('tolerance_percentage', 0)}%"
            })
        
        elif rule_type == 'accuracy':
            details.update({
                'Table': result.get('table'),
                'Column': result.get('column'),
                'Null Count': result.get('null_count'),
                'Total Count': result.get('total_count'),
                'Accuracy': f"{result.get('accuracy_percentage', 0):.2f}%",
                'Meets Threshold': result.get('meets_threshold', True)
            })
        
        elif rule_type == 'custom_sql':
            details.update({
                'SQL Executed': result.get('custom_sql'),
                'Result Count': result.get('result_count'),
                'Execution Successful': result.get('execution_successful', False)
            })
        
        # Filter out None values
        return {k: v for k, v in details.items() if v is not None}
    
    def _calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate report statistics.
        
        Args:
            results: Processed rule results
            
        Returns:
            Statistics dictionary
        """
        total = len(results)
        passed = len([r for r in results if r['status'] == 'passed'])
        failed = len([r for r in results if r['status'] == 'failed'])
        skipped = len([r for r in results if r['status'] == 'skipped'])
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            'total_rules': total,
            'passed_rules': passed,
            'failed_rules': failed,
            'skipped_rules': skipped,
            'success_rate': round(success_rate, 2)
        }
    
    def generate_json_report(self, results: List[Dict[str, Any]], report_name: Optional[str] = None) -> str:
        """Generate JSON report for programmatic consumption.
        
        Args:
            results: List of rule execution results
            report_name: Custom report name (optional)
            
        Returns:
            Path to generated JSON report
        """
        processed_results = self._process_results(results)
        stats = self._calculate_statistics(processed_results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = report_name or f"data_quality_report_{timestamp}.json"
        report_path = self.output_dir / filename
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'results': processed_results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"Generated JSON report: {report_path}")
        return str(report_path)


class ReportManager:
    """Manages multiple report formats and generations."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report manager.
        
        Args:
            output_dir: Base output directory
        """
        self.output_dir = Path(output_dir)
        self.cucumber_reporter = CucumberStyleReport(output_dir)
        self.logger = logging.getLogger(__name__)
    
    def generate_reports(self, results: List[Dict[str, Any]], formats: List[str] = None) -> Dict[str, str]:
        """Generate reports in multiple formats.
        
        Args:
            results: Rule execution results
            formats: List of formats to generate
            
        Returns:
            Dictionary mapping format to file path
        """
        if formats is None:
            formats = ['html', 'json']
        
        report_paths = {}
        
        for fmt in formats:
            if fmt == 'html':
                path = self.cucumber_reporter.generate_report(results)
                report_paths['html'] = path
            elif fmt == 'json':
                path = self.cucumber_reporter.generate_json_report(results)
                report_paths['json'] = path
            else:
                self.logger.warning(f"Unsupported report format: {fmt}")
        
        return report_paths