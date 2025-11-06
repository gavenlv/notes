"""
ClickHouse Migration Parser
Parses migration files and validates syntax
"""

import re


class MigrationParser:
    def __init__(self):
        """Initialize migration parser"""
        pass
        
    def parse(self, content):
        """Parse migration file content"""
        lines = content.split('\n')
        
        # Extract metadata from comments
        metadata = {}
        forward_sql = []
        rollback_sql = []
        
        in_rollback = False
        in_forward = False
        
        for line in lines:
            stripped = line.strip()
            
            # Parse metadata comments
            if stripped.startswith('--') and ':' in stripped:
                # Extract key-value pairs from comments
                comment_content = stripped[2:].strip()
                if ':' in comment_content:
                    key, value = comment_content.split(':', 1)
                    metadata[key.strip()] = value.strip()
                continue
                
            # Check for rollback marker
            if stripped.startswith('-- ROLLBACK:'):
                in_rollback = True
                in_forward = False
                rollback_sql.append(stripped.replace('-- ROLLBACK:', '', 1).strip())
            elif stripped.startswith('-- ROLLBACK') and ':' not in stripped:
                in_rollback = True
                in_forward = False
            elif in_rollback:
                rollback_sql.append(line)
            else:
                # Regular SQL line
                if stripped and not stripped.startswith('--'):
                    in_forward = True
                if in_forward and not in_rollback:
                    forward_sql.append(line)
                    
        return {
            'metadata': metadata,
            'forward_sql': '\n'.join(forward_sql).strip(),
            'rollback_sql': '\n'.join(rollback_sql).strip() if rollback_sql else None
        }
        
    def validate(self, parsed_migration):
        """Validate parsed migration"""
        errors = []
        
        # Check required metadata
        required_fields = ['Migration', 'Version', 'Description']
        for field in required_fields:
            if field not in parsed_migration['metadata']:
                errors.append(f"Missing required metadata field: {field}")
                
        # Check forward SQL exists
        if not parsed_migration['forward_sql']:
            errors.append("Migration must contain forward SQL statements")
            
        # Validate version format
        version = parsed_migration['metadata'].get('Version')
        if version and not str(version).isdigit():
            errors.append("Version must be a numeric value")
            
        return errors