"""
File management following Single Responsibility Principle
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .interfaces import IFileManager


class StandardFileManager(IFileManager):
    """Standard file operations implementation"""
    
    def __init__(self, base_path: str):
        self._base_path = Path(base_path)
    
    def save_report(self, data: Dict[str, Any], filename: str) -> str:
        """Save report to file"""
        # Ensure reports directory exists
        reports_dir = self._base_path / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data_quality_report_{timestamp}.json'
        
        file_path = reports_dir / filename
        
        # Save data as JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(file_path)
    
    def load_config_file(self, filepath: str) -> str:
        """Load configuration file content"""
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def ensure_directory_exists(self, directory: str) -> None:
        """Ensure directory exists"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    def write_config_file(self, content: str, filepath: str) -> None:
        """Write configuration content to file"""
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
