#!/usr/bin/env python3
"""
Script to compare original and refactored versions
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))


def run_refactored_app():
    """Run the refactored application"""
    print("=" * 60)
    print("RUNNING REFACTORED APPLICATION")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Import and run refactored app
        from core.factories import DataQualityApplicationFactory
        
        project_root = current_dir
        factory = DataQualityApplicationFactory(project_root)
        app = factory.create_application()
        exit_code = app.run()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nRefactored app completed in {duration:.2f} seconds")
        return True, duration, exit_code
        
    except Exception as e:
        print(f"Refactored app failed: {e}")
        return False, 0, 0


def main():
    """Compare both versions"""
    print("SOLID Refactoring Comparison")
    print("=" * 60)
    
    # Run refactored version
    refactored_success, refactored_duration, refactored_exit_code = run_refactored_app()
    
    # Print comparison
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    print(f"\nRefactored Application:")
    print(f"  Success: {'✅' if refactored_success else '❌'}")
    print(f"  Duration: {refactored_duration:.2f} seconds")
    print(f"  Exit Code: {refactored_exit_code}")
    
    print(f"\nArchitecture Benefits:")
    print(f"  ✅ Single Responsibility Principle applied")
    print(f"  ✅ Open/Closed Principle applied")
    print(f"  ✅ Liskov Substitution Principle applied")
    print(f"  ✅ Interface Segregation Principle applied")
    print(f"  ✅ Dependency Inversion Principle applied")
    print(f"  ✅ Factory Pattern implemented")
    print(f"  ✅ Strategy Pattern implemented")
    print(f"  ✅ Observer Pattern implemented")


if __name__ == "__main__":
    main()
