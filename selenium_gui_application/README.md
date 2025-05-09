# Selenium Element Finder GUI Application

A standalone desktop application with a dark-themed GUI that wraps the functionality of the selenium_element_finder.py script. This application allows users to scan web pages for elements and log their details.

## Features

- Clean, intuitive dark-themed user interface
- Real-time console output display
- Error handling and user feedback mechanisms
- Automatic ChromeDriver management
- Standalone executable (no Python installation required)

## Project Structure

```
project/
├── src/                         # Source code
│   ├── selenium_element_finder.py  # Original script (integrated)
│   ├── gui_app.py               # Main GUI application code
│   ├── utils/                   # Utility functions
│   │   └── script_runner.py     # Script execution and driver management
│   └── resources/               # UI resources
│       └── styles/              # CSS/styling files
├── build/                       # Build files (generated)
└── dist/                        # Distribution files (generated)
    └── element_finder_app       # Final executable
```

## Installation

See the [Installation Guide](INSTALLATION_GUIDE.md) for detailed instructions on how to install and run the application.

## Usage

1. Launch the application by running the executable
2. Enter the target URL to scan
3. Specify the output file path
4. Configure additional options as needed:
   - Chrome profile path (optional)
   - Hover simulation (optional)
   - Page load wait time
   - Tags to scan
   - Headless mode
5. Click "Start Scan" to begin the scanning process
6. View real-time progress in the console output
7. When complete, open the output file or view it in its folder

## Building from Source

If you want to build the application from source:

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the build script:
   ```
   python build_executable.py
   ```
4. The executable will be created in the `dist` directory

## Requirements

- Google Chrome browser
- Internet connection (for first run to download ChromeDriver)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

## License

This project is licensed under the MIT License - see the LICENSE file for details.