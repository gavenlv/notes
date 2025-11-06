"""
JSON file reporter implementation following Observer pattern
"""

from typing import Dict, List, Any
from core.interfaces import IDataQualityReporter, ILogger, IFileManager
from .base_reporter import BaseDataQualityReporter


class JSONDataQualityReporter(BaseDataQualityReporter):
    """JSON file-based data quality reporter"""
    
    def __init__(self, 
                 file_manager: IFileManager,
                 logger: ILogger):
        super().__init__(None, logger, 'json_file')  # No database connection needed
        self._file_manager = file_manager
    
    def store_scan_results(self, results: List[Dict[str, Any]]) -> None:
        """Store scan results as JSON files"""
        try:
            self._logger.info("Storing scan results as JSON files")
            
            for result in results:
                # Create comprehensive report data
                report_data = {
                    'scan_id': result.get('scan_id'),
                    'scan_timestamp': result.get('scan_timestamp'),
                    'data_source': result.get('data_source'),
                    'summary': {
                        'total_checks': result.get('total_checks', 0),
                        'checks_passed': result.get('checks_passed', 0),
                        'checks_failed': result.get('checks_failed', 0),
                        'checks_warned': result.get('checks_warned', 0),
                        'scan_result': result.get('scan_result', 0)
                    },
                    'checks': result.get('checks', []),
                    'logs': result.get('logs', ''),
                    'metadata': {
                        'reporter': self._reporter_name,
                        'environment': 'production'
                    }
                }
                
                # Generate filename
                timestamp = result.get('scan_timestamp', self._get_current_timestamp())
                filename = f"data_quality_report_{result['data_source']}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                
                # Save report
                file_path = self._file_manager.save_report(report_data, filename)
                self._logger.info(f"Report saved to: {file_path}")
            
            self._logger.info("Successfully stored all scan results as JSON files")
            
        except Exception as e:
            self._logger.error(f"Error storing JSON reports: {str(e)}")
            raise
