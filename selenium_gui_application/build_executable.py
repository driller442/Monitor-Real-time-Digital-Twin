#!/usr/bin/env python3
"""
Build script for Element Finder GUI application.
Creates a standalone executable using PyInstaller.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed using pip list."""
    print("Checking requirements...")
    
    # Run pip list and capture output
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        pip_output = result.stdout
    except subprocess.CalledProcessError:
        print("Error running pip list. Please check your Python installation.")
        return False
    
    # Check for required packages
    required_packages = {
        "pyinstaller": "5.6.0",
        "selenium": "4.1.0",
        "webdriver-manager": "3.8.0",
        "pyqt5": "5.15.0"
    }
    
    missing_packages = []
    
    for package, min_version in required_packages.items():
        package_lower = package.lower()
        if package_lower in pip_output.lower():
            print(f"✓ {package} is installed")
        else:
            print(f"✗ {package} is not installed. Required minimum version: {min_version}")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nMissing required packages. Please install them using:")
        for package in missing_packages:
            print(f"pip install {package}>={required_packages[package]}")
        return False
    
    return True

def check_project_structure():
    """Check if the project structure is correct."""
    print("Checking project structure...")
    
    required_files = [
        "src/gui_app.py",
        "src/selenium_element_finder.py",
        "src/utils/script_runner.py",
        "src/resources/styles/dark_theme.css",
        "element_finder_app.spec"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"✗ Missing file: {file_path}")
            missing_files.append(file_path)
        else:
            print(f"✓ Found file: {file_path}")
    
    if missing_files:
        print("\nMissing required files. Please make sure all files are in the correct location.")
        return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable with PyInstaller...")
    
    # Clean previous build files
    if os.path.exists("build"):
        print("Cleaning build directory...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("Cleaning dist directory...")
        shutil.rmtree("dist")
    
    # Run PyInstaller with the spec file
    cmd = [sys.executable, "-m", "PyInstaller", "element_finder_app.spec"]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
        
        # Check if the executable was created
        executable_name = "element_finder_app.exe" if platform.system() == "Windows" else "element_finder_app"
        executable_path = os.path.join("dist", executable_name)
        
        if os.path.exists(executable_path):
            print(f"Executable created: {executable_path}")
            return True
        else:
            print(f"Error: Executable not found at {executable_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        print("Please check the output above for error details.")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("Element Finder GUI - Executable Builder")
    print("=" * 60)
    
    if not check_requirements():
        print("\nPlease install the required packages and try again.")
        return
    
    if not check_project_structure():
        print("\nPlease fix the project structure and try again.")
        return
    
    if build_executable():
        print("\n" + "=" * 60)
        print("Build successful! You can find the executable in the 'dist' directory.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Build failed. Please check the error messages above.")
        print("=" * 60)

if __name__ == "__main__":
    main()