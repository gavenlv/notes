#!/usr/bin/env python3
"""
Test script for MySQL database connection
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.configuration import EnvironmentConfigurationManager
from core.database_connections import DatabaseConnectionFactory


def test_mysql_connection():
    """Test MySQL database connection"""
    print("Testing MySQL database connection...")
    
    # Get project root (parent of src directory)
    project_root = os.path.dirname(current_dir)
    
    # Create configuration manager
    env_file = os.path.join(project_root, 'config', 'environment.env')
    config_manager = EnvironmentConfigurationManager(env_file)
    
    # Load configuration
    config_manager.load_config()
    
    # Create MySQL connection
    mysql_connection = DatabaseConnectionFactory.create_mysql_connection(config_manager)
    
    # Test connection
    if mysql_connection.connect():
        print("✅ MySQL connection successful")
        
        # Get connection info
        info = mysql_connection.get_connection_info()
        print(f"   Host: {info.get('host')}")
        print(f"   Port: {info.get('port')}")
        print(f"   Database: {info.get('database')}")
        print(f"   User: {info.get('user')}")
        
        # Test if connected
        if mysql_connection.is_connected():
            print("✅ Connection is active")
        else:
            print("❌ Connection is not active")
        
        # Disconnect
        mysql_connection.disconnect()
        print("🔌 MySQL connection closed")
        
        return True
    else:
        print("❌ MySQL connection failed")
        return False


def main():
    """Main test function"""
    try:
        success = test_mysql_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()