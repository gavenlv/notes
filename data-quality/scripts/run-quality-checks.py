#!/usr/bin/env python3
"""
Data Quality Check Runner for ClickHouse
Executes data quality checks defined in YAML format and prints results
"""

import yaml
import clickhouse_driver
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

class DataQualityChecker:
    def __init__(self, config_file: str = "configs/data-quality-config.yml"):
        self.config = self._load_config(config_file)
        self.client = None
        self.results = []
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {config_file} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def _load_rules(self, rules_file: str) -> List[Dict[str, Any]]:
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                return rules if isinstance(rules, list) else [rules]
        except FileNotFoundError:
            print(f"Error: Rules file {rules_file} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing rules file: {e}")
            sys.exit(1)
    
    def _connect_to_clickhouse(self) -> bool:
        try:
            ch_config = self.config['clickhouse']
            self.client = clickhouse_driver.Client(
                host=ch_config['host'],
                port=ch_config['port'],
                database=ch_config['database'],
                user=ch_config['user'],
                password=ch_config['password'],
                secure=ch_config['secure'],
                settings={'timeout': ch_config['timeout']}
            )
            self.client.execute('SELECT 1')
            print("✓ Connected to ClickHouse successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to ClickHouse: {e}")
            return False
    
    def _execute_check(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sql_query = self._build_sql_query(rule)
            result = self.client.execute(sql_query, with_column_types=True)
            
            columns = [col[0] for col in result[1]]
            rows = result[0]
            
            if not rows:
                return {
                    'rule_name': rule['name'],
                    'status': 'ERROR',
                    'error': 'No results returned from query',
                    'timestamp': datetime.now().isoformat()
                }
            
            row_data = dict(zip(columns, rows[0]))
            
            return {
                'rule_name': rule['name'],
                'status': 'COMPLETED',
                'result': row_data,
                'timestamp': datetime.now().isoformat(),
                'sql_query': sql_query
            }
            
        except Exception as e:
            return {
                'rule_name': rule['name'],
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _build_sql_query(self, rule: Dict[str, Any]) -> str:
        template = rule['template']
        parameters = rule.get('parameters', {})
        
        query = template
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, str):
                query = query.replace(placeholder, value)
            else:
                query = query.replace(placeholder, str(value))
        
        return query
    
    def run_checks(self, rules_file: str) -> List[Dict[str, Any]]:
        print(f"Loading rules from: {rules_file}")
        rules = self._load_rules(rules_file)
        
        print(f"Connecting to ClickHouse...")
        if not self._connect_to_clickhouse():
            return []
        
        print(f"Executing {len(rules)} quality checks...")
        self.results = []
        
        for i, rule in enumerate(rules, 1):
            print(f"  [{i}/{len(rules)}] Running check: {rule['name']}")
            result = self._execute_check(rule)
            self.results.append(result)
            
            if result['status'] == 'COMPLETED':
                check_result = result['result'].get('check_result', 'UNKNOWN')
                print(f"    Result: {check_result}")
            else:
                print(f"    Error: {result.get('error', 'Unknown error')}")
        
        return self.results
    
    def print_summary_results(self):
        print("\n" + "="*60)
        print("DATA QUALITY CHECK SUMMARY")
        print("="*60)
        
        total_checks = len(self.results)
        completed_checks = len([r for r in self.results if r['status'] == 'COMPLETED'])
        failed_checks = len([r for r in self.results if r['status'] == 'COMPLETED' and r['result'].get('check_result') == 'FAIL'])
        error_checks = len([r for r in self.results if r['status'] == 'ERROR'])
        passed_checks = completed_checks - failed_checks
        
        print(f"Total Checks: {total_checks}")
        print(f"Completed: {completed_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print(f"Errors: {error_checks}")
        
        if failed_checks > 0:
            print(f"\nFailed Checks:")
            for result in self.results:
                if result['status'] == 'COMPLETED' and result['result'].get('check_result') == 'FAIL':
                    print(f"  - {result['rule_name']}")
        
        if error_checks > 0:
            print(f"\nError Checks:")
            for result in self.results:
                if result['status'] == 'ERROR':
                    print(f"  - {result['rule_name']}: {result.get('error', 'Unknown error')}")
    
    def print_detailed_results(self):
        print("\n" + "="*60)
        print("DETAILED CHECK RESULTS")
        print("="*60)
        
        for result in self.results:
            print(f"\nRule: {result['rule_name']}")
            print(f"Status: {result['status']}")
            print(f"Timestamp: {result['timestamp']}")
            
            if result['status'] == 'COMPLETED':
                check_data = result['result']
                print(f"Check Result: {check_data.get('check_result', 'UNKNOWN')}")
                
                for key, value in check_data.items():
                    if key != 'check_result':
                        print(f"  {key}: {value}")
                        
            elif result['status'] == 'ERROR':
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print("-" * 40)
    
    def generate_report(self, output_path: str = "reports") -> str:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(output_path, f"quality_report_{timestamp}.json")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        return json_file

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Run data quality checks for ClickHouse')
    parser.add_argument('--config', default='configs/data-quality-config.yml', 
                       help='Configuration file path')
    parser.add_argument('--rules', required=True, 
                       help='Rules file path')
    parser.add_argument('--output', default='reports', 
                       help='Output directory for reports')
    
    args = parser.parse_args()
    
    checker = DataQualityChecker(args.config)
    results = checker.run_checks(args.rules)
    
    if not results:
        print("No checks were executed. Exiting.")
        sys.exit(1)
    
    report_file = checker.generate_report(args.output)
    
    checker.print_summary_results()
    checker.print_detailed_results()
    
    print(f"\nData Quality Checks completed")
    print(f"Report saved to: {report_file}")
    
    failed_count = len([r for r in results if r['status'] == 'COMPLETED' and r['result'].get('check_result') == 'FAIL'])
    if failed_count > 0:
        print(f"Quality checks failed: {failed_count}")
        sys.exit(1)
    else:
        print("All quality checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main() 