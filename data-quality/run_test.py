#!/usr/bin/env python3
"""
Simple script to run data quality tests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_quality_runner import main as run_main
import sys

def main():
    """Main function"""
    print("=== Data Quality Test Runner ===")
    print("ClickHouse connection information:")
    print("  Host: localhost")
    print("  Port: 8123")
    print("  User: admin")
    print("  Password: admin")
    print()
    
    # Set command line arguments
    sys.argv = [
        'data_quality_runner.py',
        '--config', 'configs/test-config.yml',
        '--scenario', 'basic_test'
    ]
    
    # Run basic test scenario
    try:
        exit_code = run_main()
        
        if exit_code == 0:
            print("✅ Test completed!")
            print("Report files generated in reports/ directory")
        else:
            print(f"❌ Test failed, exit code: {exit_code}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
