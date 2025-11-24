"""
Scan coordinator following SOLID principles
"""

from typing import List, Dict, Any
from .interfaces import IDataQualityChecker, IDataQualityReporter, ILogger


class DataQualityScanCoordinator:
    """Coordinates data quality scans and reporting"""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
        self._checkers: List[IDataQualityChecker] = []
        self._reporters: List[IDataQualityReporter] = []
    
    def add_checker(self, checker: IDataQualityChecker) -> None:
        """Add a data quality checker"""
        self._checkers.append(checker)
        self._logger.info(f"Added checker: {checker.get_data_source_name()}")
    
    def add_reporter(self, reporter: IDataQualityReporter) -> None:
        """Add a data quality reporter"""
        self._reporters.append(reporter)
        self._logger.info(f"Added reporter: {reporter.get_reporter_name()}")
    
    def run_all_scans(self) -> List[Dict[str, Any]]:
        """Run all registered checkers and report results"""
        self._logger.info("Starting comprehensive data quality scans")
        
        all_results = []
        
        # Run all checkers
        for checker in self._checkers:
            try:
                self._logger.info(f"Running checks for: {checker.get_data_source_name()}")
                result = checker.run_all_checks()
                all_results.append(result)
            except Exception as e:
                self._logger.error(f"Error running checks for {checker.get_data_source_name()}: {str(e)}")
                # Create error result
                error_result = {
                    'data_source': checker.get_data_source_name(),
                    'scan_id': 'error',
                    'scan_timestamp': None,
                    'total_checks': 0,
                    'checks_passed': 0,
                    'checks_failed': 1,
                    'checks_warned': 0,
                    'scan_result': 0,
                    'checks': [{
                        'name': 'System Error',
                        'result': 'FAILED',
                        'details': str(e)
                    }]
                }
                all_results.append(error_result)
        
        # Report results using all reporters
        for reporter in self._reporters:
            try:
                self._logger.info(f"Reporting results using: {reporter.get_reporter_name()}")
                reporter.store_scan_results(all_results)
            except Exception as e:
                self._logger.error(f"Error reporting with {reporter.get_reporter_name()}: {str(e)}")
        
        return all_results
    
    def get_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of all scan results"""
        total_checks = sum(result.get('total_checks', 0) for result in results)
        total_passed = sum(result.get('checks_passed', 0) for result in results)
        total_failed = sum(result.get('checks_failed', 0) for result in results)
        total_warned = sum(result.get('checks_warned', 0) for result in results)
        
        # Determine overall status
        if total_failed > 0:
            overall_status = "⚠️  ATTENTION REQUIRED"
        elif total_warned > 0:
            overall_status = "⚠️  WARNINGS"
        else:
            overall_status = "✅ HEALTHY"
        
        return {
            'total_checks': total_checks,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_warned': total_warned,
            'overall_status': overall_status,
            'data_sources': len(results)
        }
