"""
ClickHouse Migration Manager
Handles database migrations with version control and rollback capabilities
"""

import os
import re
import yaml
from datetime import datetime
from clickhouse_driver import Client


class MigrationManager:
    def __init__(self, config_path='configs/migration-config.yml'):
        """Initialize migration manager with configuration"""
        self.config = self._load_config(config_path)
        self.client = self._create_client()
        self.migration_table = self.config.get('migration', {}).get('table_name', 'schema_migrations')
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _create_client(self):
        """Create ClickHouse client from configuration"""
        db_config = self.config.get('database', {})
        return Client(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 9000),
            database=db_config.get('database', 'default'),
            user=db_config.get('user', 'default'),
            password=db_config.get('password', ''),
            secure=db_config.get('secure', False),
            verify=db_config.get('verify', False)
        )
        
    def _ensure_migration_table(self):
        """Create migration tracking table if it doesn't exist"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migration_table} (
            version String,
            description String,
            applied_at DateTime DEFAULT now(),
            success UInt8,
            execution_time UInt32
        ) ENGINE = MergeTree()
        ORDER BY version
        """
        self.client.execute(create_table_sql)
        
    def _parse_migration_file(self, file_path):
        """Parse migration file to extract metadata and SQL statements"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract metadata from comments
        metadata = {}
        for line in content.split('\n'):
            if line.startswith('--') and ':' in line:
                key, value = line[2:].strip().split(':', 1)
                metadata[key.strip()] = value.strip()
                
        # Extract forward migration (everything before ROLLBACK marker)
        forward_sql = []
        rollback_sql = []
        in_rollback = False
        
        for line in content.split('\n'):
            if line.strip().startswith('-- ROLLBACK:'):
                in_rollback = True
                rollback_sql.append(line.replace('-- ROLLBACK:', '').strip())
            elif in_rollback:
                rollback_sql.append(line)
            else:
                forward_sql.append(line)
                
        return {
            'metadata': metadata,
            'forward_sql': '\n'.join(forward_sql),
            'rollback_sql': '\n'.join(rollback_sql) if rollback_sql else None
        }
        
    def _get_applied_migrations(self):
        """Get list of already applied migrations"""
        self._ensure_migration_table()
        result = self.client.execute(f"SELECT version FROM {self.migration_table} WHERE success = 1 ORDER BY version")
        return [row[0] for row in result]
        
    def _get_pending_migrations(self):
        """Get list of pending migrations"""
        migrations_dir = 'migrations'
        if not os.path.exists(migrations_dir):
            return []
            
        applied = self._get_applied_migrations()
        pending = []
        
        # Get all migration files
        for filename in sorted(os.listdir(migrations_dir)):
            if filename.endswith('.sql') and filename.startswith('V'):
                version = filename.split('__')[0]
                if version not in applied:
                    pending.append({
                        'version': version,
                        'filename': filename,
                        'path': os.path.join(migrations_dir, filename)
                    })
                    
        return pending
        
    def migrate(self, target_version=None, dry_run=False):
        """Apply pending migrations"""
        pending = self._get_pending_migrations()
        
        if not pending:
            print("No pending migrations to apply")
            return
            
        print(f"Applying {len(pending)} migration(s)...")
        
        for migration in pending:
            if target_version and migration['version'] > target_version:
                break
                
            print(f"Applying migration {migration['version']}...")
            
            if not dry_run:
                self._apply_migration(migration)
            else:
                print(f"[DRY RUN] Would apply {migration['version']}")
                
    def _apply_migration(self, migration):
        """Apply a single migration"""
        start_time = datetime.now()
        
        try:
            # Parse migration file
            parsed = self._parse_migration_file(migration['path'])
            
            # Execute forward migration
            forward_sql = parsed['forward_sql']
            self.client.execute(forward_sql)
            
            # Record successful migration
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_migration(migration['version'], parsed['metadata'].get('Description', ''), 1, int(execution_time))
            
            print(f"Successfully applied migration {migration['version']}")
            
        except Exception as e:
            # Record failed migration
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_migration(migration['version'], str(e), 0, int(execution_time))
            
            print(f"Failed to apply migration {migration['version']}: {str(e)}")
            raise
            
    def _record_migration(self, version, description, success, execution_time):
        """Record migration in tracking table"""
        insert_sql = f"""
        INSERT INTO {self.migration_table} (version, description, success, execution_time)
        VALUES (%s, %s, %s, %s)
        """
        self.client.execute(insert_sql, [version, description, success, execution_time])
        
    def rollback(self, target_version=None):
        """Rollback migrations"""
        applied = self._get_applied_migrations()
        
        if not applied:
            print("No applied migrations to rollback")
            return
            
        # Determine which migrations to rollback
        if target_version:
            to_rollback = [v for v in reversed(applied) if v >= target_version]
        else:
            to_rollback = [applied[-1]]  # Rollback last migration
            
        print(f"Rolling back {len(to_rollback)} migration(s)...")
        
        for version in to_rollback:
            print(f"Rolling back migration {version}...")
            self._rollback_migration(version)
            
    def _rollback_migration(self, version):
        """Rollback a single migration"""
        # Find migration file
        migrations_dir = 'migrations'
        migration_file = None
        
        for filename in os.listdir(migrations_dir):
            if filename.startswith(version):
                migration_file = os.path.join(migrations_dir, filename)
                break
                
        if not migration_file:
            raise Exception(f"Migration file for version {version} not found")
            
        # Parse migration file
        parsed = self._parse_migration_file(migration_file)
        
        if not parsed['rollback_sql']:
            raise Exception(f"No rollback SQL found for migration {version}")
            
        try:
            # Execute rollback SQL
            self.client.execute(parsed['rollback_sql'])
            
            # Remove from migration table
            delete_sql = f"DELETE FROM {self.migration_table} WHERE version = '{version}'"
            self.client.execute(delete_sql)
            
            print(f"Successfully rolled back migration {version}")
            
        except Exception as e:
            print(f"Failed to rollback migration {version}: {str(e)}")
            raise
            
    def status(self):
        """Show migration status"""
        applied = self._get_applied_migrations()
        pending = self._get_pending_migrations()
        
        print("=== Migration Status ===")
        print(f"Applied migrations ({len(applied)}):")
        for version in applied:
            print(f"  ✓ {version}")
            
        print(f"\nPending migrations ({len(pending)}):")
        for migration in pending:
            print(f"  ○ {migration['version']}")
            
    def create_migration(self, name):
        """Create a new migration file"""
        # Generate version number
        migrations_dir = 'migrations'
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
            
        # Get next version number
        existing_versions = []
        for filename in os.listdir(migrations_dir):
            if filename.endswith('.sql') and filename.startswith('V'):
                version = filename.split('__')[0][1:]  # Remove 'V' prefix
                if version.isdigit():
                    existing_versions.append(int(version))
                    
        next_version = max(existing_versions) + 1 if existing_versions else 1
        version_str = f"V{next_version}__{name.replace(' ', '_')}.sql"
        file_path = os.path.join(migrations_dir, version_str)
        
        # Create migration template
        template = f"""-- Migration: {name}
-- Version: {next_version}
-- Description: {name}
-- Author: 
-- Created: {datetime.now().strftime('%Y-%m-%d')}
-- Dependencies: 

-- Forward Migration
-- Write your forward migration SQL here

-- Rollback Migration
-- ROLLBACK: Write your rollback SQL here
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)
            
        print(f"Created migration file: {file_path}")
        return file_path