"""
Setup script for Python Data Quality Framework
Handles virtual environment creation and dependency installation.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path
from typing import List


class FrameworkSetup:
    """Handles setup and installation of the data quality framework."""
    
    def __init__(self, project_root: str = "."):
        """Initialize setup manager.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.venv_dir = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment.
        
        Returns:
            True if successful
        """
        try:
            if self.venv_dir.exists():
                print("Virtual environment already exists. Skipping creation.")
                return True
            
            print("Creating virtual environment...")
            venv.create(self.venv_dir, with_pip=True)
            print(f"Virtual environment created at: {self.venv_dir}")
            return True
            
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies from requirements.txt.
        
        Returns:
            True if successful
        """
        if not self.requirements_file.exists():
            print("requirements.txt not found. Skipping dependency installation.")
            return False
        
        pip_executable = self._get_pip_executable()
        
        try:
            print("Installing dependencies...")
            
            # Upgrade pip first
            subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
            
            # Install requirements
            subprocess.run([
                pip_executable, "install", "-r", str(self.requirements_file)
            ], check=True)
            
            print("Dependencies installed successfully.")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def _get_pip_executable(self) -> str:
        """Get the path to pip executable in virtual environment.
        
        Returns:
            Path to pip executable
        """
        if sys.platform == "win32":
            return str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            return str(self.venv_dir / "bin" / "pip")
    
    def _get_python_executable(self) -> str:
        """Get the path to Python executable in virtual environment.
        
        Returns:
            Path to Python executable
        """
        if sys.platform == "win32":
            return str(self.venv_dir / "Scripts" / "python.exe")
        else:
            return str(self.venv_dir / "bin" / "python")
    
    def setup_environment(self) -> bool:
        """Complete setup process: create venv and install dependencies.
        
        Returns:
            True if successful
        """
        print("Starting Python Data Quality Framework setup...")
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Copy environment example if needed
        self._setup_environment_file()
        
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Edit config/environment.env with your database credentials")
        print("2. Review and modify config/rules.yml for your data quality rules")
        print("3. Activate virtual environment:")
        
        if sys.platform == "win32":
            print(f"   {self.venv_dir}\\Scripts\\activate")
        else:
            print(f"   source {self.venv_dir}/bin/activate")
        
        print("4. Run data quality checks:")
        print("   python src/main.py")
        
        return True
    
    def _setup_environment_file(self) -> None:
        """Setup environment configuration file."""
        env_example = self.project_root / "config" / "environment.env.example"
        env_file = self.project_root / "config" / "environment.env"
        
        if not env_file.exists() and env_example.exists():
            import shutil
            shutil.copy2(env_example, env_file)
            print(f"Created environment file: {env_file}")
            print("Please edit this file with your actual database credentials.")
    
    def run_tests(self) -> bool:
        """Run framework tests to verify installation.
        
        Returns:
            True if tests pass
        """
        python_executable = self._get_python_executable()
        
        try:
            print("Running tests...")
            
            # Run basic import test
            result = subprocess.run([
                python_executable, "-c", 
                "from src.config_manager import ConfigManager; print('Import test passed')"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✓ Basic import test passed")
            else:
                print("✗ Basic import test failed")
                print(result.stderr)
                return False
            
            # Run configuration validation test
            result = subprocess.run([
                python_executable, "src/main.py", "--validate-only"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✓ Configuration validation test passed")
            else:
                print("✗ Configuration validation test failed")
                print(result.stderr)
                return False
            
            print("All tests passed!")
            return True
            
        except Exception as e:
            print(f"Error running tests: {e}")
            return False


def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Python Data Quality Framework')
    parser.add_argument('--test', action='store_true', help='Run tests after setup')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency installation')
    
    args = parser.parse_args()
    
    setup = FrameworkSetup()
    
    if not setup.setup_environment():
        sys.exit(1)
    
    if args.test and not setup.run_tests():
        sys.exit(1)
    
    print("\nFramework is ready to use!")


if __name__ == "__main__":
    main()