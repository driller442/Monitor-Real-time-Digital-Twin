import sys
import os
import subprocess
import threading
import shutil
from PyQt5.QtCore import QObject, pyqtSignal
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import WebDriverException

class ScriptRunner(QObject):
    """
    Utility class to run the selenium_element_finder.py script from the GUI
    and capture its output in real-time.
    """
    output_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.is_running = False
    
    def run_script(self, args):
        """
        Run the selenium_element_finder.py script with the provided arguments.
        
        Args:
            args (list): Command-line arguments to pass to the script
        """
        if self.is_running:
            self.output_received.emit("Error: A scan is already running.")
            return
        
        self.is_running = True
        
        # Get the path to the selenium_element_finder.py script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "selenium_element_finder.py")
        
        # Check for Chrome and ChromeDriver
        if not self._check_chrome_and_driver():
            self.is_running = False
            return
        
        # Prepare the command
        cmd = [sys.executable, script_path] + args
        
        # Start the process in a separate thread to avoid blocking the GUI
        threading.Thread(target=self._run_process, args=(cmd,), daemon=True).start()
    
    def _check_chrome_installed(self):
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
                return True
                
            result = subprocess.run(
                ["which", "chromium-browser"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except:
            pass
            
        return False
    
    def _check_chrome_dependencies(self):
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
                    self.output_received.emit("Missing dependency: libnss3\n")
                    self.output_received.emit("Please install with: sudo apt-get install libnss3\n")
                    return False
            except:
                # If we can't check dependencies, assume they're missing
                self.output_received.emit("Unable to check Chrome dependencies.\n")
                self.output_received.emit("If you encounter issues, please install Chrome dependencies:\n")
                self.output_received.emit("sudo apt-get install libnss3 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6\n")
                return True  # Continue anyway
        
        return True
    
    def _check_chrome_and_driver(self):
        """
        Check for Chrome browser and ChromeDriver, and install/update if needed.
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        self.output_received.emit("Checking Chrome and ChromeDriver installation...\n")
        
        # Check if Chrome is installed
        if not self._check_chrome_installed():
            self.output_received.emit("Error: Google Chrome is not installed on this system.\n")
            self.output_received.emit("Please install Google Chrome to use this application.\n")
            self.output_received.emit("Download from: https://www.google.com/chrome/\n")
            return False
        
        # Check Chrome dependencies
        if not self._check_chrome_dependencies():
            return False
        
        try:
            # Install or update ChromeDriver
            driver_path = ChromeDriverManager().install()
            
            # Extract version from the path (typically includes version in the path)
            version_info = "latest compatible version"
            try:
                # Path format is typically /path/to/drivers/chromedriver/os/version/chromedriver
                path_parts = driver_path.split(os.sep)
                if len(path_parts) >= 3:
                    # Try to extract version from path
                    for part in path_parts:
                        if part.count('.') >= 2:  # Likely a version number like 114.0.5735.90
                            version_info = part
                            break
            except:
                pass
                
            self.output_received.emit(f"ChromeDriver {version_info} installed/updated successfully at: {driver_path}\n")
            
            # Set environment variable for the script to use
            os.environ["CHROMEDRIVER_PATH"] = driver_path
            
            # Verify ChromeDriver is executable
            if not os.access(driver_path, os.X_OK):
                self.output_received.emit("Making ChromeDriver executable...\n")
                try:
                    os.chmod(driver_path, 0o755)  # rwxr-xr-x
                except Exception as e:
                    self.output_received.emit(f"Warning: Could not make ChromeDriver executable: {str(e)}\n")
            
            return True
            
        except Exception as e:
            self.output_received.emit(f"Error during ChromeDriver setup: {str(e)}\n")
            self.output_received.emit("Please ensure you have a working internet connection and Chrome is properly installed.\n")
            return False
    
    def _run_process(self, cmd):
        """
        Run the process and capture its output.
        
        Args:
            cmd (list): Command to run
        """
        try:
            self.output_received.emit(f"Starting scan with command: {' '.join(cmd)}\n")
            
            # Run the process and capture its output
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=os.environ  # Pass environment variables including CHROMEDRIVER_PATH
            )
            
            # Read and emit output in real-time
            for line in self.process.stdout:
                self.output_received.emit(line)
            
            # Wait for the process to complete
            return_code = self.process.wait()
            
            if return_code == 0:
                self.output_received.emit("\nScan completed successfully.")
            else:
                self.output_received.emit(f"\nScan failed with return code {return_code}.")
            
            self.process_finished.emit(return_code)
        
        except Exception as e:
            self.output_received.emit(f"Error running scan: {str(e)}")
            self.process_finished.emit(1)
        
        finally:
            self.is_running = False
            self.process = None
    
    def stop_script(self):
        """
        Stop the running script if it's running.
        """
        if self.process and self.is_running:
            self.output_received.emit("\nStopping scan...")
            self.process.terminate()
            self.is_running = False
            self.output_received.emit("Scan stopped.")