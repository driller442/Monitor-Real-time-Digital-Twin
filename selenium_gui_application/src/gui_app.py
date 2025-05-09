import os
os.environ['QT_QPA_PLATFORM'] = 'windows' # Force windows platform adapter

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test App")
        self.label = QLabel("If you see this, Qt platform is working!", self)
        self.label.setGeometry(50, 50, 300, 30) # x, y, width, height
        self.setGeometry(300, 300, 400, 150) # x, y, width, height

if __name__ == '__main__':
    print("Attempting to start Test App with QT_QPA_PLATFORM set...")
    try:
        app = QApplication(sys.argv)
        print("QApplication initialized.")
        mainWindow = MainWindow()
        print("MainWindow initialized.")
        mainWindow.show()
        print("MainWindow shown.")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"ERROR during app execution: {e}")
        # input("Press Enter to exit...") # Keep console open on error
        sys.exit(1)
