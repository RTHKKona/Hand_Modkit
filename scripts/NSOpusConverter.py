import os
import sys
import shutil
import subprocess
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, QApplication, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import webbrowser

class NSOpusConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.base_directory = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(self.base_directory, "data")
        self.temp_folder = os.path.join(self.data_folder, "temp_conversion")
        self.output_folder = os.path.abspath(os.path.join(self.base_directory, "..", "ConvertedOpus"))
        self.dependencies_file = os.path.join(self.data_folder, "NSOpusDirectory.txt")
        self.ffmpeg_path = os.path.join(self.data_folder, "ffmpeg.exe")
        self.nxaenc_path = os.path.join(self.data_folder, "NXAenc.exe")
        self.dependencies_valid = False
        self.init_ui()
        self.apply_initial_theme()  # Apply the initial theme
        self.check_dependencies()

    def init_ui(self):
        main_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Courier", 10))  # Set monospaced font for CMD style
        main_layout.addWidget(self.log_output)

        # Create buttons with consistent font size and buffer
        button_font = QFont()
        button_font.setPointSize(11)  # Set the font size for all buttons

        self.browse_button = QPushButton("Browse Audio Files", self)
        self.browse_button.setFont(button_font)
        self.browse_button.setStyleSheet("QPushButton { padding: 10px; }")
        self.browse_button.clicked.connect(self.open_file)
        self.browse_button.setAcceptDrops(True)
        self.browse_button.setEnabled(False)  # Initially disabled until dependency check passes
        self.browse_button.dragEnterEvent = self.dragEnterEvent
        self.browse_button.dragLeaveEvent = self.dragLeaveEvent
        self.browse_button.dropEvent = self.dropEvent
        bottom_layout.addWidget(self.browse_button)

        help_button = QPushButton("Help", self)
        help_button.setFont(button_font)
        help_button.setStyleSheet("QPushButton { padding: 10px; }")
        help_button.clicked.connect(self.show_help)
        bottom_layout.addWidget(help_button)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.setFont(button_font)
        self.toggle_theme_btn.setStyleSheet("QPushButton { padding: 10px; }")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.toggle_theme_btn)

        main_layout.addLayout(bottom_layout)
        central_widget = QLabel(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle('NSOpus Converter')
        self.setGeometry(100, 100, 1600, 800)  # Set the window size to 1600x800, positioned at 100,100

    def check_dependencies(self):
        """
        Checks the dependencies listed in NSOpusDirectory.txt and logs the result.
        If all dependencies are valid, enables the browse button; otherwise, shows an error.
        """
        self.log("Starting dependency check...\n")

        if not os.path.exists(self.dependencies_file):
            self.log(f"Error: Dependency list file '{self.dependencies_file}' not found.\n")
            return

        self.log(f"Dependency list file '{self.dependencies_file}' found. Checking each dependency...\n")
        
        missing_dependencies = []

        with open(self.dependencies_file, 'r') as file:
            dependencies = [line.strip() for line in file.readlines()]

        for dependency in dependencies:
            dependency_path = os.path.join(self.data_folder, dependency)
            if os.path.exists(dependency_path):
                self.log(f"[✔] Dependency '{dependency}' found at '{dependency_path}'.")
            else:
                self.log(f"[✘] Dependency '{dependency}' is missing.")
                missing_dependencies.append(dependency)

        if missing_dependencies:
            self.log("\nDependency check failed. The following dependencies are missing:\n")
            for dep in missing_dependencies:
                self.log(f" - {dep}")
            self.show_dependency_error(missing_dependencies)
        else:
            self.log("\nAll dependencies found. Dependency check complete.\n")
            self.dependencies_valid = True
            self.browse_button.setEnabled(True)

    def show_dependency_error(self, missing_dependencies):
        """
        Displays an error message with missing dependencies and a link to the GitHub repository.
        """
        message = (
            f"The following dependencies are missing:\n{', '.join(missing_dependencies)}\n\n"
            f"Please download the missing files from the GitHub repository:\n"
            "https://github.com/RTHKKona/Hand_Modkit/tree/main/scripts"
        )
        error_box = QMessageBox(self)
        error_box.setWindowTitle("Missing Dependencies")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)

        # Apply the current theme to the error box
        if self.dark_mode:
            error_box.setStyleSheet("""
                QMessageBox { background-color: #2b2b2b; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            """)
        else:
            error_box.setStyleSheet("")

        error_box.exec_()

    def show_help(self):
        help_text = (
            "1. Pinpoint which .opus files you would like to replace and note them down.\n"
            "2. Get your own audio files that you would like to replace, my tool supports mp4, mp3, flac, wav, and ogg.\n"
            "3. Browse for them in the NSOpus Converter tab.\n"
            "4. Let the conversion occur.\n"
            "5. Get your converted MHGU .opus files."
        )
        help_box = QMessageBox(self)
        help_box.setWindowTitle("Help")
        help_box.setText(help_text)
        help_box.setStandardButtons(QMessageBox.Ok)

        # Apply the current theme to the help box
        if self.dark_mode:
            help_box.setStyleSheet("""
                QMessageBox { background-color: #2b2b2b; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            """)
        else:
            help_box.setStyleSheet("")

        help_box.exec_()

    def open_file(self):
        if not self.dependencies_valid:
            return  # Don't allow opening files if dependencies aren't valid

        files, _ = QFileDialog.getOpenFileNames(self, "Open Audio Files", "", "Audio Files (*.mp3 *.mp4 *.wav *.flac *.ogg);;All Files (*)")
        if files:
            self.log(f"Selected Files: {', '.join(files)}")
            self.convert_to_opus(files)

    def dragEnterEvent(self, event):
        if not self.dependencies_valid:
            return  # Don't allow dragging if dependencies aren't valid

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.browse_button.setText(f"Import {event.mimeData().urls()[0].fileName()}")
            self.browse_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #FFD700;
                    padding: 30px 10px;  /* Increase padding when dragging */
                }
            """)

    def dragLeaveEvent(self, event):
        self.browse_button.setText("Browse Audio Files")
        self.browse_button.setStyleSheet("QPushButton { padding: 10px; }")

    def dropEvent(self, event):
        if not self.dependencies_valid:
            return  # Don't allow dropping if dependencies aren't valid

        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.log(f"Selected Files: {', '.join(files)}")
        self.browse_button.setText("Browse Audio Files")
        self.browse_button.setStyleSheet("QPushButton { padding: 10px; }")
        self.convert_to_opus(files)

    def convert_to_opus(self, files):
        if not files:
            self.log("No files selected for conversion.")
            return

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        try:
            for file in files:
                self.log(f"Processing: {file}")
                temp_wav = os.path.join(self.temp_folder, f"{os.path.basename(file)}_temp.wav")
                resampled_wav = os.path.join(self.temp_folder, f"{os.path.basename(file)}_resampled.wav")
                raw_file = os.path.join(self.temp_folder, f"{os.path.basename(file)}.raw")
                output_file = os.path.join(self.output_folder, f"{os.path.splitext(os.path.basename(file))[0]}.opus")

                if not file.lower().endswith('.wav'):
                    command_convert_wav = f"\"{self.ffmpeg_path}\" -i \"{file}\" \"{temp_wav}\""
                    self.run_command(command_convert_wav, "Convert to WAV", temp_wav)
                else:
                    temp_wav = file

                command_resample = f"\"{self.ffmpeg_path}\" -i \"{temp_wav}\" -ar 48000 -ac 2 -hide_banner -loglevel error \"{resampled_wav}\""
                self.run_command(command_resample, "Resample WAV", resampled_wav)

                command_pcm = f"\"{self.ffmpeg_path}\" -i \"{resampled_wav}\" -f s16le -acodec pcm_s16le -hide_banner -loglevel error \"{raw_file}\""
                self.run_command(command_pcm, "Convert to PCM", raw_file)

                command_opus = f"\"{self.nxaenc_path}\" -i \"{raw_file}\" -o \"{output_file}\""
                self.run_command(command_opus, "Convert to Opus", output_file)

            self.log("Conversion completed successfully.")
            webbrowser.open(self.output_folder)

        except Exception as e:
            self.log(f"Error during conversion: {e}")
        finally:
            self.cleanup_temp_files()

    def run_command(self, command, step_description, output_file):
        self.log(f"Running: {step_description}")
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0 or not os.path.exists(output_file):
            self.log(f"Error during {step_description}: {result.stderr}")
            raise Exception(f"{step_description} failed.")
        self.log(f"{step_description} completed successfully.")

    def cleanup_temp_files(self):
        try:
            if os.path.exists(self.temp_folder):
                shutil.rmtree(self.temp_folder)
                self.log(f"Deleted temporary folder: {self.temp_folder}")
        except Exception as e:
            self.log(f"Error deleting temporary folder: {e}")

    def log(self, message):
        self.log_output.append(message)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        self.apply_theme()

    def apply_theme(self):
        stylesheet = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """ if self.dark_mode else ""
        self.setStyleSheet(stylesheet)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NSOpusConverter()
    window.show()
    sys.exit(app.exec_())
