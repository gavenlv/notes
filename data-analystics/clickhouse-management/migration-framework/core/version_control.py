"""
ClickHouse Migration Version Control
Manages migration versions and execution history
"""

from datetime import datetime


class VersionControl:
    def __init__(self, client, table_name='schema_migrations'):
        """Initialize version control with ClickHouse client"""
        self.client = client
        self.table_name = table_name
        self._ensure_table_exists()
        
    def _ensure_table_exists(self):
        """Create migration tracking table if it doesn't exist"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            version String,
            description String,
            author String,
            applied_at DateTime DEFAULT now(),
            success UInt8,
            execution_time UInt32,
            checksum String
        ) ENGINE = MergeTree()
        ORDER BY version
        """
        self.client.execute(create_table_sql)
        
    def record_migration(self, version, description, author, success, execution_time, checksum=None):
        """Record a migration in the tracking table"""
        insert_sql = f"""
        INSERT INTO {self.table_name} 
        (version, description, author, success, execution_time, checksum)
        VALUES
        """
        
        self.client.execute(insert_sql, [{
            'version': version,
            'description': description,
            'author': author,
            'success': success,
            'execution_time': execution_time,
            'checksum': checksum or ''
        }])
        
    def get_applied_migrations(self):
        """Get list of applied migrations ordered by version"""
        result = self.client.execute(f"""
        SELECT version, description, author, applied_at, success, execution_time
        FROM {self.table_name}
        WHERE success = 1
        ORDER BY version
        """)
        
        return [{
            'version': row[0],
            'description': row[1],
            'author': row[2],
            'applied_at': row[3],
            'success': row[4],
            'execution_time': row[5]
        } for row in result]
        
    def is_migration_applied(self, version):
        """Check if a migration has been successfully applied"""
        result = self.client.execute(f"""
        SELECT count(*) FROM {self.table_name}
        WHERE version = %(version)s AND success = 1
        """, {'version': version})
        
        return result[0][0] > 0
        
    def remove_migration_record(self, version):
        """Remove a migration record (used during rollback)"""
        self.client.execute(f"""
        DELETE FROM {self.table_name}
        WHERE version = %(version)s
        """, {'version': version})
        
    def get_migration_history(self):
        """Get complete migration history"""
        result = self.client.execute(f"""
        SELECT version, description, author, applied_at, success, execution_time
        FROM {self.table_name}
        ORDER BY applied_at DESC
        """)
        
        return [{
            'version': row[0],
            'description': row[1],
            'author': row[2],
            'applied_at': row[3],
            'success': row[4],
            'execution_time': row[5]
        } for row in result]
        
    def validate_migration_order(self, migrations):
        """Validate that migrations are in correct order"""
        # Extract version numbers and sort them
        versions = [m['version'] for m in migrations]
        sorted_versions = sorted(versions, key=lambda v: [int(x) if x.isdigit() else x for x in re.split('(\d+)', v)])
        
        # Check if order matches
        return versions == sorted_versions