#!/usr/bin/env python3
"""
ClickHouse Rollback Script
Handles migration rollback operations
"""

import argparse
import sys
import os

# Add the current directory to the path so we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.migration_manager import MigrationManager
from core.rollback_manager import RollbackManager


def main():
    parser = argparse.ArgumentParser(description='ClickHouse Rollback Tool')
    parser.add_argument('--version', help='Target version to rollback to')
    parser.add_argument('--config', default='configs/migration-config.yml', help='Configuration file')
    parser.add_argument('--last', action='store_true', help='Rollback last migration only')
    
    args = parser.parse_args()
    
    try:
        # Initialize migration manager and rollback manager
        manager = MigrationManager(args.config)
        rollback_manager = RollbackManager(manager)
        
        if args.last:
            rollback_manager.rollback_last()
        elif args.version:
            rollback_manager.rollback_to_version(args.version)
        else:
            print("Error: Either --version or --last must be specified")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()