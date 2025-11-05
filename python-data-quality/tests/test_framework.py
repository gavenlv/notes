"""
Test Suite for Python Data Quality Framework
Validates framework functionality and component integration.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Add src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_manager import ConfigManager
from database_adapter import DatabaseAdapter
from rule_engine import DataQualityRule, RuleEngine
from report_generator import CucumberStyleReport


class TestConfigManager:
    """Test configuration management functionality."""
    
    def test_config_initialization(self):
        """Test ConfigManager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test environment file
            env_file = Path(temp_dir) / "test.env"
            env_file.write_text("""
CLICKHOUSE_HOST=test_host
CLICKHOUSE_PORT=9440
CLICKHOUSE_USER=test_user
CLICKHOUSE_PASSWORD=test_pass
CLICKHOUSE_SSL_ENABLED=true
""")
            
            # Create test config file
            config_file = Path(temp_dir) / "test_config.yml"
            config_file.write_text("""
rules:
  test_rule:
    type: completeness
    table: test_table
""")
            
            config_manager = ConfigManager(str(env_file), str(config_file))
            
            # Test database configuration
            db_config = config_manager.get_database_config()
            assert db_config['host'] == 'test_host'
            assert db_config['port'] == 9440
            assert db_config['user'] == 'test_user'
            assert db_config['secure'] is True
    
    def test_missing_config_files(self):
        """Test handling of missing configuration files."""
        config_manager = ConfigManager("nonexistent.env", "nonexistent.yml")
        
        # Should not raise exceptions
        db_config = config_manager.get_database_config()
        assert db_config['host'] == 'localhost'  # Default value
    
    def test_environment_variable_override(self):
        """Test environment variable override functionality."""
        os.environ['CLICKHOUSE_HOST'] = 'env_host'
        
        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()
        
        assert db_config['host'] == 'env_host'
        
        # Cleanup
        del os.environ['CLICKHOUSE_HOST']


class TestDataQualityRule:
    """Test data quality rule functionality."""
    
    def test_rule_initialization(self):
        """Test DataQualityRule initialization."""
        rule_config = {
            'type': 'completeness',
            'description': 'Test rule',
            'table': 'test_table',
            'enabled': True
        }
        
        rule = DataQualityRule('test_rule', rule_config)
        
        assert rule.name == 'test_rule'
        assert rule.rule_type == 'completeness'
        assert rule.enabled is True
    
    def test_rule_validation(self):
        """Test rule configuration validation."""
        # Valid completeness rule
        valid_rule = DataQualityRule('valid', {
            'type': 'completeness',
            'table': 'test_table'
        })
        assert valid_rule.validate_configuration() is True
        
        # Invalid completeness rule (missing table)
        invalid_rule = DataQualityRule('invalid', {
            'type': 'completeness'
        })
        assert invalid_rule.validate_configuration() is False
    
    def test_disabled_rule(self):
        """Test behavior of disabled rules."""
        rule = DataQualityRule('disabled', {
            'enabled': False,
            'type': 'completeness',
            'table': 'test_table'
        })
        
        # Mock database
        mock_db = Mock()
        
        result = rule.execute(mock_db)
        
        assert result['skipped'] is True
        assert result['enabled'] is False
        assert mock_db.execute_query.called is False


class TestRuleEngine:
    """Test rule engine functionality."""
    
    def test_rule_loading(self):
        """Test loading rules from YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = Path(temp_dir) / "rules.yml"
            rules_file.write_text("""
test_rule_1:
  type: completeness
  table: table1
  enabled: true

test_rule_2:
  type: accuracy
  table: table2
  column: col1
  enabled: false
""")
            
            rule_engine = RuleEngine(str(rules_file))
            
            assert 'test_rule_1' in rule_engine.rules
            assert 'test_rule_2' in rule_engine.rules
            assert rule_engine.rules['test_rule_1'].enabled is True
            assert rule_engine.rules['test_rule_2'].enabled is False
    
    def test_rule_execution(self):
        """Test rule execution with mock database."""
        rule_engine = RuleEngine()
        
        # Add a test rule
        rule_engine.add_rule('test_rule', {
            'type': 'completeness',
            'table': 'test_table',
            'expected_rows': 100,
            'tolerance': 0.1
        })
        
        # Mock database
        mock_db = Mock()
        mock_db.get_table_row_count.return_value = 95
        
        results = rule_engine.execute_rules(mock_db)
        
        assert len(results) == 1
        assert results[0]['rule_name'] == 'test_rule'
        assert results[0]['rule_type'] == 'completeness'
        assert mock_db.get_table_row_count.called is True


class TestCucumberStyleReport:
    """Test cucumber-style report generation."""
    
    def test_report_generation(self):
        """Test HTML report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = CucumberStyleReport(temp_dir)
            
            # Sample test results
            test_results = [
                {
                    'rule_name': 'test_rule_1',
                    'rule_type': 'completeness',
                    'success': True,
                    'execution_time_seconds': 1.5,
                    'timestamp': '2023-01-01T00:00:00',
                    'table': 'test_table',
                    'actual_row_count': 95,
                    'expected_row_count': 100,
                    'within_tolerance': True
                },
                {
                    'rule_name': 'test_rule_2',
                    'rule_type': 'accuracy',
                    'success': False,
                    'execution_time_seconds': 2.0,
                    'timestamp': '2023-01-01T00:00:00',
                    'error': 'Connection failed',
                    'error_type': 'ConnectionError'
                }
            ]
            
            report_path = reporter.generate_report(test_results)
            
            assert Path(report_path).exists()
            assert report_path.endswith('.html')
            
            # Verify report content
            with open(report_path, 'r') as f:
                content = f.read()
                assert 'Data Quality Report' in content
                assert 'test_rule_1' in content
                assert 'test_rule_2' in content
    
    def test_json_report_generation(self):
        """Test JSON report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = CucumberStyleReport(temp_dir)
            
            test_results = [
                {
                    'rule_name': 'test_rule',
                    'rule_type': 'completeness',
                    'success': True,
                    'execution_time_seconds': 1.0
                }
            ]
            
            report_path = reporter.generate_json_report(test_results)
            
            assert Path(report_path).exists()
            assert report_path.endswith('.json')
            
            # Verify JSON content
            import json
            with open(report_path, 'r') as f:
                content = json.load(f)
                assert 'statistics' in content
                assert 'results' in content
                assert content['statistics']['total_rules'] == 1


class TestIntegration:
    """Integration tests for the complete framework."""
    
    @patch('database_adapter.Client')
    def test_framework_integration(self, mock_client):
        """Test integration of all framework components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup test configuration
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Environment file
            env_file = config_dir / "environment.env"
            env_file.write_text("""
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9440
CLICKHOUSE_USER=test
CLICKHOUSE_PASSWORD=test
CLICKHOUSE_SSL_ENABLED=false
""")
            
            # Rules file
            rules_file = config_dir / "rules.yml"
            rules_file.write_text("""
integration_test_rule:
  type: completeness
  table: test_table
  expected_rows: 100
  tolerance: 0.1
  enabled: true
""")
            
            # Mock database client
            mock_instance = mock_client.return_value
            mock_instance.execute.return_value = [(1,)]  # SELECT 1 result
            mock_instance.execute.return_value = [(95,)]  # Row count result
            
            # Import and test main framework
            from main import DataQualityFramework
            
            framework = DataQualityFramework(str(config_dir), "rules.yml")
            
            # Test configuration validation
            assert framework.validate_configuration() is True
            
            # Test rule execution (with mocked database)
            results = framework.run_checks()
            
            assert len(results) == 1
            assert results[0]['rule_name'] == 'integration_test_rule'


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])