import os
os.environ['QT_QPA_PLATFORM'] = 'windows' # Force windows platform adapter

import sys
# import os # Original os import is already covered above
import subprocess
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, 
    QPushButton, QFileDialog, QPlainTextEdit, QGroupBox,
    QDoubleSpinBox, QMessageBox, QProgressBar, QStatusBar,
    QToolTip, QSplashScreen, QFrame
)
from PyQt5.QtCore import Qt, QRegExp, QTimer
from PyQt5.QtGui import QRegExpValidator, QFont, QColor, QTextCharFormat, QBrush, QIcon
from utils.script_runner import ScriptRunner

class ConsoleOutput(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        font = QFont("Consolas" if os.name == "nt" else "Monospace")
        font.setPointSize(9)
        self.setFont(font)
        self.setMaximumBlockCount(5000)  # Limit to prevent memory issues
        
        # Define text formats for different message types
        self.info_format = QTextCharFormat()
        self.info_format.setForeground(QBrush(QColor("#CCCCCC")))
        
        self.warning_format = QTextCharFormat()
        self.warning_format.setForeground(QBrush(QColor("#FFA500")))  # Orange
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QBrush(QColor("#FF6B68")))  # Red
        
        self.success_format = QTextCharFormat()
        self.success_format.setForeground(QBrush(QColor("#6A8759")))  # Green
        
    def write(self, text, message_type="info"):
        # Add timestamp to the message
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
        text_with_timestamp = f"{timestamp}{text.rstrip()}"
        
        # Select format based on message type
        if message_type == "warning":
            self.appendPlainText(text_with_timestamp)
            cursor = self.textCursor()
            cursor.movePosition(cursor.End)
            cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
            cursor.setCharFormat(self.warning_format)
        elif message_type == "error":
            self.appendPlainText(text_with_timestamp)
            cursor = self.textCursor()
            cursor.movePosition(cursor.End)
            cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
            cursor.setCharFormat(self.error_format)
        elif message_type == "success":
            self.appendPlainText(text_with_timestamp)
            cursor = self.textCursor()
            cursor.movePosition(cursor.End)
            cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
            cursor.setCharFormat(self.success_format)
        else:  # info
            self.appendPlainText(text_with_timestamp)
        
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        QApplication.processEvents()
        
    def flush(self):
        pass

class ElementFinderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_runner = ScriptRunner()
        self.script_runner.output_received.connect(self.update_console)
        self.script_runner.process_finished.connect(self.scan_finished)
        self.initUI()
        
        # Timer for progress bar animation
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        
        # Flag to prevent recursive validation
        self.is_validating = False
        
        # Validate inputs on startup
        QTimer.singleShot(100, self.validate_all_inputs)
        
    def initUI(self):
        self.setWindowTitle("Selenium Element Finder")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status bar with additional information
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label in status bar
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Form layout for inputs
        form_group = QGroupBox("Configuration")
        form_layout = QFormLayout()
        
        # Target URL (mandatory)
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        url_validator = QRegExpValidator(QRegExp("^https?://.*"))
        self.url_input.setValidator(url_validator)
        self.url_input.textChanged.connect(self.on_url_changed)
        self.url_input.setToolTip("Enter the full URL of the website to scan (must start with http:// or https://)")
        
        # URL validation indicator
        self.url_validation_label = QLabel()
        self.url_validation_label.setFixedWidth(20)
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.url_validation_label)
        form_layout.addRow("Target URL*:", url_layout)
        
        # Output File Path (mandatory)
        output_layout = QHBoxLayout()
        self.output_file_input = QLineEdit()
        self.output_file_input.setPlaceholderText("Path to save output file")
        self.output_file_input.textChanged.connect(self.on_output_path_changed)
        self.output_file_input.setToolTip("Specify where to save the scan results")
        
        # Output path validation indicator
        self.output_validation_label = QLabel()
        self.output_validation_label.setFixedWidth(20)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        
        output_layout.addWidget(self.output_file_input)
        output_layout.addWidget(self.output_validation_label)
        output_layout.addWidget(self.browse_output_btn)
        form_layout.addRow("Output File Path*:", output_layout)
        
        # Chrome Profile Path (optional)
        profile_layout = QHBoxLayout()
        self.chrome_profile_checkbox = QCheckBox("Enable")
        self.chrome_profile_checkbox.stateChanged.connect(self.toggle_chrome_profile)
        self.chrome_profile_checkbox.setToolTip("Enable to use a specific Chrome profile")
        
        self.chrome_profile_input = QLineEdit()
        self.chrome_profile_input.setPlaceholderText("Path to Chrome profile")
        self.chrome_profile_input.setEnabled(False)
        self.chrome_profile_input.textChanged.connect(self.on_chrome_profile_changed)
        self.chrome_profile_input.setToolTip("Path to your Chrome user profile directory")
        
        # Chrome profile validation indicator
        self.profile_validation_label = QLabel()
        self.profile_validation_label.setFixedWidth(20)
        
        self.browse_profile_btn = QPushButton("Browse...")
        self.browse_profile_btn.clicked.connect(self.browse_chrome_profile)
        self.browse_profile_btn.setEnabled(False)
        
        profile_layout.addWidget(self.chrome_profile_checkbox)
        profile_layout.addWidget(self.chrome_profile_input)
        profile_layout.addWidget(self.profile_validation_label)
        profile_layout.addWidget(self.browse_profile_btn)
        form_layout.addRow("Chrome Profile:", profile_layout)
        
        # Hover Simulation
        hover_layout = QHBoxLayout()
        self.hover_checkbox = QCheckBox("Enable")
        self.hover_checkbox.stateChanged.connect(self.toggle_hover)
        self.hover_checkbox.setToolTip("Enable to simulate mouse hover over an element before scanning")
        
        self.hover_selector_input = QLineEdit()
        self.hover_selector_input.setPlaceholderText("CSS Selector for hover target")
        self.hover_selector_input.setEnabled(False)
        self.hover_selector_input.textChanged.connect(self.on_hover_selector_changed)
        self.hover_selector_input.setToolTip("CSS selector for the element to hover over (e.g., #menu-item, .dropdown)")
        
        # Hover selector validation indicator
        self.hover_validation_label = QLabel()
        self.hover_validation_label.setFixedWidth(20)
        
        hover_layout.addWidget(self.hover_checkbox)
        hover_layout.addWidget(self.hover_selector_input)
        hover_layout.addWidget(self.hover_validation_label)
        form_layout.addRow("Hover Simulation:", hover_layout)
        
        # Page Load Wait
        self.page_load_wait = QDoubleSpinBox()
        self.page_load_wait.setRange(0, 60)
        self.page_load_wait.setValue(5.0)
        self.page_load_wait.setSingleStep(0.5)
        self.page_load_wait.setSuffix(" seconds")
        self.page_load_wait.setToolTip("Time to wait for the page to load before scanning")
        form_layout.addRow("Page Load Wait:", self.page_load_wait)
        
        # Hover Wait
        self.hover_wait = QDoubleSpinBox()
        self.hover_wait.setRange(0, 30)
        self.hover_wait.setValue(1.0)
        self.hover_wait.setSingleStep(0.1)
        self.hover_wait.setSuffix(" seconds")
        self.hover_wait.setEnabled(False)
        self.hover_wait.setToolTip("Time to wait after hover before scanning (for dynamic elements to appear)")
        form_layout.addRow("Hover Wait:", self.hover_wait)
        
        # Tags to Scan
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("div,span,svg,a,button")
        self.tags_input.setText("div,span,svg,a,button")
        self.tags_input.setToolTip("Comma-separated list of HTML tags to scan")
        form_layout.addRow("Tags to Scan:", self.tags_input)
        
        # Run Headless
        self.headless_checkbox = QCheckBox("Run Chrome in headless mode")
        self.headless_checkbox.setToolTip("Run Chrome without visible browser window (faster but may miss some dynamic content)")
        form_layout.addRow("", self.headless_checkbox)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Progress bar
        self.progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        progress_layout.addWidget(self.progress_bar)
        self.progress_group.setLayout(progress_layout)
        main_layout.addWidget(self.progress_group)
        
        # Console output
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        self.console_output = ConsoleOutput()
        console_layout.addWidget(self.console_output)
        console_group.setLayout(console_layout)
        main_layout.addWidget(console_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Scan")
        self.start_button.clicked.connect(self.start_scan)
        self.start_button.setMinimumHeight(40)
        self.start_button.setEnabled(False)  # Disabled until validation passes
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        # These buttons are initially hidden until scan completes
        self.open_output_button = QPushButton("Open Output File")
        self.open_output_button.clicked.connect(self.open_output_file)
        self.open_output_button.setVisible(False)
        button_layout.addWidget(self.open_output_button)
        
        self.show_folder_button = QPushButton("Show in Folder")
        self.show_folder_button.clicked.connect(self.show_in_folder)
        self.show_folder_button.setVisible(False)
        button_layout.addWidget(self.show_folder_button)
        
        main_layout.addLayout(button_layout)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Initial console message
        self.console_output.write("Selenium Element Finder initialized. Ready to scan.", "info")
        
    def apply_dark_theme(self):
        # Load the external CSS file
        css_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "resources", "styles", "dark_theme.css"
        )
        
        try:
            with open(css_file_path, "r") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except Exception as e:
            self.console_output.write(f"Error loading stylesheet: {e}", "error")
            # Fallback to basic dark theme
            self.setStyleSheet("""
                QWidget { background-color: #2D2D30; color: #CCCCCC; }
                QMainWindow { background-color: #2D2D30; }
                QGroupBox { border: 1px solid #3F3F46; border-radius: 5px; margin-top: 1ex; }
                QLineEdit, QSpinBox, QDoubleSpinBox { background-color: #1E1E1E; color: #CCCCCC; }
                QPushButton { background-color: #0E639C; color: white; }
                QPlainTextEdit { background-color: #1E1E1E; color: #CCCCCC; }
            """)
    
    # Event handlers for input changes - these trigger validation without recursion
    def on_url_changed(self):
        self.validate_all_inputs()
        
    def on_output_path_changed(self):
        self.validate_all_inputs()
        
    def on_chrome_profile_changed(self):
        self.validate_all_inputs()
        
    def on_hover_selector_changed(self):
        self.validate_all_inputs()
    
    def toggle_chrome_profile(self, state):
        enabled = state == Qt.Checked
        self.chrome_profile_input.setEnabled(enabled)
        self.browse_profile_btn.setEnabled(enabled)
        self.profile_validation_label.setVisible(enabled)
        self.validate_all_inputs()
    
    def toggle_hover(self, state):
        enabled = state == Qt.Checked
        self.hover_selector_input.setEnabled(enabled)
        self.hover_wait.setEnabled(enabled)
        self.hover_validation_label.setVisible(enabled)
        self.validate_all_inputs()
    
    def browse_chrome_profile(self):
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Chrome Profile Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        if directory:
            self.chrome_profile_input.setText(directory)
            self.validate_all_inputs()
    
    def browse_output_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.output_file_input.setText(filename)
            self.validate_all_inputs()
    
    def validate_url(self):
        """Validate the URL input"""
        url = self.url_input.text()
        if not url:
            self.url_validation_label.setText("❌")
            self.url_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.url_input.setStyleSheet("border: 1px solid #FF6B68;")
            return False
        
        if not url.startswith(("http://", "https://")):
            self.url_validation_label.setText("❌")
            self.url_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.url_input.setStyleSheet("border: 1px solid #FF6B68;")
            return False
        
        self.url_validation_label.setText("✓")
        self.url_validation_label.setStyleSheet("color: #6A8759;")  # Green
        self.url_input.setStyleSheet("")
        return True
    
    def validate_output_path(self):
        """Validate the output file path"""
        path = self.output_file_input.text()
        if not path:
            self.output_validation_label.setText("❌")
            self.output_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.output_file_input.setStyleSheet("border: 1px solid #FF6B68;")
            return False
        
        # Check if directory exists and is writable
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            self.output_validation_label.setText("❌")
            self.output_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.output_file_input.setStyleSheet("border: 1px solid #FF6B68;")
            self.output_file_input.setToolTip("Directory does not exist")
            return False
        
        if directory and not os.access(directory, os.W_OK):
            self.output_validation_label.setText("❌")
            self.output_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.output_file_input.setStyleSheet("border: 1px solid #FF6B68;")
            self.output_file_input.setToolTip("Directory is not writable")
            return False
        
        self.output_validation_label.setText("✓")
        self.output_validation_label.setStyleSheet("color: #6A8759;")  # Green
        self.output_file_input.setStyleSheet("")
        self.output_file_input.setToolTip("Specify where to save the scan results")
        return True
    
    def validate_chrome_profile(self):
        """Validate the Chrome profile path if enabled"""
        if not self.chrome_profile_checkbox.isChecked():
            return True
        
        path = self.chrome_profile_input.text()
        if not path:
            self.profile_validation_label.setText("❌")
            self.profile_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.chrome_profile_input.setStyleSheet("border: 1px solid #FF6B68;")
            return False
        
        if not os.path.exists(path):
            self.profile_validation_label.setText("❌")
            self.profile_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.chrome_profile_input.setStyleSheet("border: 1px solid #FF6B68;")
            self.chrome_profile_input.setToolTip("Profile directory does not exist")
            return False
        
        self.profile_validation_label.setText("✓")
        self.profile_validation_label.setStyleSheet("color: #6A8759;")  # Green
        self.chrome_profile_input.setStyleSheet("")
        self.chrome_profile_input.setToolTip("Path to your Chrome user profile directory")
        return True
    
    def validate_hover_selector(self):
        """Validate the hover selector if hover is enabled"""
        if not self.hover_checkbox.isChecked():
            return True
        
        selector = self.hover_selector_input.text()
        if not selector:
            self.hover_validation_label.setText("❌")
            self.hover_validation_label.setStyleSheet("color: #FF6B68;")  # Red
            self.hover_selector_input.setStyleSheet("border: 1px solid #FF6B68;")
            return False
        
        self.hover_validation_label.setText("✓")
        self.hover_validation_label.setStyleSheet("color: #6A8759;")  # Green
        self.hover_selector_input.setStyleSheet("")
        return True
    
    def validate_all_inputs(self):
        """Validate all inputs and enable/disable the Start button accordingly"""
        # Prevent recursive validation
        if self.is_validating:
            return
        
        self.is_validating = True
        
        try:
            url_valid = self.validate_url()
            output_valid = self.validate_output_path()
            
            chrome_profile_valid = True
            if self.chrome_profile_checkbox.isChecked():
                chrome_profile_valid = self.validate_chrome_profile()
            
            hover_valid = True
            if self.hover_checkbox.isChecked():
                hover_valid = self.validate_hover_selector()
            
            # Enable start button only if all validations pass
            self.start_button.setEnabled(url_valid and output_valid and chrome_profile_valid and hover_valid)
        finally:
            self.is_validating = False
    
    def build_script_args(self):
        """Build command-line arguments for the selenium_element_finder.py script"""
        args = [self.url_input.text()]
        
        # Output file
        args.extend(["-o", self.output_file_input.text()])
        
        # Chrome profile
        if self.chrome_profile_checkbox.isChecked():
            args.extend(["-p", self.chrome_profile_input.text()])
        
        # Hover simulation
        if self.hover_checkbox.isChecked():
            args.append("--enable_hover")
            args.extend(["--hover_selector", self.hover_selector_input.text()])
            args.extend(["--hover_wait", str(int(self.hover_wait.value()))]) 
        
        # Page load wait
        args.extend(["--load_wait", str(int(self.page_load_wait.value()))]) 
        
        # Tags to scan
        if self.tags_input.text():
            args.extend(["--tags_to_scan", self.tags_input.text()])
        
        # Headless mode
        if self.headless_checkbox.isChecked():
            args.append("--headless")
        
        return args
    
    def start_scan(self):
        # Re-validate before starting, ensure validate_all_inputs() is called first
        self.validate_all_inputs() 
        if not self.start_button.isEnabled(): # Check if button is enabled by validation
            QMessageBox.warning(self, "Validation Error", "Please correct the highlighted inputs.")
            return
        
        # Clear console and update UI
        self.console_output.clear()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.open_output_button.setVisible(False)
        self.show_folder_button.setVisible(False)
        
        # Update status
        self.status_label.setText("Scanning...")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Initializing...")
        
        # Start progress animation
        self.progress_value = 0
        self.progress_timer.start(100)  # Update every 100ms
        
        # Build arguments and run the script
        args = self.build_script_args()
        self.console_output.write("Starting scan with the following configuration:", "info")
        self.console_output.write(f"URL: {self.url_input.text()}", "info")
        self.console_output.write(f"Output: {self.output_file_input.text()}", "info")
        if self.chrome_profile_checkbox.isChecked():
            self.console_output.write(f"Chrome Profile: {self.chrome_profile_input.text()}", "info")
        if self.hover_checkbox.isChecked():
            self.console_output.write(f"Hover Selector: {self.hover_selector_input.text()}", "info")
            self.console_output.write(f"Hover Wait: {self.hover_wait.value()} seconds", "info")
        self.console_output.write(f"Page Load Wait: {self.page_load_wait.value()} seconds", "info")
        self.console_output.write(f"Tags to Scan: {self.tags_input.text()}", "info")
        self.console_output.write(f"Headless Mode: {'Enabled' if self.headless_checkbox.isChecked() else 'Disabled'}", "info")
        self.console_output.write("", "info")  # Empty line
        
        self.script_runner.run_script(args)
    
    def stop_scan(self):
        self.script_runner.stop_script()
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True) # Re-enable start button on stop
        self.validate_all_inputs() # Re-validate to ensure start button status is correct
        self.status_label.setText("Scan stopped")
        self.progress_bar.setFormat("Stopped")
        self.progress_timer.stop()
        self.console_output.write("Scan stopped by user.", "warning")
    
    def update_console(self, text):
        # Determine message type based on content
        if "error" in text.lower() or "exception" in text.lower() or "failed" in text.lower():
            self.console_output.write(text, "error")
        elif "warning" in text.lower():
            self.console_output.write(text, "warning")
        elif "success" in text.lower() or "completed" in text.lower():
            self.console_output.write(text, "success")
        else:
            self.console_output.write(text, "info")
    
    def update_progress(self):
        """Update the progress bar animation during scanning"""
        if self.progress_value >= 95:
            self.progress_value = 0
        else:
            self.progress_value += 5
        
        self.progress_bar.setValue(self.progress_value)
        
        # Update progress text based on value
        if self.progress_value < 30:
            self.progress_bar.setFormat("Initializing browser...")
        elif self.progress_value < 60:
            self.progress_bar.setFormat("Loading page...")
        else:
            self.progress_bar.setFormat("Scanning elements...")
    
    def scan_finished(self, return_code):
        # self.start_button.setEnabled(True) # Validation will handle this
        self.stop_button.setEnabled(False)
        self.progress_timer.stop()
        self.validate_all_inputs() # Re-validate inputs to set start_button correctly
        
        if return_code == 0:
            # Success case
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Scan completed successfully")
            self.status_label.setText("Scan completed")
            
            # Show success message with output file path
            output_file = self.output_file_input.text()
            success_message = f"Scan completed successfully!\nResults saved to: {output_file}"
            self.console_output.write("", "info")  # Empty line
            self.console_output.write(success_message, "success")
            
            # Show file action buttons
            self.open_output_button.setVisible(True)
            self.show_folder_button.setVisible(True)
            
            # Show success dialog
            QMessageBox.information(self, "Scan Complete", success_message)
        else:
            # Error case
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Scan failed")
            self.status_label.setText("Scan failed")
            
            error_message = f"Scan failed with return code {return_code}."
            self.console_output.write("", "info")  # Empty line
            self.console_output.write(error_message, "error")
            
            # Show error dialog
            QMessageBox.critical(self, "Scan Failed", 
                                f"The scan process encountered an error (code {return_code}).\n"
                                f"Please check the console output for details.")
    
    def open_output_file(self):
        output_file = self.output_file_input.text()
        if not output_file:
            QMessageBox.warning(self, "Error", "No output file specified.")
            return
        
        if not os.path.exists(output_file):
            QMessageBox.warning(self, "Error", "Output file does not exist.")
            return
        
        # Open file with default application
        try:
            if os.name == 'nt':  # Windows
                os.startfile(output_file)
            elif os.name == 'posix':  # macOS and Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', output_file])
                else:  # Linux
                    subprocess.call(['xdg-open', output_file])
            
            self.console_output.write(f"Opening output file: {output_file}", "info")
        except Exception as e:
            self.console_output.write(f"Error opening output file: {str(e)}", "error")
            QMessageBox.warning(self, "Error", f"Could not open the output file: {str(e)}")
    
    def show_in_folder(self):
        output_file = self.output_file_input.text()
        if not output_file:
            QMessageBox.warning(self, "Error", "No output file specified.")
            return
        
        output_dir = os.path.dirname(output_file)
        if not output_dir: # If path is just a filename, use current directory
            output_dir = os.getcwd() 
            
        if not os.path.exists(output_dir):
            QMessageBox.warning(self, "Error", "Output directory does not exist.")
            return
        
        # Show file in folder
        try:
            if os.name == 'nt':  # Windows
                # For selecting the file: 'explorer /select,"C:\path\to\file.txt"'
                # For just opening the folder: 'explorer "C:\path\to\folder"'
                if os.path.exists(output_file): # If the file exists, select it
                    subprocess.run(['explorer', '/select,', os.path.normpath(output_file)], check=True)
                else: # Otherwise, just open the directory
                    subprocess.run(['explorer', os.path.normpath(output_dir)], check=True)

            elif sys.platform == 'darwin':  # macOS
                if os.path.exists(output_file):
                    subprocess.call(['open', '-R', output_file])
                else:
                    subprocess.call(['open', output_dir])
            else:  # Linux
                subprocess.call(['xdg-open', output_dir])
            
            self.console_output.write(f"Opening folder for: {output_file}", "info")
        except Exception as e:
            self.console_output.write(f"Error opening folder: {str(e)}", "error")
            QMessageBox.warning(self, "Error", f"Could not open the folder: {str(e)}")


if __name__ == "__main__":
    # The QT_QPA_PLATFORM setting is now at the very top of the file.
    # This block below is now commented out to avoid conflict.
    # if not os.environ.get('DISPLAY') and not os.environ.get('QT_QPA_PLATFORM'):
    #    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    #    print("Running in offscreen mode due to no display server detected")
    
    app = QApplication(sys.argv)
    window = ElementFinderGUI()
    window.show()
    sys.exit(app.exec_())
