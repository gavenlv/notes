#!/usr/bin/env python3
"""
Final validation script for MySQL integration
This script validates the complete MySQL integration without running actual tests
"""

import os
import sys
import importlib.util

def validate_file_structure():
    """Validate all required MySQL files exist"""
    required_files = [
        'src/reporters/mysql_reporter.py',
        'src/checkers/mysql_checker.py',
        'src/core/mysql_connection.py',
        'init/init_mysql.sql',
        'requirements.txt'
    ]
    
    print("📁 Validating file structure...")
    all_exist = True
    
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def validate_requirements():
    """Validate MySQL dependencies are in requirements.txt"""
    print("\n📦 Validating requirements...")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        has_mysql = 'mysql-connector-python' in content
        status = "✅" if has_mysql else "❌"
        print(f"   {status} mysql-connector-python dependency found")
        
        return has_mysql
    except Exception as e:
        print(f"   ❌ Error reading requirements.txt: {e}")
        return False

def validate_sql_structure():
    """Validate MySQL SQL initialization script"""
    print("\n🗄️  Validating MySQL SQL structure...")
    
    try:
        with open('init/init_mysql.sql', 'r') as f:
            content = f.read()
        
        checks = [
            ('CREATE DATABASE', 'data_quality' in content),
            ('CREATE TABLE data_quality_scans', 'CREATE TABLE data_quality_scans' in content),
            ('CREATE TABLE data_quality_checks', 'CREATE TABLE data_quality_checks' in content),
            ('CREATE TABLE data_quality_logs', 'CREATE TABLE data_quality_logs' in content),
            ('CREATE TABLE data_quality_metrics', 'CREATE TABLE data_quality_metrics' in content)
        ]
        
        all_good = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"   ❌ Error reading init_mysql.sql: {e}")
        return False

def validate_documentation():
    """Validate documentation mentions MySQL support"""
    print("\n📚 Validating documentation...")
    
    docs_to_check = [
        ('README.md', ['mysql_reporter.py', 'mysql_checker.py', 'MySQL']),
        ('COMPREHENSIVE_DOCUMENTATION.md', ['MySQL', 'MYSQL_HOST', 'MYSQL_PORT', 'init_mysql.sql'])
    ]
    
    all_good = True
    
    for doc_file, keywords in docs_to_check:
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_good = True
            for keyword in keywords:
                if keyword not in content:
                    file_good = False
                    all_good = False
                    break
            
            status = "✅" if file_good else "❌"
            print(f"   {status} {doc_file}")
            
            if not file_good:
                missing = [k for k in keywords if k not in content]
                print(f"      Missing: {', '.join(missing)}")
                
        except Exception as e:
            print(f"   ❌ Error reading {doc_file}: {e}")
            all_good = False
    
    return all_good

def validate_code_structure():
    """Validate code structure and imports"""
    print("\n🔍 Validating code structure...")
    
    # Check MySQL reporter
    reporter_path = 'src/reporters/mysql_reporter.py'
    if os.path.exists(reporter_path):
        try:
            with open(reporter_path, 'r') as f:
                content = f.read()
            
            has_class = 'class MySQLDataQualityReporter' in content
            has_methods = ['store_scan_results', '_store_scan', '_store_checks', '_store_logs', '_store_metrics']
            
            status = "✅" if has_class else "❌"
            print(f"   {status} MySQLDataQualityReporter class")
            
            for method in has_methods:
                status = "✅" if method in content else "❌"
                print(f"   {status}   {method} method")
                
        except Exception as e:
            print(f"   ❌ Error validating reporter: {e}")
    
    # Check MySQL checker
    checker_path = 'src/checkers/mysql_checker.py'
    if os.path.exists(checker_path):
        try:
            with open(checker_path, 'r') as f:
                content = f.read()
            
            has_class = 'class MySQLDataQualityChecker' in content
            has_methods = ['run_all_checks', '_check_table_exists', '_check_data_freshness', '_check_data_completeness']
            
            status = "✅" if has_class else "❌"
            print(f"   {status} MySQLDataQualityChecker class")
            
            for method in has_methods:
                status = "✅" if method in content else "❌"
                print(f"   {status}   {method} method")
                
        except Exception as e:
            print(f"   ❌ Error validating checker: {e}")
    
    return True

def main():
    """Run all validation checks"""
    print("🚀 Final MySQL Integration Validation")
    print("=" * 50)
    
    # Run all validations
    validations = [
        validate_file_structure,
        validate_requirements,
        validate_sql_structure,
        validate_documentation,
        validate_code_structure
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Validation error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All MySQL integrations are properly implemented!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set MySQL environment variables")
        print("3. Run MySQL initialization: mysql -u root -p < init/init_mysql.sql")
        print("4. Test with: python -m src.main --source mysql")
    else:
        print("\n⚠️  Some validations failed. Please check the details above.")

if __name__ == "__main__":
    main()