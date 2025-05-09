import sys
import os
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui_app import ElementFinderGUI

# Set platform to offscreen for headless environments
if not os.environ.get('DISPLAY') and not os.environ.get('QT_QPA_PLATFORM'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    print("Running in offscreen mode due to no display server detected")

def main():
    app = QApplication(sys.argv)
    window = ElementFinderGUI()
    window.show()
    
    # Print confirmation that the GUI was created successfully
    print("GUI initialized successfully with the following components:")
    print(f"- Target URL input: {window.url_input.__class__.__name__}")
    print(f"- Output File input: {window.output_file_input.__class__.__name__}")
    print(f"- Chrome Profile checkbox: {window.chrome_profile_checkbox.__class__.__name__}")
    print(f"- Hover Simulation checkbox: {window.hover_checkbox.__class__.__name__}")
    print(f"- Page Load Wait input: {window.page_load_wait.__class__.__name__}")
    print(f"- Tags to Scan input: {window.tags_input.__class__.__name__}")
    print(f"- Headless Mode checkbox: {window.headless_checkbox.__class__.__name__}")
    print(f"- Console Output: {window.console_output.__class__.__name__}")
    
    # Exit after 1 second
    QTimer.singleShot(1000, app.quit)
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())