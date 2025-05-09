# Element Finder App - Installation Guide

## System Requirements

- Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+ recommended)
- Google Chrome browser installed
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

## Installation Instructions

### Windows

1. Download the `element_finder_app.exe` file from the `dist` directory.
2. Double-click the executable to run the application.
3. If Windows SmartScreen shows a warning, click "More info" and then "Run anyway".

### macOS

1. Download the `element_finder_app` file from the `dist` directory.
2. Open Terminal and navigate to the download location.
3. Make the file executable with: `chmod +x element_finder_app`
4. Right-click the file and select "Open" (required for first run on macOS).
5. If prompted with a security warning, go to System Preferences > Security & Privacy and click "Open Anyway".

### Linux

1. Download the `element_finder_app` file from the `dist` directory.
2. Open Terminal and navigate to the download location.
3. Make the file executable with: `chmod +x element_finder_app`
4. Run the application with: `./element_finder_app`

## First Run

On first run, the application will:

1. Check for Google Chrome installation
2. Download the appropriate ChromeDriver version if needed
3. Initialize the user interface

## Troubleshooting

### Common Issues

1. **Application doesn't start**
   - Ensure Google Chrome is installed
   - Try running from command line to see error messages

2. **ChromeDriver issues**
   - The application should automatically download the correct ChromeDriver
   - If issues persist, try manually installing ChromeDriver

3. **UI rendering problems**
   - Ensure your system meets the minimum requirements
   - Update your graphics drivers

### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the console output for error messages
2. Ensure you have the latest version of Google Chrome installed
3. Contact support with details about your system and the error message

## Uninstallation

To uninstall the application:

1. Simply delete the executable file
2. Optionally, remove the `.wdm` folder in your home directory to clear ChromeDriver cache