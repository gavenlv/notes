#!/usr/bin/env python3
"""
Refactored Soda Core Data Quality Application
Following SOLID principles with clean architecture
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.factories import DataQualityApplicationFactory


def main():
    """Main entry point for the refactored application"""
    try:
        # Get project root (parent of src directory)
        project_root = os.path.dirname(current_dir)
        
        # Create application using factory
        factory = DataQualityApplicationFactory(project_root)
        app = factory.create_application()
        
        # Run the application
        exit_code = app.run()
        
        # Exit with appropriate code
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
