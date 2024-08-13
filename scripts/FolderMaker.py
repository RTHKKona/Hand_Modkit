import os
import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FolderMaker(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.initUI()
        self.apply_initial_theme()  # Apply the initial theme

    def initUI(self):
        main_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        self.cmd_output = QTextEdit(self)
        self.cmd_output.setReadOnly(True)
        self.cmd_output.setFont(QFont("Courier", 10))  # Set monospaced font for CMD style
        main_layout.addWidget(self.cmd_output)

        self.folder_input = QLineEdit(self)
        self.folder_input.setPlaceholderText("Click 'Browse' to select a directory you'd like to analyze... (likely nativeNX)")
        bottom_layout.addWidget(self.folder_input)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_folder)
        bottom_layout.addWidget(browse_button)

        self.file_input = QLineEdit(self)
        self.file_input.setPlaceholderText("Input exact name of file that you want to replace (i.e bgm_v03.opus)")
        bottom_layout.addWidget(self.file_input)

        create_button = QPushButton("Create Directory/Folders", self)
        create_button.clicked.connect(self.create_folders)
        bottom_layout.addWidget(create_button)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.toggle_theme_btn)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        self.setWindowTitle('FolderMaker')
        self.setGeometry(100, 100, 1600, 800)  # Set the window size to 1600x800, positioned at 100,100

        self.update_font_size()  # Increase the font size

    def update_font_size(self):
        font = QFont()
        font.setPointSize(11)  # Increased font size by 1 point
        widgets = [
            self.folder_input, self.file_input, self.cmd_output,
            self.toggle_theme_btn
        ]
        for widget in widgets:
            widget.setFont(font)

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
                self.log(f"Created folders leading to: {result_path}")
                self.open_directory(result_path)
            else:
                self.log("No matching folders were created.")
        else:
            self.log(f"Error: File '{filename}' not found in the directory structure.")

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
            self.log(f"Error creating directory {target_path}: {e}")
            return None

    def open_directory(self, path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.Popen(['open', path])
        except Exception as e:
            self.log(f"Error opening directory: {e}")

    def log(self, message):
        self.cmd_output.append(message)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        """Apply the theme once during initialization."""
        self.apply_theme()

    def apply_theme(self):
        """Apply the appropriate stylesheet based on the current theme."""
        stylesheet = """
            QWidget { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QLineEdit { background-color: #4d4d4d; color: #ffebcd; border: 1px solid #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """ if self.dark_mode else ""
        self.setStyleSheet(stylesheet)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FolderMaker()
    window.show()
    sys.exit(app.exec_())
