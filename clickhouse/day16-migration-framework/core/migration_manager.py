#!/usr/bin/env python3
"""
ClickHouse Migration Manager
Main orchestrator for database migrations with rollback support.
"""

import os
import re
import yaml
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import clickhouse_connect
from clickhouse_connect.driver.client import Client


@dataclass
class MigrationInfo:
    """Migration information container."""
    version: int
    name: str
    description: str
    filename: str
    sql_content: str
    rollback_sql: Optional[str] = None
    dependencies: List[int] = None
    author: str = ""
    created_date: str = ""
    environment: str = "all"


class MigrationManager:
    """Main migration manager for ClickHouse database."""
    
    def __init__(self, config_path: str = "configs/migration-config.yml"):
        """Initialize migration manager with configuration."""
        self.config = self._load_config(config_path)
        self.client = self._create_client()
        self.migrations_dir = Path("migrations")
        self.logger = self._setup_logging()
        
        # Ensure migrations table exists
        self._ensure_migrations_table()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _create_client(self) -> Client:
        """Create ClickHouse client connection."""
        db_config = self.config['database']
        
        try:
            client = clickhouse_connect.get_client(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config.get('password', ''),
                secure=db_config.get('secure', False),
                verify=db_config.get('verify', False)
            )
            return client
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ClickHouse: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        logger = logging.getLogger('clickhouse_migration')
        logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Add file handler if specified
        if 'file' in log_config:
            handler = logging.FileHandler(log_config['file'])
            formatter = logging.Formatter(log_config.get('format', 
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _ensure_migrations_table(self):
        """Ensure the migrations tracking table exists."""
        table_name = self.config['migration']['table_name']
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            version UInt32,
            name String,
            description String,
            filename String,
            executed_at DateTime DEFAULT now(),
            execution_time_ms UInt64,
            status String DEFAULT 'success',
            rollback_version UInt32 DEFAULT 0,
            checksum String,
            environment String DEFAULT 'default'
        ) ENGINE = MergeTree()
        ORDER BY version
        """
        
        try:
            self.client.command(create_table_sql)
            self.logger.info(f"Migration tracking table '{table_name}' ensured")
        except Exception as e:
            self.logger.error(f"Failed to create migrations table: {e}")
            raise
    
    def get_migration_files(self) -> List[Path]:
        """Get all migration files from migrations directory."""
        if not self.migrations_dir.exists():
            return []
        
        migration_files = []
        for file_path in self.migrations_dir.glob("V*__*.sql"):
            migration_files.append(file_path)
        
        return sorted(migration_files)
    
    def parse_migration_file(self, file_path: Path) -> MigrationInfo:
        """Parse migration file and extract metadata."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract version and name from filename
        filename = file_path.name
        match = re.match(r'V(\d+)__(.+)\.sql', filename)
        if not match:
            raise ValueError(f"Invalid migration filename format: {filename}")
        
        version = int(match.group(1))
        name = match.group(2).replace('_', ' ')
        
        # Parse SQL content and metadata
        lines = content.split('\n')
        metadata = {}
        sql_lines = []
        rollback_lines = []
        in_rollback = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('--'):
                if 'ROLLBACK:' in line:
                    in_rollback = True
                    rollback_lines.append(line.replace('-- ROLLBACK:', '').strip())
                elif ':' in line:
                    key, value = line[2:].split(':', 1)
                    metadata[key.strip().lower()] = value.strip()
            elif line and not in_rollback:
                sql_lines.append(line)
            elif line and in_rollback:
                rollback_lines.append(line)
        
        sql_content = '\n'.join(sql_lines).strip()
        rollback_sql = '\n'.join(rollback_lines).strip() if rollback_lines else None
        
        return MigrationInfo(
            version=version,
            name=name,
            description=metadata.get('description', ''),
            filename=filename,
            sql_content=sql_content,
            rollback_sql=rollback_sql,
            dependencies=[int(dep.strip()) for dep in metadata.get('dependencies', '').split(',') if dep.strip()],
            author=metadata.get('author', ''),
            created_date=metadata.get('created', ''),
            environment=metadata.get('environment', 'all')
        )
    
    def get_executed_migrations(self) -> List[Dict]:
        """Get list of executed migrations from database."""
        table_name = self.config['migration']['table_name']
        query = f"SELECT * FROM {table_name} ORDER BY version"
        
        try:
            result = self.client.query(query)
            return result.result_rows
        except Exception as e:
            self.logger.error(f"Failed to get executed migrations: {e}")
            return []
    
    def validate_migration(self, migration: MigrationInfo) -> Tuple[bool, List[str]]:
        """Validate migration for syntax and dependencies."""
        errors = []
        
        # Check if migration already executed
        executed_versions = [row[0] for row in self.get_executed_migrations()]
        if migration.version in executed_versions:
            errors.append(f"Migration version {migration.version} already executed")
        
        # Check dependencies
        if migration.dependencies:
            for dep_version in migration.dependencies:
                if dep_version not in executed_versions:
                    errors.append(f"Dependency migration {dep_version} not executed")
        
        # Check SQL syntax (basic validation)
        if not migration.sql_content.strip():
            errors.append("Migration SQL content is empty")
        
        # Check for dangerous operations in production
        if self.config.get('environment') == 'production':
            dangerous_keywords = ['DROP DATABASE', 'DROP TABLE', 'TRUNCATE']
            for keyword in dangerous_keywords:
                if keyword in migration.sql_content.upper():
                    errors.append(f"Dangerous operation '{keyword}' detected in production")
        
        return len(errors) == 0, errors
    
    def execute_migration(self, migration: MigrationInfo, dry_run: bool = False) -> bool:
        """Execute a single migration."""
        self.logger.info(f"Executing migration V{migration.version}: {migration.name}")
        
        if dry_run:
            self.logger.info(f"DRY RUN: Would execute migration V{migration.version}")
            return True
        
        start_time = datetime.now()
        
        try:
            # Execute migration SQL
            self.client.command(migration.sql_content)
            
            # Record migration execution
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._record_migration_execution(migration, execution_time)
            
            self.logger.info(f"Successfully executed migration V{migration.version} in {execution_time:.2f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute migration V{migration.version}: {e}")
            self._record_migration_execution(migration, 0, status='failed', error=str(e))
            return False
    
    def _record_migration_execution(self, migration: MigrationInfo, execution_time: float, 
                                  status: str = 'success', error: str = None):
        """Record migration execution in tracking table."""
        table_name = self.config['migration']['table_name']
        
        insert_sql = f"""
        INSERT INTO {table_name} (
            version, name, description, filename, execution_time_ms, 
            status, environment
        ) VALUES (
            {migration.version}, '{migration.name}', '{migration.description}', 
            '{migration.filename}', {execution_time}, '{status}', 'default'
        )
        """
        
        try:
            self.client.command(insert_sql)
        except Exception as e:
            self.logger.error(f"Failed to record migration execution: {e}")
    
    def rollback_migration(self, version: int, dry_run: bool = False) -> bool:
        """Rollback a specific migration version."""
        self.logger.info(f"Rolling back migration V{version}")
        
        # Get migration info
        migration_files = self.get_migration_files()
        target_migration = None
        
        for file_path in migration_files:
            migration = self.parse_migration_file(file_path)
            if migration.version == version:
                target_migration = migration
                break
        
        if not target_migration:
            self.logger.error(f"Migration V{version} not found")
            return False
        
        if not target_migration.rollback_sql:
            self.logger.error(f"Migration V{version} has no rollback SQL")
            return False
        
        if dry_run:
            self.logger.info(f"DRY RUN: Would rollback migration V{version}")
            return True
        
        try:
            # Execute rollback SQL
            self.client.command(target_migration.rollback_sql)
            
            # Remove from executed migrations
            table_name = self.config['migration']['table_name']
            delete_sql = f"ALTER TABLE {table_name} DELETE WHERE version = {version}"
            self.client.command(delete_sql)
            
            self.logger.info(f"Successfully rolled back migration V{version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration V{version}: {e}")
            return False
    
    def migrate(self, target_version: Optional[int] = None, dry_run: bool = False) -> bool:
        """Execute all pending migrations up to target version."""
        migration_files = self.get_migration_files()
        executed_versions = [row[0] for row in self.get_executed_migrations()]
        
        # Parse and validate migrations
        pending_migrations = []
        for file_path in migration_files:
            migration = self.parse_migration_file(file_path)
            
            if migration.version not in executed_versions:
                if target_version and migration.version > target_version:
                    continue
                
                is_valid, errors = self.validate_migration(migration)
                if not is_valid:
                    for error in errors:
                        self.logger.error(f"Migration V{migration.version} validation error: {error}")
                    return False
                
                pending_migrations.append(migration)
        
        # Sort by version
        pending_migrations.sort(key=lambda m: m.version)
        
        if not pending_migrations:
            self.logger.info("No pending migrations to execute")
            return True
        
        self.logger.info(f"Found {len(pending_migrations)} pending migrations")
        
        # Execute migrations
        for migration in pending_migrations:
            if not self.execute_migration(migration, dry_run):
                return False
        
        self.logger.info("All migrations completed successfully")
        return True
    
    def status(self) -> Dict:
        """Get current migration status."""
        migration_files = self.get_migration_files()
        executed_migrations = self.get_executed_migrations()
        executed_versions = {row[0] for row in executed_migrations}
        
        status_info = {
            'total_migrations': len(migration_files),
            'executed_migrations': len(executed_migrations),
            'pending_migrations': [],
            'failed_migrations': [],
            'migration_details': []
        }
        
        for file_path in migration_files:
            migration = self.parse_migration_file(file_path)
            executed = migration.version in executed_versions
            
            migration_detail = {
                'version': migration.version,
                'name': migration.name,
                'description': migration.description,
                'filename': migration.filename,
                'executed': executed,
                'has_rollback': bool(migration.rollback_sql)
            }
            
            status_info['migration_details'].append(migration_detail)
            
            if not executed:
                status_info['pending_migrations'].append(migration.version)
        
        return status_info
    
    def create_migration(self, name: str, template: str = "basic") -> str:
        """Create a new migration file."""
        migration_files = self.get_migration_files()
        next_version = 1
        
        if migration_files:
            versions = [self.parse_migration_file(f).version for f in migration_files]
            next_version = max(versions) + 1
        
        # Create filename
        safe_name = name.replace(' ', '_').lower()
        filename = f"V{next_version}__{safe_name}.sql"
        file_path = self.migrations_dir / filename
        
        # Create migrations directory if it doesn't exist
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Generate migration content based on template
        content = self._generate_migration_template(template, next_version, name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Created migration file: {file_path}")
        return str(file_path)
    
    def _generate_migration_template(self, template: str, version: int, name: str) -> str:
        """Generate migration content from template."""
        templates = {
            "basic": f"""-- Migration: {name}
-- Version: {version}
-- Description: {name}
-- Author: 
-- Created: {datetime.now().strftime('%Y-%m-%d')}
-- Dependencies: 

-- Forward Migration
-- Add your SQL statements here

-- Rollback Migration
-- ROLLBACK: -- Add rollback SQL here
""",
            "table": f"""-- Migration: Create {name} table
-- Version: {version}
-- Description: Create {name} table with standard structure
-- Author: 
-- Created: {datetime.now().strftime('%Y-%m-%d')}
-- Dependencies: 

-- Forward Migration
CREATE TABLE IF NOT EXISTS {name} (
    id UInt32,
    name String,
    description String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id
PARTITION BY toYYYYMM(created_at);

-- Rollback Migration
-- ROLLBACK: DROP TABLE IF EXISTS {name};
""",
            "data": f"""-- Migration: Migrate {name} data
-- Version: {version}
-- Description: Migrate {name} data from old format to new format
-- Author: 
-- Created: {datetime.now().strftime('%Y-%m-%d')}
-- Dependencies: 

-- Forward Migration
-- Validate source data
-- SELECT count() as source_count FROM old_table;

-- Perform data migration
-- INSERT INTO new_table (column1, column2)
-- SELECT column1, column2 FROM old_table;

-- Validate migration
-- SELECT count() as target_count FROM new_table;

-- Rollback Migration
-- ROLLBACK: -- Add rollback SQL here
"""
        }
        
        return templates.get(template, templates["basic"])
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close() 