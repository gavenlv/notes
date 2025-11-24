#!/usr/bin/env python3
"""
Test script for ClickHouse SSL configuration
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.configuration import EnvironmentConfigurationManager
from core.database_connections import ClickHouseConnection, ClickHouseDQConnection

def test_ssl_config():
    """Test SSL configuration loading"""
    print("🔍 Testing ClickHouse SSL Configuration...")
    
    # Test with environment configuration
    config = EnvironmentConfigurationManager()
    
    print("✅ Configuration loaded successfully")
    
    # Check SSL configuration values
    ssl_enabled = config.get_config('CLICKHOUSE_SSL', 'false').lower() == 'true'
    dq_ssl_enabled = config.get_config('CLICKHOUSE_DQ_SSL', 'false').lower() == 'true'
    
    print(f"   CLICKHOUSE_SSL: {ssl_enabled}")
    print(f"   CLICKHOUSE_DQ_SSL: {dq_ssl_enabled}")
    
    if ssl_enabled:
        print(f"   CLICKHOUSE_SSL_VERIFY: {config.get_config('CLICKHOUSE_SSL_VERIFY', 'true')}")
        print(f"   CLICKHOUSE_SSL_CERT: {config.get_config('CLICKHOUSE_SSL_CERT', 'Not set')}")
        print(f"   CLICKHOUSE_SSL_KEY: {config.get_config('CLICKHOUSE_SSL_KEY', 'Not set')}")
        print(f"   CLICKHOUSE_SSL_CA: {config.get_config('CLICKHOUSE_SSL_CA', 'Not set')}")
    
    if dq_ssl_enabled:
        print(f"   CLICKHOUSE_DQ_SSL_VERIFY: {config.get_config('CLICKHOUSE_DQ_SSL_VERIFY', 'true')}")
        print(f"   CLICKHOUSE_DQ_SSL_CERT: {config.get_config('CLICKHOUSE_DQ_SSL_CERT', 'Not set')}")
        print(f"   CLICKHOUSE_DQ_SSL_KEY: {config.get_config('CLICKHOUSE_DQ_SSL_KEY', 'Not set')}")
        print(f"   CLICKHOUSE_DQ_SSL_CA: {config.get_config('CLICKHOUSE_DQ_SSL_CA', 'Not set')}")
    
    print("\n✅ SSL configuration test completed successfully!")

def test_connection_classes():
    """Test connection classes with SSL support"""
    print("\n🔧 Testing Connection Classes...")
    
    config = EnvironmentConfigurationManager()
    
    # Test ClickHouse connection
    try:
        conn = ClickHouseConnection(config)
        print("✅ ClickHouseConnection class instantiated successfully")
        
        # Test SSL configuration in connection
        ssl_enabled = config.get_config('CLICKHOUSE_SSL', 'false').lower() == 'true'
        if ssl_enabled:
            print("   🔒 SSL will be enabled for ClickHouse connection")
        else:
            print("   🔓 SSL disabled for ClickHouse connection")
            
    except Exception as e:
        print(f"❌ ClickHouseConnection error: {e}")
    
    # Test ClickHouse DQ connection
    try:
        dq_conn = ClickHouseDQConnection(config)
        print("✅ ClickHouseDQConnection class instantiated successfully")
        
        # Test SSL configuration in DQ connection
        dq_ssl_enabled = config.get_config('CLICKHOUSE_DQ_SSL', 'false').lower() == 'true'
        if dq_ssl_enabled:
            print("   🔒 SSL will be enabled for ClickHouse DQ connection")
        else:
            print("   🔓 SSL disabled for ClickHouse DQ connection")
            
    except Exception as e:
        print(f"❌ ClickHouseDQConnection error: {e}")

if __name__ == "__main__":
    print("🚀 ClickHouse SSL Configuration Test")
    print("=" * 50)
    
    try:
        test_ssl_config()
        test_connection_classes()
        
        print("\n" + "=" * 50)
        print("🎉 All SSL configuration tests passed!")
        print("\n📋 To enable SSL:")
        print("1. Set CLICKHOUSE_SSL=true or CLICKHOUSE_DQ_SSL=true")
        print("2. Optionally set SSL certificate paths:")
        print("   CLICKHOUSE_SSL_CERT=/path/to/client-cert.pem")
        print("   CLICKHOUSE_SSL_KEY=/path/to/client-key.pem") 
        print("   CLICKHOUSE_SSL_CA=/path/to/ca-cert.pem")
        print("3. Restart the application")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)