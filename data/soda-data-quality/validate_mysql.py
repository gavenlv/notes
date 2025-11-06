#!/usr/bin/env python3
"""
Validation script for MySQL reporter implementation
"""

import os
import sys

def main():
    print("Validating MySQL Reporter Implementation...")
    print("=" * 50)
    
    # Check MySQL reporter file
    mysql_reporter_path = 'src/reporters/mysql_reporter.py'
    print(f"\n1. Checking MySQL reporter file: {mysql_reporter_path}")
    
    if os.path.exists(mysql_reporter_path):
        print("✅ File exists")
        
        # Check file content
        try:
            with open(mysql_reporter_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'MySQLDataQualityReporter' in content:
                print("✅ MySQLDataQualityReporter class found")
            else:
                print("❌ MySQLDataQualityReporter class not found")
                
            if 'from ..core.mysql_connection import MySQLConnection' in content:
                print("✅ MySQLConnection import found")
            else:
                print("❌ MySQLConnection import not found")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print("❌ MySQL reporter file not found")
    
    # Check MySQL connection file
    mysql_connection_path = 'src/core/mysql_connection.py'
    print(f"\n2. Checking MySQL connection file: {mysql_connection_path}")
    
    if os.path.exists(mysql_connection_path):
        print("✅ File exists")
        
        try:
            with open(mysql_connection_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'MySQLConnection' in content:
                print("✅ MySQLConnection class found")
            else:
                print("❌ MySQLConnection class not found")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print("❌ MySQL connection file not found")
    
    # Check factory file
    factory_path = 'src/core/factories.py'
    print(f"\n3. Checking factory file: {factory_path}")
    
    if os.path.exists(factory_path):
        print("✅ File exists")
        
        try:
            with open(factory_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'MySQLDataQualityReporter' in content:
                print("✅ MySQLDataQualityReporter referenced in factory")
            else:
                print("❌ MySQLDataQualityReporter not found in factory")
                
            if 'DQ_STORE_TO_MYSQL' in content:
                print("✅ MySQL configuration key found")
            else:
                print("❌ MySQL configuration key not found")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print("❌ Factory file not found")
    
    # Check configuration file
    config_path = 'src/core/configuration.py'
    print(f"\n4. Checking configuration file: {config_path}")
    
    if os.path.exists(config_path):
        print("✅ File exists")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'DQ_STORE_TO_MYSQL' in content:
                print("✅ MySQL configuration key found")
            else:
                print("❌ MySQL configuration key not found")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print("❌ Configuration file not found")
    
    print("\n" + "=" * 50)
    print("Validation complete!")

if __name__ == "__main__":
    main()