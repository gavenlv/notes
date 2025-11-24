#!/usr/bin/env python3
"""
ClickHouse Migration Status Script
Shows current migration status
"""

import argparse
import sys
import os

# Add the current directory to the path so we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.migration_manager import MigrationManager


def main():
    parser = argparse.ArgumentParser(description='ClickHouse Migration Status')
    parser.add_argument('--config', default='configs/migration-config.yml', help='Configuration file')
    
    args = parser.parse_args()
    
    try:
        # Initialize migration manager
        manager = MigrationManager(args.config)
        manager.status()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()