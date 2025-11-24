"""
Rule Engine for Data Quality Framework
Processes YAML-defined rules and executes custom SQL checks.
"""

import yaml
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from database_adapter import DatabaseAdapter


class DataQualityRule:
    """Represents a single data quality rule."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize data quality rule.
        
        Args:
            name: Rule name
            config: Rule configuration
        """
        self.name = name
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Required fields
        self.rule_type = config.get('type', 'generic')
        self.description = config.get('description', '')
        self.enabled = config.get('enabled', True)
        
        # Rule-specific configuration
        self.table = config.get('table')
        self.column = config.get('column')
        self.custom_sql = config.get('custom_sql')
        self.expected_result = config.get('expected_result')
        self.tolerance = config.get('tolerance', 0.0)
        self.threshold = config.get('threshold')
    
    def validate_configuration(self) -> bool:
        """Validate that the rule configuration is complete.
        
        Returns:
            True if configuration is valid
        """
        if not self.enabled:
            return True
        
        # Check required fields based on rule type
        if self.rule_type == 'completeness':
            if not self.table:
                self.logger.error(f"Rule {self.name}: Table name is required for completeness checks")
                return False
        
        elif self.rule_type == 'accuracy':
            if not self.custom_sql and not (self.table and self.column):
                self.logger.error(f"Rule {self.name}: Custom SQL or table/column required for accuracy checks")
                return False
        
        elif self.rule_type == 'custom_sql':
            if not self.custom_sql:
                self.logger.error(f"Rule {self.name}: Custom SQL is required for custom SQL checks")
                return False
        
        return True
    
    def execute(self, database: DatabaseAdapter) -> Dict[str, Any]:
        """Execute the data quality rule.
        
        Args:
            database: Database adapter instance
            
        Returns:
            Dictionary with execution results
        """
        if not self.enabled:
            return {
                'rule_name': self.name,
                'enabled': False,
                'skipped': True,
                'timestamp': datetime.now().isoformat()
            }
        
        start_time = datetime.now()
        
        try:
            if self.rule_type == 'completeness':
                result = self._execute_completeness_check(database)
            elif self.rule_type == 'accuracy':
                result = self._execute_accuracy_check(database)
            elif self.rule_type == 'custom_sql':
                result = self._execute_custom_sql_check(database)
            else:
                result = self._execute_generic_check(database)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result.update({
                'rule_name': self.name,
                'rule_type': self.rule_type,
                'execution_time_seconds': execution_time,
                'timestamp': start_time.isoformat(),
                'success': True
            })
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'rule_name': self.name,
                'rule_type': self.rule_type,
                'execution_time_seconds': execution_time,
                'timestamp': start_time.isoformat(),
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _execute_completeness_check(self, database: DatabaseAdapter) -> Dict[str, Any]:
        """Execute completeness check (row count validation)."""
        if not self.table:
            raise ValueError("Table name is required for completeness checks")
        
        # Get actual row count
        actual_count = database.get_table_row_count(self.table)
        
        # Check against expected value if provided
        expected_count = self.config.get('expected_rows')
        
        result = {
            'check_type': 'completeness',
            'table': self.table,
            'actual_row_count': actual_count,
            'expected_row_count': expected_count,
        }
        
        if expected_count is not None:
            tolerance = self.tolerance
            min_expected = expected_count * (1 - tolerance)
            max_expected = expected_count * (1 + tolerance)
            
            result.update({
                'within_tolerance': min_expected <= actual_count <= max_expected,
                'tolerance_percentage': tolerance * 100,
                'min_expected': min_expected,
                'max_expected': max_expected
            })
        
        return result
    
    def _execute_accuracy_check(self, database: DatabaseAdapter) -> Dict[str, Any]:
        """Execute accuracy check using custom SQL or column validation."""
        if self.custom_sql:
            return self._execute_custom_sql_check(database)
        
        if not self.table or not self.column:
            raise ValueError("Table and column names are required for accuracy checks")
        
        # Basic accuracy check: count NULL values
        sql = f"SELECT COUNT(*) FROM {self.table} WHERE {self.column} IS NULL"
        result = database.check_custom_sql(sql)
        
        null_count = result['first_row'][0] if result['first_row'] else 0
        total_count = database.get_table_row_count(self.table)
        
        accuracy_percentage = ((total_count - null_count) / total_count * 100) if total_count > 0 else 100
        
        return {
            'check_type': 'accuracy',
            'table': self.table,
            'column': self.column,
            'null_count': null_count,
            'total_count': total_count,
            'accuracy_percentage': accuracy_percentage,
            'meets_threshold': accuracy_percentage >= self.threshold if self.threshold else True
        }
    
    def _execute_custom_sql_check(self, database: DatabaseAdapter) -> Dict[str, Any]:
        """Execute custom SQL check."""
        if not self.custom_sql:
            raise ValueError("Custom SQL is required for custom SQL checks")
        
        result = database.check_custom_sql(self.custom_sql, self.expected_result)
        
        return {
            'check_type': 'custom_sql',
            'custom_sql': self.custom_sql,
            'query_result': result['result'],
            'result_count': result['result_count'],
            'execution_successful': result['executed_successfully'],
            'matches_expectation': result.get('matches_expectation', True)
        }
    
    def _execute_generic_check(self, database: DatabaseAdapter) -> Dict[str, Any]:
        """Execute generic check (fallback)."""
        # For generic checks, try to execute any provided SQL
        if self.custom_sql:
            return self._execute_custom_sql_check(database)
        
        # If no specific logic, return basic table info
        table_info = database.get_table_info(self.table) if self.table else {}
        
        return {
            'check_type': 'generic',
            'table_info': table_info,
            'message': 'Generic check executed'
        }


class RuleEngine:
    """Engine for managing and executing data quality rules."""
    
    def __init__(self, rules_file: str = "config/rules.yml"):
        """Initialize rule engine.
        
        Args:
            rules_file: Path to YAML rules file
        """
        self.rules_file = Path(rules_file)
        self.rules: Dict[str, DataQualityRule] = {}
        self.logger = logging.getLogger(__name__)
        
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load rules from YAML file."""
        if not self.rules_file.exists():
            self.logger.warning(f"Rules file not found: {self.rules_file}")
            return
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules_config = yaml.safe_load(f) or {}
            
            # Handle grouped rules structure (completeness_rules, accuracy_rules, etc.)
            rule_groups = ['completeness_rules', 'accuracy_rules', 'custom_sql_rules', 
                         'generic_checks', 'advanced_rules']
            
            rule_count = 0
            
            for group_name in rule_groups:
                if group_name in rules_config:
                    rules_list = rules_config[group_name]
                    if isinstance(rules_list, list):
                        for rule_config in rules_list:
                            if isinstance(rule_config, dict) and 'name' in rule_config:
                                rule_name = rule_config['name']
                                self.rules[rule_name] = DataQualityRule(rule_name, rule_config)
                                rule_count += 1
            
            # Also load individual rules not in groups
            for key, value in rules_config.items():
                if key not in rule_groups and key not in ['framework', 'database', 'custom_validations']:
                    if isinstance(value, dict):
                        self.rules[key] = DataQualityRule(key, value)
                        rule_count += 1
            
            self.logger.info(f"Loaded {rule_count} rules from {self.rules_file}")
            
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing rules file: {e}")
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
    
    def validate_all_rules(self) -> List[str]:
        """Validate all loaded rules.
        
        Returns:
            List of invalid rule names
        """
        invalid_rules = []
        
        for rule_name, rule in self.rules.items():
            if not rule.validate_configuration():
                invalid_rules.append(rule_name)
        
        return invalid_rules
    
    def execute_rules(self, database: DatabaseAdapter, rule_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Execute data quality rules.
        
        Args:
            database: Database adapter instance
            rule_names: Specific rules to execute (None for all)
            
        Returns:
            List of execution results
        """
        rules_to_execute = []
        
        if rule_names:
            for rule_name in rule_names:
                if rule_name in self.rules:
                    rules_to_execute.append(self.rules[rule_name])
                else:
                    self.logger.warning(f"Rule not found: {rule_name}")
        else:
            rules_to_execute = list(self.rules.values())
        
        results = []
        
        for rule in rules_to_execute:
            if rule.enabled:
                self.logger.info(f"Executing rule: {rule.name}")
                result = rule.execute(database)
                results.append(result)
            else:
                self.logger.debug(f"Skipping disabled rule: {rule.name}")
        
        return results

    def execute_all_rules(self, database: DatabaseAdapter):
        """执行所有规则"""
        try:
            results = {}
            
            # 执行所有类型的规则检查
            completeness_results = self.execute_completeness_rules(database)
            accuracy_results = self.execute_accuracy_rules(database)
            custom_sql_results = self.execute_custom_sql_rules(database)
            generic_results = self.execute_generic_checks(database)
            advanced_results = self.execute_advanced_rules(database)
            
            # 合并所有结果
            results.update(completeness_results)
            results.update(accuracy_results)
            results.update(custom_sql_results)
            results.update(generic_results)
            results.update(advanced_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"执行规则时发生错误: {str(e)}")
            raise

    def execute_completeness_rules(self, database: DatabaseAdapter):
        """执行完整性检查规则"""
        try:
            results = {}
            
            for rule_name, rule in self.rules.items():
                if rule.enabled and rule.rule_type == 'completeness':
                    result = rule.execute(database)
                    results[rule_name] = result
            
            self.logger.info(f"执行完整性检查完成: {len(results)} 条规则")
            return results
            
        except Exception as e:
            self.logger.error(f"执行完整性检查时发生错误: {str(e)}")
            return {}

    def execute_accuracy_rules(self, database: DatabaseAdapter):
        """执行准确性检查规则"""
        try:
            results = {}
            
            for rule_name, rule in self.rules.items():
                if rule.enabled and rule.rule_type == 'accuracy':
                    result = rule.execute(database)
                    results[rule_name] = result
            
            self.logger.info(f"执行准确性检查完成: {len(results)} 条规则")
            return results
            
        except Exception as e:
            self.logger.error(f"执行准确性检查时发生错误: {str(e)}")
            return {}

    def execute_custom_sql_rules(self, database: DatabaseAdapter):
        """执行自定义SQL检查规则"""
        try:
            results = {}
            
            for rule_name, rule in self.rules.items():
                if rule.enabled and rule.rule_type == 'custom_sql':
                    result = rule.execute(database)
                    results[rule_name] = result
            
            self.logger.info(f"执行自定义SQL检查完成: {len(results)} 条规则")
            return results
            
        except Exception as e:
            self.logger.error(f"执行自定义SQL检查时发生错误: {str(e)}")
            return {}

    def execute_generic_checks(self, database: DatabaseAdapter):
        """执行通用检查规则"""
        try:
            results = {}
            
            for rule_name, rule in self.rules.items():
                if rule.enabled and rule.rule_type == 'generic':
                    result = rule.execute(database)
                    results[rule_name] = result
            
            self.logger.info(f"执行通用检查完成: {len(results)} 条规则")
            return results
            
        except Exception as e:
            self.logger.error(f"执行通用检查时发生错误: {str(e)}")
            return {}

    def execute_advanced_rules(self, database: DatabaseAdapter):
        """执行高级检查规则"""
        try:
            results = {}
            
            for rule_name, rule in self.rules.items():
                if rule.enabled and rule.rule_type not in ['completeness', 'accuracy', 'custom_sql', 'generic']:
                    result = rule.execute(database)
                    results[rule_name] = result
            
            self.logger.info(f"执行高级检查完成: {len(results)} 条规则")
            return results
            
        except Exception as e:
            self.logger.error(f"执行高级检查时发生错误: {str(e)}")
            return {}
    
    def add_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> bool:
        """Add a new rule to the engine.
        
        Args:
            rule_name: Name of the rule
            rule_config: Rule configuration
            
        Returns:
            True if rule was added successfully
        """
        try:
            rule = DataQualityRule(rule_name, rule_config)
            if rule.validate_configuration():
                self.rules[rule_name] = rule
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error adding rule {rule_name}: {e}")
            return False
    
    def save_rules(self, output_file: Optional[str] = None) -> bool:
        """Save current rules to YAML file.
        
        Args:
            output_file: Output file path (None for original file)
            
        Returns:
            True if save was successful
        """
        file_path = Path(output_file) if output_file else self.rules_file
        
        try:
            rules_config = {}
            for rule_name, rule in self.rules.items():
                rules_config[rule_name] = rule.config
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(rules_config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved {len(self.rules)} rules to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving rules: {e}")
            return False