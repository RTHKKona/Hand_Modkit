import os
import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QApplication
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class FolderMaker(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.folder_input = QLineEdit(self)
        self.folder_input.setPlaceholderText("Click 'Browse' to select a folder...")
        layout.addWidget(self.folder_input)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(browse_button)

        self.file_input = QLineEdit(self)
        self.file_input.setPlaceholderText("Input exact name of file that you want to replace (i.e bgm_v03.opus)")
        layout.addWidget(self.file_input)

        create_button = QPushButton("Create Folders", self)
        create_button.clicked.connect(self.create_folders)
        layout.addWidget(create_button)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.toggle_theme_btn)

        self.setLayout(layout)
        self.setWindowTitle('Folder Creation Tool')
        
        # Increase font size by 1
        self.setFont(QFont(self.font().family(), self.font().pointSize() + 1))

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_input.setText(folder)
    
    def create_folders(self):
        analysis_folder = self.folder_input.text().strip()
        filename = self.file_input.text().strip()

        if not analysis_folder or not filename:
            QMessageBox.warning(self, "Input Error", "Please provide both a folder and a file name.")
            return

        relative_path = self.find_file(analysis_folder, filename)
        
        if relative_path:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            result_path = self.create_path_to_file(script_directory, analysis_folder, relative_path)
            
            if result_path:
                self.result_label.setText(f"Created folders leading to: {result_path}")
                self.result_label.setStyleSheet("color: #ffebcd;")  # Manilla color in dark mode
                self.open_directory(result_path)
            else:
                self.show_error("No matching folders were created.")
        else:
            self.show_error(f"Error: File '{filename}' not found in the directory structure.")

    def find_file(self, base_path, filename):
        for root, _, files in os.walk(base_path):
            if filename in files:
                return os.path.relpath(root, base_path)
        return None

    def create_path_to_file(self, script_directory, analysis_folder, relative_path):
        root_folder_name = os.path.basename(analysis_folder)
        target_path = os.path.join(script_directory, root_folder_name, relative_path)
        
        try:
            os.makedirs(target_path, exist_ok=True)
            return target_path
        except Exception as e:
            self.show_error(f"Error creating directory {target_path}: {e}")
            return None

    def open_directory(self, path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.Popen(['open', path])
        except Exception as e:
            self.show_error(f"Error opening directory: {e}")

    def show_error(self, message):
        self.result_label.setText(message)
        self.result_label.setStyleSheet("color: red;")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffebcd; }
                QLineEdit { background-color: #4d4d4d; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
                QLabel { color: #ffebcd; }
            """)
            self.result_label.setStyleSheet("color: #ffebcd;")  # Manilla color for result label
        else:
            self.setStyleSheet("")
            self.result_label.setStyleSheet("color: black;")  # Reset to default black color in light mode

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FolderMaker()
    window.show()
    sys.exit(app.exec_())
