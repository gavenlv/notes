#!/usr/bin/env python3
"""
ClickHouse Migration Script
Main command-line interface for migration operations
"""

import argparse
import sys
import os

# Add the current directory to the path so we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.migration_manager import MigrationManager


def main():
    parser = argparse.ArgumentParser(description='ClickHouse Migration Tool')
    parser.add_argument('command', choices=['migrate', 'rollback', 'status', 'create', 'init', 'validate'],
                        help='Command to execute')
    parser.add_argument('--name', help='Name for new migration')
    parser.add_argument('--version', help='Target version for migrate/rollback')
    parser.add_argument('--env', default='development', help='Environment to use')
    parser.add_argument('--config', default='configs/migration-config.yml', help='Configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Preview without execution')
    
    args = parser.parse_args()
    
    try:
        # Initialize migration manager
        manager = MigrationManager(args.config)
        
        if args.command == 'migrate':
            manager.migrate(args.version, args.dry_run)
        elif args.command == 'rollback':
            manager.rollback(args.version)
        elif args.command == 'status':
            manager.status()
        elif args.command == 'create':
            if not args.name:
                print("Error: --name is required for create command")
                sys.exit(1)
            manager.create_migration(args.name)
        elif args.command == 'init':
            print("Migration framework initialized")
        elif args.command == 'validate':
            print("Migration validation not yet implemented")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()