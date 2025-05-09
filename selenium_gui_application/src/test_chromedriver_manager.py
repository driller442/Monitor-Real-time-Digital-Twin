"""
Test script to verify that the webdriver-manager integration works correctly.
This script tests the automatic ChromeDriver installation and management.
"""

import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

def check_chrome_installed():
    """
    Check if Chrome is installed on the system.
    
    Returns:
        bool: True if Chrome is installed, False otherwise
    """
    chrome_paths = [
        # Windows paths
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # macOS path
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Linux paths
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium"
    ]
    
    # Check if Chrome exists in any of the common paths
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"Chrome found at: {path}")
            return True
    
    # Check using 'which' command on Unix-like systems
    try:
        result = subprocess.run(
            ["which", "google-chrome"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"Chrome found at: {result.stdout.strip()}")
            return True
            
        result = subprocess.run(
            ["which", "chromium-browser"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"Chromium found at: {result.stdout.strip()}")
            return True
    except:
        pass
        
    print("Chrome not found on the system.")
    return False

def check_chrome_dependencies():
    """
    Check if the necessary dependencies for Chrome/ChromeDriver are installed.
    
    Returns:
        bool: True if dependencies are met, False otherwise
    """
    # On Linux, check for common dependencies
    if sys.platform.startswith('linux'):
        try:
            # Check for libnss3
            result = subprocess.run(
                ["ldconfig", "-p"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if "libnss3.so" not in result.stdout:
                print("Missing dependency: libnss3")
                print("Please install with: sudo apt-get install libnss3")
                return False
                
            print("Chrome dependencies check passed.")
        except Exception as e:
            print(f"Unable to check Chrome dependencies: {e}")
            print("If you encounter issues, please install Chrome dependencies:")
            print("sudo apt-get install libnss3 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6")
            return True  # Continue anyway
    
    return True

def test_chromedriver_manager():
    """
    Test the automatic ChromeDriver installation and management using webdriver-manager.
    """
    print("=== ChromeDriver Manager Integration Test ===")
    
    # Step 1: Check if Chrome is installed
    print("\nStep 1: Checking if Chrome is installed...")
    if not check_chrome_installed():
        print("\n❌ Error: Google Chrome is not installed on this system.")
        print("Please install Google Chrome to use this application.")
        print("Download from: https://www.google.com/chrome/")
        return False
    
    # Step 2: Check Chrome dependencies
    print("\nStep 2: Checking Chrome dependencies...")
    if not check_chrome_dependencies():
        print("\n❌ Error: Missing Chrome dependencies.")
        return False
    
    try:
        # Step 3: Install or update ChromeDriver
        print("\nStep 3: Installing/updating ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver installed/updated successfully at: {driver_path}")
        
        # Verify ChromeDriver is executable
        if not os.access(driver_path, os.X_OK):
            print("Making ChromeDriver executable...")
            try:
                os.chmod(driver_path, 0o755)  # rwxr-xr-x
            except Exception as e:
                print(f"Warning: Could not make ChromeDriver executable: {e}")
        
        # Step 4: Initialize WebDriver with the installed ChromeDriver
        print("\nStep 4: Initializing WebDriver with the installed ChromeDriver...")
        service = ChromeService(executable_path=driver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run in headless mode for testing
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Step 5: Test basic functionality
        print("\nStep 5: Testing basic functionality...")
        driver.get("https://www.google.com")
        print(f"Page title: {driver.title}")
        
        # Step 6: Clean up
        print("\nStep 6: Cleaning up...")
        driver.quit()
        
        print("\n✅ Test completed successfully! ChromeDriver manager integration is working.")
        return True
        
    except WebDriverException as e:
        print(f"\n❌ WebDriver error: {e}")
        if "Chrome failed to start" in str(e):
            print("\nPossible causes:")
            print("1. Chrome is not installed correctly")
            print("2. Missing dependencies")
            print("3. Sandbox issues (try adding --no-sandbox flag)")
            
            # Suggest installing Chrome dependencies on Linux
            if sys.platform.startswith('linux'):
                print("\nOn Linux, try installing Chrome dependencies:")
                print("sudo apt-get install libnss3 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6")
        return False
        
    except Exception as e:
        print(f"\n❌ General error: {e}")
        print("Error: Failed to set up ChromeDriver using webdriver-manager.")
        print("Possible causes:")
        print("  - Network connectivity issues")
        print("  - Incompatible Chrome version")
        print("  - Insufficient permissions")
        return False

if __name__ == "__main__":
    success = test_chromedriver_manager()
    sys.exit(0 if success else 1)