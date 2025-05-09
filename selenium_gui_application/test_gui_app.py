import os
import sys
import unittest
import tkinter as tk
from pathlib import Path

class TestGUIApp(unittest.TestCase):
    """
    Test cases for the Element Finder GUI application.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        # Add the src directory to the Python path
        src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
        if src_dir not in sys.path:
            sys.path.append(src_dir)
        
        # Check if the required files exist
        self.selenium_script_path = os.path.join(src_dir, 'selenium_element_finder.py')
        self.gui_app_path = os.path.join(src_dir, 'gui_app.py')
        self.script_runner_path = os.path.join(src_dir, 'utils', 'script_runner.py')
        
    def test_file_existence(self):
        """
        Test that all required files exist.
        """
        self.assertTrue(os.path.exists(self.selenium_script_path), 
                       f"selenium_element_finder.py not found at {self.selenium_script_path}")
        self.assertTrue(os.path.exists(self.gui_app_path), 
                       f"gui_app.py not found at {self.gui_app_path}")
        self.assertTrue(os.path.exists(self.script_runner_path), 
                       f"script_runner.py not found at {self.script_runner_path}")
    
    def test_gui_app_imports(self):
        """
        Test that the GUI app can be imported without errors.
        """
        try:
            import gui_app
            self.assertTrue(True, "gui_app.py imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import gui_app.py: {e}")
    
    def test_script_runner_imports(self):
        """
        Test that the script runner can be imported without errors.
        """
        try:
            from utils import script_runner
            self.assertTrue(True, "script_runner.py imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import script_runner.py: {e}")
    
    def test_tkinter_availability(self):
        """
        Test that tkinter is available and can create a window.
        """
        try:
            root = tk.Tk()
            root.title("Test Window")
            # Just create the window briefly to test
            root.after(100, root.destroy)
            root.mainloop()
            self.assertTrue(True, "tkinter is available and can create a window")
        except Exception as e:
            self.fail(f"Failed to create tkinter window: {e}")
    
    def test_selenium_imports(self):
        """
        Test that selenium can be imported without errors.
        """
        try:
            import selenium
            from selenium import webdriver
            self.assertTrue(True, "selenium imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import selenium: {e}")
    
    def test_webdriver_manager_imports(self):
        """
        Test that webdriver_manager can be imported without errors.
        """
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.assertTrue(True, "webdriver_manager imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import webdriver_manager: {e}")

if __name__ == "__main__":
    unittest.main()