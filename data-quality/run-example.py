#!/usr/bin/env python3
"""
Example script demonstrating how to use the data quality framework
"""

import os
import sys
from scripts.run_quality_checks import DataQualityChecker

def main():
    print("Data Quality Framework Example")
    print("=" * 40)
    
    # Check if example files exist
    config_file = "configs/data-quality-config.yml"
    rules_file = "examples/sample-rules.yml"
    
    if not os.path.exists(config_file):
        print(f"Error: Configuration file {config_file} not found")
        print("Please ensure you have set up the configuration files")
        sys.exit(1)
    
    if not os.path.exists(rules_file):
        print(f"Error: Rules file {rules_file} not found")
        print("Please ensure you have created example rules")
        sys.exit(1)
    
    # Initialize checker
    checker = DataQualityChecker(config_file)
    
    # Run checks
    print("Running data quality checks...")
    results = checker.run_checks(rules_file)
    
    if not results:
        print("No checks were executed. Please check your configuration.")
        sys.exit(1)
    
    # Print results
    checker.print_summary_results()
    checker.print_detailed_results()
    
    # Generate report
    report_file = checker.generate_report("reports")
    print(f"\nReport saved to: {report_file}")
    
    # Check exit code
    failed_count = len([r for r in results if r['status'] == 'COMPLETED' and r['result'].get('check_result') == 'FAIL'])
    if failed_count > 0:
        print(f"Quality checks failed: {failed_count}")
        sys.exit(1)
    else:
        print("All quality checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main() 