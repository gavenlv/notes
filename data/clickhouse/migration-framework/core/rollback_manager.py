"""
ClickHouse Rollback Manager
Handles migration rollback operations and strategies
"""

class RollbackManager:
    def __init__(self, migration_manager):
        """Initialize rollback manager with migration manager"""
        self.migration_manager = migration_manager
        
    def rollback_to_version(self, target_version):
        """Rollback to specific version"""
        # Get current applied migrations
        applied = self.migration_manager._get_applied_migrations()
        
        # Find migrations to rollback
        to_rollback = []
        for version in reversed(applied):
            if version > target_version:
                to_rollback.append(version)
            else:
                break
                
        if not to_rollback:
            print(f"No migrations to rollback. Already at or before version {target_version}")
            return
            
        print(f"Rolling back {len(to_rollback)} migration(s) to version {target_version}")
        
        for version in to_rollback:
            self._execute_rollback(version)
            
    def rollback_last(self):
        """Rollback the last applied migration"""
        applied = self.migration_manager._get_applied_migrations()
        
        if not applied:
            print("No migrations to rollback")
            return
            
        last_version = applied[-1]
        print(f"Rolling back last migration: {last_version}")
        self._execute_rollback(last_version)
        
    def _execute_rollback(self, version):
        """Execute rollback for a specific version"""
        try:
            self.migration_manager._rollback_migration(version)
            print(f"Successfully rolled back version {version}")
        except Exception as e:
            print(f"Failed to rollback version {version}: {str(e)}")
            raise
            
    def generate_rollback_sql(self, migration_content):
        """Generate rollback SQL from migration content"""
        # This is a simplified implementation
        # In practice, this would be more sophisticated
        lines = migration_content.split('\n')
        rollback_lines = []
        
        for line in lines:
            if line.strip().startswith('-- ROLLBACK:'):
                rollback_lines.append(line.replace('-- ROLLBACK:', '', 1).strip())
                
        return '\n'.join(rollback_lines) if rollback_lines else None