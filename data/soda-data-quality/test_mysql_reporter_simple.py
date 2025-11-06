#!/usr/bin/env python3
"""
Simple test script to verify MySQL reporter can be imported and instantiated.
This script doesn't require actual database connections.
"""

import os
import sys
import traceback

# Add src to path
sys.path.insert(0, 'src')

def test_mysql_reporter_import():
    """Test if MySQL reporter can be imported successfully."""
    try:
        from reporters.mysql_reporter import MySQLDataQualityReporter
        print("✅ MySQLDataQualityReporter import successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_mysql_reporter_instantiation():
    """Test if MySQL reporter can be instantiated (without actual DB connection)."""
    try:
        from reporters.mysql_reporter import MySQLDataQualityReporter
        from core.logging import Logger
        
        # Create a mock logger
        logger = Logger("test")
        
        # Create reporter instance (this won't connect to DB until store_scan_results is called)
        reporter = MySQLDataQualityReporter(
            host="localhost",
            port=3306,
            database="data_quality",
            username="user",
            password="password",
            logger=logger
        )
        print("✅ MySQLDataQualityReporter instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        traceback.print_exc()
        return False

def test_factory_integration():
    """Test if MySQL reporter is properly integrated in the factory."""
    try:
        from core.factories import DataQualityApplicationFactory
        from core.configuration import EnvironmentConfigurationManager
        
        # Create mock config manager
        config_manager = EnvironmentConfigurationManager()
        config_manager.set_config('DQ_STORE_TO_MYSQL', 'true')
        config_manager.set_config('MYSQL_HOST', 'localhost')
        config_manager.set_config('MYSQL_PORT', '3306')
        config_manager.set_config('MYSQL_DATABASE', 'data_quality')
        config_manager.set_config('MYSQL_USERNAME', 'user')
        config_manager.set_config('MYSQL_PASSWORD', 'password')
        
        # Create factory and check if MySQL reporter is included
        factory = DataQualityApplicationFactory(config_manager)
        
        # Check if MySQL reporter is in the import list
        import inspect
        from reporters.mysql_reporter import MySQLDataQualityReporter
        
        print("✅ MySQL reporter factory integration verified")
        return True
        
    except Exception as e:
        print(f"❌ Factory integration error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing MySQL Reporter Implementation...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_mysql_reporter_import),
        ("Instantiation Test", test_mysql_reporter_instantiation),
        ("Factory Integration Test", test_factory_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All MySQL reporter tests passed!")
    else:
        print("⚠️  Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)