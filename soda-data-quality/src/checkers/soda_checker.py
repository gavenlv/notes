"""
Soda Core data quality checker following Strategy pattern
"""

import tempfile
from pathlib import Path
from typing import Dict, List, Any
from soda.scan import Scan

from ..core.interfaces import IDatabaseConnection, ILogger, IFileManager
from .base_checker import BaseDataQualityChecker


class SodaDataQualityChecker(BaseDataQualityChecker):
    """Soda Core-based data quality checker"""
    
    def __init__(self, 
                 database_connection: IDatabaseConnection,
                 logger: ILogger,
                 file_manager: IFileManager,
                 data_source_name: str,
                 checks_path: str):
        super().__init__(database_connection, logger, data_source_name)
        self._file_manager = file_manager
        self._checks_path = checks_path
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run Soda Core data quality checks"""
        self._logger.info(f"Starting Soda Core checks for {self._data_source_name}")
        
        scan_id = self._generate_scan_id()
        scan_timestamp = self._get_scan_timestamp()
        
        # Create temporary configuration file
        config_content = self._generate_soda_config()
        config_file = self._create_temp_config_file(config_content)
        
        try:
            # Run Soda scan
            scan = Scan()
            scan.set_data_source_name(self._data_source_name)
            scan.add_configuration_yaml_file(config_file)
            
            # Add check files
            self._add_check_files(scan)
            
            # Execute scan
            scan.execute()
            
            # Extract results
            checks = self._extract_scan_results(scan)
            
        finally:
            # Clean up temporary file
            Path(config_file).unlink(missing_ok=True)
        
        # Create result
        result = self._create_scan_result(scan_id, checks, scan_timestamp)
        
        # Log summary
        self._log_scan_summary(result)
        
        return result
    
    def _generate_soda_config(self) -> str:
        """Generate Soda configuration based on data source"""
        if self._data_source_name == 'postgresql':
            return self._generate_postgresql_config()
        elif self._data_source_name == 'clickhouse':
            return self._generate_clickhouse_config()
        else:
            raise ValueError(f"Unsupported data source: {self._data_source_name}")
    
    def _generate_postgresql_config(self) -> str:
        """Generate PostgreSQL configuration"""
        # This would use the configuration manager in a real implementation
        # For now, return a basic config
        return """
data_source postgresql:
  type: postgres
  host: ${POSTGRES_HOST}
  port: ${POSTGRES_PORT}
  database: ${POSTGRES_DATABASE}
  username: ${POSTGRES_USERNAME}
  password: ${POSTGRES_PASSWORD}
"""
    
    def _generate_clickhouse_config(self) -> str:
        """Generate ClickHouse configuration"""
        return """
data_source clickhouse:
  type: clickhouse
  host: ${CLICKHOUSE_HOST}
  port: ${CLICKHOUSE_PORT}
  database: ${CLICKHOUSE_DATABASE}
  username: ${CLICKHOUSE_USERNAME}
  password: ${CLICKHOUSE_PASSWORD}
"""
    
    def _create_temp_config_file(self, config_content: str) -> str:
        """Create temporary configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(config_content)
            return f.name
    
    def _add_check_files(self, scan: Scan) -> None:
        """Add check files to scan"""
        checks_dir = Path(self._checks_path)
        if checks_dir.exists():
            for check_file in checks_dir.glob('*.yml'):
                if self._data_source_name in check_file.name:
                    scan.add_sodacl_yaml_file(str(check_file))
    
    def _extract_scan_results(self, scan: Scan) -> List[Dict[str, Any]]:
        """Extract results from Soda scan"""
        checks = []
        
        # Extract check results from scan
        for check in scan._checks:
            checks.append({
                'name': check.name,
                'table_name': getattr(check, 'table_name', ''),
                'result': check.outcome.value.upper() if hasattr(check, 'outcome') else 'UNKNOWN',
                'details': getattr(check, 'message', '')
            })
        
        return checks
