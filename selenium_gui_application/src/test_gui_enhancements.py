import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from gui_app import ElementFinderGUI

def test_gui_enhancements():
    """Test the enhanced GUI features"""
    print("Testing GUI enhancements...")
    
    # Create the application and GUI window
    app = QApplication(sys.argv)
    window = ElementFinderGUI()
    
    # Test 1: Initial state validation
    print("\nTest 1: Initial state validation")
    print(f"Start button enabled: {window.start_button.isEnabled()}")
    print(f"Stop button enabled: {window.stop_button.isEnabled()}")
    print(f"Open output button visible: {window.open_output_button.isVisible()}")
    print(f"Show folder button visible: {window.show_folder_button.isVisible()}")
    
    # Test 2: Input validation
    print("\nTest 2: Input validation")
    # Test URL validation
    window.url_input.setText("not-a-url")
    print(f"Invalid URL validation result: {window.validate_url()}")
    window.url_input.setText("https://example.com")
    print(f"Valid URL validation result: {window.validate_url()}")
    
    # Test output path validation
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_output_path = os.path.join(current_dir, "test_output.txt")
    window.output_file_input.setText(test_output_path)
    print(f"Output path validation result: {window.validate_output_path()}")
    
    # Test 3: Status indicators
    print("\nTest 3: Status indicators")
    print(f"Initial status text: {window.status_label.text()}")
    print(f"Initial progress bar format: {window.progress_bar.format()}")
    
    # Test 4: Console output with different message types
    print("\nTest 4: Console output with different message types")
    window.console_output.write("This is an info message", "info")
    window.console_output.write("This is a warning message", "warning")
    window.console_output.write("This is an error message", "error")
    window.console_output.write("This is a success message", "success")
    print("Console messages written with different formats")
    
    # Test 5: Simulate scan completion
    print("\nTest 5: Simulate scan completion")
    # Simulate successful scan completion
    window.scan_finished(0)
    print(f"After success - Progress bar value: {window.progress_bar.value()}")
    print(f"After success - Progress bar format: {window.progress_bar.format()}")
    print(f"After success - Status text: {window.status_label.text()}")
    print(f"After success - Open output button visible: {window.open_output_button.isVisible()}")
    print(f"After success - Show folder button visible: {window.show_folder_button.isVisible()}")
    
    # Simulate failed scan completion
    window.scan_finished(1)
    print(f"After failure - Progress bar value: {window.progress_bar.value()}")
    print(f"After failure - Progress bar format: {window.progress_bar.format()}")
    print(f"After failure - Status text: {window.status_label.text()}")
    
    print("\nAll tests completed!")
    return True

if __name__ == "__main__":
    # Set platform to offscreen to run in headless environments
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    test_gui_enhancements()